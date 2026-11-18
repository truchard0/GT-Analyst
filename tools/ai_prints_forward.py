#!/usr/bin/env python3
"""Forward point-and-range forecasts for the next AI-trade prints, from the V2 model in tools/ai_prints_numeric.py.

Same model, no judgment per company. The only thing added here is the range re-fit that PREREG.md allows for the
forward calls: each target's 80% half-width is multiplied by the factor that would have given 80% coverage in the
backtest (revenue 1.73, next guide 1.69), and the honest forward coverage of that re-fit is estimated leave-one-out.
Capex ranges are left at the pre-registered width (10 backtest rows is too few to re-fit).

    python tools/ai_prints_forward.py            # writes data/ai_prints_backtest/forward_20261118.json and prints it
    python tools/ai_prints_forward.py --score    # later: score the registered forecasts against actuals filled in

Stdlib only. The JSON is the registration: commit it before any of these reports is published.
"""
import json, math, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ai_prints_numeric as m

OUT = m.D / "forward_20261118.json"

# Next report per company: date status and the document that settles the number. Dates are from
# research_notes/AI trade forecasting framework/catalyst_calendar_consensus.md (18 Nov 2026).
NEXT = {
    "AVGO": ("fiscal Q4 2026 (quarter ended 1 Nov 2026)", "2026-12-09", "confirmed", "2026-12-11",
             "Broadcom Q4 FY2026 earnings release (8-K Exhibit 99.1): net revenue"),
    "ORCL": ("fiscal Q2 2027 (quarter ended 30 Nov 2026)", "2026-12-09 to 2026-12-14", "expected, not announced", "2026-12-21",
             "Oracle Q2 FY2027 earnings release (8-K Exhibit 99.1): total revenues, USD"),
    "MU": ("fiscal Q1 2027 (quarter ended about 3 Dec 2026)", "2026-12-15", "expected, not announced", "2026-12-22",
           "Micron Q1 FY2027 earnings release (8-K Exhibit 99.1): revenue"),
    "TSM": ("Q4 2026 (quarter ended 31 Dec 2026)", "2027-01-14 or 2027-01-21", "expected, not announced", "2027-01-22",
            "TSMC Q4 2026 earnings release / management report (6-K): net revenue in US dollars"),
    "META": ("Q4 2026", "about 2027-01-27", "expected, not announced", "2027-02-12",
             "Meta Q4 2026 earnings release (8-K Exhibit 99.1): total revenue"),
    "MSFT": ("fiscal Q2 2027 (Oct-Dec 2026)", "about 2027-01-27", "expected, not announced", "2027-02-12",
             "Microsoft Q2 FY2027 earnings call: capital expenditures including finance leases, as stated by the CFO"),
    "GOOGL": ("Q4 2026", "about 2027-02-02", "expected, not announced", "2027-02-12",
              "Alphabet Q4 2026 earnings release: purchases of property and equipment, three months ended 31 Dec 2026"),
    "AMZN": ("Q4 2026", "about 2027-02-04", "expected, not announced", "2027-02-12",
             "Amazon Q4 2026 earnings release (8-K Exhibit 99.1): net sales; capex = purchases of property and equipment, gross, three months"),
    "NVDA": ("fiscal Q4 2027 (quarter ended 31 Jan 2027, 14 weeks)", "2027-02-24 to 2027-03-03", "expected, not announced", "2027-03-10",
             "Nvidia Q4 FY2027 earnings release (8-K Exhibit 99.1): revenue"),
}
CAPEX_BASIS = {
    "MSFT": "capital expenditures including finance leases, as stated on the call",
    "GOOGL": "purchases of property and equipment (cash flow statement)",
    "AMZN": "purchases of property and equipment, gross (cash flow statement)",
    "META": "capital expenditures including principal payments on finance leases (release)",
    "ORCL": "capital expenditures (cash flow statement, gross of customer prepayments)",
}
FOCUS = ["AVGO", "ORCL", "MU", "TSM", "META", "AMZN", "NVDA"]            # the names asked for, in report order
CAPEX_FOCUS = ["ORCL", "MSFT", "META", "GOOGL", "AMZN"]


def ratios(rows, k):
    return [abs(r[k + "_actual"] / r[k + "_point"] - 1) / r[k + "_half"] for r in rows if r.get(k + "_actual") and r.get(k + "_point")]


def scale80(rs):
    rs = sorted(rs)
    return rs[min(len(rs) - 1, math.ceil(0.8 * len(rs)) - 1)]


