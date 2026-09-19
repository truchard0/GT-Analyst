# GT-Analyst — FULL BACKTEST & TRAINING PASS
**Run: 2026-08-01.** Every prediction audited, systematic biases measured, doctrine patched.
This is the first pass that looked at the ledger as a **portfolio** rather than a list — and
the portfolio view is where the real problems were.

---

## 1. THE SURFACE RECORD (and why it's misleading)
**12 resolved · 12 HIT · mean Brier 0.124.** Verdict breakdown:
- 10 `hit-clean` · 1 `hit-wrong-reason` (#13 — right outcome, wrong premise about Warsh, only
  rescued by the 7/16 correction) · 1 `partial` (#46 — PPI direction right, y/y wrong)

**This record is an artifact of maturity, not skill.** Nothing that *can* fail has matured yet.
Three escalation calls are failing or at risk right now:

| # | Call | P | Status |
|---|---|---|---|
| #63 | US strikes Yemen + escort by 8/4 | 0.75 | **FAILING** — US paused instead |
| #72 | US/Israel strike Iranian energy pre-Monday | 0.55 | **FAILING** — Trump stood down 8/1 |
| #59 | Ceasefire fails (no 10 strike-free days) | 0.72 | **AT RISK** — pause holding |

**Projected honest record: 12/15 = 80% hit rate, mean Brier ~0.192.** That — not 0.124 — is
the number to quote. **New standing rule: always publish the projected Brier including at-risk
calls.**

---

## 2. THE SYSTEMATIC BIAS: escalation over-prediction (3 strikes)
All three failing calls are the same shape, and all were logged at **high** probability
(0.75 / 0.72 / 0.55). The engine repeatedly read *escalation signals* as *escalation outcomes*.

**The aggravating detail:** on #72 the engine **named Trump's reversal pattern (§12.6) as
"the main brake" in that prediction's own sensitivity field — and still logged 0.55.**
Identifying a brake is not the same as weighting it.

**Counterfactual value of the fix:** applying the new §16.14 cap (0.35) to #63 and #72 alone
would have saved **~0.62 of cumulative Brier** — material at this sample size.

### → PATCH §16.14 (written): hard cap on strike-planning reports
> For a reversal-prone decider, a leaked strike plan is a **negotiating instrument, not a
> forecast** — the threat is made public *precisely so it can be traded away*. Absent a
> confirmed "go" order or ordnance released, **cap P(strike executes) at 0.35**, regardless of
> how strong the planning evidence looks (allied coordination, target lists, even market-hour
> sequencing). Escalate only on *execution* signals: aircraft launched, NOTAMs, carrier moves.
>
> **Corollary:** a stand-down is not a deal. Iran simultaneously denied movement toward a
> longer-term agreement. Don't flip from over-predicting escalation to over-predicting
> resolution — §16.12 oscillation cuts both ways.

---

## 3. THE PORTFOLIO PROBLEM (new, and the biggest finding)
**The iran-war cluster is 31 of 55 open predictions = 56% of the entire open book.**
That is *one correlated bet* presented as 31 independent ones — and it sits in the exact
cluster where the engine has a documented systematic bias. A single Iran resolution moves
more than half the ledger at once.

Directional lean inside it (**hand-corrected**, see §4): **9 escalation vs 6 de-escalation.**
A real lean, and it points the same way as the failures.

### → PATCH: portfolio hygiene (CLAUDE.md)
No cluster above ~35% of open predictions; over-weight clusters raise the bar for new calls;
calibration must be read **per cluster**, not just in aggregate.

---

## 4. A METHOD ERROR CAUGHT DURING THE AUDIT ITSELF
The first automated pass classified the iran-war lean as **18:3 escalation** — alarming, and
**wrong**. The keyword regex mislabelled *negation-form* predictions as escalation:
- #17 "Islamic Republic does **NOT** collapse" → tagged escalation (it's stability)
- #19 "**NO** return to war-scale conflict" → tagged escalation (it's de-escalation)
- #23 "Brent does **NOT** sustain above 80" → tagged escalation (it's oil-down)
- #26 "**No** Fed hike from oil" / #28 "oil-**DOWN** dovish branch" → same error

Hand-correction gives the true **9:6**. The bias is real but half what the automated pass
claimed — and the engine nearly published the inflated number.

### → PATCH: tag, don't infer
Every prediction gets an explicit **lean** tag (escalation / de-escalation / neutral) at
logging time. **Infer nothing you can tag.** Negation-form predictions defeat keyword
classifiers, and an audit that miscounts its own book is worse than no audit.

---

## 5. WHAT THE RECORD ACTUALLY VALIDATES (the genuine wins)
Not everything is a bias story. These held up under scrutiny:
- **#67 — the FOMC market-fade.** Engine 0.75 hold vs market ~0.65 (CME ~35% hike). Fed held
  with three dissents; majority waited for July/Aug CPI — *exactly* the no-SEP + data-lag +
  §11 look-through mechanism. Brier 0.06, the best on the book, and **benchmarked against a
  live market price** rather than self-graded.
- **#50/#52 — the capex cohort** (GOOGL $205B, META $130–145B, AMZN $220B, MSFT Azure +43%).
- **#61/#47 — the semis correction**, including the mid-week moment it *looked* wrong (SMH ran
  to 591) and was flagged at-risk in real time rather than rationalized. It then resolved HIT.
- **#44 — RTX** +12.8%, the only closed round-trip (+7.46% booked at the pre-registered target).

**The pattern:** the engine is strong where the mechanism is *structural and datable*
(Fed reaction functions, capex cycles, positioning unwinds, calendar arithmetic) and weak
where the outcome depends on **one person's discretionary choice** (Trump strike decisions).
That is a clean, actionable boundary — and it should govern where conviction is spent.

---

## 6. TRAINING ACTIONS TAKEN THIS PASS
| # | Patch | Where |
|---|---|---|
| 1 | Hard 0.35 cap on strike-planning reports; stand-down ≠ deal | jiang-doctrine §16.14 |
| 2 | Cluster concentration limit (~35%), per-cluster calibration | CLAUDE.md |
| 3 | Explicit lean tagging — infer nothing you can tag | CLAUDE.md |
| 4 | Publish projected Brier incl. at-risk calls, never the resolved-only figure | CLAUDE.md |
| 5 | #72 conviction 0.60→0.30, #68 restored 0.45→0.55, map re-weighted (off-ramp 0.45 now leads) | ledger + timelines |

## 7. OPEN QUESTIONS THIS PASS COULD NOT SETTLE
- **#38 (Jiang seed): US ground invasion of Iran by 2026-12-31, P=0.70** — looks increasingly
  unlikely after the stand-down, but it is the professor's call, not the engine's, and the
  head-to-head with the engine's frozen-conflict thesis (#35) is the point. Leave it; score it.
- Whether the de-escalation read is now *over*-corrected. §16.14's corollary exists precisely
  because the engine has now been caught leaning both directions once each.
- The conviction bands still don't discriminate (n too small): `<0.60` Brier 0.160 vs
  `0.60-0.80` 0.104 — directionally right (higher conviction = better) but not yet meaningful.
