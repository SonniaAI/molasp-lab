"""Pins for the COLLECTED W8 blockpower arbitration verdict (tick 143, 2026-10-21).

The frozen map (research-log/2026-10-13-w8-blockpower-prereg.md) is the
only authority; these tests verify the collected datum against it:
CAL identity, floor counts, the exact one-sided Fisher p recomputed
from raw pooled counts, the emitted branch, the VERDICTS tail line,
the frozen-direction (no post-hoc flip) guard, and receipt/record
agreement. Nothing here re-derives or extends the map.
"""
import hashlib
import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.w8_blockpower_oc import fisher_one_sided_greater  # noqa: E402

EV = REPO / "evidence" / "2026-10-13-w8-blockpower"
RUN_OUT = EV / "run.out"
RUN_OUT_SHA = "e6335756523f51193bd097a04df3e37e91459364976d33196d08623f4b614d17"
BLOB_SHA = "6b3929011321422e8edb5356e1c6947d35e2059d940ab3dff1a3c7287f9e6c1e"
REQUEST_ID = "dd5a8300de1fc0ffbe3a7464a6a96e220294a46c22e1731cc91640eae607d6a5"


def _load():
    text = RUN_OUT.read_text()
    obj, end = json.JSONDecoder().raw_decode(text)
    return obj, text[end:].strip()


class TestW8BlockpowerCollectedDatum(unittest.TestCase):
    def test_run_out_imported_verbatim(self):
        self.assertTrue(RUN_OUT.exists(), "run.out must be present at collection")
        self.assertEqual(hashlib.sha256(RUN_OUT.read_bytes()).hexdigest(), RUN_OUT_SHA)
        manifest = json.loads((EV / "run.out.import.json").read_text())
        self.assertEqual(manifest["request_id"], REQUEST_ID)
        self.assertEqual(manifest["run_out_sha256"], RUN_OUT_SHA)

    def test_cal_identity_tenth_consecutive_run(self):
        run, _ = _load()
        self.assertEqual(run["cal"], "CAL_OK")
        self.assertEqual(run["cal_mid_w4"]["D2T"], 367)
        self.assertEqual(run["cal_mid_w4"]["L2"], 131)
        self.assertEqual(run["cal_mid_w4"]["other"], 2)

    def test_floor_did_not_fire(self):
        run, _ = _load()
        self.assertGreaterEqual(run["pooled_gap"]["pair_n"], 3400)
        self.assertGreaterEqual(run["pooled_a6"]["pair_n"], 3400)

    def test_exact_fisher_recompute_matches_instrument(self):
        run, _ = _load()
        pg, pa = run["pooled_gap"], run["pooled_a6"]
        p = fisher_one_sided_greater(pg["x"], pg["pair_n"], pa["x"], pa["pair_n"])
        self.assertLessEqual(abs(p - run["tests"]["p_fisher_one_sided"]), 1e-9)
        self.assertGreater(p, 0.05)  # frozen branch condition

    def test_branch_is_not_detected(self):
        run, _ = _load()
        self.assertEqual(run["branch"], "BLOCK_MECHANISM_NOT_DETECTED")

    def test_verdicts_tail_line_matches_branch(self):
        _, tail = _load()
        self.assertIn('{"CAL": "CAL_OK", "PROBE": "BLOCK_MECHANISM_NOT_DETECTED"}', tail)
        self.assertTrue(tail.rstrip().endswith(
            'VERDICTS {"CAL": "CAL_OK", "PROBE": "BLOCK_MECHANISM_NOT_DETECTED"}'))

    def test_frozen_direction_no_post_hoc_flip(self):
        # Direction was frozen GAP > A6; the realized difference is
        # reverse and stays in descriptives only (prereg boundary).
        run, _ = _load()
        self.assertLess(run["observed_delta"], 0.0)
        self.assertEqual(run["tests"]["share_gap"], run["pooled_gap"]["x"] / run["pooled_gap"]["pair_n"])
        self.assertEqual(run["tests"]["share_a6"], run["pooled_a6"]["x"] / run["pooled_a6"]["pair_n"])

    def test_descriptives_present_for_matched_windows(self):
        run, _ = _load()
        d = run["descriptive"]
        self.assertEqual(len(d["gap_subwindows"]), 8)
        self.assertEqual(len(d["a6_subwindows"]), 8)
        self.assertLess(d["matched_w1_delta"], 0.0)
        self.assertLess(d["matched_w2_delta"], 0.0)


class TestW8BlockpowerReceiptV3(unittest.TestCase):
    def test_receipt_matches_collected_artifacts(self):
        r = json.loads((EV / "queue-receipt-v3.json").read_text())
        self.assertEqual(r["request_id"], REQUEST_ID)
        self.assertEqual(r["nonce"], "molasp-w8-blockpower-t138-b")
        self.assertEqual(r["attempt"], 3)
        self.assertEqual(r["job"], "hxq-dd5a8300de1fc0ff")
        self.assertEqual(r["pod"], "hxq-dd5a8300de1fc0ff-2mx8r")
        self.assertEqual(r["node"], "spark-4a06")
        self.assertEqual(r["exit_status"], 0)
        self.assertEqual(r["admitted"], "2026-10-14T06:08:09.844Z")
        self.assertEqual(r["finished"], "2026-10-14T06:10:56.754Z")
        self.assertEqual(r["result_blob_sha256"], BLOB_SHA)
        self.assertEqual(r["run_out_sha256"], RUN_OUT_SHA)
        self.assertIsNone(r["collected"])  # house style
        v = r["verdicts_recorded_by_instrument"]
        self.assertEqual(v["branch"], "BLOCK_MECHANISM_NOT_DETECTED")
        self.assertEqual(v["cal"], "CAL_OK")
        self.assertEqual(v["pooled_gap"], {"x": 2571, "pair_n": 3559, "share": 0.7223939308794606})
        self.assertEqual(v["pooled_a6"], {"x": 2659, "pair_n": 3557, "share": 0.7475400618498735})

    def test_receipt_run_out_consistency(self):
        r = json.loads((EV / "queue-receipt-v3.json").read_text())
        run, _ = _load()
        self.assertEqual(
            r["verdicts_recorded_by_instrument"]["p_fisher_one_sided"],
            run["tests"]["p_fisher_one_sided"])
        self.assertEqual(
            r["verdicts_recorded_by_instrument"]["observed_delta"],
            run["observed_delta"])


if __name__ == "__main__":
    unittest.main()
