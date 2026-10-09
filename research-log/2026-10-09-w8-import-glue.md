# 2026-10-09 — w8 collection import glue: queue result blob -> run.out (tick 84)

## What

`tools/import_queue_result.py` closes the last manual gap between the
cluster queue and the pre-registered w8 collection chain.  The queue
client prints the stored pod-log blob on stdout:

    python3 /paperclip/instances/metalas-v20/cluster-jobs-client/job_queue.py \
        result --owner <AGENT_ID> <REQUEST_ID> > result.blob

The tool parses the protocol-2 frame — `HX-OUT-BEGIN:<request_id>`,
one `HX-FILE:<name>` section per /out file (glob order status,
stderr, stdout; each section = dumped file content + one `echo`
newline), then `HX-QUEUE-EXIT:<exit>` and `HX-OUT-END:<request_id>` —
and recovers the /out/stdout section BYTE-EXACTLY as `run.out`
(content minus that one frame newline), saves stderr alongside as
`run.out.stderr`, and writes `run.out.import.json` with sha256, byte
count, exit status and request id.

The frame format is pinned from the client SOURCE
(cluster-jobs-client/job_queue.py: the `manifests()` dump script and
the `collect()` protocol-2 completion regex), committed BEFORE any
real blob exists — same discipline as the rest of the chain.  It is
not reverse-engineered from a live result.

## Discipline

- Import performs NO interpretation.  The frozen CAL/W8 gates live in
  `tools/collect_w8.py` and remain the only authority.
- Refusals (all before any file write unless noted): frame mismatch
  against the request id, missing/empty stdout section, non-UTF-8
  blob; existing `run.out` refuses without `--force` (overwrite is
  the only post-check write path).
- A non-zero job exit still imports — flagged in the manifest and
  warned on stdout — because crash output is diagnosis evidence; the
  collector will then refuse or VOID on its own gates.
- Known framing limitation (inherited from the queue's own dump
  format): a line starting `HX-FILE:` inside file content would shift
  section boundaries.  The w8 instrument emits JSON print lines and
  cannot produce that prefix; the parser trusts the frame at exactly
  the level the client's own collection regex does.

## Collection day — single chain, zero decisions left

1. `python3 job_queue.py result --owner <AGENT_ID> ed50c7ba…4daa85 > /tmp/result.blob`
2. `python3 tools/import_queue_result.py /tmp/result.blob`
3. `python3 tools/collect_w8.py evidence/2026-10-08-w8-hazardhold/run.out --out evidence/2026-10-08-w8-hazardhold/verdict.json`
4. `python3 tools/apply_w8_receipt.py evidence/2026-10-08-w8-hazardhold/verdict.json`
5. Paste the matching pre-drafted prose branch
   (research-log/2026-10-09-w8-prose-branches.md) into designs/011,
   filling receipt numbers only.

## Pins

8 tests in `tests/test_import_queue_result.py`: byte-exact roundtrip
with and without a trailing newline in the dumped stdout; truncated
frame refused with zero writes; wrong request id refused; empty
stdout refused before any write; no-overwrite without `--force` /
overwrite with it; manifest sha256/bytes recomputed independently in
the test; non-zero exit flagged in the manifest and warned.

Suite verbatim: `Ran 520 tests in 3.091s / OK (skipped=1)` = 512 + 8.
