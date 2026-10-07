#!/usr/bin/env python3
"""Contention dG/read-window sweep (tick 43, SON-4813) — the tick-42
queued item: WHEN does first-come contention stop matter?

Tick 42 priced the minted contention set at dG 0.5: BUILD1
Vp-missing, family fill share 0.908 vs s2 0.406, five frozen
contenders {D1T, D2T, DBr, L2, V0p} at the (2,2) vacancy.  This
sweep puts that finding on the dG and read-window axes.  Physics
of the protocol of record (Gmc=9.5, gse=Gmc-dG, T_read =
mult*e^Gmc): a b=2 tile's lifetime is e^(2*gse) against a fixed
window ~400*e^9.5 — frozen at dG 0.5 (lifetime 12x the window),
marginal at dG 2 (~1.6 detachments/window), churning at dG 4
(~90 detachments/window).  Prediction under test: the s2 fill
share RECOVERS with dG because frozen first-come squatters become
re-rollable transients, and a longer read window accelerates that
recovery; the family channel is window- and dG-robust.

Arms (n=500, protocol of tick 38/41, canonical map kept from the
FULL build): fam/s2 x dG 0.5/2/4, s2 dG 7 (starvation boundary,
descriptive band), and two 4x-window arms at dG 4 (s2 + family
control).  Fresh seed base 200261107 stride 2e7 (disjoint from
20261107 / 40261107 / 80261107 / 100261107 / 120261107 /
160261107 / 180261107 — grepped against evidence/ research-log/
log/ 2026-10-07).  SMOKE=1 runs n=8/arm (instrument check only).

PRE-REGISTERED gates (falsifiers in brackets; fixed before
submission; machine verdicts on the final VERDICTS line):
  DW1 calibration: fam_dg0.5 fill within 0.07 of 0.908 AND
      s2_dg0.5 fill within 0.07 of 0.406 (tick-42 refs)
      [either >= 0.10 off FALSIFIED: protocol drift — stop reading]
  DW2 fill recovery: s2_dg4 fill >= s2_dg0.5 fill + 0.15
      [gain <= 0.05 FALSIFIED: minting persists window-wide;
       middle band INCONCLUSIVE]
  DW3 churn mechanism: s2 west-site churn per read at dG 4
      >= 5x the dG 0.5 churn [ratio < 2 FALSIFIED: recovery is
      not churn-driven; middle INCONCLUSIVE]
  DW4 first-come stickiness: first-stable persistence at
      s2_dg0.5 >= 0.8 AND exceeds s2_dg4 persistence by >= 0.15
      [persistence(4) >= persistence(0.5) - 0.05 FALSIFIED:
       first-come is not the low-dG mechanism; middle INCONCLUSIVE]
  DW5 window axis: s2_dg4_win4 fill >= s2_dg4 fill + 0.10
      [gain < 0.03 FALSIFIED: contention is window-independent;
       middle INCONCLUSIVE]
  DW6 family floor: every family arm fill >= 0.70
      [any < 0.70 FALSIFIED: the family channel degrades too —
       a finding about dG, not about the knob]
  DW7 starvation boundary (s2_dg7, band): fill <= 0.25
      CONFIRMED (growth starvation dominates, tick-15/22 echo);
      fill > 0.60 counts as RECOVERY-BEYOND (falsifies the
      starvation expectation); middle INCONCLUSIVE.
fam_dg4_win4 is a window control (no gate): family should be
window-neutral.
"""
import json
import math
import os
import random
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SIB_AND = os.path.join(os.path.dirname(HERE),
                       "2026-10-06-body-conjunction-builds")
SIB_DEATH = os.path.join(os.path.dirname(HERE),
                         "2026-10-06-structural-death")
for p in (HERE, REPO, SIB_AND, SIB_DEATH):
    if p not in sys.path:
        sys.path.insert(0, p)

from tiles_and import BUILD1                          # noqa: E402
from tiles_death import build_missing_species         # noqa: E402
from molasp.offchannel import (canonical_assembly,    # noqa: E402
                               matched_strength)

