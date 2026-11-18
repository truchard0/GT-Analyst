"""Chart catalogue for the market update (house style from chartstyle.py; every chart returns its key numbers).

  levels_ladder      key-levels ladder: green/red gamma lines (weight = size, dashed = small), fast/slow/free band tints
                     with net gamma per band, coloured price labels left, role labels right, mini gamma columns.
                     With `path=` it becomes the intraday chart on the morning map (high/low/now with clock times).
  before_after       same expiry, two snapshots: grey = earlier, colour = now, "a -> b" on the movers; change panel.
  gamma_heatmap      strike x expiry dealer-gamma heatmap (purple = short gamma, yellow = long), spot line, king outlined.
  vanna_bars         single-name vanna by strike with spot, extremes labelled, how-to-read panel.
  route_tree         scenario routes: cyan root -> question -> tinted branches, each with a measured base rate and n,
                     or "no measured odds".
  earnings_strip     past report-day moves vs the options-implied move, report timing, gap-chance base rate.

No chart here ever shows a target, a trade, a hedge, a size or a payoff.
"""
import datetime as dt

import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
import matplotlib.dates as mdates

try:
    from . import chartstyle as cs
except ImportError:
    import chartstyle as cs

P = cs.P
F = cs.fmt_big


# ================================================================ helpers
def select_levels(strikes, vals, spot, window_pct=0.02, max_levels=8, min_frac=0.15, min_gap_pct=0.0011,
                  must=()):
    """Pick the strikes worth drawing: largest |gamma| first, a minimum spacing, plus any `must` strikes."""
    w = np.abs(strikes / spot - 1) <= window_pct
    idx = [i for i in np.where(w)[0]]
    if not idx:
        return []
    vmax = max(abs(vals[i]) for i in idx) or 1.0
    order = sorted(idx, key=lambda i: -abs(vals[i]))
    chosen = []
    gap = min_gap_pct * spot
    for k in must:
        hits = [i for i in idx if abs(strikes[i] - k) < 1e-9]
        if hits:
            chosen.append(hits[0])
    for i in order:
        if len(chosen) >= max_levels:
            break
        if i in chosen or abs(vals[i]) < min_frac * vmax:
            continue
        if any(abs(strikes[i] - strikes[j]) < gap for j in chosen):
            continue
        chosen.append(i)
    return sorted(chosen, key=lambda i: strikes[i])


def band_nets(strikes, vals, levels_idx):
    """Net gamma of the strikes strictly between consecutive drawn levels."""
    out = []
    for a, b in zip(levels_idx, levels_idx[1:]):
        lo, hi = strikes[a], strikes[b]
        sel = (strikes > lo) & (strikes < hi)
        out.append((lo, hi, float(vals[sel].sum())))
    return out


def band_style(net, vmax):
    if net <= -0.30 * vmax:
        return "fast", P["fast_heavy"], P["red"]
    if net <= -0.08 * vmax:
        return "fast", P["fast_light"], P["red"]
    if net >= 0.30 * vmax:
        return "slow", P["slow_heavy"], P["green"]
    if net >= 0.08 * vmax:
        return "slow", P["slow_light"], P["green"]
    return "free", P["free"], P["subtitle"]


def _mini_column(fig, rect_ax, strikes, vals, ylim, title, spot, n_label=2, colour_pos=None, colour_neg=None):
    ax = fig.add_axes(rect_ax)
    ax.set_facecolor("none")
    for s in ax.spines.values():
        s.set_visible(False)
    sel = (strikes >= ylim[0]) & (strikes <= ylim[1])
    ks, vs = strikes[sel], vals[sel]
    if len(ks) > 1:
        step = np.median(np.diff(np.sort(ks)))
    else:
        step = 1.0
    h = step * 0.72
    cols = [colour_pos or P["green"] if v >= 0 else colour_neg or P["red"] for v in vs]
    ax.barh(ks, vs, height=h, color=cols, edgecolor="none")
    vmax = max(np.max(np.abs(vs)) if len(vs) else 1, 1e-9)
    ax.set_xlim(-vmax * 1.9, vmax * 1.9)
    ax.set_ylim(*ylim)
    ax.axvline(0, color=P["zero"], lw=1)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(title, fontsize=cs.SIZES["small"] + 1, fontweight="bold", color=P["text"], pad=8)
    # label the extremes only
    if len(vs):
        done = []
        for i in list(np.argsort(vs)[:n_label]) + list(np.argsort(vs)[-n_label:]):
            v = vs[i]
            if abs(v) < 0.35 * vmax or any(abs(ks[i] - y0) < 0.03 * (ylim[1] - ylim[0]) for y0 in done):
                continue
            done.append(ks[i])
            ha = "right" if v < 0 else "left"
            ax.text(v + (-1 if v < 0 else 1) * vmax * 0.06, ks[i], F(v), fontsize=cs.SIZES["tiny"], color=cols[i],
                    ha=ha, va="center", fontweight="bold")
    ax.axhline(spot, color=P["white"], lw=0.8, ls=(0, (3, 2)), alpha=0.6)
    ax.text(0.5, -0.025, MINUS_NEG_POS(), transform=ax.transAxes, ha="center", va="top", fontsize=cs.SIZES["tiny"],
            color=P["subtitle"])
    return ax


