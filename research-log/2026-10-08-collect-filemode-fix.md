# 2026-10-08 — collect.py file-mode fixed: usage ≠ malformed (tick 64)

Card: SON-4856 (tick 64). Instrument fix closing the open quirk
from tick 63's collection
(`evidence/2026-10-07-dg2-window-l3vac/`, research-log
2026-10-08-dg2win-collection.md §6).

## Symptom (tick 63)

`python3 collect.py run.out` (the documented file mode) exited 3 on
the very input dash mode accepted — and 3 is documented as
"malformed run output", so file-mode exits were untrustworthy.
Tick 63's suspicion: "the exit-3 path is not the parser; suspect
main()'s file-write branch."

## Root cause (measured this tick)

Neither the parser nor the file-write branch. `main()` gated on
`len(argv) != 3`, so the documented **two-argument** form fell into
the usage branch, printed the docstring, and returned 3 — the same
code reserved for malformed run output. The documented default
destination (`run.out` → `collection.md`) was simply never
implemented; exit-code reuse made a usage mistake masquerade as
malformed data, which is what misdirected the tick-63 suspicion.

## Fix

`main()` now accepts 2 or 3 argv entries (2 → dst defaults to
`collection.md`); usage errors (0, 1, or 4+ arguments) print the
docstring to stderr and return **64**, distinct from 3. Docstring
exit-code table updated and the fix recorded in the file header.

## Verification (real data, not fixtures)

- `python3 collect.py run.out` on the committed tick-63 `run.out`:
  exit 0, wrote `collection.md` **byte-identical** to the fragment
  dash mode emitted at tick 63 (`diff` clean) — parser, verdict
  recomputation, and rendering all unchanged.
- No args: exit 64. Four args: exit 64.
- Regression pins added in `tests/test_collect_dg2win_l3vac.py`
  (three tests): two-arg file mode writes `collection.md` (chdir'd
  tempdir; asserts the fragment header), three-arg explicit
  destination still works, usage errors return 64.

## Lesson (durable)

Never reuse an exit code across failure classes. The tick-63
misdiagnosis ("suspect the file-write branch") was reasonable
*given the documented code table* — the table itself was the bug.
When an instrument's documented behavior and its observed behavior
disagree, print the docstring/usage branch first (here it was
literally on stderr of the failing run).
