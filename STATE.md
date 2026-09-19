# GT-Analyst — LIVE STATE (handoff doc)
**Last updated: 2026-08-01.** Read this first after any context reset. It records what
the engine IS, what it has LEARNED, and what is currently STAKED. Everything here is
reconstructible from `ledger/ledger.db` + `data/timelines.json`, but this is the summary.

---

## 1. WHAT THE ENGINE IS
A game-theory news-analysis prediction machine. Ingests ~38 RSS feeds + 5 JSON APIs every
5 min (Windows Task Scheduler → `pipeline/ingest.py`), matches a watchlist, optionally
auto-fires headless analysis, and maintains a **Brier-scored prediction ledger** plus a
**time-lane timeline map**. Reasoning layer = four skills in `.claude/skills/`:
`jiang-doctrine`, `formal-game-theory`, `market-transmission`, `contrarian-red-team`.

**Key distinction to keep honest:** the engine *computes* coherence, parlays, shift
propagation and Brier scores. The *probabilities themselves are analyst judgment* stored
as data. It is an accountability + bookkeeping machine over expert estimates, not a solver.

---

## 2. SCOREBOARD (as of 2026-08-04)
- **Predictions: 78 logged · 14 resolved · 12 HIT / 2 MISS · mean Brier 0.169 · 85.7% hit-rate**
- The projected 80% / 0.192 written on 8/1 was **right**: #72 and #63 both resolved MISS on
  schedule (Brier 0.30 and 0.56). The 12/12 was a maturity artifact, exactly as flagged.
- **#59 (ceasefire fails, 0.72) is the third one and is now LIKELY MISS** — resolves 8/15.
- ⚠️ **#66 (war caps the melt-up) is AT RISK**, downgraded from "tracking HIT" on 8/4. S&P set a
  record 7,736.52; SPY 771.28 is +1.54% over the prior 2026 high close (759.57, 6/2) and the
  2%-above threshold that kills #66 is **SPY 774.80** — 0.45% away, 13 sessions left.
- **Realized P&L: +7.46%, ONE closed round-trip** (RTX 195.42 → 210.00, booked at the
  pre-registered target). MU short OPEN at entry 937 (MU 892.15 on 8/4 = **+4.78% unrealized**,
  gave back most of its gain on a +7.55% day) → unrealized, excluded. NVDA HOLD = no trade.
- **Forecast accuracy (Brier) ≠ trading P&L.**
- **PORTFOLIO PROBLEM:** iran-war = **31 of 55 open (56%)** — one correlated bet dressed as 31.
  Cap is now ~35% per cluster; read calibration per-cluster.
- **THE BOUNDARY THE BACKTEST FOUND:** the engine is strong where the mechanism is *structural
  and datable* (Fed reaction functions, capex cycles, positioning unwinds, calendar arithmetic)
  and weak where the outcome is **one person's discretionary choice** (Trump strike decisions).
  Spend conviction accordingly.


### The flagship win
**FOMC 7/29:** engine faded the market — HOLD at 0.75 vs the market's ~0.65 (CME had ~35%
hike). Fed **held**; three dissents for a hike (most since 2016) but the majority sided with
Warsh to wait for the July/Aug CPI in September — *exactly* the no-SEP + data-lag + §11
supply-shock-look-through mechanism the engine used. #67 Brier 0.06.

### The systematic failure (owned)
**Escalation over-prediction.** #63 (US strikes Yemen by 8/4) and #59 (ceasefire fails) both
weighted continued escalation and ignored that Iran *requested* the pause, Oman was mediating,
and the signed 60-day window was live. Two of the same miss-shape → doctrine patch §16.12.

---

