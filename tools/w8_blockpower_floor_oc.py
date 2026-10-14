"""Pre-datum operating characteristics of the NO_EVENTS floor branch
(w8 blockpower frozen map, tick 140, SON-5152).

Tick 139 measured the Fisher test the frozen map uses at the design
n = 3560/group. But the map (``branch_map`` in
``evidence/2026-10-13-w8-blockpower/ktam_w8_blockpower.py``) fires
``NO_EVENTS`` BEFORE any p-value is read, whenever EITHER group's pooled
terminal pair census drops below MIN_EVENTS = 3400
(``if ng < MIN_EVENTS or na < MIN_EVENTS``). Each group attempts
n = 3560 seeds and a seed lands in the pair census unless its terminal
reading is 'other', so pair_n ~ Binomial(3560, q) with q the per-seed
terminal-pair yield. The prereg's stated basis is empirical: terminal
'other' <= 0.5% in every committed w8 window, i.e. q >= 0.995 and
expected pair-n >= ~3542, "floor 3400 carries ~4.5% headroom".

Nobody has measured WHEN that branch can actually fire. This module
closes the map-level gap the pre-datum way, before the queued request
(dd5a8300..., still behind the board-operator maintenance lease) can
produce a datum:

1. Exact per-group risk curve P(Bin(3560, q) < 3400) over a yield grid,
   each point summed on its DEFINING side (k = 0..3399) by a float
   log-factorial-start downward ratio walk with a recorded negligible-
   term cutoff (no 1-x complements, no underflow); anchored against
   exact-rational Decimal ground truth at prec 80 (integer-power start,
   small-integer ratio steps) at four q anchors — agreement pinned
   <= 1e-11 relative (the float walk's lnC start cancels ~2.8e4-magnitude
   log-factorials, so it is ulp-limited near 4e-12; tick-136's bounded
   oracle-noise pattern; the Decimal side carries the certified digits).
2. Two-group map risk in the cancellation-safe form 2r - r^2 (writing
   1 - (1-r)^2 would destroy every significant digit at the historical
   yield, where r ~ 1e-30).
3. Inversion: the yields q05 / q50 at which per-group NO_EVENTS risk
   reaches 5% / 50% (bisection on the same float walk), reported
   against the historical q >= 0.995 — i.e. how much terminal-yield
   collapse the floor tolerates before the arbitration defuses itself.
4. Floor-edge power: at pair_n = 3400/group EXACTLY (the worst census
   the map still adjudicates), the tick-139 exact Fisher instrument's
   realized size and MC power at the pre-registered delta 0.030
   (baseline anchoring), reusing ``w8_blockpower_oc.run_scenario``
   unchanged — RNG seeds 20261020/20261021, disjoint from census-sim
   (20261013/14), from the tick-139 OC seeds (20261015-19) and from
   every committed trajectory seed family.

ZERO kTAM trajectories; none of the probe's virgin seed windows
consumed; no gate executed; the ladder stays PAUSED; no branch of the
frozen map is touched or re-derived. Every number in the receipt is
byte-reproducible (stdlib only; hosted-CI-safe).
"""

from __future__ import annotations

import json
import math
from decimal import Decimal, getcontext

try:  # package import (tests) and script import both supported
    from .w8_blockpower_oc import ANCHOR, ALPHA, DELTA_030, run_scenario
except ImportError:  # pragma: no cover - script execution path
    from w8_blockpower_oc import ANCHOR, ALPHA, DELTA_030, run_scenario

N_PER_GROUP = 3560          # frozen design (2 x 1780-seed windows/group)
MIN_EVENTS = 3400           # frozen floor, per pooled group
REPLICATES = 4000           # floor-edge MC, same replicate count as tick 139
FLOOR_EDGE_N = 3400         # worst census the map still adjudicates
Q_HIST = 0.995              # prereg empirical floor on terminal-pair yield
# Grid: yields bracketing the floor's tolerance, historical yield included.
Q_GRID = [round(0.90 + 0.005 * i, 4) for i in range(20)]  # 0.900..0.995
# Decimal exact-rational anchors (numer, denom) for the two-method guard.
Q_ANCHORS = [(199, 200), (49, 50), (24, 25), (19, 20)]  # .995 .98 .96 .95
DECIMAL_PREC = 80
CUTOFF_REL = 1e-25          # float walk stops when term < CUTOFF_REL * acc
AGREE_BAR = 1e-11           # float-vs-Decimal relative agreement bar: the
# float walk's log-factorial start is ulp-limited near 4e-12 by
# cancellation of ~2.8e4-magnitude logs (measured 3.6e-12 at q=0.995);
# the prec-80 Decimal side carries the certified digits.

