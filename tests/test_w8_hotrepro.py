"""Pins for evidence/2026-10-13-w8-hotrepro/ktam_w8_hotrepro.py — the
w8 hot-window family reproduction probe (SON-5140), pre-registered
BEFORE submission.  Constants are identity-pinned against the
committed receipts (six-window corrected state, DW9 CAL identity chain
367:131, family rate 1110/1499).  The exact one-sided binomial is
pinned against closed-form values; the branch map is pinned at the
MEASURED cut points (tick-73/98 lesson: measure, then pin).  No
trajectory runs here (the queue job is the run of record)."""
import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HERE_DIR = REPO / "evidence" / "2026-10-13-w8-hotrepro"
PREVIOUS = REPO / "evidence" / "2026-10-09-w8-blockprobe"
TILES_AND_DIR = REPO / "evidence" / "2026-10-06-body-conjunction-builds"
TILES_DEATH_DIR = REPO / "evidence" / "2026-10-06-structural-death"

for _p in (str(REPO), str(PREVIOUS), str(TILES_AND_DIR), str(TILES_DEATH_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

_spec = importlib.util.spec_from_file_location(
    "ktam_w8_hotrepro", HERE_DIR / "ktam_w8_hotrepro.py")
h = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(h)

import unittest  # noqa: E402


class TestConstants(unittest.TestCase):
    def test_fresh_seeds_are_disjoint_from_all_burned_ranges(self):
        # A_FRESH = arm-6 block windows [1000,2000): burned in that
        # block are [0,500) (arm-6) and [500,1000) (6B).
        self.assertEqual(h.SEED0_AFRESH, 340261107 + 1000)
        self.assertGreaterEqual(h.SEED0_AFRESH, 340261107 + 1000)
        self.assertLess(h.SEED0_AFRESH, 340261107 + 2000)
        # B_FRESH = arm-8 block windows [500,1500): burned [0,500).
        self.assertEqual(h.SEED0_BFRESH, 350261107 + 500)
        self.assertLess(h.SEED0_BFRESH + 1000, 350261107 + 1501)
        # Disjointness assertions, explicit: the fresh window of each
        # block must start at or beyond every burned range in it.
        self.assertGreaterEqual(h.SEED0_AFRESH, 340261107 + 1000)
        self.assertFalse(340261107 + 0 <= h.SEED0_AFRESH < 340261107 + 1000)
        self.assertFalse(350261107 + 0 <= h.SEED0_BFRESH < 350261107 + 500)

    def test_sizes_and_null(self):
        self.assertEqual(h.N_FRESH, 1000)
        self.assertEqual(h.N_CAL, 500)
        self.assertEqual((h.FAM_X, h.FAM_K), (1110, 1499))
        self.assertAlmostEqual(h.Q0, 1110 / 1499.0, places=15)
        self.assertEqual(h.ALPHA_STAR, 0.025)
        self.assertEqual(h.MIN_EVENTS, 400)

    def test_burned_references_are_the_corrected_state(self):
        self.assertEqual((h.REF_ARM6["x"], h.REF_ARM6["k"]), (389, 500))
        self.assertEqual((h.REF_ARM6B["x"], h.REF_ARM6B["k"]), (372, 500))
        self.assertEqual((h.REF_ARM8["x"], h.REF_ARM8["k"]), (391, 500))


class TestExactOneSidedBinomial(unittest.TestCase):
    def test_closed_form_small_cases(self):
        self.assertAlmostEqual(h.p_upper(9, 10, 0.5), 0.0107421875, places=15)
        self.assertAlmostEqual(h.p_upper(8, 10, 0.5), 0.0546875, places=15)
        self.assertAlmostEqual(h.p_upper(1, 10, 0.5), 0.9990234375, places=12)

    def test_degenerate_edges(self):
        self.assertEqual(h.p_upper(0, 100, 0.5), 1.0)
        self.assertEqual(h.p_upper(101, 100, 0.5), 0.0)
        self.assertAlmostEqual(h.p_upper(100, 100, 0.5), (0.5) ** 100, places=40)

    def test_measured_cut_points_at_n1000(self):
        q0 = h.Q0
        self.assertAlmostEqual(h.p_upper(768, 1000, q0), 0.02468282, places=7)
        self.assertAlmostEqual(h.p_upper(767, 1000, q0), 0.02927526, places=7)
        self.assertAlmostEqual(h.p_upper(764, 1000, q0), 0.04742232, places=7)
        self.assertAlmostEqual(h.p_upper(763, 1000, q0), 0.05515597, places=7)


class TestBranchMap(unittest.TestCase):
    def test_block_structure_at_measured_cut(self):
        br, t = h.family_gate(768, 1000, 700, 1000)
        self.assertEqual(br, "BLOCK_STRUCTURE")
        self.assertLessEqual(t["p_afresh"], 0.025)

    def test_ambig_middle_band(self):
        br, _ = h.family_gate(766, 1000, 700, 1000)
        self.assertEqual(br, "AMBIG_MIDDLE")

    def test_window_noise_at_family_mean(self):
        br, _ = h.family_gate(740, 1000, 738, 1000)
        self.assertEqual(br, "WINDOW_NOISE")

    def test_min_over_both_families(self):
        # B below the A share: the gate reads the MIN p. 766 is inside
        # the measured AMBIG band [764,767]; 700 alone would read NOISE.
        br, _ = h.family_gate(700, 1000, 766, 1000)
        self.assertEqual(br, "AMBIG_MIDDLE")

    def test_min_events_floor(self):
        br, _ = h.family_gate(768, 399, 770, 1000)
        self.assertEqual(br, "NO_EVENTS")

    def test_smoke_sizes_do_not_reach_the_floor(self):
        br, _ = h.family_gate(8, 8, 8, 8)
        self.assertEqual(br, "NO_EVENTS")


class TestReservedSeedsNeverRun(unittest.TestCase):
    def test_no_prior_run_out_contains_the_fresh_seed0s(self):
        # The fresh ranges 341261107+[0,1000) and 350261607+[0,1000)
        # must never appear in any committed run.out before this
        # probe's own evidence lands (legit whitelist: this probe's
        # own directory once collected).
        legit = ("2026-10-13-w8-hotrepro",)
        hits = []
        for p in sorted((REPO / "evidence").glob("*/run.out")):
            if any(d in str(p) for d in legit):
                continue
            text = p.read_text(errors="replace")
            for seed in ("341261107", "350261607"):
                if seed in text:
                    hits.append((str(p), seed))
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
