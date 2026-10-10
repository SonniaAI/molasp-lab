import hashlib
import json
import unittest
from pathlib import Path

from tools.w8_conditional_n_planning import (
    DELTAS,
    N_GRID,
    REPLICATES,
    SEEDS,
    TARGET_POWERS,
    first_lower_bound_crossing,
)
from tools.w8_conditional_power import hypergeom_upper_tail, wilson_interval


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "evidence/2026-10-10-w8-conditional-n-planning/grid.json"
RECEIPT_SHA256 = "285e75b485f0ac83eff2505094d1f5e1ac27bc9670290385143f166cdf4a85a0"
ENVIRONMENT = ROOT / "evidence/2026-10-10-w8-conditional-n-planning/environment.json"
EXPECTED_REJECTIONS = (
    (0.01, 2500, 12897), (0.01, 4000, 19990), (0.01, 5000, 24784),
    (0.01, 7500, 38282), (0.01, 10000, 51208), (0.01, 15000, 72663),
    (0.01, 20000, 86173), (0.01, 25000, 93658), (0.01, 30000, 97325),
    (0.02, 2500, 51390), (0.02, 4000, 76378), (0.02, 5000, 86718),
    (0.02, 7500, 97299), (0.02, 10000, 99593), (0.02, 15000, 99995),
    (0.02, 20000, 100000), (0.02, 25000, 100000), (0.02, 30000, 100000),
)


class TestW8ConditionalNPlanningReceipt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = RECEIPT.read_bytes()
        cls.data = json.loads(cls.raw)

    def test_frozen_grid_receipt_and_rejection_counts(self):
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(), RECEIPT_SHA256)
        self.assertEqual(self.data["analysis"],
                         "prospective-exact-conditional-two-hot-sample-size-grid")
        self.assertEqual(self.data["deltas"], list(DELTAS))
        self.assertEqual(self.data["n_per_window_grid"], list(N_GRID))
        self.assertEqual(self.data["target_powers"], list(TARGET_POWERS))
        self.assertEqual(self.data["replicates_per_cell"], REPLICATES)
        self.assertEqual(self.data["rng"], "NumPy Generator(PCG64)")
        actual = tuple((row["delta"], row["n_per_window"], row["rejections"])
                       for row in self.data["results"])
        self.assertEqual(actual, EXPECTED_REJECTIONS)
        self.assertEqual(tuple(row["seed"] for row in self.data["results"]), SEEDS)

    def test_monte_carlo_intervals_recompute_from_receipt_counts(self):
        for row in self.data["results"]:
            with self.subTest(delta=row["delta"], n=row["n_per_window"]):
                self.assertEqual(row["power_estimate"],
                                 row["rejections"] / row["replicates"])
                self.assertEqual(row["wilson_95"], list(wilson_interval(
                    row["rejections"], row["replicates"])))

    def test_registered_crossings_recompute_and_are_bracketed(self):
        expected = [
            first_lower_bound_crossing(self.data["results"], delta, target)
            for delta in DELTAS for target in TARGET_POWERS
        ]
        self.assertEqual(self.data["first_lower_bound_crossings"], expected)
        for row in expected:
            self.assertLess(row["previous_wilson_95"][1], row["target_power"])
            self.assertGreaterEqual(row["wilson_95"][0], row["target_power"])

    def test_fresh_n5000_cells_overlap_prior_tick_intervals(self):
        prior = {0.01: (0.2484462208873815, 0.2522433695145046),
                 0.02: (0.8633496697130044, 0.866346314801615)}
        for row in self.data["results"]:
            if row["n_per_window"] != 5000:
                continue
            low, high = row["wilson_95"]
            old_low, old_high = prior[row["delta"]]
            self.assertLessEqual(max(low, old_low), min(high, old_high))

    def test_fixed_tail_crosscheck_matches_exact_integer_helper(self):
        row = self.data["fixed_tail_crosscheck"]
        exact = hypergeom_upper_tail(row["population"], row["successes"],
                                     row["draws"], row["observed"])
        self.assertAlmostEqual(row["integer_tail"], exact, places=14)
        self.assertAlmostEqual(row["scipy_tail"], exact, places=14)
        self.assertEqual(row["observed"], 7404)

    def test_scipy_tail_matches_integer_helper_across_rejection_boundary(self):
        from scipy.stats import hypergeom

        population, successes, draws = 30_000, 22_111, 10_000
        threshold = 0.05 / 15
        expected = {
            7468: 0.0033853420875714934,
            7469: 0.0031109384550714442,
        }
        adjusted = {}
        for observed, integer_expected in expected.items():
            with self.subTest(observed=observed):
                exact = hypergeom_upper_tail(population, successes,
                                             draws, observed)
                scipy_tail = float(hypergeom.sf(observed - 1, population,
                                                successes, draws))
                self.assertAlmostEqual(exact, integer_expected, places=14)
                self.assertAlmostEqual(scipy_tail, integer_expected, places=14)
                adjusted[observed] = 15 * exact
        self.assertGreater(adjusted[7468], 0.05)
        self.assertLess(adjusted[7469], 0.05)
        self.assertGreater(expected[7468], threshold)
        self.assertLess(expected[7469], threshold)

    def test_environment_sidecar_discloses_post_run_capture(self):
        data = json.loads(ENVIRONMENT.read_text())
        self.assertTrue(data["captured_after_run"])
        self.assertEqual(data["python"], "3.11.2")
        self.assertEqual(data["numpy"], "2.4.6")
        self.assertEqual(data["scipy"], "1.17.1")
        self.assertIn("runner did not embed", data["note"])


if __name__ == "__main__":
    unittest.main()
