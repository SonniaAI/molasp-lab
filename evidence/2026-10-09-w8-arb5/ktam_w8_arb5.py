#!/usr/bin/env python3
"""W8 arm-5 pairwise arbitration (tick 98, SON-4919) — adjudicates
the two candidate explanations for the tick-97 POOLING_CONTESTED
receipt (min_exact_p 5.6667e-3 between arm-3 375/500 = 0.750 and
arm-4 106/153 = 0.6928):

  (S) ARM4_SMALLN     arm-4's low share is a small-n artifact of
                      n=153; arm-level shares are iid draws from
                      one w8 rate; the pooling premise stands.
  (B) BLOCK_STRUCTURE the difference is real across reserved
                      stride blocks; pooling stays contested; DW9 /
                      VH cross-seed stability statements need a
                      re-read at the w8 level.

Instrument: VERBATIM ktam_w8_growth.py / ktam_w8_hazardhold.py
(same BUILD1 Vp-missing protocol, same s2 lock-read arithmetic,
same run_traj — DW9's function VERBATIM, no RNG-order change —
same WIN_MULT=8 read window, same CAL identity gate):

  CAL   seeds 260261107 + i, i in [0,500) — DW9's exact seeds
        (arm 2 of the reserved stride block).  UNCHANGED.
  ARM5  seeds 320261107 + i, i in [0,500) — arm 5 of the reserved
        stride block (220261107 + 5*2e7), NEVER run before this
        job.  n=500 gives the arbitration the same precision as
        the arm-3 datum.

PRE-REGISTERED pairwise reading (frozen before submission; tick-97
recommendation, pairwise over beta-binomial refit):

  x5      = arm-5 terminal pair census D2T count, denominator
            n5 = D2T + L2 (pair terminals; non-pair reported).
  P3      = exact_two_sided_p(n5, 375/500, x5)   — vs arm-3 rate
  P4      = exact_two_sided_p(n5, 106/153, x5)   — vs arm-4 rate
            (point-probability method, log-space — VERBATIM
            tools/w8_dispersion_receipt.py, constants duplicated
            here on purpose so the instrument is self-contained)
  alpha   = 0.05 (fixed now, before the datum)

  Branch map (mechanical, exhaustive, no default arm):
    CAL_FAIL                      -> VOID (instrument, not science)
    n5 < 50 (MIN_EVENTS floor)    -> NO_EVENTS
    P3 >= a and P4 <  a           -> ARM4_SMALLN     (account S)
    P3 <  a and P4 >= a           -> BLOCK_STRUCTURE (account B)
    P3 >= a and P4 >= a           -> AMBIGUOUS_MIDDLE
    P3 <  a and P4 <  a           -> OUTSIDE_BOTH (mechanism search)

  ARM4_SMALLN restores the ladder's pooling premise at the arm
  level (pooled line datum 481/653 becomes claimable; growing may
  resume mechanically).  BLOCK_STRUCTURE keeps pooling contested:
  arm-level reporting only, next step = block-mechanism probe
  (stride-block dependence), never more blind growth.
  AMBIGUOUS_MIDDLE / OUTSIDE_BOTH: record; OUTSIDE_BOTH reopens
  the mechanism search (neither reference rate describes w8).

Descriptive (labelled, no gates): arm-5 Wilson-95 alone; the
3-arm leave-one-out dispersion receipt recomputed at collection
with the committed tool on [(375,500),(106,153),(x5,500)].

SMOKE=1 runs n=8 per arm (instrument check only; CAL gate skipped
at smoke scale — gates stay verbatim per the tick-43 lesson).
"""
import json
import math
import os
import random
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
for p in (HERE, REPO):
    if p not in sys.path:
        sys.path.insert(0, p)

from tiles_and import BUILD1                          # noqa: E402
from tiles_death import build_missing_species         # noqa: E402
from molasp.offchannel import (canonical_assembly,    # noqa: E402
                               matched_strength)

