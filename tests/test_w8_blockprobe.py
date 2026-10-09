"""Pins for evidence/2026-10-09-w8-blockprobe/ktam_w8_blockprobe.py —
the w8 block-mechanism probe harness (tick 100, SON-4928),
pre-registered BEFORE submission.

Constants are identity-pinned against the committed receipts
(tick-96 arm-3 375/500, tick-97 arm-4 106/153, tick-98 arm-5
370/500, tick-99 arm-6 389/500 + arm-7 365/499 + pooled line
1235/1652, the DW9 CAL identity chain 367:131).  The duplicated
dispersion/exact-test arithmetic is pinned by IDENTITY against the
tick-93/98/99 receipt numbers and against the live committed tool
w8_dispersion_receipt — the duplication is the point; the identity
pin catches drift in either copy.  Branch bands were MEASURED
before pinning (tick-73/98 lesson).  No trajectory runs here (the
queue job is the run of record)."""
import importlib.util
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TILES_AND_DIR = REPO / "evidence" / "2026-10-06-body-conjunction-builds"
TILES_DEATH_DIR = REPO / "evidence" / "2026-10-06-structural-death"
HARNESS = REPO / "evidence" / "2026-10-09-w8-blockprobe" / "ktam_w8_blockprobe.py"

for _p in (str(REPO), str(TILES_AND_DIR), str(TILES_DEATH_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

_spec = importlib.util.spec_from_file_location("ktam_w8_blockprobe", HARNESS)
a = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(a)

import tools.w8_dispersion_receipt as wdr  # noqa: E402

BRANCHES = {"BLOCK_STRUCTURE", "WINDOW_NOISE", "AMBIG_MIDDLE",
            "OUTSIDE_BOTH", "NO_EVENTS", "VOID"}


class TestProbeConstants(unittest.TestCase):
    def test_arms_are_sixb_and_gap_window(self):
        self.assertEqual(a.SEED0_ARM6B, 340261607)
        self.assertEqual(a.SEED0_ARM8, 350261107)
        self.assertEqual(a.SEED0_ARM6B,
                         a.BASE_SEED + 6 * a.SEED_STRIDE + 500)
        self.assertEqual(a.SEED0_ARM8,
                         a.BASE_SEED + 13 * (a.SEED_STRIDE // 2))

    def test_full_mode_sizes(self):
        # CI runs without SMOKE: CAL 500 + arm-6b 500 + arm-8 500.
        self.assertEqual(a.N_CAL, 500)
        self.assertEqual(a.N_ARM6B, 500)
        self.assertEqual(a.N_ARM8, 500)

    def test_cal_chain_and_protocol(self):
        self.assertEqual((a.CAL_D2T, a.CAL_L2), (367, 131))
        self.assertEqual(a.SEED0_CAL, 260261107)
        self.assertEqual(a.WIN_MULT, 8.0)
        self.assertEqual(a.DG, 2.0)

    def test_reference_receipts(self):
        self.assertEqual((a.ARM3_X, a.ARM3_K), (375, 500))
        self.assertEqual((a.ARM4_X, a.ARM4_K), (106, 153))
        self.assertEqual((a.ARM5_X, a.ARM5_K), (370, 500))
        self.assertEqual((a.ARM6_X, a.ARM6_K), (389, 500))
        self.assertEqual((a.ARM7_X, a.ARM7_K), (365, 499))
        self.assertEqual((a.FAM_X, a.FAM_K), (1110, 1499))
        self.assertEqual(a.FAM_X, a.ARM3_X + a.ARM5_X + a.ARM7_X)
        # arm-4 excluded from the family pool per tick-98 ARM4_SMALLN
        self.assertNotIn(a.ARM4_X, [a.ARM3_X, a.ARM5_X, a.ARM7_X])
        self.assertEqual(a.ALPHA, 0.05)


class TestFreshSeeds(unittest.TestCase):
    def test_no_prior_run_out_contains_probe_seeds(self):
        hits = []
        for p in sorted((REPO / "evidence").glob("*/run.out")):
            if "2026-10-09-w8-blockprobe" in str(p):
                continue
            text = p.read_text(errors="replace")
            for seed in ("340261607", "350261107"):
                if seed in text:
                    hits.append((str(p), seed))
        self.assertEqual(hits, [])

    def test_no_placeholder_or_stale_names_left(self):
        src = HARNESS.read_text()
        self.assertNotIn("NotImplementedError", src)
        self.assertNotIn("LOW_OUTLIER", src)


class TestArithmeticIdentity(unittest.TestCase):
    def test_tick93_receipts(self):
        self.assertEqual(
            a.dispersion_min_p([(417, 500), (407, 500)])[0],
            0.22940515642070108)
        self.assertEqual(
            a.dispersion_min_p([(417, 500), (250, 500)])[0],
            3.0305437299158517e-66)

    def test_tick99_receipt(self):
        m, ps = a.dispersion_min_p(
            [(375, 500), (106, 153), (389, 500), (365, 499)])
        self.assertEqual(m, 0.029325814375681554)
        self.assertEqual(
            ps, [0.9181114315678452, 0.09117526276024962,
                 0.029325814375681554, 0.23172769688626216])

    def test_exact_test_identity_vs_committed_tool(self):
        # arm-6 vs its tick-99 leave-one-out pool (846/1152)
        self.assertEqual(
            a.exact_two_sided_p(500, 846 / 1152.0, 389),
            wdr.exact_two_sided_p(500, 846 / 1152.0, 389))
        self.assertEqual(
            a.exact_two_sided_p(500, 846 / 1152.0, 389),
            0.029325814375681554)

    def test_wilson_identity(self):
        self.assertEqual(a.wilson(1235, 1652), [0.72607, 0.76794])


class TestBranchMap(unittest.TestCase):
    """Bands MEASURED before pinning (tick-100 exec receipts)."""

    def test_measured_bands_x6b(self):
        # x8 held at 370 (family-consistent); n6b = n8 = 500
        for x6b, branch in [
            (300, "OUTSIDE_BOTH"), (355, "WINDOW_NOISE"),
            (375, "AMBIG_MIDDLE"), (390, "BLOCK_STRUCTURE"),
            (410, "OUTSIDE_BOTH"),
        ]:
            br, t, c, d = a.probe_reading(500, x6b, 500, 370)
            self.assertEqual(br, branch, "x6b=%d" % x6b)

    def test_measured_control_bands_x8(self):
        for x8, ctrl in [
            (330, "COLD_NEIGHBORHOOD"), (370, "FAMILY_CONSISTENT"),
            (385, "FAMILY_CONSISTENT"),
        ]:
            br, t, c, d = a.probe_reading(500, 389, 500, x8)
            self.assertEqual(c, ctrl, "x8=%d" % x8)

    def test_map_exhaustive_no_default(self):
        seen = set()
        for x6b in range(300, 451, 5):
            br, t, c, d = a.probe_reading(500, x6b, 500, 370)
            self.assertIn(br, BRANCHES - {"NO_EVENTS", "VOID"})
            seen.add(br)
        self.assertEqual(seen, {"BLOCK_STRUCTURE", "WINDOW_NOISE",
                                "AMBIG_MIDDLE", "OUTSIDE_BOTH"})

    def test_no_events_floor(self):
        br, t, c, d = a.probe_reading(49, 40, 500, 370)
        self.assertEqual(br, "NO_EVENTS")
        self.assertIsNone(t)


if __name__ == "__main__":
    unittest.main()
