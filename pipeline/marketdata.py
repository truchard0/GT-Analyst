#!/usr/bin/env python3
"""READ-ONLY market-data bridge to the Trading Bot tree.

WHY THIS EXISTS
  GT-Analyst had no price feed, and that absence cost real things:
    * every LEVEL row needed a spot and a realised vol, so `range_odds.py` was being fed assumed
      inputs. That is exactly how `brent-band-q4` shipped with --vol 0.80 (about 13 percent
      annualised) for a tape realising ~2.5 percent/day, and how a "correction" moved the number
      0.47 the wrong way on 2026-09-22.
    * trade rules T08 (stale target) and T13 (stale invalidation) cannot run without session bars,
      so `ledger.py trade-check` has been printing NOT CHECKED for the two rules that caught the
      seven-week MU blind spot.
    * resolving a price-defined row meant shelling out to WSL by hand, which is how #70 and #27
      sat two days overdue.

WHAT IT IS AND IS NOT
  It READS prices through the Trading Bot's WSL virtualenv (the only interpreter here with
  yfinance). It writes NOTHING into the Trading Bot tree - the only thing it writes is a cache
  under GT-Analyst's own data/mdcache/. It places no orders, reads no account, and imports no
  Trading Bot code. It is a data tap, not an integration.

CONFIG (pipeline/.env or the environment; the defaults are what this machine has)
  GT_WSL_PYTHON   path, inside WSL, to an interpreter with yfinance
  GT_TRADINGBOT   path, inside WSL, to the Trading Bot tree (recorded for provenance only)

USE
  python pipeline/marketdata.py spot SMH SPY XLE
  python pipeline/marketdata.py closes SMH --start 2026-07-01
  python pipeline/marketdata.py bars MU --start 2026-07-01 --out bars.csv
  python pipeline/marketdata.py odds --spot-from CL=F --lo 55 --hi 140 --days 315
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import hashlib
import json
import os
import pathlib
import statistics
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "data" / "mdcache"
WSL_PYTHON = os.environ.get("GT_WSL_PYTHON", "~/.venvs/tradingbot/bin/python")
TRADINGBOT = os.environ.get("GT_TRADINGBOT", "/mnt/c/Users/hudso/Downloads/Trading Bot")
CACHE_TTL_H = 6.0


class MarketDataError(RuntimeError):
    """Raised loudly. A silent empty series is how a gate turns into decoration."""


def _key(*parts: str) -> pathlib.Path:
    h = hashlib.sha1("|".join(parts).encode()).hexdigest()[:16]
    return CACHE / f"{h}.json"


def _fresh(p: pathlib.Path) -> bool:
    if not p.exists():
        return False
    age_h = (_dt.datetime.now().timestamp() - p.stat().st_mtime) / 3600
    return age_h < CACHE_TTL_H


_FETCH = r"""
import json, sys
try:
    import yfinance as yf
    import pandas as pd
except Exception as e:
    print(json.dumps({"error": "yfinance unavailable: %s" % e})); raise SystemExit(0)
tks, start, end = sys.argv[1].split(","), sys.argv[2], sys.argv[3]
try:
    df = yf.download(tks, start=start, end=end, auto_adjust=True, progress=False)
except Exception as e:
    print(json.dumps({"error": "download failed: %s" % e})); raise SystemExit(0)
if df is None or len(df) == 0:
    print(json.dumps({"error": "empty frame for %s %s..%s" % (tks, start, end)})); raise SystemExit(0)
multi = isinstance(df.columns, pd.MultiIndex)
idx = [d.strftime("%Y-%m-%d") for d in df.index]
out = {}
for t in tks:
    rec = {}
    for field in ("Close", "High", "Low"):
        try:
            col = df[(field, t)] if multi else df[field]
        except Exception:
            rec[field] = []
            continue
        vals = list(col.values)
        rec[field] = [[idx[i], (None if vals[i] != vals[i] else float(vals[i]))]
                      for i in range(len(idx))]
    out[t] = rec
