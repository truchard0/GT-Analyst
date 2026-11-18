#!/usr/bin/env python3
"""python -m unittest tests.test_window_plan -v

The tool exists because a plan was written without reading the book's own nodes. What is worth guarding: it finds a
focal date with no coupled conflict node, stops flagging it once one exists, flags a forward-dated statement that no
node covers, and never writes anything."""
import contextlib
import io
import json
import pathlib
import sqlite3
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import window_plan as wp  # noqa: E402


def node(i, lane, date, label, p=0.5):
    return {"id": i, "lane": lane, "date": date, "label": label, "p": p, "kind": "event", "row_class": "marker",
            "ledger": [], "parent": "now"}


class Plan(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        r = pathlib.Path(self.tmp.name)
        (r / "data").mkdir(); (r / "ledger").mkdir()
        con = sqlite3.connect(r / "ledger" / "ledger.db")
        con.execute("CREATE TABLE predictions(id INTEGER PRIMARY KEY, prob REAL, horizon TEXT, cluster TEXT, "
                    "prediction TEXT, status TEXT, source TEXT)")
        con.execute("INSERT INTO predictions VALUES (16,0.52,'2027-01-08','iran-war','Israel strikes Iran','open','manual')")
        con.commit(); con.close()
        wp.ROOT = r
        self.r = r

    def tearDown(self):
        self.tmp.cleanup()

    def run_plan(self, nodes, events=()):
        (self.r / "data" / "timelines.json").write_text(json.dumps({"lanes": [], "nodes": nodes}), encoding="utf-8")
        (self.r / "data" / "events.json").write_text(json.dumps({"events": list(events)}), encoding="utf-8")
        before = {p: p.read_bytes() for p in self.r.rglob("*") if p.is_file()}
        sys.argv = ["x", "--from", "2026-10-22", "--to", "2026-12-31"]
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            wp.main()
        after = {p: p.read_bytes() for p in self.r.rglob("*") if p.is_file()}
        self.assertEqual(before, after, "window_plan is read-only")
        return out.getvalue()

    def test_a_focal_date_with_no_conflict_node_is_a_hole(self):
        out = self.run_plan([node("vote", "global-elections", "2026-11-03", "US midterm election held"),
                             node("strike", "iran-energy", "2026-12-20", "US strikes Iran")])
        self.assertIn("HOLE", out)

    def test_a_coupled_node_within_seven_days_clears_the_hole(self):
        out = self.run_plan([node("vote", "global-elections", "2026-11-03", "US midterm election held"),
                             node("pledge", "iran-energy", "2026-11-05", "No-strike pledge ends")])
        self.assertIn("covered", out)
        self.assertNotIn("HOLE", out)

    def test_a_forward_dated_statement_with_no_node_is_uncovered(self):
        ev = [{"date": "2026-10-08", "fact": "Washington will not attack Tehran until after the midterm elections"}]
        out = self.run_plan([node("x", "misc", "2026-11-20", "Unrelated lithium auction")], ev)
        self.assertIn("UNCOVERED", out)

    def test_a_statement_covered_by_a_node_is_not_flagged(self):
        ev = [{"date": "2026-10-08", "fact": "Washington will not attack Tehran until after the midterm elections"}]
        out = self.run_plan([node("n", "iran-energy", "2026-11-04", "Washington attack on Tehran after midterm elections")], ev)
        self.assertNotIn("UNCOVERED", out)


if __name__ == "__main__":
    unittest.main()
