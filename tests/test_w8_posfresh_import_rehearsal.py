"""Collection rehearsal for the queued w8 position-tagged fresh-window probe.

Tick 113 (SON-5144) preregistered the probe (commit 3e98dc5) and
submitted it to the capped cluster queue: request
bda50c6bf65bb5433500dc7c855593c39727eb0376154b985c5efb386f9a1d66, nonce
molasp-w8-posfresh-t113, paperclip-test 1 cpu / 1 Gi / 2400 s.  The
monitor wake's next action is mechanical: job_queue.py result prints the
framed blob; tools/import_queue_result.py must accept that frame under
the REAL request id, recover run.out byte-exactly, and the collected JSON
must read out against the frozen branch map.  These pins rehearse the
chain end to end so the bounded collection wake cannot burn an attempt
on a framing or parsing surprise.

The rehearsal body is SYNTHETIC and must stay synthetic: the instrument
has no sandbox seed base, so SMOKE=1 executes the real virgin blocks
560261107/580261107 (8 trajectories per arm) — running it here would
burn the blocks on every CI run and void the fresh-window premise.  The
synthetic body mirrors the instrument's output shape only; its numbers
are invented and assert nothing about the world.
"""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import import_queue_result as iqr  # noqa: E402

REQUEST_ID = "bda50c6bf65bb5433500dc7c855593c39727eb0376154b985c5efb386f9a1d66"
JOB = "hxq-bda50c6bf65bb543"
NONCE = "molasp-w8-posfresh-t113"
IMAGE = "paperclip-test"
CPU = 1
MEMORY = "1Gi"
WALL_S = 2400
SUBMITTED_AT = "2026-10-13T17:12:34Z"
FOREIGN_RID = "f" * 64

FROZEN_BRANCHES = (
    "VOID",
    "NO_EVENTS",
    "POSITION_DECLINE_DETECTED",
    "POSITION_DECLINE_NOT_DETECTED",
)

EVIDENCE_DIR = REPO / "evidence" / "2026-10-13-w8-posfresh"
INSTRUMENT = EVIDENCE_DIR / "ktam_w8_posfresh.py"
RECEIPT = EVIDENCE_DIR / "queue-receipt.json"

SYNTHETIC_BODY = json.dumps(
    {
        "label": "W8_POSFRESH",
        "n_cal": 500,
        "n_win": 1000,
        "seed0_cal": 260261107,
        "seed0_u1": 560261107,
        "seed0_u2": 580261107,
        "late_offset": 9000,
        "cal": "CAL_OK",
        "pooled_early": {"x": 1466, "pair_n": 2000},
        "pooled_late": {"x": 1422, "pair_n": 2000},
        "branch": "POSITION_DECLINE_NOT_DETECTED",
        "tests": {"fisher_one_sided_p": 0.062},
    },
    indent=1,
    sort_keys=True,
) + "\n"


def framed(status_file, stdout_file, stderr_file="", rid=REQUEST_ID,
           exit_status=None):
    """Build a blob the same way the queue client's dump script does
    (shape copied from tests/test_import_queue_result.py)."""
    if exit_status is None:
        exit_status = status_file.strip()
    text = "HX-OUT-BEGIN:%s\n" % rid
    text += "HX-FILE:status\n%s\n" % status_file
    text += "HX-FILE:stderr\n%s\n" % stderr_file
    text += "HX-FILE:stdout\n%s\n" % stdout_file
    text += "HX-QUEUE-EXIT:%s\nHX-OUT-END:%s\n" % (exit_status, rid)
    return text


class PosfreshImportRehearsal(unittest.TestCase):
    maxDiff = None

    def test_frame_parses_under_real_request_id(self):
        blob = framed("0\n", SYNTHETIC_BODY)
        exit_status, sections = iqr.parse_framed(blob, REQUEST_ID)
        self.assertEqual(exit_status, 0)
        self.assertEqual(sections["stdout"], SYNTHETIC_BODY)

    def test_import_roundtrip_byte_exact(self):
        blob = framed("0\n", SYNTHETIC_BODY)
        with tempfile.TemporaryDirectory() as tmp:
            manifest = iqr.import_blob(blob, REQUEST_ID, tmp,
                                       blob_source="rehearsal")
            run_out = (Path(tmp) / "run.out").read_bytes()
            self.assertEqual(run_out, SYNTHETIC_BODY.encode("utf-8"))
            self.assertEqual(manifest["request_id"], REQUEST_ID)
            self.assertEqual(manifest["exit_status"], 0)
            self.assertEqual(manifest["run_out"]["sha256"],
                             hashlib.sha256(run_out).hexdigest())
            self.assertEqual(manifest["run_out"]["bytes"], len(run_out))
            self.assertFalse((Path(tmp) / "run.out.stderr").exists())

    def test_import_refuses_foreign_request_id(self):
        """The tool's default --request is the 2026-10-08 hazardhold id;
        collection MUST pass --request explicitly.  A mismatched frame
        refuses before any write."""
        blob = framed("0\n", SYNTHETIC_BODY)
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(iqr.ImportRefused):
                iqr.import_blob(blob, FOREIGN_RID, tmp)
            self.assertFalse((Path(tmp) / "run.out").exists())

    def test_collected_json_reads_against_frozen_branch_map(self):
        payload = json.loads(SYNTHETIC_BODY)
        self.assertIn(payload["branch"], FROZEN_BRANCHES)
        for name in FROZEN_BRANCHES:
            payload_ok = dict(payload, branch=name)
            self.assertIn(json.loads(json.dumps(payload_ok))["branch"],
                          FROZEN_BRANCHES)

    def test_frozen_branch_names_match_instrument(self):
        src = INSTRUMENT.read_text(encoding="utf-8")
        for name in FROZEN_BRANCHES:
            self.assertIn('"%s"' % name, src)

    def test_queue_receipt_metadata_pinned(self):
        """The receipt must carry the real request metadata in both
        scaffold and collected states; house style keeps collected null
        either way (see 2026-10-13-w8-arm6)."""
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        self.assertEqual(receipt["request_id"], REQUEST_ID)
        self.assertEqual(receipt["job"], JOB)
        self.assertEqual(receipt["nonce"], NONCE)
        self.assertEqual(receipt["image"], IMAGE)
        self.assertEqual(receipt["cpu"], CPU)
        self.assertEqual(receipt["memory"], MEMORY)
        self.assertEqual(receipt["wall_s"], WALL_S)
        self.assertEqual(receipt["submitted_at"], SUBMITTED_AT)
        self.assertIsNone(receipt["collected"])
        if "exit_status" in receipt:  # filled at collection
            self.assertIsInstance(receipt["exit_status"], int)
            sha = receipt.get("run_out_sha256")
            self.assertIsInstance(sha, str)
            self.assertRegex(sha, r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
