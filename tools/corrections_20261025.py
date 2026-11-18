"""Apply the corrections from the 10/24 deep-research report ("Stock market geopolitical game") to the book.

User 2026-10-25: "apply corrections". Every change below is sourced in
research_notes/Stock market geopolitical game/*.md and listed in the report's
"What today's research changes in the engine's book" table. Nothing here touches prereg/REGISTRY.jsonl:
registered claims are snapshots and are scored at their registered probabilities.

  python tools/corrections_20261025.py            # dry run: show every change
  python tools/corrections_20261025.py --write    # back up and write tree + calendar, revise/confirm ledger rows
"""
import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TREE = ROOT / "data" / "timelines.json"
CAL = ROOT / "data" / "constraint_calendar.json"
TAG = "[10/25 correction"

# (node id, expected old p, new p, why) - the why is prefixed to the node's rationale
REPRICES = [
    ("ev-ecb-oct29-hike", 0.30, 0.05,
     f"{TAG}: 0.30 -> 0.05] The 0.30 rested on a 3-week-old 28-29% futures read. ECB Watch showed 97.1% no change on "
     "10/16 (96-97% through mid-October); Danske (10/20) and Newsquawk (10/23) both expect a hold; French fiscal stress "
     "has already tightened core yields. R26: the reference is now the market price (~0.03), and nothing dated argues "
     "for a 0.27 divergence. Kept slightly above market for the Lagarde-energy tail."),
    ("ecb-hold", 0.55, 0.45,
     f"{TAG}: 0.55 -> 0.45] Danske (10/20) expects a final 25bp hike on 12/17 to 2.75% with risk skewed to a fourth "
     "hike; markets price ~75bp of total tightening; September flash HICP 3.7%; TTF at a post-2022 high (EUR 92.30, "
     "10/23) with storage ~75% vs ~86% normal. Kept within the committee cap: Danske also calls energy spillover into "
     "underlying inflation 'very muted', and France's 5% OAT argues for caution."),
    ("boj-hike", 0.45, 0.50,
     f"{TAG}: 0.45 -> 0.50] Core CPI 2.1% in September, first print above target since December; a December hike "
     "'considered more likely' (Rio Times, 10/2x) after the 9/18 hike to 1.25%; yen ~158 with 160 as the intervention "
     "line. Small step only: the ~80% December odds come from a weak source, and the meeting date conflicts "
     "(12/17-18 vs 12/19-20)."),
    ("opec-quota-unchanged", 0.55, 0.70,
     f"{TAG}: 0.55 -> 0.70] The 0.55 'hard cap' assumed a live quota choice. It is not: the UAE left OPEC/OPEC+ "
     "effective 5/1; the seven core members pumped ~25.0 mb/d in August, ~5 mb/d BELOW February and 'well below quota', "
     "so a quota change on 11/1 would be cosmetic; Reuters (10/4) says changes are unlikely before 2027 pending the "
     "capacity audit; Bloomberg (10/4) says a pause in quota hikes was signalled through end-2026. The discretionary "
     "decision moved to the 11/29 ministerial (new node opec-ministerial-nov29). Held at 0.70, the R13 line for a "
     "direction-class row, because a cartel can still surprise."),
    ("fomc-oct", 0.68, 0.72,
     f"{TAG}: 0.68 -> 0.72] FedWatch ~86% hold for 10/28 (10/21) and ~81% for a December hike (aggregators, NOT "
     "verified on CME); JPMorgan, Morgan Stanley, UBS and RSM expect December; Goldman (9/30) moved its hike to "
     "December but sees 'a strong chance' it proves unnecessary; September CPI 3.7% (gasoline +9.1% m/m), payrolls "
     "+29k. Small step because the market number is unverified and Goldman's caveat is real."),
]

RELABEL = {
    "opec-nov-meeting": "OPEC+ core-group meeting convenes (11/1, sets December output)",
    "ev-busan-truce-rolled": ("The US-China Busan trade truce is extended beyond its current 2027-01-10 expiry, or "
                              "replaced by a broader deal, announced on or before 2027-01-10 (no lapse)"),
}

