"""Finite-sample-exact per-stratum bands for the frozen stratified census
(w8) — pure planning math, tick 127.

Motivation (tick 124, commit 548234b): the Bonferroni-Wilson band carries
an IN-EXPECTATION simultaneity guarantee only — Wilson score intervals are
approximate per stratum, and the tick-124 fixed-seed realization of the
family coverage sat one replicate short of 0.95 (3799/4000, inside MC
error, honestly disclosed). Tick 125 bounded what the correction choice
can buy (exact Sidak reclaims <= 0.27% width; Bonferroni stays house
authority); tick 126 priced the real lever (per-stratum n, at exact
halving multiples 4.0032x/4.1046x, NOT the bare 1/sqrt(n) rule).

This module prices the remaining certificate BEFORE the blockpower
arbitration datum (request ``d3aa0acaa37ff4c9...``, queued since
21:30:04Z) lands: BONFERRONI-CLOPPER-PERSON at the same family level,
whose per-stratum coverage is >= 1-alpha/m by construction (the defining
equations ARE the coverage statement), so the all-strata family coverage
under independence is >= (1-alpha/m)^m >= 1-alpha exactly (Bernoulli
inequality) — the in-expectation caveat removed at a width price. That
price is the EXACTNESS PREMIUM, the third leg of the calibration triangle
(simultaneity premium, correction-choice floor, exactness premium).

METHOD UPGRADE, stated plainly: for any count-based interval the
per-stratum coverage at a fixed true rate is an exact binomial sum over
the count support, and the all-strata coverage under independent strata
is the exact product of the per-stratum coverages — no Monte Carlo is
needed for these two quantities. This module therefore computes them by
exact enumeration (bound-crossing search + exact CDF sums) and
CROSS-CHECKS the tick-124/125 fixed-seed MC realizations (0.94975 /
0.95275) against the closed-form products, two independent computations
of the same number. The tick-123/124/125 MC datasets remain the
authority for quantities that genuinely need the joint draw (pooled and
inverse-variance estimator coverage, the conservative theta-band).

Measured here:
- Clopper-Pearson solver validation: analytic edge cases (k=0 upper =
  1-(alpha/2)^(1/n); k=n lower = (alpha/2)^(1/n); n=1 literals),
  defining-equation residuals, k-reflection symmetry, monotonicity in k.
- Real-data readout: Bonferroni-CP family-0.95 per-stratum bounds on the
  frozen six-window and contested four-arm counts (DESCRIPTIVE only; the
  pooled line stays REPORTED-NOT-CLAIMABLE), beside the house-authority
  Bonferroni-Wilson bounds, with per-stratum width premium.
- Exact per-stratum and family coverage in both frozen worlds
  (A homogeneous six-window at q* = 22111/29989; B contested four-arm at
  the corrected observed shares), Wilson vs Clopper-Pearson.
- Expected-width premium study at bounded n (153/612/1250/2500) for the
  frozen design rates and worst-case p=0.5: E[width] under exact
  enumeration for both intervals, and the trend of the premium.

This module runs ZERO kTAM trajectories, executes NO gate, unfreezes
nothing (ladder stays PAUSED), and claims no physical-replicate result.
Determinism: stdlib only (math; no RNG at all in this module — there is
nothing random to seed); every number is byte-reproducible.
"""

from __future__ import annotations

import math

# log of the smallest NORMAL double: seeds below this are subnormal/0.0
# and corrupt the O(1) recurrence (tick-129 anchored re-seed).
_LOG_MIN_NORMAL = math.log(2.2250738585072014e-308)


try:  # package import (tests) and script import both supported
    from .w8_census_sim import _log_factorials, _world_a_rates, _world_b_rates
    from .w8_simultaneous_band import FAMILY_LEVEL, bonferroni_z
    from .w8_stratified_census import (
        CONTESTED_FOUR_ARM_STRATA,
        SIX_WINDOW_STRATA,
        wilson95,
    )
except ImportError:  # pragma: no cover - script execution path
    from w8_census_sim import _log_factorials, _world_a_rates, _world_b_rates
    from w8_simultaneous_band import FAMILY_LEVEL, bonferroni_z
    from w8_stratified_census import (
        CONTESTED_FOUR_ARM_STRATA,
        SIX_WINDOW_STRATA,
        wilson95,
    )

