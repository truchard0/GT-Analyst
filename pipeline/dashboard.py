#!/usr/bin/env python3
"""GT-Analyst dashboard — stdlib-only local web UI. Zero dependencies.

  python pipeline/dashboard.py        # serve http://127.0.0.1:8787
  python pipeline/dashboard.py 9000   # custom port

Reads ledger.db / seen.db / inbox / reports / logs, and (via POST actions on
loopback only) can trigger ingestion and headless `claude` analysis to create
new reports. Bind is localhost-only; never trades.
"""
import html
import json
import os
import pathlib
import re
import socket
import sqlite3
import subprocess
import sys
import threading
from datetime import datetime, timezone, date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, unquote

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from common import ROOT, resolve_claude, load_env, utc_iso, utc_stamp

LEDGER = ROOT / "ledger" / "ledger.db"
SEEN = ROOT / "ledger" / "seen.db"
INGEST_LOG = ROOT / "logs" / "ingest.log"
AUTORUNS = ROOT / "logs" / "autoruns.jsonl"
JOBS_FILE = ROOT / "logs" / "jobs.jsonl"

RUN_RE = re.compile(
    r"run=(\d+) feeds_ok=(\d+)/(\d+) apis=(\w) new=(\d+) trigger=(.*)$")

# ── job runner (ingest / headless analysis triggered from the UI) ─────────
JOBS = []                        # newest last; running jobs live here in-memory
JOBS_LOCK = threading.Lock()
ANALYZE_LOCK = threading.Lock()  # single-flight: one claude analysis at a time
VALID_MODELS = {"sonnet", "opus", "haiku"}

# ── on-site "Ask the engine" chat (Anthropic API via the SDK) ─────────────
CONFIG_FILE = ROOT / "config.json"
CLAUDE_MD = ROOT / "CLAUDE.md"
ENGINE_MODELS = ["claude-opus-4-8", "claude-fable-5", "claude-sonnet-5", "claude-haiku-4-5"]
ENGINE_DEFAULT_MODEL = "claude-opus-4-8"


def _read_config():
    return load_json(CONFIG_FILE, {})


def engine_cfg():
    return _read_config().get("engine", {}) or {}


def engine_public():
    """Engine config safe to expose to the browser — never the API key itself."""
    e = engine_cfg()
    return {"configured": bool(e.get("api_key")),
            "model": e.get("model", ENGINE_DEFAULT_MODEL),
            "thinking": bool(e.get("thinking", True)),
            "models": ENGINE_MODELS}


def save_engine_cfg(model, api_key, thinking):
    cfg = _read_config()
    e = cfg.get("engine", {}) or {}
    if model in ENGINE_MODELS:
        e["model"] = model
    e["thinking"] = bool(thinking)
    if api_key:                       # blank on save = keep the existing key
        e["api_key"] = api_key
    cfg["engine"] = e
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    return engine_public()


def _trim(txt, n):
    txt = (txt or "").strip()
    return txt if len(txt) <= n else txt[:n] + " …"


def engine_context(state):
    """Assemble the system prompt: doctrine identity + live engine state."""
    parts = []
    if CLAUDE_MD.exists():
        parts.append("## OPERATING DOCTRINE (from CLAUDE.md)\n"
                     + _trim(CLAUDE_MD.read_text(encoding="utf-8", errors="replace"), 3500))
    tl = state.get("timelines") or {}
    nodes = tl.get("nodes", [])
    if nodes:
        lines = [f"NOW: {_trim((tl.get('root') or {}).get('sub', ''), 220)}"]
        for n in nodes[:14]:
            lines.append(f"- [{n.get('kind','?')}] {n.get('label','')} — p={n.get('p','?')} "
                         f"({n.get('horizon','')})")
        parts.append("## LIVE TIMELINE WEB (branch p sums to 1.0)\n" + "\n".join(lines))
    preds = [p for p in state.get("predictions", []) if p.get("status") == "open"][:24]
    if preds:
        lines = [f"#{p['id']} [{p.get('cluster') or '-'}] P={p.get('prob')} "
                 f"conv={p.get('conviction')} {p.get('direction') or ''} {p.get('tickers') or ''} "
                 f":: {_trim(p.get('prediction', ''), 160)}" for p in preds]
        parts.append("## OPEN LEDGER PREDICTIONS (falsifiable, Brier-scored)\n" + "\n".join(lines))
    fus = (state.get("fusion") or {}).get("sectors", {})
    if fus:
        lines = []
        for k, v in fus.items():
            fused = v.get("fused") or {}
            sc = fused.get("score", (v.get("topdown") or {}).get("score"))
            lines.append(f"- {v.get('label', k)} ({v.get('etf','')}): {sc} "
                         f"{fused.get('badge','')} — {_trim(v.get('flag',''), 90)}")
        parts.append("## FUSION SECTOR SCORES (GT top-down × TradingAgents)\n" + "\n".join(lines))
    reps = state.get("reports", [])[:12]
    if reps:
        parts.append("## RECENT REPORTS (reports/ dir)\n"
                     + "\n".join("- " + (r.get("path", "").split("/")[-1]) for r in reps))
    header = ("You are the conversational interface to GT-Analyst, a game-theory news-analysis "
              "prediction engine. Answer from the doctrine and the live state below. Be direct and "
              "specific; cite ledger #IDs, timeline branches, and fusion sector scores when relevant. "
              "Doctrine §14: give direction and mechanism only — never position sizing, never "
              "personalized investment advice; you are not a licensed advisor. Prefer falsifiable "
              "statements and flag uncertainty honestly.\n")
    return header + "\n\n".join(parts)


CUSTOM_DIR = ROOT / "data" / "custom_maps"
CUSTOM_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["title", "lanes", "nodes"],
    "properties": {
        "title": {"type": "string"},
        "lanes": {"type": "array", "items": {"type": "string"}},
        "nodes": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["id", "label", "lane", "date", "kind", "p", "rationale"],
            "properties": {
                "id": {"type": "string"}, "label": {"type": "string"},
                "lane": {"type": "string"}, "date": {"type": "string"},
                "kind": {"type": "string", "enum": ["branch", "event", "checkpoint"]},
                "p": {"type": "number"}, "parent": {"type": "string"},
                "rationale": {"type": "string"}, "market": {"type": "string"},
                "horizon": {"type": "string"},
                "shifts": {"type": "array", "items": {
                    "type": "object", "additionalProperties": False,
                    "required": ["target"],
                    "properties": {"target": {"type": "string"}, "p_to": {"type": "number"},
                                   "date_delta": {"type": "number"}, "note": {"type": "string"}}}}}}}}}

CUSTOM_RULES = (
    "\n## TASK: build a CUSTOM prediction timeline for the user's question\n"
    "Apply the doctrine (escalation calibration, capital-committed vs rhetoric, precondition chains, "
    "chokepoints, scarcity premium, reputation games) to the QUESTION. Emit 8-16 nodes across 2-4 lanes.\n"
    "Rules: kind='checkpoint' = scheduled certainties (data prints, earnings, elections, deadlines) that occur "
    "in EVERY world - give them the date they occur. kind='branch' = mutually exclusive world-states; siblings "
    "under the same parent MUST sum to ~1.0. kind='event' = conditional occurrences (p = given its parent). "
    "dates ISO YYYY-MM-DD (estimate mid-window if uncertain). 'shifts' = conditional edges: if THIS node "
    "resolves true, which other node's probability moves (p_to) and/or date moves (date_delta days, negative "
    "= earlier) - include 3-8 shift edges total, they are the point of the map. Every p falsifiable and "
    "calibrated per the ledger discipline; rationale 1-3 sentences citing doctrine sections or ledger #IDs "
    "where relevant; market = direction/mechanism only, never sizing.")


def custom_map(question):
    e = engine_cfg()
    if not e.get("api_key"):
        return {"ok": False, "error": "No API key set - add one in the Settings tab."}
    try:
        import anthropic
    except ImportError:
        return {"ok": False, "error": "pip install anthropic, then restart the dashboard."}
    try:
        client = anthropic.Anthropic(api_key=e["api_key"], timeout=280.0, max_retries=1)
        resp = client.messages.create(
            model=e.get("model", ENGINE_DEFAULT_MODEL), max_tokens=16000,
            system=[{"type": "text", "text": engine_context(gather_state()) + CUSTOM_RULES,
                     "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": f"QUESTION: {question}"}],
            output_config={"format": {"type": "json_schema", "schema": CUSTOM_SCHEMA}})
    except Exception as ex:
        return {"ok": False, "error": f"API error: {ex}"}
    if getattr(resp, "stop_reason", None) == "refusal":
        return {"ok": False, "error": "The model declined this request."}
    try:
        m = json.loads(next(b.text for b in resp.content if b.type == "text"))
    except (StopIteration, json.JSONDecodeError) as ex:
        return {"ok": False, "error": f"bad map JSON: {ex}"}
    m["question"] = question
    m["generated"] = utc_iso()
    CUSTOM_DIR.mkdir(parents=True, exist_ok=True)
    fname = utc_stamp() + "_" + re.sub(r"[^a-z0-9]+", "-", question.lower())[:40].strip("-") + ".json"
    (CUSTOM_DIR / fname).write_text(json.dumps(m, indent=2), encoding="utf-8")
    m["file"] = fname
    return {"ok": True, "map": m}


def list_custom_maps():
    if not CUSTOM_DIR.exists():
        return []
    out = []
    for f in sorted(CUSTOM_DIR.glob("*.json"), reverse=True)[:20]:
        try:
            j = json.loads(f.read_text(encoding="utf-8"))
            out.append({"file": f.name, "title": j.get("title", f.name),
                        "question": j.get("question", ""), "generated": j.get("generated", "")})
        except (json.JSONDecodeError, OSError):
            pass
    return out


def watchlist_edit(action, ticker, aliases=None, keywords=None):
    ticker = re.sub(r"[^A-Z0-9.]", "", (ticker or "").upper())[:8]
    if not ticker:
        return {"ok": False, "error": "bad ticker"}
    wl_path = ROOT / "watchlist.json"
    wl = load_json(wl_path, {}) or {}
    wl.setdefault("tickers", {})
    cfg = _read_config()
    at = cfg.setdefault("auto_trigger", {})
    autos = set(at.get("auto_tickers", []) or [])
    if action == "add":
        wl["tickers"][ticker] = {
            "aliases": [a.strip() for a in (aliases or "").split(",") if a.strip()][:6],
            "keywords": [k.strip() for k in (keywords or "").split(",") if k.strip()][:6]}
    elif action == "remove":
        wl["tickers"].pop(ticker, None)
        for th in (wl.get("themes") or {}).values():
            (th or {}).get("tickers", {}).pop(ticker, None)
        autos.discard(ticker)
    elif action == "auto":
        autos.add(ticker)
    elif action == "manual":
        autos.discard(ticker)
    else:
        return {"ok": False, "error": "unknown action"}
    at["auto_tickers"] = sorted(autos)
    wl_path.write_text(json.dumps(wl, indent=2), encoding="utf-8")
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    return {"ok": True, "ticker": ticker, "auto": ticker in autos}


ENV_KEYS = ["NEWSAPI_KEY", "FINNHUB_KEY", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID",
            "FRED_API_KEY", "CONGRESS_API_KEY", "EIA_API_KEY"]
TRIGGER_FIELDS = {"enabled": bool, "dry_run": bool, "per_ticker_cooldown_min": int,
                  "max_runs_per_hour": int, "max_runs_per_day": int, "max_turns": int,
                  "lock_stale_min": int, "model": str}


def trigger_settings_save(d):
    cfg = _read_config()
    at = cfg.setdefault("auto_trigger", {})
    for k, typ in TRIGGER_FIELDS.items():
        if k not in d:
            continue
        v = d[k]
        if typ is bool:
            at[k] = bool(v)
        elif typ is int:
            try:
                at[k] = max(1, min(10000, int(v)))
            except (TypeError, ValueError):
                pass
        elif k == "model" and v in VALID_MODELS:
            at[k] = v
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    return {"ok": True, "auto_trigger": at}


def _env_path():
    return ROOT / ".env"


def env_keys_status():
    txt = _env_path().read_text(encoding="utf-8", errors="replace") if _env_path().exists() else ""
    have = {}
    for k in ENV_KEYS:
        m = re.search(rf"^{k}=(.+)$", txt, re.M)
        have[k] = bool(m and m.group(1).strip())
    return have


def env_keys_save(d):
    p = _env_path()
    txt = p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""
    for k in ENV_KEYS:
        v = (d.get(k) or "").strip()
        if not v:
            continue
        if re.search(rf"^{k}=", txt, re.M):
            txt = re.sub(rf"^{k}=.*$", f"{k}={v}", txt, flags=re.M)
        else:
            txt = (txt.rstrip("\n") + "\n" if txt else "") + f"{k}={v}\n"
    p.write_text(txt, encoding="utf-8")
    load_env()
    return {"ok": True, "status": env_keys_status()}


def ask_engine(messages):
    e = engine_cfg()
    key = e.get("api_key")
    if not key:
        return {"ok": False, "error": "No API key set — add one in the Settings tab."}
    try:
        import anthropic
    except ImportError:
        return {"ok": False, "error": "The 'anthropic' package isn't installed. Run: "
                "python -m pip install anthropic  (then restart the dashboard)."}
    model = e.get("model", ENGINE_DEFAULT_MODEL)
    kwargs = dict(model=model, max_tokens=8000,
                  system=[{"type": "text", "text": engine_context(gather_state()),
                           "cache_control": {"type": "ephemeral"}}],
                  messages=messages)
    if e.get("thinking", True):
        kwargs["thinking"] = {"type": "adaptive"}   # omit entirely to disable (safe on Fable too)
    try:
        client = anthropic.Anthropic(api_key=key, timeout=150.0, max_retries=1)
        resp = client.messages.create(**kwargs)
    except anthropic.AuthenticationError:
        return {"ok": False, "error": "Authentication failed — check the API key in Settings."}
    except anthropic.RateLimitError:
        return {"ok": False, "error": "Rate limited by the API — wait a moment and retry."}
    except Exception as ex:
        return {"ok": False, "error": f"API error: {ex}"}
    if getattr(resp, "stop_reason", None) == "refusal":
        return {"ok": False, "error": "The model declined this request (safety refusal)."}
    text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
    u = getattr(resp, "usage", None)
    return {"ok": True, "text": text, "model": getattr(resp, "model", model),
            "usage": {"in": getattr(u, "input_tokens", 0), "out": getattr(u, "output_tokens", 0)} if u else {}}


def load_jobs():
    global JOBS
    if not JOBS_FILE.exists():
        return
    rows = []
    for ln in JOBS_FILE.read_text(encoding="utf-8", errors="replace").splitlines()[-40:]:
        try:
            rows.append(json.loads(ln))
        except json.JSONDecodeError:
            pass
    JOBS = rows


def add_job(kind, focus="", model=""):
    with JOBS_LOCK:
        jid = (JOBS[-1]["id"] + 1) if JOBS else 1
        job = {"id": jid, "kind": kind, "focus": focus, "model": model,
               "status": "running", "started": utc_iso(), "finished": None,
               "report": None, "rc": None, "message": ""}
        JOBS.append(job)
    return job


def finish_job(job, **kw):
    with JOBS_LOCK:
        job.update(kw)
        job["finished"] = utc_iso()
        snapshot = dict(job)
    try:
        JOBS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(JOBS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(snapshot) + "\n")
    except OSError:
        pass


def run_ingest_job(job):
    try:
        r = subprocess.run([sys.executable, str(ROOT / "pipeline" / "ingest.py")],
                           cwd=ROOT, capture_output=True, text=True, timeout=240)
        msg = (r.stdout or r.stderr or "").strip().splitlines()
        finish_job(job, status="done" if r.returncode == 0 else "error",
                   rc=r.returncode, message=(msg[-1] if msg else ""))
    except Exception as e:
        finish_job(job, status="error", message=str(e)[:300])


def run_analyze_job(job, focus, model):
    if not ANALYZE_LOCK.acquire(blocking=False):
        finish_job(job, status="error", message="another analysis is already running")
        return
    try:
        load_env()
        try:
            claude = resolve_claude()
        except FileNotFoundError as e:
            finish_job(job, status="error", message=str(e))
            return
        stamp = utc_stamp()
        if focus.strip():
            slug = re.sub(r"[^a-z0-9]+", "-", focus.lower()).strip("-")[:32] or "analysis"
            rel = f"reports/{stamp}_{slug}.md"
            prompt = (
                "Follow CLAUDE.md exactly (both skills, conviction rubric, ledger rules). "
                f"Focus of this analysis: {focus}. Pull the relevant items from inbox/latest.md "
                "(and inbox/processed/ if needed), triage per doctrine 12.1, run the full output "
                "schema for each real event with conviction breakdown, sectors, tickers, direction, "
                "log predictions with python pipeline/ledger.py add, then write the report to "
                f"{rel}")
        else:
            rel = f"reports/{stamp}.md"
            prompt = (
                "Follow CLAUDE.md exactly. Analyze inbox/latest.md: triage per doctrine 12.1, run the "
                "full output schema per event including conviction breakdown, sectors, tickers, direction; "
                "log every prediction with python pipeline/ledger.py add; then write the report to "
                f"{rel} and move inbox/latest.md to inbox/processed/{stamp}.md")
        cmd = [claude, "-p", prompt, "--allowedTools",
               "Read,Glob,Grep,Write,Bash(python pipeline/ledger.py *)", "--model", model]
        try:
            r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=1800)
            report = rel if (ROOT / rel).exists() else None
            tail = (r.stdout or r.stderr or "").strip()[-400:]
            finish_job(job, status="done" if r.returncode == 0 else "error",
                       rc=r.returncode, report=report, message=tail)
        except subprocess.TimeoutExpired:
            finish_job(job, status="error", message="analysis timed out after 30 min")
    finally:
        ANALYZE_LOCK.release()


def run_outlook_job(job, tickers, batch_rel, model):
    """Combined stock + news outlook test on watchlist-triggered ticker(s)."""
    if not ANALYZE_LOCK.acquire(blocking=False):
        finish_job(job, status="error", message="another analysis is already running")
        return
    try:
        load_env()
        try:
            claude = resolve_claude()
        except FileNotFoundError as e:
            finish_job(job, status="error", message=str(e))
            return
        stamp = utc_stamp()
        slug = re.sub(r"[^A-Za-z0-9]+", "-", tickers)[:24].strip("-").lower() or "outlook"
        rel = f"reports/auto/{stamp}_{slug}-outlook.md"
        src = f"inbox/triggered/{batch_rel}" if batch_rel else "inbox/latest.md"
        prompt = (
            "Follow CLAUDE.md exactly (all four skills, conviction rubric, red-team gate, ledger rules). "
            f"OUTLOOK TEST for {tickers}. "
            f"PART 1 — NEWS OUTLOOK: read {src} (watchlist-triggered items) plus any items in inbox/latest.md "
            "matching these tickers. Triage per doctrine 12.1 (note each item's reported timestamp; stale >48h "
            "caps source quality). Run the output schema on real events; 'noise, no thesis update' is a valid verdict. "
            "PART 2 — STOCK OUTLOOK: for each ticker run a compressed TradingAgents-style debate: bull case, bear "
            "case, one rebuttal each, then verdict BUY/HOLD/SELL with confidence 0-1 and key levels. "
            "PART 3 — FUSION: read data/fusion.json, compare your verdict to the sector topdown score, state "
            "CONFIRM/CONFLICT/MIXED, and record each verdict via "
            "python tools/record_ta.py --ticker T --sector <fusion.json sector key> --verdict V --confidence C "
            "--summary '...'. Log any gate-passing predictions with python pipeline/ledger.py add. "
            f"Write the full report to {rel}.")
        cmd = [claude, "-p", prompt, "--allowedTools",
               "Read,Glob,Grep,Write,Bash(python pipeline/ledger.py *),Bash(python tools/record_ta.py *)",
               "--model", model]
        try:
            r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=1500)
            report = rel if (ROOT / rel).exists() else None
            tail = (r.stdout or r.stderr or "").strip()[-400:]
            finish_job(job, status="done" if r.returncode == 0 else "error",
                       rc=r.returncode, report=report, message=tail)
        except subprocess.TimeoutExpired:
            finish_job(job, status="error", message="outlook test timed out after 25 min")
    finally:
        ANALYZE_LOCK.release()


