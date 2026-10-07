"""d4 stack-class pins (tick 34, SON-4778) — the designs/004 tick-33
refinement: the emit-time census must report the two cooperative
classes the history-aware recombination study measured, because the
one-site census (hazards, pair channels) cannot see either of them.

Measured on BUILD1 row scope (recombination.out, job
hxq-e38ad7f3d5f377b9, pre-registered at 3fa1b4a):

- the read-block (0.141 of terminals) rides the VERTICAL lock stack
  Vp@(3,2) + DBr@(3,3) — 141/141 co-occurrence with the blocked
  cohort; west D2T co-stacks but is not load-bearing (H3);
- the surviving repair channel (0.155 stable fill, 98.71% at b=3) is
  a 2-of-3 REDUNDANT relay stack D2T@(2,2) N->DAr + S->V0p + W->S2,
  with no single load-bearing partner (lb_any 0.0129, H1) — E->L2
  appears in zero row-scope holds.

Static pins: the row-scope census enumerates the Vp+DBr vertical
stack as cooperative-only (both solo bonds 0 — invisible to the
one-site census) and the D2T@(2,2) relay fan with the canonical
S->V0p contact plus the N->DAr / W->S2 squatter relays and solo
total bond 1 (E->L2 dead under row scope); the family-scope census
sees the same filler stable-by-arithmetic (solo 2: E->L2 + S->V0p).
"""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EV_AND = os.path.join(ROOT, "evidence", "2026-10-06-body-conjunction-builds")
EV_REC = os.path.join(ROOT, "evidence", "2026-10-07-recombination")
for p in (EV_AND,):
    if p not in sys.path:
        sys.path.insert(0, p)

from molasp.offchannel import (  # noqa: E402
    apply_lock_glue_scope, check_d4, d4_report_lines)
from tiles_and import BUILD1  # noqa: E402


def receipt_arms():
    arms = {}
    with open(os.path.join(EV_REC, "recombination.out")) as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if isinstance(rec, dict) and "system" in rec and "key" in rec:
                arms[rec["key"]] = rec
    if not arms:
        raise unittest.SkipTest("recombination receipt not present")
    return arms


class VerticalLockStackPins(unittest.TestCase):

    def test_row_scope_vp_dbr_stack_is_cooperative_only(self):
        """The measured read-block channel is enumerated by the
        two-site census and is invisible to the one-site census."""
        rep = check_d4(apply_lock_glue_scope(BUILD1, "row"))
        chan = rep["lock_stack_channels"]["3,2|3,3"]["Vp+DBr"]
        self.assertEqual(chan["b_mutual_vertical"], 1)
        self.assertEqual(chan["b_lower_solo"], 0)   # Vp@(3,2) solo dead
        self.assertEqual(chan["b_upper_solo"], 0)   # DBr@(3,3) solo dead
        self.assertGreaterEqual(chan["b_lower_in_stack"], 1)
        self.assertGreaterEqual(chan["b_upper_in_stack"], 1)
        # and the one-site census sees nothing here under row scope
        self.assertNotIn("3,2", rep["lock_hazards"])
        self.assertNotIn("3,3", rep["lock_hazards"])

    def test_family_scope_same_pair_not_cooperative_only(self):
        """Under family scope Vp@(3,2) has a solo b=1 hold (the
        transient layer), so the same stack is not cooperative-only
        there — the class is a property of the scope, not the names."""
        rep = check_d4(apply_lock_glue_scope(BUILD1, "family"))
        chan = rep["lock_stack_channels"]["3,2|3,3"]["Vp+DBr"]
        self.assertEqual(chan["b_mutual_vertical"], 1)
        self.assertEqual(chan["b_lower_solo"], 1)
        self.assertEqual(chan["b_upper_solo"], 0)

    def test_measured_read_block_is_this_class(self):
        """recombination.out H3: row read-block 0.141, with the
        lock-squat counts of the blocked cohort exactly the Vp@(3,2)
        + DBr@(3,3) pair (141/141 co-occurrence)."""
        arm = receipt_arms()["row_build1"]
        self.assertAlmostEqual(arm["blocked_frac"], 0.141, places=3)
        squats = arm["lock_squats"]
        self.assertEqual(squats, {"3,2:Vp": 141, "3,3:DBr": 141})
        self.assertEqual(arm["mutual_pair_link_frac"], 0.0)
        ctx = check_d4(apply_lock_glue_scope(BUILD1, "row"))[
            "measured_context"]["row_scope_kinetics"]
        self.assertEqual(ctx["vertical_stack_read_block_dG0.5"],
                         arm["blocked_frac"])


