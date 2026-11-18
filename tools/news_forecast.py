#!/usr/bin/env python3
"""News-informed forecast of AI prints: packet builder and scorer. Rules: data/news_forecast/PREREG.md.

    python tools/news_forecast.py packets     # writes data/news_forecast/packets/<date>_<ticker>.md (17 reports)
    python tools/news_forecast.py score       # scores data/news_forecast/forecasts.json against the four baselines

Point-in-time: every packet item is dated strictly before 00:00 UTC on the report date. Stdlib only.
"""
import csv, datetime, json, pathlib, re, statistics, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BT = ROOT / "data" / "ai_prints_backtest"
NF = ROOT / "data" / "news_forecast"
PK = NF / "packets"
WINDOW = ("2026-08-01", "2026-11-17")
SET_A = {("AMAT", "2026-08-13"), ("DELL", "2026-09-01"), ("MU", "2026-09-30"), ("TSM", "2026-10-15")}
SET_B = {("MU", "2026-09-30"), ("ASML", "2026-10-14"), ("META", "2026-10-21"), ("AMZN", "2026-10-29"), ("AMD", "2026-11-03")}
NAME = {"NVDA": "Nvidia", "AVGO": "Broadcom", "MU": "Micron", "TSM": "TSMC", "AMD": "AMD", "MRVL": "Marvell", "ASML": "ASML",
        "AMAT": "Applied Materials", "LRCX": "Lam Research", "KLAC": "KLA", "DELL": "Dell", "AMZN": "Amazon", "META": "Meta",
        "ORCL": "Oracle"}
KW = {"AMD": r"\bAMD\b|Advanced Micro", "AMAT": r"Applied Materials|\bAMAT\b", "NVDA": r"Nvidia|\bNVDA\b", "MRVL": r"Marvell",
      "DELL": r"\bDell\b", "AVGO": r"Broadcom|\bAVGO\b", "ORCL": r"Oracle", "MU": r"Micron|DRAM|\bHBM\b|memory chip|memory price",
      "ASML": r"ASML|lithograph", "TSM": r"TSMC|Taiwan Semi", "LRCX": r"Lam Research", "META": r"\bMeta\b", "KLAC": r"\bKLA\b",
      "AMZN": r"Amazon|\bAWS\b"}
THEME = r"semiconductor|chipmaker|chip stock|\bchips?\b|data cent|capex|capital spending|hyperscaler|AI spending|AI infrastructure|wafer"


def rd(fp):
    with open(fp, newline="", encoding="utf-8-sig") as h:
        return list(csv.DictReader(h))


def f(x):
    try:
        return float(str(x).replace(",", ""))
    except Exception:
        return None


def mid(r, lo, hi, m):
    v = f(r.get(m))
    if v is not None:
        return v
    a, b = f(r.get(lo)), f(r.get(hi))
    return (a + b) / 2 if a is not None and b is not None else None


def ago(date, days):
    return (datetime.date.fromisoformat(date) - datetime.timedelta(days=days)).isoformat()


def prints():
    seen, out = set(), []
    for n in ("prints_history_a.csv", "prints_history_b.csv", "prints_suppliers.csv", "prints_buyers.csv"):
        for r in rd(BT / n):
            k = (r["ticker"], r["report_date"])
            if k in seen:
                continue
            seen.add(k)
            out.append({"t": r["ticker"], "d": r["report_date"], "p": r.get("fiscal_period", ""), "g": mid(r, "guide_low", "guide_high", "guide_mid"),
                        "a": f(r.get("actual_revenue")), "ng": mid(r, "next_guide_low", "next_guide_high", "next_guide_mid"),
                        "unit": r.get("currency_unit", "")})
    return sorted(out, key=lambda r: r["d"])


def rows():
    res = json.loads((BT / "results_numeric.json").read_text(encoding="utf-8"))
    return [r for r in res["rows"] if WINDOW[0] <= r["date"] <= WINDOW[1]]


