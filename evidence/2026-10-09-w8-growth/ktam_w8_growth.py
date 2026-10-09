#!/usr/bin/env python3
"""W8 stage-1 growth census (tick 97, SON-4917) — executes the
pre-registered tick-92 census policy (tools/w8_census_policy.py)
on the tick-96 datum: fresh w8 375/500 = 0.75, Wilson-95
[0.71024, 0.78595], region-ambiguous -> stage-1 GROW to the line
census k=653 (R3, practical window [489, 491], x_line=490 under
phat=0.75; P(attribution at the line) 0.108).

Instrument: VERBATIM ktam_w8_hazardhold.py (the tick-77/96 job
ed50c7ba...4daa85, run.out sha256 cea9d335...) — same BUILD1
Vp-missing protocol, same s2 lock-read arithmetic, same run_traj
(DW9's function VERBATIM, no RNG-order change), same WIN_MULT=8
read window, same CAL identity gate.  The only changes are the
growth arm's seeds and size:

  CAL    seeds 260261107 + i, i in [0,500) — DW9's exact seeds
         (arm 2 of the reserved stride block).  UNCHANGED.
  GROWTH seeds 300261107 + i, i in [0,153) — arm 4 of the same
         reserved stride block (220261107 + 4*2e7), named the
         growth arm in the tick-96 collection note and never run
         before this job.  n=153 lands the pooled line census
         exactly at k = 500 + 153 = 653 (1 additional arm-budget
         of 2400 s; the ladder's cost accounting).

PRE-REGISTERED reading (frozen before submission; this job is a
CENSUS, not a falsifier — it carries NO HELD/REFUTED verdict):
  CAL instrument identity (unchanged gate): mid-window pair census
      over the CAL arm must be EXACTLY D2T 367 : L2 131 out of 500.
      [mismatch -> CAL_FAIL and the census VOID]
  Growth datum: arm-4 terminal pair census x4 = D2T count (pair
      denominator D2T+L2; non-pair terminals reported).  Pooled
      line census: x2 = 375 + x4 out of k2 = 653 total terminals.
      Collection-day reading is MECHANICAL via the frozen ladder:
      tools/w8_census_policy.policy(375 + x4, 653) — verdict-ready
      (Wilson-95 inside one region), grow again, or stage-2 — and
      the tick-93 dispersion receipt runs on arms
      [(375,500),(x4,153)] BEFORE any pooling claim.  This harness
      never reads regions and never verdicts.
  Expected window under phat=0.75 (pre-registered, receipt-side):
      E[x4] = 114.75; the pooled line window [489,491] is x4 in
      {114,115,116}.  P(Bin(653,0.75) in window) = 0.108 — an
      out-of-window datum is NOT protocol failure; the ladder
      reads it (pre-registered tick 92).

Descriptive (labelled, no gates): arm-4 Wilson-95 alone, pooled
Wilson-95, CAL-arm terminal census (fit population, not a gate).

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
SEED0_GROWTH = BASE_SEED + 4 * SEED_STRIDE  # 300261107 (arm 4, never run)
N_CAL = 8 if os.environ.get("SMOKE") else 500
N_GROWTH = 8 if os.environ.get("SMOKE") else 153
DG = 2.0
WIN_MULT = 8.0
SITE = (2, 2)                  # the Vp vacancy: fill/substitution site
FACE_DIR = {"E": (1, 0), "N": (0, 1), "S": (0, -1), "W": (-1, 0)}
CAL_D2T = 367
CAL_L2 = 131
MIN_EVENTS = 50
DATUM_D2T = 375                # tick-96 receipt: arm-3 w8 terminal census
DATUM_K = 500                  # 375 D2T + 125 L2, other = 0
PHAT = 0.75                    # MLE of the datum; the ladder's pricing p
K_LINE = 653                   # tick-92 policy on (375,500): stage-1 line
X_LINE = 490                   # round(phat * k_line), ties away from zero
R3_WINDOW = (489, 491)         # policy practical window at the line k


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


def main():
    b1v = build_missing_species(BUILD1, "Vp")
    canon = canonical_assembly(BUILD1)
    cal_tr = [run_traj(b1v, matched_s2, canon, SEED0_CAL + i,
                       DG, WIN_MULT) for i in range(N_CAL)]
    gr_tr = [run_traj(b1v, matched_s2, canon, SEED0_GROWTH + i,
                      DG, WIN_MULT) for i in range(N_GROWTH)]
    cal_mid = census(cal_tr, "mid")
    cal_term = census(cal_tr, "terminal")
    gr_mid = census(gr_tr, "mid")
    gr_term = census(gr_tr, "terminal")

    cal = ("CAL_OK" if (N_CAL != 500 or
                        (cal_mid["D2T"] == CAL_D2T and
                         cal_mid["L2"] == CAL_L2)) else "CAL_FAIL")

    # Census, not falsifier: no HELD/REFUTED here.  The reading is
    # the frozen ladder's job at collection (see docstring); this
    # block only refuses to hand a count to it when the arm is
    # degenerate or the instrument failed identity.
    x4 = gr_term["D2T"]
    n4_pair = gr_term["D2T"] + gr_term["L2"]
    if cal != "CAL_OK":
        growth = "VOID"
    elif n4_pair < MIN_EVENTS:
        growth = "NO_EVENTS"
    else:
        growth = "COUNTED"

    out = {
        "n_cal": N_CAL, "n_growth": N_GROWTH,
        "seed0_cal": SEED0_CAL, "seed0_growth": SEED0_GROWTH,
        "dg": DG, "win_mult": WIN_MULT,
        "t_mid_is_w4": True,
        "cal_mid_w4": cal_mid, "cal_terminal_w8": cal_term,
        "growth_mid_w4": gr_mid, "growth_terminal_w8": gr_term,
        "datum": {"d2t": DATUM_D2T, "k": DATUM_K},
        "line": {"k": K_LINE, "x_line": X_LINE,
                 "window": list(R3_WINDOW), "phat": PHAT},
        "pooled": {"x2": DATUM_D2T + x4, "k2": DATUM_K + N_GROWTH,
                   "wilson95": wilson(DATUM_D2T + x4,
                                      DATUM_K + N_GROWTH)},
        "growth_wilson95": wilson(x4, n4_pair) if n4_pair else None,
        "expected_x4_under_phat": PHAT * N_GROWTH,
    }
    print(json.dumps(out))
    vs = {"CAL": cal, "GROWTH": growth}
    print(json.dumps(vs))
    print("VERDICTS " + json.dumps(vs, sort_keys=True))


if __name__ == "__main__":
    main()
