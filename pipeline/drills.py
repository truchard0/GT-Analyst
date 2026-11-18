#!/usr/bin/env python3
"""Practice questions ("drills"): many small forecasts about WORLD EVENTS that settle fast and are checked
automatically.

WHY. 56 scored calls in four months, 38 of them scored in one batch, is too little feedback to learn from. This is
a prediction bot for world events, not a stock bot, so the practice is on world events too: several times a day
it writes yes/no questions about what happens next in the news, answers them, and settles them from later news.
They are practice. They never enter the ledger and are never published as calls.

ROUNDS
  news      every GT_DRILL_NEWS_EVERY_MIN minutes (default 60; any multiple of 5 from 5 to 720), around the clock,
            whenever at least 3 new reports have arrived since the last round:
              1 settle   a judge reads the reports published inside each due question's window and answers yes,
                         no or unclear (unclear voids the question). A yes must cite the report that settles it.
              2 write    a writer reads the last 6 hours of reports and writes GT_DRILL_NEWS_QUESTIONS (default 6)
                         questions about what happens next: a strike, a statement or decision by a named official,
                         a vote, a ruling, a sanction, a published figure. Deadlines from 30 minutes to 7 days,
                         at least half within 8 hours. Never a market price.
              3 answer   the analyst gives a probability for each.
            A question means: "will a report saying X be published by the deadline?". So an event that happens
            but is not reported in this bot's feed by then counts as NO. That is the honest limit of the method.
  weekly    Mondays after 16:20 ET: Hormuz ship transits (IMF PortWatch) over the coming 7 days. Settled by data.
  markets   OFF unless GT_DRILL_PRICES=1. Index and rates moves every GT_DRILL_EVERY_MIN minutes of the US cash
            session and after the close. Replays showed these are coin flips; they only exercise calibration.
            Oil, energy and defense prices are excluded either way (the 2026-11-18 ban).

FORECASTERS (a level is only worth anything if it beats the one before it)
  coin     0.50
  base     how often past questions of the same kind came true (for news questions: same deadline class)
  pattern  market and Hormuz questions only: base, given what the last interval did
  analyst  Claude. It sees the reports published before the round time and ITS OWN record so far: its score
           against the base rate, its calibration table and its last settled questions. That record in the prompt
           is the training: the model's weights do not change, its feedback does.

Claude runs headless with no tools, one call per step, so a news round costs up to three small calls. Without the
`claude` CLI (or with GT_DRILL_ANALYST=0) no news questions are written; GT_DRILL_MODEL picks the model.

COMMANDS
  tick [--now ISO]    settle what is due, then ask the round that is due (the server loop calls this every tick)
  report              score everything in data/drills/scored/ -> data/drills/report.md
  replay [--days N]   market questions only, baselines only, over past sessions, with no look-ahead

The independence unit is the DAY: questions asked on the same day overlap heavily, so the bootstrap resamples whole
days. Stdlib only. Parses on Python 3.11.
"""
import bisect
import csv
import datetime as dt
import json
import os
import pathlib
import random
import re
import shutil
import statistics
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from common import ROOT

ET = ZoneInfo("America/New_York")
UTC = dt.timezone.utc
OUT = ROOT / "data" / "drills"
SCORED = OUT / "scored"
REPORT = OUT / "report.md"
SUMMARY = OUT / "summary.json"
REPLAY_SUMMARY = OUT / "replay_summary.json"
OPEN = ROOT / "logs" / "drills_open.json"          # logs/ is git-ignored: open questions live on the machine
STATE = ROOT / "logs" / "drills_state.json"
INBOX = ROOT / "inbox" / "latest.md"

EVERY = int(os.environ.get("GT_DRILL_EVERY_MIN", "30"))
NEWS_EVERY = int(os.environ.get("GT_DRILL_NEWS_EVERY_MIN", "60"))
NEWS_N = max(1, min(12, int(os.environ.get("GT_DRILL_NEWS_QUESTIONS", "6"))))
PRICES = os.environ.get("GT_DRILL_PRICES", "0") == "1"
DEADLINES = {30: "30m", 60: "60m", 120: "2h", 240: "4h", 480: "8h", 1440: "1d", 4320: "3d", 10080: "7d"}
GRACE = 30 * 60                                    # wait this long after a deadline for the feed to catch up
MAX_OPEN_NEWS = 200
LANES = ("iran-gulf", "fed-macro", "ai-chips", "us-politics", "taiwan-china", "world-order", "other")
MARKET_Q = re.compile(                             # a news question must never be a market-price question
    r"\$\s?\d|\b(brent|wti|crude|oil prices?|tanker rates?|share price|shares|stocks?|equit(y|ies)|s&p|nasdaq|dow jones|"
    r"bitcoin|gold|yields?|futures|the dollar)\b.*\b(close[sd]?|settle[sd]?|trade[sd]?|rise[sn]?|fall(s|en)?|gain(s|ed)?|"
    r"drop(s|ped)?|above|below|higher|lower|rall(y|ies)|sell-?off|hit|reach(es)?|top)\b", re.I)
INSTRUMENTS = [("SPY", "S&P 500 ETF (SPY)"), ("QQQ", "Nasdaq 100 ETF (QQQ)"), ("^VIX", "VIX volatility index"),
               ("^TNX", "10-year Treasury yield (percent)"), ("ZT=F", "2-year Treasury note futures price")]
BANNED = re.compile(r"brent|wti|crude|\boil\b|CL=F|BZ=F|XLE|USO|BNO|OIH|XOP|ITA|XAR|PPA", re.I)
COLS = ["qid", "round", "asked_utc", "resolved_utc", "template", "instrument", "horizon", "ref", "thr",
        "outcome_px", "outcome", "base", "pattern", "analyst", "live", "text", "evidence"]
FORECASTERS = ("coin", "base", "pattern", "analyst")
ITEM = re.compile(r"^- \*\*(.*)\*\* \((.*?) \| reported (\S+)")
ANALYST_SYSTEM = ("You are a careful probabilistic forecaster of world events answering practice questions. "
                  "Use no tools. Reply with one JSON object and nothing else.")
WRITER_SYSTEM = ("You write forecasting practice questions about world events. Use no tools. "
                 "Reply with one JSON object and nothing else.")
JUDGE_SYSTEM = ("You settle forecasting practice questions from news reports. Be strict and literal. Use no tools. "
                "Reply with one JSON object and nothing else.")
