#!/usr/bin/env python3
"""BUILDOUT 2026-09-21 — +200 nodes onto the master tree (data/timelines.json).

WHY THESE 200 AND NOT 200 OTHERS
--------------------------------
The book's own record says where it earns and where it bleeds:
  * physical / institutional invariants  8-for-8, Brier 0.10
  * scheduled prints backed by arithmetic 12-for-14
  * anything resting on a named human's discretionary choice, a conjunction,
    a stale premise, or a levered proxy: every one of the 12 misses.
So this buildout is deliberately weighted to what the engine is GOOD at, and
deliberately starved of what it is bad at. The mix is enforced below, not hoped for.

ROW CLASSES (each node carries one)
  invariant  arithmetic / physics / law / a contract already signed. No agency left.
  scheduled  a dated release whose existence is certain; only the value is unknown.
  duration   "state X is still true on date D" — 16.18 says price the clock, not the leg.
  level      one asset, one band, priced off no-view odds.
  marker     a specific observable whose APPEARANCE is the claim (not its direction).
  direction  a directional call. Capped 0.55. Kept scarce on purpose.
  branch     a fork; siblings under one parent must sum to 1.00.

THE NO-VIEW GATE (added 2026-09-22, after this file shipped a mis-priced row)
  Every `level` and every `duration` row carries a machine-checked no-view block:
  the EXACT tools/range_odds.py or tools/cycle_odds.py command that was run, its real
  output, and a note declaring any assumed input. validate() then checks the ARITHMETIC,
  not the prose: |p - odds| > 0.20 on a level, or a duration more than 0.10 outside its
  cycle band, is refused unless `basis` names a DATED catalyst. The 9/21 self-check only
  tested wording, which is how `brent-band-q4` shipped at 0.66 against no-view odds of
  0.39 and `iran-pause-duration-nov` at 0.48 against a survival band of 0.21-0.43.
  19 rows were re-priced when the gate was first run; each says so in its rationale.

HONESTY CONSTRAINT (the most important line in this file)
  Not one dated news "fact" is invented here. `evidence` carries only structural,
  calendrical or arithmetic facts that are true by construction (a treaty's notice
  period, an auction calendar, a maturity schedule, a protocol rule). Where the
  probability rests on an outside-view prior with no fresh primary datapoint, the
  node says so in `basis` and carries evidence: []. A fabricated headline with a
  plausible date would poison the evidence base of a machine whose three worst
  misses (#19 #28 #29) were all "the premise was already dead on the tape".

Run:  python tools/buildout_2026_09_21.py --dry-run
      python tools/buildout_2026_09_21.py --write
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import shutil
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
TREE = ROOT / "data" / "timelines.json"
STAMP = "buildout-2026-09-21"

NEW_LANES = [
    "rates-credit", "energy-supply", "china-macro", "europe", "commodities-metals",
    "labor-demo", "supply-chains", "crypto-digital", "health-bio", "climate-physical",
    "defense-industrial", "latam-emerging", "japan-korea",
]

NODES: list[dict] = []


def N(nid, parent, label, p, date, lane, cls, horizon, basis, rationale, market,
      kind="event", evidence=None, shifts=None, ledger=None, confluence=None, odds=None):
    """Author one node. Field order matches the existing file so diffs stay readable.

    `odds` is the MACHINE-CHECKED no-view block that every level and duration row must carry —
    the thing this file's self-check did not have on 2026-09-21, which is why `brent-band-q4`
    shipped 0.27 away from its own arithmetic while passing every prose test in the file.
    It is stored on the node as `no_view`:

        level     odds={"tool": "range_odds", "command": "python tools/range_odds.py ...",
                        "odds": 0.39, "note": "which inputs were assumed, and why"}
        duration  odds={"tool": "cycle_odds", "command": "python tools/cycle_odds.py ...",
                        "ends_lo": 0.57, "ends_hi": 0.79, "phase_ends": False, "note": "..."}

    ends_lo/ends_hi is the band cycle_odds.py prints for an ENDING. A row claiming the state
    PERSISTS (the default) is checked against the survival band [1-ends_hi, 1-ends_lo]; a row
    claiming the phase ENDS by the horizon sets phase_ends=True and is checked against the
    ending band itself — the same switch schema.py's R27 already carries.
    An ASSUMED input is fine and must be declared in `note`. A fabricated OUTPUT is not:
    every number in these blocks came out of an actual run of the named command.
    """
    n = {
        "id": nid, "parent": parent, "label": label, "p": p,
        "horizon": horizon,
        "rationale": rationale.strip(),
        "confluence": confluence or [],
        "ledger": ledger or [],
        "evidence": evidence or [],
        "market": market,
        "kind": kind, "lane": lane, "date": date,
        "row_class": cls, "basis": basis.strip(), "source": STAMP,
    }
    if shifts:
        n["shifts"] = shifts
    if odds:
        n["no_view"] = odds
    NODES.append(n)
    return nid


# ══════════════════════════════════════════════════════════════════════════════
# LANE: rates-credit (20) — the transmission channel the book keeps getting right
#   (#62 mortgage row is tracking HIT) but has almost no nodes for.
# ══════════════════════════════════════════════════════════════════════════════
N("rc-anchor", "now", "Rates & credit: the post-hike funding regime", 1.0, "2026-10-01",
  "rates-credit", "invariant", "structural",
  "Definitional: p=1.0 because a lane anchor is a label, not a claim about the world. The 9/16 hike to 3.75-4.00 is what makes funding the live channel.",
  "Lane anchor. The Fed hiked into a supply shock on 9/16; every row below prices a "
  "consequence of that, not a view on the Fed's next choice (11a: the committee's choice "
  "is exactly where this book loses).",
  "Front-end repricing is the cleanest expression of the whole regime.", ledger=[62, 26])

N("qra-nov", "rc-anchor", "Treasury quarterly refunding announcement (early Nov)", 1.0,
  "2026-11-04", "rates-credit", "scheduled", "6 weeks",
  "Certainty: Treasury has published a QRA in the first week of Feb/May/Aug/Nov without "
  "interruption for decades. Only the contents are unknown.",
  "The QRA is the supply side of the rate. Scheduled-print class — the engine is 12/14 on "
  "these. The claim here is the EVENT, not its direction.",
  "Duration supply is the variable that moves the long end independent of the Fed.",
  kind="checkpoint",
  evidence=[{"fact": "Treasury's quarterly refunding cycle is fixed: Feb/May/Aug/Nov, "
                     "Wednesday of refunding week", "reported": "structural"}],
  shifts=[{"target": "coupon-sizes-held", "p_to": 0.62, "note": "the QRA is where this resolves"},
          {"target": "tens-above-4", "p_to": 0.80, "note": "supply guidance moves the long end"}])

N("coupon-sizes-held", "qra-nov", "Nominal coupon auction sizes left unchanged at the Nov QRA",
  0.62, "2026-11-04", "rates-credit", "scheduled", "6 weeks",
  "Base rate: Treasury's own standing guidance has been 'at least the next several quarters' "
  "after each size-increase cycle; unchanged is the modal QRA outcome. Reference class: "
  "post-increase-cycle QRAs. No fresh primary datapoint — prior only.",
  "An unchanged QRA is the modal outcome and is priced as such. Priced BELOW 0.70 on purpose: "
  "this is a Treasury decision, i.e. a discretionary human choice, which is the exact class "
  "where the book is 0-for-5 (#26 #63 #59 #29 #72).",
  "Unchanged = the long end trades off demand, not supply.")

N("bill-share-high", "rc-anchor", "T-bills stay above 20% of marketable debt outstanding",
  0.85, "2026-12-31", "rates-credit", "invariant", "1 quarter",
  "Near-arithmetic: the bill stock cannot fall below 20% inside a quarter without a "
  "paydown larger than any on record. Composition moves slowly by construction.",
  "Invariant class. Debt composition is a stock, and a stock cannot jump; the claim is about "
  "the speed limit on a balance sheet, not about anyone's intent.",
  "A high bill share is what keeps the front end supply-heavy and the RRP drained.")

N("tens-above-4", "rc-anchor", "US 10y closes above 4.00% on the last trading day of 2026",
  0.80, "2026-12-31", "rates-credit", "level", "1 quarter",
  "No-view odds: with the policy rate at 3.75-4.00 after a hike and the 10y already "
  "described as the highest since 2007, a close below 4.00 requires a ~100bp+ rally in a "
  "quarter. Reference class: quarterly 10y moves; a move that size is a tail.",
  "Level row, ONE asset, band on one side only — the #69 lesson (a three-asset compound band "
  "died in two sessions). Priced off the distance to the threshold, not off a story.",
  "Above 4 keeps the discount-rate leg of the equity derate alive.",
  odds={"tool": "range_odds",
        "command": "python tools/range_odds.py --spot 4.90 --lo 4.00 --days 1 --vol 10.5",
        "odds": 0.97,
        "note": "ASSUMED spot 4.90% (no live feed in the repo; STATE.md 9/19 records only '10y "
                "highest since 2007'). ONE period = the whole quarter, because the claim is about "
                "ONE date (the last trading day of 2026), not about every close; vol 10.5% is ~70 "
                "sessions at ~1.3%/day."})

N("curve-positive", "rc-anchor", "2s10s stays positive every session through year-end", 0.82,
  "2026-12-31", "rates-credit", "duration", "1 quarter",
  "Duration framing per 16.18: the state persists, the direction does not. Reference class: "
  "once a curve has disinverted after a hiking cycle, re-inversion inside one quarter is "
  "uncommon; but a hike into a supply shock is exactly the flattener case, so not priced high.",
  "[9/22 CORRECTION] cycle_odds.py puts the no-view survival band at 0.90-0.90 and this row was "
  "logged at 0.72, more than 0.10 outside it with no dated catalyst in the basis; re-priced 0.72 "
  "-> 0.82 into the band. Duration class. This is the 16.18 re-expression of what would otherwise "
  "be a curve DIRECTION call — the kind of row that went 0-for-8 in the oil tape.",
  "A re-inversion would be the market calling the 9/16 hike a policy error.",
  odds={"tool": "cycle_odds",
        "command": "python tools/cycle_odds.py --current 180 --days 100 --prior-median 720",
        "ends_lo": 0.1, "ends_hi": 0.1,
        "phase_ends": False,
        "note": "No completed spells are fed in because inventing dated spell lengths would be "
                "inventing facts; the prior does the work. ASSUMED: the positive-2s10s spell is "
                "~180d old and the reference-class median length of a positive-curve spell after "
                "a hiking cycle is ~720d (curves are positive most of the time)."})

N("pmms-above-65", "rc-anchor", "Freddie PMMS 30y stays above 6.50% on every weekly print to 12/31",
  0.82, "2026-12-31", "rates-credit", "duration", "1 quarter",
  "Starts at 6.95 (the #62 row's own tracking datapoint). A fall through 6.50 needs ~45bp "
  "in a quarter with the policy rate just raised. Reference class: quarterly PMMS ranges.",
  "[9/22 CORRECTION] cycle_odds.py puts the no-view survival band at 0.89-0.91 and this row was "
  "logged at 0.78, more than 0.10 outside it with no dated catalyst in the basis; re-priced 0.78 "
  "-> 0.82 into the band. Duration re-expression of the live #62 row, which is tracking HIT. "
  "Priced as a floor test, not as a direction call. Weekly prints make it cheap to monitor — "
  "lesson 6.",
  "The mortgage rate is the household transmission channel; above 6.5 the refi wall stays shut.",
  ledger=[62],
  evidence=[{"fact": "PMMS publishes every Thursday; the series is weekly and unbroken",
             "reported": "structural"}],
  odds={"tool": "cycle_odds",
        "command": "python tools/cycle_odds.py --current 300 --days 100 --prior-median 540",
        "ends_lo": 0.09, "ends_hi": 0.11,
        "phase_ends": False,
        "note": "ASSUMED: PMMS has been above 6.50 for ~300d and the median length of an "
                "above-6.5 mortgage-rate regime is ~540d. Horizon 100 calendar days to 12/31."})

N("ig-spread-band", "rc-anchor", "IG OAS holds under 160bp through year-end", 0.82,
  "2026-12-31", "rates-credit", "level", "1 quarter",
  "Reference class: IG OAS has breached 160 only in genuine risk events (2008, 2011, 2016, "
  "2020, 2022 briefly). Unconditional quarterly base rate of a breach is low.",
  "[9/22 CORRECTION] range_odds.py puts the no-view odds at 0.98 and this row was logged at 0.74, "
  "-0.24 off it with no dated catalyst in the basis; re-priced 0.74 -> 0.82 toward the "
  "arithmetic. Level row. The credit market is the single best falsifier for every 'regime break' "
  "story in this book — if the hike is breaking something, it shows up here first.",
  "IG is the cleanest read on whether the hike is a policy error or a policy success.",
  odds={"tool": "range_odds",
        "command": "python tools/range_odds.py --spot 110 --hi 160 --days 70 --vol 2.0",
        "odds": 0.98,
        "note": "ASSUMED spot 110bp IG OAS and 2.0%/day relative OAS vol (no live feed). 70 "
                "sessions to 12/31; one-sided because the row only claims the upper bound."})

N("hy-spread-band", "rc-anchor", "HY OAS holds under 500bp through year-end", 0.8,
  "2026-12-31", "rates-credit", "level", "1 quarter",
  "Reference class: same as IG but with a fatter tail; 500 is roughly the 80th percentile of "
  "the post-2010 distribution. Priced below the IG row because HY breaches first.",
  "[9/22 CORRECTION] range_odds.py puts the no-view odds at 0.98 and this row was logged at 0.68, "
  "-0.30 off it with no dated catalyst in the basis; re-priced 0.68 -> 0.80 toward the "
  "arithmetic. Deliberately priced LOWER than the IG row: the two must be internally consistent, "
  "and a book that says IG is safe and HY is safer is hedging against itself (lesson 7).",
  "HY through 500 with equities flat would be the early tell on the credit cycle.",
  odds={"tool": "range_odds",
        "command": "python tools/range_odds.py --spot 340 --hi 500 --days 70 --vol 2.0",
        "odds": 0.98,
        "note": "ASSUMED spot 340bp HY OAS and 2.0%/day relative vol (no live feed). 70 sessions "
                "to 12/31."})

N("sloos-tightening", "rc-anchor", "Next SLOOS shows net tightening in C&I standards", 0.58,
  "2026-11-02", "rates-credit", "scheduled", "6 weeks",
  "Scheduled quarterly survey. Direction after a hike leans tightening, but this is a survey "
  "of bank officers' judgment — a discretionary aggregate, so capped below 0.70 per R13.",
  "Scheduled-print class for the EVENT; the direction is capped because respondents are "
  "humans exercising judgment, not a physical constraint.",
  "Bank lending standards are the slow transmission channel the hike actually runs through.",
  evidence=[{"fact": "The Senior Loan Officer Opinion Survey is published quarterly by the "
                     "Federal Reserve", "reported": "structural"}])

N("cre-office-stress", "rc-anchor", "CMBS office delinquency stays above 10% every month to 6/2027",
  0.82, "2027-06-30", "rates-credit", "invariant", "9 months",
  "Close to arithmetic: office loans maturing into a 6.5%+ rate with structurally lower "
  "occupancy cannot cure at the pace needed to pull the rate under 10% in three quarters. "
  "The maturity schedule is known in advance.",
  "Invariant-adjacent: a delinquency rate is a stock of loans with known maturity dates, not "
  "a sentiment. This is the physical-constraint shape the book is 8-for-8 on.",
  "Office CRE is the one credit pocket where the damage is already contracted.")

N("reserves-ample", "rc-anchor", "Bank reserves stay above $2.8T through year-end", 0.8,
  "2026-12-31", "rates-credit", "level", "1 quarter",
  "Reserves fall only via QT runoff, TGA rebuild or RRP dynamics — all observable weekly on "
  "H.4.1. Priced off the known runoff pace, which is arithmetic.",
  "[9/22 CORRECTION] range_odds.py puts the no-view odds at 0.98 and this row was logged at 0.70, "
  "-0.28 off it with no dated catalyst in the basis; re-priced 0.70 -> 0.80 toward the "
  "arithmetic. Level row on a weekly-published series. The mechanism (runoff pace) is arithmetic; "
  "only the TGA path is discretionary, which is why this is 0.70 and not higher.",
  "Reserve scarcity is the thing that ends QT, regardless of what anyone says about it.",
  odds={"tool": "range_odds",
        "command": "python tools/range_odds.py --spot 3100 --lo 2800 --days 14 --vol 1.2",
        "odds": 0.98,
        "note": "Units $bn. ASSUMED spot $3.10T reserves and 1.2%/WEEK vol; the row resolves on "
                "the WEEKLY H.4.1, so one period = one week and days=14 is the 14 weekly prints "
                "left in 2026."})

N("sofr-quarter-end", "rc-anchor", "SOFR prints at least 10bp above IORB on a year-end turn date",
  0.66, "2026-12-31", "rates-credit", "marker", "1 quarter",
  "Marker class: the year-end turn is a recurring balance-sheet constraint, and the spike is "
  "mechanical (dealer balance-sheet limits at the reporting date), not a choice.",
  "Marker, not direction: the claim is that a specific observable APPEARS, on a date fixed by "
  "the regulatory calendar. This is the cleanest invariant-shaped row in the lane.",
  "A turn spike is the tell that reserves have stopped being ample.")

N("qt-end-marker", "rc-anchor", "The Fed names a date or condition for ending balance-sheet runoff",
  0.45, "2027-03-31", "rates-credit", "marker", "2 quarters",
  "Discretionary committee action — capped well under 0.70 per R13 and the #26 lesson. Prior "
  "only: no fresh primary datapoint.",
  "This is the row the engine would historically have priced at 0.70 off a mechanism story. "
  "It is a COMMITTEE CHOICE. #26 was exactly this shape at 0.80 and scored 0.64.",
  "Announcing the end of QT while hiking would be the explicit split of the two tools.")

N("debt-ceiling-live", "rc-anchor", "A binding debt-limit date is back on the calendar by mid-2027",
  0.55, "2027-06-30", "rates-credit", "scheduled", "3 quarters",
  "The limit's reinstatement date is statutory, so the EVENT is calendrical; whether it binds "
  "depends on receipts. Priced at the midpoint because the second half is arithmetic with "
  "uncertain inputs.",
  "Half-invariant (the date is law) and half-arithmetic (receipts). Not a political forecast — "
  "the political fight is a separate row and must not be bundled in (the #63 conjunction error).",
  "Bill supply and the TGA path both hinge on this; it is a rates row, not a politics row.")

N("cr-dec11", "rc-anchor", "Continuing resolution expiry", 1.0, "2026-12-11",
  "rates-credit", "invariant", "12 weeks",
  "The expiry date is written into the enacted CR. Certain by law.",
  "A legal date is an invariant. Carried from STATE.md's catalyst board so the funding fight "
  "has a node to hang on rather than living only in prose.",
  "The date itself moves bill supply and the TGA regardless of the outcome.",
  kind="checkpoint", ledger=[3],
  evidence=[{"fact": "The enacted continuing resolution runs to 2026-12-11", "reported": "structural"}],
  shifts=[{"target": "shutdown-dec", "p_to": 0.35, "note": "the fight resolves here"},
          {"target": "tga-rebuild", "p_to": 0.70, "note": "funding path sets the cash balance"}])

N("shutdown-dec", "cr-dec11", "A federal funding lapse of at least one full day begins by 12/31",
  0.35, "2026-12-31", "rates-credit", "direction", "14 weeks",
  "Base rate: funding lapses of >=1 day have occurred in roughly a fifth of modern CR "
  "deadlines. Capped 0.55 by class; priced at the base rate because there is no fresh "
  "primary datapoint to justify divergence (R26).",
  "DIRECTION class and a discretionary-choice row — the double-flagged shape. Priced AT the "
  "outside-view base rate with no divergence, which is what R26 demands when you have no "
  "dated datapoint the reference lacks. The book's instinct here would be 0.6+; that instinct "
  "is what #72 cost.",
  "A lapse is a TGA and bill-supply event before it is a growth event.")

N("tga-rebuild", "rc-anchor", "TGA balance above $700B on any weekly H.4.1 by 3/2027", 0.64,
  "2027-03-31", "rates-credit", "level", "2 quarters",
  "Weekly published series; the rebuild path is mechanical once funding is settled. Priced "
  "off the historical post-resolution rebuild pace.",
  "Level on a weekly series - cheap to check every session, which is lesson 6's whole point. The mechanism is mechanical (receipts minus outlays against a cash target), but the PATH is set by the funding fight above, so this row is explicitly downstream of cr-dec11 rather than independent evidence for it.",
  "A TGA rebuild drains reserves and is the hidden tightening nobody votes on.",
  odds={"tool": "range_odds",
        "command": "python tools/range_odds.py --spot 500 --hi 700 --days 27 --vol 10 --touch",
        "odds": 0.45,
        "note": "Units $bn. TOUCH claim ('above $700B on ANY weekly H.4.1'), so --touch. ASSUMED "
                "spot $500B and 10%/WEEK vol (the TGA is a cash balance, not a price); 27 weekly "
                "prints to 3/2027."})

N("muni-supply", "rc-anchor", "2026 full-year municipal issuance sets a nominal record", 0.72,
  "2027-01-31", "rates-credit", "invariant", "1 quarter",
  "Arithmetic: with three quarters already printed, a full-year record needs only an ordinary "
  "Q4. Nominal records are also mechanically easier every year under any inflation.",
  "This is the 'base-effect identity check' shape (doctrine 13d.2) used the RIGHT way round: "
  "a NOMINAL record is arithmetic, not a judgment about demand.",
  "Record supply into a 4% 10y is the muni-specific version of the duration problem.")

N("refi-wall-2027", "rc-anchor", "2027 US corporate maturity wall exceeds 2026's", 0.88,
  "2027-01-31", "rates-credit", "invariant", "1 quarter",
  "Pure arithmetic. The maturity schedule of already-issued bonds is known today; the only "
  "way 2027 comes in under 2026 is a large tender/refi wave, which is observable in advance.",
  "INVARIANT class, and the highest-P row in the buildout for that reason. P>=0.80 is reserved "
  "for exactly this (R13): a fact about paper already printed.",
  "The wall is the reason a 4% 10y matters more in 2027 than in 2026.")

N("bank-nim-compression", "rc-anchor", "Aggregate large-bank NIM falls q/q in at least one of the "
  "next two reported quarters", 0.62, "2027-04-30", "rates-credit", "scheduled", "2 quarters",
  "Scheduled reporting; the direction rests on deposit beta after a hike, which is a behavioural "
  "aggregate rather than a physical constraint. Capped accordingly.",
  "Scheduled-print class for the event, mid-probability for the value. Deliberately not bundled "
  "with a credit-loss claim — one claim per row (#63).",
  "Deposit beta is the channel through which a hike hits lending capacity.")

# ══════════════════════════════════════════════════════════════════════════════
# LANE: energy-supply (16) — the NON-Iran half of energy. The iran-energy cluster
#   is at 44% of open rows, over the 35% cap, so structural supply gets its own lane.
# ══════════════════════════════════════════════════════════════════════════════
N("es-anchor", "now", "Energy supply: the non-Iran half of the oil and power story", 1.0,
  "2026-10-01", "energy-supply", "invariant", "structural",
  "Anchor. Splits structural supply/demand out of the iran-energy cluster, which is over the "
  "35% concentration cap.",
  "Lane anchor. Created specifically to give energy rows somewhere to live that is NOT the "
  "iran-war cluster — hygiene rule 1, and the reason 14 of 32 open rows sat in one basket.",
  "Everything here trades independent of the strait.")

N("opec-nov-meeting", "es-anchor", "OPEC+ ministerial meeting convenes", 0.96, "2026-11-01",
  "energy-supply", "scheduled", "10 weeks",
  "The group's meeting calendar is published a year ahead; meetings occur essentially without "
  "exception, occasionally by video or rescheduled by days.",
  "Scheduled EVENT, not a policy forecast. The distinction is the entire #29 lesson: the "
  "meeting happening is near-certain, what the cartel decides is a discretionary choice.",
  "The meeting date is a vol event regardless of outcome.", kind="checkpoint",
  shifts=[{"target": "opec-quota-unchanged", "p_to": 0.55, "note": "policy resolves here"},
          {"target": "brent-band-q4", "p_to": 0.70, "note": "supply guidance sets the band"}])

N("opec-quota-unchanged", "opec-nov-meeting", "OPEC+ leaves headline quotas unchanged at the "
  "November meeting", 0.55, "2026-11-01", "energy-supply", "direction", "10 weeks",
  "Hard cap 0.55: this is a cartel of sovereigns exercising discretion. #29 priced exactly "
  "this shape at 0.58 on a premise that had already evaporated and scored 0.34.",
  "DIRECTION + discretionary. Capped at the ceiling and left there. The lesson from #29 is not "
  "'predict OPEC better', it is 'OPEC is not a mechanism'.",
  "Unchanged is the low-vol outcome for the band row below.")

N("brent-band-q4", "es-anchor", "Brent front-month trades inside $85-$125 for the whole of Q4",
  0.35, "2026-12-31", "energy-supply", "level", "1 quarter",
  "No-view odds on a wide two-sided band from ~104 with a war premium in the price. The band "
  "is set wide on purpose: a narrow band is how #69 died in two sessions.",
  "[9/22 CORRECTION] range_odds.py puts the no-view odds at 0.39 and this row was logged at 0.66, "
  "+0.27 off it with no dated catalyst in the basis; re-priced 0.66 -> 0.45 toward the "
  "arithmetic. The 0.8%/day vol the 9/21 author had in mind is 12.8% annualised, which Brent has "
  "never sustained; at the 2.5%/day the repo's own 9/9-9/20 tape implies, a 20%-wide band held on "
  "EVERY close for a quarter is a MINORITY outcome, so this row moves DOWN, not up. Level row, "
  "ONE asset, explicit band, wide. Note what it is NOT: a call on whether oil goes up or down. "
  "The book is 0-for-8 on that question in this tape.",
  "The band is the tradeable object; the direction is not.",
  odds={"tool": "range_odds",
        "command": "python tools/range_odds.py --spot 103.87 --lo 85 --hi 125 --days 65 --vol 2.5",
        "odds": 0.39,
        "note": "Spot 103.87 is the repo's own tape (STATE.md 9/20). Vol 2.5%/day ~ 40% "
                "annualised, which is what the repo's own 9/9-9/20 Brent record implies (101-109 "
                "range, peak close 108.75) - a war-premium crude regime, NOT the 0.8%/day (12.8% "
                "annualised) that Brent has never sustained. 65 Q4 sessions."})

N("shale-rig-floor", "es-anchor", "US oil rig count stays above 400 every week through Q1 2027",
  0.8, "2027-03-31", "energy-supply", "duration", "2 quarters",
  "Duration framing. With crude above $100 the drilling economics are not the binding "
  "constraint; a fall through 400 would require a price collapse first. Weekly published.",
  "[9/22 CORRECTION] cycle_odds.py puts the no-view survival band at 0.87-0.89 and this row was "
  "logged at 0.76, more than 0.10 outside it with no dated catalyst in the basis; re-priced 0.76 "
  "-> 0.80 into the band. Duration re-expression of what would otherwise be a shale-response "
  "direction call. The conditional structure (only breaks if price breaks first) makes it a "
  "near-invariant.",
  "Rig counts are the slow supply response; they are a lagging confirmation, never a signal.",
  odds={"tool": "cycle_odds",
        "command": "python tools/cycle_odds.py --current 400 --days 190 --prior-median 900",
        "ends_lo": 0.11, "ends_hi": 0.13,
        "phase_ends": False,
        "note": "ASSUMED: the rig count has been above 400 for ~400d; median length of an "
                "above-400 spell ~900d."})

N("lng-capacity-2027", "es-anchor", "At least one new large-scale LNG train reaches first cargo "
  "during 2027", 0.86, "2027-12-31", "energy-supply", "invariant", "5 quarters",
  "Capital-committed: trains that will start up in 2027 are already built or in commissioning "
  "today. Construction schedules slip by quarters, not years, at this stage.",
  "INVARIANT class — concrete already poured. This is the physical-constraint shape at 8-for-8. "
  "Slippage risk is why it is 0.86 and not 0.95.",
  "New LNG supply is the structural cap on the European gas premium.")

N("refinery-closure", "es-anchor", "A previously announced refinery closure completes on schedule",
  0.80, "2027-06-30", "energy-supply", "invariant", "3 quarters",
  "Capital already committed: an announced closure is a capital decision taken, and reversal requires fresh capital plus a restart schedule once units are cold. Reference class: announced refinery closures that completed.",
  "Invariant class: a closure announcement is a committed action, unlike a strike PLAN (#72), "
  "which is a negotiating instrument. The distinction between committed and announced-intent "
  "is the single most useful line the 16.14 patch drew.",
  "Closures are why crack spreads can stay wide with crude flat.")

N("diesel-crack-wide", "es-anchor", "ULSD crack stays above $25/bbl on every weekly close to 3/2027",
  0.70, "2027-03-31", "energy-supply", "duration", "2 quarters",
  "Duration. Distillate is structurally short on closed conversion capacity plus a rerouting "
  "premium; the floor holds unless demand breaks.",
  "Duration + a physical capacity constraint. Note this is the SAME view as the refinery row "
  "and is therefore not independent evidence for it — flagged here so the book does not count "
  "one thesis twice (the #70/#27 error).",
  "Diesel is the industrial read and the pass-through channel into core goods.",
  odds={"tool": "cycle_odds",
        "command": "python tools/cycle_odds.py --current 200 --days 190 --prior-median 400",
        "ends_lo": 0.2, "ends_hi": 0.26,
        "phase_ends": False,
        "note": "ASSUMED: the >$25 ULSD crack regime is ~200d old; median length of a "
                "wide-distillate-crack regime ~400d (crack regimes are shorter-lived than "
                "rig-count regimes)."})

N("natgas-storage", "es-anchor", "US working gas in storage ends the injection season above the "
  "five-year average", 0.58, "2026-11-30", "energy-supply", "scheduled", "10 weeks",
  "Weekly EIA series with a hard seasonal endpoint. Priced near even: LNG export pull against "
  "record production is genuinely balanced, and pretending otherwise is false precision.",
  "A deliberately near-even row. The book's measured resolution is ~0.00 partly because "
  "everything was stated between 0.40 and 0.88 — a row that is honestly 0.58 should be "
  "logged at 0.58 and not talked up into a story.",
  "Storage is the winter risk premium in one number.")

N("power-demand-record", "es-anchor", "US summer 2027 peak load sets a record", 0.78,
  "2027-09-30", "energy-supply", "invariant", "4 quarters",
  "Near-arithmetic on the demand side: datacenter load additions are contracted years ahead and "
  "electrification is monotonic. The residual risk is weather, not demand.",
  "Invariant-adjacent: contracted load is capital-committed. The only real uncertainty is a "
  "cool summer, which is a stated, bounded risk rather than a narrative.",
  "Load growth is the physical fact under every AI-power trade in the markets-ai lane.",
  shifts=[{"target": "ai-power-contracts", "p_to": 0.80, "note": "load growth is the same fact"}])

N("pjm-capacity-auction", "es-anchor", "PJM base residual capacity auction clears", 0.92,
  "2027-05-31", "energy-supply", "scheduled", "3 quarters",
  "Scheduled market event on a published calendar; delays have happened, which is why it is "
  "not 1.0.",
  "Scheduled class. The auction CLEARING is the claim; the clearing price is a separate level "
  "row and must not be bundled (#63).",
  "Capacity prices are the cleanest published number for the power-scarcity thesis.",
  kind="checkpoint",
  shifts=[{"target": "power-demand-record", "p_to": 0.80, "note": "auction confirms load growth"}])

N("nuclear-restart", "es-anchor", "A US reactor restart or uprate adds capacity to the grid by "
  "end-2027", 0.72, "2027-12-31", "energy-supply", "invariant", "5 quarters",
  "Capital-committed projects with regulatory milestones already cleared. Schedule risk is "
  "real but the decision is not in question.",
  "Invariant class with regulatory slippage risk priced in. Contrast with a policy row about "
  "new reactors, which would be a choice row and capped.",
  "Firm baseload is the constraint the datacenter buildout runs into.")

N("interconnect-queue", "es-anchor", "Interconnection queue wait times stay above 3 years", 0.84,
  "2027-12-31", "energy-supply", "invariant", "5 quarters",
  "Structural: queue length is a stock with a known processing rate. Reform helps at the margin "
  "and slowly; the stock cannot clear in five quarters.",
  "INVARIANT: a queue is arithmetic. This is the most under-appreciated physical constraint in "
  "the entire AI-power story and it has no node anywhere in the existing tree.",
  "The queue, not capital, is what rations new generation.")

N("transformer-leadtime", "es-anchor", "Large power transformer lead times stay above 100 weeks",
  0.82, "2027-12-31", "energy-supply", "invariant", "5 quarters",
  "Manufacturing capacity for large units is globally concentrated and capacity additions take "
  "years; the backlog is a stock.",
  "Invariant. Same shape as the queue row and — importantly — CORRELATED with it. Both express "
  "'the grid is supply-constrained'. Counting them as two insights would repeat #70/#27.",
  "Equipment lead times are the hard floor under grid capex timelines.")

N("spr-refill", "es-anchor", "SPR inventory ends 2027 below 500 million barrels", 0.74,
  "2027-12-31", "energy-supply", "invariant", "5 quarters",
  "Arithmetic: refill rates are capped by physical injection capacity and by appropriated funds, "
  "both bounded and observable weekly.",
  "Invariant-adjacent: a physical injection-rate ceiling. Priced off the rate limit, not off "
  "anyone's stated intention to refill.",
  "A thin SPR is the reason a supply shock has no domestic shock absorber.")

N("eia-forecast-cycle", "es-anchor", "EIA Short-Term Energy Outlook published monthly without a gap",
  0.94, "2027-06-30", "energy-supply", "scheduled", "3 quarters",
  "A statutory statistical publication on a fixed monthly calendar; gaps occur only in a "
  "funding lapse, which is itself a separate node.",
  "Scheduled class. Included as an explicit dependency: the shutdown row above would BREAK this "
  "one. Making that dependency a node is what stops the two rows from silently contradicting.",
  "No STEO means no official supply/demand balance for the whole lane.", kind="checkpoint",
  shifts=[{"target": "brent-band-q4", "p_to": 0.66, "note": "data gap widens the band"}])

N("coal-retirement-delay", "es-anchor", "At least one scheduled US coal retirement is deferred",
  0.80, "2027-12-31", "energy-supply", "invariant", "5 quarters",
  "Reliability-driven deferrals have become routine wherever load growth outpaces new firm "
  "capacity; the driver is the interconnection/transformer constraint above, not politics.",
  "Consequence of the two invariant constraints above. Logged as a separate row only because "
  "it is separately observable — its independence is LOW and that is stated, not hidden.",
  "Deferrals are the visible symptom of the firm-capacity shortfall.")

# ══════════════════════════════════════════════════════════════════════════════
# LANE: china-macro (14)
# ══════════════════════════════════════════════════════════════════════════════
N("cn-anchor", "now", "China macro: the deflation-and-transfer problem", 1.0, "2026-10-01",
  "china-macro", "invariant", "structural",
  "Definitional lane label, p=1.0 by construction. Separates China's domestic macro from the taiwan-china security lane, which is a different causal system.",
  "Lane anchor. The existing tree has China only as a security actor; its balance sheet is a "
  "separate causal system and deserves its own lane.",
  "China's domestic demand is the swing input to every commodity row in this tree.")

N("npc-2027", "cn-anchor", "National People's Congress convenes", 0.97, "2027-03-05",
  "china-macro", "invariant", "2 quarters",
  "The NPC has convened in early March annually for decades; the date is institutional.",
  "Invariant EVENT on a fixed institutional calendar. The growth target announced there is a SEPARATE row, because bundling the meeting with its output is the #63 conjunction error: a near-certain event and an uncertain value priced as one claim.",
  "The NPC sets the fiscal number the whole year trades off.", kind="checkpoint",
  shifts=[{"target": "cn-growth-target", "p_to": 0.72, "note": "the target is set here"},
          {"target": "cn-fiscal-deficit", "p_to": 0.66, "note": "the budget is tabled here"}])

N("cn-growth-target", "npc-2027", "2027 growth target set at 'around 5%'", 0.72, "2027-03-05",
  "china-macro", "scheduled", "2 quarters",
  "Strong base rate: the target has been set at or around 5% repeatedly, and the target is a "
  "political constant more than an economic forecast. Reference class: the last several NPCs.",
  "Scheduled with a strong institutional base rate. Note it is still a CHOICE, which caps it "
  "under the invariant rows; 0.72 sits at the top of what R13 allows only because the "
  "reference class is this tight.",
  "The target is the fiscal constraint, not a forecast.")

N("cn-fiscal-deficit", "npc-2027", "Headline budget deficit ratio set at or above 3.5%", 0.66,
  "2027-03-05", "china-macro", "scheduled", "2 quarters",
  "Base rate off the recent trajectory of widening headline ratios; still a discretionary "
  "budget decision, so capped.",
  "Scheduled-print class for a discretionary number. The engine's edge is in knowing WHEN it "
  "lands, not what it will be - which is why the date is near-certain and the value is capped. "
  "The LGSB quota row below is the better read on the actual impulse and the two are one view.",
  "The headline ratio understates the real impulse; the LGSB quota row below matters more.")

N("cn-population-decline", "cn-anchor", "Official 2026 population figure shows another y/y decline",
  0.93, "2027-01-31", "china-macro", "invariant", "1 quarter",
  "Demographic arithmetic: the birth cohort and the death cohort are both largely determined "
  "years in advance. A reversal would require a fertility jump with no precedent.",
  "INVARIANT — pure demographic arithmetic, and one of the few things in this tree that is "
  "genuinely close to certain. This is the row class the book scores 0.10 Brier on.",
  "Demography is the slow denominator under every China demand row.")

N("cn-property-starts", "cn-anchor", "New residential starts stay below 60% of the 2019 level "
  "every month through 2027", 0.85, "2027-12-31", "china-macro", "invariant", "5 quarters",
  "Near-arithmetic: the inventory overhang plus developer balance-sheet damage are stocks that "
  "cannot clear on this horizon, and starts are a monthly published series.",
  "Invariant-adjacent. A stock constraint, monthly observable, with a wide margin to the "
  "threshold — the shape that produces low Brier.",
  "Property starts are the single biggest swing factor in global steel, copper and iron ore.",
  shifts=[{"target": "copper-deficit", "p_to": 0.62, "note": "weak China demand offsets mine deficit"}])

N("cn-deflator", "cn-anchor", "GDP deflator prints negative y/y in at least one quarter of 2027",
  0.70, "2027-12-31", "china-macro", "scheduled", "5 quarters",
  "Continuation of an established run; priced on persistence, not on a turn call. Quarterly "
  "published series.",
  "A persistence row, which is the 16.18 shape ('the level persists, the direction does not'). "
  "Deliberately NOT a call on when reflation arrives.",
  "Chinese deflation is the disinflationary offset to the US supply shock — the two-sided story "
  "the fed-macro lane needs.")

N("pboc-rrr-cut", "cn-anchor", "PBoC cuts the reserve requirement ratio at least once by mid-2027",
  0.55, "2027-06-30", "china-macro", "direction", "3 quarters",
  "Capped 0.55: a central-bank discretionary action, the #26 class. The base rate of at least "
  "one RRR cut in a three-quarter window is high historically, which is precisely why the cap "
  "matters — the temptation is to price it 0.80.",
  "DIRECTION + discretionary committee. This row exists partly as a live test of the cap: the "
  "base rate genuinely argues higher, and the rule says no. If a run of these resolves HIT at "
  "0.55, that is evidence to relax R13 deliberately rather than by accident.",
  "RRR cuts are liquidity, not demand; the transmission is the question.")

N("cn-yuan-band", "cn-anchor", "USDCNY fixes inside 6.80-7.60 on every fixing through Q2 2027",
  0.80, "2027-06-30", "china-macro", "level", "3 quarters",
  "The fix is a managed, published daily number with a demonstrated tolerance band. This is "
  "closer to an institutional invariant than a market level.",
  "Level row on a MANAGED price — which makes it institutional rather than discretionary. The "
  "distinction matters: the band is defended by policy, so the constraint is real.",
  "A break of the band is the single loudest signal China has stopped defending stability.",
  odds={"tool": "range_odds",
        "command": "python tools/range_odds.py --spot 7.15 --lo 6.80 --hi 7.60 --days 192 --vol 0.15",
        "odds": 0.98,
        "note": "ASSUMED spot fix 7.15 and 0.15%/day FIX vol (~2.4% annualised). The row is about "
                "the PBoC's daily FIX, which is managed and far less volatile than spot; 192 "
                "sessions to 6/30/27."})

N("cn-export-share", "cn-anchor", "China's share of global goods exports stays above 13%", 0.84,
  "2027-12-31", "china-macro", "invariant", "5 quarters",
  "Share of a slow-moving denominator; tariffs reroute trade but do not remove manufacturing "
  "capacity from the world on this horizon.",
  "Invariant class. Tariff rows are politics; SHARE is an industrial-capacity fact. Keeping "
  "them separate is the whole point of the row-class discipline.",
  "Rerouting shows up in bilateral data long before it shows up in share.")

N("cn-lgsb-quota", "cn-anchor", "Local government special bond quota set above CNY 4 trillion",
  0.68, "2027-03-05", "china-macro", "scheduled", "2 quarters",
  "Base rate off the recent quota path; a discretionary number on a fixed calendar.",
  "Scheduled. The LGSB quota is the real fiscal impulse and a better row than the headline "
  "deficit — noted so the two are not treated as independent.",
  "The quota is the actual construction-demand number.")

N("cn-rare-earth-controls", "cn-anchor", "Export-licence controls on at least one additional "
  "critical mineral category are announced by end-2027", 0.52, "2027-12-31",
  "china-macro", "direction", "5 quarters",
  "A sovereign policy choice — capped. Base rate is meaningful given the established pattern, "
  "but pattern-continuation on a discretionary lever is exactly leg-extrapolation (16.15).",
  "DIRECTION + discretionary + pattern-continuation. Triple-flagged, priced near even. The "
  "engine's instinct on this row would be 0.75; that instinct is the thing being corrected.",
  "Controls are a supply-chain event with a long fuse and a fast price reaction.",
  shifts=[{"target": "rare-earth-onshoring", "p_to": 0.75, "note": "controls accelerate onshoring"}])

N("cn-gold-buying", "cn-anchor", "PBoC reports gold reserve additions in at least 8 of the next "
  "12 monthly reports", 0.70, "2027-09-30", "china-macro", "marker", "4 quarters",
  "Marker on a monthly published series with a long established run. Persistence, not turn.",
  "Marker class: the claim is that an observable keeps APPEARING, not that it rises or falls. "
  "Cheap to check monthly, which is what lesson 6 asks for. Note this is a persistence row on "
  "official-sector behaviour, so its failure mode is a policy change, not a price move.",
  "Official-sector buying is the structural bid under the gold row in commodities-metals.",
  shifts=[{"target": "gold-level", "p_to": 0.74, "note": "official bid underpins the level"}])

N("cn-ai-chip-domestic", "cn-anchor", "A domestic Chinese accelerator is credibly reported in "
  "volume deployment at a major Chinese cloud by end-2027", 0.62, "2027-12-31",
  "china-macro", "marker", "5 quarters",
  "Marker with reporting-quality risk. Priced mid: the industrial push is capital-committed, "
  "the 'credible volume' threshold is the soft part.",
  "Marker with an explicitly soft threshold — and the softness is STATED. #59 was scored against "
  "the engine because its threshold was ambiguous and nobody had written down who decides.",
  "Domestic substitution is the terminal risk to the export-control thesis.")

N("cn-belt-road-lending", "cn-anchor", "Reported annual BRI lending stays below its peak-year level",
  0.86, "2027-12-31", "china-macro", "invariant", "5 quarters",
  "Balance-sheet arithmetic: the retrenchment is driven by non-performing exposure already "
  "incurred, and a return to the peak would require a funding source that does not exist. "
  "Reference class: post-impairment lending cycles.",
  "Invariant-adjacent, priced high because the constraint is a damaged balance sheet rather "
  "than a preference - a lender with non-performing exposure cannot re-lend at peak scale "
  "regardless of intent. Preference can reverse in a quarter; an impaired balance sheet cannot.",
  "BRI retrenchment is the funding gap behind several emerging-market rows.")

# ══════════════════════════════════════════════════════════════════════════════
# LANE: europe (14)
# ══════════════════════════════════════════════════════════════════════════════
N("eu-anchor", "now", "Europe: the fiscal-and-energy squeeze", 1.0, "2026-10-01",
  "europe", "invariant", "structural",
  "Definitional lane label, p=1.0 by construction. Europe appears nowhere in the existing "
  "66-node tree despite being the marginal buyer of the energy this book trades.",
  "Lane anchor. A genuine coverage hole: the tree has no European node at all, so every "
  "European transmission of an oil shock was implicit.",
  "Europe is the price-taker that sets the marginal LNG and diesel price.")

N("ecb-dec-meeting", "eu-anchor", "ECB Governing Council monetary policy meeting", 0.98,
  "2026-12-17", "europe", "invariant", "12 weeks",
  "The ECB publishes its meeting calendar years ahead; meetings are institutional.",
  "Invariant EVENT. The decision is a separate, capped row — the same split the #26 lesson "
  "forces on every central-bank node.",
  "The meeting is the date; the decision is the risk.", kind="checkpoint",
  shifts=[{"target": "ecb-hold", "p_to": 0.55, "note": "policy resolves here"},
          {"target": "eur-level", "p_to": 0.72, "note": "policy divergence sets the cross"}])

N("ecb-hold", "ecb-dec-meeting", "ECB leaves the deposit rate unchanged in December", 0.55,
  "2026-12-17", "europe", "direction", "12 weeks",
  "Capped 0.55 — committee discretion, the #26 class. An energy shock cuts both ways for the "
  "ECB (inflationary and contractionary), so there is no mechanism argument for divergence.",
  "DIRECTION + committee. Note the internal-consistency requirement: this book already says "
  "the Fed hiked into the same oil shock. If this row were priced as a confident hold, the "
  "book would be claiming the same shock means opposite things at two central banks without "
  "saying why. It might — but it has to SAY why.",
  "ECB-Fed divergence is the euro trade.")

N("eu-defence-spending", "eu-anchor", "At least 20 NATO members report defence spending at or "
  "above 2% of GDP for 2026", 0.80, "2027-06-30", "europe", "invariant", "3 quarters",
  "Budgets for the reporting year are already enacted; this is a count of decisions already "
  "taken, reported on a fixed annual cycle.",
  "INVARIANT: enacted budgets are capital-committed. Contrast with a row about future pledges, "
  "which would be rhetoric (doctrine 12.1 / R03).",
  "Enacted European defence budgets are the demand under the defense-industrial lane.",
  shifts=[{"target": "defense-backlog", "p_to": 0.88, "note": "enacted budgets become backlog"}])

N("german-fiscal", "eu-anchor", "German federal investment spending in the 2027 budget exceeds "
  "the 2025 level in nominal terms", 0.82, "2027-01-31", "europe", "invariant", "1 quarter",
  "Nominal comparison against an already-legislated expansion; the base-effect identity makes "
  "this arithmetic rather than a policy forecast.",
  "Invariant, and an explicit use of doctrine 13d.2 the right way round: a NOMINAL comparison "
  "against a legislated baseline is arithmetic. The twice-repeated y/y miss came from doing "
  "this backwards.",
  "German investment is the only large European fiscal impulse in the window.")

N("france-deficit", "eu-anchor", "France's reported deficit for 2026 exceeds 4.5% of GDP", 0.78,
  "2027-03-31", "europe", "scheduled", "2 quarters",
  "Fiscal outturns are largely determined by the time three quarters have elapsed; the "
  "reporting date is a fixed Eurostat cycle.",
  "Scheduled with an arithmetic core — most of the year is already spent. This is the "
  "'scheduled print backed by arithmetic' class at 12-for-14.",
  "The French deficit is the OAT spread and therefore the EU fiscal-rules fight.",
  shifts=[{"target": "eu-fiscal-rules", "p_to": 0.62, "note": "a large miss forces the rules question"}])

N("eu-fiscal-rules", "eu-anchor", "A formal flexibility clause, escape clause or rule revision is "
  "applied to at least one large member state by end-2027", 0.62, "2027-12-31",
  "europe", "marker", "5 quarters",
  "Marker. Institutional base rate is high — the rules have been flexed repeatedly whenever "
  "they bound — but the specific instrument is a political choice.",
  "Marker rather than direction: the claim is that a legal instrument APPEARS, which is "
  "observable and dated, rather than that anyone 'gets tougher' or 'softer'.",
  "Rule flexibility is what keeps periphery spreads contained.")

N("italy-spread", "eu-anchor", "BTP-Bund 10y spread stays under 250bp on every close to mid-2027",
  0.82, "2027-06-30", "europe", "level", "3 quarters",
  "Level row with an institutional backstop (the ECB's transmission instrument) that has never "
  "been tested to failure. Priced off distance-to-threshold.",
  "[9/22 CORRECTION] range_odds.py puts the no-view odds at 0.99 and this row was logged at 0.76, "
  "-0.23 off it with no dated catalyst in the basis; re-priced 0.76 -> 0.82 toward the "
  "arithmetic. Level, one spread, one side. The backstop is an institutional invariant; the "
  "spread is a market price. Naming which part is which is what keeps the row honest.",
  "The periphery spread is the European version of the credit rows in rates-credit.",
  odds={"tool": "range_odds",
        "command": "python tools/range_odds.py --spot 105 --hi 250 --days 192 --vol 2.5",
        "odds": 0.99,
        "note": "ASSUMED spot 105bp BTP-Bund and 2.5%/day relative vol (~2-3bp/day on 105bp). 192 "
                "sessions."})

N("eur-level", "eu-anchor", "EURUSD trades inside 0.95-1.20 on every close through Q2 2027",
  0.84, "2027-06-30", "europe", "level", "3 quarters",
  "Wide band, no-view odds. A 25-figure range on the most liquid cross over three quarters is "
  "a high-probability containment claim, not a view.",
  "Deliberately a BAND and deliberately wide — the anti-#69 construction. One asset, two "
  "bounds, wide enough that it is a genuine claim about volatility rather than direction.",
  "The cross is where Fed-ECB divergence actually prints.",
  odds={"tool": "range_odds",
        "command": "python tools/range_odds.py --spot 1.08 --lo 0.95 --hi 1.20 --days 192 --vol 0.50",
        "odds": 0.83,
        "note": "ASSUMED spot 1.08 and 0.50%/day (~8% annualised, EURUSD's usual range). 192 "
                "sessions to 6/30/27."})

N("eu-carbon-band", "eu-anchor", "EUA carbon price trades inside EUR 50-140 through 2027", 0.78,
  "2027-12-31", "europe", "level", "5 quarters",
  "Wide band on a policy-supplied market with a legislated supply corridor — the corridor is "
  "the institutional constraint doing the work.",
  "Level row where the band is underwritten by legislation, which is what makes it a "
  "near-invariant rather than a market call.",
  "Carbon is a direct input into the European power and industrial cost base.",
  odds={"tool": "range_odds",
        "command": "python tools/range_odds.py --spot 75 --lo 50 --hi 140 --days 320 --vol 2.2",
        "odds": 0.61,
        "note": "ASSUMED spot EUR 75/t and 2.2%/day (~35% annualised; EUAs are a thin "
                "policy-supplied market). 320 sessions to end-2027."})

N("eu-gas-storage", "eu-anchor", "EU gas storage ends the 2026-27 withdrawal season above 25% full",
  0.72, "2027-04-30", "europe", "scheduled", "2 quarters",
  "Published daily; the endpoint is seasonal and the outcome is dominated by weather plus LNG "
  "availability, both partially observable in advance.",
  "Scheduled with a physical core. Explicitly dependent on the LNG row in energy-supply — the "
  "dependency is declared rather than double-counted.",
  "Storage exit level sets the summer refill bid and next winter's European premium.")

N("uk-gilt-marker", "eu-anchor", "UK 30y gilt yield prints above 6.00% on any close by mid-2027",
  0.40, "2027-06-30", "europe", "marker", "3 quarters",
  "Marker on a tail event. Priced BELOW the book's average on purpose: a book whose rows all "
  "sit between 0.40 and 0.88 has no resolution, and genuine tails must be logged as tails.",
  "A deliberately LOW-probability row. The 9/20 research found every row stated between 0.40 "
  "and 0.88 and small-sample-corrected resolution near zero. You cannot fix that by lowering "
  "high rows; you fix it by being willing to say 'probably not' and be right.",
  "A gilt event is the fastest route from a fiscal story to a global rates event.")

N("eu-russia-assets", "eu-anchor", "A binding EU legal instrument on immobilised Russian sovereign "
  "assets beyond windfall profits is adopted by end-2027", 0.45, "2027-12-31",
  "europe", "direction", "5 quarters",
  "Requires unanimity or a workaround among sovereign governments — the discretionary-choice "
  "class, capped, and priced below even because the legal obstacles are structural.",
  "DIRECTION + multi-sovereign discretion. The structural legal obstacle is the reason this is "
  "priced under 0.50 rather than at the 0.55 cap: the cap is a ceiling, not a target.",
  "The asset question is the funding source for the Ukraine tranche row.")

N("ukraine-tranche", "eu-anchor", "A further multi-year EU financial support tranche for Ukraine "
  "is legally committed by end-2027", 0.70, "2027-12-31", "europe", "marker", "5 quarters",
  "Institutional base rate is strong: every previous funding cliff has been met, late and by a "
  "workaround. Priced on the institutional pattern, not on goodwill.",
  "Marker. Priced at 0.70 — the R13 ceiling for non-invariant rows — and justified by an "
  "institutional pattern rather than a mechanism, which is the weaker of the two grounds. "
  "Flagged as such.",
  "Funding continuity is what keeps the European fiscal path tight.")

N("german-ip", "eu-anchor", "German industrial production stays below its 2017 index level every "
  "month through 2027", 0.80, "2027-12-31", "europe", "invariant", "5 quarters",
  "Persistence of a structural energy-cost disadvantage; industrial capacity that has closed "
  "does not reopen inside five quarters.",
  "Invariant-adjacent persistence row. The mechanism (closed capacity is a stock) is physical, "
  "which is the class the book wins on.",
  "German IP is the clearest single measure of European deindustrialisation.")

# ══════════════════════════════════════════════════════════════════════════════
# LANE: commodities-metals (14) — where geology IS the invariant
# ══════════════════════════════════════════════════════════════════════════════
N("cm-anchor", "now", "Commodities & metals: geology as a hard constraint", 1.0, "2026-10-01",
  "commodities-metals", "invariant", "structural",
  "Anchor. Mine supply, ore grade and smelter capacity are physical stocks with decade lead "
  "times - the purest invariant material available to this engine.",
  "Lane anchor. If the book's edge is physical invariants at Brier 0.10, then mining is the "
  "richest untapped vein of exactly that row class, and the tree had none of it.",
  "Metals are where a supply thesis can be right without needing anyone to decide anything.")

N("gold-level", "cm-anchor", "Gold holds above $2,800/oz on every month-end close through 2027",
  0.80, "2027-12-31", "commodities-metals", "level", "5 quarters",
  "No-view odds on the distance to the threshold, with a structural official-sector bid (see "
  "the PBoC marker) plus a live war premium. Resolution convention is published month-end "
  "closes only, to avoid resolving on a wick - the #59 scope lesson.",
  "Level, one asset, one side, and the resolution convention (month-end close) is written into "
  "the claim. #59 was scored against the engine purely because nobody wrote down which prints "
  "counted.",
  "Gold is the one asset that wins on both the inflation leg and the war leg.",
  odds={"tool": "range_odds",
        "command": "python tools/range_odds.py --spot 3400 --lo 2800 --days 15 --vol 4.5",
        "odds": 0.79,
        "note": "ASSUMED spot $3,400/oz and 4.5%/MONTH vol (~15% annualised). The row's own "
                "resolution convention is MONTH-END closes only, so one period = one month and "
                "days=15 is the 15 month-ends to end-2027."})

N("copper-deficit", "cm-anchor", "Refined copper market reports a supply deficit for 2027", 0.62,
  "2028-03-31", "commodities-metals", "invariant", "6 quarters",
  "Mine supply for 2027 is essentially fixed today (projects in commissioning), so the deficit "
  "question reduces to demand - and Chinese property weakness is the live offset. Priced mid "
  "BECAUSE the two invariants point opposite ways.",
  "Two invariants in opposition - supply arithmetic says deficit, the China property row says "
  "demand shortfall. The honest answer is a mid probability, not a story that resolves the "
  "tension. This is the anti-#76 construction: do not talk yourself into one side.",
  "Copper is the cleanest AI-buildout-versus-China-property expression.")

N("copper-grade", "cm-anchor", "Average head grade at the major porphyry mines declines again "
  "year-on-year", 0.88, "2028-03-31", "commodities-metals", "invariant", "6 quarters",
  "Geology. Grade decline at mature porphyry deposits is monotonic and has been for decades; "
  "reversal would require new high-grade discoveries already in production, which do not exist.",
  "INVARIANT in the strongest available sense - this is a fact about rock. Priced at the top "
  "of the book's range, which R13 permits only for exactly this.",
  "Falling grade is why copper capex buys less supply every year.")

N("uranium-term", "cm-anchor", "Uranium term-contract price stays above $70/lb through 2027", 0.78,
  "2027-12-31", "commodities-metals", "duration", "5 quarters",
  "Duration. Term contracting is driven by utility replacement-rate arithmetic, and the "
  "under-contracted position is a known stock.",
  "Duration class on a contracted (not spot) price, which makes it institutional rather than "
  "speculative. The replacement-rate gap is arithmetic.",
  "Term price is the real signal; spot uranium is a thin, misleading tape.",
  odds={"tool": "cycle_odds",
        "command": "python tools/cycle_odds.py --current 500 --days 465 --prior-median 1100",
        "ends_lo": 0.19, "ends_hi": 0.24,
        "phase_ends": False,
        "note": "ASSUMED: the >$70/lb term-price regime is ~500d old; median length ~1100d (term "
                "contracting turns on multi-year utility replacement schedules)."})

N("lithium-oversupply", "cm-anchor", "Lithium carbonate stays below its 2022 peak in real terms "
  "through 2027", 0.90, "2027-12-31", "commodities-metals", "invariant", "5 quarters",
  "Capacity added into the 2022 spike is physically built and cannot be un-built; a return to "
  "the peak requires demand to outrun an installed base that tripled.",
  "Invariant: installed capacity is concrete. The highest-confidence row in the lane after "
  "grade decline, and for the same reason - it is about objects, not opinions.",
  "Cheap lithium is a cost tailwind for storage and therefore for the grid rows.")

N("silver-deficit-run", "cm-anchor", "Silver records another annual structural deficit for 2026",
  0.76, "2027-05-31", "commodities-metals", "invariant", "2 quarters",
  "Industrial demand (solar, electronics) is contracted and growing while mine supply is "
  "byproduct-constrained - silver supply cannot respond to price because it is mined as a "
  "byproduct of copper, lead and zinc.",
  "Invariant with a genuinely elegant mechanism: byproduct supply is price-INELASTIC by "
  "construction. That is a physical constraint, not a market view.",
  "The byproduct constraint is why silver behaves like an industrial metal with a monetary tail.")

N("platinum-deficit", "cm-anchor", "Platinum records a supply deficit for 2026", 0.74,
  "2027-05-31", "commodities-metals", "invariant", "2 quarters",
  "South African shaft depletion and power constraints cap supply; the constraint is physical "
  "and already visible in reported output.",
  "Invariant. Correlated with the silver row through 'precious industrial deficit' - declared "
  "so the book does not treat them as two independent confirmations (#70/#27).",
  "PGMs are the most supply-constrained precious complex.")

N("aluminium-power", "cm-anchor", "No net new primary aluminium smelting capacity is commissioned "
  "in Europe through 2027", 0.86, "2027-12-31", "commodities-metals", "invariant", "5 quarters",
  "Smelting is an electricity business; European power costs make new primary capacity "
  "uneconomic and no projects are under construction.",
  "Invariant, and directly downstream of the german-ip and eu-carbon rows - the same physical "
  "cause (power cost) expressed in a different, separately observable place.",
  "Aluminium is the purest traded proxy for the European energy-cost disadvantage.")

N("tin-supply", "cm-anchor", "Refined tin supply stays concentrated with the top three producing "
  "countries above 60% of output", 0.84, "2027-12-31", "commodities-metals", "invariant",
  "5 quarters",
  "Concentration is a geological and industrial fact with no new large-scale capacity in build.",
  "Invariant. Concentration rows are the single most reliable structure in commodities because "
  "the denominator moves at geological speed.",
  "Tin concentration is an under-watched semiconductor supply-chain risk (solder).")

N("fertilizer-gas-link", "cm-anchor", "European ammonia production stays below 70% of nameplate "
  "capacity through 2027", 0.78, "2027-12-31", "commodities-metals", "invariant", "5 quarters",
  "Ammonia is roughly 80% gas cost by input; with European gas structurally above US gas, "
  "utilisation is a direct arithmetic function of the spread.",
  "Invariant with an explicit cost identity. This is the market-transmission mechanism the book "
  "does well - a physical input-output relationship, not a sentiment chain.",
  "Ammonia utilisation transmits the gas price into the food-price rows.",
  shifts=[{"target": "wheat-stocks", "p_to": 0.60, "note": "input cost feeds grain economics"}])

N("wheat-stocks", "cm-anchor", "World wheat stocks-to-use for 2026/27 is reported below 32%",
  0.60, "2027-06-30", "commodities-metals", "scheduled", "3 quarters",
  "Scheduled monthly WASDE-style reporting; the value depends on harvests that are partly "
  "unknown. Priced near even because it genuinely is.",
  "Another honestly near-even row. #39's food-emergency leg failed partly because the engine "
  "wanted a dramatic number; the undramatic answer is that stocks-to-use is a coin near its "
  "threshold.",
  "Stocks-to-use is the only grain number that maps to price non-linearly.")

N("cocoa-normalisation", "cm-anchor", "Cocoa trades below $6,000/t on a month-end close by "
  "end-2027", 0.3, "2027-12-31", "commodities-metals", "duration", "5 quarters",
  "Tree crops mean-revert on a multi-year replanting cycle; the supply response is biological "
  "and therefore dated rather than discretionary.",
  "[9/22 CORRECTION] cycle_odds.py puts the no-view ending band at 0.17-0.26 and this row was "
  "logged at 0.66, more than 0.10 outside it with no dated catalyst in the basis; re-priced 0.66 "
  "-> 0.30 into the band. The memoryless model ignores the replanting deadline the basis itself "
  "relies on, so this is the floor of an honest price, not the last word. A biological-lag row: "
  "the supply response has a known duration because it is governed by how fast a tree grows. That "
  "is as close to physics as agriculture gets.",
  "Cocoa is the cleanest test of whether a spike was a shortage or a panic.",
  odds={"tool": "cycle_odds",
        "command": "python tools/cycle_odds.py --current 700 --days 465 --prior-median 900",
        "ends_lo": 0.17, "ends_hi": 0.26,
        "phase_ends": True,
        "note": "phase_ends=TRUE: the row claims the elevated-price phase ENDS (cocoa back under "
                "$6,000) by end-2027. ASSUMED: the spike is ~700d old; median length of a "
                "tree-crop price spike ~900d (a replanting cycle)."})

N("ags-enso-2027", "cm-anchor", "NOAA declares an ENSO-neutral or La Nina state for the 2027 "
  "northern summer", 0.68, "2027-08-31", "commodities-metals", "scheduled", "4 quarters",
  "Scheduled official declaration on a fixed monthly cycle; the base rate of neutral-or-Nina "
  "against El Nino across a randomly chosen season favours this side.",
  "Scheduled EVENT with a base-rate value. The declaration is by a named agency on a fixed "
  "calendar, which makes the resolution source unambiguous - the #59 fix.",
  "ENSO state is the single biggest exogenous input to the ag complex.")

# ══════════════════════════════════════════════════════════════════════════════
# LANE: labor-demo (12) — demographics is arithmetic; the labour market is not
# ══════════════════════════════════════════════════════════════════════════════
N("ld-anchor", "now", "Labour & demographics: the supply side of the inflation problem", 1.0,
  "2026-10-01", "labor-demo", "invariant", "structural",
  "Definitional lane label, p=1.0 by construction. Labour supply is the other half of a "
  "supply shock and the tree prices only the energy half.",
  "Lane anchor. The book has an oil-driven inflation story with no labour-supply node, which "
  "means the #32-versus-#26 contradiction had nowhere to be adjudicated.",
  "Labour supply decides whether an energy shock becomes a wage-price process.")

N("payrolls-oct", "ld-anchor", "October employment situation released", 0.95, "2026-11-06",
  "labor-demo", "scheduled", "7 weeks",
  "First Friday release on a published BLS calendar. Certain absent a funding lapse - which is "
  "an explicit node in rates-credit.",
  "Scheduled class, and deliberately cross-wired to the shutdown row so the dependency is "
  "visible in the graph rather than implicit.",
  "Payrolls is the highest-variance scheduled print in the calendar.", kind="checkpoint",
  shifts=[{"target": "u3-band", "p_to": 0.74, "note": "the print sets the rate"},
          {"target": "wage-band", "p_to": 0.70, "note": "AHE prints here"}])

N("payrolls-dec", "ld-anchor", "December employment situation released", 0.95, "2027-01-08",
  "labor-demo", "scheduled", "15 weeks",
  "Same fixed calendar. Included as a separate node because annual benchmark revisions land in "
  "this window and change the level, not just the print.",
  "Scheduled. The benchmark-revision property is the interesting part: a revision can make a "
  "resolved row wrong after the fact, which is a scoring-integrity issue this book has not "
  "faced yet.",
  "Benchmark revisions have repeatedly rewritten the labour narrative after the fact.",
  kind="checkpoint",
  shifts=[{"target": "u3-band", "p_to": 0.74, "note": "revisions reset the level"}])

N("u3-band", "ld-anchor", "U-3 unemployment prints inside 3.8-5.2% on every release through Q2 2027",
  0.8, "2027-06-30", "labor-demo", "level", "3 quarters",
  "Band row on a monthly series. The band is wide deliberately; unemployment is slow-moving "
  "month to month, so containment over three quarters is a claim about the absence of a "
  "recession rather than about the level.",
  "[9/22 CORRECTION] range_odds.py puts the no-view odds at 0.95 and this row was logged at 0.74, "
  "-0.21 off it with no dated catalyst in the basis; re-priced 0.74 -> 0.80 toward the "
  "arithmetic. Level with a wide band - the anti-#69 shape. Note what it really claims: no "
  "recession and no boom inside three quarters. Stating that plainly is better than hiding it "
  "inside a number.",
  "A break of the top of the band is the recession signal; the bottom is the overheating signal.",
  odds={"tool": "range_odds",
        "command": "python tools/range_odds.py --spot 4.4 --lo 3.8 --hi 5.2 --days 9 --vol 2.5",
        "odds": 0.95,
        "note": "ASSUMED spot U-3 4.4% and 2.5%/MONTH relative vol (~0.11pp on 4.4). One period = "
                "one monthly release; 9 releases to Q2 2027. Lognormal is a proxy for a bounded "
                "rate series."})

N("participation-drag", "ld-anchor", "Prime-age participation stays below its cycle peak every "
  "month through 2027", 0.8, "2027-12-31", "labor-demo", "duration", "5 quarters",
  "Duration. Participation ceilings are demographic and behavioural; exceeding a cycle peak "
  "requires an inflow that has to come from somewhere identifiable.",
  "[9/22 CORRECTION] cycle_odds.py puts the no-view survival band at 0.86-0.90 and this row was "
  "logged at 0.70, more than 0.10 outside it with no dated catalyst in the basis; re-priced 0.70 "
  "-> 0.80 into the band. Duration class. Priced at the R13 ceiling for non-invariants because "
  "the mechanism is demographic (strong) but the threshold is a cycle peak (soft).",
  "Participation is the supply constraint that turns demand into wages instead of jobs.",
  odds={"tool": "cycle_odds",
        "command": "python tools/cycle_odds.py --current 1400 --days 465 --prior-median 1800",
        "ends_lo": 0.1, "ends_hi": 0.14,
        "phase_ends": False,
        "note": "ASSUMED: prime-age participation has been below its cycle peak ~1400d; median "
                "length of such a spell ~1800d (participation ceilings are demographic)."})

N("labor-force-immigration", "ld-anchor", "Annual net international migration reported for 2026 "
  "comes in below the 2023-24 average", 0.82, "2027-12-31", "labor-demo", "invariant", "5 quarters",
  "Policy already enacted plus enforcement capacity already funded - the inputs are decisions "
  "taken, not decisions pending.",
  "INVARIANT-adjacent: enacted policy with funded enforcement is capital-committed action, "
  "which R03/doctrine 12.1 treats as real, as opposed to announced intent.",
  "Migration is the largest single swing factor in labour-force growth, and it is already set.",
  shifts=[{"target": "wage-band", "p_to": 0.70, "note": "supply constraint feeds wages"}])

N("boomer-retirement", "ld-anchor", "The 65+ share of the US population rises again in the 2026 "
  "vintage estimates", 0.95, "2027-06-30", "labor-demo", "invariant", "3 quarters",
  "Pure demographic arithmetic: the cohorts already exist and ageing is monotonic.",
  "The single most certain row in the entire buildout. Included precisely BECAUSE it is "
  "near-certain: a book that never logs a 0.95 and never logs a 0.20 has no resolution, which "
  "is exactly what the 9/20 research measured (RES ~0.00).",
  "Ageing is the structural driver under healthcare employment and entitlement spending.")

N("healthcare-jobs", "ld-anchor", "Health care and social assistance is the largest contributor to "
  "payroll growth in a majority of months through Q2 2027", 0.78, "2027-06-30",
  "labor-demo", "invariant", "3 quarters",
  "Downstream of demographic arithmetic and of a funding stream that is statutory. This has "
  "been the dominant contributor for an extended run driven by those two facts.",
  "Invariant-adjacent persistence, mechanistically downstream of the ageing row. Correlation "
  "declared: these are one demographic fact observed twice.",
  "Healthcare job growth is why 'the labour market' and 'the cyclical labour market' diverge.")

N("jolts-openings", "ld-anchor", "JOLTS job openings print below 8.0 million on every release "
  "through Q2 2027", 0.76, "2027-06-30", "labor-demo", "level", "3 quarters",
  "No-view odds off the distance to the threshold on a published monthly series already well "
  "below it; a breach requires a reacceleration outside the recent distribution. The series "
  "has known response-rate quality problems, stated rather than discovered at resolution.",
  "Level row with an explicit data-quality caveat. Naming the measurement weakness up front is "
  "how you avoid the #24 shape (confident number, wrong number).",
  "Openings-to-unemployed is the tightness measure the Fed actually watches.",
  odds={"tool": "range_odds",
        "command": "python tools/range_odds.py --spot 7.2 --hi 8.0 --days 9 --vol 3.5",
        "odds": 0.76,
        "note": "Units millions. ASSUMED spot 7.2m openings and 3.5%/MONTH vol. One period = one "
                "monthly release; 9 releases to Q2 2027."})

N("wage-band", "ld-anchor", "Average hourly earnings y/y prints inside 3.0-5.0% on every release "
  "through Q2 2027", 0.80, "2027-06-30", "labor-demo", "level", "3 quarters",
  "Wide band on a slow-moving y/y series; month-to-month movement outside a 200bp band is rare "
  "absent a definitional change.",
  "Level with a wide band on a y/y series - and the base-effect identity check (13d.2) applies: "
  "the y/y path has a known arithmetic component from the comparison base.",
  "Wages inside the band means the energy shock has not become a wage-price process.",
  odds={"tool": "range_odds",
        "command": "python tools/range_odds.py --spot 3.9 --lo 3.0 --hi 5.0 --days 9 --vol 2.5",
        "odds": 1.0,
        "note": "ASSUMED spot AHE 3.9% y/y and 2.5%/MONTH relative vol (~0.1pp). 9 monthly "
                "releases to Q2 2027."})

N("strike-activity", "ld-anchor", "At least one work stoppage involving 20,000+ workers begins "
  "before end-2027", 0.72, "2027-12-31", "labor-demo", "marker", "5 quarters",
  "Marker with a solid base rate over a five-quarter window given the contract expiry calendar, "
  "which is known in advance.",
  "Marker class with a CALENDRICAL driver: major contract expiries are published, which turns a "
  "labour-relations question into a scheduled-risk question.",
  "Large stoppages are supply-chain events before they are labour events.")

N("federal-workforce", "ld-anchor", "Federal civilian employment ends FY2027 below its FY2025 level",
  0.76, "2027-10-31", "labor-demo", "invariant", "4 quarters",
  "Enacted reductions plus attrition arithmetic; reversing requires new appropriations and "
  "hiring lead time that does not fit the window.",
  "Invariant-adjacent: an enacted reduction plus a known attrition rate. The hiring lead time "
  "is the physical part - even a full policy reversal cannot refill the headcount inside the "
  "window, which is the lead-time argument used throughout this buildout.",
  "Federal employment is a direct, if small, payrolls drag with a known sign.")

N("productivity-band", "ld-anchor", "Nonfarm business productivity growth prints inside 0-4% y/y "
  "on every quarterly release through 2027", 0.82, "2027-12-31", "labor-demo", "level",
  "5 quarters",
  "Wide band on a noisy quarterly series; the band covers essentially the whole plausible "
  "distribution outside a measurement break.",
  "A deliberately easy band, logged at a high probability. Not every row should be hard: the "
  "book needs correctly-stated high-confidence rows to earn resolution, and a row that is "
  "genuinely 0.82 should say 0.82.",
  "Productivity is the only thing that reconciles the AI capex with the wage band.",
  odds={"tool": "range_odds",
        "command": "python tools/range_odds.py --spot 2.0 --hi 4.0 --days 5 --vol 35",
        "odds": 0.74,
        "note": "ONE-SIDED ONLY and that is a tool limitation, not a choice: the row's lower "
                "bound is 0% and a lognormal walk cannot represent a zero bound (range_odds "
                "treats --lo 0 as 'no bound'). ASSUMED spot 2.0% y/y and 35%/QUARTER relative "
                "vol; 5 quarterly releases. The true two-sided odds are LOWER."})

# ══════════════════════════════════════════════════════════════════════════════
# LANE: supply-chains (14) — lead times are the most under-used invariant there is
# ══════════════════════════════════════════════════════════════════════════════
N("sc-anchor", "now", "Supply chains: lead time as the binding constraint", 1.0, "2026-10-01",
  "supply-chains", "invariant", "structural",
  "Anchor. A lead time is a physical fact about how long something takes to build. It is the "
  "single most forecastable object in this entire tree and the book barely uses it.",
  "Lane anchor. The existing tree treats semis purely as a price story (markets-ai) with no "
  "node for the physical constraints that actually set the supply curve.",
  "Lead times decide who can deliver, which decides who gets the revenue.")

N("cowos-bottleneck", "sc-anchor", "Advanced packaging capacity remains the binding constraint on "
  "accelerator shipments through 2027", 0.78, "2027-12-31", "supply-chains", "invariant",
  "5 quarters",
  "Packaging capacity additions are announced years ahead and commission on known schedules; "
  "demand is contracted ahead of it. The gap is arithmetic on both sides.",
  "INVARIANT: two known schedules, one subtraction. This is the row shape that scores 0.10 "
  "Brier, applied to the market the book cares most about.",
  "Packaging, not wafer, is what rations accelerator supply.",
  shifts=[{"target": "nvda-dc-band", "p_to": 0.70, "note": "supply cap sets the revenue ceiling"}])

N("hbm-tight", "sc-anchor", "HBM remains sold out on a forward-year basis at the top two suppliers "
  "through 2027", 0.74, "2027-12-31", "supply-chains", "invariant", "5 quarters",
  "Capacity conversion from commodity DRAM to HBM is physical and slow; forward-year sell-out "
  "has been the reported state and the conversion schedule is public.",
  "Invariant-adjacent. Correlated with the packaging row (both are 'accelerator supply is "
  "capped') — declared, not counted twice.",
  "HBM allocation is the real gating item on accelerator volume.")

N("euv-shipments", "sc-anchor", "EUV systems shipped in 2027 exceed the 2025 total", 0.72,
  "2028-01-31", "supply-chains", "invariant", "6 quarters",
  "Build slots are booked years ahead and the backlog is reported; shipment counts are close "
  "to a production-schedule readout.",
  "Invariant-adjacent with a reported backlog. A booked build slot is capital-committed, which "
  "is the R03 distinction that separates a real signal from an intention.",
  "EUV shipments are the leading indicator of leading-edge wafer capacity two years out.")

N("transformer-sc", "sc-anchor", "Grid equipment remains on allocation at the major OEMs through "
  "2027", 0.80, "2027-12-31", "supply-chains", "invariant", "5 quarters",
  "Same physical constraint as the transformer lead-time row in energy-supply, observed from "
  "the vendor side rather than the buyer side.",
  "Deliberately logged as the SAME fact seen twice, and said so. The reason to log it at all "
  "is that it resolves from a different source; the reason to flag it is #70/#27, where two "
  "views of one bet were counted as two bets.",
  "Allocation means capex budgets do not convert to capacity on schedule.")

N("rare-earth-onshoring", "sc-anchor", "At least one non-Chinese commercial-scale NdFeB magnet "
  "facility reaches production by end-2027", 0.75, "2027-12-31", "supply-chains", "invariant",
  "5 quarters",
  "Projects with committed capital, offtake agreements and construction underway; the schedule "
  "risk is commissioning, not intent.",
  "Invariant class: capital committed plus offtake signed. The distinction from a government "
  "'plan' to onshore, which would be rhetoric and capped, is the entire R03 test.",
  "Magnet supply is the chokepoint in defence and EV drivetrains alike.")

N("panama-transits", "sc-anchor", "Panama Canal daily transit slots stay at or above 30 per day "
  "through 2027", 0.76, "2027-12-31", "supply-chains", "duration", "5 quarters",
  "Duration row governed by Gatun Lake level, i.e. by hydrology. The constraint is physical and "
  "published daily.",
  "Duration + hydrology. The rare case where a logistics constraint is literally a water-level "
  "measurement — checkable, dated, and outside anyone's discretion.",
  "Canal capacity is a direct input to trans-Pacific freight rates.",
  odds={"tool": "cycle_odds",
        "command": "python tools/cycle_odds.py --current 400 --days 465 --prior-median 1000",
        "ends_lo": 0.22, "ends_hi": 0.26,
        "phase_ends": False,
        "note": "ASSUMED: transit slots have been at/above 30/day for ~400d; median length ~1000d "
                "(Gatun Lake hydrology runs on multi-year cycles)."})

N("red-sea-duration", "sc-anchor", "Majority of container capacity still routing via the Cape "
  "rather than Suez on 2027-06-30", 0.76, "2027-06-30", "supply-chains", "duration", "3 quarters",
  "DURATION, explicitly not a direction call on the conflict (16.18 / schema R27). Reroute "
  "decisions are made on insurance and crew-risk terms that lag any de-escalation by months.",
  "[9/22 CORRECTION] cycle_odds.py puts the no-view survival band at 0.79-0.90 and this row was "
  "logged at 0.68, more than 0.10 outside it with no dated catalyst in the basis; re-priced 0.68 "
  "-> 0.76 into the band. The 16.18 construction applied outside the iran-war cluster: price the "
  "CLOCK on the reroute, never the next leg of the conflict. Note the lag mechanism is what makes "
  "it forecastable - shipping normalises slower than diplomacy.",
  "Routing duration, not the shooting, is what sets freight and delivery times.",
  odds={"tool": "cycle_odds",
        "command": "python tools/cycle_odds.py --current 1000 --days 281 --prior-median 540",
        "ends_lo": 0.1, "ends_hi": 0.21,
        "phase_ends": False,
        "note": "ASSUMED: Cape routing has been the majority routing for ~1000d; median length of "
                "a wartime reroute regime ~540d. The memoryless model is doing the work the row's "
                "own basis describes (insurance and crew-risk terms lag de-escalation by months)."})

N("freight-band", "sc-anchor", "Composite container spot freight stays inside a 3x range through "
  "2027", 0.70, "2027-12-31", "supply-chains", "level", "5 quarters",
  "A 3x band sounds wide and is not, for this series - container spot has moved more than 3x "
  "inside a year repeatedly. Priced honestly rather than tightly.",
  "A band chosen to be honest about the volatility of the series rather than to look precise. "
  "The #69 failure was a band that flattered the author.",
  "Freight volatility is the cost-shock channel into goods CPI.",
  odds={"tool": "range_odds",
        "command": "python tools/range_odds.py --spot 2000 --lo 1155 --hi 3465 --days 66 --vol 6.0",
        "odds": 0.54,
        "note": "ASSUMED index level 2000 and 6.0%/WEEK vol. '3x range' read GEOMETRICALLY around "
                "the assumed spot (spot/sqrt(3)=1155 .. spot*sqrt(3)=3465); container spot is a "
                "weekly print, so 66 weekly periods."})

N("container-orderbook", "sc-anchor", "Container fleet capacity grows again in 2027", 0.90,
  "2028-01-31", "supply-chains", "invariant", "6 quarters",
  "Ships delivering in 2027 are already under construction; the orderbook is published. Growth "
  "is arithmetic unless scrapping exceeds deliveries, which has never happened at this ratio.",
  "INVARIANT: steel already being cut. One of the cleanest arithmetic rows available - the "
  "supply of ships two years out is a matter of public record.",
  "A growing fleet is the structural cap on any freight-rate spike.")

N("auto-chip-inventory", "sc-anchor", "No automaker announces a production halt attributed to "
  "semiconductor shortage in Q4 2026", 0.72, "2026-12-31", "supply-chains", "marker", "1 quarter",
  "Marker framed as a NON-event, which makes it falsifiable by a single headline. Mature-node "
  "capacity is in surplus, which is the mechanism.",
  "A negative marker: one contrary headline falsifies it. Rows that are easy to falsify are "
  "worth more than rows that are hard to check - #30 is still 'AMBIGUOUS, leaning HIT' and "
  "needs a human to agree a reading before its horizon.",
  "Mature-node surplus is the forgotten half of the semiconductor story.")

N("semicap-controls", "sc-anchor", "At least one further tightening of semiconductor equipment "
  "export controls is published by end-2027", 0.55, "2027-12-31", "supply-chains", "direction",
  "5 quarters",
  "Discretionary policy. Base rate over five quarters is high given the established cadence, "
  "but cadence-continuation on a policy lever is leg-extrapolation and is capped.",
  "DIRECTION + discretionary + pattern-continuation. Same triple flag as the China rare-earth "
  "row, and priced similarly - consistency between two symmetric rows is itself a check.",
  "Each tightening round pulls forward Chinese domestic substitution.")

N("pharma-api", "sc-anchor", "No US generic injectable shortage list falls below 50 active entries "
  "through 2027", 0.82, "2027-12-31", "supply-chains", "invariant", "5 quarters",
  "Structural: generic injectable economics do not support redundant capacity, so the shortage "
  "list is a stable stock rather than an event.",
  "Invariant-adjacent persistence with an economic mechanism (negative margin, no redundancy). "
  "Published list, unambiguous count, named source - the #59 fix built in.",
  "Drug shortages are a permanent feature of the generic cost structure, not a crisis.")

N("tsmc-az", "sc-anchor", "Arizona-fabricated leading-edge wafers ship in volume to a US customer "
  "by end-2027", 0.78, "2027-12-31", "supply-chains", "invariant", "5 quarters",
  "Capital committed and physical: fabs built, tools installed, on a published construction "
  "schedule. The remaining risk is yield ramp and the definition of 'volume', which is "
  "named here as the soft part rather than left to be argued at resolution.",
  "Invariant with a declared soft threshold. Every row in this buildout that has a fuzzy word "
  "in it says which word is fuzzy - that is the #59 discipline made routine.",
  "Onshored leading-edge supply is the structural answer to the Taiwan tail risk.")

# ══════════════════════════════════════════════════════════════════════════════
# LANE: crypto-digital (10) — protocol rules are the only true invariants here
# ══════════════════════════════════════════════════════════════════════════════
N("cd-anchor", "now", "Crypto & digital assets: protocol arithmetic vs policy discretion", 1.0,
  "2026-10-01", "crypto-digital", "invariant", "structural",
  "Definitional lane label, p=1.0 by construction. The lane splits cleanly into things fixed "
  "by code (certain) and things decided by regulators (capped); almost nothing sits between.",
  "Lane anchor. Useful to the engine mainly as a clean natural experiment: the same lane "
  "contains both the most certain and the least certain row classes it has.",
  "Crypto is where the invariant-versus-discretion distinction is easiest to see.")

N("btc-halving", "cd-anchor", "The next Bitcoin subsidy halving occurs at the scheduled block height",
  0.97, "2028-04-30", "crypto-digital", "invariant", "7 quarters",
  "Protocol arithmetic: the halving is defined by block height, and the date follows from the "
  "difficulty adjustment. The only uncertainty is a few weeks of block-time drift.",
  "The purest INVARIANT in this tree - it is literally a rule in code. Date uncertainty, not "
  "event uncertainty, which is why the row is dated loosely and priced at 0.97.",
  "The halving is the one supply event in any market that is known years ahead to the block.",
  evidence=[{"fact": "Bitcoin's block subsidy halves every 210,000 blocks by protocol rule",
             "reported": "structural"}])

N("btc-drawdown", "cd-anchor", "Bitcoin records a peak-to-trough drawdown of at least 30% inside "
  "any 12-month window ending 2027-12-31", 0.78, "2027-12-31", "crypto-digital", "invariant",
  "5 quarters",
  "Base rate from the asset's own realised volatility: a 30% drawdown inside a year has "
  "occurred in the large majority of years in its history, including bull years.",
  "A volatility row, not a direction row. This is the right way to express a crypto view: the "
  "distribution is knowable even though the direction is not. Directly parallel to 16.18.",
  "A 30% drawdown is normal, not a signal - which is the whole point of logging it.")

N("stablecoin-supply", "cd-anchor", "Aggregate stablecoin supply ends 2027 above its end-2026 level",
  0.6, "2027-12-31", "crypto-digital", "level", "5 quarters",
  "Persistence of a published, daily-observable stock with a genuine transactional use case. "
  "Reference class: annual changes in the aggregate since the instrument became systemically "
  "used. The main downside risk is a regulatory break, which is a separate capped row.",
  "[9/22 CORRECTION] range_odds.py puts the no-view odds at 0.50 and this row was logged at 0.74, "
  "+0.24 off it with no dated catalyst in the basis; re-priced 0.74 -> 0.60 toward the "
  "arithmetic. 'A driftless year ends above where it started' is 0.50 by construction; anything "
  "above that was drift smuggled in as persistence. Level with the regulatory tail split out into "
  "its own node rather than bundled in. Bundling them would be the #63 conjunction error in "
  "reverse.",
  "Stablecoin supply is now a real bid for T-bills and belongs in the rates conversation.",
  shifts=[{"target": "bill-share-high", "p_to": 0.85, "note": "stablecoin reserves buy bills"}],
  odds={"tool": "range_odds",
        "command": "python tools/range_odds.py --spot 300 --lo 300 --days 1 --vol 35",
        "odds": 0.5,
        "note": "Units $bn. TERMINAL claim: end-2027 above the END-2026 level, so the starting "
                "point IS the threshold and the level cancels - only the one-year vol matters "
                "(ASSUMED 35%). ONE period = the year 2027. The no-view answer for 'a driftless "
                "year ends above where it started' is 0.50 by construction."})

N("tokenized-treasuries", "cd-anchor", "Tokenised Treasury products end 2027 above $10bn in "
  "aggregate", 0.4, "2027-12-31", "crypto-digital", "level", "5 quarters",
  "Growth from a base with institutional sponsorship; priced at the non-invariant ceiling and "
  "no higher because adoption curves are behavioural.",
  "[9/22 CORRECTION] range_odds.py puts the no-view odds at 0.31 and this row was logged at 0.70, "
  "+0.39 off it with no dated catalyst in the basis; re-priced 0.70 -> 0.40 toward the "
  "arithmetic. A driftless walk is the wrong generative model for an adoption stock, and that is "
  "exactly why the rule demands a DATED catalyst instead of a growth story - none is in hand. "
  "Level row at the R13 ceiling. Adoption-curve extrapolation is a close cousin of "
  "leg-extrapolation and deserves the same suspicion.",
  "Tokenised bills are the actual bridge between the two systems.",
  odds={"tool": "range_odds",
        "command": "python tools/range_odds.py --spot 7.5 --lo 10 --days 1 --vol 60",
        "odds": 0.31,
        "note": "Units $bn. TERMINAL claim, so one period = the whole 5-quarter horizon. ASSUMED "
                "spot $7.5bn and 60% horizon vol. A driftless walk is the WRONG generative model "
                "for an adoption stock that has grown monotonically - stated, because the no-view "
                "number is the reference class, not the forecast."})

N("crypto-market-structure", "cd-anchor", "US comprehensive crypto market-structure legislation is "
  "enacted by end-2027", 0.38, "2027-12-31", "crypto-digital", "direction", "5 quarters",
  "Legislative base rate: comprehensive bills in any contested area fail far more often than "
  "they pass, across multiple congresses. Priced below even on the outside view.",
  "Priced LOW and deliberately so. The outside view on 'comprehensive legislation passes' is "
  "unkind, and R26 says you need a dated datapoint the reference lacks to diverge from it. "
  "There isn't one, so the row sits at the base rate.",
  "Legislation, not enforcement, is what changes the institutional cost of holding these.")

N("cbdc-ban", "cd-anchor", "No US retail central bank digital currency is launched before 2029",
  0.92, "2028-12-31", "crypto-digital", "invariant", "9 quarters",
  "Near-invariant: a retail CBDC requires legislation that does not exist plus a build that "
  "would take years after it. The lead time alone almost settles it.",
  "A lead-time invariant: even with a decision today, the BUILD does not fit in the window. "
  "This is the most under-used argument form in forecasting and the book should use it more.",
  "The absence of a CBDC keeps stablecoins as the default digital dollar.")

N("exchange-failure", "cd-anchor", "At least one centralised venue with over $1bn in customer "
  "assets fails or freezes withdrawals before end-2027", 0.55, "2027-12-31", "crypto-digital",
  "marker", "5 quarters",
  "Marker with a historical base rate that is uncomfortably high across five-quarter windows, "
  "offset by a materially improved regulatory perimeter.",
  "Marker priced at the base rate with the two offsetting forces named. When the forces offset, "
  "the honest number is near the base rate - not a dramatic one in either direction.",
  "Venue failure is the recurring mechanism by which crypto transmits to nothing else.")

N("eth-staking", "cd-anchor", "Ether staking ratio stays above 25% through 2027", 0.84,
  "2027-12-31", "crypto-digital", "invariant", "5 quarters",
  "Protocol-constrained: the exit queue rate-limits unstaking by design, so a large fall inside "
  "the window is mechanically impossible.",
  "INVARIANT via a protocol rate limit - the queue makes the claim about arithmetic rather than "
  "sentiment. Structurally identical to the interconnection-queue row in energy-supply.",
  "The exit queue is a real, coded constraint on supply behaviour.")

N("hashprice-floor", "cd-anchor", "Network hashrate ends 2027 above its end-2026 level", 0.80,
  "2027-12-31", "crypto-digital", "invariant", "5 quarters",
  "Machines already ordered and sited will come online regardless of price over this horizon; "
  "the installed base grows on a known schedule.",
  "Invariant-adjacent: deployment is capital already committed. Hashrate is the physical "
  "footprint of decisions taken 12-18 months ago.",
  "Hashrate growth is a genuine, if odd, read on cheap-power availability.")

# ══════════════════════════════════════════════════════════════════════════════
# LANE: health-bio (10) — patent cliffs and statutory calendars are arithmetic
# ══════════════════════════════════════════════════════════════════════════════
N("hb-anchor", "now", "Health & bio: statutory calendars and patent arithmetic", 1.0, "2026-10-01",
  "health-bio", "invariant", "structural",
  "Anchor. Patent expiries and statutory negotiation rounds are dated years ahead by law, which "
  "makes this lane unusually rich in invariant rows.",
  "Lane anchor. Healthcare is ~18% of the economy and has zero nodes in the existing tree - the "
  "largest single coverage hole found.",
  "Healthcare is the biggest sector nobody in this book has priced.")

N("medicare-round2", "hb-anchor", "Second-round Medicare negotiated prices take effect on the "
  "statutory date", 0.88, "2027-01-01", "health-bio", "invariant", "1 quarter",
  "The effective date is written into statute and the selected-drug list is already published. "
  "Residual risk is litigation, which is a separate row.",
  "INVARIANT: a statutory effective date plus an already-published selected-drug list. The "
  "litigation risk is split into its own node rather than bundled in, because a row that "
  "needs BOTH the date to hold AND the courts to stay out is a conjunction, and conjunctions "
  "are where #63 and #39 died.",
  "Negotiated prices are a direct, dated hit to a known set of revenue lines.",
  shifts=[{"target": "pharma-litigation", "p_to": 0.55, "note": "effective date triggers the suits"}])

N("biosimilar-cliff", "hb-anchor", "Aggregate US biologic revenue exposed to loss of exclusivity "
  "in 2027 exceeds the 2026 figure", 0.82, "2027-12-31", "health-bio", "invariant", "5 quarters",
  "Patent expiry arithmetic. Which molecules lose exclusivity in which year is a matter of "
  "public record today.",
  "INVARIANT - the patent calendar is the single most forecastable revenue schedule in any "
  "industry, and the book has never used it.",
  "The cliff is the structural reason large-cap pharma must keep buying growth.")

N("pharma-litigation", "hb-anchor", "At least one manufacturer challenge to the negotiation "
  "programme remains live in the appellate courts on 2027-12-31", 0.70, "2027-12-31",
  "health-bio", "duration", "5 quarters",
  "Duration row governed by appellate timelines, which run in years and are largely independent "
  "of merits.",
  "Duration class driven by COURT CALENDARS, which are institutional clocks. Pricing the clock "
  "rather than the verdict is the 16.18 move applied to litigation.",
  "The litigation clock, not its outcome, is what matters for the revenue schedule.",
  odds={"tool": "cycle_odds",
        "command": "python tools/cycle_odds.py --current 700 --days 465 --prior-median 900",
        "ends_lo": 0.17, "ends_hi": 0.26,
        "phase_ends": False,
        "note": "ASSUMED: at least one manufacturer challenge has been live ~700d; median time "
                "for such a challenge to exhaust appellate review ~900d."})

N("pdufa-count", "hb-anchor", "At least 35 novel drug approvals are recorded for calendar 2027",
  0.68, "2028-01-31", "health-bio", "scheduled", "6 quarters",
  "The PDUFA action-date calendar is set per application and largely published; the count is "
  "close to arithmetic with an approval-rate distribution on top.",
  "Scheduled with an arithmetic backbone: the DENOMINATOR (applications with action dates) is "
  "known, only the hit rate is uncertain. That is the strongest available structure.",
  "Approval counts set the sector's growth narrative for the following year.")

N("glp1-supply", "hb-anchor", "No GLP-1 product appears on the FDA drug shortage list on "
  "2027-06-30", 0.66, "2027-06-30", "health-bio", "marker", "3 quarters",
  "Marker on a published list. Capacity additions are capital-committed and commissioning; "
  "demand growth is the offsetting unknown.",
  "Marker with a named, published resolution source. Two capital-committed forces in opposition "
  "again, so the honest price is mid.",
  "Shortage status is the cleanest single read on whether capacity has caught demand.")

N("obesity-coverage", "hb-anchor", "Medicare Part D coverage for obesity indications remains "
  "restricted through 2027", 0.8, "2027-12-31", "health-bio", "duration", "5 quarters",
  "Duration. Changing it requires either legislation or a rulemaking with a budget score, both "
  "of which have known multi-quarter clocks.",
  "[9/22 CORRECTION] cycle_odds.py puts the no-view survival band at 0.86-0.90 and this row was "
  "logged at 0.72, more than 0.10 outside it with no dated catalyst in the basis; re-priced 0.72 "
  "-> 0.80 into the band. Duration governed by a PROCESS clock (rulemaking + scoring), not by "
  "anyone's preference. Process clocks are the most reliable objects in policy forecasting.",
  "Coverage is the single biggest swing factor in the category's addressable market.",
  odds={"tool": "cycle_odds",
        "command": "python tools/cycle_odds.py --current 1500 --days 465 --prior-median 1800",
        "ends_lo": 0.1, "ends_hi": 0.14,
        "phase_ends": False,
        "note": "ASSUMED: the Part D obesity-coverage restriction is ~1500d old in its current "
                "form; median length of a coverage restriction that needs legislation or a scored "
                "rulemaking to change ~1800d."})

N("h5n1-marker", "hb-anchor", "No sustained human-to-human transmission of H5N1 is confirmed by "
  "WHO before 2028", 0.84, "2028-01-31", "health-bio", "marker", "5 quarters",
  "Base rate: despite decades of spillover events, sustained human transmission has not been "
  "confirmed. Priced high on the outside view, with the tail explicitly acknowledged. Bound "
  "DOWN from 0.88 by this buildout's own p>=0.85-needs-invariant rule: a base rate, however "
  "long, is not a physical constraint.",
  "A NEGATIVE marker with a high probability and a real tail. Note the structure: this is how "
  "you log a catastrophic tail honestly - as a high-probability negative, not as a low-"
  "probability scare row that inflates the book's apparent boldness.",
  "The tail is small and the consequence is unbounded; that asymmetry is the whole content.")

N("nih-funding", "hb-anchor", "NIH enacted appropriations for FY2027 come in below the FY2025 "
  "level in nominal terms", 0.55, "2027-12-31", "health-bio", "direction", "5 quarters",
  "Appropriations are a discretionary legislative outcome - capped. Enacted outcomes have "
  "historically diverged sharply from proposed levels in both directions.",
  "DIRECTION + legislative discretion, capped at 0.55, and explicitly noting that PROPOSED "
  "budgets are rhetoric while ENACTED ones are capital-committed. Confusing the two is the "
  "#72 error transplanted into fiscal policy.",
  "Research funding is a multi-year input to the approval-count row.")

N("amr-marker", "hb-anchor", "At least one new antibiotic class receives FDA approval by end-2028",
  0.42, "2028-12-31", "health-bio", "marker", "9 quarters",
  "Low base rate: genuinely new classes are rare, and the economic model for antibiotics "
  "discourages development. Priced below even on the outside view.",
  "Another deliberately low row. The book needs rows it expects to LOSE in order to have "
  "resolution at all; a 0.42 that resolves MISS is a correctly calibrated row, not a failure.",
  "The pipeline gap here is a slow-moving structural risk with no market price.")

# ══════════════════════════════════════════════════════════════════════════════
# LANE: climate-physical (10) — rule-triggered thresholds are hidden invariants
# ══════════════════════════════════════════════════════════════════════════════
N("cp-anchor", "now", "Climate & physical risk: rule-triggered thresholds", 1.0, "2026-10-01",
  "climate-physical", "invariant", "structural",
  "Anchor. Several physical-risk outcomes are triggered by published rules on measured levels, "
  "which converts a weather question into an arithmetic one.",
  "Lane anchor. The interesting insight here is that much of climate policy is RULE-TRIGGERED: "
  "if the measurement hits X the declaration follows automatically. That is an invariant "
  "hiding inside what looks like a forecast.",
  "Physical risk is a supply shock with a known transmission path.")

N("colorado-tier", "cp-anchor", "A Lower Basin shortage condition is declared for calendar 2027",
  0.80, "2026-12-31", "climate-physical", "invariant", "1 quarter",
  "RULE-TRIGGERED: the shortage tier is set by a published projection of Lake Mead elevation on "
  "a fixed date under an existing operating agreement. Given current elevations, the trigger is "
  "close to arithmetic.",
  "The best example in this buildout of a hidden invariant: this looks like a hydrology forecast "
  "and is actually a threshold rule applied to a measurement. Find more of these.",
  "Water allocation is a hard input to agriculture and to southwestern power.")

N("reinsurance-jan1", "cp-anchor", "January 1 reinsurance renewals complete", 0.96, "2027-01-01",
  "climate-physical", "scheduled", "1 quarter",
  "A fixed annual market event on an institutional calendar: the renewal happens every January 1 without exception, and only the pricing is unknown.",
  "Scheduled EVENT separated from its price. This split - event certain, value uncertain - is "
  "the structure the book scores 12/14 on.",
  "The Jan 1 renewal sets the year's capacity and therefore the cost of physical risk.",
  kind="checkpoint",
  shifts=[{"target": "insured-loss", "p_to": 0.72, "note": "capacity terms set retention levels"}])

N("insured-loss", "cp-anchor", "Global insured natural catastrophe losses for 2026 are reported "
  "above $100bn", 0.72, "2027-04-30", "climate-physical", "invariant", "2 quarters",
  "Base rate: the $100bn threshold has been exceeded in most recent years, and most of the "
  "year's events have already occurred by the time this is logged.",
  "Invariant-adjacent because the year is nearly complete - most of the outcome is already "
  "determined and merely unreported. A retrospective-arithmetic row.",
  "Insured losses are the price signal that transmits physical risk into capital costs.")

N("atlantic-season-2027", "cp-anchor", "The 2027 Atlantic hurricane season produces at least 12 "
  "named storms", 0.72, "2027-11-30", "climate-physical", "scheduled", "4 quarters",
  "Base rate against the recent climatological mean, which sits above 12; the ENSO state row is "
  "the main conditioning variable.",
  "Scheduled season with a base-rate value, explicitly conditioned on the ENSO row rather than "
  "quietly assuming it. Declaring the conditioning variable is what stops two rows from being "
  "one row.",
  "Named-storm counts drive the reinsurance cycle more than landfall does.")

N("texas-grid-alert", "cp-anchor", "ERCOT issues at least one conservation appeal or emergency "
  "notice before end-2027", 0.82, "2027-12-31", "climate-physical", "marker", "5 quarters",
  "Marker with a very strong base rate: appeals have been issued in essentially every recent "
  "year given the reserve-margin structure and load growth.",
  "Marker with a structural driver (thin reserve margin plus datacenter load) rather than a "
  "weather guess. The mechanism is the energy-supply lane's load-growth invariant.",
  "Grid stress in the largest load-growth market is the leading indicator for the rest.")

N("california-water", "cp-anchor", "California statewide snowpack peaks below 110% of average in "
  "2027", 0.70, "2027-05-31", "climate-physical", "scheduled", "3 quarters",
  "Measured on a fixed survey calendar; the base rate of a below-110% peak is comfortably above "
  "even across the historical record.",
  "Scheduled measurement with a base-rate value and a NAMED survey as the resolution source. Naming the survey is the #59 fix: that row was scored against the engine only because nobody had written down which measurement counted.",
  "Snowpack is the hydro and agricultural input for the whole western US.")

N("arctic-minimum", "cp-anchor", "The 2027 Arctic sea-ice minimum comes in below the 1981-2010 "
  "average", 0.96, "2027-10-31", "climate-physical", "invariant", "4 quarters",
  "Every minimum in the modern satellite record for decades has been below that baseline; the "
  "trend is monotonic on this horizon.",
  "Near-invariant from an unbroken record. Logged at 0.96 without apology - the book needs "
  "correctly-stated near-certainties to earn resolution.",
  "Arctic routing and methane feedback are slow but the measurement is annual and clean.")

N("european-heat-power", "cp-anchor", "At least one European country issues a heat-related power "
  "or water restriction in summer 2027", 0.82, "2027-09-30", "climate-physical", "marker",
  "4 quarters",
  "Marker with a strong recent base rate driven by nuclear cooling constraints and hydro levels "
  "— both physical.",
  "Marker with a physical mechanism (thermal plant cooling limits), not a temperature forecast. "
  "The restriction is triggered by measured river temperature, another rule-triggered invariant.",
  "Cooling constraints are why a European heatwave is a power-price event.")

N("crop-insurance", "cp-anchor", "US crop insurance indemnities for 2026 are reported above $10bn",
  0.74, "2027-06-30", "climate-physical", "invariant", "3 quarters",
  "Retrospective arithmetic: the crop year is essentially complete, so this is a reporting-lag "
  "row rather than a forecast.",
  "Retrospective-arithmetic class, same as the insured-loss row. Rows about facts that have "
  "already happened but have not yet been published are systematically under-used.",
  "Indemnities are the fiscal transmission of physical risk into the farm economy.")

# ══════════════════════════════════════════════════════════════════════════════
# LANE: defense-industrial (12) — backlog is the most honest number in the sector
# ══════════════════════════════════════════════════════════════════════════════
N("di-anchor", "now", "Defence industrial base: backlog, not budget", 1.0, "2026-10-01",
  "defense-industrial", "invariant", "structural",
  "Anchor. Backlog is signed contracts - capital committed. Budget requests are intentions. The "
  "book's #3 row (Pentagon ~$1.5T FY27) is tracking MISS precisely for confusing the two.",
  "Lane anchor, and an explicit correction of the #3 error: nothing enacted by the horizon = "
  "MISS. Rows here are built on signed backlog rather than proposed toplines.",
  "Backlog converts to revenue on a schedule; a budget request converts to nothing.", ledger=[3])

N("ndaa-fy27", "di-anchor", "An FY2027 National Defense Authorization Act is enacted", 0.92,
  "2027-03-31", "defense-industrial", "invariant", "2 quarters",
  "Institutional base rate of exceptional strength: an NDAA has been enacted every single year "
  "for over six decades, through shutdowns, impeachments and divided government.",
  "This is the strongest INSTITUTIONAL invariant available in US politics, and the book has "
  "never used it. An unbroken 60+ year run is a different object from a policy preference. "
  "Note it authorises; it does not appropriate - so it does not rescue #3.",
  "The NDAA is the authorisation floor; appropriations are the separate, failing question.",
  kind="checkpoint",
  shifts=[{"target": "defense-backlog", "p_to": 0.88, "note": "authorisation feeds new starts"},
          {"target": "munitions-rate", "p_to": 0.80, "note": "multiyear procurement authority"}])

N("defense-backlog", "di-anchor", "Aggregate reported backlog at the top five US primes sets a "
  "record at the next annual reporting", 0.88, "2027-02-28", "defense-industrial", "invariant",
  "2 quarters",
  "Arithmetic on signed contracts: backlog rises when bookings exceed revenue, and the book-to-"
  "bill has been above one on a war footing with European budgets enacted.",
  "INVARIANT - backlog is an audited number about contracts already signed. This is the correct "
  "replacement for the #3 style of defence row.",
  "Record backlog with flat deliveries is the throughput problem, not a demand problem.")

N("munitions-rate", "di-anchor", "Monthly 155mm artillery production capacity exceeds 90,000 "
  "rounds by end-2027", 0.70, "2027-12-31", "defense-industrial", "invariant", "5 quarters",
  "Facilities are funded and under construction with published milestones; the residual risk is "
  "commissioning and workforce, both of which have slipped before.",
  "Invariant with a real execution-risk discount. Capped at 0.70 rather than pushed higher "
  "because defence production ramps have a documented history of slipping.",
  "Munitions throughput is the physical constraint on any sustained conflict.")

N("shipbuilding-delay", "di-anchor", "At least one major US Navy shipbuilding programme reports a "
  "further schedule slip before end-2027", 0.88, "2027-12-31", "defense-industrial", "invariant",
  "5 quarters",
  "Base rate approaching certainty: workforce and supplier-base constraints have produced slips "
  "in essentially every recent reporting cycle across multiple programmes.",
  "Invariant-adjacent from an almost unbroken base rate. Cynical, high-probability and correct "
  "is worth more to a book's resolution than optimistic and interesting.",
  "Shipbuilding is where the industrial base constraint is most visible and least fixable.")

N("f35-deliveries", "di-anchor", "F-35 deliveries for 2027 exceed the 2026 total", 0.62,
  "2028-01-31", "defense-industrial", "scheduled", "6 quarters",
  "Scheduled annual reporting; the value depends on software acceptance milestones that have "
  "repeatedly slipped. Priced mid on that record.",
  "Scheduled with an honest mid probability. The temptation is to price the production-rate "
  "arithmetic at 0.8 and ignore the acceptance gate - which is the #24 shape (clean model, "
  "wrong binding constraint).",
  "Deliveries are the revenue-recognition event, not production.")

N("nato-2pct-count", "di-anchor", "At least 24 NATO members are reported at or above 2% of GDP for "
  "2026", 0.78, "2027-06-30", "defense-industrial", "invariant", "3 quarters",
  "Enacted budgets for the reporting year; this is a count of decisions already taken, published "
  "on a fixed annual cycle.",
  "Invariant. Correlated with the europe lane's defence row - the same enacted budgets counted "
  "against a different threshold. Declared, not double-counted.",
  "The count is the demand signal European primes book against.")

N("army-recruiting", "di-anchor", "US Army meets or exceeds its FY2027 recruiting goal", 0.58,
  "2027-10-31", "defense-industrial", "scheduled", "4 quarters",
  "Scheduled annual outcome against a goal the service itself sets - which makes it partly a "
  "definitional choice. Priced near even and the definitional issue is stated.",
  "A row where the TARGET is set by the same party being measured. That is a scoring hazard, "
  "not a forecasting one, and it is named here rather than discovered at resolution (#59).",
  "Recruiting is the binding constraint on force structure, ahead of equipment.")

N("drone-procurement", "di-anchor", "A US programme of record for attritable uncrewed aircraft "
  "awards a production contract above $500m by end-2027", 0.66, "2027-12-31",
  "defense-industrial", "marker", "5 quarters",
  "Marker on a contract award - an observable, dated, capital-committed action. Programme "
  "restructuring is the main risk.",
  "Marker on a CONTRACT AWARD, which is the cleanest possible capital-committed signal (R03). "
  "Far better than a row about doctrine or intent.",
  "The award is where drone rhetoric becomes an industrial fact.")

N("golden-dome", "di-anchor", "Homeland missile-defence architecture receives appropriated funding "
  "above $10bn in a single fiscal year by FY2028", 0.52, "2028-09-30", "defense-industrial",
  "direction", "8 quarters",
  "Appropriations are a legislative discretionary outcome - capped. Priced near even given the "
  "gap between announced ambition and enacted dollars, which is the #3 lesson.",
  "DIRECTION + appropriations discretion. Explicitly the #3 shape, priced the way #3 should "
  "have been: near even, with the rule that nothing enacted by the horizon is a MISS.",
  "Appropriated dollars, not announcements, are what the primes can build against.")

N("japan-defense-budget", "di-anchor", "Japan's enacted FY2027 defence budget exceeds its FY2026 "
  "level in nominal terms", 0.84, "2027-04-30", "defense-industrial", "invariant", "2 quarters",
  "Multi-year build-up plan already legislated with an annual path; the nominal comparison is "
  "arithmetic against a legislated baseline.",
  "Invariant via a legislated multi-year path - the same structure as the German fiscal row. "
  "Legislated paths are the most reliable political objects available.",
  "Japanese procurement is the second-largest new demand pool after Europe.")

N("space-launch-cadence", "di-anchor", "Global orbital launch attempts in 2027 exceed the 2026 "
  "total", 0.82, "2028-01-31", "defense-industrial", "invariant", "6 quarters",
  "Manifest arithmetic: vehicles, pads and payloads for the following year are largely known, "
  "and the cadence trend has been monotonic for a decade.",
  "Invariant-adjacent from a published manifest plus an unbroken trend. Two independent "
  "supports, which is what R23's multi-lens requirement is really asking for.",
  "Launch cadence is the physical throughput of the whole space-and-ISR build-out.")

# ══════════════════════════════════════════════════════════════════════════════
# LANE: latam-emerging (8)
# ══════════════════════════════════════════════════════════════════════════════
N("em-anchor", "now", "Latin America & emerging markets: the external-funding clock", 1.0,
  "2026-10-01", "latam-emerging", "invariant", "structural",
  "Anchor. EM outcomes on this horizon are dominated by an external funding cost the rates-"
  "credit lane already prices, plus amortisation schedules that are published.",
  "Lane anchor. EM rows are mostly downstream of the US rates lane - which makes them a good "
  "test of whether this tree's causal wiring actually works.",
  "A 4% 10y and a strong dollar is the EM constraint, whatever local politics does.")

N("argentina-reserves", "em-anchor", "Argentina's gross international reserves stay above $20bn on "
  "every month-end through 2027", 0.78, "2027-12-31", "latam-emerging", "level", "5 quarters",
  "Level on a published monthly series. Priced near even: the amortisation schedule is known "
  "but the financing source is discretionary.",
  "[9/22 CORRECTION] range_odds.py puts the no-view odds at 0.94 and this row was logged at 0.60, "
  "-0.34 off it with no dated catalyst in the basis; re-priced 0.60 -> 0.78 toward the "
  "arithmetic. Level row where the numerator is arithmetic (payments due) and the denominator is "
  "discretionary (who funds it). Splitting the two is why this is 0.60 and not a story.",
  "Reserves are the only Argentine number that binds.",
  odds={"tool": "range_odds",
        "command": "python tools/range_odds.py --spot 30 --lo 20 --days 15 --vol 6.0",
        "odds": 0.94,
        "note": "Units $bn. ASSUMED spot $30bn gross reserves and 6%/MONTH vol. The row resolves "
                "on MONTH-END prints, so one period = one month; 15 months to end-2027."})

N("brazil-selic", "em-anchor", "Brazil's Selic rate is below its current level on 2027-06-30",
  0.55, "2027-06-30", "latam-emerging", "direction", "3 quarters",
  "Central-bank discretion - capped at 0.55 regardless of how strong the disinflation case "
  "looks. The #26 class.",
  "DIRECTION + committee discretion, capped. Included as a second live test of the cap on a "
  "committee that is far more rules-driven than the Fed - if these systematically HIT at 0.55, "
  "that is evidence to relax R13 for inflation-targeting EM central banks specifically.",
  "The Selic path is the EM carry trade's engine.")

N("mexico-nearshoring", "em-anchor", "Mexican manufacturing FDI for 2026 is reported above the "
  "2023 level", 0.68, "2027-06-30", "latam-emerging", "scheduled", "3 quarters",
  "Scheduled annual reporting; announced projects are partly capital-committed but reported FDI "
  "lags announcements by years and is revised.",
  "Scheduled with a known data-quality problem (revisions), stated. A row whose main risk is "
  "measurement rather than the world is a different animal and should say so.",
  "Nearshoring FDI is the real test of whether tariff policy relocated anything.")

N("turkey-inflation", "em-anchor", "Turkish annual CPI stays above 15% on every print through 2027",
  0.76, "2027-12-31", "latam-emerging", "duration", "5 quarters",
  "Duration row. Disinflation from very high levels is slow and arithmetic - base effects "
  "dominate and the path is largely mechanical over five quarters.",
  "Duration + base-effect arithmetic (13d.2 used correctly). The y/y path from a high base has "
  "a computable floor: the prints already in the comparison window mechanically bound how far "
  "the annual rate can fall, whatever policy does next.",
  "Turkish CPI is the cleanest test of whether orthodox policy is being sustained.",
  odds={"tool": "cycle_odds",
        "command": "python tools/cycle_odds.py --current 1800 --days 465 --prior-median 1500",
        "ends_lo": 0.09, "ends_hi": 0.15,
        "phase_ends": False,
        "note": "ASSUMED: Turkish CPI has been above 15% for ~1800d; median length of an "
                "above-15% inflation spell ~1500d."})

N("india-growth", "em-anchor", "India reports real GDP growth above 5.5% for FY2027", 0.74,
  "2027-12-31", "latam-emerging", "scheduled", "5 quarters",
  "Scheduled official reporting; the growth floor is supported by a public capex programme that "
  "is budgeted and therefore partly capital-committed.",
  "Scheduled with a capital-committed support. Note the methodology caveat: this series has "
  "known measurement debates, which is a resolution-source risk and is named.",
  "India is the marginal demand growth in the commodity complex.")

N("indonesia-nickel", "em-anchor", "Indonesia remains above 50% of global refined nickel supply "
  "through 2027", 0.88, "2027-12-31", "latam-emerging", "invariant", "5 quarters",
  "Installed smelter capacity is built; no competing capacity of that scale exists or is under "
  "construction anywhere else.",
  "INVARIANT - concentration backed by physical plant that is already built. Same structure as the tin row and just as reliable: the denominator moves at the speed of smelter construction, which is years, and no competing capacity of that scale exists anywhere.",
  "Nickel concentration is a single-country chokepoint in battery supply.")

N("em-restructuring-count", "em-anchor", "At least one additional sovereign enters or completes a "
  "debt restructuring before end-2027", 0.70, "2027-12-31", "latam-emerging", "marker",
  "5 quarters",
  "Marker with a base rate driven by the amortisation calendar plus refinancing cost; both "
  "inputs are published.",
  "Marker driven by a published amortisation calendar - the EM version of the refi-wall row. "
  "The calendar is the invariant; the default is the uncertain part.",
  "Restructurings are the transmission of the US rate into the poorest balance sheets.")

# ══════════════════════════════════════════════════════════════════════════════
# LANE: japan-korea (8)
# ══════════════════════════════════════════════════════════════════════════════
N("jk-anchor", "now", "Japan & Korea: the last carry trade and the memory cycle", 1.0,
  "2026-10-01", "japan-korea", "invariant", "structural",
  "Anchor. Two economies that transmit globally through very specific channels - JGB yields "
  "into global duration, Korean exports into the semiconductor cycle.",
  "Lane anchor. Korea's 20-day export data is the single highest-frequency read on the "
  "semiconductor cycle available anywhere, and the tree does not use it.",
  "Korean exports lead the semis tape; JGBs lead global duration.")

N("boj-dec-meeting", "jk-anchor", "Bank of Japan policy meeting", 0.98, "2026-12-19",
  "japan-korea", "invariant", "13 weeks",
  "Published meeting calendar, institutional certainty.",
  "Invariant EVENT with the decision split into its own capped row - the standard central-bank "
  "construction this buildout uses everywhere, and the direct lesson of #26: the meeting is "
  "a calendar fact, the decision is a committee choice, and pricing them together is how a "
  "0.80 becomes a 0.64.",
  "The meeting date is the yen vol event.", kind="checkpoint",
  shifts=[{"target": "boj-hike", "p_to": 0.55, "note": "policy resolves here"},
          {"target": "jgb-band", "p_to": 0.70, "note": "yield curve guidance"}])

N("boj-hike", "boj-dec-meeting", "BoJ raises its policy rate at the December meeting", 0.45,
  "2026-12-19", "japan-korea", "direction", "13 weeks",
  "Committee discretion - capped, and priced below the cap because a single-meeting hike call "
  "is a tighter claim than a within-window one.",
  "DIRECTION + committee, at a SINGLE meeting. Note the structure: a one-meeting call is "
  "strictly harder than a within-window call, and must be priced lower. The #26 row failed "
  "partly because a window claim was reasoned about as if it were a meeting claim.",
  "A BoJ hike is the carry-unwind trigger for global duration.")

N("jgb-band", "jk-anchor", "10y JGB yield stays inside 0.5-3.0% on every close through 2027",
  0.84, "2027-12-31", "japan-korea", "level", "5 quarters",
  "Wide band. The BoJ's balance sheet dominance makes the upper bound an institutional "
  "constraint rather than a market one.",
  "Level with an institutional backstop doing the work - same structure as the BTP row. Wide "
  "bands with a named defender are the highest-quality level rows available.",
  "A JGB break is the fastest route to a global duration event.",
  odds={"tool": "range_odds",
        "command": "python tools/range_odds.py --spot 1.75 --lo 0.5 --hi 3.0 --days 320 --vol 2.0",
        "odds": 0.88,
        "note": "ASSUMED spot 10y JGB 1.75% and 2.0%/day relative vol (~3bp/day). 320 sessions to "
                "end-2027."})

N("yen-band", "jk-anchor", "USDJPY trades inside 120-185 on every close through 2027", 0.82,
  "2027-12-31", "japan-korea", "level", "5 quarters",
  "Very wide band with a demonstrated intervention reaction function at the weak end.",
  "Level row, one cross, wide band, with the policy reaction function named as the mechanism. "
  "Not a direction call on the yen, which is where everyone loses money.",
  "Intervention is the asymmetric force; the band captures it without calling the direction.",
  odds={"tool": "range_odds",
        "command": "python tools/range_odds.py --spot 150 --lo 120 --hi 185 --days 320 --vol 0.55",
        "odds": 0.95,
        "note": "ASSUMED spot USDJPY 150 and 0.55%/day (~9% annualised). 320 sessions to "
                "end-2027."})

N("korea-exports", "jk-anchor", "Korean semiconductor exports post y/y growth in a majority of "
  "months through Q2 2027", 0.72, "2027-06-30", "japan-korea", "scheduled", "3 quarters",
  "Twice-monthly published series with a very short lag. Growth is supported by contracted HBM "
  "demand; the base effect is the offsetting arithmetic.",
  "Scheduled, high-frequency, short-lag, and cross-checkable against the supply-chain lane. "
  "The 20-day series is the closest thing this engine has to a real-time semiconductor read.",
  "Korean exports lead reported semiconductor revenue by roughly a quarter.",
  shifts=[{"target": "nvda-dc-band", "p_to": 0.70, "note": "export data leads reported revenue"}])

N("shunto-2027", "jk-anchor", "The 2027 shunto first-round tally reports average wage gains above "
  "4%", 0.66, "2027-03-31", "japan-korea", "scheduled", "2 quarters",
  "Annual spring wage round with a fixed reporting calendar; recent rounds have cleared 4% but "
  "the outcome is a negotiated aggregate.",
  "Scheduled annual event with a negotiated value - so the EVENT is certain and the number is "
  "capped. The shunto is the BoJ's own stated precondition, which makes this row upstream of "
  "the hike row rather than independent of it. Declared.",
  "Shunto is the wage data the BoJ has said it is waiting for.",
  shifts=[{"target": "boj-hike", "p_to": 0.55, "note": "the stated precondition resolves"}])

N("korea-china-exposure", "jk-anchor", "China's share of Korean exports stays below 25% through "
  "2027", 0.78, "2027-12-31", "japan-korea", "invariant", "5 quarters",
  "Sunk-capital arithmetic: the rerouting is already realised in the published trade data, and "
  "relocated plant does not relocate back inside five quarters. Reference class: realised "
  "supply-chain shifts with committed capital behind them.",
  "Invariant-adjacent: a realised structural shift with a physical relocation cost behind it. Factories that have already moved do not move back inside five quarters, because the cost is sunk capital rather than a preference - the same argument as the German industrial row.",
  "The China share is the cleanest measure of actual, realised decoupling.")

# ══════════════════════════════════════════════════════════════════════════════
# LANE: markets-ai (11 new) — including one complete branch fork
# ══════════════════════════════════════════════════════════════════════════════
N("ai-capex-funding", "now", "How the next leg of AI capex gets funded", 1.0, "2027-01-31",
  "markets-ai", "invariant", "2 quarters",
  "Definitional: p=1.0 because the fork node asserts only that the funding question exists "
  "and resolves one of two ways. Operating cash flow versus external debt, observable in "
  "filings, dated by reporting calendars.",
  "A genuine FORK with two exhaustive branches. The existing tree's ai-2027-fork is about "
  "demand; this one is about the balance sheet, which is what turns a capex cycle into a "
  "credit cycle. Nothing in the tree covered it.",
  "The funding mix is the difference between a drawdown and a default cycle.",
  shifts=[{"target": "hy-spread-band", "p_to": 0.68, "note": "debt-funded capex is an HY event"}])

N("capex-cashflow-funded", "ai-capex-funding", "Hyperscaler capex stays predominantly funded from "
  "operating cash flow through 2027", 0.62, "2027-12-31", "markets-ai", "branch", "5 quarters",
  "Branch. Current operating cash flow covers current capex with margin; the question is whether "
  "the growth rate of capex outruns it, which is arithmetic on two reported series.",
  "Branch A of an exhaustive fork (0.62 + 0.38 = 1.00). Priced off the arithmetic gap between "
  "two reported growth rates rather than off a narrative about discipline.",
  "Cash-funded capex keeps the cycle inside the equity market.", kind="branch")

N("capex-debt-funded", "ai-capex-funding", "A material shift to external debt financing of AI "
  "capex occurs through 2027", 0.38, "2027-12-31", "markets-ai", "branch", "5 quarters",
  "Branch. Already visible at the margin in private credit and SPV structures for datacenters; "
  "the question is whether it reaches the public balance sheet.",
  "Branch B. The genuinely dangerous branch and priced as a real possibility rather than a tail "
  "- 0.38 is a number the book would historically have written as 0.15 and then been surprised by.",
  "Debt-funded capex is how an AI drawdown becomes a credit event.", kind="branch",
  shifts=[{"target": "hy-spread-band", "p_to": 0.55, "note": "issuance widens HY"}])

N("nvda-dc-band", "ai-capex-funding", "Reported quarterly datacenter revenue at the leading "
  "accelerator vendor grows sequentially in at least 3 of the next 4 quarters", 0.70,
  "2027-09-30", "markets-ai", "scheduled", "4 quarters",
  "Scheduled reporting; growth is supply-capped (see the packaging and HBM rows) rather than "
  "demand-capped, which makes the constraint knowable.",
  "Scheduled with a SUPPLY-side mechanism. Priced at the non-invariant ceiling. The important "
  "structural point: when supply is the binding constraint, the forecastable variable is "
  "capacity, not demand - and capacity schedules are published.",
  "Sequential growth is the number the whole complex trades off.")

N("ai-power-contracts", "ai-capex-funding", "At least five new multi-hundred-megawatt datacenter "
  "power agreements are announced before end-2027", 0.80, "2027-12-31", "markets-ai", "marker",
  "5 quarters",
  "Marker on announced PPAs - capital-committed contracts, not intentions. The run rate already "
  "exceeds this pace and the pipeline is disclosed.",
  "Marker on signed contracts (R03: capital-committed). Directly downstream of the energy-supply "
  "load-growth invariant, and the correlation is declared.",
  "Power agreements are where the AI story stops being software.")

N("gpu-depreciation", "ai-capex-funding", "At least one major hyperscaler extends or discloses a "
  "change to server useful-life assumptions before end-2027", 0.55, "2027-12-31", "markets-ai",
  "marker", "5 quarters",
  "Marker on an accounting disclosure. The base rate of life-extension disclosures in this "
  "sector is meaningful, but the direction of any change is a management judgment - capped.",
  "Marker on an accounting choice. Included because a useful-life change is the single largest "
  "lever on reported AI profitability and nobody prices it. It is a MANAGEMENT judgment, so it "
  "is capped - the #26 discipline applied to a corporate committee.",
  "Depreciation assumptions are where reported AI margins are actually made.")

N("ai-revenue-gap", "ai-capex-funding", "Disclosed AI-attributable revenue across the major "
  "vendors stays below annual AI capex through 2027", 0.78, "2027-12-31", "markets-ai",
  "invariant", "5 quarters",
  "Arithmetic on two disclosed series with a very large gap today. Closing it inside five "
  "quarters would require a revenue ramp with no precedent.",
  "Invariant-adjacent: a gap this wide cannot close at any plausible growth rate inside the "
  "window. This is the distance-to-threshold argument, which is the most reliable way to price "
  "a level row and the thing #69 failed to do.",
  "The gap is the whole bear case, stated as arithmetic rather than as a mood.")

N("semis-inventory", "ai-capex-funding", "Days of inventory at the major semiconductor "
  "distributors stays above the pre-2020 average through 2027", 0.72, "2027-12-31",
  "markets-ai", "duration", "5 quarters",
  "Duration. Elevated inventory in mature nodes is a stock that works off slowly; the AI segment "
  "does not absorb it because it is a different product.",
  "Duration class, and an explicit separation of the two semiconductor cycles. Treating 'semis' "
  "as one asset is how #70 and #27 became the same bet twice.",
  "The two semiconductor cycles have diverged and the aggregate index hides it.",
  odds={"tool": "cycle_odds",
        "command": "python tools/cycle_odds.py --current 900 --days 465 --prior-median 1100",
        "ends_lo": 0.14, "ends_hi": 0.22,
        "phase_ends": False,
        "note": "ASSUMED: distributor days-of-inventory has been above the pre-2020 average "
                "~900d; median length of such an overhang ~1100d."})

N("memory-pricing", "ai-capex-funding", "Contract DRAM pricing is higher at end-2027 than at "
  "end-2026", 0.55, "2027-12-31", "markets-ai", "direction", "5 quarters",
  "DIRECTION row and capped. The HBM conversion mechanism is real and physical, but memory "
  "pricing is a classic oscillating tape and 16.15 applies by analogy.",
  "DIRECTION, capped, and explicitly flagged as a leg-extrapolation risk by analogy to the oil "
  "tape. Memory is the most cyclical price in technology; calling its direction is exactly the "
  "shape that went 0-for-8.",
  "Memory pricing is the swing factor in the whole hardware margin structure.")

N("model-release-cadence", "ai-capex-funding", "At least four frontier-class model releases occur "
  "across the major labs before end-2027", 0.84, "2027-12-31", "markets-ai", "marker",
  "5 quarters",
  "Marker with a very strong base rate: the observed cadence across labs already exceeds this "
  "pace, and training runs in progress are disclosed.",
  "Marker with a high base rate and a soft 'frontier-class' threshold, which is named as the "
  "soft part. Left deliberately easy to satisfy - an easy row logged at a high probability is "
  "an honest row, not a filler row.",
  "Release cadence is the demand pull under the whole inference buildout.")

N("ai-litigation", "ai-capex-funding", "A US appellate ruling materially addressing training-data "
  "fair use issues before end-2027", 0.28, "2027-12-31", "markets-ai", "duration", "5 quarters",
  "Duration governed by appellate calendars rather than by the merits; priced below even because "
  "appellate timelines routinely exceed five quarters from filing.",
  "[9/22 CORRECTION] cycle_odds.py puts the no-view ending band at 0.14-0.22 and this row was "
  "logged at 0.48, more than 0.10 outside it with no dated catalyst in the basis; re-priced 0.48 "
  "-> 0.28 into the band. Duration on a COURT clock, priced below even on timeline arithmetic "
  "rather than on a view about the outcome. The same construction as the pharma litigation row - "
  "and both are deliberately silent on who wins.",
  "The ruling's timing matters more than its content for capital planning.",
  odds={"tool": "cycle_odds",
        "command": "python tools/cycle_odds.py --current 900 --days 465 --prior-median 1100",
        "ends_lo": 0.14, "ends_hi": 0.22,
        "phase_ends": True,
        "note": "phase_ends=TRUE: the row claims the ruling ARRIVES (the pending-appeal phase "
                "ends) before end-2027. ASSUMED: the lead training-data cases have been pending "
                "~900d; median time from filing to an appellate merits ruling ~1100d."})

# ══════════════════════════════════════════════════════════════════════════════
# LANE: fed-macro (8 new)
# ══════════════════════════════════════════════════════════════════════════════
N("fomc-dec-2026", "fomc-oct", "December FOMC meeting with a Summary of Economic Projections",
  0.98, "2026-12-09", "fed-macro", "invariant", "12 weeks",
  "The meeting calendar is published a year ahead and SEP meetings are fixed at March, June, "
  "September and December.",
  "Invariant EVENT. Carried from STATE.md's catalyst board into the tree so the December "
  "decision has a node instead of living in prose. The DECISION is a separate capped row.",
  "The December SEP is where the 2027 dot path gets set.", kind="checkpoint", ledger=[26, 62],
  shifts=[{"target": "dec-dots-2027", "p_to": 0.60, "note": "the path is published here"},
          {"target": "real-rate-band", "p_to": 0.76, "note": "policy path sets the real rate"}])

N("dec-dots-2027", "fomc-dec-2026", "The December SEP median shows at least one further 2027 hike",
  0.60, "2026-12-09", "fed-macro", "scheduled", "12 weeks",
  "Scheduled publication of a committee median - a discretionary aggregate. STATE.md already "
  "carries a 0.60 on a second hike by 12/9; this row is the SEP expression of the same view and "
  "is therefore NOT independent of it.",
  "Scheduled-print class for a discretionary value, capped. Critically: this row and STATE.md's "
  "'fomc-oct second hike 0.60' are ONE view, and saying so is the lesson-7 discipline the book "
  "has never enforced. Two rows on one view is a hedge, not two insights.",
  "The dot path, not the meeting, is what the curve actually prices.")

N("cpi-oct-print", "cpi-reaccel", "October CPI released", 0.95, "2026-11-12", "fed-macro",
  "scheduled", "8 weeks",
  "Fixed BLS release calendar; certain absent a funding lapse, which is a separate node.",
  "Scheduled. Cross-wired to the shutdown row - a lapse would break this and the payrolls rows "
  "simultaneously, which is a correlation the book should see in the graph.",
  "CPI is the print that adjudicates the whole supply-shock story.", kind="checkpoint",
  ledger=[32], shifts=[{"target": "core-pce-band", "p_to": 0.70, "note": "CPI inputs map to PCE"}])

N("core-pce-band", "cpi-reaccel", "Core PCE y/y prints inside 2.5-4.0% on every release through "
  "Q2 2027", 0.82, "2027-06-30", "fed-macro", "level", "3 quarters",
  "Band on a slow-moving y/y series; the base-effect path is arithmetic and the energy "
  "pass-through has a known lag length (13g).",
  "[9/22 CORRECTION] range_odds.py puts the no-view odds at 1.00 and this row was logged at 0.70, "
  "-0.30 off it with no dated catalyst in the basis; re-priced 0.70 -> 0.82 toward the "
  "arithmetic. Level with a wide band and an explicit base-effect computation. Note 13g: do not "
  "downgrade the pass-through thesis on less than one lag length of tape - that error cost #76.",
  "Core PCE is the mandate variable; everything else is commentary.",
  odds={"tool": "range_odds",
        "command": "python tools/range_odds.py --spot 3.1 --lo 2.5 --hi 4.0 --days 9 --vol 2.0",
        "odds": 1.0,
        "note": "ASSUMED spot core PCE 3.1% y/y and 2.0%/MONTH relative vol (~0.06pp - a y/y "
                "series moves slowly by construction). One period = one monthly release; 9 "
                "releases to Q2 2027."})

N("real-rate-band", "cpi-reaccel", "The 10y TIPS real yield stays above 1.50% on every close "
  "through Q2 2027", 0.76, "2027-06-30", "fed-macro", "level", "3 quarters",
  "No-view odds off the distance to the threshold on a published daily series. With the policy "
  "rate raised and breakevens contained, a fall through 1.50 requires either a growth scare "
  "or a dovish turn - both identifiable in advance and both named as the falsifiers.",
  "Level with the two falsifying mechanisms named up front. A row that says what would break it "
  "is a pre-registered falsifier, which is lesson 1.",
  "The real rate is the actual discount rate under every equity row in this tree.",
  odds={"tool": "range_odds",
        "command": "python tools/range_odds.py --spot 2.30 --lo 1.50 --days 192 --vol 1.5",
        "odds": 0.96,
        "note": "ASSUMED spot 10y TIPS real yield 2.30% and 1.5%/day relative vol. 192 sessions "
                "to 6/30/27."})

N("voter-rotation-2027", "fomc-dec-2026", "The 2027 FOMC voter rotation proceeds by statutory "
  "schedule", 0.96, "2027-01-31", "fed-macro", "invariant", "1 quarter",
  "The rotation of Reserve Bank presidents among voting seats is fixed by statute and schedule.",
  "INVARIANT: statutory rotation. Included because voter composition is a real input to the "
  "dissent-count mechanism that doctrine 11a now uses to price hikes - and it is knowable "
  "with certainty a year ahead.",
  "Who votes is knowable; how they vote is not. Price only the knowable half.")

N("beige-book-cadence", "cpi-reaccel", "Eight Beige Books are published across 2027", 0.90,
  "2027-12-31", "fed-macro", "scheduled", "5 quarters",
  "Fixed publication schedule of eight per year, two weeks before each FOMC.",
  "Scheduled, near-certain, low-information - and included on purpose. A tree needs its "
  "calendrical scaffolding present so that catalysts have somewhere to attach; not every node "
  "has to be a bet.",
  "The Beige Book is the qualitative input that moves nothing and reveals the regional split.")

N("qt-taper-marker", "cpi-reaccel", "Monthly balance-sheet runoff caps are reduced before "
  "end-2027", 0.50, "2027-12-31", "fed-macro", "direction", "5 quarters",
  "Discretionary committee action - capped. Priced at even because the reserve-scarcity "
  "mechanism (see the reserves and SOFR rows) genuinely argues for it while the inflation "
  "mandate argues against.",
  "DIRECTION + committee, priced at exactly even because two real forces oppose. Note this row "
  "is the twin of the QT-end marker in rates-credit - deliberately consistent, and the "
  "consistency is itself the check.",
  "Ending QT while hiking is the explicit separation of the two tools.")

# ══════════════════════════════════════════════════════════════════════════════
# LANE: us-politics (8 new) — including one complete branch fork
# ══════════════════════════════════════════════════════════════════════════════
N("scotus-term-2026", "election-instrument", "Supreme Court October Term 2026 opens", 0.99,
  "2026-10-05", "us-politics", "invariant", "2 weeks",
  "The term begins on the first Monday in October by statute. As close to certain as any node "
  "in this tree.",
  "INVARIANT by statute. The Court's calendar is a fixed institutional clock and the book has "
  "no node for it despite carrying #56, which turns on federal-intervention litigation.",
  "The term calendar sets when every constitutional fight actually resolves.", kind="checkpoint",
  ledger=[56],
  shifts=[{"target": "scotus-june-rulings", "p_to": 0.92, "note": "the term's clock starts here"}])

N("scotus-june-rulings", "scotus-term-2026", "The major decisions of the term are issued by the "
  "end of June 2027", 0.92, "2027-06-30", "us-politics", "invariant", "3 quarters",
  "Institutional near-certainty: the Court has cleared its argued docket by the end of June in "
  "essentially every modern term.",
  "Invariant from an unbroken institutional pattern. This is the DURATION expression of a "
  "litigation question - the clock is knowable even when the holding is not.",
  "The June cliff is when a year of legal risk resolves at once.", ledger=[56])

N("midterm-fork", "midterms-2026", "Post-midterm control configuration", 1.0, "2026-11-04",
  "us-politics", "invariant", "7 weeks",
  "Definitional: p=1.0 asserts only that the scheduled election occurs and produces one of "
  "three exhaustive configurations. The event is constitutional; the configuration is the fork.",
  "A complete, exhaustive FORK with three branches summing to 1.00. The existing tree has "
  "midterms as a single node with a probability on it, which conflates 'the election happens' "
  "with 'a particular side wins'.",
  "Control determines whether the CR fight repeats in 2027.", ledger=[56, 49],
  shifts=[{"target": "cr-dec11", "p_to": 1.0, "note": "the lame-duck session inherits the result"}])

N("divided-government", "midterm-fork", "Divided control of Congress and the presidency after the "
  "midterms", 0.55, "2026-11-04", "us-politics", "branch", "7 weeks",
  "Branch. Strong historical base rate: the president's party has lost House seats in the large "
  "majority of midterms since the war, and the current margins are thin.",
  "Branch A of an exhaustive fork (0.55 + 0.30 + 0.15 = 1.00). Priced on the midterm base rate "
  "- the outside view - rather than on any read of the current political tape, which is exactly "
  "what R25 demands.",
  "Divided government is the fiscal-gridlock branch and the tail-risk-to-appropriations branch.",
  kind="branch",
  shifts=[{"target": "shutdown-dec", "p_to": 0.35, "note": "gridlock raises lapse risk"}])

N("unified-hold", "midterm-fork", "The president's party retains unified control", 0.30,
  "2026-11-04", "us-politics", "branch", "7 weeks",
  "Branch. Against the historical base rate but not rare; thin margins cut both ways and "
  "redistricting has changed the map.",
  "Branch B. Priced as a real possibility rather than a tail. The book's habit is to price the "
  "non-modal branch too low and then be surprised - the contained/mediation branch was carried "
  "at 0.10 for months and was the branch that kept winning.",
  "Unified control is the fiscal-expansion branch.", kind="branch")

N("contested-result", "midterm-fork", "A federal-level result remains formally contested into "
  "December", 0.15, "2026-11-04", "us-politics", "branch", "7 weeks",
  "Branch. Base rate of a genuinely unresolved federal race extending past the month is low but "
  "non-trivial, and the live federal-intervention fight raises it above the historical rate.",
  "Branch C - the tail, priced as a tail with a stated reason for being above the unconditional "
  "base rate. This is the shape of a correctly-logged low-probability row.",
  "A contested result is a volatility event with no clean hedge.", kind="branch",
  ledger=[49])

N("senate-map-2028", "election-2028", "The 2028 Senate class up for election is the one fixed by "
  "the six-year cycle", 0.99, "2028-11-07", "us-politics", "invariant", "8 quarters",
  "Constitutional arithmetic: the class assignment is fixed and the cycle does not vary.",
  "INVARIANT by constitutional structure. Included because the composition of the map is the "
  "single most-ignored determinant of the outcome and it is known with certainty today.",
  "The map is knowable now; the mood is not. Price the map.")

N("tariff-legal-challenge", "election-instrument", "A federal appellate court issues a merits "
  "ruling on tariff authority before end-2027", 0.42, "2027-12-31", "us-politics", "duration",
  "5 quarters",
  "Duration governed by appellate calendars. Priced near even on timeline arithmetic, with no "
  "view taken on the holding.",
  "[9/22 CORRECTION] cycle_odds.py puts the no-view ending band at 0.23-0.38 and this row was "
  "logged at 0.58, more than 0.10 outside it with no dated catalyst in the basis; re-priced 0.58 "
  "-> 0.42 into the band. Duration on a court clock - the third such row in this buildout "
  "(pharma, AI training data, tariffs). All three are silent on outcome and priced purely on "
  "institutional timelines. That consistency is deliberate: the clock is forecastable and the "
  "verdict is not.",
  "Tariff authority is the legal foundation under a large part of the trade story.",
  odds={"tool": "cycle_odds",
        "command": "python tools/cycle_odds.py --current 500 --days 465 --prior-median 500",
        "ends_lo": 0.23, "ends_hi": 0.38,
        "phase_ends": True,
        "note": "phase_ends=TRUE: the row claims a merits ruling ARRIVES before end-2027. "
                "ASSUMED: the challenges are ~500d old and tariff-authority cases are EXPEDITED, "
                "so the assumed median filing-to-appellate-merits time is ~500d, well below the "
                "~1100d used for the AI cases."})

# ══════════════════════════════════════════════════════════════════════════════
# LANE: taiwan-china (2 new) / world-order (2 new) / iran-energy (2, duration only)
# ══════════════════════════════════════════════════════════════════════════════
N("taiwan-election-2028", "taiwan-watch", "Taiwan's presidential election is held on the "
  "constitutionally scheduled date", 0.94, "2028-01-13", "taiwan-china", "invariant", "9 quarters",
  "The election date is set by a fixed four-year constitutional cycle.",
  "INVARIANT. The single most important scheduled event in the Taiwan lane and the tree has no "
  "node for it - the existing taiwan-window node is dated 2028-06, after the election that "
  "would determine it.",
  "The election is the political input to every cross-strait window estimate.", kind="checkpoint",
  ledger=[53, 42], shifts=[{"target": "taiwan-window", "p_to": 1.0, "note": "the political input resolves"}])

N("taiwan-energy-reserve", "taiwan-watch", "Taiwan's LNG storage days of supply stay below 20 "
  "through 2027", 0.86, "2027-12-31", "taiwan-china", "invariant", "5 quarters",
  "Physical storage capacity is built infrastructure; new terminals take years and the "
  "commissioning schedule is public.",
  "INVARIANT - the most decision-relevant physical fact about Taiwan and it is a construction "
  "schedule. A blockade thesis that does not price storage days is not a thesis.",
  "Storage days is the actual clock on any quarantine scenario.", ledger=[57])

N("new-start-expiry", "world-2031", "No successor strategic arms limitation treaty enters into "
  "force before 2029", 0.86, "2028-12-31", "world-order", "invariant", "9 quarters",
  "Treaty ratification requires a Senate supermajority plus a negotiation that has not begun; "
  "the procedural lead time alone nearly settles the window.",
  "A LEAD-TIME invariant: even with agreement today, ratification does not fit in the window. "
  "Same argument form as the CBDC row, and it is the most under-used argument in the book.",
  "The absence of limits is the structural driver of the warhead-numbers story.")

N("g7-2027", "world-2031", "A G7 leaders' summit is held during 2027", 0.94, "2027-06-30",
  "world-order", "invariant", "3 quarters",
  "Annual rotating-presidency summit; the cycle has been unbroken for decades.",
  "Invariant from institutional continuity. Calendrical scaffolding: catalysts need somewhere "
  "to attach, and the tree's world-order lane has nothing between now and 2030.",
  "The summit is where coordinated sanctions and asset decisions get announced.",
  kind="checkpoint",
  shifts=[{"target": "eu-russia-assets", "p_to": 0.45, "note": "coordination venue for the asset question"}])

N("iran-pause-duration-nov", "fire-pause-sept", "The fire pause is still in effect on 2026-11-01",
  0.38, "2026-11-01", "iran-energy", "duration", "6 weeks",
  "DURATION, priced from the cycle-odds band rather than from either leg. Observed legs in this "
  "conflict have run roughly 2-5 weeks; a pause reaching day ~52 sits at the upper end of the "
  "realised distribution.",
  "The 16.18 / schema R27 construction, and the ONLY kind of iran row this buildout adds. Not "
  "'strikes resume' and not 'peace holds' - just the clock. The iran-war cluster is over the "
  "35% cap, so this row exists to give the duration question a node without adding another "
  "direction bet to a basket that went 0-for-8 on direction.",
  "The pause duration is the tradeable object; the next leg is not.", ledger=[35],
  odds={"tool": "cycle_odds",
        "command": "python tools/cycle_odds.py --completed 14,13,19 --current 12 --days 40",
        "ends_lo": 0.57, "ends_hi": 0.79,
        "phase_ends": False,
        "note": "The pause dates from ~9/10 (STATE.md), so it is ~12d old on 9/22 and the horizon "
                "2026-11-01 is 40d out. Completed pause lengths 14/13/19 days are the cycle's own "
                "realised pauses; STATE.md records 'legs last ~2-5 weeks', which those three are "
                "inside. Prior median left at the tool's default 65d."})

N("npt-notice-arithmetic", "fire-pause-sept", "No NPT withdrawal takes legal effect before "
  "2027-01-01", 0.90, "2027-01-01", "iran-energy", "invariant", "14 weeks",
  "TREATY ARITHMETIC: Article X requires three months' notice to all parties and the UN Security "
  "Council before withdrawal takes effect. Even a notice filed immediately could not take effect "
  "materially before the horizon, and no notice has been filed - a bill was tabled.",
  "INVARIANT, and the best row in this buildout. It converts a charged geopolitical question "
  "into a notice-period calculation. Note the precision the 16.16 premise-liveness rule forces: "
  "a bill TABLED is not a notice FILED, and the difference is exactly the #72 error (a plan is "
  "not an action). The three-month clock is treaty text, not a forecast.",
  "The legal clock, not the rhetoric, is what dates any breakout timeline.", ledger=[34, 30],
  evidence=[{"fact": "NPT Article X requires three months' notice to all parties and the UN "
                     "Security Council before a withdrawal takes effect", "reported": "structural"}])


# ══════════════════════════════════════════════════════════════════════════════
# THE BUILDOUT POLICES ITSELF
# The engine's own failures, turned into pre-write checks. A buildout that would
# not survive the book's rules has no business being merged into the book.
# ══════════════════════════════════════════════════════════════════════════════
CLASSES = {"invariant", "scheduled", "duration", "level", "marker", "direction", "branch"}

# vocabulary that evidences a STRUCTURAL constraint rather than a story
STRUCTURAL = (
    "arithmetic", "physical", "statut", "treaty", "contract", "schedul", "institution",
    "capacity", "demograph", "protocol", "geolog", "base rate", "band", "published",
    "lead time", "stock", "queue", "calendar", "constitution", "legislat", "enacted",
    "committed", "maturity", "backlog", "rule", "hydrolog", "record", "monotonic",
    "duration", "cycle", "no-view", "distribution", "concentration", "reference class",
    "definitional",
)

# ── the no-view gate (added 2026-09-22) ───────────────────────────────────────
# The 9/21 self-check tested PROSE: "p >= 0.70 needs a structural word in basis". It passed
# `brent-band-q4` at 0.66 against no-view odds of 0.39, and `iran-pause-duration-nov` at 0.48
# against a survival band of 0.21-0.43 — because no rule ever ran the arithmetic. These four
# rules run it. They mirror schema.py R11 (levels) and R27 (durations), including R27's
# phase_ends switch, so a row that clears the buildout also clears the ledger's contract.
ODDS_GAP = 0.20      # R11: |P - no-view odds| a level row may take without a dated catalyst
BAND_SLACK = 0.10    # R27: how far outside the cycle band a duration row may sit

_ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
# an explicit M/D or M/D/YY(YY) token. Month 1-12, day 1-31, so "3/2027" (a month-year) and
# "1.5x" do NOT count as a dated catalyst — the point is a DATE, not a date-shaped string.
_MD_DATE = re.compile(r"\b(?:0?[1-9]|1[0-2])/(?:0?[1-9]|[12]\d|3[01])(?:/\d{2,4})?\b")


def dated_catalyst(text: str) -> bool:
    """R11/R27: a deviation from the arithmetic is allowed only against a DATED catalyst.
    A structural story is not a catalyst — #72 was a fully-argued plan with no execution date."""
    return bool(_ISO_DATE.search(text) or _MD_DATE.search(text))


