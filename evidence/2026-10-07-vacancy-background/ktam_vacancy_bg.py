#!/usr/bin/env python3
"""Vacancy-background probe (tick 41, SON-4808) — the tick-40 queued
item: WHY does L3@(3,2) squat 82/500 in the s2 Vp-missing arm and
starve the classic D2T fill 0.904 -> 0.412?

Tick 39's static pair layer says L3@(3,2) is one-substitution-enabled
(west DBr via lock_misreads) but the tick-38 MC counted only lock-site
occupancy — the background around the vacancy was never tabulated.
This probe instruments exactly that: terminal per-face bond background
of the (3,2) occupant, co-occurrence with the (2,2) occupant, the
fill-conditional starvation split, stability, and the attach race.

Systems: BUILD1 Vp-missing (build_missing_species, canonical map kept
from the FULL build, protocol of tick 38), family vs s2 lock-read
arithmetic, dG 0.5, n=500/arm.  Protocol of record: Gmc=9.5,
Gse=Gmc-dG, T_read=400*e^Gmc, no-mismatch kTAM, per-run RNG.
Fresh seed base 180261107 stride 2e7 (disjoint from 20261107 /
40261107 / 80261107 / 100261107 / 120261107 / 160261107).
CORRECTION (collection, 2026-10-07 ~12:15Z): 180261107 was
ALREADY the tick-40 viasite study's base — the disjoint claim
above is wrong.  No trajectory duplication results: every
overlapping (seed, dG) pair runs a DIFFERENT build (tick-40 arms
are plain BUILD1 / UNIT_ONLY; these arms are Vp-missing BUILD1),
so the event lists differ and the streams diverge.  VB1
calibration still compares against tick-38 refs measured on base
160261107 — a genuine cross-seed replication.
SMOKE=1 runs n=8/arm (instrument check only).

PRE-REGISTERED gates (falsifiers in brackets; fixed before
submission; machine verdicts in the final output line):
  VB1 calibration: s2 fill within 0.07 of 0.412 AND s2 terminal
      L3@(3,2) fraction within 0.08 of 0.164 (82/500)
      [either >= 0.10 off FALSIFIED: protocol drift — stop reading]
  VB2 enabling background: among s2 terminals carrying L3@(3,2),
      fraction whose W-face glue matches the (2,2) occupant's E
      glue >= 0.7 (the one-substitution west read of tick 39)
      [<= 0.4 FALSIFIED; n_L3 < 10 -> NO_EVENTS]
  VB3 starvation split: s2 fill | L3 absent >= 0.70 AND
      fill | L3 present <= 0.45 — L3 presence carries the starvation
      [fill|present >= fill|absent - 0.05 FALSIFIED (starvation is
      background-carried, not L3-carried); else INCONCLUSIVE]
  VB4 frozen squatter: among s2 terminals carrying L3@(3,2),
      stable-b>=2 fraction >= 0.9 AND mean dwell/read >= 0.5
      [stable fraction < 0.5 FALSIFIED: transient class, not frozen]
  VB5 attach race: among s2 trajectories with both first-events,
      P(first L3@(3,2) attach < first D2T@(2,2) attach) >= 0.6 —
      L3 wins the race for the vacancy's stabilizing partner
      [<= 0.5 FALSIFIED]
Reference arm fam_b1_Vp (fill ~0.904, L3 terminal rare) reported,
no gate — its role is the family contrast.
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
BASE_SEED = 180261107
SEED_STRIDE = 20000000
N_PER_ARM = 8 if os.environ.get("SMOKE") else 500
T_READ_MULT = 400.0
FACE_DIR = {"E": (1, 0), "N": (0, 1), "S": (0, -1), "W": (-1, 0)}
FACE_PAIR = {"E": "W", "W": "E", "N": "S", "S": "N"}
REFS = {"s2_fill": 0.412, "s2_L3_frac": 0.164, "fam_fill": 0.904}
SITE_LOCK = (3, 2)   # the vacancy's lock site (Vp removed)
SITE_WEST = (2, 2)   # its west neighbor, the fill/substitution site


def matched_s2(build, asm, site, tile_name):
    """Family matched strength with the lock-read bond doubled
    (verbatim tick-38 arithmetic)."""
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


def run_traj(build, matched, canon, seed, dg):
    """One trajectory, protocol of record, with vacancy-window
    bookkeeping: occupancy-change logs for (3,2) and (2,2), L3 dwell,
    and first-attach times for the two racers."""
    rng = random.Random(seed)
    rf = math.exp(-GMC)
    gse = GMC - dg
    t_read = T_READ_MULT * math.exp(GMC)
    assembly = dict((s, "seed") for s in build["seed"])
    sites = sorted(canon)
    t = 0.0
    first_L3 = None
    first_D2T = None
    dwell_open = None
    dwell = 0.0
    log32 = []
    log22 = []
    prev32 = assembly.get(SITE_LOCK)
    prev22 = assembly.get(SITE_WEST)
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
                    if (arg[0] == SITE_LOCK and arg[1] == "L3"
                            and first_L3 is None):
                        first_L3 = t
                    if (arg[0] == SITE_WEST and arg[1] == "D2T"
                            and first_D2T is None):
                        first_D2T = t
                else:
                    del assembly[arg]
                break
        occ32 = assembly.get(SITE_LOCK)
        occ22 = assembly.get(SITE_WEST)
        if occ32 != prev32:
            log32.append((round(t, 2), occ32))
            prev32 = occ32
        if occ22 != prev22:
            log22.append((round(t, 2), occ22))
            prev22 = occ22
        if occ32 == "L3" and dwell_open is None:
            dwell_open = t
        elif occ32 != "L3" and dwell_open is not None:
            dwell += t - dwell_open
            dwell_open = None
    if dwell_open is not None:
        dwell += t_read - dwell_open
    return assembly, first_L3, first_D2T, dwell, log32, log22


def face_background(build, asm, site, tile_name):
    """Per-face bond description of tile_name at site: for each face,
    the neighbor's occupant and whether the glue pair matches."""
    out = {}
    for face, (dx, dy) in FACE_DIR.items():
        nb = (site[0] + dx, site[1] + dy)
        if nb[1] == 0 and nb in build["seed"]:
            partner = "seed:" + build["seed"][nb]
            g2 = build["seed"][nb]
        elif nb in asm:
            partner = asm[nb]
            g2 = build["tiles"][asm[nb]].get(FACE_PAIR[face])
        else:
            partner = None
            g2 = None
        g1 = build["tiles"][tile_name].get(face)
        out[face] = {"partner": partner,
                     "match": bool(g1 and g2 and g1 == g2)}
    return out


