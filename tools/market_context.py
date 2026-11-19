#!/usr/bin/env python3
"""Market context for the dealer-positioning report: the Trading Bot dashboard's context panels, rebuilt from OUR
data with the dashboard's own definitions, each panel carrying its measured status.

    python -I tools/market_context.py --date 2026-11-18 [--out reports/charts/20261118_positioning] [--no-charts]

What it reproduces (definitions cite Trading Bot/tradingview/algo_succession.py, read-only; the dashboard renders them
in gamma_dash_live.js:1286-1345 from the /succession/<SYM>.json endpoint, gamma_dash.py:1476-1489):
  1. today          successions, band, range, open-to-close move class, MTD pace, rolling 20d, monthly label
  2. selloff        the 14-item exhaustion checklist and the dashboard model's -5/-7/-10% "projection"
  3. expected range ATR-5/10/20/60 and the 1/2/3-sigma bands of the 20-day range %, distribution stats
  4. probability    next-day succession distribution (200-session base, shifted by VIX/RV/ATR/day-of-week/last 5)
  5. vol regime     ATR-5/ATR-20, the VIX block, net dealer gamma near the S&P (our positioning read)
  6. move dist      30-session open-to-close move classes
  7. fib            Fibonacci levels from the open and the next day's projected levels
plus market-update extras our data supports (key index levels, options-implied curve, priced move vs realised,
earnings move strip) and our own checks of each panel over 2016-2026 (no look-ahead: day i uses rows <= i only).

Inputs (read-only; any path containing whales/unusual/cards is refused by market_update.data.check_path):
  Trading Bot/tradingview/_skylit/succession/daily_SPX.csv, daily_VIX.csv   Yahoo daily OHLC cache written by
      algo_succession.daily() (algo_succession.py:56-84); we never refresh it from here
  Trading Bot/tradingview/_skylit/vol/daily/<date>.json + vol/history_*.json  Skylit options-implied vol, 1-day move
  Trading Bot/tradingview/_skylit/moves/<session>.json                         earnings list with past report-day moves
  GT data/ai_technical/gamma_weeks_<date>.json                                  our net dealer gamma read (overnight map)
Writes data/ai_technical/market_context_<date>.json and house-style charts c1-c4. Descriptive only: no targets,
entries, stops or sizes; price direction is a no-call.
"""
import argparse
import datetime as dt
import json
import math
import pathlib
import statistics as st
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from market_update import data as D  # noqa: E402
from market_update import stats as S  # noqa: E402
from market_update import chartstyle as cs  # noqa: E402

import numpy as np  # noqa: E402

ALGO = "Trading Bot/tradingview/algo_succession.py"
SUCC_DIR = D.SKYLIT / "succession"
FIB = (0.114, 0.236, 0.382, 0.500, 0.618, 0.786, 0.886, 1.000, 1.132, 1.272)          # algo_succession.py:38
STOP = 0.70711                                                                           # algo_succession.py:39
BANDS = ["no algo-succession", "average", "above average", "high volatility", "selloff territory",
         "crisis / black swan"]                                                          # algo_succession.py:40
ROLES = {0.114: "trigger", 0.236: "trigger", 0.382: "trigger", 0.500: "trigger", 0.618: "golden reversal",
         0.786: "pullback", 0.886: "pullback", 1.000: "measured move", 1.132: "measured move",
         1.272: "measured move"}                                                         # algo_succession.py:41-42
MONTH_BEAR = 20                                                                          # algo_succession.py:43
EXT_ORDER = ["extreme extension", "extension", "OP trend", "0.114 trend"]
EXT_LABEL = {"extreme extension": "extreme extension (|move| >= 0.618%)",
             "extension": "extension (0.382-0.618%)",
             "OP trend": "OP trend (0.114-0.382%)",
             "0.114 trend": "inside (under 0.114%)"}

DEFS = {
    "data": ALGO + ":56-84 (Yahoo ^GSPC / ^VIX daily since 2016, cached in _skylit/succession/daily_*.csv)",
    "successions": ALGO + ":87-90 (range % = (high - low) / prior close x 100; 0 below 0.60%, else 1 + floor((range - 0.60) / 0.50))",
    "table": ALGO + ":104-116 (range, return vs prior close, move = close vs open, true range)",
    "move_class": ALGO + ":110-111 (|close/open - 1|: >= 0.618 extreme extension, >= 0.382 extension, >= 0.114 OP trend, else '0.114 trend' = inside)",
    "monthly": ALGO + ":121-126 and :395-399 (BEAR if month successions > 20, or pace x 21 > 20 once 3+ days; MoM vs prior month avg +-10%)",
    "exhaustion": ALGO + ":219-264 (11 price factors + 3 VIX factors; LOW < 4, MODERATE < 7, ELEVATED < 10, else HIGH; ELEVATED projects -5 to -7%, HIGH -7 to -10%, 20-25 trading days, validation = the day's high)",
    "expected_range": ALGO + ":267-286 (ATR-n = mean true range of n sessions; high/low = close +- ATR/2; k-sigma bands of the 20-day range %, ddof 0; day-of-week averages)",
    "vol_regime": ALGO + ":289-293 (ATR-5 / ATR-20: > 1.30 expanding, < 0.70 contracting)",
    "vix_block": ALGO + ":296-312 (close, change, 5-day change, 5/20/60-day means, 20-day range, 1-year percentile; <15 low, <20 normal, <30 elevated, else fear)",
    "probability": ALGO + ":315-364 (200-session base of 0/1/2/3+; score from VIX level, VIX 5d, VIX - RV20, ATR5/ATR20, next day-of-week, last 5 days; each +0.5 moves 5 points from the low bins to the high bins, capped +-20)",
    "fib": ALGO + ":13-15, :137-141, :385-388, :401-403 (level = open x (1 +- fib/100); stop +-0.7071%; next day uses the close as the estimated open)",
    "dist30": ALGO + ":408 (move classes of the last 30 sessions)",
    "dashboard": "Trading Bot/tradingview/gamma_dash_live.js:1286-1345 (render); gamma_dash.py:1476-1489 (endpoint)",
}
RECORD_SRC = {
    "report_B_D_E": "Trading Bot/tradingview/_research/succession_20261108/REPORT.md (sections B, D, E)",
    "report2": "Trading Bot/tradingview/_research/succession_20261108/REPORT2.md",
    "registry": "Trading Bot/knowledge/TEST_REGISTRY.jsonl:43 (ALGO-SUCCESSION-STATIC)",
    "trend_day": "Trading Bot/knowledge/RULES_REGISTRY.md:212 (trend-day predictors, AUC 0.44-0.61, 881 sessions)",
    "gt_record": "research_notes/gamma_maps/B_measured_record.md:87, :198",
}


# ---------------------------------------------------------------- data
def load_daily(sym, upto):
    p = D.check_path(SUCC_DIR / ("daily_%s.csv" % sym))
    rows = []
    with open(p, encoding="utf-8") as f:
        next(f)
        for line in f:
            d, o, h, lo, c = line.strip().split(",")
            if d <= upto:
                rows.append((d, float(o), float(h), float(lo), float(c)))
    return rows, str(p)


def succ_of(r):                                                  # algo_succession.py:87-90
    if r is None or not math.isfinite(r) or r < 0.60:
        return 0
    return 1 + int(math.floor((r - 0.60) / 0.50))


def ext_of(m):                                                   # algo_succession.py:110-111
    a = abs(m)
    return "extreme extension" if a >= 0.618 else "extension" if a >= 0.382 else "OP trend" if a >= 0.114 else "0.114 trend"


def build_table(rows):
    """algo_succession.table(): the first row (no prior close) is dropped, as in the original (:116)."""
    T = {k: [] for k in ("date", "open", "high", "low", "close", "prev", "range_pct", "range_pts", "succ", "ret",
                         "move", "ext", "tr", "month", "dow")}
    for (d0, o0, h0, l0, c0), (d, o, h, lo, c) in zip(rows, rows[1:]):
        rp = (h - lo) / c0 * 100
        T["date"].append(d)
        T["open"].append(o)
        T["high"].append(h)
        T["low"].append(lo)
        T["close"].append(c)
        T["prev"].append(c0)
        T["range_pct"].append(rp)
        T["range_pts"].append(h - lo)
        T["succ"].append(succ_of(rp))
        T["ret"].append((c / c0 - 1) * 100)
        T["move"].append((c / o - 1) * 100)
        T["ext"].append(ext_of((c / o - 1) * 100))
        T["tr"].append(max(h - lo, abs(h - c0), abs(lo - c0)))
        T["month"].append(d[:7])
        T["dow"].append(dt.date.fromisoformat(d).strftime("%a"))
    for k in T:
        T[k] = np.asarray(T[k]) if k not in ("date", "ext", "month", "dow") else np.asarray(T[k], dtype=object)
    n = len(T["date"])
    ms = np.zeros(n, int)
    for i in range(1, n):
        ms[i] = ms[i - 1] if T["month"][i] == T["month"][i - 1] else i
    T["month_start"] = ms
    T["n"] = n
    return T


