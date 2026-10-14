"""Pre-datum operating characteristics of the CAL exact-match VOID gate
(w8 blockpower frozen map, tick 141, SON-5152).

The frozen tick-120 map
(``research-log/2026-10-13-w8-blockpower-prereg.md``, ``branch_map`` in
``evidence/2026-10-13-w8-blockpower/ktam_w8_blockpower.py``) reads:

    CAL_FAIL -> VOID;  min pair-n < 3400 -> NO_EVENTS;
    p <= 0.05 -> SUPPORTED;  p > 0.05 -> NOT_DETECTED

Ticks 139/140 measured the Fisher branch pair and the NO_EVENTS floor
branch pre-datum. The FIRST branch — the CAL identity gate, which fires
BEFORE the floor and before any p-value — had never been measured: the
queued instrument replays the 500-seed CAL window (``260261107+[0,500)``)
and demands the mid-window pair census come back EXACTLY D2T 367 : L2 131
(so, implicitly, other = 2), else VOID. This module measures, before the
queued request (dd5a8300..., still behind the board-operator maintenance
lease) can produce a datum, what that exact-match gate is worth as an
anomaly detector, and what corruption level silently passes the WHOLE
gate set and reaches adjudication.

Anomaly model (stated before any arithmetic): each seed's terminal
reading is independently perturbed with probability eps. Two kernels
bracket destructive vs benign corruption:

- DROPOUT (a perturbed seed reads 'other'): the gate passes iff none of
  the 498 committed pair-seeds is perturbed — ``P_pass = (1-eps)^498``.
- MARGINAL RESHUFFLE (a perturbed seed re-draws iid from the committed
  census marginal m = (367/500, 131/500, 2/500)): lucky compensation is
  allowed; ``P_pass`` is the exact K-conditioned convolution
  sum_{kD,kL,kO} C(367,kD) C(131,kL) C(2,kO) eps^K (1-eps)^{500-K}
  x Mult(K; kD,kL,kO | m)  (all-positive lgamma float evaluation).

Verifications pinned in the receipt: the reshuffle sum at eps = 1
collapses to the iid multinomial pmf at m, checked against an exact
Fraction one-term ground truth; the first-order coefficient
d/d eps [1 - P_pass] at eps -> 0 is 98146/500 = 196.292 exactly (hand
derivation: 500 - sum_s m_{s,s}, sum m_{s,s} = (367^2+131^2+2^2)/500),
checked numerically at eps = 1e-6; dropout anchors vs exact Fraction
powers; and a mid-range exact anchor at eps = 1/1024 where the exact
Fraction sum truncated at K <= 10 carries a recorded Chernoff tail bound
(e*mu/k)^k with mu = 500/1024, so the comparison bar is honest.

Joint map-level quantity (dropout kernel throughout, so CAL and the
arbitration census sit on the SAME per-seed corruption scale): with
per-seed dropout eps hitting the CAL replay and both 3560-seed groups
independently, P(corrupted run reaches adjudication) =
(1-eps)^498 * (1 - 2r + r^2) with r = P(Bin(3560, 1-eps) < 3400) taken
from the tick-140 float walk unchanged (imported, never re-implemented).
The verdict-safety statement this supports: the largest corruption that
still escapes the CAL gate with 95% probability displaces each group's
expected pair census by 3560*eps05 ~ 0.4 seeds — under 0.5% of the
smallest pre-registered effect (delta 0.0223 = 79.4 seeds) — while
corruption large enough to matter verdict-wise trips the CAL near-
certainly ((1-0.0396)^498 ~ 2e-9 at the tick-140 collapse yield).

ZERO kTAM trajectories; none of the probe's virgin seed windows
consumed; no gate executed; the ladder stays PAUSED; no branch of the
frozen map is touched or re-derived. No RNG anywhere (closed forms,
exact sums, bisection only) — byte-reproducible, stdlib-only,
hosted-CI-safe.
"""

from __future__ import annotations

import json
import math
import os
from fractions import Fraction

try:  # package import (tests) and script import both supported
    from .w8_blockpower_floor_oc import (
        MIN_EVENTS,
        N_PER_GROUP,
        map_risk_two_groups,
        risk_below_float,
    )
