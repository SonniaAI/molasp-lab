"""kTAM validation of the row-scope prediction (tick 30, SON-4778).

Tick 29 evaluated ``lock_glue_scope`` statically: row scope zeroes
the lock-hazard and lock-misread classes on BUILD1 (canonical
assembly intact, every site >= tau=2) and kills the stable b=2
substitution repair (repair bonds D1T/D2T 2/2 -> 1/1).  Tick 30
closed the false-family boundary (BUILD3 Fp@(3,3), BUILD2
Vp@(3,2)/Fr@(3,3) die under the -f/-f-done extension).  This run
is the kinetic arm of that evaluation: does the static prediction
survive the no-mismatch kTAM at the protocol's measured point
(dG 0.5)?

Instrument: the tick-23/24 protocol of record (Gse=9, Gmc=9.5,
T_read = 400*e^Gmc, no-mismatch kTAM, per-run RNG, deterministic
seeds).  Fresh seed base 80261107 with 2e7 block spacing —
disjoint from the v2 grid block (20261107 + sys*1e7) and the
vp-residual block (40261107 + sys*1e7).  Systems: BUILD1 under
family scope and under row scope, each plain / Vp-missing /
L3-missing.  6 x 500 = 3,000 trajectories at dG 0.5 only.

Pre-registered BEFORE this MC runs (falsifiers in brackets):

RS1 (lock-squat elimination): read-time lock-squat blocked frac of
    row build1 <= 0.02  [>= 0.10 falsified; 0.02-0.10 inconclusive].
    Family reference: v2 measured 0.314 at the same point.
RS2 (substitution-repair elimination): read-time STABLE D2T@(2,2)
    occupancy (matched bond >= 2) over ALL terminals of row
    Vp-missing <= 0.02  [>= 0.10 falsified; 0.02-0.10 inconclusive].
    Family reference: D2T fills the Vp vacancy in 90.1% of
    strict-pqr terminals at b=2 (v2).  NOTE (design lesson from
    the n=8 smoke, 2026-10-07): raw read-time occupancy is the
    WRONG metric — a b=1 transient hold has equilibrium occupancy
    rf/(rf+exp(-Gse)) ~ 0.38 at this protocol point, and the smoke
    showed ~0.5 raw fill under row scope with zero stable holds;
    the stable/unstable split IS the tick-29 static claim
    ("degrades 2 -> 1 transient holds"), so that is what is
    gated.  Raw fill is reported alongside for the record.
    Second smoke observation (same n=8): one terminal held a
    STABLE (b=2) D2T@(2,2) under row scope — a D2T+Vp MUTUAL PAIR
    (D2T's S relay bond + an E-face pair with a Vp lock-squat at
    (3,2)) reconstituting b=2 from two b=1 channels.  RS2 there-
    fore carries a genuine recombination risk into n=500; the
    gate stands as registered and the receipt decides.
RS3 (no new channel opens): (a) L2@(3,3) misread frac over all
    terminals of row L3-missing <= 0.02  [>= 0.10 falsified];
    AND (b) strict-pqr frac of row build1 >= family build1 - 0.10
    [< family - 0.10 falsified: row scope broke canonical kinetics].
    Family reference: 23/23 of L3-missing strict decodes were the
    misread (v2, fraction 1.0 of strict; 0.046 of all terminals).
RS4 (calibration): family build1 blocked frac within 0.05 of 0.314
    AND family Vp-missing D2T fill among strict-pqr terminals
    within 0.10 of 0.901  [either off by >= 0.15: protocol drift —
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
# HERE = <repo>/evidence/2026-10-07-row-scope-ktam; dirname(HERE) =
# evidence/; dirname^2(HERE) = repo root (where the molasp package
# lives — one dirname short lands on evidence/ and the import fails)
REPO = os.path.dirname(os.path.dirname(HERE))
SIB_AND = os.path.join(os.path.dirname(HERE),
                       "2026-10-06-body-conjunction-builds")
SIB_DEATH = os.path.join(os.path.dirname(HERE),
                         "2026-10-06-structural-death")
SIB_REPAIR = os.path.join(os.path.dirname(HERE),
                          "2026-10-07-repair-mechanism")
for p in (HERE, REPO, SIB_AND, SIB_DEATH, SIB_REPAIR):
    if p not in sys.path:
        sys.path.insert(0, p)

import trap_census  # noqa: E402
from tiles_and import BUILD1  # noqa: E402
from tiles_death import build_missing_species  # noqa: E402
from atam_check_and import matched_strength  # noqa: E402
from molasp.offchannel import (  # noqa: E402
    apply_lock_glue_scope, canonical_assembly, lock_glue_scope_reports)

GSE = 9.0
GMC = 9.5
BASE_SEED = 80261107
SEED_STRIDE = 20000000
N_PER_ARM = 500
T_READ_MULTIPLIER = 400.0
CANON = dict(trap_census.CANON)
LOCK_SITES = ((3, 1), (3, 2), (3, 3))
SITES = sorted(CANON)
READERS = {"p": ("D1T", (1, 1)), "q": ("D2T", (1, 2)),
           "r": ("DBr", (2, 3))}
V2_REFS = {"build1_blocked": 0.314, "Vp_fill_strict_pqr": 0.901}


class ArmAPI(object):
    def __init__(self, build, scope):
        self.build = build
        self.scope = scope
        name = build["name"]
        self.removed = (name.rsplit("_missing_", 1)[-1]
                        if "_missing_" in name else None)
        self.vacancy = trap_census.CANON_RSITE.get(self.removed)

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
        # scope-aware: under row scope lock W glues read
        # "{atom}-t-lk{y}" — still the atom's TRUE family; a false
        # family lock ("{atom}-f[-lk{i}]") still decodes FALSE.
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
            if b["tiles"][lock]["W"].startswith(atom + "-t"):
                true_atoms.append(atom)
        return "".join(true_atoms) if true_atoms else "empty"

    def decode_loose(self, assembly):
        bits = "".join(atom for atom, (tile, site) in
                       sorted(READERS.items())
                       if assembly.get(site) == tile)
        return bits if bits else "empty"


def build_systems():
    systems = []
    for scope in ("family", "row"):
        base = apply_lock_glue_scope(BUILD1, scope)
        systems.append(ArmAPI(base, scope))
        systems.append(ArmAPI(build_missing_species(base, "Vp"), scope))
        systems.append(ArmAPI(build_missing_species(base, "L3"), scope))
    return systems


SYSTEMS = build_systems()


def run_assembly(api, Gmc, Gse, T_read, seed):
    """Protocol of record (tick 23/24): no-mismatch kTAM, attach
    rate exp(-Gmc) at neighbour-exposed sites for bonds >= 1,
    detach rate exp(-b*Gse), read at T_read."""
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
        asm = run_assembly(api, GMC, GSE, T_read, seed0 + i)
        strict = api.decode(asm)
        blocked, squats = read_lock_squats(asm)
        vac = (asm.get(api.vacancy) if api.vacancy else None)
        vac_stable = (vac == "D2T" and api.vacancy is not None and
                      api.matched(asm, api.vacancy, "D2T") >= 2)
        misread = asm.get((3, 3)) == "L2"
        outs.append((strict, blocked, dict(squats), vac, vac_stable,
                     misread))
    return sys_idx, outs


def main():
    smoke = len(sys.argv) > 1 and sys.argv[1] == "SMOKE"
    n = 8 if smoke else N_PER_ARM
    jobs = [(i, BASE_SEED + i * SEED_STRIDE, n)
            for i in range(len(SYSTEMS))]
    canon = canonical_assembly(BUILD1)
    reports = lock_glue_scope_reports(BUILD1, canon)
    print(json.dumps({
        "Gse": GSE, "Gmc": GMC, "dGmc": round(GMC - GSE, 1),
        "T_read_rule": "400*exp(Gmc)", "n_per_arm": n,
        "seed_base": BASE_SEED, "seed_stride": SEED_STRIDE,
        "model": ("kTAM v3 no-mismatch; systems = BUILD1 x "
                  "{family,row} x {plain, Vp-missing, L3-missing} "
                  "at dG 0.5 only; read-time census, no history"),
        "static_prediction": {
            "family_lock_hazards": reports["family"]["lock_hazards"],
            "row_lock_hazards": reports["row"]["lock_hazards"],
            "row_lock_misreads": reports["row"]["lock_misreads"],
            "repair_bonds": reports["repair_bonds"]},
        "predictions": [
            "RS1 row build1 read-lock-squat blocked frac <= 0.02 "
            "[>= 0.10 falsified; 0.02-0.10 inconclusive]",
            "RS2 row Vp-missing STABLE D2T@(2,2) (bond>=2) over all "
            "terminals <= 0.02 [>= 0.10 falsified; 0.02-0.10 "
            "inconclusive; raw b=1-transient occupancy ~0.38 at "
            "equilibrium is expected and reported, not gated]",
            "RS3 row L3-missing L2@(3,3) misread frac <= 0.02 "
            "[>= 0.10 falsified] AND row build1 strict-pqr >= "
            "family - 0.10 [< family - 0.10 falsified]",
            "RS4 family build1 blocked within 0.05 of 0.314 AND "
            "family Vp fill among strict-pqr within 0.10 of 0.901 "
            "[either >= 0.15 off: protocol drift]"],
        "v2_reference": V2_REFS,
    }), flush=True)
    with Pool(min(8, os.cpu_count() or 1)) as pool:
        results = pool.map(arm_chunk, jobs)
    rows = {}
    for sys_idx, outs in results:
        api = SYSTEMS[sys_idx]
        key = (api.scope + "_" + (api.removed or "build1"))
        nn = len(outs)
        strict = Counter(o[0] for o in outs)
        blocked = sum(1 for o in outs if o[1])
        squat_ctr = Counter()
        vac_all = Counter()
        vac_pqr = Counter()
        stable_all = 0
        misread_n = sum(1 for o in outs if o[5])
        for o in outs:
            squat_ctr.update(o[2])
            if o[4]:
                stable_all += 1
            if api.vacancy:
                vac_all[o[3] or "None"] += 1
                if o[0] == "pqr":
                    vac_pqr[o[3] or "None"] += 1
        pqr = strict.get("pqr", 0)
        row = {
            "system": api.build["name"], "key": key, "n": nn,
            "decode": dict(sorted(strict.items())),
            "pqr": pqr, "pqr_frac": round(pqr / float(nn), 4),
            "blocked_frac": round(blocked / float(nn), 4),
            "lock_squats": dict(sorted(squat_ctr.items())),
            "vacancy_all": (dict(sorted(vac_all.items()))
                            if api.vacancy else None),
            "vacancy_pqr": (dict(sorted(vac_pqr.items()))
                            if api.vacancy else None),
            "vacancy_stable_fill_all": (round(stable_all / float(nn), 4)
                                        if api.vacancy else None),
            "misread_L2_at_3_3": misread_n,
            "misread_frac": round(misread_n / float(nn), 4),
        }
        rows[key] = row
        print(json.dumps(row), flush=True)

    # ---- machine verdicts against the pre-registration -----------
    def fill_all(key):
        v = rows[key]["vacancy_all"] or {}
        d = float(sum(v.values()))
        return (round(v.get("D2T", 0) / d, 4) if d else None)

    def fill_pqr(key):
        v = rows[key]["vacancy_pqr"] or {}
        d = float(sum(v.values()))
        return (round(v.get("D2T", 0) / d, 4) if d else None)

    verdicts = {}
    rb = rows["row_build1"]["blocked_frac"]
    verdicts["RS1"] = {
        "row_build1_blocked_frac": rb,
        "call": ("confirmed" if rb <= 0.02 else
                 "falsified" if rb >= 0.10 else "inconclusive"),
    }
    rf_ = rows["row_Vp"]["vacancy_stable_fill_all"]
    verdicts["RS2"] = {
        "row_Vp_D2T_stable_fill_all": rf_,
        "row_Vp_raw_fill_all": fill_all("row_Vp"),
        "call": ("confirmed" if rf_ is not None and rf_ <= 0.02 else
                 "falsified" if rf_ is not None and rf_ >= 0.10 else
                 "inconclusive"),
    }
    rm = rows["row_L3"]["misread_frac"]
    dp = round(rows["row_build1"]["pqr_frac"] -
               rows["family_build1"]["pqr_frac"], 4)
    verdicts["RS3"] = {
        "row_L3_misread_frac": rm,
        "row_minus_family_pqr_frac": dp,
        "call": ("confirmed" if (rm <= 0.02 and dp >= -0.10) else
                 "falsified"),
    }
    fb = rows["family_build1"]["blocked_frac"]
    fp = fill_pqr("family_Vp")
    drift = max(abs(fb - V2_REFS["build1_blocked"]),
                abs((fp if fp is not None else 1.0) -
                    V2_REFS["Vp_fill_strict_pqr"]))
    verdicts["RS4"] = {
        "family_build1_blocked_frac": fb,
        "family_Vp_D2T_fill_strict_pqr": fp,
        "max_deviation": round(drift, 4),
        "call": ("calibrated" if drift < 0.15 else "protocol_drift"),
    }
    print("VERDICTS " + json.dumps(verdicts), flush=True)


if __name__ == "__main__":
    main()
