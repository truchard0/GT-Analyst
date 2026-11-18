"""Read cached Skylit gamma heatmaps (no API calls, no credits) per EXPIRATION - never summed across expiries.
For each map: per symbol, per expiry: King (largest |gamma| strike), top +/- nodes within +-8% of spot,
local sign at spot (sum of strikes within +-0.5% of spot, same expiry), and the expiry's share of total |gamma|."""
import glob
import gzip
import json
import os
import sys

SK = r"C:\Users\hudso\Downloads\Trading Bot\tradingview\_skylit"


def syms_of(d):
    out = []

    def find(x, depth=0):
        if depth > 6:
            return
        if isinstance(x, dict):
            if "symbol" in x and "expirations" in x and "matrix" in x:
                out.append(x)
                return
            for v in x.values():
                find(v, depth + 1)
        elif isinstance(x, list):
            for v in x[:60]:
                find(v, depth + 1)
    find(d)
    return out


def read(path, want=None, band=0.08, top=3):
    d = json.load(gzip.open(path))
    res = {}
    for s in syms_of(d):
        sym = s["symbol"]
        if want and sym not in want:
            continue
        spot = s["spot"]
        strikes = [r["strike"] for r in s["strikes"]]
        M = s["matrix"]
        exps = s["expirations"]
        tot = [sum(abs(M[i][j]) for i in range(len(strikes))) for j in range(len(exps))]
        allabs = sum(tot) or 1
        per = []
        for j, e in enumerate(exps):
            col = [(strikes[i], M[i][j]) for i in range(len(strikes))]
            king = max(col, key=lambda kv: abs(kv[1]))
            near = [kv for kv in col if abs(kv[0] / spot - 1) <= band]
            pos = sorted([kv for kv in near if kv[1] > 0], key=lambda kv: -kv[1])[:top]
            neg = sorted([kv for kv in near if kv[1] < 0], key=lambda kv: kv[1])[:top]
            at = sum(v for k, v in col if abs(k / spot - 1) <= 0.005)
            above = sum(v for k, v in near if k > spot)
            below = sum(v for k, v in near if k < spot)
            per.append(dict(exp=e, share=tot[j] / allabs, king=king, pos=pos, neg=neg, at=at, above=above, below=below))
        res[sym] = dict(spot=spot, per=per, n=len(strikes), lo=min(strikes), hi=max(strikes))
    return res


def fmt(v):
    a = abs(v)
    s = f"{a/1e9:.2f}B" if a >= 1e9 else f"{a/1e6:.1f}M" if a >= 1e6 else f"{a/1e3:.0f}k"
    return ("+" if v >= 0 else "-") + s


def show(title, res):
    print(f"\n######## {title}")
    for sym, r in res.items():
        print(f"== {sym} spot {r['spot']:.2f}  strikes {r['lo']}-{r['hi']} ({r['n']})")
        for p in r["per"]:
            k = p["king"]
            print(f"  {p['exp']} share {p['share']*100:4.1f}%  King {k[0]} {fmt(k[1])} ({(k[0]/r['spot']-1)*100:+.1f}%)"
                  f"  at-spot {fmt(p['at'])}  above {fmt(p['above'])} below {fmt(p['below'])}")
            print("     +", ", ".join(f"{k} {fmt(v)}" for k, v in p["pos"]), " | -", ", ".join(f"{k} {fmt(v)}" for k, v in p["neg"]))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "now"
    if mode == "now":
        for day in ["2026-10-20", "2026-10-21", "2026-10-22", "2026-10-23"]:
            f = os.path.join(SK, "live", day, "overnight_heatmap.json.gz")
            if os.path.exists(f):
                show(f"{day} overnight (after-hours spot)", read(f, want={"SPXW", "QQQ", "NDX", "SMH"} if day != "2026-10-23" else None))
    elif mode == "monthly":
        # NDX/SPX/VIX monthly books through time (eod archive to 9/30, then live overnight)
        files = sorted(glob.glob(os.path.join(SK, "eod", "2026-0[89]-*.json.gz")))[::5] + sorted(glob.glob(os.path.join(SK, "eod", "2026-09-30.json.gz")))
        for f in files:
            show(os.path.basename(f), read(f, want={"SPX", "NDX"}, top=2))
        for day in ["2026-10-20", "2026-10-23"]:
            show(day + " overnight", read(os.path.join(SK, "live", day, "overnight_heatmap.json.gz"), want={"NDX"}, top=2))
        ev = sorted(glob.glob(os.path.join(SK, "evening", "*.json.gz")))[-1]
        show("VIX monthly " + os.path.basename(ev), read(ev, want={"VIX"}, band=0.6, top=3))
