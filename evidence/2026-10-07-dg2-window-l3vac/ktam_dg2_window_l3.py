#!/usr/bin/env python3
"""dG-2 window arms + L3-at-vacancy class (tick 47, SON-4821) —
promotes the two honest boundaries tick 43/44 recorded:

  (a) the dG-2 stationary split (D2T 232 : L2 229, fill 0.464) was
      never window-tested — win arms sat at dG 4 only;
  (b) L3 appears at the vacancy terminal class (50/500 at
      s2 dG 0.5) outside tick-42's five-name census — recorded as
      measured; this run promotes it to a first-class class with
      per-name first-stable persistence and L3-episode bookkeeping.

Protocol of record is verbatim tick 38/41/43: BUILD1 Vp-missing,
Gmc=9.5, gse=Gmc-dG, T_read = mult*400*e^Gmc, family vs s2
lock-read arithmetic, canonical map kept from the FULL build,
stability checked on every event.  Arms (n=500 each):

  s2_dg0.5_l3probe  s2, dG 0.5, win 1  (instrumented calibration
                    replicate of tick-43 s2_dg0.5; refs 0.412
                    fill / L3 0.100 census)
  s2_dg0.5_win4     s2, dG 0.5, win 4  (frozen-regime window arm)
  s2_dg2_win4       s2, dG 2,   win 4  (the queued dG-2 window arm)
  fam_dg2_win4      family control at dG 2, win 4

Fresh seed base 220261107 stride 2e7 (grepped disjoint from
20261107 / 40261107 / 80261107 / 100261107 / 120261107 / 160261107
/ 180261107 / 200261107 across evidence/ research-log/ log/).
SMOKE=1 runs n=8/arm (instrument check only; gates stay verbatim —
tick-43 lesson).

PRE-REGISTERED gates (falsifiers in brackets; fixed before
submission; machine verdicts on the final VERDICTS line; refs are
committed tick-43 receipt values, not this run's):
  DW8 dG-2 window gain: s2_dg2_win4 fill >= 0.464 + 0.10
      [gain <= 0.03 FALSIFIED: the marginal split is
       window-independent; middle INCONCLUSIVE]
  DW9 coin survival: at s2_dg2_win4, D2T share of the D2T+L2
      terminal census in [0.40, 0.60]
      [share < 0.35 or > 0.65 FALSIFIED: the window breaks the
       near-fair coin into a one-sided split; middle INCONCLUSIVE;
       denominator < 50 NO_EVENTS]
  DW10 family window-neutrality at dG 2: fam_dg2_win4 fill >= 0.70
      [< 0.70 FALSIFIED: a longer window hurts the family channel
       at the marginal regime]
  DW11 frozen-regime window immunity: s2_dg0.5_win4 first-stable
      persistence >= 0.80
      [< 0.65 FALSIFIED: a longer window re-rolls even the frozen
       regime; middle INCONCLUSIVE]
  LV1 L3 frozen-contender class (pooled over the two dG-0.5 s2
      arms): L3 terminal census >= 0.05 in at least one arm AND
      pooled L3-episode persistence >= 0.7
      [census < 0.05 in BOTH arms FALSIFIED (tick-43's 50/500 was
       a fluke); census ok but episode persistence < 0.5 FALSIFIED
       (L3 is a re-rollable transient, not a frozen contender);
       middle INCONCLUSIVE]
  LV2 window stability of the L3 class: |L3 census (win4) - L3
      census (l3probe)| <= 0.05
      [> 0.10 FALSIFIED: the L3 contender class is window-sensitive;
       middle INCONCLUSIVE]

L3-episode definition (machine-checked): a trajectory counts as an
L3 episode the first time L3 occupies SITE with matched b >= 2;
the episode persists iff the terminal occupant is L3 (any later
re-arrival after a displacement still counts as terminal-L3, and
the episode-persist value reports the fraction of episode
trajectories that end terminal-L3 with b >= 2).
"""
import json
import math
import os
import random
import sys
from collections import Counter, defaultdict

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
BASE_SEED = 220261107
SEED_STRIDE = 20000000
N_PER_ARM = 8 if os.environ.get("SMOKE") else 500
FACE_DIR = {"E": (1, 0), "N": (0, 1), "S": (0, -1), "W": (-1, 0)}
REFS = {"s2_dg05_fill": 0.412, "s2_dg05_l3": 0.100,
        "s2_dg2_fill": 0.464, "fam_dg2_fill": 0.970}
