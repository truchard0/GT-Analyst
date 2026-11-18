#!/usr/bin/env python3
"""python -m unittest tests.test_constraints -v

R37 reads the deciders' calendar. Each test is a row the engine actually wrote (or the live call) and what the calendar says
about it using ONLY facts public on that date. The honest negatives matter as much as the catches: #59 and #72 are not caught."""
import datetime as dt
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "pipeline"))
import constraints as ct  # noqa: E402

CAL = ct.load()


def chk(**k):
    return ct.check_incentive(CAL, **k)


def sev(fs):
    return [f.severity for f in fs]


class Rows(unittest.TestCase):
    def test_19_calm_the_day_after_iran_hit_vessels_is_refused(self):
        f = chk(act="us_strike_iran", claims="does_not_occur", prob=.70, window="us-mou-jun", trigger="", horizon="2026-09-06", as_of=dt.date(2026, 7, 8))
        self.assertEqual(sev(f), ["error"])
        self.assertIn("2026-07-07", f[0].text)

    def test_calm_after_a_trigger_is_allowed_if_the_row_says_why_it_holds(self):
        f = chk(act="us_strike_iran", claims="does_not_occur", prob=.70, window="us-mou-jun", horizon="2026-09-06", as_of=dt.date(2026, 7, 8),
                trigger="the 7/7 attacks hit merchant ships, not US forces, and the MOU window is still in force")
        self.assertEqual(f, [])

    def test_59_is_not_caught_no_suppress_window_was_public(self):
        """The honest negative: on 7/21 no window was public (the 7/25 pause did not exist yet). The calendar alone cannot
        explain the 8/2-8/14 pause; a stand-down hazard after ~2 weeks of a campaign would have to."""
        f = chk(act="us_strike_iran", claims="occurs", prob=.72, window="none: no suppress window is public on 7/21 and round 2 is in its second week",
                trigger="mediators push a 10-day ceasefire", horizon="2026-08-15", as_of=dt.date(2026, 7, 21))
        self.assertEqual([x for x in f if x.severity == "error"], [])

    def test_72_is_caught_the_standdown_superseded_the_trigger(self):
        """8/2: Trump said he called off the planned attack, three days after the 7/29 trigger. The restraint was re-chosen AFTER
        the trigger, so a strike call at 0.55 inside it is refused. (Same-day timing: the row may have preceded the statement.)"""
        f = chk(act="us_strike_iran", claims="occurs", prob=.55, window="us-standdown-aug", trigger="", horizon="2026-08-03", as_of=dt.date(2026, 8, 2))
        self.assertEqual(sev(f), ["error"])

    def test_68_a_hit_is_flagged_and_must_say_why_calm_holds(self):
        """7/31: a trigger (7/29) was on file and the 8/2 stand-down was not yet public, so a calm call at 0.55 must explain itself."""
        f = chk(act="us_strike_iran", claims="does_not_occur", prob=.55, window="none: the 8/2 stand-down is not public yet", trigger="", horizon="2026-08-16", as_of=dt.date(2026, 7, 31))
        self.assertEqual(sev(f), ["error"])
        f = chk(act="us_strike_iran", claims="does_not_occur", prob=.55, window="none: the 8/2 stand-down is not public yet", horizon="2026-08-16", as_of=dt.date(2026, 7, 31),
                trigger="7/29 was a one-day retaliation and the mediators are pushing a ceasefire")
        self.assertEqual([x for x in f if x.severity == "error"], [])

    def test_a_strike_call_above_half_inside_the_stated_pledge_is_refused(self):
        f = chk(act="us_strike_iran", claims="occurs", prob=.60, window="us-pledge-midterms", horizon="2026-11-03", as_of=dt.date(2026, 10, 23))
        self.assertEqual(sev(f), ["error"])

    def test_the_same_call_at_or_below_half_is_fine(self):
        f = chk(act="us_strike_iran", claims="occurs", prob=.30, window="us-pledge-midterms", horizon="2026-11-03", as_of=dt.date(2026, 10, 23), trigger="an Iranian attack that kills US personnel")
        self.assertEqual([x for x in f if x.severity == "error"], [])

    def test_a_horizon_past_the_window_is_not_inside_it(self):
        f = chk(act="us_strike_iran", claims="occurs", prob=.45, window="us-release-postvote", horizon="2026-12-31", as_of=dt.date(2026, 10, 23))
        self.assertEqual(f, [])
        f = chk(act="us_strike_iran", claims="occurs", prob=.70, window="us-pledge-midterms", horizon="2026-12-31", as_of=dt.date(2026, 10, 23))
        self.assertEqual([x for x in f if x.severity == "error"], [])


class Declarations(unittest.TestCase):
    def test_a_window_that_was_not_yet_public_cannot_inform_a_row(self):
        f = chk(act="us_strike_iran", claims="occurs", prob=.3, window="us-pledge-midterms", horizon="2026-10-05", as_of=dt.date(2026, 9, 20))
        self.assertTrue(any("not public until" in x.text for x in f))

    def test_unknown_act_window_or_claim(self):
        self.assertEqual(sev(chk(act="nope", claims="occurs", prob=.3, window="none: x" * 5, horizon="2026-11-03", as_of=dt.date(2026, 10, 23))), ["error"])
        self.assertEqual(sev(chk(act="us_strike_iran", claims="maybe", prob=.3, window="none", horizon="2026-11-03", as_of=dt.date(2026, 10, 23))), ["error"])
        self.assertEqual(sev(chk(act="us_strike_iran", claims="occurs", prob=.3, window="ghost", horizon="2026-11-03", as_of=dt.date(2026, 10, 23))), ["error"])

    def test_none_needs_a_reason(self):
        f = chk(act="us_strike_iran", claims="occurs", prob=.3, window="none", horizon="2026-11-03", as_of=dt.date(2026, 10, 23))
        self.assertEqual(sev(f), ["error"])

    def test_a_window_must_govern_the_act(self):
        f = chk(act="ir_ship_attack", claims="occurs", prob=.9, window="us-pledge-midterms", horizon="2026-11-03", as_of=dt.date(2026, 10, 23))
        self.assertTrue(any("governs" in x.text for x in f))


class Calendar(unittest.TestCase):
    def test_every_window_is_well_formed(self):
        ids = set()
        for w in CAL["windows"]:
            self.assertNotIn(w["id"], ids)
            ids.add(w["id"])
            self.assertIn(w["effect"], ("suppresses", "permits"))
            self.assertIn(w["strength"], ("stated", "inferred"))
            self.assertTrue(set(w["acts"]) <= set(CAL["acts"]))
            self.assertLessEqual(ct.d(w["start"]), ct.d(w["end"]))
            self.assertGreater(len(w["fact"]), 40)

    def test_the_lens_reads_only_public_facts(self):
        self.assertEqual(ct.lens(CAL, "us_strike_iran", dt.date(2026, 10, 9))["suppress"], ["us-pledge-midterms"])
        self.assertEqual(ct.lens(CAL, "us_strike_iran", dt.date(2026, 10, 7))["suppress"], ["us-pause-sep"])
        self.assertEqual(ct.lens(CAL, "us_strike_iran", dt.date(2026, 7, 8))["net"], "trigger")


if __name__ == "__main__":
    unittest.main()
