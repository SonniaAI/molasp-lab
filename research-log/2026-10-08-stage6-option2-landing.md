# Stage-6 Option II landing (tick 60)

Date: 2026-10-08, wake 05:00:20Z (SON-4852, run 94a2fc7e). Times in
this entry are wake-payload times and post-commit git metadata only.

## What this tick did

Executed the pre-registered landing order (designs/009 §9.5, staged
ticks 58–59): union gate A both polarities, §9.2 consumer-aware
north-face passthrough + AND reader-order swap, false-head gate —
plus the probe-first receipt gate (step 1 was tick 59's frozen
manifest; the compiler was pristine at ec49a73 through cf66897).

## Measured results (pin order honored)

1. **Receipts.** Both census receipts regenerate byte-identically
   post-edit (sha256 `b7a5c70f…cd32`, `737f04a7…9f69a` — exact
   probe-manifest values, raw compare). Parity corpus receipt
   regenerated: 414 lines, still `9 compiling + 12 refusals`, with
   exactly three legitimate diffs — PR9's refusal lines removed
   (it compiles now), PR14's added (gate A union), PR10's message
   reworded (gate B's slot-A-conduit text is false post-§9.2; new
   message names the Option II arm). Timing-masked compare shows no
   other drift.
2. **PC9/PC10 byte-stability.** Unit-consumer layouts untouched:
   the passthrough lookahead fires only on width-2 consumers; the
   existing PC9/PC10 pins pass unchanged.
3. **PC12.** n=4 arm (`p. q. q2 :- p. r :- q2, q.`): FIRST
   FULLY-ASSEMBLING AND-over-derived build — 16 tiles, 70
   assemblies, 1 terminal, full locks, decode == least model
   {p,q,q2,r}, ok=True. n=5 arm (PC12-DOC): compiles, 20 tiles /
   70 asm / 1 terminal, but SPINE-CAPPED at row 5 — the parity
   STRENGTH table stops at SP4, S5 bonds south at strength 1 < 2,
   4-row prefix decodes {p,q,q2,s}. Design's "full locks at n=5"
   prediction demolished in-place (designs/009 §9.4 correction);
   PR13-dead's tick-55 "4 of 6 rows lock" was this same cap.
4. **PR13-dead.** Unchanged build (26 tiles / 70 asm / 1 terminal /
   4 of 6 locks); dead readers `and1_r`, `unit1_q2` BFS-proved
   absent; gate passes via derived-literal adjacency (q2 at i−1).
   §9.3's "lo q at i−2" was an arithmetic slip (q at i−3; z occupies
   row 4) — corrected in-place.
5. **PR14.** Loud refusal restored (tick-55's silent acceptance
   closed): `gate A union … accepted placements … got rows (hi 5,
   lo 4, derived 4)` — message names both arms. Convention note:
   by row-sort, z is the hi; the refusal fires on the derived
   literal's position.

False-head decision (open since tick 55): RESOLVED by measurement —
out-of-arm shapes refuse loudly (PR14), in-arm dead cascades stay
accepted with emitted dead machinery proved absent (PR13-dead).

## Reader-swap layout (measured, PC12-DOC)

`Cq2.N = q-t-done` (consumer-aware passthrough re-typing),
`DAr = {W go5, S q-t-done, E and1_r, N and1_r-done}`,
`DBr = {W and1_r, S q2-t-done, E r-t, N r-t-done}` — the lo reader
south-bonds the passthrough, the hi reader south-bonds the UNCHANGED
stage-1 chain link. First recorded case split in the compiler:
derived-hi AND readers are position-incompatible with fact-hi AND
readers (lo read moves x=1 → x=2).

Suite: `Ran 421 tests in 0.83s / OK (skipped=1)` — count unchanged
(flipped pins replaced their old baselines 1:1 in the same files).

## Honest boundaries (recorded, not hidden)

- Spine cap: NO n>4 build can complete until the STRENGTH table
  grows past SP4 (candidate stage 7 — needs its own design note;
  not slipped into stage 6).
- False-head lock completion at n=5 stays as-is (spine-capped
  prefix, acceptance not refusal — unchanged behavior).
- Compile-time lookahead case split (one derived row, depth ≤ 2,
  one consumer) is named in the compiler, pinned by PC9/PC10.

## Queue receipt (first duty)

Tick-47 waiter request 9e79de4389423dfbdb8d5313afcc7603a1abc8bf
5097743157b7ad15ff58e145 (nonce dg2win-l3vac-v1, job
hxq-9e79de4389423dfb): STILL QUEUED at the 05:03Z owner-scoped
probe (~13 h; reason "queued: resource/owner limit; gateway and
engine margin preserved"). collected: null. No resubmission
(idempotent request stands). Decision from the live probe: monitor
re-armed on SON-4852 (external_service / cluster-job-queue,
nextCheckAt before the next tick, finite timeout, wake_owner) —
the hourly loop re-checks as first duty either way.