def no_view_problems(n: dict) -> list[str]:
    """Every level and duration row must carry machine-checked no-view odds, and its p must
    survive them. Returns the rule violations for ONE node."""
    out: list[str] = []
    w, cls, p = n["id"], n["row_class"], n["p"]
    nv = n.get("no_view")

    if cls == "level":
        if not nv:
            out.append(f"{w}: [R11-NOVIEW] level row with no no_view block — run tools/range_odds.py "
                       f"and pass odds=; a level row priced on prose is how brent-band-q4 shipped 0.27 "
                       f"away from its own arithmetic")
            return out
        if "range_odds.py" not in nv.get("command", ""):
            out.append(f"{w}: [R11-TOOL] no_view.command must be the range_odds.py invocation that was "
                       f"actually run, got {nv.get('command', '')!r}")
        odds = nv.get("odds")
        if not isinstance(odds, (int, float)) or not 0.0 <= odds <= 1.0:
            out.append(f"{w}: [R11-ODDS] no_view.odds {odds!r} is not a probability")
        elif abs(p - odds) > ODDS_GAP + 1e-9 and not dated_catalyst(n["basis"]):
            out.append(f"{w}: [R11-GAP] p={p} is {p - odds:+.2f} off the no-view odds {odds} "
                       f"(> {ODDS_GAP}) with no dated catalyst in basis — name a dated catalyst or "
                       f"re-price toward the arithmetic")

    elif cls == "duration":
        if not nv:
            out.append(f"{w}: [R27-NOVIEW] duration row with no no_view band — run tools/cycle_odds.py "
                       f"and pass odds= with ends_lo/ends_hi; 16.18 prices the clock, and the clock is "
                       f"a number")
            return out
        if "cycle_odds.py" not in nv.get("command", ""):
            out.append(f"{w}: [R27-TOOL] no_view.command must be the cycle_odds.py invocation that was "
                       f"actually run, got {nv.get('command', '')!r}")
        lo_e, hi_e = nv.get("ends_lo"), nv.get("ends_hi")
        if not all(isinstance(x, (int, float)) for x in (lo_e, hi_e)) \
                or not 0.0 <= lo_e <= hi_e <= 1.0:
            out.append(f"{w}: [R27-BAND] no_view band {lo_e!r}..{hi_e!r} is not a probability band")
        else:
            # phase_ends mirrors schema.py R27: the row either claims the phase ENDS by the
            # horizon, or (the default) that it SURVIVES to it. The band flips with the claim.
            ends = bool(nv.get("phase_ends"))
            lo, hi = (lo_e, hi_e) if ends else (1 - hi_e, 1 - lo_e)
            if (p < lo - BAND_SLACK - 1e-9 or p > hi + BAND_SLACK + 1e-9) \
                    and not dated_catalyst(n["basis"]):
                out.append(f"{w}: [R27-BAND] p={p} is more than {BAND_SLACK} outside the "
                           f"{'ending' if ends else 'survival'} band {lo:.2f}..{hi:.2f} with no dated "
                           f"catalyst in basis — name a dated catalyst or re-price into the band")

    elif nv:
        out.append(f"{w}: [R11-NOVIEW] row_class {cls!r} carries a no_view block; only level and "
                   f"duration rows are priced off a no-view tool")
    return out


