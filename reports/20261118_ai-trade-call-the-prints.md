# Call the AI Prints, Not the Price

Nov 18, 2026 · GT-Analyst desk

Reported revenue is the layer of the AI trade that can be named: our exact number missed by about 1% over the last six months and 1.5% over five years, better than taking the guide as given and better than consensus in most years. Guides, capex and share prices are harder, so this note predicts revenue only and treats the rest as context.

## Key calls

We now predict one thing: each company's next reported revenue, as one exact number. Guides, capex and share prices are context, not calls: consensus has beaten us on guides every year, capex misses by about 12%, and price direction is a no-call.

| Company, quarter | Report | Company guide midpoint | **Our number** | 80% range | Threshold call |
| --- | --- | --- | --- | --- | --- |
| Broadcom FQ4 2026 | 9 Dec | $34.8bn | **$35.3bn** | 34.3-36.4 |  |
| Oracle FQ2 2027 | 9-14 Dec | $21.2bn | **$21.3bn** | 20.9-21.8 |  |
| Micron FQ1 2027 | \~15 Dec | $61.5bn | **$72.1bn** | 56.3-87.9 | at or above $61.5bn: 86% |
| TSMC Q4 2026 | 14 or 21 Jan | $53.3bn | **$54.6bn** | 53.6-55.6 | at or above $53.3bn: 90%, under review |
| Meta Q4 2026 | \~27 Jan | $74.5bn | **$76.8bn** | 75.2-78.3 |  |
| Amazon Q4 2026 | \~4 Feb | $243.5bn | **$248.6bn** | 244.2-252.9 |  |
| Nvidia FQ4 2027 | 24 Feb-3 Mar | $130.0bn | **$137.3bn** | 133.6-140.9 | at or above $130.0bn: 90% |

Dates after Broadcom's are estimates; if a company has not reported, the call waits. The full report, with five years of backtesting, is [The Path of the AI Boom](https://claude.ai/artifact/PFbtnVdXvgzd9FEStCJK1F).

## Prints: revenue can be named to about 1%, the next guide cannot

We tested a plain rule on every report from 14 AI suppliers and buyers published between 18 May and 17 November: take the company's own guide midpoint and add its average beat over its last four reports. Each forecast used only reports published before it.

&#91;embedded content: data/ai\_prints\_backtest/results\_numeric.json · 29 reports, 18 May-17 Nov 2026; consensus from data/ai\_prints\_backtest/consensus.csv\]

The revenue misses cluster in surprise quarters. Dell's May report came in 25% above its guide and Micron's June report 24% above; consensus missed them too, by 19% and 14%. Without Micron and Dell the median revenue miss was 0.96%. Next-quarter guides are different: our numbers ran about 5% low on average, because companies guided step-ups their own history did not contain, and analysts saw more of that coming.

The same rule gives one exact number for each next print, shown as the dot below. The line around it is the 80% range, the width that would have held 80% of actuals in the backtest (79% when tested out of sample); the number is its middle.

&#91;embedded content: data/ai\_prints\_backtest/forward\_20261118.json · registered 18 Nov 2026 before any of these reports\]

Micron's range is wide because its last four beats include the two largest surprises in the sample. These are statements about reported revenue, not share prices.

**One flag on TSMC.** Our 90% call that TSMC reaches its $53.3bn Q4 midpoint rests partly on a record October. Read against TSMC's usual Q4 shape, October is behind pace, not ahead:

| Year | October as % of the Q4 guide midpoint | November-December vs October | Q4 vs midpoint |
| --- | --- | --- | --- |
| 2024 | 37.1% | -11.8% | +1.4% |
| 2025 | 36.6% | -7.7% | +2.8% |
| 2026 | 34.6% | due \~10 Dec and \~10 Jan | due 14 or 21 Jan |

If 2026 repeats either year's shape, Q4 lands at $50.5-51.8bn, below the midpoint. The midpoint needs November and December to hold close to October's level. The 90% is under review: our red-team puts it nearer 65%. November revenue, out about 10 December, settles most of it; below about NT$560bn the midpoint is out of reach unless December rises.

## Financing: if this cycle fails, it fails first in the bond market

Two laws from past capex booms set the frame. Equities peaked before capex in all four booms with usable dates (UK railways 1845, Cisco 2000, Nvidia 2018, the chip index 2022), so rising capex guides do not mark a price floor. And the depth of the eventual cut scaled with outside funding: debt-funded telecom carriers cut about 60% from 2000 to 2002, while cash-funded hyperscalers cut 2% for two quarters in 2019. The variable to track is the funding mix, not demand.

| Test | Cash-funded | Debt-funded | Reading on 18 Nov 2026 |
| --- | --- | --- | --- |
| Hyperscaler free cash flow | Positive | Negative | Negative at Alphabet, Meta, Oracle and (12 months) Amazon; Microsoft positive |
| Bond issuance against forecast | At or below | Above | $296bn year to date against Goldman's $250bn full-year forecast |
| Off-balance-sheet vehicles | Rare | Pricing wider each deal | 6.58% in 2025 to above 7% in July 2026, same tenant |
| The weakest borrower's access | Open | Shut | No high-yield data-center deal since late September; CoreWeave CDS about 1,113bp |
| The vendor as guarantor | No | Yes | Nvidia guarantees of $108.5bn (July) to about $118bn (October, press) |

