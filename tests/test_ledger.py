#!/usr/bin/env python3
"""Ledger scoring tests: references, revisions, time-weighted Brier.   python -m unittest tests.test_ledger -v
Runs against a throwaway database - never the real ledger."""
import argparse
import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "pipeline"))
import ledger  # noqa: E402

UTC = timezone.utc


def ns(**kw):
    base = dict(event="e", prediction="Brent closes above 100 on 2026-10-30", prob=0.6, horizon="2026-10-30",
                falsifier="Brent settles at or below 100 on 2026-10-30", sensitivity="s", conviction=0.5,
                sectors="", tickers="", direction="", source="manual", cluster="", lean="neutral", ts=None,
                dry_run=False, base_rate=None, base_class="", market=None, market_src="", diverge="",
                level=None, hedge="", state=None,
                act="", claims="", window="", trigger="")
    base.update(kw)
    return argparse.Namespace(**base)


def quiet(fn, *a, **k):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        fn(*a, **k)
    return buf.getvalue()


class LedgerScoring(unittest.TestCase):
    def setUp(self):
        # ignore_cleanup_errors: ledger.py's 15 db() call sites never close their sqlite
        # connection - harmless for a CLI that exits, but on Windows it keeps a handle on the
        # temp file and the teardown raises PermissionError [WinError 32] AFTER the assertions
        # have already passed. The leak is a CLI-lifecycle non-issue; the red suite it caused
        # was hiding real regressions, which is why this is fixed here and not papered over.
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        ledger.DB = pathlib.Path(self.tmp.name) / "ledger.db"

    def tearDown(self):
        self.tmp.cleanup()

    def test_time_weighting_rewards_the_path_not_the_last_word(self):
        t0 = datetime(2026, 9, 1, tzinfo=UTC)
        end = t0 + timedelta(days=10)
        revs = [(t0.isoformat(), 0.5), ((t0 + timedelta(days=5)).isoformat(), 0.9)]
        got = ledger.time_weighted(revs, t0, end, 1.0)
        self.assertAlmostEqual(got, 0.5 * 0.25 + 0.5 * 0.01)

    def test_a_single_forecast_scores_exactly_as_before(self):
        t0 = datetime(2026, 9, 1, tzinfo=UTC)
        self.assertAlmostEqual(ledger.time_weighted([(t0.isoformat(), 0.7)], t0, t0 + timedelta(days=30), 0.0), 0.49)

    def test_revisions_after_the_outcome_is_known_do_not_count(self):
        t0 = datetime(2026, 9, 1, tzinfo=UTC)
        end = t0 + timedelta(days=4)
        revs = [(t0.isoformat(), 0.4), ((t0 + timedelta(days=9)).isoformat(), 0.99)]
        self.assertAlmostEqual(ledger.time_weighted(revs, t0, end, 1.0), 0.36)

    def test_window_never_runs_past_the_horizon_or_the_asof_date(self):
        now = datetime(2026, 12, 1, tzinfo=UTC)
        s, e = ledger.score_window("2026-09-01T00:00:00Z", "2026-09-30", "", now)
        self.assertEqual(e, datetime(2026, 10, 1, tzinfo=UTC))
        s, e = ledger.score_window("2026-09-01T00:00:00Z", "2026-09-30", "2026-09-10", now)
        self.assertEqual(e, datetime(2026, 9, 11, tzinfo=UTC))

    def test_add_writes_the_initial_revision_and_the_reference(self):
        quiet(ledger.add, ns(base_rate=0.45, base_class="no-view odds from range_odds.py, 30 sessions", prob=0.5))
        c = ledger.db()
        self.assertEqual(c.execute("SELECT kind,prob FROM revisions").fetchall(), [("initial", 0.5)])
        self.assertEqual(c.execute("SELECT base_rate,prob0 FROM predictions").fetchone(), (0.45, 0.5))
        self.assertNotEqual(c.execute("SELECT ref_ts FROM predictions").fetchone()[0], "")

    def test_no_base_rate_is_flagged_and_so_is_unexplained_divergence(self):
        self.assertTrue(any("NO BASE RATE" in m for m in ledger.ref_lint(0.6, None, "", None, "", "")))
        msgs = ledger.ref_lint(0.75, 0.40, "21/48 interstate ceasefires resumed (Fortna 2003)", None, "", "")
        self.assertTrue(any("DIVERGENCE" in m for m in msgs))
        msgs = ledger.ref_lint(0.75, 0.40, "21/48 interstate ceasefires resumed (Fortna 2003)", None, "",
                               "IAEA report dated 9/18 shows monitors readmitted")
        self.assertFalse(any("DIVERGENCE" in m for m in msgs))

    def test_market_price_is_the_reference_when_present_and_needs_a_source(self):
        self.assertEqual(ledger.reference(0.3, 0.62), (0.62, "market"))
        self.assertEqual(ledger.reference(0.3, None), (0.3, "base-rate"))
        self.assertTrue(any("WITHOUT A SOURCE" in m for m in ledger.ref_lint(0.6, 0.5, "x" * 20, 0.62, "", "")))

    def test_revise_keeps_history_moves_prob_and_refuses_closed_rows(self):
        quiet(ledger.add, ns(prob=0.5))
        out = quiet(ledger.revise, 1, 0.55, "EIA weekly 9/23 showed a 4mb draw")
        self.assertIn("0.50 -> 0.55", out)
        out = quiet(ledger.revise, 1, 0.80, "one headline, big jump to test the note")
        self.assertIn("NOTE", out)
        quiet(ledger.revise, 1, None, "checked Brent settle 9/25, nothing new", kind="confirm")
        c = ledger.db()
        self.assertEqual([k for (k,) in c.execute("SELECT kind FROM revisions ORDER BY id")],
                         ["initial", "revise", "revise", "confirm"])
        self.assertEqual(c.execute("SELECT prob,prob0 FROM predictions").fetchone(), (0.8, 0.5))
        c.close()
        quiet(ledger.resolve, 1, "1")
        with self.assertRaises(SystemExit):
            ledger.revise(1, 0.9, "too late, outcome already known")

    def test_a_reason_is_mandatory(self):
        quiet(ledger.add, ns())
        with self.assertRaises(SystemExit):
            ledger.revise(1, 0.7, "vibes")

    def test_the_first_reference_is_never_overwritten(self):
        quiet(ledger.add, ns(market=0.40, market_src="Kalshi KXFED-26OCT, 2c spread, 40k vol"))
        quiet(ledger.set_ref, argparse.Namespace(id=1, base_rate=None, base_class="", market=0.70,
                                                 market_src="Kalshi 9/28", diverge=""))
        c = ledger.db()
        mp, src = c.execute("SELECT market_prob,market_src FROM predictions").fetchone()
        self.assertEqual(mp, 0.40)
        self.assertIn("later: 0.70", src)

    def test_cluster_interval_is_wider_than_pretending_rows_are_independent(self):
        rows = [("a", 0.0)] * 20 + [("b", 0.5)] * 20 + [("c", 0.25), ("d", 0.2), ("e", 0.3)]
        lo, hi, k = ledger.cluster_interval(rows)
        self.assertEqual(k, 5)
        self.assertGreater(hi - lo, 0.15)

    def test_old_databases_are_migrated_with_their_history_intact(self):
        import sqlite3
        c = sqlite3.connect(ledger.DB)
        c.execute("""CREATE TABLE predictions(id INTEGER PRIMARY KEY, ts TEXT, event TEXT, prediction TEXT,
                     prob REAL, horizon TEXT, falsifier TEXT, sensitivity TEXT, conviction REAL, sectors TEXT,
                     tickers TEXT, direction TEXT, source TEXT DEFAULT 'manual', cluster TEXT DEFAULT '',
                     status TEXT DEFAULT 'open', outcome INTEGER, resolved_ts TEXT, brier REAL)""")
        c.execute("INSERT INTO predictions(ts,prediction,prob,horizon,status,outcome,brier) "
                  "VALUES('2026-05-01T00:00:00Z','x',0.7,'2026-06-01','resolved',1,0.09)")
        c.commit()
        c.close()
        c = ledger.db()
        self.assertEqual(c.execute("SELECT prob0,brier FROM predictions").fetchone(), (0.7, 0.09))
        self.assertEqual(c.execute("SELECT COUNT(*) FROM revisions").fetchone()[0], 1)
        ledger.db()                                   # idempotent
        self.assertEqual(c.execute("SELECT COUNT(*) FROM revisions").fetchone()[0], 1)


