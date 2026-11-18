#!/usr/bin/env python3
"""BUILDOUT B — WORLD PART: 70 nodes across five new lanes.

global-elections (18) · russia-ukraine (16) · regulation-legal (14) ·
africa-frontier (12) · india-sa (10)

The shape being copied is `npt-notice-arithmetic`: take a charged question nobody can
forecast and replace it with a notice period, a filing clock, an amortisation date or a
constitutional formula that is already fixed. Every election node here prices the DATE and
says nothing about the winner — the winner is the exact class that went 0-for-8. Every legal
node prices the CLOCK and says nothing about the verdict. No level and no duration rows: those
need a real range_odds.py / cycle_odds.py run and are being authored elsewhere.

Not one dated news fact is invented. Where a date is derived it is derived from a published
calendar RULE (nth-weekday formulas were computed, not recalled); where a system fixes only a
DEADLINE and leaves the polling day to an executive, the node says so in its basis and the
claim is written to turn on the deadline.
"""
from buildout_b_lib import N

# ══════════════════════════════════════════════════════════════════════════════
# LANE: global-elections (18)
#   National elections whose date is fixed by constitution or statute, plus the
#   handful of parliamentary systems where only the DEADLINE is fixed. The event
#   is the invariant. Who wins is not, and is never priced below.
# ══════════════════════════════════════════════════════════════════════════════
N("ge-anchor", "now", "Global elections: the fixed-date calendar out to 2030", 1.0, "2026-10-02",
  "global-elections", "invariant", "structural",
  "Definitional: p=1.0 because a lane anchor is a label, not a claim about the world. What makes "
  "the lane tractable is that a large share of the world's electorates vote on a date fixed by "
  "constitutional or statutory formula, not by anyone's choice.",
  "Lane anchor. The organising distinction for every child row: the DATE is arithmetic (an "
  "nth-weekday formula, a term-expiry window, a notice period) and the RESULT is a discretionary "
  "human aggregate. This book is 8-for-8 on the first kind and 0-for-8 on the second, so no node "
  "in this lane forecasts a winner, a seat count or a coalition.",
  "Election dates are tradable as volatility calendar events long before any result is knowable.")

N("ge-us-2028-date", "ge-anchor",
  "US federal general election held Tuesday 2028-11-07", 0.97, "2028-11-07",
  "global-elections", "scheduled", "2 years",
  "STATUTORY FORMULA: 2 U.S.C. §7 and 3 U.S.C. §1 fix federal election day as the Tuesday next "
  "after the first Monday in November of the even-numbered year. Applying the formula to November "
  "2028 (first Monday falls on the 6th) gives the 7th. The date is a calendar computation, not a "
  "scheduling decision, and changing it requires an Act of Congress.",
  "Scheduled-print class for the EVENT only. The statute has produced an uninterrupted series "
  "since 1845 including through civil war, depression and pandemic, so the residual 0.03 is for "
  "the legislative amendment path, not for weather or administration. Nothing here is a view on "
  "the outcome: the SOFT part of any US election question is the result, and this node refuses to "
  "price it. Parked deliberately in the far field, which is where the tree is thinnest.",
  "The single largest scheduled vol event in the 2028 calendar; options surfaces date off it.",
  evidence=[{"fact": "2 U.S.C. §7 fixes federal election day as the Tuesday next after the first "
                     "Monday in November", "reported": "structural"}])

N("ge-us-ec-meet", "ge-us-2028-date",
  "Presidential electors meet in their states on 2028-12-18", 0.95, "2028-12-18",
  "global-elections", "scheduled", "2 years",
  "STATUTORY FORMULA as amended by the Electoral Count Reform Act: electors meet on the first "
  "Monday after the second Wednesday in December. For 2028 the second Wednesday is the 13th, so "
  "the first Monday after it is the 18th. Pure calendar arithmetic off enacted text.",
  "The ECRA deliberately converted the contested parts of the 2020 cycle into clocks: a fixed "
  "certification deadline, a fixed meeting date, a fixed count date. That is exactly the "
  "transformation this engine is good at pricing. SOFT part: whether any state's slate is "
  "contested on the day — which is why the claim is only that the meeting occurs on its statutory "
  "date, not that it is uneventful.",
  "The December meeting date bounds how long post-election legal uncertainty can stay unresolved.")

N("ge-us-count-jan6", "ge-us-ec-meet",
  "Congress convenes in joint session to count electoral votes on 2029-01-06", 0.93, "2029-01-06",
  "global-elections", "scheduled", "2 years",
  "STATUTORY DATE: the Electoral Count Reform Act fixes the joint session for January 6 following "
  "the meeting of electors, moving it only when that date falls on a Sunday. 2029-01-06 is a "
  "Saturday (computed), so no substitution rule applies and the statutory date stands.",
  "A scheduled constitutional mechanic, priced on enacted text plus a weekday computation. The "
  "SOFT part is the conduct of the session, not its date — the ECRA raised the objection "
  "threshold to one-fifth of each chamber and confined the Vice-President's role to ministerial "
  "acts, which narrows what can happen but says nothing about whether anyone tries. This node "
  "makes no claim about objections.",
  "The count date is the last structural checkpoint before inauguration risk is retired.")

N("ge-us-inauguration", "ge-us-count-jan6",
  "A presidential term begins at noon on 2029-01-20 under the 20th Amendment", 0.97, "2029-01-20",
  "global-elections", "invariant", "2 years",
  "CONSTITUTIONAL TEXT: the Twentieth Amendment ends the presidential and vice-presidential terms "
  "at noon on January 20 and begins the successors' terms at that instant. The hand-over is "
  "automatic — it does not require a ceremony, an oath on the day, or anyone's cooperation. "
  "2029-01-20 is a Saturday (computed); the public ceremony is customarily moved only when the "
  "20th falls on a Sunday, and in any case the constitutional moment does not move.",
  "The strongest shape in this lane: the constitution does not schedule an event, it terminates "
  "one legal state and starts another at a named instant. There is no discretionary actor in the "
  "mechanism at all, which is why it carries a higher price than the election that precedes it. "
  "SOFT part: nothing about the identity of the office-holder is claimed, and the amendment "
  "itself contemplates the case where no president-elect has qualified.",
  "The term boundary is the hard date for every policy-regime trade that resets with an "
  "administration.",
  evidence=[{"fact": "The Twentieth Amendment fixes the end of the presidential term at noon on "
                     "January 20", "reported": "structural"}])

N("ge-mexico-2030", "ge-anchor",
  "Mexican general election held on the first Sunday of June 2030 (2030-06-02)", 0.91, "2030-06-02",
  "global-elections", "scheduled", "3+ years",
  "CONSTITUTIONAL CALENDAR: the 2014 political reform amended Article 41 to fix the federal "
  "election for the first Sunday of June of the election year, replacing the old July date. "
  "Applying the formula to June 2030 gives the 2nd (computed). Six-year presidential term with no "
  "re-election makes 2030 the scheduled presidential year.",
  "Priced below the US rows for one honest reason: Mexico's election day was moved by amendment "
  "inside the last twelve years, so the demonstrated amendment frequency here is not zero the way "
  "it is for 2 U.S.C. §7. SOFT part: the constitutional date can be amended again on a "
  "two-thirds congressional majority plus state legislatures, and a party holding that majority "
  "has standing proposals touching electoral institutions. Still an arithmetic row, just not a "
  "0.97 one. No view whatsoever on the result.",
  "A 2030 presidential date anchors the peso's long-dated political risk premium.")

N("ge-brazil-2030", "ge-anchor",
  "Brazilian general election first round on the first Sunday of October 2030 (2030-10-06)", 0.90,
  "2030-10-06", "global-elections", "scheduled", "4 years",
  "STATUTORY CALENDAR: the Brazilian elections law fixes the first round for the first Sunday of "
  "October of the election year and any runoff for the last Sunday of October. Applying both "
  "formulas to October 2030 gives the 6th and the 27th (computed). Four-year presidential term "
  "makes 2030 the scheduled year.",
  "Scheduled class on a published statutory calendar that has run on the same formula through "
  "every cycle of the current constitutional order. SOFT part: the two-round structure means the "
  "resolving date for a presidential contest may be the October 27 runoff rather than the first "
  "round, so a trade dated on this node must specify which. Deliberately silent on candidates — "
  "the Brazilian first-round polling-to-result map is the levered-proxy error waiting to happen.",
  "A fixed October first round plus a fixed late-October runoff gives two dated BRL vol humps.")

N("ge-philippines-2028", "ge-anchor",
  "Philippine national election held on the second Monday of May 2028 (2028-05-08)", 0.92,
  "2028-05-08", "global-elections", "scheduled", "19 months",
  "CONSTITUTIONAL TEXT: the 1987 Constitution sets the regular election for President and "
  "Vice-President on the second Monday of May, and the same formula governs the synchronised "
  "national and local elections. Applying it to May 2028 gives the 8th (computed). Single "
  "six-year presidential term with no re-election makes 2028 the scheduled presidential year.",
  "The formula is in the constitution itself rather than in an election code, which is why this "
  "sits at the top of the non-US group. SOFT part: the Philippines has a live charter-change "
  "discussion in most congresses, and a constitutional convention is the one path that could move "
  "the formula; none of that is forecastable, and none of it is needed for the node to resolve. "
  "No view on the succession.",
  "A dated 2028 transition is the scheduling anchor for Philippine sovereign and utility risk.")

N("ge-korea-na-2028", "ge-anchor",
  "South Korean National Assembly election on the second Wednesday of April 2028 (2028-04-12)",
  0.91, "2028-04-12", "global-elections", "scheduled", "18 months",
  "STATUTORY FORMULA: the Public Official Election Act fixes the general election for National "
  "Assembly members on the second Wednesday of April in the expiry year of the four-year term. "
  "Applying the formula to April 2028 gives the 12th (computed). Assembly terms are fixed at four "
  "years and the Assembly cannot be dissolved early under the current constitution.",
  "This is the cleaner Korean row precisely because the legislature CANNOT be dissolved — the "
  "1987 constitution removed presidential dissolution power, so the four-year clock runs "
  "mechanically and the statutory weekday formula does the rest. SOFT part: a by-election "
  "calendar runs alongside it on different statutory dates, so a resolution source must specify "
  "the general election. The presidential clock is separate and is not claimed here.",
  "A non-dissolvable legislature makes the Korean political calendar one of the few genuinely "
  "pre-dated ones in Asia.")

