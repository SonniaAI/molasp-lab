"""Secondary model-conditional bound for the registered six-window study.

This inverts the noncentral-chi-square approximation used by the primary
power tool. It is not a general bound on arbitrary window heterogeneity.
"""

from __future__ import annotations

import math
import os
import sys
from itertools import combinations

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.w8_window_power import (
    FAMILY_RATE,
    chi2_sf_df5,
    heterogeneity_stat,
    noncentral_chi2_sf_df5,
    two_hot_power,
)

OBSERVED_ARMS = (
    (3644, 4999),
    (3707, 4998),
    (3692, 4999),
    (3675, 4999),
    (3696, 4998),
    (3697, 4996),
)
PLANNING_N_PER_WINDOW = 4998


def noncentrality_upper_bound(observed_statistic: float,
                              alpha: float = 0.05) -> float:
    """Invert the lower tail for a one-sided upper limit on noncentrality.

    For X^2 ~ noncentral-chi-square(df=5, lambda), the endpoint solves
    P_lambda(X^2 <= observed_statistic) = alpha. The reference distribution
    is the same asymptotic approximation used by the preregistered power tool.
    """
    if not math.isfinite(observed_statistic) or observed_statistic <= 0:
        raise ValueError("observed_statistic must be finite and positive")
    if not math.isfinite(alpha) or not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be in (0, 1)")

    central_cdf = 1.0 - chi2_sf_df5(observed_statistic)
    if central_cdf < alpha:
        raise ValueError("no non-negative upper endpoint for this lower-tail inversion")

    target_sf = 1.0 - alpha
    lo, hi = 0.0, 1.0
    while noncentral_chi2_sf_df5(observed_statistic, hi) < target_sf:
        hi *= 2.0
        if hi > 1_000_000.0:
            raise ArithmeticError("failed to bracket noncentrality endpoint")

    for _ in range(120):
        mid = (lo + hi) / 2.0
        if noncentral_chi2_sf_df5(observed_statistic, mid) < target_sf:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def two_hot_delta_upper_bound(noncentrality: float, n_per_window: int,
                              baseline: float = FAMILY_RATE) -> float:
    """Map a noncentrality endpoint to delta for 4 baseline + 2 hot windows."""
    if not math.isfinite(noncentrality) or noncentrality < 0:
        raise ValueError("noncentrality must be finite and non-negative")
    if n_per_window <= 0:
        raise ValueError("n_per_window must be positive")
    if not math.isfinite(baseline) or not 0.0 < baseline < 1.0:
        raise ValueError("baseline must be in (0, 1)")

    lo, hi = 0.0, 1.0 - baseline
    for _ in range(16):
        if baseline + hi < 1.0:
            break
        hi = math.nextafter(hi, 0.0)
    else:
        raise ValueError("baseline leaves no representable two-hot rate range")
    max_ncp = two_hot_power(n_per_window, hi, baseline)[0]
    if noncentrality > max_ncp:
        raise ValueError("noncentrality exceeds the valid two-hot rate range")

    for _ in range(120):
        mid = (lo + hi) / 2.0
        ncp = two_hot_power(n_per_window, mid, baseline)[0]
        if ncp < noncentrality:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def two_hot_noncentrality(sample_sizes: tuple[int, ...], hot_indices: tuple[int, int],
                          delta: float, baseline: float = FAMILY_RATE) -> float:
    """Approximate noncentrality for a weighted six-window 4:2 alternative."""
    if len(sample_sizes) != 6 or any(n <= 0 for n in sample_sizes):
        raise ValueError("sample_sizes must contain six positive counts")
    if len(hot_indices) != 2 or len(set(hot_indices)) != 2 \
            or any(i < 0 or i >= 6 for i in hot_indices):
        raise ValueError("hot_indices must select two distinct windows")
    if not math.isfinite(baseline) or not 0.0 < baseline < 1.0:
        raise ValueError("baseline must be in (0, 1)")
    if not math.isfinite(delta) or delta < 0 or baseline + delta >= 1.0:
        raise ValueError("invalid rate alternative")
    rates = [baseline + (delta if i in hot_indices else 0.0)
             for i in range(6)]
    total_n = sum(sample_sizes)
    pooled_rate = sum(n * p for n, p in zip(sample_sizes, rates)) / total_n
    variance = pooled_rate * (1.0 - pooled_rate)
    return sum(n * (p - pooled_rate) ** 2
               for n, p in zip(sample_sizes, rates)) / variance


