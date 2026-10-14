"""Tick 137 pins: exact-Decimal certification of the complement
decade-bucket maxima (tools/w8_decimal_certify_buckets.py).

Tick 136 certified the six branch-class ARGMAX points of the pinned
tick-134 envelope receipt against exact-integer-factorial Decimal
ground truth and disclosed the remaining limit: "certifies the six
argmax extrema (the class-maxima claim), not all 537 grid points".
This tick closes the next ring inward for the branch that carries the
1e-8 bar and the figure-013 curves: EVERY per-decade bucket maximum of
both COMPLEMENT classes (binom_cdf: decades 0,-1..-5; binom_sf_ge:
0,-1,-2,-5) is re-located on the identical deterministic sweep grid
and certified against the same exact truth.  The located points are
guarded by exact replay of the pinned receipt's stored bucket values.

MEASURED, THEN PINNED (receipt
evidence/2026-10-14-w8-decimal-certify-buckets/buckets.json, sha256
b4e95510..e10d):

- all TEN bucket maxima hold the 1e-8 complement bar against exact
  truth, including the two n=4999 points beyond tick 136's extrema
  set: cdf(4984, 4999, 0.999) at 4.0861e-9 (decade -4) and
  sf_ge(1311, 4999, 0.25) at 1.2707e-9 (decade -2);
- the oracle-noise share is bounded at <= 5.9622e-12 across ALL ten
  bucket points (tick 136: 4.943e-12 at six argmax points);
- decade-0 bucket maxima are ~ENTIRELY oracle noise: module-vs-exact
  7.52e-20 (cdf(1475, 2500, 0.5)) and exactly 0.0 (sf_ge(0, 2500,
  0.5)) against recorded two-method bucket maxima of 3.8369e-13;
- drift guards: the replay reproduces the receipt's stored bucket
  values EXACTLY (per-point envelope_rel_recomputed ==
  bucket_rel_recorded), 537 compared / 37 below-floor, and the
  complement class argmax points; certify_point re-derives the
  branch class live and refuses on guard drift.
"""

import hashlib
import json
import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent / "tools"
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

from w8_decimal_certify import certify_point  # noqa: E402
from w8_decimal_certify_buckets import (  # noqa: E402
    SOURCE_RECEIPT,
    certify_buckets,
)

BUCKETS_RECEIPT = (
    ROOT / "evidence" / "2026-10-14-w8-decimal-certify-buckets"
    / "buckets.json")
BUCKETS_SHA256 = ("b4e95510ad690e79775dd287c1577b833be193fece05"
                  "94a1d3ed282e3e4fe10d")
SOURCE_SHA256 = "8ed76df3"


