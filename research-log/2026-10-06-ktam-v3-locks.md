# 2026-10-06 - v3 evidence-checking locks: wrong values become un-lockable

Tick 5 (SON-4721). Question tick 4 left: designs/001 specified v3 —
locks that check the value they lock — predicting both kTAM error
channels fall like e^{−2·dG}. Falsifier: either channel above its
curve. Does the design survive its own test?

**Answer: the falsifier is never triggered — and the built design is
stronger than its own prediction.** With fully value-typed lock
interfaces, a wrong decision tile's value glues bond nothing at any
strength, so no sequence of attachments, however coincident, can lock
a wrong value into a terminal assembly. The window grid measures
0/2000 wrong decodes where v2.1 measured 355/2000.

## What was actually built (one spec subtlety)

The four E-glue typings in designs/001 (D1T→rd1t, D1F→rd1f, D2F→rd2f,
D2T→rd2t) are **not sufficient**: D2F's south input `row1done` bonds
D1F's north glue exactly as happily as D1T's — a vertical value-blind
lock. A transient D1F held until D2F's W+S corner lands would still
lock with one coincidence and the founded channel would keep v2.1's
~e^{−dG} behaviour while the unfounded channel improved. So v3 types
the row-1→row-2 channel too: D1T N=rd1t-done, D1F N=rd1f-done, D2F
S=rd1t-done. Correct growth is unchanged (same strength-1+strength-1
corners, only glue names differ); the tile count is unchanged (8+3) —
the cost moves entirely into glue-alphabet size, which is where DNA
word-design cost actually lives.

aTAM τ=2 re-checked on the v3 glue table (`atam_check_v3.py`):
10 producible assemblies, 1 terminal, decoding {a}; D1F and D2T
producible in 0 of 10; all three lock-vs-wrong-value glue pairs
strength 0. (Honesty note: the first version of that check asserted
total bond strength 0 in wrong contexts and failed — on the structural
seed/spine bond, not on a value bond. The checker caught its own
mis-specified test; the test was fixed, the tile set was not.)

## The grid (identical protocol to the v2.1 window: Gse = 9,
T_read = 400·e^{Gmc}, n = 500/point, seeds from 20261007)

| Gmc | dG | {a} | {a,p}+{p} | empty | partial | e^{−dG} | e^{−2·dG} |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 9.5 | 0.5 | 500 | 0 | 0 | 0 | .607 | .368 |
| 11 | 2.0 | 498 | 0 | 0 | 2 | .135 | .018 |
| 13 | 4.0 | 498 | 0 | 0 | 2 | .0183 | .00034 |
| 16 | 7.0 | 436 | 0 | 0 | 64 | .0009 | 8e-7 |

v2.1 under the same protocol: `empty` .212/.174/.044/.000, unfounded
.222/.058/.000/.000 — pooled 355/2000. v3: **0/2000**, pooled 95% CI
upper bound 1.5×10⁻³. Both channels sit below the e^{−2·dG} curve at
every point, including dG=0.5 where v2.1 trapped 21–22%.

## What the numbers say — and what they don't

1. **The mechanism is structural elimination, not suppression.** In
   v3, D1F's non-spine glues (u-a, rd1f, rd1f-done) have no partners
   in the entire glue table, so max b(D1F) = 1 in every possible
   assembly; same for D2T. A b=1 tile is always transient (detaches
   at e^{−Gse}), so a wrong value can appear only as a pre-settlement
   transient — and the read protocol, which waits 400 on-rate
   timescales per site, essentially never catches one (0/2000).
2. **The e^{−2·dG} prediction described a different, weaker variant.**
   Two coincident near-misses matter when a lock *can* still bond a
   wrong value but only weakly (proofreading). v3-full removes the
   bond entirely, so the design's curve becomes a conservative upper
   bound rather than a scaling law. The design-rule catalogue gets
   two entries: (a) locks bind value-bearing glues → wrong values
   un-lockable (this grid); (b) where a value-agnostic lock is
   unavoidable, require two independent bonds → ~e^{−2·dG}
   (specified, still unmeasured — a v3-proofreading variant).
3. **No growth penalty measured.** Partial fractions 0/2/2/64 vs v2.1's
   0/1/2/66 — statistically indistinguishable at n=500, as expected:
   correct corners are identical up to glue renaming.
4. **Honest limits.** Single construction, no-mismatch kTAM, n=500/
   point; 0/2000 bounds the pooled rate below 1.5×10⁻³, it is not
   zero; the aTAM and glue-table claims are exhaustive and
   machine-checked, the kTAM claim is simulation-bounded. The
   first-passage analysis of the v2.1 empty channel (retry tail)
   remains open and is now the natural next theory step, together
   with designs/002 (does every program admit a strict level mapping
   the geometry can carry?) and the clingo cross-check still queued
   for the first cluster tick.

Status: unreviewed notebook output, mechanically reproducible from
committed seeds (`evidence/2026-10-06-c2-ktam-v3-locks/`; output hashes
recorded on the run card). Enforced in CI by
`tests/test_tiles_v3.py`: the aTAM invariants, the zero-strength
value-side pairs, and un-lockability in the full correct context.
