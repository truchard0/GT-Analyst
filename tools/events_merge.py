#!/usr/bin/env python3
"""events_merge.py - fold curated EVENTS into the engine: an event log, node evidence, new nodes.

Input : promo/events_<theme>.json  (written by the curation step, one per theme)
Output: data/events.json                       the permanent, dated event log (append-only by (date, fact))
        data/timelines.json                    + evidence on every node an event bears on
                                               + validated new nodes (source 'events-<date>')
        data/events_reprice_suggestions.json   SUGGESTIONS ONLY - nothing here changes a probability

What this deliberately does NOT do:
  * it never changes an existing probability. Repricing is a judgment with a reason and goes through
    `ledger.py revise` (rows) or a reviewed edit (nodes). A merge step that silently moved prices because
    an agent said so is the failure mode this engine exists to prevent.
  * it never upgrades a confidence level. 'plan-only' events attach as PLANS and are labelled that way
    (#72: a plan is not an action).
  * it refuses an event whose bears_on names a node or ledger row that does not exist.

    python tools/events_merge.py --dry-run
    python tools/events_merge.py --write
"""
import argparse
import collections
import datetime as dt
import glob
import hashlib
import json
import pathlib
import re
import shutil
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "pipeline"))
import buildout_b_lib as L   # noqa: E402  - reuse the tree's node validator, do not restate it

TREE = ROOT / "data" / "timelines.json"
LOG = ROOT / "data" / "events.json"
SUGG = ROOT / "data" / "events_reprice_suggestions.json"
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CONF = {"verified-web", "multi-outlet", "feed-only", "plan-only", "mystery-ai"}
REL = {"supports", "contradicts", "context"}
MAX_EVIDENCE_PER_NODE_ADDED = 6        # keep node detail readable; the full record lives in events.json


