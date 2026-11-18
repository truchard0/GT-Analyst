#!/usr/bin/env python3
"""Technical stack, price layers plus options positioning context (stdlib only).

Implements the measurable layers of .claude/skills/technical-stack/SKILL.md:
  trend      close vs 20/50/200-day simple moving averages, 50/200 order
  levels     52-week high/low (closing basis), % off the high, % above the low
  relative   3-month (63 trading days) return vs SMH, ratio form: (1+r)/(1+r_SMH) - 1
  vol        realised volatility, 20d and 60d, annualised (sqrt 252), and the 20d
             reading's percentile against its own trailing year
  options    gamma regime, flip, call wall, put wall, King, expected move, next earnings,
             read from our own Skylit-derived levels file (data/ai_technical/levels_<YYYYMMDD>.csv),
             or, for SPY/QQQ/SPXW/NDXP only, from a Skylit close map in --maps-dir.
Every row carries the price date, the options snapshot time and stale flags.

It never reads a source labelled Unusual Whales (the row is blanked and flagged instead),
never prints a target, a direction call or a size. Output: data/ai_technical/stack_<YYYYMMDD>.csv

Usage:
  python tools/technical_stack.py --tickers NVDA,AVGO,ORCL,MU,TSM,META,AMZN,SMH
  python tools/technical_stack.py --tickers SPY --maps-dir "C:/.../tradingview/_skylit/close_maps"
"""
import argparse
import csv
import datetime as dt
import glob
import gzip
import json
import math
import os
import pathlib
import statistics as st
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PRICES = ROOT / "data" / "ai_prints_backtest" / "5y" / "prices_5y.csv"
OUTDIR = ROOT / "data" / "ai_technical"
BENCH = "SMH"
MAP_SYMBOLS = {"SPY", "QQQ", "SPXW", "NDXP"}
BANNED_SOURCE = ("unusual whales", "unusual_whales", "unusualwhales")

FIELDS = [
    "ticker", "as_of", "price_date", "close", "price_stale_flag", "interpolated_in_window",
    "sma20", "sma50", "sma200", "pct_vs_20d", "pct_vs_50d", "pct_vs_200d", "trend_state", "ma50_vs_ma200",
    "high_52w", "high_52w_date", "pct_off_52w_high", "low_52w", "pct_above_52w_low",
    "ret_3m_pct", "smh_ret_3m_pct", "rs_vs_smh_3m_pct",
    "rv20_ann_pct", "rv60_ann_pct", "rv20_pctile_1y", "rv_1d_move_pct",
    "opt_source", "opt_snapshot_ts", "gamma_regime", "flip", "call_wall", "put_wall", "king",
    "expected_move_pct", "next_earnings", "opt_stale_flag", "notes",
]


def weekdays_between(a, b):
    """Weekdays after a up to and including b (0 if b <= a). Holidays are not modelled."""
    n, d = 0, a
    while d < b:
        d += dt.timedelta(days=1)
        if d.weekday() < 5:
            n += 1
    return n


def load_prices(path):
    data = {}
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            try:
                c = float(r["close"])
            except (TypeError, ValueError):
                continue
            data.setdefault(r["ticker"].upper(), []).append((r["date"], c, bool((r.get("interpolated") or "").strip())))
    for t in data:
        data[t].sort()
    return data


def sma(closes, n):
    return sum(closes[-n:]) / n if len(closes) >= n else None


def pct(a, b):
    return None if a is None or b in (None, 0) else 100.0 * (a / b - 1.0)


def rv(closes, n):
    if len(closes) < n + 1:
        return None
    lr = [math.log(closes[i] / closes[i - 1]) for i in range(len(closes) - n, len(closes))]
    return st.pstdev(lr) * math.sqrt(252) * 100.0


