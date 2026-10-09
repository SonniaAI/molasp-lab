#!/usr/bin/env python3
"""Independently collect the pre-registered six-window heterogeneity run.

Reads the raw stdout imported from one owned cluster-queue request, validates
its frozen calibration/seed-window identity, recomputes the Pearson
homogeneity test and Wilson intervals from raw counts, and checks the
instrument's reported branch and arithmetic before emitting a receipt.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

EXPECTED_BLOCKS = (8, 9, 10, 11, 12, 13)
EXPECTED_SEEDS = (380261107, 400261107, 420261107,
                  440261107, 460261107, 480261107)
EXPECTED_N = 5000
CAL_D2T = 367
CAL_L2 = 131
CAL_SEED0 = 260261107
ALPHA = 0.05
MIN_EVENTS = 50
FAMILY_RATE = 1110 / 1499


def _close(actual: float, expected: float, label: str) -> None:
    if not math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12):
        raise ValueError(f"{label} mismatch: {actual!r} != {expected!r}")


def chi2_sf_df5(statistic: float) -> float:
    """Chi-square(df=5) upper tail from the half-integer gamma identity."""
    if statistic <= 0:
        return 1.0
    z = statistic / 2.0
    root = math.sqrt(z)
    value = math.erfc(root) + math.exp(-z) / math.sqrt(math.pi) * (
        2.0 * root + (4.0 / 3.0) * z * root)
    return min(1.0, max(0.0, value))


def wilson95(successes: int, trials: int) -> list[float] | None:
    if trials <= 0:
        return None
    z = 1.96
    p = successes / float(trials)
    d = 1.0 + z * z / trials
    center = (p + z * z / (2.0 * trials)) / d
    half = z * math.sqrt(p * (1.0 - p) / trials +
                         z * z / (4.0 * trials * trials)) / d
    return [round(center - half, 5), round(center + half, 5)]


def parse_runout(text: str) -> tuple[dict, dict]:
    stats = None
    reported = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("VERDICTS "):
            reported = json.loads(stripped[len("VERDICTS "):])
            continue
        try:
            candidate = json.loads(stripped)
        except ValueError:
            continue
        if isinstance(candidate, dict) and "arms" in candidate and "protocol" in candidate:
            stats = candidate
    if stats is None or reported is None:
        raise ValueError("run.out must contain the stats JSON and VERDICTS line")
    return stats, reported


def collect(text: str, request_id: str | None = None) -> dict:
    stats, reported = parse_runout(text)
    protocol = stats["protocol"]
    if (protocol.get("n_per_window") != EXPECTED_N or
            protocol.get("primary_df") != 5 or
            protocol.get("primary_test") != "Pearson homogeneity" or
            protocol.get("alpha") != ALPHA or
            protocol.get("dg") != 2.0 or protocol.get("win_mult") != 8.0):
        raise ValueError("protocol fields do not match the frozen registration")

    arms_data = stats["arms"]
    if len(arms_data) != len(EXPECTED_BLOCKS):
        raise ValueError("expected exactly six confirmatory windows")
    pairs: list[tuple[int, int]] = []
    windows = []
    for index, row in enumerate(arms_data):
        expected_block = EXPECTED_BLOCKS[index]
        expected_seed = EXPECTED_SEEDS[index]
        if (row.get("block") != expected_block or
                row.get("seed0") != expected_seed or
                row.get("n_trajectories") != EXPECTED_N):
            raise ValueError(f"window {index} does not match frozen block/seed/n")
        d2t, l2, other = row.get("D2T"), row.get("L2"), row.get("other")
        if not all(isinstance(value, int) and value >= 0
                   for value in (d2t, l2, other)):
            raise ValueError(f"window {expected_block} has invalid terminal counts")
        pair_n = d2t + l2
        if row.get("pair_n") != pair_n:
            raise ValueError(f"window {expected_block} pair_n is not D2T+L2")
        share = d2t / float(pair_n) if pair_n else None
        if share is not None:
            _close(row.get("share"), share, f"window {expected_block} share")
        ci = wilson95(d2t, pair_n)
        if row.get("wilson95") != ci:
            raise ValueError(f"window {expected_block} Wilson interval mismatch")
        pairs.append((d2t, pair_n))
        windows.append({
            "block": expected_block,
            "seed0": expected_seed,
            "n_trajectories": EXPECTED_N,
            "D2T": d2t,
            "L2": l2,
            "other": other,
            "pair_n": pair_n,
            "share": share,
            "wilson95": ci,
        })

    cal = stats["calibration"]
    mid = cal["mid_w4"]
    calibration_ok = (mid.get("D2T") == CAL_D2T and mid.get("L2") == CAL_L2)
    calibration = "CAL_OK" if calibration_ok else "CAL_FAIL"
    if cal.get("status") != calibration:
        raise ValueError("calibration status does not match its frozen count gate")
    if (cal.get("expected_D2T_L2") != [CAL_D2T, CAL_L2] or
            cal.get("seed0") != CAL_SEED0 or cal.get("n") != 500):
        raise ValueError("calibration identity does not match the registration")

    pooled_x = sum(x for x, _ in pairs)
    pooled_n = sum(n for _, n in pairs)
    pooled_share = pooled_x / float(pooled_n) if pooled_n else None
    pooled_ci = wilson95(pooled_x, pooled_n)
    thresholds = {
        "at_least_family_plus_0.02": sum(
            window["share"] is not None and
            window["share"] >= FAMILY_RATE + 0.02 for window in windows),
        "at_least_family_plus_0.03": sum(
            window["share"] is not None and
            window["share"] >= FAMILY_RATE + 0.03 for window in windows),
    }
    descriptive = stats["descriptive"]
    _close(descriptive.get("pooled_pair_rate"), pooled_share,
           "pooled pair rate")
    if descriptive.get("pooled_pair_wilson95") != pooled_ci:
        raise ValueError("pooled Wilson interval mismatch")
    if descriptive.get("windows_at_least_family_plus") != thresholds:
        raise ValueError("descriptive threshold counts mismatch")

    if not calibration_ok:
        branch, metrics = "VOID_CAL_FAIL", None
    elif any(n < MIN_EVENTS for _, n in pairs):
        branch, metrics = "NO_EVENTS", None
    else:
        total_x = sum(x for x, _ in pairs)
        total_n = sum(n for _, n in pairs)
        p_hat = total_x / float(total_n)
        if p_hat in (0.0, 1.0):
            statistic, p_value = 0.0, 1.0
        else:
            statistic = sum((x - n * p_hat) ** 2 /
                            (n * p_hat * (1.0 - p_hat)) for x, n in pairs)
            p_value = chi2_sf_df5(statistic)
        branch = ("HETEROGENEITY_DETECTED" if p_value < ALPHA else
                  "HETEROGENEITY_NOT_DETECTED")
        metrics = {"statistic": statistic, "df": 5, "p_value": p_value,
                   "pooled_share": p_hat, "alpha": ALPHA}

    expected_reported = {"CAL": calibration, "PRIMARY": branch}
    if reported != expected_reported:
        raise ValueError(f"instrument verdict mismatch: {reported!r} != {expected_reported!r}")
    primary = stats["primary"]
    if primary.get("branch") != branch:
        raise ValueError("instrument primary branch disagrees with raw-count gate")
    instrument_metrics = primary.get("metrics")
    if metrics is None:
        if instrument_metrics is not None:
            raise ValueError("instrument emitted metrics on a no-verdict branch")
    else:
        if not isinstance(instrument_metrics, dict):
            raise ValueError("instrument omitted primary metrics")
        for key, value in metrics.items():
            if key not in instrument_metrics:
                raise ValueError(f"instrument omitted {key}")
            _close(instrument_metrics[key], value, f"instrument {key}")

    interpretation = {
        "HETEROGENEITY_NOT_DETECTED": (
            "The pre-registered test did not detect between-window "
            "heterogeneity at alpha=.05 for this simulator/protocol; this is "
            "not proof that the windows are identical."),
        "HETEROGENEITY_DETECTED": (
            "The pre-registered test detected between-window heterogeneity "
            "for this simulator/protocol; it does not identify a cause."),
        "VOID_CAL_FAIL": "Calibration failed; no scientific verdict is valid.",
        "NO_EVENTS": "The minimum pair-terminal count failed; no scientific verdict is valid.",
    }[branch]
    return {
        "schema": 1,
        "tool": "collect_w8_window_resolution",
        "request_id": request_id,
        "source_run_out_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "registration": {
            "blocks": list(EXPECTED_BLOCKS),
            "seed0": list(EXPECTED_SEEDS),
            "n_per_window": EXPECTED_N,
            "primary_test": "Pearson homogeneity",
            "df": 5,
            "alpha": ALPHA,
            "calibration_D2T_L2": [CAL_D2T, CAL_L2],
            "calibration_seed0": CAL_SEED0,
        },
        "cross_check": "ok",
        "branch": branch,
        "calibration": {
            "status": calibration,
            "mid_w4_D2T_L2_other": [mid.get("D2T"), mid.get("L2"), mid.get("other")],
        },
        "windows": windows,
        "descriptive": {
            "pooled_D2T": pooled_x,
            "pooled_pair_n": pooled_n,
            "pooled_pair_rate": pooled_share,
            "pooled_pair_wilson95": pooled_ci,
            "windows_at_least_family_plus": thresholds,
            "historical_family_rate": FAMILY_RATE,
        },
        "primary": metrics,
        "instrument_primary": primary,
        "interpretation": interpretation,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("runout", help="raw imported run.out from the queue result")
    parser.add_argument("--request", required=True, help="owned queue request id")
    parser.add_argument("--out", required=True, help="path to write the verified receipt")
    args = parser.parse_args(argv)
    text = Path(args.runout).read_text(encoding="utf-8")
    try:
        receipt = collect(text, request_id=args.request)
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        parser.error(f"collection refused: {exc}")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    print(json.dumps({"branch": receipt["branch"],
                      "cross_check": receipt["cross_check"],
                      "receipt": str(out),
                      "source_run_out_sha256": receipt["source_run_out_sha256"]},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