class ConflictGate(unittest.TestCase):
    """R28's conflict-level half at the door: `ledger.py add --level` is checked against the open rows that declared one."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        ledger.DB = pathlib.Path(self.tmp.name) / "ledger.db"
        quiet(ledger.add, ns(cluster="iran-war", prob=0.95, horizon="2026-12-31", level="3-4",
                             act="il_strike_iran", claims="occurs", window="us-release-postvote",
                             prediction="Israel strikes Iranian territory by 2026-12-31"))

    def tearDown(self):
        self.tmp.cleanup()

    def second(self, **kw):
        return ns(cluster="iran-war", prob=0.90, horizon="2026-12-31", level="0-3",
                  act="us_strike_iran", claims="does_not_occur", window="us-release-postvote",
                  prediction="No war-scale campaign on Iranian territory by 2026-12-31", **kw)

    def test_a_row_that_cannot_hold_with_an_open_one_is_refused(self):
        with self.assertRaises(SystemExit) as cm:
            quiet(ledger.add, self.second())
        self.assertIn("conflict level", str(cm.exception))
        self.assertEqual(ledger.db().execute("SELECT COUNT(*) FROM predictions").fetchone()[0], 1)

    def test_a_hedge_reason_lets_it_in_and_the_level_is_stored(self):
        out = quiet(ledger.add, self.second(hedge="a strike on Iranian soil need not become a campaign; #1 is the stronger view"))
        self.assertIn("HEDGE ACCEPTED", out)
        self.assertEqual(ledger.db().execute("SELECT level_lo,level_hi FROM predictions WHERE id=2").fetchone(), (0, 3))

    def test_a_compatible_row_is_logged_without_ceremony(self):
        quiet(ledger.add, ns(cluster="iran-war", prob=0.40, horizon="2026-12-31", level="0-3",
                             act="us_strike_iran", claims="does_not_occur", window="us-release-postvote",
                             prediction="No war-scale campaign on Iranian territory by 2026-12-31 (alt)"))
        self.assertEqual(ledger.db().execute("SELECT COUNT(*) FROM predictions").fetchone()[0], 2)

    def test_a_conflict_cluster_row_with_no_level_is_warned_and_none_is_silent(self):
        warned = quiet(ledger.add, ns(cluster="iran-war", level=None))
        self.assertIn("declare --level", warned)
        silent = quiet(ledger.add, ns(cluster="iran-war", level="none", prediction="No Hormuz toll by 2027-01-04"))
        self.assertNotIn("declare --level", silent)

    def test_a_level_needs_a_cluster_with_a_scale(self):
        with self.assertRaises(SystemExit):
            quiet(ledger.add, ns(cluster="fed-path", level="2"))


class StateGate(unittest.TestCase):
    """`ledger.py add --state`: a row in ANY cluster is checked against open rows that declared the same world state."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        ledger.DB = pathlib.Path(self.tmp.name) / "ledger.db"
        quiet(ledger.add, ns(cluster="iran-war", prob=0.68, horizon="2026-09-06", state=["hormuz=0-1"], level="none",
                             prediction="Hormuz does not fully normalize within 60 days", ts="2026-07-08T12:00:00Z"))

    def tearDown(self):
        self.tmp.cleanup()

    def opec(self, **kw):
        return ns(cluster="opec-policy", prob=0.58, horizon="2026-09-15", state=["hormuz=2"],
                  prediction="OPEC+ trims its hikes into a normalizing-Hormuz glut", ts="2026-07-11T12:00:00Z", **kw)

    def test_a_row_in_another_cluster_that_needs_the_opposite_state_is_refused(self):
        with self.assertRaises(SystemExit) as cm:
            quiet(ledger.add, self.opec())
        self.assertIn("world state", str(cm.exception))

    def test_a_hedge_lets_it_in_and_stores_the_state(self):
        out = quiet(ledger.add, self.opec(hedge="a glut can come from demand loss without Hormuz fully reopening; #1 is the stronger view"))
        self.assertIn("HEDGE ACCEPTED", out)
        raw = ledger.db().execute("SELECT states FROM predictions WHERE id=2").fetchone()[0]
        self.assertEqual(json.loads(raw), {"hormuz": [2, 2]})

    def test_a_compatible_state_is_logged(self):
        quiet(ledger.add, ns(cluster="opec-policy", prob=0.55, horizon="2026-09-15", state=["hormuz=1-2"],
                             prediction="OPEC+ holds quotas while Hormuz partly reopens", ts="2026-07-11T12:00:00Z"))
        self.assertEqual(ledger.db().execute("SELECT COUNT(*) FROM predictions").fetchone()[0], 2)

    def test_an_unknown_state_is_rejected(self):
        with self.assertRaises(SystemExit):
            quiet(ledger.add, ns(cluster="x", state=["nonsense=1"]))


