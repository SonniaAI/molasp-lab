"""Supported-vs-stable checker (regenerated 2026-10-06).

The original checker scripts for the C2-witness selection were lost with
the 2026-10-05 history purge (see research-log/2026-10-05-c2-witness.md);
this file regenerates them from the definitions, directly:

  - Stable models via Gelfond-Lifschitz reduct + least model.
  - Supported models (Clark completion) via model + supportedness.

Programs are inlined as explicit rule tuples (no parser dependency);
sources are quoted verbatim in PROGRAMS for traceability. The expected
table is the one published in research-log/2026-10-05-c2-witness.md,
which this script re-derives rather than trusts.

A clingo cross-check (independent oracle over the same five programs)
remains queued for the first cluster tick; this checker is the
first-party derivation of record.
"""
import itertools
import json
from collections import namedtuple

Rule = namedtuple("Rule", "head pos neg")

PROGRAMS = {
    "p :- p.": [Rule("p", ["p"], [])],
    "a. p :- p.": [Rule("a", [], []), Rule("p", ["p"], [])],
    "p :- q. q :- p.": [Rule("p", ["q"], []), Rule("q", ["p"], [])],
    "a. p :- q. q :- p.": [Rule("a", [], []), Rule("p", ["q"], []), Rule("q", ["p"], [])],
    "a. q :- a.  (tight control)": [Rule("a", [], []), Rule("q", ["a"], [])],
}


def atoms(rules):
    out = set()
    for r in rules:
        out.add(r.head)
        out.update(r.pos)
        out.update(r.neg)
    return sorted(out)


def least_model(rules_positive, herbrand):
    """Least model of a definite program: lfp of immediate consequence."""
    m = set()
    changed = True
    while changed:
        changed = False
        for r in rules_positive:
            if r.head not in m and all(b in m for b in r.pos):
                m.add(r.head)
                changed = True
    return m


def stable_models(rules):
    out = []
    aset = atoms(rules)
    for bits in itertools.product((False, True), repeat=len(aset)):
        X = {a for a, b in zip(aset, bits) if b}
        # Gelfond-Lifschitz reduct P^X: drop rules with not c, c in X;
        # strip negative literals.
        reduct = [Rule(r.head, list(r.pos), []) for r in rules
                  if not (set(r.neg) & X)]
        if least_model(reduct, aset) == X:
            out.append(frozenset(X))
    return out


def supported_models(rules):
    out = []
    aset = atoms(rules)
    for bits in itertools.product((False, True), repeat=len(aset)):
        X = {a for a, b in zip(aset, bits) if b}
        # model of P
        model = all(r.head in X for r in rules
                    if set(r.pos) <= X and not (set(r.neg) & X))
        # supportedness: every a in X has a rule body satisfied by X
        sup = all(any(set(r.pos) <= X and not (set(r.neg) & X)
                      for r in rules if r.head == a)
                  for a in X)
        if model and sup:
            out.append(frozenset(X))
    return out


def fmt(models):
    return sorted("{" + ",".join(sorted(m)) + "}" for m in models)


def main():
    rows, failures = [], []
    for src, rules in PROGRAMS.items():
        st, su = stable_models(rules), supported_models(rules)
        gap = sorted(set(su) - set(st))
        row = {
            "program": src,
            "stable": fmt(st),
            "supported": fmt(su),
            "supported_but_unstable": fmt(gap),
        }
        rows.append(row)
        print(json.dumps(row))
        if src == "a. q :- a.  (tight control)" and gap:
            failures.append("tight control shows a gap; Fages violated?")
    # expected table from research-log/2026-10-05-c2-witness.md
    expected = {
        "p :- p.": (["{}"], ["{}", "{p}"], ["{p}"]),
        "a. p :- p.": (["{a}"], ["{a}", "{a,p}"], ["{a,p}"]),
        "p :- q. q :- p.": (["{}"], ["{}", "{p,q}"], ["{p,q}"]),
        "a. p :- q. q :- p.": (["{a}"], ["{a}", "{a,p,q}"], ["{a,p,q}"]),
        "a. q :- a.  (tight control)": (["{a,q}"], ["{a,q}"], []),
    }
    for row in rows:
        exp = expected[row["program"]]
        got = (row["stable"], row["supported"], row["supported_but_unstable"])
        # order-insensitive comparison (set-of-frozensets per column)
        norm = lambda col: {frozenset(s.strip("{}").split(",")) if s != "{}" else frozenset() for s in col}
        if [norm(g) for g in got] != [norm(e) for e in exp]:
            failures.append(f"{row['program']}: got {got}, expected {exp}")
    if failures:
        print("CHECK FAILED:")
        for f in failures:
            print(" -", f)
        raise SystemExit(1)
    print("SUPPORTED-VS-STABLE CHECK PASSED: table re-derived from the "
          "GL-reduct and completion definitions; matches the published "
          "witness selection, including the tight control.")


if __name__ == "__main__":
    main()