except ImportError:  # pragma: no cover - script execution path
    from w8_blockpower_floor_oc import (  # type: ignore
        MIN_EVENTS,
        N_PER_GROUP,
        map_risk_two_groups,
        risk_below_float,
    )

# Frozen CAL gate references (tick-120 prereg "Design (frozen)" + the
# queued instrument's imported constants — never re-derived here).
CAL_N = 500
CAL_D2T = 367
CAL_L2 = 131
CAL_OTHER = 2

# smallest pre-registered effect sizes (prereg "Power"), seed units
DELTAS = {"d0223_hotrepro": 0.0223, "d030_mde": 0.030}

EPS_GRID = [1e-7, 1e-6, 1e-5, 1e-4, 5e-4, 1e-3, 5e-3, 1e-2, 5e-2]
SILENT_PASS_GRID = [1e-5, 1e-4, 1e-3, 5e-3, 1e-2, 3.96037e-2, 5e-2]
ANCHOR_RESHUFFLE_MID = Fraction(1, 1024)      # exact-rational mid anchor
MID_TRUNC_K = 10                              # K <= 10 exact sum anchor
VERIF_EPS_FIRST_ORDER = 1e-7                  # second-order bias ~1e-6 rel

_LF: list[float] = [0.0]
for _j in range(1, CAL_N + 1):
    _LF.append(_LF[-1] + math.log(_j))


def _logfact(k: int) -> float:
    return _LF[k]


def p_pass_dropout(eps: float) -> float:
    """DROPOUT kernel: gate passes iff all 498 pair seeds unperturbed."""
    if not (0.0 <= eps <= 1.0):
        raise ValueError("eps out of range")
    return math.exp((CAL_N - CAL_OTHER) * math.log1p(-eps))


def _log_multinomial_pmf(kd: int, kl: int, ko: int,
                         pd: float, pl: float, po: float) -> float:
    k = kd + kl + ko
    return (_logfact(k) - _logfact(kd) - _logfact(kl) - _logfact(ko)
            + kd * math.log(pd) + kl * math.log(pl) + ko * math.log(po))


def p_pass_reshuffle(eps: float) -> float:
    """MARGINAL RESHUFFLE kernel: exact K-conditioned convolution.

    Perturbation chooses a subset of seeds (kD of 367 D2T, kL of 131
    L2, kO of 2 other) then redraws all K iid from the committed
    marginal; the census still matches iff the redraw lands exactly on
    (kD, kL, kO). All-positive lgamma evaluation; eps = 1 collapses to
    the single-term iid pmf (handled without log(0)).
    """
    if not (0.0 <= eps <= 1.0):
        raise ValueError("eps out of range")
    pd = CAL_D2T / CAL_N
    pl = CAL_L2 / CAL_N
    po = CAL_OTHER / CAL_N
    if eps == 1.0:
        return math.exp(_log_multinomial_pmf(
            CAL_D2T, CAL_L2, CAL_OTHER, pd, pl, po))
    if eps == 0.0:
        return 1.0
    log_eps = math.log(eps)
    log_one_minus = math.log1p(-eps)
    acc = 0.0
    for kd in range(CAL_D2T + 1):
        log_cd = _logfact(CAL_D2T) - _logfact(kd) - _logfact(CAL_D2T - kd)
        for kl in range(CAL_L2 + 1):
            log_cl = _logfact(CAL_L2) - _logfact(kl) - _logfact(CAL_L2 - kl)
            for ko in range(CAL_OTHER + 1):
                k = kd + kl + ko
                log_co = (_logfact(CAL_OTHER) - _logfact(ko)
                          - _logfact(CAL_OTHER - ko))
                acc += math.exp(
                    log_cd + log_cl + log_co
                    + k * log_eps + (CAL_N - k) * log_one_minus
                    + _log_multinomial_pmf(kd, kl, ko, pd, pl, po))
    return acc


