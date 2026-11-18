#!/usr/bin/env python3
"""python -m unittest tests.test_events_merge -v

events_merge writes into data/timelines.json, so what is tested is what would make that unsafe:
it must refuse events that point at nodes/rows that do not exist, never move an existing probability,
label a plan as a plan, refuse proposed nodes that break the tree's own rules, and be idempotent."""
import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
sys.path.insert(0, str(ROOT / "tools"))
import ledger          # noqa: E402
import events_merge as em   # noqa: E402

NODE = {"id": "n1", "parent": "now", "label": "Rates anchor", "p": 0.6, "horizon": "1y", "rationale": "x" * 130,
        "confluence": [], "ledger": [], "evidence": [], "market": "m", "kind": "event", "lane": "rates-credit",
        "date": "2027-01-01", "row_class": "invariant", "basis": "statute", "source": "t"}
GOOD_EVENT = {"date": "2026-10-20", "fact": "The Treasury announced a refunding calendar change affecting coupon sizes.",
              "source": "Reuters", "confidence": "multi-outlet", "significance": 4,
              "bears_on": [{"node": "n1", "ledger": None, "relation": "supports", "note": "x"}]}
GOOD_NODE = {"id": "ev-test-1", "parent": "n1", "label": "A scheduled filing is made by its statutory deadline", "p": 0.9,
             "date": "2026-12-01", "lane": "rates-credit", "row_class": "scheduled", "horizon": "6 weeks",
             "basis": "Statutory deadline: the filing is required by law on a published calendar, with a long record of compliance.",
             "rationale": "Scheduled event on a statutory calendar; the date is certain and the soft part is only an extension, "
                          "which is itself a published, observable step. Priced on the calendar, not on anyone's intent.",
             "market": "m", "evidence": []}


class Merge(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        r = pathlib.Path(self.tmp.name)
        for d in ("data", "promo", "ledger"):
            (r / d).mkdir()
        (r / "data" / "timelines.json").write_text(json.dumps({"lanes": ["rates-credit"], "nodes": [dict(NODE)]}), encoding="utf-8")
        ledger.DB = r / "ledger" / "ledger.db"
        c = ledger.db()
        c.execute("INSERT INTO predictions(id,ts,event,prediction,prob,horizon,falsifier,status) VALUES(5,'2026-10-01','e','p',0.5,'2027-01-01','f','open')")
        c.commit(); c.close()
        em.ROOT, em.TREE = r, r / "data" / "timelines.json"
        em.LOG, em.SUGG = r / "data" / "events.json", r / "data" / "sugg.json"
        self.r = r

    def tearDown(self):
        self.tmp.cleanup()

    def run_merge(self, doc, write=True):
        (self.r / "promo" / "events_t.json").write_text(json.dumps(doc), encoding="utf-8")
        sys.argv = ["x"] + (["--write"] if write else ["--dry-run"])
        return em.main()

    def tree(self):
        return json.loads((self.r / "data" / "timelines.json").read_text(encoding="utf-8"))

    def test_a_good_event_attaches_as_evidence_and_never_moves_a_probability(self):
        self.run_merge({"theme": "t", "events": [GOOD_EVENT]})
        n = self.tree()["nodes"][0]
        self.assertEqual(n["p"], 0.6, "an existing probability must never be changed by a merge")
        self.assertEqual(len(n["evidence"]), 1)
        self.assertIn("[supports; Reuters; multi-outlet]", n["evidence"][0]["fact"])

    def test_events_pointing_at_missing_nodes_or_rows_are_refused(self):
        bad1 = dict(GOOD_EVENT, bears_on=[{"node": "nope", "ledger": None, "relation": "supports", "note": ""}])
        bad2 = dict(GOOD_EVENT, fact="A different fact that bears on a ledger row that does not exist in the book.",
                    bears_on=[{"node": None, "ledger": 999, "relation": "supports", "note": ""}])
        self.run_merge({"theme": "t", "events": [bad1, bad2]})
        self.assertEqual(self.tree()["nodes"][0]["evidence"], [])
        self.assertFalse((self.r / "data" / "events.json").exists() and json.loads(
            (self.r / "data" / "events.json").read_text(encoding="utf-8"))["n"] > 0)

    def test_a_plan_is_labelled_a_plan(self):
        e = dict(GOOD_EVENT, confidence="plan-only", fact="Officials are reportedly weighing a new round of strikes after the vote.")
        self.run_merge({"theme": "t", "events": [e]})
        self.assertTrue(self.tree()["nodes"][0]["evidence"][0]["fact"].startswith("PLAN, NOT EXECUTED:"))

    def test_the_merge_is_idempotent(self):
        self.run_merge({"theme": "t", "events": [GOOD_EVENT]})
        self.run_merge({"theme": "t", "events": [GOOD_EVENT]})
        self.assertEqual(len(self.tree()["nodes"][0]["evidence"]), 1)
        self.assertEqual(json.loads((self.r / "data" / "events.json").read_text(encoding="utf-8"))["n"], 1)

    def test_proposed_nodes_must_pass_the_trees_own_rules(self):
        level = dict(GOOD_NODE, id="ev-bad-level", row_class="level")                     # needs a tool-run no_view block
        lane = dict(GOOD_NODE, id="ev-bad-lane", lane="invented-lane")
        loud = dict(GOOD_NODE, id="ev-bad-p", row_class="marker", p=0.92)                 # >=0.85 only for invariant/scheduled
        past = dict(GOOD_NODE, id="ev-bad-date", date="2026-01-01")
        self.run_merge({"theme": "t", "events": [], "new_nodes": [level, lane, loud, past, GOOD_NODE]})
        ids = [n["id"] for n in self.tree()["nodes"]]
        self.assertIn("ev-test-1", ids)
        for bad in ("ev-bad-level", "ev-bad-lane", "ev-bad-p", "ev-bad-date"):
            self.assertNotIn(bad, ids, bad)

    def test_suggestions_are_recorded_but_never_applied(self):
        sg = {"node": "n1", "ledger": None, "from": 0.6, "to": 0.2, "reason": "dated and specific"}
        self.run_merge({"theme": "t", "events": [], "suggest_reprice": [sg]})
        self.assertEqual(self.tree()["nodes"][0]["p"], 0.6)
        self.assertEqual(len(json.loads((self.r / "data" / "sugg.json").read_text(encoding="utf-8"))["suggestions"]), 1)

    def test_dry_run_writes_nothing(self):
        self.run_merge({"theme": "t", "events": [GOOD_EVENT]}, write=False)
        self.assertEqual(self.tree()["nodes"][0]["evidence"], [])
        self.assertFalse((self.r / "data" / "events.json").exists())


if __name__ == "__main__":
    unittest.main()