N("ge-kenya-2027", "ge-anchor",
  "Kenyan general election on the second Tuesday of August 2027 (2027-08-10)", 0.90, "2027-08-10",
  "global-elections", "scheduled", "10 months",
  "CONSTITUTIONAL TEXT: the 2010 Constitution fixes the general election for the second Tuesday "
  "in August in every fifth year. Applying the formula to August 2027 gives the 10th (computed). "
  "The date is in the constitution, not in an electoral statute, so moving it needs a "
  "constitutional amendment rather than a commission decision.",
  "A constitution that literally names a weekday-of-month is the best possible basis for an "
  "election-date row. SOFT part: Kenya's courts have twice had to order reruns or extend "
  "timetables, so the general election DAY has held while the resolution of the contest has "
  "slipped past it; a node dated on the first ballot must not be read as a node on the final "
  "declaration. No view on the contest.",
  "The August date frames Kenyan eurobond and shilling risk a full year ahead.",
  evidence=[{"fact": "Kenya's 2010 Constitution fixes the general election for the second Tuesday "
                     "in August of every fifth year", "reported": "structural"}])

N("ge-nigeria-window-2027", "ge-anchor",
  "Nigerian presidential ballot falls inside the statutory 150-to-30-day pre-expiry window", 0.88,
  "2027-02-28", "global-elections", "invariant", "17 months",
  "STATUTORY WINDOW, NOT A SCHEDULED DATE: the constitution and the Electoral Act require the "
  "presidential election to be held not earlier than 150 days and not later than 30 days before "
  "the expiry of the incumbent term, and require the commission to publish a notice of election "
  "ahead of the poll. The claim is about the WINDOW, which is statutory arithmetic; the exact "
  "polling day is set by the commission inside it and is not asserted here.",
  "Written this way on purpose. I do not know Nigeria's 2027 polling date and will not guess one, "
  "so the node turns on the statutory bracket rather than on a day. That is the `npt-notice` move: "
  "a bill tabled is not a notice filed, and a commission timetable announced is not a statutory "
  "window changed. SOFT part: the commission's choice inside the window, and the real possibility "
  "that litigation reruns individual contests after the presidential poll.",
  "The window, not the day, is what bounds pre-election naira and fuel-subsidy positioning.")

N("ge-uk-deadline-2029", "ge-anchor",
  "UK general election held on or before the automatic-dissolution deadline (polling day by "
  "late summer 2029)", 0.90, "2029-08-31", "global-elections", "invariant", "3 years",
  "DEADLINE ONLY — EXPLICITLY: the UK fixes no polling day. The Dissolution and Calling of "
  "Parliament Act 2022 restored the prerogative to dissolve at any time, but left a backstop: "
  "Parliament dissolves automatically five years after the day it first met, and polling day must "
  "then follow within the statutory number of working days set by the writ timetable. So the "
  "constraint is a CEILING computed off the date the current Parliament first met, and everything "
  "before that ceiling is a prime-ministerial choice.",
  "The honest form of a Westminster election node. The five-year ceiling is statutory arithmetic; "
  "the date inside it is the single most discretionary call in British politics and is exactly the "
  "class this book loses on, so the node claims only the ceiling. SOFT part: the working-day "
  "count between automatic dissolution and polling day pushes the true ceiling a few weeks past "
  "the five-year anniversary, which is why the node is dated to a month-end rather than to a day.",
  "A ceiling, not a date — gilt and sterling event risk must be priced as an open window, not a "
  "point.")

N("ge-germany-window", "ge-anchor",
  "German Bundestag election falls inside the Basic Law's 46-to-48-month window", 0.90,
  "2029-02-28", "global-elections", "invariant", "2+ years",
  "CONSTITUTIONAL ARITHMETIC: Basic Law Article 39 requires a new Bundestag to be elected no "
  "earlier than forty-six and no later than forty-eight months after the start of the sitting "
  "term, with a shorter window after a dissolution. The window is a constitutional computation "
  "off the current Bundestag's first sitting; the day inside it is set by presidential order on "
  "the government's advice.",
  "DEADLINE-AND-FLOOR, not a date — the Basic Law gives both ends of the bracket, which is "
  "stronger than a pure ceiling. SOFT part: Article 68 lets a chancellor engineer an early "
  "dissolution through a lost confidence vote, which has happened three times in the Federal "
  "Republic and happened most recently in this decade, so the window can be pre-empted. The node "
  "is therefore a claim about the ORDINARY path and is priced below the non-dissolvable systems.",
  "A 46-48 month bracket is enough to date German fiscal-rule and defence-spending risk without "
  "guessing a polling day.")

N("ge-india-deadline-2029", "ge-anchor",
  "Indian Lok Sabha general election completed on or before the Article 83(2) five-year expiry",
  0.92, "2029-06-30", "global-elections", "invariant", "2+ years",
  "CONSTITUTIONAL ARITHMETIC: Article 83(2) gives the House of the People a term of five years "
  "from the date appointed for its first meeting and provides that the House dissolves on that "
  "expiry unless the term is extended during a proclaimed Emergency, and then only by one year at "
  "a time. The deadline is computed off the first sitting of the current House; the polling "
  "schedule inside it is the Election Commission's.",
  "Deadline arithmetic with a single named escape hatch (an Article 352 Emergency), which is what "
  "lets this be priced high: the escape hatch has been used once in the republic's history and "
  "requires a proclamation that is itself justiciable. SOFT part: the multi-phase polling schedule "
  "means the election spans weeks, so a resolution source must name either the first phase or the "
  "counting day. No view on the result, the seat count or the coalition.",
  "The five-year ceiling dates the next Indian policy-regime reset for rates, fuel and capex.")

N("ge-sa-90day-2029", "ge-anchor",
  "South African National Assembly election held within the Constitution's 90-day post-expiry "
  "window", 0.89, "2029-08-31", "global-elections", "invariant", "2+ years",
  "CONSTITUTIONAL ARITHMETIC: section 49 of the 1996 Constitution gives the National Assembly a "
  "five-year term and requires an election within ninety days of the expiry of that term, with "
  "the Assembly remaining competent in the interim. The President proclaims the date inside that "
  "bracket. So the constraint is five years plus a ninety-day tail, computed off the current "
  "Assembly's first sitting.",
  "The ninety-day tail is the unusual feature and the reason this is a window row rather than a "
  "date row: the constitution explicitly contemplates voting AFTER the term has expired, which "
  "makes a naive 'election in the expiry year' framing wrong in the tail case. SOFT part: an "
  "early dissolution under section 50 is available after three years and on a majority vote, "
  "which can pre-empt the window entirely.",
  "A bracket that can legally spill into the following quarter matters for ZAR event pricing.")

N("ge-japan-hr-ceiling", "ge-anchor",
  "Japanese House of Representatives election held on or before the four-year term ceiling", 0.95,
  "2028-10-31", "global-elections", "invariant", "2 years",
  "CONSTITUTIONAL CEILING, NO FIXED DATE: Article 45 gives members of the House of "
  "Representatives a four-year term, expressly terminable earlier by dissolution, and the Public "
  "Offices Election Act then fixes the interval within which polling must follow a dissolution or "
  "an expiry. Japan therefore has no scheduled general election date at all — only a ceiling "
  "computed off the last general election day, and in practice the House has almost always been "
  "dissolved before reaching it.",
  "The most explicitly deadline-only row in this lane and priced highest for that reason: the "
  "claim is 'on or before', and the historical base rate of reaching the full four years in the "
  "post-war Diet is close to zero, which makes an early resolution overwhelmingly likely and a "
  "LATE resolution essentially impossible. SOFT part: the exact ceiling depends on the last "
  "general election day, which is why the node is dated to a month-end and the basis states the "
  "ceiling is computed rather than quoted. Nothing is claimed about the governing coalition.",
  "An 'any time before' ceiling means Japanese political risk is a continuous, not a dated, "
  "exposure — the opposite of the US row.")

N("ge-france-art7-2027", "ge-anchor",
  "French presidential first round falls inside the Article 7 twenty-to-thirty-five-day pre-expiry "
  "window", 0.91, "2027-05-31", "global-elections", "invariant", "8 months",
  "CONSTITUTIONAL WINDOW: Article 7 of the Fifth Republic constitution requires the election of "
  "the President to be held not fewer than twenty and not more than thirty-five days before the "
  "expiry of the incumbent's powers, with the second round fourteen days after the first. The "
  "government fixes the actual Sundays by decree inside that bracket, so the window is "
  "constitutional arithmetic and the day is executive.",
  "Deliberately a window row: I am not certain of the decreed 2027 Sundays and will not state "
  "one as fact. Article 7 also supplies the two-round interval, which means the resolving date "
  "for a presidential contest is mechanically fourteen days after whatever first round is "
  "decreed. SOFT part: Article 7 also covers vacancy, in which case the window is recomputed off "
  "the vacancy rather than off the term, and the node would need re-dating rather than resolving.",
  "A fixed fourteen-day inter-round gap is the cleanest dated OAT and CAC vol structure in Europe.")

N("ge-canada-early-writs", "ge-anchor",
  "Writs for a Canadian general election are issued before the statutory fixed date", 0.42,
  "2029-10-15", "global-elections", "marker", "3 years",
  "The Canada Elections Act fixes polling day as the third Monday of October in the fourth "
  "calendar year after the previous general election — computed as 2029-10-15 for a cycle begun "
  "in 2025 — but the same section expressly preserves the Governor General's power to dissolve "
  "Parliament earlier, and the statutory date has been pre-empted in a majority of cycles since "
  "it was enacted. The reference class is 'fixed-date parliaments with a live dissolution power'.",
  "A MARKER on the appearance of early writs, priced BELOW even money and well below any of the "
  "fixed-date rows above, because the operative question is a discretionary dissolution and that "
  "is the 0-for-8 class. Logged as a genuine coin-ish row rather than dressed up: the book's "
  "measured resolution is ~0.00 precisely because nothing was ever stated near 0.40. SOFT part: "
  "everything — the parliamentary arithmetic that makes early dissolution attractive is not "
  "knowable three years out, which is why this is a marker and not an invariant.",
  "A statutory date with a demonstrated override rate is not a tradable date; treat Canadian "
  "political risk as continuous.")