ALPHA_FAMILY = 1.0 - FAMILY_LEVEL          # 0.05
TICK124_MC_ALL_STRATA = (0.94975, 0.95275)  # m=6, m=4 worlds, commit 548234b
MC_ERROR_BAR = 0.0068                       # 2-sigma at 4000 reps (tick 124)
PREMIUM_STUDY_NS = (153, 612, 1250, 2500)
PREMIUM_STUDY_PS = (0.5, 22111 / 29989, 106 / 153)
WIDTH_WINDOW_SIGMA = 8.0                    # pmf truncation ~1e-15


# ---------------------------------------------------------------------------
# Exact binomial sums (log-space pmf, shorter-side summation)
# ---------------------------------------------------------------------------

def binom_pmf(j: int, n: int, p: float) -> float:
    if not 0 <= j <= n:
        return 0.0
    if p <= 0.0:
        return 1.0 if j == 0 else 0.0
    if p >= 1.0:
        return 1.0 if j == n else 0.0
    lf = _log_factorials(n)
    return math.exp(lf[n] - lf[j] - lf[n - j]
                    + j * math.log(p) + (n - j) * math.log1p(-p))


def _pmf_terms(j_start: int, j_end: int, n: int, p: float) -> list[float]:
    """pmf terms for j in [j_start, j_end] (inclusive either direction).

    One exact log-factorial seed at j_start, then O(1) multiply recurrence
    walking toward j_end (down-walk uses pmf(j-1)/pmf(j) = j/(n-j+1) * q/p;
    up-walk uses pmf(j+1)/pmf(j) = (n-j)/(j+1) * p/q). Deterministic and
    ~10x faster than per-term exp(log(...)); relative error ~len*eps.

    ANCHORED RE-SEED (tick 129 repair of the tick-128 fenced hazard): if
    the direct seed would be subnormal (log-pmf below the min-normal
    double), the O(1) recurrence is corrupt from the start -- a 0.0 seed
    stays 0.0 forever (binom_sf_ge(2500, 4999, 0.7533) returned 0.0 where
    the truth is 1 - ~4e-12). Deep-tail seeds that are merely far down
    (still normal doubles, e.g. log-pmf -636.6 at j=2601) carry
    lgamma-cancellation-scale (~1e-11) relative error that the whole
    walk inherits; pre-repair that exposed impossible values
    (cdf(2601) = -6.33e-11, sf_ge(2601) = 1.0000000000639078), now
    clamped into [0, 1] by the callers. When the direct seed is not a
    normal double, the walk instead seeds at the mode (or the interval
    endpoint nearest the mode, when the interval does not contain it),
    walking outward, so the recurrence only ever starts at a healthy
    term and terms only ever decay toward the deep tail where they are
    negligible relative to the accumulated mass. Healthy-seed calls take
    the original path bit-for-bit (every pinned tick-127/128 number is
    unchanged).
    """
    if j_start == j_end:
        return [binom_pmf(j_start, n, p)]
    lf = _log_factorials(n)
    j0 = j_start
    log_seed = (lf[n] - lf[j0] - lf[n - j0]
                + j0 * math.log(p) + (n - j0) * math.log1p(-p))
    ratio_pq = p / (1.0 - p)
    ratio_qp = (1.0 - p) / p
    lo, hi = (j_end, j_start) if j_end < j_start else (j_start, j_end)
    if log_seed < _LOG_MIN_NORMAL:  # anchored repair path (tick 129)
        mode = int((n + 1) * p)  # floor((n+1)p), the max-pmf location
        mode = max(0, min(n, mode))
        anchor = mode if lo <= mode <= hi else (lo if mode < lo else hi)
        seed = math.exp(lf[n] - lf[anchor] - lf[n - anchor]
                        + anchor * math.log(p)
                        + (n - anchor) * math.log1p(-p))
        up = [seed]
        cur = seed
        for j in range(anchor, hi):
            cur = cur * ((n - j) / (j + 1)) * ratio_pq
            up.append(cur)
        down = []
        cur = seed
        for j in range(anchor, lo, -1):
            cur = cur * (j / (n - j + 1)) * ratio_qp
            down.append(cur)
        asc = down[::-1] + up  # terms lo..hi, ascending (down = lo..anchor-1, up = anchor..hi)
        return asc if j_end >= j_start else asc[::-1]
    seed = math.exp(log_seed)
    terms = [seed]
    cur = seed
    if j_end < j_start:  # walk down
        for j in range(j_start, j_end, -1):
            cur = cur * (j / (n - j + 1)) * ratio_qp
            terms.append(cur)
    else:  # walk up
        for j in range(j_start, j_end):
            cur = cur * ((n - j) / (j + 1)) * ratio_pq
            terms.append(cur)
    return terms


