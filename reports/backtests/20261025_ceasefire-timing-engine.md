# Ceasefire-timing engine: how close to daily timing? (built and backtested 2026-10-25)

**Question asked:** can an engine predict the *day* a war pauses (ceasefire) and the *day* it resumes, tested on the hundreds of historical cases?

**Short answer:** the engine pins the day only when a ceasefire is dead on arrival:

| Kind of call | Day-level accuracy |
|---|---|
| Dead-on-arrival ceasefires (fighting back within 3 days) | **62% within ±1 day** |
| First fatal violation, when it comes within 3 days | **73% within ±1 day** (median miss 0 days) |
| Ceasefires that last 4–30 days | Weekly precision at best: 30% within ±7 days, median miss 24 days |
| Ceasefires that last 1–12 months | No day-level skill: median miss about 5 months |

Updating the forecast every day from fresh fatalities helps a lot for *ranking* the dangerous days, with AUC 0.87 against 0.66 for the baseline. It still warns of only about a third of collapses a week ahead. On the eve of an actual collapse, its median probability for "tomorrow" was 4%.

The binding constraint is that collapse timing is a discretionary decision. It is the same boundary the ledger found (STATE §2): the engine is strong on structural, datable mechanisms and weak on one decider's choice.

## What was built
- `tools/build_ceasefire_data.py` builds the case base from public data and only needs to run once.
  - **PA-X v10** (Univ. of Edinburgh) supplies 483 dated ceasefire agreements, 1990–2025, linked to UCDP conflict ids.
  - **UCDP GED 26.1** (434,601 events, 1989–2025) plus the **candidate GED for Jan–Sep 2026** supply daily state-based fatalities per conflict.
  - The three 2026 Iran-war ceasefires (4/8, 6/17, 7/25) are added by hand as a live holdout.
  - Outputs, all committed:
    - `data/ceasefire/breakdown_cases.csv`: **401 ceasefires**, 337 of which returned to war by 2026-09-30.
    - `breakdown_daily.csv`: the daily death counts after each ceasefire.
    - `ceasefire_cases.csv`: **1,380 war spells**, 175 of which reached a ceasefire.
- `pipeline/ceasefire_engine.py` (stdlib only) answers three timing questions, each as a full distribution over days:
  - `r25`: **return to war**, the first day the trailing-7-day state-based toll reaches 25.
  - `v1`: **first fatal violation**, the first day with any fatality after signing.
  - `cf`: **war to ceasefire**, from a war spell's start (onset or resumption) to the next agreed ceasefire.
- **Models**, all censoring-aware:
  - Kaplan-Meier outside view: the baseline.
  - Interval-censored log-normal AFT on pre-start features: violence in the 7/30/90/365 days before, conflict age, interstate/local/unilateral/third-party flags, prior ceasefires, prior breakdowns known at signing, and how long the last one lasted.
  - k-nearest reference class.
  - **Ensemble**: the call.
  - A **day-by-day updating model** that re-forecasts at the end of every ceasefire day from what the ceasefire has looked like so far (deaths in the last 1/3/7 days, fatal days, days since the last fatality).
- **Point call** = the median day of the predictive distribution, which minimizes expected absolute error.
- **Test discipline:** walk-forward by year from 2000. Each fit sees only cases signed before Jan 1 of the test year, and every training outcome is **censored at that cutoff**, so there is no look-ahead. Nothing in the test year informs its own forecast. The code passes sanity checks: Kaplan-Meier and censoring match hand calculations, and the AFT recovers a synthetic log-normal (intercept 2.9 vs 3, slope 0.99 vs 1, σ 1.03 vs 1).

## Results: as-of-signing engine (267 test ceasefires, 2000–2026)
| Return to war (r25) | Naive Kaplan-Meier | **Engine (ensemble)** |
|---|---|---|
| Exact day | 0.0% | **8.1%** |
| Within ±1 day | 0.0% | **17.5%** |
| Within ±7 days | 0.9% | **25.6%** |
| Within ±30 days | 7.6% | **37.2%** |
| Median miss | 103 days | **76 days** |
| C-index (ranking) | 0.44 | **0.83** |
| Brier, P(war within 30 days) | 0.231 | **0.093** (60% skill) |
| 80% interval coverage | 0.91 | 0.95 (intervals too wide) |

| Return to war, by how long the ceasefire actually lasted | Cases | Within ±1 day | Within ±7 days | Median miss |
|---|---|---|---|---|
| Collapsed on days 1–3 | 55 | **62%** | **82%** | **1 day** |
| Days 4–30 | 37 | 11% | 30% | 24 days |
| Days 31–365 | 79 | 1% | 1% | 165 days (worse than the naive 62) |
| After a year | 52 | 0% | 0% | 962 days |
| Interstate only | 25 | – | – | 27 days (naive 81) |

**First fatal violation (v1):** 26% on the exact day and 43% within ±7 days, with a median miss of 10 days (naive: 1% exact, 28% within ±7, 13-day miss). Of first violations that came within 3 days, 73% were called within ±1 day (median miss 0 days).

**War to ceasefire (cf):** C-index 0.82 and Brier skill at one year (0.21 vs 0.39), but no day precision: 2.8% within ±7 days and a median miss of 165 days. **It is unreliable for interstate wars.** History has only 43 interstate spells, 8 of which reached a ceasefire. It missed both 2026 Iran cases badly: it called 148 days for the war's onset (actual 39) and 1,288 days for the July resumption (actual 13).

