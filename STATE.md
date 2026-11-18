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

## 2. SCOREBOARD (as of 2026-10-22)
- **10/22 SCORING: 53 resolved · 39 HIT / 14 MISS · 74% · Brier 0.2205 · 24 analyst rows open** (35 tree-promoted rows
  open and separate; none has matured). Three rows scored, all HITs:
  **#30 HIT (hit-wrong-reason)** — the user agreed the reading on 10/22: construction/activity at Pickaxe Mountain counts as
  reconstitution reporting (CSIS 9/9, Grossi 9/10-11), scored as-of 9/11, Brier 0.2304. WRONG REASON because the row's frame
  (post-war deterrence rebuild straining a US-brokered deal) was already false — the deal expired 8/16 and the war resumed.
  PROCESS FAILURE: 'credible' was flagged unscoped on 9/22 and the reading was settled 11 days AFTER the horizon (the #59 shape).
  **#79 HIT** (Brier 0.0400) — PortWatch 4 transits on 10/4 vs a pre-crisis baseline of 85/day (~5%); Kpler 7-20+ commodity
  vessels/day; 10/21 reports 4-5/day. The 9/22 "may reopen within 7 days" report did NOT convert: that is the FIFTH reopening
  signal with no durable reopening (a second "Iran sets conditions for reopening within 7 days" headline ran 10/21).
  The row named no source, so it was scored on PortWatch with Kpler as corroboration. **#14 HIT** (Brier 0.1444) — no verified
  public appearance by Mojtaba Khamenei since 3/9; the final-week (10/1-10/8) confirmation is BY ABSENCE, so a missed appearance
  is possible.
- **Skill vs own hit rate is now -0.134** (was -0.118): three HITs raised the hit rate to 74% without lowering Brier enough to
  matter — the probabilities still carry no information beyond "we are usually right". CI 0.156..0.255, still not separable
  from a coin.
- **Open level rows checked for early death (10/22): all alive.** Brent (#83) settled 100.20..113.32 since 10/5 — only ~10%
  under its $125 ceiling, so it is the one to watch; now registered in data/autoresolve.json so `tools/tripwire.py` checks it
  every run. IG OAS 0.88 vs <1.60, HY OAS 3.27 vs <5.00, DFII10 2.77 vs >1.50, U-3 4.2 vs 3.8..5.2: alive, FRED-backed so
  checked by hand (the tripwire taps yfinance only).
- **10/22 CURRENT EVENTS (verified from the tape + feed, not just headlines):** Brent 113.2 (+4.0% on the day, +10.7% since 10/02, highest
  since May); WTI 99.4; **SMH 521 (-6.4% today, -17.4% since 10/02)**, QQQ -3.1% today / -6.3%, SPY only -1.0% since 10/02; VIX 19.6
  (+17%); 10y 4.95 (-3.8% today); gold -2.7%. Drivers reported: Meta's AI-funding plan (non-voting shares; size of the drop disputed:
  CNBC ~8% vs Reuters ~2%), Nvidia's CEO on capital scarcity, CoreWeave credit worries, plus 18 Hormuz attacks in two weeks and Iranian
  state TV claiming 7 tankers burning (unconfirmed). Fed: hold expected 10/28 (CME hike odds ~17-22% per two reports), Sept payrolls
  +29k reported weak. Iran "U.S. war drags on", Iran ruled out talks until conditions met (10/22). **For the book:** (a) #83 Brent is now
  ~10% under its $125 ceiling on a 4%/day tape; (b) the tree's `capex-debt-funded` branch (0.38) is exactly what the AI-financing
  headlines are testing - REPRICED 10/22 0.38 -> 0.45 (and its sibling 0.62 -> 0.55) after fixing the fork, which was not exhaustive (equity issuance fell in neither branch); facts on the Meta issuance are disputed so the step is small; (c) the semis derate that #70/#27 forecast arrived
  ~3 weeks AFTER their windows closed - scored MISS correctly, but it is one more sign the macro call and the asset map can be right and
  wrong on timing, so do not read it as vindication; (d) `fomc-oct`'s 0.60 second-hike node should be re-checked against the hold pricing.
- **10/22 EVENT TRACKING BUILT (the user's point: events were happening and nothing tracked them).** Measured first: the feed
  captured **84,487 items since 9/21; the tree held 3 news-type evidence entries** (all hand-added). Root cause: the daily
  analyst was never set up (no .env, no CLI), so nothing digested the feed. Built: `tools/event_harvest.py` (collapses
  syndication into 55,318 stories, ranked by independent OUTLETS - a measure of how widely a story ran, NOT how much it matters),
  `tools/events_merge.py` (validates events against real node/row ids, writes `data/events.json`, attaches dated evidence,
  validates proposed nodes with the tree's own rules, NEVER changes a probability, labels plans "PLAN, NOT EXECUTED"; 7 tests).
  Four curation passes (iran/energy, macro/markets/AI, geopolitics, US politics/legal) -> **133 events (100 verified on the
  web, 17 multi-outlet, 9 plan-only, 7 feed-only), 226 evidence entries on 106 nodes, 30 new `ev-` nodes**. Tree now **504 nodes**;
  news-type evidence dated October went 3 -> 200. Only 7 events had no home - most of the gap was missing EVIDENCE on existing
  nodes, not missing nodes. NOT automated: re-run `event_harvest.py` then a curation pass then `events_merge.py` by hand
  (or set up the analyst). All suggestions stay in `data/events_reprice_suggestions.json` (17, 11 of them applied below).
- **10/22 REPRICINGS FROM THE EVENT PASS (applied only where a verified datapoint or the tape supported it):** #103 10y>4.00
  0.80->**0.95** (3.2 sigma at measured vol; the 10/3 note that 0.80 was too low went unacted for 19 days) - #96 France deficit
  0.78->0.90 (govt forecast 5.4% vs 4.5%) - #105 EU storage 0.72->0.62 (14.9pp under 5y avg) - #114 shutdown 0.35->0.30 -
  #56 0.90->0.94 - nodes fomc-oct 0.60->0.68, us-strikes-resume 0.35->0.08 (window passed), iran-six-conditions 0.25->0.12,
  pmms-above-65 0.82->0.90. Nodes synced to their rows (brent-band-q4, natgas-storage had drifted from #83/#98 - lesson 7).
  **DECLINED:** a further +0.10 on `capex-debt-funded` (strong claims about an Alphabet equity plan / Meta bond sit only in
  the reason text, not in the verified events); both Iran pause nodes (the pause is undefined - do IRGC tanker attacks and Houthi
  strikes on Riyadh break it?); `midterms-2026` (stricter claim than #56: a federal CERTIFICATION fight).
- **OPEN QUESTIONS FOR THE USER:** (1) #12 - does informal fee collection from select vessels count as an "enforced standing toll"?
  (2) define the Iran "fire pause". (3) `opec-nov-meeting` / `opec-quota-unchanged` are dated 11/30 but Reuters says the OPEC+
  core group meets 11/1 - a possible mis-date from my 10/02 buildout. (4) Several feed items are RE-RUNS of old stories (a
  4/2026 Saudi pipeline attack resurfaced 10/16; a May-2025 Russia-gas headline), so first-seen dates mislead.
- **10/22 NEWS ANALYST = THE MYSTERY MACHINE'S (user instruction: "you have the same news analyst as the mystery machine, use theirs").**
  GT-Analyst's own analyst (pipeline/analyst.py, headless Claude CLI) was never set up. The Trading Bot already runs one:
  `tradingview/mystery_machine.py` (runner `mystery`) scores headlines with a LOCAL Ollama model (qwen3:14b, up on :11434),
  groups them into STORIES with developments, and rates each development's importance / market direction with a reason.
  `tools/mystery_events.py` consumes `tradingview/_skylit/news_ai/stories_month.json` + `stories_live.json` READ-ONLY (a test
  fails if it ever writes into their directory - mutation-checked) and writes `promo/events_mystery.json`, which
  `tools/events_merge.py` folds into the event log (confidence `mystery-ai`). It does NOT call their Ollama (their live scorer
  shares that GPU). 5 tests.
  **WHAT I MEASURED BEFORE TRUSTING IT:** their importance means "moves the stock market today" - Stifel upgrades, earnings
  previews, retail commentary and market WRAPS all score high; only about a third of 14 sampled imp>=0.5 stories bore on this tree.
  So the adapter adds what they lack: macro/geo families only, a topic->lane router (word-boundary regexes - a `` mangled
  into a backspace by this shell silently zeroed the first version), no wraps / routine prints, and per-day pick of the best
  ON-TOPIC head. It surfaces real events the web-curation passes missed (the 9/23 White House 90-day DIESEL EXPORT BAN plan;
  Fed speakers Barr "further hikes likely needed", Williams, Hammack, Perli). **Node matching was ~50% wrong** (Fed-speaker
  events attached to `fed-chair-term-2030`), so NOTHING is attached to nodes automatically: events are logged with
  `candidate_nodes` for review. Result for 9/22-9/28: 21 events logged (154 total in data/events.json), 0 node evidence added.
  **LIMITS:** their month backfill (`--backfill-ai 2026-09-22 2026-10-21`, running in WSL) had reached only 9/28 of 30 days
  (894 of ~5.5k headlines; ~2.3 s/headline) - re-run `python tools/mystery_events.py --since 2026-09-29 --write` then
  `python tools/events_merge.py --write` when it finishes. Not scheduled: a standing task is the user's call.
- **10/22 NO BACKGROUND WATCHER - PULL ON DEMAND ONLY (user: "only pull this data when i ask a new question so save compute").**
  A one-shot watcher (`tools/run_when_mystery_done.py`) was started and then STOPPED the same day; it is not running and nothing
  polls anything. The Mystery Machine news adapter and the event merge are run BY HAND when the user asks:
  `python tools/mystery_events.py --since <date> --write` then `python tools/events_merge.py --write`. Their month backfill
  (`--backfill-ai 2026-09-22 2026-10-21`) was at day 9 of 30 (9/30) when checked - re-check with
  `python tools/run_when_mystery_done.py --check` (read-only, one call) before running the adapter. Do NOT schedule it or leave a
  loop running without being asked.
- **10/22 merger bug fixed:** `events_merge.py` overwrote `events_reprice_suggestions.json` each run and a later merge with no
  suggestions erased 17. It now preserves them; the record was rebuilt from promo/merged/ with a `status` on each (13 applied,
  4 declined, 0 undecided). Merged agent files are archived in promo/merged/ so the merger reads only new input.

- **Still unresolved/overdue:** none past a horizon. 10 rows are due a re-look (oldest 29 days late: #56 #38 #53 #12 #16 #36
  #80 #35 #5 #1). Known report bug: "stale 62/27" counts tree rows in the numerator.

*(10/02 entries follow for the record.)*
### 2c. SCOREBOARD (as of 2026-10-02)
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

- **10/22 rulings:** #12 RESOLVED HIT (user's FINAL ruling, reversing an earlier same-day answer: informal select-vessel fee collection does NOT count as an enforced standing toll). Resolved early on 10/22 (horizon 2027-01-04): a formal schedule appearing later does not reopen it. See current figures from `ledger.py report`.
  OPEC+ date FIXED: next meeting is 11/01 (OPEC press release 10/04, Reuters), nodes opec-nov-meeting / opec-quota-unchanged moved from 11/30 (also in buildout_2026_09_21.py). Whether a separate full ministerial falls in late Nov/Dec is UNCONFIRMED.
  VOLUME != IMPORTANCE: event_harvest 'salience' renamed 'coverage' (orders the reading queue only); mystery_events no longer admits a story because it has >=5 headlines; significance comes only from the model's/curator's judgment.

- **10/22 ELECTIONS BUILD + LESSON 9 (user: "you should have gotten iran escalation around the midterms").** The tree had it (ev-post-midterm-us-strikes 0.35, us-strikes-resume 0.08 pre-vote) - the PLAN did not, because it was written from the web without opening the tree. Built `tools/buildout_d_elections.py` (+14 nodes: Israel certification/tasking/Knesset swearing-in/Netanyahu-PM-on-12/1/no-government-by-12/1/no-bloc-61/pardon; US no-approps-pre-vote, Congress 1/3; FOMC 10/28 statement; Iran pre-vote US no-strike 0.84, Israel pre-vote strike 0.07, energy-infra strike 0.28, pledge extension 0.12) and 5 reprices (midterm fork 0.55/0.30/0.15 -> 0.80/0.12/0.08 on forecaster refs; ev-post-midterm-us-strikes 0.35 -> 0.45 on execution signals + cycle_odds 0.69-0.78 pause-ends band; knesset vote 0.95). #16 revised 0.45 -> 0.52. Tree 518 nodes. NOT promoted to ledger rows: each promotion needs a verified resolution source and base-rate counts and several here rest on recollection (coalition lags) - verify first.
  `tools/window_plan.py` (+4 tests): prints what the book already says about a window, uncovered forward-dated statements, and focal-date x conflict coupling holes. Run it BEFORE any dated plan (doctrine 16.19). First live run: 6 holes after 12/1 (APEC 11/19, FOMC 12/9, CR 12/11, ECB 12/17, BoJ 12/19) - none has an Iran-coupled node. R28 still cannot see vol-vs-vol conflicts (all Iran rows are direction 'vol'); extension (a conflict-level field) NOT built, awaiting the user.
  CHECKPOINTS (run only when asked): 10/28 Israeli result + FOMC; 11/4 US House call + certified Israeli results; ~11/18 president tasks + Knesset sworn; 12/1-12/11 formation, Georgia runoff (verify), CR deadline.

- **10/22 CONFLICT CHECK BUILT (user: "fix the conflict check").** `pipeline/conflict.py` + R28's second half. A conflict cluster (iran-war) has a
  level scale 0 settled / 1 pause / 2 incidents / 3 strikes on Iranian soil / 4 war-scale; each row declares the interval its event IMPLIES
  (`ledger.py add --level 3-4`, `--level none` to opt out, `--hedge` to hold two rows that cannot both hold; schema `conflict_level {lo,hi}`).
  Two checks: FEASIBILITY (one distribution must give both rows P(L in I) >= p; disjoint claims must sum under 1, nested windows are monotone) and
  ESCALATION (a likely strike on Iranian soil vs a likely 'no war-scale': this war's strike episodes became campaigns 3 of 3, Wilson lower bound
  0.53 errors, point estimate 0.80 warns; longer windows are scaled to the shorter at a constant hazard). Columns level_lo/level_hi added;
  #16 backfilled [3,4], #38 [4,4]. 13 new tests (conflict 10, ledger gate 5, schema 3).
  **HONEST RESULT: the 2026-07-08 batch (#19 vs #15/#16/#20/#21) is NOT formally incoherent** - `python pipeline/conflict.py --demo` finds 0 conflicts. #19's loss
  was a dead premise (16.16: Iran hit three vessels on 7/7), and no row that day asserted a strike inside #19's 60-day window (#16 ran to 1/8). The earlier
  claim that this check 'would have caught #19' was wrong; what it closes is the vol-vs-vol blind spot for FUTURE rows.

- **10/22 CALENDAR VIEW (user: "show the map also in calendar format").** Timeline tab now has a Map | Calendar toggle (`pipeline/dashboard.py`: `tlView`, `calBuild`; choice kept in localStorage `gt-tlview`). Same data as the map: tree nodes by date (probability chip, green/red/amber edge = scored hit/miss/mixed or happened) plus open analyst-row horizons in violet; month nav + jump list with counts, lane filter, 'show certainties (p>=95%)' (hidden by default) and 'ledger horizons' toggles; click a chip for the node's reasoning (or the ledger row), click a date for the full day. Dashboard server restarted to load it. Assumed 'the desk' = this GT-Analyst dashboard.

- **10/23 PAST NODES ARE HITS OR MISSES + CALENDAR WINDOWS + REFRESH FIX (user).** (1) `tools/resolve_past_nodes.py`: all 67 past-dated nodes now carry `resolved {happened, verdict, called, basis}`;
  verdict = was the CALL right (HIT iff (p>0.5)==happened); p is NOT overwritten, so branch sums still audit. 25 lane anchors = structural HIT; 42 events = 28 HIT / 14 MISS.
  Judgement calls (review): `--report` lists them (succession-tip, tech-tailwind, fire-pause-sept, frozen-oscillation [overlaps flip-b], frozen-conflict [PROVISIONAL], pause-outlasts-oct12 [depends on how
  'pause' is defined]). tripwire.py section [4] flags any new past-dated node without a verdict; `resolve_past_nodes.py --check` lists it, `--write` applies decisions in its TABLE (it refuses to guess).
  (2) Calendar view now draws each node as the WINDOW it can happen in (label 'between A and B', else [creation, deadline] from `horizon`; scheduled/invariant/checkpoint = a day; live windows start today; >45 days = grey
  line + deadline bar), % = probability of happening in that window, green/red = HIT/MISS, strike-through = did not happen. (3) Auto-refresh no longer reloads the 1.5 MB page every 30s: it asks /api/version and
  reloads only if data changed AND the tab is visible. Server runs as a detached hidden python (not tied to a chat); restart = kill the :8787 listener and `python pipeline/dashboard.py 8787`.


- **10/23 verdict fixes (user questions).** (a) fire-pause-sept read 'MISS - the engine called 100%': the node was written after the pause began, so the call graded is the 40% the engine had on the frozen-oscillation branch it realised; every pre-pinned node now stores `called` + `called_from` (ledger row first-stated P, inverted for complements) and the verdict is re-derived by the one rule (`resolve_past_nodes.py --recall`). (b) highbeta-derate flipped MISS -> HIT BY USER RULING (needed more time: 8/31->10/22 SMH -5.98% vs XLE +6.27%); ledger #27 STAYS MISS on its own 'over the following month' wording (scored to 9/30, SMH +9.41% vs XLE -3.27%), so node and row differ on purpose. Lesson: a node that says 'month following trigger' should carry an explicit end date, or the timing miss and the thesis miss look the same.
- **10/23 UNFORECAST verdict (user: 'do it').** Nodes written AFTER the event they record (round-3, fire-pause-sept) are no longer graded: verdict `UNFORECAST`, shown as 'NOT FORECAST - written after the fact; the engine had this world at 40%'. Non-anchor nodes now 29 HIT / 11 MISS / 2 UNFORECAST.

- **10/23 CROSS-CLUSTER CHECK BUILT + REPLAYED (user: "build cross cluster check, see what would have been removed").** `pipeline/conflict.py` gained named WORLD STATES (hormuz, brent_peak, cpi_jun/jul/aug) that rows from ANY cluster claim intervals of (`ledger.py add --state hormuz=0-1`; schema `states[]`; column `states`); disjoint claims about one state (horizons within 45d) must sum under 1 or the later row is refused unless `--hedge`. `data/state_labels.json` = 22 rows labelled from their own text (stated vs `inferred`). `python tools/retro_conflicts.py [--exclude-void]` replays the book: the gates would have refused 6 rows - #29 MISS, #39 MISS, #59 MISS, #38 open (vs #35, same day), #60 HIT, #64 HIT; 54 -> 49 resolved, outcome-true 74.1% -> 77.6%, first-stated Brier 0.2212 -> 0.2119. The gate refuses the LATER row and in 3 of the pairs the kept row was the miss: removal is not the value, the forced choice is. NOT caught: #26/#32, #76/#32, #72/#68 (disjunction or posture, no shared state); #29 vs #22 rests on an INFERRED label. 13 new tests (216 total).

- **10/23 two user rulings after the cross-cluster replay.** (1) #59 RESOLVED HIT (was MISS): the ceasefire did fail and was never shown to hold; IRGC tanker hits on 8/8 and 8/14 COUNT as Iranian strikes, so 10 strike-free days did not occur before 8/15. Book now 54 resolved, 41 hit (76%), Brier 0.2109. (2) The replay's remedy was wrong, not its flag: refusing the LATER row removed #60/#64 (right calls made after the conflict reignited). `tools/retro_conflicts.py` now runs policy B - when the open row's premise was already dead on the new row's date (`premise_dead` in data/state_labels.json: #19, #23, #28, all dead by 7/9) the STALE row is retired and the new one stands; only a flag against a LIVE row refuses. Under B the gates remove #19, #23-as-void, #28, #29, #38-vs-#35, and keep every hit.

- **10/23 PAUSE - REWORK REQUESTED (user: "pause and rework everything").** #59 put BACK to MISS (the 10 strike-free days 8/2-8/14 DID happen; my same-day flip to HIT is withdrawn; book 54 resolved, 40 hit). THE USER'S THESIS, to become engine logic: strikes are held off for POLITICAL and ECONOMIC reasons (US midterms 11/3, Israeli campaign 10/27, pump prices, Gulf requests - Trump stood down the 8/1 campaign at Iran's and the Gulf's request); a strike-free window is therefore PREDICTABLE from the deciders' calendar; shocks and price jumps come only after a cooling-down period (the 10/22 reports: US/Israel strike plans for after the vote). The engine priced the military leg and never asked what the deciders wanted in the window. Candidate rework (NOT built, awaiting go): (1) doctrine 16.20 decider-incentive layer; (2) data/constraint_calendar.json of dated suppress/permit windows per decider with the public fact behind each; (3) a rule that every escalation/ceasefire row cites the window it sits in; (4) a time-varying hazard (cycle_odds x window multiplier) pre-registered forward; (5) re-read every Iran miss through it. Evidence so far (N=3, suggestive only): pauses ran 20d, 32d, 43d+ and began 139, 94, 54 days before the vote.

- **10/23 WAR BACKTEST (user: "see what happened in the war and what the engine would have predicted... predictions before learning, then learn off what you predicted wrong").** `data/war_timeline.json` (strike days, dovish acts, Iranian triggers, from the Wikipedia timeline) + `tools/war_backtest.py` (rules hashed ae94053c before scoring). Result in doctrine 16.20: decider-incentive priors do NOT beat persistence over the whole war (0.280 vs 0.268), win only in the political stretch; every miss is a dovish week that broke on an IRAN trigger; a refit on early weeks overfit (held-out 0.291 vs 0.223). Coding caveat: 6/11-6/16 strike days are uncoded (the 6/10 'Y=0' may be a coding gap). Forward v1 numbers (0.02-0.07 pre-vote, 0.23 post-vote) rest on an untested pledge multiplier (n=1): do NOT replace the tree's 0.84 / 0.45 with them. NOT built: the constraint calendar, the rule that escalation rows cite their window + trigger, the re-read of every Iran miss. Awaiting the user's call on scope.

- **10/23 REWORK BUILT - all 3 (user: "all 3").** (1) `data/constraint_calendar.json` + `pipeline/constraints.py`: 10 decider windows (US pause/MOU/stand-down/pledge/energy-price, Israel campaign, post-vote release, Iran pre-vote pressure) with public fact + `known_from` + what ends them, 10 triggers. (2) RULE R37 (schema `incentive{act,claims,window,trigger}`; `ledger.py add --act --claims --window --trigger`, required with `--level`): refuses a strike call >0.5 inside a known suppress window with no live trigger, and a calm call >0.5 within 7 days of a trigger; a later stand-down supersedes an earlier trigger. Open #16/#35 backfilled. (3) `python tools/lens_reread.py`: 9 Iran rows about the four acts, calendar had a lean on 8, right on 6 (rows right on 4); R37 refuses #19, #28, #72 (misses) and #68 (a hit). NOT caught: #59 (needs a campaign-duration/stand-down hazard: rounds 39d, 16d, 11d) and #63/#29/#39 (outside the four acts). 18 new tests (234). Caveat: the calendar and triggers were coded AFTER the outcomes were known - this shows what the lens would have asked, not a clean forecast score.

- **10/23 MARKET OUTLOOK (user: "full market prediction for the coming months... using aid from the skylit data").** `reports/20261023_market_outlook.md`: where we are (SPY 759.97, -2.5% off the 10/6 high; QQQ -7.3%; SMH -21%; VIX 19.5; 10y 4.99; Brent 111.7), the dated calendar to January, three scenarios (A restraint holds 0.50 / B limited post-vote strike 0.28 / C sustained campaign 0.22) built from the tree and the war's own event reactions (strikes: Brent +22% to +38% in 10 sessions, SPY -2.5% to 0%; stand-downs: SPY +1% to +8%), no-view ranges, and 14 frozen claims registered in prereg/REGISTRY.jsonl. SKYLIT: saved overnight maps (10/23) give SPY net gamma -702M, flip 754.1, negative King 755 (-367M), SPXW flip 7495, QQQ flip 689; two tests on 734 sessions of Skylit's daily SPX gamma summary found NO significant multi-month vol or direction signal (gamma size vs next-20d vol Spearman -0.14, CI [-0.29, 0.00]). No Skylit credits spent; the Dec/Jan monthly-book maps are not stored locally (hist stops 9/30, live keeps 5 expiries) - a pull needs the user's OK with a credit count. Scripts in the session scratchpad only.

- **10/23 AUDIT OF THE OUTLOOK + EARLIER WORK ("double check your work") - 3 errors found and fixed.** (1) `pipeline/conflict.py` ESCALATION was (3, 3) - 'every strike episode became a campaign' - because the four one-off retaliations (5/7, 5/25-27, 6/7-10, 6/26-27) were left out; counting episodes in data/war_timeline.json gives **3 of 7** (Wilson lower bound 0.29, point 0.44, not 0.53 / 0.80). The check therefore flagged #59 vs #19 and #64 vs #19 wrongly: RETRACTED. Retro replay now: policy A removes #29, #38, #39, #60; policy B retires #23 (void) and #28 and refuses #29 and #38 (#19, #59, #64 are no longer flagged). The tests that leaned on 3-of-3 were retuned (235 pass). Round lengths corrected to 39, 16 (22 with the 7/29 strike) and 11 days. (2) The outlook's scenario centres (A 785 / B 767 / C 720) implied a year-end median of 771 and P(above today) 0.63, contradicting its own text and claim 1; re-centred to 775 / 760 / 715 with spreads 35-40 (median 760, 5-95% 681-826, P(above) 0.50). (3) Claim 11 compared a 754.1 barrier with a no-view figure computed for 750; recomputed on a closing basis (0.56-0.70) and set to 0.62; claims 2-4 now name the basis of their references. Re-registered as `market-outlook-20261023-r2` (REGISTRY is append-only; the first entry stays, superseded). VERIFIED CLEAN: all 16 book probabilities the report cites match the tree; the market table recomputed from raw closes; Skylit levels re-read from the saved files; trading-day counts (10/20/47/66).

- **10/23 FACTS ARE NOT CALLS + CALENDAR HIGHLIGHT (user, two messages).** (1) The Supreme Court term opening was shown as 'HIT - the engine called 99%'. User: these are factual events, nothing like this should be a call. Rule in `tools/resolve_past_nodes.py::is_fact` and the dashboard (`isFact`): a lane anchor, a node of class invariant/scheduled at p >= 0.95 (term opens, meeting held, election day), and the Islamabad window expiry are CALENDAR FACTS - verdict `FACT`, shown as 'FACT' instead of a percentage and as 'a fact, not a call', no counterfactual block, no hit/miss colour, hidden from the calendar unless 'certainties & anchors' is ticked. Past nodes now: 27 HIT / 11 MISS / 2 UNFORECAST / 27 FACT (25 anchors + scotus-term-2026 + islamabad-window). OPEN QUESTION for the user: the 35 tree-promoted LEDGER rows (source tree:invariant / tree:scheduled) are scored scaffolding, already excluded from the headline Brier/hit rate; should the pure-fact ones be dropped from scoring entirely? (2) Calendar: click a bar and its whole window is highlighted - a band over every day it can happen, the bar outlined, the thin line for long windows brightened, everything else dimmed, a 'highlighted: ... window A to B [clear]' bar (click it again, 'clear' or Esc to drop it). Month, lane and the highlighted item survive page refreshes (localStorage gt-cal).

- **10/23 DROP (user: "DROP" on dropping calendar-fact ledger rows).** Read all 35 tree-promoted ledger rows (and scanned every ledger row for an "is held / convenes / opens / published" claim): NONE is a pure calendar fact - each asserts a value, threshold, comparison or decision (T-bill share > 20%, NATO members >= 2%, Swiss Re > $100B, SLOOS net tightening, Baker Hughes > 400 ...), at 0.22-0.95. So nothing was voided; the only near-fact is #56 ("midterms are HELD on schedule, but a certification fight occurs", 0.94), whose held-on-schedule leg is a fact but whose second leg is a real call. GUARD ADDED: promote_nodes.py now refuses to promote any calendar-fact node (is_fact) to a scored row; test added (236 pass). OPEN: if the user meant the 19 invariant/scheduled-class rows (0.50-0.95 value claims), say so - they are already excluded from the headline.

- **10/24 SCHEDULED STAYS, PREDETERMINED GOES (user: "anything scheduled should be there just not anything predetermined").** Of the 19 invariant/scheduled tree rows, two were already decided when logged: **#85 and #87** (>=20 / >=24 NATO allies at 2% of GDP for 2026) - NATO published the 2026 estimates (31 of 32 allies at 2%+) on 7/7, before the 10/3 promotion; both VOIDED with that reason. The other 17 rest on figures not yet public (month-ends, year-end totals, 2027 releases) and stay scored. #80 (no NPT withdrawal effective by 1/1) became decidable once no Article X notice could take effect, but no source after May confirms the absence of a notice, so it stays open to its 1/1 horizon. GUARD: promote_nodes.py now requires `first_publication` (the date the deciding figure is first public) and refuses one on or before today; doctrine 16.22; 237 tests pass.

- **10/25 DEEP RESEARCH + CORRECTIONS + DESK DATA (user: "full analysis ... tell as story about the geopolitical game", then "use heatmaps data", "apply corrections", "we have a lot more in the trading bot file").** Report: `reports/Stock market geopolitical game.md` (8 researcher notes in `research_notes/Stock market geopolitical game/`). Corrections applied by `tools/corrections_20261025.py` (backups `.bak-20261025T111026Z`): ECB 10/29 hike 0.30->0.05, ECB Dec hold 0.55->0.45, BoJ Dec hike 0.45->0.50 (+ledger #104), OPEC+ quotas unchanged 11/1 0.55->0.70, Fed hiked by 12/9 0.68->0.72; opec-nov-meeting relabelled (core group, UAE out since 5/1); new scheduled node opec-ministerial-nov29; ev-busan-truce-rolled reworded to "extended beyond 1/10/2027"; constraint_calendar re-sourced (us-energy-price-oct now `inferred`; Reuters 10/20 -> WaPo 10/18). Outlook section 11 appended; prereg claims untouched. **BRENT CONTRACT ROLL (lesson):** BZ=F rolled to January Brent on 10/23 (111.70) while December, the ICE front month to 10/30, settled 116.72; the "stale print" read was wrong. `tools/tripwire.py` now honours `front_months` in data/autoresolve.json (#83 reads BZZ26.NYM to 10/30; tests/test_tripwire.py). #83 confirmed 0.25. Desk data (no credits, cached files only): Skylit heatmaps per expiry (SPY net -702M, King 755, flip 754.09; NDX Nov King 29,675 neg, Dec 30,000 pos growing, new Feb 27,000 neg on 10/22), Skylit vol curves (NDXP inverted 27.8/25.0/21.9, SPXW upward 19.6/20.5/21.2), Tempest 500 (84% backwardation, median IV pct 70), Alpaca skew 154 names (AI-edge names -20..-56% 1m vs SPY -1%). Readers: `python tools/desk_heatmaps.py now|monthly` and `python tools/desk_positioning.py` (read Trading Bot cached files only).
