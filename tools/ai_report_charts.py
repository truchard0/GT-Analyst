#!/usr/bin/env python3
"""Charts for the AI report ("The Path of the AI Boom"), drawn in the house dark style with its flair.

    python tools/ai_report_charts.py [--out reports/charts/20261118_ai] [--theme dark|light]

Every chart names its data file in its footer. Data:
  - SMH closes: data/ai_prints_backtest/5y/prices_5y.csv
  - relative strength: data/ai_technical/stack_20261118.csv (tools/technical_stack.py)
  - dealer-gamma grids: data/ai_technical/heatmaps_20261117.json (tools/heatmap_extract.py, our Skylit maps only)
  - scenario and channel odds: data/timelines.json (as applied 18 Nov 2026)
  - revenue record: data/ai_prints_backtest/results_5y.json (the five-year pre-registered test)
The heatmap board also writes data/ai_technical/heatmap_reads_20261117.json: the per-name numbers the report quotes.
No trades, targets or sizes are drawn. A map taken before a company's report is left out (event-stale).
"""
import argparse
import csv
import datetime as dt
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from market_update import chartstyle as cs  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle  # noqa: E402
import matplotlib.dates as mdates  # noqa: E402

P = cs.P
MONO = cs.MONO


def F(v):
    return cs.fmt_big(v, digits=1)


# ================================================================ 1. the funding loop (diagram)
def funding_loop(out):
    fig, rects = cs.frame(
        "Buyers now fund the build: prepayments covered all of Nebius's new capex",
        "Where the money for one neocloud's GPUs came from in Q3 2026, and what Nvidia lends back. "
        "Nebius 6-K (12 Nov), Nvidia Q3 FY27 release and 10-Q.",
        tags=[("THE FUNDING LOOP", "purple")], badge=("$115.8bn", "Nvidia Q3 revenue"),
        callout="Tripwires: new AI loans priced above 10%  ·  prepayments below half of capex  ·  "
                "chip rents more than 15% off their highs",
        footer_right="Nebius 6-K 12 Nov 2026; Nvidia Q3 FY27 release and call 17 Nov; "
                     "research_notes/.../financing_chain.md")
    ax = cs.panel_axes(fig, rects[0], pad=(0.4, 0.3, 0.4, 0.75))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.axis("off")

    def node(cx, cy, w, h, head, lines, col, hot=False):
        ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h, boxstyle="round,pad=0,rounding_size=1.6",
                                    facecolor=P["node_" + col] if "node_" + col in P else P["node_grey"],
                                    edgecolor=P[col], lw=2.6 if hot else 1.6, zorder=3))
        ax.text(cx, cy + h / 2 - 3.2, head, ha="center", va="top", fontsize=15, fontweight="bold",
                color=P["title"], zorder=4)
        for i, ln in enumerate(lines):
            ax.text(cx, cy + h / 2 - 7.8 - i * 3.6, ln, ha="center", va="top", fontsize=12, color=P["text"],
                    family=MONO if any(ch.isdigit() for ch in ln) else None, zorder=4)

    def arrow(x0, y0, x1, y1, col, label, lx, ly, ls="-", ha="center"):
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>,head_length=9,head_width=5",
                                     color=P[col], lw=2.2, linestyle=ls, zorder=2,
                                     connectionstyle="arc3,rad=0.0"))
        ax.text(lx, ly, label, ha=ha, va="center", fontsize=12, color=P[col], fontweight="bold", zorder=4,
                linespacing=1.3, bbox=dict(boxstyle="round,pad=0.3", facecolor=P["panel"], edgecolor="none"))

    node(17, 46, 28, 16, "Buyers", ["labs and hyperscalers", "sign capacity, pay up front"], "cyan")
    node(50, 27, 30, 18, "Neocloud (Nebius)", ["Q3 capex about $7.3bn", "2026 capex about $27bn",
                                               "2027 capex $40-45bn"], "yellow", hot=True)
    node(83, 46, 28, 16, "Nvidia", ["Q3 revenue $115.8bn", "Q4 guide $130.0bn"], "green")
    node(50, 6.5, 30, 10, "Lenders", ["secured loans, converts near 70c"], "purple")
    arrow(24, 38, 34.3, 31.5, "cyan", "prepayments: over\n100% of Q3 deal capex", 20, 27.5)
    arrow(65.7, 31.5, 74, 37.5, "green", "GPU orders", 72, 30)
    arrow(88, 38, 66, 21, "green", "$2bn stake (8.3%)\nguarantees ~$118bn (25 Oct)", 87, 22, ls=(0, (5, 3)))
    arrow(50, 11.5, 50, 18, "purple", "$3.5bn secured facility", 64, 14.5, ha="left")
    cs.save(fig, out)


# ================================================================ 2. milestones on the chip index
MILESTONES = [
    ("2022-08-09", "CHIPS Act: about $53bn to build chips at home", "policy"),
    ("2022-10-07", "First US controls on AI chips and tools for China", "policy"),
    ("2022-11-30", "ChatGPT launches; the capex cycle starts", "demand"),
    ("2023-10-17", "Controls widened to the cut-down China chips", "policy"),
    ("2024-12-02", "Memory and more chip tools controlled", "policy"),
    ("2025-01-13", "Diffusion rule caps chips country by country", "policy"),
    ("2025-04-15", "China licenses rare earths; H20 needs licences", "policy"),
    ("2025-05-13", "Diffusion rule dropped; chips leak via third countries", "policy"),
    ("2025-10-30", "Busan truce: tariffs capped, mineral curbs paused", "policy"),
    ("2025-12-15", "Largest Taiwan blockade drills since 2022", "war"),
    ("2026-01-15", "25% tariff on advanced chips", "policy"),
    ("2026-02-28", "Iran war starts; index bottoms 30 Mar", "war"),
    ("2026-06-22", "Index peaks near 669, before capex does", "demand"),
    ("2026-07-14", "Power auction at its cap, 6.8 GW short; Texas pauses", "money"),
    ("2026-09-16", "Brent over $100, 10-year over 5%, Fed hikes", "war"),
    ("2026-09-23", "Truce extended only to 10 Jan 2027", "policy"),
    ("2026-10-20", "AI-credit selloff; Alphabet cash flow negative", "money"),
    ("2026-11-03", "Democrats win Congress; local votes curb data centres", "money"),
    ("2026-11-12", "Nvidia's chief executive resigns", "money"),
    ("2026-11-16", "Remote-access rule announced (in force 19 Nov)", "policy"),
]
CH_COL = {"policy": "cyan", "war": "orange", "money": "purple", "demand": "yellow"}
CH_NAME = {"policy": "export rules, tariffs, truce", "war": "war, Taiwan, rates",
           "money": "credit, power, politics", "demand": "demand and price"}


