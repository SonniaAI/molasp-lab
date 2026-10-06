"""Pins for the species-death survey (tick 23, SON-4775).

aTAM arm: the 12-removal taxonomy receipt
(evidence/2026-10-06-species-death-survey/atam_survey.out) is
exhaustive tau=2 BFS; these tests pin the labels, the unique-terminal
property, the residual-stable-model decodes, the transitive V0p
collapse, and re-run the BFS for two representative removals so the
receipt cannot drift from the committed builds.

kTAM arm: grid-receipt consistency — per-system "pqr_total" summary
lines must equal the sum of the per-point "pqr" counts, and the
pre-registration verdicts line must be present (the scientific
verdicts themselves live in the research log; the test only pins the
receipt's internal consistency, the tick-22 discipline).
"""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EV = os.path.join(os.path.dirname(HERE), "evidence")
for p in (os.path.join(EV, "2026-10-06-body-conjunction-builds"),
          os.path.join(EV, "2026-10-06-structural-death"),
          os.path.join(EV, "2026-10-06-species-death-survey")):
    if p not in sys.path:
        sys.path.insert(0, p)

from tiles_and import BUILD1  # noqa: E402
from tiles_death import build_missing_species  # noqa: E402
from atam_check_and import producible, decode  # noqa: E402
from atam_survey import SPECIES  # noqa: E402

RECEIPT = os.path.join(EV, "2026-10-06-species-death-survey",
                       "atam_survey.out")
RUN_OUT = os.path.join(EV, "2026-10-06-species-death-survey", "run.out")

EXPECTED_LABELS = {
    "S1": "COLLAPSED", "D1T": "COLLAPSED", "V0p": "COLLAPSED",
    "L1": "COLLAPSED",
    "S2": "FAITHFUL_SUB", "D2T": "FAITHFUL_SUB", "Vp": "FAITHFUL_SUB",
    "L2": "FAITHFUL_SUB",
    "S3": "FAITHFUL_SUB", "DAr": "FAITHFUL_SUB", "DBr": "FAITHFUL_SUB",
    "L3": "FAITHFUL_SUB",
}
EXPECTED_DECODES = {
    "S2": "p", "D2T": "p", "Vp": "p", "L2": "p",
    "S3": "pq", "DAr": "pq", "DBr": "pq", "L3": "pq",
}


class TestAtamSurveyReceipt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(RECEIPT) as fh:
            cls.report = json.load(fh)

    def test_twelve_species(self):
        self.assertEqual(len(SPECIES), 12)
        self.assertEqual(sorted(r["removed"] for r in
                                self.report["rows"]),
                         sorted(SPECIES))

    def test_every_removal_has_unique_terminal(self):
        for row in self.report["rows"]:
            self.assertEqual(row["terminals"], 1, row["removed"])
            self.assertNotEqual(row["label"], "AMBIGUOUS",
                                row["removed"])

    def test_labels(self):
        for row in self.report["rows"]:
            self.assertEqual(row["label"],
                             EXPECTED_LABELS[row["removed"]],
                             row["removed"])

    def test_faithful_sub_decodes_are_residual_models(self):
        for row in self.report["rows"]:
            if row["label"] != "FAITHFUL_SUB":
                continue
            self.assertEqual(row["terminal_decodes"][0][0],
                             EXPECTED_DECODES[row["removed"]],
                             row["removed"])
            self.assertTrue(row["anchors"], row["removed"])

    def test_collapsed_rows_have_zero_locked_rows(self):
        for row in self.report["rows"]:
            if row["label"] == "COLLAPSED":
                self.assertEqual(tuple(row["terminal_decodes"][0]),
                                 ("", 0), row["removed"])

    def test_v0p_death_kills_the_lock_column(self):
        """The non-obvious transitive collapse: L1.W bonds V0p.E, so
        losing the via stub kills the row-1 LOCK too (columns V and L
        are one structure for survival purposes)."""
        row = [r for r in self.report["rows"]
               if r["removed"] == "V0p"][0]
        self.assertIn("L1", row["unproducible_tiles"])
        self.assertIn("Vp", row["unproducible_tiles"])

    def test_bfs_reproducibility_representative(self):
        for sp in ("DAr", "V0p", "L3"):
            b = build_missing_species(BUILD1, sp)
            seen, terms = producible(b)
            row = [r for r in self.report["rows"]
                   if r["removed"] == sp][0]
            self.assertEqual(len(seen), row["assemblies"], sp)
            self.assertEqual([decode(b, t) for t in terms],
                             [tuple(x) for x in
                              row["terminal_decodes"]], sp)


class TestKtamGridReceiptConsistency(unittest.TestCase):
    def test_run_out_internally_consistent(self):
        if not os.path.exists(RUN_OUT):
            self.skipTest("run.out not yet collected (queue job pending)")
        with open(RUN_OUT) as fh:
            lines = []
            for x in fh:
                x = x.strip()
                if not x:
                    continue
                try:
                    lines.append(json.loads(x))
                except ValueError:
                    continue  # queue trailer (tick-19 lesson): keep
                    # run.out byte-faithful, skip non-JSON in parsing
        header = lines[0]
        self.assertEqual(header["n_per_point"], 500)
        self.assertEqual(header["seed_base"], 20261031)
        per_sys = {}
        totals = {}
        verdicts = None
        for obj in lines[1:]:
            if "verdicts" in obj:
                verdicts = obj["verdicts"]
            elif "pqr_total" in obj:
                totals[obj["system"]] = obj["pqr_total"]
            elif "system" in obj and "pqr" in obj:
                per_sys.setdefault(obj["system"], []).append(obj["pqr"])
        self.assertEqual(len(totals), 13)
        self.assertEqual(len(per_sys), 13)
        for sysname, tot in totals.items():
            self.assertEqual(sum(per_sys[sysname]), tot, sysname)
            self.assertEqual(len(per_sys[sysname]), 4, sysname)
        self.assertIsNotNone(verdicts)
        for key in ("P2_violations", "P3_violations",
                    "P4_violations", "S4_min_ratio"):
            self.assertIn(key, verdicts)


if __name__ == "__main__":
    unittest.main()
