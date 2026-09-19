# PROFESSOR BACKTEST PROTOCOL — question-level alignment scoring
*Scaffolded 2026-07-13. Target video: ___ (awaiting link). Works for any Jiang lecture/Q&A; GT#20 "Mid-Term Examination" and the Geo-Strategy Q&As are ideal formats.*

## Purpose
Score the engine against the professor's OWN answers, question by question — a judgment backtest of the doctrine implementation, not of world outcomes. If the engine, running the four-skill stack on the same question, reaches a different answer than the professor, that's a datapoint: either (a) the engine mis-implements the doctrine (fix the skill), (b) the doctrine layer is being over/under-weighted vs the formal/market layers (fix the weights), or (c) the professor's answer itself fails the formal validity checklist (log it — the engine is ALLOWED to disagree where formal §10 wins; alignment is not the goal when validity conflicts, per CLAUDE.md rule 1).

## Protocol (anti-bias by construction)
1. **Transcript acquisition:** pull the full transcript with timestamps. Split into (question, professor-answer) pairs. Number them Q1..Qn.
2. **BLIND prediction pass:** for each question, the engine sees ONLY the question text + world state as of the video date (no answer text in context — process strictly question-first, and never read ahead). Output per question, BEFORE looking at the answer:
   - Predicted answer (2-4 sentences, in the professor's frame: which doctrine module he'll reach for)
   - Predicted stance direction (bullish/bearish/escalatory/dismissive/contrarian-to-audience)
   - Confidence 0-1 that the prediction matches his actual answer
   - Which doctrine sections (§) the engine used to predict
   - **Timeline-web fork:** if the question implies branching futures, sketch the 2-3 branches the professor would name, with his likely probabilities
3. **Reveal pass:** extract his actual answer. Score:
   - MATCH (same thesis + same mechanism) / PARTIAL (same direction, different mechanism) / MISS (different thesis)
   - Brier on the stated confidence (MATCH=1, PARTIAL=0.5, MISS=0)
4. **Divergence autopsy** (for every PARTIAL/MISS): which layer failed?
   - `doctrine-gap`: he used a move not yet in the skill → extract it, append to jiang-doctrine SKILL.md (new batch section)
   - `weighting`: engine had the module but weighted a different one → adjust CLAUDE.md guidance
   - `formal-override`: the engine disagreed BECAUSE validity checks failed → keep the disagreement, log his claim to the ledger as a scored prediction instead (doctrine §12.9 pattern)
   - `tier-c`: his answer is quarantined content (doctrine §6) → engine SHOULD diverge; no fix
5. **Report:** `reports/backtests/<video-id>.md` — per-question table, aggregate match rate, Brier, autopsy tally, and the doctrine deltas applied. Update the timeline web with any new branches his answers imply.
6. **Deep-dive trigger:** if match rate (excl. formal-override and tier-c rows) < 60%, run a full research pass on the failing doctrine areas before the next backtest.

## Scoring ledger
| Video | Date | Questions | MATCH | PARTIAL | MISS | Brier | Doctrine deltas |
|---|---|---|---|---|---|---|---|
| Breaking Points — "US Will LOSE Iran War" (singjupost transcript) | 2026-07-13 | 5 | 3 | 1 | 1 | 0.089 | §15.1 ally-desperation symmetry · §15.2 desal node · §15.3 petrodollar→AI-capex · §15.4 bribe-or-invade · §15.5 hubris weighting · §15.6 Tier-C quarantine · ledger #36/#37 · timeline houthi-saudi model corrected |
| Substack Founding Members Livestream #2 (youtube qRCSZoGC2Dg, FULL 2h55m sweep) | 2026-07-13 | 5 blind + full extraction | 2 | 1 | 2 | 0.229 | Doctrine batch 6 (§16.1–16.10) · ledger #38–#43 (invasion-by-Oct head-to-head vs #35) · heavy Tier-C quarantine · his factual-error log started · report: reports/backtests/jiang-livestream-2.md |

## Judgment evals (historical frozen cases — machinery test)
| Date | Cases | HIT | PARTIAL | MISS | Brier | Patches applied |
|---|---|---|---|---|---|---|
| 2026-07-13 | 1–3 (Russia '22, Red Sea '23, Evergrande '21) | 11 | 1 | 0 | ~0.085 | CORRIDOR branch added to market-transmission gate · expression-selection rule · FX map · endpoint-dated falsifiers · formal §10 items 23 (contagion channel test) + 24 (capital-committed precedence) · one-asset-per-row ledger rule. CAVEAT: contamination-disclosed machinery test, not live forecasting; cases 4–6 (over-fire discriminators) still to run; protocol fix pending (split inputs/ground-truth files). |
| 2026-07-14 | 4–6 OVER-FIRE (OPEC+ '23, Iran-Israel '24, Ever Given '21) | 11 | 1 | 0 | ~0.085 | THE over-fire test. Key finding: engine restraint is CONVERGENT (robust) on Case 5 (telegraphed war-spike fade — 4 independent rules) and Case 6 (short corridor) BUT ONE-RULE-DEEP (fragile) on Case 4 (OPEC+ cut) — the master gate alone over-fires a durable Branch-B bull; only the demand flip-test saved it. Patches APPLIED: market-transmission §1 SUPPLY split EXOGENOUS(persist)/ENDOGENOUS-cartel-cut(fade) · CORRIDOR duration now incentive-conditioned (cui-bono-on-prolongation) · doctrine §11.5b symmetric war-premium fade. HONESTY: Cases 5&6 are cited BY NAME in the skills they test (in-sample); Case 4 is the clean, uncontaminated finding. CORRIDOR needs genuine out-of-sample validation. |