def p_pass_reshuffle_mid_anchor_exact() -> tuple[Fraction, Fraction]:
    """Exact-rational truncated ground truth at eps = 1/1024.

    Returns (exact_partial_sum, chernoff_tail_bound) with the sum over
    all (kD, kL, kO), K = kD+kL+kO <= 10, evaluated in Fraction, and
    the bound P(K >= 11) <= (e*mu/11)^11, mu = 500/1024, on everything
    the truncation drops.
    """
    eps = ANCHOR_RESHUFFLE_MID
    pd = Fraction(CAL_D2T, CAL_N)
    pl = Fraction(CAL_L2, CAL_N)
    po = Fraction(CAL_OTHER, CAL_N)

    def fact(n: int) -> int:
        out = 1
        for j in range(2, n + 1):
            out *= j
        return out

    F = {k: fact(k) for k in range(0, CAL_N + 1) if k <= CAL_N}

    def choose(n: int, k: int) -> Fraction:
        return Fraction(F[n], F[k] * F[n - k])

    acc = Fraction(0)
    for kd in range(CAL_D2T + 1):
        for kl in range(CAL_L2 + 1):
            for ko in range(CAL_OTHER + 1):
                if kd + kl + ko > MID_TRUNC_K:
                    continue
                k = kd + kl + ko
                w = (choose(CAL_D2T, kd) * choose(CAL_L2, kl)
                     * choose(CAL_OTHER, ko)
                     * eps ** k * (1 - eps) ** (CAL_N - k))
                mult = (Fraction(F[k], F[kd] * F[kl] * F[ko])
                        * pd ** kd * pl ** kl * po ** ko)
                acc += w * mult
    mu = Fraction(CAL_N) * eps
    kbar = MID_TRUNC_K + 1
    tail = Fraction(math.e * float(mu) / kbar) ** kbar
    return acc, Fraction(tail).limit_denominator(10 ** 12)


