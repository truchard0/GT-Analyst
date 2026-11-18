---
name: ai-trade
description: Forecasting framework for the AI trade (the AI capex cycle - Nvidia and semis, hyperscalers, neoclouds, memory, power, AI labs and IPOs, the financing chain, export policy). Splits the trade into five layers with different, measured predictability - prints, capex plans, financing, constraints and policy, price - and says which calls are allowed in each and at what confidence. Core rules - call the prints, not the reaction; financing is the first failure point; equities peak before capex; price direction is a no-call unless a tail base rate or a financing trigger licenses it. Use on any AI-capex, semis, hyperscaler, neocloud, memory or AI-lab item, alongside market-transmission (rates channel) and contrarian-red-team (gate and caps).
---

# THE AI TRADE - a layered forecasting framework

Built 2026-11-18 from six research strands (`research_notes/AI trade forecasting framework/`, synthesis in
`reports/AI trade forecasting framework.md`). **Source quality is mixed:** many historical figures come from
secondary sources or search summaries and are flagged there. Laws below marked [S] rest on such sources and get
half weight until checked against a primary. Doctrine §14 binds: direction and mechanism, never sizing.

This skill replaces the blanket "AI-complex calls are capped at P 0.55" in market-transmission §5.2 with a rule
per layer (§5 below). The §5.2a stress gate (`tools/ai_stress_index.py`) stays as one input to Layer 3.

---

## 1. THE FIVE LAYERS (classify every item before forming a call)

| Layer | What it is | Predictability | Call type allowed |
|---|---|---|---|
| **L1 Prints** | Reported revenue, margins and next-quarter guides of suppliers and buyers, against the company's OWN prior guidance | HIGH | Threshold calls at 0.80-0.92 |
| **L2 Capex plans** | Buyers' forward spending guidance (annual capex, "meaningfully more") | MEDIUM-HIGH near term, low beyond one guidance cycle | "No cut" and threshold calls at 0.65-0.90 |
| **L3 Financing** | Debt, leases, guarantees, vendor finance, IPO window, ratings, CDS | MEDIUM; it is the leading layer | State calls (default, rating, deal clears) at the confidence the evidence supports |
| **L4 Constraints and policy** | Power, packaging, export rules, tariffs, hearings | Power and auctions MEDIUM; government decisions LOW | State calls for measured outcomes; decision calls capped 0.35-0.65 |
| **L5 Price** | Index and share-price direction and levels | LOW | No call, except §5 rules 6-7 |

**The master rule: never infer L5 from L1.** A beat does not predict the reaction. The Magnificent 7 beat in 6-7 of
7 in the quarters checked; Nvidia closed higher the day after earnings only 55% of the time since 2016 and fell after
four straight beat-and-raise quarters to February 2026 [S]. On 17 Nov 2026 it beat by $6.7bn, guided $5bn above
consensus, and the last after-hours trade was +0.9%.

---

## 2. LAWS FROM PAST CAPEX BOOMS (base rates; state them before the inside view)

1. **Equities peak before capex.** Held in all four dated episodes: UK railway shares peaked Oct 1845, spending in
   1847; Cisco peaked Mar 2000 while carrier capex was still rising to its 2000 peak; in 2018-19 and 2022-23 Nvidia
   and the SOX bottomed before hyperscaler capex turned [S]. **Consequence:** a falling equity complex with rising
   capex guides is the normal late-cycle pattern, not a contradiction. Do not use capex guides to call a price floor.
2. **Capex-cut depth scales with external financing.** Debt-funded builders cut 50-80% (telecom carriers 60% by 2002,
   CLECs 80%, shale 51% in three quarters); cash-funded hyperscalers cut 2% y/y for two quarters in 2019 [S].
   **Consequence:** the variable to track is the FUNDING MIX, not demand. See §3.
3. **Intensity is at telecom-peak levels.** Carriers spent 30-40% of revenue at the 2000 peak against a 20% norm [S];
   Meta 44% and Microsoft 39% in 2025; 2026 hyperscaler capex is near 100% of operating cash flow against a 40%
   ten-year average (UBS) [S].
