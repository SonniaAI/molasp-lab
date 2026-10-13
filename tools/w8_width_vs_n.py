"""Per-stratum n is the width lever for the simultaneous bands (w8) —
pure planning math, tick 126.

Tick 124 (commit 548234b) priced Bonferroni-Wilson simultaneous
per-stratum bands at family 0.95 (width price 1.3458x at m=6 / 1.2700x
at m=4 over nominal Wilson). Tick 125 (commit 8611b8c) bounded what any
correction could reclaim: exact Sidak saves only ~0.27% width, so the
simultaneity price is essentially IRREDUCIBLE for independent strata —
"the width lever is per-stratum n, not the correction choice." This
module PRICES that lever, before the blockpower arbitration datum
(request ``d3aa0acaa37ff4c9...``, queued since 21:30:04Z) lands:

1. PLANNING half-width curves: the Wilson half-width evaluated AT the
   design rate (x/n = p), w(n) = z*sqrt(p(1-p)/n + z^2/4n^2)/(1+z^2/n),
   for the frozen SIX_WINDOW (m=6) and CONTESTED_FOUR_ARM (m=4) strata
   at scales s in {1,2,4,8,16} (n_i -> s*n_i). This is the number the
   branch map's growth arithmetic turns into a per-stratum budget.
2. The 1/sqrt(n) rule is measured, not asserted — and its direction
   at THESE rates is slightly ADVERSE: Wilson's z^2/n correction makes
   w(n)*sqrt(n) increase toward its asymptote z*sqrt(p(1-p)) whenever
   p(1-p) > 1/8 (i.e. p in (0.146, 0.854)), so halving a width costs
   slightly MORE than 4x per-stratum n (4.0032x at the worst six-window
   stratum; 4.1046x at arm4's small n=153). Only for very extreme p
   does the correction run the other way. Measured via bisection.
3. n-MENU: minimal per-stratum n reaching target Bonferroni half-widths
   (0.02 / 0.015 / 0.01) at the worst-case design rate p=0.5 and at the
   worst (max-variance) OBSERVED frozen rate — the pre-datum budget
   table for whichever branch fires (NOT_DETECTED: stage-2 unchanged,
   stratified stays secondary; SUPPORTED: stratified primary + Neyman
   growth per the tick-122 branch table).
4. Paired-across-scales MC check: the SAME random.Random(seed) uniform
   stream is inverted through the scale-s binomial tables, so scale 1
   reproduces the tick-123/124 datasets byte-exactly (first_draw_row
   fingerprints pinned equal to the tick-124 tests) and scale 4 is the
   paired larger-n sibling. Verified: realized mean Bonferroni
   half-width tracks the planning curve (ratio ~1) and family coverage
   holds at the larger n.

Honesty caveats, stated not implied:
- Planning widths are evaluated at the OBSERVED rates (design
  rates); if the true rate is nearer 0.5 the width is larger. The
  worst-case (p=0.5) n-menu column is the budget-safe bound.
- MC coverage realizations are approximate (Wilson discreteness + MC
  error ~ +-0.0068 at 4000 reps); family level is claimed in
  expectation (union bound), not per-realization — same rule as ticks
  124/125.
- Nothing here unfreezes the ladder, executes a gate, or claims any
  physical-replicate result. Zero kTAM trajectories. The pooled
  contested line stays REPORTED-NOT-CLAIMABLE.

Determinism: stdlib only (random.Random, bisect, statistics.NormalDist;
hosted unittest workflow is stdlib-only — tick-123 CI rule); every
number is byte-reproducible from the pinned seeds.
"""

from __future__ import annotations

import random

try:  # package import (tests) and script execution both supported
    from .w8_census_sim import (
        REPLICATES,
        SEED_WORLD_A,
        SEED_WORLD_B,
        _BinomialCDF,
        _world_a_rates,
        _world_b_rates,
    )
    from .w8_simultaneous_band import FAMILY_LEVEL, bonferroni_z
    from .w8_stratified_census import (
        CONTESTED_FOUR_ARM_STRATA,
        SIX_WINDOW_STRATA,
        wilson95,
    )
