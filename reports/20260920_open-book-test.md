# Open-book test — every open prediction vs reality (2026-09-20)
**As-of:** 2026-09-20 18:00Z · **Scope:** all 32 rows that were open after the 9/19 scoring cycle · **Method:** prices from daily bars through the 9/18 close; events from primary documents (Fed statement + presser transcript, Freddie Mac PMMS, OFAC, P.L. 119-103, IAEA, SCOTUS) and wire / daily-log reporting gathered by three independent fact-check passes. Ambiguous wording is scored **against** the engine. A row is resolved early only when its outcome can no longer change.

> **Verification note.** The two facts that carry the most weight — the Fed's 9/16 hike and the 7/17 Kuwait desalination strike — were each checked twice: by the fact-check pass and then by me against the primary page (the Fed's 9/16 release; the AP report). One nuance from that second look: the AP piece reports the strike and Kuwait's damage statement; the IRGC's "we aimed at a US installation" line comes from the daily war logs, not from AP. Links in §6.

## 1. What changed today
| | 9/19 | 9/20 |
|---|---|---|
| resolved | 44 | **47** |
| void | 1 | **2** |
| open | 32 | **28** |
| hits / misses | 33 / 11 | **35 / 12** |
| mean Brier | 0.211 | **0.220** |

**Resolved now (outcome can no longer change):**
| # | Call | P | Result | Brier |
|---|---|---|---|---|
| **#26** | No Fed hike attributable to an Iran/oil inflation shock by 2027-01-09 — "the Fed holds or looks through even on a spike" | **0.80** | **MISS** | 0.64 |
| **#10** | The June MOU does NOT yield a durable US–Iran peace within 12 months | 0.70 | HIT | 0.09 |
| **#37** | (Jiang seed) Attributed Iranian/proxy strike or plot against GCC desalination within 12 months | 0.40 | HIT | 0.36 |
| **#11** | GL X is bearish for crude over 3 months, *absent a Hormuz disruption* | 0.55 | **VOID** | — |

## 2. The headline: the Fed hiked, and the engine's flagship thesis broke
On **2026-09-16 the FOMC raised the target range 25bp to 3.75–4.00%, 12–0** — the first hike since 2023. The dots show one more in 2026.