# Tick 131: deep-tail direct switch. Measured floor of the 1 - x
# branch (tick 130): lgamma-cancellation noise ~4e-11 ABSOLUTE at
# n=4999, p=0.753304 — every true tail mass below it computes to 0.0,
# the first decade above is wrong by up to ~7x. When the tail mass is
# PROVABLY below this switch, the 1 - x branch cannot resolve it and
# the direct short-side walk (relative error ~1e-11 at ANY depth: the
# down/up-walk's error is relative to the tiny terms themselves) is the
# only honest path. Valid bound: pmf is unimodal with mode
# floor((n+1)p); on the mode's side of the pivot the pmf is monotone
# away from it, so #terms * pmf(k) >= true tail mass. The switch never
# fires for a resolvable value class (worst measured looseness ~900x:
# bound 2.8e-8 at the true 4.2e-11, n=4999) and never near family
# levels (bounds ~0.1-4). Bit-conservatism: every frozen-window and
# coverage pin lives far above the switch, unchanged byte-for-byte.
_DEEP_TAIL_DIRECT_SWITCH = 1e-5


def _log_pmf_at(j: int, n: int, p: float) -> float:
    """log pmf(j) via three direct lgamma calls (O(1)) — bound
    arithmetic only; the walks keep seeding from the shared
    _log_factorials table, so no pinned walk bit changes."""
    return (math.lgamma(n + 1) - math.lgamma(j + 1) - math.lgamma(n - j + 1)
            + j * math.log(p) + (n - j) * math.log1p(-p))


def _deep_lower_direct(k: int, n: int, p: float) -> bool:
    """True when cdf(k) is provably below the 1 - x branch's resolution
    floor, so binom_cdf should take the direct down-walk (seed at k,
    terms decay toward 0) instead — tick 131. Requires k <= mode, so
    pmf(j) <= pmf(k) for all j <= k and (k+1)*pmf(k) bounds cdf(k)."""
    mode = max(0, min(n, int((n + 1) * p)))
    if k > mode:
        return False  # k above the mode: cdf(k) >= ~0.5, never deep
    return (math.log(k + 1) + _log_pmf_at(k, n, p)
            < math.log(_DEEP_TAIL_DIRECT_SWITCH))


def _deep_upper_direct(k: int, n: int, p: float) -> bool:
    """Mirror of _deep_lower_direct for binom_sf_ge(k): true when the
    upper tail is provably below the 1 - x floor (k >= mode, pmf
    monotone down above k, (n-k+1)*pmf(k) bounds sf_ge(k))."""
    mode = max(0, min(n, int((n + 1) * p)))
    if k < mode:
        return False  # k below the mode: sf_ge(k) >= ~0.5, never deep
    return (math.log(n - k + 1) + _log_pmf_at(k, n, p)
            < math.log(_DEEP_TAIL_DIRECT_SWITCH))


def binom_cdf(k: int, n: int, p: float) -> float:
    """P(X <= k), X ~ Bin(n, p): exact sum on the shorter side.

    Clamped to [0, 1]: walk rounding (~len*eps absolute at mass ~1) can
    push the 1 - x branch a few 1e-13 outside the unit interval.
    DEEP LOWER TAIL (tick 131): a lower-tail value with k > n/2 used to
    resolve through the 1 - x branch, whose noise floor is lgamma
    cancellation in the seed (~1e-11 RELATIVE to the O(1) complement
    mass, inherited by the whole walk) — measured at n=4999,
    p=0.753304 (tick 130): every true cdf below ~4e-11 returned 0.0
    and the first decade above was wrong by up to ~7x (computed
    5.97e-12 at k=3564 where the truth is 4.16e-11). When the tail
    mass is provably below _DEEP_TAIL_DIRECT_SWITCH, the direct
    down-walk now runs instead (seed at k, terms decay toward 0),
    which is relative-exact (~1e-11) at ANY depth — the lower tail
    becomes symmetric with the upper (sf_ge always summed its short
    side directly). Honest floor: the walk seeds subnormal below
    log-pmf ~ -708.4, so true masses < ~(n+1)e^-708 (~1e-304 at
    n=4999) return 0.0 — monotone-correct for any comparison level
    above ~1e-300. Pinned in tests/test_w8_deep_tail_symmetry.py and
    tests/test_w8_fence_retirement.py.
    """
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    if k + 1 <= n - k or _deep_lower_direct(k, n, p):
        return min(1.0, max(0.0, math.fsum(_pmf_terms(k, 0, n, p))))
    return min(1.0, max(0.0,
                        1.0 - math.fsum(_pmf_terms(k + 1, n, n, p))))


