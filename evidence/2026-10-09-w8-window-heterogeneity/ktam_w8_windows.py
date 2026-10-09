#!/usr/bin/env python3
"""Pre-registered w8 window-level heterogeneity study (tick 102).

Six fresh, non-overlapping seed windows are run at n=5000 each under the
unchanged BUILD1/Vp-missing, dG=2, s2, WIN_MULT=8 protocol.  The primary
test is an omnibus Pearson homogeneity test across the six windows (df=5,
alpha=.05); the historical 500-trajectory windows motivate the design but
are not pooled into this confirmatory test.  Run with SMOKE=1 only for
packaging checks: smoke output is never verdictable.
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
PREVIOUS = os.path.join(REPO, "evidence", "2026-10-09-w8-blockprobe")
TILES_AND_DIR = os.path.join(REPO, "evidence", "2026-10-06-body-conjunction-builds")
TILES_DEATH_DIR = os.path.join(REPO, "evidence", "2026-10-06-structural-death")
for path in (REPO, PREVIOUS, TILES_AND_DIR, TILES_DEATH_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

from ktam_w8_blockprobe import (  # noqa: E402
    BASE_SEED,
    BUILD1,
    CAL_D2T,
    CAL_L2,
    DG,
    SEED0_CAL,
    SEED_STRIDE,
    WIN_MULT,
    build_missing_species,
    canonical_assembly,
    census,
    matched_s2,
    run_traj,
    wilson,
)
from tools.w8_window_power import read_primary  # noqa: E402

ARM_BLOCKS = (8, 9, 10, 11, 12, 13)
SEED0_WINDOWS = tuple(BASE_SEED + block * SEED_STRIDE for block in ARM_BLOCKS)
N_CAL = 8 if os.environ.get("SMOKE") else 500
N_WINDOW = 8 if os.environ.get("SMOKE") else 5000
MIN_EVENTS = 50


def planned_seed_ranges() -> list[tuple[int, int]]:
    """Half-open seed intervals, exposed for CI identity/freshness pins."""
    return [(seed0, seed0 + N_WINDOW) for seed0 in SEED0_WINDOWS]


def main() -> None:
    build = build_missing_species(BUILD1, "Vp")
    canonical = canonical_assembly(BUILD1)
    cal_trajectories = [
        run_traj(build, matched_s2, canonical, SEED0_CAL + i, DG, WIN_MULT)
        for i in range(N_CAL)
    ]
    cal_mid = census(cal_trajectories, "mid")
    smoke = bool(os.environ.get("SMOKE"))
    cal_ok = smoke or (cal_mid["D2T"] == CAL_D2T and cal_mid["L2"] == CAL_L2)

    windows = []
    for block, seed0 in zip(ARM_BLOCKS, SEED0_WINDOWS):
        trajectories = [
            run_traj(build, matched_s2, canonical, seed0 + i, DG, WIN_MULT)
            for i in range(N_WINDOW)
        ]
        terminal = census(trajectories, "terminal")
        pair_n = terminal["D2T"] + terminal["L2"]
        windows.append({
            "block": block,
            "seed0": seed0,
            "n_trajectories": N_WINDOW,
            "D2T": terminal["D2T"],
            "L2": terminal["L2"],
            "other": terminal["other"],
            "pair_n": pair_n,
            "share": terminal["share"],
            "wilson95": wilson(terminal["D2T"], pair_n) if pair_n else None,
        })

    arms = [(row["D2T"], row["pair_n"]) for row in windows]
    pooled_x = sum(x for x, _ in arms)
    pooled_n = sum(n for _, n in arms)
    family_rate = 1110 / 1499
    threshold_counts = {
        "at_least_family_plus_0.02": sum(
            row["share"] is not None and row["share"] >= family_rate + 0.02
            for row in windows),
        "at_least_family_plus_0.03": sum(
            row["share"] is not None and row["share"] >= family_rate + 0.03
            for row in windows),
    }
    if smoke:
        primary, primary_metrics = "SMOKE_ONLY", None
    else:
        primary, primary_metrics = read_primary(cal_ok, arms)

    out = {
        "calibration": {
            "seed0": SEED0_CAL,
            "n": N_CAL,
            "mid_w4": cal_mid,
            "expected_D2T_L2": [CAL_D2T, CAL_L2],
            "status": "SMOKE_ONLY" if smoke else ("CAL_OK" if cal_ok else "CAL_FAIL"),
        },
        "protocol": {"dg": DG, "win_mult": WIN_MULT,
                     "n_per_window": N_WINDOW, "alpha": 0.05,
                     "primary_df": 5, "primary_test": "Pearson homogeneity"},
        "arms": windows,
        "descriptive": {
            "pooled_pair_rate": pooled_x / float(pooled_n) if pooled_n else None,
            "pooled_pair_wilson95": wilson(pooled_x, pooled_n) if pooled_n else None,
            "windows_at_least_family_plus": threshold_counts,
        },
        "primary": {"branch": primary, "metrics": primary_metrics},
        "historical_context": {
            "family_rate": family_rate,
            "full_n_windows": 6,
            "hot_windows_reported": 2,
            "use_in_primary_test": False,
        },
    }
    print(json.dumps(out, sort_keys=True))
    verdicts = {"CAL": out["calibration"]["status"], "PRIMARY": primary}
    print("VERDICTS " + json.dumps(verdicts, sort_keys=True))


if __name__ == "__main__":
    main()
