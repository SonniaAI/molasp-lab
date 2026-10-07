# Glue-family scope evaluated + related-work sweep (tick 29)

2026-10-07 (tick 29, SON-4778). Two halves of one question — where
does the d2/d3/d4 check family and the glue-family scope knob sit in
the published literature, and what does the knob actually buy when
you turn it? Part 1 is a grounded sweep (links live-checked
2026-10-07); part 2 is machine-checked arithmetic pinned in
`tests/test_glue_scope.py` (`molasp/offchannel.py`:
`apply_lock_glue_scope`, `lock_glue_scope_reports`).

## Part 1 — related work

**Error-correction transformations (the classic line).** Winfree &
Bekbolatov's proofreading tile sets
([DNA 9, LNCS 2943](https://link.springer.com/chapter/10.1007/978-3-540-24628-2_13))
suppress mismatch errors by replacing each tile with a k×k block;
Chen & Goel's snaked proofreading
([DNA 10, LNCS 3384](https://link.springer.com/chapter/10.1007/11493785_6))
fixes its nucleation weakness; compact variants trade size for
robustness (Reif–Sahu–Yin
[compact error-resilient tilings](https://users.cs.duke.edu/~reif/courses/molcomplectures/TilingAssembly/AssemblyErrorCorrection/CompactErrorResilientAssembliyReif.pdf),
Soloveichik & Winfree's
[compact-proofreading complexity](https://www.dna.caltech.edu/Papers/fragile_patterns_preprint.pdf)).
All of these MODIFY the tile system — geometric scaling, bond
redistribution — to make errors reversibly detectable. d4 modifies
nothing: it is an emit-time REPORT of the misincorporation channels
the emitted inventory already admits, with measured kinetic context
attached. The `lock_glue_scope` knob does touch the inventory, but
it moves along an axis none of those transformations use: glue-NAMING
scope, with no geometric scaling — and it pays in the repair channel
rather than in assembly size.

**Repair / self-healing.** Soloveichik, Cook & Winfree
[combine self-healing with proofreading](https://www.dna.caltech.edu/Papers/selfhealing_proofreading_preprint.pdf)
via block transformations: damaged regions re-grow because the
encoding is redundant by construction. Our substitution repair
(tick 24: D1T fills the V0p vacancy 74.9%, D2T fills Vp's 90.1%,
symmetric 94/97%) is EMERGENT — nobody designed it; it falls out of
value-glue sharing — and the new measured finding is its PRICE:
the same sharing admits lock squatters (31.4% block rate at dG 0.5,
decaying to 0 by dG 4), a 4.51× non-pqr lock-dwell sink (tick 27 P2),
and the cross-row lock misread (23/23 of the L3-arm false
positives). Repairability and squattability are one property. We
found no prior statement of that duality in the tile-assembly
literature.

**Compile-then-verify pipelines.** The closest methodological
relative: Nuskell (Badelt, Shin, Johnson, Dong, Thachuk, Winfree —
[a general-purpose CRN-to-DSD compiler with formal
verification](https://par.nsf.gov/servlets/purl/10093595),
[docs](https://www.dna.caltech.edu/~badelt/nuskell)) compiles CRNs
to strand displacement systems and verifies the implementation
against the specification (see also Shin's
[compiling-and-verifying thesis](https://users.cs.duke.edu/~reif/courses/molcomplectures/CRNs/SeungwooshinMasterThesis2011.pdf)
and the domain-level
[reaction enumerator](https://pmc.ncbi.nlm.nih.gov/articles/PMC7328391)).
Our d2 (dropped literals) and d3 (compile-model closure/support) are
the same kind of object: static semantic checks between source
semantics and compiled substrate. d4 is the piece their architecture
does not have: a warning-severity KINETIC hazard census against a
predicted canonical assembly, severity read against measured rates.
Binary verification answers "is this the specified system"; d4
answers "what else does this inventory admit, and how much read-time
might it cost."

**Framing/survey anchors.** Patitz's
[tile-based self-assembly survey](https://readkong.com/page/an-introduction-to-tile-based-self-assembly-and-a-survey-of-4619979)
(aTAM/kTAM, error-correction results) and Winfree's 1998 thesis
(kTAM's origin) frame the model; Cannon et al.'s
unique-terminal-assembly verification (see the
[producibility results](https://link.springer.com/chapter/10.1007/978-3-319-08123-6_12)
context) is the aTAM-side analogue of our BFS checkers.

Honest boundary: this is a targeted sweep (four query families,
2026-10-07), not a systematic review; no collaborator contact has
been made yet — that is a separate decision, not a finding.

## Part 2 — the knob, evaluated (machine-checked)

`lock_glue_scope ∈ {family, row}` (designs/004). Under `row`,
canonical lock-read bonds (via E ↔ lock W) become `{g}-lk{i}` for
the lock's row, and canonical vertical relay bonds on value glues
(`-t` / `-t-done`) become `{g}-lk{i+1}` for the row pair they span —
every rename touches a canonical bond on BOTH faces, so the
canonical assembly is preserved by construction (pinned: no site
falls below τ=2 on either build). What breaks is every off-channel
use of those same bonds.

BUILD1 (the census build), d4 under both scopes:

| scope | lock hazards | lock misreads | off-channel sites | repair bonds (D1T@2,1 / D2T@2,2) |
|---|---|---|---|---|
| family | V0p@(3,1):1, Vp@(3,2):1 | incl. Vp→L2, D2T→L2 at (3,3) | 7 | 2 / 2 (stable b=2 repair) |
| row | **none** | **none** | 4 | 1 / 1 (b=1 transient holds only) |

The trade, with numbers on both sides: `family` buys substitution
repair at 74.9–97% (R3b receipts) and pays in squatters (0.314 →
0.118 → 0.000 block rate by dG, R4), a 4.51× dwell sink (P2) and
the misread (23/23, R3c); `row` zeroes the static lock-hazard and
misread classes and eliminates the STABLE repair channel with them
— b=2 substitution becomes b=1 transient contact, because all three
channels are the same bonds (designs/004's claim, now arithmetic:
`repair_bonds` 2→1 both arms).

BUILD3 (W1 wrong-compile arm, A4's build) — the honest boundary:
family hazards {V0q@(3,1):1, Fplus@(3,2):1, Fp@(3,3):1}; under row,
V0q and Fplus die but **Fp@(3,3) survives** — its hold rides
non-value-family glues (false-row terminal), and the current
qualification rule covers `-t`/`-t-done` only. The knob eliminates
the measured build1 hazard class (the two exceeds-parity squatters
and the misread enablers); it is not a universal hazard eliminator.
Design follow-up noted in designs/004: extend the qualification to
false-family glues where false rows sit at lock columns.

## Files

- `molasp/offchannel.py` — `apply_lock_glue_scope`,
  `lock_glue_scope_reports` (d4 under both scopes + repair bonds).
- `tests/test_glue_scope.py` — the pins above (12 tests).

## Next

- Extend the row-scope rule to false-family glues (kill BUILD3's
  Fp@(3,3)) or document it as out of scope with a reason.
- Optional pre-registered kTAM validation of the row-scope
  prediction (lock-squat rate → 0, substitution fill → 0) — the
  static census says the channels are gone; a small grid would
  confirm no NEW channel opens.
- Collaborator/venue shortlist from Part 1 (a founder-gated
  outreach decision, not a lab default).