GMC = 9.5
BASE_SEED = 200261107
SEED_STRIDE = 20000000
N_PER_ARM = 8 if os.environ.get("SMOKE") else 500
FACE_DIR = {"E": (1, 0), "N": (0, 1), "S": (0, -1), "W": (-1, 0)}
REFS = {"fam_fill_05": 0.908, "s2_fill_05": 0.406}
SITE = (2, 2)          # the Vp vacancy: fill/substitution site
CANON_SITES = None     # set once main() builds the canonical map


def matched_s2(build, asm, site, tile_name):
    """Family matched strength with the lock-read bond doubled
    (verbatim tick-38/41 arithmetic)."""
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
    """One trajectory, protocol of record.  Vacancy bookkeeping at
    SITE: occupancy-change count (churn), first stable-b>=2
    occupant + whether it persists to terminal, terminal dwell."""
    rng = random.Random(seed)
    rf = math.exp(-GMC)
    gse = GMC - dg
    t_read = win_mult * 400.0 * math.exp(GMC)
    assembly = dict((s, "seed") for s in build["seed"])
    sites = sorted(canon)
    t = 0.0
    churn = 0
    first_stable = None
    persists = None
    prev = assembly.get(SITE)
    dwell_open = None
    dwell = 0.0
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
            if dwell_open is not None:
                dwell += t_read - dwell_open
                dwell_open = None
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
            prev = occ
        # stability check on EVERY event, not only occupancy changes:
        # a tile that attaches at b=1 and stabilizes IN PLACE when its
        # neighbor arrives (the dominant low-dG path) is a first-stable
        # occupant too (smoke n=8 caught the change-only version
        # undercounting persist_n 3/8 with 8/8 stable terminals).
        if occ is not None and first_stable is None and matched(
                build, assembly, SITE, occ) >= 2:
            first_stable = occ
        if first_stable is not None and persists is None:
            if occ is None or occ != first_stable:
                persists = False
        if occ is not None and dwell_open is None:
            dwell_open = t
        elif occ is None and dwell_open is not None:
            dwell += t - dwell_open
            dwell_open = None
    if dwell_open is not None:
        dwell += t_read - dwell_open
    if persists is None and first_stable is not None:
        persists = True
    return assembly, churn, first_stable, persists, dwell, t_read


def run_arm(name, build, s2, dg, win_mult, seed0, canon):
    matched = matched_s2 if s2 else matched_strength
    n = float(N_PER_ARM)
    fills = 0
    frozen = 0
    persist_n = 0
    persist_hit = 0
    churn_sum = 0.0
    dwell_sum = 0.0
    occ_ctr = Counter()
    partial_sum = 0.0
    for i in range(N_PER_ARM):
        asm, churn, first_stable, persists, dwell, t_read = run_traj(
            build, matched, canon, seed0 + i, dg, win_mult)
        occ = asm.get(SITE)
        occ_ctr[str(occ)] += 1
        if occ == "D2T" and matched(build, asm, SITE, "D2T") >= 2:
            fills += 1
        elif occ is not None and matched(build, asm, SITE, occ) >= 2:
            frozen += 1
        if first_stable is not None and persists is not None:
            persist_n += 1
            if persists:
                persist_hit += 1
        churn_sum += churn
        dwell_sum += dwell
        occupied = sum(1 for s in canon if s in asm)
        partial_sum += occupied / float(len(canon))
    rec = {
        "arm": name, "dg": dg, "win_mult": win_mult, "n": N_PER_ARM,
        "fill_frac": fills / n,
        "frozen_nonfill_frac": frozen / n,
        "churn_per_read": churn_sum / n / (win_mult * 400.0 *
                                           math.exp(GMC)),
        "churn_total_mean": churn_sum / n,
        "first_stable_persist": (persist_hit / float(persist_n)
                                 if persist_n else None),
        "persist_n": persist_n,
        "site_dwell_frac": dwell_sum / n / (win_mult * 400.0 *
                                              math.exp(GMC)),
        "site_occupants": dict(occ_ctr.most_common(7)),
        "mean_canonical_partial": partial_sum / n,
    }
    return rec