def MINUS_NEG_POS():
    return "%s short  ·  long +" % cs.MINUS


# ================================================================ 1/2. key-levels ladder (and intraday on the map)
def levels_ladder(out_path, m, vals, *, title, subtitle, tag, callout, footer_right, snapshot, unit_note,
                  window_pct=0.02, max_levels=8, last=None, last_label="last", prev_close=None, path=None,
                  mini=None, side_table=None, decimals=0, must=(), roles=None, morning_band=None, x_end=None,
                  min_frac=0.15, min_gap_pct=0.0011, ylim_pad=0.0018):
    """m: SymMap; vals: per-strike gamma (same order as m.strikes) for the expiry shown.
    mini: list of (title, vals) mini columns at right. side_table: (title, [(left, right, colour)]) column at right.
    roles: {strike: role text} overrides. Returns dict of the drawn levels and bands."""
    strikes = m.strikes
    spot = m.spot if last is None else last
    lv = select_levels(strikes, vals, spot, window_pct, max_levels, min_frac, min_gap_pct, must)
    if not lv:
        raise ValueError("no levels in window")
    win = np.abs(strikes / spot - 1) <= window_pct
    vmax = float(np.max(np.abs(vals[win]))) or 1.0
    bands = band_nets(strikes, vals, lv)
    right_cols = (len(mini) if mini else 0) + (1 if side_table else 0)
    pw = [3.2, 1.0 * right_cols] if right_cols else None
    fig, rects = cs.frame(title, subtitle, panels=1, tags=[tag], callout=callout, footer_right=footer_right,
                          snapshot=snapshot)
    rect = rects[0]
    fw, fh = fig.get_size_inches()
    x, y, w, h = rect
    main_w = w * ((0.58 if side_table else 0.66) if right_cols else 1.0)
    pad_l = 1.55 if path is not None else 0.4
    pad_r = 2.9 if path is not None else 0.3
    ax = fig.add_axes([x + pad_l / fw, y + 0.62 / fh, main_w - (pad_l + pad_r) / fw, h - (0.62 + 1.62) / fh])
    ax.set_facecolor("none")
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)

    ys = [strikes[i] for i in lv] + [spot] + ([prev_close] if prev_close else [])
    if path:
        ys += [p for _, p in path]
    rng = max(ys) - min(ys)
    pad = max(rng * 0.09, spot * ylim_pad)
    ylim = (min(ys) - pad, max(ys) + pad)
    ax.set_ylim(*ylim)

    if path is not None:
        t0 = path[0][0].replace(hour=9, minute=30)
        t1 = x_end or path[0][0].replace(hour=16, minute=0)
        X0, X1 = mdates.date2num(t0), mdates.date2num(t1)
        ax.set_xlim(X0, X1)
        ax.xaxis.set_major_locator(mdates.HourLocator(byhour=range(10, 17), tz=t0.tzinfo))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%-I:%M" if False else "%H:%M", tz=t0.tzinfo))
        lx0, lx1 = X0, X1
        ax.tick_params(axis="x", colors=P["subtitle"], labelsize=cs.SIZES["small"])
    else:
        ax.set_xlim(0, 1)
        ax.set_xticks([])
        lx0, lx1 = 0.20, 0.62
    ax.set_yticks([])

    # bands
    for lo, hi, net in bands:
        kind, colour, tcol = band_style(net, vmax)
        ax.add_patch(Rectangle((lx0, lo), lx1 - lx0, hi - lo, facecolor=colour, edgecolor="none", zorder=1,
                               alpha=0.6 if path is not None else 1.0))
    # band labels where there is room
    min_gap = (ylim[1] - ylim[0]) * 0.045
    obstacles = [spot] + ([prev_close] if prev_close is not None else [])
    for lo, hi, net in bands:
        kind, colour, tcol = band_style(net, vmax)
        # the largest free gap inside the band, away from the last/prior-close lines
        cuts = sorted([lo, hi] + [o for o in obstacles if lo < o < hi])
        glo, ghi = max(zip(cuts, cuts[1:]), key=lambda g: g[1] - g[0])
        if ghi - glo < 2.1 * min_gap:
            continue
        word = {"fast": "fast zone", "slow": "slow zone", "free": "little gamma"}[kind]
        txt = "%s · net %s" % (word, F(net)) if kind != "free" else "%s between" % word
        bx = (lx0 + lx1) / 2 if path is None else lx0 + (lx1 - lx0) * 0.015
        ax.text(bx, (glo + ghi) / 2, txt, ha="center" if path is None else "left", va="center",
                fontsize=cs.SIZES["small"], color=tcol, fontweight="bold", zorder=3,
                bbox=dict(boxstyle="round,pad=0.25", facecolor=P["panel"], edgecolor="none", alpha=0.75)
                if path is not None else None)

    # level lines
    roles = roles or {}
    big_pos = max(lv, key=lambda i: vals[i])
    big_neg = min(lv, key=lambda i: vals[i])
    label_y = [strikes[i] for i in lv]
    label_txt, label_col, label_w = [], [], []
    for i in lv:
        v = vals[i]
        col = P["green"] if v >= 0 else P["red"]
        frac = abs(v) / vmax
        lw = 1.6 + 4.2 * frac
        ls = "-" if frac >= 0.35 else (0, (5, 3))
        ax.plot([lx0, lx1], [strikes[i], strikes[i]], color=col, lw=lw, ls=ls, zorder=4, solid_capstyle="butt")
        k = strikes[i]
        if k in roles:
            role = roles[k]
        elif i == big_pos and v > 0:
            role = "largest + strike"
        elif i == big_neg and v < 0:
            role = "largest %s strike" % cs.MINUS
        else:
            role = "+ gamma" if v >= 0 else "%s gamma" % cs.MINUS
        label_txt.append("%s  %s" % (role, F(v)))
        label_col.append(col)
        label_w.append("bold" if frac >= 0.35 else "normal")
    # last / prev close lines
    if prev_close is not None:
        ax.plot([lx0, lx1], [prev_close, prev_close], color=P["subtitle"], lw=1.4, ls=(0, (1, 2.5)), zorder=4)
    if path is None:
        ax.plot([lx0, lx1], [spot, spot], color=P["white"], lw=2.2, ls=(0, (6, 3)), zorder=5)

    # price labels (left) and role labels (right), spread to avoid overlap
    all_y = label_y + [spot] + ([prev_close] if prev_close is not None else [])
    pos = cs.spread_labels(all_y, min_gap * 0.9)
    n = len(label_y)
    lab_left_x = lx0 - (0.012 if path is None else 0.0)
    for j, i in enumerate(lv):
        yv = pos[j]
        txt = cs.fmt_level(strikes[i], decimals)
        if path is None:
            ax.text(lab_left_x, yv, txt, ha="right", va="center", fontsize=cs.SIZES["level"], fontweight="bold",
                    color=label_col[j], zorder=6)
            ax.text(lx1 + 0.015, yv, label_txt[j], ha="left", va="center", fontsize=cs.SIZES["label"],
                    color=label_col[j], fontweight=label_w[j], zorder=6)
        else:
            ax.text(-0.012, yv, txt, transform=ax.get_yaxis_transform(), ha="right", va="center",
                    fontsize=cs.SIZES["level"], fontweight="bold", color=label_col[j], zorder=6)
            ax.text(1.012, yv, label_txt[j], transform=ax.get_yaxis_transform(), ha="left", va="center",
                    fontsize=cs.SIZES["small"], color=label_col[j], fontweight=label_w[j], zorder=6)
    # spot label
    sy = pos[n]
    spot_txt = cs.fmt_level(spot, 2)
    if path is None:
        ax.text(lab_left_x, sy, spot_txt, ha="right", va="center", fontsize=cs.SIZES["level"], fontweight="bold",
                color=P["white"], zorder=6)
        ax.text(lx1 + 0.015, sy, last_label, ha="left", va="center", fontsize=cs.SIZES["label"], fontweight="bold",
                color=P["white"], zorder=6)
    if prev_close is not None:
        py = pos[n + 1]
        tx = cs.fmt_level(prev_close, 2)
        if path is None:
            ax.text(lab_left_x, py, tx, ha="right", va="center", fontsize=cs.SIZES["label"], color=P["subtitle"],
                    zorder=6)
            ax.text(lx1 + 0.015, py, "prior close", ha="left", va="center", fontsize=cs.SIZES["label"],
                    color=P["subtitle"], zorder=6)
        else:
            ax.text(-0.012, py, tx, transform=ax.get_yaxis_transform(), ha="right", va="center",
                    fontsize=cs.SIZES["label"], color=P["subtitle"], zorder=6)
            ax.text(1.012, py, "prior close", transform=ax.get_yaxis_transform(), ha="left", va="center",
                    fontsize=cs.SIZES["small"], color=P["subtitle"], zorder=6)

    found = {}
    if path is not None:
        xs = [mdates.date2num(t) for t, _ in path]
        ps = [p for _, p in path]
        ax.plot(xs, ps, color=P["price"], lw=2.0, zorder=7, solid_joinstyle="round")
        ih, il = int(np.argmax(ps)), int(np.argmin(ps))
        found = {"high": (path[ih][0], ps[ih]), "low": (path[il][0], ps[il]), "now": (path[-1][0], ps[-1])}
        span = ylim[1] - ylim[0]
        for key, (t, p), dy in (("high", found["high"], 4), ("low", found["low"], -4)):
            xt = mdates.date2num(t)
            right = (xt - X0) / (X1 - X0) < 0.7
            ax.plot([xt], [p], "o", ms=9, color=P["yellow"], zorder=8, markeredgewidth=0)
            ax.annotate("%s %s %s" % (cs.fmt_level(p, 2), key, t.strftime("%H:%M")), (xt, p),
                        xytext=(14 if right else -14, dy), textcoords="offset points",
                        ha="left" if right else "right", va="bottom" if dy > 0 else "top",
                        fontsize=cs.SIZES["label"], fontweight="bold", color=P["white"], zorder=9,
                        bbox=dict(boxstyle="round,pad=0.2", facecolor=P["panel"], edgecolor="none", alpha=0.8))
        t, p = found["now"]
        ax.plot([mdates.date2num(t)], [p], "o", ms=9, color=P["yellow"], zorder=8, markeredgewidth=0)
        ax.annotate("%s %s" % (cs.fmt_level(p, 2), last_label), (mdates.date2num(t), p), xytext=(10, 0),
                    textcoords="offset points", ha="left", va="center", fontsize=cs.SIZES["label"],
                    fontweight="bold", color=P["white"], zorder=9,
                    bbox=dict(boxstyle="round,pad=0.2", facecolor=P["panel"], edgecolor="none", alpha=0.8))
        if morning_band:
            lo_b, hi_b = morning_band
            ax.add_patch(Rectangle((lx0, lo_b), (lx1 - lx0) * 0.006, hi_b - lo_b, facecolor=P["cyan"],
                                   edgecolor="none", zorder=6))

    # legend rows (top of panel)
    lw_ = (main_w - 0.5 / fw) if right_cols else (w - 0.5 / fw)
    lax = fig.add_axes([x + 0.25 / fw, y + h - 0.98 / fh, lw_, 0.22 / fh])
    lax.axis("off")
    items = [("line", P["green"], "positive gamma"), ("line", P["red"], "negative gamma"),
             ("dash", P["subtitle"], "thicker = larger, dashed = small")]
    items.append(("dash", P["white"], last_label if path is None else "price, 1-min samples"))
    if prev_close is not None:
        items.append(("dot", P["subtitle"], "prior close"))
    cs.legend_row(lax, items, y=0.5, x0=0.0, size=cs.SIZES["tiny"] + 0.5, gap=0.025)
    lax2 = fig.add_axes([x + 0.25 / fw, y + h - 1.26 / fh, lw_, 0.22 / fh])
    lax2.axis("off")
    cs.legend_row(lax2, [("patch", P["fast_heavy"], "fast zone: net short gamma between"),
                         ("patch", P["slow_heavy"], "slow zone: net long gamma between"),
                         ("patch", P["free"], "little gamma between")], y=0.5, x0=0.0,
                  size=cs.SIZES["tiny"] + 0.5, gap=0.025)
    fig.text(x + w - 0.25 / fw, y + h - 0.3 / fh, unit_note, ha="right", va="top", fontsize=cs.SIZES["tiny"],
             color=P["muted"])

    # right-hand columns
    if right_cols:
        cx = x + main_w
        colw = (w - main_w - 0.35 / fw) / right_cols
        k = 0
        for title_m, mv in (mini or []):
            _mini_column(fig, [cx + k * colw + 0.12 / fw, y + 0.62 / fh, colw - 0.3 / fw, h - (0.62 + 1.62) / fh],
                         strikes, mv, ylim, title_m, spot)
            k += 1
        if side_table:
            ttl, rows = side_table
            tx = cx + k * colw + 0.1 / fw
            ty = y + h - 1.35 / fh
            fig.text(tx, ty, ttl, fontsize=cs.SIZES["small"] + 1, fontweight="bold", color=P["text"], va="top",
                     linespacing=1.3)
            yy = ty - (0.32 * (ttl.count("\n") + 1) + 0.2) / fh
            for left, right, colour in rows:
                fig.text(tx, yy, left, fontsize=cs.SIZES["small"], color=P.get(colour, colour), va="top",
                         fontweight="bold")
                fig.text(tx, yy - 0.26 / fh, right, fontsize=cs.SIZES["tiny"] + 0.5, color=P["subtitle"],
                         va="top", linespacing=1.25)
                yy -= (0.62 + 0.2 * right.count("\n")) / fh
    cs.save(fig, out_path)
    return {"levels": [(float(strikes[i]), float(vals[i])) for i in lv], "bands": bands, "vmax": vmax, **found}


