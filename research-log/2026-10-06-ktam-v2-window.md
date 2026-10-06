# 2026-10-06 - The v2.1 window: the unfounded channel is lockable, and what that forces

Tick 4 (SON-4718). Question designs/001 left open: does kTAM on the
v2.1 construction of record confirm the window prediction — `empty`
falls ~e^{−(Gmc−Gse)}, `{a,p}` stays at the transient floor?

**Answer: the structure holds, but the "floor" is not what v1 made it
look like.** In v2.1 the unfounded channel is lockable and sits at the
same near-miss-trap level as the founded channel; the v1 0/4000
separation was construction luck (D2T happened to have no locking
partner at that height), exactly as designs/001 itself warned.

## Setup

`ktam_mc_v2.py` — same kTAM model as v1 (no-mismatch, k_f = 1/s,
attach k_f·e^{−Gmc} at ≥1 matched strength, detach k_f·e^{−b·Gse} with
SP spine bonds counting b = 2), on tiles_v2.py, decoded with the same
map as the machine-checked aTAM claim. Gse = 9; Gmc ∈ {9.5, 11, 13,
16}; n = 500/point; per-run seeds derived from 20261006.

## The grid of record (T_read = 400·e^{Gmc} per point)

| Gmc | dG | {a} | {a,p}+{p} | empty | partial | empty | unfounded |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 9.5 | 0.5 | 283 | 111 | 106 | 0 | .212 | .222 |
| 11 | 2.0 | 383 | 29 | 87 | 1 | .174 | .058 |
| 13 | 4.0 | 476 | 0 | 22 | 2 | .044 | .000 |
| 16 | 7.0 | 434 | 0 | 0 | 66 | .000 | .000 |

## Three things the numbers say

1. **Both wrong-value channels are the same phenomenon.** The
   unfounded track (.222 → .058 → 0) shadows the single-shot trap
   formula 1/(1+e^{dG}) (.38 → .12 → .018) with a consistent ~½
   factor (the {a,p} decode also needs D1T correct), and the founded
   track shadows it more loosely. The aTAM-level "D2T never
   producible" result transfers to kTAM only as: every wrong value
   costs ≥1 sub-τ attachment; after that, a value-blind lock makes it
   terminal with probability 1/(1+e^{dG}).
2. **The empty channel over-stays the single-shot model at small
   dG.** .174 observed at dG=2 vs ~.11 modeled. Mechanism hypothesis:
   site-reopening retries — each D1F detach re-opens the site and
   re-runs the race. Needs the exact first-passage computation, not a
   hand wave (next tick).
3. **Read time is an instrument parameter, not a constant.** Grid 1
   (fixed T = 400·e^{Gse}) read the dG=7 point before growth:
   500/500 partial. With T = 400·e^{Gmc} it grows and reads clean
   (66/500 partial = 13% — 400 attempts/site under-covers the slowest
   sites; fine for rate estimates, refine for yield claims).

## What it forces: v3 — evidence-checking locks

Rule: **a lock must check the value it locks, not merely stitch the
row shut.** v3 value-types the decision tiles' exposed glues
(D1T→rd1t, D1F→rd1f, D2F→rd2f, D2T→rd2t) and each lock's value-side
glue matches only the correct value's glue. Locking a wrong value
then requires two coincident near-misses (wrong tile at b=1 AND lock
against a mismatched value glue at b=1) → error ~e^{−2·dG}: at dG=2
that predicts unfounded ≈ 10⁻³-scale instead of 6%. This is
proofreading specialised to the decision column, and it is the first
entry in what should become the compiler's design-rule catalogue.
Falsifier: the v3 grid showing either channel above its e^{−2·dG}
curve.

## Honest status

Unreviewed notebook output; mechanically reproducible from committed
seeds. C2 not claimed at kTAM level — it now has a measured window
and a rate-statement form. The clingo cross-check of the five witness
programs (independent oracle) remains queued for the first cluster
tick; the first-party supported-vs-stable checker was regenerated
this tick and passes.
