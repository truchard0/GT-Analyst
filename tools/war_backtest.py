#!/usr/bin/env python3
"""war_backtest.py - what would the engine have predicted about the strikes, and what does it learn from being wrong?

QUESTION (user, 2026-10-23): strikes are held off for political and economic reasons - the midterms, Netanyahu's campaign,
pump prices, requests from the Gulf - and shocks come only after a cooling-down period. Does an engine that reads the
DECIDERS' incentives forecast the war better than the engine that extrapolated the military leg?

TARGET. At every weekly date t from 2026-04-08 to 2026-10-08 (27 dates): will the US or Israel strike Iranian territory
on at least one day in (t, t+14]?  Strike days: data/war_timeline.json (reconstructed from the Wikipedia timeline).

MODELS (all use only facts public on or before t):
  v0  the engine as it was: persist the current leg. P = 0.70 if a strike fell in the last 7 days, else 0.30.
  v1  v0 as the starting odds, multiplied by decider-incentive factors written down BEFORE scoring and hashed below:
        a US dovish act in the last 14 days (stand-down, pause for talks, ceasefire, call-off)     x0.4
        an explicit no-strike pledge in force (10/8 'not before the midterms')                      x0.1
        inside 60 days of the midterms (political cost of a war the public did not choose)          x0.6
        Brent above 100 (an escalation raises pump prices into a vote)                              x0.7
        an Iranian attack on US forces/bases or a major shipping attack in the last 7 days          x3.0
  v1L v1 with the coefficients re-fitted on the EARLY weeks only (t <= 2026-07-22), shrunk toward the v1 prior, then
      scored on the LATE weeks it never saw. That is 'learn from what you predicted wrong'.

HONESTY. The rules in v1 come from the user's thesis, but I wrote them knowing how the war went, so v1's scores are NOT
out-of-sample; only v1L's late-period score and the forward predictions at the bottom are. 27 weekly points with a few
dozen strike days cannot prove a mechanism; this exposes where the logic fails.

    python tools/war_backtest.py
"""
import datetime as dt
import hashlib
import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
D = dt.date
H = 14
PRIORS = {"dovish": 0.4, "pledge": 0.1, "mid60": 0.6, "brent100": 0.7, "trigger": 3.0}
V0 = {"persist": 0.70, "calm": 0.30}
SPLIT = D(2026, 7, 22)
FEATS = ["persist", "dovish", "pledge", "mid60", "brent100", "trigger"]


def days(a, b):
    return (b - a).days


def load():
    w = json.loads((ROOT / "data" / "war_timeline.json").read_text(encoding="utf-8"))
    strikes = set()
    for a, b, _ in w["strike_ranges"]:
        x = D.fromisoformat(a)
        while x <= D.fromisoformat(b):
            strikes.add(x)
            x += dt.timedelta(days=1)
    dov = [D.fromisoformat(a) for a, _ in w["dovish"]]
    trg = [D.fromisoformat(a) for a, _ in w["triggers"]]
    import marketdata as md
    brent = dict(md.closes("BZ=F", "2026-02-20", "2026-10-24"))
    return w, strikes, dov, trg, brent


def brent_at(brent, t):
    ds = [d for d in brent if D.fromisoformat(d) <= t]
    return brent[max(ds)] if ds else None


def features(t, strikes, dov, trg, brent, mid, pledge_day):
    f = {
        "persist": int(any(0 <= days(s, t) < 7 for s in strikes)),
        "dovish": int(any(0 <= days(x, t) < 14 for x in dov)),
        "pledge": int(t >= pledge_day and t <= mid),
        "mid60": int(0 <= days(t, mid) <= 60),
        "brent100": int((brent_at(brent, t) or 0) > 100),
        "trigger": int(any(0 <= days(x, t) < 7 for x in trg)),
    }
    return f


def logit(p):
    return math.log(p / (1 - p))