def _basename(p):
    return str(p or "").replace("\\", "/").split("/")[-1]


def render_batch(name):
    """Render a triggered-batch file + link any related auto reports."""
    name = _basename(name)  # sanitize: no path traversal
    if not name.endswith(".md"):
        return '<div class="muted">bad batch name</div>'
    path = ROOT / "inbox" / "triggered" / name
    processed = ROOT / "inbox" / "processed" / name
    if not path.exists() and processed.exists():
        path = processed
    if not path.exists():
        return f'<div class="muted">batch {esc(name)} not found (may have been archived)</div>'
    raw = path.read_text(encoding="utf-8", errors="replace")[:20000]
    # related auto reports: same UTC date + shares a ticker token
    date = name.split("T")[0]
    toks = {t for t in re.split(r"[_\-.]", name.replace(".md", "")) if t.isalpha() and t.isupper()}
    related = []
    auto_dir = ROOT / "reports" / "auto"
    if auto_dir.exists():
        for f in sorted(auto_dir.glob("*.md"), reverse=True)[:60]:
            ftoks = {t for t in re.split(r"[_\-.]", f.stem) if t.isupper()}
            if f.name.startswith(date) and (not toks or toks & ftoks or "outlook" in f.name):
                related.append(f"reports/auto/{f.name}")
    rel_html = ("".join(f'<div>→ <a href="#" class="jslink" data-rep="{esc(r)}">{esc(_basename(r))}</a></div>'
                        for r in related[:6])
                or '<div class="muted small">no auto-report found for this batch yet — run the outlook test below</div>')
    tickers = ",".join(sorted(toks))
    btn = (f'<button class="btn btn-primary" onclick="runOutlook(this,\'{esc(tickers)}\',\'{esc(name)}\')">'
           f'▶ Run stock + news outlook test on {esc(tickers) or "batch"}</button>')
    return (f'<div class="fcard-h"><b>trigger batch</b> <span class="mono small muted">{esc(name)}</span></div>'
            f'<div class="sect">matched items</div><pre class="batch-pre">{esc(raw)}</pre>'
            f'<div class="sect">related reports</div>{rel_html}'
            f'<div style="margin-top:10px">{btn} <span class="muted small">headless run — uses tokens, one at a time</span></div>')


# ── data gathering (all defensive: missing files never crash) ────────────

def _q(dbpath, sql, params=()):
    if not pathlib.Path(dbpath).exists():
        return []
    c = sqlite3.connect(dbpath)
    try:
        c.row_factory = sqlite3.Row
        return [dict(r) for r in c.execute(sql, params).fetchall()]
    except sqlite3.Error:
        return []
    finally:
        c.close()


def _scalar(dbpath, sql, params=(), default=0):
    if not pathlib.Path(dbpath).exists():
        return default
    c = sqlite3.connect(dbpath)
    try:
        r = c.execute(sql, params).fetchone()
        return r[0] if r and r[0] is not None else default
    except sqlite3.Error:
        return default
    finally:
        c.close()


def load_json(path, default):
    p = pathlib.Path(path)
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def parse_ingest_log(limit=400):
    runs, issues = [], []
    p = pathlib.Path(INGEST_LOG)
    if not p.exists():
        return runs, issues
    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()[-limit:]
    for line in lines:
        ts = line[:20].strip()
        m = RUN_RE.search(line)
        if m:
            runs.append({
                "ts": ts, "run": int(m.group(1)),
                "feeds_ok": int(m.group(2)), "feeds_total": int(m.group(3)),
                "apis": m.group(4) == "y", "new": int(m.group(5)),
                "trigger": m.group(6).strip()})
        elif "FATAL" in line or "fail" in line:
            issues.append(line.strip())
    return runs, issues


def parse_autoruns(limit=50):
    p = pathlib.Path(AUTORUNS)
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines()[-limit:]:
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return list(reversed(out))


def list_reports():
    out = []
    for sub, tag in [("", "manual"), ("auto", "auto")]:
        d = ROOT / "reports" / sub if sub else ROOT / "reports"
        if not d.exists():
            continue
        for f in d.glob("*.md"):
            title = f.stem
            try:
                for ln in f.read_text(encoding="utf-8", errors="replace").splitlines():
                    if ln.startswith("# "):
                        title = ln[2:].strip()
                        break
            except OSError:
                pass
            rel = str(f.relative_to(ROOT)).replace("\\", "/")
            mt = f.stat().st_mtime
            out.append({"path": rel, "title": title, "tag": tag, "mtime": mt,
                        "day": datetime.fromtimestamp(mt, timezone.utc).strftime("%Y-%m-%d"),
                        "size_kb": round(f.stat().st_size / 1024, 1)})
    return sorted(out, key=lambda r: r["mtime"], reverse=True)


def inbox_state():
    latest = ROOT / "inbox" / "latest.md"
    processed = ROOT / "inbox" / "processed"
    triggered = ROOT / "inbox" / "triggered"
    src = latest if latest.exists() else None
    if not src:
        procs = sorted(processed.glob("*.md"), key=lambda f: f.stat().st_mtime,
                       reverse=True) if processed.exists() else []
        src = procs[0] if procs else None
    headlines, item_count, src_name = [], 0, "—"
    if src:
        src_name = src.name + ("" if src.name == "latest.md" else " (archived)")
        txt = src.read_text(encoding="utf-8", errors="replace")
        lines = txt.splitlines()
        for i, ln in enumerate(lines):
            if ln.startswith("- **"):
                item_count += 1
                if len(headlines) < 60:
                    m = re.match(r"- \*\*(.+?)\*\* \((.+?)\)", ln)
                    if m:
                        h = {"title": m.group(1), "src": m.group(2), "url": "", "matched": ""}
                        for j in range(i + 1, min(i + 5, len(lines))):
                            nxt = lines[j].strip()
                            if lines[j].startswith("- **"):
                                break
                            if nxt.startswith("http") and not h["url"]:
                                h["url"] = nxt
                            elif nxt.startswith("Matched:"):
                                h["matched"] = nxt[8:].strip()
                            else:
                                mu = re.search(r'href="(https?://[^"]+)"', nxt)
                                if mu and not h["url"]:
                                    h["url"] = mu.group(1)
                        headlines.append(h)
    return {
        "current": "latest.md" if latest.exists() else "none (all analyzed)",
        "showing": src_name,
        "item_count": item_count,
        "headlines": headlines,
        "processed_count": len(list(processed.glob("*.md"))) if processed.exists() else 0,
        "triggered": sorted(
            [f.name for f in triggered.glob("*.md")], reverse=True)
        if triggered.exists() else [],
    }


def feeds_health(recent_issues):
    try:
        from ingest import FEEDS
    except Exception:
        return []
    degraded = " ".join(recent_issues).lower()
    return [{"label": lbl, "url": url,
             "degraded": lbl.lower() in degraded} for url, lbl in FEEDS]


def calibration():
    bands, buckets, sectors = [], [], []
    for label, lo, hi in [("<0.60", 0, .6), ("0.60–0.80", .6, .8), (">0.80", .8, 1.01)]:
        r = _q(LEDGER, "SELECT COUNT(*) n, AVG(brier) b FROM predictions "
               "WHERE status='resolved' AND conviction>=? AND conviction<?", (lo, hi))
        if r and r[0]["n"]:
            bands.append({"label": label, "n": r[0]["n"], "brier": r[0]["b"]})
    for lo, hi in [(0, .4), (.4, .6), (.6, .8), (.8, 1.01)]:
        r = _q(LEDGER, "SELECT COUNT(*) n, AVG(outcome) a FROM predictions "
               "WHERE status='resolved' AND prob>=? AND prob<?", (lo, hi))
        if r and r[0]["n"]:
            buckets.append({"label": f"{int(lo*100)}–{int(hi*100)}%",
                            "n": r[0]["n"], "predicted": (lo + hi) / 2, "actual": r[0]["a"]})
    for row in _q(LEDGER, "SELECT sectors, COUNT(*) n, AVG(brier) b FROM predictions "
                  "WHERE sectors!='' AND sectors IS NOT NULL GROUP BY sectors ORDER BY n DESC"):
        sectors.append({"sectors": row["sectors"], "n": row["n"], "brier": row["b"]})
    return {"bands": bands, "buckets": buckets, "sectors": sectors}


def _telegram_configured():
    p = ROOT / ".env"
    if not p.exists():
        return False
    tok = cid = False
    for ln in p.read_text(encoding="utf-8", errors="replace").splitlines():
        ln = ln.strip()
        if ln.startswith("TELEGRAM_BOT_TOKEN=") and ln.split("=", 1)[1].strip():
            tok = True
        if ln.startswith("TELEGRAM_CHAT_ID=") and ln.split("=", 1)[1].strip():
            cid = True
    return tok and cid


def gather_state():
    runs, issues = parse_ingest_log()
    _wl_raw = load_json(ROOT / "watchlist.json", {})
    _at_cfg = load_json(ROOT / "config.json", {}).get("auto_trigger", {})
    _auto_set = set(_at_cfg.get("auto_tickers", []) or [])
    _wl_flat = dict(_wl_raw.get("tickers", {}) or {})
    for _th in (_wl_raw.get("themes", {}) or {}).values():
        _wl_flat.update((_th or {}).get("tickers", {}) or {})
    preds = _q(LEDGER, "SELECT * FROM predictions ORDER BY id DESC")
    today = date.today().isoformat()
    due = _q(LEDGER, "SELECT id,horizon,prediction,prob,conviction,tickers FROM predictions "
             "WHERE status='open' AND horizon<=? ORDER BY horizon", (today,))
    last_run = runs[-1] if runs else None
    cfg = load_json(ROOT / "config.json", {}).get("auto_trigger", {})
    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"),
        "stats": {
            "total_runs": _scalar(SEEN, "SELECT v FROM run_counter WHERE k='runs'"),
            "items_seen": _scalar(SEEN, "SELECT COUNT(*) FROM seen"),
            "feeds_ok": last_run["feeds_ok"] if last_run else 0,
            "feeds_total": last_run["feeds_total"] if last_run else 0,
            "last_ingest": last_run["ts"] if last_run else "never",
            "open": _scalar(LEDGER, "SELECT COUNT(*) FROM predictions WHERE status='open'"),
            "resolved": _scalar(LEDGER, "SELECT COUNT(*) FROM predictions WHERE status='resolved'"),
            "mean_brier": _scalar(LEDGER, "SELECT AVG(brier) FROM predictions WHERE status='resolved'", default=None),
            "auto_enabled": cfg.get("enabled", False),
            "auto_dry_run": cfg.get("dry_run", True),
        },
        "runs": runs[-40:],
        "issues": issues[-8:],
        "predictions": preds,
        "trades": _q(LEDGER, "SELECT * FROM trades ORDER BY id DESC"),
        "due": due,
        "calibration": calibration(),
        "autoruns": parse_autoruns(),
        "trigger_log": _q(SEEN, "SELECT ts,tickers,decision,rc,duration_s FROM trigger_log ORDER BY id DESC LIMIT 30"),
        "cooldowns": _q(SEEN, "SELECT ticker,last_ts FROM ticker_cooldown ORDER BY last_ts DESC"),
        "watchlist_themes": _wl_raw.get("themes", {}),
        "watchlist_flat": _wl_flat,
        "watchlist_top": _wl_raw.get("tickers", {}) or {},
        "watchlist_count": len(_wl_flat),
        "auto_tickers": sorted(_auto_set),
        "telegram_on": _telegram_configured(),
        "config": _at_cfg,
        "sector_map": {k: v for k, v in load_json(ROOT / "data" / "sector_map.json", {}).items() if not k.startswith("_")},
        "reports": list_reports(),
        "inbox": inbox_state(),
        "feeds": feeds_health(issues),
        "jobs": list(reversed(JOBS[-12:])),
        "analyzing": any(j["status"] == "running" and j["kind"] == "analyze" for j in JOBS),
        "timelines": load_json(ROOT / "data" / "timelines.json", {}),
        "fusion": load_json(ROOT / "data" / "fusion.json", {}),
    }


# ── tiny markdown renderer (for report bodies) ───────────────────────────

def md_to_html(md):
    md = html.escape(md)
    out, in_ul, in_tbl = [], False, False

    def inline(s):
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
        s = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
        return s

    for ln in md.splitlines():
        st = ln.strip()
        if st.startswith("|") and st.endswith("|"):
            cells = [c.strip() for c in st.strip("|").split("|")]
            if set("".join(cells)) <= set("-: "):
                continue  # separator row
            if not in_tbl:
                out.append('<table class="md">')
                in_tbl = True
                out.append("<tr>" + "".join(f"<th>{inline(c)}</th>" for c in cells) + "</tr>")
            else:
                out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>")
            continue
        if in_tbl:
            out.append("</table>")
            in_tbl = False
        if re.match(r"^#{1,4}\s", st):
            lvl = len(st) - len(st.lstrip("#"))
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f"<h{lvl+1}>{inline(st[lvl:].strip())}</h{lvl+1}>")
        elif st.startswith("- "):
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{inline(st[2:])}</li>")
        elif st in ("---", "***", "___"):
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append("<hr>")
        elif not st:
            if in_ul:
                out.append("</ul>")
                in_ul = False
        else:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f"<p>{inline(st)}</p>")
    if in_ul:
        out.append("</ul>")
    if in_tbl:
        out.append("</table>")
    return "\n".join(out)


def render_report(rel_path):
    # path-traversal guard: must resolve under reports/
    try:
        target = (ROOT / unquote(rel_path)).resolve()
        target.relative_to((ROOT / "reports").resolve())
    except (ValueError, OSError):
        return "<p class='muted'>Invalid report path.</p>"
    if not target.exists():
        return "<p class='muted'>Report not found.</p>"
    return md_to_html(target.read_text(encoding="utf-8", errors="replace"))


# ── HTML rendering ───────────────────────────────────────────────────────

def esc(s):
    return html.escape(str(s))


def conv_class(c):
    if c is None:
        return "c-none"
    if c >= 0.8:
        return "c-high"
    if c >= 0.6:
        return "c-med"
    if c >= 0.35:
        return "c-low"
    return "c-noise"


def dir_badge(d):
    d = (d or "").strip()
    if not d:
        return '<span class="dir d-neu">—</span>'
    cls = {"up": "d-up", "down": "d-down", "vol": "d-vol", "neutral": "d-neu"}.get(d, "d-neu")
    arrow = {"up": "▲", "down": "▼", "vol": "◆", "neutral": "—"}.get(d, "·")
    return f'<span class="dir {cls}">{arrow} {esc(d)}</span>'


def stat_card(label, value, sub="", accent=""):
    s = f'<div class="card-s">{sub}</div>' if sub else ""
    return (f'<div class="card {accent}"><div class="card-v">{value}</div>'
            f'<div class="card-l">{esc(label)}</div>{s}</div>')


def render_overview(s):
    st = s["stats"]
    brier = f'{st["mean_brier"]:.3f}' if st["mean_brier"] is not None else "—"
    auto = ('<span class="pill live">LIVE</span>' if st["auto_enabled"] and not st["auto_dry_run"]
            else '<span class="pill dry">DRY-RUN</span>' if st["auto_enabled"]
            else '<span class="pill off">OFF</span>')
    feeds = f'{st["feeds_ok"]}/{st["feeds_total"]}'
    feed_ok = st["feeds_ok"] == st["feeds_total"] and st["feeds_total"] > 0
    cards = "".join([
        stat_card("ingest runs", st["total_runs"], f'last {esc(st["last_ingest"])}'),
        stat_card("feeds healthy", feeds, "all sources" if feed_ok else "degraded", "ok" if feed_ok else "warn"),
        stat_card("items ingested", f'{st["items_seen"]:,}', "deduped, all-time"),
        stat_card("open predictions", st["open"], f'{st["resolved"]} resolved'),
        stat_card("mean Brier", brier, "lower = better", "ok" if (st["mean_brier"] or 1) < .25 else ""),
        stat_card("auto-trigger", auto, "watchlist → tokens"),
    ])
    runs = s["runs"][-30:]
    spark = ""
    if runs:
        vals = [r["new"] for r in runs]
        mx = max(vals) or 1
        w, h, n = 520, 46, len(vals)
        step = w / max(n - 1, 1)
        pts = " ".join(f'{i*step:.1f},{h - (v/mx)*(h-6) - 3:.1f}' for i, v in enumerate(vals))
        spark = (f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="none" class="spark">'
                 f'<polyline points="{pts}" fill="none" stroke="var(--accent)" stroke-width="1.6"/></svg>')
    rows = "".join(
        f'<tr><td class="mono">{esc(r["ts"])}</td><td>{r["run"]}</td>'
        f'<td>{r["feeds_ok"]}/{r["feeds_total"]}</td><td>{"✓" if r["apis"] else "·"}</td>'
        f'<td class="{"hot" if r["new"] else "muted"}">{r["new"]}</td>'
        f'<td class="mono small">{esc(r["trigger"])}</td></tr>'
        for r in reversed(s["runs"][-16:]))
    issues = ""
    if s["issues"]:
        issues = ('<div class="panel warn-panel"><h3>⚠ recent feed issues</h3>'
                  + "".join(f'<div class="mono small">{esc(x)}</div>' for x in s["issues"]) + "</div>")
    return (f'<div class="grid">{cards}</div>'
            f'<div class="panel"><h3>new items / run <span class="muted small">last {len(runs)} runs</span></h3>{spark}</div>'
            f'<div class="panel"><h3>ingest activity</h3><table class="data"><thead><tr>'
            f'<th>time</th><th>run</th><th>feeds</th><th>api</th><th>new</th><th>trigger</th>'
            f'</tr></thead><tbody>{rows}</tbody></table></div>{issues}')


def render_predictions(s):
    due_ids = {d["id"] for d in s["due"]}
    due_banner = ""
    if s["due"]:
        due_banner = ('<div class="panel due-panel"><h3>⏰ due for resolution</h3>'
                      + "".join(f'<div>#{d["id"]} <span class="mono">{esc(d["horizon"])}</span> '
                                f'P={d["prob"]:.0%} [{esc(d["tickers"] or "—")}] {esc(d["prediction"])}</div>'
                                for d in s["due"]) + "</div>")
    cal = s["calibration"]
    band_rows = "".join(
        f'<tr><td>{esc(b["label"])}</td><td>{b["n"]}</td><td>{b["brier"]:.3f}</td></tr>'
        for b in cal["bands"]) or '<tr><td colspan="3" class="muted">no resolved predictions yet</td></tr>'
    calib = (f'<div class="panel half"><h3>conviction bands <span class="muted small">does conviction predict accuracy?</span></h3>'
             f'<table class="data"><thead><tr><th>band</th><th>n</th><th>mean Brier</th></tr></thead>'
             f'<tbody>{band_rows}</tbody></table></div>')
    sec_rows = "".join(
        f'<tr><td>{esc(x["sectors"])}</td><td>{x["n"]}</td>'
        f'<td>{f"{x["brier"]:.3f}" if x["brier"] is not None else "—"}</td></tr>'
        for x in cal["sectors"]) or '<tr><td colspan="3" class="muted">none</td></tr>'
    secs = (f'<div class="panel half"><h3>by sector</h3>'
            f'<table class="data"><thead><tr><th>sectors</th><th>n</th><th>mean Brier</th></tr></thead>'
            f'<tbody>{sec_rows}</tbody></table></div>')
    rows = []
    for p in s["predictions"]:
        c = p.get("conviction")
        cbadge = f'<span class="conv {conv_class(c)}">{c:.2f}</span>' if c is not None else '<span class="conv c-none">—</span>'
        status = p.get("status", "open")
        sbadge = f'<span class="st st-{status}">{status}</span>'
        if status == "resolved" and p.get("brier") is not None:
            sbadge += f' <span class="muted small">B={p["brier"]:.2f}</span>'
        due_mark = ' <span class="due-dot" title="due">●</span>' if p["id"] in due_ids else ""
        rows.append(
            f'<tr class="pred-row"><td>#{p["id"]}{due_mark}</td><td>{cbadge}</td>'
            f'<td>{p["prob"]:.0%}</td><td>{dir_badge(p.get("direction"))}</td>'
            f'<td class="mono">{esc(p.get("tickers") or "—")}</td>'
            f'<td class="mono small">{esc(p.get("sectors") or "—")}</td>'
            f'<td class="mono">{esc(p.get("horizon") or "—")}</td><td>{sbadge}</td>'
            f'<td><span class="src src-{esc(p.get("source","manual"))}">{esc(p.get("source","manual"))}</span></td></tr>'
            f'<tr class="detail"><td></td><td colspan="8"><div class="ev">{esc(p.get("event",""))}</div>'
            f'<div class="pr">→ {esc(p.get("prediction",""))}</div>'
            f'<div class="fl"><b>falsifier:</b> {esc(p.get("falsifier","") or "—")} '
            f'&nbsp;·&nbsp; <b>sensitivity:</b> {esc(p.get("sensitivity","") or "—")}</div></td></tr>')
    table = (f'<div class="panel"><h3>ledger <span class="muted small">{len(s["predictions"])} predictions</span></h3>'
             f'<table class="data preds"><thead><tr><th>id</th><th>conv</th><th>P</th><th>dir</th>'
             f'<th>tickers</th><th>sectors</th><th>horizon</th><th>status</th><th>src</th></tr></thead>'
             f'<tbody>{"".join(rows)}</tbody></table></div>')
    return due_banner + f'<div class="grid2">{calib}{secs}</div>' + table