def vix_series(vrows, dates):
    """VIX fields aligned to the SPX dates (algo_succession.vix_block, :296-312, evaluated as of each date)."""
    vd = [r[0] for r in vrows]
    vc = np.asarray([r[4] for r in vrows])
    pos = {d: i for i, d in enumerate(vd)}
    out = []
    for d in dates:
        j = pos.get(d)
        if j is None or j < 60:
            out.append(None)
            continue
        c = float(vc[j])
        prev = float(vc[j - 1])
        w20 = vc[j - 19:j + 1]
        m5, m20, m60 = float(vc[j - 4:j + 1].mean()), float(w20.mean()), float(vc[j - 59:j + 1].mean())
        out.append(dict(day=d, close=round(c, 2), chg=round(c - prev, 2), chg_pct=round((c / prev - 1) * 100, 1),
                        chg5=round(c - float(vc[j - 5]), 2), m5=round(m5, 2), m20=round(m20, 2), m60=round(m60, 2),
                        lo20=round(float(w20.min()), 2), hi20=round(float(w20.max()), 2),
                        regime="LOW" if c < 15 else "NORMAL" if c < 20 else "ELEVATED" if c < 30 else "FEAR",
                        trend="RISING" if m5 > m20 * 1.03 else "FALLING" if m5 < m20 * 0.97 else "FLAT",
                        pct_rank_1y=round(float((vc[max(0, j - 251):j + 1] <= c).mean()) * 100, 0)))
    return out


def next_trading_day(d):                                         # algo_succession.py:212-216 (weekends only)
    x = dt.date.fromisoformat(d) + dt.timedelta(days=1)
    while x.weekday() >= 5:
        x += dt.timedelta(days=1)
    return x


# ---------------------------------------------------------------- the dashboard's pieces
def exhaustion(T, i, vix):                                       # algo_succession.py:219-264
    s, ext, ret, close = T["succ"], T["ext"], T["ret"], T["close"]
    a20, a5 = max(0, i - 19), max(0, i - 4)
    w20, w5, p15 = s[a20:i + 1], s[a5:i + 1], s[a20:a5]
    roll20 = int(w20.sum())
    avg = roll20 / max(1, len(w20))
    if len(p15) and p15.mean() > 0:
        acc = w5.mean() / p15.mean()
    else:
        acc = math.inf if w5.mean() > 0 else 1.0
    nosucc5 = int((w5 == 0).sum())
    e20 = ext[a20:i + 1]
    ext_share = float(np.isin(e20, ["extension", "extreme extension"]).mean()) * 100
    maxdrop = float(ret[a20:i + 1].min())
    week = int(w5.sum())
    big3 = int((w20 >= 3).sum())
    big5 = int((w20 >= 5).sum())
    m0 = T["month_start"][i]
    pace = s[m0:i + 1].sum() / max(1, i + 1 - m0) * 21
    sma20 = float(close[a20:i + 1].mean())
    c = float(close[i])
    F = [("rolling 20d > 30", roll20 > 30, "%d" % roll20),
         ("avg / day > 1.5", avg > 1.5, "%.2f" % avg),
         ("5d acceleration > 1.2x", acc > 1.2, ("%.2fx" % acc) if math.isfinite(acc) else "inf"),
         ("sudden no-succession day (5d) with 20d > 25", nosucc5 >= 1 and roll20 > 25, "%d / %d" % (nosucc5, roll20)),
         ("extensions >= 40% of the 20d moves", ext_share >= 40, "%.0f%%" % ext_share),
         ("max daily drop (20d) <= -1.5%", maxdrop <= -1.5, "%+.2f%%" % maxdrop),
         ("weekly successions (5d) > 10", week > 10, "%d" % week),
         ("3+ succession days (20d) >= 3", big3 >= 3, "%d" % big3),
         ("a 5+ (crisis) day in the 20d", big5 >= 1, "%d" % big5),
         ("month pace > 20 / month", pace > 20, "%.0f" % pace),
         ("close below the 20d mean", c < sma20, "%.0f vs %.0f" % (c, sma20))]
    if vix is not None:
        F += [("VIX > 20", vix["close"] > 20, "%.2f" % vix["close"]),
              ("VIX up over 5d", (vix["chg5"] or 0) > 0, "%+.2f" % (vix["chg5"] or 0)),
              ("VIX above its 20d mean", vix["close"] > (vix["m20"] or 0), "%.1f vs %.1f" % (vix["close"], vix["m20"]))]
    n = sum(1 for _, ok, _ in F if ok)
    risk = "LOW" if n < 4 else "MODERATE" if n < 7 else "ELEVATED" if n < 10 else "HIGH"
    proj = None
    if risk in ("ELEVATED", "HIGH"):
        lo, hi = (5, 7) if risk == "ELEVATED" else (7, 10)
        proj = dict(pct=[-lo, -hi], bottom_zone=[round(c * (1 - hi / 100), 2), round(c * (1 - lo / 100), 2)],
                    days="20-25 trading days", validation=round(float(T["high"][i]), 2),
                    note="invalidated on a close above the validation level; fulfilled when price reaches the bottom zone")
    return dict(rolling20=roll20, avg_day=round(avg, 2), accel5=round(acc, 2) if math.isfinite(acc) else None,
                nosucc5=nosucc5, ext_share=round(ext_share), max_drop=round(maxdrop, 2), week5=week, risk=risk, n=n,
                of=len(F), factors=[dict(name=a, on=bool(b), value=v) for a, b, v in F], projected=proj)


def atr(T, i, n):
    return float(T["tr"][max(0, i - n + 1):i + 1].mean())


def expected_range(T, i):                                        # algo_succession.py:267-286
    c = float(T["close"][i])
    out = {}
    for n in (5, 10, 20, 60):
        a = atr(T, i, n)
        out["atr%d" % n] = dict(pts=round(a, 2), pct=round(a / c * 100, 3), high=round(c + a / 2, 2),
                                low=round(c - a / 2, 2))
    w = T["range_pct"][max(0, i - 19):i + 1]
    mu, sd = float(w.mean()), float(w.std())
    bands = []
    for k in (1, 2, 3):
        lo, hi = max(0.0, mu - k * sd), mu + k * sd
        share = float(((w >= lo) & (w <= hi)).mean()) * 100
        bands.append(dict(k=k, lo=round(lo, 3), hi=round(hi, 3), share_in_window=round(share),
                          high=round(c * (1 + hi / 200), 2), low=round(c * (1 - hi / 200), 2)))
    nd = next_trading_day(T["date"][i])
    dow = nd.strftime("%a")
    sel = T["dow"][:i + 1] == dow                                  # history up to day i only (no look-ahead)
    return dict(next_day=nd.isoformat(), dow=dow, close=round(c, 2), atr=out, expected=out["atr5"], bands=bands,
                stats=dict(mean=round(mu, 3), median=round(float(np.median(w)), 3), std=round(sd, 3),
                           p25=round(float(np.quantile(w, 0.25)), 3), p75=round(float(np.quantile(w, 0.75)), 3)),
                dow_avg_range=round(float(T["range_pct"][:i + 1][sel].mean()), 3),
                dow_avg_succ=round(float(T["succ"][:i + 1][sel].mean()), 2), dow_n=int(sel.sum()))


def vol_ratio(T, i):                                             # algo_succession.py:289-293
    a5, a20 = atr(T, i, 5), atr(T, i, 20)
    r = a5 / a20 if a20 else None
    return r, (None if r is None else "EXPANDING" if r > 1.30 else "CONTRACTING" if r < 0.70 else "NORMAL")