_CACHE = {}
STALE = []                                         # instruments left out of this round for want of a fresh price


# ── time and data ────────────────────────────────────────────────────────────────────────────────────────────
def ep(d):
    return int(d.timestamp())


def iso(t):
    return dt.datetime.fromtimestamp(t, UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def et(t):
    return dt.datetime.fromtimestamp(t, ET)


def session(day):
    """(open, close) epochs of the US cash session on an ET date."""
    return (ep(dt.datetime.combine(day, dt.time(9, 30), ET)), ep(dt.datetime.combine(day, dt.time(16, 0), ET)))


def yahoo(sym, rng, iv):
    key = (sym, rng, iv)
    if key not in _CACHE:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/%s?range=%s&interval=%s" % (
            urllib.parse.quote(sym), rng, iv)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                res = json.load(r)["chart"]["result"][0]
            rows = zip(res.get("timestamp") or [], res["indicators"]["quote"][0]["close"])
            _CACHE[key] = [(int(t), float(c)) for t, c in rows if c is not None]
        except Exception as e:
            print(f"fetch failed {sym} {iv}: {e}")
            _CACHE[key] = []
    return _CACHE[key]


class Bars:
    """5-minute bars. at(T) = the last bar that STARTED before T, so a price 'at T' never uses data after T."""

    def __init__(self, rows):
        self.ts = [t for t, _ in rows]
        self.px = [p for _, p in rows]

    def at(self, T):
        i = bisect.bisect_left(self.ts, T) - 1
        return (self.ts[i], self.px[i]) if i >= 0 else None


def bars5(sym):
    return Bars(yahoo(sym, "1mo", "5m"))


def daily_hist(sym, day):
    """Closes of the sessions strictly before `day`, from daily bars. History for base rates only: today's level
    and every outcome come from 5-minute bars, because the daily series can lag the close by hours."""
    out = {}
    for t, c in yahoo(sym, "6mo", "1d"):
        d = et(t).date()
        if d < day:
            out[d] = c
    return [c for _, c in sorted(out.items())]


def sessions_seen():
    """Cash sessions (ET dates) present in SPY's 5-minute bars, oldest first."""
    counts = {}
    for t in bars5("SPY").ts:
        d = et(t).date()
        o, c = session(d)
        if o <= t < c:
            counts[d] = counts.get(d, 0) + 1
    return sorted(d for d, n in counts.items() if n >= 30)


def trading_days(before):
    """Past cash sessions strictly before `before`."""
    return [d for d in sessions_seen() if d < before]


def weekday_after(day, n):
    d = day
    while n:
        d += dt.timedelta(days=1)
        n -= d.weekday() < 5
    return d


def fmt(px):
    return f"{px:.4f}" if px < 20 else f"{px:.3f}" if px < 200 else f"{px:.2f}"


def shrink(k, n, prior, m):
    return (k + m * prior) / (n + m)


# ── question building ────────────────────────────────────────────────────────────────────────────────────────
def interval_samples(b, days, every):
    """(move over [t, t+every], move over the interval before t) for every past round time."""
    out = []
    for d in days:
        o, c = session(d)
        t = o + every * 60
        while t + every * 60 <= c:
            a, z, p = b.at(t), b.at(t + every * 60), b.at(t - every * 60)
            if a and z and a[0] >= t - 600 and z[0] >= t + every * 60 - 600:
                out.append((z[1] / a[1] - 1, (a[1] / p[1] - 1) if p else 0.0))
            t += every * 60
    return out


def close_samples(b, days, offset, every):
    """(move from the same clock time to the close, move over the interval before) on past sessions."""
    out = []
    for d in days:
        o, c = session(d)
        t = o + offset
        a, z, p = b.at(t), b.at(c), b.at(t - every * 60)
        if a and z and a[0] >= t - 600 and z[0] > a[0]:
            out.append((z[1] / a[1] - 1, (a[1] / p[1] - 1) if p else 0.0))
    return out


def stats(samples, prev_now, prev_thr, min_n):
    """Usual move size, and base / pattern probabilities for up? and big?, from past (move, previous move) pairs."""
    if len(samples) < min_n:
        return None
    thr = statistics.median(abs(r) for r, _ in samples)
    if thr <= 0:
        return None
    up = [r > 0 for r, _ in samples]
    big = [abs(r) > thr for r, _ in samples]
    base_up = shrink(sum(up), len(up), 0.5, 10)
    base_big = shrink(sum(big), len(big), 0.5, 10)
    like_up = [u for (_, p), u in zip(samples, up) if (p > 0) == (prev_now > 0)]
    like_big = [g for (_, p), g in zip(samples, big) if (abs(p) > prev_thr) == (abs(prev_now) > prev_thr)]
    return {"thr": thr, "up": (base_up, shrink(sum(like_up), len(like_up), base_up, 20)),
            "big": (base_big, shrink(sum(like_big), len(like_big), base_big, 20))}


def question(rnd, T0, sym, name, tpl, label, ref, thr, base, pattern, text, live, **extra):
    q = {"qid": f"{et(T0).strftime('%Y%m%d-%H%M')}-{re.sub(r'[^A-Za-z0-9]', '', sym)}-{tpl}-{label}",
         "round": rnd, "asked_utc": iso(T0), "template": tpl, "instrument": sym, "name": name, "horizon": label,
         "ref": ref, "thr": thr, "base": round(base, 4), "pattern": round(pattern, 4), "analyst": None,
         "text": text, "live": 1 if live else 0}
    q.update(extra)
    return q


