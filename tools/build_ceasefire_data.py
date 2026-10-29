#!/usr/bin/env python3
"""Build the ceasefire-timing case base from public data. Stdlib only.

Sources (downloaded once into data/ceasefire/raw/, gitignored):
  PA-X v10 (Univ. of Edinburgh)  - dated ceasefire agreements (Stage == 'Cea'), 1990-2025,
                                   linked to UCDP conflict ids
  UCDP GED 26.1 (1989-2025) + candidate GED 26.0.1-9 (Jan-Sep 2026) - daily deaths per conflict
Plus the 2026 Iran-war ceasefires (manual, sourced in reports/) as a live holdout.

Outputs (committed; small):
  data/ceasefire/breakdown_cases.csv   one row per ceasefire: pre-ceasefire features + the DAY
                                       fighting resumed (V1 = first fatal day, R25 = first day the
                                       trailing-7-day toll reaches 25) or censoring
  data/ceasefire/breakdown_daily.csv   deaths on each fatal day 1..DAILY_MAX after every ceasefire
  data/ceasefire/mediation_daily.csv   PA-X agreements (any stage) signed on the same conflict on
                                       day 1..DAILY_MAX after every ceasefire: the dated trace of
                                       active mediation (non-fatality precursor, point-in-time)
                                       (feeds the day-by-day updating model)
  data/ceasefire/ceasefire_cases.csv   one row per war spell (onset / resumption): features + the
                                       DAY the next ceasefire was agreed, or censoring

Every feature uses only information dated BEFORE the case's start day - the backtest in
pipeline/ceasefire_engine.py additionally censors training outcomes at each cutoff.

    python tools/build_ceasefire_data.py            # download (if missing) + build
"""
import bisect
import csv
import datetime as dt
import io
import json
import math
import pathlib
import re
import urllib.request
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "ceasefire"
RAW = OUT / "raw"
URLS = {
    "pax_v10.csv": "https://pax.peaceagreements.org/cms/documents/3957/pax_data_2257_agreements_v10.csv",
    "ged261-csv.zip": "https://ucdp.uu.se/downloads/ged/ged261-csv.zip",
    "ged26_cand_01_09.csv": "https://ucdp.uu.se/downloads/candidateged/GEDEvent_v26_01_26_09.csv",
    "term_conf.csv": "https://ucdp.uu.se/downloads/monadterm/UCDPConflictTerminationDataset_v4_2024_Conflict.csv",
}
DATA_END = dt.date(2026, 9, 30)   # last day covered by the candidate GED release
WAR_7D = 25                       # "return to war": trailing-7-day state-based deaths >= 25
DAILY_MAX = 400                   # days of post-ceasefire daily deaths exported per case
QUIET_GAP = 60                    # days without a war-level week that separate two war spells

# 2026 Iran war (UCDP conflict 16905). Not in PA-X (ends 2025). Dates per the 10-25 research
# pass (reports/20261025_relaunch-sweep.md): Apr 8 ceasefire; Jun 17 Islamabad Memorandum;
# Jul 24-25 US strike pause at Iran's request (Oman mediating).
MANUAL = [
    ("iran-2026-04-08", 16905, "2026-04-08", "Inter", "Multiparty signed/agreed", 1, "Ceas"),
    ("iran-2026-06-17", 16905, "2026-06-17", "Inter", "Multiparty signed/agreed", 1, "CeaMix"),
    ("iran-2026-07-25", 16905, "2026-07-25", "Inter", "Unilateral document", 1, "Ceas"),
]


def fetch():
    RAW.mkdir(parents=True, exist_ok=True)
    for name, url in URLS.items():
        p = RAW / name
        if not p.exists():
            print(f"downloading {url}")
            req = urllib.request.Request(url, headers={"User-Agent": "GT-Analyst/1.0"})
            with urllib.request.urlopen(req, timeout=600) as r:
                p.write_bytes(r.read())


def day(s):
    return dt.date.fromisoformat(s[:10])


