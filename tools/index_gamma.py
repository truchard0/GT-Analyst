#!/usr/bin/env python3
"""Index dealer-gamma read for one session close: SPXW (S&P 0DTE book), SPY, QQQ and SMH, from our Skylit maps.

    GT_SKYLIT_ROOT=<mirror> python -I tools/index_gamma.py --date 2026-11-19 \
        [--roll 2026-11-20] [--out reports/charts/20261119_index_gamma]

Follows the gamma-maps skill read procedure (section 3): staleness, regime near the price, concentration by expiry,
geography, dynamics (09:30 -> 12:00 -> 16:00 ET), vanna (SMH only: the universe eod_vanna batch), cross-checks.

Inputs (read-only mirror of Trading Bot/tradingview/_skylit; any whales/unusual/cards path is refused by data.py):
  live/<date>/{0930,1200,1600}_heatmap.json.gz   per-minute index maps (5 expiries each)
  live/<date>/*_levels.json.gz                   half-hourly level files (only their spot is used, for the path)
  universe/<date>/eod_*_SMH / eod_vanna_*        SMH end-of-day gamma and vanna maps (20 expiries)
  vol/daily/<date>.json (falls back a day)       front ATM implied vol and the priced 1-day move
  GT data/ai_prints_backtest/5y/prices_5y.csv    SMH closes (20-day realised vol: SMH is not in the vol file)

Our computations:
  regime     net gamma within +-2% of spot as a share of the map's total |gamma| inside +-5% (flat under 3%)
  flip       total gamma re-priced at 161 candidate spots within +-4% (flat-vol Black-Scholes: each cell's value is
             scaled by phi(d1(S)) S / (phi(d1(S0)) S0); cells with |d1(S0)| > 4 are held constant), the zero
             crossing nearest spot. An approximation on the vendor's values, not a Skylit output.
  after roll the same reads with every expiry up to --roll removed (what is left after Friday's monthly expiry)
  centre     |gamma|-weighted mean strike inside +-5% (used to say whether the map moved with price)
Writes data/ai_technical/index_gamma_<date>.json and four house-style charts. Descriptive only: no targets,
entries, stops, sizes or direction.
"""
import argparse
import csv
import datetime as dt
import gzip
import json
import math
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import market_update  # noqa: E402,F401  (adds the user site-packages back for numpy under python -I)
import numpy as np  # noqa: E402
from market_update import chartstyle as cs  # noqa: E402
from market_update import data as D  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

P = cs.P
MONO = cs.MONO
BOOKS = ["SPXW", "SPY", "QQQ", "SMH"]
NAME = {"SPXW": "S&P 500 0DTE book (SPXW)", "SPY": "SPY", "QQQ": "QQQ", "SMH": "Chip ETF (SMH)"}
SHORT = {"SPXW": "SPXW", "SPY": "SPY", "QQQ": "QQQ", "SMH": "SMH"}
WIN = 0.05
NEAR = 0.02
PT_OFF = 3   # ET -> PT


def heat_cmap():
    stops = [(0.0, "#c9a6ff"), (0.18, "#8f5bff"), (0.38, "#4a2390"), (0.5, "#121016"), (0.62, "#5c4a12"),
             (0.82, "#d9a91f"), (1.0, "#ffe680")]
    return LinearSegmentedColormap.from_list("gt_gamma", stops)


def et_to_pt(hhmm):
    h, m = int(hhmm[:2]), int(hhmm[2:])
    return "%02d:%02d PT" % (h - PT_OFF, m)


def lvl(x):
    return "{:,.0f}".format(x) if x >= 1000 else cs.fmt_level(x, 1 if abs(x - round(x)) > 1e-9 else 0)


def regime(net, tot):
    return "flat" if abs(net) < 0.03 * tot else ("long" if net > 0 else "short")


# ---------------------------------------------------------------- vol inputs
def vol_inputs(date):
    out = {}
    for d in (date, D.prev_weekday(date).isoformat()):
        p = D.SKYLIT / "vol" / "daily" / ("%s.json" % d)
        if not p.exists():
            continue
        j = D._jload(p)
        for s in j["data"]["symbols"]:
            c = s["columns"]
            out[s["symbol"]] = {"iv_front": c["atm_iv_front"][0], "iv_30": c["atm_iv_30"][0],
                                "em_1d_pct": c["em_1d_pct"][0], "close": c["close"][0], "file": str(p), "date": d}
        break
    # SMH is not in the vol file: 20-day realised vol from our price file, stated as a proxy
    rows = [r for r in csv.DictReader(open(ROOT / "data/ai_prints_backtest/5y/prices_5y.csv", encoding="utf-8"))
            if r["ticker"] == "SMH" and r["date"] <= date]
    c = np.array([float(r["close"]) for r in rows[-21:]])
    rv = float(np.std(np.diff(np.log(c)), ddof=1) * math.sqrt(252))
    out["SMH"] = {"iv_front": rv, "iv_30": rv, "em_1d_pct": None, "close": float(c[-1]),
                  "file": "data/ai_prints_backtest/5y/prices_5y.csv (20-day realised vol proxy, to %s)" % rows[-1]["date"],
                  "date": rows[-1]["date"]}
    return out


# ---------------------------------------------------------------- core reads
def cut(m, date, include_today, win=WIN):
    keep = [j for j, e in enumerate(m.expiries) if (e >= date if include_today else e > date)]
    w = np.abs(m.strikes / m.spot - 1) <= win
    k = m.strikes[w]
    order = np.argsort(k)
    return k[order], [m.expiries[j] for j in keep], m.matrix[w][:, keep][order]


def years_to(expiry, snap_et):
    exp_dt = dt.datetime.combine(dt.date.fromisoformat(expiry), dt.time(16, 0), tzinfo=D.ET)
    days = max((exp_dt - snap_et).total_seconds() / 86400.0, 0.05)
    return days / 365.0


