#!/usr/bin/env python3
"""W8 BLOCK-MECHANISM PROBE (tick 100 pre-registration) — is arm-6's
elevation block structure or window noise?

Context (receipts): tick 99 (SON-4922, adopted by SON-4928) grew the
pooled w8 line census with arms 6 and 7: arm-6 340261107+[0,500) read
389/500 = 0.778 and arm-7 360261107+[0,500) read 365/499 = 0.73146.
The pre-registered 4-arm leave-one-out dispersion receipt fired
POOLING_CONTESTED (min_exact_p 2.932581e-02; driver arm-6, 0.778 vs
LOO pool 0.734375), so the pooled line datum 1235/1652 is reported
but NOT claimable, and the frozen branch map names the next step:
a block-mechanism probe, never blind growth.

The question this probe arbitrates, stated before any datum:
  account A (window noise): arm-6's elevation is one window's binomial
    fluctuation; under iid the family-wise firing probability of four
    correlated alpha-0.05 leave-one-out tests is ~15-20%, and 0.0293
    is exactly the kind of minimum such a family produces.  Prediction:
    an ADJACENT window in the SAME seed block returns to the family
    mean (~0.7405).
  account B (block structure): the 340261107 block runs hot as a
    block.  Prediction: the adjacent window in the same block stays
    high (~0.778).

Discriminating arms (both NEVER run; grep-verified in
tests/test_w8_blockprobe.py):
  ARM6B seeds 340261107 + 500 + i, i in [0,500) — arm 6's OWN block,
        the NEXT 500-seed window [500,1000).  Same block, fresh window:
        separates block-level from window-level.
  ARM8  seeds 350261107 + i, i in [0,500) — the never-used mid-stride
        gap between blocks 6 and 7 (BASE + 6.5 strides).  Any-window
        control: does an arbitrary unaligned window behave like the
        family?

Reference set (fixed from committed receipts BEFORE the probe):
  arm6    (389, 500)  — tick-99 run.out, sha256 fe7be746
  family  (1110, 1499) = arms 3+5+7 pooled: 375/500 + 370/500 +
          365/499 — the full-n arms only; arm-4 (106/153) is excluded
          per tick-98's ARM4_SMALLN adjudication and stays excluded.
  family phat = 0.7404936624416278.

PRE-REGISTERED probe reading (frozen before submission; mechanical,
exhaustive, no default arm):

  x6b, x8  = per-arm terminal pair-census D2T counts, denominators
             n6b = D2T + L2, n8 = D2T + L2 (pair terminals only).
  q6  = exact_two_sided_p(n6b, 389/500, x6b)      same-block consistency
  qF6 = exact_two_sided_p(n6b, 1110/1499, x6b)    family consistency
  qF8 = exact_two_sided_p(n8,  1110/1499, x8)     control arm vs family
  alpha = 0.05 (fixed now, before the datum).

  Branch map on (q6, qF6), with qF8 recorded alongside:
    CAL_FAIL                  -> VOID (instrument, not science)
    n6b < 50 or n8 < 50       -> NO_EVENTS
    q6 >= a and qF6 < a       -> BLOCK_STRUCTURE (6b reproduces arm-6's
                                 elevation: block-level heterogeneity;
                                 pooling across stride blocks structur-
                                 ally unsafe; family estimates go per-
                                 block; census-ladder pooling premise
                                 downgraded — this is the major finding)
    qF6 >= a and q6 < a       -> WINDOW_NOISE (6b returns to family,
                                 inconsistent with arm-6: arm-6's
                                 elevation was window-level; pooling
                                 premise restored at family level —
                                 the tick-98 ARM4_SMALLN pattern one
                                 level up)
    q6 >= a and qF6 >= a      -> AMBIG_MIDDLE (6b consistent with BOTH:
                                 underpowered; both accounts stand;
                                 no claim change until a future claim
                                 needs the family pool)
    q6 < a and qF6 < a        -> OUTSIDE_BOTH (6b outside both arm-6 and
                                 family: neither account predicted it;
                                 per-window heavy tails recorded, no
                                 account promoted)
  Control reading (recorded, never overrides the primary map):
    qF8 < a                   -> HOT_NEIGHBORHOOD if x8/n8 > 0.7405
                                 (COLD_NEIGHBORHOOD if below): the
                                 unaligned gap window deviates from the
                                 family — independent structure signal
                                 that the collection-day chain weighs
                                 WITH the primary branch.
  Descriptive (labelled, no gates): per-arm Wilson-95; pairwise exact
  tests of 6b and 8 vs arms 3, 5, 7 individually; 6-arm leave-one-out
  dispersion over [(375,500),(370,500),(389,500),(365,499),(x6b,n6b),
  (x8,n8)] — VERBATIM tools/w8_dispersion_receipt.py arithmetic,
  duplicated on purpose so the instrument is self-contained; the
  duplicate is pinned against that tool's committed receipts in
  tests/test_w8_blockprobe.py.

Honest boundaries, stated before the datum:
  - Two fresh arms are two more tests; the primary map is exhaustive
    over the (q6, qF6) sign pattern and the control is recorded as a
    label, so no unplanned comparison can be promoted post hoc.
  - AMBIG_MIDDLE is a real outcome, not protocol failure: a 6b share
    between ~0.74 and ~0.78 is genuinely consistent with both arms at
    n=500 and the honest reading is underpowered.
  - This probe adjudicates the OBSERVED arm-6 elevation only; block
    effects smaller than ~0.02-0.03 in rate remain undetectable at
    n=500 per arm (tick-98 boundary, carried forward).

Instrument identity: VERBATIM ktam_w8_line.py / arb5 / growth /
hazardhold (same BUILD1 Vp-missing protocol, same s2 lock-read
arithmetic, same run_traj — DW9's function verbatim, RNG order
unchanged — same WIN_MULT=8 window, same CAL identity gate:
260261107 must read exactly 367:131 at the w4 mid-window census,
the next link of the DW9 -> VH -> w8 -> growth -> arb5 -> line ->
here chain).  Arms 6B and 8 replace arms 6 and 7; everything else is
identical except the docstring, the reference constants, and the
probe reading map above.
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
SEED0_CAL = BASE_SEED + 2 * SEED_STRIDE      # 260261107 (DW9 layout)
SEED0_ARM6B = BASE_SEED + 6 * SEED_STRIDE + 500   # 340261607 (6's block, NEXT window)
SEED0_ARM8 = BASE_SEED + 13 * (SEED_STRIDE // 2)   # 350261107 (mid-stride gap, never run)
N_CAL = 8 if os.environ.get("SMOKE") else 500
N_ARM6B = 8 if os.environ.get("SMOKE") else 500
N_ARM8 = 8 if os.environ.get("SMOKE") else 500
DG = 2.0
WIN_MULT = 8.0
SITE = (2, 2)                  # the Vp vacancy: fill/substitution site
FACE_DIR = {"E": (1, 0), "N": (0, 1), "S": (0, -1), "W": (-1, 0)}
CAL_D2T = 367
CAL_L2 = 131
MIN_EVENTS = 50
ARM3_X = 375                   # tick-96 receipt
ARM3_K = 500
ARM4_X = 106                   # tick-97 receipt (excluded from family per t98)
ARM4_K = 153
ARM5_X = 370                   # tick-98 receipt
ARM5_K = 500
ARM6_X = 389                   # tick-99 receipt (run.out fe7be746)
ARM6_K = 500
ARM7_X = 365                   # tick-99 receipt (n=499: one non-pair terminal)
ARM7_K = 499
FAM_X = ARM3_X + ARM5_X + ARM7_X   # 1110 = family pool, full-n arms
FAM_K = ARM3_K + ARM5_K + ARM7_K   # 1499
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


def wilson(k, n, z=1.96):
    if not n:
        return None
    p = k / float(n)
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 5), round(c + h, 5)]


def probe_reading(n6b, x6b, n8, x8):
    """Probe branch map pre-registered in the docstring: mechanical,
    exhaustive, no default arm.  Returns (branch, tests, control,
    dispersion6)."""
    if n6b < MIN_EVENTS or n8 < MIN_EVENTS:
        return "NO_EVENTS", None, None, None
    q6 = exact_two_sided_p(n6b, ARM6_X / float(ARM6_K), x6b)
    qF6 = exact_two_sided_p(n6b, FAM_X / float(FAM_K), x6b)
    qF8 = exact_two_sided_p(n8, FAM_X / float(FAM_K), x8)
    if q6 >= ALPHA and qF6 < ALPHA:
        branch = "BLOCK_STRUCTURE"
    elif qF6 >= ALPHA and q6 < ALPHA:
        branch = "WINDOW_NOISE"
    elif q6 >= ALPHA and qF6 >= ALPHA:
        branch = "AMBIG_MIDDLE"
    else:
        branch = "OUTSIDE_BOTH"
    control = "HOT_NEIGHBORHOOD" if (qF8 < ALPHA and
                                     x8 / float(n8) > FAM_X / float(FAM_K)) \
        else ("COLD_NEIGHBORHOOD" if qF8 < ALPHA else "FAMILY_CONSISTENT")
    min_p, ps = dispersion_min_p(
        [(ARM3_X, ARM3_K), (ARM5_X, ARM5_K), (ARM6_X, ARM6_K),
         (ARM7_X, ARM7_K), (x6b, n6b), (x8, n8)])
    tests = {"q6": q6, "qF6": qF6, "qF8": qF8, "alpha": ALPHA}
    return branch, tests, control, {"min_exact_p": min_p, "per_arm": ps}


def main():
    b1v = build_missing_species(BUILD1, "Vp")
    canon = canonical_assembly(BUILD1)
    cal_tr = [run_traj(b1v, matched_s2, canon, SEED0_CAL + i,
                       DG, WIN_MULT) for i in range(N_CAL)]
    a6b_tr = [run_traj(b1v, matched_s2, canon, SEED0_ARM6B + i,
                       DG, WIN_MULT) for i in range(N_ARM6B)]
    a8_tr = [run_traj(b1v, matched_s2, canon, SEED0_ARM8 + i,
                      DG, WIN_MULT) for i in range(N_ARM8)]
    cal_mid = census(cal_tr, "mid")
    cal_term = census(cal_tr, "terminal")
    a6b_mid = census(a6b_tr, "mid")
    a6b_term = census(a6b_tr, "terminal")
    a8_mid = census(a8_tr, "mid")
    a8_term = census(a8_tr, "terminal")

    cal = ("CAL_OK" if (N_CAL != 500 or
                        (cal_mid["D2T"] == CAL_D2T and
                         cal_mid["L2"] == CAL_L2)) else "CAL_FAIL")

    x6b = a6b_term["D2T"]
    n6b_pair = a6b_term["D2T"] + a6b_term["L2"]
    x8 = a8_term["D2T"]
    n8_pair = a8_term["D2T"] + a8_term["L2"]

    branch = tests = control = disp6 = None
    if cal == "CAL_OK":
        branch, tests, control, disp6 = probe_reading(
            n6b_pair, x6b, n8_pair, x8)
    else:
        branch = "VOID"

    def pairwise(n, x):
        if n < MIN_EVENTS:
            return None
        return {"p3": exact_two_sided_p(n, ARM3_X / float(ARM3_K), x),
                "p5": exact_two_sided_p(n, ARM5_X / float(ARM5_K), x),
                "p6": exact_two_sided_p(n, ARM6_X / float(ARM6_K), x),
                "p7": exact_two_sided_p(n, ARM7_X / float(ARM7_K), x)}

    out = {
        "n_cal": N_CAL, "n_arm6b": N_ARM6B, "n_arm8": N_ARM8,
        "seed0_cal": SEED0_CAL, "seed0_arm6b": SEED0_ARM6B,
        "seed0_arm8": SEED0_ARM8,
        "dg": DG, "win_mult": WIN_MULT,
        "t_mid_is_w4": True,
        "cal_mid_w4": cal_mid, "cal_terminal_w8": cal_term,
        "arm6b_mid_w4": a6b_mid, "arm6b_terminal_w8": a6b_term,
        "arm8_mid_w4": a8_mid, "arm8_terminal_w8": a8_term,
        "references": {"arm3": {"x": ARM3_X, "k": ARM3_K},
                       "arm4_excluded": {"x": ARM4_X, "k": ARM4_K},
                       "arm5": {"x": ARM5_X, "k": ARM5_K},
                       "arm6": {"x": ARM6_X, "k": ARM6_K},
                       "arm7": {"x": ARM7_X, "k": ARM7_K},
                       "family": {"x": FAM_X, "k": FAM_K}},
        "pairwise_arm6b": pairwise(n6b_pair, x6b),
        "pairwise_arm8": pairwise(n8_pair, x8),
        "probe_tests": tests, "control_arm8": control,
        "dispersion6": disp6,
        "branch": branch,
        "arm6b_wilson95": wilson(x6b, n6b_pair) if n6b_pair else None,
        "arm8_wilson95": wilson(x8, n8_pair) if n8_pair else None,
    }
    print(json.dumps(out))
    vs = {"CAL": cal, "PROBE": branch}
    print(json.dumps(vs))
    print("VERDICTS " + json.dumps(vs, sort_keys=True))


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




if __name__ == "__main__":
    main()
