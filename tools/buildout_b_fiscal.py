#!/usr/bin/env python3
"""BUILDOUT B / PART: entitlement actuarials, housing, insurance risk, sovereign credit (65 nodes).

WHY THIS PART EXISTS
--------------------
The scoreboard says the engine is a good physicist and a bad psychologist: physical and
institutional invariants 8-for-8 at Brier 0.10, scheduled prints backed by arithmetic 12-for-14,
and every one of the twelve misses turned on a named human's discretionary choice, a conjunction,
a stale premise or a levered proxy. The four lanes below are the richest untapped seam of the FIRST
kind that the tree does not yet have:

  * a trust-fund depletion year is arithmetic on cohorts that are already alive and already counted;
  * a statutory transmittal deadline, an appropriations calendar and a COLA formula are law;
  * the January 1 / April 1 / June 1 reinsurance renewal rounds are a contractual calendar;
  * EU-registered rating agencies are REQUIRED to publish next year's sovereign review dates in
    advance, which turns "when does the agency act" from a guess into a schedule.

It is also deliberately weighted into the far field, because the far field is the hole: the tree had
17 nodes in 2028, 5 in 2029 and 4 in 2030. 53 of the 65 rows below are dated 2028-01-01 or later.

WHAT IS *NOT* HERE, ON PURPOSE
  * ZERO `level` rows and ZERO `duration` rows. Those owe a real range_odds.py / cycle_odds.py run
    recorded on the node, and the 9/22 units lesson says a borrowed or assumed input inside a
    correction is the most dangerous number in the repo. Claims that wanted to be levels were
    re-expressed as stock-speed-limit invariants (the `bill-share-high` shape) or dropped.
  * Only TWO `direction` rows, both at the 0.55 cap. Both are comparison-shaped claims that could
    have been dressed up as invariants off a stock-inertia story; they are priced as the class the
    engine actually loses on, because that is what they are.

HONESTY CONSTRAINT
  Not one dated news fact is invented. `evidence` carries only statutory, calendrical, contractual
  or arithmetic facts that are true by construction - a transmittal deadline, a publication cycle,
  an indexation formula, a renewal date, an accounting identity. Where a row rests on an outside-view
  prior with no primary datapoint in the repo, `basis` says "prior only" and the node carries no
  evidence. A fabricated headline would poison the evidence base of a machine whose three worst
  misses (#19 #28 #29) were all "the premise was already dead on the tape".
"""
from buildout_b_lib import N

# ══════════════════════════════════════════════════════════════════════════════
# LANE: us-fiscal (20) — entitlement actuarials and the statutory budget calendar.
#   The tree has `medicare-round2` and `debt-ceiling-live` and nothing else here, which is absurd
#   for the single largest scheduled cash flow in the world economy. Every row below is either law,
#   a publication cycle, or arithmetic on a cohort that has already been born.
# ══════════════════════════════════════════════════════════════════════════════
N("usf-anchor", "now", "US fiscal: statutory calendars and cohort arithmetic", 1.0, "2026-10-02",
  "us-fiscal", "invariant", "structural",
  "Definitional: p=1.0 because a lane anchor is a label, not a claim about the world. What makes "
  "this lane tractable is that entitlement cost is a statutory formula applied to a population that "
  "already exists, and the budget process runs on dates written into law.",
  "Lane anchor. Every row below prices a consequence of a statute, a publication cycle or cohort "
  "arithmetic - never a view on whether Congress will act, which is the exact discretionary-choice "
  "class where this book is 0-for-5 (#26 #63 #59 #29 #72).",
  "The fiscal path is the slow-moving term-premium input behind every long-duration asset.")

N("usf-no-borrow-authority", "usf-anchor",
  "OASDI/HI trust funds still have no borrowing authority on 2030-01-01", 0.97, "2030-01-01",
  "us-fiscal", "invariant", "3+ years",
  "Statutory and arithmetic: the Social Security and Medicare trust funds can pay benefits only out "
  "of accumulated assets plus incoming receipts. There is no standing authority to borrow on the "
  "funds' behalf, so depletion is a payable-benefit arithmetic event, not a default event. Removing "
  "that constraint requires new legislation.",
  "This is the load-bearing invariant for the whole lane: it is why a depletion DATE is an "
  "arithmetic object at all. SOFT part: Congress could legislate general-fund transfers or explicit "
  "borrowing authority at any time, and has done smaller versions before (the 1983 interfund "
  "borrowing). Priced at 0.97 and not 1.0 for exactly that reason. Built against the #72 miss - a "
  "plan is not an action, and equally, a proposal to change the law is not a changed law.",
  "If this ever breaks, the entire 'entitlement cliff' trade in long rates has to be re-priced.",
  evidence=[{"fact": "The OASI, DI, HI and SMI trust funds have no borrowing authority; benefits "
                     "are payable only from trust-fund assets and incoming receipts",
             "reported": "structural"}])

N("usf-trustees-2027", "usf-anchor",
  "A Social Security / Medicare Board of Trustees report is transmitted to Congress during 2027",
  0.95, "2027-12-31", "us-fiscal", "scheduled", "5 quarters",
  "Statutory duty plus an unbroken publication record: the Social Security Act directs the Board of "
  "Trustees to report annually to Congress. Only the contents and the exact transmittal day are "
  "unknown; the existence of a report inside a calendar year is near-certain.",
  "Scheduled-print class - the 12-for-14 class. The claim is the EVENT, not the depletion year it "
  "prints, and deliberately so: the engine's hit rate on 'a dated thing happens' is nothing like its "
  "hit rate on 'the number comes in here'. SOFT part: a prolonged lapse in appropriations or a "
  "vacancy on the Board could in principle slip a report past a year-end, which is why this is 0.95 "
  "rather than 0.99.",
  "The trustees report is the single annual repricing event for the entitlement leg of the fiscal path.",
  evidence=[{"fact": "The Social Security Act directs the Board of Trustees to report annually to "
                     "Congress on the operation and projected status of the trust funds",
             "reported": "structural"}])

N("usf-trustees-apr1-2028", "usf-trustees-2027",
  "The 2028 trustees report is transmitted on or before the statutory April 1 deadline", 0.30,
  "2028-04-01", "us-fiscal", "scheduled", "6 quarters",
  "Prior only, and a deliberately pessimistic one: the statutory deadline is April 1, and the "
  "reference class of recent transmittals is dominated by releases AFTER it. The deadline is a legal "
  "duty with no enforcement mechanism attached, so compliance is a scheduling choice inside the "
  "executive branch rather than a constraint.",
  "This is the genuine negative the book needs, and it is a negative about a STATUTE - which is the "
  "point. A deadline with no penalty is not an invariant; it is an aspiration, and the tree should "
  "say so out loud. SOFT part: a single on-time transmittal would resolve this HIT and the reference "
  "class is small. Priced well below 0.50 because the whole lesson of the 9/22 repricings (#2 draft "
  "0.35 -> 0.08) is that 'the law says X' and 'X happens on time' are different rows.",
  "Nothing trades off the transmittal date; it matters because it dates the next repricing.",
  evidence=[{"fact": "The statutory deadline for the Board of Trustees' annual report is April 1",
             "reported": "structural"}])

N("usf-ss-reform-2030", "usf-anchor",
  "A comprehensive OASDI solvency package is enacted before 2030-01-01", 0.12, "2030-01-01",
  "us-fiscal", "marker", "3+ years",
  "Prior only. Reference class: one comprehensive solvency act in the last half-century (1983), and "
  "that one came with the depletion date inside months rather than years. This is a pure "
  "discretionary-choice row and is priced as such.",
  "Marker class and priced LOW on purpose. This is the row the engine would historically have "
  "written at 0.45 off a 'pressure is building' mechanism story; 11a and the #26 miss say that a "
  "legislature's choice under no immediate deadline is where the book bleeds. SOFT part: 'comprehensive' "
  "is a judgment call at resolution - a partial fix (a taxmax change alone) should resolve MISS, and "
  "the resolution source must be the enacted public law, not a committee markup (R32).",
  "A credible solvency package would be the largest single duration-supply event of the decade.")

N("usf-cola-oct-2027", "usf-anchor",
  "SSA announces the OASDI cost-of-living adjustment for 2028 in October 2027", 0.96, "2027-10-31",
  "us-fiscal", "scheduled", "4 quarters",
  "Statutory formula plus a fixed publication cycle: the COLA is defined as the change in the "
  "average CPI-W for the third calendar quarter over the same quarter of the prior year, so the "
  "number is mechanically determined once BLS publishes the September CPI, which it does in October. "
  "SSA has announced on that cycle without interruption.",
  "The cleanest scheduled row in the lane: the formula is law, the input is a published index, and "
  "the announcement month follows from the input's release month. Checkpoint because two downstream "
  "arithmetic rows resolve on the same print. SOFT part: a lapse in appropriations that delayed the "
  "September CPI release could push the announcement into November - a real tail, seen in miniature "
  "during past data-collection disruptions, which is why this is 0.96 and not 0.99.",
  "The COLA is the single largest indexed federal outlay adjustment and sets the Q1 transfer-income impulse.",
  kind="checkpoint",
  evidence=[{"fact": "The OASDI COLA is set by statutory formula as the change in average CPI-W for "
                     "the third calendar quarter over the prior year's third quarter, and the statute "
                     "floors the adjustment at zero", "reported": "structural"}],
  shifts=[{"target": "usf-cola-positive-2028", "p_to": 0.90,
           "note": "the September CPI-W print is where the sign resolves"},
          {"target": "usf-taxmax-rises-2028", "p_to": 0.90,
           "note": "SSA publishes the taxable maximum in the same October release"}])