def probability(T, i, vix, dow_cache=None):                      # algo_succession.py:315-364
    s = T["succ"]
    hist = s[max(0, i - 199):i + 1]
    allh = s[:i + 1]

    def rates(x):
        return [round(float((x == 0).mean()) * 100), round(float((x == 1).mean()) * 100),
                round(float((x == 2).mean()) * 100), round(float((x >= 3).mean()) * 100)], len(x)
    base, n200 = rates(hist)
    allr, nall = rates(allh)
    score, factors = 0.0, []
    if vix:
        c = vix["close"]
        sc = 1 if c >= 25 else 0.5 if c >= 20 else -0.5 if c < 14 else 0
        score += sc
        factors.append(dict(name="VIX level", value="%.2f (%s, %.0fth pct 1y)" % (c, vix["regime"].lower(), vix["pct_rank_1y"]), s=sc))
        m = vix["chg5"] or 0
        sc = 0.5 if m > 1 else -0.5 if m < -1 else 0
        score += sc
        factors.append(dict(name="VIX momentum (5d)", value="%+.2f" % m, s=sc))
        rv = float(T["ret"][max(0, i - 19):i + 1].std()) * math.sqrt(252)
        gap = c - rv
        sc = -0.5 if gap > 5 else 0.5 if gap < -3 else 0
        score += sc
        factors.append(dict(name="implied vs realized (20d)", value="VIX %.1f vs RV %.1f (%+.1f: %s)" % (
            c, rv, gap, "IV rich" if gap > 0 else "IV cheap"), s=sc, rv20=round(rv, 2)))
    vr = vol_ratio(T, i)[0] or 1.0
    sc = 0.5 if vr > 1.15 else -0.5 if vr < 0.85 else 0
    score += sc
    factors.append(dict(name="realized compression (ATR5 / ATR20)", value="%.2fx" % vr, s=sc))
    dow = next_trading_day(T["date"][i]).strftime("%a")
    sel = T["dow"][:i + 1] == dow
    da = float(allh[sel].mean())
    am = float(allh.mean())
    sc = 0.5 if da > am * 1.08 else -0.5 if da < am * 0.92 else 0
    score += sc
    factors.append(dict(name="day of week (%s)" % dow, value="%.2f succ / day vs %.2f all" % (da, am), s=sc))
    w5 = float(s[max(0, i - 4):i + 1].mean())
    sc = 0.5 if w5 >= 2 else -0.5 if w5 < 0.8 else 0
    score += sc
    factors.append(dict(name="last 5 days", value="%.2f succ / day" % w5, s=sc))
    p = [float(x) for x in base]
    shift = max(-20.0, min(20.0, score * 10))
    take = shift / 2
    p = [max(0.0, p[0] - take * 0.4), max(0.0, p[1] - take * 0.6), p[2] + take * 0.6, p[3] + take * 0.4]
    tot = sum(p) or 1
    p = [x / tot * 100 for x in p]
    exp = p[1] / 100 + p[2] / 100 * 2 + p[3] / 100 * 3.3
    base_exp = base[1] / 100 + base[2] / 100 * 2 + base[3] / 100 * 3.3
    lab = "HIGHER" if score >= 1 else "LOWER" if score <= -1 else "NEUTRAL"
    return dict(label=lab, score=round(score, 2), expected=round(exp, 1), base_expected=round(base_exp, 1),
                adjusted=[round(x) for x in p], adjusted_raw=p, base200=base, n200=n200, base_all=allr, n_all=nall,
                factors=factors)


def fib_levels(op):                                              # algo_succession.py:137-141
    lv = [(f, round(op * (1 + f / 100), 2), round(op * (1 - f / 100), 2), ROLES[f]) for f in FIB]
    return lv, (round(op * (1 + STOP / 100), 2), round(op * (1 - STOP / 100), 2))


def monthly(T, upto_i):
    out = {}
    for k in range(upto_i + 1):
        m = T["month"][k]
        o = out.setdefault(m, dict(month=m, days=0, succ=0, ret=0.0))
        o["days"] += 1
        o["succ"] += int(T["succ"][k])
        o["ret"] += float(T["ret"][k])
    rows = list(out.values())
    for r in rows:
        r["avg"] = r["succ"] / r["days"]
        r["signal"] = "BEAR" if r["succ"] > MONTH_BEAR else "BULL"
    return rows


