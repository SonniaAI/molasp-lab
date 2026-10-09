"""Sensitivity of the w8 two-hot score limit to historical/current exchangeability.

If the historical baseline has its own unrestricted rate, its likelihood
factorizes from the current cold/hot contrast.  The rate-difference endpoint
then uses only the four current cold arms and two current hot arms; all 15
possible hot-pair assignments are enveloped.  Calibration is the same nominal
asymptotic one-sided profile-score inversion as tick 106, not an exact interval.
"""

from __future__ import annotations

import os
import sys
from itertools import combinations

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.w8_joint_baseline_bound import (
    BLOCKS,
    one_sided_score_upper,
    profiled_score_z,
)
from tools.w8_window_heterogeneity_bound import OBSERVED_ARMS

Z_ONE_SIDED_95 = 1.6448536269514722
TICK106_POOLED_HISTORY_ENVELOPE = 0.013672878392859078


def analyze_independent_history() -> dict[str, object]:
    """Profile the current cold/hot contrast, leaving history independent."""
    if len(OBSERVED_ARMS) != 6 or len(BLOCKS) != 6:
        raise ValueError("the registered input must have six labeled windows")
    for successes, trials in OBSERVED_ARMS:
        if (not isinstance(successes, int) or isinstance(successes, bool)
                or not isinstance(trials, int) or isinstance(trials, bool)
                or trials <= 0 or successes < 0 or successes > trials):
            raise ValueError("window counts must be integers with 0 <= x <= n")

    assignments = []
    for hot_indices in combinations(range(6), 2):
        hot_x = sum(OBSERVED_ARMS[i][0] for i in hot_indices)
        hot_n = sum(OBSERVED_ARMS[i][1] for i in hot_indices)
        cold_x = sum(x for i, (x, _) in enumerate(OBSERVED_ARMS)
                     if i not in hot_indices)
        cold_n = sum(n for i, (_, n) in enumerate(OBSERVED_ARMS)
                     if i not in hot_indices)
        upper = one_sided_score_upper(cold_x, cold_n, hot_x, hot_n,
                                      z=Z_ONE_SIDED_95)
        assignments.append({
            "hot_blocks": [BLOCKS[i] for i in hot_indices],
            "cold_x": cold_x,
            "cold_n": cold_n,
            "hot_x": hot_x,
            "hot_n": hot_n,
            "upper_delta": upper,
            "score_at_upper": profiled_score_z(
                cold_x, cold_n, hot_x, hot_n, upper),
        })

    assignments.sort(key=lambda row: row["upper_delta"])
    minimum = assignments[0]
    maximum = assignments[-1]
    return {
        "method": "current-only-constrained-binomial-profile-score",
        "historical_model": "independent unrestricted nuisance; contributes no information to delta",
        "calibration": "one-sided 95% nominal asymptotic normal score",
        "assignment_count": len(assignments),
        "assignments": assignments,
        "minimum_upper_delta": minimum["upper_delta"],
        "minimum_hot_blocks": minimum["hot_blocks"],
        "maximum_upper_delta": maximum["upper_delta"],
        "maximum_hot_blocks": maximum["hot_blocks"],
        "tick106_pooled_history_envelope": TICK106_POOLED_HISTORY_ENVELOPE,
        "absolute_increase_vs_tick106": (
            maximum["upper_delta"] - TICK106_POOLED_HISTORY_ENVELOPE),
    }


def main() -> None:
    result = analyze_independent_history()
    print(f"method={result['method']}")
    print(f"calibration={result['calibration']}")
    print(f"candidate_hot_pairs={result['assignment_count']}")
    print(f"minimum_current_only_upper_delta="
          f"{result['minimum_upper_delta']:.10f}"
          f" blocks={result['minimum_hot_blocks']}")
    print(f"maximum_current_only_upper_delta="
          f"{result['maximum_upper_delta']:.10f}"
          f" blocks={result['maximum_hot_blocks']}")
    print(f"tick106_pooled_history_envelope="
          f"{result['tick106_pooled_history_envelope']:.10f}")
    print(f"absolute_increase_vs_tick106="
          f"{result['absolute_increase_vs_tick106']:.10f}")
    print("INTERPRETATION=MODEL_CONDITIONAL_NOMINAL_SCORE_SENSITIVITY_NOT_EXACT")


if __name__ == "__main__":
    main()
