#!/usr/bin/env python3
"""designs/005 census-generality probe — pre-registered gates G1-G4.

Arms (compiled through compile_program v0.1, family scope):
  MINIMAL     p.
  AND_ONLY    p. q. r :- p, q.
  UNIT_ONLY   p. q. r :- p.
  DEEP_FACTS  p. q. s. r :- s, p.

Gates registered in designs/005-census-generality.md BEFORE this
script's census output was produced (compilability smoke only, no
hazard data inspected, 2026-10-07 tick 37):

  G1  every arm: >=1 lock hazard AND all lock-squat tiles V-class
      [falsified: any arm zero hazards, or any non-V lock squatter]
  G2  no arm: solo stable (b>=2) lock hazard — all solo hazards b=1
      [falsified: any stable solo hazard]
  G3  stack channels: AND_ONLY>=1 and DEEP_FACTS>=1;
      UNIT_ONLY==0 and MINIMAL==0
      [falsified: the complement in any arm]
  G4  off-channel sites: DEEP_FACTS > MINIMAL and DEEP_FACTS > AND_ONLY
      [falsified: either inequality fails]

Output: one JSON line per arm + one VERDICTS line. Exit 0 always —
the census reports; gates are recorded, not gating (d4 semantics).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from molasp.compiler import compile_program          # noqa: E402
from molasp.offchannel import check_d4               # noqa: E402

ARMS = [
    ("MINIMAL", "p."),
    ("AND_ONLY", "p. q. r :- p, q."),
    ("UNIT_ONLY", "p. q. r :- p."),
    ("DEEP_FACTS", "p. q. s. r :- s, p."),
]


def main():
    lines, per_arm = [], {}
    for name, prog in ARMS:
        build = compile_program(prog, name=name)
        rep = check_d4(build)                    # explicit receipt census
        # compile_program's auto-attached d4 must agree (A1-style
        # cross-check between the two call paths)
        assert json.dumps(build["d4"], sort_keys=True) == \
            json.dumps(rep, sort_keys=True), name
        rec = {
            "arm": name,
            "program": prog,
            "rows": len(build["rows"]),
            "tiles": len(build["tiles"]),
            "off_channel_sites": len(rep["off_channel"]),
            "lock_hazards": rep["lock_hazards"],
            "lock_hazards_stable": rep["lock_hazards_stable"],
            "lock_hazards_transient": rep["lock_hazards_transient"],
            "lock_stack_channels": rep["lock_stack_channels"],
            "lock_misreads": rep["lock_misreads"],
        }
        lines.append(json.dumps(rec, sort_keys=True))
        per_arm[name] = rec
        print(json.dumps(rec, sort_keys=True))

    def squatters(rec):
        out = []
        for _site, sq in rec["lock_hazards"].items():
            out.extend(sq.keys())
        return out

    g1 = all(
        len(squatters(r)) >= 1 and all(t.startswith("V") for t in squatters(r))
        for r in per_arm.values())
    g2 = all(r["lock_hazards_stable"] == {} for r in per_arm.values())
    g3 = (len(per_arm["AND_ONLY"]["lock_stack_channels"]) >= 1
          and len(per_arm["DEEP_FACTS"]["lock_stack_channels"]) >= 1
          and len(per_arm["UNIT_ONLY"]["lock_stack_channels"]) == 0
          and len(per_arm["MINIMAL"]["lock_stack_channels"]) == 0)
    g4 = (per_arm["DEEP_FACTS"]["off_channel_sites"]
          > per_arm["MINIMAL"]["off_channel_sites"]
          and per_arm["DEEP_FACTS"]["off_channel_sites"]
          > per_arm["AND_ONLY"]["off_channel_sites"])
    verdicts = {"G1": g1, "G2": g2, "G3": g3, "G4": g4}
    vline = "VERDICTS " + json.dumps(verdicts, sort_keys=True)
    print(vline)
    lines.append(vline)

    out_path = os.path.join(HERE, "census_generality.out")
    with open(out_path, "w") as fh:
        fh.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
