#!/usr/bin/env python3
"""Multi-week positioning read from one day's Skylit maps (gamma-maps skill, section 3 and 5).

    python tools/gamma_weeks.py --date 2026-11-18 [--out reports/charts/20261118_positioning]

For each name: share of the map's |gamma| by expiry, net gamma near the price (+-2%) now and after the front expiry
rolls off, the largest cell now and after the roll, and the largest cell in the last expiry shown. Stocks come from
data/ai_technical/heatmaps_<date>.json; the S&P 500 (SPXW) and Nasdaq-100 (QQQ) from the evening overnight map (falls
back to the 16:00 close map), via tools/market_update/data.py (set GT_SKYLIT_ROOT for a mirror of the server maps).
Writes data/ai_technical/gamma_weeks_<date>.json and two house-style charts. Descriptive only: no targets, no direction.
"""
import argparse
import datetime as dt
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import market_update  # noqa: E402,F401  (adds the user site-packages back for numpy under python -I)
import numpy as np  # noqa: E402
from market_update import chartstyle as cs  # noqa: E402

P = cs.P
NAMES = {"SPXW": "S&P 500", "QQQ": "Nasdaq-100 (QQQ)", "NVDA": "Nvidia", "AVGO": "Broadcom", "MU": "Micron",
         "META": "Meta", "AMZN": "Amazon", "SMH": "Chip index (SMH)", "CRWV": "CoreWeave"}


def regime(net, tot):
    return "flat" if abs(net) < 0.03 * tot else ("long" if net > 0 else "short")


def read(name, strikes, expiries, g, spot, batch, snap, roll):
    k = np.asarray(strikes, float)
    g = np.asarray(g, float)
    tot = np.abs(g).sum() or 1.0
    shares = [float(np.abs(g[:, j]).sum() / tot * 100) for j in range(g.shape[1])]
    near = np.abs(k / spot - 1) <= 0.02

    def king(cols):
        sub = g[:, cols]
        r, c = np.unravel_index(np.argmax(np.abs(sub)), sub.shape)
        return {"strike": float(k[r]), "expiry": expiries[cols[c]], "value": float(sub[r, c]),
                "pct_from_spot": float((k[r] / spot - 1) * 100)}

    allc = list(range(g.shape[1]))
    post = [j for j, e in enumerate(expiries) if e > roll] or allc[-1:]
    front = float(sum(shares[j] for j, e in enumerate(expiries) if e <= roll))
    gp = g[:, post]
    totp = np.abs(gp).sum() or 1.0
    return {
        "name": name, "spot": float(spot), "batch": batch, "snapshot": snap, "expiries": expiries,
        "share_by_expiry_pct": shares, "share_through_roll_pct": front, "roll": roll,
        "regime_now": regime(g[near].sum(), tot), "net_pm2_now_pct": float(g[near].sum() / tot * 100),
        "regime_after_roll": regime(gp[near].sum(), totp), "net_pm2_after_roll_pct": float(gp[near].sum() / totp * 100),
        "king_now": king(allc), "king_after_roll": king(post), "king_last_expiry": king([allc[-1]]),
    }


def load(date, roll):
    tag = date.replace("-", "")
    hm = json.load(open(ROOT / ("data/ai_technical/heatmaps_%s.json" % tag), encoding="utf-8"))
    out = {}
    from market_update import data as D
    snap = D.load_overnight(date) or D.load_live(date, "1600")
    for sym in ("SPXW", "QQQ"):
        m = snap.get(sym)
        if m is None:
            continue
        keep = [j for j, e in enumerate(m.expiries) if e > date][:5]
        w = np.abs(m.strikes / m.spot - 1) <= 0.03
        out[sym] = read(sym, m.strikes[w], [m.expiries[j] for j in keep], m.matrix[w][:, keep], m.spot,
                        "Skylit %s" % ("overnight map 17:30 ET" if snap.kind == "overnight" else "close map 16:00 ET"),
                        snap.label, roll)
    for t in hm["tickers"]:
        if t.get("event_stale"):
            continue
        out[t["ticker"]] = read(t["ticker"], t["strikes"], t["expiries"], t["gamma"], t["spot"], t["source_batch"],
                                t["snapshot_ts"], roll)
    return out