def sigm(z):
    return 1 / (1 + math.exp(-z))


def v0(f):
    return V0["persist"] if f["persist"] else V0["calm"]


def v1(f):
    z = logit(v0(f))
    for k, m in PRIORS.items():
        z += f[k] * math.log(m)
    return min(0.97, max(0.02, sigm(z)))


def fit(rows, lam=1.0, iters=4000, lr=0.05):
    """Penalised logistic regression on `rows` [(features, y)], shrinking each coefficient toward its v1 prior (and the
    intercept toward logit(0.30)). Pure python; features absent from the training window keep their prior."""
    b0 = logit(V0["calm"])
    beta = {k: (math.log(PRIORS[k]) if k in PRIORS else math.log(V0["persist"] / (1 - V0["persist"])) - b0) for k in FEATS}
    prior = dict(beta)
    p0 = b0
    for _ in range(iters):
        g0, g = 0.0, {k: 0.0 for k in FEATS}
        for f, y in rows:
            z = p0 + sum(beta[k] * f[k] for k in FEATS)
            e = sigm(z) - y
            g0 += e
            for k in FEATS:
                g[k] += e * f[k]
        n = len(rows)
        p0 -= lr * (g0 / n + 0.0 * (p0 - b0))
        for k in FEATS:
            beta[k] -= lr * (g[k] / n + lam / n * (beta[k] - prior[k]))
    return p0, beta


def pred_fit(p0, beta, f):
    return min(0.97, max(0.02, sigm(p0 + sum(beta[k] * f[k] for k in FEATS))))


def brier(ps, ys):
    return sum((p - y) ** 2 for p, y in zip(ps, ys)) / len(ys)


