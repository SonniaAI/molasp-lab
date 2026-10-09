#!/usr/bin/env python3
"""Import the w8 cluster-job result blob into the frozen evidence directory.

The queue client prints the collected pod log (the stored result blob)
on stdout when the request has reached a terminal state:

    python3 /paperclip/instances/metalas-v20/cluster-jobs-client/job_queue.py \
        result --owner <AGENT_ID> <REQUEST_ID> > result.blob

That blob is framed exactly as the client's dump script emits it
(cluster-jobs-client/job_queue.py, manifests() dump + protocol-2
collection regex):

    HX-OUT-BEGIN:<request_id>
    HX-FILE:status
    <status file: exit number + newline>
    <echo blank line>
    HX-FILE:stderr
    <stderr file content>
    <echo blank line>
    HX-FILE:stdout
    <stdout file content>
    <echo blank line>
    HX-QUEUE-EXIT:<exit status>
    HX-OUT-END:<request_id>

This tool verifies the frame against the request id, recovers the
/out/stdout section byte-exactly as run.out (the dumped file minus the
single `echo` newline the frame appends to every section), saves stderr
alongside it, and writes an import manifest with content hashes.

It performs NO interpretation: the verdict chain starts at
tools/collect_w8.py, whose frozen gates remain the only authority.

Known framing limitation (inherited from the queue's own dump format):
a file whose content contains a line starting with `HX-FILE:` would
shift section boundaries.  The w8 instrument emits JSON print lines and
cannot produce such a prefix; the parser trusts the frame at the same
level the client's own collection regex does.

Usage:
  python3 tools/import_queue_result.py result.blob \
      [--request <REQUEST_ID>] \
      [--evidence-root evidence/2026-10-08-w8-hazardhold] [--force]
"""
import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
REQUEST_DEFAULT = "ed50c7baf2d8b935bb118f25758394ddfb04a671e902f39bfa66721b274daa85"
EVIDENCE_DEFAULT = REPO / "evidence" / "2026-10-08-w8-hazardhold"


class ImportRefused(Exception):
    """Raised when the blob cannot be imported verbatim."""


def parse_framed(text, request_id):
    """Return (exit_status, sections) from a framed result blob.

    sections maps file name -> exact dumped file content (the frame's
    per-section `echo` newline stripped).  Refuses on any frame
    mismatch against request_id.
    """
    begin = "HX-OUT-BEGIN:%s\n" % request_id
    if not text.startswith(begin):
        raise ImportRefused("blob does not start with HX-OUT-BEGIN for request %s" % request_id)
    body = text[len(begin):]
    end_re = re.compile(
        r"(?m)^HX-QUEUE-EXIT:(\d+)\r?\nHX-OUT-END:" + re.escape(request_id) + r"\s*\Z"
    )
    end_match = end_re.search(body)
    if not end_match:
        raise ImportRefused("blob frame incomplete: HX-QUEUE-EXIT/HX-OUT-END for request %s not found" % request_id)
    exit_status = int(end_match.group(1))
    core = body[: end_match.start()]
    section_re = re.compile(r"(?m)^HX-FILE:([^\r\n]+)\r?\n")
    matches = list(section_re.finditer(core))
    if not matches:
        raise ImportRefused("no HX-FILE sections inside frame")
    sections = {}
    for index, match in enumerate(matches):
        start = match.end()
        stop = matches[index + 1].start() if index + 1 < len(matches) else len(core)
        payload = core[start:stop]
        if payload.endswith("\n"):
            payload = payload[:-1]
        sections[match.group(1)] = payload
    return exit_status, sections


def _sha256(data):
    return hashlib.sha256(data).hexdigest()


def import_blob(blob_text, request_id, evidence_root, force=False, blob_source=None, stream=None):
    """Import blob_text into evidence_root; returns the manifest dict."""
    if stream is None:
        stream = sys.stdout
    exit_status, sections = parse_framed(blob_text, request_id)
    stdout_text = sections.get("stdout")
    if stdout_text is None:
        raise ImportRefused("no stdout section in frame (files seen: %s)" % sorted(sections))
    if stdout_text == "":
        raise ImportRefused("stdout section is empty — refusing to import an empty run.out")
    stderr_text = sections.get("stderr") or ""

    root = Path(evidence_root)
    run_out_path = root / "run.out"
    manifest_path = root / "run.out.import.json"
    if run_out_path.exists() and not force:
        raise ImportRefused("%s already exists (use --force to re-import)" % run_out_path)

    run_out_data = stdout_text.encode("utf-8")
    stderr_data = stderr_text.encode("utf-8")
    root.mkdir(parents=True, exist_ok=True)
    run_out_path.write_bytes(run_out_data)
    stderr_entry = None
    if stderr_text:
        (root / "run.out.stderr").write_bytes(stderr_data)
        stderr_entry = {"sha256": _sha256(stderr_data), "bytes": len(stderr_data)}
    manifest = {
        "schema": 1,
        "tool": "import_queue_result",
        "request_id": request_id,
        "exit_status": exit_status,
        "imported_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "run_out": {"sha256": _sha256(run_out_data), "bytes": len(run_out_data)},
        "stderr": stderr_entry,
        "blob_source": str(blob_source) if blob_source else None,
        "interpretation": "none — the verdict chain starts at tools/collect_w8.py",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    print("imported %s (%d bytes, sha256 %s)" % (run_out_path, len(run_out_data), manifest["run_out"]["sha256"]), file=stream)
    print("manifest %s" % manifest_path, file=stream)
    if stderr_entry:
        print("stderr saved %s (%d bytes)" % (root / "run.out.stderr", stderr_entry["bytes"]), file=stream)
    print("job exit status: %d" % exit_status, file=stream)
    if exit_status != 0:
        print("WARNING: job exited non-zero — collect_w8.py will likely refuse or VOID; diagnose before applying any receipt", file=stream)
    print("next: python3 tools/collect_w8.py %s --out %s" % (run_out_path, root / "verdict.json"), file=stream)
    print("then: python3 tools/apply_w8_receipt.py %s" % (root / "verdict.json"), file=stream)
    return manifest


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("blob", help="path to the saved output of job_queue.py result")
    ap.add_argument("--request", default=REQUEST_DEFAULT, help="request id the frame must match")
    ap.add_argument("--evidence-root", default=str(EVIDENCE_DEFAULT))
    ap.add_argument("--force", action="store_true", help="allow overwriting an existing run.out")
    args = ap.parse_args(argv)
    try:
        blob_text = Path(args.blob).read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print("refused: blob is not valid UTF-8", file=sys.stderr)
        raise SystemExit(2)
    try:
        import_blob(blob_text, args.request, args.evidence_root, force=args.force, blob_source=args.blob)
    except ImportRefused as error:
        print("refused: %s" % error, file=sys.stderr)
        raise SystemExit(2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
