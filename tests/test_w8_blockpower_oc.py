"""Pins for tools/w8_blockpower_oc.py (tick 139, SON-5152).

Pre-datum Monte-Carlo operating characteristics of the FROZEN tick-120
arbitration instrument (pooled Fisher exact one-sided, H1 share(GAP) >
share(A6), alpha 0.05, n = 3560/group). Synthetic binomial counts only —
zero kTAM trajectories, none of the probe's virgin seed windows
consumed, no gate executed, ladder stays PAUSED, no branch touched.

Measured first, then frozen (house rule). Headline the pins guard: the
prereg's NORMAL-APPROXIMATION power claims (0.896 / 0.979 / 0.696 at
delta 0.030 / 0.038 / 0.0223) are each reproduced by the exact
instrument within the receipt's MC Wilson 95 interval, and the realized
size at the frozen margins is 193/4000 = 0.04825 <= 0.05 — the exact
test gives up nothing material at these margins, so a NOT_DETECTED
outcome really does mean "no persistent elevation of the pre-registered
size at ~90% power", while a hotrepro-sized effect (+0.0223) survives
NOT_DETECTED at only ~0.69 power (measured, not asserted).
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import unittest
from fractions import Fraction

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.w8_blockpower_oc import (  # noqa: E402
    ALPHA,
    ANCHOR,
    N_PER_GROUP,
    REPLICATES,
    SCENARIOS,
    fisher_one_sided_greater,
    run_scenario,
)

RECEIPT = os.path.join(ROOT, "evidence", "2026-10-14-w8-blockpower-oc",
                       "oc.json")
RECEIPT_SHA = ("142ddfb924ada0a4d341f559c75bc492247989dd"
               "c639b245b451b7d9b13025a6")


def _receipt() -> dict:
    with open(RECEIPT, "rb") as fh:
        blob = fh.read()
    assert hashlib.sha256(blob).hexdigest() == RECEIPT_SHA, "receipt drifted"
    return json.loads(blob)


class FisherExactReference(unittest.TestCase):
    """Two-method check: float tail walk vs exact Fraction hypergeometric."""

    CASES = [(11, 12, 3, 10), (27, 40, 22, 40), (30, 50, 28, 50)]

    def test_matches_exact_fractions(self):
        for x, n1, y, n2 in self.CASES:
            k = x + y
            n = n1 + n2
            kmax = min(n1, k)
            exact = sum(
                Fraction(math.comb(n1, j) * math.comb(n2, k - j),
                         math.comb(n, k))
                for j in range(x, kmax + 1)
            )
            got = fisher_one_sided_greater(x, n1, y, n2)
            self.assertAlmostEqual(got, float(exact), places=12,
                                   msg=f"case {(x, n1, y, n2)}")

    def test_edge_no_successes_anywhere_is_certain(self):
        self.assertEqual(fisher_one_sided_greater(0, 10, 0, 10), 1.0)

    def test_input_guards(self):
        with self.assertRaises(ValueError):
            fisher_one_sided_greater(11, 0, 3, 10)
        with self.assertRaises(ValueError):
            fisher_one_sided_greater(11, 12, 3, 0)
        with self.assertRaises(ValueError):
            fisher_one_sided_greater(13, 12, 3, 10)
        with self.assertRaises(ValueError):
            fisher_one_sided_greater(11, 12, -1, 10)
        with self.assertRaises(ValueError):
            run_scenario(0.5, 0.5, 100, 100, -1)
        with self.assertRaises(ValueError):
            run_scenario(0.5, 0.5, 100, 0, 1)
        with self.assertRaises(ValueError):
            run_scenario(0.5, 0.5, 100, 10, True)


class ReceiptPins(unittest.TestCase):
    """Frozen receipt: sha, design fields, and the measured OC numbers."""

    def test_receipt_sha_and_frozen_fields(self):
        receipt = _receipt()
        self.assertEqual(receipt["n_per_group"], N_PER_GROUP)
        self.assertEqual(receipt["n_per_group"], 3560)
        self.assertEqual(receipt["replicates"], REPLICATES)
        self.assertEqual(receipt["alpha"], ALPHA)
        self.assertEqual(receipt["anchor_pbar"], ANCHOR)
        self.assertEqual(
            set(receipt["results"]),
            {"H0_SIZE", "D030_BASELINE", "D030_MIDPOINT",
             "D038_BASELINE", "D0223_BASELINE"})
        for res in receipt["results"].values():
            self.assertEqual(res["replicates"], REPLICATES)

    def test_size_conservative_at_frozen_margins(self):
        res = _receipt()["results"]["H0_SIZE"]
        self.assertEqual(res["rejections"], 193)
        self.assertEqual(res["reject_rate"], 193 / 4000)
        self.assertEqual(res["p_gap"], res["p_a6"])  # true null
        self.assertLessEqual(res["reject_rate"], ALPHA)
        lo, hi = res["reject_rate_wilson95"]
        self.assertAlmostEqual(lo, 0.04203145324832355, places=15)
        self.assertAlmostEqual(hi, 0.05533543559163455, places=15)

    def test_power_pins_and_ordering(self):
        results = _receipt()["results"]
        self.assertEqual(results["D0223_BASELINE"]["rejections"], 2777)
        self.assertEqual(results["D030_MIDPOINT"]["rejections"], 3566)
        self.assertEqual(results["D030_BASELINE"]["rejections"], 3591)
        self.assertEqual(results["D038_BASELINE"]["rejections"], 3916)
        self.assertLess(results["D0223_BASELINE"]["reject_rate"],
                        results["D030_MIDPOINT"]["reject_rate"])
        self.assertLess(results["D030_MIDPOINT"]["reject_rate"],
                        results["D030_BASELINE"]["reject_rate"])
        self.assertLess(results["D030_BASELINE"]["reject_rate"],
                        results["D038_BASELINE"]["reject_rate"])

    def test_normal_approx_claims_inside_mc_wilson(self):
        """Calibration: prereg normal-approx power lands inside the exact
        instrument's MC Wilson 95 interval at every pre-registered delta."""
        results = _receipt()["results"]
        for key, claim in (("D030_BASELINE", 0.896), ("D038_BASELINE", 0.979),
                           ("D0223_BASELINE", 0.696)):
            lo, hi = results[key]["reject_rate_wilson95"]
            self.assertGreaterEqual(claim, lo, msg=key)
            self.assertLessEqual(claim, hi, msg=key)

    def test_anchor_ambiguity_immaterial_at_d030(self):
        """Baseline vs midpoint anchoring of the prereg p_bar differ by
        less than MC error at delta 0.030 (Wilson intervals overlap)."""
        results = _receipt()["results"]
        b_lo, b_hi = results["D030_BASELINE"]["reject_rate_wilson95"]
        m_lo, m_hi = results["D030_MIDPOINT"]["reject_rate_wilson95"]
        self.assertLess(b_lo, m_hi)
        self.assertLess(m_lo, b_hi)

    def test_scenario_seeds_disjoint_from_committed_rng_seeds(self):
        seeds = {seed for _, _, seed in SCENARIOS.values()}
        self.assertEqual(seeds,
                         {20261015, 20261016, 20261017, 20261018, 20261019})
        # census-sim (tick 123) RNG seeds must not be reused
        self.assertFalse(seeds & {20261013, 20261014})


class Determinism(unittest.TestCase):
    """Small-n live recompute of the full MC path (sampler + exact test)."""

    def test_small_scenario_deterministic_and_pinned(self):
        first = run_scenario(0.62, 0.5, 200, 1200, 424242)
        second = run_scenario(0.62, 0.5, 200, 1200, 424242)
        self.assertEqual(first, second)
        self.assertEqual(first["rejections"], 896)
        self.assertEqual(first["replicates"], 1200)
        self.assertAlmostEqual(first["rate"], 896 / 1200, places=15)


if __name__ == "__main__":
    unittest.main()
