# Design 003 — Body conjunction: reading two witnesses with one south face

Status: **F1–F3 machine-checked 2026-10-06 (tick 18, SON-4758)** —
exhaustive τ = 2 BFS, evidence/2026-10-06-body-conjunction-builds/,
tests pinned in tests/test_tiles_and.py. Two build-table errata (E1,
E2) found by that check and corrected; see Errata below. F4 (kTAM
grid) remains queued — it needs the cluster queue.
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
and1_r(-done), vb1, base1–3, cap3).

Cost deltas, comparator stated explicitly (*post-review correction
2026-10-06, QA run e1477162: the original sentence here claimed
"+4 types, +1 column" with no baseline that reconstructs from the
record — designs/002 budgets 12 types + 3 seed and this build's own
inventory sums to 12*):

- **vs the all-true unit-body compile of the same 3-atom program
  (9 types: 3 spine + 2 fact decisions + 1 reader decision +
  3 locks): +3 tile types, +1 column, +1 seed tile.** These are the
  three tile classes conjunction genuinely adds — source stub,
  witness via, second reader slot — and this is the baseline the
  ~(b+1) symmetry below reads against (b = 2 → b+1 = 3).
- **vs designs/002's full budget (12 types + 3 seed tiles): +0 tile
  types, +1 column, +1 seed tile** — the new classes are absorbed
  within the same 12-type count.

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
  *Tick 18: 0 violations across all 7 builds — holds.*
- **(d2) AND discipline.** Every positive body literal of a
  predicted-true atom appears as a south read in some decision slot
  of its row (direct or via). Dropping one is not a kinetic error, it
  is a wrong program — caught only by the emit-time certificate.
  *Tick 18: holds on the correct build; catches both W1 variants
  including the one that stalls past the semantic certificate —
  promoted from candidate to required emit-time check.*

## Measured outcomes (tick 18, exhaustive τ = 2 BFS)

| Arm | Measured | Verdict |
| --- | --- | --- |
| F1 build 1 | 35 assemblies, unique terminal {p,q,r}, 3/3 locked | PASS |
| F1 p-cut | terminal {}; r-t, and1_r producible in 0 | PASS (stronger: over-collapse, finding 3) |
| F1 q-cut | unique terminal {p}; r-t, and1_r producible in 0 | PASS |
| F2 | unique terminal {p}, 3/3 locked; q-t/r-t/and1_r never producible | PASS |
| F3 | unique terminal {q,r} vs clingo {q}: certificate fires; d2 flags missing p-read | PASS, both arms |
| d1 via discipline | 0 violations, all 7 builds | holds |
| d2 AND discipline | holds on build 1; fires on both W1 variants | promoted to required emit-time check |
| E1 raw build 1 | stalls at {p} | erratum, demolished |
| E2 raw build 3 | stalls at {q} — masquerades as correct | erratum, demolished |

## Errata (found by the tick-18 machine check, corrected in
evidence/2026-10-06-body-conjunction-builds/tiles_and.py)

- **E0 (clarification, not corrected):** the construction text says
  "all glues strength 1", but the spine exemption is inherited from
  designs/002 — SP1/SP2/SP3 pairs bond at strength 2. With a
  strength-1 spine nothing attaches in row 1 at τ = 2 at all.
- **E1:** `D2T.S = f-q` matches nothing below site (1,2) — a fact
  above row 1 must chain on the row-below done glue
  (`p-t-done`), exactly as this design's own Build-2 false tiles
  already do. As written, build 1 stalls at {p}. Corrected to
  `p-t-done`; the as-written variant is pinned as a demolition.
- **E2:** `F⁺.S = vb3` is a dead face. As written, the W1 wrong
  compile stalls at {q} — the stable model — i.e. it escapes the
  semantic certificate by stalling and masquerading as correct.
  Corrected to `q-t-done` (the conduit bonds the channel below it;
  the dropped-literal wrongness is unchanged). Only the static d2
  check catches the as-written variant.
