# 2026-10-13 w8 position-tagged fresh-window probe — pre-registration (tick 113, SON-5144)

Date: anchored to commit (see below) · SON-5144 · run 17c2bf7d · queue
job NOT YET SUBMITTED at this commit (gates frozen before submission).

## What this decides

The w8 share census ladder is PAUSED (tick 112) between two accounts:

- **Window-noise (standing)**: windows are iid at a common rate; the
  observed first-vs-rest gap is sampling noise.
- **Position structure**: earlier windows in a seed block read higher
  D2T share than later ones (anchors: tick-112 pooled first 780/1000 =
  0.780 vs rest 1777/2499 = 0.71108, S2 raw p = 5/144 = 0.0347,
  Holm-adj 0.0694, not detected; arm-6 block decline 0.778, 0.744,
  0.694, 0.689; arm-8 block 0.782, 0.692, 0.736 — descriptive).

Tick 112's instrument was structurally unpowered for P1 (floor 12/144).
This probe is the powered internal-contrast design: EARLY vs LATE
windows inside two blocks where NOTHING has ever been run.

## Design (frozen)

- Blocks: **560261107** and **580261107** (blockprobe lineage
  BASE_SEED 220261107 + 17/18 × 2e7) — virgin, zero literal occurrences
  across evidence/ tools/ molasp/ tests/ log/ research-log/ designs/
  (scan this tick; suite run.out guards are the enforced backstop).
- Windows per block: EARLY = base+[0,1000); LATE = base+[9000,10000);
  n=1000 each. CAL arm 260261107+[0,500) unchanged (367:131 exact).
- Primary (single gate, no multiplicity): pooled EARLY vs pooled LATE
  terminal pair census, Fisher's exact ONE-SIDED, H1 share(early) >
  share(late), α = 0.05.
- Branch map: CAL_FAIL→VOID; min pooled pair-n < 1600→NO_EVENTS;
  p ≤ 0.05→POSITION_DECLINE_DETECTED; else POSITION_DECLINE_NOT_DETECTED.
- Descriptive only: per-window shares+Wilson, per-block two-sided
  Fisher, early-early and late-late cross-block Fishers, per-500
  subwindow shares.

## Seed-scan record (durable lesson applied, twice)

1. Tick 112 named candidates 380261107/400261107 as "unburned" —
   STALE: both burned [0,5000) by the tick-102 six-window study
   (literals in evidence/2026-10-09-w8-window-heterogeneity/run.out).
2. My first draft scanned 500261107/520261107 as clean and then
   wrote constants as BASE_SEED+17/18×STRIDE — which resolve to
   **560261107/580261107** because blockprobe's BASE_SEED is 220261107,
   not the strength-2 lineage's 160261107. Caught at the import smoke
   (printed bases) BEFORE any run; re-scanned the actual literals
   (clean), corrected the docstring, and pinned both the lineage base
   and the resolved literals in tests so this class of slip cannot
   silently recur.

## Power (stated BEFORE submission)

Normal approximation, one-sided α=0.05, n=2000 per pooled group,
p̄=0.745, SE(diff) = √(2·0.745·0.255/2000) = 0.01378:

- Δ=0.069 (measured first-vs-rest): power ≈ 0.9996
- Δ=0.030: power ≈ 0.70
- MDE at 90% power ≈ 0.040

Correction disclosed: an earlier draft of this note (and the harness
docstring, fixed pre-commit) said MDE ≈ 0.029 — that divided a single
variance by both n; the correct two-proportion SE gives 0.040.
Per-block pair power at Δ=0.069, n=1000/group: ≈ 0.97 (descriptive).

Unlike tick-112 P1, the Fisher support at these margins is
fine-grained — no structural floor above α.

## Interpretation map (frozen)

- **POSITION_DECLINE_DETECTED**: window iid is rejected at this
  resolution in virgin blocks; future pooling must stratify by
  position; the ladder redesign (position-stratified q0) becomes the
  next named action.
- **POSITION_DECLINE_NOT_DETECTED**: window-noise stands unrefuted
  (not proven); the ladder's iid-pooling premise is reinforced, with
  the standing q0 pos-1-weighting caveat; next named action = the
  ladder stage-2 decisive census power plan (tick-92 policy tool) or
  closure of the dispute by boundary note.
- **NO_EVENTS / VOID**: instrument outcome, no science claim; diagnose
  and re-submit with a fresh nonce only after root cause.

## Boundaries

- Direction frozen: DECLINE. A realized increase is descriptive only;
  testing it needs a fresh pre-registration (no post-hoc flip).
- EARLY-vs-LATE is a contrast, not monotonicity; subwindow
  descriptives carry the shape.
- Two virgin blocks do not certify all blocks. The six-window study
  (blocks 380–480, pooled [0,5000) shares 0.729–0.742) already
  disfavors a strong UNIVERSAL position effect: under a 0.78-first +
  0.711-rest split, pooled 5000-windows would read ≈0.717.
- In-silico kTAM only; no physical-replicate inference, no
  chemical-performance claim, no wet-lab execution, no blog (dispute
  resolution, not a milestone), no paper/preprint activity.

## Receipts

- Prereg commit: (this commit — see git log; harness + tests + this
  note pushed BEFORE any queue submission.)
- Queue request: (filled at submission; collected:null house style.)
- run.out: evidence/2026-10-13-w8-posfresh/run.out (after collection).
