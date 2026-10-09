# designs/011 prose branches — pre-drafted BEFORE the w8 data exists (tick 83)

Companion to the executable pre-registration chain
(`tools/collect_w8.py` → `tools/apply_w8_receipt.py`).  The apply tool
writes figure + blog post + collection note; the single deliberate hand
step it names is the designs/011 prose edit.  This file pre-drafts that
edit for both milestone branches, committed while queue request
`ed50c7ba…4daa85` is still unadmitted, so the wording cannot be chosen
after seeing the numbers — same discipline as the frozen gates.

Rules:

- Fill ONLY from the verdict receipt (`verdict.json`).  Never a number
  from memory.  Receipt fields these branches read — the same field set
  `tools/apply_w8_receipt.py` reads: `fresh_terminal_share`,
  `dev_vs_pred_w8`, `fresh_w8_wilson95` (list: lo, hi),
  `fresh_terminal_census` (D2T / L2 / other), `n_per_range`.
- Placeholder map (used below): {share} ← fresh_terminal_share;
  {dev} ← dev_vs_pred_w8; {lo} {hi} ← fresh_w8_wilson95[0] / [1];
  {d2t} {l2} ← fresh_terminal_census D2T / L2; {n} ← n_per_range;
  {date} ← collection date.
- Apply exactly ONE branch; the other stays unused.
- The receipt's cross_check must read `ok` (the apply tool already
  refuses otherwise; the hand step inherits the same gate).
- Pinned by `tests/test_w8_prose_branches.py`.

## Branch CAL_OK+HELD

Action (receipt): "w8 tier stands on a measured receipt: designs/011 P3
point 0.834 is now cross-seed measured within the pre-registered
±0.05 band".

- **Curve table, w8 row** — replace
  `| w8 | — | 0.83376 [0.81585 hazard-95] | ratchet-tilted |`
  with
  `| w8 | {share} ({d2t}:{l2}) | 0.83376 [0.81585 hazard-95] | ratchet-tilted (measured {date}, Wilson 95 [{lo}, {hi}]) |`
- **Checks table** — add after the P4 row:
  `| P5 | w8 falsifier arm: measured within ±0.05 of 0.83376 | PASS — {share} vs 0.83376 (dev {dev}); Wilson 95 [{lo}, {hi}] |`
- **Falsifier section** — append:
  `Outcome (collected {date}, request ed50c7ba…4daa85): HELD.  Measured fill share {share} ({d2t}:{l2} fresh pair terminals, n={n} per range), dev {dev} from the 0.83376 chain point — inside the pre-registered ±0.05 band.  The w8 tier now stands on a measured receipt; the hazard-95 bracket remains a sensitivity arm, not a fit.`
- **Limits bullet** — replace
  `- w > 4 predictions carry the hazard-hold assumption; the bracket quotes the late-hazard Poisson-95 bound, not a fit.`
  with
  `- w > 4 predictions carried the hazard-hold assumption until the w8 falsifier landed ({date}, HELD within ±0.05); w > 8 still carries it. The bracket quotes the late-hazard Poisson-95 bound, not a fit.`
- **Figure section** — replace the sentence
  `The w8 point is drawn open and labelled VERDICT PENDING until the pre-registered falsifier (queue request ed50c7ba…4daa85) lands; the collection note re-renders or retires the extrapolated arm per the interpretation map in `research-log/2026-10-08-w8-hazardhold.md`.`
  with
  `The w8 point was drawn open and labelled VERDICT PENDING until the pre-registered falsifier (queue request ed50c7ba…4daa85) landed ({date}, HELD); it is now rendered CLOSED/measured with its Wilson 95 bar by the collection re-render (tools/window_curve_svg.py held mode).`

## Branch CAL_OK+REFUTED

Actions (receipt): "retract the designs/011 w8 tier entry
(pre-registered refutation)"; "quarantine the extrapolated arm beyond
w4 in the figure and designs/011".

- **Curve table, w8 row** — replace
  `| w8 | — | 0.83376 [0.81585 hazard-95] | ratchet-tilted |`
  with
  `| w8 | {share} (measured {date}) | 0.83376 [0.81585 hazard-95] — RETRACTED | refuted |`
- **Immediately after the curve table's parenthetical note** — insert:
  `Retraction ({date}).  The pre-registered w8 falsifier fired: measured fill share {share} ({d2t}:{l2}, n={n} per range), dev {dev} from the 0.83376 chain point — outside the ±0.05 band.  The w8 tier entry and the beyond-w4 extrapolation are retracted; the chain is measured through w4 only.`
- **Checks table, P3 row** — replace
  `| P3 | w8 extrapolation in [0.81, 0.85], monotone above w4 | PASS — 0.83376 point; hazard-95 arm 0.81585; stationary ceiling 0.97865 |`
  with
  `| P3 | w8 extrapolation in [0.81, 0.85], monotone above w4 | RETRACTED ({date}) — the extrapolated 0.83376 point failed its pre-registered falsifier (measured {share}, dev {dev}) |`
- **Falsifier section** — append:
  `Outcome (collected {date}, request ed50c7ba…4daa85): REFUTED.  Measured fill share {share} ({d2t}:{l2}, n={n} per range), dev {dev} from 0.834 — outside the pre-registered ±0.05 band.  Beyond-w4 predictions are quarantined in figure and here; no pricing above w4.`
- **Limits bullet** — replace the same `w > 4 predictions carry…` bullet with
  `- w > 4 predictions are quarantined: the hazard-hold extrapolation was falsified at w8 ({date}, measured {share}); the curve prices w1–w4 only.`
- **Figure section** — replace the same VERDICT-PENDING sentence with
  `The w8 point was drawn open and labelled VERDICT PENDING until the pre-registered falsifier (queue request ed50c7ba…4daa85) landed ({date}, REFUTED); the collection re-render quarantines the beyond-w4 extrapolation, hazard bracket and w8 marker out entirely (tools/window_curve_svg.py refuted mode), leaving w1–w4 measured receipts untouched.`

## Non-verdictable branches

VOID / NO_EVENTS / SMOKE / FORCED-DISAGREEMENT: NO designs/011 edit of
any kind — the receipt action lists say diagnose first, and the apply
tool refuses them with zero files written.  The branches above apply
only to the two milestone receipts with cross_check `ok`.
