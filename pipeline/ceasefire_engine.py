#!/usr/bin/env python3
"""Ceasefire-timing engine. Stdlib only.

Two survival questions, each answered as a full predictive distribution over DAYS:
  breakdown   ceasefire agreed on day 0 -> on which day does fighting resume?
              (r25 = trailing-7-day state-based deaths reach 25; v1 = first fatal day)
  ceasefire   war spell starts (onset or resumption) on day 0 -> on which day is the next
              ceasefire agreed?
Case bases are built by tools/build_ceasefire_data.py (PA-X + UCDP GED, 1989 - Sep 2026).

Models (all censoring-aware):
  km        Kaplan-Meier of the training set - the outside view / naive baseline
  aft       interval-censored log-normal AFT on pre-start features (L2, Adam)
  knn       reference class: weighted Kaplan-Meier of the k most similar past cases
  ens       average of the aft and knn survival curves  <- the engine's call
Point call = the median day of the predictive distribution (minimises expected |error|).

    python pipeline/ceasefire_engine.py backtest [--target r25|v1|cf] [--from 2000]
    python pipeline/ceasefire_engine.py predict --case iran-2026-07-25
    python pipeline/ceasefire_engine.py live      # the 2026 Iran war, as-of each start day

Backtest = walk-forward by calendar year: fit on cases started before Jan 1 of year Y with
every training outcome CENSORED at that cutoff (no look-ahead), predict year-Y cases.
"""
import argparse
import csv
import datetime as dt
import math
import pathlib
import random

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "ceasefire"
HMAX = 3650                      # survival curves are evaluated on days 0..HMAX
LN2 = math.sqrt(2.0)

TARGETS = {
    "r25": ("breakdown_cases.csv", "r25_day"),
    "v1": ("breakdown_cases.csv", "v1_day"),
    "cf": ("ceasefire_cases.csv", "cf_day"),
}
FEATURES = {
    "breakdown_cases.csv": ["interstate", "local", "unilateral", "third_party", "mixed", "l_d7",
                            "l_d30", "l_d90", "l_d365", "trend", "active30", "l_age",
                            "prior_cf", "prior_breaks", "has_last", "l_last_dur", "l_since_break"],
    "ceasefire_cases.csv": ["interstate", "after_cf", "l_d7", "l_d365", "l_age", "prior_cf"],
}
LOGGED = {"prior_cf", "prior_breaks"}   # counts enter as log1p


# ── data ────────────────────────────────────────────────────────────────

