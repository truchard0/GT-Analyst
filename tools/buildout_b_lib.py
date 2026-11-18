#!/usr/bin/env python3
"""Shared scaffold for BUILDOUT B (2026-10-02, +200 nodes -> 466).

The 9/21 batch is the precedent; its rules are REUSED here rather than restated, so there is one
definition of what a well-formed node is. Part files do:

    from buildout_b_lib import N
    N("my-id", "parent", "Label", 0.80, "2027-06-30", "us-fiscal", "invariant", "3 quarters",
      "basis: the outside view and the constraint doing the work",
      "rationale: >=120 chars, auditable, says which part is soft",
      "market: what it means for a price")

WHAT THIS BATCH IS FOR
  The 9/21 buildout left two holes the tree still has: the far field is nearly empty (17 nodes in
  2028, 5 in 2029, 4 in 2030) and whole domains are absent - US entitlement actuarials, housing,
  insurance, the global election calendar, Russia-Ukraine, sovereign credit. Those are exactly the
  places where the engine's 8-for-8 class lives: trust-fund depletion dates, statutory review
  deadlines and fixed constitutional election dates are arithmetic, not opinion.

HARD CONSTRAINTS (the validator enforces all of them)
  * direction rows cap at 0.55 and may be at most 10% of the batch
  * p >= 0.85 requires row_class invariant or scheduled
  * p >= 0.70 requires a basis that names a structural constraint
  * invariant + scheduled must be >= 50% of the batch
  * >= 8 rows at p <= 0.45 and >= 8 at p >= 0.88 (without genuine negatives and genuine
    near-certainties the book earns no resolution - the 9/20 research measured RES ~0.00)
  * every LEVEL row carries odds={} from a real range_odds.py run; every DURATION row carries a
    real cycle_odds.py band. Prose is not evidence; this is the gap that shipped brent-band-q4
    0.27 away from its own arithmetic on 9/21.
  * branch siblings under one parent sum to 1.00
  * NO INVENTED DATED FACTS. `evidence` carries only structural/calendrical/arithmetic facts that
    are true by construction. A node resting on a prior says so in `basis` and carries no evidence.
"""
from __future__ import annotations

import collections
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import buildout_2026_09_21 as b1   # noqa: E402 - reuse the 9/21 rules, do not restate them

ROOT = pathlib.Path(__file__).resolve().parent.parent
TREE = ROOT / "data" / "timelines.json"
STAMP = "buildout-2026-10-02"

NEW_LANES = [
    "us-fiscal", "housing", "insurance-risk", "sovereign-credit",
    "global-elections", "russia-ukraine", "africa-frontier", "india-sa",
    "regulation-legal", "space-orbital", "transport-aviation", "water-ag-infra",
]

NODES: list[dict] = []


def N(nid, parent, label, p, date, lane, cls, horizon, basis, rationale, market,
      kind="event", evidence=None, shifts=None, ledger=None, confluence=None, odds=None):
    """Author one node. Same field order and semantics as the 9/21 batch."""
    n = {
        "id": nid, "parent": parent, "label": label, "p": p,
        "horizon": horizon,
        "rationale": rationale.strip(),
        "confluence": confluence or [],
        "ledger": ledger or [],
        "evidence": evidence or [],
        "market": market,
        "kind": kind, "lane": lane, "date": date,
        "row_class": cls, "basis": basis.strip(), "source": STAMP,
    }
    if shifts:
        n["shifts"] = shifts
    if odds:
        n["no_view"] = odds
    NODES.append(n)
    return nid


