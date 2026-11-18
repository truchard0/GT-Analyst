# Engine read on seven registered revenue forecasts: desk records (18 Nov 2026 UTC / 17 Nov PT)

**Scope.** The full engine was run on the seven registered revenue numbers in
`data/ai_prints_backtest/forward_20261118.json`: jiang doctrine, formal §10 plus §12, market-transmission, ai-trade,
and the contrarian red-team gate. **Nothing was ledgered.** No existing repo file was edited, and the registered numbers
are unchanged. Every "would move the number" below is a view, not a change. The machinery is allowed here. The
plain-words version for the report is `side-session-notes/.../engine_read_plain.md`.

**Session hygiene.** Read-only only: `ledger.py report` and `learn.py prior`.
- Ledger at read: 58 resolved, 95 open, mean Brier 0.2314. Murphy RES is 0.0086 (low resolution).
- `markets` calls came true 12 of 16. The trained prior for that type is 0.74 (shadow model n56-b83a1a35); for `state` it is 0.82.
- The AI clusters (`ai-prints` 6, `ai-prints-range` 19, `ai-capex` 10, `ai-financing` 2, `ai-price` 1) are about 36% of open
  rows (STATE §7m), over the 35% line. That is one more reason this pass adds no rows.
- **Disclosure:** Anthropic appears below as a customer of Broadcom, Amazon and Nvidia, and only as a demand and
  financing input taken from public reporting. ai-trade rule 7 applies: no view on ANT.

---

## 0. Load-bearing items and their reported times

Guides are **standing state**, not tape. Each was re-checked as the latest company statement (doctrine §16.13a, premise
freshness): `prints_suppliers.csv` and `prints_buyers.csv` hold no later guide update. Tape items older than about 48h
are archival context and are not presented as live.

