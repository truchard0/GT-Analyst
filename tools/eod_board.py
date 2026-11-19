#!/usr/bin/env python3
"""One-page session board: the routes into tonight, Friday and next week plus every session read (gamma, vanna,
succession, VIX), in the house style, portrait, sized to fill a letter page.

    python tools/eod_board.py --date 2026-11-19 [--out reports/charts/<date>_routes]

Reads (all written earlier by our own tools; nothing is fetched here):
  data/ai_technical/eod_routes_<date>.json      route shares and horizon ranges (tools/eod_routes.py)
  data/ai_technical/index_gamma_<date>.json     dealer gamma by book, single-name vanna (tools/index_gamma.py)
  data/ai_technical/market_context_<date>.json  successions, checklist, ATR, VIX block (tools/market_context.py)
Descriptive only: route odds are base rates from past days like this one, not forecasts; no targets, entries, stops
or sizes; price direction stays a no-call.
"""
import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import market_update  # noqa: E402,F401
import numpy as np  # noqa: E402
from market_update import chartstyle as cs  # noqa: E402
from matplotlib.patches import FancyArrowPatch  # noqa: E402

P = cs.P
MONO = cs.MONO
W, H = 15.0, 19.4


def Y(t):
    return 1 - t / H


def X(x):
    return x / W


def box(fig, x, t, w, h, edge, fill=None, lw=1.6, r=0.12):
    return cs._round_box(fig, X(x), Y(t + h), w / W, h / H, fc=fill or P["panel"], ec=edge, lw=lw, r_in=r, z=1)


def txt(fig, x, t, s, size=12, col=None, weight="normal", ha="left", va="top", mono=False, **kw):
    return fig.text(X(x), Y(t), s, fontsize=size, color=col or P["text"], fontweight=weight, ha=ha, va=va,
                    family=MONO if mono else cs.FONT, zorder=5, **kw)


def arrow(fig, x0, t0, x1, t1, col):
    fig.add_artist(FancyArrowPatch((X(x0), Y(t0)), (X(x1), Y(t1)), transform=fig.transFigure, arrowstyle="-|>",
                                   mutation_scale=22, color=col, lw=2.0, zorder=4))


def panel(fig, x, t, w, h, tag, col="white"):
    box(fig, x, t, w, h, P["border"], P["panel"], lw=1.0)
    txt(fig, x + 0.18, t + 0.16, cs.spaced(tag), size=11.5, col=P.get(col, col), weight="bold",
        bbox=dict(boxstyle="round,pad=0.4,rounding_size=0.3", facecolor="none", edgecolor=P.get(col, col), lw=1.2))


