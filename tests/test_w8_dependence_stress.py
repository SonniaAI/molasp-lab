"""Pins for the tick-128 dependence stress module (tools/w8_dependence_stress.py).

Every number is byte-reproducible: NO random component anywhere (exact
binomial sums, CDF-identity crossing searches, deterministic trapezoid
grid — there is nothing to seed). Two catches from this tick are pinned
as permanent guards:

1. SEED UNDERFLOW (catch #5 in the measure-then-pin streak): the shared
   w8_exact_bands helpers binom_cdf/binom_sf_ge return 0.0 for deep-tail
   seeds (pmf(j_start) underflows to 0.0 and the O(1) recurrence can
   never recover) — pinned below as the documented cliff, together with
   the proof that this module's assert-bracketed +-9*sigma window makes
   the SAME quantity exact.
2. The exact families at zero drift reproduce tick 127 bit-for-bit
   (Bonferroni-Wilson) / to 1e-12 (CP via the independent fast path),
   and give the FIRST exact families for plain Wilson-95 and
   Sidak-Wilson (tick 124/125 had MC realizations only).

Headline pins: Sidak-Wilson family is BELOW nominal in world A at the
design rates themselves (0.9499025929034176 < 0.95 — the <=0.27% width
saving never bought the floor even with independence holding); in world
B Sidak equals Bonferroni BIT-IDENTICALLY at s=0 (coverage is a step
function of z; no stratum jumps between z=2.49092 and z=2.49771) and
oscillates about nominal under drift, first crossing s*=0.0297266.
Bonferroni-Wilson never breaches inside 99.5% of the feasible range in
either world (score intervals self-center: family flatness <= 0.0031).
Bonferroni-CP verifies its structural guarantee POINTWISE: per-stratum
coverage >= 1-alpha/m at every scanned (rate, shock, node) — world A
margin +7.3e-6, world B +1.7e-4 — and worst-mode floors 0.9521453 /
0.9544318 sit above (1-alpha/m)^m."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from w8_census_sim import _world_a_rates, _world_b_rates  # noqa: E402
from w8_dependence_stress import (  # noqa: E402
    ALPHA_FAMILY,
    _coverage,
    breach_threshold,
    cp_accept_window,
    family_shocked,
    world_scan,
)
from w8_exact_bands import (  # noqa: E402
    _cp_bounds_factory,
    binom_sf_ge,
    exact_coverage,
    world_coverage,
)


class DependenceStressPins(unittest.TestCase):
    """One shared measurement pass (byte-identical across all tests)."""

    @classmethod
    def setUpClass(cls):
        cls.rates_a, cls.ns_a = _world_a_rates()
        cls.rates_b, cls.ns_b = _world_b_rates()
        cls.A = world_scan("A_homogeneous_six_window", cls.rates_a, cls.ns_a)
        cls.B = world_scan("B_contested_four_arm", cls.rates_b, cls.ns_b)
        cls.T127 = world_coverage()  # independent tick-127 computation

    # -- method validation ------------------------------------------------

    def test_cp_fast_path_matches_slow_bounds_crossing(self):
        """CDF-identity window == tick-127 bounds-crossing search."""
        for m, n, p in ((4, 153, 106.0 / 153.0), (6, 4999, 0.753304),
                        (4, 500, 0.75), (6, 4999, 22111.0 / 29989.0)):
            fast = _coverage("bonferroni_cp", m, n, p)
            slow = exact_coverage(_cp_bounds_factory(n, ALPHA_FAMILY / m),
                                  n, p)
            self.assertAlmostEqual(fast, slow, delta=1e-12)
            self.assertGreaterEqual(fast, 1.0 - ALPHA_FAMILY / m - 1e-9)

    def test_seed_underflow_hazard_fenced(self):
        """The shared helpers' deep-tail cliff -- REPAIRED tick 129.

        Pre-repair, binom_sf_ge(2500, 4999, 0.753304) returned 0.0 (seed
        pmf e^-745.25 -> 0.0, recurrence stays 0) where the truth is
        1 - ~4e-12 (measured two ways: anchored re-seed inside
        w8_exact_bands, and an independent per-term-lgamma logsumep --
        the "true ~0.9958" in the original tick-128 note was itself
        wrong). The anchored re-seed fixes the class; the assert-bracketed
        +-9*sigma window stays as defense in depth, so the same quantity
        through cp_accept_window remains exact either way.
        """
        self.assertEqual(binom_sf_ge(2500, 4999, 0.753304), 1.0)
        kh, kl = cp_accept_window(4999, ALPHA_FAMILY / 6, 0.753304)
        self.assertLessEqual(kh, kl - 1)
        self.assertGreaterEqual(
            _coverage("bonferroni_cp", 6, 4999, 0.753304),
            1.0 - ALPHA_FAMILY / 6 - 1e-9)

    def test_boundary_rate_rules(self):
        """p>=1: k=n surely (CP hi=1 covers, Wilson hi<1 misses); p<=0 covers."""
        self.assertEqual(_coverage("bonferroni_cp", 6, 4999, 1.0), 1.0)
        self.assertEqual(_coverage("plain_wilson95", 6, 4999, 1.0), 0.0)
        self.assertEqual(_coverage("bonferroni_cp", 6, 4999, 0.0), 1.0)
        self.assertEqual(_coverage("plain_wilson95", 6, 4999, 0.0), 1.0)

    def test_trapezoid_convergence(self):
        """QUADRATURE BAR, not smooth convergence: the integrand is a step
        function of the rate (exact count-based coverage), so trapezoid
        error floors around 1e-4 and oscillates with how nodes land on
        the steps (world A d(41,121)=1.47e-5 but d(121,361)=2.52e-5).
        Measured worst 41-vs-121 delta across worlds/calibrations at
        s=0.05 is 2.41e-4 — that is the honest uncertainty of every
        grid-averaged number here. All breach conclusions hold with
        margin >= 4x this bar (narrowest: Bonferroni-Wilson interior
        minimum 0.950964, margin 9.6e-4); s=0 identities carry NO
        quadrature error (single node)."""
        f41 = family_shocked(self.rates_a, self.ns_a,
                             "bonferroni_wilson", 0.05, nodes=41)
        f121 = family_shocked(self.rates_a, self.ns_a,
                              "bonferroni_wilson", 0.05, nodes=121)
        d = abs(f41["family_mean"] - f121["family_mean"])
        self.assertAlmostEqual(d, 1.4730786223715597e-05, delta=1e-9)
        self.assertLess(d, 2.5e-4)

    # -- zero-drift identities (first EXACT families for plain/Sidak) ----

    def test_s0_identity_with_tick127(self):
        aw = family_shocked(self.rates_a, self.ns_a, "bonferroni_wilson", 0.0)
        ac = family_shocked(self.rates_a, self.ns_a, "bonferroni_cp", 0.0)
        self.assertEqual(aw["family_mean"],
                         self.T127["A_homogeneous_six_window"]["family_wilson"])
        self.assertAlmostEqual(
            ac["family_mean"],
            self.T127["A_homogeneous_six_window"]["family_cp"], delta=1e-12)
        bw = family_shocked(self.rates_b, self.ns_b, "bonferroni_wilson", 0.0)
        bc = family_shocked(self.rates_b, self.ns_b, "bonferroni_cp", 0.0)
        self.assertEqual(bw["family_mean"],
                         self.T127["B_contested_four_arm"]["family_wilson"])
        self.assertAlmostEqual(
            bc["family_mean"],
            self.T127["B_contested_four_arm"]["family_cp"], delta=1e-12)

    def test_s0_plain_wilson_families(self):
        self.assertAlmostEqual(
            self.A["s0_summary"]["plain_wilson95"], 0.7354224045110968,
            delta=1e-12)
        self.assertAlmostEqual(
            self.B["s0_summary"]["plain_wilson95"], 0.8194013046888571,
            delta=1e-12)
        self.assertLess(self.A["s0_summary"]["plain_wilson95"], 0.95)
        self.assertLess(self.B["s0_summary"]["plain_wilson95"], 0.95)
        # tick-124 MC agreement, 2-sigma bars at 4000 reps
        self.assertLessEqual(
            abs(self.A["s0_summary"]["plain_wilson95"] - 0.73675), 0.01395)
        self.assertLessEqual(
            abs(self.B["s0_summary"]["plain_wilson95"] - 0.81625), 0.01216)

    def test_s0_sidak_world_a_below_nominal(self):
        b = self.A["calibrations"]["sidak_wilson"]["breach"]
        self.assertTrue(b["breached_at_zero"])
        self.assertEqual(b["family_s0"], 0.9499025929034176)
        self.assertLess(b["family_s0"], 0.95)
        # tick-125 MC realization 0.949 sits inside its own 2-sigma bar
        self.assertLessEqual(abs(b["family_s0"] - 0.949), 0.0068)

    def test_s0_sidak_world_b_bitwise_equal_bonferroni(self):
        """Coverage is a STEP FUNCTION of z: no world-B stratum's acceptance
        window jumps between z_sidak=2.49092 and z_bonferroni=2.49771, so
        the two families coincide to the last bit."""
        s0 = self.B["s0_summary"]
        self.assertEqual(s0["sidak_wilson"], s0["bonferroni_wilson"])
        self.assertEqual(s0["sidak_wilson"], 0.9540651459728295)
        # tick-125 MC realization 0.95275 inside the 2-sigma bar
        self.assertLessEqual(abs(s0["sidak_wilson"] - 0.95275), 0.0068)

    # -- under drift: who keeps the 0.95 floor ----------------------------

    def test_bonferroni_wilson_no_interior_breach(self):
        for w, cap in ((self.A, 0.9512047527976644),
                       (self.B, 0.9518504378079542)):
            b = w["calibrations"]["bonferroni_wilson"]["breach"]
            self.assertTrue(b["never_within_feasible"])
            self.assertAlmostEqual(b["family_at_cap"], cap, delta=1e-12)
            fams = [r["family_mean"] for r in
                    w["calibrations"]["bonferroni_wilson"]["scan"]]
            self.assertLess(max(fams) - min(fams), 0.004)  # self-centering
        self.assertAlmostEqual(
            max(r["family_mean"] for r in
                self.A["calibrations"]["bonferroni_wilson"]["scan"])
            - min(r["family_mean"] for r in
                  self.A["calibrations"]["bonferroni_wilson"]["scan"]),
            0.0004620350738282486, delta=1e-12)

    def test_cp_never_breaches_structural_floor(self):
        for w, floor, cap in ((self.A, 0.9521453017662579, 0.9538542448186497),
                              (self.B, 0.9544317739730184, 0.959916860228442)):
            b = w["calibrations"]["bonferroni_cp"]["breach"]
            self.assertTrue(b["never_within_feasible"])
            self.assertAlmostEqual(b["family_at_cap"], cap, delta=1e-12)
            wm = min(r["family_worst_mode"] for r in
                     w["calibrations"]["bonferroni_cp"]["scan"])
            self.assertAlmostEqual(wm, floor, delta=1e-12)
            self.assertGreaterEqual(wm, w["structural_floor"] - 1e-12)
            self.assertGreaterEqual(wm, 0.95)

    def test_cp_per_stratum_pointwise_guarantee(self):
        """CP coverage >= 1-alpha/m at EVERY scanned rate — world A margin
        +7.3e-6 (the guarantee boundary, touched almost exactly)."""
        self.assertAlmostEqual(self.A["cp_min_any_stratum"],
                               0.9916739489162382, delta=1e-12)
        self.assertGreaterEqual(self.A["cp_min_any_stratum"],
                                self.A["cp_nominal_per_stratum"] - 1e-9)
        self.assertAlmostEqual(self.B["cp_min_any_stratum"],
                               0.9876698835772482, delta=1e-12)
        self.assertGreaterEqual(self.B["cp_min_any_stratum"],
                                self.B["cp_nominal_per_stratum"] - 1e-9)

    def test_structural_floor_values(self):
        self.assertEqual(self.A["structural_floor"],
                         (1.0 - ALPHA_FAMILY / 6.0) ** 6)
        self.assertAlmostEqual(self.A["structural_floor"],
                               0.9510301646897641, delta=1e-15)
        self.assertEqual(self.B["structural_floor"],
                         (1.0 - ALPHA_FAMILY / 4.0) ** 4)
        self.assertAlmostEqual(self.B["structural_floor"],
                               0.9509297119140627, delta=1e-15)

    def test_sidak_world_b_first_crossing_bracket(self):
        """First crossing on the scanned path, bisected. QUADRATURE BAR
        honesty: grid-averaged families carry ~2.4e-4 uncertainty, which
        maps to ~+-0.002 in s at the local curve slope — the meaningful
        statement is s* ~ 0.030 (an order of magnitude inside the
        feasible range), not the 4th decimal."""
        b = self.B["calibrations"]["sidak_wilson"]["breach"]
        self.assertAlmostEqual(b["s_star"], 0.029726562499999998, delta=1e-12)
        self.assertAlmostEqual(b["family_lo"], 0.950175807027748, delta=1e-12)
        self.assertAlmostEqual(b["family_hi"], 0.9499977878584493, delta=1e-12)
        self.assertGreaterEqual(b["family_lo"], 0.95)
        self.assertLess(b["family_hi"], 0.95)
        # honesty: the curve OSCILLATES about nominal (no margin), it does
        # not plunge — values on both sides of 0.95 across the scan
        fams = [r["family_mean"] for r in
                self.B["calibrations"]["sidak_wilson"]["scan"]]
        self.assertGreater(max(fams[1:]), 0.95)
        self.assertLess(min(fams[1:]), 0.95)

    def test_sidak_world_a_hovers_without_floor(self):
        fams = [r["family_mean"] for r in
                self.A["calibrations"]["sidak_wilson"]["scan"]]
        self.assertAlmostEqual(min(fams), 0.9499025929034176, delta=1e-12)
        self.assertAlmostEqual(max(fams), 0.9500327834573393, delta=1e-12)
        # entire scan band is within +-0.0002 of nominal: no floor, all step
        self.assertLess(max(fams) - min(fams), 0.0002)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
