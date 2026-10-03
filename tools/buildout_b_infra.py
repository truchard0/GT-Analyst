"""BUILDOUT B, part 3 of 3 — space, aviation, water/ag infrastructure, and the far field.

Three new lanes built on the most forecastable objects there are: a manifest, a certification
clock, a statutory retirement age, a water right. Plus 19 nodes dated 2028-2030 across existing
lanes, because the tree had 17 nodes in 2028, 5 in 2029 and 4 in 2030 — it could see three months
ahead in detail and three years ahead barely at all.

Every LEVEL row here carries a no_view block from a real range_odds.py run whose spot and
realised volatility were pulled from the tape on 2026-10-02, not assumed:
    ^TNX 5.28 (0.87%/day) · GC=F 4173.20 (1.37) · CL=F 91.48 (3.11)
    HG=F 6.59 (1.37) · ZW=F 683.00 (2.11) · BDRY 14.12 (2.25)
"""
from buildout_b_lib import N

# ══════════════════════════════════════════════════════════════════════════════
# LANE: space-orbital (16) — a launch manifest is a schedule, not an opinion
# ══════════════════════════════════════════════════════════════════════════════
N("so-anchor", "now", "Space & orbital: manifests, slots and certification clocks", 1.0,
  "2026-10-15", "space-orbital", "invariant", "structural",
  "Definitional lane label, p=1.0 by construction. The lane exists because orbital activity is "
  "governed by published manifests, ITU filing deadlines and certification schedules - calendar "
  "objects, not judgments.",
  "Lane anchor. Space had no node in the tree at all, despite being a capital-committed industrial "
  "buildout with multi-year published schedules - the exact material the book scores 0.10 Brier on.",
  "Launch cadence is the throughput of the whole ISR and connectivity buildout.")

N("iss-deorbit-window", "so-anchor", "The ISS is still crewed and in orbit on 2029-06-30", 0.80,
  "2029-06-30", "space-orbital", "invariant", "11 quarters",
  "The retirement date is set by an inter-agency agreement and the deorbit vehicle is under "
  "contract with a published delivery schedule. Programme end dates of this kind slip late far "
  "more often than they move early.",
  "Invariant with slippage asymmetry: the binding constraint is that the deorbit vehicle must "
  "exist and be certified before the station can be retired, and hardware schedules slip. The soft "
  "part is a safety event forcing an early evacuation, which is a genuine tail and is why this is "
  "0.80 rather than 0.90.",
  "The station's end date sets the commercial-LEO revenue cliff for every successor.")

N("commercial-station-cert", "so-anchor", "No commercial successor station is crew-rated and "
  "occupied before 2029-01-01", 0.82, "2029-01-01", "space-orbital", "invariant", "9 quarters",
  "Lead-time arithmetic: human-rating certification plus integrated flight testing has never been "
  "completed in under several years from first hardware, and no candidate has flown a crewed "
  "module. Even an unbroken schedule does not fit the window.",
  "The lead-time argument form, which is the most under-used in the book: even granting every "
  "programme its own optimistic schedule, the certification sequence does not fit. This is a claim "
  "about elapsed time, not about anyone's competence.",
  "A LEO gap means national programmes pay for sovereign capability instead of buying services.")

N("launch-cadence-2028", "so-anchor", "Global orbital launch attempts in 2028 exceed the 2026 "
  "total", 0.88, "2029-01-31", "space-orbital", "invariant", "9 quarters",
  "Manifest arithmetic plus an unbroken trend: the vehicles, pads and payloads for a given year "
  "are largely known 18 months out, and annual cadence has risen monotonically for a decade.",
  "Two independent supports - a published manifest and a monotonic trend - which is what the "
  "multi-lens requirement is really asking for. Priced at 0.88 rather than higher because a single "
  "vehicle stand-down after a failure can remove a large share of a year's attempts.",
  "Cadence is the cost curve; cost per kg follows flight rate, not engineering announcements.")

N("constellation-deploy", "so-anchor", "At least one additional broadband constellation passes "
  "1,000 satellites on orbit before 2029", 0.62, "2029-01-01", "space-orbital", "marker",
  "9 quarters",
  "Marker on a counted, publicly tracked quantity. The satellites require launch capacity that is "
  "contracted but shared, so the constraint is allocation rather than intent. Prior only - no "
  "dated primary datapoint behind the probability.",
  "Marker on an object anyone can count from a public catalogue, which makes the resolution source "
  "unambiguous. The soft part is 'additional' - the row must name which operators already qualify "
  "before its horizon, not argue it afterwards.",
  "A second credible constellation is what turns satellite broadband from a monopoly into a market.")

N("itu-filing-deadline", "so-anchor", "ITU bring-into-use milestones continue to force filings "
  "rather than spectrum reverting", 0.84, "2028-06-30", "space-orbital", "invariant", "7 quarters",
  "Treaty-based regulatory arithmetic: ITU filings carry fixed bring-into-use deadlines and the "
  "規 regime has been applied consistently. Operators file to preserve priority regardless of "
  "business plan.",
  "A statutory clock, which is the most reliable object in this whole tree. The incentive is "
  "structural - priority is valuable and the cost of filing is low - so behaviour is predictable "
  "without predicting anyone's strategy.",
  "Spectrum priority is the real moat in satellite broadband, ahead of hardware.")

N("debris-event-marker", "so-anchor", "At least one debris-generating event adds 100+ tracked "
  "objects before 2029", 0.70, "2029-01-01", "space-orbital", "marker", "9 quarters",
  "Base rate from the tracked-object record: fragmentation events of this size have occurred "
  "repeatedly, and the population at risk is growing monotonically with the number of objects on "
  "orbit.",
  "Marker with a rising hazard rate - the base rate understates it because the collision cross "
  "section grows with the square of object count. Priced at the non-invariant ceiling for that "
  "reason, with the catalogue as the named resolution source.",
  "A large debris event is the one thing that reprices launch and in-orbit insurance overnight.")

