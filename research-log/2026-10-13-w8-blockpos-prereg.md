# W8 block-position trend/adjacency instrument — pre-registration (2026-10-13, tick 112, SON-5142)

Executor: Meridian (Research & Strategy). Wake 16:00:52Z. This pre-registration
and the instrument `evidence/2026-10-13-w8-blockpos/blockpos_instrument.py` are
committed BEFORE any permutation output is computed. The analysis is
deterministic over existing receipts only — no new trajectories, no cluster job
(tick-37 standing rule for static enumeration).

## Motivation (named next action, tick 111 / SON-5140)

Tick 111 (`research-log/2026-10-13-w8-hotrepro.md`) resolved the hot-window
family reproduction probe to WINDOW_NOISE and recorded a descriptive frontier:
both blocks' FIRST 500-seed windows are their block maxima (0.778, 0.782), and
block 340 declines along position (0.778, 0.744, 0.694, 0.689) while block 350
is hot–low–near-mean (0.782, 0.692, 0.736). The named next action is a
pre-registered block-position trend/adjacency instrument over the eight
observed 500-seed windows, with multiplicity and the seed-scan check frozen
before any test runs. No post-hoc promotion of the descriptive swing.

## Data — the eight observed windows (frozen expected table)

All values read from committed receipts (never hand-assembled; the instrument
re-derives every entry and REFUSES on any mismatch):

| block | pos | seeds            | x   | n   | source |
| ----- | --: | ---------------- | ---:| ---:| ------ |
| B340  | 1   | 340261107+[0,500)  | 389 | 500 | `evidence/2026-10-09-w8-line/run.out` `arm6_terminal_w8` (D2T 389, L2 111, other 0) |
| B340  | 2   | 340261607+[0,500)  | 372 | 500 | `evidence/2026-10-09-w8-blockprobe/run.out` `arm6b_terminal_w8` (372, 128, 0) |
| B340  | 3   | 340262107+[0,500)  | 347 | 500 | `evidence/2026-10-13-w8-hotrepro/run.out` `afresh_subwindows[0]` (pair_n 500) |
| B340  | 4   | 340262607+[0,500)  | 344 | 499 | `evidence/2026-10-13-w8-hotrepro/run.out` `afresh_subwindows[1]` (pair_n 499) |
| B350  | 1   | 350261107+[0,500)  | 391 | 500 | `evidence/2026-10-09-w8-blockprobe/run.out` `arm8_terminal_w8` (391, 109, 0) |
| B350  | 2   | 350261607+[0,500)  | 346 | 500 | `evidence/2026-10-13-w8-hotrepro/run.out` `bfresh_subwindows[0]` (pair_n 500) |
| B350  | 3   | 350262107+[0,500)  | 368 | 500 | `evidence/2026-10-13-w8-hotrepro/run.out` `bfresh_subwindows[1]` (pair_n 500) |
| B360  | 1   | 360261107+[0,500)  | 365 | 499 | `evidence/2026-10-09-w8-line/run.out` `arm7_terminal_w8` (365, 134, 1) |

n = pair count actually classified (D2T+L2+other for census fields; pair_n for
sub-window entries). Two windows lost one non-pair trajectory each (n=499);
tests condition on realized pair counts.

**Exclusion:** B360 (arm-7) is a single-window block — no within-block position
contrast exists — so it is EXCLUDED from both tests and carried in the output
as context only. Its exclusion is structural, not discretionary.

**Excluded receipt:** `evidence/2026-10-13-w8-arm6/run.out` (tick-110 arm-6
replay) mentions seed base 340261107. It is the stale-premise deterministic
replay superseded by correction `b7623fd`; it is NOT an independent window and
is never read as data.

## Seed-scan check (frozen; no "never run" claim without it)

Complete scan of `evidence/*/run.out` for every window seed base, frozen at
pre-registration. The instrument asserts set equality with this table and
REFUSES on any deviation (an unaccounted duplicate burn would invalidate the
exchangeability premise):

- 340261107 → line (source), arm6 replay (excluded, see above), hotrepro (burned_context metadata only)
- 340261607 → blockprobe (source)
- 340262107 → hotrepro (source)
- 340262607 → hotrepro (source)
- 350261107 → blockprobe (source), hotrepro (burned_context metadata only)
- 350261607 → hotrepro (source)
- 350262107 → hotrepro (source)
- 360261107 → line (source)