GMC = 9.5
BASE_SEED = 220261107
SEED_STRIDE = 20000000
SEED0_CAL = BASE_SEED + 2 * SEED_STRIDE    # 260261107 (DW9 layout, arm 2)
SEED0_ARM5 = BASE_SEED + 5 * SEED_STRIDE  # 320261107 (arm 5, never run)
N_CAL = 8 if os.environ.get("SMOKE") else 500
N_ARM5 = 8 if os.environ.get("SMOKE") else 500
DG = 2.0
WIN_MULT = 8.0
SITE = (2, 2)                  # the Vp vacancy: fill/substitution site
FACE_DIR = {"E": (1, 0), "N": (0, 1), "S": (0, -1), "W": (-1, 0)}
CAL_D2T = 367
CAL_L2 = 131
MIN_EVENTS = 50
ARM3_X = 375                   # tick-96 receipt: arm-3 w8 terminal census
ARM3_K = 500                   # 375 D2T + 125 L2, other = 0
ARM4_X = 106                   # tick-97 receipt: arm-4 w8 terminal census
ARM4_K = 153                   # 106 D2T + 47 L2, other = 0
ALPHA = 0.05                   # pre-registered, fixed before the datum
_EPS = 1e-9                    # verbatim tools/w8_dispersion_receipt.py


def logpmf(k: int, p: float, x: int) -> float:
    """log P(X = x) for X ~ Bin(k, p), log-space via lgamma."""
    if x < 0 or x > k:
        return -math.inf
    return (
        math.lgamma(k + 1)
        - math.lgamma(x + 1)
        - math.lgamma(k - x + 1)
        + x * math.log(p)
        + (k - x) * math.log1p(-p)
    )


def exact_two_sided_p(k: int, p: float, x_obs: int) -> float:
    """Two-sided exact binomial p-value, point-probability method:
    P(pmf(X) <= pmf(x_obs)), computed in log-space.
    VERBATIM tools/w8_dispersion_receipt.py (duplication on purpose)."""
    if not (0.0 < p < 1.0):
        return 1.0
    lp_obs = logpmf(k, p, x_obs)
    if lp_obs == -math.inf:
        return 1.0
    total = 0.0
    for x in range(k + 1):
        lp = logpmf(k, p, x)
        if lp <= lp_obs + _EPS:
            total += math.exp(lp - lp_obs)
    return min(1.0, total * math.exp(lp_obs))


def matched_s2(build, asm, site, tile_name):
    """Family matched strength with the lock-read bond doubled
    (verbatim tick-38/41/43 arithmetic)."""
    b = matched_strength(build, asm, site, tile_name)
    faces = build["tiles"][tile_name]
    if tile_name.startswith("L"):
        g1 = faces.get("W")
        nb = (site[0] - 1, site[1])
        if nb[1] == 0 and nb in build["seed"]:
            g2 = build["seed"][nb]
        elif nb in asm:
            g2 = build["tiles"][asm[nb]].get("E")
        else:
            g2 = None
        if g1 and g2 and g1 == g2:
            b += 1
    else:
        g1 = faces.get("E")
        nb = (site[0] + 1, site[1])
        if nb in asm and str(asm[nb]).startswith("L"):
            g2 = build["tiles"][asm[nb]].get("W")
            if g1 and g2 and g1 == g2:
                b += 1
    return b


def run_traj(build, matched, canon, seed, dg, win_mult):
    """One trajectory, protocol of record — VERBATIM DW9 run_traj
    (passive event log included; the RNG stream is unchanged)."""
    rng = random.Random(seed)
    rf = math.exp(-GMC)
    gse = GMC - dg
    t_read = win_mult * 400.0 * math.exp(GMC)
    assembly = dict((s, "seed") for s in build["seed"])
    sites = sorted(canon)
    t = 0.0
    churn = 0
    prev = assembly.get(SITE)
    log = []
    while True:
        events = []
        for site in sites:
            if site in assembly:
                b = matched(build, assembly, site, assembly[site])
                events.append((math.exp(-b * gse), "detach", site))
            elif any((site[0] + dx, site[1] + dy) in assembly
                     for dx, dy in FACE_DIR.values()):
                for tile in build["tiles"]:
                    if matched(build, assembly, site, tile) >= 1:
                        events.append((rf, "attach", (site, tile)))
        total = sum(r for r, _, _ in events)
        if total <= 0 or t > t_read:
            break
        t_next = t + rng.expovariate(total)
        if t_next > t_read:
            t = t_read
            break
        t = t_next
        r = rng.random() * total
        acc = 0.0
        for rate, kind, arg in events:
            acc += rate
            if acc >= r:
                if kind == "attach":
                    assembly[arg[0]] = arg[1]
                else:
                    del assembly[arg]
                break
        occ = assembly.get(SITE)
        if occ != prev:
            churn += 1
            log.append((t, prev, occ))
            prev = occ
    return {"terminal": assembly.get(SITE), "churn": churn,
            "t_read": t_read, "log": log}


