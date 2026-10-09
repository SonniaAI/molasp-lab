"""Finite-sample conditional test for the six-window w8 two-hot family.

This post-result secondary audit conditions on the total D2T count and uses
Bonferroni across all 15 candidate hot pairs. It is a hypothesis test, not a
delta confidence interval or a replacement for the registered Pearson test.
"""

from __future__ import annotations

import math
import os
import sys
from itertools import combinations
from math import comb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.w8_window_heterogeneity_bound import OBSERVED_ARMS

BLOCKS = (8, 9, 10, 11, 12, 13)
ALPHA = 0.05
CANDIDATE_PAIR_COUNT = 15


def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def hypergeom_upper_tail(population: int, successes: int, draws: int,
                         observed: int) -> float:
    """Return P[X >= observed] for X~Hypergeom(population, successes, draws).

    The tail numerator is accumulated from exact integer combinatorial
    weights; only the final probability conversion uses floating point.
    """
    values = (population, successes, draws, observed)
    if not all(_is_int(value) for value in values):
        raise ValueError("hypergeometric inputs must be integers")
    if population <= 0 or not 0 <= successes <= population:
        raise ValueError("successes must be within a positive population")
    if not 0 <= draws <= population:
        raise ValueError("draws must be between zero and population")

    lower = max(0, draws - (population - successes))
    upper = min(draws, successes)
    if observed <= lower:
        return 1.0
    if observed > upper:
        return 0.0

    # C(K,x) C(N-K,m-x) are the unnormalized hypergeometric weights.
    weight = comb(successes, observed) * comb(
        population - successes, draws - observed)
    tail_weight = weight
    for x in range(observed, upper):
        numerator = (successes - x) * (draws - x)
        denominator = (x + 1) * (population - successes - draws + x + 1)
        product = weight * numerator
        next_weight, remainder = divmod(product, denominator)
        if remainder:
            raise ArithmeticError("hypergeometric weight recurrence was not integral")
        weight = next_weight
        tail_weight += weight

    probability = tail_weight / comb(population, draws)
    return min(1.0, probability)


def analyze_two_hot_family() -> dict[str, object]:
    """Conditionally test all 15 two-hot partitions with FWER control."""
    if len(OBSERVED_ARMS) != 6 or len(BLOCKS) != 6:
        raise ValueError("the frozen input must contain six labeled windows")
    for successes, trials in OBSERVED_ARMS:
        if (not _is_int(successes) or not _is_int(trials)
                or trials <= 0 or successes < 0 or successes > trials):
            raise ValueError("window counts must be integers with 0 <= x <= n")

    total_successes = sum(x for x, _ in OBSERVED_ARMS)
    total_trials = sum(n for _, n in OBSERVED_ARMS)
    assignments: list[dict[str, object]] = []
    for hot_indices in combinations(range(6), 2):
        hot_successes = sum(OBSERVED_ARMS[i][0] for i in hot_indices)
        hot_trials = sum(OBSERVED_ARMS[i][1] for i in hot_indices)
        p_value = hypergeom_upper_tail(
            total_trials, total_successes, hot_trials, hot_successes)
        assignments.append({
            "hot_blocks": [BLOCKS[i] for i in hot_indices],
            "hot_successes": hot_successes,
            "hot_trials": hot_trials,
            "cold_successes": total_successes - hot_successes,
            "cold_trials": total_trials - hot_trials,
            "conditional_upper_tail": p_value,
        })

    assignments.sort(key=lambda row: row["conditional_upper_tail"])
    minimum = assignments[0]
    raw_minimum = float(minimum["conditional_upper_tail"])
    adjusted = min(1.0, CANDIDATE_PAIR_COUNT * raw_minimum)
    return {
        "method": "exact-conditional-hypergeometric-bonferroni-two-hot",
        "analysis_status": "post-result-secondary-finite-sample-test",
        "total_successes": total_successes,
        "total_trials": total_trials,
        "candidate_pair_count": len(assignments),
        "alpha": ALPHA,
        "minimum_unadjusted_p": raw_minimum,
        "minimum_p_hot_blocks": minimum["hot_blocks"],
        "bonferroni_adjusted_p": adjusted,
        "reject_common_rate_null": adjusted < ALPHA,
        "assignments": assignments,
    }


def main() -> None:
    result = analyze_two_hot_family()
    print(f"method={result['method']}")
    print(f"analysis_status={result['analysis_status']}")
    print(f"total_successes={result['total_successes']}")
    print(f"total_trials={result['total_trials']}")
    print(f"candidate_pairs={result['candidate_pair_count']}")
    print(f"minimum_unadjusted_p={result['minimum_unadjusted_p']:.12g}"
          f" blocks={result['minimum_p_hot_blocks']}")
    print(f"bonferroni_adjusted_p={result['bonferroni_adjusted_p']:.12g}")
    print(f"alpha={result['alpha']}")
    print(f"reject_common_rate_null={result['reject_common_rate_null']}")
    for row in result["assignments"]:
        print("pair={} hot={}/{} tail={:.12g}".format(
            row["hot_blocks"], row["hot_successes"], row["hot_trials"],
            row["conditional_upper_tail"],
        ))


if __name__ == "__main__":
    main()
