#!/usr/bin/env python3
"""Pre-registered extrapolation-form sensitivity for the w8 window
prediction (designs/011 P3; queued falsifier ed50c7ba...4daa85).

Computed BEFORE the w8 datum exists (tick 86, 2026-10-09).  The frozen
W8 gate (evidence/2026-10-08-w8-hazardhold/ktam_w8_hazardhold.py:
HELD iff |s_w8 - 0.83376| <= 0.05) is NOT touched: this tool only
quantifies which beyond-w4 hazard forms a verdict datum could still
be consistent with, so the collection-day reading is fork-free.

Every input is a committed receipt (tick-37 static rule): the VH_BASIS
tables in molasp/offchannel.py (quoted from evidence receipts, never
asserted).  Deterministic pure-python arithmetic; identical inputs
give byte-identical output.

Arms (all integrate the SAME validated chain from the w1 snapshot
through the fit grid; they differ only in the hazard policy for
phases >= 5, i.e. beyond the w4 fit-grid edge):
  A hold-last   — phase-4 hazards held (the designs/011 primary;
                  identity with molasp.offchannel._vh_share(8))
  B hazard95    — D2T late hazards at their Poisson-95 upper bounds
                  (identity with marginal_window_pricing()["8"]
                  ["hazard95_share"], the committed bracket arm)
  C l2-trend    — L2 hazard log-linear in phase over the fit grid
                  (phases 2-4) and extrapolated to phases 5-8;
                  D2T held at phase 4
  D l2-zero     — L2 hazard pinned to 0 beyond w4; D2T held

Usage: python3 tools/w8_sensitivity.py [--json out.json]
"""
import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from molasp.offchannel import (VH_BASIS, _build_Q, _expm4, _vh_share,
                               marginal_window_pricing)

BAND = 0.05            # the frozen instrument band (quoted, not re-derived)
PRIMARY = 0.83376      # designs/011 P3 / the instrument's quoted centre

# Poisson-95 upper bounds on the late D2T hazards (VH1 receipt,
# duplicated from marginal_window_pricing's committed bracket arm).
_H95 = {1: VH_BASIS["haz_d2t"][1], 2: VH_BASIS["haz_d2t"][2],
        3: 3.2763010789370227e-09, 4: 3.096599867561759e-09}


def _l2_trend_table():
    """Log-linear fit of ln(haz_l2) on phase over the fit grid 2..4,
    extrapolated to phases 5..8 (static arithmetic on committed
    receipts)."""
    xs, ys = [2, 3, 4], [math.log(VH_BASIS["haz_l2"][p]) for p in (2, 3, 4)]
    n = 3
    sx, sy = sum(xs), sum(ys)
    sxx = sum(x * x for x in xs)
    sxy = sum(x * y for x, y in zip(xs, ys))
    slope = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    icpt = (sy - slope * sx) / n
    tbl = {p: VH_BASIS["haz_l2"][p] for p in (1, 2, 3, 4)}
    for p in (5, 6, 7, 8):
        tbl[p] = math.exp(icpt + slope * p)
    return tbl, slope


def _integrate(haz_at, wmult=8):
    """Forward-integrate the 4-state chain from the w1 snapshot.

    Unlike molasp.offchannel._vh_share (which CAPS the phase index at
    4 — its hold-last semantics), this integrator passes the TRUE
    phase index so arm policies can differ beyond w4.  Arm A must
    reproduce _vh_share exactly (identity-checked in compute()).
    """
    v = list(VH_BASIS["v0"])
    states = {1: [round(x, 8) for x in v]}
    for step in range(int(wmult) - 1):
        phi = 2 + step
        d, l = haz_at(phi)
        E = _expm4(_build_Q(d, l), VH_BASIS["quarter"])
        v = [sum(v[i] * E[i][j] for i in range(4)) for j in range(4)]
        states[min(phi, wmult)] = [round(x, 8) for x in v]
    return v, states


def _share(v):
    return v[1] / (v[1] + v[2])


def _stationary_ceiling():
    """Stationary pair share under phase-4 hazards held forever: the
    LEFT null vector of Q(hd4, hl4) plus normalisation (designs/011
    P3 quotes 0.97865 — reproduced, not asserted)."""
    Q = _build_Q(VH_BASIS["haz_d2t"][4], VH_BASIS["haz_l2"][4])
    M = [[Q[j][i] for j in range(4)] for i in range(4)]      # transpose
    A = [M[1], M[2], M[3], [1.0, 1.0, 1.0, 1.0]]
    rhs = [0.0, 0.0, 0.0, 1.0]
    d0 = _det(A)
    pi = [_det([A[r][:c] + [rhs[r]] + A[r][c + 1:]
                for r in range(4)]) / d0 for c in range(4)]
    return pi[1] / (pi[1] + pi[2]), pi


def _det(M):
    M = [row[:] for row in M]
    n, dv = len(M), 1.0
    for i in range(n):
        p = max(range(i, n), key=lambda r: abs(M[r][i]))
        if abs(M[p][i]) < 1e-300:
            return 0.0
        if p != i:
            M[i], M[p] = M[p], M[i]
            dv = -dv
        dv *= M[i][i]
        for r in range(i + 1, n):
            f = M[r][i] / M[i][i]
            for c in range(i, n):
                M[r][c] -= f * M[i][c]
    return dv


