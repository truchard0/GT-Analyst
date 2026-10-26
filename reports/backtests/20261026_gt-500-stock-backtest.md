# 500 GT stock predictions over the last month: what went right and wrong
*Built and scored 2026-10-26. Cohorts on Sep 25, Oct 2, Oct 9 and Oct 16, each resolved one week later.*

**Bottom line:** the engine as it stood before this session's patches **lost**:

| Metric | Engine (v0) | Coin flip |
|---|---|---|
| Hit rate | **43.2%** (216/500) | 49.8% |
| Brier score | **0.260** | 0.25 |
| Top-minus-bottom spread | **−2.8% per week** | – |

It also did no better than plain momentum (44.0%).

The loss has one dominant cause, a misapplied doctrine rule: the §16.12 "oscillation" fade, applied to stock prices. Remove that rule and the same engine scores **54.0%**. The engine's *confidence* was informative: calls at P ≥ 0.60 hit **63%** (144 calls); calls below that hit 35%.

Its biggest blind spot was the month's largest move. The AI-complex crash of Oct 9–16 (−15% to −21% vs SPY) was an AI-financing event, which no GT rule can see.

**Statistical caveat (read before anything else).** There are four weeks of outcomes, and the calls within a week are correlated: the same sector call drives many rows. There are about 64 independent (week, sector) clusters. The 95% confidence interval for v0's hit rate is **[0.35, 0.52]**. One month cannot separate skill from luck; it can only say which rules *hurt*, and point to what needs a forward test.

---

## 1. Design: how "no forward look" was enforced
- **Calls:** each is whether a stock beats SPY over 5 sessions (stock minus SPY), made at a Friday close and scored at the next Friday's close. The target strips out market direction, so it tests the GT *sector* call.
- **Universe:** 125 stocks with the highest median dollar volume over the 60 sessions ending **9/24**. The candidate pool was `watchlist.json` + `data/sector_map.json` + a fixed list of sector leaders (energy, staples, utilities, financials, healthcare, discretionary, airlines) for sectors the doctrine names but the watchlist barely covers.
  - The same 125 names are used every week: 4 × 125 = **500**.
  - **Composition:** about half is the AI complex (semis 18, neocloud 17, memory 9, photonics 9, hyperscalers 9). The rest: defense 10, energy 9, staples 8, financials 7, healthcare 6, robotics 6, discretionary 6, utilities 4, airlines 3, space 2, power 2.
- **Inputs:** only data stamped at or before the as-of close:
  - Yahoo daily closes, Brent (BZ=F), and the Treasury 2-year yield.
  - 2,469 Google News headlines with "Iran", "Hormuz" or "Houthi" in the title, each filtered by its own publication time (before 20:00 UTC, the 4pm New York close).
  - Earnings dates and BLS print dates, which are scheduled weeks ahead.
- **Look-ahead proof (in code):** for every cohort, `predict()` is re-run on a copy of the data with every price, yield and headline after the as-of moment **deleted**. The script asserts the output is identical, and it was.
- **Pre-registration:** the 500 predictions were committed *before* any outcome was computed:
  - Commit `f78913d`.
  - `predictions.csv` SHA-256 `8ff31ff9…103f1b`.
  - Re-running after scoring reproduces the same hash.
- **Doctrine version:** the rules encode the skills **as they stood before the 10/25 patches**, because those patches were written knowing Aug–Oct outcomes. The patched variant ("v1-hindsight") appears only as a labeled comparison.
- **Residual contamination risk, stated plainly:** I wrote the rules on 10/26, after seeing some of the month's tape during the 10/25 relaunch. The defenses are the ones above: rules taken from the doctrine text, weights fixed before scoring, and pre-registration. The losing result is itself some evidence the rules weren't tuned to the outcome.