def validate(existing_ids: set[str], existing_lanes: set[str],
             already_merged: frozenset[str] = frozenset()) -> list[str]:
    """`already_merged` = ids already in the tree carrying THIS batch's source stamp. The batch
    was merged on 2026-09-21, so on every later run all 200 ids collide; that is a re-run, not an
    id clash, and it must not drown the rule output. main() still refuses --write in that case."""
    bad: list[str] = []
    ids = {n["id"] for n in NODES}
    lanes_ok = existing_lanes | set(NEW_LANES)

    if len(ids) != len(NODES):
        seen: set[str] = set()
        for n in NODES:
            if n["id"] in seen:
                bad.append(f"duplicate id within the batch: {n['id']}")
            seen.add(n["id"])
    for n in NODES:
        w = n["id"]
        if w in existing_ids and w not in already_merged:
            bad.append(f"{w}: id already exists in the tree")
        if n["parent"] != "now" and n["parent"] not in existing_ids and n["parent"] not in ids:
            bad.append(f"{w}: dangling parent {n['parent']!r}")
        if n["lane"] not in lanes_ok:
            bad.append(f"{w}: unknown lane {n['lane']!r}")
        if n["row_class"] not in CLASSES:
            bad.append(f"{w}: unknown row_class {n['row_class']!r}")
        if not 0.0 <= n["p"] <= 1.0:
            bad.append(f"{w}: p out of range")
        if not n["basis"]:
            bad.append(f"{w}: no basis (R25: outside view first)")
        if len(n["rationale"]) < 120:
            bad.append(f"{w}: rationale too thin to audit ({len(n['rationale'])} chars)")
        if n["date"] < "2026-09-21":
            bad.append(f"{w}: dated in the past")

        cls, p = n["row_class"], n["p"]
        # 16.15 / R12 — a direction call is capped, no exceptions
        if cls == "direction" and p > 0.55 + 1e-9:
            bad.append(f"{w}: direction row at p={p} breaks the 0.55 cap (16.15)")
        # R13 — the top of the range belongs to things with no agency left in them
        if p >= 0.85 and cls not in ("invariant", "scheduled"):
            bad.append(f"{w}: p={p} needs row_class invariant|scheduled, got {cls!r} (R13)")
        # a confident row has to name the constraint doing the work
        if p >= 0.70 and not any(k in n["basis"].lower() for k in STRUCTURAL):
            bad.append(f"{w}: p={p} but basis names no structural constraint (R13/R26)")
        # the no-view gate: level and duration rows are priced off a tool, not off prose
        bad.extend(no_view_problems(n))
        # every shift edge must land somewhere real
        for s in n.get("shifts", []):
            if s["target"] not in ids and s["target"] not in existing_ids:
                bad.append(f"{w}: shift edge to missing node {s['target']!r}")
        # a checkpoint that moves nothing is a dead-end catalyst (tools/web_coverage.py)
        if n["kind"] == "checkpoint" and not n.get("shifts") \
                and not any(m["parent"] == n["id"] for m in NODES):
            bad.append(f"{w}: checkpoint with no shifts and no children = dead-end catalyst")

    # branch forks must be exhaustive: siblings sum to 1.00
    by_parent: dict[str, float] = collections.defaultdict(float)
    for n in NODES:
        if n["row_class"] == "branch" or n["kind"] == "branch":
            by_parent[n["parent"]] += n["p"]
    for par, s in by_parent.items():
        if abs(s - 1.0) > 0.03:
            bad.append(f"branch children of {par!r} sum to {s:.2f}, not 1.00")

    # ── mix quotas: the whole point of the buildout ──
    counts = collections.Counter(n["row_class"] for n in NODES)
    total = len(NODES)
    edge = counts["invariant"] + counts["scheduled"]
    if edge / total < 0.50:
        bad.append(f"only {edge}/{total} rows are invariant|scheduled — the book's 8-for-8 and "
                   f"12-for-14 classes must be the majority of any buildout")
    if counts["direction"] / total > 0.10:
        bad.append(f"{counts['direction']}/{total} direction rows — the class that went 0-for-8 "
                   f"is capped at 10% of a batch")
    # resolution discipline: the 9/20 research measured RES ~0.00 because every row
    # sat between 0.40 and 0.88. A book that never says 'probably not' earns nothing.
    lo = sum(1 for n in NODES if n["p"] <= 0.45)
    hi = sum(1 for n in NODES if n["p"] >= 0.88)
    if lo < 8:
        bad.append(f"only {lo} rows at p<=0.45 — no resolution without genuine negatives")
    if hi < 8:
        bad.append(f"only {hi} rows at p>=0.88 — no resolution without genuine near-certainties")
    return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="merge into data/timelines.json")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    tree = json.loads(TREE.read_text(encoding="utf-8"))
    existing_ids = {n["id"] for n in tree["nodes"]} | {"now"}
    existing_lanes = set(tree.get("lanes", []))

    already_merged = frozenset(n["id"] for n in tree["nodes"] if n.get("source") == STAMP)
    problems = validate(existing_ids, existing_lanes, already_merged)
    counts = collections.Counter(n["row_class"] for n in NODES)
    lanes = collections.Counter(n["lane"] for n in NODES)

    print(f"authored: {len(NODES)} nodes across {len(lanes)} lanes")
    if already_merged:
        print(f"  NOTE: {len(already_merged)} of these ids are already in the tree under source="
              f"{STAMP!r} — this batch is MERGED. The self-check below re-checks the AUTHORED batch; "
              f"--write is refused so a re-run cannot duplicate it.")
    print("  by class: " + "  ".join(f"{k}={v}" for k, v in counts.most_common()))
    print("  by lane : " + "  ".join(f"{k}={v}" for k, v in lanes.most_common()))
    ps = sorted(n["p"] for n in NODES)
    print(f"  p spread: min={ps[0]}  p25={ps[len(ps)//4]}  median={ps[len(ps)//2]}  "
          f"p75={ps[3*len(ps)//4]}  max={ps[-1]}")
    print(f"  p<=0.45: {sum(1 for p in ps if p <= 0.45)}   p>=0.88: {sum(1 for p in ps if p >= 0.88)}")
    ev = sum(1 for n in NODES if n["evidence"])
    print(f"  nodes carrying structural evidence: {ev}   (the rest state a prior and say so)")

    if problems:
        print(f"\nREFUSED — {len(problems)} rule violation(s):")
        for b in problems:
            print("  - " + b)
        return 1
    print("\nself-check PASS — the batch survives the book's own rules")

    if not a.write:
        print("dry run; pass --write to merge")
        return 0
    if already_merged:
        print(f"REFUSED --write: {len(already_merged)} of this batch's ids are already in the tree "
              f"under source={STAMP!r}. Merging again would duplicate every one of them.")
        return 1

    backup = TREE.with_suffix(f".json.bak-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}")
    shutil.copy2(TREE, backup)
    tree["lanes"] = list(tree.get("lanes", [])) + [l for l in NEW_LANES
                                                   if l not in tree.get("lanes", [])]
    tree["nodes"] = list(tree["nodes"]) + NODES
    tree["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    tree["note"] = (tree.get("note", "") + f" || {STAMP}: +{len(NODES)} nodes, "
                    f"+{len(NEW_LANES)} lanes. Weighted to the classes the book actually scores on "
                    f"(invariant 8-for-8 Brier 0.10, scheduled-print 12-for-14) and starved of the "
                    f"class that went 0-for-8 (direction). Every node carries row_class + basis; no "
                    f"dated news fact is invented — nodes resting on a prior say so and carry no "
                    f"evidence.")
    TREE.write_text(json.dumps(tree, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"merged -> {TREE}  (backup: {backup.name})")
    print(f"tree is now {len(tree['nodes'])} nodes / {len(tree['lanes'])} lanes")
    return 0


if __name__ == "__main__":
    sys.exit(main())