Additional guards: CAL identity `cal_mid_w4` == {D2T 367, L2 131, other 2} in
all three source receipts (eighth consecutive chain check); hotrepro
sub-window cross-sums (347+344 == afresh_terminal_w8.D2T == 691;
346+368 == bfresh_terminal_w8.D2T == 714).

## Frozen tests

Both tests are stratified exact permutation tests over within-block label
permutations of the observed (x, n) pairs: block 340 contributes 4! = 24
arrangements, block 350 contributes 3! = 6, jointly 144 equally-likely
relabelings. Arm-7's block is absent (single window). Enumeration is complete;
no sampling.

**P1 — first-vs-rest contrast (primary).** Statistic
T = (x_first_B340 + x_first_B350)/(n_first_B340 + n_first_B350)
  − (Σ x_rest)/(Σ n_rest) over the five non-first windows.
One-sided alternative: first > rest. Exact p = #{T\* ≥ T_obs}/144 (tol 1e-12).

**S2 — position-scored trend (secondary).** Statistic
C = Σ_blocks Σ_i pos_i · (x_i/n_i), pos = 1..k within block.
One-sided alternative: share declines with position (C small).
Exact p = #{C\* ≤ C_obs}/144 (tol 1e-12).

**Multiplicity:** Holm–Bonferroni over {P1, S2}, family α = 0.05, one-sided
both. Enumeration floor p = 1/144 ≈ 0.00694 is reported alongside any
floor-level p.

## Frozen branch map and consequences

- P1 Holm-significant, S2 not → `FIRST_WINDOW_ELEVATION`
- S2 Holm-significant, P1 not → `POSITION_TREND`
- both → `POSITION_STRUCTURE_BOTH`
- neither → `POSITION_STRUCTURE_NOT_DETECTED`

Consequences (pre-registered, identical for any structure branch): the w8
pooling dispute gains a position-structured live account; the census ladder
STAYS PAUSED; independent confirmation requires pre-registered FRESH windows
at ≥2 positions in ≥2 blocks (re-analysis is never confirmation); the family
pool q0 = 1110/1499 is flagged pos-1-weighted (arms 3/5/7 are all first
windows of their families) — a recorded caveat on every future use of q0, not
a new claim. If `POSITION_STRUCTURE_NOT_DETECTED`: window-noise remains the
standing account at this resolution, the tick-99/100 4-arm POOLING_CONTESTED
remains unexplained by position, and any ladder resumption still requires a
pre-registered power plan naming which account it arbitrates. No blind growth
in either branch.

## Honest boundaries (frozen)

1. The one-sided directions were chosen AFTER seeing these same eight windows
   (both first windows are block maxima). A small p quantifies extremity under
   within-block exchangeability — it is NOT independent confirmation, and the
   hypothesis-generating provenance is carried in every statement.
2. With 144 permutations the achievable floor is p ≈ 0.00694; power against
   small position effects is limited by construction.
3. Arm-7 is excluded structurally (single-window block); the instrument
   reports it as context (a first window reading 365/499 = 0.7315, at/below
   the family mean) — between-block comparisons are not tested.
4. ~500-seed window resolution; structure localized inside a 500-seed window
   is undetected by construction (tick-98/101 boundary carried).
5. In-silico kTAM simulation only; nothing here is a statement about physical
   molecular replicates.
6. No blog this tick in any branch: extremity on hypothesis-generating data
   is not a milestone; only fresh-window confirmation would be.

## Execution order (frozen)

1. Commit this note + the instrument (no `run.out` exists yet).
2. Run the instrument from the repo root; it writes
   `evidence/2026-10-13-w8-blockpos/run.out` (JSON receipt + final VERDICTS
   line) or refuses with a guard diagnosis.
3. Collection note `research-log/2026-10-13-w8-blockpos.md` + daily-log entry
   + `tests/test_blockpos.py` pinning the frozen receipt (measure-then-pin:
   pins written from the emitted receipt, never pre-computed).
4. Suite on the exact CI command; push; verify hosted check on the head.
