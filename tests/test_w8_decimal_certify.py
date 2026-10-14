"""Tick 136 pins: exact-Decimal certification of the w8 exactness
envelope maxima (tools/w8_decimal_certify.py).

Tick 132 disclosed that the envelope's direct-class maxima (6.4e-11 ..
7.4e-11, module vs per-term-lgamma logsumexp oracle) "partly reflect
the oracle's own logsumep floor", leaving tick 131's isolated Decimal
adjudication as the deepest ground truth.  This certification closes
that limit AT THE EXTREMA: every branch-class argmax of the pinned
tick-134 receipt (evidence/2026-10-14-w8-geometric-tail-bound/
envelope-full.json, sha256 8ed76df3..f844) is recomputed against
EXACT-INTEGER-factorial Decimal ground truth at prec 80 (the tick-131
method), truth taken at the module's ACTUAL float p (Decimal(float) is
the exact binary value), cdf summed on its defining side j=0..k and
sf_ge on j=k..n — never the 1-x complement, independent of the
module's branch routing.

MEASURED, THEN PINNED (receipt
evidence/2026-10-14-w8-decimal-certify/certify.json, sha256
fc81e9fc..591f):

- module TRUE deviations (vs exact): direct classes
  5.918e-11 / 6.355e-11 / 6.576e-11 / 6.847e-11 — ALL <= the 1e-10
  two-method bar, now certified against ground truth rather than a
  second float method;
- oracle deviations (vs exact): 1.93e-13 .. 4.94e-12 — the oracle's
  noise share at these points is <= 4.94e-12, i.e. the two-method
  numbers overstate the module's error by only ~7-13% here; tick
  132's honesty limit is now a QUANTIFIED, bounded term instead of an
  open caveat;
- complement extrema vs exact: 4.7502e-9 (cdf(494, 500, 0.999)) and
  2.3396e-9 (sf_ge(16, 100, 0.05)), both <= the 1e-8 complement-safe
  bar;
- drift guard: |module - oracle| / oracle recomputed live equals the
  receipt's stored max_rel EXACTLY at all six points, and the live
  branch classification re-derives the recorded class (guard change
  re-routing a point makes certification refuse, not mis-report).
"""

import hashlib
import json
import sys
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from w8_decimal_certify import (  # noqa: E402
    COMPLEMENT_BAR,
    DIRECT_BAR,
    certify_point,
    decimal_cdf,
    decimal_sf_ge,
)

EVIDENCE = (ROOT / "evidence" / "2026-10-14-w8-decimal-certify"
            / "certify.json")
EVIDENCE_SHA256 = ("fc81e9fc744c06a3b23a5fced4aa95b94facef06a"
                   "7720407b1aed6912b35891f")

# (helper, cls) -> measured certification, pinned byte-exact.
PINS = {
    ("binom_cdf", "short_side"): {
        "k": 2429, "n": 4999, "p": 0.5,
        "rel_module_vs_exact": 5.91775984789769e-11,
        "rel_oracle_vs_exact": 4.825173364683209e-12,
        "envelope_rel_recomputed": 6.400277184396893e-11,
    },
    ("binom_cdf", "deep_direct"): {
        "k": 4611, "n": 4999, "p": 0.95,
        "rel_module_vs_exact": 6.355080412407703e-11,
        "rel_oracle_vs_exact": 4.006951358468205e-12,
        "envelope_rel_recomputed": 6.755775548281594e-11,
    },
    ("binom_cdf", "complement"): {
        "k": 494, "n": 500, "p": 0.999,
        "rel_module_vs_exact": 4.7502370776798834e-09,
        "rel_oracle_vs_exact": 1.9264616791377177e-13,
        "envelope_rel_recomputed": 4.750429723848712e-09,
    },
    ("binom_sf_ge", "short_side"): {
        "k": 2500, "n": 4999, "p": 0.5,
        "rel_module_vs_exact": 6.847322708836145e-11,
        "rel_oracle_vs_exact": 4.9428239279336594e-12,
        "envelope_rel_recomputed": 7.3416051016658e-11,
    },
    ("binom_sf_ge", "deep_direct"): {
        "k": 389, "n": 4999, "p": 0.05,
        "rel_module_vs_exact": 6.575748756325634e-11,
        "rel_oracle_vs_exact": 2.1724018924768487e-12,
        "envelope_rel_recomputed": 6.792988945588077e-11,
    },
    ("binom_sf_ge", "complement"): {
        "k": 16, "n": 100, "p": 0.05,
        "rel_module_vs_exact": 2.339635530388481e-09,
        "rel_oracle_vs_exact": 2.881506308174232e-14,
        "envelope_rel_recomputed": 2.339606715325467e-09,
    },
}

ORACLE_NOISE_MAX = 4.9428239279336594e-12   # measured domain max at the 6 pts


