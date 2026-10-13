"""Provenance-stratified census estimation design (w8) — pure planning math.

Pre-registered 2026-10-13 (tick 122, SON-5152) BEFORE the blockpower
arbitration datum (`d3aa0acaa37ff4c9...`) lands. This module runs ZERO
trajectories: it recomputes descriptive summaries from already-collected,
committed evidence and states the branch-conditional census design that
serves BOTH frozen branches of the blockpower map:

- NOT_DETECTED -> pooled census stays primary (stage-2 plan 1dd0e8b
  unchanged); the stratified estimator here is the secondary,
  variance-reducing readout only.
- SUPPORTED -> the pooled line is retired by the frozen map; the design
  here becomes the primary census route: per-provenance-stratum Wilson
  intervals + a conservative simultaneous band, Neyman allocation for any
  growth, and no cross-family pooling without a fresh homogeneity gate at
  the new n.

All frozen counts below are transcribed from committed receipts (paths in
each stratum tuple). The four-arm dispersion gate instrument (tick 93/99)
is untouched and remains the pooling authority; nothing here executes a
gate, unfreezes the ladder, or claims a result.

z conventions (stated, not implied): Wilson uses z=1.96 matching the
committed receipts; the design power math uses one-sided alpha=0.05
(z=1.6448536) with 80% power (z=0.8416212) per the blockpower prereg.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

Z_WILSON = 1.96
Z_ALPHA = 1.6448536269514722   # one-sided alpha = 0.05
Z_POWER = 0.8416212335729143   # power = 0.80


@dataclass(frozen=True)
class Stratum:
    label: str
    x: int                # pair-terminal D2T count
    n: int                # pair-terminal n (D2T + L2)
    source: str           # committed receipt path
    provenance: str       # seed-base family (block provenance)
    tags: tuple = field(default=())


# --- frozen data (transcribed verbatim from committed receipts) ---------

# Tick 103 six-window homogeneity study: HETEROGENEITY_NOT_DETECTED,
# X2(5) = 2.7713095514, p = 0.7351922075. Blocks 8-13, n=5000 each.
SIX_WINDOW_STRATA = (
    Stratum("block8", 3644, 4999, "evidence/2026-10-09-w8-window-heterogeneity/run.out", "380261107"),
    Stratum("block9", 3707, 4998, "evidence/2026-10-09-w8-window-heterogeneity/run.out", "400261107"),
    Stratum("block10", 3692, 4999, "evidence/2026-10-09-w8-window-heterogeneity/run.out", "420261107"),
    Stratum("block11", 3675, 4999, "evidence/2026-10-09-w8-window-heterogeneity/run.out", "440261107"),
    Stratum("block12", 3696, 4998, "evidence/2026-10-09-w8-window-heterogeneity/run.out", "460261107"),
    Stratum("block13", 3697, 4996, "evidence/2026-10-09-w8-window-heterogeneity/run.out", "480261107"),
)

# Tick 99 line-census arms; the corrected four-arm pool of the tick-119
# dispersion gate (POOLING_CONTESTED). Descriptive here only.
CONTESTED_FOUR_ARM_STRATA = (
    Stratum("arm3", 375, 500, "evidence/2026-10-13-w8-arm6/run.out (tick-99 census, corrected set)", "340261107", ("line",)),
    Stratum("arm4", 106, 153, "evidence/2026-10-13-w8-arm6/run.out (tick-99 census, corrected set)", "340261107", ("line",)),
    Stratum("arm6", 389, 500, "evidence/2026-10-13-w8-arm6/run.out", "340261107", ("line", "hot")),
    Stratum("arm7", 365, 499, "evidence/2026-10-13-w8-arm6/run.out", "340261107", ("line",)),
)

# Calibration identity chain anchor (10 consecutive CAL_OK runs).
CAL_STRATUM = Stratum("cal-mid-w4", 367, 498, "evidence/2026-10-09-w8-window-heterogeneity/run.out", "260261107", ("cal",))


# --- interval + homogeneity math -----------------------------------------

def wilson95(x: int, n: int, z: float = Z_WILSON) -> tuple[float, float]:
    """Standard Wilson score interval (z=1.96 matches committed receipts)."""
    if n <= 0 or not 0 <= x <= n:
        raise ValueError("need 0 <= x <= n and n >= 1")
    p = x / n
    z2 = z * z
    denom = 1.0 + z2 / n
    centre = (p + z2 / (2.0 * n)) / denom
    half = (z / denom) * math.sqrt(p * (1.0 - p) / n + z2 / (4.0 * n * n))
    return (centre - half, centre + half)


def pooled(strata) -> tuple[int, int, float, tuple[float, float]]:
    """Size-weighted pooled share + Wilson-95. Valid as a *primary* reading
    only where the applicable homogeneity gate says pooling is safe."""
    x = sum(s.x for s in strata)
    n = sum(s.n for s in strata)
    share = x / n
    lo, hi = wilson95(x, n)
    return x, n, share, (lo, hi)


def homogeneity_x2(strata) -> dict:
    """Pearson homogeneity statistic, df = k-1, exact chi-square tail via the
    regularized upper incomplete gamma (series + continued fraction)."""
    k = len(strata)
    if k < 2:
        raise ValueError("need at least two strata")
    x = sum(s.x for s in strata)
    n = sum(s.n for s in strata)
    p_hat = x / n
    stat = sum((s.x - s.n * p_hat) ** 2 / (s.n * p_hat * (1.0 - p_hat))
               for s in strata)
    return {
        "statistic": stat,
        "df": k - 1,
        "p_value": chi2_sf(stat, k - 1),
        "pooled_share": p_hat,
    }


def _gamma_q(a: float, x: float) -> float:
    """Regularized upper incomplete gamma Q(a, x), x > 0."""
    if x <= 0.0:
        return 1.0
    if x < a + 1.0:                      # series for P, return 1 - P
        term = 1.0 / a
        total = term
        ap = a
        for _ in range(1000):
            ap += 1.0
            term *= x / ap
            total += term
            if abs(term) < abs(total) * 1e-16:
                break
        p = total * math.exp(-x + a * math.log(x) - math.lgamma(a))
        return 1.0 - p
    # continued fraction for Q (Lentz)
    tiny = 1e-300
    b = x + 1.0 - a
    c = 1.0 / tiny
    d = 1.0 / b
    h = d
    for i in range(1, 1000):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < tiny:
            d = tiny
        c = b + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-16:
            break
    return h * math.exp(-x + a * math.log(x) - math.lgamma(a))


def chi2_sf(x: float, df: int) -> float:
    """Chi-square survival function = Q(df/2, x/2)."""
    if x <= 0.0:
        return 1.0
    return _gamma_q(0.5 * df, 0.5 * x)


# --- stratified estimators (design math, no gates) -----------------------

def stratified_estimators(strata) -> dict:
    """Size-weighted (= pooled) and inverse-variance-weighted shares with a
    delta-method SE for the weighted form, plus a conservative simultaneous
    band (weighted sum of per-stratum Wilson half-widths; Bonferroni-flavored
    overstatement by construction, labelled conservative)."""
    p_hats = [s.x / s.n for s in strata]
    vars_ = [p * (1.0 - p) / s.n for p, s in zip(p_hats, strata)]
    w_iv = [1.0 / v for v in vars_]
    w_sum = sum(w_iv)
    theta = sum(w * p for w, p in zip(w_iv, p_hats)) / w_sum
    se_theta = math.sqrt(1.0 / w_sum)
    band = sum((w / w_sum) * 0.5 * (wilson95(s.x, s.n)[1] - wilson95(s.x, s.n)[0])
               for w, s in zip(w_iv, strata))
    return {
        "inv_var_share": theta,
        "inv_var_se": se_theta,
        "conservative_band_halfwidth": band,
        "per_stratum_wilson95": {
            s.label: wilson95(s.x, s.n) for s in strata
        },
    }


def neyman_allocation(strata, total_n: int, worst_case: bool = False) -> dict:
    """Integer Neyman allocation (largest remainder): n_i proportional to
    sigma_i. Worst case uses sigma = 0.5 for every stratum (equal split)."""
    k = len(strata)
    if total_n < k:
        raise ValueError("total_n must give at least one per stratum")
    if worst_case:
        sigma = [0.5] * k
    else:
        sigma = [math.sqrt(p * (1.0 - p))
                 for p in (s.x / s.n for s in strata)]
    total_sigma = sum(sigma)
    raw = [total_n * s / total_sigma for s in sigma]
    alloc = [max(1, int(math.floor(r))) for r in raw]
    # distribute the remainder to the largest fractional parts
    order = sorted(range(k), key=lambda i: raw[i] - math.floor(raw[i]),
                   reverse=True)
    i = 0
    while sum(alloc) < total_n:
        alloc[order[i % k]] += 1
        i += 1
    while sum(alloc) > total_n:
        cand = max(range(k), key=lambda j: alloc[j])
        if alloc[cand] > 1:
            alloc[cand] -= 1
        else:
            break
    return {
        "allocation": {s.label: a for s, a in zip(strata, alloc)},
        "sigma": {s.label: sig for s, sig in zip(strata, sigma)},
    }


def design_power(p_bar: float, n_per_group: int) -> dict:
    """Two-group normal-approximation design math (one-sided alpha=0.05,
    power 80%): SE, MDE90, and the required n at a target delta. This is the
    frozen (0.040/delta)^2 rule's underlying convention, cross-checking the
    blockpower prereg numbers; the prereg itself remains the authority."""
    if not 0.0 < p_bar < 1.0 or n_per_group < 2:
        raise ValueError("need 0 < p_bar < 1 and n >= 2")
    se = math.sqrt(2.0 * p_bar * (1.0 - p_bar) / n_per_group)
    mde90 = (Z_ALPHA + Z_POWER) * se
    return {
        "se": se,
        "mde90": mde90,
        "required_n_at": lambda delta: math.ceil(
            ((Z_ALPHA + Z_POWER) ** 2 * 2.0 * p_bar * (1.0 - p_bar))
            / (delta * delta)),
    }


def summarize() -> dict:
    """One-shot descriptive summary of the frozen strata (what the design
    note quotes). No verdicts; no gates."""
    six = pooled(SIX_WINDOW_STRATA)
    contested = pooled(CONTESTED_FOUR_ARM_STRATA)
    return {
        "six_window_pooled": {
            "x": six[0], "n": six[1], "share": six[2], "wilson95": six[3],
            "homogeneity": homogeneity_x2(SIX_WINDOW_STRATA),
        },
        "contested_four_arm_descriptive": {
            "x": contested[0], "n": contested[1], "share": contested[2],
            "wilson95": contested[3],
            "homogeneity_descriptive_only": homogeneity_x2(CONTESTED_FOUR_ARM_STRATA),
        },
        "cal": {"share": CAL_STRATUM.x / CAL_STRATUM.n,
                "wilson95": wilson95(CAL_STRATUM.x, CAL_STRATUM.n)},
        "stratified_estimators_six_window": stratified_estimators(SIX_WINDOW_STRATA),
    }


if __name__ == "__main__":
    import json
    out = summarize()
    # lambdas are not JSON-serializable; design_power printed separately
    print(json.dumps(out, indent=2, sort_keys=True))
    for p in (0.74, 0.7373036780152723):
        d = design_power(p, 3560)
        print(json.dumps({
            "p_bar": p, "n_per_group": 3560, "se": d["se"], "mde90": d["mde90"],
            "required_n_at_0.030": d["required_n_at"](0.030),
        }, sort_keys=True))
