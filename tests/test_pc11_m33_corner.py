"""Tick-161 pins: the LAST corner (designs/012 relay, k_r=3 x
k_w=3), tested live from molasp.parity.producible.

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
from tools.pc11_contention_structure import all_ideals
from tools.pc11_m33_corner import (ANCHOR, ROWS, build_receipt,
                                   corner_square, census, program_for,
                                   relay_static, unified_law)

SLOW_ROWS = (6, 7, 9)          # live census pins (fast heights)
RECEIPT_PATH = os.path.join(ROOT, "evidence", "2026-10-22-pc11-m33-corner",
                            "m33.json")
RECEIPT_SHA256 = (
    "8694994d218ace5c025d255b8f4f74639e96c58b053c0fcaac28d620a29ba528")


class TestLastCornerFragment(unittest.TestCase):
    """The (3,3) shape compiles with three relayed conduits and the
    unexamined neighbours still refuse."""

    def test_anchor_compiles_and_decodes(self):
        build = compile_program(ANCHOR, name="pin_anchor_m33")
        self.assertEqual(build["rows"][6], "w")
        self.assertEqual(build["rows"][5], "r")

    def test_relay_carries_three_conduits(self):
        for r in (6, 8):
            s = relay_static(r)
            self.assertTrue(s["r_conduit_count_is_k"], s)
            self.assertEqual(len(s["w_conduits"]), 3, s)
            self.assertEqual(s["r_conduits"], ["Cr", "Cr2", "Cr3"], s)
            self.assertEqual(s["w_conduits"], ["Cw", "Cw2", "Cw3"], s)
            self.assertTrue(s["relay_value_typed_north"], s)
            self.assertTrue(s["above_reads_only_value"], s)
            self.assertTrue(s["body_glues_each_exactly_twice"], s)
            self.assertEqual(
                sorted(s["body_glue_occurrences"]),
                ["unit1_r", "unit1_w", "unit2_r", "unit2_w",
                 "unit3_r", "unit3_w"],
                s)

    def test_intermediate_and_body_still_refused(self):
        with self.assertRaises(UnsupportedGeometry):
            compile_program(
                "p. q. s. q2 :- p. r :- q2, s. r :- q2. r :- q2. "
                "w :- r. w :- r. w :- r.", name="pin_and_m33")

    def test_and_consumer_of_relayed_head_refused(self):
        with self.assertRaises(UnsupportedGeometry):
            compile_program(
                "p. q. s. q2 :- p. r :- q2. r :- q2. r :- q2. "
                "w :- r, q2. w :- r. w :- r.", name="pin_and_cons_m33")

    def test_second_relayed_head_refused(self):
        with self.assertRaises(UnsupportedGeometry):
            compile_program(
                "p. q. s. q2 :- p. r :- q2. r :- q2. r :- q2. "
                "w :- r. w :- r. w :- r. z :- w. z :- w.",
                name="pin_stack_m33")

    def test_single_body_chain_depth_still_refused(self):
        with self.assertRaises(UnsupportedGeometry):
            compile_program(
                "p. q. q2 :- p. r :- q2. w :- r. z :- w.",
                name="pin_depth_m33")


class TestLastCornerCensus(unittest.TestCase):
    """The square-closing composition question, answered live."""

    def test_mixed_total_law_at_pinned_heights(self):
        for r in SLOW_ROWS:
            c = census(r)
            self.assertTrue(c["presence_equals_ideals"], (r, c))
            self.assertEqual(c["presence"], comb(r + 4, 4), (r, c))
            self.assertEqual(c["assemblies"], c["mixed_law"], (r, c))
            self.assertNotEqual(c["assemblies"], c["collapsed_law"], r)
            self.assertNotEqual(c["assemblies"], c["additive_law"], r)
            self.assertNotEqual(c["assemblies"], c["power_law"], r)
            # closed form of the (3,3) total law, derived
            # independently
            closed = (comb(r + 4, 4) + (r + 1) * (3 * r + 2)
                      + 6 * comb(r + 2, 2))
            self.assertEqual(c["assemblies"], closed, (r, closed))

    def test_corner_formulas(self):
        for r in SLOW_ROWS:
            c = census(r)
            self.assertEqual(c["c_r"], (r + 1) * (3 * r + 2) // 2, r)
            self.assertEqual(c["c_w"], comb(r + 2, 2), r)

    def test_fibers_are_exactly_one_three_nine(self):
        for r in SLOW_ROWS:
            c = census(r)
            hist = c["fiber_hist"]
            self.assertEqual(sorted(hist), [1, 3, 9], (r, hist))
            self.assertEqual(hist[3], c["c_r"] - c["c_w"], (r, hist))
            self.assertEqual(hist[9], c["c_w"], (r, hist))
            self.assertTrue(c["fiber2_never"], r)
            self.assertTrue(c["fiber4_never"], r)
            self.assertTrue(c["fiber6_never"], r)
            self.assertTrue(c["fiber8_never"], r)
            self.assertTrue(c["fiber3_shapes_are_Cr_minus_Cw"], r)
            self.assertTrue(c["fiber9_shapes_are_Cw"], r)
            self.assertTrue(c["elementwise_product_structure"], r)
            self.assertTrue(c["readings_differ_only_at_site_pairs"], r)

    def test_conduit_choices_split_by_head(self):
        for r in SLOW_ROWS:
            c = census(r)
            self.assertEqual(
                c["conduit_choices_at_free_sites"]["row_n_minus_1"],
                ["Cr", "Cr2", "Cr3"], (r, c))
            self.assertEqual(
                c["conduit_choices_at_free_sites"]["row_n"],
                ["Cw", "Cw2", "Cw3"], (r, c))

    def test_decor_extension_shape(self):
        self.assertEqual(program_for(7),
                         "p. q. t. s. q2 :- p. r :- q2. r :- q2. "
                         "r :- q2. w :- r. w :- r. w :- r.")
        self.assertEqual(program_for(12).count("."),
                         program_for(11).count(".") + 1)


class TestFourCornerSquare(unittest.TestCase):
    """The unified law over the whole {k_r, k_w} square."""

    def test_unified_law_matches_m33_live(self):
        for r in SLOW_ROWS:
            self.assertEqual(census(r)["assemblies"],
                             unified_law(r, 3, 3), r)

    def test_unified_law_matches_all_prior_receipts(self):
        # three prior receipts (21 scalars) + n=6 measured live
        sq = corner_square({str(r): census(r) for r in (6,)})
        self.assertTrue(sq["all_four_corners_hold"], sq)
        self.assertEqual(sq["scalars_checked"], 22, sq)
        for key in ("2x2", "3x2", "2x3", "3x3"):
            self.assertIn(key, sq["corners"])
            self.assertTrue(
                sq["corners"][key]["unified_law_holds_everywhere"], key)

    def test_unified_law_at_all_corners_n6(self):
        # the four corners at the anchor height, hand-computed:
        # (2,2)=336, (3,2)=434, (2,3)=392, (3,3)=518
        for (k_r, k_w), total in {(2, 2): 336, (3, 2): 434,
                                  (2, 3): 392, (3, 3): 518}.items():
            self.assertEqual(unified_law(6, k_r, k_w), total,
                             (k_r, k_w))


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
                     "corner_formulas_all_heights",
                     "four_corner_square_complete"):
            self.assertTrue(receipt["summary"][name], name)
        self.assertEqual(receipt["rows_measured"], list(ROWS))
        for r in ROWS:
            c = receipt["censuses"][str(r)]
            self.assertTrue(c["mixed_law_holds"], (r, c))
            self.assertTrue(c["collapsed_falsified"], (r, c))
            self.assertTrue(c["additive_falsified"], (r, c))
            self.assertTrue(c["power_falsified"], (r, c))
            self.assertTrue(c["fiber2_never"], (r, c))
            self.assertTrue(c["fiber4_never"], (r, c))
            self.assertTrue(c["fiber6_never"], (r, c))
            self.assertTrue(c["fiber8_never"], (r, c))
        self.assertTrue(receipt["corner_square"]["all_four_corners_hold"])
        self.assertEqual(receipt["corner_square"]["scalars_checked"], 28)
        # the (3,3) prediction of record, pinned scalar-by-scalar
        predicted = {6: 518, 7: 730, 8: 999, 9: 1335, 10: 1749,
                     11: 2253, 12: 2860}
        for r, total in predicted.items():
            self.assertEqual(receipt["censuses"][str(r)]["assemblies"],
                             total, r)


if __name__ == "__main__":
    unittest.main()