def ged_rows():
    with zipfile.ZipFile(RAW / "ged261-csv.zip") as z:
        name = next(n for n in z.namelist() if n.lower().endswith(".csv"))
        with z.open(name) as f:
            yield from csv.DictReader(io.TextIOWrapper(f, encoding="utf-8", errors="replace"))
    with open(RAW / "ged26_cand_01_09.csv", encoding="utf-8", errors="replace") as f:
        yield from csv.DictReader(f)


def load_daily():
    """{conflict_id: {date: deaths}} for state-based violence with day/week date precision."""
    daily, names, seen = {}, {}, set()
    for r in ged_rows():
        if r["type_of_violence"] != "1" or not r["conflict_new_id"]:
            continue
        if r["id"] in seen:            # candidate release may repeat final-release events
            continue
        seen.add(r["id"])
        if int(r["date_prec"] or 9) > 3:   # month/year-precision events would fake a daily signal
            continue
        cid = int(r["conflict_new_id"])
        d = day(r["date_start"])
        daily.setdefault(cid, {})
        daily[cid][d] = daily[cid].get(d, 0) + int(float(r["best"] or 0))
        names[cid] = r["conflict_name"]
    return daily, names


class Series:
    """Daily deaths for one conflict with fast window sums."""
    def __init__(self, dd):
        self.days = sorted(dd)
        self.cum = []
        acc = 0
        for d in self.days:
            acc += dd[d]
            self.cum.append(acc)
        self.dd = dd

    def total(self, lo, hi):
        """deaths on days lo..hi inclusive"""
        i = bisect.bisect_left(self.days, lo)
        j = bisect.bisect_right(self.days, hi)
        return (self.cum[j - 1] if j else 0) - (self.cum[i - 1] if i else 0)

    def first_fatal(self, after):
        i = bisect.bisect_right(self.days, after)
        return self.days[i] if i < len(self.days) else None

    def first_war_day(self, after):
        """first day t > after where deaths in [max(after+1, t-6), t] >= WAR_7D"""
        i = bisect.bisect_right(self.days, after)
        for d in self.days[i:]:
            lo = max(after + dt.timedelta(days=1), d - dt.timedelta(days=6))
            if self.total(lo, d) >= WAR_7D:
                return d
        return None

    def war_days(self):
        out = []
        for d in self.days:
            if self.total(d - dt.timedelta(days=6), d) >= WAR_7D:
                out.append(d)
        return out


ETHPRIO_FILE = RAW / "ethprio_cf.csv"           # drop the ETH/PRIO CF data here when it arrives
ETHPRIO_MAP = OUT / "ethprio_columns.json"      # which of its columns hold id, conflict, date, type


def ethprio_rows():
    """ETH/PRIO Civil Conflict Ceasefire cases (Clayton et al. 2023), if the file is present. Adds the
    unilateral and failed ceasefires PA-X omits; same-conflict dates within 3 days merge with PA-X."""
    if not ETHPRIO_FILE.exists():
        return []
    cols = json.loads(ETHPRIO_MAP.read_text(encoding="utf-8"))
    out = []
    with open(ETHPRIO_FILE, encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f):
            try:
                cid = int(float(r[cols["conflict_id"]]))
                if cols.get("date") and r.get(cols["date"]):
                    d = day(r[cols["date"]])
                else:
                    y, m, dd = (int(float(r[c])) for c in cols["date_parts"])
                    d = dt.date(y, m, dd)
            except (KeyError, ValueError):
                continue
            uni = str(r.get(cols.get("unilateral", ""), "")).strip() in ("1", "1.0", "yes", "True")
            out.append({"cf_id": f"ethprio-{r.get(cols['id'], len(out))}-{cid}", "conflict_id": cid,
                        "date": d, "agtp": "Intra",
                        "status": "Unilateral document" if uni else "Multiparty signed/agreed",
                        "third_party": 0, "stagesub": "Ceas", "src": "ethprio"})
    print(f"ETH/PRIO: {len(out)} ceasefires read from {ETHPRIO_FILE.name}")
    return out


