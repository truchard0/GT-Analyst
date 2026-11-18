---
name: gamma-maps
description: How to read a dealer-gamma heatmap (our Skylit maps) at research depth - the hedging physics, the map's anatomy and vocabulary (King, gatekeeper, air pocket, floor/ceiling, roll, slip-in, decoy, flip), a disciplined read procedure, and a claim-by-claim evidence table that puts the vendor's teaching beside our own measured record and the academic literature. Risk comes first - every reading carries its status (supported, lead, null, failed, untested) and the map is never used for direction, targets, entries, stops or sizing. Use whenever a report, market update or analysis reads a gamma, vanna or charm map, a strike x expiry heatmap, walls, a flip level, or "dealer positioning" for an index or single name, at any horizon from intraday to several weeks.
---

# GAMMA MAPS - reading dealer positioning without fooling ourselves

Built 18 Nov 2026 from three research passes, kept in `research_notes/gamma_maps/`:
`A_skylit_method.md` (the vendor method as taught: 7 transcripts, the doctrine files and the 96-video synthesis),
`B_measured_record.md` (about 80 rules we tested, with n, controls and status) and `C_theory_evidence.md` (the academic
literature, graded A-D). Cite those files for detail; this skill is the working distillation.

---

## 0. RISK FIRST - read this before reading any map

**What a map is.** An *estimate* of where option dealers would have to buy or sell to stay hedged. Skylit's numbers come
from an unpublished "inference layer"; the teacher never defines the unit or what the sign means, and admits the
method may not be "100% correct" (A §1.2). Our reconstruction shows the intraday ladder is driven by traded volume times
gamma, not open interest (B table E). It is not an exchange record of anyone's position.

**What our own tests found** (B; every figure has a file:line source there):
- Big nodes are not special levels. Price turns at a big node 68.8-73% of the time, and at *any* strike with the same
  geometry 72-76%. The vendor's "80% first tap" is the random-walk barrier rate (~75%).
- The King is not a magnet (price got closer only 40-48% of the time) and does not pin the close (46.7% vs the mirror
  strike, 165 readings on 55 days).
- The sign of dealer gamma does not call the next day's direction (305 sessions; four-state medians -0.01% to +0.16%).
- Map changes follow price: a "roll" appears after an 8-10 bp move in the same direction and predicts nothing.
- A pre-registered lockbox of 9 deflection contrasts went 0 for 9. The overnight node rule passed on 20 nights and failed
  on ~370 unseen nights (51.2% vs 51.1%). Single-name map setups went 0 for 17. Sign flips: 31,488 events, no edge.
- The one live lead: the S&P morning band held the close 52.3% of 260 sessions vs 43.8% for its mirror, but the second
  half alone is not significant and it was never pre-registered. It is a lead, not a finding.

**What the literature supports** (C, grades A/B): dealer gamma is a *second-moment* signal. Long gamma goes with lower
realised volatility and more intraday reversal; short gamma with higher volatility and late-day momentum. The effects are
small: on Cboe data that records who took each side of every trade, the largest volatility increase dealer gamma ever
caused in the S&P was 3.3 annualised points (Jul 2020-Jun 2023). Nothing peer-reviewed supports gamma predicting
*direction*, call/put walls as support and resistance, the flip as a trigger, or "vanna rallies" as a scheduled effect.

**The sign problem.** Most maps assume customers buy puts and sell calls, so dealers are short puts and long calls. On
signed exchange data S&P dealers are usually *long* gamma, and on single stocks the assumption is wrong on average
(end users are net short single-stock options). Skylit claims not to use that convention, but its method is unpublished,
so treat every sign as uncertain, single names most of all.

**Therefore - the only permitted uses:**
1. Describe where hedging sits: geography, size relative to the King, distance in %, which expiry holds it.
2. Describe the volatility context: long vs short gamma near the price, as a statement about how much prices may move
   and whether moves tend to continue or reverse, with its evidence grade.
3. Describe the calendar: what expires when, and what the map looks like after each roll-off.
4. Put what options price (the implied move) beside the measured base rates.

**Never:** a price target, a direction call, a touch level, an entry, a stop, a size, a hit-rate claim above our record,
or the vendor's own accuracy numbers presented as fact. Price direction stays a no-call (ai-trade §5).

