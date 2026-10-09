#!/usr/bin/env python3
"""Pre-registered FIT-PARAMETER sensitivity for the w8 window
prediction (designs/011 P3; queued falsifier ed50c7ba...4daa85).

Computed BEFORE the w8 datum exists (tick 87, 2026-10-09).  Companion
to tools/w8_sensitivity.py (tick 86), which priced the EXTRAPOLATION-
FORM axis (how hazards evolve beyond w4).  This tool prices the other
axis the form note named but did not number: FIT-PARAMETER sensitivity
— how the w8 share moves when the committed VH_BASIS parameters
themselves are perturbed (i) within their own measured-receipt
uncertainty where one is quotable (the w1 census split), and (ii) at
labelled probe deltas / scales that are ARITHMETIC PROBES, never
asserted confidence bounds (tick-37 rule: uncertainty claims need a
receipt; probe deltas are just arithmetic).

The frozen W8 gate is NOT touched: HELD iff |s_w8 - 0.83376| <= 0.05,
five-step zero-decision collection chain unchanged.

Axes (all under hold-last semantics, phase capped at 4 as in
molasp.offchannel._vh_share — the held value beyond w4 IS haz[4]):
  v0-census    — the w1 snapshot D2T:L2 split at the Wilson-95 bounds
                  of its own committed census (WINDOW_MEASURED w1:
                  232:229, n=461 pairs); E and O components held
  odds         — attach pair-share odds p_D2T/(p_D2T+p_L2) shifted
                  +/-0.01/0.02/0.04 with the pair-sum and p_O fixed
  haz_l2[4]    — phase-4 L2 hazard scaled x{0.5,0.75,1.25,1.5,2}
  haz_d2t[4]   — phase-4 D2T hazard scaled x{2} (Poisson-95 arm B
                  already brackets ~x3 late: dev 0.018)
  l2-grid x2   — ALL fit-grid L2 hazards (phases 2-4) doubled, a
                  coherent fit-miss probe
  elasticity   — central-difference d(ln s8)/d(ln param) for
                  {haz_l2[4], haz_d2t[4], odds, lam}

Usage: python3 tools/w8_param_sensitivity.py [--json out.json]
"""
import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from molasp.offchannel import (VH_BASIS, _expm4, _vh_share,
                               WINDOW_MEASURED)

BAND = 0.05            # the frozen instrument band (quoted, not re-derived)
PRIMARY = 0.83376      # designs/011 P3 / the instrument's quoted centre


def _wilson95(k, n, z=1.96):
    """Wilson score interval for k successes in n trials (standard
    formula — arithmetic on the committed census counts)."""
    p = k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1.0 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def _Q(d_d2t, d_l2, lam, pD, pL, pO, d_o):
    """_build_Q with injected parameters (structure duplicated from
    molasp.offchannel on purpose: perturbations must reach the
    computation; the baseline identity anchor below proves the copy
    is the same chain)."""
    return [
        [-lam, lam * pD, lam * pL, lam * pO],
        [d_d2t, -d_d2t, 0.0, 0.0],
        [d_l2, 0.0, -d_l2, 0.0],
        [d_o, 0.0, 0.0, -d_o],
    ]


def _integrate(v0=None, lam=None, pD=None, pL=None, pO=None,
               d_o=None, d_d2t=None, d_l2=None, wmult=8):
    """Hold-last forward integration of the 4-state chain from the w1
    snapshot, with any VH_BASIS parameter overridden.  Baseline (no
    overrides) must reproduce _vh_share(8) exactly."""
    b = VH_BASIS
    v0 = list(b["v0"]) if v0 is None else list(v0)
    lam = b["lam"] if lam is None else lam
    pD = b["p"]["D2T"] if pD is None else pD
    pL = b["p"]["L2"] if pL is None else pL
    pO = b["p"]["O"] if pO is None else pO
    d_o = b["d_o"] if d_o is None else d_o
    hd = dict(b["haz_d2t"]) if d_d2t is None else d_d2t
    hl = dict(b["haz_l2"]) if d_l2 is None else d_l2
    quarter = b["quarter"]
    for step in range(int(wmult) - 1):
        phi = min(2 + step, 4)
        E = _expm4(_Q(hd[phi], hl[phi], lam, pD, pL, pO, d_o), quarter)
        v0 = [sum(v0[i] * E[i][j] for i in range(4)) for j in range(4)]
    return v0[1] / (v0[1] + v0[2])


