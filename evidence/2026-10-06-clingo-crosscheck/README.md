# Clingo cross-check of the C2 witness programs (2026-10-06)

The supported-vs-stable partition of the five witness programs
(`../2026-10-05-supported-vs-stable/`) was derived by a first-party
checker implementing the Gelfond-Lifschitz reduct and Clark completion
directly. That checker is a re-derivation of record, not an oracle:
the same five programs owed an independent cross-check against a real
stable-model solver, queued since 2026-10-05 as "first cluster tick"
work. This directory is that tick.

Method:

- `p1`–`p5` `.lp` files carry the five programs verbatim.
- `run_crosscheck.py` asks `clingo --models 0` to enumerate all answer
  sets of each program, re-derives stable and supported models from
  the definitions independently of the first-party checker's code, and
  asserts per program:
  1. clingo's answer sets equal the definition-derived stable models;
  2. stable ⊆ supported;
  3. no supported-but-unstable set is a clingo answer set.
- Oracles, in order of preference: the potassco python `clingo` module
  where importable, and the cluster queue's fastlas image as an
  independent environment. (The pod's CLI `clingo` binary is absent —
  the earlier "no clingo on this pod" note measured the binary — but
  the module imports fine, and the queue image has both a patched CLI
  shim and the module.)

Claims this supports: the C2 witness table is not an artifact of the
first-party enumerator. The key anchor is `p1`/`p3`: clingo must return
exactly `{}` for both — a solver that admitted the self-supported `{p}`
or `{p,q}` would refute the stable-vs-supported distinction the whole
C2 design rests on.

## Results (2026-10-06)

PASSED in two independent environments, 15/15 assertions each; the
two-model completeness probe returned both models in both.

| environment | oracle | verdict |
| --- | --- | --- |
| pod (local) | module clingo 5.8.0 | PASSED (`run-local.out`, `crosscheck-report.json`) |
| cluster queue, fastlas image (request `c4499863…`) | module clingo 5.8.2 | PASSED (`queue-run-c4499863-crosscheck.out`, full blob kept) |

Per-program result (identical in both): clingo returns exactly `{}`
for `p1`/`p3`, `{a}` for `p2`/`p4`, `{a,q}` for `p5`; no
supported-but-unstable set is ever an answer set.

Failure kept as receipt: queue job v1 (request `2a0ae177…`) exited 1 —
the image's patched clingo returns status 30 on the flagged
invocation (`--models 0 --verbose=0`) and the v1 runner treated the
rc as fatal. Lesson recorded in the runner: treat parsed solver
output as authoritative, keep rc as diagnostics; the queue wrapper
harvests `/out/*` only, so reports go to files. Both queue request
records are kept here (`queue-request-v1-2a0ae177.json`,
`queue-request-v2-c4499863.json`; image digests inside).

CI: `tests/test_supported_stable_clingo.py` re-runs the equivalence
wherever the clingo module is importable (skips cleanly elsewhere).
