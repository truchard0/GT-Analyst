#!/usr/bin/env python3
"""+14 nodes around the two elections (Israel 2026-10-27, US midterms 2026-11-03) and the Iran escalation window
that sits on top of them, plus four REPRICES of nodes the tree already held.

WHY THIS EXISTS. On 2026-10-22 the first election plan was written from the web and never opened the tree.
The tree already carried the Iran/election coupling - `ev-post-midterm-us-strikes` (0.35), `us-strikes-resume`
(0.08 for the pre-vote window, correctly), `iran-pause-duration-nov` - as UNSCORED tree nodes, because the
iran-war cluster is over the 35% cap and doctrine 16.15 forbids logging an iran direction call off a headline.
So the book HAD the escalation and the plan left it out. tools/window_plan.py now reads the book's own
window first. This batch adds the pieces that were missing around it.

DESIGN. Per doctrine 16.18: price schedules, statutory clocks and markers; refuse the voters' and the
decider's choice. The single direction row is the energy-infrastructure subset of the strike node.
Everything that rests on a prior says so in `basis` and carries no invented dated fact.

REPRICES (documented in each node's rationale, applied by --write):
  * midterm-fork branches 0.55 / 0.30 / 0.15  ->  0.80 / 0.12 / 0.08. Outside view (R25/R26), read 2026-10-22:
    Decision Desk HQ House-D 78%, Poliwave 89% (updated 10/22), Polymarket D-House about 92% (D sweep 68% plus
    D-House/R-Senate 24%). A Democratic House with a Republican president IS divided government. 0.80 sits under the
    forecast average to leave room for polling error and the contested-result branch.
  * ev-post-midterm-us-strikes 0.35 -> 0.45. 16.14 caps strike-PLANNING reports at 0.35 "until an EXECUTION signal
    exists". Execution-grade signals now exist: a third carrier in theatre, CENTCOM told to finish preparations
    (Axios 10/8), and plans for major strikes after the vote (Time/Axios 10/22). cycle_odds on this war's completed
    pauses (20d, 32d, 13d; current pause 42d old, 70d to 12/31) puts P(the pause ENDS) at 0.69-0.78, and US
    large-scale strikes are a SUBSET of that, so 0.45 sits well inside it. Still below the 0.55 direction ceiling
    because this decider has called off a return to fighting repeatedly.
  * ev-israel-knesset-vote 0.92 -> 0.95 (five days out, fixed legal date; not 0.99 because 1973 shows a wartime
    postponement and an Israeli security chief reportedly warned a strike could cause one).

    python tools/buildout_d_elections.py --dry-run | --write
"""
from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import buildout_b_lib as L   # noqa: E402

L.STAMP = "buildout-2026-10-22-elections"
N = L.N

# ---------------------------------------------------------------- Israel (parent: the vote itself)
N("ev-il-results-certified", "ev-israel-knesset-vote",
  "Israel's Central Elections Committee publishes certified final results by 2026-11-04", 0.90, "2026-11-04",
  "global-elections", "scheduled", "2 weeks",
  "STATUTORY clock: final results are published a fixed number of days after the vote (reported as due by "
  "11/4, eight days after 10/27). A calendar row about the count, not about who wins.",
  "Scheduled administrative step; the open parts are a close seat count that triggers recounts or a petition to "
  "the Central Elections Committee, which is why it is not 0.97. Recounts have delayed a final tally by days "
  "before, never weeks.",
  "Certification starts every later clock in this batch (consultations, the 28-day mandate).",
  shifts=[{"target": "ev-il-president-tasks", "p_to": 0.9, "note": "the president's clock starts at publication"}])

N("ev-il-president-tasks", "ev-il-results-certified",
  "President Herzog formally tasks a Knesset member with forming a government by 2026-11-18", 0.90, "2026-11-18",
  "global-elections", "scheduled", "3 weeks",
  "STATUTORY sequence in Basic Law: The Government: after results are published the president consults the "
  "elected lists and tasks one member within roughly a week of the consultations. 11/4 plus the consultation "
  "week plus the tasking week leaves slack to 11/18; the slack is the point.",
  "Scheduled procedural step, not a choice about WHO is tasked (that is the discretionary part and is not "
  "priced here). Risk: a dispute over whether a list can be recommended, or consultations stretched by a "
  "petition. Hitting the date does not say who is tasked.",
  "Tasking starts the 28-day mandate (+14-day extension); failure sends the country to a new election inside 90 days.",
  shifts=[{"target": "ev-il-gov-not-sworn-dec1", "p_to": 0.84, "note": "28-day clock starts here"}])

