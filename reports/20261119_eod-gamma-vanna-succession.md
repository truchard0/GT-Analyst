# End of Day: 19 November — Gamma, Vanna and Succession

*@alostquant*

Thursday opened up and closed near its low. The S&P 500 opened at 7,389 and finished at 7,176, down 2.0% on the day and its sixth straight lower close. VIX ended at 28.3.

Most of the dealer hedging near the price expires tomorrow. Friday's monthly expiry holds between 61% and 93% of each map we track. Take it out and the S&P and QQQ books lean short gamma near the price, so the cushion thins after Friday. That says nothing about which way prices go, and our tests found no direction edge in these maps, so direction is a no-call.

What we can measure is size. After a day this wide, the next day was also wide 82% of the time. The median next-day range runs at about 0.82 times the 5-day average, roughly 120 S&P points.

## Read this first

> **This is a map of where dealer hedging sat at the 13:00 PT close (16:00 ET) on 19 Nov 2026, not a forecast.** Our tests found big strikes aren't special levels, the largest strike doesn't pull or pin price, and the sign of dealer gamma doesn't predict direction. The literature supports only a small effect on how much prices move. Multi-week map readings are untested, single-name maps are the least reliable, and the vanna sign convention hasn't been audited against the vendor. Every statement below carries its status: supported, lead, null, failed or untested. Not investment advice.

## What drove today: an up open, then a fade that began before the IPO

The tape faded through three scheduled events. Times are PT, from the wires' own timestamps.

- **04:47.** Walmart beat on third-quarter revenue and raised its sales outlook. The stock still traded lower by late morning (Yahoo Finance; CNBC).
- **05:27.** The Trump-Xi meetings ended with little change on chips, rare earths or tariffs (Yahoo Finance).
- **06:37.** Stocks opened higher, the S&P 500 up about 1% (Yahoo Finance).
- **08:04.** Stocks faded to session lows. AMD fell about 8% after the short seller Hunterbrook disclosed a position (Yahoo Finance; CNBC).
- **08:50.** Anthropic's shares first traded at $111.50, against an $83 offer price. By 10:07 they'd slipped to about $97 (Yahoo Finance). We don't make price calls on this stock.
- **09:24.** Chip stocks gave up their gains, and Nvidia and Broadcom turned red (Yahoo Finance). Nvidia's report this week showed revenue and profit both doubling.
- **13:00.** The Dow fell about 2.2% and the Nasdaq about 2.3%. VIX closed at 28.3, up 15% on the day.

The order matters more than any one headline. The slide to the lows came about 45 minutes before Anthropic's first trade, so the IPO didn't start it. The S&P closed at 7,175.83; our map sample at 13:00 PT read 7,177.56.

## The board: Friday holds most of every map

The board shows each book at the close with today's expired column removed, so it's the map that carries into Friday. Yellow cells are where dealers are estimated long gamma, purple ones short. Three things stand out. Friday's column dominates every book. The two S&P books disagree near the price. And QQQ's largest cell sits right on the close.

&#91;image: Strike by expiry dealer-gamma board for SPXW, SPY, QQQ and SMH at the 13:00 PT close\]

## Book by book: the S&P books are flat to short, QQQ and SMH long

### S&P 500 0DTE book (SPXW): flat near the price, short after Friday

At the close the book was flat. Net gamma within 2% of the price came to −2.9% of the map, under our 3% line for a call either way. Measured on a tighter map, 3% either side, it reads −3.5%, so call it flat to slightly short. Friday's expiry holds 61% of it.

The largest cell is a short-gamma position at 7,220 on Friday's expiry, 0.6% above the close. The largest long rows sit at 7,300 above and 7,155 just below. The largest short row below is 7,140, 0.5% down. Two thin stretches frame the price: 7,105 to 7,135 underneath and 7,355 to 7,390 overhead.

After Friday the book turns short, −23% of what's left. What's left is only 39% of today's map, and its largest cell becomes 7,160 on Monday's expiry, short, just under the close. Our re-pricing puts the flip far off: about 7,461 now, 3.9% up, and about 7,013 after Friday, 2.3% down. Status: the regime's effect on volatility is supported in the literature and small; the flip is our computation, and trading its cross failed in our tests.

### SPY: short near the price, with the day's largest put-side position underneath

SPY's book was short at the close, −10.6% of the map within 2%. Friday holds 93% of it, the most of any book. Its largest cell is a big short-gamma position at the 710 strike, 0.8% under the close, and it grew all afternoon as price fell toward it. The largest long row above is 718. Below 710 the map thins out down to 695, nearly 3% lower.

After Friday SPY reads long, +9.9%, but on a map just 7% of today's size, so it says little. Our flip sits at about 724, 1.1% above the close. Status: descriptive; the claim that the largest strike pulls price is null in our record.

