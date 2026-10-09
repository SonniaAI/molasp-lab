import unittest

from tools.w8_baseline_sensitivity import (
    HISTORICAL_SUCCESSES,
    HISTORICAL_TRIALS,
    analyze_baseline_sensitivity,
    wilson_interval,
)


class TestW8BaselineSensitivity(unittest.TestCase):
    def test_historical_baseline_wilson_interval_is_pinned(self):
        self.assertAlmostEqual(HISTORICAL_SUCCESSES / HISTORICAL_TRIALS,
                               0.7404936624416277, places=14)
        low, high = wilson_interval(HISTORICAL_SUCCESSES, HISTORICAL_TRIALS)
        self.assertAlmostEqual(low, 0.717707527015, places=11)
        self.assertAlmostEqual(high, 0.762050331519, places=11)

    def test_delta_mapping_is_pinned_at_interval_and_plugin_baselines(self):
        result = analyze_baseline_sensitivity()
        self.assertAlmostEqual(result["ncp_upper"], 4.9873176113, places=9)
        self.assertAlmostEqual(result["delta_upper_at_baseline_low"],
                               0.012259025878, places=11)
        self.assertAlmostEqual(result["delta_upper_at_plugin_baseline"],
                               0.011931911626, places=11)
        self.assertAlmostEqual(result["delta_upper_at_baseline_high"],
                               0.011583647237, places=11)
        self.assertLess(result["delta_upper_mapping_high"] -
                        result["delta_upper_mapping_low"], 0.000676)

    def test_mapping_decreases_over_this_baseline_interval(self):
        result = analyze_baseline_sensitivity()
        self.assertGreater(result["delta_upper_at_baseline_low"],
                           result["delta_upper_at_plugin_baseline"])
        self.assertGreater(result["delta_upper_at_plugin_baseline"],
                           result["delta_upper_at_baseline_high"])

    def test_invalid_binomial_counts_and_z_are_rejected(self):
        for args in ((0, 0), (-1, 3), (4, 3), (1.5, 3), (True, 3)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                wilson_interval(*args)
        with self.assertRaises(ValueError):
            wilson_interval(1, 3, z=0.0)


if __name__ == "__main__":
    unittest.main()
