#!/usr/bin/env python3
"""promote_nodes.py - turn priced timeline nodes into SCORED ledger rows.

Why: 402 of 474 nodes carried a probability and no accountability. Promoting them is the only way
the engine learns from them. Why it is dangerous: these rows were selected for being near-certain, so
pooled into the headline they would pull mean Brier toward ~0.01 and read as a better forecaster when
nothing changed. Therefore every promoted row is tagged source='tree:<row_class>' and:
  * `ledger.py report` EXCLUDES them by default and shows them as their own block, split by class,
  * the 35pct cluster cap and the analyst's R28/R34 cross-book checks are computed without distortion,
  * prereg/PREREG_calibration_20261003.md excludes them from both confirmatory samples,
  * their references count as LATE in the edge table (written after the price existed) - always.

Specs come from promo/spec_*.json (one object per node). Everything is VALIDATED before anything is
written, and the run aborts if any spec fails unless --skip-invalid is passed.

    python tools/promote_nodes.py --dry-run
    python tools/promote_nodes.py --write
"""
import argparse
import collections
import datetime as dt
import glob
import json
import os
import pathlib
import re
import sqlite3
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
import ledger  # noqa: E402

TREE = ROOT / "data" / "timelines.json"
DIRECTIONS = {"up", "down", "vol", "neutral"}
BAD_LINT = ("COMPOUND", "VAGUE", "SCOPE", "falsifier")   # lint heads that made rows unscoreable before


