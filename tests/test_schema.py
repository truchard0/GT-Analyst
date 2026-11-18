#!/usr/bin/env python3
"""Rule-by-rule tests for the typed analysis contract.  python -m unittest tests.test_schema -v

One known-good document, then one mutation per rule: each must produce exactly the rule id it
targets. If a rule is ever loosened by accident, the matching test goes red."""
import copy
import datetime
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "pipeline"))
import ledger  # noqa: E402
import schema  # noqa: E402

NOW = datetime.datetime.now(datetime.timezone.utc)
ISO = NOW.strftime("%Y-%m-%dT%H:%MZ")
HZ = (NOW + datetime.timedelta(days=30)).strftime("%Y-%m-%d")


def ctx(**over):
    base = dict(
        item_ids={"a1", "a2", "a3"}, item_sources={"a1": "fed", "a2": "oilprice", "a3": "trump-truth"},
        item_age_hours={"a1": 3.0, "a2": 5.0, "a3": 1.0},
        sector_keys={"energy", "rates", "semis", "shipping"}, node_ids={"now", "cpi-reaccel", "flip-b"},
        lanes={"fed-macro", "iran-energy"}, open_by_cluster={"iran-war": 14, "fed-path": 1}, open_total=32,
        open_ledger_ids={11, 62}, existing_predictions={"an old call already in the ledger"})
    base.update(over)
    return schema.Context(**base)


def good():
    return {
        "schema_version": 3, "batch": "inbox/queue/x.md", "generated": ISO, "summary": "one event",
        "items": [{"item_id": "a1", "triage": "analyze", "reason": "primary Fed release", "event_id": "e1"},
                  {"item_id": "a2", "triage": "noise", "reason": "analyst price target - 12.1 rhetoric"},
                  {"item_id": "a3", "triage": "sentiment-only", "reason": "Truth post, no action attached"}],
        "events": [{
            "id": "e1", "title": "FOMC statement", "item_ids": ["a1"], "load_bearing_reported": [ISO],
            "players": [{"name": "FOMC majority", "role": "setter", "objective": "anchor expectations"},
                        {"name": "Hike dissenters", "role": "minority", "objective": "pre-empt pass-through"}],
            "game": {"game_type": "signaling", "conflict_kind": "distributive",
                     "information": "public statement, private dots", "timing": "repeated, next move at the presser"},
            "preferences": [{"actor": "FOMC majority", "assumption": "looks through supply shocks",
                             "flip_test": "a hike citing energy would falsify it"}],
            "ladder_credibility_read": "costly public commitment",
            "conviction": {"source_tier": "primary-doc", "source_quality": 0.20,
                           "capital_tier": "binding-scheduled", "capital_committed": 0.20,
                           "formal_verdict": "PASS-WITH-FLAGS", "formal_validity": 0.10,
                           "formal_flags": ["item 7: payoff ordering assumed"],
                           "independent_lenses": 2, "lens_names": ["11 look-through", "13d nowcast"],
                           "multi_lens": 0.10, "precondition_status": "mixed", "precondition": 0.07,
                           "total": 0.67},
            "market": {"shock_type": "supply", "branch_confirmation": "2y up 6bp on the statement",
                       "channels": ["rate expectations"], "priced_in": "CME had 35pct hike odds before",
                       "horizon_match": "one meeting"},
            "predictions": [{
                "ref": "p1", "prediction": "The FOMC leaves the target range unchanged at its next meeting",
                "prob": 0.72, "horizon": HZ,
                "falsifier": f"The FOMC raises or cuts the target range at the meeting before {HZ}",
                "sensitivity": "a hot CPI print before the meeting breaks the look-through premise",
                "row_class": "scheduled-print", "direction": "neutral", "lean": "neutral",
                "sectors": ["rates"], "tickers": ["TLT"], "cluster": "fed-path",
                "conviction_adjust": 0.0, "timeline": {"attach_to": "cpi-reaccel"},
                "reference": {"base_rate": 0.75, "base_class": "FOMC held at 6 of the last 8 meetings that followed a supply shock",
                              "market_prob": 0.70, "market_src": "Kalshi KXFED next meeting, 2c spread, 180k volume, 14:00Z"},
                "resolution_source": {"publisher": "Federal Reserve Board", "series": "FOMC statement, target range for the federal funds rate",
                                      "convention": "the statement released at the meeting; first release, not the minutes",
                                      "url": "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"},
                "meeting": {"meeting_date": HZ, "window_prob": 0.80},
                "red_team": {"key_assumptions": "look-through holds; no SEP", "mini_ach": "rival: pre-emptive hike - dissent count is diagnostic",
                             "premortem": "August CPI +0.6 forces the majority", "cascade_check": "evidence is the primary statement, not commentary",
                             "reference_class": "holds after supply shocks: ~80pct", "independence": "two independent lenses, no extremizing",
                             "leg_neutral_and_arithmetic": "not an oil-direction row; no level involved", "verdict": "PASS"}}]}],
        "suggested_resolutions": [{"ledger_id": 62, "outcome": "hit", "evidence": "PMMS rose 31bp by the horizon",
                                   "source_url": "https://www.freddiemac.com/pmms"}]}