**Every output that shows a map carries a risk box** (template in §7) stating the snapshot time, the measured record,
and that the map is positioning, not a forecast.

---

## 1. The physics in one page

- **Hedging.** A dealer short an option and delta-hedged holds -delta of the underlying. Gamma is how fast that hedge
  must change. Short gamma: price up -> dealer buys, price down -> sells (pro-cyclical, amplifies). Long gamma: the
  reverse (counter-cyclical, damps). The prediction is about *variance and autocorrelation*, not the sign of the next
  return (feedback models: Jarrow 1994; Frey & Stremme 1997; Sircar & Papanicolaou 1998).
- **Units.** The usual convention is dollars of delta per 1% move: `sum(sign * gamma * OI * 100 * S^2 * 0.01)`. Our
  computed GEX uses it (B table E); Skylit's display is in thousands and its scale is uniform only *within* one ticker.
  Never compare raw values across tickers.
- **Time.** At-the-money gamma scales like 1/(S * sigma * sqrt(T)), so the nearest expiry and nearest strikes dominate
  any summed map, and a map changes sharply when an expiry rolls off. Our check: 1-day gamma peaks ~5.5x with a
  half-width ~1.05%; "everything outside +-3 sigma*sqrt(T) is decoration" (A §2.3).
- **Charm** (delta decay with time) and **vanna** (delta change with implied volatility) move hedges with no price
  move. Charm has one solid result: dealer net charm predicts the overnight move into the monthly AM-settled S&P expiry
  (t = 2.99, R^2 3%; Baltussen, Terstegge & Whelan 2024). Vanna has no peer-reviewed test.
- **Pinning.** Theory pins price to a big strike at expiry only when hedgers are net *long* options and open interest is
  large (Avellaneda & Lipkin 2003). Single stocks show modest clustering at expiry (Ni, Pearson & Poteshman 2005). The
  S&P shows the opposite of what dealer hedging predicts, and one non-peer-reviewed study finds no S&P pinning in
  2016-2025.
- **0DTE.** Most of the gamma that matters on a 0DTE day was accumulated earlier in longer-dated contracts (about 25 bp of
  hedging needs vs 3 bp from same-day trades; Adams et al. 2026). Signed data say 0DTE adds long gamma to dealers on
  average and damps index volatility; this is contested, not settled.

---

## 2. Anatomy of our Skylit maps

- **Grid.** Rows are strikes, columns are expiries, nearest first. Our extract (`tools/heatmap_extract.py`) keeps five
  expiries and a +-12% strike window; the board (`tools/ai_report_charts.py`) shows up to 11 rows per name.
- **Values.** Signed, scaled ("by the thousandth"), described as "net notional" or "dealer exposure"; positive = dealers
  long gamma (damping), negative = short gamma (amplifying), as far as the sign can be trusted.
- **Construction.** Flow-driven: best reconstruction is cumulative volume x Black-Scholes gamma with zero OI weight, so
  nodes can be born intraday. The API nets five expiries by default. The API "SPX" ladder is the *monthly* book; the 0DTE
  S&P book is SPXW. SPXW and SPY are different maps (their Kings agree within 5 points only 18% of the time).
- **Colour.** On Skylit's default palette colour ranks *value*, not sign: "a purple- or blue-looking cell without a minus
  sign is still a positive node". Read the number. Our board uses a signed scale (yellow long, purple short).
- **Size.** Absolute value is strength; express nodes as a signed % of that book's own King, never as raw dollars across
  books. Four-digit (thousands) values are the teacher's significance floor.

**Vocabulary** (definitions from A §1.5; measured status from B):