def problems(spec, node, sectors, existing_text):
    out = []
    from resolve_past_nodes import is_fact
    if is_fact(node):
        # doctrine 16.21: a scheduled or structural calendar fact is not a call - it is never promoted to a scored ledger row
        return ["calendar fact, not a call (doctrine 16.21): never promoted to a scored ledger row"]
    # doctrine 16.22: a PREDETERMINED outcome is not a call. #85/#87 (NATO allies at 2% for 2026) were promoted on 10/3 although
    # NATO had published the 2026 estimates on 7/7. Every spec now names the date the deciding figure is FIRST public.
    import datetime as _dt
    fp = spec.get("first_publication")
    try:
        fpd = _dt.date.fromisoformat(str(fp)[:10]) if fp else None
    except ValueError:
        fpd = None
    if fpd is None:
        out.append("first_publication missing: the date the deciding figure is first made public (doctrine 16.22)")
    elif fpd <= _dt.date.today():
        out.append(f"predetermined, not a call: the deciding figure was already public on {fpd} (doctrine 16.22)")
    g = spec.get
    for k in ("prediction", "falsifier", "resolution_source", "base_rate", "base_class", "direction", "sectors"):
        if g(k) in (None, "", []):
            out.append(f"missing {k}")
    if out:
        return out
    if len(g("prediction")) < 25:
        out.append("prediction too short to be self-contained")
    rs = g("resolution_source")
    for k in ("publisher", "series", "convention"):
        if len(str(rs.get(k, "")).strip()) < 4:
            out.append(f"resolution_source.{k} missing or too thin to settle a dispute (R30)")
    br = g("base_rate")
    if not isinstance(br, (int, float)) or not 0 < br < 1:
        out.append(f"base_rate {br!r} not strictly in (0,1)")
        return out
    if len(g("base_class")) < 25 or not re.search(r"\d", g("base_class")):
        out.append("base_class must name the comparison class WITH a count or structural reason (R25)")
    if g("direction") not in DIRECTIONS:
        out.append(f"direction {g('direction')!r} not in {sorted(DIRECTIONS)}")
    bad = [s for s in g("sectors") if s not in sectors]
    if bad:
        out.append(f"unknown sector(s) {bad}")
    if node["date"] not in g("falsifier"):
        out.append(f"falsifier must restate the horizon {node['date']}")
    key = re.sub(r"\W+", " ", g("prediction").lower()).strip()
    if key in existing_text:
        out.append("prediction text already in the ledger (R24)")
    for m in ledger.lint(g("prediction"), g("falsifier"), node["p"]):
        if m.split(":")[0].startswith(BAD_LINT):
            out.append(f"lint: {m[:110]}")
    gap = abs(node["p"] - br)
    if gap > 0.10 and len(str(g("diverge") or "").strip()) < 20:
        out.append(f"|p {node['p']} - base_rate {br}| = {gap:.2f} > 0.10 needs a dated 'diverge' reason (R26)")
    nv = node.get("no_view") or {}
    if node["row_class"] == "level":
        if "odds" not in nv:
            out.append("level node has no no_view.odds to take as its base rate")
        elif abs(br - nv["odds"]) > 0.005:
            out.append(f"level row: base_rate {br} must equal its recorded no-view odds {nv['odds']}")
    if node["row_class"] == "duration" and "ends_lo" in nv:
        lo, hi = nv["ends_lo"], nv["ends_hi"]
        band = (lo, hi) if nv.get("phase_ends") else (1 - hi, 1 - lo)
        if not (band[0] - 0.01 <= br <= band[1] + 0.01):
            out.append(f"duration row: base_rate {br} outside its recorded cycle band {band}")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-invalid", action="store_true", help="promote the valid ones, report the rest")
    a = ap.parse_args()

    tree = json.loads(TREE.read_text(encoding="utf-8"))
    nodes = {n["id"]: n for n in tree["nodes"]}
    smap = json.loads((ROOT / "data" / "sector_map.json").read_text(encoding="utf-8"))
    sectors = {k for k in smap if not k.startswith("_")}
    c = sqlite3.connect(ledger.DB)
    existing_text = {re.sub(r"\W+", " ", (r[0] or "").lower()).strip()
                     for r in c.execute("SELECT prediction FROM predictions")}
    c.close()

    specs = []
    for f in sorted(glob.glob(str(ROOT / "promo" / "spec_*.json"))):
        specs += json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
    seen, todo, skipped, invalid = set(), [], [], []
    for sp in specs:
        nid = sp.get("node_id")
        if nid in seen:
            invalid.append((nid, ["listed twice"]))
            continue
        seen.add(nid)
        node = nodes.get(nid)
        if node is None:
            invalid.append((nid, ["no such node"]))
            continue
        if node.get("ledger"):
            invalid.append((nid, [f"node already carries ledger id(s) {node['ledger']}"]))
            continue
        if sp.get("skip"):
            skipped.append((nid, sp["skip"]))
            continue
        pr = problems(sp, node, sectors, existing_text)
        if pr:
            invalid.append((nid, pr))
        else:
            todo.append((sp, node))
            existing_text.add(re.sub(r"\W+", " ", sp["prediction"].lower()).strip())

    print(f"specs read: {len(specs)}   promotable: {len(todo)}   skipped by the author: {len(skipped)}   INVALID: {len(invalid)}")
    for nid, why in invalid:
        print(f"  INVALID {nid}")
        for w in why:
            print(f"      - {w}")
    if todo:
        print("  by class :", dict(collections.Counter(n["row_class"] for _, n in todo)))
        print("  by lane  :", dict(collections.Counter(n["lane"] for _, n in todo).most_common()))
        hi = sum(1 for _, n in todo if n["p"] >= 0.88)
        mp = sum(n["p"] for _, n in todo) / len(todo)
        print(f"  mean p = {mp:.2f};  p>=0.88: {hi} of {len(todo)} -> pooled into the headline these would flatter "
              f"Brier. That is why they never enter it.")
    if invalid and not a.skip_invalid:
        print("\nREFUSED: fix the invalid specs, or pass --skip-invalid to promote only the valid ones.")
        return 1
    if not a.write:
        print("dry run; pass --write to promote")
        return 0

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    done = 0
    for sp, node in todo:
        rs = sp["resolution_source"]
        sens = (f"RESOLUTION SOURCE (R30): {rs['publisher']}; series: {rs['series']}; counts: {rs['convention']}. "
                f"BASIS (tree node '{node['id']}', lane {node['lane']}, class {node['row_class']}): {node['basis'][:380]} "
                f"PROMOTED from the tree at its tree price {node['p']} on {stamp}; the reference below was decided "
                f"AFTER that price existed, so this row never counts toward the edge table.")
        cmd = [sys.executable, str(ROOT / "pipeline" / "ledger.py"), "add",
               "--event", f"tree node {node['id']} ({node['lane']}), promoted {stamp}",
               "--prediction", sp["prediction"], "--prob", str(node["p"]), "--horizon", node["date"],
               "--falsifier", sp["falsifier"], "--sensitivity", sens,
               "--sectors", ",".join(sp["sectors"]), "--direction", sp["direction"],
               "--source", f"tree:{node['row_class']}", "--cluster", node["lane"], "--lean", "neutral",
               "--base-rate", str(sp["base_rate"]), "--base-class", sp["base_class"]]
        if sp.get("tickers"):
            cmd += ["--tickers", ",".join(sp["tickers"])]
        if sp.get("diverge"):
            cmd += ["--diverge", sp["diverge"]]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
        m = re.search(r"logged #(\d+)", r.stdout or "")
        if r.returncode or not m:
            print(f"  !! {node['id']} add failed rc={r.returncode}: {(r.stdout or '')[-200:]}{(r.stderr or '')[-200:]}")
            continue
        lid = int(m.group(1))
        node.setdefault("ledger", []).append(lid)
        node["promoted"] = {"ledger_id": lid, "on": stamp, "source": f"tree:{node['row_class']}"}
        done += 1
    tree["updated"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    TREE.write_text(json.dumps(tree, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\npromoted {done} of {len(todo)} -> ledger rows; tree updated. Run web_coverage, then `ledger.py report`.")
    return 0 if done == len(todo) else 1


if __name__ == "__main__":
    sys.exit(main())
