"""Grid sample-size planning for the exact conditional w8 two-hot test.

Prospective design calibration only; this does not analyze the observed
six-window result or replace the registered primary Pearson analysis.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.w8_conditional_power import audit_scipy_tail, simulate_power

DELTAS = (0.01, 0.02)
N_GRID = (2500, 4000, 5000, 7500, 10000, 15000, 20000, 25000, 30000)
TARGET_POWERS = (0.80, 0.90, 0.95)
REPLICATES = 100_000
SEEDS = tuple(range(20261020, 20261038))


def first_lower_bound_crossing(
    rows: list[dict[str, object]], delta: float, target: float,
) -> dict[str, object] | None:
    """Return the first tested n whose Wilson lower bound reaches target."""
    if delta not in DELTAS or target not in TARGET_POWERS:
        raise ValueError("delta and target must be in the frozen design")
    eligible = sorted(
        (row for row in rows if row.get("delta") == delta),
        key=lambda row: int(row["n_per_window"]),
    )
    for index, row in enumerate(eligible):
        interval = row.get("wilson_95")
        if (not isinstance(interval, list) or len(interval) != 2
                or not all(isinstance(x, (int, float)) for x in interval)):
            raise ValueError("each row needs a two-endpoint Wilson interval")
        if interval[0] >= target:
            previous = eligible[index - 1] if index else None
            return {
                "delta": delta,
                "target_power": target,
                "first_tested_n": row["n_per_window"],
                "power_estimate": row["power_estimate"],
                "wilson_95": interval,
                "previous_tested_n": (previous["n_per_window"]
                                       if previous else None),
                "previous_wilson_95": (previous["wilson_95"]
                                        if previous else None),
                "interpretation": "first tested grid point with pointwise Wilson lower bound at or above target; not an exact minimum-n guarantee",
            }
    return None


def run_planning_grid() -> dict[str, object]:
    """Run the preregistered grid once and produce its raw receipt object."""
    if len(SEEDS) != len(DELTAS) * len(N_GRID):
        raise ValueError("frozen seed grid must have one seed per design cell")
    results: list[dict[str, object]] = []
    cells = ((delta, n) for delta in DELTAS for n in N_GRID)
    for cell_index, (delta, n_per_window) in enumerate(cells):
        results.append(simulate_power(
            delta, SEEDS[cell_index], REPLICATES, n_per_window,
        ))
    crossings = [
        first_lower_bound_crossing(results, delta, target)
        for delta in DELTAS
        for target in TARGET_POWERS
    ]
    return {
        "analysis": "prospective-exact-conditional-two-hot-sample-size-grid",
        "deltas": list(DELTAS),
        "n_per_window_grid": list(N_GRID),
        "target_powers": list(TARGET_POWERS),
        "replicates_per_cell": REPLICATES,
        "rng": "NumPy Generator(PCG64)",
        "seed_assignment": "20261020-20261037 in delta-major then n-major order",
        "fixed_tail_crosscheck": audit_scipy_tail(),
        "results": results,
        "first_lower_bound_crossings": crossings,
        "limits": [
            "fixed historical baseline p0=1110/1499 treated as known",
            "four equal-rate windows and exactly two elevated windows",
            "independent binomial pair-terminal outcomes with equal denominators",
            "pointwise Wilson intervals quantify Monte Carlo error only",
            "grid crossing is not an exact minimum-n or simultaneous guarantee",
            "not a new kinetic result or physical-replicate inference",
        ],
    }


def main() -> None:
    result = run_planning_grid()
    out = Path("evidence/2026-10-10-w8-conditional-n-planning/grid.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    for row in result["results"]:
        low, high = row["wilson_95"]
        print("delta={delta:.2f} n={n_per_window} reject={rejections}/{replicates} "
              "power={power_estimate:.6f} Wilson95=[{:.6f},{:.6f}]".format(
                  low, high, **row))
    print("grid crossings (first tested n with Wilson lower bound >= target):")
    for row in result["first_lower_bound_crossings"]:
        print(row)
    print("fixed tail: {:.15f} == integer helper {:.15f}".format(
        result["fixed_tail_crosscheck"]["scipy_tail"],
        result["fixed_tail_crosscheck"]["integer_tail"],
    ))
    print("wrote {}".format(out))


if __name__ == "__main__":
    main()
