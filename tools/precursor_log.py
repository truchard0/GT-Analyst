#!/usr/bin/env python3
"""Prospective log of non-fatality ceasefire precursors, built from the ingest tape. Stdlib only.

The ceasefire engine can only learn from precursors that have a dated historical record (PA-X
mediation activity). Deadlines, flight bans and force posture have none in the public data, so
this log starts recording them now, point-in-time, to become training data:

  flight_ban     NOTAMs, airspace closures, airline suspensions
  force_posture  carriers, bombers, deployments, embassy drawdowns, evacuations
  mediator       mediators, envoys, drafts, proposals, talks
  deadline       deadlines, ultimatums, expiring windows

Only items in the conflict's context (Iran, Hormuz, Houthis, IRGC, Gulf, Red Sea) are kept. Each
row keeps the item's REPORTED time, so the log never back-dates a precursor.

    python tools/precursor_log.py update          # scan inbox/latest.md + inbox/processed/*.md
    python tools/precursor_log.py summary [--days 14]
"""
import csv
import datetime as dt
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOG = ROOT / "data" / "ceasefire" / "precursor_log.csv"
ITEM = re.compile(r"^- \*\*(.*)\*\* \((.*?) \| reported (\S+)")
CONTEXT = re.compile(r"\b(iran|iranian|tehran|hormuz|houthi|irgc|persian gulf|red sea|bab el-mandeb|centcom)", re.I)
KINDS = [
    ("flight_ban", re.compile(r"\b(notam|airspace|no-fly|flights? (ban|suspend|cancel|divert)|"
                              r"airlines? (suspend|cancel|halt|reroute))", re.I)),
    ("force_posture", re.compile(r"\b(carrier|strike group|bomber|b-2|b-52|f-35|deploy|troops|warship|"
                                 r"destroyer|submarine|evacuat|embass|drawdown|reinforce|blockade|"
                                 r"minesweep|mine-clear|escort|patrol|inspection flight|build-?up|"
                                 r"prepare for (possible )?strikes)", re.I)),
    ("mediator", re.compile(r"\b(mediat|qatar(?!energy)|qatari|(?<!gulf of )oman|omani|pakistan|envoy|draft|proposal|"
                            r"negotiat|talks|deal)", re.I)),
    ("deadline", re.compile(r"\b(deadline|ultimatum|expire|expiry|window|countdown|"
                            r"within \d+ (days|hours)|after (the )?midterms|end of the week)", re.I)),
]


def scan():
    files = [ROOT / "inbox" / "latest.md"] + sorted((ROOT / "inbox" / "processed").glob("*.md"))
    for p in files:
        if not p.exists():
            continue
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            m = ITEM.match(line)
            if not m or not CONTEXT.search(m.group(1)):
                continue
            title, src, rep = m.group(1), m.group(2), m.group(3).rstrip(",")
            if not re.match(r"\d{4}-\d{2}-\d{2}T", rep):
                continue                      # 'unknown' report times are never logged
            for kind, rx in KINDS:
                if rx.search(title):
                    yield rep, kind, src, title


def update():
    have = []
    if LOG.exists():
        have = [(r["reported_utc"], r["kind"], r["source"], r["title"]) for r in csv.DictReader(open(LOG, encoding="utf-8"))]
    seen = {(k, t.lower()) for _, k, _, t in have}
    new = [r for r in scan() if (r[1], r[3].lower()) not in seen and not seen.add((r[1], r[3].lower()))]
    rows = sorted(have + new)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["reported_utc", "kind", "source", "title"])
        w.writerows(rows)
    print(f"precursor log: {len(rows)} rows (+{len(new)})")


def summary(days):
    if not LOG.exists():
        sys.exit("no log yet - run update")
    rows = list(csv.DictReader(open(LOG, encoding="utf-8")))
    since = (dt.datetime.now(dt.UTC) - dt.timedelta(days=days)).strftime("%Y-%m-%d")
    by = {}
    for r in rows:
        if r["reported_utc"][:10] >= since:
            by.setdefault(r["reported_utc"][:10], {}).setdefault(r["kind"], 0)
            by[r["reported_utc"][:10]][r["kind"]] += 1
    kinds = [k for k, _ in KINDS]
    print("date        " + "  ".join(f"{k:>13}" for k in kinds))
    for d in sorted(by):
        print(f"{d}  " + "  ".join(f"{by[d].get(k, 0):>13}" for k in kinds))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "update":
        update()
    elif cmd == "summary":
        summary(int(sys.argv[sys.argv.index("--days") + 1]) if "--days" in sys.argv else 14)
    else:
        print(__doc__)