def chart_calendar(reads, path, date):
    order = [s for s in ("SPXW", "QQQ", "NVDA", "AVGO", "MU", "META", "AMZN", "SMH", "CRWV") if s in reads]
    stocks = [s for s in order if s not in ("SPXW", "QQQ")]
    front = float(np.median([reads[s]["share_through_roll_pct"] for s in stocks]))
    fig, rects = cs.frame(
        "Friday's expiry holds %d%% of the typical AI-stock map; the rest runs to 18 Dec" % round(front),
        "Share of each map's dealer gamma by expiry, %s close (index maps: the evening map, which covers about one "
        "week). The front segment rolls off first; what is left is the map for the weeks after." % dt.date.fromisoformat(date).strftime("%d %b %Y").lstrip("0"),
        tags=[("WHAT EXPIRES WHEN", "cyan")], badge=("%d%%" % round(front), "expires Fri 20 Nov"),
        footer_right="via data/ai_technical/gamma_weeks_%s.json" % date.replace("-", ""),
        snapshot="%s 16:00-17:30 ET" % dt.date.fromisoformat(date).strftime("%d %b %Y").lstrip("0"))
    ax = cs.panel_axes(fig, rects[0], pad=(2.6, 0.5, 0.5, 1.0))
    cols = [P["cyan"], P["purple"], P["yellow"], P["orange"], "#7a7a7a"]
    for i, s in enumerate(order):
        r = reads[s]
        left = 0
        for j, (sh, e) in enumerate(zip(r["share_by_expiry_pct"], r["expiries"])):
            ax.barh(i, sh, left=left, height=0.62, color=cols[j % 5], edgecolor=P["panel"], lw=1.2)
            if sh >= 7:
                ax.text(left + sh / 2, i, "%s\n%d%%" % (dt.date.fromisoformat(e).strftime("%d %b").lstrip("0"), round(sh)),
                        ha="center", va="center", fontsize=9.5, family=cs.MONO, fontweight="bold",
                        color="#111111" if j in (0, 2, 3) else P["title"], linespacing=1.1)
            left += sh
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([NAMES[s] for s in order], fontsize=13, color=P["title"])
    ax.set_xticks([])
    ax.set_xlim(0, 100)
    ax.invert_yaxis()
    cs.save(fig, path)