### The rules (v0), each tied to its doctrine section
| Rule | Doctrine | What it does |
|---|---|---|
| R1 branch | market-transmission §1/§4/§10 | Brent 20-session trend + 2-year yield 10-session change → **B** (supply/hawkish), **A** (generic/dovish, the default) or good-oil; weight 1 / 0.5 / 0.25 |
| R2 sector map | market-transmission §12, §5; doctrine §10.8, §11.2, §11.4 | Branch → sector tilt. In B: energy, tankers, defense, staples up; AI complex, space, airlines down |
| R3 war economy | doctrine §10.10/§12.5 | Defense +0.25 while the war is live |
| R4 oscillation | doctrine §16.12 | Headline escalation index; fade spikes along the Branch-B vector (−0.35 × z) |
| R5 catalysts | market-transmission §13e | Earnings inside the window halve the score; payrolls/CPI scale the branch terms by 0.75 |
| R6 momentum | contrarian #7 | A call against a top/bottom-tercile 12-1-month mover is halved |

Probability: P = 0.5 + 0.18·tanh(|score|), so the maximum is about 0.68.

What the engine saw at each as-of moment (all point-in-time):

| As-of | Branch | Brent, 20d | 2y, 10d | Headline escalation index (z vs prior 4 wks) |
|---|---|---|---|---|
| 9/25 | **B**, full weight | +16.3% | +18 bp | 0.63 (z −1.8) |
| 10/2 | **B**, full weight | +7.1% | +7 bp | 0.33 (z −2.0) |
| 10/9 | A, default 0.25 | +0.1% | −1 bp | 0.88 (z +0.9) |
| 10/16 | A, default 0.25 | +5.8% | −4 bp | 0.93 (z +1.2) |

## 2. Results
| Model (same 500 rows) | Hit rate | Brier | Top − bottom / wk | Mean rank IC |
|---|---|---|---|---|
| **GT v0 (pre-registered)** | **43.2%** | 0.260 | −2.8% | −0.15 |
| v1-hindsight (10/25 patches, contaminated) | 41.6% | 0.260 | −2.9% | −0.21 |
| Momentum 12-1 | 44.0% | 0.262 | −1.8% | −0.11 |
| Reversal 1-week | 39.4% (so 1-week *continuation* = 60.6%) | 0.297 | −3.7% | −0.30 |
| Sector momentum 20d | 48.8% | 0.268 | −1.6% | −0.07 |
| Coin flip | 49.8% | 0.250 | – | – |

Every naive baseline also lost. It was a month of violent sector rotation that punished standard factors.

### Week by week
| Week (as-of → resolve) | v0 | Branch layer only | v1-hindsight | What happened (context added afterward, not model input) |
|---|---|---|---|---|
| 9/25 → 10/2 | **31%** | 31% | 49% | Branch B called the AI complex down; instead it **ripped** (memory +9.0% vs SPY, photonics +9.9%, semis +4.7%) while SMH climbed toward its 10/6 peak. Energy +2.4% ✓. Defense −2.4% and staples −1.9% ✗. |
| 10/2 → 10/9 | **67%** | 67% | 43% | Branch B **right**: AI complex −3.5% to −7.3% (photonics, semis, neocloud, memory), power +14%, energy +2.3%. The S&P set a record 10/6, then the AI complex rolled. |
| 10/9 → 10/16 | **29%** | 58% | 29% | The headline fade (R4) read rising escalation as about to mediate and **flipped** the calls to AI-up, energy-down. The AI complex **crashed** (photonics −19.7%, neocloud −16.4%, memory −15.3%, space −20.9%) and energy **rose** 7.0% (Brent +4.9% that week). |
| 10/16 → 10/23 | **46%** | 59% | 46% | Same R4 drag: neocloud −6.0%, photonics −9.6%; energy +2.8%, utilities +2.9%. |