### QQQ: long at the price, short after Friday

QQQ was long, +35% of the map within 2%. Its largest cell is a long position at 645, right on the close, on Friday's expiry, and Friday holds 84% of the book. The nearest long rows are 650 and 640, each under 1% away. The short rows are far off, at 670 and 625. A thin patch runs from 626 to 634, between 1.7% and 2.9% under the close.

Take Friday out and the book turns short, −11.5% of a map that's 16% of today's size. Its largest cell is then a short position at the same 645 strike, on Monday's expiry. Our re-pricing finds no flip within 4% either now or after the roll. Status: descriptive; the claim that the largest cell pins the close is null (46.7% against a mirror strike over 165 readings).

### SMH: long on the live map, flat to short on the longer one

The live SMH map runs five expiries to 30 Nov. It was long near the price, +22%, with its largest cell a long position at 460 on Friday, 2.8% above the close. A second long row at 457.5 holds 80% of that cell's size. After Friday it stays long, +24%, with the largest cell at 450 on 30 Nov.

The end-of-day map runs to the 18 Dec monthly and tells a different story. Near the price it's flat, +0.4%, and after Friday it's short, −15%. Its largest cell is a short-gamma position at 450 on 18 Dec, 0.7% above the close. The two maps aren't really contradicting each other; they weight different expiries, and the December position sits outside the live map. Status: single-name and ETF maps are untested in our record, and the sign convention is least reliable there.

## Through the selloff: the map followed price down

On the whole S&P map, gamma near the price stayed long all day. It read +18% at the open and +32% at the close. That reading leaned on today's own expiry, which grew from 29% to 63% of the map as the session went on.

Strip today's expiry out and the picture slides. The part of the S&P book that carries into Friday went from +18% at 06:30 to −3% at 13:00. SPY's slid the same way, from +11% to −11%. QQQ and SMH stayed long on both reads.

&#91;image: Net gamma within 2% of the price on every map of the day, with and without today's expiry\]

The map's centre of weight moved down with price in all four books, and the largest cell changed strike in all four. SPY's moved once, from 740 to 710 by 07:30, and then kept growing as price fell toward it. The S&P King started at 7,350, jumped briefly to 7,450, sat at 7,250 by 09:00 and ended at 7,190.

&#91;image: Price, the largest cell and the map's centre through the day, per book\]

This is what our record says to expect. Rolls show up after price has already moved 8 to 10 basis points the same way, and they haven't predicted the next move. Status: the map follows price (supported, descriptive); rolls as a signal are null.

## After Friday: three of four books change state

Friday 20 Nov is the monthly expiry, and it takes most of every map with it. Here's what's left near the price, measured on what remains.

| Book | Now, within ±2% | After Friday | Map left | Largest cell after Friday |
| --- | --- | --- | --- | --- |
| S&P 0DTE (SPXW) | flat, −2.9% | short, −23% | 39% | 7,160, 23 Nov, short, −0.2% |
| SPY | short, −10.6% | long, +9.9% | 7% | 695, 23 Nov, short, −2.9% |
| QQQ | long, +35% | short, −11.5% | 16% | 645, 23 Nov, short, at the close |
| SMH (live map) | long, +22% | long, +24% | 27% | 450, 30 Nov, long, +0.6% |
| SMH (map to 18 Dec) | flat, +0.4% | short, −15% | 50% | 450, 18 Dec, short, +0.7% |

&#91;image: Re-priced total gamma now and after Friday's expiry, with the flip, per book\]

The practical reading is about cushion. Most of today's long gamma near the price lives in Friday's column. Once it's gone, the S&P and QQQ maps lean short near the price, which the literature links to somewhat larger and more persistent moves.

The effect is small. The largest volatility increase dealer gamma ever caused in the S&P, on exchange data that records who took each side, was 3.3 annualised points. And the post-roll maps are thin (SPY's is 7% of today's), so Monday's live map will matter more than this projection. Status: what rolls off is true by construction; the post-roll map's effect on prices over days is untested.

## Vanna: SMH leans positive, the single names split four and four

Vanna measures how much dealers' hedges change when implied volatility moves while price stays put. On SMH's end-of-day map, net vanna within 5% of the price is positive: +12% of the map now and +13% after Friday. The largest cell after Friday is a negative position at 477.5 on 27 Nov, about 7% above the close.

Read it both ways. If implied vol falls, positive-vanna re-hedging leans to buying. If it rises, it leans to selling. Vol is high going into the roll, with VIX at its 99th percentile for the year, so both paths are live.

&#91;image: SMH net dealer vanna by strike, now and after Friday\]

