"""Pre-datum operating characteristics of the FROZEN Fisher-exact
one-sided arbitration test (w8 blockpower, tick 139, SON-5152).

The tick-120 pre-registration
(``research-log/2026-10-13-w8-blockpower-prereg.md``) states the power of
the pooled one-sided Fisher test by NORMAL APPROXIMATION at anchor
p_bar = 0.745, n = 3560/group: power 0.896 at delta 0.030, 0.979 at
0.038 (tick-101 realized contrast), 0.696 at 0.0223 (hotrepro realized).
The instrument that will actually adjudicate SUPPORTED vs NOT_DETECTED
is the EXACT conditional test, whose realized size is below nominal by
construction. This module measures, by fixed-seed Monte Carlo over
SYNTHETIC binomial counts, what the exact instrument actually delivers
at the frozen margins — BEFORE the datum lands.

Measured (then frozen in tests): the realized size under H0 and the MC
power at the three pre-registered effect sizes, under BOTH anchoring
readings of the prereg text (baseline anchoring: GAP = anchor + delta,
A6 = anchor; midpoint anchoring: GAP = anchor + delta/2, A6 =
anchor - delta/2 — the prereg's SE formula uses the H0-variance form,
which does not disambiguate; both are reported, neither is chosen).

This module runs ZERO kTAM trajectories and consumes none of the
probe's virgin seed windows (synthetic draws only, RNG seeds 20261015+
distinct from every committed trajectory seed). No gate is executed;
the ladder stays PAUSED; no branch of the frozen map is touched.
Determinism: stdlib Mersenne Twister with fixed per-scenario seeds and
the cached log-CDF binomial sampler imported from ``w8_census_sim``
(tick 123, stdlib-only because the hosted unittest workflow installs
nothing); every number in the receipt is byte-reproducible.
"""

from __future__ import annotations

import json
import math
import random

try:  # package import (tests) and script import both supported
    from .w8_census_sim import _BinomialCDF
    from .w8_stratified_census import wilson95
except ImportError:  # pragma: no cover - script execution path
    from w8_census_sim import _BinomialCDF
    from w8_stratified_census import wilson95

N_PER_GROUP = 3560          # frozen design, prereg "Design (frozen)"
REPLICATES = 4000
ALPHA = 0.05
ANCHOR = 0.745              # prereg "Power (stated BEFORE submission)" p_bar
# Normal-approximation power claims from the prereg, for side-by-side:
NORMAL_APPROX_POWER = {
    "delta_0.030": 0.896,
    "delta_0.038": 0.979,
    "delta_0.0223": 0.696,
}
DELTA_030 = 0.030
DELTA_038 = 0.038
DELTA_0223 = 0.0223

# Scenario table: name -> (p_gap, p_a6, seed). Baseline reading puts the
# prereg anchor on A6 and elevates GAP by delta (H1: share(GAP) >
# share(A6)); midpoint reading splits delta around the anchor. Seeds
# 20261015..20261019 are disjoint from census-sim (20261013/20261014)
# and from every trajectory seed family in committed evidence.
SCENARIOS: dict[str, tuple[float, float, int]] = {
    "H0_SIZE": (ANCHOR, ANCHOR, 20261015),
    "D030_BASELINE": (ANCHOR + DELTA_030, ANCHOR, 20261016),
    "D030_MIDPOINT": (ANCHOR + DELTA_030 / 2.0, ANCHOR - DELTA_030 / 2.0, 20261017),
    "D038_BASELINE": (ANCHOR + DELTA_038, ANCHOR, 20261018),
    "D0223_BASELINE": (ANCHOR + DELTA_0223, ANCHOR, 20261019),
}


