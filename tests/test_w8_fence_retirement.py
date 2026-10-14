"""Tick 130 pins: the ±9σ underflow fence is RETIRED (tools/
w8_dependence_stress.py) and the honest resolution floor of the shared
helpers is measured. Every number is byte-reproducible (no RNG; exact
binomial sums; independent per-term-lgamma logsumep cross-checks).

Retirement (the recorded tick-128 follow-up, executed after tick 129's
anchored re-seed repair 1fe220b): cp_accept_window's two crossing
searches now binary-search the full [0, n] range instead of an
assert-bracketed np ± 9σ window.

MEASURED HONESTY (catch #8 in the measure-then-pin streak): a
lower-tail value with k > n/2 resolves through binom_cdf's 1 − x
branch, whose noise floor is lgamma-cancellation scale (~1e-11
RELATIVE to the O(1) complement mass, inherited by the whole up-walk)
— NOT the "~1e-13" walk-rounding scale the tick-129 docstring
recorded. At n=4999, p=0.753304: every true cdf below ~4e-11 computes
to 0.0 (the true 1e-22 crossing sits at k=3461 — floored), and the
first decade above the floor is wrong by up to ~7x (computed
5.965672400520816e-12 at k=3564 where an independent logsumep gives
4.15992404828027e-11) before converging. Upper-tail crossings have no
such floor: sf_ge sums the short upper side directly and stays exact
at any depth — verified at α_m=2e-22 where k_low=4055 sits 9.5σ beyond
np, OUTSIDE the old ±9σ window (3481, 4051): the measurement the
retired fence would have rejected outright.

Domain statement pinned: full-range search is exact for α_m ≥ 1e-8
(half ≥ 5e-9, >100x above the measured floor); this module's family
levels (α_m ≥ 8.3e-3) sit eight orders above it. The first-draft
"beyond-9σ unlock at α_m=2e-22" for the LOWER crossing was overreach
and is withdrawn with numbers: k_high comes back 3564
(resolution-limited), not the true 3461.
"""

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from w8_census_sim import _world_a_rates, _world_b_rates  # noqa: E402
from w8_dependence_stress import ALPHA_FAMILY, _coverage, cp_accept_window  # noqa: E402
from w8_exact_bands import binom_cdf, binom_sf_ge  # noqa: E402

# Reference windows captured from the FENCED code immediately before
# the tick-130 edit (bit-conservatism: retirement changes no value).
FENCED_REFERENCE_A = [  # m = 6, strata in _world_a_rates order
    (4999, 0.7373036780152723, 3603, 3768, 0.9919842558091475),
    (4998, 0.7373036780152723, 3602, 3768, 0.9923690193774849),
    (4999, 0.7373036780152723, 3603, 3768, 0.9919842558091475),
    (4999, 0.7373036780152723, 3603, 3768, 0.9919842558091475),
    (4998, 0.7373036780152723, 3602, 3768, 0.9923690193774849),
    (4996, 0.7373036780152723, 3601, 3766, 0.9920080436050464),
]
FENCED_REFERENCE_B = [  # m = 4, strata in _world_b_rates order
    (500, 0.75, 350, 400, 0.9902664157463819),
    (153, 0.6928104575163399, 91, 121, 0.9916366738675969),
    (500, 0.778, 365, 413, 0.9903000709902401),
    (499, 0.7314629258517034, 340, 390, 0.988518038172168),
]

N, P = 4999, 0.753304  # the stratum where the tick-128 hazard fired


def _cdf_independent(k: int, n: int, p: float) -> float:
    """P(X <= k) by per-term lgamma + logsumep (no shared code)."""
    logs = [math.lgamma(n + 1) - math.lgamma(j + 1) - math.lgamma(n - j + 1)
            + j * math.log(p) + (n - j) * math.log1p(-p)
            for j in range(k + 1)]
    m = max(logs)
    return math.exp(m + math.log(math.fsum(math.exp(x - m) for x in logs)))


