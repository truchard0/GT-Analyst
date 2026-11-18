# Mechanism sweep on the AI trade: desk records (17 Nov 2026 PT / 18 Nov UTC)

**Status: every change below is PROPOSED.** Nothing was ledgered. `data/timelines.json`, the ledger and the existing
skills are untouched. The user decides.
- **House view swept:** `reports/20261118_ai-boom-full-report.md` (How we got here / Where we are / What we see
  ahead) and the 17 Nov house-view brief.
- **Library:** `.claude/skills/mechanism-library/SKILL.md` (v1, 35 rules). The evidence comes from distilled reading
  notes. Dates are the dates the notes give; items older than about 48h are standing context, not tape.
- **Disclosure:** Anthropic appears as a lab-revenue input and as a listing. ai-trade rule 7: no ANT view. The analyst
  is an Anthropic model.
- **Hygiene:** the AI clusters already hold about 36% of open rows, over the 35% line. So the proposals are timeline
  conditionals and shift edges, not new ledger rows.

---

## 1. Proposals, by rule

### P1. Read neocloud stress at the contract (MX-A4, R4, S2)
- **House now:** the board leads with CoreWeave five-year CDS (about 1,113bp on 17 Nov; peak 1,289bp on 5 Nov). The
  financing chain holds to 31 Mar at 80%.
- **Evidence:**
  - new secured CoreWeave debt priced at 7-7.5%, and interest fell from 25x adjusted operating income in Q1 to 2.2x in
    Q3 (Q3 report, about 11 Nov);
  - Nebius prepayments covered more than 100% of capex on its Q3 deals (6-K, 12 Nov, primary);
  - H100 rent $3.10/hr, +58% y/y (13 Nov); B300 index -7% from its September high (22 Oct, archival);
  - MOVE above 100 since Aug-Oct, but none of the repo precursors that MX-R4 requires.
- **Reading:** the CDS line prices old unsecured bonds. The asset-level lines read healthy.
- **Proposed:**
  - add four contract gauges to the ai-trade board:
    - new-loan pricing (distress above 10%);
    - prepayments as a share of capex (distress below 50%);
    - interest over adjusted operating income (healthy below 1.5x);
    - B300 and H100 rents (dark-GPU trigger: B300 over 15% below its October high and H100 below a six-year
      straight-line schedule);
  - count a new CDS high as a tightening trigger only when one contract gauge confirms it;
  - raise "financing chain holds to 31 Mar" from **80% to 82%**.
- **Falsifier:** a neocloud default or restructuring while all the contract gauges read healthy.

### P2. Nvidia after its chief executive's exit (MX-A6, A5, X3)
- **House now:** the board has guarantees ($108.5bn July 10-Q; about $118bn October, press) and notes the
  resignation. It has no execution line. Nvidia FQ4 at or above $130bn, 90%.
- **Evidence:** resignation 12-13 Nov; the interim CEO counts "customers' access to capital" in guidance (call,
  17 Nov, live); one reading (13 Nov) expects less sponsorship of neoclouds and big buyers trialling other
  accelerators; listed execution risks are a slower next-generation ramp, losing first claim on supplier capacity and
  discovery in the 1-10 Dec hearings.
- **Proposed:**
  - new node: "guarantee and credit-support lines flat or lower in the FY27 10-K (late Feb to early Mar 2027)" at
    **35%**;
  - shift edges if it resolves yes: financing-accident branch **+0.05**, 2027 capex 30%+ branch **-0.03**;
  - leave the FQ4 revenue call at 90%. It is an L1 call against the company's own guide, and MX-X3 says the policy
    hit lands on middlemen.
  - Watch: further senior departures; next-platform timing against the stated window; custom-accelerator wins.

### P3. Data-centre permission as a supply shock (MX-S3, S2, R1)
- **House now:** context only (PJM cleared at its cap, 6.8 GW short; Texas froze a 474 GW queue; New York
  moratorium; 2027 slip estimates 2.3-15 GW).