def run_arm(name, build, s2, dg, seed0, canon):
    matched = matched_s2 if s2 else matched_strength
    t_read = T_READ_MULT * math.exp(GMC)
    n = float(N_PER_ARM)
    fills = l3_term = l3_stable = 0
    fill_with = fill_without = 0
    with_l3 = without_l3 = 0
    west_match = west_total = 0
    race_win = race_total = 0
    dwell_sum = 0.0
    bg_ctr = Counter()
    west_occ_ctr = Counter()
    for i in range(N_PER_ARM):
        asm, fL3, fD2T, dw, _l32, _l22 = run_traj(
            build, matched, canon, seed0 + i, dg)
        occ22 = asm.get(SITE_WEST)
        west_occ_ctr[str(occ22)] += 1
        if occ22 == "D2T" and matched(build, asm, SITE_WEST, "D2T") >= 2:
            fills += 1
        has_l3 = asm.get(SITE_LOCK) == "L3"
        if has_l3:
            l3_term += 1
            with_l3 += 1
            if matched(build, asm, SITE_LOCK, "L3") >= 2:
                l3_stable += 1
            bg = face_background(build, asm, SITE_LOCK, "L3")
            key = tuple(sorted(
                (f, v["partner"]) for f, v in bg.items() if v["match"]))
            bg_ctr[key] += 1
            west_total += 1
            if bg["W"]["match"]:
                west_match += 1
            if occ22 == "D2T" and matched(
                    build, asm, SITE_WEST, "D2T") >= 2:
                fill_with += 1
        else:
            without_l3 += 1
            if occ22 == "D2T" and matched(
                    build, asm, SITE_WEST, "D2T") >= 2:
                fill_without += 1
        if fL3 is not None and fD2T is not None:
            race_total += 1
            if fL3 < fD2T:
                race_win += 1
        dwell_sum += dw
    rec = {
        "arm": name, "dg": dg, "n": N_PER_ARM,
        "fill_frac": fills / n,
        "L3_term_frac": l3_term / n,
        "L3_stable_of_term": (l3_stable / float(l3_term)
                              if l3_term else None),
        "mean_L3_dwell_over_read": dwell_sum / n / t_read,
        "fill_given_L3": (fill_with / float(with_l3)
                          if with_l3 else None),
        "fill_given_noL3": (fill_without / float(without_l3)
                            if without_l3 else None),
        "west_match_of_L3": (west_match / float(west_total)
                             if west_total else None),
        "race_L3_first_frac": (race_win / float(race_total)
                               if race_total else None),
        "race_n": race_total,
        "west_site_occupants": dict(west_occ_ctr.most_common(6)),
        "L3_matched_faces": {" | ".join(
            "%s->%s" % (f, p) for f, p in k): c
            for k, c in bg_ctr.most_common(6)},
    }
    return rec


