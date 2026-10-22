"""Tick-154 pins: the PC11 contention law is DERIVED, not just
measured — gap bijections for L1/L2, live multiplicity partition for
L3, and a first-visit prediction at n = 11 (SON-5152).

The two-term law assemblies(n) = C(n+4,4) + C(n+2,2) now follows
from:

  L1  ideals <-> weakly-decreasing heights <-> compositions of n
      into 5 parts (gap map)          -> |ideals| = C(n+4,4)
  L2  corner ideals (containing (1,n)) <-> compositions of n into
      3 parts                         -> |corner| = C(n+2,2)
  L3  multiplicity 1 on non-corner ideals, exactly 2 on corner
      ideals (machine-verified live at every measured height)

so assemblies(n) = C(n+4,4) + C(n+2,2). The empirical content is
reduced to L3 alone. New height n = 11 was predicted from the closed
form BEFORE its census ran (1365 / 78 / 1443) and confirmed exactly;
the bijections are stress-checked at n = 20 (10626 ideals).

Receipt evidence/2026-10-22-pc11-law-derivation/derivation.json is
pinned by sha256 and every scalar in it is re-derived live. Zero
queue spend, stdlib-only, no RNG, no trajectories, no gate; nothing
here is a validated result until independently reviewed.
"""

import hashlib
import json
import os
import unittest
from math import comb

from tools.pc11_law_derivation import (
    BIJECTION_STRESS,
    NEW_HEIGHT,
    ROWS,
    build_receipt,
    census_partition,
    compositions,
    corner_gaps_to_heights,
    derive_height,
    gaps_to_heights,
    heights_to_gaps,
)
from tools.pc11_contention_structure import (
    all_ideals,
    census_height,
    ideals_containing,
)

RECEIPT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "evidence", "2026-10-22-pc11-law-derivation", "derivation.json")
RECEIPT_SHA = ("62508ea813a274cf902a1188db59893af4056bcaf1770836fa3"
               "6baf0cd496880")

# the new-height prediction, written down from the closed form
# before this tick's census read it
N11 = {"presence": 1365, "contended": 78, "assemblies": 1443}

ASSEMBLY_SEQUENCE = (147, 238, 366, 540, 770, 1067)


