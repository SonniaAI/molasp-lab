"""Dependence stress test for the simultaneous per-stratum bands (w8) —
pure planning math, tick 128.

Context (the calibration arc this closes): tick 124 priced simultaneity
(Bonferroni-Wilson family-0.95 at 1.3458x / 1.2700x width); tick 125
bounded the correction choice (exact Sidak reclaims <= 0.27% width BUT
needs an independence premise — Bonferroni stayed house authority); tick
126 priced the real lever (per-stratum n, exact halving multiples
4.0032x / 4.1046x); tick 127 priced exactness (Bonferroni-Clopper-
Pearson premium 1.006-1.040, family floor structural under
INDEPENDENCE). This module stress-tests the one premise the whole arc
left implicit: INDEPENDENCE OF THE STRATA.

Model (deliberately the adverse direction for AND-events): a common-mode
rate shock. Every stratum rate shifts together, p_i -> p_i + s*u with
u ~ Uniform[-1, 1] (deterministic trapezoid grid, no RNG anywhere in
this module) and shock scale s; conditional on u the strata stay
independent, so the family (all-strata) coverage is
    F(s) = E_u[ prod_i cov_i(p_i + s*u) ],
an exact 1-D integral of exact products. cov_i(u) peaks near u ~ 0 (the
bands are centered at the frozen design rates) and collapses as |u|
grows, and the collapse is COMONOTONE across strata — so F(s) falls with
s. That is exactly the coupling Sidak's product premise ignores, and it
is the physically-motivated hazard for the frozen readout too (a shared
calibration/concentration error moves every window/arm the same way).

What is measured:
- s = 0 degenerates to u = {0}: family = product of per-stratum
  coverages, byte-identical to the tick-127 exact families for
  Bonferroni-Wilson / Bonferroni-CP, and gives the FIRST exact families
  for plain per-stratum Wilson-95 and Sidak-Wilson (tick 124/125 had MC
  realizations only).
- Shock scan s in SHOCK_SCAN for all four calibrations, both frozen
  worlds: mean-over-u family F(s) AND the worst-mode floor
  min_u prod_i cov_i (the stronger statement: even the worst common
  mode keeps the family above this).
- Breach thresholds: the smallest s at which F(s) drops below the
  family target 0.95 (self-bracketing bisection; the bracket endpoints
  are verified, so the threshold is a first-crossing-on-the-scanned-path
  statement, not a global-monotonicity claim).
- Structural CP check: per-stratum Clopper-Pearson coverage at level
  1-alpha/m is >= 1-alpha/m at EVERY shifted rate (defining-equation
  identity), so the worst-mode floor is >= (1-alpha/m)^m >= 0.95 for
  ANY coupling, not just this one. Verified numerically pointwise.

CP fast path (method point): the CP acceptance window needs NO interval
solves. Because cdf(k,n,p) is decreasing in p and sf_ge(k,n,p) is
increasing in p, the defining equations give
    hi_CP(k) >= p  <=>  cdf(k,n,p) >= alpha/2
    lo_CP(k) >  p  <=>  sf_ge(k,n,p) <  alpha/2
so both crossings are binary searches over exact CDF values — the
interval's defining equations ARE the coverage statement.

FENCE RETIRED (tick 130, the recorded tick-128 follow-up): the
anchored re-seed repair in w8_exact_bands (tick 129, commit 1fe220b)
landed, so every walk seed is healthy and the crossing searches no
longer need the assert-bracketed np +- 9*sigma underflow window —
both now binary-search the full [0, n] range. Boundary identities
keep the predicates well-posed: cdf(n) = 1 >= half always, sf_ge(0) =
1 >= half always, and sf_ge(n) >= half means the upper exit is
impossible (k_low = n + 1, handled explicitly). Honest domain
(measured this tick, pinned in test_w8_fence_retirement): a
lower-tail crossing with k > n/2 resolves through the 1 - x branch,
whose lgamma-cancellation noise floor is ~4e-11 at n ~ 5000 — below
the floor the computed cdf returns 0.0 and the first decade above it
is wrong by up to ~7x before converging (binom_cdf(3564, 4999,
0.753304) = 5.97e-12 where the truth is 4.16e-11, first nonzero at
exactly that k). Full-range search is therefore exact for alpha_m >=
1e-8 (half >= 5e-9, >100x above the floor); the module's family
levels (alpha_m >= 8.3e-3) sit eight orders above it. Upper-tail
crossings have no such floor: sf_ge sums the short upper side
directly and stays ~13-digit exact at any depth (verified against an
independent per-term-lgamma logsumep at alpha_m = 2e-22, k_low =
4055 at 9.5 sigma beyond np — the measurement the old fence would
have rejected outright).

Boundary-rate rules (exact, not artifacts): at p >= 1 only k = n
occurs and CP hi(n) = 1 covers, while Wilson hi(k=n) < 1 strictly does
NOT (score intervals never touch 1); at p <= 0 only k = 0 occurs and
both lo(0) <= 0 covers. The breach search caps the shock grid at
0.995 x s_feasible so these rules fire only through genuine interior
limits, and cap-driven crossings are reported as such.

This module runs ZERO kTAM trajectories, executes NO gate, unfreezes
nothing (ladder stays PAUSED), and claims no physical-replicate result.
Descriptive real-data bands are unchanged. Determinism: stdlib only
(math; no RNG — nothing is seeded); every number is byte-reproducible.
"""

