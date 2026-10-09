"""Pins for evidence/2026-10-09-w8-line/ktam_w8_line.py — the w8
stage-1 line census harness (tick 99, SON-4922), pre-registered
BEFORE submission.

Constants are identity-pinned against the committed receipts
(tick-96 arm-3 375/500, tick-97 arm-4 106/153, tick-98 arm-5
370/500, the DW9 CAL identity chain 367:131, the tick-97 pooled
line datum 481/653).  The duplicated dispersion arithmetic is
pinned by IDENTITY against the tick-93/98 receipt numbers — the
duplication is the point; the identity pin catches drift in
either copy.  The live census-policy tool is pinned on (481, 653)
so the growth this harness implements stays mechanically tied to
the pre-registered ladder.  Branch bands were MEASURED before
pinning (tick-73/98 lesson).  No trajectory runs here (the queue
job is the run of record).
"""
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TILES_AND_DIR = REPO / "evidence" / "2026-10-06-body-conjunction-builds"
TILES_DEATH_DIR = REPO / "evidence" / "2026-10-06-structural-death"
HARNESS = REPO / "evidence" / "2026-10-09-w8-line" / "ktam_w8_line.py"

for _p in (str(REPO), str(TILES_AND_DIR), str(TILES_DEATH_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

_spec = importlib.util.spec_from_file_location("ktam_w8_line", HARNESS)
a = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(a)

import tools.w8_dispersion_receipt as wdr  # noqa: E402


class TestLineConstants(unittest.TestCase):
    def test_arms_are_reserved_blocks_six_and_seven(self):
        self.assertEqual(a.SEED0_ARM6, 340261107)
        self.assertEqual(a.SEED0_ARM7, 360261107)
        self.assertEqual(a.SEED0_ARM6, a.BASE_SEED + 6 * a.SEED_STRIDE)
        self.assertEqual(a.SEED0_ARM7, a.BASE_SEED + 7 * a.SEED_STRIDE)

    def test_full_mode_sizes(self):
        # CI runs without SMOKE: CAL 500 + arm-6 500 + arm-7 500.
        self.assertEqual(a.N_CAL, 500)
        self.assertEqual(a.N_ARM6, 500)
        self.assertEqual(a.N_ARM7, 500)

    def test_cal_chain_and_protocol(self):
        self.assertEqual((a.CAL_D2T, a.CAL_L2), (367, 131))
        self.assertEqual(a.SEED0_CAL, 260261107)
        self.assertEqual(a.WIN_MULT, 8.0)
        self.assertEqual(a.DG, 2.0)

    def test_reference_receipts(self):
        self.assertEqual((a.ARM3_X, a.ARM3_K), (375, 500))
        self.assertEqual((a.ARM4_X, a.ARM4_K), (106, 153))
        self.assertEqual((a.ARM5_X, a.ARM5_K), (370, 500))
        self.assertEqual((a.POOL_X_REF, a.POOL_K_REF), (481, 653))
        self.assertEqual(a.POOL_X_REF, a.ARM3_X + a.ARM4_X)


class TestReservedSeedsNeverRun(unittest.TestCase):
    def test_no_prior_run_out_contains_arm6_or_arm7_seeds(self):
        this = "2026-10-09-w8-line"
        hits = []
        for p in sorted((REPO / "evidence").glob("*/run.out")):
            if this in str(p):
                continue
            text = p.read_text(errors="replace")
            for seed in ("340261107", "360261107"):
                if seed in text:
                    hits.append((str(p), seed))
        self.assertEqual(hits, [])


class TestPolicyReceiptIdentity(unittest.TestCase):
    def test_policy_on_pooled_481_653_names_the_line_census(self):
        out = subprocess.run(
            [sys.executable, "tools/w8_census_policy.py", "481", "653"],
            cwd=str(REPO), capture_output=True, text=True,
            timeout=60).stdout
        for needle in ("k=1524", "x_line=1123", "[1123, 1162]",
                       "4 arms total", "0.494",
                       "[0.70150, 0.76893]"):
            self.assertIn(needle, out)


class TestDispersionDuplicateIsVerbatim(unittest.TestCase):
    def test_tick93_canonical_receipt(self):
        min_p, _ps = a.dispersion_min_p([(417, 500), (407, 500)])
        self.assertAlmostEqual(min_p, 0.22940515642070108, places=15)

    def test_tick93_wild_arm_receipt(self):
        min_p, _ps = a.dispersion_min_p([(417, 500), (250, 500)])
        self.assertAlmostEqual(min_p, 3.0305437299158517e-66, delta=1e-80)

    def test_tick98_three_arm_receipt(self):
        min_p, _ps = a.dispersion_min_p(
            [(375, 500), (106, 153), (370, 500)])
        self.assertAlmostEqual(min_p, 0.13858226897330395, places=15)

    def test_identity_against_committed_tool_function(self):
        for k, p, x in ((500, 0.75, 370), (153, 106 / 153.0, 100),
                        (500, 481 / 653.0, 355)):
            self.assertAlmostEqual(
                a.exact_two_sided_p(k, p, x),
                wdr.exact_two_sided_p(k, p, x), places=15)


class TestLineReadingBranches(unittest.TestCase):
    def test_supported_line_at_measured_band(self):
        br, min_p, _ps, pooled = a.line_reading(500, 370, 500, 370)
        self.assertEqual(br, "SUPPORTED_LINE")
        self.assertAlmostEqual(min_p, 0.164736, places=5)
        self.assertEqual((pooled["x"], pooled["k"]), (1221, 1653))
        self.assertAlmostEqual(pooled["share"],
                               0.7386569872958257, places=15)
        self.assertEqual(pooled["wilson95"], [0.71694, 0.75927])

    def test_contested_on_wild_arm(self):
        br, min_p, _ps, _pooled = a.line_reading(500, 250, 500, 450)
        self.assertEqual(br, "POOLING_CONTESTED")
        self.assertAlmostEqual(min_p, 1.24645e-53, delta=1e-57)

    def test_contested_on_plausible_high_pair(self):
        # Honest-band pin: the 4-arm leave-one-out receipt has more
        # power than tick-98's 3-arm one — moderately high arm pairs
        # can fire.  Sensitivity, not a bug.
        br, min_p, _ps, _pooled = a.line_reading(500, 390, 500, 380)
        self.assertEqual(br, "POOLING_CONTESTED")
        self.assertAlmostEqual(min_p, 0.0454933, places=6)

    def test_no_events_below_floor(self):
        self.assertEqual(a.line_reading(40, 30, 500, 370)[0],
                         "NO_EVENTS")
        self.assertEqual(a.line_reading(500, 370, 40, 30)[0],
                         "NO_EVENTS")

    def test_branch_map_exhaustive_on_grid(self):
        allowed = {"SUPPORTED_LINE", "POOLING_CONTESTED"}
        for x6 in range(250, 451, 25):
            for x7 in range(250, 451, 25):
                br, _b, _c, _d = a.line_reading(500, x6, 500, x7)
                self.assertIn(br, allowed)

    def test_pooled_base_includes_arms_three_and_four(self):
        _br, _mp, _ps, pooled = a.line_reading(500, 370, 500, 370)
        self.assertEqual(pooled["x"], 375 + 106 + 370 + 370)
        self.assertEqual(pooled["k"], 500 + 153 + 500 + 500)


if __name__ == "__main__":
    unittest.main()
