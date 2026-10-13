"""Pins for the tick-126 width-vs-n pricing (tools/w8_width_vs_n.py).

Numbers are byte-reproducible from the pinned seeds (20261013 /
20261014) on the stdlib-only sampler. The paired-dataset proof is the
first_draw_row fingerprint equality with the tick-124 pins at scale 1
(same seed, same stratum order, same draw machinery) AND the exact
reproduction of the tick-124 Bonferroni all-strata realizations
(0.94975 / 0.95275). Direction pins encode the measured (not assumed)
sign of Wilson's z^2/n correction: at all frozen rates halving costs
slightly MORE than 4x per-stratum n."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from w8_simultaneous_band import bonferroni_z  # noqa: E402
from w8_stratified_census import (  # noqa: E402
    CONTESTED_FOUR_ARM_STRATA,
    SIX_WINDOW_STRATA,
    wilson95,
)
from w8_width_vs_n import (  # noqa: E402
    halving_multiple,
    n_for_half_width,
    n_menu,
    planning_table,
    real_data_readout,
    run,
    wilson_half_width,
)


class WidthIdentity(unittest.TestCase):
    def test_half_width_is_endpoint_half_distance(self):
        # At x/n == p the planning half-width must equal (hi-lo)/2 of the
        # Wilson interval exactly — this ties the planning curve to the
        # same wilson95 used for the reported bands.
        for strata in (SIX_WINDOW_STRATA, CONTESTED_FOUR_ARM_STRATA):
            z = bonferroni_z(len(strata))
            for s in strata:
                p = s.x / s.n
                lo, hi = wilson95(s.x, s.n, z)
                self.assertAlmostEqual(
                    wilson_half_width(p, s.n, z), (hi - lo) / 2.0,
                    places=12, msg=s.label)

    def test_validation(self):
        for bad_p in (0.0, 1.0, -0.1, 1.1):
            with self.assertRaises(ValueError):
                wilson_half_width(bad_p, 100, 1.96)
        for bad_n in (0, -1, 2.0, True):
            with self.assertRaises(ValueError):
                wilson_half_width(0.5, bad_n, 1.96)
        with self.assertRaises(ValueError):
            n_for_half_width(0.5, 0.0, 1.96)
        with self.assertRaises(ValueError):
            n_for_half_width(0.5, 1.1, 1.96)
        with self.assertRaises(ValueError):
            n_for_half_width(0.0, 0.05, 1.96)


class PlanningTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.six = planning_table(SIX_WINDOW_STRATA)
        cls.con = planning_table(CONTESTED_FOUR_ARM_STRATA)

    def test_current_width_pins(self):
        # Worst frozen stratum by Bonferroni half-width, both families.
        self.assertAlmostEqual(self.six["rows"][0]["half_widths"][0],
                               0.016577888572134457, places=12)  # block8
        self.assertEqual(
            max(range(6), key=lambda i: self.six["rows"][0]["half_widths"][i]),
            0)  # block8 is the worst six-window stratum
        self.assertAlmostEqual(
            min(self.con["rows"][0]["half_widths"]),
            0.0462619591737877, places=12)  # arm6 tightest
        self.assertAlmostEqual(
            max(self.con["rows"][0]["half_widths"]),
            0.09162385192989601, places=12)  # arm4 worst (n=153)

    def test_scaling_direction_and_pins(self):
        # Measured: width ratio sits slightly ABOVE 1/sqrt(s) at every
        # frozen rate (p(1-p) > 1/8) — the adverse direction. Pinned.
        base = self.six["rows"][0]["mean_half_width"]
        for row, sqrt_rule in zip(self.six["rows"][1:],
                                  (2 ** -0.5, 0.5, 8 ** -0.5, 0.25)):
            ratio = row["mean_half_width"] / base
            self.assertGreater(ratio, sqrt_rule)
        self.assertAlmostEqual(
            self.six["rows"][1]["mean_half_width"] / base,
            0.707281, places=6)
        self.assertAlmostEqual(
            self.six["rows"][2]["mean_half_width"] / base,
            0.500185, places=6)
        self.assertAlmostEqual(
            self.six["rows"][4]["mean_half_width"] / base,
            0.250116, places=6)


class HalvingAndMenu(unittest.TestCase):
    def test_halving_multiples(self):
        # Slightly ABOVE 4x at all frozen rates (measured direction).
        six = halving_multiple(3644 / 4999, 4999, bonferroni_z(6))
        self.assertEqual(six["n_to_halve"], 20012)
        self.assertAlmostEqual(six["exact_multiple"],
                               4.003200640128026, places=12)
        self.assertGreater(six["exact_multiple"], 4.0)
        arm4 = halving_multiple(106 / 153, 153, bonferroni_z(4))
        self.assertEqual(arm4["n_to_halve"], 628)
        self.assertAlmostEqual(arm4["exact_multiple"],
                               4.104575163398692, places=12)
        self.assertGreater(arm4["exact_multiple"], 4.0)

    def test_menu_pins_and_exactness(self):
        six = n_menu(SIX_WINDOW_STRATA)["rows"]
        expected_six = [(0.02, 4344, 3434), (0.015, 7727, 6108),
                        (0.01, 17395, 13748)]
        for row, (h, n_worst, n_obs) in zip(six, expected_six):
            self.assertEqual(row["target_half_width"], h)
            self.assertEqual(row["n_worst_case_p05"], n_worst)
            self.assertEqual(row["n_observed_rate"], n_obs)
        con = n_menu(CONTESTED_FOUR_ARM_STRATA)["rows"]
        expected_con = [(0.02, 3893, 3315), (0.015, 6926, 5896),
                        (0.01, 15591, 13272)]
        for row, (h, n_worst, n_obs) in zip(con, expected_con):
            self.assertEqual(row["target_half_width"], h)
            self.assertEqual(row["n_worst_case_p05"], n_worst)
            self.assertEqual(row["n_observed_rate"], n_obs)
        # Bisection exactness: minimal n — n-1 must MISS the target.
        z6, z4 = bonferroni_z(6), bonferroni_z(4)
        self.assertLessEqual(wilson_half_width(0.5, 4344, z6), 0.02)
        self.assertGreater(wilson_half_width(0.5, 4343, z6), 0.02)
        self.assertLessEqual(wilson_half_width(0.5, 15591, z4), 0.01)
        self.assertGreater(wilson_half_width(0.5, 15590, z4), 0.01)
        # Observed design rates: max-variance frozen rate per family.
        self.assertAlmostEqual(n_menu(SIX_WINDOW_STRATA)["rows"][0]
                               ["observed_design_rate"],
                               0.7289457891578316, places=12)  # block8
        self.assertAlmostEqual(n_menu(CONTESTED_FOUR_ARM_STRATA)["rows"][0]
                               ["observed_design_rate"],
                               0.6928104575163399, places=12)  # arm4

    def test_readout_shape(self):
        out = real_data_readout()
        self.assertEqual(out["six_window"]["worst_stratum"], "block8")
        self.assertEqual(out["contested_four_arm"]["worst_stratum"], "arm4")


class ScaledWorlds(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.worlds = {(w["label"], w["scale"]): w for w in run()}

    def test_scale1_fingerprints_equal_tick124(self):
        # PAIRED-DATASET PROOF: scale 1 reproduces the tick-123/124
        # datasets byte-exactly (pinned there as first_draw_row).
        self.assertEqual(
            self.worlds[("A_homogeneous_six_window", 1)]["first_draw_row"],
            [3695, 3658, 3722, 3728, 3671, 3682])
        self.assertEqual(
            self.worlds[("B_contested_four_arm", 1)]["first_draw_row"],
            [381, 101, 396, 374])

    def test_scale1_coverage_reproduces_tick124(self):
        # Exact reproduction of the tick-124 Bonferroni realizations.
        self.assertAlmostEqual(
            self.worlds[("A_homogeneous_six_window", 1)]["all_coverage"],
            0.94975, places=12)
        self.assertAlmostEqual(
            self.worlds[("B_contested_four_arm", 1)]["all_coverage"],
            0.95275, places=12)

    def test_scale4_coverage_holds(self):
        # Family level holds at 4x n (in-expectation union-bound claim;
        # realizations approximate within MC error ~ +-0.0068).
        self.assertAlmostEqual(
            self.worlds[("A_homogeneous_six_window", 4)]["all_coverage"],
            0.95, places=12)
        self.assertAlmostEqual(
            self.worlds[("B_contested_four_arm", 4)]["all_coverage"],
            0.94975, places=12)
        self.assertEqual(
            self.worlds[("A_homogeneous_six_window", 4)]["first_draw_row"],
            [14761, 14686, 14816, 14827, 14713, 14730])
        self.assertEqual(
            self.worlds[("B_contested_four_arm", 4)]["first_draw_row"],
            [1512, 413, 1570, 1477])

    def test_realized_tracks_planning_curve(self):
        # Realized mean Bonferroni half-width tracks the planning curve
        # within 0.3% at both scales — the budget tool is calibrated.
        expected = {
            ("A_homogeneous_six_window", 1): 0.999939878727958,
            ("B_contested_four_arm", 1): 0.9978107206078272,
            ("A_homogeneous_six_window", 4): 1.0000018239601371,
            ("B_contested_four_arm", 4): 0.9994438674374818,
        }
        for key, value in expected.items():
            self.assertAlmostEqual(
                self.worlds[key]["realized_over_planned"], value,
                places=10, msg=str(key))
            self.assertLess(abs(self.worlds[key]["realized_over_planned"]
                                - 1.0), 0.003, msg=str(key))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
