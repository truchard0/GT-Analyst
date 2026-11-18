---
name: technical-stack
description: The technical-analysis stack used for POSITIONING CONTEXT in GT-Analyst - trend versus the 20/50/200-day averages, distance from the 52-week high and low, 3-month relative strength against SMH, realised volatility, and dealer options positioning from our own Skylit maps (gamma regime, flip, call and put walls, the largest node, expected move into earnings), plus breadth, patterns, vanna, charm and flow as observed in a studied practitioner archive. Each layer is rebuilt on our data (prices_5y.csv, the Skylit levels file and close maps, the GEX/VEX registry), carries its measured record and an ADOPT or SHADOW status, and comes with a report format, wording rules, staleness rules and a daily and pre-earnings runbook. Use it whenever a report or analysis mentions where a stock or index sits technically, what dealers are positioned for, or what the options market prices into an event. It never produces a price target, a touch level, a trade or a size; price direction stays a no-call under ai-trade section 5, and war-driven oil, energy, defense and tanker price calls stay banned.
---

# TECHNICAL STACK - positioning context, measured and dated

Built 18 Nov 2026 from a study of one practitioner archive: about 2,100 short posts from 4 Sep to 16 Nov 2026, read in
full or by technical keyword (about 1,350 read), plus a sample of their charts. The archive's long-form posts were
not on disk. Everything below is restated in our own words and re-scored on our data. Where each layer came from is
recorded only in `PROVENANCE.md`; never name, quote or imitate the source in a skill, analysis or report.

**Where it sits.** After the ai-trade layering (checklist 26-30) and the mechanism sweep (31-35). It feeds the
"market translation" step and the report's positioning box. ai-trade wins on which calls a layer allows,
formal-game-theory wins on validity, and the stack never overrides either.

## 0. RULES THAT OVERRIDE EVERYTHING BELOW

1. **No targets, no touch levels.** The archive's core output was "if X holds, price goes to Y today". Those calls
   mostly missed when scored (section 3). We publish levels as places where the positioning changes, never as
   destinations.
2. **Price direction is a no-call** (ai-trade section 5 rule 6). The only price statements allowed are the two
   ai-trade exceptions. Technical states can describe a price, never forecast it.
3. **No trade instructions, no sizing** (doctrine section 14). Spreads, hedges, entries and stops seen in the archive
   are recorded as observed behaviour and never reach a report.
4. **War ban.** No oil, energy, defense or tanker level, wall or expected move appears as a call. Such charts can
   show context only.
5. **Data hygiene.** Options positioning comes only from our own Skylit maps. The archive's dealer charts came from a
   commercial flow vendor that house rules exclude; never use or recommend it, and `tools/technical_stack.py` skips
   any row labelled with it.
6. **Every number carries a timestamp and a stale flag.** No timestamp, no publication.

## 1. THE STACK AS OBSERVED

The archive was about 85% S&P 500 intraday positioning. Single names appeared mostly around earnings, and long-horizon
macro charts on weekends. Shares below are the share of posts touching each layer (n = 2,095). About 36% of posts
quoted an S&P level in the 7,300-7,900 band.

