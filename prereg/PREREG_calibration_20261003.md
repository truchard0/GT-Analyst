# PRE-REGISTRATION — calibration hypotheses H1 and H2
**Registered 2026-10-03, before any row in the confirmatory sample has resolved.**
Evaluator: `tools/prereg_calibration.py` (hashed in `prereg/REGISTRY.jsonl`). Do not edit either file;
if the analysis must change, write a NEW dated prereg and say why.

## Where the hypotheses came from (so you can discount them correctly)
`ledger.py report` on 2026-10-02 showed, over 47 resolved rows:

| first-stated P | n | stated | actual | one-tail p |
|---|---|---|---|---|
| 40–60% | 12 | 55% | 83% (10/12) | 0.042, **5 clusters** |
| ≥ 80%  | 5  | 83% | 60% (3/5)   | 0.211, 3 clusters |

Both were found by *looking at the table*, not by prediction, so the nominal p-values overstate
the evidence (a garden of forking paths: I could have cut the buckets anywhere). The rows are
correlated within clusters (iran-war alone is 21 of 47). **These 17 resolved rows are exploratory and
are EXCLUDED from the confirmatory sample.** The H1 result in particular is the kind that routinely
vanishes on replication.

## Hypotheses (directions fixed in advance)
- **H1 — under-confidence in the middle.** Rows whose *first* stated P is in [0.40, 0.60) hit
  MORE often than they state. Statistic T1 = hit rate − mean(first P). Prediction: T1 > 0.
- **H2 — over-confidence at the top.** Rows whose first stated P is ≥ 0.80 hit LESS often than
  they state. Statistic T2 = mean(first P) − hit rate. Prediction: T2 > 0.

Both are one-sided. Alpha = 0.05 / 2 = **0.025 each** (Bonferroni over the two).

## Confirmatory sample (frozen)
- **Primary:** every row with source ≠ `tree:*` whose first stated P falls in the band and that was
  either (a) OPEN on 2026-10-03 — frozen by id below — or (b) logged on/after 2026-10-03.
  - H1 frozen open ids: **2, 3, 4, 6, 30, 35, 36, 40, 41, 54, 56** (11 rows)
  - H2 frozen open ids: **42, 53, 79, 80** (4 rows)
- Use the **first** stated probability (`prob0`), never the current one: revision is the thing
  being credited elsewhere; this tests the initial calibration.
- A blank `cluster` counts as an independent bet (its own cluster).
- VOID rows are excluded (unscored by definition).
- **Tree-promoted rows (`source` = `tree:<row_class>`) are NEVER in the primary sample.** The 149
  near-certain nodes are about to be promoted; letting them in would manufacture H2's "result"
  or dilute H1's. They form a separate secondary stratum, reported by row class.

## Decision rule (no discretion)
A verdict is issued **only** when the resolved confirmatory sample has
- H1: n ≥ 20 **and** ≥ 8 clusters;  H2: n ≥ 10 **and** ≥ 5 clusters.

Below those minimums the evaluator prints the descriptive gap and the words *NONE YET*; nothing
may be concluded or acted on. At or above them, the hypothesis is **SUPPORTED only if BOTH**
1. the exact one-tail Poisson-binomial p (each row at its own first P) is < 0.025, **and**
2. the one-tail cluster-bootstrap p (10,000 resamples of clusters, seed 7) is < 0.025.
Otherwise it is **NOT SUPPORTED**, and the matching exploratory pattern is to be treated as noise.

## What this is allowed to change — and what it is not
- If H1 is SUPPORTED: only then may a first-P shift (e.g. 0.55 → higher) be tested as a *rule*, and
  that rule needs its own prereg. Nothing in the live pricing changes before then.
- If H2 is SUPPORTED: R13's ≥0.70 reservation stays as is (it is already conservative).
- If neither: the 9/20 research reading stands — the book's probabilities carry no information
  beyond its hit rate, and the right response is *more scored rows*, not recalibration.

## Honest expectation about timing
The 11 frozen H1 rows have horizons from 2026-10-11 to 2028+, with most beyond 2027. At the
current rate of ~1–2 new manual rows/month in the band, **n ≥ 20 is a 2027–2028 event.** This
registration is cheap insurance against fooling ourselves later, not a near-term answer. If a faster
answer is wanted, the lever is logging more *manual, timely-referenced* rows in the band, not
loosening the thresholds.
