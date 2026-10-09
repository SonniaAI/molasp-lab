# designs/011 — Window-indexed MARGINAL pricing as tier computation

Date: 2026-10-08 (tick 73, SON-4879) — time anchored to this note's
landing commit; no wall-clock value here anticipates an event.

## Problem

designs/007's MARGINAL tier priced knob-sensitive vacancies at a
fixed read window.  Ticks 71-72 named the honest form: the dG-2
fill-vs-squatter split is window-length-dependent (DW9: 4x window
tilts 367:131, share 0.737; tick 43's near-fair coin 232:229 was the
1x window), and pricing severity at one fixed window is a labelled
choice, not a silent default.  Tick 70's VH ratchet supplied the
measured basis: pooled homogeneous attach odds + per-phase detach
hazards, forward-integrated (held-out dev 0.0035, fresh dev 0.0254).
This design makes the window curve itself the tier computation.

## Key realization

The DW10 snapshot fracs of the 4x window ARE measured window points:
window w means read time w x 400 e^Gmc, so snap 0.25 = the w1 read
(the same 232:229 census tick 43 measured at the 1x window), snap
0.5 = w2, snap 0.75 = w3, and the DW9 terminal = w4.  The window
curve therefore has FOUR measured anchors plus a chain validated at
its terminal — no new kinetics are needed to price the curve.

## Construction (molasp/offchannel.py)

- `VH_BASIS` — the fit quoted verbatim from
  `evidence/2026-10-08-vh-ratchet/run.out` (lam, pooled p, d_o,
  per-phase hazards, snapshot init v0, share_pred receipt 0.74135,
  homo stationary receipt 0.71240).  Never asserted; pinned in
  tests/test_window_pricing.py.
- `WINDOW_MEASURED` — the w1-w4 census points (232:229, 318:174,
  348:146, 367:131) with sources.
- `_vh_share(w, haz_d2t=None)` — the VH 4-state chain (E, D2T, L2,
  O) forward-integrated from the w1 snapshot through the fit-grid
  phases (2, 3, 4), each one w1 wide; beyond w4 the LAST fit-phase
  hazards are held (extrapolation).  Pure-python uniformized expm
  (the validated VH construction; closed-form-pinned here).
- `marginal_window_pricing()` — the emitted curve: measured share +
  census (where measured), chain share + kind (snapshot / fit-grid
  prediction / EXTRAPOLATED), tier label, the frozen-class quote
  (DW11 persist 0.826 — window-immune), and the homo stationary
  (what a window-blind model would say).  Extrapolated entries
  carry a `hazard95_share` sensitivity arm (Poisson-95 upper bounds
  on the late D2T hazards, VH1 receipt) — a bracket, not a second
  prediction.
- `window_tier(share)` — `contested` < 0.55 (the near-fair attach
  coin; the fill is NOT reliable), `ratchet-tilting` 0.55-0.75 (the
  ratchet has engaged; squatter holds 25-35%), `ratchet-tilted`
  >= 0.75.  Thresholds are labelled choices on a measured curve,
  not derived constants.
- Wiring: `contention_severity(..., dg=2)` gains `window_pricing`;
  `check_d4(dg=2)` flows it; `d4_report_lines` prints the curve and
  the frozen quote.  Other regimes emit nothing (the default dG
  stays the 0.5 protocol point — labelled choice preserved).

## Checks (computed this tick; static deterministic arithmetic per
the tick-37 rule — every input is a committed receipt)

| # | Gate | Result |
| --- | --- | --- |
| P1 | chain w4 == receipt share_pred 0.74135 (implementation identity) | PASS — 0.74135 (delta < 5e-4) |
| P2 | chain w2/w3 vs DW10 snapshots (never gates during the fit) | PASS — 0.65254 vs 0.64634 (+0.0062), 0.71067 vs 0.70445 (+0.0062); band ±0.05 |
| P3 | w8 extrapolation in [0.81, 0.85], monotone above w4 | RETRACTED 2026-10-09 — measured w8 share 0.75 (375:500), Wilson-95 [0.71024, 0.78595]; frozen gate verdict CAL_OK+REFUTED (evidence/2026-10-08-w8-hazardhold/verdict.json) |
| P4 | frozen class quoted, never computed | PASS — 0.826 at w4 (DW11), window-immune |

