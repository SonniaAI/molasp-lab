"""Pins for tools/import_queue_result.py — the result-blob -> run.out glue.

The framed fixtures below mirror the queue client's dump concatenation
(cluster-jobs-client/job_queue.py manifests()): for each file in /out/*
(glob order: status, stderr, stdout) the dump emits

    HX-FILE:<name>\\n<file content>\\n          (echo adds the last newline)

then `HX-QUEUE-EXIT:<status>\\nHX-OUT-END:<id>\\n`.  Recovery must be
byte-exact: run.out equals the dumped stdout file, no more, no less.
"""
import contextlib
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import import_queue_result as iqr  # noqa: E402

RID = "ed50c7baf2d8b935bb118f25758394ddfb04a671e902f39bfa66721b274daa85"
OTHER_RID = "f" * 64


def framed(status_file, stdout_file, stderr_file="", rid=RID, exit_status=None):
    """Build a blob the same way the client's dump script does."""
    if exit_status is None:
        exit_status = status_file.strip()
    text = "HX-OUT-BEGIN:%s\n" % rid
    text += "HX-FILE:status\n%s\n" % status_file
    text += "HX-FILE:stderr\n%s\n" % stderr_file
    text += "HX-FILE:stdout\n%s\n" % stdout_file
    text += "HX-QUEUE-EXIT:%s\nHX-OUT-END:%s\n" % (exit_status, rid)
    return text


class ParseFramedTests(unittest.TestCase):
    def test_roundtrip_stdout_exact_bytes(self):
        stdout = 'VERDICTS {"cal": "CAL_OK", "w8": "HELD"}\n{"n": 500}\n'
        exit_status, sections = iqr.parse_framed(framed("0\n", stdout), RID)
        self.assertEqual(exit_status, 0)
        self.assertEqual(sections["stdout"], stdout)
        self.assertEqual(sections["status"], "0\n")

    def test_roundtrip_stdout_without_trailing_newline(self):
        stdout = "no trailing newline"
        _, sections = iqr.parse_framed(framed("0\n", stdout), RID)
        self.assertEqual(sections["stdout"], stdout)

    def test_frame_without_end_marker_refused(self):
        blob = framed("0\n", "out\n")
        with self.assertRaises(iqr.ImportRefused):
            iqr.parse_framed(blob[: blob.index("HX-OUT-END")], RID)

    def test_wrong_request_id_refused(self):
        with self.assertRaises(iqr.ImportRefused):
            iqr.parse_framed(framed("0\n", "out\n", rid=OTHER_RID), RID)


class ImportTests(unittest.TestCase):
    def _run(self, blob_text, force=False):
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "evidence"
            with contextlib.redirect_stdout(out):
                iqr.import_blob(blob_text, RID, root, force=force, blob_source="result.blob")
            result = {
                "run_out": (root / "run.out").read_text(),
                "stderr": (root / "run.out.stderr").read_text() if (root / "run.out.stderr").exists() else None,
                "manifest": json.loads((root / "run.out.import.json").read_text()),
            }
        return result, out.getvalue()

    def test_import_writes_runout_and_manifest(self):
        stdout = 'VERDICTS {"cal": "CAL_OK"}\nfinal line\n'
        result, printed = self._run(framed("0\n", stdout, "warn line\n"))
        self.assertEqual(result["run_out"], stdout)
        self.assertEqual(result["stderr"], "warn line\n")
        data = stdout.encode("utf-8")
        manifest = result["manifest"]
        self.assertEqual(manifest["run_out"], {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
        self.assertEqual(manifest["stderr"]["sha256"], hashlib.sha256(b"warn line\n").hexdigest())
        self.assertEqual(manifest["request_id"], RID)
        self.assertEqual(manifest["exit_status"], 0)
        self.assertIn("collect_w8.py", printed)
        self.assertNotIn("WARNING", printed)

    def test_import_refuses_empty_stdout_before_any_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "evidence"
            with self.assertRaises(iqr.ImportRefused):
                iqr.import_blob(framed("0\n", ""), RID, root)
            self.assertFalse((root / "run.out").exists())

    def test_import_refuses_overwrite_without_force(self):
        stdout_a, stdout_b = "first\n", "second\n"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "evidence"
            iqr.import_blob(framed("0\n", stdout_a), RID, root)
            with self.assertRaises(iqr.ImportRefused):
                iqr.import_blob(framed("0\n", stdout_b), RID, root)
            self.assertEqual((root / "run.out").read_text(), stdout_a)
            iqr.import_blob(framed("0\n", stdout_b), RID, root, force=True)
            self.assertEqual((root / "run.out").read_text(), stdout_b)

    def test_nonzero_exit_imports_with_flag_and_warning(self):
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "evidence"
            with contextlib.redirect_stdout(out):
                iqr.import_blob(framed("1\n", "crash\n", exit_status=1), RID, root)
            manifest = json.loads((root / "run.out.import.json").read_text())
            run_out = (root / "run.out").read_text()
        self.assertEqual(manifest["exit_status"], 1)
        self.assertEqual(run_out, "crash\n")
        self.assertIn("non-zero", out.getvalue())


if __name__ == "__main__":
    unittest.main()
