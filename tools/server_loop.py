#!/usr/bin/env python3
"""GT-Analyst as ONE supervised server process. Stdlib only, Python 3.11+.

It replaces the Windows 5-minute task and the Claude cloud scheduled runs. A supervisor keeps it alive: the
Printer fork's watchdog (through its gt_analyst_runner.py), systemd, or a terminal.

    python3 tools/server_loop.py            # run forever
    python3 tools/server_loop.py --once     # one ingest and one daily cycle now, then exit (exit 1 if a gate fails)
    python3 tools/server_loop.py --status   # print the status file

EVERY TICK (GT_TICK_S, default 300 s, aligned to the wall clock: :00:20, :05:20, ...)
    1 pipeline/drills.py tick   practice questions about world events: settle what is due, then, every
                                GT_DRILL_NEWS_EVERY_MIN minutes (default 60, down to 5), write new questions from
                                the latest news and answer them. Up to three small Claude calls per round when the
                                CLI is installed (GT_DRILL_ANALYST=0 turns them off). Market questions stay off
                                unless GT_DRILL_PRICES=1.
    2 pipeline/ingest.py        news. Watchlist triggers stay dry-run unless config.json turns them on, so
                                ingest alone never spends Claude usage.
ONCE A DAY (after GT_DAILY_UTC, default 13:17 UTC)
    1 git pull            merge only. A conflict aborts the merge and is reported; it is never settled by picking
                          a side (ledger.db cannot be merged). The cycle is retried an hour later.
    2 tape data           precursor log, AI-financing index
    3 learning loop       pipeline/learn.py nightly (train, validate, shadow, scoreboard); drills.py report
    4 due calls           pipeline/ledger.py due
    5 scoring             only when calls are due AND the `claude` CLI is installed: one headless run that
                          researches each outcome, resolves it and records the lesson. GT_CLAUDE_SCORING=0 turns
                          it off. Without Claude the due calls are listed in the status file as needs_scoring.
    6 gates               ledger.py sweep, tools/web_coverage.py, tools/debug_all.py
    7 commit and push     only the bot's own paths. A refused push is shown in the status and retried every tick.

STATUS. GT_HEARTBEAT (default logs/server_status.json) is rewritten before every step: state, due calls,
needs_scoring, gate results, push_ok, unpushed commits, last error. A stale file means the loop is wedged.
The loop never logs new predictions and never places trades.
"""
import datetime
import json
import os
import pathlib
import re
import shutil
import signal
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
PY = sys.executable or "python3"
TICK_S = int(os.environ.get("GT_TICK_S", "300"))
DAILY_UTC = os.environ.get("GT_DAILY_UTC", "13:17")
STATUS = pathlib.Path(os.environ.get("GT_HEARTBEAT") or (ROOT / "logs" / "server_status.json"))
STATE = ROOT / "logs" / "server_state.json"            # survives restarts; logs/ is git-ignored
INBOX = ROOT / "inbox" / "latest.md"
INBOX_ROTATE_BYTES = 2 * 1024 * 1024
SCORING_TIMEOUT_S = 45 * 60
COMMIT_PATHS = ["data/ai_stress", "data/ceasefire/precursor_log.csv", "data/learn", "data/drills", "data/timelines.json",
                "ledger/ledger.db", "STATE.md", "reports", ".claude/skills"]
FALLBACK_IDENT = ["-c", "user.name=GT-Analyst server", "-c", "user.email=gt-analyst-server@users.noreply.github.com"]

SCORING_PROMPT = """You are the GT-Analyst scoring run on the server. These predictions are past their horizon: {ids}.
Read CLAUDE.md and STATE.md first. Then, for each one:
1. Research its outcome from primary or top-tier sources dated after the call was logged, and cite them.
2. Resolve it against its pre-registered falsifier: `python3 pipeline/ledger.py resolve <id> <1|0>`. Where the
   falsifier is defective (rival-branch, escape-clause or conjunctive), score the substance and say so.
3. Record `python3 pipeline/ledger.py lesson <id> --verdict ... --diagnosis ... --patch ...`, naming the premise
   that held or failed. A repeated miss-shape needs a patch in the named skill file.
4. Update the matching node in data/timelines.json (p, evidence with its reported date, resolved label) and
   STATE.md's scoreboard and live-calls table.
Finish by running `python3 pipeline/ledger.py sweep` and `python3 tools/web_coverage.py` until both pass.
If you cannot establish an outcome from sources, leave that call open and say why. Never guess an outcome.
Do not log new predictions, do not run git (the server loop commits and pushes), and never place trades."""
SCORING_TOOLS = ("Read,Glob,Grep,Edit,Write,WebSearch,WebFetch,"
                 "Bash(python3 pipeline/ledger.py *),Bash(python pipeline/ledger.py *),"
                 "Bash(python3 tools/web_coverage.py*),Bash(python3 tools/debug_all.py*)")

status = {"pid": os.getpid(), "started_utc": None, "state": "starting"}
STOP = False
CHILD = None


