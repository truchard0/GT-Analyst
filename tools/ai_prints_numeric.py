#!/usr/bin/env python3
"""Numeric point-and-range forecasts for AI-trade prints: the V2 model in data/ai_prints_backtest/PREREG.md.

Walk-forward and mechanical. For each report it uses only that company's earlier reports (pooled figures when a
company has fewer than two). Stdlib only.

    python3 tools/ai_prints_numeric.py                 # backtest scorecard for the window
    python3 tools/ai_prints_numeric.py --rows          # ... plus every forecast row
    python3 tools/ai_prints_numeric.py --json          # machine-readable (also written to results_numeric.json)
    python3 tools/ai_prints_numeric.py --forward       # next forecasts per company from all data on file
    python3 tools/ai_prints_numeric.py --forward --scale 1.3   # widen (or narrow) the forward ranges by a factor
"""
import csv, json, math, pathlib, statistics, sys

D = pathlib.Path(__file__).resolve().parent.parent / "data" / "ai_prints_backtest"
WINDOW = ("2026-05-18", "2026-11-17")
PRINT_FILES = ["prints_history_a.csv", "prints_history_b.csv", "prints_suppliers.csv", "prints_buyers.csv"]
FLOOR = {"N1": 0.005, "N2": 0.010, "N3": 0.030, "N4": 0.020}      # pre-registered minimum half-widths
TIGHT = {"N1": 0.02, "N2": 0.04, "N3": 0.08, "N4": 0.05}          # pre-registered tightness lines
Z80 = 1.28
LAST = 4


def f(x):
    try:
        v = float(str(x).replace(",", "").replace("$", "").strip())
        return v if math.isfinite(v) else None
    except Exception:
        return None


def read(name):
    fp = D / name
    if not fp.exists():
        return []
    with open(fp, newline="", encoding="utf-8-sig") as h:
        return [{(k or "").strip(): (v or "").strip() for k, v in r.items()} for r in csv.DictReader(h)]


def mid(r, lo, hi, m):
    v = f(r.get(m))
    if v is not None:
        return v
    a, b = f(r.get(lo)), f(r.get(hi))
    return (a + b) / 2 if a is not None and b is not None else None


def mean_sd(xs, pooled):
    """Mean and sample sd of the last LAST values; the pooled pair when there are fewer than two."""
    xs = xs[-LAST:]
    if len(xs) >= 2:
        return statistics.mean(xs), statistics.stdev(xs)
    return pooled


def pooled_of(xs):
    if len(xs) >= 2:
        return statistics.mean(xs), statistics.stdev(xs)
    return (xs[0] if xs else 0.0), 0.0


def load_prints():
    seen, out = set(), []
    for name in PRINT_FILES:
        for r in read(name):
            key = (r.get("ticker", "").upper(), r.get("report_date", ""))
            if not key[0] or not key[1] or key in seen:
                continue
            seen.add(key)
            out.append({"ticker": key[0], "date": key[1], "period": r.get("fiscal_period", ""),
                        "timing": r.get("timing", ""), "quality": r.get("quality", ""),
                        "guide": mid(r, "guide_low", "guide_high", "guide_mid"), "actual": f(r.get("actual_revenue")),
                        "next_guide": mid(r, "next_guide_low", "next_guide_high", "next_guide_mid")})
    return sorted(out, key=lambda r: (r["date"], r["ticker"]))


def load_consensus():
    cons = {}
    for r in read("consensus.csv"):
        cons.setdefault((r.get("ticker", "").upper(), (r.get("metric") or "revenue").lower()), []).append(
            (r.get("report_date", ""), f(r.get("consensus_value")), f(r.get("consensus_next_q_value"))))
    return cons


def consensus_for(cons, ticker, metric, date):
    best = None
    for d, v, nv in cons.get((ticker, metric), []):
        try:
            gap = abs((_ord(d) - _ord(date)))
        except Exception:
            continue
        if gap <= 4 and (best is None or gap < best[0]):
            best = (gap, v, nv)
    return (best[1], best[2]) if best else (None, None)


def _ord(d):
    import datetime
    return datetime.date.fromisoformat(d[:10]).toordinal()


