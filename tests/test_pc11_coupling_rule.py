"""Tick-156 pins: the PC11 coupling rule is DERIVED from conduit
geometry (SON-5152).

Three lemmas, all verified live from molasp.compiler at every
censusable height 5..12, static (no BFS) except where a census
cross-check is named:

  L_east  each body of the or-head r owns ONE named conduit glue
          (unit1_r / and1_r) that occurs exactly twice in the whole
          inventory: the conduit's east face and its own reader's
          west face — an east-west body-identity handshake;
  L_west  against the forced row-n context every conduit reaches
          TAU = 2 by west+south (1+1), so the free bit lives only at
          (1,n) and its south bond is the value-typed lo read
          ({lo}-t-done via the passthrough re-type);
  L_coupling  at (2,n) south gives exactly 1 < TAU, a west match is
          necessary, and by L_east the only west-matching tile is the
          chosen body's own reader — the reader is a FUNCTION of the
          bit.  Growth order closes the last escape: L{n} east of
          (2,n) cannot arrive first (south alone 1 < 2), so no east
          bond is ever available to a reader.

Corollary (derived): assemblies(n) = |ideals| + (k-1)*|corner ideals|
with k = live body count of the or-head; census cross-checks agree
at every height 5..12 (fiber == k == 2 on corner ideals, never 4,
including the 13 both-site corner ideals at n = 12).

Receipt evidence/2026-10-22-pc11-coupling-rule/rule.json is pinned
by sha256 and re-derived live. Zero queue spend, stdlib-only, no
RNG; nothing here is a validated result until independently
reviewed.
"""

import hashlib
import json
import os
import unittest
from math import comb

from tools.pc11_coupling_rule import (
    ROWS,
    analyze_height,
    build_receipt,
    census_cross_check,
)
from tools.pc11_contention_structure import program_for
from molasp.compiler import TAU

RECEIPT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "evidence", "2026-10-22-pc11-coupling-rule", "rule.json",
)
RECEIPT_SHA256 = ("53daa0aa9dcf0a434f46ed8121904ad0"
                  "3518f2519da230819be2dac7be21108b")


class LEast(unittest.TestCase):
    def test_body_glues_exactly_twice_at_every_height(self):
        for r in ROWS:
            h = analyze_height(r)
            self.assertEqual(
                h["L_east"]["body_glue_occurrences"],
                {"and1_r": 2, "unit1_r": 2}, r)
            self.assertTrue(h["L_east"]["each_glue_exactly_twice"], r)
            # the two occurrences are the conduit-E / reader-W pair
            for info in h["bodies"].values():
                tiles = _tiles(r)
                self.assertEqual(
                    tiles[info["conduit"]]["E"], info["glue"], r)
                self.assertEqual(
                    tiles[info["reader"]]["W"], info["glue"], r)

    def test_body_inventory(self):
        for r in ROWS:
            h = analyze_height(r)
            self.assertEqual(
                h["bodies"]["unit"],
                {"conduit": "Cr", "reader": "Ur", "glue": "unit1_r"}, r)
            self.assertEqual(
                h["bodies"]["and"],
                {"conduit": "DAr", "reader": "DBr", "glue": "and1_r"}, r)


class LWest(unittest.TestCase):
    def test_free_bit_exactly_two_conduits(self):
        for r in ROWS:
            h = analyze_height(r)
            self.assertEqual(h["L_west"]["admissible_at_1n"],
                             ["Cr", "DAr"], r)
            self.assertEqual(h["L_west"]["bond_sums"],
                             {"Cr": TAU, "DAr": TAU}, r)

    def test_south_bond_is_value_typed_lo_read(self):
        for r in ROWS:
            h = analyze_height(r)
            self.assertTrue(
                h["L_west"]["south_is_value_typed_lo_read"], r)
            # the passthrough re-type puts s-t-done on Cq2's north face
            self.assertEqual(h["context"]["D_below_north"],
                             "s-t-done", r)

    def test_reader_south_is_hi_chain_link(self):
        for r in ROWS:
            h = analyze_height(r)
            self.assertTrue(h["reader_south_is_hi_chain_link"], r)
            self.assertEqual(h["context"]["V_below_north"],
                             "q2-t-done", r)


class LCoupling(unittest.TestCase):
    def test_reader_is_function_of_bit(self):
        for r in ROWS:
            h = analyze_height(r)
            self.assertEqual(
                h["L_coupling"]["per_bit"]["unit"]["admissible_at_2n"],
                ["Ur"], r)
            self.assertEqual(
                h["L_coupling"]["per_bit"]["and"]["admissible_at_2n"],
                ["DBr"], r)

    def test_cross_pairs_fail_tau(self):
        for r in ROWS:
            h = analyze_height(r)
            for v in h["L_coupling"]["per_bit"].values():
                self.assertLess(v["cross_bond_sum"], TAU, r)
                self.assertEqual(v["cross_bond_sum"], 1, r)

    def test_south_only_admits_nothing_at_2n(self):
        for r in ROWS:
            h = analyze_height(r)
            self.assertTrue(h["L_coupling"]["south_only_is_empty"], r)
            self.assertEqual(
                h["L_coupling"]["south_only_admissible_at_2n"], [], r)

    def test_growth_order_closes_east_escape(self):
        for r in ROWS:
            g = analyze_height(r)["L_coupling"]["growth_order"]
            self.assertEqual(g["tile"], "L%d" % r)
            self.assertEqual(g["south_only_sum"], 1)
            self.assertEqual(g["with_west_sum"], TAU)
            self.assertTrue(g["cannot_arrive_first"], r)


class Corollary(unittest.TestCase):
    def test_census_agrees_with_static_rule_everywhere(self):
        for r in ROWS:
            c = census_cross_check(r)
            self.assertTrue(c["section_prediction_agrees"], r)
            self.assertTrue(c["fiber_equals_k_never_4"], r)
            self.assertGreater(c["corner_ideals_with_both_sites"], 0, r)
            self.assertEqual(c["max_fiber_on_both_site_sets"], 2, r)

    def test_k_form_law(self):
        k = 2
        for r in ROWS:
            c = census_cross_check(r)
            self.assertEqual(
                c["assemblies"],
                comb(r + 4, 4) + (k - 1) * comb(r + 2, 2), r)

    def test_lemmas_compound_across_heights(self):
        receipt = build_receipt()
        for name in ("L_east_all_heights", "L_west_all_heights",
                     "L_coupling_all_heights", "census_agrees_all_heights"):
            self.assertTrue(receipt["lemmas"][name], name)
        self.assertEqual(receipt["rows_measured"], list(ROWS))


class ReceiptPins(unittest.TestCase):
    def test_receipt_bytes_stable(self):
        with open(RECEIPT_PATH, "rb") as fh:
            data = fh.read()
        self.assertEqual(
            hashlib.sha256(data).hexdigest(), RECEIPT_SHA256)

    def test_live_receipt_reproduction(self):
        receipt = build_receipt()
        live = json.dumps(receipt, indent=2, sort_keys=True,
                          default=sorted) + "\n"
        with open(RECEIPT_PATH, "rb") as fh:
            pinned = fh.read().decode()
        self.assertEqual(live, pinned)


def _tiles(rows):
    from molasp.compiler import compile_program
    return compile_program(program_for(rows),
                           name="PC11ruleTest%d" % rows)["tiles"]


if __name__ == "__main__":
    unittest.main()