# ══════════════════════════════════════════════════════════════════════════════
# LANE: russia-ukraine (16)
#   The lane behind several existing Europe nodes that had none of its own.
#   Force-generation and equipment arithmetic, route capacity, the sanctions and
#   frozen-asset legal clocks, reconstruction financing, the institutional calendar.
#   No node here forecasts a front line, a ceasefire or a negotiation outcome.
# ══════════════════════════════════════════════════════════════════════════════
N("ru-anchor", "now", "Russia-Ukraine: the arithmetic under the war", 1.0, "2026-10-02",
  "russia-ukraine", "invariant", "structural",
  "Definitional: p=1.0 because a lane anchor is a label, not a claim about the world. The lane "
  "exists because the forecastable content of this war is stocks, capacities, legal notice "
  "periods and renewal calendars — not intentions.",
  "Lane anchor. Every child row below is a stock, a capacity, a treaty clock or a published "
  "renewal date. Nothing in this lane prices a front line, a ceasefire, a negotiation or a "
  "leadership outcome: those are the conjunction-and-choice shapes behind the engine's twelve "
  "misses, and the Iran cluster already demonstrated what leg-extrapolation on an oscillating "
  "war tape costs (0-for-8, Brier 0.47).",
  "The war's tradable content is energy routing, defence backlogs and the euro-area's legal "
  "exposure, all of which are calendared.")

N("ru-stored-stock-monotonic", "ru-anchor",
  "Refurbishment of Soviet-era stored armour remains a monotonically depleting draw through "
  "mid-2028", 0.92, "2028-06-30", "russia-ukraine", "invariant", "20 months",
  "STOCK ARITHMETIC: open-air storage parks are a finite, non-replenishing inventory. Every "
  "vehicle pulled for refurbishment permanently reduces the remaining count, and nothing adds to "
  "it — the production lines that built those hulls are closed. So the stock is monotonic "
  "downward by construction, and the refurbishment rate is bounded above by the remaining stock "
  "divided by the horizon, whatever anyone intends.",
  "An invariant in the strict sense: no agency left in the direction of travel, only in the rate. "
  "This is the correct way to express what would otherwise be a 'Russia runs out of tanks by "
  "date X' call — the stock claim is arithmetic and the date claim is not, so only the arithmetic "
  "is logged. SOFT part: the stock's STARTING level and the share of it that is recoverable are "
  "both contested and are not asserted here; the monotonicity does not depend on either.",
  "Equipment attrition that cannot be replaced from inventory is what eventually forces the "
  "procurement mix toward new build, repricing the whole European defence backlog.")

N("ru-newbuild-capacity-ceiling", "ru-stored-stock-monotonic",
  "New-build heavy-armour output stays bounded by installed plant capacity through 2028", 0.89,
  "2028-12-31", "russia-ukraine", "invariant", "2 years",
  "CAPACITY AND LEAD TIME: new-build armour output is bounded by installed capacity at a small "
  "number of integrated plants, and installed capacity cannot be materially expanded inside the "
  "horizon because the binding inputs — large-format machine tools, armour-plate rolling and "
  "skilled fitters — carry lead times measured in years and are themselves sanctioned imports. "
  "A capacity ceiling is a physical constraint, not a budget decision.",
  "Capacity-and-lead-time class, the same shape as the transformer and CoWoS nodes that this book "
  "gets right. The claim is about the CEILING, not about utilisation: a plant running flat out and "
  "a plant running at half rate both satisfy it. SOFT part: the ceiling's level, and the "
  "possibility that imported tooling arrives through third countries faster than the sanctioned "
  "lead time implies. Money does not compress a machine-tool delivery.",
  "A hard output ceiling is why the war's equipment economics are a stock-depletion story rather "
  "than an industrial-mobilisation story.")

N("ru-westbound-route-capacity", "ru-anchor",
  "EU-bound Russian pipeline capacity stays bounded by the operable southern route through 2028",
  0.90, "2028-12-31", "russia-ukraine", "invariant", "2 years",
  "CAPACITY ARITHMETIC ON A FIXED PIPE SET: westbound Russian gas has only a handful of physical "
  "corridors, and the ceiling on deliveries is the sum of the installed capacity of those that "
  "are operable and contracted. The Baltic subsea route is physically damaged, the Belarus "
  "corridor is unused, and the five-year Ukraine transit contract reached its own stated expiry — "
  "so the ceiling is set by the southern route's nameplate, a published number that cannot be "
  "raised without building compression.",
  "A route-capacity row, not a flow forecast. The useful property is that new pipeline capacity "
  "has a construction lead time of years, so the 2028 CEILING is already fixed by what exists "
  "today whatever any party decides. SOFT part: utilisation inside the ceiling, which is a "
  "commercial and political variable; and the possibility of interruptible capacity bookings "
  "restoring flow through a corridor without a long-term contract, which would not breach the "
  "ceiling claim.",
  "The ceiling, not the politics, is what caps how much European gas supply can re-source "
  "eastward in any scenario.")

N("ru-sanctions-renewal-2027", "ru-anchor",
  "EU sectoral sanctions renewal decision falls due on its six-month cycle in early 2027", 0.93,
  "2027-01-31", "russia-ukraine", "scheduled", "4 months",
  "PUBLISHED RENEWAL CYCLE PLUS A UNANIMITY RULE: the EU's sectoral measures are established by a "
  "Council decision with a fixed expiry and are extended by unanimity every six months, which is "
  "why the renewal dates land in the same two months each year. The renewal is a calendared "
  "institutional act; its REQUIREMENT is treaty-based, because CFSP decisions need unanimity "
  "under Article 31 TEU and a single member state's abstention-or-worse is dispositive.",
  "Scheduled-print class for the EVENT — the engine is 12-for-14 on these. The node claims the "
  "decision point exists on the cycle, not what it decides. That distinction matters more here "
  "than anywhere: the unanimity requirement means the clock, not the consensus, is the thing that "
  "can be priced. SOFT part: the outcome, obviously, and the fact that a lapse would not "
  "automatically unwind national implementing measures.",
  "Every six months the euro area re-underwrites its own exposure; the date is the risk, not the "
  "rhetoric.",
  kind="checkpoint",
  evidence=[{"fact": "EU CFSP decisions require unanimity in Council under Article 31 TEU",
             "reported": "structural"}],
  shifts=[{"target": "ru-asset-immobilisation-clock", "p_to": 0.90,
           "note": "the immobilisation rides the same renewal instrument"},
          {"target": "ru-reparations-principal-held", "p_to": 0.84,
           "note": "a contested renewal is the moment the principal question gets forced"}])

N("ru-asset-immobilisation-clock", "ru-sanctions-renewal-2027",
  "Immobilisation of Russian central-bank assets still rests on a periodically renewed instrument "
  "at mid-2027", 0.92, "2027-07-31", "russia-ukraine", "scheduled", "10 months",
  "LEGAL-INSTRUMENT ARITHMETIC: the immobilisation is not a permanent confiscation — it is a "
  "restrictive measure carried by a Council instrument with a stated expiry that must be renewed "
  "on the same six-month cycle and by the same unanimity rule as the sectoral package. The claim "
  "is about the LEGAL FORM of the measure on a date, which is documentary, not about the policy.",
  "This is the node that explains why the reparations-loan argument exists at all: an asset held "
  "under a renewable measure cannot safely be pledged against a multi-decade liability, and that "
  "is a legal-structure fact, not an opinion. SOFT part: the Commission has floated moving the "
  "measure to a qualified-majority legal basis, which would change the renewal arithmetic; a "
  "PROPOSAL to do so is not an adopted act, which is the #72 distinction exactly.",
  "Renewable immobilisation is a different collateral than permanent seizure; the difference is "
  "the entire financing argument.")

N("ru-reparations-principal-held", "ru-asset-immobilisation-clock",
  "No principal of immobilised Russian sovereign reserves is transferred outright to Ukraine "
  "before 2028-01-01", 0.82, "2027-12-31", "russia-ukraine", "invariant", "15 months",
  "PROCESS ARITHMETIC: an outright transfer of principal requires, in sequence, a new EU legal "
  "basis, compatibility with the depositary jurisdiction's own property and banking law, and a "
  "defence against sovereign-immunity and expropriation claims — each a separate act with its own "
  "statutory and judicial timetable. The binding constraint is the SEQUENCE, not the will: the "
  "steps cannot be run in parallel because each is a precondition for the next.",
  "Priced in the low 0.80s rather than higher because the sequence can be short-circuited by a "
  "political decision to accept litigation risk, and that is a discretionary choice — the class "
  "this book loses on. Written as the npt-notice shape: the claim is that the PROCESS cannot "
  "complete inside the window, not that nobody wants it to. SOFT part: a 'reparations loan' "
  "structure that pledges future profits rather than principal would leave this node HIT while "
  "looking to a headline reader like a MISS, so the resolution source must specify principal.",
  "Principal versus profits is the whole distinction for Euroclear, Belgian sovereign risk and "
  "the euro's reserve-currency argument.")

N("ru-windfall-profit-arithmetic", "ru-asset-immobilisation-clock",
  "The immobilised-asset contribution stream stays mechanically bounded by interest actually "
  "earned through 2027", 0.93, "2027-12-31", "russia-ukraine", "invariant", "15 months",
  "ARITHMETIC IDENTITY: the contribution derived from immobilised reserves is the interest "
  "actually earned on the cash balances, net of the depositary's costs and taxes. It is therefore "
  "the product of a known stock and the prevailing policy rate on that currency, and it cannot "
  "exceed what was earned. If the deposit rate falls, the stream falls proportionally — not as a "
  "forecast but as a definition.",
  "An arithmetic-identity row, the cheapest kind of correct node. Its value is as a falsifier for "
  "every reconstruction-financing plan sized off the current rate environment: the funding "
  "capacity of this channel is a rate derivative, which means a cutting cycle shrinks Ukraine's "
  "non-budgetary financing mechanically. SOFT part: the cost-and-tax wedge the depositary "
  "retains, which is set by national law and has been litigated, and whether a future instrument "
  "capitalises the stream rather than paying it out.",
  "Reconstruction financing sized off the windfall is implicitly long euro rates; a cutting cycle "
  "is a funding shock.")

N("ru-icc-warrants-no-expiry", "ru-anchor",
  "Outstanding ICC arrest warrants in the Ukraine situation remain legally in force on 2029-01-01",
  0.95, "2029-01-01", "russia-ukraine", "invariant", "2+ years",
  "TREATY TEXT: Article 29 of the Rome Statute provides that the crimes within the Court's "
  "jurisdiction are not subject to any statute of limitations, and a warrant issued by a "
  "Pre-Trial Chamber remains in force until executed or withdrawn by the Chamber itself. There is "
  "no lapse mechanism and no renewal requirement — persistence is the default state written into "
  "the treaty.",
  "The purest npt-notice shape in this lane: a charged question about accountability becomes a "
  "question about whether an instrument has an expiry clause, and it does not. Note what is NOT "
  "claimed — nothing about execution, surrender, custody or trial, all of which depend on a state "
  "choosing to act. SOFT part: a Chamber can withdraw a warrant, and an Article 16 Security "
  "Council deferral can suspend proceedings for twelve months at a time, which is the one dated "
  "mechanism that could bite. Far-field by design: the tree has four nodes in 2029.",
  "Legal persistence by default is what keeps sanctions-adjacent counterparty risk priced into "
  "Russian-linked settlement years after any ceasefire.",
  evidence=[{"fact": "Rome Statute Article 29: crimes within the Court's jurisdiction are not "
                     "subject to any statute of limitations", "reported": "structural"}])

