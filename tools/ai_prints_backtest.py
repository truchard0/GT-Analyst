#!/usr/bin/env python3
"""Score the AI prints backtest against the pre-registered rules in data/ai_prints_backtest/PREREG.md.

Reads data/ai_prints_backtest/prints.csv, capex.csv and (optional) prices.csv. Stdlib only.
    python3 tools/ai_prints_backtest.py            # print the scorecard
    python3 tools/ai_prints_backtest.py --json     # machine-readable
"""
import csv, json, pathlib, sys

D = pathlib.Path(__file__).resolve().parent.parent / "data" / "ai_prints_backtest"
P = {"R1": 0.86, "R2": 0.72, "R3": 0.88}          # pre-registered, do not edit after 2026-11-18
WINDOW = ("2026-05-18", "2026-11-17")


def f(x):
    try:
        return float(str(x).replace(",", "").strip())
    except Exception:
        return None


def rows(name):
    fp = D / name
    if not fp.exists():
        return []
    with open(fp, newline="", encoding="utf-8") as h:
        return [r for r in csv.DictReader(h)]


def score(outcomes, p):
    n = len(outcomes)
    if not n:
        return {"n": 0}
    hits = sum(outcomes)
    brier = sum((p - o) ** 2 for o in outcomes) / n
    base = hits / n
    return {"n": n, "hits": hits, "hit_rate": round(base, 3), "stated_p": p, "brier": round(brier, 4),
            "brier_coin": 0.25, "brier_base_rate": round(base * (1 - base), 4)}


def main():
    allp = rows("prints.csv") + rows("prints_suppliers.csv") + rows("prints_buyers.csv")   # data arrived in two files
    for r in allp:                                         # midpoints may be blank when only a range was given
        for m, lo, hi in (("guide_mid", "guide_low", "guide_high"), ("next_guide_mid", "next_guide_low", "next_guide_high")):
            if f(r.get(m)) is None and f(r.get(lo)) is not None and f(r.get(hi)) is not None:
                r[m] = (f(r[lo]) + f(r[hi])) / 2
    prints = [r for r in allp if WINDOW[0] <= r["report_date"] <= WINDOW[1]]
    capex = [r for r in rows("capex.csv") if WINDOW[0] <= r["report_date"] <= WINDOW[1]]
    px = {}
    for r in rows("prices.csv"):
        px.setdefault(r["ticker"], []).append((r["date"], f(r["close"])))
    for t in px:
        px[t].sort()
    out = {"window": WINDOW, "excluded": [], "detail": []}
    r1, r2, r4, r1q = [], [], [], {"primary": [], "other": []}
    for r in prints:
        gm, act, ng = f(r.get("guide_mid")), f(r.get("actual_revenue")), f(r.get("next_guide_mid"))
        d = {"ticker": r["ticker"], "period": r["fiscal_period"], "date": r["report_date"]}
        if gm is None or act is None:
            out["excluded"].append({**d, "rule": "R1", "why": "no numeric guide or actual"})
        else:
            o = 1 if act >= gm else 0
            r1.append(o); d["R1"] = o; d["vs_mid_pct"] = round((act / gm - 1) * 100, 2)
            r1q["primary" if r.get("quality", "").strip() == "primary" else "other"].append(o)
        if ng is None or act is None:
            out["excluded"].append({**d, "rule": "R2", "why": "no numeric next-quarter guide"})
        else:
            o2 = 1 if ng > act else 0
            r2.append(o2); d["R2"] = o2; d["next_vs_actual_pct"] = round((ng / act - 1) * 100, 2)
        # R4: next-session reaction. AMC report -> close(report day) to next close. BMO -> prior close to report-day close.
        s = px.get(r["ticker"])
        if s and "R1" in d:
            dates = [x[0] for x in s]
            timing = (r.get("timing") or "AMC").strip().upper()
            i = next((k for k, dt in enumerate(dates) if dt >= r["report_date"]), None)
            if i is not None:
                a, b = (i, i + 1) if timing == "AMC" else (i - 1, i)
                if 0 <= a and b < len(s) and s[a][1] and s[b][1]:
                    mv = s[b][1] / s[a][1] - 1
                    d["next_session_pct"] = round(mv * 100, 2)
                    if d["R1"] == 1:
                        r4.append(1 if mv > 0 else 0)
        out["detail"].append(d)
    r3 = []
    for r in capex:
        ch = (r.get("change") or "").strip().lower()
        if ch in ("raise", "hold", "cut"):
            o = 0 if ch == "cut" else 1
            r3.append(o)
            out["detail"].append({"ticker": r["ticker"], "date": r["report_date"], "R3": o, "capex_change": ch})
        else:
            out["excluded"].append({"ticker": r["ticker"], "date": r["report_date"], "rule": "R3", "why": "no capex statement"})
    out["R1"] = score(r1, P["R1"]); out["R2"] = score(r2, P["R2"]); out["R3"] = score(r3, P["R3"])
    out["R1_by_quality"] = {k: score(v, P["R1"]) for k, v in r1q.items()}
    n4 = len(r4)
    out["R4"] = {"n_beats_with_prices": n4, "closed_higher": sum(r4), "freq": round(sum(r4) / n4, 3) if n4 else None,
                 "claim": "between 0.40 and 0.65", "claim_holds": (0.40 <= sum(r4) / n4 <= 0.65) if n4 else None}
    out["raises"] = sum(1 for r in capex if (r.get("change") or "").strip().lower() == "raise")
    if "--json" in sys.argv:
        print(json.dumps(out, indent=1)); return
    for k in ("R1", "R2", "R3"):
        print(k, out[k])
    print("R1 by source quality", out["R1_by_quality"])
    print("R4", out["R4"], "| capex raises:", out["raises"], "of", len(r3))
    print("excluded:", len(out["excluded"]))
    for d in sorted(out["detail"], key=lambda x: (x["date"], x["ticker"])):
        print("  ", d)


if __name__ == "__main__":
    main()
