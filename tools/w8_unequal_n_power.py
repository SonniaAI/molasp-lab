"""Exact conditional two-hot-family power with unequal window denominators.

This is prospective design calibration under independent binomial windows;
it does not analyze or replace the registered observed-data test.
"""

from __future__ import annotations

import math
import os
import sys
from itertools import combinations
from typing import Sequence

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.w8_conditional_exact import hypergeom_upper_tail
from tools.w8_conditional_power import wilson_interval

BASELINE = 1110 / 1499
WINDOWS = 6
PAIR_COUNT = math.comb(WINDOWS, 2)
ALPHA = 0.05
REPLICATES = 100_000
DELTAS = (0.01, 0.02)
ALLOCATIONS = {
    "balanced": (5000, 5000, 5000, 5000, 5000, 5000),
    "hot_small": (2500, 2500, 6250, 6250, 6250, 6250),
    "hot_large": (6500, 6500, 4250, 4250, 4250, 4250),
}
CELL_SEEDS = {
    ("balanced", None): 20261040,
    ("hot_small", None): 20261041,
    ("hot_large", None): 20261042,
    ("balanced", 0.01): 20261043,
    ("balanced", 0.02): 20261044,
    ("hot_small", 0.01): 20261045,
    ("hot_small", 0.02): 20261046,
    ("hot_large", 0.01): 20261047,
    ("hot_large", 0.02): 20261048,
}
PAIRS = tuple(combinations(range(WINDOWS), 2))
TRUE_HOT_PAIR = (0, 1)


def validate_counts(counts: Sequence[int], trials: Sequence[int]) -> None:
    """Validate six integer success and trial counts, with 0 <= x_i <= n_i."""
    if len(counts) != WINDOWS or len(trials) != WINDOWS:
        raise ValueError("exactly six window counts and denominators are required")
    for successes, n in zip(counts, trials):
        if (not isinstance(successes, int) or isinstance(successes, bool)
                or not isinstance(n, int) or isinstance(n, bool)
                or n <= 0 or successes < 0 or successes > n):
            raise ValueError("require integer counts with 0 <= successes <= trials")


def conditional_pair_tails(counts: Sequence[int], trials: Sequence[int]) -> tuple[float, ...]:
    """Exact upper tails for each fixed pair, conditioning on total successes."""
    validate_counts(counts, trials)
    population = sum(trials)
    total_successes = sum(counts)
    tails = []
    for i, j in PAIRS:
        pair_successes = counts[i] + counts[j]
        pair_trials = trials[i] + trials[j]
        tails.append(hypergeom_upper_tail(
            population, total_successes, pair_trials, pair_successes))
    return tuple(tails)


def minimum_pair_tail(counts: Sequence[int], trials: Sequence[int]) -> tuple[float, tuple[int, int]]:
    """Return the minimum exact conditional tail and its first pair."""
    tails = conditional_pair_tails(counts, trials)
    winning_index = min(range(PAIR_COUNT), key=tails.__getitem__)
    return tails[winning_index], PAIRS[winning_index]


def scipy_pair_tails(counts: Sequence[int], trials: Sequence[int]) -> tuple[float, ...]:
    """Vector-library cross-check/simulation implementation of the same tails."""
    validate_counts(counts, trials)
    from scipy.stats import hypergeom

    population = sum(trials)
    total_successes = sum(counts)
    return tuple(float(hypergeom.sf(
        counts[i] + counts[j] - 1,
        population,
        total_successes,
        trials[i] + trials[j],
    )) for i, j in PAIRS)


