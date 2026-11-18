---
name: market-update
description: Our own daily US market update (morning, pre-close and overnight editions) built from our Skylit dealer-gamma maps by tools/market_update - event lead first, then the index map, the strike x expiry heatmap layer, VIX positioning, single-name gamma and vanna, the earnings move strip and scenario routes whose odds come only from measured base rates with n. Defines the run commands, section anatomy, chart catalogue and the data each chart needs, wording and no-trade rules, staleness rules, the morning-band self-scoring routine (data/market_update/scorecard.csv) and the known data gaps. Also the house matplotlib chart style (tools/market_update/chartstyle.py) for any chart in the repo. Use when asked for a market update, a pre-close or overnight note, a levels map, a gamma heatmap, or any new matplotlib chart.
---

# MARKET UPDATE - our daily US market note from our own maps

The update is a transmission and context layer under the events-first rule: the world event of the day leads in one or
two lines, the market map follows. It is descriptive. Levels are places where dealer positioning changes, never
destinations. Price direction is a no-call. Nothing here is advice.

Format study (learning only; never name, quote or copy the studied letter, its branding or watermark): `SPEC_NOTES.md`
in this folder.

## 1. Run it

```
python -I tools/market_update/build.py --date 2026-11-17 --edition preclose --tickers NVDA        # cut 15:45 ET
python -I tools/market_update/build.py --date 2026-11-17 --edition preclose --asof 1530           # other cut
python -I tools/market_update/build.py --date 2026-11-17 --edition overnight --tickers NVDA,MU,SMH
python -I tools/market_update/build.py --edition overnight                                        # latest night
python -I tools/market_update/build.py --date 2026-11-18 --edition morning --tickers MU          # needs the 09:30 map
python -I tools/market_update/build.py --date 2026-11-17 --score-only                            # score the band at the close
python -I tools/market_update/build.py ... --theme light                                          # print variant (_light dir)
```

Output: `reports/market_update/<date>_<edition>/` with the PNG charts (3000x1875, 2x), `update.md`, `update.pdf`
(ReportLab, letter, charts kept whole) and `update.docx` (python-docx). Always `python -I` (the scratchpad holds an
`inspect.py` that would shadow the stdlib); the package adds the user site-packages back for numpy on its own.
Before a run, write the day's event lines to `data/market_update/events/<date>.json` (section 4).

Timing: the pre-close edition uses only data stamped at or before its cut (maps, spot path, events by report time,
vol files by publish time, scorecard rows by date), so a back-dated edition never knows the future. The overnight
edition reads the 17:30 ET overnight map. The morning edition needs the 09:30 live map (there is no pre-market index
map; that is a gap).

## 2. Section anatomy

