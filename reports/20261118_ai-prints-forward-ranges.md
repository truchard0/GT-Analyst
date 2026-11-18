# Next AI prints: numbers with ranges (registered 18 Nov 2026 UTC, 17 Nov PT)

**Method.** Each company's own guide, adjusted by its average beat over its last four reports (revenue), then by its
average guide step-up over the last four (next-quarter guide). Quarterly capex averages last-quarter momentum with what
the annual guide implies is left to spend. No judgment per company. Ranges are 80% ranges: the pre-registered width
times the factor that would have held 80% of actuals in the backtest (1.73 revenue, 1.69 guide); refit and tested
leave-one-out, those widths held 79% of actuals. Capex keeps its pre-registered width (9 of 10 actuals fell inside).

**Backtest record (29 reports, 18 May to 17 Nov 2026).**
| Target | Median miss | Consensus median miss | Verdict |
|---|---|---|---|
| Revenue | 1.0% | 1.9% | Better than consensus on 20 of 29; fails on surprise quarters |
| Next-quarter guide | 5.6% | 3.7% | Consensus better; ranges wide by construction |
| Quarterly capex | 9.5% | 9.7% | Same as consensus; ranges too wide to use |

**The number to quote is "Our number"**, the middle of the range (user instruction, 17 Nov PT: "pick an exact
number"). It is scored on its miss; the range is the honest uncertainty around it. Every row is also a ledger call at
80% that the actual lands inside the range. Dates other than Broadcom's are estimates;
if a company has not reported by the ledger horizon, the horizon moves and the call is not scored early.

## Revenue (US$ bn)
| Company, quarter | Report date | Own guide midpoint | Our number | 80% range | P |
|---|---|---|---|---|---|
| Broadcom FQ4 2026 | 9 Dec (confirmed) | 34.80 | 35.33 | 34.28 - 36.39 | 80% |
| Oracle FQ2 2027 | 9-14 Dec | 21.20 | 21.33 | 20.88 - 21.78 | 80% |
| Micron FQ1 2027 | ~15 Dec | 61.50 | 72.10 | 56.34 - 87.86 | 80% |
| TSMC Q4 2026 | 14 or 21 Jan | 53.30 | 54.59 | 53.59 - 55.60 | 80% |
| Meta Q4 2026 | ~27 Jan | 74.50 | 76.75 | 75.19 - 78.31 | 80% |
| Amazon Q4 2026 | ~4 Feb | 243.50 | 248.56 | 244.18 - 252.93 | 80% |
| Nvidia FQ4 2027 | 24 Feb - 3 Mar | 130.00 | 137.29 | 133.64 - 140.95 | 80% |

> **Revenue only from 17 Nov PT (user instruction: "lets only predict this for now and update all reports so it only
> includes revenue predictions").** The two tables below are no longer published in any report. Their ledger rows
> (#143-#154) stay open and will be scored honestly at their horizons, like the legacy oil rows; the user can ask to
> void them.

## Next-quarter revenue guide midpoint (US$ bn) — not published from 17 Nov PT
| Company, guide given with | Our number | 80% range | P |
|---|---|---|---|
| Broadcom FQ4 2026 | 41.52 | 31.48 - 51.57 | 80% |
| Oracle FQ2 2027 | 22.70 | 20.15 - 25.26 | 80% |
| Micron FQ1 2027 | 92.20 | 59.71 - 124.68 | 80% |
| TSMC Q4 2026 | 60.21 | 54.57 - 65.85 | 80% |
| Meta Q4 2026 | 79.75 | 62.99 - 96.50 | 80% |
| Amazon Q4 2026 | 255.24 | 166.68 - 343.80 | 80% |
| Nvidia FQ4 2027 | 154.61 | 148.69 - 160.53 | 80% |

## Quarterly capex (US$ bn, each company's own definition) — not published from 17 Nov PT
| Company, quarter | Last quarter | Our number | 80% range | P |
|---|---|---|---|---|
| Oracle FQ2 2027 | 28.50 | 30.53 | 16.35 - 44.71 | 80% |
| Microsoft FQ2 2027 (incl. finance leases) | 45.20 | 50.32 | 38.84 - 61.79 | 80% |
| Meta Q4 2026 (incl. finance-lease principal) | 34.91 | 47.72 | 30.64 - 64.80 | 80% |
| Alphabet Q4 2026 | 51.36 | 65.13 | 59.41 - 70.86 | 80% |
| Amazon Q4 2026 (gross) | 77.26 | 69.45 | 56.75 - 82.15 | 80% |

## How to read it
- **Tight and usable:** revenue for Broadcom, Oracle, TSMC, Meta, Amazon and Nvidia (about ±2-3%), and Nvidia's next
  guide (±4%).
- **Not tight:** Micron (±22% on revenue) because its last four reports include two large surprises; every next guide
  except Nvidia's; all capex. These are published because they were asked for and are scored honestly, not because they
  are useful ranges.
- **Known blind spots, stated before the prints:** the guide model has no seasonality, so Amazon's and Meta's Q1 guide
  points ignore the usual Q4-to-Q1 drop (Amazon guided Q1 2026 at 176 after a 213 Q4) and are likely too high; Nvidia's
  Q4 has 14 weeks and Q1 13; Amazon's capex guide is on a net basis while this row resolves on gross.
- These are statements about reported numbers, not about share prices.

---
## Desk records (repo copy)
- Registration: `data/ai_prints_backtest/forward_20261118.json` (commit `eb7bf40`, before any of these reports), made by
  `tools/ai_prints_forward.py`; logged by `tools/ledger_forward_ranges_20261118.py` through `pipeline/ledger.py add`.
- Ledger: revenue #136 AVGO, #137 ORCL, #138 MU, #139 TSM, #140 META, #141 AMZN, #142 NVDA; next guide #143-#149 in the
  same order; capex #150 ORCL, #151 MSFT, #152 META, #153 GOOGL, #154 AMZN. All P 0.80, conviction 0.62, kind markets,
  source mechanical, direction neutral, each with a resolution source and a void rule.
- Conviction: source 0.20 (company guides) + capital 0.20 (scheduled binding reports) + formal 0.10 (PASS-WITH-FLAGS:
  model designed after seeing some outcomes) + lenses 0.05 (one mechanical lens) + preconditions 0.07 (up-cycle intact,
  financing mixed) = 0.62.
- Cluster: new `ai-prints-range`, not `ai-prints`. A range call misses on an upside surprise that the threshold rows
  (#124, #127, #132, #125, #129) score as hits, so it scores the size of the surprise, not the sign: not the same bet
  restated. Open book after logging: 95 rows; `ai-prints-range` 19 (20%). Read with `ai-prints` and `ai-capex` as one
  demand bet: 31 of 95 (33%), under the 35% line but close; all AI clusters together 34 of 95 (36%), over it.
- Red-team gate (new cluster, 19 rows): (1) assumptions: the up-cycle and each company's beat habit continue, definitions
  unchanged, dates hold. (2) ACH: rival "surprise quarter" (upside miss, as Micron and Dell) and rival "financing or
  export shock" (downside miss); the 80% widths already contain two surprise quarters. (3) premortem: Nvidia shipments
  cut by the 16 Nov remote-access rule puts revenue under 133.6; Micron prices higher again. (4) cascade: none, inputs
  are filings. (5) reference class: the 29-report backtest, one up-cycle. (6) independence: one model, one regime;
  clustered, no extremizing, P held at the nominal 0.80. Trained prior for `markets` calls is 0.74 (shadow, not binding).
  VERDICT: pass at 0.80.
- Map: rows appended to `avgo-fq4`, `memory-prints`, `tsmc-q4`, `nvda-fq4`, `hyperscaler-q4-guides`; new checkpoint
  `orcl-fq2` (10 Dec) with shift edges to `ai-financing-chain` and `capex-digestion`. Gates: `web_coverage.py` OK
  (153/153), `ledger.py sweep` clean, `debug_all.py` ALL CLEAR.
