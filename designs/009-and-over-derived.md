# 009 — AND bodies over derived literals: the PC11 via-generalization

Status: **DESIGN ONLY** — nothing here is compiled, emitted, or
BFS-verified. No measurements are claimed. This is the designs/008
residue named at tick 51 ("PC11 via-generalization design"); every
count marked `predicted` is hand arithmetic from committed receipts
(PC2, PC4, PC9, PC10), not output.

## 1. What blocks PC11 today, exactly

PC11 `p. q. s. q2 :- p. r :- q2, s. r :- q2, s.` (least model
{p,q,s,q2,r}) hits three loud refusals in `molasp/compiler.py`
(pinned as PR9/PR10 in the tick-48 corpus):

| gate | code | message (fragment) | why it fires on PC11 |
| --- | --- | --- | --- |
| A (PR9) | compiler.py:276–284 | `conjunctive variant … literals must sit at (adjacent-below, row-1 via), got rows (…)` | `s` lands at row 3; lo must sit at row 1 |
| B (PR10) | compiler.py:286–292 | `adjacent-below literal … is a derived row — the slot-A conduit would read its variant glue, not a truth-typed value` | hi `q2` is the derived row at i−1 |
| C (via suspension) | compiler.py:293–300 | `row-1 via relay suspended below row i (a derived row occupies the V column)` | `q2`'s row suspends the row-1 via that the lo read would ride |

(Also: the duplicated `r :- q2, s.` pair collapses to one body under
ASP semantics — PC11-as-listed exercises nothing extra; see §4.)

## 2. The observation that unlocks gate B

Gate B's premise is **stage-0-era**. designs/008 stage 1 (tick 48,
commit 77879c4) gave the intermediate derived row a truth-typed
north face: `q2`'s lock column exposes `{q2}-t-done` on its N face —
the chain link the unit reader already consumes (`unit variant … lit
== below and lit in rules: pass`). The DA conduit's S face reads
`{hi}-t-done` at strength 2 — for a derived hi, that glue name IS
the chain relay's name. Relaxing gate B is therefore a **channel
re-typing, not a new glue class**: point the DA conduit's S read at
the derived row's lock-column N face. Value typing carries verbatim
from stage 1: the relay realizes iff `q2` is true in the least
model, so a dead `q2` leaves the conduit's S face unrealized and the
AND reader never assembles — dead links stay dead by value, the
same argument that passed BFS for PC9/PC10.

## 3. Gates A and C: one mechanism question, honestly open

With hi re-typed (§2), the lo literal still must reach the terminal
row's DB reader (`S = {lo}-t-done`). Two candidates:

- **Option I — keep lo at row 1, extend the via.** Program shape
  `s. p. q2 :- p. r :- q2, s.` puts `s` at row 1 (via) and `p` at
  row 2… but `q2 :- p` then reads `p` at row 2, which is neither
  row-1 via nor adjacent-below-derived — refused (unit-variant
  gate). Putting `p` at row 1 instead (`p. s. …`) moves the problem
  to `s`. **A two-fact prefix cannot feed both the chain body and
  the AND lo under current row algebra** — this is the actual
  content of gate A. Lifting it needs Option II of designs/008
  (via-carry extension: the V column becomes stateful at every
  height), rejected there for multiplying column-2 variants and
  touching the PC3/PC4 dead-reader pins.
- **Option II — second N-face channel on the derived row.** The
  derived row relays its own truth north (stage 1) *and* re-emits
  the row below's `{lo}-t-done` on a second face. Reuses the
  stage-1 relay pattern but adds a per-row second channel — new
  machinery, no existing pin, over-production risk on false links.

**Recommendation: stage 6 = gate B only** (§2), corpus candidate
PC11a below; gates A/C stay loud refusals with this design as the
recorded reason. That keeps every relaxation single-mechanism, the
discipline that made stages 1–5 reviewable.

## 4. Corpus candidate for stage 6

| name | program | least model (hand) | exercises |
| --- | --- | --- | --- |
| PC11a | `s. p. q2 :- p. r :- q2, s.` — **refused by gates A/C as listed**; the stage-6 shape is `p. s. q2 :- s. r :- q2, p.`? no — see note | — | — |

Correction recorded in-place rather than silently: hand-working §3
shows **no 4-row placement satisfies gates A+C simultaneously** with
a derived hi AND a via lo under current row algebra. The honest
stage-6 corpus shape is therefore **n=4 with the AND terminal
reading derived-hi adjacent-below AND lo adjacent-below-2**:
`p. s. q. q2 :- p. r :- q2, q.` — lo `q` is a *fact at row 3*, read
by the DB reader through the same row-(i−2) positional channel v0.1
already uses at n=3 (lo at row 1, hi at row 2, reader at row 3).
Gate A's message says "row-1 via" but the v0.1 arithmetic is
positional: DB.S bonds at row i−1 to the value exposed there; the
row algebra generalizes (i−2, i−1, i) by one row exactly as the
unit chain did. Gates that must still move: B (re-typing, §2) and
the width/position check (A narrows from `(i−1, 1)` to `(i−1,
i−2)`). Gate C does not fire: no via crosses the derived row — the
lo read is positional, not via-carried.

