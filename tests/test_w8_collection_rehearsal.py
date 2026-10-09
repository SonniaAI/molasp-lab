"""Pins for the collection-day rehearsal (tools/w8_collection_rehearsal.py).

The rehearsal drives the REAL CLIs (import_queue_result, collect_w8,
w8_decision_atlas) end to end on SYNTHETIC data in an isolated root.
These pins hold the discipline: byte-exact run.out recovery, the
synthetic stamp, the evidence-tree guard, the refusal spot-checks, and
the three scenario verdicts — so collection day differs from the drill
by exactly one thing: the blob comes from the queue, not from us.
"""

import json
import tempfile
import unittest
from pathlib import Path

from tools.w8_collection_rehearsal import (
    REQUEST_ID,
    RehearsalRefused,
    ensure_safe_root,
    rehearse,
    synth_blob,
    synthetic_runout,
)

REPO = Path(__file__).resolve().parents[1]


class RootGuardTests(unittest.TestCase):
    def test_rehearsal_root_inside_evidence_refused(self):
        with self.assertRaises(RehearsalRefused):
            ensure_safe_root(REPO / "evidence" / "2026-10-08-w8-hazardhold")
        with self.assertRaises(RehearsalRefused):
            ensure_safe_root(REPO / "evidence")

    def test_rehearsal_root_outside_evidence_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(str(ensure_safe_root(tmp)))


class FrameTests(unittest.TestCase):
    def test_blob_frame_round_trips_stdout_byte_exactly(self):
        stdout_text = synthetic_runout((384, 77), "HELD")
        blob = synth_blob(stdout_text)
        self.assertTrue(blob.startswith(
            "HX-OUT-BEGIN:%s\nHX-FILE:status\n0\n\n" % REQUEST_ID))
        # stdout section = content + one echo newline, then the closer
        self.assertIn(stdout_text + "\nHX-QUEUE-EXIT:0", blob)
        self.assertTrue(blob.rstrip("\n").endswith(
            "HX-OUT-END:" + REQUEST_ID))

    def test_synthetic_runout_is_stamped(self):
        self.assertTrue(synthetic_runout((30, 10), "NO_EVENTS")
                        .startswith("REHEARSAL-SYNTHETIC"))


class ChainRehearsalTests(unittest.TestCase):
    def test_all_scenarios_pass_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt = rehearse(tmp)
            self.assertTrue(receipt["synthetic"])
            self.assertTrue(receipt["interpretation"]
                            .startswith("none"))
            by_name = {s["scenario"]: s for s in receipt["scenarios"]}
            self.assertEqual(by_name["held"]["collector_branch"],
                             "CAL_OK+HELD")
            self.assertEqual(by_name["held"]["atlas_verdict"], "HELD")
            self.assertEqual(by_name["held"]["atlas_region"],
                             "hold-only")
            self.assertEqual(by_name["refuted"]["collector_branch"],
                             "CAL_OK+REFUTED")
            self.assertEqual(by_name["refuted"]["atlas_verdict"],
                             "REFUTED")
            self.assertEqual(by_name["refuted"]["atlas_region"],
                             "chain-falsified")
            self.assertEqual(by_name["no_events"]["collector_branch"],
                             "CAL_OK+NO_EVENTS")
            self.assertEqual(by_name["no_events"]["atlas_verdict"],
                             "NO_EVENTS")

    def test_held_scenario_artifacts_on_disk(self):
        with tempfile.TemporaryDirectory() as tmp:
            rehearse(tmp)
            held = Path(tmp) / "held"
            run_out = (held / "run.out").read_text()
            self.assertTrue(run_out.startswith("REHEARSAL-SYNTHETIC"))
            manifest = json.loads(
                (held / "run.out.import.json").read_text())
            self.assertTrue(manifest["interpretation"]
                            .startswith("none"))
            self.assertEqual(manifest["exit_status"], 0)
            verdict = json.loads((held / "verdict.json").read_text())
            self.assertEqual(verdict["cross_check"], "ok")
            atlas = json.loads((held / "atlas.json").read_text())
            self.assertEqual(atlas["datum"], [384, 461])
            self.assertEqual(
                atlas["attribution"]["else"], "region-ambiguous at "
                                              "census k=461")
            receipt_path = Path(tmp) / "rehearsal_receipt.json"
            self.assertTrue(receipt_path.exists())

    def test_refusal_spot_checks_all_refuse(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt = rehearse(tmp)
            refusals = receipt["refusals"]
            self.assertEqual(
                sorted(refusals),
                ["empty_stdout", "wrong_request_id"])
            for check in refusals.values():
                self.assertTrue(check["refused"], check)
                self.assertNotEqual(check["exit"], 0)


if __name__ == "__main__":
    unittest.main()
