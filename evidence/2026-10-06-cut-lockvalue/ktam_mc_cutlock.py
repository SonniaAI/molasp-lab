"""kTAM grid — WRONG_CUT_LOCKFALSE under the v3 protocol (tick 16,
designs/002 F2 boundary; the tick-15 "natural next build").

Same protocol as the tick-15 multirow grid, unchanged rates: Gse=9,
Gmc in {9.5, 11, 13, 16} => dG {0.5, 2, 4, 7}, T_read = 400*e^Gmc,
n=500 trajectories/point, no-mismatch kTAM, per-run independent RNG,
seeds printed in the header.  Strict decode = spine + all decision
sites + all lock sites filled (the multirow AnchoredAPI wrapper).

Pre-registered BEFORE running (lab discipline):

P1 (self-correction is LOCK-typed, not CUT-typed — the F2 boundary
    closes): WRONG_CUT_LOCKFALSE strict-decodes its own predicted
    terminal "ap" — a decode that is neither stable nor a model of P
    (clingo: ap-only unsatisfiable, aTAM check this tick) — at >=0.9
    per point for dG <= 4.  The tick-15 WRONG_CUT self-correction
    channel (true tile captured by a true-typed lock into {a,p,q})
    is structurally absent here: no tile bonds rq-t from the lock
    side, so the true tile's b=1 transient has no capture partner.
    Falsifier: strict "ap" < 0.5 at any dG <= 4.
P2 (no reassertion of the true stable model): strict "apq" <= 3/500
    at dG in {2, 4, 7} (CI95 3/n).  At dG=0.5 a transient coincidence
    channel (D3T and L3 both b=1 at read) may appear — recorded, not
    gated; it is the same transient family as the 2cycle's 13/2000.
    Falsifier: strict "apq" > 3/500 at any of dG in {2,4,7}.
P3 (measurement, no falsifier): the "ap" completion curve tracks
    anchored CORRECT's tick-15 "apq" curve (500/499/495/433 per 500)
    within ~2x at every point — the false-typed lock + falsity chain
    cost nothing in growth.
P4 (measurement, no falsifier): loose "apq" (decision sites only)
    ~ 0 at dG >= 2 — D3F absorbs the row-3 decision site at b=2 and
    never detaches, so true-tile transients die before read.

Reference curves printed per point (envelope discipline from the
multirow grid): e^{-dG}, e^{-2dG}; plus the tick-15 comparison rows
WRONG_CUT strict apq (1.000/0.992/0.726/0.006) and CORRECT apq.
"""
import json
import math
import os
import random
import sys
from collections import Counter
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
MULTIROW = os.path.join(os.path.dirname(HERE), "2026-10-06-multirow-ktam-grid")
for p in (HERE, MULTIROW):
    if p not in sys.path:
        sys.path.insert(0, p)

from ktam_mc_multirow import (AnchoredAPI, run_assembly,  # noqa: E402
                              GSE, GMC_GRID, N_PER_POINT, T_READ_MULTIPLIER)
from tiles_cutlock import WRONG_CUT_LOCKFALSE  # noqa: E402

BASE_SEED = 20261016

# tick-15 reference rows (evidence/2026-10-06-multirow-ktam-grid/run.out)
WRONGCUT_APQ_STRICT = {0.5: 1.000, 2.0: 0.992, 4.0: 0.726, 7.0: 0.006}
CORRECT_APQ_STRICT = {0.5: 1.000, 2.0: 0.998, 4.0: 0.990, 7.0: 0.866}

API = AnchoredAPI(WRONG_CUT_LOCKFALSE)


def point_chunk(args):
    Gmc, seed0, n = args
    T_read = T_READ_MULTIPLIER * math.exp(Gmc)
    return Gmc, [run_assembly(API, Gmc, GSE, T_read, seed0 + i)
                 for i in range(n)]


def main():
    jobs = []
    for Gmc in GMC_GRID:
        seed0 = BASE_SEED + int(round((Gmc - GSE) * 1000)) * 10000
        jobs.append((Gmc, seed0, N_PER_POINT))
    print(json.dumps({
        "Gse": GSE, "T_read_rule": "400*exp(Gmc)", "n_per_point": N_PER_POINT,
        "seed_base": BASE_SEED,
        "model": "kTAM v3 no-mismatch, per-row value-typed locks, 3 rows",
        "system": {"name": API.name, "expected": API.expected,
                   "build": "wrong cut (q:-p) + post-cut fixpoint re-pred"
                            " q=false; lock on rq-f; falsity chain"
                            " D3F.S=rp-t-done"},
        "predictions": ["P1 strict ap >= 0.9 per point at dG<=4",
                        "P2 strict apq <= 3/500 at dG in {2,4,7}",
                        "P3 ap curve within ~2x of CORRECT apq curve",
                        "P4 loose apq ~ 0 at dG>=2"],
        "tick15_reference": {"wrongcut_apq_strict": WRONGCUT_APQ_STRICT,
                             "correct_apq_strict": CORRECT_APQ_STRICT},
    }), flush=True)
    with Pool(min(16, os.cpu_count() or 1)) as pool:
        results = pool.map(point_chunk, jobs)
    tot_wrong_apq = 0
    tot_ap = 0
    tot = 0
    for Gmc, decodes in results:
        c = Counter(d.split("|")[0] for d in decodes)
        cl = Counter(d.split("|")[1] for d in decodes)
        n = sum(c.values())
        dG = round(Gmc - GSE, 1)
        tot_wrong_apq += c.get("apq", 0)
        tot_ap += c.get("ap", 0)
        tot += n
        print(json.dumps({
            "system": API.name, "Gmc": Gmc, "dGmc": dG, "n": n,
            "decode": dict(sorted(c.items())),
            "decode_loose": dict(sorted(cl.items())),
            "expected": API.expected,
            "ap_frac": round(c.get("ap", 0) / n, 4),
            "apq_frac": round(c.get("apq", 0) / n, 4),
            "partial_frac": round(c.get("partial", 0) / n, 4),
            "tick15_wrongcut_apq": WRONGCUT_APQ_STRICT[dG],
            "tick15_correct_apq": CORRECT_APQ_STRICT[dG],
            "curve_e_neg_dG": round(math.exp(-dG), 4),
            "curve_e_neg_2dG": round(math.exp(-2 * dG), 5),
        }), flush=True)
    print(json.dumps({
        "system": API.name, "ap_total": tot_ap, "apq_total": tot_wrong_apq,
        "n_total": tot, "apq_ci95_upper": round(3.0 / tot, 6),
    }), flush=True)


if __name__ == "__main__":
    main()
