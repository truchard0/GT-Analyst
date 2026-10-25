---
name: market-transmission
description: Market-transmission layer for geopolitical news analysis — turns a geopolitical/macro headline into a dated, mechanism-based, cross-asset prediction. Core is a CONDITIONAL FORK: classify the shock as oil-SUPPLY-driven (inflationary/hawkish → rate-hike odds up → high-beta/long-duration re-rating) vs GENERIC/DEMAND (risk-off/deflationary → oil DOWN, 2y yield DOWN, buy-the-dip). Covers the Caldara-Iacoviello GPR baseline, Kilian supply-vs-demand decomposition, the rate-expectations fast channel, equity-duration derating, safe-haven-failure cases, horizon-matching, and priced-in discipline. Use on every market-relevant event alongside jiang-doctrine + formal-game-theory; it upgrades the "market translation" step of the output schema from ad-hoc to mechanism-based.
---

# MARKET TRANSMISSION — how geopolitics reprices assets

Built from a verified deep-research pass (2026; primary sources: Fed IFDP 1222 / Caldara-Iacoviello AER 2022, Kilian & Park 2009 / Kilian RBA 2009, ECB WP2472 & Economic Bulletin 2026, IMF GFSR 2025, SSGA 2026). Sources in §14. This layer answers "so what does it DO to the tape," and it replaces the naive reflexes ("war = oil up, gold up, stocks down") with a branching, mechanism-based map. Doctrine §14 still binds: **direction and mechanism, never position sizing.**

---

## 1. THE MASTER GATE — classify the shock first (everything hinges on this)
Before any cross-asset call, decide which of three the event is. This single classification flips the entire prediction.

- **SUPPLY-driven** — the event disrupts (or credibly threatens) oil/energy supply. **Diagnostic:** the headline names a producer/chokepoint AND oil is *rallying* without a strong-growth story. → **Inflationary/hawkish branch (§3).** BUT split by cause (the over-fire fix, from eval Case 4 — OPEC+ Apr-2023):
  - **EXOGENOUS / involuntary** (facility knocked out, chokepoint closed, war, sanctions — Hormuz, Aramco strike, Russia-energy): supply is *taken away against the producer's will* → **persistent**, size for multi-quarter (§7).
  - **ENDOGENOUS / voluntary** (a **cartel CHOOSES to cut** — OPEC+ quota action): the cut is a **costly signal that the producer privately forecasts weak demand** (§10.6 cui-bono; Fearon private-info tell) → **typically FADES**, because OPEC cuts precisely when it sees softness. Do NOT accept Branch-B persistence for a voluntary cut until you run the demand flip-test (formal §10 item 2): does the bull survive a plausible demand-softening? If demand fragility is on the tape (banking stress, recession fears), the cut fades below the pre-cut level within 1-3 months. **A managed cut is not a war.**
