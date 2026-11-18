"""Positioning picture from the Trading Bot's cached files (no API calls, no credits):
A. Skylit index vol curves 10/23 vs their own history (vol/history_* + vol/daily/*)
B. Tempest 500-name screener by sector (term structure, IV percentile, skew)
C. Alpaca 154-name skew recorder by sector"""
import csv
import glob
import json
import os
import statistics as st
from collections import defaultdict

SK = r"C:\Users\hudso\Downloads\Trading Bot\tradingview\_skylit"


def pct_rank(series, v):
    xs = [x for x in series if x is not None]
    return 100.0 * sum(1 for x in xs if x <= v) / len(xs) if xs else float("nan")


# ---------- A. index vol curves
hist = defaultdict(lambda: defaultdict(list))   # sym -> col -> [(date, v)]
for f in sorted(glob.glob(os.path.join(SK, "vol", "history_*.json"))) + sorted(glob.glob(os.path.join(SK, "vol", "daily", "*.json"))):
    d = json.load(open(f))
    for s in d["data"]["symbols"]:
        for col, vals in s["columns"].items():
            for dt_, v in zip(s["dates"], vals):
                hist[s["symbol"]][col].append((dt_, v))
cols = ["svx9", "svx30", "svx3m", "svx6m", "term_slope", "rr25_30", "skew_s30", "atm_iv_30", "close"]
print("A. INDEX VOL CURVES (Skylit svx = VIX-style index on each book; pct = percentile vs history since 2023-03)")
for sym in ["SPXW", "NDXP", "SPY", "QQQ", "GLD", "NVDA", "MSFT", "META", "AAPL", "TSLA"]:
    if sym not in hist:
        continue
    out = []
    for c in ["svx9", "svx30", "svx3m", "svx6m", "term_slope", "rr25_30"]:
        ser = sorted(set(hist[sym][c]))
        if not ser:
            continue
        last_d, last = ser[-1]
        if last is None:
            continue
        one_y = [v for d_, v in ser if d_ >= "2025-10-23"]
        m1 = [v for d_, v in ser if d_ <= "2026-09-23"]
        prev = m1[-1] if m1 else None
        out.append(f"{c} {last:.2f} (1y pct {pct_rank(one_y, last):.0f}; 9/23 {prev if prev is None else round(prev, 2)})")
    print(f"  {sym} {last_d}: " + " | ".join(out))
# daily files only (Oct): svx30 vs svx3m path for SPXW and NDXP
for sym in ["SPXW", "NDXP"]:
    ser30 = dict(hist[sym]["svx30"]); ser3m = dict(hist[sym]["svx3m"]); ser6m = dict(hist[sym]["svx6m"])
    ds = [d_ for d_ in sorted(ser30) if d_ >= "2026-08-25"]
    print(f"  {sym} curve path (30d / 3m / 6m): " + "; ".join(f"{d_[5:]} {ser30[d_]:.1f}/{ser3m.get(d_) or float('nan'):.1f}/{ser6m.get(d_) or float('nan'):.1f}" for d_ in ds[::3] + ds[-1:]))
    # how often since 2023 has svx3m > svx30 AND svx6m > svx3m (upward curve) while svx30 >= 18?
    allds = sorted(set(ser30) & set(ser3m) & set(ser6m))
    up = [d_ for d_ in allds if ser30[d_] and ser3m[d_] and ser6m[d_] and ser6m[d_] > ser3m[d_] > ser30[d_]]
    print(f"    days with 6m > 3m > 30d: {len(up)} of {len(allds)} ({100*len(up)/max(1,len(allds)):.0f}%)")

# ---------- B. Tempest screener by sector
print("\nB. TEMPEST 500-NAME SCREENER BY SECTOR (10/23 close vs 10/21)")
for day in ["2026-10-21", "2026-10-23"]:
    rows = json.load(open(os.path.join(SK, "universe", "tempest", f"{day}_daily.json")))["data"]["rows"]
    by = defaultdict(list)
    for r in rows:
        by[r.get("sector") or "?"].append(r)
    print(f"  {day}: n={len(rows)}; backwardation {sum(r.get('curve') == 'backwardation' for r in rows)} "
          f"({100*sum(r.get('curve') == 'backwardation' for r in rows)/len(rows):.0f}%); median iv_pct {st.median([r['iv_pct'] for r in rows if r.get('iv_pct') is not None]):.0f}")
    if day != "2026-10-23":
        continue
    print(f"    {'sector':22s} {'n':>3s} {'backw%':>6s} {'ivpct':>5s} {'svx30':>6s} {'skew_pct_1y':>11s} {'rr25':>6s} {'earn<21d%':>9s}")
    for sec, rs in sorted(by.items(), key=lambda kv: -len(kv[1])):
        def med(k):
            xs = [r[k] for r in rs if r.get(k) is not None]
            return st.median(xs) if xs else float("nan")
        bw = 100 * sum(r.get("curve") == "backwardation" for r in rs) / len(rs)
        er = 100 * sum(bool(r.get("earnings_within_21")) for r in rs) / len(rs)
        print(f"    {sec:22s} {len(rs):3d} {bw:6.0f} {med('iv_pct'):5.0f} {med('svx30'):6.1f} {med('skew_pct_1y'):11.0f} {med('rr25_30'):6.1f} {er:9.0f}")
    hot = sorted([r for r in rows if r.get("iv_pct") is not None and r.get("opt_vol", 0) > 20000], key=lambda r: -r["iv_pct"])[:12]
    print("    high-IV liquid names: " + ", ".join(f"{r['ticker']}({r.get('sector')},{r['iv_pct']:.0f},{r.get('curve')})" for r in hot))

# ---------- C. Alpaca skew recorder by sector
print("\nC. ALPACA SKEW RECORDER (154 names, 11/20 monthly; skew = (p25-c25)/atm) BY SECTOR, 10/23")
rows = list(csv.DictReader(open(os.path.join(SK, "skew", "2026-10-23.csv"))))
by = defaultdict(list)
for r in rows:
    by[r["sector"]].append(r)


def f(r, k):
    try:
        return float(r[k])
    except (TypeError, ValueError):
        return None


print(f"    {'sector':24s} {'n':>3s} {'atmIV':>6s} {'skew':>6s} {'P/C OI':>6s} {'r1m%':>6s} {'r1w%':>6s}")
for sec, rs in sorted(by.items(), key=lambda kv: st.median([f(r, 'r1m') for r in kv[1] if f(r, 'r1m') is not None] or [0])):
    def med(k):
        xs = [f(r, k) for r in rs if f(r, k) is not None]
        return st.median(xs) if xs else float("nan")
    print(f"    {sec:24s} {len(rs):3d} {med('m_atm')*100:6.1f} {med('m_skew'):6.2f} {med('m_pc_oi'):6.2f} {med('r1m')*100:6.1f} {med('r1w')*100:6.1f}")
pilot = json.load(open(os.path.join(SK, "skew", "hist_pilot.json")))["names"]
for nm in ["SPY", "QQQ", "SMH", "XLE", "GLD", "TLT", "IWM", "XLF"]:
    if nm in pilot and pilot[nm].get("series"):
        ser = pilot[nm]["series"]; ks = sorted(ser)
        print(f"  {nm} 11/20 skew path: " + ", ".join(f"{k[5:]} {ser[k]:.2f}" for k in ks[::3] + ks[-1:]))
