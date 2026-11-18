#!/usr/bin/env python3
"""mystery_events.py - use the Mystery Machine's news analyst as GT-Analyst's news analyst.

WHY: GT-Analyst's own analyst (pipeline/analyst.py, headless Claude CLI) was never set up, and on 2026-10-22 the
user pointed out the Trading Bot already runs one: tradingview/mystery_machine.py scores headlines with a local
Ollama model (qwen3:14b), de-duplicates them into STORIES with developments, and rates each development's
importance and market direction with a one-line reason. That is the judgment my syndication-count harvester
(tools/event_harvest.py) could not make. This adapter consumes THEIR output and feeds GT-Analyst's event log.

WHAT IT READS (strictly read-only; it never writes into the Trading Bot tree):
    tradingview/_skylit/news_ai/stories_month.json   (the month backfill: grows as their job runs)
    tradingview/_skylit/news_ai/stories_live.json    (the live stories)
WHAT IT WRITES: promo/events_mystery.json - the SAME schema the other curation files use, so
    tools/events_merge.py validates and merges it unchanged (nothing here touches a probability).

WHAT IT DELIBERATELY DOES NOT DO
  * it does not call Ollama. Their live scorer shares that GPU and "never waits on the model"; a second client
    would slow their live #news posts. All matching here is deterministic text overlap.
  * it never claims more than the model said: confidence is 'mystery-ai' (a local 14B model's rating, below
    'verified-web'), the model's own reason goes in `note`, and relation is always 'context' - deciding whether
    an event SUPPORTS or CONTRADICTS a node's probability is a judgment this adapter does not make.
  * mappings are conservative: a wrong 'evidence' line on a node is worse than a missing one.

    python tools/mystery_events.py --since 2026-09-22            # report only
    python tools/mystery_events.py --since 2026-09-22 --write    # write promo/events_mystery.json
"""
import argparse
import collections
import datetime as dt
import json
import math
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
NEWS = ROOT.parent / "Trading Bot" / "tradingview" / "_skylit" / "news_ai"
STOP = set("a an the of to in on for and or at by with from as is are was were be been it its this that after over amid says "
           "say said new us u.s. will could may might than into about up down out not no vs q1 q2 q3 q4 year first more".split())
# families where an ordinary single story can matter to this tree (macro / policy / geo); others need imp >= 0.5 to qualify
MACRO_FAMILIES = {"macro_other", "macro_release", "policy", "geo_policy", "fed", "oil", "rates"}
# Their importance means "moves the stock market today": upgrades, earnings previews, retail commentary and market WRAPS
# all score high. Measured 10/22 on 14 sampled imp>=0.5 stories: about a third bore on this tree. So only macro/geo
# families are taken, and a story must route to a lane (below) or it is not about anything this tree models.
TOPICS = {  # lane -> regex over story title + headline. Transparent on purpose: edit it, do not trust it.
    "iran-energy":      r"(iran\w*|hormuz|houthi\w*|irgc|tehran|persian gulf|red sea|strait|blockade|hezbollah|israel\w*)",
    "energy-supply":    r"(oil|crude|opec\+?|brent|wti|diesel|gasoline|lng|natural gas|refiner\w*|spr|pipeline|fuel)",
    "russia-ukraine":   r"(russia\w*|ukrain\w*|kyiv|putin|zelensk\w*|moscow|kremlin)",
    "china-macro":      r"(china|chinese|beijing|yuan|pboc|us-china|xi jinping)",
    "taiwan-china":     r"(taiwan\w*|pratas|strait of taiwan)",
    "fed-macro":        r"(fed|fomc|powell|warsh|rate (hike|cut)s?|inflation|cpi|pce|payrolls?|jobs report|unemployment|ism|pmi)",
    "rates-credit":     r"(treasur\w+|yields?|10-year|30-year|bond\w*|credit|cds|spreads?|mortgage)",
    "markets-ai":       r"(nvidia|openai|anthropic|coreweave|datacenter\w*|data center\w*|hyperscaler\w*|ai (spending|capex|bubble)|semiconductor\w*)",
    "us-politics":      r"(midterm\w*|shutdown|congress|senate|supreme court|doj|justice department|executive order|tariff\w*|sanction\w*)",
    "europe":           r"(ecb|eurozone|euro zone|brussels|germany|german|france|french|uk gilt\w*|boe)",
    "japan-korea":      r"(boj|bank of japan|yen|jgb|japan\w*|korea\w*)",
}
MIN_IMP_STORY, MIN_IMP_DEV, MAX_EVENTS_PER_STORY = 0.5, 0.5, 20