**New validation finding.**  The VH chain was validated only at its
terminal (VH2).  P2 checks it at the mid-window points the fit never
gated: it tracks the measured curve within +0.0062 / +0.0062 /
+0.0044 at w2 / w3 / w4 — a coherent small over-prediction, not
noise.  The ratchet account now explains the whole measured window
curve, point by point.

## Curve (as emitted)

| window | measured | chain | tier |
| --- | --- | --- | --- |
| w1 | 0.50325 (232:229) | 0.47863 (snapshot init) | contested |
| w2 | 0.64634 (318:174) | 0.65254 | ratchet-tilting |
| w3 | 0.70445 (348:146) | 0.71067 | ratchet-tilting |
| w4 | 0.73695 (367:131) | 0.74135 (receipt identity) | ratchet-tilting |
| w8 | 0.75 (375:125) REFUTED 2026-10-09 | ~~0.83376~~ extrapolation retracted | — (region 3, trend-alive) |

(The w1 chain value is the fit-range snapshot 112:122 = 0.4787; the
w1 measured point is the full-range census 232:229 = 0.50325 — the
0.025 gap is snapshot sampling, not model error.)

## Falsifier (pre-registered for a future MC arm)

A w8 window arm (BUILD1 Vp-missing, s2, dG=2, fresh seeds, n=500)
whose measured fill share falls outside ±0.05 of 0.834 refutes the
hazard-hold extrapolation.  w2/w3 fresh-seed arms outside ±0.05 of
0.646 / 0.704 would refute the mid-window chain (those points are
already cross-seed stable via the DW9 CAL / CC3 chain).

## Limits

- Basis arm: BUILD1 Vp-missing, site (2,2), dG=2, s2.  The curve is
  an ARM PRICING, not a general kTAM law; other vacancies inherit it
  only through the MARGINAL tier's census semantics.
- w > 4 predictions carry the hazard-hold assumption; the bracket
  quotes the late-hazard Poisson-95 bound, not a fit.
- The frozen class has no window pricing because it has no window
  dependence (measured 0.826 at w4): a window can tilt a marginal
  vacancy but cannot repair first-come.

## Figure (tick 79, 2026-10-08)

`assets/011-window-curve.svg` — deterministic render of this design's
emitted curve by `tools/window_curve_svg.py` (dependency-free SVG;
every number is read from `marginal_window_pricing()`, committed
receipts only — the tick-37 static rule).  It shows the four measured
census points (w1–w4), the chain fit solid through w4 and dashed
beyond it, the w8 hazard-95 bracket, the tier bands, the window-blind
stationary, and the DW11 frozen-persist line.  The w8 point is drawn
open and labelled VERDICT PENDING until the pre-registered falsifier
(queue request ed50c7ba…4daa85) lands; the collection note re-renders
or retires the extrapolated arm per the interpretation map in
`research-log/2026-10-08-w8-hazardhold.md`.  Pinned by
`tests/test_window_curve_svg.py`.

### Figure verdict modes (tick 82, 2026-10-09)

`tools/window_curve_svg.py` now renders the w8 presentation in three
modes: `pending` (default — byte-identical to the tick-79 render), and
the two receipt-driven collection modes.  On a `CAL_OK+HELD` receipt
(`--receipt verdict.json`) the w8 point is drawn CLOSED/measured with
its census label and Wilson 95 bar, the bold pending line replaced by
the measured-verdict line, while the dashed chain arm and hazard-95
bracket remain visible as the prediction they were.  On
`CAL_OK+REFUTED` the beyond-w4 extrapolation, hazard bracket and w8
marker are quarantined out entirely per the pre-registered refutation
action; w1–w4 measured receipts are untouched.  Non-verdictable
receipts are refused (exit 2).  The whole collection-day application —
figure + blog post + research-log addendum, numbers verbatim from the
receipt — is one command: `tools/apply_w8_receipt.py`; only the
designs/011 prose edit stays by hand.  Pinned end-to-end by
`tests/test_apply_w8_receipt.py` (8 tests), including
pending-byte-identity against the committed figure.
