#!/usr/bin/env python3
"""tools/cycle_odds.py - the no-view number for duration rows.   python -m unittest tests.test_cycle_odds -v"""
import contextlib
import io
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "tools"))
import cycle_odds  # noqa: E402


class CycleOdds(unittest.TestCase):
    def test_no_prior_is_the_cycles_own_history(self):
        # 2 endings in 60 pause-days, 22 more days: (60/82)^2
        self.assertAlmostEqual(cycle_odds.survive([22, 28], 10, 22, 65, 0.0), (60 / 82) ** 2)

    def test_prior_median_is_honoured_when_there_is_no_data(self):
        # with no data and weight 1 the prior alone gives survival 0.5 at its median
        self.assertAlmostEqual(cycle_odds.survive([], 0, 65, 65, 1.0), 0.5, places=6)

    def test_a_longer_reference_class_makes_the_pause_more_durable(self):
        self.assertGreater(cycle_odds.survive([22, 28], 10, 22, 193, 1.0), cycle_odds.survive([22, 28], 10, 22, 65, 1.0))

    def test_longer_horizons_are_never_safer(self):
        self.assertGreater(cycle_odds.survive([20, 32], 10, 10, 65, 1.0), cycle_odds.survive([20, 32], 10, 40, 65, 1.0))

    def test_verdict_flags_a_view_outside_the_band(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            cycle_odds.main(["--completed", "22,28", "--current", "10", "--days", "22", "--stated", "0.75"])
        self.assertIn("That is a VIEW", buf.getvalue())
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            cycle_odds.main(["--completed", "22,28", "--current", "10", "--days", "22", "--stated", "0.40"])
        self.assertIn("inside the band", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
