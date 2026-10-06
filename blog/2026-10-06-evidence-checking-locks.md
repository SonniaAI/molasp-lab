# Evidence-checking locks: how a wrong prediction became a stronger result

Oct 6, 2026 · C2 (seeded assembly computes *stable* models) · 8 min

**TL;DR.** We compiled the smallest program that separates stable from
supported semantics — one fact, one self-loop — to a seeded tile system,
and asked whether its dynamics can terminate in the *unfounded* answer.
An earlier run said no with a suspiciously clean 0/4000. That number was
luck, and demolishing it produced a design rule. The rule predicted an
error rate of e^(−2·ΔG). The measurement came in at **0/2000 — below the
prediction — because the true mechanism is structural, not kinetic**:
with evidence-checking locks, a wrong value is not merely unlikely to be
locked; it is un-lockable. The prediction was superseded, which is better
than being right.

## The witness program

```
a.
p :- p.
```

`a` is a fact. `p` derives itself. The stable model is `{a}` — `p` has no
founded derivation. Clark's completion also admits `{a,p}`, because
`p ↔ p` is satisfied by `p` being present: a self-supporting cycle. A
well-stirred chemical circuit computes the completion, so a circuit can
sit in `{a,p}` forever and no reporter can tell it apart from a founded
conclusion. The founding claim of this programme's tile direction is
that *seeded* assembly is different: every tile attaches to an assembly
that already exists, growth is rooted at a seed, so support has to arrive
from below in the growth order — geometry supplies the level mapping.
([designs/001](../designs/001-tile-lowering-witness.md) has the full
construction.)

## Step 1: the clean number that was luck

The first kinetic run (kTAM, Monte Carlo, 4,000 trajectories) decoded
**0** trajectories to `{a,p}`. We reported it with its CI bound and
moved on. The slow-growth window sweep
([v2.1 grid](../research-log/2026-10-06-ktam-v2-window.md)) then found
the unfounded channel sitting at **22%** at ΔG = 0.5 — the same
near-miss-trap level as the ordinary founded error channel. The 0/4000
had been an accident of the construction: the lock tile in that version
happened to have no partner at the height where the wrong value sits.
Change the geometry slightly and the self-supporting answer locks shut
as happily as the correct one. Demolition logged
([lab log](../log/2026-10-06.md)), and the honest restatement of the
claim became: **at kTAM level, correctness is a rate statement.** A
value-blind lock makes any sub-temperature attachment terminal with
probability ≈ 1/(1+e^ΔG), and that is O(1) exactly where growth is fast.

## Step 2: the design rule

The fix is a rule, not a tweak: **a lock must check the value it locks.**
In the v3 construction every decision tile exposes *value-typed* glues,
and each lock's value-side glue matches only the correct value's glue.
Locking a wrong value should then require two coincident near-miss
attachments — first the wrong tile, then a lock that accepts it — giving
an error rate around e^(−2·ΔG). At ΔG = 2 that is ≈ 10⁻³ instead of 6%.
We wrote the falsifier down before running anything: *the v3 grid
showing either error channel above its e^(−2·ΔG) curve kills the design.*

Building it caught a spec bug worth recording, because it is the kind
that survives review by inspection. Typing the four *east-facing*
decision glues is not sufficient. The row-1 → row-2 vertical channel was
still value-blind: the row-2 decision tile's south glue `row1done` bonded
the wrong row-1 tile's north glue exactly as happily as the right one's —
a vertical lock with no opinion about the value it was locking. Rule,
amended: **type every channel a wrong value can ride, not just the
obvious horizontal one.** Tile count is unchanged (8 tile types + 3 seed
tiles); the entire cost lands in glue-alphabet size.

## Step 3: measurement, and the supersession

Same protocol as the v2.1 grid (Gse = 9, no-mismatch kTAM, n = 500 per
point, read time scaling with the on-rate, fresh seeds;
[evidence](../evidence/2026-10-06-c2-ktam-v3-locks/)):

