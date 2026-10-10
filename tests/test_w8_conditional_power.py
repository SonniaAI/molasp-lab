import math
import unittest
from itertools import combinations

from tools.w8_conditional_power import (
    ALPHA,
    BASELINE,
    DELTAS,
    N_PER_WINDOW,
    PAIR_COUNT,
    REPLICATES,
    SEEDS,
    bonferroni_adjust,
    maximum_two_window_sum,
    wilson_interval,
)


class TestW8ConditionalPower(unittest.TestCase):
    def test_registered_design_constants_are_pinned(self):
        self.assertAlmostEqual(BASELINE, 1110 / 1499, places=15)
        self.assertEqual(DELTAS, (0.01, 0.02, 0.03))
        self.assertEqual(N_PER_WINDOW, 5000)
        self.assertEqual(REPLICATES, 200_000)
        self.assertEqual(SEEDS, (20261010, 20261011, 20261012))
        self.assertEqual(PAIR_COUNT, 15)
        self.assertEqual(ALPHA, 0.05)

    def test_top_pair_sum_matches_all_fifteen_pair_enumeration(self):
        counts = (3644, 3707, 3692, 3675, 3696, 3697)
        top_sum, top_pair = maximum_two_window_sum(counts)
        all_sums = [(counts[i] + counts[j], (i, j))
                    for i, j in combinations(range(6), 2)]
        self.assertEqual(len(all_sums), 15)
        self.assertEqual(top_sum, max(value for value, _ in all_sums))
        self.assertIn((top_sum, top_pair), all_sums)
        self.assertEqual(top_pair, (1, 5))

    def test_top_pair_ties_are_handled_deterministically(self):
        total, pair = maximum_two_window_sum((5, 5, 5, 5, 5, 5))
        self.assertEqual(total, 10)
        self.assertEqual(pair, (0, 1))

    def test_two_window_sum_validates_shape_and_types(self):
        for counts in ((1, 2), (1, 2, 3, 4, 5, True),
                       (1, 2, 3, 4, 5, -1), (1, 2, 3, 4, 5, 6.0)):
            with self.subTest(counts=counts), self.assertRaises(ValueError):
                maximum_two_window_sum(counts)

    def test_bonferroni_adjustment_caps_at_one_and_uses_fifteen_pairs(self):
        self.assertAlmostEqual(bonferroni_adjust(0.001), 0.015)
        self.assertEqual(bonferroni_adjust(0.5), 1.0)
        self.assertAlmostEqual(bonferroni_adjust(0.02, 2), 0.04)

    def test_bonferroni_adjustment_rejects_invalid_inputs(self):
        for value in (-0.1, 1.1, math.inf, math.nan):
            with self.subTest(value=value), self.assertRaises(ValueError):
                bonferroni_adjust(value)
        for count in (0, -1, True, 1.5):
            with self.subTest(count=count), self.assertRaises(ValueError):
                bonferroni_adjust(0.01, count)

    def test_wilson_interval_covers_boundary_counts(self):
        low, high = wilson_interval(0, 200_000)
        self.assertEqual(low, 0.0)
        self.assertGreater(high, 0.0)
        low, high = wilson_interval(200_000, 200_000)
        self.assertLess(low, 1.0)
        self.assertEqual(high, 1.0)

    def test_wilson_interval_contains_estimate_and_validates(self):
        low, high = wilson_interval(16, 20)
        self.assertLess(low, 0.8)
        self.assertGreater(high, 0.8)
        for args in ((-1, 20), (21, 20), (1.5, 20), (1, 0),
                     (1, 20, 0.0), (1, 20, math.inf)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                wilson_interval(*args)


if __name__ == "__main__":
    unittest.main()
