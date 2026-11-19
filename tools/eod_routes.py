#!/usr/bin/env python3
"""Routes into tonight, Friday and next week from one session's S&P close, measured on past days like it.

    GT_SKYLIT_ROOT=<mirror> python tools/eod_routes.py --date 2026-11-19 [--h 5] [--out reports/charts/<date>_routes]

Reference set: every day since 2016 on which the selloff checklist (tools/market_context.exhaustion, 14 factors with
VIX) read HIGH, as it does on --date. For each, the path from that close: next open (overnight), then the next --h
closes. Each path is sorted into four routes (exhaustive, mutually exclusive, on closes and the next open):
    lower      the window ends 2% or more below the start
    dip & rip  the path touches -3% or worse, then ends at or above the start
    reclaim    the window ends 2% or more above the start without touching -3%
    chop       everything else
Writes data/ai_technical/eod_routes_<date>.json and two house-style charts. Base rates, not forecasts: no targets,
entries, stops or sizes; price direction stays a no-call.
"""
import argparse
import datetime as dt
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import market_context as MC  # noqa: E402

np = MC.np
cs = MC.cs
P = cs.P

ROUTES = [("reclaim", "Reclaim", "green"), ("chop", "Chop", "white"), ("diprip", "Dip & rip", "cyan"),
          ("lower", "Lower", "red")]


def route_of(path):
    end, mn = path[-1], min(path[1:])
    if end <= -0.02:
        return "lower"
    if mn <= -0.03 and end >= 0:
        return "diprip"
    if end >= 0.02 and mn > -0.03:
        return "reclaim"
    return "chop"


def pct(a, q):
    return float(np.percentile(a, q))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--h", type=int, default=5)
    ap.add_argument("--labels", default="Thu 19|Fri open|Fri 20|Mon 23|Tue 24|Wed 25|Fri 27")
    ap.add_argument("--priced", default="1.99", help="options-priced 1-day move in percent, Skylit vol file")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    H = a.h
    rows, p_spx = MC.load_daily("SPX", a.date)
    vrows, p_vix = MC.load_daily("VIX", a.date)
    T = MC.build_table(rows)
    VX = MC.vix_series(vrows, list(T["date"]))
    n = T["n"]
    c, o = T["close"], T["open"]
    i0 = n - 1
    if T["date"][i0] != a.date:
        raise SystemExit("no row for %s" % a.date)
    c0 = float(c[i0])
    risk_today = MC.exhaustion(T, i0, VX[i0])["risk"]

    def path(i):
        return [0.0, o[i + 1] / c[i] - 1] + [c[i + k] / c[i] - 1 for k in range(1, H + 1)]

    sets = {"high": [], "all": []}
    for i in range(60, n - H):
        if VX[i] is None:
            continue
        pth = path(i)
        sets["all"].append((i, pth))
        if MC.exhaustion(T, i, VX[i])["risk"] == "HIGH":
            sets["high"].append((i, pth))
    hi = sets["high"]
    eps = []
    for i, _ in hi:
        if not eps or i - eps[-1][-1] > H:
            eps.append([i])
        else:
            eps[-1].append(i)
    first = set(e[0] for e in eps)

    R = {}
    for key, _, _ in ROUTES:
        mem = [p for i, p in hi if route_of(p) == key]
        epm = [p for i, p in hi if i in first and route_of(p) == key]
        R[key] = dict(days=len(mem), share=round(100 * len(mem) / len(hi)), episodes=len(epm),
                      episode_share=round(100 * len(epm) / len(first)),
                      median_path=[round(float(np.median([p[k] for p in mem])) * 100, 3) for k in range(H + 2)] if mem else None,
                      median_end_pct=round(float(np.median([p[-1] for p in mem])) * 100, 2) if mem else None)

    def horizon(k, S):
        v = np.asarray([p[k] for _, p in S])
        return dict(n=len(v), p_up=round(float((v > 0).mean()) * 100), median=round(pct(v, 50) * 100, 2),
                    p10=round(pct(v, 10) * 100, 2), p25=round(pct(v, 25) * 100, 2), p75=round(pct(v, 75) * 100, 2),
                    p90=round(pct(v, 90) * 100, 2))
    Hz = {name: {s: horizon(k, sets[s]) for s in ("high", "all")}
          for name, k in (("tonight", 1), ("friday", 2), ("next_week", H + 1))}
    fan = {q: [round(pct([p[k] for _, p in hi], q) * 100, 3) for k in range(H + 2)] for q in (10, 25, 75, 90)}

    out = pathlib.Path(a.out) if a.out else ROOT / "reports" / "charts" / ("%s_routes" % a.date.replace("-", ""))
    out.mkdir(parents=True, exist_ok=True)
    doc = dict(date=a.date, close=c0, risk_today=risk_today, horizon_sessions=H, labels=a.labels.split("|"),
               reference=dict(days=len(hi), episodes=len(first), window="%s to %s" % (T["date"][60], T["date"][n - H - 1]),
                              definition="selloff checklist HIGH (tools/market_context.exhaustion)"),
               routes=R, horizons=Hz, fan=fan, sources=dict(spx=p_spx, vix=p_vix),
               rules="Base rates from past HIGH-checklist days, not forecasts. No targets, entries, stops or sizes.")
    jp = ROOT / "data" / "ai_technical" / ("eod_routes_%s.json" % a.date)
    jp.write_text(json.dumps(doc, indent=1), encoding="utf-8")
    print("wrote", jp)
    cs.apply("dark")
    print(chart_routes(T, i0, doc, out, float(a.priced)))
    print(chart_horizons(doc, out, float(a.priced)))
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "median_path"} for k, v in R.items()}))
    print(json.dumps(Hz))


