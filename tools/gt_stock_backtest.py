#!/usr/bin/env python3
"""GT stock backtest: 500 point-in-time predictions, Sep 25 - Oct 23 2026. Stdlib only.

PRE-REGISTERED DESIGN (frozen in git before any outcome is computed)
  cohorts   as-of Friday closes 2026-09-25, 10-02, 10-09, 10-16; each call resolves at the next
            Friday close (5 sessions). Four non-overlapping weeks = the last month.
  universe  125 stocks: highest median dollar volume over the 60 sessions ending 2026-09-24,
            from watchlist.json + data/sector_map.json + SECTOR_LEADERS (tools/gt_backtest_data.py).
            The same 125 names every week -> 4 x 125 = 500 predictions.
  target    sign of the 5-session EXCESS return vs SPY (stock minus SPY). Isolates the GT sector
            call from market direction.
  inputs    only data stamped at or before the as-of close: prices, Brent, the 2-year yield,
            headlines published before 20:00 UTC on the as-of day, scheduled earnings/macro dates.
  doctrine  the skills AS THEY STOOD BEFORE the 2026-10-25 patches (git 0a4656e). The 10/25
            patches were written with knowledge of Aug-Oct outcomes, so the variant that uses
            them ("v1-hindsight") is reported only as a labeled, contaminated comparison.

RULES (model "v0", each tagged with its doctrine source)
  R1 branch      market-transmission §1/§4/§10: classify the as-of regime from Brent's 20-session
                 change and the 2-year yield's 10-session change -> B (supply/hawkish), A
                 (generic/dovish, the statistical default) or good-oil (demand); weight 1 / 0.5 /
                 0.25 by how cleanly the two channels agree.
  R2 sector map  market-transmission §12 table + §5 equity-duration law + §1 CORRIDOR + doctrine
                 §10.8 (fertilizer cascade), §11.2 (resilience), §11.4 (aviation): tilt per sector.
  R3 war economy doctrine §10.10/§12.5: defense +0.25 while the war is live (it is, since 2/28).
  R4 oscillation doctrine §16.12 (written 8/1): an escalation spike in the headline tape is not
                 extrapolated - fade it. -0.35 x z(escalation index) along the Branch-B vector.
  R5 catalysts   market-transmission §13e: inside a scheduled catalyst the catalyst governs -
                 earnings inside the horizon halve the name's score; a CPI/payrolls print inside the
                 horizon scales the branch terms by 0.75.
  R6 momentum    contrarian-red-team #7: never fight 6-12 month momentum without a catalyst -
                 a call against a top/bottom-tercile 12-1 month mover is halved.
  P = 0.5 + 0.18 * tanh(|score|)   (mechanical signals: no capital-committed or source-quality
                 component, so the ceiling stays ~0.68 per the conviction rubric's spirit)

    python tools/gt_stock_backtest.py predict    # writes data/gt_backtest/predictions.csv
    python tools/gt_stock_backtest.py score      # writes data/gt_backtest/scored.csv + summary
    python tools/gt_stock_backtest.py insample-v2   # v2-candidate on the same month (in-sample only)
    python tools/gt_stock_backtest.py forward YYYY-MM-DD --hormuz-impaired 1|0   # live v2 calls
"""
import csv
import datetime as dt
import json
import math
import pathlib
import random
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = ROOT / "data" / "gt_backtest"
COHORTS = ["2026-09-25", "2026-10-02", "2026-10-09", "2026-10-16"]
UNIVERSE_ASOF = "2026-09-24"
N_UNIVERSE = 125
HORIZON = 5
NOT_STOCKS = {"SPY", "BZ=F", "XLE", "XLK", "SMH", "ITA", "XLP", "XLU", "XLF", "XLV", "XLY", "QQQ"}
# scheduled macro prints (BLS calendar, public in advance): Sept payrolls 10/02, Sept CPI 10/14
MACRO_PRINTS = ["2026-10-02", "2026-10-14"]

sys.path.insert(0, str(ROOT / "tools"))
from gt_backtest_data import SECTOR_LEADERS  # noqa: E402

