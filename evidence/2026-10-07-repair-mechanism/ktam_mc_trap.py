"""kTAM trajectory census — repair-mechanism study (tick 24, SON-4778).

Tick 23's species-death survey measured WHICH removals repair; this
run measures HOW. Two open items: (i) V0p/Vp removals EXCEED build1
parity at dG 0.5 (1.25x/1.53x) — self-trap relief or faster path?
(ii) the L3-only falsifier channel (18/500 strict "pqr" with the
lock species absent) — the structural census (trap_census.py,
machine-checked, in-process below) says L2 can hold (3,3) on a b=1
west bond if Vp or D2T squats (2,3), and any "-t" W glue reads TRUE.

Instrument: the survey's protocol of record (Gse=9, Gmc grid, T_read
= 400*e^Gmc, no-mismatch kTAM, per-run RNG, deterministic seeds),
plus a READ-TIME CENSUS of all 12 canonical sites per trajectory.
Systems: build1 + the seven removals that were not DEAD everywhere
(tick-23 rows L1/L2/S1/S2/S3 are 0/2000 — excluded; L3 kept as the
misread arm). Points: dG {0.5, 2, 4} (dG 7 is starved everywhere;
tick-23 numbers stand). n = 500/point, 8 systems, 12,000 runs.

Pre-registered BEFORE this MC runs (falsifiers in brackets):

R2 (trap-relief explains exceeds-parity): conditioned on NO
    read-time squatter at any lock site, strict "pqr" rates at
    dG 0.5 of build1 / V0p-missing / Vp-missing agree within 0.10
    [any conditional gap >= 0.15 in the raw direction].
R3a (blocker identity): in build1 non-pqr trajectories at dG 0.5,
    the dominant read-time squatters are Vp at (3,2) and V0p at
    (3,1) [any other tile top-1 at either site].
R3b (substitution repair identity): strict-pqr terminals of
    V0p-missing occupy (2,1) with D1T, and of Vp-missing occupy
    (2,2) with D2T, each in >= 50% of cases [majority other/None].
R3c (misread channel): strict-pqr terminals of L3-missing at
    dG 0.5 hold L2 at (3,3) with Vp or D2T at (2,3) in >= 2/3 of
    cases [L2-fraction < 0.5 or empty west enablers].
R4 (dG trend): build1's read-time lock-squat rate decreases
    monotonically in dG, and Vp-missing's ratio falls below 1 by
    dG 4 (trap relief vanishes while repair starves)
    [non-monotone squat rate or ratio >= 1 at dG 4].

Verdicts are machine-computed in the job's final line.
"""
import json
import math
import os
import random
import sys
from collections import Counter
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
SIB_AND = os.path.join(os.path.dirname(HERE),
                       "2026-10-06-body-conjunction-builds")
SIB_DEATH = os.path.join(os.path.dirname(HERE),
                         "2026-10-06-structural-death")
for p in (HERE, SIB_AND, SIB_DEATH):
    if p not in sys.path:
        sys.path.insert(0, p)

import trap_census  # noqa: E402
from tiles_and import BUILDS  # noqa: E402
from tiles_death import build_missing_species  # noqa: E402
from atam_check_and import matched_strength  # noqa: E402

T_READ_MULTIPLIER = 400.0
BASE_SEED = 20261107
GSE = 9.0
GMC_GRID = (9.5, 11.0, 13.0)
N_PER_POINT = 500
REMOVALS = ("Vp", "V0p", "D1T", "D2T", "DAr", "DBr", "L3")
TICK23_PQR = {  # reference from evidence/2026-10-06-species-death-survey
    "build1": {0.5: 0.540, 2.0: 0.794, 4.0: 0.986},
    "D1T": {0.5: 0.584, 2.0: 0.822, 4.0: 0.966},
    "D2T": {0.5: 0.544, 2.0: 0.748, 4.0: 0.976},
    "V0p": {0.5: 0.674, 2.0: 0.772, 4.0: 0.932},
    "Vp": {0.5: 0.824, 2.0: 0.928, 4.0: 0.648},
    "DAr": {0.5: 0.476, 2.0: 0.660, 4.0: 0.700},
    "DBr": {0.5: 0.242, 2.0: 0.116, 4.0: 0.020},
    "L3": {0.5: 0.036, 2.0: 0.010, 4.0: 0.0},
}
CANON = dict(trap_census.CANON)
LOCK_SITES = ((3, 1), (3, 2), (3, 3))
SITES = sorted(CANON)
READERS = {"p": ("D1T", (1, 1)), "q": ("D2T", (1, 2)),
           "r": ("DBr", (2, 3))}


