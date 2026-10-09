"""Baseline-aware score bound for the registered w8 four-cold/two-hot shape.

Each candidate assignment pools the historical baseline with four cold
windows, and compares that binomial group to the two candidate hot windows.
The null difference is inverted with a constrained-binomial score test that
profiles the shared cold probability as a nuisance parameter.  The reported
envelope over all 15 assignments avoids choosing a hot pair post hoc; the
score calibration remains asymptotic, not an exact finite-sample guarantee.
"""

from __future__ import annotations

import math
import os
import sys
from itertools import combinations

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.w8_window_heterogeneity_bound import OBSERVED_ARMS

HISTORICAL_SUCCESSES = 1110
HISTORICAL_TRIALS = 1499
BLOCKS = (8, 9, 10, 11, 12, 13)
Z_ONE_SIDED_95 = 1.6448536269514722
_EPS = 1e-14


def _validate_counts(successes: int, trials: int, label: str) -> None:
    if (not isinstance(successes, int) or isinstance(successes, bool)
            or not isinstance(trials, int) or isinstance(trials, bool)
            or trials <= 0 or successes < 0 or successes > trials):
        raise ValueError(f"{label} counts must be integers with 0 <= x <= n")


def profiled_score_z(cold_x: int, cold_n: int, hot_x: int, hot_n: int,
                     delta: float) -> float:
    """Signed efficient score z for H0: p_hot - p_cold == delta.

    The constrained MLE p_cold maximizes the two-binomial likelihood with
    p_hot=p_cold+delta.  The efficient information profiles out p_cold.
    Negative z means the observed contrast is below the hypothesized delta.
    """
    _validate_counts(cold_x, cold_n, "cold")
    _validate_counts(hot_x, hot_n, "hot")
    if not math.isfinite(delta) or delta < 0.0 or delta >= 1.0:
        raise ValueError("delta must be finite and in [0, 1)")

    lo, hi = _EPS, 1.0 - delta - _EPS
    if hi <= lo:
        raise ValueError("delta leaves no interior probability range")

    def nuisance_score(p: float) -> float:
        q = p + delta
        return (cold_x / p - (cold_n - cold_x) / (1.0 - p)
                + hot_x / q - (hot_n - hot_x) / (1.0 - q))

    left_score = nuisance_score(lo)
    right_score = nuisance_score(hi)
    if left_score <= 0.0:
        p_cold = lo
    elif right_score >= 0.0:
        p_cold = hi
    else:
        left, right = lo, hi
        for _ in range(100):
            mid = (left + right) / 2.0
            if nuisance_score(mid) > 0.0:
                left = mid
            else:
                right = mid
        p_cold = (left + right) / 2.0

    p_hot = p_cold + delta
    hot_score = hot_x / p_hot - (hot_n - hot_x) / (1.0 - p_hot)
    info_cold = cold_n / (p_cold * (1.0 - p_cold))
    info_hot = hot_n / (p_hot * (1.0 - p_hot))
    efficient_info = info_cold * info_hot / (info_cold + info_hot)
    return hot_score / math.sqrt(efficient_info)


def one_sided_score_upper(cold_x: int, cold_n: int, hot_x: int,
                          hot_n: int,
                          z: float = Z_ONE_SIDED_95) -> float:
    """Invert the one-sided lower-tail score test for an upper delta limit."""
    if not math.isfinite(z) or z <= 0.0:
        raise ValueError("z must be finite and positive")

    def endpoint_function(delta: float) -> float:
        return profiled_score_z(cold_x, cold_n, hot_x, hot_n, delta) + z

    if endpoint_function(0.0) <= 0.0:
        return 0.0

    low, high = 0.0, 1.0 - 1e-10
    if endpoint_function(high) > 0.0:
        raise ArithmeticError("failed to bracket score upper endpoint")
    for _ in range(100):
        mid = (low + high) / 2.0
        if endpoint_function(mid) > 0.0:
            low = mid
        else:
            high = mid
    return (low + high) / 2.0


def analyze_joint_baseline_bound() -> dict[str, object]:
    """Profile the common baseline and return the all-pairs upper envelope."""
    if len(OBSERVED_ARMS) != 6:
        raise ValueError("the registered study must contain six windows")
    if len(BLOCKS) != len(OBSERVED_ARMS):
        raise ValueError("block labels do not match the registered windows")

    assignments = []
    for hot_indices in combinations(range(6), 2):
        hot_x = sum(OBSERVED_ARMS[i][0] for i in hot_indices)
        hot_n = sum(OBSERVED_ARMS[i][1] for i in hot_indices)
        cold_x = HISTORICAL_SUCCESSES + sum(
            x for i, (x, _) in enumerate(OBSERVED_ARMS)
            if i not in hot_indices)
        cold_n = HISTORICAL_TRIALS + sum(
            n for i, (_, n) in enumerate(OBSERVED_ARMS)
            if i not in hot_indices)
        assignments.append({
            "hot_blocks": [BLOCKS[i] for i in hot_indices],
            "cold_x": cold_x,
            "cold_n": cold_n,
            "hot_x": hot_x,
            "hot_n": hot_n,
            "observed_difference": hot_x / hot_n - cold_x / cold_n,
            "upper_delta": one_sided_score_upper(
                cold_x, cold_n, hot_x, hot_n),
        })

    assignments.sort(key=lambda row: row["upper_delta"])
    return {
        "method": "constrained-binomial-profiled-efficient-score",
        "calibration": "one-sided 95% nominal asymptotic normal score",
        "historical_baseline": {
            "successes": HISTORICAL_SUCCESSES,
            "trials": HISTORICAL_TRIALS,
        },
        "assignment_count": len(assignments),
        "assignments": assignments,
        "upper_envelope": assignments[-1]["upper_delta"],
        "envelope_hot_blocks": assignments[-1]["hot_blocks"],
        "minimum_assignment_upper": assignments[0]["upper_delta"],
        "minimum_upper_hot_blocks": assignments[0]["hot_blocks"],
    }


def main() -> None:
    result = analyze_joint_baseline_bound()
    print(f"method={result['method']}")
    print(f"calibration={result['calibration']}")
    print(f"candidate_hot_pairs={result['assignment_count']}")
    print(f"minimum_pair_upper_delta="
          f"{result['minimum_assignment_upper']:.10f}"
          f" blocks={result['minimum_upper_hot_blocks']}")
    print(f"selection_conservative_upper_envelope="
          f"{result['upper_envelope']:.10f}"
          f" blocks={result['envelope_hot_blocks']}")
    print("INTERPRETATION=MODEL_CONDITIONAL_NOMINAL_SCORE_LIMIT_NOT_EXACT")


if __name__ == "__main__":
    main()
