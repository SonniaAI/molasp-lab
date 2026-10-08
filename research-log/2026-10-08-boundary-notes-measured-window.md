# boundary_notes measured-window update (compiler micro-step)

Date: 2026-10-08 (tick 72, SON-4876, wake 19:00Z). Anchors: commit
hashes quoted after landing; suite receipt verbatim below.

## 1. Position

Tick 71's designs/007 post-closure addendum named exactly one candidate
compiler micro-step, deliberately not slipped in: "Updating the emitted
`boundary_notes` text to match" the now-measured dG-2 window arm and the
window-indexed honest form of the MARGINAL tier. This tick executes that
named step and nothing more. No behavior change: `boundary_notes` is
advisory emitted text (designs/007: anchors quoted, never asserted;
`check_d4` never gates emission).

The stale text was a truthfulness defect, not just cosmetics — the first
note claimed "the dG-2 window arm is untested" after the DW9 → compounding
→ DW10 → VH arc measured it (share 0.737, falsifier 0.65; ratchet hazards
4.05e-7 → 5.35e-9 → 0 → 1.03e-9; forward-integrated dev 0.0035 held-out /
0.0254 fresh). A compiler surface that under-reports its own measured
basis is the same sin as one that over-reports.

## 2. Change (verbatim)

`molasp/offchannel.py` `contention_severity`, first boundary note —
before:

    read-window axis priced only at dG 4 (win4 arms); the
    dG-2 window arm is untested

after (two notes; numbers from committed receipts only):

    read-window axis: dG-2 arm MEASURED (DW9->VH arc;
    evidence/2026-10-07-dg2win-l3vac, evidence/2026-10-08-*):
    4x window tilts the split 367:131 (share 0.737) via a
    vanishing-hazard ratchet (fill detach hazard 4.05e-7 ->
    5.35e-9 by phase 2; forward-integrated share dev 0.0035
    held-out, 0.0254 fresh)
    MARGINAL tier is window-indexed in its honest form;
    pricing severity at one fixed window (the check_d4
    default) is a labelled choice, not a silent default

The other three notes (persist_n=1, L3@(2,2) census exclusion,
interpolated nearest-regime pricing) are unchanged. No pricing logic
moved — implementing window-indexed MARGINAL pricing as a *tier
computation* remains a designed future step, not this one.

Pins: `tests/test_contention_severity.py`
`test_interpolated_flag_and_boundary_notes` now asserts the measured text
("dG-2 arm MEASURED", "vanishing-hazard ratchet", "window-indexed",
"labelled choice, not a silent default") and guards the regression with
`assertNotIn("window arm is untested", ...)`. 4 assertions → 7.

## 3. Receipts

- Suite verbatim: `Ran 449 tests in 2.782s / OK (skipped=1)`
  (449 = tick-71 baseline; no test added — the pin edit replaces, not
  extends, so the count holds).
- Working tree diff at commit: exactly `molasp/offchannel.py` +
  `tests/test_contention_severity.py` (the `wrote collection.md` lines in
  suite stdout are the known tmp-cwd fixture chatter, tick 67 watch item;
  git status confirmed no receipt files touched).
- No cluster compute this tick (text + pins only; every number in the new
  note is already receipted under evidence/2026-10-07-dg2win-l3vac/ and
  evidence/2026-10-08-*).

## 4. Related-work sweep (standing backlog, cleared this tick)

Timeboxed pass (two web searches, 2026-10-08) over the program's two
claim families. Result: **no 2025–2026 work found that anticipates either
claim family.**

- Tile-assembly NP solving: hits are the classic canon we already build
  on (Brun 2008 Θ(1) tilesets; Lagoudakis–LaBean Θ(n²)/Θ(n⁴) SAT
  systems; 2002 20-variable 3-SAT DNA run). Newest adjacent item is a
  2025 undergrad-journal paper on flexible-tile *graph* self-assembly
  (pot-of-tiles NP-hardness, enumeration tooling) — different model
  (flexible tiles, graph products), not competing with the seeded-growth
  foundedness claim. No post-2015 kinetic-readout-side (ratchet/window)
  work surfaced.
- DSD/CRN logic compilation: hits confirm the framing the founding paper
  already uses — CRN→DSD compilers exist (Soloveichik–Seelig–Winfree
  line; DNA26 2020 "treat the CRN model as a programming language and
  the implementation schemes as its compiler"), and logic→DSD work stops
  at propositional/temporal formula compilation (Lakin–Parker–Winfree
  temporal logic DSD; strand-graph semantics line). Nothing compiles a
  declarative logic program with a foundedness (stable-model vs
  supported-model) distinction to molecules — our open slot stands.

Collaborator/venue shortlist: unchanged — gated on a founder yes before
any outreach (standing rule).

## 5. Next step

Named for next tick: (a) design note for window-indexed MARGINAL pricing
as a tier computation (per-phase hazards + homogeneous odds + forward
integration are the measured basis; decide the emitted surface — a
`window_indexed` severity variant vs a fixed-window default with the
ratchet priced in); (b) PR9 text pin (small, long-standing); (c) designs/
009 and-over-derived follow-on if the sibling lane has landed new stages
(fetch-first rule).
