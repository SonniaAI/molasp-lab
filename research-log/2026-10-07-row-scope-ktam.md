# Row-scope kTAM validation (tick 31, 2026-10-07)

Pre-registered at fb3e08e (tick 30) — the script
`evidence/2026-10-07-row-scope-ktam/ktam_row_scope.py` was committed
BEFORE any MC ran. Job lineage: v1 (nonce `row-scope-v1`, request
`f061d27f…9fe27c`) FAILED with exit 2 — the task command referenced the
script relative to cwd `/work`, but `--archive` sources extract to
`/work/source/` (zero simulation output; stdout empty; k8s still reported
the pod "succeeded" — the real exit code lives in the queue's status
file). v2 (nonce `row-scope-v2`, request `6da45fb7…b0c593`) re-ran the
BYTE-IDENTICAL archive (content hash `a9443602…51a` on both receipts)
with the corrected `/work/source/…` invocation. The pre-registered
script was never modified between attempts; gates stand as registered.

Receipt: `row_scope.out` (8 lines) + `queue-receipt-v1-failed.json` +
`queue-receipt-v2.json`. Job `hxq-6da45fb7e03bf736`, paperclip-test
image (verified), 1 core / 1 GiB / 3600 s cap, ~22 s runtime on
spark-4a06, execution_status 0. Operational lesson: archive task
commands must use `/work/source`-prefixed absolute paths.

## Instrument

kTAM v3 no-mismatch, Gse=9, Gmc=9.5 (dG 0.5), T_read = 400·e^Gmc,
n=500/arm, read-time census (no history). Arms: BUILD1 x {family, row}
x {plain, Vp-missing, L3-missing}. Seed base 80261107, stride 2e7 —
disjoint from the v2-grid block and the vp-residual block.

## Machine verdicts (RS1–RS4, all pre-registered)

- **RS1 FALSIFIED** — row build1 read-lock-squat blocked 0.144
  [gate ≤ 0.02; falsifier ≥ 0.10]. The static "lock hazards {}" reading
  does NOT mean kinetic elimination: with the value-family bonds
  qualified away, Vp still occupies lock site (3,2) in 72/500 terminals
  via a b=1 transient hold, and DBr (3,3) in 72/500. Row scope HALVES
  the squat-block (family 0.27); the b=1 transient layer carries the
  rest.
- **RS2 FALSIFIED** — row Vp-missing STABLE (b≥2) D2T fill 0.162 over
  all terminals [gate ≤ 0.02; falsifier ≥ 0.10]; raw fill 0.44 (the
  expected b=1 transient occupancy). The stable substitution repair
  degrades 5.6x (family stable fill 0.908; strict-pqr fill 0.9202 vs
  v2's 0.901) but is NOT eliminated. The n=8 smoke's warning — a stable
  b=2 hold reconstituted from two b=1 channels — was a real risk class
  and it decides the verdict at n=500. Mechanism attribution at
  trajectory level stays OPEN: this receipt is a read-time census
  without history; the visible co-squat in row Vp-missing is DBr@(3,3)
  (29/500).
- **RS3 CONFIRMED** — (a) row L3-missing misread 0.0 [gate ≤ 0.02]:
  the L2@(3,3) misread channel needs the value-family sharing; with the
  bonds qualified it never fires (family L3: 28/500). (b) row build1
  strict-pqr 0.762 vs family 0.582 (+0.18, comfortably above family −
  0.10): row scope IMPROVES canonical yield — trap relief again (the
  R2/P1 story, now at the scope level).
- **RS4 CALIBRATED** — family build1 blocked 0.27 (v2 ref 0.314, dev
  0.044 ≤ 0.05) and family Vp strict-pqr fill 0.9202 (ref 0.901, dev
  0.019). Fresh seed block, no protocol drift; the comparisons above
  are valid.

## The six arms (n=500 each)

| arm | strict-pqr | blocked | notable |
|---|---|---|---|
| family build1 | 0.582 | 0.270 | squats Vp@(3,2)=109, V0p@(3,1)=62, Vp@(3,3)=64, DBr@(3,3)=53; misread 8 |
| family Vp-missing | 0.852 | 0.064 | D2T stable fill 0.908; strict-pqr fill 0.9202 (392/426) |
| family L3-missing | 0.000 | 0.384 | 486 partial; misread 28 (0.056) |
| row build1 | 0.762 | 0.144 | squats ONLY Vp@(3,2)=72 + DBr@(3,3)=72; misread 0 |
| row Vp-missing | 0.866 | 0.058 | raw D2T fill 0.44, STABLE 0.162; DBr@(3,3)=29 |
| row L3-missing | 0.000 | 0.240 | 500 partial; misread 0 |

## Interpretation

1. **Static hazard-zeroing is not kinetic elimination.** d4/tick-29's
   row-scope table says "lock hazards {}" — true for b≥2 holds, but the
   read-time census shows the b=1 transient layer still blocks 14.4% of
   reads (half the family's 27%). Emit-time guidance must therefore
   report TWO layers: statically stable hazards (b≥2, the current d4
   table) and the b=1 transient class (kinetically ~0.14 read-block at
   this protocol point). The static table alone over-promises.
2. **The repairability/squattability duality goes all the way down.**
   Even with the shared value-family bonds statically qualified away,
   single-bond geometry keeps BOTH sides alive at reduced amplitude:
   the read-cost (0.144) and a stable recombined repair channel
   (0.162). The duality is not purely a property of the glue-sharing
   graph; it survives the knob that removes the sharing.
3. **The knob's honest trade at dG 0.5** (designs/004 revision):
   family = {squat-block 0.27, stable repair 0.908, misread 0.056,
   pqr 0.582}; row = {squat-block 0.144, stable repair 0.162, misread
   0.000, pqr 0.762}. Row scope halves the cost, kills the misread,
   IMPROVES canonical yield, and leaves a 16% repair floor. "Zero
   hazards" was the wrong promise; "half the cost, no misread, better
   yield, degraded repair" is the measured one.

## What this opens

- d4 emit-time layer split (static b≥2 hazards vs b=1 transient class)
  — the natural next compiler-guidance step, numbers now measured.
- Trajectory-level mechanism of the surviving stable channel
  (history-aware rerun of the row arms): is it the smoke's mutual-pair
  class?
- The glue-CLASS boundary (spine/go*/caps/and*/w* relays never
  qualified) remains untested kinetically.
