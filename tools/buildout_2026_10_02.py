#!/usr/bin/env python3
"""BUILDOUT B — merge +200 nodes onto the master tree (266 -> 466).

Three part files, one contract (`buildout_b_lib`), one validator. The parts are imported for
their side effect: each is nothing but N() calls appending to buildout_b_lib.NODES.

    python tools/buildout_2026_10_02.py --dry-run
    python tools/buildout_2026_10_02.py --write

The self-check is the point. On 2026-09-21 the equivalent script refused its own author 32 times
and every one of those was fixed by moving the NUMBER, never the rule. The one rule that WAS
amended since (p>=0.85 on a level row) was amended in writing, tied to machine-checked evidence,
with the reasoning recorded in buildout_b_lib — not quietly relaxed to let a node through.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import buildout_b_lib as L                 # noqa: E402
import buildout_b_fiscal                   # noqa: E402,F401 - side effect: appends its nodes
import buildout_b_world                    # noqa: E402,F401
import buildout_b_infra                    # noqa: E402,F401


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="merge into data/timelines.json")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    tree = json.loads(L.TREE.read_text(encoding="utf-8"))
    existing_ids = {n["id"] for n in tree["nodes"]} | {"now"}
    existing_lanes = set(tree.get("lanes", []))

    already = {n["id"] for n in tree["nodes"] if n.get("source") == L.STAMP}
    if already:
        print(f"  NOTE: {len(already)} ids already in the tree under source='{L.STAMP}' — this "
              f"batch is MERGED. --write is refused so a re-run cannot duplicate it.")
        existing_ids -= already

    problems = L.validate(existing_ids, existing_lanes)
    L.summarise()

    if problems:
        print(f"\nREFUSED — {len(problems)} rule violation(s):")
        for b in problems:
            print("  - " + b)
        return 1
    print("\nself-check PASS — the batch survives the book's own rules")

    if not a.write:
        print("dry run; pass --write to merge")
        return 0
    if already:
        print("REFUSED --write: this batch is already merged.")
        return 1

    backup = L.TREE.with_suffix(f".json.bak-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}")
    shutil.copy2(L.TREE, backup)
    tree["lanes"] = list(tree.get("lanes", [])) + [x for x in L.NEW_LANES
                                                   if x not in tree.get("lanes", [])]
    tree["nodes"] = list(tree["nodes"]) + L.NODES
    tree["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    tree["note"] = (tree.get("note", "") + f" || {L.STAMP}: +{len(L.NODES)} nodes, "
                    f"+{len(L.NEW_LANES)} lanes. Built to fill the two holes the 9/21 batch left: "
                    f"the far field (the tree had 17 nodes in 2028, 5 in 2029, 4 in 2030) and the "
                    f"missing domains - US entitlement actuarials, housing, insurance, the global "
                    f"election calendar, Russia-Ukraine, sovereign credit, space, aviation, water. "
                    f"Every level row carries a no-view block from a real tool run on a spot and "
                    f"realised vol pulled from the tape, which is the gate the 9/21 batch lacked.")
    L.TREE.write_text(json.dumps(tree, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"merged -> {L.TREE}  (backup: {backup.name})")
    print(f"tree is now {len(tree['nodes'])} nodes / {len(tree['lanes'])} lanes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
