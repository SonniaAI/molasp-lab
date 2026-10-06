"""kTAM kinetics grid — designs/003 structural-death arm, tick 22
(SON-4773). K4's honest successor: the true-model completion is
structurally forbidden (one tile species missing), so ANY full
true-model strict decode at read time is kinetic reassertion with no
growth-incompletion confound (a strict decode requires the spine and
all three locks simultaneously; an unfinished assembly reads
"partial" by construction).

Protocol of record (unchanged from the tick-15/16/19 grids): Gse=9,
Gmc in {9.5, 11, 13, 16} => dG {0.5, 2, 4, 7}, T_read = 400*e^Gmc,
n = 500 trajectories/point, no-mismatch kTAM (attach k_f*e^-Gmc for
b >= 1, detach k_f*e^(-b*Gse), spine bonds count 2), per-run
independent RNG, deterministic seeds printed in the header.

Systems:
  build1  P_AND (calibration — must reproduce tick 19 within 2x)
  dead    P_AND_missing_DAr (BUILD1 minus species DAr; aTAM-dead
          row 3, see atam_death.py for the S1 receipt)

Pre-registered BEFORE running (lab discipline):

S2 (reassertion channel existence): dead strict "pqr" count > 0 at
    at least one grid point (>= 1/500). Structural note: in the dead
    build a strict "pqr" read requires L3 present at read time; L3
    can only be there via kTAM b=1 attachments (its aTAM bond is 1),
    alone (transient) or with DBr (mutual b=2 stabilization: DBr.E
    r-t bonds L3.W r-t). Both are counted; the row-3 state split
    separates the mechanisms.
    Falsifier: dead strict "pqr" total = 0 across the grid
    (CI95 upper 1.5e-3) — kinetics does NOT bypass the missing
    species; it is read-time visible only as a row-3 vacancy.
S3 (mechanism class, evaluated only if S2 > 0):
    (i) trapping-vs-floor: dead "pqr" fraction >= 10 * e^{-2dG} at
        dG=4 => near-miss trapping class (b=1 bridging), not the
        value-typing error floor;
    (ii) kinetic invisibility: dead/build1 "pqr" fraction ratio per
        point; ratio >= 0.5 at dG <= 2 reads "the missing species is
        kinetically invisible in the fast regime";
    (iii) the dG-slope of the dead "pqr" fraction is recorded as the
        detection-window lever (flat = invisible everywhere; decays
        = a slow-growth window exposes the missing species — the
        tick-10 escalate-don't-extend rule).
S4 (calibration): build1 strict "pqr" within 2x of the tick-19
    measured curve (0.540/0.790/0.984/0.870 per 500).
    Falsifier: build1 "pqr" < 0.5x tick-19 at any point.

Decode discipline (strict): spine S1/S2/S3 at (0,1..3) AND an
L-tile at every lock site (3,1..3); TRUE atoms = rows whose lock
tile bonds a "-t" value on W (tick-19 discipline). Loose: decision
readers only — p=D1T@(1,1), q=D2T@(1,2), r=DBr@(2,3) for BOTH
systems (the dead build keeps build1's readers: the question is
whether the readout is rebuilt, not which readers exist).

Row-3 state at read (dead mechanism split): dbr_l3 = DBr@(2,3) and
L3@(3,3) both present (mutually stabilized trap); l3_only = L3
present without DBr (b=1 transient caught at the read); dbr_only;
empty.
"""
import json
import math
import os
import random
import sys
from collections import Counter
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
SIBLING = os.path.join(os.path.dirname(HERE),
                       "2026-10-06-body-conjunction-builds")
for p in (HERE, SIBLING):
    if p not in sys.path:
        sys.path.insert(0, p)

from tiles_and import BUILDS  # noqa: E402
from tiles_death import BUILD_DEAD  # noqa: E402
from atam_check_and import matched_strength  # noqa: E402

T_READ_MULTIPLIER = 400.0
BASE_SEED = 20261022
GSE = 9.0
GMC_GRID = (9.5, 11.0, 13.0, 16.0)
N_PER_POINT = 500
# tick-19 measured build1 curve (evidence/2026-10-06-and-ktam-grid/)
TICK19_BUILD1 = {0.5: 0.540, 2.0: 0.790, 4.0: 0.984, 7.0: 0.870}

TRUE_READERS = {
    "P_AND_corrected": {"p": ("D1T", (1, 1)), "q": ("D2T", (1, 2)),
                        "r": ("DBr", (2, 3))},
    "P_AND_corrected_missing_DAr": {"p": ("D1T", (1, 1)),
                                    "q": ("D2T", (1, 2)),
                                    "r": ("DBr", (2, 3))},
}
SYSTEM_BUILDS = (BUILDS["build1"], BUILD_DEAD)


