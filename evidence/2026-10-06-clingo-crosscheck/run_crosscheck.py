"""Clingo cross-check of the five C2 witness programs (2026-10-06).

Independent-oracle check owed since the 2026-10-05 purge (see
evidence/2026-10-05-supported-vs-stable/README.md): clingo enumerates
the stable models of each witness program, and this script re-derives
stable and supported models from the Gelfond-Lifschitz reduct and
Clark-completion definitions, then asserts, per program:

  (1) clingo's answer sets == the definition-derived stable models;
  (2) stable models are a subset of supported models;
  (3) no supported-but-unstable set appears as a clingo answer set.

Oracle selection, in order of preference:
  - module: the potassco `clingo` Python module (Control(["0"]),
    full enumeration, no output parsing) when importable;
  - cli: the `clingo` binary. v1 lesson (queue request 2a0ae177…, exit
    1): the fastlas image's patched clingo returned status 30 for the
    flagged call, so the CLI path probes invocation variants
    (plain / --models 0 / --models 0 --verbose=0) and treats parsed
    output as authoritative, recording every attempt as diagnostics.

A sixth program (two stable models, tight) is included as an
enumeration-completeness diagnostic: under full enumeration both
models must appear; under a degraded (single-model) oracle it is
reported, not asserted.

The five rule sets are inlined verbatim from the first-party checker
(evidence/2026-10-05-supported-vs-stable/checker.py); the .lp files in
this directory carry the same programs for clingo to read, so the
oracle and the derivation share only the source programs, not code.

Exit 0 only if assertions (1)-(3) hold for all five witness programs.
"""
import itertools
import json
import shutil
import subprocess
import sys
from collections import namedtuple

Rule = namedtuple("Rule", "head pos neg")

# source, rules, .lp filename
PROGRAMS = [
    ("p :- p.",            [Rule("p", ["p"], [])], "p1-selfloop.lp"),
    ("a. p :- p.",         [Rule("a", [], []), Rule("p", ["p"], [])], "p2-min-clean.lp"),
    ("p :- q. q :- p.",    [Rule("p", ["q"], []), Rule("q", ["p"], [])], "p3-2cycle.lp"),
    ("a. p :- q. q :- p.", [Rule("a", [], []), Rule("p", ["q"], []), Rule("q", ["p"], [])], "p4-2cycle-entry.lp"),
    ("a. q :- a.",         [Rule("a", [], []), Rule("q", ["a"], [])], "p5-tight-control.lp"),
]
DIAGNOSTIC = ("a :- not b. b :- not a.  (completeness probe)",
              [Rule("a", [], ["b"]), Rule("b", [], ["a"])],
              "p6-choice-diagnostic.lp")


def atoms(rules):
    out = set()
    for r in rules:
        out.add(r.head)
        out.update(r.pos)
        out.update(r.neg)
    return sorted(out)


def least_model(rules):
    m = set()
    changed = True
    while changed:
        changed = False
        for r in rules:
            if r.head not in m and all(b in m for b in r.pos):
                m.add(r.head)
                changed = True
    return m


def stable_models(rules):
    out = []
    aset = atoms(rules)
    for bits in itertools.product((False, True), repeat=len(aset)):
        X = {a for a, b in zip(aset, bits) if b}
        reduct = [Rule(r.head, list(r.pos), []) for r in rules
                  if not (set(r.neg) & X)]
        if least_model(reduct) == X:
            out.append(frozenset(X))
    return set(out)


def supported_models(rules):
    out = []
    aset = atoms(rules)
    for bits in itertools.product((False, True), repeat=len(aset)):
        X = {a for a, b in zip(aset, bits) if b}
        model = all(r.head in X for r in rules
                    if set(r.pos) <= X and not (set(r.neg) & X))
        sup = all(any(set(r.pos) <= X and not (set(r.neg) & X)
                      for r in rules if r.head == a)
                  for a in X)
        if model and sup:
            out.append(frozenset(X))
    return set(out)


def fmt(models):
    return sorted("{" + ",".join(sorted(m)) + "}" if m else "{}" for m in models)


def module_oracle():
    """Return (enumerate fn, env description) using the potassco module."""
    import clingo  # noqa: imported lazily; caller handles ImportError

    def enumerate_all(path):
        ctl = clingo.Control(["0"])  # 0 = enumerate all answer sets
        ctl.load(path)
        ctl.ground([("base", [])])
        found = []

        def on_model(model):
            found.append(frozenset(s.name for s in model.symbols(atoms=True)))

        ctl.solve(on_model=on_model)
        return set(found), "full", None

    return enumerate_all, f"module clingo {clingo.__version__}"


