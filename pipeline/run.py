#!/usr/bin/env python3
"""One cycle: ingest -> (optionally) headless analysis via `claude -p`.
Inside an interactive Claude Code session just run ingest, then ask Claude
to 'analyze inbox/latest.md'. Headless: python pipeline/run.py --headless"""
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from common import ROOT, load_env, resolve_claude

subprocess.run([sys.executable, str(ROOT / "pipeline" / "ingest.py")], check=True)

if "--headless" in sys.argv:
    load_env()
    prompt = ("Follow CLAUDE.md exactly. Analyze inbox/latest.md: triage per doctrine 12.1, "
              "run the full output schema per event including conviction breakdown, sectors, "
              "tickers, direction; log every prediction with python pipeline/ledger.py add; "
              "then run 'python pipeline/ledger.py due' and resolve anything matured. "
              "Compute a UTC timestamp yourself (YYYYMMDDTHHMMZ) and write the analysis to "
              "reports/<timestamp>.md, then move inbox/latest.md to inbox/processed/<timestamp>.md")
    subprocess.run([resolve_claude(), "-p", prompt,
                    "--allowedTools",
                    "Read,Glob,Grep,Write,Bash(python pipeline/ledger.py *)"],
                   cwd=ROOT)
