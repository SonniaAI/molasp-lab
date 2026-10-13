"""Pins for evidence/2026-10-13-w8-blockpos/blockpos_instrument.py — the
tick-112 (SON-5142) block-position trend/adjacency instrument, pre-registered
in research-log/2026-10-13-w8-blockpos-prereg.md (commit 8269278) BEFORE any
permutation output existed.

Constants are pinned from the emitted receipt run.out (measure-then-pin). The
floor-property tests re-derive the enumeration independently with exact
fractions: P1's statistic is invariant under permutations of the non-first
windows, so its achievable p-floor is 12/144 (not the prereg's stated 1/144 —
corrected and disclosed in the collection note); S2's floor is 1/144. No
trajectory runs here; the receipt is the run of record.
"""
import importlib.util
import json
import unittest
from fractions import Fraction
from itertools import permutations
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INSTRUMENT = REPO / "evidence" / "2026-10-13-w8-blockpos" / "blockpos_instrument.py"
RECEIPT = REPO / "evidence" / "2026-10-13-w8-blockpos" / "run.out"

_spec = importlib.util.spec_from_file_location("blockpos_instrument", INSTRUMENT)
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)

B340 = [(389, 500), (372, 500), (347, 500), (344, 499)]
B350 = [(391, 500), (346, 500), (368, 500)]


def load_receipt():
    return json.loads(RECEIPT.read_text().rsplit("VERDICTS", 1)[0])


def t_frac(o):
    from fractions import Fraction as F

    fx = o["340"][0][0] + o["350"][0][0]
    fn = o["340"][0][1] + o["350"][0][1]
    rx = sum(x for x, _ in o["340"][1:]) + sum(x for x, _ in o["350"][1:])
    rn = sum(n for _, n in o["340"][1:]) + sum(n for _, n in o["350"][1:])
    return F(fx, fn) - F(rx, rn)


def c_frac(o):
    from fractions import Fraction as F

    return sum(F((i + 1) * x, n) for w in (o["340"], o["350"]) for i, (x, n) in enumerate(w))


class TestBlockposReceiptPins(unittest.TestCase):
    """Frozen receipt values for the blockpos instrument (tick 112)."""

    def test_branch_and_verdicts_line(self):
        d = load_receipt()
        self.assertEqual(d["status"], "OK")
        self.assertEqual(d["branch"], "POSITION_STRUCTURE_NOT_DETECTED")
        last = RECEIPT.read_text().splitlines()[-1]
        self.assertEqual(
            last,
            'VERDICTS {"P1": "NOT_DETECTED", "S2": "NOT_DETECTED", '
            '"BRANCH": "POSITION_STRUCTURE_NOT_DETECTED"}',
        )

    def test_guards_all_ok(self):
        g = load_receipt()["guards"]
        self.assertTrue(g["ok"])
        self.assertTrue(g["expected_table"])
        self.assertTrue(g["seed_scan"]["ok"])
        self.assertTrue(g["cal_identity"]["ok"])
        self.assertTrue(all(g["hotrepro_cross_sums"].values()))

    def test_windows_table_and_structural_exclusion(self):
        d = load_receipt()
        self.assertEqual(len(d["windows"]), 8)
        self.assertTrue(all(w["ok"] for w in d["windows"]))
        self.assertEqual(len(d["excluded_windows"]), 1)
        ex = d["excluded_windows"][0]
        self.assertEqual((ex["block"], ex["x"], ex["n"]), ("B360", 365, 499))
        self.assertIn("single-window block", ex["reason"])

    def test_observed_statistics(self):
        obs = load_receipt()["observed"]
        self.assertEqual(obs["pooled_first"]["x"], 780)
        self.assertEqual(obs["pooled_first"]["n"], 1000)
        self.assertAlmostEqual(obs["pooled_first"]["share"], 0.78, places=12)
        self.assertEqual(obs["pooled_rest"]["x"], 1777)
        self.assertEqual(obs["pooled_rest"]["n"], 2499)
        self.assertAlmostEqual(obs["pooled_rest"]["share"], 1777 / 2499, places=12)
        self.assertAlmostEqual(obs["T_obs"], 0.06891556622649064, places=12)
        self.assertAlmostEqual(obs["C_obs"], 11.47951503006012, places=12)
        self.assertEqual(obs["block_totals"], {"B340": {"x": 1452, "n": 1999}, "B350": {"x": 1105, "n": 1500}})

    def test_p_values_and_holm(self):
        t = load_receipt()["tests"]
        self.assertEqual(t["alpha_family"], 0.05)
        self.assertAlmostEqual(t["P1"]["p"], 1 / 12, places=12)
        self.assertAlmostEqual(t["S2"]["p"], 5 / 144, places=12)
        self.assertAlmostEqual(t["P1"]["holm_adj"], 1 / 12, places=12)
        self.assertAlmostEqual(t["S2"]["holm_adj"], 10 / 144, places=12)
        self.assertFalse(t["P1"]["reject"])
        self.assertFalse(t["S2"]["reject"])
        self.assertEqual(t["P1"]["perm_count"], 144)
        self.assertEqual(t["S2"]["perm_count"], 144)


