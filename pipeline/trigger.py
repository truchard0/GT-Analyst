#!/usr/bin/env python3
"""Auto-trigger worker: runs headless `claude -p` analysis on a watchlist-matched
batch, behind a guardrail gauntlet. Spawned detached by ingest.py.

Gauntlet (any failure -> log decision, exit; extras are DROPPED, never queued):
  enabled? -> dry_run? -> lockfile free? -> hourly cap? -> daily cap? -> cooldown?

State lives in ledger/seen.db (trigger_log, ticker_cooldown); every decision is
mirrored as a JSON line in logs/autoruns.jsonl for grep-ability.
"""
import argparse
import datetime
import json
import os
import pathlib
import sqlite3
import subprocess
import sys
import time
import traceback

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from common import ROOT, load_env, load_json, log, resolve_claude, utc_iso, utc_now, utc_stamp

LOGFILE = ROOT / "logs" / "trigger.log"
AUTORUNS = ROOT / "logs" / "autoruns.jsonl"
LOCK = ROOT / "logs" / "trigger.lock"

DEFAULTS = {
    "enabled": True, "dry_run": True,
    "per_ticker_cooldown_min": 90, "max_runs_per_hour": 2, "max_runs_per_day": 8,
    "lock_stale_min": 45, "model": "sonnet", "max_turns": 25,
}


def cfg():
    c = load_json(ROOT / "config.json", {}) or {}
    merged = dict(DEFAULTS)
    merged.update(c.get("auto_trigger", {}))
    return merged


def state_db():
    c = sqlite3.connect(ROOT / "ledger" / "seen.db")
    c.execute("""CREATE TABLE IF NOT EXISTS trigger_log(
        id INTEGER PRIMARY KEY, ts TEXT, tickers TEXT, batch TEXT,
        decision TEXT, rc INTEGER, duration_s REAL)""")
    c.execute("CREATE TABLE IF NOT EXISTS ticker_cooldown(ticker TEXT PRIMARY KEY, last_ts TEXT)")
    return c


def record(c, tickers, batch, decision, rc=None, duration=None, cmd=None):
    c.execute("INSERT INTO trigger_log(ts,tickers,batch,decision,rc,duration_s) VALUES(?,?,?,?,?,?)",
              (utc_iso(), tickers, batch, decision, rc, duration))
    c.commit()
    AUTORUNS.parent.mkdir(parents=True, exist_ok=True)
    with open(AUTORUNS, "a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": utc_iso(), "tickers": tickers, "batch": batch,
                            "decision": decision, "rc": rc, "duration_s": duration,
                            "cmd": cmd}) + "\n")
    log(LOGFILE, f"{decision} tickers={tickers} batch={batch}")


def ran_count_since(c, cutoff_iso):
    return c.execute("SELECT COUNT(*) FROM trigger_log WHERE decision='ran' AND ts>?",
                     (cutoff_iso,)).fetchone()[0]


def acquire_lock(stale_min):
    if LOCK.exists():
        age_min = (time.time() - LOCK.stat().st_mtime) / 60
        if age_min < stale_min:
            return False
        LOCK.unlink(missing_ok=True)  # stale lock from a killed process
    try:
        fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)  # atomic on NTFS
        os.write(fd, f"{os.getpid()} {utc_iso()}".encode())
        os.close(fd)
        return True
    except FileExistsError:
        return False


def build_cmd(conf, batch_rel, tickers, claude_bin):
    stamp = utc_stamp()
    slug = tickers.replace(",", "-")
    prompt = (
        f"Follow CLAUDE.md exactly, including the conviction rubric and triggered-batch rules. "
        f"Analyze ONLY {batch_rel} (watchlist tickers: {tickers}). Triage per doctrine 12.1 first; "
        f"if the items are rhetoric-layer noise, write a 3-line triage verdict and stop — that is a "
        f"valid, cheap output. For capital-committed events run the full output schema with "
        f"conviction breakdown, sectors, tickers, direction; log predictions with "
        f"python pipeline/ledger.py add --source auto ...; write the report to "
        f"reports/auto/{stamp}_{slug}.md")
    return [claude_bin, "-p", prompt,
            "--allowedTools", "Read,Glob,Grep,Write,Bash(python pipeline/ledger.py *)",
            "--model", conf["model"], "--max-turns", str(conf["max_turns"])]