def load_stories():
    out = {}
    for name in ("stories_month.json", "stories_live.json"):
        p = NEWS / name
        if not p.exists():
            continue
        for _ in range(3):                       # their job rewrites these files; retry on a half-written read
            try:
                out.update(json.loads(p.read_text(encoding="utf-8"))["stories"])
                break
            except Exception:
                continue
    return out


def toks(text):
    return [w for w in re.findall(r"[a-z0-9$%.&]+", text.lower()) if w not in STOP and len(w) > 2]


def build_index(nodes):
    # label words only: the lane's own name ('iran', 'energy', 'rates') would match every node in the lane, and the lane
    # restriction in map_nodes already supplies that information
    docs = {n["id"]: set(toks(n["label"])) for n in nodes}
    df = collections.Counter(w for s in docs.values() for w in s)
    idf = {w: math.log((1 + len(docs)) / (1 + c)) + 1 for w, c in df.items()}
    return docs, idf


def lanes_of(text):
    # word boundaries are applied here, once, so every TOPICS pattern is a plain alternation
    return [lane for lane, rx in TOPICS.items() if re.search(r"\b" + rx + r"\b", text, re.I)]


def map_nodes(text, lanes, nodes_by_lane, docs, idf, k=3, min_sum=4.0, rare=2.6):
    """Within the story's own lane(s) only. Score = sum of idf over shared tokens; at least one shared token must be RARE
    in the node corpus (so 'war' or 'deal' alone never match). Conservative: a wrong evidence line is worse than none."""
    q = set(toks(text))
    scored = []
    for lane in lanes:
        for nid in nodes_by_lane.get(lane, []):
            ov = q & docs[nid]
            sm = sum(idf[w] for w in ov)
            # measured 10/22: with one rare word required, ~half the matches were wrong (Fed-speaker headlines attached to
            # 'fed-chair-term-2030'). Two rare shared words is the bar now; anything weaker is logged with NO node.
            if len(ov) >= 2 and sm >= min_sum and sum(1 for w in ov if idf[w] >= rare) >= 2:
                scored.append((sm, nid, sorted(ov)))
    scored.sort(reverse=True)
    return scored[:k]


