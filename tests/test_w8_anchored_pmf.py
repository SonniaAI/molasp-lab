"""Tick 129: anchored re-seed repair of _pmf_terms' seed-underflow hazard.

The tick-128 dependence stress fenced (but did not fix) a seed-underflow
hazard inherited from tick 127's _pmf_terms: when the direct walk seed
pmf(j_start) is not a normal double, the O(1) recurrence is corrupt from
its first step --

  * a 0.0 seed stays 0.0 forever: binom_sf_ge(2500, 4999, 0.7533)
    returned 0.0 where the truth is 1 - ~4e-12;
  * a DEEP-TAIL seed (subnormal or merely far down) carries
    lgamma-cancellation-scale (~1e-11) relative error that every later
    term inherits, and the branches exposed impossible values:
    cdf(2601, 4999, 0.753304) = -6.3308...e-11 (negative) and
    sf_ge(2601, ...) = 1.0000000000639078 (> 1) -- both measured
    pre-repair; both now clamped into [0, 1], and seeds below
    min-normal re-anchor so the corruption cannot start at all.

The repair re-anchors the walk at the mode (or the interval endpoint
nearest the mode) whenever the direct seed's log-pmf is below the
min-normal double; healthy-seed calls take the original path
bit-for-bit, so every pinned tick-127/128 number is unchanged.

These tests cross-check against an INDEPENDENT implementation (per-term
lgamma + running logsumexp -- a different algorithm, not a copy), pin
the repair battery, pin the bit-conservatism of healthy paths against
an inline copy of the original recurrence, and pin the concatenation
invariant that the first draft of the fix itself got wrong (it dropped
the anchored seed term pmf(anchor), missing the mode's ~0.0131 mass and
returning 0.9869... where the truth is ~1.0 -- caught before pinning).

Zero kTAM trajectories, no gate, stdlib only, no RNG.
"""

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from w8_exact_bands import (  # noqa: E402
    _LOG_MIN_NORMAL,
    _log_factorials,
    _pmf_terms,
    binom_cdf,
    binom_sf_ge,
    clopper_pearson,
)


# ---------------------------------------------------------------------------
# independent verifier: per-term lgamma + running logsumexp (different
# algorithm from the module's log-factorial-seeded O(1) recurrence)
# ---------------------------------------------------------------------------

def _logpmf_indep(j, n, p):
    return (math.lgamma(n + 1) - math.lgamma(j + 1) - math.lgamma(n - j + 1)
            + j * math.log(p) + (n - j) * math.log1p(-p))


def sf_ge_indep(k, n, p):
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    m = _logpmf_indep(k, n, p)
    acc = m
    for j in range(k + 1, n + 1):
        m += (math.log((n - j + 1) / j)
              + math.log(p) - math.log1p(-p))
        if m > acc:
            acc = m + math.log1p(math.exp(acc - m))
        else:
            acc = acc + math.log1p(math.exp(m - acc))
    return math.exp(acc)


def cdf_indep(k, n, p):
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    m = _logpmf_indep(k, n, p)
    acc = m
    for j in range(k - 1, -1, -1):
        m += (math.log(j + 1) - math.log(n - j)
              + math.log1p(-p) - math.log(p))
        if m > acc:
            acc = m + math.log1p(math.exp(acc - m))
        else:
            acc = acc + math.log1p(math.exp(m - acc))
    return math.exp(acc)


def _original_pmf_terms(j_start, j_end, n, p):
    """Inline copy of the PRE-repair recurrence, for bit-conservatism."""
    if j_start == j_end:
        lf = _log_factorials(n)
        return [math.exp(lf[n] - lf[j_start] - lf[n - j_start]
                         + j_start * math.log(p)
                         + (n - j_start) * math.log1p(-p))]
    lf = _log_factorials(n)
    seed = math.exp(lf[n] - lf[j_start] - lf[n - j_start]
                    + j_start * math.log(p)
                    + (n - j_start) * math.log1p(-p))
    ratio_pq = p / (1.0 - p)
    ratio_qp = (1.0 - p) / p
    terms = [seed]
    cur = seed
    if j_end < j_start:
        for j in range(j_start, j_end, -1):
            cur = cur * (j / (n - j + 1)) * ratio_qp
            terms.append(cur)
    else:
        for j in range(j_start, j_end):
            cur = cur * ((n - j) / (j + 1)) * ratio_pq
            terms.append(cur)
    return terms