def prints_forecasts(prints, cons, forward=False):
    by = {}
    for r in prints:
        by.setdefault(r["ticker"], []).append(r)
    rows = []

    def hist(ticker, before):
        own = [r for r in by[ticker] if r["date"] < before]
        allb = [r for r in prints if r["date"] < before]
        beats = [r["actual"] / r["guide"] - 1 for r in own if r["guide"] and r["actual"]]
        steps = [r["next_guide"] / r["actual"] - 1 for r in own if r["next_guide"] and r["actual"]]
        pb = pooled_of([r["actual"] / r["guide"] - 1 for r in allb if r["guide"] and r["actual"]])
        ps = pooled_of([r["next_guide"] / r["actual"] - 1 for r in allb if r["next_guide"] and r["actual"]])
        b, sb = mean_sd(beats, pb)
        g, sg = mean_sd(steps, ps)
        return b, sb, g, sg, len(beats[-LAST:]), len(steps[-LAST:])

    if forward:
        for t, rs in sorted(by.items()):
            last = rs[-1]
            if not last["next_guide"]:
                continue
            b, sb, g, sg, nb, ns = hist(t, "9999")
            n1 = last["next_guide"] * (1 + b)
            rows.append({"ticker": t, "after_report": last["date"], "guide_mid": last["next_guide"], "b": b, "g": g,
                         "N1_point": n1, "N1_half": max(FLOOR["N1"], Z80 * sb),
                         "N2_point": n1 * (1 + g), "N2_half": max(FLOOR["N2"], Z80 * math.hypot(sb, sg)),
                         "n_beats": nb, "n_steps": ns})
        return rows
    for r in prints:
        if not (WINDOW[0] <= r["date"] <= WINDOW[1]) or not r["guide"]:
            continue
        b, sb, g, sg, nb, ns = hist(r["ticker"], r["date"])
        n1 = r["guide"] * (1 + b)
        c_now, c_next = consensus_for(cons, r["ticker"], "revenue", r["date"])
        row = {"ticker": r["ticker"], "date": r["date"], "period": r["period"], "quality": r["quality"],
               "guide_mid": r["guide"], "n_beats": nb, "n_steps": ns,
               "N1_point": n1, "N1_half": max(FLOOR["N1"], Z80 * sb), "N1_actual": r["actual"],
               "N1_b0": r["guide"], "N1_b1": c_now,
               "N2_point": n1 * (1 + g), "N2_half": max(FLOOR["N2"], Z80 * math.hypot(sb, sg)),
               "N2_actual": r["next_guide"], "N2_b0": r["guide"], "N2_b1": c_next}
        rows.append(row)
    return rows


