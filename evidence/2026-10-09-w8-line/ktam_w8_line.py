#!/usr/bin/env python3
"""W8 stage-1 LINE CENSUS (tick 99, SON-4922) — grows the claimable
pooled w8 datum from 481/653 to the policy line k=1524.

Context (receipts): tick 96 measured w8 arm-3 375/500 and REFUTED
hazard-hold; tick 97 grew with arm-4 106/153 and the dispersion
receipt fired POOLING_CONTESTED; tick 98's arm-5 370/500 pairwise
arbitration returned ARM4_SMALLN — the arm-4 gap was a small-n
artifact, the 3-arm dispersion receipt reads POOLING_SUPPORTED
(min_exact_p 1.385823e-1), and the pooled line datum 481/653
became claimable.  The tick-92 census policy recomputed on
(481, 653) BEFORE this harness was written names the next step
mechanically:

    first census: x=481 / k=653 -> Wilson-95 CI [0.70150, 0.76893]
      region-ambiguous (crosses an edge) -> stage-1 growth policy:
        line k=1524, x_line=1123, region R3
        practical window at line k: [1123, 1162]
        cost: 2 additional arm(s) x 2400 s; pooled census 4 arms total
      attribution probability AT the line census: 0.494
      P>=0.80 (stage-2 decisive census) at k=3090 (7 arms)

Instrument: VERBATIM ktam_w8_arb5.py / ktam_w8_growth.py /
ktam_w8_hazardhold.py (same BUILD1 Vp-missing protocol, same s2
lock-read arithmetic, same run_traj — DW9's function VERBATIM, no
RNG-order change — same WIN_MULT=8 read window, same CAL gate):

  CAL   seeds 260261107 + i, i in [0,500) — DW9's exact seeds
        (arm 2 of the reserved stride block).  UNCHANGED.  This is
        the next queued run of the identity chain
        DW9 -> VH -> w8 -> growth -> arb5 -> here; the mid-window
        census must read exactly 367:131.
  ARM6  seeds 340261107 + i, i in [0,500) — arm 6 of the reserved
        stride block, NEVER run before this job (grep-verified).
  ARM7  seeds 360261107 + i, i in [0,500) — arm 7 of the reserved
        stride block, NEVER run before this job (grep-verified).

Two full arms (not an 871-terminal partial) because the policy's
own cost model prices whole arms; pooled k becomes 653+500+500 =
1653 >= k_line 1524, and the region reading is recomputed at the
OBSERVED pooled k at collection — no region constants live in this
instrument (pre-registered: region arithmetic belongs to the frozen
atlas/policy tools only).

PRE-REGISTERED line reading (frozen before submission):

  x6, x7     = per-arm terminal pair census D2T counts, denominators
               n6 = D2T + L2, n7 = D2T + L2 (pair terminals;
               non-pair reported).
  dispersion = leave-one-out exact two-sided binomial tests over the
               4-arm set [(375,500),(106,153),(x6,n6),(x7,n7)]
               (point-probability method, log-space — VERBATIM
               tools/w8_dispersion_receipt.py, duplicated here on
               purpose so the instrument is self-contained; the
               duplicate is pinned against that tool's tick-93/98
               receipt numbers in tests/test_w8_line.py).
  alpha      = 0.05 (fixed now, before the datum).

  Branch map (mechanical, exhaustive, no default arm):
    CAL_FAIL                     -> VOID (instrument, not science)
    n6 < 50 or n7 < 50           -> NO_EVENTS (arm-level reporting
                                   only; pooled line not formed)
    min_exact_p <  alpha         -> POOLING_CONTESTED (pooled
                                   attribution NOT claimable; next
                                   step = block-mechanism probe,
                                   never blind growth)
    else                         -> SUPPORTED_LINE: pooled
                                   (x, k) = (481+x6+x7, 653+n6+n7)
                                   is the claimable line datum; the
                                   frozen atlas reads it at
                                   collection (inside one region ->
                                   VERDICT-READY, ladder stops;
                                   ambiguous -> stage 2 named
                                   mechanically by the policy tool
                                   from the observed pooled phat).

Descriptive (labelled, no gates): per-arm Wilson-95; pairwise exact
p of each new arm vs each of arms 3/4/5; pooled Wilson-95.

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
SEED0_ARM6 = BASE_SEED + 6 * SEED_STRIDE  # 340261107 (arm 6, never run)
SEED0_ARM7 = BASE_SEED + 7 * SEED_STRIDE  # 360261107 (arm 7, never run)
N_CAL = 8 if os.environ.get("SMOKE") else 500
N_ARM6 = 8 if os.environ.get("SMOKE") else 500
N_ARM7 = 8 if os.environ.get("SMOKE") else 500
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
ARM5_X = 370                   # tick-98 receipt: arm-5 w8 terminal census
ARM5_K = 500                   # 370 D2T + 130 L2, other = 0
POOL_X_REF = ARM3_X + ARM4_X   # 481 — tick-97 pooled, claimable post tick 98
POOL_K_REF = ARM3_K + ARM4_K   # 653
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


def dispersion_min_p(arms):
    """Leave-one-out exact two-sided p per arm vs the pooled rest.
    Semantics VERBATIM tools/w8_dispersion_receipt.py (tick 93):
    p_i = exact_two_sided_p(k_i, p_rest, x_i) with p_rest estimated
    from the OTHER arms pooled.  Returns (min_p, per-arm list)."""
    X = sum(x for x, _ in arms)
    K = sum(k for _, k in arms)
    ps = []
    for x, k in arms:
        p_rest = (X - x) / float(K - k)
        ps.append(exact_two_sided_p(k, p_rest, x))
    return min(ps), ps


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


def line_reading(n6, x6, n7, x7):
    """Line-census branch map pre-registered in the docstring:
    mechanical, exhaustive, no default arm.  Returns (branch,
    min_exact_p, per-arm p list, pooled summary)."""
    if n6 < MIN_EVENTS or n7 < MIN_EVENTS:
        return "NO_EVENTS", None, None, None
    min_p, ps = dispersion_min_p(
        [(ARM3_X, ARM3_K), (ARM4_X, ARM4_K), (x6, n6), (x7, n7)])
    px = POOL_X_REF + x6 + x7
    pk = POOL_K_REF + n6 + n7
    pooled = {"x": px, "k": pk, "share": px / float(pk),
              "wilson95": wilson(px, pk)}
    if min_p < ALPHA:
        return "POOLING_CONTESTED", min_p, ps, pooled
    return "SUPPORTED_LINE", min_p, ps, pooled


def main():
    b1v = build_missing_species(BUILD1, "Vp")
    canon = canonical_assembly(BUILD1)
    cal_tr = [run_traj(b1v, matched_s2, canon, SEED0_CAL + i,
                       DG, WIN_MULT) for i in range(N_CAL)]
    a6_tr = [run_traj(b1v, matched_s2, canon, SEED0_ARM6 + i,
                      DG, WIN_MULT) for i in range(N_ARM6)]
    a7_tr = [run_traj(b1v, matched_s2, canon, SEED0_ARM7 + i,
                      DG, WIN_MULT) for i in range(N_ARM7)]
    cal_mid = census(cal_tr, "mid")
    cal_term = census(cal_tr, "terminal")
    a6_mid = census(a6_tr, "mid")
    a6_term = census(a6_tr, "terminal")
    a7_mid = census(a7_tr, "mid")
    a7_term = census(a7_tr, "terminal")

    cal = ("CAL_OK" if (N_CAL != 500 or
                        (cal_mid["D2T"] == CAL_D2T and
                         cal_mid["L2"] == CAL_L2)) else "CAL_FAIL")

    x6 = a6_term["D2T"]
    n6_pair = a6_term["D2T"] + a6_term["L2"]
    x7 = a7_term["D2T"]
    n7_pair = a7_term["D2T"] + a7_term["L2"]

    branch = min_p = ps = pooled = None
    if cal == "CAL_OK":
        branch, min_p, ps, pooled = line_reading(n6_pair, x6, n7_pair, x7)
    else:
        branch = "VOID"

    def pairwise(n, x):
        if n < MIN_EVENTS:
            return None
        return {"p3": exact_two_sided_p(n, ARM3_X / float(ARM3_K), x),
                "p4": exact_two_sided_p(n, ARM4_X / float(ARM4_K), x),
                "p5": exact_two_sided_p(n, ARM5_X / float(ARM5_K), x)}

    out = {
        "n_cal": N_CAL, "n_arm6": N_ARM6, "n_arm7": N_ARM7,
        "seed0_cal": SEED0_CAL, "seed0_arm6": SEED0_ARM6,
        "seed0_arm7": SEED0_ARM7,
        "dg": DG, "win_mult": WIN_MULT,
        "t_mid_is_w4": True,
        "cal_mid_w4": cal_mid, "cal_terminal_w8": cal_term,
        "arm6_mid_w4": a6_mid, "arm6_terminal_w8": a6_term,
        "arm7_mid_w4": a7_mid, "arm7_terminal_w8": a7_term,
        "references": {"arm3": {"x": ARM3_X, "k": ARM3_K},
                       "arm4": {"x": ARM4_X, "k": ARM4_K},
                       "arm5": {"x": ARM5_X, "k": ARM5_K},
                       "pooled_ref": {"x": POOL_X_REF, "k": POOL_K_REF}},
        "pairwise_arm6": pairwise(n6_pair, x6),
        "pairwise_arm7": pairwise(n7_pair, x7),
        "dispersion": {"min_exact_p": min_p, "per_arm": ps,
                       "alpha": ALPHA},
        "branch": branch, "pooled_line": pooled,
        "arm6_wilson95": wilson(x6, n6_pair) if n6_pair else None,
        "arm7_wilson95": wilson(x7, n7_pair) if n7_pair else None,
    }
    print(json.dumps(out))
    vs = {"CAL": cal, "LINE": branch}
    print(json.dumps(vs))
    print("VERDICTS " + json.dumps(vs, sort_keys=True))


if __name__ == "__main__":
    main()