All five read debt-funded for the marginal builder. The four big buyers still have balance sheets, so the neoclouds and single-tenant vehicles sit in the deep-cut class if access stays shut, and the hyperscalers sit between that and 2019.

**A correction on Nvidia.** The widely repeated "$530bn of guarantees" is total commitments plus guarantees. In the 10-Q for the quarter to 26 July 2026, guarantees were $108.5bn ($105.0bn on one OpenAI-leased campus, $3.5bn on land, power and shell); the rest is $366bn of commitments and $56bn of additional commitments, mostly Nvidia's own supply purchases. Our 18 November tape note repeated the wrong figure and has been corrected. The test is the next 10-Q: flat or shrinking support lines would mean Nvidia is pulling back, and its interim chief executive said on 17 November that guidance now considers "customers' access to capital".

## Catalysts to 30 June 2027

&#91;embedded content: research\_notes/AI trade forecasting framework/catalyst\_calendar\_consensus.md · 11 dated catalysts\]

The December prints test the suppliers; the late-January guides test the buyers. A first 2027 guide below 2026 from any of the four hyperscalers would be one of the two triggers for the second-leg branch; all four above 2026 with credit reopening is the repair path.

## What we do not call, and the limits

| No call | Why |
| --- | --- |
| AI share-price direction | Prints do not predict the reaction; valuation explains little of one-year returns |
| The Anthropic listing (ANT) | The analyst writing this note is an Anthropic model |
| Government decisions on chip exports | The 16 November rule came days before a summit; such decisions are not forecastable with confidence |
| The PJM capacity auction | New rules exclude new large loads, so three cap-clears are no longer a base rate |

Three limits. The six-month backtest covers one up-cycle; the five-year test in the full report shows the rule weakens in a downturn, when consensus did much better. The rule was designed by an analyst who had seen some of the outcomes, so only the row-by-row forecasts are blind; the clean test is the seven revenue numbers above. Several historical base rates rest on secondary sources and carry half weight until checked against primary data.

This note states direction and mechanism only. It is analysis, not investment advice, and it gives no position sizes.

## Sources

Repo data (every chart names its file): `data/ai_prints_backtest/results_numeric.json`, `consensus.csv`, `capex_history.csv`, `prices.csv`, `forward_20261118.json`; `data/timelines.json`; `research_notes/AI trade forecasting framework/`. Full citations are in the markdown copy, `reports/AI trade forecasting framework.md`.

- [Nvidia 10-Q, quarter to 26 July 2026](https://www.sec.gov/Archives/edgar/data/0001045810/000104581026000075/nvda-20260726.htm) and [Q3 FY27 results](https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-third-quarter-fiscal-2027)
- [TSMC Q4 2026 guide (6-K)](https://www.sec.gov/Archives/edgar/data/0001046179/000104617926000726/a3q26e_withguidancexfinal.htm) and [October 2026 revenue (6-K)](https://www.sec.gov/Archives/edgar/data/0001046179/000104617926000796/tsm-revenue20261110.htm); [Q4 2025 results](https://pr.tsmc.com/english/news/3281), [Q4 2024 results](https://pr.tsmc.com/english/news/3201), [November 2025 revenue](https://www.sec.gov/Archives/edgar/data/1046179/000104617925000137/tsm-revenue20251210.htm), [November 2024 revenue](https://pr.tsmc.com/english/news/3195)
- [Broadcom Q4 date](https://investors.broadcom.com/news-releases/news-release-details/broadcom-inc-announce-fourth-quarter-and-fiscal-year-2026); [Micron fiscal Q4 prepared remarks](https://s25.q4cdn.com/621799436/files/doc_financials/2026/q4/Q4-FY26-Prepared-Remarks.pdf)
- [CNBC on Nvidia's guarantees and guidance, 17 Nov](https://www.cnbc.com/2026/11/17/nvidia-nvda-earnings-report-q3-2027.html); [CNBC on AI credit stress, 6 Nov](https://www.cnbc.com/2026/11/06/coreweave-bond-yield-tops-16percent-as-ai-credit-stress-rises.html); [CNBC, Apollo on AI debt, 17 Nov](https://www.cnbc.com/2026/11/17/apollo-ceo-marc-rowan-on-ai-debt.html)
- [IFR on AI ratings and CDS](https://www.ifre.com/topic-codes/2509450/cds-market-flashes-warning-on-ai-ratings-downgrades); [IMF Global Financial Stability Report, Oct 2026, ch. 1](https://www.imf.org/-/media/files/publications/gfsr/2026/october/english/ch1.pdf)
- [Doms, FRBSF, on telecom capex](https://www.frbsf.org/wp-content/uploads/er19-34bk.pdf); [Synergy Research on 2019 hyperscale capex](https://www.srgresearch.com/articles/hyperscale-operator-capex-takes-a-breather-in-q1-down-2-from-2018); [QuantFlowLab chip-drawdown table](https://quantflowlab.com/?p=936) (secondary)
- [YieldTheory hyperscaler capex tracker](https://www.yieldtheory.app/research/hyperscaler-capex-2027-forecast); [Startup Fortune on the BofA November survey](https://startupfortune.com/fund-managers-cut-tech-the-most-since-2006-but-they-still-own-it/) (secondary)
- [Focus Taiwan on the NT dollar, 11 Nov](https://focustaiwan.tw/business/202611110004)

---

# APPENDIX: DESK RECORDS (repo copy only)
- Revenue-only edition from 17 Nov PT. Full report: reports/20261118_ai-boom-full-report.md.