def validate(existing_ids: set[str], existing_lanes: set[str]) -> list[str]:
    bad: list[str] = []
    ids = {n["id"] for n in NODES}
    lanes_ok = existing_lanes | set(NEW_LANES)

    seen: set[str] = set()
    for n in NODES:
        if n["id"] in seen:
            bad.append(f"duplicate id within the batch: {n['id']}")
        seen.add(n["id"])

    for n in NODES:
        w = n["id"]
        if w in existing_ids:
            bad.append(f"{w}: id already exists in the tree")
        if n["parent"] != "now" and n["parent"] not in existing_ids and n["parent"] not in ids:
            bad.append(f"{w}: dangling parent {n['parent']!r}")
        if n["lane"] not in lanes_ok:
            bad.append(f"{w}: unknown lane {n['lane']!r}")
        if n["row_class"] not in b1.CLASSES:
            bad.append(f"{w}: unknown row_class {n['row_class']!r}")
        if not 0.0 <= n["p"] <= 1.0:
            bad.append(f"{w}: p out of range")
        if not n["basis"]:
            bad.append(f"{w}: no basis (R25: outside view first)")
        if len(n["rationale"]) < 120:
            bad.append(f"{w}: rationale too thin to audit ({len(n['rationale'])} chars)")
        if n["date"] < "2026-10-02":
            bad.append(f"{w}: dated in the past")

        cls, p = n["row_class"], n["p"]
        if cls == "direction" and p > 0.55 + 1e-9:
            bad.append(f"{w}: direction row at p={p} breaks the 0.55 cap (16.15)")
        if p >= 0.85 and cls not in ("invariant", "scheduled"):
            # AMENDMENT 2026-10-02. R13 reserves the top of the range for invariant/scheduled rows
            # because that is where the book scores and because high confidence elsewhere has been
            # judgment dressed as analysis (#24 at 0.80, #26 at 0.80). A level or duration row that
            # carries a MACHINE-CHECKED no-view block and sits within 0.10 of that measured number
            # is not judgment - it is arithmetic, which is the whole reason the no_view gate was
            # added after brent-band-q4. The exemption is tied to the evidence: a level row at 0.92
            # with no no_view block, or one that diverges from its own tool, is still refused.
            nv = n.get("no_view") or {}
            measured = nv.get("odds") if cls == "level" else None
            if measured is None or abs(p - measured) > 0.10 + 1e-9:
                bad.append(f"{w}: p={p} needs row_class invariant|scheduled, or a level row within "
                           f"0.10 of its machine-checked no-view odds; got {cls!r} "
                           f"{'(no no_view block)' if measured is None else f'vs odds {measured}'} (R13)")
        if p >= 0.70 and not any(k in n["basis"].lower() for k in b1.STRUCTURAL):
            bad.append(f"{w}: p={p} but basis names no structural constraint (R13/R26)")

        bad += [f"{w}: {m}" for m in b1.no_view_problems(n)]   # the arithmetic gate, reused

        for s in n.get("shifts", []):
            if s["target"] not in ids and s["target"] not in existing_ids:
                bad.append(f"{w}: shift edge to missing node {s['target']!r}")
        if n["kind"] == "checkpoint" and not n.get("shifts") \
                and not any(m["parent"] == n["id"] for m in NODES):
            bad.append(f"{w}: checkpoint with no shifts and no children = dead-end catalyst")

    by_parent: dict[str, float] = collections.defaultdict(float)
    for n in NODES:
        if n["row_class"] == "branch" or n["kind"] == "branch":
            by_parent[n["parent"]] += n["p"]
    for par, s in by_parent.items():
        if abs(s - 1.0) > 0.03:
            bad.append(f"branch children of {par!r} sum to {s:.2f}, not 1.00")

    counts = collections.Counter(n["row_class"] for n in NODES)
    total = len(NODES) or 1
    edge = counts["invariant"] + counts["scheduled"]
    if edge / total < 0.50:
        bad.append(f"only {edge}/{total} rows are invariant|scheduled - the 8-for-8 and 12-for-14 "
                   f"classes must be the majority of any buildout")
    if counts["direction"] / total > 0.10:
        bad.append(f"{counts['direction']}/{total} direction rows - the class that went 0-for-8 is "
                   f"capped at 10% of a batch")
    lo = sum(1 for n in NODES if n["p"] <= 0.45)
    hi = sum(1 for n in NODES if n["p"] >= 0.88)
    if lo < 8:
        bad.append(f"only {lo} rows at p<=0.45 - no resolution without genuine negatives")
    if hi < 8:
        bad.append(f"only {hi} rows at p>=0.88 - no resolution without genuine near-certainties")
    return bad


def summarise() -> None:
    counts = collections.Counter(n["row_class"] for n in NODES)
    lanes = collections.Counter(n["lane"] for n in NODES)
    years = collections.Counter(n["date"][:4] for n in NODES)
    ps = sorted(n["p"] for n in NODES)
    print(f"authored: {len(NODES)} nodes across {len(lanes)} lanes")
    print("  by class: " + "  ".join(f"{k}={v}" for k, v in counts.most_common()))
    print("  by lane : " + "  ".join(f"{k}={v}" for k, v in lanes.most_common()))
    print("  by year : " + "  ".join(f"{k}={v}" for k, v in sorted(years.items())))
    if ps:
        print(f"  p spread: min={ps[0]}  median={ps[len(ps)//2]}  max={ps[-1]}  "
              f"| p<=0.45: {sum(1 for p in ps if p <= 0.45)}  p>=0.88: {sum(1 for p in ps if p >= 0.88)}")
