#!/usr/bin/env python3
"""One-off (18 Nov 2026 UTC): log the registered forward range forecasts as ledger rows and wire them into the map.

Reads data/ai_prints_backtest/forward_20261118.json (written by tools/ai_prints_forward.py), adds one row per
forecast through `pipeline/ledger.py add` (so every lint and guard runs), then appends the new IDs to the matching
checkpoint node in data/timelines.json. Refuses to run twice: it checks for its own prediction texts first.

    python tools/ledger_forward_ranges_20261118.py --dry-run
    python tools/ledger_forward_ranges_20261118.py
"""
import json, pathlib, re, sqlite3, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FWD = ROOT / "data" / "ai_prints_backtest" / "forward_20261118.json"
TL = ROOT / "data" / "timelines.json"
DB = ROOT / "ledger" / "ledger.db"
TAG = "[range call, registered 2026-11-18]"

NAME = {"AVGO": "Broadcom", "ORCL": "Oracle", "MU": "Micron", "TSM": "TSMC", "META": "Meta", "AMZN": "Amazon",
        "NVDA": "Nvidia", "MSFT": "Microsoft", "GOOGL": "Alphabet"}
SECTOR = {"AVGO": "semis", "MU": "memory", "TSM": "semis", "NVDA": "semis", "ORCL": "hyperscalers", "META": "hyperscalers",
          "AMZN": "hyperscalers", "MSFT": "hyperscalers", "GOOGL": "hyperscalers"}
NODE = {"AVGO": "avgo-fq4", "MU": "memory-prints", "TSM": "tsmc-q4", "NVDA": "nvda-fq4", "ORCL": "orcl-fq2",
        "META": "hyperscaler-q4-guides", "AMZN": "hyperscaler-q4-guides", "MSFT": "hyperscaler-q4-guides",
        "GOOGL": "hyperscaler-q4-guides"}
THRESHOLD_ROW = {("AVGO", "revenue"): None, ("MU", "revenue"): 124, ("MU", "next_guide"): 125, ("TSM", "revenue"): 127,
                 ("NVDA", "revenue"): 132, ("MSFT", "quarter_capex"): 129}
NEXT_GUIDE_SOURCE = {
    "AVGO": "the fiscal Q1 2027 revenue guide in the same Broadcom release ('approximately $X billion')",
    "ORCL": "the fiscal Q3 2027 total-revenue growth guide (USD) in the same Oracle release, converted to dollars on "
            "fiscal Q3 2026 revenue of $17.19B, midpoint",
    "MU": "midpoint of the fiscal Q2 2027 revenue guide in the same Micron release",
    "TSM": "midpoint of the Q1 2027 US-dollar revenue guide in the same TSMC release",
    "META": "midpoint of the Q1 2027 total-revenue guide in the same Meta release",
    "AMZN": "midpoint of the Q1 2027 net-sales guide in the same Amazon release",
    "NVDA": "midpoint of the fiscal Q1 2028 revenue guide in the same Nvidia release",
}
METHOD = ("Mechanical model tools/ai_prints_numeric.py (PREREG V2), registration data/ai_prints_backtest/forward_20261118.json "
          "(commit before the report). ")
VOID = ("VOID RULE: if the company has not reported by the horizon, the horizon is extended to the report date; "
        "not scored early.")
INDEP = ("Cluster ai-prints-range, not ai-prints: a range call scores the SIZE of the surprise on both sides and misses "
         "on an upside surprise that the threshold rows score as hits, so it is not the same bet restated.")


def money(x):
    return f"${x:,.2f}B"


