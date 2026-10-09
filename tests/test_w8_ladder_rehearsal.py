"""Pins for the tick-95 w8 LADDER rehearsal (tools/w8_ladder_rehearsal.py).

Every expectation here was committed BEFORE the real w8 datum exists; the
rehearsal drills the census-policy growth ladder on synthetic first-arm
censuses at pre-named truths. Numbers pinned from live measured output of
the real policy() (measure-then-pin); tick-92 receipt identities are the
drift guard for the ladder against its own landed record.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.w8_census_policy import policy  # noqa: E402
from tools.w8_ladder_rehearsal import (  # noqa: E402
    EXPECT_MODE,
    MIN_EVENTS_FLOOR,
    RECEIPT_PRIMARY,
    check,
    rehearse,
    render,
)

import tools.w8_census_policy as policy_mod  # noqa: E402


class TestLadderRehearsalModes(unittest.TestCase):
    """The mechanical stage naming at each pre-named truth."""

    @classmethod
    def setUpClass(cls):
        cls.rows = {r["truth"]: r for r in rehearse()}

    def test_all_truths_match_committed_expectations(self):
        for truth, want in EXPECT_MODE.items():
            self.assertEqual(
                self.rows[truth]["mode"], want,
                "%s: ladder mode drifted from the committed expectation" % truth)

    def test_check_passes_on_live_rehearsal(self):
        self.assertEqual(check(rehearse()), [])

    def test_render_carries_authority_disclaimer(self):
        text = render(rehearse())
        self.assertIn("Verdict authority stays with collect_w8", text)
        self.assertIn("never stage 4", text)


class TestLadderRehearsalReceiptIdentities(unittest.TestCase):
    """The ladder reproduces the committed tick-91/92 record."""

    def test_primary_reproduces_tick92_receipt(self):
        g = policy(417, 500)["growth"]
        self.assertEqual(g["k_line_prac"], RECEIPT_PRIMARY["k_line_prac"])
        self.assertEqual(g["k_line_prac"], 1442)
        self.assertEqual(g["region"], "R2")
        self.assertEqual(g["window"], (1203, 1250))
        self.assertEqual(g["line_x_at_k"], 1203)
        self.assertEqual(g["total_arms"], RECEIPT_PRIMARY["total_arms"])
        self.assertEqual(g["total_arms"], 3)
        self.assertEqual(g["additional_arms"], RECEIPT_PRIMARY["additional_arms"])
        self.assertEqual(g["additional_arms"], 2)
        self.assertAlmostEqual(
            g["growth_wall_hours"], RECEIPT_PRIMARY["growth_wall_hours"], places=2)

    def test_trend_arm_ladder_answer_is_the_first_window_k(self):
        # New number recorded at the rehearsal's first run: the policy scans
        # for the first k whose >=3-count practical window contains the
        # point-estimate line — 1634 (4 arms), NOT the tick-91 planner's R3
        # regional minimum 653. Different pre-registered questions; both
        # receipts stand.
        g = policy(382, 500)["growth"]
        self.assertEqual(g["k_line_prac"], 1634)
        self.assertEqual(g["region"], "R3")
        self.assertEqual(g["total_arms"], 4)
        self.assertEqual(g["additional_arms"], 3)
        self.assertAlmostEqual(g["growth_wall_hours"], 2.00, places=2)

    def test_destructive_verdicts_need_no_growth(self):
        for x1, region in ((325, "R4"), (475, "R5")):
            d = policy(x1, 500)
            self.assertEqual(d["mode"], "verdict_ready")
            self.assertIsNone(d["growth"])
            self.assertEqual(d["regions"], [region])


class TestLadderRehearsalContracts(unittest.TestCase):
    """Refusal paths and authority fences."""

    def test_k1_below_floor_refuses(self):
        with self.assertRaises(ValueError):
            policy(5, MIN_EVENTS_FLOOR - 1)

    def test_x_out_of_range_refuses(self):
        with self.assertRaises(ValueError):
            policy(501, 500)
        with self.assertRaises(ValueError):
            policy(-1, 500)

    def test_rehearsal_never_imports_the_frozen_collector(self):
        src = Path("tools/w8_ladder_rehearsal.py").read_text()
        self.assertNotIn("from tools.collect_w8", src)
        self.assertNotIn("import collect_w8", src)

    def test_policy_module_untouched_by_rehearsal(self):
        # The rehearsal imports policy/collection_report only; the frozen
        # gate module (collect_w8) is not part of this chain at all.
        self.assertFalse(hasattr(policy_mod, "GATE"))
        self.assertTrue(hasattr(policy_mod, "policy"))


if __name__ == "__main__":
    unittest.main()