# ================================================================ 3. before vs now (same expiry)
def before_after(out_path, strikes, before, now, spot, *, title, subtitle, callout, footer_right, snapshot,
                 label_before, label_now, window_pct=0.02, n_rows=14, decimals=0, unit_note=""):
    w = np.abs(strikes / spot - 1) <= window_pct
    idx = [i for i in np.where(w)[0]]
    idx = sorted(idx, key=lambda i: -max(abs(before[i]), abs(now[i])))[:n_rows]
    idx = sorted(idx, key=lambda i: strikes[i])
    ks = strikes[idx]
    b, nw = before[idx], now[idx]
    ch = nw - b
    fig, rects = cs.frame(title, subtitle, panels=2, tags=[("GAMMA BY STRIKE", "cyan"), ("CHANGE SINCE " +
                                                                                        label_before.upper(),
                                                                                        "purple")],
                          callout=callout, footer_right=footer_right, snapshot=snapshot, size=cs.WIDE_SIZE,
                          panel_widths=[1.15, 1])
    ypos = np.arange(len(ks))
    vmax = max(np.max(np.abs(b)), np.max(np.abs(nw)), 1e-9)
    ax = cs.panel_axes(fig, rects[0], pad=(1.45, 1.0, 0.45, 1.05))
    ax.barh(ypos + 0.21, b, height=0.38, color=P["muted"], edgecolor="none")
    ax.barh(ypos - 0.21, nw, height=0.38, color=[P["green"] if v >= 0 else P["red"] for v in nw], edgecolor="none")
    ax.axvline(0, color=P["zero"], lw=1.2)
    ax.set_yticks(ypos)
    ax.set_yticklabels([cs.fmt_level(k, decimals) for k in ks], fontsize=cs.SIZES["label"], color=P["subtitle"])
    ax.set_xticks([])
    ax.set_xlim(-vmax * 1.55, vmax * 1.55)
    ax.set_ylim(-0.7, len(ks) - 0.3)
    movers = sorted(range(len(ks)), key=lambda i: -abs(ch[i]))[:6]
    for i in movers:
        end = max(b[i], nw[i], 0) if (nw[i] >= 0 or b[i] >= 0) and max(b[i], nw[i]) > 0 and abs(max(b[i], nw[i])) >= abs(min(b[i], nw[i], 0)) else min(b[i], nw[i], 0)
        ha = "left" if end >= 0 else "right"
        off = vmax * 0.04 * (1 if end >= 0 else -1)
        ax.text(end + off, ypos[i], "%s → %s" % (F(b[i]), F(nw[i])), ha=ha, va="center",
                fontsize=cs.SIZES["small"], color=P["text"])
    sp_y = np.interp(spot, ks, ypos) if ks[0] <= spot <= ks[-1] else None
    if sp_y is not None:
        ax.axhline(sp_y, color=P["white"], lw=1, ls=(0, (3, 2)), alpha=0.7)
        ax.text(vmax * 1.52, sp_y - 0.1, "spot %s" % cs.fmt_level(spot, 2), fontsize=cs.SIZES["tiny"],
                color=P["white"], va="top", ha="right")
    fw, fh = fig.get_size_inches()
    x, y, wd, h = rects[0]
    fig.text(x + 0.3 / fw, y + 0.32 / fh, "Grey = %s.  Colour = %s: green positive, red negative." %
             (label_before, label_now), fontsize=cs.SIZES["small"], color=P["subtitle"], va="bottom")
    # change panel
    ax2 = cs.panel_axes(fig, rects[1], pad=(1.45, 1.0, 0.45, 1.05))
    cmax = max(np.max(np.abs(ch)), 1e-9)
    ax2.barh(ypos, ch, height=0.55, color=[P["green"] if v >= 0 else P["red"] for v in ch], edgecolor="none")
    ax2.axvline(0, color=P["zero"], lw=1.2)
    ax2.set_yticks(ypos)
    ax2.set_yticklabels([cs.fmt_level(k, decimals) for k in ks], fontsize=cs.SIZES["label"], color=P["subtitle"])
    ax2.set_xticks([])
    ax2.set_xlim(-cmax * 1.6, cmax * 1.6)
    ax2.set_ylim(-0.7, len(ks) - 0.3)
    for i in sorted(range(len(ks)), key=lambda i: -abs(ch[i]))[:4]:
        v = ch[i]
        ax2.text(v + cmax * 0.05 * (1 if v >= 0 else -1), ypos[i], F(v), ha="left" if v >= 0 else "right",
                 va="center", fontsize=cs.SIZES["small"], fontweight="bold",
                 color=P["green"] if v >= 0 else P["red"])
    if sp_y is not None:
        ax2.axhline(sp_y, color=P["white"], lw=1, ls=(0, (3, 2)), alpha=0.7)
    x2, y2, w2, h2 = rects[1]
    fig.text(x2 + 0.3 / fw, y2 + 0.32 / fh, "Change in each strike's gamma: green = more long gamma, red = less. %s"
             % unit_note, fontsize=cs.SIZES["small"], color=P["subtitle"], va="bottom")
    cs.save(fig, out_path)
    return {"rows": [(float(k), float(bb), float(nn)) for k, bb, nn in zip(ks, b, nw)]}


