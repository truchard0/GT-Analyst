#!/usr/bin/env python3
"""Five-year AI prints backtest (rules: data/ai_prints_backtest/PREREG_5Y.md). Same V2 model as ai_prints_numeric.py,
unchanged; this file only widens the window, narrows the names and adds the pre-registered splits.

    python tools/ai_prints_5y.py           # summary; writes data/ai_prints_backtest/results_5y.json
    python tools/ai_prints_5y.py --rows    # ... plus every forecast row
Stdlib only.
"""
import csv, datetime, json, pathlib, statistics, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ai_prints_numeric as m

D = m.D
PRINT_NAMES = {"NVDA", "AVGO", "MU", "TSM", "AMZN", "META"}
CAPEX_NAMES = {"MSFT", "GOOGL", "AMZN", "META"}
WINDOW = ("2021-11-18", "2026-11-17")
SIX_MONTH = ("2026-05-18", "2026-11-17")
EXTRA = {"prints": ["5y/prints_nvda_avgo.csv", "5y/prints_mu_tsm.csv", "5y/prints_amzn_meta.csv"],
         "consensus.csv": ["5y/consensus_nvda_avgo.csv", "5y/consensus_mu_tsm.csv", "5y/consensus_amzn_meta.csv"],
         "capex_history.csv": ["5y/capex_hyperscalers.csv"]}
STATED = {"R1": 0.86, "R2": 0.72}
_read = m.read


def read(name):
    rows = _read(name) + [r for x in EXTRA.get(name, []) for r in _read(x)]
    if name == "capex_history.csv":
        rows = [r for r in rows if r.get("ticker", "").upper() in CAPEX_NAMES]
    if name == "consensus.csv":   # TSMC consensus is quoted in NT dollars; the actuals are US dollars, so it cannot be compared
        rows = [r for r in rows if "TWD" not in (r.get("currency_unit") or "").upper()]
    return rows


def year_of(d):
    for i in range(5):
        lo = datetime.date(2021 + i, 11, 18).isoformat()
        hi = datetime.date(2022 + i, 11, 17).isoformat()
        if lo <= d <= hi:
            return f"Y{i + 1} ({lo[:7]} to {hi[:7]})"
    return "outside"


def prices():
    out = {}
    fp = D / "5y" / "prices_5y.csv"
    if fp.exists():
        for r in csv.DictReader(open(fp, encoding="utf-8")):
            out.setdefault(r["ticker"], []).append((r["date"], float(r["close"])))
    return out


def reaction(px, ticker, date, timing):
    """Next-session close vs the last close before the news (AMC: close on the report date; BMO: the day before)."""
    s = px.get(ticker)
    if not s:
        return None
    dates = [d for d, _ in s]
    if timing.upper().startswith("B"):
        before = [c for d, c in s if d < date]
        after = [c for d, c in s if d >= date]
    else:
        before = [c for d, c in s if d <= date]
        after = [c for d, c in s if d > date]
    if not before or not after:
        return None
    return after[0] / before[-1] - 1


def brier(p, hits):
    return round(statistics.mean((p - h) ** 2 for h in hits), 3) if hits else None