def fisher_one_sided_greater(x: int, n1: int, y: int, n2: int) -> float:
    """One-sided Fisher exact p-value for H1: p1 > p2.

    Convention (scipy ``fisher_exact(alternative='greater')`` for the
    table [[x, n1-x], [y, n2-y]]): p = P[X >= x] with X ~
    Hypergeometric(N = n1+n2, K = x+y successes, n1 draws). The tail is
    summed upward from x by the exact term ratio (log-factorial start,
    multiplicative walk) — no 1-x complements anywhere.
    """
    if n1 <= 0 or n2 <= 0:
        raise ValueError("need n1 >= 1 and n2 >= 1")
    if not (0 <= x <= n1 and 0 <= y <= n2):
        raise ValueError("counts out of range")
    big_k = x + y
    total_n = n1 + n2
    if big_k == 0:
        return 1.0  # P[X >= 0] with no successes anywhere
    kmax = min(n1, big_k)
    # log P(X=x) = lnC(n1,x) + lnC(n2,K-x) - lnC(N,K)
    logt = (
        _lchoose(n1, x) + _lchoose(n2, big_k - x) - _lchoose(total_n, big_k)
    )
    term = math.exp(logt)
    tail = term
    k = x
    while k < kmax:
        # P(k+1)/P(k) = (n1-k)(K-k) / ((k+1)(n2-K+k+1)), exact integers
        num = (n1 - k) * (big_k - k)
        den = (k + 1) * (n2 - big_k + k + 1)
        if num <= 0 or den <= 0:
            break  # left the support (K-k == 0 or n2 support exhausted)
        term *= num / den
        tail += term
        k += 1
    return min(1.0, tail)


_LF_CACHE: dict[int, list[float]] = {}


def _lchoose(n: int, k: int) -> float:
    """ln C(n,k) from a cached log-factorial table (census-sim pattern)."""
    if k < 0 or k > n:
        raise ValueError("k out of range")
    cached = _LF_CACHE.get(n)
    if cached is None:
        table = [0.0]
        for j in range(1, n + 1):
            table.append(table[-1] + math.log(j))
        _LF_CACHE[n] = table
        cached = table
    return cached[n] - cached[k] - cached[n - k]


def run_scenario(p_gap: float, p_a6: float, n: int, replicates: int,
                 seed: int) -> dict:
    """Fixed-seed MC rejection rate of the frozen exact test."""
    if not isinstance(seed, int) or isinstance(seed, bool) or seed < 0:
        raise ValueError("seed must be a non-negative integer")
    if (not isinstance(replicates, int) or isinstance(replicates, bool)
            or replicates <= 0):
        raise ValueError("replicates must be a positive integer")
    rng = random.Random(seed)
    gap = _BinomialCDF(n, p_gap)
    a6 = _BinomialCDF(n, p_a6)
    rejections = 0
    for _ in range(replicates):
        x = gap.draw(rng)
        y = a6.draw(rng)
        if fisher_one_sided_greater(x, n, y, n) <= ALPHA:
            rejections += 1
    rate = rejections / replicates
    lo, hi = wilson95(rejections, replicates)
    return {
        "rejections": rejections,
        "replicates": replicates,
        "rate": rate,
        "wilson95_lo": lo,
        "wilson95_hi": hi,
    }


def build_receipt() -> dict:
    results = {}
    for name, (p_gap, p_a6, seed) in SCENARIOS.items():
        res = run_scenario(p_gap, p_a6, N_PER_GROUP, REPLICATES, seed)
        results[name] = {
            "p_gap": p_gap,
            "p_a6": p_a6,
            "seed": seed,
            "rejections": res["rejections"],
            "replicates": res["replicates"],
            "reject_rate": res["rate"],
            "reject_rate_wilson95": [res["wilson95_lo"], res["wilson95_hi"]],
        }
    return {
        "analysis": "blockpower-frozen-fisher-exact-one-sided-oc",
        "instrument": ("pooled Fisher exact one-sided, H1 share(GAP) > "
                       "share(A6), alpha 0.05 (tick-120 prereg PRIMARY)"),
        "n_per_group": N_PER_GROUP,
        "replicates": REPLICATES,
        "alpha": ALPHA,
        "anchor_pbar": ANCHOR,
        "anchor_note": ("prereg power-section p_bar = 0.745; the SE formula "
                        "is H0-variance and does not fix where delta sits — "
                        "both baseline and midpoint anchorings measured"),
        "normal_approx_power_prereg": NORMAL_APPROX_POWER,
        "results": results,
        "limits": [
            "Monte Carlo over synthetic binomial counts; Wilson intervals "
            "quantify simulation error only",
            "no kTAM trajectories; none of the probe's virgin seed windows "
            "consumed; no gate executed; ladder stays PAUSED",
            "pre-datum: measured before request dd5a8300 is adjudicated; "
            "no branch of the frozen map is touched or re-derived",
            "not a physical-replicate or exact-confidence claim",
        ],
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--out", default="evidence/2026-10-14-w8-blockpower-oc/oc.json")
    args = parser.parse_args()
    receipt = build_receipt()
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(json.dumps(receipt["results"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