4. **Vendor financing is the classic tell.** Lucent's commitments were ~24% of revenue and unwound in ~15 months
   with $3.5bn of provisions [S]. Nvidia (10-Q, quarter to 26 Jul 2026): $108.5bn of guarantees inside $530.5bn of
   total commitments plus guarantees; ~$164.5bn is customer credit support, dominated by a $105bn lease guarantee on
   an OpenAI-leased campus. **Never call the $530bn "guarantees".** The tell is the next 10-Q: flat or shrinking
   support lines = withdrawal.
5. **Semis drawdowns have a shape.** Seven completed SOX drawdowns of 20%+ since 2004: median depth 35%, median 9
   months peak to trough, median 5 months from trough to a new high [S]. Memory equities lead memory fundamentals by
   1-2 quarters and fall 50-60% per cycle.
6. **Run-ups predict crash risk, not low mean returns.** A 100% two-year industry run-up puts the probability of a
   40% crash near 53%, 150% near 80% (Greenwood-Shleifer-You). Valuation explains little of one-year returns.
7. **Hiking cycles alone do not sink tech.** Flat to up in 4 of 5 cycles since 1994; 2022 was the exception [S].
   In 2026 itself SMH rose 16% from the September hike day to 5 Oct. Rates matter through L3 (refinancing cost),
   not through a discount-rate reflex (market-transmission §5.1).
8. **The second-derivative rule is contested.** Do not time a peak off the growth-rate peak alone [S].

---

## 3. THE REGIME SWITCH: cash-funded sprint -> debt-funded build

The single most important classification. Law 2 says the two regimes have different cut distributions.

| Test | Cash-funded | Debt-funded | Reading 18 Nov 2026 |
|---|---|---|---|
| Hyperscaler free cash flow | positive | negative | negative at Alphabet, Meta, Oracle, Amazon (TTM) |
| Bond issuance vs forecast | at or below | above | $296bn YTD vs Goldman's $250bn full-year |
| Off-balance-sheet vehicles | rare | pricing wider each deal | 6.58% (2025) -> above 7% (Jul 2026); QTS placed $300m of $800m |
| Weakest borrower's access | open | shut | no high-yield data-center deal since late Sept; CoreWeave CDS ~1,113bp |
| Vendor as guarantor | no | yes | Nvidia guarantees $108.5-118bn; CEO who built it resigned 12 Nov |

**Reading: 5 of 5 on the debt-funded side for the marginal builder.** The big four still have balance sheets, so
the cut distribution is a mixture: neoclouds and single-tenant vehicles sit in the 50-80% class if access stays
shut; the four hyperscalers sit between. A call on aggregate capex must say which class it is about.

---

## 4. THE INDICATOR BOARD (update every cycle; these move the L5 tree and license L3 calls)

| Gauge | Level (date) | Tightening trigger | Loosening trigger |
|---|---|---|---|
| CoreWeave 5y CDS | ~1,113bp (17 Nov); peak 1,289bp (5 Nov) | new high above 1,289bp | below 700bp |
| Oracle 5y CDS / ratings | ~300bp; S&P BBB- stable, Moody's Baa2 negative | new record above 343bp; Moody's to Baa3; any junk rating | Moody's outlook to stable |
| High-yield data-center primary | 0 deals since late Sept | stays shut into 2027 | first deal of $500m+ clears |
| AI credit vs IG index | +44bp (Nov) | wider | tighter |
| Hyperscaler initial 2027 capex guides | due late Jan - early Feb 2027 | any of the four guides below 2026 | all four above, two with numbers above consensus |
| Nvidia support lines (10-Q) | $108.5bn guarantees (Jul), ~$118bn (Oct, press) | flat or lower | n/a (rising = more vendor finance, a later risk) |
| DRAM contract price q/q | ~+20% in 4Q26, gains narrowing | flat or down | re-accelerating |
| Fund-manager tech overweight (BofA) | 12% (Nov), from 37% | below 0 | back above 25% |
| `ai_stress_index` weekly z | -1.25 (17 Nov), gate off | z >= 1.0 | n/a |
| 10-year Treasury | 5.10% (17 Nov) | above 5.25% | below 4.75% |

Two or more tightening triggers in one cycle = "financing accident" branch up by at least 0.10. Two or more
loosening triggers = "repair" branch up by at least 0.10.