def mid_class(tr):
    """SITE occupancy class at t_mid = t_read/2 (the 4x window time).
    Same convention as DW9's terminal read: state after the last log
    transition with t <= t_mid, initial class (empty) if none."""
    t_mid = tr["t_read"] / 2.0
    s = None
    for (t, frm, to) in tr["log"]:
        if t <= t_mid:
            s = to
        else:
            break
    return s


def census(trajs, at):
    """Pair census at 'mid' (4x window) or 'terminal' (8x window)."""
    cls = (mid_class(tr) for tr in trajs) if at == "mid" else \
          (tr["terminal"] for tr in trajs)
    c = Counter("EMPTY" if x is None else str(x) for x in cls)
    d2t = c.get("D2T", 0)
    l2 = c.get("L2", 0)
    other = len(trajs) - d2t - l2
    share = d2t / float(d2t + l2) if d2t + l2 else None
    return {"D2T": d2t, "L2": l2, "other": other, "share": share}


def wilson(k, n, z=1.96):
    if not n:
        return None
    p = k / float(n)
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 5), round(c + h, 5)]


def arbitrate(n5_pair, x5):
    """Pairwise arbitration, branch map pre-registered in the
    docstring: mechanical, exhaustive, no default arm.  Returns
    (branch, p3, p4); p3/p4 None outside the COUNTED regime."""
    if n5_pair < MIN_EVENTS:
        return "NO_EVENTS", None, None
    p3 = exact_two_sided_p(n5_pair, ARM3_X / float(ARM3_K), x5)
    p4 = exact_two_sided_p(n5_pair, ARM4_X / float(ARM4_K), x5)
    if p3 >= ALPHA and p4 < ALPHA:
        return "ARM4_SMALLN", p3, p4
    if p3 < ALPHA and p4 >= ALPHA:
        return "BLOCK_STRUCTURE", p3, p4
    if p3 >= ALPHA and p4 >= ALPHA:
        return "AMBIGUOUS_MIDDLE", p3, p4
    return "OUTSIDE_BOTH", p3, p4


def main():
    b1v = build_missing_species(BUILD1, "Vp")
    canon = canonical_assembly(BUILD1)
    cal_tr = [run_traj(b1v, matched_s2, canon, SEED0_CAL + i,
                       DG, WIN_MULT) for i in range(N_CAL)]
    ar_tr = [run_traj(b1v, matched_s2, canon, SEED0_ARM5 + i,
                      DG, WIN_MULT) for i in range(N_ARM5)]
    cal_mid = census(cal_tr, "mid")
    cal_term = census(cal_tr, "terminal")
    ar_mid = census(ar_tr, "mid")
    ar_term = census(ar_tr, "terminal")

    cal = ("CAL_OK" if (N_CAL != 500 or
                        (cal_mid["D2T"] == CAL_D2T and
                         cal_mid["L2"] == CAL_L2)) else "CAL_FAIL")

    x5 = ar_term["D2T"]
    n5_pair = ar_term["D2T"] + ar_term["L2"]
    p3 = p4 = None
    arb = None
    if cal == "CAL_OK":
        arb, p3, p4 = arbitrate(n5_pair, x5)
    else:
        arb = "VOID"

    out = {
        "n_cal": N_CAL, "n_arm5": N_ARM5,
        "seed0_cal": SEED0_CAL, "seed0_arm5": SEED0_ARM5,
        "dg": DG, "win_mult": WIN_MULT,
        "t_mid_is_w4": True,
        "cal_mid_w4": cal_mid, "cal_terminal_w8": cal_term,
        "arm5_mid_w4": ar_mid, "arm5_terminal_w8": ar_term,
        "references": {"arm3": {"x": ARM3_X, "k": ARM3_K},
                       "arm4": {"x": ARM4_X, "k": ARM4_K}},
        "pairwise": {"p3": p3, "p4": p4, "alpha": ALPHA},
        "branch": arb,
        "arm5_wilson95": wilson(x5, n5_pair) if n5_pair else None,
    }
    print(json.dumps(out))
    vs = {"CAL": cal, "ARB": arb}
    print(json.dumps(vs))
    print("VERDICTS " + json.dumps(vs, sort_keys=True))


if __name__ == "__main__":
    main()
