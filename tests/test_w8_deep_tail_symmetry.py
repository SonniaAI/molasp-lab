"""Tick 131 pins (switch-edge and transition pins updated tick 134):
SYMMETRIC deep-tail exactness for both binomial tail
helpers (tools/w8_exact_bands.py). Every number is byte-reproducible
(no RNG; exact binomial sums; independent per-term-lgamma logsumep
cross-checks — no shared code with the module under test).

The tick-130 measurement this repairs: the 1 - x branch of binom_cdf
(k > n/2) floors at lgamma-cancellation scale ~4e-11 ABSOLUTE at
n=4999, p=0.753304 — everything below computed to 0.0, the first
decade above wrong by up to ~7x — while sf_ge's direct short-side
sums stay ~13-digit exact at ANY depth. The tick-131 fix: when the
tail mass is PROVABLY below _DEEP_TAIL_DIRECT_SWITCH = 1e-5 (the
monotone #terms*pmf(k) bound on the mode's side of the pivot, pmf
being unimodal), the 1 - x complement is routed to the direct
short-side walk instead — relative-exact (~1e-11) at any depth, for
BOTH tails symmetrically.

Pinned here:
- The six deep lower-tail points (k=2601..3580) exact vs the
  independent logsumep (rel <= 1e-9; measured <= 7e-11), byte-pinned.
- The un-withdrawn crossing: cp_accept_window(4999, 2e-22, 0.753304)
  = (3461, 4055) — BOTH crossings outside the retired ±9σ window
  (3481, 4051), defining equations inequality-verified independently
  on both sides.
- The mirror world p -> 1-p: window (945, 1539), exercising the
  sf_ge guard (mode 1233 < k < n/2), with the reflection identity
  sf_ge(1538, q) == cdf(3461, p) to ~2e-12 relative.
- The switch edges (tick 134, geometric bound): _deep_lower_direct
  fires through k=3633, off from 3634 (through tick 133 it fired
  through 3594 / off 3595 under the count bound). The tick-131
  transition disclosure (0.09% at k=3600, true 4.4e-8) is retired:
  k=3600 now routes direct (4.4276521107896456e-08, rel 4.6e-11);
  the complement persists at k=3700 (rel ~1.6e-9, mass ~1.7e-2).
- The honest floor: below the subnormal seed (~e^-708.4 per term)
  the walk returns 0.0 (cdf(2500), true ~1e-324) — monotone-correct;
  the alpha_m=1e-300 window (2549, 4741) is exact at the floor's
  edge (defining level half = 5e-301), both crossings
  inequality-verified independently, and the walk's ~7e-301 values
  additionally checked against an exact-integer-factorial Decimal
  partial sum to ~7e-11 relative.
"""

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from w8_dependence_stress import cp_accept_window  # noqa: E402
from w8_exact_bands import (  # noqa: E402
    _DEEP_TAIL_DIRECT_SWITCH,
    _deep_lower_direct,
    _deep_upper_direct,
    binom_cdf,
    binom_sf_ge,
)

N, P = 4999, 0.753304
Q = 1.0 - P

# byte-pins captured this tick (deterministic module, no RNG)
DEEP_CDF_PINS = {
    2601: 5.082067281969146e-277,
    3000: 1.681271165456129e-125,
    3461: 1.0091961624198102e-22,
    3563: 3.3674510443081154e-11,
    3564: 4.159924048444505e-11,
    3580: 1.0742669044780542e-09,
}


def _log_pmf(j: int, n: int, p: float) -> float:
    return (math.lgamma(n + 1) - math.lgamma(j + 1) - math.lgamma(n - j + 1)
            + j * math.log(p) + (n - j) * math.log1p(-p))


def _cdf_independent(k: int, n: int, p: float) -> float:
    logs = [_log_pmf(j, n, p) for j in range(k + 1)]
    m = max(logs)
    return math.exp(m + math.log(math.fsum(math.exp(x - m) for x in logs)))


def _sf_independent(k: int, n: int, p: float) -> float:
    logs = [_log_pmf(j, n, p) for j in range(k, n + 1)]
    m = max(logs)
    return math.exp(m + math.log(math.fsum(math.exp(x - m) for x in logs)))