def loo_coverage(rs):
    """Refit the 80% factor without row i, then ask whether row i falls inside. The honest forward coverage."""
    hits = 0
    for i, r in enumerate(rs):
        hits += r <= scale80(rs[:i] + rs[i + 1:])
    return hits / len(rs)


def build():
    cons = m.load_consensus()
    prints = m.load_prints()
    back = m.prints_forecasts(prints, cons)
    n3, _ = m.capex_forecasts(cons)
    fit = {}
    for k, rows in (("N1", back), ("N2", back), ("N3", n3)):
        rs = ratios(rows, k)
        fit[k] = {"n": len(rs), "scale_for_80pct": round(scale80(rs), 2), "coverage_at_scale_1": round(sum(r <= 1 for r in rs) / len(rs), 3),
                  "leave_one_out_coverage_after_refit": round(loo_coverage(rs), 3)}
    s1, s2, s3 = fit["N1"]["scale_for_80pct"], fit["N2"]["scale_for_80pct"], 1.0
    fwd = {r["ticker"]: r for r in m.prints_forecasts(prints, cons, forward=True)}
    cap = {r["ticker"]: r for r in m.capex_forecasts(cons, forward=True)[0]}
    out = {"registered": "2026-11-18", "model": "tools/ai_prints_numeric.py (PREREG.md V2), unchanged",
           "range_refit": {"revenue": {"factor": s1, **fit["N1"]}, "next_guide": {"factor": s2, **fit["N2"]},
                           "quarter_capex": {"factor": s3, **fit["N3"], "note": "not re-fitted: 10 backtest rows"}},
           "revenue": [], "next_guide": [], "quarter_capex": []}
    for t in FOCUS:
        r = fwd[t]
        period, date, status, horizon, source = NEXT[t]
        h1, h2 = r["N1_half"] * s1, r["N2_half"] * s2
        base = {"ticker": t, "period": period, "report_date": date, "date_status": status, "ledger_horizon": horizon, "resolution_source": source}
        out["revenue"].append({**base, "company_guide_mid": r["guide_mid"], "avg_beat_last4_pct": round(100 * r["b"], 2),
                               "point": round(r["N1_point"], 2), "low": round(r["N1_point"] * (1 - h1), 2), "high": round(r["N1_point"] * (1 + h1), 2),
                               "half_width_pct": round(100 * h1, 1), "actual": None})
        out["next_guide"].append({**base, "avg_step_last4_pct": round(100 * r["g"], 2),
                                  "point": round(r["N2_point"], 2), "low": round(r["N2_point"] * (1 - h2), 2), "high": round(r["N2_point"] * (1 + h2), 2),
                                  "half_width_pct": round(100 * h2, 1), "actual": None})
    for t in CAPEX_FOCUS:
        r = cap[t]
        period, date, status, horizon, source = NEXT[t]
        h = r["N3_half"] * s3
        out["quarter_capex"].append({"ticker": t, "period": period, "report_date": date, "date_status": status, "ledger_horizon": horizon,
                                     "resolution_source": source if t in ("MSFT", "GOOGL") else source.split(":")[0] + ": " + CAPEX_BASIS[t],
                                     "basis": CAPEX_BASIS[t], "last_quarter": round(r["N3_b0"], 2),
                                     "momentum_leg": round(r["N3_momentum"], 2), "guide_implied_leg": round(r["N3_implied"], 2) if r["N3_implied"] else None,
                                     "point": round(r["N3_point"], 2), "low": round(r["N3_point"] * (1 - h), 2), "high": round(r["N3_point"] * (1 + h), 2),
                                     "half_width_pct": round(100 * h, 1), "actual": None})
    return out


def score():
    d = json.loads(OUT.read_text(encoding="utf-8"))
    for k in ("revenue", "next_guide", "quarter_capex"):
        done = [r for r in d[k] if r.get("actual")]
        if not done:
            print(k, "nothing reported yet"); continue
        err = sorted(abs(r["point"] / r["actual"] - 1) for r in done)
        inside = sum(r["low"] <= r["actual"] <= r["high"] for r in done)
        print(f"{k}: {len(done)} reported, median miss {100 * err[len(err) // 2]:.2f}%, inside the range {inside} of {len(done)}")


if __name__ == "__main__":
    if "--score" in sys.argv:
        score()
    else:
        res = build()
        if OUT.exists() and "--overwrite" not in sys.argv:
            sys.exit(f"{OUT.name} already exists: it is the registration. Use --overwrite only before any of these reports is out.")
        OUT.write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8", newline="\n")
        print(json.dumps(res, indent=1))