N("usf-cola-positive-2028", "usf-cola-oct-2027",
  "The OASDI COLA announced for 2028 is greater than zero", 0.90, "2027-10-31",
  "us-fiscal", "invariant", "4 quarters",
  "Arithmetic on a statutory formula: a zero COLA requires the average CPI-W over a full third "
  "calendar quarter to be no higher than the prior year's third-quarter average. Reference class: "
  "quarter-average year-over-year declines in a consumer price index are confined to genuine "
  "deflationary episodes (2009, 2010, 2015 produced the only zero COLAs on record).",
  "Invariant rather than scheduled because the SIGN is near-arithmetic even though the magnitude is "
  "not - the formula is a year-over-year quarter average, which is the smoothest object in the CPI "
  "family and essentially cannot go negative outside a demand collapse. SOFT part: this is a claim "
  "about an unpublished index value, so it is not law; priced at 0.90 and not higher because the "
  "9/22 lesson is that an arithmetic framing does not make an unknown input known.",
  "A zero COLA would be the cleanest single confirmation of a deflationary regime break.")

N("usf-taxmax-rises-2028", "usf-cola-oct-2027",
  "The OASDI taxable maximum for 2028 is higher than the 2027 figure", 0.90, "2027-10-31",
  "us-fiscal", "invariant", "4 quarters",
  "Statutory indexation: the contribution and benefit base is indexed to the national average wage "
  "index. A flat or lower taxable maximum requires the AWI to have fallen year-over-year, which has "
  "happened once in the series' modern history (the 2009 wage year).",
  "Invariant class on an indexation formula, which is the same shape as the 8-for-8 group. SOFT "
  "part: the AWI used is lagged two years, so the input is already partly determined by wages that "
  "have already been earned - but the figure itself is not yet published, so this is not a certainty. "
  "Also note the statute does not let the base DECLINE in a no-COLA year, which truncates the "
  "downside and is part of why this sits at 0.90.",
  "The taxable maximum is the payroll-tax receipts lever; a step up is a small withholding drag on high earners.",
  evidence=[{"fact": "The OASDI contribution and benefit base (taxable maximum) is indexed by "
                     "statute to the national average wage index", "reported": "structural"}])

N("usf-addl-medicare-threshold", "usf-anchor",
  "The $200,000 Additional Medicare Tax wage threshold is still unindexed on 2029-01-01", 0.92,
  "2029-01-01", "us-fiscal", "invariant", "2+ years",
  "Statutory text plus arithmetic: the 0.9% Additional Medicare Tax applies above fixed dollar "
  "thresholds that the statute does not index to inflation or wages. Because the thresholds are "
  "frozen while nominal wages grow, an ever-rising share of the wage base crosses them every year "
  "with no action by anyone - a silent HI revenue escalator.",
  "This is the purest invariant in the lane: unindexed statutory thresholds are a mechanism that "
  "runs on its own, which is exactly the class scoring Brier 0.10. SOFT part: indexation could be "
  "legislated at any time, usually as a pay-for in an unrelated bill, and tax thresholds do get "
  "revisited; 0.92 prices that rather than the arithmetic, which is certain.",
  "Bracket-creep on an unindexed threshold is a structural tailwind to HI receipts and thus to the depletion date.",
  evidence=[{"fact": "The 0.9% Additional Medicare Tax applies to wages above fixed statutory "
                     "thresholds ($200,000 single / $250,000 joint) that are not indexed",
             "reported": "structural"}])

N("usf-fra-67", "usf-anchor",
  "The statutory full retirement age for the 1960-and-later cohort is still 67 on 2030-01-01", 0.94,
  "2030-01-01", "us-fiscal", "invariant", "3+ years",
  "Statute plus demographics: the 1983 amendments wrote a full retirement age schedule that tops out "
  "at 67 for workers born in 1960 or later, and that schedule is already fully phased in. Changing "
  "it requires legislation, and every such proposal has been structured with long phase-ins that "
  "would not bind by 2030 even if enacted.",
  "Invariant on enacted law with a demographic phase-in already complete - the single most leveraged "
  "parameter in the OASDI projection and the one least likely to move inside four years. SOFT part: "
  "a solvency package could legislate a further increase; but note that even an enacted increase "
  "would almost certainly apply to cohorts not yet near retirement, so this row could survive its own "
  "falsifying headline. That ambiguity is named here deliberately (R30: the resolution source is the "
  "FRA table in force, not the news).",
  "FRA is the biggest single swing factor in the long-run entitlement cost projection.",
  evidence=[{"fact": "The statutory full retirement age is 67 for workers born in 1960 or later",
             "reported": "structural"}])

N("usf-cbo-outlook-2028", "usf-anchor",
  "CBO publishes a Budget and Economic Outlook in the first half of 2028", 0.94, "2028-06-30",
  "us-fiscal", "scheduled", "6 quarters",
  "Statutory duty plus an unbroken publication record: the Congressional Budget Act directs CBO to "
  "submit an annual report on the budget and economic outlook to the Budget Committees, and CBO has "
  "published one every year on a January-to-spring cycle.",
  "Scheduled-print class. The EVENT is the claim; the baseline numbers are not. This is the row that "
  "dates the fiscal repricing calendar for the rest of the lane, which is most of its value - a "
  "checkpoint you can monitor cheaply (lesson 6) beats a forecast you can only score at horizon. "
  "SOFT part: the statutory February 15 date is routinely missed, so the window here is the half-year, "
  "not the deadline; a government-wide funding lapse is the main tail.",
  "The CBO baseline is the reference deficit path every Treasury-supply model is calibrated against.",
  evidence=[{"fact": "The Congressional Budget Act directs CBO to submit an annual report on the "
                     "budget and economic outlook to the House and Senate Budget Committees",
             "reported": "structural"}])

N("usf-cbo-ltbo-2028", "usf-cbo-outlook-2028",
  "CBO publishes a Long-Term Budget Outlook with a 30-year projection window during 2028", 0.88,
  "2028-12-31", "us-fiscal", "scheduled", "2+ years",
  "Publication cycle plus institutional practice: CBO has produced a long-term outlook annually, and "
  "the 30-year window is its standing convention rather than a one-off. Only the contents are unknown.",
  "Scheduled-print class, priced below the main Outlook row because the long-term report is a "
  "discretionary product of CBO's own work plan rather than the same statutory annual report, and "
  "its timing has moved around the calendar. SOFT part: the 30-year window specification - if CBO "
  "changed its convention the row resolves MISS on a technicality, which is the #59 ambiguous-wording "
  "failure mode, so the resolution source must be the published report's own stated horizon.",
  "The long-term outlook is where debt-to-GDP divergence becomes an explicit published number.")

N("usf-presbudget-feb-2028", "usf-anchor",
  "The President's FY2029 budget is transmitted on or before the statutory first-Monday-in-February date",
  0.35, "2028-02-07", "us-fiscal", "scheduled", "5 quarters",
  "Prior only. The transmittal date is set in statute (31 U.S.C. 1105(a)) but carries no enforcement, "
  "and the reference class of recent transmittals - especially in a presidential transition or "
  "election year - is dominated by releases weeks or months late.",
  "A second deliberate negative about a statutory deadline, and the pair with usf-trustees-apr1-2028 "
  "is the lane's calibration test: if both resolve HIT the book is systematically under-pricing "
  "statutory compliance and that is worth knowing. SOFT part: the exact first-Monday date in 2028 "
  "follows from the calendar, but a budget transmitted in two tranches (a 'skinny' budget first) "
  "creates a resolution ambiguity - resolve on the full appendix-bearing transmittal.",
  "The President's budget matters to markets only as the opening bid on next year's discretionary caps.",
  evidence=[{"fact": "31 U.S.C. 1105(a) requires the President to transmit the budget no later than "
                     "the first Monday in February", "reported": "structural"}])

N("usf-fy2028-cr", "usf-anchor",
  "FY2028 begins under a continuing resolution rather than with all 12 regular bills enacted", 0.85,
  "2027-10-01", "us-fiscal", "scheduled", "4 quarters",
  "Statutory calendar plus a dominant base rate: the fiscal year begins October 1 by statute and "
  "there are 12 regular annual appropriations bills. The reference class since the modern budget "
  "process began is overwhelmingly 'at least one CR', with full on-time enactment occurring a handful "
  "of times in five decades.",
  "Scheduled class because the DATE is statutory and only the state of the world on it is unknown; "
  "priced high off a base rate rather than off any view about the politics of 2027, which is the "
  "distinction the #26 miss was bought with. SOFT part: a full-year omnibus enacted in September "
  "would resolve this MISS, and the row does not distinguish a CR from a shutdown - a lapse with no "
  "CR at all should also resolve HIT on the 'not all 12 enacted' leg, and the label is written to "
  "carry that.",
  "A CR start caps discretionary outlays at prior-year rates, which is a small but real Q4 fiscal drag.",
  evidence=[{"fact": "The federal fiscal year begins October 1 and the regular appropriations process "
                     "comprises 12 annual bills", "reported": "structural"}])

N("usf-12-bills-fy2029", "usf-fy2028-cr",
  "All 12 regular appropriations bills are enacted before FY2029 begins", 0.08, "2028-10-01",
  "us-fiscal", "marker", "2 years",
  "Prior only, and the mirror image of the CR row above: the reference class of on-time full "
  "enactment is a handful of years out of roughly fifty, and FY2029 begins immediately after a "
  "presidential election year, historically the worst case for the calendar.",
  "Marker class, priced at the base rate and nothing else. This exists as the lane's hardest negative: "
  "a book stated entirely between 0.40 and 0.88 scored resolution ~0.00 on the 9/20 research pass, and "
  "you fix that by being willing to say 'almost certainly not'. SOFT part: 'enacted' means signed "
  "into law, so a bill presented but unsigned on October 1 resolves MISS; and this row is "
  "near-redundant with usf-fy2028-cr one year apart, which is a deliberate two-year read on the same "
  "mechanism rather than two insights (R34 - it is logged once per year, not twice per year).",
  "Nothing trades this directly; it is the control that tells you whether the CR row is skill or a base rate.")