---

## 5. CALL RULES

1. **Thresholds come from the company's own guidance**, never from aggregator consensus (stale consensus sat below
   Micron's own guided range in Nov 2026). State the guide and its date in the event field.
2. **One number, one row.** A print call and a guide call are separate rows. No "beats and raises" conjunctions
   (formal §8.1).
3. **Unannounced dates get a void rule.** If the report date is a pattern estimate, set the horizon a week past it
   and pre-register: not reported by the horizon -> extend the horizon, do not score.
4. **L1 calls: 0.80-0.92.** A company clearing the midpoint of its own guide is the base case; go below 0.80 only
   with a named reason (a 14-week quarter flattering the guide, a known customer push-out).
5. **L2 calls say which funding class they are about** (§3) and never extend past one guidance cycle at above 0.65.
6. **L5 direction and level calls are "no call"** and are published as scenario odds on the timeline, not ledgered.
   Two exceptions:
   - **Tail base-rate calls.** A bounded statement whose reference-class base rate is 0.85 or more (for example, no
     new all-time high within N months while a 30%+ drawdown has not yet troughed). Ledger at the base rate, kind
     `markets`, with the class named in the sensitivity.
   - **Financing-triggered underperform calls.** Allowed up to 0.65 only when two §4 tightening triggers have fired
     AND the `ai_stress_index` gate is on.
7. **No price call on Anthropic (ANT).** The analyst is an Anthropic model. Treat the listing as an L3 gauge (does a
   $64bn deal clear, at what price against the range) and say why there is no call.
8. **Government decisions are decision-kind calls**, capped 0.35-0.65 (contrarian C.2). A rule issued days before a
   summit by a reversal-prone decider is a bargaining chip until it survives the summit (jiang 16.14).
9. **War ban interplay.** Power-price and capacity-auction outcomes are measured-state calls and are allowed; do not
   name energy or defense sector tickers on any row.
10. **Clusters:** `ai-prints` (L1), `ai-capex` (L2), `ai-financing` (L3), `ai-policy` and `power` (L4), `ai-price`
    (L5). They are correlated through demand; read calibration per cluster and treat `ai-prints` + `ai-capex` as one
    effective bet when a miss comes from demand.

---

## 6. THE L5 SCENARIO TREE (maintained on the timeline as `ai-trade-h1-2027`; not ledgered)

Measured on the SMH close on 30 June 2027, from 460.10 on 17 Nov 2026 (31.5% below the 22 June 2026 high, about 5
months into a drawdown already at the median depth of law 5).

| Branch | SMH on 30 Jun 2027 | Start odds | What it needs |
|---|---|---|---|
| Repair | at or above 520 | 0.35 | 2027 capex guides hold, high-yield primary reopens, CoreWeave CDS below 700bp |
| Range | 400-520 | 0.40 | prints hold, financing stays selective, the Fed keeps hiking |
| Second leg | below 400 | 0.25 | a financing accident (neocloud restructuring, a junk rating for Oracle) or a hyperscaler capex cut |

All three are in the no-call zone by construction. The tree exists to be moved by §4, and its moves are the product.

---

## 7. CHECKLIST ADDITIONS (run on every AI-trade item, after formal §10 and market-transmission §13b)

26. **Layer:** is the item L1, L2, L3, L4 or L5, and is the call type one that layer allows?
27. **No L1 -> L5 inference:** does any price statement rest on a print? If so, delete it.
28. **Funding class:** for a capex call, cash-funded or debt-funded builder (§3)?
29. **Own-guidance threshold:** is the number the company's own guide, with its date?
30. **Board update:** which §4 gauges moved, and did two triggers fire on one side?

## 8. FORWARD TEST (this framework is provisional)

Every rule here is in-sample to the 2026 research pass. Score by layer once 10 calls in a layer have resolved:
- L1 hit rate below 0.80 -> the "prints are predictable" premise failed; drop the band to 0.65-0.80.
- L2/L3 Brier worse than 0.20 -> cap them at 0.65.
- Tail base-rate calls (rule 6): two misses in the first five -> remove the exception.
- If the L5 tree's largest branch is wrong on 30 Jun 2027, record which §4 gauges failed to move it.
