"""Monte Carlo power for the exact conditional w8 two-hot family test.

The simulation is prospective design calibration under independent binomial
windows. It does not analyze or replace the registered observed-data test.
"""

from __future__ import annotations

import math
import os
import sys
from itertools import combinations

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.w8_conditional_exact import hypergeom_upper_tail
from tools.w8_window_power import two_hot_power

BASELINE = 1110 / 1499
WINDOWS = 6
HOT_WINDOWS = 2
ALPHA = 0.05
PAIR_COUNT = math.comb(WINDOWS, HOT_WINDOWS)
REPLICATES = 200_000
N_PER_WINDOW = 5_000
DELTAS = (0.01, 0.02, 0.03)
SEEDS = (20261010, 20261011, 20261012)
WILSON_Z = 1.959963984540054


def maximum_two_window_sum(counts: tuple[int, ...] | list[int]) -> tuple[int, tuple[int, int]]:
    """Return the largest two-count sum and its first index pair."""
    if len(counts) != WINDOWS:
        raise ValueError("exactly six window counts are required")
    if any(not isinstance(x, int) or isinstance(x, bool) or x < 0 for x in counts):
        raise ValueError("window counts must be non-negative integers")
    pairs = list(combinations(range(WINDOWS), HOT_WINDOWS))
    pair, total = max(((pair, counts[pair[0]] + counts[pair[1]])
                       for pair in pairs), key=lambda item: item[1])
    return total, pair


def bonferroni_adjust(minimum_p: float, candidate_count: int = PAIR_COUNT) -> float:
    """Bonferroni-adjust a minimum p-value, capped at one."""
    if not math.isfinite(minimum_p) or not 0.0 <= minimum_p <= 1.0:
        raise ValueError("p-value must be finite and between zero and one")
    if not isinstance(candidate_count, int) or isinstance(candidate_count, bool) or candidate_count <= 0:
        raise ValueError("candidate_count must be a positive integer")
    return min(1.0, candidate_count * minimum_p)


def wilson_interval(successes: int, trials: int,
                    z: float = WILSON_Z) -> tuple[float, float]:
    """Wilson score interval for a Monte Carlo rejection fraction."""
    if (not isinstance(successes, int) or isinstance(successes, bool)
            or not isinstance(trials, int) or isinstance(trials, bool)
            or trials <= 0 or not 0 <= successes <= trials):
        raise ValueError("require integer counts with 0 <= successes <= trials")
    if not math.isfinite(z) or z <= 0:
        raise ValueError("z must be a positive finite number")
    p = successes / trials
    z2 = z * z
    denominator = 1.0 + z2 / trials
    center = (p + z2 / (2.0 * trials)) / denominator
    half = z * math.sqrt(p * (1.0 - p) / trials + z2 / (4.0 * trials * trials)) / denominator
    return max(0.0, center - half), min(1.0, center + half)


def audit_scipy_tail() -> dict[str, float | int]:
    """Cross-check SciPy against exact integer arithmetic on a fixed dataset."""
    from scipy.stats import hypergeom

    population = 29_989
    total_successes = 22_111
    draws = 9_994
    observed = 7_404
    scipy_tail = float(hypergeom.sf(observed - 1, population,
                                    total_successes, draws))
    integer_tail = hypergeom_upper_tail(population, total_successes,
                                        draws, observed)
    if not math.isclose(scipy_tail, integer_tail, rel_tol=1e-10,
                        abs_tol=1e-13):
        raise ArithmeticError("SciPy hypergeometric tail disagrees with exact helper")
    return {"population": population, "successes": total_successes,
            "draws": draws, "observed": observed,
            "scipy_tail": scipy_tail, "integer_tail": integer_tail}


