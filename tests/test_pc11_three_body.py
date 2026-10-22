"""Tick-157 pins: tick-156's falsifiable prediction is CONFIRMED —
a 3-body or-head censuses at fiber exactly 3, never 2^3 (SON-5152).

Live from molasp.compiler at every censusable height 5..12, on the
PC11 decorative extension with duplicate-body k-body or-heads (the
fragment admits at most two DISTINCT terminal-or body shapes; the
emitter mints a fresh conduit glue per rule body, so duplicate
bodies are real geometric bodies):

  k = 3  assemblies(n) = C(n+4,4) + 2*C(n+2,2)
         = 168/266/402/585/825/1133/1521/2002, multiplicity
         histogram {1: rest, 3: C(n+2,2)} at EVERY height, fiber 3
         never 8 — including the 13 both-site corner ideals at
         n = 12 (max fiber there == 3);
  k = 4  (beyond the recorded prediction) assemblies(n) =
         C(n+4,4) + 3*C(n+2,2) = 189/294/438/630/880/1199/1599/2093,
         fiber 4 never 16;
  body identity  in every contended fiber the conduit at (1, n)
         and the reader at (2, n) — when that site is present —
         carry the SAME body glue (east == west), element-wise;
  duplicate-shape independence  duplicating the unit body
         (PC11-3U) or the AND body (PC11-3A) gives identical
         presence/assembly/multiplicity censuses at n = 12;
  static lemmas re-verified on the k = 3 inventory: each body glue
         (and1_r/unit1_r/unit2_r) occurs exactly twice; the
         admissible (1, n) tiles against the forced context are
         exactly the three conduits [Cr, Cr2, DAr]; each body's
         reader is the unique admissible (2, n) tile given its own
         west glue, all cross-body pairings fail TAU, and growth
         order still closes the (3, n) escape.

Receipt evidence/2026-10-22-pc11-three-body/three_body.json is
pinned by sha256 and re-derived live. Zero queue spend, stdlib-only,
no RNG; nothing here is a validated result until independently
reviewed.
"""

import hashlib
import json
import os
import unittest
from math import comb

from tools.pc11_three_body import (
    ANCHOR_3U,
    ROWS,
    body_glues,
    build_receipt,
    census,
    program_for_k,
    static_lemmas,
)

RECEIPT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "evidence", "2026-10-22-pc11-three-body", "three_body.json")
RECEIPT_SHA256 = (
    "10ea6dd06be6fdbef0bda4e809f28c8965120e5cd8306e1f4a0877e795183052")

LAW_K3 = [168, 266, 402, 585, 825, 1133, 1521, 2002]
LAW_K4 = [189, 294, 438, 630, 880, 1199, 1599, 2093]


class PredictionPins(unittest.TestCase):
    """Fiber == k exactly; the law's k-slot holds at k = 3 and 4."""

    def test_k3_law_and_fiber_all_heights(self):
        for rows, want in zip(ROWS, LAW_K3):
            c = census(rows, "3U")
            self.assertEqual(c["assemblies"], want, rows)
            self.assertEqual(c["law"], want, rows)
            self.assertTrue(c["law_holds"], rows)
            self.assertEqual(c["presence"], comb(rows + 4, 4), rows)
            self.assertTrue(c["presence_equals_ideals"], rows)
            self.assertEqual(c["contended"], comb(rows + 2, 2), rows)
            self.assertTrue(c["contended_equals_corner_ideals"], rows)
            self.assertEqual(
                c["multiplicity_hist"],
                {1: comb(rows + 4, 4) - comb(rows + 2, 2),
                 3: comb(rows + 2, 2)}, rows)
            self.assertTrue(c["fiber_exactly_k_on_corner_else_1"], rows)
            self.assertTrue(c["never_power"], rows)          # 3 < 8
            self.assertTrue(c["readings_differ_only_at_site_pair"], rows)
            self.assertTrue(c["body_identity_pairing"], rows)

    def test_k4_beyond_the_recorded_prediction(self):
        for rows, want in zip(ROWS, LAW_K4):
            c = census(rows, "4")
            self.assertEqual(c["assemblies"], want, rows)
            self.assertTrue(c["law_holds"], rows)
            self.assertEqual(
                c["multiplicity_hist"],
                {1: comb(rows + 4, 4) - comb(rows + 2, 2),
                 4: comb(rows + 2, 2)}, rows)
            self.assertTrue(c["never_power"], rows)          # 4 < 16
            self.assertTrue(c["body_identity_pairing"], rows)

    def test_both_site_corner_ideals_never_explode(self):
        c = census(12, "3U")
        self.assertEqual(c["both_site_corner_ideals"], 13)
        self.assertEqual(c["max_fiber_both_site"], 3)        # never 8
        c4 = census(12, "4")
        self.assertEqual(c4["both_site_corner_ideals"], 13)
        self.assertEqual(c4["max_fiber_both_site"], 4)       # never 16

    def test_duplicate_shape_independence(self):
        u = census(12, "3U")
        a = census(12, "3A")
        self.assertEqual(a["assemblies"], u["assemblies"])
        self.assertEqual(a["presence"], u["presence"])
        self.assertEqual(a["multiplicity_hist"], u["multiplicity_hist"])
        self.assertTrue(a["law_holds"])


class StaticLemmaPins(unittest.TestCase):
    """The tick-156 lemmas on the k = 3 inventory, glue by glue."""

    def test_body_glue_minting(self):
        head, bodies, glues = body_glues(ANCHOR_3U)
        self.assertEqual(head, "r")
        self.assertEqual(bodies, [["q2", "s"], ["q2"], ["q2"]])
        self.assertEqual(glues,
                         {0: "and1_r", 1: "unit1_r", 2: "unit2_r"})

    def test_lemmas_at_representative_heights(self):
        for rows in (5, 9, 12):
            s = static_lemmas(rows)
            self.assertTrue(s["L_east"]["each_exactly_twice"], rows)
            self.assertTrue(
                s["L_east"]["one_conduit_one_reader_each"], rows)
            self.assertEqual(
                {g: 2 for g in s["body_glues"].values()},
                s["L_east"]["occurrences"], rows)
            self.assertEqual(
                s["L_west"]["admissible_at_1n"],
                ["Cr", "Cr2", "DAr"], rows)
            self.assertTrue(s["L_west"]["exactly_the_k_conduits"], rows)
            self.assertEqual(s["L_coupling"]["south_only_at_2n"], [])
            self.assertTrue(s["L_coupling"]["reader_function_of_bit"], rows)
            self.assertTrue(
                s["L_coupling"]["all_cross_pairs_fail_tau"], rows)
            self.assertTrue(
                s["L_coupling"]["growth_order_L_cannot_arrive_first"],
                rows)

    def test_decor_saturation_unchanged(self):
        self.assertEqual(program_for_k(13, "3U"),
                         program_for_k(12, "3U"))
        self.assertEqual(program_for_k(5, "3U"), ANCHOR_3U)


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

    def test_receipt_lemma_flags(self):
        with open(RECEIPT_PATH) as fh:
            receipt = json.load(fh)
        for name in ("L_east_all_heights", "L_west_all_heights",
                     "L_coupling_all_heights",
                     "prediction_k3_all_heights",
                     "beyond_prediction_k4_all_heights",
                     "duplicate_shape_independence_top"):
            self.assertTrue(receipt["lemmas"][name], name)
        self.assertEqual(receipt["rows_measured"], list(ROWS))


if __name__ == "__main__":
    unittest.main()