| # | Layer | What it computed, as observed | Parameters seen | Share |
|---|---|---|---|---|
| 1 | Data inputs | Per-strike dealer gamma and vanna by expiry, intraday snapshots; index and futures 1-minute bars; VIX and VIX futures; option premiums | 0DTE and 1DTE columns read separately; pre-market and close snapshots | n/a |
| 2 | Gamma regime and pin | Net dealer gamma per strike in dollars per 1% move. Positive strikes damp moves and pin; negative strikes speed them up. The day's range is set in the first hour, inside the band where gamma concentrates | A simulation: short-gamma book realises 1.46x raw vol, long-gamma 0.73x; a session's net gamma of about +$9bn per 1% above a pivot strike, negative below | 4.7% |
| 3 | Walls and largest nodes | The biggest strikes above and below price as brakes or accelerants; a "box" between two large positive strikes; an empty run of strikes as a fast lane | Pin box of about 26 index points between two strikes on an expiry day | in 2 |
| 4 | Charm | Delta decay with time pulls price toward a heavy strike into the close; strongest and narrowest in the last hour; fails when price is far away or another node sits in between | Same-day expiries only | 0.7% |
| 5 | Vanna and vol crush | Dealer buying or selling when implied vol drops, by strike; used for post-event and post-spike moves; negative vanna above price blocks a post-earnings rally | Each expiry repriced at the post-event vol; a base-vol and event-move straddle fit | 1.5% |
| 6 | Vol regime | VIX level and its own dealer gamma by expiry; whether VIX and the index move together or apart; post-spike decay | Hedging called cheap below ~18; spikes under ~18-19 said to retrace; ~20-22 read as a washout zone | 7.1% |
| 7 | Expected move | The at-the-money straddle's implied move into an event | Quoted per name (for example 6.2%, 7.2%, 10.3%) | 0.8% |
| 8 | Earnings setups | A three-branch ladder (better than perfect / in line / disappointing), each mapped to a gamma or vanna level; reaction judged during the call, not the headline | Two to three levels per name | 2.9% |
| 9 | Levels | Intraday support and resistance, prior highs and lows, all-time high, gaps between strikes; ETF-to-index conversion | SPY roughly SPX/10 minus 2 at the time | 4.6% |
| 10 | Trend lines and patterns | Rising and falling wedges, channels, long-run trend lines on log charts, double tops | Daily and weekly; the archive itself said double tops work badly near highs | 2.1% |
| 11 | Moving averages | Index and stock position against the 20/50-day (short), 200-day (crash filter) and 500/1000-day (regime); 20- versus 50-week order | A claim: no 20%+ S&P fall since 1928 without a close below the 200-day first, after a median 7.5% drop | 0.6% |
| 12 | Momentum oscillators | RSI extremes as exhaustion | 4-hour RSI near 16 oversold; RSI above 80 a stretch | 1.1% |
| 13 | Breadth | Members above the 200-day, count and frequency of new 52-week lows, equal-weight against cap-weight, share of members up on the month, members in downtrends, compared with 2000, 2007 and 2013 templates | S&P 500 and Nasdaq-100 constituents, daily closes | 0.9% |
| 14 | Relative strength and rotation | Semis' gains concentrated overnight; index return with and without AI names; sector up-share against the index-wide rate | Month-to-date, one-year | 1.0% |
| 15 | Flow | Put and call premium direction, trades at the bid read as sales; premiums rising with price read as a warning | Its own check found big call buying had about zero correlation with direction | 2.1% |
| 16 | State model | Long-horizon bull / bear / transition regimes with persistence; a two-dimensional "map" of where an index sits | Persistence quoted near 94% (bull) and 90% (bear); said to work only on month-plus scales | 1.0% |
| 17 | Time of day | Overnight versus cash-session drift, early-morning and late-morning reversal windows, event reactions in steps | Overnight drift up, cash session flat, since mid-2026 | 6.0% |
| 18 | Risk framing | Defined-risk spreads, hedging both sides, closing short-dated options the same day | Out of scope for GT | 2.6% |
| 19 | Routine and presentation | Pre-market structure post, intraday updates, close post, weekend long-horizon charts. Charts: dark panels, the finding as the title, horizontal gamma-by-strike bars with the traded band shaded, A/B/C panels, a table of levels above and below price, a bottom-line box with the conditional read, and a footer with source, snapshot time and method | Daily | n/a |

**How the layers combined.** The chain ran: vol regime (is VIX rising or decaying?) -> gamma map (where is the pin and
where are the fast zones?) -> charm and vanna (what does time decay or a vol drop force dealers to do?) -> time of day
(when does that force bite?) -> a level ladder with "holds / breaks" branches. Earnings swapped the first link for the
implied move and repriced the map at post-event vol. Trend, breadth and state charts were a separate weekend layer
for the medium-term backdrop and rarely entered the day's call.

## 2. THE SAME STACK ON OUR DATA

Our sources:
- `data/ai_prints_backtest/5y/prices_5y.csv`: daily closes from 2 Nov 2020 to 17 Nov 2026 for NVDA, AVGO, MU, TSM,
  AMZN, META and SMH. No highs, lows, volume or ORCL.
- `data/ai_technical/levels_<YYYYMMDD>.csv`: a separate process writes this from Skylit maps and Tempest. Per name it
  holds the snapshot time, the expiries netted, the regime, flip, walls, the largest node, the event move and the next
  report date.
- Skylit close maps (Trading Bot `tradingview/_skylit/close_maps/`, read-only): per-strike, per-expiry gamma for SPY,
  QQQ, SPXW and NDXP. The last file is 20 Oct 2026, so it is stale.
- The GEX/VEX registry, heatmap doctrine and test registry in Trading Bot `knowledge/`, for measured verdicts.