def main():
    m.read = read
    m.PRINT_FILES = m.PRINT_FILES + EXTRA["prints"]
    m.WINDOW = WINDOW
    cons = m.load_consensus()
    prints = [p for p in m.load_prints() if p["ticker"] in PRINT_NAMES]
    rows = m.prints_forecasts(prints, cons)
    n3, n4 = m.capex_forecasts(cons)
    by_key = {(p["ticker"], p["date"]): p for p in prints}
    px = prices()
    for r in rows:
        p = by_key[(r["ticker"], r["date"])]
        r["year"] = year_of(r["date"])
        r["cycle"] = "down" if r["N2_actual"] and r["N1_actual"] and r["N2_actual"] < r["N1_actual"] else "up"
        r["timing"] = p["timing"]
        r["R1"] = int(r["N1_actual"] >= r["guide_mid"]) if r["N1_actual"] else None
        r["R2"] = int(r["N2_actual"] > r["N1_actual"]) if r["N2_actual"] and r["N1_actual"] else None
        r["reaction"] = reaction(px, r["ticker"], r["date"], p["timing"])
    for r in n3:
        r["year"] = year_of(r["date"])
    res = {"window": WINDOW, "names": sorted(PRINT_NAMES), "capex_names": sorted(CAPEX_NAMES),
           "counts": {"print_rows_on_file": len(prints), "scored_print_rows": len(rows), "scored_capex_rows": len(n3)},
           "N1": m.card(rows, "N1"), "N2": m.card(rows, "N2"), "N3": m.card(n3, "N3"), "splits": {}}
    # forward refit factors registered on 18 Nov from the 6-month window: how do they hold over 5 years?
    for k, f in (("N1", 1.73), ("N2", 1.69)):
        xs = [r for r in rows if r.get(k + "_actual")]
        out_of_window = [r for r in xs if r["date"] < SIX_MONTH[0]]
        res[k + "_refit_coverage"] = {
            "factor": f, "all": round(sum(abs(r[k + "_actual"] / r[k + "_point"] - 1) <= f * r[k + "_half"] for r in xs) / len(xs), 3),
            "before_the_fit_window": round(sum(abs(r[k + "_actual"] / r[k + "_point"] - 1) <= f * r[k + "_half"] for r in out_of_window) / max(1, len(out_of_window)), 3),
            "n_before": len(out_of_window)}
    for label, key in (("year", "year"), ("cycle", "cycle"), ("company", "ticker")):
        groups = sorted({r[key] for r in rows})
        res["splits"][label] = {g: {"N1": m.card([r for r in rows if r[key] == g], "N1"),
                                    "N2": m.card([r for r in rows if r[key] == g], "N2")} for g in groups}
    res["splits"]["six_month_window"] = {"N1": m.card([r for r in rows if r["date"] >= SIX_MONTH[0]], "N1"),
                                         "N2": m.card([r for r in rows if r["date"] >= SIX_MONTH[0]], "N2")}
    res["splits"]["capex_by_year"] = {g: m.card([r for r in n3 if r["year"] == g], "N3") for g in sorted({r["year"] for r in n3})}
    v1 = {}
    for rule in ("R1", "R2"):
        for grp, sel in (("all", rows), ("up", [r for r in rows if r["cycle"] == "up"]), ("down", [r for r in rows if r["cycle"] == "down"])):
            hits = [r[rule] for r in sel if r[rule] is not None]
            v1[f"{rule}_{grp}"] = {"n": len(hits), "hit_rate": round(sum(hits) / len(hits), 3) if hits else None,
                                   "brier_at_stated": brier(STATED[rule], hits), "coin": 0.25}
    beats = [r for r in rows if r["R1"] == 1 and r["reaction"] is not None]
    v1["R4_up_after_beat"] = {"n": len(beats), "share_up": round(sum(r["reaction"] > 0 for r in beats) / len(beats), 3) if beats else None,
                              "median_move_pct": round(100 * statistics.median(r["reaction"] for r in beats), 2) if beats else None,
                              "claim": "40-65%"}
    res["V1"] = v1
    res["rows"] = [{k: v for k, v in r.items()} for r in rows]
    res["capex_rows"] = n3
    (D / "results_5y.json").write_text(json.dumps(res, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
    for k in ("counts", "N1", "N2", "N3", "N1_refit_coverage", "N2_refit_coverage", "V1"):
        print(k, json.dumps(res[k]))
    for label in ("year", "cycle", "company"):
        for g, c in res["splits"][label].items():
            print(f"{label:8} {g:28} N1 n={c['N1'].get('n')} med={c['N1'].get('median_abs_err_pct')} naive={c['N1'].get('b0', {}).get('median_abs_err_pct')} | "
                  f"N2 n={c['N2'].get('n')} med={c['N2'].get('median_abs_err_pct')} naive={c['N2'].get('b0', {}).get('median_abs_err_pct')}")
    for g, c in res["splits"]["capex_by_year"].items():
        print("capex", g, c.get("n"), c.get("median_abs_err_pct"), c.get("b0", {}).get("median_abs_err_pct"))
    if "--rows" in sys.argv:
        for r in rows:
            e1 = 100 * (r["N1_point"] / r["N1_actual"] - 1) if r["N1_actual"] else None
            e2 = 100 * (r["N2_point"] / r["N2_actual"] - 1) if r["N2_actual"] else None
            print(r["date"], r["ticker"], r["cycle"], "N1", round(r["N1_point"], 2), r["N1_actual"], None if e1 is None else round(e1, 1),
                  "N2", round(r["N2_point"], 2), r["N2_actual"], None if e2 is None else round(e2, 1), "react", r["reaction"] and round(100 * r["reaction"], 1))


if __name__ == "__main__":
    main()
