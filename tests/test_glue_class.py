"""Glue-CLASS boundary pins (tick 35, SON-4778) — the last open
designs/004 item closed by exact enumeration.

Measured (receipt: evidence/2026-10-07-glue-class/glue_class.out):
  C1  every non-value glue in BUILD1/2/3 is canonical_pair,
      seed_bond or inert_single — no shared structural glue, so no
      off-channel use exists for the class glues at all.
  C2  scope 'class' (row + every non-value non-SP canonical-bond
      rename) has an EMPTY matching-predicate diff vs row on all
      three builds: the class boundary is inert — kinetically
      identical to row by construction, no Monte Carlo needed (the
      enumeration is the complete inventory predicate, not a
      sampled channel census).
  C3  canonical assemblies stay >= tau=2 under class scope.
  C4  the full check_d4 report is identical row vs class.
  R1  rename principle: the row-scope surviving channel bonds all
      have EQUAL final names on both faces (displaced-pair / same-
      tag recombination); the kill case is the one-face split
      D1T.E 'p-t' vs L1.W 'p-t-lk1'.  Renames are structurally
      blind to displaced pairs — the static reason RS1/RS2
      falsified the elimination reading.
"""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
EV_AND = os.path.join(REPO, "evidence",
                      "2026-10-06-body-conjunction-builds")
EV_GC = os.path.join(REPO, "evidence", "2026-10-07-glue-class")
for p in (REPO, EV_AND):
    if p not in sys.path:
        sys.path.insert(0, p)

from molasp.offchannel import (  # noqa: E402
    apply_lock_glue_scope, canonical_assembly, check_d4,
    glue_class, glue_class_census, lock_glue_scope_reports,
    matched_strength, scope_bond_identity)
from tiles_and import BUILD1, BUILD2, BUILD3  # noqa: E402


class TestGlueClassLabels(unittest.TestCase):
    def test_labels_and_lk_tag_stripping(self):
        self.assertEqual(glue_class("q-t"), "value")
        self.assertEqual(glue_class("p-t-done-lk3"), "value")
        self.assertEqual(glue_class("p-f-done"), "value")
        self.assertEqual(glue_class("SP2"), "spine")
        self.assertEqual(glue_class("go2"), "go")
        self.assertEqual(glue_class("go2-lk2"), "go")
        self.assertEqual(glue_class("and1_r"), "and")
        self.assertEqual(glue_class("base2"), "base")
        self.assertEqual(glue_class("vb1"), "base")
        self.assertEqual(glue_class("f-p"), "fact")
        self.assertEqual(glue_class("w1-relay"), "relay")
        self.assertEqual(glue_class("cap3"), "cap")
        self.assertEqual(glue_class("pf-cap"), "cap")


class TestClassScopeKnob(unittest.TestCase):
    """scope 'class' = row PLUS the never-qualified classes; row
    itself is unchanged (tick-29/30 semantics preserved)."""

    @classmethod
    def setUpClass(cls):
        cls.canon = canonical_assembly(BUILD1)
        cls.row = apply_lock_glue_scope(BUILD1, "row", cls.canon)
        cls.cls = apply_lock_glue_scope(BUILD1, "class", cls.canon)

    def test_row_leaves_go_class_bond_unrenamed(self):
        self.assertEqual(self.row["tiles"]["S2"]["E"], "go2")
        self.assertEqual(self.row["tiles"]["D2T"]["W"], "go2")

    def test_class_qualifies_go_entry_on_both_faces(self):
        self.assertEqual(self.cls["tiles"]["S2"]["E"], "go2-lk2")
        self.assertEqual(self.cls["tiles"]["D2T"]["W"], "go2-lk2")

    def test_class_exempts_strength2_spine_self_bonds(self):
        self.assertEqual(self.cls["tiles"]["S2"]["S"], "SP2")
        self.assertEqual(self.cls["tiles"]["S2"]["N"], "SP3")

    def test_class_preserves_canonical_tau2_everywhere(self):
        for name, b in (("BUILD1", BUILD1), ("BUILD2", BUILD2),
                        ("BUILD3", BUILD3)):
            c = canonical_assembly(b)
            cb = apply_lock_glue_scope(b, "class", c)
            for site, t in c.items():
                self.assertGreaterEqual(
                    matched_strength(cb, c, site, t), 2,
                    f"{name} {site} falls below tau=2 under class")