def ask_intraday(T0, every, live):
    """The questions for the round at T0 (an epoch on a round boundary). Uses only bars that started before T0."""
    day = et(T0).date()
    o, c = session(day)
    days = trading_days(day)[-21:]
    hm = et(T0).strftime("%H:%M")
    qs = []
    for sym, name in INSTRUMENTS:
        b = bars5(sym)
        ref, prev = b.at(T0), b.at(T0 - every * 60)
        if not ref or not prev or ref[0] < T0 - 600:          # no fresh bar: market closed or data delayed
            STALE.append(sym)
            continue
        prev_now = ref[1] / prev[1] - 1
        iv = interval_samples(b, days, every)
        if len(iv) < 30:
            continue
        prev_thr = statistics.median(abs(r) for r, _ in iv)
        horizons = []
        if T0 + every * 60 <= c:
            horizons.append((f"{every}m", T0 + every * 60, stats(iv, prev_now, prev_thr, 30)))
        if c - T0 > every * 60:
            horizons.append(("close", c, stats(close_samples(b, days, T0 - o, every), prev_now, prev_thr, 8)))
        for label, H, st in horizons:
            if not st:
                continue
            when = "the close (16:00 ET)" if label == "close" else et(H).strftime("%H:%M") + " ET"
            qs.append(question("intraday", T0, sym, name, "up", label, ref[1], None, st["up"][0], st["up"][1],
                               f"{name}: higher at {when} than {fmt(ref[1])}, its level at {hm} ET?", live,
                               resolves_utc=iso(H), ref_ts=ref[0]))
            qs.append(question("intraday", T0, sym, name, "big", label, ref[1], st["thr"], st["big"][0], st["big"][1],
                               f"{name}: moves more than {st['thr'] * 100:.3f}% either way between {hm} ET "
                               f"({fmt(ref[1])}) and {when}? That is its usual move over this stretch.", live,
                               resolves_utc=iso(H), ref_ts=ref[0]))
    return qs


def ask_daily(day, live):
    """After the close of `day`: up? and big? by the next close, up? over five sessions. The level is the 16:00 ET
    price from 5-minute bars; base rates come from daily closes before `day`."""
    o, T0 = session(day)
    qs = []
    for sym, name in INSTRUMENTS:
        ref = bars5(sym).at(T0)
        cl = daily_hist(sym, day)
        if not ref or ref[0] < o or len(cl) < 70:          # no bar from today's session, or too little history
            continue
        px = ref[1]
        extra = dict(ask_date=day.isoformat(), ref_ts=ref[0])
        r1 = [(cl[i] / cl[i - 1] - 1, cl[i - 1] / cl[i - 2] - 1) for i in range(2, len(cl))]
        st = stats(r1, px / cl[-1] - 1, statistics.median(abs(r) for r, _ in r1), 60)
        if st:
            qs.append(question("daily", T0, sym, name, "up", "1d", px, None, st["up"][0], st["up"][1],
                               f"{name}: higher at the next session's close (16:00 ET) than {fmt(px)}, "
                               "its level at today's close?", live, sessions=1, **extra))
            qs.append(question("daily", T0, sym, name, "big", "1d", px, st["thr"], st["big"][0], st["big"][1],
                               f"{name}: more than {st['thr'] * 100:.2f}% away from {fmt(px)} at the next session's "
                               "close? That is its usual daily move.", live, sessions=1, **extra))
        r5 = [(cl[i + 5] / cl[i] - 1, cl[i] / cl[i - 5] - 1) for i in range(5, len(cl) - 5)]
        st5 = stats(r5, px / cl[-5] - 1, statistics.median(abs(r) for r, _ in r5), 40) if len(r5) >= 40 else None
        if st5:
            qs.append(question("daily", T0, sym, name, "up", "5d", px, None, st5["up"][0], st5["up"][1],
                               f"{name}: higher at the close five sessions from now than {fmt(px)}, "
                               "its level at today's close?", live, sessions=5, **extra))
    return qs


def portwatch():
    """{date: total daily transits} through the Strait of Hormuz, 2026 on (IMF PortWatch)."""
    if "pw" in _CACHE:
        return _CACHE["pw"]
    base = ("https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/"
            "Daily_Chokepoints_Data/FeatureServer/0/query")
    rows, off = {}, 0
    try:
        while True:
            q = urllib.parse.urlencode({"where": "portname='Strait of Hormuz' AND year>=2026", "outFields": "*",
                                        "returnGeometry": "false", "resultOffset": off, "f": "json"})
            with urllib.request.urlopen(base + "?" + q, timeout=60) as r:
                d = json.load(r)
            feats = [f["attributes"] for f in d.get("features", [])]
            for a in feats:                                # the date arrives as epoch milliseconds or as ISO text
                v = a["date"]
                day = (dt.datetime.fromtimestamp(v / 1000, UTC).date() if isinstance(v, (int, float))
                       else dt.date.fromisoformat(str(v)[:10]))
                rows[day] = a["n_total"]
            off += len(feats)
            if not feats or not d.get("exceededTransferLimit"):
                break
    except Exception as e:
        print(f"portwatch fetch failed: {e}")
        rows = {}
    _CACHE["pw"] = rows
    return rows


def ask_weekly(day, live):
    """Mondays: Hormuz transits over the 7 days after `day`, against the published record (which lags ~10 days)."""
    pw = portwatch()
    if len(pw) < 120:
        return []
    last = max(pw)
    means = []
    for j in range(27):                                    # non-overlapping weeks ending at the latest published day
        vals = [pw[last - dt.timedelta(days=7 * j + i)] for i in range(7) if last - dt.timedelta(days=7 * j + i) in pw]
        if len(vals) < 6:
            break
        means.append(sum(vals) / len(vals))
    if len(means) < 12:
        return []
    T0 = session(day)[1]
    ge = [m >= 10 for m in means]
    up = [means[j] > means[j + 1] for j in range(len(means) - 1)]
    base10 = shrink(sum(ge[:-1]), len(ge) - 1, 0.25, 4)
    like10 = [ge[j] for j in range(len(ge) - 1) if ge[j + 1] == ge[0]]
    baseup = shrink(sum(up[:-1]), len(up) - 1, 0.5, 4)
    likeup = [up[j] for j in range(len(up) - 1) if up[j + 1] == up[0]]
    extra = dict(ask_date=day.isoformat(), latest=last.isoformat())
    span = f"{(day + dt.timedelta(days=1)).isoformat()} to {(day + dt.timedelta(days=7)).isoformat()}"
    return [question("weekly", T0, "HORMUZ", "Strait of Hormuz transits", "hz10", "7d", round(means[0], 2), 10.0,
                     base10, shrink(sum(like10), len(like10), base10, 4),
                     f"Hormuz ship transits (IMF PortWatch) average 10 a day or more over {span}? "
                     f"The latest published week, ending {last.isoformat()}, averaged {means[0]:.1f}.", live, **extra),
            question("weekly", T0, "HORMUZ", "Strait of Hormuz transits", "hzup", "7d", round(means[0], 2), None,
                     baseup, shrink(sum(likeup), len(likeup), baseup, 4),
                     f"Hormuz ship transits (IMF PortWatch) average more over {span} than the {means[0]:.1f} a day "
                     f"of the latest published week, ending {last.isoformat()}?", live, **extra)]


