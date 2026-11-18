# Market-update engine: format study notes (internal)

Written 18 Nov 2026 from a study of a third-party daily index-options newsletter ("the reference letter" below).
The reference letter is for learning only. Nothing here copies its text, name, branding or watermark, and nothing
here tells anyone to trade. Our engine produces the same kind of update from our own data, under our rules (section F).

Corpus: 25 emails from the reference sender in the connected mailbox (6 Jun to 19 Oct 2026: 1 welcome, 11 morning,
10 pre-close, 1 closing-bell, 1 medium-term metals piece, 1 errata), 1 forwarded print of the 17 Nov pre-close
edition, and 9 platform digests carrying the author's short notes and post teasers (19 Sep to 14 Nov). Archive:
`Trading Bot/knowledge/substack/ddstocks_email/` (markdown per email plus `index.csv`). Twenty chart images were
sampled at full resolution for the palette and grammar below. Gap: the connected mailbox stops receiving the letter
after 19 Oct (the 17 Nov print came from a different mailbox), so 20 Oct to 16 Nov is unseen.

---

## A. Line-up and cadence

| Edition | Sent (ET) | Length | Charts | What it is for |
|---|---|---|---|---|
| Morning | 08:59-09:27, every session | 630-1,350 words (median ~850) | 7-12 (median 9) | Overnight recap, today's level map for the 0DTE book, vanna, VIX positioning, three cases and a decision tree |
| Pre-close | 15:20-15:55, every session | 320-915 words (median ~600) | 5-8 (median 6) | Score this morning's map against the day, show how tomorrow's expiry book changed, the overnight map |
| Closing bell | 16:30, occasional (1 seen) | ~860 words | 8 | Same as pre-close plus a rest-of-week view: Wed/Thu/Fri expiries summed into weekly pins |
| Friday pre-close | 15:20-15:30 | ~350-650 words | 5-6 | Next week's map: weekly expiries summed, weekly vanna |
| Event night (17 Nov) | pre-close | ~900 words | ~7 | Built around one after-hours catalyst (a mega-cap print): IV-drop routes A/B/C with VIX brackets and past-case ranges, the overnight session clock, horizon outlook |
| Errata | minutes after a morning edition | 50 words | 1-3 | A missing chart re-sent |
| Medium-term asset piece | midday, irregular | ~770 words | 8 | Metals vs dollar and bonds: RSI, betas, past-case table, options levels on the ETFs |
| Short notes (platform) | weekly-ish | 1-6 sentences | 1 chart or short video | Frequency stats (how the next day usually behaved after a similar day), a regime-state map for the Nasdaq, breadth remarks, an oversold flag on one name |
| Long posts (seen as teasers) | irregular | long | many | Tutorials on reading the levels and on short-dated options, single-name multi-month forecasts, a weekly outlook |

Each email repeats a title card image, then a one-line deck (informal, often a question), then the sections.
Sending is twice a day on every session (Mon-Fri) in October; there is no weekend edition in the corpus.

## B. Anatomy by edition

### B1. Morning edition (pre-open)
1. **Greeting and overnight recap** (80-150 words). Prior cash close and % change; overnight futures range stated
   in cash terms; where futures point now in cash; VIX now vs prior close; the dollar and 10y/30y yields; the
   morning's scheduled prints with consensus and prior (8:30 data, 10:00 ISM, auctions, Fed speakers, bank calls).
   Data: SPX daily close; ES/NQ overnight 1-min bars and the futures-cash basis; VIX spot; DXY, 10y, 30y; the
   macro calendar with consensus.
2. **What changed overnight** (optional, 60-100 words + chart). Net gamma last night vs pre-market, the strikes that
   grew or shrank, charm build at the heavy strikes. Data: two snapshots of per-strike gamma and charm for the
   same expiry (prior evening, pre-market).
3. **The levels that matter today** (120-250 words + key-levels chart). The largest positive strike(s) as the pin
   or range, red strikes as fast zones, the bull trigger, the bear trigger, the max-case target. Numbers in
   parentheses are per-strike net gamma. A fixed colour-legend paragraph is repeated in every edition.
   Data: per-strike net dealer gamma and charm for today's 0DTE expiry, spot.
4. **Vanna and dealer positions** (80-200 words + 1-2 bar charts). Where a falling VIX forces dealer buying and
   where it forces selling; net dealer contracts by strike (calls vs puts, long vs short). Data: per-strike vanna
   for the expiry; per-strike dealer net positions (contracts).
