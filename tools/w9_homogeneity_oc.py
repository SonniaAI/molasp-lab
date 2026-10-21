#!/usr/bin/env python3
"""Pre-datum operating characteristics of the W9 four-arm homogeneity instrument (2026-10-21, tick 147).

The post-W8 triage note (research-log/2026-10-21-postw8-thread-triage.md,
tick 146) staged two exits for the POOLING_CONTESTED thread and made the
next tick's duty explicit BEFORE either exit is chosen: measure the exact
conditional operating characteristics of the candidate four-arm homogeneity
instrument pre-datum (the tick-139..142 pattern), then let the exit with
the higher honest information-per-queue-hour win.

This module is that measurement. The instrument candidate is the house
statistic of record that fired the contest in the first place: the tick-93
dispersion receipt rule — per arm, an exact two-sided binomial test of that
arm against the leave-one-out pool of the other arms; POOLING_CONTESTED iff
the minimum p <= alpha (0.05, the tick-93 planning convention, no
multiplicity correction). Measuring THAT statistic's realized size and
power is the honest pre-datum duty: it is what a W9 prereg would freeze if
Exit A (powered four-arm arbitration) were chosen.

Method: fixed-seed Monte Carlo, stdlib Mersenne Twister (random.Random),
binomial draws via the cached log-CDF inversion sampler imported from the
tick-123 census-sim module; two-sided point-probability p-values computed
with a precomputed log-factorial table and cross-checked against
tools.w8_dispersion_receipt.exact_two_sided_p (the tick-93 reference
implementation) on every receipt write.

Worlds:
- SIZE_*: all four arms at the pooled tick-99 census share (H0: one
  common true share). Realized size of the min-p rule at nominal 0.05.
- RESIDUAL_*: the tick-99 pattern as it looks AFTER W8 reassigned arm-6's
  hot share to its family-consistent fresh continuation — shares
  (0.7500, 0.6928, 0.744, 0.7315) (arm3, arm4, arm6, arm7).
- ORIGINAL_*: the raw tick-99 pattern (arm-6 at 0.7780), the detectability
  W8 just dismantled — kept as the calibration cross-check.

Fresh-continuation scale, equal n per arm: n in {500, 1000, 1500}.
n = 1500/arm = 6000 pair terminals ~ 1.7x the W8 probe's entire budget
(~7116); n = 1000/arm = 4000 ~ W8-scale.

Zero kTAM trajectories, no gate executed, no branch of any frozen map
touched, ladder PAUSED. Synthetic binomial counts only. Stdlib-only,
hosted-CI-safe. Seeds 20261021..20261027, disjoint from census-sim
(20261013/14), the blockpower OC (20261015-19) and every committed
trajectory seed family.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import random
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.w8_census_sim import _BinomialCDF
from tools.w8_dispersion_receipt import exact_two_sided_p as reference_two_sided_p

ARMS = 4
ALPHA = 0.05
REPLICATES = 4000
SEEDS = tuple(range(20261021, 20261028))
N_VALUES = (500, 1000, 1500)
WILSON_Z = 1.959963984540054

# H0 common share: pooled tick-99 census of record (375+106+389+365)/(500+153+500+499)
POOLED_TICK99 = 1235 / 1652
PATTERN_RESIDUAL = (0.7500, 0.6928, 0.744, 0.7315)
PATTERN_ORIGINAL = (0.7500, 0.6928, 0.7780, 0.7315)

_Epsilon = 1e-9


class _LogFactorials:
    """Precomputed log-factorial table; lg[0]=0.0, lg[i]=lg[i-1]+log(i)."""

    def __init__(self, max_n: int) -> None:
        self.lg = [0.0] * (max_n + 2)
        for i in range(1, max_n + 2):
            self.lg[i] = self.lg[i - 1] + math.log(i)


_TABLE = _LogFactorials(2 * max(N_VALUES))


def fast_two_sided_p(k: int, p: float, x_obs: int) -> float:
    """Two-sided exact binomial p (point-probability method) with table lookups.

    Same definition as tools.w8_dispersion_receipt.exact_two_sided_p:
    P(pmf(X) <= pmf(x_obs)), summed over the full support.
    """
    if not (0.0 < p < 1.0):
        return 1.0
    lg = _TABLE.lg
    if x_obs < 0 or x_obs > k:
        return 1.0
    log_p = math.log(p)
    log_1mp = math.log1p(-p)
    lp_obs = lg[k] - lg[x_obs] - lg[k - x_obs] + x_obs * log_p + (k - x_obs) * log_1mp
    total = 0.0
    for y in range(k + 1):
        lp = lg[k] - lg[y] - lg[k - y] + y * log_p + (k - y) * log_1mp
        if lp <= lp_obs + _Epsilon:
            total += math.exp(lp - lp_obs)
    return min(1.0, total * math.exp(lp_obs))


def cross_check_fast_p() -> dict:
    """Assert fast_two_sided_p matches the tick-93 reference implementation,
    and hypergeom_two_sided_p matches pinned known Fisher values."""
    cases = [
        (500, 0.7475, 375), (153, 0.7475, 106), (500, 0.7475, 389),
        (499, 0.7475, 365), (1500, 0.7475782126, 1122), (1000, 0.6928, 693),
        (50, 0.5, 25), (7, 0.9, 6), (12, 0.05, 0),
    ]
    worst = 0.0
    for k, p, x in cases:
        a = fast_two_sided_p(k, p, x)
        b = reference_two_sided_p(k, p, x)
        worst = max(worst, abs(a - b))
    # Residual drift is float summation-order noise (per-term lgamma vs a
    # cumulative log-factorial table), immaterial on probabilities in [0,1].
    if worst > 1e-10:
        raise AssertionError(f"fast/reference p-value drift {worst:.3e} > 1e-10")
    # Known two-sided Fisher values (scipy.stats.fisher_exact, verified in-run
    # 2026-10-21; same point-probability convention as this implementation):
    fisher_cases = [
        (3, 4, 1, 4, 0.4857142857142857),
        (5, 10, 8, 10, 0.34984520123839014),
        (375, 500, 106, 153, 0.1730588496885811),
        (389, 500, 365, 499, 0.09114117334678429),
    ]
    fworst = 0.0
    for x1, n1, x2, n2, want in fisher_cases:
        got = hypergeom_two_sided_p(x1, n1, x2, n2)
        fworst = max(fworst, abs(got - want))
    if fworst > 1e-12:
        raise AssertionError(f"Fisher cross-check drift {fworst:.3e} > 1e-12")
    return {"max_abs_diff": worst, "cases": len(cases),
            "fisher_max_abs_diff": fworst, "fisher_cases": len(fisher_cases)}


def min_p_statistic(counts: list[int], n: int) -> float:
    """Tick-93 receipt statistic: min over arms of the exact two-sided
    binomial p of that arm against the leave-one-out pooled share.

    OC caveat measured this tick: the per-replicate estimated (LOO) null
    breaks marginal exactness, so thresholding this family cannot control
    size by Boole; recorded here precisely to document that inflation."""
    total = sum(counts)
    arms = len(counts)
    best = 1.0
    for i, x in enumerate(counts):
        other_x = total - x
        other_n = arms * n - n
        pool = other_x / other_n if other_n > 0 else 0.0
        pv = fast_two_sided_p(n, pool, x)
        if pv < best:
            best = pv
    return best


def hypergeom_two_sided_p(x1: int, n1: int, x2: int, n2: int) -> float:
    """Two-sided exact Fisher p (point-probability method) for the 2x2 table
    [[x1, n1-x1], [x2, n2-x2]], X1 ~ Hypergeometric(n1+n2, x1+x2, n1).

    Closed-form conditional-exact: both margins fixed, no estimated null.
    Log-space weights from the shared log-factorial table, full-support
    point-probability scan (same convention as the tick-93 binomial
    reference). Validated against scipy.stats.fisher_exact (same
    convention) to <=1.4e-16 on tick-99-scale tables; committed
    cross-check pins those values."""
    pop = n1 + n2
    succ = x1 + x2
    lo = max(0, n1 - (pop - succ))
    hi = min(n1, succ)
    if x1 < lo or x1 > hi:
        return 1.0
    lg = _TABLE.lg

    def pmf_log(k: int) -> float:
        return (lg[succ] - lg[k] - lg[succ - k]
                + lg[pop - succ] - lg[n1 - k] - lg[pop - succ - n1 + k])

    lp_obs = pmf_log(x1)
    eps = 1e-9
    log_total = -math.inf
    log_tail = -math.inf
    for k in range(lo, hi + 1):
        lp = pmf_log(k)
        log_total = _log_add(log_total, lp)
        if lp <= lp_obs + eps:
            log_tail = _log_add(log_tail, lp)
    return min(1.0, math.exp(log_tail - log_total))


def _log_add(a: float, b: float) -> float:
    if a == -math.inf:
        return b
    if b == -math.inf:
        return a
    if b > a:
        a, b = b, a
    return a + math.log1p(math.exp(b - a))


def min_pairwise_fisher_p(counts: list[int], n: int) -> float:
    """Size-controlled omnibus candidate: min over the 6 pairwise exact
    two-sided Fisher p-values (equal n per arm). Reject iff <= alpha/6
    (Bonferroni; each marginal test is conditional-exact, so Boole bounds
    the union at <= 0.05 under any dependence structure)."""
    arms = len(counts)
    best = 1.0
    for i in range(arms):
        for j in range(i + 1, arms):
            pv = hypergeom_two_sided_p(counts[i], n, counts[j], n)
            if pv < best:
                best = pv
    return best


def wilson(successes: int, trials: int) -> tuple[float, float]:
    phat = successes / trials
    denom = 1 + WILSON_Z * WILSON_Z / trials
    centre = (phat + WILSON_Z * WILSON_Z / (2 * trials)) / denom
    half = (WILSON_Z / denom) * math.sqrt(
        phat * (1 - phat) / trials + WILSON_Z * WILSON_Z / (4 * trials * trials))
    return centre - half, centre + half


def run_config(label: str, shares: tuple[float, ...], n: int) -> dict:
    samplers = [_BinomialCDF(n, p) for p in shares]
    rej_loo_nom = rej_loo_bonf = rej_pw_bonf = 0
    for seed in SEEDS:
        rng = random.Random(seed)
        per_seed = REPLICATES // len(SEEDS)
        for _ in range(per_seed):
            counts = [s.draw(rng) for s in samplers]
            m_loo = min_p_statistic(counts, n)
            if m_loo <= ALPHA:
                rej_loo_nom += 1
            if m_loo <= ALPHA / ARMS:
                rej_loo_bonf += 1
            if min_pairwise_fisher_p(counts, n) <= ALPHA / 6:
                rej_pw_bonf += 1
    out = {
        "label": label,
        "n_per_arm": n,
        "pair_terminals": ARMS * n,
        "shares": list(shares),
        "alpha": ALPHA,
        "replicates": REPLICATES,
        "seeds": list(SEEDS),
    }
    for key, rej, thr in (
        ("loo_min_binom_nominal", rej_loo_nom, ALPHA),
        ("loo_min_binom_bonferroni", rej_loo_bonf, ALPHA / ARMS),
        ("pairwise_min_fisher_bonferroni", rej_pw_bonf, ALPHA / 6),
    ):
        low, high = wilson(rej, REPLICATES)
        out[key] = {
            "threshold": thr,
            "rejections": rej,
            "estimate": rej / REPLICATES,
            "wilson95_low": low,
            "wilson95_high": high,
        }
    return out


def run() -> list[dict]:
    results = []
    for n in N_VALUES:
        results.append(run_config(f"SIZE_{n}", (POOLED_TICK99,) * ARMS, n))
    for n in N_VALUES:
        results.append(run_config(f"RESIDUAL_{n}", PATTERN_RESIDUAL, n))
    for n in N_VALUES:
        results.append(run_config(f"ORIGINAL_{n}", PATTERN_ORIGINAL, n))
    return results


def write_receipt(out_dir: str | None = None) -> dict:
    cross = cross_check_fast_p()
    configs = run()
    receipt = {
        "schema": "w9-homogeneity-oc-v1",
        "generated_for": "SON-5152 tick 147 pre-datum OC measurement",
        "instrument": ("tick-93 dispersion receipt rule: min over 4 arms of the "
                       "exact two-sided binomial p against the leave-one-out pool; "
                       "reject iff min p <= 0.05 (no multiplicity correction)"),
        "alpha": ALPHA,
        "replicates": REPLICATES,
        "seeds": list(SEEDS),
        "n_values": list(N_VALUES),
        "pooled_tick99_share": POOLED_TICK99,
        "pattern_residual": list(PATTERN_RESIDUAL),
        "pattern_original": list(PATTERN_ORIGINAL),
        "cross_check_vs_tick93_reference": cross,
        "configs": configs,
    }
    path = Path(out_dir or os.path.join(
        ROOT, "evidence", "2026-10-21-w9-homogeneity-oc")) / "oc.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    path.write_text(payload, encoding="utf-8")
    receipt["receipt_path"] = str(path.relative_to(ROOT))
    receipt["receipt_sha256"] = hashlib.sha256(
        payload.encode("utf-8")).hexdigest()
    return receipt


def main(argv=None) -> int:
    receipt = write_receipt()
    print(f"receipt {receipt['receipt_path']} sha256 {receipt['receipt_sha256']}")
    for c in receipt["configs"]:
        for key in ("loo_min_binom_nominal", "loo_min_binom_bonferroni",
                    "pairwise_min_fisher_bonferroni"):
            e = c[key]
            print(f"{c['label']:>14} {key:<30} {e['rejections']:>4}/"
                  f"{c['replicates']} = {e['estimate']:.5f} "
                  f"[{e['wilson95_low']:.5f}, {e['wilson95_high']:.5f}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
