# Design 012 — the northward truth-OR relay (intermediate OR-heads)

**Date:** 2026-10-22 · **Card:** SON-5152 (tick 158) · **Status:** pinned by
`tests/test_pc11_two_or.py` (live census) + refusal pins + PC11 byte-stability pins

## 0. What was refused, and why this design exists

Compiler v0.2 admits multi-body heads (name contention) only at the
terminal row — an OR at an intermediate derived row raised
`UnsupportedGeometry` ("needs a northward truth-OR relay"), and a
second intermediate derived row raised the designs/008 §6 chain-depth
refusal. Tick 157 closed the *terminal* k-body question (fiber = k
exactly); the open two-or-pair question — do two independent or-heads
compose multiplicatively or additively — is unreachable without an
intermediate OR-head, so the fragment boundary has to move first, by
design, not by guess.

## 1. Shape admitted (and nothing more)

A **relayed OR-head** is an intermediate derived row `a` (row `i < n`)
all of whose bodies are **unit bodies on the adjacent-below derived
row** (the duplicate-unit shape of tick 157's PC11-3U, now one row up):

```
q2 :- p.            row i-1  (single-body intermediate, unchanged)
r :- q2. r :- q2.   row i    (relayed OR-head — NEW)
w :- r.  w :- r.    row n    (terminal OR-head, unchanged)
```

Refused loudly (unchanged or newly): intermediate AND bodies; mixed
AND/unit intermediates; non-adjacent or row-1-via unit bodies at an
intermediate multi-body row; an AND consumer of a relayed head (the
designs/009 §9.2 passthrough re-type would collide with the relay —
§4); a second relayed head in one chain (unexamined stacking);
single-body chain depth > 2 (designs/008 §6, unchanged).

## 2. The relay itself

For a relayed head `a` at row `i` the emitter keeps the per-body
machinery byte-identical to the terminal case — each body `j` mints its
own conduit glue `unit{j}_a` (E face of conduit `C{a}{j}` at `(1,i)`,
W face of reader `U{a}{j}` at `(2,i)`) — and re-types only the
**northward** faces to the *value* glue:

* conduit `C{a}{j}` N face: `{a}-t-done` (was `unit{j}_a-done`),
* `d_north[i] = {a}-t-done` (was `unit1_a-done`),
* `v_north[i] = {a}-t-done` (unchanged; the stage-1 chain link).

Everything above row `i` bonds south against `{a}-t-done` only: the
next row's conduits read `d_north[i]`, its unit readers read the chain
link. Both are **bit-blind**: they match whichever body's conduit /
reader sits at row `i`, so growth north of a relayed head does not see
the body-identity bit at all.

## 3. Soundness (glue arithmetic, the stage-2/3 pattern)

The relay is value-typed, so it is sound by the same arithmetic that
pins dead readers (designs/008 stages 2–4):

* `{a}-t-done` is exposed on a north face at row `i` **iff** a live
  body's conduit realizes there. A live body's conduit needs W `go{i}`
  (spine, strength 1) + S `below_d` (strength 1) = TAU 2; a dead
  body's conduit reads its own `unit{j}_a-done` nowhere (d3 guarantees
  the head is true, hence ≥ 1 live body; least-model support kills
  every body of a false head).
* The bit (WHICH live body) stays a free east–west handshake at row
  `i` exactly as at the terminal row (tick 156's L-east/L-west
  arithmetic is row-generic): cross-body pairings fail TAU, so the
  reader is a function of the conduit choice, one assembly per body.
* Rows above bond to the value glue, not to `unit{j}_a`, so no north
  face can privilege one body — this is precisely what the old
  `d_north[i] = unit1_a-done` would have broken (row `i+1`'s conduit
  would bond south only against body 1's conduit, killing every other
  body's continuation and with it the name contention itself).

## 4. Boundary interactions

* **designs/009 §9.2 passthrough:** the consumer-aware lookahead adds
  row `i` to `passthrough_rows` only when the row above carries an AND
  body with `b_hi = a`. That re-type writes `below_d` onto the conduit
  N face and would clobber the relay; a relayed head with an AND
  consumer is therefore REFUSED (a real fragment boundary, recorded).
* **designs/008 §6 chain depth:** a relayed head may sit above
  single-body intermediate rows (its own south faces are the unchanged
  stage-1 chain reads); single-body chain depth > 2 stays refused.
* **Terminal regression:** programs with no intermediate multi-body
  head take none of the new branches — every pre-existing build is
  byte-identical (pinned).

## 5. What the design buys (measured in this tick's census)

The first two-or-pair family censuses at fiber 4 — multiplicative —
on the both-site ideals: `research-log/2026-10-22-tick158-two-or-relay.md`,
receipt `evidence/2026-10-22-pc11-two-or/two_or.json`.