N("usf-mts-monthly", "usf-anchor",
  "Treasury publishes a Monthly Treasury Statement for every month of FY2028", 0.93, "2028-09-30",
  "us-fiscal", "scheduled", "2 years",
  "Publication cycle with an institutional record: Treasury has published the MTS of receipts and "
  "outlays monthly, on roughly the eighth business day, without interruption. The series' existence "
  "is not discretionary; only the numbers are.",
  "Scheduled-print class and the cheapest monitoring instrument in the lane - twelve observations a "
  "year is what makes the net-interest and deficit rows checkable monthly instead of annually "
  "(lesson 6: check price- and print-defined rows every session, not at horizon). SOFT part: a "
  "funding lapse has delayed individual releases before, so 'every month' is a stronger claim than "
  "'the series continues'; priced at 0.93 for that, not for any doubt about the series.",
  "The MTS is the highest-frequency honest read on the deficit, ahead of any CBO estimate.",
  evidence=[{"fact": "Treasury publishes the Monthly Treasury Statement of receipts and outlays each "
                     "month", "reported": "structural"}])

N("usf-net-interest-nominal", "usf-mts-monthly",
  "FY2028 net interest outlays exceed FY2027's in nominal dollars", 0.90, "2028-10-31",
  "us-fiscal", "invariant", "2 years",
  "Rollover arithmetic on a known maturity schedule: net interest is the debt stock times its average "
  "rate. The stock grows with every deficit, and the average rate on the debt rises mechanically for "
  "as long as retiring securities carry coupons below the rate on new issuance. For FY2028 net "
  "interest to FALL, the stock would have to shrink or new issuance would have to price materially "
  "below the retiring average - both of which require a large rate rally, not a policy choice.",
  "Invariant class, and the strongest arithmetic row in the lane: it is a statement about the "
  "composition of a stock with a published maturity schedule, not a forecast of rates. SOFT part: a "
  "sharp enough rally in the front end could pull the average rate down fast because the bill share "
  "reprices within a year - that is the single channel that falsifies this, and it is the reason this "
  "is 0.90 rather than 0.96. Written against the #74 levered-proxy miss: the claim is the direct "
  "accounting quantity, not an ETF that is supposed to track it.",
  "Net interest is the fastest-growing outlay line and the mechanical link from rates to the deficit.")

N("usf-avg-rate-rises", "usf-anchor",
  "Treasury's published average interest rate on total interest-bearing debt is higher on 2028-09-30 "
  "than on 2026-09-30", 0.86, "2028-09-30", "us-fiscal", "invariant", "2 years",
  "Rollover arithmetic on a published series: Treasury publishes the average rate monthly. The "
  "average is a weighted mean over a maturity schedule that is already fixed; over two years a large "
  "block of sub-market coupons retires and is replaced at prevailing rates, which pushes the mean up "
  "unless new issuance prices below the retiring average.",
  "The same mechanism as the net-interest row stated on the cleaner object - a published rate rather "
  "than a dollar total that also moves with the stock. Logged separately and explicitly as the "
  "mechanism leg, so that if net interest rises while the average rate falls the book learns which "
  "half was doing the work. SOFT part: two years is long enough for a genuine easing cycle to turn "
  "the bill share over at lower rates; priced at 0.86 for that.",
  "The average rate on the debt is the cleanest single number for the fiscal cost of the rate regime.",
  evidence=[{"fact": "Treasury publishes the average interest rate on total interest-bearing debt "
                     "monthly", "reported": "structural"}])

N("usf-debt-held-grows", "usf-anchor",
  "Debt held by the public is higher in nominal dollars on 2029-09-30 than on 2026-09-30", 0.96,
  "2029-09-30", "us-fiscal", "invariant", "3 years",
  "Accounting arithmetic: debt held by the public falls only when the unified budget runs a surplus. "
  "The reference class is unambiguous - the last federal surplus was FY2001, and no baseline from any "
  "official scorekeeper projects one inside this window. For this row to resolve MISS, three "
  "consecutive years would have to net to a surplus.",
  "Invariant class and close to a tautology given the deficit path, which is precisely why it belongs "
  "in the book: a tree with no near-certainties earns no resolution, and the 9/20 research measured "
  "resolution ~0.00 on a book stated entirely between 0.40 and 0.88. SOFT part: none that is "
  "economic - the only real risk is a definitional change to the series or an accounting treatment "
  "shift, so resolve on Treasury's own published debt-held-by-the-public figure (R30).",
  "Nominal debt growth is the supply side of every long-end term-premium argument.")

N("usf-oasdi-cost-gap", "usf-anchor",
  "OASDI total cost exceeds total non-interest income in the FY2028 figures as reported", 0.93,
  "2029-06-30", "us-fiscal", "invariant", "3 years",
  "Demographics already determined: the cohort reaching full retirement age in 2028 was born in 1961 "
  "and is already alive, already counted and already covered. Beneficiary growth is therefore a "
  "known quantity, while covered-worker growth is bounded by the labour force. The cost-over-"
  "non-interest-income gap is a structural feature of the ratio, not a cyclical one.",
  "The single best example of why this lane was worth building: this is arithmetic on a population "
  "that exists, which is the 8-for-8 class. SOFT part: 'non-interest income' excludes trust-fund "
  "interest by construction and the row depends on that definition holding in the reported tables - "
  "a reporting-convention risk, not an economic one. A wage boom large enough to close the gap in one "
  "year is the only economic falsifier and is a tail.",
  "The non-interest gap is the rate at which the trust fund actually draws down, and so sets the depletion date.",
  evidence=[{"fact": "OASDI non-interest income comprises payroll tax contributions and taxation of "
                     "benefits; trust-fund interest is excluded from non-interest income by "
                     "definition", "reported": "structural"}])

# ══════════════════════════════════════════════════════════════════════════════
# LANE: housing (16) — a stock, a queue and a set of statutory caps.
#   Housing is the slowest-moving large asset class in the economy, which makes it the ideal lane
#   for stock-speed-limit invariants (the `bill-share-high` shape) and accounting identities. It
#   also has the richest statutory furniture: HERA's loan-limit formula, Prop 13, Save Our Homes.
# ══════════════════════════════════════════════════════════════════════════════
N("hsg-anchor", "now", "Housing: stocks, queues and statutory caps", 1.0, "2026-10-02",
  "housing", "invariant", "structural",
  "Definitional: p=1.0 because a lane anchor is a label, not a claim about the world. What makes "
  "housing tractable is that almost every quantity in it is a stock with a construction lead time "
  "or a formula written into state law, and stocks cannot jump.",
  "Lane anchor. The tree had one housing-adjacent row (pmms-above-65) for ~16% of GDP. Rows below "
  "are deliberately weighted to identities, lead times and statutory caps rather than to price "
  "direction, which is the oscillating-tape class that went 0-for-8 (doctrine 16.15).",
  "Housing is the household transmission channel; its stocks lead its prices by quarters.")

N("hsg-nrc-monthly", "hsg-anchor",
  "Census and HUD publish New Residential Construction for every month of 2028", 0.94, "2028-12-31",
  "housing", "scheduled", "2+ years",
  "Publication cycle with an institutional record: permits, starts and completions are published "
  "jointly each month by Census and HUD and the series is unbroken. The existence of the release is "
  "not discretionary.",
  "Scheduled-print class - the EVENT, not the level. This is the monitoring spine for the rest of the "
  "lane: twelve prints a year is what makes the under-construction and completions rows checkable "
  "rather than scoreable-only-at-horizon (lesson 6). SOFT part: a funding lapse has delayed "
  "individual Census releases before, so 'every month' carries real tail risk even though the series' "
  "continuation does not.",
  "Starts and permits are the earliest read on the residential construction contribution to GDP.",
  evidence=[{"fact": "Census and HUD publish New Residential Construction (permits, starts, "
                     "completions) jointly each month", "reported": "structural"}])

N("hsg-completions-identity", "hsg-nrc-monthly",
  "2028 single-family completions do not exceed end-2027 units under construction plus 2028 starts",
  0.98, "2029-01-31", "housing", "invariant", "2+ years",
  "Pure accounting arithmetic on a stock: a unit cannot be completed unless it was either already "
  "under construction at the start of the period or started inside it. The inequality is an identity "
  "of the flow accounts, not an estimate.",
  "Invariant class in its strongest form - this is the housing lane's version of a conservation law, "
  "and it is in the book precisely to be a near-certainty (the 9/20 research says a book with no "
  "near-certainties earns no resolution). SOFT part: only measurement. Census estimates each of the "
  "three series separately from a sample, with independent revisions, so the identity can be violated "
  "in the PUBLISHED numbers by sampling error even though it cannot be violated in the world. That "
  "measurement gap is the entire 0.02.",
  "No direct price; it is the arithmetic that caps how fast new supply can arrive.")

