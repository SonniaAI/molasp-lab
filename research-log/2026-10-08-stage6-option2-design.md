# Stage-6 Option II design: the second N-face channel, specified

Date: 2026-10-08, started ~03:05Z · SON-4848 · run 76b034cc ·
design-only tick (compiler pristine at a4a53f5).

## What this tick did

Implements §8's consequence: designs/009 §9 now specifies the Option
II channel concretely, grounded line-by-line in the live compiler
(`molasp/compiler.py` at a4a53f5) instead of the one-line sketch §3
carried. No compiler change, no measurement beyond re-reading the
tick-55 baseline pins; every count in §9 stays `predicted`.

## The design in one paragraph

The second N-face channel is NOT a new glue name or a new column —
it is a consumer-aware north-face layout on the intermediate
derived row plus a reader-order swap in the AND terminal. When the
row above reads the derived atom as an AND hi literal (compile-time
lookahead; single derived row, single consumer, both pinned by
designs/008 §6), the derived row's conduit `C{hi}` re-types its N
face from the conduit glue `unit1_{hi}-done` to the **passthrough of
the row-below D-column value** (`below_d` = `{lo}-t-done` for a true
lo), and `d_north` carries that passthrough; the row-below value is
thereby reachable one row up at x=1. The AND terminal then emits
lo-reader-first: `DA'` at x=1 south-reads the passthrough (v0.1's
own `D-tile S = below_d` positional arithmetic, unchanged), `DB'` at
x=2 south-reads the UNCHANGED stage-1 chain link `U{hi}.N` =
`{hi}-t-done` (§2's gate-B re-typing, landed in the column where the
link actually lives). Unit-consumer shapes (PC9/PC10) keep the
stage-1 layout byte-identically — `C{hi}.N` stays the conduit glue,
`U{hi}.N` stays the chain link — so the load-bearing unit readers
are untouched. The false-link guard is inherited, not added: the
channel re-exposes a value-typed done glue, so a false lo yields
`{lo}-f-done` against the true-head reader's `{lo}-t-done` read —
bond 0, dead by value typing, the stage-1 argument verbatim.

Two consequences now on the record before any code moves:

1. **Gate A is a union for BOTH head polarities** (§9.3): row-1 via
   OR positional i−2, and the check must move out of the
   predicted-true-only branch — tick-55 measured PR13-dead/PR14
   compiling with all gates bypassed (the gate code never runs for
   false heads). PR14's unplaced `z` lo must refuse loudly on the
   false-head side too; PR13-dead (positional lo `q` at i−2) stays
   an accepted dead-cascade pin.
2. **Derived-hi AND readers are position-incompatible with fact-hi
   AND readers** (hi read moves x=1 → x=2). No corpus build reads a
   derived hi today (gate B refused them all), so no pin can break —
   but the landing tick must name the case split in the compiler,
   not just emit different tiles.

## Correction made while writing

The §9.4 first draft carried the original §4 PR13 program
(`q2 :- s`) — wrong in-place since tick-55 (`s` is a fact, q2 comes
out true). Fixed to the measured baseline shape
`p. s. q. q2 :- z. r :- q2, q.`, least model {p,q,s}
(tests/test_and_over_derived_baseline.py, PR13_DEAD). Caught by
re-reading the baseline pins before committing — the measure-then-
claim habit applied to prose.

## Landing order for the next tick (pre-registered)

1. Probe-first: census + corpus receipts re-run and byte-compared
   BEFORE any gate edit (tick-56 lesson).
2. Union gate A (both polarities) + the §9.2 layout + reader swap.
3. Pins in §9.4's order: receipts byte-identical; PC9/PC10
   byte-stability; PC12 model/locks/dead-glue absence; PR13-dead
   reader absence BFS-proved; PR14 loud refusal naming both
   placements.
4. Honest boundaries carried: false-head lock completion at n=5
   open (tick-55: 4/6, d4 collision — accepted behavior, unchanged
   by this design); OR-at-intermediate and depth > 2 stay refused.

## Waiter status

Tick-47 request 9e79de43…e145 (dg2win-l3vac-v1) STILL QUEUED at the
~03:02Z check (~10 h, resource/owner limit; other owners hold
capacity). No resubmission — the request is durable and idempotent;
the monitor on SON-4846 (nextCheckAt 03:05Z, timeoutAt 04:15Z) is
the standing collector path. Collection remains the next tick's
first duty.

Suite verbatim on the exact CI command (`python3 -m unittest
discover -s tests -v`): `Ran 421 tests` / `OK (skipped=1)` —
docs-only tick, count unchanged from a4a53f5.