def load(target):
    fname, col = TARGETS[target]
    feats = FEATURES[fname]
    cases = []
    with open(DATA / fname, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            x = [math.log1p(float(r[k])) if k in LOGGED else float(r[k]) for k in feats]
            ev = r[col] != ""
            cases.append({"id": r.get("cf_id") or r["spell_id"], "conflict": r["conflict_name"],
                          "date": dt.date.fromisoformat(r["date"]), "x": x,
                          "t": max(1, int(r[col])) if ev else int(r["censor_day"]), "e": int(ev),
                          "src": r.get("src", "")})
    return cases, feats


def censor_at(cases, cutoff):
    """Training view as of `cutoff`: outcomes after the cutoff are unknown (right-censored)."""
    out = []
    for c in cases:
        if c["date"] >= cutoff:
            continue
        seen = (cutoff - c["date"]).days
        if c["t"] <= seen:
            out.append(c)
        elif seen >= 1:
            out.append({**c, "t": seen, "e": 0})
    return out


# ── survival primitives ─────────────────────────────────────────────────

def Phi(z):
    return 0.5 * math.erfc(-z / LN2)


def phi(z):
    return math.exp(-0.5 * z * z) / math.sqrt(2 * math.pi)


def km_curve(times, events, weights=None):
    """Weighted Kaplan-Meier -> list S[0..HMAX]."""
    w = weights or [1.0] * len(times)
    at = {}
    for t, e, wi in zip(times, events, w):
        at.setdefault(t, [0.0, 0.0])
        at[t][0] += wi * e
        at[t][1] += wi
    risk = sum(w)
    S, s, last = [1.0] * (HMAX + 1), 1.0, 0
    for t in sorted(at):
        d, n = at[t]
        for k in range(last + 1, min(t, HMAX + 1)):
            S[k] = s
        if risk > 0:
            s *= max(0.0, 1 - d / risk)
        if t <= HMAX:
            S[t] = s
        last = min(t, HMAX)
        risk -= n
    for k in range(last + 1, HMAX + 1):
        S[k] = s
    return S


def quantile(S, q):
    """first day on which P(event by day) >= q; HMAX+1 if never inside the curve"""
    for t, s in enumerate(S):
        if 1 - s >= q:
            return t
    return HMAX + 1


# ── models ──────────────────────────────────────────────────────────────

class KM:
    def fit(self, tr):
        self.S = km_curve([c["t"] for c in tr], [c["e"] for c in tr])
        return self

    def curve(self, x):
        return self.S


class Std:
    def fit(self, X):
        n = len(X)
        self.mu = [sum(c) / n for c in zip(*X)]
        self.sd = [max(1e-6, math.sqrt(sum((v - m) ** 2 for v in c) / n))
                   for c, m in zip(zip(*X), self.mu)]
        return self

    def __call__(self, x):
        return [(v - m) / s for v, m, s in zip(x, self.mu, self.sd)]


class AFT:
    """Interval-censored log-normal AFT: event on day t means T in (t-1, t]."""
    def __init__(self, l2=0.05, iters=600, lr=0.05):
        self.l2, self.iters, self.lr = l2, iters, lr

    def fit(self, tr):
        self.z = Std().fit([c["x"] for c in tr])
        X = [[1.0] + self.z(c["x"]) for c in tr]
        lt = [math.log(c["t"]) for c in tr]
        lt0 = [math.log(c["t"] - 1) if c["t"] > 1 else None for c in tr]
        E = [c["e"] for c in tr]
        p = len(X[0])
        b = [sum(l for l, e in zip(lt, E) if e) / max(1, sum(E))] + [0.0] * (p - 1)
        s = 0.5                                  # log sigma
        mb, vb, ms, vs = [0.0] * p, [0.0] * p, 0.0, 0.0
        n = len(X)
        for it in range(1, self.iters + 1):
            sig = math.exp(s)
            gb, gs = [0.0] * p, 0.0
            for xi, hi, lo, e in zip(X, lt, lt0, E):
                mu = sum(a * v for a, v in zip(b, xi))
                zb = (hi - mu) / sig
                if e:
                    Pb, pb = Phi(zb), phi(zb)
                    if lo is None:
                        Pa, pa, za = 0.0, 0.0, 0.0
                    else:
                        za = (lo - mu) / sig
                        Pa, pa = Phi(za), phi(za)
                    den = max(Pb - Pa, 1e-300)
                    dmu = (pa - pb) / (sig * den)
                    dsg = (pa * za - pb * zb) / den
                else:
                    sv = max(1 - Phi(zb), 1e-300)
                    dmu = phi(zb) / (sig * sv)
                    dsg = phi(zb) * zb / sv
                for j in range(p):
                    gb[j] += dmu * xi[j]
                gs += dsg
            gb = [g / n - (self.l2 * bj if j else 0.0) for j, (g, bj) in enumerate(zip(gb, b))]
            gs /= n
            # Adam ascent
            for j in range(p):
                mb[j] = 0.9 * mb[j] + 0.1 * gb[j]
                vb[j] = 0.999 * vb[j] + 0.001 * gb[j] ** 2
                b[j] += self.lr * (mb[j] / (1 - 0.9 ** it)) / (math.sqrt(vb[j] / (1 - 0.999 ** it)) + 1e-8)
            ms = 0.9 * ms + 0.1 * gs
            vs = 0.999 * vs + 0.001 * gs ** 2
            s += self.lr * (ms / (1 - 0.9 ** it)) / (math.sqrt(vs / (1 - 0.999 ** it)) + 1e-8)
        self.b, self.sig = b, math.exp(s)
        return self

    def curve(self, x):
        mu = self.b[0] + sum(a * v for a, v in zip(self.b[1:], self.z(x)))
        return [1.0] + [1 - Phi((math.log(t) - mu) / self.sig) for t in range(1, HMAX + 1)]


class KNN:
    """Reference class: Kaplan-Meier over the k most similar past cases."""
    def __init__(self, k=30):
        self.k = k

    def fit(self, tr):
        self.tr = tr
        self.z = Std().fit([c["x"] for c in tr])
        self.Z = [self.z(c["x"]) for c in tr]
        return self

    def curve(self, x):
        q = self.z(x)
        d = sorted((math.sqrt(sum((a - b) ** 2 for a, b in zip(q, zi))), i)
                   for i, zi in enumerate(self.Z))[:self.k]
        idx = [i for _, i in d]
        w = [1.0 / (1.0 + dist) for dist, _ in d]
        return km_curve([self.tr[i]["t"] for i in idx], [self.tr[i]["e"] for i in idx], w)


class Ensemble:
    def fit(self, tr):
        self.m = [AFT().fit(tr), KNN().fit(tr)]
        return self

    def curve(self, x):
        a, b = (m.curve(x) for m in self.m)
        return [(u + v) / 2 for u, v in zip(a, b)]


MODELS = {"km": KM, "aft": AFT, "knn": KNN, "ens": Ensemble}


# ── scoring ─────────────────────────────────────────────────────────────

def score(preds, label):
    """preds: list of (case, S). Day-level error on observed events + censoring-aware Brier."""
    obs = [(c, S) for c, S in preds if c["e"]]
    ae = sorted(abs(quantile(S, 0.5) - c["t"]) for c, S in obs)
    out = {"model": label, "n": len(preds), "n_obs": len(obs)}
    if ae:
        out["medAE"] = ae[len(ae) // 2]
        out["MAE"] = round(sum(ae) / len(ae), 1)
        for w in (0, 1, 3, 7, 30):
            out[f"in{w}"] = round(sum(a <= w for a in ae) / len(ae), 3)
        out["logAE"] = round(sorted(abs(math.log1p(quantile(S, 0.5)) - math.log1p(c["t"]))
                                    for c, S in obs)[len(obs) // 2], 3)
        out["cov50"] = round(sum(quantile(S, .25) <= c["t"] <= quantile(S, .75) for c, S in obs) / len(obs), 3)
        out["cov80"] = round(sum(quantile(S, .10) <= c["t"] <= quantile(S, .90) for c, S in obs) / len(obs), 3)
        out["p_exact"] = round(sum((S[c["t"] - 1] - S[c["t"]]) if c["t"] <= HMAX else 0
                                   for c, S in obs) / len(obs), 4)
    for h in (1, 7, 30, 90, 365):
        bs = [((1 - S[h]) - (1 if (c["e"] and c["t"] <= h) else 0)) ** 2
              for c, S in preds if (c["e"] and c["t"] <= h) or c["t"] >= h]
        out[f"brier{h}"] = round(sum(bs) / len(bs), 4) if bs else None
    # Harrell C on the median call (shorter predicted median = earlier event)
    num = den = 0
    for i, (ci, Si) in enumerate(preds):
        if not ci["e"]:
            continue
        mi = quantile(Si, 0.5)
        for cj, Sj in preds:
            if cj["t"] > ci["t"]:
                den += 1
                mj = quantile(Sj, 0.5)
                num += 1 if mi < mj else 0.5 if mi == mj else 0
    out["C"] = round(num / den, 3) if den else None
    return out


def walk_forward(cases, model_names, start_year):
    years = sorted({c["date"].year for c in cases if c["date"].year >= start_year})
    preds = {m: [] for m in model_names}
    for y in years:
        cut = dt.date(y, 1, 1)
        tr = censor_at(cases, cut)
        te = [c for c in cases if c["date"].year == y]
        if len(tr) < 40 or not te:
            continue
        for m in model_names:
            fit = MODELS[m]().fit(tr)
            preds[m] += [(c, fit.curve(c["x"])) for c in te]
    return preds


# ── day-by-day updating model (breakdown) ───────────────────────────────
# The static engine sees only the signing day. This one re-forecasts at the end of EVERY day
# of the ceasefire from what the ceasefire has looked like so far (fatal days, deaths in the
# last 1/3/7 days, days since the last fatality) - violations are the precursor of collapse.

DYN_MAX = 365
DYN_FEATS = ["l_s", "l_last1", "l_last3", "l_last7", "l_total", "l_quiet", "any_fatal"]


def load_daily():
    dd = {}
    with open(DATA / "breakdown_daily.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            dd.setdefault(r["cf_id"], {})[int(r["day"])] = int(r["deaths"])
    return dd


def dyn_rows(case, deaths, h, last_s=None):
    """(s, features, y) for every day s the ceasefire is still holding at the end of day s.
    y = 1 if fighting resumes within (s, s+h]. Rows stop once the h-day outcome is unknown."""
    arr = [0] * (DYN_MAX + 2)
    for k, n in deaths.items():
        if k <= DYN_MAX + 1:
            arr[k] = n
    pre = [0] * (DYN_MAX + 2)
    for k in range(1, DYN_MAX + 2):
        pre[k] = pre[k - 1] + arr[k]
    T, E = case["t"], case["e"]
    stop = min(DYN_MAX, T - 1) if E else min(DYN_MAX, T - h)
    if last_s is not None:
        stop = min(stop, last_s)
    out, last = [], 0
    for s in range(0, stop + 1):
        if s and arr[s]:
            last = s
        w = lambda a: pre[s] - pre[max(0, s - a)]
        f = [math.log1p(s), math.log1p(w(1)), math.log1p(w(3)), math.log1p(w(7)),
             math.log1p(pre[s]), math.log1p(s - last if last else s + 1), int(last > 0)]
        y = int(bool(E) and T <= s + h)
        out.append((s, case["x"] + f, y))
    return out


class Logit:
    """Weighted L2 logistic regression (Adam, full batch). Negatives subsampled at rate q."""
    def __init__(self, l2=0.01, iters=150, lr=0.08, q=0.15, seed=7):
        self.l2, self.iters, self.lr, self.q, self.seed = l2, iters, lr, q, seed

    def fit(self, rows):
        rnd = random.Random(self.seed)
        keep = [(x, y, 1.0 if y else 1 / self.q) for x, y in rows if y or rnd.random() < self.q]
        self.z = Std().fit([x for x, _, _ in keep])
        X = [[1.0] + self.z(x) for x, _, _ in keep]
        Y = [y for _, y, _ in keep]
        W = [w for _, _, w in keep]
        p, n = len(X[0]), sum(W)
        b = [0.0] * p
        m, v = [0.0] * p, [0.0] * p
        for it in range(1, self.iters + 1):
            g = [0.0] * p
            for xi, yi, wi in zip(X, Y, W):
                eta = sum(a * c for a, c in zip(b, xi))
                pr = 1 / (1 + math.exp(-max(-30, min(30, eta))))
                r = wi * (yi - pr)
                for j in range(p):
                    g[j] += r * xi[j]
            g = [gj / n - (self.l2 * bj if j else 0) for j, (gj, bj) in enumerate(zip(g, b))]
            for j in range(p):
                m[j] = 0.9 * m[j] + 0.1 * g[j]
                v[j] = 0.999 * v[j] + 0.001 * g[j] ** 2
                b[j] += self.lr * (m[j] / (1 - 0.9 ** it)) / (math.sqrt(v[j] / (1 - 0.999 ** it)) + 1e-8)
        self.b = b
        return self

    def prob(self, x):
        eta = self.b[0] + sum(a * c for a, c in zip(self.b[1:], self.z(x)))
        return 1 / (1 + math.exp(-max(-30, min(30, eta))))


def auc(scores, ys):
    pairs = sorted(zip(scores, ys))
    pos = sum(ys)
    neg = len(ys) - pos
    if not pos or not neg:
        return None
    rank_sum, i = 0.0, 0
    while i < len(pairs):
        j = i
        while j < len(pairs) and pairs[j][0] == pairs[i][0]:
            j += 1
        avg = (i + j + 1) / 2
        rank_sum += avg * sum(y for _, y in pairs[i:j])
        i = j
    return round((rank_sum - pos * (pos + 1) / 2) / (pos * neg), 3)


def daily_backtest(start_year, step=2, tau=0.5):
    """Walk-forward in `step`-year blocks. For each test ceasefire, a live forecaster re-scores
    every day; we measure the daily hazard (h=1) and the 7-day warning (h=7)."""
    cases, _ = load("r25")
    daily = load_daily()
    res = {1: [], 7: []}
    alarms = []
    years = sorted({c["date"].year for c in cases if c["date"].year >= start_year})
    blocks = [years[i:i + step] for i in range(0, len(years), step)]
    for blk in blocks:
        cut = dt.date(blk[0], 1, 1)
        tr = censor_at(cases, cut)
        te = [c for c in cases if c["date"].year in blk]
        if len(tr) < 40 or not te:
            continue
        km = km_curve([c["t"] for c in tr], [c["e"] for c in tr])
        models = {}
        for h in (1, 7):
            rows = [(x, y) for c in tr for _, x, y in dyn_rows(c, daily.get(c["id"], {}), h)]
            models[h] = Logit().fit(rows)
        for c in te:
            dd = daily.get(c["id"], {})
            for h in (1, 7):
                for s, x, y in dyn_rows(c, dd, h):
                    base = (km[s] - km[min(s + h, HMAX)]) / km[s] if km[s] > 0 else 0
                    res[h].append((models[h].prob(x), base, y))
            if c["e"] and c["t"] <= DYN_MAX:
                p7 = {s: models[7].prob(x) for s, x, _ in dyn_rows(c, dd, 7, last_s=c["t"] - 1)}
                p1 = {s: models[1].prob(x) for s, x, _ in dyn_rows(c, dd, 1, last_s=c["t"] - 1)}
                alarms.append((c, p7, p1))
    out = {}
    for h, rr in res.items():
        bm = sum((p - y) ** 2 for p, _, y in rr) / len(rr)
        bb = sum((b - y) ** 2 for _, b, y in rr) / len(rr)
        out[f"h{h}"] = {"rows": len(rr), "events": sum(y for *_, y in rr),
                        "brier": round(bm, 4), "brier_km": round(bb, 4),
                        "skill": round(1 - bm / bb, 3), "auc": auc([p for p, _, _ in rr], [y for *_, y in rr]),
                        "auc_km": auc([b for _, b, _ in rr], [y for *_, y in rr])}
    # the live-warning view, on every test ceasefire that collapsed within a year
    T = [c["t"] for c, _, _ in alarms]
    warned = [any(p7.get(s, 0) >= tau for s in range(max(0, c["t"] - 7), c["t"])) for c, p7, _ in alarms]
    warned2 = [any(p7.get(s, 0) >= tau for s in range(max(0, c["t"] - 7), c["t"] - 1)) for c, p7, _ in alarms]
    leads = sorted(c["t"] - min(s for s in range(max(0, c["t"] - 7), c["t"]) if p7.get(s, 0) >= tau)
                   for (c, p7, _), w in zip(alarms, warned) if w)
    eve = [p1.get(c["t"] - 1) for c, _, p1 in alarms if c["t"] >= 1]
    # exact-day call: on the eve, is "tomorrow" the engine's most likely break day this week?
    rr7 = res[7]
    fa = sum(1 for p, _, y in rr7 if p >= tau and not y)
    al = sum(1 for p, _, _ in rr7 if p >= tau)
    out["warning"] = {
        "collapses": len(alarms), "day1_collapses": sum(t == 1 for t in T),
        "warned_within_7d": round(sum(warned) / len(warned), 3),
        "warned_2plus_days_ahead": round(sum(warned2) / len(warned2), 3),
        "median_lead_days": leads[len(leads) // 2] if leads else None,
        "alarm_precision": round(1 - fa / al, 3) if al else None,
        "eve_p_tomorrow_median": round(sorted(eve)[len(eve) // 2], 3) if eve else None,
    }
    return out, alarms


def trace(case_id, days):
    """Live replay of one ceasefire: the 7-day and next-day call at chosen days."""
    cases, _ = load("r25")
    daily = load_daily()
    c = next(c for c in cases if c["id"] == case_id)
    tr = censor_at(cases, c["date"])
    m7 = Logit().fit([(x, y) for t in tr for _, x, y in dyn_rows(t, daily.get(t["id"], {}), 7)])
    m1 = Logit().fit([(x, y) for t in tr for _, x, y in dyn_rows(t, daily.get(t["id"], {}), 1)])
    dd = daily.get(c["id"], {})
    rows7 = {s: x for s, x, _ in dyn_rows({**c, "e": 0, "t": DYN_MAX + 7}, dd, 7)}
    out = []
    for s in days:
        if s in rows7:
            out.append((s, (c["date"] + dt.timedelta(days=s)).isoformat(),
                        dd.get(s, 0), round(m7.prob(rows7[s]), 3), round(m1.prob(rows7[s]), 3)))
    return c, out


# ── CLI ─────────────────────────────────────────────────────────────────

def fmt_day(d0, n):
    return (d0 + dt.timedelta(days=n)).isoformat() if n <= HMAX else f">{HMAX}d"


def explain(case, S, label=""):
    q = {p: quantile(S, p) for p in (.1, .25, .5, .75, .9)}
    d0 = case["date"]
    hz = ", ".join(f"P(<= {h}d)={1 - S[h]:.0%}" for h in (1, 7, 30, 90, 365))
    actual = (f"actual day {case['t']} ({fmt_day(d0, case['t'])})" if case["e"]
              else f"no event through day {case['t']} (censored)")
    return (f"{case['id']} {label} start {d0}: median day {q[.5]} ({fmt_day(d0, q[.5])}); "
            f"50% [{q[.25]}, {q[.75]}]  80% [{q[.1]}, {q[.9]}]\n    {hz}\n    {actual}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    b = sub.add_parser("backtest")
    b.add_argument("--target", default="r25", choices=list(TARGETS))
    b.add_argument("--from", dest="start", type=int, default=2000)
    b.add_argument("--models", default="km,aft,knn,ens")
    p = sub.add_parser("predict")
    p.add_argument("--case", required=True)
    p.add_argument("--target", default="r25", choices=list(TARGETS))
    sub.add_parser("live")
    d = sub.add_parser("backtest-daily")
    d.add_argument("--from", dest="start", type=int, default=2000)
    d.add_argument("--tau", type=float, default=0.5)
    a = ap.parse_args()
    random.seed(7)

    if a.cmd == "backtest":
        cases, _ = load(a.target)
        preds = walk_forward(cases, a.models.split(","), a.start)
        for m, pr in preds.items():
            print(score(pr, m))
    elif a.cmd == "predict":
        cases, _ = load(a.target)
        c = next(c for c in cases if c["id"] == a.case)
        S = Ensemble().fit(censor_at(cases, c["date"])).curve(c["x"])
        print(explain(c, S, a.target))
    elif a.cmd == "live":
        for target in ("r25", "v1", "cf"):
            cases, _ = load(target)
            for c in cases:
                if c["id"].startswith(("iran-2026", "16905-")):
                    S = Ensemble().fit(censor_at(cases, c["date"])).curve(c["x"])
                    print(explain(c, S, target))
        for cid in ("iran-2026-04-08", "iran-2026-06-17", "iran-2026-07-25"):
            c, rows = trace(cid, range(0, 120))
            hot = [r for r in rows if (r[2] or r[3] >= 0.3) and (not c["e"] or r[0] <= c["t"])]
            end = f"war resumed day {c['t']}" if c["e"] else f"no war through day {c['t']}"
            print(f"\n{cid} day-by-day ({end}) - day, date, deaths that day, P(war within 7d), P(war tomorrow):")
            for r in hot:
                print("   ", r)
    elif a.cmd == "backtest-daily":
        out, _ = daily_backtest(a.start, tau=a.tau)
        for k, v in out.items():
            print(k, v)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
