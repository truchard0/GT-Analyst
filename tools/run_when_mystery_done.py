#!/usr/bin/env python3
"""run_when_mystery_done.py - ONE-SHOT: wait for the Mystery Machine's month backfill to finish, then run
        python tools/mystery_events.py --since 2026-09-29 --write
        python tools/events_merge.py --write
and exit. It registers nothing (no scheduled task), runs once, and gives up after --max-hours.

It only WATCHES their process (a read-only `pgrep` inside WSL) and READS their output; it never signals, stops or
writes to their job. Everything it does is appended to logs/mystery_merge.log.

    python tools/run_when_mystery_done.py --check      # report the state once and exit (changes nothing)
    python tools/run_when_mystery_done.py              # wait, then run the two commands, then exit
Stop it any time:  Stop-Process -Id (Get-Content logs\\mystery_watch.pid)
"""
import argparse
import datetime as dt
import glob
import os
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
NEWS = ROOT.parent / "Trading Bot" / "tradingview" / "_skylit" / "news_ai"
LOG = ROOT / "logs" / "mystery_merge.log"
PATTERN = "[b]ackfill-ai"          # the [b] stops pgrep from matching its own command line
TARGET_LAST_DAY = "2026-10-21"


def log(msg):
    LOG.parent.mkdir(exist_ok=True)
    line = f"{dt.datetime.now():%Y-%m-%d %H:%M:%S}  {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def running():
    r = subprocess.run(["wsl", "-e", "bash", "-lc", f"pgrep -f '{PATTERN}' | wc -l"], capture_output=True, text=True, timeout=60)
    return int((r.stdout or "0").strip() or 0) > 0


def progress():
    days = sorted(os.path.basename(d) for d in glob.glob(str(NEWS / "2026-*")) if os.path.isdir(d))
    n = 0
    for d in days:
        p = NEWS / d / "ai_scores.jsonl"
        if p.exists():
            n += sum(1 for _ in open(p, encoding="utf-8"))
    return days, n


def run(cmd):
    log("RUN  " + " ".join(cmd[1:]))
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    for line in (r.stdout or "").strip().splitlines()[-8:]:
        log("     " + line)
    if r.returncode:
        log(f"     !! exit code {r.returncode}: {(r.stderr or '')[-300:]}")
    return r.returncode


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--poll-min", type=float, default=5.0)
    ap.add_argument("--max-hours", type=float, default=18.0)
    a = ap.parse_args()

    days, n = progress()
    state = "RUNNING" if running() else "NOT running"
    print(f"backfill process: {state}   days with output: {len(days)} ({days[0] if days else '-'} .. {days[-1] if days else '-'})   "
          f"headlines scored: {n:,}   target last day {TARGET_LAST_DAY}")
    if a.check:
        return 0

    (ROOT / "logs").mkdir(exist_ok=True)
    (ROOT / "logs" / "mystery_watch.pid").write_text(str(os.getpid()), encoding="utf-8")
    log(f"watching (pid {os.getpid()}); will give up after {a.max_hours}h. Backfill: {state}, {len(days)} days, {n:,} headlines")
    deadline = time.time() + a.max_hours * 3600
    gone = 0
    while time.time() < deadline:
        gone = gone + 1 if not running() else 0
        if gone >= 2:                       # not running on two consecutive polls: finished, not a blip
            break
        time.sleep(a.poll_min * 60)
    else:
        log("GAVE UP: the backfill was still running at the deadline - nothing was run")
        return 2

    days, n = progress()
    complete = bool(days) and days[-1] >= TARGET_LAST_DAY
    log(f"backfill process has exited. {len(days)} days ({days[0]} .. {days[-1]}), {n:,} headlines. "
        + ("COMPLETE to " + TARGET_LAST_DAY if complete else f"ENDED EARLY (last day {days[-1]} < {TARGET_LAST_DAY}) - merging what exists; re-run later"))
    py = sys.executable
    rc = run([py, str(ROOT / "tools" / "mystery_events.py"), "--since", "2026-09-29", "--write"])
    if rc == 0:
        rc = run([py, str(ROOT / "tools" / "events_merge.py"), "--write"])
    log("DONE" if rc == 0 else f"STOPPED with errors (rc {rc}) - see above")
    return rc


if __name__ == "__main__":
    sys.exit(main())
