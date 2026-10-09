import unittest

from tools.w8_joint_baseline_bound import (
    HISTORICAL_SUCCESSES,
    HISTORICAL_TRIALS,
    analyze_joint_baseline_bound,
    one_sided_score_upper,
    profiled_score_z,
)


class TestW8JointBaselineBound(unittest.TestCase):
    def test_nuisance_profile_score_is_zero_at_fitted_common_rate(self):
        cold_x, cold_n, hot_x, hot_n = 740, 1000, 750, 1000
        fitted = (cold_x + hot_x) / (cold_n + hot_n)
        self.assertAlmostEqual(
            profiled_score_z(cold_x, cold_n, hot_x, hot_n, delta=0.0),
            (hot_x / hot_n - cold_x / cold_n)
            / ((fitted * (1.0 - fitted)
                * (1.0 / cold_n + 1.0 / hot_n)) ** 0.5),
            places=10,
        )

    def test_invalid_counts_and_delta_are_rejected(self):
        for args in ((0, 0, 1, 2, 0.1), (-1, 3, 1, 2, 0.1),
                     (1, 2, 3, 2, 0.1), (1.5, 3, 1, 2, 0.1),
                     (1, 3, 1, 2, -0.1), (1, 3, 1, 2, 1.0)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                profiled_score_z(*args)
        with self.assertRaises(ValueError):
            one_sided_score_upper(1, 3, 1, 3, z=0.0)

    def test_registered_counts_and_fifteen_hot_pair_envelope_are_pinned(self):
        self.assertEqual((HISTORICAL_SUCCESSES, HISTORICAL_TRIALS),
                         (1110, 1499))
        result = analyze_joint_baseline_bound()
        self.assertEqual(result["assignment_count"], 15)
        self.assertEqual(result["minimum_upper_hot_blocks"], [8, 11])
        self.assertEqual(result["envelope_hot_blocks"], [9, 13])
        self.assertAlmostEqual(result["minimum_assignment_upper"],
                               0.000832919288, places=11)
        self.assertAlmostEqual(result["upper_envelope"],
                               0.013672878393, places=11)
        uppers = [row["upper_delta"] for row in result["assignments"]]
        self.assertEqual(uppers, sorted(uppers))

    def test_upper_endpoint_inverts_the_one_sided_score(self):
        result = analyze_joint_baseline_bound()
        selected = next(row for row in result["assignments"]
                        if row["hot_blocks"] == [9, 13])
        self.assertAlmostEqual(
            profiled_score_z(selected["cold_x"], selected["cold_n"],
                             selected["hot_x"], selected["hot_n"],
                             selected["upper_delta"]),
            -1.6448536269514722,
            places=9,
        )


if __name__ == "__main__":
    unittest.main()