N("ru-echr-residual-jurisdiction", "ru-anchor",
  "The European Court of Human Rights still issues judgments against Russia on pre-cessation "
  "facts in 2028", 0.90, "2028-12-31", "russia-ukraine", "invariant", "2 years",
  "TREATY ARITHMETIC: denunciation of the Convention takes effect six months after notification "
  "under Article 58, and the same article expressly preserves the Court's jurisdiction over acts "
  "that occurred BEFORE the denunciation took effect. Russia therefore has a fixed cessation date "
  "computed off its notice, and an open-ended residual docket of applications concerning facts "
  "before it. Jurisdiction over that docket is treaty text, not discretion.",
  "Deliberately written on the RULE rather than the date: the basis names the six-month notice "
  "arithmetic and the Article 58 carve-out instead of quoting a cessation date I would be "
  "guessing at. The claim then needs only that the residual docket outlives the horizon, which "
  "follows from the Court's published backlog. SOFT part: enforcement and payment, which are "
  "nil — this is a judgment-production claim, not a compliance claim, and anyone reading it as "
  "the latter has the premise wrong.",
  "A live judgment stream is the legal substrate under every future claims-commission or "
  "reparations vehicle.")

N("ru-unsc-veto-arithmetic", "ru-anchor",
  "No Chapter VII enforcement resolution concerning Ukraine is adopted by the Security Council "
  "before 2029-01-01", 0.96, "2029-01-01", "russia-ukraine", "invariant", "2+ years",
  "CHARTER ARITHMETIC: Article 27(3) of the UN Charter requires the concurring votes of the "
  "permanent members for all non-procedural decisions. Russia is a permanent member and is the "
  "party any enforcement measure would bind. The arithmetic is therefore closed: the vote cannot "
  "pass, and the only route around it — a Charter amendment under Article 108 — itself requires "
  "ratification by all five permanent members.",
  "The single highest-confidence row in this buildout and the clearest example of the discipline "
  "the lane is built on: a question that reads as geopolitics ('will the UN act?') is a counting "
  "problem with a locked answer. SOFT part: nothing in the mechanism, but the DEFINITION of "
  "'concerning Ukraine' must be tight — procedural votes, Uniting-for-Peace referrals to the "
  "General Assembly and humanitarian resolutions that Russia chooses to let pass are all outside "
  "the claim, and a loose resolution source would score this wrongly.",
  "Security Council paralysis is why every actual enforcement instrument in this conflict is "
  "national or EU law, which is where the tradable legal risk lives.",
  evidence=[{"fact": "UN Charter Article 27(3) requires the concurring votes of the permanent "
                     "members for non-procedural Security Council decisions",
             "reported": "structural"}])

N("ru-osce-ministerial-2027", "ru-anchor",
  "An OSCE Ministerial Council is convened on its annual December cycle in 2027", 0.90,
  "2027-12-03", "russia-ukraine", "scheduled", "14 months",
  "PUBLISHED INSTITUTIONAL CALENDAR PLUS A CONSENSUS RULE: the OSCE holds a Ministerial Council "
  "once a year, normally in the host chair's December slot, and the chairmanship rotates annually "
  "by consensus of all participating states. The MEETING is calendared; the chairmanship "
  "succession and every substantive decision require consensus among fifty-seven states "
  "including Russia, which is why the organisation has repeatedly reached its own deadlines "
  "without agreed outcomes.",
  "Scheduled class on the event only, and a good illustration of why that restraint pays: the "
  "OSCE's recent record is of meetings that CONVENE and decide nothing, so a node on the outcome "
  "would be a coin flip while a node on the calendar is near-certain. Dated to early December as "
  "the cycle's normal slot, with the basis stating the cycle rather than a confirmed date. SOFT "
  "part: the host and therefore the exact dates, which the incoming chair sets.",
  "The only remaining pan-European forum that includes Russia; its calendar is the de-escalation "
  "optionality nobody prices.")

N("ru-ukraine-facility-term-end", "ru-anchor",
  "A successor or bridging instrument covering Ukraine financing past the current instrument's "
  "expiry is adopted before 2027-12-31", 0.45, "2027-12-31", "russia-ukraine", "marker", "15 months",
  "The clock itself is regulation text: the instrument has a fixed term tied to the current "
  "multi-annual financial framework and expires by its own terms. What is NOT structural is the "
  "replacement — a successor must be adopted as a new legal act inside the NEXT framework "
  "(unanimity in Council plus European Parliament consent, a procedure whose historical duration "
  "runs to years), while a bridging act under the existing framework's flexibility provisions is "
  "much faster. Reference class: EU budgetary bridging acts adopted against a hard expiry.",
  "A MARKER on the ADOPTION of an instrument, priced at a coin, and re-expressed from a 0.84 "
  "invariant during the self-check: the original row claimed the instrument reaches expiry with "
  "no successor in force while its own rationale conceded that a bridging act was the most likely "
  "path — a self-contradiction of the exact R28 shape (#26 vs #32), where the node hedges against "
  "itself and the price is doing no work. The honest statement is that the EXPIRY is arithmetic "
  "and the REPLACEMENT is twenty-seven discretionary choices, so the expiry is logged in the MFF "
  "row below and the replacement is logged here, at 0.45, as a coin. SOFT part: all of it.",
  "A financing cliff with a slower replacement procedure behind it is the real Ukraine credit "
  "event, and the cliff date is knowable even when the bridge is not.")

N("ru-mff-2028-rollover-rule", "ru-ukraine-facility-term-end",
  "The 2028 EU budget year opens either under an adopted new framework or under the Treaty's "
  "rollover rule", 0.96, "2028-01-01", "russia-ukraine", "invariant", "15 months",
  "TREATY TEXT COVERS BOTH BRANCHES: Article 312 TFEU requires a multi-annual financial framework "
  "of at least five years and provides that if no new framework has been adopted when the current "
  "one expires, the ceilings of its final year are extended until a new one is adopted. So the "
  "budget cannot simply stop — the treaty supplies the fallback. The claim is the DISJUNCTION, "
  "which is exhaustive by construction.",
  "This is the shape worth copying: instead of forecasting whether twenty-seven governments agree "
  "a framework on time — a conjunction of discretionary choices, the exact #63 error — the node "
  "claims the treaty's own exhaustive disjunction, which has no failure mode short of treaty "
  "breach. It also dates precisely the constraint that governs the Ukraine successor instrument "
  "above. SOFT part: which branch obtains, which is not claimed; and the fact that the rollover "
  "branch would freeze NEW instruments while continuing old ones.",
  "Rollover-versus-adoption decides whether 2028 European fiscal capacity is frozen at 2027 "
  "ceilings, which is a real spread trade on peripheral sovereigns.",
  evidence=[{"fact": "Article 312 TFEU extends the final-year ceilings of an expiring financial "
                     "framework until a new one is adopted", "reported": "structural"}])

N("ru-tanker-replacement-locked", "ru-anchor",
  "The 2028 replacement rate for the sanctioned-trade tanker fleet is already fixed by today's "
  "shipyard orderbook", 0.88, "2028-06-30", "russia-ukraine", "invariant", "20 months",
  "ORDERBOOK LEAD TIME: a crude tanker ordered today delivers against a berth slot booked years "
  "out, because large-hull capacity is a finite physical queue and the yards capable of building "
  "VLCC and Aframax tonnage are few and fully scheduled. The tonnage that can be delivered into "
  "2028 is therefore already in the orderbook; no amount of demand creates a 2028 delivery slot "
  "that does not exist, and vessel age rises monotonically in the meantime.",
  "A queue-and-lead-time invariant of exactly the kind this book is 8-for-8 on. The claim is "
  "about the CEILING on replacement, not about the fleet's size, utilisation or insurance status. "
  "SOFT part: the secondhand market can move existing tonnage between trades instantly, so the "
  "sanctioned fleet's SIZE is not constrained by the orderbook even though its average age and "
  "replacement rate are. A node claiming the fleet cannot grow would be wrong; this one does not.",
  "An ageing, non-replaceable shadow fleet is a slow-burning tail risk for insurance, straits "
  "transit and crude freight rates.")

N("ru-monitoring-mandate-marker", "ru-anchor",
  "A formal published monitoring-mission mandate document for a Ukraine ceasefire appears before "
  "mid-2027", 0.22, "2027-06-30", "russia-ukraine", "marker", "9 months",
  "Reference class: internationally mandated ceasefire monitoring missions require a mandating "
  "instrument — a Security Council resolution, an OSCE Permanent Council decision or a treaty "
  "annex — each of which needs consensus including the party to be monitored. The base rate of "
  "such an instrument appearing inside any given nine-month window of an active interstate war is "
  "very low, and the Security Council route is closed by the veto arithmetic logged above.",
  "A MARKER on the APPEARANCE of a document, which is the only honest way to hold a ceasefire "
  "node in this book: the engine went 0-for-8 extrapolating legs of the Iran war in both "
  "directions, and a monitoring mandate is a thing that either exists on paper or does not. "
  "Priced low and logged anyway, because a book with no genuine negatives earns no resolution — "
  "the 9/20 research measured resolution at ~0.00 and traced it to every row sitting between 0.40 "
  "and 0.88. SOFT part: all of it. This is a 0.22 row, not a forecast I would defend.",
  "A mandate document is the first hard, verifiable artefact of any real de-escalation; headlines "
  "are not.")

# ══════════════════════════════════════════════════════════════════════════════
# LANE: regulation-legal (14)
#   Court and agency calendars. Every node prices the CLOCK — a filing period, a
#   waiting period, a layover, a mandate interval, a sunset — and not one prices a
#   verdict, a grant, a rule's content or an agency's intent.
# ══════════════════════════════════════════════════════════════════════════════
N("rl-anchor", "now", "Regulation & legal: price the clock, never the verdict", 1.0, "2026-10-02",
  "regulation-legal", "invariant", "structural",
  "Definitional: p=1.0 because a lane anchor is a label, not a claim about the world. The lane "
  "exists because litigation and rulemaking run on statutory clocks that are published, "
  "computable and indifferent to the merits.",
  "Lane anchor. The doctrine for every child row: a court's CALENDAR is arithmetic and a court's "
  "HOLDING is a discretionary human judgment. The book's record says to buy the first and refuse "
  "the second. Existing nodes like scotus-term-2026 and tariff-legal-challenge price outcomes; "
  "these price timetables, and the two should resolve independently.",
  "Timetables, not holdings, are what let an event-driven position be sized and dated.")