def rules(doc_dict, c=None):
    doc = schema.parse(doc_dict)
    return [f.rule for f in schema.check(doc, c or ctx(), ledger.lint) if f.severity == "error"]


class Structure(unittest.TestCase):
    def test_good_document_is_clean(self):
        self.assertEqual(rules(good()), [])

    def test_unknown_key_rejected(self):
        d = good(); d["events"][0]["predictions"][0]["size"] = "5pct"
        with self.assertRaises(schema.SchemaError) as cm:
            schema.parse(d)
        self.assertIn("unknown field", str(cm.exception))

    def test_string_is_not_a_number(self):
        d = good(); d["events"][0]["predictions"][0]["prob"] = "0.72"
        with self.assertRaises(schema.SchemaError):
            schema.parse(d)

    def test_bool_is_not_a_number(self):
        d = good(); d["events"][0]["conviction"]["total"] = True
        with self.assertRaises(schema.SchemaError):
            schema.parse(d)

    def test_enum_enforced(self):
        d = good(); d["events"][0]["predictions"][0]["direction"] = "sideways"
        with self.assertRaises(schema.SchemaError) as cm:
            schema.parse(d)
        self.assertIn("direction", str(cm.exception))

    def test_missing_required(self):
        d = good(); del d["events"][0]["predictions"][0]["falsifier"]
        with self.assertRaises(schema.SchemaError) as cm:
            schema.parse(d)
        self.assertIn("falsifier", str(cm.exception))

    def test_json_schema_generated_from_types(self):
        js = schema.json_schema()
        self.assertIn("Prediction", js["$defs"])
        self.assertFalse(js["$defs"]["Prediction"]["additionalProperties"])
        self.assertIn("falsifier", js["$defs"]["Prediction"]["required"])


