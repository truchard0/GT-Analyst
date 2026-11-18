#!/usr/bin/env python3
"""tripwire.py - what needs a human TODAY. Read-only: it proposes, it never writes the ledger.

Three things went wrong in a row on 2026-09/10, and each is a check here:
  1. OVERDUE      #70 and #27 sat two days past their horizon unscored.             (lesson 6)
  2. LOOK DUE     scoring is TIME-WEIGHTED, so a correct revision made at day 51 of 61 recovered
                  0.053 of Brier. A row's price only earns credit for the days it was held, so a
                  look is due at 25 / 50 / 75 percent of the row's window - not "when I remember".
  3. DEAD EARLY   a price-defined row can be decided long before its horizon (MU's 800 target was
                  touched 7/28 and unbooked for seven weeks). Rows registered in
                  data/autoresolve.json are checked against the tape every run.

    python tools/tripwire.py            # analyst rows in full, tree rows summarised
    python tools/tripwire.py --all      # every row in full
    python tools/tripwire.py --strict   # exit 1 if anything is overdue or decided (for a scheduler)

autoresolve.json  {"<ledger id>": {"type": "stay_inside", "ticker": "CL=F", "lo": 55, "hi": 140,
                                   "start": "2026-10-03", "end": "2027-12-31"}}
                  stay_inside: TRUE iff EVERY close in [start,end] is within [lo,hi] (omit a bound for one-sided)
                  touch:       TRUE iff ANY close reaches `level` going `dir` (up|down) in [start,end]
Conventions are CLOSES, adjusted. A row that needs a different convention does not belong in this file.
"""
import argparse
import datetime as dt
import json
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
DB = ROOT / "ledger" / "ledger.db"
REG = ROOT / "data" / "autoresolve.json"
LOOKS = (0.25, 0.50, 0.75)


def parse(ts):
    t = dt.datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)


