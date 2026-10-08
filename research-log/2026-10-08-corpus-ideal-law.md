# 2026-10-08 — The corpus-wide law: presence == well-founded (tick 66)

Card: SON-4861 (hourly loop, tick 66). Receipts verbatim:
`evidence/2026-10-08-corpus-ideal-law/probe.out` (v1, the
falsification) and `probe2.out` (v2, the law), both JSON-lines,
run at HEAD 1915589. Predictions frozen in each probe docstring
before its run; v1's P2/P3 were falsified by v1 itself — kept,
not discarded.

## 1. Question

Tick 65 derived assemblies == ideals of the 4-column poset
(C(n+4,4)) for the decorative family and left corpus-wide
extension as the named next candidate. Does the poset argument
extend to every compiling corpus program?

## 2. What v1 falsified (recorded, instructive)

The naive statement "presence sets == ideals of the DAG derived
from local strengths" is FALSE for every corpus program. Local
or-support is the norm: e.g. PC12-N4 has 13 of 16 sites with ≥2
minimal support sets — the north-bond cooperative alternatives
(a D-column site held by below+north instead of below+west).
Tick 65's §2 table survives because the extra options are pruned
by *reachability*, not by strength — exactly the parenthetical in
its column-2 row, now measured corpus-wide. The law must live at
the level where that pruning is native.

## 3. The corrected law (v2, pre-registered before its run)

**BFS presence sets == well-founded sets of the face-table attach
grammar, both directions, for every compiling corpus program.**
Grammar: per (site, name), all minimal non-seed support sets over
all four directions (contended neighbours pooled); well-founded =
least family containing ∅ and closed under "add a site when some
name there has some minimal support set inside". New module
`molasp/poset.py` makes the derivation mechanical — no hand-read
face tables.

Measured: **14/14 programs hold** (PC1..PC9, PC10, PC11, PC12-N4,
PC12-DOC, PR13-dead). [Corrected in place tick 76, §7 below: the
sentence this replaces — "PR9 also compiles but has no pinned
program text in molasp/tests, the one compiling shape not probed"
— was wrong. PR9's registry text is byte-identical to the PC11
pin, so the 14/14 already covered it.]

## 4. Findings beyond the prediction

1. **The binomial box law extends**: PC12-N4 70 = C(8,4),
   PC12-DOC 126 = C(9,4), PR13-dead 210 = C(10,4) (tick-62
   anchor reproduced; dead tiles AD6r/UD5q2 BFS-absent; all 24
   box sites occupied somewhere) — and **PC11's presence level is
   the n=5 box: 126 = C(9,4)**. The tick-62 "147" is
   name-contention above the poset level: 147 name-labelled
   assemblies over 126 presence sets.
2. **Contention is name-level only.** PC2/PC6/PC7/PC8/PC11 carry
   contended sites (PC7's terminal row is three-way by design);
   at presence level every one of them is still well-founded-clean
   (assemblies − presence: 10/15/30/15/21). All contended sites
   are contended-SHARED (identical minimal-support collections
   across names) — v2's P2' predicted PC7 contended-SPLIT and was
   falsified: three-way contention shares supports too.
3. **"and" sites are always exactly the S-column rows** (3 per
   program beyond n=4 shapes): the spine self-bond is the only
   strength-2-alone channel; every other site needs cooperation.
4. Dead tiles are BFS-absent in four programs (PC3: DAr/DBr, PC4:
   AD3r/UD3r, PC10: UD3q/UD4r, PR13-dead: AD6r/UD5q2) — the
   dead-variant emission discipline, now recorded per program.

## 5. Evidence

- `evidence/2026-10-08-corpus-ideal-law/probe.py` + `probe.out`
  (v1: local or-support counts, D-field failures — the
  falsification receipt), `probe2.py` + `probe2.out` (v2: L1/L2a/
  L2b per program, class histograms, box checks).
- Pins: `tests/test_corpus_ideal_law.py` — the law re-derived
  LIVE for all 14 programs (suite cost ~1 s); EMPIRICAL constants
  labeled as such (assembly/presence counts, class histograms,
  contention deltas, PR13-dead dead-tile set and full-box ideal).
- Suite verbatim: `Ran 437 tests in 2.561s / OK (skipped=1)`.

## 6. Scope

One compiler (v0.1 + spine closure), one strength predicate, the
14 compiling shapes with pinned texts. The law is a statement
about THIS attach grammar; a compiler or strength-table change
that breaks it fails the pins loudly. Not claimed: refusal
shapes, kTAM kinetics (the poset is the aTAM-level structure the
kTAM work layers on top of). ["PR9" removed from the not-claimed
list tick 76, §7 — it is PC11, inside the law.]

Nothing here is a validated result until independently reviewed.

## 7. Correction (tick 76, run 813f39ca): the PR9 gap never existed

The closing sentence of §3 and the "Not claimed: PR9" of §6 were
both wrong. PR9's refusal-registry text at 4b71903 —
`p. q. s. q2 :- p. r :- q2, s. r :- q2.` — is BYTE-IDENTICAL to
the PC11 pin in tests/test_corpus_ideal_law.py EXTRAS. Name
lineage: the shape was designed as designs/009's PC11
(via-generalization candidate), refused at tick 48 and registered
as PR9 ("AND lo-literal at row 3, not the row-1 via"), made to
compile by stage 6 (ff60932: "PR9-out (compiles now)"), then
pinned and probed under its candidate name PC11 by this very
note's tick-66 probe. Two names, one program, one ghost hole.

Consequence: the 14/14 measurement covered every compiling shape
with a known text on the day it was measured; there was no 15th
program to probe and no follow-up pin needed. The identity is now
enforced by PR9_REGISTRY_TEXT + PR9HoleOfOneClosed in the test
file. Verification method: extract the registry entry with
`git show 4b71903:molasp/parity.py`, decode the string literal,
compare with python `==` (True; no whitespace or rule-order
difference). The blog post and guide 04 carry dated errata.