class TrapAPI(object):
    def __init__(self, build):
        self.build = build
        name = build["name"]
        self.removed = (name.rsplit("_missing_", 1)[-1]
                        if "_missing_" in name else None)
        self.vacancy = (trap_census.CANON_RSITE[self.removed]
                        if self.removed else None)

    def tiles(self):
        return self.build["tiles"]

    def seed(self):
        return {(x, 0): "seed" + str(x) for x in range(4)}

    def sites(self):
        return SITES

    def matched(self, assembly, site, tile):
        return matched_strength(self.build, assembly, site, tile)

    def neighbour(self, assembly, site):
        return any((site[0] + dx, site[1] + dy) in assembly
                   for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)))

    def decode(self, assembly):
        b = self.build
        spined = all(assembly.get((0, r)) == "S%d" % r for r in (1, 2, 3))
        locks = [assembly.get((3, r)) for r in (1, 2, 3)]
        locked = all(l is not None and str(l).startswith("L")
                     for l in locks)
        if not spined or not locked:
            return "partial"
        true_atoms = []
        for y, atom in b["rows"].items():
            lock = assembly[(3, y)]
            if b["tiles"][lock]["W"].endswith("-t"):
                true_atoms.append(atom)
        return "".join(true_atoms) if true_atoms else "empty"

    def decode_loose(self, assembly):
        bits = "".join(atom for atom, (tile, site) in
                       sorted(READERS.items())
                       if assembly.get(site) == tile)
        return bits if bits else "empty"


def build_systems():
    sys_list = [TrapAPI(BUILDS["build1"])]
    for sp in REMOVALS:
        sys_list.append(TrapAPI(build_missing_species(BUILDS["build1"], sp)))
    return sys_list


SYSTEMS = build_systems()


def lock_squats(assembly):
    """(blocked_any, Counter of 'site:tile' squatters at lock sites)."""
    blocked = False
    ctr = Counter()
    for site in LOCK_SITES:
        occ = assembly.get(site)
        if occ is not None and occ != CANON[site]:
            blocked = True
            ctr["%d,%d:%s" % (site[0], site[1], occ)] += 1
    return blocked, ctr


def run_assembly(api, Gmc, Gse, T_read, seed):
    """Protocol of record (ktam_mc_survey.run_assembly verbatim),
    returning the read-time assembly for the census."""
    rng = random.Random(seed)
    rf = math.exp(-Gmc)
    tiles = api.tiles()
    assembly = api.seed()
    sites = api.sites()
    t = 0.0
    while True:
        events = []
        for site in sites:
            if site in assembly:
                b = api.matched(assembly, site, assembly[site])
                events.append((math.exp(-b * Gse), "detach", site))
            elif api.neighbour(assembly, site):
                for tile in tiles:
                    if api.matched(assembly, site, tile) >= 1:
                        events.append((rf, "attach", (site, tile)))
        total = sum(r for r, _, _ in events)
        if total <= 0 or t > T_read:
            break
        t += rng.expovariate(total)
        if t > T_read:
            break
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
    return assembly


def point_chunk(args):
    sys_idx, Gmc, seed0, n = args
    api = SYSTEMS[sys_idx]
    T_read = T_READ_MULTIPLIER * math.exp(Gmc)
    outs = []
    for i in range(n):
        asm = run_assembly(api, Gmc, GSE, T_read, seed0 + i)
        strict = api.decode(asm)
        blocked, squats = lock_squats(asm)
        vac = (asm.get(api.vacancy) if api.vacancy else None)
        outs.append((strict, api.decode_loose(asm), blocked,
                     dict(squats), vac,
                     {("%d,%d" % s): asm.get(s) for s in SITES
                      if asm.get(s) is not None}))
    return sys_idx, Gmc, outs


