#!/usr/bin/env python3
"""python -m unittest tests.test_mystery_events -v

The adapter reads ANOTHER project's files, so the things worth guarding are: it never writes into their tree, it
drops what is not an event (market wraps, routine prints, off-topic stories), it never turns an unreviewed guess
into node evidence, and its topic router uses real word boundaries (a 'fed' inside 'federal' is not the Fed)."""
import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import mystery_events as me  # noqa: E402

FILLER = ["Housing starts", "Cocoa prices", "Lithium supply", "Carbon market", "Airline slots", "Water rights", "Steel tariffs",
          "Copper deficit", "Reinsurance renewals", "Crop insurance", "Stablecoin supply", "Launch cadence", "Nickel smelters",
          "Fiscal deficit", "Payroll growth", "Mortgage rates", "Gold reserves", "Rare earth magnets", "Grain storage", "Power demand"]
# 'rare' is measured against the node corpus (idf), so the synthetic tree needs a realistic number of unrelated nodes
TREE = {"lanes": ["russia-ukraine", "fed-macro", "misc"], "nodes": [
    {"id": "ru-anchor", "label": "Russia Ukraine war anchor", "lane": "russia-ukraine", "p": 1.0, "date": "2026-10-02"},
    {"id": "ev-trump-putin-meeting", "label": "Trump and Putin hold an in-person meeting", "lane": "russia-ukraine", "p": 0.15, "date": "2026-12-01"},
] + [{"id": f"filler-{i}", "label": f"{t} {i}", "lane": "misc", "p": 0.5, "date": "2026-12-01"} for i, t in enumerate(FILLER)]}


def head(t, imp, text):
    return {"id": "h" + str(t), "t": float(t), "et": "2026-10-10 12:00", "headline": text, "imp": imp, "mkt": 0, "reason": "model says so"}


def story(sid, title, family, imp, heads, n=None):
    return {"id": sid, "title": title, "family": family, "imp": imp, "mkt": 0, "n": n or len(heads), "heads": heads,
            "first_t": 1.0, "last_t": 2.0, "symbols": [], "prim": "", "top": heads[0]["headline"]}


class Adapter(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        r = pathlib.Path(self.tmp.name)
        (r / "data").mkdir(); (r / "promo").mkdir(); (r / "news").mkdir()
        (r / "data" / "timelines.json").write_text(json.dumps(TREE), encoding="utf-8")
        me.ROOT, me.NEWS = r, r / "news"
        self.r = r

    def tearDown(self):
        self.tmp.cleanup()

    def put_stories(self, stories):
        (self.r / "news" / "stories_month.json").write_text(json.dumps({"stories": {s["id"]: s for s in stories}}), encoding="utf-8")

    def run_with(self, stories, fixture=True):
        if fixture:
            self.put_stories(stories)
        sys.argv = ["x", "--since", "2026-10-01", "--write"]
        me.main()
        return json.loads((self.r / "promo" / "events_mystery.json").read_text(encoding="utf-8"))["events"]

    def test_a_real_macro_story_becomes_an_event_with_candidates_but_no_evidence(self):
        ev = self.run_with([story("s1", "Russia-Ukraine war", "macro_other", 0.7,
                                  [head(1, 0.8, "Trump says he will meet Putin in person next month to discuss ending the war in Ukraine")])])
        self.assertEqual(len(ev), 1)
        self.assertEqual(ev[0]["confidence"], "mystery-ai")
        self.assertEqual(ev[0]["bears_on"], [], "an unreviewed guess must never become node evidence")
        self.assertTrue(ev[0]["candidate_nodes"], "the guess is kept for a reviewer")

    def test_market_wraps_routine_prints_and_off_topic_stories_are_not_events(self):
        ev = self.run_with([
            story("w", "Russia-Ukraine war", "macro_other", 0.7, [head(1, 0.9, "Stock Market Today: S&P 500 falls as Russia Ukraine tensions grow")]),
            story("p", "US manufacturing data", "macro_release", 0.6, [head(2, 0.7, "USA S&P Global Manufacturing PMI For September 57.0 Vs 53.6 Est")]),
            story("e", "Boston Beer Q3 results", "results", 0.7, [head(3, 0.9, "Boston Beer Q3 earnings beat estimates and raise full year guidance")]),
        ])
        self.assertEqual(ev, [])

    def test_the_router_uses_word_boundaries(self):
        self.assertIn("fed-macro", me.lanes_of("The Fed raises rates again"))
        self.assertNotIn("fed-macro", me.lanes_of("The federal government released a new report"))

    def test_it_never_writes_into_the_other_projects_tree(self):
        stories = [story("s1", "Russia-Ukraine war", "macro_other", 0.7,
                         [head(1, 0.8, "Zelenskiy asks Trump for a winter package of Patriot missiles for Ukraine")])]
        self.put_stories(stories)                       # the fixture is written FIRST, then the directory is snapshotted
        before = {p: p.read_bytes() for p in (self.r / "news").rglob("*") if p.is_file()}
        self.run_with(stories, fixture=False)
        after = {p: p.read_bytes() for p in (self.r / "news").rglob("*") if p.is_file()}
        self.assertEqual(after, before, "the adapter must not create, change or delete anything in the source directory")

    def test_an_event_already_in_the_log_is_not_logged_twice(self):
        (self.r / "data" / "events.json").write_text(json.dumps({"events": [
            {"date": "2026-10-10", "fact": "Trump says he will meet Putin in person next month to discuss ending the war in Ukraine"}]}), encoding="utf-8")
        ev = self.run_with([story("s1", "Russia-Ukraine war", "macro_other", 0.7,
                                  [head(1, 0.8, "Trump says he will meet Putin in person next month to discuss ending the war in Ukraine - Reuters")])])
        self.assertEqual(ev, [])


if __name__ == "__main__":
    unittest.main()