def ceasefires():
    rows = ethprio_rows()
    with open(RAW / "pax_v10.csv", encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f):
            if r["Stage"] != "Cea":
                continue
            ids = [int(float(x)) for x in re.findall(r"\d+(?:\.\d+)?", r["UcdpCon"] or "")]
            if not ids:
                continue
            for cid in ids:
                rows.append({"cf_id": f"pax-{r['AgtId']}-{cid}", "conflict_id": cid,
                             "date": day(r["Dat"]), "agtp": r["Agtp"], "status": r["Status"],
                             "third_party": int(bool((r["ThrdPart"] or "").strip())),
                             "stagesub": r["StageSub"], "src": "pax"})
    for cf_id, cid, d, agtp, status, tp, sub in MANUAL:
        rows.append({"cf_id": cf_id, "conflict_id": cid, "date": day(d), "agtp": agtp,
                     "status": status, "third_party": tp, "stagesub": sub, "src": "manual"})
    rows.sort(key=lambda r: (r["conflict_id"], r["date"]))
    # same conflict, agreements within 3 days of each other = one ceasefire event
    merged = []
    for r in rows:
        if merged and merged[-1]["conflict_id"] == r["conflict_id"] and \
                (r["date"] - merged[-1]["date"]).days <= 3:
            continue
        merged.append(r)
    return merged


def pax_agreements():
    """{conflict_id: sorted signing dates} for every PA-X agreement, any stage - talks that produce
    documents are the one mediation signal with a dated historical record"""
    out = {}
    with open(RAW / "pax_v10.csv", encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f):
            for cid in {int(float(x)) for x in re.findall(r"\d+(?:\.\d+)?", r["UcdpCon"] or "")}:
                out.setdefault(cid, []).append(day(r["Dat"]))
    return {k: sorted(v) for k, v in out.items()}


def interstate_ids():
    """UCDP type_of_conflict 2 = interstate. 16905 (the 2026 Iran war) postdates term v4."""
    ids = {16905}
    with open(RAW / "term_conf.csv", encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f):
            if r["type_of_conflict"] == "2":
                ids.add(int(r["conflict_id"]))
    return ids


def lg(x):
    return round(math.log1p(max(x, 0)), 4)