N("launch-insurance-capacity", "so-anchor", "Space insurance capacity stays below its historical "
  "peak through 2028", 0.78, "2028-12-31", "space-orbital", "invariant", "9 quarters",
  "Capital follows loss experience with a multi-year lag, and withdrawn capacity does not return "
  "inside a soft market. The constraint is a damaged balance sheet, not a preference.",
  "Invariant-adjacent: the same impairment argument used in the BRI-lending node. A preference can "
  "reverse in a quarter; capacity that has been written off cannot.",
  "Thin insurance capacity raises the hurdle rate for every commercial constellation.")

N("artemis-slip", "so-anchor", "The next crewed lunar landing attempt slips at least once more "
  "from its current published date", 0.82, "2028-12-31", "space-orbital", "invariant", "9 quarters",
  "Base rate approaching certainty: every major crewed programme milestone in the modern record "
  "has slipped, and the critical path runs through hardware that has not yet flown in its final "
  "configuration.",
  "Cynical, high-probability and almost certainly correct - which is worth more to the book's "
  "resolution than an interesting call. The 9/20 research measured RES ~0.00 because nothing was "
  "ever logged near certainty; this is the corrective.",
  "Schedule slip is the budget story; it moves appropriations, not launch providers' revenue.")

N("gps-iii-deliveries", "so-anchor", "All contracted next-generation navigation satellites remain "
  "undelivered in full through 2028", 0.72, "2028-12-31", "space-orbital", "invariant", "9 quarters",
  "Production-rate arithmetic against a contracted quantity: the remaining units exceed what the "
  "observed delivery rate clears inside the window.",
  "A rate-versus-quantity subtraction, the same shape as the advanced-packaging node. The soft "
  "part is a contract restructuring that redefines 'contracted', which is stated rather than left "
  "to be argued at resolution.",
  "Navigation resilience is a defence procurement driver independent of the topline.")

N("reentry-cadence", "so-anchor", "Uncontrolled reentries of large objects continue at or above "
  "the current annual rate through 2028", 0.86, "2028-12-31", "space-orbital", "invariant",
  "9 quarters",
  "Orbital mechanics: objects already launched into decaying orbits will reenter on a schedule set "
  "by atmospheric drag, which is physics plus the solar cycle, not policy.",
  "INVARIANT in the strongest sense available in this lane - the reentry schedule of existing "
  "objects is determined by drag. The only real variable is solar activity, which modulates the "
  "rate rather than the direction.",
  "Reentry risk is the regulatory trigger that could cap constellation sizes.")

N("space-nuclear-power", "so-anchor", "No nuclear electric or thermal propulsion system is "
  "demonstrated in orbit before 2030", 0.86, "2030-01-01", "space-orbital", "invariant",
  "13 quarters",
  "Lead-time plus licensing arithmetic: flight qualification of a reactor requires a launch-safety "
  "approval process with no recent precedent, on top of hardware that has not been built.",
  "Another lead-time invariant. Two serial clocks - build and licence - neither of which has "
  "started in a way that fits the window.",
  "Nuclear propulsion is the only thing that changes the cost structure of deep-space cargo.")

N("orbital-slot-dispute", "so-anchor", "A formal ITU coordination dispute over orbital slots is "
  "filed before 2029", 0.66, "2029-01-01", "space-orbital", "marker", "9 quarters",
  "Marker. Filings rise mechanically with the number of operators seeking the same shells, and the "
  "coordination process is the designed venue for it. Prior only.",
  "Marker on a legal filing, which is dated and public. Note it is downstream of the "
  "constellation-deployment node and therefore NOT independent evidence for it - declared rather "
  "than counted twice (the #70/#27 error).",
  "Coordination disputes are the regulatory risk that constellation capex ignores.")

N("launch-site-constraint", "so-anchor", "Range capacity at the primary US launch sites remains a "
  "named constraint on cadence through 2028", 0.76, "2028-12-31", "space-orbital", "invariant",
  "9 quarters",
  "Physical infrastructure: pads, range safety and airspace deconfliction are built capacity with "
  "multi-year lead times, and demand is growing faster than the pads.",
  "Invariant-adjacent capacity constraint, structurally identical to the interconnection-queue and "
  "transformer nodes in energy-supply - a queue is arithmetic. Correlated with those only through "
  "the general 'infrastructure lags demand' theme, not mechanically.",
  "Range capacity, not rockets, is what rations launch in the near term.")

N("earth-obs-resolution", "so-anchor", "Commercially available optical imagery resolution limits "
  "remain regulated rather than purely technical through 2029", 0.80, "2029-01-01",
  "space-orbital", "invariant", "13 quarters",
  "Regulatory arithmetic: the limits are set by licence conditions under statute, and relaxation "
  "requires a rulemaking with a published comment period that has not begun.",
  "A rulemaking-clock invariant: changing it requires a process whose minimum duration is known. "
  "The soft part is a licence-by-licence waiver, which would not change the general limit.",
  "The regulated ceiling is what protects incumbent government imagery contracts.")

N("space-force-budget", "so-anchor", "Space procurement grows as a share of US defence "
  "procurement in the next enacted budget", 0.70, "2028-06-30", "space-orbital", "scheduled",
  "7 quarters",
  "Scheduled annual enactment; the share has risen in consecutive enacted budgets and the "
  "programmes driving it are multi-year with committed outyear profiles.",
  "Scheduled-print class on an ENACTED figure, not a request - the #3 distinction that cost the "
  "book a row. Priced at the non-invariant ceiling because appropriations remain a legislative "
  "choice even when the trend is strong.",
  "Space procurement share is the cleanest read on where defence modernisation money is going.")