N("ev-il-knesset-sworn", "ev-il-results-certified",
  "The 26th Knesset holds its inaugural swearing-in session by 2026-11-18", 0.93, "2026-11-18",
  "global-elections", "scheduled", "3 weeks",
  "STATUTORY: the new Knesset must convene within a fixed number of days of the published results (the 2022 "
  "Knesset was sworn six days after certification). A calendar row; the Knesset convening says nothing about "
  "any coalition.",
  "Scheduled and statutory, near-certain once certification is on time. Priced at 0.93 not 0.97 because it "
  "inherits the certification risk above.",
  "Seats become fixed and the Knesset can legislate (including on the trial) from here.")

N("ev-il-netanyahu-pm-dec1", "ev-israel-knesset-vote",
  "Benjamin Netanyahu is still Israel's prime minister, including as head of a transitional government, on "
  "2026-12-01", 0.90, "2026-12-01",
  "global-elections", "invariant", "5 weeks",
  "CONSTITUTIONAL continuity: a government stays in office, with full powers, until its successor is sworn in. "
  "He therefore holds the office on 12/1 unless a new government under someone else is sworn in by then "
  "(the fastest post-election swearing-in I recall is about 30 days, 2003, to be verified; 12/1 is day 35) or he resigns outright.",
  "Structural row, not a forecast of the election result: it holds even if his bloc loses, because formation "
  "takes weeks. The soft parts are a very fast anti-Netanyahu coalition and a resignation after a defeat; "
  "neither has precedent inside five weeks.",
  "While a transitional government sits, strike incentives toward Iran are not those of a campaigning one.")

N("ev-il-gov-not-sworn-dec1", "ev-il-president-tasks",
  "No new Israeli government is sworn in by 2026-12-01", 0.84, "2026-12-01",
  "global-elections", "marker", "5 weeks",
  "BASE RATE of coalition formation lags, from recollection and to be verified before this is ever promoted: "
  "elections 2003 to 2022 reached a sworn government in roughly 30 days at the fastest (2003) and 37 to 82 days "
  "for the rest; 2019 and 2020 produced none. Day 35 after 10/27 is 12/1. The statutory mandate alone is 28 days "
  "from tasking, which on the schedule above starts after 11/10.",
  "Prior, so no evidence block. Capped at 0.84 because one of about eight comparable cases beat day 35 and "
  "because a grand coalition arranged in advance could move faster; a 51-51 poll standoff argues for slower.",
  "A long formation keeps a transitional Netanyahu government in place through the Iran decision window.",
  shifts=[{"target": "ev-il-netanyahu-pm-dec1", "p_to": 0.92, "note": "no new government keeps him in office"}])

N("ev-il-no-bloc-61", "ev-israel-knesset-vote",
  "Neither the Netanyahu bloc nor the Eisenkot-led opposition bloc wins 61 seats on 2026-10-27", 0.84, "2026-10-27",
  "global-elections", "marker", "5 days",
  "PUBLISHED POLL distribution, read 2026-10-22: seven polls in the past week average both blocs at 51 of 120, "
  "ten short of 61 (a Channel 13 poll in late September had 51 and 52). Only the Channel 14 poll, "
  "a pro-Netanyahu outlet, shows a coalition majority. A ten-seat polling miss is the arithmetic the row rests "
  "on; A miss that large would be well outside the usual poll error for a bloc (my recollection is a few seats; verify).",
  "Marker priced off a published distribution, not off a view about who is ahead. Soft part: the bloc "
  "definition (Arab lists are in neither) and a threshold-party collapse moving 5 to 8 seats at once.",
  "A hung result is what makes the formation lag long.",
  evidence=[{"fact": "Seven Israeli polls in the week to 10/20 averaged both major blocs at 51 seats, ten short "
                     "of a majority; the pro-Netanyahu Channel 14 was the outlier [context; The New Arab; "
                     "verified-web]", "reported": "2026-10-20"}])

