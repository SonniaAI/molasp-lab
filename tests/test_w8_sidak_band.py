"""Pins for the tick-125 exact-Sidak simultaneous-band calibration
(tools/w8_sidak_band.py). Numbers are byte-reproducible from the pinned
seeds (20261013 / 20261014) on the stdlib-only sampler; the paired-dataset
proof is the first_draw_row fingerprint equality with the tick-124 pins
AND the recomputed tick-124 coverage/width values."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from w8_simultaneous_band import bonferroni_z  # noqa: E402
from w8_sidak_band import (  # noqa: E402
    real_data_readout,
    run,
    sidak_z,
)


class SidakZ(unittest.TestCase):
    def test_z_pins(self):
        # m=1: Sidak degenerates to the plain two-sided 95% z.
        self.assertAlmostEqual(sidak_z(1), 1.959963984540054, places=12)
        self.assertAlmostEqual(sidak_z(6), 2.6310382845367783, places=12)
        self.assertAlmostEqual(sidak_z(4), 2.4909151310191397, places=12)

    def test_ordering_vs_bonferroni(self):
        # Sidak is strictly tighter than Bonferroni for m >= 2 but the
        # gap is tiny at these m (the tick-125 headline).
        for m in range(2, 9):
            self.assertLess(sidak_z(m), bonferroni_z(m))
        self.assertAlmostEqual(bonferroni_z(6) / sidak_z(6),
                               1.0027437795118377, places=10)
        self.assertAlmostEqual(bonferroni_z(4) / sidak_z(4),
                               1.0027260436570777, places=10)

    def test_validation(self):
        for bad in (0, -1, 2.0, True):
            with self.assertRaises(ValueError):
                sidak_z(bad)
        with self.assertRaises(ValueError):
            sidak_z(6, family=1.5)


class SidakWorlds(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.worlds = {res["world"]: res for res in run()}

    def test_paired_datasets_fingerprint(self):
        """Draw rows are the tick-123/124 ones, byte-identical."""
        self.assertEqual(
            self.worlds["A_homogeneous_six_window"]["first_draw_row"],
            [3695, 3658, 3722, 3728, 3671, 3682])
        self.assertEqual(
            self.worlds["B_contested_four_arm"]["first_draw_row"],
            [381, 101, 396, 374])

    def test_tick124_values_reproduce_from_paired_data(self):
        """The tick-124 measurements recompute exactly on the shared
        datasets (nominal non-simultaneity + Bonferroni repair)."""
        a = self.worlds["A_homogeneous_six_window"]
        b = self.worlds["B_contested_four_arm"]
        self.assertAlmostEqual(a["all_strata_coverage_nominal95"],
                               0.73675, places=12)
        self.assertAlmostEqual(b["all_strata_coverage_nominal95"],
                               0.81625, places=12)
        self.assertAlmostEqual(a["all_strata_coverage_bonferroni"],
                               0.94975, places=12)
        self.assertAlmostEqual(b["all_strata_coverage_bonferroni"],
                               0.95275, places=12)
        self.assertAlmostEqual(a["width_ratio_bonf_over_nominal"],
                               1.345752050417358, places=12)
        self.assertAlmostEqual(b["width_ratio_bonf_over_nominal"],
                               1.2700487106225113, places=12)

    def test_world_a_sidak_pins(self):
        a = self.worlds["A_homogeneous_six_window"]
        self.assertAlmostEqual(a["z_sidak"], 2.6310382845367783,
                               places=12)
        self.assertAlmostEqual(a["all_strata_coverage_sidak"], 0.949,
                               places=12)
        self.assertAlmostEqual(a["per_stratum_coverage_sidak_min"],
                               0.9895, places=12)
        self.assertAlmostEqual(a["mean_per_stratum_width_nominal"],
                               0.024394190338389524, places=12)
        self.assertAlmostEqual(a["mean_per_stratum_width_bonferroni"],
                               0.032828531666159004, places=12)
        self.assertAlmostEqual(a["mean_per_stratum_width_sidak"],
                               0.03273879215450366, places=12)
        self.assertAlmostEqual(a["width_ratio_sidak_over_nominal"],
                               1.3420733256714041, places=12)
        self.assertAlmostEqual(a["width_ratio_bonf_over_sidak"],
                               1.0027410758231958, places=12)

    def test_world_b_sidak_pins(self):
        b = self.worlds["B_contested_four_arm"]
        self.assertAlmostEqual(b["z_sidak"], 2.4909151310191397,
                               places=12)
        self.assertAlmostEqual(b["all_strata_coverage_sidak"], 0.95275,
                               places=12)
        self.assertAlmostEqual(b["per_stratum_coverage_sidak_min"],
                               0.9865, places=12)
        self.assertAlmostEqual(b["mean_per_stratum_width_sidak"],
                               0.11712088787994598, places=12)
        self.assertAlmostEqual(b["width_ratio_sidak_over_nominal"],
                               1.2666559918408227, places=12)
        self.assertAlmostEqual(b["width_ratio_bonf_over_sidak"],
                               1.0026784847689847, places=12)

    def test_honest_claims(self):
        """Realized family level of Wilson-at-z_Sidak is within MC error
        of the 0.95 target in both worlds (Sidak is exact in expectation
        only under exact per-stratum intervals + independence); width
        ordering nominal < Sidak < Bonferroni; and the Bonferroni premium
        over independence-exact Sidak is under 0.3% at these m."""
        for res in self.worlds.values():
            self.assertLess(abs(res["all_strata_coverage_sidak"]
                                - 0.95), 0.0068)
            self.assertLess(res["mean_per_stratum_width_nominal"],
                            res["mean_per_stratum_width_sidak"])
            self.assertLess(res["mean_per_stratum_width_sidak"],
                            res["mean_per_stratum_width_bonferroni"])
            self.assertLess(res["width_ratio_bonf_over_sidak"], 1.003)
            # Bonferroni coverage is at least Sidak's on these datasets.
            self.assertGreaterEqual(res["all_strata_coverage_bonferroni"],
                                    res["all_strata_coverage_sidak"])


class RealDataReadout(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.groups = {g["group"]: g for g in real_data_readout()}

    def test_six_window_pins(self):
        g = self.groups["six_window"]
        self.assertEqual(g["strata"], 6)
        self.assertAlmostEqual(g["z_sidak"], 2.6310382845367783,
                               places=12)
        expected = {
            "block8": (0.7120966218653122, 0.7451617681504628),
            "block9": (0.7250807427718698, 0.757644027970639),
            "block10": (0.7218738098160563, 0.7545618652331457),
            "block11": (0.7184099207812423, 0.7512337991519541),
            "block12": (0.7228380479466041, 0.7554910502146401),
            "block13": (0.7233402287535038, 0.7559796219793815),
        }
        for row in g["rows"]:
            lo, hi = expected[row["stratum"]]
            self.assertAlmostEqual(row["sidak95"][0], lo, places=12)
            self.assertAlmostEqual(row["sidak95"][1], hi, places=12)
            # width ordering nominal < sidak < bonferroni expressed
            # via endpoints: bigger z => lower lo, higher hi
            self.assertGreater(row["nominal95"][0], row["sidak95"][0])
            self.assertLess(row["nominal95"][1], row["sidak95"][1])
            self.assertGreater(row["sidak95"][0], row["bonferroni95"][0])
            self.assertLess(row["sidak95"][1], row["bonferroni95"][1])
            self.assertAlmostEqual(row["width_bonf_over_sidak"],
                                   1.0027411, places=6)

    def test_contested_four_arm_pins(self):
        g = self.groups["contested_four_arm"]
        self.assertEqual(g["strata"], 4)
        self.assertAlmostEqual(g["z_sidak"], 2.4909151310191397,
                               places=12)
        expected = {
            "arm3": (0.6988980309197369, 0.7949733627057917),
            "arm4": (0.5939132255421923, 0.77667894601104),
            "arm6": (0.7284554398083134, 0.8207295499032743),
            "arm7": (0.6794219619648217, 0.7778184776376803),
        }
        for row in g["rows"]:
            lo, hi = expected[row["stratum"]]
            self.assertAlmostEqual(row["sidak95"][0], lo, places=12)
            self.assertAlmostEqual(row["sidak95"][1], hi, places=12)
            # descriptive only: contested pool stays REPORTED-NOT-CLAIMABLE
            self.assertLess(row["width_bonf_over_sidak"], 1.003)


if __name__ == "__main__":
    unittest.main()
