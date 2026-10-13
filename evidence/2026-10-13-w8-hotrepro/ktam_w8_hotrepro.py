#!/usr/bin/env python3
"""W8 hot-window family reproduction probe (SON-5140) — the successor
to the tick-101 block probe, pre-registered from the CORRECTED state
(see research-log/2026-10-13-w8-arm6-prereg.md CORRECTION and the
2026-10-13 log entry): the six-window set is
[(375,500),(370,500),(389,500),(365,499),(372,500),(391,500)] with
exactly two hot 500-seed windows — arm-6 340261107+[0,500) at 389/500
and the mid-stride control arm-8 350261107+[0,500) at 391/500 — against
the family rate q0 = 1110/1499.  The tick-101 probe returned AMBIG_MIDDLE
+ HOT_NEIGHBORHOOD and was underpowered.  This probe asks the question
with real power against the window-noise account: does EITHER hot
family reproduce its elevation on FRESH, DISJOINT windows of its own
block at n=1000 per family (resolution the 500-seed instrument lacks)?

Instrument: the simulation core imported VERBATIM from
ktam_w8_blockprobe.py (same BUILD1 Vp-missing protocol, same s2
lock-read arithmetic, same run_traj — DW9's function verbatim, no
RNG-order change — same WIN_MULT=8 read window, same CAL identity gate
mid-window pair census over seeds 260261107+[0,500) must be EXACTLY
D2T 367 : L2 131):

  CAL      seeds 260261107 + i, i in [0,500)  (arm 2) — UNCHANGED.
  A_FRESH  seeds 340261107 + 1000 + i, i in [0,1000) — arm-6's block,
           windows [1000,2000), DISJOINT from the burned [0,1000)
           (arm-6's own window + tick-101's 6B window [500,1000)).
  B_FRESH  seeds 350261107 + 500 + i, i in [0,1000) — arm-8's block,
           windows [500,1500), DISJOINT from the burned [0,500).

PRE-REGISTERED family gate (frozen before submission):

  x_j    = family-j fresh terminal pair census D2T count; denominator
           n_j = D2T + L2 (pair terminals; non-pair reported).
  test   = exact ONE-SIDDED upper-tail binomial
           p_j = P(X >= x_j | n_j, q0),  q0 = 1110/1499 (frozen).
  gate   = min over the two families of p_j vs Bonferroni
           alpha* = 0.025 per family (family alpha = 0.05, 2 families).

  Branch map (mechanical, exhaustive, no default):
    CAL_FAIL                        -> VOID (instrument, not science)
    min n_j < 400 (MIN_EVENTS)      -> NO_EVENTS
    min p_j <= 0.025                -> BLOCK_STRUCTURE
    0.025 < min p_j <= 0.05         -> AMBIG_MIDDLE
    min p_j > 0.05                  -> WINDOW_NOISE

  BLOCK_STRUCTURE: at least one hot family's FRESH windows reproduce
  the elevation above the family rate — the window-noise account is
  rejected for that family at this resolution.
  WINDOW_NOISE: neither hot family reproduces on fresh windows; the
  window-noise account stands UNREFUTED (not proven — see boundaries).

  MEASURED branch windows at n_j = 1000 (exact binomial, q0=1110/1499,
  pre-registered as descriptive context): min p <= 0.025 first at
  x = 768 (p=0.02468282); p <= 0.05 first at x = 764 (p=0.04742232).
  So at exactly n=1000: x >= 768 -> BLOCK_STRUCTURE, 764..767 ->
  AMBIG_MIDDLE, x <= 763 -> WINDOW_NOISE.  The map itself reads p,
  not x, so a realized n_j < 1000 (non-pair terminals) stays mechanical.

Power (planning, normal approximation, descriptive only): under a true
family rate of 0.78 at n=1000, z = (0.78-0.7405)/0.01386 = 2.85 ->
per-family power at one-sided 0.025 is ~0.81, family (>=1 of 2)
~0.96.  Under 0.76 (elevation ~0.02): z = 1.41 -> per-family ~0.29,
family ~0.50.  Elevations of ~0.02 remain hard to detect: the
0.02-0.03 rate-resolution boundary is ENGAGED, not erased.

Boundaries (frozen): this probe adjudicates FAMILY/BLOCK-level
elevation only.  Hot structure localized to fewer than ~500 seeds
inside a family remains undetected by any 500-seed-window instrument
(tick-98/101 boundary carried forward).  A WINDOW_NOISE verdict does
not certify that all windows are identical.  In-silico kTAM simulation
only; no physical-replicate inference, no chemical-performance claim,
no wet-lab execution.

SMOKE=1 runs 8 trajectories per arm and labels output SMOKE_ONLY; it
is never a verdict surface.
"""