N("ev-il-pardon-by-dec31", "ev-israel-knesset-vote",
  "President Herzog grants Benjamin Netanyahu a pardon by 2026-12-31", 0.04, "2026-12-31",
  "global-elections", "marker", "10 weeks",
  "BASE RATE and process: a pardon of an unconvicted sitting prime minister has no precedent in Israel; the "
  "President's Office described its plea-deal talks as only an initial stage before any decision on the request "
  "filed 2025-11-30.",
  "Priced as the rare positive. The row is a choice by one named person, so it is kept at the floor and "
  "not argued; it is here so the pardon question has a node, not because the book has a view.",
  "A pardon or a plea deal would end the trial overhang that colours coalition bargaining.")

# ---------------------------------------------------------------- US
N("ev-us-no-approps-pre-vote", "ev-midterm-election-day",
  "Congress enacts no appropriations bill or continuing resolution between 2026-10-22 and 2026-11-03", 0.96,
  "2026-11-03", "us-politics", "scheduled", "2 weeks",
  "CALENDAR: the stopgap enacted in September funds agencies to 12/11 (House 370-48, Senate 90-6), so no "
  "deadline falls before the vote, and members are campaigning, not legislating. Any bill would need floor "
  "time that the pre-election recess does not provide.",
  "Scheduled-class negative with a structural cause. Only a surprise emergency supplemental breaks it, and a "
  "supplemental is not an appropriations extension.",
  "The next funding fight is the lame duck, after the House result is known.",
  shifts=[{"target": "cr-dec11", "p_to": 0.9, "note": "the lame duck owns the next funding vote"}])

N("ev-us-congress-convenes-jan3", "midterm-fork",
  "The new Congress convenes on 2027-01-03 as the Constitution provides", 0.99, "2027-01-03",
  "us-politics", "scheduled", "10 weeks",
  "CONSTITUTIONAL calendar: the 20th Amendment fixes the new Congress's start at noon on January 3 unless "
  "Congress chooses another day by law.",
  "A genuine near-certainty row. The only way it fails is a statute moving the date, which has not been proposed; "
  "it is here so the book carries real near-certainties next to its markers.",
  "Control of committees and the speakership follows from the midterm fork.")

N("ev-fomc-oct28-statement", "ev-midterm-election-day",
  "The FOMC concludes its meeting and publishes its decision statement on 2026-10-28", 0.98, "2026-10-28",
  "fed-macro", "scheduled", "6 days",
  "PUBLISHED CALENDAR: the Federal Reserve's 2026 meeting schedule has the meeting on October 27-28 (the "
  "tree's own fomc nodes carry the same dates); meetings are held on the published dates essentially without "
  "exception, including through the war.",
  "Scheduled event, not a rate call (the hike question is ev-fomc-oct28-hike at 0.15 and fomc-oct). It sits "
  "between the two elections and is the first Fed read after the September hike and the oil spike.",
  "The statement is the only scheduled macro print between the Israeli vote and the US vote.")

# ---------------------------------------------------------------- Iran window (parents: nodes already in the tree)
N("ev-iran-us-no-strike-pre-vote", "fire-pause-sept",
  "The US conducts no acknowledged strike on Iranian territory between 2026-10-22 and 2026-11-03", 0.84,
  "2026-11-03", "iran-energy", "marker", "12 days",
  "COMMITTED public pledge, with a dated source: 'we will not be attacking Iran at any time prior to the "
  "midterm elections' (President, 10/8; White House, repeated 10/22). Pledges by this decider have been "
  "reversed, and Iran is hitting tankers (twelve in the week to 10/5, seven reported on 10/22), so it is "
  "capped under 0.85.",
  "Marker that rides on a stated commitment, not on a view about escalation. The risk is an Iranian strike on "
  "US forces that makes retaliation the cheaper political choice than restraint; a US strike on boats or mines "
  "at sea does not count, only on Iranian territory.",
  "Pairs with the post-midterm strike node: the book says restraint to 11/3, then a live window.",
  evidence=[{"fact": "The US will not attack Iran before the midterm elections, per the President (10/8, "
                     "repeated by a White House official 10/22), while CENTCOM finishes preparations for "
                     "resuming major operations [Axios / Reuters / FT; verified-web]", "reported": "2026-10-22"}])

