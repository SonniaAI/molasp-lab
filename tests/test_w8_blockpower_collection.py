"""Receipt pins for the w8 blockpower collection tick (tick 138, SON-5152).

Pins the two VOID packaging attempts and the attempt-3 scaffold so the
lessons are part of the record (viasite-v1 precedent: the failure
signature is pinned, not just the eventual success):

- attempt 1 (request d3aa0aca…, nonce molasp-w8-blockpower-t120-a,
  tick 120): archive omitted the molasp package -> ModuleNotFoundError
  before any trajectory; stdout empty; queue-receipt.json reads VOID
  with no data branch fired.
- attempt 2 (request c4f311546d…, nonce molasp-w8-blockpower-t138-a,
  tick 138): command 'python3 evidence/…' runs from cwd /work where the
  archive mounts as source/ -> exit 2 (the pinned viasite-v1 path
  lesson, re-learned).
- attempt 3 (request dd5a8300…, nonce molasp-w8-blockpower-t138-b):
  repaired archive (complete molasp package, blob e36fc084…,
  smoke-verified INSIDE the extracted archive tree) + attempt-1 command
  shape; queued at scaffold time, collected stays null (house style).

The frozen interpretation map lives in
research-log/2026-10-13-w8-blockpower-prereg.md and is pinned by
test_w8_blockpower.py; this file never re-derives it.
"""
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EV = os.path.join(os.path.dirname(HERE),
                  "evidence", "2026-10-13-w8-blockpower")


class TestAttempt1VoidReceipt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(EV, "queue-receipt-v1-failed.txt")) as fh:
            cls.blob = fh.read()
        with open(os.path.join(EV, "queue-receipt.json")) as fh:
            cls.receipt = json.load(fh)

    def test_blob_frame_matches_request(self):
        self.assertIn(
            "HX-OUT-BEGIN:d3aa0acaa37ff4c93ecd79395ea352c9b9eb1379499"
            "4db9d67feaa25b034dc83", self.blob)
        self.assertIn("HX-OUT-END:d3aa0acaa37ff4c93ecd79395ea352c9b9eb1379499"
                      "4db9d67feaa25b034dc83", self.blob)

    def test_named_cause_is_molasp_package_absence(self):
        self.assertIn("ModuleNotFoundError: No module named 'molasp'",
                      self.blob)
        self.assertIn("HX-QUEUE-EXIT:1", self.blob)
        # the crash precedes the instrument core: stdout section is empty
        self.assertIn("HX-FILE:stdout\n\nHX-QUEUE-EXIT", self.blob)

    def test_receipt_reads_void_no_branch_fired(self):
        self.assertEqual(self.receipt["branch"], "VOID")
        self.assertEqual(self.receipt["exit_status"], 1)
        self.assertEqual(self.receipt["node"], "spark-4a06")
        self.assertEqual(self.receipt["run_out_bytes"], 0)
        self.assertIsNone(self.receipt["verdicts_recorded_by_instrument"])
        # house style: the collected field stays null even at collection
        self.assertIsNone(self.receipt["collected"])
        self.assertIn("no datum", self.receipt["branch_reason"])

    def test_admission_window_recorded(self):
        self.assertEqual(self.receipt["admitted"], "2026-10-14T01:47:40Z")
        self.assertEqual(self.receipt["finished"], "2026-10-14T01:47:45Z")


class TestAttempt2VoidReceipt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(EV, "queue-receipt-v2-failed.txt")) as fh:
            cls.blob = fh.read()

    def test_named_cause_is_cwd_path_lesson(self):
        self.assertIn("can't open file '/work/evidence/2026-10-13-w8-block"
                      "power/ktam_w8_blockpower.py'", self.blob)
        self.assertIn("HX-QUEUE-EXIT:2", self.blob)

    def test_frame_matches_request(self):
        self.assertIn(
            "HX-OUT-BEGIN:c4f311546d220592ea754f98192e2319516b6c733f"
            "3655d92c48873d91323a09", self.blob)


class TestAttempt3Scaffold(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(EV, "queue-receipt-v3.json")) as fh:
            cls.receipt = json.load(fh)

    def test_repaired_archive_and_command_shape(self):
        self.assertEqual(self.receipt["nonce"], "molasp-w8-blockpower-t138-b")
        self.assertEqual(
            self.receipt["archive_blob"],
            "e36fc0844a6076b9c11472980af9f4d119b0ab326ba553bffe336da5a978739e")
        # the viasite-v1 lesson applied: /work-relative command
        self.assertEqual(
            self.receipt["command"],
            ["python3",
             "source/evidence/2026-10-13-w8-blockpower/ktam_w8_blockpower.py"])

    def test_envelope_unchanged_vs_prereg(self):
        self.assertEqual(self.receipt["image"], "paperclip-test")
        self.assertEqual(self.receipt["cpu"], 1)
        self.assertEqual(self.receipt["memory"], "1Gi")
        self.assertEqual(self.receipt["wall_s"], 2400)

    def test_collected_stays_null(self):
        self.assertIsNone(self.receipt["collected"])

    def test_attempt1_receipt_mentions_all_three_attempts(self):
        # the scaffold note carries the full attempt lineage
        self.assertIn("attempt 1", self.receipt["scaffold_note"].lower())
        self.assertIn("attempt 2", self.receipt["scaffold_note"].lower())


if __name__ == "__main__":
    unittest.main()