def rows():
    d = json.loads(FWD.read_text(encoding="utf-8"))
    rf = d["range_refit"]
    out = []
    for r in d["revenue"]:
        t, n = r["ticker"], NAME[r["ticker"]]
        thr = THRESHOLD_ROW.get((t, "revenue"))
        out.append(dict(
            t=t, target="revenue", horizon=r["ledger_horizon"],
            event=f"{n} {r['period']} report, {r['report_date']} ({r['date_status']}). Company guide midpoint {money(r['company_guide_mid'])}; "
                  f"model point = guide x (1 + mean beat of the last 4 reports, {r['avg_beat_last4_pct']:+.2f}%) = {money(r['point'])}.",
            pred=f"{n} reports {r['period']} revenue between {money(r['low'])} and {money(r['high'])} inclusive "
                 f"(model point {money(r['point'])}, 80% range) {TAG}.",
            fals=f"{n}'s reported {r['period']} revenue is below {money(r['low'])} or above {money(r['high'])}.",
            sens=f"LEAN: neutral. LAYER L1. {METHOD}80% range = pre-registered half-width x {rf['revenue']['factor']} "
                 f"(the backtest factor for 80% coverage; leave-one-out coverage of that refit {100 * rf['revenue']['leave_one_out_coverage_after_refit']:.0f}% "
                 f"on 29 reports). Backtest: median miss 1.02% vs 1.91% consensus. Breaks on a surprise quarter outside the company's own beat "
                 f"history (Dell May, Micron June 2026). {INDEP}" + (f" Threshold row on the same print: #{thr}." if thr else "") +
                 f" RESOLUTION: {r['resolution_source']}. {VOID}"))
    for r in d["next_guide"]:
        t, n = r["ticker"], NAME[r["ticker"]]
        thr = THRESHOLD_ROW.get((t, "next_guide"))
        out.append(dict(
            t=t, target="next_guide", horizon=r["ledger_horizon"],
            event=f"{n} {r['period']} report, {r['report_date']} ({r['date_status']}): the next-quarter revenue guide. Model point = "
                  f"revenue point x (1 + mean step-up of the last 4 guides, {r['avg_step_last4_pct']:+.2f}%) = {money(r['point'])}.",
            pred=f"The next-quarter revenue guide {n} gives with its {r['period']} report has a midpoint between {money(r['low'])} and "
                 f"{money(r['high'])} inclusive (model point {money(r['point'])}, 80% range) {TAG}.",
            fals=f"The next-quarter revenue guide midpoint {n} gives with its {r['period']} report is below {money(r['low'])} or above "
                 f"{money(r['high'])}, or no numeric next-quarter revenue guide is given.",
            sens=f"LEAN: neutral. LAYER L1 (guide). {METHOD}80% range = pre-registered half-width x {rf['next_guide']['factor']} "
                 f"(leave-one-out coverage of the refit {100 * rf['next_guide']['leave_one_out_coverage_after_refit']:.0f}%). Backtest WEAK spot: "
                 f"median miss 5.6% vs 3.7% consensus, biased 4.8% low; ranges wide by construction. Breaks on a guided step-up the company's "
                 f"own history does not contain." + (" Nvidia's Q4 has 14 weeks, Q1 13: the model does not know the week count." if t == "NVDA" else "") +
                 f" {INDEP}" + (f" Threshold row on the same guide: #{thr}." if thr else "") +
                 f" RESOLUTION: {NEXT_GUIDE_SOURCE[t]}. {VOID}"))
    for r in d["quarter_capex"]:
        t, n = r["ticker"], NAME[r["ticker"]]
        thr = THRESHOLD_ROW.get((t, "quarter_capex"))
        legs = f"momentum leg {money(r['momentum_leg'])}" + (f", guide-implied leg {money(r['guide_implied_leg'])}" if r["guide_implied_leg"] else "")
        out.append(dict(
            t=t, target="quarter_capex", horizon=r["ledger_horizon"],
            event=f"{n} {r['period']} report, {r['report_date']} ({r['date_status']}): quarterly capex ({r['basis']}). Last quarter "
                  f"{money(r['last_quarter'])}; model point = average of {legs} = {money(r['point'])}.",
            pred=f"{n} reports {r['period']} capital expenditures, measured as {r['basis']}, between {money(r['low'])} and {money(r['high'])} "
                 f"inclusive (model point {money(r['point'])}, 80% range) {TAG}.",
            fals=f"{n}'s reported {r['period']} capital expenditures, measured as {r['basis']}, are below {money(r['low'])} or above {money(r['high'])}.",
            sens=f"LEAN: neutral. LAYER L2. {METHOD}Range at the pre-registered width, not re-fitted (10 backtest rows; 9 of 10 fell "
                 f"inside). Backtest: median miss 9.5% vs 9.7% consensus; fails the +/-8% tightness line. Definitions differ by company "
                 f"(see data/ai_prints_backtest/buyers_notes.md)." +
                 (" Amazon's annual guide is on a net cash basis while this row resolves on gross purchases." if t == "AMZN" else "") +
                 f" {INDEP}" + (f" Threshold row on the same figure: #{thr}." if thr else "") +
                 f" RESOLUTION: {r['resolution_source']}. {VOID}"))
    return out