def two_hot_delta_range_upper_bound(noncentrality: float,
                                    sample_sizes: tuple[int, ...],
                                    baseline: float = FAMILY_RATE) -> tuple[float, float]:
    """Return min/max delta endpoints over all 15 possible hot-window pairs."""
    if not math.isfinite(noncentrality) or noncentrality < 0:
        raise ValueError("noncentrality must be finite and non-negative")
    if len(sample_sizes) != 6 or any(n <= 0 for n in sample_sizes):
        raise ValueError("sample_sizes must contain six positive counts")
    if not math.isfinite(baseline) or not 0.0 < baseline < 1.0:
        raise ValueError("baseline must be in (0, 1)")

    delta_hi = 1.0 - baseline
    for _ in range(16):
        if baseline + delta_hi < 1.0:
            break
        delta_hi = math.nextafter(delta_hi, 0.0)
    else:
        raise ValueError("baseline leaves no representable two-hot rate range")

    endpoints = []
    for hot in combinations(range(6), 2):
        max_ncp = two_hot_noncentrality(sample_sizes, hot, delta_hi, baseline)
        if noncentrality > max_ncp:
            raise ValueError("noncentrality exceeds the valid two-hot rate range")
        lo, hi = 0.0, delta_hi
        for _ in range(120):
            mid = (lo + hi) / 2.0
            ncp = two_hot_noncentrality(sample_sizes, hot, mid, baseline)
            if ncp < noncentrality:
                lo = mid
            else:
                hi = mid
        endpoints.append((lo + hi) / 2.0)
    return min(endpoints), max(endpoints)


def analyze_observed() -> dict[str, float]:
    """Return the registered-data statistic and the secondary conditional bound."""
    statistic, p_value, pooled_share = heterogeneity_stat(list(OBSERVED_ARMS))
    ncp_upper = noncentrality_upper_bound(statistic, alpha=0.05)
    delta_upper = two_hot_delta_upper_bound(
        ncp_upper, PLANNING_N_PER_WINDOW, FAMILY_RATE)
    delta_min_actual_n, delta_max_actual_n = two_hot_delta_range_upper_bound(
        ncp_upper, tuple(n for _, n in OBSERVED_ARMS), FAMILY_RATE)
    return {
        "statistic": statistic,
        "p_value": p_value,
        "pooled_share": pooled_share,
        "alpha": 0.05,
        "ncp_upper": ncp_upper,
        "n_per_window": float(PLANNING_N_PER_WINDOW),
        "baseline": FAMILY_RATE,
        "two_hot_delta_upper": delta_upper,
        "delta_min_actual_n": delta_min_actual_n,
        "delta_max_actual_n": delta_max_actual_n,
    }


def main() -> None:
    result = analyze_observed()
    print(f"X2(5)={result['statistic']:.10f}; p={result['p_value']:.10f}")
    print(f"pooled_pair_share={result['pooled_share']:.10f}")
    print(f"one_sided_95_upper_lambda={result['ncp_upper']:.10f}")
    print(f"two_hot_delta_upper_at_n={int(result['n_per_window'])}="
          f"{result['two_hot_delta_upper']:.10f}")
    print(f"two_hot_delta_range_actual_n="
          f"[{result['delta_min_actual_n']:.10f},"
          f"{result['delta_max_actual_n']:.10f}]")
    print("INTERPRETATION=MODEL_CONDITIONAL_SECONDARY_BOUND_NOT_GENERAL_HETEROGENEITY_CLAIM")


if __name__ == "__main__":
    main()
