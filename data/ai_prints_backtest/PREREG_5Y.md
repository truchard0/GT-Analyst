# AI prints backtest, 5 years: rules fixed BEFORE the extra data is gathered (18 Nov 2026 UTC, 17 Nov PT)

**User instruction, 17 Nov 2026 PT:** "full version and 5 years of backtesting", "on a thinner list for the full backtest".
Extends the 6-month test in `PREREG.md` (V1 boolean rules and V2 numeric model) to five years. Nothing about the
model changes. Committed before any of the 2020-2025 rows below is collected.

## Sample (fixed)
- **Revenue and next-quarter guide (V2 N1, N2; V1 R1, R2, R4):** NVDA, AVGO, MU, TSM, AMZN, META.
- **Quarterly capex (V2 N3):** MSFT, GOOGL, AMZN, META.
- **Scored window:** every quarterly report published **18 Nov 2021 to 17 Nov 2026** inclusive.
- **Warm-up history (never scored):** reports published 18 Nov 2020 to 17 Nov 2021, so the first scored row has up to
  four earlier reports.
- The 6-month window already scored (18 May to 17 Nov 2026) is part of the 5 years; it is reported both inside the
  total and separately, so nothing already published is hidden or re-run differently.

## Model, rules and scoring
Unchanged from `PREREG.md`: the same point and range formulas (walk-forward, last up to 4 reports, pooled when fewer
than 2), the same baselines (B0 naive; B1 consensus where collected), the same pass lines (accuracy, calibration 65-95%,
tightness ±2% / ±4% / ±8%), the same V1 stated probabilities (R1 0.86, R2 0.72) and the R4 reaction check.

## Splits reported (decided now)
1. By year of report (Nov-Nov years 1 to 5).
2. Up-cycle vs down-cycle quarters. A report counts as down-cycle when the company's next-quarter guide midpoint is
   below the quarter's actual revenue (a guided decline). This is defined from data, not chosen after looking.
3. By company.
4. The 2022-2023 downturn is the test the 6-month sample could not run: does the revenue model still beat the naive
   guide, and do R1 and R2 still hold, when guides were being cut?

## Data rules
- Guides and actuals from the company's own earnings release (SEC 8-K Exhibit 99.1, TSMC 6-K, company IR), tagged
  primary; anything else tagged secondary with the source named. No cell is estimated; a missing figure stays blank.
- Consensus: collected only where results-day press coverage states it with a named provider (LSEG/Refinitiv, FactSet,
  S&P Capital IQ, Bloomberg). Consensus results are reported on that subset only, with its size.
- Prices for R4: next-session close vs the close before the report, from a market-data feed, recorded with the source.

## What this test is NOT
- Not blind on design: the model was written in Nov 2026 by an analyst who knows how 2022-2026 went. The model is
  mechanical, so the row-by-row forecasts cannot use that knowledge, but the choice of rule could have.
- Not a test of judgment calls, the financing layer or the news-informed forecast (no point-in-time news archive
  exists before 31 Jul 2026).
