# AI prints backtest: six months of reports, forecast blind (first run, 18 Nov 2026)

**Status: revenue and next-guide results are final for the first run. Capex forecasts and the consensus benchmark
are pending two data files (see the end).** Rules, pass lines and scorers were committed before the window data was
read (`data/ai_prints_backtest/PREREG.md`, commits `99c0181` and `06329b7`). Numbers below are the first run, unedited.

Sample: 29 reports published 18 May to 17 Nov 2026 by Nvidia (3), Broadcom, Micron, TSMC, AMD, Marvell, ASML, Applied
Materials, Lam, KLA, Dell, Amazon, Meta and Oracle (2 each). All 29 guides and actuals were read from company filings.
The model for each report used only that company's four earlier reports.

## Result in one paragraph
Naming the revenue number works about as well as a mechanical rule can: half the forecasts landed within 1% and 86%
within 3%, twice as accurate as taking the guide at face value. But the ranges were too narrow on the quarters that
mattered, and the next-quarter guide could not be forecast to a tight range at all: the median miss was 5.6% and the
forecasts ran low, because guides stepped up faster than each company's own history. Yes/no versions of the same
calls looked excellent (29 of 29 beat their guide), which is exactly why they are not informative.

## Numeric forecasts (the test that matters)
| Target | Forecasts | Median miss | Within 1% | Within 2% | Within 3% | Within 5% | Naive median miss | Actual inside the 80% range | Average range |
|---|---|---|---|---|---|---|---|---|---|
| Reported revenue | 29 | **1.02%** | 48% | 72% | 86% | 86% | 2.14% (guide as given) | **62%** | ±2.8% |
| Next-quarter guide | 29 | **5.60%** | 10% | 17% | 24% | 34% | 14.89% (guide unchanged) | 66% | ±11.4% |

Against the pass lines set in advance:
| Line | Revenue | Next-quarter guide |
|---|---|---|
| Accuracy: beat the naive guide (consensus check pending) | PASS (closer on 27 of 29) | n/a (closer on 26 of 29) |
| Calibration: 80% range holds the actual 65-95% of the time | **FAIL** (62%) | pass, barely (66%) |
| Tightness: average range within ±2% / ±4% | **FAIL** (±2.8%) | **FAIL** (±11.4%) |

- **Bias:** revenue forecasts were 0.5% low on average; guide forecasts 4.8% low.
- **July-November only** (23 reports, the subset that cannot be in the model's training data): revenue median miss
  1.12%, 74% within 2%, range coverage 57%; next guide median miss 7.17%, 17% within 2%.
- **Without Micron and Dell** (25 reports): revenue median miss 0.96%, mean 1.15%, average range ±1.4%. Four reports
  from two companies account for most of the error and most of the range width.

## Where it broke
| Report | Guide midpoint | Forecast | Actual | Miss |
|---|---|---|---|---|
| Dell, 28 May | 35.2 | 36.1 | 43.8 | -17.6% |
| Micron, 24 Jun | 33.5 | 37.5 | 41.5 | -9.5% |
| Micron, 30 Sep | 50.0 | 58.3 | 54.2 | +7.5% (over-corrected after June) |
| ASML, 15 Jul | 8.70 | 8.84 | 9.33 | -5.2% |

Next-quarter guides missed by more than 10% eight times (ASML twice, Broadcom, Lam, Dell, Meta, Amazon, AMD, Micron).
Seven of the eight were too low: the company guided a step-up its own history did not contain (Amazon guided
Q4 at 243.5 against a 201.9 Q3; Meta 74.5 against 64.6; AMD 17.0 against 13.4).

These are the quarters where outside information existed before the report (memory contract prices, AI-server
backlog, hyperscaler capex raises, holiday-quarter seasonality). A model that reads only the company's own guide and
beat history cannot see any of it. That is the case for the news-informed forecast described in `STATE.md` §7l.

## Yes/no rules (first design; kept for the record)
| Rule | Result | Stated probability | Read |
|---|---|---|---|
| Revenue at or above own guide midpoint | 29 of 29 | 86% | True every time, so it carries almost no information |
| Next guide above this quarter's actual | 27 of 29 (93%) | 72% | Under-confident |
| Annual capex guide not lowered | 9 of 10 (8 of 10 if Microsoft's July lease reclassification counts as a cut) | 88% | In line; 5 of 10 were raises |
| Stock closed higher the session after a beat | **11 of 28 (39%)** | claim: 40-65% | Claim missed by a hair, on the low side: a beat was followed by a fall more often than a rise |

## What this does and does not show
- It shows the direction calls (beat, guide up, no capex cut) are nearly certain in an up-cycle and therefore worth
  little, and that a beat did not predict the share-price reaction.
- It shows a mechanical number forecast is good to about 1% on a normal quarter and useless on a surprise quarter.
- It does not show how the model does in a downturn: every company in the sample was raising guides.
- The model design was written after its author had seen a few of these outcomes, so only the row-by-row forecasts are
  blind. The clean test is forward.

## Pending
- `capex_history.csv` (quarterly capex and annual guides): needed for the capex number forecasts.
- `consensus.csv` (sell-side consensus before each report): the benchmark that matters. Re-run
  `python3 tools/ai_prints_numeric.py --rows` when both are present.
- Forward numbers with ranges for the next prints (`--forward --scale 1.73` for revenue, `1.69` for guides, the
  factors that would have given 80% coverage here) have not been produced or logged.
