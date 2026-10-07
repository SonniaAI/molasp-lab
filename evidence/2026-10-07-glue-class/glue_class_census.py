#!/usr/bin/env python3
"""Glue-CLASS boundary census (tick 35, SON-4778) — the last open
designs/004 item, closed by EXACT enumeration (no Monte Carlo).

Question: the row scope never qualifies the structural glue classes
(spine go* entries, and*/base/w* relays, caps).  Does extending the
knob to them (scope 'class' = row PLUS every non-value, non-SP
canonical-bond rename) change any hazard channel — or is the class
boundary inert?

Why static is exact here (and no cluster spend is warranted): the
row-scope kinetic surprises (RS1/RS2, ticks 31-33) happened because
the one-site census OVER-APPROXIMATES channels and kinetics decides.
This study enumerates the complete inventory matching predicate
(scope_bond_identity: every opposing tile-face pair + every seed
bond, compared row vs class).  kTAM/aTAM dynamics depend only on
that predicate and the strengths, both unchanged under a rename
that touches a canonical-pair-exclusive glue on both faces.  An
empty diff therefore decides kinetics by construction — there is
no sampled channel left for a trajectory to over-rule.

PRE-REGISTERED predictions (gates fixed before running):
  C1  every non-value glue in BUILD1/2/3 is canonical_pair,
      seed_bond or inert_single — no 'shared' structural glue, so
      no off-channel use exists for the class glues at all.
      [FALSIFIED: any non-value glue with status 'shared']
  C2  the row-vs-class matching-predicate diff is EMPTY on
      BUILD1/2/3 — the class scope renames only canonical-pair-
      exclusive glues, splits nothing, and is kinetically identical
      to row.
      [FALSIFIED: any nonempty diff entry]
  C3  canonical assemblies stay >= tau=2 at every site under class
      scope on all three builds.
      [FALSIFIED: any site < 2]
  C4  the full check_d4 report is IDENTICAL row vs class on
      BUILD1/2/3 — the emit-time census view sees no change.
      [FALSIFIED: any report difference]
  R1  (rename principle, explanatory) every row-scope surviving
      channel bond has EQUAL final glue names on both faces — the
      displaced-pair / same-tag recombination class:
        Vp.N <-> DBr.S   (vertical lock stack, H3's 141/141)
        D2T.N <-> DAr.S  (relay-stack repair, N arm)
        D2T.S <-> V0p.N  (relay-stack repair, S arm)
        D2T.W <-> S2.E   (relay-stack repair, W arm — go2, a class
                          glue the row rule never touched)
      and the kill case is a one-face split: D1T.E 'p-t' vs L1.W
      'p-t-lk1' (the lock-read rename that broke the D1T/V0p
      channel).  A rename can only kill a bond whose faces land on
      DIFFERENT final names; it is structurally blind to displaced
      pairs, which is why RS1/RS2 falsified the elimination
      reading.
      [checked as enumeration; reported]

Verdicts are machine-computed in the final line.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SIB_AND = os.path.join(os.path.dirname(HERE),
                       "2026-10-06-body-conjunction-builds")
for p in (HERE, REPO, SIB_AND):
    if p not in sys.path:
        sys.path.insert(0, p)

from tiles_and import BUILD1, BUILD2, BUILD3  # noqa: E402
from molasp.offchannel import (  # noqa: E402
    apply_lock_glue_scope, canonical_assembly, check_d4,
    glue_class_census, matched_strength, scope_bond_identity)

BUILDS = (("BUILD1", BUILD1), ("BUILD2", BUILD2), ("BUILD3", BUILD3))

# R1 face pairs: (tileA, faceA, tileB, faceB, expected_final_equality)
R1_PAIRS = (
    ("Vp", "N", "DBr", "S"), ("D2T", "N", "DAr", "S"),
    ("D2T", "S", "V0p", "N"), ("D2T", "W", "S2", "E"))
R1_SPLIT = ("D1T", "E", "L1", "W")


def main():
    report = {"study": "glue-class boundary census (tick 35)",
              "builds": {}, "r1_rename_principle": {}}
    c1 = c2 = c3 = c4 = True
    for name, b in BUILDS:
        canon = canonical_assembly(b)
        row_b = apply_lock_glue_scope(b, "row", canon)
        cls_b = apply_lock_glue_scope(b, "class", canon)
        cen = glue_class_census(b, canon)
        shared_nonvalue = sorted(
            g for g, v in cen.items()
            if v["status"] == "shared" and v["class"] != "value")
        diff = scope_bond_identity(b, "row", "class", canon)
        tau = {("%d,%d" % s): matched_strength(cls_b, canon, s, t)
               for s, t in canon.items()}
        tau_ok = all(v >= 2 for v in tau.values())
        d4_same = check_d4(row_b, canon) == check_d4(cls_b, canon)
        report["builds"][name] = {
            "census": cen,
            "shared_nonvalue_glues": shared_nonvalue,
            "row_vs_class_bond_diff": diff,
            "class_canonical_bonds": tau,
            "d4_report_identical_row_vs_class": d4_same,
        }
        c1 = c1 and not shared_nonvalue
        c2 = c2 and not diff
        c3 = c3 and tau_ok
        c4 = c4 and d4_same

    row1 = apply_lock_glue_scope(BUILD1, "row", canonical_assembly(BUILD1))
    t1 = report["r1_rename_principle"]
    t1["surviving_pairs_equal_final_names"] = {
        "%s.%s<->%s.%s" % p: [row1["tiles"][p[0]][p[1]],
                              row1["tiles"][p[2]][p[3]]] for p in R1_PAIRS}
    t1["all_survivors_equal"] = all(
        row1["tiles"][a][fa] == row1["tiles"][c][fc] for a, fa, c, fc
        in R1_PAIRS)
    t1["kill_case_split_final_names"] = {
        "D1T.E": row1["tiles"]["D1T"]["E"], "L1.W": row1["tiles"]["L1"]["W"]}
    t1["split_is_real"] = (row1["tiles"]["D1T"]["E"]
                           != row1["tiles"]["L1"]["W"])

    verdicts = {
        "C1_no_shared_structural_glue": c1,
        "C2_row_class_matching_predicate_identical": c2,
        "C3_canonical_assemblies_ge_tau2_under_class": c3,
        "C4_d4_reports_identical_row_vs_class": c4,
        "R1_rename_principle_holds": t1["all_survivors_equal"]
        and t1["split_is_real"],
    }
    out = os.path.join(HERE, "glue_class.out")
    with open(out, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps({k: v for k, v in report.items()
                      if k != "builds"}, indent=1, sort_keys=True))
    print("VERDICTS " + json.dumps(verdicts, sort_keys=True))
    return report


if __name__ == "__main__":
    main()
