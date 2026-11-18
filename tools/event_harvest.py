#!/usr/bin/env python3
"""event_harvest.py - turn tens of thousands of feed headlines into a short, ranked list of STORIES.

WHY: on 2026-10-22 the feed held 84,487 items since 9/21 and the tree carried 3 news-type evidence entries
since then. The analyst that was meant to digest the feed was never set up, so nothing tracked events. Reading
84k headlines is not possible; ranking STORIES is. A story = one syndicated headline carried by many outlets.

Method (deterministic, no model):
  1. parse every item (title, feed, reported date) out of inbox/latest.md
  2. strip the trailing ' - Publisher' that Google News appends, keeping the publisher as the OUTLET
  3. cluster by the first six content words (sorted), which collapses syndication
  4. coverage = distinct OUTLETS carrying it. This only orders the READING queue; it is NOT importance and never feeds significance
  5. route each story to one theme by keyword hits; drop sports/entertainment/local noise

    python tools/event_harvest.py --since 2026-09-21 --top 220
writes promo/events_candidates_<theme>.json  (one file per theme)

HONEST LIMITS: coverage measures how widely a story was syndicated, not whether it matters. A viral
non-event outranks a quiet decisive one, and the first-six-words key splits some stories in two and merges
a few unrelated ones. This narrows 84k to a few hundred for a human or model to judge; it does not judge.
"""
import argparse
import collections
import json
import math
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
ITEM = re.compile(r"^- \*\*(.+?)\*\* \(([a-z0-9-]+) \| reported (\d{4}-\d{2}-\d{2})T([0-9:]+)Z", re.M)
PUB = re.compile(r"\s[-–|]\s([^-–|]{2,70})$")
STOP = set("a an the of to in on for and or at by with from as is are was were be been it its this that "
           "after over amid says say said new us u.s. will could may might than into about up down out".split())

THEMES = {   # priority order breaks ties
    "iran_energy": r"\b(iran\w*|hormuz|irgc|tehran|houthi\w*|red sea|saudi|opec\+?|brent|crude|oil (price|output|export)\w*|"
                   r"tanker\w*|lng|persian gulf|strait|israel\w*|hezbollah|lebanon|gaza|hamas|qatar|oman|kuwait|uae|mine[sd]?|blockade|"
                   r"natural gas|refiner\w*|pipeline)\b",
    "macro_markets_ai": r"\b(fed|fomc|warsh|powell|inflation|cpi|pce|payrolls?|jobs report|unemployment|treasury|yields?|s&p|nasdaq|dow|"
                        r"nvidia|meta|microsoft|alphabet|google|amazon|apple|tesla|coreweave|openai|anthropic|\bai\b|semiconductor\w*|chips?|"
                        r"earnings|dollar|yen|euro|gold|bitcoin|crypto\w*|bond\w*|credit|recession|gdp|rate (hike|cut)s?|stocks?|wall street)\b",
    "geopolitics": r"\b(russia\w*|ukrain\w*|putin|zelensk\w*|kyiv|nato|cuba\w*|venezuela\w*|maduro|china|chinese|taiwan\w*|xi jinping|beijing|"
                   r"north korea\w*|pyongyang|india\w*|pakistan\w*|japan\w*|korea\w*|europe\w*|eu\b|brussels|sanction\w*|tariff\w*|"
                   r"coup|election\w* in|prime minister|south china sea|pratas|arctic|greenland|panama)\b",
    "us_politics_legal": r"\b(trump|congress|senate|house (republicans|democrats|speaker)|shutdown|midterm\w*|supreme court|justice department|doj|"
                         r"executive order|immigration|ice\b|medicare|medicaid|fda|vaccine\w*|hurricane|wildfire|drought|court rules?|"
                         r"indict\w*|impeach\w*|housing|mortgage|student loan|tax\w*|budget|appropriations|veto|filibuster|governor)\b",
}
NOISE = re.compile(r"\b(man united|rooney|premier league|nfl|nba|mlb|nhl|soccer|football|cricket|ipl|olympics|oscars?|grammy|"
                   r"celebrity|royal family|kardashian|taylor swift|netflix series|box office|recipe|horoscope|lottery|"
                   r"obituary|wedding|dating|fashion|skyhawks|kidney|dialysis)\b", re.I)


def parse(text):
    out = []
    for title, feed, day, hhmm in ITEM.findall(text):
        t = title.strip()
        m = PUB.search(t)
        outlet = m.group(1).strip() if m else feed
        core = PUB.sub("", t).strip() if m else t
        out.append((core, outlet, feed, day, hhmm))
    return out


def key_of(core):
    toks = [w for w in re.findall(r"[a-z0-9$%.&+]+", core.lower()) if w not in STOP and len(w) > 1]
    return " ".join(sorted(toks[:6])) if len(toks) >= 3 else None


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--since", default="2026-09-21")
    ap.add_argument("--until", default="2099-01-01")
    ap.add_argument("--top", type=int, default=220, help="stories kept per theme")
    ap.add_argument("--src", default=str(ROOT / "inbox" / "latest.md"))
    a = ap.parse_args()

    items = [i for i in parse(pathlib.Path(a.src).read_text(encoding="utf-8", errors="replace"))
             if a.since <= i[3] <= a.until]
    clusters = collections.OrderedDict()
    for core, outlet, feed, day, hhmm in items:
        k = key_of(core)
        if not k or NOISE.search(core):
            continue
        c = clusters.setdefault(k, {"headline": core, "first": f"{day}T{hhmm}Z", "last": f"{day}T{hhmm}Z",
                                    "outlets": set(), "feeds": set(), "n": 0, "variants": []})
        stamp = f"{day}T{hhmm}Z"
        if stamp < c["first"]:
            c["first"], c["headline"] = stamp, core          # keep the EARLIEST wording as the headline
        c["last"] = max(c["last"], stamp)
        c["outlets"].add(outlet); c["feeds"].add(feed); c["n"] += 1
        if len(c["variants"]) < 3 and core not in c["variants"]:
            c["variants"].append(core)

    themed = collections.defaultdict(list)
    for k, c in clusters.items():
        scores = {t: len(re.findall(rx, c["headline"], re.I)) for t, rx in THEMES.items()}
        best = max(scores.values())
        if best == 0:
            continue
        theme = next(t for t in THEMES if scores[t] == best)
        c["coverage"] = len(c["outlets"]) * 3 + math.log1p(c["n"])
        themed[theme].append(c)

    outdir = ROOT / "promo"
    outdir.mkdir(exist_ok=True)
    print(f"items in window: {len(items):,}   stories after clustering: {len(clusters):,}   routed to a theme: {sum(len(v) for v in themed.values()):,}")
    for theme, cs in themed.items():
        cs.sort(key=lambda c: (-c["coverage"], c["first"]))
        keep = cs[:a.top]
        rows = [{"headline": c["headline"], "first": c["first"], "last": c["last"], "n_items": c["n"],
                 "outlets": sorted(c["outlets"])[:8], "n_outlets": len(c["outlets"]), "coverage_is_not_importance": True, "feeds": sorted(c["feeds"])[:4],
                 "variants": c["variants"]} for c in keep]
        (outdir / f"events_candidates_{theme}.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"  {theme:<18} {len(cs):>6} stories -> kept top {len(keep)}   (best carried by {rows[0]['n_outlets']} outlets: {rows[0]['headline'][:70]})")


if __name__ == "__main__":
    main()