# ================================================================ 4. strike x expiry heatmap
def _heat_cmap():
    if cs.THEME["name"] == "dark":
        stops = [(0.0, "#c9a6ff"), (0.18, "#8f5bff"), (0.38, "#4a2390"), (0.5, "#121016"), (0.62, "#5c4a12"),
                 (0.82, "#d9a91f"), (1.0, "#ffe680")]
    else:
        stops = [(0.0, "#4b1f9e"), (0.2, "#7c4dff"), (0.4, "#cdb8ff"), (0.5, "#f7f7f7"), (0.6, "#ffe9a8"),
                 (0.8, "#f2b705"), (1.0, "#a87b00")]
    return LinearSegmentedColormap.from_list("gt_gamma", stops)


def gamma_heatmap(out_path, strikes, expiries, matrix, spot, *, title, subtitle, callout, footer_right, snapshot,
                  tag=("DEALER GAMMA  STRIKE X EXPIRY", "cyan"), window_pct=0.02, max_rows=22, decimals=0,
                  unit_note="", exp_labels=None, banner=None, must=()):
    w = np.abs(strikes / spot - 1) <= window_pct
    idx = [i for i in np.where(w)[0]]
    score = {i: np.max(np.abs(matrix[i])) for i in idx}
    near = sorted(idx, key=lambda i: abs(strikes[i] - spot))[:4]
    chosen = set(near) | {i for i in idx if strikes[i] in must}
    for i in sorted(idx, key=lambda i: -score[i]):
        if len(chosen) >= max_rows:
            break
        chosen.add(i)
    rows = sorted(chosen, key=lambda i: -strikes[i])  # high strike at top
    M = matrix[rows][:, :len(expiries)]
    ks = strikes[rows]
    vmax = float(np.max(np.abs(M))) or 1.0
    Z = np.sign(M) * (np.abs(M) / vmax) ** 0.55
    fig, rects = cs.frame(title, subtitle, panels=1, tags=[tag], callout=callout, footer_right=footer_right,
                          snapshot=snapshot)
    ax = cs.panel_axes(fig, rects[0], pad=(1.55, 0.95, 2.9, 1.1))
    cmap = _heat_cmap()
    ax.imshow((Z + 1) / 2, cmap=cmap, vmin=0, vmax=1, aspect="auto", interpolation="nearest")
    # cell grid lines (panel colour) for a tiled look
    for r in range(len(ks) + 1):
        ax.axhline(r - 0.5, color=P["panel"], lw=2.2)
    for c in range(M.shape[1] + 1):
        ax.axvline(c - 0.5, color=P["panel"], lw=2.2)
    ax.set_yticks(range(len(ks)))
    ax.set_yticklabels([cs.fmt_level(k, decimals) for k in ks], fontsize=cs.SIZES["small"] + 0.5,
                       color=P["subtitle"])
    ax.set_xticks(range(M.shape[1]))
    labs = exp_labels or [dt.date.fromisoformat(e).strftime("%a %d %b") for e in expiries]
    ax.set_xticklabels(labs, fontsize=cs.SIZES["small"] + 0.5, color=P["text"])
    ax.xaxis.tick_top()
    # annotate the big cells
    for r in range(M.shape[0]):
        for c in range(M.shape[1]):
            v = M[r, c]
            if abs(v) >= 0.18 * vmax:
                light = (abs(Z[r, c]) > 0.55 and v > 0 or abs(Z[r, c]) > 0.8) and cs.THEME["name"] == "dark"
                col = "#141414" if light else P["title"]
                if cs.THEME["name"] == "light":
                    col = "#ffffff" if abs(Z[r, c]) > 0.6 else P["title"]
                ax.text(c, r, F(v), ha="center", va="center", fontsize=cs.SIZES["tiny"] + 0.5, color=col,
                        fontweight="bold")
    # king
    r0, c0 = np.unravel_index(np.argmax(np.abs(M)), M.shape)
    ax.add_patch(Rectangle((c0 - 0.5, r0 - 0.5), 1, 1, fill=False, edgecolor=P["white"], lw=3, zorder=5))
    # spot line between the bracketing rows
    if ks[-1] <= spot <= ks[0]:
        yspot = float(np.interp(spot, ks[::-1], np.arange(len(ks))[::-1]))
        ax.axhline(yspot, color=P["cyan"], lw=2, ls=(0, (5, 3)), zorder=6)
        ax.text(M.shape[1] - 0.45, yspot, "  spot %s" % cs.fmt_level(spot, 2), color=P["cyan"], va="center",
                ha="left", fontsize=cs.SIZES["small"], fontweight="bold", clip_on=False)
    ax.set_xlim(-0.5, M.shape[1] - 0.5)
    ax.set_ylim(len(ks) - 0.5, -0.5)
    # legend: colour scale
    fw, fh = fig.get_size_inches()
    x, y, wd, h = rects[0]
    cax = fig.add_axes([x + wd - 0.95 / fw, y + 1.2 / fh, 0.2 / fw, h - 2.6 / fh])
    grad = np.linspace(1, 0, 256).reshape(-1, 1)
    cax.imshow(grad, cmap=cmap, aspect="auto")
    cax.set_xticks([])
    cax.set_yticks([0, 128, 255])
    cax.set_yticklabels(["long", "0", "short"], fontsize=cs.SIZES["tiny"], color=P["subtitle"])
    cax.yaxis.tick_right()
    for s in cax.spines.values():
        s.set_visible(False)
    fig.text(x + 0.3 / fw, y + 0.3 / fh, "Yellow = dealers long gamma, purple = short; shade on a signed "
             "square-root-like scale. White box = largest cell shown (the king). %s" % unit_note,
             fontsize=cs.SIZES["small"], color=P["subtitle"], va="bottom")
    if banner:
        ax.text(0.5, 0.5, banner, transform=ax.transAxes, ha="center", va="center", fontsize=22,
                fontweight="bold", color=P["red"], alpha=0.9, rotation=0,
                bbox=dict(boxstyle="round,pad=0.6", facecolor=P["panel"], edgecolor=P["red"], lw=2))
    cs.save(fig, out_path)
    return {"king": (float(ks[r0]), expiries[c0], float(M[r0, c0])), "rows": [float(k) for k in ks]}