- **Evidence:** 46 of 47 local measures on 3 Nov favoured restriction; moratoria pending in about 14 states; the Texas
  governor-elect (sworn in 19 Jan) keeps the freeze; Nebius's third-party capacity slipped into 2027 (12 Nov); an
  early-November AI sell-off was put down to permitting while the 10y10y held (7 Nov). A year's delay with idle GPUs
  costs over 10 IRR points; 50% dearer power about 0.7.
- **Proposed:**
  - new measured-state node: "at least 2 of Virginia, Texas, Georgia and Ohio restrict or reprice large data-centre
    approvals by 31 Jul 2027" at **75%** (first check whether the Texas freeze counts as formal);
  - in the 2027 capex fork, move **3 points from 30%+ growth (40 to 37) to the slowdown (40 to 43)**, labelled timing,
    not demand, with a shift edge from the new node;
  - note the offset: scarce powered capacity supports GPU rents, which feed P1.

### P4. Bottleneck parts are immune to digestion, for two quarters (MX-S1, M1)
- **House now:** a 2027 decline (20%) is read as hitting every accelerator print. Micron leans below its number
  because DRAM price gains are slowing.
- **Evidence:** a large memory maker is sold out through 2029 (27 Oct); Micron says its contracts have no exit clauses
  (7 Nov); capacitor lead times are about 40 weeks; the leading foundry sees no slowdown, with power and substrates the
  bottlenecks (11 Nov).
- **Proposed:** in the decline branch, hold the revenue-call odds of contract-backed memory, optics and substrate
  suppliers **within 5 points of the base case for the first two quarters** after a capex cut. Keep Micron's
  lean-below: the rule protects volume, not price gains.
- **Falsifier:** a long-term agreement is renegotiated, or a contract price cut, within two quarters of a hyperscaler
  capex cut.

### P5. Iran secondary sanctions tied to the 10 Jan truce (MX-W5, X6, X1)
- **House now:** truce lapse 34%; Gulf flare-up 10-13%. The scenario products treat the lanes as independent.
- **Evidence:** the sanctions campaign threatens buyers of Iranian oil, and China takes over 80% of Iran's shipped
  barrels (Aug); no secondary sanctions on Chinese firms since Sept; China's control list keeps growing (dredger parts
  from 18 Nov; solar, tunnel-boring and drone controls in draft); the 16 Nov rule is a tightening counter-signal; the
  gallium pause lapses 27 Nov.
- **Proposed:**
  - new node: "the US designates a major Chinese refiner, terminal or bank over Iranian oil before 10 Jan" at
    **12%**;
  - shift edges: truce lapse **60%** given a designation and **31%** without one, so the total stays at 34%;
    designation **30%** given a Gulf escalation (P7);
  - tag truce rollover as correlated with Taiwan arms delay and control slack.
- **Effect:** the joint bad tail (Gulf flare-up and truce lapse together) rises from about 4% under independence to
  about 7% with P7.

### P6. Split Taiwan three ways (MX-W6)
- **House now:** PLA action 10% by 30 Jun 2027 (6% in 2026). It would move a 2027 capex decline from 20% to 55%.
- **Evidence:** the readings rank quarantine and gray-zone pressure above invasion; the deterrent is thin (about 40%
  of the underway US Navy in the Middle East, missile and interceptor stocks drawn down); purges are ambiguous; the
  Arizona ramp puts the constraint window after mid-2027. No sign of PLA preparation, so no licence to raise the total.
- **Proposed:**
  - split the 10% into **invasion 1.5%, quarantine or blockade 4.5%, limited kinetic gray-zone action 4%**;
  - attach conditional 2027-decline odds of **85%, 65% and 30%** (weighted 54%, matching the house 55%);
  - add a second-horizon node to 31 Dec 2028 at **15%**, with quarantine as the modal form, keyed to the January
    2028 election and PLA readiness in 2027.

