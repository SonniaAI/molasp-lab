"""Tick 132 pins: the DOMAIN-OF-EXACTNESS ENVELOPE for the w8 exact-band
tail helpers (tools/w8_exactness_envelope.py sweeping
tools/w8_exact_bands.py).  Every number is byte-reproducible (no RNG,
stdlib only, deterministic grid) and every full-grid pin is checked
against the committed evidence receipt
evidence/2026-10-14-w8-exactness-envelope/envelope-full.json.

The envelope turns ticks 129-131's isolated deep-tail pins into a
measured domain-wide bound: max relative deviation of binom_cdf /
binom_sf_ge vs the independent per-term-lgamma logsumexp oracle,
per branch CLASS (short_side direct sum / 1-x complement / tick-131
deep_direct guard), over the stratified grid n in {100, 500, 1000,
2500, 4999}, p in {0.05, 0.246696, 0.25, 0.5, 0.753304, 0.95, 0.999},
k at {0, n, mode, mode +- 2/5/9 sigma}.

Measured story pinned here:
- short_side and deep_direct are <= 7.4e-11 RELATIVE across the whole
  grid (two-method bar 1e-10 held domain-wide, not just at the
  tick-131 points).
- The complement branch is <= 1.1e-9 for true masses >= 1e-2 and
  <= 4.8e-9 down to 1e-5; in the TRANSITION band (bound >= 1e-5 but
  true mass < 1e-5 — the monotone #terms*pmf(k) bound is loose there)
  relative error degrades monotone-in-mass to the measured worst
  1.689e-4 at mass 1.03e-8 (cdf(2484, 2500, 0.999)).  No frozen
  consumer compares below 8.3e-3 — five decades above the band.
- 537 points compared; 37 below the 1e-290 comparison floor (documented
  subnormal-seed behaviour, counted not compared); the hard-failure
  guard (module 0.0 against an above-floor oracle mass) never fired.
"""

import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from w8_exactness_envelope import QUICK_NS, QUICK_PS, sweep  # noqa: E402

EVIDENCE = (ROOT / "evidence" / "2026-10-14-w8-exactness-envelope"
            / "envelope-full.json")
EVIDENCE_SHA256 = ("b86642010de08e512b0fac0ad0098d937faf0c07e"
                   "b64864bbd569f20f3cd725b")

# (max_rel, argmax [k, n, p], oracle mass at argmax) — deterministic.
FULL_MAX = {
    "binom_cdf": {
        "short_side": (6.400277184396893e-11, [2429, 4999, 0.5],
                       0.023840898482816217),
        "deep_direct": (6.755775548281594e-11, [4611, 4999, 0.95],
                        5.2490849299333095e-17),
        "complement": (0.00016885795311436137, [2484, 2500, 0.999],
                       1.0332231439817974e-08),
    },
    "binom_sf_ge": {
        "short_side": (7.3416051016658e-11, [2500, 4999, 0.5],
                       0.4999999999975286),
        "deep_direct": (6.792988945588077e-11, [389, 4999, 0.05],
                        3.2600952213040047e-17),
        "complement": (0.00009857730143632725, [1403, 4999, 0.25],
                       4.148343783686462e-07),
    },
}

QUICK_MAX = {
    "binom_cdf": {
        "short_side": (4.960485306387786e-12, [250, 1000, 0.25],
                       0.5169865459089759),
        "deep_direct": (3.978482183294479e-12, [631, 1000, 0.753304],
                        6.226709219079718e-18),
        "complement": (3.680180700225249e-06, [686, 1000, 0.753304],
                       8.944521852526522e-07),
    },
    "binom_sf_ge": {
        "short_side": (4.930370372010139e-12, [754, 1000, 0.753304],
                       0.49673681617824467),
        "deep_direct": (3.838379069402401e-12, [373, 1000, 0.25],
                        5.366782778015997e-18),
        "complement": (3.872727137789232e-06, [318, 1000, 0.25],
                       7.710035260758047e-07),
    },
}

TWO_METHOD_BAR = 1e-10
COMPLEMENT_SAFE_DECADes = -5        # masses >= 1e-5
COMPLEMENT_SAFE_BAR = 1e-8
TRANSITION_BUCKETS = {              # decade -> (cdf, sf_ge) pinned
    "-8": (0.00016885795311436137, None),
    "-7": (8.9649873904734e-05, 9.857730143632725e-05),
    "-6": (3.806882339501406e-05, 4.757342938442594e-06),
}


