#!/usr/bin/env python3
"""resolve_past_nodes.py - every node dated in the past is a HIT or a MISS, and says why.

WHY (2026-10-23). The Timeline tab still showed 'High-beta/AI complex tailwind persists 70%' for a call that had been
scored MISS (#28): a past node hung at its old probability. The user's rule: any past event is either a hit or a miss.

WHAT A VERDICT MEANS. `resolved.happened` is what the world did. `resolved.verdict` is whether the engine's CALL was right:
HIT iff (p > 0.5) == happened; a node written after the fact is UNFORECAST, so a 5% call on something that did not happen is a HIT and a 45% call on something that
did is a MISS. Nodes that were already pinned to 0/1 before this tool existed carry an explicit verdict taken from the
ledger row or note that scored them. The node's probability is NOT overwritten - it is the call being graded - and branch
siblings still sum to 1, so the branch-sum audit stays meaningful.

JUDGEMENT CALLS are marked `"judgement": true` and listed by --report; they rest on how a loosely-worded node maps to the
world (e.g. 'fire pause' has no agreed definition) and are the ones to review.

    python tools/resolve_past_nodes.py --check       # list past-dated nodes with no resolution (exit 1 if any)
    python tools/resolve_past_nodes.py --write       # resolve the ones in the table below, back up the tree first
    python tools/resolve_past_nodes.py --report      # the judgement calls
A node whose id is not in the table is never guessed at: --write refuses to invent a verdict.
"""
import argparse
import datetime as dt
import json
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TREE = ROOT / "data" / "timelines.json"
T, F = True, False

