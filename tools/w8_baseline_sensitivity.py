"""Sensitivity of the w8 secondary delta bound to its historical baseline input.

This varies the plug-in baseline over its Wilson interval while holding the
observed noncentrality endpoint fixed. It is a mapping sensitivity check, not
an unconditional interval or a propagation of baseline uncertainty.
"""

from __future__ import annotations

import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.w8_window_heterogeneity_bound import (
    PLANNING_N_PER_WINDOW,
    analyze_observed,
    two_hot_delta_upper_bound,
)

HISTORICAL_SUCCESSES = 1110
HISTORICAL_TRIALS = 1499
Z_95 = 1.959963984540054


def wilson_interval(successes: int, trials: int,
                    z: float = Z_95) -> tuple[float, float]:
    """Return the two-sided Wilson score interval for a binomial proportion."""
    if (not isinstance(successes, int) or isinstance(successes, bool)
            or not isinstance(trials, int) or isinstance(trials, bool)
            or trials <= 0 or successes < 0 or successes > trials):
        raise ValueError("counts must be integers with 0 <= successes <= trials")
    if not math.isfinite(z) or z <= 0:
        raise ValueError("z must be finite and positive")
    p = successes / trials
    z2 = z * z
    denom = 1.0 + z2 / trials
    center = (p + z2 / (2.0 * trials)) / denom
    half = z * math.sqrt(p * (1.0 - p) / trials + z2 / (4.0 * trials * trials)) / denom
    return center - half, center + half


def analyze_baseline_sensitivity() -> dict[str, float]:
    """Map the observed lambda endpoint across the baseline's Wilson interval."""
    baseline = HISTORICAL_SUCCESSES / HISTORICAL_TRIALS
    low, high = wilson_interval(HISTORICAL_SUCCESSES, HISTORICAL_TRIALS)
    observed = analyze_observed()
    lam = observed["ncp_upper"]
    n = PLANNING_N_PER_WINDOW
    delta_low_baseline = two_hot_delta_upper_bound(lam, n, low)
    delta_plugin = two_hot_delta_upper_bound(lam, n, baseline)
    delta_high_baseline = two_hot_delta_upper_bound(lam, n, high)
    return {
        "historical_baseline": baseline,
        "baseline_wilson_low": low,
        "baseline_wilson_high": high,
        "observed_statistic": observed["statistic"],
        "ncp_upper": lam,
        "n_per_window": float(n),
        "delta_upper_at_baseline_low": delta_low_baseline,
        "delta_upper_at_plugin_baseline": delta_plugin,
        "delta_upper_at_baseline_high": delta_high_baseline,
        "delta_upper_mapping_low": min(delta_low_baseline, delta_high_baseline),
        "delta_upper_mapping_high": max(delta_low_baseline, delta_high_baseline),
    }


def main() -> None:
    result = analyze_baseline_sensitivity()
    print(f"historical_p0={result['historical_baseline']:.10f}")
    print("historical_p0_wilson95="
          f"[{result['baseline_wilson_low']:.10f},"
          f"{result['baseline_wilson_high']:.10f}]")
    print(f"observed_X2(5)={result['observed_statistic']:.10f}")
    print(f"one_sided_95_upper_lambda={result['ncp_upper']:.10f}")
    print("delta_upper_at_p0_low="
          f"{result['delta_upper_at_baseline_low']:.10f}")
    print("delta_upper_at_plugin_p0="
          f"{result['delta_upper_at_plugin_baseline']:.10f}")
    print("delta_upper_at_p0_high="
          f"{result['delta_upper_at_baseline_high']:.10f}")
    print("SCOPE=PLUG_IN_MAPPING_SENSITIVITY_NOT_UNCONDITIONAL_INTERVAL")


if __name__ == "__main__":
    main()