class EnvelopeEvidencePins(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.full = json.loads(EVIDENCE.read_text())

    def test_evidence_sha256(self):
        got = hashlib.sha256(EVIDENCE.read_bytes()).hexdigest()
        self.assertEqual(got, EVIDENCE_SHA256)

    def test_full_grid_point_counts(self):
        self.assertEqual(self.full["points_compared"], 537)
        self.assertEqual(self.full["points_below_floor"], 37)
        self.assertEqual(self.full["grid"], "full")

    def test_full_grid_class_maxima(self):
        for helper, classes in FULL_MAX.items():
            for cls_name, (max_rel, argmax, mass) in classes.items():
                got = self.full["per_helper"][helper][cls_name]
                self.assertEqual(got["max_rel"], max_rel,
                                 msg=f"{helper}.{cls_name}.max_rel")
                self.assertEqual(got["argmax_k_n_p"], argmax,
                                 msg=f"{helper}.{cls_name}.argmax")
                self.assertEqual(got["mass_at_argmax"], mass,
                                 msg=f"{helper}.{cls_name}.mass")

    def test_direct_classes_hold_two_method_bar(self):
        """short_side and deep_direct <= 1e-10 relative domain-wide —
        the bar tick 131 verified at six points now holds across the
        whole grid."""
        for helper, classes in FULL_MAX.items():
            for cls_name in ("short_side", "deep_direct"):
                self.assertLessEqual(classes[cls_name][0], TWO_METHOD_BAR,
                                     msg=f"{helper}.{cls_name}")

    def test_complement_safe_above_transition(self):
        """Complement masses >= 1e-5: every decade bucket <= 1e-8."""
        for helper in FULL_MAX:
            buckets = self.full["per_helper"][helper]["complement"][
                "decade_buckets"]
            for decade, rel in buckets.items():
                if int(decade) >= COMPLEMENT_SAFE_DECADes:
                    self.assertLessEqual(rel, COMPLEMENT_SAFE_BAR,
                                         msg=f"{helper} decade {decade}")

    def test_transition_band_measured_and_monotone(self):
        """The transition band (mass < 1e-5, bound >= 1e-5): pinned
        worst cases, and error grows monotonically as mass shrinks."""
        for helper in FULL_MAX:
            buckets = {
                int(d): rel for d, rel in
                self.full["per_helper"][helper]["complement"][
                    "decade_buckets"].items()
            }
            deep = [d for d in buckets if d < COMPLEMENT_SAFE_DECADes]
            for d in sorted(deep):
                self.assertGreaterEqual(buckets[d],
                                        buckets.get(d + 1, 0.0),
                                        msg=f"{helper} monotone at {d}")
        cdf_b = self.full["per_helper"]["binom_cdf"]["complement"][
            "decade_buckets"]
        sf_b = self.full["per_helper"]["binom_sf_ge"]["complement"][
            "decade_buckets"]
        self.assertEqual(cdf_b["-8"], TRANSITION_BUCKETS["-8"][0])
        self.assertEqual(cdf_b["-7"], TRANSITION_BUCKETS["-7"][0])
        self.assertEqual(sf_b["-7"], TRANSITION_BUCKETS["-7"][1])
        self.assertEqual(cdf_b["-6"], TRANSITION_BUCKETS["-6"][0])
        self.assertEqual(sf_b["-6"], TRANSITION_BUCKETS["-6"][1])


class EnvelopeQuickRecompute(unittest.TestCase):
    """The quick grid recomputes bit-identically from the live module —
    any future walk-bit change flips these pins (bit-conservatism)."""

    @classmethod
    def setUpClass(cls):
        cls.quick = sweep(QUICK_NS, QUICK_PS)

    def test_quick_point_counts(self):
        self.assertEqual(self.quick["points_compared"], 66)
        self.assertEqual(self.quick["points_below_floor"], 2)

    def test_quick_class_maxima(self):
        for helper, classes in QUICK_MAX.items():
            for cls_name, (max_rel, argmax, mass) in classes.items():
                got = self.quick["per_helper"][helper][cls_name]
                self.assertEqual(got["max_rel"], max_rel,
                                 msg=f"{helper}.{cls_name}.max_rel")
                self.assertEqual(got["argmax_k_n_p"], argmax,
                                 msg=f"{helper}.{cls_name}.argmax")
                self.assertEqual(got["mass_at_argmax"], mass,
                                 msg=f"{helper}.{cls_name}.mass")


if __name__ == "__main__":
    unittest.main()
