#!/usr/bin/env python3
"""Rule-by-rule tests for the buildout's no-view gate.  python -m unittest tests.test_buildout_validate -v

Same shape as tests/test_schema.py: one node that must trip each rule and one that must clear it,
so a rule that is ever loosened by accident turns a test red.

WHY THIS FILE EXISTS. The 2026-09-21 self-check tested PROSE - "p >= 0.70 needs a structural word
in `basis`" - and passed `brent-band-q4` at 0.66 against no-view odds of 0.39, and
`iran-pause-duration-nov` at 0.48 against a survival band of 0.21-0.43. A check on wording cannot
catch a mis-priced number. These tests cover the four rules that run the arithmetic instead, plus
the dated-catalyst escape hatch that is the only legal way past them.
"""
import copy
import importlib.util
import pathlib
import re
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("buildout", ROOT / "tools" / "buildout_2026_09_21.py")
bo = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bo)          # authoring the 200 nodes is a module-level side effect
AUTHORED = {n["id"]: n for n in bo.NODES}

RANGE_CMD = "python tools/range_odds.py --spot 100 --lo 90 --hi 110 --days 20 --vol 1.0"
CYCLE_CMD = "python tools/cycle_odds.py --current 12 --days 40 --prior-median 65"


def level(**over):
    """A level row that CLEARS the gate: p 0.72 against no-view odds 0.80."""
    n = {"id": "lvl", "row_class": "level", "p": 0.72,
         "basis": "No-view odds off the distance to the threshold on a published daily series.",
         "no_view": {"tool": "range_odds", "command": RANGE_CMD, "odds": 0.80, "note": "assumed spot"}}
    n.update(over)
    return n


def duration(**over):
    """A duration row that CLEARS the gate: p 0.32, survival band 0.21-0.43."""
    n = {"id": "dur", "row_class": "duration", "p": 0.32,
         "basis": "DURATION, priced from the cycle-odds band rather than from either leg.",
         "no_view": {"tool": "cycle_odds", "command": CYCLE_CMD,
                     "ends_lo": 0.57, "ends_hi": 0.79, "phase_ends": False, "note": "assumed ages"}}
    n.update(over)
    return n


def tags(node):
    """The rule tags no_view_problems raises for one node."""
    return " | ".join(bo.no_view_problems(node))


class LevelRows(unittest.TestCase):
    """R11: a level row is priced against tools/range_odds.py, not against prose."""

    def test_a_level_row_without_no_view_odds_is_refused(self):
        n = level()
        del n["no_view"]
        self.assertIn("R11-NOVIEW", tags(n))
        self.assertNotIn("R11-NOVIEW", tags(level()))

    def test_the_command_must_actually_invoke_range_odds(self):
        """Mirrors schema.py R11's check on no_view_odds.command: a note is not a run."""
        self.assertIn("R11-TOOL", tags(level(no_view={"tool": "range_odds", "odds": 0.80,
                                                      "command": "eyeballed it against Q3"})))
        self.assertIn("R11-TOOL", tags(level(no_view={"tool": "range_odds", "odds": 0.80,
                                                      "command": "python tools/cycle_odds.py --current 1 --days 2"})))
        self.assertNotIn("R11-TOOL", tags(level()))

    def test_odds_must_be_a_probability(self):
        for bogus in (1.4, -0.1, "0.80", None):
            self.assertIn("R11-ODDS", tags(level(no_view={"tool": "range_odds",
                                                          "command": RANGE_CMD, "odds": bogus})), bogus)
        self.assertNotIn("R11-ODDS", tags(level()))

    def test_more_than_0_20_off_the_no_view_odds_is_refused(self):
        """brent-band-q4: logged 0.66 against odds of 0.39 and nothing in the file objected."""
        self.assertIn("R11-GAP", tags(level(p=0.45, no_view={"tool": "range_odds",
                                                             "command": RANGE_CMD, "odds": 0.80})))
        self.assertIn("R11-GAP", tags(level(p=0.66, no_view={"tool": "range_odds",
                                                             "command": RANGE_CMD, "odds": 0.39})))
        self.assertNotIn("R11-GAP", tags(level(p=0.60)))      # 0.20 off exactly: legal
        self.assertNotIn("R11-GAP", tags(level(p=0.72)))

    def test_a_dated_catalyst_buys_the_deviation_and_a_story_does_not(self):
        far = dict(p=0.45, no_view={"tool": "range_odds", "command": RANGE_CMD, "odds": 0.80})
        self.assertIn("R11-GAP", tags(level(basis="OPEC+ is widely expected to act soon.", **far)))
        self.assertNotIn("R11-GAP", tags(level(basis="The OPEC+ quota decision lands 2026-11-29.", **far)))
        self.assertNotIn("R11-GAP", tags(level(basis="The QRA lands 11/4 and resets coupon sizes.", **far)))
        self.assertNotIn("R11-GAP", tags(level(basis="Resolves on the 12/9/2026 SEP.", **far)))

    def test_a_month_year_token_is_not_a_dated_catalyst(self):
        """'through 3/2027' is a horizon, not a catalyst. #72 was a plan with no execution date."""
        self.assertTrue(bo.dated_catalyst("the panel reports 2027-06-30"))
        self.assertTrue(bo.dated_catalyst("the auction settles 12/31"))
        self.assertFalse(bo.dated_catalyst("every weekly close to 3/2027"))
        self.assertFalse(bo.dated_catalyst("a 1.5x vol ratio and a 13/45 split"))
        self.assertFalse(bo.dated_catalyst("the supply response is biological"))