from __future__ import annotations

import math

try:  # package import (tests) and script import both supported
    from .w8_census_sim import _world_a_rates, _world_b_rates
    from .w8_exact_bands import (
        ALPHA_FAMILY,
        TICK124_MC_ALL_STRATA,
        _wilson_bounds_factory,
        _cp_bounds_factory,
        binom_cdf,
        binom_sf_ge,
        exact_coverage,
    )
    from .w8_simultaneous_band import FAMILY_LEVEL, bonferroni_z
    from .w8_sidak_band import sidak_z
    from .w8_stratified_census import Z_WILSON
except ImportError:  # pragma: no cover - script execution path
    from w8_census_sim import _world_a_rates, _world_b_rates
    from w8_exact_bands import (
        ALPHA_FAMILY,
        TICK124_MC_ALL_STRATA,
        _wilson_bounds_factory,
        _cp_bounds_factory,
        binom_cdf,
        binom_sf_ge,
        exact_coverage,
    )
    from w8_simultaneous_band import FAMILY_LEVEL, bonferroni_z
    from w8_sidak_band import sidak_z
    from w8_stratified_census import Z_WILSON

FAMILY_TARGET = FAMILY_LEVEL                 # 0.95
SHOCK_SCAN = (0.0, 0.01, 0.02, 0.03, 0.05, 0.08, 0.12, 0.18)
GRID_N = 41                                  # trapezoid nodes on [-1, 1]
CALIBRATIONS = ("plain_wilson95", "sidak_wilson",
                "bonferroni_wilson", "bonferroni_cp")
MC_ERROR_BAR_095 = 0.0068                    # 2-sigma at 4000 reps, p~0.95
PLAIN_MC_ALL_STRATA = (0.73675, 0.81625)     # tick 124, commit 548234b
SIDAK_MC_ALL_STRATA = (0.949, 0.95275)       # tick 125, commit 8611b8c

_COV_CACHE: dict[tuple, float] = {}


def _u_grid(nodes: int = GRID_N) -> list[float]:
    """Inclusive uniform grid on [-1, 1] (odd N puts a node at u = 0)."""
    return [-1.0 + 2.0 * i / (nodes - 1) for i in range(nodes)]


def _wilson_z(calib: str, m: int) -> float:
    if calib == "plain_wilson95":
        return Z_WILSON
    if calib == "sidak_wilson":
        return sidak_z(m)
    if calib == "bonferroni_wilson":
        return bonferroni_z(m)
    raise ValueError(f"not a wilson calibration: {calib}")


