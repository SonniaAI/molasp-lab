# Body conjunction F1–F3 machine-checked — the AND is real, and it caught two bugs in its own spec (tick 18)

**Date:** 2026-10-06 · **Evidence:** `evidence/2026-10-06-body-conjunction-builds/` (`tiles_and.py`, `atam_check_and.py` + `atam_and.out`), `tests/test_tiles_and.py` (12 tests; suite 106/106 green) · **Status:** measured this tick, unreviewed promotion per lab convention.

## Question

designs/003 (tick 17) derived the width-2 body construction
`r :- p, q.` — sequential gating over a via column — and
pre-registered four falsifiers, explicitly derivation-only:
"F1–F4 are the next tick's queue head, before any kTAM spend."
This tick ran the aTAM arm: exhaustive τ = 2 BFS over all
assemblies reachable from the 4-wide seed, for the corrected
builds, the two fact-cut re-runs, and — because the machine check
is exactly the tool that earns its keep — the builds **exactly as
the tick-17 tables stand**.

## Results

| Arm | Outcome | Verdict |
| --- | --- | --- |
| F1 build 1 | 35 reachable assemblies, unique terminal decodes {p,q,r}, 3/3 rows locked; `r-t` producible | PASS |
| F1 p-cut | terminal decode {}; `r-t` and `and1_r` producible in 0 assemblies | PASS (stronger than spec — see finding 3) |
| F1 q-cut | unique terminal {p}; `r-t`/`and1_r` producible in 0 | PASS, exactly the design narrative |
| F2 build 2 | unique terminal {p}, 3/3 rows locked; `q-t`, `r-t`, `and1_r` never producible | PASS |
| F3 build 3 | unique terminal {q,r} — clingo says the stable model of P_AND−p is {q} — certificate fires; d2 static flags the missing p-read | PASS, both arms |
| E1 build 1 as written | stalls at {p} | design-table bug, demolished |
| E2 build 3 as written | stalls at {q} — which IS the stable model | design-table bug, demolished (see finding 2) |
| d1 via discipline | 0 violations across all 7 builds | invariant holds |
| d2 AND discipline | holds on build 1; fires on both W1 variants | promoted to compiler invariant |

clingo 5.8.0 anchors all three programs: P_AND → {p,q,r},
P_AND−q → {p}, P_AND−p → {q}.

## The two errata (machine-checked, not hand-waved)

**E1 — `D2T.S = f-q` matches nothing below it.** A fact above
row 1 cannot read its own `f-` glue off the seed; the row-2 fact
must chain on the row-below done glue (`p-t-done`), exactly as the
design's own Build-2 false tiles already do. As written, build 1
terminates at {p} and fails its own F1 prediction. Corrected in
`tiles_and.py`; the as-written variant is pinned in the tests as a
demolition.

**E2 — `F⁺.S = vb3` is a dead face.** Nothing below site (2,2)
exposes `vb3`; the W1 wrong compile as written never locks r, and
its terminal decode is {q} — the *correct* stable model. The wrong
compile escapes the semantic certificate **by stalling and
masquerading as correct**. With the corrected south face
(`q-t-done`: the conduit bonds the channel below it; the
dropped-literal wrongness is unchanged — no tile in r's row reads
p), the build realizes the pre-registered F3 arm: {q,r}, a
non-model, certificate fires.

## Three findings worth keeping

1. **d2 is load-bearing at compile time, not a nicety.** The BFS-
   vs-clingo certificate is blind to wrong compiles that stall
   before expressing their wrongness (E2). The static AND-
   discipline check — every positive body literal of a predicted-
   true atom must appear as a south read in its row — catches both
   W1 variants regardless of kinetics. This upgrades d2 from
   "candidate invariant" to required emit-time check, alongside
   the producibility certificate that catches the ones that *do*
   assemble wrongly.
2. **The tile path cannot distinguish `q.` from `q :- p`** when
   q's row sits directly above p's row: both read `p-t-done` on
   the south face. Fact-vs-rule is a compile-time distinction
   only. Harmless here (both true), but it bounds what the
   substrate can express about *why* an atom is true — same family
   as the foundedness story, one level down.
3. **Fact deletion is not modular.** Cutting p's seed fact kills
   q's fact tile too (chain discipline), so the p-cut re-run
   terminates at the empty decode, not {q}. The pre-registered
   criterion (r's true tiles producible in 0) still passes, and
   passes *more* strongly. But a compiler user expecting
   incremental re-compilation semantics from a seed edit will not
   get them; a fact cut re-compiles the world above it.

## What this does NOT establish

- **F4 (kinetics) is untouched** — the kTAM grid (Gse = 9, Gmc ∈
  {9.5, 11, 13, 16}, T = 400·e^Gmc, n = 500/point) is now the
  queue head, and it needs the cluster queue, not this laptop.
- The three open items from designs/003 stand: negative literals,
  OR∧AND composition, b ≥ 3.
- aTAM producibility is the idealised model; kTAM error behaviour
  is precisely what F4 exists to measure.
- Unreviewed promotion per lab convention; no C-claim advanced;
  C2 evidence base unchanged (this strengthens the construction
  C2 depends on, but adds no C2 evidence).

## Next queued

F4 on the cluster queue (one job, four grid points × three
builds); then OR∧AND composition as designs/003 item 3.