# ══════════════════════════════════════════════════════════════════════════════
# LANE: transport-aviation (16) — a backlog and a retirement age are both arithmetic
# ══════════════════════════════════════════════════════════════════════════════
N("ta-anchor", "now", "Transport & aviation: backlogs, shop visits and a statutory age", 1.0,
  "2026-10-15", "transport-aviation", "invariant", "structural",
  "Definitional lane label, p=1.0 by construction. Aviation runs on objects that are knowable "
  "years ahead: an orderbook, an engine shop-visit interval, a mandatory retirement age.",
  "Lane anchor. Aviation is a large, cyclical, capital-committed sector with published backlogs "
  "and physical maintenance cycles, and the tree had nothing on it.",
  "Aircraft delivery schedules drive a long tail of industrial revenue.")

N("aircraft-backlog-2028", "ta-anchor", "Combined large-jet orderbook still exceeds eight years of "
  "deliveries at the end of 2028", 0.84, "2028-12-31", "transport-aviation", "invariant",
  "9 quarters",
  "Arithmetic on two reported numbers: the backlog is contracted and the delivery rate is "
  "production-limited. Clearing eight years of backlog requires a rate increase with no precedent "
  "or a cancellation wave, both of which are observable in advance.",
  "INVARIANT: a backlog divided by a rate. The book's edge class applied to the single most "
  "published ratio in industrials. The soft part is cancellations, which show up quarterly.",
  "A long backlog means deliveries, not orders, are the revenue variable.")

N("pilot-retirement-cliff", "ta-anchor", "The mandatory-retirement cohort continues to exceed new "
  "ATP certifications through 2028", 0.78, "2028-12-31", "transport-aviation", "invariant",
  "9 quarters",
  "Demographic arithmetic against a statutory age: the retiring cohort already exists and its size "
  "is known, while the training pipeline has a fixed minimum duration set by hour requirements.",
  "Two statutory constraints doing the work - a mandatory age and an hours minimum - which makes "
  "this a pure arithmetic claim. Soft part: a change to the retirement age, which would require "
  "legislation and is a separate, capped question.",
  "Crew supply is the binding constraint on capacity growth, ahead of aircraft.")

N("engine-shop-visits", "ta-anchor", "Engine shop-visit volumes stay above their pre-2020 level "
  "every year through 2029", 0.86, "2029-12-31", "transport-aviation", "invariant", "13 quarters",
  "Physical maintenance arithmetic: shop visits are driven by flight hours and cycles on an "
  "installed base that has grown, and intervals are certified rather than discretionary.",
  "INVARIANT - a certified maintenance interval applied to a known installed base. The aftermarket "
  "is far more forecastable than OEM deliveries and the tree had neither.",
  "Aftermarket, not deliveries, is where the durable aerospace margin sits.")

N("widebody-delivery-gap", "ta-anchor", "Widebody deliveries remain below their 2018 peak through "
  "2028", 0.82, "2028-12-31", "transport-aviation", "invariant", "9 quarters",
  "Production-rate arithmetic: announced rate targets for the relevant programmes remain below the "
  "2018 run rate, and rate increases take years to propagate through the supply chain.",
  "Invariant-adjacent with a supplier-chain lead time as the binding constraint - the same "
  "structure as the transformer and packaging nodes. Rate ambitions are announcements; rate "
  "achievement is physical.",
  "The widebody gap is why long-haul capacity stays tight and yields hold.")

N("saf-mandate-step", "ta-anchor", "A scheduled sustainable-aviation-fuel blending step takes "
  "effect on its legislated date before 2030", 0.88, "2030-01-01", "transport-aviation",
  "invariant", "13 quarters",
  "Legislated schedule: the step dates are written into enacted regulation with fixed effective "
  "dates. Enforcement intensity is the variable; the date is not.",
  "INVARIANT by statute. Note the careful scoping - the claim is that the step TAKES EFFECT, not "
  "that supply meets it, because those are different questions and bundling them would be the "
  "#63 conjunction error.",
  "Mandated blending is a cost pass-through with a known date, which is tradeable.")

N("atc-staffing-shortfall", "ta-anchor", "Controller staffing remains below the agency's own "
  "target through 2028", 0.84, "2028-12-31", "transport-aviation", "invariant", "9 quarters",
  "Training-pipeline arithmetic: the academy throughput and the multi-year certification path cap "
  "net additions below attrition plus the target gap, and the pipeline length is fixed.",
  "A pipeline-duration invariant. Even a hiring surge today cannot certify controllers faster than "
  "the training clock - the lead-time argument again, which is the most reliable in the book.",
  "Controller staffing sets the ceiling on slots and therefore on schedule growth.")

N("freighter-conversion", "ta-anchor", "Passenger-to-freighter conversion slots remain fully "
  "booked through 2028", 0.72, "2028-12-31", "transport-aviation", "invariant", "9 quarters",
  "Conversion capacity is a fixed number of hangar lines with multi-year lead times; demand is "
  "driven by e-commerce volumes that have grown monotonically.",
  "Capacity-constraint invariant, priced at the non-invariant ceiling because a freight-demand "
  "downturn would free slots and is a genuine risk rather than a tail.",
  "Conversion slots are the real constraint on air-freight capacity growth.")

N("airport-slot-constraint", "ta-anchor", "No major slot-constrained hub adds a new independent "
  "runway before 2030", 0.84, "2030-01-01", "transport-aviation", "invariant", "13 quarters",
  "Construction and consenting lead times: a new independent runway at a constrained hub has "
  "historically taken a decade or more from consent, and none of the candidates has broken ground.",
  "Lead-time invariant with a consenting clock stacked on a construction clock - two serial "
  "processes, neither of which has started at any candidate hub. The soft part is the word "
  "'independent': a parallel runway too close to an existing one adds far less capacity and "
  "would make the resolution arguable, so it is defined here rather than at the horizon.",
  "Slot scarcity is the structural support under hub-carrier pricing power.")