def binom_sf_ge(k: int, n: int, p: float) -> float:
    """P(X >= k) = 1 - cdf(k-1), exact sum on the shorter side.

    Clamped to [0, 1] with the same rationale as binom_cdf. DEEP
    UPPER TAIL (tick 131): the mirror of binom_cdf's fix — when the
    upper tail is provably below _DEEP_TAIL_DIRECT_SWITCH (k >= mode,
    terms decay above k), the direct up-walk replaces the 1 - x
    branch, removing the same ~4e-11 cancellation floor for deep
    upper tails with k < n/2 (fires when the mode sits below the
    pivot, i.e. p < 1/2). Same honest subnormal-seed floor as
    binom_cdf. Pinned in tests/test_w8_deep_tail_symmetry.py.
    """
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    if n - k + 1 <= k or _deep_upper_direct(k, n, p):
        return min(1.0, max(0.0, math.fsum(_pmf_terms(k, n, n, p))))
    return min(1.0, max(0.0,
                        1.0 - math.fsum(_pmf_terms(k - 1, 0, n, p))))


# ---------------------------------------------------------------------------
# Clopper-Pearson exact interval (two-sided), by CDF bisection
# ---------------------------------------------------------------------------

def _bisect_increasing(f, target: float, iters: int = 60) -> float:
    lo, hi = 0.0, 1.0
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if f(mid) < target:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-16:
            break
    return 0.5 * (lo + hi)


def clopper_pearson(k: int, n: int, alpha: float) -> tuple[float, float]:
    """Exact two-sided CP interval at level 1-alpha.

    Defining equations (checked to <= 1e-10 in validate_solver):
      k > 0:  P(X >= k | p = lo) = alpha/2      (lo = 0 for k = 0)
      k < n:  P(X <= k | p = hi) = alpha/2      (hi = 1 for k = n)
    """
    if n < 1 or not 0 <= k <= n:
        raise ValueError("need 0 <= k <= n and n >= 1")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha in (0,1)")
    half = alpha / 2.0
    lo = 0.0 if k == 0 else _bisect_increasing(
        lambda p: binom_sf_ge(k, n, p), half)
    # hi solves P(X <= k | hi) = alpha/2; as 1 - cdf is INCREASING in p,
    # its bisection target is 1 - alpha/2 (first draft passed alpha/2 and
    # solved the wrong tail - caught by the k=0 analytic check pre-pin).
    hi = 1.0 if k == n else _bisect_increasing(
        lambda p: 1.0 - binom_cdf(k, n, p), 1.0 - half)
    return lo, hi


# ---------------------------------------------------------------------------
# Exact coverage of a monotone count-based interval, by crossing search
# ---------------------------------------------------------------------------

def _cross_low(bounds, n: int, p: float) -> int:
    """min k with bounds(k)[0] > p (lower bound strictly above p)."""
    lo, hi = 0, n + 1
    while lo < hi:
        mid = (lo + hi) // 2
        if bounds(mid)[0] > p:
            hi = mid
        else:
            lo = mid + 1
    return lo  # n+1 if never above


def _cross_high(bounds, n: int, p: float) -> int:
    """min k with bounds(k)[1] >= p (upper bound at or above p)."""
    lo, hi = 0, n + 1
    while lo < hi:
        mid = (lo + hi) // 2
        if bounds(mid)[1] >= p:
            hi = mid
        else:
            lo = mid + 1
    return lo


