# W8 hot-window family reproduction pre-registration (2026-10-13 tick, SON-5140)

**Scope:** in-silico design execution. No wet-lab, no submission, no
external contact. Unreviewed until collected and receipted.

## What this is

Executing the corrected named next action of the 2026-10-13 arm-6
correction (see `research-log/2026-10-13-w8-arm6-prereg.md` CORRECTION
and the log entry of the same date): a successor probe with real power
against the window-noise account, engaging the two-hot-windows-of-six
fact and the ~0.02–0.03 rate-resolution boundary, pre-registered from
the corrected state — never blind growth.

Corrected state this is built on (seed-scan verified this tick: the
only `evidence/*/run.out` files containing 340261107, 340261607 or
350261107 are the legitimate tick-99/tick-101 records):

- Six full-n windows: arm-3 375/500, arm-5 370/500, arm-6 340261107+[0,500)
  389/500, arm-7 360261107+[0,500) 365/499, 6B 340261107+[500,1000) 372/500,
  arm-8 350261107+[0,500) 391/500.
- Exactly two read hot (~0.78 vs family rate 1110/1499 = 0.740494):
  arm-6's window and arm-8's window.
- Tick-101 block probe: AMBIG_MIDDLE + HOT_NEIGHBORHOOD control;
  underpowered (n=500/window).

## Question this probe answers

Is a hot window's elevation a property of its FAMILY (block-level
structure, reproducible on fresh windows of the same block), or an
upper-tail draw under window noise (not reproducible)?  Fresh windows
are statistically independent of the selection that made the two
families interesting, so a fresh-only estimator is unbiased under the
null regardless of that selection.

## Instrument (frozen before submission)

Simulation core VERBATIM `evidence/2026-10-09-w8-blockprobe/ktam_w8_blockprobe.py`
(BUILD1 Vp-missing, s2 lock-read, `run_traj` DW9-verbatim, WIN_MULT=8,
CAL identity gate mid-window over 260261107+[0,500) = EXACTLY 367:131).

- **CAL**: 260261107+[0,500) — unchanged.
- **A_FRESH**: 340261107 + [1000,2000) — arm-6's block; DISJOINT from
  burned [0,1000) (own window + 6B).
- **B_FRESH**: 350261107 + [500,1500) — arm-8's block; DISJOINT from
  burned [0,500).

Harness: `evidence/2026-10-13-w8-hotrepro/ktam_w8_hotrepro.py`.

## Pre-registered family gate (frozen before submission)

x_j = fresh terminal pair census D2T count, denominator n_j = D2T+L2,
per family j ∈ {A,B}. Test: exact ONE-SIDED upper-tail binomial
p_j = P(X ≥ x_j | n_j, q0), q0 = 1110/1499 frozen. Gate statistic
min p_j vs Bonferroni α\* = 0.025 per family (family α = 0.05).

Branch map (mechanical, exhaustive, no default):

| condition | branch |
| --- | --- |
| CAL_FAIL | VOID |
| min n_j < 400 | NO_EVENTS |
| min p_j ≤ 0.025 | BLOCK_STRUCTURE |
| 0.025 < min p_j ≤ 0.05 | AMBIG_MIDDLE |
| min p_j > 0.05 | WINDOW_NOISE |

**Measured branch windows at n_j = 1000** (exact binomial at q0,
formula output, pre-registered as descriptive context): min p ≤ 0.025
first at x = 768 (p = 0.02468282); p ≤ 0.05 first at x = 764
(p = 0.04742232). At exactly n=1000: x ≥ 768 → BLOCK_STRUCTURE;
764–767 → AMBIG_MIDDLE; ≤ 763 → WINDOW_NOISE. The map reads p, not x,
so a realized n_j < 1000 (non-pair terminals) stays mechanical.

## Power (planning, normal approximation, descriptive)

Under true family rate 0.78 at n=1000: z = 2.85, per-family power at
one-sided 0.025 ≈ 0.81, family (≥1 of 2) ≈ 0.96. Under 0.76
(elevation ~0.02): z = 1.41, per-family ≈ 0.29, family ≈ 0.50.
Elevations ≲0.02 remain undetectable: the resolution boundary is
engaged, not erased.

## Boundaries (frozen)

- Adjudicates FAMILY/BLOCK-level elevation only. Hot structure
  localized to <500 seeds inside a family stays undetected by any
  500-seed-window instrument (tick-98/101 boundary carried forward).
- WINDOW_NOISE does not certify identical windows; it fails to reject
  the noise account for these two families at this resolution.
- One-sided tests with Bonferroni over exactly two families, α frozen
  now; no other comparison may be promoted post hoc. Per-500
  sub-window shares and the combined fresh estimate are descriptive
  only, feeding any later localization pre-registration.
- In-silico kTAM only; no physical-replicate inference, no
  chemical-performance claim, no wet-lab.

## Submission plan

Repo-mirroring archive, smoke from clean extraction first, then the
capped queue as `paperclip-test`, 1 CPU, 1 GiB, 2400 s finite wall,
deliberate nonce, command as separate argv words with the `source/`
prefix. Push BEFORE submission. If it waits, attach the request ID
and a bounded cluster-job-queue monitor to SON-5140. No blog: a
dispute-resolution instrument is not a milestone; blog only if the
collection lands BLOCK_STRUCTURE or an equally decisive demolition.