# ── sector classes ──────────────────────────────────────────────────────
SM = json.loads((ROOT / "data" / "sector_map.json").read_text(encoding="utf-8"))
WL = json.loads((ROOT / "watchlist.json").read_text(encoding="utf-8"))["themes"]
POWER = set(SM["uranium_power"]["tickers"]) | {"TLN", "OKLO", "SMR", "NNE"}
CLASS_ORDER = [  # first match wins
    ("ENERGY", set(SM["energy"]["tickers"]) | set(SECTOR_LEADERS["energy"]) | {"XOM"}),
    ("DEFENSE", set(WL["defense"]["tickers"]) | set(SM["defense"]["tickers"])),
    ("TANKER", {"FRO", "STNG"}),
    ("CONTAINER", {"ZIM", "MATX", "GSL", "DAC"}),
    ("AG_INPUTS", set(SM["ag_inputs"]["tickers"])),
    ("POWER", POWER),
    ("STAPLES", set(SECTOR_LEADERS["staples"])),
    ("UTILITIES", set(SECTOR_LEADERS["utilities"])),
    ("FINANCIALS", set(SECTOR_LEADERS["financials"])),
    ("HEALTHCARE", set(SECTOR_LEADERS["healthcare"])),
    ("AIRLINES", set(SECTOR_LEADERS["airlines"])),
    ("DISCRETIONARY", set(SECTOR_LEADERS["discretionary"]) | {"TSLA"}),
    ("MEMORY", set(WL["memory"]["tickers"])),
    ("SEMIS", set(WL["chips"]["tickers"]) | set(SM["semis"]["tickers"])),
    ("PHOTONICS", set(WL["photonics"]["tickers"])),
    ("NEOCLOUD", set(WL["ai_datacenters"]["tickers"])),
    ("HYPERSCALER", set(WL["hyperscalers"]["tickers"])),
    ("SPACE", set(WL["space"]["tickers"])),
    ("ROBOTICS", set(WL["robotics"]["tickers"])),
]


def sector_of(sym):
    for name, members in CLASS_ORDER:
        if sym in members:
            return name
    return "OTHER"


# R2: market-transmission §12 table (+ the sections named in the docstring)
TILT = {  #              B (supply)  A (generic)  G (good-oil)
    "ENERGY":        (+1.00, -0.75, +0.50),
    "DEFENSE":       (+0.75, +0.25, 0.00),
    "TANKER":        (+1.00, -0.50, +0.25),
    "CONTAINER":     (+0.50, -0.25, +0.25),
    "AG_INPUTS":     (+0.50, -0.25, 0.00),
    "POWER":         (+0.25, 0.00, 0.00),
    "STAPLES":       (+0.50, +0.50, -0.50),
    "UTILITIES":     (-0.25, +0.50, -0.50),
    "FINANCIALS":    (+0.25, -0.25, +0.50),
    "HEALTHCARE":    (+0.25, +0.50, -0.25),
    "AIRLINES":      (-1.00, 0.00, 0.00),
    "DISCRETIONARY": (-0.50, -0.25, +0.25),
    "MEMORY":        (-1.00, -0.25, +0.25),
    "SEMIS":         (-1.00, 0.00, +0.25),
    "PHOTONICS":     (-1.00, -0.25, 0.00),
    "NEOCLOUD":      (-1.00, -0.50, 0.00),
    "HYPERSCALER":   (-0.50, +0.50, 0.00),
    "SPACE":         (-1.00, -0.50, 0.00),
    "ROBOTICS":      (-0.75, -0.25, 0.00),
    "OTHER":         (0.00, 0.00, 0.00),
}
AI_COMPLEX = {"MEMORY", "SEMIS", "PHOTONICS", "NEOCLOUD", "HYPERSCALER"}

# R4 lexicon (headline classifier, word-prefix match)
ESC = re.compile(r"\b(strike|struck|attack|missile|drone|bomb|kill|war\b|escalat|retaliat|blockade|"
                 r"mine[sd]?\b|seiz|hits?\b|shoot|shot\b|sink|sank|threat|warn|clash|assault|raid|"
                 r"explosion|intercept|barrage|target)", re.I)
