import unittest
from itertools import combinations

from tools.w8_unequal_n_power import (
    ALLOCATIONS,
    BASELINE,
    CELL_SEEDS,
    DELTAS,
    PAIR_COUNT,
    REPLICATES,
    conditional_pair_tails,
    minimum_pair_tail,
    validate_counts,
)


class TestW8UnequalNPower(unittest.TestCase):
    def test_registered_design_and_equal_total_exposure(self):
        self.assertAlmostEqual(BASELINE, 1110 / 1499, places=15)
        self.assertEqual(DELTAS, (0.01, 0.02))
        self.assertEqual(REPLICATES, 100_000)
        self.assertEqual(PAIR_COUNT, 15)
        self.assertEqual(len(CELL_SEEDS), 9)
        self.assertEqual(list(CELL_SEEDS.values()), list(range(20261040, 20261049)))
        self.assertEqual(set(ALLOCATIONS), {"balanced", "hot_small", "hot_large"})
        self.assertEqual({sum(ns) for ns in ALLOCATIONS.values()}, {30_000})

    def test_all_fifteen_fixed_pair_tails_match_exact_integer_helper(self):
        counts = (1820, 1854, 4650, 4631, 4659, 4681)
        trials = ALLOCATIONS["hot_small"]
        tails = conditional_pair_tails(counts, trials)
        self.assertEqual(len(tails), 15)
        for (i, j), p_value in zip(combinations(range(6), 2), tails):
            from tools.w8_conditional_exact import hypergeom_upper_tail
            expected = hypergeom_upper_tail(
                sum(trials), sum(counts), trials[i] + trials[j], counts[i] + counts[j])
            self.assertEqual(p_value, expected)

    def test_unequal_denominator_minimum_need_not_be_pair_with_largest_raw_sum(self):
        trials = (1, 1, 1, 1, 1, 5)
        counts = (1, 1, 0, 0, 0, 3)
        _, winning_pair = minimum_pair_tail(counts, trials)
        raw_sums = [(counts[i] + counts[j], (i, j))
                    for i, j in combinations(range(6), 2)]
        largest_count_pair = max(raw_sums)[1]
        self.assertEqual(winning_pair, (0, 1))
        self.assertNotEqual(winning_pair, largest_count_pair)

    def test_equal_denominator_top_two_counts_have_a_minimum_pair_tail(self):
        trials = (20, 20, 20, 20, 20, 20)
        counts = (11, 17, 13, 9, 16, 10)
        tails = conditional_pair_tails(counts, trials)
        max_sum = max(counts[i] + counts[j] for i, j in combinations(range(6), 2))
        minimum_tail = min(tails)
        self.assertEqual(tails[0], minimum_tail) if counts[0] + counts[1] == max_sum else None
        self.assertIn(minimum_tail, [p for (i, j), p in zip(combinations(range(6), 2), tails)
                                     if counts[i] + counts[j] == max_sum])

    def test_validation_rejects_wrong_shape_or_invalid_counts(self):
        for counts, trials in (
            ((1, 2), (1, 2)),
            ((1, 2, 3, 4, 5, True), (1, 2, 3, 4, 5, 6)),
            ((1, 2, 3, 4, 5, 7), (1, 2, 3, 4, 5, 6)),
            ((1, 2, 3, 4, 5, 6), (1, 2, 3, 4, 5, 0)),
            ((1, 2, 3, 4, 5, 6.0), (1, 2, 3, 4, 5, 6)),
        ):
            with self.subTest(counts=counts, trials=trials), self.assertRaises(ValueError):
                validate_counts(counts, trials)

    @unittest.skipUnless(__import__("importlib.util", fromlist=["find_spec"]).find_spec("scipy") is not None,
                         "SciPy is used only by the optional simulation cross-check")
    def test_scipy_and_integer_tails_agree_for_unequal_pair_draws(self):
        from tools.w8_unequal_n_power import scipy_pair_tails

        counts = (1820, 1854, 4650, 4631, 4659, 4681)
        trials = ALLOCATIONS["hot_small"]
        integer_tails = conditional_pair_tails(counts, trials)
        scipy_tails = scipy_pair_tails(counts, trials)
        for integer_tail, scipy_tail in zip(integer_tails, scipy_tails):
            self.assertAlmostEqual(integer_tail, scipy_tail, places=12)


if __name__ == "__main__":
    unittest.main()
