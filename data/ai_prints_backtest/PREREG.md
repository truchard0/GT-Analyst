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