| Layer | Powered by | Computation spec (`tools/technical_stack.py`) | Gaps |
|---|---|---|---|
| Trend and MAs | prices_5y | SMA20/50/200 of closes; % close vs each; state = above all, below all, or mixed; 50d vs 200d order | No intraday; 500/1000-day possible but not shipped |
| Levels | prices_5y | 52-week (252-session) closing high and its date, closing low; % off high, % above low | Closing basis only (no highs and lows), so intraday extremes are missed. No trend lines or volume profile |
| Relative strength | prices_5y | 63-session return; RS = (1 + r) / (1 + r_SMH) - 1 | The levels file uses the difference r - r_SMH; the two differ by under 1 point at these sizes. State which |
| Realised vol | prices_5y | Close-to-close log-return stdev, 20d and 60d, x sqrt(252); 20d percentile against its own trailing year (5-day steps); 1-day sigma = RV20 / sqrt(252) | Close-to-close underestimates gap-heavy names |
| Gamma regime, flip, walls, largest node | levels file; close maps for index ETFs | Pass-through from the levels file with its source string and snapshot. For maps: regime = sign of net gamma within +-2% of spot; call wall = largest positive strike above spot; put wall = largest negative strike below spot; largest node = max abs value with sign; flip left blank, because a zero-cross of strike sums is not the re-priced flip | Single-name maps exist only where the levels process pulled them (no TSM or ORCL map on 18 Nov). Expiry netting differs by source and must be stated |
| Vanna, charm | none live | Not computed. The registry's vanna work is SPY/QQQ only | No single-name vanna or charm |
| Expected move | levels file (Tempest event move) | Pass-through; compare to the RV-based 1-day sigma | Only where Tempest priced an event |
| Breadth | none | Not computed | Needs constituent closes |
| Flow, time of day, state model | none | Not computed and out of scope | Intraday and vendor-dependent |

The script also flags a wall on the wrong side of spot and a spot-vs-close gap above 2%.

## 3. EVIDENCE AND TRACK RECORD

**What our registries measured.** The heatmap doctrine pre-registered 55 days of 1-second Skylit maps across four
books, with day-block bootstrap and controls (mirror levels, other-day Kings, any strike with the same geometry):
- **King magnet, early drive-off and late pin:** null. Price closed nearer the King than a mirror level 46.7% of the
  time on 0DTE SPXW (n = 165).
- **First-tap deflection:** 68-73% at big nodes against 72-76% at any strike with the same geometry. That is
  random-walk arithmetic, and later taps reversed slightly more.
- **Negative gamma means bigger ranges:** range ratios of 1.28 (SPX), 0.96 (SPY) and 0.80 (QQQ), so no consistent
  sign. 0DTE SPXW gave 1.09 [0.90, 1.35]: the only cell leaning the doctrine's way, and still not significant.
- **Rolling ceilings and floors:** these follow price rather than lead it.
- **Deflection lockbox:** all nine contrasts failed (836-touch baseline).
- **Flip-cross trade:** falsified (+0.3 to +0.9 points on 597-1,287 signals against a +12 bar).
- **Wall definition and greek math:** validated as computations. Walls are side-restricted, vanna is computed from
  vanna and not vega, and the vanna check came within about 1% of a hand grid.
- **Four GEX x VEX states (305-324 sessions):** next-day SPY does not separate by state.
- **Vanna sweep:** 12 of 42 vanna splits passed against 12.6 expected by chance. Two leads survived permutation, but
  they are day-quality labels, not direction.
- **Prior day's largest-node sign:** a lead for next-day fade quality in both halves (median peak 107 vs 70% in the
  first half, 82 vs 42% in the second), with money only in the first half.
- **Fibonacci levels from the open as support and resistance:** failed (held 51% vs 55% shuffled).
- **Trend-day predictors, breadth among them:** AUC 0.44-0.61 on 881 sessions, so nothing.
- Chart-pattern votes are doctrine with no statistics. Moving averages, relative strength and daily breadth had no
  test in any registry.

**What we added (18 Nov 2026, in-sample, prices_5y).** Six names, 21-session steps, 63-session forward windows that
overlap, Nov 2021-Aug 2026, n = 348. There was no shuffled null and only one regime, so read these as leads only.

| Split | Median 63d return vs SMH | Share beating SMH |
|---|---|---|
| Above 200-day (n 244) / below (n 104) | +2.2% / -2.4% | 56% / 46% |
| 3-month RS > 0 (n 176) / < 0 (n 172) | +3.4% / -1.9% | 59% / 47% |
| More than 25% off the 52-week high (n 79) / not (n 269) | +0.4% / +0.8% | 53% / 53% |

