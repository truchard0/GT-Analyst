# AI prints backtest: six months of reports, forecast blind (first run, 18 Nov 2026)

**Status: complete for the first run.** Revenue, next-quarter guide and capex forecasts are all scored, with the
consensus comparison. Rules, pass lines and scorers were committed before the window data was
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

## Against Wall Street consensus (added when the consensus file landed; same 29 reports)
| Target | Our median miss | Consensus median miss | Naive median miss | We were closer than consensus on | Within tolerance: us vs consensus |
|---|---|---|---|---|---|
| Reported revenue | **1.02%** | 1.91% | 2.14% | **20 of 29** | within 2%: 72% vs 52% |
| Next-quarter guide | 5.60% | **3.69%** | 14.89% | 8 of 29 | within 5%: 34% vs 69% |

- **Revenue: the mechanical model beat consensus.** Consensus sits close to the company's guide (1.91% against the
  guide's 2.14%), and companies beat their guides by a steady margin; adding each company's own average beat captures
  what consensus leaves out. Mean miss 2.27% against 3.17%.
- **Next-quarter guide: consensus beat the model clearly.** Analysts carry information about the coming quarter
  (seasonality, order books, pricing) that a company's past step-ups do not.
- **Consensus missed the surprise quarters too.** Micron's June report: guide 33.5, consensus 35.8, our model 37.5,
  actual 41.5. Dell's May report: guide 35.2, consensus 35.4, our model 36.1, actual 43.8. Analysts had the news and
  were still 14% and 19% low. So reading the news is not a guaranteed fix for those quarters; a news-informed
  forecast has to be tested against exactly these cases.
- Consensus figures are from results-day press coverage (26 of 29 attributed to LSEG; a few unattributed or
  conflicting, listed in the data run's summary). Treat differences of a few tenths of a point as noise.

## Numeric forecasts (the test that matters)
| Target | Forecasts | Median miss | Within 1% | Within 2% | Within 3% | Within 5% | Naive median miss | Actual inside the 80% range | Average range |
|---|---|---|---|---|---|---|---|---|---|
| Reported revenue | 29 | **1.02%** | 48% | 72% | 86% | 86% | 2.14% (guide as given) | **62%** | ±2.8% |
| Next-quarter guide | 29 | **5.60%** | 10% | 17% | 24% | 34% | 14.89% (guide unchanged) | 66% | ±11.4% |

Against the pass lines set in advance:
| Line | Revenue | Next-quarter guide |
|---|---|---|
| Accuracy: beat the naive guide, and within 0.25 points of consensus | PASS (closer than the guide on 27 of 29; better than consensus) | n/a (beat the naive figure, lost to consensus) |
| Calibration: 80% range holds the actual 65-95% of the time | **FAIL** (62%) | pass, barely (66%) |
| Tightness: average range within ±2% / ±4% | **FAIL** (±2.8%) | **FAIL** (±11.4%) |

- **Bias:** revenue forecasts were 0.5% low on average; guide forecasts 4.8% low.
- **July-November only** (23 reports, the subset that cannot be in the model's training data): revenue median miss
  1.12%, 74% within 2%, range coverage 57%; next guide median miss 7.17%, 17% within 2%.
- **Without Micron and Dell** (25 reports): revenue median miss 0.96%, mean 1.15%, average range ±1.4%. Four reports
  from two companies account for most of the error and most of the range width.

## Capex numbers (five hyperscalers; added when the capex history landed)
| Target | Forecasts | Our median miss | Naive median miss | Consensus median miss | Within 5% | Actual inside the 80% range | Average range |
|---|---|---|---|---|---|---|---|
| Quarterly capex | 10 | **9.5%** | 19.5% (last quarter repeated) | 9.7% (6 reports with a consensus; ours 9.75% on the same 6) | 30% | 90% | **±24%** |
| New annual capex guide | 9 | **5.4%** | **1.8%** (prior guide unchanged) | n/a | 33% | 89% | ±15% |

- **Quarterly capex: about as good as consensus, twice as good as repeating last quarter, and nowhere near tight.**
  Misses ran from 3% to 25% (Amazon's October quarter came in at 77.3 against a 61.3 forecast; Oracle's September
  quarter at 28.5 against 21.4). A ±24% range is not a forecast anyone can use. Fails the ±8% tightness line.
- **Annual capex guide: the model lost to doing nothing.** It assumed each company would keep revising up at its
  recent pace and ran 7% high on average; in the window guides were mostly held and Microsoft's was cut twice
  (190 to 175 to 170). "The guide stays where it is" was closer on 7 of 9. The correct reading: a capex guide is
  sticky inside its year, and the forecastable event is the first guide for the next year, which this sample does
  not contain.
- Definitions differ by company (Microsoft and Meta include finance leases; Amazon guides on cash capex but reports
  gross), and Microsoft's July figure fell because of a lease reclassification, so the quarterly series is not fully
  like-for-like. Ten forecasts is a small sample.

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

Outside information existed before these reports (memory contract prices, AI-server backlog, hyperscaler capex
raises, holiday-quarter seasonality), and a model that reads only the company's own guide and beat history cannot
see it. On guides that information helps: consensus, which has it, was much closer. On the two largest revenue
surprises it did not help analysts either. That is what the news-informed forecast in `STATE.md` §7l has to be
tested on.

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

## Verdict by target
| Target | Can it be named in a tight range from the company's own history? |
|---|---|
| Reported revenue | Mostly: about ±1% on a normal quarter, better than consensus; fails on surprise quarters |
| Next-quarter guide | No: 5.6% median miss, and consensus is better |
| Quarterly capex | No: about 10% median miss, same as consensus |
| Annual capex guide inside its year | Assume no change; the model added nothing |

## Not done
- Forward numbers with ranges for the next prints (`--forward --scale 1.73` for revenue, `1.69` for guides, the
  factors that would have given 80% coverage here) have not been produced or logged.