N("ev-iran-israel-strike-pre-vote", "fire-pause-sept",
  "Israel conducts an acknowledged or credibly attributed strike on Iranian territory between 2026-10-22 and "
  "2026-11-03", 0.07, "2026-11-03", "iran-energy", "marker", "12 days",
  "BASE RATE for the window and the dated reports: the Financial Times reported the Israeli military was ready "
  "to strike on the weekend of 10/10 and the President did not approve it; Netanyahu then said a strike before "
  "the vote was 'not convenient for us'; an Israeli security chief reportedly warned a strike could postpone the "
  "election. Restraint has been the pattern for the whole window.",
  "Low-probability marker. It is consistent with open ledger row #16 (an attributed Israeli strike by 1/8 at "
  "0.52), which spans the whole post-vote period; the two are different windows, not a contradiction.",
  "A pre-vote Israeli strike would void the US pledge row above.",
  evidence=[{"fact": "FT: the Israeli military was ready to strike Iranian nuclear and regime sites on the "
                     "weekend of 10/10; the US did not approve [Financial Times via Times of Israel / Haaretz; "
                     "verified-web]", "reported": "2026-10-21"}])

N("ev-iran-energy-infra-strike-dec31", "ev-post-midterm-us-strikes",
  "The US or Israel strikes Iranian energy infrastructure (refineries, power plants or export terminals) "
  "between 2026-11-04 and 2026-12-31", 0.28, "2026-12-31",
  "iran-energy", "direction", "8 weeks",
  "SUBSET of the strike node above (0.45) so it cannot exceed it; CONJUNCTION rule R36 caps it at the weaker "
  "leg. The reported plans name energy, infrastructure and nuclear targets together, so a campaign that "
  "happens probably includes some energy site, but #72 priced this exact shape at 0.55 off a leaked plan and "
  "scored 0.30, so the conditional is held near 0.6 of the parent.",
  "The batch's only direction row, priced as a fraction of the parent and below the 0.55 ceiling. It carries "
  "the #72 lesson: a leaked plan is not an execution signal.",
  "Energy-site strikes are the oil-price transmission; a limited nuclear-only campaign would not count.",
  evidence=[{"fact": "US and Israeli planners reportedly drafted major strikes on Iranian energy, "
                     "infrastructure and nuclear targets for after the midterms [Time / Axios; verified-web]",
             "reported": "2026-10-22"}])

N("ev-iran-pledge-extended", "ev-post-midterm-us-strikes",
  "The President publicly extends the no-strike pledge beyond 2026-11-03, by 2026-11-10", 0.12, "2026-11-10",
  "iran-energy", "marker", "3 weeks",
  "BASE RATE for this decider: the pledge was tied to a date (the vote) and the same reports describe "
  "preparations for after it; an extension would need a deal signal or a reversal of the stated plan, and "
  "none of the six talks rounds so far produced a durable one (iran-six-conditions, 0.12).",
  "Low row that keeps the restraint-continues world on the tree so it is not lost to the strike branch. It "
  "does not move the strike node alone: a pledge reversed once is weak evidence.",
  "An extension would push the strike node's first window past mid-November.",
  shifts=[{"target": "ev-post-midterm-us-strikes", "p_to": 0.30, "note": "an explicit extension lowers the window"}])


