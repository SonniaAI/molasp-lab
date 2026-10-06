# WRONG_CUT lock-on-false — the F2 boundary closes (tick 16)

**Date:** 2026-10-06 · **Evidence:** `evidence/2026-10-06-cut-lockvalue/`
(`tiles_cutlock.py`, `atam_check_cutlock.py` + `atam_cutlock.out`,
`ktam_mc_cutlock.py`, `run.out`) · **Status:** measured this tick,
unreviewed promotion per lab convention.

## Question

Tick 15's F2 boundary, verbatim: the WRONG_CUT build self-corrected to
the stable model only because its lock stayed keyed to the pre-cut
(TRUE) prediction — "a compiler that re-predicted q=false after
cutting would emit lock-on-rq-f and would presumably capture {a,p}
instead. The cut's kinetic fate is decided by the lock's value typing,
not by the cut. That variant is the natural next build."

This tick is that build. Same wrong cut (q:-p severed, u-cut inert
south), but the compiler re-runs its fixpoint on the severed program:
q loses its only support, the prediction flips to FALSE, and the
emission follows the 2cycle falsity-chain discipline — D3F.S =
rp-t-done (row-below's predicted-true done glue), L3.W = rq-f (the
predicted value's output). Everything else byte-identical to WRONG_CUT.

## aTAM (machine-checked, `atam_cutlock.out`)

20 producible assemblies, 1 terminal, decode **{a,p}** — the compile's
own prediction. D3T producible in 0; and unlike WRONG_CUT, **no tile
bonds rq-t from the lock side** (`rq_t_bonded_by_any_w_face: []`) —
the cooperative capture channel that let tick 15's true tile ride a
b=1 transient into a b=2 terminal is structurally absent. clingo
(tick 7 lesson, module on pod): unique stable model of P is
{a,p,q}; {a,p} under assumptions (a,p,¬q) is UNSAT — the terminal the
build locks in is not a model of P at all.

## kTAM (v3 protocol, n=500/point, seeds in header)

| dG | strict ap | strict apq | partial | loose apq |
|---|---|---|---|---|
| 0.5 | **500/500** | 0 | 0 | 0 |
| 2 | **499/500** | 0 | 1 | 0 |
| 4 | **494/500** | 0 | 6 | 0 |
| 7 | **440/500** | 0 | 60 | 0 |

Totals: **1933/2000 ap, 0/2000 apq — every pre-registered prediction
holds.** P1 ✓ (ap ≥ 0.988 at dG ≤ 4). P2 ✓, stronger than registered:
zero reassertion of the true stable model at ANY point, including
dG=0.5 where the transient coincidence channel was allowed 3/500. P4 ✓
(loose apq 0 everywhere; D3F absorbs the site at b=2 and never
detaches). P3 ✓ and it is the sharpest row: the ap curve
(1.000/0.998/0.988/0.880) tracks anchored CORRECT's apq curve
(1.000/0.998/0.990/0.866) within ~1.02x — the false-typed lock and
falsity chain cost nothing in growth. At dG=7 this build completes at
0.880 where WRONG_CUT's self-correction had collapsed to 0.006: the
anchored chain attaches directly at b=2, while WRONG_CUT's true tile
needs the cooperative b=1→b=2 capture that slow kinetics kills.

## Finding

**Self-correction is lock-typed, not cut-typed — and a consistent
compile is kinetically stable even when it is wrong.** Tick 15's
benign self-correction was an artifact of an *inconsistent* compile
(dead true tile, live true-typed lock). The moment the compiler makes
its error consistently — re-predict, re-type the lock, re-chain the
falsity glues — the substrate executes that error faithfully, at full
completion rates, with zero reassertion of the true model across 2000
trajectories. Kinetics neither repairs nor detects a wrong compile;
it amplifies whichever prediction the lock chain encodes.

Compiler consequence (designs/002 updated): soundness must be
certified at emit time. The aTAM producibility check against the
solver's stable-model enumeration IS the certificate; no kinetic
safety net exists downstream. This closes the F2 boundary and
completes the wrong-compile taxonomy:

| error family | aTAM | kTAM | mechanism |
|---|---|---|---|
| wrong VALUE (v3 falsifier) | dead | dead (0/2000, tick 5) | un-lockable: b=1 everywhere |
| wrong CUT, true-typed lock (inconsistent) | dead | captured → stable model (tick 15) | lock bonds true output; cooperative capture |
| wrong CUT, false-typed lock (consistent) | terminal {a,p} | **terminal {a,p}, 1933/2000** | no capture partner; anchored false chain |
| wrong ROW ORDER (geometry) | dead | dead (0/2000, tick 15) | lock south faces mismatched |

## Limits

Unreviewed promotion; single n=500/point grid; no mismatch errors
modelled (protocol constant since the v2.1 grid); the dG=0.5 transient
channel registered under P2 never fired, so no measurement of its
rate exists here; the aTAM certificate claim (emit-time checking) is
stated for this family only — body conjunction (designs/003) and
wider OR fan-in remain untested territory.