### P7. A Gulf re-escalation window to 3 Jan (MX-W3, W1, W2, G1)
- **House now:** tanker war frozen, 85% to 30 Nov; flare-up 10-13%; strait more than half open by 31 Mar, 22%.
- **Evidence for:** a US strike on an Iranian island (2 Nov); Iranian drones hit a US base in Bahrain (15 Nov, two
  days old); a third carrier, an expeditionary unit and embassy evacuations (Oct); the lame-duck and Israeli caretaker
  periods both run to about 3 Jan; Iran's floating-storage cash is said to run low.
- **Against:** the Qatari track is open but static (4 Nov); the midterm result favours an end by purchase (6 Nov); the
  escalation case has been called imminent about ten times (MX-G1 discount).
- **Proposed:**
  - flare-up, defined as a multi-day US strike campaign or a ground operation inside Iran between 18 Nov and 3 Jan:
    **18%**, of which a ground operation **4%** (troops in theatre earn no credit; MX-W1);
  - frozen to 30 Nov: **85% to 80%**;
  - add a sibling, "ends by purchase (money for access) by 31 Mar", at **20%**, correlated with the 22% reopening
    node;
  - cap every truce-holds-60-days conditional at **35%** while the nuclear and strait issues are open (MX-W2);
  - if ledgered, the 18% decision call needs an execution signal, and force posture qualifies.
- **AI route:** only through the Fed and inputs (helium, Taiwan LNG; MX-S4). No oil call.

### P8. Lab revenue as a print (MX-A1, A2)
- **Evidence:** one lab's September run-rate was about $70bn against high-$70s expectations, and AI semis fell
  (Oct). A gross-to-net redefinition cut another lab's perceived base 25-30% (8 Oct). The December run-rate is
  estimated at $86-90bn (22 Oct).
- **Proposed:** add a dated catalyst, about mid-January, with shift edges:
  - below $80bn: chip-index repair branch **-0.05**, capex 30%+ branch **-0.03**;
  - above $90bn: the reverse.
- Shadow-test the five-day sign. Input only: no ANT view.

### P9. Capex is GDP demand (MX-R2, R1, R3)
- **Proposed:** a shift edge from the capex-decline branch (revealed by the late-January guides) to the Fed lane:
  "no net easing in H1 2027" goes from **90% to 70%** given a decline. A 25% cut to spending worth about 3% of GDP
  takes about 0.75pp off growth, roughly 0.75m jobs.
- The relief comes at the front end. The long-end premium is fiscal (MX-R1), so a 10-year rally should not be
  expected from an AI bust.
- No change to the December hike (93%). Pricing beats "should" views, which missed at least seven times in 2026
  (MX-R3).

### P10. The mega-listing drains share supply (MX-M2)
- Anthropic trades from 19 Nov; day 47 is 5 Jan. The one precedent (a 2026 mega-listing) saw QQQ -8% and semis -19%
  over 47 days. **Proposed:** shadow test only (SMH lags QQQ, 19 Nov close to 5 Jan close); weight zero, no ledger
  row, no ANT view. Track IPO and at-the-market issuance into Q1.

### P11. The 16 Nov rule: retaliation, middlemen, enforcement (MX-X1, X3, X4, X2)
- **Proposed:**
  - Chinese retaliation explicitly tied to the rule before about 15 Jan: **15%**, as a timeline conditional. The rule
    is licence-based with a 90-day wind-down, so it should draw lobbying. The 27 Nov gallium lapse is a scheduled
    clock, not retaliation.
  - The stress lands on Southeast Asian neoclouds' funding after the mid-February wind-down, not on Nvidia's guide.
  - Score enforcement by **16 May 2027**: fines, informing letters, indictments.
  - Watch the layer below: indium phosphide permits and transceivers (China makes about two-thirds).
  - If the chip-control bill clears the defence-bill conference, lower the odds that a truce roll comes with US
    control slack.

### P12. The private-credit second channel (MX-A7)
- Watch only: software price to free cash flow, high-yield spreads and private-credit flows moving together, to
  end-Feb 2027.

---

## 2. Rules checked that leave the house view unchanged
- **MX-A3, MX-M1:** confirm the five-of-five debt-funded reading and "call the prints, not the reaction". The low
  gate is not met: the 10-year is not falling and hikes are priced.