EVIDENCE = {
    "ev-busan-truce-rolled": [
        {"fact": "Label clarified 10/25: the truce was ALREADY extended from 11/10/2026 to 1/10/2027 on 9/23 (Bessent), "
                 "so the call is about the NEXT roll, past 1/10/2027. Read as the 11/10 expiry it would be predetermined "
                 "(doctrine 16.22). MOFCOM reportedly confirmed on 9/28 that the trade arrangements run to 1/10/2027, "
                 "which also covers the October-2025 rare-earth package suspended to 11/10 (no official Chinese text "
                 "found; the April-2025 licensing regime was never suspended). [context; Yahoo Finance via search "
                 "summary / Carra Globe; unverified]", "reported": "2026-09-28"},
        {"fact": "Greer runs the truce as two-month 'compliance periods' (soybeans ~13.7 Mt of a 25 Mt pledge plus "
                 "8-10 cargoes in mid-October; ~$4bn of $17bn other farm goods); export controls are outside the "
                 "trade track; APEC Shenzhen 11/18-19 and the Miami G20 in December are the checkpoints. "
                 "[context; CNBC 9/25 / Ag Bull via search summary]", "reported": "2026-10-15"},
    ],
    "opec-nov-meeting": [
        {"fact": "The 11/1 meeting is the seven-member core group (the UAE left OPEC/OPEC+ effective 5/1/2026); the "
                 "full ministerial plus JMMC meets 11/29 to set 2027 policy pending a capacity audit. [context; "
                 "Reuters via StreetInsider / World Oil-Bloomberg 10/4; verified-web]", "reported": "2026-10-04"},
    ],
    "fomc-oct": [
        {"fact": "FedWatch 87.3% hold / 12.7% hike for 10/28 (10/16), 86.2% hold (10/21); a December hike ~81% "
                 "(aggregator figures, not CME directly). [supports; 0xzx / Tech-Insider; unverified]",
         "reported": "2026-10-21"},
    ],
}

NEW_NODES = [{
    "id": "opec-ministerial-nov29",
    "parent": "es-anchor",
    "label": "OPEC+ full ministerial meeting and JMMC convene (11/29, 2027 policy)",
    "p": 0.96,
    "horizon": "5 weeks",
    "rationale": "Scheduled EVENT, not a policy forecast (the #29 lesson): the meeting happening is near-certain; what "
                 "it decides on 2027 quotas, the capacity audit and the 2022-cut layer is discretionary and is NOT "
                 "priced here. Added 10/25 because the research showed the 11/1 meeting is only the core group's "
                 "monthly call and the real decision sits here.",
    "confluence": [],
    "ledger": [],
    "evidence": [{"fact": "OPEC+ next steps: 11/1 sub-group meeting for December; full ministerial plus JMMC on "
                          "2026-11-29 to set 2027 policy, with a decision pending on restoring another layer of the "
                          "cuts halted in 2022, shaped by the capacity audit. [context; World Oil / Bloomberg; "
                          "verified-web]", "reported": "2026-10-04"}],
    "market": "Sets the 2027 supply path; low near-term signal while Gulf capacity, not quotas, binds.",
    "kind": "checkpoint",
    "lane": "energy-supply",
    "date": "2026-11-29",
    "row_class": "scheduled",
    "basis": "The group's meeting calendar is published a year ahead; meetings occur essentially without exception, "
             "occasionally by video or moved by days.",
    "source": "corrections-2026-10-25",
}]

SHIFT_FIX = ("opec-nov-meeting", "opec-quota-unchanged", 0.70)

# constraint calendar: re-source or downgrade what the 10/24 researchers could not find
CAL_FIX = {
    "us-pledge-midterms": {
        "fact": "Trump: the US 'will not be attacking Iran at any time prior to the Midterm Elections' (10/8); a White "
                "House official repeats it 10/22; two senior Iranian officials tell Reuters (10/14) the tanker attacks "
                "aim to keep prices high and influence the midterms, and the Washington Post (10/18) reports Tehran "
                "front-loading the pain before the vote. [10/25: the 'Reuters 10/20' citation could not be found and "
                "is replaced by WaPo 10/18]"},
    "us-energy-price-oct": {
        "strength": "inferred",
        "fact": "NYT (10/21-22): Trump has repeatedly vetoed a return to major combat and wants refineries spared, "
                "with gasoline ~$4.27-4.30 (first October ever above $4) and Brent above 110; at rallies he says the "
                "US may hit Iran 'a little bit further' (10/22) and 'another little Epic Fury' (10/23). [10/25: the "
                "10/22 NewsNation 'temporarily postpones major combat operations' statement could not be re-sourced, "
                "so this window is downgraded from stated to inferred; the 10/8 pledge alone carries the suppression "
                "to 11/3]"},
    "ir-pressure-prevote": {
        "fact": "Two senior Iranian officials tell Reuters (10/14) the tanker strikes aim to keep energy prices high and "
                "pressure Trump before the midterms; the Washington Post (10/18) reports Tehran front-loading the pain "
                "because it expects Trump to care less about prices after the vote; October is the war's worst month "
                "for shipping, 27 attacks on commercial ships by IMO count as of 10/22 (UKMTO: 15 in 10/6-10/14). "
                "[10/25: 'Reuters 10/20' replaced by WaPo 10/18]"},
    "us-pause-sep": {
        "fact": "No US strikes on Iranian land after round 3 ended in early September (AFP 10/24: no major strikes on "
                "land targets since early September; the exact 9/10 start is the engine's inference, unsourced); "
                "Trump willing to negotiate (9/14), expects talks (9/27), 'always open' (10/5); Iran gave mediators "
                "conditions via Qatar 9/19"},
}

