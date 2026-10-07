#!/usr/bin/env python3
"""Via-site lock placement kinetics under s2 (tick 40, designs/007)
— pre-registered BEFORE any MC run.

Tick 39's census split lock misplacements into two layers: the
kinetic-dominant lock-site class is one-substitution-enabled (pair
layer lock_misreads); the SOLO class is VIA-SITE placements L1@(2,1)
and L2@(2,2), W-read carried, bond 1 at family arithmetic -> bond 2
under s2.  Never tabulated kinetically — this study does that.

Race mechanism (prediction): at a via site the canonical via tile is
stable once placed; a lock arriving there is b=1 at family strength
(detaches, lopsided race).  Under s2 the lock's W read doubles: both
competitors frozen, first-come wins.  The s2 via-lock terminal
fraction is the flip probability of a coin the family encoding never
tosses.

Protocol of record (tick 38 verbatim): Gmc=9.5, Gse=Gmc-dG,
T_read=400*e^Gmc, no-mismatch kTAM, per-run RNG, matched_s2 bond
rule imported from the tick-38 harness.  Strict completion refined
to FULL canonical occupancy (strict_filled); the decode-only number
is also reported, no gate depends on it.  Arms: fam_b1, s2_b1,
s2_b1_dG2, fam_unit, s2_unit; n=500 each (SMOKE=1 -> n=8,
instrument check only, gates NOT evaluated).  Seed base 180261107
stride 2e7.

PRE-REGISTERED gates (falsifiers in brackets; fixed before
submission; machine verdicts in the final output line):
  V1  EXISTENCE: s2_b1 stable via-lock terminal frac >= 0.05 AND
      >= fam_b1's + 0.02  [s2_b1 < 0.05 OR <= fam_b1+0.02 FALSIFIED]
  V2  TRANSIENCY SPLIT: fam_b1 mean via-lock dwell frac <= 0.15 AND
      s2_b1's >= 0.8  [fam >= 0.5 OR s2 <= 0.5 FALSIFIED;
      no attach events in either arm -> NO_EVENTS]
  V3  COMPLETION COST: among s2_b1 not-strict_filled terminals the
      stable-via-lock-carrying frac >= 0.10  [<= 0.02 FALSIFIED;
      n_nonstrict < 10 -> NO_EVENTS]
  V4  CALIBRATION: fam_b1 blocked within 0.05 of 0.308 AND s2_b1
      within 0.05 of 0.314 (tick-38 receipt, same instrument)
      [either >= 0.10 off FALSIFIED: protocol drift — stop reading]
  V5  dG DIRECTION: s2 via-lock stable frac at dG2 < at dG0.5
      [>= FALSIFIED]
  V6  GENERALITY: s2_unit stable via-lock frac >= 0.05
      [< 0.02 FALSIFIED; 0.02–0.05 INCONCLUSIVE]
"""
import json
import math
import os
import random
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
EV = os.path.dirname(HERE)
SIB_STRENGTH = os.path.join(EV, "2026-10-07-strength2-lock")
SIB_AND = os.path.join(EV, "2026-10-06-body-conjunction-builds")
SIB_DEATH = os.path.join(EV, "2026-10-06-structural-death")
for p in (HERE, REPO, SIB_STRENGTH, SIB_AND, SIB_DEATH):
    if p not in sys.path:
        sys.path.insert(0, p)

from tiles_and import BUILD1                          # noqa: E402
from ktam_strength2 import matched_s2, decode, median  # noqa: E402
from molasp.compiler import compile_program           # noqa: E402
from molasp.offchannel import (canonical_assembly,    # noqa: E402
                               infer_lock_sites,
                               matched_strength)

GMC = 9.5
BASE_SEED = 180261107
SEED_STRIDE = 20000000
N_PER_ARM = 8 if os.environ.get("SMOKE") else 500
T_READ_MULT = 400.0
T_READ = T_READ_MULT * math.exp(GMC)
FACE_DIR = {"E": (1, 0), "N": (0, 1), "S": (0, -1), "W": (-1, 0)}
REFS = {"fam_b1_blocked": 0.308, "s2_b1_blocked": 0.314}


def run_traj(build, matched, canon, via_sites, seed, dg):
    """One trajectory, protocol of record, with via-site L*
    bookkeeping (attach events + dwell of L* at via sites)."""
    rng = random.Random(seed)
    rf = math.exp(-GMC)
    gse = GMC - dg
    tiles = build["tiles"]
    assembly = dict((s, "seed") for s in build["seed"])
    sites = sorted(canon)
    t = 0.0
    via_events = 0
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
                for tile in tiles:
                    if matched(build, assembly, site, tile) >= 1:
                        events.append((rf, "attach", (site, tile)))
        total = sum(r for r, _, _ in events)
        if total <= 0 or t > T_READ:
            break
        t_next = t + rng.expovariate(total)
        if t_next > T_READ:
            if dwell_open is not None:
                dwell += T_READ - dwell_open
                dwell_open = None
            t = T_READ
            break
        t = t_next
        r = rng.random() * total
        acc = 0.0
        for rate, kind, arg in events:
            acc += rate
            if acc >= r:
                if kind == "attach":
                    assembly[arg[0]] = arg[1]
                    if arg[0] in via_sites and str(arg[1]).startswith("L"):
                        via_events += 1
                else:
                    del assembly[arg]
                break
        via_locked = any(
            str(assembly.get(s)).startswith("L")
            for s in via_sites if assembly.get(s) is not None)
        if via_locked and dwell_open is None:
            dwell_open = t
        elif not via_locked and dwell_open is not None:
            dwell += t - dwell_open
            dwell_open = None
    if dwell_open is not None:
        dwell += T_READ - dwell_open
    return assembly, via_events, dwell


