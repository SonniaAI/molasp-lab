import hashlib
import json
import unittest
from itertools import combinations
from pathlib import Path

from tools.w8_conditional_exact import hypergeom_upper_tail
from tools.w8_conditional_power import (
    ALPHA,
    BASELINE,
    DELTAS,
    N_PER_WINDOW,
    PAIR_COUNT,
    REPLICATES,
    SEEDS,
    maximum_two_window_sum,
    wilson_interval,
)


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "evidence/2026-10-10-w8-exact-power/power.json"
RECEIPT_SHA256 = "e359641d1a3f898d11e42692f110d66980c6dbbcf13afdcaccf1e24b911b9b96"


class TestW8ConditionalPowerReceipt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = RECEIPT.read_bytes()
        cls.data = json.loads(cls.raw)

    def test_receipt_is_the_frozen_power_run(self):
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(), RECEIPT_SHA256)
        self.assertEqual(self.data["analysis"],
                         "prospective-design-calibration-exact-conditional-two-hot-test")
        self.assertEqual(self.data["baseline_rate"], BASELINE)
        self.assertEqual(self.data["n_per_window"], N_PER_WINDOW)
        self.assertEqual(self.data["replicates_per_effect"], REPLICATES)
        self.assertEqual(self.data["rng"], "NumPy Generator(PCG64)")
        self.assertEqual(self.data["results"], [
            {
                "baseline_rate": BASELINE,
                "candidate_pair_count": PAIR_COUNT,
                "decision_rule": "15 * minimum exact conditional upper-tail p < 0.05",
                "delta": 0.01,
                "familywise_alpha": ALPHA,
                "hot_rate": BASELINE + 0.01,
                "n_per_window": N_PER_WINDOW,
                "pearson_chi2_approx_power": 0.256609442907212,
                "pearson_noncentrality": 3.4986737238506693,
                "power_estimate": 0.25034,
                "rejections": 50068,
                "replicates": REPLICATES,
                "seed": SEEDS[0],
                "true_hot_blocks": [8, 9],
                "wilson_95": [0.2484462208873815, 0.2522433695145046],
            },
            {
                "baseline_rate": BASELINE,
                "candidate_pair_count": PAIR_COUNT,
                "decision_rule": "15 * minimum exact conditional upper-tail p < 0.05",
                "delta": 0.02,
                "familywise_alpha": ALPHA,
                "hot_rate": BASELINE + 0.02,
                "n_per_window": N_PER_WINDOW,
                "pearson_chi2_approx_power": 0.8420469888529613,
                "pearson_noncentrality": 14.115936992473875,
                "power_estimate": 0.864855,
                "rejections": 172971,
                "replicates": REPLICATES,
                "seed": SEEDS[1],
                "true_hot_blocks": [8, 9],
                "wilson_95": [0.8633496697130044, 0.866346314801615],
            },
            {
                "baseline_rate": BASELINE,
                "candidate_pair_count": PAIR_COUNT,
                "decision_rule": "15 * minimum exact conditional upper-tail p < 0.05",
                "delta": 0.03,
                "familywise_alpha": ALPHA,
                "hot_rate": BASELINE + 0.03,
                "n_per_window": N_PER_WINDOW,
                "pearson_chi2_approx_power": 0.9973954720873225,
                "pearson_noncentrality": 32.04222309235609,
                "power_estimate": 0.99855,
                "rejections": 199710,
                "replicates": REPLICATES,
                "seed": SEEDS[2],
                "true_hot_blocks": [8, 9],
                "wilson_95": [0.9983733874115349, 0.9987074613633579],
            },
        ])

    def test_each_monte_carlo_interval_recomputes(self):
        for row in self.data["results"]:
            with self.subTest(delta=row["delta"]):
                self.assertEqual(row["power_estimate"],
                                 row["rejections"] / row["replicates"])
                self.assertEqual(row["wilson_95"],
                                 list(wilson_interval(row["rejections"],
                                                      row["replicates"])))

    def test_selected_pair_matches_all_exact_pair_tails_on_small_support(self):
        counts = (9, 8, 7, 6, 5, 4)
        top_sum, pair = maximum_two_window_sum(counts)
        tails = [hypergeom_upper_tail(60, sum(counts), 20,
                                     counts[i] + counts[j])
                 for i, j in combinations(range(6), 2)]
        self.assertEqual(pair, (0, 1))
        self.assertEqual(top_sum, 17)
        self.assertEqual(min(tails), hypergeom_upper_tail(
            60, sum(counts), 20, top_sum))

    def test_scipy_tail_crosscheck_matches_integer_receipt(self):
        crosscheck = self.data["tail_crosscheck"]
        exact = hypergeom_upper_tail(crosscheck["population"],
                                     crosscheck["successes"],
                                     crosscheck["draws"],
                                     crosscheck["observed"])
        self.assertAlmostEqual(crosscheck["integer_tail"], exact, places=14)
        self.assertAlmostEqual(crosscheck["scipy_tail"], exact, places=14)
        self.assertEqual(crosscheck["observed"], 7404)


if __name__ == "__main__":
    unittest.main()
