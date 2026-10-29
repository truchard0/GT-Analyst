#!/usr/bin/env python3
"""AI-financing stress index from point-in-time headlines. Stdlib only.

Feeds market-transmission §5.2 and doctrine §13 / contrarian #8 (Minsky financing test): the
catalyst a call against the AI complex needs is an attack on its FINANCING or its capex
architecture, not a rate argument. This index measures that attack from the news tape.

  data      Google News, one date-bounded query per day (after:D-1 before:D+1), headlines with
            AI-infrastructure subjects (neocloud, data center, AI capex, hyperscaler, named
            neoclouds). Each item keeps its own publication time, so an as-of reading uses only
            headlines published before the as-of instant.
  classify  STRESS (credit, debt, spreads, downgrades, IPO pulled or delayed, capex cut, writedown,
            overbuild) vs RELIEF (capex raised, financing secured, IPO priced or upsized).
  index     daily (stress - relief) / (stress + relief + 1); weekly = mean of the trailing 7 days;
            z = this week vs the 4 weeks before it.

    python tools/ai_stress_index.py fetch [--from 2026-08-01]   # append new days to the cache
    python tools/ai_stress_index.py build                        # data/ai_stress/index.csv
    python tools/ai_stress_index.py latest [--asof YYYY-MM-DD]   # the as-of reading + gate verdict
"""
import csv
import datetime as dt
import email.utils
import pathlib
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "ai_stress"
QUERY = ('(neocloud OR CoreWeave OR Nebius OR "data center" OR "data centre" OR "AI capex" OR '
         '"AI infrastructure" OR hyperscaler OR "AI spending")')
STRESS = re.compile(
    r"\b(credit|debt|bond|loan|spread|downgrad|default|distress|refinanc|covenant|margin call|"
    r"pull[s]? (its |the )?ipo|withdraw|postpone|delay|cancel|scrap|scale[sd]? back|pause|"
    r"cut[s]? (capex|spending|guidance)|capex cut|writedown|write-down|impair|overbuil|glut|"
    r"bubble|selloff|sell-off|plunge|tumble|slump|crash|snag|warning|miss(es)?\b|put off|hold off)", re.I)
RELIEF = re.compile(
    r"\b(raises? (capex|spending|guidance|forecast)|record (capex|spending)|secures?|lands? \$|"
    r"oversubscribed|upsized?|prices? ipo|ipo (soars|jumps|pops)|beats?|expands?|boost)", re.I)
GATE_Z = 1.0   # z at or above this = financing attack present (permits an AI-complex fade, §5.2)


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read()


def cache_path():
    return OUT / "headlines.csv"


def load_cache():
    p = cache_path()
    if not p.exists():
        return []
    return [(r["published_utc"], r["title"]) for r in csv.DictReader(open(p, encoding="utf-8"))]


def fetch(start):
    OUT.mkdir(parents=True, exist_ok=True)
    have = load_cache()
    seen = {t.lower() for _, t in have}
    days_done = {ts[:10] for ts, _ in have}
    d, end = start, dt.date.today()
    added = 0
    while d <= end:
        if d.isoformat() in days_done and d < end - dt.timedelta(days=2):
            d += dt.timedelta(days=1)
            continue
        q = f"{QUERY} after:{(d - dt.timedelta(days=1)).isoformat()} before:{(d + dt.timedelta(days=1)).isoformat()}"
        url = "https://news.google.com/rss/search?q=" + urllib.parse.quote(q) + "&hl=en-US&gl=US&ceid=US:en"
        try:
            root = ET.fromstring(get(url))
            for it in root.findall(".//item"):
                title, pub = (it.findtext("title") or "").strip(), it.findtext("pubDate")
                if not title or not pub or title.lower() in seen:
                    continue
                seen.add(title.lower())
                ts = email.utils.parsedate_to_datetime(pub).astimezone(dt.UTC).strftime("%Y-%m-%dT%H:%MZ")
                have.append((ts, title))
                added += 1
        except Exception as e:
            print("fetch fail", d, e)
        time.sleep(1.5)
        d += dt.timedelta(days=1)
    have.sort()
    with open(cache_path(), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["published_utc", "title"])
        w.writerows(have)
    print(f"cache: {len(have)} headlines (+{added})")


def classify(title):
    s, r = bool(STRESS.search(title)), bool(RELIEF.search(title))
    return 1 if s and not r else -1 if r and not s else 0


def window_index(items, lo, hi):
    st = rl = 0
    for ts, title in items:
        if lo < ts <= hi:
            c = classify(title)
            st += c == 1
            rl += c == -1
    return (st - rl) / (st + rl + 1), st, rl


def reading(items, asof):
    """as-of reading: this week's index and its z against the four weeks before (20:00 UTC cut)"""
    end = dt.datetime.fromisoformat(asof + "T20:00")
    vals = []
    for k in range(5):
        hi = end - dt.timedelta(days=7 * k)
        lo = hi - dt.timedelta(days=7)
        vals.append(window_index(items, lo.strftime("%Y-%m-%dT%H:%MZ"), hi.strftime("%Y-%m-%dT%H:%MZ")))
    cur, prior = vals[0], [v[0] for v in vals[1:]]
    mu = sum(prior) / len(prior)
    sd = (sum((v - mu) ** 2 for v in prior) / len(prior)) ** 0.5 or 1e-6
    return {"asof": asof, "index": round(cur[0], 3), "stress": cur[1], "relief": cur[2],
            "z": round((cur[0] - mu) / sd, 2), "gate": int((cur[0] - mu) / sd >= GATE_Z)}


def build():
    items = load_cache()
    if not items:
        sys.exit("no cache - run fetch first")
    first = dt.date.fromisoformat(items[0][0][:10]) + dt.timedelta(days=35)
    rows, d = [], first
    while d <= dt.date.today():
        rows.append(reading(items, d.isoformat()))
        d += dt.timedelta(days=1)
    with open(OUT / "index.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"index: {len(rows)} daily readings {rows[0]['asof']} .. {rows[-1]['asof']}")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "fetch":
        start = sys.argv[sys.argv.index("--from") + 1] if "--from" in sys.argv else "2026-08-01"
        fetch(dt.date.fromisoformat(start))
    elif cmd == "build":
        build()
    elif cmd == "latest":
        asof = sys.argv[sys.argv.index("--asof") + 1] if "--asof" in sys.argv else dt.date.today().isoformat()
        r = reading(load_cache(), asof)
        verdict = ("financing attack PRESENT - an AI-complex fade has its §5.2 catalyst" if r["gate"]
                   else "no financing attack - AI-complex fades lack a catalyst (stay capped)")
        print(f"{r}\n{verdict}")
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