def _sf_independent(k: int, n: int, p: float) -> float:
    """P(X >= k) by per-term lgamma + logsumep (no shared code)."""
    logs = [math.lgamma(n + 1) - math.lgamma(j + 1) - math.lgamma(n - j + 1)
            + j * math.log(p) + (n - j) * math.log1p(-p)
            for j in range(k, n + 1)]
    m = max(logs)
    return math.exp(m + math.log(math.fsum(math.exp(x - m) for x in logs)))


class FenceRetirementPins(unittest.TestCase):

    def test_frozen_strata_windows_bit_conservative(self):
        """Full-range searches reproduce the fenced windows byte-for-byte."""
        for world, m in (("A", 6), ("B", 4)):
            rates, ns = (_world_a_rates() if world == "A" else _world_b_rates())
            reference = FENCED_REFERENCE_A if world == "A" else FENCED_REFERENCE_B
            for (p, n), (rn, rp, kh_ref, kl_ref, cov_ref) in zip(
                    zip(rates, ns), reference):
                self.assertEqual((n, p), (rn, rp))  # stratum identity
                kh, kl = cp_accept_window(n, ALPHA_FAMILY / m, p)
                self.assertEqual((kh, kl), (kh_ref, kl_ref))
                self.assertEqual(
                    _coverage("bonferroni_cp", m, n, p), cov_ref)

    def test_resolution_floor_zero_below(self):
        """True cdf below ~4e-11 computes to 0.0 on the 1 − x branch."""
        # k=3461: the TRUE crossing of 1e-22 (independent logsumep) — floored.
        self.assertGreaterEqual(_cdf_independent(3461, N, P), 1e-22)
        self.assertLess(_cdf_independent(3460, N, P), 1e-22)
        self.assertEqual(binom_cdf(3461, N, P), 0.0)
        # k=3563: true 3.367e-11, an order above 1e-22 — still floored.
        self.assertEqual(binom_cdf(3563, N, P), 0.0)

    def test_first_nonzero_wrong_by_seven_x(self):
        """First resolvable value is wrong by ~7x — pinned honestly."""
        computed = binom_cdf(3564, N, P)
        truth = _cdf_independent(3564, N, P)
        self.assertEqual(computed, 5.965672400520816e-12)
        self.assertAlmostEqual(
            truth / computed, 4.15992404828027e-11 / 5.965672400520816e-12,
            delta=0.05)  # ~6.97x — the honest first-decade wrongness
        # and it converges: by true ~1e-9 the relative error is ~3%.
        self.assertAlmostEqual(
            binom_cdf(3580, N, P) / _cdf_independent(3580, N, P),
            1.0389942239896754e-09 / 1.0742669044362198e-09,
            places=2)

    def test_upper_crossing_exact_beyond_retired_fence(self):
        """α_m=2e-22: k_low=4055 sits OUTSIDE the old ±9σ window and is
        exact (short upper side summed directly); k_high is
        resolution-limited at 3564, not the true 3461 — withdrawn."""
        kh, kl = cp_accept_window(N, 2e-22, P)
        self.assertEqual(kh, 3564)  # floored (true crossing 3461)
        self.assertEqual(kl, 4055)
        # the retired fence would have rejected this very call
        sigma = math.sqrt(N * P * (1.0 - P))
        whi = min(N, int(math.ceil(N * P + 9.0 * sigma + 10.0)))
        self.assertEqual(whi, 4051)
        self.assertGreater(kl, whi)
        # defining equations, byte-level on the helper ...
        self.assertEqual(binom_sf_ge(4055, N, P), 8.911166361078581e-23)
        self.assertEqual(binom_sf_ge(4054, N, P), 1.256186946808807e-22)
        # ... and inequality-level on the independent logsumep
        self.assertLess(_sf_independent(4055, N, P), 1e-22)
        self.assertGreaterEqual(_sf_independent(4054, N, P), 1e-22)

    def test_family_alpha_eight_orders_above_floor(self):
        """Domain: α_m ≥ 8.3e-3 at family levels; floor ~4.2e-11."""
        half = ALPHA_FAMILY / 6 / 2
        self.assertGreater(half / 4.15992404828027e-11, 1e8)


if __name__ == "__main__":
    unittest.main()