# ── the analyst ──────────────────────────────────────────────────────────────────────────────────────────────
def as_int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def utc(t, f="%m-%d %H:%M"):
    return dt.datetime.fromtimestamp(t, UTC).strftime(f)


def parse_iso(sv):
    return ep(dt.datetime.strptime(sv, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC))


def feed_items():
    """News reports the ingest has stored, oldest first: (reported epoch, source, headline, first line of the body).
    Read from inbox/latest.md and the inbox/processed files of the last 9 days. Reports with no report time are
    left out."""
    if "items" in _CACHE:
        return _CACHE["items"]
    paths = [INBOX]
    proc = ROOT / "inbox" / "processed"
    if proc.exists():
        paths += [q for q in proc.glob("*.md") if q.stat().st_mtime >= time.time() - 9 * 86400]
    seen = {}
    for path in paths:
        if not path.exists():
            continue
        with open(path, "rb") as f:                        # the newest reports are at the end of the file
            f.seek(0, 2)
            f.seek(max(0, f.tell() - 12_000_000))
            lines = f.read().decode("utf-8", "replace").splitlines()
        for i, line in enumerate(lines):
            m = ITEM.match(line)
            if not m:
                continue
            try:
                t = ep(dt.datetime.strptime(m.group(3).rstrip(",")[:16], "%Y-%m-%dT%H:%M").replace(tzinfo=UTC))
            except ValueError:
                continue
            nxt = lines[i + 1].strip() if i + 1 < len(lines) and lines[i + 1].startswith("  ") else ""
            title = m.group(1).strip()
            if title.lower() not in seen or t < seen[title.lower()][0]:
                seen[title.lower()] = (t, m.group(2).strip(), title, "" if nxt.startswith("http") else nxt)
    _CACHE["items"] = sorted(seen.values())
    return _CACHE["items"]


def headlines(T0, hours=6, limit=70):
    """The newest reports published in the `hours` before T0, newest first. Nothing after T0. Truth Social posts
    are left out here (rhetoric, not events); the judge still sees them, because a post can settle a question."""
    its = [it for it in feed_items() if T0 - hours * 3600 <= it[0] <= T0 and it[1] != "trump-truth"][-limit:]
    return [f"  {utc(t)} ({src}) {title[:140]}" for t, src, title, _ in reversed(its)]


def load_scored(live_only=False):
    rows, seen = [], set()
    for p in sorted(SCORED.glob("*.csv")) if SCORED.exists() else []:
        with open(p, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["qid"] not in seen and (not live_only or r["live"] == "1"):
                    seen.add(r["qid"])
                    rows.append(r)
    return rows


def is_news(r):
    return r["round"] == "news"


def deadline_class(label):
    return "hours" if label in ("30m", "60m", "2h", "4h", "8h") else "days"


def event_base(rows, label):
    """How often past news questions of the same deadline class came true, shrunk toward 0.30 while the record
    is short. Returns (rate, number of past questions)."""
    same = [int(r["outcome"]) for r in rows if is_news(r) and deadline_class(r["horizon"]) == deadline_class(label)]
    return shrink(sum(same), len(same), 0.30, 8), len(same)


def calibration(pairs):
    out = []
    for lo in (0.0, 0.2, 0.4, 0.6, 0.8):
        sub = [o for p, o in pairs if lo <= p < lo + 0.2 or (lo == 0.8 and p == 1.0)]
        if sub:
            out.append((f"{int(lo * 100)}-{int(lo * 100) + 20}%", sum(sub) / len(sub), len(sub)))
    return out


def feedback(rows):
    """The analyst's own record, as text for its next prompt."""
    mine = [r for r in rows if r["analyst"] not in ("", None)]
    if len(mine) < 10:
        return "No scored answers yet. Start from the base rate and move away from it only with a reason."
    sq = lambda r, who: (float(r[who]) - int(r["outcome"])) ** 2
    L = [f"Your record on {len(mine)} scored practice answers (Brier, lower is better): you "
         f"{sum(sq(r, 'analyst') for r in mine) / len(mine):.3f}, the base rate "
         f"{sum(sq(r, 'base') for r in mine) / len(mine):.3f}, a coin 0.250.",
         "When you said | how often it came true | answers"]
    L += [f"  {band} | {rate:.0%} | {n}" for band, rate, n in
          calibration([(float(r["analyst"]), int(r["outcome"])) for r in mine])]
    L.append("Correct for any gap between what you said and what happened.")
    last = [r for r in mine if is_news(r)][-10:]
    if last:
        L.append("Your last settled news questions (what you said -> what happened):")
        L += [f"  {float(r['analyst']):.2f} -> {'YES' if r['outcome'] == '1' else 'NO'}: {r['text'][:150]}" for r in last]
    return "\n".join(L)


def claude_bin():
    if os.environ.get("GT_DRILL_ANALYST", "1") == "0":
        return None
    return os.environ.get("CLAUDE_BIN") or shutil.which("claude")


def claude_json(prompt, system, tag):
    """One headless Claude call with no tools that must answer with a JSON object. The prompt goes in on standard
    input. Returns (object or None, usage or None)."""
    cb = claude_bin()
    if not cb:
        return None, None
    cmd = [cb, "-p", "--output-format", "json", "--max-turns", "1", "--system-prompt", system]
    if os.environ.get("GT_DRILL_MODEL"):
        cmd += ["--model", os.environ["GT_DRILL_MODEL"]]
    cmd += ["--tools", ""]
    cwd = ROOT / "logs" / "drills_cwd"                     # an empty folder: the repo's CLAUDE.md is not loaded
    cwd.mkdir(parents=True, exist_ok=True)
    try:
        r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=120, cwd=cwd, encoding="utf-8")
        env = json.loads(r.stdout)
        m = re.search(r"\{.*\}", env.get("result") or "", flags=re.S)
        obj = json.loads(m.group(0)) if m else None
    except Exception as e:
        print(f"{tag} call failed: {e}")
        return None, None
    u = env.get("usage") or {}
    return obj, {"calls": 1, "input": u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
                 + u.get("cache_read_input_tokens", 0), "output": u.get("output_tokens", 0),
                 "cost_usd": env.get("total_cost_usd") or 0.0}


def spend(st, now_t, usage):
    if usage:
        days = st.setdefault("usage", {})
        u = days.setdefault(utc(now_t, "%Y-%m-%d"), {"calls": 0, "input": 0, "output": 0, "cost_usd": 0.0})
        for k, v in usage.items():
            u[k] = u[k] + v
        for old in sorted(days)[:-30]:                     # keep a month
            del days[old]