Among the single names with a vanna map today, four lean positive after Friday: SMH, PANW, AMD and MSFT, between +9% and +13% of their maps. Four lean negative: QCOM, MU, AAPL and NVDA, between −3% and −10%. KLAC and WMT had no vanna map today, only morning gamma maps. Index vanna isn't in our data.

&#91;image: Net vanna near the price for SMH and seven single names, now and after Friday\]

Treat all of it as description. On our data the vanna family tested null: 12 of 42 splits passed, against 12.6 expected by chance. The four gamma-plus-vanna states didn't separate next-day direction over 305 sessions, and vanna added nothing inside a gamma state. Status: null as a family; single names untested; sign convention unaudited.

## SPX against SPY: two books, not two votes

The S&P 0DTE book and SPY disagree tonight. SPXW is flat near the price, with its largest cell above the close at 7,220. SPY is short, with its largest cell at 710, about 7,120 on the S&P scale and below the close.

That's normal. The two books are built from different contracts, and their largest cells land within 5 points of each other only 18% of the time. In price they move almost one for one, so even when they agree it isn't independent evidence. Status: the books are distinct (validated); agreement as a filter is null.

## Succession: a crisis-band day in a month running at bear pace

Successions are our count of how wide a day was. Under a 0.60% range it's zero, then one more for every half-point. Today's 3.30% range made six, the "crisis" band. The close finished 2.89% under the open, an extreme extension.

November has had 38 successions in 14 sessions. That's a pace of 57 a month, against the 20 that labels a month bearish. The last 20 sessions hold 43. The bearish monthly label hasn't meant lower returns, though: the month after a bearish one averaged +1.6% since 2016, better than after a bullish one. Status: the count is arithmetic; volatility persistence is validated; the label failed as a direction signal.

The selloff checklist reads HIGH, with 13 of 14 items on. On a HIGH reading it projects a further 7-10% drop over 20-25 sessions, to a zone of 6,458 to 6,674. It's invalidated by a close above today's high of 7,415.64.

Its record says not to read that as a forecast. Since 2016 the projection was fulfilled after 14% of HIGH days and invalidated first after 84% (473 days). Of 17 separate HIGH episodes, 3 reached −7% within 25 sessions. The average 25-session return after a HIGH day was +2.6%, and 68% ended higher. But 41% of those days saw a drawdown of 5% or more along the way. Status: failed as a selloff forecast; it marks volatility, not direction.

&#91;image: The selloff checklist reads HIGH, 13 of 14, with its measured record\]

For Friday the 5-day average true range (ATR-5) is 147 points, 2.1% of the close. Over 2,675 days the next day's range had a median of 0.82 times ATR-5, which is about 121 points, and it stayed at or under the full ATR-5 66% of the time. The band of the close plus or minus half an ATR, 7,102 to 7,249, held the next close 52% of the time but the whole next-day range only 22%. Status: validated as a size gauge, not as levels.

&#91;image: Friday's range models: 20-day bands, ATR, the options-priced move and Fibonacci\]

ATR-5 over ATR-20 is 1.19. That's the "normal" regime, short of the 1.30 that marks expanding volatility. In the normal regime the next day's range had a median of 0.84%; in the expanding one, 1.25%. VIX closed at 28.3, up 9.6 points in five sessions and 7.5 above its 20-day mean. Status: regime labels descriptive.

&#91;image: VIX over 120 sessions and implied vol by horizon\]

Twelve of the last 30 sessions were extreme extensions, 40% against 34% over all history. The Fibonacci ladder from today's open was hit on all ten downside levels and two upside ones. That ladder failed our test: its levels held 51% of 793 touches, against 55% at shuffled distances. Status: move distribution descriptive; Fibonacci failed.

&#91;image: Move classes over the last 30 sessions against all history\]

## Dave's three questions

### What's most likely, in probabilities?

These are the only odds we can stand behind. Each is measured, with its sample.

| Statement | Odds | Sample | Resolves |
| --- | --- | --- | --- |
| S&P closes Friday inside the options-priced 1-day move, ±1.99% (7,036 to 7,321) | 74% | 389 sessions, Mar 2025 to Nov 2026 | Fri 20 Nov, 13:00 PT |
| Same, only on days with 30-day implied vol near today's | 59% | 17 sessions (small) | Fri 20 Nov, 13:00 PT |
| Friday's range is two successions or more (1.10% or wider) | 82% | 476 days after a 3+ day | Fri 20 Nov close |
| Friday's range is at or under ATR-5 (147 points) | 66% | 2,675 days | Fri 20 Nov close |
| Direction of the S&P on Friday | No call | gamma sign: up 49-55% in every state, 305 sessions | n/a |

Today was one of the misses on the first line. The priced move was ±1.48% and the S&P fell about 2.0%. That happens about one day in four, and 6 of the last 20 sessions have landed outside.