except ImportError:  # pragma: no cover - script execution path
    from w8_census_sim import (
        REPLICATES,
        SEED_WORLD_A,
        SEED_WORLD_B,
        _BinomialCDF,
        _world_a_rates,
        _world_b_rates,
    )
    from w8_simultaneous_band import FAMILY_LEVEL, bonferroni_z
    from w8_stratified_census import (
        CONTESTED_FOUR_ARM_STRATA,
        SIX_WINDOW_STRATA,
        wilson95,
    )

SCALES = (1, 2, 4, 8, 16)
TARGET_HALF_WIDTHS = (0.02, 0.015, 0.01)
MC_SCALES = (1, 4)


def wilson_half_width(p: float, n: int, z: float) -> float:
    """Wilson half-width evaluated AT the design rate p (x/n == p).

    This is exactly (hi - lo) / 2 of wilson95(x, n, z) when x/n == p:
    center p, half-width z*sqrt(p(1-p)/n + z^2/4n^2)/(1+z^2/n).
    """
    if not 0.0 < p < 1.0:
        raise ValueError("design rate p must be in (0, 1)")
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise ValueError("n must be a positive integer")
    denom = 1.0 + z * z / n
    rad = p * (1.0 - p) / n + z * z / (4.0 * n * n)
    return z * rad ** 0.5 / denom


def planning_table(strata, scales=SCALES, family: float = FAMILY_LEVEL) -> dict:
    """Bonferroni planning half-widths per stratum at n_i -> s * n_i."""
    m = len(strata)
    z = bonferroni_z(m, family)
    names = [s.label for s in strata]
    rates = [s.x / s.n for s in strata]
    ns = [s.n for s in strata]
    rows = []
    for scale in scales:
        widths = [wilson_half_width(p, n * scale, z)
                  for p, n in zip(rates, ns)]
        rows.append({
            "scale": scale,
            "half_widths": widths,
            "max_half_width": max(widths),
            "mean_half_width": sum(widths) / m,
        })
    return {
        "m": m,
        "z_bonferroni": z,
        "names": names,
        "rates": rates,
        "ns": ns,
        "rows": rows,
    }


def n_for_half_width(p: float, h: float, z: float,
                     n_max: int = 10_000_000) -> int:
    """Minimal per-stratum n with planning half-width <= h at rate p.

    w(n) is strictly decreasing in n, so plain bisection on n is exact.
    """
    if not 0.0 < p < 1.0:
        raise ValueError("design rate p must be in (0, 1)")
    if not 0.0 < h < 1.0:
        raise ValueError("target half-width h must be in (0, 1)")
    if wilson_half_width(p, 1, z) <= h:
        return 1
    if wilson_half_width(p, n_max, z) > h:
        raise ValueError("target unreachable within n_max")
    lo, hi = 1, n_max  # invariant: w(lo) > h >= w(hi)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if wilson_half_width(p, mid, z) > h:
            lo = mid
        else:
            hi = mid
    return hi


def halving_multiple(p: float, n: int, z: float) -> dict:
    """Exact per-stratum n multiple that halves the planning width.

    The 1/sqrt(n) rule says 4x; Wilson's z^2/n correction shifts the
    exact multiple slightly ABOVE 4x for p(1-p) > 1/8 (all frozen
    strata) and below it only for extreme p. Direction measured, not
    assumed — see the module docstring and the tick-126 log.
    """
    w0 = wilson_half_width(p, n, z)
    n_half = n_for_half_width(p, w0 / 2.0, z)
    return {
        "n": n,
        "half_width": w0,
        "n_to_halve": n_half,
        "exact_multiple": n_half / n,
        "sqrt_rule_multiple": 4.0,
    }


def n_menu(strata, targets=TARGET_HALF_WIDTHS,
           family: float = FAMILY_LEVEL) -> dict:
    """Budget table: per-stratum n for each target half-width.

    worst_case: p=0.5 (budget-safe). observed: the max-variance frozen
    rate (closest to 0.5), which is what the branch map would actually
    plan against pre-datum.
    """
    m = len(strata)
    z = bonferroni_z(m, family)
    rates = [s.x / s.n for s in strata]
    p_obs = max(rates, key=lambda r: r * (1.0 - r))
    rows = []
    for h in targets:
        rows.append({
            "target_half_width": h,
            "n_worst_case_p05": n_for_half_width(0.5, h, z),
            "n_observed_rate": n_for_half_width(p_obs, h, z),
            "observed_design_rate": p_obs,
        })
    return {"m": m, "z_bonferroni": z, "rows": rows}