N("rl-scotus-ot2028-opens", "rl-anchor",
  "The Supreme Court's 2028 Term begins on the first Monday in October 2028 (2028-10-02)", 0.96,
  "2028-10-02", "regulation-legal", "scheduled", "2 years",
  "STATUTORY DATE: 28 U.S.C. §2 fixes the Court's term to begin on the first Monday in October "
  "and to continue until the next term begins. Applying the formula to October 2028 gives the 2nd "
  "(computed). The Court has no discretion over the opening date; changing it takes an Act of "
  "Congress, and the statute has produced an unbroken series since 1917.",
  "Scheduled class and about as clean as the lane gets: a statutory formula, a computed weekday "
  "and an unbroken institutional record. Its real use is as the denominator for every other "
  "timing row in this lane — a case that misses the OT2028 argument calendar cannot be decided "
  "before OT2029. SOFT part: nothing in the date. The argument calendar INSIDE the term is set by "
  "the Clerk and is not claimed.",
  "Term boundaries bound how long a regulatory question can stay legally unresolved, which is "
  "what option tenor should match.")

N("rl-cert-clock-arithmetic", "rl-scotus-ot2028-opens",
  "A judgment entered after mid-2028 cannot be decided on the merits by the Supreme Court within "
  "that Term", 0.92, "2028-10-01", "regulation-legal", "invariant", "2 years",
  "FILING-CLOCK ARITHMETIC: a petition for certiorari is due within ninety days of entry of "
  "judgment under 28 U.S.C. §2101(c), the respondent then has a thirty-day brief in opposition "
  "period under the Court's Rule 15, distribution and conference follow, and a granted case needs "
  "a merits briefing schedule and an argument slot before it can be decided. Summing the minimum "
  "statutory and rule-based intervals — not any court's pace — exceeds the remaining Term.",
  "This is the npt-notice-arithmetic shape transplanted into litigation: a charged question "
  "('will the Court decide X this year?') becomes a sum of filing periods. It is the single most "
  "useful node in this lane because it kills a whole family of bad trades — positions sized for a "
  "ruling that is arithmetically impossible inside the horizon. SOFT part: the Court can expedite "
  "and has, granting certiorari before judgment and compressing briefing to days in genuine "
  "emergencies, which is the one escape hatch and the reason this is 0.92 and not 0.98.",
  "Most 'the courts will settle this by year-end' trades are refuted by the filing calendar alone.",
  evidence=[{"fact": "28 U.S.C. §2101(c) requires a certiorari petition in a civil case within "
                     "ninety days of entry of judgment", "reported": "structural"}])

N("rl-term-disposal-rule", "rl-scotus-ot2028-opens",
  "Every case argued in a Supreme Court Term is disposed of before that Term ends", 0.91,
  "2029-07-01", "regulation-legal", "invariant", "2+ years",
  "INSTITUTIONAL RECORD AS A REFERENCE CLASS: the Court's practice is to decide or otherwise "
  "dispose of every argued case within the Term in which it was argued, with the rare exception "
  "handled by setting the case for re-argument in the following Term rather than by holding it "
  "undecided. The constraint is the Term structure in 28 U.S.C. §2 plus an institutional record "
  "with essentially no counterexamples in the modern era.",
  "A reference-class row rather than a statutory one, and priced accordingly — the Term structure "
  "makes carrying a case over procedurally awkward but not illegal. Its value is that it converts "
  "'when will we know?' into a hard outer bound: whatever is argued is answered by the end of "
  "June or early July. SOFT part: re-argument is the documented escape, and a re-argued case "
  "resolves this node HIT while leaving the underlying question open for another year — a "
  "resolution source must treat re-argument as disposal or the node is ambiguous.",
  "An outer bound on decision timing is what makes June a structurally crowded event window "
  "every year.")

N("rl-hsr-second-request-clock", "rl-anchor",
  "A merger that draws a Second Request cannot lawfully close inside thirty days of certifying "
  "substantial compliance", 0.93, "2027-06-30", "regulation-legal", "invariant", "9 months",
  "STATUTORY WAITING PERIOD: the Hart-Scott-Rodino Act bars consummation during an initial "
  "thirty-day waiting period, and a request for additional information extends it so that a "
  "further thirty-day period runs from the date the parties certify substantial compliance. The "
  "clock is statutory and runs regardless of the agency's view of the deal; only the parties' "
  "compliance date, not the length of the period, is variable.",
  "Pure clock arithmetic and a direct answer to the way merger-arb spreads misprice timing. The "
  "node says nothing about whether a deal is challenged, cleared or abandoned — it says the "
  "EARLIEST lawful closing date is computable from a certification date. SOFT part: timing "
  "agreements routinely extend the period by consent, and pull-and-refile resets the initial "
  "period, so the statutory floor is a floor and not an estimate.",
  "The floor on closing dates is what sets the carry on every arb position with a Second Request.",
  evidence=[{"fact": "The HSR Act provides a further thirty-day waiting period running from "
                     "certification of substantial compliance with a second request",
             "reported": "structural"}])

N("rl-cra-60day-layover", "rl-anchor",
  "A major rule published after late 2027 cannot take effect sooner than sixty days after "
  "publication", 0.94, "2027-12-31", "regulation-legal", "invariant", "15 months",
  "STATUTORY LAYOVER: the Congressional Review Act requires an agency to submit a rule to both "
  "chambers and the Comptroller General before it takes effect, and a MAJOR rule's effective date "
  "cannot be earlier than sixty calendar days after publication in the Federal Register or "
  "submission to Congress, whichever is later. The layover is a statutory precondition to "
  "effectiveness, not a courtesy.",
  "Clock class. The constraint binds the AGENCY, which makes it an invariant rather than a "
  "forecast about anyone's behaviour: a rule that takes effect early is simply unlawful and "
  "vulnerable on that ground alone. SOFT part: the good-cause and emergency exceptions in the "
  "statute, which agencies invoke and which courts sometimes accept, and the separate question of "
  "whether a rule is 'major' — a determination the Office of Management and Budget makes and that "
  "can be contested.",
  "Sixty days between publication and effect is a tradable window for every compliance-cost "
  "repricing.")

N("rl-cra-lookback-2029", "rl-cra-60day-layover",
  "Rules finalised inside the end-of-session lookback window are exposed to disapproval by the "
  "Congress seated in January 2029", 0.88, "2029-01-03", "regulation-legal", "invariant", "2+ years",
  "STATUTORY LOOKBACK PLUS A CONSTITUTIONAL DATE: the Congressional Review Act provides that "
  "rules submitted within a defined number of session days before a session ends are treated, for "
  "the purpose of the disapproval clock, as having been submitted on a specified day of the next "
  "session — which revives the privileged disapproval procedure for the incoming Congress. The "
  "new Congress convenes on January 3 under the Twentieth Amendment, computed as a Wednesday for "
  "2029.",
  "A composite clock row: a statutory lookback window times a constitutional convening date, "
  "neither of which depends on anyone's intent. The EXPOSURE is the claim, not the use of it — "
  "whether a resolution is actually passed and signed is three discretionary choices stacked, "
  "which is the #63 conjunction error and is not priced. SOFT part: the lookback is counted in "
  "SESSION days, not calendar days, so the cut-off date is only knowable once the congressional "
  "calendar is set, which is why the node claims the exposure rather than a date.",
  "Late-cycle rulemaking carries a built-in reversal option; its premium belongs in 2029 "
  "compliance-cost pricing.")

N("rl-fy2029-oct1", "rl-anchor",
  "The federal fiscal year 2029 begins on 2028-10-01 and requires enacted appropriations or a "
  "continuing resolution", 0.97, "2028-10-01", "regulation-legal", "scheduled", "2 years",
  "STATUTORY DATE: 31 U.S.C. §1102 fixes the fiscal year as beginning on October 1. The "
  "Antideficiency Act then makes obligation without an appropriation unlawful, so at the stroke "
  "of the new fiscal year every account either has enacted budget authority, has a continuing "
  "resolution, or lapses. The date is statutory and the trilemma is exhaustive by construction.",
  "Scheduled class, and like the MFF rollover node this one is written as an EXHAUSTIVE "
  "disjunction so it does not require forecasting a congressional choice. That is the correction "
  "for the whole family of shutdown rows that price a negotiation: the date is certain, the "
  "branch is not, and only the date is logged. SOFT part: which branch obtains. Deliberately "
  "placed in 2028, where the tree is thin.",
  "October 1 is the only genuinely pre-dated US fiscal risk event, every year, for as long as the "
  "statute stands.")

N("rl-wto-ab-consensus", "rl-anchor",
  "No Appellate Body division hears a WTO appeal before 2028-01-01", 0.90, "2028-01-01",
  "regulation-legal", "invariant", "15 months",
  "APPOINTMENT ARITHMETIC: Appellate Body members are appointed by the Dispute Settlement Body, "
  "which decides by consensus, so a single member's sustained objection prevents any appointment. "
  "The Working Procedures require a division of three to hear an appeal. With the membership "
  "exhausted and appointments blocked, the quorum arithmetic — not anyone's view of the merits — "
  "closes the Body.",
  "Consensus-rule arithmetic, the same closed-counting shape as the Security Council veto node. "
  "The useful property is that restoring the Body requires an affirmative consensus, which is "
  "much harder to produce than the blockage is to maintain, so the asymmetry favours persistence. "
  "SOFT part: the interim appeal-arbitration arrangement under Article 25 of the DSU continues to "
  "issue awards and a loose resolution source could score one of those as an 'appeal heard', so "
  "the node must be read as referring to the Appellate Body proper.",
  "A permanently closed appellate stage means trade-remedy risk resolves politically, not "
  "judicially — which changes who bears tariff uncertainty.")

N("rl-ect-sunset-2030", "rl-anchor",
  "Energy Charter Treaty sunset protection still covers pre-withdrawal investments on 2030-01-01",
  0.92, "2030-01-01", "regulation-legal", "invariant", "3+ years",
  "TREATY TEXT, TWO CLOCKS: Article 47 of the Energy Charter Treaty provides that a withdrawal "
  "takes effect one year after written notice, and that the treaty's investment protections "
  "continue to apply to investments made before that effective date for a further twenty years. "
  "So a withdrawing party's exposure does not end with withdrawal — it ends two decades later, by "
  "the treaty's own terms.",
  "The best far-field node in this lane and the clearest npt-notice relative: a question that "
  "reads as energy politics ('has Europe left the ECT?') is answered by two numbers written in "
  "the treaty, one year and twenty years. A party can have withdrawn and still be fully exposed, "
  "which is precisely the kind of distinction the engine's premise-liveness rule exists to catch. "
  "SOFT part: an inter se agreement among withdrawing parties can disapply the sunset BETWEEN "
  "them, so the node is about investor claims generally, not about intra-EU disputes where a "
  "separate line of reasoning already applies. Dated 2030, where the tree has four nodes.",
  "Twenty-year sunset protection is the real duration of regulatory risk in European energy "
  "assets, and it is far longer than anyone's investment horizon.",
  evidence=[{"fact": "Energy Charter Treaty Article 47: withdrawal takes effect one year after "
                     "notice, and investments made before that date remain protected for twenty "
                     "further years", "reported": "structural"}])