def price_layers(series, bench, as_of):
    out = {}
    dates = [d for d, _, _ in series]
    closes = [c for _, c, _ in series]
    last_d = dt.date.fromisoformat(dates[-1])
    lag = weekdays_between(last_d, as_of)
    out["price_date"] = dates[-1]
    out["close"] = closes[-1]
    out["price_stale_flag"] = ("fresh: same-day close" if lag == 0 else
                               "fresh: T-1 close" if lag == 1 else
                               "STALE %d weekdays" % lag)
    out["interpolated_in_window"] = sum(1 for _, _, i in series[-252:] if i)
    for n in (20, 50, 200):
        m = sma(closes, n)
        out["sma%d" % n] = m
        out["pct_vs_%dd" % n] = pct(closes[-1], m)
    above = [out["pct_vs_%dd" % n] is not None and out["pct_vs_%dd" % n] > 0 for n in (20, 50, 200)]
    if out["sma200"] is None:
        out["trend_state"] = "insufficient history (<200d)"
    elif all(above):
        out["trend_state"] = "above 20/50/200"
    elif not any(above):
        out["trend_state"] = "below 20/50/200"
    else:
        out["trend_state"] = "mixed: above " + "/".join(str(n) for n, a in zip((20, 50, 200), above) if a)
    if out["sma50"] is not None and out["sma200"] is not None:
        out["ma50_vs_ma200"] = "50d above 200d" if out["sma50"] > out["sma200"] else "50d below 200d"
    win = series[-252:]
    hi = max(win, key=lambda x: x[1])
    lo = min(win, key=lambda x: x[1])
    out["high_52w"], out["high_52w_date"] = hi[1], hi[0]
    out["pct_off_52w_high"] = pct(closes[-1], hi[1])
    out["low_52w"] = lo[1]
    out["pct_above_52w_low"] = pct(closes[-1], lo[1])
    if len(closes) > 63:
        r = closes[-1] / closes[-64] - 1.0
        out["ret_3m_pct"] = 100.0 * r
        if bench:
            bmap = dict((d, c) for d, c, _ in bench)
            b1, b0 = bmap.get(dates[-1]), bmap.get(dates[-64])
            if b1 and b0:
                rb = b1 / b0 - 1.0
                out["smh_ret_3m_pct"] = 100.0 * rb
                out["rs_vs_smh_3m_pct"] = 100.0 * ((1 + r) / (1 + rb) - 1.0)
    out["rv20_ann_pct"] = rv(closes, 20)
    out["rv60_ann_pct"] = rv(closes, 60)
    if out["rv20_ann_pct"] is not None and len(closes) >= 272:
        hist = [rv(closes[: len(closes) - k], 20) for k in range(0, 252, 5)]
        hist = [h for h in hist if h is not None]
        out["rv20_pctile_1y"] = 100.0 * sum(1 for h in hist if h <= out["rv20_ann_pct"]) / len(hist)
    if out["rv20_ann_pct"] is not None:
        out["rv_1d_move_pct"] = out["rv20_ann_pct"] / math.sqrt(252)
    return out


def latest_levels_file(as_of, explicit):
    if explicit:
        return pathlib.Path(explicit) if explicit.lower() != "none" else None
    best = None
    for f in glob.glob(str(OUTDIR / "levels_*.csv")):
        stem = pathlib.Path(f).stem.split("_")[-1]
        try:
            d = dt.datetime.strptime(stem, "%Y%m%d").date()
        except ValueError:
            continue
        if d <= as_of and (best is None or d > best[0]):
            best = (d, pathlib.Path(f))
    return best[1] if best else None


def load_levels(path):
    rows = {}
    if not path or not path.exists():
        return rows
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows[r["ticker"].upper()] = r
    return rows


def opt_stale(snapshot_ts, as_of, given):
    try:
        d = dt.datetime.fromisoformat(snapshot_ts.split(" ")[0].replace("Z", "+00:00")).date()
    except (ValueError, AttributeError):
        return "UNKNOWN snapshot time" + ("; " + given if given else "")
    lag = weekdays_between(d, as_of)
    base = "fresh: same day" if lag == 0 else "fresh: T-1" if lag == 1 else "STALE %d weekdays" % lag
    return base + ("; source note: " + given if given else "")