SITE = (2, 2)          # the Vp vacancy: fill/substitution site


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
    """One trajectory, protocol of record.  Vacancy bookkeeping at
    SITE: occupancy-change count (churn), first stable-b>=2
    occupant + whether it persists to terminal, terminal dwell,
    per-name first-stable persistence, L3-episode bookkeeping."""
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
    l3_episode = False
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
        # stability check on EVERY event (tick-43 instrument note):
        # attach-at-b=1 then stabilize-in-place is the dominant
        # low-dG path and must count as first-stable.
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
        if (not l3_episode and occ == "L3" and matched(
                build, assembly, SITE, "L3") >= 2):
            l3_episode = True
    if dwell_open is not None:
        dwell += t_read - dwell_open
    if persists is None and first_stable is not None:
        persists = True
    l3_terminal = False
    toc = assembly.get(SITE)
    if toc == "L3" and matched(build, assembly, SITE, "L3") >= 2:
        l3_terminal = True
    return (assembly, churn, first_stable, persists, dwell, t_read,
            l3_episode, l3_terminal)


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
    by_name = defaultdict(lambda: [0, 0])
    l3_ep_n = 0
    l3_ep_term = 0
    for i in range(N_PER_ARM):
        (asm, churn, first_stable, persists, dwell, t_read,
         l3_episode, l3_terminal) = run_traj(
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
            key = str(first_stable)
            by_name[key][0] += 1
            if persists:
                by_name[key][1] += 1
        if l3_episode:
            l3_ep_n += 1
            if l3_terminal:
                l3_ep_term += 1
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
        "first_stable_persist_by_name": {
            k: {"n": v[0], "persist": (v[1] / float(v[0])
                                       if v[0] else None)}
            for k, v in sorted(by_name.items())},
        "l3_terminal_frac": occ_ctr.get("L3", 0) / n,
        "l3_episode_n": l3_ep_n,
        "l3_episode_terminal_frac": (l3_ep_term / float(l3_ep_n)
                                     if l3_ep_n else None),
    }
    return rec


def verdicts(per):
    v = {}
    w2 = per["s2_dg2_win4"]
    gain = w2["fill_frac"] - REFS["s2_dg2_fill"]
    v["DW8"] = ("CONFIRMED" if gain >= 0.10 else
                "FALSIFIED" if gain <= 0.03 else "INCONCLUSIVE")
    d2t = w2["site_occupants"].get("D2T", 0)
    l2 = w2["site_occupants"].get("L2", 0)
    if d2t + l2 < 50:
        v["DW9"] = "NO_EVENTS"
    else:
        share = d2t / float(d2t + l2)
        v["DW9"] = ("CONFIRMED" if 0.40 <= share <= 0.60 else
                    "FALSIFIED" if share < 0.35 or share > 0.65
                    else "INCONCLUSIVE")
    v["DW10"] = ("CONFIRMED" if per["fam_dg2_win4"]["fill_frac"]
                 >= 0.70 else "FALSIFIED")
    p = per["s2_dg0.5_win4"]["first_stable_persist"]
    if p is None:
        v["DW11"] = "NO_EVENTS"
    else:
        v["DW11"] = ("CONFIRMED" if p >= 0.80 else
                     "FALSIFIED" if p < 0.65 else "INCONCLUSIVE")
    probe = per["s2_dg0.5_l3probe"]
    win4 = per["s2_dg0.5_win4"]
    census_ok = max(probe["l3_terminal_frac"],
                    win4["l3_terminal_frac"]) >= 0.05
    ep_n = probe["l3_episode_n"] + win4["l3_episode_n"]
    ep_term = ((probe["l3_episode_terminal_frac"] or 0.0)
               * probe["l3_episode_n"]
               + (win4["l3_episode_terminal_frac"] or 0.0)
               * win4["l3_episode_n"])
    ep_persist = ep_term / float(ep_n) if ep_n >= 10 else None
    if not census_ok:
        v["LV1"] = "FALSIFIED"
    elif ep_persist is None:
        v["LV1"] = "NO_EVENTS"
    elif ep_persist >= 0.7:
        v["LV1"] = "CONFIRMED"
    elif ep_persist < 0.5:
        v["LV1"] = "FALSIFIED"
    else:
        v["LV1"] = "INCONCLUSIVE"
    diff = abs(win4["l3_terminal_frac"] - probe["l3_terminal_frac"])
    v["LV2"] = ("CONFIRMED" if diff <= 0.05 else
                "FALSIFIED" if diff > 0.10 else "INCONCLUSIVE")
    return v


def main():
    b1v = build_missing_species(BUILD1, "Vp")
    canon = canonical_assembly(BUILD1)
    arms = [
        ("s2_dg0.5_l3probe", b1v, True, 0.5, 1.0),
        ("s2_dg0.5_win4", b1v, True, 0.5, 4.0),
        ("s2_dg2_win4", b1v, True, 2.0, 4.0),
        ("fam_dg2_win4", b1v, False, 2.0, 4.0),
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