20-day realised vol predicted the next 20 days' realised vol with correlation 0.51 (n = 348). Volatility clusters,
and this is the one forecast-shaped property strong enough to use as context.

**The archive's own record.** The archive never published a scorecard and set its own bar at about 60% accuracy for
intraday calls. We could check seven single-name statements against daily closes:
- NVDA 4 Sep (a failed push, then lower): hit by the next session.
- NVDA 9 Sep (below a level, then about 4% lower): reached on day 3.
- NVDA 10 Sep (recovery to a band by week's end): miss.
- META 25 Sep (stall, then a bounce): miss, about 5% lower.
- MU 30 Sep (earnings ladder): void, a +3.0% move that stayed inside the ±6.2% implied move.
- META 21 Oct (earnings ladder, disappointing branch): reached on day 3.
- NVDA 8 Nov (an IV-crush rally to $200): miss, 155 on 17 Nov.

That is 1 clean hit, 2 late partials, 3 misses and 1 void; the intraday S&P levels, most of the archive, cannot be
scored without intraday index data. Touch-level targets mostly missed. The mechanics it explained well (pinning, vol
crush after events, charm into expiry) are real; using them as dated price forecasts is what failed.

**Status.** "Describe" means the layer may appear in a report body as timestamped context. "Forecast" means it may
shape a probability or move a timeline conditional. No layer is ADOPT as a price forecast.

| Layer | Describe | Forecast | Test that would promote the forecast use |
|---|---|---|---|
| Data timestamps and stale flags | ADOPT | n/a | n/a |
| Trend vs 20/50/200 | ADOPT | SHADOW | 30+ names, pre-registered, shuffled-date null, both halves, then 2027 out of sample; even then only as a tail base rate (ai-trade 6) |
| 52-week distance | ADOPT | SHADOW (no separation) | Same protocol |
| RS vs SMH (3m) | ADOPT | SHADOW | Same protocol, plus a 6- and 12-month form against the momentum literature |
| Realised vol | ADOPT | ADOPT for vol-state context only (corr 0.51) | Score 20 dated vol-state statements; promotion to ledgered vol calls needs Brier below 0.20 |
| Expected move (implied) | ADOPT (it is a market price) | SHADOW | Log realised vs implied for 20+ reports; if 60-75% land inside, the containment rate becomes a base rate |
| Gamma regime and flip | ADOPT, as a map description | SHADOW (null-55d; flip trade falsified) | Pre-register "positive vs negative regime -> next-5-session realised range ratio" on single-name EOD maps, 60+ name-days, both halves |
| Walls and largest node | ADOPT, as a map description | SHADOW (null-55d; lockbox 0/9) | Close-at-expiry distance to the largest node vs a mirror strike, 50+ expiries |
| Vanna, charm | SHADOW | SHADOW (vanna chance-level) | Needs single-name vanna data first |
| Breadth | SHADOW (no data) | SHADOW | Needs constituent closes; then the 200-day crash-filter claim on 1928+ data |
| Trend lines, wedges, patterns, RSI | SHADOW | SHADOW (doctrine; Fibonacci failed) | 100+ pre-registered daily-bar patterns against shuffled lines |
| Earnings ladders | not used | SHADOW (archive 1 partial of 3) | Never: breaks ai-trade's "no L1 -> L5" |
| Flow, time of day, state model, risk framing | not used | not used | Out of scope for a world-events engine |

## 4. HOW IT APPEARS IN GT-ANALYST REPORTS

**The positioning box.** At most one short box per name, placed after the call that needs it, with this shape:
> *Positioning as of 17 Nov close (Skylit end-of-day map, 10 expiries to 18 Dec; prices to 17 Nov):* MU closed 22.9%
> under its 50-day and 6.4% under its 200-day, 40.8% off its June high, 6.8% behind SMH over three months. Dealers
> were long gamma above 710, the call wall sat at 727.5, and the largest node was a negative strike at 750. 20-day
> realised vol 104%, the 86th percentile of its year.

**Standard chart set.** Every title states the finding with its number. Every footer gives the source, the snapshot
time, the expiries netted and the stale flag.
1. **Levels ladder per name:** one vertical price axis with the close, the 20/50/200-day averages, the 52-week high and
   low, the flip, the walls and the largest node (sign coloured, never by colour alone). Example title: "NVDA closed
   24% under its 200-day and 35% off its October high".
2. **Expected move into earnings:** a ±band for the implied move next to the RV-based move over the same horizon, and
   past realised report moves where we have them. Example title: "Options price AVGO's 9 Dec report at ±8.9%, about 2x
   a normal day".
3. **RS vs SMH:** the 3-month ratio line rebased to 100, one line per name.
4. **Trend strip:** names by % vs 20/50/200-day as a diverging heat strip.
5. **Realised-vol percentile:** horizontal bars, one per name.
6. **Gamma by strike** (only when the map is fresh and the story needs it): horizontal bars by strike in dollars per
   1% move, with the close marked. Not on event-stale maps.

**Wording rules.**

| Say | Never say |
|---|---|
| "Dealers were short gamma below 150 in the 17 Nov map" | "NVDA will fall to 150" |
| "The largest node sat at 750, a negative strike" | "750 is the magnet / target" |
| "Options priced a ±8.9% move" | "AVGO will move 9%" / "a beat sends it to X" |
| "MU sits 23% under its 50-day" | "MU is oversold and due a bounce" |
| "Realised vol is at the 98th percentile of its year" | "Vol will crush after the print" |
| "In positive-gamma maps moves tend to be damped; our 55-day test could not confirm it" | "Positive gamma means it will pin" |

**Staleness rules.**
- Prices: a T-1 close is fresh. Older than one weekday, label it STALE with its date. Older than five, do not chart it.
- Options maps: same-day or T-1 only. A map taken before an earnings report or a scheduled shock is EVENT-STALE from
  the release onward: say the map predates the event and show no levels from it.
- Any map older than two weekdays is not shown. A node describes its own expiry and lapses when that expiry passes.
- Every map read states its expiry netting (for example "10 expiries to 18 Dec" or "same-day only"), because "the
  largest node" depends on it.
- A side-restriction warning or a spot gap above 2% from the script must be resolved or footnoted before publication.

**What never goes in:** targets, "goes to", touch levels or intraday levels; entries, stops, spreads, hedges or sizes;
time-of-day patterns; "smart money" reads of flow; earnings ladders mapping a beat to a price; oil, energy, defense or
tanker levels; any price view on ANT; vendor data excluded in rule 0.5; the archive's name; ledger IDs, statuses or
this skill's name in the body. Statuses and the stack CSV path belong in the desk-records appendix.

**What may become a ledgered statement** (only through the normal gates, kind `markets`, never on war-banned tickers):
- vol-state calls ("SMH 20-day realised vol above 40% on 31 Dec"), once the forecast use is ADOPT;
- the two ai-trade price exceptions, where the stack supplies the measured input (for example the drawdown depth).

Every such statement is endpoint-dated with a falsifier. Nothing touch-based is allowed.

## 5. RUNBOOK

**Daily (after the close or before the session's analysis):**
1. Check the inputs. Find the last date in `prices_5y.csv` and the newest `levels_<date>.csv`. If prices lag by more
   than one weekday, refresh them before anything else or carry the STALE flag.
2. Run `python tools/technical_stack.py --tickers <names> --date <today>`. Add `--maps-dir <Trading Bot>/tradingview/_skylit/close_maps` for SPY or QQQ.
3. Read every stale flag and note. Drop event-stale or more-than-two-weekday maps from the report. Resolve
   side-restriction and spot-gap warnings.
4. Diff against the previous `stack_<date>.csv`. Note crossings (200-day, 50/200 order), new 52-week closing highs or
   lows, regime sign changes, and RS sign changes. These are the only technical items worth a sentence.
5. Tie each item to the world-events read as description. Never infer the next move from it, or price from a print
   (ai-trade checklist 27).
6. Write the positioning boxes and the chart set. Put statuses and the CSV path in the appendix.
7. Ledger nothing from this skill unless it is a gated vol-state or ai-trade-exception statement.

**Pre-earnings (from T-5 sessions to T+1):**
1. Confirm the report date from the company (ai-trade rule 3). A pattern estimate gets a void rule.
2. Record the implied event move (levels file or Tempest) and the RV-based 1-day sigma. Report the ratio as "the
   market prices about Nx a normal day".
3. Take the last map before the release. Label it pre-event, and from the release onward treat it as EVENT-STALE.
4. Make the L1 print calls under ai-trade, as separate rows. The technical layer adds only "what is priced".
5. At T+1, log the realised close-to-close move against the implied move, with the snapshot time, for the
   expected-move containment test (section 3). Record misses as well as hits.

**Checklist additions** (run whenever this skill is used):
- **36.** Every technical number has a timestamp, a source, its expiry netting and a stale flag.
- **37.** No sentence turns a level, a wall, a node or a pattern into a destination or a direction.
- **38.** The positioning box is description; any forecast use is SHADOW unless section 3 says ADOPT.
