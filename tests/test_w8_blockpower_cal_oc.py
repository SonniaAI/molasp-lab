"""Pins for tools/w8_blockpower_cal_oc.py (tick 141, SON-5152).

Pre-datum operating characteristics of the CAL exact-match VOID gate —
the FIRST branch of the frozen tick-120 arbitration map, and the last
one nobody had measured: the instrument replays the 500-seed CAL window
(260261107+[0,500)) and VOIDs unless the mid-window pair census returns
EXACTLY D2T 367 : L2 131 (implicitly other = 2). Measured first, then
frozen (house rule). Zero kTAM trajectories, none of the probe's virgin
seed windows consumed, no gate executed, ladder stays PAUSED, no branch
of the frozen map touched or re-derived.

Headline the pins guard: under independent per-seed corruption at rate
eps, the gate's pass probability is (1-eps)^498 (dropout kernel) — 5%
mismatch already at eps = 1.03e-4, i.e. the CAL is ~385x more sensitive
to per-seed corruption than the NO_EVENTS floor (5% only at the tick-140
other-rate 3.96e-2), and corruption that still escapes the CAL with 95%
probability displaces each group census by 0.37 seeds (dropout; 0.94
reshuffle) — under 0.5% / 1.2% of the smallest pre-registered effect
(delta 0.0223 = 79.4 seeds). Corruption large enough to matter
verdict-wise trips the CAL near-certainly: pass 1.8e-9 at the tick-140
collapse yield. The gate's coherence rests on the deterministic replay
of committed seeds (9 consecutive identity runs; the CAL measures
substrate drift, not sampling variation — the historical 0.5% other-rate
is ACROSS seeds, so it cannot fire this gate by statistical chance).
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import unittest
from fractions import Fraction

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.w8_blockpower_cal_oc import (  # noqa: E402
    CAL_D2T,
    CAL_L2,
    CAL_N,
    CAL_OTHER,
    DELTAS,
    p_pass_dropout,
    p_pass_reshuffle,
    build_receipt,
)
from tools.w8_blockpower_floor_oc import (  # noqa: E402
    MIN_EVENTS,
    N_PER_GROUP,
    map_risk_two_groups,
    risk_below_float,
)

RECEIPT = os.path.join(ROOT, "evidence", "2026-10-14-w8-blockpower-cal-oc",
                       "cal-oc.json")
RECEIPT_SHA256 = ("d38f09307cc90730f9702bb3e82dc126bd8545d4d9f64e"
                  "b3891901da87ad4970")


def _load() -> dict:
    with open(RECEIPT) as fh:
        return json.load(fh)


class CalOCPins(unittest.TestCase):
    """Receipt pins — every claim above is frozen to the committed bytes."""

    def test_receipt_sha256(self):
        with open(RECEIPT, "rb") as fh:
            digest = hashlib.sha256(fh.read()).hexdigest()
        self.assertEqual(digest, RECEIPT_SHA256)

    def test_receipt_regeneration_byte_identical(self):
        # no RNG, no timestamps: the receipt is a pure function of the
        # frozen gate constants — rebuild and compare bytes
        rebuilt = json.dumps(build_receipt(), indent=1, sort_keys=True)
        with open(RECEIPT) as fh:
            self.assertEqual(rebuilt + "\n", fh.read())

    def test_gate_constants_frozen(self):
        r = _load()
        self.assertEqual((r["gate"]["n_seeds"], r["gate"]["d2t"],
                          r["gate"]["l2"], r["gate"]["other"]),
                         (500, 367, 131, 2))
        self.assertEqual((CAL_N, CAL_D2T, CAL_L2, CAL_OTHER),
                         (500, 367, 131, 2))
        self.assertEqual(r["gate"]["rule"], "EXACT match or VOID")
        # the arbitration side stays the tick-140 constants (imported,
        # never re-implemented)
        self.assertEqual((N_PER_GROUP, MIN_EVENTS), (3560, 3400))

    def test_dropout_closed_form_live(self):
        r = _load()
        self.assertEqual(
            r["kernels"]["dropout"]["curve_eps_to_p_pass"]["0.005"],
            0.08239373898667053)
        self.assertAlmostEqual(p_pass_dropout(0.005),
                               (1.0 - 0.005) ** 498, places=14)
        self.assertAlmostEqual(p_pass_dropout(1e-4),
                               (1.0 - 1e-4) ** 498, places=12)
        # 498 pair seeds: the 2 committed others are unperturbable into
        # a pair reading under the dropout kernel. First-order relation
        # 1 - P ≈ 498*eps carries the O(eps^2) binomial bias
        # C(498,2)*eps^2 ≈ 1.24e-3 at eps = 1e-4 (recorded, not hidden)
        self.assertAlmostEqual(
            1.0 - p_pass_dropout(1e-4), 498 * 1e-4, delta=1.5e-3)

    def test_epsilon_tolerances_ordered_and_cross_checked(self):
        k = _load()["kernels"]
        d, s = k["dropout"], k["reshuffle"]
        # bisection vs the analytic closed-form inversion (dropout)
        self.assertAlmostEqual(d["eps_p05"], d["eps_p05_analytic"],
                               places=12)
        self.assertAlmostEqual(d["eps_p50"], d["eps_p50_analytic"],
                               places=12)
        self.assertAlmostEqual(d["eps_p05"], 0.00010299327893557904,
                               places=18)
        self.assertAlmostEqual(d["eps_p50"], 0.0013908936179543707,
                               places=16)
        # benign kernel strictly more tolerant at every level
        self.assertGreater(s["eps_p05"], d["eps_p05"])
        self.assertGreater(s["eps_p50"], d["eps_p50"])
        self.assertAlmostEqual(s["eps_p05"], 0.00026459219948163533,
                               places=18)
        self.assertAlmostEqual(s["eps_p50"], 0.004406444207983877,
                               places=16)

    def test_eps1_anchor_vs_exact_fraction(self):
        a = _load()["verification"]["eps1_anchor"]
        # at eps = 1 the convolution collapses to the single-term iid
        # multinomial pmf at the committed marginal
        exact = Fraction(a["iid_multinomial_exact_fraction"])
        self.assertAlmostEqual(float(exact), a["iid_multinomial_exact_float"],
                               places=18)
        self.assertAlmostEqual(a["reshuffle_float"],
                               a["iid_multinomial_exact_float"], places=10)
        self.assertLessEqual(a["rel_diff"], 5e-12)
        self.assertAlmostEqual(a["rel_diff"], 1.8289346862103033e-12,
                               places=24)

    def test_first_order_coefficient_matches_hand_derivation(self):
        fo = _load()["verification"]["first_order_coefficient"]
        # d/deps [1 - P_pass] at 0 is exactly (500^2 - 367^2 - 131^2
        # - 2^2)/500 = 49073/250 = 196.292 (reshuffle) and 498 (dropout)
        self.assertEqual(Fraction(fo["exact_fraction"]), Fraction(49073, 250))
        self.assertEqual(fo["exact_float"], 196.292)
        self.assertEqual(fo["dropout_exact"], 498)
        # numeric slope at eps = 1e-7: the residual is the O(eps)
        # second-order bias of the finite difference, bounded < 1e-4
        self.assertLess(
            abs(fo["reshuffle_numeric_at_1e-7"] - fo["exact_float"])
            / fo["exact_float"], 1e-4)
        self.assertLess(
            abs(fo["dropout_numeric_at_1e-7"] - 498) / 498, 1e-4)

    def test_mid_anchor_within_recorded_tail_bound(self):
        m = _load()["verification"][
            "reshuffle_mid_anchor_eps_1_1024"]
        # exact Fraction sum truncated at K <= 10; everything dropped is
        # bounded by the recorded Chernoff term
        self.assertLess(m["tail_bound_float"], 1e-10)
        self.assertLessEqual(m["abs_gap_float_vs_partial"],
                             m["tail_bound_float"])
        self.assertAlmostEqual(m["abs_gap_float_vs_partial"],
                               9.614531393253856e-13, places=26)
        self.assertGreater(m["float_full_sum"], 0.83)

    def test_silent_pass_historical_floor_cross_pins_tick140(self):
        row = _load()["silent_pass_table_dropout"]["0.005"]
        self.assertEqual(row["p_cal_pass"], 0.08239373898667053)
        # the NO_EVENTS arm reuses the tick-140 float walk unchanged:
        # the pinned per-group risk is byte-identical to the tick-140
        # receipt's q = 0.995 row
        r_live = risk_below_float(N_PER_GROUP, MIN_EVENTS, 0.995)[0]
        self.assertEqual(row["per_group_no_events_risk"],
                         3.0967845439759556e-95)
        self.assertEqual(r_live, 3.0967845439759556e-95)
        self.assertAlmostEqual(row["two_group_no_events_risk"],
                               map_risk_two_groups(r_live), delta=0.0)
        self.assertAlmostEqual(row["p_reaches_adjudication"],
                               row["p_cal_pass"]
                               * (1.0 - row["two_group_no_events_risk"]),
                               places=18)
        # at the historical floor the CAL, not the census floor, is the
        # binding guard: 8.2% pass vs a 1e-95 floor risk
        self.assertLess(row["two_group_no_events_risk"], 1e-94)

    def test_silent_pass_at_tick140_collapse(self):
        row = _load()["silent_pass_table_dropout"]["0.0396037"]
        # consistency with the tick-140 q05 inversion: at q = 0.9604 the
        # per-group floor risk sits at ~5% (0.9603653... is the exact
        # q05, so the rounded grid point lands just under it)
        live_at_q05 = risk_below_float(
            N_PER_GROUP, MIN_EVENTS, 0.9603653544224855)[0]
        self.assertLess(abs(row["per_group_no_events_risk"]
                            - live_at_q05), 2e-3)
        self.assertGreater(row["per_group_no_events_risk"], 0.045)
        self.assertLess(row["per_group_no_events_risk"], 0.055)
        # a corruption this large almost never survives the CAL first
        self.assertLess(row["p_cal_pass"], 2e-9)
        self.assertAlmostEqual(row["p_cal_pass"],
                               1.8211183117773637e-09, places=22)
        self.assertLess(row["p_reaches_adjudication"], row["p_cal_pass"])

    def test_verdict_safety_bracket(self):
        v = _load()["verdict_safety"]
        smallest = N_PER_GROUP * DELTAS["d0223_hotrepro"]
        self.assertEqual(v["smallest_effect_seeds"]["d0223_hotrepro"],
                         smallest)
        # corruption that escapes the CAL with >= 95% probability moves
        # each group census by < 1 seed — under 1.2% of the smallest
        # pre-registered effect under BOTH kernels
        self.assertLess(v["escape_displacement_seeds"]["dropout"]
                        / smallest, 0.005)
        self.assertLess(v["escape_displacement_seeds"]["reshuffle"]
                        / smallest, 0.012)
        self.assertAlmostEqual(v["escape_displacement_seeds"]["dropout"],
                               0.3666560730106614, places=15)
        # and verdict-scale corruption VOIDs near-certainly at the CAL
        self.assertLess(v["cal_pass_at_tick140_collapse"], 2e-9)
        self.assertEqual(v["tick140_collapse_q05"], 0.96037)

    def test_kernels_monotone_and_ordered_live(self):
        grid = sorted({1e-7, 1e-6, 1e-5, 1e-4, 5e-4, 1e-3, 5e-3,
                       1e-2, 5e-2})
        prev_d = prev_s = 2.0
        for e in grid:
            d, s = p_pass_dropout(e), p_pass_reshuffle(e)
            self.assertGreaterEqual(prev_d, d)   # monotone down
            self.assertGreaterEqual(prev_s, s)
            if e >= 1e-5:
                # destructive kernel is the pessimistic bracket
                self.assertLess(d, s)
            prev_d, prev_s = d, s

    def test_range_guards(self):
        for bad in (-0.1, 1.5):
            with self.assertRaises(ValueError):
                p_pass_dropout(bad)
            with self.assertRaises(ValueError):
                p_pass_reshuffle(bad)
        # degenerate endpoints are exact, not crashes
        self.assertEqual(p_pass_dropout(0.0), 1.0)
        self.assertEqual(p_pass_reshuffle(0.0), 1.0)
        self.assertGreater(p_pass_reshuffle(1.0), 0.0)


if __name__ == "__main__":
    unittest.main()
