# AI prints backtest, five years (first run, 18 Nov 2026 UTC / 17 Nov PT)

Rules fixed before the data was gathered: `data/ai_prints_backtest/PREREG_5Y.md` (commit `0022eca`). Scorer
`tools/ai_prints_5y.py` (the V2 model of `tools/ai_prints_numeric.py`, unchanged). Results `results_5y.json`.
Data: 108 added rows in `data/ai_prints_backtest/5y/` (all primary, from 8-K Exhibit 99.1 / 6-K releases, actuals
checked against SEC XBRL), consensus where results-day coverage named a provider, daily closes from a market-data feed.

Sample: Nvidia, Broadcom, Micron, TSMC, Amazon, Meta; every report published 18 Nov 2021 to 17 Nov 2026 (117 scored;
warm-up from Nov 2020).

## Headline
| Target | Our number, median miss | Consensus | Naive | Within 2% | 80% range held |
|---|---|---|---|---|---|
| Revenue (117) | **1.52%** (1.37% on the 77 with consensus) | 1.95% | 2.41% (guide as given) | 61% | 65% at the registered width; 85% at the forward refit |
| Next-quarter guide (116) | 6.45% (7.39% on the 74 with consensus) | **2.90%** | 11.37% (guide unchanged) | 19% | 74%; 86% at the refit |

Pass lines (PREREG): revenue accuracy PASS (beats naive; better than consensus on the same rows); calibration PASS for
both (65% and 74%); tightness FAIL for both (±3.0% and ±12.9% against ±2% and ±4%).

**Out-of-sample check of the forward ranges:** the widths fitted on the last six months (x1.73 revenue, x1.69 guide)
held 84.6% and 86.4% of actuals over the 104 earlier reports. Slightly wide; within the 65-95% band.

## By year (median miss: ours / consensus on its rows / naive)
| Year | Revenue | Next guide |
|---|---|---|
| Y1 Nov 21-Nov 22 | 1.60 / 1.08 / 1.55 | 6.07 / 5.91 / 6.74 |
| Y2 Nov 22-Nov 23 | 1.88 / 1.97 / 2.62 | 11.44 / 1.47 / 9.62 |
| Y3 Nov 23-Nov 24 | 2.12 / 2.07 / 3.10 | 6.90 / 2.05 / 13.50 |
| Y4 Nov 24-Nov 25 | 1.75 / 2.04 / 2.26 | 5.86 / 2.63 / 10.22 |
| Y5 Nov 25-Nov 26 | 0.96 / 2.99 / 3.25 | 5.57 / 3.53 / 15.52 |

On the same rows (ours / consensus): revenue Y1 1.66/1.08, Y2 1.71/1.97, Y3 1.72/2.07, Y4 1.47/2.04, Y5 1.02/2.99: ours
closer in four years of five. Guides: consensus closer in all five.

## Up-cycle vs down-cycle (down = the company guided the next quarter below the quarter's actual; 27 reports)
| | Revenue: ours / consensus / naive | Next guide: ours / consensus / naive |
|---|---|---|
| Up (90) | 1.34 / 1.99 / 2.68 | 5.55 / 2.84 / 11.38 |
| Down (27) | 1.87 / 0.80 / 2.12 | 13.36 / 3.07 / 10.13 |

The rule extrapolates the up-cycle. In a turn it still beats the naive guide on revenue, but consensus is far better,
and on guides it loses even to "no change".

## Yes/no rules
| Rule | All | Up | Down | Stated | Brier |
|---|---|---|---|---|---|
| R1 revenue >= own guide midpoint | 91.5% (117) | 96.7% | 74.1% | 0.86 | 0.081 |
| R2 next guide > this quarter's actual | 76.7% (116) | (by definition 100%) | (by definition 0%) | 0.72 | 0.181 |
| R4 stock up next session after a beat | 54.7% of 106, median +1.16% | | | claim 40-65% | inside the claim |

R2 by cycle is tautological (the cycle split is defined by R2's own outcome); only the overall rate is informative.

## By company (revenue / next guide, ours vs naive)
Broadcom 0.58/0.76 and 1.88/5.07; Amazon 0.95/1.81 and 6.82/10.95; Meta 1.13/3.05 and 8.87/8.91; TSMC 1.63/2.03 and
6.22/10.28; Nvidia 2.20/5.35 (consensus 4.91) and 5.84/15.01; **Micron 5.20/3.86 (worse than its own guide)** and
12.68/14.10. Memory moves faster than four quarters of history can follow.

## What changes
1. Print calls at 86-92% are an up-cycle number. In a down-cycle companies cleared their own midpoint 74% of the time.
   Proposed patch (for the user to approve, not applied): ai-trade skill §5 rule 4 gets a regime clause, "if the company
   guided the current quarter below the prior quarter's actual, cap at 0.75".
2. Micron's revenue number should be presented with its guide alongside; the model loses to the guide on Micron.
3. Next-guide numbers: publish, but say plainly that consensus has beaten this rule every year.

## Quarterly capex (Microsoft, Alphabet, Amazon, Meta; 80 reports)
Median miss 11.91% vs 12.67% for last quarter repeated (closer on 51 of 80); 80% range held 74% at ±22% average width;
tightness FAIL (±8% line). By year (ours / naive): Y1 15.35/17.44, Y2 14.24/10.17 (worse in the 2023 pause), Y3
12.50/14.44, Y4 9.23/11.88, Y5 8.40/13.26. Data: `5y/capex_hyperscalers.csv` (58 primary, 6 secondary Amazon rows whose
annual guide comes from third-party transcripts) plus the existing `capex_history.csv`.

History check of "equities peak before capex": SMH's quarter-end high was Q4 2021 (154.4); the four buyers' combined
quarterly capex peaked in Q4 2022 ($40.2bn) and dipped in Q1-Q2 2023 ($35.4bn), after SMH's Q3 2022 low (92.6).
