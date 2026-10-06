"""Per-row kTAM grid — designs/002 multi-row systems under the v3 protocol.

This file runs the tick-14 "next unblocked" measurement: the 3-row
2-cycle system (tiles_2cycle.py) and all three anchored-cycle builds
(tiles_anchored.py: CORRECT, WRONG_CUT, WRONG_ROWS) under the kTAM
protocol of evidence/2026-10-06-c2-ktam-v3-locks/ktam_mc_v3.py —
unchanged rates (attach k_f*e^-Gmc for b>=1, detach k_f*e^(-b*Gse),
no mismatch), Gse=9, Gmc grid {9.5, 11, 13, 16} => dG {0.5, 2, 4, 7},
T_read = 400*e^Gmc, n=500 trajectories/point.

Pre-registered BEFORE running (lab discipline; see designs/002):

P1 (2-cycle, error suppression carries over rows): complete-decode
    wrong fraction (any decode other than {a}) sits at/below the v3
    envelope e^(-2*dG) at dG=2 (1.83e-2) and dG=4 (3.35e-4, testable
    only as CI95 upper 3/n). Falsifier: wrong > 10x envelope at dG=2.
P2 (anchored CORRECT, same envelope): wrong complete decodes (any
    decode other than {a,p,q}) obey the same bound. Falsifier: same.
P3 (wrong builds are kinetically dead too — order is load-bearing at
    kTAM, not only aTAM): the {a,p,q} decode count in WRONG_CUT and
    WRONG_ROWS stays 0 within CI (<= 3 per 500 at every dG), counted
    on the LOOSE decode (decision sites only, locks ignored) — the
    strictly more permissive resurrection detector.
    Falsifier: any wrong build decoding {a,p,q} above 3/500 loose.
P4 (depth pays in read time, designs/002 budget claim): the partial
    (growth-incomplete at read) fraction grows with row count vs the
    C2 v3 baseline (2 rows: partials 0/2/2/64 per 500 at
    dG=0.5/2/4/7); at dG=7 the 3-row partial fraction exceeds the
    2-row 0.128. No falsifier — a measurement, not a pass/fail claim.

Decode discipline: complete decodes require the spine complete, all
three decision sites filled and all three lock sites filled (the
2-cycle decode() already enforces this; the anchored builds get the
same strict wrapper here — the anchored checker's decode is looser
because the aTAM BFS only visits tau=2-stable assemblies).

Anchored WRONG_CUT / WRONG_ROWS predicted terminal decodes are {a,p}
and {a} (aTAM, tick 14); their kinetic interest is P3 only.

Per-run independent RNG; seeds derived deterministically per
(system, point) and printed in the header.
"""
import json
import math
import os
import random
import sys
from collections import Counter
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import tiles_2cycle as tc  # noqa: E402
from atam_check_2cycle import decode as decode_2cycle  # noqa: E402
from atam_check_anchored import decode as decode_anchored_loose  # noqa: E402
from tiles_anchored import BUILDS, locked_rows, true_variants  # noqa: E402

T_READ_MULTIPLIER = 400.0
BASE_SEED = 20261015
GSE = 9.0
GMC_GRID = (9.5, 11.0, 13.0, 16.0)
N_PER_POINT = 500
# v3 C2 baseline (2 rows), evidence/2026-10-06-c2-ktam-v3-locks/run.out
V3_C2_PARTIAL = {0.5: 0, 2.0: 2, 4.0: 2, 7.0: 64}


class TwoCycleAPI(object):
    name = "2cycle"
    expected = "a"

    @staticmethod
    def tiles():
        return tc.TILES

    @staticmethod
    def seed():
        return dict(tc.SEED_TILES)

    @staticmethod
    def sites():
        return tc.SITES

    @staticmethod
    def matched(assembly, site, tile):
        return tc.matched_strength(assembly, site, tile)

    @staticmethod
    def neighbour(assembly, site):
        return tc.has_neighbour(assembly, site)

    @staticmethod
    def decode(assembly):
        return decode_2cycle(assembly)

    @staticmethod
    def decode_loose(assembly):
        a = {"D1T": True, "D1F": False}.get(assembly.get((1, 1)))
        p = {"D2T": True, "D2F": False}.get(assembly.get((1, 2)))
        q = {"D3T": True, "D3F": False}.get(assembly.get((1, 3)))
        bits = ""
        bits += "a" if a else ""
        bits += "p" if p else ""
        bits += "q" if q else ""
        return bits if bits else "empty"