def gamma_curve(k, exps, g, spot, snap_et, iv, xs):
    """Total gamma re-priced at spot*(1+x) for x in xs (flat vol); returns array of totals."""
    if g.size == 0:
        return np.zeros_like(xs)
    T = np.array([years_to(e, snap_et) for e in exps])[None, :]
    K = k[:, None]
    sd = iv * np.sqrt(T)
    d10 = (np.log(spot / K) + 0.5 * iv * iv * T) / sd
    hold = np.abs(d10) > 4
    out = []
    for x in xs:
        S = spot * (1 + x)
        d1 = (np.log(S / K) + 0.5 * iv * iv * T) / sd
        expo = np.clip(-(d1 * d1 - d10 * d10) / 2, -50, 50)
        ratio = (S / spot) * np.exp(expo)
        ratio = np.where(hold, 1.0, ratio)
        out.append(float((g * ratio).sum()))
    return np.array(out)


def flip_from(xs, curve, spot):
    """Zero crossing of the re-priced total nearest spot (linear interpolation); None if no crossing."""
    s = np.sign(curve)
    cands = []
    for i in range(len(xs) - 1):
        if s[i] == 0:
            cands.append(xs[i])
        elif s[i] * s[i + 1] < 0:
            x0, x1, y0, y1 = xs[i], xs[i + 1], curve[i], curve[i + 1]
            cands.append(x0 - y0 * (x1 - x0) / (y1 - y0))
    if not cands:
        return None
    x = min(cands, key=abs)
    return {"level": float(spot * (1 + x)), "pct_from_spot": float(x * 100), "n_crossings": len(cands)}


def king_of(k, exps, g, spot):
    if g.size == 0:
        return None
    r, c = np.unravel_index(np.argmax(np.abs(g)), g.shape)
    return {"strike": float(k[r]), "expiry": exps[c], "value": float(g[r, c]), "sign": "+" if g[r, c] > 0 else "-",
            "pct_from_spot": float((k[r] / spot - 1) * 100)}


def rows_read(k, g, spot):
    row = g.sum(axis=1)
    out = {}
    for side, sel in (("above", k > spot), ("below", k < spot)):
        idx = np.where(sel)[0]
        pos = [i for i in idx if row[i] > 0]
        neg = [i for i in idx if row[i] < 0]
        out["largest_long_row_%s" % side] = ({"strike": float(k[max(pos, key=lambda i: row[i])]),
                                              "value": float(max(row[i] for i in pos)),
                                              "pct_from_spot": float((k[max(pos, key=lambda i: row[i])] / spot - 1) * 100)}
                                             if pos else None)
        out["largest_short_row_%s" % side] = ({"strike": float(k[min(neg, key=lambda i: row[i])]),
                                               "value": float(min(row[i] for i in neg)),
                                               "pct_from_spot": float((k[min(neg, key=lambda i: row[i])] / spot - 1) * 100)}
                                              if neg else None)
    # air pockets: the longest run of strikes within +-3% whose |row| is under 10% of the largest |row| there
    w3 = np.abs(k / spot - 1) <= 0.03
    mx = float(np.max(np.abs(row[w3]))) if w3.any() else 0.0
    pockets = {}
    for side, sel in (("above", (k > spot) & w3), ("below", (k < spot) & w3)):
        idx = list(np.where(sel)[0])
        if side == "below":
            idx = idx[::-1]
        best, cur = [], []
        for i in idx:
            if mx and abs(row[i]) < 0.10 * mx:
                cur.append(i)
                if len(cur) > len(best):
                    best = list(cur)
            else:
                cur = []
        if len(best) >= 2:
            lo, hi = sorted([float(k[best[0]]), float(k[best[-1]])])
            pockets[side] = {"from": lo, "to": hi, "n_strikes": len(best),
                             "pct": [float((lo / spot - 1) * 100), float((hi / spot - 1) * 100)]}
        else:
            pockets[side] = None
    out["air_pockets"] = pockets
    return out


def gatekeepers(k, g, spot, king):
    """Rows between spot and the King whose largest cell is at least 25% of the King cell."""
    if king is None:
        return []
    lo, hi = sorted([spot, king["strike"]])
    cellmax = g[np.arange(len(k)), np.argmax(np.abs(g), axis=1)] if g.size else np.array([])
    out = []
    for i in range(len(k)):
        if lo < k[i] < hi and k[i] != king["strike"] and abs(cellmax[i]) >= 0.25 * abs(king["value"]):
            out.append({"strike": float(k[i]), "share_of_king_pct": float(cellmax[i] / abs(king["value"]) * 100)})
    return out


def read_book(m, date, roll, iv, snap_et, include_today=False):
    k, exps, g = cut(m, date, include_today)
    spot = float(m.spot)
    tot = float(np.abs(g).sum()) or 1.0
    near = np.abs(k / spot - 1) <= NEAR
    net = float(g[near].sum())
    xs = np.linspace(-0.04, 0.04, 161)
    curve = gamma_curve(k, exps, g, spot, snap_et, iv, xs)
    post = [j for j, e in enumerate(exps) if e > roll]
    gp = g[:, post]
    totp = float(np.abs(gp).sum()) or 1.0
    netp = float(gp[near].sum())
    curve_p = gamma_curve(k, [exps[j] for j in post], gp, spot, snap_et, iv, xs)
    king = king_of(k, exps, g, spot)
    out = {
        "symbol": m.symbol, "spot": spot, "asof_et": m.asof.isoformat() if m.asof else None,
        "expiries": exps, "iv_used": iv, "strike_window_pct": WIN * 100, "n_strikes": int(len(k)),
        "share_by_expiry_pct": [float(np.abs(g[:, j]).sum() / tot * 100) for j in range(len(exps))],
        "share_through_roll_pct": float(sum(np.abs(g[:, j]).sum() for j, e in enumerate(exps) if e <= roll) / tot * 100),
        "net_pm2_pct": net / tot * 100, "regime": regime(net, tot),
        "flip": flip_from(xs, curve, spot), "total_at_spot_pct": float(curve[80] / tot * 100),
        "king": king, "gatekeepers": gatekeepers(k, g, spot, king),
        "centre": float((np.abs(g).sum(axis=1) * k).sum() / tot),
        "after_roll": {
            "expiries": [exps[j] for j in post],
            "net_pm2_pct": netp / totp * 100, "regime": regime(netp, totp),
            "flip": flip_from(xs, curve_p, spot), "king": king_of(k, [exps[j] for j in post], gp, spot),
            "map_size_vs_now_pct": totp / tot * 100,
        },
        "curve": {"x_pct": [float(x * 100) for x in xs], "now_pct_of_map": [float(v / tot * 100) for v in curve],
                  "after_roll_pct_of_map": [float(v / totp * 100) for v in curve_p]},
    }
    out.update(rows_read(k, g, spot))
    out["after_roll"].update({kk: vv for kk, vv in rows_read(k, gp, spot).items() if kk.startswith("largest")})
    return out, (k, exps, g)