class Rules(unittest.TestCase):
    def mutate(self, fn, c=None):
        d = good(); fn(d); return rules(d, c)

    def P(self, d):
        return d["events"][0]["predictions"][0]

    def test_R01_every_item_needs_a_verdict(self):
        self.assertIn("R01", self.mutate(lambda d: d["items"].pop()))

    def test_R02_analyze_must_point_at_its_event(self):
        self.assertIn("R02", self.mutate(lambda d: d["items"][0].update(event_id="e9")))

    def test_R03_truth_social_rhetoric_is_not_an_event(self):
        def f(d):
            d["items"][0].update(triage="noise", event_id=None)
            d["items"][2].update(triage="analyze", event_id="e1")
            d["events"][0]["item_ids"] = ["a3"]
            d["events"][0]["conviction"].update(capital_tier="rhetoric", capital_committed=0.0, total=0.47)
        self.assertIn("R03", self.mutate(f))

    def test_R04_stale_items_cap_source_quality(self):
        self.assertIn("R04", self.mutate(lambda d: None, ctx(item_age_hours={"a1": 90.0, "a2": 5.0, "a3": 1.0})))

    def test_R05_components_must_be_anchors_and_sum(self):
        self.assertIn("R05", self.mutate(lambda d: d["events"][0]["conviction"].update(source_quality=0.18)))
        self.assertIn("R05", self.mutate(lambda d: d["events"][0]["conviction"].update(total=0.80)))

    def test_R06_noise_band_and_formal_fail_do_not_ledger(self):
        def noise(d):
            d["events"][0]["conviction"].update(source_tier="aggregator", source_quality=0.0,
                                                capital_tier="rhetoric", capital_committed=0.0, total=0.27)
        self.assertIn("R06", self.mutate(noise))
        self.assertIn("R06", self.mutate(lambda d: d["events"][0]["conviction"].update(
            formal_verdict="FAIL", formal_validity=0.0, total=0.57)))

    def test_R07_adjust_bounds(self):
        self.assertIn("R07", self.mutate(lambda d: self.P(d).update(conviction_adjust=0.10)))
        self.assertIn("R07", self.mutate(lambda d: self.P(d).update(conviction_adjust=0.05)))

    def test_R08_horizon_and_prob(self):
        self.assertIn("R08", self.mutate(lambda d: self.P(d).update(horizon="2020-01-01")))
        self.assertIn("R08", self.mutate(lambda d: self.P(d).update(prob=1.0)))

    def test_R09_compound_wording(self):
        self.assertIn("R09", self.mutate(lambda d: self.P(d).update(
            prediction="The FOMC holds AND the 2y yield falls below 4 percent by the meeting")))

    def test_R10_state_premise_needs_fresh_datapoint(self):
        def f(d):
            self.P(d).update(prediction="The ceasefire holds through the next FOMC meeting with no exchange of fire",
                             row_class="event-occurrence", prob=0.6)
        self.assertIn("R10", self.mutate(f))

        def stale(d):
            f(d)
            old = (NOW - datetime.timedelta(hours=60)).strftime("%Y-%m-%dT%H:%MZ")
            self.P(d)["state_premise"] = {"state": "ceasefire", "datapoint": "no strikes logged", "datapoint_ts": old,
                                          "source_url": "https://example.org/x"}
        self.assertIn("R10", self.mutate(stale))

    def test_R11_level_rows_need_no_view_odds_and_one_asset(self):
        def f(d):
            self.P(d).update(prediction="TLT does NOT close above 95 on any session before the meeting",
                             row_class="level-range", prob=0.6, tickers=["TLT", "IEF"])
        r = self.mutate(f)
        self.assertGreaterEqual(r.count("R11"), 2)

        def far(d):
            f(d); self.P(d)["tickers"] = ["TLT"]
            self.P(d)["no_view_odds"] = {"command": "python tools/range_odds.py --spot 90 --hi 95 --days 20 --vol 0.9",
                                        "odds": 0.20, "mechanism": "none"}
        self.assertIn("R11", self.mutate(far))

    def test_R12_leg_extrapolation_capped(self):
        def f(d):
            self.P(d).update(cluster="oil-tape", sectors=["energy"], direction="down", row_class="direction",
                             prob=0.65, prediction="Brent settles lower on the horizon date than on the analysis date",
                             falsifier=f"Front-month Brent settles higher on {HZ} than on the analysis date")
        self.assertIn("R12", self.mutate(f))

        def capped(d):
            f(d)
            self.P(d)["leg_neutral"] = {"tape_direction_10d": "de-escalation", "evidence": "Brent 104 -> 96 over ten sessions",
                                        "same_direction_as_call": True, "reversal_trigger": "Brent back above 100 within 5 sessions"}
        self.assertIn("R12", self.mutate(capped))

    def test_R13_high_probability_reserved(self):
        self.assertIn("R13", self.mutate(lambda d: self.P(d).update(row_class="event-occurrence")))
        self.assertIn("R13", self.mutate(lambda d: self.P(d).update(prob=0.85)))

    def test_R14_red_team_gate_required(self):
        self.assertIn("R14", self.mutate(lambda d: self.P(d).pop("red_team")))
        self.assertIn("R14", self.mutate(lambda d: self.P(d)["red_team"].update(verdict="FAIL")))

    def test_R15_overweight_cluster_needs_note(self):
        def f(d):
            self.P(d).update(cluster="iran-war", row_class="invariant")
            self.P(d)["leg_neutral"] = {"tape_direction_10d": "mixed", "evidence": "strike nights 0 of last 10; Brent 104 flat",
                                        "same_direction_as_call": False, "reversal_trigger": "10 consecutive strike nights"}
        self.assertIn("R15", self.mutate(f))

    def test_R16_sectors_and_tickers(self):
        self.assertIn("R16", self.mutate(lambda d: self.P(d).update(sectors=["crypto"])))
        self.assertIn("R16", self.mutate(lambda d: self.P(d).update(tickers=["tlt"])))

    def test_R17_timeline_wiring(self):
        self.assertIn("R17", self.mutate(lambda d: self.P(d).update(timeline={"attach_to": "no-such-node"})))
        self.assertIn("R17", self.mutate(lambda d: self.P(d).update(timeline={})))

    def test_R18_no_sizing(self):
        self.assertIn("R18", self.mutate(lambda d: self.P(d).update(
            sensitivity="a hot CPI breaks it; risk 2% of the portfolio on this")))

    def test_R19_conditional_needs_void_clause(self):
        self.assertIn("R19", self.mutate(lambda d: self.P(d).update(row_class="conditional")))

    def test_R21_resolutions_must_be_open_rows(self):
        self.assertIn("R21", self.mutate(lambda d: d["suggested_resolutions"][0].update(ledger_id=9999)))

    def test_R23_chessboard_needs_two_players(self):
        self.assertIn("R23", self.mutate(lambda d: d["events"][0]["players"].pop()))

    def test_R24_no_duplicate_calls(self):
        self.assertIn("R24", self.mutate(lambda d: self.P(d).update(
            prediction="An old call already in the ledger!")))

    def test_R25_every_row_needs_an_outside_view(self):
        self.assertIn("R25", self.mutate(lambda d: self.P(d).pop("reference")))
        self.assertIn("R25", self.mutate(lambda d: self.P(d)["reference"].update(base_class="history")))
        self.assertIn("R25", self.mutate(lambda d: self.P(d)["reference"].update(market_src="")))

    def test_R26_divergence_from_the_reference_needs_a_dated_reason(self):
        self.assertIn("R26", self.mutate(lambda d: self.P(d)["reference"].update(market_prob=0.50)))
        self.assertNotIn("R26", self.mutate(lambda d: self.P(d)["reference"].update(
            market_prob=0.50, divergence_reason="the 9/16 statement dropped 'further firming'; the market quote predates it")))
        # with no market price the base rate is the reference
        self.assertIn("R26", self.mutate(lambda d: self.P(d)["reference"].update(market_prob=None, market_src="", base_rate=0.4)))

    def iran(self, d, **kw):
        self.P(d).update(cluster="iran-war", prob=0.5, sectors=["defense"], lean="escalation",
                         leg_neutral={"tape_direction_10d": "de-escalation", "evidence": "no launches since 9/9; Brent 108 -> 103",
                                      "same_direction_as_call": False, "reversal_trigger": "a strike on Iranian soil before 10/12"})
        self.P(d)["reference"].update(base_rate=0.45, market_prob=None, market_src="")
        self.P(d).update(**kw)

    def test_R27_no_direction_rows_in_the_iran_cluster(self):
        self.assertIn("R27", self.mutate(lambda d: self.iran(d, row_class="direction")))

    def test_R27_duration_rows_carry_the_cycle_band(self):
        self.assertIn("R27", self.mutate(lambda d: self.iran(d, row_class="duration")))
        ok = {"command": "python tools/cycle_odds.py --completed 22,28 --current 10 --days 22", "ends_lo": 0.29, "ends_hi": 0.46}
        self.assertNotIn("R27", self.mutate(lambda d: self.iran(d, row_class="duration", phase_ends=True, cycle_odds=ok)))
        self.assertIn("R27", self.mutate(lambda d: self.iran(d, row_class="duration", phase_ends=True, cycle_odds=ok, prob=0.62)))
        # the same band read the other way round: "the pause LASTS" at 0.62 is inside 0.54..0.71
        self.assertNotIn("R27", self.mutate(lambda d: self.iran(d, row_class="duration", phase_ends=False, cycle_odds=ok,
                                                                prob=0.55, lean="de-escalation")))
        self.assertNotIn("R27", self.mutate(lambda d: self.iran(
            d, row_class="duration", phase_ends=True, prob=0.62,
            cycle_odds=dict(ok, catalyst="DoD order dated 9/24 moves a second carrier group into CENTCOM by 10/2"))))

    def test_duration_and_marker_rows_are_not_capped_as_leg_extrapolation(self):
        ok = {"command": "python tools/cycle_odds.py --completed 22,28 --current 10 --days 22", "ends_lo": 0.29, "ends_hi": 0.46}
        def go(d):
            self.iran(d, row_class="duration", phase_ends=False, cycle_odds=ok, prob=0.62, lean="de-escalation")
            self.P(d)["leg_neutral"]["same_direction_as_call"] = True
            self.P(d)["reference"].update(base_rate=0.6)
        self.assertNotIn("R12", self.mutate(go))

    # ══ v3 — the self-coherence rules. Every test below is a resolved loss. ══

    def test_R28_the_book_may_not_contradict_itself(self):
        """#26 said no oil-driven hike; the engine's OWN #32 said the print would be hot."""
        c = ctx(open_rows={32: schema.OpenRow(32, "August CPI runs hot", 0.62, "down",
                                              ("TLT",), "cpi-tape", HZ)},
                open_ledger_ids={11, 62, 32})
        up = lambda d: self.P(d).update(direction="up")
        self.assertIn("R28", self.mutate(up, c))
        def declared(d):
            up(d)
            self.P(d)["contradicts"] = [{"ledger_id": 32, "nature": "this row needs the CPI print #32 calls hot",
                                         "hedge_reason": "they cannot both pay; #32 is the one with the arithmetic and this row is being cut"}]
        self.assertNotIn("R28", self.mutate(declared, c))

    def test_R28_conflict_level_two_vol_rows_that_cannot_both_hold(self):
        """#19 and #16 were both direction 'vol', so the up-vs-down rule could not see them. Open #16 says a strike on
        Iranian soil (level 3-4) at 0.95; a new row saying war-scale does NOT happen (0-3) at 0.90 leaves 0.10 for a
        campaign, and 3 of this war's 7 strike episodes became campaigns."""
        c = ctx(open_rows={16: schema.OpenRow(16, "Israel strikes Iranian territory", 0.95, "vol", ("ITA",),
                                              "iran-war", HZ, level_lo=3, level_hi=4)},
                open_ledger_ids={11, 62, 16})
        def new(d):
            self.iran(d, prob=0.90, row_class="marker")
            self.P(d)["conflict_level"] = {"lo": 0, "hi": 3}
        self.assertIn("R28", self.mutate(new, c))
        def declared(d):
            new(d)
            self.P(d)["contradicts"] = [{"ledger_id": 16, "nature": "a strike on Iranian soil does not have to become a campaign",
                                         "hedge_reason": "the two cannot both pay; #16 is the one with the Israeli-readiness reporting"}]
        self.assertNotIn("R28", self.mutate(declared, c))

    def test_R28_conflict_level_a_compatible_row_passes(self):
        c = ctx(open_rows={16: schema.OpenRow(16, "Israel strikes Iranian territory", 0.52, "vol", ("ITA",),
                                              "iran-war", HZ, level_lo=3, level_hi=4)},
                open_ledger_ids={11, 62, 16})
        def new(d):
            self.iran(d, prob=0.70, row_class="marker")
            self.P(d)["conflict_level"] = {"lo": 0, "hi": 3}
        self.assertNotIn("R28", self.mutate(new, c))

    def test_R28_conflict_level_off_the_scale_is_an_error(self):
        def new(d):
            self.iran(d, row_class="marker")
            self.P(d)["conflict_level"] = {"lo": 3, "hi": 9}
        self.assertIn("R28", self.mutate(new))

    def test_R28_world_states_cross_cluster(self):
        """#29 (OPEC+ glut, needs Hormuz normal) vs open #22 (Hormuz does not normalize): different clusters."""
        c = ctx(open_rows={22: schema.OpenRow(22, "Hormuz does not fully normalize", 0.68, "vol", ("FRO",),
                                              "iran-war", HZ, states=(("hormuz", 0, 1),))},
                open_ledger_ids={11, 62, 22})
        def new(d):
            self.P(d).update(cluster="opec-policy", prob=0.58, row_class="marker")
            self.P(d)["states"] = [{"state": "hormuz", "lo": 2, "hi": 2}]
        self.assertIn("R28", self.mutate(new, c))
        def declared(d):
            new(d)
            self.P(d)["contradicts"] = [{"ledger_id": 22, "nature": "a glut can come from demand loss",
                                         "hedge_reason": "they cannot both pay; #22 has the transit data behind it"}]
        self.assertNotIn("R28", self.mutate(declared, c))
        def compatible(d):
            new(d); self.P(d)["states"] = [{"state": "hormuz", "lo": 1, "hi": 2}]
        self.assertNotIn("R28", self.mutate(compatible, c))

    def test_R37_a_conflict_row_must_read_the_deciders_calendar(self):
        """#72 priced a strike inside no window and #19 priced calm the day after Iran hit vessels: both skipped the question
        'what do the deciders want in this window, and what would end their restraint?'"""
        import datetime as _d
        def new(d, **inc):
            self.iran(d, prob=0.70, row_class="marker", lean="de-escalation")
            self.P(d)["conflict_level"] = {"lo": 0, "hi": 3}
            if inc is not None:
                self.P(d)["incentive"] = inc
        c = ctx(as_of=_d.date(2026, 7, 8))
        self.assertIn("R37", self.mutate(lambda d: (self.iran(d, prob=0.70, row_class="marker", lean="de-escalation"),
                                                    self.P(d).__setitem__("conflict_level", {"lo": 0, "hi": 3})), c))
        calm = dict(act="us_strike_iran", claims="does_not_occur", window="us-mou-jun", trigger="")
        self.assertIn("R37", self.mutate(lambda d: new(d, **calm), c))                       # a trigger fired 7/7
        held = dict(calm, trigger="the MOU window stays in force and the trigger was a shipping attack, not a US-force attack")
        self.assertNotIn("R37", self.mutate(lambda d: new(d, **held), c))
        c2 = ctx(as_of=_d.date(2026, 10, 23))
        strike = dict(act="us_strike_iran", claims="occurs", window="us-pledge-midterms", trigger="")
        def inside(d):
            new(d, **strike); self.P(d).update(prob=0.60, horizon="2026-11-03", lean="escalation")
            self.P(d)["conflict_level"] = {"lo": 3, "hi": 4}
        self.assertIn("R37", self.mutate(inside, c2))

    def test_R28_not_both_sides_in_one_batch(self):
        def f(d):
            p2 = copy.deepcopy(self.P(d))
            self.P(d).update(direction="up")
            p2.update(ref="p2", direction="down", prediction="The target range is raised at the next meeting",
                      falsifier=f"The target range is unchanged or lower on {HZ}")
            d["events"][0]["predictions"].append(p2)
        self.assertIn("R28", self.mutate(f))

    def test_R29_a_spread_between_unequal_legs_is_a_direction_bet(self):
        """#74: XLE 1.25pct/day against USO 3.8pct/day, priced 0.75. Second-worst score in the book."""
        def f(d):
            self.P(d).update(tickers=["XLE", "USO"], row_class="direction", prob=0.75)
        self.assertIn("R29", self.mutate(f))          # no relative_value block at all
        def declared(d):
            f(d)
            self.P(d)["relative_value"] = {"high_vol_ticker": "USO", "low_vol_ticker": "XLE",
                                           "high_vol_daily": 3.8, "low_vol_daily": 1.25}
        self.assertIn("R29", self.mutate(declared))   # 3.0x ratio at 0.75 is still refused
        def capped(d):
            declared(d)
            self.P(d).update(prob=0.55)
            self.P(d)["reference"].update(base_rate=0.55, market_prob=None, market_src="")
        self.assertNotIn("R29", self.mutate(capped))

    def test_R30_every_row_names_who_settles_it(self):
        """#59 was scored against the engine because 'strike-free' was never scoped to a source."""
        self.assertIn("R30", self.mutate(lambda d: self.P(d).pop("resolution_source")))
        self.assertIn("R30", self.mutate(lambda d: self.P(d)["resolution_source"].update(convention="")))

    def test_R31_no_self_downgrade_inside_one_lag_length(self):
        """#76 reversed the correct #32 on two sessions against a 2-3 week pass-through lag."""
        def f(d, data_days):
            self.P(d)["self_downgrade"] = {"ledger_id": 62, "lag_length_days": 18, "data_days": data_days,
                                           "mechanism": "pump prices track crude with a 2-3 week lag"}
        self.assertIn("R31", self.mutate(lambda d: f(d, 2)))
        self.assertNotIn("R31", self.mutate(lambda d: f(d, 21)))

    def test_R32_a_plan_is_not_an_action(self):
        """#72 read a fully-coordinated leaked strike plan as an action forecast."""
        self.assertIn("R32", self.mutate(lambda d: self.P(d).update(
            sensitivity="the committee is reportedly weighing a draft framework before the meeting")))
        def planned(d):
            self.P(d)["planning"] = {"reported_plan": "a drafted policy framework circulated to the board"}
        self.assertIn("R32", self.mutate(planned))    # 0.72 with no execution signal
        def executed(d):
            self.P(d)["planning"] = {"reported_plan": "a drafted policy framework circulated to the board",
                                     "execution_signal": "the framework was adopted and published 2026-09-18"}
        self.assertNotIn("R32", self.mutate(executed))

    def test_R33_a_row_at_the_books_own_base_rate_warns(self):
        """9/20 research: a flat forecast at the book's hit rate would have scored BETTER than the book."""
        doc = schema.parse(good())
        warns = [f.rule for f in schema.check(doc, ctx(), ledger.lint) if f.severity == "warning"]
        self.assertIn("R33", warns)                   # the repo's own canonical row is non-informative
        def informative(d):
            self.P(d).update(prob=0.55)
            self.P(d)["reference"].update(market_prob=None, market_src="", base_rate=0.75,
                                          divergence_reason="three hike dissents on the record at the 2026-09-16 meeting")
        d = good(); informative(d)
        warns2 = [f.rule for f in schema.check(schema.parse(d), ctx(), ledger.lint) if f.severity == "warning"]
        self.assertNotIn("R33", warns2)

    def test_R34_one_bet_may_not_be_logged_twice(self):
        """#70 (SMH<SPY) and #27 (SMH<XLE) were one semis bet, and they tracked MISS together."""
        c = ctx(open_rows={70: schema.OpenRow(70, "SMH underperforms SPY", 0.58, "down",
                                              ("TLT",), "market-regime", HZ)},
                open_ledger_ids={11, 62, 70})
        down = lambda d: self.P(d).update(direction="down")
        self.assertIn("R34", self.mutate(down, c))
        def argued(d):
            down(d)
            self.P(d)["independence"] = [{"ledger_id": 70,
                                          "argument": "different mechanism and a different falsifier: #70 is a relative equity call, this is a rate-path call"}]
        self.assertNotIn("R34", self.mutate(argued, c))

    def test_R35_one_meeting_is_a_subset_of_its_window(self):
        """#26 priced a six-month window with one-meeting reasoning and scored 0.64."""
        self.assertIn("R35", self.mutate(lambda d: self.P(d).pop("meeting")))
        self.assertIn("R35", self.mutate(lambda d: self.P(d)["meeting"].update(window_prob=0.60)))
        self.assertNotIn("R35", self.mutate(lambda d: self.P(d)["meeting"].update(window_prob=0.90)))

    def test_R36_a_conjunction_cannot_beat_its_weakest_leg(self):
        """#63 needed a strike AND a framework announcement, and was priced above either leg alone."""
        def f(d, prob):
            self.P(d).update(prob=prob)
            self.P(d)["conjunction"] = {"legs": ["US strikes Houthi targets in Yemen",
                                                 "a formal Red Sea escort framework is announced"],
                                        "leg_probs": [0.55, 0.40]}
            self.P(d)["reference"].update(base_rate=prob, market_prob=None, market_src="")
            self.P(d)["meeting"].update(window_prob=0.95)
        self.assertIn("R36", self.mutate(lambda d: f(d, 0.75)))
        self.assertNotIn("R36", self.mutate(lambda d: f(d, 0.38)))

    def test_R36_rewording_a_compound_does_not_fix_its_price(self):
        """R09 bans the wording. R36 makes you price it. Fixing only the wording was always the dodge."""
        found = self.mutate(lambda d: self.P(d).update(
            prediction="The FOMC holds AND the 2y yield falls below 4 percent by the meeting"))
        self.assertIn("R09", found)
        self.assertIn("R36", found)

    def test_every_rule_is_documented(self):
        self.assertEqual(sorted(schema.RULES), [f"R{i:02d}" for i in range(1, 38)])


if __name__ == "__main__":
    unittest.main()