def packet(r, P, capex, heads, tsmc):
    t, d = r["ticker"], r["date"]
    L = [f"# Forecast packet: {NAME[t]} ({t}), report of {d}", "",
         f"You are forecasting {NAME[t]}'s report published on {d} ({r['period']}). Everything below was public before "
         f"00:00 UTC on {d}. Nothing about the report itself is included.", "",
         f"The company's own guide for the quarter being reported: midpoint {r['guide_mid']:.3f} (company currency unit, bn).", "",
         "## 1. The company's last four reports (bn)", "| Report date | Period | Guide midpoint | Actual revenue | Next-quarter guide midpoint given |", "|---|---|---|---|---|"]
    own = [p for p in P if p["t"] == t and p["d"] < d][-4:]
    for p in own:
        L.append(f"| {p['d']} | {p['p']} | {p['g']} | {p['a']} | {p['ng']} |")
    L += ["", "## 2. Mechanical forecast (company guide x its average beat; then x its average guide step-up)",
          f"- Revenue this quarter: {r['N1_point']:.3f}, 80% range +/-{100 * r['N1_half']:.1f}%",
          f"- Next-quarter guide midpoint: {r['N2_point']:.3f}, 80% range +/-{100 * r['N2_half']:.1f}%",
          "- Backtest of this mechanical model: revenue median miss about 1%; next-quarter guide median miss about 5.6%, "
          "usually too LOW, because guides stepped up faster than each company's own history.", "",
          "## 3. Other companies' reports in the 90 days before (revenue vs own guide; next guide vs actual)",
          "| Date | Company | Actual vs guide | Next guide vs actual |", "|---|---|---|---|"]
    for p in P:
        if p["t"] != t and ago(d, 90) <= p["d"] < d and p["g"] and p["a"]:
            ng = f"{100 * (p['ng'] / p['a'] - 1):+.1f}%" if p["ng"] else "n/a"
            L.append(f"| {p['d']} | {NAME.get(p['t'], p['t'])} | {100 * (p['a'] / p['g'] - 1):+.1f}% | {ng} |")
    L += ["", "## 4. Buyers' capex statements in the 120 days before (bn)", "| Date | Company | Quarter capex | Annual guide before | Annual guide after |", "|---|---|---|---|---|"]
    for c in capex:
        if ago(d, 120) <= c["report_date"] < d:
            pb = mid(c, "prior_guide_low", "prior_guide_high", "prior_guide_mid")
            nw = mid(c, "new_guide_low", "new_guide_high", "new_guide_mid")
            L.append(f"| {c['report_date']} | {NAME.get(c['ticker'], c['ticker'])} ({c['guide_year']}) | {c['reported_quarter_capex']} | {pb or 'n/a'} | {nw or 'n/a'} |")
    L += ["", "## 5. TSMC monthly revenue released before the report (NT$ bn)"]
    for m in tsmc:
        if m["released"] < d:
            L.append(f"- {m['month']}: {m['revenue_ntd_bn']} (released {m['released']})")
    own_h = [h for h in heads if ago(d, 45) <= h["published_utc"][:10] < d and re.search(KW[t], h["title"], re.I)][-40:]
    seen = {h["title"] for h in own_h}
    theme = [h for h in heads if ago(d, 45) <= h["published_utc"][:10] < d and h["title"] not in seen and re.search(THEME, h["title"], re.I)][-40:]
    L += ["", f"## 6. Headlines naming {NAME[t]} (45 days before, most recent last; titles only)"]
    L += [f"- {h['published_utc'][:10]} {h['title']}" for h in own_h] or ["- none in the cache"]
    L += ["", "## 7. Headlines on the AI-chip and capex theme (45 days before, most recent last)"]
    L += [f"- {h['published_utc'][:10]} {h['title']}" for h in theme] or ["- none in the cache"]
    return "\n".join(L) + "\n"


def build():
    P = prints()
    capex = rd(BT / "capex_history.csv")
    heads = sorted(rd(ROOT / "data" / "ai_stress" / "headlines.csv"), key=lambda h: h["published_utc"])
    tsmc = rd(NF / "tsmc_monthly.csv")
    PK.mkdir(parents=True, exist_ok=True)
    for r in rows():
        fp = PK / f"{r['date']}_{r['ticker']}.md"
        fp.write_text(packet(r, P, capex, heads, tsmc), encoding="utf-8", newline="\n")
        print(fp.name, len(fp.read_text(encoding="utf-8")), "chars")


def stats(xs):
    return (round(statistics.median(xs), 2), round(statistics.mean(xs), 2)) if xs else (None, None)


def score():
    fc = json.loads((NF / "forecasts.json").read_text(encoding="utf-8"))
    out = {}
    for k in ("N2", "N1"):
        per = []
        for r in rows():
            key = f"{r['date']}_{r['ticker']}"
            if key not in fc or not r.get(k + "_actual"):
                continue
            a = r[k + "_actual"]
            n = fc[key]
            e = lambda v: abs(v / a - 1) * 100 if v else None
            per.append({"key": key, "set": "test" if (r["ticker"], r["date"]) in SET_A | SET_B else "control",
                        "A": (r["ticker"], r["date"]) in SET_A, "B": (r["ticker"], r["date"]) in SET_B, "actual": a,
                        "naive": e(r[k + "_b0"]), "mech": e(r[k + "_point"]), "news": e(n[k + "_point"]), "cons": e(r.get(k + "_b1")),
                        "news_point": n[k + "_point"], "mech_point": r[k + "_point"], "cons_point": r.get(k + "_b1"),
                        "news_in": n[k + "_low"] <= a <= n[k + "_high"],
                        "mech_in": abs(a / r[k + "_point"] - 1) <= r[k + "_half"] * (1.73 if k == "N1" else 1.69)})
        sets = {"test": [p for p in per if p["set"] == "test"], "control": [p for p in per if p["set"] == "control"],
                "A": [p for p in per if p["A"]], "B": [p for p in per if p["B"]], "all": per}
        card = {}
        for s, ps in sets.items():
            c = {"n": len(ps)}
            for m in ("naive", "mech", "news", "cons"):
                c[m + "_median_mean"] = stats([p[m] for p in ps if p[m] is not None])
            c["news_closer_than_mech"] = sum(p["news"] < p["mech"] for p in ps)
            c["news_closer_than_cons"] = sum(p["news"] < p["cons"] for p in ps if p["cons"] is not None)
            c["news_cover80"] = sum(p["news_in"] for p in ps)
            c["mech_cover80_refit"] = sum(p["mech_in"] for p in ps)
            card[s] = c
        t, ctl, al = card["test"], card["control"], card["all"]
        card["pass"] = {"1_news_helps": t["news_median_mean"][0] < t["mech_median_mean"][0] and t["news_closer_than_mech"] >= 5,
                        "2_no_harm": ctl["news_median_mean"][0] <= ctl["mech_median_mean"][0] + 0.5,
                        "3_near_consensus": al["news_median_mean"][0] <= al["cons_median_mean"][0] + 1.0}
        out[k] = {"card": card, "rows": per}
    (NF / "results.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8", newline="\n")
    for k in out:
        print(k, json.dumps(out[k]["card"], indent=1))


if __name__ == "__main__":
    {"packets": build, "score": score}[sys.argv[1]]()