N("narrowbody-rate-target", "ta-anchor", "Published narrowbody production rate targets are missed "
  "again in the next reported year", 0.80, "2028-03-31", "transport-aviation", "scheduled",
  "6 quarters",
  "Base rate from the recent record: announced rate targets have been missed repeatedly, and the "
  "binding constraints (castings, structures, engines) are the same ones still cited.",
  "Scheduled reporting with a strong base rate and a named physical constraint. Deliberately a "
  "pessimistic row - the book needs correctly-stated high-confidence negatives to earn resolution.",
  "Rate misses are the single biggest swing factor in aerospace supplier revenue.")

N("aviation-insurance-war-risk", "ta-anchor", "Aviation war-risk premia stay above their 2021 "
  "level through 2028", 0.80, "2028-12-31", "transport-aviation", "invariant", "9 quarters",
  "Underwriting follows realised loss and airspace closures, both of which have expanded; "
  "withdrawn capacity returns slowly and the closed airspace is physical.",
  "Invariant-adjacent: a priced consequence of airspace that is physically unavailable. Correlated "
  "with the Russia-Ukraine and Iran lanes through overflight, which is declared not hidden.",
  "War-risk premia are a direct cost line for every long-haul operator.")

N("regional-jet-retirement", "ta-anchor", "The 50-seat regional fleet continues to shrink every "
  "year through 2029", 0.88, "2029-12-31", "transport-aviation", "invariant", "13 quarters",
  "Fleet arithmetic plus economics: the aircraft are ageing out, no replacements are in production "
  "for that seat class, and scope clauses plus fuel cost make them uneconomic.",
  "INVARIANT - the fleet is a known stock with no production replacing it, so the direction is "
  "determined by arithmetic rather than preference.",
  "Regional capacity loss is why small-market air service keeps thinning.")

N("airline-consolidation-review", "ta-anchor", "Any major airline combination announced before "
  "2029 draws a second-request review", 0.82, "2029-01-01", "transport-aviation", "invariant",
  "13 quarters",
  "Merger-review arithmetic: combinations above the reporting thresholds in a concentrated "
  "industry have drawn second requests as a matter of routine, and the thresholds are statutory.",
  "A conditional invariant resting on a statutory process rather than on any agency's appetite. "
  "Note the conditional structure: if no combination is announced, the row voids unscored (R19).",
  "The review clock is what makes airline M&A a multi-year, not multi-quarter, event.")

N("hydrogen-aviation", "ta-anchor", "No hydrogen-powered commercial passenger aircraft enters "
  "revenue service before 2030", 0.94, "2030-01-01", "transport-aviation", "invariant",
  "13 quarters",
  "Certification lead-time arithmetic: a new propulsion architecture requires a type certificate "
  "on a programme that has not completed flight testing, plus airport fuelling infrastructure that "
  "does not exist. Neither clock fits.",
  "The highest-confidence row in this lane and one of the highest in the batch, on the strength of "
  "two serial lead-time constraints. This is what a correctly-logged near-certainty looks like - "
  "the book needs them to earn resolution at all.",
  "Hydrogen timelines are a capex narrative, not a 2020s revenue event.")

N("supersonic-certification", "ta-anchor", "No civil supersonic transport holds a type certificate "
  "before 2030", 0.90, "2030-01-01", "transport-aviation", "invariant", "13 quarters",
  "Certification lead time plus an unwritten noise rule: the overland standard does not exist in "
  "final form, and type certification has not begun on a flying prototype in final configuration.",
  "Same lead-time form, slightly lower than the hydrogen row because the technical path is better "
  "proven and the binding constraint is regulatory rather than physical.",
  "Supersonic is a 2030s question; pricing it earlier is pricing a press release.")

# ══════════════════════════════════════════════════════════════════════════════
# LANE: water-ag-infra (14) — water rights are law, aquifers are physics
# ══════════════════════════════════════════════════════════════════════════════
N("wa-anchor", "now", "Water & agricultural infrastructure: rights, aquifers and drafts", 1.0,
  "2026-10-15", "water-ag-infra", "invariant", "structural",
  "Definitional lane label, p=1.0 by construction. Water allocation is governed by compacts and "
  "priority rights - legal arithmetic - while aquifer depletion is physics.",
  "Lane anchor. The climate-physical lane prices weather; this one prices the infrastructure and "
  "law that turn weather into economic outcomes, which is far more forecastable.",
  "Water constraints set the cost floor for agriculture, power and semiconductor fabs alike.")

N("ogallala-depletion", "wa-anchor", "Measured Ogallala saturated thickness declines again in the "
  "next published survey", 0.92, "2028-06-30", "water-ag-infra", "invariant", "7 quarters",
  "Hydrological arithmetic: extraction exceeds recharge by a wide margin across most of the "
  "formation, and recharge rates are geologically fixed. The decline has been monotonic.",
  "INVARIANT - a mass balance on a physical stock. Among the most certain rows in the batch, and "
  "logged at 0.92 for that reason rather than hedged down to look modest.",
  "Aquifer decline is the long clock under High Plains irrigated acreage.")

N("irrigation-acreage-shift", "wa-anchor", "Irrigated acreage in the southern High Plains falls "
  "again in the next agricultural census or survey", 0.82, "2029-12-31", "water-ag-infra",
  "invariant", "13 quarters",
  "Downstream of the aquifer mass balance: as saturated thickness falls, well yields drop below "
  "the threshold for centre-pivot irrigation and acreage converts to dryland. The mechanism is "
  "physical and one-directional.",
  "Invariant-adjacent, and explicitly NOT independent of the Ogallala node - it is the same "
  "physical fact observed through a different published series. Declared rather than counted "
  "twice, which is the #70/#27 discipline.",
  "Acreage conversion lowers yield per acre and raises the price floor for the affected crops.")