# ---------------------------------------------------------------- our checks of each panel (2016-2026)
def records(T, VX):
    n = T["n"]
    s, c, h, lo, rp = T["succ"], T["close"], T["high"], T["low"], T["range_pct"]
    R = {}

    # 1. succession clustering: today's successions -> next day
    groups = {"0": [], "1": [], "2": [], "3+": []}
    for i in range(n - 1):
        groups["3+" if s[i] >= 3 else str(int(s[i]))].append(i)
    R["clustering"] = {k: dict(days=len(v), p_next_ge2=round(float(np.mean([s[i + 1] >= 2 for i in v])) * 100),
                               next_range_median=round(float(np.median([rp[i + 1] for i in v])), 3))
                       for k, v in groups.items()}
    R["clustering"]["all"] = dict(days=n - 1, p_next_ge2=round(float((s[1:] >= 2).mean()) * 100),
                                  next_range_median=round(float(np.median(rp[1:])), 3))

    # 2. selloff checklist (14 factors with VIX) -> next 25 sessions; and the projection as stated
    H = 25
    buckets = {}
    proj_tests = {"HIGH (-7%)": [], "ELEVATED (-5%)": []}
    base_proj = {7: [], 5: []}
    high_days = []
    for i in range(60, n - H):
        v = VX[i]
        if v is None:
            continue
        ex = exhaustion(T, i, v)
        fwd_lo = float(lo[i + 1:i + H + 1].min()) / c[i] - 1
        r25 = c[i + H] / c[i] - 1
        buckets.setdefault(ex["risk"], []).append((fwd_lo, r25))
        buckets.setdefault("all", []).append((fwd_lo, r25))

        def path(pct):
            zone = c[i] * (1 - pct / 100)
            for j in range(i + 1, i + H + 1):
                if lo[j] <= zone:
                    return "fulfilled"
                if c[j] > h[i]:
                    return "invalidated"
            return "neither"
        for pct in (7, 5):
            base_proj[pct].append(path(pct))
        if ex["risk"] == "HIGH":
            proj_tests["HIGH (-7%)"].append(path(7))
            high_days.append(i)
        elif ex["risk"] == "ELEVATED":
            proj_tests["ELEVATED (-5%)"].append(path(5))

    def summ(v):
        a = np.asarray(v)
        return dict(days=len(v), worst25_median_pct=round(float(np.median(a[:, 0])) * 100, 2),
                    p_worst_le_5=round(float((a[:, 0] <= -0.05).mean()) * 100),
                    p_worst_le_7=round(float((a[:, 0] <= -0.07).mean()) * 100),
                    p_worst_le_10=round(float((a[:, 0] <= -0.10).mean()) * 100),
                    ret25_mean_pct=round(float(a[:, 1].mean()) * 100, 2),
                    p_ret25_up=round(float((a[:, 1] > 0).mean()) * 100))

    def ptally(v):
        return dict(n=len(v), fulfilled=round(100 * v.count("fulfilled") / max(1, len(v))),
                    invalidated_first=round(100 * v.count("invalidated") / max(1, len(v))),
                    neither=round(100 * v.count("neither") / max(1, len(v))))
    eps = []
    for i in high_days:
        if not eps or i - eps[-1][-1] > H:
            eps.append([i])
        else:
            eps[-1].append(i)
    ep_hit = sum(1 for e in eps if float(lo[e[0] + 1:e[0] + H + 1].min()) / c[e[0]] - 1 <= -0.07)
    R["selloff"] = dict(
        window="%s to %s (days with 25 sessions after them)" % (T["date"][60], T["date"][n - H - 1]),
        by_risk={k: summ(v) for k, v in sorted(buckets.items())},
        projection={k: ptally(v) for k, v in proj_tests.items()},
        projection_base_all_days={"-7%": ptally(base_proj[7]), "-5%": ptally(base_proj[5])},
        high_episodes=dict(n=len(eps), reached_minus7_within_25=ep_hit,
                           first_days=[T["date"][e[0]] for e in eps]),
        note="Overlapping 25-session windows; HIGH days cluster in episodes, so the episode count is the honest n.")

    # 3. expected range: ATR-5 at day i vs day i+1; sigma bands out of sample
    ratio, inside_band, close_in, x, y = [], [], [], [], []
    cover = {1: [], 2: [], 3: []}
    for i in range(60, n - 1):
        a5 = atr(T, i, 5)
        nr = h[i + 1] - lo[i + 1]
        ratio.append(nr / a5)
        x.append(a5 / c[i] * 100)
        y.append(rp[i + 1])
        inside_band.append(h[i + 1] <= c[i] + a5 / 2 and lo[i + 1] >= c[i] - a5 / 2)
        close_in.append(abs(c[i + 1] - c[i]) <= a5 / 2)
        w = rp[i - 19:i + 1]
        mu, sd = w.mean(), w.std()
        for k in (1, 2, 3):
            cover[k].append(max(0, mu - k * sd) <= rp[i + 1] <= mu + k * sd)
    R["expected_range"] = dict(
        n=len(ratio), window="%s to %s" % (T["date"][61], T["date"][n - 1]),
        next_range_over_atr5_median=round(float(np.median(ratio)), 2),
        p_next_range_le_atr5=round(float((np.asarray(ratio) <= 1).mean()) * 100),
        corr_atr5pct_vs_next_range=round(float(np.corrcoef(x, y)[0, 1]), 2),
        p_whole_next_day_inside_close_pm_half_atr5=round(float(np.mean(inside_band)) * 100),
        p_next_close_inside_close_pm_half_atr5=round(float(np.mean(close_in)) * 100),
        sigma_band_coverage_next_day={str(k): round(float(np.mean(v)) * 100) for k, v in cover.items()},
        normal_reference={"1": 68, "2": 95, "3": 99.7})

    # 4. probability: adjusted vs 200-session base vs all-history base (multi-class Brier, next day's bin)
    b_adj, b_base, b_all, lab = [], [], [], {"HIGHER": [], "NEUTRAL": [], "LOWER": []}
    for i in range(200, n - 1):
        v = VX[i]
        if v is None:
            continue
        pr = probability(T, i, v)
        k = min(int(s[i + 1]), 3)
        o = [0, 0, 0, 0]
        o[k] = 1

        def brier(p):
            return sum((p[j] / 100 - o[j]) ** 2 for j in range(4))
        b_adj.append(brier(pr["adjusted_raw"]))
        b_base.append(brier(pr["base200"]))
        b_all.append(brier(pr["base_all"]))
        lab[pr["label"]].append(int(s[i + 1]))
    d = np.asarray(b_adj) - np.asarray(b_base)
    se = float(d.std(ddof=1) / math.sqrt(len(d)))
    R["probability"] = dict(
        n=len(b_adj), brier_adjusted=round(float(np.mean(b_adj)), 4), brier_base200=round(float(np.mean(b_base)), 4),
        brier_base_all=round(float(np.mean(b_all)), 4), adj_minus_base200=round(float(d.mean()), 4),
        adj_minus_base200_se=round(se, 4),
        skill_vs_base200_pct=round((1 - float(np.mean(b_adj)) / float(np.mean(b_base))) * 100, 1),
        by_label={k: dict(days=len(v), next_succ_mean=round(float(np.mean(v)), 2) if v else None,
                          p_next_ge2=round(float(np.mean([x >= 2 for x in v])) * 100) if v else None)
                  for k, v in lab.items()},
        note="The rule's weights were set by hand (no fitting), so 2016-2026 is a fair test of the fixed rule; overlapping days, simple standard error.")

    # 5. vol regime -> next day
    reg = {"EXPANDING": [], "NORMAL": [], "CONTRACTING": []}
    for i in range(60, n - 1):
        reg[vol_ratio(T, i)[1]].append(i)
    R["vol_regime"] = {k: dict(days=len(v), next_range_median=round(float(np.median([rp[i + 1] for i in v])), 3) if v else None,
                               p_next_ge2=round(float(np.mean([s[i + 1] >= 2 for i in v])) * 100) if v else None)
                       for k, v in reg.items()}

    # 6. monthly label -> next month (complete months only)
    mon = monthly(T, n - 1)
    cur = T["month"][n - 1]
    pairs = [(a, b) for a, b in zip(mon, mon[1:]) if b["month"] != cur]
    R["monthly"] = {}
    for sig in ("BULL", "BEAR"):
        pp = [b for a, b in pairs if a["signal"] == sig]
        R["monthly"][sig] = dict(months=len(pp), next_ret_mean_pct=round(float(np.mean([b["ret"] for b in pp])), 2),
                                 next_green=round(float(np.mean([b["ret"] > 0 for b in pp])) * 100),
                                 next_succ_mean=round(float(np.mean([b["succ"] for b in pp])), 1))
    # 7. move classes: full-history shares (for the 30-session comparison)
    R["move_classes_all"] = {k: round(float((T["ext"] == k).mean()) * 100, 1) for k in EXT_ORDER}
    R["move_classes_n"] = n
    yr = T["date"][n - 1][:4]
    sel = np.asarray([d[:4] == yr for d in T["date"]])
    R["move_classes_ytd"] = {k: round(float((T["ext"][sel] == k).mean()) * 100, 1) for k in EXT_ORDER}
    R["move_classes_ytd_n"] = int(sel.sum())
    return R


# ---------------------------------------------------------------- extras from our other data
def extras(T, i, date):
    c = T["close"]
    X = {}
    lv = {}
    for k in (20, 50, 200):
        m = float(c[i - k + 1:i + 1].mean())
        lv["sma%d" % k] = dict(level=round(m, 2), close_vs_pct=round((c[i] / m - 1) * 100, 2))
    hi52 = float(T["high"][max(0, i - 251):i + 1].max())
    lo52 = float(T["low"][max(0, i - 251):i + 1].min())
    j_hi = int(np.argmax(T["high"][max(0, i - 251):i + 1])) + max(0, i - 251)
    lv["high_52w"] = dict(level=round(hi52, 2), date=T["date"][j_hi], close_vs_pct=round((c[i] / hi52 - 1) * 100, 2))
    lv["low_52w"] = dict(level=round(lo52, 2), close_vs_pct=round((c[i] / lo52 - 1) * 100, 2))
    X["key_levels"] = lv

    v = D.load_vol_daily(date)
    prevd = T["date"][i - 1]
    vp = D.load_vol_daily(prevd)
    if v:
        curve = {}
        for sym in ("SPXW", "QQQ"):
            q = v["symbols"].get(sym)
            if q:
                curve[sym] = dict(svx1d_adj=q["svx1d_adj"], svx9=q["svx9"], svx30=q["svx30"], svx3m=q["svx3m"],
                                  svx6m=q["svx6m"], atm_iv_front=round(q["atm_iv_front"] * 100, 2),
                                  atm_iv_30=round(q["atm_iv_30"] * 100, 2), term_slope=q["term_slope"],
                                  rr25_30=q["rr25_30"], skew_s30=q["skew_s30"], close=q["close"])
        q = v["symbols"]["SPXW"]
        X["implied_curve"] = dict(file=v["path"], published=v["published"].isoformat() if v["published"] else None,
                                  curves=curve,
                                  note="svx = Skylit VIX-style implied vol at 1 day (event-adjusted), 9 days, 30 days, 3 and 6 months")
        X["priced_move_next"] = dict(for_session=next_trading_day(date).isoformat(), em_pts=q["em_1d"],
                                     em_pct=q["em_1d_pct"], low=q["range_1d_low"], high=q["range_1d_high"],
                                     close=q["close"], file=v["path"])
    if vp and v:
        qp = vp["symbols"]["SPXW"]
        mv = (v["symbols"]["SPXW"]["close"] / qp["close"] - 1) * 100
        X["priced_vs_realised_today"] = dict(session=date, priced_pct=qp["em_1d_pct"], priced_pts=qp["em_1d"],
                                             realised_pct=round(mv, 3), inside=abs(mv) <= qp["em_1d_pct"],
                                             file=vp["path"])
    rows = D.load_vol_history("SPXW")
    svx30 = v["symbols"]["SPXW"]["svx30"] if v else None
    rr = S.route_rates(rows, today_svx30=svx30)
    X["priced_move_record"] = dict(all=rr["all"], cond=rr.get("cond"), cond_band=rr.get("cond_band"),
                                   k_em_over_svx1d=rr["k"],
                                   source="Skylit vol/history_* + vol/daily/* via tools/market_update/stats.route_rates")
    last20 = []
    tail = [r for r in rows if r[0] <= date][-21:]
    for (d1, c1, _, s1, e1), (d2, c2, _, _, _) in zip(tail, tail[1:]):
        em = e1 if e1 else (rr["k"] * s1 if s1 else None)
        if em:
            last20.append(abs(c2 / c1 - 1) * 100 <= em)
    X["priced_move_last20"] = dict(n=len(last20), inside=int(sum(last20)))

    sess = next_trading_day(date).isoformat()
    E = D.load_earnings(sess)
    strip = []
    for r in E.get("rows", []):
        past = [x for x in (r.get("typical") or []) if x is not None]
        strip.append(dict(sym=r["sym"], name=r.get("name", ""), when=r.get("when"), report_day=r.get("report_day"),
                          past_moves=past, past_median=round(st.median(past), 1) if past else None,
                          gap_chance=r.get("est")))
    X["earnings"] = dict(session=sess, file=E.get("path"), rows=strip, base=E.get("base"),
                         implied="none of these names is in the Skylit vol file, so no implied move is shown",
                         base_rate="across 2,901 earnings events the median realised gap was 0.61x the implied move and 27% went beyond it (gamma-maps skill, section 3 step 7)")
    X["skipped"] = [
        "Market breadth (advance/decline, % above averages): no breadth series in our data.",
        "Dollar, 10y/30y yields, metals panels: no DXY, yield or metal price series wired (FRED folder holds events only).",
        "Index vanna and charm by strike, dealer net contracts: not in our Skylit maps.",
        "Overnight night-turn clock: 55 nights of ES/NQ bars, far short of the years it needs.",
        "VIX bracket to index range past cases: not built yet; would need n stated per bracket.",
    ]
    return X