class DurationRows(unittest.TestCase):
    """R27: a duration row is priced against tools/cycle_odds.py's BAND, not its point."""

    def test_a_duration_row_without_a_band_is_refused(self):
        n = duration()
        del n["no_view"]
        self.assertIn("R27-NOVIEW", tags(n))
        self.assertNotIn("R27-NOVIEW", tags(duration()))

    def test_the_command_must_actually_invoke_cycle_odds(self):
        self.assertIn("R27-TOOL", tags(duration(no_view={"tool": "cycle_odds", "ends_lo": 0.57,
                                                         "ends_hi": 0.79, "command": "legs run 2-5 weeks"})))
        self.assertNotIn("R27-TOOL", tags(duration()))

    def test_the_band_must_be_a_probability_band(self):
        for lo, hi in ((0.79, 0.57), (-0.1, 0.5), (0.5, 1.2), (None, 0.5)):
            self.assertIn("R27-BAND", tags(duration(no_view={"tool": "cycle_odds", "command": CYCLE_CMD,
                                                             "ends_lo": lo, "ends_hi": hi})), (lo, hi))
        self.assertNotIn("R27-BAND", tags(duration()))

    def test_p_more_than_0_10_outside_the_survival_band_is_refused(self):
        """The band the tool prints is for an ENDING; a 'still in effect' row is its complement."""
        self.assertIn("R27-BAND", tags(duration(p=0.70)))     # survival band is 0.21-0.43
        self.assertIn("R27-BAND", tags(duration(p=0.05)))
        self.assertNotIn("R27-BAND", tags(duration(p=0.52)))  # 0.10 outside exactly: legal
        self.assertNotIn("R27-BAND", tags(duration(p=0.38)))

    def test_phase_ends_flips_which_band_is_checked(self):
        """Same tool output, opposite claim: cocoa-normalisation and ai-litigation claim the phase ENDS."""
        ends = duration(p=0.68)
        ends["no_view"] = dict(ends["no_view"], phase_ends=True)
        self.assertNotIn("R27-BAND", tags(ends))              # 0.68 sits inside the 0.57-0.79 ending band
        self.assertIn("R27-BAND", tags(duration(p=0.68)))     # the same price as a SURVIVAL claim is refused
        lasts = duration(p=0.32)
        lasts["no_view"] = dict(lasts["no_view"], phase_ends=True)
        self.assertIn("R27-BAND", tags(lasts))

    def test_a_dated_catalyst_buys_the_deviation(self):
        self.assertIn("R27-BAND", tags(duration(p=0.70)))
        self.assertNotIn("R27-BAND", tags(duration(p=0.70, basis="The MOU expires 2026-11-16.")))