# Floor-edge MC scenarios (tick-139 baseline anchoring, n = 3400).
SCENARIOS = {
    "FLOOR_EDGE_H0_SIZE": (ANCHOR, ANCHOR, 20261020),
    "FLOOR_EDGE_D030_POWER": (ANCHOR + DELTA_030, ANCHOR, 20261021),
}

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


def risk_below_float(n: int, kmax: int, q: float) -> tuple[float, int]:
    """P(X <= kmax - 1), X ~ Bin(n, q), summed on its defining side.

    Starts from the pmf at kmax-1 (log-factorial start) and walks DOWN
    by the exact integer ratio P(k-1)/P(k) = k*(1-q) / ((n-k+1)*q),
    stopping when terms are negligible relative to the accumulated sum
    (cutoff index returned — the omitted left tail is beyond 1e-25 of
    the total). No 1-x complements; no underflow (the walk never
    multiplies by an unrepresentable intermediate).
    """
    if not (0.0 < q < 1.0):
        raise ValueError("q must be in (0, 1)")
    if kmax < 1 or kmax > n + 1:
        raise ValueError("kmax out of range")
    k = kmax - 1
    term = math.exp(_lchoose(n, k) + k * math.log(q)
                    + (n - k) * math.log1p(-q))
    acc = term
    k_stop = k
    while k > 0:
        # P(k-1)/P(k) = k*(1-q) / ((n-k+1)*q)  — exact float ratio
        ratio = (k * (1.0 - q)) / ((n - k + 1) * q)
        term *= ratio
        if term < CUTOFF_REL * acc and k < kmax - 1:
            k_stop = k  # this and every smaller term is negligible
            break
        acc += term
        k -= 1
        k_stop = k + 1
    return acc, k_stop


def risk_below_decimal(n: int, kmax: int, numer: int, denom: int) -> Decimal:
    """Exact-rational ground truth for P(X <= kmax - 1) at prec 80.

    q = numer/denom as an exact rational: t_0 = ((denom-numer)^n /
    denom^n) by integer powers then one high-precision division; the
    walk up from k=0 uses only small-integer ratios
    t_{k+1} = t_k * (n-k)*numer / ((k+1)*(denom-numer)).  Terms are
    never dropped (Decimal exponent range dwarfs 1e-3000), so this is
    the full defining-side sum with arithmetic error <= ~1e-76.
    """
    getcontext().prec = DECIMAL_PREC
    other = denom - numer
    t = Decimal(other ** n) / Decimal(denom ** n)
    acc = t
    for k in range(0, kmax - 1):
        t = (t * Decimal((n - k) * numer)
             / Decimal((k + 1) * other))
        acc += t
    return acc


def map_risk_two_groups(r: float) -> float:
    """P(group A OR group B below floor) in the cancellation-safe form.

    Independent groups: 1 - (1-r)^2 == 2r - r^2 exactly; the latter
    form is required because at the historical yield r ~ 1e-30 and
    1 - (1-r)^2 evaluates to exactly 0.0 in float.
    """
    return 2.0 * r - r * r


def invert_risk(n: int, kmax: int, target: float,
                lo: float = 0.90, hi: float = 0.9995) -> float:
    """Yield q at which P(Bin(n, q) <= kmax-1) == target (bisection).

    Monotone decreasing in q; default brackets [0.90, 0.9995] suit
    the receipt regime (n = 3560, kmax = 3400); other regimes pass
    their own. 200 iterations of bisection pin q far below the float
    walk's own precision, so the returned digits are limited by the
    walk, not the bisection (recorded honestly as such).
    """
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if risk_below_float(n, kmax, mid)[0] > target:
            lo = mid  # risk still too high -> yield must rise
        else:
            hi = mid
    return 0.5 * (lo + hi)