class EnvelopeBucketsReceiptPins(unittest.TestCase):
    """Structural + numeric pins on the generated bucket receipt."""

    @classmethod
    def setUpClass(cls):
        cls.raw = BUCKETS_RECEIPT.read_bytes()
        cls.sha = hashlib.sha256(cls.raw).hexdigest()
        cls.receipt = json.loads(cls.raw)
        cls.source = json.loads(Path(SOURCE_RECEIPT).read_text())

    def test_receipt_sha256_pinned(self):
        self.assertEqual(self.sha, BUCKETS_SHA256)

    def test_source_receipt_is_the_pinned_tick134_envelope(self):
        self.assertEqual(
            hashlib.sha256(Path(SOURCE_RECEIPT).read_bytes()).hexdigest()
            [:8], SOURCE_SHA256)

    def test_ten_buckets_all_holding_the_complement_bar(self):
        self.assertEqual(self.receipt["buckets_certified"], 10)
        self.assertTrue(self.receipt["all_complement_module_holds_bar"])
        self.assertEqual(self.receipt["complement_bar"], 1e-8)
        for row in self.receipt["points"]:
            self.assertLessEqual(row["rel_module_vs_exact"], 1e-8)
            self.assertTrue(row["module_bar_held"])
            self.assertEqual(row["cls"], "complement")

    def test_bucket_decades_match_source_receipt_keys(self):
        for helper in ("binom_cdf", "binom_sf_ge"):
            stored = self.source["per_helper"][helper]["complement"][
                "decade_buckets"]
            got = {str(r["decade"]) for r in self.receipt["points"]
                   if r["helper"] == helper}
            self.assertEqual(got, set(stored.keys()), helper)

    def test_every_located_point_reproduces_its_stored_bucket_max(self):
        # the per-point drift guard asserted at generation time: the
        # located point's live two-method rel equals the stored bucket
        # maximum EXACTLY for all ten rows.
        for row in self.receipt["points"]:
            self.assertEqual(row["envelope_rel_recomputed"],
                             row["bucket_rel_recorded"], str(row))

    def test_replay_counts_match_source_receipt(self):
        self.assertEqual(self.receipt["replay_points_compared"], 537)
        self.assertEqual(self.receipt["replay_points_below_floor"], 37)
        self.assertEqual(self.source["points_compared"], 537)

    def test_pinned_worst_points_beyond_the_tick136_extrema(self):
        by = {(r["helper"], r["decade"]): r for r in self.receipt["points"]}
        cdf_m4 = by[("binom_cdf", -4)]
        self.assertEqual(
            (cdf_m4["k"], cdf_m4["n"], cdf_m4["p"]), (4984, 4999, 0.999))
        self.assertEqual(cdf_m4["rel_module_vs_exact"],
                         4.086078832175916e-9)
        sf_m2 = by[("binom_sf_ge", -2)]
        self.assertEqual(
            (sf_m2["k"], sf_m2["n"], sf_m2["p"]), (1311, 4999, 0.25))
        self.assertEqual(sf_m2["rel_module_vs_exact"],
                         1.2706953709053496e-9)

    def test_pinned_global_extrema_rows_unchanged(self):
        by = {(r["helper"], r["decade"]): r for r in self.receipt["points"]}
        self.assertEqual(by[("binom_cdf", -5)]["rel_module_vs_exact"],
                         4.7502370776798834e-9)
        self.assertEqual(by[("binom_sf_ge", -5)]["rel_module_vs_exact"],
                         2.339635530388481e-9)
        self.assertEqual(self.receipt["max_rel_module_vs_exact_overall"],
                         4.7502370776798834e-9)

    def test_decade0_bucket_maxima_are_oracle_noise_not_module_error(self):
        by = {(r["helper"], r["decade"]): r for r in self.receipt["points"]}
        self.assertLessEqual(by[("binom_cdf", 0)]["rel_module_vs_exact"],
                             1e-18)
        self.assertEqual(by[("binom_sf_ge", 0)]["rel_module_vs_exact"], 0.0)
        self.assertGreaterEqual(
            by[("binom_cdf", 0)]["bucket_rel_recorded"], 3.8e-13)
        # oracle noise share bounded across ALL ten bucket points
        self.assertLessEqual(self.receipt["max_rel_oracle_vs_exact_overall"],
                             5.9623e-12)


class BucketLiveRecomputes(unittest.TestCase):
    """Live exact recomputation of two cheap bucket points (n <= 500):
    the receipt's numbers must reproduce exactly under the current
    code (drift guard)."""

    def test_cdf_extremum_recomputes_live(self):
        row = certify_point("binom_cdf", 494, 500, 0.999, "complement")
        self.assertEqual(row["rel_module_vs_exact"],
                         4.7502370776798834e-9)
        self.assertEqual(row["rel_oracle_vs_exact"],
                         1.9264616791377177e-13)
        self.assertTrue(row["module_bar_held"])

    def test_sf_extremum_recomputes_live(self):
        row = certify_point("binom_sf_ge", 16, 100, 0.05, "complement")
        self.assertEqual(row["rel_module_vs_exact"],
                         2.339635530388481e-9)
        self.assertEqual(row["rel_oracle_vs_exact"],
                         2.881506308174232e-14)
        self.assertTrue(row["module_bar_held"])

    def test_wrong_class_refuses(self):
        # (40, 100, 0.5) is short_side (k+1 <= n-k); demanding
        # 'complement' must raise, not mis-report.
        with self.assertRaises(AssertionError):
            certify_point("binom_cdf", 40, 100, 0.5, "complement")


if __name__ == "__main__":
    unittest.main()