def lvl(x):
    return cs.fmt_level(x, 0)


def chart_routes(T, i0, doc, out, priced):
    c0, H, R, ref = doc["close"], doc["horizon_sessions"], doc["routes"], doc["reference"]
    labels = doc["labels"]
    up = doc["horizons"]["next_week"]["high"]["p_up"]
    title = "Four routes from %s into next week: %d%% of past HIGH-checklist weeks ended higher" % (lvl(c0), up)
    sub = ("S&P 500, last 20 closes, then what happened after the %d past days the selloff checklist read HIGH (%d episodes, "
           "2016 to %s). Lines are each route's median path; shading is the middle 50%% and 80%% of all paths." % (
               ref["days"], ref["episodes"], T["date"][-1 - H][:4]))
    call = "Routes are what happened before, not a forecast. 40-60% is a no-call on direction; the size of the moves is the signal."
    fig, rects = cs.frame(title, sub, panels=1, tags=[("TONIGHT · FRIDAY · NEXT WEEK", "white")], callout=call,
                          footer_right="daily_SPX.csv + daily_VIX.csv (Yahoo), 2016 to %s; eod_routes_%s.json" % (
                              doc["date"], doc["date"]))
    ax = cs.panel_axes(fig, rects[0], pad=(1.05, 0.55, 0.3, 0.75))
    hist = [float(x) for x in T["close"][i0 - 19:i0 + 1]]
    hx = list(range(-19, 1))
    xs = [0, 0.5] + list(range(1, H + 1))
    F = doc["fan"]
    f = lambda q: [c0 * (1 + v / 100) for v in F[q]]
    ax.fill_between(xs, f(10), f(90), color="#1b1b1b", lw=0, zorder=1)
    ax.fill_between(xs, f(25), f(75), color="#262626", lw=0, zorder=1)
    ax.plot(hx, hist, color=P["yellow"], lw=2.4, zorder=4)
    ax.scatter([0], [c0], s=70, color=P["yellow"], zorder=6)
    ax.text(-0.3, c0, lvl(c0) + "  ", ha="right", va="center", color=P["yellow"], fontsize=cs.SIZES["level"],
            family=cs.MONO, fontweight="bold", zorder=6)
    ends = []
    for key, name, col in ROUTES:
        mp = R[key]["median_path"]
        if not mp:
            continue
        ys = [c0 * (1 + v / 100) for v in mp]
        ax.plot(xs, ys, color=P[col], lw=2.6, zorder=5, solid_capstyle="round")
        ax.scatter([xs[-1]], [ys[-1]], s=46, color=P[col], zorder=6)
        ends.append((ys[-1], key, name, col))
    # reference levels
    for y, txt, col in ((7415.64, "7,416  checklist cancel (today's high)", "green"), (7348.02, "7,348  200-day average", "subtitle")):
        ax.axhline(y, color=P[col], lw=0.9, ls=(0, (2, 3)), zorder=2, alpha=0.8)
        ax.text(-19, y, txt, color=P[col], fontsize=cs.SIZES["tiny"], va="bottom", ha="left", family=cs.MONO)
    lo_b, hi_b = c0 * (1 - priced / 100), c0 * (1 + priced / 100)
    ax.plot([1, 1], [lo_b, hi_b], color=P["purple"], lw=5, alpha=0.55, zorder=3, solid_capstyle="butt")
    ax.text(1.12, lo_b, "options price ±%.2f%%\nfor Friday: %s-%s" % (priced, lvl(lo_b), lvl(hi_b)), color=P["purple"],
            fontsize=cs.SIZES["tiny"], va="top", ha="left", family=cs.MONO)
    # route labels, spread
    ends.sort()
    ys = cs.spread_labels([e[0] for e in ends], (max(hist + [7415.64]) - min(f(10))) * 0.085)
    for (yv, key, name, col), yl in zip(ends, ys):
        r = R[key]
        ax.text(H + 0.25, yl, "%s  %d%%" % (name, r["share"]), color=P[col], fontsize=cs.SIZES["label"] + 1,
                fontweight="bold", va="bottom", ha="left")
        ax.text(H + 0.25, yl, "%d days · %d of %d episodes · median %s" % (
            r["days"], r["episodes"], ref["episodes"], cs.fmt_pct(r["median_end_pct"], 1)), color=P["subtitle"],
            fontsize=cs.SIZES["tiny"], va="top", ha="left", family=cs.MONO)
    ax.axvline(0, color=P["zero"], lw=1, zorder=1)
    top = max(hist + [7415.64, max(f(90))]) + 25
    bot = min(min(f(10)), lo_b) - 30
    ax.set_ylim(bot, top)
    ax.set_xlim(-19.5, H + 3.6)
    for x, t in ((0.5, "TONIGHT"), (1, ""), (3, "NEXT WEEK  ·  closed Thu 26")):
        if t:
            ax.text(x, top - 5, t, ha="center", va="top", fontsize=cs.SIZES["tiny"], color=P["subtitle"], fontweight="bold")
    ax.text(1, top - 5, "\n\nFRI · OPEX", ha="center", va="top", fontsize=cs.SIZES["tiny"], color=P["subtitle"],
            fontweight="bold")
    tk = [-19, -10] + xs
    tl = [T["date"][i0 - 19][5:], T["date"][i0 - 10][5:]] + [labels[0], "", ] + labels[2:]
    ax.set_xticks(tk)
    ax.set_xticklabels(tl, color=P["subtitle"], fontsize=cs.SIZES["tiny"])
    ax.tick_params(axis="y", colors=P["subtitle"], labelsize=cs.SIZES["tiny"])
    ax.yaxis.set_major_formatter(cs.plt.FuncFormatter(lambda v, _: lvl(v)))
    for t in ax.get_yticklabels():
        t.set_family(cs.MONO)
    ax.grid(axis="y", color=P["border"], lw=0.6)
    return cs.save(fig, out / "r1_routes.png")


