#!/usr/bin/env python3
"""Stack-channel dG sweep (tick 34 pre-registration, SON-4778).

Question: does 2-of-3 REDUNDANT stacking starve with dG the way the
solo family channel did (R4: squat 0.314 -> 0.118 -> 0.000 by dG 4),
or does redundancy keep both surviving row-scope channels alive?

Systems: BUILD1 under row scope only (the regime where the stack
channels are the survivors), plain + Vp-missing — the two arms of
recombination.out.  dG grid: 0.5 / 2.0 / 4.0 (the R4 levels), Gmc
fixed at 9.5, Gse = Gmc - dG, protocol of record (T_read =
400*exp(Gmc)), fresh seed block base 120261107 stride 2e7 (disjoint
from all prior studies), n=500/arm (6 arms, 3000 trajectories).

Per trajectory: read-time decode, lock squats, the VERTICAL lock
stack co-hold (Vp@(3,2) AND DBr@(3,3)), stable (b>=2) D2T@(2,2)
fill with its partner fan (redundancy via load-bearing flags).

PRE-REGISTERED predictions (gates fixed before submission):
  S1  row_build1 read-block decays with dG: blocked(dG4) <= 0.02
      AND monotone non-increasing over 0.5/2/4.
      [FALSIFIED: blocked(dG4) >= 0.10 — redundancy does not starve]
  S2  row_Vp stable D2T fill decays with dG: fill(dG4) <= 0.02
      AND monotone non-increasing.
      [FALSIFIED: fill(dG4) >= 0.10]
  S3  redundant composition survives among events: b_ge3 frac of
      stable holds >= 0.8 at every dG with n_stable >= 10.
      [FALSIFIED: < 0.5 at any such dG]
  S4  calibration at dG 0.5 vs recombination.out refs: |blocked -
      0.141| <= 0.05 AND |fill - 0.155| <= 0.05.
      [FALSIFIED: any drift >= 0.10 — protocol drift]
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SIB_AND = os.path.join(os.path.dirname(HERE),
                       "2026-10-06-body-conjunction-builds")
SIB_REC = os.path.join(os.path.dirname(HERE), "2026-10-07-recombination")
for p in (HERE, REPO, SIB_AND, SIB_REC):
    if p not in sys.path:
        sys.path.insert(0, p)

from ktam_recombination import (  # noqa: E402
    GMC, SYSTEMS, VAC, partner_bonds, read_lock_squats,
    run_assembly_history)

DG_GRID = (0.5, 2.0, 4.0)
N_PER_ARM = 500
BASE_SEED = 120261107
SEED_STRIDE = 20000000
T_READ_MULT = 400.0
ARMS = ("row_build1", "row_Vp")   # SYSTEMS order: fam, famVp, row, rowVp
SYS_INDEX = {"row_build1": 2, "row_Vp": 3}

REFS = {"row_build1_blocked_dG0.5": 0.141,
        "row_Vp_stable_fill_dG0.5": 0.155}

PREDICTIONS = [
    "S1 row_build1 blocked(dG4) <= 0.02 AND monotone [>= 0.10 at dG4 falsified]",
    "S2 row_Vp stable fill(dG4) <= 0.02 AND monotone [>= 0.10 falsified]",
    "S3 stable-hold b_ge3 frac >= 0.8 at every dG with n_stable >= 10 [< 0.5 falsified]",
    "S4 dG0.5 within 0.05 of 0.141 blocked / 0.155 fill [>= 0.10 drift falsified]",
]


def run_arm(key, dg, seed0, n):
    api = SYSTEMS[SYS_INDEX[key]]
    gse = GMC - dg
    t_read = T_READ_MULT * math.exp(GMC)
    outs = []
    for i in range(n):
        h = run_assembly_history(api, GMC, gse, t_read, seed0 + i)
        asm = h["assembly"]
        strict = api.decode(asm)
        blocked, squats = read_lock_squats(asm)
        occ22 = asm.get(VAC)
        stable = occ22 == "D2T" and api.matched(asm, VAC, "D2T") >= 2
        vstack = asm.get((3, 2)) == "Vp" and asm.get((3, 3)) == "DBr"
        b22, partners = (partner_bonds(api, asm, VAC, "D2T")
                         if occ22 == "D2T" else (None, None))
        lb_any = bool(partners) and any(
            p["load_bearing"] for p in partners.values())
        n_relay = (sum(1 for p in (partners or {}).values() if p["bond"] > 0)
                   if partners else 0)
        outs.append({
            "strict": strict, "blocked": blocked,
            "squats": dict(squats), "vstack": vstack, "stable": stable,
            "b22": b22, "n_relay": n_relay, "lb_any": lb_any,
        })
    blocked_frac = sum(o["blocked"] for o in outs) / float(n)
    vstack_frac = sum(o["vstack"] for o in outs) / float(n)
    vstack_of_blocked = (
        sum(o["vstack"] for o in outs if o["blocked"]) /
        float(sum(1 for o in outs if o["blocked"]) or 1))
    stable_n = sum(o["stable"] for o in outs)
    stable_fill = stable_n / float(n)
    b_hist = {}
    for o in outs:
        if o["stable"]:
            b_hist[o["b22"]] = b_hist.get(o["b22"], 0) + 1
    b_ge3 = sum(v for k, v in b_hist.items() if k >= 3)
    return {
        "system": api.build["name"], "key": key, "dG": dg, "n": n,
        "blocked_frac": round(blocked_frac, 4),
        "vstack_frac": round(vstack_frac, 4),
        "vstack_of_blocked": round(vstack_of_blocked, 4),
        "stable_fill": round(stable_fill, 4),
        "stable_n": stable_n,
        "b22_hist": {str(k): v for k, v in sorted(b_hist.items())},
        "b_ge3_frac": round(b_ge3 / float(stable_n), 4) if stable_n else None,
        "lb_any_frac": round(
            sum(o["lb_any"] for o in outs if o["stable"]) /
            float(stable_n), 4) if stable_n else None,
        "mean_relay_contacts": round(
            sum(o["n_relay"] for o in outs if o["stable"]) /
            float(stable_n), 3) if stable_n else None,
    }


def verdicts(arms):
    by = {(a["key"], a["dG"]): a for a in arms}
    out = {}
    b = {dg: by[("row_build1", dg)]["blocked_frac"] for dg in DG_GRID}
    mono_b = b[0.5] >= b[2.0] >= b[4.0]
    out["S1"] = {"blocked": b, "monotone": mono_b,
                 "call": ("confirmed" if (b[4.0] <= 0.02 and mono_b)
                          else ("falsified" if b[4.0] >= 0.10
                                else "inconclusive"))}
    f = {dg: by[("row_Vp", dg)]["stable_fill"] for dg in DG_GRID}
    mono_f = f[0.5] >= f[2.0] >= f[4.0]
    out["S2"] = {"stable_fill": f, "monotone": mono_f,
                 "call": ("confirmed" if (f[4.0] <= 0.02 and mono_f)
                          else ("falsified" if f[4.0] >= 0.10
                                else "inconclusive"))}
    bad = [dg for dg in DG_GRID
           if by[("row_Vp", dg)]["stable_n"] >= 10
           and by[("row_Vp", dg)]["b_ge3_frac"] is not None
           and by[("row_Vp", dg)]["b_ge3_frac"] < 0.8]
    out["S3"] = {"b_ge3_by_dG": {str(dg): by[("row_Vp", dg)]["b_ge3_frac"]
                                 for dg in DG_GRID},
                 "call": ("falsified" if any(
                     by[("row_Vp", dg)]["b_ge3_frac"] is not None
                     and by[("row_Vp", dg)]["b_ge3_frac"] < 0.5
                     for dg in DG_GRID
                     if by[("row_Vp", dg)]["stable_n"] >= 10)
                     else ("confirmed" if not bad else "inconclusive"))}
    dev_b = abs(b[0.5] - REFS["row_build1_blocked_dG0.5"])
    dev_f = abs(f[0.5] - REFS["row_Vp_stable_fill_dG0.5"])
    out["S4"] = {"dev_blocked": round(dev_b, 4),
                 "dev_fill": round(dev_f, 4),
                 "call": ("calibrated" if (dev_b <= 0.05 and dev_f <= 0.05)
                          else "drift" if (dev_b >= 0.10 or dev_f >= 0.10)
                          else "inconclusive")}
    return out


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else N_PER_ARM
    print(json.dumps({
        "Gse_rule": "Gmc - dG", "Gmc": GMC, "dG_grid": DG_GRID,
        "T_read_rule": "400*exp(Gmc)", "n_per_arm": n,
        "seed_base": BASE_SEED, "seed_stride": SEED_STRIDE,
        "model": "kTAM v3 no-mismatch; systems = BUILD1 row scope "
                 "{plain, Vp-missing}; stack-channel dG sweep "
                 "(recombination.out mechanism, S1-S4)",
        "predictions": PREDICTIONS, "references": REFS,
    }))
    arms = []
    arm_i = 0
    for key in ARMS:
        for dg in DG_GRID:
            seed0 = BASE_SEED + arm_i * SEED_STRIDE
            arm_i += 1
            arms.append(run_arm(key, dg, seed0, n))
            print(json.dumps(arms[-1]))
            sys.stdout.flush()
    print("VERDICTS " + json.dumps(verdicts(arms)))


if __name__ == "__main__":
    main()