N("hsg-mf-uc-falls", "hsg-nrc-monthly",
  "Census's 5+ unit units-under-construction stock is lower at end-2028 than at end-2027", 0.55,
  "2028-12-31", "housing", "direction", "2+ years",
  "Stock arithmetic sets the speed limit but not the sign: the under-construction stock falls when "
  "completions exceed starts, and multifamily construction has a lead time measured in years, so the "
  "stock can only drift. Whether it drifts DOWN over a particular twelve months depends on the "
  "start rate, which depends on financing conditions - a market choice, not a constraint.",
  "Direction class at the 0.55 cap, and logged that way on purpose. This claim could easily have been "
  "dressed as an invariant off a 'the pipeline is draining' story, which is exactly the costume the "
  "twelve misses wore (doctrine 16.15: leg-extrapolation, 0-for-8). The constraint is real and gives "
  "the row its SHAPE; it does not give it a sign, so the price stays at the cap. SOFT part: all of "
  "it - this is the weakest row in the lane and is here as a calibration probe, not as a view.",
  "The multifamily pipeline is the supply side of the rent disinflation argument.")

N("hsg-ehs-monthly", "hsg-anchor",
  "NAR publishes Existing Home Sales for every month of 2028", 0.92, "2028-12-31",
  "housing", "scheduled", "2+ years",
  "Publication cycle with an institutional record: the series is produced monthly by a trade "
  "association from its own members' MLS data on a fixed schedule, and it has run without "
  "interruption for decades.",
  "Scheduled-print class. Deliberately priced slightly below the Census row: a private publisher's "
  "series is not immune to a methodology break or a decision to restructure the product, and the "
  "resolution source has to be NAR's own release (R30). SOFT part: NAR has rebenchmarked the series "
  "before; a rebenchmark that skipped a monthly release would resolve this MISS even though nothing "
  "about housing had changed.",
  "Existing sales, not new sales, is where the transaction-volume channel to brokerage and mortgage revenue lives.")

N("hsg-mos-identity", "hsg-ehs-monthly",
  "Published months-of-supply continues to equal inventory divided by the monthly sales pace in "
  "every 2028 release", 0.96, "2028-12-31", "housing", "invariant", "2+ years",
  "Definitional arithmetic: months of supply is not a measurement, it is a quotient of two other "
  "published numbers. The claim is that the published definition still holds, which is a statement "
  "about a publisher's convention, not about housing.",
  "Invariant class, and included for a specific reason: months-of-supply is the number most often "
  "quoted as if it were an independent signal, when it is a ratio whose denominator is the thing "
  "everyone is actually arguing about. Pinning the identity in the tree makes every downstream "
  "inventory claim auditable. SOFT part: rounding in the published figure, and the risk that NAR "
  "switches to a seasonally adjusted denominator, which would break the identity arithmetically "
  "without anyone calling it a change.",
  "Months of supply is the headline tightness metric; knowing it is a ratio stops you double-counting sales.",
  evidence=[{"fact": "Months of supply is defined as end-of-period inventory divided by the current "
                     "monthly sales pace", "reported": "structural"}])

N("hsg-lockin-gap", "hsg-anchor",
  "The outstanding first-lien mortgage weighted average coupon is still below the prevailing 30y "
  "origination rate on 2029-01-01", 0.90, "2029-01-01", "housing", "invariant", "2+ years",
  "Stock arithmetic: the weighted average coupon of the outstanding mortgage stock moves only as "
  "loans prepay and are replaced. The stock turns over at single-digit annual percentages when rates "
  "are above the stock's coupon, because the high-coupon loans are the ones that refinance - a "
  "self-reinforcing brake. Closing a gap of hundreds of basis points therefore takes most of a decade "
  "of turnover, not two years. Prior only on the current gap's size; no live feed in the repo.",
  "This is the lock-in effect stated as what it actually is - a property of a stock's amortisation "
  "schedule - rather than as a story about seller psychology. The arithmetic is the whole argument. "
  "SOFT part: the comparison is to the PREVAILING rate, so a large enough rally in origination rates "
  "closes the gap from the other side without any turnover at all. That is the real falsifier and it "
  "is a rate call, which is why this is 0.90 rather than 0.97.",
  "Lock-in is why existing-home transaction volume, not price, is the variable that stays depressed.")

N("hsg-wac-under-6", "hsg-lockin-gap",
  "The outstanding first-lien mortgage weighted average coupon stays below 6% through 2029", 0.80,
  "2029-12-31", "housing", "invariant", "3 years",
  "Stock-speed-limit arithmetic, the same shape as the tree's bill-share row: a weighted average "
  "coupon over a multi-trillion-dollar stock can only move at the pace of payoff plus new origination. "
  "The stock is dominated by loans written in the low-rate era, and turnover at single-digit annual "
  "rates cannot lift the mean several hundred basis points inside three years. Prior only on the "
  "starting level - the repo carries no live WAC feed, and that assumption is declared here rather "
  "than hidden in a tool call (the 9/22 units lesson).",
  "Priced at 0.80, visibly below the companion row, because it names a THRESHOLD rather than an "
  "inequality between two moving quantities, and a threshold claim with an assumed starting point is "
  "exactly the construction that shipped brent-band-q4 0.27 away from its own arithmetic. SOFT part: "
  "the 6% level itself; if the starting WAC is higher than assumed, the arithmetic is unchanged but "
  "the headroom is not. Deliberately NOT given a range_odds block, because an assumed spot plus an "
  "assumed vol is not evidence - it is the mistake with a tool receipt stapled to it.",
  "A rising stock WAC is the mechanical end of the refi wall and the start of normal transaction volume.")

N("hsg-cs-construction", "hsg-anchor",
  "Case-Shiller remains a three-month moving average published with roughly a two-month lag in every "
  "2028 release", 0.93, "2028-12-31", "housing", "invariant", "2+ years",
  "Published methodology: the index is constructed as a three-month moving average of repeat-sales "
  "pairs and released with an approximately two-month reporting lag. Both are features of the index "
  "definition, not of the housing market.",
  "Invariant on a publisher's construction, and it is in the tree as a defence against a specific "
  "failure mode this project has already paid for twice: the VIX-lookahead and partial-bar findings "
  "were both 'the series is not telling you about the period you think it is'. A smoothed, lagged "
  "index read as a current price is the same error in housing clothing. SOFT part: the publisher can "
  "change methodology with notice, and index families do get restructured; 0.93 prices that, not any "
  "doubt about the current construction.",
  "Anyone trading a housing print off Case-Shiller is trading a quarter-old average, not today's market.",
  evidence=[{"fact": "S&P CoreLogic Case-Shiller home price indices are constructed as three-month "
                     "moving averages and published with an approximately two-month lag",
             "reported": "structural"}])

N("hsg-fhfa-limit-nov", "hsg-anchor",
  "FHFA announces the 2028 baseline conforming loan limit in November 2027", 0.94, "2027-11-30",
  "housing", "scheduled", "4 quarters",
  "Statutory formula plus a fixed publication cycle: HERA sets the baseline conforming loan limit by "
  "a formula on FHFA's house price index, and FHFA has announced the following year's limit each "
  "November so that lenders can price January originations. The calendar is driven by the lending "
  "cycle, not by discretion.",
  "Scheduled-print class with a formula behind it, which is the 12-for-14 combination. Checkpoint "
  "because the direction of the limit resolves on the same announcement. SOFT part: the announcement "
  "month is convention plus operational necessity rather than a statutory date, so a slip into "
  "December is possible; priced at 0.94 for that.",
  "The conforming limit is the jumbo/agency boundary and moves the spread between those two mortgage markets.",
  kind="checkpoint",
  evidence=[{"fact": "HERA sets the baseline conforming loan limit by a formula on FHFA's house price "
                     "index, and provides that the limit does not fall below the prior year's level",
             "reported": "structural"}],
  shifts=[{"target": "hsg-fhfa-limit-rises", "p_to": 0.88,
           "note": "the November announcement is where the direction resolves"}])

N("hsg-fhfa-limit-rises", "hsg-fhfa-limit-nov",
  "The 2028 baseline conforming loan limit is higher than the 2027 limit", 0.88, "2027-11-30",
  "housing", "invariant", "4 quarters",
  "Statutory ratchet plus formula arithmetic: HERA indexes the limit to the FHFA house price index "
  "and provides that it does not DECLINE below the prior year's level. So the only two outcomes are "
  "'higher' and 'unchanged', and 'unchanged' requires the measured index to be flat or lower over the "
  "measurement window.",
  "Invariant because the statute truncates the distribution - the downside is legally impossible, "
  "which is a much stronger argument than any view on house prices. That asymmetry is the whole row. "
  "SOFT part: 'unchanged' is a live outcome in a flat or falling HPI year, and the FHFA index used is "
  "an expanded-data series whose window ends well before the announcement, so the input is partly "
  "already determined but not published. Priced at 0.88, not higher, because a flat year is a real "
  "branch and not a tail.",
  "A higher limit pushes loans from the jumbo market into agency execution, tightening that spread.")

N("hsg-hvs-quarterly", "hsg-anchor",
  "Census publishes Housing Vacancies and Homeownership for all four quarters of 2028", 0.90,
  "2028-12-31", "housing", "scheduled", "2+ years",
  "Publication cycle: the HVS is produced quarterly from the Current Population Survey on a fixed "
  "schedule and is the only official quarterly read on vacancy and homeownership rates.",
  "Scheduled-print class, priced below the monthly construction release because four observations a "
  "year gives a funding lapse four chances to break 'all four quarters' rather than twelve chances to "
  "break one month - the arithmetic of the claim's conjunction matters (R36: a conjunction cannot "
  "beat its weakest leg). SOFT part: survey-based series have been suspended and rebenchmarked "
  "before, and the HVS has known coverage issues that have prompted methodology reviews.",
  "Vacancy and homeownership rates are the demand-side counterpart to the supply queue in this lane.",
  evidence=[{"fact": "Census publishes the Housing Vacancies and Homeownership survey quarterly from "
                     "Current Population Survey data", "reported": "structural"}])

