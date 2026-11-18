#!/usr/bin/env python3
"""Rule-by-rule tests for the enforced trading ruleset.  python -m unittest tests.test_trade_rules -v

One known-good OPEN trade and one known-good CLOSED trade, then at least one PASS and one FAIL
per rule: each FAIL must produce exactly the rule id it targets. If a rule is ever loosened by
accident, the matching test goes red.

The last class replays the three real rows in `trades` (RTX #1, MU #2) plus the synthetic XLE/USO
pair from #74 as regression fixtures. Price bars are supplied as DATA - this suite never fetches
a price, and neither does the module under test."""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "pipeline"))
import trade_rules as tr  # noqa: E402


# ── the known-good trade + the world it lives in ─────────────────────────────
def trade(**over):
    base = dict(
        id=9, pred_id=44, ticker="RTX", direction="long",
        entry_price=195.42, entry_ts="2026-07-14T18:16Z", target=210.0, invalidation=188.0,
        status="open",
        note="single best swing; branch-robust defense prime; pre-registered entry 192-196, "
             "target 210, invalidation close <188")
    base.update(over)
    return tr.Trade(**base)


def closed(**over):
    base = dict(
        exit_price=210.0, exit_ts="2026-07-27T20:00Z", exit_reason="target", status="closed",
        pct=tr.derive_pct("long", 195.42, 210.0))
    base.update(over)
    return trade(**base)


def ctx(**over):
    base = dict(
        predictions={
            44: tr.LedgerRow(44, "up", "open", "defense-swing", 0.60),
            33: tr.LedgerRow(33, "down", "resolved", "memory-cycle", 0.62),
            27: tr.LedgerRow(27, "down", "open", "iran-war", 0.35),
            74: tr.LedgerRow(74, "up", "resolved", "oil-tape", 0.75),
            11: tr.LedgerRow(11, "up", "void", "iran-war", 0.55)},
        open_by_cluster={"defense-swing": 3, "iran-war": 10, "memory-cycle": 1},
        open_total=28,
        # tape that never touches the 210 target nor the 188 invalidation
        prices={"RTX": [("2026-07-15", 198.0, 193.0), ("2026-07-16", 201.0, 196.0),
                        ("2026-07-17", 205.0, 199.0)]},
        last_price={"RTX": 205.0},
        branch_p={44: 0.55},
        asof="2026-07-20")
    base.update(over)
    return tr.TradeContext(**base)


def closed_ctx(**over):
    """The same world, with a session on the exit date that could actually have filled 210."""
    over.setdefault("prices", {"RTX": [("2026-07-27", 211.0, 205.0)]})
    return ctx(**over)


def rules(t, c=None):
    return [f.rule for f in tr.check_trade(t, c or ctx()) if f.severity == "error"]


def warnings(t, c=None):
    return [f.rule for f in tr.check_trade(t, c or ctx()) if f.severity == "warning"]


class Structure(unittest.TestCase):
    def test_the_good_open_trade_is_clean(self):
        self.assertEqual(rules(trade()), [])
        self.assertEqual(warnings(trade()), [])

    def test_the_good_closed_trade_is_clean(self):
        self.assertEqual(rules(closed(), closed_ctx()), [])
        self.assertEqual(warnings(closed(), closed_ctx()), [])

    def test_rule_ids_are_contiguous_and_described(self):
        self.assertEqual(list(tr.TRADE_RULES), [f"T{i:02d}" for i in range(1, 15)])
        for rid, text in tr.TRADE_RULES.items():
            self.assertTrue(text.strip(), rid)

    def test_every_emitted_rule_id_is_a_declared_rule(self):
        seen = set()
        for t, c in ((trade(pred_id=None), ctx()),
                     (trade(target="a close above the highs"), ctx()),
                     (closed(exit_reason="manual"), closed_ctx())):
            seen |= {f.rule for f in tr.check_trade(t, c)}
        self.assertTrue(seen <= set(tr.TRADE_RULES), seen - set(tr.TRADE_RULES))

    def test_the_module_imports_nothing_from_the_repo(self):
        src = (pathlib.Path(tr.__file__)).read_text(encoding="utf-8")
        for repo_mod in ("ledger", "schema", "common", "dashboard", "analyst", "jev"):
            self.assertNotIn(f"import {repo_mod}", src)