def check_spec(spec):
    """-> (state, outcome or None, evidence). state: DECIDED | OPEN | NODATA."""
    import marketdata as md
    start, end = spec["start"], spec["end"]
    try:
        s = md.closes(spec["ticker"], start, (dt.date.fromisoformat(end) + dt.timedelta(days=1)).isoformat())
    except md.MarketDataError as e:
        return "NODATA", None, f"market data unavailable: {e}"
    s = [(d, v) for d, v in s if start <= d <= end]
    # front_months: [{"ticker": "BZZ26.NYM", "until": "2026-10-30"}] - a continuous ticker can roll BEFORE the
    # contract expires (BZ=F moved to January Brent on 10/23 at 111.70 while December, still the ICE front month,
    # settled 116.72). Up to `until`, the named contract's closes replace the continuous series.
    cut = start
    for fm in sorted(spec.get("front_months", []), key=lambda f: f["until"]):
        try:
            c = md.closes(fm["ticker"], start, (dt.date.fromisoformat(fm["until"]) + dt.timedelta(days=1)).isoformat())
        except md.MarketDataError as e:
            return "NODATA", None, f"front-month {fm['ticker']} unavailable: {e}"
        s = ([(d, v) for d, v in s if d < cut] + [(d, v) for d, v in c if cut <= d <= fm["until"]]
             + [(d, v) for d, v in s if d > fm["until"]])
        cut = (dt.date.fromisoformat(fm["until"]) + dt.timedelta(days=1)).isoformat()
    s.sort()
    if not s:
        return "NODATA", None, f"no closes for {spec['ticker']} in {start}..{end}"
    last = s[-1]
    if spec["type"] == "stay_inside":
        lo, hi = spec.get("lo"), spec.get("hi")
        for d, v in s:
            if (lo is not None and v < lo) or (hi is not None and v > hi):
                return "DECIDED", 0, f"{spec['ticker']} closed {v:.4g} on {d}, outside [{lo}, {hi}] - the claim is dead"
        if end <= dt.date.today().isoformat() and last[0] >= end:
            return "DECIDED", 1, f"every close {s[0][0]}..{last[0]} stayed inside [{lo}, {hi}] (last {last[1]:.4g})"
        return "OPEN", None, f"still inside [{lo}, {hi}] through {last[0]} (last {last[1]:.4g})"
    if spec["type"] == "touch":
        lvl, up = spec["level"], spec["dir"] == "up"
        for d, v in s:
            if (up and v >= lvl) or ((not up) and v <= lvl):
                return "DECIDED", 1, f"{spec['ticker']} closed {v:.4g} on {d}, through {lvl}"
        if end <= dt.date.today().isoformat() and last[0] >= end:
            return "DECIDED", 0, f"{spec['ticker']} never closed through {lvl} by {last[0]}"
        return "OPEN", None, f"not yet through {lvl} (last {last[1]:.4g} on {last[0]})"
    return "NODATA", None, f"unknown spec type {spec['type']!r}"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--all", action="store_true", help="show tree-promoted rows in full too")
    ap.add_argument("--strict", action="store_true", help="exit 1 if anything is overdue or decided")
    a = ap.parse_args()

    now = dt.datetime.now(dt.timezone.utc)
    today = now.date()
    c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    c.row_factory = sqlite3.Row
    rows = c.execute("SELECT id,ts,horizon,prob,prob0,source,cluster,prediction FROM predictions "
                     "WHERE status='open' ORDER BY horizon").fetchall()
    last_look = {}
    for r in c.execute("SELECT pred_id, MAX(ts) t FROM revisions WHERE kind!='initial' GROUP BY pred_id"):
        last_look[r["pred_id"]] = parse(r["t"])

    overdue, looks, tree_looks = [], [], 0
    for r in rows:
        is_tree = str(r["source"] or "").startswith("tree")
        try:
            hz = dt.datetime.fromisoformat(r["horizon"][:10]).replace(tzinfo=dt.timezone.utc) + dt.timedelta(days=1)
        except ValueError:
            continue
        t0 = parse(r["ts"])
        if hz.date() <= today:
            overdue.append(r)
            continue
        span = (hz - t0).total_seconds()
        if span <= 0:
            continue
        frac = (now - t0).total_seconds() / span
        crossed = [f for f in LOOKS if frac >= f]
        if not crossed:
            continue
        top = max(crossed)
        due_at = t0 + dt.timedelta(seconds=top * span)
        seen = last_look.get(r["id"])
        if seen is None or seen < due_at:
            if is_tree and not a.all:
                tree_looks += 1
            else:
                looks.append((r, top, frac, (now - due_at).days))

    print(f"TRIPWIRE {today}   open rows: {len(rows)}")
    print()
    print(f"[1] OVERDUE - horizon passed, not scored: {len(overdue)}")
    for r in overdue:
        print(f"    #{r['id']:<4} horizon {r['horizon']}  P={r['prob']:.2f}  {r['prediction'][:90]}")
    print()
    print(f"[2] LOOK DUE - price not revisited since it crossed a {'/'.join(str(int(x*100)) for x in LOOKS)}% mark: "
          f"{len(looks)}" + (f"   (+{tree_looks} tree-promoted rows, use --all)" if tree_looks else ""))
    for r, top, frac, late in sorted(looks, key=lambda x: -x[1]):
        print(f"    #{r['id']:<4} {frac:4.0%} of window elapsed, {int(top*100)}% mark passed {late}d ago  "
              f"P={r['prob']:.2f}  {r['prediction'][:70]}")
    print()
    reg = json.loads(REG.read_text(encoding="utf-8")) if REG.exists() else {}
    live = {int(k): v for k, v in reg.items() if not str(k).startswith("_")}
    print(f"[3] TAPE CHECK - {len(live)} price-defined row(s) registered in data/autoresolve.json")
    decided = 0
    open_ids = {r["id"] for r in rows}
    for pid in sorted(live):
        if pid not in open_ids:
            continue
        state, outcome, ev = check_spec(live[pid])
        mark = {"DECIDED": ">>", "OPEN": "  ", "NODATA": "??"}[state]
        print(f"  {mark} #{pid:<4} {state:<7} {ev}")
        if state == "DECIDED":
            decided += 1
            print(f"       PROPOSED (not executed): python pipeline/ledger.py resolve {pid} {outcome} "
                  f"--asof {today}   then write the lesson")
    if not live:
        print("    (none registered yet)")
    print()
    try:   # tree nodes dated in the past must carry a HIT/MISS verdict (tools/resolve_past_nodes.py)
        nodes = json.loads((ROOT / "data" / "timelines.json").read_text(encoding="utf-8"))["nodes"]
        stale = [n for n in nodes if n["date"] < dt.date.today().isoformat() and "resolved" not in n]
        print(f"\n[4] PAST-DATED NODES WITHOUT A HIT/MISS VERDICT: {len(stale)}"
              + ("" if not stale else "   -> python tools/resolve_past_nodes.py --check"))
        for n in stale[:12]:
            print(f"     {n['date']} {n['id']:<28} p={n['p']}  {n['label'][:60]}")
    except (OSError, KeyError, ValueError):
        pass
    print("Nothing above was written. Resolving stays a human decision; this only stops rows going unseen.")
    return 1 if (a.strict and (overdue or decided)) else 0


if __name__ == "__main__":
    sys.exit(main())
