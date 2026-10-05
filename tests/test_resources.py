"""Checks for the programme's load-bearing resource arithmetic.

These assertions are the record: if one fails, a note somewhere is wrong
(or physics changed). Tolerances are deliberate — inputs are approximate
(330 g/mol per nt, 5.97e27 g Earth), outputs are not false precision.
"""

import unittest

from molasp import resources as R


class TestMassArithmetic(unittest.TestCase):
    def test_library_mass_coefficient(self):
        # Draft: 2^n * n * 2.74e-20 g for ell = 50. Computed:
        coeff = R.mass_per_assignment_grams(50)
        self.assertLess(abs(coeff - 2.74e-20) / 2.74e-20, 0.005)

    def test_earth_mass_ceiling_is_150(self):
        # Draft: brute-force library hits Earth mass at n ~ 150.
        self.assertEqual(R.max_variables_for_mass(R.EARTH_MASS_G), 150)


class TestVesselArithmetic(unittest.TestCase):
    def test_vessel_capacity_1uM(self):
        # Draft: 100 uL at 1 uM holds 6.0e13 = 2^45.8 molecules.
        self.assertAlmostEqual(R.vessel_molecules(100e-6, 1e-6), 6.0e13, delta=0.05e13)
        self.assertAlmostEqual(R.bits(R.vessel_molecules(100e-6, 1e-6)), 45.8, places=1)

    def test_vessel_capacity_10nM(self):
        # Draft: at 10 nM the same well holds 2^39.1.
        self.assertAlmostEqual(R.bits(R.vessel_molecules(100e-6, 10e-9)), 39.1, places=1)

    def test_brute_force_saturation_near_40(self):
        # Draft: a standard well saturates brute force at n ~ 40 (10 nM).
        self.assertEqual(R.brute_force_ceiling_n(100e-6, 10e-9), 39)

    def test_1536_well_plate_bits(self):
        # Draft: partitioning across 1536 wells adds 10.6 bits at best.
        self.assertAlmostEqual(R.plate_bits(1536), 10.6, places=1)


class TestPruningArithmetic(unittest.TestCase):
    def test_correction_A_saving_at_60_is_1e2_not_1e4(self):
        # Draft claimed (2/1.8393)^60 ~ 1e4. It is ~1.5e2. The draft's
        # own scaling section ("differ by only 1.087^n") implies this
        # smaller number; the 1e4 passage is the error.
        saving = R.pruning_ratio(60)
        self.assertGreater(saving, 1.0e2)
        self.assertLess(saving, 2.0e2)
        self.assertLess(saving, 1.0e4)  # the documented correction

    def test_correction_A_crossover_for_1e4_is_near_110(self):
        # The 10^4 saving arrives at n ~ 110, not n = 60.
        n = R.n_for_ratio(1.0e4)
        self.assertGreater(n, 105.0)
        self.assertLess(n, 115.0)

    def test_correction_B_extra_variables_at_earth_mass(self):
        # Draft: pruning buys "roughly ten" extra variables at the
        # Earth-mass line. Computed: n_b = 150 * log2/log(1.8393) ~ 170.5,
        # i.e. ~20 extra variables.
        extra = R.extra_variables(150.0)
        self.assertGreater(extra, 19.0)
        self.assertLess(extra, 22.0)


class TestErrorBudget(unittest.TestCase):
    def test_proofread_assembly_budget(self):
        # Draft: eps0 = 1.3e-3, k = 2 -> N_max ~ 6e4 at delta = 0.1.
        nmax = R.max_assembly_size(delta=0.1, eps0=1.3e-3, k=2)
        self.assertGreater(nmax, 5.5e4)
        self.assertLess(nmax, 6.5e4)


if __name__ == "__main__":
    unittest.main()
