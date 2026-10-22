"""Tick-160 pins: the MIRROR mixed point (designs/012 relay,
k_r=2 x k_w=3), tested live from molasp.parity.producible.

Every scalar is re-derived live on each run (no stored constants for
the census results); the receipt hash pins byte stability of the
recorded evidence.
"""

import hashlib
import json
import os
import sys
import unittest
from math import comb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from molasp.compiler import (CompileError, UnsupportedGeometry,
                             compile_program)
from tools.pc11_contention_structure import all_ideals, assembly_sets
from tools.pc11_mixed_mirror import (ANCHOR, ROWS, build_receipt, census,
                                     program_for, relay_static)

SLOW_ROWS = (6, 7, 9)          # live census pins (fast heights)
RECEIPT_PATH = os.path.join(ROOT, "evidence", "2026-10-22-pc11-mixed-mirror",
                            "mixed_mirror.json")
RECEIPT_SHA256 = (
    "b585cdc18f8475a441f0d6e56df4e29560163c239569aceacdf1c5404a27efef")


class TestMirrorRelayFragment(unittest.TestCase):
    """The mirror shape compiles with two relayed conduits and the
    unexamined neighbours still refuse."""

    def test_anchor_compiles_and_decodes(self):
        build = compile_program(ANCHOR, name="pin_anchor_m23")
        self.assertEqual(build["rows"][6], "w")
        self.assertEqual(build["rows"][5], "r")

    def test_relay_carries_two_conduits(self):
        for r in (6, 8):
            s = relay_static(r)
            self.assertTrue(s["r_conduit_count_is_k"], s)
            self.assertEqual(len(s["w_conduits"]), 3, s)
            self.assertTrue(s["relay_value_typed_north"], s)
            self.assertTrue(s["above_reads_only_value"], s)
            self.assertTrue(s["body_glues_each_exactly_twice"], s)
            self.assertEqual(
                sorted(s["body_glue_occurrences"]),
                ["unit1_r", "unit1_w", "unit2_r", "unit2_w", "unit3_w"],
                s)

    def test_intermediate_and_body_still_refused(self):
        with self.assertRaises(UnsupportedGeometry):
            compile_program(
                "p. q. s. q2 :- p. r :- q2, s. r :- q2. "
                "w :- r. w :- r. w :- r.", name="pin_and_m23")

    def test_and_consumer_of_relayed_head_refused(self):
        with self.assertRaises(UnsupportedGeometry):
            compile_program(
                "p. q. s. q2 :- p. r :- q2. r :- q2. "
                "w :- r. w :- r, q2. w :- r.", name="pin_and_cons_m23")

    def test_stacked_relay_chain_compiles_and_censuses(self):
        """Tick-164 boundary move (designs/013 §1): this stacked
        chain is the admitted depth-3 fragment and censuses exactly
        on the nested-shell law at a NEVER-PINNED mixed point:
        [2,3,2] at n=7 -> 1069."""
        prog = ("p. q. s. q2 :- p. r :- q2. r :- q2. "
                "w :- r. w :- r. w :- r. z :- w. z :- w.")
        build = compile_program(prog, name="pin_stack_m23")
        self.assertGreater(len(build["tiles"]), 0)
        assemblies, _ = assembly_sets(prog, "pin_stack_m23_census")
        self.assertEqual(len(assemblies), 1069)

    def test_single_body_chain_depth_still_refused(self):
        with self.assertRaises(UnsupportedGeometry):
            compile_program(
                "p. q. q2 :- p. r :- q2. w :- r. z :- w.",
                name="pin_depth_m23")