DEESC = re.compile(r"\b(ceasefire|cease-fire|truce|deal|talks|negotiat|diploma|agreement|reopen|"
                   r"mediat|pause|de-escalat|peace|proposal|envoy|accord|framework)", re.I)


# ── data ────────────────────────────────────────────────────────────────

def load_wide(name):
    rows = list(csv.reader(open(D / name)))
    head = rows[0][1:]
    out = {s: {} for s in head}
    for r in rows[1:]:
        for s, v in zip(head, r[1:]):
            if v != "":
                out[s][r[0]] = float(v)
    return out


class Data:
    def __init__(self):
        self.px = load_wide("closes.csv")
        self.vol = load_wide("volumes.csv")
        self.cal = sorted(self.px["SPY"])  # trading calendar = SPY sessions
        self.y2 = {r["date"]: float(r["y2"]) for r in csv.DictReader(open(D / "rates.csv")) if r["y2"]}
        self.news = [(r["published_utc"], r["title"]) for r in csv.DictReader(open(D / "news.csv", encoding="utf-8"))]
        self.earn = {}
        for r in csv.DictReader(open(D / "earnings.csv")):
            self.earn.setdefault(r["symbol"], set()).add(r["date"])

    def idx(self, day):
        return self.cal.index(day)

    def close(self, sym, day):
        """last close at or before `day` (never after)"""
        s = self.px.get(sym, {})
        if day in s:
            return s[day]
        prior = [d for d in s if d <= day]
        return s[max(prior)] if prior else None

    def ret(self, sym, d0, d1):
        a, b = self.close(sym, d0), self.close(sym, d1)
        return b / a - 1 if a and b else None


