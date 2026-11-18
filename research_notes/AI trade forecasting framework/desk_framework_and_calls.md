# Desk framework and calls (written by the coordinating analyst, 18 Nov 2026)

This file is NOT research. It is the framework and the dated calls the desk derived from the six research notes in
this folder. The report must present these exactly (same thresholds, probabilities and dates) and use the research
notes to explain and support them. The full framework text is in `/home/user/GT-Analyst/.claude/skills/ai-trade/SKILL.md`.

## The framework in one paragraph
The AI trade is five layers with different predictability. (1) Prints: reported revenue and next-quarter guides
against the company's own guidance: highly predictable. (2) Capex plans: buyers' forward spending guidance:
predictable one guidance cycle ahead. (3) Financing: debt, leases, guarantees, vendor finance, ratings, the IPO
window: the leading layer and the first point of failure. (4) Constraints and policy: power is measurable, government
decisions are not forecastable with confidence. (5) Price: direction is a no-call. Master rule: never infer price from
a print (Nvidia rose the day after earnings only 55% of the time since 2016; on 17 Nov 2026 it beat by $6.7bn and the
last after-hours trade was +0.9%). History's two laws: equities peak before capex, and the depth of the capex cut
scales with external financing (debt-funded builders cut 50-80%, cash-funded hyperscalers 2%). The regime test (free
cash flow, bond issuance against forecast, off-balance-sheet pricing, the weakest borrower's access, the vendor as
guarantor) reads 5 of 5 on the debt-funded side for the marginal builder.

## Key calls (probability, resolve date, what flips it)
| Call | Probability | Resolves | What flips it |
|---|---|---|---|
| Broadcom guides fiscal Q1 AI semiconductor revenue above its fiscal Q4 actual (report 9 Dec) | 82% | 11 Dec 2026 | A custom-chip customer push-out, or a guide withheld over the 16 Nov export rule |
| Micron reports fiscal Q1 revenue at or above $61.5bn (its guide midpoint; report ~15 Dec) | 86% | 22 Dec 2026 | Shipments slipping into the next quarter |
| Micron guides fiscal Q2 revenue above its fiscal Q1 actual | 72% | 22 Dec 2026 | Contract prices flattening; this is the memory-cycle test |
| TrendForce shows 1Q27 conventional DRAM contract prices up on the quarter | 72% | 31 Jan 2027 | PC and phone makers cutting orders |
| TSMC reports Q4 revenue at or above $53.3bn (guide midpoint) | 90% | 22 Jan 2027 | A December shipment collapse |
| TSMC's first 2027 capex guide has a midpoint at or above $68bn | 70% | 22 Jan 2027 | TSMC holding capex flat as customers' financing tightens |
| Microsoft reports December-quarter capex above $50bn | 87% | 5 Feb 2027 | More third-party capacity or power delays |
| None of Microsoft, Alphabet, Amazon, Meta guides 2027 capex below 2026 | 88% | 12 Feb 2027 | A financing accident before late January; an ROI revolt at Meta |
| Alphabet's first 2027 capex guide has a midpoint at or above $240bn | 70% | 12 Feb 2027 | Alphabet trading capex for cash flow, or giving only qualitative guidance |
| Nvidia reports fiscal Q4 revenue at or above $130.0bn (guide midpoint) | 90% | 10 Mar 2027 | The 16 Nov licensing rule halting third-country shipments; a customer financing failure |
| CoreWeave does not miss a payment, do a distressed exchange or file for bankruptcy | 92% | 31 Mar 2027 | Nvidia withdrawing its backstops; a large customer deferral |
| Oracle is not rated below investment grade by S&P, Moody's or Fitch | 85% | 31 Mar 2027 | An OpenAI payment deferral; a failed financing |
| SMH closes below 671.83 (its 2026 high) on 30 June 2027 | 90% | 30 Jun 2027 | A V-shaped recovery on rate cuts or a capex surprise with credit repair |
| Direction of AI equities to mid-2027 | No call | 30 Jun 2027 | See the scenario tree |

Report dates marked "~" or falling in 2027 are pattern estimates; if a company has not reported by the resolve date,
the date moves to the report date.

## Scenario tree (no-call odds, SMH close on 30 June 2027; SMH was 460.10 on 17 Nov 2026)
- Repair, at or above 520: 35%. Needs 2027 capex guides to hold, the high-yield data-center bond market to reopen,
  CoreWeave CDS below 700bp.
- Range, 400 to 520: 40%. Prints hold, financing stays selective, the Fed keeps hiking.
- Second leg, below 400: 25%. Needs a financing accident (a neocloud restructuring, a junk rating for Oracle, Nvidia
  withdrawing customer support) or a hyperscaler guiding 2027 capex down.
- 2027 hyperscaler capex: another 30%+ year 40%; slowdown to under 25% growth 40%; outright decline 20%.

## Deliberate no-calls (say why in one line each)
- AI share-price direction (history: prints do not predict the reaction; valuation explains little of one-year returns).
- The Anthropic listing (ANT, first trade 19 Nov): the analyst is an Anthropic model, so no price call; it is treated
  as a gauge of financing appetite (does a deal of up to $64bn clear, and where against the $70-78 range).
- Government decisions on chip exports (the 16 Nov Commerce rule came three days before the Shenzhen summit; decisions
  of this kind are not forecastable with confidence).
- The PJM capacity auction (results ~22 Dec): the 2029/30 rules exclude new large loads from auction demand, so the
  run of three cap-clears is no longer a base rate.

## Indicator board (level, tightening trigger, loosening trigger): use the table in section 4 of the skill file.

## Corrections the report must carry
- Nvidia's "$530bn" is total commitments plus guarantees (10-Q, quarter to 26 July 2026): guarantees alone were
  $108.5bn (about $118bn at 25 Oct per press); about $164.5bn is customer credit support. Never call $530bn "guarantees".
- The "China data center curb" (Reuters, 17 Nov) is an FCC plan on Chinese data-center equipment, not a chip rule; the
  chip rule is the 16 Nov Commerce interim final rule on data centers serving China-headquartered firms.

## House style for the report (mandatory)
- Reads like a sell-side research note. Lead with the key-calls table above, then the sections that carry the calls.
- 40-60% is published as "no call".
- Do NOT mention internal machinery: no ledger, prediction IDs, "the engine", skill or section numbers, gates, red-team
  steps or conviction scores. Say "we" or "the desk".
- No calls on oil prices, energy or defense sectors, or tanker rates. Oil may appear only as context.
- Direction and mechanism only; no position sizes; state that it is analysis, not investment advice.
- State the date of each load-bearing figure, and flag figures that rest on secondary sources.