LEDGER = [
    ["revise", "104", "--prob", "0.50", "--reason",
     "10/25 correction (deep research 10/24): Japan core CPI 2.1% in September, first print above target since "
     "December; a December hike 'considered more likely' after the 9/18 hike to 1.25%; yen ~158 vs the 160 "
     "intervention line. Small step: ~80% December odds come from a weak source and the meeting date conflicts "
     "(12/17-18 vs 12/19-20). Synced with tree node boj-hike."],
    ["confirm", "83", "--reason",
     "10/25 Brent input corrected to the 116.72 settlement on 10/23 (Reuters), not 111.66. range_odds.py --spot "
     "116.72 --lo 85 --hi 125 --days 47 --vol 2.52 gives NO-VIEW 0.32 (0.47 at 1.82%/day). 0.25 stands: scenarios B "
     "and C (0.50 together) both breach 125, and the spot rise moved the no-view DOWN toward the row, not away."],
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    tree = json.loads(TREE.read_text(encoding="utf-8"))
    by = {n["id"]: n for n in tree["nodes"]}
    bad = []
    for nid, old, new, _ in REPRICES:
        if nid not in by:
            bad.append(f"missing {nid}")
        elif abs(by[nid]["p"] - old) > 1e-9:
            bad.append(f"{nid}: expected p={old}, tree has {by[nid]['p']} (already corrected?)")
    for n in NEW_NODES:
        if n["id"] in by:
            bad.append(f"{n['id']} already exists")
        if n["parent"] not in by:
            bad.append(f"{n['id']}: parent {n['parent']} missing")
        if n["lane"] not in tree["lanes"]:
            bad.append(f"{n['id']}: lane {n['lane']} missing")
    cal = json.loads(CAL.read_text(encoding="utf-8"))
    wins = {w["id"]: w for w in cal["windows"]}
    for wid in CAL_FIX:
        if wid not in wins:
            bad.append(f"calendar window missing: {wid}")
    if bad:
        print("REFUSED:\n  - " + "\n  - ".join(bad))
        return 1

    for nid, old, new, why in REPRICES:
        print(f"  reprice {nid}: {old} -> {new}")
    for nid, lab in RELABEL.items():
        print(f"  relabel {nid}: {by[nid]['label']!r}\n       -> {lab!r}")
    for nid, ev in EVIDENCE.items():
        print(f"  evidence {nid}: +{len(ev)}")
    for n in NEW_NODES:
        print(f"  new node {n['id']} ({n['row_class']}, {n['date']}, p={n['p']})")
    for wid, fx in CAL_FIX.items():
        print(f"  calendar {wid}: " + ", ".join(f"{k}{' ' + wins[wid].get(k, '') + ' -> ' + v if k == 'strength' else ''}"
                                                 for k, v in fx.items()))
    for cmd in LEDGER:
        print(f"  ledger {cmd[0]} #{cmd[1]}")
    if not a.write:
        print("dry run; pass --write")
        return 0

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    shutil.copy2(TREE, TREE.with_suffix(f".json.bak-{stamp}"))
    shutil.copy2(CAL, CAL.with_suffix(f".json.bak-{stamp}"))
    for nid, old, new, why in REPRICES:
        by[nid]["p"] = new
        by[nid]["rationale"] = why + " || " + (by[nid].get("rationale") or "")
    for nid, lab in RELABEL.items():
        by[nid]["rationale"] = f"{TAG}: relabel] was: {by[nid]['label']} || " + (by[nid].get("rationale") or "")
        by[nid]["label"] = lab
    for nid, ev in EVIDENCE.items():
        by[nid]["evidence"] = list(by[nid].get("evidence") or []) + ev
    src, tgt, p_to = SHIFT_FIX
    for s in by[src].get("shifts") or []:
        if s.get("target") == tgt:
            s["p_to"] = p_to
    tree["nodes"] = list(tree["nodes"]) + NEW_NODES
    tree["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    TREE.write_text(json.dumps(tree, indent=2, ensure_ascii=False), encoding="utf-8")
    for wid, fx in CAL_FIX.items():
        wins[wid].update(fx)
    CAL.write_text(json.dumps(cal, indent=2, ensure_ascii=False), encoding="utf-8")
    for cmd in LEDGER:
        r = subprocess.run([sys.executable, str(ROOT / "pipeline" / "ledger.py")] + cmd, cwd=ROOT,
                           capture_output=True, text=True, timeout=60)
        print(f"  ledger {cmd[0]} #{cmd[1]}: rc={r.returncode} {r.stdout.strip()[-140:]} {r.stderr.strip()[-200:]}")
    print(f"written (backups .bak-{stamp})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