| Term | Definition | Measured status |
|---|---|---|
| King | Largest absolute value on the board for the chosen expiries; depends on the expiry setting | Magnet null; pin null |
| Gatekeeper | Node between spot and the King, at least ~25% of the King (five competing definitions) | Gatekeeper tap failed (precision below clock-matched controls) |
| Floor / ceiling | The biggest node below / above price (docs); the largest positive node (Academy) - conflict | Not tested as a level |
| Call / put wall | Our computed max +GEX strike above spot / max -GEX below | No academic or internal support as a level |
| Air pocket | Strikes under ~10-20% of the King, or missing | Speed lead only (n tiny); direction null |
| Roll | Floor moving up / ceiling moving down across updates | Lags price 8-10 bp; null |
| Slip-in | Node born at spot | Direction null |
| Rug / reverse rug | Positive over negative / negative over positive (five definitions) | Untested as price behaviour |
| Decoy / hedge node | Large far-OTM node around data, FOMC, OPEX, earnings | Descriptive |
| Flip | Spot where total gamma changes sign (we compute it; Skylit's terminal does not show it) | Flip-cross trade failed; no academic test |
| Velocity | Rate of change of a node's size | Descriptive |

---

## 3. The disciplined read (eight steps; write each down with a timestamp)

1. **Instrument and staleness.** Name the book (SPXW 0DTE vs SPX monthly vs SPY/QQQ vs single name), the snapshot time
   and batch (close, open, overnight), and the expiries shown. Flag staleness: a pre-report map is event-stale from the
   release; the S&P 0DTE book changes a median 24% overnight and its King changes on a third of nights; the first 30-45
   minutes reshuffle; OPEX and quarter-end distort.
2. **Regime near the price.** Sum net gamma within +-2% of spot across the shown expiries; call it long, short or flat
   (flat = under 3% of the map's total absolute gamma). State it as volatility context with its grade: literature
   supports a small damping/amplifying effect (index, grade A/B); our intraday tests on the index are inconsistent
   (range ratio 1.28 / 0.96 / 0.80 across books); single names are untested and the sign itself is least reliable there.
3. **Concentration by expiry.** Share of the map's absolute gamma in each expiry. A front expiry holding most of the map
   means the picture changes at that roll-off. Re-read the map with that column removed: that is the next map.
4. **Geography.** King (strike, expiry, % from spot, sign), the largest long and short rows above and below, gatekeepers
   between spot and the King, air pockets. Describe distances in %; distance, not size, governs whether price reaches the
   nearest node (503,816 states: reach ~65-72% within 60 minutes regardless of size or sign).
5. **Dynamics.** Velocity, rolls, slip-ins, washed-off nodes. Say plainly that changes follow price.
6. **Cross-checks.** S&P books (SPX, SPY) are ~0.999 correlated, so agreement between them is not independent evidence.
   Trinity agreement tested null. For a single name, note the index regime and the sector ETF map.
7. **What options price.** Put the implied move beside the base rates: the S&P closed inside its priced 1-day move 73% of
   419 days; across 2,901 earnings events the median realised gap was 0.61x the implied move and 27% went beyond it.
8. **Write it with labels.** Every statement carries its status word (supported / lead / null / failed / untested), and
   the risk box goes with the read.

---

## 4. Claim-by-claim evidence (teaching vs our record vs literature)

| Claim (as taught) | Our record | Literature | How to use it |
|---|---|---|---|
| The King is a magnet / settles price | Null (magnet 40-48%; pin 46.7% vs mirror) | Pinning only at expiry, small; S&P runs opposite | Describe as the largest position; never a target |
| First tap of a big node deflects ~80%; taps decay 80/66/33 | Null: 68.8-73% vs 72-76% any strike; later taps reverse *more* | None | Do not cite deflection odds |
| Yellow damps, purple accelerates (node level) | Null (SPY lead did not replicate) | Book-level sign has support; node colour none | Use the book-level regime only |
| Negative gamma = bigger ranges | Inconsistent across books; 0DTE SPXW 1.09 [0.90, 1.35] leans that way | Supported, small (max +3.3 vol pts S&P) | Volatility context, graded |
| Positive gamma = mean reversion | Not separately tested | Supported (A/B), decays within ~1 hour | Volatility context |
| Gamma sign calls direction | Failed (305 sessions) | No support | Never |
| Rolls signal direction | Null; map follows price | None | Describe, never forecast |
| Gatekeeper tap / King tap | Failed vs clock-matched controls | None | Never as a trigger |
| Flip cross-and-fail reversal | Failed (+0.3-0.9 pts vs +12 bar) | Flip untested as a level | Descriptive only |
| Walls as support/resistance | Stock walls failed as NQ levels; single-name walls untested | No located test | Descriptive only |
| Charm pins after 14:00 | Failed | Charm into monthly AM expiry supported (narrow) | Note only for monthly SPX expiry |
| Vanna rally / vanna features | Family null (12 of 42 vs 12.6 chance); 2 non-directional leads | No test | Context only, sign unaudited |
| Overnight nodes as levels | Failed out of sample (~370 nights) | None | Never |
| Single-name setups | 0 of 17 | Sign convention wrong on average | Highest skepticism |
| Morning band (S&P closes between the largest strikes either side of the open) | Lead only (52.3% vs 43.8%; H2 ns) | None | SHADOW; out-of-sample test pending |
| Expiry concentration / roll-off changes the map | Descriptive, true by construction | Supported mechanically | Safe to describe |
| Implied move vs realised | 73% inside (index, n 419); earnings 0.61x median, 27% beyond (n 2,901) | Options over-price earnings on average | Safe base rates |

---

## 5. Horizons - what can honestly be said

- **Intraday.** Geography and regime as context; nothing as a trigger. Our deepest tests are here and they are null.
- **Next day.** Regime does not call direction. The evening map is stale by the open (24% median change).
- **One to four weeks.** Nothing on our data tests multi-week map reads (B "never tested"). What *is* defensible: the
  expiry calendar (what rolls off when), the post-roll map, the regime of the expiries that remain, and the implied move
  into scheduled events. Say explicitly that multi-week map readings are untested.
- **Earnings.** A pre-report map is event-stale after the release. Use the implied-move base rates; the map adds nothing
  tested.
- **OPEX / quarter-end.** Front-expiry nodes "wash off" at the close and the next column takes over; OPEX columns are
  noisy by the vendor's own account. Monthly AM-settled S&P expiry is the one place charm has evidence.

---

## 6. Single names vs indices

Index 0DTE maps are dense (5-point strikes); the vendor doctrine was built on sparse single-stock maps (next node 15-45
points away), and rules do not transfer between them. Single names add three problems: the dealer sign convention is
wrong on average, liquidity is thinner (where gamma effects are larger but less certain), and we have only end-of-day
maps for a few weeks. Read single-name maps as geography and calendar only.

---

## 7. Output template (positioning read)

> **[Name] · [book] · map [date time ET, batch] · expiries [list]**
> Near the price: [long / short / flat] gamma ([x]% of the map within +-2%) - volatility context, [grade].
> Concentration: [y]% of the map expires [date]; after that the largest position is [strike, expiry, sign, % from spot].
> Geography: King [strike / expiry / sign / % away]; largest long row above [ ]; below [ ]; largest short row [ ].
> Options price: [implied move] into [event] (base rate: [ ]).
> Status: descriptive; [any lead named]; direction no-call.

**Risk box (mandatory, verbatim core):** "This is a map of where dealer hedging sat at [time], not a forecast. Our tests
found big strikes are not special levels, the largest strike does not pull or pin price, and the sign of dealer gamma
does not predict direction. The literature supports only a small effect on how much prices move. Multi-week map
readings are untested. Not investment advice."

Wording: say "dealers are long gamma near the price", never "support" or "magnet"; "the largest position", never
"target"; "untested" whenever a claim has no test. Charts follow the house style (`market-update` skill) and name
their data file.

---

## 8. Open tests (the research agenda, from B)

1. Morning band out of sample (pre-registered, unchanged definition).
2. Single-name regime -> next-5-session range (60+ name-days, both halves, shuffled-date null).
3. Single-name largest node at expiry vs mirror strike (50+ expiries, weekly and monthly separately).
4. Single-name walls over 1-10 sessions vs mirror and shuffled walls (n >= 60 touches).
5. Pre-report map vs |realised| / implied move on the 2,901-event earnings set.
6. 0DTE SPXW negative gamma -> next-hour range (~150+ days, ideally 1-second maps).
7. Evening map vs next session against mirror levels (~250 nights).
8. Vanna sign audit against Skylit's vanna files before any further vanna claim.
9. Growing vs fading node, and gatekeeper break vs reversion, with the any-strike geometry control.
10. Score the forward shadows registered 1-2 Oct 2026; keep the sealed OPEX-week charm test sealed.

Until a test passes out of sample, the map stays descriptive. formal-game-theory and ai-trade rules still apply; the
war-price ban is absolute.
