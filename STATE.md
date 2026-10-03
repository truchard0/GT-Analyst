# GT-Analyst — LIVE STATE (handoff doc)
**Last updated: 2026-09-21** (rules v3 + tree buildout — see `reports/20260921_rules-v3-and-tree-buildout.md`). *Previous: 2026-09-20* (open-book test — see `reports/20260920_open-book-test.md`; full scoring cycle 9/19 — `reports/20260919_scoring-cycle-reality-check.md`). Read this first after any context reset. It records what
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

## 2. SCOREBOARD (as of 2026-10-02)
- **10/02 SCORING CYCLE: 50 resolved · 36 HIT / 14 MISS · 72% · Brier 0.2254 · 27 open.** Three rows
  matured and were scored against primary series (yfinance adjusted closes; FRED MORTGAGE30US):
  **#70 MISS** (SMH +12.67% vs SPY +2.34% — outperformed by 10.3pp, Brier 0.2831) · **#27 MISS**
  (SMH +9.41% vs XLE −3.27% from the 8/31 trigger, 12.7pp the wrong way, Brier 0.4709 — and robust
  to the #59-style scope ambiguity: the alternative 9/9 trigger reading gives 12.8pp the same way) ·
  **#62 HIT-CLEAN** (7/23 anchor 6.58 → 10/1 print **7.28** = +70bp; weekly minimum 6.65 never near
  the 6.43 floor; Brier 0.1273).
- **THE OPEN PUZZLE IS CLOSED, and it is a finding, not a puzzle.** STATE.md has carried since 9/20:
  "the hike moved rates but NOT the equity derate leg — mechanism fired, asset map did not." Both
  tests have now failed by >10pp **while the mechanism was confirmed HIT by #62 in the same window**.
  The engine priced the rate path correctly and the equity consequence of that path incorrectly, in
  the same two months. **New boundary: the book may forecast the macro variable; it may NOT forecast
  which asset expresses it.** The 'hike → semis derate' channel is 0-for-2 by double digits — 11a's
  0.55 cap is too generous and those rows should be refused until the AI-capex bid visibly weakens.
- **REVISE EARLY OR DON'T BOTHER (the cycle's second lesson).** Scoring is TIME-WEIGHTED. #70 was
  revised 0.58 → 0.15 → 0.10 and still scored **0.2831**, because it sat at 0.58 for ~51 of its 61
  open days. The revision was right in direction and recovered only **0.053** of Brier. #27 the same.
  Only #62's revision paid, because it came when the remaining window was short and the arithmetic
  was already decided. Being right late is worth almost nothing.
