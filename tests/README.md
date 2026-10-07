# Lab test rules

The CI suite runs exactly:

    python3 -m unittest discover -s tests -v

## Rule of record: test files must prove themselves in verbose output

A new test file must show its test names in the verbose output of the
exact ci.yml command above **before** its test count is claimed on a
card, in a report, or anywhere else.

Why: `unittest` discovery collects `unittest.TestCase` classes (or a
module `load_tests` hook) — **not** module-level `test_*` functions.
A file written with bare functions contributes zero tests while CI
stays green, so its assertions never run and any numbers it "pins" can
drift silently. This bit us twice (SON-4725; tick 23 re-review of
424d4dc, where receipt pins were dead code at a claimed 169 vs. an
actual 163).

`tests/test_collection_guard.py` enforces the mechanical part: it
fails the suite if any `tests/test_*.py` module would contribute zero
tests to discovery. When you add a test file:

1. Write tests as `class TestSomething(unittest.TestCase)` methods
   (or provide `load_tests` if you need a custom loader).
2. Run the exact CI command and grep the verbose output for your new
   test names.
3. Claim the count that the verbose `Ran N tests` line reports.
