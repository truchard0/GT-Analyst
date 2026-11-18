# GT-Analyst — LIVE STATE (handoff doc)
**Last updated: 2026-11-18 (practice questions on world events, written from the news and settled by the news, §7j; cloud runs off; server loop + learning loop built, §7i and §9; tape note: Gulf tit-for-tat, Brent 93, December hike priced, Nvidia after Huang; new calls #86, #87, §7h; war-driven price calls banned).** Read this first after any context reset. It records what
the engine IS, what it has LEARNED, and what is currently STAKED. Everything here can be rebuilt from
`ledger/ledger.db` and `data/timelines.json`; this is the summary.

---

## 1. WHAT THE ENGINE IS
A game-theory news-analysis prediction machine.
- **Ingest:** about 38 RSS feeds and 5 JSON APIs, every 5 minutes (`pipeline/ingest.py`).
- **Watchlist:** matches feed items to tickers and can auto-fire headless analysis.
- **Bookkeeping:** a **Brier-scored prediction ledger** and a **time-lane timeline map**.
- **Reasoning layer:** four skills in `.claude/skills/`: `jiang-doctrine`, `formal-game-theory`,
  `market-transmission` and `contrarian-red-team`.
- **NEW (10/25): a ceasefire-timing engine** (`pipeline/ceasefire_engine.py`). See §7b.

**Key distinction to keep honest:** the engine *computes* coherence, parlays, shift propagation and Brier
scores. The *probabilities themselves are analyst judgment* stored as data. It is an accountability and
bookkeeping machine over expert estimates, not a solver.

---

## 2. SCOREBOARD (as of 2026-11-14)
- **56 resolved: 37 HIT / 19 MISS = 66.1%, mean Brier 0.236.** Changes on 11/14: #79 MISS (US struck Qeshm 11/2), #56 HIT and #10 HIT early.
  By category: rates and inflation 9/10 (Brier 0.147), markets 12/16 (0.215), geopolitics 16/30 (0.277, worse than a coin
  flip). Nine misses logged at 70% or more carry 37% of total error.
- Before that: **53 resolved: 35 HIT / 18 MISS = 66.0%, mean Brier 0.234** (#81 FOMC hold HIT on 10/28). On 10/25 it was 52 resolved / 0.238. On 8/4 it was 0.169 on 14 resolved.
  The old number was a maturity artifact, exactly as the 8/1 note warned.
- **Projected, counting the at-risk #80, #38, #16 and #36 as failing (outcome 0): 37/60 = 61.7% / Brier 0.249.** Adding #3 (Pentagon $1.5T, at risk since the 11/17 Senate bill at $1.1T): 37/61 = 60.7% / Brier 0.250.
- **Murphy decomposition:**

  | Term | Value | Read |
  |---|---|---|
  | Reliability | 0.025 | Calibration is OK |
  | **Resolution** | **0.009** | **Low: the forecasts barely beat guessing the base rate.** This is the main disease. |

  The next gains come from *discrimination*: fewer 0.55–0.70 hedges on calls the engine can't separate.
- **The 10/25 sweep:** 35 calls were 14–79 days overdue, plus 3 resolved early: **22 HIT / 16 MISS, mean Brier
  0.264.** All 38 have lessons.
- **Both directions missed on Iran.** #59 (escalation) and #19 (de-escalation) both failed. **The boundary holds:**
  - **Strong** where the mechanism is structural and datable: July CPI nailed exactly (#71), August CPI
    re-acceleration (#32), the Fed's reaction (#67 and #62, mortgage +70bp), physical Hormuz flows (#73, #22),
    the memory-cycle peak (#33).
  - **Weak** on one decider's choices: strikes, deals, OPEC+ timing.
- **Realized P&L: +7.46%, ONE closed round-trip** (RTX). **⚠️ The MU short record (trade #2) is STALE.**
  - It was opened at 937, with a target of 800 and invalidation at 1035.
  - MU *closed* at 739 on 7/29, through the target, but the 8/4 handoff still listed it as open.
  - MU then closed above the invalidation on 9/21 (first close ≥1035).
  - The real exit is unknown. Record it with `ledger.py trade-close 2 --exit <real price> --reason ...`, and
    never at a hindsight price.
- **PORTFOLIO PROBLEM persists (11/18):** iran-war is **12 of 30 open = 40%** (was 11 of 28 = 39% on 11/14), over the ~35% cap. New iran-war calls
  need the red-team gate and a materially higher bar.

---

## 3. DOCTRINE PATCHES ON FILE
| § | Lesson |
|---|---|
| 13d.2 | Base-effect identity check MANDATORY before quoting any y/y |
| 13e / 13e.1 / 13e.2 | Event-time vs regime-time; bifurcated tape; n=1 betas get half-weight |
| 16.11 | Grievance-anchored precondition building runs backward-first |
| 16.12 | Escalation-mediation OSCILLATION: track the window, not the daily strikes |
| **16.12b (10/25)** | **Oscillation ≠ off-ramp.** A pause *without a deal* is the cheap stable state when the chokepoint is shut. Price "pause holds", "deal signed" and "strait reopens" separately. (#68) |
| 16.13 | Structural-state staleness |
| **16.13a (10/25)** | **Premise freshness AT LOGGING:** re-verify the load-bearing premise against its primary source and record it in the sensitivity tag. A premise <72h old and contested → conviction capped at 0.55. Five misses were stale on the day they were logged. (#19, #11, #24, #29, #28) |
| 16.14 | HARD CAP 0.35 on strike-planning reports for a reversal-prone decider |
| **mkt §7.1 (10/25)** | **PHYSICAL-FLOW GATE:** no oil-premium-unwind call while measured chokepoint flow is <50% of baseline and war-risk premia are >5× pre-war. Announcement flushes reverse at the next physical datapoint. (5 misses: #28, #74, #76, #23, #11) |
| **mkt §5.1 (10/25)** | **The rate-derate law failed 0-for-4 against a live AI-capex revision engine.** A semis fade needs a capex-architecture or revision catalyst, not a rate path. (#24, #69, #70, #27) |
| **jiang 16.14a (11/14)** | **Planned campaign ≠ reactive fire.** The 0.35 cap governs a decider's PLANNED strike only. A zero-event call ("no strike of any size") over N days in a live contact zone is priced from the tactical base rate 1-(1-q)^N, carries a scale threshold, and its sensitivity names the lowest-threshold breaker. (#79) |
| **formal §8.1 + item 25 (10/25)** | **FALSIFIER SYMMETRY:** falsifier = NOT(prediction). No rival-branch, escape-clause ("absent X", "with no new shock") or conjunctive falsifiers. A defective contract is scored on substance. `ledger.py add` now lints escape-clause wording. (#68, #11, #23, #14) |

---

## 4. THE IRAN WAR — STATE AT 10/25
- **War began 2/28** (Khamenei killed). **Mojtaba has been SL since 3/9**; succession is RESOLVED. He has made no
  verified public appearance, and the IRGC holds operational control.
- **Arc:**
  - 4/8 ceasefire
  - 4/13 blockade
  - **6/17 Islamabad Memorandum**, declared "over" by Trump on 7/8
  - 7/11–23: 13 nights of US strikes
  - Pauses on 7/24 and **7/30–8/29**
  - **8/16–17:** the window lapsed with **no deal**
  - 8/30: tit-for-tat resumed (9/1 wave, tanker-for-tanker strikes)
  - 9/9: IAEA referral to the UNSC
  - 9/11: the Houthis took Perim / Bab el-Mandeb
  - October: record tanker attacks, Houthi strikes on Riyadh and near Mecca
- **The 8/1 fork resolved to FROZEN OSCILLATION**, the 0.07 branch the engine under-priced. It was not a mediation
  off-ramp (0.45) and not a full round-3 war.
- **Now: the DEAL-OR-STRIKE fork.** Trump on 10/25: "no strike today… make a deal or finish them off". CENTCOM plans
  are reportedly sequenced **after the 11/3 midterms**, and Qatar is mediating.
  - Hormuz is near standstill: PortWatch counted **4 transits on 10/18, vs ~85/day pre-war**.
  - **Brent (Dec) settled 116.72 on 10/23.**
  - The Fed **hiked 9/16** to 3.75–4.00 (#26 MISS: it did not look through the oil shock).

| Branch of `iran-fork-oct`, by 11/30 | p |
|---|---|
| Post-midterm strike campaign (held at the §16.14 cap) | 0.35 |
| Deal confirmed by BOTH sides | 0.15 |
| Frozen tanker war | 0.50 |

---

## 5. LIVE STAKED CALLS
| # | Call | P | Horizon |
|---|---|---|---|
| **#81** | FOMC HOLDS 3.75–4.00 on 10/28. **✓ HIT** (10–2, Cook + Hammack for a hike; no forward guidance) | 0.82 | resolved 10/28 |
| **#79** | No US strike on Iranian LAND territory 10/26–11/3. **✗ MISS (11/14)**: US struck Qeshm radar and launchers on 11/2 after IRGC SAM fire (reactive, not the planned campaign) | 0.70 | resolved |
| **#80** | Front-month Brent settles ≥ $100 on 11/30 (physical-flow gate). **AT RISK**: Brent 95.84 on 11/13 after two weekly declines, although the strait is still shut (desk now 0.35) | 0.70 | 11/30 |
| #56 | Midterms held + ≥1 federal certification fight. **✓ HIT (11/14)**: held 11/3 (Democrats won both chambers), and DOJ's bid to pause Alaska's Senate election was rejected 11/1 | 0.55 | resolved |
| #38 | Jiang: US ground invasion of Iran by 12/31. **AT RISK**: the plans are strikes, not ground forces | 0.70 | 12/31 |
| #53 | No PLA kinetic action vs Taiwan in 2026 | 0.93 | 12/31 |
| **#82** | Hormuz STILL IMPAIRED on 3/31/2027 (PortWatch 7-day avg < 40.5, half of pre-war 81) | 0.70 | 2027-03-31 |
| **#83** | Brent front month settles ≥ $85 on 3/31/2027 (correlated with #82) | 0.70 | 2027-03-31 |
| **#84** | Fed upper bound ≥ 4.00% on 6/30/2027 (no net easing in H1) | 0.75 | 2027-06-30 |
| **#85** | No PLA blockade/quarantine/invasion of Taiwan through 6/30/2027 | 0.90 | 2027-06-30 |
| #16 | Attributed Israeli action on Iranian territory/assets by 1/8. **AT RISK**: no strike on Iran proper since 6/8 | 0.74 | 2027-01-08 |
| #36 | US ground troops OR a compensated cessation by 1/13. **AT RISK** | 0.45 | 2027-01-13 |
| #35 / #1 | Frozen conflict / no durable peace. **Tracking** (desk 0.72 / 0.80). #10 **✓ HIT early (11/14)**: 12 clean months are now impossible | 0.55 / 0.70 | 2027–28 |
| #82–#85 | Hormuz impaired 3/31 · Brent ≥85 3/31 · Fed ≥4.00% 6/30 · no PLA action to 6/30. Desk now 0.78 / 0.62 / 0.82 / 0.92 | 0.70 / 0.70 / 0.75 / 0.90 | 2027 |

**10/29 update** (`reports/20261029_scorecard-update.md`):
- Israel's 10/27 vote was gridlock (Netanyahu bloc ~53 seats), with no Israeli first strike.
- The FOMC held, but Warsh gave **no forward guidance**. The engine's expected "hawkish guidance" was wrong; `fed-dec-hike` is now 0.65.
- GOOGL fell 12% after holding capex flat with negative free cash flow: a capex *plateau*, the first AI-referee signal.
- `iran-fork-oct` is now campaign 0.35 (held at the cap) / deal 0.10 / frozen tanker war 0.55.

**11/18 update** (`reports/20261118_tape-note-gulf-oil-fed.md`, §7h):
- **New calls:** #86 Fed raises on 12/9 (upper bound ≥ 4.25%), P 0.92, rates. #87 at least one more US strike on Iranian
  territory 11/18–11/30, P 0.72, base-rate (forward test of jiang 16.14a).
- **Desk re-marks:** #84 0.82 → 0.90; #3 → 0.30 (at risk); #82 held 0.78 with a meter warning (AIS transits ~1% of normal
  vs barrels 48–82%). **#80 and #83 are legacy rows under the 11/18 ban:** carried for scoring only, not re-marked or
  published (Brent settled 93.14 on 11/17, so #80 is on course to miss).
- `iran-fork-oct` held: campaign 0.10 / deal 0.05 / frozen 0.85. `fed-dec-hike` 0.55 → 0.93. AI 2027 fork: digestion 0.42 /
  sprint 0.40 / winter 0.18 after Nvidia's beat and raised FY28 outlook.

**Next catalysts (rebuilt 11/18):** FOMC minutes 11/18 · **Xi–Trump–Putin trilateral, Shenzhen 11/19** · Anthropic IPO (ANT)
11/19 · **OPEC+ 2027 quotas 11/29** · **11/30: Iran fork, #87, legacy #80 scored** · payrolls 12/4 · **FOMC 12/9 (#86)** ·
November CPI 12/10.

**Older catalyst list (10/29):**
- **AMZN earnings 10/29 (after the close):** the second half of the AI-capex referee.
- OPEC+ 11/1 · **US midterms 11/3** (#79 horizon) · jobs 11/6 · **October CPI 11/10** (decides December) ·
  FOMC Dec 8–9.

---

## 6. THE MACHINE (rules that are ENFORCED, not remembered)
Three gates. **A cycle is not complete until all pass:**
```
python tools/web_coverage.py    # every prediction wired to the map + no dead-end catalysts
python pipeline/ledger.py sweep # nothing overdue-unscored, nothing resolved-without-lesson
python tools/debug_all.py       # full system debug (syntax/db/json/coherence/routes)
```
- **Ledger commands:** `add` (now with the §8.1 escape-clause lint), `resolve`, `lesson`, `due`, `sweep`, `report`,
  `redteam`, `trade-open`, `trade-close`, `pnl`.
- **Cross-platform:** `ingest.py` detaches the trigger worker portably (Windows `creationflags` / POSIX
  `start_new_session`). Before 10/25 it crashed on Linux.

---

## 7. THE DASHBOARD
- **Run it:** `pipeline/dashboard.py` (stdlib only), on port 8787. **5 tabs:** Monitor, **Timeline &
  Predictions**, Fusion, Ask Engine, Settings.
- **The Reports tab is gone (11/18, user request).** Its pieces moved: "Pull fresh news" and "Analyze inbox → report"
  plus the jobs list sit on Monitor above the tape panels; the focused-analysis box and the report library (search,
  manual/auto filter, reader) sit on Ask Engine under the chat. Job "open report" links jump to Ask Engine. Verified in
  a browser: 5 nav buttons, 26 reports listed, open/filter/search work, no page errors.
- **The timeline map:** a time-lane DAG with 63 nodes. Edges mean "IF x THEN y". Green = happened; resolved forks
  show the counterfactual siblings.
- **Verified 10/25:** a Playwright screenshot, 0 overlapping node pairs, all routes 200, no page errors.
- **The catalyst board (`week_ahead`)** is reset for the week of Oct 26.
- **LAN (Windows):** `tools/start_lan.ps1`. Still pending, and it needs admin once:
  `New-NetFirewallRule -DisplayName 'GT-Analyst 8787' -Direction Inbound -LocalPort 8787 -Protocol TCP -Action Allow -Profile Private`

## 7b. CEASEFIRE-TIMING ENGINE (new 10/25)
- **Files:**
  - `tools/build_ceasefire_data.py`: builds the case base from PA-X v10 (483 ceasefires) and UCDP GED 26.1 plus the
    Jan–Sep 2026 candidate release (daily fatalities). Output: **401 ceasefire cases and 1,380 war spells.**
  - `pipeline/ceasefire_engine.py`: Kaplan-Meier, a censored log-normal AFT, a kNN reference class, an ensemble,
    and a **day-by-day updating** model.
- **Walk-forward backtest, 2000–2026, no look-ahead** (`reports/backtests/20261025_ceasefire-timing-engine.md`):
  - **Return to war:** median miss 76 days vs 103 naive; C-index 0.83; 60% Brier skill on P(war within 30 days).
  - **Day-precise only for dead-on-arrival ceasefires:** 62% within ±1 day when the collapse comes within 3 days.
    Months-level error beyond that.
  - **Daily model:** AUC 0.87 for war-within-7-days (0.66 baseline), but it warns of only about 1/3 of collapses,
    with a median lead of 3 days. On the eve of collapse, the median P(tomorrow) was 4%.
  - The **war→ceasefire direction is unreliable for interstate wars**; it missed both 2026 Iran ceasefires badly.
- **Usage:** P(window) and ranking, never exact dates. Commands: `python pipeline/ceasefire_engine.py
  backtest|backtest-daily|live|predict`.
- **Next step:** add non-fatality precursors (deadlines, mediator movement, NOTAMs) from the ingest tape as daily
  covariates.

## 7c. 500-CALL STOCK BACKTEST (10/26): `reports/backtests/20261026_gt-500-stock-backtest.md`
- **Setup:** 4 weekly cohorts (9/25–10/16) × 125 stocks, scored on beating SPY over 5 sessions. The calls were
  **pre-registered** (commit `f78913d`) and the no-look-ahead check is asserted in code.
- **Doctrine version:** pre-10/25.
- **Result: 43.2% hit, Brier 0.260 (coin 0.25).** That is no better than momentum (44%).
  - The sector map alone scored 54%.
  - The §16.12 headline-oscillation fade applied to prices cost about 11 points; reversed, it would have hit 59%.
- **Confidence ranked accuracy:** P ≥ 0.60 hit 63% (n = 144); P < 0.60 hit 35% (n = 356).
- **Energy beat SPY every week (+2.3% to +7.0%).**
- **The blind spot:** the 10/9–16 AI-complex crash (−15% to −21% vs SPY) was an AI-financing event.
- **Patches:**
  - jiang §16.12c (mandatory)
  - market-transmission §4.1 (provisional)
  - market-transmission §5.2 (AI-financing feed gap; AI calls capped at 0.55)
  - contrarian Part C abstain-below-0.60
- **Forward test of the v2 candidate:** `python tools/gt_stock_backtest.py forward <date> --hormuz-impaired 1|0`.
  The 58% in-sample score counts for nothing.
- **Watchlist hygiene:** stale tickers (ABB, ERJ→EMBJ, PSTG, …) silently drop out of every tool. Fix them.

## 7d. FOLLOW-ON WORK (10/29)
- **Geopolitical report:** [The 2026 US–Iran War: A Game-Theoretic Analysis and Forecast Audit](https://claude.ai/artifact/2b2haoi6ZA6gdnoHBVBUoH).
  - The geopolitical record is **12/19 (63%), Brier 0.236, RES 0.031**.
  - Physical and structural calls went **9/9**; principal decisions **1/7**.
- **Abstention enforced:** `ledger.py add` refuses `auto` or `mechanical` calls with 0.40 < P < 0.60 and warns on
  manual ones. `report` tracks resolution before and after 10/29; the baseline is RES 0.008.
- **Dormancy alarm:** `sweep` fails after 7 days with no ledger activity. **Fixed cadence:** `tools/daily_cycle.sh`
  plus a daily scheduled cloud session (§9).
- **AI-financing stress index:** `tools/ai_stress_index.py` feeds market-transmission §5.2a.
  - It is a necessary-condition gate for any bet against the AI complex.
  - **Not yet predictive:** over 7 weeks, gate-on weeks −0.45% vs gate-off −1.07%. The 0.55 cap stays.
- **Ceasefire precursors:**
  - PA-X mediation features add a marginal gain (day-by-day AUC 0.873 → 0.877; warnings 2+ days ahead 23% → 25%).
  - Deadlines, flight bans and force posture are hand-coded for Iran 2026 (`precursors_manual.csv`) and logged
    prospectively (`tools/precursor_log.py`).
- **ETH/PRIO:** the request draft is `docs/requests/2026-10-29_ethprio-ceasefire-data-request.md`. **It needs
  sending by you;** the build tool ingests the dataset when it is saved to `data/ceasefire/raw/ethprio_cf.csv`.
- **Watchlist fixed:**
  - Renamed: ABB→ABBNY, ERJ→EMBJ, HXSCL→SKHY, SATS→ECHO, VLD→VELO, PSTG→P (Everpure), OSAT→NXPL.
  - Removed (no US listing): BITF, MIGI, GREE, IRBT, SATX, SKYT, WLAC, QRVO.
  - Audit list: `_retired` in `watchlist.json`.
- **Forward test of the stock-call candidate:**
  - The universe is frozen (`data/gt_backtest/universe.csv`), live inputs go to `data/gt_backtest/live/`, and
    registrations go to `data/gt_backtest/forward/` (never overwritten).
  - Cohorts are registered after the closes of 10/30, 11/6, 11/13 and 11/20, and scored 11/27 by scheduled sessions.
  - On a 10/23 dry run it abstained on all 125 names (2y falling → weight 0.5 → max P 0.5998). Abstaining
    weeks count as "no calls".
  - **10/30 cohort: 0 calls** (abstained on all 125; best P 0.5875, defense outperform). Hormuz flag 1. sha256
    `b0493a1c…`; see `reports/backtests/forward_v2_scorecard.md`, including how the lost push was recovered.
  - These calls never enter `ledger.db`.

---

## 7j. PRACTICE QUESTIONS ON WORLD EVENTS (11/18): `pipeline/drills.py`
User instructions, 11/18: "a daily set of practice questions that resolve within a week and are checked
automatically"; "not just for indexes but things that may happen intraday based on the news"; "this is not a stock
bot, it is a prediction bot for world events, remember that".
- **What it is:** several times a day the bot writes yes/no questions about what happens next in the news, answers
  them, and settles them from later news, with no one watching. They are practice. They never enter the ledger, the
  timeline or any report as calls.
- **A news round** (every `GT_DRILL_NEWS_EVERY_MIN` minutes, default 60, any multiple of 5 from 5 to 720, around the
  clock, only when 3 or more new reports have arrived):
  1. **settle:** a judge reads the reports published inside each due question's window and answers yes, no or
     unclear (unclear voids it). A yes must cite the report that settles it; the report is stored with the score;
  2. **write:** a writer reads the last 6 hours of reports and writes `GT_DRILL_NEWS_QUESTIONS` (default 6)
     questions: an attack, a statement or decision by a named official, a vote, a ruling, a sanction, a published
     figure. Deadlines 30 minutes to 7 days, at least half within 8 hours. Market-price questions are refused in code;
  3. **answer:** the analyst gives a probability for each, seeing only reports published before the round time,
     plus its own record: score against the base rate, calibration table, last 10 settled questions.
- **Baselines:** a coin, and the base rate (how often past questions with a deadline of hours, or of days, came
  true). The analyst only counts if it beats the base rate.
- **Weekly, Mondays:** Hormuz ship transits over the next 7 days (IMF PortWatch), settled by data.
- **Market questions are OFF** (`GT_DRILL_PRICES=1` turns them on). Replayed over 13 sessions at round lengths from
  5 to 60 minutes, every intraday index and rates question sat within 0.007 Brier of a coin, so they exercise
  calibration only. Oil, energy and defense prices are excluded either way.
- **Files:** open questions `logs/drills_open.json`; scored answers `data/drills/scored/<date>.csv` (with the
  question and the settling report); scoreboard `data/drills/report.md` and `summary.json`, rebuilt daily and
  committed. Commands: `tick`, `report`, `replay`.
- **Live test on 11/17-11/18 headlines (test copy, real Claude):** 4 rounds wrote 24 questions, for example "Will
  Iran launch a new missile or drone attack on US forces or a Gulf Arab state's territory within the next 24
  hours?" (analyst 0.60). Two reached their deadline and were settled; I checked both against the reports in their
  windows, and gave the judge a third question with a known answer:
  - Bahrain reports damage or casualties within 4 hours: NO. Correct; reports carried sirens and an alert only.
  - Trump remarks on the Qeshm strike within 4 hours: NO. Debatable; a WSJ headline said "Trump Signals Restraint
    on Iran". The judge is strict, so vague questions lean NO. The writer is now told to avoid them.
  - Known answer (Kuwait reports drone attacks within 4 hours): YES, citing the Al Jazeera report. Correct.
- **Limits:**
  - a question means "will a report saying X reach this bot's feed by the deadline". An event that happens but is
    not reported in the feed in time counts as NO;
  - the judge reads headlines and first lines, not full articles, and can be wrong;
  - on the first rounds the writer chose many long shots (analyst answers mostly 0.04 to 0.45). It is shown its
    hit rate each round and told to aim for 30% to 60%; whether that works is not yet seen;
  - nothing has been scored over more than a few hours. There is no evidence yet that the analyst beats the base rate.
- **Usage, measured:** about 6,000 input tokens and $0.12 at list price per call, on the model the CLI defaulted
  to here. A round is 2 calls plus 1 judge call when something is due:

  | Round every | Rounds a day, at most | Questions a day, at most | Calls a day, at most | List price a day, at most |
  |---|---|---|---|---|
  | 15 min | 96 | 576 | 288 | about $35 |
  | 30 min | 48 | 288 | 144 | about $17 |
  | 60 min (default) | 24 | 144 | 72 | about $9 |
  | 120 min | 12 | 72 | 36 | about $4 |

  `GT_DRILL_MODEL` picks a cheaper model. Quiet hours cost nothing: a round with fewer than 3 new reports is skipped.
- **Not live:** it starts when the server loop starts (§9), and needs the `claude` CLI there.

## 7i. THE LEARNING LOOP (11/18)
- **Diagnosis on the 56 scored calls:**
  - the stated probabilities could not tell hits from misses (AUC 0.47; misses were stated at 0.664 on average,
    hits at 0.655);
  - they scored worse (Brier 0.236) than saying the 66% base rate every time (0.224 in sample, 0.232 leave-one-out);
  - 47 of the 56 calls were logged in July and 38 were scored in one batch on 10/25, so there was almost no feedback
    while the calls were being made;
  - calls with a horizon of 14 days or less did better (13/17, Brier 0.191) than longer ones (24/39, 0.256);
  - 26 of the 56 sit in one cluster (iran-war).
- **`pipeline/learn.py`** trains a correction on the scored record: P(call comes true | call type), shrunk toward the
  base rate. It does not retrain the language model. Commands: `train`, `validate`, `shadow`, `scoreboard`, `nightly`,
  `prior`.
- **Out-of-sample result (Brier):**
  - leave-one-out: type model 0.208, stated 0.236, base rate 0.232;
  - leave-one-CLUSTER-out: type model 0.259, stated 0.236, coin 0.250. The type model loses on a topic it has not
    seen.
  - So the type lessons, including the 11/14 caps and the 11/18 ban, are lessons about this war and these topics.
    They are not proven general rules.
- **The model runs in SHADOW.** `data/learn/shadow.csv` logs its probability for every open call. The pre-registered
  rule: after 20 of those calls resolve, promote it if it beats the stated probabilities by 0.01 Brier, retire it if
  it loses by 0.01.
- **`ledger.py add` now prints the trained prior** for the call's type next to the stated probability. It never
  blocks.
- **Practice questions on world events: built 11/18, see §7j.** More and faster scored answers is the main thing the
  record lacked.
- **Stock-call forward test closed** with 0 scored calls: no evidence either way; v2 retired
  (`reports/backtests/forward_v2_scorecard.md`).

## 7g. WHERE THE FORECASTS WENT WRONG, AND THE FIX (11/14)
- **Calibration was inverted at the top.**
  - Calls stated at 70%+ came true only 59-67% of the time.
  - Calls stated at 50-70% came true 67-72%.
  - Nine misses logged at 70% or more carry 37% of total error.
- **By call type (56 resolved):**
  - state (measured flows, tolls, regime status) 7/8, Brier 0.145;
  - rates 9/10, 0.147;
  - markets 12/16, 0.215;
  - **decision** (a leader's act or non-act in a live crisis) 7/14, 0.294, no skill;
  - **war-price** (oil level, energy vs tech) 1/6, 0.385, worse than chance.
- **Fix, enforced in code (`pipeline/ledger.py`, contrarian-red-team Part C.2):**
  - Every call carries `--kind`. All 84 rows were backfilled.
  - decision and war-price calls are capped at 0.35-0.65 unless `--execution-signal` cites capital-committed
    evidence, which allows up to 0.20-0.80.
  - Zero-event decision contracts get a 16.14a lint.
  - `ledger.py report` prints calibration by type every cycle.
- **11/18 (user instruction): war-driven oil and sector price calls are BANNED, not capped.**
  - `ledger.py add` refuses kind `war-price`, and refuses any call that names an oil price, an energy or defense
    sector, or tanker rates unless `--not-war-driven` gives a reason.
  - CPI energy components stay allowed under `rates`.
  - Reports show oil and sector moves only as context, never as a call.
  - The rule is written into CLAUDE.md, the market-transmission skill banner and contrarian-red-team C.2.
  - The stock-call forward test is stopped. Its v2 rules are war-driven sector calls (defense, energy, the
    Hormuz flag), so the 11/20 cohort task is disabled. The 11/27 final-scoring task still runs and closes the
    test on the two registered cohorts (10/30 and 11/13, both 0 calls). No v2 calls are made from now on.
  - The two open Brent calls (#80, #83) stay on the book to be scored honestly. They are not withdrawn and will
    not appear as calls in future reports.
- **Grandfathered open calls outside the new band:** #16 (0.74), #38 (0.70), #80 (0.70), #83 (0.70). Read them as
  capped.
- **Operational failure:** the scheduled tasks could not push for two weeks. The cause and fix are in §9.

## 7k. THE AI-TRADE FRAMEWORK (11/18, user request: "predict everything possible about the AI trade")
- **New skill: `.claude/skills/ai-trade/SKILL.md`.** Five layers with different predictability: L1 prints (high), L2 capex
  plans, L3 financing (the first failure point), L4 constraints and policy, L5 price (no call). Master rule: never infer
  price from a print. It replaces the blanket 0.55 cap on AI calls (market-transmission §5.2b) with a rule per layer.
- **Research behind it:** six strands in `research_notes/AI trade forecasting framework/` (history and base rates, demand
  and capex, financing chain, constraints and policy, valuation and positioning, catalyst calendar). Source quality is
  mixed; laws marked [S] in the skill rest on secondary sources and get half weight until checked.
- **Thirteen calls logged (#123–#135), all wired.** They were first logged as #88–#100 and renumbered the same hour, because the server's import of 35 PC-only predictions had taken #88–#122:

  | # | Call | P | Horizon |
  |---|---|---|---|
  | 123 | Broadcom guides fiscal Q1 AI semiconductor revenue above its Q4 actual | 0.82 | 12/11 |
  | 124 | Micron fiscal Q1 revenue ≥ $61.5B | 0.86 | 12/22 |
  | 125 | Micron fiscal Q2 guide midpoint above Q1 actual | 0.72 | 12/22 |
  | 126 | TrendForce 1Q27 DRAM contract prices up q/q | 0.72 | 1/31/27 |
  | 127 | TSMC Q4 revenue ≥ $53.3B | 0.90 | 1/22/27 |
  | 128 | TSMC 2027 capex guide midpoint ≥ $68B | 0.70 | 1/22/27 |
  | 129 | Microsoft December-quarter capex > $50B | 0.87 | 2/5/27 |
  | 130 | None of the four hyperscalers guides 2027 capex below 2026 | 0.88 | 2/12/27 |
  | 131 | Alphabet 2027 capex guide midpoint ≥ $240B | 0.70 | 2/12/27 |
  | 132 | Nvidia fiscal Q4 revenue ≥ $130.0B | 0.90 | 3/10/27 |
  | 133 | CoreWeave: no missed payment, distressed exchange or bankruptcy | 0.92 | 3/31/27 |
  | 134 | Oracle not rated junk by any of the three agencies | 0.85 | 3/31/27 |
  | 135 | SMH closes below 671.83 (its 2026 high) on 6/30/27 | 0.90 | 6/30/27 |

  Report dates for #124, #127–#132 are pattern estimates: each row carries a void rule (extend the horizon, never score early).
- **Not ledgered, on the map as scenario odds:** `ai-trade-h1-2027` on the SMH close of 30 June 2027: repair (≥ 520) 0.35,
  range (400–520) 0.40, second leg (< 400) 0.25. Moved by the indicator board in the skill's §4.
- **No call, by rule:** AI price direction; the Anthropic listing (the analyst is an Anthropic model); government
  decisions on chip exports (decision kind, capped); the PJM capacity auction (2029/30 rules exclude new large loads,
  so "clears at the cap" is no longer a base rate).
- **2027 capex fork re-marked:** digestion 0.40 / sprint 0.40 / winter 0.20.
- **Correction carried into the records:** Nvidia's "$530B" is total commitments plus guarantees; guarantees alone are
  $108.5B (July 10-Q), about $118B in October per press. The 11/18 tape note said "$530bn of guarantees"; fix its doc and
  exports with the AI-trade report.
- **Portfolio after logging:** see the per-cluster count in `ledger.py report` (the PC import added 34 open rows the same day); iran-war is back under the 35% cap; ai-prints 6, ai-capex 6, ai-financing 2.
  The AI clusters share one demand bet: read them together when a miss comes from demand.
- **Forward test:** the skill's §8 sets the kill criteria per layer once 10 calls in a layer have resolved.

## 7l. CLOUD SESSION WIND-DOWN (11/18): what is unfinished and how to resume it
**CLOUD STATUS: NOT DONE YET. Data-gathering runs are still writing files. This line changes to "CLOUD SESSION DONE"
in the last commit; do not archive the cloud session before then.**

The cloud session (`session_01AwChvHXzuPFbFQLR4ELyXC`) was told to finish its step, push everything and stop. It no
longer writes `ledger/ledger.db`. Unfinished work, in the order to pick it up:

1. **AI prints backtest v2 (numeric point-and-range forecasts).** User request: "predict these numbers (in a tight
   range), not just booleans."
   - Rules and pass lines: `data/ai_prints_backtest/PREREG.md` (V1 boolean rules, then V2 numeric), committed before
     any window data was read (`99c0181`, `06329b7`). Scorers: `tools/ai_prints_numeric.py` (V2) and
     `tools/ai_prints_backtest.py` (V1). Both were self-tested on synthetic data only. **No real score has been run.**
   - Data files in `data/ai_prints_backtest/` (status is in the last commit message of this section):
     `prices.csv` (daily closes, 17 tickers), `prints_suppliers.csv` (window, 11 suppliers), `prints_buyers.csv`
     (window: AMZN, META, ORCL), `capex.csv` (window capex guide changes), `prints_history_a.csv` and
     `prints_history_b.csv` (the four reports before the window, feeds the model), `capex_history.csv` (quarterly capex
     and annual guides, 2025-2026), `consensus.csv` (sell-side consensus before each report, the benchmark).
   - To resume: when the files are present run `python3 tools/ai_prints_numeric.py --rows` and
     `python3 tools/ai_prints_backtest.py`, and report the first-run numbers against the PREREG pass lines (accuracy
     vs the naive guide and vs consensus, 80% range coverage, tightness). Check the `*_notes.md` files for rows the
     data runs could not verify before trusting a number. V1's `capex.csv` scoring needs the column `change`.
   - Then the forward numbers: `python3 tools/ai_prints_numeric.py --forward --scale <scale_for_80pct_coverage from the
     backtest>` gives a point and range for each company's next revenue print, next guide and next quarterly capex.
     Log them as range calls **from a PC session** (the cloud must not write the ledger). The 13 AI calls already
     logged (#123-#135) are yes/no thresholds, which is what the user said is not enough.
   - **Next design step, asked by the user on 11/18 ("could it not just look at all the news surrounding a company and
     use that to make a more informed prediction"): a news-informed forecast, tested blind.** The mechanical model
     only knows the company's own guide and its past beats, so it will miss the quarters that matter most: in the
     window Micron reported 41.456 against a 33.5 guide midpoint (+24%) and Dell 43.842 against 35.2 (+25%), both
     visible beforehand in DRAM contract prices and AI-server backlog news. Protocol to build:
     1. for each window report, assemble a point-in-time packet: only items published BEFORE the report date
        (`inbox/processed/` archives, the `data/ai_stress/headlines.csv` cache, TSMC monthly revenue, TrendForce
        contract prices, peers and customers that reported earlier in the same season, 8-K pre-announcements);
     2. a fresh analyst run that sees only the packet plus the company's guide and history gives a point and an 80%
        range for revenue and for the next guide, and states which items moved it off the mechanical number;
     3. score four forecasts side by side on the same rows: naive guide, mechanical, mechanical + news, consensus.
        The bar is consensus, which already contains the news; "news helps" means beating the mechanical model and
        getting within reach of consensus, most of all on the large-beat quarters.
     Leakage rule: reports published before July 2026 may be inside the model's training data, so score July-November
     separately and treat that subset as the clean one. Pre-register the packet rules before running it.
2. **The AI-trade report is not delivered.** The research synthesis is `reports/AI trade forecasting framework.md`
   if present (written by a background run from the notes in `research_notes/AI trade forecasting framework/` and the
   desk brief `desk_framework_and_calls.md`). Not built: the Claude Doc with charts, its `.docx`/`.pdf` exports and
   the markdown copy, with the backtest result folded in.
3. **Tape note correction not applied.** The 11/18 tape note
   (https://claude.ai/artifact/TtZJa6WZu9Ce2YWtd6EvXF, `reports/20261118_tape-note-gulf-oil-fed.md`, both exports)
   says Nvidia carries "about $530bn of financial guarantees". Correct figure: $108.5bn of guarantees (July 10-Q),
   about $118bn in October per press; $530bn is total commitments plus guarantees. Fix the doc, re-export, re-commit.
4. **Server and PC move.** `tools/server_loop.py` now supervises the dashboard, writes the weekly server-only archive
   and re-executes itself after a pull; the running loop needs one manual restart to pick that up.
   `tools/pc_weekly_backup.ps1` and `tools/pc_register_backup.ps1` have never been run on Windows, and the `scp` step
   has not been run against the real server.
5. **Gates at last check (11/18 ~03:00 UTC):** `web_coverage.py` failed on one dead-end catalyst from the PC line
   (`opec-ministerial-nov29`) and `ledger.py sweep` on #109 (PC import, 16 days overdue). Neither came from the cloud
   session; both were left for the PC/server side.
6. **Instruction tension to settle:** `CLAUDE.md` now says this is a prediction bot for world events, not a stock bot.
   The AI-trade framework, its 13 calls and the prints backtest are markets work the user asked for directly in the
   cloud session. Decide whether they stay.

## 7h. TAPE NOTE (11/18): Gulf fire, falling oil, a hiking Fed
- **Report:** [Tape Note: Gulf Fire, Falling Oil, a Hiking Fed](https://claude.ai/artifact/TtZJa6WZu9Ce2YWtd6EvXF) (Claude Doc, 6 charts).
  - Markdown copy with the desk-records appendix: `reports/20261118_tape-note-gulf-oil-fed.md`.
  - Exports: `reports/exports/20261118_tape-note-gulf-oil-fed.{docx,pdf}` (docx embeds all 6 charts).
- **Batch:** 2,012 items (11/15–11/18 00:40Z), moved to `inbox/processed/`. The three triggered batches of 11/15–11/17 and the
  11/18 one were covered by this note (Nvidia, AI names); no separate auto reports written.
- **The model change:** the strait STATE and the oil PRICE have decoupled. Barrels leave by pipeline, ship-to-ship and dark
  or escorted transits (IEA: Gulf exports 74% of pre-war in October; Kpler 48% through/around the strait), while AIS-visible
  traffic reads ~1%. The timeline now carries the legacy price rows on their own nodes (`brent-100-nov30`,
  `brent-85-q1`), for scoring only and with no shift edges.
- **Ban applied mid-cycle:** the 11/18 instruction (no war-driven oil or sector price calls) landed on the branch while this
  note was being written. The note, its exports, the catalyst board and #87 (sector and ticker blanked) were corrected
  before the push; oil appears as context only.
- **PENDING DOCTRINE PATCH (file when #80 resolves on 11/30):** market-transmission §7.1a — the physical-flow gate must meter
  BARRELS (Kpler/IEA mb/d, including pipeline and ship-to-ship), not AIS transits. When the two differ by more than 2x,
  barrels govern the channel analysis and any barrel-defined state call; transits govern only transit-defined state calls. #82 then carries a hit-wrong-reason risk.
- **The other stale node:** `fed-dec-hike` sat at 0.55 while futures went to ~95%. The driver moved from oil to core CPI and
  the engine was still reading the Fed through Brent. Lesson to log with #86's resolution.
- **New checkpoints on the map:** `shenzhen-trilateral` (11/19) and `opec-nov29` (11/29), both with shift edges.

## 7f. PREDICTION RANKINGS (11/14)
- **Report:** [Prediction Rankings: 14 November 2026](https://claude.ai/artifact/HaEZSeaML46AmZjCveQwSc) (Claude Doc).
  - Exports: `reports/exports/20261114_prediction-rankings.{docx,pdf}`.
  - Repo copy with the ID map: `reports/20261114_prediction-rankings.md`.
- **Content:** all 28 open calls ranked by the current desk probability (11 expected wins, 2 coin flips, 15 likely
  losses, mostly long-dated tail and Jiang calls), and all 56 resolved calls ranked by Brier.
- **The tape since 11/2:**
  - US struck Qeshm (11/2, then 11/6); Trump calls new attacks "highly unlikely" and says "no deal necessary".
  - Vance sidelined; the blockade stays; talks stalled.
  - Brent fell from 117.64 to 95.84.
  - Democrats won both chambers.
  - October CPI ran hot (core +0.3%).
  - Eisenkot is forming an Israeli government and is against a return to war.
- **Timeline re-weights:**
  - `iran-fork-oct` branches: planned campaign 0.10, deal 0.05, frozen 0.85.
  - `hormuz-impaired-q1` 0.78, `fed-h1-no-cuts` 0.82, `fed-dec-hike` 0.55, `war-economy-2027` 0.25.
  - `midterms-2026` resolved.
- **Forward test:**
  - The 11/13 cohort was recovered byte-identically: sha `5fe62aa6…`, 0 calls.
  - The 11/06 cohort is missing: the scheduled run failed on the usage limit, and it cannot be redone without
    look-ahead.

## 7e. OUTLOOK TO H1 2027 (11/02)
- **Report:** [Iran War Outlook: Q4 2026 – H1 2027](https://claude.ai/artifact/5wiVwSz9t67oCXco46iPLF) (Claude Doc,
  seven drawn charts and diagrams), with a repo copy in `reports/20261102_outlook-h1-2027.md` (desk records in its
  appendix).
- **New report style (user rule, now in CLAUDE.md):** quant-desk note, lots of visuals, no internal machinery in the
  body.
- **Every report also ships as .docx and .pdf** (user rule, now in CLAUDE.md), in `reports/exports/`. Both the
  11/02 outlook and the 10/29 war analysis are exported; the outlook's docx embeds all 7 charts.
- **New calls:** #82 to #85 (above). Each passed the red-team gate; the gates are in the report appendix.
  - Iran-war is now 13 of 31 open rows (42%), over the 35% guide. This is accepted for physical-state calls and
    flagged.
- **Re-weights on the 11/1 tape:**
  - `iran-fork-oct` branches are now campaign 0.35, deal 0.15 and frozen 0.50.
  - `fed-dec-hike` is now 0.50: the 2y fell 14bp while Brent hit $117.64, so this is no call.
  - New nodes: `hormuz-impaired-q1` 0.71, `fed-h1-no-cuts` 0.75 and `taiwan-h1-2027` 0.10.
  - The scenario tree gives P(Hormuz still impaired) of 0.71 at 3/31 and 0.61 at 6/30.
- **Data:** IMF PortWatch daily Hormuz transits can be pulled from the ArcGIS endpoint `Daily_Chokepoints_Data`
  (`where=portname='Strait of Hormuz'`, `outFields=*`; a named outFields list returns 400). The pre-war average
  (Jun 2025 to Feb 2026) is 81 a day; the last 4 weeks average 3.5.
- **Oil profiteering research (memo summarised in the report):**
  - About $2.65bn (ABC/LSEG) to $7bn (Reuters) of well-timed bearish oil futures preceded four Iran announcements,
    23 March to 21 April.
  - The White House warned staff on 3/24.
  - Bloomberg (October) reported that a CFTC referral was retracted. There are no charges and no identified traders.
  - The documented windfall goes to producers: Exxon earned $15.4bn in Q3 and Chevron $9.9bn.
- **ETH/PRIO ceasefire data from another source:** a public CC0 subset exists in the authors' ISQ 2021 replication
  archive (Harvard Dataverse doi:10.7910/DVN/YMCDBG).
  - It covers 280 ceasefires with durations in days, types and termination flags, but **no calendar dates** and
    only 13 unilateral ceasefires. So it cannot replace the full dataset for the day-level engine.
  - It is downloaded to `data/ceasefire/raw/ethprio_isq/`, which is gitignored. Its Kaplan–Meier breakdown by 90
    days is 41% overall, 49% for COH-type and 14% for definitive ceasefires.
  - The full 2,202-ceasefire file still needs the emailed request.

## 8. HARD-WON LESSONS ABOUT PROCESS
1. **Pre-register falsifiers before the move.** And now: **make them the exact negation of the call** (formal §8.1).
2. **Never claim a tool action ran without the tool result.**
3. **Check the staleness of the structural state AND of the premise at logging time** (§16.13 / §16.13a).
4. **Book exits at the pre-registered target, never the hindsight high.**
5. **Verify visually, not just in the DOM.**
6. **Never leave the ledger dormant (10/25).** 35 calls went 14–79 days unscored. The gates only work if a cycle
   actually runs.
7. **Verify re-indexed aggregator headlines (10/25).** Google News resurfaced Dawn's July–August "War returns to
   Iran" liveblog with a 10/25 timestamp. Check the underlying page date before treating it as live tape.

---

## 9. MACHINES: laptop + desktop + cloud
- **Repo:** the private git repo `https://github.com/truchard0/GT-Analyst`. The 10/25 cloud relaunch lives on the
  branch **`claude/gracious-lamport-6wef9u`**; it is **not yet merged to `main`**.
- **What travels:** code, doctrine, `data/` (including `data/ceasefire/*.csv`), `reports/` and
  **`ledger/ledger.db`**.
- **Excluded:** `.env`, `config.json`, `inbox/`, `ledger/seen.db`, `logs/`, and `data/ceasefire/raw/`
  (~55MB of downloads, rebuilt by the builder).

**⚠️ THE ONE RULE: `ledger.db` is SQLite, and git CANNOT merge it.** The cloud branch's ledger has 38 new
resolutions and 3 new calls (#79–#81).
- **Before running any cycle on a local machine:** merge or pull this branch first.
- **If a local machine logged predictions after 9/19 and never pushed them:** reconcile by hand. Re-add those rows
  on top of this ledger; do not overwrite it.

The rest of the routine is unchanged:
1. `git pull` before a session.
2. `git push` after it.
3. Never run cycles on two machines at once.

**WHERE THE BOT RUNS (changed 11/18, user instruction: "add this to the server from the printer fork, I don't want it
running here either").**
- **Claude cloud: nothing scheduled.** All GT-Analyst scheduled tasks are disabled (daily scoring gate, forward-test
  cohort and final scoring). The runner session `session_01AwChvHXzuPFbFQLR4ELyXC` is idle. Do not re-enable them
  without the user asking.
- **Server: `tools/server_loop.py`**, one supervised process (stdlib, Python 3.11+):
  - every 5 minutes, on the clock: practice questions (`pipeline/drills.py tick`, §7j), then `pipeline/ingest.py`;
  - once a day (13:17 UTC): git pull, tape data, `pipeline/learn.py nightly`, the practice scoreboard, due calls,
    scoring, the three gates, then commit and push;
  - scoring runs only when calls are due AND the `claude` CLI is installed on the server (one headless run, capped at
    45 minutes). Without it, due calls are listed as `needs_scoring` in the status file and the sweep gate fails;
  - status and heartbeat: `logs/server_status.json` (or `GT_HEARTBEAT`), rewritten before every step, with `push_ok`,
    `unpushed`, `needs_scoring`, gate results and the last error. A refused push is retried every tick;
  - watchlist triggers stay dry-run unless a `config.json` on that machine turns them on.
- **The server also serves the dashboard (11/18, user instruction: "none of it on this PC, all on the server, with a
  once-a-week download to ensure it's backed up").** `server_loop.py` keeps `pipeline/dashboard.py` running on port 8787,
  restarts it if it dies and after a pull changes its code. It binds to loopback only; open it from the PC through an
  SSH tunnel (`ssh -L 8787:127.0.0.1:8787 <user>@<server>`, then http://localhost:8787). `GT_LAN=1` binds all
  interfaces instead: the dashboard has no login and its buttons spend Claude usage, so only on a private network.
  `GT_DASHBOARD=0` turns it off. The loop also re-executes itself when a pull changes `server_loop.py`.
- **Weekly backup.** On Sundays the loop writes `backups/gt_server_only_<date>.tar.gz` (git-ignored, mode 600):
  `.env`, `config.json`, `ledger/seen.db` and the loop's state. The PC runs nothing except a weekly scheduled download,
  `tools/pc_weekly_backup.ps1`: a full git mirror from GitHub, a dated zip of the branch (8 kept), and with `-Server`
  the server-only archive by scp. One-time PC setup: `tools/pc_register_backup.ps1` (removes the old ingest task, stops
  local processes, registers the Sunday 10:00 task, runs and verifies the first backup). It does not delete the PC
  checkout; the owner does that after "Backup verified".
- **Tested 11/18 in the cloud container:** dashboard start, restart after death, restart after a code change, a port
  clash reported as an error, clean stop; the archive; the self-restart; the mirror, verify and zip steps of the backup
  with git on Linux. **Not tested: the two PowerShell scripts on Windows, and scp against the real server.**
- **To go live the server needs one manual restart of the loop** (the running copy predates the self-update code).
- **Supervisor: the Printer fork's watchdog** (`Sampatel00/Printer`, commit `d81b674`, merged into the fork's `main`
  on 11/18 by fast-forward). Runner `gtanalyst` = `tradingview/gt_analyst_runner.py`, non-critical (`storm=False`),
  heartbeat `_gt_analyst_alive.json`. With no GT-Analyst checkout on the machine it idles; it never crash-loops.
- **NOT LIVE YET. The owner still has to, on the server:**
  1. `git pull` the fork's `main` (the merge is done);
  2. clone `truchard0/GT-Analyst` next to the Printer checkout (or set `GT_ANALYST_HOME`), on branch
     `claude/gracious-lamport-6wef9u`, with git credentials that can push;
  3. install and log in the `claude` CLI there, if due calls are to be scored and practice questions answered
     automatically (without it the baselines still run);
  4. restart the watchdog, then check `python3 tools/server_loop.py --status` for `push_ok: true`.
- **Until then nothing scores predictions.** The next call due is #80 (Brent, 11/30). An interactive session can score
  it by hand.
- **Tested 11/18 in an isolated copy** (local push target, stand-in Claude):
  - a full cycle scored a due call and pushed;
  - with no Claude, the due call was flagged and the run exited 1;
  - the loop stops within 2 s of SIGTERM;
  - the fork's watchdog matches the process.
  It has not run on the real server.

**History of the cloud runs (10/29 to 11/18).** The 10/29 tasks started fresh sessions with no repository attached, so
every push got 403 until 11/14. Lost and recovered: the 10/30 and 11/13 cohorts, and the 11/14 scoring of #79. The
11/06 cohort run failed on the usage limit. From 11/14 to 11/17 the tasks fired into the runner session and pushed
daily. On 11/18 the user moved everything off Claude cloud.

**Running a cycle anywhere else while the server loop is live risks a `ledger.db` conflict.** Pull first and push
straight after. On a conflict the server loop aborts the merge, reports it and retries an hour later; it never picks
a side.

**Cloud specifics:**
- The Windows Task Scheduler cadence does not exist here. Each cloud session runs ingest manually
  (`python pipeline/ingest.py`).
- A recurring cloud schedule is possible, at most hourly.
- The container is ephemeral: anything worth keeping must be committed and pushed.