class Rules(unittest.TestCase):
    # ── T01 ──────────────────────────────────────────────────────────────────
    def test_T01_pass_direction_agrees_with_the_parent_row(self):
        self.assertNotIn("T01", rules(trade()))

    def test_T01_fail_orphan_trade(self):
        self.assertIn("T01", rules(trade(pred_id=None)))

    def test_T01_fail_prediction_does_not_exist(self):
        self.assertIn("T01", rules(trade(pred_id=999)))

    def test_T01_fail_direction_disagrees(self):
        # #44 is stated 'up'; a short is the opposite bet wearing the same reference
        self.assertIn("T01", rules(trade(direction="short")))

    def test_T01_fail_parent_is_void(self):
        self.assertIn("T01", rules(trade(pred_id=11)))

    # ── T02 ──────────────────────────────────────────────────────────────────
    def test_T02_pass_stored_values_unchanged(self):
        c = ctx(stored={9: trade()})
        self.assertNotIn("T02", rules(trade(), c))

    def test_T02_fail_level_missing_at_open(self):
        self.assertIn("T02", rules(trade(target=None)))

    def test_T02_fail_target_edited_after_entry(self):
        c = ctx(stored={9: trade()})
        self.assertIn("T02", rules(trade(target=230.0), c))

    def test_T02_fail_entry_redated(self):
        c = ctx(stored={9: trade()})
        self.assertIn("T02", rules(trade(entry_ts="2026-07-20T14:00Z"), c))

    # ── T03 ──────────────────────────────────────────────────────────────────
    def test_T03_pass_price_on_the_losing_side(self):
        self.assertNotIn("T03", rules(trade()))

    def test_T03_fail_narrative_invalidation(self):
        self.assertIn("T03", rules(trade(invalidation="if the defense thesis breaks")))

    def test_T03_fail_invalidation_on_the_winning_side(self):
        self.assertIn("T03", rules(trade(invalidation=215.0)))

    def test_T03_fail_short_ordering(self):
        t = trade(pred_id=33, ticker="MU", direction="short", entry_price=937.0,
                  target=1035.0, invalidation=800.0)
        self.assertIn("T03", rules(t, ctx(prices={})))

    # ── T04 ──────────────────────────────────────────────────────────────────
    def test_T04_pass_two_to_one(self):
        self.assertNotIn("T04", rules(trade()))

    def test_T04_fail_below_one_and_a_half(self):
        self.assertIn("T04", rules(trade(target=200.0)))

    def test_T04_warns_on_a_fantasy_target(self):
        t = trade(target=400.0)
        self.assertEqual(rules(t), [])
        self.assertIn("T04", warnings(t))

    # ── T05 ──────────────────────────────────────────────────────────────────
    def test_T05_pass_small_cluster_no_duplicate(self):
        self.assertNotIn("T05", rules(trade()))

    def test_T05_fail_cluster_over_the_concentration_cap(self):
        # iran-war holds 10 of 28 open rows = 36pct
        t = trade(pred_id=27, ticker="SMH", direction="short", entry_price=550.0,
                  target=470.0, invalidation=595.0)
        self.assertEqual(rules(t, ctx(prices={})), ["T05"])

    def test_T05_fail_same_ticker_and_direction_already_open(self):
        c = ctx(open_trades=(trade(id=5),))
        self.assertIn("T05", rules(trade(), c))

    # ── T06 ──────────────────────────────────────────────────────────────────
    def test_T06_pass_two_legs_of_comparable_vol(self):
        t = trade(ticker="XLE/XOP", entry_price=1.00, target=1.08, invalidation=0.96,
                  leg_vol={"XLE": 1.25, "XOP": 1.60})
        self.assertEqual(rules(t), [])

    def test_T06_fail_vol_not_declared(self):
        t = trade(ticker="XLE/USO", entry_price=1.00, target=1.08, invalidation=0.96)
        self.assertIn("T06", rules(t))

    def test_T06_fail_three_vol_against_one_vol_is_a_direction_bet(self):
        t = trade(pred_id=74, ticker="XLE/USO", entry_price=1.00, target=1.08,
                  invalidation=0.96, leg_vol={"XLE": 1.25, "USO": 3.8})
        got = tr.check_trade(t, ctx())
        self.assertEqual([f.rule for f in got], ["T06", "T06"])
        self.assertIn("USO", str(got[0]))               # names the high-vol leg
        self.assertIn("0.55", str(got[1]))              # and applies the direction cap

    # ── T07 ──────────────────────────────────────────────────────────────────
    def test_T07_pass_direction_and_mechanism_only(self):
        self.assertNotIn("T07", rules(trade()))

    def test_T07_fail_sizing_language_in_the_note(self):
        t = trade(note="branch-robust defense prime; position size 3% of the portfolio")
        self.assertIn("T07", rules(t))

    def test_T07_fail_share_count_in_the_note(self):
        self.assertIn("T07", rules(trade(note="branch-robust; buy 200 shares on the open")))

    # ── T08 ──────────────────────────────────────────────────────────────────
    def test_T08_pass_target_never_touched(self):
        self.assertNotIn("T08", rules(trade()))

    def test_T08_fail_long_target_touched_and_still_open(self):
        c = ctx(prices={"RTX": [("2026-07-16", 211.0, 199.0)]})
        self.assertEqual(rules(trade(), c), ["T08"])

    def test_T08_ignores_bars_before_the_entry(self):
        c = ctx(prices={"RTX": [("2026-07-01", 240.0, 230.0)]})
        self.assertEqual(rules(trade(), c), [])

    def test_T08_ignores_bars_after_the_asof_date(self):
        c = ctx(prices={"RTX": [("2026-08-01", 240.0, 230.0)]})
        self.assertEqual(rules(trade(), c), [])

    def test_T08_does_not_fire_on_a_closed_trade(self):
        c = closed_ctx(prices={"RTX": [("2026-07-27", 218.0, 205.0)]})
        self.assertNotIn("T08", rules(closed(), c))

    # ── T09 ──────────────────────────────────────────────────────────────────
    def test_T09_pass_booked_at_the_pre_registered_target(self):
        self.assertNotIn("T09", rules(closed(), closed_ctx()))

    def test_T09_fail_booked_at_the_hindsight_extreme(self):
        c = closed_ctx(prices={"RTX": [("2026-07-27", 219.0, 208.0)]})
        t = closed(exit_price=218.0, pct=tr.derive_pct("long", 195.42, 218.0))
        self.assertEqual(rules(t, c), ["T09"])

    def test_T09_warns_when_the_fill_slipped_the_other_way(self):
        c = closed_ctx(prices={"RTX": [("2026-07-27", 211.0, 205.0)]})
        t = closed(exit_price=209.0, pct=tr.derive_pct("long", 195.42, 209.0))
        self.assertEqual(rules(t, c), [])
        self.assertIn("T09", warnings(t, c))

    # ── T10 ──────────────────────────────────────────────────────────────────
    def test_T10_pass_no_prior_position(self):
        self.assertNotIn("T10", rules(trade()))

    def test_T10_pass_prior_position_is_in_profit(self):
        c = ctx(open_trades=(trade(id=5, entry_price=190.0),), last_price={"RTX": 205.0})
        self.assertNotIn("T10", rules(trade(), c))

    def test_T10_fail_adding_to_an_underwater_position(self):
        c = ctx(open_trades=(trade(id=5, entry_price=200.0),), last_price={"RTX": 190.0})
        self.assertIn("T10", rules(trade(), c))

    # ── T11 ──────────────────────────────────────────────────────────────────
    def test_T11_pass_closed_vocabulary_and_matching_arithmetic(self):
        self.assertNotIn("T11", rules(closed(), closed_ctx()))

    def test_T11_fail_exit_reason_outside_the_vocabulary(self):
        # ledger.py's own trade-close help still advertises "manual" - it is not a reason
        self.assertIn("T11", rules(closed(exit_reason="manual"), closed_ctx()))

    def test_T11_fail_pct_does_not_re_derive(self):
        self.assertEqual(rules(closed(pct=12.0), closed_ctx()), ["T11"])

    def test_T11_fail_no_note(self):
        self.assertIn("T11", rules(closed(note=""), closed_ctx()))

    def test_T11_fail_status_outside_the_vocabulary(self):
        self.assertIn("T11", rules(trade(status="pending")))

    def test_T01_fail_direction_outside_the_vocabulary(self):
        self.assertIn("T01", rules(trade(direction="flat")))

    def test_T11_short_arithmetic_is_the_mirror(self):
        self.assertAlmostEqual(tr.derive_pct("short", 937.0, 800.0), 14.621131270010673)

    # ── T12 ──────────────────────────────────────────────────────────────────
    def test_T12_pass_modal_branch(self):
        self.assertEqual(warnings(trade()), [])

    def test_T12_warns_on_a_tail_branch_but_accepts_a_robust_note(self):
        c = ctx(branch_p={44: 0.20})
        self.assertEqual(rules(trade(), c), [])
        self.assertIn("T12", warnings(trade(), c))

    def test_T12_fail_tail_branch_with_no_robustness_statement(self):
        c = ctx(branch_p={44: 0.20})
        t = trade(note="long RTX into the Iran round-3 escalation")
        self.assertEqual(rules(t, c), ["T12"])

    # ── T13 ──────────────────────────────────────────────────────────────────
    def test_T13_pass_invalidation_never_touched(self):
        self.assertNotIn("T13", rules(trade()))

    def test_T13_fail_long_invalidation_touched_and_still_open(self):
        c = ctx(prices={"RTX": [("2026-07-16", 196.0, 187.0)]})
        self.assertEqual(rules(trade(), c), ["T13"])

    # ── T14 ──────────────────────────────────────────────────────────────────
    def test_T14_pass_the_fill_is_inside_that_sessions_range(self):
        self.assertNotIn("T14", rules(closed(), closed_ctx()))

    def test_T14_fail_exit_before_entry(self):
        c = closed_ctx(prices={"RTX": [("2026-07-13", 211.0, 205.0)]})
        self.assertIn("T14", rules(closed(exit_ts="2026-07-13T20:00Z"), c))

    def test_T14_fail_a_fill_that_never_traded(self):
        c = closed_ctx(prices={"RTX": [("2026-07-27", 205.0, 200.0)]})
        self.assertEqual(rules(closed(), c), ["T14"])

    def test_T14_fail_exit_dated_to_a_session_that_is_not_on_the_tape(self):
        c = closed_ctx(prices={"RTX": [("2026-07-27", 211.0, 205.0)]})
        self.assertIn("T14", rules(closed(exit_ts="2026-07-26T20:00Z"), c))