# ---------------------------------------------------------------- snapshot
def snapshot(date):
    rows, spx_path = load_daily("SPX", date)
    vrows, vix_path = load_daily("VIX", date)
    T = build_table(rows)
    i = T["n"] - 1
    if T["date"][i] != date:
        raise SystemExit("no SPX row for %s (latest %s)" % (date, T["date"][i]))
    VX = vix_series(vrows, list(T["date"]))
    vix = VX[i]
    mon = monthly(T, i)
    cur, prev = mon[-1], (mon[-2] if len(mon) > 1 else None)
    monthly_sig = "BEAR" if cur["succ"] > MONTH_BEAR or (cur["days"] >= 3 and cur["avg"] * 21 > MONTH_BEAR) else "BULL"
    mom = ("INCREASING" if prev and cur["avg"] > prev["avg"] * 1.1 else
           "DECREASING" if prev and cur["avg"] < prev["avg"] * 0.9 else "FLAT")
    ex = exhaustion(T, i, vix)
    lv, stop = fib_levels(float(T["open"][i]))
    hits_up = [bool(T["high"][i] >= r) for _, r, _, _ in lv]
    hits_dn = [bool(T["low"][i] <= s_) for _, _, s_, _ in lv]
    nlv, nstop = fib_levels(float(T["close"][i]))
    reg_r, reg_lab = vol_ratio(T, i)
    pr = probability(T, i, vix)
    pr.pop("adjusted_raw")
    d30 = {k: int((T["ext"][max(0, i - 29):i + 1] == k).sum()) for k in EXT_ORDER}
    wk = {}
    for k in range(max(0, i - 24 * 5), i + 1):
        y, w, _ = dt.date.fromisoformat(T["date"][k]).isocalendar()
        wk.setdefault("%d-W%02d" % (y, w), 0)
        wk["%d-W%02d" % (y, w)] += int(T["succ"][k])
    gw_path = ROOT / "data" / "ai_technical" / ("gamma_weeks_%s.json" % date.replace("-", ""))
    gamma = None
    if gw_path.exists():
        g = json.load(open(gw_path, encoding="utf-8"))["reads"].get("SPXW")
        if g:
            gamma = dict(regime=g["regime_now"], net_pm2_pct=round(g["net_pm2_now_pct"], 1),
                         regime_after_roll=g["regime_after_roll"], net_pm2_after_roll_pct=round(g["net_pm2_after_roll_pct"], 1),
                         roll=g["roll"], snapshot=g["snapshot"], file=str(gw_path.relative_to(ROOT)).replace("\\", "/"))
    snap = dict(
        date=date,
        today=dict(open=round(T["open"][i], 2), high=round(T["high"][i], 2), low=round(T["low"][i], 2),
                   close=round(T["close"][i], 2), prev_close=round(T["prev"][i], 2), ret_pct=round(T["ret"][i], 2),
                   move_pct=round(T["move"][i], 3), range_pts=round(T["range_pts"][i], 2),
                   range_pct=round(T["range_pct"][i], 3), succ=int(T["succ"][i]), band=BANDS[min(int(T["succ"][i]), 5)],
                   ext=T["ext"][i], mtd_succ=cur["succ"], mtd_days=cur["days"], mtd_avg=round(cur["avg"], 2),
                   rolling20=ex["rolling20"], avg_day=ex["avg_day"],
                   nosucc20=int((T["succ"][max(0, i - 19):i + 1] == 0).sum())),
        signal=dict(monthly=monthly_sig, label="BEARISH / VOL" if monthly_sig == "BEAR" else "BULLISH",
                    month=cur["month"], month_succ=cur["succ"], month_days=cur["days"],
                    month_pace=round(cur["avg"] * 21, 1), prev_month=prev["month"] if prev else None,
                    prev_succ=prev["succ"] if prev else None, prev_days=prev["days"] if prev else None,
                    prev_avg=round(prev["avg"], 2) if prev else None, mom=mom),
        exhaustion=ex, expected=expected_range(T, i), probability=pr,
        regime=dict(ratio=round(reg_r, 3), regime=reg_lab, atr5=round(atr(T, i, 5), 2), atr20=round(atr(T, i, 20), 2)),
        vix=vix, dealer_gamma=gamma,
        fib=dict(op=round(T["open"][i], 2), high=round(T["high"][i], 2), low=round(T["low"][i], 2), stop=stop,
                 levels=[dict(f=f, r=r, s=s_, role=ro, hit_r=hu, hit_s=hd) for (f, r, s_, ro), hu, hd in zip(lv, hits_up, hits_dn)],
                 hits_up=sum(hits_up), hits_dn=sum(hits_dn)),
        fib_next=dict(day=next_trading_day(date).isoformat(), est_op=round(T["close"][i], 2), stop=nstop,
                      levels=[dict(f=f, r=r, s=s_, role=ro) for f, r, s_, ro in nlv]),
        dist30=d30,
        weeks=[dict(week=k, succ=v) for k, v in list(wk.items())[-26:]],
        daily60=[dict(d=T["date"][k], s=int(T["succ"][k]), r=round(float(T["ret"][k]), 2),
                      roll20=int(T["succ"][max(0, k - 19):k + 1].sum())) for k in range(max(0, i - 59), i + 1)],
        vix120=[dict(d=vrows[k][0], c=vrows[k][4]) for k in range(max(0, len(vrows) - 120), len(vrows))],
    )
    return T, VX, snap, dict(spx=spx_path, vix=vix_path)


STATUS = {
    "today": ("descriptive; volatility persistence validated, direction failed",
              "The count is arithmetic on the day's range. Big-range days are followed by big-range days (2016-2026); "
              "the monthly BEARISH / VOL label does not predict lower returns, and as a filter for the prior day it failed."),
    "selloff": ("failed (as a selloff forecast)",
                "HIGH readings raise the odds of a 5% drawdown but the average 25-session return after them is positive: "
                "volatility, not direction (TEST_REGISTRY ALGO-SUCCESSION-STATIC). The -7% to -10% projection is the dashboard model's claim, not ours."),
    "expected_range": ("validated as a size gauge; not as levels",
                       "ATR-5 tracks the next day's range; the close +- ATR/2 'high/low' does not contain the next day's whole range most of the time."),
    "probability": ("untested before today; our first check below",
                    "Base rates are descriptive; the hand-set adjustment is scored against the 200-session base."),
    "vol_regime": ("descriptive; ATR ratio checked below; gamma-volatility link a lead",
                   "Literature supports a small damping effect of dealer long gamma on index volatility; our intraday tests are inconsistent across books."),
    "move_distribution": ("descriptive (no forecast claim)", "Counts of what happened; trend-day predictors failed out of sample (AUC 0.44-0.61, 881 sessions)."),
    "fib": ("failed", "Levels from the open held 51% of 793 touches vs 55% at shuffled non-Fibonacci distances (139 days of SPY 1-minute bars)."),
}


# ---------------------------------------------------------------- charts
P = cs.P


def _day(d):
    return dt.date.fromisoformat(d).strftime("%d %b %Y").lstrip("0")