def _s8():
    return _integrate()


def _odds_shift(delta):
    b = VH_BASIS
    pair = b["p"]["D2T"] + b["p"]["L2"]
    o = b["p"]["D2T"] / pair
    o2 = o + delta
    return _integrate(pD=pair * o2, pL=pair * (1.0 - o2))


def _scale_haz(axis, phi, factor):
    b = VH_BASIS
    tbl = dict(b[axis])
    tbl[phi] = tbl[phi] * factor
    kw = {"d_l2": tbl} if axis == "haz_l2" else {"d_d2t": tbl}
    return _integrate(**kw)


def _elasticity(perturb, eps):
    """Central-difference log-log elasticity of s8 wrt a scalar
    parameter scaled by (1 +/- eps)."""
    up = perturb(1.0 + eps)
    dn = perturb(1.0 - eps)
    return (math.log(up) - math.log(dn)) / (2.0 * eps)


def compute():
    b = VH_BASIS
    base = _s8()

    # --- identity anchors (prove the local chain IS the chain) -------
    assert abs(base - _vh_share(8)) < 1e-12, "baseline broke _vh_share"
    assert abs(base - PRIMARY) < 5e-6, "baseline broke quoted primary"

    # --- v0 census bracket (the one quotable committed uncertainty) --
    w1 = WINDOW_MEASURED[1]
    k, n = w1["d2t"], w1["d2t"] + w1["l2"]
    lo, hi = _wilson95(k, n)
    pair_mass = b["v0"][1] + b["v0"][2]        # keep E and O fixed
    v0_lo = [0.0, pair_mass * lo, pair_mass * (1.0 - lo), b["v0"][3]]
    v0_hi = [0.0, pair_mass * hi, pair_mass * (1.0 - hi), b["v0"][3]]
    s_v0_lo = _integrate(v0=v0_lo)
    s_v0_hi = _integrate(v0=v0_hi)

    # --- attach-odds probes (arithmetic probes, not bounds) ----------
    odds = b["p"]["D2T"] / (b["p"]["D2T"] + b["p"]["L2"])
    odds_arms = []
    for d in (-0.04, -0.02, -0.01, 0.01, 0.02, 0.04):
        s = _odds_shift(d)
        odds_arms.append({"delta": d, "odds": round(odds + d, 5),
                          "w8": round(s, 5),
                          "dev": round(s - base, 5)})

    # --- hazard scale probes -----------------------------------------
    l2_arms = []
    for f in (0.5, 0.75, 1.25, 1.5, 2.0):
        s = _scale_haz("haz_l2", 4, f)
        l2_arms.append({"factor": f, "w8": round(s, 5),
                        "dev": round(s - base, 5)})
    s_d2t_x2 = _scale_haz("haz_d2t", 4, 2.0)
    hl2 = dict(b["haz_l2"])
    for p_ in (2, 3, 4):
        hl2[p_] *= 2.0
    s_l2_grid_x2 = _integrate(d_l2=hl2)

    # --- elasticities --------------------------------------------------
    def _sc_l2(f):
        return _scale_haz("haz_l2", 4, f)

    def _sc_d2t(f):
        return _scale_haz("haz_d2t", 4, f)

    def _sc_odds(f):
        pair = b["p"]["D2T"] + b["p"]["L2"]
        o = b["p"]["D2T"] / pair
        return _integrate(pD=pair * o * f, pL=pair * (1.0 - o * f))

    def _sc_lam(f):
        return _integrate(lam=b["lam"] * f)

    eps = 1e-3
    elas = {
        "haz_l2[4]": round(_elasticity(_sc_l2, eps), 3),
        "haz_d2t[4]": round(_elasticity(_sc_d2t, eps), 3),
        "odds": round(_elasticity(_sc_odds, eps), 3),
        "lam": round(_elasticity(_sc_lam, eps), 3),
    }

    # lam-ratio-cancellation guard (tick-86 zero-sensitivity rule): the
    # pair share is a RATIO and lam scales every attach flux equally, so
    # the stationary ratios pi_D2T:pi_L2 = (p_D2T/d_d2t):(p_L2/d_l2) are
    # lam-free — the 0.0 elasticity is mechanism, not a dead branch.
    # Proof the perturbation still reaches the computation: under lam x2
    # the E-state mass at w8 changes materially while the share does not.
    def _vec(lam=None):
        v0l = list(b["v0"])
        lam_l = b["lam"] if lam is None else lam
        for step in range(7):
            phi = min(2 + step, 4)
            E = _expm4(_Q(b["haz_d2t"][phi], b["haz_l2"][phi],
                         lam_l, b["p"]["D2T"], b["p"]["L2"],
                         b["p"]["O"], b["d_o"]), b["quarter"])
            v0l = [sum(v0l[i] * E[i][j] for i in range(4))
                   for j in range(4)]
        return v0l
    v_base, v_lam2 = _vec(), _vec(lam=b["lam"] * 2.0)
    assert abs(v_base[0] - v_lam2[0]) > 1e-9, \
        "lam perturbation did not reach the computation"
    _sb = v_base[1] / (v_base[1] + v_base[2])
    _sl = v_lam2[1] / (v_lam2[1] + v_lam2[2])
    lam_check = {
        "share_lam_x2": round(_sl, 8),
        "share_base": round(_sb, 8),
        "residual_abs_x2": round(abs(_sl - _sb), 8),
        "E_mass_base_w8": "%.4e" % v_base[0],
        "E_mass_lam_x2_w8": "%.4e" % v_lam2[0],
        "mechanism": "lam scales all attach fluxes equally; the pair "
                     "share is a ratio (stationary pi_D2T:pi_L2 = "
                     "(p_D2T/d_d2t):(p_L2/d_l2) is lam-free), so the E "
                     "mass moves O(1) while the share moves only ~4e-5 "
                     "at x2 (elasticity ~7e-5, four orders below odds)",
    }
    assert lam_check["residual_abs_x2"] < 1e-4, \
        "lam residual grew beyond the measured cancellation scale"

    v0_width = s_v0_hi - s_v0_lo
    odds_width = odds_arms[-1]["w8"] - odds_arms[0]["w8"]
    l2_width = l2_arms[-1]["w8"] - l2_arms[0]["w8"]

    return {
        "registered": "2026-10-09 (tick 87) — BEFORE the w8 datum exists",
        "frozen_gate": "HELD iff |s_w8 - %.5f| <= %.2f (instrument "
                       "ed50c7ba...4daa85; NOT touched by this note)"
                       % (PRIMARY, BAND),
        "baseline_w8": round(base, 5),
        "v0_census_bracket": {
            "census": "WINDOW_MEASURED w1 = %d:%d (n=%d pairs)" % (k, n, n),
            "wilson95": [round(lo, 5), round(hi, 5)],
            "w8_at_lo": round(s_v0_lo, 5),
            "w8_at_hi": round(s_v0_hi, 5),
            "induced_width": round(v0_width, 5),
            "vs_band_halfwidth": round(v0_width / BAND, 3),
        },
        "attach_odds_probes": {
            "fitted_odds": round(odds, 5),
            "label": "arithmetic probes at fixed pair-sum and p_O — "
                     "NOT confidence bounds (no odds-bracket receipt)",
            "arms": odds_arms,
            "induced_width_pm0.04": round(odds_width, 5),
        },
        "haz_l2_4_scale_probes": {
            "arms": l2_arms,
            "induced_width_x0.5_to_x2": round(l2_width, 5),
        },
        "haz_d2t_4_x2": {"w8": round(s_d2t_x2, 5),
                         "dev": round(s_d2t_x2 - base, 5)},
        "haz_l2_grid_x2": {"w8": round(s_l2_grid_x2, 5),
                           "dev": round(s_l2_grid_x2 - base, 5)},
        "elasticities_d_ln_s8_d_ln_param": elas,
        "lam_ratio_cancellation": lam_check,
        "for_comparison_tick86": {
            "hazard_form_spread": 0.20609,
            "band_halfwidth": BAND,
            "arm_B_hazard95_d2t_dev": 0.01791,
        },
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