class AndAPI(object):
    EXPECTED = {"P_AND_corrected": "pqr",
                "P_AND_corrected_missing_DAr": "partial"}

    def __init__(self, build):
        self.name = build["name"]
        self.expected = AndAPI.EXPECTED[build["name"]]
        self.build = build
        self.readers = TRUE_READERS[build["name"]]

    def tiles(self):
        return self.build["tiles"]

    def seed(self):
        return {(x, 0): "seed" + str(x) for x in range(4)}

    def sites(self):
        return [(x, y) for y in (1, 2, 3) for x in (0, 1, 2, 3)]

    def matched(self, assembly, site, tile):
        return matched_strength(self.build, assembly, site, tile)

    def neighbour(self, assembly, site):
        return any((site[0] + dx, site[1] + dy) in assembly
                   for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)))

    def decode(self, assembly):
        b = self.build
        spined = all(assembly.get((0, r)) == "S%d" % r for r in (1, 2, 3))
        locks = {assembly.get((3, r)) for r in (1, 2, 3)}
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
                       sorted(self.readers.items())
                       if assembly.get(site) == tile)
        return bits if bits else "empty"

    def row3_state(self, assembly):
        dbr = assembly.get((2, 3)) == "DBr"
        l3 = str(assembly.get((3, 3), "")).startswith("L")
        if dbr and l3:
            return "dbr_l3"
        if l3:
            return "l3_only"
        if dbr:
            return "dbr_only"
        return "empty"


SYSTEMS = [AndAPI(b) for b in SYSTEM_BUILDS]


def run_assembly(api, Gmc, Gse, T_read, seed):
    """Verbatim protocol of record from ktam_mc_multirow.run_assembly,
    with the read-time row-3 state added to the return tuple."""
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
    return (api.decode(assembly), api.decode_loose(assembly),
            api.row3_state(assembly))


def point_chunk(args):
    sys_idx, Gmc, seed0, n = args
    api = SYSTEMS[sys_idx]
    T_read = T_READ_MULTIPLIER * math.exp(Gmc)
    out = [run_assembly(api, Gmc, GSE, T_read, seed0 + i)
           for i in range(n)]
    return sys_idx, Gmc, out


def main():
    jobs = []
    for sys_idx in range(len(SYSTEMS)):
        for Gmc in GMC_GRID:
            seed0 = (BASE_SEED + sys_idx * 10000000
                     + int(round((Gmc - GSE) * 1000)) * 10000)
            jobs.append((sys_idx, Gmc, seed0, N_PER_POINT))
    print(json.dumps({
        "Gse": GSE, "T_read_rule": "400*exp(Gmc)",
        "n_per_point": N_PER_POINT, "seed_base": BASE_SEED,
        "model": ("kTAM v3 no-mismatch, per-row value-typed locks, "
                  "4-column AND geometry (S|D|V|L), 3 rows; dead "
                  "system = build1 minus species DAr"),
        "systems": [{"idx": i, "name": a.name, "expected": a.expected}
                    for i, a in enumerate(SYSTEMS)],
        "predictions": [
            "S2 dead strict pqr > 0 somewhere (reassertion channel "
            "exists); falsifier: total 0, CI95 upper 1.5e-3",
            "S3i dead pqr frac >= 10*e^{-2dG} at dG=4 => trapping "
            "class; S3ii dead/build1 pqr ratio >= 0.5 at dG<=2 => "
            "kinetically invisible in fast regime; S3iii slope is "
            "the detection-window lever",
            "S4 build1 pqr within 2x of tick-19 "
            "(0.540/0.790/0.984/0.870)"],
        "tick19_build1_reference": TICK19_BUILD1,
    }), flush=True)
    with Pool(min(16, os.cpu_count() or 1)) as pool:
        results = pool.map(point_chunk, jobs)
    by_sys = {}
    for sys_idx, Gmc, decodes in results:
        strict = Counter(d[0] for d in decodes)
        loose = Counter(d[1] for d in decodes)
        r3 = Counter(d[2] for d in decodes)
        # joint strict x row3 split for the mechanism discriminator
        joint = Counter((d[0], d[2]) for d in decodes)
        by_sys.setdefault(sys_idx, {})[Gmc] = (strict, loose, r3, joint)
    for sys_idx, api in enumerate(SYSTEMS):
        ctrs = by_sys[sys_idx]
        for Gmc in GMC_GRID:
            c, cl, r3, joint = ctrs[Gmc]
            n = sum(c.values())
            dG = round(Gmc - GSE, 1)
            row = {
                "system": api.name, "Gmc": Gmc, "dGmc": dG, "n": n,
                "decode": dict(sorted(c.items())),
                "decode_loose": dict(sorted(cl.items())),
                "row3_state": dict(sorted(r3.items())),
                "pqr_joint_row3": {kk[1]: vv
                                   for kk, vv in sorted(joint.items())
                                   if kk[0] == "pqr"},
                "expected": api.expected,
                "expected_frac": round(c.get(api.expected, 0) / n, 4),
                "pqr_frac": round(c.get("pqr", 0) / n, 4),
                "tick19_build1": TICK19_BUILD1[dG],
                "curve_e_neg_dG": round(math.exp(-dG), 4),
                "curve_e_neg_2dG": round(math.exp(-2 * dG), 5),
            }
            print(json.dumps(row), flush=True)
        # S2/S3 summary lines
        tot = N_PER_POINT * len(GMC_GRID)
        pqr_tot = sum(ctrs[G][0].get("pqr", 0) for G in GMC_GRID)
        print(json.dumps({
            "system": api.name, "pqr_total": pqr_tot, "n_total": tot,
            "pqr_ci95_upper": round(3.0 / tot, 6),
        }), flush=True)


if __name__ == "__main__":
    main()
