"""kTAM Gillespie MC on designs/001 v3p — the cage ratio falsifier (tick 12).

Runs the MC that tick 11 queued: identical protocol to the v2.1 window
grid and the v3 lock grid (Gse = 9, Gmc in {9.5, 11, 13, 16},
T_read = 400*exp(Gmc), n = 500/point, no-mismatch kTAM, seeds printed),
on the maximally-blind cage tiles_v3p.py.

Tick-11 prediction under test: correct completion ~exp(-2*dG)
(D2F^L1 overlap + L2 arrival over D1T's tau-residency); wrong
completion ~exp(-3*dG) (adds D1F's b=1 window); wrong/correct ~exp(-dG),
"the SAME ratio as v2.1". Falsifier as written: wrong completions at or
above exp(-2*dG) with correct completion within exp(-dG) of v3's rate
refutes the lemma.

Structural fact this harness makes measurable (spotted before running):
in the cage D2F and D2T are bond-arithmetic IDENTICAL — both ride only
the blind W=go2 into S2.E (cap3/no-p/topF/topT each appear exactly once
in the whole system, so they bond nothing). The unfounded completion
'ap' therefore rides at the SAME rate as the correct 'a' (a fair coin
on which row-2 tile is resident when L2's b=2 arrival catches the
overlap). The exp(-3*dG) arithmetic modeled only the D1F (empty)
channel; the symmetric ap channel should dominate wrong completions.

Reference curves printed per point: exp(-dG), exp(-2*dG), the
co-residency budget curve 1-exp(-400*p_L1*p_row2) with
p_L1 = 1/(1+exp(dG)) and p_row2 = 2/(2+exp(dG)) (steady-state
occupancies of the two churning b=1 sites under the same rates), and
v3's measured correct fractions for the falsifier's second clause.

Model: identical to ktam_mc_v3.py except the tile system. Attach rate
per (site, tile) with >=1 matched strength: k_f*exp(-Gmc); detach rate
k_f*exp(-b*Gse), b = summed matched glue strength (SP bonds count 2);
k_f = 1/s; mismatch-attachments neglected. Read at T = 400*exp(Gmc).
"""
import json
import math
import os
import random
import sys
from collections import Counter
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, os.pardir, "2026-10-06-v3p-blind-cage"))

from tiles_v3p import (  # noqa: E402
    TILES, SEED_TILES, SITES, matched_strength, has_neighbour, decode)

T_READ_MULTIPLIER = 400.0

BASE_SEED = 20261008
GSE = 9.0
GMC_GRID = (9.5, 11.0, 13.0, 16.0)
N_PER_POINT = 500
V3_MEASURED_CORRECT = {  # evidence/2026-10-06-c2-ktam-v3-locks/run.out, n=500
    0.5: 1.000,
    2.0: 0.996,
    4.0: 0.996,
    7.0: 0.872,
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


def budget_curve(dG):
    """Rough completion guide: expected b=2 L2 catches over T_read.

    Steady-state occupancy of a churning b=1 site with one tile option
    (L1 at (2,1)) is p_L1 = rf/(rf+rr1) = 1/(1+exp(dG)); the row-2 site
    has TWO symmetric options, p_row2 = 2/(2+exp(dG)). L2 arrivals at
    rate exp(-Gmc) catch both-resident windows; expected catches over
    400*exp(Gmc) is 400*p_L1*p_row2, so completion ~ 1-exp(-that).
    Independence approximation; printed as a guide, not the claim.
    """
    p_l1 = 1.0 / (1.0 + math.exp(dG))
    p_row2 = 2.0 / (2.0 + math.exp(dG))
    catches = T_READ_MULTIPLIER * p_l1 * p_row2
    return 1.0 - math.exp(-catches)


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
                      "model": "kTAM v3p no-mismatch, maximally-blind cage",
                      "prediction_under_test": "correct ~exp(-2dG), wrong ~exp(-3dG), wrong/correct ~exp(-dG)",
                      "structural_note": "D2F/D2T bond-identical: ap channel rides at the correct rate",
                      "v3_measured_correct": V3_MEASURED_CORRECT}))
    totals = {"a": 0, "ap": 0, "p": 0, "empty": 0, "partial": 0}
    for Gmc, decodes in sorted(Pool(min(16, os.cpu_count())).map(point_chunk, jobs)):
        c = Counter(decodes)
        n = len(decodes)
        for k in totals:
            totals[k] += c.get(k, 0)
        dG = Gmc - GSE
        wrong = c.get("ap", 0) + c.get("p", 0) + c.get("empty", 0)
        correct = c.get("a", 0)
        row = {
            "Gse": GSE, "Gmc": Gmc, "dGmc": round(dG, 1), "n": n,
            "decode": {k: c.get(k, 0) for k in ("a", "ap", "p", "empty", "partial")},
            "correct_frac": round(correct / n, 4),
            "wrong_frac": round(wrong / n, 4),
            "unfounded_frac": round((c.get("ap", 0) + c.get("p", 0)) / n, 5),
            "ratio_wrong_over_correct": round(wrong / correct, 4) if correct else None,
            "ratio_ap_over_a": (round(c.get("ap", 0) / correct, 4)
                                if correct else None),
            "curve_e_neg_dG": round(math.exp(-dG), 4),
            "curve_e_neg_2dG": round(math.exp(-2 * dG), 5),
            "budget_curve": round(budget_curve(dG), 4),
            "v3_correct": V3_MEASURED_CORRECT[round(dG, 1)],
            "falsifier_wrong_ge_e2dG": wrong / n >= math.exp(-2 * dG),
            "falsifier_correct_ratio_ge_v3_times_e_dG":
                (correct / n) >= V3_MEASURED_CORRECT[round(dG, 1)] * math.exp(-dG),
        }
        print(json.dumps(row), flush=True)
    n_total = sum(totals.values())
    print(json.dumps({"totals": totals, "n_total": n_total}))


if __name__ == "__main__":
    main()
