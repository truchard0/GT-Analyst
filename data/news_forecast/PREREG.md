# News-informed forecast of AI prints: rules fixed BEFORE any forecast is made (18 Nov 2026 UTC)

**Question (user, 18 Nov 2026):** "could it not just look at all the news surrounding a company and use that to make a
more informed prediction?" Design in `STATE.md` §7l. This file is committed before any packet is shown to a forecaster.

## What it predicts
For each quarterly report in the test window, made blind before the report:
- **Primary target, N2:** the midpoint of the next-quarter revenue guide the company gives with the report. This is the
  target where the mechanical model lost to consensus in the backtest (median miss 5.6% vs 3.7%).
- **Secondary target, N1:** the revenue reported for the quarter.
Each forecast is a point and an 80% range, plus the packet items that moved it off the mechanical number.

## Test window (clean subset only)
Reports published **1 Aug 2026 to 17 Nov 2026** from the backtest sample (`data/ai_prints_backtest/results_numeric.json`
rows): 17 reports. Reason for the start date: the dated headline cache (`data/ai_stress/headlines.csv`) begins on
31 Jul 2026, and reports after June 2026 are past the forecaster model's training data. Reports before August are not
used (no dated news, and possible training-data leakage).

Sets, defined from figures already known when this file was written (the backtest has been run, so the sets are chosen
knowing which quarters were surprises; that is the point of the test):
- **Set A, surprises analysts also missed:** consensus next-quarter estimate missed the actual guide midpoint by 5% or
  more: AMAT 13 Aug, DELL 1 Sep, MU 30 Sep, TSM 15 Oct (4 reports).
- **Set B, surprises the mechanical model missed:** mechanical N2 missed by 10% or more: MU 30 Sep, ASML 14 Oct,
  META 21 Oct, AMZN 29 Oct, AMD 3 Nov (5 reports).
- **Test set = A ∪ B** (8 reports). **Control = the other 9** (where news could also make things worse).

## The packet (the only thing the forecaster sees), built by `tools/news_forecast.py packets`
Everything dated strictly before 00:00 UTC on the report date. Nothing from the report itself or later.
1. The company's own last four reports: guide midpoint, actual, next guide (from the prints files).
2. The mechanical forecast for this report (N1 and N2 point and 80% range, as scored in the backtest).
3. Peer prints published in the 90 days before: every other company in the prints files, actual vs its guide and its
   next guide vs its actual.
4. Buyer capex statements published in the 120 days before (`capex_history.csv`): quarterly capex and annual guide.
5. TSMC monthly revenue released before the report date (6-K filings; release dates in the packet).
6. Headlines from `data/ai_stress/headlines.csv` published in the 45 days before: up to 40 most recent that name the
   company, and up to 40 most recent on the AI-chip/capex theme. Titles only.
Excluded: `consensus.csv` (it is the benchmark), any analyst estimate not already in a headline title, all prices.

## The forecaster
A fresh Claude subagent per report (one packet each, so no later packet can leak into an earlier answer), told to use
no tools and to answer from the packet alone. Limits stated now: the instruction cannot be enforced or audited from
here (no tool-free API or CLI is installed on this PC), and the packet headlines are titles of a financing-focused
cache, thin for semicap names (TSMC, ASML, KLA, Lam, Applied have 0-2 matching titles each).

## Scoring (`tools/news_forecast.py score`)
Four forecasts on the same rows: naive (this quarter's guide unchanged), mechanical, mechanical + news, consensus.
Per set: median and mean absolute % error; how many rows news beat mechanical and beat consensus; 80% range coverage
(news and mechanical).

## Pass bar (set now)
1. **News helps (primary):** on the test set (8), news median absolute N2 error is below mechanical's AND news is
   closer than mechanical on at least 5 of 8.
2. **No harm:** on the control set (9), news median N2 error is no more than 0.5 points worse than mechanical's.
3. **Within reach of consensus:** on all 17, news median N2 error is within 1.0 point of consensus's.
4. Secondary (reported, not a pass line): the same three for N1 revenue.
All three lines must pass for "news-informed beats the baseline". Results are reported as first run, including a fail.
Nothing is wired into the ledger, the timeline or any report call.
