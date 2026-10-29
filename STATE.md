# GT-Analyst — LIVE STATE (handoff doc)
**Last updated: 2026-10-29 (scorecard update; cloud relaunch 10/25).** Read this first after any context reset. It records what
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

## 2. SCOREBOARD (as of 2026-10-25)
- **53 resolved: 35 HIT / 18 MISS = 66.0%, mean Brier 0.234** (#81 FOMC hold HIT on 10/28). On 10/25 it was 52 resolved / 0.238. On 8/4 it was 0.169 on 14 resolved.
  The old number was a maturity artifact, exactly as the 8/1 note warned.
- **Projected, counting the at-risk #38, #16 and #36 as misses: 61.8% / Brier 0.248.**
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
- **PORTFOLIO PROBLEM persists:** iran-war is **11 of 28 open = 39%**, over the ~35% cap. New iran-war calls
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
| **#79** | No US strike on Iranian LAND territory 10/26–11/3 (pre-midterm). **Tracking HIT**: none through 10/29; WSJ says the US warned Gulf states to prepare for strikes *after* the midterms | 0.70 | 11/3 |
| **#80** | Front-month Brent settles ≥ $100 on 11/30 (physical-flow gate). **Tracking HIT**: front month 110–116 through 10/29 | 0.70 | 11/30 |
| #56 | Midterms held + ≥1 federal certification fight. DOJ v. Alaska (10/22) is already filed. **Tracking HIT** | 0.55 | 11/30 |
| #38 | Jiang: US ground invasion of Iran by 12/31. **AT RISK**: the plans are strikes, not ground forces | 0.70 | 12/31 |
| #53 | No PLA kinetic action vs Taiwan in 2026 | 0.93 | 12/31 |
| #16 | Attributed Israeli action on Iranian territory/assets by 1/8. **AT RISK**: no strike on Iran proper since 6/8 | 0.74 | 2027-01-08 |
| #36 | US ground troops OR a compensated cessation by 1/13. **AT RISK** | 0.45 | 2027-01-13 |
| #35 / #10 / #1 | Frozen conflict / no durable peace. **Tracking** | 0.55 / 0.70 / 0.70 | 2027–28 |

**10/29 update** (`reports/20261029_scorecard-update.md`):
- Israel's 10/27 vote was gridlock (Netanyahu bloc ~53 seats), with no Israeli first strike.
- The FOMC held, but Warsh gave **no forward guidance**. The engine's expected "hawkish guidance" was wrong; `fed-dec-hike` is now 0.65.
- GOOGL fell 12% after holding capex flat with negative free cash flow: a capex *plateau*, the first AI-referee signal.
- `iran-fork-oct` is now campaign 0.35 (held at the cap) / deal 0.10 / frozen tanker war 0.55.

**Next catalysts:**
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
- **Run it:** `pipeline/dashboard.py` (stdlib only), on port 8787. **6 tabs:** Monitor, Reports, **Timeline &
  Predictions**, Fusion, Ask Engine, Settings.
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
  - These calls never enter `ledger.db`.

---

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

**Scheduled cloud sessions (created 10/29; each starts a fresh session, clones this branch, pushes back):**

| Task | When (UTC) | Does |
|---|---|---|
| GT-Analyst daily scoring gate | daily 13:17 | `tools/daily_cycle.sh`; researches and resolves due calls with lessons; updates the timeline and STATE; gates; push |
| Forward test: register cohort | 10/30 21:13 · 11/6, 11/13, 11/20 22:13 | Refresh live data; set the Hormuz flag from flow counts; register the v2 cohort; score earlier ones |
| Forward test: final scoring | 11/27 20:13 | Final verdict in `reports/backtests/forward_v2_scorecard.md` + STATE §7d |

None of these sessions holds MCP connectors (git, web search and price feeds need none).
**Running a cycle locally while one is scheduled risks a `ledger.db` conflict.** Pull first. The daily session
is told to stop rather than pick a side on a ledger conflict.

**Cloud specifics:**
- The Windows Task Scheduler cadence does not exist here. Each cloud session runs ingest manually
  (`python pipeline/ingest.py`).
- A recurring cloud schedule is possible, at most hourly.
- The container is ephemeral: anything worth keeping must be committed and pushed.