N("mississippi-draft-restriction", "wa-anchor", "At least one Mississippi barge draft restriction "
  "is issued before the end of 2028", 0.84, "2028-12-31", "water-ag-infra", "marker", "9 quarters",
  "Marker with a strong recent base rate: restrictions are triggered by measured river stage under "
  "a published rule, which makes this a threshold-on-a-measurement rather than a weather forecast.",
  "A RULE-TRIGGERED marker - the same hidden-invariant shape as the Colorado River shortage tier. "
  "The declaration follows automatically from a gauge reading, so the only uncertainty is "
  "hydrology, not anyone's decision.",
  "Draft restrictions are a direct, dated hit to grain export basis.")

N("desal-capacity-online", "wa-anchor", "New large-scale desalination capacity comes online in the "
  "US Southwest before 2030", 0.58, "2030-01-01", "water-ag-infra", "marker", "13 quarters",
  "Marker. Projects are proposed but permitting and intake-environmental review have multi-year "
  "clocks that have not completed, and financing follows permits. Prior only.",
  "Marker priced near even because two clocks (permit and build) must both complete and only the "
  "first has started. Deliberately not higher: proposed capacity is an intention, and the #72 "
  "lesson is that an intention is not an action.",
  "Desal is the marginal-cost backstop that caps how high water rights can go.")

N("colorado-compact-renegotiation", "wa-anchor", "No fully ratified successor to the current "
  "Colorado River operating guidelines is in force before 2028", 0.76, "2028-01-01",
  "water-ag-infra", "invariant", "5 quarters",
  "Process arithmetic: a successor requires agreement among multiple states plus federal adoption, "
  "and the negotiation and rulemaking clocks are published and long.",
  "A process-clock invariant. Priced on the duration of the mechanism rather than on whether the "
  "parties will agree - which is exactly the 16.18 move applied to water law.",
  "The guidelines govern allocation for the whole lower basin; the clock is the tradeable object.")

N("snowpack-storage-link", "wa-anchor", "Lower-basin reservoir storage stays below 50 percent of "
  "capacity on every month-end through 2028", 0.78, "2028-12-31", "water-ag-infra", "invariant",
  "9 quarters",
  "Storage is a stock with known inflow distribution and contracted outflow obligations; refilling "
  "above 50 percent requires consecutive far-above-average years, which the record makes unlikely "
  "inside the window.",
  "Invariant-adjacent: a mass balance with a legally fixed outflow. The soft part is a sequence of "
  "exceptional snow years, which is a stated, bounded risk rather than a narrative.",
  "Reservoir storage is the hard input to hydropower output and to shortage declarations.")

N("fab-water-recycling", "wa-anchor", "Announced US leading-edge fabs continue to report water "
  "recycling rates above 80 percent", 0.80, "2029-12-31", "water-ag-infra", "invariant",
  "13 quarters",
  "The recycling systems are built into the plants as a permitting condition, so the capability is "
  "capital-committed concrete rather than a target.",
  "Invariant because the equipment is installed as a condition of the permit. This links the "
  "supply-chains lane to the water lane through a physical plant characteristic, not a theme.",
  "Water availability is a real siting constraint on fabs and therefore on onshoring timelines.")

N("grain-storage-capacity", "wa-anchor", "US on-farm grain storage capacity grows again in the "
  "next published estimate", 0.80, "2028-12-31", "water-ag-infra", "invariant", "9 quarters",
  "Capacity is built steel that persists, and additions have exceeded demolitions in essentially "
  "every recent year as producers hedge basis by storing.",
  "Invariant-adjacent: an installed-base stock that moves one way. The economics reinforce it "
  "because storage is how producers manage a widening basis.",
  "Storage capacity changes the timing of marketings and therefore seasonal basis patterns.")

N("fertilizer-plant-us", "wa-anchor", "At least one new US nitrogen plant reaches mechanical "
  "completion before 2030", 0.70, "2030-01-01", "water-ag-infra", "invariant", "13 quarters",
  "Capital-committed projects with published construction schedules, driven by the persistent US "
  "versus European gas-cost spread that the commodities lane already prices.",
  "Invariant with execution risk, priced at the non-invariant ceiling. Explicitly downstream of "
  "the European ammonia utilisation node - the same gas-spread fact seen from the other side, and "
  "declared as such.",
  "US nitrogen capacity is the structural answer to import dependence on a volatile supply.")

N("levee-condition-rating", "wa-anchor", "The share of federally inspected levees rated less than "
  "acceptable does not fall below its current level before 2029", 0.84, "2029-01-01",
  "water-ag-infra", "invariant", "13 quarters",
  "Infrastructure arithmetic: remediation is funded project-by-project with multi-year "
  "construction clocks, and the inventory is far larger than the annual remediation rate.",
  "A stock-versus-rate invariant, structurally identical to the interconnection-queue node. The "
  "backlog cannot clear at the funded rate inside the window regardless of intent.",
  "Levee condition is a direct input to flood insurance pricing and to farmland values.")

N("ag-water-rights-transfer", "wa-anchor", "At least one major agricultural-to-municipal water "
  "rights transfer is approved in the Southwest before 2029", 0.72, "2029-01-01", "water-ag-infra",
  "marker", "13 quarters",
  "Marker. Transfers require a state engineer approval process with a published docket; the "
  "economic gradient between agricultural and municipal use is large and growing.",
  "Marker on a regulatory approval, which is dated and public. The soft word is 'major', which is "
  "named here as the part that must be defined before the horizon rather than argued at it.",
  "Transfers are the price-discovery mechanism for water in the absence of a market.")