## 3. DOCTRINE PATCHES WRITTEN THIS CYCLE (all live in the skills)
| § | Lesson |
|---|---|
| **13d.2** | Base-effect identity check MANDATORY before quoting any y/y (twice-repeated miss) |
| **13e** | Event-time vs regime-time: inside 48h of a catalyst, the catalyst governs, not the regime |
| **13e.1** | Bifurcated tape: physical markets trade flows, equities trade narrative — both tails can fire at once |
| **13e.2** | Single-confirmation beta discipline: n=1 betas get half-weight |
| **16.11** | Grievance-anchored precondition building runs BACKWARD-first (2020 relitigation, not forward threat) |
| **16.12** | **Escalation-mediation OSCILLATION**: with exhausted belligerents + live mediators + a signed deadline, war cycles — it does not climb a ladder. Track the WINDOW, not the daily strikes |
| **16.14** | **HARD CAP 0.35 on strike-planning reports** for a reversal-prone decider — a leaked plan is a negotiating instrument, not a forecast. Escalate only on execution signals (aircraft launched, NOTAMs). Stand-down ≠ deal |
| **16.13** | Structural-state staleness: verify a state hasn't already RESOLVED (carried "succession" live for months after Mojtaba took over 3/9) |

---

## 4. THE IRAN WAR — CORRECTED MODEL (the big rebuild)
War began **2/28/2026** (US Epic Fury + Israel Roaring Lion; **Khamenei killed**).
**Mojtaba Khamenei = Supreme Leader since 3/9 — succession RESOLVED.**
Arc: Apr 8 ceasefire → Apr 22 blockade → **Jun 17 Islamabad Memorandum signed (14-point,
60-day window expiring ~Aug 16)** → ~Jul 9 crumbles → Jul 11–24 round 2 (13 strike nights,
Brent >$100, oil $132, Houthi Red Sea blockade on Saudi) → ~Jul 25+ **US pauses at Iran's
request**, Oman mediating.

**The master clock is the Aug-16 window expiry** — everything else is oscillation inside it.
Branches (sum 1.00): **mediation off-ramp 0.35** (was under-priced at 0.10) · window collapse
→ round-3 0.45 · frozen oscillation 0.07 · succession residual 0.08 · capitulation 0.05.
Market read: **the war premium is CYCLICAL, not permanent** — trade convexity into the window.

---

## 5. LIVE STAKED CALLS (the ones that matter)
| # | Call | P | Horizon |
|---|---|---|---|
| **#68** | Iran mediation off-ramp by the 8/16 window (the bias correction) | 0.55 | 8/16 |
| **#69** | Range: SPY 705-775 / QQQ 640-720 / SMH 480-605 | 0.60 | 9/30 |
| **#70** | SMH underperforms SPY | 0.58 | 9/30 |
| **#62** | 30y mortgage +25bp by 10/1 | 0.62 | 10/1 |
| **#49** | Concrete federal election instrument by 8/16 | 0.55 | 8/16 |
| **#59** | Ceasefire fails — **LIKELY MISS** (pause held; Hormuz talks live) | 0.72 | 8/15 |
| **#65 / #66** | No crash tracking HIT · **war-caps-melt-up AT RISK** (SPY 774.80 line) | 0.80 / 0.60 | 8/21 |
| **#73** | Hormuz NOT normalized commercial transit by Fri 8/7 (physics, not politics) | 0.85 | 8/7 |
| **#77** | SMH stays below 605 this week (+14.1% in 4 sessions already) | 0.78 | 8/7 |
| **#74** | XLE outperforms USO over 5 sessions (war-premium unwind ≠ demand event) | 0.75 | 8/11 |
| **#78** | SPY not >774.80 on all of Wed/Thu/Fri | 0.70 | 8/7 |
| **#76** | Pump avg <$4.00 by 8/25 — **self-downgrade** of the Aug-CPI-is-hot thesis | 0.68 | 8/25 |
| **#75** | Payrolls conditional: ≥110k→SPY red, ≤70k→SPY green, VOID in between | 0.62 | 8/7 |

⚠️ **MIRROR RISK:** four of the six new calls are fade-the-move. After three wrong escalation
calls the engine must not over-correct into assuming relief cannot compound. The single scenario
that breaks #66/#77/#78 together: a signed Hormuz deal + a soft payroll in the same week.

**Next catalysts:** Aug 12 CPI (THE referee — carries the Brent>100 pass-through) · Aug 13
PPI · **Aug 16 Islamabad window** · late-Aug NVDA · Sept FOMC (the deferred hike).
**Levels:** SMH 605 = correction over; SMH 480 = deeper de-rate; SPY 775 / 705 = the breakers.

---

