# 2026-10-07 — Contention severity with the dG axis (designs/007 closed)

Tick 44 · SON-4815 · run started 15:00Z · static arithmetic (tick-37
rule: every kinetic number below is already receipted; no cluster job
spent).

## What this tick did

Joined the tick-42 vacancy-contention census to the tick-43 dG
regimes into a compiler-facing severity ranking:

- `molasp.offchannel.REGIME_ANCHORS` — the four measured operating
  points (frozen 0.5 / marginal 2 / churn 4 / starvation 7), quoted
  verbatim from `evidence/2026-10-07-contention-dg-sweep/contention_dg.out`
  (n=500/arm), never asserted.
- `regime_at(dg)` — midpoint boundaries 1.0/3.0/6.0 with an
  `interpolated` flag off the measured points.
- `contention_severity(build, dg, ...)` — per-vacancy tier priced
  against the regime: critical / high / moderate in the hazard
  regimes, mitigating / starved in churn (principle #7's sign
  flip), moot in starvation (refuse the operating point).
- `check_d4` auto-attaches at `DEFAULT_DG = 0.5`; `d4_report_lines`
  names the regime, knob verdict, and every tier ≥ moderate.

## The story the tiers pin (all measured)

- BUILD1 Vp@2,2 at frozen: **critical** — minted {D1T, DBr, V0p}
  over family fill D2T (fill 0.904 → 0.412); marginal: still
  critical (232:229 stationary split); churn: **mitigating** (the
  knob is the growth carrier, 0.074 vs 0.564); starvation: moot.
- Lock/spine vacancies at frozen: **high** — minted 3–6 frozen
  contenders over NO family fill (first-come among squatters).
- BUILD2 minting generalises (D3F, Fr minted); BUILD3 tiers valid
  and minting constructional.

## Honest boundaries (carried in-artifact, `boundary_notes`)

1. dG-2 window arm untested (read-window axis priced only at dG 4).
2. Starvation persist rests on persist_n = 1.
3. L3@(2,2) (54/500) outside the tick-42 five-name census.
4. Off-point dG is nearest-regime pricing (`interpolated: true`).

## Receipt

| Claim | Evidence |
| --- | --- |
| anchors verbatim | `tests/test_contention_severity.py::TestRegimeAnchors` vs `contention_dg.out` |
| BUILD1 tier story | `TestSeverityTiers` (4 regimes) |
| generality | `TestSeverityIntegration` (BUILD2/3) |
| integration | `check_d4` carries severity; report lines name regime+tier |

Suite verbatim: `Ran 365 tests OK (skipped=1)` = 351 + 14 pins.

## Next

designs/007 is closed. Queue: (1) dG-2 window arm + L3-at-vacancy
class follow-up if promoted from boundary note; (2) founder-gated
collaborator/venue shortlist (tick-37 gate stands, no founder yes
yet); (3) principles #5/#6/#7 blog candidate (#7 now has its
compiler surface); (4) OR-AND parity corpus for compiler v0.1
(queued from tick 22).