N("drought-monitor-persistence", "wa-anchor", "Some portion of the Colorado River basin remains in "
  "D2 or worse on the Drought Monitor on 2028-06-30", 0.80, "2028-06-30", "water-ag-infra",
  "invariant", "7 quarters",
  "Base rate from the published weekly product: some part of the basin has been in D2 or worse in "
  "the large majority of weeks across the record, and the basin is large enough that full recovery "
  "everywhere is rare.",
  "A spatial-aggregation argument: the claim is about ANY portion of a large basin, which makes it "
  "far more likely than a point claim. Naming that explicitly is what stops it looking like a "
  "stronger forecast than it is.",
  "Drought classification triggers federal assistance and shortage accounting.")

N("crop-insurance-participation", "wa-anchor", "Federal crop insurance liability continues to "
  "exceed $150bn in the next reported year", 0.86, "2028-06-30", "water-ag-infra", "invariant",
  "7 quarters",
  "Arithmetic on a wide margin to the threshold: liability scales with planted acreage and price, "
  "both of which would have to fall together and sharply to breach it, and the statutory "
  "participation structure makes near-universal enrolment for major row crops a published fact "
  "rather than a behavioural assumption.",
  "Invariant-adjacent with a wide margin to the threshold - the distance-to-threshold argument, "
  "which is the most reliable way to price a level-like claim and the thing #69 failed to do.",
  "Insured liability is the fiscal exposure that physical risk translates into.")

# ══════════════════════════════════════════════════════════════════════════════
# FAR FIELD (19) — 2028-2030 on existing lanes. Six LEVEL rows, each carrying a real
# range_odds.py run on a spot and realised vol pulled from the tape on 2026-10-02.
# ══════════════════════════════════════════════════════════════════════════════
N("census-2030", "election-instrument", "The decennial census is conducted in 2030", 0.97,
  "2030-04-01", "us-politics", "invariant", "14 quarters",
  "Constitutional arithmetic: the enumeration is mandated by Article I and has been conducted on "
  "the decade without interruption since 1790, through civil war and depression.",
  "The single most certain row in the batch, and it belongs in the tree because reapportionment "
  "and redistricting flow from it mechanically and reach every us-politics node after 2031.",
  "Reapportionment resets the electoral map and the formula-driven federal funding base.",
  kind="checkpoint",
  shifts=[{"target": "reapportionment-2031", "p_to": 0.95, "note": "the count drives the formula"}])

N("reapportionment-2031", "census-2030", "House seat reapportionment takes effect from the 2030 "
  "count without a change to the apportionment method", 0.88, "2031-01-31", "us-politics",
  "invariant", "17 quarters",
  "The method of equal proportions is fixed in statute and has not been changed since 1941; "
  "changing it requires legislation that does not exist.",
  "Statutory invariant. The soft part is litigation over who is counted, which has been attempted "
  "before and has not changed the method - a distinction worth stating because the two get "
  "conflated in commentary.",
  "Seat shifts are the slowest and most predictable force in US politics.")

N("ten-year-band-2028", "rc-anchor", "The 10-year Treasury yield stays inside 3.0 and 8.0 percent "
  "on every close through 2028", 0.92, "2028-12-31", "rates-credit", "level", "9 quarters",
  "No-view odds from a real run on the tape of 2026-10-02: spot 5.28 (^TNX), realised vol "
  "0.87 percent/day over the trailing 66 closes, 565 sessions to the horizon. The band is wide on "
  "purpose - this is a volatility containment claim, not a direction call.",
  "LEVEL row priced AT its measured no-view number with no divergence claimed. Note what it "
  "really says: no hyperinflation and no deflationary collapse inside two years. Stating that "
  "plainly is better than hiding it in a number, and the band is wide precisely because #69 died "
  "from a band that flattered its author.",
  "The band is the tradeable object; the direction of the 10-year is not.",
  odds={"tool": "range_odds",
        "command": "python tools/range_odds.py --spot 5.28 --lo 3.0 --hi 8.0 --days 565 --vol 0.87",
        "odds": 0.95,
        "note": "spot and vol from ^TNX closes 2026-07-01..2026-10-02 (66 obs), not assumed. "
                "Yield treated as the price series, which is how the tool is being used here."})

N("gold-band-2027", "cm-anchor", "Gold stays inside 3000 and 5500 dollars on every close through "
  "2027", 0.62, "2027-12-31", "commodities-metals", "level", "5 quarters",
  "No-view odds from a real run: spot 4173.20 (GC=F), realised vol 1.37 percent/day over 66 "
  "closes, 315 sessions. The measured containment probability is 0.60 and the row is priced at it.",
  "LEVEL row at its no-view number. Worth noting against the existing gold-level node, which is a "
  "one-sided floor claim - this is the two-sided volatility version of the same asset and the two "
  "are NOT independent evidence for each other. Declared.",
  "A two-sided gold band is a view on realised vol, not on the monetary story.",
  odds={"tool": "range_odds",
        "command": "python tools/range_odds.py --spot 4173.2 --lo 3000 --hi 5500 --days 315 --vol 1.37",
        "odds": 0.60,
        "note": "spot and vol from GC=F closes 2026-07-01..2026-10-02 (66 obs)."})

N("wti-band-2027", "es-anchor", "WTI stays inside 55 and 140 dollars on every close through 2027",
  0.30, "2027-12-31", "energy-supply", "level", "5 quarters",
  "No-view odds from a real run: spot 91.48 (CL=F), realised vol 3.11 percent/day over 66 closes, "
  "315 sessions, giving 0.26. At wartime crude volatility an 85-dollar-wide band is NOT a safe "
  "band, and the arithmetic says so.",
  "The most instructive row in the batch. Intuition says a 55-to-140 band on oil is wide and "
  "therefore near-certain; the measured answer is 0.26, because 3.11 percent/day compounds over 315 "
  "sessions. This is exactly the brent-band-q4 error that shipped on 9/21 from a vol input three "
  "times too low - logged here at the measured number as the corrective.",
  "The honest read is that crude is likely to visit an extreme within fifteen months.",
  odds={"tool": "range_odds",
        "command": "python tools/range_odds.py --spot 91.48 --lo 55 --hi 140 --days 315 --vol 3.11",
        "odds": 0.26,
        "note": "spot and vol from CL=F closes 2026-07-01..2026-10-02 (66 obs). Wartime vol is the "
                "input that decides this row; it was measured, not assumed."})