# id: (happened, verdict or None = from the call, basis, judgement?)
TABLE = {
    "flip-b": (T, None, "Round 3 fired 8/31-9/9, after the 8/16 Islamabad window expired with no deal (node round-3).", F),
    "cpi-june-soft": (T, "HIT", "June CPI printed soft (-0.4 m/m, energy -5.7): #31, #46 HIT.", F),
    "brent-90": (T, None, "Brent closed above 90 on every session 8/31-9/18 (peak close 108.75 on 9/15); 100.69 on 7/23.", F),
    "red-sea-front": (T, "HIT", "Houthi blockade of Saudi persisted; Saudi seaborne exports about -33% m/m in August (#58 HIT).", F),
    "capex-verdict": (T, None, "No top-4 hyperscaler cut at the 7/22-7/30 prints (#50 HIT, #52 HIT).", F),
    "contained": (F, None, "The Islamabad window expired 8/16 with no deal or extension (#10, #19); round 3 followed.", F),
    "succession-tip": (F, None, "No IRGC fracture: the regime survived the transition (#17, #18 HIT). Label asserts succession resolved; the 7% was the residual fracture branch.", T),
    "capitulation": (F, None, "No consolidation and no proxy stand-down; the deal did not stick (#10, #18 HIT).", F),
    "nuclear-recon": (T, None, "Strikes hit reconstitution targets (unfinished plant 7/21); #30 and #64 HIT.", F),
    "us-houthi-response": (F, "MISS", "Neither a US strike on Yemen nor an escort framework (#63 MISS, Brier 0.56).", F),
    "dovish-fed": (T, None, "The 7/29 FOMC was a hawkish hold with three hike dissents (#13, #45, #67 HIT; #26 MISS).", F),
    "capex-raise": (T, None, "At least one explicit capex raise at the prints (#52 HIT).", F),
    "capex-hold": (F, None, "A raise occurred, so 'all in-line holds' did not (#52).", F),
    "energy-strike-weekend": (F, "MISS", "No energy-infrastructure strike (#72 MISS, Brier 0.30).", F),
    "opec-defends": (F, "MISS", "OPEC+ did not pause or trim to defend price (#29 MISS).", F),
    "hormuz-framework-only": (T, "HIT", "Framework talk, no normalized traffic (#73, #68, #79 HIT).", F),
    "hormuz-normalized": (F, "HIT", "Hormuz did not fully normalize that week (#73 HIT) - the tail was priced low.", F),
    "payrolls-jul": (T, "HIT", "July payrolls printed -23k and SPY closed green (#75 HIT).", F),
    "smh-605-cap": (T, "HIT", "SMH did not close above 605 that week (#77 HIT).", F),
    "spy-breakout-fails": (T, "HIT", "The record breakout did not hold above 2% for three straight sessions (#78, #66, #65 HIT).", F),
    "naval-escort": (F, None, "No US escort or toll regime materialized; the dual blockade persisted.", F),
    "oil-premium-unwind": (F, "MISS", "XLE did not outperform USO as the war premium unwound (#74 MISS).", F),
    "cpi-reaccel": (T, "HIT", "July benign (#71), August +0.4 m/m with energy +2.1 (#32 HIT): the reacceleration landed in the August print as sequenced.", F),
    "semis-correction": (T, None, "SMH closed 548.55 on 7/27 and 504.22 on 7/29 (below 550); it did not close above 605 again until 9/22 (607.46).", F),
    "houthi-saudi": (T, "HIT", "The proxy theater persisted and turned on Saudi (#15, #20, #58, #37 HIT).", F),
    "election-instrument": (T, "HIT", "DHS letters and funding conditions on 7/17 (#49 HIT).", F),
    "islamabad-window": (T, "HIT", "The 60-day window expired about 8/16 with no deal or extension (#68 HIT).", F),
    "market-regime-q3": (T, None, "SPY 727.7-776.0 (+3.0% 7/20 to 9/30), QQQ 661-747, SMH 504-609: two-sided range, no melt-up, no index crash.", F),
    "gas-sub-4": (F, "MISS", "Pump average did not fall below $4.00 (#76 MISS).", F),
    "round-3": (T, "MISS", "US strikes 8/31-9/9, Brent back above 100. Written after it happened, so not graded; the engine had the flip-b branch it realised at 45%.", F),
    "iaea-unsc-referral": (T, "HIT", "The IAEA Board referred Iran to the UN Security Council on 9/9 (#30 HIT).", F),
    "tech-tailwind": (F, None, "Hormuz re-closed and Brent held above 85, flipping Iran to the hawkish branch (#28 MISS); SMH hit 504 on 7/29. The AI complex later recovered, so 'persists' is read at the node's own window.", T),
    "fire-pause-sept": (T, "MISS", "A fire pause began about 9/10. Written after it began, so not graded; the engine had the frozen-oscillation branch it realised at 40%.", T),
    "highbeta-derate": (T, None, "USER RULING 2026-10-23: the call needed more time (the trigger, Brent >90, is still live at 113). 8/31 to 10/22: SMH -5.98% vs XLE +6.27% (gap -12.3 pts; since 9/30 SMH -14.06% vs XLE +9.87%). LEDGER #27 STAYS MISS on its own wording ('over the following month', scored to 9/30: SMH +9.41% vs XLE -3.27%) - the node and the row now differ on purpose; the call was right and about three weeks early.", T),
    "frozen-oscillation": (T, None, "Strike/pause legs of 2-5 weeks: round 3 8/31-9/9 then the fire pause from 9/10; no deal, no full war. Overlaps flip-b, which also happened.", T),
    "fomc-sept-hike": (T, "MISS", "The FOMC hiked 25bp to 3.75-4.00 on 9/16, 12-0 (#26 MISS).", F),
    "price-map-q3": (F, "MISS", "QQQ broke 720 on 8/4 and SPY 775 on 8/13 (#69 MISS).", F),
    "frozen-conflict": (T, None, "To 10/22: no ratified treaty and no war-scale campaign beyond 30 days (#35, #1, #10 tracking). PROVISIONAL - the claim runs to 2027.", T),
    "us-strikes-resume": (F, None, "No large-scale US campaign found 9/20-10/22; a public no-strike pledge to 11/3.", F),
    "scotus-term-2026": (T, None, "October Term 2026 opened on Monday 10/5.", F),
    "pause-outlasts-oct12": (T, None, "No US or Iranian strikes on territory found 9/10-10/12; tanker attacks continued (the tree counts the pause as strikes and launches).", T),
    "iran-six-conditions": (F, None, "Only shuttle messages through Qatar; the US rejected the offer 9/26 and no negotiation of the six conditions began.", F),
}
ANCHOR_BASIS = "Lane anchor: a structural certainty that held; not a forecast of an event."