## 6. THE MACHINE (rules that are ENFORCED, not remembered)
Three gates. **A cycle is not complete until all pass:**
```
python tools/web_coverage.py   # every open prediction wired to the map + no dead-end catalysts
python pipeline/ledger.py sweep # nothing overdue-unscored, nothing resolved-without-lesson
python tools/debug_all.py       # 8-section full system debug (syntax/db/json/coherence/routes)
```
**Standing rules in CLAUDE.md:** timeline-web sync · the learning loop (TRACK→SCORE→DIAGNOSE→PATCH;
a repeated miss-shape is systematic, never variance) · time-lane fields on every node
(lane/date/checkpoint/shifts) · no dead-end catalysts.

**Ledger commands:** `add`, `resolve`, `lesson`, `due`, `sweep`, `report`, `redteam`,
`trade-open`, `trade-close`, `pnl`.

---

## 7. THE DASHBOARD
`pipeline/dashboard.py` (stdlib only). **6 tabs:** Monitor (overview + P&L + watchlist
manager + triggers + tape) · Reports · **Timeline & Predictions** · Fusion · Ask Engine · Settings.

- **Theme:** monotone dark — one neutral ramp (`#0b0b0c`→`#f4f4f6`), 3px radii, no glows.
  Colour ONLY for state (sage=HIT, clay=MISS, amber=due).
- **Timeline map:** time-lane DAG. X = real time (near-term gets the space: July 2026 ≈ 870px),
  6 lanes, 48 nodes. **Edges = temporal implication "IF x THEN y"** with arrowheads, all
  forward in time; green = happened, gold = favoured, grey = alternative, dark-dashed = ruled
  out, amber-dashed = shift edges. Green dotted spine = actual history in occurrence order.
  Drag to pan, ctrl+scroll/±  to zoom, PIN a node for what-if propagation.
- **Long lists are scroll-capped** (Monitor went 47,775px → 5,397px).
- **Ask Engine:** needs an Anthropic API key in Settings; queries with doctrine + live state
  as context. Custom question-maps save to `data/custom_maps/`.
- **LAN:** `powershell -File tools\start_lan.ps1` → serves on `0.0.0.0:8787`, reachable at
  **http://192.168.4.53:8787**. Loopback-only is the default (opt in via `GT_LAN=1`).
  ⚠️ **PENDING (needs admin, once):**
  `New-NetFirewallRule -DisplayName 'GT-Analyst 8787' -Direction Inbound -LocalPort 8787 -Protocol TCP -Action Allow -Profile Private`

---

## 8. HARD-WON LESSONS ABOUT PROCESS
1. **Pre-register falsifiers before the move.** #61 looked WRONG mid-week (SMH ran to 591),
   was flagged as at-risk *in real time* rather than rationalized, then resolved HIT.
2. **Never claim a tool action ran without the tool result** (a phantom "logged #45" once
   corrupted downstream state).
3. **Check staleness of the structural state, not just headline dates.**
4. **Book exits at the pre-registered target, never the hindsight high.**
5. **Verify visually, not just in the DOM** — the map "rendered fine" while being an
   illegible overlapping pile (47 overlapping node pairs).

---

## 9. TWO-MACHINE SETUP (laptop + desktop, since 2026-09-19)
The project is a **private git repo**. Code, doctrine, `data/timelines.json`, `reports/` and
**`ledger/ledger.db`** all travel. Excluded: `.env`, `config.json` (API key), `inbox/`
(~29MB feed dump), `ledger/seen.db` (~6MB dedup cache, rebuilds itself), `logs/`.

**⚠️ THE ONE RULE: `ledger.db` is SQLite — git CANNOT merge it.**
If both machines commit a change to the ledger, you get a binary conflict resolvable only by
picking one file and *losing the other machine's predictions*. So:
1. `git pull` **before** you start a session.
2. `git push` **when you finish** one.
3. Never run a logging/resolving cycle on both machines at once.

**Per-machine setup after cloning:**
- `cp .env.example .env` and fill in keys (RSS-only ingestion works with none).
- Re-enter the Anthropic API key in the dashboard Settings tab — `config.json` is gitignored
  and does NOT travel, by design.
- `seen.db` regenerates on the first ingest run; expect one noisy cycle as it re-learns what
  it has already seen.
- The **Task Scheduler ingest job is machine-local** (`tools/register_task.ps1`). Run it on
  ONE machine only, or both will write to their own diverging `seen.db`.
