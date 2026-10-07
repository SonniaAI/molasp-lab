#!/usr/bin/env python3
"""Strength-2 lock-read encoding (tick 38, SON-4778) — designs/005
deferred item (b), pre-registered BEFORE any MC run.

The arc's knob so far was a RENAME (lock_glue_scope family|row);
R1: renames change bond identity.  This is the first KINETIC lever
at fixed identity: the lock-read bond (a lock tile's W face reading
the row's value glue) counts strength 2 instead of 1, on BOTH
evaluation sides (the lock's own W bond, and any tile's E bond into
a placed lock).  Everything else — value relays, done glues, base
relays, squatter bonds — is untouched.  Both measured hazard
classes keep their intrinsic bonds: the solo b=1 transient squat
(Vp.W<->D2T.E at the lock site) and the lo-read cooperative stack
(Vp.N<->DBr.S) ride non-lock bonds and stay strength 1.

Prediction duty (designs/005 "(b) deferred"): price squat-dwell vs
lock-capture-time against the published b=1 equilibrium (~0.38 at
dG 0.5).  With a strength-2 lock-read the canonical lock can
capture on its W bond ALONE (b=2) without the base relay, so lock
capture should accelerate while the squat classes keep their old
rates; the classic substitution fill's E->L2 bond also doubles, so
repair should hold or rise.

Systems: BUILD1 (tiles_and, family scope) plain + Vp-missing, and
UNIT_ONLY (compile_program v0.1, the designs/005 generality arm).
dG grid 0.5/2.0 on BUILD1 arms; UNIT_ONLY at dG 0.5.
Protocol of record: Gmc=9.5, Gse=Gmc-dG, T_read=400*e^Gmc,
no-mismatch kTAM, per-run RNG.  Fresh seed base 160261107 stride
2e7 (disjoint from 20261107 / 40261107 / 80261107 / 100261107 /
120261107).  n=500/arm (8 arms, 4000 trajectories); SMOKE=1 runs
n=8 per arm (instrument check only, gates NOT evaluated).

PRE-REGISTERED gates (falsifiers in brackets; fixed before
submission; machine verdicts in the final output line):
  K1  s2_b1 blocked <= 0.22 (a >= 0.05 drop vs family ref 0.27)
      [>= 0.27 FALSIFIED: encoding does not help the read-block;
      0.22-0.27 INCONCLUSIVE]
  K2  s2_b1_Vp stable D2T fill >= 0.85 (ref 0.908; the classic
      fill's E->L2 bond doubles, so repair holds or rises)
      [<= 0.70 FALSIFIED]
  K3  among s2_b1 blocked terminals, Vp@(3,2)+DBr@(3,3) stack
      co-occurrence >= 0.7 — the surviving block is still the
      lo-read stack class [<= 0.4 FALSIFIED; n_blocked < 10 ->
      NO_EVENTS]
  K4  s2_b1 strict-pqr >= 0.55 (family ref 0.582; no yield loss)
      [<= 0.45 FALSIFIED]
  K5  calibration: fam_b1 blocked within 0.05 of 0.27 AND
      fam_b1_Vp fill within 0.05 of 0.908
      [any >= 0.10 off FALSIFIED: protocol drift — stop reading]
  K6  dG direction: s2 blocked(dG2) < blocked(dG0.5) AND
      s2 fill(dG2) < fill(dG0.5) — both channels still starve
      [either >= FALSIFIED]
  K7  generality direction: s2_unit blocked <= fam_unit blocked
      [> fam_unit + 0.02 FALSIFIED]
  K8  lock capture accelerates: median first-passage of L2@(3,2)
      in s2_b1 strictly below fam_b1's
      [>= FALSIFIED; missing medians -> NO_EVENTS]
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
from molasp.compiler import compile_program           # noqa: E402
from molasp.offchannel import (canonical_assembly,    # noqa: E402
                               infer_lock_sites,
                               matched_strength)

GMC = 9.5
BASE_SEED = 160261107
SEED_STRIDE = 20000000
N_PER_ARM = 8 if os.environ.get("SMOKE") else 500
T_READ_MULT = 400.0
FACE_DIR = {"E": (1, 0), "N": (0, 1), "S": (0, -1), "W": (-1, 0)}
REFS = {"fam_b1_blocked": 0.27, "fam_b1_Vp_fill": 0.908,
        "fam_b1_strict": 0.582}
LOCK32 = (3, 2)


def matched_s2(build, asm, site, tile_name):
    """Family matched strength with the lock-read bond doubled
    (a lock tile's W-face glue pair counts 2 on both evaluation
    sides; site-agnostic and structural: any L* tile's W read)."""
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
    """One trajectory, protocol of record, with lock-capture
    first-passage and squat@(3,2) dwell bookkeeping."""
    rng = random.Random(seed)
    rf = math.exp(-GMC)
    gse = GMC - dg
    t_read = T_READ_MULT * math.exp(GMC)
    tiles = build["tiles"]
    assembly = dict((s, "seed") for s in build["seed"])
    sites = sorted(canon)
    t = 0.0
    t_lock32 = None
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
                    if (arg[0] == LOCK32 and arg[1] == "L2"
                            and t_lock32 is None):
                        t_lock32 = t
                else:
                    del assembly[arg]
                break
        occ32 = assembly.get(LOCK32)
        squat32 = occ32 is not None and occ32 != canon.get(LOCK32)
        if squat32 and dwell_open is None:
            dwell_open = t
        elif not squat32 and dwell_open is not None:
            dwell += t - dwell_open
            dwell_open = None
    if dwell_open is not None:
        dwell += t_read - dwell_open
    return assembly, t_lock32, dwell


def decode(build, canon, assembly):
    """Scope-aware lock decode (family scope: lock W glues read the
    atom's true '-t' family)."""
    rows = build["rows"]
    spined = all(assembly.get((0, y)) == canon[(0, y)]
                 for y in rows if (0, y) in canon)
    locks_ok = all(assembly.get(s) is not None
                   and str(assembly[s]).startswith("L")
                   for s in canon if canon[s].startswith("L"))
    if not spined or not locks_ok:
        return "partial"
    atoms = []
    for y, atom in sorted(rows.items()):
        lock = assembly[(3, y)]
        if build["tiles"][lock]["W"].startswith(atom + "-t"):
            atoms.append(atom)
    return "".join(atoms) if atoms else "empty"


def median(xs):
    ys = sorted(xs)
    if not ys:
        return None
    m = len(ys) // 2
    return ys[m] if len(ys) % 2 else 0.5 * (ys[m - 1] + ys[m])


def run_arm(name, build, s2, dg, seed0, canon=None):
    matched = matched_s2 if s2 else matched_strength
    if canon is None:
        canon = canonical_assembly(build)
    locks = infer_lock_sites(canon)
    full = "".join(a for _, a in sorted(build["rows"].items()))
    is_vp = "_Vp" in name
    blocked_n = squatters = stacks = strict_n = vstacks = fills = 0
    ctr = Counter()
    t32 = []
    dwell = []
    for i in range(N_PER_ARM):
        asm, tl, dw = run_traj(build, matched, canon, seed0 + i, dg)
        sq = [s for s in locks
              if asm.get(s) is not None and asm[s] != canon[s]]
        if sq:
            blocked_n += 1
            for s in sq:
                ctr["%s@%d,%d" % (asm[s], s[0], s[1])] += 1
        sqset = set(sq)
        if any((s[0], s[1] + 1) in sqset for s in sq):
            stacks += 1
        if decode(build, canon, asm) == full:
            strict_n += 1
        if asm.get((3, 2)) == "Vp" and asm.get((3, 3)) == "DBr":
            vstacks += 1
        if is_vp:
            occ22 = asm.get((2, 2))
            if (occ22 == "D2T"
                    and matched(build, asm, (2, 2), "D2T") >= 2):
                fills += 1
        if tl is not None:
            t32.append(tl)
        dwell.append(dw)
    n = float(N_PER_ARM)
    rec = {
        "arm": name, "dg": dg, "n": N_PER_ARM,
        "blocked_frac": blocked_n / n,
        "strict_frac": strict_n / n,
        "fill_frac": (fills / n) if is_vp else None,
        "vstack_frac": vstacks / n,
        "vstack_of_blocked": (vstacks / float(blocked_n)
                              if blocked_n else None),
        "adjacent_lock_stack_frac": stacks / n,
        "median_t_first_L2_32": median(t32),
        "mean_squat32_dwell": sum(dwell) / n,
        "squatters": dict(ctr.most_common(8)),
    }
    return rec


def build_arms():
    unit = compile_program("p. q. r :- p.", name="UNIT_ONLY")
    b1v = build_missing_species(BUILD1, "Vp")
    canon_b1 = canonical_assembly(BUILD1)
    # missing-species builds keep the full build's canonical map (the
    # vacancy is a site whose canonical occupant was removed)
    return [
        ("fam_b1", BUILD1, False, 0.5, None),
        ("s2_b1", BUILD1, True, 0.5, None),
        ("fam_b1_Vp", b1v, False, 0.5, canon_b1),
        ("s2_b1_Vp", b1v, True, 0.5, canon_b1),
        ("s2_b1_dG2", BUILD1, True, 2.0, None),
        ("s2_b1_Vp_dG2", b1v, True, 2.0, canon_b1),
        ("fam_unit", unit, False, 0.5, None),
        ("s2_unit", unit, True, 0.5, None),
    ]


def verdicts(per):
    v = {}
    a = per["fam_b1"]; s = per["s2_b1"]
    v["K1"] = ("CONFIRMED" if s["blocked_frac"] <= 0.22 else
               "FALSIFIED" if s["blocked_frac"] >= 0.27 else
               "INCONCLUSIVE")
    f = per["s2_b1_Vp"]
    v["K2"] = ("CONFIRMED" if f["fill_frac"] >= 0.85 else
               "FALSIFIED" if f["fill_frac"] <= 0.70 else
               "INCONCLUSIVE")
    if s["blocked_frac"] * s["n"] < 10:
        v["K3"] = "NO_EVENTS"
    else:
        co = s["vstack_of_blocked"]
        v["K3"] = ("CONFIRMED" if co >= 0.7 else
                   "FALSIFIED" if co <= 0.4 else "INCONCLUSIVE")
    v["K4"] = ("CONFIRMED" if s["strict_frac"] >= 0.55 else
               "FALSIFIED" if s["strict_frac"] <= 0.45 else
               "INCONCLUSIVE")
    d1 = abs(a["blocked_frac"] - REFS["fam_b1_blocked"])
    d2 = abs(per["fam_b1_Vp"]["fill_frac"] - REFS["fam_b1_Vp_fill"])
    v["K5"] = ("CONFIRMED" if d1 <= 0.05 and d2 <= 0.05 else
               "FALSIFIED" if d1 >= 0.10 or d2 >= 0.10 else
               "INCONCLUSIVE")
    v["K6"] = ("CONFIRMED" if (per["s2_b1_dG2"]["blocked_frac"]
                               < s["blocked_frac"]
                               and per["s2_b1_Vp_dG2"]["fill_frac"]
                               < f["fill_frac"]) else "FALSIFIED")
    v["K7"] = ("CONFIRMED" if per["s2_unit"]["blocked_frac"]
               <= per["fam_unit"]["blocked_frac"] else
               "FALSIFIED" if per["s2_unit"]["blocked_frac"]
               > per["fam_unit"]["blocked_frac"] + 0.02 else
               "INCONCLUSIVE")
    ma = a["median_t_first_L2_32"]; ms = s["median_t_first_L2_32"]
    v["K8"] = ("NO_EVENTS" if ma is None or ms is None else
               "CONFIRMED" if ms < ma else "FALSIFIED")
    return v


def main():
    per = {}
    lines = []
    for idx, (name, build, s2, dg, canon) in enumerate(build_arms()):
        rec = run_arm(name, build, s2, dg,
                      BASE_SEED + idx * SEED_STRIDE, canon)
        per[name] = rec
        print(json.dumps(rec, sort_keys=True), flush=True)
        lines.append(json.dumps(rec, sort_keys=True))
    v = {"_smoke_note": "SMOKE run (n=8): gates NOT evaluated"
        } if os.environ.get("SMOKE") else verdicts(per)
    vline = "VERDICTS " + json.dumps(v, sort_keys=True)
    print(vline, flush=True)
    lines.append(vline)
    out_path = os.path.join(HERE, "strength2.out")
    with open(out_path, "w") as fh:
        fh.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