# A node pinned to 0 or 1 after the fact would otherwise read 'the engine called 100%'. The call being graded is the one the
# engine actually made: its first-stated probability on the ledger row that scored it (inverted when the node is the
# complement of the row), or - for a node written AFTER it happened - the branch call it realised.
CALLS = {  # node: ("ledger", id, invert) | ("node", id)
    "cpi-june-soft": ("ledger", 31, False), "red-sea-front": ("ledger", 58, False), "us-houthi-response": ("ledger", 63, False),
    "energy-strike-weekend": ("ledger", 72, False), "opec-defends": ("ledger", 29, False),
    "hormuz-framework-only": ("ledger", 73, False), "hormuz-normalized": ("ledger", 73, True),
    "payrolls-jul": ("ledger", 75, False), "smh-605-cap": ("ledger", 77, False), "spy-breakout-fails": ("ledger", 78, False),
    "oil-premium-unwind": ("ledger", 74, False), "cpi-reaccel": ("ledger", 32, False), "houthi-saudi": ("ledger", 15, False),
    "election-instrument": ("ledger", 49, False), "gas-sub-4": ("ledger", 76, False), "iaea-unsc-referral": ("ledger", 30, False),
    "fomc-sept-hike": ("ledger", 26, True), "price-map-q3": ("ledger", 69, False),
    "round-3": ("node", "flip-b"), "fire-pause-sept": ("node", "frozen-oscillation"),
}


def call_for(nid, nodes_by_id):
    """-> (probability, where it came from) or None."""
    if nid not in CALLS:
        return None
    kind, ref, *rest = CALLS[nid]
    if kind == "node":
        return nodes_by_id[ref]["p"], f"the {ref} branch it realised"
    import sqlite3
    row = sqlite3.connect(ROOT / "ledger" / "ledger.db").execute("SELECT prob0,prob FROM predictions WHERE id=?", (ref,)).fetchone()
    pr = row[0] if row[0] is not None else row[1]
    return (1 - pr if rest and rest[0] else pr), f"#{ref}" + (" (inverted: this node is its complement)" if rest and rest[0] else "")


def grade(nid, called, happened):
    """A node written AFTER the event it records was never a forecast: it is UNFORECAST, with the nearest call kept for display."""
    if CALLS.get(nid, (None,))[0] == "node":
        return "UNFORECAST"
    return verdict_for(called, happened)


FACT_IDS = {"islamabad-window"}      # a dated expiry on the calendar, not a forecast


def is_fact(n):
    """A scheduled or structural calendar FACT (a lane anchor, the term opens, the meeting is held): it occurs or it does not, nobody
    called it, and it is never graded as a hit or a miss. (User, 2026-10-23: 'these are not calls... these are just factual events.')"""
    return n["id"].endswith("-anchor") or n["id"] in FACT_IDS or (n.get("row_class") in ("invariant", "scheduled") and (n.get("p") or 0) >= 0.95)


def verdict_for(p, happened):
    return "HIT" if (p is not None and p > 0.5) == happened else "MISS"