## Results: day-by-day updating model (walk-forward, 46,000 test ceasefire-days)
| | Engine | Baseline (Kaplan-Meier hazard by day) |
|---|---|---|
| AUC, war **tomorrow** | **0.917** | 0.710 |
| AUC, war **within 7 days** | **0.873** | 0.664 |
| Brier skill, 7 days | +9.3% | – |
| Brier skill, tomorrow | −0.7% (well ranked, poorly calibrated in level) | – |

Live-warning simulation over 171 test collapses that came within a year:

| Alarm threshold: P(war within 7 days) ≥ | 0.5 | 0.3 |
|---|---|---|
| Collapses warned within the prior 7 days | 16% | **32%** |
| Warned 2+ days ahead | 9% | 23% |
| Median lead time | 2 days | 3 days |
| Alarm precision | 60% | 40% |

On the eve of collapse, the median P(war tomorrow) was 4.4%, so the engine does not name the day.

## Live holdout: the 2026 Iran war (UCDP conflict 16905)
| Ceasefire | Engine call at signing | Actual | Miss |
|---|---|---|---|
| 4/8: first violation | day 1 (P = 53%) | day 1 (4/9) | **exact** |
| 6/17: first violation | day 17 | day 10 (6/27) | 7 days |
| 7/25: first violation | day 3 | day 5 (7/30) | 2 days |
| 4/8: return to war | day 11 | day 95 (7/12) | 84 days |
| 6/17: return to war | day 157 | day 25 (7/12) | 132 days |
| 7/25: return to war | day 51 | none by 9/30 in GED's count* | – |

The day-by-day replay of the June 17 memorandum shows P(war within 7 days) rising to 0.47–0.53 on 7/8–7/9, after 13 and then 10 deaths. War registered on 7/12, so the warning came **3–4 days ahead**. Under the April 8 ceasefire, the engine raised a **false alarm on 5/1** (0.54, after 14 deaths); full war did not follow for 10 weeks.

\*GED's fatality count understates an air and naval strike war. The 13 nights of US strikes from 7/11 register at only 2–8 deaths a day, and the 9/1 strike wave at 19. A 25-deaths-a-week threshold is a weak proxy for "return to war" in this conflict. For Iran, read **v1 and the news tape**, not r25 alone.

**Forward view, as engine output only.** These are diagnostics, not ledgered calls, and they use GED only through 9/30.
- **War to ceasefire, from the 8/30 resumption,** given no ceasefire through 10/25: the AFT gives P(ceasefire) of **3% by 11/3, 18% by 12/31 and 45% by 2027-08-30**. The nearest-neighbour model gives about 0% because its nearest cases never reached a ceasefire. Given this direction's track record on Iran (both 2026 ceasefires came far sooner than called), **do not lean on it**.
- **If a ceasefire were signed around 11/1:**

  | | Median | 7 days | 30 days | 90 days |
  |---|---|---|---|---|
  | First fatal violation | day 12 | 39% | 75% | – |
  | Return to war (median day 93; 50% band 33–419) | day 93 | 7% | 24% | 50% |

## Verdict and what would move it closer to daily
1. **Day-level timing is achievable only for dead-on-arrival ceasefires.** For everything else the honest resolution is weeks (days 4–30) or months (beyond). Keep using the engine for **P(war within window)**, where it beats the naive baseline by about 60% on the 30-day Brier, and for **ranking which ceasefire breaks first** (C-index 0.83). Do not use it for exact dates.
2. **Fatality data carries little precursor signal.** Most collapses are a single decision, not a slow climb in violations: the median P(tomorrow) on the eve was 4%. Closing the gap needs **non-fatality precursors**, which the news pipeline already ingests: announced deadlines and expiries (the doctrine §16.12 master clock), mediator movement, strike-planning reports (capped by §16.14), NOTAMs and force posture. Next step: tag those events by date in the ingest tape and add them as daily covariates.
3. **Data upgrades:**
   - The ETH/PRIO CF dataset (2,202 ceasefires, 1989–2020) would add failed and unilateral ceasefires that PA-X misses. It is not publicly downloadable; the ETH page names Govinda Clayton as the contact for data queries.
   - ACLED would give a better daily violence series for strike wars.
4. **Calibration:** the 80% intervals cover 95% and the 50% intervals cover 69%, so the predictive distributions are too wide. A conformal-style rescaling is a cheap fix.

## Reproduce
```
python tools/build_ceasefire_data.py                              # once: download + build (about 10 s after download)
python pipeline/ceasefire_engine.py backtest --target r25         # also: v1, cf
python pipeline/ceasefire_engine.py backtest-daily --tau 0.3
python pipeline/ceasefire_engine.py live                          # Iran 2026: as-of calls + day-by-day replay
python pipeline/ceasefire_engine.py predict --case iran-2026-06-17
```
Sources: PA-X v10, peaceagreements.org (`pax_data_2257_agreements_v10.csv`). UCDP GED 26.1 and candidate GED 26.0.1–9, ucdp.uu.se/downloads. UCDP Conflict Termination v4 (interstate typing).
