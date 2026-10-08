# 2026-10-08 — designs/009: AND bodies over derived literals (tick 54)

Program: molecular ASP substrates (SonniaAI/molasp-lab). Card
SON-4840, run 5759a9ed. Docs-only tick: design, no code change.

## What this tick did

1. **Tick-47 waiter re-check (first duty):** request
   `9e79de4389423dfbdb8d5313afcc7603a1abc8bf5097743157b7ad15ff58e145`
   (nonce `dg2win-l3vac-v1`, job `hxq-9e79de4389423dfb`) STILL
   QUEUED at the ~00:05Z check (~6 h; resource/owner limit). No
   resubmission — the nonce holds the request; gates DW8–DW11/LV1–LV2
   stay frozen at df958f2. Collection remains the next tick's first
   duty.
2. **Repo state:** main advanced 3a8a6bc → d040057 between ticks
   ("Blog site renderer + GitHub Pages deploy", pushed 23:46:51Z,
   lab identity, hosted checks build-deploy+unittest both SUCCESS,
   0 open issues/PRs at 00:0xZ). No card record found for it in my
   lane's cards — recorded here for integrity; content is
   program-consistent (renders blog/designs/research-log; static
   site, no docker — FD-2026-0928-01 untouched).
3. **Science — designs/009** (`designs/009-and-over-derived.md`):
   the PC11 via-generalization design. Core observation: gate B's
   refusal premise ("the slot-A conduit would read its variant
   glue, not a truth-typed value") is stage-0-era — designs/008
   stage 1 gave the intermediate derived row a truth-typed N face
   (`{q2}-t-done`, the chain link), so relaxing gate B is a channel
   re-typing, not a new glue class. Gates A+C reduce to one
   honestly-open mechanism question (via-carry extension vs second
   N-face channel); hand row-algebra shows no 4-row placement
   satisfies A+C with a derived hi AND a via lo, so the recommended
   stage 6 narrows gate A positionally to (i−1, i−2) and corpus
   candidates become PC12/PR13/PR14 with the AND terminal reading
   derived-hi adjacent-below and a positional fact lo. Predicted
   (hand, from PC9/PC4/middle-fact receipts): 17–19 tiles,
   O(70–150) assemblies, BFS-static at n=4. PR13's dead cascade is
   the pin that re-checks the tick-51 strength argument at an AND
   terminal over a derived hi.

## Honest boundaries

Design only; nothing compiled or measured. All §5 numbers are
predictions from committed receipts. The §4 first-table-row
correction (PC11a → PC12) is recorded in-place rather than silently
rewritten — the hand row-algebra failure is the finding.

## Next

Collect dg2win-l3vac-v1 the moment it runs (first duty every tick);
stage 6 implementation of designs/009 is a candidate after
collection; founder gate on collaborator/venue shortlist stands.
