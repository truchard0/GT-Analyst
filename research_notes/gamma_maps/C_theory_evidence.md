# Dealer Gamma Maps: Theory and Evidence — A Literature Review

*Prepared 2026-11-18 as background for a guide that will sit beside vendor (Skylit) dealer-gamma heatmaps. Read-only research; every claim is cited. Items marked **UNVERIFIED** could not be confirmed against a primary source in this session. Where only a working-paper draft or a secondary summary was readable, the review says so.*

**Evidence grades used below.** **A** = peer-reviewed, signed or exchange-identified position data, replicated or corroborated by independent work. **B** = peer-reviewed or strong working paper, but relying on the open-interest sign assumption or a single sample. **C** = practitioner / vendor white paper, single episode, or non-peer-reviewed preprint. **D** = asserted in practice, no located test.

---

## 0. Summary of findings

1. The core mechanism is sound and old. If the aggregate delta-hedger book is short gamma, re-hedging trades *with* the price move; if long, *against* it. Feedback models (Jarrow 1994; Frey & Stremme 1997; Sircar & Papanicolaou 1998; Schönbucher & Wilmott 2000) all predict that underlying volatility falls in the hedgers' net gamma, provided the underlying market is not perfectly liquid (summarised in Pearson, Poteshman & White 2006 draft of Ni et al. 2021).
2. The best evidence (grade A/B) supports **second-moment** readings: higher dealer net gamma goes with lower subsequent realised volatility and more intraday reversal; negative gamma goes with higher volatility and intraday momentum (Ni, Pearson, Poteshman & White 2021; Baltussen, Da, Lammers & Martens 2021; Barbon & Buraschi 2021; Adams et al. 2026; Amaya et al. 2025).
3. The effects are **modest in size**. Exchange-signed SPX data put the *maximum* impact of market-maker gamma at +3.3 vol points on daily annualised realised volatility over July 2020–June 2023, against a 4.5-point standard deviation of daily changes from all causes (Amaya, Garcia-Ares, Pearson & Vasquez 2025).
4. **Pinning** at expiry is documented in single stocks (Ni, Pearson & Poteshman 2005) and in S&P 500 futures (Golez & Jackwerth 2012), but the index result runs *opposite* to what dealer delta hedging alone predicts, and one recent non-peer-reviewed test finds no SPX pinning in 2016–2025 (Elms 2026, grade C).
5. The **0DTE** literature mostly finds that, on average, 0DTE positions *dampen* index volatility because market makers are typically net long gamma (Adams et al. 2026; Cboe/Xu 2023, 2025; Amaya et al. 2025). Brogaard, Han & Won find the opposite on a volume-share measure. This is contested, not settled.
6. **No located peer-reviewed support** for: GEX predicting the *direction* of returns; "call wall/put wall" strikes as support/resistance on non-expiry days; the zero-gamma "flip" as a precise trigger level; or vanna-driven rallies as a scheduled effect. Charm has one strong recent result, confined to monthly AM-settled SPX expiries (Baltussen, Terstegge & Whelan 2024).
7. The biggest practical risk is **measurement**: maps built from end-of-day open interest plus a "customers long puts, short calls" sign convention can get the sign of dealer gamma wrong. Exchange-signed data show SPX market makers are *typically long* gamma, not short (Amaya et al. 2025; Adams et al. 2026), which contradicts the common vendor assumption that dealers are structurally short puts.

---

## 1. Mechanics

### 1.1 Delta hedging, gamma and feedback

A market maker who sells an option and wants to remain delta-neutral holds −Δ·(contracts)·(multiplier) of the underlying. Gamma Γ = ∂Δ/∂S is the rate at which that hedge must change. For a short-gamma book, a rise in S makes the book shorter delta, so the hedger buys; a fall makes it longer delta, so the hedger sells. Hedging is pro-cyclical. A long-gamma book does the reverse and is counter-cyclical (Pearson, Poteshman & White 2006, §2; SqueezeMetrics 2017, pp. 3–6).

The formal literature models this as a price-impact feedback: with an imperfectly elastic underlying, the instantaneous volatility becomes σ·v(Γ), with v decreasing in the hedgers' aggregate gamma (Frey & Stremme 1997; Sircar & Papanicolaou 1998; Schönbucher & Wilmott 2000; Platen & Schweizer 1998; Jarrow 1994; Frey 1998 — all as summarised in Pearson, Poteshman & White 2006, pp. 3–8). The prediction is about **variance and autocorrelation**, not about the sign of the next return. That distinction matters for how maps should be read (§5).

Two premises are load-bearing and both can fail: (i) the hedgers actually delta-hedge, continuously enough to matter, and (ii) the underlying's liquidity is finite relative to hedge size. On (i), account-level KOSPI 200 data show only 4 of 43 market makers consistently delta-hedged; most manage risk by rebalancing option inventory within minutes (Hu, Kirilova, Muravyev & Ryu, "Options Market Makers," working paper, R&R at *JFE* per author page — **UNVERIFIED** status). On (ii), the effects in Barbon & Buraschi (2021) and Ni et al. (2021) are concentrated in less liquid underlyings.

### 1.2 Estimating dealer net gamma from open interest

**The standard OI-based estimator.** SqueezeMetrics' white paper (March 2016, revised December 2017) formalised the practitioner Gamma Exposure (GEX) measure with four assumptions: (1) every option is facilitated by a delta-hedger; (2) calls are sold by investors and bought by market makers; (3) puts are bought by investors and sold by market makers; (4) market makers hedge exactly to Black–Scholes delta. Per strike and expiry, GEX = Γ × OI × 100 for calls and Γ × OI × (−100) for puts, summed across all strikes and expiries (SqueezeMetrics 2017, pp. 4–5). Baltussen et al. (2021, eqs. 13–15) adopt exactly these four assumptions, multiply by the index level, and divide by S&P 500 market value. They verified that SqueezeMetrics' series matched their own OptionMetrics computation over 2002–2017 "virtually identically" (fn. 7).

