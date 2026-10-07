"""lock_glue_scope knob pins (tick 29 + tick 30, SON-4778) —
designs/004's glue-family scope EVALUATED: d4 under both scopes,
the repairability trade made mechanical at emit time.

Measured on BUILD1 (family census receipt: tick 24):
  family: lock hazards {V0p@(3,1):1, Vp@(3,2):1} + misreads incl.
          {Vp->L2, D2T->L2 at (3,3)}; stable b=2 substitution repair
          (D1T 2, D2T 2 at their vacancy sites).
  row:    hazards {} and misreads {}; canonical assembly intact
          (every site still >= tau=2); repair degraded to b=1
          transient holds (D1T 1, D2T 1) — the stable substitution
          channel is eliminated because all three are the same bonds.

BUILD3 (W1 wrong compile) was tick 29's honest boundary —
Fp@(3,3) survived row scope because its hold rides the FALSE
family (p-f). Tick 30 extended the qualification to all four
shared value-family suffixes (-t/-t-done/-f/-f-done): the
false-family squats die (BUILD3 Fp@(3,3); BUILD2 Vp@(3,2) and
Fr@(3,3), pinned below), canonical assemblies still intact. The
remaining boundary is glue CLASS, not family: non-value glues
(spine, go* entries, caps, and*/w* relays) are never qualified.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EV_AND = os.path.join(os.path.dirname(HERE), "evidence",
                      "2026-10-06-body-conjunction-builds")
for p in (EV_AND,):
    if p not in sys.path:
        sys.path.insert(0, p)

from molasp.offchannel import (  # noqa: E402
    apply_lock_glue_scope, canonical_assembly, lock_glue_scope_reports,
    matched_strength)
from tiles_and import BUILD1, BUILD2, BUILD3  # noqa: E402


class TestGlueScopeKnobBuild1(unittest.TestCase):
    """designs/004 knob on BUILD1: the trade, both sides pinned."""

    @classmethod
    def setUpClass(cls):
        cls.canon = canonical_assembly(BUILD1)
        cls.rep = lock_glue_scope_reports(BUILD1, cls.canon)

    def test_family_scope_reproduces_the_census_hazards(self):
        self.assertEqual(self.rep["family"]["lock_hazards"],
                         {"3,1": {"V0p": 1}, "3,2": {"Vp": 1}})
        self.assertEqual(
            self.rep["family"]["lock_misreads"]["3,3"],
            {"Vp": {"L2": 1}, "D2T": {"L2": 1}})

    def test_row_scope_kills_every_lock_hazard(self):
        self.assertEqual(self.rep["row"]["lock_hazards"], {})

    def test_row_scope_kills_every_lock_misread(self):
        self.assertEqual(self.rep["row"]["lock_misreads"], {})

    def test_row_scope_shrinks_but_does_not_empty_the_table(self):
        # non-lock off-channel sites survive at b=1 (the relay-pair
        # glues the substitution tiles legitimately carry) — the knob
        # eliminates the LOCK hazard class, not all off-channel contact
        self.assertEqual(sorted(self.rep["row"]["off_channel"]),
                         ["1,1", "1,2", "2,1", "2,2"])

    def test_row_scope_preserves_the_canonical_assembly(self):
        row_build = self.rep["row_build"]
        for site, tile in self.canon.items():
            self.assertGreaterEqual(
                matched_strength(row_build, self.canon, site, tile), 2,
                f"canonical {tile}@{site} fell below tau=2 under row scope")

    def test_row_scope_lock_read_glues_are_row_qualified_on_both_faces(self):
        row_build = self.rep["row_build"]
        via_e = row_build["tiles"][self.canon[(2, 1)]].get("E")
        lock_w = row_build["tiles"][self.canon[(3, 1)]].get("W")
        self.assertEqual(via_e, lock_w)
        self.assertTrue(lock_w.endswith("-lk1"))
        # propagation bond untouched: D.E <-> V.W still the family glue
        self.assertEqual(row_build["tiles"][self.canon[(1, 1)]]["E"],
                         row_build["tiles"][self.canon[(2, 1)]]["W"])

    def test_repair_bonds_degrade_from_stable_b2_to_b1(self):
        """The repairability trade, statically: family buys stable
        b=2 substitution repair; row keeps only b=1 transient holds."""
        self.assertEqual(self.rep["repair_bonds"]["family"],
                         {"D1T": 2, "D2T": 2})
        self.assertEqual(self.rep["repair_bonds"]["row"],
                         {"D1T": 1, "D2T": 1})

    def test_family_scope_returns_an_independent_copy(self):
        fam = apply_lock_glue_scope(BUILD1, "family")
        self.assertIsNot(fam, BUILD1)
        self.assertEqual(fam["tiles"], BUILD1["tiles"])
        fam["tiles"]["L1"]["W"] = "mutated"
        self.assertEqual(BUILD1["tiles"]["L1"]["W"], "p-t")

    def test_unknown_scope_is_refused_loudly(self):
        with self.assertRaises(ValueError):
            apply_lock_glue_scope(BUILD1, "column")


class TestGlueScopeKnobBuild3(unittest.TestCase):
    """A4 analogue under the knob: the wrong compile reports the
    same-class table, and the honest boundary — row scope kills the
    value-family hazards only."""

    @classmethod
    def setUpClass(cls):
        cls.canon = canonical_assembly(BUILD3)
        cls.rep = lock_glue_scope_reports(BUILD3, cls.canon)

    def test_family_scope_reproduces_the_tick28_hazards(self):
        self.assertEqual(self.rep["family"]["lock_hazards"],
                         {"3,1": {"V0q": 1}, "3,2": {"Fplus": 1},
                          "3,3": {"Fp": 1}})

    def test_row_scope_kills_every_lock_hazard(self):
        # tick 30: the -f/-f-done extension closes tick 29's honest
        # boundary — Fp@(3,3) rode the false family (p-f lock read of
        # row 3) and dies with the value-family hazards.
        self.assertEqual(self.rep["row"]["lock_hazards"], {})

    def test_row_scope_lock_read_glues_qualify_on_both_faces(self):
        row_build = self.rep["row_build"]
        via_e = row_build["tiles"][self.canon[(2, 3)]].get("E")
        lock_w = row_build["tiles"][self.canon[(3, 3)]].get("W")
        self.assertEqual(via_e, lock_w)
        self.assertTrue(lock_w.endswith("-lk3"))
        # squatter Fp's W keeps the bare family glue -> the squat bond
        # against the renamed via E face is gone
        self.assertEqual(row_build["tiles"]["Fp"]["W"], "p-f")
        self.assertNotEqual(row_build["tiles"]["Fp"]["W"], via_e)

    def test_row_scope_preserves_the_canonical_assembly(self):
        row_build = self.rep["row_build"]
        for site, tile in self.canon.items():
            self.assertGreaterEqual(
                matched_strength(row_build, self.canon, site, tile), 2,
                f"canonical {tile}@{site} fell below tau=2 under row scope")


class TestGlueScopeKnobBuild2(unittest.TestCase):
    """The falsity chain (P_AND-q): its locks read the FALSE
    families, so BUILD2 is the wrong-compile-free check that the
    tick-30 -f/-f-done extension is inventory-driven, not a
    BUILD3 patch — the false-family squats Vp@(3,2)/Fr@(3,3) and
    their misread channels die under row scope like the true-family
    ones on BUILD1."""

    @classmethod
    def setUpClass(cls):
        cls.canon = canonical_assembly(BUILD2)
        cls.rep = lock_glue_scope_reports(BUILD2, cls.canon)

    def test_family_scope_reports_the_false_family_hazards(self):
        self.assertEqual(self.rep["family"]["lock_hazards"],
                         {"3,1": {"V0p": 1}, "3,2": {"Vp": 1},
                          "3,3": {"Fr": 1}})

    def test_row_scope_kills_true_and_false_family_hazards(self):
        # pre-tick-30 this was {"3,2": {"Vp": 1}, "3,3": {"Fr": 1}} —
        # the false-family boundary, now closed
        self.assertEqual(self.rep["row"]["lock_hazards"], {})
        self.assertEqual(self.rep["row"]["lock_misreads"], {})

    def test_row_scope_qualifies_false_family_lock_reads(self):
        row_build = self.rep["row_build"]
        # row-2 lock read rides q-f (false family)
        via_e = row_build["tiles"][self.canon[(2, 2)]].get("E")
        lock_w = row_build["tiles"][self.canon[(3, 2)]].get("W")
        self.assertEqual((via_e, lock_w), ("q-f-lk2", "q-f-lk2"))
        # row-3 lock read rides r-f
        via_e3 = row_build["tiles"][self.canon[(2, 3)]].get("E")
        lock_w3 = row_build["tiles"][self.canon[(3, 3)]].get("W")
        self.assertEqual((via_e3, lock_w3), ("r-f-lk3", "r-f-lk3"))

    def test_row_scope_preserves_the_canonical_assembly(self):
        row_build = self.rep["row_build"]
        for site, tile in self.canon.items():
            self.assertGreaterEqual(
                matched_strength(row_build, self.canon, site, tile), 2,
                f"canonical {tile}@{site} fell below tau=2 under row scope")


if __name__ == "__main__":
    unittest.main()