class TestMirrorCensus(unittest.TestCase):
    """The mirror composition question, answered live."""

    def test_mixed_total_law_at_pinned_heights(self):
        for r in SLOW_ROWS:
            c = census(r)
            self.assertTrue(c["presence_equals_ideals"], (r, c))
            self.assertEqual(c["presence"], comb(r + 4, 4), (r, c))
            self.assertEqual(c["assemblies"], c["mixed_law"], (r, c))
            self.assertNotEqual(c["assemblies"], c["collapsed_law"], r)
            self.assertNotEqual(c["assemblies"], c["additive_law"], r)
            self.assertNotEqual(c["assemblies"], c["power_law"], r)
            # closed form of the mirror total law, derived
            # independently
            closed = (comb(r + 4, 4) + (r + 1) * (3 * r + 2) // 2
                      + 4 * comb(r + 2, 2))
            self.assertEqual(c["assemblies"], closed, (r, closed))

    def test_corner_formulas(self):
        for r in SLOW_ROWS:
            c = census(r)
            self.assertEqual(c["c_r"], (r + 1) * (3 * r + 2) // 2, r)
            self.assertEqual(c["c_w"], comb(r + 2, 2), r)

    def test_fibers_are_exactly_one_two_six(self):
        for r in SLOW_ROWS:
            c = census(r)
            hist = c["fiber_hist"]
            self.assertEqual(sorted(hist), [1, 2, 6], (r, hist))
            self.assertEqual(hist[2], c["c_r"] - c["c_w"], (r, hist))
            self.assertEqual(hist[6], c["c_w"], (r, hist))
            self.assertTrue(c["fiber3_never"], r)
            self.assertTrue(c["fiber4_never"], r)
            self.assertTrue(c["fiber8_never"], r)
            self.assertTrue(c["fiber2_shapes_are_Cr_minus_Cw"], r)
            self.assertTrue(c["fiber6_shapes_are_Cw"], r)
            self.assertTrue(c["elementwise_product_structure"], r)
            self.assertTrue(c["readings_differ_only_at_site_pairs"], r)

    def test_conduit_choices_split_by_head(self):
        for r in SLOW_ROWS:
            c = census(r)
            self.assertEqual(
                c["conduit_choices_at_free_sites"]["row_n_minus_1"],
                ["Cr", "Cr2"], (r, c))
            self.assertEqual(
                c["conduit_choices_at_free_sites"]["row_n"],
                ["Cw", "Cw2", "Cw3"], (r, c))

    def test_decor_extension_shape(self):
        self.assertEqual(program_for(7),
                         "p. q. t. s. q2 :- p. r :- q2. r :- q2. "
                         "w :- r. w :- r. w :- r.")
        self.assertEqual(program_for(12).count("."),
                         program_for(11).count(".") + 1)


class TestReceiptStability(unittest.TestCase):
    """The recorded evidence is a byte-stable pure function."""

    def test_receipt_bytes_stable(self):
        if not os.path.exists(RECEIPT_PATH):
            self.skipTest("receipt not built in this checkout")
        with open(RECEIPT_PATH, "rb") as fh:
            data = fh.read()
        self.assertEqual(hashlib.sha256(data).hexdigest(),
                         RECEIPT_SHA256)

    def test_live_receipt_reproduction(self):
        if not os.path.exists(RECEIPT_PATH):
            self.skipTest("receipt not built in this checkout")
        live = json.dumps(build_receipt(), indent=2, sort_keys=True,
                          default=sorted) + "\n"
        with open(RECEIPT_PATH) as fh:
            self.assertEqual(live, fh.read())

    def test_receipt_summary_flags(self):
        if not os.path.exists(RECEIPT_PATH):
            self.skipTest("receipt not built in this checkout")
        with open(RECEIPT_PATH) as fh:
            receipt = json.load(fh)
        for name in ("mixed_total_law_all_heights",
                     "presence_box_law_all_heights",
                     "fiber_structure_all_heights",
                     "relay_static_all_heights",
                     "corner_formulas_all_heights"):
            self.assertTrue(receipt["summary"][name], name)
        self.assertEqual(receipt["rows_measured"], list(ROWS))
        for r in ROWS:
            c = receipt["censuses"][str(r)]
            self.assertTrue(c["mixed_law_holds"], (r, c))
            self.assertTrue(c["collapsed_falsified"], (r, c))
            self.assertTrue(c["additive_falsified"], (r, c))
            self.assertTrue(c["power_falsified"], (r, c))
            self.assertTrue(c["fiber3_never"], (r, c))
            self.assertTrue(c["fiber4_never"], (r, c))
            self.assertTrue(c["fiber8_never"], (r, c))
        # the mirror prediction of record, pinned scalar-by-scalar
        predicted = {6: 392, 7: 566, 8: 792, 9: 1080, 10: 1441,
                     11: 1887, 12: 2431}
        for r, total in predicted.items():
            self.assertEqual(receipt["censuses"][str(r)]["assemblies"],
                             total, r)


if __name__ == "__main__":
    unittest.main()