from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
PREVIOUS = os.path.join(REPO, "evidence", "2026-10-09-w8-blockprobe")
TILES_AND_DIR = os.path.join(REPO, "evidence", "2026-10-06-body-conjunction-builds")
TILES_DEATH_DIR = os.path.join(REPO, "evidence", "2026-10-06-structural-death")
for path in (REPO, PREVIOUS, TILES_AND_DIR, TILES_DEATH_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

from ktam_w8_blockprobe import (  # noqa: E402
    BASE_SEED,
    BUILD1,
    CAL_D2T,
    CAL_L2,
    DG,
    SEED0_CAL,
    WIN_MULT,
    build_missing_species,
    canonical_assembly,
    census,
    matched_s2,
    run_traj,
    wilson,
)

# ---- frozen probe constants (identity-pinned in tests) ----
SEED0_AFRESH = 340261107 + 1000   # 341261107: arm-6 block, window [1000,2000)
SEED0_BFRESH = 350261107 + 500    # 350261607: arm-8 block, window [500,1500)
N_FRESH = 8 if os.environ.get("SMOKE") else 1000
N_CAL = 8 if os.environ.get("SMOKE") else 500

FAM_X = 1110                      # family pool, full-n arms (3+5+7)
FAM_K = 1499
Q0 = FAM_X / float(FAM_K)         # 0.7404936624... frozen null rate
ALPHA_STAR = 0.025                # Bonferroni per-family (family alpha .05)
ALPHA_SOFT = 0.05                 # AMBIG upper edge
MIN_EVENTS = 400

# burned-window references (context, never pooled into the primary test)
REF_ARM6 = {"x": 389, "k": 500, "seed0": 340261107, "offset": 0}
REF_ARM6B = {"x": 372, "k": 500, "seed0": 340261107, "offset": 500}
REF_ARM8 = {"x": 391, "k": 500, "seed0": 350261107, "offset": 0}


def log_binom_pmf(k, n, q):
    return (math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)
            + k * math.log(q) + (n - k) * math.log(1.0 - q))


def p_upper(x, n, q):
    """Exact one-sided upper-tail binomial P(X >= x | X~Bin(n,q)),
    log-space summation (mirrors the committed exact conventions)."""
    if x <= 0:
        return 1.0
    if x > n:
        return 0.0
    return math.fsum(math.exp(log_binom_pmf(k, n, q)) for k in range(x, n + 1))


def family_gate(xa, na, xb, nb):
    """Frozen branch map. Returns (branch, tests)."""
    pa = p_upper(xa, na, Q0)
    pb = p_upper(xb, nb, Q0)
    tests = {"p_afresh": pa, "p_bfresh": pb,
             "alpha_star": ALPHA_STAR, "alpha_soft": ALPHA_SOFT}
    if min(na, nb) < MIN_EVENTS:
        return "NO_EVENTS", tests
    mp = min(pa, pb)
    if mp <= ALPHA_STAR:
        return "BLOCK_STRUCTURE", tests
    if mp <= ALPHA_SOFT:
        return "AMBIG_MIDDLE", tests
    return "WINDOW_NOISE", tests


def subwindow_shares(trajs, seed0, width, sub=500):
    """Descriptive per-500-sub-window D2T shares (no gates ride on
    these; they feed any later localization pre-registration)."""
    out = []
    for start in range(0, len(trajs), sub):
        chunk = trajs[start:start + sub]
        c = census(chunk, "terminal")
        n = c["D2T"] + c["L2"]
        out.append({"seed0": seed0 + start, "n": len(chunk),
                    "x": c["D2T"], "pair_n": n,
                    "share": (c["D2T"] / n) if n else None})
    return out


def main():
    b1v = build_missing_species(BUILD1, "Vp")
    canon = canonical_assembly(BUILD1)
    cal_tr = [run_traj(b1v, matched_s2, canon, SEED0_CAL + i,
                       DG, WIN_MULT) for i in range(N_CAL)]
    a_tr = [run_traj(b1v, matched_s2, canon, SEED0_AFRESH + i,
                     DG, WIN_MULT) for i in range(N_FRESH)]
    b_tr = [run_traj(b1v, matched_s2, canon, SEED0_BFRESH + i,
                     DG, WIN_MULT) for i in range(N_FRESH)]

    cal_mid = census(cal_tr, "mid")
    a_term = census(a_tr, "terminal")
    b_term = census(b_tr, "terminal")

    cal = ("CAL_OK" if (N_CAL != 500 or
                        (cal_mid["D2T"] == CAL_D2T and
                         cal_mid["L2"] == CAL_L2)) else "CAL_FAIL")

    xa = a_term["D2T"]
    na = a_term["D2T"] + a_term["L2"]
    xb = b_term["D2T"]
    nb = b_term["D2T"] + b_term["L2"]

    if cal == "CAL_OK":
        branch, tests = family_gate(xa, na, xb, nb)
    else:
        branch, tests = "VOID", None

    combined_x, combined_n = xa + xb, na + nb
    out = {
        "label": "SMOKE_ONLY" if os.environ.get("SMOKE") else "W8_HOTREPRO",
        "n_cal": N_CAL, "n_fresh": N_FRESH,
        "seed0_cal": SEED0_CAL, "seed0_afresh": SEED0_AFRESH,
        "seed0_bfresh": SEED0_BFRESH,
        "dg": DG, "win_mult": WIN_MULT, "t_mid_is_w4": True,
        "q0": Q0, "family": {"x": FAM_X, "k": FAM_K},
        "cal_mid_w4": cal_mid, "cal": cal,
        "afresh_terminal_w8": a_term, "bfresh_terminal_w8": b_term,
        "afresh": {"x": xa, "n": na},
        "bfresh": {"x": xb, "n": nb},
        "afresh_wilson95": wilson(xa, na),
        "bfresh_wilson95": wilson(xb, nb),
        "combined_fresh": {"x": combined_x, "n": combined_n,
                           "share": (combined_x / float(combined_n))
                           if combined_n else None,
                           "wilson95": wilson(combined_x, combined_n)},
        "burned_context": {"arm6": REF_ARM6, "arm6b": REF_ARM6B,
                           "arm8": REF_ARM8,
                           "arm6_block_burned": {"x": REF_ARM6["x"] + REF_ARM6B["x"],
                                                 "k": REF_ARM6["k"] + REF_ARM6B["k"]}},
        "afresh_subwindows": subwindow_shares(a_tr, SEED0_AFRESH, N_FRESH),
        "bfresh_subwindows": subwindow_shares(b_tr, SEED0_BFRESH, N_FRESH),
        "branch": branch, "tests": tests,
    }
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
