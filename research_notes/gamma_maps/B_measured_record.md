# B. The measured record of gamma-map / heatmap reading rules

Compiled 18 Nov 2026, read-only, from the user's Trading Bot project (`TB` below = `C:\Users\hudso\Downloads\Trading Bot`)
and GT-Analyst (`GT` = `C:\Users\hudso\Downloads\GT-Analyst`). Every number is copied from the cited file, except the
morning-band halves, which were recomputed on 18 Nov from `GT\data\market_update\history_spxw.json` with the same
definition as `GT\tools\market_update\stats.py:95-124` (script: `scratchpad\gamma_research\band_check.py`).

Scope: claims about what a dealer-gamma (or vanna / charm) map says about future PRICE behaviour, plus the definitional
checks those claims rest on. The options-bot P&L tests (Scooby / Velma / Fred / Shaggy engines) are listed separately in
table F, because they score option P&L of one bot's entries, not price behaviour at a level.

Status vocabulary used here:
- **validated**: measured on our data, survived its control (and, for forecast claims, out of sample).
- **lead / in-sample only**: beat its control in-sample or on one split; not pre-registered, or not replicated out of sample.
- **null**: tested against a control, no effect as large as claimed (CIs span zero). Not "proven false": small effects are undetectable at these n.
- **failed**: tested and lost against its control or its pre-registered bar (includes "falsified" and "contradicted").
- **untested**: no test found in any registry.

Sources are cited as `file:line`. `TB\knowledge\HEATMAP_DOCTRINE.md` is abbreviated `HD`; `TB\tradingview\_skylit\study\RESULTS.md`
`R55`; `RESULTS_spxw.md` `RS`; `TB\knowledge\TEST_REGISTRY.jsonl` `TR`; `TB\knowledge\SKYLIT_RULEBOOK.md` `RB`;
`TB\brain\Research\<x>.md` `BR:<x>`.

Two corrections to the figures quoted in the brief, both visible in the sources:
1. The "largest-strike pin null, n = 165" is 165 readings (15:00, 15:30 and 15:45 King on each of 55 days), not 165
   independent days (`RS:59`). The day count is 55.
2. The "gamma sign: no next-day separation over 324 sessions" table is the four-state table on **305** sessions with a
   measured vanna sign (95 + 88 + 64 + 58); 324 is the gamma-only sample (`TB\knowledge\GEX_VEX_STATES.md:34-44`).

---

## A. Index intraday maps (SPY, QQQ, SPXW 0DTE, SPX monthly): what nodes do to price

