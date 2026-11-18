#!/usr/bin/env python3
"""ledger_export.py - a text twin of ledger.db that git CAN merge.

THE PROBLEM (STATE.md section 9): ledger.db is SQLite, so git treats it as an opaque binary. If the
laptop and the desktop both commit a ledger change, one side's predictions are LOST - silently,
because there is no merge, only 'pick one file'. The only defence was a rule ("never run a cycle
on both machines at once").

THE FIX: ledger/ledger.jsonl - one JSON object per row, sorted by (table, id), keys sorted, floats
printed identically every time. Properties that matter:
  * two machines editing DIFFERENT rows merge cleanly (different lines),
  * two machines editing the SAME row produce a visible conflict you must resolve - which is the
    correct failure mode, versus the old one where it vanished,
  * it is deterministic, so an unchanged ledger produces a zero-line diff.
It deliberately does NOT use git's `merge=union`: union would keep both versions of a row that both
sides edited, producing a duplicate id and a ledger that looks fine and is wrong.

    python tools/ledger_export.py export            # ledger.db -> ledger/ledger.jsonl
    python tools/ledger_export.py check             # exit 1 if the two have diverged (db vs text)
    python tools/ledger_export.py rebuild           # ledger.jsonl -> ledger/ledger.rebuilt.db (never overwrites ledger.db)
After a git merge of ledger.jsonl:  rebuild, run `check`-style comparison by eye, then replace ledger.db.
"""
import argparse
import json
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
DB = ROOT / "ledger" / "ledger.db"
OUT = ROOT / "ledger" / "ledger.jsonl"
REBUILT = ROOT / "ledger" / "ledger.rebuilt.db"
TABLES = ("predictions", "revisions", "lessons", "trades")       # order = load order
KEY = {"predictions": "id", "revisions": "id", "lessons": "pred_id", "trades": "id"}


def rows_of(con):
    con.row_factory = sqlite3.Row
    out = []
    for t in TABLES:
        cols = [r[1] for r in con.execute(f"PRAGMA table_info({t})")]
        if not cols:
            continue
        for r in con.execute(f"SELECT * FROM {t} ORDER BY {KEY[t]}"):
            d = {c: r[c] for c in cols}
            out.append({"t": t, **d})
    return out


def dump(rows):
    # sort_keys + ensure_ascii=False + one object per line: stable, diffable, mergeable
    return "".join(json.dumps(r, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + chr(10) for r in rows)


def load(text):
    seen, rows = set(), []
    for n, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        if line.startswith(("<<<<<<<", "=======", ">>>>>>>")):
            raise SystemExit(f"line {n}: unresolved git merge conflict marker - resolve ledger.jsonl first")
        r = json.loads(line)
        k = (r["t"], r[KEY[r["t"]]])
        if k in seen:
            raise SystemExit(f"line {n}: duplicate {k[0]} key {k[1]} - two versions of one row survived a merge")
        seen.add(k)
        rows.append(r)
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["export", "check", "rebuild"])
    a = ap.parse_args()
    if a.cmd == "export":
        con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
        rows = rows_of(con)
        OUT.write_text(dump(rows), encoding="utf-8", newline="")
        by = {}
        for r in rows:
            by[r["t"]] = by.get(r["t"], 0) + 1
        print(f"wrote {OUT.name}: {len(rows)} rows  " + "  ".join(f"{k}={v}" for k, v in by.items()))
        return 0
    if a.cmd == "check":
        con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
        want = dump(rows_of(con))
        have = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if want == have:
            print("ledger.db and ledger.jsonl agree")
            return 0
        a_ = {(r["t"], r[KEY[r["t"]]]): r for r in load(have)} if have else {}
        b_ = {(r["t"], r[KEY[r["t"]]]): r for r in rows_of(con)}
        only_db = sorted(set(b_) - set(a_)); only_txt = sorted(set(a_) - set(b_))
        diff = sorted(k for k in set(a_) & set(b_) if a_[k] != b_[k])
        print(f"DIVERGED: {len(only_db)} row(s) only in ledger.db, {len(only_txt)} only in ledger.jsonl, "
              f"{len(diff)} differ.  Re-run `export` if ledger.db is the truth.")
        for k in (only_db + only_txt + diff)[:10]:
            print("   ", k)
        return 1
    # rebuild
    import ledger as L
    if REBUILT.exists():
        REBUILT.unlink()
    L.DB = REBUILT
    L.db().close()                                   # creates the exact current schema
    con = sqlite3.connect(REBUILT)
    for r in load(OUT.read_text(encoding="utf-8")):
        t = r.pop("t")
        cols = list(r)
        con.execute(f"INSERT INTO {t}({','.join(cols)}) VALUES({','.join('?' * len(cols))})", [r[c] for c in cols])
    con.commit(); con.close()
    print(f"rebuilt {REBUILT.name} from {OUT.name}. Compare it, then replace ledger.db yourself - this tool never does.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
