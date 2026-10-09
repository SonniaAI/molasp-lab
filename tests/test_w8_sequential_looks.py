"""Pins for tools/w8_sequential_looks.py (tick 94, 2026-10-09).

Every pinned number was measured from the tool's own live output
(measure-then-pin) BEFORE this file was committed.  The tick-88
single-look cross-checks (31.3% / 27.4% / 27.0% / 21.5%) are
receipt-duplicated from research-log/2026-10-09-w8-datum-noise.md —
they pin the identity between this module's gate arithmetic and the
committed datum-noise map.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.w8_sequential_looks import (  # noqa: E402
    K1,
    K80,
    K_LINE,
    GROW2,
    GROW3,
    TRUTHS,
    _gate_held_x,
    sequential_map,
    single_look_error,
)


class TestLadderConstants(unittest.TestCase):
    def test_canonical_ladder_prices(self):
        # The tick-92 committed canonical prices this module freezes.
        self.assertEqual(K1, 500)
        self.assertEqual(K_LINE, 1442)      # 3 pooled arms
        self.assertEqual(K80, 2895)         # 6 pooled arms
        self.assertEqual(GROW2, 942)
        self.assertEqual(GROW3, 1453)
        self.assertEqual(GROW2 + GROW3, K80 - K1)

    def test_truth_grid_covers_edges_and_probes(self):
        for edge in ("0.78376", "0.88376", "0.81415", "0.71415", "0.83376"):
            self.assertIn(edge, TRUTHS)
        self.assertEqual(len(TRUTHS), 10)

    def test_gate_fraction_exact_at_k500(self):
        # Tick-88 receipt: below-floor x<=391, within-ceiling x<=441.
        held, _, _ = _gate_held_x(500)
        self.assertFalse(held[391])
        self.assertTrue(held[392])
        self.assertTrue(held[441])
        self.assertFalse(held[442])


class TestSingleLookIdentityTick88(unittest.TestCase):
    """err_1look must reproduce the committed tick-88 edge probes."""

    def test_floor_side_probes(self):
        # 0.01 outside the floor false-HELDs 31.3% (tick-88 receipt).
        self.assertAlmostEqual(single_look_error("0.77376")[0], 0.3134, places=3)
        # 0.01 inside the floor false-REFUTEDs 27.4%.
        self.assertAlmostEqual(single_look_error("0.79376")[1], 0.2737, places=3)

    def test_ceiling_side_probes(self):
        # 0.01 inside the ceiling false-REFUTEDs 27.0%.
        self.assertAlmostEqual(single_look_error("0.87376")[1], 0.2704, places=3)
        # 0.01 outside the ceiling false-HELDs 21.5%.
        self.assertAlmostEqual(single_look_error("0.89376")[0], 0.2152, places=3)


class TestPinnedRows(unittest.TestCase):
    """Verbatim pins from the tool's live output (2026-10-09 run)."""

    def test_primary_row(self):
        m = sequential_map("0.83376")
        self.assertAlmostEqual(m["stop1"], 0.08113814456, places=8)
        self.assertAlmostEqual(m["stop2"], 0.43345738457, places=8)
        self.assertAlmostEqual(m["stop3"], 0.30353792723, places=8)
        self.assertAlmostEqual(m["stage3_no_verdict"], 0.18186654364, places=8)
        self.assertAlmostEqual(m["error_total"], 2.9403191e-07, places=12)

    def test_worst_edge_rows(self):
        # The two exact gate edges carry the worst staged error.
        self.assertAlmostEqual(sequential_map("0.78376")["error_total"],
                               0.04257020016, places=8)
        self.assertAlmostEqual(sequential_map("0.88376")["error_total"],
                               0.05637233572, places=8)

    def test_trend_arm_row(self):
        m = sequential_map("0.76415")
        self.assertAlmostEqual(m["false_held"], 3.0466591e-06, places=11)
        self.assertAlmostEqual(single_look_error("0.76415")[0], 0.16039171, places=7)

    def test_far_flank(self):
        m = sequential_map("0.71415")
        self.assertAlmostEqual(m["error_total"], 5.9078322e-13, places=15)
        self.assertAlmostEqual(m["stage3_no_verdict"], 0.89812659, places=8)


class TestStructure(unittest.TestCase):
    def test_rows_conserve_probability(self):
        for s in TRUTHS:
            m = sequential_map(s)
            total = m["stop1"] + m["stop2"] + m["stop3"] + m["stage3_no_verdict"]
            self.assertAlmostEqual(total, 1.0, places=9, msg=s)

    def test_error_signs_follow_truth_side(self):
        for s in TRUTHS:
            m = sequential_map(s)
            if m["truth_inside_band"]:
                self.assertEqual(m["false_held"], 0.0, s)
                self.assertGreaterEqual(m["false_refuted"], 0.0)
            else:
                self.assertEqual(m["false_refuted"], 0.0, s)

    def test_staged_never_inflates_over_single_look(self):
        # The pre-registered headline: ambiguity-gated stopping is a
        # conservative filter at EVERY truth on the grid.
        for s in TRUTHS:
            m = sequential_map(s)
            e1 = single_look_error(s)
            self.assertLess(m["error_total"], e1[0] + e1[1], s)

    def test_kline_sensitivity_flat_at_primary(self):
        # A2 disclosure: realized k_line moves with phat; plausible
        # movement keeps the primary-truth error negligible.
        for k_line in (1342, 1542):
            m = sequential_map("0.83376", k_line=k_line)
            self.assertLess(m["error_total"], 1e-05)
            stops = m["stop1"] + m["stop2"] + m["stop3"]
            self.assertGreater(stops, 0.70)
            self.assertLess(stops, 0.95)


if __name__ == "__main__":
    unittest.main()
