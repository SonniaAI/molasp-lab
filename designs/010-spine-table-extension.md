# 010 — Spine table extension: closing the n>4 spine cap

Stage-7 candidate, **design-only** (tick 61, 2026-10-08, SON-4852).
Compiler pristine at `ff60932`. This note fulfils the designs/009 §9.4
promise that spine-table extension is "a separate, explicitly designed
step, not slipped in". Nothing here is landed; every prediction below
is pre-registered for a later landing tick and must be measured, not
assumed.

## 10.1 Problem — measured baseline (all numbers at `ff60932`)

Every build with more than four spine rows is capped at a 4-row prefix:

| probe | measured shape | pin |
|---|---|---|
| PC12-DOC (n=5), `p. s. q. q2 :- p. r :- q2, z.` | (5 rows, 20 tiles, 70 assemblies, 1 terminal); full_locks FALSE; L5 unreachable; terminal decodes the 4-row prefix {p,q,q2,s} | `tests/test_and_over_derived_baseline.py::test_pc12_doc_compiles_but_spine_capped_at_row_5` (tick 60) |
| PR13-dead (n=5), `p. s. q. q2 :- z. r :- q2, q.` | 26 tiles, 70 assemblies, unique terminal, **4 of 6 rows locked**; dead readers `and1_r`/`unit1_q2` BFS-proved absent | tick 55, re-read §9.4 |
| PC11 (n=5), `p. q. s. q2 :- p. r :- q2, s. r :- q2.` | compiles on the positional i-2 arm; "spine-capped at row 5 like every n>4 build" | `tests/test_chain_refusal_corpus.py::test_pc11_compiles_on_positional_i2_arm` |

Cost of the cap: the compiler cannot scale past four derived rows, and
the cap already ate one recorded prediction — §9.4 demolished the n=5
"full locks" row of the §9.3 table on an inventory artifact (the
strength table), not on a gate property.

## 10.2 Root cause — an enumeration where the invariant is a class

Three facts, all verified in-source this tick:

1. **The emitter is generic.** `molasp/compiler.py:244` mints spine
   tiles for any row index: `emit(f"S{i}", {"S": f"SP{i}", "E":
   f"go{i}", "N": f"SP{i + 1}"}, i)`. `SPn` names exist for all n.
2. **The blessing is enumerated, and inconsistently — three tables.**
   The live enumerator table `molasp/parity.py:52` blesses SP1–SP4 at
   strength 2. A second LIVE table, `molasp/offchannel.py:95`
   (`DEFAULT_STRENGTH`, consumed by `offchannel.glue_strength` at
   line 161 — the d4/kinetic-report path), blesses only SP1–SP3. A
   third, `molasp/compiler.py:66`, blesses SP1–SP3 and has no
   in-module consumer (grep-verified this tick; vestigial). The n=4
   landing (PC12-N4, `ff60932`) rode on parity's SP4 entry — the
   offchannel path stopped one row earlier, so the divergence is
   already live at row 4, not hypothetical.