def chart_horizons(doc, out, priced):
    c0, Hz, ref = doc["close"], doc["horizons"], doc["reference"]
    hw = Hz["next_week"]["high"]
    title = "How far each horizon has run after HIGH readings: next week's middle 80%% spans %s to %s" % (
        cs.fmt_pct(hw["p10"], 1), cs.fmt_pct(hw["p90"], 1))
    sub = ("Change from the %s close to the next open (tonight), Friday's close and the close five sessions on. Bright bars: "
           "%d past HIGH-checklist days; grey bars: all %d days since 2016. Thick = middle 50%%, thin = middle 80%%, dot = median." % (
               lvl(c0), Hz["tonight"]["high"]["n"], Hz["tonight"]["all"]["n"]))
    call = "Ranges are wider after HIGH readings at every horizon; the share that ended higher is no-call territory."
    fig, rects = cs.frame(title, sub, panels=3, tags=[("TONIGHT · NEXT OPEN", "cyan"), ("FRIDAY CLOSE · OPEX", "purple"),
                                                      ("NEXT WEEK · FRI 27", "yellow")], callout=call,
                          footer_right="daily_SPX.csv + daily_VIX.csv (Yahoo); Skylit vol file 19 Nov for the priced move")
    for rect, key in zip(rects, ("tonight", "friday", "next_week")):
        ax = cs.panel_axes(fig, rect, pad=(0.35, 0.55, 0.35, 0.85))
        h, al = Hz[key]["high"], Hz[key]["all"]
        lim = max(abs(h["p10"]), abs(h["p90"]), priced if key == "friday" else 0) * 1.35
        ax.set_xlim(-lim, lim)
        ax.set_ylim(0, 10)
        ax.axvline(0, color=P["zero"], lw=1)
        for y, s, col in ((6.6, h, P["white"]), (3.4, al, P["muted"])):
            ax.plot([s["p10"], s["p90"]], [y, y], color=col, lw=3, solid_capstyle="round")
            ax.plot([s["p25"], s["p75"]], [y, y], color=col, lw=13, solid_capstyle="butt", alpha=0.9)
            ax.scatter([s["median"]], [y], s=90, color=P["yellow"], zorder=5, edgecolor=P["canvas"], linewidth=1.5)
            ax.text(s["p10"], y - 0.75, cs.fmt_pct(s["p10"], 1), ha="center", va="top", color=col,
                    fontsize=cs.SIZES["tiny"], family=cs.MONO)
            ax.text(s["p90"], y - 0.75, cs.fmt_pct(s["p90"], 1), ha="center", va="top", color=col,
                    fontsize=cs.SIZES["tiny"], family=cs.MONO)
            ax.text(0, y + 0.85, "%s · %d%% higher · median %s" % ("HIGH days" if col == P["white"] else "all days",
                                                                 s["p_up"], cs.fmt_pct(s["median"], 2)),
                    ha="center", va="bottom", color=col, fontsize=cs.SIZES["tiny"], family=cs.MONO)
        if key == "friday":
            ax.plot([-priced, priced], [1.2, 1.2], color=P["purple"], lw=5, alpha=0.6, solid_capstyle="butt")
            ax.text(0, 0.95, "options price ±%.2f%%" % priced, ha="center", va="top", color=P["purple"],
                    fontsize=cs.SIZES["tiny"], family=cs.MONO)
        ax.text(0, 9.7, "in points from %s: %s to %s" % (lvl(c0), lvl(c0 * (1 + h["p10"] / 100)),
                                                         lvl(c0 * (1 + h["p90"] / 100))),
                ha="center", va="top", color=P["subtitle"], fontsize=cs.SIZES["tiny"], family=cs.MONO)
        ax.set_xticks([])
        ax.set_yticks([])
    return cs.save(fig, out / "r2_horizons.png")


if __name__ == "__main__":
    main()
