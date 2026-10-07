"""d4 b=1 transient layer split pins (tick 32, SON-4778) — the
designs/004 follow-up from the tick-31 half-falsified row-scope
sweep (RS1/RS2 falsified, RS3/RS4 confirmed): the emit-time census
must report the layer that actually carried the kinetic read-cost,
so a static ``lock_hazards {}`` can never again be misread as
kinetic elimination.

Measured on BUILD1 (row-scope receipt, RS1): every static
canonical-background lock hazard died under row scope, yet reads
still blocked at 0.144 = 72/500 — carried by b=1 channels: the
west-substitution pair {west D2T -> Vp@(3,2)} (exactly the
smoke-predicted D2T+Vp mutual pair) and the non-west-axis
DBr@(3,3), 72/500 each, co-occurring.  The west-bounded deep probe
sees the first class only; the caveat ships inside the report
(``pair_probe_bound``).
"""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EV_AND = os.path.join(ROOT, "evidence", "2026-10-06-body-conjunction-builds")
EV_ROW = os.path.join(ROOT, "evidence", "2026-10-07-row-scope-ktam")
for p in (EV_AND,):
    if p not in sys.path:
        sys.path.insert(0, p)

from molasp.compiler import compile_program  # noqa: E402
from molasp.offchannel import (  # noqa: E402
    apply_lock_glue_scope, canonical_assembly, check_d4, d4_report_lines)
from tiles_and import BUILD1  # noqa: E402


def row_receipt_arms():
    arms = {}
    with open(os.path.join(EV_ROW, "row_scope.out")) as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if isinstance(rec, dict) and "key" in rec:
                arms[rec["key"]] = rec
    return arms


class TestStaticSplitFamily(unittest.TestCase):
    """Family scope on BUILD1: every static lock hazard is b=1 —
    the famous squatters ARE the transient layer (which is why they
    track equilibrium occupancy, not stable holds)."""

    @classmethod
    def setUpClass(cls):
        cls.canon = canonical_assembly(BUILD1)
        cls.rep = check_d4(BUILD1, cls.canon)

    def test_stable_class_is_empty(self):
        self.assertEqual(self.rep["lock_hazards_stable"], {})

    def test_transient_class_is_the_census_pair(self):
        self.assertEqual(self.rep["lock_hazards_transient"],
                         {"3,1": {"V0p": 1}, "3,2": {"Vp": 1}})
        self.assertEqual(self.rep["lock_hazards_transient"],
                         self.rep["lock_hazards"])

    def test_split_covers_every_hazard_exactly_once(self):
        for site, sq in self.rep["lock_hazards"].items():
            for tile, b in sq.items():
                in_stable = tile in self.rep["lock_hazards_stable"].get(
                    site, {})
                in_trans = tile in self.rep["lock_hazards_transient"].get(
                    site, {})
                self.assertTrue(in_stable != in_trans,
                                f"{tile}@{site} b={b} misclassified")


class TestRowSplitSurvivesAsPairChannels(unittest.TestCase):
    """Row scope kills both canonical-background classes — and the
    census now says what survives instead: the b=1 pair channels."""

    @classmethod
    def setUpClass(cls):
        cls.canon = canonical_assembly(BUILD1)
        row_build = apply_lock_glue_scope(BUILD1, "row", cls.canon)
        cls.rep = check_d4(row_build, cls.canon)

    def test_both_static_classes_die(self):
        self.assertEqual(self.rep["lock_hazards_stable"], {})
        self.assertEqual(self.rep["lock_hazards_transient"], {})

    def test_b1_pair_channels_survive(self):
        self.assertEqual(
            self.rep["lock_pair_channels"]["transient"],
            {"3,1": {"D1T": {"V0p": 1}}, "3,2": {"D2T": {"Vp": 1}}})

    def test_stable_pair_channels_absent(self):
        self.assertEqual(self.rep["lock_pair_channels"]["stable"], {})


class TestReceiptCrossCheck(unittest.TestCase):
    """The (3,2) pair channel IS the measured kinetic survivor; the
    probe's west-bounded coverage is recorded, not hidden."""

    @classmethod
    def setUpClass(cls):
        cls.canon = canonical_assembly(BUILD1)
        row_build = apply_lock_glue_scope(BUILD1, "row", cls.canon)
        cls.rep = check_d4(row_build, cls.canon)
        cls.row_b1 = row_receipt_arms()["row_build1"]

    def test_receipt_survivors_are_exactly_the_mutual_pair(self):
        self.assertEqual(self.row_b1["lock_squats"],
                         {"3,2:Vp": 72, "3,3:DBr": 72})

    def test_read_block_is_the_mutual_pair_class(self):
        self.assertEqual(self.row_b1["blocked_frac"], 0.144)
        self.assertAlmostEqual(self.row_b1["blocked_frac"], 72 / 500)

    def test_pair_channel_names_the_measured_survivor(self):
        # west D2T + channel Vp = the smoke-predicted mutual pair
        self.assertEqual(
            self.rep["lock_pair_channels"]["transient"]["3,2"],
            {"D2T": {"Vp": 1}})

    def test_dbr_survivor_is_outside_the_west_bounded_probe(self):
        self.assertNotIn("DBr", json.dumps(self.rep["lock_deep_probe"]))
        bound = self.rep["pair_probe_bound"]
        self.assertIn("west", bound)
        self.assertIn("DBr", bound)

    def test_measured_context_quotes_the_row_sweep(self):
        ctx = self.rep["measured_context"]["row_scope_kinetics"]
        self.assertEqual(ctx["read_lock_squat_blocked_dG0.5"], 0.144)
        self.assertEqual(ctx["surviving_lock_squats_of_500"]["V0p@(3,1)"], 0)
        self.assertEqual(ctx["stable_b2_repair_fill"], 0.162)
        self.assertTrue(any("row_scope.out" in s for s in
                            self.rep["measured_context"]["sources"]))


class TestCompilerWiringAndLines(unittest.TestCase):
    """The split ships at emit time (build['d4']) and the human
    block speaks the bond classes."""

    P_AND = "p.\nq.\nr :- p, q.\n"

    def test_emit_report_carries_the_split(self):
        build = compile_program(self.P_AND, name="and")
        for key in ("lock_hazards_stable", "lock_hazards_transient",
                    "lock_pair_channels", "pair_probe_bound"):
            self.assertIn(key, build["d4"])
        # the compiled AND build is BUILD1 up to tile naming (the
        # row-2 squatter is V2p there): pin the transient class to
        # the same site and bond as the canonical census hazard,
        # not to a hand-copied tile name
        self.assertEqual(build["d4"]["lock_hazards_transient"]["3,2"],
                         build["d4"]["lock_hazards"]["3,2"])
        self.assertEqual(
            list(build["d4"]["lock_hazards_transient"]["3,2"].values()),
            [1])

    def test_report_lines_speak_the_classes(self):
        build = compile_program(self.P_AND, name="and")
        text = "\n".join(d4_report_lines(build["d4"]))
        self.assertIn("b=1 transient", text)
        self.assertIn("pair channel", text)
        self.assertIn("0.144", text)


if __name__ == "__main__":
    unittest.main()
