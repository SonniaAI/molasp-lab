"""Tick-155 pins: the PC11 multiplicity partition (L3) is ONE shared
or-support bit, witnessed by a closed-form canonical section
(SON-5152).

Theorem mechanics, all verified live from molasp.compiler /
molasp.parity on every run:

  (a) rule inventory: the only or-supported derived head is r, with
      bodies {q2, s} and {q2} — so the only atom that can carry a
      compile-time choice is r;
  (b) tile table: every site's tile is forced by (n, site) alone
      except the column-top pair (1,n) in {Cr, DAr} and (2,n) in
      {Ur, DBr};
  (c) one shared bit: section(n, ideal, bit) reproduces the census
      fiber EXACTLY at every censusable height 5..12 — unique
      assembly off corner ideals, the two bit-orbits on corner
      ideals, fiber 2 (never 4) even when both free sites are
      present.

New height n = 12 (never censused before this tick) was pinned from
the closed form (presence 1820, contended 91, assemblies 1911) and
confirmed live; the decorative lineage's alphabet caps the family at
height 12 (program_for(13) == program_for(12)), so the section is
verified across the ENTIRE census range, eight consecutive heights.

Receipt evidence/2026-10-22-pc11-fiber-mechanics/mechanics.json is
pinned by sha256 and re-derived live. Zero queue spend, stdlib-only,
no RNG, no trajectories, no gate; nothing here is a validated result
until independently reviewed.
"""

import hashlib
import json
import os
import unittest
from math import comb

from tools.pc11_contention_structure import (
    all_ideals,
    program_for,
)
from tools.pc11_fiber_mechanics import (
    FAMILY_HEIGHT_CAP,
    NEW_HEIGHT,
    ROWS,
    analyze_height,
    build_receipt,
    forced_tile,
    rule_inventory,
    section,
)

RECEIPT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "evidence", "2026-10-22-pc11-fiber-mechanics", "mechanics.json",
)
RECEIPT_SHA256 = ("940668cda9ad47ea1e5a7d8ec39d0848"
                  "abe39c473d11dc4515d401f66c10d926")


class TestRuleInventory(unittest.TestCase):
    def test_only_or_supported_head_is_r(self):
        inv = rule_inventory(8)
        self.assertEqual(inv["or_supported_heads"], ["r"])
        self.assertEqual(inv["r_bodies"], [["q2"], ["q2", "s"]])
        self.assertEqual(inv["head_multiplicities"], {"q2": 1, "r": 2})


class TestForcedTileTable(unittest.TestCase):
    def test_parametric_pins_at_n7(self):
        # absolute-position columns
        self.assertEqual(forced_tile(7, (0, 4), 0), "S4")
        self.assertEqual(forced_tile(7, (3, 2), 1), "L2")
        # transport + forced rule readings in column 1
        self.assertEqual(forced_tile(7, (1, 5), 0), "D5T")
        self.assertEqual(forced_tile(7, (1, 6), 0), "Cq2")
        # fanout column: V0p bottom, V< y>p interior, Uq2 at n-1
        self.assertEqual(forced_tile(7, (2, 1), 0), "V0p")
        self.assertEqual(forced_tile(7, (2, 3), 0), "V3p")
        self.assertEqual(forced_tile(7, (2, 6), 1), "Uq2")
        # the two free sites, bit-coupled exactly as measured
        self.assertEqual(forced_tile(7, (1, 7), 0), "Cr")
        self.assertEqual(forced_tile(7, (1, 7), 1), "DAr")
        self.assertEqual(forced_tile(7, (2, 7), 0), "Ur")
        self.assertEqual(forced_tile(7, (2, 7), 1), "DBr")
        # bit never touches a forced site
        for site in [(0, 3), (1, 6), (2, 6), (3, 7)]:
            self.assertEqual(forced_tile(7, site, 0),
                             forced_tile(7, site, 1))