# ── news questions: write, answer, settle ────────────────────────────────────────────────────────────────────
def write_events(T0, open_q, rows):
    """One call: the writer reads the reports of the last 6 hours and writes questions about what happens next."""
    heads = headlines(T0)
    if len(heads) < 5:
        return [], None
    still = [q["text"] for q in open_q if q["round"] == "news"]
    past = [int(r["outcome"]) for r in rows if is_news(r)]
    L = [f"Time now: {utc(T0, '%A %Y-%m-%d %H:%M')} UTC ({et(T0).strftime('%H:%M')} in New York).",
         "You write practice forecasting questions for a desk that forecasts world events: wars and ceasefires, "
         "diplomacy, sanctions, shipping chokepoints, decisions by central banks, governments, courts and "
         "legislatures, elections, export controls. It is not a markets desk.", "",
         "News reports from the last 6 hours, newest first (time UTC, source, headline):"] + heads
    L += ["", "Questions still open (do not repeat or closely paraphrase them):"] + ["  " + t for t in still[-40:]] if still else []
    if len(past) >= 12:
        L += ["", f"Of the last {len(past[-60:])} questions you wrote, {sum(past[-60:]) / len(past[-60:]):.0%} came true. "
              "Aim for between 30% and 60%."]
    L += ["", f"Write {NEWS_N} new yes/no questions about what happens NEXT in the stories above.", "Rules:",
          "1. Each question is about an event in the world: an attack, a statement or decision by a named official "
          "or body, a vote, a ruling, a meeting or its outcome, a deployment, a sanction, a published figure. "
          "Never about a market price, a share price, a yield or an index.",
          "2. It is settled by news reports alone: YES if a report published after now and by the deadline says "
          "the event happened, NO if no such report appears by then. Write that rule in one sentence in 'settle', "
          "naming what a report must say.",
          "3. The event must not already be reported as having happened.",
          f"4. 'minutes' is the deadline in minutes from now, one of {', '.join(str(m) for m in DEADLINES)}. "
          "At least half of the questions must use 480 or less.",
          "5. Aim for real doubt. Skip anything nearly certain either way. Mix questions you think are more "
          "likely than not with questions you think are less likely than not.",
          "6. Spread the questions over different stories, and prefer stories that are moving right now.",
          "7. 'keywords': 3 to 8 lower-case words or short phrases. Any report that settles the question YES "
          "would contain at least one of them.",
          f"8. 'lane' is one of: {', '.join(LANES)}.",
          "9. A reader must be able to settle it from a headline. Avoid questions that turn on fine wording, on "
          "what counts as 'addressing' or 'signalling' something, or on details a headline would not carry.", "",
          'Reply with one JSON object and no other text: {"questions": [{"text": "...?", "settle": "...", '
          '"minutes": 120, "keywords": ["..."], "lane": "..."}]}']
    obj, usage = claude_json("\n".join(L), WRITER_SYSTEM, "writer")
    qs, have = [], {re.sub(r"\W+", " ", t.lower()).strip() for t in still}
    for raw in (obj or {}).get("questions") or []:
        try:
            text, settle = str(raw["text"]).strip(), str(raw["settle"]).strip()
            minutes = int(raw["minutes"])
            kws = [str(k).lower().strip() for k in raw["keywords"] if str(k).strip()][:8]
        except (KeyError, TypeError, ValueError):
            continue
        norm = re.sub(r"\W+", " ", text.lower()).strip()
        if (minutes not in DEADLINES or not 20 <= len(text) <= 320 or not settle or len(kws) < 2 or norm in have
                or MARKET_Q.search(text)):
            continue
        have.add(norm)
        label = DEADLINES[minutes]
        base, n = event_base(rows, label)
        lane = raw.get("lane") if raw.get("lane") in LANES else "other"
        qs.append({"qid": f"{utc(T0, '%Y%m%d-%H%M')}Z-ev{len(qs) + 1}", "round": "news", "asked_utc": iso(T0),
                   "resolves_utc": iso(T0 + minutes * 60), "template": "event", "instrument": lane, "name": lane,
                   "horizon": label, "ref": None, "thr": None, "base": round(base, 4), "base_n": n, "pattern": None,
                   "analyst": None, "text": text, "settle": settle[:400], "keywords": kws, "live": 1})
        if len(qs) == NEWS_N:
            break
    return qs, usage


def ask_analyst(qs, T0, rows):
    """One call. Returns ({qid: probability}, usage); an empty dict when Claude is unavailable or the reply is unusable."""
    if not qs or not claude_bin():
        return {}, None
    news = headlines(T0)                                   # nothing reported after the round time
    L = [f"Time now: {utc(T0, '%A %Y-%m-%d %H:%M')} UTC ({et(T0).strftime('%H:%M')} in New York).",
         "These are practice questions that will be checked. For each one give the probability that the answer is YES.",
         "A news question is YES only if a news report published after now and by its deadline says the event "
         "happened. If nothing is reported by then it is NO, so short deadlines usually deserve low numbers.",
         "'base' is how often past questions of the same kind came true. It is a starting point, not an answer.", "",
         feedback(rows), "",
         "News reports from the last 6 hours, newest first (time UTC, source, headline):" if news
         else "No recent news reports are available."] + news + ["", "Questions:"]
    for i, q in enumerate(qs, 1):
        if q["round"] == "news":
            base = f"base {q['base']:.2f} from {q['base_n']} past questions" if q.get("base_n") else "no base rate yet"
            L.append(f"  q{i}: {q['text']} Deadline {utc(parse_iso(q['resolves_utc']), '%a %H:%M')} UTC "
                     f"({q['horizon']} from now). Settles YES if: {q['settle']} [{base}]")
        else:
            L.append(f"  q{i}: {q['text']} [base {q['base']:.2f}, pattern {q['pattern']:.2f}]")
    L += ["", 'Reply with one JSON object mapping each question id to a probability between 0.02 and 0.98, '
          'like {"q1": 0.55, "q2": 0.31}. No other text.']
    raw, usage = claude_json("\n".join(L), ANALYST_SYSTEM, "analyst")
    ans = {}
    for i, q in enumerate(qs, 1):
        v = (raw or {}).get(f"q{i}")
        if isinstance(v, (int, float)) and not isinstance(v, bool) and 0 <= v <= 1:
            ans[q["qid"]] = min(0.98, max(0.02, float(v)))
    return ans, usage