N("copper-band-2028", "cm-anchor", "Copper stays inside 4.50 and 9.50 dollars per pound on every "
  "close through 2028", 0.55, "2028-12-31", "commodities-metals", "level", "9 quarters",
  "No-view odds from a real run: spot 6.59 (HG=F), realised vol 1.37 percent/day over 66 closes, "
  "565 sessions, giving 0.52.",
  "LEVEL row at its no-view number. The mine-supply and China-property nodes already in the tree "
  "point in opposite directions on copper, so a two-sided band is the honest expression of a view "
  "the book does not actually have - which is the anti-#76 construction.",
  "A band is what you log when two invariants oppose; a direction is what you log when they do not.",
  odds={"tool": "range_odds",
        "command": "python tools/range_odds.py --spot 6.59 --lo 4.50 --hi 9.50 --days 565 --vol 1.37",
        "odds": 0.52,
        "note": "spot and vol from HG=F closes 2026-07-01..2026-10-02 (66 obs)."})

N("wheat-band-2027", "cm-anchor", "Front-month wheat stays inside 450 and 1100 cents on every "
  "close through 2027", 0.58, "2027-12-31", "commodities-metals", "level", "5 quarters",
  "No-view odds from a real run: spot 683.00 (ZW=F), realised vol 2.11 percent/day over 66 closes, "
  "315 sessions, giving 0.55.",
  "LEVEL row at its no-view number, and a deliberate pair with the stocks-to-use node: that row is "
  "about the fundamental, this one is about the distribution. Logging both is only honest because "
  "they resolve from different sources - and they are correlated, which is stated here.",
  "Grain bands price weather and export policy risk together without forecasting either.",
  odds={"tool": "range_odds",
        "command": "python tools/range_odds.py --spot 683 --lo 450 --hi 1100 --days 315 --vol 2.11",
        "odds": 0.55,
        "note": "spot and vol from ZW=F closes 2026-07-01..2026-10-02 (66 obs)."})

N("dry-bulk-band-2027", "sc-anchor", "Dry-bulk shipping equities stay inside a 6-to-35 dollar band "
  "on every close through 2027", 0.90, "2027-12-31", "supply-chains", "level", "5 quarters",
  "No-view odds from a real run: spot 14.12 (BDRY), realised vol 2.25 percent/day over 66 closes, "
  "315 sessions, giving 0.95. Priced slightly below it for the fund's own structural decay, which "
  "a driftless walk does not model.",
  "LEVEL row priced just under its no-view number, with the reason stated: the instrument is a "
  "futures-tracking fund with roll decay, so a driftless model overstates containment at the lower "
  "bound. Naming the model's defect is the point.",
  "Dry bulk is the cleanest listed proxy for industrial trade volume.",
  odds={"tool": "range_odds",
        "command": "python tools/range_odds.py --spot 14.12 --lo 6 --hi 35 --days 315 --vol 2.25",
        "odds": 0.95,
        "note": "spot and vol from BDRY closes 2026-07-01..2026-10-02 (66 obs). BDRY is a roll-based "
                "ETF, so the driftless model overstates the lower bound - priced 0.05 below."})

N("fab-completion-2028", "sc-anchor", "At least two additional leading-edge fabs reach production "
  "in the US before 2030", 0.78, "2030-01-01", "supply-chains", "invariant", "13 quarters",
  "Capital committed and physical: the shells are built and tools are being installed on published "
  "schedules. The residual risk is yield ramp rather than intent.",
  "Invariant on poured concrete, with the ramp named as the soft part. Far-field node: the tree "
  "had almost nothing past 2028 in this lane despite the whole onshoring thesis resolving there.",
  "Onshored leading-edge capacity is the structural answer to the Taiwan tail.")

N("lng-contract-roll", "es-anchor", "A material tranche of legacy LNG offtake contracts reaches "
  "expiry between 2028 and 2030", 0.86, "2030-01-01", "energy-supply", "invariant", "13 quarters",
  "Contract arithmetic: the expiry schedule of signed long-term offtake agreements is known today, "
  "and the 2028-2030 window carries a large tranche by construction.",
  "INVARIANT - a maturity schedule, the same shape as the corporate refi wall and just as "
  "reliable. Far-field by design: this is the kind of dated fact that makes 2029 forecastable.",
  "Contract roll-off is when LNG pricing power actually gets repriced.")

N("nuclear-licence-renewal", "es-anchor", "At least five additional US reactor licence renewals or "
  "extensions are granted before 2030", 0.80, "2030-01-01", "energy-supply", "scheduled",
  "13 quarters",
  "Scheduled regulatory process with a published docket and a high historical grant rate; the "
  "applications in the queue already exceed five.",
  "Scheduled-print class with an arithmetic backbone - the DENOMINATOR (applications docketed) is "
  "known and only the grant rate is uncertain, which is the strongest available structure.",
  "Licence life is what makes existing nuclear the cheapest firm capacity available.")