def main():
    w, strikes, dov, trg, brent = load()
    mid, pledge_day = D.fromisoformat(w["midterms"]), D(2026, 10, 8)
    frozen = hashlib.sha256(json.dumps({"priors": PRIORS, "v0": V0, "split": str(SPLIT), "H": H, "feats": FEATS}, sort_keys=True).encode()).hexdigest()[:16]
    print(f"rules frozen before scoring: sha256[:16] = {frozen}   priors {PRIORS}   v0 {V0}\n")
    ts = [D(2026, 4, 8) + dt.timedelta(days=7 * k) for k in range(27)]
    rows = []
    for t in ts:
        f = features(t, strikes, dov, trg, brent, mid, pledge_day)
        y = int(any(0 < days(t, s) <= H for s in strikes))
        rows.append((t, f, y))
    train = [(f, y) for t, f, y in rows if t <= SPLIT]
    test = [(t, f, y) for t, f, y in rows if t > SPLIT]
    base = sum(y for f, y in train) / len(train)
    p0, beta = fit(train)

    print("date        Y  v0    v1    v1L   features")
    for t, f, y in rows:
        a, b, c = v0(f), v1(f), pred_fit(p0, beta, f)
        on = ",".join(k for k in FEATS if f[k])
        print(f"{t}  {y}  {a:.2f}  {b:.2f}  {c:.2f}  {on}" + ("   <- held out" if t > SPLIT else ""))

    def score(sel):
        ys = [y for *_, y in sel]
        return (brier([v0(f) for _, f, _ in sel], ys), brier([v1(f) for _, f, _ in sel], ys),
                brier([pred_fit(p0, beta, f) for _, f, _ in sel], ys), brier([base] * len(ys), ys), len(ys), sum(ys))
    for name, sel in (("ALL 27 weeks", rows), (f"EARLY (<= {SPLIT}) in-sample for v1L", [r for r in rows if r[0] <= SPLIT]), (f"LATE (> {SPLIT}) held out", test)):
        s = score(sel)
        print(f"\n{name}: n={s[4]} strike-weeks={s[5]}   Brier  v0 {s[0]:.3f}   v1 {s[1]:.3f}   v1L {s[2]:.3f}   base-rate {s[3]:.3f}")

    print("\nWHAT v1L LEARNED (log-odds multipliers, prior -> fitted):")
    for k in FEATS:
        pr = math.log(PRIORS[k]) if k in PRIORS else math.log(V0["persist"] / (1 - V0["persist"])) - logit(V0["calm"])
        print(f"   {k:<9} x{math.exp(pr):.2f} -> x{math.exp(beta[k]):.2f}")
    print(f"   intercept (calm-week odds) {sigm(p0):.2f}")

    print("\nBIGGEST v1 ERRORS (|p-Y| > 0.5):")
    for t, f, y in rows:
        if abs(v1(f) - y) > 0.5:
            print(f"   {t}  Y={y}  v1 {v1(f):.2f}  v0 {v0(f):.2f}  [{','.join(k for k in FEATS if f[k]) or 'no flags'}]")

    # ---- round 2: what the errors say. v0 and v1 both missed because 'any strike' mixes two processes: sporadic retaliation that
    # follows an Iranian attack, and a CAMPAIGN the president decides to start. The thesis is about the second. So: forecast
    # campaign ONSET (a strike range of >= 3 days) in the pause weeks (no strike in the last 7 days), with the SAME frozen priors
    # and a prior base rate of 0.14 (a 65-day median pause, cycle_odds' default prior, not fitted to this war).
    starts = sorted(D.fromisoformat(x) for x, y_, _ in w["strike_ranges"] if days(D.fromisoformat(x), D.fromisoformat(y_)) >= 2)[1:]
    pause = [(t, f) for t, f, y in rows if not f["persist"]]
    base_c = 0.14

    def v1c(f):
        z = logit(base_c)
        for k, m in PRIORS.items():
            z += f[k] * math.log(m)
        return min(0.97, max(0.01, sigm(z)))
    ys2 = [int(any(0 < days(t, st) <= H for st in starts)) for t, f in pause]
    print(f"\nROUND 2 - CAMPAIGN ONSET in pause weeks (campaigns after the first start: {', '.join(str(x) for x in starts)}):")
    print(f"   {len(pause)} pause weeks, {sum(ys2)} followed by an onset within 14 days")
    for (t, f), y in zip(pause, ys2):
        print(f"   {t}  Y={y}  v0c {base_c:.2f}  v1c {v1c(f):.2f}  [{','.join(k for k in FEATS if f[k]) or 'no flags'}]")
    for name, idx in (("all pause weeks", list(range(len(pause)))), ("late pause weeks (> 7/22)", [i for i, (t, f) in enumerate(pause) if t > SPLIT])):
        yy = [ys2[i] for i in idx]
        print(f"   {name}: n={len(yy)}  Brier  v0c {brier([base_c] * len(yy), yy):.3f}   v1c {brier([v1c(pause[i][1]) for i in idx], yy):.3f}")

    print("\nFORWARD (not scored yet; pre-registered here):")
    for label, t, over in (("10/22 -> strike on Iranian territory 10/23..11/05", D(2026, 10, 22), {}),
                           ("11/05, pledge lapsed, cooling-down over, no new dovish act", D(2026, 11, 5), {"pledge": 0, "mid60": 0, "dovish": 0, "persist": 0, "trigger": 0}),
                           ("11/05, same but an Iranian trigger in the last 7 days", D(2026, 11, 5), {"pledge": 0, "mid60": 0, "dovish": 0, "persist": 0, "trigger": 1}),
                           ("11/19, same, still no strike yet", D(2026, 11, 19), {"pledge": 0, "mid60": 0, "dovish": 0, "persist": 0, "trigger": 0})):
        f = features(t, strikes, dov + [D(2026, 10, 22)], trg, brent, mid, pledge_day)
        f.update(over)
        print(f"   {label:<62} v0 {v0(f):.2f}  v1 {v1(f):.2f}  v1L {pred_fit(p0, beta, f):.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