class AnchoredRepairBattery(unittest.TestCase):
    # (k, n, p): the two documented class-1 zeros, the class-2 corruption,
    # a healthy near-mode call, a healthy deep-upper-tail else-branch call,
    # the p=0.5 symmetry case, and the two boundary cases.
    SF_CASES = [
        (2500, 4999, 0.7533),      # was 0.0; truth 1 - 4e-12
        (2500, 4999, 0.753304),    # was 0.0; truth 1 - 4e-12
        (2601, 4999, 0.753304),    # was 1.0000000000639078 (> 1)
        (3766, 4999, 0.753304),    # healthy: 0.50459576964362
        (4500, 4999, 0.753304),    # healthy: 2.613964657949628e-154
        (2500, 4999, 0.5),         # symmetry: truth exactly 0.5
        (0, 4999, 0.753304),       # identity: 1 - q^n
        (4999, 4999, 0.753304),    # identity: p^n (underflows to 0.0)
    ]

    def test_sf_ge_battery_vs_independent(self):
        for k, n, p in self.SF_CASES:
            got = binom_sf_ge(k, n, p)
            ref = sf_ge_indep(k, n, p)
            # the independent method's own 2500-step logsumexp error bar is
            # ~1e-11 absolute on O(1) values; the module's lgamma-seeded
            # recurrence is ~1e-11 on the same walks, so 1e-10 is the honest
            # two-method bar (both are far more accurate than any consumer).
            self.assertLessEqual(
                abs(got - ref), 1e-10,
                msg=f"sf_ge({k},{n},{p}) = {got!r} vs indep {ref!r}")

    def test_documented_corruptions_repaired(self):
        self.assertEqual(binom_sf_ge(2500, 4999, 0.7533), 1.0)
        self.assertEqual(binom_sf_ge(2500, 4999, 0.753304), 1.0)
        # impossible values gone: everything in [0, 1]
        for k, n, p in self.SF_CASES:
            v = binom_sf_ge(k, n, p)
            self.assertGreaterEqual(v, 0.0)
            self.assertLessEqual(v, 1.0)
        self.assertGreaterEqual(binom_cdf(2601, 4999, 0.753304), 0.0)

    def test_healthy_values_unchanged_spot_pins(self):
        # byte-conservative spot pins (pre-repair measured values)
        self.assertEqual(binom_sf_ge(3766, 4999, 0.753304),
                         0.50459576964362)
        self.assertEqual(binom_sf_ge(4500, 4999, 0.753304),
                         2.613964657949628e-154)
        self.assertEqual(binom_cdf(3766, 4999, 0.753304),
                         0.5084925982028998)

    def test_p_half_symmetry(self):
        # Bin(4999, 0.5) is symmetric about 2499.5, so
        # P(X >= 2500) = exactly 0.5 (both methods carry ~1e-11 walk error)
        self.assertLessEqual(abs(binom_sf_ge(2500, 4999, 0.5) - 0.5),
                             1e-10)

    def test_boundary_identities(self):
        q = 1.0 - 0.753304
        self.assertAlmostEqual(binom_sf_ge(0, 4999, 0.753304),
                               1.0 - q ** 4999, places=12)
        self.assertEqual(binom_sf_ge(4999, 4999, 0.753304), 0.0)  # p^n
        self.assertEqual(binom_sf_ge(-1, 4999, 0.753304), 1.0)
        self.assertEqual(binom_sf_ge(5000, 4999, 0.753304), 0.0)
        self.assertEqual(binom_cdf(-1, 4999, 0.753304), 0.0)
        self.assertEqual(binom_cdf(4999, 4999, 0.753304), 1.0)

    def test_clamped_short_side_documented(self):
        # Known clamp (recorded, not a defect): the shorter-side 1 - x
        # branch cannot resolve a true CDF of ~5e-277 and returns 0.0.
        # No consumer compares at that scale (CP targets are alpha/2 ~4e-3).
        self.assertEqual(binom_cdf(2601, 4999, 0.753304), 0.0)
        self.assertEqual(binom_cdf(2500, 4999, 0.753304), 0.0)
        self.assertEqual(binom_cdf(4500, 4999, 0.753304), 1.0)