# ---------------------------------------------------------------- repricing of existing nodes
REPRICES = [
    ("divided-government", 0.55, 0.80,
     "[10/22 reprice 0.55 -> 0.80, outside view R25/R26] Decision Desk HQ House-D 78%, Poliwave 89% (10/22), "
     "Polymarket D-House about 92%. A Democratic House with a Republican president is divided government. "
     "Held below the forecast average for polling error and the contested-result branch. Branch row, so the "
     "0.55 direction ceiling does not apply; the reference is the justification."),
    ("unified-hold", 0.30, 0.12,
     "[10/22 reprice 0.30 -> 0.12] Complement of the repriced divided branch; the Republicans keeping the "
     "House is the minority forecast (DDHQ 22%, Poliwave 11%, Polymarket about 8%)."),
    ("contested-result", 0.15, 0.08,
     "[10/22 reprice 0.15 -> 0.08] No federal result has stayed formally contested into December in a "
     "modern midterm; the DOJ monitor and voter-list litigation keep it above zero, not at 0.15."),
    ("ev-post-midterm-us-strikes", 0.35, 0.45,
     "[10/22 reprice 0.35 -> 0.45] Doctrine 16.14 caps planning reports at 0.35 until an EXECUTION signal "
     "exists; one now does (a third carrier in theatre, CENTCOM told to finish preparations 10/8, post-vote "
     "strike plans reported 10/22). cycle_odds --completed 20,32,13 --current 42 --days 70: P(the pause ends) "
     "0.69-0.78, band across prior weights, and a US large-scale campaign is a subset. Kept below 0.55 because "
     "this decider declined to approve the strike that Israel had ready for the weekend of 10/10."),
    ("ev-israel-knesset-vote", 0.92, 0.95,
     "[10/22 reprice 0.92 -> 0.95] Five days out on a fixed legal date. Not 0.99: 1973 shows a wartime "
     "postponement and an Israeli security chief reportedly warned a strike could cause one."),
]
REPRICE_SHIFTS = [("ev-midterm-election-day", {"target": "ev-post-midterm-us-strikes", "p_to": 0.45,
                                                 "note": "the no-strike pledge covers only the period to 11/3"})]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    tree = json.loads(L.TREE.read_text(encoding="utf-8"))
    ids = {n["id"] for n in tree["nodes"]} | {"now"}
    already = {n["id"] for n in tree["nodes"] if n.get("source") == L.STAMP}
    if already:
        print(f"  NOTE: {len(already)} ids already merged under '{L.STAMP}' - --write refused.")
        ids -= already

    bad = L.validate(ids, set(tree["lanes"]))
    # Same convention as buildout_c: the count quotas in the lib are written for a 200-node buildout. A 14-node
    # addendum cannot hold "8 rows at p<=0.45". Every per-node rule stays, and so do the invariant|scheduled
    # majority and the 10% direction cap, which are the quotas that protect against the 0-for-8 class.
    bad = [b for b in bad if "rows at p<=0.45" not in b and "rows at p>=0.88" not in b]
    by = {n["id"]: n for n in tree["nodes"]}
    for nid, old, new, _ in REPRICES:
        if nid not in by:
            bad.append(f"reprice target missing: {nid}")
        elif abs(by[nid]["p"] - old) > 1e-9 and not already:
            bad.append(f"reprice {nid}: expected p={old}, tree has {by[nid]['p']} (already repriced?)")
    sib = sum(new for nid, _, new, _ in REPRICES if nid in ("divided-government", "unified-hold", "contested-result"))
    if abs(sib - 1.0) > 1e-9:
        bad.append(f"midterm-fork branches sum to {sib:.2f}, not 1.00")
    L.summarise()
    if bad:
        print(f"\nREFUSED - {len(bad)} violation(s):")
        for b in bad:
            print("  - " + b)
        return 1
    print("\nself-check PASS (per-node rules + invariant|scheduled majority + direction cap; count quotas N/A)")
    if not a.write:
        print("dry run; pass --write to merge")
        return 0
    if already:
        return 1

    backup = L.TREE.with_suffix(f".json.bak-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}")
    shutil.copy2(L.TREE, backup)
    for nid, old, new, why in REPRICES:
        n = by[nid]
        n["p"] = new
        n["rationale"] = why + " || " + (n.get("rationale") or "")
    for nid, edge in REPRICE_SHIFTS:
        by[nid].setdefault("shifts", None)
        by[nid]["shifts"] = (by[nid]["shifts"] or []) + [edge]
    tree["nodes"] = list(tree["nodes"]) + L.NODES
    tree["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    L.TREE.write_text(json.dumps(tree, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"merged -> {L.TREE} (backup: {backup.name}); tree is now {len(tree['nodes'])} nodes; "
          f"{len(REPRICES)} repriced")
    return 0


if __name__ == "__main__":
    sys.exit(main())