N("rl-pte-14-year-cap", "rl-anchor",
  "No US patent term extension pushes effective exclusivity beyond fourteen years from drug "
  "approval", 0.94, "2029-01-01", "regulation-legal", "invariant", "2+ years",
  "STATUTORY CAP: 35 U.S.C. §156 restores patent term lost to regulatory review but caps the "
  "restoration at five years and separately caps the total remaining term at fourteen years from "
  "the date of approval of the product. Both caps are in the statute. An exclusivity cliff is "
  "therefore computable from an approval date and a filing date — arithmetic, not a forecast.",
  "An invariant that converts a whole category of pharma questions into subtraction. The caps do "
  "the work, and they bind the Patent Office rather than depending on anyone's behaviour. SOFT "
  "part: effective exclusivity is not the same as the extended patent — regulatory exclusivities, "
  "pediatric extensions, orphan designations, formulation and method-of-use patents and "
  "settlement terms all sit on top, so a node claiming 'generic entry by date X' would be wrong "
  "while this one, about the §156 term cap, is right. Keeping those distinct is the whole point.",
  "The cap is what makes a biosimilar or generic cliff a datable event rather than a litigation "
  "guess.")

N("rl-appellate-median-clock", "rl-anchor",
  "A federal appeal noticed in late 2027 is not decided within nine months of the notice", 0.85,
  "2027-12-31", "regulation-legal", "invariant", "15 months",
  "PUBLISHED STATISTICS AS A REFERENCE CLASS: the federal judiciary publishes median time "
  "intervals from notice of appeal to disposition for the courts of appeals, and the medians run "
  "comfortably above nine months in every circuit, before counting the briefing extensions that "
  "are granted as a matter of course. The claim is a reference-class timing claim, not a view on "
  "any panel.",
  "Price the clock, never the verdict — stated as literally as the lane allows. The node is "
  "useful mainly as a refutation device: 'the appeal will be resolved by spring' is, for a median "
  "case, arithmetically unlikely. SOFT part: expedited and emergency appeals, interlocutory "
  "stay practice and summary dispositions all run far faster than the median, so this node is "
  "about the ORDINARY path and would resolve MISS on any case the court chose to accelerate. "
  "That is the honest exposure and it is why the price is 0.85 rather than 0.93.",
  "Appeal duration is the carry cost of every litigation-overhang discount in a single name.")

N("rl-frap41-mandate-floor", "rl-anchor",
  "No court of appeals mandate issues sooner than the FRAP 41 interval after judgment, absent a "
  "court order", 0.94, "2028-06-30", "regulation-legal", "invariant", "20 months",
  "RULE ARITHMETIC: Federal Rule of Appellate Procedure 41 provides that the mandate issues seven "
  "days after the time to file a petition for rehearing expires, or seven days after entry of an "
  "order denying a timely petition, whichever is later. The rehearing period is itself fixed by "
  "rule. So the earliest date a judgment becomes operative is a sum of two rule-set intervals, "
  "computable the day judgment is entered.",
  "The most mechanical row in the lane: a judgment is not an effect, and the gap between them is "
  "a rule-set number of days. This is the litigation version of 'a bill tabled is not a notice "
  "filed' — a decision ANNOUNCED is not a mandate ISSUED, and positions that treat the two as the "
  "same date are mispriced by weeks. SOFT part: the rule expressly lets the court shorten or "
  "expedite the mandate by order, and in high-salience cases it does, so this is a floor that the "
  "court itself can lower.",
  "Weeks between an announced ruling and an operative one is enough time for a whole position to "
  "be rebuilt.")

N("rl-aiact-delay-marker", "rl-anchor",
  "An amending regulation delaying the EU AI Act's staged application dates is published in the "
  "Official Journal before the next tranche applies", 0.42, "2027-08-02", "regulation-legal",
  "marker", "10 months",
  "The Act's application dates are fixed in its own final article as offsets from entry into "
  "force — six, twelve, twenty-four and thirty-six months — so they are self-executing and no "
  "agency can defer them. Moving one requires an amending regulation through the ordinary "
  "legislative procedure: Commission proposal, European Parliament and Council. The reference "
  "class is 'OLP files completed inside a year', which is a minority of files.",
  "A MARKER on the appearance of a published amending act, priced below even money. The "
  "structural asymmetry is real — the deadlines bind automatically and the only override is a "
  "slow procedure — but the EU has demonstrably fast-tracked targeted amendments when industry "
  "pressure and a deadline coincided, so this is not a row to hold at 0.20 either. SOFT part: "
  "everything about the legislative appetite. Note the premise discipline: a Commission "
  "announcement of intent to simplify is NOT a published amending regulation, which is the #72 "
  "plan-is-not-an-action distinction and the thing a headline reader would get wrong.",
  "Whether the compliance deadline is real decides a year of European enterprise software spend.")

# ══════════════════════════════════════════════════════════════════════════════
# LANE: africa-frontier (12)
#   IMF program review calendars, eurobond amortisation, AfCFTA deadlines,
#   concession terms, restructuring process sequence. Every node is a published
#   calendar or a contractual schedule; none forecasts a government's choice.
# ══════════════════════════════════════════════════════════════════════════════
N("af-anchor", "now", "Africa & frontier: calendars, schedules and sequences", 1.0, "2026-10-02",
  "africa-frontier", "invariant", "structural",
  "Definitional: p=1.0 because a lane anchor is a label, not a claim about the world. The lane is "
  "tractable because frontier sovereign risk is largely governed by published documents — program "
  "schedules, amortisation tables, treaty annexes and concession terms — rather than by "
  "announcements.",
  "Lane anchor. The organising insight: a frontier credit's cash-flow calendar for the next three "
  "years is already written down in bond indentures and Fund program documents, and those are the "
  "forecastable objects. Whether a government MEETS a target is a choice; when the payment falls "
  "due is a contract. Every child row below prices the second kind.",
  "Frontier spreads trade on calendar events that are knowable years ahead and routinely "
  "mispriced as surprises.")

N("af-imf-review-conditionality", "af-anchor",
  "Disbursements under upper-credit-tranche IMF arrangements remain conditioned on board "
  "completion of a scheduled review, not on calendar time", 0.93, "2027-06-30", "africa-frontier",
  "invariant", "9 months",
  "PROGRAM-DOCUMENT STRUCTURE: every extended or credit-facility arrangement is approved with a "
  "schedule of reviews, each tied to performance criteria assessed at a named test date, and the "
  "associated tranche becomes available only when the Executive Board completes that review. The "
  "conditionality architecture is institutional, written into the arrangement itself, and "
  "identical in form across countries.",
  "An institutional invariant about the MECHANISM, which is why it can be stated without naming a "
  "country or a date — and that is deliberate, because naming a specific review board date I was "
  "not certain of would be inventing a fact. Its value is as the correction for the commonest "
  "frontier error: treating a program as a funding stream when it is a sequence of conditional "
  "gates. SOFT part: waivers of non-observance, rephasings and augmentations are all available "
  "and routinely granted, so a missed target is not a stopped program.",
  "Program money is gated, not scheduled; frontier curves that price it as an annuity are wrong.")

N("af-article-iv-cadence", "af-anchor",
  "Article IV consultations continue on their twelve-month surveillance cycle through 2027", 0.92,
  "2027-12-31", "africa-frontier", "scheduled", "15 months",
  "PUBLISHED SURVEILLANCE RULE: the Fund's surveillance framework puts members on a standard "
  "twelve-month Article IV consultation cycle, with a defined grace period and a longer cycle "
  "available for a small set of qualifying members. The cadence is an institutional obligation "
  "under the Articles of Agreement rather than a discretionary scheduling choice, and the staff "
  "reports are published on a known lag.",
  "Scheduled class on the cadence only. Article IV reports are the single best regularly "
  "published primary source on a frontier credit's fiscal arithmetic, which makes the CALENDAR "
  "itself tradable information: you know roughly when a hard number lands. SOFT part: publication "
  "requires member consent, which is occasionally withheld, and consultations with members in "
  "arrears or without a functioning government slip well past the cycle.",
  "Knowing when the next audited fiscal number prints is worth more than guessing what it says.")

N("af-maturity-wall-fixed", "af-anchor",
  "The 2028 frontier eurobond amortisation calendar is already fixed by the existing stock of "
  "instruments", 0.95, "2028-12-31", "africa-frontier", "invariant", "2 years",
  "AMORTISATION ARITHMETIC: a bond's principal repayment dates are written into its indenture at "
  "issuance. The aggregate principal falling due in any future year is therefore a known number, "
  "computable today from the outstanding stock, and it can only CHANGE through a buyback, an "
  "exchange, a tender or a default — each of which is an identifiable, documented event rather "
  "than a drift.",
  "An arithmetic invariant with an unusually clean falsifier: the claim is wrong only if "
  "instruments are actively retired or restructured, and both are observable. This is the node "
  "that makes 'the maturity wall' a measurable object rather than a narrative. SOFT part: the "
  "aggregate's LEVEL depends on which issuers are in the index you count, and new issuance into "
  "a 2028 maturity would add to it — so the node claims the calendar is fixed by the EXISTING "
  "stock, not that the 2028 total cannot rise.",
  "A known redemption calendar means refinancing risk is datable; the surprise is always the "
  "price, never the date.")

N("af-debt-service-2028-known", "af-maturity-wall-fixed",
  "A frontier sovereign's 2028 external debt service from instruments already outstanding is "
  "knowable today within rounding", 0.94, "2028-12-31", "africa-frontier", "invariant", "2 years",
  "CONTRACT ARITHMETIC: for a fixed-coupon instrument, every future cash flow is a function of "
  "the principal schedule and the coupon, both set at issuance. Summing across the outstanding "
  "stock gives next year's and 2028's service exactly; floating-rate and concessional tranches "
  "add a rate-dependent term whose sensitivity is itself computable. New borrowing can only ADD "
  "to the total.",
  "The sharpest form of the lane's central claim. Note the one-sided structure, which is what "
  "makes it robust: existing contracts set a FLOOR on 2028 service, and the only thing that "
  "lowers it is a restructuring. That asymmetry is the whole reason distressed frontier credits "
  "trade the way they do. SOFT part: the floating and FX-linked components, and official-sector "
  "lending whose terms are not always public — which is why the claim is 'within rounding' rather "
  "than exact.",
  "A floor on debt service is a floor on required financing, which is the real constraint behind "
  "every frontier reform program.")

