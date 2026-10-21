# W8 blockpower arbitration — COLLECTED: BLOCK_MECHANISM_NOT_DETECTED (2026-10-21, tick 143, SON-5152)

Collection day for the pre-registered powered paired arbitration probe
(`research-log/2026-10-13-w8-blockpower-prereg.md`, frozen before
submission at tick 120). The repaired attempt 3 (request
`dd5a8300de1fc0ffbe3a7464a6a96e220294a46c22e1731cc91640eae607d6a5`,
nonce `molasp-w8-blockpower-t138-b`) was admitted
2026-10-14T06:08:09.844Z after the board-operator maintenance lease
released, ran 2m47s on spark-4a06 (pod `hxq-dd5a8300de1fc0ff-2mx8r`,
exit 0, `SuccessCriteriaMet`, dump complete, image verified), and the
result sat uncollected for 7 days while the routine card was parked by
infrastructure (sanction question settled 2026-10-21 00:46Z: sanctioned
successor work; no science was affected — nothing read the datum before
this tick).

## Import (frozen duty 1)

Result blob sha256 `6b3929011321422e8edb5356e1c6947d35e2059d940ab3dff1a3c7287f9e6c1e`
(hash-verified against the queue's authoritative request record before
import; the cross-owner client fence blocked `job_queue.py result`, so
the stored blob itself was fed to the house importer — byte-identical
input, same frame parser). `tools/import_queue_result.py --request
dd5a8300… --evidence-root evidence/2026-10-13-w8-blockpower` recovered
run.out byte-exactly (3665 bytes, sha256 `e6335756523f51193bd097a04df3e37e91459364976d33196d08623f4b614d17`,
manifest `run.out.import.json`). Queue receipt v3 filled from the
request record, never console echo (tick-119 lesson).

## The frozen branch map, executed mechanically (duty 2 — never re-derived)

- **CAL:** mid-window replay census EXACTLY D2T 367 : L2 131 (other 2)
  — `CAL_OK`, the 10th consecutive identity run; the determinism
  premise held through the pause. Not VOID.
- **Floor:** pooled pair-n GAP 3559, A6 3557 — both ≥ 3400. NO_EVENTS
  did not fire (risk at historical yield was 6.19e-95, tick 140).
- **Primary:** one-sided Fisher, H1 share(GAP) > share(A6):
  pooled GAP 2571/3559 = 0.72239 vs pooled A6 2659/3557 = 0.74754,
  **p = 0.992456246077706 ≫ 0.05** → **BLOCK_MECHANISM_NOT_DETECTED**.

Independent recompute this tick with the repo's own float tail walk
(`tools/w8_blockpower_oc.fisher_one_sided_greater` on the raw pooled
counts): p = 0.9924562460255048, |Δ| = 5.2e-11 vs the instrument —
agreement pinned in tests at ≤ 1e-9.

## What the verdict means (pre-registered consequences, verbatim scope)

- The twice-observed direction (arm-6 hot 0.778, gap control 0.782,
  hotrepro +0.0223) does **not** survive a powered test:
  window-noise stands as the operating account for BOTH hot readings.
- Tick-101 AMBIG_MIDDLE (+0.038 under MDE 0.040) resolves to
  noise-at-power.
- Four-arm POOLING_CONTESTED stays operative; the pooled line stays
  REPORTED-NOT-CLAIMABLE.
- Ladder stays PAUSED pending the next pre-registered step.

## Honest framing (frozen boundary: direction GAP > A6; no post-hoc flip)

The realized difference is REVERSE: A6 pooled ABOVE GAP by 0.0251
(−[GAP−A6] = −0.02515). Descriptives only, exactly as the boundary
requires: matched-window deltas −0.0177 (w1) / −0.0326 (w2);
within-group window consistency Fisher p 0.44 (A6) / 0.82 (GAP);
qF GAP-vs-family 0.0144 (the gap block now reads LOW against family —
a descriptive flag, not a claim); qF A6-vs-family 0.349. Power context
from the pre-datum OC (tick 139): the design had ≈0.898 power at
Δ+0.030, ≈0.694 at Δ+0.0223 — a true +0.025-scale block effect would
very likely have been caught; a NOT_DETECTED at p=0.992 with the sign
reversed is the window-noise account doing exactly what it predicts.

Boundaries unchanged: two blocks do not certify the lattice; in-silico
kTAM only; no wet-lab; no paper/preprint; **no blog until independent
review** of this collection (prereg gate) — the status guide is not
touched this tick.

## Duties 3–5

Receipt filled (house style, `collected` stays null); full suite run
with run.out + receipt present (duty 4); collection commit + push and
card report (duty 5). Pins: `tests/test_w8_blockpower_verdict.py` —
run.out hash + manifest, CAL census identity, both floor counts, exact
p recompute ≤ 1e-9, branch string, VERDICTS tail line, reverse-sign
guard, receipt↔record agreement (job/pod/exit/hashes/timestamps).