def intraday(date, roll, ivs):
    out = {}
    slots = [h for h, _ in D.live_minutes(date) if h[2:] in ("00", "30") and h >= "0930"]
    for hh in slots:
        snap = D.load_live(date, hh)
        if snap is None:
            continue
        for sym in BOOKS:
            m = snap.get(sym)
            if m is None:
                continue
            k, exps, g = cut(m, date, include_today=True)
            spot = float(m.spot)
            tot = float(np.abs(g).sum()) or 1.0
            near = np.abs(k / spot - 1) <= NEAR
            kfwd, efwd, gfwd = cut(m, date, include_today=False)
            totf = float(np.abs(gfwd).sum()) or 1.0
            nearf = np.abs(kfwd / spot - 1) <= NEAR
            out.setdefault(sym, []).append({
                "net_pm2_ex_today_pct": float(gfwd[nearf].sum() / totf * 100),
                "regime_ex_today": regime(gfwd[nearf].sum(), totf),
                "slot_et": hh, "slot_pt": et_to_pt(hh), "asof_et": m.asof.isoformat() if m.asof else None,
                "spot": spot, "king": king_of(k, exps, g, spot), "king_ex_today": king_of(kfwd, efwd, gfwd, spot),
                "net_pm2_pct": float(g[near].sum() / tot * 100), "regime": regime(g[near].sum(), tot),
                "centre": float((np.abs(g).sum(axis=1) * k).sum() / tot), "map_abs": tot,
                "today_share_pct": float(np.abs(g[:, 0]).sum() / tot * 100) if exps and exps[0] == date else 0.0})
    return out


def spot_path(date):
    d = D.live_dir(date)
    pts = {}
    if not d.is_dir():
        return pts
    for f in sorted(os.listdir(d)):
        if f.endswith("_levels.json.gz") and f[:4].isdigit():
            j = D._jload(d / f)
            for s in j["body"]["data"]["symbols"]:
                if s["symbol"] in BOOKS:
                    pts.setdefault(s["symbol"], []).append((f[:4], float(s["spot"])))
    return pts


def smh_vanna(date, roll, last="2026-12-18", win=0.10):
    return names_eod(date, roll, ("SMH",), last, win).get("SMH")


VANNA_NAMES = ("SMH", "NVDA", "AMD", "MU", "QCOM", "MSFT", "AAPL", "PANW")


def names_eod(date, roll, syms=VANNA_NAMES, last="2026-12-18", win=0.10):
    """End-of-day universe gamma and vanna reads per name (16:00 ET batch). {sym: {gamma: ..., vanna: ...}}"""
    d = D.SKYLIT / "universe" / date
    out = {}
    if not d.is_dir():
        return out
    for f in sorted(os.listdir(d)):
        if not f.startswith("eod_"):
            continue
        j = D._jload(d / f)
        hm = j.get("heatmap", j.get("body", j))
        metric = hm.get("meta", {}).get("metric")
        if metric not in ("gamma", "vanna"):
            continue
        for s in hm["data"]["symbols"]:
            if s["symbol"] in syms and metric not in out.get(s["symbol"], {}):
                out.setdefault(s["symbol"], {})[metric] = _eod_read(s, metric, f, date, roll, last, win)
    return out


def _eod_read(s, metric, f, date, roll, last, win):
    """One name's gamma or vanna read from a universe batch: shares by expiry, net near spot now and after the roll."""
    exps = list(s["expirations"])
    keep = [i for i, e in enumerate(exps) if date < e <= last]
    k = np.array([float(r["strike"]) for r in s["strikes"]])
    mtx = np.array(s["matrix"], float)
    spot = float(s["spot"])
    w = np.abs(k / spot - 1) <= win
    o = np.argsort(k[w])
    kk, g = k[w][o], mtx[w][:, keep][o]
    ex = [exps[i] for i in keep]
    post = [i for i, e in enumerate(ex) if e > roll]
    tot = float(np.abs(g).sum()) or 1.0
    totp = float(np.abs(g[:, post]).sum()) or 1.0
    band = 0.05 if metric == "vanna" else NEAR
    near = np.abs(kk / spot - 1) <= band
    res = {
        "file": f, "asof": s.get("asOf"), "spot": spot, "expiries": ex,
        "share_by_expiry_pct": [float(np.abs(g[:, i]).sum() / tot * 100) for i in range(len(ex))],
        "near_band_pct": band * 100,
        "net_near_now_pct": float(g[near].sum() / tot * 100),
        "net_near_after_roll_pct": float(g[near][:, post].sum() / totp * 100),
        "king": king_of(kk, ex, g, spot), "king_after_roll": king_of(kk, [ex[i] for i in post], g[:, post], spot),
        "rows": {"strikes": kk.tolist(), "now": g.sum(axis=1).tolist(), "after_roll": g[:, post].sum(axis=1).tolist()},
    }
    if metric == "gamma":
        res["regime_now"] = regime(g[near].sum(), tot)
        res["regime_after_roll"] = regime(g[near][:, post].sum(), totp)
    return res


