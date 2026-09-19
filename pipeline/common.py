#!/usr/bin/env python3
"""Shared helpers for the GT-Analyst pipeline. Stdlib only."""
import datetime
import json
import os
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOG_CAP_BYTES = 5 * 1024 * 1024  # truncate logs past 5 MB


def load_env(root=ROOT):
    """Parse .env into os.environ (setdefault — real env wins).
    Scheduled tasks inherit no shell exports, so this is mandatory."""
    p = root / ".env"
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def utc_now():
    return datetime.datetime.now(datetime.UTC)


def utc_iso():
    """Sortable ISO timestamp: 2026-07-03T14:05:00Z"""
    return utc_now().strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_stamp():
    """Filename-safe timestamp: 20260703T1405Z"""
    return utc_now().strftime("%Y%m%dT%H%M%SZ")


def log(logfile, msg):
    """Append one timestamped line; cap file size (pythonw has no console)."""
    p = pathlib.Path(logfile)
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists() and p.stat().st_size > LOG_CAP_BYTES:
        p.write_text("", encoding="utf-8")
    with open(p, "a", encoding="utf-8") as f:
        f.write(f"{utc_iso()} {msg}\n")


def load_json(path, default=None):
    p = pathlib.Path(path)
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))


def resolve_claude():
    """Find the claude CLI. Scheduled-task processes may not see the
    interactive PATH, so .env CLAUDE_BIN takes precedence."""
    override = os.getenv("CLAUDE_BIN")
    if override:
        return override
    for name in ("claude", "claude.cmd", "claude.exe"):
        p = shutil.which(name)
        if p:
            return p
    raise FileNotFoundError(
        "claude CLI not found on PATH; install with "
        "'npm install -g @anthropic-ai/claude-code' or set CLAUDE_BIN in .env")