def judge_events(due, st, now_t):
    """Settle news questions whose deadline has passed, from the reports published inside each question's window.
    Returns {qid: (outcome, evidence)} or {qid: "void"}; a question that cannot be settled yet is left out."""
    items = feed_items()
    newest = items[-1][0] if items else 0
    out, todo = {}, []
    for q in due:
        A, H = parse_iso(q["asked_utc"]), parse_iso(q["resolves_utc"])
        if newest < H:                                     # the feed has not caught up past the deadline (outage?)
            continue
        win = [it for it in items if A < it[0] <= H]
        hits = [it for it in win if any(k in (it[2] + " " + it[3]).lower() for k in q["keywords"])]
        cand = win if len(win) <= 120 else hits[-80:]
        if cand:
            todo.append((q, cand))
        else:
            out[q["qid"]] = (0, "no report in the window matched")
    while todo:
        batch, reports = [], []
        while todo and len(batch) < 10 and len(set(reports) | set(todo[0][1])) <= 260:
            batch.append(todo.pop(0))
            reports = sorted(set(reports) | set(batch[-1][1]))
        if not batch:                                      # one question alone is over the limit: trim it
            q, cand = todo.pop(0)
            batch, reports = [(q, cand[-260:])], sorted(cand[-260:])
        num = {it: i for i, it in enumerate(reports, 1)}
        L = ["Reports (number, time UTC, source, headline, first line):"]
        L += [f"  {i}. {utc(it[0])} ({it[1]}) {it[2][:160]}" + (f" | {it[3][:140]}" if it[3] else "") for it, i in num.items()]
        L += ["", "Questions:"]
        for j, (q, cand) in enumerate(batch, 1):
            L += [f"  e{j} (asked {utc(parse_iso(q['asked_utc']))} UTC, deadline {utc(parse_iso(q['resolves_utc']))} UTC): {q['text']}",
                  f"      Rule: {q['settle']}",
                  f"      Reports published inside its window: {', '.join(str(num[it]) for it in cand)}"]
        L += ["", 'For each question answer "yes" only if one of the reports listed for it says that the event '
              "happened after the question was asked, and give that report's number.",
              "A report that only repeats what was already known before the question was asked does not count. "
              "A report of a plan, a threat, a possibility, a call for action or an expectation is not the event.",
              'Answer "no" if none of its reports says so. Answer "unclear" only if its reports contradict each '
              "other or the rule cannot be applied.", "",
              'Reply with one JSON object and no other text, like {"e1": {"outcome": "yes", "report": 12}, '
              '"e2": {"outcome": "no"}}']
        obj, usage = claude_json("\n".join(L), JUDGE_SYSTEM, "judge")
        spend(st, now_t, usage)
        if obj is None:
            st["judge_retry_after"] = now_t + 30 * 60
            break
        back = {i: it for it, i in num.items()}
        for j, (q, cand) in enumerate(batch, 1):
            v = obj.get(f"e{j}") if isinstance(obj.get(f"e{j}"), dict) else {}
            verdict = str(v.get("outcome", "")).lower()
            if verdict == "no":
                out[q["qid"]] = (0, "")
            elif verdict == "yes" and back.get(as_int(v.get("report"))) in cand:
                it = back[as_int(v["report"])]
                out[q["qid"]] = (1, f"{utc(it[0])} ({it[1]}) {it[2][:200]}")
            elif verdict in ("yes", "unclear"):            # a yes with no valid report behind it does not count
                out[q["qid"]] = "void"
    return out