# ================================================================ 5. single-name vanna by strike
def vanna_bars(out_path, strikes, vals, spot, *, ticker, title, subtitle, callout, footer_right, snapshot,
               expiry_note, window_pct=0.15, n_rows=22, decimals=1, how_to=None):
    w = np.abs(strikes / spot - 1) <= window_pct
    idx = [i for i in np.where(w)[0] if vals[i] != 0]
    idx = sorted(idx, key=lambda i: -abs(vals[i]))[:n_rows]
    idx = sorted(idx, key=lambda i: strikes[i])
    ks, vs = strikes[idx], vals[idx]
    fig, rects = cs.frame(title, subtitle, panels=2, tags=[("%s VANNA BY STRIKE" % ticker, "purple"),
                                                           ("HOW TO READ IT", "white")],
                          callout=callout, footer_right=footer_right, snapshot=snapshot, size=cs.WIDE_SIZE,
                          panel_widths=[2.3, 1])
    ax = cs.panel_axes(fig, rects[0], pad=(1.35, 0.95, 0.5, 1.05))
    ypos = np.arange(len(ks))
    cols = [P["green"] if v >= 0 else P["red"] for v in vs]
    ax.barh(ypos, vs, height=0.62, color=cols, edgecolor="none")
    vmax = max(np.max(np.abs(vs)), 1e-9)
    ax.set_xlim(-vmax * 1.45, vmax * 1.45)
    ax.axvline(0, color=P["zero"], lw=1.2)
    ax.set_yticks(ypos)
    ax.set_yticklabels([cs.fmt_level(k, decimals if k != round(k) else 0) for k in ks],
                       fontsize=cs.SIZES["label"] - 0.5, color=P["subtitle"])
    ax.set_xticks([])
    ax.set_ylim(-0.7, len(ks) - 0.3)
    for i in list(np.argsort(vs)[:3]) + list(np.argsort(vs)[-3:]):
        v = vs[i]
        if abs(v) < 0.2 * vmax:
            continue
        ax.text(v + vmax * 0.04 * (1 if v >= 0 else -1), ypos[i], F(v), ha="left" if v >= 0 else "right",
                va="center", fontsize=cs.SIZES["small"], fontweight="bold", color=cols[i])
    if ks[0] <= spot <= ks[-1]:
        sy = float(np.interp(spot, ks, ypos))
        ax.axhline(sy, color=P["white"], lw=1.2, ls=(0, (1, 2)))
        ax.text(vmax * 1.42, sy + 0.15, "spot %s" % cs.fmt_level(spot, 2), ha="right", va="bottom",
                fontsize=cs.SIZES["small"], fontweight="bold", color=P["white"])
    fw, fh = fig.get_size_inches()
    x, y, wd, h = rects[0]
    fig.text(x + 0.3 / fw, y + 0.32 / fh, expiry_note, fontsize=cs.SIZES["small"], color=P["subtitle"], va="bottom")
    x2, y2, w2, h2 = rects[1]
    lines = how_to or []
    yy = y2 + h2 - 1.2 / fh
    for head, body in lines:
        fig.text(x2 + 0.3 / fw, yy, head, fontsize=cs.SIZES["label"], fontweight="bold",
                 color=P.get(head.split()[0].lower(), P["text"]) if head.split()[0].lower() in ("green", "red")
                 else P["text"], va="top")
        fig.text(x2 + 0.3 / fw, yy - 0.34 / fh, body, fontsize=cs.SIZES["small"], color=P["subtitle"], va="top",
                 linespacing=1.4)
        yy -= (0.62 + 0.29 * body.count("\n") + 0.25) / fh
    cs.save(fig, out_path)
    pos = [(float(k), float(v)) for k, v in zip(ks, vs)]
    return {"max_pos": max(pos, key=lambda t: t[1]), "max_neg": min(pos, key=lambda t: t[1]), "rows": pos}