print(json.dumps(out))
"""


def _fetch(tickers: list[str], start: str, end: str) -> dict:
    CACHE.mkdir(parents=True, exist_ok=True)
    cp = _key(",".join(sorted(tickers)), start, end)
    if _fresh(cp):
        return json.loads(cp.read_text(encoding="utf-8"))
    cmd = ["wsl", "-e", "bash", "-lc",
           f"{WSL_PYTHON} - {','.join(tickers)} {start} {end} <<'__PY__'\n{_FETCH}\n__PY__"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180,
                           encoding="utf-8", errors="replace")
    except (OSError, subprocess.TimeoutExpired) as e:
        raise MarketDataError(f"could not reach the WSL interpreter {WSL_PYTHON!r}: {e}") from e
    body = (r.stdout or "").strip().splitlines()
    if not body:
        raise MarketDataError(f"no output from the fetcher (stderr: {(r.stderr or '')[-300:]})")
    try:
        data = json.loads(body[-1])
    except json.JSONDecodeError as e:
        raise MarketDataError(f"fetcher returned non-JSON: {body[-1][:200]}") from e
    if isinstance(data, dict) and data.get("error"):
        raise MarketDataError(str(data["error"]))
    cp.write_text(json.dumps(data), encoding="utf-8")
    return data


def _series(ticker: str, field: str, start: str, end: str) -> list[tuple[str, float]]:
    d = _fetch([ticker], start, end).get(ticker) or {}
    if "error" in d:
        raise MarketDataError(f"{ticker}: {d['error']}")
    return [(dt, v) for dt, v in (d.get(field) or []) if v is not None]


def closes(ticker: str, start: str, end: str | None = None) -> list[tuple[str, float]]:
    end = end or (_dt.date.today() + _dt.timedelta(days=1)).isoformat()
    s = _series(ticker, "Close", start, end)
    if not s:
        raise MarketDataError(f"{ticker}: no closes between {start} and {end}")
    return s


def spot_vol(ticker: str, start: str | None = None,
             end: str | None = None) -> tuple[float, float, int, str]:
    """-> (spot, realised daily vol in PERCENT, n closes, last date).

    PERCENT, because that is the unit `range_odds.py --vol` takes (1.6 = 1.6%/day). Getting that
    unit wrong is the single documented cause of a wrong correction in this repo, so the function
    returns it already in the tool's unit and the CLI prints the unit next to the number.
    """
    start = start or (_dt.date.today() - _dt.timedelta(days=120)).isoformat()
    s = closes(ticker, start, end)
    if len(s) < 10:
        raise MarketDataError(f"{ticker}: only {len(s)} closes — too few to estimate vol")
    import math
    rets = [math.log(s[i][1] / s[i - 1][1]) for i in range(1, len(s)) if s[i - 1][1] > 0]
    return s[-1][1], statistics.pstdev(rets) * 100.0, len(s), s[-1][0]


def bars(ticker: str, start: str, end: str | None = None) -> list[tuple[str, float, float]]:
    """Session (date, high, low) in the shape trade_rules.TradeContext.prices wants (T08/T13)."""
    end = end or (_dt.date.today() + _dt.timedelta(days=1)).isoformat()
    d = _fetch([ticker], start, end).get(ticker) or {}
    hi = {dt: v for dt, v in (d.get("High") or []) if v is not None}
    lo = {dt: v for dt, v in (d.get("Low") or []) if v is not None}
    out = [(dt, hi[dt], lo[dt]) for dt in sorted(hi) if dt in lo]
    if not out:
        raise MarketDataError(f"{ticker}: no high/low bars between {start} and {end}")
    return out


def write_bars_csv(tickers: list[str], start: str, path: pathlib.Path,
                   end: str | None = None) -> int:
    """Write the ticker,date,high,low CSV that `ledger.py trade-check --bars` consumes."""
    n = 0
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["ticker", "date", "high", "low"])
        for t in tickers:
            for dt, h, lo in bars(t, start, end):
                w.writerow([t.upper(), dt, h, lo]); n += 1
    return n


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("spot", help="spot + realised daily vol (in PERCENT, range_odds' unit)")
    sp.add_argument("tickers", nargs="+"); sp.add_argument("--start", default=None)
    cl = sub.add_parser("closes", help="comma-separated closes, ready for range_odds --closes")
    cl.add_argument("ticker"); cl.add_argument("--start", required=True); cl.add_argument("--end")
    br = sub.add_parser("bars", help="write the ticker,date,high,low CSV trade-check wants")
    br.add_argument("tickers", nargs="+"); br.add_argument("--start", required=True)
    br.add_argument("--out", required=True); br.add_argument("--end")
    od = sub.add_parser("odds", help="no-view odds with the spot and vol pulled from the tape")
    od.add_argument("--spot-from", required=True); od.add_argument("--lo", type=float)
    od.add_argument("--hi", type=float); od.add_argument("--days", type=int, required=True)
    a = ap.parse_args()

    try:
        if a.cmd == "spot":
            for t in a.tickers:
                s, v, n, last = spot_vol(t, a.start)
                print(f"{t:10} spot={s:12.4f}  vol={v:5.2f} %/day  ({n} closes to {last})")
        elif a.cmd == "closes":
            print(",".join(f"{v:g}" for _, v in closes(a.ticker, a.start, a.end)))
        elif a.cmd == "bars":
            n = write_bars_csv(a.tickers, a.start, pathlib.Path(a.out), a.end)
            print(f"wrote {n} bars for {len(a.tickers)} ticker(s) -> {a.out}")
        elif a.cmd == "odds":
            s, v, n, last = spot_vol(a.spot_from)
            cmd = [sys.executable, str(ROOT / "tools" / "range_odds.py"),
                   "--spot", f"{s:.4f}", "--days", str(a.days), "--vol", f"{v:.2f}"]
            if a.lo is not None:
                cmd += ["--lo", str(a.lo)]
            if a.hi is not None:
                cmd += ["--hi", str(a.hi)]
            print(f"# spot {s:.4f} and vol {v:.2f} %/day from {a.spot_from} "
                  f"({n} closes to {last}) — measured, not assumed")
            print("# " + " ".join(cmd[1:]))
            r = subprocess.run(cmd, capture_output=True, text=True,
                               encoding="utf-8", errors="replace")
            sys.stdout.write(r.stdout or r.stderr)
    except MarketDataError as e:
        print(f"MARKET DATA UNAVAILABLE: {e}", file=sys.stderr)
        print("Nothing is assumed in its place — fix the feed or price the row by hand and say so.",
              file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
