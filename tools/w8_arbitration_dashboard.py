"""Consolidated pre-datum dashboard of the frozen W8 blockpower
arbitration map (tick 142, SON-5152).

The frozen map (``research-log/2026-10-13-w8-blockpower-prereg.md``) is

    CAL_FAIL -> VOID;  min pair-n < 3400 -> NO_EVENTS;
    p <= 0.05 -> BLOCK_MECHANISM_SUPPORTED;  p > 0.05 -> NOT_DETECTED

Ticks 139-141 measured the operating characteristics of every branch
BEFORE any datum exists, in three receipts:

- tick 139  evidence/2026-10-14-w8-blockpower-oc/oc.json
            (Fisher branch pair: realized size + power)
- tick 140  evidence/2026-10-14-w8-blockpower-floor-oc/floor-oc.json
            (NO_EVENTS floor: cannot fire by chance at historical yield)
- tick 141  evidence/2026-10-14-w8-blockpower-cal-oc/cal-oc.json
            (CAL exact-match VOID gate: substrate-drift detector)

No single artifact consolidates them. This tool emits that consolidated
dashboard as a PURE FUNCTION of the three committed receipts: every
scalar carries its receipt provenance path, and the only new content is
cross-receipt relations (ratios, orderings, coverage chains) computed
here from those fields. It derives no new science, executes no gate,
consumes no seed window, uses no RNG anywhere, and touches no branch of
the frozen map (the queued request dd5a8300 remains the only datum
source; the ladder stays PAUSED). Byte-stable: identical inputs produce
byte-identical output.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

RECEIPTS = {
    "fisher_oc": ("evidence/2026-10-14-w8-blockpower-oc/oc.json", "tick139"),
    "floor_oc": ("evidence/2026-10-14-w8-blockpower-floor-oc/floor-oc.json", "tick140"),
    "cal_oc": ("evidence/2026-10-14-w8-blockpower-cal-oc/cal-oc.json", "tick141"),
}

OUT_DIR = ROOT / "evidence" / "2026-10-14-w8-arbitration-dashboard"
OUT_PATH = OUT_DIR / "dashboard.json"

BRANCH_MAP = (
    "CAL_FAIL -> VOID;  min pair-n < 3400 -> NO_EVENTS;  "
    "p <= 0.05 -> BLOCK_MECHANISM_SUPPORTED;  p > 0.05 -> BLOCK_MECHANISM_NOT_DETECTED"
)


def _load(rel: str) -> dict:
    with open(ROOT / rel, "rb") as fh:
        return json.loads(fh.read().decode("utf-8"))


def _sha256(rel: str) -> str:
    h = hashlib.sha256()
    with open(ROOT / rel, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def build_dashboard() -> dict:
    fisher = _load(RECEIPTS["fisher_oc"][0])
    floor = _load(RECEIPTS["floor_oc"][0])
    cal = _load(RECEIPTS["cal_oc"][0])

    inputs = {
        key: {"path": rel, "sha256": _sha256(rel), "source_tick": tick}
        for key, (rel, tick) in RECEIPTS.items()
    }

    # --- branch-level OC, traced to receipt fields ---------------------
    cal_drop = cal["kernels"]["dropout"]
    cal_resh = cal["kernels"]["reshuffle"]
    vs = cal["verdict_safety"]
    floor_q05 = floor["inversions"]["q_at_5pct_risk"]
    floor_q50 = floor["inversions"]["q_at_50pct_risk"]
    hist_row = floor["yield_curve"][19]  # q_yield = 0.995 (historical floor)
    assert abs(hist_row["q_yield"] - 0.995) < 1e-12

    size = fisher["results"]["H0_SIZE"]
    p_d0223 = fisher["results"]["D0223_BASELINE"]
    p_d030 = fisher["results"]["D030_BASELINE"]
    p_d038 = fisher["results"]["D038_BASELINE"]
    prereg_pow = fisher["normal_approx_power_prereg"]
    floor_edge_size = floor["floor_edge_mc"]["FLOOR_EDGE_H0_SIZE"]
    floor_edge_power = floor["floor_edge_mc"]["FLOOR_EDGE_D030_POWER"]

    branches = [
        {
            "order": 1,
            "branch": "CAL_FAIL",
            "fires_when": "500-seed CAL replay pair census != D2T 367 : L2 131 exactly",
            "verdict": "VOID",
            "role": "substrate-drift detector on fixed replayed seeds (determinism premise; not a sampling gate)",
            "read_before": "the floor and any p-value",
            "oc": {
                "per_seed_corruption_5pct_mismatch": {
                    "dropout": cal_drop["eps_p05"],
                    "marginal_reshuffle": cal_resh["eps_p05"],
                },
                "per_seed_corruption_50pct_mismatch": {
                    "dropout": cal_drop["eps_p50"],
                    "marginal_reshuffle": cal_resh["eps_p50"],
                },
                "cal_pass_at_floor_5pct_collapse_yield": vs["cal_pass_at_tick140_collapse"],
            },
            "provenance": [
                "cal_oc#kernels.dropout.eps_p05",
                "cal_oc#kernels.dropout.eps_p50",
                "cal_oc#kernels.reshuffle.eps_p05",
                "cal_oc#kernels.reshuffle.eps_p50",
                "cal_oc#verdict_safety.cal_pass_at_tick140_collapse",
            ],
        },
        {
            "order": 2,
            "branch": "min pair-n < 3400",
            "fires_when": "pooled pair census below 3400 in either group",
            "verdict": "NO_EVENTS",
            "role": "catastrophic-collapse backstop (execution/substrate anomaly signal, not a sampling outcome)",
            "read_before": "any p-value",
            "oc": {
                "two_group_fire_risk_at_hist_q995": hist_row["map_risk_two_groups"],
                "other_rate_5pct_fire_risk": round(1.0 - floor_q05, 6),
                "q_yield_5pct_fire_risk": floor_q05,
                "q_yield_50pct_fire_risk": floor_q50,
                "floor_edge_pair_n_3400_fisher_size": floor_edge_size["reject_rate"],
                "floor_edge_pair_n_3400_power_delta030": floor_edge_power["reject_rate"],
            },
            "provenance": [
                "floor_oc#yield_curve[19].map_risk_two_groups",
                "floor_oc#inversions.q_at_5pct_risk",
                "floor_oc#inversions.q_at_50pct_risk",
                "floor_oc#floor_edge_mc.FLOOR_EDGE_H0_SIZE.reject_rate",
                "floor_oc#floor_edge_mc.FLOOR_EDGE_D030_POWER.reject_rate",
            ],
        },
        {
            "order": 3,
            "branch": "p <= 0.05",
            "fires_when": "exact one-sided Fisher rejects H0 at alpha 0.05",
            "verdict": "BLOCK_MECHANISM_SUPPORTED",
            "role": "adjudicator (prereg PRIMARY instrument)",
            "read_before": "nothing (terminal)",
            "oc": {
                "realized_size": size["reject_rate"],
                "realized_size_wilson95": size["reject_rate_wilson95"],
                "power_delta030": p_d030["reject_rate"],
                "power_delta030_wilson95": p_d030["reject_rate_wilson95"],
                "power_delta038": p_d038["reject_rate"],
                "prereg_normal_approx_power_lands_inside_mc_wilson": all(
                    lo <= approx <= hi
                    for approx, (lo, hi) in {
                        prereg_pow["delta_0.0223"]: p_d0223["reject_rate_wilson95"],
                        prereg_pow["delta_0.030"]: p_d030["reject_rate_wilson95"],
                        prereg_pow["delta_0.038"]: p_d038["reject_rate_wilson95"],
                    }.items()
                ),
            },
            "provenance": [
                "fisher_oc#results.H0_SIZE.reject_rate",
                "fisher_oc#results.D030_BASELINE.reject_rate",
                "fisher_oc#results.D038_BASELINE.reject_rate",
                "fisher_oc#normal_approx_power_prereg",
            ],
        },
        {
            "order": 4,
            "branch": "p > 0.05",
            "fires_when": "exact one-sided Fisher fails to reject",
            "verdict": "BLOCK_MECHANISM_NOT_DETECTED",
            "role": "adjudicator complement (calibrated reading, not evidence of absence)",
            "read_before": "nothing (terminal)",
            "oc": {
                "power_at_hotrepro_sized_delta0223": p_d0223["reject_rate"],
                "not_detected_rate_if_true_delta0223": round(1.0 - p_d0223["reject_rate"], 5),
                "power_delta0223_wilson95": p_d0223["reject_rate_wilson95"],
            },
            "provenance": [
                "fisher_oc#results.D0223_BASELINE.reject_rate",
                "fisher_oc#results.D0223_BASELINE.reject_rate_wilson95",
            ],
        },
    ]

    # --- cross-receipt relations (the only new content) ----------------
    cal_floor_ratio = (1.0 - floor_q05) / cal_drop["eps_p05"]
    smallest_effect = vs["smallest_effect_seeds"]["d0223_hotrepro"]
    displacement_fractions = {
        kern: vs["escape_displacement_seeds"][kern] / smallest_effect
        for kern in ("dropout", "reshuffle")
    }

    cross_receipt = {
        "cal_to_floor_sensitivity_ratio_per_seed_scale": cal_floor_ratio,
        "cal_to_floor_ratio_meaning": (
            "both 5%-firing points on the same per-seed scale: CAL at independent "
            "per-seed corruption eps (dropout kernel), floor at per-seed other-rate; "
            "the CAL detects corruption ~385x finer than the floor tolerates collapse"
        ),
        "size_chain": {
            "floor_edge_pair_n_3400": floor_edge_size["reject_rate"],
            "nominal_pair_n_3560": size["reject_rate"],
            "alpha": fisher["alpha"],
            "ordering_holds": floor_edge_size["reject_rate"] < size["reject_rate"] <= fisher["alpha"],
        },
        "power_monotone_in_delta": {
            "d0223": p_d0223["reject_rate"],
            "d030": p_d030["reject_rate"],
            "d038": p_d038["reject_rate"],
            "strictly_increasing": p_d0223["reject_rate"] < p_d030["reject_rate"] < p_d038["reject_rate"],
        },
        "clean_run_void_risk": {
            "floor_at_hist_q995": hist_row["map_risk_two_groups"],
            "cal_under_determinism_premise": (
                "0 by construction under the determinism premise on the committed "
                "substrate (9 consecutive committed identity runs; the CAL measures "
                "substrate drift on fixed replayed seeds, not sampling variation)"
            ),
            "reading": "a clean run cannot be VOIDed by statistical chance at historical yield",
        },
        "escape_displacement_fraction_of_smallest_effect": displacement_fractions,
        "coverage_chain": (
            "any per-seed corruption that escapes the CAL with >=95% probability "
            "displaces each group census by at most "
            f"{max(displacement_fractions.values()) * 100:.2f}% of the smallest "
            "pre-registered effect (79.388 seeds at delta 0.0223), while corruption "
            "large enough to matter verdict-wise VOIDs at the CAL near-certainly"
        ),
    }

    return {
        "analysis": "w8-blockpower-arbitration-dashboard",
        "tick": "tick142",
        "inputs": inputs,
        "branch_map": BRANCH_MAP,
        "branches": branches,
        "cross_receipt": cross_receipt,
        "framing": {
            "pre_datum": (
                "measured while request dd5a8300 (nonce molasp-w8-blockpower-t138-b) "
                "is still queued behind the board-operator maintenance lease; "
                "no datum exists; no branch of the frozen map is touched or re-derived"
            ),
            "aggregation_only": (
                "pure function of the three committed receipts; every scalar traces "
                "to a recorded provenance path; the only new content is the "
                "cross_receipt block; byte-stable given identical inputs"
            ),
            "ladder": "PAUSED",
            "no_rng": "no RNG, no trajectories, no gate executed, no seed window consumed",
        },
    }


def main() -> None:
    dashboard = build_dashboard()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(dashboard, indent=2, sort_keys=True) + "\n").encode("utf-8")
    OUT_PATH.write_bytes(payload)
    try:
        print(OUT_PATH.relative_to(ROOT))
    except ValueError:
        print(OUT_PATH)
    print(hashlib.sha256(payload).hexdigest())


if __name__ == "__main__":
    main()