def chart_range(snap, X, R, out, src):
    c = snap["today"]["close"]
    e = snap["expected"]
    a5 = e["expected"]
    pm = X.get("priced_move_next")
    fn = snap["fib_next"]
    nd = _day(fn["day"])
    title = "%s: ATR-5 expects a %.0f-point range (%.2f%%); options price a %.0f-point move" % (
        dt.date.fromisoformat(fn["day"]).strftime("%A"), a5["pts"], a5["pct"], pm["em_pts"])
    sub = ("S&P 500 around the %s close of %s. Each column is one model's band for %s (Fibonacci uses the close as the open).\n"
           "In 2016-2026 the next day's range was %.2fx ATR-5 at the median; the whole next day stayed "
           "inside close ± ATR/2 on %d%% of days." % (
               _day(snap["date"]), cs.fmt_level(c), nd, R["expected_range"]["next_range_over_atr5_median"],
               R["expected_range"]["p_whole_next_day_inside_close_pm_half_atr5"]))
    call = ("Our record: Fibonacci levels from the open failed (held 51% of 793 touches vs 55% at shuffled distances). "
            "These are model bands, not targets or stops.")
    fig, rects = cs.frame(title, sub, panels=1, tags=[("RANGE MODELS AND LEVELS", "white")], callout=call,
                          footer_right=src, snapshot="Skylit implied-vol file, %s close" % _day(snap["date"]))
    ax = cs.panel_axes(fig, rects[0], pad=(1.25, 0.35, 0.35, 0.75))
    b3 = e["bands"][2]
    lo_y = min(b3["low"], pm["low"], fn["levels"][-1]["s"]) - 18
    hi_y = max(b3["high"], pm["high"], fn["levels"][-1]["r"]) + 18
    ax.set_ylim(lo_y, hi_y)
    ax.set_xlim(0, 10)
    cols = [(0.3, 2.1, "20-DAY RANGE BANDS"), (2.5, 4.1, "ATR-5 / 20"), (4.5, 6.1, "OPTIONS-PRICED"),
            (6.6, 9.9, "FIBONACCI FROM THE CLOSE")]
    for x0, x1, lab in cols:
        ax.text((x0 + x1) / 2, hi_y - 4, lab, ha="center", va="top", fontsize=cs.SIZES["small"], color=P["subtitle"],
                fontweight="bold")
    # sigma bands of the range, centred on the close (the dashboard draws high/low = close x (1 +- hi/200))
    shades = [P["free"], "#1c1c1c", "#262626"]
    for k, b in zip((3, 2, 1), (e["bands"][2], e["bands"][1], e["bands"][0])):
        ax.add_patch(cs.plt.Rectangle((0.3, b["low"]), 1.8, b["high"] - b["low"], facecolor=shades[k - 1],
                                      edgecolor=P["border"], lw=0.8, zorder=1))
        ax.text(0.38, b["high"] - 2, "%dσ  %s" % (k, cs.fmt_level(b["high"], 0)), fontsize=cs.SIZES["tiny"],
                color=P["text"], va="top", family=cs.MONO, zorder=3)
        ax.text(0.38, b["low"] + 2, "%dσ  %s" % (k, cs.fmt_level(b["low"], 0)), fontsize=cs.SIZES["tiny"], color=P["text"],
                va="bottom", family=cs.MONO, zorder=3)
    # ATR-5 and ATR-20
    a20 = e["atr"]["atr20"]
    ax.add_patch(cs.plt.Rectangle((2.5, a20["low"]), 1.6, a20["high"] - a20["low"], facecolor="none",
                                  edgecolor=P["subtitle"], lw=1.2, ls=(0, (3, 2)), zorder=2))
    ax.add_patch(cs.plt.Rectangle((2.65, a5["low"]), 1.3, a5["high"] - a5["low"], facecolor=P["slow_light"],
                                  edgecolor=P["green"], lw=1.5, zorder=2))
    ax.text(3.3, a5["high"] + 3, "ATR-5  %s" % cs.fmt_level(a5["high"], 0), ha="center", va="bottom",
            fontsize=cs.SIZES["tiny"], color=P["green"], family=cs.MONO)
    ax.text(3.3, a5["low"] - 3, cs.fmt_level(a5["low"], 0), ha="center", va="top", fontsize=cs.SIZES["tiny"],
            color=P["green"], family=cs.MONO)
    ax.text(3.3, lo_y + 6, "dashed: ATR-20\n%s–%s" % (cs.fmt_level(a20["low"], 0), cs.fmt_level(a20["high"], 0)),
            ha="center", va="bottom", fontsize=cs.SIZES["tiny"], color=P["subtitle"], family=cs.MONO, linespacing=1.3)
    # options-priced 1-day move (Skylit vol)
    ax.add_patch(cs.plt.Rectangle((4.6, pm["low"]), 1.4, pm["high"] - pm["low"], facecolor="#2a1a06",
                                  edgecolor=P["orange"], lw=1.5, zorder=2))
    ax.text(5.3, pm["high"] + 3, "%s" % cs.fmt_level(pm["high"], 0), ha="center", va="bottom",
            fontsize=cs.SIZES["tiny"], color=P["orange"], family=cs.MONO)
    ax.text(5.3, pm["low"] - 3, "%s" % cs.fmt_level(pm["low"], 0), ha="center", va="top",
            fontsize=cs.SIZES["tiny"], color=P["orange"], family=cs.MONO)
    ax.text(5.3, (pm["high"] + c) / 2 + 6, "±%.2f%%" % pm["em_pct"], ha="center", va="center",
            fontsize=cs.SIZES["small"], color=P["orange"], fontweight="bold")
    # fib levels from the close
    for L in fn["levels"]:
        for y, side in ((L["r"], "+"), (L["s"], "−")):
            golden = L["f"] == 0.618
            col = P["yellow"] if golden else P["purple"]
            ax.plot([6.7, 7.9], [y, y], color=col, lw=1.6 if golden else 1.0, zorder=2)
    # labels on the right, spread
    labs = []
    for L in fn["levels"]:
        labs.append((L["r"], "+%.3f%%  %s  %s" % (L["f"], cs.fmt_level(L["r"], 0), L["role"]), L["f"]))
        labs.append((L["s"], "−%.3f%%  %s  %s" % (L["f"], cs.fmt_level(L["s"], 0), L["role"]), L["f"]))
    labs.append((fn["stop"][0], "+0.707%%  %s  dashboard 'stop'" % cs.fmt_level(fn["stop"][0], 0), 0.707))
    labs.append((fn["stop"][1], "−0.707%%  %s  dashboard 'stop'" % cs.fmt_level(fn["stop"][1], 0), 0.707))
    for y in fn["stop"]:
        ax.plot([6.7, 7.9], [y, y], color=P["red"], lw=1.0, ls=(0, (3, 2)), zorder=2)
    span = hi_y - lo_y
    ys = cs.spread_labels([l[0] for l in labs], span * 0.026)
    for (y0, txt, f), y in zip(labs, ys):
        col = P["yellow"] if f == 0.618 else P["red"] if f == 0.707 else P["purple"]
        ax.plot([7.9, 8.05], [y0, y], color=col, lw=0.6, zorder=2)
        ax.text(8.08, y, txt, fontsize=cs.SIZES["tiny"] - 1, color=col, va="center", ha="left", family=cs.MONO)
    # the close
    ax.axhline(c, color=P["white"], lw=1.2, ls=(0, (5, 3)), zorder=4, xmin=0.02, xmax=0.79)
    ax.text(-0.05, c, "close %s" % cs.fmt_level(c), ha="right", va="center", fontsize=cs.SIZES["small"],
            color=P["white"], fontweight="bold", family=cs.MONO)
    ax.set_xticks([])
    ax.set_yticks([])
    p = out / "c1_range_ladder.png"
    cs.save(fig, p)
    return p