def render_watchlist(s):
    themes = s["watchlist_themes"]
    auto_set = set(s["auto_tickers"])
    theme_blocks = []
    for key, th in themes.items():
        tickers = th.get("tickers", {}) or {}
        idx = th.get("index", "")
        alts = th.get("index_alts", []) or []
        idx_badge = (f'<span class="idx">{esc(idx)}</span>'
                     + (f'<span class="idx-alt">{esc(" / ".join(alts))}</span>' if alts else "")) if idx else ""
        note = f'<div class="muted small">{esc(th["index_note"])}</div>' if th.get("index_note") else ""
        chips = []
        for sym in tickers:
            is_auto = sym in auto_set
            chips.append(f'<span class="tk {"tk-auto" if is_auto else "tk-watch"}" '
                         f'title="{"auto-tier: burns tokens" if is_auto else "watch-only"}">{esc(sym)}</span>')
        n_auto = sum(1 for sym in tickers if sym in auto_set)
        theme_blocks.append(
            f'<div class="theme"><div class="theme-h"><span class="theme-name">{esc(th.get("label", key))}</span>'
            f'{idx_badge}<span class="muted small">{len(tickers)} names · {n_auto} auto</span></div>'
            f'{note}<div class="tks">{"".join(chips)}</div></div>')
    wl = "".join(theme_blocks)
    cfg = s["config"]
    hide = {"auto_tickers", "_tier_doc"}
    cfg_rows = "".join(f'<tr><td>{esc(k)}</td><td class="mono">{esc(v)}</td></tr>'
                       for k, v in cfg.items() if k not in hide)
    live = cfg.get("enabled") and not cfg.get("dry_run", True)
    txt = ("LIVE — spends tokens on auto-tier hits" if live
           else "DRY-RUN — logs intent only, spends nothing" if cfg.get("enabled")
           else "DISABLED")
    tg = ('<span class="pill live">on</span>' if s["telegram_on"]
          else '<span class="pill off">not set</span>')
    tier = (f'<span class="pill live">{len(auto_set)} auto</span>' if cfg.get("tier_enabled")
            else '<span class="pill dry">tiering off — all names trigger</span>')
    banner = (f'<div class="panel {"live-panel" if live else "dry-panel"}">'
              f'<b>Auto-trigger: {txt}</b> &nbsp; tier {tier} &nbsp; '
              f'Telegram alerts {tg} &nbsp;<span class="muted small">'
              f'{s["watchlist_count"]} tickers · {len(themes)} themes</span></div>')
    ar_rows = "".join(
        f'<tr><td class="mono small">{esc(a.get("ts",""))}</td><td class="mono">{esc(a.get("tickers",""))}</td>'
        f'<td><span class="dec dec-{esc(str(a.get("decision","")).split("_")[0])}">{esc(a.get("decision",""))}</span></td>'
        f'<td class="small">'
        + (f'<a href="#" class="jslink" data-batch="{esc(_basename(a.get("batch","")))}">{esc(_basename(a.get("batch","")))}</a>'
           if a.get("batch") else '<span class="muted">—</span>')
        + '</td>'
        f'<td><button class="btn-mini" onclick="runOutlook(this,\'{esc(str(a.get("tickers","")))}\',\'{esc(_basename(a.get("batch","")))}\')">▶ outlook</button></td></tr>'
        for a in s["autoruns"]) or '<tr><td colspan="5" class="muted">no auto-trigger events yet</td></tr>'
    trig_files = "".join(
        f'<li class="mono small"><a href="#" class="jslink" data-batch="{esc(_basename(t))}">{esc(_basename(t))}</a> '
        f'<button class="btn-mini" onclick="runOutlook(this,\'\',\'{esc(_basename(t))}\')">▶ outlook</button></li>'
        for t in s["inbox"]["triggered"]) or '<li class="muted">none</li>'
    cool = "".join(f'<tr><td class="mono">{esc(c["ticker"])}</td><td class="mono small">{esc(c["last_ts"])}</td></tr>'
                   for c in s["cooldowns"]) or '<tr><td colspan="2" class="muted">none active</td></tr>'
    legend = ('<div class="muted small" style="margin-bottom:8px">'
              '<span class="tk tk-auto">AUTO</span> burns tokens on a match &nbsp; '
              '<span class="tk tk-watch">WATCH</span> matched &amp; shown, no spend</div>')
    return (banner
            + '<div class="panel" id="batch-view" style="display:none"></div>'
            + f'<div class="panel"><h3>watchlist by theme <span class="muted small">{s["watchlist_count"]} tickers · {len(themes)} themes</span></h3>{legend}<div class="cap-md">{wl}</div></div>'
            + '<div class="grid2">'
            + f'<div class="panel half"><h3>auto-trigger config</h3><table class="data">{cfg_rows}</table></div>'
            + f'<div class="panel half"><h3>ticker cooldowns</h3><table class="data"><thead><tr><th>ticker</th><th>last run</th></tr></thead><tbody>{cool}</tbody></table></div>'
            + '</div>'
            + f'<div class="panel"><h3>auto-run decision log <span class="muted small">logs/autoruns.jsonl · click a batch to see what triggered &amp; its report</span></h3>'
            + '<div class="cap-md">'
            f'<table class="data"><thead><tr><th>time</th><th>tickers</th><th>decision</th><th>batch</th><th></th></tr></thead><tbody>{ar_rows}</tbody></table></div>'
            + '</div>'
            + f'<div class="panel"><h3>pending triggered batches</h3><div class="cap-md"><ul class="plain">{trig_files}</ul></div></div>')


def render_jobs(s):
    if not s.get("jobs"):
        return ""
    rows = []
    for j in s["jobs"]:
        icon = {"running": "◍", "done": "✓", "error": "✕"}.get(j["status"], "·")
        label = esc(j["kind"]) + (f': {esc(j["focus"])}' if j.get("focus") else "")
        link = (f' → <a href="#" class="joblink" data-path="{esc(j["report"])}">open report</a>'
                if j.get("report") else "")
        msg = (f' <span class="muted small">{esc(j.get("message",""))}</span>'
               if j["status"] != "running" and j.get("message") else "")
        rows.append(f'<div class="job job-{j["status"]}"><span class="job-i">{icon}</span> '
                    f'<b>{label}</b> <span class="muted small mono">{esc(j["started"])}</span>{link}{msg}</div>')
    return f'<div class="panel"><h3>jobs</h3>{"".join(rows)}</div>'


def render_reports(s):
    busy = ' disabled title="an analysis is already running"' if s.get("analyzing") else ""
    actions = (
        '<div class="panel actions"><h3>make a new report</h3>'
        '<div class="act-row">'
        '<button class="btn btn-ghost" onclick="act(this,\'/action/ingest\')">⟳ Pull fresh news</button>'
        f'<button class="btn btn-primary" onclick="act(this,\'/action/analyze\')"{busy}>▶ Analyze inbox → report</button>'
        '</div>'
        '<div class="act-row">'
        '<input id="focus" class="inp" placeholder="Focused analysis, e.g. look at the Iran news and predict what comes next">'
        '<select id="model" class="inp sel"><option value="sonnet">sonnet</option>'
        '<option value="opus">opus</option><option value="haiku">haiku</option></select>'
        f'<button class="btn btn-primary" onclick="actFocus(this)"{busy}>▶ Run focused analysis</button>'
        '</div>'
        '<div class="muted small">Analysis runs headless Claude and <b>uses tokens</b> (one at a time). '
        'Ingestion is free. New reports appear below when done.</div></div>')
    groups, last_day = [], None
    for r in s["reports"]:
        if r.get("day") != last_day:
            groups.append(f'<div class="rep-day">{esc(r.get("day",""))}</div>')
            last_day = r.get("day")
        groups.append(
            f'<div class="rep-item" data-path="{esc(r["path"])}" '
            f'data-title="{esc(r["title"].lower())}" data-tag="{r["tag"]}">'
            f'<span class="rep-tag rt-{r["tag"]}">{r["tag"]}</span>'
            f'<div class="rep-t">{esc(r["title"])}</div>'
            f'<div class="rep-m mono small">{esc(r["path"].split("/")[-1])} · {r["size_kb"]} KB</div></div>')
    listing = "".join(groups) or '<div class="muted">No reports yet — run an analysis above.</div>'
    controls = ('<div class="rep-controls">'
                '<input id="rep-search" class="inp" placeholder="search reports…" oninput="filterReports()">'
                '<div class="chips"><button class="chip active" data-f="all" onclick="repFilter(this)">all</button>'
                '<button class="chip" data-f="manual" onclick="repFilter(this)">manual</button>'
                '<button class="chip" data-f="auto" onclick="repFilter(this)">auto</button></div></div>')
    return (actions + render_jobs(s)
            + f'<div class="rep-layout"><div class="rep-col">{controls}'
            f'<div class="rep-list">{listing}</div></div>'
            f'<div class="rep-view" id="report-view"><div class="muted center">← select a report</div></div></div>')


def render_tape(s):
    ib = s["inbox"]
    feed_rows = "".join(
        f'<tr><td>{"<span class=\"fdot-bad\">●</span>" if f["degraded"] else "<span class=\"fdot-ok\">●</span>"} {esc(f["label"])}</td>'
        f'<td class="mono small muted">{esc(f["url"][:70])}</td></tr>'
        for f in s["feeds"]) or '<tr><td class="muted">feed list unavailable</td></tr>'
    heads = "".join(
        f'<div class="hl"><span class="hl-src">{esc(h["src"])}</span> '
        + (f'<a href="{esc(h["url"])}" target="_blank" rel="noopener" class="hl-a">{esc(h["title"])}</a>'
           if h.get("url") else esc(h["title"]))
        + (f' <span class="hl-match" title="watchlist match">{esc(h["matched"])}</span>' if h.get("matched") else "")
        + '</div>'
        for h in ib["headlines"]) or '<div class="muted">inbox empty</div>'
    return ('<div class="grid2">'
            + stat_card("current inbox", ib["current"], f'{ib["item_count"]} items in {esc(ib["showing"])}')
            + stat_card("processed batches", ib["processed_count"], "analyzed & archived")
            + '</div>'
            + f'<div class="grid2"><div class="panel half"><h3>news feeds <span class="muted small">{len(s["feeds"])}</span></h3>'
            f'<div class="feed-wrap"><table class="data"><tbody>{feed_rows}</tbody></table></div></div>'
            + f'<div class="panel half"><h3>latest headlines <span class="muted small">{esc(ib["showing"])}</span></h3>'
            f'<div class="hl-wrap">{heads}</div></div></div>')


def wl_manager(s):
    autos = set(s.get("auto_tickers", []))
    rows = []
    for sym in sorted(s.get("watchlist_flat", {})):
        meta = s["watchlist_flat"][sym] or {}
        al = ", ".join(meta.get("aliases", [])[:4])
        kw = ", ".join(meta.get("keywords", [])[:4])
        is_auto = sym in autos
        badge = ('<span class="pill live">AUTO</span>' if is_auto else '<span class="pill off">manual</span>')
        toggle = ("manual" if is_auto else "auto")
        rows.append(
            f'<tr><td><span class="wl-sym">{esc(sym)}</span></td>'
            f'<td class="small muted">{esc(al)}{(" · <i>" + esc(kw) + "</i>") if kw else ""}</td>'
            f'<td>{badge}</td>'
            f'<td><button class="btn-mini" onclick="wlEdit(\'{toggle}\',\'{esc(sym)}\')">'
            f'{"→ manual" if is_auto else "→ AUTO"}</button> '
            f'<button class="btn-mini" onclick="wlEdit(\'remove\',\'{esc(sym)}\')">✕</button></td></tr>')
    table = ("".join(rows)) or '<tr><td class="muted" colspan="4">watchlist empty</td></tr>'
    return (
        '<div class="panel"><h3>watchlist manager '
        '<span class="muted small">AUTO = matches burn tokens automatically (guardrailed) · manual = flagged only</span></h3>'
        '<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px">'
        '<input id="wl-sym" class="inp" style="max-width:90px" placeholder="SYM">'
        '<input id="wl-al" class="inp" style="min-width:170px" placeholder="aliases, comma-sep (Nvidia, …)">'
        '<input id="wl-kw" class="inp" style="min-width:170px" placeholder="keywords (Blackwell, …)">'
        '<label class="set-check"><input id="wl-auto" type="checkbox"> auto-run</label>'
        '<button class="btn" onclick="wlAdd(this)">add</button>'
        '<span id="wl-msg" class="muted small"></span></div>'
        f'<div class="wl-wrap"><table class="data"><thead><tr><th>ticker</th><th>aliases · <i>keywords</i></th>'
        f'<th>priority</th><th></th></tr></thead><tbody>{table}</tbody></table></div></div>')


def render_calibration(s):
    st = s["stats"]
    cal = s.get("calibration") or {}
    mb = st.get("mean_brier")
    head = (f'<div class="body" style="margin-bottom:8px">resolved <b>{st.get("resolved",0)}</b> · '
            f'open <b>{st.get("open",0)}</b> · mean Brier <b>{f"{mb:.4f}" if mb is not None else "—"}</b> '
            '<span class="muted small">(0 = clairvoyant, 0.25 = coin-flip at 50%)</span></div>')
    b_rows = "".join(f'<tr><td>{esc(b["label"])}</td><td>{b["n"]}</td>'
                     f'<td>{f"{b['brier']:.3f}" if b.get("brier") is not None else "—"}</td></tr>'
                     for b in cal.get("bands", [])) or '<tr><td class="muted" colspan="3">none yet</td></tr>'
    k_rows = "".join(f'<tr><td>{esc(k["label"])}</td><td>{k["n"]}</td>'
                     f'<td>{k["predicted"]:.0%}</td><td>{f"{k['actual']:.0%}" if k.get("actual") is not None else "—"}</td></tr>'
                     for k in cal.get("buckets", [])) or '<tr><td class="muted" colspan="4">none yet</td></tr>'
    s_rows = "".join(f'<tr><td>{esc(x["sectors"])}</td><td>{x["n"]}</td>'
                     f'<td>{f"{x['brier']:.3f}" if x.get("brier") is not None else "—"}</td></tr>'
                     for x in cal.get("sectors", [])[:10]) or '<tr><td class="muted" colspan="3">none yet</td></tr>'
    return ('<details class="panel" style="margin-top:12px"><summary style="cursor:pointer;font-size:13px;'
            'font-weight:600;color:#dbe2ec;text-transform:uppercase;letter-spacing:.5px">calibration report</summary>'
            f'<div style="margin-top:10px">{head}<div class="grid2">'
            '<div><div class="sect" style="font-size:10px;text-transform:uppercase;color:#6b7688;margin-bottom:4px">probability calibration (does P predict outcomes?)</div>'
            f'<table class="data"><thead><tr><th>bucket</th><th>n</th><th>predicted</th><th>actual</th></tr></thead><tbody>{k_rows}</tbody></table>'
            '<div class="sect" style="font-size:10px;text-transform:uppercase;color:#6b7688;margin:10px 0 4px">conviction bands (does conviction predict accuracy?)</div>'
            f'<table class="data"><thead><tr><th>band</th><th>n</th><th>brier</th></tr></thead><tbody>{b_rows}</tbody></table></div>'
            '<div><div class="sect" style="font-size:10px;text-transform:uppercase;color:#6b7688;margin-bottom:4px">by sector</div>'
            f'<table class="data"><thead><tr><th>sectors</th><th>n</th><th>brier</th></tr></thead><tbody>{s_rows}</tbody></table></div>'
            '</div></div></details>')


def render_pnl(s):
    tr = s.get("trades", [])
    closed = [t for t in tr if t.get("status") == "closed"]
    openp = [t for t in tr if t.get("status") == "open"]
    realized = sum(t.get("pct") or 0 for t in closed)
    wins = sum(1 for t in closed if (t.get("pct") or 0) > 0)
    rows = "".join(
        f'<tr><td class="mono">{esc(t["ticker"])}</td>'
        f'<td>{esc(t["direction"])}</td>'
        f'<td class="mono">{t["entry_price"]:g} &rarr; {t["exit_price"]:g}</td>'
        f'<td class="mono" style="color:{"#7fbf95" if (t.get("pct") or 0)>0 else "#c8837c"};font-weight:700">'
        f'{(t.get("pct") or 0):+.2f}%</td>'
        f'<td class="small muted">{esc(t.get("exit_reason") or "")}</td>'
        f'<td class="small muted mono">{esc(str(t.get("entry_ts") or "")[:10])}&rarr;{esc(str(t.get("exit_ts") or "")[:10])}</td>'
        f'<td class="small"><span class="led-link" data-lid="{t["pred_id"]}">#{t["pred_id"]}</span></td></tr>'
        for t in closed) or '<tr><td class="muted" colspan="7">no closed round-trips yet</td></tr>'
    orows = "".join(
        f'<tr><td class="mono">{esc(t["ticker"])}</td><td>{esc(t["direction"])}</td>'
        f'<td class="mono">entry {t["entry_price"]:g}</td>'
        f'<td class="mono small muted">target {t.get("target") or "-"} · inval {t.get("invalidation") or "-"}</td>'
        f'<td class="small"><span class="led-link" data-lid="{t["pred_id"]}">#{t["pred_id"]}</span></td></tr>'
        for t in openp) or '<tr><td class="muted" colspan="5">no open positions</td></tr>'
    return (
        '<div class="panel"><h3>realized p&amp;l '
        '<span class="muted small">CLOSED round-trips only — a buy that was actually sold. '
        'Paper gains are not profit.</span></h3>'
        '<div class="grid">'
        + stat_card("realized return", f"{realized:+.2f}%",
                    f"{len(closed)} closed round-trip{'s' if len(closed)!=1 else ''}")
        + stat_card("win rate", f"{wins}/{len(closed)}" if closed else "—",
                    "closed trades only")
        + stat_card("open positions", str(len(openp)), "unrealized — excluded")
        + '</div>'
        f'<table class="data"><thead><tr><th>ticker</th><th>side</th><th>entry &rarr; exit</th>'
        f'<th>realized</th><th>exit</th><th>held</th><th>call</th></tr></thead><tbody>{rows}</tbody></table>'
        '<div class="sect" style="margin:14px 0 6px;font-size:10px;text-transform:uppercase;'
        'letter-spacing:.7px;color:var(--ink-faint);font-weight:700">open — unrealized, NOT counted as profit</div>'
        f'<table class="data"><thead><tr><th>ticker</th><th>side</th><th>entry</th>'
        f'<th>exit plan</th><th>call</th></tr></thead><tbody>{orows}</tbody></table>'
        '<div class="muted small" style="margin-top:12px;line-height:1.6">'
        'Exits are booked at the <b>pre-registered target or invalidation</b> — never at the '
        'hindsight high. Forecast accuracy (Brier) and trading P&amp;L are separate scoreboards: '
        'most ledger calls are directional/structural and never became positions.</div></div>')


def render_monitor(s):
    return (render_overview(s) + render_pnl(s) + wl_manager(s) + render_watchlist(s) + render_tape(s))