def universe(data):
    i = data.idx(UNIVERSE_ASOF)
    window = data.cal[i - 59:i + 1]
    dv = []
    for s in data.px:
        if s in NOT_STOCKS:
            continue
        v = sorted(data.px[s].get(d, 0) * data.vol[s].get(d, 0) for d in window)
        dv.append((v[len(v) // 2], s))
    dv.sort(reverse=True)
    return sorted(s for _, s in dv[:N_UNIVERSE])


# ── the engine ──────────────────────────────────────────────────────────

def branch(data, asof):
    i = data.idx(asof)
    oil20 = data.ret("BZ=F", data.cal[i - 20], asof)
    rd = sorted(d for d in data.y2 if d <= asof)
    y2_10 = (data.y2[rd[-1]] - data.y2[rd[-11]]) * 100   # bp over 10 sessions
    spx20 = data.ret("SPY", data.cal[i - 20], asof)
    if oil20 > 0.03 and y2_10 >= 2:
        name, w = ("G", 1.0) if spx20 > 0.04 else ("B", 1.0)
    elif oil20 < -0.03 and y2_10 <= -2:
        name, w = "A", 1.0
    elif y2_10 >= 5:
        name, w = "B", 0.5
    elif y2_10 <= -5:
        name, w = "A", 0.5
    else:
        name, w = "A", 0.25          # §2: Branch A is the statistical default
    return {"branch": name, "w": w, "oil20": oil20, "y2_10bp": y2_10, "spx20": spx20}


def esc_index(data, start_utc, end_utc):
    e = n = 0
    for ts, title in data.news:
        if start_utc < ts <= end_utc:
            a, b = bool(ESC.search(title)), bool(DEESC.search(title))
            if a and not b:
                e += 1
            elif b and not a:
                n += 1
    return (e - n) / (e + n + 1), e, n


def news_z(data, asof):
    end = dt.datetime.fromisoformat(asof + "T20:00")
    vals = []
    for k in range(5):  # this week + 4 prior weeks
        hi = end - dt.timedelta(days=7 * k)
        lo = hi - dt.timedelta(days=7)
        vals.append(esc_index(data, lo.strftime("%Y-%m-%dT%H:%MZ"), hi.strftime("%Y-%m-%dT%H:%MZ"))[0])
    cur, prior = vals[0], vals[1:]
    mu = sum(prior) / len(prior)
    sd = math.sqrt(sum((v - mu) ** 2 for v in prior) / len(prior)) or 1e-6
    return max(-2.0, min(2.0, (cur - mu) / sd)), cur


def momentum_terciles(data, syms, asof):
    i = data.idx(asof)
    m = {}
    for s in syms:
        r = data.ret(s, data.cal[max(0, i - 252)], data.cal[i - 21])
        if r is not None:
            m[s] = r
    ranked = sorted(m, key=m.get)
    n = len(ranked)
    return {s: (0 if k < n / 3 else 2 if k >= 2 * n / 3 else 1) for k, s in enumerate(ranked)}, m


# v2-candidate (written AFTER scoring v0 - in-sample on Sep 25 - Oct 23, so its score there is not
# evidence; it exists to be forward-tested). Physical chokepoint status is an as-of input from the
# tape (Kpler / IMF PortWatch / UKMTO): Hormuz flow < 50% of pre-war on every date below.
HORMUZ_IMPAIRED = {"2026-09-25": 1, "2026-10-02": 1, "2026-10-09": 1, "2026-10-16": 1, "2026-10-23": 1}
ABSTAIN_BELOW = 0.60


def branch_v2(data, asof):
    """market-transmission §4.1 (provisional): with the chokepoint physically impaired, SUPPLY
    does not need 2-year confirmation - the 2y sign sizes the weight instead of gating."""
    br = branch(data, asof)
    if HORMUZ_IMPAIRED.get(asof) and br["oil20"] > 0:
        br["branch"], br["w"] = "B", (1.0 if br["y2_10bp"] >= 2 else 0.5)
    return br


def predict(data, syms, asof, variant="v0"):
    i = data.idx(asof)
    end = data.cal[i + HORIZON] if i + HORIZON < len(data.cal) else "pending"
    br = branch_v2(data, asof) if variant == "v2-candidate" else branch(data, asof)
    col = {"B": 0, "A": 1, "G": 2}[br["branch"]]
    z, esc_now = news_z(data, asof)
    macro = any(asof < d <= end for d in MACRO_PRINTS)
    terc, mom = momentum_terciles(data, syms, asof)
    smh_6m = data.ret("SMH", data.cal[i - 126], asof) - data.ret("SPY", data.cal[i - 126], asof)
    out = []
    for s in syms:
        sec = sector_of(s)
        t = TILT[sec]
        r1 = br["w"] * t[col]                                   # R1 + R2
        r3 = 0.25 if sec == "DEFENSE" else 0.0                  # R3
        r4 = -0.35 * z * t[0]                                   # R4 (fade along the B vector)
        if variant == "v1-hindsight":
            # §7.1 physical-flow gate: no premium-fade while the supply branch is live
            if br["branch"] == "B":
                r4 = 0.0
            # §5.1: no rate-derate on the AI complex while its own revision engine runs
            if sec in AI_COMPLEX and smh_6m > 0 and r1 < 0:
                r1 = 0.0
        if variant == "v2-candidate":
            r4 = 0.0   # jiang §16.12c: oscillation is a kinetic-event rule, never an asset-price fade
        if macro:                                              # R5 (macro print)
            r1 *= 0.75
            r4 *= 0.75
        score = r1 + r3 + r4
        earn = end != "pending" and any(asof < d <= end for d in data.earn.get(s, ()))
        if earn:                                                # R5 (earnings)
            score *= 0.5
        tc = terc.get(s, 1)
        fights_mom = (score < 0 and tc == 2) or (score > 0 and tc == 0)
        if fights_mom:                                          # R6
            score *= 0.5
        direction = "outperform" if score >= 0 else "underperform"
        p = 0.5 + 0.18 * math.tanh(abs(score))
        out.append({
            "asof": asof, "resolve": end, "ticker": s, "sector": sec,
            "call": direction, "p": round(p, 4), "score": round(score, 4),
            "r_branch": round(r1, 4), "r_war": r3, "r_news": round(r4, 4),
            "earnings_in_window": int(earn), "fights_momentum": int(fights_mom),
            "branch": br["branch"], "branch_w": br["w"], "oil20": round(br["oil20"], 4),
            "y2_10bp": round(br["y2_10bp"], 1), "spx20": round(br["spx20"], 4),
            "news_z": round(z, 3), "esc_index": round(esc_now, 3), "macro_print": int(macro),
            "mom_12_1": round(mom.get(s, 0.0), 4),
            "falsifier": f"{s} 5-session return minus SPY's, {asof} close -> {end} close, is "
                         f"{'<= 0' if direction == 'outperform' else '>= 0'}",
            "variant": variant,
        })
    return out


# ── baselines (same names, same weeks) ──────────────────────────────────

def baselines(data, syms, asof):
    i = data.idx(asof)
    end = data.cal[i + HORIZON]
    _, mom = momentum_terciles(data, syms, asof)
    vals = sorted(mom.values())
    med = vals[len(vals) // 2]
    sd = (sum((v - med) ** 2 for v in vals) / len(vals)) ** 0.5 or 1
    rev = {s: -(data.ret(s, data.cal[i - 5], asof) - data.ret("SPY", data.cal[i - 5], asof)) for s in syms}
    by_sec = {}
    for s in syms:
        x = data.ret(s, data.cal[i - 20], asof) - data.ret("SPY", data.cal[i - 20], asof)
        by_sec.setdefault(sector_of(s), []).append(x)
    secmom = {k: sorted(v)[len(v) // 2] for k, v in by_sec.items()}
    rnd = random.Random(int(asof.replace("-", "")))
    out = []
    for s in syms:
        for name, sc in (("momentum-12-1", (mom.get(s, med) - med) / sd),
                         ("reversal-1w", rev[s] / 0.05),
                         ("sector-momentum-20d", secmom[sector_of(s)] / 0.05),
                         ("coin-flip", rnd.choice([-1e-9, 1e-9]))):
            out.append({"asof": asof, "resolve": end, "ticker": s, "sector": sector_of(s),
                        "call": "outperform" if sc >= 0 else "underperform",
                        "p": round(0.5 + 0.18 * math.tanh(abs(sc)), 4), "score": round(sc, 4),
                        "variant": name})
    return out


# ── scoring ─────────────────────────────────────────────────────────────

def score_rows(data, rows):
    for r in rows:
        ex = data.ret(r["ticker"], r["asof"], r["resolve"]) - data.ret("SPY", r["asof"], r["resolve"])
        up = ex > 0
        hit = (r["call"] == "outperform") == up
        p = float(r["p"])
        r["excess_ret"] = round(ex, 5)
        r["hit"] = int(hit)
        r["brier"] = round((p - (1 if hit else 0)) ** 2, 5)
    return rows


def spearman(xs, ys):
    def rank(v):
        o = sorted(range(len(v)), key=lambda k: v[k])
        r = [0] * len(v)
        for pos, k in enumerate(o):
            r[k] = pos
        return r
    rx, ry = rank(xs), rank(ys)
    n = len(xs)
    mx, my = sum(rx) / n, sum(ry) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    vx = sum((a - mx) ** 2 for a in rx) ** 0.5
    vy = sum((b - my) ** 2 for b in ry) ** 0.5
    return cov / (vx * vy) if vx and vy else 0.0


def summarize(rows, label):
    n = len(rows)
    hits = sum(r["hit"] for r in rows)
    brier = sum(r["brier"] for r in rows) / n
    longs = [r["excess_ret"] for r in rows if r["call"] == "outperform"]
    shorts = [r["excess_ret"] for r in rows if r["call"] == "underperform"]
    spread = (sum(longs) / len(longs) if longs else 0) - (sum(shorts) / len(shorts) if shorts else 0)
    ics = []
    for a in sorted({r["asof"] for r in rows}):
        c = [r for r in rows if r["asof"] == a]
        ics.append(spearman([float(r["score"]) for r in c], [r["excess_ret"] for r in c]))
    return {"model": label, "n": n, "hit_rate": round(hits / n, 4), "brier": round(brier, 4),
            "ls_spread_wk": round(spread, 4), "rank_ic_by_week": [round(x, 3) for x in ics],
            "mean_ic": round(sum(ics) / len(ics), 3)}


def cluster_bootstrap(rows, B=2000, seed=11):
    """hit-rate CI resampling (week x sector) clusters - the honest unit of independence"""
    cl = {}
    for r in rows:
        cl.setdefault((r["asof"], r["sector"]), []).append(r["hit"])
    keys = list(cl)
    rnd = random.Random(seed)
    stats = []
    for _ in range(B):
        hs = [h for k in (rnd.choice(keys) for _ in keys) for h in cl[k]]
        stats.append(sum(hs) / len(hs))
    stats.sort()
    return len(keys), round(stats[int(0.025 * B)], 3), round(stats[int(0.975 * B)], 3)


def write(path, rows):
    keys = list(rows[0])
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def truncated(data, asof):
    """A copy holding ONLY what was observable at the as-of close. The trading calendar and the
    scheduled earnings/macro dates stay (both are published in advance)."""
    t = object.__new__(Data)
    t.px = {s: {d: v for d, v in ser.items() if d <= asof} for s, ser in data.px.items()}
    t.vol = data.vol
    t.cal = data.cal
    t.y2 = {d: v for d, v in data.y2.items() if d <= asof}
    t.news = [(ts, title) for ts, title in data.news if ts <= asof + "T20:00Z"]
    t.earn = data.earn
    return t


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    data = Data()
    syms = universe(data)
    if cmd == "predict":
        rows, extra = [], []
        for a in COHORTS:
            full = predict(data, syms, a, "v0")
            blind = predict(truncated(data, a), syms, a, "v0")
            assert full == blind, f"LOOK-AHEAD: {a} predictions change when future data is removed"
            rows += full
            extra += predict(data, syms, a, "v1-hindsight") + baselines(data, syms, a)
        write(D / "predictions.csv", rows)
        write(D / "comparisons.csv", extra)
        print(f"universe {len(syms)}; wrote {len(rows)} v0 predictions + {len(extra)} comparison rows")
    elif cmd == "score":
        rows = list(csv.DictReader(open(D / "predictions.csv", encoding="utf-8")))
        comp = list(csv.DictReader(open(D / "comparisons.csv", encoding="utf-8")))
        score_rows(data, rows)
        score_rows(data, comp)
        write(D / "scored.csv", rows)
        write(D / "comparisons_scored.csv", comp)
        print(json.dumps(summarize(rows, "GT v0 (pre-registered)")))
        for v in sorted({r["variant"] for r in comp}):
            print(json.dumps(summarize([r for r in comp if r["variant"] == v], v)))
        k, lo, hi = cluster_bootstrap(rows)
        print(f"v0 hit-rate 95% CI over {k} week x sector clusters: [{lo}, {hi}]")
    elif cmd == "insample-v2":
        rows = []
        for a in COHORTS:
            rows += predict(data, syms, a, "v2-candidate")
        score_rows(data, rows)
        print("IN-SAMPLE ONLY (rules written after seeing v0's scores):")
        print(json.dumps(summarize(rows, "v2-candidate, all calls")))
        kept = [r for r in rows if r["p"] >= ABSTAIN_BELOW]
        if kept:
            print(json.dumps(summarize(kept, f"v2-candidate, P >= {ABSTAIN_BELOW} only")))
    elif cmd == "forward":
        asof = sys.argv[2]
        if "--hormuz-impaired" not in sys.argv:
            sys.exit("forward needs --hormuz-impaired 1|0 (as-of physical flow status from the tape)")
        HORMUZ_IMPAIRED[asof] = int(sys.argv[sys.argv.index("--hormuz-impaired") + 1])
        rows = [r for r in predict(data, syms, asof, "v2-candidate") if r["p"] >= ABSTAIN_BELOW]
        path = D / f"forward_v2_{asof}.csv"
        write(path, rows)
        print(f"{len(rows)} v2 calls (P >= {ABSTAIN_BELOW}) as of {asof} close -> {path.name}")
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