- **DEMAND-driven** — oil moves because global growth is moving (aggregate-demand shock). **Diagnostic:** oil rising *alongside* a strong-growth narrative, or falling on a growth scare. → treat via §9 (good-oil) or the risk-off default.
- **GENERIC** — broad tension, terror attack, non-energy region, election/coup with no supply impact. **Diagnostic:** oil *flat-to-down*, no chokepoint named. → **Risk-off/deflationary branch (§2).**
- **CORRIDOR** *(added from eval run 2026-07-13 — the gate's missing branch)* — a chokepoint/route closure **without production loss** (Red Sea 2023, Ever Given 2021): oil supply is intact but a freight corridor isn't. **Diagnostic:** shipping suspensions/reroutings + war-risk insurance repricing while crude is muted. → Transmission runs through **freight rates, insurance premia, and corridor-specific equities**, NOT oil or broad equities (those default to Branch-A-minimal). Duration is **incentive-conditioned, not just physical** (refined from eval Case 6): run cui-bono-on-prolongation — if EVERY actor wants it cleared fast (Ever Given: canal authority, shippers, insurers, salvors all aligned → refloat in days → **fast fade**, and the falsifier is the *salvage/refloat date itself*, not a rate level), it resolves fast; if a **spoiler benefits** from keeping it closed (Red Sea: the Houthis gain legitimacy/leverage, compellence fails → **persistent**). The "% of global trade transiting" is a scare number that's irrelevant when the blockage is days — don't manufacture a structural thesis from a salvage op. Expression rule: within the winning sector, the alpha concentrates in the most **spot-exposed / operating-levered** name (ZIM-type, 2024) — name the expression, never the size (§14).

**The fast confirmation signal (§4):** read the **2-year Treasury yield / Fed-funds-futures sign**. Yield **DOWN** = risk-off/dovish (generic/demand). Yield **UP** = inflation/hawkish (supply). When the classification is ambiguous, the rates market disambiguates it in real time.

---

## 2. BRANCH A — GENERIC / RISK-OFF (the statistical DEFAULT)
Caldara-Iacoviello, the GPR-index creators, on the *average* geopolitical shock (167-pt VAR):
- **Equities −3% on impact, MEAN-REVERTING (~3 months)** — sell the fear, then recover even while the conflict is unresolved.
- **Oil DOWN ~7%** (demand destruction) — *not* up.
- **2y yield DOWN ~20bp** → **DOVISH** repricing: rate-**CUT** odds up, not hike.
- Flight-to-quality: **gold up, Treasuries up, USD up, VIX up.**
- **Prediction:** buy-the-dip; predict *cut* odds up; defensives over high-beta near-term but the index reverts.
- **This REVERSES the two most common reflexes:** "geopolitics = oil up" and "war = rate hikes." For the generic shock, both are wrong.

---

## 3. BRANCH B — SUPPLY / INFLATIONARY (the regime-change tail)
When the event actually disrupts oil supply (Kilian; ECB WP2472):
- **Oil UP; headline + long-run inflation expectations reprice UP** (the inflation-expectations channel moves with a delay and shifts inflation risk premia).
- **Real yields / rate-HIKE odds UP; financial conditions TIGHTEN.**
- **Effect is PERSISTENT** (regime-change, multi-quarter), not a 3-month blip.
- Central bank **REACTS** (hike/hold-hawkish) because expectations threaten to de-anchor — the opposite of the look-through it applies to isolated/demand shocks (§11).
- **This is the branch where "war fears → rate-hike odds up → high-beta re-rating" is CORRECT.** It requires a real supply disruption, not just tension.

---

## 4. THE RATE-EXPECTATIONS FAST CHANNEL (the leading indicator)
The **2y yield / Fed-funds futures move is the fastest transmission** and resolves within hours-to-days, ahead of any actual FOMC move. Its **sign is the branch discriminator**: falling = risk-off/dovish (Branch A); rising = inflation/hawkish (Branch B). The slower **long-run breakevens** channel (Branch B) moves with a delay; when the fast and slow channels initially disagree, weight the fast channel for the near-term trade and the slow channel for the persistence call.

---

## 5. THE EQUITY-DURATION DERATING LAW (the user's mechanism, formalized)
- **ONLY on the hawkish/supply branch (Branch B)** does a rate-hike repricing **derate high-beta / long-duration / growth / unprofitable-tech stocks hardest** — their cash flows are far-dated, so a higher discount rate compresses their multiples most (equity-duration; the **2022 analog**). Rotate to **energy, defense, staples, value.**
- **On the risk-off branch (Branch A)**, long-duration **quality can OUTPERFORM** as yields *fall* — the same "war" headline, the **opposite factor trade**.
- Operational tell for the engine's watchlist: the AI-semis / hyperscaler / neocloud complex (high-duration equity) is a **Branch-B loser and a Branch-A relative winner.** The Iran-rate-path calls (#26/#27) are this rule in action.

---

## 6. SAFE-HAVEN CONDITIONALITY (when the heuristics fail)
- **"war → gold up / bonds up" holds on Branch A** (risk-off, real rates falling).
- **It FAILS on Branch B**: a real-rate hawkish repricing can send **gold AND bonds DOWN even amid war fear** — the discount-rate effect swamps the risk-premium/haven effect. (The tape's 7/4 batch showed exactly this: gold *fell* as hike-bets rose.) Never assume gold rallies on conflict without checking the rate branch first.
- **USD is the one robust haven across both branches** (haven flow on A, rate-differential on B).

---

## 7. HORIZON-MATCHING & THE OIL-SUPPLY-DISRUPTION MASTER RULE
The single best predictor of **LASTING (regime-change) vs TRANSIENT (buy-the-dip)** impact is **whether the event physically disrupts oil supply:**
- **Supply-disrupting** (Gulf War 1990-91, Russia-Ukraine 2022) → evolves into a macro shock, tightens financial conditions, **lingers** → size for multi-quarter/multi-year persistence.
- **Non-supply-disrupting** (Iraq 2003, Gaza 2023, Iran's 2024 attack) → oil *falls* slightly, equities **track above the average recovery path** → buy-the-dip, expect reversion in weeks-to-a-quarter.
This is the same discipline as the Ever-Given horizon-matching lesson: match the trade's horizon to the *physical* duration of the disruption, not the headline's drama.

### 7.1 THE PHYSICAL-FLOW GATE (from the 2026-10-25 resolution sweep — five misses, one shape: #28, #74, #76, #23, #11)
The engine called the oil war-premium *unwinding* off the ANNOUNCEMENT layer: the GL X license, "Persian Gulf flows near pre-war" headlines, a Hormuz "framework," and a one-week Brent drop below $80. The MEASURED physical layer disagreed. Kpler counted about 5 vessels a day on average over 7/15–8/23, against about 130 a day pre-war (−95%). War-risk cover cost 3–10% of hull value against 0.15–0.25% pre-war. Brent went 79 → 89 in one week, settled above $100 by 9/9, and was $116.72 on 10/23. The AAA gasoline average stayed above $4 every day of August. The engine's own #73 ("physics, not politics": HIT) had the right data, and it was never carried over to the price calls.
**RULE:** no oil-premium-UNWIND call (crude down, energy equity over crude, pump price down, "generic branch persists") while measured chokepoint flow is below ~50% of the pre-war baseline AND war-risk premia are above 5× pre-war. A price collapse on announcements alone is a positioning flush inside a physical Branch-B regime (§13e.1 bifurcated tape); expect it to REVERSE at the next physical datapoint.
**Required input on every energy call:** the latest *independent* flow count (Kpler / Vortexa / IMF PortWatch transits) with its date. Official or political flow claims get Crawford–Sobel coarseness (formal §12.4): on 8/12 and 9/1 US claims ran 3–8× above Kpler. When flows and price disagree, flows win on a 2–4 week horizon.

---

## 8. PRICED-IN DISCOUNT
Markets **partially pre-price** geopolitical risk (a statistically significant GPR premium existed 2012-2021; VIX spikes; prediction markets move). **Discount naive surprise:** a telegraphed or materialized-but-expected event moves markets *less*. Check VIX level, prediction-market odds, and whether the event was pre-announced before pricing a big reaction. **Regime-aware caveat:** the GPR equity premium FLIPPED POSITIVE after the Feb-2022 Ukraine invasion — don't hard-code its sign.

---

## 9. DEMAND-DRIVEN "GOOD OIL" & COUNTRY SCALING
- **Good-oil case:** if oil is rising *with* a strong-growth narrative (aggregate-demand shock, Kilian & Park), predict **equities UP and yields UP** — the benign map, NOT the recessionary one. "Oil up = bad for stocks" is false when demand-driven.
- **Country scaling (IMF GFSR):** international military conflict hits **EM equities ~5× harder** (~5pp monthly drop vs ~1pp domestic) and widens **EM sovereign CDS ~180bp vs ~40bp AE**; reserve-weak sovereigns take ~100bp more. Scale the emerging-market and weak-sovereign legs up.

---

## 10. THE DECISION TREE (run on every market-relevant headline)
```
1. Does the event physically disrupt oil SUPPLY (chokepoint / producer / energy sanctions)?
   ├─ YES → is oil rallying?  → BRANCH B (supply/inflationary/hawkish): §3 + §5 derating + §6 haven-fail
   └─ NO / oil flat-or-down   → is oil rising WITH a strong-growth story?
        ├─ YES → §9 good-oil (equities up, yields up)
        └─ NO  → BRANCH A (generic/risk-off/dovish): §2 buy-the-dip default
2. CONFIRM with the 2y-yield sign (§4): down = A, up = B.
3. HORIZON-MATCH (§7): supply-disruption = regime-change/persist; else buy-the-dip/revert.
4. PRICED-IN discount (§8): telegraphed/expected → smaller move.
5. COUNTRY-SCALE (§9): EM / reserve-weak multipliers.
```

---

## 11. CENTRAL-BANK LOOK-THROUGH
Predict the Fed **LOOKS THROUGH** isolated/demand oil shocks (recessionary-and-deflationary in isolation → no hike, even a cut) but **REACTS** to supply shocks that threaten to de-anchor inflation expectations (hike/hold-hawkish). The "in isolation" premise is frequently violated (2022) — so the trigger for a hawkish reaction is **inflation-expectation de-anchoring** (breakevens, survey measures), not the oil price alone.

---

## 12. CROSS-ASSET DIRECTION MAP (the two branches side by side)

| Asset | Branch A: GENERIC / risk-off | Branch B: SUPPLY / inflationary |
|---|---|---|
| Equities (broad) | ↓ ~3%, **mean-revert ~3mo** (buy-dip) | ↓ **persistent** (regime-change) |
| Oil | **↓ ~7%** | **↑** |
| 2y yield / hike odds | **↓ ~20bp (dovish, CUT)** | **↑ (hawkish, HIKE)** |
| Gold | ↑ (haven) | **↓/ambiguous** (real-rate headwind) |
| Treasuries (TLT) | ↑ | ↓ |
| USD | ↑ | ↑ (robust both) |
| VIX | ↑ | ↑ |
| Factor tilt | long-duration **quality outperforms** | **high-beta/growth/long-duration DERATE**; value wins |
| Sector winners | staples, utilities, gold | **energy, defense**, staples, value |
| Sector losers | high-beta cyclicals (short-term) | **tech/semis, discretionary, unprofitable-growth** |

---

## 13. OVERRATED HEURISTICS TO AVOID
- "geopolitics = oil up" — the *generic* GPR shock LOWERS oil (~−7%).
- "war = gold/bonds always up" — FAILS on the hawkish real-rate branch.
- "oil up = bad for stocks" — bullish if demand-driven (good-oil).
- "every headline is a tradable surprise" — partly pre-priced and mean-reverting.
- "all conflicts are regime-change" — most are buy-the-dip *unless oil supply is hit.*

## 13b. CHECKLIST ADDITIONS (append to formal skill §10; run on market-relevant events)
18. **Shock-type gate:** classified as SUPPLY vs DEMAND vs GENERIC before any cross-asset call?
19. **Branch consistency:** does the predicted rate direction match the 2y-yield sign and the branch (A dovish / B hawkish)?
20. **Safe-haven check:** if predicting "gold/bonds up," confirmed it's Branch A (not a Branch-B real-rate repricing)?
21. **Horizon match:** persistence sized to the *physical* supply-disruption duration, not the headline drama?
22. **Priced-in:** discounted for pre-pricing (VIX / prediction markets / telegraphing)?

---

## 13c. EVAL-RUN PATCHES (2026-07-13, from judgment backtest cases 1–3)
- **FX transmission map (was missing — Case 3's only wobble):** commodity FX (AUD/CAD/NOK/CLP) ← terms-of-trade channel, driven by the underlying commodity branch; sanctioned-sovereign FX → down hard and structurally (RUB-2022 pattern: crash → capital-control distortion, not a clean trade); EM FX per §9 scaling (reserve-weak worst); USD haven-robust across branches (§6).
- **Endpoint-dated falsifiers on persistence calls (Case 1):** a multi-quarter directional call must be graded AT its horizon date, tolerating violent counter-rallies en route (2022 Europe-equities pattern). Write falsifiers as "above/below X at date D," never "touches X."
- **Precedence rule (Case 1):** when §12.x information-structure lenses (publicity multiplier, destabilizing-public-info) conflict with doctrine §12.1 capital-committed evidence, **capital-committed wins.** Blood banks forward-deployed beat any bluff-amplification story.
- **One asset per ledger row (Case 3):** separate assets = separate rows, each with its own falsifier. Compound baskets defeat scoring.

## 13d. CPI NOWCAST MODULE (added 2026-07-14 after the June-print autopsy; verified 3-0 to primary sources)
The engine's inflation calls must be NUMERIC (point estimate ± range vs consensus), never sign-only. Built from the verified Knotek–Zaman (JMCB 2017) methodology.

**Primary source — consume directly:** the Cleveland Fed daily inflation nowcast (clevelandfed.org/indicators-and-data/inflation-nowcasting; needs a browser User-Agent — 403 to generic fetchers). Publishes m/m, y/y, and quarterly SAAR point estimates for headline+core CPI/PCE every business day from just TEN free series (5 BLS monthly, 3 BEA monthly, EIA weekly gasoline, daily Brent). Real-time record: beat Blue Chip at every point in the quarter 1999–2022 and the SPF median on headline CPI by 0.39–0.41pp RMSE (bigger edge in volatile samples). **Always use the LATEST pre-print reading** — early-month nowcasts are documented to be materially worse.

**Replication mechanics (if the site is unreachable):** core = trailing-12-month average of core m/m · food = same · gasoline = EIA weekly retail average + daily Brent as leading indicator, then SEASONALLY ADJUSTED (the seasonal factor is decisive in specific months) · headline = time-varying rolling-regression combination. After seasonal adjustment, **gasoline is the dominant swing factor in headline m/m** — the exact arithmetic skipped in the June-2026 miss.

**Weight arithmetic (free, mechanical):** BLS publishes relative importance monthly in every release's Table 1 (motor fuel ≈ 2.981% as of Dec 2025; food 13.512%); between-publication update = Dec weight × (component index_t / index_Dec). A gasoline m/m of ±10% moves headline by ±0.30pp — do this multiplication, never narrate it.

**Y/Y base effects (mechanical, never narrative):** y/y_t = y/y_{t−1} + m/m_t − m/m_{t−12}. Maintain the 12-month drop-off table: whether y/y rises or falls is determined by the month FALLING OUT as much as the month coming in. (The "y/y stays hot" June error dies here.)

**Spike-timing rule (the Hormuz question):** the CPI gasoline index (crowdsourced daily data since 2021) averages prices over the ENTIRE calendar month → a mid/late-month price spike is only PARTIALLY captured in that month's print, with the remainder mechanically landing in the NEXT month. Applied now: the July 7–13 spike hits July CPI (Aug 12 print) pro-rata to elevated-price days × ramp, with the FULL level effect landing in August CPI (Sep print). Two-print spread, mechanically — don't expect the whole shock on Aug 12.

**Trend-vs-tail separation (the inflection-point guard):** the nowcast's documented failure mode is the trailing-average core lagging at inflection points (its survey edge REVERSED at end-2022 disinflation). Always cross-check **Cleveland Fed median CPI and 16% trimmed-mean CPI**: June 2026 worked example — headline −0.4% but median +0.2% and trimmed-mean 0.0% → the plunge was tail/energy, NOT a trend shift. Quote both numbers in every CPI analysis.

**PRE-PRINT RECIPE (run T-7 → print morning):** (1) latest Cleveland nowcast = point estimate; (2) bottom-up gasoline cross-check (EIA calendar-month average × seasonal factor × current weight); (3) y/y base-effect table; (4) compare vs consensus → surprise-direction call with the branch-conditional reaction map; (5) post-print: median/trimmed-mean before ANY "regime" conclusion.

### 13d.1 THE CONFLUENCE STACK (added after the June core miss — the fix is MORE INDEPENDENT streams, not a better single model)
A CPI estimate's conviction = how many *genuinely independent* streams converge. Correlated streams that agree are DOUBLE-COUNTING, not confluence (extremizing rule, contrarian #5). Tag each stream's independence; only extremize on genuine independence.

| # | Stream | Type | Independent of… | Status (verified 2026-07-14) |
|---|---|---|---|---|
| 1 | Cleveland Fed nowcast | model (trailing-MA core + oil) | — | LIVE. FAILURE CONFIRMED: core = recursive 12-mo moving average, no high-freq input → structurally lags at disinflation inflections (the June miss; its survey edge reversed at end-2022 disinflation). |
| 2 | Bottom-up gasoline arithmetic | mechanical (EIA weekly × weight) | correlated w/ #1 on the oil leg — do NOT double-count energy | LIVE. Crude ≈ **51-57% of pump price**; pass-through FAST up ("rockets & feathers"). |
| 3 | Median / 16% trimmed-mean CPI | trend-vs-tail guard | independent of headline mix | LIVE |
| 4 | **Shelter: Zillow ZORI-based CPI-shelter nowcast** (the CORE FIX) | independent leading indicator | **fully independent of #1-3** | **LIVE — plug it in.** Zillow publishes a monthly OER/rent m/m estimate from ZORI (Ball & Koh NBER WP 34113). June-2026: OER **+0.27% m/m**, Rent **+0.26%**, "shallow-deceleration, no cliff." Mechanism: **~21% renewal pass-through** (mkt rent +10% → renewing tenant +2.1%) = why shelter lags slowly. BLS NTRR leads CPI rent ~4 quarters but is QUARTERLY + **paused since Apr-2026** → trend-confirmer only, not a monthly input. |
| 5 | **Prediction markets / fixings — as an UNCERTAINTY GAUGE, not a whisper** | market distribution | independent of models AND consensus | **LIVE but RE-SPEC'd (premise corrected).** Peer-reviewed (Kalshi: Angelini 2026; Goel IREF 2026): the market-implied MEAN does NOT beat consensus as a point forecast and predicts surprise *direction* only weakly (57% hit). Use the implied **WIDTH to size the range / tail risk**, NOT to call direction. Kalshi has live headline/core m/m + y/y markets (resolve Aug-12) but the m/m market is thinly traded (~$6k) — least reliable exactly where you want it. |
| 6 | Consensus (Bloomberg/DJ) — as the benchmark to surprise against | human forecasters | partly correlated (anchoring) | **PARTIAL — FAILED verification.** The "±0.1pp typical error / fat-tails / energy-month bias" claims did NOT verify. Keep consensus as the *level to beat*, but do NOT cite a calibrated error distribution as established. |

**Rule:** the June core miss happened because streams #1-3 are all correlated on the *headline/energy* axis and NONE independently tracks *shelter*. Now #4 (ZORI shelter) is the independent core voice. **Honest limit:** even #4 had a "shallow-deceleration, +0.27% OER" view for June while actual core printed 0.0% — so the June softness was likely BROADER than shelter (used cars/apparel/airfares), and #4 de-correlates the core estimate without guaranteeing every inflection. Confluence is real only when streams disagree in their *inputs*: when #1 (model) + #4 (shelter-lead) + #3 (trend guard) agree, extremize; when they diverge, the divergence flags which component is inflecting. Size the RANGE with #5's implied width, the LEVEL with #1/#4, the surprise vs #6. Generalizes beyond CPI: every high-conviction prediction names its confluence stack and tags each stream's independence (doctrine §10.12 + extremizing #5). **Energy pass-through / live Hormuz:** CPI gasoline is a calendar-MONTH average → the July 7-13 spike lands only partially in July CPI (Aug-12 print), more fully in August CPI (Sep) — do not expect the full oil shock on Aug 12.

**Honest gaps (failed verification, sourced separately or flagged):** CPI fixings/swaps accuracy vs consensus; the consensus-error distribution (the "±0.1pp typical" figure is UNVERIFIED); NTRR/ZORI shelter pass-through coefficients; quantified crude→pump cents-per-gallon lags. Do not cite these as established.

## 14. SOURCES & CAVEATS
**Sources:** Caldara & Iacoviello, *Measuring Geopolitical Risk* (Fed IFDP 1222 / AER 2022) — GPR baseline (eq −3%/revert, oil −7%, 2y −20bp). Kilian & Park (2009, *Int'l Econ Review*) + Kilian (RBA 2009) — supply-vs-demand decomposition & stagflation/look-through logic. Venditti & Veronese, ECB WP2472 (2020) — daily supply/demand identification & inflation-expectations channel. ECB Economic Bulletin (2026) & SSGA (2026) — oil-supply-disruption master rule & buy-the-dip regularity. IMF GFSR (April 2025, Ch.2) — country/EM scaling, CDS widening, persistence, GPR premium.

**Caveats (bind these):** (1) **Direction robust, magnitude contested** — the −3%/−7%/−20bp figures are pre-2022 priors; treat as directional anchors, not point forecasts, and down-weight in a more inflation-reactive regime. (2) **US vs rest** — the scarcity-shock *direct* equity effect is muted for the US (S&P tech weighting) but significant for Europe/Japan/China. (3) **Persistence tracks event TYPE, not magnitude** — a smaller country-specific shock can be *more* persistent (2yr) than a larger global one (1 quarter). (4) **Buy-the-dip regularity carries survivorship bias** — "equities higher 1-2yr later" is an average *conditioned on no catastrophe*; the failure cases (1973 embargo, 1990 Gulf, 2022 Ukraine) ARE the supply/macro tail. (5) **Refuted, do not hard-code:** oil +30%/S&P −20% ECB magnitudes; a rate-DECLINE under supply shocks (surviving evidence says supply shock → yields UP); MDPI regime-sign-reversal claims. (6) **Open:** the exact headline-stage decision boundary for supply-disruption (before oil confirms), and a quantitative bp-yield → factor-multiple-compression mapping — both flagged for the next research pass; until then this layer is directional + conditional, not sized.

### 13d.2 Base-Effect Identity Check (MANDATORY before quoting any y/y figure)
Lesson from #46 (PPI y/y est 6.2-6.4 vs actual 5.5) and the June CPI y/y - the same too-high shape twice = systematic. Never extrapolate y/y from the prior month's y/y plus the m/m estimate alone. Compute the identity explicitly: new y/y = old y/y + (entering month m/m) - (dropped year-ago month m/m). The dropped base month dominates when the year-ago period had a large print (energy spikes, reopening surges). If the dropped month's m/m is not known, SAY SO and widen the y/y range asymmetrically toward the base effect - do not publish a point y/y. The m/m estimate is the engine's real skill; the y/y is arithmetic and should never be the miss.

### 13e. Event-Time vs Regime-Time (from the 7/21 semis decoupling)
Regime pressure (war branch, rate derate) governs drift; a DECISIVE SCHEDULED CATALYST within ~24-48h governs direction, and the two can point opposite ways. Within the catalyst window, the market trades the catalyst's EXPECTED outcome (front-running the confirm), not the regime - SMH +4.1pct WHILE Brent broke 90 and TLT fell. Rules: (1) inside 48h of a checkpoint, damp the branch-beta on directly-exposed assets and weight the catalyst distribution instead; (2) a pre-catalyst move IS information - it reveals the market's implied odds for the print (compare to the engine's; large gaps are the trade); (3) do not count regime-contradicting moves inside the window as evidence against the regime call - score them against the catalyst call.

### 13e.1 Bifurcated-Tape Rule (both tails can fire at once)
When escalation facts and de-escalation narrative arrive together, assets split by what is LOAD-BEARING for each: physical markets (oil, tankers, gold) trade the flows; equity/rates trade the narrative + positioning. A bifurcated tape is NOT incoherent - read each asset against its own driver, and expect the two to reconverge at the next physical datapoint (flows) or scheduled print. Positioning amplifies the narrative side: heavy hedging into a weekend makes any non-catastrophic Monday a squeeze regardless of regime.

### 13e.2 Single-Confirmation Beta Discipline
One confirming observation (SMH -4.2pct on 7/13 strike day) is not a stable beta estimate. Any cross-asset sensitivity used in fusion topdown scores must carry a confidence tag (n of observations); n=1 betas get half-weight until a second independent confirmation, and a contradicting observation (7/21) forces an immediate re-estimate, not a rationalization.