class TestCensusInertness(unittest.TestCase):
    """C1: no shared structural glue in the three inventories."""

    def test_no_shared_nonvalue_glue_any_build(self):
        for name, b in (("BUILD1", BUILD1), ("BUILD2", BUILD2),
                        ("BUILD3", BUILD3)):
            cen = glue_class_census(b, canonical_assembly(b))
            shared = [g for g, v in cen.items()
                      if v["status"] == "shared" and v["class"] != "value"]
            self.assertEqual(shared, [], f"{name}: {shared}")

    def test_build1_statuses(self):
        cen = glue_class_census(BUILD1, canonical_assembly(BUILD1))
        self.assertEqual(cen["go2"]["status"], "canonical_pair")
        self.assertEqual(cen["and1_r"]["status"], "canonical_pair")
        self.assertEqual(cen["base2"]["status"], "canonical_pair")
        self.assertEqual(cen["SP2"]["status"], "canonical_pair")
        self.assertEqual(cen["f-p"]["status"], "seed_bond")
        self.assertEqual(cen["vb1"]["status"], "seed_bond")
        self.assertEqual(cen["cap3"]["status"], "inert_single")
        self.assertEqual(cen["q-t"]["status"], "shared")

    def test_build3_w1_relay_is_canonical_pair(self):
        cen = glue_class_census(BUILD3, canonical_assembly(BUILD3))
        self.assertEqual(cen["w1-relay"]["status"], "canonical_pair")
        self.assertEqual(cen["pf-cap"]["status"], "inert_single")


class TestMatchingPredicateIdentity(unittest.TestCase):
    """C2/C4: the class boundary is inert — exact predicate proof."""

    def test_row_vs_class_diff_empty_all_builds(self):
        for name, b in (("BUILD1", BUILD1), ("BUILD2", BUILD2),
                        ("BUILD3", BUILD3)):
            self.assertEqual(
                scope_bond_identity(b, "row", "class"), {},
                f"{name}: class scope changed the match predicate")

    def test_checker_detects_real_differences(self):
        # sanity: family vs row DOES split faces (the lock reads)
        diff = scope_bond_identity(BUILD1, "family", "row")
        self.assertIn("D1T.E<->L1.W", diff)
        self.assertEqual(len(diff), 10)

    def test_d4_report_identical_row_vs_class(self):
        for name, b in (("BUILD1", BUILD1), ("BUILD2", BUILD2),
                        ("BUILD3", BUILD3)):
            c = canonical_assembly(b)
            self.assertEqual(
                check_d4(apply_lock_glue_scope(b, "row", c), c),
                check_d4(apply_lock_glue_scope(b, "class", c), c),
                f"{name}: d4 differs row vs class")

    def test_reports_expose_class_with_row_identical_hazards(self):
        rep = lock_glue_scope_reports(BUILD1)
        self.assertEqual(rep["class"]["lock_hazards"], {})
        self.assertEqual(rep["class"]["lock_hazards"], rep["row"]["lock_hazards"])


class TestRenamePrinciple(unittest.TestCase):
    """R1: survivors bond by equal final names; kills are splits."""

    @classmethod
    def setUpClass(cls):
        cls.row = apply_lock_glue_scope(
            BUILD1, "row", canonical_assembly(BUILD1))

    def test_surviving_channel_bonds_equal_final_names(self):
        t = self.row["tiles"]
        pairs = (("Vp", "N", "DBr", "S"),   # vertical lock stack (H3)
                 ("D2T", "N", "DAr", "S"),  # relay-stack repair N arm
                 ("D2T", "S", "V0p", "N"),  # relay-stack repair S arm
                 ("D2T", "W", "S2", "E"))   # W arm — the go2 class glue
        for a, fa, c, fc in pairs:
            self.assertEqual(t[a][fa], t[c][fc],
                             f"{a}.{fa} vs {c}.{fc} split")

    def test_kill_case_is_a_one_face_split(self):
        t = self.row["tiles"]
        self.assertEqual(t["D1T"]["E"], "p-t")
        self.assertEqual(t["L1"]["W"], "p-t-lk1")
        self.assertNotEqual(t["D1T"]["E"], t["L1"]["W"])


class TestReceiptPin(unittest.TestCase):
    """The published receipt carries the closure, machine-read."""

    @classmethod
    def setUpClass(cls):
        with open(os.path.join(EV_GC, "glue_class.out")) as fh:
            cls.rep = json.load(fh)

    def test_all_builds_closed_inert_in_receipt(self):
        for name in ("BUILD1", "BUILD2", "BUILD3"):
            b = self.rep["builds"][name]
            self.assertEqual(b["shared_nonvalue_glues"], [])
            self.assertEqual(b["row_vs_class_bond_diff"], {})
            self.assertTrue(b["d4_report_identical_row_vs_class"])
            self.assertTrue(all(v >= 2 for v in
                                b["class_canonical_bonds"].values()))

    def test_receipt_rename_principle(self):
        r1 = self.rep["r1_rename_principle"]
        self.assertTrue(r1["all_survivors_equal"])
        self.assertTrue(r1["split_is_real"])
        self.assertEqual(r1["kill_case_split_final_names"]["D1T.E"],
                         "p-t")


if __name__ == "__main__":
    unittest.main()