class OtherRowClasses(unittest.TestCase):
    def test_only_level_and_duration_rows_carry_a_no_view_block(self):
        self.assertIn("R11-NOVIEW", tags(level(row_class="invariant")))
        for cls in ("invariant", "scheduled", "marker", "direction", "branch"):
            n = level(row_class=cls)
            del n["no_view"]
            self.assertEqual(tags(n), "", cls)


class WiredIntoValidate(unittest.TestCase):
    """The unit rules above are worthless if validate() never calls them (the 9/21 failure mode
    was exactly a rule that existed in prose and bound on nothing)."""

    def batch(self, nodes):
        saved = bo.NODES[:]
        bo.NODES.clear()
        bo.NODES.extend(nodes)
        try:
            return " | ".join(bo.validate({"now"}, {"rates-credit"}))
        finally:
            bo.NODES.clear()
            bo.NODES.extend(saved)

    def full(self, **over):
        n = copy.deepcopy(AUTHORED["real-rate-band"])
        n.update(over)
        return n

    def test_validate_surfaces_the_no_view_rules(self):
        stripped = self.full()
        stripped.pop("no_view")
        self.assertIn("R11-NOVIEW", self.batch([stripped]))
        self.assertIn("R11-GAP", self.batch([self.full(p=0.20)]))
        self.assertNotIn("R11-", self.batch([self.full()]))

    def test_the_authored_batch_carries_a_no_view_block_on_every_level_and_duration_row(self):
        need = [n for n in bo.NODES if n["row_class"] in ("level", "duration")]
        self.assertEqual(len(need), 39)
        self.assertEqual([n["id"] for n in need if "no_view" not in n], [])
        self.assertEqual([n["id"] for n in bo.NODES if bo.no_view_problems(n)], [])


class TheRecordedNumbersAreReal(unittest.TestCase):
    """An assumed INPUT is fine and is declared in `note`; a fabricated OUTPUT is not. Every
    duration band is re-derived here from the recorded command - cycle_odds.py is pure arithmetic,
    and range_odds.py is seeded, so both are reproducible."""

    def recompute(self, cmd):
        args = cmd.split()[2:]
        out = subprocess.run([sys.executable, str(ROOT / "tools" / "cycle_odds.py")] + args,
                             capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
        self.assertEqual(out.returncode, 0, out.stderr)
        tail = out.stdout.split("no-view odds of an ending:")[1].split("\n")[0]
        lo, hi = tail.split("..")
        return round(float(lo), 2), round(float(hi), 2)

    def test_every_duration_band_reproduces_from_its_recorded_command(self):
        for n in bo.NODES:
            if n["row_class"] != "duration":
                continue
            nv = n["no_view"]
            with self.subTest(node=n["id"]):
                self.assertEqual((nv["ends_lo"], nv["ends_hi"]), self.recompute(nv["command"]))

    def test_a_short_level_row_reproduces_from_its_recorded_command(self):
        """range_odds.py is a 40k-path Monte Carlo on seed 7, so it is deterministic. Only the
        cheap rows are re-run here; the rest were produced by the same batch runner."""
        for nid in ("u3-band", "stablecoin-supply", "tokenized-treasuries", "wage-band"):
            nv = AUTHORED[nid]["no_view"]
            args = nv["command"].split()[2:]
            out = subprocess.run([sys.executable, str(ROOT / "tools" / "range_odds.py")] + args,
                                 capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
            self.assertEqual(out.returncode, 0, out.stderr)
            got = float(re.search(r"NO-VIEW P\([^)]*\) = ([0-9.]+)", out.stdout).group(1))
            with self.subTest(node=nid):
                self.assertEqual(nv["odds"], got)


if __name__ == "__main__":
    unittest.main()
