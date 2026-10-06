"""Instrumented full-assembly kTAM MC on designs/001 v2.1 — row-2 ordering.

Tick 8 residual 2 (research-log/2026-10-06-empty-first-passage.md): the
exact window CTMC over-predicts the unfounded channel 2.4x at dG=2
(t2 = .1381 vs .058 measured, n=500) and at dG=4 (.0276 vs 0/500).
Candidates named there: spatial growth ordering, read-time churn.
Neither measured. This file measures both, on the full 6-site assembly,
identical protocol to the v2.1 window grid (Gse=9, T_read=400*e^Gmc,
no-mismatch kTAM, n=500/point, fresh seed base 20261008).

Mechanism under test. The unfounded channel is a D2T near-miss locked by
the value-blind L2. Structural facts of tiles_v2.py the decomposition
rides on:
  - D2T can NEVER bond at b=2 on entry (S=no-p has no partner): every
    D2T residency is a sub-tau near-miss via W=go2 alone.
  - L2 reaches b=2 only when L1 is resident (S=base2 vs L1.N) AND a
    row-2 decision tile is resident (W=r2): without L1 the lock itself
    is a b=1 near-miss and the pair (D2T b=1, L2 b=1) is doubly
    unstable.
So the trap pipeline is: D2T excursion -> excursion overlapping an L1
residency -> L2 attaches onto resident D2T (trap formed) -> pair
survives to read -> row 1 also complete at read (decode ap/p vs
partial). Each stage is counted per trajectory; the 2.4x gap must live
in one of them.

Also cross-checks the tick-8 window claim E[D1F excursions] .61-.95 in
the full assembly, and counts b>=2 detach events (read-time churn).
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

T_READ_MULTIPLIER = 400.0
BASE_SEED = 20261008
GSE = 9.0
GMC_GRID = (9.5, 11.0, 13.0)
N_PER_POINT = 500
WINDOW_CTMC_T2 = {0.5: 0.2646, 2.0: 0.1381, 4.0: 0.0276}  # tick 8, joint solve
V21_MEASURED_UNFOUNDED = {0.5: 0.222, 2.0: 0.058, 4.0: 0.000}


def run_assembly(Gmc, Gse, T_read, seed):
    rng = random.Random(seed)
    rf = math.exp(-Gmc)
    assembly = dict(SEED_TILES)
    t = 0.0
    s = Counter()
    first_d2t_t = None
    while True:
        events = []
        for site in SITES:
            if site in assembly:
                b = matched_strength(assembly, site, assembly[site])
                events.append((math.exp(-b * Gse), "detach", site))
                if b >= 2:
                    s["b2_sites_present"] += 1  # opportunity weight, not count
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
                    site, tile = arg
                    if site == (1, 2) and tile == "D2T":
                        s["d2t_attach"] += 1
                        if first_d2t_t is None:
                            first_d2t_t = t
                        if assembly.get((2, 1)) == "L1":
                            s["d2t_attach_with_l1"] += 1
                    if site == (1, 1) and tile == "D1F":
                        s["d1f_attach"] += 1
                    if site == (2, 2) and tile == "L2" and assembly.get((1, 2)) == "D2T":
                        s["l2_onto_d2t"] += 1
                    assembly[site] = tile
                else:
                    site = arg
                    if site == (1, 2) and assembly[site] == "D2T":
                        s["d2t_detach"] += 1
                        if assembly.get((2, 2)) == "L2":
                            s["trapped_d2t_churned"] += 1
                    if site == (2, 2) and assembly[site] == "L2":
                        s["l2_detach"] += 1
                        if assembly.get((1, 2)) == "D2T":
                            s["trap_broken_by_l2"] += 1
                    if matched_strength(assembly, site, assembly[site]) >= 2:
                        s["b2_detach_events"] += 1
                    del assembly[site]
                break
    d2t_at_read = assembly.get((1, 2)) == "D2T"
    l2_at_read = assembly.get((2, 2)) == "L2"
    s["trap_at_read"] = 1 if (d2t_at_read and l2_at_read) else 0
    s["d2t_ever"] = 1 if s["d2t_attach"] > 0 else 0
    s["trap_ever"] = 1 if (s["l2_onto_d2t"] > 0 or s["trap_at_read"]) else 0
    if first_d2t_t is not None:
        s["first_d2t_before_half_read"] = 1 if first_d2t_t < T_read / 2 else 0
    return decode(assembly), dict(s)


def point_chunk(args):
    Gmc, seed0, n = args
    T_read = T_READ_MULTIPLIER * math.exp(Gmc)
    return Gmc, [run_assembly(Gmc, GSE, T_read, seed0 + i) for i in range(n)]


def frac(n, d):
    return round(n / d, 4) if d else None


def main():
    jobs = [(Gmc, BASE_SEED + int(round((Gmc - GSE) * 1000)) * 10000, N_PER_POINT)
            for Gmc in GMC_GRID]
    print(json.dumps({"Gse": GSE, "T_read_rule": "400*exp(Gmc)",
                      "n_per_point": N_PER_POINT, "seed_base": BASE_SEED,
                      "model": "kTAM v2.1 no-mismatch, instrumented",
                      "window_ctmc_t2": WINDOW_CTMC_T2,
                      "v21_measured_unfounded": V21_MEASURED_UNFOUNDED}))
    with Pool(min(16, os.cpu_count())) as pool:
        results = pool.map(point_chunk, jobs)
    for Gmc, runs in sorted(results):
        n = len(runs)
        c = Counter(d for d, _ in runs)
        tot = Counter()
        for _, s in runs:
            for k, v in s.items():
                tot[k] += v
        dG = round(Gmc - GSE, 1)
        trap_reads = Counter(d for d, s in runs if s["trap_at_read"])
        unfounded = c.get("ap", 0) + c.get("p", 0)
        row = {
            "Gmc": Gmc, "dG": dG, "n": n,
            "decode": {k: c.get(k, 0) for k in ("a", "ap", "p", "empty", "partial")},
            "unfounded_frac": round(unfounded / n, 4),
            "window_t2": WINDOW_CTMC_T2.get(dG),
            "pipeline": {
                "d2t_ever": frac(tot["d2t_ever"], n),
                "d2t_attach_events_mean": round(tot["d2t_attach"] / n, 3),
                "d2t_attach_with_l1_frac_of_events": frac(tot["d2t_attach_with_l1"], tot["d2t_attach"]),
                "l2_onto_d2t_trajectories": frac(tot["trap_ever"], n),
                "trapped_d2t_churned_events_mean": round(tot["trapped_d2t_churned"] / n, 4),
                "trap_broken_by_l2_events_mean": round(tot["trap_broken_by_l2"] / n, 4),
                "trap_at_read": frac(tot["trap_at_read"], n),
                "trap_at_read_decodes": dict(trap_reads),
            },
            "d1f_attach_mean": round(tot["d1f_attach"] / n, 3),
            "b2_detach_events_mean": round(tot["b2_detach_events"] / n, 3),
        }
        print(json.dumps(row), flush=True)


if __name__ == "__main__":
    main()