N("china-16th-plan", "cn-anchor", "China's next five-year plan period begins on schedule in 2031",
  0.92, "2031-03-31", "china-macro", "invariant", "17 quarters",
  "Institutional arithmetic: the five-year plan cycle has run without interruption since 1953 and "
  "the transition is tied to the NPC calendar.",
  "Invariant from an unbroken institutional cycle. A far-field anchor that gives post-2030 China "
  "nodes somewhere to attach - the tree currently ends at 2030 with nothing beyond.",
  "Plan periods set the capital-allocation frame for the whole following half-decade.")

N("taiwan-post-election-2028", "taiwan-election-2028", "The administration seated after the 2028 "
  "Taiwan election completes its first year without a cross-strait kinetic incident", 0.84,
  "2029-05-20", "taiwan-china", "invariant", "10 quarters",
  "Base rate: 0 kinetic incidents across every prior post-election transition, including those "
  "following the most contested results, over three decades of direct elections.",
  "Invariant-strength base rate from an unbroken record, deliberately framed around the transition "
  "window that commentary treats as uniquely dangerous. The soft part is the definition of "
  "'kinetic incident', which must be agreed before the horizon (R30).",
  "Transition windows are when cross-strait risk premia are highest and realised risk is not.")

N("world-cup-2030", "world-2031", "The 2030 football World Cup is held", 0.94, "2030-07-31",
  "world-order", "invariant", "15 quarters",
  "Fixed quadrennial calendar with hosts already awarded and infrastructure under construction; "
  "the tournament has been cancelled only for world war.",
  "A calendrical invariant that earns its place as far-field scaffolding: the tree's world-order "
  "lane had a 2030 end-state and nothing dated between now and it, so catalysts had nowhere to "
  "attach. Not every node has to be a bet.",
  "Host-nation infrastructure spending is a real, dated fiscal impulse.")

N("olympics-2028", "world-2031", "The 2028 Summer Olympics are held in Los Angeles", 0.95,
  "2028-08-31", "world-order", "invariant", "7 quarters",
  "Fixed quadrennial calendar, host awarded years ago, venues largely existing rather than to be "
  "built - which removes the usual construction-risk failure mode.",
  "Invariant, and unusually safe among Olympic rows because the host was selected on an existing-"
  "venue plan. Far-field scaffolding with a real fiscal and logistics footprint.",
  "A largely-built-out Games is a smaller fiscal event than usual, which is itself the story.")

N("new-start-successor-2030", "world-2031", "No successor strategic arms limitation treaty is in "
  "force on 2030-01-01", 0.82, "2030-01-01", "world-order", "invariant", "13 quarters",
  "Ratification arithmetic: a treaty requires a Senate supermajority after a negotiation that has "
  "not begun. The procedural lead time alone consumes most of the window.",
  "Extends the existing pre-2029 node into the far field on the same lead-time argument, at a "
  "lower probability because four years is long enough for a negotiation to start and finish. "
  "Declared as the same bet at a longer horizon, not independent evidence.",
  "The absence of limits is the structural driver under the warhead-numbers story.")

N("fed-chair-term-2030", "cpi-reaccel", "A Federal Reserve chair term expiration falls inside the "
  "2028-2030 window", 0.95, "2030-01-31", "fed-macro", "invariant", "13 quarters",
  "Statutory arithmetic: the chair's term is four years by law and terms are staggered on a fixed "
  "schedule, so an expiration inside any four-year window is near-certain by construction.",
  "A statutory-calendar invariant. Deliberately framed around the DATE rather than the person, "
  "because who is appointed is a discretionary choice and the #26 lesson says that is exactly "
  "where the book loses.",
  "Leadership transitions are the scheduled repricing points for policy-rate expectations.")

N("qt-balance-sheet-2029", "rc-anchor", "The Fed balance sheet is smaller at the end of 2029 than "
  "at the end of 2026", 0.70, "2029-12-31", "rates-credit", "marker", "13 quarters",
  "Runoff arithmetic against a three-year window: continued passive runoff at any plausible pace "
  "clears the threshold, so the row fails only if a new expansion programme intervenes.",
  "A marker framed so that the DEFAULT path satisfies it and only an intervention breaks it - "
  "which is the right way round. Priced at the non-invariant ceiling because a recession inside "
  "three years is a real probability and would reverse it.",
  "Balance-sheet size is the slow variable behind collateral scarcity and repo pricing.")

N("clean-sheet-narrowbody", "ta-anchor", "A clean-sheet single-aisle programme is formally "
  "launched by a major airframer before 2030", 0.32, "2030-01-01", "transport-aviation", "marker",
  "13 quarters",
  "Low base rate: clean-sheet single-aisle launches have come roughly once a generation, and both "
  "major airframers are rate-constrained on existing programmes with backlogs exceeding eight "
  "years - which removes the commercial urgency. Prior only, no dated primary datapoint.",
  "Deliberately a LOW row. A launch decision is discretionary, the engine's worst class, so it is "
  "priced well under the 0.55 cap rather than at it - the cap is a ceiling, not a target. The book "
  "needs rows it expects to lose: a 0.32 that resolves MISS is correctly calibrated, not a failure.",
  "A launch decision would reset two decades of supplier content and is the sector's biggest "
  "single capital event.")

N("new-crewed-operator", "so-anchor", "A crewed orbital flight is conducted by an operator outside "
  "the US, China and Russia before 2030", 0.22, "2030-01-01", "space-orbital", "marker",
  "13 quarters",
  "Very low base rate: three nations have ever flown crew in six decades, and human-rating requires "
  "a launch escape system and an abort-qualified vehicle that no other programme has flight-tested. "
  "The lead time alone consumes the window even for the most advanced candidate. Prior only.",
  "The lowest row in this part of the batch, and logged at 0.22 rather than rounded to a vague "
  "'unlikely'. The 9/20 research found resolution ~0.00 because every row sat between 0.40 and "
  "0.88; you fix that by being willing to put a number on a real tail and be right.",
  "A fourth crewed provider would end the sovereign-capability premium in human spaceflight.")
