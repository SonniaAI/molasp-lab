import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from tools.collect_w8_window_resolution import collect


class TestCollectW8WindowResolution(unittest.TestCase):
    def make_runout(self, counts=None, cal=(367, 131), reported=None):
        counts = counts or [(3702, 1298)] * 6
        arms = []
        for index, (d2t, l2) in enumerate(counts):
            arms.append({
                "block": 8 + index,
                "seed0": 380261107 + index * 20000000,
                "n_trajectories": 5000,
                "D2T": d2t,
                "L2": l2,
                "other": 0,
                "pair_n": d2t + l2,
                "share": d2t / float(d2t + l2),
                "wilson95": None,
            })
        # These synthetic fixtures use full pair counts and their Wilson
        # intervals are filled by the same public formula pinned in tests.
        from tools.collect_w8_window_resolution import wilson95
        for arm in arms:
            arm["wilson95"] = wilson95(arm["D2T"], arm["pair_n"])
        total_x = sum(row["D2T"] for row in arms)
        total_n = sum(row["pair_n"] for row in arms)
        rate = total_x / float(total_n)
        cal_ok = cal == (367, 131)
        from tools.w8_window_power import read_primary
        branch, metrics = read_primary(
            cal_ok, [(row["D2T"], row["pair_n"]) for row in arms])
        primary = {"branch": branch, "metrics": metrics}
        verdicts = {"CAL": "CAL_OK" if cal_ok else "CAL_FAIL",
                    "PRIMARY": branch}
        if reported is not None:
            verdicts = reported
        stats = {
            "calibration": {
                "seed0": 260261107, "n": 500,
                "mid_w4": {"D2T": cal[0], "L2": cal[1], "other": 0},
                "expected_D2T_L2": [367, 131],
                "status": "CAL_OK" if cal_ok else "CAL_FAIL"},
            "protocol": {"dg": 2.0, "win_mult": 8.0,
                         "n_per_window": 5000, "alpha": 0.05,
                         "primary_df": 5,
                         "primary_test": "Pearson homogeneity"},
            "arms": arms,
            "descriptive": {
                "pooled_pair_rate": rate,
                "pooled_pair_wilson95": wilson95(total_x, total_n),
                "windows_at_least_family_plus": {
                    "at_least_family_plus_0.02": sum(
                        row["share"] >= 1110 / 1499 + 0.02 for row in arms),
                    "at_least_family_plus_0.03": sum(
                        row["share"] >= 1110 / 1499 + 0.03 for row in arms)}},
            "primary": primary,
        }
        if not cal_ok:
            verdicts = {"CAL": "CAL_FAIL", "PRIMARY": "VOID_CAL_FAIL"}
        return json.dumps(stats) + "\nVERDICTS " + json.dumps(verdicts) + "\n"

    def test_equal_window_rates_cross_check_to_no_detection(self):
        receipt = collect(self.make_runout(), request_id="test-request")
        self.assertEqual(receipt["branch"], "HETEROGENEITY_NOT_DETECTED")
        self.assertAlmostEqual(receipt["primary"]["statistic"], 0.0, places=20)
        self.assertAlmostEqual(receipt["primary"]["p_value"], 1.0, places=12)
        self.assertEqual(receipt["cross_check"], "ok")
        self.assertEqual(receipt["request_id"], "test-request")

    def test_preregistered_two_hot_pattern_is_detected(self):
        counts = [(3702, 1298)] * 4 + [(3852, 1148)] * 2
        receipt = collect(self.make_runout(counts=counts))
        self.assertEqual(receipt["branch"], "HETEROGENEITY_DETECTED")
        self.assertLess(receipt["primary"]["p_value"], 0.05)

    def test_calibration_failure_voids_the_result(self):
        receipt = collect(self.make_runout(cal=(366, 131)))
        self.assertEqual(receipt["branch"], "VOID_CAL_FAIL")
        self.assertIsNone(receipt["primary"])

    def test_wrong_seed_or_instrument_branch_is_refused(self):
        text = self.make_runout()
        stats, verdicts = text.split("\nVERDICTS ", 1)
        obj = json.loads(stats)
        obj["arms"][0]["seed0"] += 1
        with self.assertRaisesRegex(ValueError, "frozen block/seed/n"):
            collect(json.dumps(obj) + "\nVERDICTS " + verdicts)

        with self.assertRaisesRegex(ValueError, "instrument verdict mismatch"):
            collect(self.make_runout(reported={"CAL": "CAL_OK",
                                               "PRIMARY": "HETEROGENEITY_DETECTED"}))


if __name__ == "__main__":
    unittest.main()
