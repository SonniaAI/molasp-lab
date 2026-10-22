"""Tick-158 pins: the two-or-pair family MULTIPLIES (designs/012
northward truth-OR relay), tested live from molasp.parity.producible.

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
from tools.pc11_two_or import (ANCHOR, ROWS, build_receipt, census,
                               program_for, relay_static)

SLOW_ROWS = (6, 7, 9)          # live census pins (fast heights)
RECEIPT_PATH = os.path.join(ROOT, "evidence", "2026-10-22-pc11-two-or",
                            "two_or.json")
RECEIPT_SHA256 = (
    "21b4734494e6dcf2e9f46470b6f86aa36a2f70823b653543c1966e1f3ca3a6a9")


class TestRelayFragment(unittest.TestCase):
    """The fragment extension compiles the two-or shape and still
    refuses the unexamined neighbours."""

    def test_anchor_compiles_and_decodes(self):
        build = compile_program(ANCHOR, name="pin_anchor")
        self.assertEqual(build["rows"][6], "w")
        self.assertEqual(build["rows"][5], "r")

    def test_relay_is_value_typed(self):
        for r in (6, 8):
            s = relay_static(r)
            self.assertTrue(s["relay_value_typed_north"], s)
            self.assertTrue(s["above_reads_only_value"], s)
            self.assertTrue(s["body_glues_each_exactly_twice"], s)

    def test_intermediate_and_body_still_refused(self):
        with self.assertRaises(UnsupportedGeometry):
            compile_program(
                "p. q. s. q2 :- p. r :- q2, s. r :- q2. "
                "w :- r. w :- r.", name="pin_and")

    def test_and_consumer_of_relayed_head_refused(self):
        with self.assertRaises(UnsupportedGeometry):
            compile_program(
                "p. q. s. q2 :- p. r :- q2. r :- q2. "
                "w :- r. w :- r, q2.", name="pin_and_cons")

    def test_second_relayed_head_refused(self):
        with self.assertRaises(UnsupportedGeometry):
            compile_program(
                "p. q. s. q2 :- p. r :- q2. r :- q2. "
                "w :- r. w :- r. z :- w. z :- w.", name="pin_stack")

    def test_single_body_chain_depth_still_refused(self):
        with self.assertRaises(UnsupportedGeometry):
            compile_program(
                "p. q2 :- p. r :- q2. w :- r. z :- w.",
                name="pin_depth")


class TestTwoOrCensus(unittest.TestCase):
    """The additive-vs-multiplicative question, answered live."""

    def test_multiplicative_at_pinned_heights(self):
        for r in SLOW_ROWS:
            c = census(r)
            self.assertTrue(c["presence_equals_ideals"], (r, c))
            self.assertEqual(c["presence"], comb(r + 4, 4), (r, c))
            self.assertEqual(c["assemblies"], c["multiplicative_law"],
                             (r, c))
            self.assertNotEqual(c["assemblies"], c["additive_law"], r)
            self.assertNotEqual(c["assemblies"], c["collapsed_law"], r)

    def test_corner_formulas(self):
        for r in SLOW_ROWS:
            c = census(r)
            self.assertEqual(c["c_r"], (r + 1) * (3 * r + 2) // 2, r)
            self.assertEqual(c["c_w"], comb(r + 2, 2), r)

    def test_fiber_never_three(self):
        for r in SLOW_ROWS:
            c = census(r)
            self.assertTrue(c["fiber3_never"], (r, c["fiber_hist"]))
            self.assertTrue(c["fiber2_shapes_are_Cr_minus_Cw"], r)
            self.assertTrue(c["fiber4_shapes_are_Cw"], r)
            self.assertTrue(c["elementwise_product_structure"], r)
            self.assertTrue(c["readings_differ_only_at_site_pairs"], r)

    def test_decor_extension_shape(self):
        self.assertEqual(program_for(7),
                         "p. q. t. s. q2 :- p. r :- q2. r :- q2. "
                         "w :- r. w :- r.")
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
        for name in ("multiplicative_all_heights",
                     "presence_box_law_all_heights",
                     "fiber_structure_all_heights",
                     "relay_value_typed_all_heights",
                     "corner_formulas_all_heights"):
            self.assertTrue(receipt["summary"][name], name)
        self.assertEqual(receipt["rows_measured"], list(ROWS))
        for r in ROWS:
            c = receipt["censuses"][str(r)]
            self.assertTrue(c["multiplicative_holds"], (r, c))
            self.assertTrue(c["additive_falsified"], (r, c))
            self.assertTrue(c["collapsed_falsified"], (r, c))
            self.assertTrue(c["fiber3_never"], (r, c))


if __name__ == "__main__":
    unittest.main()