def main():
    dry = "--dry-run" in sys.argv
    c = sqlite3.connect(DB)
    if c.execute("SELECT COUNT(*) FROM predictions WHERE prediction LIKE ?", (f"%{TAG}%",)).fetchone()[0]:
        sys.exit("already logged: refusing to log the same calls twice")
    new = []
    for r in rows():
        cmd = [sys.executable, str(ROOT / "pipeline" / "ledger.py"), "add", "--event", r["event"], "--prediction", r["pred"],
               "--prob", "0.80", "--horizon", r["horizon"], "--falsifier", r["fals"], "--sensitivity", r["sens"],
               "--conviction", "0.62", "--sectors", SECTOR[r["t"]], "--tickers", r["t"], "--direction", "neutral",
               "--source", "mechanical", "--cluster", "ai-prints-range", "--kind", "markets"]
        if dry:
            print(r["t"], r["target"], r["horizon"], "|", r["pred"]); continue
        p = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
        print(p.stdout.strip(), p.stderr.strip())
        m = re.search(r"logged #(\d+)", p.stdout)
        if not m:
            sys.exit(f"not logged: {r['t']} {r['target']}")
        new.append((int(m.group(1)), r["t"]))
    if dry:
        return
    tl = json.loads(TL.read_text(encoding="utf-8"))
    nodes = {n["id"]: n for n in tl["nodes"]}
    if "orcl-fq2" not in nodes:
        node = {"id": "orcl-fq2", "parent": "now", "kind": "event", "checkpoint": True, "date": "2026-12-10", "horizon": "scheduled",
                "p": 1.0, "ledger": [], "lane": "markets-ai",
                "label": "Oracle fiscal Q2 2027 report (9-14 Dec, unconfirmed): revenue, capex, RPO",
                "rationale": "Added 11/18 for the mechanical range calls on Oracle's revenue, next guide and quarterly capex. Oracle "
                             "is the most debt-funded of the five buyers (S&P BBB-, ~$638B backlog about half OpenAI), so its "
                             "capex and its financing are read together.",
                "shifts": [{"target": "ai-financing-chain", "p_to": 0.72, "date_delta": 0,
                            "note": "a capex step-up with no new funding, or a cut to the FY27 capex range, raises the rating risk on #134"},
                           {"target": "capex-digestion", "p_to": 0.46, "date_delta": 0,
                            "note": "an Oracle capex cut would be the first buyer to trim on financing rather than supply timing"}],
                "evidence": [], "confluence": [], "market": "no price call (prints and plans only)"}
        tl["nodes"].append(node)
        nodes["orcl-fq2"] = node
    for pid, t in new:
        nodes[NODE[t]].setdefault("ledger", []).append(pid)
    tl["updated"] = "2026-11-18"
    TL.write_text(json.dumps(tl, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n")
    print("wired:", new)


if __name__ == "__main__":
    main()
