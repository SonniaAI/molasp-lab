"""CI invariants for the exact first-passage CTMC (tick 8).

Pins the structural properties of the window-chain solver so the exact
numbers in research-log/2026-10-06-empty-first-passage.md cannot drift
silently: probability conservation, dG-monotonicity of the trap
channels, and the attribution ordering that demoted the retry story.
Solver calls are deterministic (no RNG); runtime ~10 s.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE),
                                "evidence", "2026-10-06-empty-first-passage"))

import ctmc_first_passage as C  # noqa: E402


class FirstPassageInvariants(unittest.TestCase):
    def test_probabilities_conserved(self):
        probs, _, ns, na = C.point(2.0)
        self.assertEqual(ns, 72)
        self.assertEqual(na, 15)
        self.assertAlmostEqual(sum(probs.values()), 1.0, places=9)

    def test_trap_channels_fall_with_dg(self):
        t1 = {}
        for dg in (0.5, 2.0, 4.0):
            probs, _, _, _ = C.point(dg)
            t1[dg] = probs["empty"] + probs["p"]
        self.assertGreater(t1[0.5], t1[2.0])
        self.assertGreater(t1[2.0], t1[4.0])

    def test_attribution_ordering_demotes_retries(self):
        full, _, _, _ = C.point(2.0)
        no_l1, _, _, _ = C.point(2.0, variant="no-L1-first")
        wonly, _, _, _ = C.point(2.0, variant="D1F-W-only")
        t = lambda p: p["empty"] + p["p"]  # noqa: E731
        self.assertGreater(t(full), t(no_l1))
        self.assertGreater(t(no_l1), t(wonly))
        # W-only race sits BELOW the single-shot formula (attach race
        # competition), so retries alone cannot explain the .174 excess.
        self.assertLess(t(wonly), 1.0 / (1.0 + pow(2.718281828459045, 2.0)))

    def test_empty_cell_prediction_pinned(self):
        probs, _, _, _ = C.point(2.0)
        t1 = probs["empty"] + probs["p"]
        t2 = probs["ap"] + probs["p"]
        pred = t1 * (1 - t2)
        self.assertGreater(pred, 0.15)
        self.assertLess(pred, 0.25)


if __name__ == "__main__":
    unittest.main()