CLI_VARIANTS = [
    ("plain", []),
    ("models0", ["--models", "0"]),
    ("models0-quiet", ["--models", "0", "--verbose", "0"]),
]


def parse_models(stdout):
    import re
    models, pending = [], False
    for line in stdout.splitlines():
        if line.startswith("Answer:"):
            pending = True
        elif pending and line.strip():
            found = [a for a in re.split(r"[{},\s]+", line.strip()) if a]
            models.append(frozenset(found))
            pending = False
    return models


def cli_oracle():
    """Probe invocation variants; parsed output is authoritative.

    Degraded mode: if no variant returns rc in (0,10,20) with parsed
    models, use the variant that parsed the most models and mark the
    enumeration incomplete.
    """
    ver = subprocess.run(["clingo", "--version"], capture_output=True,
                         text=True, timeout=60)
    env = "cli clingo: " + " ".join(ver.stdout.splitlines()[:1])

    def enumerate_all(path):
        attempts, best = [], (None, [], None)
        for name, extra in CLI_VARIANTS:
            proc = subprocess.run(["clingo"] + extra + [path],
                                  capture_output=True, text=True, timeout=300)
            models = parse_models(proc.stdout)
            attempts.append({"variant": name, "rc": proc.returncode,
                             "models_found": len(models),
                             "stdout_head": proc.stdout[:300],
                             "stderr_head": proc.stderr[:300]})
            if proc.returncode in (0, 10, 20) and models:
                return set(models), "full", attempts
            if len(models) > len(best[1]):
                best = (proc.returncode, models, name)
        if best[1]:
            return set(best[1]), f"degraded(rc={best[0]},{best[2]})", attempts
        raise RuntimeError(f"no usable clingo invocation for {path}: "
                           f"{json.dumps(attempts)}")

    return enumerate_all, env


def main():
    report = {"oracle": None, "environment": None, "rows": [],
              "diagnostic": None, "failures": []}
    try:
        enumerate_all, env = module_oracle()
        report["oracle"] = "python-module"
    except ImportError:
        if shutil.which("clingo") is None:
            print("FATAL: no clingo module and no clingo binary")
            return 2
        enumerate_all, env = cli_oracle()
        report["oracle"] = "cli-binary"
    report["environment"] = env
    print("ORACLE:", env)

    def run_one(src, rules, lp, assert_checks):
        st, su = stable_models(rules), supported_models(rules)
        gap = su - st
        got, quality, detail = enumerate_all(lp)
        row = {"program": src, "lp": lp, "enumeration": quality,
               "clingo": fmt(got), "stable": fmt(st), "supported": fmt(su),
               "supported_but_unstable": fmt(gap)}
        if detail is not None:
            row["cli_attempts"] = detail
        failures = []
        if assert_checks:
            checks = {
                "clingo_eq_stable": got == st,
                "stable_subset_supported": st <= su,
                "no_unstable_in_clingo": (got & gap) == set(),
            }
            row["checks"] = checks
            failures = [f"{src}: {k} failed" for k, ok in checks.items() if not ok]
        return row, failures

    for src, rules, lp in PROGRAMS:
        row, failures = run_one(src, rules, lp, assert_checks=True)
        report["rows"].append(row)
        print(json.dumps(row))
        report["failures"].extend(failures)

    src, rules, lp = DIAGNOSTIC
    row, _ = run_one(src, rules, lp, assert_checks=False)
    st = stable_models(rules)
    row["expected_two_models"] = fmt(st)
    row["completeness_observed"] = set(row["clingo"]) == set(fmt(st))
    report["diagnostic"] = row
    print(json.dumps(row))

    if report["failures"]:
        print("CLINGO CROSS-CHECK FAILED:")
        for f in report["failures"]:
            print(" -", f)
        verdict = "FAILED"
        code = 1
    else:
        print("CLINGO CROSS-CHECK PASSED: independent oracle agrees with the "
              "GL-reduct derivation on all five witness programs; no "
              "supported-but-unstable set is a clingo answer set.")
        verdict = "PASSED"
        code = 0
    report["verdict"] = verdict
    blob = json.dumps(report, indent=2)
    for target in ("crosscheck-report.json", "/out/crosscheck.out"):
        try:
            with open(target, "w") as handle:
                handle.write(blob + "\n")
        except OSError:
            pass
    return code


if __name__ == "__main__":
    sys.exit(main())