def cp_accept_window(n: int, alpha_m: float, p: float) -> tuple[int, int]:
    """(k_high, k_low) acceptance window for CP at level 1-alpha_m.

    Zero interval solves — direct from the defining equations:
      hi_CP(k) >= p  <=>  cdf(k,n,p) >= alpha_m/2   (cdf decreasing in p)
      lo_CP(k) >  p  <=>  sf_ge(k,n,p) <  alpha_m/2 (sf increasing in p)
    Coverage = P(k_high <= X <= k_low - 1) > 1 - alpha_m at EVERY p
    (both tail exits are < alpha_m/2 by the minimizing property of the
    crossing search). Both predicates are monotone in k -> binary
    search over the full [0, n] range (tick 130: the +-9*sigma
    underflow fence is retired; every seed is healthy post-1fe220b,
    and the boundary identities cdf(n) = 1 >= half / sf_ge(0) = 1 >=
    half make both searches well-posed without a bracket).
    """
    if not 0.0 < p < 1.0:
        return 0, n + 1  # boundary rates: k=n (or k=0) surely; caller's
        # boundary rules decide coverage; window degenerates
    half = alpha_m / 2.0
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi) // 2
        if binom_cdf(mid, n, p) >= half:
            hi = mid
        else:
            lo = mid + 1
    k_high = lo
    if binom_sf_ge(n, n, p) >= half:  # upper exit impossible: k_low = n+1
        return k_high, n + 1
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi) // 2
        if binom_sf_ge(mid, n, p) < half:
            hi = mid
        else:
            lo = mid + 1
    k_low = lo
    return k_high, k_low


def _coverage(calib: str, m: int, n: int, p: float) -> float:
    """Exact per-stratum coverage, with the exact boundary-rate rules:
    p >= 1 -> k = n surely (CP hi = 1 covers; Wilson hi < 1 misses);
    p <= 0 -> k = 0 surely (both lo(0) <= 0 cover).
    """
    key = (calib, m, n, p)
    hit = _COV_CACHE.get(key)
    if hit is not None:
        return hit
    if p >= 1.0:
        cov = 1.0 if calib == "bonferroni_cp" else 0.0
    elif p <= 0.0:
        cov = 1.0
    elif calib == "bonferroni_cp":
        k_high, k_low = cp_accept_window(n, ALPHA_FAMILY / m, p)
        cov = (0.0 if k_high > k_low - 1 else
               binom_cdf(k_low - 1, n, p) - binom_cdf(k_high - 1, n, p))
    else:
        cov = exact_coverage(_wilson_bounds_factory(n, _wilson_z(calib, m)),
                             n, p)
    _COV_CACHE[key] = cov
    return cov


def family_shocked(rates: list[float], ns: list[int], calib: str, s: float,
                   nodes: int = GRID_N) -> dict:
    """Mean-over-u and worst-mode family coverage at shock scale s.

    s = 0 short-circuits to the single node u = 0: the exact product of
    per-stratum coverages, byte-identical to the tick-127 independent
    family numbers (same multiplication order).
    """
    m = len(rates)
    if s == 0.0:
        prod = 1.0
        for p0, n in zip(rates, ns):
            prod *= _coverage(calib, m, n, p0)
        return {"s": 0.0, "family_mean": prod, "family_worst_mode": prod}
    us = _u_grid(nodes)
    prods = []
    for u in us:
        prod = 1.0
        for p0, n in zip(rates, ns):
            prod *= _coverage(calib, m, n, p0 + s * u)
        prods.append(prod)
    h = us[1] - us[0]
    total = (0.5 * prods[0] + 0.5 * prods[-1]
             + math.fsum(prods[1:-1]))
    return {"s": s,
            "family_mean": total * h / (us[-1] - us[0]),
            "family_worst_mode": min(prods)}


def s_feasible(rates: list[float]) -> float:
    """Largest s keeping every shifted rate inside (0,1) on the grid."""
    return min(min(p, 1.0 - p) for p in rates)