def band(value, lo, hi):
    if value is None:
        return "NO_EVENTS"
    if value <= lo:
        return "CONFIRMED"
    if value > hi:
        return "FALSIFIED"
    return "INCONCLUSIVE"


def verdicts(per):
    v = {}
    fam05 = per["fam_dg0.5"]["fill_frac"]
    s205 = per["s2_dg0.5"]["fill_frac"]
    off = max(abs(fam05 - REFS["fam_fill_05"]),
              abs(s205 - REFS["s2_fill_05"]))
    v["DW1"] = ("CONFIRMED" if off < 0.07 else
                "FALSIFIED" if off >= 0.10 else "INCONCLUSIVE")
    gain = per["s2_dg4"]["fill_frac"] - s205
    v["DW2"] = ("CONFIRMED" if gain >= 0.15 else
                "FALSIFIED" if gain <= 0.05 else "INCONCLUSIVE")
    ratio = (per["s2_dg4"]["churn_per_read"] /
             per["s2_dg0.5"]["churn_per_read"]
             if per["s2_dg0.5"]["churn_per_read"] > 0 else None)
    v["DW3"] = ("CONFIRMED" if ratio is not None and ratio >= 5 else
                "FALSIFIED" if ratio is not None and ratio < 2 else
                "NO_EVENTS" if ratio is None else "INCONCLUSIVE")
    p05 = per["s2_dg0.5"]["first_stable_persist"]
    p04 = per["s2_dg4"]["first_stable_persist"]
    if p05 is None or p04 is None:
        v["DW4"] = "NO_EVENTS"
    elif p05 >= 0.8 and p05 - p04 >= 0.15:
        v["DW4"] = "CONFIRMED"
    elif p04 >= p05 - 0.05:
        v["DW4"] = "FALSIFIED"
    else:
        v["DW4"] = "INCONCLUSIVE"
    wgain = (per["s2_dg4_win4"]["fill_frac"] -
             per["s2_dg4"]["fill_frac"])
    v["DW5"] = ("CONFIRMED" if wgain >= 0.10 else
                "FALSIFIED" if wgain < 0.03 else "INCONCLUSIVE")
    fam_fills = [per["fam_dg0.5"]["fill_frac"],
                 per["fam_dg2"]["fill_frac"],
                 per["fam_dg4"]["fill_frac"]]
    v["DW6"] = ("CONFIRMED" if min(fam_fills) >= 0.70 else "FALSIFIED")
    s27 = per["s2_dg7"]["fill_frac"]
    v["DW7"] = ("CONFIRMED" if s27 <= 0.25 else
                "RECOVERY-BEYOND" if s27 > 0.60 else "INCONCLUSIVE")
    return v


def main():
    global CANON_SITES
    b1v = build_missing_species(BUILD1, "Vp")
    canon = canonical_assembly(BUILD1)
    CANON_SITES = canon
    arms = [
        ("fam_dg0.5", b1v, False, 0.5, 1.0),
        ("s2_dg0.5", b1v, True, 0.5, 1.0),
        ("fam_dg2", b1v, False, 2.0, 1.0),
        ("s2_dg2", b1v, True, 2.0, 1.0),
        ("fam_dg4", b1v, False, 4.0, 1.0),
        ("s2_dg4", b1v, True, 4.0, 1.0),
        ("s2_dg7", b1v, True, 7.0, 1.0),
        ("s2_dg4_win4", b1v, True, 4.0, 4.0),
        ("fam_dg4_win4", b1v, False, 4.0, 4.0),
    ]
    per = {}
    for idx, (name, build, s2, dg, win) in enumerate(arms):
        rec = run_arm(name, build, s2, dg, win,
                      BASE_SEED + idx * SEED_STRIDE, canon)
        per[name] = rec
        print(json.dumps(rec))
    vs = verdicts(per)
    print(json.dumps(vs))
    print("VERDICTS " + json.dumps(vs, sort_keys=True))


if __name__ == "__main__":
    main()