def invert_p_pass(func, target: float, lo: float = 0.0,
                  hi: float = 1.0) -> float:
    """eps at which P_pass == target (bisection; P_pass monotone down)."""
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if func(mid) > target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def build_receipt() -> dict:
    # --- kernel curves over the eps grid -----------------------------
    drop_curve = {f"{e:g}": p_pass_dropout(e) for e in EPS_GRID}
    resh_curve = {f"{e:g}": p_pass_reshuffle(e) for e in EPS_GRID}

    # --- inversions: corruption the CAL gate tolerates ----------------
    drop_eps05_analytic = 1.0 - 0.95 ** (1.0 / (CAL_N - CAL_OTHER))
    drop_eps50_analytic = 1.0 - 0.50 ** (1.0 / (CAL_N - CAL_OTHER))
    drop_eps05 = invert_p_pass(p_pass_dropout, 0.95)
    drop_eps50 = invert_p_pass(p_pass_dropout, 0.50)
    resh_eps05 = invert_p_pass(p_pass_reshuffle, 0.95)
    resh_eps50 = invert_p_pass(p_pass_reshuffle, 0.50)

    # --- verification block ------------------------------------------
    # eps = 1 anchor: reshuffle collapses to the iid pmf at m
    pmf_float = p_pass_reshuffle(1.0)
    fr = Fraction
    pmf_exact = (fr(math.factorial(CAL_N),
                    math.factorial(CAL_D2T) * math.factorial(CAL_L2)
                    * math.factorial(CAL_OTHER))
                 * fr(CAL_D2T, CAL_N) ** CAL_D2T
                 * fr(CAL_L2, CAL_N) ** CAL_L2
                 * fr(CAL_OTHER, CAL_N) ** CAL_OTHER)
    pmf_exact_float = float(pmf_exact)

    # first-order coefficient: d/deps [1 - P_pass(0)] == 98146/500
    first_order_exact = Fraction(
        CAL_N * CAL_N - (CAL_D2T ** 2 + CAL_L2 ** 2 + CAL_OTHER ** 2),
        CAL_N)
    first_order_numeric = (1.0 - p_pass_reshuffle(
        VERIF_EPS_FIRST_ORDER)) / VERIF_EPS_FIRST_ORDER
    first_order_numeric_drop = (1.0 - p_pass_dropout(
        VERIF_EPS_FIRST_ORDER)) / VERIF_EPS_FIRST_ORDER

    # dropout exact anchors (dyadic eps)
    drop_anchors = {}
    for denom in (64, 1024):
        eps = 1.0 / denom
        exact = float(Fraction(denom - 1, denom) ** (CAL_N - CAL_OTHER))
        drop_anchors[f"1/{denom}"] = {
            "float": p_pass_dropout(eps), "exact_fraction": exact,
            "rel_diff": abs(p_pass_dropout(eps) - exact) / exact,
        }

    # mid-range exact anchor for the reshuffle convolution
    mid_float = p_pass_reshuffle(float(ANCHOR_RESHUFFLE_MID))
    mid_partial, mid_tail = p_pass_reshuffle_mid_anchor_exact()
    mid_gap = abs(mid_float - float(mid_partial))

    verification = {
        "eps1_anchor": {
            "reshuffle_float": pmf_float,
            "iid_multinomial_exact_fraction": str(pmf_exact),
            "iid_multinomial_exact_float": pmf_exact_float,
            "rel_diff": abs(pmf_float - pmf_exact_float) / pmf_exact_float,
        },
        "first_order_coefficient": {
            "exact_fraction": str(first_order_exact),
            "exact_float": float(first_order_exact),
            "reshuffle_numeric_at_1e-7": first_order_numeric,
            "dropout_numeric_at_1e-7": first_order_numeric_drop,
            "dropout_exact": CAL_N - CAL_OTHER,
        },
        "dropout_dyadic_anchors": drop_anchors,
        "reshuffle_mid_anchor_eps_1_1024": {
            "float_full_sum": mid_float,
            "exact_fraction_partial_K_le_10": str(mid_partial),
            "chernoff_tail_bound_P_K_ge_11": str(mid_tail),
            "tail_bound_float": float(mid_tail),
            "abs_gap_float_vs_partial": mid_gap,
        },
    }

    # --- joint silent-pass table (dropout kernel, map level) ---------
    silent = {}
    for e in SILENT_PASS_GRID:
        r = risk_below_float(N_PER_GROUP, MIN_EVENTS, 1.0 - e)[0]
        two = map_risk_two_groups(r)
        cal = p_pass_dropout(e)
        silent[f"{e:g}"] = {
            "p_cal_pass": cal,
            "per_group_no_events_risk": r,
            "two_group_no_events_risk": two,
            "p_reaches_adjudication": cal * (1.0 - two),
            "expected_census_displacement_per_group": N_PER_GROUP * e,
        }

    # verdict-safety: escape-the-CAL corruption vs smallest effect
    verdict_safety = {
        "escape_eps05": {"dropout": drop_eps05, "reshuffle": resh_eps05},
        "escape_displacement_seeds": {
            "dropout": N_PER_GROUP * drop_eps05,
            "reshuffle": N_PER_GROUP * resh_eps05,
        },
        "smallest_effect_seeds": {
            k: N_PER_GROUP * v for k, v in DELTAS.items()},
        "cal_pass_at_tick140_collapse":
            p_pass_dropout(1.0 - 0.96037),
        "tick140_collapse_q05": 0.96037,
    }

    return {
        "label": "W8_BLOCKPOWER_CAL_OC",
        "tick": 141,
        "gate": {"n_seeds": CAL_N, "d2t": CAL_D2T, "l2": CAL_L2,
                 "other": CAL_OTHER, "rule": "EXACT match or VOID"},
        "kernels": {
            "dropout": {"curve_eps_to_p_pass": drop_curve,
                        "eps_p05": drop_eps05,
                        "eps_p05_analytic": drop_eps05_analytic,
                        "eps_p50": drop_eps50,
                        "eps_p50_analytic": drop_eps50_analytic},
            "reshuffle": {"curve_eps_to_p_pass": resh_curve,
                          "eps_p05": resh_eps05, "eps_p50": resh_eps50},
        },
        "silent_pass_table_dropout": silent,
        "verdict_safety": verdict_safety,
        "verification": verification,
    }


def main() -> None:
    receipt = build_receipt()
    out_dir = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))),
        "evidence", "2026-10-14-w8-blockpower-cal-oc")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "cal-oc.json")
    with open(path, "w") as fh:
        json.dump(receipt, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps({
        "drop_eps05": receipt["kernels"]["dropout"]["eps_p05"],
        "resh_eps05": receipt["kernels"]["reshuffle"]["eps_p05"],
        "verif_rel_eps1":
            receipt["verification"]["eps1_anchor"]["rel_diff"],
        "verif_mid_gap":
            receipt["verification"]["reshuffle_mid_anchor_eps_1_1024"][
                "abs_gap_float_vs_partial"],
        "verif_tail_bound":
            receipt["verification"]["reshuffle_mid_anchor_eps_1_1024"][
                "tail_bound_float"],
    }, indent=1))


if __name__ == "__main__":
    main()