class AnchoredAPI(object):
    def __init__(self, build):
        self.name = build["name"]
        self.expected = build["expected_terminal_decode"]
        self.build = build

    def tiles(self):
        return self.build["tiles"]

    def seed(self):
        from tiles_anchored import SEED_TILES
        return dict(SEED_TILES)

    def sites(self):
        from tiles_anchored import SITES
        return SITES

    def matched(self, assembly, site, tile):
        from tiles_anchored import matched_strength
        return matched_strength(self.build, assembly, site, tile)

    def neighbour(self, assembly, site):
        from tiles_anchored import has_neighbour
        return has_neighbour(assembly, site)

    def decode(self, assembly):
        b = self.build
        spined = all(assembly.get((0, r)) == "S%d" % r for r in (1, 2, 3))
        if locked_rows(b, assembly) != 3 or not spined:
            return "partial"
        return decode_anchored_loose(b, assembly) or "empty"

    def decode_loose(self, assembly):
        # decision sites only — catches unlocked transients at read;
        # the aTAM WRONG_ROWS terminal {a} (empty upper rows) reads "a"
        # here, which is why P3 runs on this decode.
        return decode_anchored_loose(self.build, assembly) or "empty"


SYSTEMS = [TwoCycleAPI()] + [AnchoredAPI(b) for b in BUILDS]


def run_assembly(api, Gmc, Gse, T_read, seed):
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
    for sys_idx, api in enumerate(SYSTEMS):
        for Gmc in GMC_GRID:
            seed0 = (BASE_SEED + sys_idx * 10000000
                     + int(round((Gmc - GSE) * 1000)) * 10000)
            jobs.append((sys_idx, Gmc, seed0, N_PER_POINT))
    print(json.dumps({
        "Gse": GSE, "T_read_rule": "400*exp(Gmc)", "n_per_point": N_PER_POINT,
        "seed_base": BASE_SEED,
        "model": "kTAM v3 no-mismatch, per-row value-typed locks, 3-row systems",
        "systems": [{"idx": i, "name": a.name, "expected": a.expected}
                    for i, a in enumerate(SYSTEMS)],
        "predictions": ["P1 2cycle wrong<=e^-2dG at dG=2,4",
                        "P2 anchored CORRECT wrong<=e^-2dG at dG=2,4",
                        "P3 wrong builds: apq <= 3/500 everywhere",
                        "P4 3-row partial@dG=7 > C2 2-row 0.128"],
        "v3_c2_partial_baseline": V3_C2_PARTIAL,
    }), flush=True)
    with Pool(min(16, os.cpu_count() or 1)) as pool:
        results = pool.map(point_chunk, jobs)
    by_sys = {}
    for sys_idx, Gmc, decodes in results:
        strict = Counter(d.split("|")[0] for d in decodes)
        loose = Counter(d.split("|")[1] for d in decodes)
        by_sys.setdefault(sys_idx, {})[Gmc] = (strict, loose)
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
                "wrong_frac": round(sum(v for k, v in c.items()
                                        if k not in (expected, "partial")) / n, 4),
                "partial_frac": round(c.get("partial", 0) / n, 4),
                "curve_e_neg_dG": round(math.exp(-dG), 4),
                "curve_e_neg_2dG": round(math.exp(-2 * dG), 5),
            }
            print(json.dumps(row), flush=True)
        tot_wrong = sum(sum(v for k, v in ctrs[Gmc][0].items()
                            if k not in (expected, "partial"))
                        for Gmc in GMC_GRID)
        tot_loose_apq = sum(ctrs[Gmc][1].get("apq", 0) for Gmc in GMC_GRID)
        tot = N_PER_POINT * len(GMC_GRID)
        print(json.dumps({"system": api.name, "wrong_total": tot_wrong,
                          "n_total": tot,
                          "wrong_ci95_upper": round(3.0 / tot, 6),
                          "loose_apq_total": tot_loose_apq}), flush=True)


if __name__ == "__main__":
    main()
