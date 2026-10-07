"""Collection guard — every test module must be visible to CI discovery.

Defect class (SON-4725, then tick 23's re-review of 424d4dc): a test
file written with module-level test functions (or otherwise outside a
unittest.TestCase) is silently collected as ZERO tests by

    python3 -m unittest discover -s tests -v

so CI stays green while the file's assertions never run. This guard
imports every tests/test_*.py module and fails if any of them would
contribute no tests to discovery.

Lab rule of record (see tests/README.md): a new test file must show
its test names in the verbose output of the exact ci.yml command
before its test count is claimed anywhere.
"""
import glob
import importlib.util
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(path):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return name, mod


def _collected_test_count(mod):
    cases = [obj for obj in vars(mod).values()
             if isinstance(obj, type)
             and issubclass(obj, unittest.TestCase)
             and obj is not unittest.TestCase]
    return sum(1 for case in cases for attr in dir(case)
               if attr.startswith("test_") and callable(getattr(case, attr)))


class TestEveryTestModuleIsCollected(unittest.TestCase):
    def test_no_test_module_is_invisible_to_discovery(self):
        offenders = []
        for path in sorted(glob.glob(os.path.join(HERE, "test_*.py"))):
            name, mod = _load(path)
            if hasattr(mod, "load_tests"):
                continue  # custom loader opts in explicitly
            if _collected_test_count(mod) == 0:
                orphan_fns = sorted(
                    k for k, v in vars(mod).items()
                    if k.startswith("test_") and callable(v))
                why = ("module-level test functions but no unittest.TestCase "
                       "(discovery collects 0 — dead code in CI)"
                       if orphan_fns else
                       "no collectable tests at all (discovery collects 0)")
                offenders.append("%s: %s" % (name, why))
        self.assertEqual(
            offenders, [],
            "test modules invisible to `python3 -m unittest discover`: %s"
            % offenders)


if __name__ == "__main__":
    unittest.main()
