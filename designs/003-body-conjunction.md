# Design 003 — Body conjunction: reading two witnesses with one south face

Status: derived 2026-10-06 (tick 17, SON-4755); NOT yet machine-checked —
the aTAM builds below are the next tick's queue head. This document is
the construction of record plus its falsifier plan.
Date opened: 2026-10-06. Prerequisites: designs/001 (v3 value typing,
rule (a)), designs/002 (3-column geometry, stage order lemma, OR pair
convention, tick 16 emit-time certificate).

## Goal

designs/002's stated honest limit, item 1: every body there has ≤ 1
atom, and "a single south glue cannot read two witnesses." `r :- p, q.`
is the smallest program the 3-column geometry cannot yet lower. The
paper's τ=2 section says the whole compilation rides on the two-input
cooperative AND; a b-literal body needs a b-input AND, and this design
is where that AND is actually built.

## Witness programs and stage tables

| Program | Source | Stable model (least model; positive program) | Discriminates |
| --- | --- | --- | --- |
| P_AND | `p. q. r :- p, q.` | {p,q,r} | the AND chain fires when it should |
| P_AND−q | `p. r :- p, q.` | {p} | slot-A death: q false kills the read |
| P_AND−p | `q. r :- p, q.` | {q} | via death: p false kills the relay |

Stage tables by immediate-consequence iteration:
- P_AND: T⁰ = {p,q}, r enters at T¹. Stages p = q = 1, r = 2. Row
  order p < q < r (order among equal-stage atoms free; convention: the
  reader reads the HIGHEST-row body literal directly, lower literals
  travel by via).
- P_AND−q: T⁰ = {p}; q, r never enter. Rows p < q < r with q, r false
  — order among false atoms free (designs/002 lemma).
- P_AND−p: T⁰ = {q}; p, r false. Correct rows q < p < r; the W1 wrong
  compile below uses q < r < p — also legal on false atoms.

## Construction of record — sequential gating over a 4th column

Columns become **S | D^A | V | L**: spine, first decision slot, the
via column (source stub / witness via / second decision slot / value
conduit, one role per row), lock. All glues strength 1, τ = 2.

Uniform via-column rule: the column-3 tile of row i bonds WEST to row
i's own value glue (exposed east by its col-2 decision), re-exposes
that value EAST (the lock bonds it), and uses NORTH to relay an
upstream witness when one must pass through.

### Build 1 — P_AND, rows p < q < r (all true)

```
row r: [S3: S=SP3,E=go3,N=SP4] [D^A_r: W=go3,S=q-t-done,E=and1_r,N=and1_r-done]
                                     [D^B_r: W=and1_r,S=p-t-done,E=r-t,N=r-t-done] [L3: W=r-t,S=base3,N=cap3]
row q: [S2: S=SP2,E=go2,N=SP3] [D2T: W=go2,S=f-q,E=q-t,N=q-t-done]
                                     [V_p: W=q-t,E=q-t,S=p-t-done,N=p-t-done]      [L2: W=q-t,S=base2,N=base3]
row p: [S1: S=SP1,E=go1,N=SP2] [D1T: W=go1,S=f-p,E=p-t,N=p-t-done]
                                     [V⁰_p: W=p-t,E=p-t,S=vb1,N=p-t-done]          [L1: W=p-t,S=base1,N=base2]
seed (4 wide):  N = SP1 | f-p | vb1 | base1
```

