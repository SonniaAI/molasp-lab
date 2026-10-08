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