N("hsg-cohort-alive", "hsg-anchor",
  "Everyone who will be in the 25-34 age band in 2030 is already alive on 2026-10-02", 0.99,
  "2030-01-01", "housing", "invariant", "3+ years",
  "Definitional demographics: the 25-34 band in 2030 consists of people born between 1996 and 2005. "
  "That cohort is closed - no future birth can enter it. Household formation out of that band is "
  "therefore bounded above by a population that is already counted, and the only open variable is "
  "net migration and mortality.",
  "The purest invariant in the lane and arguably in the batch: it is a statement about a closed set. "
  "It is in the tree because household formation is routinely forecast as if it were a demand "
  "variable, when its ceiling is a demographic fact that was settled two decades ago. SOFT part: "
  "literally only migration - an immigrant aged 25-34 in 2030 was also already alive in 2026, so the "
  "claim as written survives migration too, which is why it is 0.99 and not 0.90. The 0.01 is "
  "measurement and definitional drift in the published age bands.",
  "The formation ceiling is the long-run demand constraint behind every housing-shortage argument.")

N("hsg-backlog-identity", "hsg-anchor",
  "Public homebuilder quarterly deliveries continue to be drawn from beginning backlog plus net new "
  "orders in every 2028 filing", 0.97, "2028-12-31", "housing", "invariant", "2+ years",
  "Accounting arithmetic on a reported stock: backlog is a stock, orders are the inflow and "
  "deliveries are the outflow, and the roll-forward is an identity the filings themselves present. "
  "A builder cannot deliver a home that was never ordered or specced into inventory.",
  "Invariant class. This row exists because builder backlog is the best lead indicator in the lane "
  "and is constantly mis-read: a falling backlog with rising deliveries is the SAME identity as a "
  "rising backlog with falling deliveries, and pinning the roll-forward in the tree makes the "
  "distinction scoreable. SOFT part: spec homes built without an order complicate the inflow leg, so "
  "the identity holds on the combined order-plus-spec inflow rather than on orders alone, and the "
  "label is written to carry that.",
  "Backlog-to-delivery conversion is the cleanest forward read on builder revenue and on completions.")

N("hsg-prop13-cap", "hsg-anchor",
  "California's 2% annual cap on assessed-value growth for unsold property is still in force on "
  "2029-01-01", 0.93, "2029-01-01", "housing", "invariant", "2+ years",
  "Constitutional text: Proposition 13 is in the California constitution and limits annual growth in "
  "assessed value for property that has not changed hands to 2%. Repeal or amendment requires a "
  "statewide ballot measure, and the reference class of attempts to narrow it is a record of "
  "failures and partial carve-outs.",
  "Invariant on a constitutional provision - the strongest kind of institutional constraint short of "
  "arithmetic. It matters for the lane because it means property-tax cost growth for long-held homes "
  "is CAPPED by law while insurance cost growth is not, which is the actual mechanism behind "
  "'ownership costs are rising' in the largest state. SOFT part: a split-roll or commercial carve-out "
  "measure could pass and would resolve this ambiguously; resolve on whether the 2% cap applies to "
  "owner-occupied residential property, which is the leg the housing claim rests on.",
  "Capped assessments are why California's effective property-tax burden is bimodal by tenure length.",
  evidence=[{"fact": "California's Proposition 13 limits annual growth in assessed value for property "
                     "that has not changed ownership to 2%", "reported": "structural"}])

N("hsg-mid-repeal", "hsg-anchor",
  "A statutory repeal of the mortgage interest deduction is enacted before 2030-01-01", 0.06,
  "2030-01-01", "housing", "marker", "3+ years",
  "Prior only. Reference class: the deduction has survived every major tax rewrite since 1913, "
  "including one that halved its cap rather than removing it. This is a pure legislative-choice row "
  "against a century-long record of survival.",
  "Marker class and the lane's hardest negative, priced off a record rather than a story. Logged "
  "because the engine's failure mode is the opposite one: pricing 'pressure is building on X' at 0.40 "
  "when the base rate is 0.05 (the 9/22 pass moved #2 from 0.35 to 0.08 on exactly this reasoning - "
  "zero drafts in 46 years). SOFT part: 'repeal' excludes further cap reductions, which are far more "
  "likely and would resolve MISS; the resolution source is the enacted public law, not a proposal "
  "or a committee print (R32: a plan is not an action).",
  "Repeal would be a step change in the user cost of owner-occupied housing; nothing prices it today.")

# ══════════════════════════════════════════════════════════════════════════════
# LANE: insurance-risk (15) — a contractual calendar and a set of accounting identities.
#   The tree has `reinsurance-jan1` and `insured-loss` and no structure underneath them. Reinsurance
#   is the rare market whose entire repricing schedule is written into contracts years in advance:
#   January 1 for most of the world, April 1 for Japan, June 1/July 1 for Florida.
# ══════════════════════════════════════════════════════════════════════════════
N("ins-anchor", "now", "Insurance risk: the renewal calendar and the capital stack", 1.0,
  "2026-10-02", "insurance-risk", "invariant", "structural",
  "Definitional: p=1.0 because a lane anchor is a label, not a claim about the world. What makes this "
  "lane tractable is that reinsurance reprices on contractually fixed renewal dates and reports "
  "through statutory filings with statutory deadlines - the calendar is the market.",
  "Lane anchor. Rows below are weighted to the renewal calendar, cat-bond contract mechanics and "
  "statutory accounting identities, and starved of any view on whether a given season is severe - "
  "which is a physical-tail question the book has no edge on and should not pretend to.",
  "Reinsurance pricing is the cost of capital for catastrophe risk and feeds straight into primary rates.")

N("ins-jan1-2028", "ins-anchor",
  "The January 1, 2028 treaty reinsurance renewal round completes on its contractual date", 0.96,
  "2028-01-01", "insurance-risk", "scheduled", "5 quarters",
  "Contractual calendar: the majority of global treaty reinsurance incepts on January 1, because the "
  "underlying treaties are written to that date. Completion is not a negotiation that can be "
  "postponed - cover either attaches at inception or the cedent is unprotected, so the date binds "
  "both sides.",
  "Scheduled class, and the lane's central checkpoint: January 1 is where the year's capacity and "
  "pricing are set, and several downstream rows resolve against what happens there. SOFT part: "
  "'completes' is soft at the margin - late placements and partially-filled programmes are routine, "
  "and a hard market can leave layers unplaced at inception. The row claims the ROUND happens on its "
  "date, not that every layer fills, and that distinction is where the #59 ambiguous-wording loss "
  "came from, so it is named here.",
  "January 1 renewal pricing is the single best annual read on the cost of catastrophe capital.",
  kind="checkpoint",
  evidence=[{"fact": "The majority of global treaty reinsurance incepts on January 1, with April 1 "
                     "for Japanese business and June 1 / July 1 for Florida-centric programmes",
             "reported": "structural"}],
  shifts=[{"target": "ins-catbond-q2-dir", "p_to": 0.55,
           "note": "January pricing sets the arbitrage that drives Q2 cat-bond supply"},
          {"target": "ins-reserve-dev-adverse", "p_to": 0.78,
           "note": "renewal terms reveal how reinsurers are reading their own reserve adequacy"}])

N("ins-jun1-2028", "ins-jan1-2028",
  "The June 1, 2028 Florida-centric renewal round completes on its contractual date", 0.95,
  "2028-06-01", "insurance-risk", "scheduled", "6 quarters",
  "Contractual calendar aligned to a physical constraint: Florida programmes incept June 1 because "
  "the Atlantic hurricane season begins that day. No cedent in that market can carry an unplaced "
  "layer into June, so the date is enforced by the hazard itself as well as by contract.",
  "Scheduled class. This is the most constrained renewal date in the lane because the deadline is set "
  "by meteorology rather than convention - a physical backstop behind a contractual one, which is the "
  "8-for-8 combination. SOFT part: the same 'completes' ambiguity as the January row; and in a "
  "capacity-short year Citizens absorbs what the private market will not write, which is a completion "
  "of a sort that a strict reading might score MISS.",
  "June 1 Florida pricing is the purest traded price of US hurricane risk.")

N("ins-apr1-japan-2028", "ins-jan1-2028",
  "The April 1, 2028 Japanese treaty renewal round completes on its contractual date", 0.94,
  "2028-04-01", "insurance-risk", "scheduled", "6 quarters",
  "Contractual calendar: Japanese reinsurance programmes incept April 1 to match the Japanese fiscal "
  "year, and the treaties are written to that date. The alignment is institutional and has not moved.",
  "Scheduled class and the lane's geographic diversifier - a second, independent renewal observation "
  "on a different peril set and a different capital base. Logged separately from January rather than "
  "bundled, because R36 says a conjunction cannot beat its weakest leg and 'all three rounds complete' "
  "would have been a weaker row than any of the three. SOFT part: the same 'completes' ambiguity; and "
  "April 1 Japan is a smaller market whose round is less publicly documented, so resolution depends on "
  "broker market reports rather than a primary filing.",
  "April 1 Japan is the cleanest read on whether capacity is being allocated away from US wind.")

N("ins-catbond-q2-dir", "ins-jan1-2028",
  "Catastrophe bond new issuance in Q2 2028 exceeds Q4 2027 issuance", 0.55, "2028-06-30",
  "insurance-risk", "direction", "6 quarters",
  "The calendar explains the seasonality but not the level: cat-bond issuance clusters in Q2 because "
  "the notes must be placed before the June 1 Florida inceptions, so Q2 is the structural peak "
  "quarter and Q4 the structural trough. Whether a particular Q2 beats the PRECEDING Q4 also depends "
  "on total market size, which is a capital-flow question with no constraint behind it.",
  "Direction class at the 0.55 cap. This row could have been written as an invariant off the renewal "
  "calendar and it would have looked respectable, which is precisely why it is not: the calendar "
  "constrains WHEN issuance happens, not HOW MUCH, and conflating the two is the levered-proxy error "
  "that cost #74. SOFT part: all of the magnitude. A single large Q4 cat-bond-for-casualty deal would "
  "flip it with no change in the seasonal mechanism at all.",
  "Cat-bond supply is the marginal capacity that caps how far traditional reinsurance pricing can run.")