def load_closes(ticker):
    rows = [r for r in csv.DictReader(open(ROOT / "data/ai_prints_backtest/5y/prices_5y.csv", encoding="utf-8"))
            if r["ticker"] == ticker]
    d = [dt.date.fromisoformat(r["date"]) for r in rows]
    c = np.array([float(r["close"]) for r in rows])
    return d, c


def milestones(out):
    d, c = load_closes("SMH")
    keep = [i for i, x in enumerate(d) if x >= dt.date(2022, 6, 1)]
    d, c = [d[i] for i in keep], c[keep]
    i26 = [i for i, x in enumerate(d) if x.year == 2026]
    lo = min(i26, key=lambda i: c[i])
    hi = max(i26, key=lambda i: c[i])
    last = len(c) - 1
    off = c[last] / c[hi] - 1
    rise = c[hi] / c[lo] - 1
    fig, rects = cs.frame(
        "The chip index rose %d%% from its war low, then gave back %d%% when the bill came due"
        % (round(rise * 100), round(-off * 100)),
        "SMH daily close, June 2022 to %s, with the twenty policy, war and money events that shaped "
        "the AI trade. Numbered dots sit on the close of each event's date." % d[-1].strftime("%d %b %Y").lstrip("0"),
        panels=2, panel_widths=[1.75, 1], tags=[("THE CHIP INDEX", "white"), ("WHAT HAPPENED", "purple")],
        badge=(cs.fmt_pct(off * 100, 0), "SMH off its high"),
        footer_right="data/ai_prints_backtest/5y/prices_5y.csv; BIS rules 2022-25; constraints_policy.md; "
                     "data/timelines.json")
    ax = cs.panel_axes(fig, rects[0], pad=(0.95, 0.6, 0.35, 0.85))
    ax.fill_between(d, c, c.min() * 0.9, color=P["white"], alpha=0.05, lw=0)
    ax.plot(d, c, color=P["price"], lw=1.6)
    ax.set_ylim(c.min() * 0.9, c.max() * 1.08)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.yaxis.set_major_formatter(lambda v, _: "%d" % v)
    for lab in ax.get_yticklabels():
        lab.set_family(MONO)
    dix = {x: i for i, x in enumerate(d)}
    for n, (ds, _, ch) in enumerate(MILESTONES, 1):
        day = dt.date.fromisoformat(ds)
        j = min(range(len(d)), key=lambda i: abs((d[i] - day).days))
        ax.plot([d[j]], [c[j]], "o", ms=15, color=P[CH_COL[ch]], zorder=5, markeredgecolor=P["panel"],
                markeredgewidth=1.5)
        ax.text(d[j], c[j], str(n), ha="center", va="center", fontsize=8.5, fontweight="bold", color="#0a0a0a",
                family=MONO, zorder=6)
    for i, lab, va, dy in ((lo, "war low %d" % c[lo], "top", -16), (hi, "peak %d" % c[hi], "bottom", 14),
                           (last, "%s %d" % (d[last].strftime("%d %b").lstrip("0"), c[last]), "top", -16)):
        ax.annotate(lab, (d[i], c[i]), xytext=(0, dy), textcoords="offset points", ha="center", va=va,
                    fontsize=12, color=P["title"], fontweight="bold", family=MONO)
    # the event list
    x, y, w, h = rects[1]
    fw, fh = fig.get_size_inches()
    top = y + h - 0.85 / fh
    step = (h - 1.6 / fh) / len(MILESTONES)
    for n, (ds, ev, ch) in enumerate(MILESTONES, 1):
        yy = top - (n - 0.5) * step
        fig.text(x + 0.22 / fw, yy, "%2d" % n, color=P[CH_COL[ch]], fontsize=11, fontweight="bold", family=MONO,
                 va="center")
        fig.text(x + 0.58 / fw, yy, dt.date.fromisoformat(ds).strftime("%b %y"), color=P["muted"], fontsize=10,
                 family=MONO, va="center")
        fig.text(x + 1.28 / fw, yy, ev, color=P["text"], fontsize=10.5, va="center")
    for k, ch in enumerate(("policy", "war", "money", "demand")):
        fig.text(x + (0.22 + (k % 2) * 2.55) / fw, y + (0.5 - (k // 2) * 0.26) / fh, "● " + CH_NAME[ch],
                 color=P[CH_COL[ch]], fontsize=10, va="center")
    cs.save(fig, out)
    return {"low": (str(d[lo]), float(c[lo])), "high": (str(d[hi]), float(c[hi])), "last": float(c[last]),
            "rise_pct": rise * 100, "off_pct": off * 100}


# ================================================================ 3. channels by layer
CHANNELS = [  # (channel, prints, capex, financing, limits, price, odds or date) - odds from data/timelines.json
    ("Export controls (19 Nov rule)", 0, 1, 1, 2, 1, "licence clock ends ~17 Feb"),
    ("US-China truce and minerals", 0, 1, 0, 2, 1, "truce rolls 10 Jan: 66%"),
    ("Taiwan (if it happens)", 2, 2, 2, 2, 2, "PLA action by 30 Jun: 10%"),
    ("Gulf war and oil", 0, 0, 1, 1, 1, "US campaign by 3 Jan: 18%"),
    ("Fed, yields and the dollar", 1, 1, 2, 0, 2, "9 Dec hike: 93%"),
    ("The financing chain", 1, 2, 2, 0, 2, "holds to 31 Mar: 82%"),
    ("Power and local politics", 0, 2, 1, 2, 0, "PJM auction in December"),
    ("Chip tariffs", 0, 1, 0, 1, 0, "25% in force"),
]
LAYERS = ["Revenue", "Capex", "Credit", "Limits", "Price"]


def channels(out):
    n_print = sum(1 for r in CHANNELS if r[1] == 2)
    fig, rects = cs.frame(
        "Only %s of eight forces is a main threat to this winter's revenue: Taiwan" % ("one" if n_print == 1 else n_print),
        "Each geopolitical channel by the layer of the AI trade it hits, as of 18 Nov 2026. "
        "Big dot = main channel, small = secondary, faint ring = none.",
        tags=[("CHANNEL  X  LAYER", "purple")], badge=("1 / 8", "forces that hit revenue"),
        footer_right="data/timelines.json (odds as of 18 Nov 2026); reports/20261118_tape-note-gulf-oil-fed.md; "
                     "constraints_policy.md")
    ax = cs.panel_axes(fig, rects[0], pad=(0.4, 0.35, 0.4, 0.8))
    ax.set_xlim(0, 100)
    ax.set_ylim(len(CHANNELS) + 0.2, -1.1)
    ax.axis("off")
    xs = [36, 44.5, 53, 61.5, 70]
    for k, lab in enumerate(LAYERS):
        ax.text(xs[k], -0.75, lab, ha="center", va="center", fontsize=13, fontweight="bold", color=P["title"])
    ax.text(99, -0.75, "Our odds or next date", ha="right", va="center", fontsize=13, fontweight="bold",
            color=P["title"])
    for i, row in enumerate(CHANNELS):
        hot = row[0].startswith("Taiwan")
        if i % 2 == 0:
            ax.add_patch(Rectangle((0.5, i - 0.5), 99, 1, facecolor=P["free"], edgecolor="none", zorder=0))
        ax.text(1.5, i, row[0], va="center", fontsize=13.5, color=P["yellow"] if hot else P["text"],
                fontweight="bold" if hot else "normal")
        for k in range(5):
            s = row[1 + k]
            if s == 0:
                ax.plot(xs[k], i, "o", ms=9, mfc="none", mec=P["zero"], mew=1.2)
            else:
                col = P["yellow"] if (k == 0 and s == 2) else P["cyan"] if s == 2 else P["purple"]
                ax.plot(xs[k], i, "o", ms=24 if s == 2 else 13, color=col, alpha=1 if s == 2 else 0.85)
        ax.text(99, i, row[6], ha="right", va="center", fontsize=12.5, color=P["subtitle"], family=MONO)
    ax.add_patch(Rectangle((xs[0] - 3.6, -0.5), 7.2, len(CHANNELS), fill=False, edgecolor=P["yellow"], lw=1.4,
                           ls=(0, (4, 3))))
    cs.save(fig, out)


# ================================================================ 4. relative strength
NAMES = {"META": "Meta", "AMZN": "Amazon", "AVGO": "Broadcom", "TSM": "TSMC", "MU": "Micron", "NVDA": "Nvidia",
         "ORCL": "Oracle", "SMH": "Chip index"}


def relative_strength(out, stack="data/ai_technical/stack_20261118.csv"):
    rows = {r["ticker"]: r for r in csv.DictReader(open(ROOT / stack, encoding="utf-8"))}
    pdate = dt.date.fromisoformat(next(iter(rows.values()))["price_date"]).strftime("%d %b %Y").lstrip("0")
    data = [(t, float(rows[t]["rs_vs_smh_3m_pct"]), float(rows[t]["pct_vs_200d"]), float(rows[t]["pct_off_52w_high"]))
            for t in ("META", "AMZN", "AVGO", "TSM", "MU", "NVDA") if t in rows and rows[t]["rs_vs_smh_3m_pct"]]
    data.sort(key=lambda r: -r[1])
    top, bot = data[0], data[-1]
    fig, rects = cs.frame(
        "Over three months %s beat the chip index by %d points; %s lagged it by %d"
        % (NAMES[top[0]], round(top[1]), NAMES[bot[0]], round(-bot[1])),
        "Return relative to SMH, three months to the %s close, percentage points. Right: distance from " % pdate +
        
        "the 200-day average and from the 52-week high.",
        panels=2, panel_widths=[1.7, 1], tags=[("RELATIVE STRENGTH", "white"), ("WHERE EACH SITS", "white")],
        badge=("%+.1f" % top[1], "%s vs SMH, pts" % NAMES[top[0]]),
        footer_right="data/ai_technical/stack_20261118.csv (tools/technical_stack.py on prices_5y.csv)")
    ax = cs.panel_axes(fig, rects[0], pad=(1.6, 0.4, 0.9, 0.85))
    ys = np.arange(len(data))
    vals = [r[1] for r in data]
    ax.barh(ys, vals, height=0.62, color=[P["green"] if v >= 0 else P["red"] for v in vals])
    ax.axvline(0, color=P["zero"], lw=1.2)
    ax.set_yticks(ys)
    ax.set_yticklabels([NAMES[r[0]] for r in data], fontsize=14, color=P["title"])
    ax.set_xticks([])
    ax.invert_yaxis()
    span = max(abs(v) for v in vals)
    ax.set_xlim(min(0, min(vals)) - span * 0.3, max(vals) + span * 0.18)
    for y, v in zip(ys, vals):
        ax.text(v + (span * 0.02 if v >= 0 else -span * 0.02), y, "%+.1f" % v, va="center",
                ha="left" if v >= 0 else "right", fontsize=14, fontweight="bold", family=MONO,
                color=P["green"] if v >= 0 else P["red"])
    ax2 = cs.panel_axes(fig, rects[1], pad=(0.3, 0.4, 0.3, 0.85))
    ax2.axis("off")
    ax2.set_ylim(len(data) - 0.5, -1.2)
    ax2.set_xlim(0, 10)
    ax2.text(3.2, -0.9, "vs 200-day", ha="center", fontsize=12, color=P["subtitle"])
    ax2.text(7.6, -0.9, "off 52w high", ha="center", fontsize=12, color=P["subtitle"])
    for y, r in zip(ys, data):
        ax2.text(3.2, y, cs.fmt_pct(r[2], 0), ha="center", va="center", fontsize=15, family=MONO, fontweight="bold",
                 color=P["green"] if r[2] >= 0 else P["red"])
        ax2.text(7.6, y, cs.fmt_pct(r[3], 0), ha="center", va="center", fontsize=15, family=MONO,
                 color=P["text"])
    cs.save(fig, out)
    return data


# ================================================================ 5. the heatmap board (one page)
BOARD = ["MU", "META", "AMZN", "SMH", "AVGO", "CRWV"]
INDEX_BOARD = [("SPXW", "SPX", "S&P 500 (SPX)", 0.025), ("QQQ", "QQQ", "Nasdaq-100 (QQQ)", 0.03)]
FULL = {"NVDA": "Nvidia", "MU": "Micron", "META": "Meta", "AMZN": "Amazon", "SMH": "Chip index (SMH)", "AVGO": "Broadcom",
        "CRWV": "CoreWeave"}


def heat_cmap():
    if cs.THEME["name"] == "dark":
        stops = [(0.0, "#c9a6ff"), (0.18, "#8f5bff"), (0.38, "#4a2390"), (0.5, "#121016"), (0.62, "#5c4a12"),
                 (0.82, "#d9a91f"), (1.0, "#ffe680")]
    else:
        stops = [(0.0, "#4b1f9e"), (0.2, "#7c4dff"), (0.4, "#cdb8ff"), (0.5, "#f7f7f7"), (0.6, "#ffe9a8"),
                 (0.8, "#f2b705"), (1.0, "#a87b00")]
    return LinearSegmentedColormap.from_list("gt_gamma", stops)


def read_grid(t):
    k = np.array(t["strikes"], float)
    g = np.array(t["gamma"], float)
    spot = float(t["spot"])
    tot = np.abs(g).sum() or 1.0
    row = g.sum(axis=1)
    near2 = np.abs(k / spot - 1) <= 0.02
    near5 = np.abs(k / spot - 1) <= 0.05
    r0, c0 = np.unravel_index(np.argmax(np.abs(g)), g.shape)
    above = [i for i in range(len(k)) if k[i] > spot and row[i] > 0]
    below = [i for i in range(len(k)) if k[i] < spot and row[i] > 0]
    shorts = [i for i in range(len(k)) if row[i] < 0]
    pick = lambda idx: (float(k[max(idx, key=lambda i: row[i])]), float(max(row[i] for i in idx))) if idx else None
    return {
        "ticker": t["ticker"], "spot": spot, "snapshot": t["snapshot_ts"], "batch": t["source_batch"],
        "expiries": t["expiries"],
        "front_share_pct": float(np.abs(g[:, 0]).sum() / tot * 100),
        "net_pm2_share_pct": float(g[near2].sum() / tot * 100),
        "net_pm5_share_pct": float(g[near5].sum() / tot * 100),
        "regime_pm2": "flat" if abs(g[near2].sum()) < 0.03 * tot else ("long" if g[near2].sum() > 0 else "short"),
        "king": {"strike": float(k[r0]), "expiry": t["expiries"][c0], "value": float(g[r0, c0]),
                 "pct_from_spot": float((k[r0] / spot - 1) * 100)},
        "largest_long_row_above": pick(above), "largest_long_row_below": pick(below),
        "largest_short_row": (float(k[min(shorts, key=lambda i: row[i])]), float(min(row[i] for i in shorts)))
        if shorts else None,
    }


def index_grids(date="2026-11-17"):
    """S&P 500 and Nasdaq-100 grids: the 17:30 ET overnight Skylit map when it exists, else the 16:00 ET close map
    with the same-day (expired) expiry dropped."""
    from market_update import data as D
    snap = D.load_overnight(date)
    src = "overnight map 17:30 ET"
    if snap is None:
        snap = D.load_live(date, "1600")
        src = "close map 16:00 ET"
    out = {}
    for sym, key, name, win in INDEX_BOARD:
        m = snap.get(sym)
        if m is None:
            continue
        keep = [j for j, e in enumerate(m.expiries) if e > date][:5]
        w = np.abs(m.strikes / m.spot - 1) <= win
        out[key] = {"ticker": key, "name": name, "spot": float(m.spot), "expiries": [m.expiries[j] for j in keep],
                    "strikes": [float(x) for x in m.strikes[w]], "gamma": m.matrix[w][:, keep].tolist(),
                    "snapshot_ts": snap.label, "source_batch": "Skylit %s (%s)" % (src, sym)}
    return out, src


def heatmap_board(out, reads_out, date="2026-11-17"):
    tag = date.replace("-", "")
    day = dt.date.fromisoformat(date).strftime("%d %b %Y").lstrip("0")
    hm_path = "data/ai_technical/heatmaps_%s.json" % tag
    hm = json.load(open(ROOT / hm_path, encoding="utf-8"))
    by = {t["ticker"]: t for t in hm["tickers"]}
    stocks = [tk for tk in ["NVDA"] + BOARD if tk in by and not by[tk].get("event_stale")]
    left_out = [FULL.get(tk, tk) for tk in ["NVDA"] + BOARD if tk in by and by[tk].get("event_stale")]
    reads = {tk: read_grid(by[tk]) for tk in stocks}
    idx, isrc = index_grids(date)
    by.update(idx)
    for k, v in idx.items():
        FULL[k] = v["name"]
    ireads = {k: read_grid(v) for k, v in idx.items()}
    friday = min(e for r in reads.values() for e in r["expiries"])
    fri_lab = dt.date.fromisoformat(friday).strftime("%a %d %b").replace(" 0", " ")
    n_front = sum(1 for r in reads.values() if r["king"]["expiry"] == friday)
    med_front = float(np.median([r["front_share_pct"] for r in reads.values()]))
    regs = {r["regime_pm2"] for r in ireads.values()}
    lead = ("Both indices sit in %s gamma" % regs.pop()) if len(regs) == 1 else "The indices split"
    open_names = [FULL[tk].split(" (")[0] for tk in stocks if "09:30" in by[tk].get("source_batch", "")]
    size = (13.6, 17.0)
    fig, rects = cs.frame(
        "%s; %d%% of the AI-stock maps expire on %s" % (lead, round(med_front), dt.date.fromisoformat(friday).strftime("%A")),
        "Dealer gamma by strike and expiry. Indices: the %s %s. Stocks: the %s close%s. %s's expiry holds the "
        "largest stock position on %d of %d maps.%s"
        % (day[:-5], isrc, day[:-5], (" (%s: 09:30 ET open)" % ", ".join(open_names)) if open_names else "",
           fri_lab.split()[0], n_front, len(stocks),
           (" Left out: %s (map predates its report)." % ", ".join(left_out)) if left_out else ""),
        panels=1, size=size, tags=None, badge=("%d%%" % round(med_front), "expires %s" % fri_lab),
        callout="Our record: the largest strike did not pull price (55 days, n=165)  ·  big strikes reversed price no more than any strike  ·  "
                "gamma sign: no next-day edge (324 sessions)",
        footer_right="Skylit maps via " + hm_path,
        snapshot="%s 16:00 ET" % day)
    fw, fh = fig.get_size_inches()
    x0, y0, W, H = rects[0]
    order_all = [k for k in ("SPX", "QQQ") if k in idx] + stocks
    cols = 2
    show_share = (len(order_all) + 2) <= 10
    rows_n = -(-(len(order_all) + 1 + (1 if show_share else 0)) // cols)
    gx, gy = 0.22 / fw, 0.22 / fh
    tw = (W - gx * (cols + 1)) / cols
    th = (H - gy * (rows_n + 1)) / rows_n
    cmap = heat_cmap()
    exp_lab = lambda e: dt.date.fromisoformat(e).strftime("%d %b").lstrip("0")
    tiles = [(i % cols, i // cols) for i in range(cols * rows_n)]
    allreads = dict(ireads, **reads)
    for n, tk in enumerate(order_all):
        t, r = by[tk], allreads[tk]
        cx, cy = tiles[n]
        tx = x0 + gx + cx * (tw + gx)
        ty = y0 + H - (cy + 1) * (th + gy)
        cs._round_box(fig, tx, ty, tw, th, fc=P["canvas"], ec=P["border"], lw=1.0, r_in=0.08, z=0)
        k = np.array(t["strikes"], float)
        g = np.array(t["gamma"], float)
        spot = float(t["spot"])
        # rows: the 4 strikes nearest spot plus the biggest by |cell|, max 12, high strike on top
        near = sorted(range(len(k)), key=lambda i: abs(k[i] - spot))[:4]
        chosen = set(near)
        for i in sorted(range(len(k)), key=lambda i: -np.max(np.abs(g[i]))):
            if len(chosen) >= 11:
                break
            chosen.add(i)
        rows_sel = sorted(chosen, key=lambda i: -k[i])
        M, ks = g[rows_sel], k[rows_sel]
        vmax = float(np.max(np.abs(M))) or 1.0
        Z = np.sign(M) * (np.abs(M) / vmax) ** 0.55
        ax = fig.add_axes([tx + 0.72 / fw, ty + 0.25 / fh, tw - 1.05 / fw, th - 1.0 / fh])
        ax.imshow((Z + 1) / 2, cmap=cmap, vmin=0, vmax=1, aspect="auto", interpolation="nearest")
        for rr in range(len(ks) + 1):
            ax.axhline(rr - 0.5, color=P["canvas"], lw=1.6)
        for cc in range(M.shape[1] + 1):
            ax.axvline(cc - 0.5, color=P["canvas"], lw=1.6)
        for s in ax.spines.values():
            s.set_visible(False)
        ax.tick_params(length=0)
        ax.set_yticks(range(len(ks)))
        ax.set_yticklabels([("{:,.0f}".format(v) if v >= 1000 else cs.fmt_level(v, 1 if v < 100 and v != int(v) else 0))
                            for v in ks], fontsize=8.5,
                           family=MONO, color=P["subtitle"])
        ax.set_xticks(range(M.shape[1]))
        ax.set_xticklabels([exp_lab(e) for e in t["expiries"]], fontsize=8.5, color=P["text"])
        ax.xaxis.tick_top()
        r0, c0 = np.unravel_index(np.argmax(np.abs(M)), M.shape)
        ax.add_patch(Rectangle((c0 - 0.5, r0 - 0.5), 1, 1, fill=False, edgecolor=P["white"], lw=2.2, zorder=5))
        ax.text(c0, r0, F(M[r0, c0]), ha="center", va="center", fontsize=7.5, fontweight="bold", family=MONO,
                color="#141414" if (M[r0, c0] > 0 or abs(Z[r0, c0]) > 0.8) else P["title"], zorder=6)
        if ks[-1] <= spot <= ks[0]:
            ysp = float(np.interp(spot, ks[::-1], np.arange(len(ks))[::-1]))
            ax.axhline(ysp, color=P["cyan"], lw=1.8, ls=(0, (4, 2)), zorder=6)
        ax.set_xlim(-0.5, M.shape[1] - 0.5)
        ax.set_ylim(len(ks) - 0.5, -0.5)
        # tile header: name, price, regime chip
        reg = r["regime_pm2"]
        fig.text(tx + 0.16 / fw, ty + th - 0.2 / fh, FULL[tk], fontsize=12.5, fontweight="bold", color=P["title"],
                 va="top")
        fig.text(tx + tw - 0.16 / fw, ty + th - 0.2 / fh,
                 "%s  ·  %s gamma" % (cs.fmt_level(spot, 2), reg), fontsize=10, family=MONO,
                 color={"long": P["green"], "short": P["red"]}.get(reg, P["subtitle"]), va="top", ha="right")
        fig.text(tx + 0.16 / fw, ty + 0.08 / fh, "%s %d%% of map  ·  king %s %s"
                 % ("front expiry" if tk not in idx else "%s expiry" % exp_lab(t["expiries"][0]),
                    round(r["front_share_pct"]), "{:,.0f}".format(r["king"]["strike"]) if r["king"]["strike"] >= 1000
                    else cs.fmt_level(r["king"]["strike"]), exp_lab(r["king"]["expiry"])),
                 fontsize=8.5, color=P["muted"], family=MONO, va="bottom")
    nxt = len(order_all)
    if show_share:
        share_tile(fig, tiles[nxt], reads, (x0, y0, W, H), (tw, th, gx, gy), fri_lab)
        nxt += 1
    key_tile(fig, tiles[nxt], (x0, y0, W, H), (tw, th, gx, gy), cmap)
    cs.save(fig, out)
    json.dump({"generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
               "source": hm_path, "index_source": isrc, "note": "shares are of total |gamma| on the "
               "map shown; vendor units, compare within a ticker only", "reads": reads, "index_reads": ireads},
              open(reads_out, "w", encoding="utf-8"), indent=1)
    return {"stocks": reads, "indices": ireads}


def share_tile(fig, tile, reads, frame_rect, geom, fri_lab):
    fw, fh = fig.get_size_inches()
    x0, y0, W, H = frame_rect
    tw, th, gx, gy = geom
    cx, cy = tile
    tx = x0 + gx + cx * (tw + gx)
    ty = y0 + H - (cy + 1) * (th + gy)
    cs._round_box(fig, tx, ty, tw, th, fc=P["canvas"], ec=P["border"], lw=1.0, r_in=0.08, z=0)
    fig.text(tx + 0.16 / fw, ty + th - 0.2 / fh, "Share of each stock map expiring %s" % fri_lab, fontsize=12.5,
             fontweight="bold", color=P["title"], va="top")
    ax = fig.add_axes([tx + 1.25 / fw, ty + 0.3 / fh, tw - 1.8 / fw, th - 0.85 / fh])
    order = sorted(reads.values(), key=lambda r: -r["front_share_pct"])
    ys = np.arange(len(order))
    vals = [r["front_share_pct"] for r in order]
    ax.barh(ys, vals, height=0.6, color=P["cyan"])
    ax.barh(ys, [100 - v for v in vals], left=vals, height=0.6, color=P["free"])
    ax.set_yticks(ys)
    ax.set_yticklabels([FULL[r["ticker"]].split(" (")[0] for r in order], fontsize=10, color=P["text"])
    ax.set_xticks([])
    ax.set_xlim(0, 100)
    ax.invert_yaxis()
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
    for y, v in zip(ys, vals):
        ax.text(v + 1.5, y, "%d%%" % round(v), va="center", fontsize=10, family=MONO, fontweight="bold",
                color=P["title"])


def key_tile(fig, tile, frame_rect, geom, cmap):
    fw, fh = fig.get_size_inches()
    x0, y0, W, H = frame_rect
    tw, th, gx, gy = geom
    cx, cy = tile
    tx = x0 + gx + cx * (tw + gx)
    ty = y0 + H - (cy + 1) * (th + gy)
    cs._round_box(fig, tx, ty, tw, th, fc=P["canvas"], ec=P["yellow"], lw=1.2, r_in=0.08, z=0)
    fig.text(tx + 0.16 / fw, ty + th - 0.2 / fh, "How to read the maps", fontsize=12.5, fontweight="bold",
             color=P["yellow"], va="top")
    lines = [
        ("Yellow", "dealers long gamma: hedging tends to damp moves"),
        ("Purple", "dealers short gamma: hedging can extend moves"),
        ("White box", "the largest cell on the map (the king)"),
        ("Cyan dash", "the price when the map was taken"),
        ("Units", "the vendor's own; compare within a name only"),
        ("Status", "a map of positioning, not a forecast"),
    ]
    for i, (a, b) in enumerate(lines):
        yy = ty + th - (0.55 + i * 0.27) / fh
        fig.text(tx + 0.18 / fw, yy, a, fontsize=10, fontweight="bold", color=P["title"], va="top")
        fig.text(tx + 1.25 / fw, yy, b, fontsize=10, color=P["text"], va="top")
    cax = fig.add_axes([tx + 0.2 / fw, ty + 0.36 / fh, tw - 0.4 / fw, 0.13 / fh])
    cax.imshow(np.linspace(0, 1, 256).reshape(1, -1), cmap=cmap, aspect="auto")
    cax.set_xticks([0, 128, 255])
    cax.set_xticklabels(["short", "0", "long"], fontsize=8.5, color=P["subtitle"])
    cax.set_yticks([])
    for s in cax.spines.values():
        s.set_visible(False)
    cax.tick_params(length=0)


# ================================================================ 6. scenarios
def scenarios(out):
    rows = [
        ("Base: Gulf calm, Fed hikes, truce rolls, no Taiwan action", 0.41, None,
         "A slower 2027: capex growth under 25% is the likeliest path"),
        ("US-China truce lapses on 10 Jan", 0.34, None,
         "Minerals, transceivers, Southeast Asian neoclouds hit first; ~60% if a big Chinese buyer of Iranian oil is sanctioned"),
        ("Gulf war ends by purchase by 31 Mar", 0.20, None, "Slight relief in rates; Gulf AI builds resume"),
        ("US strike campaign or ground operation in Iran by 3 Jan", 0.18, None,
         "Reaches AI only through core inflation, the Fed and Taiwan's energy bill"),
        ("PLA action on Taiwan by 30 Jun 2027", 0.10, [("quarantine", 0.045), ("gray-zone fire", 0.04),
                                                       ("invasion", 0.015)],
         "Odds of a 2027 capex decline rise from 20% to 30-85%"),
    ]
    fig, rects = cs.frame(
        "About 41% on a slower 2027; the truce is the biggest risk and Taiwan the tail",
        "Geopolitical scenarios for the AI trade to mid-2027, our odds as of 18 Nov 2026. They overlap, so they "
        "do not sum to 100%. Base = 0.80 × 0.93 × 0.93 × 0.66 × 0.90.",
        tags=[("SCENARIOS", "yellow")], badge=("41%", "base case"),
        footer_right="data/timelines.json; reports/desk/20261118_mechanism-sweep-ai.md")
    ax = cs.panel_axes(fig, rects[0], pad=(0.45, 0.35, 0.45, 0.85))
    ax.set_xlim(0, 100)
    ax.set_ylim(len(rows) - 0.3, -0.7)
    ax.axis("off")
    scale = 60 / 0.5
    for i, (name, p, parts, does) in enumerate(rows):
        ax.text(0.5, i - 0.3, name, fontsize=14, fontweight="bold", color=P["title"], va="center")
        ax.add_patch(Rectangle((0.5, i - 0.08), 0.5 * scale * 1.0 + 0, 0.2, facecolor=P["free"], edgecolor="none"))
        if parts:
            x = 0.5
            for j, (lab, v) in enumerate(parts):
                col = [P["orange"], P["red"], "#ff2a2a"][j]
                ax.add_patch(Rectangle((x, i - 0.08), v * scale, 0.2, facecolor=col, edgecolor=P["panel"], lw=1.2))
                x += v * scale
            ax.text(x + 1.2, i + 0.02, "10%", fontsize=15, fontweight="bold", family=MONO, color=P["title"],
                    va="center")
            ax.text(x + 7.5, i + 0.02, "quarantine 4.5 · gray-zone 4 · invasion 1.5", fontsize=11.5, family=MONO,
                    color=P["subtitle"], va="center")
        else:
            col = P["yellow"] if i == 0 else P["cyan"]
            ax.add_patch(Rectangle((0.5, i - 0.08), p * scale, 0.2, facecolor=col, edgecolor="none"))
            ax.text(0.5 + p * scale + 1.2, i + 0.02, "%d%%" % round(p * 100), fontsize=15, fontweight="bold",
                    family=MONO, color=P["title"], va="center")
        ax.text(0.5, i + 0.33, does, fontsize=12, color=P["subtitle"], va="center")
    cs.save(fig, out)


# ================================================================ 7. revenue record
REV = [("Y1  Nov 21-Nov 22", 1.60, 1.08, 1.55), ("Y2  Nov 22-Nov 23", 1.88, 1.97, 2.62),
       ("Y3  Nov 23-Nov 24", 2.12, 2.07, 3.10), ("Y4  Nov 24-Nov 25", 1.75, 2.04, 2.26),
       ("Y5  Nov 25-Nov 26", 0.96, 2.99, 3.25)]


def revenue_record(out):
    beats = sum(1 for _, m, c, _ in REV if m < c)
    fig, rects = cs.frame(
        "Our revenue number beat consensus in %d of 5 years, most widely in the latest" % beats,
        "Median absolute miss on reported revenue, % of the actual, by year: 117 reports from Nvidia, Broadcom, "
        "Micron, TSMC, Amazon and Meta. Rules committed before the data was gathered.",
        tags=[("OUR RECORD", "yellow")], badge=("1.5%", "median miss, 5 yrs"),
        callout="Our record: median miss 1.5% vs consensus 2.0% and company guide 2.4% (117 reports)  ·  "
                "consensus beat us on next-quarter guides every year",
        footer_right="data/ai_prints_backtest/results_5y.json (tools/ai_prints_5y.py; PREREG_5Y.md)")
    ax = cs.panel_axes(fig, rects[0], pad=(2.4, 0.45, 0.6, 1.05))
    ser = [("our number", 1, P["yellow"]), ("consensus", 2, P["subtitle"]), ("naive (last quarter's growth)", 3,
                                                                              P["zero"])]
    h = 0.26
    for i, row in enumerate(REV):
        for j, (lab, k, col) in enumerate(ser):
            y = i + (j - 1) * h
            ax.barh(y, row[k], height=h * 0.88, color=col)
            ax.text(row[k] + 0.04, y, "%.1f%%" % row[k], va="center", fontsize=11.5 if j == 0 else 10.5,
                    family=MONO, fontweight="bold" if j == 0 else "normal",
                    color=P["yellow"] if j == 0 else P["subtitle"])
    ax.set_yticks(range(len(REV)))
    ax.set_yticklabels([r[0] for r in REV], fontsize=13, color=P["title"], family=MONO)
    ax.set_xticks([])
    ax.set_xlim(0, 3.8)
    ax.invert_yaxis()
    lx = 0.0
    for lab, _, c in ser:
        ax.text(lx, 1.035, "■ " + lab, transform=ax.transAxes, color=c if c != P["zero"] else P["muted"],
                fontsize=12, va="bottom", fontweight="bold")
        lx += 0.24
    cs.save(fig, out)


# ================================================================ 8. signposts
SIGNS = [
    ("19 Nov", "Xi-Trump-Putin meeting at APEC, Shenzhen; rule in force", "chips, Iran, Taiwan", False),
    ("27 Nov", "China's gallium and germanium pause lapses", "first US-China lever", False),
    ("29-30 Nov", "OPEC+ quotas; the Iran fork resolves", "Gulf path", False),
    ("1-2 Dec", "Nvidia hearings in the House", "export policy", False),
    ("9 Dec", "Fed decision; Broadcom results", "hike 93%  ·  ours $35.3bn", True),
    ("~10 Dec", "TSMC November revenue", "the TSMC call", False),
    ("9-14 Dec", "Oracle fiscal Q2", "ours $21.3bn", False),
    ("15-23 Dec", "Micron fiscal Q1 (date unconfirmed)", "ours $72.1bn", False),
    ("December", "PJM capacity auction", "the power limit", False),
    ("10 Jan", "US-China truce and rare-earth cliff", "truce rolls 66%", True),
    ("14/21 Jan", "TSMC Q4 and first 2027 capex guide", "ours $54.6bn", False),
    ("27 Jan-4 Feb", "Hyperscaler Q4 and 2027 capex guides", "the 2027 fork", True),
    ("~17 Feb", "Remote-access licence clock ends", "SE Asian neoclouds", False),
    ("24 Feb-3 Mar", "Nvidia fiscal Q4; annual report", "ours $137.3bn  ·  guarantees", False),
    ("31 Mar", "Hormuz state; financing chain", "credit holds 82%", False),
    ("30 Jun", "Taiwan, Fed and chip-index branches resolve", "PLA action 10%", False),
]


def signposts(out):
    fig, rects = cs.frame(
        "Three dates decide the path: the 9 Dec Fed, the 10 Jan truce cliff, late-January capex guides",
        "Signposts from 19 Nov 2026 to 30 Jun 2027 and what each one bears on. Most company dates are estimates.",
        size=(15, 11.5), tags=[("SIGNPOSTS", "yellow")], badge=("3", "dates that decide"),
        footer_right="data/timelines.json; research_notes/AI trade forecasting framework/catalyst_calendar_consensus.md")
    ax = cs.panel_axes(fig, rects[0], pad=(0.4, 0.3, 0.4, 0.8))
    ax.set_xlim(0, 100)
    n = len(SIGNS)
    ax.set_ylim(n - 0.4, -0.6)
    ax.axis("off")
    spine = 17
    ax.plot([spine, spine], [-0.3, n - 0.7], color=P["zero"], lw=2)
    for i, (when, ev, bears, big) in enumerate(SIGNS):
        if big:
            ax.add_patch(FancyBboxPatch((0.6, i - 0.42), 98.8, 0.84, boxstyle="round,pad=0,rounding_size=0.4",
                                        facecolor=P["node_yellow"], edgecolor=P["yellow"], lw=1.2,
                                        mutation_aspect=0.05))
        ax.text(spine - 2, i, when, ha="right", va="center", fontsize=12.5, family=MONO,
                color=P["yellow"] if big else P["subtitle"], fontweight="bold" if big else "normal")
        ax.plot(spine, i, "o", ms=13 if big else 8, color=P["yellow"] if big else P["cyan"],
                markeredgecolor=P["panel"], markeredgewidth=1.5, zorder=4)
        ax.text(spine + 2.5, i, ev, va="center", fontsize=13.5, color=P["title"], fontweight="bold" if big else "normal")
        ax.text(99, i, bears, ha="right", va="center", fontsize=12, family=MONO, color=P["subtitle"])
    cs.save(fig, out)


# ================================================================ 9. Anthropic's compute commitments (S-1/A)
ANT_COMMIT = [  # (provider, low $bn, high $bn, note) - S-1/A Amendment No. 3, filed 17 Nov 2026
    ("Google (TPUs)", 121.3, 271.3, "at least; $125-150bn more est. 2028-31"),
    ("Nvidia GPUs via SpaceXAI", 120.5, 120.5, "up to; cancellable after early 2027"),
    ("Amazon (Trainium)", 110.0, 110.0, "at least; May 2026 to Apr 2036"),
    ("Microsoft", 47.2, 49.2, "Nov 2026 to Jun 2033"),
    ("Nscale", 44.6, 44.6, "up to; depends on Nscale's own financing"),
    ("Lambda", 41.3, 41.3, "to 2034"),
    ("AMD (Helios)", 20.0, 20.0, "more than"),
]


def anthropic_commitments(out):
    fig, rects = cs.frame(
        "Anthropic has signed about $900bn of commitments, nearly all of it for compute",
        "Compute commitments by provider from the IPO filing (S-1/A No. 3, 17 Nov 2026), $bn. About $452bn falls "
        "due by 2030 and $71bn in the next twelve months, against a run-rate revenue of about $81bn.",
        tags=[("THE BUYER AT THE TOP", "purple")], badge=("$81bn", "run-rate revenue, 31 Oct"),
        callout="Most of the counterparties are also its investors: Amazon owns 14.7% and Google 13.7%; Google and "
                "Nvidia each buy $10bn in the placement",
        footer_right="Anthropic S-1/A Amendment No. 3 (sec.gov), filed 17 Nov 2026")
    ax = cs.panel_axes(fig, rects[0], pad=(3.2, 0.4, 3.9, 0.8))
    ys = np.arange(len(ANT_COMMIT))
    for y, (name, lo, hi, note) in zip(ys, ANT_COMMIT):
        ax.barh(y, lo, height=0.58, color=P["purple"] if "Nvidia" in name or name in ("Nscale", "Lambda") else P["cyan"])
        if hi > lo:
            ax.barh(y, hi - lo, left=lo, height=0.58, color=P["free"], edgecolor=P["cyan"], lw=1.2, ls=(0, (3, 2)))
        ax.text((hi if hi > lo else lo) + 4, y, ("$%.0f-%.0fbn" % (lo, hi)) if hi > lo else "$%.0fbn" % lo, va="center",
                fontsize=13, family=MONO, fontweight="bold", color=P["title"])
        ax.text(1.02, y, note, transform=ax.get_yaxis_transform(), va="center", fontsize=10.5, color=P["subtitle"])
    ax.set_yticks(ys)
    ax.set_yticklabels([r[0] for r in ANT_COMMIT], fontsize=13, color=P["title"])
    ax.set_xticks([])
    ax.set_xlim(0, 330)
    ax.invert_yaxis()
    ax.text(0, 1.03, "■ cloud and chip makers' own capacity", transform=ax.transAxes, color=P["cyan"], fontsize=11, fontweight="bold")
    ax.text(0.55, 1.03, "■ GPU capacity through chip renters", transform=ax.transAxes, color=P["purple"], fontsize=11, fontweight="bold")
    cs.save(fig, out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="reports/charts/20261118_ai")
    ap.add_argument("--theme", default="dark")
    ap.add_argument("--only", default="")
    ap.add_argument("--map-date", default="2026-11-18", help="dealer-gamma map day for the heatmap board")
    a = ap.parse_args()
    cs.apply(a.theme)
    out = ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)
    jobs = {
        "01_funding_loop": lambda p: funding_loop(p),
        "02_milestones": lambda p: milestones(p),
        "03_channels": lambda p: channels(p),
        "04_relative_strength": lambda p: relative_strength(p),
        "05_heatmap_board": lambda p: heatmap_board(
            p, ROOT / ("data/ai_technical/heatmap_reads_%s.json" % a.map_date.replace("-", "")), a.map_date),
        "06_scenarios": lambda p: scenarios(p),
        "07_revenue_record": lambda p: revenue_record(p),
        "08_signposts": lambda p: signposts(p),
        "09_anthropic_commitments": lambda p: anthropic_commitments(p),
    }
    for name, fn in jobs.items():
        if a.only and a.only not in name:
            continue
        res = fn(out / (name + ".png"))
        print(name, "ok", json.dumps(res, default=str)[:300] if res else "")


if __name__ == "__main__":
    main()
