"""C2 witness programs vs an independent clingo oracle (2026-10-06).

Wherever the potassco clingo module is importable, asserts for all five
witness programs of evidence/2026-10-05-supported-vs-stable/:

  1. clingo's answer sets == the GL-reduct derivation (runner functions,
     loaded from the evidence directory of record);
  2. stable models ⊆ supported models;
  3. no supported-but-unstable set is a clingo answer set.

Stdlib-only unittest port (2026-10-06, tick 7 review fix): the repo's
CI command is `python3 -m unittest discover -s tests -v` with no pytest
installed, so this file must not import pytest. Skips cleanly where the
clingo module is absent via `unittest.skipUnless`. The evidence run of
record is evidence/2026-10-06-clingo-crosscheck/ (pod clingo 5.8.0 and
queue fastlas image clingo 5.8.2 both PASSED).
"""
import importlib.util
import pathlib
import unittest

try:
    import clingo
    HAVE_CLINGO = True
except ImportError:
    HAVE_CLINGO = False

RUNNER_PATH = (pathlib.Path(__file__).resolve().parents[1]
               / "evidence" / "2026-10-06-clingo-crosscheck" / "run_crosscheck.py")
_spec = importlib.util.spec_from_file_location("molasp_crosscheck_runner", RUNNER_PATH)
runner = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(runner)

LP_DIR = RUNNER_PATH.parent


def enumerate_all(path):
    ctl = clingo.Control(["0"])  # enumerate all answer sets
    ctl.load(str(path))
    ctl.ground([("base", [])])
    found = []

    def on_model(model):
        found.append(frozenset(s.name for s in model.symbols(atoms=True)))

    ctl.solve(on_model=on_model)
    return set(found)


@unittest.skipUnless(HAVE_CLINGO, "clingo module not importable")
class WitnessCrossCheck(unittest.TestCase):
    def test_clingo_matches_derivation(self):
        for src, rules, lp in runner.PROGRAMS:
            with self.subTest(lp=lp):
                got = enumerate_all(LP_DIR / lp)
                stable = runner.stable_models(rules)
                supported = runner.supported_models(rules)
                self.assertEqual(got, stable, f"{lp}: clingo {got} != derived {stable}")
                self.assertTrue(stable <= supported)
                self.assertEqual(got & (supported - stable), set())

    def test_tight_control_has_no_gap(self):
        by_src = {src: rules for src, rules, _ in runner.PROGRAMS}
        rules = by_src["a. q :- a."]
        self.assertEqual(runner.supported_models(rules), runner.stable_models(rules))

    def test_enumeration_completeness_probe(self):
        _, rules, lp = runner.DIAGNOSTIC
        self.assertEqual(enumerate_all(LP_DIR / lp), runner.stable_models(rules))


if __name__ == "__main__":
    unittest.main()