class IncentiveGate(unittest.TestCase):
    """R37 at the door: a --level row must read the deciders' calendar."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        ledger.DB = pathlib.Path(self.tmp.name) / "ledger.db"

    def tearDown(self):
        self.tmp.cleanup()

    def row(self, **kw):
        base = dict(cluster="iran-war", prob=0.30, horizon="2026-11-03", level="3-4", ts="2026-10-23T12:00:00Z",
                    prediction="The US strikes Iranian territory before the 2026-11-03 midterms")
        base.update(kw)
        return ns(**base)

    def test_a_conflict_row_with_no_window_is_refused(self):
        with self.assertRaises(SystemExit) as cm:
            quiet(ledger.add, self.row())
        self.assertIn("R37", str(cm.exception))

    def test_a_strike_call_inside_a_stated_pledge_window_is_refused_above_half(self):
        with self.assertRaises(SystemExit):
            quiet(ledger.add, self.row(prob=0.60, act="us_strike_iran", claims="occurs", window="us-pledge-midterms"))

    def test_a_properly_declared_row_is_logged_with_its_incentive(self):
        quiet(ledger.add, self.row(act="us_strike_iran", claims="occurs", window="us-pledge-midterms",
                                   trigger="an Iranian attack that kills US personnel"))
        r = ledger.db().execute("SELECT act,claims,window_id,trigger_text FROM predictions").fetchone()
        self.assertEqual(r, ("us_strike_iran", "occurs", "us-pledge-midterms", "an Iranian attack that kills US personnel"))

    def test_an_unknown_window_is_refused(self):
        with self.assertRaises(SystemExit):
            quiet(ledger.add, self.row(act="us_strike_iran", claims="occurs", window="no-such-window"))


if __name__ == "__main__":
    unittest.main()