# ================================================================ 6. scenario route tree
def _node(ax, cx, cy, w, h, label, sub, colour, fill, lw=2.2, ls="-", label_size=None, sub_size=None):
    box = FancyBboxPatch((cx - w / 2, cy - h / 2), w, h, boxstyle="round,pad=0,rounding_size=1.6",
                         facecolor=fill, edgecolor=colour, linewidth=lw, linestyle=ls, zorder=3,
                         mutation_aspect=ax.figure.get_size_inches()[1] / ax.figure.get_size_inches()[0] * 1.6)
    ax.add_patch(box)
    if sub:
        ax.text(cx, cy + h * 0.17, label, ha="center", va="center", fontsize=label_size or cs.SIZES["label"] + 2,
                fontweight="bold", color=colour, zorder=4)
        ax.text(cx, cy - h * 0.22, sub, ha="center", va="center", fontsize=sub_size or cs.SIZES["small"],
                color=P["text"], zorder=4, linespacing=1.3)
    else:
        ax.text(cx, cy, label, ha="center", va="center", fontsize=label_size or cs.SIZES["label"] + 2,
                fontweight="bold", color=colour, zorder=4)


def _arrow(ax, x0, y0, x1, y1, colour, ls="-"):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=26, color=colour, lw=2.2,
                                 linestyle=ls, zorder=2, shrinkA=0, shrinkB=0))


