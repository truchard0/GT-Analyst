# AI prints backtest: rules fixed BEFORE the data was gathered (committed 2026-11-18)

**Question (user, 18 Nov 2026):** "Prints are highly predictable": backtest the last six months of major prints and
see how well the framework would have done blind.

## Window and sample (fixed)
Every quarterly report PUBLISHED from 18 May 2026 to 17 Nov 2026 inclusive by:
- **Suppliers (revenue guide to revenue actual):** NVDA, AVGO, MU, TSM, AMD, MRVL, ASML, AMAT, LRCX, KLAC, DELL.
- **Buyers with a numeric revenue guide:** AMZN, META, ORCL (growth-range guide converted to a midpoint).
- **Buyers' capex plans:** MSFT, GOOGL, AMZN, META, ORCL.
A report with no numeric company guide for that metric is excluded from that rule and listed as excluded.

## The rules (mechanical: one probability per rule, no judgment per company)
| Rule | Statement scored | Stated probability |
|---|---|---|
| R1 print | reported revenue >= midpoint of the company's own prior guide for that quarter | 0.86 |
| R2 guide | next-quarter revenue guide midpoint > this quarter's reported revenue | 0.72 |
| R3 capex no-cut | at the report, the company does NOT lower its annual capex guide (numeric or stated direction) against its previous statement | 0.88 |
| R4 reaction | NOT a call. Record how often the stock closed higher the next session after an R1 beat. The framework's claim under test: this frequency lies between 40% and 65% (a beat carries little price signal). |

Inputs allowed per prediction: only the company's guidance as it stood BEFORE the report. The prediction is the same
for every row, so no outcome knowledge can enter a prediction.

## Scoring
Hit rate and Brier score per rule, against two baselines: a coin (P 0.50, Brier 0.250) and the rule's own in-sample
base rate (reported, never used as the prediction). Rows are also split by source quality (primary vs secondary).
Kill criteria, taken from the framework's own forward-test section: R1 hit rate below 0.80 = the "prints are
predictable" premise fails in this sample.

## What this test is NOT (stated before the result)
- **Not a clean blind test of the rule itself.** The probabilities 0.86 / 0.72 / 0.88 were written on 18 Nov 2026
  after a research pass that said large tech companies usually beat, and after seeing a handful of these outcomes
  (Nvidia's 17 Nov print, Micron's last quarter, hyperscaler capex direction). The predictions are blind row by row;
  the choice of rule is not. The only fully blind test is the forward one (13 calls resolving Dec 2026 to Jun 2027).
- **Six months is one regime** (an up-cycle with rising guides). It says nothing about a downturn, when guides get cut.
- Beating the midpoint of one's own guide is partly an artefact of conservative guidance. The test measures whether
  that habit held, not whether the business was forecastable from outside.

---

# V2 (same day, before any window data was read): NUMERIC forecasts in a tight range

**User instruction, 18 Nov 2026:** "you have to predict these numbers (in a tight range) not just have booleans."
The boolean rules above stay and are still scored, but the test that matters is this one. Committed before the
window data files were opened; the data-gathering runs were still in progress.

## Data
- **Window (scored):** reports published 18 May 2026 to 17 Nov 2026, same companies as above.
- **History (never scored, only feeds the model):** each company's reports published 18 May 2025 to 17 May 2026.
- Each forecast for report t uses only reports published before t (walk-forward). In-window reports become history
  for later in-window reports.

## The model (mechanical; no judgment per company)
For company c and report t, from its earlier reports k:
- `beat_k = actual_k / guide_mid_k - 1`
- `step_k = next_guide_mid_k / actual_k - 1` (the guide given at report k for the following quarter, against quarter k's actual)
- `b` = mean of the last up to 4 beats before t; `g` = mean of the last up to 4 steps before t. With fewer than 2
  observations for the company, use the pooled mean over all companies' reports published before t.

| Target | Point forecast | 80% range (half-width) |
|---|---|---|
| **N1 reported revenue** | `guide_mid_t x (1 + b)` | `max(0.5%, 1.28 x sd(last <=4 beats))` |
| **N2 next-quarter guide midpoint** | `N1 point x (1 + g)` (the actual is not known before the report, so the forecast chains) | `max(1.0%, 1.28 x sqrt(sd(beats)^2 + sd(steps)^2))` |
| **N3 reported quarterly capex** (MSFT, GOOGL, AMZN, META, ORCL) | average of (a) momentum: `capex_{t-1} x (1 + mean q/q growth, last <=4 quarters)` and (b) guide-implied: `(annual guide midpoint in force before the report - capex already reported that year) / quarters left`; momentum alone when (b) cannot be computed | `max(3.0%, 1.28 x sd(last <=4 q/q growth rates))` |
| **N4 new annual capex guide midpoint** (where numeric, same guide year) | `prior midpoint x (1 + mean revision at the company's last <=4 reports)` | `max(2.0%, 1.28 x sd(revisions))` |

sd is the sample standard deviation; with fewer than 2 observations use the pooled sd. The first guide for a new
year (no prior midpoint for that year) is excluded from N4 and listed.

## Scoring
Per target: median and mean absolute % error; share of forecasts within 1%, 2%, 3% and 5% of the actual; how often
the actual fell inside the 80% range (coverage); mean half-width. Against two baselines:
- **B0 naive:** the guide midpoint as given (N1); the current-quarter guide midpoint unchanged (N2); last quarter's
  capex (N3); the prior annual guide unchanged (N4).
- **B1 sell-side consensus** before the report, where it could be collected (N1, and N2 where a guide consensus exists).

## Pass / fail lines (set now)
1. **Accuracy:** N1 median absolute error below B0's, and no more than 0.25 percentage points worse than consensus.
2. **Calibration:** coverage of the 80% ranges between 65% and 95% for each target with 10 or more forecasts.
3. **Tightness:** mean half-width at or below 2% (N1), 4% (N2), 8% (N3), 5% (N4).
A target that misses a line is reported as a miss. Range widths may be re-fitted afterwards for the FORWARD calls
only; the backtest numbers are reported as first run.

## Still true
The row-by-row forecasts are blind; the model design is not out-of-sample (it was written on 18 Nov 2026 by an
analyst who had seen a few of the outcomes). One six-month up-cycle. The forward numeric calls are the clean test.
