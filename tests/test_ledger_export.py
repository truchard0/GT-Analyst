#!/usr/bin/env python3
"""python -m unittest tests.test_ledger_export -v

The export's whole value is that a git merge of it is trustworthy, so what is tested is exactly the
things that would make it untrustworthy: a round trip that loses or reorders data, a non-deterministic
dump (every export would diff), and a merge that leaves two versions of one row behind."""
import json
import pathlib
import sqlite3
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
sys.path.insert(0, str(ROOT / "tools"))
import ledger          # noqa: E402
import ledger_export as lx   # noqa: E402


class Export(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        d = pathlib.Path(self.tmp.name)
        ledger.DB = d / "ledger.db"
        lx.DB, lx.OUT, lx.REBUILT = d / "ledger.db", d / "ledger.jsonl", d / "rebuilt.db"
        c = ledger.db()
        for i, (pr, cl) in enumerate([(0.7, "a"), (0.4, ""), (0.9, "b")], 1):
            c.execute("INSERT INTO predictions(id,ts,event,prediction,prob,horizon,falsifier,cluster,source,prob0,status)"
                      " VALUES(?,?,?,?,?,?,?,?,?,?, 'open')",
                      (i, "2026-10-01T00:00Z", "e", f"p{i} with a quote ' and unicode \u2192 ok", pr, "2027-01-01", "f", cl, "manual", pr))
            c.execute("INSERT INTO revisions(pred_id,ts,prob,reason,kind) VALUES(?,?,?,?, 'initial')", (i, "2026-10-01T00:00Z", pr, "r"))
        c.commit(); c.close()

    def tearDown(self):
        self.tmp.cleanup()

    def _export(self):
        rows = lx.rows_of(sqlite3.connect(lx.DB))
        lx.OUT.write_text(lx.dump(rows), encoding="utf-8", newline="")
        return rows

    def test_export_is_deterministic(self):
        self._export(); a = lx.OUT.read_bytes()
        self._export(); self.assertEqual(a, lx.OUT.read_bytes())

    def test_round_trip_loses_nothing_compared_by_column_NAME(self):
        self._export()
        sys.argv = ["x", "rebuild"]
        self.assertEqual(lx.main(), 0)
        a, b = sqlite3.connect(lx.DB), sqlite3.connect(lx.REBUILT)
        a.row_factory = b.row_factory = sqlite3.Row
        for t, k in (("predictions", "id"), ("revisions", "id")):
            ra = [dict(r) for r in a.execute(f"SELECT * FROM {t} ORDER BY {k}")]
            rb = [dict(r) for r in b.execute(f"SELECT * FROM {t} ORDER BY {k}")]
            self.assertEqual(ra, rb, t)
        b.close()

    def test_duplicate_row_after_a_merge_is_refused(self):
        rows = self._export()
        twin = dict(rows[0]); twin["prob"] = 0.01          # the same id with a different value
        text = lx.dump(rows + [twin])
        with self.assertRaises(SystemExit) as cm:
            lx.load(text)
        self.assertIn("duplicate", str(cm.exception))

    def test_unresolved_conflict_markers_are_refused(self):
        rows = self._export()
        text = "<<<<<<< HEAD" + chr(10) + lx.dump(rows)
        with self.assertRaises(SystemExit) as cm:
            lx.load(text)
        self.assertIn("conflict", str(cm.exception))

    def test_check_detects_a_silent_divergence_and_tolerates_crlf(self):
        self._export()
        sys.argv = ["x", "check"]
        self.assertEqual(lx.main(), 0)
        lx.OUT.write_bytes(lx.OUT.read_bytes().replace(b"\n", b"\r\n"))     # a Windows checkout
        self.assertEqual(lx.main(), 0, "CRLF must not read as divergence")
        c = sqlite3.connect(lx.DB); c.execute("UPDATE predictions SET prob=0.123 WHERE id=1"); c.commit(); c.close()
        self.assertEqual(lx.main(), 1, "a real edit to the db must be flagged")


if __name__ == "__main__":
    unittest.main()