| name | program | least model (hand) | exercises |
| --- | --- | --- | --- |
| PC12 | `p. s. q. q2 :- p. r :- q2, q.` | {p,s,q,q2,r} | AND over derived hi (gate B relaxed) + positional lo at i−2; live chain + live AND |
| PR13 | `p. s. q. q2 :- s. r :- q2, q.` | {p,s,q,r} | `q2` false (no support from p): AND reader must stay absent while row locks hold — the dead-link cascade at the AND terminal |
| PR14 | `p. s. q. q2 :- p. r :- q2, z.` | — | lo `z` not below terminal → loud refusal stands (gate A narrows, never silently widens) |

## 5. Predicted arithmetic (hand, from committed receipts)

PC9 (3 rows, unit chain) measured 12 tiles / 35 assemblies; PC4
(n=4, AND + dead readers) 14 tiles / 35 assemblies; middle-fact
chain 16 tiles / 70 assemblies. PC12 adds one intermediate derived
row (+1 true lock, +1 false cap vs a fact row, per designs/008 §3)
to a PC4-shaped terminal: **predicted 17–19 tiles, O(70–150)
assemblies**, BFS-static at n=4 (tick-37 rule; PC8's 85-at-n=4 is
the scale precedent). PR13's dead cascade mirrors PC10's proven
absence argument: the AND reader's S faces read `{q2}-t-done`
(unrealized: `q2` false) and `{q}-t-done` (realized), so the
conduit half stays dead — but the DB half's S face realizes on `q`
alone, **predicted to need the tick-51 strength argument** (W face
unique to the body, match 1 < TAU 2) re-checked at the AND terminal
over a derived hi. If that argument fails, the failure mode is
over-production (`r` true on a false `q2`), caught by the
decode-uniqueness pin.

## 6. Parity conditions to pin (unchanged claim shape)

Per PC12/PR13/PR14: predicted model = least model; every terminal
assembly decodes to exactly the least model; full locks on all 4
rows; every dead-body reader glue absent from every producible
assembly (PR13 is the cascade pin). Receipt regenerated by
`parity_run.py`, never assembled (tick-53 CI lesson).

## 7. Boundaries

Chain length 2 and AND width 2 only; depth > 2 and OR at an
intermediate row stay refused (designs/008 §6); via-carry extension
(Option II) remains rejected pending a design that does not touch
the PC3/PC4 dead-reader pins; all counts in §5 are predictions.

## 8. Stage-6 sequencing correction (tick 56, 2026-10-08 — measured, supersedes §3's "narrow A first, B second")

Attempted landing of stage 6 as gated at tick 55 (gate A narrowed to
(i−1, i−2), gate B relaxed, gate C value-re-typed) and reverted; both
ends of the sequencing fail, for independent reasons:

1. **Gate A cannot be a replacement — only a union.** The
   census-generality arms' AND terminals read lo = the row-1 atom
   through the V-column via relay at n>3 (`got rows (3, 1)`,
   measured: census-receipt recompute and chain-corpus byte-stability
   pins both fail under the narrowed check). Every v0.1 AND with a
   row-1 lo works through that channel. Narrowed gate A refuses them:
   a receipt-breaking narrowing, not a relaxation. Stage 6 must accept
   **(i−1, 1) via-channel OR (i−1, i−2) positional**, never the
   replacement.

2. **The positional-lo channel does not exist for a derived hi.** The
   DB half of the AND reader sits at column 2 and reads its lo value
   from the V-column tile at row i−1 — but an intermediate derived
   row's V tile carries the *chain link* (`{hi}-t-done`), which is
   load-bearing for the unit readers above it (PC9/PC10 pins; the
   stage-1 relay). The lo row's own `{lo}-t-done` N face sits two rows
   down at column 1 and is unreachable from row i. Measured shape with
   A-narrow + B-relax + value-typed C landed: PC12-N4 refuses at gate C
   with "the V column at row 3 carries 'q2-t-done', not the lo value
   'q-t-done'" — the honest sound of the missing channel. Gate B's
   relaxation alone *is* sound name-wise (DA.S = `{hi}-t-done` already
   matches the D-column chain link), but PC12's DB.S would be a dead
   glue: BFS would show `r` absent from terminal decodes — a silent
   dead build, the class tick 52 closed.

**Consequence:** stage 6 = Option II (§3): a second N-face channel on
the intermediate derived row re-emitting the row below's
`{lo}-t-done`, with the false-link over-production guard §3 names;
gate A as union. The §4 corpus choice PC12 is unreachable by gate
moves alone. The false-head decision (PR13-dead/PR14 silent
acceptance, tick 55) is unchanged and still open.

Compiler left pristine at 4b71903; suite `Ran 421 tests` / `OK
(skipped=1)` before and after. Evidence: research-log
2026-10-08-and-over-derived-stage6-correction.md.