def run_arm(name, build, s2, dg, seed0):
    matched = matched_s2 if s2 else matched_strength
    canon = canonical_assembly(build)
    locks = infer_lock_sites(canon)
    via_sites = tuple(sorted(s for s in canon if s[0] == 2))
    full = "".join(a for _, a in sorted(build["rows"].items()))
    blocked_n = strict_n = dec_n = nonstrict_n = 0
    via_term = via_stable = nonstrict_via = 0
    via_events_total = 0
    dwell_fracs = []
    ctr = Counter()
    for i in range(N_PER_ARM):
        asm, ve, dw = run_traj(build, matched, canon, via_sites,
                               seed0 + i, dg)
        sq = [s for s in locks
              if asm.get(s) is not None and asm[s] != canon[s]]
        if sq:
            blocked_n += 1
            for s in sq:
                ctr["%s@%d,%d" % (asm[s], s[0], s[1])] += 1
        strict_filled = all(asm.get(s) == canon[s] for s in canon)
        if strict_filled:
            strict_n += 1
        else:
            nonstrict_n += 1
        if decode(build, canon, asm) == full:
            dec_n += 1
        occ = [(s, asm[s]) for s in via_sites
               if asm.get(s) is not None and str(asm[s]).startswith("L")]
        if occ:
            via_term += 1
            if any(matched(build, asm, s, tl) >= 2 for s, tl in occ):
                via_stable += 1
                if not strict_filled:
                    nonstrict_via += 1
        via_events_total += ve
        if ve:
            dwell_fracs.append(dw / T_READ)
    n = float(N_PER_ARM)
    return {
        "arm": name, "dg": dg, "n": N_PER_ARM,
        "blocked_frac": blocked_n / n,
        "strict_filled_frac": strict_n / n,
        "strict_decode_frac": dec_n / n,
        "via_lock_terminal_frac": via_term / n,
        "via_lock_stable_frac": via_stable / n,
        "via_attach_events": via_events_total,
        "mean_via_dwell_frac": (sum(dwell_fracs) / len(dwell_fracs)
                                if dwell_fracs else None),
        "nonstrict_n": nonstrict_n,
        "nonstrict_via": nonstrict_via,
        "squatters": dict(ctr.most_common(8)),
    }


def build_arms():
    unit = compile_program("p. q. r :- p.", name="UNIT_ONLY")
    return [
        ("fam_b1", BUILD1, False, 0.5),
        ("s2_b1", BUILD1, True, 0.5),
        ("s2_b1_dG2", BUILD1, True, 2.0),
        ("fam_unit", unit, False, 0.5),
        ("s2_unit", unit, True, 0.5),
    ]


def verdicts(per):
    v = {}
    f = per["fam_b1"]
    s = per["s2_b1"]
    v["V1"] = ("CONFIRMED"
               if (s["via_lock_stable_frac"] >= 0.05
                   and s["via_lock_stable_frac"]
                   >= f["via_lock_stable_frac"] + 0.02)
               else "FALSIFIED")
    if (f["mean_via_dwell_frac"] is None
            or s["mean_via_dwell_frac"] is None):
        v["V2"] = "NO_EVENTS"
    else:
        v["V2"] = ("CONFIRMED"
                   if (f["mean_via_dwell_frac"] <= 0.15
                       and s["mean_via_dwell_frac"] >= 0.8)
                   else "FALSIFIED"
                   if (f["mean_via_dwell_frac"] >= 0.5
                       or s["mean_via_dwell_frac"] <= 0.5)
                   else "INCONCLUSIVE")
    if s["nonstrict_n"] < 10:
        v["V3"] = "NO_EVENTS"
    else:
        ratio = s["nonstrict_via"] / float(s["nonstrict_n"])
        v["V3"] = ("CONFIRMED" if ratio >= 0.10 else
                   "FALSIFIED" if ratio <= 0.02 else "INCONCLUSIVE")
    d1 = abs(f["blocked_frac"] - REFS["fam_b1_blocked"])
    d2 = abs(s["blocked_frac"] - REFS["s2_b1_blocked"])
    v["V4"] = ("CONFIRMED" if d1 <= 0.05 and d2 <= 0.05 else
               "FALSIFIED" if d1 >= 0.10 or d2 >= 0.10 else
               "INCONCLUSIVE")
    v["V5"] = ("CONFIRMED" if per["s2_b1_dG2"]["via_lock_stable_frac"]
               < s["via_lock_stable_frac"] else "FALSIFIED")
    u = per["s2_unit"]["via_lock_stable_frac"]
    v["V6"] = ("CONFIRMED" if u >= 0.05 else
               "FALSIFIED" if u < 0.02 else "INCONCLUSIVE")
    return v


def main():
    per = {}
    lines = []
    for idx, (name, build, s2, dg) in enumerate(build_arms()):
        rec = run_arm(name, build, s2, dg,
                      BASE_SEED + idx * SEED_STRIDE)
        per[name] = rec
        print(json.dumps(rec, sort_keys=True), flush=True)
        lines.append(json.dumps(rec, sort_keys=True))
    v = {"_smoke_note": "SMOKE run (n=8): gates NOT evaluated"
        } if os.environ.get("SMOKE") else verdicts(per)
    vline = "VERDICTS " + json.dumps(v, sort_keys=True)
    print(vline, flush=True)
    lines.append(vline)
    out_path = os.path.join(HERE, "viasite.out")
    with open(out_path, "w") as fh:
        fh.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
