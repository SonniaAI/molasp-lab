"""Pins for evidence/2026-10-13-w8-posfresh/ktam_w8_posfresh.py — the
w8 position-tagged fresh-window probe (tick 113, SON-5144),
pre-registered BEFORE submission.

Constants identity-pinned against the harness and the receipt lineage
(DW9 CAL identity chain 367:131; tick-112 first-vs-rest anchors
780/1000 vs 1777/2499).  Branch bands and Fisher values were MEASURED
before pinning (tick-73/98/111 lesson: never pin a band or a float
from a guess).  No trajectory runs here (the queue job is the run of
record).
"""
import importlib.util
import math
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TILES_AND_DIR = REPO / "evidence" / "2026-10-06-body-conjunction-builds"
TILES_DEATH_DIR = REPO / "evidence" / "2026-10-06-structural-death"
HARNESS = REPO / "evidence" / "2026-10-13-w8-posfresh" / "ktam_w8_posfresh.py"

for _p in (str(REPO), str(TILES_AND_DIR), str(TILES_DEATH_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

_spec = importlib.util.spec_from_file_location("ktam_w8_posfresh", HARNESS)
a = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(a)


class TestPosFreshConstants(unittest.TestCase):
    def test_virgin_block_bases(self):
        # blockprobe lineage: BASE_SEED 220261107 (NOT 160261107) —
        # the arithmetic catch of this tick, pinned so it can never
        # silently drift back to a scanned-as-clean-but-wrong base.
        self.assertEqual(a.BASE_SEED, 220261107)
        self.assertEqual(a.SEED0_U1, 560261107)
        self.assertEqual(a.SEED0_U2, 580261107)
        self.assertEqual(a.SEED0_U1, a.BASE_SEED + 17 * a.SEED_STRIDE)
        self.assertEqual(a.SEED0_U2, a.BASE_SEED + 18 * a.SEED_STRIDE)

    def test_window_layout(self):
        self.assertEqual(a.LATE_OFFSET, 9000)     # window [9000,10000)
        self.assertEqual(a.N_WIN, 1000)           # CI mode (no SMOKE)
        self.assertEqual(a.N_CAL, 500)
        self.assertEqual(a.ALPHA, 0.05)
        self.assertEqual(a.MIN_EVENTS, 1600)

    def test_cal_chain_unchanged(self):
        self.assertEqual((a.CAL_D2T, a.CAL_L2), (367, 131))
        self.assertEqual(a.SEED0_CAL, 260261107)
        self.assertEqual(a.DG, 2.0)
        self.assertEqual(a.WIN_MULT, 8.0)


class TestFisherArithmetic(unittest.TestCase):
    """Measured pins (computed from the harness itself before the
    receipt exists; identity-duplicated here so drift in either copy
    fails loudly)."""

    def test_one_sided_anchor_scale(self):
        # tick-112 anchor contrast at per-block n: 0.780 vs 0.711
        self.assertAlmostEqual(
            a.fisher_one_sided(780, 1000, 711, 1000),
            0.00023745138246714543, places=15)

    def test_one_sided_null_case(self):
        self.assertAlmostEqual(
            a.fisher_one_sided(740, 1000, 740, 1000),
            0.520326596451997, places=12)

    def test_two_sided_small_table(self):
        self.assertAlmostEqual(
            a.fisher_two_sided(7, 10, 3, 10),
            0.17889540799757442, places=12)
        self.assertAlmostEqual(
            a.fisher_two_sided(370, 500, 355, 500),
            0.3214435589822277, places=12)


class TestBranchMap(unittest.TestCase):
    """Frozen exhaustive map, pinned at measured points on both sides
    of the single gate (pooled n=2000 vs 2000, late fixed 1422 =
    share .711)."""

    def test_detected(self):
        branch, tests = a.branch_map(1500, 2000, 1422, 2000, True)
        self.assertEqual(branch, "POSITION_DECLINE_DETECTED")
        self.assertAlmostEqual(
            tests["p_fisher_one_sided"],
            0.0030283485769280792, places=12)

    def test_detected_just_inside_gate(self):
        branch, tests = a.branch_map(1470, 2000, 1422, 2000, True)
        self.assertEqual(branch, "POSITION_DECLINE_DETECTED")
        self.assertAlmostEqual(
            tests["p_fisher_one_sided"],
            0.048387116486505614, places=12)

    def test_not_detected_just_outside_gate(self):
        branch, tests = a.branch_map(1466, 2000, 1422, 2000, True)
        self.assertEqual(branch, "POSITION_DECLINE_NOT_DETECTED")
        self.assertAlmostEqual(
            tests["p_fisher_one_sided"], 0.064552, places=5)
        branch, tests = a.branch_map(1464, 2000, 1422, 2000, True)
        self.assertEqual(branch, "POSITION_DECLINE_NOT_DETECTED")

    def test_no_events_and_void(self):
        branch, _ = a.branch_map(1000, 1500, 1000, 1500, True)
        self.assertEqual(branch, "NO_EVENTS")
        branch, tests = a.branch_map(1500, 2000, 1422, 2000, False)
        self.assertEqual(branch, "VOID")
        self.assertIsNone(tests)


class TestPowerStatement(unittest.TestCase):
    """The prereg power statement, recomputed from the same formula
    (normal approx, one-sided alpha=0.05, n=2000/group, p_bar=0.745)."""

    SE = math.sqrt(2 * 0.745 * 0.255 / 2000)

    def power(self, delta):
        z = delta / self.SE - 1.645
        return 0.5 * (1 + math.erf(z / math.sqrt(2)))

    def test_stated_powers(self):
        self.assertAlmostEqual(self.power(0.069), 0.9996, places=3)
        self.assertTrue(0.69 <= self.power(0.030) <= 0.72)

    def test_mde_at_90(self):
        # corrected value: 0.040, NOT the 0.029 single-variance slip
        mde = (1.645 + 1.2816) * self.SE
        self.assertAlmostEqual(mde, 0.0403, places=3)


class TestVirginSeeds(unittest.TestCase):
    def test_no_prior_run_out_contains_probe_seeds(self):
        # Legitimate receipts mentioning these bases:
        # - this probe's own directory (the original burn, once run).
        # Any OTHER run.out containing either seed is a seed-reuse bug.
        legit = ("2026-10-13-w8-posfresh",)
        hits = []
        for p in sorted((REPO / "evidence").glob("*/run.out")):
            if any(d in str(p) for d in legit):
                continue
            text = p.read_text(errors="replace")
            for seed in ("560261107", "580261107"):
                if seed in text:
                    hits.append((str(p), seed))
        self.assertEqual(hits, [])


class TestNoStalePlaceholders(unittest.TestCase):
    def test_no_placeholder_or_stale_names_left(self):
        src = HARNESS.read_text()
        self.assertNotIn("NotImplementedError", src)
        self.assertNotIn("placeholder", src)
        # the stale tick-112 candidates must appear only as CORRECTED
        # context, never as runnable seed constants
        self.assertNotIn("SEED0_U1 = 380261107", src)
        self.assertNotIn("SEED0_U2 = 400261107", src)


if __name__ == "__main__":
    unittest.main()
