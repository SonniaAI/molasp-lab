"""kTAM Gillespie MC on designs/001 v2.1 geometry — slow-growth window sweep.

The experiment designs/001 specifies as next (and this file runs):

  Gse = 9 fixed, Gmc in {9.5, 11, 13, 16}  (window Gse < Gmc < 2*Gse)
  Read time per point T = 400*exp(Gmc): the first grid used a fixed
  T = 400*exp(Gse), which reads the dG=7 point before any growth
  (500/500 partial -- instrumental failure, preserved in
  run-grid1-fixedT.out); read time must scale with the on-rate.
  Prediction: `empty` (founded value error via D1F near-miss) falls
  roughly exponentially with Gmc - Gse; `{a,p}` (unfounded p via D2T
  near-miss) stays at the transient floor. Refutes the design if
  `empty` does not fall, or if `{a,p}` rises above it.

Model: identical to ktam_mc.py (v1) except the tile system is the
construction of record tiles_v2.py (3 cols x 2 rows over a 3-tile seed,
row-typed strength-2 spine glues) and decode is atam_check_v2.decode,
the same map the machine-checked aTAM claim used. Attach rate per
(site, tile) with >=1 matched strength: k_f*exp(-Gmc); detach rate
k_f*exp(-b*Gse), b = summed matched glue strength (SP bonds count 2);
k_f = 1/s; mismatch-attachments neglected (Xgrow "no-mismatch" mode,
as in v1). Read at fixed T = 400*exp(Gse). Per-run independent RNG
(parallel-safe, reproducible from seeds printed in the output).
"""
import json
import math
import os
import random
import sys
from collections import Counter
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "2026-10-05-c2-ktam"))

from tiles_v2 import TILES, SEED_TILES, SITES, matched_strength, has_neighbour  # noqa: E402
from atam_check_v2 import decode  # noqa: E402

# Each site gets ~400 attachment attempts at its own on-rate.
T_READ_MULTIPLIER = 400.0

BASE_SEED = 20261006
GSE = 9.0
GMC_GRID = (9.5, 11.0, 13.0, 16.0)
N_PER_POINT = 500


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
                      "n_per_point": N_PER_POINT,
                      "seed_base": BASE_SEED, "model": "kTAM v2.1 no-mismatch"}))
    with Pool(min(16, os.cpu_count())) as pool:
        results = pool.map(point_chunk, jobs)
    unfounded_total = 0
    n_total = 0
    for Gmc, decodes in sorted(results):
        c = Counter(decodes)
        n = len(decodes)
        n_total += n
        unfounded = c.get("ap", 0) + c.get("p", 0)
        unfounded_total += unfounded
        row = {
            "Gse": GSE, "Gmc": Gmc, "dGmc": round(Gmc - GSE, 1), "n": n,
            "decode": {k: c.get(k, 0) for k in ("a", "ap", "p", "empty", "partial")},
            "empty_frac": round(c.get("empty", 0) / n, 4),
            "unfounded_frac": round(unfounded / n, 5),
        }
        print(json.dumps(row), flush=True)
    print(json.dumps({"unfounded_total": unfounded_total, "n_total": n_total,
                      "unfounded_ci95_upper": round(3.0 / n_total, 6)}))


if __name__ == "__main__":
    main()
