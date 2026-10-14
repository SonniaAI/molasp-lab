"""Pins for the consolidated pre-datum arbitration dashboard (tick 142).

The dashboard is a pure function of three committed receipts; these pins
verify (a) input receipt hashes live, (b) branch structure/order/provenance,
(c) the cross-receipt relations recomputed INDEPENDENTLY from the receipts,
and (d) byte-stability of the committed artifact under regeneration.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DASH_PATH = ROOT / "evidence" / "2026-10-14-w8-arbitration-dashboard" / "dashboard.json"

_spec = importlib.util.spec_from_file_location(
    "w8_arbitration_dashboard", ROOT / "tools" / "w8_arbitration_dashboard.py"
)
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def _sha(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


class ArbitrationDashboardPins(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dash = json.loads(DASH_PATH.read_text(encoding="utf-8"))
        cls.cal = _load("evidence/2026-10-14-w8-blockpower-cal-oc/cal-oc.json")
        cls.floor = _load("evidence/2026-10-14-w8-blockpower-floor-oc/floor-oc.json")
        cls.fisher = _load("evidence/2026-10-14-w8-blockpower-oc/oc.json")

    def test_input_hashes_live(self):
        for key, meta in self.dash["inputs"].items():
            self.assertEqual(
                meta["sha256"],
                _sha(meta["path"]),
                f"receipt {key} changed on disk vs dashboard record",
            )
        self.assertEqual(set(self.dash["inputs"]), {"fisher_oc", "floor_oc", "cal_oc"})
        self.assertEqual(self.dash["inputs"]["cal_oc"]["source_tick"], "tick141")
        self.assertEqual(self.dash["inputs"]["floor_oc"]["source_tick"], "tick140")
        self.assertEqual(self.dash["inputs"]["fisher_oc"]["source_tick"], "tick139")

    def test_four_branches_in_evaluation_order(self):
        branches = self.dash["branches"]
        self.assertEqual([b["order"] for b in branches], [1, 2, 3, 4])
        self.assertEqual(
            [b["verdict"] for b in branches],
            ["VOID", "NO_EVENTS", "BLOCK_MECHANISM_SUPPORTED", "BLOCK_MECHANISM_NOT_DETECTED"],
        )
        self.assertEqual(
            [b["branch"] for b in branches],
            ["CAL_FAIL", "min pair-n < 3400", "p <= 0.05", "p > 0.05"],
        )
        # evaluation-order claim: CAL before floor before any p-value
        self.assertIn("the floor and any p-value", branches[0]["read_before"])
        self.assertIn("any p-value", branches[1]["read_before"])
        for b in branches:
            for prov in b["provenance"]:
                stem = prov.split("#")[0]
                self.assertIn(
                    stem, ("cal_oc", "floor_oc", "fisher_oc"),
                    f"unknown provenance receipt '{stem}'",
                )
                field = prov.split("#")[1].split("[")[0].split(".")
                src = {"cal_oc": self.cal, "floor_oc": self.floor, "fisher_oc": self.fisher}[stem]
                node = src
                for part in field:
                    self.assertIn(part, node, f"provenance path broken: {prov}")
                    node = node[part]

    def test_cal_to_floor_sensitivity_ratio(self):
        ratio = self.dash["cross_receipt"]["cal_to_floor_sensitivity_ratio_per_seed_scale"]
        expected = (1.0 - self.floor["inversions"]["q_at_5pct_risk"]) / self.cal[
            "kernels"
        ]["dropout"]["eps_p05"]
        self.assertAlmostEqual(ratio, expected, places=10)
        self.assertGreater(ratio, 380.0)
        self.assertLess(ratio, 390.0)

    def test_size_chain(self):
        chain = self.dash["cross_receipt"]["size_chain"]
        floor_edge = self.floor["floor_edge_mc"]["FLOOR_EDGE_H0_SIZE"]["reject_rate"]
        nominal = self.fisher["results"]["H0_SIZE"]["reject_rate"]
        self.assertAlmostEqual(chain["floor_edge_pair_n_3400"], floor_edge, places=12)
        self.assertAlmostEqual(chain["nominal_pair_n_3560"], nominal, places=12)
        self.assertEqual(chain["alpha"], 0.05)
        self.assertTrue(chain["ordering_holds"])
        self.assertLess(floor_edge, nominal)
        self.assertLessEqual(nominal, 0.05)

    def test_power_monotone_in_delta(self):
        pm = self.dash["cross_receipt"]["power_monotone_in_delta"]
        r = self.fisher["results"]
        self.assertAlmostEqual(pm["d0223"], r["D0223_BASELINE"]["reject_rate"], places=12)
        self.assertAlmostEqual(pm["d030"], r["D030_BASELINE"]["reject_rate"], places=12)
        self.assertAlmostEqual(pm["d038"], r["D038_BASELINE"]["reject_rate"], places=12)
        self.assertTrue(pm["strictly_increasing"])
        # every prereg normal-approx power claim lands inside the exact MC Wilson-95
        self.assertTrue(
            self.dash["branches"][2]["oc"]["prereg_normal_approx_power_lands_inside_mc_wilson"]
        )
        for approx_key, res_key in (
            ("delta_0.0223", "D0223_BASELINE"),
            ("delta_0.030", "D030_BASELINE"),
            ("delta_0.038", "D038_BASELINE"),
        ):
            lo, hi = r[res_key]["reject_rate_wilson95"]
            approx = self.fisher["normal_approx_power_prereg"][approx_key]
            self.assertGreaterEqual(approx, lo)
            self.assertLessEqual(approx, hi)

    def test_clean_run_void_risk(self):
        crv = self.dash["cross_receipt"]["clean_run_void_risk"]
        hist_row = next(
            row for row in self.floor["yield_curve"] if abs(row["q_yield"] - 0.995) < 1e-12
        )
        self.assertAlmostEqual(crv["floor_at_hist_q995"], hist_row["map_risk_two_groups"], places=30)
        self.assertLess(crv["floor_at_hist_q995"], 1e-90)
        self.assertIn("determinism premise", crv["cal_under_determinism_premise"])

    def test_escape_displacement_bracket(self):
        fracs = self.dash["cross_receipt"]["escape_displacement_fraction_of_smallest_effect"]
        seeds = self.cal["verdict_safety"]["escape_displacement_seeds"]
        smallest = self.cal["verdict_safety"]["smallest_effect_seeds"]["d0223_hotrepro"]
        for kern in ("dropout", "reshuffle"):
            self.assertAlmostEqual(fracs[kern], seeds[kern] / smallest, places=10)
            self.assertLess(fracs[kern], 0.012)
            self.assertGreater(fracs[kern], 0.0)

    def test_branch_oc_scalars_traced(self):
        cal_oc = self.dash["branches"][0]["oc"]
        self.assertAlmostEqual(
            cal_oc["per_seed_corruption_5pct_mismatch"]["dropout"],
            self.cal["kernels"]["dropout"]["eps_p05"],
            places=20,
        )
        self.assertAlmostEqual(
            cal_oc["cal_pass_at_floor_5pct_collapse_yield"],
            self.cal["verdict_safety"]["cal_pass_at_tick140_collapse"],
            places=30,
        )
        self.assertLess(cal_oc["cal_pass_at_floor_5pct_collapse_yield"], 1e-8)
        b4 = self.dash["branches"][3]["oc"]
        self.assertAlmostEqual(
            b4["power_at_hotrepro_sized_delta0223"],
            self.fisher["results"]["D0223_BASELINE"]["reject_rate"],
            places=12,
        )
        self.assertAlmostEqual(
            b4["not_detected_rate_if_true_delta0223"],
            round(1.0 - self.fisher["results"]["D0223_BASELINE"]["reject_rate"], 5),
            places=8,
        )

    def test_framing_pre_datum_and_paused(self):
        f = self.dash["framing"]
        self.assertIn("dd5a8300", f["pre_datum"])
        self.assertEqual(f["ladder"], "PAUSED")
        self.assertIn("no RNG", f["no_rng"])

    def test_dashboard_byte_stable(self):
        regenerated = json.dumps(
            mod.build_dashboard(), indent=2, sort_keys=True
        ) + "\n"
        self.assertEqual(DASH_PATH.read_text(encoding="utf-8"), regenerated)

    def test_regeneration_writes_identical_bytes(self):
        payload_before = DASH_PATH.read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "regen.json"
            original = mod.OUT_PATH
            try:
                mod.OUT_PATH = out
                mod.OUT_DIR = Path(tmp)
                mod.main()
            finally:
                mod.OUT_PATH = original
                mod.OUT_DIR = ROOT / "evidence" / "2026-10-14-w8-arbitration-dashboard"
            self.assertEqual(payload_before, out.read_bytes())


if __name__ == "__main__":
    unittest.main()