def route_tree(out_path, *, title, subtitle, root, question, branches, callout, footer_right, snapshot,
               aside=None):
    """root/question: (label, sub). branches: list of dicts {label, sub, colour, leaf: (label, sub) or None,
    dashed_leaf: bool}. aside: (label, sub) dashed grey node under the question for 'not measured' paths."""
    fig, rects = cs.frame(title, subtitle, panels=1, tags=[("SCENARIO ROUTES", "yellow")], callout=callout,
                          footer_right=footer_right, snapshot=snapshot)
    ax = cs.panel_axes(fig, rects[0], pad=(0.3, 0.3, 0.3, 0.6))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_xticks([])
    ax.set_yticks([])
    fills = {"green": P["node_green"], "red": P["node_red"], "yellow": P["node_yellow"], "cyan": P["node_cyan"],
             "grey": P["node_grey"], "white": P["node_grey"]}
    _node(ax, 50, 88, 50, 12, root[0], root[1], P["cyan"], fills["cyan"])
    _arrow(ax, 50, 82, 50, 74.5, P["cyan"])
    _node(ax, 50, 68, 46, 11, question[0], question[1], P["yellow"], P["panel"])
    n = len(branches)
    xs = [50] if n == 1 else list(np.linspace(18, 82, n))
    bw = min(29, 88 / n - 2)
    for bx, br in zip(xs, branches):
        col = P[br["colour"]]
        _arrow(ax, 50 + (bx - 50) * 0.45, 62.5, bx, 50.5, col)
        _node(ax, bx, 44, bw, 12, br["label"], br.get("sub"), col, fills[br["colour"]])
        if br.get("leaf"):
            ls = (0, (4, 3)) if br.get("dashed_leaf") else "-"
            lc = P["muted"] if br.get("dashed_leaf") else col
            _arrow(ax, bx, 38, bx, 29.5, lc, ls="--" if br.get("dashed_leaf") else "-")
            _node(ax, bx, 21, bw, 15, br["leaf"][0], br["leaf"][1], lc,
                  P["panel"] if br.get("dashed_leaf") else fills[br["colour"]], ls=ls, label_size=cs.SIZES["label"],
                  sub_size=cs.SIZES["small"] - 0.5)
    if aside:
        _node(ax, 50, 5.5, 62, 7.5, aside[0], None, P["muted"], P["panel"], lw=1.6, ls=(0, (4, 3)),
              label_size=cs.SIZES["small"])
    cs.save(fig, out_path)