N("ins-catbond-maturity", "ins-anchor",
  "At least one catastrophe bond scheduled to mature in 2028 redeems at par on its contractual "
  "maturity date", 0.96, "2028-12-31", "insurance-risk", "invariant", "2+ years",
  "Contract and maturity arithmetic: cat bonds are typically three-year notes, so the 2028 maturity "
  "schedule is already fixed by deals already issued. Each note redeems on its scheduled date unless "
  "a covered event triggers a principal loss or an extension provision. The claim is that at least "
  "ONE of a large scheduled cohort comes through clean.",
  "Invariant class on a contract already signed, and framed as a weakest-link claim deliberately: "
  "'at least one of many' is the inverse of the conjunction that killed #63, and it is near-certain "
  "for the same arithmetic reason that the conjunction was near-impossible. SOFT part: extension "
  "provisions, which let a sponsor hold principal past maturity while losses develop, mean a very "
  "heavy season could delay a large share of the cohort - but not all of it.",
  "Clean maturities are what recycle ILS capital back into the next renewal; a blocked cohort tightens capacity.",
  evidence=[{"fact": "Catastrophe bonds are typically issued with three-year terms and redeem at "
                     "par on a contractual maturity date absent a covered event or an extension",
             "reported": "structural"}])

N("ins-catbond-collateral", "ins-catbond-maturity",
  "Catastrophe bonds outstanding on 2029-01-01 remain fully collateralised by indenture", 0.96,
  "2029-01-01", "insurance-risk", "invariant", "2+ years",
  "Definitional and contractual: a catastrophe bond is a note issued by a special purpose insurer "
  "whose proceeds sit in a collateral trust. Full collateralisation is what the instrument IS - it is "
  "why cat bonds carry no reinsurer credit risk, and it is written into the indenture rather than "
  "being a market practice.",
  "Invariant on an instrument definition. This is in the tree because the single most common error in "
  "reasoning about ILS is treating it as reinsurance with a different wrapper: collateralisation means "
  "the capacity is trapped until losses develop, which is a completely different liquidity object "
  "from a reinsurer's balance sheet. SOFT part: hybrid and partially-collateralised structures exist "
  "at the margin, so the claim is about the cat-bond market as defined, not about every ILS vehicle; "
  "resolve on the 144A cat-bond universe.",
  "Trapped collateral is the mechanism by which one bad season removes capacity from the NEXT renewal.")

N("ins-hurricane-window", "ins-anchor",
  "The Atlantic hurricane season window remains June 1 to November 30 in NOAA's 2028 definition",
  0.95, "2028-06-01", "insurance-risk", "invariant", "6 quarters",
  "Definitional and institutional: the season dates are a published administrative convention set to "
  "bracket the climatological period of activity, and the entire reinsurance and ILS calendar is "
  "built on them. Changing them would require a deliberate redefinition.",
  "Invariant on a published definition, and load-bearing for the lane: the June 1 renewal date, the "
  "Q2 cat-bond window and the seasonality of every loss estimate all hang off these two dates. SOFT "
  "part: there is a live scientific discussion about moving the start date earlier given "
  "early-season activity, so this is not a frozen object - and an administrative change would resolve "
  "this MISS while telling you something genuinely important about the hazard. That is a feature.",
  "The season window is the clock every catastrophe-exposed book is priced against.",
  evidence=[{"fact": "NOAA defines the Atlantic hurricane season as June 1 through November 30",
             "reported": "structural"}])

N("ins-combined-ratio-identity", "ins-anchor",
  "Combined ratios in 2028 statutory filings continue to equal the loss-and-LAE ratio plus the "
  "underwriting expense ratio", 0.97, "2028-12-31", "insurance-risk", "invariant", "2+ years",
  "Definitional arithmetic on a statutory accounting convention: the combined ratio is not a measured "
  "quantity, it is the sum of two published ratios, and a value below 100 means underwriting profit "
  "by construction rather than by inference.",
  "Invariant class. In the tree because the combined ratio is the most-quoted and least-understood "
  "number in insurance: it is routinely compared across companies whose expense ratios are computed "
  "on different bases (written versus earned premium), which makes the SUM comparable only if you "
  "know the convention. Pinning the identity makes every downstream profitability row auditable. "
  "SOFT part: the written-versus-earned denominator convention differs between statutory and GAAP "
  "presentation, so the identity holds within a presentation basis, not across them.",
  "Combined ratio under 100 is the threshold at which underwriting, not investment income, is paying.",
  evidence=[{"fact": "The combined ratio is defined as the loss-and-loss-adjustment-expense ratio "
                     "plus the underwriting expense ratio", "reported": "structural"}])

N("ins-naic-mar1-2028", "ins-anchor",
  "Property-casualty insurers file 2027 NAIC annual statements, including Schedule P, by the March 1 "
  "statutory filing date", 0.93, "2028-03-01", "insurance-risk", "scheduled", "5 quarters",
  "Statutory deadline with a regulatory enforcement mechanism: the annual statement is filed with "
  "state insurance departments by March 1, and unlike a congressional deadline this one is backed by "
  "the regulator's authority over the licence. Compliance is near-universal for that reason.",
  "Scheduled class, and the best-enforced deadline in the whole batch - worth contrasting explicitly "
  "with usf-trustees-apr1-2028, which is the same kind of statutory date with no penalty attached and "
  "is priced at 0.30. The difference between those two numbers is the lane's thesis: a deadline is "
  "only an invariant when something bad happens if you miss it. SOFT part: individual extensions are "
  "granted, so 'insurers file' is an aggregate claim, not a universal one.",
  "Schedule P is the only annual window into reserve adequacy across the whole admitted market.",
  evidence=[{"fact": "NAIC annual statements, including Schedule P's loss development exhibits, are "
                     "filed with state insurance regulators by March 1", "reported": "structural"}])

N("ins-schedulep-triangle", "ins-naic-mar1-2028",
  "Schedule P in the 2028 filings still presents a ten-year loss development triangle", 0.92,
  "2028-12-31", "insurance-risk", "invariant", "2+ years",
  "Published regulatory form: Schedule P's structure, including the ten accident-year rows, is set by "
  "the NAIC annual statement instructions rather than by each filer, and the ten-year window is what "
  "makes reserve development comparable across companies and years.",
  "Invariant on a regulatory form's construction. Its value is that a ten-year triangle means adverse "
  "development is observable with a LAG measured in years, not quarters - so 'reserves are adequate' "
  "is never a statement about the present. That is the same lesson as the Case-Shiller row and the "
  "VIX-lookahead finding in a third domain. SOFT part: the NAIC revises annual statement instructions "
  "regularly, and a change to the triangle's depth is a live possibility in a long-tail-liability "
  "review cycle.",
  "The triangle's depth sets how long a reserving error can stay hidden, and so how late a casualty cycle turns.")

N("ins-citizens-glidepath", "ins-anchor",
  "Florida's statutory cap on annual Citizens Property Insurance rate increases is still in force on "
  "2029-01-01", 0.85, "2029-01-01", "insurance-risk", "invariant", "2+ years",
  "Statutory text: Florida law caps the annual rate increase Citizens may take, which is what makes a "
  "state insurer of last resort structurally under-priced relative to the private market and "
  "therefore structurally growing in a hard market. The cap is a statute, so removing or raising it "
  "requires legislation.",
  "Invariant on enacted law, priced at 0.85 rather than higher because this particular statute has "
  "been AMENDED repeatedly as part of Florida's market reforms - the cap's existence is durable, its "
  "level is not. SOFT part: exactly that. If the legislature raises the cap the row's letter survives "
  "while its economic meaning is gutted, which is a resolution trap; resolve on whether a statutory "
  "annual limit exists, and log any level change as a revision rather than a resolution (R31).",
  "A capped last-resort rate is a subsidy that pulls risk onto the state's balance sheet every hard market.",
  evidence=[{"fact": "Florida statute limits the annual rate increase Citizens Property Insurance "
                     "Corporation may implement", "reported": "structural"}])

N("ins-fairplan-assessment", "ins-anchor",
  "The California FAIR Plan levies a member-insurer assessment at any point before 2030-01-01", 0.40,
  "2030-01-01", "insurance-risk", "marker", "3+ years",
  "Prior only, and contingent on a physical tail: the FAIR Plan is a statutorily mandated syndicated "
  "pool whose members are the admitted insurers, and its funding stack reaches member assessments "
  "only after reinsurance and surplus are exhausted. So the trigger is a wildfire loss large enough "
  "to break through a capital stack, which is a hazard event, not a decision.",
  "Marker class, priced below 0.50 because the row needs a conjunction - a large enough event AND a "
  "capital stack that does not absorb it - and R36 says a conjunction cannot beat its weakest leg. "
  "The engine's instinct here would be 0.65 off a 'fire risk is rising' story; that is the "
  "leg-extrapolation shape that went 0-for-8. SOFT part: the assessment mechanism has been "
  "restructured and the definition of a qualifying assessment has changed, so resolution must name "
  "the instrument - a member assessment, not a surcharge passed to policyholders.",
  "A FAIR Plan assessment is the moment California wildfire risk stops being an insurer problem and becomes a market one.")

