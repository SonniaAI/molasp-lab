"""Apply design 011's descriptive window tiers to each w8 arm separately.

This is a deterministic interpretation of committed census counts. It runs
no trajectories and performs no cross-arm or family-level inference.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from molasp.offchannel import window_tier
from tools.w8_stratified_census import summarize

TIERS = ("contested", "ratchet-tilting", "ratchet-tilted")


def interval_tiers(lo: float, hi: float) -> tuple[str, ...]:
    """Return the design-011 labels intersected by one closed interval."""
    if not 0.0 <= lo <= hi <= 1.0:
        raise ValueError("need 0 <= lo <= hi <= 1")
    first = TIERS.index(window_tier(lo))
    last = TIERS.index(window_tier(hi))
    return TIERS[first:last + 1]


def summarize_armwise_tiers() -> dict:
    """Report point labels and interval compatibility arm by arm."""
    arms = summarize()["contested_four_arm_armwise_report_only"]["arms"]
    rows = {}
    for label, arm in arms.items():
        lo, hi = arm["wilson95"]
        rows[label] = {
            "x": arm["x"],
            "n": arm["n"],
            "share": arm["share"],
            "point_tier": window_tier(arm["share"]),
            "wilson95": [lo, hi],
            "interval_compatible_tiers": list(interval_tiers(lo, hi)),
            "single_tier_throughout_interval": len(interval_tiers(lo, hi)) == 1,
        }
    return {
        "source": "tools/w8_stratified_census.py; committed tick-99 receipts",
        "tier_definition": "designs/011-window-indexed-marginal-pricing.md",
        "scope": "per-arm descriptive labels; pointwise intervals, not simultaneous; no cross-arm inference",
        "arms": rows,
    }


if __name__ == "__main__":
    print(json.dumps(summarize_armwise_tiers(), indent=2, sort_keys=True))