- **MX-W4, MX-X7, MX-G2:** transits are the Hormuz state variable; read agency actions around Shenzhen (19 Nov), not
  the readout; the resignation followed each institution's own procedure, so there is no plot model.
- **MX-X5, R4, R5, S4, M3, G3:** shadow watch; nothing moves.

---

## 3. The five changes that matter most for the AI trade over the next 12 months

1. **Read neocloud stress at the contract (P1).** Financing is the first failure point, and the house gauge (parent
   CDS) is the noisiest one. Financing chain **80% to 82%**; a CDS high counts only with a contract gauge confirming;
   distress triggers at new loans above 10% or prepayments below 50% of capex.
2. **Vendor finance after the founder's exit (P2).** A new node, support lines flat or lower in the FY27 10-K, at
   **35%**, with shift edges +0.05 to the financing accident and -0.03 to 30%+ capex growth. Print calls unchanged.
3. **Permission is a supply shock, and bottleneck parts are carved out (P3 + P4).** **+3 points** to the 2027 slowdown,
   labelled timing. A **75%** state node for two of four states restricting by 31 Jul 2027. Contract-backed suppliers'
   odds held within 5 points for two quarters of any capex cut.
4. **Wire the truce cliff to Iran secondary sanctions (P5).** Designation before 10 Jan at **12%**; truce lapse **60%**
   with it and **31%** without (total 34%). The joint Gulf-and-truce tail goes from about 4% to about 7%.
5. **Split Taiwan (P6).** Invasion **1.5%**, quarantine or blockade **4.5%**, kinetic gray-zone action **4%**, with
   capex-decline impacts of 85, 65 and 30%. Add a 2028 node at **15%**.

Next in line: the Gulf window (P7: flare-up **18%** to 3 Jan), lab revenue as a print (P8), and the capex-to-Fed edge
(P9: **90% to 70%**).

## 4. Dated signposts these add

| Date | Signpost | Rule | What it moves |
|---|---|---|---|
| 19 Nov to 19 Dec | Agency actions around the Shenzhen summit | X7 | Truce odds (P5) |
| 19 Nov to 5 Jan | SMH against QQQ after the Anthropic listing | M2 | Shadow test (P10) |
| 27 Nov | Gallium, germanium and antimony pause lapses | X2 | Counter-lever watch; not retaliation |
| 1-10 Dec | Nvidia hearings | A6 | Execution node (P2) |
| Mid-Dec | Texas freeze status; Micron print and contract language | S3, S1 | P3 state node; P4 carve-out |
| By 3 Jan | Multi-day US strike campaign or ground operation in Iran | W3, W1 | Flare-up 18% (P7) |
| Before 10 Jan | US designation of a Chinese refiner or bank | W5 | Truce lapse 60/31 (P5) |
| 10 Jan | US-China truce cliff | X6 | Correlated with arms and control slack |
| About 15 Jan | 60 days after the 16 Nov rule | X1 | Tied retaliation 15% (P11) |
| About mid-Jan | One lab's December run-rate ($86-90bn est.) | A1 | Capex and repair edges (P8) |
| Late Jan to early Feb | First 2027 capex guides | A2, R2 | Fork; Fed edge 90% to 70% (P9) |
| About 14 Feb | Remote-access wind-down ends | X3 | Southeast Asian neocloud funding |
| Late Feb to early Mar | Nvidia FQ4 and FY27 10-K support lines | A5, A6 | Support-line node 35% (P2) |
| End-Feb 2027 | Private-credit three-gauge test | A7 | Watch (P12) |
| 16 May 2027 | Six-month enforcement check on the 16 Nov rule | X4 | Rule strength (P11) |
| 30 Jun 2027 | Taiwan split horizon | W6 | 1.5 / 4.5 / 4 (P6) |
| 31 Jul 2027 | Two of four states restrict or reprice | S3 | 75% node (P3) |
| 31 Dec 2028 | Second Taiwan horizon | W6 | 15% node (P6) |