def pending(nodes, today):
    return [n for n in nodes if n["date"] < today and "resolved" not in n]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--redo", nargs="+", default=[], help="drop and re-apply the table decision for these node ids")
    ap.add_argument("--recall", action="store_true", help="re-derive called/verdict on already-resolved nodes")
    ap.add_argument("--asof", default=dt.date.today().isoformat())
    a = ap.parse_args()
    tree = json.loads(TREE.read_text(encoding="utf-8"))
    nodes = tree["nodes"]

    if a.report:
        for n in nodes:
            r = n.get("resolved")
            if r and r.get("judgement"):
                print(f"{n['id']:<22} p={n['p']:<5} happened={r['happened']!s:<5} {r['verdict']:<4} {r['basis']}")
        return 0

    byid = {n['id']: n for n in nodes}
    for n in nodes:
        if n['id'] in a.redo:
            n.pop('resolved', None)
    if a.recall:
        n_fix = 0
        for n in nodes:
            r = n.get("resolved")
            c = call_for(n["id"], byid) if r else None
            if not c:
                continue
            was = (r.get("called"), r["verdict"])
            r["called"], r["called_from"] = round(c[0], 4), c[1]
            r["verdict"] = grade(n["id"], c[0], r["happened"])
            n_fix += 1
            print(f"  {n['id']:<24} called {c[0]:.2f} from {c[1]}  happened={r['happened']}  -> {r['verdict']}" + ("" if was[1] == r["verdict"] else f"   (was {was[1]})"))
        TREE.write_text(json.dumps(tree, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"re-derived {n_fix} node(s)")
        return 0
    todo = pending(nodes, a.asof)
    unknown = [n for n in todo if not is_fact(n) and n["id"] not in TABLE]
    if a.check or not a.write:
        print(f"{len(todo)} past-dated node(s) without a resolution as of {a.asof}")
        for n in todo:
            print(f"  {n['date']} {n['id']:<28} p={n['p']:<5} {'(in table)' if n['id'] in TABLE or n['id'].endswith('-anchor') else 'NEEDS A DECISION'}  {n['label'][:60]}")
        return 1 if todo else 0
    for n in nodes:                        # facts that were graded before this rule existed are re-filed as facts
        if is_fact(n) and n["date"] < a.asof and n.get("resolved", {}).get("verdict") not in (None, "FACT"):
            n.pop("resolved")
    todo = pending(nodes, a.asof)
    unknown = [n for n in todo if not is_fact(n) and n["id"] not in TABLE]
    if unknown:
        print("REFUSED - no decision on file for: " + ", ".join(n["id"] for n in unknown))
        return 1
    backup = TREE.with_suffix(f".json.bak-{dt.datetime.now():%Y%m%dT%H%M%S}")
    shutil.copy2(TREE, backup)
    done = 0
    for n in todo:
        if is_fact(n):
            n["resolved"] = {"happened": True, "verdict": "FACT", "called": None, "asof": a.asof,
                             "basis": "A calendar or structural fact: it occurred. Facts are not calls and are never graded."}
            done += 1
            continue
        if False:
            happened, verdict, basis, judgement = True, "HIT", ANCHOR_BASIS, False
        else:
            happened, verdict, basis, judgement = TABLE[n["id"]]
        c = call_for(n["id"], byid)
        called, src = (c if c else (n["p"], None))
        calc = grade(n['id'], called, happened)
        if verdict and verdict != calc:
            print(f"  NOTE {n['id']}: table says {verdict} but a call of {called:.2f} and happened={happened} grades {calc}; using {calc}")
        verdict = calc
        n["resolved"] = {"happened": happened, "verdict": verdict, "called": round(called, 4), "asof": a.asof,
                         "basis": basis, **({"called_from": src} if src else {}), **({"judgement": True} if judgement else {})}
        done += 1
    tree["updated"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    TREE.write_text(json.dumps(tree, indent=2, ensure_ascii=False), encoding="utf-8")
    hits = sum(1 for n in nodes if n.get("resolved", {}).get("verdict") == "HIT")
    miss = sum(1 for n in nodes if n.get("resolved", {}).get("verdict") == "MISS")
    print(f"resolved {done} node(s) (backup {backup.name}); non-anchor nodes now {hits} HIT / {miss} MISS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