def now():
    return datetime.datetime.now(datetime.timezone.utc)


def iso(t=None):
    return (t or now()).strftime("%Y-%m-%dT%H:%M:%SZ")


def say(msg):
    print(f"{iso()} {msg}", flush=True)


def beat(**kw):
    """Update the status dict and rewrite the heartbeat file atomically."""
    status.update(kw)
    status["ts"] = iso()
    try:
        STATUS.parent.mkdir(parents=True, exist_ok=True)
        tmp = STATUS.with_name(STATUS.name + ".tmp")
        tmp.write_text(json.dumps(status, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        os.replace(tmp, STATUS)
    except Exception as e:                                 # a full disk must not kill the loop
        say(f"status write failed: {e}")


def load_state():
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(st):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(st, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def run(cmd, timeout, label):
    """Run one child with a time cap. Returns (rc, last lines of output). rc 124 = timed out, 125 = not started."""
    global CHILD
    beat(state=label)
    try:
        CHILD = subprocess.Popen(cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 stdin=subprocess.DEVNULL, text=True, errors="replace")
    except Exception as e:
        say(f"{label}: could not start ({e})")
        return 125, str(e)
    try:
        out, _ = CHILD.communicate(timeout=timeout)
        rc = CHILD.returncode
    except subprocess.TimeoutExpired:
        CHILD.kill()
        out, _ = CHILD.communicate()
        rc = 124
    finally:
        CHILD = None
    tail = "\n".join((out or "").strip().splitlines()[-6:])
    say(f"{label}: rc={rc}" + (f" | {tail.splitlines()[-1][:160]}" if tail else ""))
    return rc, tail


def git(*args, timeout=180, label=None, ident=False):
    return run(["git"] + (FALLBACK_IDENT if ident else []) + list(args), timeout, label or f"git {args[0]}")


def git_out(*args):
    try:
        return subprocess.run(["git"] + list(args), cwd=ROOT, capture_output=True, text=True, timeout=60).stdout.strip()
    except Exception:
        return ""


def unpushed():
    n = git_out("rev-list", "--count", "@{u}..HEAD")
    return int(n) if n.isdigit() else None


def push(dry=False):
    """Push (or dry-run it). Records push_ok and the reason when it is refused."""
    args = ["push"] + (["--dry-run"] if dry else [])
    rc, tail = git(*args, label="push check" if dry else "git push")
    if rc != 0 and "no upstream" in tail.lower():
        rc, tail = git(*(args + ["-u", "origin", "HEAD"]), label="git push (set upstream)")
    beat(push_ok=(rc == 0), push_error=("" if rc == 0 else tail[-300:]), unpushed=unpushed())
    return rc == 0


def claude_bin():
    if os.environ.get("GT_CLAUDE_SCORING", "1") == "0":
        return None
    return os.environ.get("CLAUDE_BIN") or shutil.which("claude")


def due_ids():
    beat(state="due")
    try:
        out = subprocess.run([PY, "pipeline/ledger.py", "due"], cwd=ROOT, capture_output=True, text=True,
                             timeout=60).stdout
    except Exception as e:
        say(f"due: failed ({e})")
        return []
    ids = [int(m) for m in re.findall(r"^#(\d+) due ", out, flags=re.M)]
    say(f"due: {ids if ids else 'nothing due'}")
    return ids


def ingest():
    rc, _ = run([PY, "pipeline/ingest.py"], 420, "ingest")
    beat(last_ingest_utc=iso(), last_ingest_rc=rc)
    try:                                                   # nobody analyses the inbox on the server: keep it bounded
        if INBOX.exists() and INBOX.stat().st_size > INBOX_ROTATE_BYTES:
            dest = INBOX.parent / "processed" / f"{now().strftime('%Y%m%dT%H%M%SZ')}_unanalysed.md"
            dest.parent.mkdir(parents=True, exist_ok=True)
            INBOX.rename(dest)
            say(f"inbox rotated to {dest.name}")
    except Exception as e:
        say(f"inbox rotation failed: {e}")


def drills():
    rc, tail = run([PY, "pipeline/drills.py", "tick"], 420, "drills")
    beat(last_drills=(tail.splitlines()[-1][:200] if tail else f"rc={rc}"))


def commit_and_push(message):
    paths = [p for p in COMMIT_PATHS if (ROOT / p).exists()]
    git("add", "--", *paths, label="git add")
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT).returncode == 0:
        say("nothing to commit")
    else:
        rc, tail = git("commit", "-q", "-m", message, label="git commit")
        if rc != 0 and ("identity" in tail.lower() or "user.email" in tail.lower()):
            rc, tail = git("commit", "-q", "-m", message, label="git commit (fallback identity)", ident=True)
        if rc != 0:
            beat(last_error=f"commit failed: {tail[-200:]}")
            return False
    if unpushed() == 0:
        beat(push_ok=True, push_error="", unpushed=0)
        return True
    return push()


def daily_cycle():
    """One full cycle. Returns True when it finished (even with a failed gate), False when it must be retried."""
    today = now().strftime("%Y-%m-%d")
    say(f"daily cycle {today} starting")
    rc, tail = git("pull", "--no-rebase", "--no-edit", label="git pull")
    if rc != 0:
        if (ROOT / ".git" / "MERGE_HEAD").exists():
            git("merge", "--abort", label="git merge --abort")
            beat(state="CONFLICT", last_error="pull hit a merge conflict; merge aborted, nothing changed. "
                 "Reconcile by hand (never pick a side on ledger.db).")
            return False
        beat(last_error=f"pull failed (continuing on the local copy): {tail[-200:]}")
    run([PY, "tools/precursor_log.py", "update"], 180, "precursor log")
    since = (now() - datetime.timedelta(days=5)).strftime("%Y-%m-%d")
    if run([PY, "tools/ai_stress_index.py", "fetch", "--from", since], 900, "ai-stress fetch")[0] == 0:
        run([PY, "tools/ai_stress_index.py", "build"], 180, "ai-stress build")
    run([PY, "pipeline/learn.py", "nightly"], 180, "learning loop")
    run([PY, "pipeline/drills.py", "report"], 180, "drills report")

    due = due_ids()
    scored_with = None
    if due:
        cb = claude_bin()
        if cb:
            cmd = [cb, "-p", SCORING_PROMPT.format(ids=", ".join(f"#{i}" for i in due)),
                   "--allowedTools", SCORING_TOOLS, "--max-turns", "80"]
            if os.environ.get("GT_CLAUDE_MODEL"):
                cmd += ["--model", os.environ["GT_CLAUDE_MODEL"]]
            run(cmd, SCORING_TIMEOUT_S, f"scoring {len(due)} due call(s) with claude")
            scored_with = cb
            run([PY, "pipeline/learn.py", "nightly"], 180, "learning loop (after scoring)")
        else:
            say(f"{len(due)} call(s) due and no claude CLI: {due} stay unscored")
    still = due_ids() if due else []

    gates = {"sweep": run([PY, "pipeline/ledger.py", "sweep"], 120, "gate: sweep")[0] == 0,
             "web_coverage": run([PY, "tools/web_coverage.py"], 120, "gate: web coverage")[0] == 0}
    rc, tail = run([PY, "tools/debug_all.py"], 300, "gate: debug")
    gates["debug"] = "ALL CLEAR" in tail
    beat(due=due, needs_scoring=still, scored_with=scored_with, gates=gates, last_cycle_utc=iso(),
         last_error=("" if not still else f"{len(still)} due call(s) unscored: {still}"))
    what = f"scored {len(due) - len(still)} of {len(due)} due" if due else "nothing due"
    commit_and_push(f"Server cycle {today}: tape refresh, learning loop; {what}")
    return True


def cycle_due(st):
    """True once per UTC day, at or after DAILY_UTC, and not before a retry backoff expires."""
    t = now()
    if st.get("last_cycle_date") == t.strftime("%Y-%m-%d"):
        return False
    if time.time() < st.get("retry_after", 0):
        return False
    hh, mm = (int(x) for x in DAILY_UTC.split(":"))
    return (t.hour, t.minute) >= (hh, mm)


def stop(signum, frame):
    global STOP
    STOP = True
    if CHILD is not None:
        try:
            CHILD.terminate()
        except Exception:
            pass


def main():
    if "--status" in sys.argv:
        print(STATUS.read_text(encoding="utf-8") if STATUS.exists() else "no status file yet")
        return 0
    os.chdir(ROOT)
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    once = "--once" in sys.argv
    beat(started_utc=iso(), state="starting", root=str(ROOT), python=sys.version.split()[0],
         branch=git_out("rev-parse", "--abbrev-ref", "HEAD"), head=git_out("rev-parse", "--short", "HEAD"),
         claude=claude_bin(), tick_s=TICK_S, daily_utc=DAILY_UTC)
    say(f"server loop up: root={ROOT} branch={status['branch']} claude={status['claude']}")
    if not push(dry=True):
        say("WARNING: a test push was refused. Work will be committed locally and pushes retried every tick. "
            "Fix the git credentials on this machine.")
    st = load_state()
    while not STOP:
        drills()                                           # first: its rounds are tied to the clock
        if STOP:
            break
        ingest()
        if STOP:
            break
        if once or cycle_due(st):
            if daily_cycle():
                st.update(last_cycle_date=now().strftime("%Y-%m-%d"), retry_after=0)
            else:
                st["retry_after"] = time.time() + 3600
            save_state(st)
        elif status.get("unpushed"):
            push()
        beat(state="idle", head=git_out("rev-parse", "--short", "HEAD"))
        if once:
            g = status.get("gates") or {}
            return 0 if g and all(g.values()) else 1
        nxt = (int(time.time()) // TICK_S + 1) * TICK_S + 20     # the next wall-clock boundary, plus 20 s for data
        while not STOP and time.time() < nxt:
            time.sleep(2)
    beat(state="stopped")
    say("server loop stopped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
