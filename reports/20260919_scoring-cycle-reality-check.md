# Scoring cycle — predictions vs reality (2026-09-19)
**As-of:** 2026-09-19 · **Scope:** every ledger row past horizon (29) + 2 rows already decided by price (#33, #69) · **Method:** prices from daily OHLC bars (SPY/QQQ/SMH/XLE/USO/BNO/TSM/MU, 7/1–9/18); events from primary sources (BLS, TSMC IR, OPEC, AAA, Lloyd's List Intelligence, FAO) and wire/daily-log reporting, cross-checked. Ambiguous wording was scored **against** the engine.

## 1. Result
| | before | after |
|---|---|---|
| resolved | 14 | **44** (+1 void) |
| hit rate | 12/14 = 86% | **33/44 = 75%** |
| mean Brier | 0.169 | **0.211** |
| skill vs coin (0.25) | +0.33 | **+0.16** |
| skill vs own base rate | −0.38 | **−0.13** |
| Murphy resolution | — | **0.009** (threshold for "adds information": 0.02) |

This cycle alone: **21 HIT / 9 MISS / 1 VOID, Brier 0.231.** The 8/1 maturity-bias warning was right: the 12/12 was an artifact of which rows had matured.

**HIT (21):** #15 #17 #18 #20 #21 #22 #25 #32 #33 #49 #51 #58 #60 #65 #66 #68 #71 #73 #75 #77 #78
**MISS (9):** #19 #24 #28 #29 #39 #59 #69 #74 #76 · **VOID:** #23 (own carve-out: Hormuz re-closed)
Five of the hits are **hit-wrong-reason** (#15 #20 #21 #68, and #23 partial): they scored because the premise they were built on was false, or on an easier clause than the headline claim.

## 2. What the numbers say
1. **The engine picks the right side 3 times in 4, but its probabilities carry no information.** Misses were stated at a *higher* mean P (0.675) than hits (0.654). The calibration curve is inverted: P < 0.60 → 82% hit · 0.60–0.70 → 80% · P ≥ 0.70 → 67%. Confidence has tracked how vivid the tape was, not how robust the mechanism was.
2. **One error shape accounts for 8 of the 11 misses in the book: extrapolating the current leg of the Iran/oil oscillation.** 0-for-8, Brier 0.47:
   - logged on the peace leg (7/8–7/11), killed by the war resuming: #19, #28, #29
   - logged on the war leg (7/21–8/2), killed by the pause: #59, #63, #72
   - logged on the relief leg (8/4), killed by the re-rally two sessions later: #74, #76
   Everything else in the book: **33-for-36, Brier 0.155.** (Classification is post-hoc; treat the split as a hypothesis the next 20 rows must confirm.)
3. **Where the edge is:** rows built on physical or institutional invariants went **8-for-8 (Brier 0.10)** inside the same cluster — regime survives (#17), Mojtaba invisible (#18), Hormuz does not normalize (#22, #73), more maritime attacks (#15), Saudi exports −33% (#58), Brent prints 100 (#60), crude → CPI with a lag (#32). Scheduled-print rows backed by arithmetic went 12/14 (the CPI nowcast module landed every point estimate on July CPI).
4. **Energy-direction is worse than a coin** (sector `energy` Brier 0.33; `oil-tape` 0.56; `opec-policy` 0.34). Short-fuse (≤7d) rows are the best horizon (9/11, Brier 0.15).
5. **Process defects found:** #33 (MU < 800) resolved on **7/28** and sat open for seven weeks; trade #2's pre-registered 800 target was touched the same day and never booked (STATE.md still carried it open at 892 on 8/4; MU has since traded 1042 on 9/9, through the 1035 invalidation line intraday). #69 was dead on 8/4 and stayed "live" in STATE.md. The engine only looks at a row when its horizon arrives.
6. **Wording defects:** #59 turned on whether IRGC tanker hits count as "Iranian strikes"; #68's "i.e." clause scored an easier proposition than its headline; #21's OR-leg (Israel hits a proxy) had a ~0.95 base rate and was priced 0.58; #69 compounded three assets; #23/#32 needed judgment calls on "sustains".

## 3. What changed in the engine
| Change | Where | Evidence it answers |
|---|---|---|
| **Leg-neutral gate** — same direction as the last 10 sessions of tape → cap 0.55 or re-express as an invariant; max one same-direction iran/oil row per session | jiang-doctrine **16.15** | 0-for-8 |
| **Premise-liveness check** — state-premise rows need a primary datapoint < 24h old | jiang-doctrine **16.16** | 7/8 batch logged on "ceasefire holds" a day after it broke |
| Jiang scorecard: direction yes, clock no | jiang-doctrine **16.17** | #39 |
| **No-view odds** for every level/range row | market-transmission **13f** + new `tools/range_odds.py` | #69 (needed +0.5 over arithmetic) |
| Pass-through uses the window average; never downgrade a lag thesis on < 1 lag-length | market-transmission **13g** | #76 vs #32 |
| RV between a 3-vol and a 1-vol leg is a levered direction call | market-transmission **13h** | #74 |
| A circulating number beats a long-run prior; P ≥ 0.80 on a print needs the quarter guide | market-transmission **13i** | #24 |
| Gate step 7 (applies to **every** row, not just conviction ≥ 0.65) + state-of-the-book note: P ≥ 0.70 reserved for invariant/arithmetic rows until resolution > 0.02 | contrarian-red-team Part B/C | inverted calibration |
| `ledger.py`: `void` command · `--lean` tag (hygiene rule 2 finally has a column) · `add --dry-run` wording lint (compound AND, easy-leg OR, conditional without void clause, vague threshold, unscoped "strike", state-premise, level/range) · report now prints skill vs coin/base-rate, per-cluster, per-horizon, per-source Brier and mean-stated-vs-actual gaps | `pipeline/ledger.py` | §2.5–2.6 |

Run against the 77 historical rows, the lint flags every one of the wording failures above (#69, #59, #21, #63, #39, #23, #19, #28).

## 4. Open book — what to look at next
- **#70** (SMH underperforms SPY to 9/30, 0.58): tracking MISS — SMH +6.0% vs SPY +2.0% at 9/18.
- **#11** (GL-X bearish for crude to 10/4, 0.55): Brent ~104; tracking MISS unless the "no new supply shock" carve-out is invoked → it would be the second void on the same premise. Decide the reading *before* 10/4.
- **#27** (if Brent > 90 on Iran, SMH underperforms XLE next month, 0.72): trigger looks live since 8/31; SMH +2.9% vs XLE +0.5% so far — tracking MISS.
- **#16** (Israel strikes Iran proper by 2027-01-08, **0.74**): Israel has not struck Iran 7/8–9/18 and sat out the July campaign. Over-priced on the evidence that resolved #21.
- **#38** (Jiang: US ground invasion by 12/31, 0.70) and **#36**: no ground troops as of 9/18.
- **#14** tracking HIT (10/8) · **#30** leaning HIT, wording judgment needed (10/11) · **#62** PMMS (10/1).
- **Trade #2 (MU short 937): BOOKED** at the pre-registered 800 target, dated 7/28 (open 839.61, low 789.09 - a cover limit at 800 fills at 800) = **+14.62%**; realized P&L now +22.08% summed over 2 closed round-trips. Booked at the target, not the 737.88 hindsight low (lesson 4). Had it stayed open, MU printed 1042.40 on 9/9 against the 1035 invalidation. This is the engine's rule-based bookkeeping, not a statement about any live brokerage position.
- iran-war is still 14 of 32 open rows (44%) vs the 35% cap.

## 5. Sources
BLS CPI (Jul, Aug) and Employment Situation (Jul) releases · TSMC 2Q26 earnings release · OPEC 2 Aug 2026 press release · AAA gas prices (Aug) · Lloyd's List Intelligence Strait of Hormuz briefs (5 Aug, 12 Aug) · USNI News 28 Aug · Al Jazeera (23 Jul, 14 Aug, 16 Aug, 27 Aug) · ABC News ceasefire timeline · JINSA Iran War Update 9/2 · GlobalSecurity.org daily Iran-war updates · gCaptain/Bloomberg tanker tracking (2 Sep) · FAO Food Price Index · CSIS Pickaxe Mountain imagery (9 Sep) · DHS 17 Jul release via HSToday/Democracy Docket/NBC · Rigzone/Yahoo BZ=F for Brent closes. Per-row facts are in each row's lesson (`ledger.py`) and on its timeline node.

*Analysis, not advice (doctrine §14).*
