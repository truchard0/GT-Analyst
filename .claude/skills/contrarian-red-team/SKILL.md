---
name: contrarian-red-team
description: Contrarian-generation and adversarial self-testing layer — 10 proven frameworks (ACH, premortem, reference-class forecasting, noise audits, extremizing, information cascades, contrarian returns + momentum caveat, reflexivity/Minsky, neglected risk/convexity, surprisingly-popular) reduced to executable procedures. Contains THE RED-TEAM GATE that must run before ledgering any prediction with conviction >= 0.65, and the self-test loop driven by `python pipeline/ledger.py redteam` and the Brier decomposition. Use whenever forming a thesis, before logging high-conviction predictions, when the tape shows a strong consensus, or on the periodic self-audit.
---

# CONTRARIAN & RED-TEAM LAYER — attack your own book

The other three skills build theses; this one tries to kill them. Two jobs: (a) generate justified contrarian calls (not reflexive disagreement), (b) catch the engine's own errors before the ledger does.

## §0 PROVENANCE (bind this)
Built 2026-07 from deep-research passes that were repeatedly **rate-limited during verification**. Current status: **ACH core (framework 1) is VERIFIED** against the CIA's own Heuer text (2-0 panels): the 8-step procedure and the refutation-based selection rule. Frameworks 2–5 quote primary sources fetched in-session (extracted verbatim, panels errored). Frameworks 6–10 are canonical results from training knowledge, still flagged. The 2026 re-run also extracted the **Chang–Berdini–Mandel–Tetlock (2018) critique** (see Part D) — primary-source support for this skill's own anti-theater rules. Numbers cited carry their labels. This labeling is itself the discipline this skill teaches.

---

## PART A — THE TEN FRAMEWORKS (each: result → procedure → contrarian/self-test use → degeneration)

