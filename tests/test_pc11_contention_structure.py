"""Tick-153 pins: the PC11 contention law holds at two NEW heights it
had never seen (n = 9, 10), element-wise, placement-independent (SON-5152).

Tick 152 measured, at n = 5..8, that the PC11 decorative family's
name-level assemblies follow assemblies(n) = C(n+4,4) + C(n+2,2) with
the contended presence sets exactly the ideals containing site (1, n).
A closed form earns its keep by predicting, so this tick extended the
census to n = 9 and n = 10 BEFORE reading any count, and verified every
structural claim element-wise at every height 5..10.

Live BFS re-derivation on every run (molasp.parity.producible):

  P1  presence == full four-column ideal set == C(rows+4,4) at 5..10
  A1  assemblies == C(rows+4,4) + C(rows+2,2) at 5..10 — the new
      predictions 770 (n=9) and 1067 (n=10) confirmed exactly, with
      presence 715/1001 and contended 55/66
  C1  contended sets == exactly the ideals containing (1, rows)
  C2  multiplicity exactly 2 on contended sets, exactly 1 elsewhere,
      no other multiplicity anywhere, and the two readings of each
      contended set differ only at sites (1, n) / (2, n)
  D1  placement independence at the new top height: both valid
      decorative insertions (after `q.` and after `p.`) produce the
      SAME assembly set at n = 10
  F1  the fourth finite difference of the six assembly counts is
      exactly 1 at both interior offsets — the degree-4 signature of
      C(n+4,4) with the C(n+2,2) term contributing 0

Receipt evidence/2026-10-22-pc11-contention-structure/structure.json
is pinned by sha256 and every scalar in it is re-derived live. Zero
queue spend, stdlib-only, no RNG, no trajectories, no gate; nothing
here is a validated result until independently reviewed.
"""

import hashlib
import json
import os
import unittest
from math import comb

from tools.pc11_contention_structure import (
    ROWS,
    build_receipt,
    census_height,
    finite_differences,
    ideal_sites,
    program_for,
)

RECEIPT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "evidence", "2026-10-22-pc11-contention-structure", "structure.json")
RECEIPT_SHA = ("91b91f7118597d5b32d8ed141b50da4a62b82fb580b3bca0a2cd3f6ad125437a")

# tick-66 corpus constants for the n=5 anchor (probe2.out, 2026-10-08)
ANCHOR_ASSEMBLIES = 147
ANCHOR_PRESENCE = 126
ANCHOR_CONTENDED = 21

# the two new-height predictions, written down by the tick-152 law
# before this tick's census read them
N9 = {"presence": 715, "contended": 55, "assemblies": 770}
N10 = {"presence": 1001, "contended": 66, "assemblies": 1067}


class Pc11ContentionStructurePins(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(RECEIPT_PATH, "rb") as fh:
            cls.raw = fh.read()
        cls.receipt = json.loads(cls.raw)
        cls.live = {rows: census_height(rows) for rows in ROWS}

    def test_receipt_sha_pinned(self):
        self.assertEqual(
            hashlib.sha256(self.raw).hexdigest(), RECEIPT_SHA)

    def test_receipt_rows_and_new_heights(self):
        self.assertEqual(self.receipt["rows_measured"], [5, 6, 7, 8, 9, 10])
        self.assertEqual(self.receipt["new_heights_this_tick"], [9, 10])

    def test_live_matches_receipt_scalars_every_height(self):
        for rows in ROWS:
            got, want = self.live[rows], self.receipt["heights"][str(rows)]
            for key in ("presence", "assemblies", "contended",
                        "multiplicity_1_sets", "multiplicity_2_sets",
                        "terminals"):
                self.assertEqual(got[key], want[key],
                                 "%s mismatch at n=%d" % (key, rows))
            for key in ("presence_equals_ideals",
                        "contended_equals_corner_ideals",
                        "no_other_multiplicity",
                        "readings_differ_only_at_corner_pair"):
                self.assertTrue(got[key], "%s failed at n=%d" % (key, rows))

    def test_box_and_two_term_laws_all_heights(self):
        for rows in ROWS:
            self.assertEqual(self.live[rows]["presence"], comb(rows + 4, 4))
            self.assertEqual(self.live[rows]["box_law"], comb(rows + 4, 4))
            self.assertEqual(
                self.live[rows]["assemblies"],
                comb(rows + 4, 4) + comb(rows + 2, 2))
            self.assertEqual(self.live[rows]["contended"], comb(rows + 2, 2))

    def test_new_height_predictions_confirmed(self):
        for rows, pred in ((9, N9), (10, N10)):
            self.assertEqual(self.live[rows]["presence"], pred["presence"])
            self.assertEqual(self.live[rows]["contended"], pred["contended"])
            self.assertEqual(self.live[rows]["assemblies"], pred["assemblies"])

    def test_anchor_reconciles_tick66(self):
        self.assertEqual(self.live[5]["assemblies"], ANCHOR_ASSEMBLIES)
        self.assertEqual(self.live[5]["presence"], ANCHOR_PRESENCE)
        self.assertEqual(self.live[5]["contended"], ANCHOR_CONTENDED)

    def test_multiplicity_partition_closes(self):
        for rows in ROWS:
            h = self.live[rows]
            self.assertEqual(
                h["multiplicity_1_sets"] + h["multiplicity_2_sets"],
                h["presence"])
            self.assertEqual(
                h["multiplicity_1_sets"] + 2 * h["multiplicity_2_sets"],
                h["assemblies"])

    def test_placement_independence_top_height(self):
        top = self.receipt["placement_agreement_top"]
        self.assertEqual(top["rows"], 10)
        self.assertTrue(top["agree"])
        # independent live re-check, not just the receipt's word
        from tools.pc11_contention_structure import placement_agreement
        self.assertTrue(placement_agreement(10))

    def test_fourth_difference_one(self):
        counts = [self.live[rows]["assemblies"] for rows in ROWS]
        self.assertEqual(finite_differences(counts, 4), [1, 1])
        self.assertEqual(self.receipt["fourth_difference_assemblies"], [1, 1])

    def test_build_receipt_is_pure_function_of_census(self):
        # byte-stability: rebuilding the receipt reproduces the pinned
        # artifact exactly (no timestamps, no RNG, sorted keys)
        self.assertEqual(json.dumps(build_receipt(), sort_keys=True, indent=1),
                         json.dumps(self.receipt, sort_keys=True, indent=1))

    def test_program_shape_unchanged(self):
        self.assertEqual(program_for(5),
                         "p. q. s. q2 :- p. r :- q2, s. r :- q2.")
        self.assertEqual(program_for(6),
                         "p. q. t. s. q2 :- p. r :- q2, s. r :- q2.")
        self.assertEqual(program_for(10),
                         "p. q. t. u. v. w. x. s. q2 :- p. r :- q2, s. r :- q2.")

    def test_ideal_shape_helper(self):
        # site (1, n) belongs to an ideal iff h0 = h1 = n
        full = ideal_sites((10, 10, 0, 0))
        self.assertIn((1, 10), full)
        self.assertNotIn((1, 10), ideal_sites((10, 9, 0, 0)))


if __name__ == "__main__":
    unittest.main()
