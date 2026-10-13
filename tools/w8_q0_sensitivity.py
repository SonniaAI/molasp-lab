"""Position-weighting sensitivity of the w8 family pool constant q0.

The family pool q0 = 1110/1499 (arms 3+5+7: 375/500, 370/500, 365/499,
receipt evidence/2026-10-09-w8-blockprobe/run.out sha256 fe7be746) is built
ONLY from first-position windows of their seed families.  The tick-113
blockpos census flagged q0 as pos-1-weighted; the posfresh probe (SON-5144,
request bda50c6b...) is queued to adjudicate between window-noise and a
position-decline account.  Until it returns, every future use of q0 must
carry this sensitivity band.

This module is design arithmetic on committed counts: no simulation, no new
seed burns, and no re-test of the frozen eight-window verdicts.  It answers
one forward-looking question: if the descriptive first-vs-rest gap were
real, how wrong is q0 as a family-rate constant, and what does that error do
to the two instruments that consume it?

Numbers are deterministic; tests pin the exact outputs.
"""

from __future__ import annotations

import math

# Committed receipt facts (evidence/2026-10-09-w8-blockprobe/run.out).
ARM3 = (375, 500)
ARM5 = (370, 500)
ARM7 = (365, 499)
FAMILY_X = ARM3[0] + ARM5[0] + ARM7[0]   # 1110
FAMILY_N = ARM3[1] + ARM5[1] + ARM7[1]   # 1499
Q0 = FAMILY_X / FAMILY_N                 # 0.7404936624416277...

# Tick-112 descriptive anchors (research-log/2026-10-13-w8-blockpos.md):
# pooled first windows 780/1000, pooled rest 1777/2499.
FIRST_X, FIRST_N = 780, 1000
REST_X, REST_N = 1777, 2499
SHARE_FIRST = FIRST_X / FIRST_N          # 0.780
SHARE_REST = REST_X / REST_N             # 0.7110844337735094...
DELTA_DESC = SHARE_FIRST - SHARE_REST    # 0.0689155662264905...

ALPHA = 0.05
Z_ALPHA = 1.6448536269514722


def wilson95(x: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion."""
    p = x / n
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2.0 * n)) / denom
    half = z / denom * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n))
    return (centre - half, centre + half)


def family_rate_under_decline(delta: float, w_first: float) -> float:
    """Family rate implied when q0 (a first-window-only pool) estimates
    share(first) and non-first windows sit delta below it.

    w_first is the first window's share of a family's windows.  The
    position-balanced family mean is q0 - delta * (1 - w_first): exact when
    every non-first window shares one rate, which is the two-rate decline
    model the dispute is about.
    """
    if not 0.0 < w_first <= 1.0:
        raise ValueError("w_first must be in (0, 1]")
    return Q0 - delta * (1.0 - w_first)


def _log_binom_pmf(i: int, n: int, p: float) -> float:
    return (math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1)
            + i * math.log(p) + (n - i) * math.log1p(-p))


def binom_cdf(k: int, n: int, p: float) -> float:
    """Exact binomial P(X <= k) by log-sum-exp over the pmf (n <= ~2000)."""
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    terms = [_log_binom_pmf(i, n, p) for i in range(k + 1)]
    m = max(terms)
    return math.exp(m) * sum(math.exp(t - m) for t in terms)


def binom_sf(k: int, n: int, p: float) -> float:
    """Exact binomial P(X > k) = 1 - CDF, clamped to [0, 1]."""
    return min(1.0, max(0.0, 1.0 - binom_cdf(k, n, p)))


def critical_low(n: int, p0: float, alpha: float = ALPHA) -> int:
    """Largest k with P(X <= k | p0) <= alpha (one-sided low gate)."""
    k = int(p0 * n)
    while binom_cdf(k, n, p0) > alpha:
        k -= 1
    while binom_cdf(k + 1, n, p0) <= alpha:
        k += 1
    return k


def false_flag_rate(n: int, p_true: float, p_gate: float,
                    alpha: float = ALPHA) -> float:
    """P(a window at true rate p_true trips the low gate calibrated at
    p_gate): exact binomial tail at the gate's critical value."""
    c = critical_low(n, p_gate, alpha)
    return binom_cdf(c, n, p_true)


def normal_power_one_sided(delta: float, n: int, p_bar: float,
                           z_alpha: float = Z_ALPHA) -> float:
    """Normal-approximation one-sided two-proportion power at equal group
    size n (planning arithmetic; the confirmatory census uses the exact
    conditional hypergeometric scan)."""
    se = math.sqrt(2.0 * p_bar * (1.0 - p_bar) / n)
    return 0.5 * (1.0 + math.erf((delta / se - z_alpha) / math.sqrt(2.0)))


SCENARIOS = (
    # (label, delta, w_first) — delta is the first-vs-rest gap assumed real.
    ("window-noise (q0 stands)", 0.0, None),
    ("decline d=0.0689, w=1/10 (10-window blocks, posfresh plan)", DELTA_DESC, 0.1),
    ("decline d=0.0689, w=1/5 (5-window families)", DELTA_DESC, 0.2),
    ("decline d=0.0689, w=1/2 (2-window families)", DELTA_DESC, 0.5),
    ("half-effect d=0.0345, w=1/2", DELTA_DESC / 2.0, 0.5),
)


def build_report() -> str:
    lines = []
    lo, hi = wilson95(FAMILY_X, FAMILY_N)
    lines.append(f"family pool: {FAMILY_X}/{FAMILY_N} = {Q0:.7f} "
                 f"(Wilson-95 [{lo:.5f}, {hi:.5f}])")
    lines.append(f"descriptive first-vs-rest gap: {SHARE_FIRST:.5f} - "
                 f"{SHARE_REST:.7f} = {DELTA_DESC:.7f}")
    n_gate = 1000
    c_gate = critical_low(n_gate, Q0)
    n_census, delta_census = 5000, 0.02
    power_at_q0 = normal_power_one_sided(delta_census, n_census, Q0)
    lines.append(f"low-gate calibration at q0, n={n_gate}: "
                 f"P(X<=k|q0)<=0.05 up to k={c_gate}")
    lines.append("")
    lines.append(f"{'scenario':<58} {'family rate':>11} "
                 f"{'low-gate flag':>13} {'census pwr':>10}")
    for label, delta, w in SCENARIOS:
        rate = Q0 if w is None else family_rate_under_decline(delta, w)
        flag = (false_flag_rate(n_gate, rate, Q0) if w is not None
                else ALPHA)
        power = normal_power_one_sided(delta_census, n_census, rate)
        lines.append(f"{label:<58} {rate:>11.7f} {flag:>13.4f} "
                     f"{power:>10.4f}")
    lines.append("")
    lines.append("census power at q0 for reference: "
                 f"{power_at_q0:.4f} (delta=0.02, n=5000/window, normal "
                 "approx)")
    return "\n".join(lines)


if __name__ == "__main__":
    print(build_report())
