"""Operating-characteristics simulation for the frozen stratified census
estimators (w8) — pure planning math, tick 123.

This module runs ZERO kTAM trajectories. It draws synthetic binomial
counts calibrated to ALREADY-COMMITTED, frozen receipts (tick 122 design:
``tools/w8_stratified_census.py``) and measures, by fixed-seed Monte
Carlo, the operating characteristics of the frozen estimator menu:

- per-stratum Wilson-95 (the primary reporting unit under stratification)
- size-weighted pooled share with Wilson-95 (valid only where the
  applicable homogeneity gate passes)
- inverse-variance-weighted share theta-hat with delta-method SE
- the conservative simultaneous band theta-hat +/- weighted Wilson
  half-widths (the honesty-first summary under unresolved heterogeneity)

Two scenario worlds are frozen, one per branch of the pending blockpower
arbitration (request ``d3aa0acaa37ff4c9...``, queued since 21:30:04Z):

- WORLD A "homogeneous six-window" (models BLOCK_MECHANISM_NOT_DETECTED):
  six strata at the six-window n's, true share equal to the committed
  pooled share 22111/29989 in every stratum.
- WORLD B "contested four-arm" (models BLOCK_MECHANISM_SUPPORTED): the
  four corrected arms with true shares equal to their committed observed
  shares (arm3 375/500, arm4 106/153, arm6 389/500, arm7 365/499), i.e.
  the dispersion pattern the exact gate flagged as POOLING_CONTESTED.

Truth conventions (stated, not implied):
- pooled truth q* = sum(n_i p_i)/sum(n_i)
- inverse-variance truth theta* = plim(theta-hat) =
  [sum n_i/(1-p_i)] / [sum n_i/(p_i(1-p_i))]; equals p under homogeneity.
- the conservative band is scored BOTH on covering theta* and on covering
  every stratum p_i simultaneously.

No gate is executed; the pooled contested line stays
REPORTED-NOT-CLAIMABLE; the ladder stays PAUSED. Determinism: stdlib
Mersenne Twister (random.Random) with fixed per-scenario seeds and a
cached lgamma binomial-CDF inversion sampler; NO third-party imports
(the hosted unittest workflow is stdlib-only; see tick 123 repair);
every pin below is byte-reproducible.
"""

from __future__ import annotations

import bisect
import math
import random

try:  # package import (tests) and script import both supported
    from .w8_stratified_census import (
        CONTESTED_FOUR_ARM_STRATA,
        SIX_WINDOW_STRATA,
        pooled,
        stratified_estimators,
        wilson95,
    )
except ImportError:  # pragma: no cover - script execution path
    from w8_stratified_census import (
        CONTESTED_FOUR_ARM_STRATA,
        SIX_WINDOW_STRATA,
        pooled,
        stratified_estimators,
        wilson95,
    )

REPLICATES = 4000
SEED_WORLD_A = 20261013
SEED_WORLD_B = 20261014
Z_WILSON = 1.96


_LF_CACHE: dict[int, list[float]] = {}


def _log_factorials(n: int) -> list[float]:
    cached = _LF_CACHE.get(n)
    if cached is None:
        cached = [0.0]
        for k in range(1, n + 1):
            cached.append(cached[-1] + math.log(k))
        _LF_CACHE[n] = cached
    return cached


class _BinomialCDF:
    """Deterministic binomial sampler: cached log-CDF table (lgamma-free,
    plain log-sum with max-shift) + bisection inversion of Random.random()."""

    def __init__(self, n: int, p: float):
        if n <= 0 or not 0.0 < p < 1.0:
            raise ValueError("need n >= 1 and 0 < p < 1")
        lf = _log_factorials(n)
        lp = math.log(p)
        l1p = math.log(1.0 - p)
        lf_n = lf[n]
        # log pmf = ln C(n,k) + k ln p + (n-k) ln(1-p)
        logs = [lf_n + k * lp + (n - k) * l1p - lf[k] - lf[n - k]
                for k in range(n + 1)]
        shift = max(logs)
        acc = 0.0
        cdf = []
        for value in logs:
            acc += math.exp(value - shift)
            cdf.append(acc)
        total = cdf[-1]
        self.cdf = [v / total for v in cdf]
        self.cdf[-1] = 1.0  # guard floating-point drift at the right edge

    def draw(self, rng: random.Random) -> int:
        return bisect.bisect_left(self.cdf, rng.random())


def _world_a_rates() -> tuple[list[float], list[int]]:
    x_total, n_total, _, _ = pooled(SIX_WINDOW_STRATA)
    rate = x_total / n_total
    return ([rate] * len(SIX_WINDOW_STRATA),
            [s.n for s in SIX_WINDOW_STRATA])


