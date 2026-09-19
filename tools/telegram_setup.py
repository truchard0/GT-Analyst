#!/usr/bin/env python3
"""Find your Telegram chat_id after creating a bot.

Steps:
  1. In Telegram, message @BotFather -> /newbot -> get the bot token.
  2. Put TELEGRAM_BOT_TOKEN=<token> in .env  (in the GT-Analyst root).
  3. Open your new bot in Telegram and send it any message (e.g. "hi").
  4. Run:  python tools/telegram_setup.py
     It prints your chat_id -> add TELEGRAM_CHAT_ID=<id> to .env.
  5. Test:  python pipeline/notify.py "hello from GT-Analyst"
"""
import json
import os
import pathlib
import sys
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "pipeline"))
from common import load_env

load_env()
token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
if not token:
    sys.exit("Set TELEGRAM_BOT_TOKEN in .env first (get it from @BotFather).")

url = f"https://api.telegram.org/bot{token}/getUpdates"
try:
    data = json.loads(urllib.request.urlopen(url, timeout=15).read())
except Exception as e:
    sys.exit(f"getUpdates failed: {e}")

if not data.get("ok"):
    sys.exit(f"Telegram error: {data}")

chats = {}
for upd in data.get("result", []):
    msg = upd.get("message") or upd.get("channel_post") or {}
    ch = msg.get("chat", {})
    if ch.get("id"):
        who = ch.get("username") or ch.get("title") or ch.get("first_name") or ""
        chats[ch["id"]] = who

if not chats:
    print("No messages found. Open your bot in Telegram, send it 'hi', then re-run.")
else:
    print("Found chat(s):")
    for cid, who in chats.items():
        print(f"  TELEGRAM_CHAT_ID={cid}   ({who})")
    print("\nAdd the line above to your .env, then: python pipeline/notify.py \"test\"")
