"""Pins for the w8 Branch A dispersion gate execution (tick 119, SON-5152).

The frozen stage-2 plan (1dd0e8b) Branch A step 1 gates every pooled
claim on the corrected four-arm pool at 1235/1652. The gate reads
POOLING_CONTESTED (min_exact_p 0.0293258, driver arm-6), so BOTH
pooled verdict surfaces recorded at tick 118 — policy VERDICT-READY
and atlas REFUTED-low — are unclaimable, and the dispute closes by the
frozen boundary route (pooled line REPORTED-NOT-CLAIMABLE, tick-101
AMBIG_MIDDLE stands, stage-2 steps 2-4 do not activate). These pins
freeze that closure, the arm provenance, and the posfresh queue-receipt
job-id correction (transcription truncation caught by hosted CI on
ab1ece7; authoritative id from the queue request record).
"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.w8_dispersion_receipt import receipt  # noqa: E402

# Corrected four-arm pool, verbatim from the committed tick-99 evidence
# (references block + arm-6/arm-7 terminal counts). Order: arm3, arm4,
# arm6, arm7.
GATE_ARMS = [(375, 500), (106, 153), (389, 500), (365, 499)]
EXPECTED_PER_ARM_P = [
    0.9181114315678452,
    0.09117526276024962,
    0.029325814375681554,
    0.23172769688626216,
]
AUTHORITATIVE_JOB = "hxq-bda50c6bf65bb543"


class BranchADispersionGate(unittest.TestCase):
    def test_gate_verdict_and_numbers(self):
        rep = receipt(list(GATE_ARMS), 0.05)
        self.assertEqual(rep["verdict"], "POOLING_CONTESTED")
        self.assertEqual(len(rep["rows"]), 4)
        self.assertAlmostEqual(
            rep["pooled_phat"], 0.7475786924939467, delta=1e-12
        )
        self.assertAlmostEqual(
            rep["min_exact_p"], 0.029325814375681554, delta=1e-12
        )
        for row, expected in zip(rep["rows"], EXPECTED_PER_ARM_P):
            self.assertAlmostEqual(
                row["exact_two_sided_p"], expected, delta=1e-12
            )
        # The driver is arm-6 (row index 2): hot 0.778 vs loo family.
        self.assertEqual(rep["rows"][2]["phat"], 0.778)

    def test_arms_are_the_committed_corrected_pool(self):
        text = (
            ROOT / "evidence" / "2026-10-09-w8-line" / "run.out"
        ).read_text()
        # The instrument's payload is the FIRST JSON document; the
        # following lines are its own compact verdict echo + VERDICTS
        # line (3-line run.out), so decode exactly one document.
        run, end = json.JSONDecoder().raw_decode(text)
        self.assertTrue(text[end:].lstrip().startswith('{"CAL"'),
                        "unexpected trailing content in run.out")
        refs = run["references"]
        derived = [
            (refs["arm3"]["x"], refs["arm3"]["k"]),
            (refs["arm4"]["x"], refs["arm4"]["k"]),
            (run["arm6_terminal_w8"]["D2T"], 500),
            (run["arm7_terminal_w8"]["D2T"], 499),
        ]
        self.assertEqual(derived, GATE_ARMS)
        self.assertEqual(sum(x for x, _ in GATE_ARMS), 1235)
        self.assertEqual(sum(k for _, k in GATE_ARMS), 1652)
        # The committed dispersion block agrees with the gate re-derivation.
        self.assertEqual(
            run["dispersion"]["per_arm"], EXPECTED_PER_ARM_P
        )
        self.assertEqual(run["branch"], "POOLING_CONTESTED")

    def test_closure_note_records_unclaimable_both_sides(self):
        note = (
            ROOT
            / "research-log"
            / "2026-10-13-w8-branchA-dispersion-gate.md"
        ).read_text()
        for literal in (
            "NOT claimable",
            "VERDICT-READY",
            "REFUTED (low)",
            "REPORTED-NOT-CLAIMABLE",
            "AMBIG_MIDDLE",
            "no growth, no k80 census, no submission",
            "n ≈ 3560 terminals/group",
        ):
            self.assertIn(literal, note)

    def test_posfresh_receipt_job_id_authoritative(self):
        rec = json.loads(
            (
                ROOT / "evidence" / "2026-10-13-w8-posfresh" / "queue-receipt.json"
            ).read_text()
        )
        # Corrected against the queue request record (CI failure on
        # ab1ece7): the job id is the full 16-hex form, not the
        # truncated console echo.
        self.assertEqual(rec["job"], AUTHORITATIVE_JOB)
        self.assertTrue(
            rec["job"].endswith(rec["request_id"][:16]),
            "job id must be hxq- + first 16 hex of the request id",
        )
        # The correction touched only the job field: evidence hashes
        # pinned by the import rehearsal stay unchanged.
        self.assertEqual(
            rec["run_out_sha256"],
            "76e3e066b086a32e1e3b151a64bf17db7ad1344f58077592f6c6f15446945a72",
        )
        self.assertEqual(rec["run_out_bytes"], 2238)
        self.assertEqual(rec["verdicts_recorded_by_instrument"]["branch"],
                         "POSITION_DECLINE_NOT_DETECTED")


if __name__ == "__main__":
    unittest.main()