def chart_selloff(snap, R, out, src):
    ex = snap["exhaustion"]
    sel = R["selloff"]
    hi, al = sel["by_risk"].get("HIGH"), sel["by_risk"]["all"]
    pj, pjb = sel["projection"]["HIGH (-7%)"], sel["projection_base_all_days"]["-7%"]
    title = "Selloff checklist: %d of %d; after past %s readings a 7%% drop followed only %d%% of the time" % (
        ex["n"], ex["of"], ex["risk"], pj["fulfilled"]) if ex["risk"] == "HIGH" else \
        "The selloff checklist reads %d of %d (%s)" % (ex["n"], ex["of"], ex["risk"])
    sub = ("S&P 500 successions per session (range bands of 0.5%% above 0.60%%) and the dashboard's 14-item checklist at the %s close. "
           "After HIGH readings (%d days, %d episodes) the 25-session low reached −7%% before a close above that day's high %d%% of the time, "
           "vs %d%% on all days; the average 25-session return was %+.1f%% vs %+.1f%%." % (
               _day(snap["date"]), hi["days"], sel["high_episodes"]["n"], pj["fulfilled"], pjb["fulfilled"],
               hi["ret25_mean_pct"], al["ret25_mean_pct"]))
    call = "Our record: the checklist flags volatility, not direction. Its −7% to −10% 'projection' is the dashboard model's claim; on our data it failed."
    fig, rects = cs.frame(title, sub, panels=2, panel_widths=[1.25, 1],
                          tags=[("SUCCESSIONS, LAST 60 SESSIONS", "purple"), ("SELLOFF CHECKLIST", "yellow")],
                          callout=call, footer_right=src)
    ax = cs.panel_axes(fig, rects[0], pad=(0.75, 0.6, 0.75, 0.85))
    d60 = snap["daily60"]
    xs = np.arange(len(d60))
    colmap = {0: P["muted"], 1: P["green"], 2: P["yellow"], 3: P["orange"]}
    cols = [colmap.get(r["s"], P["red"]) for r in d60]
    ax.bar(xs, [r["s"] for r in d60], color=cols, width=0.72, zorder=2)
    ax.set_ylim(0, max(6, max(r["s"] for r in d60) + 1))
    ax.set_ylabel("successions per session", color=P["subtitle"], fontsize=cs.SIZES["small"])
    ax.set_xlim(-1, len(d60))
    ticks = [0, len(d60) // 2, len(d60) - 1]
    ax.set_xticks(ticks)
    ax.set_xticklabels([dt.date.fromisoformat(d60[k]["d"]).strftime("%d %b").lstrip("0") for k in ticks])
    ax.axhline(0, color=P["zero"], lw=1)
    ax2 = ax.twinx()
    ax2.plot(xs, [r["roll20"] for r in d60], color=P["purple"], lw=2.2, zorder=3)
    ax2.axhline(30, color=P["purple"], lw=1, ls=(0, (4, 3)), alpha=0.7)
    ax2.set_ylim(0, max(45, max(r["roll20"] for r in d60) + 5))
    for sp in ax2.spines.values():
        sp.set_visible(False)
    ax2.tick_params(length=0, colors=P["purple"])
    ax2.text(0, 30.8, "checklist bar: 30", color=P["purple"], fontsize=cs.SIZES["tiny"], ha="left", va="bottom")
    last = d60[-1]
    ax2.annotate("rolling 20d: %d" % last["roll20"], (xs[-1], last["roll20"]), xytext=(-130, 0), textcoords="offset points",
                 ha="right", va="center", color=P["purple"], fontsize=cs.SIZES["small"], fontweight="bold",
                 arrowprops=dict(arrowstyle="-", color=P["purple"], lw=0.8))
    cs.legend_row(ax, [("line", P["muted"], "0"), ("line", P["green"], "1"), ("line", P["yellow"], "2"),
                       ("line", P["orange"], "3"), ("line", P["red"], "4+ per session"),
                       ("line", P["purple"], "rolling 20-day sum")],
                  y=1.04, x0=0.0, size=cs.SIZES["tiny"])
    # checklist
    x, y, w, h = rects[1]
    fw, fh = fig.get_size_inches()
    top = y + h - 0.75 / fh
    step = (h - 0.95 / fh) / len(ex["factors"])
    for k, f in enumerate(ex["factors"]):
        yy = top - k * step
        col = P["orange"] if f["on"] else P["muted"]
        fig.text(x + 0.22 / fw, yy, "■" if f["on"] else "□", color=col, fontsize=cs.SIZES["small"], va="top")
        fig.text(x + 0.48 / fw, yy, f["name"], color=P["text"] if f["on"] else P["muted"], fontsize=cs.SIZES["tiny"] + 0.5, va="top")
        fig.text(x + w - 0.2 / fw, yy, f["value"], color=col, fontsize=cs.SIZES["tiny"] + 0.5, va="top", ha="right",
                 family=cs.MONO)
    p = out / "c2_selloff_checklist.png"
    cs.save(fig, p)
    return p


def chart_vol(snap, X, R, out, src, snapshot):
    v = snap["vix"]
    reg = snap["regime"]
    g = snap["dealer_gamma"]
    cur = X["implied_curve"]["curves"]
    q = cur.get("QQQ")
    title = "VIX closed at %.2f, higher than %.0f%% of the past year; the S&P curve is flat, the Nasdaq's inverted" % (
        v["close"], v["pct_rank_1y"])
    if q:
        title = title.rstrip(".") + " (%.0f vs %.0f)" % (q["svx1d_adj"], q["svx6m"])
    sub = ("VIX %+.2f on the day, %+.2f over 5 sessions, 20-day mean %.2f, 20-day range %.2f-%.2f. ATR-5/ATR-20 = %.2f (%s; "
           "expanding above 1.30). Dealer gamma near the S&P: %s, %+.1f%% of the map within ±2%%." % (
               v["chg"], v["chg5"], v["m20"], v["lo20"], v["hi20"], reg["ratio"], reg["regime"].lower(),
               g["regime"] if g else "n/a", g["net_pm2_pct"] if g else float("nan")))
    rg = R["vol_regime"]
    call = ("Our record: next-day range median %.2f%% after EXPANDING ratios vs %.2f%% after NORMAL (2016-2026). "
            "Dealer gamma's effect on volatility is small in the literature and inconsistent in our tests." % (
                rg["EXPANDING"]["next_range_median"], rg["NORMAL"]["next_range_median"]))
    fig, rects = cs.frame(title, sub, panels=2, panel_widths=[1.35, 1],
                          tags=[("VIX, LAST 120 SESSIONS", "orange"), ("IMPLIED VOL BY HORIZON", "orange")],
                          callout=call, footer_right=src, snapshot=snapshot)
    ax = cs.panel_axes(fig, rects[0], pad=(0.75, 0.6, 0.55, 0.85))
    vv = snap["vix120"]
    ys = np.asarray([r["c"] for r in vv])
    xs = np.arange(len(ys))
    m20 = np.asarray([ys[max(0, k - 19):k + 1].mean() for k in range(len(ys))])
    ax.plot(xs, m20, color=P["muted"], lw=1.4, zorder=2)
    ax.plot(xs, ys, color=P["orange"], lw=2.2, zorder=3)
    for lvl, lab in ((20, "20 elevated"), (30, "30 fear")):
        ax.axhline(lvl, color=P["zero"], lw=1, ls=(0, (4, 3)))
        ax.text(-0.5, lvl + 0.25, lab, color=P["subtitle"], fontsize=cs.SIZES["tiny"], va="bottom", bbox=dict(facecolor=P["panel"], edgecolor="none", pad=1), zorder=5)
    ax.set_ylim(max(0, ys.min() - 3), max(32, ys.max() + 3))
    ax.set_xlim(-1, len(ys) + 12)
    ticks = [0, len(ys) // 2, len(ys) - 1]
    ax.set_xticks(ticks)
    ax.set_xticklabels([dt.date.fromisoformat(vv[k]["d"]).strftime("%d %b").lstrip("0") for k in ticks])
    ax.plot([xs[-1]], [ys[-1]], "o", ms=9, color=P["yellow"], zorder=6, markeredgewidth=0)
    ax.annotate("%.2f" % ys[-1], (xs[-1], ys[-1]), xytext=(10, 0), textcoords="offset points", ha="left", va="center", fontsize=cs.SIZES["label"], fontweight="bold", color=P["orange"], zorder=7)
    j = int(np.argmax(ys))
    ax.annotate("high %.2f" % ys[j], (xs[j], ys[j]), xytext=(0, 8), textcoords="offset points", ha="center",
                color=P["subtitle"], fontsize=cs.SIZES["tiny"])
    cs.legend_row(ax, [("line", P["orange"], "VIX close"), ("line", P["muted"], "20-day mean")], y=1.04,
                  size=cs.SIZES["tiny"])
    ax2 = cs.panel_axes(fig, rects[1], pad=(0.75, 0.6, 0.35, 0.85))
    labels = ["1 day", "9 days", "30 days", "3 months", "6 months"]
    keys = ["svx1d_adj", "svx9", "svx30", "svx3m", "svx6m"]
    for sym, col, lab in (("SPXW", P["orange"], "S&P 500"), ("QQQ", P["purple"], "Nasdaq-100 (QQQ)")):
        if sym not in cur:
            continue
        vals = [cur[sym][k] for k in keys]
        ax2.plot(range(5), vals, color=col, lw=2.2, marker="o", ms=7, zorder=3)
        for k in (0, 4):
            ax2.annotate("%.1f" % vals[k], (k, vals[k]), xytext=(0, 9 if sym == "QQQ" else -18), textcoords="offset points", ha="center",
                         color=col, fontsize=cs.SIZES["tiny"], family=cs.MONO)
    ax2.axhline(v["close"], color=P["white"], lw=1, ls=(0, (2, 3)))
    ax2.text(4.2, v["close"], "VIX %.2f" % v["close"], color=P["white"], fontsize=cs.SIZES["tiny"], va="center", ha="right",
             bbox=dict(facecolor=P["panel"], edgecolor="none", pad=1))
    ax2.set_xticks(range(5))
    ax2.set_xticklabels(labels, fontsize=cs.SIZES["tiny"])
    allv = [cur[s][k] for s in cur for k in keys]
    ax2.set_ylim(min(allv) - 4, max(allv) + 5)
    ax2.set_xlim(-0.4, 4.4)
    cs.legend_row(ax2, [("line", P["orange"], "S&P 500"), ("line", P["purple"], "Nasdaq-100 (QQQ)")], y=1.04,
                  size=cs.SIZES["tiny"])
    p = out / "c3_vol_regime.png"
    cs.save(fig, p)
    return p


def chart_moves(snap, R, out, src):
    d30 = snap["dist30"]
    allp = R["move_classes_all"]
    n30 = sum(d30.values())
    big = d30["extreme extension"]
    ytd = R["move_classes_ytd"]
    title = "%d of the last 30 sessions moved 0.618%% or more open to close (%.0f%%), vs %.0f%% since 2016 and %.0f%% this year" % (
        big, big / n30 * 100, allp["extreme extension"], ytd["extreme extension"])
    sub = ("S&P 500 open-to-close move classes, 30 sessions to %s vs all %s sessions since Jan 2016. "
           "Last 30: %s. Only %d inside days, vs about %.0f expected at the long-run rate." % (
               _day(snap["date"]), "{:,}".format(R["move_classes_n"]),
               ", ".join("%d %s" % (d30[k], k if k != "0.114 trend" else "inside") for k in EXT_ORDER),
               d30["0.114 trend"], allp["0.114 trend"] * 0.3))
    call = "Our record: these are counts of what happened. No signal tested so far predicts a trend day (AUC 0.44-0.61, 881 sessions)."
    fig, rects = cs.frame(title, sub, panels=1, tags=[("MOVE DISTRIBUTION, CLOSE VS OPEN", "white")], callout=call,
                          footer_right=src)
    ax = cs.panel_axes(fig, rects[0], pad=(3.7, 0.5, 1.2, 0.95))
    ys = np.arange(len(EXT_ORDER))[::-1]
    share30 = [d30[k] / n30 * 100 for k in EXT_ORDER]
    shareall = [allp[k] for k in EXT_ORDER]
    ax.barh(ys + 0.18, share30, height=0.34, color=P["orange"], zorder=2)
    ax.barh(ys - 0.18, shareall, height=0.34, color=P["zero"], zorder=2)
    for y, a, b, k in zip(ys, share30, shareall, EXT_ORDER):
        ax.text(a + 0.8, y + 0.18, "%d of 30  (%.0f%%)" % (d30[k], a), va="center", fontsize=cs.SIZES["small"],
                color=P["text"], family=cs.MONO)
        ax.text(b + 0.8, y - 0.18, "%.1f%% since 2016" % b, va="center", fontsize=cs.SIZES["tiny"],
                color=P["subtitle"], family=cs.MONO)
        ax.text(-1.2, y, EXT_LABEL[k], ha="right", va="center", fontsize=cs.SIZES["small"], color=P["text"])
    ax.set_xlim(0, max(share30 + shareall) * 1.3)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.axvline(0, color=P["zero"], lw=1)
    cs.legend_row(ax, [("line", P["orange"], "last 30 sessions"), ("line", P["zero"], "Jan 2016 to date")],
                  y=1.06, size=cs.SIZES["tiny"])
    p = out / "c4_move_distribution.png"
    cs.save(fig, p)
    return p


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--date", required=True, help="completed session YYYY-MM-DD")
    ap.add_argument("--out", default=None, help="chart folder (default reports/charts/<date>_positioning)")
    ap.add_argument("--no-charts", action="store_true")
    a = ap.parse_args()
    date = a.date
    T, VX, snap, paths = snapshot(date)
    R = records(T, VX)
    i = T["n"] - 1
    X = extras(T, i, date)
    out = pathlib.Path(a.out) if a.out else ROOT / "reports" / "charts" / ("%s_positioning" % date.replace("-", ""))
    out.mkdir(parents=True, exist_ok=True)
    doc = dict(
        date=date, built=dt.datetime.now().isoformat(timespec="seconds"),
        session_note="Latest completed session; the Yahoo cache (daily_SPX.csv / daily_VIX.csv) was written after the close.",
        sources=dict(spx_daily=paths["spx"], vix_daily=paths["vix"], vol_daily=X.get("implied_curve", {}).get("file"),
                     earnings=X["earnings"]["file"], dealer_gamma=(snap["dealer_gamma"] or {}).get("file")),
        definitions=DEFS, record_sources=RECORD_SRC,
        status={k: dict(status=v[0], why=v[1]) for k, v in STATUS.items()},
        panels={k: snap[k] for k in ("today", "signal", "exhaustion", "expected", "probability", "regime", "vix",
                                     "dealer_gamma", "dist30", "fib", "fib_next", "weeks")},
        records=R, extras=X,
        differences_from_dashboard=[
            "Day-of-week and all-history averages use sessions up to the date only (the dashboard uses the whole cached table; identical for the latest day).",
            "The dashboard's 4-states block is not reproduced: its vanna sign is unaudited and the family tested null; our positioning read covers gamma.",
        ],
        rules="Descriptive only. No targets, entries, stops or sizes; price direction is a no-call.")
    jp = ROOT / "data" / "ai_technical" / ("market_context_%s.json" % date)
    with open(jp, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, default=str)
    print("wrote", jp)
    if not a.no_charts:
        cs.apply("dark")
        dd = date
        src_spx = "Yahoo daily via Trading Bot _skylit/succession/daily_SPX.csv, to %s" % dd
        print(chart_range(snap, X, R, out, "daily_SPX.csv (Yahoo) + Skylit vol/daily/%s.json, %s close" % (dd, dd)))
        print(chart_selloff(snap, R, out, "daily_SPX.csv + daily_VIX.csv (Yahoo), 2016 to %s" % dd))
        g = snap["dealer_gamma"]
        print(chart_vol(snap, X, R, out, "daily_VIX.csv; vol/daily/%s.json; gamma_weeks_%s.json" % (
            dd, dd.replace("-", "")), "%s, 13:00 PT close" % _day(dd) if g and "16:00" in str(g.get("snapshot")) else ("%s, 14:30 PT" % _day(dd) if g else "")))
        print(chart_moves(snap, R, out, src_spx))
    t, ex, e, pr = snap["today"], snap["exhaustion"], snap["expected"], snap["probability"]
    print("today", json.dumps(t))
    print("signal", json.dumps(snap["signal"]))
    print("exhaustion", ex["risk"], ex["n"], ex["of"], json.dumps(ex["projected"]))
    for f in ex["factors"]:
        print("   ", f["on"], f["name"], f["value"])
    print("expected", json.dumps({k: e[k] for k in ("next_day", "dow", "atr", "bands", "stats", "dow_avg_range", "dow_avg_succ", "dow_n")}))
    print("prob", json.dumps({k: pr[k] for k in pr if k != "factors"}))
    for f in pr["factors"]:
        print("   ", f)
    print("regime", snap["regime"], "vix", snap["vix"])
    print("gamma", snap["dealer_gamma"])
    print("dist30", snap["dist30"])
    print("fib", snap["fib"]["hits_up"], snap["fib"]["hits_dn"], snap["fib"]["stop"])
    print("records", json.dumps(R, indent=0)[:6000])
    print("extras", json.dumps({k: v for k, v in X.items() if k != "earnings"}, default=str)[:3000])
    print("earnings", json.dumps(X["earnings"], default=str)[:2500])


if __name__ == "__main__":
    main()