def axes(fig, x, t, w, h):
    ax = fig.add_axes([X(x), Y(t + h), w / W, h / H])
    ax.set_zorder(3)
    ax.set_facecolor("none")
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0, colors=P["subtitle"], labelsize=9.5)
    return ax


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--priced", type=float, default=1.99)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    d = a.date
    tag = d.replace("-", "")
    RT = json.load(open(ROOT / "data" / "ai_technical" / ("eod_routes_%s.json" % d), encoding="utf-8"))
    IG = json.load(open(ROOT / "data" / "ai_technical" / ("index_gamma_%s.json" % tag), encoding="utf-8"))
    MCX = json.load(open(ROOT / "data" / "ai_technical" / ("market_context_%s.json" % d), encoding="utf-8"))
    out = pathlib.Path(a.out) if a.out else ROOT / "reports" / "charts" / ("%s_routes" % tag)
    out.mkdir(parents=True, exist_ok=True)
    cs.apply("dark")
    plt = cs.plt
    fig = plt.figure(figsize=(W, H), dpi=cs.DPI)
    fig.patch.set_facecolor(P["canvas"])
    cs.signal_stripe(fig)

    c0 = RT["close"]
    R, ref, Hz = RT["routes"], RT["reference"], RT["horizons"]
    vix = MCX["panels"]["vix"]
    today = MCX["panels"]["today"]
    ex = MCX["panels"]["exhaustion"]
    exp = MCX["panels"]["expected"]
    lv = MCX["extras"]["key_levels"]
    rec = MCX["records"]["selloff"]["projection"]["HIGH (-7%)"]
    pmv = MCX["extras"]["priced_move_next"]
    a.priced = round(pmv["em_pct"], 2)
    lo_b, hi_b = pmv["low"], pmv["high"]
    L = lambda v: cs.fmt_level(v, 0)

    # ---------------------------------------------------------------- header
    txt(fig, 0.45, 0.42, "Into tonight, Friday and next week: four routes from %s" % L(c0), size=27, col=P["title"],
        weight="bold")
    txt(fig, 0.45, 1.02, ("S&P 500 at the Thursday 19 Nov close, VIX %.2f. Route odds are what happened after the %d past days "
                          "our selloff checklist read HIGH\n(%d episodes, 2016-2026), the reading it shows tonight. "
                          "They are base rates, not forecasts, and direction stays a no-call.") % (
        vix["close"], ref["days"], ref["episodes"]), size=13, col=P["subtitle"], linespacing=1.4)

    # ---------------------------------------------------------------- row A: uncertainty + drivers
    t = 1.95
    box(fig, 0.45, t, 7.6, 1.15, P["border"])
    txt(fig, 0.7, t + 0.2, "HOW WIDE THE NEXT WEEK HAS RUN", size=10.5, col=P["subtitle"], weight="bold")
    segs = [("LOW", "#2a2a2a"), ("NORMAL", "#2a2a2a"), ("HIGH", P["orange"]), ("EXTREME", "#2a2a2a")]
    for k, (lab, col) in enumerate(segs):
        box(fig, 0.7 + k * 1.15, t + 0.55, 1.05, 0.16, col, col, lw=0.5, r=0.04)
        txt(fig, 0.7 + k * 1.15 + 0.52, t + 0.78, lab, size=8.5, col=P["muted"] if col == "#2a2a2a" else P["orange"],
            ha="center", weight="bold")
    hw, aw = Hz["next_week"]["high"], Hz["next_week"]["all"]
    span_h, span_a = hw["p90"] - hw["p10"], aw["p90"] - aw["p10"]
    txt(fig, 5.45, t + 0.2, "HIGH", size=20, col=P["orange"], weight="bold")
    txt(fig, 5.45, t + 0.62, "next-week middle 80%%:\n%.1f%% wide vs %.1f%% (%.1fx)" % (
        span_h, span_a, span_h / span_a), size=9.5, col=P["text"], mono=True, linespacing=1.3)
    box(fig, 8.3, t, 6.25, 1.15, P["border"])
    txt(fig, 8.55, t + 0.2, "WHAT MOVED TODAY AND WHAT IS SCHEDULED", size=10.5, col=P["subtitle"], weight="bold")
    chips = [("OPEX FRI", "yellow"), ("VIX %.1f" % vix["close"], "red"), ("200-DAY %s" % L(lv["sma200"]["level"]), "white"),
             ("CHIPS · AMD −8%", "purple"), ("ANTHROPIC IPO", "cyan"), ("SHORT WEEK", "white")]
    x = 8.55
    row = 0
    for lab, col in chips:
        wlab = 0.098 * len(lab) + 0.3
        if x + wlab > 14.4:
            x, row = 8.55, row + 1
        box(fig, x, t + 0.52 + row * 0.33, wlab, 0.27, P[col], P["canvas"], lw=1.2, r=0.06)
        txt(fig, x + wlab / 2, t + 0.655 + row * 0.33, lab, size=9.5, col=P[col], weight="bold", ha="center",
            va="center", mono=True)
        x += wlab + 0.12

    # ---------------------------------------------------------------- row B: route tree
    t = 3.35
    panel(fig, 0.45, t, 14.1, 6.55, "ROUTE TREE · TONIGHT → FRIDAY → NEXT WEEK", "cyan")
    cx = 7.5
    box(fig, cx - 2.6, t + 0.55, 5.2, 0.72, P["cyan"], "#04181d")
    txt(fig, cx, t + 0.66, "TONIGHT", size=14, col=P["cyan"], weight="bold", ha="center")
    txt(fig, cx, t + 0.98, "S&P %s close (−2.0%%) · VIX %.2f · low %s" % (L(c0), vix["close"], L(today["low"])),
        size=10, col=P["text"], ha="center", mono=True)
    arrow(fig, cx, t + 1.28, cx, t + 1.55, P["cyan"])
    box(fig, cx - 3.6, t + 1.57, 7.2, 0.72, P["yellow"], "#141204")
    txt(fig, cx, t + 1.68, "FRI 20 NOV · MONTHLY OPEX", size=13.5, col=P["yellow"], weight="bold", ha="center")
    txt(fig, cx, t + 2.0, "06:30 PT S&P monthly settles · 13:00 PT: 61-93% of every dealer map expires", size=10,
        col=P["text"], ha="center", mono=True)
    cols = [
        ("reclaim", "RECLAIM", "green", ["VIX eases toward its", "20-day mean, %.1f" % vix["m20"]],
         ["Close back above the", "200-day, %s" % L(lv["sma200"]["level"])], "ends +2% or more"),
        ("chop", "CHOP", "white", ["VIX holds in the", "mid-to-high 20s"],
         ["Friday closes inside", "the priced %s-%s" % (L(lo_b), L(hi_b))], "ends within ±2%"),
        ("diprip", "DIP & RIP", "cyan", ["Another 3%+ flush,", "below about %s" % L(c0 * 0.97)],
         ["VIX spike fades", "within days"], "ends at or above %s" % L(c0)),
        ("lower", "LOWER", "red", ["VIX closes above", "today's %.1f" % vix["close"]],
         ["Close below the", "priced band, %s" % L(lo_b)], "ends −2% or worse"),
    ]
    xs = [2.15, 5.75, 9.35, 12.95]
    for (key, name, col, b1, b2, endtxt), x in zip(cols, xs):
        r = R[key]
        c = P[col]
        arrow(fig, cx, t + 2.3, x, t + 2.72, c)
        txt(fig, x, t + 2.78, "%s  %d%%" % (name, r["share"]), size=15.5, col=c, weight="bold", ha="center")
        txt(fig, x, t + 3.12, "%d of %d episodes" % (r["episodes"], ref["episodes"]), size=9.5, col=P["subtitle"],
            ha="center", mono=True)
        for k, lines in enumerate((b1, b2)):
            tt = t + 3.45 + k * 0.98
            box(fig, x - 1.55, tt, 3.1, 0.7, c, P["canvas"], lw=1.4)
            txt(fig, x, tt + 0.13, lines[0], size=10.5, col=c, weight="bold", ha="center")
            txt(fig, x, tt + 0.4, lines[1], size=10, col=P["text"], ha="center", mono=True)
            arrow(fig, x, tt + 0.71, x, tt + 0.97, c)
        tt = t + 5.41
        box(fig, x - 1.55, tt, 3.1, 0.92, c, P["canvas"], lw=2.0)
        txt(fig, x, tt + 0.12, "BY FRI 27: %s" % endtxt, size=9.5, col=c, weight="bold", ha="center")
        txt(fig, x, tt + 0.42, "median %s" % cs.fmt_pct(r["median_end_pct"], 1), size=12.5, col=P["title"],
            weight="bold", ha="center", mono=True)
        txt(fig, x, tt + 0.7, "%d past days" % r["days"], size=9, col=P["subtitle"], ha="center", mono=True)

    # ---------------------------------------------------------------- row C: paths + horizons
    t = 10.1
    panel(fig, 0.45, t, 7.6, 3.75, "ROUTE PATHS · MEDIANS", "green")
    ax = axes(fig, 1.35, t + 0.75, 6.4, 2.65)
    xs_p = [0, 0.5, 1, 2, 3, 4, 5]
    F = RT["fan"]
    f = lambda q: [c0 * (1 + v / 100) for v in F[str(q)]]
    ax.fill_between(xs_p, f(10), f(90), color="#1b1b1b", lw=0)
    ax.fill_between(xs_p, f(25), f(75), color="#262626", lw=0)
    for key, col in (("reclaim", "green"), ("chop", "white"), ("diprip", "cyan"), ("lower", "red")):
        mp = R[key]["median_path"]
        ys = [c0 * (1 + v / 100) for v in mp]
        ax.plot(xs_p, ys, color=P[col], lw=2.4)
        ax.scatter([5], [ys[-1]], s=30, color=P[col], zorder=5)
    ax.axhline(lv["sma200"]["level"], color=P["subtitle"], lw=0.9, ls=(0, (2, 3)))
    ax.text(0.05, lv["sma200"]["level"], "200-day %s" % L(lv["sma200"]["level"]), color=P["subtitle"], fontsize=9,
            va="bottom", family=MONO)
    ax.plot([1, 1], [lo_b, hi_b], color=P["purple"], lw=5, alpha=0.55, solid_capstyle="butt")
    ax.text(1.1, lo_b + 5, "priced ±%.2f%%" % a.priced, color=P["purple"], fontsize=9, va="bottom", family=MONO)
    ax.scatter([0], [c0], s=50, color=P["yellow"], zorder=6)
    ax.set_xticks(xs_p)
    ax.set_xticklabels(RT["labels"], fontsize=9)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: L(v)))
    ax.grid(axis="y", color=P["border"], lw=0.6)
    ax.set_xlim(-0.15, 5.2)

    panel(fig, 8.3, t, 6.25, 3.75, "HOW FAR EACH HORIZON RAN", "purple")
    ax = axes(fig, 8.6, t + 0.75, 5.7, 2.75)
    rows = [("tonight", "Tonight → Fri open"), ("friday", "Friday close"), ("next_week", "Next week, Fri 27")]
    lim = max(abs(Hz["next_week"]["high"]["p10"]), Hz["next_week"]["high"]["p90"]) * 1.12
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-0.3, 3.0)
    ax.axvline(0, color=P["zero"], lw=1)
    for k, (key, lab) in enumerate(rows):
        y = 2.55 - k * 1.05
        for dy, s, col in ((0.0, Hz[key]["high"], P["white"]), (-0.32, Hz[key]["all"], P["muted"])):
            ax.plot([s["p10"], s["p90"]], [y + dy, y + dy], color=col, lw=2.2, solid_capstyle="round")
            ax.plot([s["p25"], s["p75"]], [y + dy, y + dy], color=col, lw=9, solid_capstyle="butt")
            ax.scatter([s["median"]], [y + dy], s=40, color=P["yellow"], zorder=5)
        h = Hz[key]["high"]
        ax.text(-lim, y + 0.22, lab, color=P["text"], fontsize=10, fontweight="bold", va="bottom")
        ax.text(lim, y + 0.22, "%d%% higher · %s to %s" % (h["p_up"], L(c0 * (1 + h["p10"] / 100)),
                                                            L(c0 * (1 + h["p90"] / 100))),
                color=P["subtitle"], fontsize=9, va="bottom", ha="right", family=MONO)
    ax.set_yticks([])
    ax.set_xticks([-4, -2, 0, 2, 4])
    ax.set_xticklabels(["−4%", "−2%", "0", "+2%", "+4%"], fontsize=9)
    ax.text(0, -0.28, "white: past HIGH days (n=%d) · grey: all days (n=%d) · bar 50%%, line 80%%" % (
        Hz["tonight"]["high"]["n"], Hz["tonight"]["all"]["n"]), color=P["muted"], fontsize=8.5, ha="center",
        va="bottom", family=MONO)

    # ---------------------------------------------------------------- row D: gamma, vanna, succession, VIX
    t = 14.05
    th = 4.0
    tw = 3.4
    gx = [0.45, 0.45 + tw + 0.17, 0.45 + 2 * (tw + 0.17), 0.45 + 3 * (tw + 0.17)]
    # gamma
    panel(fig, gx[0], t, tw, th, "GAMMA", "yellow")
    books = [("SPXW", -2.9, -23.0, "7,220 −"), ("SPY", -10.6, 9.9, "710 −"), ("QQQ", 35.0, -11.5, "645 +"),
             ("SMH", 22.0, 24.0, "460 +")]
    ax = axes(fig, gx[0] + 0.25, t + 0.75, tw - 0.45, 2.45)
    ax.set_xlim(-40, 40)
    ax.set_ylim(-0.6, 3.6)
    ax.axvspan(-3, 3, color="#1c1c1c", lw=0)
    ax.axvline(0, color=P["zero"], lw=1)
    for k, (bk, now, aft, king) in enumerate(books):
        y = 3 - k
        ax.barh(y + 0.17, now, height=0.3, color=P["yellow"] if now > 0 else P["purple"])
        ax.barh(y - 0.17, aft, height=0.3, color=P["yellow"] if aft > 0 else P["purple"], alpha=0.4)
        ax.text(-39, y + 0.38, bk, color=P["text"], fontsize=9.5, fontweight="bold", va="bottom")
        ax.text(39, y + 0.38, "king %s" % king, color=P["subtitle"], fontsize=8.5, va="bottom", ha="right", family=MONO)
    ax.set_yticks([])
    ax.set_xticks([])
    txt(fig, gx[0] + 0.25, t + 3.3, "Net gamma within 2% of price, short ← → long.\nSolid: now · faded: after Friday.\n"
                                     "Friday holds 61-93% of every map.", size=8.8, col=P["subtitle"], linespacing=1.3)
    # vanna
    panel(fig, gx[1], t, tw, th, "VANNA", "purple")
    ne = IG["names_eod"]
    vv = sorted(((k, v["vanna"]["net_near_after_roll_pct"]) for k, v in ne.items() if v.get("vanna")),
                key=lambda kv: kv[1])
    ax = axes(fig, gx[1] + 0.25, t + 0.75, tw - 0.45, 2.45)
    m = max(abs(v) for _, v in vv) * 1.25
    ax.set_xlim(-m, m)
    ax.axvline(0, color=P["zero"], lw=1)
    for k, (nm, v) in enumerate(vv):
        col = P["cyan"] if v > 0 else P["purple"]
        ax.plot([0, v], [k, k], color=col, lw=2)
        ax.scatter([v], [k], s=38, color=col, zorder=5)
        ax.text(-m * 0.97, k, nm, color=P["text"], fontsize=9, va="center", fontweight="bold")
        ax.text(m * 0.97, k, cs.fmt_pct(v, 0), color=col, fontsize=9, va="center", ha="right", family=MONO)
    ax.set_yticks([])
    ax.set_xticks([])
    txt(fig, gx[1] + 0.25, t + 3.3, "Net vanna near price after Friday.\nOur record: null, 12 of 42 tests\n"
                                     "vs 12.6 by chance. Sign unaudited.", size=8.8, col=P["subtitle"], linespacing=1.3)
    # succession
    panel(fig, gx[2], t, tw, th, "SUCCESSION", "orange")
    sx = gx[2] + 0.3
    txt(fig, sx, t + 0.7, "%d" % today["succ"], size=40, col=P["orange"], weight="bold", mono=True)
    txt(fig, sx + 1.05, t + 0.82, "today · %s\n%.2f%% range" % ("crisis band", today["range_pct"]),
        size=10, col=P["text"], linespacing=1.3)
    lines = [("November", "%d in %d sessions" % (today["mtd_succ"], today["mtd_days"])),
             ("Pace", "%d / month (20 = bear)" % round(today["mtd_avg"] * 21)),
             ("Rolling 20d", "%d" % today["rolling20"]),
             ("Checklist", "%s, %d of %d" % (ex["risk"], ex["n"], ex["of"])),
             ("Its record", "drop %d%% · cancel %d%%" % (rec["fulfilled"], rec["invalidated_first"])),
             ("Cancel level", "close > %s" % cs.fmt_level(ex["projected"]["validation"], 2))]
    for k, (a1, a2) in enumerate(lines):
        txt(fig, sx, t + 1.75 + k * 0.33, a1, size=9.5, col=P["subtitle"])
        txt(fig, sx + 3.0, t + 1.75 + k * 0.33, a2, size=9.5, col=P["text"], mono=True, ha="right")
    # vix
    panel(fig, gx[3], t, tw, th, "VIX AND RANGE", "red")
    sx = gx[3] + 0.3
    txt(fig, sx, t + 0.7, "%.1f" % vix["close"], size=40, col=P["red"], weight="bold", mono=True)
    txt(fig, sx + 1.75, t + 0.82, "%+.2f today\n%d%% of the year" % (vix["chg"], vix["pct_rank_1y"]), size=10,
        col=P["text"], linespacing=1.3)
    a5 = exp["expected"]
    lines = [("5-day change", "%+.2f" % vix["chg5"]), ("20-day mean", "%.2f" % vix["m20"]),
             ("20-day high", "%.2f" % vix["hi20"]), ("ATR-5", "%.0f pts (%.2f%%)" % (a5["pts"], a5["pct"])),
             ("ATR-5 / ATR-20", "%.2f, normal" % MCX["panels"]["regime"]["ratio"]),
             ("Priced Friday", "±%.2f%%" % a.priced)]
    for k, (a1, a2) in enumerate(lines):
        txt(fig, sx, t + 1.75 + k * 0.33, a1, size=9.5, col=P["subtitle"])
        txt(fig, sx + 3.0, t + 1.75 + k * 0.33, a2, size=9.5, col=P["text"], mono=True, ha="right")

    # ---------------------------------------------------------------- callout + footer
    t = 18.25
    box(fig, 0.45, t, 14.1, 0.6, P["callout_border"], P["callout_fill"], lw=1.6)
    txt(fig, 7.5, t + 0.3, "Our record: dealer maps, vanna and the checklist showed no direction edge. "
                           "What holds up is size: wide days follow wide days.", size=12, col=P["callout_text"],
        weight="bold", ha="center", va="center")
    txt(fig, 0.45, 19.2, "Data: Skylit dealer-positioning maps, 19 Nov 2026, 13:00 PT close · Skylit vol file · "
                         "Yahoo daily S&P 500 and VIX 2016-2026", size=10.5, col=P["subtitle"], weight="bold", va="bottom")
    txt(fig, 14.55, 19.2, "G T · A N A L Y S T   ·   not investment advice", size=10, col=P["muted"], ha="right",
        va="bottom")
    p = out / "r3_session_board.png"
    fig.savefig(p, dpi=cs.DPI, facecolor=P["canvas"])
    print(p)


if __name__ == "__main__":
    main()