N("ins-withdrawal-notice", "ins-anchor",
  "Statutory non-renewal notice and withdrawal-plan filing requirements still apply to admitted "
  "homeowners insurers in a majority of states on 2029-01-01", 0.93, "2029-01-01",
  "insurance-risk", "invariant", "2+ years",
  "Statutory and institutional: state insurance codes generally require an admitted insurer to give "
  "advance non-renewal notice and, for a book-wide exit, to file a withdrawal plan with the "
  "regulator. These are licensing conditions, so an insurer cannot exit a state at the speed its "
  "underwriting model would prefer - the withdrawal is rate-limited by law.",
  "Invariant on a regulatory constraint, and the key mechanism for the lane: admitted-market "
  "withdrawal looks like a corporate decision but is executed on a statutory clock, which is why the "
  "shift from admitted to surplus lines shows up as a multi-year drift rather than an event. SOFT "
  "part: 'a majority of states' is an aggregate and the specific requirements vary widely, so this is "
  "a claim about the regulatory regime's character, not a count; resolve on whether the "
  "notice-and-plan architecture is intact, not on a tally.",
  "Rate-limited exit is why a hard property market produces years of non-renewals rather than one clean break.")

N("ins-reserve-dev-adverse", "ins-jan1-2028",
  "At least one top-ten US property-casualty writer reports adverse prior-year reserve development "
  "in a 2028 filing", 0.78, "2028-12-31", "insurance-risk", "marker", "2+ years",
  "Base rate over a wide reference class: with ten large writers, dozens of lines each and a "
  "ten-year development triangle on every one, the probability that NONE of them reports adverse "
  "development on ANY prior year in a full calendar year is small. The claim is 'at least one of "
  "many', which is the arithmetic that makes weakest-link claims cheap.",
  "Marker class rather than invariant, because the observable is a reported accounting judgment and "
  "reserving is where management discretion lives - exactly the discretionary-choice class the book "
  "loses on, which is why this is 0.78 and not 0.92 despite the arithmetic looking stronger than "
  "that. SOFT part: 'adverse development' at the company level can be netted against favourable "
  "development in other lines, so resolution must read the development exhibit, not the headline; and "
  "'top ten' needs a fixed definition at logging time (direct premiums written) per R30.",
  "Adverse development is the tell that the casualty cycle has turned, and it leads pricing by quarters.")

# ══════════════════════════════════════════════════════════════════════════════
# LANE: sovereign-credit (14) — the one market whose repricing dates are published in advance.
#   This is the discovery that justifies the lane: EU-registered rating agencies are REQUIRED to
#   publish, in advance, a calendar of the dates on which they may publish sovereign actions. So
#   "when does the agency move" is a schedule, not a guess - and the engine is 12-for-14 on schedules.
# ══════════════════════════════════════════════════════════════════════════════
N("svc-anchor", "now", "Sovereign credit: published review calendars and contractual amortisation",
  1.0, "2026-10-02", "sovereign-credit", "invariant", "structural",
  "Definitional: p=1.0 because a lane anchor is a label, not a claim about the world. What makes this "
  "lane tractable is that the EU rating regulation forces agencies to pre-publish their sovereign "
  "review dates, the IMF runs its consultations and programme reviews on fixed cycles, and a bond's "
  "amortisation is a contract.",
  "Lane anchor. The tree has no sovereign-credit structure at all despite it being the transmission "
  "channel for every emerging-market risk row. Rows below price the CALENDAR and the CONTRACT, never "
  "a country-specific rating call - naming a sovereign's current rating would require a dated fact "
  "this file refuses to invent.",
  "Sovereign spreads are the discount rate for every asset in a jurisdiction; the calendar dates their repricing.")

N("svc-cra-calendar-2028", "svc-anchor",
  "EU-registered rating agencies publish their 2028 sovereign review calendars by end-December 2027",
  0.93, "2027-12-31", "sovereign-credit", "scheduled", "5 quarters",
  "Statutory requirement with a regulatory enforcement mechanism: the EU rating regulation requires "
  "registered agencies to publish, at the end of December, a calendar of the dates on which they will "
  "publish sovereign ratings and related outlooks for the following year. Non-publication is a "
  "supervisory breach, not a missed convention.",
  "The best scheduled row in the batch, because it converts an apparently discretionary act - an "
  "agency deciding to review a sovereign - into a published calendar. That is the whole reason this "
  "lane was worth building, and it is the 12-for-14 class in its purest form. SOFT part: the "
  "requirement binds EU-registered entities and their EU-endorsed ratings; actions published outside "
  "that perimeter are not calendared, so the row is about the EU regime, not about all ratings "
  "everywhere. Checkpoint because two regime rows resolve against what the calendars show.",
  "Pre-published review dates are tradeable event dates for sovereign spreads and index-inclusion risk.",
  kind="checkpoint",
  evidence=[{"fact": "The EU credit rating agency regulation requires registered agencies to publish "
                     "at the end of December a calendar of dates for the following year on which "
                     "they will publish sovereign ratings and related outlooks",
             "reported": "structural"}],
  shifts=[{"target": "svc-calendar-adherence", "p_to": 0.88,
           "note": "the published calendars are the denominator for the adherence row"},
          {"target": "svc-three-per-year", "p_to": 0.90,
           "note": "the calendars reveal how many dates each agency reserved"}])

N("svc-calendar-adherence", "svc-cra-calendar-2028",
  "At least 90% of 2028 EU sovereign rating publications fall on a pre-published calendar date",
  0.88, "2028-12-31", "sovereign-credit", "invariant", "2+ years",
  "Statutory rule plus its own escape hatch: the regulation confines sovereign publications to the "
  "calendared dates but permits deviation where necessary to comply with the duty to publish promptly "
  "on material new information, with an explanation. So the base case is adherence and the deviations "
  "are documented exceptions rather than silent ones.",
  "Invariant on a regulation rather than on arithmetic, which is why it is 0.88 rather than 0.95. The "
  "90% threshold is a deliberate choice: a 100% claim would be refused by the regulation's own "
  "deviation clause, and a threshold claim keeps the row scoreable instead of reducing it to the "
  "exception. SOFT part: the threshold itself, and the fact that nobody publishes this ratio - "
  "resolution requires counting actions against calendars, which is work, so log the counting method "
  "at logging time (R30) rather than discovering the ambiguity at horizon.",
  "Off-calendar actions are the ones that move spreads, because they are the ones nobody positioned for.")

N("svc-afterclose", "svc-cra-calendar-2028",
  "EU sovereign rating actions in 2028 continue to be published after the close of EU trading venues",
  0.92, "2028-12-31", "sovereign-credit", "invariant", "2+ years",
  "Statutory publication-timing rule: the regulation requires sovereign rating actions to be released "
  "after the close of business of EU trading venues and before they next open, specifically so that "
  "the market has time to absorb them. The timing is a legal obligation, not a courtesy.",
  "Invariant on a rule, and operationally the most useful row in the lane: it means sovereign rating "
  "risk is a GAP risk, concentrated into the overnight window on a known set of dates, rather than an "
  "intraday risk. That is a structural fact about when the price can move, which is the kind of "
  "statement this engine scores Brier 0.10 on. SOFT part: the perimeter is EU-registered entities, "
  "and a US-domiciled action on a US sovereign has no such constraint.",
  "Sovereign downgrade risk is an overnight gap on calendared Fridays, which is precisely how to hedge it.",
  evidence=[{"fact": "The EU rating regulation requires sovereign rating actions to be published "
                     "after the close of business of EU trading venues and at least one hour before "
                     "they open", "reported": "structural"}])

N("svc-three-per-year", "svc-cra-calendar-2028",
  "No EU-registered agency publishes more than three unsolicited sovereign reviews for a single "
  "sovereign in 2028", 0.90, "2028-12-31", "sovereign-credit", "invariant", "2+ years",
  "Statutory cap: the regulation limits the number of dates an agency may reserve for publishing "
  "unsolicited sovereign ratings in a year. The constraint is on the agency's own calendar, so "
  "exceeding it is a supervisory matter rather than a market event.",
  "Invariant on an explicit numerical cap written into law - the cleanest kind of structural "
  "constraint this lane has. It matters because it bounds how often an unsolicited sovereign view can "
  "be refreshed, which bounds how fast a rating can walk down in a crisis under the EU regime. SOFT "
  "part: the cap applies to unsolicited ratings and the regulation's deviation clause still permits "
  "additional publications on material new information, so a stressed sovereign can be reviewed more "
  "often than three times with an explanation; the row claims the CAP holds as the default, and that "
  "distinction is the soft edge.",
  "The cap bounds the pace of a ratings-driven spread spiral under the EU regime.")

N("svc-ig-boundary", "svc-anchor",
  "The investment-grade boundary is still BBB-/Baa3 on 2030-01-01", 0.96, "2030-01-01",
  "sovereign-credit", "invariant", "3+ years",
  "Definitional and institutional: investment grade is defined as BBB-/Baa3 and above on the "
  "agencies' published long-term scales, and that boundary is hard-wired into index rules, regulatory "
  "capital regimes and investment mandates worldwide. Moving it would require coordinated change "
  "across all of those at once.",
  "Invariant on a definition whose stickiness comes from network effects rather than from law - "
  "thousands of mandates reference it, so it is the most expensive definition in finance to change. "
  "In the tree because the IG boundary is the only place in sovereign credit where a one-notch rating "
  "move produces a discontinuous flow event, and every 'fallen angel' trade depends on the boundary "
  "staying where it is. SOFT part: scale notation could be revised without moving the economic "
  "boundary; resolve on whether BBB-/Baa3 remains the lowest IG notch.",
  "The IG boundary is where a one-notch move becomes a forced-seller event rather than a spread wiggle.",
  evidence=[{"fact": "Investment grade is defined as BBB-/Baa3 and above on the major agencies' "
                     "long-term rating scales", "reported": "structural"}])