def exact_coverage(bounds, n: int, p: float) -> float:
    """Exact P(bounds(X) covers p), X ~ Bin(n, p).

    bounds must be monotone non-decreasing in k on both endpoints
    (asserted for every interval used here by validate_solver /
    the test-suite monotonicity scans). Coverage =
    P(k_high <= X <= k_low - 1), the crossing window.
    """
    k_high = _cross_high(bounds, n, p)
    k_low = _cross_low(bounds, n, p)
    if k_high > k_low - 1:
        return 0.0
    return binom_cdf(k_low - 1, n, p) - binom_cdf(k_high - 1, n, p)


def _wilson_bounds_factory(n: int, z: float):
    def bounds(k: int) -> tuple[float, float]:
        return wilson95(k, n, z)
    return bounds


def _cp_bounds_factory(n: int, alpha: float):
    def bounds(k: int) -> tuple[float, float]:
        return clopper_pearson(k, n, alpha)
    return bounds


def assert_bounds_monotone(bounds, n: int, step: int = 1) -> bool:
    prev = bounds(0)
    for k in range(step, n + 1, step):
        cur = bounds(k)
        if cur[0] < prev[0] - 1e-15 or cur[1] < prev[1] - 1e-15:
            raise AssertionError(f"bounds not monotone at k={k}: {prev} -> {cur}")
        prev = cur
    return True


# ---------------------------------------------------------------------------
# Readouts
# ---------------------------------------------------------------------------

def validate_solver() -> dict:
    """Analytic + defining-equation + symmetry checks (measure, then pin)."""
    analytic = {}
    for n in (1, 2, 7, 153, 4999):
        analytic[f"upper_k0_n{n}"] = clopper_pearson(0, n, 0.05)[1]
        analytic[f"analytic_upper_k0_n{n}"] = 1.0 - 0.025 ** (1.0 / n)
        analytic[f"lower_kn_n{n}"] = clopper_pearson(n, n, 0.05)[0]
        analytic[f"analytic_lower_kn_n{n}"] = 0.025 ** (1.0 / n)
    analytic["cp_0_1"] = clopper_pearson(0, 1, 0.05)
    analytic["cp_1_1"] = clopper_pearson(1, 1, 0.05)
    analytic["cp_5_10"] = clopper_pearson(5, 10, 0.05)
    analytic["cp_106_153"] = clopper_pearson(106, 153, 0.05 / 4)
    residuals = []
    for k, n, alpha in ((1, 10, 0.05), (3, 12, 0.05 / 6), (5, 10, 0.05),
                        (367, 498, 0.05), (106, 153, 0.05 / 4),
                        (3644, 4999, 0.05 / 6), (3707, 4998, 0.05 / 6)):
        lo, hi = clopper_pearson(k, n, alpha)
        residuals.append({
            "k": k, "n": n, "alpha": alpha,
            "lo_resid": abs(binom_sf_ge(k, n, lo) - alpha / 2.0),
            "hi_resid": abs(binom_cdf(k, n, hi) - alpha / 2.0),
            "sym_resid": abs((lo - (1.0 - clopper_pearson(n - k, n, alpha)[1]))),
        })
    return {"analytic": analytic, "residuals": residuals,
            "max_residual": max(max(r["lo_resid"], r["hi_resid"],
                                    r["sym_resid"]) for r in residuals)}


def real_data_readout() -> dict:
    """Bonferroni-CP vs Bonferroni-Wilson family-0.95 on the frozen strata.

    DESCRIPTIVE ONLY: the pooled contested line stays
    REPORTED-NOT-CLAIMABLE (POOLING_CONTESTED, tick 119); this is the
    per-stratum certificate menu, priced pre-datum.
    """
    out = {}
    for name, strata in (("six_window", SIX_WINDOW_STRATA),
                         ("contested_four_arm", CONTESTED_FOUR_ARM_STRATA)):
        m = len(strata)
        alpha_m = ALPHA_FAMILY / m
        z_m = bonferroni_z(m)
        rows = []
        for s in strata:
            cp_lo, cp_hi = clopper_pearson(s.x, s.n, alpha_m)
            w_lo, w_hi = wilson95(s.x, s.n, z_m)
            rows.append({
                "label": s.label, "x": s.x, "n": s.n,
                "cp": (cp_lo, cp_hi), "wilson": (w_lo, w_hi),
                "cp_half_width": (cp_hi - cp_lo) / 2.0,
                "wilson_half_width": (w_hi - w_lo) / 2.0,
                "premium": ((cp_hi - cp_lo) / (w_hi - w_lo)),
            })
        out[name] = {"m": m, "alpha_m": alpha_m, "z_m": z_m, "rows": rows}
    return out


