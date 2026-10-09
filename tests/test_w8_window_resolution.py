import glob
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WINDOWS_DIR = os.path.join(
    ROOT, "evidence", "2026-10-09-w8-window-heterogeneity")
BLOCKPROBE_DIR = os.path.join(ROOT, "evidence", "2026-10-09-w8-blockprobe")
TILES_AND_DIR = os.path.join(ROOT, "evidence", "2026-10-06-body-conjunction-builds")
TILES_DEATH_DIR = os.path.join(ROOT, "evidence", "2026-10-06-structural-death")
for path in (ROOT, WINDOWS_DIR, BLOCKPROBE_DIR, TILES_AND_DIR, TILES_DEATH_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

import ktam_w8_windows as harness  # noqa: E402
from tools.w8_window_power import (  # noqa: E402
    FAMILY_RATE,
    chi2_critical_df5,
    chi2_sf_df5,
    heterogeneity_stat,
    read_primary,
    two_hot_power,
)


class TestW8WindowResolution(unittest.TestCase):
    def test_df5_alpha_cutoff(self):
        cutoff = chi2_critical_df5(0.05)
        self.assertAlmostEqual(cutoff, 11.0704976935, places=8)
        self.assertAlmostEqual(chi2_sf_df5(cutoff), 0.05, places=10)

    def test_equal_window_rates_have_no_heterogeneity_signal(self):
        arms = [(3702, 5000)] * 6
        statistic, p_value, pooled = heterogeneity_stat(arms)
        self.assertAlmostEqual(statistic, 0.0, places=20)
        self.assertEqual(p_value, 1.0)
        self.assertAlmostEqual(pooled, 3702 / 5000)
        self.assertEqual(read_primary(True, arms)[0],
                         "HETEROGENEITY_NOT_DETECTED")

    def test_two_hot_windows_match_the_registered_alternative(self):
        arms = [(3702, 5000)] * 4 + [(3852, 5000)] * 2
        branch, metrics = read_primary(True, arms)
        self.assertEqual(branch, "HETEROGENEITY_DETECTED")
        self.assertEqual(metrics["df"], 5)
        self.assertLess(metrics["p_value"], 0.05)

    def test_calibration_failure_has_no_science_verdict(self):
        self.assertEqual(read_primary(False, [(3700, 5000)] * 6),
                         ("VOID_CAL_FAIL", None))

    def test_insufficient_pair_events_has_no_science_verdict(self):
        self.assertEqual(read_primary(True, [(20, 30)] * 6),
                         ("NO_EVENTS", None))

    def test_rate_resolution_power_is_pinned_at_n500_and_n5000(self):
        ncp500, power500 = two_hot_power(500, 0.02)
        ncp5000, power5000 = two_hot_power(5000, 0.02)
        self.assertGreater(ncp500, 0.0)
        self.assertGreater(ncp5000, ncp500)
        self.assertAlmostEqual(power500, 0.122, places=3)
        self.assertAlmostEqual(power5000, 0.842, places=3)
        self.assertAlmostEqual(FAMILY_RATE, 1110 / 1499)

    def test_three_point_shift_has_eighty_percent_power_at_n2000(self):
        _, power = two_hot_power(2000, 0.03)
        self.assertAlmostEqual(power, 0.800, places=3)

    def test_six_new_seed_windows_are_fresh_and_nonoverlapping(self):
        self.assertEqual(harness.ARM_BLOCKS, (8, 9, 10, 11, 12, 13))
        ranges = harness.planned_seed_ranges()
        self.assertEqual(len(ranges), 6)
        self.assertTrue(all(stop - start == 5000 for start, stop in ranges))
        previous = [
            (260261107, 260261607),  # fixed CAL window
            (280261107, 280261607),  # w8 fresh arm 3
            (300261107, 300261260),  # growth arm 4
            (320261107, 320261607),  # arm 5
            (340261107, 340261607),  # arm 6
            (340261607, 340262107),  # arm 6B
            (350261107, 350261607),  # arm 8
            (360261107, 360261606),  # arm 7 (n=499)
        ]
        for start, stop in ranges:
            for old_start, old_stop in previous:
                self.assertTrue(stop <= old_start or start >= old_stop,
                                (start, stop, old_start, old_stop))

    def test_reserved_windows_are_absent_from_prior_receipts(self):
        starts = tuple(harness.SEED0_WINDOWS)
        for run_path in glob.glob(os.path.join(ROOT, "evidence", "*", "run.out")):
            if os.path.dirname(run_path) == WINDOWS_DIR:
                continue
            with open(run_path, encoding="utf-8") as stream:
                receipt = stream.read()
            for seed in starts:
                self.assertNotIn(str(seed), receipt, run_path)

    def test_power_is_monotone_in_sample_size_and_effect(self):
        _, p_small = two_hot_power(2000, 0.02)
        _, p_large = two_hot_power(5000, 0.02)
        _, p_effect = two_hot_power(5000, 0.03)
        self.assertLess(p_small, p_large)
        self.assertLess(p_large, p_effect)


if __name__ == "__main__":
    unittest.main()