class AnchoredPathInvariants(unittest.TestCase):

    def test_anchored_walk_returns_every_term(self):
        # the first-draft fix dropped pmf(anchor) (mode mass ~0.0131) --
        # length and sum invariants pin the concatenation
        for j_start, j_end, n, p in [
            (2500, 4999, 4999, 0.753304),   # up-walk, mode interior
            (4999, 2500, 4999, 0.753304),   # down-walk, mode interior
            (3766, 4999, 4999, 0.753304),   # healthy up-walk (original path)
        ]:
            terms = _pmf_terms(j_start, j_end, n, p)
            self.assertEqual(len(terms), abs(j_end - j_start) + 1)
            # the anchored seed is at the mode: the largest term must be
            # O(1/sqrt(2 pi npq)) at the mode index, i.e. the mode mass is
            # present (0.0131 for this (n, p)), not dropped
            self.assertGreater(max(terms), 0.013)

    def test_anchored_sum_matches_independent(self):
        terms = _pmf_terms(2500, 4999, 4999, 0.753304)
        self.assertLessEqual(abs(math.fsum(terms)
                                 - sf_ge_indep(2500, 4999, 0.753304)),
                             1e-10)

    def test_repair_fires_only_below_min_normal_seed(self):
        # MEASURED (tick 129), n=4999 p=0.753304: log_seed(2500) = -745.2543
        # (seed 0.0), 2510/2520/2530 = -734.1352/-723.0961/-712.1369
        # (subnormal seeds), 2534 = -707.7757 (first normal seed),
        # 2601 = -636.6287 (normal deep-tail: its pre-repair impossible
        # values were the ~1e-11 lgamma-cancellation error of a deep seed
        # inherited by the whole walk, cured by the [0,1] clamp, NOT by
        # the anchored path), 3766 = -4.336 (near mode), 4500 = -354.0499.
        lf = _log_factorials(4999)
        n, p = 4999, 0.753304
        for j_start, expect_anchored in [
            (2500, True),   # -745.2543: seed 0.0
            (2520, True),   # -723.0961: subnormal seed
            (2530, True),   # -712.1369: subnormal seed
            (2534, False),  # -707.7757: first normal seed above threshold
            (2601, False),  # -636.6287: normal seed, original path
            (3766, False),  # -4.336: near mode, healthy original path
            (4500, False),  # -354.0499: normal seed
        ]:
            log_seed = (lf[n] - lf[j_start] - lf[n - j_start]
                        + j_start * math.log(p)
                        + (n - j_start) * math.log1p(-p))
            if expect_anchored:
                self.assertLess(log_seed, _LOG_MIN_NORMAL)
            else:
                self.assertGreaterEqual(log_seed, _LOG_MIN_NORMAL)

    def test_healthy_walks_bit_identical_to_original(self):
        # bit-conservatism: healthy-seed calls take the original path
        # byte-for-byte (every pinned tick-127/128 number rides on this)
        for j_start, j_end, n, p in [
            (3766, 4999, 4999, 0.753304),
            (4500, 0, 4999, 0.753304),
            (2500, 4999, 4999, 0.5),
            (120, 0, 153, 106 / 153),       # tick-127 arm4 stratum
        ]:
            self.assertEqual(_pmf_terms(j_start, j_end, n, p),
                             _original_pmf_terms(j_start, j_end, n, p))


class NaiveQuantileSearchRecovered(unittest.TestCase):
    # the withdrawn tick-128 first draft collapsed because a CDF-quantile
    # search starting at k = n/2 walks straight into the underflow cliff;
    # post-repair the same search is sane

    def test_cp_at_midpoint_sane(self):
        lo, hi = clopper_pearson(2500, 4999, 0.05)
        self.assertLess(lo, 2500 / 4999)
        self.assertGreater(hi, 2500 / 4999)
        self.assertLess(hi - lo, 0.05)
        # pinned post-repair values
        self.assertAlmostEqual(lo, 0.48614293075084325, places=15)
        self.assertAlmostEqual(hi, 0.5140569923589355, places=15)

    def test_cp_defining_equations_hold_at_solution(self):
        # CP defining equations at the returned bounds (tick-127 identities)
        k, n, alpha = 2500, 4999, 0.05
        lo, hi = clopper_pearson(k, n, alpha)
        self.assertLess(abs(binom_sf_ge(k, n, lo) - alpha / 2), 1e-9)
        self.assertLess(abs(binom_cdf(k, n, hi) - alpha / 2), 1e-9)


if __name__ == "__main__":
    unittest.main()
