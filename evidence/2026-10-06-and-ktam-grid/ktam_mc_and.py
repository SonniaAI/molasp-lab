"""kTAM kinetics grid — designs/003 F4, the AND builds under the v3
protocol (tick 19, SON-4761; queue head handed over by tick 18).

Protocol of record (unchanged from the tick-15/16 grids,
evidence/2026-10-06-multirow-ktam-grid/ktam_mc_multirow.py): Gse = 9,
Gmc in {9.5, 11, 13, 16} => dG {0.5, 2, 4, 7}, T_read = 400*e^Gmc,
n = 500 trajectories/point, no-mismatch kTAM (attach k_f*e^-Gmc for
b >= 1, detach k_f*e^(-b*Gse), spine bonds count 2), per-run
independent RNG, seeds derived deterministically per (system, point)
and printed in the header.

Systems: the three corrected designs/003 builds
(tiles_and.py, errata E1/E2 applied; the aTAM arm is tick 18's
evidence/2026-10-06-body-conjunction-builds/):
  build1  P_AND           expected strict "pqr" (the AND fires)
  build2  P_AND-q         expected strict "p"   (slot-A death)
  build3  P_AND-p W1      expected strict "qr"  (consistent wrong
                          compile; {q,r} is a NON-model — clingo {q})

Pre-registered BEFORE running (lab discipline; designs/003 F4):

K1 (correct-build rates): build1 strict "pqr" tracks the tick-15
    anchored CORRECT curve (1.000/0.998/0.990/0.866 per 500 at
    dG=0.5/2/4/7) within ~2x at every point.  Structural note: a
    strict decode other than "pqr"/"partial" is impossible in build1
    (L3 present => lock reads r-t => r true; no false locks exist),
    so build1's wrong channel is partials only.
    Falsifier: strict "pqr" < 0.5x tick-15 CORRECT at any point.
K2 (consistent-wrong execution, the tick-16 prediction carried to the
    AND geometry): build3 strict "qr" >= 0.9 at every dG <= 4 — the
    substrate executes the compile's error faithfully, at full rate.
    Falsifier: strict "qr" < 0.9 at any dG <= 4.
K3 (slot-A death kinetics): build2 strict "p" >= 0.9 at dG <= 4; the
    q/r true tiles are absent from the inventory, so loose decodes
    can only lose atoms, never gain them (structural).
    Falsifier: strict "p" < 0.9 at any dG <= 4.
K4 (no reassertion — THE falsifier for sequential gating): the
    true-model reassertion proxies stay at the e^{-2dG} floor:
    build3 loose "q" and build1 loose "pq"/"p" counted ONLY on
    runs whose strict decode is "partial" (r's row genuinely
    incomplete: decision dead AND unlocked at read).  Strict "q" in
    build3 is structurally impossible (L2 present => lock reads
    r-t), which is why the detector runs on the LOOSE decode.
    Smoke test (12 traj/build, dG=2, pre-run): the naive loose
    count also fires on 'qr|q' pairs — lock-stable WRONG decodes
    whose decision tile merely churned off at the read instant.
    Those are NOT reassertion (the lock column still reads r), so
    they are tallied separately as decision_vacancy, and the K4
    gate runs on the partial-strict intersection only.
    Falsifier: any reassertion channel above 3/500 at dG in {2,4,7}.

Decode discipline (strict): spine S1/S2/S3 at (0,1..3) AND an
L-tile at every lock site (3,1..3); TRUE atoms = rows whose lock
tile bonds a "-t" value on W (the aTAM decode of record, tightened
to name-check the lock tile because kTAM admits b=1 non-lock
transients at lock sites that aTAM's tau=2 BFS never visits).
Loose: decision readers only — build1 p=D1T@(1,1), q=D2T@(1,2),
r=DBr@(2,3); build2 p=D1T@(1,1); build3 q=D1Tq@(1,1), r=DAr@(1,2).

Reference curves printed per point: e^{-dG}, e^{-2dG}; tick-15
anchored CORRECT completion for K1.
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
from atam_check_and import matched_strength  # noqa: E402

T_READ_MULTIPLIER = 400.0
BASE_SEED = 20261019
GSE = 9.0
GMC_GRID = (9.5, 11.0, 13.0, 16.0)
N_PER_POINT = 500
# tick-15 reference (evidence/2026-10-06-multirow-ktam-grid/run.out)
TICK15_CORRECT = {0.5: 1.000, 2.0: 0.998, 4.0: 0.990, 7.0: 0.866}

# loose-decode decision readers, pre-registered per build
TRUE_READERS = {
    "P_AND_corrected": {"p": ("D1T", (1, 1)), "q": ("D2T", (1, 2)),
                        "r": ("DBr", (2, 3))},
    "P_AND_minus_q": {"p": ("D1T", (1, 1))},
    "W1_dropped_literal_corrected": {"q": ("D1Tq", (1, 1)),
                                     "r": ("DAr", (1, 2))},
}
SYSTEM_KEYS = ("build1", "build2", "build3")


class AndAPI(object):
    EXPECTED = {"P_AND_corrected": "pqr",
                "P_AND_minus_q": "p",
                "W1_dropped_literal_corrected": "qr"}

    def __init__(self, build):
        self.name = build["name"]
        self.expected = AndAPI.EXPECTED[build["name"]]
        self.build = build
        self.readers = TRUE_READERS[build["name"]]

    def tiles(self):
        return self.build["tiles"]

    def seed(self):
        # placeholder names, as in the aTAM checker: seed cells expose
        # their north-face glues via build["seed"], read by
        # matched_strength directly
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


SYSTEMS = [AndAPI(BUILDS[k]) for k in SYSTEM_KEYS]


def run_assembly(api, Gmc, Gse, T_read, seed):
    """Verbatim protocol of record from ktam_mc_multirow.run_assembly."""
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
    return api.decode(assembly) + "|" + api.decode_loose(assembly)


def point_chunk(args):
    sys_idx, Gmc, seed0, n = args
    api = SYSTEMS[sys_idx]
    T_read = T_READ_MULTIPLIER * math.exp(Gmc)
    return sys_idx, Gmc, [run_assembly(api, Gmc, GSE, T_read, seed0 + i)
                          for i in range(n)]


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
                  "4-column AND geometry (S|D|V|L), 3 rows"),
        "systems": [{"idx": i, "name": a.name, "expected": a.expected}
                    for i, a in enumerate(SYSTEMS)],
        "predictions": ["K1 build1 pqr within ~2x of tick15 CORRECT",
                        "K2 build3 strict qr >= 0.9 at dG<=4",
                        "K3 build2 strict p >= 0.9 at dG<=4",
                        "K4 reassertion (build3 loose q; build1 loose "
                        "pq/p) <= 3/500 at dG in {2,4,7}"],
        "tick15_correct_reference": TICK15_CORRECT,
    }), flush=True)
    with Pool(min(16, os.cpu_count() or 1)) as pool:
        results = pool.map(point_chunk, jobs)
    by_sys = {}
    for sys_idx, Gmc, decodes in results:
        strict = Counter(d.split("|")[0] for d in decodes)
        loose = Counter(d.split("|")[1] for d in decodes)
        by_sys.setdefault(sys_idx, {})[Gmc] = (strict, loose)
        # joint pairs for the K4 detector (per point)
        pairs = Counter(decodes)
        by_sys[sys_idx].setdefault("pairs", {})[Gmc] = pairs
    for sys_idx, api in enumerate(SYSTEMS):
        ctrs = by_sys[sys_idx]
        for Gmc in GMC_GRID:
            c, cl = ctrs[Gmc]
            n = sum(c.values())
            dG = round(Gmc - GSE, 1)
            expected = api.expected
            row = {
                "system": api.name, "Gmc": Gmc, "dGmc": dG, "n": n,
                "decode": dict(sorted(c.items())),
                "decode_loose": dict(sorted(cl.items())),
                "expected": expected,
                "expected_frac": round(c.get(expected, 0) / n, 4),
                "partial_frac": round(c.get("partial", 0) / n, 4),
                "tick15_correct": TICK15_CORRECT[dG],
                "curve_e_neg_dG": round(math.exp(-dG), 4),
                "curve_e_neg_2dG": round(math.exp(-2 * dG), 5),
            }
            print(json.dumps(row), flush=True)
        # reassertion + wrong tallies for K4
        # reassertion tallies for K4 (refined detector, see header):
        # only runs whose strict decode is "partial" count — the
        # decision tile dead AND the row unlocked. Lock-stable reads
        # with a momentarily-vacant decision site are tallied as
        # decision_vacancy (measurement channel, not reassertion).
        keys = ("p", "pq") if sys_idx == 0 else (("q",) if sys_idx == 2 else ())
        pairs_all = by_sys[sys_idx].get("pairs", {})
        reassert = sum(pairs_all[G].get("partial|" + k, 0)
                       for G in GMC_GRID for k in keys)
        vacancy = sum(v for G in GMC_GRID for kk in keys
                      for k, v in pairs_all[G].items()
                      if k.endswith("|" + kk)
                      and not k.startswith("partial|"))
        tot = N_PER_POINT * len(GMC_GRID)
        print(json.dumps({
            "system": api.name, "reassertion_loose_total": reassert,
            "decision_vacancy_total": vacancy,
            "n_total": tot, "reassertion_ci95_upper": round(3.0 / tot, 6),
        }), flush=True)


if __name__ == "__main__":
    main()
