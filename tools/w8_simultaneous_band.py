"""Simultaneous per-stratum bands for the frozen stratified census (w8) —
pure planning math, tick 124.

Motivation (tick 123, commit fdab2ec): the OC simulation pinned that the
conservative band is a THETA-interval, not a stratum-simultaneous band —
in the contested four-arm world it covered theta* at 0.99975 but covered
all four stratum shares simultaneously in 0/4000 replicates. Per-stratum
Wilson-95 is nominal per stratum, not simultaneous (under independence
all-m coverage would be ~0.95^m before Wilson conservatism). This module
prices the obvious repair BEFORE the blockpower arbitration datum
(request ``d3aa0acaa37ff4c9...``, queued since 21:30:04Z) lands:
BONFERRONI per-stratum Wilson at family level 1-alpha with per-stratum
level 1-alpha/m (m = number of strata), i.e. z_m = Phi^-1(1 - alpha/2m).

PAIRED DATASETS: the worlds, seeds (20261013 / 20261014), replicate
count (4000) and the deterministic _BinomialCDF draw sequence are the
tick-123 ones, reused verbatim, so every replicate dataset here is
byte-identical to the corresponding tick-123 replicate. The comparison
"same 4000 datasets, different band" is therefore paired, not parallel.

Measured per world:
- simultaneous (all-strata) coverage of plain per-stratum Wilson-95
- simultaneous coverage of the Bonferroni band (union-bound guarantee
  >= 1-alpha in expectation; fixed-seed value is exact for these datasets)
- min per-stratum coverage of the Bonferroni band
- mean per-stratum widths at both levels and their ratio (the price of
  simultaneity per stratum)

This module runs ZERO kTAM trajectories, executes NO gate, unfreezes
nothing (ladder stays PAUSED), and claims no physical-replicate result.
Determinism: stdlib only (random.Random + statistics.NormalDist; the
hosted unittest workflow is stdlib-only — see the tick-123 repair); every
number is byte-reproducible from the pinned seeds.
"""

from __future__ import annotations

import random
from statistics import NormalDist

try:  # package import (tests) and script import both supported
    from .w8_census_sim import (
        REPLICATES,
        SEED_WORLD_A,
        SEED_WORLD_B,
        _BinomialCDF,
        _world_a_rates,
        _world_b_rates,
    )
    from .w8_stratified_census import wilson95
except ImportError:  # pragma: no cover - script execution path
    from w8_census_sim import (
        REPLICATES,
        SEED_WORLD_A,
        SEED_WORLD_B,
        _BinomialCDF,
        _world_a_rates,
        _world_b_rates,
    )
    from w8_stratified_census import wilson95

FAMILY_LEVEL = 0.95
Z_NOMINAL = 1.96


def bonferroni_z(m: int, family: float = FAMILY_LEVEL) -> float:
    """Per-stratum two-sided z giving family level 1-alpha over m strata."""
    if not isinstance(m, int) or isinstance(m, bool) or m < 1:
        raise ValueError("m must be a positive integer")
    if not 0.0 < family < 1.0:
        raise ValueError("family level must be in (0, 1)")
    per_stratum_alpha = (1.0 - family) / m
    return NormalDist().inv_cdf(1.0 - per_stratum_alpha / 2.0)


def simultaneous_band_world(label: str, rates: list[float], ns: list[int],
                            seed: int, replicates: int = REPLICATES,
                            family: float = FAMILY_LEVEL) -> dict:
    """Fixed-seed paired MC of per-stratum Wilson vs Bonferroni-Wilson."""
    if not isinstance(seed, int) or isinstance(seed, bool) or seed < 0:
        raise ValueError("seed must be a non-negative integer")
    if (not isinstance(replicates, int) or isinstance(replicates, bool)
            or replicates <= 0):
        raise ValueError("replicates must be a positive integer")
    if len(rates) != len(ns) or not rates or not ns:
        raise ValueError("rates and ns must be non-empty and aligned")

    m = len(ns)
    z_bonf = bonferroni_z(m, family)

    rng = random.Random(seed)
    tables = [_BinomialCDF(n, p) for n, p in zip(ns, rates)]
    draws = [[t.draw(rng) for t in tables] for _ in range(replicates)]

    all_nominal_hits = 0
    all_bonf_hits = 0
    per_stratum_bonf_hits = [0] * m
    width_nominal_sum = 0.0
    width_bonf_sum = 0.0

    for row in draws:
        all_nominal = True
        all_bonf = True
        for i, (x, n) in enumerate(zip(row, ns)):
            lo_n, hi_n = wilson95(int(x), n, Z_NOMINAL)
            lo_b, hi_b = wilson95(int(x), n, z_bonf)
            width_nominal_sum += hi_n - lo_n
            width_bonf_sum += hi_b - lo_b
            if not lo_n <= rates[i] <= hi_n:
                all_nominal = False
            if lo_b <= rates[i] <= hi_b:
                per_stratum_bonf_hits[i] += 1
            else:
                all_bonf = False
        if all_nominal:
            all_nominal_hits += 1
        if all_bonf:
            all_bonf_hits += 1

    per_stratum = [h / replicates for h in per_stratum_bonf_hits]
    mean_w_nominal = width_nominal_sum / (replicates * m)
    mean_w_bonf = width_bonf_sum / (replicates * m)
    return {
        "world": label,
        "seed": seed,
        "replicates": replicates,
        "strata": m,
        "strata_n": list(ns),
        "true_rates": list(rates),
        "family_level": family,
        "z_nominal": Z_NOMINAL,
        "z_bonferroni": z_bonf,
        "all_strata_coverage_nominal95": all_nominal_hits / replicates,
        "all_strata_coverage_bonferroni": all_bonf_hits / replicates,
        "per_stratum_coverage_bonferroni_min": min(per_stratum),
        "per_stratum_coverage_bonferroni": per_stratum,
        "mean_per_stratum_width_nominal": mean_w_nominal,
        "mean_per_stratum_width_bonferroni": mean_w_bonf,
        "width_ratio_bonf_over_nominal": mean_w_bonf / mean_w_nominal,
        "first_draw_row": [int(x) for x in draws[0]],
    }


def run() -> list[dict]:
    rates_a, ns_a = _world_a_rates()
    rates_b, ns_b = _world_b_rates()
    return [
        simultaneous_band_world("A_homogeneous_six_window", rates_a, ns_a,
                                SEED_WORLD_A),
        simultaneous_band_world("B_contested_four_arm", rates_b, ns_b,
                                SEED_WORLD_B),
    ]


if __name__ == "__main__":
    import json
    for res in run():
        print(json.dumps(res, indent=2))
