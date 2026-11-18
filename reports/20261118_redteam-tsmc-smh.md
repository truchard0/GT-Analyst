# Red-team: the TSMC revenue call and the SMH call (17 Nov 2026 PT)

Run with `pipeline/ledger.py redteam` and the contrarian-red-team gate (key assumptions, rivals, premortem, cascade,
reference class, independence). No probability was changed: no rule in `CLAUDE.md` requires it. Both recommendations
below are for the user to decide.

## TSMC Q4 2026 revenue at or above US$53.3bn (#127, 90%, resolves 22 Jan 2027)

**What it rests on.** (1) TSMC's own guide, US$52.3-54.3bn at NT$31.8 (6-K, 15 Oct). (2) The beat habit: TSMC beat its
midpoint in all 6 quarters on file, and all 29 reports in the prints backtest beat. (3) October revenue of NT$586.89bn,
read as "34.6% of the midpoint in one month", that is, ahead of pace.

**The red-team finding: read against TSMC's own Q4 shape, October is behind pace, not ahead.** In the last two years
October was TSMC's biggest month of Q4, and November and December ran 8-12% below it.

| Year | October as % of the guide midpoint (NT$ at the guide rate) | Nov-Dec average vs October | Q4 result vs midpoint |
|---|---|---|---|
| 2024 | 37.1% | -11.8% | +1.4% |
| 2025 | 36.6% | -7.7% | +2.8% |
| 2026 | **34.6%** | ? | ? |

If 2026 repeats either year's shape relative to its guide, Q4 lands at **US$50.5bn (2024 shape) or US$51.8bn (2025
shape)**: below the midpoint, and in the first case below the low end. To reach the midpoint, November and December must
average about NT$554bn a month at the guide rate, or NT$581bn if the NT$ stays near 32.8 (it traded 32.8-33.0 in early
November). That is October's level or 1% under it, against the 8-12% drop of the past two years. Aug-Sep 2026 averaged
NT$513bn.

**What would falsify it.** Reported Q4 revenue below US$53.3bn. Early read: November revenue, out about 10 Dec. Below
about NT$560bn puts the midpoint out of reach unless December rises; at or above October's NT$587bn makes the call safe.

**Does it double-count evidence?** Not within the row: the guide, the beat habit and October are different items. The
problem is that October was read the wrong way. Across rows, yes: the new mechanical range call on the same print
(#139, 53.59-55.60) sits entirely above #127's threshold, so on the downside the two are one bet. The capex call on the
same report (#128) rests on different evidence.

**Gate.** Assumptions: Nov-Dec hold near October; no shipment slip into Q1; the beat habit holds. Rival: "October was the
quarter's peak, as in 2024 and 2025"; the October share above is diagnostic for that rival, not against it. Premortem:
November prints NT$540bn, December NT$550bn, Q4 comes in at US$51.5-52bn. Cascade: none, all inputs are filings.
Reference class: midpoint beats 6 of 6 (TSMC) and 29 of 29 (backtest), but every one in a quarter where October-type
data did not lag the usual shape. Independence: guide, beat habit and October are all TSMC's own reporting on one order
book; no extremizing credit.

**Recommendation (yours to decide): cut #127 from 90% to about 65%,** or hold and let the 10 Dec November print decide.
The AI-trade skill allows a print call below 80% with a named reason; the Q4 shape is that reason. Sources:
[TSMC Nov 2025 report](https://www.sec.gov/Archives/edgar/data/1046179/000104617925000137/tsm-revenue20251210.htm),
[TSMC Q4 2025 results](https://pr.tsmc.com/english/news/3281),
[TSMC Nov 2024 report](https://pr.tsmc.com/english/news/3195), [TSMC Q4 2024 results](https://pr.tsmc.com/english/news/3201),
[TrendForce on the Q4 2024 guide](https://www.trendforce.com/news/2024/10/17/news-tsmc-expects-q4-revenue-to-surpass-usd-26-1-billion-revises-full-year-revenue-forecast-upward/),
[Focus Taiwan, NT$ on 11 Nov 2026](https://focustaiwan.tw/business/202611110004),
[Trading Economics, NT$ near 33](https://tradingeconomics.com/taiwan/currency/news/598953). December figures are
derived: Q4 total less October and November.

## SMH closes below 671.83 on 30 Jun 2027 (#135, 90%)

**What it rests on.** One reference class: seven completed SOX drawdowns of 20%+ since 2004 (secondary source,
QuantFlowLab). SMH peaked on 22 Jun 2026 and was 31.5% down on 17 Nov, five months in. 30 Jun 2027 is 12.3 months after
the peak. Supporting, not load-bearing: credit stress and a hiking Fed say the trough is not in.

**Two ways to read the same table, and they disagree.**
| Reading | Count | P(still below the high on 30 Jun) |
|---|---|---|
| From the peak: regained the high within 12.3 months of the peak | 1 of 7 (2020, at 3.5 months; 2018 at 12.7 just missed) | 6 of 7 = 86% |
| From the peak, only episodes still in drawdown 5 months in | 0 of 6 | about 88% |
| From the trough, if the trough is already in: regained within 7.5 months | 4 of 7 | 43% |

The writer's flag is the third row. The reference class itself says the trough is probably later: in all six episodes
that were still falling at month 5, the low came at 5.6 to 16.2 months. The first two rows are the better measure,
because long, deep drawdowns also had long recoveries. They support 86-88%, slightly under the 90% logged.

**What would falsify it.** An SMH close at or above 671.83 on 30 Jun 2027. Early signs: SMH back above 520 by February
(the repair branch), CoreWeave CDS below 700bp, a high-yield data-center deal clearing, a Fed turn to cuts.

**Does it double-count evidence?** No. The credit stress behind "trough not in" is the same evidence as the two financing
calls (#133, #134), but those bet the chain holds while #135 profits from stress lasting, so the rows offset rather than
stack. The capex-print calls bet demand stays strong, again the opposite sign. One data flag: the repo's price file
(`data/ai_prints_backtest/prices.csv`) has SMH's highest close at 668.91 on 22 Jun, not 671.83. The threshold should be
checked against the resolution source before 30 Jun; the 0.4% gap does not change the read.

**Gate.** Assumptions: no V-shaped recovery; the 2026 episode behaves like the seven; SMH tracks SOX. Rival: "the low was
in on 29 Jul or is in now, and a 2020/2024-style recovery follows"; the from-peak table is diagnostic against it.
Premortem: Fed cuts in March, 2027 capex guides come in 25%+ above 2026, SMH +46% by June. Cascade: none. Reference class:
n = 7, secondary source, weighted half until checked. Independence: single lens, no extremizing.

**Recommendation (yours to decide): trim #135 from 90% to about 87%.** The skill's rule for tail calls says to log at the
base rate, and the base rate is 86-88%. The difference is small; the call stands.
