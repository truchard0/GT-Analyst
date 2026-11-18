#!/usr/bin/env python3
"""lens_reread.py - re-read the Iran rows through the deciders' calendar, using only facts PUBLIC on each row's date.

For every resolved Iran row that is about one of the four acts (data/lens_claims.json) it prints what the row said, what the
calendar said that day (a suppress window in force, a permit window, a trigger on file in the last 7 days that no later stand-down
superseded, or nothing), whether R37 would have refused the row as written, and who was right: the row, or the calendar's lean.
The lean is: trigger or permit window -> the act is live; suppress window -> held off; nothing -> no view. Rows whose horizon is
more than 60 days out are given no lean (a window cannot speak to a year).

This is a retrospective on facts I coded AFTER the outcomes were known, so it shows what the lens would have asked, not what a
clean out-of-sample forecast would have scored.

    python tools/lens_reread.py
Read-only.
"""
import datetime as dt
import json
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
import constraints as ct  # noqa: E402


def main():
    cal = ct.load()
    spec = json.loads((ROOT / "data" / "lens_claims.json").read_text(encoding="utf-8"))
    con = sqlite3.connect(f"file:{ROOT / 'ledger' / 'ledger.db'}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    rows = {str(r["id"]): dict(r) for r in con.execute("SELECT id,ts,prob0,prob,outcome,status,horizon FROM predictions")}
    print(f"{'#':<4}{'date':<11}{'row says':<46}{'P':>5}  {'true?':<6}{'calendar that day':<34}{'R37':<9}{'lean':<8}{'who was right'}")
    stats = {"lens_right": 0, "lens_wrong": 0, "row_right_where_lens_spoke": 0, "spoke": 0, "flagged": 0, "flagged_misses": 0, "flagged_hits": 0}
    for rid, c in sorted(spec["rows"].items(), key=lambda kv: int(kv[0])):
        r = rows[rid]
        if r["status"] != "resolved":
            continue
        p = r["prob0"] if r["prob0"] is not None else r["prob"]
        on = ct.d(r["ts"])
        lz = ct.lens(cal, c["act"], on)
        window = (lz["suppress"] or lz["permit"] or [None])[0]
        fs = ct.check_incentive(cal, act=c["act"], claims=c["claims"], prob=p, horizon=r["horizon"], as_of=on, trigger="",
                                window=window or "none: the calendar has no window for this act on this date")
        err = [f for f in fs if f.severity == "error"]
        far = (ct.d(r["horizon"]) - on).days > 60
        lean = None
        if not far and lz["net"] in ("trigger", "permit"):
            lean = "occurs"
        elif not far and lz["net"] == "suppress":
            lean = "does_not_occur"
        # did the ACT occur? the row's claim came true iff outcome == 1
        occurred = (r["outcome"] == 1) if c["claims"] == "occurs" else (r["outcome"] == 0)
        row_right = (abs(p - r["outcome"]) < 0.5)
        lens_right = None if lean is None else ((lean == "occurs") == occurred)
        cal_txt = lz["net"] + (f" {','.join(lz['suppress'] or lz['permit'])}" if lz["suppress"] or lz["permit"] else "") + \
            (f" trg {lz['triggers'][-1][0][5:]}" if lz["triggers"] else "")
        who = "n/a (no view)" if lens_right is None else ("both" if row_right and lens_right else "lens only" if lens_right else "row only" if row_right else "neither")
        if err:
            stats["flagged"] += 1
            stats["flagged_misses" if not row_right else "flagged_hits"] += 1
        if lens_right is not None:
            stats["spoke"] += 1
            stats["lens_right" if lens_right else "lens_wrong"] += 1
            stats["row_right_where_lens_spoke"] += int(row_right)
        print(f"#{rid:<3}{str(on)[5:]:<11}{c['short'][:44]:<46}{p:>5.2f}  {'yes' if r['outcome'] == 1 else 'no':<6}{cal_txt[:32]:<34}{'REFUSE' if err else 'ok':<9}{(lean or '-'):<8}{who}")
    s = stats
    print(f"\nthe calendar had a lean on {s['spoke']} rows: right {s['lens_right']}, wrong {s['lens_wrong']}; the rows themselves were right on "
          f"{s['row_right_where_lens_spoke']} of those {s['spoke']}")
    print(f"R37 would have refused {s['flagged']} rows as written: {s['flagged_misses']} that were misses, {s['flagged_hits']} that were hits (each could be re-logged with its reason)")
    print("\noutside the lens (no claim about the four acts):")
    for k, v in spec["outside_the_lens"].items():
        print(f"   #{k:<3} {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