class TestSectionMechanics(unittest.TestCase):
    def test_all_censusable_heights(self):
        for rows in ROWS + (NEW_HEIGHT,):
            h = analyze_height(rows)
            self.assertTrue(h["free_sites_exactly_column_tops"], rows)
            self.assertTrue(h["free_pairs_expected"], rows)
            self.assertTrue(h["section_reproduces_fibers"], rows)
            self.assertTrue(h["section_unique_on_noncorner"], rows)
            self.assertTrue(h["section_two_bit_orbits_on_corner"], rows)
            self.assertTrue(h["coupling_holds_no_fourfold"], rows)
            self.assertEqual(h["max_fiber"], 2, rows)
            self.assertTrue(h["assemblies_equals_law"], rows)
            self.assertEqual(
                h["assemblies"],
                comb(rows + 4, 4) + comb(rows + 2, 2), rows)

    def test_involution_is_bit_flip(self):
        # sigma: the second reading of a corner fiber is EXACTLY the
        # bit-flip of the first, at every corner ideal of n = 9.
        rows = 9
        h = analyze_height(rows)
        from tools.pc11_contention_structure import assembly_sets
        assemblies, _ = assembly_sets(program_for(rows), "sig9")
        by_shape = {}
        for asm in assemblies:
            by_shape.setdefault(
                frozenset((x, y) for x, y, _t in asm), set()).add(asm)
        corners = [s for s in by_shape if (1, rows) in s]
        self.assertEqual(len(corners), comb(rows + 2, 2))
        self.assertEqual(h["contended"], len(corners))
        for ideal in corners:
            a0, a1 = section(rows, ideal, 0), section(rows, ideal, 1)
            self.assertNotEqual(a0, a1)
            # differences confined to the column-top pair
            d0 = {(x, y): t for x, y, t in a0}
            d1 = {(x, y): t for x, y, t in a1}
            diff = {p for p in d0 if d0[p] != d1[p]}
            self.assertTrue(diff <= {(1, rows), (2, rows)})
            self.assertEqual(by_shape[ideal], {a0, a1})


class TestNewHeightAndCap(unittest.TestCase):
    def test_n12_prediction_pins(self):
        # pinned from the closed form before the census ran
        self.assertEqual(comb(16, 4), 1820)
        self.assertEqual(comb(14, 2), 91)
        self.assertEqual(comb(16, 4) + comb(14, 2), 1911)
        receipt = json.load(open(RECEIPT_PATH))
        block = receipt["new_heights_this_tick"]
        self.assertEqual(block["rows"], [12])
        self.assertEqual(block["predicted_first"]["12"], {
            "presence": 1820, "contended": 91, "assemblies": 1911})
        self.assertEqual(block["seen"]["12"]["presence"], 1820)
        self.assertEqual(block["seen"]["12"]["assemblies"], 1911)
        self.assertTrue(block["seen"]["12"]["section_reproduces_fibers"])

    def test_family_height_cap(self):
        self.assertEqual(FAMILY_HEIGHT_CAP, 12)
        # the decorative alphabet is exhausted one past the cap
        self.assertEqual(program_for(13), program_for(12))
        cap = json.load(open(RECEIPT_PATH))["family_height_cap"]
        self.assertTrue(cap["cap_exact"])
        self.assertEqual(cap["census_range"], list(range(5, 13)))


class TestReceipt(unittest.TestCase):
    def test_receipt_hash_and_byte_stability(self):
        raw = open(RECEIPT_PATH, "rb").read()
        self.assertEqual(
            hashlib.sha256(raw).hexdigest(), RECEIPT_SHA256)
        fresh = json.dumps(build_receipt(), sort_keys=True, indent=1) + "\n"
        self.assertEqual(raw.decode(), fresh)

    def test_every_scalar_in_receipt(self):
        receipt = json.load(open(RECEIPT_PATH))
        for rows in map(int, receipt["rows_measured"]):
            h = receipt["heights"][str(rows)]
            self.assertTrue(h["section_reproduces_fibers"])
            self.assertTrue(h["coupling_holds_no_fourfold"])
            self.assertTrue(h["partition_closes_weighted"])
            self.assertEqual(h["presence"], comb(rows + 4, 4))
            self.assertEqual(h["contended"], comb(rows + 2, 2))
        # ideals count sanity at one height
        self.assertEqual(len(all_ideals(8)), comb(12, 4))


if __name__ == "__main__":
    unittest.main()