def render_timelines(s):
    tl = s.get("timelines") or {}
    n = len(tl.get("nodes", []))
    upd = tl.get("updated", "never")
    if not n:
        return ('<div class="panel"><h3>timeline web</h3><div class="muted">No timelines yet — '
                'data/timelines.json is empty. Run an analysis; the analyst layer maintains the web.</div></div>')
    legend = ('<div class="muted small" style="margin-bottom:6px">'
              '<b>◆ solid = BRANCH</b> (mutually exclusive futures — siblings always sum to 100%, audited below) · '
              '<b>◇ dashed = EVENT</b> (a conditional inside a branch — siblings do NOT sum; each shows '
              '<b>if-branch %</b> and its complement <b>else %</b>). '
              '<b>parlay</b> multiplies only along the branch spine; <b>joint</b> = branch AND event together; '
              'binary policy events also show the <b>marginal</b> (integrated across ALL branches — the number '
              'to quote for "will the FOMC hike?"). Gold = most probable chain. Click any node for reasoning.</div>'
              '<div id="tl-audit" class="small" style="color:#7fbf95;margin-bottom:6px">branch-sum audit: …</div>'
              '<div class="edge-key">'
              '<span><i class="ln-act"></i> happened (actual history, in time order)</span>'
              '<span><i class="ln-likely"></i> if&nbsp;→&nbsp;then (favoured)</span>'
              '<span><i class="ln-poss"></i> if&nbsp;→&nbsp;then (alternative)</span>'
              '<span><i class="ln-out"></i> ruled out — fork went the other way</span>'
              '<span><i class="ln-shift"></i> shifts (re-weights another node)</span></div>'
              '<div class="chips" style="margin-top:4px">'
              '<span class="muted small" style="margin-right:4px">jump to arc:</span>'
              + "".join(f'<button class="chip" onclick="tlJump(\'{nid}\')">{lbl}</button>' for nid, lbl in [
                  ("flip-b", "Iran fork"), ("capex-verdict", "AI capex"), ("semis-correction", "Semis"),
                  ("dovish-fed", "Fed 7/29"), ("election-instrument", "Election→2028"),
                  ("taiwan-watch", "Taiwan window"), ("war-economy-2027", "War economy 27"),
                  ("world-2031", "World 2029-31")])
              + '</div>')
    wa = tl.get("week_ahead") or {}
    wa_html = ""
    if wa.get("prints"):
        cards = []
        for p in wa["prints"]:
            st = p.get("status", "pending")
            res = p.get("result", "")
            badge = (f'<span class="wa-badge wa-{res.lower()}">{esc(res)}'
                     + (f' · Brier {p["brier"]}' if p.get("brier") is not None else '') + '</span>'
                     if st == "resolved"
                     else '<span class="wa-badge wa-pending">PENDING</span>')
            led = f'<span class="led-link" data-lid="{p["ledger"]}">#{p["ledger"]}</span>' if p.get("ledger") else ""
            actual = (f'<div class="wa-row"><span class="wa-k">actual</span>'
                      f'<span class="wa-v" style="color:#eef2f7">{esc(p.get("actual",""))}</span></div>'
                      if st == "resolved" else
                      f'<div class="wa-row"><span class="wa-k">actual</span><span class="wa-v muted">— awaiting print —</span></div>')
            cards.append(
                f'<div class="wa-card wa-card-{st}">'
                f'<div class="wa-head"><b>{esc(p.get("event",""))}</b> {badge}'
                f'<span class="wa-when">{esc(p.get("when",""))} {led}</span></div>'
                f'<div class="wa-row"><span class="wa-k">engine</span><span class="wa-v">{esc(p.get("estimate",""))}</span></div>'
                f'<div class="wa-row"><span class="wa-k">consensus</span><span class="wa-v muted">{esc(p.get("consensus",""))}</span></div>'
                f'{actual}'
                f'<div class="wa-note">{esc(p.get("note",""))}</div></div>')
        # NOW shows only what is still PENDING; resolved catalysts drop into a
        # collapsed archive so this board can never go stale again.
        live = [c for c, p in zip(cards, wa["prints"]) if p.get("status") != "resolved"]
        done = [c for c, p in zip(cards, wa["prints"]) if p.get("status") == "resolved"]
        n_hit = sum(1 for p in wa["prints"] if p.get("status") == "resolved" and p.get("result") == "HIT")
        wa_html = (f'<div class="panel" style="margin-bottom:10px"><h3>{esc(wa.get("label","catalyst board"))} '
                   f'<span class="muted small">NOW — {len(live)} upcoming · the engine is holding a call on each</span></h3>'
                   + (f'<div class="wa-grid">{"".join(live)}</div>'
                      if live else '<div class="muted small">no pending catalysts on the board</div>')
                   + (('<details class="arch" style="margin-top:14px"><summary class="arch-sum">'
                       f'past catalysts <b>{len(done)}</b> · <span style="color:var(--ok)">{n_hit} HIT</span>'
                       f'</summary><div class="wa-grid" style="margin-top:10px">{"".join(done)}</div></details>')
                      if done else '')
                   + '</div>')
    return (wa_html + f'<div class="panel" style="margin-bottom:10px"><h3>timeline web '
            f'<span class="muted small">{n} branches · updated {esc(upd)} · maintained by every analysis</span></h3>'
            f'{legend}</div>'
            '<div class="panel" style="margin-bottom:10px"><h3>custom timeline '
            '<span class="muted small">ask a question — the engine builds a map for it from the doctrine</span></h3>'
            '<div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">'
            '<input id="cm-q" class="inp" style="min-width:300px" placeholder="e.g. what happens to European defense stocks if Russia attacks a NATO member?">'
            '<button class="btn" onclick="tlGenMap(this)">generate custom timeline</button>'
            '<span id="cm-status" class="muted small">master map</span></div>'
            '<div id="cm-saved" class="chips small" style="margin-top:8px"></div></div>'
            '<div class="tl-layout">'
            '<div class="tl-canvas-wrap"><div class="tl-zoombar"><button class="btn-mini" onclick="tlZoom(-1)">&minus;</button><span id="tl-zoomlbl" class="small muted">100%</span><button class="btn-mini" onclick="tlZoom(1)">+</button><button class="btn-mini" onclick="tlZoom(0)">reset</button><span class="muted small" style="margin-left:6px">ctrl+scroll zooms</span></div><div id="tl-zoomer"><div id="tl-canvas" class="tl-canvas"></div></div></div>'
            '<div id="tl-detail" class="tl-detail"><div class="muted center">← click a node<br><br>'
            'Time runs left→right; lanes are arcs. ◆ diamonds = scheduled certainties every world passes '
            'through. Click a node, then PIN it to see what its outcome shifts (amber = moved).</div></div></div>'
            +
            '<div class="panel" style="margin-top:12px"><h3>prediction ledger '
            '<span class="muted small" id="led-count"></span></h3>'
            '<div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:8px">'
            '<input id="led-q" class="inp" style="min-width:220px" placeholder="search predictions, tickers, clusters, #id" oninput="ledQ(this)">'
            '<div class="chips">'
            '<button class="chip active" data-st="active" onclick="ledSt(this)">active</button>'
            '<button class="chip" data-st="due" onclick="ledSt(this)">due now</button>'
            '<button class="chip" data-st="all" onclick="ledSt(this)">all</button></div>'
            '<select id="led-sort" class="inp" style="max-width:170px" onchange="ledSortSel(this)">'
            '<option value="id">newest first</option><option value="horizon">horizon (soonest)</option>'
            '<option value="prob">probability</option><option value="conviction">conviction</option>'
            '<option value="brier">brier</option></select></div>'
            '<div id="led-body"></div>'
            '<details id="led-archive-wrap" class="arch"><summary class="arch-sum"><span id="led-arch-count">archive</span></summary><div id="led-archive"></div></details></div>'
            + render_calibration(s))


def _fscore(v):
    """Score chip: -1..+1 -> colored arrow chip."""
    if v is None:
        return '<span class="fs fs-none">—</span>'
    cls = "fs-up" if v > 0.15 else "fs-dn" if v < -0.15 else "fs-flat"
    arrow = "▲" if v > 0.15 else "▼" if v < -0.15 else "◆"
    return f'<span class="fs {cls}">{arrow} {v:+.2f}</span>'


def render_fusion(s):
    f = s.get("fusion") or {}
    secs = f.get("sectors") or {}
    if not secs:
        return '<div class="panel"><h3>fusion map</h3><div class="muted">data/fusion.json missing.</div></div>'
    intro = (f'<div class="panel"><h3>fusion map <span class="muted small">GT-Analyst top-down × TradingAgents '
             f'bottom-up · updated {esc(f.get("updated", "?"))}</span></h3>'
             '<div class="muted small">Top-down = branch-weighted sector score from the timeline web. '
             'Bottom-up = per-ticker TradingAgents debate verdicts (record with '
             '<code>python tools/record_ta.py</code> after each debate). '
             '<b>CONFIRM</b> = engines agree (conviction) · <b>CONFLICT</b> = they fight (investigate first) · '
             'no verdict = bottom-up pending.</div></div>')
    cards = []
    for key, sec in secs.items():
        td = sec.get("topdown", {})
        fused = sec.get("fused")
        tickers = (sec.get("bottomup") or {}).get("tickers") or {}
        badge = ""
        if fused and isinstance(fused, dict):
            b = fused.get("badge", "")
            badge = f'<span class="fbadge fb-{b.lower()}">{esc(b)}</span>'
        fused_chip = _fscore(fused.get("score") if isinstance(fused, dict) else None)
        tk_rows = "".join(
            f'<tr><td class="mono">{esc(t)}</td><td><span class="fverdict fv-{v["verdict"].lower()}">{v["verdict"]}</span></td>'
            f'<td>{_fscore(v.get("score"))}</td><td class="muted small">{esc(v.get("recorded", ""))}</td></tr>'
            f'<tr class="fsum"><td colspan="4" class="muted small">{esc(v.get("summary", ""))}</td></tr>'
            for t, v in tickers.items()) or '<tr><td colspan="4" class="muted small">no debates recorded — run /tradingagents, then record_ta.py</td></tr>'
        branches = "".join(f'<div class="fbr"><span class="mono small">{esc(k)}</span> {esc(v)}</div>'
                           for k, v in (td.get("by_branch") or {}).items())
        cards.append(
            f'<div class="fcard"><div class="fcard-h"><b>{esc(sec.get("label", key))}</b> '
            f'<span class="mono muted small">{esc(sec.get("etf", ""))}</span>{badge}</div>'
            f'<div class="frow"><span class="flbl">top-down</span>{_fscore(td.get("score"))} '
            f'<span class="muted small">{esc(td.get("direction", ""))}</span></div>'
            f'<div class="frow"><span class="flbl">fused</span>{fused_chip} '
            f'<span class="muted small">{esc(sec.get("flag", ""))}</span></div>'
            f'<details><summary class="muted small">reasoning + branch decomposition + debates</summary>'
            f'<div class="fdet"><div class="body small">{esc(td.get("rationale", ""))}</div>{branches}'
            f'<table class="data" style="margin-top:8px"><thead><tr><th>ticker</th><th>verdict</th><th>score</th><th>when</th></tr></thead>'
            f'<tbody>{tk_rows}</tbody></table></div></details></div>')
    return intro + f'<div class="fgrid">{"".join(cards)}</div>'


PAGE = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GT-Analyst</title><style>
*{box-sizing:border-box}
:root{
 /* monotone: a single neutral ramp. Colour is reserved for STATE (hit/miss/due) only. */
 --bg:#0b0b0c; --surface:#131315; --surface-2:#19191c; --line:#26262a; --line-soft:#1c1c1f;
 --ink:#cfcfd3; --ink-hi:#f4f4f6; --ink-dim:#87878e; --ink-faint:#5a5a61;
 --accent:#e6e6e9; --accent-dim:#2e2e34; --ok:#7fbf95; --warn:#bfa367; --bad:#c8837c; --violet:#9c92b8;
 --r:3px; --r-sm:2px;
}
body{margin:0;background:var(--bg);color:var(--ink);
 font:13px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
 -webkit-font-smoothing:antialiased}