def chart_roll(reads, path, date):
    order = [s for s in ("SPXW", "QQQ", "NVDA", "AVGO", "MU", "META", "AMZN", "SMH", "CRWV") if s in reads]
    flips = sum(1 for s in order if reads[s]["regime_now"] != reads[s]["regime_after_roll"])
    fig, rects = cs.frame(
        "After Friday's roll-off, %d of %d maps change their gamma state near the price" % (flips, len(order)),
        "Net dealer gamma within 2% of the price as a share of the map, now and with every expiry through Fri 20 Nov removed. "
        "Long = hedging tends to damp moves; short = it can extend them; flat = under 3% of the map.",
        tags=[("NOW  VS  AFTER  THE  ROLL", "purple")],
        footer_right="via data/ai_technical/gamma_weeks_%s.json" % date.replace("-", ""),
        snapshot="%s 16:00-17:30 ET" % dt.date.fromisoformat(date).strftime("%d %b %Y").lstrip("0"))
    ax = cs.panel_axes(fig, rects[0], pad=(2.6, 0.5, 2.2, 1.0))
    for i, s in enumerate(order):
        a, b = reads[s]["net_pm2_now_pct"], reads[s]["net_pm2_after_roll_pct"]
        ax.plot([a, b], [i, i], color=P["zero"], lw=2.2, zorder=1)
        ax.plot(a, i, "o", ms=11, color=P["subtitle"], zorder=2)
        ax.plot(b, i, "o", ms=13, color=P["green"] if b > 3 else (P["red"] if b < -3 else P["white"]), zorder=3)
        ax.text(1.02, i, "%s -> %s" % (reads[s]["regime_now"], reads[s]["regime_after_roll"]),
                transform=ax.get_yaxis_transform(), va="center", fontsize=11.5, family=cs.MONO, color=P["text"])
    ax.axvline(0, color=P["zero"], lw=1.2)
    ax.axvspan(-3, 3, color=P["free"], zorder=0)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([NAMES[s] for s in order], fontsize=13, color=P["title"])
    ax.invert_yaxis()
    ax.xaxis.set_major_formatter(lambda v, _: "%+d%%" % v)
    for lab in ax.get_xticklabels():
        lab.set_family(cs.MONO)
    for x0, col, lab in ((0.0, P["subtitle"], "now"), (0.12, P["green"], "after Friday: long"),
                         (0.36, P["red"], "after Friday: short"), (0.61, P["white"], "after Friday: flat")):
        ax.text(x0, 1.03, "● " + lab, transform=ax.transAxes, color=col, fontsize=11.5, fontweight="bold")
    cs.save(fig, path)
    return flips


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--out", default="")
    ap.add_argument("--roll", default="2026-11-20", help="monthly expiry that rolls off (inclusive)")
    ap.add_argument("--universe", default="", help="Skylit universe folder holding eod_vanna_* batches")
    a = ap.parse_args()
    cs.apply("dark")
    reads = load(a.date, a.roll)
    tag = a.date.replace("-", "")
    out = ROOT / (a.out or "reports/charts/%s_positioning" % tag)
    out.mkdir(parents=True, exist_ok=True)
    json.dump({"date": a.date, "reads": reads}, open(ROOT / ("data/ai_technical/gamma_weeks_%s.json" % tag), "w",
                                                     encoding="utf-8"), indent=1)
    chart_calendar(reads, out / "w1_calendar.png", a.date)
    flips = chart_roll(reads, out / "w2_roll.png", a.date)
    if a.universe:
        van = load_vanna(a.date, a.universe)
        chart_vanna(van, reads, out / "w3_vanna.png", a.date)
        data = json.load(open(ROOT / ("data/ai_technical/gamma_weeks_%s.json" % tag), encoding="utf-8"))
        data["vanna"] = van
        json.dump(data, open(ROOT / ("data/ai_technical/gamma_weeks_%s.json" % tag), "w", encoding="utf-8"), indent=1)
        for n, v in van.items():
            print("VANNA %-5s now %+6.1f%% after %+6.1f%% king %s %s %+.0f %+.1f%% shares %s" % (n, v["net_pm5_now_pct"], v["net_pm5_after_roll_pct"], v["king"]["strike"], v["king"]["expiry"][5:], v["king"]["value"], v["king"]["pct_from_spot"], [round(x) for x in v["share_by_expiry_pct"]]))
    for s, r in reads.items():
        kn, kr, kl = r["king_now"], r["king_after_roll"], r["king_last_expiry"]
        print("%-5s %8.2f front %3.0f%% | now %-5s %+5.1f%% | after %-5s %+5.1f%% | king %s %s %+.1fM %+.1f%% | post %s %s %+.1fM %+.1f%% | last %s %+.1fM %+.1f%%"
              % (s, r["spot"], r["share_through_roll_pct"], r["regime_now"], r["net_pm2_now_pct"], r["regime_after_roll"],
                 r["net_pm2_after_roll_pct"], kn["strike"], kn["expiry"][5:], kn["value"] / 1e6, kn["pct_from_spot"],
                 kr["strike"], kr["expiry"][5:], kr["value"] / 1e6, kr["pct_from_spot"], kl["strike"], kl["value"] / 1e6,
                 kl["pct_from_spot"]))
    print("regime changes after roll:", flips)