| Item | Reported (UTC / ET) | Age at 18 Nov 00Z | Source |
|---|---|---|---|
| Broadcom FQ4 guide "approximately $34.8bn" | 2 Sep 2026, 8-K accepted 16:26 ET | standing | [8-K Ex.99](https://www.sec.gov/Archives/edgar/data/1730168/000173016826000076/avgo-08022026x8kxex99.htm); `data/ai_prints_backtest/prints_suppliers.csv` |
| Oracle FQ2 guide +30-34% (cc and USD) on $16.058bn = 20.875-21.518 | 10 Sep 2026, 16:16 ET | standing | [8-K Ex.99](https://www.sec.gov/Archives/edgar/data/1341439/000119312526387905/orcl-ex99_1.htm); `prints_buyers.csv` |
| Micron FQ1 guide $61.5bn ± $1.5bn | 30 Sep 2026, 16:02 ET | standing | [8-K](https://www.sec.gov/Archives/edgar/data/0000723125/000072312526000018/a2026q4ex991-pressrelease.htm) |
| TSMC Q4 guide $52.3-54.3bn at NT$31.8 | 15 Oct 2026, 06:40 ET | standing | [6-K](https://www.sec.gov/Archives/edgar/data/0001046179/000104617926000726/a3q26e_withguidancexfinal.htm) |
| Meta Q4 guide $73-76bn | 21 Oct 2026, 16:03 ET | standing | [8-K Ex.99](https://www.sec.gov/Archives/edgar/data/1326801/000162828026066700/meta-09302026xexhibit991.htm) |
| Amazon Q4 guide $240-247bn | 29 Oct 2026, 16:05 ET | standing | [8-K Ex.99](https://www.sec.gov/Archives/edgar/data/1018724/000101872426000038/amzn-20260930xex991.htm) |
| Nvidia FQ4 guide $130.0bn ± 3%, 14-week quarter, no China data-center compute | 17 Nov 2026, 16:20 ET | ~4h, live | [8-K](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000088/q3fy27pr.htm); `prints_suppliers.csv` |
| Kress: guidance considers "customers' access to capital" | 17 Nov 2026 (call) | live | [CNBC 17 Nov](https://www.cnbc.com/2026/11/17/nvidia-nvda-earnings-report-q3-2027.html); `reports/20261118_ai-boom-full-report.md` |
| TSMC October revenue NT$586.89bn | 10 Nov 2026 | 7d (filing, standing) | [6-K](https://www.sec.gov/Archives/edgar/data/0001046179/000104617926000796/tsm-revenue20261110.htm) |
| TrendForce: 4Q26 DRAM contract about +20% q/q, after about +80% (2Q) and about +40% (3Q); slowdown attributed partly to "price ceilings under long-term agreements" | 20 Oct 2026 | 28d, archival but the latest read found | [TrendForce 20 Oct](https://www.trendforce.com/news/2026/10/20/news-dram-prices-seen-rising-20-qoq-in-4q26-despite-slower-gains-ai-demand) (fetched 17 Nov PT) |
| TrendForce forecast for 1Q26 contract DRAM, +55-60% q/q | 5 Jan 2026 | archival | [TrendForce 5 Jan](https://www.trendforce.com/presscenter/news/20260105-12860.html) |
| DRAM price-fixing class action survives the motion to dismiss (14 Nov); answers due 7 Dec | 16 Nov 2026 | ~1.5d | [TrendForce 16 Nov](https://www.trendforce.com/news/2026/11/16/news-u-s-judge-rejects-samsung-sk-hynix-microns-dram-price-fixing-dismissal-bid-citing-plausible-collusion/) |
| BIS interim final rule: licenses for Indonesia, Malaysia, Singapore, Thailand, Brazil; China-HQ data-center tenancy | 16 Nov 2026 | ~1.5d | [CNBC 16 Nov](https://www.cnbc.com/2026/11/16/nvidia-commerce-china-lutnick.html); [TrendForce 17 Nov](https://www.trendforce.com/news/2026/11/17/news-u-s-targets-chinas-ai-compute-loophole-tightens-chip-exports-to-malaysia-singapore-and-three-others/). My web search found only pre-rule coverage (11-12 Nov), so the repo citations carry this item. |
| Nebius 6-K: 2026 revenue to the low end because third-party capacity slips into H1 2027; prepayments cover more than 100% of capex on Q3 deals | 12 Nov 2026 | 5d, archival (primary) | [Nebius 6-K](https://www.sec.gov/Archives/edgar/data/0001513845/000110465926126008/tm2629571d1_ex99-2.htm) |
| FedWatch 95% for +25bp on 9 Dec; 10y ~5.10% (27th session above 5%); dollar at a 19-month high | 17 Nov 2026 | live | `reports/20261118_tape-note-gulf-oil-fed.md` (CNBC/CME) |
| Brent settled $93.14, 21% below its 30 Oct war high | 17 Nov 2026, 22:36 UTC | live | same tape note (context only, no oil call) |
| Shenzhen Xi-Trump(-Putin) meeting, 19 Nov; chips on the agenda, no deliverable expected | previews, mid-Nov | pre-event | `data/timelines.json` `shenzhen-trilateral`; [Outlook India preview](https://www.outlookindia.com/international/trump-xi-shenzhen-summit-nvidia-h200-ai-chips) (undated); [SCMP on the Sept summit](https://www.scmp.com/news/us/article/3368918/why-us-chip-controls-took-back-seat-xi-trump-summit) |

---

## 1. The common frame: the guide is a biased message in a repeated game

Formal §12.4 (Crawford-Sobel) and §4/§12.7 (reputation) together say what the mechanical number is. A company guide is
cheap talk from a sender whose preferred outcome, a beat, differs from the receiver's, an unbiased forecast. Reputation
and legal liability over many observed rounds discipline it into a **stable, biased bucket**. Our registered number is
guide × (1 + average beat over the last four reports), which **estimates the sender's equilibrium bias**. The estimate is
valid only while the game is stationary.

The engine's job on each print is to ask what, if anything, breaks that stationarity this quarter:
1. A change of sender. Nvidia now has an interim CEO.
2. A regime turn. In a down-cycle the bias collapses: midpoint beats fall from 96.7% to 74.1% in the 5-year backtest.
3. An exogenous price shock that sets the size of the beat rather than management's choice. This is Micron.
4. An outlier inside the four-quarter average. This is Broadcom.
5. Information released inside the quarter. TSMC publishes monthly revenue.

**Base rates** (`data/ai_prints_backtest/results_5y.json`, 117 reports, Nov 2021-Nov 2026; computed this session):

| Class | n | Actual ≥ our point | Actual ≥ guide midpoint |
|---|---|---|---|
| All | 117 | 0.48 | 0.91 |
| Up-cycle (next guide above actual) | 90 | 0.54 | 0.97 |
| Down-cycle | 27 | 0.26 | 0.74 |

All seven current guides are above the prior quarter's actual, so all seven sit in the up-cycle class:

| Company | Guide | Prior actual |
|---|---|---|
| Broadcom | 34.8 | 29.59 |
| Oracle | 21.197 | 19.345 |
| Micron | 61.5 | 54.23 |
| TSMC | 53.3 | 46.72 |
| Meta | 74.5 | 64.60 |
| Amazon | 243.5 | 201.94 |
| Nvidia | 130.0 | 115.84 |

The proposed 0.75 down-cycle cap therefore does not bind on any of them.

Beat history per company (beat = actual against guide midpoint, %):

| Company | Last 8 beats | Reports beating by at least our assumed beat |
|---|---|---|
| Broadcom | 0.39, 2.16, 0.70, 0.96, 3.53, 1.10, 0.85, 0.65 | 3/17 at ≥1.53 |
| Micron | 0.10, 1.94, 5.69, 5.75, 9.14, 27.59, 23.75, 8.46 | 2/20 at ≥17.24 |
| TSMC | 1.43, 0.51, 4.41, 2.16, 2.84, 1.99, 1.52, 3.36 | 7/20 at ≥2.43 |
| Meta | 4.05, 4.09, 7.99, 4.58, 4.16, 2.38, 2.19, 3.36 | 10/20 at ≥3.02 |
| Amazon | 1.51, 1.58, 3.84, 1.93, 1.85, 3.14, 2.09, 1.23 | 8/20 at ≥2.08 |
| Nvidia | 4.88, 2.47, 3.87, 5.57, 4.81, 4.63, 5.74, 7.26 | 9/20 at ≥5.61 |

Oracle is not in the 5-year sample. Its six reports in `prints_history_*.csv` and `prints_buyers.csv` (four rows
secondary) beat by +2.12, -0.74, -0.68, +1.38, +0.52 and +1.26%.

## 2. The board, and which of it can reach revenue this quarter (market-transmission master gate)

- **Fed hiking and the 10y above 5%.** The 17 Nov tape is a real-rate shock: TLT and gold down, the dollar up, with
  hike odds driven by core inflation and not oil (tape note A4). By branch, that is the Branch-B cross-asset map
  without the oil leg; the 2y sign is up, which is consistent (items 18-19). **For revenue it is a financing and cost
  channel.** It raises neocloud and Oracle funding costs and can move delivery timing. It does not set this quarter's
  billings. The one direct revenue channel is **FX translation**: a dollar at a 19-month high is a headwind for USD
  reporters with large non-US sales (Meta, Amazon, Oracle) against guides set at September and October rates. Its size
  is not measurable from the sources at hand, so it is direction only and not sized (checklist item 23).
- **The Gulf war.** In price terms it now behaves as GENERIC/CORRIDOR: crude down 21% from the 30 Oct high while
  strikes continue (tape note A3). No route reaches these seven prints in-quarter. Three channels can be named, none
  sized or ledgerable:
  1. Lower pump prices since the 29 Oct Amazon guide are a mild consumer tailwind.
  2. LNG costs for Taipower hit TSMC's costs, not its revenue (`constraints_policy.md` §5).
  3. Gulf sovereign AI deployments (doctrine §15.3) have no sourced evidence of delay, so they are noise under item 23.

  No oil call is made (CLAUDE.md, 18 Nov).
- **Export rules and Shenzhen.** The 16 Nov rule came three days before the summit from a reversal-prone decider, so
  it is a bargaining chip until it survives the summit (doctrine §16.14; ai-trade rule 8). Any call on it is decision
  kind and capped at 0.35-0.65, so there is no call. Its effect on revenue in the window:
  - Broadcom: none (quarter closed 1 Nov).
  - Nvidia: small. Customers in the five named countries are at most 1.3% of revenue†. The 90-day clock for existing
    data centers ends about mid-February if it runs from publication, after Nvidia's 31 Jan quarter-end. The guide
    excludes China data-center compute, so a summit thaw is an **upside-only** tail for Nvidia. China has refused H200
    purchases so far ([Outlook India](https://www.outlookindia.com/international/trump-xi-shenzhen-summit-nvidia-h200-ai-chips)).
- **The financing chain from Nvidia to the neoclouds.** Gauges: guarantees $108.5bn (July 10-Q) and about $118bn
  (October, press†); $32bn of neocloud commitments contingent on financing; CoreWeave CDS about 1,113bp. The chain now
  runs on customer prepayments (Nebius above 100% on Q3 deals; CoreWeave collected prepayments on 70% of its deals,
  [secondary](https://fourweekmba.com/ai-neoclouds-turn-to-customer-cash-as-coreweave-bonds-yield-14/)).
  For in-window revenue the channel is **timing**: third-party capacity slipping (Microsoft and Nebius) moves rack
  deliveries across quarter-ends. This touches Nvidia and Oracle. No indicator-board trigger has fired on either side
  (ai-trade §4; full report, 17 Nov readings).
- **DRAM pricing.** Contract gains are narrowing: about +80% (2Q26), about +40% (3Q26), about +20% (4Q26). TrendForce
  partly attributes the slowdown to LTA price ceilings. This is the Micron variable (§5 below).

---

## 3. BROADCOM, fiscal Q4 2026 (quarter closed 1 Nov; report 9 Dec after the close, confirmed)

**Event.** Net revenue for the quarter to 1 Nov 2026. Guide "approximately $34.8bn" (2 Sep). Registered number
**$35.33bn** (+1.53%). Date confirmed by [Broadcom IR](https://investors.broadcom.com/news-releases/news-release-details/broadcom-inc-announce-fourth-quarter-and-fiscal-year-2026).
AI semiconductor guide $21.7bn against $16.7bn in FQ3, +30% q/q
([release](https://investors.broadcom.com/node/64671/pdf)).

**Players (chessboard; allies separate).**
- **Broadcom.**
  - King: management whose franchise rests on precise guidance.
  - Queen: custom XPUs plus Ethernet networking.
  - Rooks: TSMC CoWoS allocation and VMware cash flow.
  - Pawns: non-AI semis.
- **Customers, as separate players:**
  - Google: TPU, cash-funded.
  - Anthropic: TPU capacity buyer, now equity-funded via the 19 Nov listing. Reported as on track to become Broadcom's
    largest XPU customer in 2027 ([secondary, undated](https://www.webull.com/news/15513120997254144)).
  - Meta and OpenAI. Each wants a second source against Nvidia and price concessions from Broadcom, so their interests
    diverge.
- **Suppliers:** TSMC and the HBM makers.
- **Lenders:** CDS widened 49% in the month to 6 Nov (full report). No revenue channel.
- **US and Chinese governments:** no FQ4 channel, since the quarter closed before the 16 Nov rule.
- **Fed:** none for revenue.

**Game structure.** The quarter is closed, so the remaining game is pure **disclosure**: a repeated sender-receiver
game with 17 observed rounds.
- Distributive: contracted B2B shipments under bilateral bargaining with a few XPU buyers.
- Information is complete for Broadcom and incomplete for us.
- Sequential: guide, then report.

**Preference assumptions and flip-test.** Management prefers a small, reliable beat, because precision underwrites
the credibility of its multi-year AI revenue targets. Flip: if it preferred Micron-style sandbagging, beats above 2%
would be routine. They are 3 of 17. The conclusion is revealed in the data, not assumed, so it survives the flip.

**Ladder/credibility.** The guide is credible (17 of 17 cleared). The +30% q/q AI ramp rests on customers' committed
TPU and XPU capacity orders. Our 1.53% average beat is lifted by **one outlier**, FQ4 FY25 at +3.53%. Fiscal-Q4 beats
otherwise ran 0.78, 0.34, 0.27 and 0.39%.

**Formal checklist: PASS (0.20).**
- 1-2 pass.
- 3 pass: we need no unknowable fact; the quarter is closed.
- 4 pass: genuinely repeated and observed.
- 5 pass: the guide is not read as a costly signal.
- 6-8 n/a.
- 9 pass: a beatable guide is management's best response.
- 10 pass: base rate stated.
- 11 pass: reported revenue, 9 Dec.
- 12 pass: management in the gain domain, so risk-averse guidance.
- 13 n/a.
- 16 pass: guide read as the bucket "34.8, +0-1.5%".
- 17 soft: reputation, not commitment, but 17 observed rounds support it.
- 18-22: no shock reaches a closed quarter; consensus at guide time was LSEG $35.03bn (`consensus.csv`, 2 Sep).
- 26: L1. 27: no price inference. 28: customers mostly cash-funded. 29: guide of 2 Sep. 30: no gauge fired.

**Market-transmission branch.** None. Rates and the war are cost and financing channels and cannot reach a closed
quarter.

**AI-trade.** Layer L1. Funding class of the customers: mostly cash-funded hyperscalers plus one newly equity-funded lab.

**Conviction.**

| Component | Score | Note |
|---|---|---|
| Source quality | 0.20 | primary 8-K guide (standing state) |
| Capital-committed | 0.20 | scheduled binding filing; quarter closed |
| Formal validity | 0.20 | PASS |
| Multi-lens | 0.10 | Broadcom beat history + supply chain (TSMC record October, all suppliers guided up); customer capex correlated with the second, no third credit |
| Preconditions | 0.15 | AI ramp materializing |
| **Total** | **0.85 → 0.80** | -0.05: n = 17 beat distribution, point driven by one outlier |

**Predictions (not ledgered).**

| # | Call | P | Horizon | Falsifier | Sensitivity |
|---|---|---|---|---|---|
| B1 | FQ4 revenue ≥ $35.33bn (our number) | **0.25** | 11 Dec 2026 | Reported revenue < $35.33bn resolves NO | AI line above about $22.2bn (+2.4% on the $21.7bn guide, with non-AI at the implied $13.1bn) from XPU racks pulled in before quarter-end, as in FQ4 FY25 |
| B2 | FQ4 revenue ≥ $34.8bn (guide) | **0.94** | 11 Dec 2026 | Reported revenue < $34.8bn | An XPU push-out across the 1 Nov quarter-end |

**Red-team gate (0.80).**
1. Key assumptions: (a) the beat distribution is stationary; (b) FQ4 FY25 was not a fiscal-Q4 seasonal (four of five
   Q4 beats were below 0.8%); (c) no shipment slip.
2. ACH: H1 small beat (0-1.5%), H2 repeat of a large Q4 beat, H3 miss. Diagnostic: the last three beats of
   0.65-1.10% and four of five small Q4 beats are inconsistent with H2 as the base case.
3. Premortem: "11 Dec: revenue $35.6bn; TPU racks shipped early; AI line $22.6bn." Customer pull-in was added to B1's
   sensitivity. P unchanged.
4. Cascade: filings only; vendor consensus ($35.03-35.57bn, undated pages) was not used. No discount.
5. Reference class: 17 Broadcom reports; ≥ guide 17/17; ≥ +1.53% 3/17 = 0.18. +0.07 because a larger AI share means
   lumpier quarters.
6. Independence: two lenses correlated through AI demand. No extremizing.

Verdict: **pass at 0.80**.

**ENGINE READ.**
- (a) **Skew: below our number.** Broadcom's beats are small and steady: median 0.76% over 17 reports, last three
  0.65-1.10%. The 1.53% average carries one 3.53% outlier. The quarter closed before any part of the board could act.
- (b) **P(actual ≥ $35.33bn) = 0.25. P(actual ≥ $34.8bn) = 0.94.**
- (c) If unregistered: about **$35.1bn** (guide plus the last-8 median beat of 0.91%), **-$0.2bn (-0.6%)**. That is
  still inside the registered 80% range of 34.28-36.39, so #136 holds at about 0.93.
- (d) The one thing: the **AI semiconductor line in the 9 Dec release**. At or above about $22.2bn, the total clears
  our number. The only pre-print read is Marvell's FQ3 report on **1 Dec** (custom-silicon peer; confirmed date,
  `catalyst_calendar_consensus.md`).

**Ledger IDs touching this print:** #123 (FQ1 AI guide above the FQ4 actual), #136 (range), #143 (next-guide range).
None added.

---

## 4. ORACLE, fiscal Q2 2027 (quarter ends 30 Nov; report expected 9-14 Dec, not announced)

**Event.** Total revenue. Guide +30-34% in cc and USD on $16.058bn, i.e. $20.875-21.518bn, midpoint **$21.197bn**
(10 Sep). Registered number **$21.33bn** (+0.62%). LSEG at guide time: $21.20bn (`consensus.csv`). The date is
unconfirmed. Vendors list 9, 10 or 14 Dec. Last year Oracle announced its date about a week ahead
([days.to](https://days.to/oracle-earnings); [finanzen.net on the 2025 notice](https://www.finanzen.net/nachricht/aktien/oracle-sets-the-date-for-its-second-quarter-fiscal-year-2026-earnings-announcement-15328040)).

**Players.**
- **Oracle.**
  - King: management, whose overriding objective is defending the investment-grade rating.
  - Queen: OCI as AI-capacity landlord.
  - Rooks: database cash flow and balance-sheet access.
  - Pawns: shareholders (diluted by $10bn of stock at an 11.2% discount†) and bondholders.
- **OpenAI.** About half of RPO†. Its November round was cut to about $20bn from $30bn† (full report). It is a
  counterparty, not an ally.
- **Other OCI tenants.**
- **Suppliers:** Nvidia, and the data-center developers and power providers. Third-party capacity delays were cited by
  Microsoft and Nebius on 12 Nov.
- **Lenders and agencies:**
  - S&P BBB- stable.
  - Moody's Baa2 negative.
  - Fitch BBB stable.
  - 5y CDS about 300bp.
- **US government:** no channel.
- **Fed:** funding cost.
- **FX:** the dollar, a revenue channel.

**Game structure.** Two games run at once. (1) A **bilateral hold-up game** with OpenAI: Oracle has sunk
relationship-specific capex; revenue recognition follows delivered capacity. Distributive, incomplete information,
sequential. (2) A **rating-defense game** with the agencies: Oracle must show RPO converting into revenue. The revenue
print itself is gated by **capacity online**, a supply constraint, not demand. New RPO "not expected to affect revenue
until fiscal 2028" (`catalyst_calendar_consensus.md`, FourWeekMBA citation), so FQ2 bills on existing halls.

**Preference assumptions and flip-test.** Oracle prefers visible acceleration. Its FY27 target is at least $90bn,
and acceleration defends the IG rating. Flip: if it preferred cash preservation (cut capex to defend the rating), the
effect lands in FY28 revenue, not in FQ2, because FQ2 capacity is already built or contracted. The FQ2 read survives.

**Ladder/credibility.** The guide is a growth range stated as equal in cc and USD at **10 Sep** rates. The dollar has
since risen to a 19-month high (tape note, 17 Nov), a USD-reported headwind the guide did not contain. Oracle's record
against its midpoint is mixed: 4 of 6 cleared, and **the same quarter last year missed by 0.68%**.

**Formal checklist: PASS-WITH-FLAGS (0.10).** Flags:
- Item 3: we cannot observe when capacity comes online; Oracle can.
- Item 10: the base rate rests on 6 reports, 4 of them secondary.

All other items pass. Item 9: a beatable range is Oracle's best response, but the range is narrow. Item 17: a weak
reputation record, so the estimate leans toward the discretionary, worse case. Items 26-30: L1; debt-funded; guide of
10 Sep; no gauge fired.

**Market-transmission branch.** The rates shock reaches Oracle through funding cost and the rating, not FQ2 revenue.
**FX translation is the only live revenue channel** (headwind, unsized). The Gulf war has no channel.

**AI-trade.** L1. Funding class: **debt-funded**, the most of the five buyers:
- FQ1 free cash flow about -$5bn.
- Capex/OCF about 123% (`demand_capex_state.md`).
- FY27 capex $90-95bn.

**Conviction.**

| Component | Score | Note |
|---|---|---|
| Source quality | 0.20 | primary 8-K guide |
| Capital-committed | 0.20 | scheduled binding filing |
| Formal validity | 0.10 | PASS-WITH-FLAGS |
| Multi-lens | 0.10 | Oracle beat history + industry capacity-delay evidence (Microsoft, Nebius: independent of Oracle) |
| Preconditions | 0.07 | mixed: OCI +121% and RPO $664bn against delays and OpenAI's smaller round |
| **Total** | **0.67** | |

**Predictions (not ledgered).**

| # | Call | P | Horizon | Falsifier | Sensitivity |
|---|---|---|---|---|---|
| O1 | FQ2 revenue ≥ $21.33bn | **0.40 (no-call band)** | 21 Dec 2026 | Reported < $21.33bn resolves NO | License-revenue lumpiness; the dollar reversing before 30 Nov |
| O2 | FQ2 revenue ≥ $21.197bn (guide midpoint) | **0.62** | 21 Dec 2026 | Reported < $21.197bn | Capacity slipping past 30 Nov; dollar strength |

**Red-team gate (0.67).**
1. Key assumptions: Oracle-owned capacity on plan; FX drag under about 1pt; license revenue not lumpy-down.
2. ACH: H1 clears (the last three beats were +0.52 to +1.38%); H2 misses (same quarter last year -0.68%; industry
   delays). Diagnostic: Oracle's own FQ1 beat of +1.26% is inconsistent with a generalized Oracle capacity shortfall.
   Microsoft's and Nebius's delays concern other builders and are weakly diagnostic.
3. Premortem: "Revenue $21.0bn: two halls slipped into December; the dollar cost 0.5pt." Covered by O2's sensitivity.
4. Cascade: filings, no herd input.
5. Reference class: 6 Oracle reports, midpoint cleared 4/6 = 0.67. -0.05 for an FX headwind that was absent at the
   guide.
6. Independence: two lenses, no extremizing.

Verdict: **pass at 0.67**.

**ENGINE READ.**
- (a) **Skew: below our number.**
  - Small average beat (0.62%).
  - The same quarter last year missed.
  - A guide stated in USD at 10 Sep rates, before the dollar's run to a 19-month high.
  - Industry-wide capacity-delivery slippage.
- (b) **P(actual ≥ $21.33bn) = 0.40** (no call). **P(actual ≥ $21.197bn) = 0.62.**
- (c) If unregistered: about **$21.2bn**, the guide midpoint. **-$0.13bn (-0.6%).** Still inside the registered range
  of 20.88-21.78. #137 is at about 0.83 by this read: P(≥20.88) about 0.88 less P(>21.78) about 0.05.
- (d) The one thing: whether Oracle discloses **capacity slipping into calendar 2027** in or before the report
  (expected **9-14 Dec**; date notice likely late Nov). The earliest dated read is the dollar's level at the
  **30 Nov** quarter-end.

**Ledger IDs:** #134 (Oracle stays investment grade; this print is its next test), #137, #144, #150. None added.

---

## 5. MICRON, fiscal Q1 2027 (quarter ends about 3 Dec; report about 15 Dec, vendor date)

**Event.** Revenue. Guide **$61.5bn ± $1.5bn** (30 Sep). Registered number **$72.10bn** (+17.24% = the average of
beats of 9.14, 27.59, 23.75 and 8.46%). The 5-year backtest: Micron's mechanical number **lost to its own guide**
(median miss 5.20% vs 3.86%).

**Players.**
- **Micron.**
  - King: management.
  - Queen: HBM plus server DRAM.
  - Rooks: LTAs. Customer supply commitments are $32bn and RPO about $150bn
    ([InvestingCube](https://www.investingcube.com/shares/micron-earnings-smash-estimates-as-ai-memory-demand-drives-record-revenue-and-strong-2027-outlook/)).
  - Pawns: PC and mobile bit allocation.
- **Samsung and SK Hynix.** Allies in supply discipline, rivals in share. Separate players.
- **Buyers.**
  - Hyperscalers and Nvidia: HBM, with "the vast majority" of CY2027 HBM agreed at significantly higher prices
    ([prepared remarks](https://s25.q4cdn.com/621799436/files/doc_financials/2026/q4/Q4-FY26-Prepared-Remarks.pdf)).
  - PC and phone OEMs: resisting, "tense negotiations"†.
- **Plaintiffs and court.** Class action past the motion to dismiss. Answers are due 7 Dec; the CMC is about 12 Jan.
- **Governments:** no in-quarter channel.
- **Fed:** none.

**Game structure.** A **repeated Cournot oligopoly with capacity discipline**. Cooperation is sustained by observed
capacity announcements and a long shadow of the future, which makes it valid repeated play under formal §4. Buyers hold
countervailing power through LTAs **with price ceilings** (TrendForce, 20 Oct). Suppliers are shortening contracts and
moving to post-settlement pricing
([Tom's Hardware, undated, search summary](https://www.tomshardware.com/tech-industry/samsung-and-sk-hynix-shorten-memory-contracts-as-pricing-power-shifts-back-to-suppliers)).
The class action raises the cost of *visible* coordination but runs on a court clock of years: no FQ1 effect, an
overhang for 2027-28.

Information: contract prices settle inside the quarter. The guide (30 Sep) embedded the then-expected Q4 price. The
full report (citing TrendForce) records the 4Q forecast being raised from +10-15% to about +20% during the quarter.
That raise is post-guide upside, but small.

**Preference assumptions and flip-test.** Suppliers prefer price over volume: PC DRAM output is cut in 2027 by more
than 20%† ([Sammy Fans, 30 Oct](https://www.sammyfans.com/2026/10/30/dram-nand-prices-samsung-sk-hynix-pc-dram-2027/amp/)),
and 2027 capacity is largely allocated†
([Notebookcheck, Aug](https://www.notebookcheck.net/AI-demand-could-leave-PC-makers-fighting-over-shrinking-DRAM-supply-in-2027.1362586.0.html)).
Flip: if one supplier defected to share (adding capacity), no new capacity arrives inside FQ1. The read survives.

**Ladder/credibility. The beat tracks the contract-price increment, and both are decelerating.**

| Micron quarter (approx. calendar match) | Contract DRAM q/q | Beat vs guide |
|---|---|---|
| FQ2 FY26 (Dec-Feb ≈ 1Q26) | +55-60% (TrendForce forecast, 5 Jan) | +27.59% |
| FQ3 FY26 (Mar-May ≈ 2Q26) | about +80% | +23.75% |
| FQ4 FY26 (Jun-Aug ≈ 3Q26) | about +40% | +8.46% |
| **FQ1 FY27 (Sep-Nov ≈ 4Q26)** | **about +20%**, LTA ceilings | ? |

Beat-to-price ratios run 0.48, 0.30 and 0.21, so FQ1 points to roughly **+3-6%**. Fiscal-to-calendar matching is
approximate: flagged.

**Formal checklist: PASS-WITH-FLAGS (0.10).** Flags:
- Item 10: two base rates conflict. The company's beat history (last 8: 8 of 8 ≥ guide) against the backtest (the
  mechanical number loses to the guide; down-cycle ≥ guide only 2 of 5).
- Item 3: intra-quarter prices are only partly observable to us.

Item 4 passes: an observed repeated oligopoly. Items 16-17: no guidance cheap talk is used beyond the bucket. Items
26-30: L1; no price inference (memory equities -43% from June are doctrine §13 narrative repricing, not FQ1 revenue);
guide of 30 Sep; DRAM gauge "gains narrowing", not a trigger.

**Market-transmission branch.** None to revenue. Rates and the war do not touch FQ1 billings.

**AI-trade.** L1. Customers are mostly cash-funded hyperscalers and Nvidia's supply chain.

**Conviction.**

| Component | Score | Note |
|---|---|---|
| Source quality | 0.20 | primary 8-K guide |
| Capital-committed | 0.20 | scheduled filing; LTAs |
| Formal validity | 0.10 | PASS-WITH-FLAGS |
| Multi-lens | 0.15 | three independent: Micron's guide history; TrendForce contract prices (third party); oligopoly structure and capacity allocation (Samsung, SK Hynix) |
| Preconditions | 0.15 | materializing (prices still rising) |
| **Total** | **0.80** | |

**Predictions (not ledgered).**

| # | Call | P | Horizon | Falsifier | Sensitivity |
|---|---|---|---|---|---|
| M1 | FQ1 revenue ≥ $72.10bn | **0.07** | 22 Dec 2026 | Reported < $72.10bn resolves NO | A server-DRAM spot or contract spike plus a bit mix-shift from PC to server at much higher prices |
| M2 | FQ1 revenue ≥ $61.5bn (guide) | **0.88** | 22 Dec 2026 | Reported < $61.5bn | Shipments (HBM4 qualification lots) slipping past about 3 Dec; PC OEM order cuts |

**Red-team gate (0.80).**
1. Key assumptions: 4Q contract about +20% holds; no slip past quarter-end; LTA ceilings bind.
2. ACH: H1 modest beat (2-8%), H2 large beat (≥17%), H3 miss. Diagnostic: TrendForce's "slowdown ... price ceilings
   under long-term agreements" is inconsistent with H2.
3. Premortem for M2: "Revenue $60.2bn: HBM4 lots pushed to FQ2; PCs cut." Covered. Premortem for M1: "$73bn on a
   server mix-shift." Mix-shift added to M1's sensitivity.
4. Cascade: TrendForce is independent of Micron; aggregator consensus ($56.6-63.8bn, partly pre-guide) was not used.
5. Reference class: Micron ≥ guide 16/20 (0.80); last 8 8/8; up-cycle class. Gives **0.88**. Beat ≥17.24% 2/20 = 0.10,
   both in +55-80% contract quarters. Gives **0.07**.
6. Independence: the contract-price lens is independent of the company. Modest extremizing allowed on M2 (0.88 against
   ledger #124's 0.86).

Verdict: **pass at 0.80**.

**ENGINE READ.**
- (a) **Skew: strongly below our number.** The four-quarter average is driven by two quarters when contract prices
  rose +55-80%. This quarter's increment is about +20% and capped by LTAs, and the beat has fallen with the price
  increment every quarter since.
- (b) **P(actual ≥ $72.10bn) = 0.07. P(actual ≥ $61.5bn) = 0.88.**
- (c) If unregistered: about **$64.5bn** (guide +4.9%), **-$7.6bn (-10.5%)**. Still inside the very wide registered
  range of 56.34-87.86, so #138 holds at about 0.9. This is the one print where the engine would materially move the
  number, consistent with the backtest finding that the mechanical rule loses to the guide on Micron.
- (d) The one thing: TrendForce's next contract-price read (**late Nov to early Dec**; pattern estimate). A
  re-acceleration above the +20% 4Q pace would lift the read toward $67bn+. The decisive item is the release
  (**about 15 Dec**).

**Ledger IDs:** #124 (≥$61.5bn, 0.86), #125, #126, #138, #145. None added.

---

## 6. TSMC, Q4 2026 (quarter ends 31 Dec; report 14 or 21 Jan 2027, unconfirmed)

**Event.** USD net revenue. Guide **$52.3-54.3bn**, midpoint $53.3bn, at NT$31.8 (15 Oct). Registered number
**$54.59bn** (+2.43%). October revenue NT$586.89bn is 34.6% of the midpoint, against 37.1% (2024) and 36.6% (2025),
years in which Nov-Dec ran 8-12% below October (`reports/20261118_redteam-tsmc-smh.md`). The NT$ traded at 32.8-33.0 in
early November ([Focus Taiwan, 11 Nov](https://focustaiwan.tw/business/202611110004), via the red-team).

**Players.**
- **TSMC.**
  - King: management with a conservative-guidance reputation (6 of 6 recent beats).
  - Queen: the leading-edge monopoly.
  - Rooks: CoWoS and the N2 ramp.
  - Pawns: mature nodes.
- **Customers, separate:** Nvidia, Broadcom and AMD (continuous AI ramp); Apple (seasonal phone peak).
- **Taiwan state and Taipower:** LNG cost via Hormuz. A cost item.
- **US government:** a Section 301 step-up on Chinese semis in June 2027; Arizona. Not in-window.
- **China and the PLA:** largest exercise since 2025†; a Polymarket 9% invasion contract to end-2027†. A tail, not
  sized.
- **FX:** NT$.

**Game structure.** A repeated disclosure game with **monthly partial disclosure**. Monthly revenue is a precise public
signal (formal §12.2-12.3: the market over-weights it). The contested inference (item 3) is what October's lower share
means:
- **Red-team reading:** October is behind the usual Q4 shape. Repeating the 2024 or 2025 shape gives $50.5bn or
  $51.8bn.
- **Information-structure reading:** TSMC set the guide on 15 Oct *with about half of October in hand*. A guide is not
  a seasonal extrapolation, so a lower October share means management planned a flatter Nov-Dec than in prior years.

Both readings put the expected outcome **near the midpoint, not 2.4% above it**. Holding October flat at NT$32.8
roughly reaches the midpoint: the red-team's hurdle is NT$581bn a month. Our number needs Nov-Dec *above* October at
the weaker NT$ (about NT$600bn a month: (54.59 × 32.8 - 586.89) / 2, desk arithmetic).

**Preference assumptions and flip-test.** TSMC prefers to beat and to protect pricing. Flip: if TSMC managed to the
midpoint rather than sandbagging, the +2.43% point is too high. The read is unchanged in direction.

**Ladder/credibility.** The guide is credible: ≥ guide 18 of 20 in the 5-year sample, last 8 8 of 8. Monthly filings
make the outcome partly observable before the report.

**Formal checklist: PASS-WITH-FLAGS (0.10).** Flags:
- Item 3: contested information inference.
- Item 15: a precise public monthly signal with a publicity multiplier. The read must not over-weight one month.

Other items pass. Items 26-30: L1; customers cash-funded; guide of 15 Oct; no gauge fired.

**Market-transmission branch.** FX only: a weaker NT$ is roughly neutral to USD revenue (sales are largely USD) but
raises the NT$ hurdle. Hormuz LNG is a cost. The Taiwan tail is unsized (item 23).

**AI-trade.** L1. Funding class of customers: cash-funded.

**Conviction.**

| Component | Score | Note |
|---|---|---|
| Source quality | 0.20 | primary 6-K guide and monthly filing |
| Capital-committed | 0.20 | scheduled filing |
| Formal validity | 0.10 | PASS-WITH-FLAGS |
| Multi-lens | 0.10 | guide history + monthly-revenue shape |
| Preconditions | 0.07 | mixed (October record but behind the usual share) |
| **Total** | **0.67** | |

**Predictions (not ledgered).**

| # | Call | P | Horizon | Falsifier | Sensitivity |
|---|---|---|---|---|---|
| T1 | Q4 revenue ≥ $54.59bn | **0.20** | 22 Jan 2027 | Reported < $54.59bn resolves NO | Nov-Dec above October (an N2 or AI back-loaded profile) |
| T2 | Q4 revenue ≥ $53.3bn (guide midpoint) | **0.65** | 22 Jan 2027 | Reported < $53.3bn | November revenue below about NT$560bn; a shipment slip into Q1 |

**Red-team gate (0.67).**
1. Key assumptions: Nov-Dec within about 5% of October; no slip; NT$ near 32.8-33.
2. ACH: H1 October peak with an 8-12% fade ($50.5-51.8bn); H2 flat profile (about $53.3-53.6bn); H3 rising ($54.6bn+).
   The 34.6% share is diagnostic against H3. Guide-set-after-seeing-October is diagnostic against H1.
3. Premortem for T2: "Nov NT$545bn, Dec NT$560bn, Q4 about $51.5bn." Covered by the November print.
4. Cascade: filings only.
5. Reference class: ≥ guide 18/20 (0.90); beat ≥2.43% 7/20 (0.35). The inside view (October share) cuts these to
   0.65 and 0.20. This agrees with the red-team's 0.65 recommendation on #127.
6. Independence: one company's own reporting. No extremizing.

Verdict: **pass at 0.67**.

**ENGINE READ.**
- (a) **Skew: below our number.** October's share of the guide is the lowest of three years. Holding October's level
  only reaches the midpoint. Our number needs a rising quarter.
- (b) **P(actual ≥ $54.59bn) = 0.20. P(actual ≥ $53.3bn) = 0.65.**
- (c) If unregistered: about **$53.5bn**, **-$1.1bn (-2.0%)**. Implication: **#139 (range 53.59-55.60) is at risk**, at
  about 0.50 by this read (P(≥53.59) about 0.57 less P(>55.6) about 0.05) against its stated 0.80. #127 at 0.90 is too
  high on this read. The red-team's 0.65 stands.
- (d) The one thing: **November revenue, about 10 Dec**.
  - At or above NT$587bn (October's level): P(≥ $53.3bn) rises to about 0.85 and P(≥ $54.59bn) to about 0.40.
  - Below NT$560bn: P(≥ $53.3bn) falls to about 0.25.

**Ledger IDs:** #127 (0.90; red-team recommends about 0.65; the user decides), #128, #139, #146. None added.

---

## 7. META, Q4 2026 (report about 27 Jan 2027, pattern estimate)

**Event.** Total revenue. Guide **$73-76bn** (21 Oct), midpoint $74.5bn. LSEG had expected $73.73bn (`consensus.csv`).
Registered number **$76.75bn** (+3.02%).

| Growth arithmetic (repo actuals) | Value |
|---|---|
| Q3 2026 y/y (64.601 vs 51.242) | +26.1% |
| Guide midpoint, implied y/y on Q4 2025's 59.893 | +24.4% |
| Our number, implied y/y | +28.1% |
| Q4 2025 q/q step | +16.9% |
| Guide-implied q/q step this year | +15.3% |
| Our number, implied q/q step | +18.8% |

**Players.**
- **Meta.**
  - King: founder control (dual class), so no shareholder discipline.
  - Queen: the ad auction plus AI ranking.
  - Rooks: reach.
  - Pawns: Reality Labs.
- **Advertisers:** SMBs, large brands, China-based e-commerce advertisers. Separate: different exposure to consumer
  stress and trade policy.
- **Competitors:** Google, TikTok, Amazon ads.
- **Regulators:** EU, FTC.
- **Funders:** Meta priced $37.5bn of stock and preferred†; Q3 FCF -$2.12bn (`demand_capex_state.md`). A capex-side
  channel, not revenue.
- **Fed:** through advertiser demand and the dollar.

**Game structure.** An **auction**: revenue is impressions times price, and price is set by advertiser competition. AI
ranking raises advertiser ROI, and advertisers bid it back. Q3: impressions +10%, average price per ad +14% (search
summary of [MediaPost](https://www.mediapost.com/publications/article/418930/meta-q3-boosts-ai-spend-ad-biz-users.html)).
On top of the auction sits a repeated guidance game with 20 observed rounds. Distributive; incomplete information;
simultaneous bids.

**Preference assumptions and flip-test.** Management faces capex-ROI scrutiny (52% of fund managers expect a
hyperscaler capex cut†; an "ROI revolt at Meta" is a named risk on #130), so it prefers a beatable guide. Flip: if
advertisers are budget-constrained, price per ad decelerates (one report of US and Asia deceleration†, conflicting with
Q3's +14%) and the beat shrinks toward the last-8 minimum of 2.19%, about $76.1bn.

**Ladder/credibility.** The guide is credible: 18 of 20 cleared, last 8 8 of 8 by 2.19-7.99%, Q4 median beat 4.05%.
The FX headwind since 21 Oct is unsized.

**Formal checklist: PASS (0.20).** Item 17 is reputation-based, but 20 rounds are observed. Items 26-30: L1 buyer
print; funding class (debt and equity at the margin) touches capex, not revenue; guide of 21 Oct; no gauge fired.

**Market-transmission branch.** Real-rate and dollar shock. Two in-quarter channels:
1. FX translation, a headwind.
2. Advertiser demand via consumer stress, mild. Lower pump prices since late October are a small offset.

No Gulf channel is sized.

**AI-trade.** L1.

**Conviction.**

| Component | Score | Note |
|---|---|---|
| Source quality | 0.20 | primary 8-K |
| Capital-committed | 0.20 | scheduled filing |
| Formal validity | 0.20 | PASS |
| Multi-lens | 0.10 | guide-beat history + y/y trend (partly independent) |
| Preconditions | 0.15 | materializing (Q3 ad volume and price both up) |
| **Total** | **0.85 → 0.80** | -0.05: FX unsized; conflicting ad-price reports |

**Predictions (not ledgered).**

| # | Call | P | Horizon | Falsifier | Sensitivity |
|---|---|---|---|---|---|
| E1 | Q4 revenue ≥ $76.75bn | **0.52 (no-call band)** | 12 Feb 2027 | Reported < $76.75bn resolves NO | Holiday ad pricing; dollar into 31 Dec |
| E2 | Q4 revenue ≥ $74.5bn (guide midpoint) | **0.93** | 12 Feb 2027 | Reported < $74.5bn | Advertiser pullback after an equity drawdown or a 50bp hike; strong dollar |

**Red-team gate (0.80).**
1. Key assumptions: guide conservatism is stationary; FX under about 1pt; normal holiday demand.
2. ACH: H1 typical Q4 beat (about 4%, $77.5bn); H2 a smaller beat under deceleration (about 2%, $76.0bn); H3 miss.
   Diagnostic: Q3 beat by 3.36% when its guide implied about +22% y/y (actual +26.1%), which is inconsistent with H2
   as the norm. The y/y deceleration (28% to 26%) is consistent with H2.
3. Premortem for E2: "$74.2bn: advertisers cut after equities fell; FX -1.5pt." The equity-wealth and advertiser
   channel was added to E2's sensitivity.
4. Cascade: none.
5. Reference class: ≥ guide 18/20; last 8 8/8; up-cycle 0.97. Gives **0.93**. Beat ≥3.02%: 10/20 all, 6/8 last 8,
   3/5 Q4, about 0.55. -0.03 for FX. Gives **0.52**.
6. Independence: partly independent lenses. No extremizing on E1.

Verdict: **pass at 0.80** (E2).

**ENGINE READ.**
- (a) **Skew: balanced.**
  - Above our number: history. The Q4 median beat of 4.05% gives about $77.5bn, and the last 8 beat by ≥3.02% six
    times.
  - Below our number: our figure implies y/y growth *re-accelerating* to 28.1% from 26.1%, against a guide at 24.4%,
    plus a stronger dollar since 21 Oct.
- (b) **P(actual ≥ $76.75bn) = 0.52** (no call). **P(actual ≥ $74.5bn) = 0.93.**
- (c) If unregistered: **no material move** (within about ±$0.3bn). #140 (range 75.19-78.31) is at about 0.76 by this
  read: P(≥75.19) about 0.88 less P(>78.31) about 0.12.
- (d) The one thing: US Cyber Week online-sales tallies (**about 1-2 Dec**, pattern estimate) as the first holiday
  ad-demand read, then the dollar into **31 Dec**. The decisive item is the release (**about 27 Jan**).

**Ledger IDs:** #130 (capex, not revenue), #140, #147, #152. None added.

---

## 8. AMAZON, Q4 2026 (report about 4 Feb 2027, pattern estimate)

**Event.** Net sales. Guide **$240-247bn**, +12-16% y/y, midpoint $243.5bn (29 Oct). That was below LSEG's $244.51bn;
Reuters coverage tied the shortfall to consumer worries: higher gas prices and cost of living
([Reuters via FashionNetwork, 29 Oct](https://us.fashionnetwork.com/news/Amazon-projects-fourth-quarter-sales-below-estimates,1880439.html)).
Registered number **$248.56bn** (+2.08%). That is above the top of the range, which is normal: Q4 beats ran 1.51-3.95%.
Growth check: our number implies +16.5% y/y on Q4 2025's $213.386bn. Q3 2026 printed +12.1%, depressed by Prime Day
falling in Q2 (the company put the effect at nearly 400bp, `prints_buyers.csv`), so underlying growth was about 16%. Our
number holds the underlying pace; the guide midpoint (+14.1%) assumes deceleration.

**Players.**
- **Amazon.**
  - King: management.
  - Queen: logistics retail plus AWS.
  - Rooks: ads, Prime, Trainium.
  - Pawns: third-party sellers.
- **Consumers.**
- **AWS customers, separate:** Anthropic (no view on ANT); OpenAI; enterprises.
- **Suppliers:** Nvidia, power.
- **Competitors:** Walmart, Temu and Shein; Microsoft and Google in cloud.
- **US government:** tariffs.
- **Funders:** TTM FCF negative. A capex channel.
- **Fed:** consumer credit and the dollar.

**Game structure.** Retail runs as holiday **Bertrand competition**. AWS is a **capacity-constrained seller**:
capacity is short into 2027, and Amazon expects AWS growth above 40% in 2027 and 2028 (`demand_capex_state.md`). So AWS
revenue is set by capacity online, not demand. A repeated guidance game sits on top (20 rounds).

**Preference assumptions and flip-test.** Amazon sets a conservative range and builds an FX assumption into it.
Flip: if consumer stress bites retail harder than planned, AWS capacity additions partly offset. The midpoint read
survives; the read on our number is sensitive.

**Ladder/credibility.** ≥ guide 19 of 20; last-8 minimum beat +1.23%. The guide was set at 29 Oct FX (headwind since)
and at the oil war high (Brent's high was 30 Oct; it is now 21% lower). Pump-price relief during the holiday quarter is
a consumer tailwind relative to the guide date. That is context, not an oil call.

**Formal checklist: PASS (0.20).** Items 26-30: L1; debt-funded at the margin (capex side); guide of 29 Oct; no
trigger.

**Market-transmission branch.** Rates and the dollar give FX translation (headwind) and consumer credit (mild). The
war's generic-branch oil decline is a mild consumer offset. Net: offsetting, small.

**AI-trade.** L1.

**Conviction.**

| Component | Score | Note |
|---|---|---|
| Source quality | 0.20 | primary 8-K |
| Capital-committed | 0.20 | scheduled filing |
| Formal validity | 0.20 | PASS |
| Multi-lens | 0.10 | guide history + underlying-growth arithmetic |
| Preconditions | 0.15 | materializing (AWS +39% in Q3, backlog about $578bn) |
| **Total** | **0.85 → 0.80** | -0.05: FX and consumer channel unsized |

**Predictions (not ledgered).**

| # | Call | P | Horizon | Falsifier | Sensitivity |
|---|---|---|---|---|---|
| A1 | Q4 net sales ≥ $248.56bn | **0.42 (no-call band)** | 12 Feb 2027 | Reported < $248.56bn resolves NO | AWS capacity adds ahead of plan; gas-price relief |
| A2 | Q4 net sales ≥ $243.5bn (guide midpoint) | **0.95** | 12 Feb 2027 | Reported < $243.5bn | A holiday promotional war; an AWS capacity slip |

**Red-team gate (0.80).**
1. Key assumptions: small FX drag; consumer not breaking; AWS capacity on plan.
2. ACH: H1 typical beat (about 1.9%, $248.0bn); H2 bigger beat (≥2.1%); H3 miss. The last-8 minimum of 1.23% is
   inconsistent with H3.
3. Premortem for A2: "AWS slip plus a promotional war, $243bn." Promotional war added to A2's sensitivity.
4. Cascade: none.
5. Reference class: ≥ guide 19/20, last 8 8/8. Gives **0.95**. Beat ≥2.08%: 8/20 all, 3/8 last 8, 2/5 Q4, 0.40. +0.02
   for gas relief. Gives **0.42**.
6. No extremizing.

Verdict: **pass at 0.80** (A2).

**ENGINE READ.**
- (a) **Skew: slightly below our number.** The Q4 median beat of 1.85% gives about $248.0bn. The dollar has
  strengthened since the guide, and Amazon itself flagged consumer strain. Lower pump prices since the guide date
  partly offset.
- (b) **P(actual ≥ $248.56bn) = 0.42** (no call). **P(actual ≥ $243.5bn) = 0.95.**
- (c) If unregistered: about **$248.0bn**, **-$0.5bn (-0.2%)**, immaterial. #141 (range 244.18-252.93) is at about 0.86.
- (d) The one thing: Cyber Week online-sales tallies (**about 1-2 Dec**, pattern estimate). The decisive item is the
  release (**about 4 Feb**).

**Ledger IDs:** #130, #141, #148, #154. None added.

---

## 9. NVIDIA, fiscal Q4 2027 (14 weeks to 31 Jan 2027; report about 24 Feb-3 Mar, pattern estimate)

**Event.** Revenue. Guide **$130.0bn ± 3%**, a 14-week quarter excluding China data-center compute (17 Nov). LSEG had
expected $125.25bn (`consensus.csv`). Registered number **$137.29bn** (+5.61%).

| Run-rate arithmetic (repo actuals) | Value |
|---|---|
| Q3 vs Q2 | +20.4% (115.844 vs 96.221) |
| Guide, headline step | +12.2% |
| Guide, weekly-pace step | about +4% |
| Our number, headline step | +18.5% |
| Our number, weekly-pace step | about +10% (137.29/14 vs 115.844/13) |

The guide implies a sharp weekly deceleration; our number still implies one.

**Players.**
- **Nvidia.**
  - King: the board and interim CEO Kress (Huang resigned 12 Nov; the board will not rehire him).
  - Queen: the full-stack platform.
  - Rooks: supply allocation (CoWoS, HBM) and vendor finance ($108.5bn guarantees, July 10-Q; about $118bn October†;
    stakes in Nebius 8.3%† and Anthropic).
  - Pawns: the neoclouds as a demand channel.
- **Customers, separate:**
  - Four direct customers at 11-13% each; three were 36% of Q3.
  - Hyperscalers: cash-funded. Microsoft is delivery-constrained. Alphabet (TPU) and Amazon (Trainium) are also
    competitors.
  - Neoclouds: debt- and prepayment-funded; $32bn of commitments contingent on financing.
  - Frontier labs: about 15% of data-center sales.
  - Gulf sovereign buyers: no sourced war effect.
- **Suppliers:** TSMC and the HBM makers (sold out).
- **US government:**
  - Commerce: the 16 Nov rule and its 90-day clock.
  - Congress: testimony requested for 3 Dec; the Wyden-Neal H200 probe; Democratic control of both chambers from
    January (preliminary counts†).
- **China:** refuses H200 purchases; Shenzhen on 19 Nov.
- **Neocloud lenders:** Apollo's Rowan says access "is going to disappear" without Nvidia's guarantor role (CNBC,
  17 Nov).
- **Fed:** the 10y above 5% raises neocloud funding cost.

**Game structure.** Four games:
1. **Supply allocation by a capacity-constrained monopolist.** Revenue is limited by CoWoS and HBM and by customer
   readiness (power, sites).
2. **Vendor-finance commitment game.** Guarantees are a commitment device for neocloud lenders. Their withdrawal would
   be a costly, observable signal.
3. **Disclosure game with a new sender.** This is formal §12.13 (Kreps-Wilson): early rounds are the cheapest time to
   buy reputation, so an interim CEO guides beatably. The tells:
   - The guide implies only about +4% weekly growth against +20% last quarter.
   - The band was widened to ±3% from ±2%, a coarser message (Crawford-Sobel: more uncertainty, fewer distinguishable
     messages).
   - Guidance "considers customers' access to capital", a disclosed haircut.
4. **Export bargaining.** The rule is a chip before Shenzhen. Decision kind, no call. Upside-only via China (excluded
   from the guide); small downside via the five-country licences.

**Preference assumptions and flip-test.** Kress prefers no miss in the first quarter under interim leadership. Audience
and career costs are asymmetric. Flip: if interim management preferred to signal continuity by guiding aggressively,
the beat shrinks to the historical low end (about 2.5-4%). Evidence is non-diagnostic either way: the guide was $5bn
above consensus, consistent with both. The access-to-capital caveat leans conservative. Net: **balanced**.

**Ladder/credibility.**
- ≥ guide 19 of 20 in the 5-year sample. The one miss (-17.2%) came in the 2022 down-cycle.
- The last 8 beats were 2.47-7.26%, rising over the last four (4.81 → 4.63 → 5.74 → 7.26).
- The support lines in the next 10-Q (filed "in the coming weeks", per
  [Constellation](https://www.constellationr.com/insights/news/nvidia-posts-strong-q3-ups-q4-fiscal-2028-outlook-amid-huang-resignation))
  are the observable commitment.

**Formal checklist: PASS-WITH-FLAGS (0.10).** Flags:
- Item 4: the change of sender breaks the stationarity of the repeated guidance game, so the beat estimate is less
  reliable.
- Item 13: export decisions sit with a reversal-prone decider facing a new Congress.

Item 7 n/a. Item 9 passes (a conservative guide is the interim CEO's best response). Item 23: the Gulf deployment
channel is unsized, so it is noise. Items 26-30: L1; no price inference; mixed funding; guide of 17 Nov; no trigger.

**Market-transmission branch.** Real-rate shock leads to neocloud funding cost (CoreWeave CDS about 1,113bp), which can
move delivery timing. That is the only rates channel into this revenue, and it is a financing and timing channel.
Export rules are small. The Gulf war is not sized.

**AI-trade.** L1. Funding mix of customers: hyperscalers (cash, but FCF negative at several) plus neoclouds (debt and
prepayments). The marginal builder is 5 of 5 debt-funded (ai-trade §3).

**Conviction.**

| Component | Score | Note |
|---|---|---|
| Source quality | 0.20 | primary 8-K; call remarks via CNBC |
| Capital-committed | 0.20 | scheduled filing; supply contracts |
| Formal validity | 0.10 | PASS-WITH-FLAGS |
| Multi-lens | 0.15 | three: guide-beat history; run-rate arithmetic; supply chain (TSMC record October, HBM sold out) |
| Preconditions | 0.07 | mixed: demand materializing, financing strained, no trigger |
| **Total** | **0.72** | |

**Predictions (not ledgered).**

| # | Call | P | Horizon | Falsifier | Sensitivity |
|---|---|---|---|---|---|
| N1 | FQ4 revenue ≥ $137.29bn | **0.50 (no-call band)** | 10 Mar 2027 | Reported < $137.29bn resolves NO | Rubin supply ramp; size of the interim-guide haircut |
| N2 | FQ4 revenue ≥ $130.0bn (guide midpoint) | **0.90** | 10 Mar 2027 | Reported < $130.0bn | A large neocloud deferral; Rubin yield slip; flat or lower support lines in the next 10-Q |

**Red-team gate (0.72).**
1. Key assumptions: the Rubin ramp is on plan; no large customer deferral; guide bias at or above history.
2. ACH: H1 typical beat (4.8%, $136.3bn); H2 large beat (run-rate plus interim conservatism); H3 miss (financing
   failure or Rubin slip). Diagnostic: implied weekly +4% against +20% is inconsistent with H3 unless supply binds.
   The "access to capital" remark is non-diagnostic.
3. Premortem for N2: "A CoreWeave-class customer deferred racks; Rubin yields slipped; $128bn." Covered.
4. Cascade: no herd input.
5. Reference class: ≥ guide 19/20; up-cycle 0.97; -0.07 for a 14-week transition quarter and financing. Gives
   **0.90**. Beat ≥5.61%: 9/20, 2/8 last 8, about 0.40. +0.10 for the run-rate gap and interim conservatism. Gives
   **0.50**.
6. Independence: the supply lens is independent of guide history. No extremizing on a 0.50 call.

Verdict: **pass at 0.72**.

**ENGINE READ.**
- (a) **Skew: balanced.**
  - Above our number: the run-rate and the new CEO's incentive to set a beatable bar.
  - Below our number: supply-bound shipments, delivery delays at third-party sites, and $32bn of neocloud commitments
    that depend on financing.
- (b) **P(actual ≥ $137.29bn) = 0.50** (no call). **P(actual ≥ $130.0bn) = 0.90.**
- (c) If unregistered: **no move**, about $137bn. #142 (range 133.64-140.95) is at about 0.77.
- (d) The one thing: the **Q3 FY27 10-Q** (expected late Nov to early Dec; date not announced). Flat or lower
  customer-support or guarantee lines would turn the skew below our number. Rising lines would mean more vendor
  finance: supportive for Q4 deliveries, a later risk.

**Ledger IDs:** #132 (≥$130.0bn, 0.90), #133, #142, #149. None added.

---

## 10. Summary

| Company | Our number | Guide midpoint | Skew around our number | P(≥ ours) | P(≥ guide) | Engine number if unregistered (view only) | Conviction | Date that changes the read |
|---|---|---|---|---|---|---|---|---|
| Broadcom FQ4 | 35.33 | 34.8 | Below | 0.25 | 0.94 | ~35.1 (-0.6%) | 0.80 | AI line in the 9 Dec release (Marvell peer read 1 Dec) |
| Oracle FQ2 | 21.33 | 21.197 | Below | 0.40 | 0.62 | ~21.2 (-0.6%) | 0.67 | Capacity disclosure by the ~9-14 Dec report; dollar at 30 Nov |
| Micron FQ1 | 72.10 | 61.5 | Strongly below | 0.07 | 0.88 | ~64.5 (-10.5%) | 0.80 | TrendForce contract read late Nov/early Dec; report ~15 Dec |
| TSMC Q4 | 54.59 | 53.3 | Below | 0.20 | 0.65 | ~53.5 (-2.0%) | 0.67 | November revenue ~10 Dec |
| Meta Q4 | 76.75 | 74.5 | Balanced | 0.52 | 0.93 | no move | 0.80 | Cyber Week ~1-2 Dec; report ~27 Jan |
| Amazon Q4 | 248.56 | 243.5 | Slightly below | 0.42 | 0.95 | ~248.0 (-0.2%) | 0.80 | Cyber Week ~1-2 Dec; report ~4 Feb |
| Nvidia FQ4 | 137.29 | 130.0 | Balanced | 0.50 | 0.90 | no move | 0.72 | Q3 10-Q support lines (late Nov-early Dec) |

- Sum of P(≥ ours) = 2.36 of 7. The registered set is expected to land *below* our number more often than not. That
  is consistent with the backtest's up-cycle P(≥ point) of 0.54 less the specific stationarity breaks found here
  (Micron, Broadcom, TSMC).
- Sum of P(≥ guide) = 5.87 of 7. About one company is expected to miss its own midpoint, most likely Oracle or TSMC.

**Implications for open range rows** (a view; no row changed):
- #136 about 0.93.
- #137 about 0.83.
- #138 about 0.9.
- **#139 about 0.50, at risk.**
- #140 about 0.76.
- #141 about 0.86.
- #142 about 0.77.

That is an average of about 0.79 against 0.80 stated: the ranges are roughly right except TSMC's.

**Neglected-risk sweep (contrarian #9).** What do the guides assume away? The common in-window downside is **delivery
timing**: power and third-party data-center slippage (Microsoft, Nebius) moving shipments across quarter-ends. It
reaches Nvidia and Oracle directly and TSMC and Micron through customer pull. It is not priced into any of our
numbers, which are pure guide-bias estimates.

**Correlation.** All seven are one AI-demand bet plus one guide-bias bet. A demand miss would hit them together. The
macro board enters almost only through FX translation (Meta, Amazon, Oracle) and financing-driven timing (Nvidia,
Oracle).

**Gaps.**
- No post-11-Nov coverage of the BIS rule was found by web search this session (the repo's CNBC and TrendForce
  citations carry it).
- No 1Q27 DRAM contract forecast was found.
- No sized dollar move since the guide dates.
- No sourced 2026 holiday ad-spend data.
- The Shenzhen summit has not happened yet (19 Nov).
- Oracle's and Micron's report dates are unconfirmed.

## Sources

Repo:
- `data/ai_prints_backtest/forward_20261118.json`
- `data/ai_prints_backtest/results_5y.json` (beat statistics computed this session)
- `data/ai_prints_backtest/prints_suppliers.csv`, `prints_buyers.csv`, `prints_history_b.csv`, `consensus.csv`
- `reports/backtests/20261118_ai-prints-5y-backtest.md`
- `reports/backtests/20261118_news-informed-forecast.md`
- `reports/20261118_redteam-tsmc-smh.md`
- `reports/20261118_tape-note-gulf-oil-fed.md`
- `reports/20261118_ai-boom-full-report.md`
- `research_notes/AI trade forecasting framework/{catalyst_calendar_consensus,demand_capex_state,constraints_policy,financing_chain}.md`
- `data/timelines.json` (nodes `avgo-fq4`, `orcl-fq2`, `memory-prints`, `tsmc-q4`, `hyperscaler-q4-guides`, `nvda-fq4`,
  `fed-dec-hike`, `shenzhen-trilateral`, `ai-financing-chain`, `capex-*`)
- `ledger/ledger.db` (read-only)

Web, read 17 Nov 2026 PT (in addition to the filings linked in §0):
- [TrendForce DRAM 20 Oct](https://www.trendforce.com/news/2026/10/20/news-dram-prices-seen-rising-20-qoq-in-4q26-despite-slower-gains-ai-demand)
- [TrendForce 5 Jan](https://www.trendforce.com/presscenter/news/20260105-12860.html)
- [Outlook India, Shenzhen preview](https://www.outlookindia.com/international/trump-xi-shenzhen-summit-nvidia-h200-ai-chips)
- [SCMP on the Sept summit](https://www.scmp.com/news/us/article/3368918/why-us-chip-controls-took-back-seat-xi-trump-summit)
- [FourWeekMBA on the truce terms ending 10 Jan](https://fourweekmba.com/ai-nvidia-row-tests-us-china-truce-as-4-key-terms-end-jan-10/) (secondary)
- [Reuters via FashionNetwork, Amazon guide](https://us.fashionnetwork.com/news/Amazon-projects-fourth-quarter-sales-below-estimates,1880439.html)
- [MediaPost, Meta Q3](https://www.mediapost.com/publications/article/418930/meta-q3-boosts-ai-spend-ad-biz-users.html)
- [Tom's Hardware, contract terms](https://www.tomshardware.com/tech-industry/samsung-and-sk-hynix-shorten-memory-contracts-as-pricing-power-shifts-back-to-suppliers)
- [Notebookcheck, 2027 allocation](https://www.notebookcheck.net/AI-demand-could-leave-PC-makers-fighting-over-shrinking-DRAM-supply-in-2027.1362586.0.html)
- [Sammy Fans, PC DRAM cuts](https://www.sammyfans.com/2026/10/30/dram-nand-prices-samsung-sk-hynix-pc-dram-2027/amp/)
- [FourWeekMBA, neocloud prepayments](https://fourweekmba.com/ai-neoclouds-turn-to-customer-cash-as-coreweave-bonds-yield-14/)
- [Webull, Broadcom-Anthropic](https://www.webull.com/news/15513120997254144)
- [Constellation, Nvidia Q3](https://www.constellationr.com/insights/news/nvidia-posts-strong-q3-ups-q4-fiscal-2028-outlook-amid-huang-resignation)
- [days.to, Oracle date](https://days.to/oracle-earnings)
- [CNBC Apollo, 17 Nov](https://www.cnbc.com/2026/11/17/apollo-ceo-marc-rowan-on-ai-debt.html)

† = secondary source, not checked against a primary.