def verdicts(per):
    v = {}
    s2 = per["s2_b1_Vp"]
    fill_ok = abs(s2["fill_frac"] - REFS["s2_fill"]) < 0.07
    l3_ok = abs(s2["L3_term_frac"] - REFS["s2_L3_frac"]) < 0.08
    off = max(abs(s2["fill_frac"] - REFS["s2_fill"]),
              abs(s2["L3_term_frac"] - REFS["s2_L3_frac"]))
    v["VB1"] = ("CONFIRMED" if fill_ok and l3_ok else
                "FALSIFIED" if off >= 0.10 else "INCONCLUSIVE")
    if (s2["L3_term_frac"] or 0) * N_PER_ARM >= 10:
        wm = s2["west_match_of_L3"]
        v["VB2"] = ("CONFIRMED" if wm is not None and wm >= 0.7 else
                    "FALSIFIED" if wm is not None and wm <= 0.4 else
                    "INCONCLUSIVE")
    else:
        v["VB2"] = "NO_EVENTS"
    fg = s2["fill_given_L3"]
    fn = s2["fill_given_noL3"]
    if fg is not None and fn is not None:
        v["VB3"] = ("CONFIRMED" if fn >= 0.70 and fg <= 0.45 else
                    "FALSIFIED" if fg >= fn - 0.05 else
                    "INCONCLUSIVE")
    else:
        v["VB3"] = "NO_EVENTS"
    st = s2["L3_stable_of_term"]
    dwr = s2["mean_L3_dwell_over_read"]
    v["VB4"] = ("CONFIRMED" if st is not None and st >= 0.9
                and dwr is not None and dwr >= 0.5 else
                "FALSIFIED" if st is not None and st < 0.5 else
                "INCONCLUSIVE")
    rc = s2["race_L3_first_frac"]
    v["VB5"] = ("CONFIRMED" if rc is not None and rc >= 0.6 else
                "FALSIFIED" if rc is not None and rc <= 0.5 else
                "INCONCLUSIVE")
    return v


def main():
    b1v = build_missing_species(BUILD1, "Vp")
    canon_b1 = canonical_assembly(BUILD1)
    arms = [
        ("fam_b1_Vp", b1v, False, 0.5),
        ("s2_b1_Vp", b1v, True, 0.5),
    ]
    per = {}
    for idx, (name, build, s2, dg) in enumerate(arms):
        rec = run_arm(name, build, s2, dg,
                      BASE_SEED + idx * SEED_STRIDE, canon_b1)
        per[name] = rec
        print(json.dumps(rec))
    vs = verdicts(per)
    print(json.dumps(vs))
    print("VERDICTS " + json.dumps(vs, sort_keys=True))


if __name__ == "__main__":
    main()