### Sectors (realized median excess vs SPY, %; the engine's majority call in brackets)
| Sector | 9/25 | 10/2 | 10/9 | 10/16 | v0 hit |
|---|---|---|---|---|---|
| Photonics | +9.9 (−) | −3.5 (−) | −19.7 (+) | −9.6 (+) | **19%** |
| Staples | −1.9 (+) | +2.9 (+) | +7.1 (−) | +0.8 (−) | 31% |
| Neocloud | +0.2 (−) | −7.1 (−) | −16.4 (+) | −6.0 (+) | 35% |
| Defense | −2.4 (+) | −0.5 (+) | +2.8 (+) | +1.3 (−) | 38% |
| Semis | +4.7 (−) | −5.3 (−) | −7.1 (+) | −0.9 (+) | 39% |
| Hyperscalers | +0.1 (−) | +1.2 (−) | −0.1 (+) | −0.4 (+) | 39% |
| Financials | −2.9 (+) | −0.3 (+) | +0.4 (−) | −0.9 (−) | 39% |
| Memory | +9.0 (−) | −7.3 (−) | −15.3 (+) | −0.9 (+) | 44% |
| Energy | +2.4 (+) | +2.3 (+) | +7.0 (−) | +2.8 (−) | 50% |
| Healthcare | −2.8 (+) | +0.9 (+) | +6.2 (+) | +1.8 (+) | 62% |
| Discretionary | −2.5 (−) | +1.5 (−) | +8.3 (+) | +3.2 (+) | 71% |
| Airlines | −1.1 (−) | −3.4 (−) | −6.1 (+) | +2.3 (+) | 75% |
| Power | −0.3 (+) | +14.4 (+) | −5.4 (−) | −6.8 (−) | 88% |

**Energy outperformed SPY every single week (+2.3% to +7.0%)**, the clearest GT signal of the month. The engine got it right only in the two weeks the branch layer was allowed to speak. In the other two, the headline fade flipped energy to "underperform".