def _world_b_rates() -> tuple[list[float], list[int]]:
    return ([s.x / s.n for s in CONTESTED_FOUR_ARM_STRATA],
            [s.n for s in CONTESTED_FOUR_ARM_STRATA])


def _truths(rates: list[float], ns: list[int]) -> dict[str, float]:
    n_total = sum(ns)
    q_star = sum(n * p for n, p in zip(ns, rates)) / n_total
    num = sum(n / (1.0 - p) for n, p in zip(ns, rates))
    den = sum(n / (p * (1.0 - p)) for n, p in zip(ns, rates))
    return {"pooled_truth": q_star, "inv_var_truth": num / den}


def simulate_world(label: str, rates: list[float], ns: list[int],
                   seed: int, replicates: int = REPLICATES) -> dict:
    """Fixed-seed Monte Carlo of the frozen estimator menu over one world."""
    if not isinstance(seed, int) or isinstance(seed, bool) or seed < 0:
        raise ValueError("seed must be a non-negative integer")
    if (not isinstance(replicates, int) or isinstance(replicates, bool)
            or replicates <= 0):
        raise ValueError("replicates must be a positive integer")
    if len(rates) != len(ns) or not rates or not ns:
        raise ValueError("rates and ns must be non-empty and aligned")

    rng = random.Random(seed)
    tables = [_BinomialCDF(n, p) for n, p in zip(ns, rates)]
    draws = [[t.draw(rng) for t in tables] for _ in range(replicates)]

    truths = _truths(rates, ns)
    q_star = truths["pooled_truth"]
    theta_star = truths["inv_var_truth"]

    per_stratum_hits = [0] * len(ns)
    pooled_hits = 0
    theta_hits = 0
    band_theta_hits = 0
    band_all_hits = 0
    band_width_sum = 0.0
    pooled_width_sum = 0.0

    for row in draws:
        x_total = 0
        n_total = 0
        strata = []
        for i, (x, n) in enumerate(zip(row, ns)):
            lo, hi = wilson95(int(x), n)
            if lo <= rates[i] <= hi:
                per_stratum_hits[i] += 1
            strata.append((int(x), n))
            x_total += int(x)
            n_total += n

        lo, hi = wilson95(x_total, n_total)
        if lo <= q_star <= hi:
            pooled_hits += 1
        pooled_width_sum += hi - lo

        est = stratified_estimators([
            _mk(label_j, x, n) for label_j, (x, n) in
            enumerate(zip(row, ns))
        ])
        theta = est["inv_var_share"]
        se = est["inv_var_se"]
        if abs(theta - theta_star) <= Z_WILSON * se:
            theta_hits += 1
        band = est["conservative_band_halfwidth"]
        band_width_sum += 2.0 * band
        if abs(theta - theta_star) <= band:
            band_theta_hits += 1
        if all(abs(theta - p) <= band for p in rates):
            band_all_hits += 1

    per_stratum = [h / replicates for h in per_stratum_hits]
    return {
        "world": label,
        "seed": seed,
        "replicates": replicates,
        "strata_n": list(ns),
        "true_rates": list(rates),
        "pooled_truth": q_star,
        "inv_var_truth": theta_star,
        "per_stratum_wilson_coverage": per_stratum,
        "per_stratum_wilson_coverage_min": min(per_stratum),
        "pooled_wilson_coverage": pooled_hits / replicates,
        "inv_var_coverage": theta_hits / replicates,
        "band_coverage_theta": band_theta_hits / replicates,
        "band_coverage_all_strata": band_all_hits / replicates,
        "mean_band_width": band_width_sum / replicates,
        "mean_pooled_wilson_width": pooled_width_sum / replicates,
        "width_ratio_band_over_pooled":
            (band_width_sum / replicates) / (pooled_width_sum / replicates),
    }


def _mk(label, x, n):
    try:
        from .w8_stratified_census import Stratum
    except ImportError:  # pragma: no cover - script execution path
        from w8_stratified_census import Stratum
    return Stratum(f"s{label}", int(x), int(n), "sim", "sim")


def run() -> list[dict]:
    rates_a, ns_a = _world_a_rates()
    rates_b, ns_b = _world_b_rates()
    return [
        simulate_world("A_homogeneous_six_window", rates_a, ns_a,
                       SEED_WORLD_A),
        simulate_world("B_contested_four_arm", rates_b, ns_b,
                       SEED_WORLD_B),
    ]


if __name__ == "__main__":
    import json
    for res in run():
        print(json.dumps(res, indent=2))