- **Lock faces completed:** the build-2/build-3 tables truncated
  lock south/north faces; they follow the base-chain discipline
  (L2.S = base2, L3.S = base3, N = base3/cap3) as in builds above.

Two design consequences recorded from the corrected builds: the tile
path cannot distinguish `q.` from `q :- p` when q's row sits directly
above p's row (fact-vs-rule is a compile-time distinction only), and
fact deletion is not modular — a seed fact cut re-compiles every row
above it (p-cut terminal is the empty decode, not {q}).

## Falsification criteria (pre-registered)

**F1–F4 measured — see Measured outcomes above and the F4 note below.**

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

### F4 measured (tick 19, evidence/2026-10-06-and-ktam-grid/)

Cluster queue job `10c9aa52…` (paperclip-test, 1 CPU, ~45 s wall):
6000 trajectories, protocol of record, BASE_SEED 20261019, receipt
and raw blob in the evidence directory. Strict completion (expected
decode fraction, per 500):

| dG | build1 pqr | build2 p | build3 qr | tick-15 CORRECT | build3/build1 |
| --- | --- | --- | --- | --- | --- |
| 0.5 | 0.540 | 0.524 | 0.560 | 1.000 | 1.037 |
| 2 | 0.790 | 0.748 | 0.810 | 0.998 | 1.025 |
| 4 | 0.984 | 0.972 | 0.976 | 0.990 | 0.992 |
| 7 | 0.870 | 0.854 | 0.844 | 0.866 | 0.970 |

Verdicts against the pre-registration (the pre-registered text
above is unchanged — this is the record of what it predicted vs
what happened):

- **K1 PASS**: build1 stays within the ~2× band of tick-15 CORRECT
  at every point (min ratio 0.540 at dG=0.5 — the band is nearly
  exhausted there) and matches it from dG=4 up.
- **K2 FAIL as pre-registered**: strict qr < 0.9 at dG=0.5 (0.560)
  and dG=2 (0.810). The failure mode is completion rate, not
  consistency: the 4-column geometry completes at roughly half the
  3-column rate at fast churn (the via column costs ~0.46
  completion at dG=0.5 — a new measurable) and does not cross 0.9
  before dG=4. The 0.9 threshold was calibrated on the wrong
  geometry.
- **K3 FAIL as pre-registered**: same story (0.524/0.748 at
  dG=0.5/2).
- **K4 FIRES as operationalized**: partial-strict loose counts
  239/2000 (build1) and 136/2000 (build3). The detector is refuted
  as a measurement, not the claim: in a positive program whose rows
  can always complete, an unfinished assembly reads as a subset of
  the true model by construction — growth-incompletion is
  indistinguishable from reassertion at a fixed read time. No
  completion-independent reassertion channel exists in this
  geometry; a kinetic reassertion claim needs a structural-death
  build (a tile type removed), which is a different experiment.

What stands (pinned in CI, tests/test_ktam_and_grid.py):

- **The consistent-wrong claim, restated correctly**: build3's
  strict-qr completion is statistically indistinguishable from
  build1's strict-pqr completion at every point (ratios
  0.970–1.037) — the substrate executes the wrong compile at the
  correct compile's own rate. Tick 16's prediction carries into the
  AND geometry.
- **Slot-A death is nearly free kinetically**: build2 tracks build1
  at 0.947–0.988 across the grid (floor at dG=2) — false rows cost
  at most ~5% completion, and nothing at the operating points.
- **The depth ceiling is unchanged**: all three builds sit on the
  tick-15 dG=7 partial wall (0.844–0.870 vs 0.866).

## What this does not establish

1. F1–F3 are machine-checked (tick 18); F4 is measured (tick 19,
   kTAM grid on the cluster queue): thresholds K2/K3 failed as
   pre-registered (miscalibrated on 3-column completions), the
   consistent-wrong-rate claim is confirmed, and the reassertion
   detector is refuted as a measurement (growth-incompletion
   conflation).
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