- **THE EDGE TABLE IS CONTAMINATED — do not quote it.** It populated for the first time (n=3, mean
  edge −0.2999, CI −0.4559..−0.1219) and the number is **uninterpretable**: all three references were
  backfilled on 9/22, **53–75 days after** their rows were logged, by someone who could already see
  the tape (#70's comparison class literally cites the 9/18 gap). A late reference beating an early
  forecast is near-tautological. `ledger.py report` now prints `timely reference only: n=0 -> THERE
  IS NO EDGE MEASUREMENT YET` instead of letting the headline stand alone. R25 means the base rate is
  decided BEFORE the probability; only rows logged that way can ever score an edge.

- **10/02 MARKET-DATA BRIDGE (`pipeline/marketdata.py`) — the repo finally has a price feed.**
  READ-ONLY tap on the Trading Bot tree's WSL venv (the only interpreter here with yfinance). It
  writes NOTHING into that tree, imports none of its code, touches no account: a data tap, not an
  integration. `spot` returns realised vol **already in range_odds' unit (percent/day)** because the
  wrong unit is the one documented cause of a wrong correction here; `odds --spot-from TICKER` pulls
  spot and vol from the tape and runs range_odds, so **a level row can no longer be fed an assumed
  vol**; `bars` writes the CSV `ledger.py trade-check --bars` needs. On failure it raises loudly —
  a silent empty series is how a gate turns into decoration.
- **10/02 T14 FIRED ON THE CLEAN TRADE — and the date is now FIXED (10/03).**
  With real bars, trade #1 (RTX long, exit 210.00 recorded 2026-07-27) was refused: RTX traded
  **213.80–220.39 raw** that session, so a 210.00 fill never existed there. The pre-registered 210
  target was **first touched 2026-07-23** (raw 202.51–213.49). Checked under BOTH adjusted and raw
  prices so it is not a feed artifact. **Corrected 2026-10-03: exit_ts 2026-07-27 -> 2026-07-23**,
  reasoning appended to the trade note; exit PRICE stays 210.00 (booked at the target, lesson 4), so
  **realized pct is unchanged at +7.46% and book P&L is unchanged at +22.08%, 2/2**. Holding period
  drops from 13 days to 9. T14 now passes on #1; the only remaining refusal is the known MU T04
  fixture (R:R 1.40 < 1.50).
  **Precision on the earlier claim:** trade #2 (MU) was NOT date-corrected — 2026-07-28 IS its true
  first touch (low 789.09), and its lateness was the seven-week WALL-CLOCK booking its note already
  records. So one record carried a wrong date (RTX, by two sessions); both trades were booked late
  operationally. That is still the case for T08, stated accurately rather than as "2 of 2 bad dates".

*(9/22 entries follow for the record.)*
### 2b. SCOREBOARD (as of 2026-09-22)
- **9/22 MEASUREMENT PASS - the book can now be measured at all.** References backfilled onto **30/30
  open rows** (was 0/28): every row carries a base rate with a NAMED comparison class, and no citation
  is invented - each class is either the engine own recorded tape, a structural count, or a stated
  institutional record. Full update pass: **8 revised, 20 confirmed, stale 9 -> 0**, cadence 0.2 -> 0.6
  updates/row (GJ superforecasters ~8). The edge-over-reference table is STILL empty because no
  *resolved* row carries a reference - that only fixes itself as v3 rows mature.
- **9/22 biggest repricings, all outside-view corrections not tape reactions:** #2 draft 0.35 -> **0.08**
  (0 drafts in 46 years of continuous registration) - #3 Pentagon 1.5T 0.30 -> **0.12** (CR to 12/11,
  nothing enacted) - #5 Russian Cuba chokepoint attrition 0.35 -> **0.10** (untouched since 4/21, 0
  instances since 1962) - #4 0.40 -> **0.28** - #16 Israel strikes Iran 0.60 -> **0.45** (0 of 4 rounds
  pulled Israel in) - #41 SCOTUS 4th 0.55 -> **0.42** (71 days of window consumed, no vacancy).
- **9/22 #12 DELIBERATELY NOT MOVED and it is the book biggest single exposure.** A Hormuz reopening
  report printed 9/22 (crude below 90, LMT/RTX -3pct). #12 says no enforced Hormuz toll, P=0.62 - but an
  escort/toll regime is the ONE structure that has ever made a chokepoint reopening durable, so a
  *successful* deal resolves #12 MISS. Held anyway: 1 day of tape on a signal that is **0-for-4 in this
  war** (6/18, 7/13, 8/3, 8/4), and R31 refuses a reversal inside one lag length. Watch weekly TRANSIT
  COUNTS, not headlines.
- **9/22 two new rows logged: #79** Hormuz transits stay <50pct of pre-war through 10/15 (P=0.80,
  cluster hormuz-flows) and **#80** no NPT withdrawal takes legal effect before 1/1/27 (P=0.90, treaty
  arithmetic: Article X needs 3 months notice, and a bill TABLED is not a notice FILED). Both clustered
  OUTSIDE iran-war with an explicit independence argument - neither co-moves with the direction rows.
- **9/22 T01-T14 are now ENFORCED, not just written.** `ledger.py trade-open` requires `--target` and
  `--invalidation` and refuses any trade the rules refuse (verified: T01/T03/T04/T06 all block, nothing
  written); `trade-close` uses the closed exit vocabulary and re-derives pct; new **`ledger.py
  trade-check`** runs T01-T14 over the whole book. It currently exits 1 on the known MU T04 contradiction
  (R:R 1.40 < 1.50) - that is why it is NOT wired into `sweep`: a permanently-red cycle gate is worse
  than no gate. **T08/T13 print NOT CHECKED without `--bars`** rather than silently passing.
- **9/22 `tests/test_ledger.py` un-redded** - 5 errors were Windows PermissionError on temp-dir teardown
  (ledger.py 15 db() sites never close their connection), never assertion failures. All 5 suites now OK.

