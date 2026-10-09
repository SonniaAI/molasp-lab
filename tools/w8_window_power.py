"""Pre-registered power and homogeneity arithmetic for the w8 window study.

The primary test treats six fresh seed windows as six binomial groups and
uses the Pearson homogeneity statistic (df=5).  The power calculation uses
the standard noncentral-chi-square approximation for a specified two-hot,
four-baseline alternative; it is design arithmetic, not a scientific result.
"""

from __future__ import annotations

import math

WINDOWS = 6
ALPHA = 0.05
FAMILY_RATE = 1110 / 1499
MIN_EVENTS = 50


def chi2_sf_df5(statistic: float) -> float:
    """Survival function for chi-square with 5 degrees of freedom."""
    if statistic <= 0:
        return 1.0
    z = statistic / 2.0
    root = math.sqrt(z)
    return min(1.0, max(0.0, math.erfc(root) +
                        math.exp(-z) / math.sqrt(math.pi) *
                        (2.0 * root + (4.0 / 3.0) * z * root)))


def _regularized_gamma_q_half_integer(shape: float, z: float) -> float:
    """Regularized upper incomplete gamma for shape=2.5+j, j>=0."""
    if z <= 0:
        return 1.0
    q = math.erfc(math.sqrt(z))  # Q(1/2, z)
    current = 0.5
    while current < shape - 1e-12:
        q += math.exp(current * math.log(z) - z - math.lgamma(current + 1.0))
        current += 1.0
    return min(1.0, max(0.0, q))


def noncentral_chi2_sf_df5(statistic: float, noncentrality: float) -> float:
    """Noncentral chi-square survival via its Poisson mixture (df=5)."""
    if statistic <= 0:
        return 1.0
    if noncentrality < 0:
        raise ValueError("noncentrality must be non-negative")
    mean = noncentrality / 2.0
    z = statistic / 2.0
    weight = math.exp(-mean)
    total = 0.0
    for j in range(1000):
        total += weight * _regularized_gamma_q_half_integer(2.5 + j, z)
        weight *= mean / (j + 1.0)
        if j > mean + 12.0 * math.sqrt(mean + 1.0) and weight < 1e-14:
            break
    return min(1.0, max(0.0, total))


def chi2_critical_df5(alpha: float = ALPHA) -> float:
    """Upper critical value for chi-square(df=5) at tail probability alpha."""
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be in (0, 1)")
    lo, hi = 0.0, 100.0
    for _ in range(100):
        mid = (lo + hi) / 2.0
        if chi2_sf_df5(mid) > alpha:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def heterogeneity_stat(arms: list[tuple[int, int]]) -> tuple[float, float, float]:
    """Return (Pearson statistic, df=5 p-value, pooled share) for six arms.

    Each arm is (D2T_count, pair_terminal_count), where pair terminals are
    D2T+L2. The asymptotic chi-square test is well supported at the planned
    counts (expected successes and failures are both far above 5).
    """
    if len(arms) != WINDOWS:
        raise ValueError(f"expected exactly {WINDOWS} arms")
    if any(n <= 0 or x < 0 or x > n for x, n in arms):
        raise ValueError("arm counts must satisfy 0 <= x <= n and n > 0")
    total_x = sum(x for x, _ in arms)
    total_n = sum(n for _, n in arms)
    p_hat = total_x / float(total_n)
    if p_hat in (0.0, 1.0):
        return 0.0, 1.0, p_hat
    statistic = sum((x - n * p_hat) ** 2 /
                    (n * p_hat * (1.0 - p_hat)) for x, n in arms)
    return statistic, chi2_sf_df5(statistic), p_hat


def read_primary(cal_ok: bool, arms: list[tuple[int, int]]) -> tuple[str, dict | None]:
    """Frozen primary branch; no-event and calibration failures have no verdict."""
    if not cal_ok:
        return "VOID_CAL_FAIL", None
    if len(arms) != WINDOWS or any(n < MIN_EVENTS for _, n in arms):
        return "NO_EVENTS", None
    statistic, p_value, p_hat = heterogeneity_stat(arms)
    branch = "HETEROGENEITY_DETECTED" if p_value < ALPHA \
        else "HETEROGENEITY_NOT_DETECTED"
    return branch, {"statistic": statistic, "df": WINDOWS - 1,
                    "p_value": p_value, "pooled_share": p_hat,
                    "alpha": ALPHA}


def two_hot_power(n_per_window: int, delta: float,
                  baseline: float = FAMILY_RATE) -> tuple[float, float]:
    """Approximate power for four windows at baseline and two at baseline+delta."""
    if n_per_window <= 0 or delta < 0 or baseline + delta >= 1.0:
        raise ValueError("invalid sample size or rate alternative")
    rates = [baseline] * 4 + [baseline + delta] * 2
    mean_rate = sum(rates) / WINDOWS
    variance = mean_rate * (1.0 - mean_rate)
    noncentrality = n_per_window * sum((p - mean_rate) ** 2 for p in rates) / variance
    power = noncentral_chi2_sf_df5(chi2_critical_df5(), noncentrality)
    return noncentrality, power
