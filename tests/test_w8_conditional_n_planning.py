import unittest

from tools.w8_conditional_n_planning import (
    DELTAS,
    N_GRID,
    REPLICATES,
    SEEDS,
    TARGET_POWERS,
    first_lower_bound_crossing,
)


class TestW8ConditionalNPlanning(unittest.TestCase):
    def test_preregistered_design_is_pinned(self):
        self.assertEqual(DELTAS, (0.01, 0.02))
        self.assertEqual(N_GRID,
                         (2500, 4000, 5000, 7500, 10000, 15000, 20000,
                          25000, 30000))
        self.assertEqual(TARGET_POWERS, (0.80, 0.90, 0.95))
        self.assertEqual(REPLICATES, 100_000)
        self.assertEqual(SEEDS, tuple(range(20261020, 20261038)))
        self.assertEqual(len(SEEDS), len(DELTAS) * len(N_GRID))

    def test_crossing_is_first_tested_n_and_keeps_neighbor(self):
        rows = [
            {"delta": 0.01, "n_per_window": 5000,
             "power_estimate": 0.70, "wilson_95": [0.69, 0.71]},
            {"delta": 0.01, "n_per_window": 10000,
             "power_estimate": 0.82, "wilson_95": [0.81, 0.83]},
            {"delta": 0.01, "n_per_window": 15000,
             "power_estimate": 0.94, "wilson_95": [0.93, 0.95]},
        ]
        crossing = first_lower_bound_crossing(rows, 0.01, 0.80)
        self.assertEqual(crossing["first_tested_n"], 10000)
        self.assertEqual(crossing["previous_tested_n"], 5000)
        self.assertEqual(crossing["wilson_95"], [0.81, 0.83])

    def test_no_crossing_is_reported_as_none(self):
        rows = [{"delta": 0.02, "n_per_window": 30000,
                 "power_estimate": 0.89, "wilson_95": [0.88, 0.90]}]
        self.assertIsNone(first_lower_bound_crossing(rows, 0.02, 0.90))

    def test_crossing_rejects_unregistered_targets(self):
        with self.assertRaises(ValueError):
            first_lower_bound_crossing([], 0.03, 0.80)
        with self.assertRaises(ValueError):
            first_lower_bound_crossing([], 0.01, 0.85)


if __name__ == "__main__":
    unittest.main()
