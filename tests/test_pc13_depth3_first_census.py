"""Tick 164 pins: the FIRST true depth-3 census — the designs/013
§1 fragment implemented (MAX_RELAY_STAGES = 3) and every
prediction that tick 163 pinned BEFORE the family could compile
lands exactly.

Live census pins (PC13-D3, decor alphabet tyzkmba):

  [2,2,2]   577/813/1110/1478/1928/2472/3123 at n=6..12
  [2,2,3]   n=12 -> 3997 (power alternative separates here:
            shell_2 fiber 3, not 2^(k-1))
  [3,2,2]   n=6 -> 689
  [2,2,2,2] n=8 -> 2010 (depth 4, three relay stages)

Element-wise at every primary height: presence == ideal set
C(n+4,4); corner nesting C^(0) <= C^(1) <= C^(2); realized fiber ==
product of the k_i over the corners a shape contains (never
additive); every full fiber realizes all conduit combinations at
the column-1 corner sites; readings differ only at the corner site
pairs; every relay stage value-typed north with its per-body glues
each exactly twice; the terminal or-head keeps per-body glues
north.

Fence pins: depth-5 chains refuse verbatim at the new boundary;
AND and mixed bodies at a relay row still refuse verbatim; a
second terminal consumer of a relayed head still refuses (now via
the non-adjacency arm); both tick-163 depth-3 axes compile.
"""
import hashlib
import json
import os
import unittest

from tools.pc13_depth3_first_census import (
    DECOR,
    GUARD_PROBES,
    PINNED_222,
    PINNED_2222,
    PINNED_223,
    PINNED_322,
    RELAYS_D3,
    RELAYS_D4,
    additive_falsifier,
    census_height,
    chain_program,
    guard_probe,
    shell_law,
    static_checks,
)

RECEIPT_PATH = os.path.join(
    "evidence", "2026-10-22-pc13-depth3-first-census", "depth3.json")
RECEIPT_SHA256 = (
    "50c663f592636de844fee2a36fe1ba8187a9d678795622721be67063fdd972ed")


class PrimaryCensusTest(unittest.TestCase):
    """The seven pinned scalars, live, plus the element-wise
    structure at every height."""

    def test_pinned_table_lands_live(self):
        for n in range(6, 13):
            leg = census_height(n, [2, 2, 2], RELAYS_D3, PINNED_222[n])
            self.assertEqual(leg["assemblies"], PINNED_222[n], (n, leg))
            self.assertTrue(leg["matches_pinned"], (n, leg))
            self.assertTrue(leg["law_holds"], (n, leg))

    def test_structure_elementwise_every_height(self):
        for n in range(6, 13):
            leg = census_height(n, [2, 2, 2], RELAYS_D3, PINNED_222[n])
            self.assertTrue(leg["presence_equals_ideals"], (n, leg))
            self.assertTrue(leg["nesting_elementwise"], (n, leg))
            self.assertTrue(leg["expected_fiber_elementwise"], (n, leg))
            self.assertTrue(leg["fiber_hist_is_shell_hist"], (n, leg))
            self.assertTrue(leg["conduit_combos_realized"], (n, leg))
            self.assertTrue(
                leg["readings_differ_only_at_corner_pairs"], (n, leg))
            self.assertTrue(leg["additive_falsified"], (n, leg))

    def test_fiber_histogram_n6(self):
        leg = census_height(6, [2, 2, 2], RELAYS_D3, PINNED_222[6])
        self.assertEqual(leg["fiber_histogram"],
                         {"1": 95, "2": 45, "4": 42, "8": 28}, leg)
        self.assertEqual(leg["shell_sizes"],
                         {"1": 95, "2": 45, "4": 42, "8": 28}, leg)

    def test_additive_falsifier_separates(self):
        for n in range(6, 13):
            self.assertGreater(
                shell_law(n, [2, 2, 2]) - additive_falsifier(n, [2, 2, 2]),
                100, n)