- **9/21 RULES v3 + BUILDOUT (`reports/20260921_rules-v3-and-tree-buildout.md`).** Read across all twelve
  misses at once and they are ONE error in four costumes: pricing a **choice**, a **conjunction**, a **stale
  state** or a **levered proxy** as if it were a mechanism. The book is a good physicist and a bad
  psychologist — invariants 8-for-8 at Brier 0.10, and every miss that turned on a named human deciding.
  Built from that: **nine new rules R28-R36**, each bought with a named loss — R28 self-contradiction
  (#26 vs #32, lesson 7 finally enforced) · R29 RV-is-levered-direction (#74) · R30 resolution source
  (#59, #30) · R31 no self-downgrade inside one lag length (#76) · R32 a plan is not an action (#72) ·
  R33 base-rate-adjacent rows carry no information (warning) · R34 one bet logged twice (#70/#27) ·
  R35 one meeting is a subset of its window (#26) · R36 a conjunction cannot beat its weakest leg (#63).
  **Schema is now v3; every row carries a `resolution_source`.** 46 tests, mutation-checked.
  R36 closes a dodge open since R09: banning the WORDING "A AND B" never made anyone fix the PRICE.
  #63 would now be refused at 0.75 against legs of 0.55/0.40 — logged at <=0.40 its Brier goes 0.56 -> ~0.16.
- **9/21 TRADING RULESET (`pipeline/trade_rules.py`, T01-T14, 64 tests).** There were ZERO enforced trading
  rules. **T08** fails the check on an open trade whose tape touched its target (trade #2 MU, seven weeks);
  **T13** does the same on the invalidation side (MU printed 1042.40 through its own 1035 stop while the
  trade read "open"); **T09/T14** make the 737.88 hindsight booking unwritable. NOT yet wired into
  `ledger.py trade-open`. **Known contradiction: MU 937->800 has R:R 1.40, below T04's 1.5 floor** — logged
  as an explicit test, not fitted away.
- **9/21 TREE 66 -> 266 nodes / 19 lanes** (`tools/buildout_2026_09_21.py`, reproducible + self-policing).
  Mix is the argument: **61% invariant-or-scheduled, 7% direction (all capped 0.55), 10 rows <=0.45 and 50
  >=0.88** — the direct answer to resolution ~0.00, which you fix by being willing to say *probably not*.
  Only 2 new iran-energy nodes, both durations (cluster is over the 35pct cap). 13 new lanes fill real holes
  (healthcare ~18pct of GDP had zero nodes; Europe zero; mining zero). **No dated news fact is invented** —
  6 nodes carry structural evidence, the rest state a prior and say so. The script refused its own author
  32 times on the first run; all 32 fixed by moving the NUMBER, never the rule.
- **9/21 `ecb` feed fixed** — Python's anchor set had Sectigo root R46 (RSA) but not E46 (ECC); Windows
  fetches missing roots on demand, OpenSSL does not. Fixed by ADDING that root, with badssl.com negative
  controls proving verification is still enforced. Feeds **37/38 -> 40/40**.
- **NONE of R28-R36 or T01-T14 is outcome-tested.** Zero resolved rows carry a resolution source, an
  independence argument or a conjunction block. These are mechanism-grounded hypotheses about what would
  have helped, not measured improvements. First honest read is when v3-logged rows mature.

- **9/20 RESEARCH REVIEW + THE THREE CHANGES (`reports/20260920_research-improving-the-engine.md`).** Measured
  properly the book cannot yet be told from a coin: Brier 0.221, **95pct interval resampling the 14 clusters
  0.16-0.26**; a flat forecast at the book's own hit rate (0.745) would have scored 0.190; every row was
  stated between 0.40 and 0.88; small-sample-corrected resolution ~0.00. The 'inverted calibration' reading
  below is SUGGESTIVE, NOT ESTABLISHED (3/5 at a true 0.8 happens a quarter of the time); leg-extrapolation
  stands because it is a mechanism with outside evidence, not a bucket statistic. Built the same day:
  (1) **a reference per row + edge score** - `--base-rate/--base-class/--market/--market-src/--diverge` on
  `add`, `ledger.py ref <id>` for open rows, `report` -> "edge over the reference" with cluster intervals,
  log score, bias-corrected decomposition; (2) **live probabilities** - `revisions` table, `revise` /
  `confirm` / `stale`, time-weighted Brier, `resolve --asof`; first pass done 9/20: 10 rows revised, 9
  confirmed, 9 long-dated rows still stale (no fresh evidence gathered for them); (3) **Iran cluster =
  durations, markers, levels, invariants** - doctrine 16.18, schema R27, `tools/cycle_odds.py`. Schema is
  now **v2, rules R01-R27**; 62 unit tests. NONE of this is outcome-tested: zero resolved rows carry a
  reference yet, so the edge table is empty until new rows mature.
- **9/20 OPEN-BOOK TEST: 77 logged · 47 resolved · 35 HIT / 12 MISS · 2 VOID · Brier 0.220 · 74% · 28 open.**
- **THE FED HIKED 9/16 (25bp to 3.75-4.00, 12-0).** #26 ("no oil-driven hike for six months", **P=0.80**)
  = MISS, Brier 0.64 - the second 0.80 to miss. The 7/29 "flagship win" below was real but its
  extension was not: look-through was a one-meeting wait for the July/Aug CPI (three hike dissents
  on the record), and the engine's OWN CPI row (#32) said that print would be hot. Patch: 11a.
- Also resolved: **#10 HIT** (no durable peace - decided), **#37 HIT** (Jiang desalination call;
  Kuwait plant struck 7/17; under-priced at 0.40), **#11 VOID** (Hormuz carve-out again; GL X was
  dated 6/21 and revoked 7/7, three days after logging).
- Calibration is STILL inverted and worse at the top: P>=0.80 3/5 · P>=0.70 13/20 (65pct) ·
  P<0.60 10/12 (83pct) · skill vs base rate -0.16 · RES 0.014.
- **OPEN PUZZLE:** the hike moved rates (#62 paying: PMMS 6.58 -> 6.95) but NOT the equity derate
  leg - #70 (SMH<SPY) and #27 (SMH<XLE) both tracking MISS. Mechanism fired, asset map did not.
- *(9/19 scoreboard follows for the record.)*
- **Predictions: 77 logged · 44 resolved · 33 HIT / 11 MISS · 1 VOID · mean Brier 0.211 · 75% hit-rate** · 32 open.
- The 9/19 cycle scored 30 rows against primary data: **21 HIT / 9 MISS, Brier 0.231** (+ #23 void).
  The 8/1 maturity-bias warning was right again - 0.169 was flattering.
- **Skill vs a coin: +0.16. Skill vs the engine's own base rate: -0.13. Murphy resolution 0.009.**
  Read plainly: the engine picks the right side 3 times in 4, but its PROBABILITIES carry no
  information - misses were stated at a higher mean P (0.675) than hits (0.654); P<0.60 hit 82pct,
  P>=0.70 hit 67pct. Until resolution clears 0.02, P>=0.70 is reserved for invariant/arithmetic rows.
- **THE LOSS SOURCE (doctrine 16.15):** leg-extrapolation in the Iran/oil oscillation went
  **0-for-8, Brier 0.47** (#19 #28 #29 on the peace leg · #59 #63 #72 on the war leg · #74 #76 on
  the relief leg). Everything else: **33-for-36, Brier 0.155.** Whipsawed three times in eight weeks.
- **THE EDGE:** physical/institutional invariants 8-for-8 (Brier 0.10): #17 #18 #22 #73 #15 #58 #60
  #32. Scheduled prints backed by arithmetic 12/14 (July CPI: every point estimate landed).
- Worst single scores: #24 TSMC GM (0.80 on a long-run prior vs a circulating number -> 0.64),
  #74 XLE>USO (0.56), #59 (0.52, ambiguous wording scored against the engine).
- **Realized P&L: +22.08% summed over TWO closed round-trips, 2/2 wins** - RTX long 195.42 -> 210.00
  (+7.46%) and **MU short 937 -> 800.00 (+14.62%), booked LATE on 9/19**: the pre-registered 800
  target was touched on 7/28 (open 839.61, low 789.09) and went unnoticed for seven weeks. Booked
  AT the target per lesson 4, not at the 737.88 hindsight low. Ledger bookkeeping only - it
  records the rule-based exit, it is not a statement about any live brokerage position. No open
  trades. (Had it been left open: MU printed 1042.40 intraday on 9/9 vs the 1035 invalidation.)
- **Forecast accuracy (Brier) ≠ trading P&L.**
- **PORTFOLIO:** iran-war = 14 of 32 open (44%) - still over the ~35% cap.
- **THE BOUNDARY (revised):** strong where the mechanism is structural, physical and datable;
  weak on one person's discretionary choice (8/1 finding) AND on the DIRECTION of an oscillating
  tape (9/19 finding). Spend conviction accordingly.


### The flagship win
**FOMC 7/29:** engine faded the market — HOLD at 0.75 vs the market's ~0.65 (CME had ~35%
hike). Fed **held**; three dissents for a hike (most since 2016) but the majority sided with
Warsh to wait for the July/Aug CPI in September — *exactly* the no-SEP + data-lag + §11
supply-shock-look-through mechanism the engine used. #67 Brier 0.06.

### The systematic failure (owned) - SUPERSEDED 9/19 by doctrine 16.15
The 8/1 diagnosis below (escalation over-prediction) was HALF the pattern. The engine then
over-corrected into de-escalation (#74, #76) and had already missed the other way in early July
(#19, #28, #29). The real shape is LEG-EXTRAPOLATION in either direction: 0-for-8.

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
| **16.15** | **LEG-EXTRAPOLATION GATE (9/19)**: a call in the direction of the last 10 sessions of Iran/oil tape caps at 0.55 or gets re-expressed as a physical invariant; max ONE same-direction iran/oil row per session |
| **16.16** | **Premise-liveness (9/19)**: a state-premise row ('ceasefire holds', 'strait open') needs a primary datapoint <24h old - the 7/8 batch was logged a day after the ceasefire broke |
| **16.17** | Jiang scorecard: #39 MISS - take his direction and chokepoint salience, never his clock |
| **13f** | No-view odds (`tools/range_odds.py`) before any level/range row; >0.20 off arithmetic needs a dated catalyst; compound bands banned (#69) |
| **13g** | Pass-through is priced off the WINDOW AVERAGE; never downgrade a lag thesis on <1 lag-length of tape (#76 vs #32) |
| **13h** | RV between a 3-vol and a 1-vol leg is a levered direction call (#74) |
| **13i** | A circulating pre-print number beats a long-run prior; P>=0.80 on a print needs the quarter guide (#24) |
| **11a** | **LOOK-THROUGH HAS A CLOCK (9/20, from #26)**: price central-bank rows per meeting; N hawkish dissents + a named print = a scheduled hike; the Fed row must agree with the engine's own CPI row; never hang a falsifier on the statement's vocabulary; 'hike -> equity derate' rows capped 0.55 until the #70/#27 puzzle is explained |
| **16.18** | **DURATIONS, MARKERS, LEVELS, INVARIANTS - never the direction of the next leg (9/20 research)**: the level persists, the direction does not (ViEWS: no-change beats the models); a talks round is near-neutral for termination (Min 2020); this pause is in Fortna's worst durability cell (stalemate, no monitors/DMZ/guarantee); sort information vs commitment problem after every leg. Duration rows priced by `tools/cycle_odds.py` (band; >0.10 outside needs a dated capital-committed catalyst). Do NOT over-correct into the opposite leg. Enforced as schema R27 |
| **16.13** | Structural-state staleness: verify a state hasn't already RESOLVED (carried "succession" live for months after Mojtaba took over 3/9) |

---

## 4. THE IRAN WAR — CORRECTED MODEL (the big rebuild)
War began **2/28/2026** (US Epic Fury + Israel Roaring Lion; **Khamenei killed**).
**Mojtaba Khamenei = Supreme Leader since 3/9 — succession RESOLVED.**
Arc: Apr 8 ceasefire → Apr 22 blockade → **Jun 17 Islamabad Memorandum signed (14-point,
60-day window expiring ~Aug 16)** → ~Jul 9 crumbles → Jul 11–24 round 2 (13 strike nights,
Brent >$100, oil $132, Houthi Red Sea blockade on Saudi) → ~Jul 25+ **US pauses at Iran's
request**, Oman mediating.

**UPDATE 9/20: fire pause day 10 - Iran sends SIX CONDITIONS via Qatar (9/19; reparations dropped) - Iran says it
has been told the US is preparing to resume strikes (9/20) - IAEA Board referred Iran to the UNSC (9/9) -
NPT-withdrawal bill tabled (9/20) - Brent 103.87 - Hormuz 97 non-Iranian transits/week. Root re-weighted:
**frozen oscillation 0.40 - round-3/collapse world 0.45** - succession 0.07 - mediation 0.05 - capitulation 0.03.

**UPDATE 9/19 - what actually happened:** the Jun-17 deal broke on **Jul 7-9** (Iran hit three
vessels; Trump declared it over) → round 2 Jul 9-30 (10+ strike nights, 300+ sites, Brent 100.69
on 7/23, Hormuz ~10 transits/day, Houthi blockade of Saudi) → Trump cancels the 8/1 campaign →
**17 quiet nights** but IRGC tanker hits 8/8 + 8/14 → **window EXPIRED 8/16 with no deal, no
extension** → **round 3 Aug 31-Sep 9** (~100 IRGC targets 9/1; 59 Iranian launches 9/2) →
fire pause since ~9/10 → **Brent 101-109 since 9/9** (peak close 108.75 on 9/15), Aug CPI +0.4,
10y highest since 2007. Hormuz ~10pct of pre-war transits throughout. No Israeli strike on Iran
proper, no US ground troops, regime intact, Mojtaba invisible. Legs last ~2-5 weeks.
Branches now (sum 1.00): **round-3/collapse world 0.55 · frozen oscillation 0.30** (was 0.07 -
the branch the engine under-priced all summer) · succession residual 0.07 · mediation 0.05 ·
capitulation 0.03.

*(8/1 text, kept for the record:)* **The master clock is the Aug-16 window expiry** — everything else is oscillation inside it.
Branches (sum 1.00): **mediation off-ramp 0.35** (was under-priced at 0.10) · window collapse
→ round-3 0.45 · frozen oscillation 0.07 · succession residual 0.08 · capitulation 0.05.
Market read: **the war premium is CYCLICAL, not permanent** — trade convexity into the window.

---

## 5. LIVE STAKED CALLS (tested 9/20 - full table in `reports/20260920_open-book-test.md`)
*P column: first stated -> CURRENT after the 9/20 revision pass (`ledger.py revise`; history in the `revisions` table; also #2 0.50 -> 0.35, #54 0.55 -> 0.45). Rows score time-weighted, so seven weeks at the old price still count. These are the analyst's catch-up steps from the 9/20 evidence - overrule any of them with another `revise`.*
| # | Call | P | Horizon | Status 9/20 |
|---|---|---|---|---|
| **#70** | SMH underperforms SPY since 7/31 | 0.58 -> **0.15** | 9/30 | tracking MISS (SMH +6.0 vs SPY +2.0) |
| **#27** | IF Brent>90 on Iran THEN SMH < XLE next month | 0.72 -> **0.35** | judged ~9/30 | trigger fired 8/31; tracking MISS (+2.9 vs +0.5) |
| **#62** | 30y mortgage +25bp vs 7/23, never -15bp | 0.62 -> **0.82** | 10/1 | tracking HIT (6.58 -> 6.95; two prints left) |
| **#14** | Succession contested / not publicly exercised | 0.62 | 10/8 | tracking HIT (no appearance in six months) |
| **#30** | Credible reconstitution reporting | 0.52 | 10/11 | AMBIGUOUS, leaning HIT (WSJ 7/21 + CSIS + Grossi vs 'no concrete information') - AGREE THE READING BEFORE 10/11 |
| **#56** | Midterms held + federal intervention fight | 0.55 -> **0.75** | 11/30 | tracking HIT (the fight is already here; SCOTUS blocked the USPS rule 9/15) |
| **#38 / #36** | Jiang: ground invasion by 12/31 - troops-or-bribe | 0.70 -> **0.20** / 0.45 -> **0.38** | 12/31 - 1/13/27 | tracking MISS (no troops; Iran's 9/19 conditions ask for frozen funds) |
| **#53** | No PLA action on Taiwan in 2026; China presses de-escalation | 0.93 | 12/31 | tracking HIT |
| **#12** | No published, enforced Hormuz toll | 0.62 | 1/4/27 | tracking HIT |
| **#16** | Israel strikes Iran proper | 0.74 -> **0.60** | 1/8/27 | not occurred; OVER-PRICED unless a renewed US round pulls Israel in |
| **#3** | Pentagon ~$1.5T FY27 | 0.55 -> **0.30** | 1/31/27 | tracking MISS (CR to 12/11; nothing enacted). RULE: nothing enacted by the horizon = MISS |
| **#35 / #1** | Frozen conflict - war continues for years | 0.55 / 0.70 | 7/13/27 - 4/21/28 | tracking HIT; #35 threatened by renewed-strike reports 9/20 |

**Tree forward nodes (NOT ledger rows):** `us-strikes-resume` 0.45 -> **0.35** by ~10/12 (repriced from `cycle_odds`: pause-ends band 0.32-0.46, and strikes are a subset of endings) - `pause-outlasts-oct12` 0.58 (duration) - `pause-durability-marker` 0.08 by 10/31 (monitors/DMZ/guarantee - the only thing that should move frozen-conflict much) - `iran-six-conditions` 0.25 -
`fomc-oct` second hike 0.60 by 12/9. **Catalysts:** PMMS 9/24 + 10/1 - UNSC panel 9/26-27 - 9/30 (#70/#27) -
FOMC minutes ~10/7 (the #26 attribution check) - 10/8 (#14) - 10/11 (#30) - FOMC 10/27-28 - midterms 11/3 - CR 12/11.
**Levels:** Brent 100 support, 108-110 the round-3 high - SMH 605 / 480 - PMMS 6.83.
**Before the next batch:** `ledger.py stale` (revise/confirm first), then `ledger.py add --dry-run` WITH `--base-rate/--base-class`
(and `--market` where liquid), `tools/range_odds.py`, `tools/cycle_odds.py` for durations, the 16.15 leg-neutral gate, and 11a
on anything touching the Fed. New rows go OUTSIDE the iran-war cluster (over the 35pct cap). Log NOTHING off the 9/19-20 conditions/strike headlines (16.15).

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

**Rules (v3, 2026-09-21):** `python pipeline/schema.py rules` prints R01-R36; `python pipeline/trade_rules.py`
prints T01-T14. `schema.Context` now carries `open_rows` + `book_base_rate` so R28/R31/R34 can check the
book against ITSELF — pass them or those three rules silently no-op.

**Ledger commands:** `add` (now with `--lean`, `--dry-run` wording lint), `resolve`, `void` (conditional
whose trigger never fired - unscored, still needs a lesson), `lesson`, `due`, `sweep`, `report`, `redteam`,
`trade-open`, `trade-close`, `pnl`. **Since 9/20:** `ref` (record a row's reference forecast), `revise` / `confirm`
(live probabilities, history kept), `stale` (open rows nobody has looked at in 7 days; the sweep warns, does not fail),
`resolve --asof` (scoring stops the day the outcome was known). `tools/cycle_odds.py` = no-view odds for duration rows.

---

## 6b. THE DAILY ANALYST (built 2026-09-20)
`pipeline/analyst.py` + `pipeline/schema.py`. Twice a day: inbox -> deterministic pre-cut -> headless
Claude (four skills, lint, range_odds, web) -> **typed** `proposals/<stamp>/analysis.json` checked by
rules R01-R27 -> `REVIEW.md`. **Propose-only:** the run cannot write the ledger (no tool for it, and
protected files are hashed + restored); rows enter only via `analyst.py approve`, which re-checks the
rules, backs up, logs `--source auto`, wires the timeline. Verified 9/20: mypy --strict clean, 30 rule
tests, and an end-to-end run where a deliberately hostile stub CLI wrote to ledger.db and CLAUDE.md -
both were restored and the leg-extrapolation row it proposed (P=0.70, with the tape) was BLOCKED by
R12+R13. Two REAL headless runs (Claude Code CLI 2.1, sonnet, ~10 min each on tiny batches) produced
clean typed output, self-validated to 0 errors, proposed ONE modest row each (P 0.58-0.60), and
triaged a prompt-injection headline as noise without acting on it. **Pending on this machine:** Claude Code CLI installed + `CLAUDE_BIN` in `.env`, then
`tools\start_analyst.cmd`.
**Per-article stage (9/20): Jev by TypeSafe AI** (`pipeline/jev.py`) - typed verdict on EVERY article, never
discards alone, state-change alerts feed 16.16, keyword fallback without a key. Built against the
PUBLISHED API contract and tested against a local mock of it (request shape, strict answer parsing,
429/529 retry, 401/422/outage fallback) - **NOT yet run against the live service: needs
`TYPESAFE_API_KEY` in `.env`, then `python pipeline/jev.py try "Fed holds rates"`.** Watch
`logs/jev_agreement.jsonl` (articles Jev alone would have lost) before leaning on it harder.
Claude Code commands: `/jev-triage`, `/analyze-news`, `/review-proposals`. The rules encode the 9/19 findings - if resolution climbs past 0.02, relax
R13 in `schema.py` deliberately, not by accident.

---

## 7. THE DASHBOARD
`pipeline/dashboard.py` (stdlib only). **6 tabs:** Monitor (overview + P&L + watchlist
manager + triggers + tape) · Reports · **Timeline & Predictions** · Fusion · Ask Engine · Settings.

- **Theme:** monotone dark — one neutral ramp (`#0b0b0c`→`#f4f4f6`), 3px radii, no glows.
  Colour ONLY for state (sage=HIT, clay=MISS, amber=due).
- **Timeline map:** time-lane DAG. X = real time (near-term gets the space: July 2026 ≈ 870px),
  **31 lanes, 466 nodes** (66 + 200 on 9/21 + 200 on 10/02). Verified after the 10/02 merge: 505
  positioned boxes, **0 overlapping pairs**, canvas 2860×8604, and checked visually as well as in the
  DOM (lesson 5). BUILDOUT B deliberately filled the far field — the tree had 17 nodes in 2028, 5 in
  2029 and 4 in 2030; it now has 82 / 39 / 30. New lanes: us-fiscal, housing, insurance-risk,
  sovereign-credit, global-elections, russia-ukraine, africa-frontier, india-sa, regulation-legal,
  space-orbital, transport-aviation, water-ag-infra. **Edges = temporal implication "IF x THEN y"** with arrowheads, all
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
6. **Check price-defined rows and trade targets EVERY session, not only at horizon.** #33
   resolved on 7/28 and sat open seven weeks; trade #2's 800 target was touched and never
   booked; #69 was dead the day STATE.md listed it as live. Rows can die early - look.
7. **When two of your own rows contradict (#32 vs #76), that is a hedge, not two insights.**
8. **CHECK THE UNITS BEFORE YOU TRUST A TOOL'S ANSWER (9/22).** `range_odds.py --vol` is **daily
   percent**, not annualised — `1.6` means 1.6%/day. `brent-band-q4` was "corrected" from 0.66 UP to
   0.82 on a run passing `--vol 0.80` (≈13% annualised) for a tape realising ~2.5%/day (≈40%). At the
   honest vol the no-view odds are **0.33, not 0.97**, so the original price was already too high and
   the "fix" moved it further the wrong way. The arithmetic was never wrong; the input was. Same shape
   as the VIX-lookahead and rolling-tape-window failures, and it happened INSIDE a correction — which
   is the dangerous place for it, because a correction carries borrowed authority. Rule: when a tool
   returns a number that makes your row look safe, re-derive its inputs from the repo's own tape
   before you act on it.

---

## 9. TWO-MACHINE SETUP (laptop + desktop, since 2026-09-19)
The project is a **private git repo**: `https://github.com/truchard0/GT-Analyst` (pushed 2026-09-19, first commit 645f994). Code, doctrine, `data/timelines.json`, `reports/` and
**`ledger/ledger.db`** all travel. Excluded: `.env`, `config.json` (API key), `inbox/`
(~29MB feed dump), `ledger/seen.db` (~6MB dedup cache, rebuilds itself), `logs/`.

**⚠️ THE ONE RULE: `ledger.db` is SQLite — git CANNOT merge it.**
If both machines commit a change to the ledger, you get a binary conflict resolvable only by
picking one file and *losing the other machine's predictions*. So:
1. `git pull` **before** you start a session.
2. `git push` **when you finish** one.
3. Never run a logging/resolving cycle on both machines at once.

**Per-machine setup after cloning:**
- **Python 3.12+ required** (`dashboard.py` uses nested-quote f-strings; `common.py` uses
  `datetime.UTC`, 3.11+). 3.10/3.11 fail `tools/debug_all.py` on syntax.
- `cp .env.example .env` and fill in keys (RSS-only ingestion works with none).
- Re-enter the Anthropic API key in the dashboard Settings tab — `config.json` is gitignored
  and does NOT travel, by design.
- `seen.db` regenerates on the first ingest run; expect one noisy cycle as it re-learns what
  it has already seen.
- The **Task Scheduler ingest job is machine-local** (`tools/register_task.ps1`). Run it on
  ONE machine only, or both will write to their own diverging `seen.db`.