def simulate_power(delta: float, seed: int, replicates: int = REPLICATES,
                   n_per_window: int = N_PER_WINDOW) -> dict[str, object]:
    """Estimate rejection probability under four baseline and two hot windows."""
    if not math.isfinite(delta) or delta < 0 or BASELINE + delta >= 1.0:
        raise ValueError("invalid effect size")
    if not isinstance(seed, int) or isinstance(seed, bool) or seed < 0:
        raise ValueError("seed must be a non-negative integer")
    if (not isinstance(replicates, int) or isinstance(replicates, bool)
            or replicates <= 0 or not isinstance(n_per_window, int)
            or isinstance(n_per_window, bool) or n_per_window <= 0):
        raise ValueError("replicates and n_per_window must be positive integers")

    import numpy as np
    from scipy.stats import hypergeom

    rng = np.random.Generator(np.random.PCG64(seed))
    rates = np.array([BASELINE + delta, BASELINE + delta]
                     + [BASELINE] * (WINDOWS - HOT_WINDOWS))
    counts = rng.binomial(n_per_window, rates,
                          size=(replicates, WINDOWS))
    total_successes = counts.sum(axis=1)
    two_largest = np.partition(counts, -HOT_WINDOWS, axis=1)[:, -HOT_WINDOWS:].sum(axis=1)
    # Equal group sizes mean every candidate pair has 2*n draws. The most
    # extreme pair is exactly the pair of largest counts.
    raw_minimum_p = hypergeom.sf(two_largest - 1,
                                 WINDOWS * n_per_window,
                                 total_successes,
                                 HOT_WINDOWS * n_per_window)
    adjusted_p = np.minimum(1.0, PAIR_COUNT * raw_minimum_p)
    rejected = adjusted_p < ALPHA
    rejection_count = int(rejected.sum())
    lower, upper = wilson_interval(rejection_count, replicates)
    pearson_ncp, pearson_power = two_hot_power(n_per_window, delta, BASELINE)
    return {
        "delta": delta,
        "true_hot_blocks": [8, 9],
        "baseline_rate": BASELINE,
        "hot_rate": BASELINE + delta,
        "n_per_window": n_per_window,
        "replicates": replicates,
        "seed": seed,
        "rejections": rejection_count,
        "power_estimate": rejection_count / replicates,
        "wilson_95": [lower, upper],
        "pearson_chi2_approx_power": pearson_power,
        "pearson_noncentrality": pearson_ncp,
        "familywise_alpha": ALPHA,
        "candidate_pair_count": PAIR_COUNT,
        "decision_rule": "15 * minimum exact conditional upper-tail p < 0.05",
    }


def run_calibration() -> dict[str, object]:
    """Run the fixed three-effect simulation and record its provenance."""
    import numpy as np
    import scipy

    validation = audit_scipy_tail()
    rows = [simulate_power(delta, seed)
            for delta, seed in zip(DELTAS, SEEDS)]
    return {
        "analysis": "prospective-design-calibration-exact-conditional-two-hot-test",
        "numpy_version": np.__version__,
        "scipy_version": scipy.__version__,
        "rng": "NumPy Generator(PCG64)",
        "baseline_rate": BASELINE,
        "n_per_window": N_PER_WINDOW,
        "replicates_per_effect": REPLICATES,
        "tail_crosscheck": validation,
        "results": rows,
        "limits": [
            "conditional pair-terminal binomial model, equal denominators",
            "four windows at fixed historical baseline and two at baseline+delta",
            "Monte Carlo Wilson intervals quantify simulation error only",
            "not a new trajectory result, exact confidence bound, or physical-replicate claim",
        ],
    }


def main() -> None:
    import json
    from pathlib import Path

    result = run_calibration()
    out = Path("evidence/2026-10-10-w8-exact-power/power.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    for row in result["results"]:
        print("delta={delta:.2f} reject={rejections}/{replicates} power={power_estimate:.6f} "
              "Wilson95=[{:.6f},{:.6f}] PearsonApprox={pearson_chi2_approx_power:.6f}".format(
                  *row["wilson_95"], **row))
    print("SciPy exact-tail cross-check: {:.15f} == integer helper {:.15f}".format(
        result["tail_crosscheck"]["scipy_tail"],
        result["tail_crosscheck"]["integer_tail"],
    ))
    print("versions numpy={} scipy={}".format(
        result["numpy_version"], result["scipy_version"]))
    print("wrote {}".format(out))


if __name__ == "__main__":
    main()