def capex_forecasts(cons, forward=False):
    raw = read("capex_history.csv")
    by = {}
    for r in raw:
        t = r.get("ticker", "").upper()
        if not t or not r.get("report_date"):
            continue
        by.setdefault(t, {})[r["report_date"]] = {
            "ticker": t, "date": r["report_date"], "year": r.get("guide_year", ""), "capex": f(r.get("reported_quarter_capex")),
            "prior": mid(r, "prior_guide_low", "prior_guide_high", "prior_guide_mid"),
            "new": mid(r, "new_guide_low", "new_guide_high", "new_guide_mid"), "quality": r.get("quality", "")}
    by = {t: [v[d] for d in sorted(v)] for t, v in by.items()}
    allrows = sorted((r for rs in by.values() for r in rs), key=lambda r: r["date"])
    n3, n4 = [], []

    def growths(rs):
        c = [r["capex"] for r in rs if r["capex"]]
        return [c[i] / c[i - 1] - 1 for i in range(1, len(c))]

    def revisions(rs):
        return [r["new"] / r["prior"] - 1 for r in rs if r["new"] and r["prior"]]

    def one(t, own, target):
        """Forecast for `target` (a row dict, or a stub for the next unreported quarter) from `own` earlier rows."""
        before = target["date"]
        allb = [r for r in allrows if r["date"] < before]
        pg = pooled_of([x for tt in by for x in growths([r for r in by[tt] if r["date"] < before])])
        gm, gs = mean_sd(growths(own), pg)
        prev = next((r["capex"] for r in reversed(own) if r["capex"]), None)
        out = {}
        if prev:
            momentum = prev * (1 + gm)
            implied = None
            if target.get("prior") and target.get("year"):
                same = [r for r in own if r["year"] == target["year"] and r["capex"]]
                left = 4 - len(same)
                if left >= 1:
                    implied = (target["prior"] - sum(r["capex"] for r in same)) / left
                    if implied <= 0:
                        implied = None
            point = (momentum + implied) / 2 if implied else momentum
            out["N3"] = {"point": point, "half": max(FLOOR["N3"], Z80 * gs), "b0": prev, "momentum": momentum, "implied": implied}
        if target.get("prior"):
            pr = pooled_of(revisions(allb))
            rm, rsd = mean_sd(revisions([r for r in own if r["year"] == target.get("year")] or own), pr)
            out["N4"] = {"point": target["prior"] * (1 + rm), "half": max(FLOOR["N4"], Z80 * rsd), "b0": target["prior"]}
        return out

    for t, rs in sorted(by.items()):
        if forward:
            last = rs[-1]
            stub = {"date": "9999", "year": last["year"], "prior": last["new"]}
            fc = one(t, rs, stub)
            if "N3" in fc:
                n3.append({"ticker": t, "after_report": last["date"], "annual_guide_mid": last["new"], **{"N3_" + k: v for k, v in fc["N3"].items()}})
            continue
        for i, r in enumerate(rs):
            if not (WINDOW[0] <= r["date"] <= WINDOW[1]):
                continue
            fc = one(t, rs[:i], r)
            c_capex, _ = consensus_for(cons, t, "capex", r["date"])
            if "N3" in fc and r["capex"]:
                n3.append({"ticker": t, "date": r["date"], "quality": r["quality"], "N3_point": fc["N3"]["point"],
                           "N3_half": fc["N3"]["half"], "N3_actual": r["capex"], "N3_b0": fc["N3"]["b0"], "N3_b1": c_capex,
                           "momentum": fc["N3"]["momentum"], "implied": fc["N3"]["implied"]})
            if "N4" in fc and r["new"]:
                n4.append({"ticker": t, "date": r["date"], "quality": r["quality"], "N4_point": fc["N4"]["point"],
                           "N4_half": fc["N4"]["half"], "N4_actual": r["new"], "N4_b0": fc["N4"]["b0"], "N4_b1": None})
    return n3, n4


def card(rows, k):
    xs = [r for r in rows if r.get(k + "_actual") and r.get(k + "_point")]
    if not xs:
        return {"n": 0}
    err = [abs(r[k + "_point"] / r[k + "_actual"] - 1) for r in xs]
    signed = [r[k + "_point"] / r[k + "_actual"] - 1 for r in xs]
    inside = [abs(r[k + "_actual"] / r[k + "_point"] - 1) <= r[k + "_half"] for r in xs]
    out = {"n": len(xs), "median_abs_err_pct": round(100 * statistics.median(err), 2), "mean_abs_err_pct": round(100 * statistics.mean(err), 2),
           "mean_signed_err_pct": round(100 * statistics.mean(signed), 2),
           "within": {f"{p}%": round(sum(e <= p / 100 for e in err) / len(err), 3) for p in (1, 2, 3, 5)},
           "coverage_80": round(sum(inside) / len(inside), 3), "mean_half_width_pct": round(100 * statistics.mean(r[k + "_half"] for r in xs), 2),
           "tight_line_pct": 100 * TIGHT[k]}
    ratios = sorted(abs(r[k + "_actual"] / r[k + "_point"] - 1) / r[k + "_half"] for r in xs)
    out["scale_for_80pct_coverage"] = round(ratios[min(len(ratios) - 1, math.ceil(0.8 * len(ratios)) - 1)], 2)
    for b in ("b0", "b1"):
        ys = [r for r in xs if r.get(f"{k}_{b}")]
        if ys:
            be = [abs(r[f"{k}_{b}"] / r[k + "_actual"] - 1) for r in ys]
            me = [abs(r[k + "_point"] / r[k + "_actual"] - 1) for r in ys]
            out[b] = {"n": len(ys), "median_abs_err_pct": round(100 * statistics.median(be), 2),
                      "model_median_on_same_rows_pct": round(100 * statistics.median(me), 2),
                      "model_closer_on": sum(m < x for m, x in zip(me, be)), "of": len(ys)}
    out["pass"] = {"calibration_65_95": (0.65 <= out["coverage_80"] <= 0.95) if out["n"] >= 10 else None,
                   "tightness": out["mean_half_width_pct"] <= out["tight_line_pct"]}
    if k == "N1" and "b0" in out:
        ok = out["median_abs_err_pct"] < out["b0"]["median_abs_err_pct"]
        if "b1" in out:
            ok = ok and out["b1"]["model_median_on_same_rows_pct"] <= out["b1"]["median_abs_err_pct"] + 0.25
        out["pass"]["accuracy"] = ok
    return out