def build_receipt() -> dict:
    curve = []
    for q in Q_GRID:
        r, k_stop = risk_below_float(N_PER_GROUP, MIN_EVENTS, q)
        curve.append({
            "q_yield": q,
            "other_rate": round(1.0 - q, 6),
            "per_group_risk": r,
            "map_risk_two_groups": map_risk_two_groups(r),
            "float_walk_k_stop": k_stop,
        })
    anchors = []
    for numer, denom in Q_ANCHORS:
        q = numer / denom
        r_f, k_stop = risk_below_float(N_PER_GROUP, MIN_EVENTS, q)
        r_d = risk_below_decimal(N_PER_GROUP, MIN_EVENTS, numer, denom)
        rel = abs(r_f - float(r_d)) / float(r_d)
        anchors.append({
            "q_exact": f"{numer}/{denom}",
            "q_float": q,
            "float_risk": r_f,
            "decimal_risk_prec80": str(r_d),
            "rel_diff": rel,
            "float_walk_k_stop": k_stop,
        })
    scenarios = {}
    for name, (p_gap, p_a6, seed) in SCENARIOS.items():
        res = run_scenario(p_gap, p_a6, FLOOR_EDGE_N, REPLICATES, seed)
        scenarios[name] = {
            "p_gap": p_gap, "p_a6": p_a6, "seed": seed,
            "rejections": res["rejections"],
            "replicates": res["replicates"],
            "reject_rate": res["rate"],
            "reject_rate_wilson95": [
                res["wilson95_lo"], res["wilson95_hi"]],
        }
    q05 = invert_risk(N_PER_GROUP, MIN_EVENTS, 0.05)
    q50 = invert_risk(N_PER_GROUP, MIN_EVENTS, 0.50)
    return {
        "analysis": "blockpower-noevents-floor-oc",
        "map_rule": ("NO_EVENTS iff ng < 3400 OR na < 3400 "
                     "(branch_map, evidence/2026-10-13-w8-blockpower/"
                     "ktam_w8_blockpower.py)"),
        "n_per_group": N_PER_GROUP,
        "min_events": MIN_EVENTS,
        "q_hist_floor": Q_HIST,
        "q_hist_note": ("prereg: terminal 'other' <= 0.5% in every "
                        "committed w8 window -> q >= 0.995, expected "
                        "pair-n >= ~3542"),
        "yield_curve": curve,
        "two_method_anchors": anchors,
        "agreement_bar": AGREE_BAR,
        "inversions": {
            "q_at_5pct_risk": q05,
            "q_at_50pct_risk": q50,
            "other_rate_at_5pct": 1.0 - q05,
            "other_rate_at_50pct": 1.0 - q50,
            "other_rate_hist": 1.0 - Q_HIST,
            "other_rate_multiple_at_5pct": (1.0 - q05) / (1.0 - Q_HIST),
        },
        "floor_edge_mc": scenarios,
        "limits": [
            "defining-side sums only; float walk drops terms below 1e-25 "
            "of the accumulated total (cutoff index recorded per point)",
            "Decimal ground truth at prec 80, exact-rational q, full "
            "defining-side sum, arithmetic error <= ~1e-76 relative",
            "floor-edge MC over synthetic binomial counts at pair_n = 3400 "
            "exactly; Wilson intervals quantify simulation error only",
            "no kTAM trajectories; none of the probe's virgin seed windows "
            "consumed; no gate executed; ladder stays PAUSED",
            "pre-datum: measured while request dd5a8300 is still queued; "
            "no branch of the frozen map is touched or re-derived",
        ],
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--out",
        default="evidence/2026-10-14-w8-blockpower-floor-oc/floor-oc.json")
    args = parser.parse_args()
    receipt = build_receipt()
    for a in receipt["two_method_anchors"]:
        if a["rel_diff"] > AGREE_BAR:
            raise SystemExit(f"two-method guard failed at {a['q_exact']}: "
                             f"{a['rel_diff']:.3e} > {AGREE_BAR:.0e}")
    import os
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(receipt, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps({
        "written": args.out,
        "q_at_5pct_risk": receipt["inversions"]["q_at_5pct_risk"],
        "q_at_50pct_risk": receipt["inversions"]["q_at_50pct_risk"],
        "risk_at_q_hist":
            next(c["map_risk_two_groups"] for c in receipt["yield_curve"]
                 if c["q_yield"] == Q_HIST),
        "max_anchor_rel_diff":
            max(a["rel_diff"] for a in receipt["two_method_anchors"]),
        "floor_edge_size":
            scenarios_view(receipt)["FLOOR_EDGE_H0_SIZE"]["reject_rate"],
        "floor_edge_power_d030":
            scenarios_view(receipt)["FLOOR_EDGE_D030_POWER"]["reject_rate"],
    }, indent=1))


def scenarios_view(receipt: dict) -> dict:
    return receipt["floor_edge_mc"]


if __name__ == "__main__":
    main()