class TestBlockposFloorProperty(unittest.TestCase):
    """Independent exact re-derivation of the enumeration and its floors."""

    def _enumerate(self):
        obs = {"340": B340, "350": B350}
        t_obs, c_obs = t_frac(obs), c_frac(obs)
        perms = [
            {"340": list(p1), "350": list(p2)}
            for p1 in permutations(B340)
            for p2 in permutations(B350)
        ]
        return obs, t_obs, c_obs, perms

    def test_p_values_reproduced_exactly(self):
        obs, t_obs, c_obs, perms = self._enumerate()
        self.assertEqual(sum(1 for o in perms if t_frac(o) >= t_obs), 12)
        self.assertEqual(sum(1 for o in perms if c_frac(o) <= c_obs), 5)

    def test_p1_floor_is_rest_invariance_limited(self):
        # T only depends on which window is first in each block: the joint max
        # is realized by 3!*2! = 12 of the 144 labelings, so P1's achievable
        # floor is 12/144 ≈ 0.0833 — ABOVE alpha 0.05 (prereg floor statement
        # corrected in the collection note: 1/144 holds for S2 only).
        _, t_obs, _, perms = self._enumerate()
        self.assertEqual(sum(1 for o in perms if t_frac(o) == t_obs), 12)
        self.assertGreater(Fraction(12, 144), Fraction(1, 20))

    def test_s2_floor_is_one_over_perms(self):
        _, _, c_obs, perms = self._enumerate()
        cmin = min(c_frac(o) for o in perms)
        # The minimum C is uniquely realized and is NOT the observed ordering
        # (block 350 is not monotone: 0.782, 0.692, 0.736).
        self.assertEqual(sum(1 for o in perms if c_frac(o) == cmin), 1)
        self.assertGreater(c_obs, cmin)

    def test_observed_t_is_joint_maximum(self):
        _, t_obs, _, perms = self._enumerate()
        self.assertEqual(max(t_frac(o) for o in perms), t_obs)


class TestBlockposGuardConventions(unittest.TestCase):
    """The receipt-convention guards that fired on the first (refused) run."""

    def test_census_pair_count_excludes_other(self):
        # share convention on all three sources: pairs = D2T + L2, "other" out
        # (arm-7: 365+134=499 pairs, one non-pair trajectory).
        self.assertEqual(mod.census_pair_count({"D2T": 365, "L2": 134, "other": 1}), 499)
        self.assertEqual(mod.census_pair_count({"D2T": 389, "L2": 111, "other": 0}), 500)

    def test_build_windows_detects_any_mismatch(self):
        line_d = {
            "arm6_terminal_w8": {"D2T": 389, "L2": 111, "other": 0},
            "arm7_terminal_w8": {"D2T": 365, "L2": 134, "other": 1},
            "seed0_arm6": 340261107,
            "seed0_arm7": 360261107,
        }
        probe_d = {
            "arm6b_terminal_w8": {"D2T": 372, "L2": 128, "other": 0},
            "arm8_terminal_w8": {"D2T": 391, "L2": 109, "other": 0},
            "seed0_arm6b": 340261607,
            "seed0_arm8": 350261107,
        }
        hot_d = {
            "afresh_subwindows": [
                {"x": 347, "pair_n": 500, "seed0": 340262107},
                {"x": 344, "pair_n": 499, "seed0": 340262607},
            ],
            "bfresh_subwindows": [
                {"x": 346, "pair_n": 500, "seed0": 350261607},
                {"x": 368, "pair_n": 500, "seed0": 350262107},
            ],
        }
        rows = mod.build_windows(line_d, probe_d, hot_d)
        self.assertTrue(all(r["ok"] for r in rows))
        probe_d["arm8_terminal_w8"]["D2T"] = 390  # one count off -> refuse
        rows_bad = mod.build_windows(line_d, probe_d, hot_d)
        self.assertFalse(all(r["ok"] for r in rows_bad))


class TestBlockposDeterminism(unittest.TestCase):
    """A re-run must reproduce the committed receipt byte-identically."""

    def test_rerun_reproduces_receipt_byte_identically(self):
        import contextlib
        import io

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = mod.main()
        self.assertEqual(rc, 0)
        self.assertEqual(buf.getvalue(), RECEIPT.read_text())


if __name__ == "__main__":
    unittest.main()