def _find_new_report(since_ts):
    """Newest reports/auto/*.md created since the run started (for the notification)."""
    d = ROOT / "reports" / "auto"
    if not d.exists():
        return None
    fresh = [f for f in d.glob("*.md") if f.stat().st_mtime >= since_ts - 2]
    if not fresh:
        return None
    newest = max(fresh, key=lambda f: f.stat().st_mtime)
    return f"reports/auto/{newest.name}"


def main():
    load_env()
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", required=True)
    ap.add_argument("--tickers", required=True)
    args = ap.parse_args()
    conf = cfg()
    c = state_db()
    batch_rel = str(pathlib.Path(args.batch).resolve().relative_to(ROOT)).replace("\\", "/")

    if not conf["enabled"]:
        record(c, args.tickers, batch_rel, "disabled")
        return

    # cooldown filter BEFORE spending a run slot
    now = utc_now()
    survivors = []
    for t in args.tickers.split(","):
        row = c.execute("SELECT last_ts FROM ticker_cooldown WHERE ticker=?", (t,)).fetchone()
        if row:
            last = datetime.datetime.strptime(row[0], "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=datetime.UTC)
            if (now - last).total_seconds() / 60 < conf["per_ticker_cooldown_min"]:
                continue
        survivors.append(t)
    if not survivors:
        record(c, args.tickers, batch_rel, "blocked_cooldown")
        return
    tickers = ",".join(survivors)

    if conf["dry_run"]:
        # log the exact would-be command; consume NO budget/cooldown/lock.
        # A missing CLI is fine in dry-run — use a placeholder so the user
        # can still inspect what WOULD run.
        try:
            claude_bin = resolve_claude()
        except FileNotFoundError:
            claude_bin = "<claude: set CLAUDE_BIN in .env>"
        record(c, tickers, batch_rel, "dry_run",
               cmd=build_cmd(conf, batch_rel, tickers, claude_bin))
        return

    try:
        cmd = build_cmd(conf, batch_rel, tickers, resolve_claude())
    except FileNotFoundError as e:
        record(c, tickers, batch_rel, "error", cmd=str(e))
        return

    hour_ago = (now - datetime.timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    if ran_count_since(c, hour_ago) >= conf["max_runs_per_hour"]:
        record(c, tickers, batch_rel, "blocked_hourly")
        return
    midnight = now.strftime("%Y-%m-%dT00:00:00Z")
    if ran_count_since(c, midnight) >= conf["max_runs_per_day"]:
        record(c, tickers, batch_rel, "blocked_daily")
        return

    if not acquire_lock(conf["lock_stale_min"]):
        record(c, tickers, batch_rel, "blocked_lock")
        return

    try:
        t0 = time.time()
        r = subprocess.run(cmd, cwd=ROOT, timeout=1800, capture_output=True, text=True)
        dur = round(time.time() - t0, 1)
        for t in survivors:
            c.execute("INSERT INTO ticker_cooldown VALUES(?,?) "
                      "ON CONFLICT(ticker) DO UPDATE SET last_ts=excluded.last_ts",
                      (t, utc_iso()))
        record(c, tickers, batch_rel, "ran", rc=r.returncode, duration=dur, cmd=cmd)
        # Notify (user chose: auto-trigger analysis ran). Best-effort, never blocks.
        try:
            from notify import send as notify_send
            report = _find_new_report(t0)
            status = "ok" if r.returncode == 0 else f"rc={r.returncode}"
            msg = f"GT-Analyst: auto-analysis ran [{tickers}] {status}"
            if report:
                msg += f" -> {report}"
            notify_send(msg)
        except Exception as e:
            log(LOGFILE, f"notify error: {e}")
        if r.returncode != 0:
            log(LOGFILE, f"claude stderr: {r.stderr[:500]}")
    except subprocess.TimeoutExpired:
        record(c, tickers, batch_rel, "error", cmd="timeout after 1800s")
    finally:
        LOCK.unlink(missing_ok=True)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log(LOGFILE, "FATAL " + traceback.format_exc().replace("\n", " | "))
        raise
