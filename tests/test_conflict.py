#!/usr/bin/env python3
"""python -m unittest tests.test_conflict -v

The check exists because R28 compared up-vs-down only and every Iran row is 'vol'. Each test is one way two rows can
fail to fit one distribution over 'how hard the fighting gets', plus the honest negative: the 2026-07-08 batch that
motivated the work is NOT formally incoherent, and the check must say so rather than flag it to look useful."""
import datetime as dt
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "pipeline"))
import conflict as cf  # noqa: E402

T = dt.date(2026, 7, 8)


def row(i, p, lo, hi, hz="2026-09-06"):
    return cf.Claim(str(i), p, lo, hi, hz, "iran-war")


class Pairs(unittest.TestCase):
    def test_disjoint_claims_over_one_window_that_sum_past_one_are_refused(self):
        f = cf.check([row(1, .70, 0, 1), row(2, .50, 3, 4)], T)
        self.assertEqual([x.severity for x in f], ["error"])

    def test_disjoint_claims_that_fit_under_one_pass(self):
        self.assertEqual(cf.check([row(1, .40, 0, 1), row(2, .50, 3, 4)], T), [])

    def test_a_longer_window_cannot_end_lower_than_a_shorter_one(self):
        # a strike by 8/1 forces level >= 3 by 9/1, so 'stays at or under 2 by 9/1' cannot also be likely
        f = cf.check([row(1, .60, 3, 4, "2026-08-01"), row(2, .60, 0, 2, "2026-09-01")], T)
        self.assertTrue(f and f[0].severity == "error")

    def test_overlapping_claims_are_fine(self):
        self.assertEqual(cf.check([row(1, .70, 2, 4), row(2, .70, 0, 3)], T), [])


class Escalation(unittest.TestCase):
    def test_a_near_certain_strike_with_a_near_certain_no_war_scale_is_an_error(self):
        f = cf.check([row(1, .95, 3, 4), row(2, .90, 0, 3)], T)
        self.assertEqual([x.severity for x in f], ["error"])
        self.assertIn("3 of 7", f[0].text)

    def test_the_lower_bound_passes_while_the_point_estimate_warns(self):
        f = cf.check([row(1, .50, 3, 4), row(2, .85, 0, 3)], T)
        self.assertEqual([x.severity for x in f], ["warn"])

    def test_an_unlikely_strike_is_fine(self):
        self.assertEqual(cf.check([row(1, .30, 3, 4), row(2, .70, 0, 3)], T), [])

    def test_a_longer_window_is_scaled_down_before_it_is_compared(self):
        self.assertAlmostEqual(cf._scale_window(.74, 184, 60), .354, delta=.01)
        self.assertEqual(cf._scale_window(.74, 60, 184), .74)


class Batch(unittest.TestCase):
    def test_the_2026_07_08_batch_is_not_formally_incoherent(self):
        """#19 [0,3] .70, #15 [2,4] .70, #20 [2,4] .55, #21 [2,3] .58 by 9/6, #16 [3,4] .74 by 1/8."""
        rows = [row(19, .70, 0, 3), row(15, .70, 2, 4), row(20, .55, 2, 4), row(21, .58, 2, 3),
                row(16, .74, 3, 4, "2027-01-08")]
        self.assertEqual(cf.check(rows, T), [])


class Parse(unittest.TestCase):
    def test_levels(self):
        self.assertEqual(cf.parse_level("3", "iran-war"), (3, 3))
        self.assertEqual(cf.parse_level("0-3", "iran-war"), (0, 3))
        for bad in ("5", "3-1", "a", "1-2-3"):
            with self.assertRaises(ValueError):
                cf.parse_level(bad, "iran-war")


class WorldStates(unittest.TestCase):
    """The cross-cluster check: rows from ANY cluster claim values of a named state; disjoint claims must sum under 1."""
    T = dt.date(2026, 7, 11)

    def sc(self, i, p, state, lo, hi, hz="2026-09-06"):
        return cf.StateClaim(str(i), p, state, lo, hi, hz)

    def test_opec_glut_against_hormuz_does_not_normalize_is_refused(self):
        f = cf.check_states([self.sc(22, .68, "hormuz", 0, 1), self.sc("new", .58, "hormuz", 2, 2, "2026-09-15")], self.T)
        self.assertEqual([x.severity for x in f], ["error"])
        self.assertIn("1.26", f[0].text)

    def test_overlapping_state_claims_fit(self):
        self.assertEqual(cf.check_states([self.sc(22, .68, "hormuz", 0, 1), self.sc("new", .55, "hormuz", 1, 2)], self.T), [])

    def test_disjoint_claims_that_sum_under_one_fit(self):
        self.assertEqual(cf.check_states([self.sc(22, .40, "hormuz", 0, 1), self.sc("new", .50, "hormuz", 2, 2)], self.T), [])

    def test_horizons_far_apart_are_not_compared(self):
        self.assertEqual(cf.check_states([self.sc(22, .68, "hormuz", 0, 1, "2026-09-06"),
                                          self.sc("new", .58, "hormuz", 2, 2, "2027-03-01")], self.T), [])

    def test_brent_peak_a_calm_call_against_a_spike_call(self):
        f = cf.check_states([self.sc(23, .66, "brent_peak", 0, 0), self.sc("new", .55, "brent_peak", 3, 3, "2026-09-01")], self.T)
        self.assertEqual(len(f), 1)

    def test_different_states_never_conflict(self):
        self.assertEqual(cf.check_states([self.sc(22, .9, "hormuz", 0, 0), self.sc("new", .9, "brent_peak", 3, 3)], self.T), [])

    def test_parse_state(self):
        self.assertEqual(cf.parse_state("hormuz=0-1"), ("hormuz", 0, 1))
        self.assertEqual(cf.parse_state("brent_peak=3"), ("brent_peak", 3, 3))
        for bad in ("hormuz=3", "nonsense=1", "hormuz", "hormuz=2-1"):
            with self.assertRaises(ValueError):
                cf.parse_state(bad)

    def test_every_label_on_file_parses_against_the_registry(self):
        import json
        labels = json.loads((pathlib.Path(__file__).resolve().parent.parent / "data" / "state_labels.json")
                            .read_text(encoding="utf-8"))["labels"]
        for rid, lab in labels.items():
            for name, rng in (lab.get("states") or {}).items():
                cf.parse_state(f"{name}={rng}")
            if lab.get("level"):
                cf.parse_level(lab["level"], "iran-war")


if __name__ == "__main__":
    unittest.main()
