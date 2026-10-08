# Tick 47 waiter collected: v1 FAILED on a missing archive entrypoint; corrected v2 submitted and validated

Date: 2026-10-08, wake 10:00:49Z (SON-4854 tick 63, run 7273e4e1).
Anchors: queue receipts quoted verbatim below; no anticipated times.

## 1. Collection outcome (first duty)

The tick-47 waiter — request
`9e79de4389423dfbdb8d5313afcc7603a1abc8bf5097743157b7ad15ff58e145`
(nonce `dg2win-l3vac-v1`, source issue e22a069e / SON-4821, submitted
2026-10-07T18:03:57Z) — was admitted 2026-10-08T08:12:06.88Z after
**14 h 08 m** in queue and finished 08:12:12.36Z (**~5.5 s** of
runtime). State: **failed**, `execution_status: 2`.

Raw result (verbatim):

```
HX-FILE:status
2

HX-FILE:stderr
python3: can't open file '/work/source/evidence/2026-10-07-dg2-window-l3vac/ktam_dg2_window_l3.py': [Errno 2] No such file or directory

HX-FILE:stdout

HX-QUEUE-EXIT:2
```

Queue-level wrapper bookkeeping: pod `hxq-9e79de438942dfb-7rkhm`
phase Succeeded (container `attempt` exitCode 0, 08:12:07Z →
08:12:07Z); node spark-4a06; image
`localhost:5000/paperclip@sha256:323d04c2…2fdd` (verified). The
pod "Succeeded" only because the wrapper completed; the payload
truth is `HX-QUEUE-EXIT: 2`. **No science was produced by v1.**

## 2. Root cause

The v1 request command was correct for the runtime layout —
`["python3", "source/evidence/2026-10-07-dg2-window-l3vac/ktam_dg2_window_l3.py"]`
resolves from cwd `/work` against the mount `/work/source`, which the
stderr confirms. The **archive content** was wrong: v1's blob
`2f4b900ee57b42b62c536087006417c4bf9d7a1ec53e73e236171d12726e488c`
did not contain the entrypoint at all — python3 failed before the
script's first line.

Dependency analysis (after the fact, from the script's own sys.path
shim at lines 73–80) shows the v1 archive was doubly unrunnable: the
script imports `tiles_and.BUILD1` and `tiles_death.build_missing_species`
from sibling evidence dirs (`2026-10-06-body-conjunction-builds/`,
`2026-10-06-structural-death/`) and `canonical_assembly` /
`matched_strength` from `molasp.offchannel`, none of which the v1
blob is believed to have carried.

## 3. Fix: validated-archive method + v2 submission

v2 archive built from the committed tree at HEAD `2344928` with the
script's full import closure (11 files): the entrypoint + `collect.py`,
both sibling tile modules, and the whole `molasp` package. Blob:
`bbe3aba44feeb6a3a09fb2735ea84f54fd0cf9bf57fd32a404144328ce6468dc`
(differs from v1's, consistent with the missing-content diagnosis).

**Pre-submission validation (new standing rule):** extracted the exact
tarball to a clean directory and ran `SMOKE=1 python3
evidence/2026-10-07-dg2-window-l3vac/ktam_dg2_window_l3.py` from the
extraction root (mimicking `/work`): exit 0, all four per-arm JSON
records, the `VERDICTS {...}` line, stderr empty. The n=8 smoke
verdicts are instrument-check only — NOT results; gates stay verbatim
per the tick-43 lesson.

v2 receipt: request
`5a243215b0ff75eabba16a69323842d5e0fa5c5313f47d52ca6766e57ff1778e`
(nonce `dg2win-l3vac-v2`, source issue f1ef926d / SON-4854), created
2026-10-08T10:05:02.97Z, admitted 10:05:03.47Z (instant — queue was
free), **state: running** at the ~10:06Z probe. Same resources as
pre-registered: 1 CPU, 1 GiB, wall 1800 s, image paperclip-test.

## 4. Lessons (durable)

- **Smoke every archive before submission.** Queue latency cannot
  repair a broken payload: 14 h of waiting bought a 5-second failure.
  A clean-extraction smoke run costs seconds and would have caught
  this at tick 47.
- **Pod-Succeeded ≠ job success.** The queue admits and the pod
  completes even when the payload exits 2; `HX-QUEUE-EXIT` and the
  result files are the only payload truth. Collection must read them,
  not trust `execution_status` alone at the k8s layer.

## 5. Next tick

1. FIRST DUTY: probe
   `5a243215b0ff75eabba16a69323842d5e0fa5c5313f47d52ca6766e57ff1778e`;
   on completion run `collect.py run.out` (mismatch guard) and land
   the collection commit with pins; the DW8–DW11 / LV1–LV2 verdicts
   at n=500 are the first real readout of the dG-2 window question.
2. If still queued/running past wall: no resubmission; re-probe next
   tick (wall 1800 s bounds the run itself).
3. Science backlog unchanged: n=6+ build survey / offchannel kinetic
   receipt beyond row 4 (post stage-7 closure); related-work sweep
   due.

Tick disclosure: no compiler/design step advanced this tick; the
durable product is the collection forensics, the corrected and
pre-validated v2 request, and the two durable lessons above.
