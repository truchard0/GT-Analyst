#!/usr/bin/env python3
"""Download the point-in-time inputs for the GT stock backtest. Stdlib only.

  prices    Yahoo Finance daily closes + volumes, 2025-08-01 .. today, for the universe
            (watchlist.json + data/sector_map.json + the fixed SECTOR_LEADERS list below), SPY,
            Brent (BZ=F) and sector ETFs
  rates     US Treasury daily par yield curve (2-year), 2025-2026
  news      Google News headlines per day (Iran / Hormuz / Houthi in the title), 2026-08-26 ..
            today, with each item's publication time - the engine only ever sees items
            published before its as-of cutoff
  earnings  Nasdaq earnings calendar for each trading day 2026-09-28 .. today+10 (report
            dates are scheduled weeks ahead, so they are as-of information)

Outputs go to data/gt_backtest/ (closes.csv, volumes.csv, rates.csv, news.csv, earnings.csv).

    python tools/gt_backtest_data.py                              # backtest inputs (committed)
    python tools/gt_backtest_data.py --out data/gt_backtest/live  # forward-test inputs (gitignored)
"""
import concurrent.futures as cf
import csv
import datetime as dt
import email.utils
import json
import pathlib
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "gt_backtest"
UA = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
START, END = dt.date(2025, 8, 1), dt.date.today() + dt.timedelta(days=1)

# Large caps for the sectors the doctrine's Branch-A/B table names (market-transmission §12)
# but the tech-heavy watchlist barely covers. Chosen from index leaders, not from outcomes.
SECTOR_LEADERS = {
    "energy": ["XOM", "CVX", "COP", "EOG", "SLB", "PSX", "MPC", "VLO", "OXY", "WMB", "KMI", "HAL"],
    "staples": ["PG", "KO", "PEP", "WMT", "COST", "PM", "MO", "MDLZ", "CL", "KMB"],
    "utilities": ["NEE", "SO", "DUK", "AEP", "D"],
    "financials": ["JPM", "BAC", "WFC", "GS", "MS", "C", "BRK-B"],
    "healthcare": ["LLY", "UNH", "JNJ", "ABBV", "MRK", "PFE"],
    "discretionary": ["HD", "MCD", "NKE", "SBUX", "LOW"],
    "airlines": ["DAL", "UAL", "AAL", "LUV"],
}
MARKET = ["SPY", "BZ=F", "XLE", "XLK", "SMH", "ITA", "XLP", "XLU", "XLF", "XLV", "XLY", "QQQ"]
YAHOO_ALIAS = {"MOG.A": "MOG-A", "BRK.B": "BRK-B"}


def get(url, headers=UA, timeout=40):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def universe():
    w = json.loads((ROOT / "watchlist.json").read_text(encoding="utf-8"))
    sm = json.loads((ROOT / "data" / "sector_map.json").read_text(encoding="utf-8"))
    names = set()
    for th in w["themes"].values():
        names.update(th.get("tickers", {}))
    for k, v in sm.items():
        if isinstance(v, dict):
            names.update(v.get("tickers", []))
    for lst in SECTOR_LEADERS.values():
        names.update(lst)
    return sorted(names)


def yahoo(sym):
    p1 = int(dt.datetime.combine(START, dt.time(), dt.UTC).timestamp())
    p2 = int(dt.datetime.combine(END, dt.time(), dt.UTC).timestamp())
    ys = YAHOO_ALIAS.get(sym, sym)
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(ys)}"
           f"?period1={p1}&period2={p2}&interval=1d")
    for attempt in range(4):
        try:
            d = json.loads(get(url))["chart"]["result"][0]
            q = d["indicators"]["quote"][0]
            adj = (d["indicators"].get("adjclose") or [{}])[0].get("adjclose") or q["close"]
            rows = {}
            for ts, c, v in zip(d["timestamp"], adj, q["volume"]):
                if c is None:
                    continue
                day = dt.datetime.fromtimestamp(ts, dt.UTC) + dt.timedelta(hours=-4)  # NY session date
                rows[day.date().isoformat()] = (round(c, 4), v or 0)
            return sym, rows
        except Exception:
            time.sleep(2 * (attempt + 1))
    return sym, {}


