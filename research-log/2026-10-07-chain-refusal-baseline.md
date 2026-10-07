# Chain-refusal baseline — what v0.1 actually does to the designs/008 programs (tick 47 wait-work, SON-4821)

Card: SON-4821 (tick 47 monitor waits). Tests:
`../tests/test_chain_refusal_corpus.py` (7 pins, all probed live
~18:44Z before pinning). Suite verbatim on the exact CI command:
`Ran 394 tests in 0.759s / OK (skipped=1)` = 387 + 7.

## Question

designs/008 §1/§4 tables the twice-derived-chain corpus programs
(PC9/PC10/PC11) as blocked behind the two v0.1 refusals it names
(G1 rule-atom-below-terminal, G2 direct-below-unit). Before any
relaxation work: what does the current compiler *actually* do with
each proposed program, probed, not read off the design?

## Probed today-truth (v0.1)

| program | today's behavior | gate |
| --- | --- | --- |
| PC9 `p. q :- p. r :- q.` ({p,q,r}) | refused: `rule atom 'q' at non-terminal row 2 … multi-derived-row chains are untested geometry` | G1 |
| PC11 `p. q. s. q2 :- p. r :- q2, s. r :- q2.` ({p,q,s,q2,r}) | refused: `rule atom 'q2' at non-terminal row 4` | G1 |
| `p. q :- p. s. r :- q.` (all predicted) | refused with the **G1** message, not the G2/via-carried one | G1 fires before G2 |
| PC10 `p. q :- z. r :- q.` ({p}) | **compiles and BFS-verifies**: ok=true, model {p}, full locks, dead glue `unit1_r` absent, 4 rows, 16 tiles, 70 assemblies, 1 terminal | none — see below |
| CYC `q :- r. r :- q.` | refused: `row order: dependency cycle … tick-14 order falsifier` | order falsifier (pre-G1) |

## The PC10 surprise

designs/008 §1 lists PC10 as blocked by G1+G2. It is not: `q` and
`r` fall outside `predicted`, and the G1 gate is armed only inside
the `if a in predicted:` branch — non-predicted rule atoms take
**fact-false rows**. So PC10's least model {p} already verifies
today, on a fact-false-row basis, without any chain machinery. The
correction to the design: the v0.2 relaxation is needed for the
*false-cap relay machinery* at intermediate derived rows (PC10 as
the first pin of dead-link cascade semantics), **not** for PC10's
model. Consequence for the corpus plan: PC10's acceptance flip is a
*basis swap* (fact-false rows → derived-row machinery with relay),
not a refusal→acceptance flip like PC9/PC11; its v0.1 numbers above
are the baseline the swap is measured against (16 tiles / 70
assemblies free to move; model, locks, dead-reader absence must
not).

## Gate ordering

In a chain, G1 (rule atom at a non-terminal row) rejects the
program before G2 (unit literal not via-carried) is ever consulted —
pinned by the third row above. The v0.2 relaxation must lift G1 for
legal chain geometry and *then* route `r`'s unit reader to the
slot-A direct-below channel (designs/008 option I), at which point
G2's via-carried refusal becomes the non-adjacent-chain refusal
(head reading a derived atom ≥2 rows below) — not probed today
because it is unreachable behind G1.

## v0.2 acceptance boundary (for the PR3 tick)

1. PC9, PC11: refusal → verified corpus entries (model, unique
   terminal decode, full locks, dead-reader absence per designs/008
   §5).
2. CYC: refusal **survives verbatim** (order falsifier is
   geometry-independent).
3. PC10: re-verifies on the derived-row basis; model/locks/
   dead-reader pins unchanged, tile/assembly counts may move.
4. New refusals appear for non-adjacent and wrong-depth chain reads
   once G1 stops firing first.

No measurements claimed beyond the compiler/BFS probes above; the
dG-2 window + L3-vacancy job (request `9e79de43…e145`) was still
queued at collection time of this entry and is unaffected.
