---
name: formal-game-theory
description: Formal rigor and validity layer for game-theoretic news analysis — Schelling commitment/brinkmanship, Fearon's bargaining model of war, signaling vs cheap talk, audience costs, repeated games, Kahn escalation, prospect theory, Tetlock forecasting discipline, plus a modern-GT module (§12): global games / coordination-crisis thresholds, the destabilizing-public-information reversal, the publicity multiplier, Crawford-Sobel cheap-talk coarseness, forward guidance as Bayesian persuasion, uninformative-propaganda-under-censorship, and reputation-vs-commitment. Includes the §10/§12.9 validity checklist run on every analyzed event. Always run alongside jiang-doctrine; on validity conflicts THIS skill wins.
---

# FORMAL GAME THEORY — VALIDITY LAYER

The jiang-doctrine skill supplies salience (which game is being played, what to watch). This skill supplies validity (whether the argument is sound). Every event analysis runs the §10 checklist; a FAIL verdict means the prediction is not ledgered, whatever the doctrine layer says. Reference text: `references/GT_book.pdf`.

---

## 1. SCHELLING: COMMITMENT, FOCAL POINTS, BRINKMANSHIP

- **Commitment is the power to bind oneself.** A threat or promise moves behavior only if the committing move is *observable* and *irreversible* (burning bridges, tripwire troops, treaty ratification, capacity construction). A stated intention with a retained exit option is NOT a commitment — classify it as cheap talk. This is the formal ground of doctrine §12.1: budgets and force posture commit; speeches don't.
- **Focal points.** Under coordination problems with no communication, outcomes converge on prominence (status quo lines, round numbers, old borders, straits and rivers). Predictive use: settlements and ceasefire lines gravitate to focal geography; proposals far from any focal point are less stable.
- **Brinkmanship = the threat that leaves something to chance.** Rational actors can credibly threaten mutual disaster only by creating shared *risk* they do not fully control (escalation spirals, autonomous local commanders, hair-trigger postures). When you see an actor deliberately degrading its own control, read it as manufactured credibility, not incompetence — but demand observable mechanism.
- **Deterrence vs. compellence (with Kahn, §6):** deterrence (don't do X) exploits the status quo and an adversary's inertia; compellence (undo X / start doing Y) demands visible climb-down and is systematically harder. Flag any prediction that assumes quick compellence success.

## 2. FEARON: THE BARGAINING MODEL OF WAR

War is ex-post inefficient — a bargain both sides prefer exists *ex ante*. Therefore every war/continuation prediction MUST name at least one of the three rationalist mechanisms that block the bargain:
1. **Private information + incentives to misrepresent** — sides disagree about relative strength/resolve and have reasons to bluff. Diagnostic: war becomes *more* likely when capabilities are opaque or leaders have just changed.
2. **Commitment problems** — a deal today can't be enforced tomorrow (shifting power → preventive war; first-strike advantages; disarmament demands that gut future bargaining power). Doctrine §11.5's *constitutive* conflicts are commitment problems over the system architecture itself — no third party can enforce the terms, so ceasefires are unstable. This is the formal justification for fading truce rallies.
3. **Issue indivisibility** — rare in reality (most things are divisible via side payments); treat claimed indivisibility (holy sites, capital cities) as constructed by domestic politics, and ask who benefits from constructing it.

**Rule: no mechanism, no war prediction.** "Tensions are rising" is not a mechanism.

## 3. SIGNALING VS. CHEAP TALK; AUDIENCE COSTS

- A **signal** is informative only if it is *costly* — sinking costs (mobilization spending, capacity construction) or tying hands (public commitments a leader can't cheaply abandon). Costless statements are cheap talk and carry zero evidentiary weight for resolve — exactly doctrine §12.1's rhetoric filter, formalized.
- **Audience costs:** leaders who back down from *public* threats pay domestic punishment, so public threats by leaders facing real domestic accountability are partially credible; private or deniable threats are not. Weight threats by the political cost of retreating from them, not by their volume.
- **Cheap-talk exception:** costless communication can still coordinate (focal-point selection) when interests already align. Distinguish coordination talk from resolve talk.

## 4. REPEATED GAMES & REPUTATION

- Cooperation among egoists is sustainable when interaction is repeated, observable, and the shadow of the future is long (folk theorem intuition). Reputation arguments are valid ONLY when the audience actually observes repeated play by the same actor in the same domain.
- Check the discount factor: an actor in terminal decline (doctrine §4 structural desperation) has a short shadow of the future — reputation logic weakens, gamble logic strengthens.
- One-shot interactions (succession crises, endgame negotiations) void reputation-based predictions; re-derive from stage-game incentives.

## 5. PUTNAM: TWO-LEVEL GAMES

International moves must survive ratification by a domestic win-set (legislature, coalition, street). Small win-sets are bargaining *leverage* ("my hands are tied") but execution *risk*. For every predicted agreement or escalation, ask: does the actor's domestic win-set permit it? A predicted deal outside any player's win-set is invalid regardless of international logic.

## 6. KAHN: ESCALATION LADDERS

Kahn's 44-rung ladder is the formal ancestor of doctrine §2. Operational rules:
- Escalation is a *bargaining process* conducted in rungs — each rung is a message about resolve plus a probe of the opponent's.
- Rung-skipping requires an articulated mechanism (first-strike advantage, use-it-or-lose-it pressure, catastrophic intelligence failure). Absent that, discount jump scenarios heavily.
- Distinguish escalation *dominance* (having higher rungs available) from escalation *control* (ability to choose the rung that serves the objective) — control wins; this is doctrine §2's core claim and it is formally sound.

## 7. PROSPECT THEORY

- Actors are risk-averse in the gain domain, risk-SEEKING in the loss domain, relative to a reference point (usually the status quo or a recent peak).
- Assign each player a domain before predicting risk appetite: a declining power defending a slipping status quo is in losses → expect gambles (grounds doctrine §4). A rising power consolidating gains is in gains → expect caution.
- Certainty effect: actors overpay to eliminate small risks entirely — explains lopsided insurance-like behavior (buffer zones, pre-emptive strikes on nascent capabilities).
- Reference points shift: after a loss is normalized, the new status quo re-anchors. Time your predictions to the anchoring, not the event.

## 8. TETLOCK: FORECASTING DISCIPLINE

- **Outside view FIRST**: state the base rate for the event class before any inside-view story ("interstate wars lasting >2 years resolve by negotiated settlement X% of the time"). Inside view adjusts, never replaces.
- Granular probabilities (0.55 vs 0.70 is a real distinction; "likely" is not a probability).
- Fermi-decompose compound predictions; multiply through explicitly. A prediction requiring 4 independent 70% steps is a 24% prediction.
- Pre-registration: the ledger IS the pre-registration device. A prediction not logged before resolution does not exist.
- Brier feedback: run `python pipeline/ledger.py report` and treat calibration drift as a model bug to diagnose, not noise (this is also Jiang's own §1.3 standard).
- Reject your own output if any prediction lacks probability, horizon, falsifier, or sensitivity tag.

## 9. DOCTRINE INTERFACE (Jiang claim → formal grounding → constraint)

| Doctrine concept | Formal grounding | Validity constraint |
|---|---|---|
| §12.1 rhetoric filter | Costly signaling (§3) | Only sunk-cost/tied-hands moves update the thesis |
| §2 credibility trap | Schelling commitment + reputation (§1,§4) | Requires observable repeated play; hegemon must actually be watched |
| §11.5 constitutive conflict | Fearon commitment problem (§2) | Must show why no enforceable bargain exists |
| §2 no rung-skipping | Kahn (§6) | Jumps need an articulated mechanism |
| §4 structural desperation | Prospect theory (§7) | Must establish the actor is genuinely in the loss domain |
| §10.5 coalition rules | Repeated games / alliance credibility (§4) | "Strong respect strong" needs demonstrated, observed capability |
| §10.7 steelman inversion | Revealed preference | Hypothesis only until it makes verified differential predictions |
| §12.6 opposition theater | — (no formal grounding) | Tier B heuristic; never assert coordination as fact |

**Conflict rule:** when a doctrine-layer argument fails any §10 check, the formal layer wins. Either repair the argument (find the costly signal, name the Fearon mechanism) or downgrade conviction and drop the prediction.

## 10. FORMAL VALIDITY CHECKLIST (run per event; verdict: PASS / PASS-WITH-FLAGS / FAIL)

1. Players and their choice sets explicit? (No "the West decides…" blobs — doctrine §4: allies are separate players.)
2. Preferences stated, plus flip-test: does the conclusion survive a plausible alternative preference ordering?
3. Information structure identified — does the argument require an actor to know something unknowable to them?
4. One-shot vs. repeated correctly identified; reputation claims only in genuinely repeated, observed play?
5. Every claimed "signal" costly (sunk cost or tied hands)? Cheap talk discarded as resolve evidence?
6. Commitment claims backed by observable, irreversible devices?
7. War/continuation predictions name a Fearon mechanism (private info / commitment problem / indivisibility)?
8. Escalation predictions: intermediate rungs observed; no rung-skipping without stated mechanism?
9. Equilibrium sanity: is the predicted behavior a best response for EACH player? Dominated strategies explained (misperception, audience costs, principal-agent) or the prediction rejected?
10. Base rate stated before the inside view?
11. Falsifier observable, dated, and *discriminating* (would actually distinguish this model from rivals)?
12. Prospect-theory frame: loss vs. gain domain assigned per actor, with justification?
13. Two-level check: does each actor's domestic win-set permit the predicted move?

Scoring: all pass → PASS (0.20 conviction component). 1–2 soft failures with stated caveats → PASS-WITH-FLAGS (0.10). Any hard failure (esp. items 5, 7, 9, 11) → FAIL (0.00): do not ledger; note in report why.

## 11. GAME ARCHETYPE QUICK REFERENCE

- **Chicken** — two actors on collision course; swerving is humiliation, collision is catastrophe. Equilibria are asymmetric: someone swerves. Commitment devices (visible hand-tying) win. News diagnostic: public, irreversible commitments arriving BEFORE a deadline. Market: vol spikes into deadline, fades on any swerve — but check §11.5 first; constitutive chicken doesn't resolve.
- **Deterrence** — status-quo defense via threat. Stable while threat is credible and challenger is in gain domain. Watch credibility erosion events (cheap absorbed punishment, doctrine §2). Market: slow repricing, then a step when credibility visibly breaks.
- **Compellence** — demanding change under threat. Base rate of success is LOW; demands visible climb-down. Predictions of quick sanctions/blockade success should be discounted by default. Market: fade "X will fold quickly" narratives.
- **Bargaining with outside options** — settlement range exists between reservation points; outside options (alternate buyers, patrons, corridors) set the floor. When an actor's outside option improves (doctrine §10.8 redirection effect), expect harder bargaining, not capitulation.
- **War of attrition** — costly waiting contest won by the side with lower per-period costs or higher stakes valuation. Predict duration from cost asymmetry (doctrine §10.2 triad), not from battlefield snapshots. Market: durable supply-chain/defense theses, not event trades.
- **Stag hunt** — cooperation is best for all but requires trust; defection is safe. Alliances and sanctions coalitions are stag hunts: predict defection by the member with the best private (hare) option — doctrine §10.5.3's "the weak attach, not coalition" is the same claim.

## 12. MODERN GAME THEORY EXTENSIONS (added 2026 from a verified deep-research pass; sources in §13)

These are post-1980 results that *change* predictions the classics (§1–11) get wrong. Each: formal result → news-flow diagnostic → how it sharpens/reverses the call → misapplication guardrail.

### 12.1 Global games — coordination crises have a computable threshold, not "indeterminacy" (Tier A)
- **Result (Carlsson–van Damme 1993; Morris–Shin).** In coordination games with strategic complementarities, replacing common knowledge of the fundamental θ with noisy *private* signals collapses the classic multiplicity into a UNIQUE, dominance-solvable **threshold** equilibrium (risk-dominant; canonical cutoff ½). Crisis happens iff θ < θ*.
- **Diagnostic.** Applies whenever actors act on idiosyncratic (not commonly-known) reads of a fundamental: currency pegs, bank/deposit runs, debt rollover, protest/regime survival, coordinated selling.
- **Sharpens.** Reject "it's a coordination game so anything can happen" as an analytic cop-out. Forecast a *discrete* crisis probability from fundamentals **plus the information structure**, and identify the θ* trigger.
- **Guardrail.** Uniqueness holds only in the small-private-noise regime (private signals precise relative to public/prior); it breaks under a precise public signal (§12.2) or endogenous informative prices.

### 12.2 The destabilizing-public-information reversal (Tier A — counterintuitive, high value)
- **Result (Morris–Shin).** Uniqueness holds *iff* private noise is small relative to public noise squared: **σ_x/σ_z² ≤ √(2π)**. Above that knife-edge, multiplicity (a self-fulfilling-crisis equilibrium) re-emerges. Making PUBLIC information more precise is **destabilizing**.
- **Diagnostic.** A single highly-precise, widely-shared public signal — a benchmark print, one dominant headline, a coordinating official statement — begins to dominate dispersed private assessments.
- **Reverses.** Crisis risk peaks not merely when fundamentals are worst, but when a precise *common* signal overwhelms private views → self-fulfilling attacks/runs become possible again. This flips the naive "more transparency = more stability."
- **Guardrail.** Multiplicity means a crisis equilibrium *can exist*, not that its probability is provably maximal; it's about payoff-relevant public signals, not payoff-irrelevant sunspots.

### 12.3 The publicity multiplier — rational overreaction to announcements (Tier A)
- **Result (Morris–Shin).** Public information carries strategic weight ζ *exceeding* its literal news content (a coordination device on what others believe), largest just before the multiplicity threshold.
- **Diagnostic.** Markets move out of proportion to the actual news content of a Fed/central-bank statement or a headline that merely restates known policy.
- **Sharpens.** Weight public/coordinating signals as AMPLIFIED vs equivalent private information; "overreaction" is often rational when participants care about others' reactions. Pairs with doctrine §13 (scarcity repricing) and the priced-in check — a public restatement can move price precisely because it's public.
- **Guardrail.** Use the positive mechanism; the *normative* "social value of public information" welfare corollary is genuinely contested (Morris–Shin vs Svensson) — do not import the anti-transparency politics. Empirical overreaction is weaker than the theory's point estimate.

### 12.4 Cheap talk is inherently coarse (Crawford–Sobel) (Tier A — formalizes the rhetoric filter)
- **Result (Crawford–Sobel 1982).** Every cheap-talk equilibrium partitions the state into at most **N\*** intervals (types pool on a message); N\* shrinks as sender–receiver conflict rises. No equilibrium transmits more than N\* distinct actions.
- **Diagnostic.** Any biased communicator whose preferred outcome diverges from the audience's: sell-side analysts, corporate guidance, spokespeople, diplomats, state media.
- **Sharpens.** Never read precise information out of a biased source — extract only a coarse *bucket*, and expect *fewer* credibly distinguishable messages as interests diverge. This is the formal engine under doctrine §12.1's rhetoric filter (it explains *why* rhetoric is low-information, not just that it is).
- **Guardrail.** Comparative statics need a monotonicity condition; selection refinements (NITS) change *which* equilibrium, not the coarseness. (Refuted over-claim: cheap talk does NOT strictly require both differing preferences AND common interest in the strong form.)

### 12.5 Forward guidance = Bayesian persuasion; the Delphic puzzle (Tier B)
- **Result (Kamenica–Gentzkow; Fujiwara–Waki).** Forward guidance is a Sender committing to a disclosure policy. In the textbook New-Keynesian model, **"Delphic" guidance** (revealing the bank's private forecast of shocks) *unambiguously reduces* welfare → secrecy is optimal. In full DSGE the sign flips by shock type.
- **Diagnostic.** Distinguish **Delphic** (revealing shock forecasts) from **Odyssean** (committing to future policy) guidance; watch which shock a central bank is implicitly disclosing.
- **Reverses.** More transparency about a policymaker's private forecast is *not* reliably stabilizing; don't assume "the Fed clarified" is calming.
- **Guardrail.** The "secrecy optimal" result is scoped to the simple model and flips in richer ones — beneficial Delphic guidance is hard to identify ex ante.

### 12.6 Uninformative propaganda under censorship (Tier B — direct geopolitics use)
- **Result (Gehlbach–Luo–Shirikov–Vorobyev).** When propaganda operates *alongside* censorship, equilibrium-optimal propaganda is **entirely uninformative** (media always report the regime is winning/competent). Censorship does the persuading; propaganda just avoids contradicting it.
- **Diagnostic.** A regime that both censors *and* broadcasts relentlessly positive messaging.
- **Sharpens.** Do NOT infer regime strength from upbeat state media — its informativeness is zero by design. Read the *censorship apparatus*, not the content. (Directly applies to reading "defiance/new regional order" state coverage in the Iran cluster: weight the censorship, discount the funeral optics.)
- **Guardrail.** Contingent on the censorship+repression pairing; a persuader *without* a censorship technology still optimally mixes fact and fiction.

### 12.7 Reputation & transparency are weak substitutes for commitment (Tier B — tempers folk-theorem optimism)
- **Result (Duffy–Heinemann 2021, lab test of repeated Barro–Gordon).** Discretionary play converges toward the high-inflation one-shot Nash, NOT the efficient Ramsey outcome; cheap-talk gains are transitory (agents learn to ignore messages); transparency mechanisms don't reach commitment-level welfare.
- **Diagnostic.** A policymaker relying on reputation/announcements rather than hard commitment — inflation targeting, sanctions credibility, extended deterrence.
- **Sharpens/Reverses.** Don't price in that repeated interaction or transparency *automatically* delivers commitment-level credibility. Reputation is fragile and cheap-talk credibility decays. Cross-checks §4 (reputation needs observed repeated play) and §1 (commitment must be observable + irreversible).
- **Guardrail.** Lab evidence with student subjects — directionally informative, not field-validated for real central bankers or sanctioning states.

### 12.8 Common-knowledge destruction — not a shared narrative — drives self-fulfilling crises (Tier A)
- **Result (Heinemann–Illing).** Adding a commonly-observed sunspot/news variable does NOT restore multiplicity; *uncertainty about others' information* (destroyed common knowledge) does.
- **Diagnostic.** A shared focal narrative alone is insufficient to trigger a self-fulfilling attack if private signals stay dispersed and precise.
- **Sharpens.** Assess *higher-order beliefs* ("what does each side think the others know") — not merely the presence of a shared story or a viral narrative.
- **Guardrail.** Endogenous informative *prices* (Angeletos–Werning) can restore multiplicity via higher-order beliefs — a distinct channel from a payoff-irrelevant sunspot.

### 12.9 New validity-checklist items (append to §10; run on coordination/communication events)
14. **Coordination frame:** is this a strategic-complementarity game (peg / run / rollover / regime survival / coordinated selling)? If so, use a global-games **threshold θ*** rather than declaring "indeterminate."
15. **Public-vs-private information:** is one precise, widely-shared public signal dominating dispersed private views (σ_x/σ_z² near √(2π))? If so, flag elevated self-fulfilling-crisis risk and a publicity multiplier on the announcement.
16. **Source-bias coarseness:** for any biased communicator, has the message been reduced to a coarse Crawford–Sobel bucket instead of read literally?
17. **Commitment vs reputation:** does the prediction rest on reputation/announcements rather than an observable irreversible commitment? If so, discount toward the discretionary (worse) outcome.

*(Items 18–22 live in market-transmission §13b. Items 23–24 added from the 2026-07-13 eval run:)*
23. **Contagion channel test:** any contagion/spillover prediction must NAME a demonstrable transmission channel with a rough size, and show the run-prone layer can actually run (closed capital accounts and state-directed banks can't produce Lehman mechanics — the Evergrande lesson). No sized channel → the contagion call is unledgerable noise.
24. **Capital-committed precedence:** when information-structure lenses (§12.2/§12.3) and capital-committed evidence (doctrine §12.1) point opposite ways, capital-committed wins.

### 12.11 Level-k / cognitive hierarchy — how deep the market actually thinks (Nagel 1995 [VERIFIED 3-0]; Camerer–Ho–Chong 2004 [extracted])
- **Result (verified against Nagel's paper):** in the p-beauty contest the unique Nash equilibrium (zero) predicts NOBODY's first-round play — 0% chose it, only 6% below 10. Behavior is organized by finite depth-of-reasoning from a naive anchor (level-0 = 50; level-n = 50·pⁿ), with ~50% of players at **1–2 steps** and only 6–10% at step 3+. Repetition converges toward equilibrium by **re-anchoring on last period's outcome, not by deeper thinking** — modal depth stays at step 2. CH model (extracted): Poisson distribution over levels, average ≈ **1.5 steps** across many games.
- **Diagnostic:** any "what does the market think the market thinks" situation — priced-in analysis, front-running a known catalyst, adversary anticipation in crises.
- **Sharpens:** (a) never model the market (or a state) as solving to equilibrium in one-shot/novel situations — model it at 1–2 steps from the salient anchor; (b) the profitable position is roughly **one step deeper than the modal crowd, not maximally deep** (over-thinking loses to the actual distribution); (c) Nash is a good predictor ONLY when few reasoning levels reach it from the anchor; (d) after repeated plays of the "same" event (Fed meetings, OPEC meetings), expect anchoring-convergence, not sudden depth.
- **Guardrail:** level-0 anchor specification is the whole game — mis-specify the naive anchor and every level is wrong. In novel geopolitical shocks the anchor is usually the headline itself.

### 12.12 Quantal response equilibrium — noisy best response, used honestly (McKelvey–Palfrey 1995 [extracted incl. its own falsifiability critique])
- **Result:** QRE replaces knife-edge best response with probabilistic response (Nash = zero-noise limit). CRITICAL caveat the research surfaced: **raw QRE is empirically vacuous** — it can rationalize ANY observed play without parametric structure (logit). Use it directionally, not as a fitted model. Its two robust directional lessons: the **own-payoff effect** (actors play actions with higher own payoffs more often than equilibrium mixing says — asymmetric matching pennies), and QRE can **fully REVERSE Nash comparative statics** (volunteer's dilemma: Nash says no-volunteer probability rises with group size; QRE says it falls — experiments confirm QRE).
- **Sharpens:** (a) discount any prediction resting on an actor holding a knife-edge mixed strategy; (b) in "someone must volunteer" coalitions (who intervenes, who enforces sanctions), larger groups make action MORE likely than free-rider Nash logic suggests; (c) never present a fitted QRE as evidence — logit-QRE intuitions only.

### 12.13 Finite-horizon reputation — the chain-store resolution (Kreps–Wilson 1982; Milgrom–Roberts 1982 [extracted])
- **Result:** a *tiny* prior probability that the incumbent is a genuine "commitment type" makes fighting rational for a WEAK incumbent in all but the final rounds — predation is an investment in deterrence. The equilibrium has an observable **three-phase structure**: pure toughness while reputation is high → a **mixed/randomization phase** as the end nears → certain acquiescence at the last stage. Deterrence holds "no matter how small" the commitment-type prior (unique among sequential equilibria).
- **Diagnostic:** early-round disproportionate toughness (sanctions enforced brutally on the first violator; a new Fed chair's first decision; a leader's first challenge) = reputation-investment phase, NOT proportionate response. Watch for the **mixing phase** (inconsistent enforcement) as the tell that the horizon is shortening, and **end-game unraveling** near terms/transitions/exits.
- **Sharpens:** (a) don't read early overreaction as irrational escalation — it's the cheapest point to buy reputation; (b) credibility predictions must be indexed to horizon position: the SAME actor rationally flips from tough to soft as the end approaches (lame-duck effects are structural, not psychological); (c) refines §12.7 — reputation DOES work with a commitment-type prior, but decays on schedule.
- **Guardrail:** requires a genuinely finite, commonly-known horizon; with indefinite horizons use §4 folk-theorem logic instead.

### 12.14 Beauty-contest amplification — rational bubbles from dispersed information (Angeletos–Lorenzoni–Pavan [extracted])
- **Result:** with two-way information spillovers between real investment and asset prices, **fully rational** agents produce equilibrium outcomes that respond LESS to fundamentals and MORE to noise — agents rationally tilt toward correlated signals to speculate on the market's predictable pricing errors. Price-fundamental disconnects do NOT imply irrationality.
- **Sharpens/REVERSES:** "this is a bubble, participants are irrational, it must mean-revert" is a non-sequitur — exuberant disconnects can be equilibrium behavior under dispersed information and can persist. A disconnect trade needs a *mechanism for the information structure to change* (the §13/reflexivity twilight test), not just the observation of disconnect.
- **Guardrail:** pairs with §12.2 — both are "information structure, not sentiment" results; neither licenses a timing call on its own.

### 12.15 Coverage gaps — STILL researched-empty, do not fabricate
Two rate-limited research passes have now covered §12.1–12.8 (verified) and §12.11–12.14 (verified/extracted per labels). Still genuinely unresearched: **Rubinstein/Abreu–Gul bargaining delay** (ceasefire/deal timing from patience + obstinacy posturing), **Aumann agreement / no-trade theorems** (what persistent public disagreement reveals), **mechanism & auction design** (OPEC quotas, procurement, treasury auctions, collusion diagnostics), **evolutionary dynamics** (tactic diffusion, drone-swarm/sanctions-workaround adoption curves), **network contagion thresholds** (Acemoglu et al. absorb-vs-amplify phase transition), **Kydland–Prescott time-consistency formalism** (which announced commitments lack enforcement technology), and **coalition/cooperative theory** (burden-sharing, empty-core fracture). Doctrine §10.5/§10.8 partial coverage still applies. Flag for the next pass; do not invent rules.

## 13. SOURCES (modern-GT module, §12)
- Morris & Shin, *Global Games: Theory and Applications* (2003 survey) — global-games core, σ_x/σ_z² knife-edge, publicity multiplier.
- Angeletos, MIT 14.462 lecture notes — uniqueness iff condition, threshold strategies.
- Morris & Shin, *Social Value of Public Information* (AER 2002) + Svensson (2005) — transparency paradox and its bound (contested; use bounded form only).
- Heinemann & Illing, *J. Int'l Economics* (2002) — common-knowledge destruction vs correlating device.
- Crawford & Sobel, *Econometrica* (1982) — cheap-talk N* partition; Sobel Paris lecture notes.
- Fujiwara & Waki, *Forward Guidance as Bayesian Persuasion* (CAMA WP 91/2019; RED 2022).
- Gehlbach, Luo, Shirikov & Vorobyev (2021) — optimal propaganda under censorship.
- Duffy & Heinemann, *J. Monetary Economics* (2021) — reputation/transparency vs commitment (lab).