class VacancyRelayStackPins(unittest.TestCase):

    def test_row_scope_d2t_relay_fan_matches_measured_partners(self):
        """The measured 2-of-3 relay stack (N->DAr + S->V0p + W->S2)
        is enumerated as D2T's fan at the vacancy site (2,2), with
        solo total bond 1 — E->L2 is dead under row scope."""
        rep = check_d4(apply_lock_glue_scope(BUILD1, "row"))
        fan = rep["vacancy_relay_stacks"]["2,2"]["D2T"]
        self.assertEqual(fan["contacts"]["S"]["canonical"], "V0p")
        self.assertIn("DAr", fan["contacts"]["N"]["squatter_relays"])
        self.assertIn("S2", fan["contacts"]["W"]["squatter_relays"])
        self.assertGreaterEqual(fan["n_relay_contacts"], 3)
        self.assertEqual(fan["solo_total_bond"], 1)

    def test_family_scope_same_filler_stable_by_arithmetic(self):
        """Family scope: D2T@(2,2) holds at solo bond 2 (E->L2 +
        S->V0p, the classic b=2 canonical fill — 711/886 measured
        family holds) — not a cooperative-only channel."""
        rep = check_d4(apply_lock_glue_scope(BUILD1, "family"))
        fan = rep["vacancy_relay_stacks"]["2,2"]["D2T"]
        self.assertEqual(fan["solo_total_bond"], 2)
        self.assertEqual(fan["contacts"]["E"]["canonical"], "L2")
        self.assertEqual(fan["contacts"]["S"]["canonical"], "V0p")

    def test_measured_relay_numbers_quoted_in_context(self):
        """recombination.out H1/H4: row_Vp stable fill 0.155 at
        b_ge3_frac 0.9871, lb_any 0.0129 — quoted in the report so
        no single-partner severity is read off the static fan."""
        arm = receipt_arms()["row_Vp"]
        self.assertAlmostEqual(
            arm["d2t22_stable_fill_all"], 0.155, places=3)
        coh = arm["stable_cohort"]
        self.assertAlmostEqual(coh["b_ge3_frac"], 0.9871, places=4)
        self.assertAlmostEqual(coh["lb_any_frac"], 0.0129, places=4)
        # E->L2 in zero row holds (the receipt's partner table)
        self.assertNotIn("E@3,2:L2:1", coh["all_partners"])
        ctx = check_d4(apply_lock_glue_scope(BUILD1, "row"))[
            "measured_context"]["row_scope_kinetics"]
        self.assertEqual(ctx["relay_stack_stable_fill_dG0.5"],
                         arm["d2t22_stable_fill_all"])
        self.assertEqual(ctx["relay_stack_b3_frac"], coh["b_ge3_frac"])
        self.assertEqual(ctx["relay_stack_lb_any_frac"],
                         coh["lb_any_frac"])


class ReportLinesPins(unittest.TestCase):

    def test_cooperative_classes_appear_in_warning_block(self):
        lines = "\n".join(d4_report_lines(
            check_d4(apply_lock_glue_scope(BUILD1, "row"))))
        self.assertIn("vertical lock stack: Vp+DBr at 3,2|3,3", lines)
        self.assertIn("cooperative-only", lines)
        self.assertIn("vacancy relay stack: D2T at 2,2", lines)
        self.assertIn("Redundant fan", lines)


if __name__ == "__main__":
    unittest.main()