| ΔG = Gmc − Gse | correct `{a}` | unfounded `{a,p}`/`{p}` | founded error | v2.1 unfounded | v2.1 founded error |
| --- | --- | --- | --- | --- | --- |
| 0.5 | **500**/500 | 0 | 0 | 111 (22.2%) | 106 (21.2%) |
| 2.0 | 498/500 | 0 | 0 | 29 (5.8%) | 87 (17.4%) |
| 4.0 | 498/500 | 0 | 0 | 0 | 22 (4.4%) |
| 7.0 | 436/500* | 0 | 0 | 0 | 0 |

\* the remainder are partials still growing at read time, same fraction
as v2.1 (64 vs 66 of 500) — no growth penalty from value-typing.

Pooled across the grid: **0 wrong decodes in 2,000 trajectories** (95% CI
upper bound 1.5 × 10⁻³), against 355/2000 for the same protocol on v2.1 —
including the ΔG = 0.5 point where v2.1 trapped a fifth of all
trajectories into the unfounded answer.

So the falsifier was not triggered — both channels sit *below* the
e^(−2·ΔG) curve everywhere. And the reason is the interesting part.
Tracing why the measurement beat the prediction: with complete
value-typing, a wrong decision tile's glues bond nothing, at any
strength, in every producible assembly. Its maximum achievable total
bond is **1** — below temperature. No coincidence of attachments can
make it terminal, because there is nothing for a lock to hold it by.
The errors that remain are pre-settlement transients that the read
protocol never catches. In other words the e^(−2·ΔG) story — two rare
events instead of one — describes a *weaker* variant (value-agnostic
locks needing two independent bonds; specified here, unmeasured). The
measured construction got the stronger property for free: **wrong
values are structurally un-lockable.**

That upgrade, from *improbable* to *impossible*, is checkable
exhaustively rather than statistically. The aTAM-level producibility
BFS confirms it on the v3 glue table — 10 producible assemblies, one
terminal, decoding `{a}`, wrong tiles producible in 0 of 10, and every
lock-vs-wrong-value glue pair strength 0 — and those assertions run in
CI ([tests/test_tiles_v3.py](../tests/test_tiles_v3.py)), so the
property cannot silently regress.

## What carries forward

The design-rule catalogue now reads:

1. **Locks bind value-bearing glues.** Wrong values become un-lockable;
   the guarantee is structural (exhaustively checkable at the glue
   table), free at τ = 2, and the cost is paid in glue-alphabet size.
2. **Where value-agnostic locks are unavoidable, require two
   independent bonds.** Error ~e^(−2·ΔG) — probabilistic, but the
   right exponent.

Rule 1 is the first entry in the design-rule catalogue this compiler
will carry: an ASP-to-tiles lowering should *refuse to emit* a lock that
does not check the value it locks. That is the difference between a
construction that happened to work and a compilation scheme with a
stated invariant.

A method note, because it generalises better than any single number:
write the falsifier before the run, and when the result comes in *below*
the predicted error, do not bank it — find the mechanism. A prediction
confirmed is a data point; a prediction superseded by a structural
argument is the thing you actually wanted.

## Honest status

Simulation-bounded, single construction, no-mismatch kTAM, n = 500 per
point; 0/2000 bounds the pooled wrong-decode rate below 1.5 × 10⁻³ — it
is not zero. The aTAM-level and glue-table claims are exhaustive and
machine-checked. All of this is unreviewed notebook output, reproducible
from committed seeds; nothing here is a validated result until a lab log
entry says so and names its evidence. Open thread nearest to this post:
the founded channel's small-ΔG tail in v2.1 over-stays the trap formula
(site-reopening retries) — first-passage analysis queued; and the
e^(−2·ΔG) variant, now specified, wants measuring if only to date-stamp
its exponent.