.mono{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-variant-numeric:tabular-nums}
.small{font-size:12px}.muted{color:var(--ink-faint)}.center{text-align:center;padding:22px}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
::-webkit-scrollbar{width:10px;height:10px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:#232c3d;border-radius:2px;border:2px solid var(--bg)}
::-webkit-scrollbar-thumb:hover{background:#2e394e}
header{display:flex;align-items:center;gap:14px;padding:8px 16px;background:var(--surface);
 border-bottom:1px solid var(--line);position:sticky;top:0;z-index:10}
.logo{font-weight:700;letter-spacing:.5px;font-size:16px;color:var(--ink-hi)}.logo b{color:var(--accent);font-weight:800}
.hstat{color:var(--ink-faint);font-size:12px}.hstat b{color:var(--ink);font-weight:600}
.dot{width:7px;height:7px;border-radius:50%;background:var(--ok);display:inline-block;margin-right:6px;
 box-shadow:none}
.spacer{flex:1}
label.ref{font-size:12px;color:var(--ink-dim);cursor:pointer;user-select:none}
nav{display:flex;gap:1px;padding:0 12px;background:var(--surface);
 border-bottom:1px solid var(--line);position:sticky;top:39px;z-index:9;flex-wrap:wrap}
nav button{background:none;border:none;color:var(--ink-dim);padding:9px 13px;cursor:pointer;
 font-size:12.5px;font-weight:500;border-bottom:2px solid transparent;transition:color .1s}
nav button:hover{color:var(--ink)}
nav button.active{color:var(--accent);border-bottom-color:var(--accent)}
main{padding:13px 14px 40px;max-width:1320px;margin:0 auto}
section{display:none}section.active{display:block;animation:fade .18s ease}
@keyframes fade{from{opacity:0;transform:translateY(3px)}to{opacity:1;transform:none}}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:7px;margin-bottom:9px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:9px}
@media(max-width:800px){.grid2{grid-template-columns:1fr}}
.card{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:9px 11px;
 transition:border-color .12s}
.card:hover{border-color:#2a3446}
.card.ok{border-color:rgba(74,222,128,.28)}.card.warn{border-color:rgba(227,179,65,.3)}
.card-v{font-size:20px;font-weight:700;color:var(--ink-hi);letter-spacing:-.4px;font-variant-numeric:tabular-nums}
.card-l{font-size:9.5px;text-transform:uppercase;letter-spacing:.7px;color:var(--ink-faint);margin-top:2px;font-weight:600}
.card-s{font-size:10.5px;color:var(--ink-dim);margin-top:3px}
.panel{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:10px 12px;margin-bottom:9px}
.panel.half{margin-bottom:0}
.panel h3{margin:0 0 8px;font-size:10px;font-weight:700;color:var(--ink-dim);text-transform:uppercase;letter-spacing:1px}
table{width:100%;border-collapse:collapse}
table.data th{text-align:left;font-size:9.5px;text-transform:uppercase;letter-spacing:.7px;color:var(--ink-faint);padding:4px 8px;border-bottom:1px solid var(--line);font-weight:600}
table.data td{padding:4px 8px;border-bottom:1px solid var(--line-soft);font-size:12px;vertical-align:top}
table.data tbody tr{transition:background .1s}table.data tbody tr:hover{background:rgba(90,169,255,.04)}
table.data tr:last-child td{border-bottom:none}
.hot{color:var(--accent);font-weight:600}
.spark{width:100%;height:46px}
.pill{padding:1px 6px;border-radius:var(--r-sm);font-size:10px;font-weight:700;letter-spacing:.3px}
.pill.live{background:#1c3a26;color:var(--ok)}.pill.dry{background:#3a3218;color:#bfa367}.pill.off{background:#2a2f3a;color:#8b95a7}
.conv{padding:2px 7px;border-radius:2px;font-weight:700;font-size:12px}
.c-high{background:#12351f;color:#7fbf95}.c-med{background:#123049;color:var(--accent)}.c-low{background:#3a3218;color:#bfa367}.c-noise{background:#3a1f1f;color:#c8837c}.c-none{color:#6b7688}
.dir{font-size:12px;font-weight:600}.d-up{color:var(--ok)}.d-down{color:#c8837c}.d-vol{color:#9c92b8}.d-neu{color:#8b95a7}
.st{padding:1px 7px;border-radius:4px;font-size:11px;font-weight:600}
.st-open{background:#123049;color:var(--accent)}.st-resolved{background:#1c3a26;color:var(--ok)}
.src{padding:1px 6px;border-radius:4px;font-size:10px}
.src-manual{background:#22293a;color:#9aa5b8}.src-auto{background:#123049;color:var(--accent)}.src-jiang-seed{background:#2e2440;color:#9c92b8}
.preds .detail td{padding-top:0;border-bottom:1px solid #1e2633}
.detail .ev{color:#aeb8c8;font-size:12px}.detail .pr{color:#dbe2ec;margin:3px 0}
.detail .fl{color:#7c869a;font-size:11.5px}
.due-panel{border-color:#4a3a18;background:#1a1710}.due-panel div{padding:2px 0;font-size:13px}
.due-dot{color:#bfa367}.warn-panel{border-color:#4a3a18}
.wl-wrap{max-height:340px;overflow:auto;border:1px solid var(--line);border-radius:3px}
.wl-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}
.wl-card{background:#0f1622;border:1px solid #1e2633;border-radius:2px;padding:10px 12px}
.wl-sym{font-weight:700;color:var(--accent);font-size:15px}.wl-a{font-size:12px;color:#aeb8c8;margin-top:3px}
.wl-k{font-size:11px;color:#9c92b8;margin-top:4px}.wl-guard{font-size:10px;color:#bfa367;margin-top:3px}
.theme{margin:0 0 14px}
.theme-h{display:flex;align-items:center;gap:9px;flex-wrap:wrap;margin-bottom:7px}
.theme-name{font-weight:700;color:#dbe2ec;font-size:13px}
.idx{background:#123049;color:var(--accent);font-weight:700;font-size:11px;padding:1px 7px;border-radius:2px;font-family:ui-monospace,Consolas,monospace}
.idx-alt{color:#6b7688;font-size:11px;font-family:ui-monospace,Consolas,monospace}
.tks{display:flex;flex-wrap:wrap;gap:5px}
.tk{font-family:ui-monospace,Consolas,monospace;font-size:11px;padding:2px 7px;border-radius:2px;border:1px solid #1e2633}
.tk-auto{background:#12351f;color:#7fbf95;border-color:#1c3a26;font-weight:700}
.tk-watch{background:#141b28;color:#8b95a7}
.dec{padding:1px 7px;border-radius:4px;font-size:11px;font-weight:600}
.dec-ran{background:#1c3a26;color:var(--ok)}.dec-dry{background:#3a3218;color:#bfa367}.dec-blocked{background:#3a1f1f;color:#c8837c}.dec-disabled,.dec-error{background:#2a2f3a;color:#8b95a7}
.live-panel{border-color:#1c3a26;background:#0f1c14}.dry-panel{border-color:#3a3218;background:#1a1710}
.plain{list-style:none;padding:0;margin:0}.plain li{padding:3px 0}
.rep-layout{display:grid;grid-template-columns:300px 1fr;gap:14px}
@media(max-width:800px){.rep-layout{grid-template-columns:1fr}}

.rep-list{display:flex;flex-direction:column;gap:8px;max-height:75vh;overflow:auto}
.rep-item{background:#121826;border:1px solid #1e2633;border-radius:2px;padding:10px 12px;cursor:pointer}
.rep-item:hover{border-color:#2d3a4d}.rep-item.sel{border-color:var(--accent)}
.rep-tag{font-size:9px;text-transform:uppercase;padding:1px 6px;border-radius:4px;font-weight:700}
.rt-manual{background:#22293a;color:#9aa5b8}.rt-auto{background:#123049;color:var(--accent)}
.rep-t{font-size:13px;color:#dbe2ec;margin:5px 0 2px}
.rep-col{display:flex;flex-direction:column;gap:10px}
.rep-controls{display:flex;flex-direction:column;gap:8px}
.rep-day{font-size:10px;text-transform:uppercase;letter-spacing:.6px;color:#6b7688;margin:8px 0 2px;font-weight:700}
.actions .act-row{display:flex;gap:8px;margin-bottom:9px;flex-wrap:wrap}
.inp{background:var(--bg);border:1px solid var(--line);border-radius:var(--r-sm);color:var(--ink);padding:9px 12px;font-size:13px;flex:1;min-width:120px;transition:border-color .12s}
.inp:focus{outline:none;border-color:var(--accent);box-shadow:none}
.sel{flex:0 0 auto;min-width:90px}
.btn{border:1px solid var(--line);border-radius:var(--r-sm);padding:6px 13px;font-size:12.5px;font-weight:600;cursor:pointer;white-space:nowrap;transition:all .12s}
.btn:disabled{opacity:.45;cursor:not-allowed}
.btn-primary{background:#123049;color:var(--accent);border-color:#1c3a52}.btn-primary:hover:not(:disabled){background:#173d5e}
.btn-ghost{background:#161d29;color:#c8d0dc}.btn-ghost:hover{background:#1e2633}
.chips{display:flex;gap:6px}
.chip{background:var(--surface-2);border:1px solid var(--line);border-radius:20px;color:var(--ink-dim);padding:5px 13px;font-size:11px;cursor:pointer;transition:all .12s;font-weight:500}
.chip:hover{color:var(--ink);border-color:#2c3648}
.set-row{display:flex;flex-direction:column;gap:5px;margin-bottom:12px}
.set-row>label:first-child{font-size:11px;text-transform:uppercase;letter-spacing:.5px;color:#8b95a7}
.set-row .inp{flex:none;width:100%}
.set-check{display:flex;align-items:center;gap:8px;font-size:13px;color:#c8d0dc;text-transform:none;letter-spacing:0}
.set-check input{width:auto}
.ask-wrap{display:flex;flex-direction:column;height:calc(100vh - 150px);min-height:480px}
.ask-log{flex:1;overflow-y:auto;padding:4px 2px 12px;display:flex;flex-direction:column;gap:12px}
.ask-msg{max-width:88%;padding:10px 14px;border-radius:3px;font-size:13.5px;line-height:1.6;white-space:pre-wrap;word-wrap:break-word}
.ask-u{align-self:flex-end;background:#123049;color:#dbe6f2;border:1px solid #1c3a5a}
.ask-a{align-self:flex-start;background:#121826;color:#c8d0dc;border:1px solid #1e2633}
.ask-a b{color:#eef2f7}.ask-a code{background:#0b0e14;padding:1px 5px;border-radius:4px;font-family:ui-monospace,Consolas,monospace;font-size:12px}
.ask-meta{align-self:flex-start;font-size:10.5px;color:#6b7688;margin:-6px 0 2px 4px}
.ask-empty{color:#6b7688;text-align:center;margin:auto;max-width:440px;line-height:1.7}
.ask-bar{display:flex;gap:8px;align-items:flex-end;padding-top:10px;border-top:1px solid #1e2633}
.ask-bar textarea{flex:1;background:#0b0e14;border:1px solid #1e2633;border-radius:3px;color:#c8d0dc;padding:10px 12px;font:13.5px/1.5 inherit;resize:none;max-height:160px}
.ask-bar textarea:focus{outline:none;border-color:var(--accent)}
.ask-typing{align-self:flex-start;color:#8b95a7;font-size:12px;padding:4px 6px}
.ask-err{align-self:center;background:#3a1f1f;color:#c8837c;border:1px solid #5a2b2b;padding:8px 12px;border-radius:2px;font-size:12.5px}
.chip.active{background:#123049;color:var(--accent);border-color:#1c3a52}
.job{padding:6px 0;border-bottom:1px solid #161d29;font-size:13px}
.job:last-child{border-bottom:none}
.job-i{font-family:ui-monospace,Consolas,monospace}
.job-running .job-i{color:#bfa367}.job-done .job-i{color:var(--ok)}.job-error .job-i{color:#c8837c}
.rep-view h2{color:#eef2f7;font-size:20px;border-bottom:1px solid #1e2633;padding-bottom:8px}
.rep-view h3{color:var(--accent);font-size:15px;margin-top:22px}.rep-view h4{color:#9c92b8;font-size:13px}
.rep-view table.md{margin:12px 0;font-size:12.5px}
.rep-view table.md th{background:#0f1622;text-align:left;padding:6px 9px;border:1px solid #1e2633;color:#8b95a7}
.rep-view table.md td{padding:6px 9px;border:1px solid #1e2633}
.rep-view code{background:#0f1622;padding:1px 5px;border-radius:4px;font-size:12px;color:#bfa367}
.rep-view hr{border:none;border-top:1px solid #1e2633;margin:18px 0}
.cap-md{max-height:300px;overflow:auto;border:1px solid var(--line);border-radius:3px;padding:4px 6px}
.feed-wrap{max-height:300px;overflow:auto}
.hl-wrap{max-height:420px;overflow:auto;max-height:60vh;overflow:auto}.hl{padding:5px 0;border-bottom:1px solid #161d29;font-size:13px}
.hl-src{color:#6b7688;font-size:10px;text-transform:uppercase;margin-right:6px}
.hl-a{color:#c8d0dc;text-decoration:none}.hl-a:hover{color:var(--accent);text-decoration:underline}
.hl-match{background:#3a3218;color:#bfa367;font-size:10px;font-weight:700;border-radius:4px;padding:1px 6px;margin-left:5px}
.fdot-ok{color:var(--ok)}.fdot-bad{color:#c8837c}
.tl-layout{display:grid;grid-template-columns:1fr 340px;gap:12px}
@media(max-width:900px){.tl-layout{grid-template-columns:1fr}}
.tl-canvas-wrap{background:#0d1119;border:1px solid #1e2633;border-radius:3px;overflow:auto;max-height:78vh}
.tl-canvas-wrap{cursor:grab}.tl-canvas-wrap.grabbing{cursor:grabbing;user-select:none}
.tl-zoombar{position:sticky;top:6px;left:6px;z-index:6;display:inline-flex;gap:5px;align-items:center;background:#0f141dcc;border:1px solid #1e2633;border-radius:2px;padding:4px 8px;margin:6px}
#tl-zoomer{position:relative;overflow:hidden}
.lane-label{position:absolute;left:6px;font-size:10px;text-transform:uppercase;letter-spacing:.6px;color:#6b7688;background:#0d1119;padding:1px 5px;z-index:3}
.era-label{position:absolute;top:2px;font-size:10px;color:var(--ink-dim);font-weight:700;z-index:3;letter-spacing:.5px}
.edge-key{display:flex;gap:16px;flex-wrap:wrap;font-size:10.5px;color:var(--ink-faint);margin:8px 0 2px}
.edge-key span{display:flex;align-items:center;gap:6px}
.edge-key i{width:22px;height:0;border-top-width:2px;border-top-style:solid;display:inline-block}
.ln-act{border-color:#7fbf95;border-top-width:2.6px}
.ln-likely{border-color:#bfa367}
.ln-poss{border-color:#3a4a68}
.ln-out{border-color:#6b4444;border-top-style:dashed}
.ln-shift{border-color:#8a6d1f;border-top-style:dashed}
.hist-spine{pointer-events:none}
.today-tag{position:absolute;top:0;font-size:9px;font-weight:800;color:#0a0d13;background:#cfcfd3;padding:1px 7px;border-radius:0 0 6px 6px;z-index:5;letter-spacing:.7px}
.tl-node.ln.verified{border-color:#7fbf95;background:rgba(127,191,149,.14);height:30px;line-height:28px;width:176px;font-size:12.5px;font-weight:600;color:#dff7e6;box-shadow:inset 0 0 0 1px rgba(127,191,149,.35);z-index:4}
.tl-node.ln.verified:hover{box-shadow:inset 0 0 0 1px rgba(127,191,149,.6)}
.tl-node.ln.falsified{height:26px;line-height:24px}
.tl-node.falsified{border-color:rgba(240,119,106,.5);background:rgba(240,119,106,.06)}
.vchk{color:#7fbf95;font-weight:900;margin-right:3px}
.vx{color:#c8837c;font-weight:900;margin-right:3px}
.cf-row{padding:6px 0 6px 9px;border-left:2px solid #2a3446;margin:5px 0;font-size:12px;color:var(--ink-dim);cursor:pointer;transition:border-color .12s}
.cf-row:hover{border-left-color:var(--accent);color:var(--ink)}
.cf-t{font-size:9.5px;font-weight:800;text-transform:uppercase;letter-spacing:.5px;padding:1px 6px;border-radius:4px;margin-right:6px}
.cf-hit{background:rgba(74,222,128,.15);color:var(--ok)}
.cf-miss{background:rgba(240,119,106,.15);color:var(--bad)}
.cf-open{background:rgba(139,149,167,.15);color:var(--ink-dim)}
.cf-p{font-weight:700;color:var(--ink);margin-right:5px;font-variant-numeric:tabular-nums}
.cf-w{font-size:11px;color:var(--ink-faint);margin-top:2px;line-height:1.45}
.tl-node.ln{width:156px;height:22px;padding:0 5px;font-size:10.5px;line-height:20px;white-space:nowrap;overflow:hidden;cursor:pointer;display:flex;align-items:center;gap:4px}
.tl-node.ln .tl-lb{flex:1;overflow:hidden;text-overflow:ellipsis}
.tl-node.ln .tl-dt{font-size:9px;color:var(--ink-faint);flex:none;letter-spacing:-.2px}
.tl-node.ln .cpd{color:#9fb4cc;flex:none;font-size:9px}
.tl-node.ln:hover{overflow:visible;z-index:9;width:auto;min-width:156px;max-width:420px}
.tl-node.ln:hover .tl-lb{overflow:visible}
.tl-node.ln:hover{overflow:visible;z-index:9;width:auto;min-width:178px;max-width:420px}
.tl-pb{font-weight:800;font-size:10px;border-radius:4px;padding:0 4px;margin-right:4px}
.pl-sure{background:#1a2433;color:#7dd3fc;font-weight:700;font-size:9px}
.tl-node.dim{opacity:.22}
.tl-node.desc{border-color:var(--accent);box-shadow:0 0 5px var(--accent)33}
.fw-row{padding:3px 0 3px 8px;border-left:2px solid #123049;margin:3px 0;font-size:12px;color:#aeb8c8;cursor:pointer}
.fw-row:hover{color:#eef2f7;border-left-color:var(--accent)}
.fw-d{font-family:ui-monospace,Consolas,monospace;font-size:10px;color:#6b7688;margin-right:4px}
#led-body{max-height:440px;overflow:auto;border:1px solid var(--line);border-radius:3px}
#led-archive{max-height:340px;overflow:auto}
.led-row{display:flex;gap:7px;align-items:center;flex-wrap:wrap;padding:5px 8px;border-bottom:1px solid var(--line-soft);font-size:12.5px;cursor:pointer;border-left:2px solid transparent;transition:background .1s,border-color .1s}
.led-row:hover{background:rgba(90,169,255,.05);border-left-color:var(--accent)}
.led-row.flash{background:rgba(74,222,128,.14);transition:background 1.6s}
.st-hit{background:rgba(74,222,128,.15);color:var(--ok)}
.st-miss{background:rgba(240,119,106,.15);color:var(--bad)}
.st-due{background:rgba(227,179,65,.15);color:var(--warn)}
.arch{margin-top:14px;border-top:1px solid var(--line);padding-top:12px}
.arch-sum{cursor:pointer;font-size:11px;text-transform:uppercase;letter-spacing:.8px;color:var(--ink-faint);font-weight:700;padding:6px 0;list-style:none;user-select:none}
.arch-sum::marker{content:''}
.arch-sum:before{content:'▸ ';color:var(--ink-faint)}
.arch[open] .arch-sum:before{content:'▾ '}
.arch-sum:hover{color:var(--ink-dim)}
.arch[open]{background:rgba(0,0,0,.15);border-radius:var(--r-sm);padding:12px}
.led-id{color:var(--accent);font-weight:700;font-family:ui-monospace,Consolas,monospace}
.led-p{font-weight:700;color:#dbe2ec}
.led-hz{font-family:ui-monospace,Consolas,monospace;font-size:11px;color:#8b95a7}
.led-tk{background:#123049;color:var(--accent);border-radius:4px;padding:0 6px;font-size:10.5px;font-weight:700}
.led-cl{background:#2e2440;color:#9c92b8;border-radius:4px;padding:0 6px;font-size:10.5px}
.led-tx{flex:1;min-width:200px;color:#aeb8c8}
.led-map{color:#bfa367}
.led-det{display:none;width:100%;font-size:12px;color:#9fb4cc;line-height:1.55;padding:6px 4px 2px;border-left:2px solid #123049;margin-left:4px}
.led-row.open .led-det{display:block}
.led-link{color:var(--accent);cursor:pointer;font-weight:700}
.led-link:hover{text-decoration:underline}
path.pedge.esel{stroke:var(--accent) !important;stroke-width:2.6 !important;opacity:1 !important}
path.sedge.esel{stroke:#bfa367 !important;stroke-width:1.8 !important;opacity:1 !important}
path.edim{opacity:.06 !important}
.tl-node.cp{border-color:#3b82c4;background:#0e1a2a}
.tl-node.pinned{border-color:#bfa367;box-shadow:none}
.tl-node.shifted{border-color:#bfa367;background:#221c0c}
.shift-chip{margin-top:3px;font-size:10px;font-weight:800;color:#bfa367;background:#3a3218;border-radius:4px;padding:1px 5px;display:inline-block}
.tl-canvas{position:relative;min-height:420px}
.tl-canvas svg{position:absolute;top:0;left:0;pointer-events:none}
.tl-edge{fill:none;stroke:#243044;stroke-width:1.6}
.tl-edge.best{stroke:#d4a017;stroke-width:2.6}
.tl-edge.lit{stroke:var(--accent);stroke-width:2.2}
.tl-node{position:absolute;width:200px;background:#121826;border:1.5px solid #2a3446;border-radius:2px;
 padding:7px 10px;cursor:pointer;transition:transform .08s;z-index:2}
.tl-node:hover{transform:scale(1.03);border-color:var(--accent)}
.tl-node.sel{border-color:var(--accent);box-shadow:0 0 0 2px #123049}
.tl-node.best{border-color:#d4a017;background:#171407}
.tl-node.ev{border-style:dashed;background:#10151f}
.tl-node.ev.best{border-color:#d4a017}
.tl-kind{color:var(--accent);font-size:10px}.tl-kind.tk-br{color:#d4a017}
.tl-marg{font-weight:800;font-size:10.5px;color:#7dd3fc;background:#0c2233;padding:1px 6px;border-radius:2px}
.wa-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
@media(max-width:760px){.wa-grid{grid-template-columns:1fr}}
.wa-card{background:#0d1119;border:1px solid #1e2633;border-radius:3px;padding:11px 13px}
.wa-card-pending{border-color:#3a3218}.wa-card-resolved{border-color:#1c3a26}
.wa-head{display:flex;align-items:center;gap:8px;font-size:14px;color:#eef2f7;margin-bottom:8px;flex-wrap:wrap}
.wa-when{margin-left:auto;font-size:11px;color:#6b7688;font-family:ui-monospace,Consolas,monospace}
.wa-badge{padding:1px 8px;border-radius:2px;font-size:10px;font-weight:800}
.wa-hit{background:#12351f;color:#7fbf95}.wa-miss{background:#3a1f1f;color:#c8837c}.wa-pending{background:#3a3218;color:#bfa367}
.wa-row{display:flex;gap:8px;padding:2px 0;font-size:12.5px}
.wa-k{color:#6b7688;width:74px;flex:0 0 74px;text-transform:uppercase;font-size:10px;letter-spacing:.5px;padding-top:2px}
.wa-v{color:#c8d0dc;flex:1}
.wa-note{margin-top:7px;padding-top:7px;border-top:1px solid #161d29;font-size:11.5px;color:#8b95a7;line-height:1.45}
.tl-node.root{background:#0f1c2e;border-color:var(--accent);width:150px}
.tl-t{font-size:12px;color:#dbe2ec;font-weight:600;line-height:1.3}
.tl-p{display:flex;gap:8px;margin-top:4px;font-size:10.5px}
.tl-cond{color:#8b95a7}.tl-parlay{font-weight:800}
.pl-hi{color:#7fbf95}.pl-md{color:var(--accent)}.pl-lo{color:#bfa367}.pl-tail{color:#c8837c}
.tl-hz{font-size:9.5px;color:#6b7688;margin-top:2px}
.tl-detail{background:#121826;border:1px solid #1e2633;border-radius:3px;padding:14px 16px;max-height:78vh;overflow:auto}
.tl-detail h4{margin:0 0 4px;color:#eef2f7;font-size:15px}
.tl-detail .sect{margin-top:12px;font-size:10px;text-transform:uppercase;letter-spacing:.6px;color:#6b7688;font-weight:700}
.tl-detail .body{font-size:12.5px;color:#aeb8c8;line-height:1.5;margin-top:3px}
.tl-detail .conf-item{padding:3px 0 3px 10px;border-left:2px solid #123049;margin:4px 0;font-size:12px;color:#9fb4cc}
.tl-detail .ev{font-size:12px;padding:3px 0}
.tl-detail .ev .ts{color:#d4a017;font-family:ui-monospace,Consolas,monospace;font-size:10.5px}
.tl-badge{display:inline-block;padding:1px 8px;border-radius:2px;font-size:11px;font-weight:700;margin-right:6px}
.tl-badge.gold{background:#3a2f10;color:#d4a017}
.fgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:12px}
.fcard{background:#121826;border:1px solid #1e2633;border-radius:3px;padding:13px 15px}
.fcard-h{display:flex;align-items:center;gap:8px;margin-bottom:8px;font-size:14px;color:#eef2f7}
.frow{display:flex;align-items:center;gap:8px;padding:3px 0}
.flbl{font-size:10px;text-transform:uppercase;letter-spacing:.5px;color:#6b7688;width:64px}
.fs{font-weight:800;font-size:13px;padding:1px 8px;border-radius:2px}
.fs-up{background:#12351f;color:#7fbf95}.fs-dn{background:#3a1f1f;color:#c8837c}
.fs-flat{background:#2a2f3a;color:#9aa5b8}.fs-none{color:#5b667a}
.fbadge{margin-left:auto;padding:1px 8px;border-radius:2px;font-size:10px;font-weight:800}
.fb-confirm{background:#12351f;color:#7fbf95}.fb-conflict{background:#3a1f1f;color:#c8837c}.fb-mixed{background:#3a3218;color:#bfa367}
.fverdict{padding:1px 7px;border-radius:4px;font-size:11px;font-weight:700}
.fv-buy{background:#12351f;color:#7fbf95}.fv-sell{background:#3a1f1f;color:#c8837c}.fv-hold{background:#2a2f3a;color:#9aa5b8}
.fdet{margin-top:8px}.fbr{padding:2px 0 2px 10px;border-left:2px solid #123049;margin:3px 0;font-size:12px;color:#9fb4cc}
.fsum td{border-bottom:1px solid #1e2633 !important;padding-top:0 !important}
.fcard details summary{cursor:pointer;margin-top:6px}
a.jslink{color:var(--accent);text-decoration:none;border-bottom:1px dotted #2d4a6b}
a.jslink:hover{border-bottom-style:solid}
.btn-mini{background:#123049;color:var(--accent);border:1px solid #1c3a52;border-radius:2px;
 padding:2px 9px;font-size:11px;font-weight:600;cursor:pointer;white-space:nowrap}
.btn-mini:hover:not(:disabled){background:#173d5e}
.btn-mini:disabled{opacity:.6;cursor:default}
.batch-pre{white-space:pre-wrap;background:#0b0e14;border:1px solid #1e2633;border-radius:2px;
 padding:10px 13px;font-size:12px;max-height:40vh;overflow:auto;color:#aeb8c8}
#batch-view .sect{margin-top:10px;font-size:10px;text-transform:uppercase;letter-spacing:.6px;color:#6b7688;font-weight:700}
</style></head><body>
<header><span class="logo">GT<b>·</b>ANALYST</span>
<span class="hstat"><span class="dot"></span>ingest <b>__LAST__</b></span>
<span class="hstat">feeds <b>__FEEDS__</b></span>
<span class="hstat">open <b>__OPEN__</b></span>
<span class="spacer"></span>
<label class="ref"><input type="checkbox" id="ar" checked> auto-refresh 30s</label>
<span class="hstat mono">__GEN__</span></header>
<nav>__NAV__</nav>
<main>__SECTIONS__</main>
<script>window.__TL__=__TLDATA__;window.__PREDS=__PREDS__;window.__L2N=__L2N__;window.__NSTATE=__NSTATE__;window.__TODAY="__TODAY__";</script>
<script>
var tabs=["monitor","reports","timelines","fusion","ask","settings"];
function wlEdit(action,sym){fetch("/api/watchlist",{method:"POST",headers:{"Content-Type":"application/json"},
 body:JSON.stringify({action:action,ticker:sym})}).then(function(r){return r.json()})
 .then(function(j){if(j.ok)location.reload();else alert(j.error||"failed");});}
function wlAdd(btn){var sym=document.getElementById("wl-sym").value.trim().toUpperCase();
 if(!sym){return;}btn.disabled=true;
 fetch("/api/watchlist",{method:"POST",headers:{"Content-Type":"application/json"},
  body:JSON.stringify({action:"add",ticker:sym,aliases:document.getElementById("wl-al").value,
   keywords:document.getElementById("wl-kw").value})}).then(function(r){return r.json()})
 .then(function(j){if(!j.ok){btn.disabled=false;document.getElementById("wl-msg").textContent="✗ "+(j.error||"failed");return;}
  if(document.getElementById("wl-auto").checked){
   return fetch("/api/watchlist",{method:"POST",headers:{"Content-Type":"application/json"},
    body:JSON.stringify({action:"auto",ticker:sym})}).then(function(){location.reload();});}
  location.reload();})
 .catch(function(){btn.disabled=false;document.getElementById("wl-msg").textContent="✗ failed";});}
function show(t){tabs.forEach(function(x){
 document.getElementById("s-"+x).classList.toggle("active",x===t);
 document.getElementById("n-"+x).classList.toggle("active",x===t);});
 localStorage.setItem("gt-tab",t);
 // Ask/Settings hold live state (a chat, an unsaved key) — a reload would wipe it, so pause there.
 window.__paused=(t==="ask"||t==="settings");}
function openReport(path){window.__paused=true;
 document.querySelectorAll(".rep-item").forEach(function(e){
   e.classList.toggle("sel",e.dataset.path===path)});
 fetch("/report?path="+encodeURIComponent(path))
  .then(function(r){return r.text()}).then(function(h){
   document.getElementById("report-view").innerHTML=h;});}
function bindReports(){
 document.querySelectorAll(".rep-item").forEach(function(el){
  el.onclick=function(){openReport(el.dataset.path)};});
 document.querySelectorAll(".joblink").forEach(function(el){
  el.onclick=function(ev){ev.preventDefault();show("reports");openReport(el.dataset.path)};});}
function filterReports(){
 var q=(document.getElementById("rep-search").value||"").toLowerCase();
 var f=(document.querySelector(".chip.active")||{}).dataset;f=f?f.f:"all";
 document.querySelectorAll(".rep-item").forEach(function(el){
  var ok=(f==="all"||el.dataset.tag===f)&&el.dataset.title.indexOf(q)>=0;
  el.style.display=ok?"":"none";});
 document.querySelectorAll(".rep-day").forEach(function(d){
  var n=d.nextElementSibling,any=false;
  while(n&&n.classList.contains("rep-item")){if(n.style.display!=="none")any=true;n=n.nextElementSibling;}
  d.style.display=any?"":"none";});}
function repFilter(btn){document.querySelectorAll(".chip").forEach(function(c){c.classList.remove("active")});
 btn.classList.add("active");filterReports();}
function act(btn,url){window.__paused=true;if(btn){btn.disabled=true;btn.textContent="… started";}
 fetch(url,{method:"POST"}).then(function(r){return r.json()}).then(function(){
  setTimeout(function(){location.reload()},1500);})
  .catch(function(){if(btn){btn.disabled=false;btn.textContent="failed — retry";}});}
function actFocus(btn){var f=document.getElementById("focus").value.trim();
 var m=document.getElementById("model").value;window.__paused=true;
 if(btn){btn.disabled=true;btn.textContent="… started";}
 fetch("/action/analyze",{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded"},
  body:"focus="+encodeURIComponent(f)+"&model="+encodeURIComponent(m)})
  .then(function(r){return r.json()}).then(function(){setTimeout(function(){location.reload()},1500);})
  .catch(function(){if(btn){btn.disabled=false;btn.textContent="failed — retry";}});}
bindReports();
document.addEventListener("click",function(ev){
 var a=ev.target.closest("a.jslink");if(!a)return;ev.preventDefault();window.__paused=true;
 var bv=document.getElementById("batch-view");if(!bv)return;
 bv.style.display="block";bv.innerHTML='<div class="muted">loading…</div>';
 var url=a.dataset.batch?("/batch?name="+encodeURIComponent(a.dataset.batch))
                        :("/report?path="+encodeURIComponent(a.dataset.rep));
 fetch(url).then(function(r){return r.text()}).then(function(h){
  bv.innerHTML='<div style="text-align:right"><button class="btn-mini" onclick="this.parentNode.parentNode.style.display=\\'none\\'">✕ close</button></div>'+h;
  bv.scrollIntoView({behavior:"smooth",block:"start"});});});
function runOutlook(btn,tickers,batch){
 btn.disabled=true;btn.textContent="queued…";window.__paused=true;
 fetch("/action/outlook",{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded"},
  body:"tickers="+encodeURIComponent(tickers||"")+"&batch="+encodeURIComponent(batch||"")})
  .then(function(r){return r.json()}).then(function(j){
   btn.textContent=j.ok?"✓ running — see Jobs (Reports tab)":"✗ "+(j.error||"failed");
   if(j.ok)setTimeout(function(){window.__paused=false;},4000);})
  .catch(function(){btn.textContent="✗ failed";btn.disabled=false;});}
// ── Settings ─────────────────────────────────────────────────────────
function saveSettings(btn){
 var key=document.getElementById("set-key").value;
 var model=document.getElementById("set-model").value;
 var think=document.getElementById("set-think").checked;
 var msg=document.getElementById("set-msg");
 btn.disabled=true;msg.textContent="saving…";msg.style.color="#8b95a7";
 fetch("/api/settings",{method:"POST",headers:{"Content-Type":"application/json"},
  body:JSON.stringify({api_key:key,model:model,thinking:think})})
  .then(function(r){return r.json()}).then(function(j){
   btn.disabled=false;document.getElementById("set-key").value="";
   if(j.ok){msg.textContent="✓ saved"+(j.configured?" — key set":"");msg.style.color="var(--ok)";}
   else{msg.textContent="✗ "+(j.error||"failed");msg.style.color="#c8837c";}})
  .catch(function(){btn.disabled=false;msg.textContent="✗ failed";msg.style.color="#c8837c";});}

function saveTrigger(btn){var m=document.getElementById("tg-msg");btn.disabled=true;
 fetch("/api/settings/trigger",{method:"POST",headers:{"Content-Type":"application/json"},
  body:JSON.stringify({enabled:document.getElementById("tg-enabled").checked,
   dry_run:document.getElementById("tg-dry").checked,
   per_ticker_cooldown_min:document.getElementById("tg-cool").value,
   max_runs_per_hour:document.getElementById("tg-hr").value,
   max_runs_per_day:document.getElementById("tg-day").value,
   max_turns:document.getElementById("tg-turns").value,
   lock_stale_min:document.getElementById("tg-lock").value,
   model:document.getElementById("tg-model").value})})
 .then(function(r){return r.json()}).then(function(j){btn.disabled=false;
  m.textContent=j.ok?"\u2713 saved":"\u2717 failed";m.style.color=j.ok?"var(--ok)":"#c8837c";})
 .catch(function(){btn.disabled=false;m.textContent="\u2717 failed";});}
function saveEnvKeys(btn){var m=document.getElementById("ek-msg");btn.disabled=true;
 fetch("/api/settings/env",{method:"POST",headers:{"Content-Type":"application/json"},
  body:JSON.stringify({NEWSAPI_KEY:document.getElementById("ek-news").value,
   FINNHUB_KEY:document.getElementById("ek-finn").value,
   TELEGRAM_BOT_TOKEN:document.getElementById("ek-tgb").value,
   TELEGRAM_CHAT_ID:document.getElementById("ek-tgc").value,
   FRED_API_KEY:document.getElementById("ek-fred").value,
   CONGRESS_API_KEY:document.getElementById("ek-cong").value,
   EIA_API_KEY:document.getElementById("ek-eia").value})})
 .then(function(r){return r.json()}).then(function(j){btn.disabled=false;
  ["ek-news","ek-finn","ek-tgb","ek-tgc","ek-fred","ek-cong","ek-eia"].forEach(function(i){document.getElementById(i).value="";});
  m.textContent=j.ok?"\u2713 saved — restart ingest task to apply":"\u2717 failed";
  m.style.color=j.ok?"var(--ok)":"#c8837c";})
 .catch(function(){btn.disabled=false;m.textContent="\u2717 failed";});}
function saveUiPrefs(btn){var m=document.getElementById("ui-msg");
 var r=parseInt(document.getElementById("ui-refresh").value,10);
 var z=parseInt(document.getElementById("ui-zoom").value,10);
 if(r>=5&&r<=3600)localStorage.setItem("gt-refresh-s",String(r));
 if(z>=40&&z<=250)localStorage.setItem("gt-zoom-def",String(z/100));
 m.textContent="\u2713 saved";m.style.color="var(--ok)";
 window.__Z=parseFloat(localStorage.getItem("gt-zoom-def")||"1")||1;tlZoomApply();}
(function(){var r=document.getElementById("ui-refresh"),z=document.getElementById("ui-zoom");
 if(r)r.value=localStorage.getItem("gt-refresh-s")||"30";
 if(z)z.value=Math.round((parseFloat(localStorage.getItem("gt-zoom-def")||"1")||1)*100);})();
// ── Ask the engine ───────────────────────────────────────────────────
var askHist=[];        // [{role,content}] sent to the API
var askBusy=false;
function askGrow(t){t.style.height="auto";t.style.height=Math.min(t.scrollHeight,160)+"px";}
function askKey(e){if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();sendAsk();}}
function askEsc(s){return String(s==null?"":s).replace(/[&<>]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;"}[c];});}
function askFmt(s){return askEsc(s)
  .replace(/\\*\\*([^*]+)\\*\\*/g,"<b>$1</b>")
  .replace(/`([^`]+)`/g,"<code>$1</code>");}
function askAppend(cls,htmlBody){
 var log=document.getElementById("ask-log");
 var empty=log.querySelector(".ask-empty");if(empty)empty.remove();
 var d=document.createElement("div");d.className="ask-msg "+cls;d.innerHTML=htmlBody;
 log.appendChild(d);log.scrollTop=log.scrollHeight;return d;}
function sendAsk(){
 if(askBusy)return;
 var inp=document.getElementById("ask-in");var q=inp.value.trim();if(!q)return;
 askBusy=true;window.__paused=true;
 askAppend("ask-u",askEsc(q));askHist.push({role:"user",content:q});
 inp.value="";inp.style.height="auto";
 var log=document.getElementById("ask-log");
 var typing=document.createElement("div");typing.className="ask-typing";typing.textContent="engine is thinking…";
 log.appendChild(typing);log.scrollTop=log.scrollHeight;
 fetch("/api/ask",{method:"POST",headers:{"Content-Type":"application/json"},
  body:JSON.stringify({messages:askHist})})
  .then(function(r){return r.json()}).then(function(j){
   typing.remove();askBusy=false;
   if(j.ok){
    askAppend("ask-a",askFmt(j.text));askHist.push({role:"assistant",content:j.text});
    if(j.usage){var m=document.createElement("div");m.className="ask-meta";
     m.textContent=(j.model||"")+"  ·  "+(j.usage.in||0)+" in / "+(j.usage.out||0)+" out tok";
     var lg=document.getElementById("ask-log");lg.appendChild(m);lg.scrollTop=lg.scrollHeight;}
   }else{
    var e=document.createElement("div");e.className="ask-err";e.textContent=j.error||"request failed";
    var lg2=document.getElementById("ask-log");lg2.appendChild(e);lg2.scrollTop=lg2.scrollHeight;
    askHist.pop();}})  // drop the unanswered user turn so retry doesn't double it
  .catch(function(){typing.remove();askBusy=false;askHist.pop();
   var e=document.createElement("div");e.className="ask-err";e.textContent="network error";
   document.getElementById("ask-log").appendChild(e);});}

var saved=localStorage.getItem("gt-tab");show(tabs.indexOf(saved)>=0?saved:"monitor");
window.__lastR=Date.now();
setInterval(function(){var ar=document.getElementById("ar");
 var ms=1000*parseInt(localStorage.getItem("gt-refresh-s")||"30",10);
 if(ar&&ar.checked&&!window.__paused&&Date.now()-window.__lastR>=ms){window.__lastR=Date.now();location.reload();}},5000);

// ── Time-lane map (A+B+D hybrid): time = x, lanes = arcs, checkpoints = diamonds ──
var TL=window.__TL__||{nodes:[]};
var CUR=TL;            // dataset currently rendered (master or a custom map)
var PIN=null;          // pinned node id (what-if mode)
function tlEsc(s){return String(s==null?"":s).replace(/[&<>"]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;","\\"":"&quot;"}[c];});}
function fmtD(d){if(!d)return'';var p=String(d).split('-');
 var M=['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
 return p.length>2?(M[+p[1]]+' '+(+p[2])+(p[0]!=='2026'?" '"+p[0].slice(2):'')):d;}
function plClass(p){return p>=0.55?"pl-hi":p>=0.3?"pl-md":p>=0.12?"pl-lo":"pl-tail";}
// space allocated where the NODES are: the active near-term needs room for cards.
var ANCH=[["2026-07-01",110],["2026-08-01",980],["2026-09-01",1420],["2026-11-01",1720],
          ["2027-01-01",1900],["2027-07-01",2130],["2028-01-01",2320],["2029-01-01",2520],
          ["2031-06-01",2760]];
function xOf(ds){var t=Date.parse(ds||"2027-01-01");
 for(var i=1;i<ANCH.length;i++){var a=Date.parse(ANCH[i-1][0]),b=Date.parse(ANCH[i][0]);
  if(t<=b||i===ANCH.length-1){var f=Math.max(0,Math.min(1,(t-a)/(b-a)));
   return ANCH[i-1][1]+f*(ANCH[i][1]-ANCH[i-1][1]);}}return 2760;}
var ERAS=[["JUL 2026","2026-07-16"],["AUG","2026-08-16"],["SEP","2026-09-15"],
          ["OCT-DEC","2026-11-15"],["2027","2027-04-01"],["2028","2028-06-01"],["2029-31","2030-01-01"]];
function shiftInfo(id){ if(!PIN)return null; var pn=CUR.nodes.find(function(n){return n.id===PIN;});
 if(!pn||!pn.shifts)return null; return pn.shifts.find(function(s){return s.target===id;})||null;}
function laneBuild(){
 var cv=document.getElementById("tl-canvas"); if(!cv)return;
 var nodes=CUR.nodes||[]; if(!nodes.length){cv.innerHTML='<div class="muted center">no nodes</div>';return;}
 var lanes=(CUR.lanes||[]).slice(); var seen={};
 nodes.forEach(function(n){var l=n.lane||"main";if(lanes.indexOf(l)<0){lanes.push(l);}});
 var byId={};nodes.forEach(function(n){byId[n.id]=n;});
 var ROWH=30,TOP=38,W=2860;
 // pass 1: x + row assignment per lane (collision if x within 190px)
 var placed={},laneRows={};
 lanes.forEach(function(l){placed[l]=[];laneRows[l]=1;});
 nodes.forEach(function(n){
  n.__x=xOf(n.date);var l=n.lane||"main";var row=0;
  while(placed[l].some(function(q){return q.row===row&&Math.abs(q.x-n.__x)<168;}))row++;
  placed[l].push({x:n.__x,row:row});n.__row=row;
  if(row+1>laneRows[l])laneRows[l]=row+1;});
 // pass 2: cumulative lane y from real row counts
 var laneY={},y=TOP;
 lanes.forEach(function(l){laneY[l]=y;y+=laneRows[l]*ROWH+30;});
 var H=y+16;
 nodes.forEach(function(n){n.__y=laneY[n.lane||"main"]+8+n.__row*ROWH;
  var _s=(window.__NSTATE||{})[n.id];
  n.__w=(_s==="hit")?176:156; n.__h=(_s==="hit")?30:((_s==="miss")?26:22);});
 window.__mapW=W;window.__mapH=H;cv.style.width=W+"px";cv.style.height=H+"px";
 var svg='<svg width="'+W+'" height="'+H+'">'
  +'<defs>'
  +'<marker id="ar-act" markerWidth="9" markerHeight="9" refX="8" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6" fill="none" stroke="#7fbf95" stroke-width="1.6"/></marker>'
  +'<marker id="ar-likely" markerWidth="9" markerHeight="9" refX="8" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6" fill="none" stroke="#bfa367" stroke-width="1.4"/></marker>'
  +'<marker id="ar-poss" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="none" stroke="#3a4a68" stroke-width="1.2"/></marker>'
  +'<marker id="ar-out" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="none" stroke="#6b4444" stroke-width="1.1"/></marker>'
  +'</defs>';
 ERAS.forEach(function(e){var x=xOf(e[1]);
  svg+='<line x1="'+x+'" y1="14" x2="'+x+'" y2="'+(H-8)+'" stroke="#1e2633" stroke-width="1"/>';});
 lanes.forEach(function(l){svg+='<line x1="56" y1="'+(laneY[l]-2)+'" x2="'+(W-16)+'" y2="'+(laneY[l]-2)+'" stroke="#161d29" stroke-width="1"/>';});
 var _tx=xOf(window.__TODAY);
 svg+='<line x1="'+_tx+'" y1="10" x2="'+_tx+'" y2="'+(H-8)+'" stroke="#cfcfd3" stroke-width="1.5" stroke-dasharray="4 4" opacity=".8"/>';
 // ══ EDGES = TEMPORAL IMPLICATION: "IF <source> THEN <target>" ══
 // Every edge runs strictly LEFT->RIGHT in time and carries an arrowhead. A fork's
 // alternatives are NOT drawn as equal flowing lines: once a fork resolves, the
 // branch that happened keeps the solid line and its siblings are dashed "ruled out".
 var ST=(window.__NSTATE||{});
 nodes.forEach(function(n){
  var p=n.parent&&byId[n.parent];if(!p)return;
  var vs=ST[n.id];
  // did this fork already resolve to a DIFFERENT sibling? then this path is a road not taken
  var ruledOut=(vs!=="hit")&&nodes.some(function(x){
    return x.parent===n.parent&&x.id!==n.id&&x.kind===n.kind&&ST[x.id]==="hit";});
  var pw=(p.__w||178), ph=(p.__h||24), nh=(n.__h||24), nw=(n.__w||178);
  // ROUTING: nodes are ~178px wide but a short time gap spans few px, so consecutive
  // events overlap horizontally. When they do, route DOWN-then-OVER (an orthogonal
  // "then" connector) instead of a horizontal bezier that would double back.
  var x1=p.__x+pw-2, y1=p.__y+ph/2, x2=n.__x-10, y2=n.__y+nh/2;
  var stacked=(x2<x1+14);
  if(stacked){ x1=p.__x+pw/2; y1=p.__y+ph; x2=n.__x+nw/2; y2=n.__y-8; }
  var backward=false;
  var mx=(x1+x2)/2;
  var gold=(n.kind!=="event"&&n.p>=0.5);
  var col,w,dash="",mk,op;
  if(vs==="hit"){          col="#7fbf95"; w=2.8; mk="ar-act";    op=1;    }
  else if(vs==="miss"){    col="#c8837c"; w=1.6; dash="5 4"; mk="ar-out"; op=.8; }
  else if(ruledOut){       col="#6b4444"; w=1.1; dash="4 5"; mk="ar-out"; op=.42;}
  else if(gold){           col="#bfa367"; w=1.9; mk="ar-likely"; op=.92;  }
  else {                   col="#3a4a68"; w=1.2; mk="ar-poss";
                           op=(0.3+0.6*(n.p==null?1:n.p)).toFixed(2); }
  if(backward){ dash="2 4"; op=.25; }   // flag, don't pretend it's a forward implication
  var lbl=(vs==="hit")?"HAPPENED":(ruledOut?"ruled out — this fork went the other way":
           (n.p!=null?("IF "+p.label+" THEN "+n.label+" — "+Math.round(n.p*100)+"%"):""));
  svg+='<path class="pedge'+(vs==="hit"?" verified-edge":"")+(ruledOut?" out-edge":"")+'"'
   +' data-from="'+(n.parent||"now")+'" data-to="'+n.id+'"'
   +' d="'+(stacked
       ? ('M'+x1+','+y1+' C'+x1+','+(y1+16)+' '+x2+','+(y2-16)+' '+x2+','+y2)
       : ('M'+x1+','+y1+' C'+mx+','+y1+' '+mx+','+y2+' '+x2+','+y2))+'"'
   +' fill="none" stroke="'+col+'" stroke-width="'+w+'"'
   +(dash?(' stroke-dasharray="'+dash+'"'):'')
   +' marker-end="url(#'+mk+')" opacity="'+op+'">'
   +'<title>'+tlEsc(lbl)+'</title></path>';});
 // ══ THE ACTUAL-HISTORY SPINE: resolved events chained in the order they OCCURRED ══
 var hist=nodes.filter(function(n){return ST[n.id]==="hit";})
   .sort(function(a,b){return String(a.date||"").localeCompare(String(b.date||""));});
 for(var hi=1;hi<hist.length;hi++){
  var A=hist[hi-1],B=hist[hi];
  var ax=A.__x+((A.__w||178)/2), ay=A.__y+((A.__h||24)),
      bx=B.__x+((B.__w||178)/2), by=B.__y;
  svg+='<path class="hist-spine" d="M'+ax+','+ay+' C'+ax+','+(ay+18)+' '+bx+','+(by-18)+' '+bx+','+by+'"'
   +' fill="none" stroke="#7fbf95" stroke-width="1.6" stroke-dasharray="1 5" stroke-linecap="round" opacity=".55">'
   +'<title>then, in time: '+tlEsc(A.label)+'  \u2192  '+tlEsc(B.label)+'</title></path>';}
 nodes.forEach(function(n){
  (n.shifts||[]).forEach(function(s){var t=byId[s.target];if(!t)return;
   var x1=n.__x+88,y1=n.__y+(t.__y>n.__y?24:0),x2=t.__x+88,y2=t.__y+(t.__y>n.__y?0:24),mx=(x1+x2)/2;
   svg+='<path class="sedge" data-from="'+n.id+'" data-to="'+s.target+'" d="M'+x1+','+y1+' C'+x1+','+(y1+y2)/2+' '+x2+','+(y1+y2)/2+' '+x2+','+y2+'" fill="none" stroke="#8a6d1f" stroke-width="1" stroke-dasharray="5 4" opacity="'+((PIN===n.id)?1:0.4)+'"/>';});});
 svg+='</svg>';
 var html=svg;
 ERAS.forEach(function(e){html+='<div class="era-label" style="left:'+(xOf(e[1])-26)+'px">'+e[0]+'</div>';});
 html+='<div class="today-tag" style="left:'+(xOf(window.__TODAY)-20)+'px">TODAY</div>';
 lanes.forEach(function(l){html+='<div class="lane-label" style="top:'+(laneY[l]-10)+'px">'+tlEsc(l)+'</div>';});
 nodes.forEach(function(n){
  var si=shiftInfo(n.id);
  var _vs2=(window.__NSTATE||{})[n.id];
  var cls="tl-node ln"+(n.checkpoint||n.kind==="checkpoint"?" cp":"")+(n.kind==="event"?" ev":"")
    +(PIN===n.id?" pinned":"")+(si?" shifted":"")+(n.p>=0.55&&n.kind!=="event"?" best":"")+(_vs2==="hit"?" verified":_vs2==="miss"?" falsified":"");
  var chip=si?('<span class="shift-chip">'+(si.p_to!=null?("p&rarr;"+Math.round(si.p_to*100)+"%"):"")
    +(si.date_delta?((si.date_delta<0?" &#10554;":" &#10555;")+Math.abs(si.date_delta)+"d"):"")+'</span>'):"";
  n.__w=(_vs2==="hit")?176:156; n.__h=(_vs2==="hit")?30:((_vs2==="miss")?26:22);
  html+='<div class="'+cls+'" id="tln-'+n.id+'" data-nid="'+n.id+'" title="'+tlEsc(n.label)+'" '
   +'style="left:'+n.__x+'px;top:'+n.__y+'px">'
   +((_vs2==="hit")?'<span class="vchk">&#10003;</span>':(_vs2==="miss")?'<span class="vx">&#10007;</span>':'')
   +((n.p>=0.995)?'<span class="tl-pb pl-sure" title="occurs in every world">ALL</span>':
     '<span class="tl-pb '+plClass(n.p)+'" title="'+(n.kind==="branch"?"share of its fork (siblings sum to 100)":"probability given its parent")+'">'+Math.round(n.p*100)+'</span>')
   +(n.checkpoint||n.kind==="checkpoint"?'<span class="cpd">&#9670;</span>':'')
   +'<span class="tl-lb">'+tlEsc(n.label)+'</span>'
   +'<span class="tl-dt mono">'+fmtD(n.date)+'</span>'+chip+'</div>';});
 cv.innerHTML=html;
 cv.onclick=function(ev){if(window.__dragged&&Date.now()-window.__dragged<150)return;
  var el=ev.target.closest(".tl-node");
  if(el){tlDetail(el.dataset.nid);}
  else{document.querySelectorAll(".tl-node.dim,.tl-node.desc").forEach(function(e){e.classList.remove("dim","desc");});
   document.querySelectorAll("#tl-canvas path.esel,#tl-canvas path.edim").forEach(function(pe){pe.classList.remove("esel","edim");});}};
 tlZoomApply();
 var aud=document.getElementById("tl-audit");
 if(aud){var kids={};nodes.forEach(function(n){if(n.kind==="branch"){var p=n.parent||"NOW";(kids[p]=kids[p]||[]).push(n.p);}});
  var out=[];Object.keys(kids).forEach(function(k){var s=kids[k].reduce(function(a,b){return a+b;},0);
   out.push(k+" "+Math.round(s*100)+"%"+(Math.abs(s-1)<=0.03?" \u2713":" \u2717"));});
  aud.textContent="branch-sum audit: "+(out.join(" \u00b7 ")||"n/a")+(PIN?"  \u00b7  PINNED: "+PIN+" (what-if mode)":"");}
}
function tlZoomApply(){var cv=document.getElementById("tl-canvas"),zr=document.getElementById("tl-zoomer");
 if(!cv||!zr)return;var Z=window.__Z,W=window.__mapW||1400,H=window.__mapH||800;
 cv.style.transform="scale("+Z+")";cv.style.transformOrigin="0 0";
 zr.style.width=Math.round(W*Z)+"px";zr.style.height=Math.round(H*Z)+"px";
 var lb=document.getElementById("tl-zoomlbl");if(lb)lb.textContent=Math.round(Z*100)+"%";}
function tlZoom(d){window.__Z=(d===0)?1:Math.max(0.4,Math.min(2.5,window.__Z*(d>0?1.2:1/1.2)));tlZoomApply();}
(function(){var w=document.querySelector(".tl-canvas-wrap");if(!w)return;
 w.addEventListener("wheel",function(ev){if(ev.ctrlKey){ev.preventDefault();tlZoom(ev.deltaY<0?1:-1);}},{passive:false});
 var drag=null;
 w.addEventListener("mousedown",function(ev){if(ev.button!==0)return;
  drag={x:ev.clientX,y:ev.clientY,sl:w.scrollLeft,st:w.scrollTop,moved:false};w.classList.add("grabbing");});
 window.addEventListener("mousemove",function(ev){if(!drag)return;
  var dx=ev.clientX-drag.x,dy=ev.clientY-drag.y;
  if(Math.abs(dx)>5||Math.abs(dy)>5)drag.moved=true;
  w.scrollLeft=drag.sl-dx;w.scrollTop=drag.st-dy;});
 window.addEventListener("mouseup",function(){if(drag&&drag.moved)window.__dragged=Date.now();drag=null;w.classList.remove("grabbing");});})();
window.__Z=parseFloat(localStorage.getItem("gt-zoom-def")||"1")||1;
function tlDetail(id){
 var n=(CUR.nodes||[]).find(function(x){return x.id===id;});if(!n)return;
 document.querySelectorAll(".tl-node").forEach(function(e){e.classList.remove("sel");});
 var el=document.getElementById("tln-"+id);if(el)el.classList.add("sel");
 var d=document.getElementById("tl-detail");if(!d)return;
 var chain=[],par=n,guard=0;
 while(par&&guard++<12){chain.push(par);par=(CUR.nodes||[]).find(function(x){return x.id===par.parent;});}
 var parlay=chain.reduce(function(a,x){return a*(x.p==null?1:x.p);},1);
 var sem;
 if(n.p>=0.995){sem="occurs in EVERY world (scheduled certainty / structural fork) - the probabilities live on its children";}
 else if(n.kind==="branch"){sem="share of its fork: "+Math.round(n.p*100)+"% (mutually exclusive siblings sum to 100)";}
 else{sem="given "+(n.parent||"NOW")+": "+Math.round(n.p*100)+"% yes / "+Math.round((1-n.p)*100)+"% no";}
 var probBlock='<div class="sect">probability decomposition</div>'
  +'<div class="body">'+tlEsc(sem)+'</div>'
  +'<div class="body"><b>unconditional (parlay from NOW): '+(parlay*100).toFixed(1)+'%</b> = '
  +chain.slice().reverse().map(function(x){return Math.round((x.p==null?1:x.p)*100)+'%';}).join(' × ')+'</div>';
 var kids={};(CUR.nodes||[]).forEach(function(x){if(x.parent)(kids[x.parent]=kids[x.parent]||[]).push(x.id);});
 var descRows=[],stack=[[id,1]];
 while(stack.length){var cur=stack.pop();(kids[cur[0]]||[]).forEach(function(cid){
  var c=(CUR.nodes||[]).find(function(x){return x.id===cid;});if(!c)return;
  var rp=cur[1]*(c.p==null?1:c.p);descRows.push({n:c,rp:rp});stack.push([cid,rp]);});}
 descRows.sort(function(a,b){return String(a.n.date||"").localeCompare(String(b.n.date||""));});
 // COUNTERFACTUAL: for a RESOLVED node, show the sibling branches that did NOT happen
 var _st=(window.__NSTATE||{})[id];
 var cfBlock="";
 if(_st){
  var sibs=(CUR.nodes||[]).filter(function(x){return x.parent===n.parent&&x.id!==id&&x.kind===n.kind;});
  var head=(_st==="hit")?'this path HAPPENED &#10003; — the roads not taken'
        :(_st==="miss")?'this path did NOT happen &#10007; — what the engine had as alternatives'
        :'partially resolved — sibling paths';
  cfBlock='<div class="sect">counterfactual: '+head+'</div>';
  if(sibs.length){cfBlock+=sibs.map(function(sx){
    var sst=(window.__NSTATE||{})[sx.id];
    var tag=(sst==="hit")?'<span class="cf-t cf-hit">happened</span>'
          :(sst==="miss")?'<span class="cf-t cf-miss">ruled out</span>'
          :'<span class="cf-t cf-open">unrealized</span>';
    return '<div class="cf-row" data-nid="'+sx.id+'">'+tag
      +'<span class="cf-p">'+Math.round((sx.p==null?0:sx.p)*100)+'%</span> '
      +tlEsc(sx.label)+'<div class="cf-w">'+tlEsc((sx.market||sx.rationale||"").slice(0,150))+'</div></div>';}).join("");
  }else{cfBlock+='<div class="body muted">no sibling alternatives mapped at this fork</div>';}
 }
 var fwBlock;
 if(descRows.length){fwBlock='<div class="sect">the timeline from this node (given it happens)</div>'
  +descRows.map(function(r){return '<div class="fw-row" data-nid="'+r.n.id+'"><span class="fw-d">'+String(r.n.date||"").slice(0,10)+'</span> '
   +tlEsc(r.n.label)+' <span class="tl-parlay '+plClass(r.rp)+'">'+Math.round(r.rp*100)+'%</span></div>';}).join('');}
 else{fwBlock='<div class="sect">the timeline from this node</div><div class="body muted">terminal node - no mapped downstream; its influence flows through the shift edges</div>';}
 var descSet={};descRows.forEach(function(r){descSet[r.n.id]=1;});
 var ancSet={};chain.forEach(function(x){ancSet[x.id]=1;});
 document.querySelectorAll(".tl-node").forEach(function(e){var q=e.dataset.nid;
  e.classList.remove("dim","desc");
  if(q===id)return;
  if(descSet[q])e.classList.add("desc");
  else if(!ancSet[q])e.classList.add("dim");});
 document.querySelectorAll("#tl-canvas path.pedge,#tl-canvas path.sedge").forEach(function(pe){
  var touch=(pe.dataset.from===id||pe.dataset.to===id);
  pe.classList.toggle("esel",touch);pe.classList.toggle("edim",!touch);});
 var pinBtn=(n.shifts&&n.shifts.length)?(\'<button class="btn-mini" onclick="tlPin(\\'\'+id+\'\\')">\'
   +(PIN===id?"unpin (exit what-if)":"PIN this outcome → see what shifts")+\'</button>\'):"";
 var shifts=(n.shifts||[]).map(function(s){return \'<div class="conf-item">→ \'+tlEsc(s.target)+\': \'
   +(s.p_to!=null?("p→"+Math.round(s.p_to*100)+"%"):"")+(s.date_delta?(" · "+(s.date_delta<0?"earlier ":"later ")+Math.abs(s.date_delta)+"d"):"")
   +(s.note?(" — "+tlEsc(s.note)):"")+\'</div>\';}).join("");
 d.innerHTML=\'<h4>\'+tlEsc(n.label)+\'</h4>\'
  +\'<div class="tl-p" style="font-size:13px"><span class="tl-parlay \'+plClass(n.p)+\'">\'+Math.round(n.p*100)+\'%</span>\'
  +\'<span class="tl-cond">\'+tlEsc(n.kind||"")+\' · \'+tlEsc((n.date||"").slice(0,10))+\' · \'+tlEsc(n.horizon||"")+\'</span></div>\'
  +probBlock
  +cfBlock
  +fwBlock
  +(pinBtn?(\'<div style="margin:6px 0">\'+pinBtn+\'</div>\'):"")
  +\'<div class="sect">rationale</div><div class="body">\'+tlEsc(n.rationale||"—")+\'</div>\'
  +(shifts?(\'<div class="sect">shift edges — what this outcome moves</div>\'+shifts):"")
  +\'<div class="sect">confluence</div>\'+((n.confluence||[]).map(function(c){return \'<div class="conf-item">\'+tlEsc(c)+\'</div>\';}).join("")||\'<div class="body muted">—</div>\')
  +\'<div class="sect">evidence</div>\'+(((n.evidence||[]).length)?n.evidence.map(function(e){return \'<div class="ev">• \'+tlEsc(e.fact)+\' <span class="ts">\'+tlEsc(e.reported||"?")+\'</span></div>\';}).join(""):\'<div class="body muted">none</div>\')
  +\'<div class="sect">market expression</div><div class="body">\'+tlEsc(n.market||"—")+\'</div>\'
  +\'<div class="sect">ledger anchors</div><div class="body">\'+(((n.ledger||[]).map(function(i){return '<span class="led-link" data-lid="'+i+'">#'+i+'</span>';}).join(", "))||"—")+\'</div>\';
 d.onclick=function(ev){var r=ev.target.closest(".fw-row")||ev.target.closest(".cf-row");
  if(r)tlDetail(r.dataset.nid);};
}
function tlPin(id){PIN=(PIN===id)?null:id;laneBuild();tlDetail(id);}
function tlJump(id){show("timelines");var el=document.getElementById("tln-"+id);
 if(!el)return;el.scrollIntoView({behavior:"smooth",block:"center",inline:"center"});tlDetail(id);}
// ── custom question maps ────────────────────────────────────────────────
function tlLoadMaster(){CUR=TL;PIN=null;laneBuild();
 document.getElementById("cm-status").textContent="master map";}
function tlGenMap(btn){var q=document.getElementById("cm-q").value.trim();if(!q)return;
 btn.disabled=true;btn.textContent="engine building map… (can take 1-3 min)";
 fetch("/api/custom_map",{method:"POST",headers:{"Content-Type":"application/json"},
  body:JSON.stringify({question:q})}).then(function(r){return r.json()}).then(function(j){
   btn.disabled=false;btn.textContent="generate custom timeline";
   if(!j.ok){document.getElementById("cm-status").textContent="✗ "+(j.error||"failed");return;}
   CUR=j.map;PIN=null;laneBuild();
   document.getElementById("cm-status").innerHTML=\'custom: <b>\'+tlEsc(j.map.title)+\'</b> \'
    +\'<button class="btn-mini" onclick="tlLoadMaster()">← back to master map</button>\';
   tlListMaps();})
  .catch(function(){btn.disabled=false;btn.textContent="✗ failed — retry";});}
function tlLoadMap(f){fetch("/api/custom_map?file="+encodeURIComponent(f))
 .then(function(r){return r.json()}).then(function(m){CUR=m;PIN=null;laneBuild();
  document.getElementById("cm-status").innerHTML=\'custom: <b>\'+tlEsc(m.title||f)+\'</b> \'
   +\'<button class="btn-mini" onclick="tlLoadMaster()">← back to master map</button>\';});}
function tlListMaps(){fetch("/api/custom_maps").then(function(r){return r.json()}).then(function(ms){
 var el=document.getElementById("cm-saved");if(!el)return;
 el.innerHTML=ms.length?("saved: "+ms.map(function(m){return \'<button class="chip" title="\'+tlEsc(m.question)+\'" onclick="tlLoadMap(\\'\'+tlEsc(m.file)+\'\\')">\'+tlEsc(m.title.slice(0,34))+\'</button>\';}).join("")):"";});}
var LSTATE={q:"",st:"active",sort:"id"};
function ledQ(el){LSTATE.q=el.value;ledRender();}
function ledSt(btn){document.querySelectorAll(".chip[data-st]").forEach(function(c){c.classList.remove("active");});
 btn.classList.add("active");LSTATE.st=btn.dataset.st;ledRender();}
function ledSortSel(el){LSTATE.sort=el.value;ledRender();}
function ledRowHTML(p){
  var node=window.__L2N[p.id];
  var st=(p.status==="resolved")?(p.outcome?'<span class="st st-hit">HIT</span>':'<span class="st st-miss">MISS</span>')
    :'<span class="st st-open">open</span>';
  var due=(p.status==="open"&&p.horizon&&p.horizon<=window.__TODAY)?'<span class="st st-due">due</span>':'';
  return '<div class="led-row" data-lid="'+p.id+'" id="led-'+p.id+'">'
   +'<span class="led-id">#'+p.id+'</span>'+st+due
   +'<span class="led-p">'+Math.round((p.prob||0)*100)+'%</span>'
   +'<span class="led-hz mono">'+tlEsc((p.horizon||"").slice(0,10))+'</span>'
   +(p.tickers?'<span class="led-tk">'+tlEsc(p.tickers)+'</span>':"")
   +(p.cluster?'<span class="led-cl">'+tlEsc(p.cluster)+'</span>':"")
   +'<span class="led-tx">'+tlEsc((p.prediction||"").slice(0,120))+'</span>'
   +(node?'<span class="btn-mini led-map" data-node="'+node+'">map</span>':"")
   +'<div class="led-det"><b>event:</b> '+tlEsc(p.event||"-")
   +'<br><b>prediction:</b> '+tlEsc(p.prediction||"-")
   +'<br><b>falsifier:</b> '+tlEsc(p.falsifier||"-")
   +'<br><b>sensitivity:</b> '+tlEsc(p.sensitivity||"-")
   +(p.brier!=null?'<br><b>brier:</b> '+Number(p.brier).toFixed(3):"")
   +'</div></div>';}
function ledRender(){var el=document.getElementById("led-body");if(!el)return;
 var all=(window.__PREDS||[]).slice();
 // ARCHIVE: resolved calls live in a collapsed section, never at the top
 var archive=all.filter(function(p){return p.status==="resolved";});
 var ps;
 if(LSTATE.st==="due")ps=all.filter(function(p){return p.status==="open"&&p.horizon&&p.horizon<=window.__TODAY;});
 else if(LSTATE.st==="all")ps=all.slice();
 else ps=all.filter(function(p){return p.status==="open";});   // "active" default
 var q=LSTATE.q.toLowerCase();
 if(q)ps=ps.filter(function(p){return ((p.event||"")+" "+(p.prediction||"")+" "+(p.tickers||"")+" "+(p.cluster||"")+" #"+p.id).toLowerCase().indexOf(q)>=0;});
 var k=LSTATE.sort;
 ps.sort(function(a,b){
  if(k==="horizon")return String(a.horizon||"9999").localeCompare(String(b.horizon||"9999"));
  if(k==="prob")return (b.prob||0)-(a.prob||0);
  if(k==="conviction")return (b.conviction||0)-(a.conviction||0);
  if(k==="brier")return (b.brier==null?9:a.brier==null?9:b.brier)-(a.brier==null?9:a.brier);
  return b.id-a.id;});
 el.innerHTML=ps.map(ledRowHTML).join("")||'<div class="muted center">no matches</div>';
 // archive section (resolved only, collapsed by default)
 var av=document.getElementById("led-archive");
 if(av){var aq=LSTATE.q.toLowerCase();
  var af=aq?archive.filter(function(p){return ((p.event||"")+" "+(p.prediction||"")+" "+(p.tickers||"")+" "+(p.cluster||"")+" #"+p.id).toLowerCase().indexOf(aq)>=0;}):archive;
  af.sort(function(a,b){return b.id-a.id;});
  av.innerHTML=af.map(ledRowHTML).join("")||'<div class="muted center small">nothing archived yet</div>';
  var hits=archive.filter(function(p){return p.outcome;}).length;
  var ac=document.getElementById("led-arch-count");
  if(ac)ac.innerHTML='archive — resolved calls <b>'+archive.length+'</b> · '
    +'<span style="color:var(--ok)">'+hits+' HIT</span>'
    +(archive.length-hits?' · <span style="color:var(--bad)">'+(archive.length-hits)+' MISS</span>':'');}
 var ct=document.getElementById("led-count");if(ct)ct.textContent=ps.length+" active"+(LSTATE.q?" matching":"")+" · "+archive.length+" archived";}
function ledGoto(id){show("timelines");
 var tgt=(window.__PREDS||[]).find(function(x){return x.id===id;});
 if(tgt&&tgt.status==="resolved"){var aw=document.getElementById("led-archive-wrap");if(aw)aw.open=true;}
 LSTATE.q="";LSTATE.st="all";var q=document.getElementById("led-q");if(q)q.value="";
 document.querySelectorAll(".chip[data-st]").forEach(function(c){c.classList.toggle("active",c.dataset.st==="all");});
 ledRender();
 var r=document.getElementById("led-"+id);if(!r)return;
 r.scrollIntoView({behavior:"smooth",block:"center"});r.classList.add("open","flash");
 setTimeout(function(){r.classList.remove("flash");},2000);}
(function(){var handler=function(ev){
  var mp=ev.target.closest(".led-map");
  if(mp){ev.stopPropagation();tlJump(mp.dataset.node);return;}
  var r=ev.target.closest(".led-row");if(r)r.classList.toggle("open");};
 var lb=document.getElementById("led-body");if(lb)lb.onclick=handler;
 var av=document.getElementById("led-archive");if(av)av.onclick=handler;})();
document.addEventListener("click",function(ev){
 var l=ev.target.closest(".led-link");if(l){ev.preventDefault();ledGoto(parseInt(l.dataset.lid,10));}});
laneBuild();tlListMaps();ledRender();

</script></body></html>"""


def render_settings(s):
    e = engine_public()
    opts = "".join(f'<option value="{m}"{" selected" if m == e["model"] else ""}>{m}</option>'
                   for m in e["models"])
    status = ('<span class="pill live">● key configured</span>' if e["configured"]
              else '<span class="pill off">no key set</span>')
    ph = "leave blank to keep current key" if e["configured"] else "sk-ant-…"
    return (
        '<div class="panel" style="max-width:640px">'
        '<h3>engine — API connection</h3>'
        f'<div style="margin-bottom:14px">{status}</div>'
        '<div class="set-row"><label>Anthropic API key</label>'
        f'<input id="set-key" class="inp" type="password" placeholder="{ph}" autocomplete="off"></div>'
        '<div class="set-row"><label>Model</label>'
        f'<select id="set-model" class="inp">{opts}</select></div>'
        '<div class="set-row"><label>Extended thinking</label>'
        f'<label class="set-check"><input id="set-think" type="checkbox"{" checked" if e["thinking"] else ""}>'
        ' adaptive thinking — deeper reasoning, a little slower</label></div>'
        '<div style="margin-top:6px"><button class="btn" onclick="saveSettings(this)">Save</button> '
        '<span id="set-msg" class="muted small"></span></div>'
        '<div class="muted small" style="margin-top:16px;line-height:1.65">'
        'The key is stored locally in <span class="mono">config.json</span> (gitignored), used only '
        'server-side, and never sent back to the browser. Requires the <span class="mono">anthropic</span> '
        'Python package (<span class="mono">pip install anthropic</span>). The <b>Ask</b> tab queries this '
        'engine with the live doctrine, timeline web, open ledger, and fusion scores as context — so it '
        'answers as GT-Analyst, not a blank model.</div></div>')


def render_settings_extra(s):
    at = s.get("config", {}) or {}
    env = env_keys_status()

    def chk(k):
        return " checked" if at.get(k) else ""

    def val(k, dflt):
        return esc(str(at.get(k, dflt)))

    opts = "".join(f'<option value="{m}"{" selected" if at.get("model","sonnet")==m else ""}>{m}</option>'
                   for m in sorted(VALID_MODELS))
    pills = " ".join(
        f'<span class="pill {"live" if env[k] else "off"}">{k.replace("_"," ").lower()}</span>'
        for k in ENV_KEYS)
    return (
        '<div class="panel" style="max-width:640px"><h3>auto-trigger guardrails '
        '<span class="muted small">config.json — governs token-burning auto runs</span></h3>'
        f'<div class="set-row"><label class="set-check"><input id="tg-enabled" type="checkbox"{chk("enabled")}> enabled</label></div>'
        f'<div class="set-row"><label class="set-check"><input id="tg-dry" type="checkbox"{chk("dry_run")}> dry-run (log the decision, burn nothing)</label></div>'
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">'
        f'<div class="set-row"><label>per-ticker cooldown (min)</label><input id="tg-cool" class="inp" value="{val("per_ticker_cooldown_min",90)}"></div>'
        f'<div class="set-row"><label>max runs / hour</label><input id="tg-hr" class="inp" value="{val("max_runs_per_hour",2)}"></div>'
        f'<div class="set-row"><label>max runs / day</label><input id="tg-day" class="inp" value="{val("max_runs_per_day",8)}"></div>'
        f'<div class="set-row"><label>max turns / run</label><input id="tg-turns" class="inp" value="{val("max_turns",25)}"></div>'
        f'<div class="set-row"><label>stale-lock clear (min)</label><input id="tg-lock" class="inp" value="{val("lock_stale_min",45)}"></div>'
        f'<div class="set-row"><label>auto-run model</label><select id="tg-model" class="inp">{opts}</select></div></div>'
        '<button class="btn" onclick="saveTrigger(this)">Save guardrails</button> <span id="tg-msg" class="muted small"></span></div>'

        '<div class="panel" style="max-width:640px"><h3>data & alert keys '
        '<span class="muted small">.env — blank fields keep current values</span></h3>'
        f'<div style="margin-bottom:10px">{pills}</div>'
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">'
        '<div class="set-row"><label>NewsAPI key</label><input id="ek-news" class="inp" type="password" autocomplete="off"></div>'
        '<div class="set-row"><label>Finnhub key</label><input id="ek-finn" class="inp" type="password" autocomplete="off"></div>'
        '<div class="set-row"><label>Telegram bot token</label><input id="ek-tgb" class="inp" type="password" autocomplete="off"></div>'
        '<div class="set-row"><label>Telegram chat id</label><input id="ek-tgc" class="inp" autocomplete="off"></div>'
        '<div class="set-row"><label>FRED key (fred.stlouisfed.org) — 2y/Brent/gasoline</label><input id="ek-fred" class="inp" type="password" autocomplete="off"></div>'
        '<div class="set-row"><label>Congress.gov key (api.data.gov) — enacted laws</label><input id="ek-cong" class="inp" type="password" autocomplete="off"></div>'
        '<div class="set-row"><label>EIA key (eia.gov) — crude/gasoline stocks</label><input id="ek-eia" class="inp" type="password" autocomplete="off"></div></div>'
        '<button class="btn" onclick="saveEnvKeys(this)">Save keys</button> <span id="ek-msg" class="muted small"></span></div>'

        '<div class="panel" style="max-width:640px"><h3>ui preferences '
        '<span class="muted small">stored in this browser</span></h3>'
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">'
        '<div class="set-row"><label>auto-refresh every (seconds)</label><input id="ui-refresh" class="inp"></div>'
        '<div class="set-row"><label>timeline default zoom (%)</label><input id="ui-zoom" class="inp"></div></div>'
        '<button class="btn" onclick="saveUiPrefs(this)">Save preferences</button> <span id="ui-msg" class="muted small"></span></div>')


def render_ask(s):
    e = engine_public()
    if not e["configured"]:
        banner = ('<div class="ask-empty">No API key yet. Add one in the <b>Settings</b> tab, '
                  'then ask the engine anything — it answers with the live doctrine, timelines, '
                  'ledger, and fusion state loaded as context.</div>')
    else:
        banner = ('<div class="ask-empty">Ask the engine anything about the tape, a ledger call, a '
                  'timeline branch, or a sector. It has the live doctrine + state loaded.<br><br>'
                  '<span class="small">e.g. “why is semis CONFIRM-bearish?” · “what kills the Warsh '
                  'hawkish-hold theorem?” · “summarize the open energy calls”</span></div>')
    return (
        f'<div class="panel"><h3>ask the engine <span class="muted small">model: {esc(e["model"])} · '
        f'thinking {"on" if e["thinking"] else "off"} · not investment advice</span></h3>'
        '<div class="ask-wrap">'
        f'<div id="ask-log" class="ask-log">{banner}</div>'
        '<div class="ask-bar">'
        '<textarea id="ask-in" rows="1" placeholder="Ask GT-Analyst…  (Enter to send, Shift+Enter for newline)" '
        'oninput="askGrow(this)" onkeydown="askKey(event)"></textarea>'
        '<button class="btn" onclick="sendAsk()">Send</button>'
        '</div></div></div>')


def build_page(s):
    st = s["stats"]
    nav = "".join(
        f'<button id="n-{k}" onclick="show(\'{k}\')">{lbl}</button>'
        for k, lbl in [("monitor", "Monitor"), ("reports", "Reports"),
                       ("timelines", "Timeline &amp; Predictions"), ("fusion", "Fusion"),
                       ("ask", "Ask Engine"), ("settings", "Settings")])
    sections = "".join([
        f'<section id="s-monitor">{render_monitor(s)}</section>',
        f'<section id="s-reports">{render_reports(s)}</section>',
        f'<section id="s-timelines">{render_timelines(s)}</section>',
        f'<section id="s-fusion">{render_fusion(s)}</section>',
        f'<section id="s-ask">{render_ask(s)}</section>',
        f'<section id="s-settings">{render_settings(s)}{render_settings_extra(s)}</section>',
    ])
    tl_json = json.dumps(s.get("timelines") or {}).replace("</", "<\\/")
    preds_json = json.dumps([{k: p.get(k) for k in (
        "id", "event", "prediction", "falsifier", "sensitivity", "prob", "conviction",
        "horizon", "status", "outcome", "brier", "tickers", "cluster", "direction", "source")}
        for p in s.get("predictions", [])]).replace("</", "<\\/")
    l2n = {}
    for nd in (s.get("timelines") or {}).get("nodes", []):
        for lid in nd.get("ledger", []):
            l2n.setdefault(lid, nd["id"])
    l2n_json = json.dumps(l2n)
    # per-node verification: nodes whose ledger anchors RESOLVED get hit/miss/mixed
    _res = {p["id"]: p.get("outcome") for p in s.get("predictions", []) if p.get("status") == "resolved"}
    node_state = {}
    for nd in (s.get("timelines") or {}).get("nodes", []):
        outs = [_res[i] for i in nd.get("ledger", []) if i in _res]
        if outs:
            node_state[nd["id"]] = "hit" if all(outs) else ("miss" if not any(outs) else "mixed")
    nstate_json = json.dumps(node_state)
    return (PAGE.replace("__NAV__", nav).replace("__SECTIONS__", sections)
            .replace("__TLDATA__", tl_json)
            .replace("__PREDS__", preds_json).replace("__L2N__", l2n_json).replace("__NSTATE__", nstate_json)
            .replace("__TODAY__", date.today().isoformat())
            .replace("__LAST__", esc(st["last_ingest"]))
            .replace("__FEEDS__", f'{st["feeds_ok"]}/{st["feeds_total"]}')
            .replace("__OPEN__", str(st["open"]))
            .replace("__GEN__", esc(s["generated"])))


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, body, ctype="text/html; charset=utf-8", code=200):
        b = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")  # never serve a stale dashboard
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        u = urlparse(self.path)
        try:
            if u.path == "/":
                self._send(build_page(gather_state()))
            elif u.path == "/favicon.ico":
                self._send(b"", "image/x-icon", 204)
            elif u.path == "/api/state":
                self._send(json.dumps(gather_state(), default=str), "application/json")
            elif u.path == "/api/engine":
                self._send(json.dumps(engine_public()), "application/json")
            elif u.path == "/api/custom_maps":
                self._send(json.dumps(list_custom_maps()), "application/json")
            elif u.path == "/api/custom_map":
                q = parse_qs(u.query)
                f = _basename(q.get("file", [""])[0])
                fp = CUSTOM_DIR / f
                if not f.endswith(".json") or not fp.exists():
                    self._send(json.dumps({"ok": False, "error": "not found"}), "application/json", 404)
                else:
                    self._send(fp.read_text(encoding="utf-8"), "application/json")
            elif u.path == "/report":
                q = parse_qs(u.query)
                self._send(render_report(q.get("path", [""])[0]))
            elif u.path == "/batch":
                q = parse_qs(u.query)
                self._send(render_batch(q.get("name", [""])[0]))
            else:
                self._send("<h1>404</h1>", code=404)
        except Exception as e:
            self._send(f"<pre>error: {esc(e)}</pre>", code=500)

    def do_POST(self):
        u = urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(length) if length else b""
        try:
            # JSON endpoints (Settings + Ask) ─────────────────────────────
            if u.path == "/api/settings":
                d = json.loads(raw.decode("utf-8") or "{}")
                res = save_engine_cfg(d.get("model", ""), (d.get("api_key") or "").strip(),
                                      bool(d.get("thinking", True)))
                self._send(json.dumps({"ok": True, **res}), "application/json")
                return
            if u.path == "/api/settings/trigger":
                self._send(json.dumps(trigger_settings_save(json.loads(raw.decode("utf-8") or "{}"))),
                           "application/json")
                return
            if u.path == "/api/settings/env":
                self._send(json.dumps(env_keys_save(json.loads(raw.decode("utf-8") or "{}"))),
                           "application/json")
                return
            if u.path == "/api/watchlist":
                dd = json.loads(raw.decode("utf-8") or "{}")
                self._send(json.dumps(watchlist_edit(dd.get("action"), dd.get("ticker"),
                                                     dd.get("aliases"), dd.get("keywords"))),
                           "application/json")
                return
            if u.path == "/api/custom_map":
                dd = json.loads(raw.decode("utf-8") or "{}")
                q = (dd.get("question") or "").strip()[:1000]
                if not q:
                    self._send(json.dumps({"ok": False, "error": "empty question"}), "application/json", 400)
                    return
                self._send(json.dumps(custom_map(q)), "application/json")
                return
            if u.path == "/api/ask":
                d = json.loads(raw.decode("utf-8") or "{}")
                msgs = [{"role": m.get("role"), "content": str(m.get("content", ""))[:8000]}
                        for m in (d.get("messages") or [])
                        if m.get("role") in ("user", "assistant")][-20:]
                if not msgs:
                    self._send(json.dumps({"ok": False, "error": "empty message"}), "application/json", 400)
                    return
                self._send(json.dumps(ask_engine(msgs)), "application/json")
                return
            # form-urlencoded action endpoints ────────────────────────────
            params = parse_qs(raw.decode("utf-8")) if raw else {}
            if u.path == "/action/ingest":
                job = add_job("ingest")
                threading.Thread(target=run_ingest_job, args=(job,), daemon=True).start()
                self._send(json.dumps({"ok": True, "job": job}), "application/json")
            elif u.path == "/action/analyze":
                focus = params.get("focus", [""])[0].strip()
                model = params.get("model", ["sonnet"])[0]
                model = model if model in VALID_MODELS else "sonnet"
                job = add_job("analyze", focus=focus, model=model)
                threading.Thread(target=run_analyze_job, args=(job, focus, model), daemon=True).start()
                self._send(json.dumps({"ok": True, "job": job}), "application/json")
            elif u.path == "/action/outlook":
                tickers = params.get("tickers", [""])[0].strip().upper()
                batch = _basename(params.get("batch", [""])[0])
                model = params.get("model", ["sonnet"])[0]
                model = model if model in VALID_MODELS else "sonnet"
                if not tickers and not batch:
                    self._send(json.dumps({"ok": False, "error": "need tickers or batch"}),
                               "application/json", 400)
                    return
                job = add_job("outlook", focus=tickers or batch, model=model)
                threading.Thread(target=run_outlook_job, args=(job, tickers, batch, model),
                                 daemon=True).start()
                self._send(json.dumps({"ok": True, "job": job}), "application/json")
            else:
                self._send(json.dumps({"ok": False, "error": "unknown action"}),
                           "application/json", 404)
        except Exception as e:
            self._send(json.dumps({"ok": False, "error": str(e)}), "application/json", 500)


class V6Server(ThreadingHTTPServer):
    address_family = socket.AF_INET6


def _lan_ip():
    """Best-effort primary LAN IPv4 (the address other wifi devices reach)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))   # no packets sent; just picks the egress iface
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def main():
    load_env()
    load_jobs()
    port = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 8787
    # SECURE BY DEFAULT: loopback only. LAN exposure is opt-in via env GT_LAN=1 or a
    # `lan` arg — it makes the token-burning action endpoints reachable by any device
    # on the wifi, so only enable on a trusted network.
    lan = os.getenv("GT_LAN") == "1" or "lan" in sys.argv[1:]
    servers = []
    if lan:
        try:
            servers.append(ThreadingHTTPServer(("0.0.0.0", port), Handler))  # all IPv4 ifaces
        except OSError as e:
            print(f"note: could not bind 0.0.0.0:{port} ({e})")
    else:
        # Bind BOTH loopback stacks so http://127.0.0.1 AND http://localhost (->::1) work.
        for fam, host, cls in [(socket.AF_INET, "127.0.0.1", ThreadingHTTPServer),
                               (socket.AF_INET6, "::1", V6Server)]:
            try:
                servers.append(cls((host, port), Handler))
            except OSError as e:
                print(f"note: could not bind {host}:{port} ({e})")
    if not servers:
        sys.exit(f"could not bind port {port}")
    if lan:
        print(f"GT-Analyst dashboard (LAN) -> http://{_lan_ip()}:{port}  "
              f"reachable from any device on this wifi · also http://127.0.0.1:{port}  Ctrl+C to stop")
    else:
        print(f"GT-Analyst dashboard -> http://127.0.0.1:{port}  (also http://localhost:{port})  Ctrl+C to stop")
    threads = [threading.Thread(target=s.serve_forever, daemon=True) for s in servers]
    for t in threads:
        t.start()
    try:
        while True:
            threads[0].join(1)
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