The AND is **sequential gating**: D^A_r attaches at b = 2 only with
(spine `go3` ∧ q's witness `q-t-done`); its east glue `and1_r` exists
only then; D^B_r attaches at b = 2 only with (`and1_r` ∧ p's
via-carried witness `p-t-done`); r's value output `r-t`/`r-t-done`
exists only then; L3 bonds `r-t`. Two cooperative attachments in
series realise the two-input conjunction that a single τ = 2
attachment cannot.

Foundedness is material here, and checkable by BFS re-runs: delete
p's fact → D1T dead → `p-t` absent → V⁰_p dead (b = 1) → V_p dead →
D^B_r dead → r unproducible. Delete q's fact → D2T dead → `q-t-done`
absent → D^A_r dead (and the via, gated by `q-t`, dies with it) →
r unproducible. Cut EITHER witness channel and r's truth loses its
realizing assembly — that is criterion F1 below.

### Build 2 — P_AND−q, rows p < q < r (q, r false; falsity chains)

Row p unchanged. Predicted-false rows follow designs/002 discipline
(lock and falsity chain encode the prediction, v3 rule (a)):

```
row r: S3 | D3F: W=go3,S=q-f-done,E=r-f,N=r-f-done | F_r: W=r-f,E=r-f,S=p-t-done,N=rf-relay | L3: W=r-f
row q: S2 | D2F: W=go2,S=p-t-done,E=q-f,N=q-f-done | V_p: W=q-f,E=q-f,S=p-t-done,N=p-t-done | L2: W=q-f
```

D2F reads the row-below PREDICTED-TRUE done glue (`p-t-done`, col 2);
D3F reads the row-below PREDICTED-value done glue (`q-f-done`). The
via still stands in q's row — gated by `q-f`, reading the stub — but
its north face is inert above a dead slot A (D^B_r needs `and1_r`,
which only a live D^A_r exposes; D^A_r needs `q-t-done`, which a
false q never exposes). Expected terminal: {p}, the linear
certificate, one row per atom.

### Build 3 — W1, the dropped-literal (AND-as-OR) wrong compile

P_AND−p with rows q < r < p (legal: order among false atoms free).
The compiler drops the false literal from the body it emits: r's
decision reads only the directly-below literal q; the via column in
r's row degenerates to a value conduit with a base south face
(`S=vb3`), no witness read:

```
row r: S2' | D^A_r: W=go2,S=q-t-done,E=r-t,N=r-t-done | F⁺: W=r-t,E=r-t,S=vb3 | L2: W=r-t
```

Predicted aTAM: unique terminal **{q,r}** — a NON-model of P_AND−p
(r has no support: p is absent). This is the smallest wrong-AND
compile: conjunction silently degraded to the directly-below read.
Per tick 16 it is a CONSISTENT compile (the miscompiling solver
predicted r true and typed its lock `r-t` accordingly), so the
pre-registered kinetic prediction is: strict {q,r} at high rate,
~0 reassertion of {q} — kinetics neither repairs nor detects it;
the emit-time certificate (aTAM producibility vs clingo enumeration)
is the only net that catches it.

## Tile budget (build 1)

**12 tile types + 4-wide seed**: 3 spine + 2 fact decisions + 1 source
stub + 1 witness via + 2 reader decisions + 3 locks; glue alphabet
~24 names (SP1–4, go1–3, f-p/f-q, value chains p/q/r-t(-done),
and1_r(-done), vb1, base1–3, cap3). designs/002 needed 12+3 for three
atoms with unit bodies: a width-2 body costs **+4 types, +1 column**.

General width-b body at depth d: reader row +(b−1) decision slots,
+(b−1) source stubs, +O((b−1)·d) vias — linear in program size at
fixed max body width, i.e. Θ(Σ_r b_r) tile types. Note the symmetry:
the paper's DSD table prices a b-literal AND at b+1 species; the tile
AND prices at ~(b+1) types plus relay. The species-ceiling argument
against branch (b) (level arguments cost a factor |atoms|) survives:
here |atoms| is paid in DEPTH only. Read time now scales with depth
PLUS total extra body literals (each slot is one more attachment),
composing with tick 10's readwindow arithmetic.

## Candidate compiler invariants (extracted, to be pinned by the builds)

- **(d1) Via discipline.** A north-face witness glue may only be
  exposed by a tile whose south face READS the same-named witness in
  the row below; vias are gated in-row by the row's own predicted
  value glue. No broadcast: a detached or forged via has b ≤ 1.
- **(d2) AND discipline.** Every positive body literal of a
  predicted-true atom appears as a south read in some decision slot
  of its row (direct or via). Dropping one is not a kinetic error, it
  is a wrong program — caught only by the emit-time certificate.

## Falsification criteria (pre-registered)

- **F1 (foundedness of the AND).** Build 1: exhaustive τ = 2 BFS must
  yield exactly one terminal, decoding {p,q,r}; re-run with p's fact
  deleted and with q's fact deleted: r's true tiles producible in 0
  of the resulting assemblies both times.
- **F2 (slot-A death).** Build 2: unique terminal {p}; D^A_r/D^B_r
  producible in 0; `q-t-done` and `and1_r` occur only under a live
  slot A.
- **F3 (certificate arm).** Build 3: unique terminal {q,r}, a
  non-model — the BFS-vs-clingo certificate must fire on it.
- **F4 (kinetics).** v3 protocol grid (Gse = 9, Gmc ∈ {9.5, 11, 13,
  16}, T = 400·e^Gmc, n = 500/point): build 1 decodes {p,q,r} at
  CORRECT-build rates (compare tick 15 anchored curve); build 3 shows
  consistent-wrong behaviour (strict {q,r} ≥ 0.9 at dG ≤ 4, ~0
  reassertion of {q}); build 2's false rows stay at false-chain rates.
  Any reassertion channel above the e^{−2dG} floor refutes the
  sequential-gating claim kinetically.

## What this does not establish

1. Nothing here is machine-checked yet — derivation only. F1–F4 are
   the next tick's queue head, before any kTAM spend.
2. **Negative literals.** `not c` bodies remain unexpressed on the
   tile path (dual rail is the DSD answer; the tile answer is open).
3. **OR ∧ AND.** An atom with k rules where some body is conjunctive
   should compose with designs/002's OR pair (k TRUE variants sharing
   value outputs, conjunctive variants widened per this design), but
   that composition is unbuilt and unproven.
4. **b ≥ 3** extends by more slots but grows lock-column width and
   read time; untested.
5. The stage table and body order are still computed by hand
   (designs/002 item 4); this design is another specification for the
   compiler pass, not the pass itself.