N("af-restructured-amortisation-contractual", "af-maturity-wall-fixed",
  "Post-restructuring instruments pay on their documented amortising schedules through 2028", 0.90,
  "2028-12-31", "africa-frontier", "invariant", "2 years",
  "EXCHANGE-DOCUMENT TEXT: a restructuring exchanges old bullet claims for new instruments whose "
  "principal amortises on dates fixed in the exchange memorandum, frequently with step-up coupons "
  "and occasionally with a state-contingent upside clause keyed to a published macro variable. "
  "Those dates and formulas are contractual terms, not policy choices, and they bind from "
  "settlement.",
  "Contract arithmetic. The structurally interesting part is the amortising profile itself: "
  "restructurings replace one large bullet with a ladder, which mechanically smooths the maturity "
  "wall and changes WHEN the next stress point is — a thing that is knowable from the documents "
  "and routinely misread as a general improvement. SOFT part: state-contingent clauses make part "
  "of the cash flow depend on a published variable rather than on a schedule, and a second "
  "restructuring is always available to a sovereign.",
  "Amortising ladders change the shape of frontier refinancing risk, not its existence.")

N("af-common-framework-sequence", "af-anchor",
  "No Common Framework bondholder exchange completes before an official-creditor understanding is "
  "in place", 0.90, "2027-09-30", "africa-frontier", "invariant", "12 months",
  "PROCESS SEQUENCE: the Common Framework requires an IMF-supported program, an official creditor "
  "committee, and comparability of treatment between official and private claims. Comparability "
  "cannot be assessed against an official envelope that does not yet exist, so the official step "
  "is a logical precondition to the private one. The constraint is the ORDER of the steps, which "
  "is institutional, not the willingness of any participant.",
  "A sequence invariant — the shape that makes 'when will the restructuring finish?' tractable "
  "without forecasting any creditor's behaviour. You cannot run the legs in parallel, so the "
  "total duration is at least the sum of the slowest path, and that is arithmetic. SOFT part: "
  "sovereigns have launched consent solicitations and reprofiling exchanges OUTSIDE the Common "
  "Framework entirely, which would satisfy a loose reading of 'bondholder exchange' while leaving "
  "this node's premise intact — the resolution source must specify a Common Framework case.",
  "Sequence, not goodwill, is what sets the duration of a frontier workout and therefore its "
  "recovery discount rate.")

N("af-afcfta-ldc-2030", "af-anchor",
  "AfCFTA tariff phase-down for least-developed State Parties still runs on its annexed schedule "
  "into 2030", 0.88, "2030-01-01", "africa-frontier", "invariant", "3+ years",
  "TREATY ANNEX: the Protocol on Trade in Goods liberalises tariffs on schedules annexed to the "
  "agreement, with a longer phase-down period for least-developed State Parties than for others "
  "and a separate, slower track for a defined share of sensitive lines. The end-points are treaty "
  "text with dated tranches, so the SCHEDULE is an invariant even where implementation lags.",
  "A treaty-schedule row placed deliberately in 2030, where the tree has four nodes. The "
  "discipline is in the wording: the claim is that the SCHEDULE runs, which is a documentary "
  "fact, not that applied tariffs match it — and those are very different things in practice. "
  "SOFT part: implementation is uneven and several State Parties have not yet deposited complete "
  "schedules, so a node claiming actual tariff elimination would be a much weaker row. I am "
  "pricing the calendar, not the compliance.",
  "The schedule, not the rhetoric, is what dates intra-African trade cost reduction for anyone "
  "building supply chains against it.")

N("af-afcfta-roo-completion", "af-afcfta-ldc-2030",
  "Outstanding AfCFTA rules-of-origin annexes for the contested sectors are completed before "
  "mid-2027", 0.35, "2027-06-30", "africa-frontier", "marker", "9 months",
  "Rules of origin for the sectors where regional value chains are genuinely contested — autos "
  "and textiles above all — require agreement among State Parties, and the negotiation has "
  "already run well past its original target without closing those annexes. Reference class: "
  "multilateral technical annexes whose economics are zero-sum between members, which close "
  "slowly or not at all.",
  "A MARKER priced well below even money, and logged precisely because it is a negative. The "
  "asymmetry is structural: a trade agreement's tariff schedule can run on autopilot while the "
  "rules that determine WHICH goods qualify stay open, and the open rules are the binding "
  "constraint on actual trade. SOFT part: all of it — this is a negotiation among sovereigns and "
  "therefore the discretionary-choice class the engine is worst at, which is exactly why it is "
  "stated at 0.35 rather than dressed as an invariant.",
  "Without rules of origin, a tariff schedule does not move a single container; this is the gate "
  "on the whole AfCFTA trade.")

N("af-mineral-stability-clause", "af-anchor",
  "Fiscal terms inside an unexpired mining stability-clause period are not altered without "
  "legislation or consent", 0.88, "2027-12-31", "africa-frontier", "invariant", "15 months",
  "CONCESSION CONTRACT TEXT: mining conventions and licences are granted for fixed terms recorded "
  "in a public cadastre and commonly include a stability clause freezing the fiscal regime for a "
  "stated period. Changing the applicable terms inside that period therefore requires either the "
  "holder's consent or an act of the legislature overriding the contract — each a documented, "
  "observable step with its own procedure.",
  "A contract-term invariant. The claim is about the mechanism of change, not about whether "
  "change comes: a government that legislates over a stability clause resolves this node HIT "
  "while an administrative decree that simply reinterprets a royalty rate resolves it MISS. That "
  "precision is the point — 'resource nationalism' as a theme is unforecastable, while the "
  "question of whether a specific fiscal change passed through a specific instrument is checkable. "
  "SOFT part: the enforceability of stability clauses against a determined sovereign, which "
  "arbitral practice answers unevenly, and the licence-renewal moment, where leverage resets.",
  "Stability-clause expiry dates, not political rhetoric, are the datable risk in frontier mining "
  "assets.")

N("af-ida-replenishment-cycle", "af-anchor",
  "The IDA replenishment cycle continues on its three-year cadence with a negotiation concluding "
  "in 2027", 0.88, "2027-12-31", "africa-frontier", "scheduled", "15 months",
  "INSTITUTIONAL CADENCE: IDA is funded by replenishments negotiated on a standing three-year "
  "cycle, each covering a three-fiscal-year commitment period beginning on the institution's July "
  "1 fiscal-year boundary, and each concluded by a donors' pledging meeting in the final calendar "
  "year of the preceding cycle. The cadence is institutional and has held across every cycle of "
  "the modern facility.",
  "Scheduled class on the CADENCE, with the basis stating the three-year rule rather than quoting "
  "a replenishment number or a confirmed pledging date I am not certain of. Why it matters for "
  "this lane: IDA terms are the cheapest external financing most of these sovereigns can access, "
  "so the replenishment size is the single largest determinant of their non-market funding "
  "envelope for three years at a time. SOFT part: the SIZE, entirely — that is a donor choice and "
  "nothing here prices it.",
  "A three-year concessional envelope set at one meeting is the floor under a dozen frontier "
  "financing programs.")

N("af-au-summit-feb-2028", "af-anchor",
  "An African Union Assembly ordinary session convenes on its annual February cycle in 2028", 0.90,
  "2028-02-28", "africa-frontier", "scheduled", "17 months",
  "CONSTITUTIVE ACT AND RULES OF PROCEDURE: the Assembly of the Union meets in ordinary session "
  "at least once a year, and the established calendar places the ordinary session in February at "
  "the Addis Ababa headquarters, with extraordinary sessions available on request. The annual "
  "ordinary session is an institutional obligation in the founding instrument, not a scheduling "
  "preference.",
  "Scheduled class, dated to a month-end rather than a day because the exact February dates are "
  "set by the Executive Council each cycle and I will not state one as fact. The reason this "
  "belongs in a forecasting tree at all: the Assembly's February slot is when continental "
  "positions on debt architecture, AfCFTA implementation and the Union's own financing get "
  "formalised, so it is a dated clustering point for frontier policy news. SOFT part: the "
  "contents, and the chairship rotation that shapes the agenda.",
  "An annual, dated continental agenda-setting event is a scheduling anchor for frontier policy "
  "risk.")

# ══════════════════════════════════════════════════════════════════════════════
# LANE: india-sa (10)
#   The budget calendar, the MPC's statutory meeting floor, the constitutional
#   delimitation freeze, the roll-revision cycle, and capacity that is already
#   under construction. Nothing here forecasts a rate decision or a target.
# ══════════════════════════════════════════════════════════════════════════════
N("in-anchor", "now", "India & South Asia: the fixed calendar and the committed capacity", 1.0,
  "2026-10-02", "india-sa", "invariant", "structural",
  "Definitional: p=1.0 because a lane anchor is a label, not a claim about the world. India is "
  "unusually tractable for this engine because its fiscal, monetary and electoral calendars are "
  "fixed by statute or long-established practice and its energy capacity additions have "
  "multi-year, contracted lead times.",
  "Lane anchor. Two forecastable objects in this lane: published calendars (the Union Budget, the "
  "MPC's statutory meeting floor, roll revision, the delimitation freeze) and committed capacity "
  "(refineries and renewables already under construction or already auctioned). Nothing below "
  "prices a policy rate, a growth number or a target — the existing india-growth node already "
  "carries that kind of exposure and these should resolve independently of it.",
  "India's calendar density means its risk events are datable a year out, unlike most of EM.")

N("in-budget-feb-2028", "in-anchor",
  "The Union Budget for FY2028-29 is presented to Parliament on or about 2028-02-01", 0.91,
  "2028-02-01", "india-sa", "scheduled", "17 months",
  "CONSTITUTIONAL OBLIGATION PLUS ESTABLISHED PRACTICE — and the two are different, which this "
  "basis states plainly: Article 112 requires an annual financial statement to be laid before "
  "Parliament for every financial year, so the EVENT is constitutionally compelled. The February "
  "1 date is an established practice adopted in 2017 (moved forward from the end of February) and "
  "repeated every year since; it is NOT a statutory date and the government could move it.",
  "Scheduled class, and the honest split is in the basis: the budget's existence is "
  "constitutional, its date is a convention with a near-decade run. I am not pricing it as 0.97 "
  "for that reason. SOFT part: the date, and the fact that an election-year budget is presented as "
  "an interim vote-on-account with the full budget following the new Parliament — which is a real "
  "scenario given the 2029 Lok Sabha deadline logged in the elections lane, though FY2028-29 sits "
  "before it.",
  "The budget is India's single largest scheduled fiscal print; the date sets the rates and "
  "capex-name event window.")

