"""Exact-Sidak calibration of the simultaneous per-stratum bands (w8) —
pure planning math, tick 125.

Tick 124 (commit 548234b) priced BONFERRONI-Wilson simultaneous bands on
the paired tick-123 datasets: family-0.95 simultaneity costs 1.3458x
(m=6) / 1.2700x (m=4) per-stratum width over nominal Wilson-95. This
module asks the natural follow-up BEFORE the blockpower arbitration
datum (request ``d3aa0acaa37ff4c9...``, queued since 21:30:04Z) lands:
how much of that price is CORRECTION SLACK rather than irreducible?

For INDEPENDENT strata (true here by design: disjoint seed bases /
disjoint blocks feed each stratum), the exact simultaneous calibration
is SIDAK: per-stratum two-sided level 1 - alpha' with
alpha' = 1 - (1-alpha)^(1/m), giving family miscoverage exactly alpha in
expectation — strictly tighter than Bonferroni's alpha/m. The measured
answer (pinned in tests): at m=6 / m=4 the Bonferroni width premium over
exact Sidak is ~0.3% — essentially ALL of tick 124's simultaneity price
is irreducible for independent strata; the width lever is per-stratum n,
not the correction choice. Bonferroni keeps one advantage: it needs NO
independence assumption.

Honesty caveats, stated not implied:
- Sidak exactness assumes each per-stratum interval has EXACTLY
  per-stratum level 1-alpha'. Wilson intervals carry O(n^-1)
  discreteness deviations, so the REALIZED family level of
  Wilson-at-z_Sidak is approximate; the fixed-seed MC below measures it
  on the paired datasets, and the realization may land on either side of
  0.95 within MC error (~ +-0.0068 at 4000 reps), exactly as tick 124's
  world-A Bonferroni realization did (0.94975).
- Independence holds for the strata in BOTH frozen worlds and in the
  real readout (disjoint data per stratum); Sidak must NOT be reused for
  overlapping/reused-seed strata.

Real-data readout: per-stratum Wilson intervals at nominal /
Bonferroni / Sidak z for the frozen SIX_WINDOW_STRATA (m=6) and
CONTESTED_FOUR_ARM_STRATA (m=4) — the concrete simultaneous-band table
the branch map reports once blockpower adjudicates.

PAIRED DATASETS: seeds (20261013 / 20261014), replicates (4000) and the
deterministic _BinomialCDF draw sequence are the tick-123/124 ones,
reused verbatim (first_draw_row fingerprints pinned equal to tick 124's
tests). Zero kTAM trajectories; no gate executed; the pooled contested
line stays REPORTED-NOT-CLAIMABLE; the ladder stays PAUSED.
Determinism: stdlib only (random.Random, statistics.NormalDist; hosted
unittest workflow is stdlib-only — tick-123 repair).
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
    from .w8_simultaneous_band import FAMILY_LEVEL, Z_NOMINAL, bonferroni_z
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
    from w8_simultaneous_band import FAMILY_LEVEL, Z_NOMINAL, bonferroni_z
    from w8_stratified_census import (
        CONTESTED_FOUR_ARM_STRATA,
        SIX_WINDOW_STRATA,
        wilson95,
    )


def sidak_z(m: int, family: float = FAMILY_LEVEL) -> float:
    """Per-stratum two-sided z for EXACT family level over m INDEPENDENT
    strata: alpha' = 1 - (1-alpha)^(1/m), z = Phi^-1(1 - alpha'/2)."""
    if not isinstance(m, int) or isinstance(m, bool) or m < 1:
        raise ValueError("m must be a positive integer")
    if not 0.0 < family < 1.0:
        raise ValueError("family level must be in (0, 1)")
    per_stratum_alpha = 1.0 - (1.0 - (1.0 - family)) ** (1.0 / m)
    return NormalDist().inv_cdf(1.0 - per_stratum_alpha / 2.0)


def sidak_band_world(label: str, rates: list[float], ns: list[int],
                     seed: int, replicates: int = REPLICATES,
                     family: float = FAMILY_LEVEL) -> dict:
    """Fixed-seed paired MC: nominal vs Bonferroni vs Sidak per-stratum
    Wilson bands on the tick-123 datasets (identical draw rows)."""
    if not isinstance(seed, int) or isinstance(seed, bool) or seed < 0:
        raise ValueError("seed must be a non-negative integer")
    if (not isinstance(replicates, int) or isinstance(replicates, bool)
            or replicates <= 0):
        raise ValueError("replicates must be a positive integer")
    if len(rates) != len(ns) or not rates or not ns:
        raise ValueError("rates and ns must be non-empty and aligned")

    m = len(ns)
    z_bonf = bonferroni_z(m, family)
    z_sidak = sidak_z(m, family)

    rng = random.Random(seed)
    tables = [_BinomialCDF(n, p) for n, p in zip(ns, rates)]
    draws = [[t.draw(rng) for t in tables] for _ in range(replicates)]

    all_nominal_hits = 0
    all_bonf_hits = 0
    all_sidak_hits = 0
    per_stratum_sidak_hits = [0] * m
    width_nominal_sum = 0.0
    width_bonf_sum = 0.0
    width_sidak_sum = 0.0

    for row in draws:
        all_nominal = True
        all_bonf = True
        all_sidak = True
        for i, (x, n) in enumerate(zip(row, ns)):
            lo_n, hi_n = wilson95(int(x), n, Z_NOMINAL)
            lo_b, hi_b = wilson95(int(x), n, z_bonf)
            lo_s, hi_s = wilson95(int(x), n, z_sidak)
            width_nominal_sum += hi_n - lo_n
            width_bonf_sum += hi_b - lo_b
            width_sidak_sum += hi_s - lo_s
            if not lo_n <= rates[i] <= hi_n:
                all_nominal = False
            if not lo_b <= rates[i] <= hi_b:
                all_bonf = False
            if lo_s <= rates[i] <= hi_s:
                per_stratum_sidak_hits[i] += 1
            else:
                all_sidak = False
        if all_nominal:
            all_nominal_hits += 1
        if all_bonf:
            all_bonf_hits += 1
        if all_sidak:
            all_sidak_hits += 1

    per_stratum = [h / replicates for h in per_stratum_sidak_hits]
    mean_w_nominal = width_nominal_sum / (replicates * m)
    mean_w_bonf = width_bonf_sum / (replicates * m)
    mean_w_sidak = width_sidak_sum / (replicates * m)
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
        "z_sidak": z_sidak,
        "all_strata_coverage_nominal95": all_nominal_hits / replicates,
        "all_strata_coverage_bonferroni": all_bonf_hits / replicates,
        "all_strata_coverage_sidak": all_sidak_hits / replicates,
        "per_stratum_coverage_sidak_min": min(per_stratum),
        "per_stratum_coverage_sidak": per_stratum,
        "mean_per_stratum_width_nominal": mean_w_nominal,
        "mean_per_stratum_width_bonferroni": mean_w_bonf,
        "mean_per_stratum_width_sidak": mean_w_sidak,
        "width_ratio_bonf_over_nominal": mean_w_bonf / mean_w_nominal,
        "width_ratio_sidak_over_nominal": mean_w_sidak / mean_w_nominal,
        "width_ratio_bonf_over_sidak": mean_w_bonf / mean_w_sidak,
        "first_draw_row": [int(x) for x in draws[0]],
    }


def real_data_readout(family: float = FAMILY_LEVEL) -> list[dict]:
    """Per-stratum Wilson intervals at nominal / Bonferroni / Sidak z on
    the FROZEN committed strata (descriptive readout table for the
    branch map; m=6 six-window and m=4 contested four-arm)."""
    readouts = []
    for group_name, strata in (("six_window", SIX_WINDOW_STRATA),
                               ("contested_four_arm",
                                CONTESTED_FOUR_ARM_STRATA)):
        m = len(strata)
        z_bonf = bonferroni_z(m, family)
        z_sidak = sidak_z(m, family)
        rows = []
        for s in strata:
            lo_n, hi_n = wilson95(s.x, s.n, Z_NOMINAL)
            lo_b, hi_b = wilson95(s.x, s.n, z_bonf)
            lo_s, hi_s = wilson95(s.x, s.n, z_sidak)
            rows.append({
                "stratum": s.label,
                "x": s.x,
                "n": s.n,
                "share": s.x / s.n,
                "nominal95": (lo_n, hi_n),
                "bonferroni95": (lo_b, hi_b),
                "sidak95": (lo_s, hi_s),
                "width_bonf_over_sidak":
                    (hi_b - lo_b) / (hi_s - lo_s),
            })
        readouts.append({
            "group": group_name,
            "strata": m,
            "family_level": family,
            "z_nominal": Z_NOMINAL,
            "z_bonferroni": z_bonf,
            "z_sidak": z_sidak,
            "rows": rows,
        })
    return readouts


def run() -> list[dict]:
    rates_a, ns_a = _world_a_rates()
    rates_b, ns_b = _world_b_rates()
    return [
        sidak_band_world("A_homogeneous_six_window", rates_a, ns_a,
                         SEED_WORLD_A),
        sidak_band_world("B_contested_four_arm", rates_b, ns_b,
                         SEED_WORLD_B),
    ]


if __name__ == "__main__":
    import json
    for res in run():
        print(json.dumps(res, indent=2))
    print(json.dumps(real_data_readout(), indent=2))
