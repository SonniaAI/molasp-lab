# Tick 157 — the 3-body prediction is confirmed: fiber = k exactly, never 2^k

**Date:** 2026-10-22 · **Card:** SON-5152 (tick 157) · **Head after this tick:** see receipt commit

## What was predicted, what was tested

Tick 156 derived `assemblies(n) = |ideals| + (k-1)·|corner ideals|` with
`k` = live body count of the or-head, and recorded a falsifiable
prediction: a 3-body or-head censuses at **fiber 3 on its corner
ideals, never 2³**. This tick built the families and ran the censuses.

### Fragment boundary first (probed, not assumed)

Compiler v0.2's terminal-or geometry admits at most **two distinct
body shapes**: a unit body on the adjacent-below derived row, and one
AND body on (adjacent-below derived, i-2 passthrough). Every other
placement is refused by the emitter's geometry guards (unit on the
row-1 via dies once the V relay is suspended; fact-hi AND bodies need
their lo at row 1; non-adjacent chain reads are refused; direct-below
fact readers are unwired). The k > 2 families that compile are
**duplicate bodies** — semantically idempotent in ASP, geometrically
real: the emitter mints a fresh conduit glue per rule body
(`unit1_r`, `unit2_r`, …), so each duplicate carries its own
body-identity handshake. Two 3-body families and one 4-body family:

- `PC11-3U`: `r :- q2, s. / r :- q2. / r :- q2.` (duplicate unit)
- `PC11-3A`: `r :- q2, s. / r :- q2, s. / r :- q2.` (duplicate AND)
- `PC11-4`:  both duplicates together.

## Result (all heights 5..12, live, element-wise)

| n | k=2 (tick 156) | k=3 measured | k=3 law | k=4 measured | k=4 law |
|---|---|---|---|---|---|
| 5 | 147 | 168 | 168 | 189 | 189 |
| 6 | 238 | 266 | 266 | 294 | 294 |
| 7 | 366 | 402 | 402 | 438 | 438 |
| 8 | 540 | 585 | 585 | 630 | 630 |
| 9 | 770 | 825 | 825 | 880 | 880 |
| 10 | 1067 | 1133 | 1133 | 1199 | 1199 |
| 11 | 1443 | 1521 | 1521 | 1599 | 1599 |
| 12 | 1911 | 2002 | 2002 | 2093 | 2093 |

- **Presence unchanged**: the full four-column ideal set, `C(n+4,4)`,
  at every height — k does not touch the poset level.
- **Contended sets are still exactly the corner ideals** (those
  containing site (1,n)), `C(n+2,2)` at every height.
- **Fiber exactly k**: multiplicity histogram `{1: rest, 3: C(n+2,2)}`
  (k=3) and `{1: rest, 4: C(n+2,2)}` (k=4) at every height — **never
  8, never 16**, including the 13 both-site corner ideals at n=12
  (max fiber there = 3 resp. 4). The prediction is confirmed and the
  law's k-slot now has three measured values.
- **Body-identity pairing, element-wise**: in every contended fiber,
  the conduit at (1,n) and the reader at (2,n) — when that site is
  present in the ideal — carry the *same* body glue (conduit east ==
  reader west). 78 of the 91 corner ideals at n=12 contain (1,n) but
  not (2,n): there the conduit attaches west+south alone and the
  fiber is the bare conduit choice; the 13 both-site ideals are where
  the coupling rule binds the pair into one choice.
- **Duplicate-shape independence**: PC11-3U and PC11-3A give identical
  presence/assembly/multiplicity censuses at n=12 — which body shape
  is duplicated is immaterial.
- **Static lemmas re-verified on the k=3 inventory**: each body glue
  (`and1_r`, `unit1_r`, `unit2_r`) occurs exactly twice in the whole
  inventory (conduit east + own reader west); the admissible (1,n)
  tiles against the forced context are exactly `[Cr, Cr2, DAr]`; each
  body's reader is the *unique* admissible (2,n) tile given its own
  west glue, every cross-body pairing fails TAU, and growth order
  still closes the (3,n) escape. The census adds no new physics — it
  agrees with the static rule everywhere.

## Honest limits

- Duplicate bodies are the only compilable k > 2 route in this
  fragment; a *distinct*-body 3-or (e.g. three different conjuncts)
  needs geometry v0.2 refuses by design. The measured claim is "fiber
  = number of rule bodies of the or-head, each live under the least
  model", at k ∈ {2,3,4}.
- Census range capped by the 7-letter decorative alphabet
  (`program_for(13) == program_for(12)` for the k=3 family too).
- Docs + static analysis + census only; zero queue spend; nothing
  here is a validated result until independently reviewed.

## Receipt

`evidence/2026-10-22-pc11-three-body/three_body.json`
sha256 `10ea6dd06be6fdbef0bda4e809f28c8965120e5cd8306e1f4a0877e795183052`
Pins: `tests/test_pc11_three_body.py` (live re-derivation of every
scalar above, static lemma pins, receipt hash + byte stability).

## Open next

- Two-or-pair family (two independent or-heads in one program): does
  the fiber multiply across *independent* or-heads, i.e. is
  `assemblies = |ideals| + (k₁-1)|A₁| + (k₂-1)|A₂| + (k₁-1)(k₂-1)|A₁∩A₂|`
  with independent corner classes? That would pin when multiplicity
  is additive vs multiplicative — the natural completion of the
  k-series.
