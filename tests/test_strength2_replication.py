"""Replication receipt pin for the tick-38 strength-2 study.

Two loop runs adopted the same 63d12d9 pre-registration within the
same minute and each submitted a queue job. This pins the second
lineage (request 36d7d83c…1692) and the fact that both lineages
produced the identical strength2.out — the deterministic-seed
protocol making the duplication a replication, not a conflict.
"""
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EV = os.path.join(os.path.dirname(HERE), "evidence",
                  "2026-10-07-strength2-lock")
OUT = os.path.join(EV, "strength2.out")
PRIMARY = os.path.join(EV, "queue-receipt.json")
REPLICATION = os.path.join(EV, "queue-receipt-replication.json")


class Strength2Replication(unittest.TestCase):
    def test_files_exist(self):
        self.assertTrue(os.path.exists(PRIMARY))
        self.assertTrue(os.path.exists(REPLICATION))

    def test_two_independent_queue_lineages(self):
        with open(PRIMARY) as fh:
            primary = fh.read()
        with open(REPLICATION) as fh:
            rep = json.load(fh)
        # primary receipt is the raw HX dump carrying its own request
        self.assertIn("2791e8805defef754a40597e91136d9d0f4f27939207"
                      "1352f51622fd422c1122", primary)
        self.assertEqual(rep["id"],
                         "36d7d83ce0c77896a00a5b0f06f02cf6353e3a51fd2"
                         "64c4facdaf43141781692")
        self.assertNotEqual(rep["id"][:16], primary[:16])

    def test_replication_lineage_pins(self):
        with open(REPLICATION) as fh:
            rep = json.load(fh)
        self.assertEqual(rep["archive_blob"],
                         "9c7e7a521ad8bcefa3e7faa88642cad6db026fe4"
                         "6259f914b075082482c4ae5e")
        self.assertEqual(rep["pre_registration_commit"],
                         "63d12d9c1de02e4797d34f776ed627796b8745d0")
        self.assertEqual(rep["nonce"], "strength2-v1")
        self.assertEqual(rep["execution_status"], 0)
        self.assertEqual(rep["state"], "complete")

    def test_shared_output_pinned_by_both(self):
        # one .out serves both receipts; the replication receipt
        # records the byte-identical comparison explicitly
        self.assertTrue(os.path.exists(OUT))
        with open(REPLICATION) as fh:
            rep = json.load(fh)
        self.assertIn("IDENTICAL", rep["collection"])


if __name__ == "__main__":
    unittest.main()
