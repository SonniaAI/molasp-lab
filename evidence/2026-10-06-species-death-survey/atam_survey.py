"""Species-death survey — aTAM arm (tick 23, SON-4775).

Tick 22 removed ONE species (DAr) and found the true-model readout
kinetically rebuilt through a DBr+L3 mutual b=2 trap (designs/003
F5 arm). Its honest limits named the general question: which
removals repair, which kill. This survey is the aTAM half:
BUILD1 (P_AND `p. q. r :- p, q.`, errata E1/E2 applied) minus EACH
of its 12 tile species in turn, exhaustive tau=2 BFS per removal
(same machinery as tick 18 / tick 22).

Recorded per removal (machine-checked, exhaustive):
  - producible assembly count, terminal count
  - every terminal's lock-column decode + locked-row count
  - which surviving tiles are never producible
  - whether a strict "pqr" terminal survives (PRESERVED)
  - clingo anchor: which residual program's stable model the
    terminal decode equals, if any

Classification (computed, not asserted):
  PRESERVED      some terminal decodes "pqr"
  FAITHFUL_SUB   all terminals decode a strict subset of "pqr"
                 with >= 1 locked row (the missing species reads
                 as a dropped-something model)
  COLLAPSED      some terminal has zero locked rows or an empty
                 decode (upstream spine/lock death)
  AMBIGUOUS      terminals disagree — recorded with the split; a
                 confidently-wrong read needs a unique terminal

Pre-registration for the paired kTAM arm lives in ktam_mc_survey.py
(both files are submitted together; the aTAM table is computed
in-process by the job so the receipts cannot drift apart).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SIB_AND = os.path.join(os.path.dirname(HERE),
                       "2026-10-06-body-conjunction-builds")
SIB_DEATH = os.path.join(os.path.dirname(HERE),
                         "2026-10-06-structural-death")
for p in (HERE, SIB_AND, SIB_DEATH):
    if p not in sys.path:
        sys.path.insert(0, p)

from tiles_and import BUILD1, PROGRAMS  # noqa: E402
from tiles_death import build_missing_species  # noqa: E402
from atam_check_and import (producible, decode, clingo_models,  # noqa: E402
                            TAU)

# The 12 synthesised species of BUILD1 (seed cells are not species).
SPECIES = sorted(BUILD1["tiles"].keys())

# Canonical position of each species in the correct assembly
# (S | D | V | L columns x=0..3, rows y=1..3 above the 4-wide seed).
CANONICAL_SITE = {
    "S1": (0, 1), "D1T": (1, 1), "V0p": (2, 1), "L1": (3, 1),
    "S2": (0, 2), "D2T": (1, 2), "Vp": (2, 2), "L2": (3, 2),
    "S3": (0, 3), "DAr": (1, 3), "DBr": (2, 3), "L3": (3, 3),
}

# Residual programs whose stable models anchor terminal decodes
# (which solver answer, if any, does the death read as?).
RESIDUALS = {
    "P_AND": "p. q. r :- p, q.",
    "drop_r_rule": "p. q.",
    "drop_q_fact": "p. r :- p, q.",
    "drop_p_fact": "q. r :- p, q.",
    "r_rule_loses_p": "p. q. r :- q.",
    "r_rule_loses_q": "p. q. r :- p.",
    "p_only": "p.",
    "q_only": "q.",
}


def classify(term_rows):
    """term_rows: list of (decode_string, locked_count)."""
    decodes = sorted({d for d, _ in term_rows})
    if "pqr" in decodes:
        label = "PRESERVED"
    elif len(decodes) > 1:
        label = "AMBIGUOUS"
    elif decodes == [""]:
        label = "COLLAPSED"
    elif decodes and set(decodes[0]) < set("pqr"):
        locked = [l for _, l in term_rows]
        label = "FAITHFUL_SUB" if min(locked) >= 1 else "COLLAPSED"
    else:
        label = "OTHER"
    return label, decodes


def run_survey():
    anchors = {}
    for name, prog in RESIDUALS.items():
        models = clingo_models(prog)
        if models:
            atoms = sorted(a.rstrip(".") for a in models[0])
            anchors[name] = "".join(a for a in "pqr" if a in atoms)
        else:
            anchors[name] = None

    rows = []
    for sp in SPECIES:
        b = build_missing_species(BUILD1, sp)
        seen, terms = producible(b)
        term_rows = [decode(b, t) for t in terms]
        label, decodes = classify(term_rows)
        placed = {n: any(n in dict(a).values() for a in seen)
                  for n in b["tiles"]}
        unproducible = sorted(n for n, v in placed.items() if not v)
        row = {
            "removed": sp,
            "canonical_site": CANONICAL_SITE[sp],
            "assemblies": len(seen),
            "terminals": len(terms),
            "terminal_decodes": term_rows,
            "label": label,
            "unproducible_tiles": unproducible,
            "anchors": sorted(k for k, v in anchors.items()
                              if v is not None and v in decodes),
        }
        rows.append(row)
    return {"tau": TAU, "species": SPECIES, "anchors": anchors,
            "rows": rows,
            "programs": dict(PROGRAMS), "residuals": RESIDUALS}


def main():
    report = run_survey()
    out = os.path.join(HERE, "atam_survey.out")
    with open(out, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    print(json.dumps(report, indent=1, sort_keys=True))
    return report


if __name__ == "__main__":
    main()