# ================================================================ 7. earnings expected-move strip
def earnings_strip(out_path, rows, *, title, subtitle, callout, footer_right, snapshot, session_label):
    """rows: list of dicts {sym, name, when, past: [abs %], implied: % or None, gap_chance: fraction or None,
    stale: bool}. Past reactions as grey dots, their median as a white tick, implied move as a cyan bar."""
    fig, rects = cs.frame(title, subtitle, panels=1, tags=[("EARNINGS  " + session_label, "cyan")],
                          callout=callout, footer_right=footer_right, snapshot=snapshot)
    fw, fh = fig.get_size_inches()
    x, y, w, h = rects[0]
    ax = fig.add_axes([x + 2.6 / fw, y + 0.95 / fh, w - (2.6 + 2.9) / fw, h - (0.95 + 1.35) / fh])
    ax.set_facecolor("none")
    for s in ax.spines.values():
        s.set_visible(False)
    n = len(rows)
    xmax = max([max(r["past"]) if r["past"] else 0 for r in rows] + [r["implied"] or 0 for r in rows] + [5]) * 1.15
    ax.set_xlim(0, xmax)
    ax.set_ylim(n - 0.4, -0.6)
    ax.set_yticks([])
    ax.tick_params(axis="x", colors=P["subtitle"], labelsize=cs.SIZES["small"])
    ax.xaxis.set_major_formatter(lambda v, p: "%g%%" % v)
    for i, r in enumerate(rows):
        ax.axhline(i, color=P["zero"], lw=0.8, zorder=1)
        if r.get("implied"):
            ax.add_patch(Rectangle((0, i - 0.17), r["implied"], 0.34, facecolor=P["cyan"], alpha=0.30,
                                   edgecolor=P["cyan"], lw=1.4, zorder=2))
            ax.text(r["implied"] + xmax * 0.01, i - 0.2, "priced %s" % cs.fmt_pct(r["implied"], 1, signed=False)
                    .replace("%", "%"), va="bottom", ha="left", fontsize=cs.SIZES["small"], color=P["cyan"],
                    fontweight="bold")
        if r["past"]:
            ax.scatter(r["past"], [i] * len(r["past"]), s=90, color=P["subtitle"], zorder=3, edgecolors="none")
            med = float(np.median(r["past"]))
            ax.plot([med, med], [i - 0.25, i + 0.25], color=P["white"], lw=3, zorder=4)
        else:
            ax.text(xmax * 0.01, i - 0.06, "no past reactions on file", fontsize=cs.SIZES["small"], va="bottom",
                    color=P["muted"])
        # left labels
        ax.text(-0.02, i - 0.08, r["sym"], transform=ax.get_yaxis_transform(), ha="right", va="bottom",
                fontsize=cs.SIZES["label"] + 3, fontweight="bold", color=P["title"])
        ax.text(-0.02, i + 0.1, r["when"], transform=ax.get_yaxis_transform(), ha="right", va="top",
                fontsize=cs.SIZES["small"], color=P["orange"] if "after" in r["when"] else P["cyan"])
        # right column
        gc = r.get("gap_chance")
        rt = ("%d%%" % round(100 * gc)) if gc is not None else "n/a"
        ax.text(1.03, i, rt, transform=ax.get_yaxis_transform(), ha="left", va="center",
                fontsize=cs.SIZES["label"] + 3, fontweight="bold", color=P["text"])
    ax.text(1.03, -0.75, "chance of a\n10%+ open gap", transform=ax.get_yaxis_transform(), ha="left",
            va="bottom", fontsize=cs.SIZES["small"], color=P["subtitle"], linespacing=1.2)
    fig.text(x + 0.3 / fw, y + 0.3 / fh, "Grey dots = absolute moves on the last report days; white tick = their "
             "median. Cyan bar = options-implied move where we have it. Moves are absolute: direction is not shown.",
             fontsize=cs.SIZES["small"], color=P["subtitle"], va="bottom")
    cs.save(fig, out_path)
