#!/usr/bin/env python3
"""W8 arm-6 ladder growth (SON-5138) — first stride of the
RESUMED census ladder, executing the named next action of
`research-log/2026-10-10-w8-pooling-premise-live-recheck.md`
verbatim: grow toward the k_line_prac=1524 attribution target with
the reserved stride-block arms, first arm = arm-6, seeds
340261107 + [0,153), never run before this job.

Premise state (tick 98, arbitration): arm-5 pairwise arbitration
resolved the tick-97 POOLING_CONTESTED receipt in favour of (S)
ARM4_SMALLN — arm-level shares are consistent with one w8 rate —
so the iid pooling premise behind the census ladder is RESTORED at
arm level, the pooled line datum 481/653 is claimable, and the
ladder resumes mechanically.  The tick-96 w8 REFUTED verdict is
unchanged by anything here.

Instrument: VERBATIM ktam_w8_arb5.py / ktam_w8_growth.py /
ktam_w8_hazardhold.py (same BUILD1 Vp-missing protocol, same s2
lock-read arithmetic, same run_traj — DW9's function VERBATIM, no
RNG-order change — same WIN_MULT=8 read window, same CAL identity
gate):

  CAL   seeds 260261107 + i, i in [0,500) — DW9's exact seeds
        (arm 2 of the reserved stride block).  UNCHANGED.
  ARM6  seeds 340261107 + i, i in [0,153) — arm 6 of the reserved
        stride block (220261107 + 6*2e7), NEVER run before this
        job.  n=153 is the frozen stride of the named action.

PRE-REGISTERED dispersion gate at the new pool size (frozen before
submission; leave-one-out convention VERBATIM
tools/w8_dispersion_receipt.py, constants duplicated here on
purpose so the instrument is self-contained; the test suite
identity-pins the two copies):

  x6     = arm-6 terminal pair census D2T count, denominator
           n6 = D2T + L2 (pair terminals; non-pair reported).
  pool   = line arms [(375,500), (106,153), (x6, n6)]
           (tick-96 arm-3 datum, tick-97 arm-4 datum, arm-6).
           Arm-5 (370/500) is NOT a line arm: it was the tick-98
           arbitration instrument and stays out of the ladder pool.
  gate   = min over arms of exact_two_sided_p(k_i, loo_pooled_phat,
           x_i), alpha = 0.05 (fixed now, before the datum)

  Branch map (mechanical, exhaustive, no default arm):
    CAL_FAIL                       -> VOID (instrument, not science)
    n6 < 50 (MIN_EVENTS floor)     -> NO_EVENTS
    min_exact_p <  alpha           -> POOLING_CONTESTED
    min_exact_p >= alpha           -> POOLING_CONTINUES

  POOLING_CONTINUES: the new pooled line datum (481+x6)/(653+n6)
  is claimable as one binomial census and the ladder keeps growing
  toward k_line_prac=1524 (next arm named by the frozen policy
  rerun at collection; R3 window [1123,1162] at k=1524).
  POOLING_CONTESTED: stop blind growth; next step is a fresh
  n=500 arbitration arm over the contested pair (tick-98 pattern),
  arm-level reporting meanwhile.

  Measured branch windows at n6=153 (formula output, pre-registered
  as descriptive context): POOLING_CONTINUES for x6 in [112, 122];
  POOLING_CONTESTED for x6 <= 111 or x6 >= 123.  Binder arm: arm-6
  (vs the 481/653 pool) low, arm-4 high — arm-3 never binds first.

Descriptive (labelled, no gates): arm-6 Wilson-95 alone; the new
pooled line datum with Wilson-95; the committed census-policy tool
rerun on the new pooled datum at collection (grow / window reading
— the frozen policy stays the only verdict surface).

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
N_CAL = 8 if os.environ.get("SMOKE") else 500
N_ARM6 = 8 if os.environ.get("SMOKE") else 153
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
POOL_X = ARM3_X + ARM4_X       # 481 — the claimable pooled line datum
POOL_K = ARM3_K + ARM4_K       # 653
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


def dispersion_receipt(arms, alpha):
    """Leave-one-out per-arm exact dispersion receipt.
    VERBATIM tools/w8_dispersion_receipt.py receipt() (duplication
    on purpose; the test suite identity-pins the two copies)."""
    sum_x = sum(x for x, _ in arms)
    sum_k = sum(k for _, k in arms)
    pooled = sum_x / sum_k
    rows = []
    for i, (x, k) in enumerate(arms):
        loo_x = sum_x - x
        loo_k = sum_k - k
        loo_p = loo_x / loo_k if loo_k > 0 else float("nan")
        p_i = exact_two_sided_p(k, loo_p, x)
        rows.append(
            {
                "arm": i,
                "x": x,
                "k": k,
                "phat": x / k,
                "loo_pooled_phat": loo_p,
                "exact_two_sided_p": p_i,
            }
        )
    min_p = min(r["exact_two_sided_p"] for r in rows)
    verdict = "POOLING_CONTESTED" if min_p < alpha else "POOLING_SUPPORTED"
    return {
        "arms": len(arms),
        "pooled_phat": pooled,
        "alpha": alpha,
        "rows": rows,
        "min_exact_p": min_p,
        "verdict": verdict,
    }


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


def gate(n6_pair, x6):
    """Ladder dispersion gate, branch map pre-registered in the
    docstring: mechanical, exhaustive, no default arm.  Returns
    (branch, receipt_or_None); receipt None outside COUNTED regime.
    POOLING_CONTINUES is the ladder's name for the committed tool's
    POOLING_SUPPORTED verdict at the new pool size."""
    if n6_pair < MIN_EVENTS:
        return "NO_EVENTS", None
    rep = dispersion_receipt(
        [(ARM3_X, ARM3_K), (ARM4_X, ARM4_K), (x6, n6_pair)], ALPHA)
    if rep["min_exact_p"] < ALPHA:
        return "POOLING_CONTESTED", rep
    return "POOLING_CONTINUES", rep


def main():
    b1v = build_missing_species(BUILD1, "Vp")
    canon = canonical_assembly(BUILD1)
    cal_tr = [run_traj(b1v, matched_s2, canon, SEED0_CAL + i,
                       DG, WIN_MULT) for i in range(N_CAL)]
    ar_tr = [run_traj(b1v, matched_s2, canon, SEED0_ARM6 + i,
                      DG, WIN_MULT) for i in range(N_ARM6)]
    cal_mid = census(cal_tr, "mid")
    cal_term = census(cal_tr, "terminal")
    ar_mid = census(ar_tr, "mid")
    ar_term = census(ar_tr, "terminal")

    cal = ("CAL_OK" if (N_CAL != 500 or
                        (cal_mid["D2T"] == CAL_D2T and
                         cal_mid["L2"] == CAL_L2)) else "CAL_FAIL")

    x6 = ar_term["D2T"]
    n6_pair = ar_term["D2T"] + ar_term["L2"]
    branch = None
    rep = None
    if cal == "CAL_OK":
        branch, rep = gate(n6_pair, x6)
    else:
        branch = "VOID"

    pooled_x = POOL_X + x6
    pooled_k = POOL_K + n6_pair
    out = {
        "n_cal": N_CAL, "n_arm6": N_ARM6,
        "seed0_cal": SEED0_CAL, "seed0_arm6": SEED0_ARM6,
        "dg": DG, "win_mult": WIN_MULT,
        "t_mid_is_w4": True,
        "cal_mid_w4": cal_mid, "cal_terminal_w8": cal_term,
        "arm6_mid_w4": ar_mid, "arm6_terminal_w8": ar_term,
        "references": {"arm3": {"x": ARM3_X, "k": ARM3_K},
                       "arm4": {"x": ARM4_X, "k": ARM4_K},
                       "pool_pre": {"x": POOL_X, "k": POOL_K}},
        "gate": ({"min_exact_p": rep["min_exact_p"],
                  "alpha": rep["alpha"], "rows": rep["rows"],
                  "tool_verdict": rep["verdict"]} if rep else None),
        "branch": branch,
        "arm6_wilson95": wilson(x6, n6_pair) if n6_pair else None,
        "pooled_line_datum": {
            "x": pooled_x, "k": pooled_k,
            "share": (pooled_x / float(pooled_k)) if pooled_k else None,
            "wilson95": wilson(pooled_x, pooled_k) if pooled_k else None},
    }
    print(json.dumps(out))
    vs = {"CAL": cal, "GATE": branch}
    print(json.dumps(vs))
    print("VERDICTS " + json.dumps(vs, sort_keys=True))


if __name__ == "__main__":
    main()