## 3. Attribution: which rule did what
| Same 500 rows, sign recomputed from… | Hit rate |
|---|---|
| Full v0 score (R1–R6) | 43.2% |
| **R1+R2 branch/sector only** | **54.0%** |
| R1+R2+R3 (with the war-economy tilt) | 54.0% |
| R4 headline-oscillation fade only | **40.8%** |
| R4 *reversed* (follow escalation, don't fade it) | 59.2% |
| Branch tilt reversed | 41.6% |

- **R4 (§16.12) cost about 11 points.** It is the same mistake as August's #74 and #76: fading the war premium while the chokepoint was physically shut. That is three occurrences, which makes a patch mandatory: **jiang §16.12c**.
- **R1 (the 2-year gate) misclassified weeks 3 and 4.** Oil was up and Hormuz shut, but the 2-year didn't rise, so the engine defaulted to A at 0.25 weight. Even that weak defensive A tilt hit 58–59%. This is a **provisional** patch, **market-transmission §4.1**: a physical closure needs no 2-year confirmation. It rests on only two weeks, so it is forward-test only.
- **The AI-complex leg was a coin flip.** It was wrong in week 1 and right in week 2. The hindsight §5.1 proxy fixed week 1 and broke week 2. The crash in week 3 was an AI-*financing* event, a feed the GT layer doesn't have: **market-transmission §5.2**, a coverage gap, with AI calls capped at 0.55.
- R5 and R6 only scale scores and never flip a direction, so they don't change the hit rate. Names with earnings in the window hit 62% (n = 34), against 42% without; that is noise-level.

## 4. Calibration: the one thing that clearly worked
| Engine probability | Calls | Hit rate |
|---|---|---|
| 0.50–0.55 | 202 | 40.6% |
| 0.55–0.60 | 154 | **27.9%** |
| 0.60–0.65 | 69 | 58.0% |
| 0.65–0.70 | 75 | **68.0%** |

Within each week, the higher-confidence calls did better:

| Week | P ≥ 0.60 | P < 0.60 |
|---|---|---|
| 9/25 | 49% | 22% |
| 10/2 | 69% | 58% |

The engine's **P ≥ 0.60 calls hit 63% (n = 144)**, about what it claimed (0.64). Weeks 3 and 4 produced *no* calls above 0.60; the engine flagged its own lack of edge, then made 250 calls anyway. **Patch: contrarian Part C abstain zone.** Mechanical outputs below P 0.60 are "no view", not predictions. The caveat: the confident calls come from only two weeks.

## 5. What went right
1. **The core sector map (market-transmission §12) had positive information:** 54% without the bad rule.
2. **Energy outperformed every week**, as the supply branch says it should. The Brent pass-through (Brent +16% over 20 sessions to 9/25, then $116 by 10/23) was the dominant GT fact of the month, and the branch layer read it.
3. **The 10/2 week (67%):** Branch B called the AI complex's turn and the power-name surge.
4. **Confidence ranked accuracy.** The rubric's instinct, that conviction should predict hit rate, held.
5. **The machinery held:** point-in-time inputs, an asserted no-look-ahead proof, and pre-registration with a verified hash.

## 6. What went wrong
1. **A doctrine rule applied outside its scope** (§16.12 to prices), for the third time. **About 11 points.**
2. **Fighting the AI complex's momentum** in week 1 (+39% 6-month excess vs SPY): the §5.1 miss-shape again.
3. **The 2-year gate** blinded the supply branch in weeks 3–4.
4. **No AI-financing lens.** The largest cross-sectional move of the month (−15% to −21% in a week) came from neocloud credit stress, outside the geopolitical frame.
5. **Making low-confidence calls at all:** 356 calls below 0.60 hit 35%.
6. **"Outperform" calls hit only 38%,** against 49% for "underperform". The engine tilted long into the AI complex exactly when it broke (weeks 3–4, via R4).

## 7. Patches written (learning loop)
| Patch | Status | Evidence |
|---|---|---|
| **jiang §16.12c:** oscillation is a kinetic-event rule, never an asset-price fade while a chokepoint is impaired | **Mandatory** (3rd occurrence: #74, #76, this) | R4 alone 40.8%; reversed 59.2% |
| **market-transmission §4.1:** physical closure → SUPPLY without 2-year confirmation (the 2-year sets the weight) | **Provisional**, forward-test only | Weeks 3–4 only |
| **market-transmission §5.2:** AI-complex calls capped at P 0.55 until an AI-financing stress index exists | **Coverage gap**, top priority | Week 1 vs week 2; the week 3 crash |
| **contrarian Part C:** abstain below P 0.60 for mechanical lenses | Provisional | 63% vs 35% |

**The v2 candidate** combines §16.12c, §4.1 and the abstain rule. It scores **58.4%** on this month (64.6% on its 79 calls at P ≥ 0.60), but **that is in-sample and counts for nothing**; it was written after seeing v0's results. It exists to be tested forward:
```
python tools/gt_backtest_data.py                        # refresh inputs after that Friday's close
python tools/gt_stock_backtest.py forward 2026-10-30 --hormuz-impaired 1   # flag from the tape (Kpler/PortWatch) that day
```

## 8. Reproduce
```
python tools/gt_backtest_data.py          # downloads: prices, 2y, headlines, earnings (~5 min)
python tools/gt_stock_backtest.py predict # with the COMMITTED data files, the 500 calls hash to 8ff31ff9…
                                          # (a fresh download can shift adjusted closes in the 4th decimal)
python tools/gt_stock_backtest.py score   # results + baselines + cluster bootstrap
python tools/gt_stock_backtest.py insample-v2
```
**Files** (in `data/gt_backtest/`):
- Calls: `predictions.csv`, the 500 calls, each with probability, falsifier, component scores, and the as-of features.
- Scores: `scored.csv`.
- Comparisons: `comparisons_scored.csv` (v1 and the baselines).

These are backtest rows, deliberately **not** written to `ledger.db`. Adding 500 correlated, already-resolved calls would corrupt the live calibration record and break the cluster cap.

**Data notes:**
- 15 of the 345 candidates had no usable Yahoo history:
  - 11 symbols no longer exist under the watchlist's ticker (e.g. ABB's US delisting; Embraer is now EMBJ; PSTG).
  - QRVO and SKYT returned no prices for the period.
  - SATS has only 4 days.

  Some of these (e.g. PSTG) might have made the top 125. That is a small universe gap caused by stale watchlist tickers, not look-ahead. **Fix the watchlist symbols.**
- Returns use dividend-adjusted closes.
- Headline coverage is missing 10/11 (fetch error).