class DecimalCertifyEvidencePins(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cert = json.loads(EVIDENCE.read_text())

    def test_evidence_sha256(self):
        got = hashlib.sha256(EVIDENCE.read_bytes()).hexdigest()
        self.assertEqual(got, EVIDENCE_SHA256)

    def test_six_points_pinned(self):
        by_key = {(r["helper"], r["cls"]): r for r in self.cert["points"]}
        self.assertEqual(set(by_key), set(PINS))
        for key, pin in PINS.items():
            row = by_key[key]
            self.assertEqual([row["k"], row["n"], row["p"]],
                             [pin["k"], pin["n"], pin["p"]], msg=key)
            for field in ("rel_module_vs_exact", "rel_oracle_vs_exact",
                          "envelope_rel_recomputed"):
                self.assertEqual(row[field], pin[field],
                                 msg=f"{key}.{field}")

    def test_summary_pins(self):
        self.assertTrue(self.cert["all_direct_module_holds_bar"])
        self.assertTrue(self.cert["all_complement_module_holds_bar"])
        self.assertEqual(self.cert["max_rel_module_vs_exact_overall"],
                         4.7502370776798834e-09)
        self.assertEqual(self.cert["max_rel_oracle_vs_exact_overall"],
                         ORACLE_NOISE_MAX)
        self.assertEqual(self.cert["decimal_prec"], 80)

    def test_recomputed_two_method_equals_recorded_max_rel(self):
        """Drift guard: the live |module - oracle| / oracle equals the
        envelope receipt's stored max_rel at all six points — any
        walk-bit change in either code path flips this."""
        for row in self.cert["points"]:
            self.assertEqual(row["envelope_rel_recomputed"],
                             row["envelope_max_rel_recorded"],
                             msg=(row["helper"], row["cls"]))

    def test_direct_bar_held_vs_exact(self):
        for row in self.cert["points"]:
            if row["cls"] != "complement":
                self.assertLessEqual(row["rel_module_vs_exact"],
                                     DIRECT_BAR,
                                     msg=(row["helper"], row["cls"]))

    def test_complement_bar_held_vs_exact(self):
        for row in self.cert["points"]:
            if row["cls"] == "complement":
                self.assertLessEqual(row["rel_module_vs_exact"],
                                     COMPLEMENT_BAR,
                                     msg=(row["helper"], row["cls"]))

    def test_oracle_noise_share_bounded(self):
        """The tick-132 open caveat becomes a bounded term: the oracle
        sits within 4.95e-12 of exact truth at every extremum."""
        for row in self.cert["points"]:
            self.assertLessEqual(row["rel_oracle_vs_exact"],
                                 ORACLE_NOISE_MAX,
                                 msg=(row["helper"], row["cls"]))


class DecimalCertifyLiveRecompute(unittest.TestCase):
    """Cheap points (n <= 500) re-certify bit-identically in-test —
    ground-truth arithmetic included, keeping CI honest about the
    Decimal path itself."""

    def test_cdf_complement_point_reproduces(self):
        row = certify_point("binom_cdf", 494, 500, 0.999, "complement")
        pin = PINS[("binom_cdf", "complement")]
        self.assertEqual(row["rel_module_vs_exact"],
                         pin["rel_module_vs_exact"])
        self.assertEqual(row["rel_oracle_vs_exact"],
                         pin["rel_oracle_vs_exact"])
        self.assertTrue(row["module_bar_held"])

    def test_sf_complement_point_reproduces(self):
        row = certify_point("binom_sf_ge", 16, 100, 0.05, "complement")
        pin = PINS[("binom_sf_ge", "complement")]
        self.assertEqual(row["rel_module_vs_exact"],
                         pin["rel_module_vs_exact"])
        self.assertEqual(row["rel_oracle_vs_exact"],
                         pin["rel_oracle_vs_exact"])
        self.assertTrue(row["module_bar_held"])

    def test_classification_drift_guard_fires(self):
        """A wrong class must make certification REFUSE (guard drift
        is an error, never a silent re-report)."""
        with self.assertRaises(AssertionError):
            certify_point("binom_cdf", 494, 500, 0.999, "short_side")


class DecimalGroundTruthSelfCheck(unittest.TestCase):
    """Dyadic textbook cases are EXACT in binary floats and Decimal —
    the ground-truth sums must return them exactly, not approximately."""

    def test_dyadic_identities(self):
        self.assertEqual(decimal_cdf(0, 2, 0.5), Decimal("0.25"))
        self.assertEqual(decimal_sf_ge(2, 2, 0.5), Decimal("0.25"))
        self.assertEqual(decimal_cdf(2, 4, 0.5), Decimal("0.6875"))
        self.assertEqual(decimal_sf_ge(3, 4, 0.5), Decimal("0.3125"))
        self.assertEqual(decimal_cdf(4, 4, 0.5), Decimal("1"))
        self.assertEqual(decimal_sf_ge(0, 4, 0.5), Decimal("1"))
        self.assertEqual(decimal_cdf(-1, 4, 0.5), Decimal("0"))
        self.assertEqual(decimal_sf_ge(5, 4, 0.5), Decimal("0"))

    def test_defining_sides_partition_unit(self):
        """cdf(k-1) + sf_ge(k) == 1 exactly at a dyadic p (11/16 +
        5/16 = 1)."""
        a = decimal_cdf(2, 4, 0.5)
        b = decimal_sf_ge(3, 4, 0.5)
        self.assertEqual(a + b, Decimal(1))


if __name__ == "__main__":
    unittest.main()
