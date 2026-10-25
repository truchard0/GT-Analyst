# GT-Analyst — LIVE STATE (handoff doc)
**Last updated: 2026-10-25 (cloud relaunch).** Read this first after any context reset. It records what
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
- **52 resolved: 34 HIT / 18 MISS = 65.4%, mean Brier 0.238.** On 8/4 it was 0.169 on 14 resolved.
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
| **#81** | FOMC HOLDS 3.75–4.00 on 10/28 | 0.82 | 10/28 |
| **#79** | No US strike on Iranian LAND territory 10/26–11/3 (pre-midterm) | 0.70 | 11/3 |
| **#80** | Front-month Brent settles ≥ $100 on 11/30 (physical-flow gate) | 0.70 | 11/30 |
| #56 | Midterms held + ≥1 federal certification fight. DOJ v. Alaska (10/22) is already filed. **Tracking HIT** | 0.55 | 11/30 |
| #38 | Jiang: US ground invasion of Iran by 12/31. **AT RISK**: the plans are strikes, not ground forces | 0.70 | 12/31 |
| #53 | No PLA kinetic action vs Taiwan in 2026 | 0.93 | 12/31 |
| #16 | Attributed Israeli action on Iranian territory/assets by 1/8. **AT RISK**: no strike on Iran proper since 6/8 | 0.74 | 2027-01-08 |
| #36 | US ground troops OR a compensated cessation by 1/13. **AT RISK** | 0.45 | 2027-01-13 |
| #35 / #10 / #1 | Frozen conflict / no durable peace. **Tracking** | 0.55 / 0.70 / 0.70 | 2027–28 |

**Next catalysts:**
- Israel election 10/27
- **FOMC + MSFT/GOOGL capex 10/28.** This is the AI-architecture referee after Meta's operating income fell 37%,
  neocloud credit stress, and SMH dropping −16.6% from its 10/6 high.
- AMZN 10/29 · OPEC+ 11/1 · **US midterms 11/3** · jobs 11/6 · October CPI 11/10 · FOMC Dec 8–9.

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

**Cloud specifics:**
- The Windows Task Scheduler cadence does not exist here. Each cloud session runs ingest manually
  (`python pipeline/ingest.py`).
- A recurring cloud schedule is possible, at most hourly.
- The container is ephemeral: anything worth keeping must be committed and pushed.
