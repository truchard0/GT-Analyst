#!/usr/bin/env python3
"""Full-system debug: syntax, imports, DB integrity, JSON validity, timeline
coherence, gate checks, data-file sanity. Run: python tools/debug_all.py
Prints a PASS/FAIL line per check and a summary. Exit 1 if any FAIL."""
import ast
import json
import pathlib
import sqlite3
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
fails, warns = [], []


def ok(msg): print(f"  [PASS] {msg}")
def fail(msg): fails.append(msg); print(f"  [FAIL] {msg}")
def warn(msg): warns.append(msg); print(f"  [WARN] {msg}")


print("=== 1. PYTHON SYNTAX (all .py) ===")
for p in sorted(ROOT.rglob("*.py")):
    if ".claude" in str(p):
        continue
    try:
        ast.parse(p.read_text(encoding="utf-8"))
        ok(f"syntax {p.relative_to(ROOT)}")
    except SyntaxError as e:
        fail(f"syntax {p.relative_to(ROOT)}: {e}")

print("\n=== 2. MODULE IMPORTS ===")
sys.path.insert(0, str(ROOT / "pipeline"))
for mod in ["common", "ledger", "ingest", "trigger", "dashboard"]:
    try:
        __import__(mod)
        ok(f"import {mod}")
    except Exception as e:
        fail(f"import {mod}: {type(e).__name__}: {e}")

print("\n=== 3. DATABASE INTEGRITY ===")
for db in ["ledger/ledger.db", "ledger/seen.db"]:
    fp = ROOT / db
    if not fp.exists():
        fail(f"{db} missing")
        continue
    try:
        c = sqlite3.connect(fp)
        r = c.execute("PRAGMA integrity_check").fetchone()[0]
        (ok if r == "ok" else fail)(f"{db} integrity: {r}")
        tbls = [t[0] for t in c.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        ok(f"{db} tables: {', '.join(tbls)}")
        c.close()
    except Exception as e:
        fail(f"{db}: {e}")

# ledger row sanity
try:
    c = sqlite3.connect(ROOT / "ledger" / "ledger.db")
    n_open = c.execute("SELECT COUNT(*) FROM predictions WHERE status='open'").fetchone()[0]
    n_res = c.execute("SELECT COUNT(*) FROM predictions WHERE status='resolved'").fetchone()[0]
    bad_prob = c.execute("SELECT COUNT(*) FROM predictions WHERE prob<0 OR prob>1").fetchone()[0]
    unlessoned = c.execute("SELECT COUNT(*) FROM predictions p LEFT JOIN lessons l ON l.pred_id=p.id "
                           "WHERE p.status='resolved' AND l.pred_id IS NULL").fetchone()[0]
    ok(f"ledger: {n_open} open, {n_res} resolved")
    (ok if bad_prob == 0 else fail)(f"probabilities in [0,1]: {bad_prob} violations")
    (ok if unlessoned == 0 else fail)(f"resolved-without-lesson: {unlessoned}")
    c.close()
except Exception as e:
    fail(f"ledger sanity: {e}")

print("\n=== 4. JSON VALIDITY ===")
for jf in ["data/timelines.json", "data/fusion.json", "watchlist.json", "config.json",
           "data/sector_map.json"]:
    fp = ROOT / jf
    if not fp.exists():
        warn(f"{jf} missing"); continue
    try:
        json.load(open(fp, encoding="utf-8")); ok(f"{jf} valid JSON")
    except Exception as e:
        fail(f"{jf}: {e}")

print("\n=== 5. TIMELINE COHERENCE ===")
try:
    d = json.load(open(ROOT / "data" / "timelines.json", encoding="utf-8"))
    from collections import defaultdict
    kids = defaultdict(list)
    ids = {n["id"] for n in d["nodes"]}
    for n in d["nodes"]:
        if n.get("kind") == "branch":
            kids[n.get("parent", "now")].append((n["id"], n["p"]))
    for par, ch in sorted(kids.items()):
        s = sum(p for _, p in ch)
        (ok if abs(s - 1) <= 0.03 else fail)(f"branch-sum {par}: {s:.2f}")
    # dangling parents / shift targets
    dangling = [n["id"] for n in d["nodes"] if n.get("parent") and n["parent"] not in ids and n["parent"] != "now"]
    (ok if not dangling else fail)(f"dangling parents: {dangling or 'none'}")
    bad_shifts = [(n["id"], s["target"]) for n in d["nodes"] for s in n.get("shifts", []) if s["target"] not in ids]
    (ok if not bad_shifts else fail)(f"shift edges to missing nodes: {bad_shifts or 'none'}")
    ok(f"nodes={len(d['nodes'])}, lanes={len(d.get('lanes',[]))}")
except Exception as e:
    fail(f"timeline coherence: {e}")

print("\n=== 6. DASHBOARD ROUTES (if running) ===")
BASE = "http://127.0.0.1:8787"
def hit(path, method="GET", body=None):
    try:
        req = urllib.request.Request(BASE + path, method=method,
                                     data=(body.encode() if body else None),
                                     headers={"Content-Type": "application/json"} if body else {})
        r = urllib.request.urlopen(req, timeout=8)
        return r.status, r.read()
    except Exception as e:
        return None, str(e)
st, _ = hit("/")
if st is None:
    warn("dashboard not running — skipping route checks (start it to test)")
else:
    for path in ["/", "/api/state", "/api/engine", "/api/custom_maps"]:
        s, _ = hit(path)
        (ok if s == 200 else fail)(f"GET {path} -> {s}")
    s, b = hit("/api/watchlist", "POST", '{"action":"noop","ticker":"ZZZZ"}')
    (ok if s == 200 else fail)(f"POST /api/watchlist -> {s}")

print("\n=== 7. SCRIPTS/GATES SMOKE ===")
import subprocess
for cmd in [["tools/web_coverage.py"], ["pipeline/ledger.py", "sweep"]]:
    r = subprocess.run([sys.executable] + cmd, cwd=ROOT, capture_output=True, text=True)
    last = (r.stdout or r.stderr).strip().splitlines()[-1] if (r.stdout or r.stderr) else ""
    (ok if r.returncode == 0 else fail)(f"{' '.join(cmd)} -> rc={r.returncode} :: {last[:70]}")

print("\n=== 8. RECENT LOG ERRORS ===")
lg = ROOT / "logs" / "ingest.log"
if lg.exists():
    tail = lg.read_text(encoding="utf-8", errors="replace").splitlines()[-60:]
    ferr = [l for l in tail if "FATAL" in l or "Traceback" in l]
    (ok if not ferr else warn)(f"FATAL/traceback in last 60 log lines: {len(ferr)}")
    fails_feed = [l.split("feed fail ")[1].split(":")[0] for l in tail if "feed fail" in l]
    if fails_feed:
        warn(f"feed failures (last 60): {set(fails_feed)}")
    else:
        ok("no feed failures in last 60 lines")

print("\n" + "=" * 50)
print(f"SUMMARY: {len(fails)} FAIL, {len(warns)} WARN")
if fails:
    print("FAILURES:"); [print("  - " + f) for f in fails]
if warns:
    print("WARNINGS:"); [print("  - " + w) for w in warns]
print("ALL CLEAR" if not fails else "DEBUG FOUND FAILURES")
sys.exit(1 if fails else 0)
