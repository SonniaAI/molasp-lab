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

## 10.6 Landing record (tick 62, 2026-10-08, SON-4852)

Option A landed as the single closure predicate in `compiler.py`
(`glue_strength` backed by `_SPINE_GLUE_RE`, strict `SP[1-9][0-9]*`
fullmatch); `parity.py` re-exports it and its SP1–4 table is deleted;
`offchannel.py` delegates by default (explicit per-call `strength=`
tables still override) and `DEFAULT_STRENGTH` (SP1–3) is deleted;
the vestigial `compiler.py` STRENGTH is gone. No other semantic edits
in the landing commit. Suite: `Ran 425 tests in 1.180s / OK
(skipped=1)` — 421 + the four §10.4-1 unification pins in
`tests/test_spine_closure_unification.py`.

Measured outcomes (§10.4, verbatim):

1. **Unification ✓** — `parity.glue_strength is compiler.glue_strength`;
   SP4/SP5/SP6/SP40 = 2 on BOTH paths; value glues 1; mismatched and
   blank 0; explicit-table override honored.
2. **PC12-DOC (n=5) ✓ (primary shape)** — (5 rows, 20 tiles, **126**
   assemblies, 1 terminal), full_locks **TRUE**, decode == the FULL
   least model **{p,q,q2,r,s}**. Row 5 attached; no second hidden cap.
3. **PR13-dead ✓** — rows locked **4 → 6**, assemblies **70 → 210**,
   dead readers `and1_r`/`unit1_q2` **still BFS-absent** (falsifier
   did not fire). Terminal decode {p,q,s} unchanged; d4 severity
   still "error" (reported, not gated).
4. **Byte-stability ✓ (with one predicted healing, corrected
   in place)** — lock-misplacement regenerates BYTE-IDENTICAL
   (`b7a5c70f…cd32`). The census-generality receipt is NOT
   byte-identical — exactly ONE line changes (the DEEP_FACTS arm,
   `p. q. s. r :- s, p.`), and the field diff is exactly 9 leaves,
   every one an `S3+S4` lock-stack channel count 1→2: the SP4↔SP4
   spine self-bond on the OFFCHANNEL path, previously under-priced
   by its SP1–3 table — i.e. the row-4 divergence healing §10.4-1
   pre-registered, now recorded in the receipt itself. The committed
   receipt is updated to the regenerated content. The parity-corpus
   receipt differs only in `seconds_*`/wall fields (timing-masked
   identical; the corpus is n≤4 — PC1–PC9 + the PR refusals).
   PC12-N4 stays (4,16,70,1) with full locks.
5. **PC11 ✓** — (5 rows, 22 tiles, 147 assemblies, **2 terminals**,
   both decoding the full model {p,q,q2,r,s}), full locks; the
   pin/comment in `test_chain_refusal_corpus.py` carries the measured
   shape.

**Falsifier: NOT triggered.** The only 1→2 strengthening anywhere
in the receipts is the SPINE pair SP4↔SP4 on the offchannel path
(the S3+S4 healing above — parity already priced it at 2; this is
unification, not a new strengthening); no NON-spine pair changed,
and no dead-reader resurrection (BFS-absent). The bare class rule stands; no name-shape fallback
needed — the predicate already matches strictly `SP<digits>`, the
emitter's own shape, so nothing else can ride the closure silently.

**Record-keeping slips in THIS note, corrected in place (caught by
the pins, not silently rewritten):**

- §10.1 quotes the PC12-DOC program as `r :- q2, z.` — the pinned
  fixture (tick 55/60, `tests/test_and_over_derived_baseline.py`)
  is `r :- q2, q.`; the quote is PR14's z-channel transcription
  bleed. The §10.1 measured row (5 rows, 20 tiles) matches the
  fixture, not the quote.
- §10.4-2 predicted "decode == least model {p,q,s,q2} (r stays
  dead: z absent)" — that prediction follows the slipped quote.
  Measured: decode == the FULL model {p,q,q2,r,s} (r is TRUE and now
  reachable at row 5). The primary prediction (full_locks TRUE,
  unique terminal) holds.
- §10.4-5's "exhaustive" flip list omitted the PR13-dead
  measured-shape pins (`(6,26,70,1)`→`(6,26,210,1)`, full_locks
  `assertFalse`→`assertTrue`, `locked == 4`→`6`), which §10.4-3 had
  pre-registered as predictions; they flipped exactly as predicted.

The cap is closed: n>4 builds are no longer spine-capped. Next
frontier: n=6+ build survey and offchannel-path kinetic reports
beyond row 4 (the healed row-4 divergence deserves its own receipt).

**Receipt-compare methodology correction (same tick):** the first
in-tick compare said "census-generality byte-identical" — that was
a measurement error: the generator rewrites its own `.out`, so a
disk-vs-stdout compare is self-referential. `git status` vs HEAD
caught it; every future receipt compare must run against HEAD
(`git diff HEAD -- <receipt>`), never the working-tree file.

## §10.7 Addendum (tick 64, SON-4856): closure measured through n=9

§10.4's "no second hidden cap" was measured at n=5 only. The tick-64
survey (receipt `evidence/2026-10-08-n6-build-survey/probe.out`;
record `research-log/2026-10-08-n6-build-survey.md`) extends the
PC12-DOC family with decorative facts to n=6..9 under pre-registered
predictions P1–P6: full locks, unique terminal, and full-model decode
at every n; no refusal as the unit-via distance grows to 7 (p row 1 →
q2 row n−1). Assemblies fit C(n+4, 4) exactly at every measured point
n=4..9 — an empirical closed form, unproven from the enumerator
(open; tick-65 candidate). Scope: one family, one geometry; this
widens the measured support of §10.4, it is not a theorem. Pins:
`tests/test_n6_build_survey.py`.
