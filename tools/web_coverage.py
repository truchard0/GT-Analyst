#!/usr/bin/env python3
"""Timeline-web coverage check: every OPEN ledger prediction should be wired
into data/timelines.json (referenced in some node's ledger[] list), except
long-horizon doctrine seeds. Run after any `ledger.py add`:

    python tools/web_coverage.py

Exit code 1 if uncovered tactical predictions exist (so it can gate a cycle).
"""
import json
import pathlib
import sqlite3
import sys
from datetime import date

TODAY = date.today().isoformat()

ROOT = pathlib.Path(__file__).resolve().parent.parent
# Jiang doctrine seeds / long-horizon structural calls - deliberately not web nodes
EXEMPT_CLUSTERS = set()   # RULE: no exemptions - every prediction lives on the timeline
EXEMPT_SOURCES = set()

d = json.load(open(ROOT / "data" / "timelines.json", encoding="utf-8"))
nodes = d.get("nodes", [])
covered = set()
for n in nodes:
    covered.update(n.get("ledger", []))

# Dead-end catalyst check: a scheduled certainty (checkpoint) or a decision-fork
# event that shifts NOTHING downstream is a wiring gap — its outcome should move
# something, or it isn't a catalyst. Terminal-era nodes (2029+) are exempt (they
# ARE the end states). A node with children OR shift edges is wired.
ids = {n["id"] for n in nodes}
has_child = {n.get("parent") for n in nodes if n.get("parent")}
TERMINAL_LANES = {"world-order"}
dead_catalysts = []
for n in nodes:
    is_catalyst = n.get("checkpoint") or n.get("kind") == "checkpoint" or \
        (n.get("kind") == "event" and n["id"] in has_child)
    if not is_catalyst:
        continue
    # past catalysts have already fired — their forward influence is realized;
    # terminal-era nodes (2029+) ARE the end states, nothing downstream to shift.
    ndate = str(n.get("date", ""))
    if n.get("lane") in TERMINAL_LANES or ndate >= "2029" or (ndate and ndate[:10] < TODAY):
        continue
    wired = bool(n.get("shifts")) or (n["id"] in has_child)
    if not wired:
        dead_catalysts.append((n["id"], n.get("date", "?")))

c = sqlite3.connect(ROOT / "ledger" / "ledger.db")
rows = c.execute("SELECT id, source, cluster, substr(prediction,1,70) FROM predictions "
                 "ORDER BY id").fetchall()  # RULE: EVERY prediction, open or resolved

missing = [(i, cl, p) for i, src, cl, p in rows
           if i not in covered
           and (src or "") not in EXEMPT_SOURCES
           and (cl or "") not in EXEMPT_CLUSTERS]
exempt = [i for i, src, cl, _ in rows
          if i not in covered
          and ((src or "") in EXEMPT_SOURCES or (cl or "") in EXEMPT_CLUSTERS)]

print(f"open={len(rows)}  wired={sum(1 for i,_,_,_ in rows if i in covered)}  "
      f"exempt(seeds)={len(exempt)}  MISSING={len(missing)}  dead_catalysts={len(dead_catalysts)}")
if exempt:
    print("exempt (doctrine seeds, not web material):", exempt)
bad = False
if missing:
    bad = True
    print("\nNOT wired into the timeline web - fix these:")
    for i, cl, p in missing:
        print(f"  #{i} [{cl or '-'}] {p}")
if dead_catalysts:
    bad = True
    print("\nDEAD-END CATALYSTS - a catalyst that shifts nothing downstream (add shift edges):")
    for nid, dt in dead_catalysts:
        print(f"  {nid} ({dt}) — its outcome should move something")
if bad:
    sys.exit(1)
print("timeline web coverage OK — ledger wired, no dead-end catalysts")