### 1. Analysis of Competing Hypotheses — the least-inconsistency rule (Heuer, *Psychology of Intelligence Analysis*, 1999; Pherson)
- **Result:** default "satisficing" (pick favored hypothesis, collect confirmation) fails two ways: supporting evidence is often equally consistent with rivals (non-diagnostic), and it ignores *absent* evidence that should exist if the favorite were true. ACH inverts the rule: rate each evidence item against ALL hypotheses ("if H were true, how likely is this evidence?") and select the hypothesis with the **least evidence against it** — not the most for it.
- **Procedure:** (1) enumerate the full hypothesis set incl. the uncomfortable ones; (2) matrix: evidence × hypotheses, score consistency; (3) strike non-diagnostic rows (consistent with everything — most "confirmation" dies here); (4) rank by inconsistency count; (5) list the observable evidence that SHOULD exist under the favorite but is missing.
- **Use here:** run a mini-ACH on every event analysis (the OUTPUT SCHEMA's players/game steps generate the rival hypotheses). Worked example: "Iran deal holds" vs "armistice decentralizes" vs "regime collapses" — the funeral optics are non-diagnostic (consistent with all three); Mojtaba's absence is diagnostic (inconsistent with clean consolidation). That's why it carried the weight.
- **Verified 8-step procedure (CIA/Heuer, 2-0):** (1) brainstorm hypotheses with diverse perspectives; (2) list evidence for/against each; (3) matrix + rate *diagnosticity*; (4) delete non-diagnostic evidence; (5) conclude by trying to DISPROVE, not prove; (6) **sensitivity test** — how much does the conclusion hang on 2–3 critical evidence items? (those items become watch-priorities); (7) report relative likelihood of ALL hypotheses, never just the winner; (8) **identify milestones that would indicate events diverging from expectation** — these are exactly the engine's falsifiers and timeline-web branch triggers.
- **The "no evidence that X" trap (Heuer, extracted):** before concluding from absence of evidence (the India-1998 failure), ask whether the evidence would realistically be VISIBLE if the hypothesis were true. Absence of observable-if-true evidence is diagnostic; absence of unobservable evidence is nothing. (Pairs with doctrine §12.6: under censorship, most evidence is unobservable-by-design.)
- **Degenerates when:** hypothesis set is padded with strawmen so the favorite wins by construction; or evidence scoring is done by the thesis author with no certainty-framing (see #2). MITRE's controlled experiment (extracted) found ACH reduced confirmation bias only in NOVICES — experienced analysts showed no reduction — so the matrix must be run mechanically (scores written down), not "mentally."

### 2. Premortem / prospective hindsight (Klein, HBR 2007; Mitchell-Russo-Pennington, *J. Behavioral Decision Making* 1989)
- **Result:** imagining an outcome as **certain-already-happened** ("the prediction failed — why?") produces longer, more concrete, more episodic causal accounts than "what might go wrong?" MRP: the active ingredient is the **certainty framing**, not time-shifting; prospective hindsight raised correct reason-identification ~30%.
- **Procedure (bot version):** before ledgering, write 3 lines under the frame "It is [horizon date]. This prediction resolved 0. What happened?" — forced past-tense, specific causes, no hedging. Any cause not already covered by the `--sensitivity` tag gets added or the probability gets revised.
- **Use here:** the premortem output IS the falsifier-quality check: if the imagined failure mode isn't observable/dated, the falsifier is defective.
- **Degenerates when:** it becomes a listing ritual whose outputs never move the probability — if 10 premortems in a row change nothing, the gate is theater (see §D).

### 3. Reference-class forecasting / outside view (Flyvbjerg 2006; Kahneman-Tversky 1979; Mellers et al. CHAMPS KNOW, *JDM* 2014)
- **Result:** three steps — identify a reference class of comparable past cases; build its outcome distribution; position the current case in it — BEFORE any inside-view story. It corrects both honest optimism and agenda-driven forecasts because it bypasses the narrative entirely. In IC forecasting tournaments, a <1hr debiasing checklist improved Brier 6–11%, and the single principle correlated with better scores was **comparison-class use**.
- **Procedure:** every prediction states its base rate line first: "Reference class: N comparable cases, X% base rate; my P deviates because [named mechanism]." No named mechanism → P snaps to the base rate.
- **Use here:** already partially wired (formal §10 item 10); this upgrades it from "state a base rate" to "name the reference class and justify the deviation." Worked example: 60-day regime-collapse calls — base rate of mid-war clerical-regime collapse within 60 days of a leader's death is very low → #17's P=0.88 survival call is the outside view winning against the vivid inside story.
- **Degenerates when:** reference class is cherry-picked post-hoc to justify the inside view ("reference class of times I was right").

### 4. Noise audit + decision hygiene (Kahneman, Sibony & Sunstein, *Noise*, 2021)
- **Result:** noise = variability across judgments of the SAME problem, distinct from bias (directional error); organizations typically carry more noise than bias — an insurance noise audit found ~55% median variance where executives expected ~10%. Remedies: independent parallel judgments, base rates, structured decomposition (Mediating Assessments Protocol), aggregate-then-discuss.
- **Procedure (bot self-audit):** periodically re-run the SAME event cold (fresh session, no sight of the prior analysis) and compare conviction/probability spread. Spread >0.10 on identical inputs = the engine's rubric is noisy, not just biased — tighten the rubric anchors, don't just recalibrate.
- **Use here:** the conviction rubric IS the noise-control device (anchored components, not holistic gut). The audit tests whether it's working.
- **Degenerates when:** the "independent" re-judgment can see the first answer (anchoring destroys the audit); or noise findings get explained away case-by-case.

### 5. Extremizing aggregation (Baron, Mellers, Tetlock & Ungar, *Decision Analysis* 2014)
- **Result:** averaged probability forecasts are systematically too moderate for two reasons: (a) scale compression near 0/1 pushes means toward 0.5 (fixed by median or log-odds pooling); (b) each forecaster hedges toward 0.5 because they hold only part of the crowd's information — biasing even the median — so the pooled forecast should be **extremized** (pushed toward 0/1) when inputs are genuinely independent.
- **Procedure:** when multiple independent lenses (doctrine, formal, market-transmission, watchlist flow) agree directionally, do NOT average their hedged probabilities — extremize: the multi-lens P should sit *outside* the most confident single-lens P. When lenses are correlated (same underlying evidence), do the opposite — no extremizing credit (this is the cluster-tag logic applied to conviction).
- **Use here:** upgrades doctrine §10.12 (convergence rule) from "confidence multiplier" vibe to a directional rule with an independence precondition.
- **Degenerates when:** extremizing correlated inputs — the deadly version. Three skills reading the SAME headline are one lens, not three.

### 6. Information cascades & rational herding (Bikhchandani-Hirshleifer-Welch, *JPE* 1992; Scharfstein-Stein, *AER* 1990) — [canonical; re-verify]
- **Result:** when actors observe predecessors' ACTIONS but not their private signals, it becomes rational to ignore one's own signal and copy — after which the consensus carries **no additional information** (a cascade: fragile, shatterable by small public news). Scharfstein-Stein: professionals herd to protect reputation ("share the blame" — being wrong conventionally beats being wrong alone).
- **Procedure — the cascade test (contrarian license):** before treating consensus as evidence, ask: (1) are the consensus-holders' inputs independent, or are they citing each other? (2) does anyone visibly hold private information, or is it all public-signal recycling? (3) is there career/reputation cost to dissent? If mostly (copying + recycling + dissent-cost) → the consensus is informationally EMPTY → fading it costs nothing informationally; a contrarian call needs only your own signal.
- **Use here:** meshes with formal §12.2/§12.8 — a cascade is precisely a consensus built on a public signal with dispersed private info suppressed; those are the fragile, headline-shatterable ones.
- **Degenerates when:** used to dismiss ALL consensus — sometimes everyone agrees because the evidence is overwhelming and independent. The test is input independence, not agreement itself.

### 7. Contrarian returns + the momentum caveat (De Bondt-Thaler, *JF* 1985; Lakonishok-Shleifer-Vishny, *JF* 1994; Jegadeesh-Titman, *JF* 1993) — [canonical; re-verify]
- **Result:** prior extreme LOSERS over 3–5 years beat prior extreme winners (long-horizon overreaction reverses); value/contrarian portfolios beat glamour without extra risk (LSV: expectational errors, not risk premia). BUT over 6–12 months, MOMENTUM wins — recent winners keep winning.
- **Procedure — the horizon fork:** fading consensus is a **long-horizon** (multi-quarter/year) trade on expectational extremes; NEVER fade 6–12-month momentum just because it "feels stretched." A contrarian call must state which horizon it lives on: reversal horizon (3–5y expectational extreme) or it's fighting the momentum tape and needs a *catalyst*, not just valuation.
- **Use here:** disciplines §13 scarcity-premium fades — "priced for perfection" alone is a reversal-horizon argument; a tradeable near-term fade needs the §13 architecture-attack catalyst.
- **Degenerates when:** "it's up a lot" masquerades as analysis — that's fighting momentum without a catalyst, the classic contrarian graveyard.
- **Worked miss — the "fade AI strength" shape (2026-10-25 sweep: #69, #70, #24):** the engine faded semis/AI on a rate-derate mechanism (market-transmission §5) and a "priced-in" read, into 6–12-month AI-capex momentum, with no catalyst attacking the capex architecture. Result over 7/31→9/30: SMH +12.7% vs SPY +2.1%, *through* a Fed hike (9/16) and a 5% 10-year. QQQ broke its 720 cap on day 3 (8/4). TSMC printed a 67.7% gross margin, above the top of its own 65.5–67.5% guide. The §5 derating law is a prior *relative to regime*; it does not beat rising earnings revisions (NVDA Q2 FY27 revenue +106%, guide above consensus). **RULE:** a semis/AI underperformance or range-cap call needs either (a) a capex-architecture attack (doctrine §13) or (b) a dated earnings-revision rollover. A rate-path argument alone is not a catalyst.

### 8. Reflexivity & the financial-instability staging (Soros, *Alchemy of Finance*, 1987; Minsky, FIH, 1977/1986) — [canonical; re-verify]
- **Result:** Soros — prices don't just reflect fundamentals, they *alter* them (rising prices → more collateral/credibility → better fundamentals → higher prices), so boom-bust is endogenous with identifiable stages (trend + bias → test → acceleration → twilight (fundamentals no longer confirm but price rises on belief) → crossover → crash). Minsky — stability breeds instability via credit staging: **hedge** (cash flows cover debt) → **speculative** (cover interest only) → **Ponzi** (need asset appreciation to service debt); the Ponzi share is the regime-break clock.
- **Procedure — the top-call checklist (contrarian regime-break):** (1) is price itself improving the fundamentals story (reflexive loop live)? (2) twilight test: has incremental fundamental news stopped confirming while price still rises? (3) financing test: what share of marginal buying is hedge vs speculative vs Ponzi (needs-appreciation)? Regime-break calls require ≥2 of 3; otherwise it's a #7 momentum fight.
- **Use here:** gives the engine a structured way to call tops against consensus (the current AI-capex/neocloud complex is the standing candidate: apply the three tests before any bubble call, and ledger the result).
- **Degenerates when:** permabear mode — reflexivity/Minsky language can "justify" a top call at any time; the falsifier discipline (dated, observable) is the antidote.

### 9. Neglected risk & convex expression (Gennaioli-Shleifer-Vishny, *JFE* 2012; Zeckhauser; Taleb, *Antifragile*) — [canonical; re-verify]
- **Result:** GSV — investors neglect low-probability risks not present in recent data ("what you see is all there is" applied to tails); intermediaries manufacture securities that look safe precisely because the neglected risk is unpriced; when the risk surfaces, repricing is violent. Expression side (Taleb): when you can't price the tail, structure the position convexly (barbell: safe core + small positions with unbounded upside) rather than betting the middle.
- **Procedure — the neglected-risk sweep:** each analysis session, ask "what risk does the CURRENT pricing structure assume away?" (not "what could go wrong" — what is *structurally absent from prices*: vol surface, spread levels, positioning). That absence + a doctrine-layer mechanism = the highest-value contrarian call class. Express via convexity (options/vol) not linear fades.
- **Use here:** formalizes what the Iran Branch-B analysis did instinctively (the under-priced supply-shock tail as a *hedge*, not a fade) — now it's a standing sweep, not an accident.
- **Degenerates when:** everything becomes a "neglected tail" — the sweep needs the pricing evidence (what IS the vol/spread assuming?) not just imagination.

### 10. Surprisingly-popular answer / Bayesian Truth Serum (Prelec, *Science* 2004; Prelec-Seung-McCoy, *Nature* 2017) — [canonical; re-verify]
- **Result:** asking respondents both "what's true?" AND "what will others say?" identifies correct minority answers: the answer that is **more common than people predicted** is disproportionately the true one (those with genuine private knowledge correctly anticipate the crowd's error).
- **Procedure (bot adaptation):** for any consensus question, explicitly model BOTH "what does the market believe?" and "what would the market predict OTHER participants believe?" A divergence — where informed actors' positioning (flows, insider tells, §10.11/§11.8 revealed-expectations signals) contradicts the surveyed/narrated consensus — is the surprisingly-popular flag: weight the positioning over the narrative.
- **Use here:** operationalizes "watch what they do, not what they say" (§12.1) into a two-question test; prediction-market whale divergence from polls is the canonical instance.
- **Degenerates when:** positioning data is itself noise (thin markets) — require the §10.11 corroboration rule.

---

## PART B — THE RED-TEAM GATE (mandatory, pre-ledger)
Run before ledgering ANY prediction with conviction ≥ 0.65, and before adding a 5th+ row to an existing cluster:
1. **Key assumptions check:** list the ≤3 assumptions that, if false, kill the call (they become/extend the `--sensitivity` tag).
2. **Mini-ACH (#1):** name ≥2 rival hypotheses; confirm ≥1 evidence item is *diagnostic* (inconsistent with a rival). All-non-diagnostic evidence → conviction cap 0.55.
3. **Premortem (#2):** certainty-framed failure story; unlisted cause → revise sensitivity or P.
4. **Cascade check (#6):** is my evidence independent, or am I reading the herd reading itself? Herd-derived → conviction −0.10.
5. **Reference class (#3):** named class, base rate, named deviation mechanism.
6. **Independence/extremizing (#5):** multi-lens agreement from independent evidence → extremize is allowed; same-evidence lenses → no convergence credit.
Log the gate verdict in the analysis (one line per step is enough). FAIL any step → don't ledger at that conviction.

## PART C — THE SELF-TEST LOOP (periodic, `ledger.py` driven)
- **Weekly (or per session):** `python pipeline/ledger.py redteam` — attack every open position with fresh tape: falsifier still observable? new contradicting evidence? sensitivity already firing? cluster-thesis check on the concentration warning.
- **On resolutions:** `report` reads the **Murphy decomposition** — REL high = miscalibrated (probabilities drift from frequencies → fix the rubric anchors); RES low = no discrimination (forecasts hug the base rate → the engine adds nothing over the outside view). These are different diseases with different cures; never read mean Brier alone.
- **Noise audit (#4), monthly:** re-run one already-analyzed event cold; conviction spread >0.10 → rubric anchors need tightening.
- **Abstain zone for mechanical lenses (500-call stock backtest, 2026-10-26).** The engine's own confidence carried information, but its low-confidence calls were worse than a coin:

  | Engine probability | Calls | Hit rate |
  |---|---|---|
  | P ≥ 0.60 | 144 | **63%** (claimed 64%, well calibrated) |
  | P < 0.60 | 356 | **35%** (claimed 54%) |

  The 0.55–0.60 bucket hit 28%. **Rule:** mechanical/screening outputs below P 0.60 are NOT predictions. Report them as "no view" and never ledger or score them as calls. Caveat: the confident calls came from only two weeks, so treat this as a provisional threshold.
- **Method audit (RAND RR1408 caveat):** structured techniques are institutionally assumed, not proven — track whether gate-passed predictions actually out-score gate-skipped ones once ≥10 resolve. If they don't, the gate is theater; change it.

## PART D — DEGENERATION GUARDRAILS (the avoid-list)
- **Reflexive contrarianism:** disagreement is not alpha; the cascade test (#6) or neglected-risk evidence (#9) must license the fade. No license → you're the herd's mirror image.
- **Bias bipolarity (Chang–Berdini–Mandel–Tetlock 2018, extracted — the strongest version of the warning):** one-directional contrarian techniques predictably trigger the OPPOSITE bias — over-predicting change, base-rate neglect, time burned on frivolous contrarian arguments. **Measure the direction of the current bias before applying a corrective:** if the engine's recent misses were over-predicting change, more contrarianism makes it worse. The Brier decomposition tells you which way you're leaning; correct against THAT, not against consensus generically.
- **Differential efficacy (Coulthart review, extracted):** techniques are not equal — devil's advocacy beat consensus decisions in ~70% of studied cases, but collaborative face-to-face brainstorming was consistently DETRIMENTAL, and ACH helps novices not experts. Prefer independent-then-aggregate over discuss-then-decide in every multi-lens step.
- **The validation void (RAND RR1408 + Chang et al., both extracted):** the entire structured-analytic-technique canon "has never been subjected to sustained scientific validation" — its accuracy benefits are institutionally assumed. The fix both papers prescribe is EXACTLY this engine's architecture: numeric probabilities per hypothesis, Brier tracking per technique, test-retest reliability (the noise audit), coherence checks, and evidence-outcome records building base rates. The ledger isn't decoration — it's the only thing that makes the rest of this skill non-theater.
- **Devil's-advocacy theater (RAND):** SAT labels without transparent logic are performative. If the red-team gate never changes a probability, delete it and rebuild.
- **Momentum graveyard (#7):** no near-term consensus fade without a catalyst.
- **Permabear drift (#8):** top-calls require the 3-test checklist AND a dated falsifier.
- **Extremizing the correlated (#5):** the cluster tag exists precisely so convergence credit isn't given twice.

## SOURCES
Fetched this session (quotes extracted, panels rate-limited): Heuer/Pherson ACH paper (pherson.org); Klein premortem (HBR reprint); Mitchell-Russo-Pennington 1989 (Wiley); Flyvbjerg RCF (SSRN 2238013); Mellers et al. CHAMPS KNOW (Cambridge JDM); Kahneman-Sibony-Sunstein *Noise*; Baron-Mellers-Tetlock-Ungar extremizing (INFORMS Decision Analysis 2014); RAND RR1408 (SAT validation gap). Canonical pending re-verify: BHW 1992; Scharfstein-Stein 1990; De Bondt-Thaler 1985; LSV 1994; Jegadeesh-Titman 1993; Soros 1987; Minsky FIH; GSV 2012; Taleb; Prelec 2004/2017.