5. **VIX** (60-120 words + 1-2 charts). The VIX's own dealer gamma by VIX expiry (short gamma = squeeze risk),
   accel-up and accel-down strikes, regime (dampening vs amplifying). Data: VIX option gamma by strike and expiry.
6. **Technicals / dollar / Mag 7** (optional, 60-120 words + annotated daily chart). 20/50/200-day averages and
   crosses, rising support lines on the VIX, a wedge on a mega-cap basket, DXY patterns. Data: daily OHLC for SPX,
   VIX, DXY, a mega-cap ETF.
7. **The call ("my take") and decision tree** (60-150 words + tree). Base case plus alternatives, the time window
   to watch (usually 10-11:30am ET), and in the source an options tactic (dropped by us, section F).

### B2. Pre-close edition
1. **What happened today** (80-150 words + intraday chart on this morning's map). Open, high and low with clock
   times, which of the morning's paths happened, an explicit admission when the base case failed, VIX path.
   Data: SPX 1-5 min bars for the session; VIX intraday; the morning snapshot of levels.
2. **Intraday chart with trendlines** (17 Nov form): 15-min SPX with a rising support line and the floor.
3. **Tomorrow's expiry book: this morning vs now** (60-120 words + paired bar chart). Grey = earlier snapshot,
   colour = now; which pair of strikes faded, which red strikes appeared above or below price, net gamma within
   +-3% flipping sign. Data: per-strike gamma for the next expiry at two times.
4. **The overnight map** (60-120 words + levels chart). Levels in cash, the futures-cash offset, the floor, the red
   strike below it, the green pull at the top.
5. **Single-name IV question** (event nights): asks how far index vanna would carry the index if the reporting
   name's implied vol collapses - green vanna strikes in sequence with stalls, then VIX brackets matched to index ranges from past cases.
   Data: the single name's ATM IV and expected move; index vanna by strike; a history table of VIX level vs index
   level change (past cases from a similar VIX level).
6. **Scenario routes A/B/C** (120-200 words + route tree). A = base case (event IV drop, VIX falls, index moves to
   a band by the open, extended best case into the monthly expiry); B = muted reaction (VIX in a band, index chops
   between two levels); C = tail (VIX bracket, past-case range, the level whose loss opens the next). Each route
   carries a VIX bracket and a past-case range.
7. **Outlook by horizon** (50-90 words + panel). Uncertainty grade (low/medium/high), the drivers, and a view per
   horizon (1-2 weeks, 2-4 months, 6-24 months).
8. **Keep in mind** (4-6 bullets). The clock times, the conditional levels, the tail line.
9. **When the night turns** (50-80 words + panel). Share of overnight highs and lows by ET hour over ~570 nights,
   when swing turns bunch, how often the Europe open flips the night's direction. Data: years of ES/NQ overnight
   1-min bars.
10. **Risk note** (1-3 sentences). A closing reminder that the preferred route can fail and the tail needs a plan.

### B3. Closing bell and weekly
Adds a rest-of-week block: the next three expiries summed by strike into weekly pins and a red strip between them,
charm and vanna far from spot noted as out of reach, an analog week (a named earlier week the map resembles), and the next
morning's scheduled prints with consensus.

### B4. Medium-term asset piece
Title states the setup; RSI(14) of the dollar vs long bonds; five-session changes; trendline and first resistance per
metal; regression betas of each metal to the dollar over 120 sessions and the implied move for a dollar pullback;
past cases since 2000 matching the setup with best gain and worst drop over the next 40 sessions; options levels on
the ETFs mapped from spot targets (with a caveat that open-interest estimates are cruder than index books).

## C. Chart catalogue

Common frame (every analytic chart): pure-black outer canvas; a rounded content panel; a two-line header outside the
panel (bold title that states the finding, grey subtitle with the numbers); an uppercase letter-spaced panel tag in a
rounded outline box whose colour codes the panel type; a bottom call-out box with a yellow outline and cream bold
text giving the conditional read; a footer row (attribution left, source string with snapshot time right). Tiled
diagonal watermark at very low contrast (we do not reproduce it). Exported at 2x (3000-4000 px wide), shown at
1456 px in email.

| # | Chart | Size (px) / aspect | Grammar |
|---|---|---|---|
| 1 | Title card | 3000x1380 / 2.17 | Outline tag (cyan), huge white title, green date line, short cyan rule, grey sub-line listing the topics. No data |
| 2 | Key-levels ladder ("today's map") | 3000x1875 / 1.60 | Left: horizontal level lines across a price ladder, green = positive gamma, red = negative; line weight = size (solid fat, dashed thin); dotted = charm level; white dash = last close. Bands between lines shaded: red tint = fast, green tint = slow, dark grey = little gamma. Coloured bold price labels at left, coloured descriptor at right (a short role label after the colour word). Right: two thin mini-columns, gamma by strike and charm by strike, horizontal bars on a shared y, only extremes labelled. Legend row top-left inside the panel |
| 3 | Intraday path on the morning map | 3000x1725 / 1.74 | Same ladder; white 5-min price line across the session; prior close dashed white; net gamma per band written in a small dark label inside each band; high/low/now dots with labels; same gamma/charm mini-columns at right |
| 4 | 15-min chart with trendlines | ~3000x1725 | Candles or line on the 15-min, rising support line, floor level; purple/blue lines for trendlines |
| 5 | Before vs after bars (same expiry, two snapshots) | 4000x2500 / 1.60 | Two panels (gamma, charm). Horizontal bars per strike: grey = earlier snapshot, coloured = now (green/red by sign); "a -> b" value labels on the movers; one-line legend at panel bottom |
| 6 | Vanna by strike | 4000x2500 / 1.60 | Horizontal bars per strike, green = falling VIX makes dealers buy, red = rising VIX makes dealers buy; spot as a thin dotted line with a label; extremes labelled in bar colour; right column "how to read it" text block |
| 7 | Vanna + dealer net positions | 4000x2500 / 1.60 | Two panels side by side: vanna bars, contracts long/short by strike (calls vs puts) |
| 8 | Multi-expiry sum (week map) | 4000x2500 / 1.60 | Stacked or side-by-side bars for Wed/Thu/Fri expiries and their sum; pins and red strip labelled |
| 9 | VIX key levels | 3000x1875 / 1.60 | The ladder grammar applied to the VIX: accel-up, accel-down, call wall, short-gamma strikes |
| 10 | VIX expiry gamma over snapshots | 4000x2500 / 1.60 | Vertical bars per snapshot (red short / green long) with $ labels, a thin annotation line to an event note |
| 11 | VIX regime card | 1736x3354 tall | A vendor dashboard screenshot framed in the house panel (this one cites the excluded vendor - see F) |
| 12 | Decision tree | 2360x1400 / 1.69 | Root node (cyan outline, dark cyan fill) -> question node (yellow) -> three branches coloured red / yellow / green, each node a rounded rectangle with a tinted fill of its colour, a bold label and a grey sub-line; arrows in branch colour; a dashed grey node for "not today" paths. Different typeface (geometric sans) from the matplotlib charts |
| 13 | Overnight map with VIX brackets | ~3000x1875 | Ladder (#2) plus a right column listing VIX brackets and the past-case index range for each (each VIX level paired with an index range seen in past cases) |
| 14 | Route tree A/B/C | ~2360x1400 | Decision-tree grammar with three named routes, each leaf carrying the index band and VIX bracket |
| 15 | Night clock / tenor panel | ~3000x2000 multi-panel | A: bar per ET hour of share of overnight highs/lows (orange bars, cyan for the Europe window, % labels); B: hourly moves in small bars; C: table of tenors with coloured status pills |
| 16 | Outlook panel | ~3000x1700 | Uncertainty gauge, driver list, horizon rows (short/medium/long) with coloured verdict pills |
| 17 | Annotated daily screenshots | 1736x2749, 1636x1667 | Charting-platform screenshots (index and VIX daily, weekly trendline) with hand-drawn arrows, framed in the house panel with A/B section labels in cyan/orange |
| 18 | Macro mini-dashboard | 3000x2250 / 1.33 | Three panels: RSI lines with overbought/oversold tinted bands; five-session % bars per asset; lollipop "past cases" chart (best gain top dot, worst drop bottom dot, dashed target lines, n and hit counts in the panel title) |
| 19 | Options payoff | 4000x2500 / 1.60 | Payoff at expiry (white) vs model mark at a date (yellow dashed). Out of scope for us |
| 20 | Earnings schedule card | 4000x2500 | Names, report times and call times as a timeline |

**Why they look sleek.** One finding per chart, written as the title with its number; a strict two-colour semantic
(green/red) used identically in every chart; near-black panels on black so the frame recedes; no gridlines in bar
charts (one zero axis line only); labels only on the extremes; the same header, tag, call-out and footer on every
chart so a reader learns the grammar once; generous inner margins; 2x export so text stays crisp in email.

### Palette (measured from 20 sampled images, exact pixel values)

| Role | Hex | Notes |
|---|---|---|
| Outer canvas | `#000000` | 18-27% of pixels |
| Panel fill | `#0a0a0a` | 40-75% of pixels |
| Panel border | `#1f1f1f` | ~1 px at 2000 px width, radius ~8 px |
| Call-out fill | `#0e0e0e` | |
| Call-out border | `#ffd23f` | ~1.5 px, radius ~10 px |
| Call-out text | `#f3dfa2` | bold, centred |
| Title / primary text | `#ececec` | bold title ~2.4% of width high |
| Subtitle / secondary text | `#a8a8a8` | regular |
| Muted / "previous snapshot" bars | `#6f6f6f` | also footer text |
| Zero axis | `#3a3a3a` | |
| "Free move" band | `#141414` | |
| Positive gamma / falling-VIX buying | `#2ec48a` | the green |
| Negative gamma / rising-VIX buying | `#ff4d4f` | the red |
| Fast-move band (red tint) | `#581f20` (heavy) / `#3a1717` (light) | |
| Slow-move band (green tint) | `#154533` (heavy) / `#0f271e` (light) | |
| Gamma panel tag, root node, dollar line | `#19c3f0` | cyan |
| Vanna/charm panel tag | `#b388ff` | purple |
| Bonds line, overnight bars, VIX accents | `#ff8c1a` | orange |
| Gold series / question node | `#ffd23f` | shared with the call-out border |
| Tree node fills | green `#06140f`, red `#220707`, yellow `#141204`, cyan `#04181d` | tinted near-black |
| Screenshot annotations | `#2d62ff` arrows, `#4dae51` trendlines | platform screenshots only |

Fonts: the analytic charts use a matplotlib-default sans (DejaVu Sans): title bold, subtitle and labels regular,
panel tags bold with ~0.3 em letter-spacing in capitals. Decision trees use a geometric sans (Inter-like). For ours,
use one sans everywhere.

## D. Writing pattern

- **Opening.** A greeting to several time zones, then the prior close with % change, then the overnight range in
  cash terms and where futures point now. The deck line under the title is a casual one-liner, often a question.
- **Levels.** Always comma thousands; ranges hyphenated ("7,690-7,720"); each level gets its role (floor, lid,
  pin, trigger, target) and the gamma number in parentheses; three cases in a fixed order (bull trigger, neutral
  band, bear trigger) and a max-case target. The colour rule is repeated verbatim in every edition (boilerplate).
- **Self-scoring.** Every pre-close opens by scoring the morning: the high and the low with clock times, which named
  path occurred, and a plain admission when the base case failed. The next morning opens by saying whether the
  overnight move was expected or not. Failures are explained by mechanism
  (short VIX gamma overwhelmed the cushion), not dropped.
- **Uncertainty.** Mostly verbal ("most probable", "base case", keep both paths in view, plan for the low-odds tail);
  explicit odds occasionally (one edition gave 40/50/10 for flat/down/new high). A time window to watch is named almost daily
  (10-11:30 ET). Medium-term: an uncertainty grade (low/medium/high) and a view per horizon.
- **Section length.** 60-150 words per section, one idea per paragraph, chart caption under every chart restating
  the finding with numbers. Whole morning edition ~850 words with ~9 charts: the charts carry most of the content.
- **Tone and quality issues to avoid copying.** Typos and loose grammar, hype in subject lines, sweeping claims
  (about market makers and retail), trade tactics inside analysis, and boilerplate repeated daily.

## E. Track record visible in the emails

Scored only from the letter's own later editions (their quoted highs, lows and closes), 2-16 Oct, base case only:

| Edition (base case) | Outcome per next edition | Verdict |
|---|---|---|
| 5 Oct AM: flat 7,700-7,725 | broke up to 7,794 | miss |
| 5 Oct PM: new high to 7,860 next day | new record 7,844.52, not 7,860 | partial |
| 6 Oct AM: grind to 7,860 | same, 7,844 then faded | partial |
| 6 Oct close: flat Wed, early dip | dip at 7am, then 7,800 pin | hit |
| 7 Oct AM: 7,800 +-20 | low 7,763, then pinned 7,800 | hit (loose) |
| 7 Oct PM: Thu range 7,750-7,825 | 7,750-7,800 most of day | hit |
| 8 Oct AM: bounce 7,750-7,800 | held, one dip to 7,731 | hit |
| 8 Oct PM: 50% "really down" to 7,615 | up to 7,820; their own structure closed at a loss | miss |
| 9 Oct AM: range 7,700-7,775 | low 7,779, high 7,820 | miss |
| 9 Oct PM: Mon flat or back to 7,840 | overnight 7,837 | hit |
| 12 Oct AM: pin 7,840, band 7,810-7,850 | 7,810 broke, 7,797 low | miss |
| 12 Oct PM: Tue flat 7,775-7,825 | flat, one dip 7,786 | hit |
| 13 Oct AM: flat, modest flash-crash risk | flat | hit |
| 13 Oct PM: Wed 7,800 or below | hot CPI, below 7,800 | hit |
| 14 Oct AM: gap up to 7,800, swing 7,760-7,800 | 4th listed path: 7,693 low | miss (alt path hit) |
| 14 Oct PM: overnight bounce to 7,740-7,750 | no bounce | miss |
| 15 Oct AM: close near 7,700 | dip 7,670 then 7,754 | miss |
| 15 Oct PM: Fri leans higher to 7,780 | 7,632 low, VIX squeeze | miss |
| 16 Oct AM: run to 7,775-7,810 | bear case to 7,632 | miss |
| 16 Oct PM: Monday green | futures +0.4% pre-market | hit |

Tally: 9 hits, 2 partials, 9 misses out of 20 (45% clean, 55% counting partials). Split: range/flat calls 6 of 10;
directional calls 3 hits, 2 partials, 5 misses out of 10. The standing "VIX squeeze risk" flag (13-16 Oct) did
materialise twice (14 Oct to 17.45, 16 Oct to 22.31) but the same-day base case pointed the other way on 16 Oct.
17 Nov: the morning's bear route occurred (the edition says it did not expect the VIX through 24); the event-night
routes are unresolved in the corpus. The 5 Oct metals call (silver +7%, gold +6% over weeks) is unresolved in the
corpus. Caveats: self-reported prices, my judgment on "partial", base case only, 12 sessions. This matches our
measured null for level-based forecasts (technical-stack section 3): pinned/flat days score, breakouts do not.

## F. What must change for our engine

**Rules.**
1. No trade suggestions, hedges, spreads, tenors, entries, exits, "take profit at the level", "buy the dip" or
   tenor-holding panels. Sections titled "How to play it" or "My take" become "What would change the
   picture". The payoff chart (#19) and the tenor table in #15 are dropped. No sizing, ever (doctrine 14).
2. Price direction is a no-call (ai-trade 5). Levels are described as places where positioning changes, never as
   destinations or targets (technical-stack 0.1). Scenario routes stay as scenarios: each route states its
   trigger, the mechanism, and an odds figure only if it comes from a measured base rate (with n and window);
   otherwise it is labelled "no call". The VIX-bracket ranges are shown as historical distributions ("past cases
   from this VIX level, n = ..."), not forecasts.
3. Every chart carries a record line where a mechanism is shown: our tests found the King magnet and pin null
   (46.7% vs mirror, n = 165), first-tap deflection at random-walk rates, the gamma-sign range ratio inconsistent
   (1.28 / 0.96 / 0.80), the flip-cross trade falsified, the overnight GEX rule null on ~370 holdout nights, and
   vanna splits at chance (12 of 42). The yellow call-out box becomes our "record" box, not a conditional trade read.
4. Events first (user instruction 2026-11-18): the update is a transmission/context layer. A lead item names the
   world event of the day (data, Fed, war/truce, chips policy) and the market section follows; no war-driven oil,
   energy, defense or tanker calls anywhere (charts may show them as context).
5. Data hygiene: never Unusual Whales data. The reference letter's VIX regime card is a screenshot of that vendor
   (its footer says so); its other dealer charts give no source. Ours come only from our own Skylit maps (plus
   Alpaca indicative IV, FRED, our price files). Every number carries a snapshot time and a stale flag.
6. Our own palette and frame: keep the dark-panel grammar (it is generic), but use our tokens, our footer
   ("GT-Analyst, data: Skylit dealer-gamma maps, snapshot HH:MM ET"), no watermark, no title card mimicking theirs.
7. Report-style rules still apply for user-facing documents (no internal machinery in the body, docx + pdf).

**Our files per section (Trading Bot paths are under `tradingview/_skylit/` unless stated; freshness as of 18 Nov).**

| Section | Our source | Freshness | Gap |
|---|---|---|---|
| Prior close, intraday path, 15-min trendlines | `live/<date>/HHMM_heatmap.json.gz`: per-minute Skylit gamma maps with `spot` for SPY, SPXW, QQQ, NDXP, NDX, SMH, VIX (09:30-16:00, 390-400 files/day) | 2 Jan - 17 Nov 2026 (221 days); current to yesterday | RTH only; spot is a 1-min sample, not OHLC bars |
| Today's map (0DTE gamma by strike) | same live files (5 expiries per symbol, `strikes[]`, `matrix[]`) | to 17 Nov 16:00 | no pre-market (08:30) index snapshot; first is 09:30 |
| Overnight map | `live/<date>/overnight_heatmap.json.gz` (17:30 ET, incl. VIX) and `overnight_levels.json.gz` | 17 Nov 17:30 ET | one snapshot a night |
| This morning vs now (two snapshots) | 0930 vs latest `live` file; prior evening = `overnight_heatmap` | current | old `close_maps/` (per-expiry EOD) STALE since 20 Oct |
| Charm by strike | none | - | GAP: not in Skylit gamma maps; compute ourselves from chains or drop |
| Index vanna by strike | none for SPX/SPY/QQQ; `universe/<date>/eod_vanna_*` has VIX and ~120 single names (NVDA yes) | 17 Nov EOD | GAP for index vanna (the vanna-path paragraph cannot be built for SPX yet) |
| Dealer net contracts by strike | none | - | GAP; and the letter's "contracts" view is vendor-derived |
| VIX dealer gamma by expiry, accel levels | `live` and `overnight` maps include VIX; `vixmap/` older runs | live to 17 Nov; `vixmap/` STALE (1 Oct) | regime score (dampening/amplifying) must be our own definition |
| VIX, ATM IV, expected move, term structure | `vol/daily/<date>.json` (SPXW, NDXP, SPY, QQQ, GLD, AAPL, MSFT, NVDA, META, TSLA: atm_iv, em_1d, svx1d/30/3m, skew, term slope, close) | 17 Nov | no intraday IV; high/low null |
| Single-name IV / skew (event nights) | `vol/daily` (NVDA etc.), `skew/<date>.json` (Alpaca indicative greeks + IV, 150 names) | 17 Nov | indicative feed, not NBBO |
| Single-name gamma heatmaps (our heatmap layer) | GT `data/ai_technical/heatmaps_20261117.json` via `tools/heatmap_extract.py` from `universe/<date>/eod_*`; `levels_20261118.csv`, `stack_20261118.csv` | 17 Nov EOD | NVDA map EVENT-STALE after its 17 Nov print |
| Overnight futures, night-turn clock | `dealer_flow/<date>/fut_ES.json`, `fut_NQ.json` (1-min OHLCV bars) | 31 Aug - 16 Nov (55 nights); 2 days stale | ~55 nights vs the letter's ~570: night-clock stats need years of bars (gap) |
| Past-case VIX bracket -> index range | build from `live` (VIX + SPXW spot per minute since 2 Jan) and `vol/history_2025-06-06_2026-09-30.json` | builds to yesterday | ~10 months only; state n on every bracket |
| Daily technicals (20/50/200) | GT `data/ai_prints_backtest/5y/prices_5y.csv` (7 AI names + SMH closes) | 17 Nov | no SPX/VIX/DXY daily OHLC file (gap); FRED daily closes via `fred/` |
| Macro calendar with consensus | `Trading Bot/knowledge/econ_calendar_2026.json`; GT `data/constraint_calendar.json` | dates only | consensus and prior values missing |
| Earnings calendar, expected moves | `moves/<date>.json` and `moves/cal/` (single names, typical move, warnings) | 18 Nov | - |
| Dollar, yields, metals panels | none (GLD IV in `vol/daily`) | - | DXY, 10y/30y, gold/silver series missing (FRED could supply yields) |
| Measured record box | `Trading Bot/knowledge/HEATMAP_DOCTRINE.md`, `RULES_REGISTRY.md`, `TEST_REGISTRY.jsonl`, `OVERNIGHT_LEVELS.md`, GT technical-stack section 3 | registry dated | - |

**Edition plan for us (same kind, our rules).** Morning: event lead, overnight recap (Skylit overnight map + ES
bars), today's map with record box, VIX positioning, what would change the picture, dated watch-list. Pre-close:
score this morning's descriptions (did price stay inside the described band, yes/no, logged), expiry book this
morning vs now, overnight map, event-night scenario table with past-case distributions (n stated), horizon outlook
as no-call unless a licensed base rate exists. Scoring of our own descriptive statements goes to a log, never to
the ledger as price calls.
