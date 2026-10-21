"""Pins for tools/w9_homogeneity_oc.py (tick 147, SON-5152).

Pre-datum Monte-Carlo operating characteristics of the candidate W9
four-arm homogeneity instruments, measured BEFORE any exit was chosen
(the duty fixed by the tick-146 triage note). Synthetic binomial counts
only — zero kTAM trajectories, no virgin seed windows consumed, no gate
executed, no branch of any frozen map touched.

Headline findings the pins guard:

1. The tick-93 receipt rule (min over 4 arms of the exact two-sided
   binomial p against the leave-one-out pool, nominal alpha 0.05, no
   multiplicity correction) has REALIZED SIZE ~0.26-0.27 under the
   null of one common share — it fires roughly one time in four. The
   per-replicate estimated (LOO) null breaks marginal exactness, so
   even a Bonferroni threshold (0.0125) leaves size ~0.097-0.099;
   thresholding this family cannot control size.
2. The pairwise exact Fisher family (min over the 6 pairwise
   two-sided Fisher p-values, Bonferroni threshold 0.05/6) IS a valid
   size-controlled omnibus: measured size 0.0275-0.0305 (<= 0.05 by
   Boole regardless of dependence; conservative as expected).
3. The valid instrument's power on the RESIDUAL tick-99 pattern (the
   operative alternative after W8 reassigned arm-6's hot share):
   0.3665 at n=500/arm, 0.6990 at n=1000/arm (4000 pair terminals,
   W8-scale), 0.88775 at n=1500/arm (6000 pair terminals, ~1.7x the
   W8 probe's entire budget) — the input to the tick-147 exit decision.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.w9_homogeneity_oc import (  # noqa: E402
    ALPHA,
    ARMS,
    REPLICATES,
    SEEDS,
    cross_check_fast_p,
    fast_two_sided_p,
    hypergeom_two_sided_p,
    min_pairwise_fisher_p,
    min_p_statistic,
)

RECEIPT = os.path.join(ROOT, "evidence", "2026-10-21-w9-homogeneity-oc",
                       "oc.json")
RECEIPT_SHA = ("560225f6cf8321f980c16d0ad7eb25e407b52635d"
               "161f8a4d870d96fab8d16a0")

# Exact rejection counts of record (fixed seeds, deterministic).
PINNED = {
    ("SIZE_500", "loo_min_binom_nominal"): 1059,
    ("SIZE_500", "loo_min_binom_bonferroni"): 390,
    ("SIZE_500", "pairwise_min_fisher_bonferroni"): 110,
    ("SIZE_1000", "loo_min_binom_nominal"): 1069,
    ("SIZE_1000", "loo_min_binom_bonferroni"): 388,
    ("SIZE_1000", "pairwise_min_fisher_bonferroni"): 115,
    ("SIZE_1500", "loo_min_binom_nominal"): 1074,
    ("SIZE_1500", "loo_min_binom_bonferroni"): 394,
    ("SIZE_1500", "pairwise_min_fisher_bonferroni"): 122,
    ("RESIDUAL_500", "loo_min_binom_nominal"): 3060,
    ("RESIDUAL_500", "loo_min_binom_bonferroni"): 2269,
    ("RESIDUAL_500", "pairwise_min_fisher_bonferroni"): 1466,
    ("RESIDUAL_1000", "loo_min_binom_nominal"): 3769,
    ("RESIDUAL_1000", "loo_min_binom_bonferroni"): 3376,
    ("RESIDUAL_1000", "pairwise_min_fisher_bonferroni"): 2796,
    ("RESIDUAL_1500", "loo_min_binom_nominal"): 3943,
    ("RESIDUAL_1500", "loo_min_binom_bonferroni"): 3813,
    ("RESIDUAL_1500", "pairwise_min_fisher_bonferroni"): 3551,
    ("ORIGINAL_500", "loo_min_binom_nominal"): 3727,
    ("ORIGINAL_500", "loo_min_binom_bonferroni"): 3296,
    ("ORIGINAL_500", "pairwise_min_fisher_bonferroni"): 2772,
    ("ORIGINAL_1000", "loo_min_binom_nominal"): 3987,
    ("ORIGINAL_1000", "loo_min_binom_bonferroni"): 3934,
    ("ORIGINAL_1000", "pairwise_min_fisher_bonferroni"): 3842,
    ("ORIGINAL_1500", "loo_min_binom_nominal"): 3997,
    ("ORIGINAL_1500", "loo_min_binom_bonferroni"): 3996,
    ("ORIGINAL_1500", "pairwise_min_fisher_bonferroni"): 3990,
}

# scipy.stats.fisher_exact two-sided values (verified in-run 2026-10-21).
FISHER_PINS = [
    (3, 4, 1, 4, 0.4857142857142857),
    (5, 10, 8, 10, 0.34984520123839014),
    (375, 500, 106, 153, 0.1730588496885811),
    (389, 500, 365, 499, 0.09114117334678429),
]


def _receipt() -> dict:
    with open(RECEIPT, encoding="utf-8") as fh:
        return json.load(fh)


class TestReceipt(unittest.TestCase):
    def test_receipt_sha_matches_pin(self) -> None:
        raw = open(RECEIPT, "rb").read()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), RECEIPT_SHA)

    def test_receipt_schema_and_replicates(self) -> None:
        rep = _receipt()
        self.assertEqual(rep["schema"], "w9-homogeneity-oc-v1")
        self.assertEqual(rep["alpha"], ALPHA)
        self.assertEqual(rep["replicates"], REPLICATES)
        self.assertEqual(tuple(rep["seeds"]), SEEDS)
        self.assertEqual(len(rep["configs"]), 9)
        self.assertEqual(ARMS, 4)

    def test_pinned_rejection_counts(self) -> None:
        rep = _receipt()
        by_label = {c["label"]: c for c in rep["configs"]}
        for (label, key), rejections in PINNED.items():
            cfg = by_label[label]
            self.assertEqual(cfg["replicates"], REPLICATES, label)
            self.assertEqual(cfg[key]["rejections"], rejections,
                             f"{label}/{key}")

    def test_tick93_rule_size_is_materially_inflated(self) -> None:
        """The finding of record: the contest trigger fires ~1-in-4 under H0."""
        rep = _receipt()
        for cfg in rep["configs"]:
            if not cfg["label"].startswith("SIZE_"):
                continue
            nom = cfg["loo_min_binom_nominal"]["estimate"]
            bonf = cfg["loo_min_binom_bonferroni"]["estimate"]
            self.assertGreaterEqual(nom, 0.20, cfg["label"])
            self.assertGreaterEqual(bonf, 0.08, cfg["label"])

    def test_pairwise_fisher_family_is_size_controlled(self) -> None:
        """Valid omnibus: Bonferroni threshold keeps realized size <= 0.05."""
        rep = _receipt()
        for cfg in rep["configs"]:
            if not cfg["label"].startswith("SIZE_"):
                continue
            size = cfg["pairwise_min_fisher_bonferroni"]
            self.assertLessEqual(size["wilson95_high"], ALPHA, cfg["label"])

    def test_residual_power_curve_is_recorded(self) -> None:
        by_label = {c["label"]: c for c in _receipt()["configs"]}
        p500 = by_label["RESIDUAL_500"]["pairwise_min_fisher_bonferroni"]["estimate"]
        p1000 = by_label["RESIDUAL_1000"]["pairwise_min_fisher_bonferroni"]["estimate"]
        p1500 = by_label["RESIDUAL_1500"]["pairwise_min_fisher_bonferroni"]["estimate"]
        # Monotone in n, and the two decision anchors of record.
        self.assertLess(p500, p1000)
        self.assertLess(p1000, p1500)
        self.assertAlmostEqual(p1000, 2796 / REPLICATES, places=10)
        self.assertAlmostEqual(p1500, 3551 / REPLICATES, places=10)


class TestInstruments(unittest.TestCase):
    def test_cross_check_against_reference_implementations(self) -> None:
        cross = cross_check_fast_p()
        self.assertLessEqual(cross["max_abs_diff"], 1e-10)
        self.assertLessEqual(cross["fisher_max_abs_diff"], 1e-12)

    def test_fisher_matches_scipy_pins(self) -> None:
        for x1, n1, x2, n2, want in FISHER_PINS:
            got = hypergeom_two_sided_p(x1, n1, x2, n2)
            self.assertAlmostEqual(got, want, delta=1e-12)

    def test_fisher_extreme_table_edges(self) -> None:
        # All-success vs all-failure arms: strongest possible table.
        self.assertLess(hypergeom_two_sided_p(10, 10, 0, 10), 1e-4)
        # Identical arms: zero evidence against homogeneity.
        self.assertAlmostEqual(hypergeom_two_sided_p(7, 10, 7, 10), 1.0)

    def test_min_statistic_deterministic_micro_run(self) -> None:
        import random

        from tools.w9_homogeneity_oc import PATTERN_RESIDUAL, _BinomialCDF
        rng = random.Random(SEEDS[0])
        samplers = [_BinomialCDF(40, p) for p in PATTERN_RESIDUAL]
        first = [tuple(s.draw(rng) for s in samplers) for _ in range(50)]
        rng2 = random.Random(SEEDS[0])
        samplers2 = [_BinomialCDF(40, p) for p in PATTERN_RESIDUAL]
        second = [tuple(s.draw(rng2) for s in samplers2) for _ in range(50)]
        self.assertEqual(first, second)
        for counts in first[:5]:
            self.assertLessEqual(min_pairwise_fisher_p(list(counts), 40), 1.0)
            self.assertLessEqual(min_p_statistic(list(counts), 40), 1.0)
            for x in counts:
                self.assertTrue(0 <= x <= 40)


if __name__ == "__main__":
    unittest.main()