def wall_check(row, spot):
    """Side-restriction check: call wall must sit above spot, put wall below it."""
    msgs = []
    for k, side in (("call_wall", 1), ("put_wall", -1)):
        try:
            v = float(row.get(k) or "nan")
        except (TypeError, ValueError):
            continue
        if not math.isnan(v) and spot and (v - spot) * side < 0:
            msgs.append("%s %.2f is on the wrong side of spot %.2f (not side-restricted; read as a node, not a wall)" % (k, v, spot))
    return msgs


def map_read(maps_dir, sym, as_of):
    """Latest Skylit close map on/before as_of for an index symbol. Sums the expirations the map
    carries (stated in opt_source); regime = sign of net gamma within +-2% of spot;
    walls side-restricted (call wall = max + above spot, put wall = max - below spot); King = max |value|.
    No flip: the zero-cross of strike sums is not the re-priced flip, so it is left blank."""
    files = sorted(glob.glob(os.path.join(maps_dir, "*.json.gz")))
    files = [f for f in files if os.path.basename(f)[:10] <= as_of.isoformat()]
    for f in reversed(files):
        try:
            d = json.load(gzip.open(f))
        except (OSError, ValueError):
            continue
        meta = json.dumps(d.get("body", {}).get("meta", {})).lower()
        if any(b in meta for b in BANNED_SOURCE):
            continue
        for s in d.get("body", {}).get("data", {}).get("symbols", []):
            if s.get("symbol") != sym:
                continue
            spot = s["spot"]
            ks = s["strikes"]
            near = sum(k["value"] for k in ks if abs(k["strike"] / spot - 1) <= 0.02)
            above = [k for k in ks if k["strike"] > spot and k["value"] > 0]
            below = [k for k in ks if k["strike"] < spot and k["value"] < 0]
            king = max(ks, key=lambda k: abs(k["value"]))
            exps = s.get("expirations", [])
            return {
                "opt_source": "Skylit close map %s, %d expiries %s..%s (summed), gamma" % (
                    os.path.basename(f)[:15], len(exps), exps[0] if exps else "?", exps[-1] if exps else "?"),
                "opt_snapshot_ts": s.get("asOf", ""),
                "gamma_regime": "positive" if near > 0 else "negative" if near < 0 else "flat",
                "flip": "",
                "call_wall": max(above, key=lambda k: k["value"])["strike"] if above else "",
                "put_wall": min(below, key=lambda k: k["value"])["strike"] if below else "",
                "king": "%s (%s)" % (king["strike"], "+" if king["value"] > 0 else "-"),
                "expected_move_pct": "",
                "next_earnings": "n/a",
                "spot": spot,
            }
    return None


