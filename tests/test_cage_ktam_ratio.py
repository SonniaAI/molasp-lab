"""CI invariants for the cage kTAM ratio measurement (tick 12).

Pins the facts behind the measured supersession of tick 11's ratio
arithmetic (designs/001, entry (b), "Cage MC measured"):
  1. structural: D2F and D2T are bond-arithmetic IDENTICAL in the cage
     (shared bonding glues {go2, r2}; every other face glue is
     unique-name inert), so the unfounded completion rides the correct
     channel's own kinetics — the fair-coin fact behind wrong/correct~1;
  2. arithmetic: the co-residency budget guide 1-exp(-400*p_L1*p_row2);
  3. behavioural: a small fixed-seed MC run completes and splits a/ap
     near evenly (the symmetry is kinetic, not just bookkeeping);
  4. verdict: the run.out evidence rows carry the refutation clauses at
     dG=2 and dG=4, and the totals carry the 511/487 fair coin.
"""
import collections
import json
import math
import os
import sys
import unittest

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
EV = os.path.join(HERE, "evidence", "2026-10-06-v3p-cage-ktam-ratio")
CAGE = os.path.join(HERE, "evidence", "2026-10-06-v3p-blind-cage")
sys.path.insert(0, EV)
sys.path.insert(0, CAGE)

from ktam_mc_v3p import budget_curve, run_assembly, GSE  # noqa: E402
from tiles_v3p import (  # noqa: E402
    TILES, SEED_N, matched_strength, glue_strength)


class TestRow2ValueChannelIdentical(unittest.TestCase):
    def test_bonding_glue_sets_are_identical(self):
        counts = {}
        for t in TILES.values():
            for g in t.values():
                counts[g] = counts.get(g, 0) + 1
        for g in SEED_N.values():
            counts[g] = counts.get(g, 0) + 1

        def bonding_glues(tile):
            return {g for g in TILES[tile].values() if counts.get(g, 0) > 1}

        self.assertEqual(bonding_glues("D2F"), bonding_glues("D2T"))
        self.assertEqual(bonding_glues("D2F"), {"go2", "r2"})
        # the faces that DIFFER between D2F and D2T are unique-name inert
        for g in (TILES["D2F"]["S"], TILES["D2T"]["S"],
                  TILES["D2F"]["N"], TILES["D2T"]["N"]):
            self.assertEqual(counts.get(g), 1,
                             "%s must appear exactly once" % g)

    def test_matched_strength_equal_in_canonical_contexts(self):
        base = {(0, 0): "seed0", (1, 0): "seed1", (2, 0): "seed2",
                (0, 1): "S1", (0, 2): "S2", (1, 1): "D1T"}
        with_l1 = dict(base)
        with_l1[(2, 1)] = "L1"
        ctxs = [base, with_l1]
        for ctx in ctxs:
            self.assertEqual(matched_strength(ctx, (1, 2), "D2F"),
                             matched_strength(ctx, (1, 2), "D2T"))

    def test_lock_glues_bond_both_values_equally(self):
        self.assertEqual(glue_strength(TILES["L2"]["W"], TILES["D2F"]["E"]), 1)
        self.assertEqual(glue_strength(TILES["L2"]["W"], TILES["D2T"]["E"]), 1)


class TestBudgetCurve(unittest.TestCase):
    def test_grid_values(self):
        self.assertGreaterEqual(budget_curve(2.0), 0.97)
        self.assertTrue(0.15 <= budget_curve(4.0) <= 0.35)
        self.assertLess(budget_curve(7.0), 0.01)

    def test_monotone_decreasing(self):
        vals = [budget_curve(d) for d in (0.5, 2.0, 4.0, 7.0)]
        self.assertEqual(vals, sorted(vals, reverse=True))


class TestSmallRunSymmetry(unittest.TestCase):
    def test_fixed_seed_small_grid(self):
        n = 60
        T_read = 400.0 * math.exp(9.5)
        decodes = [run_assembly(9.5, GSE, T_read, 20261008 + 70000 + i)
                   for i in range(n)]
        c = collections.Counter(decodes)
        completions = sum(c.get(k, 0) for k in ("a", "ap", "p", "empty"))
        self.assertGreaterEqual(completions, 50)
        self.assertLessEqual(abs(c.get("a", 0) - c.get("ap", 0)), 20)


class TestEvidenceVerdict(unittest.TestCase):
    def test_run_out_rows_carry_refutation(self):
        rows = {}
        totals = None
        with open(os.path.join(EV, "run.out")) as f:
            for line in f:
                rec = json.loads(line)
                if "dGmc" in rec:
                    rows[rec["dGmc"]] = rec
                if "totals" in rec:
                    totals = rec["totals"]
        for dG in (2.0, 4.0):
            self.assertIn(dG, rows, "missing evidence row for dG=%s" % dG)
            rec = rows[dG]
            self.assertTrue(rec["falsifier_wrong_ge_e2dG"])
            self.assertTrue(rec["falsifier_correct_ratio_ge_v3_times_e_dG"])
            # the measured fair-coin symmetry, NOT the predicted e^{-dG}
            self.assertTrue(0.7 <= rec["ratio_ap_over_a"] <= 1.3)
            self.assertGreater(rec["ratio_wrong_over_correct"],
                               math.exp(-dG) * 3)
        # fair coin over the whole grid: 511 a vs 487 ap
        self.assertEqual(totals["a"], 511)
        self.assertEqual(totals["ap"], 487)
        self.assertEqual(sum(totals.values()), 2000)


if __name__ == "__main__":
    unittest.main()