def breach_threshold(rates: list[float], ns: list[int], calib: str,
                     target: float = FAMILY_TARGET) -> dict:
    """First crossing of family_mean below target, self-bracketing.

    Returns breached_at_zero / never_within_feasible flags; otherwise a
    verified bracket (s_lo, s_hi) with family(s_lo) >= target >
    family(s_hi) and its bisection midpoint s_star.
    """
    m = len(rates)
    fam0 = family_shocked(rates, ns, calib, 0.0)["family_mean"]
    if fam0 < target:
        return {"breached_at_zero": True, "family_s0": fam0}
    s_hi_cap = 0.995 * s_feasible(rates)  # interior only: boundary-rate
    # nodes (a stratum rate hitting exactly 0/1) are degenerate and are
    # handled by the boundary rules, not treated as a drift breach
    grid = sorted(set([s for s in SHOCK_SCAN if s <= s_hi_cap] + [s_hi_cap]))
    s_lo = 0.0
    s_hi = None
    for s in grid:
        fam = family_shocked(rates, ns, calib, s)["family_mean"]
        if fam < target:
            s_hi = s
            break
        s_lo = s
    if s_hi is None:
        return {"breached_at_zero": False, "never_within_feasible": True,
                "family_s0": fam0, "family_at_cap":
                    family_shocked(rates, ns, calib, s_hi_cap)["family_mean"],
                "s_cap": s_hi_cap}
    while s_hi - s_lo > 1e-4:
        mid = 0.5 * (s_lo + s_hi)
        fam_mid = family_shocked(rates, ns, calib, mid)["family_mean"]
        if fam_mid < target:
            s_hi = mid
        else:
            s_lo = mid
    fam_lo = family_shocked(rates, ns, calib, s_lo)["family_mean"]
    fam_hi = family_shocked(rates, ns, calib, s_hi)["family_mean"]
    assert fam_lo >= target > fam_hi, "bracket verification failed"
    return {"breached_at_zero": False, "never_within_feasible": False,
            "s_star": 0.5 * (s_lo + s_hi), "bracket": (s_lo, s_hi),
            "family_lo": fam_lo, "family_hi": fam_hi,
            "family_s0": fam0, "m": m}


def world_scan(label: str, rates: list[float], ns: list[int]) -> dict:
    """Full stress readout for one frozen world."""
    m = len(rates)
    s_cap = s_feasible(rates)
    out = {"label": label, "m": m, "s_feasible": s_cap,
           "structural_floor": (1.0 - ALPHA_FAMILY / m) ** m,
           "calibrations": {}}
    for calib in CALIBRATIONS:
        rows = []
        for s in SHOCK_SCAN:
            if s <= s_cap:
                rows.append(family_shocked(rates, ns, calib, s))
        out["calibrations"][calib] = {
            "scan": rows,
            "breach": breach_threshold(rates, ns, calib),
        }
    # structural CP checks, pointwise over the whole scan/grid
    worst_per_stratum = [1.0] * m
    alpha_m = ALPHA_FAMILY / m
    for s in SHOCK_SCAN:
        if s > s_cap:
            continue
        for u in (_u_grid() if s > 0 else [0.0]):
            for i, (p0, n) in enumerate(zip(rates, ns)):
                cov = _coverage("bonferroni_cp", m, n, p0 + s * u)
                worst_per_stratum[i] = min(worst_per_stratum[i], cov)
    out["cp_min_per_stratum"] = worst_per_stratum
    out["cp_min_any_stratum"] = min(worst_per_stratum)
    out["cp_nominal_per_stratum"] = 1.0 - alpha_m
    c = out["calibrations"]
    out["s0_summary"] = {
        "plain_wilson95": c["plain_wilson95"]["scan"][0]["family_mean"],
        "sidak_wilson": c["sidak_wilson"]["scan"][0]["family_mean"],
        "bonferroni_wilson":
            c["bonferroni_wilson"]["scan"][0]["family_mean"],
        "bonferroni_cp": c["bonferroni_cp"]["scan"][0]["family_mean"],
    }
    return out


def _worlds() -> list[tuple[str, list[float], list[int]]]:
    rates_a, ns_a = _world_a_rates()
    rates_b, ns_b = _world_b_rates()
    return [("A_homogeneous_six_window", rates_a, ns_a),
            ("B_contested_four_arm", rates_b, ns_b)]


def run() -> list[dict]:
    """Measurement entry: one world_scan per frozen world, with the
    tick-124/125 MC realizations attached for the comparison table."""
    out = []
    for idx, (label, rates, ns) in enumerate(_worlds()):
        scan = world_scan(label, rates, ns)
        scan["s0_summary"]["tick124_mc_bonferroni"] = TICK124_MC_ALL_STRATA[idx]
        scan["s0_summary"]["tick124_mc_plain"] = PLAIN_MC_ALL_STRATA[idx]
        scan["s0_summary"]["tick125_mc_sidak"] = SIDAK_MC_ALL_STRATA[idx]
        out.append(scan)
    return out


if __name__ == "__main__":  # pragma: no cover - measurement entry point
    import json
    print(json.dumps(run(), indent=1))