| Rule / claim | Test design | Result (n, hit rate vs baseline) | Status | Source |
|---|---|---|---|---|
| **King (largest node) is a magnet** (price drawn to it within 30 min) | 55 days 15 Jul-30 Sep 2026, 1-s maps, pre-registered, day-block bootstrap; controls: mirror level, wrong-day King | King-minus-mirror shrink at 30 min +0.13 / -0.06 / -0.21 pad (SPX monthly / SPY / QQQ), all CIs span 0; P(closer) 48.3% / 41.1% / 39.7% on n = 19,088 / 19,539 / 19,559 decision minutes (overlapping) | null | `R55:16,33-35`; `HD:110` |
| **King pins the 0DTE close** | 0DTE SPXW, 15-min grid, 55 days, pre-registered; mirror level and wrong-day King controls | Close nearer the King than the mirror 46.7% of 165 readings on 55 days; King-minus-mirror -0.02 pad [-0.49, +0.48]; mean distance to King at close 11.0 pts | null | `RS:19,59`; `HD:119` |
| **King drives price off early, pins late** | Same 55-day 1-s set; early 09:35-11:00 vs late 14:30-15:50 | late-minus-early ns on all three; QQQ moves AWAY from the King both early (-0.61 pad at 15 min, CI excludes 0) and into the close (-0.73, CI excludes 0) | null (QQQ leans contradicted) | `R55:17,41-48`; `HD:111` |
| **First tap of a big node (>= 25% of King) deflects ~80%; later taps decay (80/66/33)** | 55 days, 1-s path; reversal barrier symmetric about strike; controls: any strike with same geometry (clock-matched), LOW (< 10%) nodes, wrong-day nodes | HIGH tap-1 reversal 71.4% (n 49) SPX monthly, 72.7% (176) SPY, 69.9% (193) QQQ vs any strike 72.9% (1,529) / 76.1% (825) / 72.4% (1,727); differences -0.6 / -2.6 / -1.8 pp, CIs span 0. Taps 3+ reverse MORE (76.0% / 79.1% / 75.1%) | null; the "80%" is geometry (~75% base) | `R55:18,64-72`; `R55:148-149` (caveat 7); `HD:112` |
| Same, on 0DTE SPXW | 15-min grid, map <= 15 min old, 52-55 days | HIGH tap-1 68.8% [60.5, 76.9] (n 176, 52 d) vs any strike 72.7% (1,465), clock-matched 71.8%: -3.0 pp [-9.8, +3.9]; tap 3+ 77.2% (329); decay -8.5 pp [-18.7, +1.6] (wrong way); map <= 5 min old -2.9 pp (n 69) | null | `RS:22,123-139` |
| **Deflection lockbox** (9 pre-registered contrasts: big node vs nothing-strike, + vs -, tap 3+ vs 1, old vs new node, delivered vs not, regime, clean vs crowded, King after 14:30, growing vs flat) | Pre-registered DEFL, Holm thresholds, sealed lockbox 16-30 Sep 2026, 11 days, baseline 836 touches (base rate 72.2%) | 0 of 9 pass. D1 big vs nothing-strike -4.7 pp (n 500 vs 836, p 0.956, wrong sign); D5 not-delivered vs delivered +14.2 pp (n 463 vs 37, p 0.043 vs Holm 0.0125); D9 growing vs flat -1.4 pp (n 110 vs 195) | failed | `TR:22-23` |
| **Yellow (+) nodes deflect, purple (-) nodes run** | 55-day 1-s set + 0DTE SPXW | + minus - +7.4 / +4.4 / +0.7 pp (SPX monthly / SPY / QQQ, ns); 0DTE SPXW -1.5 pp [-8.2, +5.7] (n 375 / 322) | null (SPY lead did not replicate) | `R55:70-72`; `RS:126,138`; `HD:113` |
| **Nearest node ahead: size / sign decides whether price reaches it or goes through** | 503,816 states, 324 sessions Mar 2025-Nov 2026, SPY + QQQ, all four books on the ETF axis; descriptive, no control | P(reach within 60 min) 0.717 (fuel 10-25%, n 78,503) down to 0.654 (positive King 90%+, n 57,789); P(goes through and holds) 0.25-0.27 in every size bucket; reach is set by distance (< 1 pt: ~0.66-0.72; 1-2 pts: 0.41-0.57) | descriptive: size and sign change almost nothing; distance dominates | `BR:matrix_exit_20261108:18-31` |
| **"The run stopped at a node"** (winners' extremes sit on nodes) | 162 green bot trades; control = random minute same symbol and day | best price within 0.5 of a strong node 100% (0.25: 88%) vs random minute 98% (0.25: 84%) | null (strike-grid geometry) | `TB\knowledge\RULES_REGISTRY.md:177` |
| **Gatekeeper tap** (first tap of a >= 70%-of-King node) | 93-session corpus, 5 controls | lift +8.4, then precision 0.1558 vs time-of-day-matched 0.2784, frequency-matched 0.2240, wrong-session 0.1735, shuffled 0.1575 | failed | `RB:852` |
| **King tap** (tap the largest-|GEX| strike and deflect) | Corpus, clock-matched base rate, +12 bar | lift +4.7 to +6.5 vs +12 bar (read +16.8 against the pooled base, which would have wrongly promoted it) | failed | `RB:851` |
| **Big negative nodes 0.15-2% away pull price to them** | 133 days, 15-min reads 09:45-14:45, SPY 2,754 / QQQ 2,753 reads; pull = P(touch node in 60 min) - P(touch mirror) | 15 scored cells, 0 leads (0.8 expected by chance); e.g. size >= 0.5x King, near band, both books: touch 19% vs mirror 19% (n 1,499) | null | `BR:negnode_20261028:15-41` |
| **Opening move toward a far untouched negative King** | Pre-registered; signal days vs all other days, shuffle p | e.g. "either book, UP": 38 days, close toward 55% vs control 54%, shuffle p 0.239; all 6 cells FAIL | failed | `BR:openking_20261028:16-21` |
| **Node sign flip marks a turning level** (neg->pos catches price, pos->neg removes support) | 31,488 flips, 35 days (Sep 15-s maps + Oct minute frames) + 55-day SPXW grid; distance-matched random prices at the same moment; 25,158 threshold cells, BH; dev/holdout split | neg->pos reversal 58.4% vs random 58.2% (n 1,041); at >= 15% of King 53.1% vs 53.6% (n 286); 0 BH discoveries; 9 of 11 dev picks collapsed on holdout; the user's literal rule -0.19 R/trade, n 194 | failed | `BR:nodeflip_20261020:24-31` |
| **The user's own map-change triggers** (King roll -> fade old King, node growth / flip at price, cross-book confluence) | Codified from 7 hindsight-picked winning trades; run blind on 17 held-out September days; controls random entry, price-only, sign-flip | all four rules FAIL: avg R -0.03 to +0.07, every CI spans 0; conditions fire ~28 times per book per day; -0.12 R over 69 trades on the trained days; v2 with tolerance stops: win 31% -> ~43%, avg R ~0 -> +0.05, nothing passes | failed | `TB\knowledge\INTERPRETATION_AUDIT_20261004.md:55-66` |
| **Fade a fresh session extreme with a node at it** (pattern of the user's 22 proposals) | Descriptive only (all 22 chosen with outcome visible, 20 of 22 positive) | proposed as a blind test with random-extreme and sign-flip controls; no result found | untested | `TB\knowledge\PROPOSAL_PATTERNS_20261004.md:31-34` |
| **Ceiling rolls down / floor rolls up -> next-30-min direction** (2 rolls = signal) | 55-day 1-s set; shuffled-timing control; SPXW grid for the two-step form | directional return minus shuffle +0.23 / +0.20 / +0.03 bps (n 382 / 540 / 894 events), all ns; the roll follows a prior 15-min move of +8.4 to +10.3 bps the same way. SPXW two-step: 8 events on 8 days (untestable); one-step leans opposite, -1.76 bps [-3.74, +0.19] (n 165) | null (map follows price) | `R55:20,105-107`; `RS:21,100-101`; `HD:115` |
| **"Nodes rolling" / "growth above price" confirm a trend call** | Every live price-rule trend call; dev Apr-Oct 2026, holdout Oct 2025-Apr 2026, confirm Mar-May 2025; bar: keep >= 70% of trends, cut >= 30% of pops | Rolling true on 100 / 100 / 97% of trend calls and 3 / 0 / 1% of pops cut (fires on every call); best lead D1 (same strikes built >= 1.5x in 30 min) kept only 66% in Apr-Jul | failed | `BR:poptrend_20261106:14-30` |
| **Map "reshuffle" against price marks bad entries** | 1,622 bot trades, 139 days; pre-registered | trades against a map walking with price were BETTER (R20: median peak +95% vs +86%, n 211) | failed | `BR:reshuffle_20261107:18-22` |
| **Slip-in node (born at spot) supports / caps price** | 55-day 1-s set; same-day and other-day controls | direction +0.29 / +0.50 bps (SPY n 102, QQQ n 192), ns; QQQ 15-min range -6.9% (CI excl. 0), plausibly reverse causation; SPX 3 events | null (direction) | `R55:21,123-124`; `HD:116` |
| **Node "pop" (fresh node at price) beats an established node** | 321 days Mar 2025-Nov 2026, train/test split; bar: both halves | all 4 cells FAIL, plus pop+established, surge (>= 1.5x in 2 min) and small-quiet addenda: all FAIL. E.g. + node floor: POP median peak +1.50 pts (n 517 test) vs established +1.23 (n 2,856) but stop-first not better | failed | `BR:nodepop_20261106:39-43,89-120,175-179` |
| **Stubborn node (>= 0.5x King most of the day): price returns after leaving it** | 12,433 leave events, 150 days Apr-Nov 2026; pre-registered | back within 120 min: stubborn 53% (n 1,281) vs strong-now 73% (n 2,832) vs any 62% (8,320); -19 pts vs bar +10 | failed | `BR:stubborn_revert_20261107:24-35` |
| **Stubborn node sets the MOC (close) direction** | 135 days, SPY/QQQ 0DTE, 15:50 -> close; pre-registered; controls big-but-not-all-day, 14:50 window | toward the node 53% (n 79, p 0.65) vs control 51% (n 162); stubborn King 59% (n 44, p 0.29) | null | `BR:stubborn_moc_20261028:16-37` |
| **Which way a King pin breaks** (8 map reads) | 273 pin episodes (SPY 168, QQQ 105), 133 days, 121 broke; 1,000-shuffle p; bar: gap >= 12 pts both halves, p <= 0.05 | 0 pass. G3 nearest big negative node side +24 pts, p 0.062 (n 42 / 32). G4 "where nodes grew" points the WRONG way: -26 pts, p 0.009, both halves (n 67 / 54) = reverse lead | null (one reverse lead) | `BR:pinbreak_20261028:18-27` |
| **Pin day read from the map at 10:30** | 108 days, 463 trades; tiered exits on pin days | PIN-G -$32,755, 1 of 7 months positive, p 0.835 | failed | `BR:pinmap_20261023:20-25` |
| **Post-14:00 charm / vanna pin rejection** | 93-session corpus, 5 controls | lift +9.3; precision 0.1186 vs frequency-matched 0.2284, TOD-matched 0.1537, shuffled 0.1098 | failed | `RB:857` |
| **Negative King beach-balls** (overshoot and reclaim) | 338 tests of negative Kings; random-timing pseudo-levels; 4,434 entry rules, BH | HOLD 41% / BEACH BALL 18% / FAIL 17% / NONE 25% vs random 38 / 18 / 20 / 23%; 0 of 4,434 rules pass BH; positive gamma beyond the King lowers break-through (pos5 AUC 0.40 [0.32, 0.48], BH q 0.20) | failed (pos5 a lead, sign consistent both halves) | `BR:beachball_20261020:24-37` |
| **Trinity agreement (2 or 3 of SPX / SPY / QQQ maps)** | 55-day set and SPXW grid | 2-of-3 +3.1 pp [-9, +15]; SPXW 3-of-3 75.2% (n 298) vs 1-of-3 69.8% (n 86): +5.3 pp [-3.4, +17.6]; touches with no node anywhere reverse most (77.7%). Corpus: 3-of-3 lowers precision (0.2148 -> 0.1765); SPX and SPY ~0.999 correlated so 94% of plays read 3/3 | null; as a filter failed | `RS:23,156`; `HD:121,280`; `RB:865-866` |
| **Growing vs fading node ("tug of war")** | 55-day set | +6.5 pp SPY / +8.4 pp QQQ, CIs +-20 pp, fading arm n 29 | null, leans doctrine way (forward candidate, never run) | `HD:281` |
| **Gamma flip crossed and failed -> reversal** | Corpus, 597-1,287 signals | +0.3 to +0.9 pts vs +12 bar | failed | `RB:853`; `HD:117` |
| **Gatekeeper break -> acceleration** vs beach-ball reversion | none | listed as open question 4 | untested | `HD:298,337` |
| **Rug / reverse rug as a pattern** | none as price pattern (bot vote variants only, table F) | sources conflict on meaning | untested as price behaviour | `HD:300-301` |
| **Air pocket + velocity -> fastest moves** | velocity backfill 10 sessions | after a velocity spike, next 30 min moved 1.19x an average minute; where activity sat called direction 49% | null (direction); size lead only, n tiny | `TB\knowledge\RULES_REGISTRY.md:198`; `HD:306` |
| **Static 09:30 map vs live evolving map** | 19 days in-sample, engine P&L | live +367.1 vs static +47.5 (evolution 87%); the engine itself failed out of sample (+0.24 R/day, t 0.80, 119 sessions) | validated only as a comparison; no absolute edge | `HD:118`; `TB\knowledge\GAMMA_TRADING_SHEET.md:65-66` |
| **Positioning carries information not in price** (positioning-only sequence model) | Shifted-positioning control (other session's ladders on this tape); 5 folds inside a 133-session pool | edge collapses with shifted maps (retains 4% HIGH / 37% LOW of edge over chance) but mean fold lift +8.24 / +10.60 vs +12 bar; LOW AUC < 0.5 in 2 of 5 folds; no OOS number | lead / in-sample only (the project's only mechanism evidence) | `RB:874-900` |
| Direction model on 8 positioning features | Folds, pre-registered decay rule | AUC 0.63-0.82 stable but the predicted SIDE rotates across folds; first headline was a leak | failed | `RB:859` |

## B. Index regime, vol, vanna and charm

| Rule / claim | Test design | Result | Status | Source |
|---|---|---|---|---|
| **Negative net gamma = bigger ranges / trend; positive = chop** (intraday, next 60 min) | 55-day 1-s set; within-day and wrong-day controls | range ratio neg/pos 1.28 [1.05, 1.52] SPX monthly, 0.96 [0.79, 1.16] SPY, 0.80 [0.67, 0.96] QQQ (opposite sign); within-day versions ~1 | null (inconsistent sign) | `R55:19,85-87`; `HD:114` |
| Same, 0DTE SPXW | 15-min grid; 834 pos / 359 neg readings, 30 days with negative | 1.09 [0.90, 1.35]; within-day +0.14 log [-0.06, +0.39] on 16 days | null, leans doctrine way (the one open forward candidate; needs ~150+ days) | `RS:20,82`; `HD:331-333` |
| **Gamma sign at 09:35 -> next-day direction** (and the GEX x VEX four states: melt-up, gap-and-go, calm-fades-fail, violent bounce) | SPY net gamma and vanna within 2% of spot; 305 sessions with both signs (324 gamma only); medians, no formal test | next-day SPY median -0.01% / +0.07% / +0.16% / +0.04%, up 49% / 53% / 53% / 55% (n 95 / 88 / 64 / 58) | null (directional claims fail) | `TB\knowledge\GEX_VEX_STATES.md:34-47` |
| Gamma sign as a same-day label for the bot's fade quality | Both halves | +GEX better in Apr-Jul (peak 101% vs 75%), REVERSED in Aug-Nov (83% vs 96%) | failed (flips by half) | `GEX_VEX_STATES.md:58`; `TR:44` |
| **Prior day's largest node positive -> next-day fade quality** | Daily dominant-node label (true 30% of days); both halves | next-day bot median peak 107% vs 70% (H1), 82% vs 42% (H2); never ran 11% vs 17-22%; money separates in H1 only; not replayed; quality label, not direction | lead / in-sample only | `GEX_VEX_STATES.md:59`; `TR:44` |
| **Vanna features (sign, above/below sums, King sign, pull, rugs, alignment)** | 14 features x SPY/QQQ x summed/0DTE = 42 splits; both-halves bar; 300 shuffled-label null; permutation per lead | 12 of 42 pass vs 12.6 expected by chance. Two survive permutation: SPY 0DTE vanna-King sign + (peak 122% vs 62%, p 0.000), QQQ summed top-5 pull + (106% vs 55%, p 0.003); neither transfers across book or column; calls and puts improve together (day-quality, not direction) | null as a family; 2 non-directional leads | `GEX_VEX_STATES.md:60-68`; `TR:45` |
| Vanna adds to gamma inside a gamma cell | 305 days | adds nothing | failed | `GEX_VEX_STATES.md:49,68`; `TR:44` |
| Old daily vanna proxy = real vanna sign | Overlap days | agreement 49% (later 51%) = coin flip | failed (proxy invalid) | `GEX_VEX_STATES.md:36,59` |
| **OPEX-week charm flow (NDXP 3-6 DTE, 17:30 map) -> 5-session NQ direction** | In-sample 2024-01-16..2026-10-23, random-day control; then a SEALED forward test pre-registered 27 Oct 2026, 250 sessions (~57 swings, to ~Oct 2027) | in-sample 160 swings, PF 1.44, p 0.029 vs random-day legs, both halves positive; spot input flipped the charm sign on 23 of 159 days in the original research (PF 1.71 version) | lead / in-sample only; forward test running | `BR:swing_fwd_20261027:14-35`; `TB\brain\Standings.md:132` |
| **QQQ 5-day fade in negative gamma (MR5g)** | 142 swings, hold 5, 1-ATR stop, control mean | mean +$113 vs control +$7 per swing, p 0.07; 83% of the total from the 14 swings through a quarterly expiry week; without the stop p 0.25 | lead / in-sample only (concentrated) | `BR:mr5g_recheck_20261027:14-45` |
| Premarket -> open gamma shift predicts the day | 8 sessions, then 63 sessions | 62% match, corr +0.36 (8 sessions); +0.21 after removing price, p ~0.1 (63 sessions) | lead / in-sample only | `RULES_REGISTRY.md:194,212` |
| Trend-day predictors (incl. evening map, gap, VIX, breadth, opening drive) | 881 sessions, out of sample | AUC 0.44-0.61 | failed | `RULES_REGISTRY.md:212` |
| Regime reads (dealer gamma among 5) as a bot gate | 424 trades, random-skip control | 0 of 9 pass | failed | `TB\brain\Standings.md:221`; `BR:regime_20261022:12-30` |
| **Morning band: SPX closes between the largest + 0DTE strikes either side of the 09:30 open (within 1.5%)** | 260 sessions 24 Oct 2025-17 Nov 2026; control = mirror band (same width reflected through the open); day-block bootstrap; NOT pre-registered | 136 / 260 = 52.3% inside vs mirror 114 / 260 = 43.8%; gap CI +1.9 to +15.0 pts. Halves (recomputed): H1 (to 8 May 2026) 74/130 = 56.9% vs 46.2%, CI +1.5 to +20.0; H2 62/130 = 47.7% vs 41.5%, CI -2.3 to +14.6. Median band width 0.88% of the open. First live scored statement (17 Nov): close below the band (miss) | lead / in-sample only (SHADOW); H2 alone not significant | `GT\.claude\skills\market-update\SKILL.md:119-128`; `GT\data\market_update\scorecard.csv:2`; recomputed |
| **Next close inside the options-priced 1-day move** | SPX close-to-close vs implied 1-day move; unconditional and by 30-day IV bucket | 73% inside, n 419 (some days use a scaled svx1d proxy, median ratio ~0.062) | validated as a descriptive base rate (not a gamma claim) | `GT\.claude\skills\market-update\SKILL.md:129-133` |
| MOC: the close continues the day | 996 SPY sessions, contamination removed | 47.5% (the 54.9% first edition included the predicted minutes) | failed (retracted) | `TB\MOC_nodes_pattern_analysis.md:13-25` |
| Late-day momentum x prior-day SPXW King (A2) | Pre-registered, Bonferroni k = 3, lockbox sealed | c 0.0297, CI98 [-0.0421, 0.1027]; option vehicle -$16.6/trade | failed | `TR:1-2` |

## C. Overnight levels

| Rule / claim | Test design | Result | Status | Source |
|---|---|---|---|---|
| **Overnight top-5 GEX nodes are reversal levels (NQ)** | Pre-registered; placebo levels | 20 nights (14 Aug-17 Sep): 54.5% vs 49.1% placebo, +5.5 pts [+1.7, +10.0] PASS; ~370 unseen nights (Nov 2024-Sep 2026): 51.2% vs 51.1%, +0.1 [-1.3, +1.5] | failed out of sample (the only pre-registered GEX pass, did not hold) | `TB\knowledge\OVERNIGHT_LEVELS.md:17-26` |
| Same, ES; top-15 variant | Same holdout | ES 53.2% vs 52.9%; top-15 null on both | null | `OVERNIGHT_LEVELS.md:21-22` |
| **One side of the overnight range breaks ~95%** | 332 NQ sessions; random same-width range around the 09:30 open | 93.1% [90.3, 95.5] vs random 91.1%: +1.9 pp ns | true frequency, null as a level effect (geometry: RTH is wider than ON) | `HD:122,282-283` |
| "If the ON lows hold, target the highs" | Same | +5.8 pp [-1.7, +13.9] | null | `HD:284` |
| Overnight King shift (last night vs this morning >= 1.5%) as a bot block | 868 entries, 125 sessions; 9 flag days | blocking would have cut winners (10 trades, +$2,966) | failed (n tiny) | `BR:nightking_20261105:14-31` |
| Closing reads (King, tilt, net gamma, trend, skew, MAs) call a down night | TRAIN 2016-19 / VALIDATE 2020-23 / TEST 2024-26 | nothing at the close calls a down night in all regimes | failed | `BR:downnight_20261029:70` |
| How much the 0DTE book changes overnight (descriptive) | 189 real nights, SPXW / SPX / VIX books, 5 instants a night | SPXW 0DTE book value changes a median 24% from 20:30 to 08:30; the King unchanged on only 67% of nights; 62% of the change by 03:30, 79% by 06:00. SPX monthly: 5%, King unchanged 80% | descriptive (staleness fact) | `BR:nightmap_20261101:22-30` |
| Skylit's posted overnight (TDO) levels: reach rates | 727 nights 2024-26, ES / NQ; up-side mirror | ES "down" level at 0.5R reached 29% of nights (P1, n 415) vs UP mirror 31%; calibration only, the bot grid test failed | descriptive; failed as a bot grid | `BR:tdo_20261026:12-30` |

## D. Single names, earnings, expected move, multi-day horizons

| Rule / claim | Test design | Result | Status | Source |
|---|---|---|---|---|
| **Single-name map setups** (below a negative King, toward a growing negative King, flush-and-reclaim, negative both sides, MA + map) | Maps 2-28 Oct 2026, ~120-163 names/day; Fred = 30-day ATM held 5 sessions; Velma = weekly ATM intraday; control = same name and side on other days; pre-registered | 0 of 17 pass. "Toward a growing negative King": Fred median peak +16% vs control +24% (n 184), Velma +29% vs +38% (n 141). Best: S1 below a negative King on Velma +144% vs +36% (n 14, p 0.000), fails n >= 15. Only 4 weeks of maps | failed (one lead, n 14) | `BR:namesqueeze_20261028:18-48` |
| **NDX-constituent "stock walls" as NQ levels** | 64 days Aug-Nov 2026, 101 names at 09:30:30; mirror and shuffle controls; pre-registered point needed 60 touches | 23 of 60 required touches (not testable); at 0.1% / >= 3%: HELD 30% vs mirror 37% / shuffle 33%; >= 5% bucket at 0.25%: 44% vs 36 / 29% (n 36). Wall vs QQQ King when apart: King held 43-50%, wall 10-14% | failed as a level; >= 5% bucket a lead | `BR:stockwalls_20261108:16-40` |
| **Earnings: what the straddle prices vs what happens** | 2,901 earnings events with both ATM legs priced, 538 names, 2024-26 (TRAIN 2,220 / TEST 681); buy at the close before, sell 09:30-09:44 next day, costs included | median realised gap 0.61x the implied move (4.8% vs 8.2%); only 27% of reports gap beyond it; every straddle -5.1% / -7.0% per trade (train / test); no closing read calls direction (47-52%) | validated as a descriptive base rate (sell-side containment); no direction read survives | `BR:daphne_earn_20261028:16-34` |
| Earnings gamma / vanna setups (ladders mapping a beat to a level; post-event vanna rally) | none on our data; the studied archive's 3 scorable single-name earnings ladders: 1 reached day 3, 1 void, 1 miss (NVDA $200 IV-crush call) | n 3 | untested on our data | `GT\.claude\skills\technical-stack\SKILL.md:130-142,160` |
| **Single-name gamma regime -> next 5 sessions' range** | none; proposed protocol (60+ name-days, both halves) | | untested | `GT\.claude\skills\technical-stack\SKILL.md:155` |
| **Single-name largest node as close-at-expiry magnet** | none; proposed (50+ expiries vs mirror strike) | | untested | `technical-stack\SKILL.md:156` |
| **Single-name walls as multi-day support / resistance** | none | | untested | n/a |
| **Expected-move containment on single names (pre-earnings implied vs realised)** | logging protocol only (T+1 log) | earnings sample above gives 27% beyond implied over 2,901 events | untested as our own forward log; base rate exists | `technical-stack\SKILL.md:154,237-238` |
| Single-name vanna / charm | no single-name vanna or charm data in GT; universe vanna files exist only for a 16:00 batch | | untested | `technical-stack\SKILL.md:86,157`; `GT\.claude\skills\market-update\SKILL.md:67` |
| Trend / 52-week / RS context (prices_5y, 6 names, n 348 overlapping 63-day windows) | In-sample, no shuffled null, one regime | above 200-day: median +2.2% vs SMH, 56% beat (n 244) vs -2.4%, 46% (n 104); RS > 0: +3.4%, 59% (n 176) vs -1.9%, 47% (n 172); 52-week distance no separation; RV20 -> next RV20 corr 0.51 | lead (RV persistence adopted for vol-state context only) | `technical-stack\SKILL.md:118-128` |
| The archive's single-name touch-level calls, re-scored on our closes | 7 statements | 1 clean hit, 2 late partials, 3 misses, 1 void | failed (as targets), n 7 | `technical-stack\SKILL.md:130-142` |

## E. Definitions and computations (validated as computations, not as edges)

| Item | Check | Result | Status | Source |
|---|---|---|---|---|
| Net GEX formula, $ per 1% move | Formula + academic basis | `(gamma_call*OI_call - gamma_put*OI_put)*100*S^2*0.01`, dealer long calls / short puts by convention | validated as computation; dealer side is an assumption | `RB:101-104` |
| Flip by re-pricing total gamma at 81 candidate spots | Code check | validated method; Skylit does not display a flip, ours is computed | validated | `RB:106-108`; `GAMMA_TRADING_SHEET.md:53` |
| Vanna = vanna, not vega; greek math | Hand Black-Scholes to 6 dp; one SPY cell (735 / 06-22) $1.789B vs user grid $1.815B | ~1% match, one cell | validated (magnitude, one cell) | `RB:110-120` |
| Walls side-restricted (call wall above spot, put wall below) | Bug fixed, verified | walls bracket price | validated | `RB:128-131` |
| Skylit intraday ladder is flow-driven (cumulative volume x gamma), not OI | 19 days, alignment with Skylit | OI weight 1.0 -> 2.44/5 top-5 alignment; weight 0 -> 3.29/5 | validated (what the vendor map measures) | `RB:139-146` |
| 0DTE map vs all-expiry map are different objects | Top-5 overlap | pooled 0.81/5, SPXW 0.00/5 | validated | `RB:148-151` |
| SPXW map is not SPY x 10 | 55 days | King match within 5 pts 18.4% vs 19.6% wrong-day baseline | validated (distinct books) | `RS:18,35` |
| Vendor substitution (the excluded vendor for Skylit) | 19 hand-walked days | top-5 strike overlap 1.46/5 | failed (do not substitute) | `RB:325` |

## F. Map reads tested as options-bot rules (P&L of one bot's entries; in-sample replays unless stated)

These are not price-behaviour tests; listed so the guide does not mistake them for evidence either way.

| Read | Result | Status | Source |
|---|---|---|---|
| Node in the way to target (positive >= 35% of King within $2) -> skip | -$309,458; throws out half the 10x runners ("big moves run through those nodes") | failed | `BR:mapthree_20261107:21-30` |
| King roll against the trade -> break-even or sell | -$10,587 / -$230,783 | failed | `BR:mapthree_20261107:25-26` |
| Both other Kings against -> skip | marks the bot's best bucket (avg +$399, median peak +101%) | failed | `BR:mapthree_20261107:27,35-37` |
| Entries into a negative-gamma pocket -> skip | skipped trades were not worse (P2: +$139,600 skipped) | failed | `BR:negpocket_20261028:20-25` |
| Tap-count reset on node growth | all 4 arms FAIL (-$7.7k to -$11.0k) | failed | `BR:tapgrow_20261106:10-16` |
| Strong-node 25% threshold removed | FAIL | failed | `BR:weaknode_20261028:82-84` |
| King path (weak node with an untouched King behind) | FAIL | failed | `BR:kingpath_20261110:44` |
| Coil breakout toward the nearest untouched negative King | C3 median peak +73% vs control +53% (224 trades, 64 days, p 0.001); C4 +79% vs +51% (102 trades, p 0.006); 133 days, static, in-sample | lead / in-sample only | `BR:coil_20261028:24-25` |
| Pin vote + lean entry | 23 trades, PASS; post-hoc, 1 pass in 10 looks | lead / in-sample only | `BR:pinlean_20261031:26,45,95-96` |
| Near-touch of the King in the first 30 min | descriptive, no control verdict (NEAR-TURN median peak +85%, n 297) | lead / descriptive | `BR:neartouch_20261113:22-25` |
| 09:35 SPXW gamma-centre entry | right side 57.9% of 57, halves 45% / 71%, shuffle p 0.19 | failed | `BR:centroid0935_20261113:19-26` |
| 3:1 R:R gate, 80/66/33 tap gate, clean-path, dominance (283 sessions) | -0.033 / -0.067 / no-op / -0.078 R/day; all four together 11 plays | failed | `RB:837-840`; `HD:117` |
| Forward shadows FWD-ODTE (tap fade + afternoon King pull), FWD-REV, FWD-FW3N | Pre-registered 1-2 Oct 2026; no scored forward result found in the registry or brain notes | untested (result not located) | `TR:3-19` |

---

## What is solidly established

1. **Nodes are not special levels for intraday index price.** Across four books, 55 days of 1-second maps and a
   0DTE SPXW grid, big nodes deflect at the same rate as any strike with the same geometry: ~68.8-73% at big nodes vs
   ~72-76% at any strike (`R55:64-66`, `RS:123-128`). The doctrine's "80% first tap" is the ~75% random-walk barrier
   base rate (`R55:148-149`). The pre-registered lockbox went 0 of 9 (`TR:23`). The 503,816-state record shows the
   nearest node is reached ~65-72% of the time within 60 minutes whatever its size or sign, and is gone through ~25%
   of the time in every bucket (`BR:matrix_exit_20261108:18-31`).
2. **The map follows price.** Rolls appear after an 8-10 bps move the same way (`R55:105-107`); "rolling" is true on
   nearly every trend call and every pop alike (`BR:poptrend_20261106:24-30`).
3. **The King does not pin the close** (0DTE SPXW 46.7% vs mirror over 165 readings on 55 days, `RS:59`) and is not a
   magnet in the 30-minute window (`R55:33-35`).
4. **Gamma sign does not forecast next-day direction** (four-state medians -0.01% to +0.16%, up 49-55%, 305 sessions,
   `GEX_VEX_STATES.md:39-47`), and its sign for intraday range is inconsistent across books (1.28 / 0.96 / 0.80, `R55:85-87`).
5. **Options over-price earnings moves on average.** Over 2,901 events the median realised gap was 0.61x the implied
   move; 27% exceeded it (`BR:daphne_earn_20261028:20-21`). For the index, 73% of next closes landed inside the priced
   1-day move (n 419, `market-update\SKILL.md:129`).
6. **The computations are right** (GEX, flip by re-pricing, vanna not vega, side-restricted walls), and the vendor map
   is flow-driven, front-expiry specific, and not interchangeable with another vendor or with the all-expiry map (table E).
7. **Overnight books move a lot**: the SPXW 0DTE book value changes a median 24% overnight and the King changes on a
   third of nights (`BR:nightmap_20261101:27`), so an evening map is a different object by the open.

## What is null (tested, no effect as large as claimed; small effects not excluded)

King magnet and early-drive-off / late-pin; first-tap deflection and tap decay; yellow-vs-purple; negative gamma =
bigger range (SPY / QQQ / SPX monthly; 0DTE SPXW 1.09 leans the doctrine way); roll-down / roll-up direction; slip-in
direction; Trinity agreement; growing-vs-fading (leans doctrine way, n 29 fading); big negative nodes pulling price;
stubborn node into the MOC; pin-break direction from 8 map reads; overnight ON-range break as a level effect;
overnight ES nodes. Power caveat stated by the study itself: day-bootstrap CIs are about +-6 pp (SPY / QQQ) and
+-11 pp (SPX) at a tap, so an effect under ~5 pp would not be seen (`R55:134-136`).

## What failed (lost against its control or its pre-registered bar)

The deflection lockbox (0 of 9); gatekeeper tap and King tap on clock-matched controls; flip-cross / flip-fail
(+0.3 to +0.9 pts vs +12); node sign flips as levels (31,488 flips, 0 BH discoveries, the user's rule -0.19 R on 194);
the user's map-change triggers run blind (17 held-out days); post-14:00 charm / vanna pin rejection; negative-King beach
ball (18% of 338 tests, same as random levels); stubborn-node reversion (53% vs 73%); node pop vs established; reshuffle;
opening move toward a far negative King; pin day from the map; the overnight top-5 node rule out of sample (51.2% vs 51.1%
on ~370 nights after a 20-night pass); the GEX x VEX four-state direction calls; gamma sign as a same-day label (flips
by half); vanna as a family (12 of 42 vs 12.6 by chance); the daily vanna proxy (49% agreement); single-name map
setups (0 of 17); stock walls as NQ levels; Fibonacci from the open (51% vs 55% shuffled, `TR:43`); trend-day
predictors (AUC 0.44-0.61 on 881 sessions); the doctrine's 3:1 and tap-count gates on 283 sessions; the lean vote
(reads backwards on single names, `RULES_REGISTRY.md:69`); vendor substitution.

## What was never tested (or only by a tiny or non-independent sample)

- **Single names over days or weeks.** No test of single-name regime -> multi-day range, the largest node as a
  close-at-expiry magnet, walls as multi-day support / resistance, or call / put walls on weekly or monthly expiries.
  The only single-name map test covers 4 weeks (2-28 Oct 2026) and option P&L, not price at levels
  (`BR:namesqueeze_20261028:18`). Single-name maps exist only where the levels process pulled them (`technical-stack\SKILL.md:85`).
- **Earnings and the map.** No test of whether a pre-report gamma or vanna map says anything about the post-report
  move or its direction; no single-name post-event vanna ("IV-crush rally") test. The earnings evidence is about the
  implied move only (straddle containment), not the map.
- **Single-name vanna and charm.** No data in GT; universe vanna files only from a 16:00 batch; the registry's vanna
  work is SPY / QQQ only.
- **Index charm into the close** as a measured effect (charm maps are a gap in our data, `market-update\SKILL.md:71`);
  only the corpus pm-pin rule (failed) and the OPEX-week multi-day charm swing (in-sample lead, forward test running).
- **Overnight, beyond the NQ/ES node rule:** no test of the evening (17:30) map's walls or King against the next
  session's open or close; no test of overnight VIX-map reads.
- **Gatekeeper break -> acceleration vs reversion**, rugs as price patterns, air-pocket speed with a control, and the
  user's "fresh extreme + node" fade (designed, never run).
- **Index walls / King over multi-day horizons** (weekly or OPEX expiries as weekly magnets); every index test is intraday
  or next-day.
- **0DTE SPXW at 1-second resolution** (the SPXW tests use a 15-minute grid, maps up to 15 min old; `HD:342-343`).
- **The morning band out of sample** (not pre-registered; 2027 sessions proposed, `market-update\SKILL.md:127-128`).
- **Forward shadows** registered 1-2 Oct 2026 (FWD-ODTE tap fade + afternoon King pull, FWD-REV, FWD-FW3N): no scored
  result located.

## Known data caveats

1. **Vendor normalisation unknown.** Skylit dealer positioning is "derived, not exchange-reported", method unpublished
   (`HD:57-59`); the intraday ladder is volume-driven, not OI (`RB:139-146`). The "$ per 1% move" scale is uniform only
   within a ticker; cross-ticker ratios (an SPX King vs a QQQ King, or a stock wall vs an index King) are unverified
   (`GAMMA_TRADING_SHEET.md:119,171`). Skylit's own docs call the playbooks "habits, not proof" and its only published
   study found no reliable price-direction edge (`HD:128-131`).
2. **Dealer side is an assumption.** Our GEX assumes dealers long call OI / short put OI (`RB:101-102`); Skylit infers
   side by an unpublished method. On the "% of King" view, the sign of a row against a NEGATIVE King is undefined on
   disk (`GAMMA_TRADING_SHEET.md:149`), and colour is not sign on the default palette (`HD:74-79`).
3. **Vanna sign convention unverified against Skylit's files.** Our vanna math matches Black-Scholes and one SPY cell to
   ~1% in magnitude (`RB:110-120`); the dealer sign for vanna inherits the call/put convention above; the four-state
   "long vanna buys when vol drops" reading comes from a third-party chart, status REFERENCE (`GEX_VEX_STATES.md:3-5`);
   Skylit's vanna `value` is a 5-expiration sum while the 0DTE column gave different answers (`GEX_VEX_STATES.md:67`).
4. **Snapshot timing.** The 55-day SPXW tests use a 15-minute grid (maps up to 15 min old); the GEX x VEX vanna sign mixes
   62 event-sampled matrices with one 09:35 matrix a day (`GEX_VEX_STATES.md:35-36`); the overnight node rule used a
   frozen evening map that is stale by the open (`OVERNIGHT_LEVELS.md:98-106`), and the 0DTE book changes ~24%
   overnight; pre-earnings single-name maps are EVENT-STALE from the release. The morning band is scored on the 16:00 map
   spot sample, which differs from the official close (7,340.90 vs 7,333.89 on 17 Nov, `market-update\SKILL.md:146-147`).
5. **Off-grid and off-ladder strikes.** SPXW strikes are 5 pts apart and SPY / QQQ $1 (0.5 on SPXW scaled), so "price
   stopped at a node" happens at random minutes 98% of the time (`RULES_REGISTRY.md:177`); index nodes rescaled onto the
   ETF axis can be misplaced by 4-5 pts through the index spot glitch (`BR:bothnode_20261111:41`); Skylit ladders show
   50 strikes re-centred on spot, so a larger node off-ladder is invisible (`R55:140-141`); "% of King" displays as an
   integer, +-0.5 pt quantisation (`GAMMA_TRADING_SHEET.md:148`); the API "SPX" ladder is the MONTHLY book, so the
   55-day "SPX" results are not 0DTE (`R55:137-139`).
6. **Sample and regime.** Most map tests sit inside one rising regime (Jul-Nov 2026); SPX and SPY are ~0.999 correlated,
   so they are not independent confirmations (`R55:142-143`, `RB:865`); many bot replays are in-sample and spent the
   Apr 17-Jul 31 lockbox (`BR:blindbox` in `TB\brain\Research\_index.md:320`).
7. **Hindsight selection.** The user's own trades and proposals (7 and 22) were all picked with the outcome visible
   (`INTERPRETATION_AUDIT_20261004.md:51-53`, `PROPOSAL_PATTERNS_20261004.md:31`); practitioner recaps claim an 87% hit
   rate against their own scorecards of 3/6 and 4/6 days (`HD:225-228`).

## Recommended tests that would settle open questions

1. **Morning band, out of sample** (pre-register now, unchanged definition): 2027 sessions vs the mirror band, both
   halves, day-block bootstrap. Promote only if the gap CI excludes zero in the new sample; H2 of the existing sample
   already spans zero (47.7% vs 41.5%, CI -2.3 to +14.6).
2. **Single-name regime -> range** on end-of-day maps: positive vs negative net gamma within +-2% -> next-5-session
   realised range ratio, 60+ name-days, both halves, same-name shuffled-date null; state the expiry netting.
3. **Single-name largest node at expiry**: close-at-expiry distance to the largest node vs a mirror strike and a
   random same-moneyness strike, 50+ expiries, weekly and monthly separately; report node size and distance buckets
   (the index record says distance, not size, drives reach).
4. **Single-name walls over 1-10 sessions**: touch-and-hold rate of the call / put wall vs the mirror level and a
   shuffled-date wall, pre-registered n >= 60 touches (stock walls failed at 23 of 60).
5. **Earnings, map vs implied move**: on pre-report maps (last map before release), does net gamma sign or the
   largest node predict |realised| / implied or direction? Use the 2,901-event earnings set where maps exist; control
   = the straddle base rate (0.61x, 27% beyond). Separately, log our own T+1 realised vs implied for 20+ reports
   (technical-stack runbook) to confirm the containment base rate on our names.
6. **0DTE SPXW negative gamma -> next-hour range**, the one cell leaning the doctrine way (1.09 [0.90, 1.35]): ~150+
   days, ideally 1-second SPXW (removes the 15-minute map lag).
7. **Overnight evening map vs next session**: 17:30 map's King / walls vs the next 09:30 open and 16:00 close against
   mirror levels, ~250 nights, with the 24% overnight book drift recorded per night.
8. **Vanna sign audit**: compare our computed vanna sign per strike against Skylit's vanna file on overlapping days
   (both 0DTE column and 5-expiry sum) before any further vanna claim; then re-run the 2 surviving non-directional
   leads (SPY 0DTE vanna-King sign; QQQ top-5 pull) out of sample.
9. **Growing-vs-fading node (tug of war)** and **gatekeeper break vs reversion** on the same events, with the
   any-strike geometry control and day-block bootstrap; both are open, cheap, and the first leaned the doctrine way.
10. **Score the forward shadows** registered 1-2 Oct 2026 (FWD-ODTE, FWD-REV, FWD-FW3N) and report them, misses
    included; and keep the sealed OPEX-week charm swing (to ~Oct 2027) sealed.