# ---------------------------------------------------------------- charts
def _tile(fig, rect, label, right, right_col, foot):
    fw, fh = fig.get_size_inches()
    tx, ty, tw, th = rect
    cs._round_box(fig, tx, ty, tw, th, fc=P["canvas"], ec=P["border"], lw=1.0, r_in=0.08, z=0)
    fig.text(tx + 0.16 / fw, ty + th - 0.18 / fh, label, fontsize=13, fontweight="bold", color=P["title"], va="top")
    fig.text(tx + tw - 0.16 / fw, ty + th - 0.2 / fh, right, fontsize=10.5, family=MONO, color=right_col, va="top",
             ha="right")
    if foot:
        fig.text(tx + 0.16 / fw, ty + 0.1 / fh, foot, fontsize=9, color=P["muted"], family=MONO, va="bottom")


def _grid(fig, rects0, n=4, cols=2):
    fw, fh = fig.get_size_inches()
    x0, y0, W, H = rects0
    gx, gy = 0.2 / fw, 0.2 / fh
    rows = -(-n // cols)
    tw = (W - gx * (cols + 1)) / cols
    th = (H - gy * (rows + 1)) / rows
    return [(x0 + gx + (i % cols) * (tw + gx), y0 + H - ((i // cols) + 1) * (th + gy), tw, th) for i in range(n)]


def chart_board(reads, grids, out, snap_lbl, src):
    fronts = {s: reads[s]["share_through_roll_pct"] for s in BOOKS}
    regs = [reads[s]["regime"] for s in BOOKS]
    nshort = regs.count("short")
    nlong = regs.count("long")
    lo, hi = min(fronts.values()), max(fronts.values())
    title = "Friday's expiry holds %d-%d%% of each map; %d of 4 books short gamma near the price" % (
        round(lo), round(hi), nshort) if nshort else \
        "Friday's expiry holds %d-%d%% of each map; %d of 4 books long gamma near the price" % (round(lo), round(hi), nlong)
    fig, rects = cs.frame(
        title,
        "Dealer gamma by strike and expiry at the 13:00 PT close (16:00 ET), today's expired column left out. "
        "Yellow = dealers long gamma, purple = short; white box = the largest cell; cyan dash = the price. Rows: the four "
        "strikes nearest the price plus the largest cells inside +-5%. Vendor units: compare within one book only.",
        panels=1, size=(15, 13.2),
        badge=("%d%%" % round(np.median(list(fronts.values()))), "median share expiring Fri"),
        callout="Our record: the largest strike did not pull or pin price (55 days, 165 readings)  ·  big strikes "
                "reversed price no more than any strike  ·  gamma sign: no next-day direction edge (305 sessions)",
        footer_right=src, snapshot=snap_lbl)
    cmap = heat_cmap()
    fw, fh = fig.get_size_inches()
    for rect, sym in zip(_grid(fig, rects[0]), BOOKS):
        k, exps, g = grids[sym]
        r = reads[sym]
        spot = r["spot"]
        reg = r["regime"]
        _tile(fig, rect, NAME[sym], "%s  ·  %s gamma" % (lvl(spot), reg),
              {"long": P["green"], "short": P["red"]}.get(reg, P["subtitle"]),
              "Fri 20 Nov %d%% of map  ·  king %s %s (%s)" % (
                  round(r["share_through_roll_pct"]), lvl(r["king"]["strike"]),
                  dt.date.fromisoformat(r["king"]["expiry"]).strftime("%d %b").lstrip("0"),
                  cs.fmt_pct(r["king"]["pct_from_spot"])))
        near = sorted(range(len(k)), key=lambda i: abs(k[i] - spot))[:4]
        chosen = set(near)
        for i in sorted(range(len(k)), key=lambda i: -np.max(np.abs(g[i]))):
            if len(chosen) >= 13:
                break
            chosen.add(i)
        sel = sorted(chosen, key=lambda i: -k[i])
        M, ks = g[sel], k[sel]
        vmax = float(np.max(np.abs(M))) or 1.0
        Z = np.sign(M) * (np.abs(M) / vmax) ** 0.55
        tx, ty, tw, th = rect
        ax = fig.add_axes([tx + 0.8 / fw, ty + 0.36 / fh, tw - 1.05 / fw, th - 1.05 / fh])
        ax.imshow((Z + 1) / 2, cmap=cmap, vmin=0, vmax=1, aspect="auto", interpolation="nearest")
        for rr in range(len(ks) + 1):
            ax.axhline(rr - 0.5, color=P["canvas"], lw=1.4)
        for cc in range(M.shape[1] + 1):
            ax.axvline(cc - 0.5, color=P["canvas"], lw=1.4)
        for s_ in ax.spines.values():
            s_.set_visible(False)
        ax.tick_params(length=0)
        ax.set_yticks(range(len(ks)))
        ax.set_yticklabels([lvl(v) for v in ks], fontsize=8.5, family=MONO, color=P["subtitle"])
        ax.set_xticks(range(M.shape[1]))
        ax.set_xticklabels([dt.date.fromisoformat(e).strftime("%d %b").lstrip("0") for e in exps], fontsize=9,
                           color=P["text"])
        ax.xaxis.tick_top()
        r0, c0 = np.unravel_index(np.argmax(np.abs(M)), M.shape)
        ax.add_patch(Rectangle((c0 - 0.5, r0 - 0.5), 1, 1, fill=False, edgecolor=P["white"], lw=2.2, zorder=5))
        ax.text(c0, r0, cs.fmt_big(M[r0, c0]), ha="center", va="center", fontsize=7.5, fontweight="bold",
                family=MONO, color="#141414" if M[r0, c0] > 0 else P["title"], zorder=6)
        if ks[-1] <= spot <= ks[0]:
            ysp = float(np.interp(spot, ks[::-1], np.arange(len(ks))[::-1]))
            ax.axhline(ysp, color=P["cyan"], lw=1.8, ls=(0, (4, 2)), zorder=4)
        ax.set_xlim(-0.5, M.shape[1] - 0.5)
        ax.set_ylim(len(ks) - 0.5, -0.5)
    cs.save(fig, out)
    return title


def chart_roll(reads, out, snap_lbl, src):
    flips = [s for s in BOOKS if reads[s]["regime"] != reads[s]["after_roll"]["regime"]]
    title = ("After Friday's expiry, %d of 4 books change gamma state near the price" % len(flips)) if flips else \
        "After Friday's expiry, all 4 books keep their gamma state near the price"
    fig, rects = cs.frame(
        title,
        "Our re-pricing: total dealer gamma over the +-5% map if the price moved x% from the close (flat-vol Black-Scholes "
        "on the vendor's cells), each curve as a share of its own map. Grey = now; colour = with every expiry to Fri 20 Nov "
        "removed. Dot = the flip (zero crossing); the scale fits the +-2.5% range. The header state uses only strikes within +-2%.",
        panels=1, size=(15, 11.0), tags=None,
        callout="Status: the flip is our computation, not a vendor level; trading the flip cross failed (+0.3 to +0.9 pts "
                "vs a +12 bar), and multi-week map reads are untested",
        footer_right=src, snapshot=snap_lbl)
    fw, fh = fig.get_size_inches()
    for rect, sym in zip(_grid(fig, rects[0]), BOOKS):
        r = reads[sym]
        a = r["after_roll"]
        _tile(fig, rect, NAME[sym], "now %s  ->  after Fri %s" % (r["regime"], a["regime"]),
              {"long": P["green"], "short": P["red"]}.get(a["regime"], P["subtitle"]),
              "flip now %s  ·  after Fri %s" % (
                  ("%s (%s)" % (lvl(r["flip"]["level"]), cs.fmt_pct(r["flip"]["pct_from_spot"]))) if r["flip"] else "none in +-4%",
                  ("%s (%s)" % (lvl(a["flip"]["level"]), cs.fmt_pct(a["flip"]["pct_from_spot"]))) if a["flip"] else "none in +-4%"))
        tx, ty, tw, th = rect
        ax = fig.add_axes([tx + 0.85 / fw, ty + 0.62 / fh, tw - 1.15 / fw, th - 1.15 / fh])
        x = np.array(r["curve"]["x_pct"])
        y0 = np.array(r["curve"]["now_pct_of_map"])
        y1 = np.array(r["curve"]["after_roll_pct_of_map"])
        col = {"long": P["green"], "short": P["red"]}.get(a["regime"], P["white"])
        ax.axhline(0, color=P["zero"], lw=1.2)
        ax.axvline(0, color=P["cyan"], lw=1.3, ls=(0, (4, 2)))
        ax.fill_between(x, 0, y1, where=y1 > 0, color=P["green"], alpha=0.10, lw=0)
        ax.fill_between(x, 0, y1, where=y1 < 0, color=P["red"], alpha=0.10, lw=0)
        ax.plot(x, y0, color=P["subtitle"], lw=1.8)
        ax.plot(x, y1, color=col, lw=2.6)
        for f, c in ((r["flip"], P["subtitle"]), (a["flip"], col)):
            if f:
                ax.plot([f["pct_from_spot"]], [0], "o", ms=8, color=c, zorder=5)
        ax.set_xlim(-4, 4)
        mid = np.abs(x) <= 2.5
        ymax = max(5.0, float(np.max(np.abs(np.concatenate([y0[mid], y1[mid]])))) * 1.35)
        ax.set_ylim(-ymax, ymax)
        ax.xaxis.set_major_formatter(lambda v, _: "%+d%%" % v if v else "close")
        ax.yaxis.set_major_formatter(lambda v, _: "%+d%%" % v if v else "0")
        for lab in ax.get_xticklabels() + ax.get_yticklabels():
            lab.set_family(MONO)
            lab.set_fontsize(9)
        for s_ in ax.spines.values():
            s_.set_visible(False)
        ax.tick_params(length=0)
    cs.save(fig, out)
    return title


def _mins(hh):
    return (int(hh[:2]) - 9) * 60 + int(hh[2:]) - 30


def _time_axis(ax, slots):
    ax.set_xlim(-25, 415)
    ticks = [h for h in slots if h[2:] == "00" or h == "0930"]
    ax.set_xticks([_mins(h) for h in ticks])
    ax.set_xticklabels([et_to_pt(h).replace(" PT", "") for h in ticks], fontsize=9, family=MONO, color=P["subtitle"])


def chart_intraday(intra, path, out, snap_lbl, src):
    moved = [s for s in BOOKS if s in intra and len({p["king"]["strike"] for p in intra[s]}) > 1]
    follow = []
    for s in BOOKS:
        pts = intra.get(s, [])
        if len(pts) >= 2:
            dspot = pts[-1]["spot"] - pts[0]["spot"]
            dcen = pts[-1]["centre"] - pts[0]["centre"]
            if dspot and dcen and np.sign(dspot) == np.sign(dcen):
                follow.append(s)
    nmaps = max(len(v) for v in intra.values())
    title = "The map's centre moved down with price in %d of 4 books; the largest cell changed strike in %d of 4" % (
        len(follow), len(moved))
    fig, rects = cs.frame(
        title,
        "Price (white line, half-hourly) and the largest cell (the king; green long, red short) on each of the day's %d "
        "maps, 06:30 to 13:00 PT, in %% from the 06:30 price. A label marks each new king strike. Grey dashes: the map's "
        "|gamma|-weighted centre. Today's own expiry included (it was live)." % nmaps,
        panels=1, size=(15, 11.0),
        callout="Our record: map changes follow price (a roll appears after an 8-10 bp move the same way) and "
                "predict nothing; the king is not a magnet (closer only 40-48% of the time)",
        footer_right=src, snapshot=snap_lbl)
    fw, fh = fig.get_size_inches()
    for rect, sym in zip(_grid(fig, rects[0]), BOOKS):
        pts = intra.get(sym, [])
        if not pts:
            continue
        base = pts[0]["spot"]
        d_sp = (pts[-1]["spot"] / base - 1) * 100
        d_c = (pts[-1]["centre"] / pts[0]["centre"] - 1) * 100
        _tile(fig, rect, NAME[sym], "price %s  ·  centre %s" % (cs.fmt_pct(d_sp, 2), cs.fmt_pct(d_c, 2)), P["text"], "")
        tx, ty, tw, th = rect
        ax = fig.add_axes([tx + 0.85 / fw, ty + 0.55 / fh, tw - 1.2 / fw, th - 1.15 / fh])
        sp = path.get(sym, [])
        if sp:
            ax.plot([_mins(h) for h, _ in sp], [(v / base - 1) * 100 for _, v in sp], color=P["price"], lw=2.0, zorder=3)
        ax.plot([_mins(p["slot_et"]) for p in pts], [(p["centre"] / base - 1) * 100 for p in pts], color=P["subtitle"],
                lw=1.4, ls=(0, (3, 2)), zorder=2)
        ys, prev = [], None
        for p in pts:
            kg = p["king"]
            y = (kg["strike"] / base - 1) * 100
            ys.append(y)
            x = _mins(p["slot_et"])
            ax.plot([x], [y], "o", ms=10, color=P["green"] if kg["value"] > 0 else P["red"], zorder=5)
            if kg["strike"] != prev:
                ax.annotate(lvl(kg["strike"]), (x, y), xytext=(0, 8), textcoords="offset points", ha="center",
                            va="bottom", fontsize=9, family=MONO, fontweight="bold", color=P["title"], zorder=6,
                            bbox=dict(boxstyle="round,pad=0.2", facecolor=P["canvas"], edgecolor="none", alpha=0.85))
            prev = kg["strike"]
        allv = ys + ([(v / base - 1) * 100 for _, v in sp] if sp else [0])
        lo, hi = min(allv), max(allv)
        padv = max(0.15, (hi - lo) * 0.15)
        ax.set_ylim(lo - padv, hi + padv * 1.6)
        _time_axis(ax, [p["slot_et"] for p in pts])
        ax.axhline(0, color=P["zero"], lw=1.0)
        ax.yaxis.set_major_formatter(lambda v, _: "%+.1f%%" % v if abs(v) > 1e-9 else "0")
        for lab in ax.get_yticklabels():
            lab.set_family(MONO)
            lab.set_fontsize(9)
        for s_ in ax.spines.values():
            s_.set_visible(False)
        ax.tick_params(length=0)
    cs.save(fig, out)
    return title


def chart_gamma_path(intra, out, snap_lbl, src):
    stayed = [s for s in BOOKS if intra.get(s) and all(p["regime"] == "long" for p in intra[s])]
    notlong = [s for s in BOOKS if intra.get(s) and intra[s][-1]["regime_ex_today"] != "long"]
    title = "Long gamma held all day in %d of 4 books, but without today's expiry %d of 4 aren't long by the close" % (
        len(stayed), len(notlong))
    fig, rects = cs.frame(
        title,
        "Net dealer gamma within +-2% of the price as a share of each map, on every map of the day. Bars: the whole map "
        "including today's expiring column (green long, red short, grey flat under 3%). Cyan line: the same read without "
        "today's expiry, i.e. what carries into Friday.",
        panels=1, size=(15, 11.0),
        callout="Status: the regime describes how much prices may move, not which way; gamma sign showed no next-day "
                "direction edge (305 sessions) and its intraday range effect was inconsistent across books",
        footer_right=src, snapshot=snap_lbl)
    fw, fh = fig.get_size_inches()
    for rect, sym in zip(_grid(fig, rects[0]), BOOKS):
        pts = intra.get(sym, [])
        if not pts:
            continue
        last = pts[-1]
        _tile(fig, rect, NAME[sym], "close %s %s  ·  ex-today %s %s" % (
            last["regime"], cs.fmt_pct(last["net_pm2_pct"], 0), last["regime_ex_today"],
            cs.fmt_pct(last["net_pm2_ex_today_pct"], 0)),
              {"long": P["green"], "short": P["red"]}.get(last["regime_ex_today"], P["subtitle"]), "")
        tx, ty, tw, th = rect
        ax = fig.add_axes([tx + 0.85 / fw, ty + 0.55 / fh, tw - 1.2 / fw, th - 1.15 / fh])
        xs = [_mins(p["slot_et"]) for p in pts]
        cols = [{"long": P["green"], "short": P["red"]}.get(p["regime"], P["zero"]) for p in pts]
        ax.bar(xs, [p["net_pm2_pct"] for p in pts], width=20, color=cols, zorder=2)
        ax.plot(xs, [p["net_pm2_ex_today_pct"] for p in pts], color=P["cyan"], lw=2.2, marker="o", ms=5, zorder=3)
        ax.axhline(0, color=P["zero"], lw=1.0)
        ax.axhspan(-3, 3, color=P["free"], zorder=0)
        _time_axis(ax, [p["slot_et"] for p in pts])
        ax.yaxis.set_major_formatter(lambda v, _: "%+d%%" % v if abs(v) > 1e-9 else "0")
        for lab in ax.get_yticklabels():
            lab.set_family(MONO)
            lab.set_fontsize(9)
        for s_ in ax.spines.values():
            s_.set_visible(False)
        ax.tick_params(length=0)
    cs.save(fig, out)
    return title


def chart_vanna_names(names, out, snap_lbl, src):
    order = [s for s in VANNA_NAMES if s in names and "vanna" in names[s]]
    vals = {s: names[s]["vanna"]["net_near_after_roll_pct"] for s in order}
    pos = sum(1 for v in vals.values() if v > 0)
    big = max(order, key=lambda s: abs(vals[s]))
    title = "After Friday, vanna near the price is positive on %d of %d maps; %s is the most one-sided (%s)" % (
        pos, len(order), big, cs.fmt_pct(vals[big], 0))
    fig, rects = cs.frame(
        title,
        "Net dealer vanna within +-5% of the price as a share of each name's map, expiries to 18 Dec, end-of-day maps. "
        "Grey = now; colour = with Fri 20 Nov removed. Right: gamma state near the price after Friday / vanna sign. "
        "KLAC and WMT have no vanna map today (only 09:30 gamma maps).",
        tags=[("VANNA  (VEX)", "purple")],
        callout="Status: vanna sign convention not audited against the vendor; the vanna family tested null (12 of 42 "
                "splits vs 12.6 by chance); single-name vanna and gamma untested",
        footer_right=src, snapshot=snap_lbl)
    ax = cs.panel_axes(fig, rects[0], pad=(1.6, 0.55, 3.2, 1.0))
    for i, s_ in enumerate(order):
        a_, b_ = names[s_]["vanna"]["net_near_now_pct"], vals[s_]
        ax.plot([a_, b_], [i, i], color=P["zero"], lw=2.2, zorder=1)
        ax.plot(a_, i, "o", ms=10, color=P["subtitle"], zorder=2)
        ax.plot(b_, i, "o", ms=13, color=P["purple"] if b_ < 0 else P["cyan"], zorder=3)
        gs = names[s_].get("gamma", {}).get("regime_after_roll", "n/a")
        ax.text(1.02, i, "gamma %s / vanna %s" % (gs, "+" if b_ > 0 else "-"), transform=ax.get_yaxis_transform(),
                va="center", fontsize=11.5, family=MONO, color=P["text"])
    ax.axvline(0, color=P["zero"], lw=1.2)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels(order, fontsize=13, color=P["title"], family=MONO)
    ax.invert_yaxis()
    ax.xaxis.set_major_formatter(lambda v, _: "%+d%%" % v)
    for lab in ax.get_xticklabels():
        lab.set_family(MONO)
    for x0, col, lab in ((0.0, P["subtitle"], "now"), (0.10, P["cyan"], "after Friday: positive"),
                         (0.40, P["purple"], "after Friday: negative")):
        ax.text(x0, 1.03, "● " + lab, transform=ax.transAxes, color=col, fontsize=11.5, fontweight="bold")
    cs.save(fig, out)
    return title


def chart_vanna(v, gam, out, snap_lbl, src):
    rows = v["rows"]
    k = np.array(rows["strikes"])
    now = np.array(rows["now"])
    aft = np.array(rows["after_roll"])
    spot = v["spot"]
    s = v["net_near_after_roll_pct"]
    title = "SMH vanna near the price is %s after Friday (%s of the map within +-5%%)" % (
        "positive" if s > 0 else "negative", cs.fmt_pct(s, 0))
    fig, rects = cs.frame(
        title,
        "Net dealer vanna by strike, summed over expiries to 18 Dec, end-of-day map. Grey = now; purple = with Fri 20 Nov "
        "removed. Gamma near the price after Friday: %s. If implied vol falls, %s-vanna re-hedging leans to %s; if it "
        "rises, to %s." % (gam.get("regime_after_roll", "n/a") if gam else "n/a", "positive" if s > 0 else "negative",
                           "buying" if s > 0 else "selling", "selling" if s > 0 else "buying"),
        panels=1, tags=[("VANNA  (VEX)", "purple")],
        callout="Status: vanna sign convention not audited against the vendor; the vanna family tested null (12 of 42 "
                "splits vs 12.6 by chance); single-name vanna untested",
        footer_right=src, snapshot=snap_lbl)
    ax = cs.panel_axes(fig, rects[0], pad=(1.1, 0.75, 0.5, 0.95))
    wbar = (k[1] - k[0]) * 0.8 if len(k) > 1 else 1
    ax.bar(k, now, width=wbar, color=P["zero"], zorder=1)
    ax.bar(k, aft, width=wbar * 0.55, color=P["purple"], zorder=2)
    ax.axvline(spot, color=P["cyan"], lw=1.6, ls=(0, (4, 2)))
    ax.axvspan(spot * 0.95, spot * 1.05, color=P["free"], zorder=0)
    ax.axhline(0, color=P["zero"], lw=1.0)
    i = int(np.argmax(np.abs(aft)))
    ax.annotate("largest after Fri: %s %s" % (lvl(k[i]), cs.fmt_big(aft[i])), (k[i], aft[i]),
                xytext=(0, 10 if aft[i] > 0 else -14), textcoords="offset points", ha="center",
                va="bottom" if aft[i] > 0 else "top", fontsize=10.5, family=MONO, fontweight="bold", color=P["title"])
    ax.text(spot, 1.0, " price %s" % lvl(spot), transform=ax.get_xaxis_transform(), color=P["cyan"], fontsize=10.5,
            family=MONO, va="top", ha="left")
    ax.text(spot * 0.95, 0.02, "+-5% band", transform=ax.get_xaxis_transform(), color=P["muted"], fontsize=9.5,
            va="bottom", ha="left")
    ax.yaxis.set_major_formatter(lambda vv, _: cs.fmt_big(vv) if vv else "0")
    for lab in ax.get_xticklabels() + ax.get_yticklabels():
        lab.set_family(MONO)
    ax.text(0.99, 1.04, "■ now (expiries to 18 Dec)", transform=ax.transAxes, ha="right", va="bottom", fontsize=11,
            color=P["subtitle"])
    ax.text(0.70, 1.04, "■ after Fri 20 Nov", transform=ax.transAxes, ha="right", va="bottom", fontsize=11,
            color=P["purple"])
    cs.save(fig, out)
    return title


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--date", required=True)
    ap.add_argument("--roll", default="2026-11-20")
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    date, tag = a.date, a.date.replace("-", "")
    cs.apply("dark")
    snap = D.load_live(date, "1600")
    if snap is None or snap.slot_et.strftime("%H%M") != "1600":
        sys.exit("no 16:00 ET map for %s under %s" % (date, D.SKYLIT))
    ivs = vol_inputs(date)
    reads, grids = {}, {}
    for sym in BOOKS:
        m = snap.get(sym)
        iv = ivs.get(sym, ivs.get("SPXW"))["iv_front"]
        reads[sym], grids[sym] = read_book(m, date, a.roll, iv, m.asof or snap.slot_et)
        reads[sym]["iv_source"] = ivs.get(sym, {}).get("file")
        reads[sym]["em_1d_pct"] = ivs.get(sym, {}).get("em_1d_pct")
    intra = intraday(date, a.roll, ivs)
    path = spot_path(date)
    van = smh_vanna(date, a.roll)
    day = dt.date.fromisoformat(date).strftime("%d %b %Y").lstrip("0")
    snap_lbl = "%s 13:00 PT close (16:00 ET)" % day
    out = ROOT / (a.out or "reports/charts/%s_index_gamma" % tag)
    out.mkdir(parents=True, exist_ok=True)
    jpath = "data/ai_technical/index_gamma_%s.json" % tag
    titles = {
        "g1_board": chart_board(reads, grids, out / "g1_board.png", snap_lbl, "via " + jpath),
        "g2_roll": chart_roll(reads, out / "g2_roll.png", snap_lbl, "via " + jpath),
        "g3_intraday": chart_intraday(intra, path, out / "g3_intraday.png", "%s, every map 06:30-13:00 PT" % day,
                                      "via " + jpath),
    }
    titles["g5_gamma_path"] = chart_gamma_path(intra, out / "g5_gamma_path.png", "%s, every map 06:30-13:00 PT" % day,
                                               "via " + jpath)
    names = names_eod(date, a.roll)
    if names:
        titles["g6_vanna_names"] = chart_vanna_names(names, out / "g6_vanna_names.png",
                                                     "%s, end-of-day vanna maps" % day, "via " + jpath)
    if van and "vanna" in van:
        titles["g4_smh_vanna"] = chart_vanna(van["vanna"], van.get("gamma"), out / "g4_smh_vanna.png",
                                             "%s, SMH end-of-day vanna map" % day,
                                             "via " + jpath)
    # SPX vs SPY consistency on the S&P axis (SPY x ~10)
    ratio = reads["SPXW"]["spot"] / reads["SPY"]["spot"]
    cons = {"spx_spy_ratio": ratio,
            "king_spxw": reads["SPXW"]["king"], "king_spy_on_spx_axis": reads["SPY"]["king"]["strike"] * ratio,
            "flip_spxw_pct": (reads["SPXW"]["flip"] or {}).get("pct_from_spot"),
            "flip_spy_pct": (reads["SPY"]["flip"] or {}).get("pct_from_spot"),
            "regime_agree": reads["SPXW"]["regime"] == reads["SPY"]["regime"],
            "after_roll_regime_agree": reads["SPXW"]["after_roll"]["regime"] == reads["SPY"]["after_roll"]["regime"]}
    doc = {"date": date, "built_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "snapshot": {"path": snap.path, "slot_et": "16:00", "slot_pt": "13:00", "fetched": snap.fetched},
           "roll": a.roll, "vol_inputs": ivs, "reads": reads, "intraday": intra, "spot_path": path,
           "smh_eod": van, "names_eod": {k: {m: {kk: vv for kk, vv in v.items() if kk != "rows"} for m, v in d.items()}
                                          for k, d in names.items()}, "spx_spy": cons, "chart_titles": titles,
           "notes": ["Units are the vendor's own, comparable within one book only.",
                     "Regime: net gamma within +-2% of spot over total |gamma| within +-5%; flat under 3%.",
                     "Flip: our flat-vol re-pricing of the vendor cells; not a vendor level.",
                     "Descriptive only: no targets, entries, stops, sizes or direction."]}
    with open(ROOT / jpath, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, default=str)
    print("wrote", jpath)
    for s in BOOKS:
        r, ar = reads[s], reads[s]["after_roll"]
        print("%-5s spot %9.2f iv %.3f | exp %s shares %s | Fri %4.1f%% | now %-5s %+6.1f%% flip %s tot@spot %+5.1f%% | "
              "after %-5s %+6.1f%% flip %s size %3.0f%% | king %s %s %s %+.2f%% | after king %s %s %s %+.2f%%"
              % (s, r["spot"], r["iv_used"], [e[5:] for e in r["expiries"]], [round(x) for x in r["share_by_expiry_pct"]],
                 r["share_through_roll_pct"], r["regime"], r["net_pm2_pct"],
                 r["flip"] and "%.2f (%+.2f%%)" % (r["flip"]["level"], r["flip"]["pct_from_spot"]), r["total_at_spot_pct"],
                 ar["regime"], ar["net_pm2_pct"], ar["flip"] and "%.2f (%+.2f%%)" % (ar["flip"]["level"], ar["flip"]["pct_from_spot"]),
                 ar["map_size_vs_now_pct"],
                 r["king"]["strike"], r["king"]["expiry"][5:], cs.fmt_big(r["king"]["value"]), r["king"]["pct_from_spot"],
                 ar["king"]["strike"], ar["king"]["expiry"][5:], cs.fmt_big(ar["king"]["value"]), ar["king"]["pct_from_spot"]))
        for key in ("largest_long_row_above", "largest_long_row_below", "largest_short_row_above", "largest_short_row_below"):
            x = r[key]
            print("      %-24s %s" % (key, x and "%s %s %+.2f%%" % (x["strike"], cs.fmt_big(x["value"]), x["pct_from_spot"])))
        print("      air pockets", r["air_pockets"], "gatekeepers", r["gatekeepers"][:4])
        for p in intra.get(s, []):
            print("      %s spot %.2f king %s %s %s | ex-today %s %s | net %+.1f%% %s centre %.2f today-share %.0f%%"
                  % (p["slot_pt"], p["spot"], p["king"]["strike"], p["king"]["expiry"][5:], cs.fmt_big(p["king"]["value"]),
                     p["king_ex_today"] and p["king_ex_today"]["strike"], p["king_ex_today"] and p["king_ex_today"]["expiry"][5:],
                     p["net_pm2_pct"], p["regime"], p["centre"], p["today_share_pct"]))
    if van:
        for mtr, v in van.items():
            print("SMH eod %s %s spot %.2f near now %+.1f%% after %+.1f%% king %s king-after %s shares %s" % (
                mtr, v["file"], v["spot"], v["net_near_now_pct"], v["net_near_after_roll_pct"],
                v["king"], v["king_after_roll"], [round(x) for x in v["share_by_expiry_pct"]]))
    print("spx/spy", json.dumps(cons, default=str))
    print(json.dumps(titles, indent=1))


if __name__ == "__main__":
    main()
