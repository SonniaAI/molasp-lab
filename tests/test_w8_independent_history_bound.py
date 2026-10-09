import unittest

from tools.w8_independent_history_bound import (
    TICK106_POOLED_HISTORY_ENVELOPE,
    Z_ONE_SIDED_95,
    analyze_independent_history,
)
from tools.w8_window_heterogeneity_bound import OBSERVED_ARMS


class TestW8IndependentHistoryBound(unittest.TestCase):
    def test_registered_six_window_counts_and_all_pairs_are_used(self):
        self.assertEqual(OBSERVED_ARMS, (
            (3644, 4999), (3707, 4998), (3692, 4999),
            (3675, 4999), (3696, 4998), (3697, 4996),
        ))
        result = analyze_independent_history()
        self.assertEqual(result["assignment_count"], 15)
        pairs = [tuple(row["hot_blocks"]) for row in result["assignments"]]
        self.assertEqual(len(set(pairs)), 15)

    def test_current_only_envelope_and_change_from_tick106_are_pinned(self):
        result = analyze_independent_history()
        self.assertEqual(result["minimum_hot_blocks"], [8, 11])
        self.assertEqual(result["maximum_hot_blocks"], [9, 13])
        self.assertAlmostEqual(result["minimum_upper_delta"],
                               0.000977107135, places=12)
        self.assertAlmostEqual(result["maximum_upper_delta"],
                               0.014126577273, places=12)
        self.assertAlmostEqual(result["tick106_pooled_history_envelope"],
                               TICK106_POOLED_HISTORY_ENVELOPE, places=15)
        self.assertAlmostEqual(result["absolute_increase_vs_tick106"],
                               0.000453698881, places=12)

    def test_historical_reference_is_not_in_current_cold_aggregate(self):
        result = analyze_independent_history()
        selected = next(row for row in result["assignments"]
                        if row["hot_blocks"] == [9, 13])
        self.assertEqual((selected["cold_x"], selected["cold_n"]),
                         (14707, 19995))
        self.assertEqual((selected["hot_x"], selected["hot_n"]),
                         (7404, 9994))
        self.assertEqual(
            result["historical_model"],
            "independent unrestricted nuisance; contributes no information to delta",
        )

    def test_every_reported_endpoint_inverts_to_the_registered_score(self):
        result = analyze_independent_history()
        for row in result["assignments"]:
            with self.subTest(pair=row["hot_blocks"]):
                self.assertAlmostEqual(row["score_at_upper"],
                                       -Z_ONE_SIDED_95, places=9)


if __name__ == "__main__":
    unittest.main()
