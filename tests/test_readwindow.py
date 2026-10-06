"""CI pinning for design rule (c) — read-window arithmetic (tick 10).

Pins the tick 9 corrected closed form (QA verdict d1997431) so the
compiler invariant cannot silently drift back to the flipped-convention
prose: expected breaks of a trapped pair under the grid protocol are
800 * e^-(Gse - dG) with the GRID convention dG = Gmc - Gse (standard
kTAM uses dG = Gse - Gmc; the flip is the error this file exists to
prevent), and survival is exp(-breaks). Also pins the tick 9
reconciliation triple and the rule-(c) read_window() contract.
"""

import math
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from molasp import readwindow as rw  # noqa: E402

GSE = 9.0  # grid constant, instrument_mc.py

# Tick 9 grid: (dG, window t2 first-passage, measured unfounded decode)
TICK9_GRID = [
    (0.5, 0.2646, 0.222),
    (2.0, 0.1381, 0.058),
    (4.0, 0.0276, 0.000),
]


class TestTick9ClosedForm(unittest.TestCase):
    def test_expected_breaks(self):
        # 800 * e^-(9 - dG): 0.163 / 0.730 / 5.390
        for dg, expected in [(0.5, 0.163), (2.0, 0.730), (4.0, 5.390)]:
            self.assertAlmostEqual(
                rw.trap_expected_breaks(GSE, dg), expected, places=3)

    def test_survival(self):
        # e^{-breaks}: .850 / .482 / .00455 — the log's .85/.48/.005
        for dg, expected in [(0.5, 0.850), (2.0, 0.482), (4.0, 0.00455)]:
            self.assertAlmostEqual(rw.trap_survival(GSE, dg), expected, places=3)

    def test_grid_convention_not_standard_ktam(self):
        # Regression pin for the d1997431 prose slip: under the STANDARD
        # convention (dG = Gse - Gmc) the dG=0.5 value would be
        # 800*e^-9.5 = 0.0664 — a factor 2.4 away. If this test fails
        # after an "innocent refactor", a convention was flipped.
        grid = rw.trap_expected_breaks(GSE, 0.5)
        standard = 2.0 * rw.T_READ_MULTIPLIER * math.exp(-(GSE + 0.5))
        self.assertGreater(grid, 2.0 * standard)
        self.assertNotAlmostEqual(grid, standard, delta=0.05)

    def test_conventions_agree(self):
        # The general per-site form reproduces the trap closed form when
        # instantiated at the grid protocol (2 sites at b=2, T=400*e^Gmc).
        for dg, _, _ in TICK9_GRID:
            gmc = GSE + dg
            t_read = rw.T_READ_MULTIPLIER * math.exp(gmc)
            self.assertAlmostEqual(
                rw.breaks_over_window(GSE, 2, 2, t_read),
                rw.trap_expected_breaks(GSE, dg), places=12)

    def test_reconciliation_triple(self):
        # window t2 (passage) x survival = .225 / .067 / .0001
        for (dg, t2, measured), recon in zip(TICK9_GRID, (0.225, 0.067, 0.0001)):
            product = t2 * rw.trap_survival(GSE, dg)
            if recon >= 0.001:
                self.assertAlmostEqual(product, recon, places=2)
            else:
                self.assertLess(product, 1.3e-4)


class TestReadWindowRule(unittest.TestCase):
    def test_no_weak_fabric_unconstrained(self):
        w = rw.read_window(GSE, 11.0, n_sites=6, n_weak=0)
        self.assertTrue(w["feasible"])
        self.assertEqual(w["t_max"], math.inf)

    def test_t_max_shrinks_with_weak_count(self):
        a = rw.read_window(GSE, 11.0, 6, n_weak=4)["t_max"]
        b = rw.read_window(GSE, 11.0, 6, n_weak=8)["t_max"]
        self.assertLess(b, a)

    def test_infeasible_flag_flips(self):
        # At grid kinetics (Gse=9, dG=2) ten weakly held sites leave no
        # window at all: growth alone outlives the 90%-survival bound.
        # This is rule (c)'s content: the compiler must refuse or raise
        # the barrier, not silently extend the wait.
        bad = rw.read_window(GSE, 11.0, n_sites=6, n_weak=10)
        self.assertFalse(bad["feasible"])
        self.assertLess(bad["t_max"], bad["t_grow"])
        # Raising the effective barrier (proofreading regime, Gse=12)
        # makes the same weak fabric readable at 90%.
        ok = rw.read_window(12.0, 13.0, n_sites=6, n_weak=10)
        self.assertTrue(ok["feasible"])
        self.assertGreaterEqual(ok["t_max"], ok["t_grow"])

    def test_protocol_window_matches_closed_form(self):
        # Consistency: the tick-9 protocol window (400*e^Gmc) is exactly
        # the t_max one trapped pair (n_weak=2) gets when the survival
        # target is set to the tick-9 closed-form survival.
        s = rw.trap_survival(GSE, 0.5)
        w = rw.read_window(GSE, 9.5, n_sites=6, n_weak=2, target_survival=s)
        self.assertAlmostEqual(
            w["t_max"] / (rw.T_READ_MULTIPLIER * math.exp(9.5)), 1.0, places=6)

    def test_t_grow_tracks_exp_gmc(self):
        w1 = rw.read_window(GSE, 10.0, 6, n_weak=2)["t_grow"]
        w2 = rw.read_window(GSE, 11.0, 6, n_weak=2)["t_grow"]
        self.assertAlmostEqual(w2 / w1, math.e, places=9)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            rw.read_window(GSE, 11.0, 6, n_weak=1, target_survival=1.0)
        with self.assertRaises(ValueError):
            rw.breaks_over_window(GSE, 1, b=0, t_read=1.0)


if __name__ == "__main__":
    unittest.main()
