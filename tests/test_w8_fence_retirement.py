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

TICK 131 SUPERSEDES THE FLOOR (deep-tail direct switch, symmetric
tails): when the tail mass is provably below 1e-5 (the monotone
#terms*pmf(k) bound on the mode's side of the pivot), binom_cdf /
binom_sf_ge route to the direct short-side walk instead of the
1 − x branch — relative-exact (~1e-11) at ANY depth, symmetric for
both tails. The withdrawn crossing is repaired: α_m=2e-22 now gives
(3461, 4055), BOTH ends outside the retired ±9σ window (3481, 4051),
verified against the independent logsumep on both sides. The three
floor pins below are corrected to the exact values (history kept in
docstrings); full symmetry pins live in test_w8_deep_tail_symmetry.
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

    def test_resolution_floor_repaired_exact(self):
        """Tick-131 correction: the floored deep lower tail is now exact.

        Tick-130 history: k=3461 (the TRUE crossing of 1e-22) and k=3563
        (true 3.37e-11) computed to 0.0 through the 1 - x branch. The
        deep-tail direct switch (tail mass provably < 1e-5: bounds
        9.3e-20 / 2.3e-8) routes both to the direct down-walk.
        """
        self.assertGreaterEqual(_cdf_independent(3461, N, P), 1e-22)
        self.assertLess(_cdf_independent(3460, N, P), 1e-22)
        computed = binom_cdf(3461, N, P)
        self.assertEqual(computed, 1.0091961624198102e-22)
        self.assertLess(abs(computed - _cdf_independent(3461, N, P))
                        / _cdf_independent(3461, N, P), 1e-9)
        computed63 = binom_cdf(3563, N, P)
        self.assertEqual(computed63, 3.3674510443081154e-11)
        self.assertLess(abs(computed63 - _cdf_independent(3563, N, P))
                        / _cdf_independent(3563, N, P), 1e-9)

    def test_first_decade_wrongness_repaired(self):
        """Tick-131 correction: the 7x-wrong first-decade value is exact.

        Tick-130 history: the 1 - x branch computed 5.965672400520816e-12
        at k=3564 where the independent logsumep gives 4.15992404828027e-11
        (~6.97x wrong), converging to ~3% by true ~1e-9 (k=3580 computed
        1.0389942239896754e-09 vs 1.0742669044362198e-09). Both points
        now take the direct down-walk (bounds 2.8e-8 / 6.8e-7 < 1e-5).
        """
        computed = binom_cdf(3564, N, P)
        self.assertEqual(computed, 4.159924048444505e-11)
        self.assertLess(abs(computed - _cdf_independent(3564, N, P))
                        / _cdf_independent(3564, N, P), 1e-9)
        computed80 = binom_cdf(3580, N, P)
        self.assertEqual(computed80, 1.0742669044780542e-09)
        self.assertLess(abs(computed80 - _cdf_independent(3580, N, P))
                        / _cdf_independent(3580, N, P), 1e-9)

    def test_both_crossings_exact_beyond_retired_fence(self):
        """Tick-131: α_m=2e-22 gives (3461, 4055) — BOTH crossings now
        exact and BOTH outside the retired ±9σ window (3481, 4051). The
        tick-130 withdrawal of the lower crossing (k_high came back 3564,
        resolution-limited) is repaired by the deep-tail direct switch."""
        kh, kl = cp_accept_window(N, 2e-22, P)
        self.assertEqual(kh, 3461)  # the true crossing (was 3564, floored)
        self.assertEqual(kl, 4055)
        # the retired fence would have rejected BOTH ends of this window
        sigma = math.sqrt(N * P * (1.0 - P))
        wlo = max(0, int(N * P - 9.0 * sigma - 10.0))
        whi = min(N, int(math.ceil(N * P + 9.0 * sigma + 10.0)))
        self.assertEqual((wlo, whi), (3481, 4051))
        self.assertLess(kh, wlo)
        self.assertGreater(kl, whi)
        # defining equations, byte-level on the helper ...
        self.assertEqual(binom_sf_ge(4055, N, P), 8.911166361078581e-23)
        self.assertEqual(binom_sf_ge(4054, N, P), 1.256186946808807e-22)
        # ... and inequality-level on the independent logsumep, both sides
        self.assertLess(_sf_independent(4055, N, P), 1e-22)
        self.assertGreaterEqual(_sf_independent(4054, N, P), 1e-22)
        self.assertLess(_cdf_independent(3460, N, P), 1e-22)
        self.assertGreaterEqual(_cdf_independent(3461, N, P), 1e-22)

    def test_family_alpha_eight_orders_above_floor(self):
        """Domain: α_m ≥ 8.3e-3 at family levels; floor ~4.2e-11."""
        half = ALPHA_FAMILY / 6 / 2
        self.assertGreater(half / 4.15992404828027e-11, 1e8)


if __name__ == "__main__":
    unittest.main()