class Pc11LawDerivationPins(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(RECEIPT_PATH, "rb") as fh:
            cls.raw = fh.read()
        cls.receipt = json.loads(cls.raw)
        cls.live_deriv = {rows: derive_height(rows) for rows in ROWS}
        cls.live_census = {rows: census_partition(rows) for rows in ROWS}

    def test_receipt_sha_pinned(self):
        self.assertEqual(
            hashlib.sha256(self.raw).hexdigest(), RECEIPT_SHA)

    def test_receipt_stable_roundtrip(self):
        self.assertEqual(
            json.dumps(self.receipt, sort_keys=True, indent=1) + "\n",
            self.raw.decode())

    # ---- L1: the gap bijection is exact, at every measured height

    def test_gap_bijection_exact_at_every_height(self):
        for rows in ROWS:
            self.assertTrue(
                self.live_deriv[rows]["gap_bijection_exact"],
                msg="gap bijection fails at n=%d" % rows)
            self.assertTrue(
                self.live_deriv[rows]["encoding_bijection_exact"],
                msg="height encoding is not a bijection at n=%d" % rows)

    def test_box_law_from_compositions(self):
        for rows in ROWS:
            d = self.live_deriv[rows]
            self.assertEqual(d["ideals"], comb(rows + 4, 4))
            self.assertEqual(d["ideals_from_gaps"], comb(rows + 4, 4))
            self.assertEqual(d["composition_count_5"], comb(rows + 4, 4))

    def test_gap_maps_are_inverse(self):
        for rows in ROWS:
            for g in compositions(rows, 5):
                h = gaps_to_heights(g)
                self.assertEqual(sorted(h, reverse=True), list(h))  # decreasing
                self.assertLessEqual(h[0], rows)
                self.assertEqual(heights_to_gaps(h, rows), g)
                self.assertEqual(sum(g), rows)

    # ---- L2: the corner bijection is exact

    def test_corner_gap_bijection_exact_at_every_height(self):
        for rows in ROWS:
            d = self.live_deriv[rows]
            self.assertTrue(d["corner_gap_bijection_exact"],
                            msg="corner bijection fails at n=%d" % rows)
            self.assertEqual(d["corner_ideals"], comb(rows + 2, 2))
            self.assertEqual(d["composition_count_3"], comb(rows + 2, 2))

    def test_corner_ideals_are_exactly_site_ideals(self):
        for rows in ROWS:
            corner = ideals_containing((1, rows), rows)
            from_gaps = {frozenset(
                (x, y) for x in range(4) for y in range(1, h[x] + 1))
                for h in ((rows, rows) + corner_gaps_to_heights(g)
                          for g in compositions(rows, 3))}
            self.assertEqual(corner, from_gaps)

    def test_corner_heights_have_h0_h1_maximal(self):
        for rows in ROWS:
            for s in ideals_containing((1, rows), rows):
                hs = {}
                for x, y in s:
                    hs[x] = max(hs.get(x, 0), y)
                self.assertEqual((hs.get(0, 0), hs.get(1, 0)),
                                 (rows, rows))

    # ---- L3 + theorem: census partition closes, law reproduced

    def test_partition_closes_and_theorem_holds(self):
        for rows in ROWS:
            c = self.live_census[rows]
            self.assertTrue(c["partition_closes_sets"])
            self.assertTrue(c["partition_closes_weighted"])
            self.assertTrue(c["assemblies_equals_presence_plus_contended"])
            self.assertTrue(c["structure_ok"])
            self.assertEqual(c["assemblies"], c["theorem_pred"])

    def test_assembly_sequence_matches_all_heights(self):
        for rows, assemblies in zip(ROWS, ASSEMBLY_SEQUENCE):
            self.assertEqual(self.live_census[rows]["assemblies"],
                             assemblies)

    # ---- new height predicted first, then censused

    def test_new_height_prediction_confirmed(self):
        n = receipt = self.receipt["new_height_this_tick"]
        self.assertEqual(n["rows"], NEW_HEIGHT)
        self.assertEqual(n["predicted_first"], N11)
        self.assertEqual(n["seen"]["presence"], N11["presence"])
        self.assertEqual(n["seen"]["contended"], N11["contended"])
        self.assertEqual(n["seen"]["assemblies"], N11["assemblies"])
        self.assertTrue(n["structure_ok"])

    def test_new_height_live_census(self):
        c = census_height(NEW_HEIGHT)
        self.assertEqual(c["presence"], N11["presence"])
        self.assertEqual(c["contended"], N11["contended"])
        self.assertEqual(c["assemblies"], N11["assemblies"])
        self.assertTrue(c["presence_equals_ideals"]
                        and c["contended_equals_corner_ideals"]
                        and c["no_other_multiplicity"]
                        and c["readings_differ_only_at_corner_pair"])

    # ---- bijection-only stress far past the census range

    def test_bijection_stress_beyond_census(self):
        s = self.receipt["bijection_stress"]
        self.assertEqual(s["rows"], BIJECTION_STRESS)
        self.assertEqual(s["ideals"], comb(BIJECTION_STRESS + 4, 4))
        self.assertEqual(s["ideals"], 10626)
        self.assertTrue(s["gap_bijection_exact"])
        self.assertTrue(s["corner_gap_bijection_exact"])
        live = derive_height(BIJECTION_STRESS)
        self.assertEqual(live["ideals"], s["ideals"])
        self.assertTrue(live["gap_bijection_exact"]
                        and live["corner_gap_bijection_exact"])

    # ---- receipt mirrors the live derivation

    def test_receipt_matches_live_derivation(self):
        for rows in ROWS:
            self.assertEqual(self.receipt["derivation"][str(rows)],
                             self.live_deriv[rows])
            self.assertEqual(self.receipt["census_partition"][str(rows)],
                             self.live_census[rows])


if __name__ == "__main__":
    unittest.main()