def main():
    cons = load_consensus()
    prints = load_prints()
    if "--forward" in sys.argv:
        scale = float(sys.argv[sys.argv.index("--scale") + 1]) if "--scale" in sys.argv else 1.0
        rows = prints_forecasts(prints, cons, forward=True)
        n3, _ = capex_forecasts(cons, forward=True)
        out = {"scale": scale, "revenue": [], "capex": []}
        for r in rows:
            h1, h2 = r["N1_half"] * scale, r["N2_half"] * scale
            out["revenue"].append({"ticker": r["ticker"], "after_report": r["after_report"], "guide_mid": r["guide_mid"],
                                   "revenue_point": round(r["N1_point"], 3), "revenue_low": round(r["N1_point"] * (1 - h1), 3),
                                   "revenue_high": round(r["N1_point"] * (1 + h1), 3), "revenue_half_pct": round(100 * h1, 2),
                                   "next_guide_point": round(r["N2_point"], 3), "next_guide_low": round(r["N2_point"] * (1 - h2), 3),
                                   "next_guide_high": round(r["N2_point"] * (1 + h2), 3), "next_guide_half_pct": round(100 * h2, 2),
                                   "avg_beat_pct": round(100 * r["b"], 2), "avg_step_pct": round(100 * r["g"], 2),
                                   "n_beats": r["n_beats"], "n_steps": r["n_steps"]})
        for r in n3:
            h = r["N3_half"] * scale
            out["capex"].append({"ticker": r["ticker"], "after_report": r["after_report"], "capex_point": round(r["N3_point"], 2),
                                 "capex_low": round(r["N3_point"] * (1 - h), 2), "capex_high": round(r["N3_point"] * (1 + h), 2),
                                 "half_pct": round(100 * h, 2), "momentum": round(r["N3_momentum"], 2),
                                 "implied": round(r["N3_implied"], 2) if r["N3_implied"] else None})
        print(json.dumps(out, indent=1))
        return
    rows = prints_forecasts(prints, cons)
    n3, n4 = capex_forecasts(cons)
    res = {"window": WINDOW, "counts": {"print_rows_on_file": len(prints), "window_forecasts": len(rows)},
           "N1_revenue": card(rows, "N1"), "N2_next_guide": card(rows, "N2"), "N3_quarter_capex": card(n3, "N3"),
           "N4_annual_capex_guide": card(n4, "N4"),
           "N1_primary_only": card([r for r in rows if r["quality"] == "primary"], "N1"),
           "rows": rows, "capex_rows": n3, "capex_guide_rows": n4}
    (D / "results_numeric.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
    if "--json" in sys.argv:
        print(json.dumps(res, indent=1)); return
    for k in ("N1_revenue", "N2_next_guide", "N3_quarter_capex", "N4_annual_capex_guide", "N1_primary_only"):
        print(k, json.dumps(res[k]))
    if "--rows" in sys.argv:
        for r in rows:
            def pe(k):
                return f"{100 * (r[k + '_point'] / r[k + '_actual'] - 1):+.2f}%" if r.get(k + "_actual") else "n/a"
            print(f"  {r['date']} {r['ticker']:5} guide {r['guide_mid']:.2f} | rev fc {r['N1_point']:.2f} ±{100 * r['N1_half']:.1f}% "
                  f"act {r['N1_actual']} err {pe('N1')} | next-guide fc {r['N2_point']:.2f} ±{100 * r['N2_half']:.1f}% act {r['N2_actual']} err {pe('N2')}")
        for r in n3:
            print(f"  {r['date']} {r['ticker']:5} capex fc {r['N3_point']:.2f} ±{100 * r['N3_half']:.1f}% act {r['N3_actual']} "
                  f"err {100 * (r['N3_point'] / r['N3_actual'] - 1):+.2f}% (momentum {r['momentum']:.2f}, implied {r['implied']})")
        for r in n4:
            print(f"  {r['date']} {r['ticker']:5} annual guide fc {r['N4_point']:.1f} ±{100 * r['N4_half']:.1f}% act {r['N4_actual']} "
                  f"err {100 * (r['N4_point'] / r['N4_actual'] - 1):+.2f}%")


if __name__ == "__main__":
    main()
