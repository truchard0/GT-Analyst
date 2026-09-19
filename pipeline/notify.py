#!/usr/bin/env python3
"""Telegram notifier. Stdlib only. No-ops safely if unconfigured.

Set in .env:
  TELEGRAM_BOT_TOKEN=123456:ABC...      (from @BotFather)
  TELEGRAM_CHAT_ID=123456789            (run tools/telegram_setup.py to find it)

Usage:
  from notify import send
  send("auto-analysis ran: NVDA -> reports/auto/...md")
"""
import json
import os
import pathlib
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from common import ROOT, load_env, log

LOGFILE = ROOT / "logs" / "notify.log"


def send(text, silent=False):
    """Send a Telegram message. Returns True on success, False otherwise
    (missing config, network error). Never raises."""
    load_env()
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat:
        log(LOGFILE, "skip (TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set)")
        return False
    try:
        data = urllib.parse.urlencode({
            "chat_id": chat,
            "text": text[:4000],
            "disable_web_page_preview": "true",
            "disable_notification": "true" if silent else "false",
        }).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage", data=data,
            headers={"User-Agent": "gt-analyst/1.0"})
        r = json.loads(urllib.request.urlopen(req, timeout=15).read())
        ok = bool(r.get("ok"))
        log(LOGFILE, f"sent ok={ok} :: {text[:80]}")
        return ok
    except Exception as e:
        log(LOGFILE, f"FAIL {type(e).__name__}: {str(e)[:120]}")
        return False


if __name__ == "__main__":
    msg = " ".join(sys.argv[1:]) or "GT-Analyst test notification"
    print("sent" if send(msg) else "not sent (check .env TELEGRAM_* and logs/notify.log)")