# ---------------------------------------------------------------- vanna (VEX) read
def load_vanna(date, universe, names=("NVDA", "MU", "META", "AMZN", "SMH", "CRWV"), last="2026-12-18", win=0.10):
    """Net dealer vanna per name from the Skylit end-of-day vanna batch (eod_vanna_*). Sign convention unaudited."""
    import gzip, os
    d = pathlib.Path(universe) / date
    out = {}
    for f in sorted(os.listdir(d)):
        if not f.startswith("eod_vanna_"):
            continue
        j = json.load(gzip.open(d / f))
        hm = j.get("heatmap", j.get("body", j))
        for s in hm.get("data", {}).get("symbols", []):
            if s["symbol"] not in names or s["symbol"] in out:
                continue
            exps = list(s.get("expirations", []))
            keep = [i for i, e in enumerate(exps) if date < e <= last]
            k = np.array([float(r["strike"]) for r in s.get("strikes", [])])
            m = np.array(s.get("matrix") or [], float)
            spot = float(s["spot"])
            w = np.abs(k / spot - 1) <= win
            g = m[w][:, keep]
            kk = k[w]
            ex = [exps[i] for i in keep]
            tot = np.abs(g).sum() or 1.0
            near = np.abs(kk / spot - 1) <= 0.05
            post = [i for i, e in enumerate(ex) if e > "2026-11-20"]
            r0, c0 = np.unravel_index(np.argmax(np.abs(g)), g.shape)
            out[s["symbol"]] = {"spot": spot, "expiries": ex, "file": f,
                                "share_by_expiry_pct": [float(np.abs(g[:, i]).sum() / tot * 100) for i in range(len(ex))],
                                "net_pm5_now_pct": float(g[near].sum() / tot * 100),
                                "net_pm5_after_roll_pct": float(g[near][:, post].sum() / (np.abs(g[:, post]).sum() or 1) * 100),
                                "king": {"strike": float(kk[r0]), "expiry": ex[c0], "value": float(g[r0, c0]),
                                         "pct_from_spot": float((kk[r0] / spot - 1) * 100)}}
    return out


def chart_vanna(van, reads, path, date):
    order = [s for s in ("NVDA", "MU", "META", "AMZN", "SMH", "CRWV") if s in van]
    fig, rects = cs.frame(
        "After Friday, CoreWeave has the most negative vanna near the price (-52%), Nvidia the most positive (+15%)",
        "Net vanna within 5% of the price as a share of each map, now and after Fri 20 Nov, expiries to 18 Dec. "
        "Label = gamma state / vanna sign. Vanna sign convention not yet audited against the vendor.",
        tags=[("VANNA  (VEX)", "purple")],
        footer_right="via data/ai_technical/gamma_weeks_%s.json" % date.replace("-", ""),
        snapshot="vanna, %s 16:00 ET" % dt.date.fromisoformat(date).strftime("%d %b %Y").lstrip("0"))
    ax = cs.panel_axes(fig, rects[0], pad=(2.6, 0.5, 2.6, 1.0))
    for i, s in enumerate(order):
        a, b = van[s]["net_pm5_now_pct"], van[s]["net_pm5_after_roll_pct"]
        ax.plot([a, b], [i, i], color=P["zero"], lw=2.2, zorder=1)
        ax.plot(a, i, "o", ms=11, color=P["subtitle"], zorder=2)
        ax.plot(b, i, "o", ms=13, color=P["purple"] if b < 0 else P["cyan"], zorder=3)
        gs = reads.get(s, {}).get("regime_after_roll", "?")
        ax.text(1.02, i, "gamma %s / vanna %s" % (gs, "+" if b > 0 else "-"), transform=ax.get_yaxis_transform(),
                va="center", fontsize=11.5, family=cs.MONO, color=P["text"])
    ax.axvline(0, color=P["zero"], lw=1.2)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([NAMES[s] for s in order], fontsize=13, color=P["title"])
    ax.invert_yaxis()
    ax.xaxis.set_major_formatter(lambda v, _: "%+d%%" % v)
    for x0, col, lab in ((0.0, P["subtitle"], "now"), (0.12, P["cyan"], "after Friday: positive"),
                         (0.42, P["purple"], "after Friday: negative")):
        ax.text(x0, 1.03, "● " + lab, transform=ax.transAxes, color=col, fontsize=11.5, fontweight="bold")
    cs.save(fig, path)


if __name__ == "__main__":
    main()