def jacc(a, b):
    a, b = set(toks(a)), set(toks(b))
    return len(a & b) / len(a | b) if a and b else 0.0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--since", default="2026-09-22")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    stories = load_stories()
    if not stories:
        print(f"no stories found under {NEWS} - is the Mystery Machine running?")
        return 1
    tree = json.loads((ROOT / "data" / "timelines.json").read_text(encoding="utf-8"))
    docs, idf = build_index(tree["nodes"])
    log = json.loads((ROOT / "data" / "events.json").read_text(encoding="utf-8"))["events"] if (ROOT / "data" / "events.json").exists() else []
    known = collections.defaultdict(list)
    for e in log:
        known[e["date"]].append(e["fact"])

    nodes_by_lane = collections.defaultdict(list)
    for n in tree["nodes"]:
        nodes_by_lane[n["lane"]].append(n["id"])
    qualifying, off_topic, no_lane = [], 0, 0
    for s_ in stories.values():
        # headline COUNT (s_["n"]) never admits a story: how many outlets ran it says nothing about whether it matters
        if s_["family"] not in MACRO_FAMILIES or s_["imp"] < MIN_IMP_STORY:
            off_topic += 1
            continue
        if not lanes_of(s_["title"] + " " + (s_.get("top") or "")):
            no_lane += 1
            continue
        qualifying.append(s_)
    events, skipped_dupe, unmapped = [], 0, 0
    for s_ in qualifying:
        story_lanes = lanes_of(s_["title"] + " " + (s_.get("top") or ""))
        by_day = {}
        for h in s_["heads"]:
            if h.get("imp", 0) < MIN_IMP_DEV:
                continue
            day = h["et"][:10]
            on_topic = bool(set(lanes_of(h["headline"])) & set(story_lanes))
            rank = (on_topic, h["imp"])
            if day >= a.since and (day not in by_day or rank > by_day[day][0]):
                by_day[day] = (rank, h)
        for day, (rank, h) in sorted(by_day.items())[:MAX_EVENTS_PER_STORY]:
            if not rank[0]:
                continue                                           # nothing that day was actually about the topic
            fact = re.sub(r"\s[-|]\s[^-|]{2,60}$", "", h["headline"]).strip()
            if len(fact) < 25 or re.match(r"(stock market today|stocks? (rise|fall|slip|surge))", fact, re.I):
                continue                                           # a market wrap is not an event
            if re.search(r"\b(pmi|crude oil inventories|jobless claims|mortgage applications|housing starts|beige book)\b", fact, re.I):
                continue                                           # a routine weekly/monthly print is not an event
            near = [f for dd in (day, (dt.date.fromisoformat(day) - dt.timedelta(days=1)).isoformat(),
                                 (dt.date.fromisoformat(day) + dt.timedelta(days=1)).isoformat()) for f in known[dd]]
            if any(jacc(fact, f) >= 0.3 for f in near):
                skipped_dupe += 1
                continue
            m = map_nodes(fact + " " + s_["title"], story_lanes, nodes_by_lane, docs, idf)
            if not m:
                unmapped += 1
            events.append({
                "date": day, "fact": fact, "source": "Mystery Machine (qwen3:14b, AI-rated)",
                "confidence": "mystery-ai", "significance": 5 if h["imp"] >= 0.8 else 4 if h["imp"] >= 0.7 else 3,
                # Measured 10/22: about half of the auto-matches were wrong. A wrong evidence line on a node is worse than a
                # missing one, so NOTHING is attached to a node here. The guesses are kept for a reviewer to accept or reject.
                "bears_on": [],
                "candidate_nodes": [{"node": nid, "shared_words": ov, "idf_sum": round(sc, 1)} for sc, nid, ov in m],
                "note": f"AI importance {h['imp']:.2f}, market {h.get('mkt', 0):+.0f}; story '{s_['title']}' ({s_['family']}, {s_['n']} headlines; "
                        f"lanes {', '.join(story_lanes)}). Model's reason: {h.get('reason', '')[:200]}",
            })
    print(f"stories read: {len(stories)}   off-family/low-importance: {off_topic}   macro but no lane in this tree: {no_lane}   qualifying: {len(qualifying)}")
    print(f"-> events: {len(events)}   already in the log: {skipped_dupe}   logged WITHOUT a node match: {unmapped}")
    span = sorted({e["date"] for e in events})
    print(f"  dates covered: {span[0] if span else '-'} .. {span[-1] if span else '-'}   ({len(span)} days)")
    print("  by significance:", dict(collections.Counter(e["significance"] for e in events)))
    if a.write:
        (ROOT / "promo" / "events_mystery.json").write_text(json.dumps(
            {"theme": "mystery", "events": events, "new_nodes": [], "suggest_reprice": [],
             "gaps": "Mystery Machine stories only; their month backfill was still running when this was generated. Node matches are CANDIDATES, not evidence."},
            indent=1, ensure_ascii=False), encoding="utf-8")
        print("wrote promo/events_mystery.json - merge with: python tools/events_merge.py --write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
