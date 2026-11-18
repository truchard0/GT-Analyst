#!/usr/bin/env python3
"""retro_conflicts.py - replay the ledger through the conflict gates and see what they would have forced.

The gates (pipeline/conflict.py: the iran-war level check and the cross-cluster world-state check) stop a NEW row that
cannot hold with a row already open. This replays the book in the order it was written, with the labels in
data/state_labels.json (written from each row's own text, never from its outcome), under two remedies:

  A. REFUSE THE LATER ROW (what the bare gate does).
  B. RETIRE A STALE COUNTERPART. A flag forces a decision, and the right decision depends on which row is still alive: if
     the open row's PREMISE was already dead on the new row's date (data/state_labels.json `premise_dead`, taken from the
     ledger lessons - the tape facts that were public on that date), the old row is retired (voided) and the new row
     stands. Only a flag against a LIVE row refuses the new one. B is what a careful analyst does; A is what a dumb
     gate does, and A removes good rows (#60 was right to be logged after the conflict reignited).

Findings that rest on a label marked `inferred` are tagged. Read-only: it writes nothing.

    python tools/retro_conflicts.py [--exclude-void]
"""
import argparse
import datetime as dt
import json
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
import conflict as cf  # noqa: E402


def d(s):
    return dt.date.fromisoformat(str(s)[:10])


def load(exclude_void):
    blob = json.loads((ROOT / "data" / "state_labels.json").read_text(encoding="utf-8"))
    con = sqlite3.connect(f"file:{ROOT / 'ledger' / 'ledger.db'}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute(
        "SELECT id,ts,prob0,prob,outcome,status,horizon,resolved_ts,asof,cluster,prediction FROM predictions "
        "WHERE source NOT LIKE 'tree:%' ORDER BY ts,id")]
    if exclude_void:
        rows = [r for r in rows if r["status"] != "void"]
    return rows, blob["labels"], blob.get("premise_dead", {})


def P(r):
    return r["prob0"] if r["prob0"] is not None else r["prob"]


def end_of(r):
    e = r["asof"] or (r["resolved_ts"] or "")[:10] or r["horizon"]
    return d(min(str(e)[:10], str(r["horizon"])[:10]))


def replay(rows, labels, dead, policy):
    """-> (refused {id: [counterpart ids]}, retired {id: date}). policy 'A' or 'B'."""
    accepted, refused, retired = [], {}, {}
    for r in rows:
        lab = labels.get(str(r["id"]))
        if not lab:
            accepted.append(r)
            continue
        t = d(r["ts"])
        live = [a for a in accepted if str(a["id"]) in labels and d(a["ts"]) <= t and end_of(a) > t
                and not (str(a["id"]) in retired and retired[str(a["id"])] <= t)]
        lv, st = [], []
        for x in live + [r]:
            xid = str(x["id"]) if x is not r else "new"
            lx = labels[str(x["id"])]
            if lx.get("level"):
                lo, hi = cf.parse_level(lx["level"], "iran-war")
                lv.append(cf.Claim(xid, P(x), lo, hi, x["horizon"], "iran-war"))
            for name, rng in (lx.get("states") or {}).items():
                _, lo, hi = cf.parse_state(f"{name}={rng}")
                st.append(cf.StateClaim(xid, P(x), name, lo, hi, x["horizon"]))
        errs = [f for f in cf.check(lv, t) + cf.check_states(st, t) if f.severity == "error" and "new" in f.ids]
        others = sorted({o for f in errs for o in f.ids if o != "new"}, key=int)
        if not errs:
            accepted.append(r)
            continue
        stale = [o for o in others if policy == "B" and str(o) in dead and d(dead[str(o)]["date"]) <= t]
        alive = [o for o in others if o not in stale]
        for o in stale:
            retired[o] = t
        if alive:
            refused[str(r["id"])] = alive
        else:
            accepted.append(r)
    return refused, retired


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--exclude-void", action="store_true", help="treat void rows as never live")
    args = ap.parse_args()
    rows, labels, dead = load(args.exclude_void)
    by = {str(r["id"]): r for r in rows}

    def verdict(r):
        if r["status"] != "resolved":
            return r["status"]
        return "HIT" if abs(P(r) - r["outcome"]) < 0.5 else "MISS"

    def inferred(a, b):
        sa, sb = labels[a], labels[b]
        common = set((sa.get("states") or {})) & set((sb.get("states") or {}))
        return bool(common & (set(sa.get("inferred") or []) | set(sb.get("inferred") or [])))

    def score(rs):
        rs = [r for r in rs if r["status"] == "resolved"]
        n = len(rs)
        return (n, sum(r["outcome"] == 1 for r in rs) / n, sum(abs(P(r) - r["outcome"]) < 0.5 for r in rs) / n,
                sum((P(r) - r["outcome"]) ** 2 for r in rs) / n)

    base = score(rows)
    print(f"{len(rows)} analyst rows replayed; {len(labels)} labelled\n")
    print(f"baseline: {base[0]} resolved; outcome-true {base[1]:.1%}; call-right {base[2]:.1%}; first-stated Brier {base[3]:.4f}\n")
    for pol, title in (("A", "A. refuse the later row (the bare gate)"), ("B", "B. retire a counterpart whose premise was already dead; refuse only against a LIVE row")):
        refused, retired = replay(rows, labels, dead, pol)
        print(f"== {title}")
        for rid, others in sorted(refused.items(), key=lambda kv: int(kv[0])):
            for o in others:
                tag = "inferred label" if inferred(rid, o) else "stated labels"
                print(f"   REFUSE  #{rid} ({by[rid]['ts'][:10]}, P {P(by[rid]):.2f}, {verdict(by[rid])})  vs live #{o} ({by[o]['ts'][:10]}, P {P(by[o]):.2f}, {verdict(by[o])})  [{tag}]")
        for rid, t in sorted(retired.items(), key=lambda kv: int(kv[0])):
            print(f"   RETIRE  #{rid} ({verdict(by[rid])}) on {t}: {dead[rid]['why']}")
        gone = set(refused) | set(retired)
        keep = [r for r in rows if str(r["id"]) not in gone]
        s = score(keep)
        print(f"   removed: " + ", ".join(f"#{i} {verdict(by[i])}" for i in sorted(gone, key=int)))
        print(f"   -> {s[0]} resolved; outcome-true {s[1]:.1%}; call-right {s[2]:.1%}; first-stated Brier {s[3]:.4f}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
