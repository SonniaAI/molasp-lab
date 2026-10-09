import unittest

from tools.w8_window_heterogeneity_bound import (
    OBSERVED_ARMS,
    analyze_observed,
    noncentrality_upper_bound,
    two_hot_delta_range_upper_bound,
    two_hot_delta_upper_bound,
)
from tools.w8_window_power import noncentral_chi2_sf_df5, two_hot_power


class TestW8WindowHeterogeneityBound(unittest.TestCase):
    def test_registered_observation_and_secondary_endpoint_are_pinned(self):
        result = analyze_observed()
        self.assertAlmostEqual(result["statistic"], 2.7713095514, places=9)
        self.assertAlmostEqual(result["p_value"], 0.7351922075, places=9)
        self.assertAlmostEqual(result["pooled_share"], 22111 / 29989, places=12)
        self.assertAlmostEqual(result["ncp_upper"], 4.9873176113, places=8)
        self.assertAlmostEqual(result["two_hot_delta_upper"],
                               0.0119319116, places=8)

    def test_endpoint_inverts_the_one_sided_lower_tail(self):
        result = analyze_observed()
        cdf = 1.0 - noncentral_chi2_sf_df5(
            result["statistic"], result["ncp_upper"])
        self.assertAlmostEqual(cdf, 0.05, places=10)

    def test_delta_maps_back_to_the_same_noncentrality(self):
        result = analyze_observed()
        ncp, _ = two_hot_power(
            int(result["n_per_window"]), result["two_hot_delta_upper"],
            result["baseline"])
        self.assertAlmostEqual(ncp, result["ncp_upper"], places=10)

    def test_registered_two_point_alternative_has_small_left_tail(self):
        result = analyze_observed()
        ncp, _ = two_hot_power(4998, 0.02, result["baseline"])
        lower_tail = 1.0 - noncentral_chi2_sf_df5(
            result["statistic"], ncp)
        self.assertAlmostEqual(lower_tail, 0.0018829074, places=9)

    def test_actual_denominators_make_equal_n_endpoint_error_negligible(self):
        result = analyze_observed()
        low, high = two_hot_delta_range_upper_bound(
            result["ncp_upper"], (4999, 4998, 4999, 4999, 4998, 4996),
            result["baseline"])
        self.assertAlmostEqual(low, 0.0119312089, places=9)
        self.assertAlmostEqual(high, 0.0119324208, places=9)
        self.assertLess(high - low, 0.000002)

    def test_actual_observed_windows_are_the_frozen_six_counts(self):
        self.assertEqual(tuple(n for _, n in OBSERVED_ARMS),
                         (4999, 4998, 4999, 4999, 4998, 4996))
        self.assertEqual(sum(x for x, _ in OBSERVED_ARMS), 22111)
        self.assertEqual(sum(n for _, n in OBSERVED_ARMS), 29989)

    def test_invalid_observation_and_sample_size_are_rejected(self):
        with self.assertRaises(ValueError):
            noncentrality_upper_bound(-1.0)
        with self.assertRaises(ValueError):
            noncentrality_upper_bound(2.0, alpha=1.0)
        with self.assertRaises(ValueError):
            two_hot_delta_upper_bound(1.0, 0)


if __name__ == "__main__":
    unittest.main()
