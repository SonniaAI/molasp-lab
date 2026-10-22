"""Tick-162 pins: the coefficient ladder DERIVED from staircase
geometry, tested live.

Every scalar is re-derived live on each run (no stored constants
for the census/derivation results); the receipt hash pins byte
stability of the recorded evidence.
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

from molasp.compiler import UnsupportedGeometry
from tools.pc11_coefficient_ladder import (
    DERIV_ROWS,
    GUARD_PROBES,
    c_r_closed,
    c_w_closed,
    decreasing_tuples_count,
    derivation_check,
    derived_unified_law,
    guard_probe,
    ladder_check,
    ladder_count,
    square_from_receipts,
)
from tools.pc11_contention_structure import all_ideals
from tools.pc11_coefficient_ladder import live_leg  # noqa: E402
from tools.pc11_two_or import program_for as t2u_program_for
from tools.pc11_m33_corner import program_for as m33_program_for

RECEIPT_PATH = os.path.join(
    ROOT, "evidence", "2026-10-22-pc11-coefficient-ladder", "ladder.json")
RECEIPT_SHA256 = (
    "ba74170238d211db46d56f4935662577c6d647a5d5869fc147b5c90bc321042f")


class TestBoxLawDerivation(unittest.TestCase):
    """L0: the hockey-stick DP witnesses |I| = C(n+4,4)."""

    def test_dp_matches_closed_form(self):
        for top in range(0, 13):
            for k in range(0, 5):
                self.assertEqual(
                    decreasing_tuples_count(top, k),
                    comb(top + k, k),
                    (top, k))


class TestRelayCornerDerivation(unittest.TestCase):
    """L1/L2/L3: |C_r| = (n+1)(3n+2)/2 from the three strata, the
    containment C_w <= C_r, and the two-strata difference set."""

    def test_l1_collapse_live(self):
        for n in DERIV_ROWS:
            self.assertEqual(c_r_closed(n), (n + 1) * (3 * n + 2) // 2)
            d = derivation_check(n)
            self.assertTrue(d["l1_collapse_to_polynomial"], d)
            self.assertTrue(d["l1_enum_count_equals_derived"], d)
            self.assertTrue(d["l1_strata_match_enumeration"], d)

    def test_l1_strata_counts(self):
        # n = 8: C(10,2) + 2*C(9,2) = 45 + 72 = 117 — identity
        # computed live, not a stored table.
        for n in (6, 9, 12):
            d = derivation_check(n)
            self.assertEqual(
                d["l1_strata"],
                {"full": comb(n + 2, 2), "shoulder": comb(n + 1, 2),
                 "even": comb(n + 1, 2)},
                d)
            self.assertEqual(sum(d["l1_strata"].values()), c_r_closed(n))

    def test_l2_l3_elementwise(self):
        for n in (6, 10):
            d = derivation_check(n)
            self.assertTrue(d["l2_containment_cw_subset_cr"], d)
            self.assertTrue(d["l2_overlap_equals_cw"], d)
            self.assertTrue(d["l3_diff_is_two_strata"], d)
            self.assertEqual(d["l3_diff_size"], n * (n + 1), d)

    def test_l2_enumerated_directly(self):
        from tools.pc11_contention_structure import ideals_containing
        n = 9
        cw = ideals_containing((1, n), n)
        cr = ideals_containing((1, n - 1), n)
        self.assertTrue(cw <= cr)
        self.assertEqual(len(cw), c_w_closed(n))
        self.assertEqual(len(cr), c_r_closed(n))


class TestDepthLadder(unittest.TestCase):
    """L4: |C^(m)| = sum (j+1) C(n-j+2, 2) exact at every reachable
    (m, n), and satisfying its hockey-stick recurrence beyond the
    census reach."""

    def test_ladder_exact_live(self):
        for m in (0, 1, 2, 3):
            for n in (5, 7, 10, 12):
                if n - m >= 2:
                    self.assertTrue(ladder_check(n, m)["equal"],
                                    (m, n, ladder_check(n, m)))

    def test_m1_is_the_relay_corner(self):
        for n in DERIV_ROWS:
            self.assertEqual(ladder_count(n, 1), c_r_closed(n))

    def test_recurrence_beyond_census(self):
        # Each deeper corner adds ONE stratum: h1 = n-m with (m+1)
        # h0-choices, so |C^(m)| - |C^(m-1)| = (m+1)*C(n-m+2,2).
        for m in (1, 2, 3, 4):
            for n in (13, 17, 20):
                self.assertEqual(
                    ladder_count(n, m) - ladder_count(n, m - 1),
                    (m + 1) * comb(n - m + 2, 2),
                    (m, n))


class TestSquareDerivedOnly(unittest.TestCase):
    """S1: the derived-only law reproduces every receipt scalar."""

    def test_four_corners(self):
        sq = square_from_receipts()
        self.assertTrue(sq["all_four_corners_hold_derived_only"], sq)
        self.assertEqual(sq["scalars_checked"], 28, sq)

    def test_derived_law_values(self):
        # live identity, not a stored table: the n=6 corners
        self.assertEqual(derived_unified_law(6, 2, 2), 336)
        self.assertEqual(derived_unified_law(6, 3, 2), 434)
        self.assertEqual(derived_unified_law(6, 2, 3), 392)
        self.assertEqual(derived_unified_law(6, 3, 3), 518)


class TestLiveCensusLegs(unittest.TestCase):
    """The live T2U/M33 censuses still land on the derived law."""

    def test_t2u_heights(self):
        leg = live_leg(t2u_program_for, (6, 7), "T2U")
        self.assertEqual([leg["6"]["assemblies"],
                          leg["7"]["assemblies"]], [336, 494], leg)
        self.assertTrue(leg["6"]["holds"] and leg["7"]["holds"], leg)
        self.assertEqual(leg["6"]["fiber_hist"], {1: 140, 2: 42, 4: 28},
                         leg)

    def test_m33_height(self):
        leg = live_leg(m33_program_for, (6,), "M33")
        self.assertEqual(leg["6"]["assemblies"], 518, leg)
        self.assertTrue(leg["6"]["holds"], leg)


class TestGuardProbe(unittest.TestCase):
    """G1: a second consumer of the relayed head stays refused by
    the v0.2 geometry guard, pinned verbatim.  Post-tick-164 note:
    with the designs/013 §1 carve-out (relay chains up to depth 3)
    the refusal now fires from the adjacency arm — the second
    consumer reads the relayed head from a NON-adjacent row — which
    is the genuine geometric reason; the blanket second-relay
    sentence was the tick-163 fence."""

    def test_both_second_consumers_refuse(self):
        probe = guard_probe()
        for label in GUARD_PROBES:
            self.assertFalse(probe[label]["compiled"], probe[label])
            self.assertEqual(
                probe[label]["refusal"],
                "UnsupportedGeometry: unit variant of 'v': chain "
                "literal 'r' at row 5 is non-adjacent (must sit "
                "directly below its reader); untested geometry",
                probe[label])

    def test_compile_raises_directly(self):
        with self.assertRaises(UnsupportedGeometry):
            from molasp.compiler import compile_program
            compile_program(GUARD_PROBES["second_terminal_unit_consumer"],
                            name="pin_direct_refusal")


class TestReceiptByteStability(unittest.TestCase):
    def test_receipt_hash(self):
        with open(RECEIPT_PATH, "rb") as fh:
            data = fh.read()
        self.assertEqual(
            hashlib.sha256(data).hexdigest(), RECEIPT_SHA256)
        receipt = json.loads(data)
        self.assertTrue(all(receipt["summary"].values()),
                        receipt["summary"])


if __name__ == "__main__":
    unittest.main()