def scaled_world(label: str, rates: list[float], ns: list[int],
                 seed: int, scale: int,
                 replicates: int = REPLICATES,
                 family: float = FAMILY_LEVEL) -> dict:
    """Paired-across-scales MC: same uniform stream, scale-s tables.

    At scale 1 the draw rows are byte-identical to the tick-123/124
    datasets (same seed, same stratum order) — pinned by
    first_draw_row. At scale s the SAME uniforms are inverted through
    the s*n tables: the larger-n sibling of the same experiment.
    """
    if not isinstance(seed, int) or isinstance(seed, bool) or seed < 0:
        raise ValueError("seed must be a non-negative integer")
    if (not isinstance(replicates, int) or isinstance(replicates, bool)
            or replicates <= 0):
        raise ValueError("replicates must be a positive integer")
    if (not isinstance(scale, int) or isinstance(scale, bool)
            or scale < 1):
        raise ValueError("scale must be a positive integer")
    if len(rates) != len(ns) or not rates or not ns:
        raise ValueError("rates and ns must be non-empty and aligned")

    m = len(ns)
    z_bonf = bonferroni_z(m, family)
    ns_s = [n * scale for n in ns]

    rng = random.Random(seed)
    tables = [_BinomialCDF(n, p) for n, p in zip(ns_s, rates)]
    draws = [[t.draw(rng) for t in tables] for _ in range(replicates)]

    all_hits = 0
    half_sum = 0.0
    first_draw_row = list(draws[0])
    for row in draws:
        all_cov = True
        for x, n, p in zip(row, ns_s, rates):
            lo, hi = wilson95(int(x), n, z_bonf)
            half_sum += (hi - lo) / 2.0
            if not lo <= p <= hi:
                all_cov = False
        if all_cov:
            all_hits += 1

    planned = [wilson_half_width(p, n * scale, z_bonf)
               for p, n in zip(rates, ns)]
    planned_mean = sum(planned) / m
    realized_mean = half_sum / (replicates * m)
    return {
        "label": label,
        "scale": scale,
        "replicates": replicates,
        "all_coverage": all_hits / replicates,
        "mean_realized_half_width": realized_mean,
        "mean_planned_half_width": planned_mean,
        "realized_over_planned": realized_mean / planned_mean,
        "max_planned_half_width": max(planned),
        "first_draw_row": first_draw_row,
    }


def real_data_readout() -> dict:
    """Frozen-data readout: current widths, halving multiples, n-menu."""
    out = {}
    for key, strata in (("six_window", SIX_WINDOW_STRATA),
                        ("contested_four_arm", CONTESTED_FOUR_ARM_STRATA)):
        m = len(strata)
        z = bonferroni_z(m)
        rates = [s.x / s.n for s in strata]
        ns = [s.n for s in strata]
        widths = [wilson_half_width(p, n, z) for p, n in zip(rates, ns)]
        worst = max(range(m), key=lambda i: widths[i])
        out[key] = {
            "m": m,
            "current_half_widths": widths,
            "worst_stratum": strata[worst].label,
            "worst_half_width": widths[worst],
            "halving": halving_multiple(rates[worst], ns[worst], z),
            "n_menu": n_menu(strata),
        }
    return out


def run() -> list[dict]:
    worlds = []
    a_rates, a_ns = _world_a_rates()
    b_rates, b_ns = _world_b_rates()
    for scale in MC_SCALES:
        worlds.append(scaled_world("A_homogeneous_six_window", a_rates,
                                   a_ns, SEED_WORLD_A, scale))
        worlds.append(scaled_world("B_contested_four_arm", b_rates,
                                   b_ns, SEED_WORLD_B, scale))
    return worlds


if __name__ == "__main__":  # pragma: no cover - manual inspection
    import json

    print(json.dumps(real_data_readout(), indent=2))
    for w in run():
        print(json.dumps(w))
    six = planning_table(SIX_WINDOW_STRATA)
    print("six_window scaling (mean half-width, ratio to s=1, vs 1/sqrt):")
    base = six["rows"][0]["mean_half_width"]
    for row in six["rows"]:
        s = row["scale"]
        print(f"  s={s:>2} mean_w={row['mean_half_width']:.6f} "
              f"ratio={row['mean_half_width'] / base:.6f} "
              f"1/sqrt={s ** -0.5:.6f}")