- The engine's 7/29 "flagship win" (#67, fade the market's hike odds) rested on **supply-shock look-through**: the Fed would not hike into an oil spike. #26 extended that to six months at **P = 0.80**. It lasted ten weeks.
- **Why MISS and not "unclear":** the statement itself does not name energy, oil or Iran, and Warsh said "we cannot affect… oil prices." But headline PCE ran 3.6% against core 3.2%, he framed the hike as stopping "relative price changes in some sectors" from broadening into "second and third order effects," and he named the changed **geopolitical situation** as one of three reasons for a unanimous decision. The prediction said the Fed would *hold or look through*. It did neither. The literal falsifier ("cites energy… as a driver") is arguable; the claim is not. Scored against the engine. The 9/16 minutes (due ~10/7) are the check on the attribution.
- **What the engine got wrong:** it treated look-through as a *policy* when it was a *one-meeting grace period*. On 7/29 three members already dissented for a hike and the majority said explicitly they were waiting for the July/August CPI. The engine logged that fact in its own win note — and still priced "no hike for six months" at 0.80. August CPI then printed +0.4 (#32, which the engine also called). **It held two rows that contradicted each other and was most confident in the wrong one.** That is lesson 7 from yesterday, again, one day later, at the highest probability in the book.
- This is the **second 0.80 to miss** (after #24, TSMC margin). Rows at P ≥ 0.80 are now **3 for 5**; the three hits were all "X does not happen within days/weeks" (#73, #65, #17). Rule R13 already reserves P ≥ 0.70 for invariant and scheduled-print rows; #26 was neither — it was a six-month call on a committee's discretion.

## 3. The other three
- **#10 HIT (0.70).** Kinetic exchange resumed 7/8–9; OFAC revoked GL X on 7/7 and Treasury launched "Operation Economic Outcast" on 8/24. A ratified peace plus twelve clean months inside the window is now impossible. Clean, structural, and correctly sized.
- **#37 HIT (0.40), with a caveat.** On 7/17 — four days after logging — an Iranian strike damaged a power-and-desalination plant in Kuwait; Kuwait attributed it to Iran; the IRGC claimed the strike but said it aimed at a US installation. The row says "strike… *against* GCC desalination infrastructure"; a grader who demands proven intent could contest it. The strike and the attribution are not in doubt, and desalination plants on both sides had already been hit or damaged earlier in the war (AP cites Kuwait's Doha West plant, Iranian plants on Qeshm, and Houthi attacks on Saudi facilities), which makes accident a thin defence. This is Jiang's §15.2 "desalination = the GCC existential node" call landing — and it was **under-priced**: with desalination plants already damaged in this war when it was logged, 0.40 ignored the base rate. Yesterday's fact-check pass missed this strike; today's found it.
- **#11 VOID.** Same carve-out, same premise, same death as #23: "absent a Hormuz disruption." Worse on inspection: the row says GL X was a July event; OFAC dated it **June 21**, Brent had already fallen from 80.57 to ~72 on it, and the licence was **revoked on 7/7, three days after the row was logged on 7/4**. The thesis was right for two weeks *before* it was written down. Doctrine 16.16 (premise-liveness) exists because of rows like this.

## 4. Every open row, tested
**Tracking MISS — these are likely losses; do not be surprised by them**
| # | Call | P | Horizon | Where it stands |
|---|---|---|---|---|
| #70 | SMH underperforms SPY, 7/31→9/30 | 0.58 | 9/30 | SMH **+6.0%** vs SPY **+2.0%** at 9/18. Seven sessions left; needs a ~4-point swing. |
| #27 | IF Brent >90 on Iran THEN SMH < XLE over the next month | 0.72 | 1/9/27 | Trigger fired 8/31 (Brent >90 on all 15 sessions since, peak 108.75). SMH **+2.9%** vs XLE **+0.5%** so far. Judged ~9/30. The hike did not derate semis relative to energy. |
| #38 | Jiang: US ground invasion of Iran by 12/31 | 0.70 | 12/31 | No ground troops. Posture is air + naval blockade. 9/20 escalation talk is about *strikes*. |
| #36 | US ground troops OR a compensated-cessation deal | 0.45 | 1/13/27 | Neither. Iran's 9/19 six conditions ask for frozen funds (and drop reparations); no US reply. |
| #2 | US introduces a draft after automatic registration | 0.50 | 6/30/27 | Registration rules were *withdrawn* 7/23; switch-over date 12/18; no induction bill anywhere. |
| #3 | Pentagon ~$1.5T in FY27 | 0.55 | 1/31/27 | Nothing enacted. CR (P.L. 119-103) holds DOD at ~$838B to 12/11. House NDAA $1.15T; reconciliation carries $60B of the $350B asked. Best plausible package ≈ $1.2–1.28T. **The row needs a rule now for "nothing enacted by the horizon" — I would score that a MISS (the prediction is that the budget *reaches* $1.5T).** |
| #54 | 2027 hyperscaler capex grows < +25% | 0.55 | 12/31/27 | Too early, leaning miss: 2026 guidance is +77–80%; 2027 consensus drifted from +22% (June) to ~+29% (August). First real signal: Q3 calls, late October. |

**Tracking HIT**
| # | Call | P | Horizon | Where it stands |
|---|---|---|---|---|
| #62 | 30y mortgage +25bp vs the 7/23 print, never −15bp | 0.62 | 10/1 | 6.58 → **6.95** (+37bp, cleared 9/17); never printed below baseline. Two prints left; 12bp cushion if judged at the 10/1 print. The hike that killed #26 is what is paying this row. |
| #14 | Succession contested / not publicly exercised | 0.62 | 10/8 | Mojtaba: no public appearance in six months; governs by written decree; 9/16–17 hardliner move against Pezeshkian; IRGC faction clashes. Flips only on a verified appearance. |
| #12 | No enforced, published Hormuz toll at 1/4/27 | 0.62 | 1/4/27 | "No published toll system exists." An unpublished case-by-case IRGC fee practice does. The Iran–Oman corridor (agreed 8/26) is not in effect. |
| #53 | No PLA kinetic action on Taiwan in 2026; China presses de-escalation | 0.93 | 12/31 | PLA ADIZ sorties −52% y/y; no blockade. Wang Yi 9/16: "reopen the Strait of Hormuz at an early date." Counter-signals are rhetorical (IAEA No vote, MANPAD sales). |
| #56 | Midterms held + a federal intervention / certification fight | 0.55 | 11/30 | The fight is already here: DHS grant coercion, 23 states suing, DOJ suing 20+ states for voter files, HSI "surge" in nine states, SCOTUS **blocking** the USPS mail-ballot rule 9/15. Needs only the election held on schedule. |
| #35 | Frozen conflict by 7/13/27 (no treaty, no 30-day war-scale campaign) | 0.55 | 7/13/27 | Round 2 ~23 days, round 3 ~10 days, fire pause day 10. **Under threat today:** Iran says it has been told the US is preparing to resume strikes; Trump left Camp David early. |
| #1 | War continues for years, no durable treaty | 0.70 | 4/21/28 | Day 204; three collapses; sanctions back; file referred to the UNSC 9/9. |
| #43 | No durable Russia–Ukraine peace through 2028 | 0.75 | 12/31/28 | Witkoff/Kushner shuttle 9/5–6: no agreement, no ceasefire. |
| #42 | No PLA invasion of Taiwan through 2028 | 0.85 | 12/31/28 | Exercises only. |
| #40 | Major European NATO state begins Russia-tied conscription expansion | 0.55 | 12/31/28 | Not yet. Germany's law predates the row and is voluntary; mandatory *screening* starts 7/1/27; a Bundestag activation vote is expected by ~July 2027. France and Poland are voluntary. |

**Genuinely ambiguous — decide the reading before the date, not after**
| # | Call | P | Horizon | The question |
|---|---|---|---|---|
| #30 | Credible IAEA / intelligence reporting of Iranian moves to reconstitute enrichment | 0.52 | 10/11 | For: WSJ 7/21 (Israeli intelligence, US officials concurring: thousands of centrifuges moved into Pickaxe Mountain), CSIS 9/9 (record construction), Grossi 9/10–11 (activity confirmed), NPT-withdrawal bill 9/20. Against: the centrifuge move dates to autumn 2025, US intelligence says no enrichment since June 2025, CSIS says "not yet capable," Grossi has "no concrete information," and the IAEA Board's 9/9 UNSC referral rested on non-compliance, not reconstitution. **My read: the 7/21 intelligence report is "credible reporting of moves" and the row is a HIT on its wording — but I have not resolved it, because you should agree the reading first.** |
| #16 | Israel strikes Iranian territory / assets by 1/8/27 | **0.74** | 1/8/27 | Nothing since 7/8; Israel sat out the whole July campaign ("US wants no Israeli involvement"). Still over-priced — *unless* a renewed US round this week pulls Israel in. |

**Too early to say anything useful:** #34 (nuclear test/declaration — precursors only: NPT bill, 441 kg of 60% unverified), #5 (Russia/Cuba — the chokepoint incidents are NATO boarding Russian ships, the reverse of the call), #41 (no SCOTUS vacancy; Alito staying the term), #7, #6, #55, #57, #8, #4.

## 5. What this does to the picture
1. **The fed-macro lane flipped branch.** The engine's tree still carried the hawkish-hold world. The Fed is now in a hiking cycle into a supply shock: the market-transmission skill's **Branch B** (supply/inflationary → rate-hike odds up → long-duration derate) is the live regime, not the tail. Yet the derate did *not* show up where the engine said it would (#70, #27 both tracking miss): semis have out-run both SPY and energy since 8/31. The mechanism fired; the asset mapping did not. That is the next thing to understand, and it should not be papered over.
2. **The calibration finding from yesterday got stronger, not weaker.** P ≥ 0.70 rows are now **13 for 20 (65%)**; P < 0.60 rows are **10 for 12 (83%)**; skill against the engine's own base rate fell to −0.16. The engine's confidence is still inversely informative. #26 is the cleanest example yet: the most confident row in its cluster was the one the engine's own evidence argued against.
3. **Jiang's scorecard: 1 hit, 1 miss.** #37 (desalination) landed; #39 (emergency by 8/31) did not. Both fit "right about the node, wrong about the clock" — and #38 (ground invasion by year-end, 0.70) is tracking the same way.
4. **This week matters.** Iran's six conditions (9/19) and the reports that the US is preparing to resume strikes (9/20) point in opposite directions inside 24 hours. That is the oscillation again (doctrine 16.15). No new iran/oil direction row should be logged off either headline.

## 5b. What changed in the engine today
- **market-transmission 11a — look-through has a clock:** price central-bank rows per meeting; dissent count + a named print = a scheduled hike; a Fed row must agree with the engine's own CPI row; never write a falsifier that turns on the statement's vocabulary. Also records the open puzzle: the hike moved rates but not the equity derate leg — such rows are capped at 0.55 until that is explained.
- **contrarian-red-team:** reference class = *recurrence* when the event type has already happened in the same conflict (#37); P ≥ 0.80 now needs a second independent line of evidence.
- **Tree:** 7 new nodes (round-3, fire-pause-sept, us-strikes-resume 0.45, iran-six-conditions 0.25, iaea-unsc-referral, fomc-sept-hike, fomc-oct 0.60), status evidence on every node holding an open row, root re-weighted to flip-b 0.45 / frozen-oscillation 0.40, catalyst board through 12/11.
- The two new forward nodes (`us-strikes-resume`, `fomc-oct`) are **tree probabilities, not ledger rows**. Doctrine 16.15 forbids logging an iran/oil direction call off a same-day headline; the Fed node can become a row through the analyst's gates if you want it staked.

## 6. Primary sources to confirm the two load-bearing facts
- Fed, 9/16 statement: https://www.federalreserve.gov/newsevents/pressreleases/monetary20260916a.htm · presser: https://www.federalreserve.gov/mediacenter/files/FOMCpresconf20260916.pdf · 7/29 statement: https://www.federalreserve.gov/newsevents/pressreleases/monetary20260729a.htm
- AP via KSAT, 7/17 Kuwait desalination strike: https://www.ksat.com/news/world/2026/07/17/iranian-strike-damages-a-kuwait-desalination-plant-exposing-water-vulnerability-in-dry-mideast/

**Other sources:** Freddie Mac PMMS releases (6.58 on 7/23; 6.95 on 9/17) · OFAC recent actions 6/22 and 7/7 (GL X, GL X1) · Paul Hastings / NatLawReview on Operation Economic Outcast · White House, H.R. 6500 signed (P.L. 119-103) · CSIS FY27 defense tracker · Air & Space Forces · Breaking Defense · Al Jazeera 9/20 (Iran's conditions), 9/9 (IAEA referral), 8/26 (Iran–Oman corridor) · Times of Israel 9/20 · Asharq Al-Awsat 9/20 · USNI News 9/18 (Hormuz transits) · GlobalSecurity.org daily Iran-war reports 9/17–9/19 · CSIS Pickaxe Mountain imagery · Israel Hayom / JPost on the 7/21 WSJ report · The National 9/16 (Wang Yi) · AEI China–Taiwan update 9/4 · Votebeat 9/15 and 8/24 · SCOTUS 26A124 · Brennan Center · House of Commons Library CBP-12198 · Al Jazeera 7/29 and ICDS on German military service · Goldman / Morgan Stanley capex notes via Investing.com and TechTimes · investing.com and Yahoo BZ=F for Brent closes.

*Analysis, not advice (doctrine §14).*
