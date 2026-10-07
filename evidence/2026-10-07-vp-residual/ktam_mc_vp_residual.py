"""kTAM Vp-residual dissection — n=2000 history-tracking arm
(tick 26, SON-4778).

The tick-24/25 repair-mechanism grid confirmed R2 with the Vp arm
carrying a residual: conditioned on read-time-clean lock columns,
strict "pqr" at dG 0.5 is 0.927 in Vp-missing vs 0.7813 in build1
(gap 0.1457 — inside the 0.15 falsifier, outside the 0.10 target).
Either a second-order Vp effect survives the conditioning, or the
read-time conditioning itself selects (a trajectory can visit an
off-channel squatter, be delayed, and still be clean at read).
This run separates the two: n=2000 per arm at dG 0.5 only, plus
FULL-HISTORY tracking — per-trajectory ever-visited flags and
cumulative off-channel DWELL time (how long non-canonical tiles
held canonical sites), reported for the read-clean pqr and
read-clean non-pqr cohorts of build1.

Instrument: the tick-23/24 protocol of record (Gse=9, Gmc=9.5,
T_read = 400*e^Gmc, no-mismatch kTAM, per-run RNG, deterministic
seeds).  Fresh seed base 40261107 — disjoint from the v2 grid's
block (20261107 + sys*10^7), so samples are independent.  Systems:
build1 + Vp-missing only.  2 x 2000 = 4,000 trajectories.

Pre-registered BEFORE this MC runs (falsifiers in brackets):

P1 (residual is real at power): the read-time-clean conditional
    strict-"pqr" gap (Vp-missing minus build1) at dG 0.5 is
    >= 0.10  [gap < 0.08: the n=500 residual was selection/noise;
    0.08 <= gap < 0.10: inconclusive band — design a dwell-matched
    conditioning study rather than re-running blind].
P2 (the residual is visitation delay): among build1 read-time-clean
    trajectories at dG 0.5, mean lock-site squatter dwell in the
    non-pqr cohort is >= 2x that in the pqr cohort  [ratio <= 1.0:
    dwell does not separate the cohorts, so the residual is not
    lock-squat delay; 1.0 < ratio < 2.0 inconclusive].  Secondary
    (reported, unregistered): ever-visited fractions and any-site
    dwell for the same cohorts.
P3 (calibration): read-time-clean conditional "pqr" of build1 and
    of Vp-missing at n=2000 each within 0.05 of the v2 values
    (0.7813 / 0.927)  [either deviates >= 0.08: protocol drift —
    stop interpreting].

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
SIB_REPAIR = os.path.join(os.path.dirname(HERE),
                          "2026-10-07-repair-mechanism")
for p in (HERE, SIB_AND, SIB_DEATH, SIB_REPAIR):
    if p not in sys.path:
        sys.path.insert(0, p)

import trap_census  # noqa: E402
from tiles_and import BUILDS  # noqa: E402
from tiles_death import build_missing_species  # noqa: E402
from atam_check_and import matched_strength  # noqa: E402

GSE = 9.0
GMC = 9.5
BASE_SEED = 40261107
N_PER_ARM = 2000
T_READ_MULTIPLIER = 400.0
CANON = dict(trap_census.CANON)
CANON_RSITE = dict(trap_census.CANON_RSITE)
LOCK_SITES = ((3, 1), (3, 2), (3, 3))
SITES = sorted(CANON)
READERS = {"p": ("D1T", (1, 1)), "q": ("D2T", (1, 2)),
           "r": ("DBr", (2, 3))}
V2_CLEAN = {"build1": 0.7813, "Vp": 0.927}  # evidence/.../trap_grid.out


class ArmAPI(object):
    def __init__(self, build):
        self.build = build
        name = build["name"]
        self.removed = (name.rsplit("_missing_", 1)[-1]
                        if "_missing_" in name else None)
        self.vacancy = CANON_RSITE.get(self.removed)

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
    return [ArmAPI(BUILDS["build1"]),
            ArmAPI(build_missing_species(BUILDS["build1"], "Vp"))]


SYSTEMS = build_systems()


def run_assembly_history(api, Gmc, Gse, T_read, seed):
    """Protocol of record + history tracking.  Returns (assembly,
    ever_off_any, ever_lock, dwell_any, dwell_lock) where dwell_* sum
    the time canonical sites were held by NON-canonical occupants
    (closed at read time for occupants still present)."""
    rng = random.Random(seed)
    rf = math.exp(-Gmc)
    tiles = api.tiles()
    assembly = api.seed()
    sites = api.sites()
    ever_off_any = False
    ever_lock = False
    sq_since = {}
    dwell_any = 0.0
    dwell_lock = 0.0
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
                    if arg[1] != CANON[arg[0]]:
                        ever_off_any = True
                        sq_since[arg[0]] = t
                        if arg[0] in LOCK_SITES:
                            ever_lock = True
                else:
                    if arg in sq_since:
                        dt = t - sq_since.pop(arg)
                        dwell_any += dt
                        if arg in LOCK_SITES:
                            dwell_lock += dt
                    del assembly[arg]
                break
    now = t if t < T_read else T_read
    for site, t0 in sq_since.items():
        dt = now - t0
        if dt > 0:
            dwell_any += dt
            if site in LOCK_SITES:
                dwell_lock += dt
    return assembly, ever_off_any, ever_lock, dwell_any, dwell_lock


def read_lock_squats(assembly):
    blocked = False
    ctr = Counter()
    for site in LOCK_SITES:
        occ = assembly.get(site)
        if occ is not None and occ != CANON[site]:
            blocked = True
            ctr["%d,%d:%s" % (site[0], site[1], occ)] += 1
    return blocked, ctr


def arm_chunk(args):
    sys_idx, seed0, n = args
    api = SYSTEMS[sys_idx]
    T_read = T_READ_MULTIPLIER * math.exp(GMC)
    outs = []
    for i in range(n):
        asm, e_any, e_lock, d_any, d_lock = run_assembly_history(
            api, GMC, GSE, T_read, seed0 + i)
        strict = api.decode(asm)
        blocked, squats = read_lock_squats(asm)
        vac = (asm.get(api.vacancy) if api.vacancy else None)
        outs.append((strict, api.decode_loose(asm), blocked,
                     dict(squats), vac, e_any, e_lock, d_any, d_lock,
                     {("%d,%d" % s): asm.get(s) for s in SITES
                      if asm.get(s) is not None}))
    return sys_idx, outs


def cohort_stats(outs, keep):
    sel = [o for o in outs if keep(o)]
    n = len(sel)
    return {
        "n": n,
        "ever_off_any_frac": (round(sum(1 for o in sel if o[5]) /
                                    float(n), 4) if n else None),
        "ever_lock_frac": (round(sum(1 for o in sel if o[6]) /
                                 float(n), 4) if n else None),
        "mean_dwell_any": (round(sum(o[7] for o in sel) / float(n), 4)
                           if n else None),
        "mean_dwell_lock": (round(sum(o[8] for o in sel) / float(n), 4)
                            if n else None),
    }


def main():
    smoke = len(sys.argv) > 1 and sys.argv[1] == "SMOKE"
    n = 8 if smoke else N_PER_ARM
    jobs = [(i, BASE_SEED + i * 10000000, n) for i in range(len(SYSTEMS))]
    cen = trap_census.compute()["systems"]["build1"]
    print(json.dumps({
        "Gse": GSE, "Gmc": GMC, "dGmc": round(GMC - GSE, 1),
        "T_read_rule": "400*exp(Gmc)", "n_per_arm": n,
        "seed_base": BASE_SEED,
        "model": ("kTAM v3 no-mismatch + full-history off-channel "
                  "tracking (ever-visited flags, dwell time); systems "
                  "= build1 + Vp-missing at dG 0.5 only"),
        "trap_census_build1": {
            "off_channel": cen["off_channel"],
            "off_channel_sites_per_species":
                cen["off_channel_sites_per_species"]},
        "predictions": [
            "P1 clean-conditional gap (Vp minus build1) >= 0.10 "
            "[< 0.08 falsified; 0.08-0.10 inconclusive]",
            "P2 build1 clean non-pqr mean lock dwell >= 2x clean pqr "
            "[ratio <= 1.0 falsified; 1.0-2.0 inconclusive]",
            "P3 clean-conditional within 0.05 of 0.7813/0.927 "
            "[either >= 0.08 drift]"],
        "v2_reference_clean": V2_CLEAN,
    }), flush=True)
    with Pool(min(8, os.cpu_count() or 1)) as pool:
        results = pool.map(arm_chunk, jobs)
    rows = {}
    for sys_idx, outs in results:
        api = SYSTEMS[sys_idx]
        key = api.removed or "build1"
        nn = len(outs)
        strict = Counter(o[0] for o in outs)
        loose = Counter(o[1] for o in outs)
        pqr = strict.get("pqr", 0)
        blocked = sum(1 for o in outs if o[2])
        pqr_blocked = sum(1 for o in outs if o[2] and o[0] == "pqr")
        squat_ctr = Counter()
        squat_pqr_ctr = Counter()
        census_pqr = Counter()
        vac_pqr = Counter()
        vac_all = Counter()
        for o in outs:
            squat_ctr.update(o[3])
            if o[0] == "pqr":
                squat_pqr_ctr.update(o[3])
                census_pqr.update("%s:%s" % kv for kv in o[9].items())
            if api.vacancy:
                vac_all[o[4] or "None"] += 1
                if o[0] == "pqr":
                    vac_pqr[o[4] or "None"] += 1
        clean = [o for o in outs if not o[2]]
        row = {
            "system": api.build["name"], "key": key, "n": nn,
            "decode": dict(sorted(strict.items())),
            "decode_loose": dict(sorted(loose.items())),
            "pqr": pqr, "pqr_frac": round(pqr / float(nn), 4),
            "blocked_traj": blocked,
            "blocked_frac": round(blocked / float(nn), 4),
            "pqr_and_blocked": pqr_blocked,
            "pqr_clean_frac": (round((pqr - pqr_blocked) /
                                     float(nn - blocked), 4)
                               if nn - blocked else None),
            "clean_pqr": cohort_stats(outs, lambda o: (not o[2]) and
                                      o[0] == "pqr"),
            "clean_nonpqr": cohort_stats(outs, lambda o: (not o[2]) and
                                         o[0] != "pqr"),
            "all_traj": cohort_stats(outs, lambda o: True),
            "lock_squats": dict(sorted(squat_ctr.items())),
            "lock_squats_pqr": dict(sorted(squat_pqr_ctr.items())),
            "vacancy_pqr": (dict(sorted(vac_pqr.items()))
                            if api.vacancy else None),
            "vacancy_all": (dict(sorted(vac_all.items()))
                            if api.vacancy else None),
            "census_pqr": dict(sorted(census_pqr.items())),
        }
        rows[key] = row
        print(json.dumps(row), flush=True)
    # ---- machine verdicts against the pre-registration -------------
    verdicts = {}
    cb = rows["build1"]["pqr_clean_frac"]
    cv = rows["Vp"]["pqr_clean_frac"]
    gap = round(cv - cb, 4) if (cb is not None and cv is not None) else None
    verdicts["P1"] = {
        "build1_clean": cb, "Vp_clean": cv, "gap": gap,
        "call": ("real" if gap is not None and gap >= 0.10 else
                 "falsified" if gap is not None and gap < 0.08 else
                 "inconclusive"),
    }
    dp = rows["build1"]["clean_pqr"]["mean_dwell_lock"]
    dn = rows["build1"]["clean_nonpqr"]["mean_dwell_lock"]
    ratio = (round(dn / dp, 4) if (dp not in (None, 0.0) and
                                   dn is not None) else None)
    verdicts["P2"] = {
        "clean_pqr_dwell_lock": dp,
        "clean_nonpqr_dwell_lock": dn,
        "ratio": ratio,
        "call": ("delay" if ratio is not None and ratio >= 2.0 else
                 "falsified" if ratio is not None and ratio <= 1.0 else
                 "inconclusive"),
    }
    dev_b = (round(abs(cb - V2_CLEAN["build1"]), 4)
             if cb is not None else None)
    dev_v = (round(abs(cv - V2_CLEAN["Vp"]), 4)
             if cv is not None else None)
    ok = (dev_b is not None and dev_v is not None and
          dev_b < 0.05 and dev_v < 0.05)
    drift = (dev_b is not None and dev_v is not None and
             (dev_b >= 0.08 or dev_v >= 0.08))
    verdicts["P3"] = {
        "build1_dev": dev_b, "Vp_dev": dev_v,
        "call": ("calibrated" if ok else
                 "drift" if drift else "inconclusive"),
    }
    print(json.dumps({"verdicts": verdicts}), flush=True)


if __name__ == "__main__":
    main()