# ── resolving and scoring ────────────────────────────────────────────────────────────────────────────────────
def outcome(q, now_t, pw_ok=True):
    """(outcome 0/1, outcome value) once the data can settle the question; None while it cannot; 'void' if it never
    will. Nothing is fetched before the earliest time a question could resolve."""
    asked = ep(dt.datetime.strptime(q["asked_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC))
    if q["round"] == "intraday":
        H = ep(dt.datetime.strptime(q["resolves_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC))
        if now_t < H + 20 * 60:
            return None
        z = bars5(q["instrument"]).at(H)
        if not z or z[0] <= q["ref_ts"]:
            return "void" if now_t > H + 3 * 86400 else None
        px = z[1]
    elif q["round"] == "daily":
        day = dt.date.fromisoformat(q["ask_date"])
        if now_t < session(weekday_after(day, q["sessions"]))[1] + 20 * 60:
            return None
        later = [d for d in sessions_seen() if d > day]
        if len(later) < q["sessions"]:
            return "void" if now_t > asked + 20 * 86400 else None
        o, c = session(later[q["sessions"] - 1])
        if now_t < c + 20 * 60:
            return None
        z = bars5(q["instrument"]).at(c)
        if not z or z[0] < o:
            return "void" if now_t > c + 3 * 86400 else None
        px = z[1]
    else:
        day = dt.date.fromisoformat(q["ask_date"])
        if not pw_ok or now_t < asked + 8 * 86400:         # the published record lags by about 10 days
            return None
        pw = portwatch()
        vals = [pw[day + dt.timedelta(days=i)] for i in range(1, 8) if day + dt.timedelta(days=i) in pw]
        if len(vals) < 6 or max(pw, default=day) < day + dt.timedelta(days=7):
            return "void" if now_t > asked + 40 * 86400 else None
        px = sum(vals) / len(vals)
        return (1 if (px >= 10 if q["template"] == "hz10" else px > q["ref"]) else 0), px
    if q["template"] == "up":
        return (1 if px > q["ref"] else 0), px
    return (1 if abs(px / q["ref"] - 1) > q["thr"] else 0), px


def row_of(q, res, now_t, evidence=""):
    news = q["round"] == "news"
    return {"qid": q["qid"], "round": q["round"], "asked_utc": q["asked_utc"], "resolved_utc": iso(now_t),
            "template": q["template"], "instrument": q["instrument"], "horizon": q["horizon"],
            "ref": "" if q["ref"] is None else round(q["ref"], 4),
            "thr": "" if q["thr"] is None else f"{q['thr']:.6f}",
            "outcome_px": "" if res[1] is None else f"{res[1]:.4f}", "outcome": res[0],
            "base": q["base"], "pattern": "" if q.get("pattern") is None else q["pattern"],
            "analyst": "" if q.get("analyst") is None else q["analyst"], "live": q["live"],
            "text": q["text"] if news or q["round"] == "weekly" else "", "evidence": evidence}


def write_rows(rows):
    SCORED.mkdir(parents=True, exist_ok=True)
    by = {}
    for r in rows:
        by.setdefault(r["resolved_utc"][:10], []).append(r)
    for day, rs in by.items():
        p = SCORED / f"{day}.csv"
        fresh = not p.exists()
        with open(p, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS)
            if fresh:
                w.writeheader()
            w.writerows(rs)


def load_json(p, default):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default


def save_json(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def resolve(now_t, st, judge):
    """Score every open question the data or the news can settle now. News questions are settled only when
    `judge` is set (once per news round), so their judge calls are batched."""
    open_q = load_json(OPEN, [])
    keep, done, void = [], [], 0
    pw_ok = now_t - st.get("pw_checked", 0) >= 6 * 3600    # poll PortWatch at most every 6 hours
    if pw_ok and any(q["round"] == "weekly" for q in open_q):
        st["pw_checked"] = now_t
    verdicts = {}
    if judge and now_t >= st.get("judge_retry_after", 0):
        due = [q for q in open_q if q["round"] == "news" and now_t >= parse_iso(q["resolves_utc"]) + GRACE]
        verdicts = judge_events(due, st, now_t) if due else {}
    for q in open_q:
        if q["round"] == "news":
            v = verdicts.get(q["qid"])
            if v is None:                                  # not due, not judged yet, or the feed has not caught up
                if now_t > parse_iso(q["resolves_utc"]) + 3 * 86400:
                    void += 1
                else:
                    keep.append(q)
            elif v == "void":
                void += 1
            else:
                done.append(row_of(q, (v[0], None), now_t, v[1]))
            continue
        res = outcome(q, now_t, pw_ok)
        if res is None:
            keep.append(q)
        elif res == "void":
            void += 1
        else:
            done.append(row_of(q, res, now_t))
    if done or void:
        write_rows(done)
        save_json(OPEN, keep)
    return len(done), void


def tick(now_t, every):
    """Settle what is due, then ask the rounds that are due at `now_t`."""
    st = load_json(STATE, {})
    now_et = et(now_t)
    day = now_et.date()
    # the news round: its slot starts on the UTC clock; settling and writing both happen once per slot
    n_slot = now_t // (NEWS_EVERY * 60)
    Tn = n_slot * NEWS_EVERY * 60
    news_due = (claude_bin() is not None and st.get("news_slot") != f"{NEWS_EVERY}:{n_slot}"
                and now_t - Tn <= min(NEWS_EVERY * 60 - 60, 600))
    done, void = resolve(now_t, st, news_due)
    rows = load_scored(live_only=True)
    asked, note = [], ""
    if news_due:
        st["news_slot"] = f"{NEWS_EVERY}:{n_slot}"
        open_q = load_json(OPEN, [])
        fresh = [it for it in feed_items() if st.get("news_seen", 0) < it[0] <= Tn]
        if len(fresh) >= 3 and sum(q["round"] == "news" for q in open_q) < MAX_OPEN_NEWS:
            evs, usage = write_events(Tn, open_q, rows)
            spend(st, now_t, usage)
            if evs:
                st["news_seen"] = Tn
            asked += evs
            note += f", wrote {len(evs)} news question(s)"
        else:
            note += ", no fresh news"
    # the weekly measured-state round: Hormuz transits, Mondays after 16:20 ET
    if now_et.weekday() == 0 and now_et.time() >= dt.time(16, 20) and st.get("weekly") != day.isoformat():
        st["weekly"] = day.isoformat()
        asked += ask_weekly(day, True)
    # market rounds: off unless GT_DRILL_PRICES=1
    if PRICES and now_et.weekday() < 5:
        o, c = session(day)
        slot = (now_t - o) // (every * 60)
        T0 = o + slot * every * 60
        key = f"{day.isoformat()}:{every}:{slot}"
        if slot >= 1 and T0 < c and now_t - T0 <= min(every * 60 - 60, 600) and st.get("slot") != key:
            asked += ask_intraday(T0, every, True)
            st["slot"] = key
        elif now_et.time() >= dt.time(16, 20) and now_t - c <= 4 * 3600 and st.get("daily") != day.isoformat():
            if bars5("SPY").at(c) and bars5("SPY").at(c)[0] >= c - 900:      # the session really traded today
                asked += ask_daily(day, True)
            st["daily"] = day.isoformat()
    if asked:
        ans, usage = ask_analyst(asked, min(parse_iso(q["asked_utc"]) for q in asked), rows)
        spend(st, now_t, usage)
        for q in asked:
            q["analyst"] = ans.get(q["qid"])
        save_json(OPEN, load_json(OPEN, []) + asked)
        note += f", analyst answered {len(ans)}" if ans else ", no analyst"
    save_json(STATE, st)
    stale = f", no fresh price for {' '.join(STALE)}" if STALE else ""
    print(f"drills: settled {done}" + (f", void {void}" if void else "") + f", asked {len(asked)}{note}{stale}, "
          f"open {len(load_json(OPEN, []))}")


# ── reporting ────────────────────────────────────────────────────────────────────────────────────────────────
def prob(r, who):
    if who == "coin":
        return 0.5
    return float(r[who]) if r[who] not in ("", None) else None


def summarize(rows):
    """Brier by forecaster, overall and by template and horizon, on the rows each forecaster answered."""
    out = {"n": len(rows), "days": len({r["asked_utc"][:10] for r in rows}), "groups": {}}
    groups = {"all": rows}
    for r in rows:
        groups.setdefault(f"{r['template']} / {r['horizon']}", []).append(r)
    for name, rs in groups.items():
        g = {"n": len(rs), "yes": sum(int(r["outcome"]) for r in rs) / len(rs)}
        for who in FORECASTERS:
            sub = [(prob(r, who), int(r["outcome"])) for r in rs if prob(r, who) is not None]
            g[who] = {"n": len(sub), "brier": sum((p - o) ** 2 for p, o in sub) / len(sub)} if sub else None
        out["groups"][name] = g
    return out


def day_boot(rows, a, b):
    """Share of day-resamples in which forecaster b beats forecaster a (lower Brier), on rows both answered."""
    by = {}
    for r in rows:
        pa, pb = prob(r, a), prob(r, b)
        if pa is not None and pb is not None:
            o = int(r["outcome"])
            by.setdefault(r["asked_utc"][:10], []).append((pa - o) ** 2 - (pb - o) ** 2)
    days = sorted(by)
    if len(days) < 5:
        return None
    rng = random.Random(7)
    wins = 0
    for _ in range(1000):
        pick = [d for day in (rng.choice(days) for _ in days) for d in by[day]]
        wins += sum(pick) > 0
    return wins / 1000


def table(summary):
    L = ["| Questions | Answers | Came true | Coin | Base | Pattern | Analyst |", "|---|---|---|---|---|---|---|"]
    for name, g in sorted(summary["groups"].items(), key=lambda kv: (kv[0] != "all", kv[0])):
        cell = lambda who: f"{g[who]['brier']:.3f}" if g[who] else "-"
        an = f"{g['analyst']['brier']:.3f} ({g['analyst']['n']})" if g["analyst"] else "-"
        L.append(f"| {name} | {g['n']} | {g['yes']:.0%} | {cell('coin')} | {cell('base')} | {cell('pattern')} | {an} |")
    return L


def section(title, rows, rival):
    """One block of the report: the score table, the analyst against its rival baseline, its calibration."""
    s = summarize(rows)
    s["analyst_beats_" + rival] = day_boot(rows, rival, "analyst")
    L = ["", f"## {title}: {s['n']} scored answers over {s['days']} day(s)", ""] + table(s)
    if s["analyst_beats_" + rival] is not None:
        L += ["", f"The analyst beats the {rival} baseline in {s['analyst_beats_' + rival]:.0%} of day-resamples."]
    else:
        L += ["", f"Too few days yet to say whether the analyst beats the {rival} baseline (needs 5)."]
    cal = calibration([(float(r["analyst"]), int(r["outcome"])) for r in rows if r["analyst"] not in ("", None)])
    if cal:
        L += ["", "| Analyst said | Came true | Answers |", "|---|---|---|"]
        L += [f"| {band} | {rate:.0%} | {n} |" for band, rate, n in cal]
    return s, L


def report():
    rows = load_scored(live_only=True)
    st = load_json(STATE, {})
    world = [r for r in rows if r["round"] in ("news", "weekly")]
    market = [r for r in rows if r["round"] in ("intraday", "daily")]
    L = ["# Practice questions report", "",
         "Brier score, lower is better; 0.250 is a coin. Practice only: nothing here is a published call."]
    summary = {}
    if world:
        summary["world"], block = section("World-event questions", world, "base")
        L += block
        last = [r for r in world if is_news(r)][-15:]
        if last:
            L += ["", "### Last settled news questions", "", "| Asked (UTC) | Deadline | Question | Analyst | Outcome | Settled by |",
                  "|---|---|---|---|---|---|"]
            clean = lambda t: t.replace("|", "/").replace("\n", " ")
            L += [f"| {r['asked_utc'][5:16].replace('T', ' ')} | {r['horizon']} | {clean(r['text'])} | "
                  f"{r['analyst'] or '-'} | {'YES' if r['outcome'] == '1' else 'NO'} | {clean(r['evidence']) or '-'} |"
                  for r in reversed(last)]
    else:
        L += ["", "## World-event questions", "", "No answers scored yet."]
    if market:
        summary["market"], block = section("Market questions", market, "pattern")
        L += block
    if summary:
        save_json(SUMMARY, summary)
    use = st.get("usage") or {}
    if use:
        L += ["", "## Claude usage", "", "| Day (UTC) | Calls | Input tokens | Output tokens | Cost at list prices |", "|---|---|---|---|---|"]
        L += [f"| {d} | {use[d]['calls']} | {use[d]['input']:,} | {use[d]['output']:,} | ${use[d]['cost_usd']:.2f} |"
              for d in sorted(use)[-7:]]
    rp = load_json(REPLAY_SUMMARY, None)
    if rp:
        L += ["", f"## Market baselines replayed over {rp['days']} past session(s), {rp['n']} answers "
              f"(rounds every {rp['every']} minutes, no analyst)", ""] + table(rp)
        if rp.get("pattern_beats_coin") is not None:
            L += ["", f"The pattern baseline beats a coin in {rp['pattern_beats_coin']:.0%} of day-resamples."]
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"drills report: {len(rows)} live answers -> {REPORT.relative_to(ROOT)}")


def replay(n_days, every):
    """Score the baselines over past sessions. Each question is built from bars before its round time only."""
    now_t = ep(dt.datetime.now(UTC))
    today = et(now_t).date()
    days = trading_days(today)
    rows = []
    for day in days[-n_days:]:
        if len([d for d in days if d < day]) < 8:
            continue
        o, c = session(day)
        t = o + every * 60
        while t < c:
            for q in ask_intraday(t, every, live=False):
                res = outcome(q, c + 86400)
                if res not in (None, "void"):
                    rows.append(row_of(q, res, c))
            t += every * 60
        for q in ask_daily(day, live=False):
            res = outcome(q, now_t)
            if res not in (None, "void"):
                rows.append(row_of(q, res, c))
    if not rows:
        sys.exit("replay produced no rows (no data?)")
    s = summarize(rows)
    s.update(every=every, pattern_beats_coin=day_boot(rows, "coin", "pattern"),
             run_utc=iso(ep(dt.datetime.now(UTC))))
    save_json(REPLAY_SUMMARY, s)
    print(f"replay: {s['n']} answers over {s['days']} day(s), rounds every {every} min")
    for line in table(s):
        print(line)
    print(f"pattern beats coin in {s['pattern_beats_coin']:.0%} of day-resamples" if s["pattern_beats_coin"] is not None else "")


def main():
    if EVERY % 5 or not 5 <= EVERY <= 120:
        sys.exit("GT_DRILL_EVERY_MIN must be a multiple of 5 between 5 and 120")
    if NEWS_EVERY % 5 or not 5 <= NEWS_EVERY <= 720:
        sys.exit("GT_DRILL_NEWS_EVERY_MIN must be a multiple of 5 between 5 and 720")
    assert not any(BANNED.search(s + " " + n) for s, n in INSTRUMENTS), "oil, energy and defense prices are banned"
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    arg = lambda flag, default: sys.argv[sys.argv.index(flag) + 1] if flag in sys.argv else default
    if cmd == "tick":
        now = arg("--now", None)
        now_t = ep(dt.datetime.strptime(now, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)) if now else ep(dt.datetime.now(UTC))
        tick(now_t, EVERY)
    elif cmd == "report":
        report()
    elif cmd == "replay":
        replay(int(arg("--days", "10")), EVERY)
        report()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
