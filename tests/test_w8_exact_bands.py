"""Pins for the tick-127 exact-bands module (tools/w8_exact_bands.py).

Every number is byte-reproducible: the module has NO random component at
all (exact binomial sums + bisection; there is nothing to seed). The
first-draft upper-bound bisection solved the wrong tail (target alpha/2
instead of 1-alpha/2 on the increasing form 1-cdf); the k=0 analytic
check and the 5/10 textbook reference caught it BEFORE any pin landed —
the analytic-identity and defining-equation pins below are the guard
that keeps that bug dead. Wilson half-widths re-pin the tick-126 values
(block8 0.016578, arm4 0.091624) from an independent module."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from w8_exact_bands import (  # noqa: E402
    ALPHA_FAMILY,
    _cp_bounds_factory,
    _wilson_bounds_factory,
    assert_bounds_monotone,
    clopper_pearson,
    real_data_readout,
    validate_solver,
    width_premium_study,
    world_coverage,
)


class SharedComputations(unittest.TestCase):
    """One shared measurement pass for all pin classes (byte-identical)."""

    @classmethod
    def setUpClass(cls):
        cls.V = validate_solver()
        cls.R = real_data_readout()
        cls.W = world_coverage()
        cls.S = width_premium_study()


class SolverValidation(SharedComputations):
    def test_analytic_edge_cases(self):
        a = self.V["analytic"]
        for n in (1, 2, 7, 153, 4999):
            self.assertAlmostEqual(a[f"upper_k0_n{n}"],
                                   1.0 - 0.025 ** (1.0 / n), places=12)
            self.assertAlmostEqual(a[f"lower_kn_n{n}"],
                                   0.025 ** (1.0 / n), places=12)
        self.assertAlmostEqual(a["cp_0_1"][1], 0.975, places=12)
        self.assertAlmostEqual(a["cp_1_1"][0], 0.025, places=12)

    def test_textbook_reference_5_of_10(self):
        # Clopper-Pearson 95% for 5/10: [0.1871, 0.8129] (standard tables).
        lo, hi = clopper_pearson(5, 10, 0.05)
        self.assertAlmostEqual(lo, 0.18708602844740266, places=12)
        self.assertAlmostEqual(hi, 0.8129139715525973, places=12)

    def test_contested_arm4_reference(self):
        lo, hi = clopper_pearson(106, 153, 0.05 / 4)
        self.assertAlmostEqual(lo, 0.5916360852431162, places=10)
        self.assertAlmostEqual(hi, 0.7823016906034694, places=10)

    def test_defining_equations_symmetry(self):
        self.assertLess(self.V["max_residual"], 1e-10)
        for r in self.V["residuals"]:
            self.assertLess(r["lo_resid"], 1e-10)
            self.assertLess(r["hi_resid"], 1e-10)
            self.assertLess(r["sym_resid"], 1e-10)

    def test_bounds_monotone_in_k(self):
        # Monotonicity is a theorem for CP (P(X>=k|p) decreases in k at
        # fixed p, so lo must rise; likewise hi), and is scanned, not
        # assumed, for Wilson. Step scans bound cost at the n~5000 strata.
        self.assertTrue(assert_bounds_monotone(_cp_bounds_factory(153, 0.05), 153))
        self.assertTrue(assert_bounds_monotone(
            _cp_bounds_factory(4999, 0.05 / 6), 4999, step=50))
        self.assertTrue(assert_bounds_monotone(
            _wilson_bounds_factory(4999, 2.6382572734772957), 4999))


class RealDataPins(SharedComputations):
    PREMIUMS = {
        "six_window": {
            "block8": 1.006193428014, "block9": 1.006267918413,
            "block10": 1.006248372893, "block11": 1.006228456370,
            "block12": 1.006254657325, "block13": 1.006258908842},
        "contested_four_arm": {
            "arm3": 1.021720002559, "arm4": 1.040480187988,
            "arm6": 1.022075705217, "arm7": 1.021538902072},
    }

    def test_premiums_pinned(self):
        for fam, rows in self.PREMIUMS.items():
            for row in self.R[fam]["rows"]:
                self.assertAlmostEqual(row["premium"], rows[row["label"]],
                                       places=9, msg=row["label"])

    def test_wilson_half_widths_repin_tick126(self):
        by_label = {r["label"]: r for r in self.R["six_window"]["rows"]}
        self.assertAlmostEqual(by_label["block8"]["wilson_half_width"],
                               0.016577888572, places=10)
        by_label4 = {r["label"]: r for r in self.R["contested_four_arm"]["rows"]}
        self.assertAlmostEqual(by_label4["arm4"]["wilson_half_width"],
                               0.091623851930, places=10)

    def test_cp_bounds_and_half_widths_pinned(self):
        by_label = {r["label"]: r for r in self.R["six_window"]["rows"]}
        b8 = by_label["block8"]
        self.assertAlmostEqual(b8["cp"][0], 0.712035645552, places=10)
        self.assertAlmostEqual(b8["cp"][1], 0.745396770615, places=10)
        self.assertAlmostEqual(b8["cp_half_width"], 0.016680562532, places=10)
        by_label4 = {r["label"]: r for r in self.R["contested_four_arm"]["rows"]}
        a4 = by_label4["arm4"]
        self.assertAlmostEqual(a4["cp"][0], 0.591636085243, places=10)
        self.assertAlmostEqual(a4["cp"][1], 0.782301690603, places=10)
        self.assertAlmostEqual(a4["cp_half_width"], 0.095332802680, places=10)

    def test_every_stratum_cp_wider_than_wilson(self):
        for fam in ("six_window", "contested_four_arm"):
            for row in self.R[fam]["rows"]:
                self.assertGreater(row["cp_half_width"],
                                   row["wilson_half_width"], row["label"])


class WorldCoveragePins(SharedComputations):
    def test_family_coverage_pinned(self):
        a, b = self.W["A_homogeneous_six_window"], self.W["B_contested_four_arm"]
        self.assertAlmostEqual(a["family_wilson"], 0.951427533107, places=9)
        self.assertAlmostEqual(a["family_cp"], 0.953621264948, places=9)
        self.assertAlmostEqual(b["family_wilson"], 0.954065145973, places=9)
        self.assertAlmostEqual(b["family_cp"], 0.961293574133, places=9)

    def test_tick124_mc_cross_check_inside_error_bar(self):
        # Two independent computations of the same number: the tick-124
        # 4000-rep MC realizations vs these closed-form products.
        for world in self.W.values():
            self.assertLess(abs(world["mc_minus_exact_wilson"]), 0.0068)
        self.assertAlmostEqual(
            self.W["A_homogeneous_six_window"]["mc_minus_exact_wilson"],
            -0.001677533, places=9)
        self.assertAlmostEqual(
            self.W["B_contested_four_arm"]["mc_minus_exact_wilson"],
            -0.001315146, places=9)

    def test_cp_guarantee_holds_per_stratum(self):
        for world in self.W.values():
            self.assertGreaterEqual(world["min_cp"],
                                    1.0 - world["alpha_m"] - 1e-9)

    def test_wilson_under_nominal_per_stratum_direction(self):
        # The honest content of the tick-124 in-expectation caveat: the
        # WORST Wilson stratum sits below its nominal per-stratum level in
        # both worlds (family still >= 0.95 there via over-coverage
        # elsewhere - measured, not guaranteed).
        a, b = self.W["A_homogeneous_six_window"], self.W["B_contested_four_arm"]
        self.assertLess(a["min_wilson"], 1.0 - a["alpha_m"])
        self.assertLess(b["min_wilson"], 1.0 - b["alpha_m"])
        self.assertAlmostEqual(a["min_wilson"], 0.991601675972, places=9)
        self.assertAlmostEqual(b["min_wilson"], 0.986749872001, places=9)
        for world in self.W.values():
            self.assertGreaterEqual(world["family_wilson"], 0.95 - 1e-9)

    def test_family_premium_ratio_pinned(self):
        self.assertAlmostEqual(
            self.W["A_homogeneous_six_window"]["premium_family_ratio"],
            1.002305726673, places=9)
        self.assertAlmostEqual(
            self.W["B_contested_four_arm"]["premium_family_ratio"],
            1.007576451347, places=9)


class WidthPremiumStudy(SharedComputations):
    PREMIUMS = {
        (0.5, 153): 1.039657900157, (0.5, 612): 1.017698602372,
        (0.5, 1250): 1.011896467631, (0.5, 2500): 1.008171816053,
        (22111 / 29989, 153): 1.039078465243,
        (22111 / 29989, 612): 1.018587743920,
        (22111 / 29989, 1250): 1.012771047284,
        (22111 / 29989, 2500): 1.008911995470,
        (106 / 153, 153): 1.040465189990,
        (106 / 153, 612): 1.018991000746,
        (106 / 153, 1250): 1.012994688381,
        (106 / 153, 2500): 1.009042488201,
    }

    def test_premium_rows_pinned(self):
        for row in self.S:
            key = (row["p"], row["n"])
            self.assertAlmostEqual(row["premium"], self.PREMIUMS[key],
                                   places=9, msg=str(key))

    def test_premium_decays_with_n_and_stays_above_one(self):
        by_p = {}
        for row in self.S:
            by_p.setdefault(row["p"], []).append(row)
        for p, rows in by_p.items():
            prems = [r["premium"] for r in sorted(rows, key=lambda r: r["n"])]
            self.assertGreater(prems[0], 1.0)
            for hi_n, lo_n in zip(prems, prems[1:]):
                self.assertLess(lo_n, hi_n, msg=f"p={p}")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