def simulate_cell(allocation: str, delta: float | None, seed: int,
                  replicates: int = REPLICATES) -> dict[str, object]:
    """Estimate familywise rejection under the frozen six-window design."""
    if allocation not in ALLOCATIONS:
        raise ValueError("allocation must be one of the registered names")
    if delta is not None and (not math.isfinite(delta) or delta < 0
                              or BASELINE + delta >= 1.0):
        raise ValueError("invalid effect size")
    if (not isinstance(seed, int) or isinstance(seed, bool) or seed < 0
            or not isinstance(replicates, int) or isinstance(replicates, bool)
            or replicates <= 0):
        raise ValueError("seed and replicate count must be positive integers")

    import numpy as np
    from scipy.stats import hypergeom

    trials = np.asarray(ALLOCATIONS[allocation], dtype=np.int64)
    rates = np.full(WINDOWS, BASELINE, dtype=float)
    if delta is not None:
        rates[:2] += delta
    rng = np.random.Generator(np.random.PCG64(seed))
    counts = rng.binomial(trials, rates, size=(replicates, WINDOWS))
    total_successes = counts.sum(axis=1)
    pair_successes = np.stack(
        [counts[:, i] + counts[:, j] for i, j in PAIRS], axis=1)
    pair_trials = np.asarray(
        [ALLOCATIONS[allocation][i] + ALLOCATIONS[allocation][j]
         for i, j in PAIRS], dtype=np.int64)
    raw_tails = hypergeom.sf(
        pair_successes - 1,
        int(trials.sum()),
        total_successes[:, None],
        pair_trials[None, :],
    )
    minimum_indices = np.argmin(raw_tails, axis=1)
    raw_minimum = raw_tails[np.arange(replicates), minimum_indices]
    rejected = raw_minimum * PAIR_COUNT < ALPHA
    rejection_count = int(rejected.sum())
    rejection_fraction = rejection_count / replicates
    rejection_interval = wilson_interval(rejection_count, replicates)
    row: dict[str, object] = {
        "allocation": allocation,
        "trials_per_window": list(ALLOCATIONS[allocation]),
        "total_trials": int(trials.sum()),
        "delta": delta,
        "baseline_rate": BASELINE,
        "hot_rate": None if delta is None else BASELINE + delta,
        "hot_windows": [] if delta is None else [8, 9],
        "seed": seed,
        "replicates": replicates,
        "rejections": rejection_count,
        "fraction": rejection_fraction,
        "wilson_95": list(rejection_interval),
        "candidate_pair_count": PAIR_COUNT,
        "familywise_alpha": ALPHA,
        "decision_rule": "15 * min exact conditional upper-tail p < 0.05",
    }
    if delta is not None:
        selected = int(np.count_nonzero(minimum_indices == 0))
        row["true_pair_minimum_count"] = selected
        row["true_pair_minimum_fraction"] = selected / replicates
        row["true_pair_minimum_wilson_95"] = list(wilson_interval(selected, replicates))
    return row


def run_calibration() -> dict[str, object]:
    """Run the preregistered null and two-hot power grid with fixed seeds."""
    import numpy as np
    import scipy

    rows = [simulate_cell(allocation, delta, seed)
            for (allocation, delta), seed in CELL_SEEDS.items()]
    contrasts = []
    for delta in DELTAS:
        balanced = next(row for row in rows
                        if row["allocation"] == "balanced" and row["delta"] == delta)
        for allocation in ("hot_small", "hot_large"):
            row = next(row for row in rows
                       if row["allocation"] == allocation and row["delta"] == delta)
            difference = float(row["fraction"]) - float(balanced["fraction"])
            p1 = float(row["fraction"])
            p0 = float(balanced["fraction"])
            se = math.sqrt(p1 * (1 - p1) / REPLICATES
                           + p0 * (1 - p0) / REPLICATES)
            contrasts.append({
                "allocation_vs_balanced": allocation,
                "delta": delta,
                "difference": difference,
                "mc_normal_95": [difference - 1.959963984540054 * se,
                                  difference + 1.959963984540054 * se],
            })
    return {
        "analysis": "prospective-exact-conditional-two-hot-power-unequal-denominators",
        "numpy_version": np.__version__,
        "scipy_version": scipy.__version__,
        "rng": "NumPy Generator(PCG64)",
        "allocation_total_trials": 30000,
        "replicates_per_cell": REPLICATES,
        "seeds": {str(key): value for key, value in CELL_SEEDS.items()},
        "alternative": {
            "baseline_rate": BASELINE,
            "hot_windows": [8, 9],
            "deltas": list(DELTAS),
        },
        "null": "all six window probabilities equal baseline_rate",
        "method": "for each of 15 fixed pairs, condition on total successes and use Hypergeometric(total_trials, total_successes, pair_trials); Bonferroni over 15",
        "results": rows,
        "power_differences_vs_balanced": contrasts,
        "limits": [
            "independent-binomial windows and fixed baseline rate",
            "exactly two predesignated hot windows for power cells",
            "Bonferroni conditional test targets a common-probability global null",
            "unequal-n cases enumerate every pair; the two-largest-count shortcut is not used",
            "Wilson and contrast intervals describe Monte Carlo error only",
            "not a kinetic-trajectory result or an inference about physical replicates",
        ],
    }


def main() -> None:
    import json
    from pathlib import Path

    result = run_calibration()
    out = Path("evidence/2026-10-10-w8-unequal-n/grid.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    for row in result["results"]:
        print("{} delta={} reject={}/{} fraction={:.6f} Wilson95=[{:.6f},{:.6f}]".format(
            row["allocation"], row["delta"], row["rejections"], row["replicates"],
            row["fraction"], *row["wilson_95"]))
    print("wrote {}".format(out))


if __name__ == "__main__":
    main()
