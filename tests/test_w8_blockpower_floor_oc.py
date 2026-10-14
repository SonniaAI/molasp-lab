"""Pins for tools/w8_blockpower_floor_oc.py (tick 140, SON-5152).

Pre-datum operating characteristics of the NO_EVENTS floor branch of the
frozen tick-120 arbitration map: the map fires NO_EVENTS BEFORE any
p-value is read whenever EITHER group's pooled terminal pair census is
< 3400 of 3560 (branch_map in the queued instrument). Measured first,
then frozen (house rule). Zero kTAM trajectories, none of the probe's
virgin seed windows consumed, no gate executed, ladder stays PAUSED,
no branch touched.

Headline the pins guard: at the historical terminal-pair yield
q >= 0.995 (prereg: terminal 'other' <= 0.5% in every committed w8
window) the two-group NO_EVENTS risk is 6.19e-95 — the branch CANNOT
fire by statistical chance under any historically observed yield; it
takes an ~8x collapse of the terminal yield (other-rate 0.5% -> 3.96%)
before the branch even reaches 5% risk, and at the floor edge
(pair_n = 3400/group exactly, the worst census the map still
adjudicates) the exact Fisher instrument still delivers size 0.04325
and power 0.89225 at delta 0.030 — inside the tick-139 n=3560 Wilson
band, so the floor does not erode the arbitration.
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

from tools.w8_blockpower_floor_oc import (  # noqa: E402
    AGREE_BAR,
    FLOOR_EDGE_N,
    MIN_EVENTS,
    N_PER_GROUP,
    Q_HIST,
    map_risk_two_groups,
    risk_below_decimal,
    risk_below_float,
    invert_risk,
)

RECEIPT = os.path.join(ROOT, "evidence", "2026-10-14-w8-blockpower-floor-oc",
                       "floor-oc.json")
RECEIPT_SHA256 = ("9c72da356e0573209e0b78aad0941fe0e070d05c1"
                  "6f62be018a9ebc8fa76303c")


def _load() -> dict:
    with open(RECEIPT) as fh:
        return json.load(fh)


class FloorOCPins(unittest.TestCase):
    """Receipt pins — every claim above is frozen to the committed bytes."""

    def test_receipt_sha256(self):
        with open(RECEIPT, "rb") as fh:
            digest = hashlib.sha256(fh.read()).hexdigest()
        self.assertEqual(digest, RECEIPT_SHA256)

    def test_frozen_constants(self):
        r = _load()
        self.assertEqual(r["n_per_group"], 3560)
        self.assertEqual(r["min_events"], 3400)
        self.assertEqual(r["q_hist_floor"], 0.995)
        self.assertEqual(FLOOR_EDGE_N, MIN_EVENTS)  # worst admissible census

    def test_historical_yield_risk_is_astronomical(self):
        r = _load()
        row = next(c for c in r["yield_curve"] if c["q_yield"] == Q_HIST)
        self.assertAlmostEqual(row["per_group_risk"], 3.0967845439759556e-95,
                               delta=1e-110)
        self.assertLess(row["map_risk_two_groups"], 1e-94)

    def test_map_risk_form_is_cancellation_safe(self):
        # 1 - (1-r)^2 evaluates to exactly 0.0 at small r; the shipped
        # 2r - r^2 form must retain every significant digit.
        self.assertEqual(1.0 - (1.0 - 1e-30) ** 2, 0.0)
        self.assertAlmostEqual(map_risk_two_groups(1e-30), 2e-30,
                               delta=1e-60)
        r = _load()["yield_curve"][-1]
        self.assertAlmostEqual(
            r["map_risk_two_groups"],
            map_risk_two_groups(r["per_group_risk"]), delta=0.0)

    def test_yield_curve_monotone_decreasing_risk(self):
        curve = _load()["yield_curve"]
        risks = [c["per_group_risk"] for c in curve]
        self.assertEqual(len(curve), 20)
        # monotone to within the float walk's own precision: adjacent
        # grid points near q=1 differ by ~5e-15, below the ~4e-13 walk
        # error when the accumulated sum sits at ~1.0
        for a, b in zip(risks, risks[1:]):
            self.assertLessEqual(b, a + 1e-11)

    def test_inversions_ordered_and_finite(self):
        inv = _load()["inversions"]
        self.assertGreater(inv["q_at_5pct_risk"], inv["q_at_50pct_risk"])
        self.assertAlmostEqual(inv["q_at_5pct_risk"], 0.9603653544224855,
                               places=12)
        self.assertAlmostEqual(inv["q_at_50pct_risk"], 0.9548731056040096,
                               places=12)
        self.assertAlmostEqual(inv["other_rate_at_5pct"],
                               0.039634645577514505, places=12)
        # the ~8x yield-collapse multiple, computed from the pinned parts
        self.assertAlmostEqual(inv["other_rate_multiple_at_5pct"],
                               inv["other_rate_at_5pct"] / (1.0 - Q_HIST),
                               places=10)

    def test_two_method_anchors_within_bar_and_nonzero(self):
        anchors = _load()["two_method_anchors"]
        self.assertEqual(len(anchors), 4)
        for a in anchors:
            self.assertLessEqual(a["rel_diff"], AGREE_BAR)
            self.assertGreater(a["rel_diff"], 1e-15)  # a real measurement
            # the stored prec-80 decimal reproduces the float within the
            # claimed relative difference
            self.assertAlmostEqual(
                a["float_risk"], float(a["decimal_risk_prec80"]),
                delta=a["rel_diff"] * float(a["decimal_risk_prec80"]))

    def test_floor_edge_size_and_power(self):
        mc = _load()["floor_edge_mc"]
        size = mc["FLOOR_EDGE_H0_SIZE"]
        power = mc["FLOOR_EDGE_D030_POWER"]
        self.assertEqual(size["rejections"], 173)
        self.assertEqual(size["replicates"], 4000)
        self.assertAlmostEqual(size["reject_rate"], 0.04325, places=6)
        self.assertLessEqual(size["reject_rate_wilson95"][1], 0.050005)
        self.assertEqual(power["rejections"], 3569)
        self.assertAlmostEqual(power["reject_rate"], 0.89225, places=6)
        lo, hi = power["reject_rate_wilson95"]
        self.assertGreater(lo, 0.88)
        self.assertLess(hi, 0.91)
        # floor-edge power stays inside the tick-139 n=3560 Wilson band
        # (0.89775 [0.88798, 0.90676]) — the floor does not erode power
        self.assertLessEqual(lo, 0.90676)

    def test_floor_edge_seeds_disjoint_from_all_committed_families(self):
        mc = _load()["floor_edge_mc"]
        seeds = {mc[k]["seed"] for k in mc}
        self.assertEqual(seeds, {20261020, 20261021})
        # disjoint from tick-139 OC (20261015-19), census-sim
        # (20261013/14) and every trajectory seed family
        self.assertFalse(seeds & set(range(20261013, 20261020)))

    def test_limits_disclose_cutoff_and_ulp_limited_float(self):
        limits = " ".join(_load()["limits"])
        self.assertIn("1e-25", limits)       # recorded negligible-term cutoff
        self.assertIn("prec 80", limits)     # decimal ground truth carries
        self.assertIn("ladder stays PAUSED", limits)

    def test_live_small_n_float_vs_decimal(self):
        # live two-method recompute at n=500, kmax=450, q=9/10 — cheap
        # enough for CI, same guard bar as the receipt
        r_f, _ = risk_below_float(500, 450, 0.9)
        r_d = risk_below_decimal(500, 450, 9, 10)
        self.assertLess(abs(r_f - float(r_d)) / float(r_d), AGREE_BAR)

    def test_live_inverter_sanity_at_small_n(self):
        # Bin(200, q): the 50% risk point of P(X <= 169) sits at the
        # mode boundary q ~ 170/200 = 0.85 (normal-corrected slightly
        # down); brackets must be passed for this regime
        q50 = invert_risk(200, 170, 0.50, lo=0.80, hi=0.90)
        self.assertGreater(q50, 0.84)
        self.assertLess(q50, 0.86)


if __name__ == "__main__":
    unittest.main()