**Morning** (09:30 map): events lead -> key calls -> overnight (last night's map spot vs the open) -> today's map
(same-day ladder, morning band logged as the base case) -> VIX positioning -> single names (T-1 universe maps) ->
earnings strip -> routes for today -> dated watch-list -> data and staleness.

**Pre-close** (cut 15:45 ET default): events lead -> key calls -> what happened today (open, high, low with clock
times, VIX path, the priced move, the morning-band score so far) with the intraday chart on the 09:30 map -> the next
expiry this morning vs now -> the map across expiries (heatmap, today's expiring column left out) -> the next expiry's
levels -> VIX -> single names into tonight's reports (pre-report maps flagged) and the earnings strip -> routes into
the next session -> what would change the picture -> dated watch-list -> our record -> data and staleness.

**Overnight** (17:30 ET map): events lead -> key calls -> how the day closed and how the morning band scored (final)
-> the overnight map (next expiry, levels in cash, futures-cash offset with its stale flag, base-rate side table) ->
heatmap -> next expiry this morning vs tonight -> VIX -> single names (EVENT-STALE names dropped with a note) ->
earnings strip with the implied move that covers each report -> routes -> watch-list -> our record -> data notes.

Key calls table (house report style): Call | Odds | Resolves | What flips it. Rows: the morning-band base case (odds =
its measured containment rate), the next close inside the priced move (odds = measured share with n), and "Direction
of SPX: No call". 40-60% is never published as a call. Prose voice follows `report-writing`; no internal machinery
(ledger ids, skill sections, gates) in the body.

## 3. Chart catalogue (tools/market_update/charts.py)

| Chart | Function | Data it needs | Status |
|---|---|---|---|
| Key-levels ladder: green/red gamma lines, weight = size, dashed = small, fast/slow/free band tints with net gamma per band, mini gamma columns | `levels_ladder` | one expiry column of a Skylit map + spot (+ prior close) | works (live, overnight, VIX) |
| Intraday price on the morning map, high/low/now with clock times, band marker | `levels_ladder(path=...)` | 09:30 map + per-minute spot (`spot_path`, cached in `data/market_update/cache/`) | works |
| Same expiry before vs now, "a -> b" on movers, change panel | `before_after` | two snapshots of one expiry (09:30 vs cut, or 09:30 vs overnight) | works |
| Strike x expiry dealer-gamma heatmap (purple short / yellow long, spot line, king outlined) | `gamma_heatmap` | live or overnight index map (5 expiries); universe single-name maps (8 expiries shown) | works |
| Single-name vanna by strike with spot and a how-to-read panel | `vanna_bars` | `universe/<date>/eod_vanna_*` (16:00 ET batch only) | works after 16:00; blocked for earlier cuts |
| Overnight map with a measured base-rate side table | `levels_ladder(side_table=...)` | overnight map + vol history | works |
| Scenario route tree (cyan root, tinted branches, each leaf a measured share with n, dashed "no measured odds" node) | `route_tree` | vol history (close, svx30, implied 1-day move) | works |
| Earnings expected-move strip (past report-day moves, implied move, gap chance) | `earnings_strip` | `moves/<session>.json`, vol daily of the close before the reaction session | works; implied move only for names in the vol file |
| Charm by strike | - | not in our maps | GAP |
| Index vanna (SPX/SPY/QQQ), vanna IV-crush path for the index | - | none | GAP |
| Dealer net contracts by strike | - | none (the studied letter's view was vendor-derived) | GAP |
| VIX bracket -> index range past cases | - | live VIX + SPX since Jan 2026 could build it; not built (state n) | TODO |
| Night-turn clock (share of overnight highs/lows by hour) | - | needs years of full overnight ES/NQ bars; ours are 06:00-16:14 ET, 55 days | GAP |
| Multi-expiry week map, macro mini-dashboard (DXY, yields, metals), annotated daily charts | - | no DXY/yield/metal series wired; FRED folder holds events only | GAP |
| Payoff charts, tenor-holding tables, trade boxes | - | - | BANNED |

**House style** (`chartstyle.py`, use it for every matplotlib chart in the repo): `cs.apply("dark"|"light")`,
`cs.frame(title, subtitle, panels, tags, callout, footer_right, snapshot)` -> fig and panel rects, `cs.panel_axes`,
`cs.save` (dpi 200 -> 3000 px wide). Measured palette: canvas #000000, panel #0a0a0a, border #1f1f1f, green #2ec48a,
red #ff4d4f, cyan #19c3f0 (gamma tags), purple #b388ff (vanna/change), orange #ff8c1a (VIX), yellow #ffd23f
(call-out border, scenario tags), call-out text #f3dfa2. Grammar: the title states the finding with its number; grey
subtitle carries the numbers; uppercase letter-spaced tag; no gridlines; labels on extremes only; the yellow call-out
states OUR MEASURED RECORD (never a trade read); footer "GT-Analyst · data: Skylit maps <snapshot> · not investment
advice" left, exact source right. Titles shrink and subtitles and call-outs wrap automatically; check every PNG by eye.

## 4. Inputs and staleness

Loaders (`data.py`) return a snapshot time and a stale flag for everything:
- Same-day or T-1 = fresh; 2 weekdays = STALE (shown, flagged); older = not shown.
- A single-name map taken before that name's earnings release is EVENT-STALE from the release on: no levels shown, a
  note says why. Before the release it is labelled "pre-report map".
- Release times come from the moves list ("after the close" = 16:00 ET, "before the open" = 08:00 ET).
- The implied move for an earnings reaction comes only from the vol file of the close before the reaction session,
  and only if it was published before the edition's cut.
- ES/NQ bars cover 06:00-16:14 ET; the futures-cash offset carries its T-n flag.
- Events: `data/market_update/events/<date>.json`, items `{kind: lead|watch, topic, text, source, reported_utc |
  known_from_et, until_et, when_et}`. Facts come from our processed tape with report times; never from the studied
  letter. Oil and war items are context only.

Hygiene: never Unusual Whales data; any path containing whales/unusual/cards is refused by `data.check_path`; never
the cached option chains of unclear source. Nothing is written to Trading Bot.

## 5. Wording and no-trade rules

- Say "dealers are net long gamma above 7,310 on the 18 Nov expiry"; never "7,310 is the target / magnet / floor
  that will hold". Roles allowed on a level: largest + strike, largest - strike, band floor, band top, + gamma, - gamma.
- No entries, exits, hedges, spreads, tenors, sizes, "take profit", "buy the dip", payoff charts. "My take" and "how to
  play it" sections become "What would change the picture".
- Price direction is a no-call. Routes are about the size of the next move relative to what options price, and each
  carries a measured share with its n and window, or "no measured odds". Event-night odds stay "no measured odds"
  until a report-night sample exists.
- No war-driven oil, energy, defense or tanker calls anywhere; charts may show them as context only.
- Every number carries its snapshot time; Skylit gamma units are compared within one symbol only.

## 6. Self-scoring (TRACK -> SCORE)

- **Statement scored daily:** "SPX closes inside the morning band", the span between the largest positive same-day
  gamma strike at or below the 09:30 open and the one at or above it, within 1.5%. Endpoint-dated, never touch-based.
- **Log:** the morning edition (or the first edition of the day, back-filling from the 09:30 map) appends a row to
  `data/market_update/scorecard.csv` with outcome `pending`.
- **Score:** the overnight edition or `--score-only` scores it on the 16:00 ET spot sample (inside / above / below).
- **Record shown:** `stats.band_record` over the live history (cache `data/market_update/history_spxw.json`, built
  incrementally): containment of the close by the real band vs its MIRROR band (same band reflected through the open),
  with a day-block bootstrap of the gap. As of 17 Nov 2026: 52-53% vs 44%, n = 259-260 sessions (Oct 2025 to Nov
  2026), gap CI about +2 to +15 points. In-sample and not pre-registered: SHADOW, a lead only. Promote only after a
  pre-registered out-of-sample run (2027 sessions, same definition, both halves).
- **Routes record:** `stats.route_rates`: next close vs the priced 1-day move, unconditional (n = 419, 73% inside)
  and by 30-day implied vol bucket (+-2.5 points). History days without a stored implied move use svx1d_adj x the
  median ratio em_1d_pct / svx1d_adj from the daily files (about 0.062); state it if asked.
- These are descriptive statements, never ledger price calls. Misses stay in the scorecard and in the record box.

## 7. Measured record used in the call-out boxes

Largest node as a magnet null (46.7% vs mirror, n = 165); first-tap deflection at random-walk rates; gamma-sign
range ratios 1.28 / 0.96 / 0.80 (inconsistent); flip-cross trade falsified; overnight node rule 51.2% vs 51.1%
placebo on ~370 unseen nights; vanna splits 12 of 42 against 12.6 by chance; rolling ceilings and floors follow
price. Sources: Trading Bot `knowledge/HEATMAP_DOCTRINE.md`, `OVERNIGHT_LEVELS.md`, `TEST_REGISTRY.jsonl`, and
`technical-stack` section 3.

## 8. Known caveats

- Skylit spot is a 1-minute sample: highs and lows can differ from exchange prints by a few points (17 Nov: our
  7,413.88 / 7,290.92 vs printed extremes a few points wider).
- The 16:00 map spot (7,340.90 on 17 Nov) differs from the official close in the vol file (7,333.89); the overnight
  edition quotes the vol-file close and scores the band on the 16:00 map sample (stated in the scorecard note).
- The SPX history before Oct 2025 has no 09:30 file, so the band record starts there.
- The single-name universe folder can be empty for a day (16 Nov 2026): the edition says so instead of reaching back.