def fetch_prices():
    syms = sorted(set(universe()) | set(MARKET))
    with cf.ThreadPoolExecutor(6) as ex:
        res = dict(ex.map(yahoo, syms))
    dates = sorted({d for r in res.values() for d in r})
    ok = [s for s in syms if len(res[s]) > 50]
    for name, idx in (("closes.csv", 0), ("volumes.csv", 1)):
        with open(OUT / name, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["date"] + ok)
            for d in dates:
                w.writerow([d] + [res[s].get(d, ("", ""))[idx] for s in ok])
    print(f"prices: {len(ok)}/{len(syms)} symbols, {len(dates)} days, dropped: "
          f"{sorted(set(syms) - set(ok))}")


def fetch_rates():
    rows = []
    for y in (2025, 2026):
        url = ("https://home.treasury.gov/resource-center/data-chart-center/interest-rates/"
               f"daily-treasury-rates.csv/{y}/all?type=daily_treasury_yield_curve"
               f"&field_tdr_date_value={y}&page&_format=csv")
        for r in csv.DictReader(get(url).decode().splitlines()):
            m, d, yy = r["Date"].split("/")
            rows.append((f"{yy}-{m}-{d}", r.get("2 Yr", ""), r.get("10 Yr", "")))
    rows.sort()
    with open(OUT / "rates.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "y2", "y10"])
        w.writerows(rows)
    print(f"rates: {len(rows)} days, {rows[0][0]} .. {rows[-1][0]}")


def fetch_news():
    q = "(intitle:Iran OR intitle:Hormuz OR intitle:Houthi OR intitle:Houthis)"
    seen, out = set(), []
    d = dt.date(2026, 8, 26)
    while d <= END:
        qq = f"{q} after:{(d - dt.timedelta(days=1)).isoformat()} before:{(d + dt.timedelta(days=1)).isoformat()}"
        url = "https://news.google.com/rss/search?q=" + urllib.parse.quote(qq) + "&hl=en-US&gl=US&ceid=US:en"
        try:
            root = ET.fromstring(get(url, {"User-Agent": "Mozilla/5.0"}))
            for it in root.findall(".//item"):
                title = (it.findtext("title") or "").strip()
                pub = it.findtext("pubDate")
                if not title or not pub:
                    continue
                ts = email.utils.parsedate_to_datetime(pub).astimezone(dt.UTC)
                key = title.lower()
                if key in seen:
                    continue
                seen.add(key)
                out.append((ts.strftime("%Y-%m-%dT%H:%MZ"), title))
        except Exception as e:
            print("news fail", d, e)
        time.sleep(1.5)
        d += dt.timedelta(days=1)
    out.sort()
    with open(OUT / "news.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["published_utc", "title"])
        w.writerows(out)
    print(f"news: {len(out)} unique headlines")


def fetch_earnings():
    rows = []
    d = dt.date(2026, 9, 28)
    while d <= END + dt.timedelta(days=10):   # scheduled dates for the next forward week too
        if d.weekday() < 5:
            try:
                j = json.loads(get(f"https://api.nasdaq.com/api/calendar/earnings?date={d.isoformat()}"))
                for r in (j.get("data") or {}).get("rows") or []:
                    rows.append((d.isoformat(), r.get("symbol"), r.get("time")))
            except Exception as e:
                print("earnings fail", d, e)
            time.sleep(0.5)
        d += dt.timedelta(days=1)
    with open(OUT / "earnings.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "symbol", "time"])
        w.writerows(rows)
    print(f"earnings: {len(rows)} report-days")


if __name__ == "__main__":
    if "--out" in sys.argv:   # forward runs write to data/gt_backtest/live, never over the backtest inputs
        OUT = (ROOT / sys.argv[sys.argv.index("--out") + 1]).resolve()
    OUT.mkdir(parents=True, exist_ok=True)
    fetch_prices()
    fetch_rates()
    fetch_earnings()
    fetch_news()
