"""Pins for the tick-120 powered paired block-mechanism arbitration
probe (evidence/2026-10-13-w8-blockpower/ktam_w8_blockpower.py).

Covers: frozen constants and seed lineage; virgin-window guarantee
(no prior run output may contain any seed literal inside the fresh
ranges); the frozen branch map on synthetic counts; the one-sided
Fisher arithmetic cross-checked against exact Fraction hypergeometric;
the direction encoding; the pre-submission power statement; the fixed
family references.  See research-log/2026-10-13-w8-blockpower-prereg.md.
"""

from __future__ import annotations

import importlib.util
import math
import os
import re
from fractions import Fraction
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
MODULE_PATH = (REPO / "evidence" / "2026-10-13-w8-blockpower"
               / "ktam_w8_blockpower.py")

spec = importlib.util.spec_from_file_location("ktam_w8_blockpower",
                                              MODULE_PATH)
bp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bp)

GAP_FRESH = range(350262607, 350266667)   # 350261107 + [1500, 5060)
A6_FRESH = range(340263107, 340266667)    # 340261107 + [2000, 5560)


class TestConstants(unittest.TestCase):
    def test_seed_lineage_pinned(self):
        # blockprobe lineage: BASE_SEED 220261107, STRIDE 20,000,000
        self.assertEqual(bp.BASE_SEED, 220261107)
        self.assertEqual(bp.SEED_STRIDE, 20_000_000)
        self.assertEqual(bp.A6_BLOCK, 340261107)    # BASE + 6 strides
        self.assertEqual(bp.GAP_BLOCK, 350261107)   # BASE + 6.5 strides
        self.assertEqual(bp.A6_OFFSET, 2000)        # burned [0,2000)
        self.assertEqual(bp.GAP_OFFSET, 1500)       # burned [0,1500)
        self.assertEqual(bp.SEED0_A6, 340263107)
        self.assertEqual(bp.SEED0_GAP, 350262607)
        self.assertEqual(bp.SEED0_CAL, 260261107)

    def test_design_size_pinned(self):
        self.assertEqual(bp.N_WIN, 1780)            # per window
        self.assertEqual(bp.N_GROUP, 3560)          # 2000*(0.040/0.030)^2
        self.assertEqual(bp.MIN_EVENTS, 3400)
        self.assertEqual(bp.ALPHA, 0.05)

    def test_burned_offsets_are_outside_fresh_ranges(self):
        burned = [350261107, 350261607,            # arm8, B-fresh
                  340261107, 340261607, 340262107]  # arm6, arm6b, A-fresh
        for seed in burned:
            self.assertNotIn(seed, GAP_FRESH)
            self.assertNotIn(seed, A6_FRESH)

    def test_family_references_pinned(self):
        self.assertEqual(bp.FAMILY, {"x": 1110, "k": 1499})
        self.assertEqual(bp.ARM6, {"x": 389, "k": 500})
        self.assertEqual(bp.ARM6B, {"x": 372, "k": 500})
        self.assertEqual(bp.ARM8, {"x": 391, "k": 500})
        self.assertEqual(bp.AFRESH, {"x": 691, "k": 999})
        self.assertEqual(bp.BFRESH, {"x": 714, "k": 1000})


class TestVirginSeeds(unittest.TestCase):
    def test_no_prior_run_out_contains_probe_seeds(self):
        """Any run.out outside this probe's own evidence dir that
        contains a seed literal inside the fresh windows is a
        seed-reuse bug (tick-113 rule; enforced backstop)."""
        hits = []
        own = "2026-10-13-w8-blockpower"
        for path in REPO.glob("evidence/**/run.out"):
            if own in str(path):
                continue
            text = path.read_text(errors="ignore")
            for literal in re.findall(r"3[45]026\d{4}", text):
                value = int(literal)
                if value in GAP_FRESH or value in A6_FRESH:
                    hits.append((str(path), value))
        self.assertEqual(hits, [])


class TestBranchMap(unittest.TestCase):
    def test_void_on_cal_fail(self):
        branch, tests = bp.branch_map(2730, 3500, 2450, 3500, False)
        self.assertEqual(branch, "VOID")
        self.assertIsNone(tests)

    def test_no_events_below_floor(self):
        branch, tests = bp.branch_map(2730, 3399, 2450, 3399, True)
        self.assertEqual(branch, "NO_EVENTS")
        self.assertIsNotNone(tests)

    def test_supported_on_strong_gap_excess(self):
        branch, tests = bp.branch_map(2730, 3500, 2450, 3500, True)
        self.assertEqual(branch, "BLOCK_MECHANISM_SUPPORTED")
        self.assertLessEqual(tests["p_fisher_one_sided"], bp.ALPHA)

    def test_not_detected_on_null_contrast(self):
        branch, tests = bp.branch_map(2600, 3500, 2601, 3500, True)
        self.assertEqual(branch, "BLOCK_MECHANISM_NOT_DETECTED")
        self.assertGreater(tests["p_fisher_one_sided"], bp.ALPHA)


class TestFisher(unittest.TestCase):
    def test_one_sided_matches_fraction_hypergeometric(self):
        # GAP 7/10 vs A6 2/10: p = P(X>=7 | 20 balls, 9 succ, n=10)
        num = sum(Fraction(math.comb(9, k)) * math.comb(11, 10 - k)
                  for k in (7, 8, 9))
        expected = Fraction(num, math.comb(20, 10))
        got = bp.fisher_one_sided(7, 10, 2, 10)
        self.assertLess(abs(got - float(expected)), 1e-12)

    def test_direction_encoding_gap_gt_a6(self):
        # the same table read in the frozen direction is small;
        # read reversed it is large — pins H1: share(GAP) > share(A6)
        self.assertLess(bp.fisher_one_sided(7, 10, 2, 10), 0.05)
        self.assertGreater(bp.fisher_one_sided(2, 10, 7, 10), 0.9)


class TestPowerStatement(unittest.TestCase):
    """Pre-submission power statement, recomputed here and pinned to
    the prereg note's numbers (research-log/...-prereg.md)."""

    def test_power_numbers(self):
        se = math.sqrt(2 * 0.745 * 0.255 / 3560)

        def power(delta):
            z = delta / se - 1.6448536269514722
            return 0.5 * (1 + math.erf(z / math.sqrt(2)))

        self.assertAlmostEqual(se, 0.010332, places=5)
        mde90 = (1.6448536269514722 + 1.2815515655446004) * se
        self.assertAlmostEqual(mde90, 0.03024, places=4)
        self.assertAlmostEqual(power(0.030), 0.896, delta=0.005)
        self.assertAlmostEqual(power(0.038), 0.979, delta=0.005)
        self.assertAlmostEqual(power(0.0223), 0.696, delta=0.005)

    def test_n_derivation_frozen_rule(self):
        n = 2000 * (0.040 / 0.030) ** 2
        self.assertAlmostEqual(n, 3555.6, places=1)
        self.assertEqual(bp.N_GROUP, 3560)


if __name__ == "__main__":
    unittest.main()