def build():
    fetch()
    interstate = interstate_ids()
    daily, names = load_daily()
    series = {cid: Series(dd) for cid, dd in daily.items()}
    cfs = [c for c in ceasefires() if c["conflict_id"] in series]
    agreements = pax_agreements()

    # outcomes first (needed for the "known by D" track-record features)
    for c in cfs:
        s, d = series[c["conflict_id"]], c["date"]
        v1, r25 = s.first_fatal(d), s.first_war_day(d)
        c["v1"] = (v1 - d).days if v1 else None
        c["r25"] = (r25 - d).days if r25 else None
        c["r25_date"] = r25
        c["censor"] = (DATA_END - d).days

    rows = []
    by_conf = {}
    for c in cfs:
        by_conf.setdefault(c["conflict_id"], []).append(c)
    for c in cfs:
        s, d, D = series[c["conflict_id"]], c["date"], dt.timedelta
        prior = [p for p in by_conf[c["conflict_id"]] if p["date"] < d]
        broke = [p for p in prior if p["r25_date"] and p["r25_date"] < d]
        last_break = max((p["r25_date"] for p in broke), default=None)
        last_dur = None
        if broke:
            lb = max(broke, key=lambda p: p["date"])
            last_dur = lb["r25"]
        d30, d90 = s.total(d - D(days=30), d - D(days=1)), s.total(d - D(days=90), d - D(days=1))
        first = s.days[0]
        rows.append({
            "cf_id": c["cf_id"], "src": c["src"], "conflict_id": c["conflict_id"],
            "conflict_name": names.get(c["conflict_id"], ""), "date": d.isoformat(),
            "interstate": int(c["agtp"] in ("Inter", "InterIntra") or c["conflict_id"] in interstate),
            "local": int(c["agtp"] == "IntraLocal"),
            "unilateral": int(c["status"].startswith("Unilateral")),
            "third_party": c["third_party"], "mixed": int(c["stagesub"] == "CeaMix"),
            "l_d7": lg(s.total(d - D(days=7), d - D(days=1))), "l_d30": lg(d30),
            "l_d90": lg(d90), "l_d365": lg(s.total(d - D(days=365), d - D(days=1))),
            "trend": round(math.log1p(d30) - math.log1p(d90 / 3), 4),
            "active30": int(d30 > 0),
            "l_age": lg((d - first).days) if first < d else 0.0,
            "prior_cf": len(prior), "prior_breaks": len(broke),
            "has_last": int(last_dur is not None), "l_last_dur": lg(last_dur or 0),
            "l_since_break": lg((d - last_break).days) if last_break else 0.0,
            "l_med90": lg(sum(1 for a in agreements.get(c["conflict_id"], ()) if d - D(days=90) <= a < d)),
            "v1_day": c["v1"] if c["v1"] is not None and c["v1"] <= c["censor"] else "",
            "r25_day": c["r25"] if c["r25"] is not None and c["r25"] <= c["censor"] else "",
            "censor_day": c["censor"],
        })
    write(OUT / "breakdown_cases.csv", rows)
    daily_rows = []
    for c in cfs:
        s, d = series[c["conflict_id"]], c["date"]
        for k in range(1, DAILY_MAX + 1):
            n = s.dd.get(d + dt.timedelta(days=k), 0)
            if n:
                daily_rows.append({"cf_id": c["cf_id"], "day": k, "deaths": n})
    write(OUT / "breakdown_daily.csv", daily_rows)
    med_rows = []
    for c in cfs:
        d = c["date"]
        for a in agreements.get(c["conflict_id"], ()):
            k = (a - d).days
            if 1 <= k <= DAILY_MAX:
                med_rows.append({"cf_id": c["cf_id"], "day": k})
    write(OUT / "mediation_daily.csv", med_rows or [{"cf_id": "", "day": ""}])

    # ---- war spell -> next ceasefire ----
    spells = []
    for cid, s in series.items():
        wd = s.war_days()
        starts = [x for i, x in enumerate(wd) if i == 0 or (x - wd[i - 1]).days > QUIET_GAP]
        # resumption after a ceasefire = that ceasefire's R25 day (if inside an ongoing spell)
        for c in by_conf.get(cid, []):
            if c["r25_date"] and all(abs((c["r25_date"] - x).days) > 14 for x in starts):
                starts.append(c["r25_date"])
        starts.sort()
        conf_cfs = sorted(c["date"] for c in by_conf.get(cid, []))
        for st in starts:
            if st < dt.date(1990, 1, 1):          # PA-X starts in 1990
                continue
            nxt = next((x for x in conf_cfs if x > st), None)
            # war spell ends at the last war-day before a QUIET_GAP lull -> censor 60d later
            later = [x for x in wd if x >= st]
            end = later[0] if later else st
            for x in later[1:]:
                if (x - end).days > QUIET_GAP:
                    break
                end = x
            horizon = min(DATA_END, end + dt.timedelta(days=QUIET_GAP))
            prior_cf = [x for x in conf_cfs if x < st]
            D = dt.timedelta
            spells.append({
                "spell_id": f"{cid}-{st.isoformat()}", "conflict_id": cid,
                "conflict_name": names.get(cid, ""), "date": st.isoformat(),
                "interstate": int(cid in interstate),
                "after_cf": int(bool(prior_cf) and (st - prior_cf[-1]).days <= 365),
                "l_d7": lg(s.total(st - D(days=6), st)), "l_d365": lg(s.total(st - D(days=365), st - D(days=7))),
                "l_age": lg((st - s.days[0]).days), "prior_cf": len(prior_cf),
                "cf_day": (nxt - st).days if nxt and nxt <= horizon else "",
                "censor_day": (horizon - st).days,
            })
    write(OUT / "ceasefire_cases.csv", spells)
    nb = sum(1 for r in rows if r["r25_day"] != "")
    print(f"breakdown cases: {len(rows)} ({nb} returned to war <= {DATA_END}); "
          f"war spells: {len(spells)} ({sum(1 for r in spells if r['cf_day'] != '')} reached a ceasefire)")


def write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    build()
