#!/usr/bin/env python3
"""window_plan.py - what the BOOK ALREADY SAYS about a date window. Read-only: it prints, it never writes.

WHY IT EXISTS (2026-10-22). Asked for a plan around the Israeli election and the US midterms, I searched the web and
never opened the tree. The tree already held the Iran/election coupling - `ev-post-midterm-us-strikes` 0.35,
`us-strikes-resume` 0.08 for the pre-vote window, `iran-pause-duration-nov` - as unscored nodes (the iran-war cluster
is over the 35% cap), and the plan left them out. The failure was not a missing forecast, it was not reading the
forecasts the book had. This tool is the first step of any dated plan.

It prints four things for [--from, --to]:
  1. TREE   every node dated in the window, by lane, with p / class / whether a ledger row backs it
  2. LEDGER every OPEN ledger row whose horizon falls in the window or after it and whose cluster has nodes here
  3. FOCAL  event-log statements that name a forward focal date ("not before the midterms", "after the vote",
            "until the deadline") with NO tree node that shares two label words with them
  4. COUPLE every focal node (an election, vote, deadline, summit, meeting, expiry) against every ACTIVE conflict
            cluster: is there a node for that cluster within +-7 days of the focal date? Wars cluster their
            escalations and pauses around dated focal points (the Islamabad 60-day window, the pause that ran to the
            vote), so a focal date with no coupled node is a hole, not a quiet period.

LIMITS: FOCAL matching is word overlap on node labels, so it errs toward calling things UNCOVERED; COUPLE only knows
the clusters in CLUSTER_LANES below. It lists holes. It does not price them.

    python tools/window_plan.py                        # today .. +45 days
    python tools/window_plan.py --from 2026-10-22 --to 2026-12-31
"""
import argparse
import collections
import datetime as dt
import json
import pathlib
import re
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CLUSTER_LANES = {"iran-war": {"iran-energy"}}    # ledger cluster -> tree lanes that carry it
FOCAL_NODE = re.compile(r"\b(elections?|votes?|midterms?|deadline|summit|meeting|expir\w*|referendum|convenes?|fomc)\b", re.I)
FOCAL_STATEMENT = re.compile(r"\b(before|after|until|ahead of|prior to|through)\b.{0,40}?\b(midterm\w*|election\w*|vote|"
                             r"deadline|expir\w*|summit|window|referendum)\b", re.I)
STOP = set("a an the of to in on for and or at by with from as is are was were be been it its this that after before "
           "over will could may than into about up down out not no".split())
COUPLE_DAYS = 7


def toks(text):
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOP and len(w) > 3}


def d(s):
    return dt.date.fromisoformat(s[:10])


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--from", dest="start", default=dt.date.today().isoformat())
    ap.add_argument("--to", dest="end", default=None)
    a = ap.parse_args()
    start = d(a.start)
    end = d(a.end) if a.end else start + dt.timedelta(days=45)

    tree = json.loads((ROOT / "data" / "timelines.json").read_text(encoding="utf-8"))
    nodes = tree["nodes"]
    inwin = sorted((n for n in nodes if start <= d(n["date"]) <= end), key=lambda n: (n["date"], n["lane"]))
    print(f"WINDOW {start} .. {end}   tree {len(nodes)} nodes   {len(inwin)} dated in the window\n")

    print("1. TREE - what the book already prices in the window")
    lanes = collections.defaultdict(list)
    for n in inwin:
        lanes[n["lane"]].append(n)
    for lane, ns in sorted(lanes.items()):
        print(f"  [{lane}]")
        for n in ns:
            print(f"    {n['date']}  p={n['p']:<5}  {str(n.get('row_class') or n['kind']):<10} {n['id']:<34} {n['label'][:70]}"
                  f"{'  [ledger ' + str(n['ledger']) + ']' if n.get('ledger') else ''}")

    db = ROOT / "ledger" / "ledger.db"
    clusters_here = {c for c, ls in CLUSTER_LANES.items() if ls & set(lanes)}
    print("\n2. LEDGER - open rows still live after the window opens (clusters with nodes in it)")
    open_rows = []
    if db.exists():
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        for pid, prob, hz, cl, pred in con.execute(
                "SELECT id,prob,horizon,cluster,prediction FROM predictions WHERE status='open' AND source NOT LIKE 'tree:%'"):
            if hz and d(hz) >= start:
                open_rows.append((pid, prob, hz, cl, pred))
        con.close()
    shown = [r for r in open_rows if r[3] in clusters_here] or []
    for pid, prob, hz, cl, pred in sorted(shown, key=lambda r: r[2]):
        print(f"    #{pid:<4} P={prob:.2f}  horizon {hz}  [{cl}]  {pred[:80]}")
    if not shown:
        print("    (none in a mapped cluster)")

    print("\n3. FOCAL - event-log statements that name a forward focal date but share no node label")
    ev_path = ROOT / "data" / "events.json"
    events = json.loads(ev_path.read_text(encoding="utf-8"))["events"] if ev_path.exists() else []
    node_words = [(n["id"], toks(n["label"] + " " + n["id"].replace("-", " "))) for n in nodes]
    uncovered = 0
    for e in sorted(events, key=lambda e: e["date"]):
        if not FOCAL_STATEMENT.search(e["fact"]):
            continue
        ew = toks(e["fact"])
        best = max((len(ew & w) for _, w in node_words), default=0)
        if best < 2:
            uncovered += 1
            print(f"    UNCOVERED {e['date']}  {e['fact'][:130]}")
    if not uncovered:
        print("    (every forward-dated statement shares at least two words with a tree node)")

    print(f"\n4. COUPLE - each focal node against each active conflict cluster, +-{COUPLE_DAYS} days")
    holes = 0
    focal = [n for n in inwin if FOCAL_NODE.search(n["label"]) and n["lane"] not in
             {l for ls in CLUSTER_LANES.values() for l in ls}]
    active = {c for c in (r[3] for r in open_rows) if c in CLUSTER_LANES}
    for cl in sorted(active):
        lane_nodes = [n for n in nodes if n["lane"] in CLUSTER_LANES[cl]]
        for f in focal:
            near = [n for n in lane_nodes if abs((d(n["date"]) - d(f["date"])).days) <= COUPLE_DAYS]
            if near:
                print(f"    covered   {f['date']} {f['id']:<30} x {cl}: " + ", ".join(n["id"] for n in near[:3]))
            else:
                holes += 1
                print(f"    HOLE      {f['date']} {f['id']:<30} x {cl}: no {cl} node within {COUPLE_DAYS} days")
    print(f"\n{uncovered} uncovered focal statement(s), {holes} coupling hole(s). Nothing was written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