def eid(e):
    return "evt-" + e["date"].replace("-", "") + "-" + hashlib.sha1(e["fact"].encode("utf-8")).hexdigest()[:6]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    tree = json.loads(TREE.read_text(encoding="utf-8"))
    nodes = {n["id"]: n for n in tree["nodes"]}
    lanes = set(tree.get("lanes", []))
    c = sqlite3.connect(ROOT / "ledger" / "ledger.db")
    ledger_ids = {r[0] for r in c.execute("SELECT id FROM predictions")}
    c.close()

    docs = []
    for f in sorted(glob.glob(str(ROOT / "promo" / "events_*.json"))):
        if "candidates" in f:
            continue
        docs.append(json.loads(pathlib.Path(f).read_text(encoding="utf-8")))
    if not docs:
        print("no promo/events_<theme>.json files found")
        return 1

    existing = {}
    if LOG.exists():
        existing = {e["id"]: e for e in json.loads(LOG.read_text(encoding="utf-8")).get("events", [])}

    events, bad_events, new_nodes, suggestions, gaps = [], [], [], [], {}
    for doc in docs:
        theme = doc.get("theme", "?")
        gaps[theme] = doc.get("gaps", "")
        for e in doc.get("events", []):
            why = []
            if not ISO.match(str(e.get("date", ""))):
                why.append("bad date")
            if e.get("confidence") not in CONF:
                why.append(f"confidence {e.get('confidence')!r}")
            if not isinstance(e.get("significance"), int) or not 1 <= e["significance"] <= 5:
                why.append("significance not 1..5")
            if len(str(e.get("fact", ""))) < 25 or not e.get("source"):
                why.append("fact/source too thin")
            for b in e.get("bears_on", []):
                if b.get("relation") not in REL:
                    why.append(f"relation {b.get('relation')!r}")
                if b.get("node") and b["node"] not in nodes:
                    why.append(f"unknown node {b['node']!r}")
                if b.get("ledger") and b["ledger"] not in ledger_ids:
                    why.append(f"unknown ledger row {b['ledger']!r}")
            if why:
                bad_events.append((theme, e.get("fact", "")[:70], why))
                continue
            e = dict(e, theme=theme)
            e["id"] = eid(e)
            events.append(e)
        for s in doc.get("suggest_reprice", []):
            suggestions.append(dict(s, theme=theme))
        for n in doc.get("new_nodes", []):
            new_nodes.append(dict(n, _theme=theme))

    # ── new nodes: built in the tree's exact shape, then run through the tree's own validator ──
    built = []
    for n in new_nodes:
        built.append({"id": n["id"], "parent": n["parent"], "label": n["label"], "p": n["p"], "horizon": n.get("horizon", ""),
                      "rationale": n["rationale"].strip(), "confluence": [], "ledger": [], "evidence": n.get("evidence", []),
                      "market": n.get("market", ""), "kind": "event", "lane": n["lane"], "date": n["date"],
                      "row_class": n["row_class"], "basis": n["basis"].strip(),
                      "source": "events-" + dt.date.today().isoformat()})
    L.NODES[:] = built
    node_problems = [b for b in L.validate(set(nodes), lanes)
                     if not b.startswith("only ") and "of the batch" not in b and "direction rows" not in b]
    direction = sum(1 for n in built if n["row_class"] == "direction")
    if built and direction / len(built) > 0.25:
        node_problems.append(f"{direction}/{len(built)} proposed nodes are direction rows - the 0-for-8 class; cap is 25% here")
    bad_ids = {re.match(r"([^:]+):", p).group(1) for p in node_problems if re.match(r"([^:]+):", p)}
    good_nodes = [n for n in built if n["id"] not in bad_ids]

    new_events = [e for e in events if e["id"] not in existing]
    print(f"themes: {len(docs)}   events curated: {len(events)}   already in log: {len(events) - len(new_events)}   refused: {len(bad_events)}")
    for th, f, why in bad_events:
        print(f"  REFUSED [{th}] {f}  -> {'; '.join(why)}")
    print("  by confidence:", dict(collections.Counter(e['confidence'] for e in events)),
          "  significance>=4:", sum(1 for e in events if e['significance'] >= 4))
    orphan = [e for e in events if not e.get("bears_on")]
    print(f"  events that bear on NOTHING in the tree: {len(orphan)} (the gap the user pointed at)")
    print(f"new nodes proposed: {len(built)}   pass the tree validator: {len(good_nodes)}   refused: {len(built) - len(good_nodes)}")
    for p in node_problems:
        print("  NODE REFUSED:", p[:150])
    print(f"repricing SUGGESTIONS collected (not applied): {len(suggestions)}")

    if not a.write:
        print("dry run; pass --write")
        return 0

    shutil.copy2(TREE, TREE.with_suffix(".json.bak-" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")))
    # 1. the permanent log
    merged = dict(existing)
    for e in events:
        merged[e["id"]] = e
    LOG.write_text(json.dumps({"updated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                               "n": len(merged), "events": sorted(merged.values(), key=lambda x: (x["date"], x["id"]))},
                              indent=1, ensure_ascii=False), encoding="utf-8")
    # 2. evidence on the nodes (idempotent: skip a fact already present)
    added = 0
    per_node = collections.Counter()
    for e in sorted(events, key=lambda x: (-x["significance"], x["date"])):
        for b in e["bears_on"]:
            nid = b.get("node")
            if not nid or per_node[nid] >= MAX_EVIDENCE_PER_NODE_ADDED:
                continue
            tag = "PLAN, NOT EXECUTED: " if e["confidence"] == "plan-only" else ""
            fact = f"{tag}{e['fact']} [{b['relation']}; {e['source']}; {e['confidence']}]"
            if any(x.get("fact") == fact for x in nodes[nid].get("evidence", [])):
                continue
            nodes[nid].setdefault("evidence", []).append({"fact": fact, "reported": e["date"]})
            per_node[nid] += 1
            added += 1
    # 3. validated new nodes
    for n in good_nodes:
        tree["nodes"].append(n)
    tree["updated"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    TREE.write_text(json.dumps(tree, indent=2, ensure_ascii=False), encoding="utf-8")
    # PRESERVE earlier suggestions: an earlier version overwrote this file on every run and a merge that carried no
    # suggestions silently erased 17 of them. Keep what is there, add what is new (keyed on target + from + to).
    prior = json.loads(SUGG.read_text(encoding="utf-8")) if SUGG.exists() else {"suggestions": [], "gaps": {}}
    key = lambda x: (x.get("node"), x.get("ledger"), x.get("from"), x.get("to"))
    seen = {key(x) for x in prior.get("suggestions", [])}
    kept = prior.get("suggestions", []) + [x for x in suggestions if key(x) not in seen]
    all_gaps = dict(prior.get("gaps", {}), **{k: v for k, v in gaps.items() if v})
    SUGG.write_text(json.dumps({"note": "SUGGESTIONS ONLY. Apply through ledger.py revise (rows) or a reviewed node edit. "
                                         "'status' records what was decided; absent = undecided.",
                                "suggestions": kept, "gaps": all_gaps}, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {LOG.name} ({len(merged)} events), +{added} evidence entries on {len(per_node)} nodes, "
          f"+{len(good_nodes)} new nodes, {len(suggestions)} suggestions -> {SUGG.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