def world_coverage() -> dict:
    """Exact per-stratum and family coverage, both frozen worlds, both bands.

    Worlds are the tick-123 ones (imported, not restated): A homogeneous
    six-window (q* everywhere), B contested four-arm (observed shares).
    Family coverage under independent strata = product of per-stratum
    coverages, EXACT for count-based intervals — this cross-checks the
    tick-124 MC realizations from an independent computation.
    """
    worlds = (
        ("A_homogeneous_six_window",) + _world_a_rates() + (6,),
        ("B_contested_four_arm",) + _world_b_rates() + (4,),
    )
    out = {}
    for idx, (label, rates, ns, m) in enumerate(worlds):
        alpha_m = ALPHA_FAMILY / m
        z_m = bonferroni_z(m)
        per_stratum = {"wilson": [], "cp": []}
        for p, n in zip(rates, ns):
            w_cov = exact_coverage(_wilson_bounds_factory(n, z_m), n, p)
            c_cov = exact_coverage(_cp_bounds_factory(n, alpha_m), n, p)
            per_stratum["wilson"].append(w_cov)
            per_stratum["cp"].append(c_cov)
        fam_w = math.prod(per_stratum["wilson"])
        fam_c = math.prod(per_stratum["cp"])
        out[label] = {
            "m": m, "alpha_m": alpha_m, "z_m": z_m,
            "per_stratum_wilson": per_stratum["wilson"],
            "per_stratum_cp": per_stratum["cp"],
            "min_wilson": min(per_stratum["wilson"]),
            "min_cp": min(per_stratum["cp"]),
            "family_wilson": fam_w,
            "family_cp": fam_c,
            "tick124_mc": TICK124_MC_ALL_STRATA[idx],
            "mc_minus_exact_wilson": TICK124_MC_ALL_STRATA[idx] - fam_w,
            "premium_family_ratio": fam_c / fam_w,
        }
    return out


def _expected_width(bounds, n: int, p: float) -> float:
    """E[width(X)] by exact windowed enumeration (truncation ~1e-15)."""
    sigma = math.sqrt(n * p * (1.0 - p))
    klo = max(0, int(math.floor(n * p - WIDTH_WINDOW_SIGMA * sigma)) - 1)
    khi = min(n, int(math.ceil(n * p + WIDTH_WINDOW_SIGMA * sigma)) + 1)
    total = 0.0
    for k in range(klo, khi + 1):
        lo, hi = bounds(k)
        total += (hi - lo) * binom_pmf(k, n, p)
    return total


def width_premium_study() -> list[dict]:
    """E[width] premium CP/Wilson at bounded n for frozen design rates.

    Bounded to n <= 2500 (per-k CP solves); the trend, not the asymptote,
    is the deliverable. p=0.5 is the worst case; 22111/29989 the pooled
    six-window rate; 106/153 the smallest contested arm rate.
    """
    rows = []
    for p in PREMIUM_STUDY_PS:
        for n in PREMIUM_STUDY_NS:
            m = 6 if p != 106 / 153 else 4
            alpha_m = ALPHA_FAMILY / m
            z_m = bonferroni_z(m)
            w = _expected_width(_wilson_bounds_factory(n, z_m), n, p) / 2.0
            c = _expected_width(_cp_bounds_factory(n, alpha_m), n, p) / 2.0
            rows.append({"p": p, "n": n, "wilson_mean_half": w,
                         "cp_mean_half": c, "premium": c / w})
    return rows


def run() -> list[dict]:
    return [
        {"kind": "solver_validation", "payload": validate_solver()},
        {"kind": "real_data_readout", "payload": real_data_readout()},
        {"kind": "world_coverage", "payload": world_coverage()},
        {"kind": "width_premium_study", "rows": width_premium_study()},
    ]


if __name__ == "__main__":  # pragma: no cover - measurement entry point
    import json
    print(json.dumps(run(), indent=1))
