"""Family-wise (multiplicity-controlled) arm bands for the w8 four-arm
census (tick 151, SON-5152).

Ticks 148-149 established the report-only arm-wise baseline: per-arm
pointwise Wilson-95 intervals (z=1.96, receipt convention), with the
explicit caveat that they are not simultaneous. This module answers the
next bounded question with zero new sampling: what survives multiplicity
control when all four arms are read together?

Two family-wise readings, both Bonferroni over k=4 arms (valid under any
dependence structure, so no cross-arm model is smuggled in):

- TWO-SIDED simultaneous family-95% bands: per-arm two-sided interval at
  level 1 - alpha/k = 0.9875 (per-side tail alpha/(2k) = 0.00625,
  z = Phi^-1(0.99375)). P(all four true shares inside their bands) >= 0.95.
- ONE-SIDED family-95% lower bounds: per-arm lower bound at tail
  alpha/k = 0.0125 (z = Phi^-1(0.9875)). P(all four true shares above
  their lower bounds) >= 0.95.

Against design 011's descriptive tier semantics this yields exactly two
statements and nothing more: (a) every arm's simultaneous two-sided band
still straddles the 0.75 tier boundary, so NO arm earns a family-wise
stable tier label; (b) every arm's family-wise lower bound (one-sided,
and even the two-sided lower endpoint) exceeds the 0.55 floor tier.

Counts are imported from tools.w8_stratified_census.CONTESTED_FOUR_ARM_
STRTA (receipt-pinned there, cross-checked by its own tests); this module
adds no new data, runs zero trajectories, and executes no gate. The four
arms are the four observed tick-99 strata — a fixed census vector, not a
random sample of arms; the family is these four arms and nobody else.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from statistics import NormalDist

ROOT = str(Path(__file__).resolve().parent.parent)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.w8_stratified_census import CONTESTED_FOUR_ARM_STRATA

ALPHA = 0.05
K = len(CONTESTED_FOUR_ARM_STRATA)
Z_TWO_SIDED = NormalDist().inv_cdf(1.0 - ALPHA / (2.0 * K))   # 0.99375 quantile
Z_ONE_SIDED = NormalDist().inv_cdf(1.0 - ALPHA / K)           # 0.9875 quantile

TIER_FLOOR = 0.55     # design 011 descriptive tier floor
TIER_BOUNDARY = 0.75  # design 011 descriptive tier boundary


def wilson(x: int, n: int, z: float, one_sided_lower: bool = False):
    """Wilson score interval at quantile z. one_sided_lower=True returns
    (lower, None) using the same centring (the lower endpoint is the
    one-sided family bound)."""
    if n <= 0 or not 0 <= x <= n:
        raise ValueError("need 0 <= x <= n and n >= 1")
    p = x / n
    z2 = z * z
    denom = 1.0 + z2 / n
    centre = (p + z2 / (2.0 * n)) / denom
    half = (z / denom) * math.sqrt(p * (1.0 - p) / n + z2 / (4.0 * n * n))
    if one_sided_lower:
        return centre - half, None
    return centre - half, centre + half


def familywise_bands() -> dict:
    """Per-arm Bonferroni-adjusted bands + the two family statements."""
    arms = {}
    for s in CONTESTED_FOUR_ARM_STRATA:
        lo2, hi2 = wilson(s.x, s.n, Z_TWO_SIDED)
        lo1, _ = wilson(s.x, s.n, Z_ONE_SIDED, one_sided_lower=True)
        arms[s.label] = {
            "x": s.x,
            "n": s.n,
            "share": s.x / s.n,
            "band_simultaneous_95": (lo2, hi2),
            "lower_one_sided_family_95": lo1,
            "straddles_0_75": lo2 < TIER_BOUNDARY < hi2,
            "above_floor_two_sided": lo2 > TIER_FLOOR,
            "above_floor_one_sided": lo1 > TIER_FLOOR,
            "seed_base": s.provenance,
            "source": s.source,
        }
    return {
        "method": "Bonferroni-adjusted Wilson, k=4, alpha=0.05 (valid under any dependence)",
        "z_two_sided_simultaneous": Z_TWO_SIDED,
        "z_one_sided_family": Z_ONE_SIDED,
        "arms": arms,
        "family_statements": {
            "no_arm_has_familywise_stable_tier_label":
                all(a["straddles_0_75"] for a in arms.values()),
            "every_arm_above_floor_familywise":
                all(a["above_floor_one_sided"] and a["above_floor_two_sided"]
                    for a in arms.values()),
            "min_two_sided_lower_endpoint":
                min(a["band_simultaneous_95"][0] for a in arms.values()),
            "min_one_sided_lower_bound":
                min(a["lower_one_sided_family_95"] for a in arms.values()),
        },
        "scope": ("census shares of the four observed tick-99 arms; "
                  "not a test of equality across arms; no pooled claim"),
    }


if __name__ == "__main__":
    out = familywise_bands()
    print(json.dumps(out, indent=2, sort_keys=True))