**Why the sign assumption fails.**
- *It is index-specific at best.* Gârleanu, Pedersen & Poteshman (2009, *RFS* 22(10):4259–4299) find end users net **long** index options, concentrated in OTM puts, but net **short** single-stock options. So the "dealers short puts" logic does not carry over to single names, where dealers are on average long options (also noted by Golez & Jackwerth 2012 WP, p. 2).
- *It ignores OTC and other venues.* Baltussen et al. (2021, fn. 8) state plainly that their measure omits OTC positions and actual end-user positions. They find NGE was positive on 3,158 of 6,088 days (1996–May 2020), which they say may reflect the data choice.
- *Exchange-signed data contradict it in SPX.* Using Cboe trade records that identify each side's capacity, Amaya et al. (2025) find the aggregate SPX/SPXW market-maker gamma is "typically positive" though "often negative" (July 2020–June 2023). Adams et al. (2026) use Cboe Open-Close Volume Summary data and find market makers keep positive net gamma through 0DTE expiration days. Cboe's own analysis finds median 0DTE market-maker net gamma at 3:30 pm of +$173mm, with an interquartile range of about −$1.1bn to +$2.4bn (Xu, Cboe, 8 Sept 2023).
- *Structural flows change the mix.* Covered-call/overwriting and collar programs make investors net call sellers (SqueezeMetrics' own justification for assumption 2), but the share of index calls bought outright by speculators, and of puts *sold* by yield programs, varies over time. No located paper quantifies how much this rotation biases OI-based GEX (**UNVERIFIED** magnitude; grade D).

**Call/put convention.** Under the OI convention, calls contribute positive and puts negative dealer gamma, so a strike-level map is mechanically positive above spot (call-heavy) and negative below (put-heavy) in a typical SPX surface. Much of the "positive gamma above, negative below" picture therefore follows from the convention rather than from observed positions. Signed-data vendors avoid this. The guide should state which convention the vendor uses; this review could not verify Skylit's methodology (**UNVERIFIED**).

### 1.3 Aggregation and units: "$ gamma per 1% move"

Different papers and vendors scale differently, so numbers are not comparable across sources:

| Measure | Formula (dealer sign sᵢ, multiplier m=100) | Source |
|---|---|---|
| Share gamma per 1-point move | Σ sᵢ Γᵢ OIᵢ m | SqueezeMetrics 2017 |
| Dollar delta change per 1-point move, scaled by market cap | Σ sᵢ Γᵢ OIᵢ m S / MV | Baltussen et al. 2021, eq. 15 |
| Dollar delta change per 1% move | Σ sᵢ Γᵢ OIᵢ m S² × 0.01 | Industry convention; Cboe/Xu 2023 reports gamma "per 1% SPX move" |
| Fraction of index shares to trade per 1% move ("hedging needs") | as above ÷ (MV) | Adams et al. 2026 (≈1% of S&P 500 shares on average) |

*Illustrative arithmetic, not data:* an SPX strike with OI 10,000, Γ = 0.01 per index point and S = 6,000 gives 0.01 × 10,000 × 100 × 6,000² × 0.01 ≈ $3.6bn of delta change per 1% move. Gamma itself must be computed from an implied-volatility input, so a vendor's choice of IV (strike-specific vs. ATM, quote snapshot time) changes the number (Amaya et al. 2025 compute IV from one-minute BBO midpoints).

Aggregation across expiries weights near-dated, near-the-money options heavily, because Black–Scholes ATM gamma ≈ φ(0)/(Sσ√T) grows like 1/√T (standard result). Ni et al. (2021) and Barbon & Buraschi (2021) normalise by shares outstanding or dollar volume to compare across stocks. A map that shows raw dollar gamma by strike will be dominated by the nearest expiries.

### 1.4 The zero-gamma ("flip") level

Practitioners define the flip as the spot level S* at which re-computed total dealer gamma, holding OI and IV fixed, crosses zero. No peer-reviewed paper located here tests S* as a level. The academic literature conditions on the **sign** of aggregate gamma at the current spot (Baltussen et al. 2021, Table 7; Barbon & Buraschi 2021). The flip is therefore a model-dependent extrapolation of a sign variable that has support, not an independently validated level (grade D). One practitioner analysis (OptionMetrics, quoted in Mannix, *Risk.net*, 25 Oct 2022) argues volatility is highest when dealer gamma is *near zero*, not merely negative, because dealers then hedge less and supply less liquidity. No numbers are given in the article (grade C).

### 1.5 Vanna and charm

- **Vanna** = ∂Δ/∂σ. When implied volatility falls, the delta of OTM puts held short by dealers shrinks in magnitude, so dealers buy back short hedges; this is the practitioner "vanna rally." **No peer-reviewed test was located.** The most concrete figure found is a press estimate attributed to OptionMetrics of nearly $1bn of vanna-driven buying after a VIX move from 28 to 38 (single episode, grade C; **UNVERIFIED** primary). Vendor pages note vanna depends on the volatility model used.
- **Charm** = ∂Δ/∂t. Close to expiry, OTM deltas decay to 0 and ITM deltas to ±1, so a hedged book's delta drifts even with spot unchanged. Baltussen, Terstegge & Whelan ("The Derivative Payoff Bias," Sept 2024 version, presented AEA 2025) find that over 2003–2021 the S&P 500 Special Opening Quotation on third Fridays exceeds the prior close by 18 bps on average. Dealers' net charm at Thursday close implies at least $280mm of overnight buying, against an observed $306mm order imbalance. Net charm predicts the overnight return with t = 2.99 and R² = 3%, robust to controlling for net gamma, and the sign flips (−6 to −11 bps) when dealer charm is positive. They estimate a $3.5bn per year wealth transfer in SPX options (grade B). Dim, Eraker & Vilkov (2024) reportedly find 0DTE market-maker charm exposure affects intraday volatility (as cited by Baltussen, Terstegge & Whelan 2024; the original now subsumed into Adams et al. 2026).

### 1.6 What changes into expiry

As T → 0, ATM gamma and charm explode while OTM gamma collapses. Gamma becomes concentrated at the strikes nearest spot, which is the basis for pinning models. Avellaneda & Lipkin (2003, *Quantitative Finance* 3(6):417–425) derive a singular drift toward the strike, with a positive probability of pinning, when (a) open interest is unusually large and (b) delta hedgers are **net long** options. Net short hedgers produce anti-pinning. Jeannin, Iori & Samuel (2008, *Quantitative Finance* 8(8):823–831) extend this with simulated order flow. After expiry the expiring gamma disappears at once, which is why maps can change sharply day to day. Adams et al. (2026) show that the gamma that matters on 0DTE days is mostly *accumulated earlier* in longer-dated contracts that roll into 0DTE status: about 25 bps of hedging needs from pre-existing positions against 3 bps from same-day 0DTE trades.

---

## 2. Evidence on effects

### 2.1 Pinning at expiry

- **Single stocks — Ni, Pearson & Poteshman (2005, *JFE* 78(1):49–87).** On expiration dates, optionable stocks' closes cluster at strikes. Returns are altered by at least 16.5 bps per expiration on average, about $9bn of aggregate market-cap shift. Attributed to market-maker hedge rebalancing and to manipulation by firm proprietary traders (abstract figures as reported by CXO Advisory's summary of the 2004 SSRN version). Clustering occurs when delta-hedgers are net *purchasers* and de-clustering when net *writers*, consistent with Avellaneda–Lipkin (Pearson, Poteshman & White 2006, pp. 2–3). Sample period and data source not re-read here (**UNVERIFIED** detail). Grade A for existence in its sample.
- **S&P 500 futures — Golez & Jackwerth (2012, *JFE* 106(3):566–585).** In the 2010 working paper, 13.56% of serial-expiry futures settlements fall within $0.25 of a strike against 10% expected under uniformity (Aug 1987–Nov 2009). The figure is 17.89% for Jan 1998–Nov 2009, and the effect is asymmetric, stronger from above (WP Table 1, pp. 16–17). Crucially, dealers are short index options, so delta-hedge time decay alone predicts *anti*-pinning. The authors find that effect but overcompensated by investors' reselling and early exercise of ITM options. Before SPX expiries they find anti-cross-pinning; notional shift at least $115mm per expiration (published abstract). Grade B: pinning exists, but **not** by the mechanism maps usually imply.
- **Theory/anecdote.** Krishnan & Nelken (2001, *Risk*) report pinning in Microsoft and a Brownian-bridge model (as described by later papers; **UNVERIFIED** primary).
- **Failed or contrary.** Elms (2026), "From Pinning to Amplification…," SSRN 6564078 / Zenodo, finds no SPX pinning across 2,294 days in 2016–2025. Four of five tests are null, and high-OI days show 16.2% wider ranges (p = 0.0003). It is self-published, uses SPY OI as a proxy and makes no multiple-testing correction (as described by FirmTape's literature sweep and a Substack repost; grade C, **UNVERIFIED** primary). An NSE study of five stocks also found no pinning (CXO Advisory summary of a 2004 SSRN paper; grade C).

**Reading:** pinning is a real but conditional, small, expiry-only effect. In single names it requires dealers net long options and large OI. In the index, the sign of the dealer mechanism predicts the opposite of pinning, and the post-2016 evidence is weak.

### 2.2 Dealer gamma and volatility

- **Ni, Pearson, Poteshman & White (2021, *RFS* 34(4):1952–1986).** First pervasive (non-expiry) evidence. Using CBOE data that classify open interest by trader type (the 2006 draft uses all CBOE equity options 1990–2001), the net gamma of likely delta-hedgers is significantly *negatively* related to the next day's absolute stock return. In the draft, a one-s.d. gamma shock moves absolute return by 37 bps against a 310 bps mean, so about 12% of daily absolute return is attributable to hedge rebalancing. Hedge-rebalancing volume explains about 14% of average stock volume per s.d. The result holds for large and small stocks, both halves of the sample and excluding expiration week (Pearson, Poteshman & White 2006, pp. 4–5). The published abstract adds an effect on the probability of large moves. Published magnitudes not re-read (**UNVERIFIED** that they match the draft). Grade A: signed data, top journal.
- **Barbon & Buraschi (2021), "Gamma Fragility" (WP, SSRN 3725454, rev. 19 Mar 2021).** Sample of large stocks and indices (about 300 underlyings with largest dollar OI, 1996–2017, per press coverage). One s.d. of gamma imbalance lowers single-stock absolute daily returns by 5–25 bps and index returns by more than 20 bps (about 20% of a s.d.). A one-s.d. fall in gamma widens the daily high–low range by about 16 bps. Gamma lowers intraday return autocorrelation by about 1.5–2% per s.d. Flash crashes are more frequent and larger on negative-gamma days, and effects are concentrated in illiquid names (figures from the BSIC summary and author page; t-statistics up to −5.07 per FirmTape; grade B, **UNVERIFIED** against the PDF, which could not be text-extracted here).
- **Amaya, Garcia-Ares, Pearson & Vasquez (2025), "0DTE Index Options and Market Volatility: How Large is Their Impact?"** (WP, 25 Jan 2025, hosted by Cboe). They build minute-by-minute SPX/SPXW market-maker positions from Cboe trade records with trader capacity (July 2020–June 2023) and fit GARCH and linear models. Conditional variance falls with lagged market-maker gamma. The median effect *reduces* daily vol by 0.08 points. The **maximum** gamma-induced *increase* is 3.3 points of annualised daily realised volatility and 6.4 points for 30-minute windows, against all-cause daily-change s.d. of 4.5 points and a 30-minute maximum change of 63.4 points. The authors judge this "not large." Grade A: signed exchange data, counterfactual simulation.
- **SqueezeMetrics (2017).** Following the top GEX quartile, 1-day SPX s.d. was 0.55%, versus 0.85% for the second-highest quartile (sample unstated). The paper shows a scatter of returns widening "exponentially" below zero GEX. Vendor, unaudited, no standard errors (grade C).
- **FX — Anderegg, Ulmann & Sornette, SNB Working Paper 2019-03.** From DTCC trade-repository data, dealer gamma near −$1,000bn corresponds to about 0.7 vol-point higher EURUSD and 0.9 higher USDJPY volatility. That is a small effect in a deep market (grade B; a journal version is **UNVERIFIED**).

### 2.3 Gamma and intraday momentum / reversal

- **Baltussen, Da, Lammers & Martens (2021, *JFE* 142(1):377–403).** More than 60 futures across asset classes, 1974–2020. The rest-of-day return predicts the last-30-minute return everywhere, and the effect reverts over subsequent days. For the S&P 500 (Jan 1996–May 2020; 2,930 negative-NGE vs 3,158 positive-NGE days), the slope of last-half-hour on rest-of-day return is **6.63** (t = 4.78, adj. R² 3.58%) on days after negative NGE, against **0.82** (t = 1.03, R² 0.05%) after positive NGE; coefficients ×100 (Table 7). Interacted regressions confirm stronger momentum the more negative NGE (Table 8). Leveraged-ETF rebalancing provides a second hedging-demand channel (Table 9; Cheng & Madhavan's estimate that LETF rebalancing was 16.8% of market-on-close volume on a 1% day, cited p. 389). Caveat: NGE uses the OI sign assumption (§1.2). Grade B+: top journal, large sample, but assumption-based gamma.
- **Barbon, Beckmeyer, Buraschi & Moerke (2021/2022), SSRN 3925725 / SFI RP 22-40.** Large negative (positive) gamma imbalance relative to dollar volume gives end-of-day momentum (reversal) in single stocks. The effect reverts at the next open, and LETF flows attract more liquidity provision and are shorter-lived (abstract; grade B).
- **Adams, Dim, Eraker, Fontaine, Ornthanalai & Vilkov (2026), "Do S&P 500 Options Increase Market Volatility? Evidence from 0DTEs"** (SSRN 5641974, draft 15 July 2026). Higher market-maker hedging needs predict stronger E-mini order-flow reversals for about 30 minutes, and weaker or negative hour-to-hour momentum. One s.d. of 0DTE net gamma lowers next-10-minute realised vol by about 23 bps annualised, persisting about an hour. The authors state this second part is predictive, not causal. Grade A−.
- **Robustness of the underlying anomaly.** Gao, Han, Li & Zhou (2018, *JFE* 129(2):394–414) report the first-half-hour → last-half-hour predictive R² of 1.6% in-sample and 1.2% out-of-sample (SPY, 1993–2013). Li, Sakkas & Urquhart (2022) find it in 12 of 16 markets. Rosa (2022, *J. Futures Markets* 42(12)) finds a related overnight-return signal disappears out of sample. No located study tests whether the gamma-conditional effect survived post-2020 0DTE growth; Adams et al. (2026) find market makers mostly *long* gamma in that period, which would predict weaker momentum (grade: open question).

### 2.4 The 0DTE literature

| Study | Data | Finding |
|---|---|---|
| Xu, Cboe "Volatility Insights" (8 Sept 2023) | Cboe signed SPX 0DTE positions by capacity | Avg intraday MM net gamma $170–670mm; hedging ≈0.04–0.17% of daily S&P futures liquidity; no rise in 2σ gap moves. Caveat: excludes SPY/ES options and other expiries. |
| Xu, Cboe "0DTEs Decoded" (2 May 2025) | Same | Customer flow "extremely balanced"; MM gamma hedging ≤0.2% of SPX daily liquidity; ~4% of 0DTE trading is naked short (search excerpt; **UNVERIFIED** full text). |
| Adams, Fontaine & Ornthanalai (2024), SSRN 4881008 | Intraday SPX volume 2019–2023 | Index vol 60–90 annualised bps lower on 0DTE days (abstract). |
| Dim, Eraker & Vilkov (2024), SSRN 4692190 | OI gamma | No evidence 0DTE OI gamma propagates or unconditionally raises vol; higher short-term gamma → lower intraday vol (secondary summaries). |
| Adams et al. (2026), SSRN 5641974 (merges the two above) | Cboe Open-Close Volume Summary, 10-min, Jan 2018–Dec 2024 | 10-min realised vol 61 bps lower (≈7% of mean) on 0DTE days, identified from Tue/Thu expiries before May 2022; effect vanishes once daily expiries begin; hedging-needs→vol multiplier ≈ −4. |
| Amaya et al. (2025) | Cboe trade records with capacity | Max gamma-induced vol increase +3.3 pts daily, +6.4 pts 30-min. |
| Brogaard, Han & Won (2023–2025), SSRN | 5-min SPY vol, 0DTE share; instrumented by staggered SPXW introductions | 1 s.d. ↑ 0DTE volume ≈ +14% daily vol (Bloomberg coverage); 0DTE share predicts vol better than longer-dated volume. Identification critiqued by Adams et al. (2026). Grade B−, **UNVERIFIED** magnitudes. |
| Beckmeyer, Branger & Gayda (2023), SSRN 4404704 | Retail flows | >75% of retail SPX option trades are 0DTE; ~60% of retail 0DTE losses are transaction costs (via Bank Underground). |

The weight of signed-data evidence is that 0DTE positions, on average, add long gamma to dealers and dampen index volatility. The tail case, when dealers are short, raises volatility, but by amounts within normal daily variation (Amaya et al. 2025). Concerns that 0DTE unwinds could turn a 5% fall into 25% (JPMorgan, March 2023, via Bank Underground) are not supported by any located estimate.

### 2.5 Central-bank, BIS and IMF notes

- **BIS Quarterly Review, March 2018, Box A (Sushko & Turner).** Concerns VIX ETP rebalancing on 5 Feb 2018, not option-dealer gamma. Leveraged and inverse VIX ETPs (about $4bn of assets) had to buy VIX futures into the close. Front-running from about 15:30 and a feedback loop followed: 115,862 VIX futures traded in one minute at 16:08, XIV lost 84%, and VIX-futures dealers hedged by shorting E-minis. The box is the canonical official account of a *convexity-driven* feedback loop, and shows that small vehicles can amplify jumps.
- **IMF GFSR, April 2026 (Ch. 1).** Classifies dealer-gamma regimes as stabilising (positive) or amplifying (negative). Says short-gamma regimes "can occur frequently" and exert net downward pressure on those days, on proxy measures. Puts 0DTE at about 60% of S&P 500 option volume, up from about 40% two years earlier, and lists leveraged ETFs and short-gamma regimes as sell-off amplifiers. A policy assessment using proxy (assumption-based) measures; grade B/C for the gamma claims.
- **Bank of England, Bank Underground (Xiao, 4 Dec 2024).** Surveys the 0DTE debate. Notes conflicting studies and that intraday risk is not explicitly captured in Pillar 1 capital. No new estimate.
- **Swiss National Bank WP 2019-03.** See §2.2 (FX).
- **Federal Reserve.** No FEDS Note or Financial Stability Report box specifically estimating dealer-gamma effects was located (absence **UNVERIFIED**; the Fed Board hosted presentations of Adams et al. per their acknowledgements).

---

## 3. Single stocks versus index

**Sign of the dealer book differs.** End users are net long index options (especially OTM puts) but net short single-stock options (Gârleanu, Pedersen & Poteshman 2009). Single-name dealers are therefore more often *long* gamma, which is the condition for pinning in Avellaneda–Lipkin, and this fits the single-stock clustering in Ni, Pearson & Poteshman (2005). Applying the index sign convention to single names is unsupported.

**Evidence in single names.**
- Volatility falls with hedgers' net gamma across large and small stocks (Ni et al. 2021).
- Barbon & Buraschi (2021) find the momentum effect needs illiquidity and is strongest in the least liquid names.
- O'Donovan, Yu & Zhang (WP 2023) find that dealers net long options supply liquidity to the underlying stock and net short dealers withdraw it, more so where other liquidity supply is limited. They use proprietary exchange data by trader type (abstract only; grade B, **UNVERIFIED** details).
- Lipson, Tomio & Zhang (WP March 2023), using Robinhood's January 2018 zero-commission options launch as a shock, find stocks with the largest rise in retail option trading had about 4% larger volatility increases. Effects were greater with larger buy/sell imbalance and market-maker inventory (secondary coverage; **UNVERIFIED** magnitudes).
- *GameStop, January 2021.* The SEC staff report (18 Oct 2021) found put buying dominated and market makers were *buying* calls, and said this was not by itself consistent with a gamma squeeze. Mitts, Battalio, Brogaard, Cain, Glosten & Kochuba (CLS Blue Sky, 22 Feb 2022) argue hedging direction, not put/call identity, is what matters, and that a large volume looked like hedging. Both sides concede the magnitude cannot be measured without deanonymised data. This is an instructive case of the sign problem.

**Earnings.** No peer-reviewed test of dealer-gamma maps around earnings was located (gap; grade D). The closest evidence is de Silva, Smith & So ("Losing is Optional," *Review of Finance* 2025). Retail investors heavily *buy* options before high expected-volatility announcements, the demand is absorbed mainly by market makers, and retail loses 5–9% on average (10–14% for high-EAV events). By inference only, dealers in retail-heavy names tend to be short gamma into earnings, but this inference is **UNVERIFIED**. Pre-earnings gamma also collapses with the post-announcement implied-volatility crush, so OI-based maps computed before the print overstate post-print gamma (mechanical; untested).

**Contract design.**
- SPX options are European and cash-settled. Standard monthlies are AM-settled off the opening print (SOQ); SPXW weeklies and dailies are PM-settled at the close (Cboe SPX specifications).
- Single-stock and SPY/QQQ options are American and physically settled. Early exercise (around dividends especially) removes OI before expiry, and assignment uncertainty at expiry ("pin risk") creates weekend stock exposure for writers.
- Index hedging is done largely in E-mini futures (Adams et al. 2026), and the Cboe estimates are scaled to futures liquidity. Single-stock hedges go into the cash stock, which is far less deep relative to option OI in small names. This is consistent with stronger effects in illiquid stocks (Barbon & Buraschi 2021).
- The AM/PM split means monthly SPX gamma and charm unwind overnight into the open (Baltussen, Terstegge & Whelan 2024), while 0DTE gamma unwinds into the close.

---

## 4. Measurement problems

1. **OI is end-of-day.** Exchange OI updates overnight, so intraday position changes, including most 0DTE activity opened and closed the same day, never appear in OI. Adams et al. (2026) and Amaya et al. (2025) needed intraday signed data (10-minute and 1-minute) to study 0DTE, and found that same-day 0DTE trades add only about 3 bps of hedging needs against about 25 bps from pre-existing positions.
2. **Who is long is unknown without signed data.** OI cannot separate a market maker short 5, flat, or long 5 on the same OI of 5 (vendor illustration; mechanical). Signed sources include Cboe Open-Close Volume Summary (by origin: customer, professional customer, broker-dealer, market maker; by buy/sell and open/close). It covers only Cboe venues, and its OI fields come from third-party vendors (Cboe DataShop). Others are the CBOE trader-type OI data used by Ni et al. (2021) and the trade-capacity records in Amaya et al. (2025). Trade-side inference (ask = customer buy) is an alternative with known misclassification at the midpoint, where SqueezeMetrics (2017) notes most SPX trades occur.
3. **Venue and product fragmentation.** SPX, SPXW, SPY, XSP, ES options and OTC all hedge the same risk. Cboe's 2023 analysis explicitly excludes SPY/ES options and other expiries. Baltussen et al. (2021) exclude OTC.
4. **Hedging behaviour is assumed.** Black–Scholes delta, full hedging and no hedging bands are assumptions (SqueezeMetrics 2017, assumption 4; Adams et al. 2026, §3.1). Market makers may hedge with other options rather than futures (Xu 2023) or barely delta-hedge (Hu et al., KOSPI).
5. **Model inputs.** Gamma depends on the IV used. Vanna and charm depend on the volatility model and are more fragile still.
6. **Vendor normalisation.** Share gamma, dollar gamma per point, per 1%, per market cap, per ADV (§1.3) give different rankings across names and over time. A heatmap's colour scale is a vendor choice, not a quantity from the literature.
7. **Self-fulfilling and illusory levels.** If many traders act on the same published strike (a global-games coordination point), price clustering can occur without any hedging mechanism. Conversely, a level computed under the wrong sign is an artefact of the convention. No located paper separates hedging-driven from attention-driven clustering at mapped levels; Ni, Pearson & Poteshman (2005) separate hedging from manipulation only.
8. **Data snooping.** Level-based rules (flip, walls, max-gamma strike) have many free parameters: expiry window, strike band, normalisation, threshold, holding period. With many tested variants, conventional t > 2 hurdles are too low. Harvey, Liu & Zhu (2016, *RFS* 29(1):5–68) argue for t > 3 for new factors. None of the vendor claims located report out-of-sample or multiple-testing-adjusted results. The one practitioner sweep found (FirmTape) explicitly flags unverified numbers and pre-2022 samples.
9. **Regime change.** Most evidence ends before daily SPXW expiries (11 May 2022) or before the current 0DTE share. The sign of dealer gamma and the dominance of pre-positioned versus same-day gamma have both shifted (Adams et al. 2026; IMF 2026).

---

## 5. Synthesis: which map readings have support

| Map reading | Support | Strength | Conditions / caveats | Key sources |
|---|---|---|---|---|
| Negative aggregate dealer gamma → higher next-day/intraday realised volatility | Yes | Moderate (A/B); effect sizes small: ≈12% of single-stock daily abs. return per Ni et al. draft; max +3.3 vol pts in SPX | Strongest in illiquid underlyings; requires correct sign; second-moment only | Ni et al. 2021; Barbon & Buraschi 2021; Amaya et al. 2025 |
| Positive aggregate dealer gamma → dampened volatility, intraday reversal | Yes | Moderate-to-strong in SPX with signed data | Typical SPX state per signed data; decays within ~1 hour intraday | Adams et al. 2026; Amaya et al. 2025; Cboe/Xu 2023 |
| Negative gamma → intraday momentum into the close | Yes | Moderate (B+) | OI-sign proxy; 1996–2020 sample; reverts over following days; LETFs a parallel channel | Baltussen et al. 2021; Barbon et al. 2021 |
| Pinning to large-OI strikes **at expiry** | Partly | Weak-to-moderate; small (≥16.5 bps; 13.6–17.9% vs 10%) | Single names when dealers net long; index pinning not driven by dealer hedging; post-2016 SPX evidence absent | Ni, Pearson & Poteshman 2005; Golez & Jackwerth 2012; Elms 2026 (C) |
| Charm-driven drift into monthly AM SPX expiry | Yes, narrow | Moderate (B), R² 3% | Third-Friday SOQ only; sign follows dealer net charm | Baltussen, Terstegge & Whelan 2024 |
| 0DTE flows destabilise the index | Contested | Mostly *against* on signed data | Tail days with short dealer gamma raise vol modestly | Adams et al. 2026 vs Brogaard, Han & Won |
| GEX predicts **direction** of returns | No | — | Theory predicts variance and autocorrelation, not sign | none located |
| Call wall = resistance, put wall = support, on ordinary days | No located test | D | Possibly attention/coordination, not hedging | none located |
| Zero-gamma flip as a precise trigger price | No located test | D | Sign of aggregate gamma has support; extrapolated crossing level does not | practitioner only; Risk.net 2022 (C) |
| Vanna rallies after vol spikes / around OpEx | No located test | C/D | Model-dependent; single-episode estimates | OptionMetrics press quote |
| Single-name "gamma squeezes" | Mixed | C | Sign disputed even with regulator data (GME) | SEC 2021; Mitts et al. 2022 |

**Practical implications for reading a vendor heatmap.**
1. First establish whether the vendor uses signed (exchange-capacity) positions or the OI sign convention. Under the convention, SPX maps are biased toward showing dealers short gamma below spot, which signed data contradict on most days.
2. Read the aggregate regime as a **volatility and mean-reversion forecast**, not a direction forecast, and expect small effect sizes.
3. Treat strike "walls" and the flip as descriptive positioning, not as levels with a measured hit rate, unless the user's own out-of-sample record says otherwise.
4. Discount single-name maps more heavily than index maps: the sign convention is wrong on average for single stocks, and liquidity matters.
5. Expect maps to be stale intraday on 0DTE-heavy days, and to reset after each expiry and each implied-volatility crush.

---

## References

- Adams, G., Dim, C., Eraker, B., Fontaine, J.-S., Ornthanalai, C., & Vilkov, G. (2026). Do S&P 500 Options Increase Market Volatility? Evidence from 0DTEs. Working paper, 15 July 2026; SSRN 5641974. https://www.jean-sebastienfontaine.com/papers/0dte-options-volatility.pdf
- Adams, G., Fontaine, J.-S., & Ornthanalai, C. (2024). The Market for 0DTE: The Role of Liquidity Providers in Volatility Attenuation. SSRN 4881008. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4881008
- Amaya, D., Garcia-Ares, P. A., Pearson, N. D., & Vasquez, A. (2025). 0DTE Index Options and Market Volatility: How Large is Their Impact? Working paper, 25 Jan 2025. https://cdn.cboe.com/resources/education/research_publications/gammasqueezes.pdf
- Anderegg, B., Ulmann, F., & Sornette, D. (2019). Quantification of feedback effects in FX options markets. SNB Working Paper 2019-03. https://www.snb.ch/en/publications/research/working-papers/2019/working_paper_2019_03
- Avellaneda, M., & Lipkin, M. D. (2003). A market-induced mechanism for stock pinning. *Quantitative Finance* 3(6), 417–425. https://math.nyu.edu/inmemoriam/avellaneda/qf3601.pdf
- Baltussen, G., Da, Z., Lammers, S., & Martens, M. (2021). Hedging demand and market intraday momentum. *Journal of Financial Economics* 142(1), 377–403. https://academicweb.nd.edu/~zda/intramom.pdf
- Baltussen, G., Terstegge, J., & Whelan, P. (2024). The Derivative Payoff Bias. Working paper, Sept 2024 (AEA 2025). https://www.aeaweb.org/conference/2025/program/paper/N7rsBN2N
- Barbon, A., & Buraschi, A. (2021). Gamma Fragility: Asset Pricing Implications of Delta-Hedging. Working paper, SSRN 3725454. https://abarbon.com/papers/gamma-fragility ; summary https://bsic.it/how-dealers-gamma-impacts-underlying-stocks/
- Barbon, A., Beckmeyer, H., Buraschi, A., & Moerke, M. (2021/2022). The Role of Leveraged ETFs and Option Market Imbalances on End-of-Day Price Dynamics / Liquidity Provision to Leveraged ETFs and Equity Options Rebalancing Flows. SSRN 3925725; SFI RP 22-40. https://papers.ssrn.com/abstract=3925725
- Beckmeyer, H., Branger, N., & Gayda, L. (2023). Retail Traders Love 0DTE Options… But Should They? SSRN 4404704.
- Brogaard, J., Han, J., & Won, P. Y. (2023–2025). How Does Zero-Day-to-Expiry Options Trading Affect the Volatility of Underlying Assets? SSRN working paper (coverage: https://www.bnnbloomberg.ca/zero-day-options-are-reordering-the-way-the-stock-market-behaves-1.1921930).
- Cboe. SPX Options Product Specifications. https://ww2.cboe.com/tradable_products/sp_500/spx_options/specifications ; Cboe DataShop, Open-Close Volume Summary. https://datashop.cboe.com/volume-summary-data
- de Silva, T., Smith, K., & So, E. C. (2025). Losing is Optional: Retail Option Trading and Expected Announcement Volatility. *Review of Finance*. https://www.gsb.stanford.edu/faculty-research/publications/losing-optional-retail-option-trading-expected-announcement
- Elms (2026). From Pinning to Amplification: Evidence of a Regime Shift in S&P 500 Options Expiration Dynamics, 2016–2025. SSRN 6564078 (non-peer-reviewed). https://harbourfrontquant.substack.com/p/from-pinning-to-amplification-evidence
- FirmTape (2026). What the 0DTE literature actually claims. https://firmtape.com/research/what-the-0dte-literature-claims
- Gao, L., Han, Y., Li, S. Z., & Zhou, G. (2018). Market intraday momentum. *Journal of Financial Economics* 129(2), 394–414. https://econpapers.repec.org/RePEc:eee:jfinec:v:129:y:2018:i:2:p:394-414
- Gârleanu, N., Pedersen, L. H., & Poteshman, A. M. (2009). Demand-Based Option Pricing. *Review of Financial Studies* 22(10), 4259–4299. https://www.nber.org/papers/w11843
- Golez, B., & Jackwerth, J. C. (2012). Pinning in the S&P 500 futures. *Journal of Financial Economics* 106(3), 566–585. WP: http://www.uni-konstanz.de/FuF/wiwi/workingpaperseries/WP_Jackwerth-Golez-12-10.pdf ; https://ideas.repec.org/a/eee/jfinec/v106y2012i3p566-585.html
- Harvey, C. R., Liu, Y., & Zhu, H. (2016). …and the Cross-Section of Expected Returns. *Review of Financial Studies* 29(1), 5–68.
- Hu, J., Kirilova, A., Muravyev, D., & Ryu, D. Options Market Makers. Working paper. https://sites.google.com/view/antoniakirilova/research
- IMF (2026). Global Financial Stability Report, April 2026, Ch. 1. https://www.imf.org/-/media/files/publications/gfsr/2026/april/english/text.pdf.md
- Jeannin, M., Iori, G., & Samuel, D. (2008). Modeling stock pinning. *Quantitative Finance* 8(8), 823–831. https://ideas.repec.org/a/taf/quantf/v8y2008i8p823-831.html
- Li, Z., Sakkas, A., & Urquhart, A. (2022). Intraday time series momentum: Global evidence and links to market characteristics. *Journal of Financial Markets* (as cited in secondary search; **UNVERIFIED** venue).
- Lipson, M., Tomio, D., & Zhang, J. (2023). A Real Cost of Free Trades: Retail Option Trading Increases the Volatility of Underlying Securities. Working paper. https://www.wealthmanagement.com/equities/retail-options-trading-increasing-volatility-securities
- Mannix, R. (2022). Gamma zero: an overlooked signal of volatility is flashing red. *Risk.net*, 25 Oct 2022. https://www.risk.net/investing/7954930/gamma-zero-an-overlooked-signal-of-volatility-is-flashing-red
- Mitts, J., Battalio, R., Brogaard, J., Cain, M., Glosten, L., & Kochuba, B. (2022). An Academic Critique of the SEC's GameStop Report. CLS Blue Sky Blog, 22 Feb 2022. https://clsbluesky.law.columbia.edu/2022/02/22/an-academic-critique-of-the-secs-gamestop-report/
- Muravyev, D. (2016). Order Flow and Expected Option Returns. *Journal of Finance* 71(2), 673–708.
- Ni, S. X., Pearson, N. D., & Poteshman, A. M. (2005). Stock price clustering on option expiration dates. *Journal of Financial Economics* 78(1), 49–87. https://econpapers.repec.org/RePEc:eee:jfinec:v:78:y:2005:i:1:p:49-87 ; summary https://www.cxoadvisory.com/equity-options/stock-price-pinning-at-options-expiration
- Ni, S. X., Pearson, N. D., Poteshman, A. M., & White, J. (2021). Does Option Trading Have a Pervasive Impact on Underlying Stock Prices? *Review of Financial Studies* 34(4), 1952–1986. https://ideas.repec.org/a/oup/rfinst/v34y2021i4p1952-1986..html ; 2006 draft (Pearson, Poteshman & White): https://ou.edu/dam/price/Finance/CFS/paper/pdf/pearsonPoteshmanWhite.pdf
- O'Donovan, J., Yu, J., & Zhang (first names and initials UNVERIFIED) (2023). Option market maker hedging and stock market liquidity. Working paper. https://ink.library.smu.edu.sg/lkcsb_research/7870
- Rosa, C. (2022). *Journal of Futures Markets* 42(12), 2218–2234. https://ideas.repec.org/a/wly/jfutmk/v42y2022i12p2218-2234.html
- SEC Staff (2021). Staff Report on Equity and Options Market Structure Conditions in Early 2021. https://www.sec.gov/files/staff-report-equity-options-market-struction-conditions-early-2021.pdf
- SqueezeMetrics (2017). Gamma Exposure (GEX): Quantifying hedge rebalancing in SPX options. March 2016, rev. Dec 2017. https://slopeofhope.com/wp-content/uploads/2020/11/GEX-white_paper.pdf
- Sushko, V., & Turner, G. (2018). The equity market turbulence of 5 February – the role of exchange-traded volatility products. *BIS Quarterly Review*, March 2018, Box A. https://www.bis.org/publ/qtrpdf/r_qt1803t.htm
- Xiao, B. (2024). Zero-day options and financial market vulnerability. Bank Underground (Bank of England), 4 Dec 2024. https://bankunderground.co.uk/2024/12/04/zero-day-options-and-financial-market-vulnerability/
- Xu, M. (2023). Volatility Insights: Much Ado About 0DTEs — Evaluating the Market Impact of SPX 0DTE Options. Cboe, 8 Sept 2023. https://www.cboe.com/insights/posts/volatility-insights-evaluating-the-market-impact-of-spx-0-dte-options
- Xu, M. (2025). 0DTEs Decoded: Positioning, Trends, and Market Impact. Cboe, 2 May 2025. https://www.cboe.com/insights/posts/0-dt-es-decoded-positioning-trends-and-market-impact
- Feedback-model theory cited via Pearson, Poteshman & White (2006): Jarrow (1994, *JFQA*); Frey & Stremme (1997, *Mathematical Finance*); Frey (1998, *Finance and Stochastics*); Platen & Schweizer (1998, *Mathematical Finance*); Sircar & Papanicolaou (1998, *Applied Mathematical Finance*); Schönbucher & Wilmott (2000, *SIAM J. Applied Mathematics*). Venues from the draft's bibliography and general knowledge; page numbers **UNVERIFIED**.

### Verification notes
- Read in full text this session: Baltussen et al. 2021 (published PDF), Pearson-Poteshman-White 2006 draft, Amaya et al. 2025, Adams et al. 2026, Golez & Jackwerth 2010 WP, Baltussen-Terstegge-Whelan 2024, SqueezeMetrics 2017, Cboe/Xu 2023 (web page), BIS 2018 box, IMF GFSR April 2026 (text extract), Bank Underground 2024.
- Abstract or secondary summary only: Barbon & Buraschi 2021 (PDF not text-extractable), Ni-Pearson-Poteshman 2005 figures, Brogaard-Han-Won, Dim-Eraker-Vilkov (now merged), Lipson-Tomio-Zhang, O'Donovan-Yu-Zhang, Elms 2026, Cboe/Xu 2025, Krishnan & Nelken 2001, Hu-Kirilova-Muravyev-Ryu, de Silva-Smith-So.
- Vendor methodology for Skylit maps: not examined (**UNVERIFIED**).