N("svc-outlook-precedes", "svc-anchor",
  "More sovereign outlook changes than sovereign rating changes are published in 2028", 0.86,
  "2028-12-31", "sovereign-credit", "invariant", "2+ years",
  "Near-definitional institutional arithmetic: the agencies' published methodologies use an outlook "
  "as the signalling step that precedes a rating change over a one-to-two-year horizon. So most "
  "rating changes are preceded by an outlook change, AND outlooks are also assigned and revised "
  "without any rating change following. The outlook count is therefore structurally the larger of "
  "the two.",
  "Invariant because the relationship is a feature of how the rating process is constructed, not a "
  "statistical regularity - the set of outlook changes essentially contains the set of rating-change "
  "precursors plus the set of false starts. SOFT part: an agency can and does move a rating without a "
  "prior outlook change in a fast crisis, and a mass action across many sovereigns at once would "
  "distort the counts; priced at 0.86 for that and because nobody publishes the two counts side by "
  "side, so resolution requires a defined universe fixed at logging time.",
  "An outlook change is the cheap early warning; it reprices spreads at a fraction of a downgrade's size.")

N("svc-g7-no-hy", "svc-anchor",
  "No G7 sovereign carries a sub-investment-grade rating from any major agency on 2031-01-01", 0.97,
  "2031-01-01", "sovereign-credit", "invariant", "4+ years",
  "Notch-distance arithmetic on published transition data: the G7 sovereigns sit in the AA-to-AAA "
  "region of a 21-notch scale, so reaching sub-investment grade requires traversing roughly ten "
  "notches. The agencies' own published multi-year transition matrices put five-year migration from "
  "that region to speculative grade at effectively zero absent a default, and ratings move "
  "predominantly one notch at a time.",
  "Invariant class and the batch's strongest far-field near-certainty, built entirely out of the "
  "agencies' own published transition behaviour rather than out of any view about fiscal policy. It "
  "is also the lane's deliberate answer to the 9/20 resolution-~0.00 finding: a book unwilling to "
  "state a 0.97 earns no resolution. SOFT part: the rating floor for the most stretched G7 members is "
  "a long way above HY but the DIRECTION of travel is not in doubt, so this row is comfortable only "
  "because of the distance, not because the trend is favourable.",
  "If this ever looked live, every risk-free-rate assumption in global finance would be re-based.")

N("svc-g7-no-imf", "svc-anchor",
  "No G7 member has an IMF financing arrangement approved before 2030-01-01", 0.95, "2030-01-01",
  "sovereign-credit", "invariant", "3+ years",
  "Institutional structure plus a half-century record: G7 members are large quota holders and net "
  "creditors to the Fund, issue in their own currencies, and have central bank swap lines available "
  "as the first line of defence. The reference class of G7 programmes contains one entry in fifty "
  "years (the UK in 1976), before swap lines and floating rates were the norm.",
  "Invariant on institutional structure. Logged as a far-field negative on an event that the "
  "'sovereign debt crisis' genre prices as live every few years; the engine's job here is to say the "
  "base rate out loud. SOFT part: a precautionary or flexible credit line for a G7 member would be an "
  "'arrangement' on a literal reading while meaning something completely different from a programme, "
  "which is a resolution trap of exactly the #59 shape - resolve on an upper-credit-tranche "
  "arrangement with conditionality and reviews.",
  "A G7 programme would be the single largest repricing of sovereign risk in the post-war era.")

N("svc-weo-2028", "svc-anchor",
  "The IMF publishes a World Economic Outlook in both April and October 2028", 0.95, "2028-10-31",
  "sovereign-credit", "scheduled", "2+ years",
  "Published semiannual cycle tied to a fixed calendar: the WEO is released around the Spring "
  "Meetings and the Annual Meetings, both of which are themselves scheduled years in advance. The "
  "publication has run on that cycle without interruption.",
  "Scheduled-print class and the lane's cheap monitoring instrument: two observations a year on the "
  "debt-service and revenue projections that every sovereign-credit row in the tree is implicitly "
  "calibrated against. The claim is the EVENT, not the forecasts, and that distinction is the whole "
  "12-for-14 record. SOFT part: this is a conjunction of two publications, so by R36 it cannot beat "
  "its weaker leg; priced at 0.95 rather than at the single-publication rate for that reason.",
  "WEO publication dates are when the official debt-sustainability numbers get re-based.",
  evidence=[{"fact": "The IMF publishes the World Economic Outlook twice a year, around the Spring "
                     "Meetings and the Annual Meetings", "reported": "structural"}])

N("svc-art4-12m", "svc-anchor",
  "The IMF's standard Article IV consultation cycle is still twelve months for the great majority of "
  "members in 2028", 0.90, "2028-12-31", "sovereign-credit", "invariant", "2+ years",
  "Institutional rule: Article IV consultations are conducted on a standard twelve-month cycle under "
  "the Fund's surveillance framework, with a longer cycle available for a defined subset of members. "
  "The cycle length is set by Board decision, so it is an institutional constant rather than a "
  "staff-level choice.",
  "Invariant on an institutional cycle, and the reason the lane can date sovereign surveillance at "
  "all: a twelve-month cycle means every member's next staff report has a knowable window, which "
  "turns 'when do we get fresh official numbers' into a schedule. SOFT part: the 'great majority' "
  "qualifier is doing real work - the 24-month option, programme countries on different cadences and "
  "delayed consultations all exist, so this is a claim about the default, and a Board review of "
  "surveillance cadence is the live falsifier.",
  "The consultation cycle dates the arrival of official debt-service-to-revenue numbers for each sovereign.",
  evidence=[{"fact": "IMF Article IV consultations are conducted on a standard twelve-month cycle, "
                     "with a longer cycle available for certain members", "reported": "structural"}])

N("svc-review-board", "svc-anchor",
  "Every 2028 disbursement under an IMF upper-credit-tranche arrangement requires Board completion of "
  "a scheduled review", 0.97, "2028-12-31", "sovereign-credit", "invariant", "2+ years",
  "Institutional rule written into the arrangements themselves: purchases under an upper-credit-"
  "tranche arrangement become available only on the Executive Board's completion of the review for "
  "that period, against conditionality set out in the programme documents. The review schedule is "
  "published in the arrangement.",
  "Invariant on a rule, and the mechanism that makes programme countries datable: a review calendar "
  "is a published schedule of binary events with money attached, which is the single most tradeable "
  "structure in sovereign credit. This is the row that justifies the lane's existence alongside the "
  "CRA calendar rule. SOFT part: waivers of non-observance and rephasings are routine and let a "
  "review complete when conditionality was missed, so the row claims the PROCEDURE binds, not that "
  "conditionality does.",
  "Review completion dates are discrete, pre-published catalysts for programme-country spreads.",
  evidence=[{"fact": "Purchases under an IMF upper-credit-tranche arrangement become available only "
                     "upon Executive Board completion of the scheduled review",
             "reported": "structural"}])

N("svc-amort-contract", "svc-anchor",
  "Every eurobond with a 2028 contractual maturity either pays at par on that date or constitutes an "
  "event of default under its own terms", 0.97, "2028-12-31", "sovereign-credit", "invariant",
  "2+ years",
  "Contract arithmetic: a bond's maturity date and principal are terms of the instrument. "
  "Non-payment on the date is not a soft outcome - it is an event of default as the document defines "
  "it, subject only to the stated grace period. The amortisation calendar is therefore a published "
  "schedule of hard dates, which is what makes a debt-service-to-revenue ratio a forward-looking "
  "arithmetic object rather than an estimate.",
  "Invariant on contract terms, and the row that anchors every amortisation-calendar claim in the "
  "lane. Stated as a disjunction on purpose: it does not forecast WHETHER anyone pays, which would be "
  "a country call requiring facts this file will not invent - it pins the fact that there is no third "
  "option, which is what makes the calendar informative. SOFT part: a consensual exchange completed "
  "BEFORE maturity removes the bond from the schedule without triggering anything, and aggregated "
  "CACs make exactly that the modal restructuring path - so the row can be true while the economic "
  "question is answered elsewhere.",
  "The amortisation calendar is the hard-date grid every sovereign liquidity analysis is built on.",
  evidence=[{"fact": "A sovereign bond's maturity date and principal amount are contractual terms, "
                     "and non-payment after any stated grace period is an event of default under the "
                     "instrument", "reported": "structural"}])

N("svc-cf-fast", "svc-anchor",
  "A G20 Common Framework debt treatment is concluded within twelve months of its creditor committee "
  "being formed, for any case in 2028", 0.25, "2028-12-31", "sovereign-credit", "marker", "2+ years",
  "Prior only. The Common Framework requires an official creditor committee to agree a treatment and "
  "then comparability of treatment from private creditors - a sequential, multi-party process with no "
  "deadline and no enforcement. The reference class of completed cases is small and slow, and the "
  "structure itself has no mechanism that would make it fast.",
  "Marker class, priced as a genuine negative because the mechanism is a coordination problem among "
  "sovereign creditors with divergent interests - which is the discretionary-choice class where this "
  "book is 0-for-5, and here the choice has to be made many times over by different parties. R36 "
  "applies with force: a treatment needs committee agreement AND comparability, and the conjunction "
  "cannot beat its weakest leg. SOFT part: 'concluded' and 'formed' both need dates that are "
  "sometimes announced only in retrospect, so fix the definitions at logging time.",
  "Slow official-sector treatment is why distressed sovereign recovery timelines are measured in years, not quarters.")