3. **The fallback does the damage.** `glue_strength` (parity.py:56)
   returns 1 for any unmatched same-name pair, so SP5↔SP5 bonds at
   1 < TAU 2: row 5 can never attach, and every n>4 build decodes a
   4-row prefix. (§9.4's measured demolition.)

The enumeration is an accident of the tested range, not a physical
claim. The invariant is stated in-source (offchannel.py:91–94,
"designs/002 v2.0 row-typed-spine exemption: spine self-bonds are
strength 2 …; all other matched glues are cooperative strength 1") and
the glue-class census (tick 35, `tests/test_glue_class.py`) proved the
boundary: the strength-2 spine self-relay is a **class property**
(designs/002) and C1 found **no shared structural glue at all** —
nothing outside the spine consumes an SPn name. The honest boundary is
"the spine class is exempt", not "the first three-or-four members are
exempt, differently per module".

## 10.3 Options

**A (chosen) — class closure rule.** Replace all three enumerated
tables with one shared predicate in `compiler.py` (parity and
offchannel consume it; the vestigial copy is deleted): a
same-name `SPi↔SPi` pair bonds at strength 2 for all i ≥ 1; every
other pair keeps the existing fallback. Justification: §10.2 — the
invariant being encoded is the class, and the class has no off-channel
users (C1). The rule also forcibly unifies the divergent tables, so
the compiler/parity split cannot re-diverge.

*Risk and its guard:* any accidental SP-name reuse outside the spine
would silently jump 1→2. C1 says no such reuse exists today; the
landing tick must **re-prove it with the census receipts** (falsifier
below), not assume it.

**B (rejected) — one shared spine species.** Reuse a single glue name
for every spine bond. Destroys row addressability: row i+1 could bond
any exposed spine face, contradicting the anchored-cycle order
invariant that designs/002's order-falsifier work exists to enforce.
Falsified by construction; not measured.

**C (rejected) — document the cap at n≤4.** Contradicts the compiler's
purpose (arbitrary programs ⇒ arbitrary row counts) and leaves §9.4's
demolition unrepaired. The cap has already manufactured one false
negative prediction; keeping it keeps the failure mode.

**Standing strength arguments the rule must NOT touch (scan):**

- PR13-dead's dead-reader proof (tick-51 argument, re-derived at x=1 in
  §9.4): `DA'.W = vj` unique to the body, `DA'.S ≤ 1` even on a true
  lo → max 1 < TAU 2. That arithmetic lives on **value glues**
  (t-done/f-done classes at strength 1), not SPn — unaffected.
- The value-glue strength-1 channel, cage/vacancy KTAM receipts, and
  the contention sweeps consume no SP>4 pairs.
- PC9/PC10 unit-consumer layouts are n≤4 builds: byte-stability is
  required at landing (pin below).

## 10.4 Pre-registered predictions (landing tick measures; no fitting)

1. **Unification:** exactly one strength predicate (compiler.py);
   parity and offchannel consume it, the divergent copies are gone; a
   new pin asserts `SP5↔SP5 = SP6↔SP6 = 2` **on both the parity and
   offchannel paths** (healing the row-4 divergence too) and that
   value glues still bond at 1, so the cap has no silent regression
   path.
2. **PC12-DOC (n=5):** row-5 spine attachment becomes reachable; the
   §9.3 table's original row ("unique terminal decode, full locks" at
   n=5) is re-opened. Primary prediction: full_locks TRUE, unique
   terminal, decode == least model {p,q,s,q2} (r stays dead: `z`
   absent, dead-cascade shape). If row 5 still cannot attach — a
   second, hidden cap — that is a demolition to record in-place, not a
   reason to widen the rule.
3. **PR13-dead (n=5):** rows locked 4 → 6 (both remaining rows are
   spine rows); assemblies grow from the prefix-capped 70; **dead
   readers `and1_r`/`unit1_q2` must remain BFS-absent.** If spine
   extension resurrects a dead reader, option A is falsified in its
   bare form (see falsifier).
4. **Byte-stability:** PC9/PC10 layouts byte-identical; both census
   receipts regenerate byte-identical (timing-masked, tick-59 rule);
   parity corpus unchanged at n≤4 (9 compiling + 12 refusals).
5. **Deliberate pin flips (exhaustive list):**
   `test_pc12_doc_compiles_but_spine_capped_at_row_5` (full_locks
   assertFalse → assertTrue; expected tuple and decode updated to the
   measured shape) and the PC11 spine-cap comment/pin in
   `test_chain_refusal_corpus.py`. Any OTHER receipt diff = landing
   bug, revert.

## 10.5 Landing order (probe-first, mirrors §9.5 discipline)

1. **Probe tick** (evidence/docs only): freeze baseline receipts on the
   pristine tree; record PC12-DOC / PR13-dead / PC11 n=5 numbers
   verbatim; re-confirm by grep that `compiler.py:66` STRENGTH stays
   unused in-module (checked once this tick) so deleting it is a
   no-op by measurement.
2. **Implement:** the single closure predicate; no other semantic
   edits in the same commit.
3. **Receipts:** regenerate all three pinned receipts; census
   byte-identical (timing-masked); corpus diff empty or exactly the
   §10.4-5 flips.
4. **Measure §10.4** and record outcomes verbatim; a miss is a
   demolition recorded in-place (§9.4 precedent), never patched
   around.
5. Suite green (`Ran 421 tests … OK` at `ff60932`; count may grow with
   the new unification pin). Blog post only if full locks land at n=5 —
   that is the first genuine scalability milestone; a design note is
   not a milestone.

**Falsifier for option A:** the census diff shows any non-spine pair
strengthened 1→2, or a dead reader resurfaces at n=5 → the bare class
rule is falsified; fall back to a name-shape-guarded rule (literal
`SP<n>` pattern), re-run the census, and re-review. Do not ship a
silent strengthening to buy row 5.