class DeepTailSymmetryPins(unittest.TestCase):

    def test_switch_constant_and_edges(self):
        """The switch and its flip point: fires through k=3633, off
        from 3634 (geometric bound crosses 1e-5; through tick 133
        the count-bound edge was 3594/3595); never above the mode."""
        self.assertEqual(_DEEP_TAIL_DIRECT_SWITCH, 1e-5)
        for k in (2601, 3000, 3461, 3563, 3564, 3580, 3594, 3595,
                  3620, 3633):
            self.assertTrue(_deep_lower_direct(k, N, P), msg=f"k={k}")
        for k in (3634, 3700, 3766, 4000):
            self.assertFalse(_deep_lower_direct(k, N, P), msg=f"k={k}")
        # mirror guard: fires at the deep upper tail with k < n/2 (p<1/2),
        # not below the mode
        self.assertTrue(_deep_upper_direct(1539, N, Q))
        self.assertFalse(_deep_upper_direct(1000, N, Q))

    def test_deep_lower_tail_exact_vs_independent(self):
        """Six deep points, six decades of scale: relative-exact."""
        for k, pinned in DEEP_CDF_PINS.items():
            computed = binom_cdf(k, N, P)
            truth = _cdf_independent(k, N, P)
            self.assertEqual(computed, pinned, msg=f"k={k}")
            self.assertLess(abs(computed - truth) / truth, 1e-9,
                            msg=f"k={k}")

    def test_withdrawn_lower_crossing_unwithdrawn(self):
        """α_m=2e-22 at P: (3461, 4055), both crossings exact, both
        outside the retired ±9σ window (3481, 4051)."""
        kh, kl = cp_accept_window(N, 2e-22, P)
        self.assertEqual((kh, kl), (3461, 4055))
        self.assertLess(_cdf_independent(3460, N, P), 1e-22)
        self.assertGreaterEqual(_cdf_independent(3461, N, P), 1e-22)
        self.assertLess(_sf_independent(4055, N, P), 1e-22)
        self.assertGreaterEqual(_sf_independent(4054, N, P), 1e-22)

    def test_mirror_window_and_reflection(self):
        """p -> 1-p mirrors the window: (945, 1539); k_low exercises
        the sf_ge guard (mode 1233 <= 1539 < n/2); reflection identity
        sf_ge(1538, q) == cdf(3461, p) holds to ~2e-12 relative."""
        kh, kl = cp_accept_window(N, 2e-22, Q)
        self.assertEqual((kh, kl), (945, 1539))
        self.assertEqual(kh, N - 4055 + 1)   # mirror of k_low(P)
        self.assertEqual(kl, N - 3461 + 1)   # mirror of k_high(P)
        self.assertLess(_cdf_independent(944, N, Q), 1e-22)
        self.assertGreaterEqual(_cdf_independent(945, N, Q), 1e-22)
        self.assertLess(_sf_independent(1539, N, Q), 1e-22)
        self.assertGreaterEqual(_sf_independent(1538, N, Q), 1e-22)
        sf = binom_sf_ge(1538, N, Q)
        cdf = binom_cdf(3461, N, P)
        self.assertEqual(sf, 1.0091961624215313e-22)
        self.assertLess(abs(sf - cdf) / cdf, 1e-9)

    def test_one_x_transition_disclosed(self):
        """Tick 134 retired the old transition disclosure: k=3600
        took the 1 - x path through tick 133 (0.09% rel error, pinned
        4.423649579976541e-08); with the geometric tail-ratio bound
        the guard fires there and the direct walk returns
        4.4276521107896456e-08 (rel 4.6e-11). The complement survives
        at k=3700 (bound ~1.9e-2, mass ~1.7e-2) with rel ~1.6e-9 —
        residual mid-tail behaviour, now far from any deep mass."""
        c600 = binom_cdf(3600, N, P)
        self.assertEqual(c600, 4.4276521107896456e-08)
        self.assertLess(abs(c600 - _cdf_independent(3600, N, P))
                        / _cdf_independent(3600, N, P), 1e-9)
        c700 = binom_cdf(3700, N, P)
        self.assertLess(abs(c700 - _cdf_independent(3700, N, P))
                        / _cdf_independent(3700, N, P), 1e-8)

    def test_subnormal_floor_and_deep_deepest_window(self):
        """Below the subnormal seed (~e^-708.4/term) the walk returns
        0.0 — monotone-correct; the alpha_m=1e-300 window (2549, 4741)
        is exact at the floor's edge, both crossings verified at the
        defining level half = alpha_m/2 = 5e-301. (In-tick catch: the
        first draft of this test pinned the inequalities at 1e-300 —
        the wrong level, alpha_m instead of alpha_m/2; the module was
        right, and the walk's values at ~7e-301 were additionally
        verified against an exact-integer-factorial Decimal partial
        sum to ~7e-11 relative — module vs logsumep vs Decimal, three
        independent computations agreeing.)"""
        self.assertEqual(binom_cdf(2500, N, P), 0.0)  # true ~1e-324
        half = 1e-300 / 2.0
        kh, kl = cp_accept_window(N, 1e-300, P)
        self.assertEqual((kh, kl), (2549, 4741))
        self.assertLess(_cdf_independent(2548, N, P), half)
        self.assertGreaterEqual(_cdf_independent(2549, N, P), half)
        self.assertLess(_sf_independent(4741, N, P), half)
        self.assertGreaterEqual(_sf_independent(4740, N, P), half)
        computed = binom_cdf(2549, N, P)
        self.assertEqual(computed, 7.093841273336218e-301)
        self.assertLess(abs(computed - _cdf_independent(2549, N, P))
                        / _cdf_independent(2549, N, P), 1e-9)


if __name__ == "__main__":
    unittest.main()
