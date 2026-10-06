"""kTAM kinetics grid — species-death survey (tick 23, SON-4775).

The general-species death survey queued by tick 22: BUILD1
(P_AND `p. q. r :- p, q.`) minus EACH of its 12 tile species in
turn, under the protocol of record (unchanged from the
tick-15/16/19/22 grids): Gse=9, Gmc in {9.5, 11, 13, 16} =>
dG {0.5, 2, 4, 7}, T_read = 400*e^Gmc, n = 500 trajectories/point,
no-mismatch kTAM (attach k_f*e^-Gmc for b >= 1, detach
k_f*e^(-b*Gse), spine bonds count 2), per-run independent RNG,
deterministic seeds printed in the header. build1 runs first as
calibration (tick-19/22 curves).

Per trajectory: strict decode (spine S1/S2/S3 at (0,1..3) AND an
L-tile at every lock site (3,1..3); TRUE atoms = rows whose lock
bonds a "-t" value on W), loose decode (build1's decision readers
kept in every system: p=D1T@(1,1), q=D2T@(1,2), r=DBr@(2,3)), and
whether the removed species' canonical site is occupied by ANY
tile at read time (the kinetic-bypass instrument).

Pre-registered BEFORE running (lab discipline; aTAM taxonomy from
atam_survey.py is exhaustive and machine-checked, so SV1 is a
measurement, not a prediction):

SV1 (structural taxonomy, aTAM): every removal's terminal-decode
    set, producibility table and label (PRESERVED / FAITHFUL_SUB /
    COLLAPSED / AMBIGUOUS) is recorded from the exhaustive BFS.
    Interesting iff every removal has a UNIQUE terminal decode
    (a confidently-wrong or confidently-dead read); AMBIGUOUS
    would break the readout story and is reported as such.

SV2 (repair measurement, kTAM): per removal, strict "pqr" fraction
    per point and ratio vs build1's same-point fraction.
    Per point: REPAIRED (ratio >= 0.5), PARTIAL (0 < ratio < 0.5),
    DEAD (strict pqr = 0).

P1 (from tick 22): DAr and DBr removals REPAIR at some dG <= 4
    (the DBr+L3 mutual b=2 stabilization trap, or its mirror).
P2: lock and spine removals (L1, L2, L3, S1, S2, S3) are DEAD at
    every point — their strict-decode sites admit no alternate
    occupant (no other inventory tile bonds >= 1 there).
    Falsifier: strict "pqr" > 0 anywhere on those six rows.
P3: decision/via removals (D1T, D2T, V0p, Vp) repair at most
    PARTIALLY (ratio < 0.5 at every point): their repair channels
    need chains of b=1 coincidences, not a single mutual pair.
    Falsifier: any ratio >= 0.5 on those four rows.
P4 (window lever, tick-22 S3(iii) generalisation): every removal
    REPAIRED at some dG <= 4 starves at dG=7 (ratio < 0.1 there).
    Falsifier: any removal with ratio >= 0.5 at dG=7.

S4 (calibration): build1 strict "pqr" within 2x of the tick-19/22
    curve (0.540/0.790/0.984/0.870 per 500).
    Falsifier: build1 "pqr" < 0.5x tick-19 at any point.
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

from tiles_and import BUILDS  # noqa: E402
from tiles_death import build_missing_species  # noqa: E402
from atam_check_and import matched_strength  # noqa: E402
from atam_survey import run_survey, CANONICAL_SITE, SPECIES  # noqa: E402

T_READ_MULTIPLIER = 400.0
BASE_SEED = 20261031
GSE = 9.0
GMC_GRID = (9.5, 11.0, 13.0, 16.0)
N_PER_POINT = 500
TICK19_BUILD1 = {0.5: 0.540, 2.0: 0.790, 4.0: 0.984, 7.0: 0.870}

LOCKS_AND_SPINE = ("L1", "L2", "L3", "S1", "S2", "S3")
DECISION_AND_VIA = ("D1T", "D2T", "V0p", "Vp")
READERS = {"p": ("D1T", (1, 1)), "q": ("D2T", (1, 2)),
           "r": ("DBr", (2, 3))}


class SurveyAPI(object):
    def __init__(self, build, aTAM_row):
        self.name = build["name"]
        self.build = build
        self.aTAM = aTAM_row          # label/decodes/anchors from BFS
        self.expected = (aTAM_row["terminal_decodes"][0][0]
                         if len(aTAM_row["terminal_decodes"]) == 1
                         else "ambiguous")
        self.vacancy = aTAM_row["canonical_site"]

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
                       sorted(READERS.items())
                       if assembly.get(site) == tile)
        return bits if bits else "empty"

    def vacancy_filled(self, assembly):
        return assembly.get(self.vacancy) is not None


def build_systems():
    survey = run_survey()          # exhaustive aTAM, in-process
    by_species = {r["removed"]: r for r in survey["rows"]}
    systems = [SurveyAPI(BUILDS["build1"],
                         {"terminal_decodes": [("pqr", 3)],
                          "canonical_site": None,
                          "label": "CALIBRATION"})]
    for sp in SPECIES:
        systems.append(SurveyAPI(
            build_missing_species(BUILDS["build1"], sp), by_species[sp]))
    return systems, survey


SYSTEMS, ATAM_SURVEY = build_systems()


def run_assembly(api, Gmc, Gse, T_read, seed):
    """Verbatim protocol of record (ktam_mc_death.run_assembly),
    with the vacancy-occupancy instrument instead of the row-3
    split (generalises it to any removed species)."""
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
            api.vacancy_filled(assembly))


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
                  "4-column AND geometry (S|D|V|L), 3 rows; systems = "
                  "build1 + each single-species removal"),
        "systems": [{"idx": i, "name": a.name,
                     "removed": (SYSTEMS[i].build["name"]
                                 .rsplit("_missing_", 1)[-1]
                                 if i else None),
                     "aTAM_label": a.aTAM.get("label"),
                     "expected": a.expected}
                    for i, a in enumerate(SYSTEMS)],
        "atam_survey": ATAM_SURVEY["rows"],
        "predictions": [
            "SV1 aTAM taxonomy measured (exhaustive BFS); report "
            "AMBIGUOUS labels if any",
            "P1 DAr, DBr removals REPAIRED (ratio>=0.5) at some dG<=4",
            "P2 L1/L2/L3/S1/S2/S3 removals DEAD everywhere; falsifier: "
            "strict pqr > 0 on those rows",
            "P3 D1T/D2T/V0p/Vp removals ratio < 0.5 everywhere; "
            "falsifier: any ratio >= 0.5 on those rows",
            "P4 every REPAIRED-at-dG<=4 removal starves at dG=7 "
            "(ratio < 0.1); falsifier: ratio >= 0.5 at dG=7",
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
        vac = sum(1 for d in decodes if d[2])
        by_sys.setdefault(sys_idx, {})[Gmc] = (strict, loose, vac)
    base = {G: by_sys[0][G][0].get("pqr", 0) / float(N_PER_POINT)
            for G in GMC_GRID}
    for sys_idx, api in enumerate(SYSTEMS):
        ctrs = by_sys[sys_idx]
        for Gmc in GMC_GRID:
            c, cl, vac = ctrs[Gmc]
            n = sum(c.values())
            dG = round(Gmc - GSE, 1)
            pqr = c.get("pqr", 0)
            row = {
                "system": api.name, "Gmc": Gmc, "dGmc": dG, "n": n,
                "decode": dict(sorted(c.items())),
                "decode_loose": dict(sorted(cl.items())),
                "vacancy_filled": vac,
                "pqr": pqr, "pqr_frac": round(pqr / n, 4),
                "build1_pqr_frac": round(base[Gmc], 4),
                "ratio": (round(pqr / n / base[Gmc], 4)
                          if base[Gmc] else None),
                "expected": api.expected,
                "curve_e_neg_dG": round(math.exp(-dG), 4),
                "curve_e_neg_2dG": round(math.exp(-2 * dG), 5),
            }
            print(json.dumps(row), flush=True)
        tot = N_PER_POINT * len(GMC_GRID)
        pqr_tot = sum(ctrs[G][0].get("pqr", 0) for G in GMC_GRID)
        print(json.dumps({
            "system": api.name, "pqr_total": pqr_tot, "n_total": tot,
            "pqr_ci95_upper": round(3.0 / tot, 6),
        }), flush=True)
    # P-verdicts (computed after the run, against the pre-registration)
    verdicts = {"P2_violations": [], "P3_violations": [],
                "P4_violations": [], "S4_min_ratio": None}
    s4 = []
    for sys_idx, api in enumerate(SYSTEMS):
        removed = (None if sys_idx == 0 else
                   SPECIES[sys_idx - 1])
        if removed is None:
            for Gmc in GMC_GRID:
                f = by_sys[0][Gmc][0].get("pqr", 0) / float(N_PER_POINT)
                dG = round(Gmc - GSE, 1)
                s4.append(round(f / TICK19_BUILD1[dG], 4))
            continue
        for Gmc in GMC_GRID:
            c = by_sys[sys_idx][Gmc][0]
            dG = round(Gmc - GSE, 1)
            if removed in LOCKS_AND_SPINE and c.get("pqr", 0) > 0:
                verdicts["P2_violations"].append([removed, dG])
            if (removed in DECISION_AND_VIA and base[Gmc] > 0
                    and (c.get("pqr", 0) / float(N_PER_POINT)
                         / base[Gmc]) >= 0.5):
                verdicts["P3_violations"].append([removed, dG])
            if (dG == 7.0 and base[Gmc] > 0
                    and (c.get("pqr", 0) / float(N_PER_POINT)
                         / base[Gmc]) >= 0.5):
                verdicts["P4_violations"].append([removed, dG])
    verdicts["S4_min_ratio"] = min(s4) if s4 else None
    print(json.dumps({"verdicts": verdicts}), flush=True)


if __name__ == "__main__":
    main()
