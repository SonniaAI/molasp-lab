"""Pins for the descriptive arm-wise reading of design 011's w8 tier labels."""

from __future__ import annotations

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.w8_armwise_tier_readout import interval_tiers, summarize_armwise_tiers


class TestArmwiseTierReadout(unittest.TestCase):
    def test_four_arm_counts_and_point_labels(self):
        arms = summarize_armwise_tiers()["arms"]
        expected = {
            "arm3": (375, 500, "ratchet-tilted"),
            "arm4": (106, 153, "ratchet-tilting"),
            "arm6": (389, 500, "ratchet-tilted"),
            "arm7": (365, 499, "ratchet-tilting"),
        }
        self.assertEqual(set(arms), set(expected))
        for label, (x, n, tier) in expected.items():
            with self.subTest(arm=label):
                self.assertEqual((arms[label]["x"], arms[label]["n"]), (x, n))
                self.assertEqual(arms[label]["point_tier"], tier)

    def test_every_pointwise_interval_crosses_075_only_between_two_tiers(self):
        arms = summarize_armwise_tiers()["arms"]
        for label, arm in arms.items():
            with self.subTest(arm=label):
                lo, hi = arm["wilson95"]
                self.assertLess(lo, 0.75)
                self.assertGreater(hi, 0.75)
                self.assertGreater(lo, 0.55)
                self.assertEqual(arm["interval_compatible_tiers"],
                                 ["ratchet-tilting", "ratchet-tilted"])
                self.assertFalse(arm["single_tier_throughout_interval"])

    def test_interval_tier_boundaries_are_half_open_as_design_011_states(self):
        self.assertEqual(interval_tiers(0.54, 0.55),
                         ("contested", "ratchet-tilting"))
        self.assertEqual(interval_tiers(0.75, 0.80), ("ratchet-tilted",))
        self.assertEqual(interval_tiers(0.70, 0.75),
                         ("ratchet-tilting", "ratchet-tilted"))

    def test_rejects_invalid_interval(self):
        with self.assertRaises(ValueError):
            interval_tiers(0.8, 0.7)
        with self.assertRaises(ValueError):
            interval_tiers(-0.1, 0.2)


if __name__ == "__main__":
    unittest.main()
