#!/usr/bin/env python3
"""W8 hazard-hold falsifier (tick 74, SON-4881) — executes the
falsifier pre-registered in designs/011 (tick 73, SON-4879), frozen
before submission:

  "A w8 window arm (BUILD1 Vp-missing, s2, dG=2, fresh seeds, n=500)
   whose measured fill share falls outside +/-0.05 of 0.834 refutes
   the hazard-hold extrapolation."

Protocol of record is VERBATIM DW9/DW10/VH (ktam_dw9_compound.py),
which is VERBATIM tick 47/63: BUILD1 Vp-missing, Gmc=9.5,
gse=Gmc-dG=7.5, s2 lock-read arithmetic (matched_s2 doubling),
canonical map from the FULL build, stability checked on every event.
Only change: read window 8x400*e^Gmc at dG=2 (WIN_MULT=8).  run_traj
below is DW9's function VERBATIM, log included, no RNG-order change:
with t_read doubled, the event stream up to t_mid = t_read/2 (the 4x
window) is bit-identical to DW9's stream, so the mid-window census
over DW9's own seeds must reproduce the tick-63 receipt EXACTLY.
All new science is in the read length, not the instrument.

Arms:
  CAL   seeds 260261107 + i, i in [0,500) — DW9's exact seeds
        (arm 2 of the reserved stride block).
  FRESH seeds 280261107 + i, i in [0,500) — arm 3 of the same
        reserved stride block (220261107 + 3*2e7), named the next
        fresh base in research-log/2026-10-08-dw9-compounding-chain.md
        S5 and never run before this job.

PRE-REGISTERED gates (frozen before submission; machine verdicts on
the final VERDICTS line):
  CAL instrument identity: mid-window (t = 4x window) pair census
      over the CAL arm must be EXACTLY D2T 367 : L2 131 out of 500
      (tick-63/DW9 receipt; the residual 2 are non-pair terminals).
      [any mismatch -> CAL_FAIL and W8 VOID: the instrument is not
      the tick-63 instrument]
  W8 hazard-hold: fresh-arm terminal (t = 8x window) fill share
      s = D2T/(D2T+L2).  HELD if |s - 0.83376| <= 0.05 (designs/011
      P3 chain w8 point, quoted "0.834" in the pre-registration).
      [> 0.05 REFUTED: the hazard-hold extrapolation is refuted
      exactly as pre-registered; pair terminals < 50 NO_EVENTS]

Descriptive (labelled, no gates): fresh-arm mid-window share (the
w4 point on fresh seeds; cross-check band vs the DW9/VH fresh w4
receipts 0.716/0.7379, +/-0.05), CAL-arm terminal share at w8 (not
a gate: those seeds are the fit population), Wilson 95% CI on the
fresh terminal share, distance to the hazard-95 bracket arm
0.81585 (a sensitivity arm, not a second prediction).

SMOKE=1 runs n=8 per arm (instrument check only; CAL skipped —
gates stay verbatim per the tick-43 lesson).
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
SEED0_CAL = BASE_SEED + 2 * SEED_STRIDE   # 260261107 (DW9 layout, arm 2)
SEED0_FRESH = BASE_SEED + 3 * SEED_STRIDE  # 280261107 (arm 3, never run)
N_PER_RANGE = 8 if os.environ.get("SMOKE") else 500
DG = 2.0
WIN_MULT = 8.0
SITE = (2, 2)                  # the Vp vacancy: fill/substitution site
FACE_DIR = {"E": (1, 0), "N": (0, 1), "S": (0, -1), "W": (-1, 0)}
CAL_D2T = 367
CAL_L2 = 131
PRED_W8 = 0.83376              # designs/011 P3 chain w8 point ("0.834")
BAND = 0.05
MIN_EVENTS = 50
HAZ95_ARM = 0.81585            # designs/011 hazard-95 bracket arm
DW9_FRESH_W4 = 0.716           # receipt: fresh-seed w4 share (DW9 CC3)
VH_FRESH_W4 = 0.7379032258064516  # receipt: VH held-out w4 share


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
                       DG, WIN_MULT) for i in range(N_PER_RANGE)]
    fr_tr = [run_traj(b1v, matched_s2, canon, SEED0_FRESH + i,
                      DG, WIN_MULT) for i in range(N_PER_RANGE)]
    cal_mid = census(cal_tr, "mid")
    cal_term = census(cal_tr, "terminal")
    fr_mid = census(fr_tr, "mid")
    fr_term = census(fr_tr, "terminal")

    cal = ("CAL_OK" if (N_PER_RANGE != 500 or
                        (cal_mid["D2T"] == CAL_D2T and
                         cal_mid["L2"] == CAL_L2)) else "CAL_FAIL")

    if fr_term["D2T"] + fr_term["L2"] < MIN_EVENTS:
        w8 = "NO_EVENTS"
        dev = None
    else:
        dev = abs(fr_term["share"] - PRED_W8)
        w8 = "HELD" if dev <= BAND else "REFUTED"
    if cal != "CAL_OK":
        w8 = "VOID"

    fresh_mid_dev = (abs(fr_mid["share"] - DW9_FRESH_W4)
                     if fr_mid["share"] is not None else None)
    out = {
        "n_per_range": N_PER_RANGE,
        "seed0_cal": SEED0_CAL, "seed0_fresh": SEED0_FRESH,
        "dg": DG, "win_mult": WIN_MULT,
        "t_mid_is_w4": True,
        "cal_mid_w4": cal_mid, "cal_terminal_w8": cal_term,
        "fresh_mid_w4": fr_mid, "fresh_terminal_w8": fr_term,
        "pred_w8": PRED_W8, "haz95_arm": HAZ95_ARM,
        "dev_fresh_w8": dev,
        "fresh_w8_wilson95": wilson(fr_term["D2T"],
                                    fr_term["D2T"] + fr_term["L2"]),
        "fresh_mid_w4_dev_vs_dw9_receipt": fresh_mid_dev,
        "receipts": {"dw9_fresh_w4": DW9_FRESH_W4,
                     "vh_heldout_w4": VH_FRESH_W4},
    }
    print(json.dumps(out))
    vs = {"CAL": cal, "W8": w8}
    print(json.dumps(vs))
    print("VERDICTS " + json.dumps(vs, sort_keys=True))


if __name__ == "__main__":
    main()