N("in-rbi-mpc-calendar", "in-anchor",
  "The RBI publishes an advance MPC meeting calendar for 2028-29 and holds at least the statutory "
  "minimum number of meetings", 0.94, "2028-06-30", "india-sa", "scheduled", "20 months",
  "STATUTORY FLOOR PLUS A PUBLISHED CALENDAR: the amended RBI Act requires the Monetary Policy "
  "Committee to meet at least four times a year and requires the Bank to publish the meeting "
  "schedule in advance. In practice the Bank publishes a six-meeting bi-monthly calendar for each "
  "fiscal year. The claim is the statutory floor plus the publication obligation, both of which "
  "are in the Act.",
  "Scheduled class, and written against the floor rather than the practice so that it resolves on "
  "the statute: four is the legal minimum and six is the convention, so the node is robust to the "
  "Bank trimming its own cadence. The engine is 12-for-14 on scheduled prints and 0-for-8 on "
  "discretionary decisions, so nothing here says anything about a rate. SOFT part: additional "
  "off-cycle meetings, which the Act permits and which have been convened in stress episodes, "
  "would exceed the claim rather than break it.",
  "A published advance calendar for a 2028 central-bank cycle is the kind of far-dated event "
  "structure that is nearly free to monitor.")

N("in-mpc-external-terms", "in-rbi-mpc-calendar",
  "The external MPC cohort turns over on its statutory four-year non-renewable term in 2028", 0.90,
  "2028-10-31", "india-sa", "invariant", "2 years",
  "STATUTORY TERM: the RBI Act fixes the term of an externally appointed Monetary Policy "
  "Committee member at four years and makes the member ineligible for reappointment. Appointments "
  "are made as a cohort, so the cohort's expiry is a computable date four years from "
  "notification, and the non-renewability means the turnover is mandatory rather than "
  "discretionary.",
  "An institutional invariant with no agency in the turnover itself — only in who replaces whom, "
  "which is not priced. This is the useful shape for central-bank composition questions: the "
  "DATE of a reshuffle is statutory while its CONTENT is a government appointment, and the "
  "engine should only ever buy the first. SOFT part: the exact expiry depends on the notification "
  "date of the sitting cohort, which is why the node is dated to a month-end; and a vacancy "
  "filled late leaves the Committee short of its full strength without breaching the term rule.",
  "A mandated, dated change in the voting composition of a major EM central bank is a real "
  "scheduled risk that nobody prices because it is not a meeting.")

N("in-delimitation-freeze", "in-anchor",
  "No reallocation of Lok Sabha seats among states takes legal effect before 2029-01-01", 0.90,
  "2029-01-01", "india-sa", "invariant", "2+ years",
  "CONSTITUTIONAL TEXT PLUS A TWO-STEP PROCESS: Article 82 requires readjustment of seat "
  "allocation after each census, and the Eighty-fourth and Eighty-seventh Amendments froze the "
  "allocation among states by reference to the first census taken after the year 2026. Lifting "
  "the freeze therefore requires, in sequence, a completed and published census and then a "
  "Delimitation Commission constituted by an Act of Parliament whose order must itself be laid "
  "before the House. Neither step can be skipped and they cannot be run in parallel.",
  "The npt-notice shape applied to the most charged question in Indian federal politics: the "
  "answer is not a prediction about intent, it is a count of sequential legal preconditions and "
  "their minimum durations. A census ANNOUNCED is not a census PUBLISHED, and a commission "
  "CONSTITUTED is not an order IN FORCE — the same distinction that made the NPT row the best in "
  "the last batch. SOFT part: the government controls the pace of every step and could compress "
  "them; and a reallocation WITHIN a state's constituencies is a different exercise that would "
  "not breach this node.",
  "Seat reallocation is the fiscal-federalism tail risk for Indian state credits; its earliest "
  "possible date is a process computation.",
  evidence=[{"fact": "The Indian Constitution's delimitation freeze runs by reference to the first "
                     "census taken after the year 2026", "reported": "structural"}])

N("in-roll-revision-cycle", "in-anchor",
  "Electoral roll revision continues on its published cycle with the statutory qualifying dates "
  "through 2027", 0.90, "2027-01-01", "india-sa", "scheduled", "3 months",
  "STATUTORY CYCLE: the Representation of the People Act, as amended, provides multiple "
  "qualifying dates per year for enrolment rather than a single January 1 cut-off, and the "
  "Election Commission conducts a special summary revision on a published schedule with draft "
  "publication, a claims-and-objections window and final publication. Each stage has a notified "
  "date; the cycle is a statutory administrative process.",
  "Scheduled class on an administrative calendar, included because roll revision is the "
  "upstream constraint on every electoral timetable in the lane — a commission cannot notify a "
  "poll against a roll that has not been finally published. SOFT part: intensive or special "
  "revisions ordered ahead of a state election run on bespoke schedules that override the annual "
  "cycle, and those are discretionary; so the node is about the ORDINARY annual process.",
  "Roll publication dates are the real leading indicator of state election timing, well before "
  "any announcement.")

N("in-refinery-leadtime", "in-anchor",
  "No greenfield Indian refinery beyond those already under construction is commissioned before "
  "2030-01-01", 0.90, "2030-01-01", "india-sa", "invariant", "3+ years",
  "LEAD-TIME ARITHMETIC: a greenfield refinery takes longer than the remaining horizon to go from "
  "final investment decision to mechanical completion — land, environmental clearance, long-lead "
  "equipment with multi-year fabrication slots, construction and commissioning. So the set of "
  "refineries that can be running before 2030 is already closed: it is exactly those under "
  "construction today. The constraint is physical and contractual, not fiscal.",
  "A capacity-and-lead-time invariant, the class the engine is 8-for-8 on, placed in 2030 where "
  "the tree is nearly empty. The structure is what makes it strong: the claim is about a CLOSED "
  "SET, and new announcements cannot enlarge it because they cannot beat the lead time. SOFT "
  "part: brownfield expansions and debottlenecking at existing sites add real capacity on much "
  "shorter timelines and are explicitly outside the claim — which is exactly how most Indian "
  "refining capacity has actually been added, so a careless resolution source would score this "
  "wrongly.",
  "Refining capacity additions are already determined for the rest of the decade; crack spreads "
  "should be priced off the construction list, not the announcement list.")

N("in-renewable-pipeline-bound", "in-anchor",
  "FY2028 Indian renewable capacity additions come overwhelmingly from already-awarded capacity",
  0.90, "2028-03-31", "india-sa", "invariant", "18 months",
  "AUCTION-TO-COMMISSIONING LEAD TIME: utility-scale solar and wind projects are built against a "
  "power purchase agreement awarded in a competitive auction, and the PPA itself specifies a "
  "scheduled commissioning date typically two years or more after signature, with the "
  "transmission connectivity queue adding its own wait. So capacity commissioning in FY2028 was "
  "already auctioned; the pipeline is a contracted backlog, not a forecast.",
  "A backlog invariant — the same shape as the defence-backlog and interconnect-queue nodes this "
  "book already carries. The claim is about the SOURCE of the additions, not their quantity, "
  "which is what keeps it out of level-row territory: I am not claiming a gigawatt number, I am "
  "claiming the additions were already contracted. SOFT part: rooftop and behind-the-meter solar "
  "is built outside the auction pipeline on much shorter timelines and is excluded; and awarded "
  "capacity can be cancelled or delayed, which reduces additions without breaking the source "
  "claim.",
  "The awarded-but-unbuilt backlog, not policy ambition, is the forecastable part of Indian power "
  "capex.")

N("in-gst-supermajority", "in-anchor",
  "No GST rate change takes effect without the Centre's concurrence under the Article 279A voting "
  "rule", 0.95, "2027-12-31", "india-sa", "invariant", "15 months",
  "CONSTITUTIONAL VOTE ARITHMETIC: Article 279A establishes the GST Council and fixes its "
  "decision rule as a three-fourths weighted majority of members present and voting, with the "
  "Union Government's vote weighted at one third of the total and all state votes together "
  "weighted at two thirds. One third exceeds the one quarter needed to block a three-fourths "
  "threshold, so the Centre holds a structural veto. This is counting, not politics.",
  "Closed-counting arithmetic of the same kind as the Security Council veto row, and the "
  "highest-confidence node in this lane for that reason: the constitution hands one party a "
  "blocking stake, so no outcome requiring the Centre's defeat is available. Note what is NOT "
  "claimed — nothing about what rates will be, when they change, or whether the states and the "
  "Centre agree. SOFT part: the Council has in practice decided by consensus rather than by "
  "voting, which means the formal arithmetic is rarely exercised; a change adopted by consensus "
  "still satisfies this node, since consensus includes the Centre.",
  "A constitutional veto on indirect-tax changes is why Indian GST risk is a negotiation, never a "
  "surprise.",
  evidence=[{"fact": "Article 279A weights the Union Government's vote in the GST Council at one "
                     "third of total votes cast, against a three-fourths decision threshold",
             "reported": "structural"}])

N("in-500gw-milestone-marker", "in-anchor",
  "An official Indian statement confirming 500 GW of installed non-fossil generating capacity "
  "appears on or before 2030-12-31", 0.40, "2030-12-31", "india-sa", "marker", "4 years",
  "A stated national target is not a structural constraint. The binding constraints are the "
  "auction-to-commissioning lead time logged above, the transmission connectivity queue and the "
  "storage required to absorb the variable share — none of which is set by the target. Reference "
  "class: national capacity targets with a round number and a round year, which are met late more "
  "often than on time.",
  "A MARKER on the appearance of an official confirmation, priced BELOW even money on purpose and "
  "parked in 2030, the thinnest year in the tree. The whole point of logging it as a marker at "
  "0.40 rather than as an invariant at 0.80 is that a TARGET is a policy aspiration — the exact "
  "class the engine's twelve misses came from — while the queue and the lead time are the real "
  "constraints, and those are already logged separately. SOFT part: everything, including the "
  "definition of non-fossil capacity, which sweeps in large hydro and nuclear and makes the "
  "accounting itself a judgment call. That ambiguity is a second reason not to price it high.",
  "A target is not a forecast; the awarded pipeline is. Anyone sizing Indian renewables capex off "
  "the 500 GW number is pricing an aspiration.")
