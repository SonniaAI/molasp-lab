"""Pins for the w8 ladder stage-2 conditional power plan (SON-5148).

The plan (research-log/2026-10-13-w8-ladder-stage2-power-plan.md) is
pre-registered BEFORE the posfresh datum exists. These pins freeze:

- the plan file itself and its branch->design mapping literals;
- the corrected-record constants it inherits (1524 target, R3 window);
- the dual-null band arithmetic recomputed from the tick-115 q0 module
  constants (q0 - DELTA_DESC*(1-w) at w=1/2 must equal the committed
  w=1/2 decline-scenario rate 0.7060359...);
- the second-order power-shift bound (0.7377 - 0.6901 <= 0.048).

Doc-only pins plus arithmetic; no simulation, no seeds.
"""

import math
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "research-log" / "2026-10-13-w8-ladder-stage2-power-plan.md"

import sys  # noqa: E402

sys.path.insert(0, str(ROOT))

from tools.w8_q0_sensitivity import DELTA_DESC, Q0  # noqa: E402


class TestLadderStage2Plan(unittest.TestCase):
    def setUp(self):
        self.assertTrue(PLAN.exists(), "plan note must exist")
        self.text = PLAN.read_text()

    def test_plan_exists_with_branch_mapping(self):
        for literal in (
            "POSITION_DECLINE_NOT_DETECTED",
            "POSITION_DECLINE_DETECTED",
            "Branch A",
            "Branch B",
        ):
            self.assertIn(literal, self.text)

    def test_branches_are_pre_registered_before_datum(self):
        self.assertIn("still QUEUED", self.text)
        self.assertIn("frozen BEFORE", self.text)
        # neither branch activates on instrument failure
        self.assertIn("NEITHER branch activates", self.text)

    def test_branch_a_inherits_corrected_policy_constants(self):
        self.assertIn("1524", self.text)
        self.assertIn("[1123, 1162]", self.text)
        # stage-3 no-auto-stage-4 rule is restated verbatim in spirit
        self.assertIn("Never an automatic stage 4", self.text)

    def test_dual_null_band_edge_matches_q0_module(self):
        # w = 1/2 band lower edge must equal the committed w=1/2 decline rate
        edge = Q0 - DELTA_DESC * (1 - 0.5)
        self.assertAlmostEqual(edge, 0.7060359, places=6)
        # and the plan quotes the band formula and the same edge
        self.assertIn("[q0 − Δ(1−w), q0]", self.text)
        self.assertIn("0.7060", self.text)

    def test_second_order_power_shift_bound(self):
        shift = 0.7377 - 0.6901
        self.assertLessEqual(shift, 0.048)
        self.assertIn("≤ 0.048", self.text)

    def test_branch_b_retires_pooled_q0(self):
        self.assertIn("(q_early, q_late)", self.text)
        self.assertIn("RETIRED", self.text)
        # stratified MDE scaling rule is named
        self.assertIn("(0.040/Δ_meas)²", self.text)

    def test_pause_is_not_lifted_by_this_note(self):
        self.assertIn("does not resume the ladder", self.text)
        self.assertIn("PAUSED", self.text)


if __name__ == "__main__":
    unittest.main()
