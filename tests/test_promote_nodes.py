#!/usr/bin/env python3
"""python -m unittest tests.test_promote_nodes -v

The promoter turns priced nodes into scored rows. What it must NOT do is let a row in that nobody can
settle (#59, #30), that is priced against an invented reference, or that quietly contradicts the
tool-checked odds the node already carries (brent-band-q4). One mutation per refusal."""
import copy
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
sys.path.insert(0, str(ROOT / "tools"))
import promote_nodes as pn  # noqa: E402

SECTORS = {"energy", "rates", "gold_pm", "shipping"}
NODE = {"id": "n1", "p": 0.70, "date": "2027-06-30", "lane": "rates-credit", "row_class": "scheduled",
        "basis": "published monthly series", "no_view": None}
SPEC = {"node_id": "n1", "skip": None,
        "prediction": "The Freddie Mac 30-year PMMS print for the week ending 2027-06-24 is above 6.00 percent",
        "falsifier": "The PMMS print for the week ending 2027-06-24 is at or below 6.00 percent, read on 2027-06-30",
        "resolution_source": {"publisher": "Freddie Mac", "series": "PMMS 30-year fixed, weekly",
                              "convention": "first published print, not a revision"},
        "base_rate": 0.65, "base_class": "weekly PMMS above 6.00 in 190 of the last 260 weeks (structural count)",
        "direction": "up", "sectors": ["rates"], "tickers": [], "first_publication": "2027-06-24"}


def run(spec=None, node=None, existing=frozenset()):
    return pn.problems(spec or SPEC, node or NODE, SECTORS, set(existing))


class Validator(unittest.TestCase):
    def test_a_good_spec_is_clean(self):
        self.assertEqual(run(), [])

    def test_a_calendar_fact_is_never_promoted(self):
        """User 2026-10-23: 'these are not calls... just factual events that occur'. An invariant or scheduled node at p >= 0.95
        (the term opens, the meeting is held) and every lane anchor are facts and cannot become a scored ledger row."""
        fact = dict(NODE, id="ev-fomc-statement", p=0.98, row_class="scheduled")
        self.assertTrue(any("calendar fact" in p for p in run(node=fact)))
        anchor = dict(NODE, id="rc-anchor", p=1.0, row_class="invariant")
        self.assertTrue(any("calendar fact" in p for p in run(node=anchor)))
        self.assertFalse(any("calendar fact" in p for p in run(node=dict(NODE, p=0.90, row_class="scheduled"))))      # a scheduled VALUE call below 0.95 is still a call

    def test_a_predetermined_outcome_is_never_promoted(self):
        """#85/#87 asked whether NATO allies would be at 2% for 2026 after NATO had already published the 2026 estimates."""
        self.assertTrue(any("predetermined" in p for p in run(dict(SPEC, first_publication="2026-07-07"))))
        self.assertTrue(any("first_publication missing" in p for p in run({k: v for k, v in SPEC.items() if k != "first_publication"})))

    def test_missing_resolution_source_detail_is_refused(self):
        s = copy.deepcopy(SPEC)
        s["resolution_source"]["convention"] = ""
        self.assertTrue(any("R30" in p for p in run(s)))

    def test_falsifier_must_restate_the_horizon(self):
        s = copy.deepcopy(SPEC)
        s["falsifier"] = "The PMMS print is at or below 6.00 percent"
        self.assertTrue(any("restate the horizon" in p for p in run(s)))

    def test_base_class_needs_a_count(self):
        s = copy.deepcopy(SPEC)
        s["base_class"] = "historically this has usually been the case for mortgages"
        self.assertTrue(any("R25" in p for p in run(s)))

    def test_gap_over_a_tenth_needs_a_dated_reason(self):
        s = copy.deepcopy(SPEC)
        s["base_rate"] = 0.40
        self.assertTrue(any("R26" in p for p in run(s)))
        s["diverge"] = "the 2026-10-01 print of 7.28 puts the series 1.28 points above the threshold"
        self.assertFalse(any("R26" in p for p in run(s)))

    def test_unknown_sector_and_direction_are_refused(self):
        s = copy.deepcopy(SPEC)
        s["sectors"] = ["crypto"]
        s["direction"] = "sideways"
        out = " ".join(run(s))
        self.assertIn("unknown sector", out)
        self.assertIn("direction", out)

    def test_a_duplicate_prediction_is_refused(self):
        key = pn.re.sub(r"\W+", " ", SPEC["prediction"].lower()).strip()
        self.assertTrue(any("R24" in p for p in run(existing={key})))

    def test_level_row_must_take_its_recorded_no_view_odds_as_the_base_rate(self):
        """The brent-band-q4 lesson: the node already carries a tool-checked number. A spec may not
        quietly replace it with a more flattering one."""
        n = copy.deepcopy(NODE)
        n["row_class"] = "level"
        n["no_view"] = {"odds": 0.33, "command": "python tools/range_odds.py --spot 98 --lo 85 --hi 125 --days 70 --vol 2.5"}
        s = copy.deepcopy(SPEC)
        s["base_rate"] = 0.65
        s["diverge"] = "a dated reason that is long enough to pass the length check 2026-10-01"
        self.assertTrue(any("no-view odds" in p for p in run(s, n)))
        s["base_rate"] = 0.33
        s.pop("diverge")
        self.assertFalse(any("no-view odds" in p for p in run(s, n)))

    def test_duration_row_base_rate_must_sit_inside_its_cycle_band(self):
        n = copy.deepcopy(NODE)
        n["row_class"] = "duration"
        n["no_view"] = {"ends_lo": 0.57, "ends_hi": 0.79, "phase_ends": False}      # survival band = 0.21..0.43
        s = copy.deepcopy(SPEC)
        s["base_rate"] = 0.70
        s["diverge"] = "a dated reason that is long enough to pass the length check 2026-10-01"
        self.assertTrue(any("cycle band" in p for p in run(s, n)))
        s["base_rate"] = 0.30
        s.pop("diverge")
        self.assertFalse(any("cycle band" in p for p in run(s, n)))

    def test_a_compound_claim_is_refused_by_the_ledger_lint(self):
        s = copy.deepcopy(SPEC)
        s["prediction"] = "The PMMS print is above 6.00 percent AND the 10-year yield closes above 4.00 percent by 2027-06-30"
        self.assertTrue(any(p.startswith("lint:") for p in run(s)))


if __name__ == "__main__":
    unittest.main()