def compute():
    hd, hl = VH_BASIS["haz_d2t"], VH_BASIS["haz_l2"]
    l2t, slope = _l2_trend_table()

    def arm_A(phi):
        return hd[min(phi, 4)], hl[min(phi, 4)]

    def arm_B(phi):
        return _H95[min(phi, 4)], hl[min(phi, 4)]

    def arm_C(phi):
        return hd[4], l2t[phi]

    def arm_D(phi):
        return hd[4], (hl[4] if phi <= 4 else 0.0)

    vA, states = _integrate(arm_A)
    vB, _ = _integrate(arm_B)
    vC, _ = _integrate(arm_C)
    vD, _ = _integrate(arm_D)
    a, b, c, d = _share(vA), _share(vB), _share(vC), _share(vD)

    # Identity anchors (the tool must reproduce the committed numbers)
    assert abs(a - _vh_share(8)) < 1e-12, "arm A broke _vh_share identity"
    assert abs(a - PRIMARY) < 5e-6, "arm A broke the quoted primary"
    mwp8 = marginal_window_pricing()["windows"]["8"]
    assert abs(b - mwp8["hazard95_share"]) < 1e-12, \
        "arm B broke the committed bracket identity"

    ceiling, pi = _stationary_ceiling()
    assert abs(ceiling - 0.97865) < 5e-5, "stationary anchor drifted"

    odds = VH_BASIS["p"]["D2T"] / (VH_BASIS["p"]["D2T"] + VH_BASIS["p"]["L2"])
    arms = [
        {"arm": "A hold-last", "w8": round(a, 5),
         "policy": "phase-4 hazards held beyond w4 (designs/011 primary)",
         "identity": "_vh_share(8)"},
        {"arm": "B hazard95-d2t", "w8": round(b, 5),
         "policy": "late D2T hazards at Poisson-95 upper bounds (VH1)",
         "identity": "marginal_window_pricing bracket"},
        {"arm": "C l2-loglinear-trend", "w8": round(c, 5),
         "policy": "ln(haz_l2) linear in phase over 2-4, extrapolated; "
                   "ratio/phase %.4f" % math.exp(slope)},
        {"arm": "D l2-zero-beyond-w4", "w8": round(d, 5),
         "policy": "no L2 detach at all beyond w4"},
    ]
    for rec in arms:
        rec["band"] = [round(rec["w8"] - BAND, 5), round(rec["w8"] + BAND, 5)]
        rec["abs_dev_from_primary"] = round(abs(rec["w8"] - a), 5)
        rec["within_primary_band"] = abs(rec["w8"] - a) <= BAND
    spread = max(x["w8"] for x in arms) - min(x["w8"] for x in arms)
    lo_a, hi_a = a - BAND, a + BAND
    lo_c, hi_c = c - BAND, c + BAND
    reading = {
        "frozen_gate_verdict(s)":
            "HELD iff %.5f <= s <= %.5f; else REFUTED (instrument, "
            "frozen)" % (lo_a, hi_a),
        "regions": [
            {"s": "[0.78376, 0.81415]", "verdict": "HELD",
             "arms_alive": "A and C (B nested): form AMBIGUOUS — the "
                           "datum cannot separate hold-last from the "
                           "log-linear trend; chain account intact"},
            {"s": "(0.81415, 0.88376]", "verdict": "HELD",
             "arms_alive": "A only: hold-last form confirmed over the "
                           "trend (trend band tops at 0.81415)"},
            {"s": "[0.71415, 0.78376)", "verdict": "REFUTED",
             "arms_alive": "C not A: the falsified content is the "
                           "hazard-HOLD choice, not the chain account. "
                           "Frozen refutation actions STILL apply; the "
                           "trend form becomes the working hypothesis "
                           "for a FOLLOW-UP design (w6 anchor or direct "
                           "late-L2 hazard measurement) — not an "
                           "automatic un-quarantine"},
            {"s": "< 0.71415", "verdict": "REFUTED",
             "arms_alive": "none (D band [0.57767, 0.67767] only "
                           "covers s < 0.67767 and predicts the share "
                           "FALLS below w4's 0.74135 — an unmodeled "
                           "process): the flux/chain account itself is "
                           "falsified beyond w4"},
            {"s": "> 0.88376", "verdict": "REFUTED (high)",
             "arms_alive": "none: no hazard form predicts above the "
                           "primary band; only the stationary ceiling "
                           "(0.97865) lies above — unmodeled "
                           "acceleration"},
        ],
        "region_bounds_computed": {
            "primary_band": [round(lo_a, 5), round(hi_a, 5)],
            "trend_band": [round(lo_c, 5), round(hi_c, 5)],
            "overlap_A_and_C": [round(max(lo_a, lo_c), 5),
                                round(min(hi_a, hi_c), 5)],
        },
    }
    return {
        "registered": "2026-10-09 (tick 86) — BEFORE the w8 datum exists",
        "frozen_gate": "HELD iff |s_w8 - %.5f| <= %.2f (instrument "
                       "ed50c7ba...4daa85; NOT touched by this note)"
                       % (PRIMARY, BAND),
        "primary": round(a, 5),
        "arms": arms,
        "hazard_form_spread": round(spread, 5),
        "all_forms_inside_primary_band": all(
            x["within_primary_band"] for x in arms),
        "stationary_ceiling_hold_last": round(ceiling, 5),
        "stationary_pi": [round(x, 5) for x in pi],
        "state_vectors_hold_last": states,
        "attach_odds_pair_share": round(odds, 5),
        "trend_l2_hazards_5_to_8": {str(p): "%.4e" % l2t[p]
                                    for p in (5, 6, 7, 8)},
        "reading_map": reading,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", metavar="OUT", help="also write JSON here")
    args = ap.parse_args()
    out = compute()
    text = json.dumps(out, indent=2, sort_keys=True)
    print(text)
    if args.json:
        Path(args.json).write_text(text + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