class LegsTest(unittest.TestCase):
    """The mixed and depth-4 points, live."""

    def test_mixed_bottom_relay_n12(self):
        leg = census_height(12, [2, 2, 3], RELAYS_D3, PINNED_223[12])
        self.assertEqual(leg["assemblies"], 3997, leg)
        self.assertTrue(leg["expected_fiber_elementwise"], leg)

    def test_mixed_terminal_n6(self):
        leg = census_height(6, [3, 2, 2], RELAYS_D3, PINNED_322[6])
        self.assertEqual(leg["assemblies"], 689, leg)

    def test_depth4_n8(self):
        leg = census_height(8, [2, 2, 2, 2], RELAYS_D4, PINNED_2222[8])
        self.assertEqual(leg["assemblies"], 2010, leg)
        self.assertTrue(leg["law_holds"], leg)
        self.assertTrue(leg["expected_fiber_elementwise"], leg)


class StaticTest(unittest.TestCase):
    def test_handshake_every_height(self):
        for n in range(6, 13):
            stat = static_checks(n, [2, 2, 2], RELAYS_D3)
            self.assertTrue(stat["all_stages_ok"], (n, stat))
            # relays value-typed; terminal per-body north
            self.assertEqual(
                stat["stages"]["u"]["north_faces"], ["u-t-done"], stat)
            self.assertEqual(
                stat["stages"]["r"]["north_faces"], ["r-t-done"], stat)
            self.assertEqual(
                stat["stages"]["w"]["north_faces"],
                ["unit1_w-done", "unit2_w-done"], stat)


class FenceTest(unittest.TestCase):
    def test_depth5_refused_verbatim(self):
        probes = guard_probe()
        entry = probes["depth5_chain"]
        self.assertFalse(entry["compiled"], entry)
        self.assertEqual(
            entry["refusal"],
            "UnsupportedGeometry: rule atom 'x' at non-terminal row 7: "
            "relay chain depth 4 exceeds the admitted maximum 3 "
            "(designs/013 \u00a71)", entry)

    def test_and_and_mixed_still_refused(self):
        probes = guard_probe()
        for label in ("and_body_at_relay", "mixed_bodies_at_relay"):
            self.assertFalse(probes[label]["compiled"], label)
            self.assertIn("designs/012 admits only duplicate unit "
                          "bodies", probes[label]["refusal"], label)

    def test_second_consumer_still_refused(self):
        probes = guard_probe()
        entry = probes["second_terminal_consumer"]
        self.assertFalse(entry["compiled"], entry)
        self.assertIn("non-adjacent", entry["refusal"], entry)

    def test_tick163_axes_compile(self):
        probes = guard_probe()
        for label in ("tick163_axis_stacked_spine_relay",
                      "tick163_axis_head_chained_relay"):
            self.assertTrue(probes[label]["compiled"], label)


class ReceiptTest(unittest.TestCase):
    def test_receipt_byte_stability(self):
        with open(RECEIPT_PATH, "rb") as fh:
            digest = hashlib.sha256(fh.read()).hexdigest()
        self.assertEqual(digest, RECEIPT_SHA256)

    def test_receipt_records_full_tables(self):
        with open(RECEIPT_PATH) as fh:
            receipt = json.load(fh)
        self.assertEqual(receipt["kind"], "pc13-depth3-first-census")
        self.assertEqual(len(receipt["primary_222"]), 7)
        self.assertTrue(all(receipt["summary"].values()),
                        receipt["summary"])


class DecorTest(unittest.TestCase):
    """Family-local alphabet: no decor letter is a head atom (the
    tick-158 collision lesson), and the program builder reaches
    every censused height."""

    def test_decor_avoids_head_atoms(self):
        heads = set("purwv") | {"q2"}
        for letter in DECOR:
            self.assertNotIn(letter, heads, letter)

    def test_program_shape(self):
        prog = chain_program(6, [2, 2, 2], RELAYS_D3)
        self.assertEqual(prog,
                         "p. t. q2 :- p. u :- q2. u :- q2. "
                         "r :- u. r :- u. w :- r. w :- r.")
        # n=6: 2 facts + 7 rules = 9 statements; n=12: 8 facts + 7
        self.assertEqual(chain_program(6, [2, 2, 2],
                                       RELAYS_D3).count("."), 9)
        self.assertEqual(chain_program(12, [2, 2, 2],
                                       RELAYS_D3).count("."), 15)


if __name__ == "__main__":
    unittest.main()