class RealTrades(unittest.TestCase):
    """The book's actual round-trips, replayed. These are the rows the rules were written from."""

    # RTX #1: the branch-robust swing, the one trade nothing is wrong with
    RTX = tr.Trade(
        id=1, pred_id=44, ticker="RTX", direction="long", entry_price=195.42,
        entry_ts="2026-07-14T18:16Z", target=210.0, invalidation=188.0,
        exit_price=210.0, exit_ts="2026-07-27T20:00Z", exit_reason="target", status="closed",
        pct=7.460853546208174,
        note="single best swing; branch-robust defense prime; pre-registered entry 192-196, "
             "target 210, invalidation close <188")

    # MU #2: short 937 -> 800. The 800 target was TOUCHED on 7/28 (open 839.61, low 789.09) and the
    # row sat open until 9/19 - during which MU printed 1042.40 on 9/9, through the 1035 invalidation.
    MU_NOTE = ("cyclical-peak short; target <800, invalidation reclaim/hold 1035 | BOOKED 2026-09-19 "
               "(late): pre-registered 800 target was touched 7/28 - exit recorded AT the target per "
               "process lesson 4, not at the 737.88 hindsight low.")
    MU_BARS = [("2026-07-28", 839.61, 789.09),      # only the open and the low are on the record;
               ("2026-09-09", 1042.40, 1000.00)]    # the high is floored at the open, conservatively

    def rtx_ctx(self, **over):
        over.setdefault("predictions", {44: tr.LedgerRow(44, "up", "resolved", "defense-swing", 0.60)})
        over.setdefault("prices", {"RTX": [("2026-07-27", 218.0, 205.0)]})
        over.setdefault("branch_p", {44: 0.55})
        return tr.TradeContext(open_total=28, **over)

    def mu_ctx(self, **over):
        over.setdefault("predictions", {33: tr.LedgerRow(33, "down", "resolved", "memory-cycle", 0.62)})
        over.setdefault("prices", {"MU": self.MU_BARS})
        return tr.TradeContext(open_by_cluster={"memory-cycle": 1}, open_total=28,
                               asof="2026-09-19", **over)

    def test_rtx_the_good_trade_passes_every_rule(self):
        self.assertEqual([f.rule for f in tr.check_trade(self.RTX, self.rtx_ctx())], [])

    def test_mu_as_it_sat_open_on_9_18_is_refused_by_both_stale_gates(self):
        mu_open = tr.Trade(id=2, pred_id=33, ticker="MU", direction="short", entry_price=937.0,
                           entry_ts="2026-07-13T21:09Z", target=800.0, invalidation=1035.0,
                           status="open", note=self.MU_NOTE)
        got = rules(mu_open, self.mu_ctx())
        self.assertIn("T08", got)   # the seven-week defect
        self.assertIn("T13", got)   # and the invalidation pierced while it read "open"
        self.assertIn("T04", got)   # see below - the trade never met the 1.5 floor either

    def test_mu_as_booked_on_9_19_is_clean_except_for_reward_risk(self):
        mu = tr.Trade(id=2, pred_id=33, ticker="MU", direction="short", entry_price=937.0,
                      entry_ts="2026-07-13T21:09Z", target=800.0, invalidation=1035.0,
                      exit_price=800.0, exit_ts="2026-07-28T20:00Z", exit_reason="target",
                      status="closed", pct=14.621131270010673, note=self.MU_NOTE)
        # T09 and T14 both pass: booked AT the 800 target, dated to the session that could fill it.
        self.assertEqual(rules(mu, self.mu_ctx()), ["T04"])

    def test_mu_reward_risk_is_the_repo_contradiction(self):
        # 137 points of reward against 98 of risk = 1.40, below the 1.5 floor T04 enforces.
        rr = tr.reward_risk(937.0, 800.0, 1035.0)
        assert rr is not None
        self.assertAlmostEqual(rr, 137.0 / 98.0, places=6)
        self.assertLess(rr, tr.MIN_REWARD_RISK)

    def test_mu_booked_at_the_hindsight_low_would_have_been_refused(self):
        mu = tr.Trade(id=2, pred_id=33, ticker="MU", direction="short", entry_price=937.0,
                      entry_ts="2026-07-13T21:09Z", target=800.0, invalidation=1035.0,
                      exit_price=737.88, exit_ts="2026-07-28T20:00Z", exit_reason="target",
                      status="closed", pct=tr.derive_pct("short", 937.0, 737.88),
                      note=self.MU_NOTE)
        got = rules(mu, self.mu_ctx())
        self.assertIn("T09", got)   # better than the pre-registered target
        self.assertIn("T14", got)   # and 737.88 is outside the 7/28 range anyway

    def test_xle_uso_relative_value_pair_is_rejected(self):
        # #74: XLE 1.25%/day against USO 3.8%/day. A 3-vol leg against a 1-vol leg is a levered
        # direction call on crude (doctrine 13h) - second-worst score in the book.
        rv = tr.Trade(id=99, pred_id=74, ticker="XLE/USO", direction="long", entry_price=1.00,
                      entry_ts="2026-08-04T20:00Z", target=1.08, invalidation=0.96,
                      note="war-premium unwind, not a demand event; refining margins expand",
                      leg_vol={"XLE": 1.25, "USO": 3.8})
        c = tr.TradeContext(predictions={74: tr.LedgerRow(74, "up", "resolved", "oil-tape", 0.75)},
                            open_total=28, asof="2026-08-11")
        got = tr.check_trade(rv, c)
        self.assertEqual([f.rule for f in got], ["T06", "T06"])
        self.assertIn("levered direction bet on USO", str(got[0]))

    def test_xle_uso_without_declared_vol_is_also_rejected(self):
        rv = tr.Trade(id=99, pred_id=74, ticker="XLE/USO", direction="long", entry_price=1.00,
                      entry_ts="2026-08-04T20:00Z", target=1.08, invalidation=0.96,
                      note="war-premium unwind")
        c = tr.TradeContext(predictions={74: tr.LedgerRow(74, "up", "resolved", "oil-tape", 0.75)},
                            open_total=28, asof="2026-08-11")
        self.assertEqual([f.rule for f in tr.check_trade(rv, c)], ["T06"])


if __name__ == "__main__":
    unittest.main()
