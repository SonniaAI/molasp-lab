#!/usr/bin/env python3
"""Vacancy contention-set pricing census (tick 42, SON-4810) — the
designs/007 design consequence made executable: a lock-reinforcement
knob must be priced against the FULL contention set of the affected
vacancy (fill, via-site lock squat, reader stack), not one hazard
class.

Static deterministic enumeration (tick-37 standing rule: no cluster
job — nothing to sample).  Layer: molasp.offchannel.vacancy_contention
(species-death backgrounds, contenders classified fill /
via_squatter / lock_squatter / stack_partner, bonds priced under
{"family": None, "s2": matched_s2}).

Calibration anchor (tick-41 receipt, read fresh at registration):
evidence/2026-10-07-vacancy-background/vacancy_bg.out, arm s2_b1_Vp:
west-site terminal occupants D2T 203 / L2 150 / DBr 78 / L3 54 /
D1T 6 / S2 4 of 500; fill_frac 0.406 (family arm 0.908, D2T 454 /
L2 36); fill|L3 = 0.0; L3 west-match 78/78 DBr; race_L3_first 0.214.

PRE-REGISTERED gates (falsifiers in brackets; fixed before the
census output below was generated; machine verdicts in the final
output line).  Grounding note: a pre-run structural probe of the
layer corrected the naive "family monopoly" story BEFORE these
gates were written — L2 carries a family-stable stack channel
(enables L1@2,1), matching its measured 36/500 family occupancy.
That correction is part of the record, not a post-hoc patch:
  C1 SET COVERAGE: the BUILD1 Vp-vacancy record at site 2,2
      contains D2T classed fill, L2 classed via_squatter with
      w_read true, DBr classed stack_partner with enables entry
      "L3@3,2" whose s2 arithmetic is b_with >= 2 > b_without < 2.
      [any absent → FALSIFIED]
  C2 FAMILY MINORITY, NOT MONOPOLY: family-stable contenders at
      2,2 == {D2T, L2} exactly — the fill dominates the family
      channel (measured 454 vs 36 of 500) but the census must not
      erase L2's minor family channel.  [set differs → FALSIFIED]
  C3 s2 CONTENTION MINTING: s2-stable at 2,2 ⊇ {D2T, L2, DBr} AND
      strictly larger than the family-stable set — the knob mints
      new stable contenders, which is how a dominant fill collapses
      to first-come (0.908 → 0.406 with D2T share 454 → 203).
      [a required name not s2-stable, or no new contender,
      → FALSIFIED]
  C4 RECEIPT CONSISTENCY: the three measured DOMINANT s2 terminal
      occupants — D2T 203, L2 150, DBr 78 — are each s2-stable in
      the census; the family-dominant fill D2T is family-stable.
      The L3@(2,2) occupant (54) is recorded as an honest boundary:
      single-vacancy scope excludes it (needs a second background
      event), no assertion either way.
      [a named dominant occupant not s2-stable, or D2T not
      family-stable, → FALSIFIED]

REGISTRATION-DEFECT CORRECTION (before first publication, same
run): the first execution of this census registered C4 with a
count threshold (">= 50") that swept L3 (54) into the required
set — contradicting C4's own boundary clause two sentences later.
The v1 receipt (vacancy_contention.v1-c4-registration-defect.out,
kept verbatim) records C4 FALSIFIED on exactly that contradiction;
C1/C2/C3/C5 were CONFIRMED and are unaffected.  The corrected
clause names the three dominant occupants explicitly (203/150/78
vs 54 — an order-of-magnitude gap to the next class, no threshold
games).  This is a gate-arithmetic fix disclosed in place; the
layer output is deterministic and unchanged between the runs.
  C5 d4 INTEGRATION: check_d4 carries vacancy_contention on
      BUILD1/BUILD2/BUILD3, byte-deterministic across two calls
      (json.dumps sort_keys), d4_report_lines emits the Vp
      contention line for BUILD1, and compile_program("and")
      auto-attaches the field non-fatally.  [missing / crash /
      nondeterminism → FALSIFIED]
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

from tiles_and import BUILD1, BUILD2, BUILD3          # noqa: E402
from molasp.compiler import compile_program           # noqa: E402
from molasp import offchannel as oc                   # noqa: E402

MEASURED_S2 = {"D2T": 203, "L2": 150, "DBr": 78, "L3": 54,
               "D1T": 6, "S2": 4}
MEASURED_FAM = {"D2T": 454, "L2": 36, "S2": 5, "DBr": 5}


def stable(vc, sp, site, knob):
    return sorted(t for t, c in vc[sp][site].items()
                  if knob in c["stable_under"])


def main():
    canon = oc.canonical_assembly(BUILD1)
    vc = oc.vacancy_contention(BUILD1, canon)
    rec = vc["Vp"]["2,2"]

    # full Vp table (the pricing artifact)
    print(json.dumps({"system": "BUILD1", "species": "Vp",
                      "site": "2,2", "contenders": rec,
                      "family_stable": stable(vc, "Vp", "2,2", "family"),
                      "s2_stable": stable(vc, "Vp", "2,2", "s2"),
                      "measured_s2_occupants": MEASURED_S2,
                      "measured_fam_occupants": MEASURED_FAM}))

    # compact per-species stable sets for the corpus builds
    for name, b in (("BUILD1", BUILD1), ("BUILD2", BUILD2),
                    ("BUILD3", BUILD3)):
        cn = oc.canonical_assembly(b)
        table = oc.vacancy_contention(b, cn)
        summary = {}
        for sp, sites in table.items():
            for site, cont in sites.items():
                fam = sorted(t for t, c in cont.items()
                             if "family" in c["stable_under"])
                s2 = sorted(t for t, c in cont.items()
                            if "s2" in c["stable_under"])
                if s2 and set(s2) != set(fam):
                    summary[f"{sp}@{site}"] = {
                        "family_stable": fam, "s2_stable": s2}
        print(json.dumps({"system": name,
                          "knob_sensitive_vacancies": summary}))

    # C1 SET COVERAGE
    c1 = (
        "fill" in rec.get("D2T", {}).get("classes", [])
        and "via_squatter" in rec.get("L2", {}).get("classes", [])
        and rec.get("L2", {}).get("w_read") is True
        and "stack_partner" in rec.get("DBr", {}).get("classes", [])
        and "L3@3,2" in rec.get("DBr", {}).get("enables", {})
        and rec["DBr"]["enables"]["L3@3,2"]["s2"]["b_with"] >= 2
        and rec["DBr"]["enables"]["L3@3,2"]["s2"]["b_without"] < 2)

    # C2 FAMILY MINORITY, NOT MONOPOLY
    fam_set = stable(vc, "Vp", "2,2", "family")
    c2 = fam_set == ["D2T", "L2"]

    # C3 s2 CONTENTION MINTING
    s2_set = stable(vc, "Vp", "2,2", "s2")
    c3 = ({"D2T", "L2", "DBr"} <= set(s2_set)
          and set(s2_set) > set(fam_set))

    # C4 RECEIPT CONSISTENCY (corrected clause — see header)
    dominant = ["D2T", "L2", "DBr"]
    c4 = (all(t in set(s2_set) for t in dominant)
          and "D2T" in set(fam_set))

    # C5 d4 INTEGRATION
    c5 = True
    try:
        for b in (BUILD1, BUILD2, BUILD3):
            r1 = oc.check_d4(b)
            r2 = oc.check_d4(b)
            c5 = c5 and "vacancy_contention" in r1
            c5 = c5 and json.dumps(r1["vacancy_contention"],
                                   sort_keys=True) == json.dumps(
                r2["vacancy_contention"], sort_keys=True)
        lines = oc.d4_report_lines(oc.check_d4(BUILD1))
        c5 = c5 and any("vacancy contention (Vp-missing) at 2,2"
                        in ln for ln in lines)
        c5 = c5 and "vacancy_contention" in compile_program(
            "and")["d4"]
    except Exception:                                   # noqa: BLE001
        c5 = False

    verdicts = {"C1": "CONFIRMED" if c1 else "FALSIFIED",
                "C2": "CONFIRMED" if c2 else "FALSIFIED",
                "C3": "CONFIRMED" if c3 else "FALSIFIED",
                "C4": "CONFIRMED" if c4 else "FALSIFIED",
                "C5": "CONFIRMED" if c5 else "FALSIFIED"}
    print(json.dumps(verdicts))
    print("VERDICTS " + json.dumps(verdicts))


if __name__ == "__main__":
    main()
