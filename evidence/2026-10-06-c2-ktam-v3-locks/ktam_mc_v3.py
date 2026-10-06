"""kTAM Gillespie MC on designs/001 v3 — evidence-checking locks grid.

The experiment designs/001 specifies as next (and this file runs):
identical protocol to the v2.1 window grid (Gse = 9, Gmc in
{9.5, 11, 13, 16}, T_read = 400*exp(Gmc), n = 500/point, no-mismatch
kTAM), on the value-typed tile set tiles_v3.py.

Prediction (designs/001 "v3"): with locks that check the value they
lock, a terminal wrong decode needs two coincident sub-tau attachments,
so BOTH error channels (founded `empty` and unfounded `{a,p}`) fall
like ~e^{-2*dG} instead of v2.1's ~e^{-dG}. At dG=2 that is ~1.8e-2
instead of the measured .174 (empty) / .058 (unfounded).

Falsifier (designs/001): the v3 grid showing either channel above its
e^{-2*dG} curve. Reference curves are printed per point; v2.1's
measured fractions are carried in the header for direct comparison.

Model: identical to ktam_mc_v2.py except the tile system. Attach rate
per (site, tile) with >=1 matched strength: k_f*exp(-Gmc); detach rate
k_f*exp(-b*Gse), b = summed matched glue strength (SP bonds count 2);
k_f = 1/s; mismatch-attachments neglected. Read at fixed T = 400*exp(Gmc).
Per-run independent RNG, reproducible from seeds printed in the output.
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

from tiles_v3 import TILES, SEED_TILES, SITES, matched_strength, has_neighbour  # noqa: E402
from atam_check_v3 import decode  # noqa: E402

T_READ_MULTIPLIER = 400.0

BASE_SEED = 20261007
GSE = 9.0
GMC_GRID = (9.5, 11.0, 13.0, 16.0)
N_PER_POINT = 500
V21_MEASURED = {  # evidence/2026-10-06-c2-ktam-v2-window/run.out, n=500
    0.5: {"empty": 0.212, "unfounded": 0.222},
    2.0: {"empty": 0.174, "unfounded": 0.058},
    4.0: {"empty": 0.044, "unfounded": 0.000},
    7.0: {"empty": 0.000, "unfounded": 0.000},
}


def run_assembly(Gmc, Gse, T_read, seed):
    rng = random.Random(seed)
    rf = math.exp(-Gmc)
    assembly = dict(SEED_TILES)
    t = 0.0
    while True:
        events = []
        for site in SITES:
            if site in assembly:
                b = matched_strength(assembly, site, assembly[site])
                events.append((math.exp(-b * Gse), "detach", site))
            elif has_neighbour(assembly, site):
                for tile in TILES:
                    if matched_strength(assembly, site, tile) >= 1:
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
    return decode(assembly)


def point_chunk(args):
    Gmc, seed0, n = args
    Gse = GSE
    T_read = T_READ_MULTIPLIER * math.exp(Gmc)
    return Gmc, [run_assembly(Gmc, Gse, T_read, seed0 + i) for i in range(n)]


def main():
    jobs = [(Gmc, BASE_SEED + int(round((Gmc - GSE) * 1000)) * 10000, N_PER_POINT)
            for Gmc in GMC_GRID]
    print(json.dumps({"Gse": GSE, "T_read_rule": "400*exp(Gmc)",
                      "n_per_point": N_PER_POINT, "seed_base": BASE_SEED,
                      "model": "kTAM v3 no-mismatch, value-typed locks",
                      "prediction": "both channels ~ exp(-2*dG)",
                      "v21_measured": V21_MEASURED}))
    with Pool(min(16, os.cpu_count())) as pool:
        results = pool.map(point_chunk, jobs)
    wrong_total = 0
    n_total = 0
    for Gmc, decodes in sorted(results):
        c = Counter(decodes)
        n = len(decodes)
        n_total += n
        dG = Gmc - GSE
        unfounded = c.get("ap", 0) + c.get("p", 0)
        wrong_total += unfounded + c.get("empty", 0)
        row = {
            "Gse": GSE, "Gmc": Gmc, "dGmc": round(dG, 1), "n": n,
            "decode": {k: c.get(k, 0) for k in ("a", "ap", "p", "empty", "partial")},
            "empty_frac": round(c.get("empty", 0) / n, 4),
            "unfounded_frac": round(unfounded / n, 5),
            "curve_e_neg_dG": round(math.exp(-dG), 4),
            "curve_e_neg_2dG": round(math.exp(-2 * dG), 5),
        }
        print(json.dumps(row), flush=True)
    print(json.dumps({"wrong_total": wrong_total, "n_total": n_total,
                      "wrong_ci95_upper": round(3.0 / n_total, 6)}))


if __name__ == "__main__":
    main()
