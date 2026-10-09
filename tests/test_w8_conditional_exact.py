import math
import unittest
from fractions import Fraction
from itertools import combinations

from tools.w8_conditional_exact import (
    ALPHA,
    CANDIDATE_PAIR_COUNT,
    analyze_two_hot_family,
    hypergeom_upper_tail,
)
from tools.w8_window_heterogeneity_bound import OBSERVED_ARMS


class TestW8ConditionalExact(unittest.TestCase):
    def test_small_support_matches_direct_combinatorial_tail(self):
        # Hypergeom(N=6, K=3, draws=2): P(X>=1)=(9+3)/15=0.8.
        numerator = sum(math.comb(3, x) * math.comb(3, 2 - x)
                        for x in range(1, 3))
        denominator = math.comb(6, 2)
        self.assertEqual(numerator, 12)
        self.assertAlmostEqual(
            hypergeom_upper_tail(6, 3, 2, 1), numerator / denominator,
            places=15,
        )

    def test_support_boundaries_and_invalid_inputs(self):
        self.assertEqual(hypergeom_upper_tail(6, 3, 2, 0), 1.0)
        self.assertEqual(hypergeom_upper_tail(6, 3, 2, 3), 0.0)
        for args in ((0, 0, 0, 0), (6, 7, 2, 1), (6, 3, 7, 1),
                     (6, True, 2, 1), (6, 3, 2, 1.0)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                hypergeom_upper_tail(*args)

    def test_frozen_six_window_inputs_and_all_fifteen_pairs_are_used(self):
        self.assertEqual(OBSERVED_ARMS, (
            (3644, 4999), (3707, 4998), (3692, 4999),
            (3675, 4999), (3696, 4998), (3697, 4996),
        ))
        result = analyze_two_hot_family()
        pairs = [tuple(row["hot_blocks"]) for row in result["assignments"]]
        self.assertEqual(result["candidate_pair_count"], CANDIDATE_PAIR_COUNT)
        self.assertEqual(len(set(pairs)), CANDIDATE_PAIR_COUNT)
        self.assertEqual(result["total_successes"], 22111)
        self.assertEqual(result["total_trials"], 29989)

    def test_family_adjustment_is_bonferroni_over_all_candidates(self):
        result = analyze_two_hot_family()
        raw_minimum = min(row["conditional_upper_tail"]
                          for row in result["assignments"])
        self.assertAlmostEqual(result["minimum_unadjusted_p"], raw_minimum,
                               places=15)
        self.assertAlmostEqual(
            result["bonferroni_adjusted_p"],
            min(1.0, CANDIDATE_PAIR_COUNT * raw_minimum), places=15,
        )
        self.assertEqual(result["alpha"], ALPHA)
        self.assertEqual(
            result["reject_common_rate_null"],
            result["bonferroni_adjusted_p"] < ALPHA,
        )
        self.assertEqual(result["minimum_p_hot_blocks"], [9, 13])
        self.assertAlmostEqual(result["minimum_unadjusted_p"],
                               0.165759251604651, places=14)
        self.assertEqual(result["bonferroni_adjusted_p"], 1.0)
        self.assertFalse(result["reject_common_rate_null"])

    def test_minimum_tail_matches_direct_integer_combinatorial_sum(self):
        result = analyze_two_hot_family()
        selected = next(row for row in result["assignments"]
                        if row["hot_blocks"] == [9, 13])
        population = result["total_trials"]
        successes = result["total_successes"]
        draws = selected["hot_trials"]
        observed = selected["hot_successes"]
        numerator = sum(
            math.comb(successes, x)
            * math.comb(population - successes, draws - x)
            for x in range(observed, min(successes, draws) + 1)
        )
        direct = float(Fraction(numerator, math.comb(population, draws)))
        self.assertAlmostEqual(selected["conditional_upper_tail"], direct,
                               places=14)

    def test_each_assignment_uses_its_two_hot_blocks_and_exact_tail(self):
        result = analyze_two_hot_family()
        expected_pairs = set(combinations((8, 9, 10, 11, 12, 13), 2))
        observed_pairs = {tuple(row["hot_blocks"])
                          for row in result["assignments"]}
        self.assertEqual(observed_pairs, expected_pairs)
        for row in result["assignments"]:
            self.assertEqual(row["hot_successes"] + row["cold_successes"],
                             result["total_successes"])
            self.assertEqual(row["hot_trials"] + row["cold_trials"],
                             result["total_trials"])
            self.assertGreaterEqual(row["conditional_upper_tail"], 0.0)
            self.assertLessEqual(row["conditional_upper_tail"], 1.0)


if __name__ == "__main__":
    unittest.main()
