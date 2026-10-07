"""d4 off-channel census pins (tick 28, SON-4778) — designs/004
acceptance criteria A1-A4, machine-checked.

A1 pins check_d4 on BUILD1 to the published tick-24 census receipt
(evidence/2026-10-07-repair-mechanism/trap_census.out) AND to a live
recompute by the independent measurement implementation
(trap_census.py) — receipt pin catches serialization drift, live pin
catches implementation drift.
"""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EV_AND = os.path.join(os.path.dirname(HERE), "evidence",
                      "2026-10-06-body-conjunction-builds")
EV_REP = os.path.join(os.path.dirname(HERE), "evidence",
                      "2026-10-07-repair-mechanism")
for p in (EV_AND, EV_REP):
    if p not in sys.path:
        sys.path.insert(0, p)

from molasp.compiler import compile_program  # noqa: E402
from molasp.offchannel import (  # noqa: E402
    canonical_assembly, check_d4, d4_report_lines)
from tiles_and import BUILD1, BUILD3  # noqa: E402
import trap_census  # noqa: E402

RECEIPT = json.load(
    open(os.path.join(EV_REP, "trap_census.out")))


class TestA1Build1CensusReproduced(unittest.TestCase):
    """check_d4 on BUILD1 returns exactly the tick-24 census."""

    @classmethod
    def setUpClass(cls):
        cls.canon = canonical_assembly(BUILD1)
        cls.rep = check_d4(BUILD1)
        cls.b1 = RECEIPT["systems"]["build1"]

    def test_canonical_assembly_is_the_receipt_canon(self):
        got = {f"{x},{y}": t for (x, y), t in self.canon.items()}
        self.assertEqual(got, RECEIPT["canonical"])

    def test_off_channel_table_exact(self):
        self.assertEqual(self.rep["off_channel"], self.b1["off_channel"])

    def test_per_species_sites_exact(self):
        self.assertEqual(self.rep["off_channel_sites_per_species"],
                         self.b1["off_channel_sites_per_species"])
        self.assertEqual(
            self.rep["off_channel_sites_per_species"]["Vp"],
            ["1,1", "1,2", "2,1", "2,3", "3,2"])
        self.assertEqual(
            self.rep["off_channel_sites_per_species"]["V0p"],
            ["1,1", "2,2", "3,1"])

    def test_lock_hazards_are_the_two_census_squatters(self):
        self.assertEqual(self.rep["lock_hazards"],
                         {"3,1": {"V0p": 1}, "3,2": {"Vp": 1}})

    def test_spine_sites_admit_no_squatter(self):
        for site in ("0,1", "0,2", "0,3"):
            self.assertNotIn(site, self.rep["off_channel"])

    def test_deep_probe_matches_and_names_the_misread(self):
        self.assertEqual(self.rep["lock_deep_probe"],
                         self.b1["lock_deep_probe"])
        # the L3-style misread: L2 holds (3,3) iff the west neighbour
        # exposes a q-t value glue (Vp or D2T) — A1's pinned probe
        self.assertEqual(self.rep["lock_misreads"]["3,3"],
                         {"Vp": {"L2": 1}, "D2T": {"L2": 1}})

    def test_independent_live_implementation_agrees(self):
        """The tick-24 measurement code, recomputed now, gives the
        same table — the lift is faithful, not receipt-copied."""
        self.assertEqual(trap_census.off_channel(BUILD1),
                         self.rep["off_channel"])


class TestA2NoFalseHazards(unittest.TestCase):
    """DAr, L3 and the spine tiles have unique glues: zero
    off-channel sites — d4 must not flag them."""

    @classmethod
    def setUpClass(cls):
        cls.rep = check_d4(BUILD1)

    def test_unique_glue_species_absent(self):
        for tile in ("DAr", "L3", "S1", "S2", "S3"):
            self.assertNotIn(
                tile, self.rep["off_channel_sites_per_species"], tile)


class TestA3NonGatingAndCompilerWired(unittest.TestCase):
    """d4 attaches a WARNING report at emit time; d2/d3 semantics
    and output shape are unchanged (structural signature parity is
    pinned separately in test_compiler_v01)."""

    P_AND = "p.\nq.\nr :- p, q.\n"

    def test_emit_attaches_warning_report(self):
        build = compile_program(self.P_AND, name="and")
        self.assertEqual(build["d4"]["severity"], "warning")
        # the compiled AND build is BUILD1 up to tile naming, so the
        # census class carries over: via tile squats the row-2 lock
        self.assertIn("3,2", build["d4"]["lock_hazards"])
        self.assertIn("3,1", build["d4"]["lock_hazards"])
        self.assertTrue(d4_report_lines(build["d4"]))

    def test_hazards_do_not_gate_emission(self):
        # BUILD1's hazards are the measured status quo; compiling the
        # same program succeeds and reports rather than raising
        build = compile_program(self.P_AND, name="and2")
        self.assertIn("tiles", build)

    def test_clean_build_empty_report(self):
        build = {
            "name": "synthetic_disjoint",
            "row_of": {"S1": 1, "D": 1, "V": 1, "L": 1},
            "seed": {(0, 0): "SP1", (1, 0): "f-a", (2, 0): "vb1",
                     (3, 0): "base1"},
            "tiles": {
                "S1": {"S": "SP1", "E": "go1", "N": "SP2"},
                "D": {"W": "go1", "S": "f-a", "E": "x1",
                      "N": "x1-done"},
                "V": {"W": "x1", "E": "x2", "S": "vb1", "N": "x3"},
                "L": {"W": "x2", "S": "base1", "N": "base2"},
            },
        }
        rep = check_d4(build)
        self.assertEqual(rep["severity"], "warning")
        self.assertEqual(rep["off_channel"], {})
        self.assertEqual(rep["lock_hazards"], {})
        self.assertEqual(rep["lock_misreads"], {})


class TestA4WrongCompileArm(unittest.TestCase):
    """On BUILD3 (W1 dropped-literal) d4 reports the same class of
    table — the check is inventory-driven, not tuned to build1."""

    @classmethod
    def setUpClass(cls):
        cls.rep = check_d4(BUILD3)

    def test_same_report_shape(self):
        for key in ("off_channel", "off_channel_sites_per_species",
                    "lock_hazards", "lock_deep_probe", "lock_misreads",
                    "measured_context"):
            self.assertIn(key, self.rep)

    def test_row_q_value_tile_squats_the_lock(self):
        # the V0p@(3,1) build1 hazard has a row-q analogue: V0q
        # bonds (3,1) at b=1 against the canonical background
        self.assertEqual(self.rep["lock_hazards"]["3,1"], {"V0q": 1})

    def test_spine_still_clean(self):
        for site in ("0,1", "0,2", "0,3"):
            self.assertNotIn(site, self.rep["off_channel"])

    def test_table_non_empty(self):
        self.assertTrue(self.rep["off_channel"])


if __name__ == "__main__":
    unittest.main()