def main():
    smoke = len(sys.argv) > 1 and sys.argv[1] == "SMOKE"
    n_pp = 8 if smoke else N_PER_POINT
    grid = (9.5,) if smoke else GMC_GRID
    jobs = []
    for sys_idx in range(len(SYSTEMS)):
        for Gmc in grid:
            seed0 = (BASE_SEED + sys_idx * 10000000
                     + int(round((Gmc - GSE) * 1000)) * 10000)
            jobs.append((sys_idx, Gmc, seed0, n_pp))
    print(json.dumps({
        "Gse": GSE, "T_read_rule": "400*exp(Gmc)",
        "n_per_point": n_pp, "seed_base": BASE_SEED,
        "Gmc_grid": list(grid),
        "model": ("kTAM v3 no-mismatch + read-time 12-site census; "
                  "systems = build1 + 7 non-DEAD single-species "
                  "removals (tick-23 protocol of record)"),
        "trap_census": trap_census.compute()["systems"]["build1"],
        "predictions": [
            "R2 conditional-on-clean-locks pqr rates of build1/V0p/Vp "
            "at dG 0.5 agree within 0.10 [gap >= 0.15]",
            "R3a build1 non-pqr blockers at (3,2)=Vp,(3,1)=V0p top-1 "
            "[any other tile top-1]",
            "R3b V0p-missing pqr has D1T@(2,1) and Vp-missing pqr has "
            "D2T@(2,2) in >= 50% [majority other/None]",
            "R3c L3-missing pqr at dG 0.5: L2@(3,3) with Vp-or-D2T@(2,3) "
            "in >= 2/3 [L2 < 0.5]",
            "R4 build1 lock-squat rate monotone down in dG; Vp ratio "
            "< 1 by dG 4 [non-monotone or ratio >= 1]"],
        "tick23_reference_pqr": TICK23_PQR,
    }), flush=True)
    with Pool(min(16, os.cpu_count() or 1)) as pool:
        results = pool.map(point_chunk, jobs)
    by_sys = {}
    for sys_idx, Gmc, outs in results:
        by_sys.setdefault(sys_idx, {})[Gmc] = outs
    base = {}
    for Gmc in grid:
        c = Counter(o[0] for o in by_sys[0][Gmc])
        base[Gmc] = c.get("pqr", 0) / float(n_pp)
    rows = {}
    for sys_idx, api in enumerate(SYSTEMS):
        for Gmc in grid:
            outs = by_sys[sys_idx][Gmc]
            n = len(outs)
            strict = Counter(o[0] for o in outs)
            loose = Counter(o[1] for o in outs)
            pqr = strict.get("pqr", 0)
            blocked = sum(1 for o in outs if o[2])
            pqr_blocked = sum(1 for o in outs if o[2] and o[0] == "pqr")
            pqr_clean = pqr - pqr_blocked
            squat_ctr = Counter()
            squat_pqr_ctr = Counter()
            for o in outs:
                squat_ctr.update(o[3])
                if o[0] == "pqr":
                    squat_pqr_ctr.update(o[3])
            vac_pqr = Counter()
            vac_all = Counter()
            if api.vacancy:
                for o in outs:
                    vac_all[o[4] or "None"] += 1
                    if o[0] == "pqr":
                        vac_pqr[o[4] or "None"] += 1
            census_pqr = Counter()
            for o in outs:
                if o[0] == "pqr":
                    # NOTE: never Counter.update(a str-valued dict) — the
                    # empty-Counter fast path silently copies the strings,
                    # then string-concatenates, and only raises on a novel
                    # key (v1 job died exactly here). Count "site:tile"
                    # pairs instead, matching the R3c keys.
                    census_pqr.update(
                        "%s:%s" % kv for kv in o[5].items())
            key = api.removed or "build1"
            row = {
                "system": api.build["name"], "key": key,
                "Gmc": Gmc, "dGmc": round(Gmc - GSE, 1), "n": n,
                "decode": dict(sorted(strict.items())),
                "decode_loose": dict(sorted(loose.items())),
                "pqr": pqr, "pqr_frac": round(pqr / float(n), 4),
                "build1_pqr_frac": round(base[Gmc], 4),
                "ratio": (round(pqr / float(n) / base[Gmc], 4)
                          if base[Gmc] else None),
                "blocked_traj": blocked,
                "blocked_frac": round(blocked / float(n), 4),
                "pqr_and_blocked": pqr_blocked,
                "pqr_clean_frac": (round(pqr_clean /
                                         float(n - blocked), 4)
                                   if n - blocked else None),
                "lock_squats": dict(sorted(squat_ctr.items())),
                "lock_squats_pqr": dict(sorted(squat_pqr_ctr.items())),
                "vacancy_pqr": (dict(sorted(vac_pqr.items()))
                                if api.vacancy else None),
                "vacancy_all": (dict(sorted(vac_all.items()))
                                if api.vacancy else None),
                "census_pqr": dict(sorted(census_pqr.items())),
            }
            rows.setdefault(key, {})[str(Gmc)] = row
            print(json.dumps(row), flush=True)
    # ---- machine verdicts against the pre-registration -------------
    verdicts = {}
    dg05 = [g for g in grid if round(g - GSE, 1) == 0.5]
    if dg05:
        g = dg05[0]
        cond = {k: rows[k][str(g)]["pqr_clean_frac"]
                for k in ("build1", "V0p", "Vp")}
        vals = [v for v in cond.values() if v is not None]
        verdicts["R2"] = {
            "conditional_clean_pqr": cond,
            "max_gap": (round(max(vals) - min(vals), 4) if vals else None),
            "pass": bool(vals and max(vals) - min(vals) < 0.15),
        }
        sq = rows["build1"][str(g)]["lock_squats"]
        nonpqr_sq = Counter()
        # squats among non-pqr: approximate with all-minus-pqr counters
        allsq = Counter(rows["build1"][str(g)]["lock_squats"])
        pqrsq = Counter(rows["build1"][str(g)]["lock_squats_pqr"])
        for k, v in allsq.items():
            rem = v - pqrsq.get(k, 0)
            if rem > 0:
                nonpqr_sq[k] = rem
        top32 = [k for k, _ in sorted(nonpqr_sq.items(), key=lambda x: -x[1])
                 if k.startswith("3,2:")][:1]
        top31 = [k for k, _ in sorted(nonpqr_sq.items(), key=lambda x: -x[1])
                 if k.startswith("3,1:")][:1]
        verdicts["R3a"] = {
            "top_squat_3_2": top32, "top_squat_3_1": top31,
            "pass": bool(top32 == ["3,2:Vp"] and top31 == ["3,1:V0p"]),
        }
    for key, site, tile in (("V0p", "2,1", "D1T"), ("Vp", "2,2", "D2T")):
        dg = rows.get(key, {}).get(str(g)) if dg05 else None
        if dg:
            vac = dg["vacancy_pqr"] or {}
            tot = sum(vac.values())
            verdicts["R3b_" + key] = {
                "vacancy_pqr": vac,
                "frac": round(vac.get(tile, 0) / float(tot), 4) if tot else None,
                "pass": bool(tot and vac.get(tile, 0) / float(tot) >= 0.5),
            }
    if dg05:
        g = dg05[0]
        dg = rows.get("L3", {}).get(str(g))
        if dg:
            cen = dg["census_pqr"]
            n_pqr = dg["pqr"]
            l2_33 = cen.get("3,3:L2", 0)
            west_ok = (cen.get("2,3:Vp", 0) + cen.get("2,3:D2T", 0))
            verdicts["R3c"] = {
                "pqr": n_pqr, "L2_at_3_3": l2_33,
                "L2_frac": round(l2_33 / float(n_pqr), 4) if n_pqr else None,
                "west_Vp_or_D2T_frac": (round(west_ok / float(n_pqr), 4)
                                        if n_pqr else None),
                "pass": bool(n_pqr and l2_33 / float(n_pqr) >= 0.5
                             and west_ok / float(n_pqr) >= 0.5),
            }
    bl = [rows["build1"][str(g2)]["blocked_frac"]
          for g2 in sorted(grid)]
    mono = all(bl[i] >= bl[i + 1] for i in range(len(bl) - 1))
    r_4 = None
    g4 = [g for g in grid if round(g - GSE, 1) == 4.0]
    if g4:
        r_4 = rows["Vp"][str(g4[0])]["ratio"]
    verdicts["R4"] = {
        "build1_blocked_by_dG": bl, "monotone_down": mono,
        "Vp_ratio_dG4": r_4,
        "pass": bool(mono and r_4 is not None and r_4 < 1.0),
    }
    print(json.dumps({"verdicts": verdicts}), flush=True)


if __name__ == "__main__":
    main()
