#!/usr/bin/env python3
"""Evaluator for the pre-registered calibration tests (prereg/PREREG_calibration_20261003.md).

THE ANALYSIS IS FIXED. This file is hashed into prereg/REGISTRY.jsonl before any row in the
confirmatory sample resolves. Changing the thresholds, the bands, the alpha or the bootstrap
after the fact is exactly the researcher-degrees-of-freedom problem the registration exists to
prevent: if the analysis needs to change, write a NEW dated prereg and say why. Do not edit this.

    python tools/prereg_calibration.py            # report, never writes
"""
import math
import pathlib
import random
import sqlite3
import sys

DB = pathlib.Path(__file__).resolve().parent.parent / "ledger" / "ledger.db"

# ── frozen parameters (changing any of these voids the registration) ──────────────────────────
ALPHA = 0.025                 # Bonferroni: 0.05 across two hypotheses
BOOT, SEED = 10000, 7
H1_BAND = (0.40, 0.60)        # first stated P in [lo, hi): "maybe" rows are UNDER-confident
H2_BAND = (0.80, 1.01)        # first stated P >= 0.80: high rows are OVER-confident
MIN_N = {"H1": 20, "H2": 10}
MIN_CLUSTERS = {"H1": 8, "H2": 5}
# rows already resolved on 2026-10-03 generated the hypotheses; they are EXPLORATORY and excluded.
# Open-at-registration rows in each band, frozen by id so later cluster/prob edits cannot move them:
FROZEN_OPEN = {"H1": {2, 3, 4, 6, 30, 35, 36, 40, 41, 54, 56}, "H2": {42, 53, 79, 80}}
EXPLORATORY_RESOLVED_BEFORE = "2026-10-03"


def poisson_binomial_tail(ps, k):
    """P(X >= k) where X = sum of independent Bernoulli(p_i). Exact DP, no normal approximation."""
    dist = [1.0]
    for p in ps:
        nxt = [0.0] * (len(dist) + 1)
        for j, q in enumerate(dist):
            nxt[j] += q * (1 - p)
            nxt[j + 1] += q * p
        dist = nxt
    return sum(dist[k:])


def cluster_key(row):
    c = (row["cluster"] or "").strip()
    return c if c else f"solo-{row['id']}"      # a blank cluster is an INDEPENDENT bet


def in_sample(row, hyp, band):
    if row["source"] and str(row["source"]).startswith("tree"):
        return False                              # tree-promoted rows are a separate stratum
    p0 = row["prob0"]
    if p0 is None or not (band[0] <= p0 < band[1]):
        return False
    if row["id"] in FROZEN_OPEN[hyp]:
        return True
    # a row not in the frozen list qualifies only if it was logged AFTER registration
    return str(row["ts"])[:10] >= EXPLORATORY_RESOLVED_BEFORE


def boot_p(rows, sign):
    """One-sided cluster-bootstrap p for sign*(hit_rate - mean_p0) <= 0."""
    groups = {}
    for r in rows:
        groups.setdefault(cluster_key(r), []).append(r)
    keys = list(groups)
    rnd = random.Random(SEED)
    le0 = 0
    for _ in range(BOOT):
        pick = [groups[rnd.choice(keys)] for _ in keys]
        flat = [x for g in pick for x in g]
        t = sum(x["outcome"] for x in flat) / len(flat) - sum(x["prob0"] for x in flat) / len(flat)
        le0 += (sign * t <= 0)
    return le0 / BOOT


def evaluate(c, hyp, band, sign, label):
    rows = [r for r in c.execute("SELECT * FROM predictions") if in_sample(r, hyp, band)]
    res = [r for r in rows if r["status"] == "resolved" and r["outcome"] is not None]
    clusters = {cluster_key(r) for r in res}
    print(f"\n{hyp}  {label}")
    print(f"    in sample: {len(rows)}   resolved: {len(res)}   clusters among resolved: {len(clusters)}")
    print(f"    need n >= {MIN_N[hyp]} and clusters >= {MIN_CLUSTERS[hyp]} before any verdict")
    if not res:
        print("    VERDICT: NONE YET (nothing in the confirmatory sample has resolved)")
        return
    k = sum(r["outcome"] for r in res)
    n = len(res)
    mp = sum(r["prob0"] for r in res) / n
    t = k / n - mp
    print(f"    hits {k}/{n} = {k / n:.0%}   mean first-stated P = {mp:.0%}   gap (hit - stated) = {t:+.1%}")
    if n < MIN_N[hyp] or len(clusters) < MIN_CLUSTERS[hyp]:
        print("    VERDICT: NONE YET (below the registered minimums; the numbers above are descriptive only)")
        return
    ps = [r["prob0"] for r in res]
    p_exact = poisson_binomial_tail(ps, k) if sign > 0 else 1 - poisson_binomial_tail(ps, k + 1)
    p_b = boot_p(res, sign)
    print(f"    exact Poisson-binomial one-tail p = {p_exact:.4f}   cluster-bootstrap one-tail p = {p_b:.4f}   (alpha {ALPHA})")
    ok = p_exact < ALPHA and p_b < ALPHA
    print("    VERDICT:", "SUPPORTED (both tests under alpha)" if ok else "NOT SUPPORTED at the registered threshold")


def main():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    print("Pre-registered calibration tests - primary sample = non-tree rows, open at 2026-10-03 or logged since")
    evaluate(c, "H1", H1_BAND, +1, "'maybe' rows (first P in [0.40,0.60)) hit MORE often than stated")
    evaluate(c, "H2", H2_BAND, -1, "high rows (first P >= 0.80) hit LESS often than stated")
    tree = [r for r in c.execute("SELECT * FROM predictions") if str(r["source"] or "").startswith("tree")]
    done = [r for r in tree if r["status"] == "resolved"]
    print(f"\nSECONDARY stratum (tree-promoted rows, never part of the primary tests): "
          f"{len(tree)} rows, {len(done)} resolved - read these by row class, not pooled.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