def fmt(v):
    if v is None:
        return ""
    if isinstance(v, float):
        return "%.2f" % v
    return v


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tickers", required=True, help="comma list, e.g. NVDA,AVGO,MU,SMH")
    ap.add_argument("--date", default=dt.date.today().isoformat(), help="as-of date YYYY-MM-DD (default today)")
    ap.add_argument("--prices", default=str(PRICES))
    ap.add_argument("--levels", default="", help="levels CSV; default latest data/ai_technical/levels_<date>.csv on/before --date; 'none' to skip")
    ap.add_argument("--maps-dir", default="", help="Skylit close_maps folder (read-only) for SPY/QQQ/SPXW/NDXP")
    ap.add_argument("--out", default="", help="output CSV (default data/ai_technical/stack_<YYYYMMDD>.csv)")
    a = ap.parse_args()

    as_of = dt.date.fromisoformat(a.date)
    tickers = [t.strip().upper() for t in a.tickers.split(",") if t.strip()]
    prices = load_prices(a.prices)
    lv_path = latest_levels_file(as_of, a.levels)
    levels = load_levels(lv_path)
    bench = prices.get(BENCH)

    rows = []
    for t in tickers:
        row = {k: "" for k in FIELDS}
        row["ticker"], row["as_of"] = t, as_of.isoformat()
        notes = []
        series = prices.get(t)
        if series:
            series = [x for x in series if x[0] <= as_of.isoformat()]
        if series and len(series) >= 64:
            row.update(price_layers(series, bench, as_of))
            if t == BENCH:
                row["rs_vs_smh_3m_pct"] = 0.0
        else:
            row["price_stale_flag"] = "NO PRICE HISTORY in %s" % os.path.basename(a.prices)
            notes.append("price layers blank")

        lv = levels.get(t)
        if lv and any(b in (lv.get("source") or "").lower() for b in BANNED_SOURCE):
            notes.append("options row skipped: banned source")
            lv = None
        if lv:
            for k in ("gamma_regime", "flip", "call_wall", "put_wall", "king", "expected_move_pct", "next_earnings"):
                row[k] = lv.get(k, "")
            row["opt_source"] = "%s [%s]" % (lv.get("source", ""), lv_path.name)
            row["opt_snapshot_ts"] = lv.get("snapshot_ts", "")
            row["opt_stale_flag"] = opt_stale(row["opt_snapshot_ts"], as_of, (lv.get("stale_flag") or "").strip())
            try:
                spot = float(lv.get("spot") or "nan")
            except (TypeError, ValueError):
                spot = float("nan")
            if not math.isnan(spot):
                if row["close"] and abs(spot / row["close"] - 1) > 0.02:
                    notes.append("levels spot %.2f differs from price close %.2f by >2%%" % (spot, row["close"]))
                notes.extend(wall_check(row, spot))
        elif a.maps_dir and t in MAP_SYMBOLS:
            m = map_read(a.maps_dir, t, as_of)
            if m:
                m.pop("spot", None)
                row.update(m)
                row["opt_stale_flag"] = opt_stale(row["opt_snapshot_ts"], as_of, "gamma only, no vanna")
            else:
                row["opt_stale_flag"] = "NO MAP"
        else:
            row["opt_stale_flag"] = "NO OPTIONS DATA (no levels row%s)" % ("" if lv_path else ", no levels file")
        row["notes"] = "; ".join(notes)
        rows.append(row)

    out = pathlib.Path(a.out) if a.out else OUTDIR / ("stack_%s.csv" % as_of.strftime("%Y%m%d"))
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: fmt(r.get(k)) for k in FIELDS})

    print("technical stack as of %s | prices %s | levels %s" % (as_of, os.path.basename(a.prices), lv_path.name if lv_path else "none"))
    hdr = "%-5s %-10s %9s %7s %7s %7s %8s %8s %6s %6s  %-8s %7s %7s %7s %-9s %5s  %s"
    print(hdr % ("tkr", "px_date", "close", "vs20%", "vs50%", "vs200%", "off52H%", "RSvSMH%", "RV20", "RVpct",
                 "regime", "flip", "callW", "putW", "king", "EM%", "stale"))
    for r in rows:
        print(hdr % (r["ticker"], r["price_date"] or "-", fmt(r["close"]) or "-", fmt(r["pct_vs_20d"]) or "-",
                     fmt(r["pct_vs_50d"]) or "-", fmt(r["pct_vs_200d"]) or "-", fmt(r["pct_off_52w_high"]) or "-",
                     fmt(r["rs_vs_smh_3m_pct"]) or "-", fmt(r["rv20_ann_pct"]) or "-",
                     ("%.0f" % r["rv20_pctile_1y"]) if isinstance(r["rv20_pctile_1y"], float) else "-",
                     r["gamma_regime"] or "-", r["flip"] or "-", r["call_wall"] or "-", r["put_wall"] or "-",
                     r["king"] or "-", r["expected_move_pct"] or "-",
                     (r["price_stale_flag"] or "") + " | opt: " + (r["opt_stale_flag"] or "")))
    print("wrote", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