On direction we have nothing to sell you. Our tests of these maps found no edge, so the honest answer is no-call.

### How should risk be managed?

We don't give positions or sizes. The maps and base rates do say something about how big moves may be and when cushions go away.

- **Moves are running about 1.7 times their 60-day norm.** ATR-5 is 2.1% of the close, against 1.2% for ATR-60. Range persistence is the best-measured thing in this report.
- **Options are pricing a bigger day than the averages.** Friday's priced move of ±1.99% sits just under ATR-5 and well above the median range our record expects.
- **Most of the near-price cushion expires Friday at 13:00 PT.** Between 61% and 93% of each map sits in that column. After it, the S&P and QQQ maps lean short gamma near the price.
- **Monday's map is the one that counts.** The post-roll maps here are thin projections, and the S&P 0DTE book changes a median 24% overnight, so any map is stale by the open.
- **Thanksgiving week is short.** Markets close Thursday 26 Nov and close early Friday 27 Nov.

### What would signal a trend reversal?

These are closing tripwires you can watch, with today's reading. None is a tested reversal signal, and the status column says so.

| Tripwire | Today | Gap | Status |
| --- | --- | --- | --- |
| VIX closes back under its 20-day mean | 28.3 vs 20.9 | 7.4 points | Untested as a reversal signal |
| S&P closes above today's high, 7,415.64, the checklist's invalidation | 7,176 | +3.3% | Came first after 84% of HIGH days; the checklist failed as a forecast |
| S&P closes back above its 200-day average, 7,348 | 7,176 | +2.4% | Untested on the index |
| ATR-5 over ATR-20 back under 1.0 | 1.19 | −0.19 | Size gauge, validated; not a direction signal |
| A day with zero successions, a range under 0.60% | 3.30% range | n/a | Descriptive |
| QQQ map long near the price after the roll | short, −11.5% | sign change | Null for direction (305 sessions) |

If several of these trip together, the volatility picture has changed. That's what they're good for. Whether the trend turns is a separate question, and nothing here answers it.

## For long-term holders

The near-term risk is real, and we won't dress it up. VIX sits at its 99th percentile for the year. The selloff checklist reads HIGH. The S&P has fallen six days running and is 8.5% below its October high.

Our record after HIGH readings cuts both ways. The average 25-session return afterwards was positive, and about two in three ended higher. About two in five also saw a further drop of 5% or more first. That's a market with wider swings in both directions, not a broken one. The base rates support neither a crash call nor an all-clear.

## Dated checkpoints

- **Fri 20 Nov, 06:30 PT.** Monthly expiry day. The AM-settled S&P monthly settles at the open. Dealer charm into that settlement is the one map effect with peer-reviewed support, and it's narrow.
- **Fri 20 Nov, 13:00 PT.** Friday's column expires, taking 61-93% of every map with it. The close also scores the priced-move line in the table above.
- **Fri 20 Nov, 14:30 PT.** The evening map shows the post-roll book as it really is, not as projected.
- **Mon 23 Nov, 06:30 PT.** First session on the post-roll maps. Check whether the S&P and QQQ books are short near the price, as projected here.
- **Wed 25 Nov.** SMH's next weekly expiry.
- **Thu 26 Nov.** US markets are closed for Thanksgiving. Friday 27 Nov closes early, at 10:00 PT.
- **Fri 18 Dec.** The December monthly expiry, where SMH's largest longer-dated position sits.

## Sources

- **Dealer positioning:** Skylit dealer-positioning maps. Live index maps for 19 Nov 2026, eight snapshots from 06:30 to 13:00 PT; half-hourly level files; end-of-day single-name gamma and vanna batches taken at 13:01-13:03 PT. Reads, re-pricing and charts: `tools/index_gamma.py`, written to `data/ai_technical/index_gamma_20261119.json`.
- **Succession and ranges:** Yahoo daily S&P 500 and VIX, 2016 to 19 Nov 2026, via the Trading Bot succession cache; `tools/market_context.py`, written to `data/ai_technical/market_context_2026-11-19.json`.
- **Options-priced moves and implied vol:** Skylit volatility files for 18 and 19 Nov 2026 and their history from March 2025.
- **News:** Yahoo Finance live blog "Stock market today", 19 Nov 2026, updated 13:06 PT; CNBC "Stocks making the biggest moves", 19 Nov 2026, updated 09:59 PT.
- **Our tested record:** `research_notes/gamma_maps/B_measured_record.md` (the 55-day magnet and pin tests, the 305-session gamma-sign table, the 42-split vanna family, the 9-contrast lockbox).
- **Literature:** dealer gamma and S&P volatility on signed Cboe data, July 2020 to June 2023 (largest effect +3.3 volatility points).
