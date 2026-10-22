"""Tick 165 pins: depth-4 FULL pinned table + the first ALL-stages-
unequal depth-3 point — every law-only prediction pinned in the
tool's docstring BEFORE this tick's census lands exactly.

Live census pins (PC13-D3/D4, decor alphabet tyzkmba):

  [2,2,2,2] (depth 4)  1099/1511/2010/2606/3310/4134/5091 at
            n=6..12 — the COMPLETE tick-163 pinned table (tick 164
            censused only n=8..10; heights 6/7/11/12 are new)
  [3,2,3]   986/1348/1788/2316/2943/3681/4543 at n=6..12 —
            unequal multiplicities at ALL THREE stages, pinned
            law-only in tick 165 before census; fibers exactly the
            suffix products {1, 3, 6, 18}, never additive
  [3,2,2,2] n=6 -> 1323 and [2,2,2,3] n=6 -> 1621 — which depth-4
            stage carries the 3 (terminal vs bottom relay); fibers
            of the bottom-3 point exactly {1, 3, 6, 12, 24}

Element-wise at every censused height: presence == ideal set
C(n+4,4); corner nesting element-wise; realized fiber == product
of the k_i over the corners a shape contains; every full fiber
realizes all conduit combinations at the column-1 corner sites;
readings differ only at the corner site pairs.  Statics: every
depth-4 relay stage value-typed north, per-body glues each exactly
twice, at every height 6..12 — the handshake holds at four stacked
stages.

Fence pins: the tick-164 boundary is unchanged (depth-5 refuses;
AND/mixed bodies at relay rows refuse; second terminal consumer
refuses; both admitted depth-3 axes compile).
"""
import hashlib
import json
import os
import unittest

from tools.pc13_depth3_first_census import (
    PINNED_2222,
    RELAYS_D3,
    RELAYS_D4,
    shell_law,
)
from tools.pc13_depth4_full_and_unequal import (
    FIBERS_2223,
    FIBERS_323,
    PINNED_323,
    build_receipt,
)

RECEIPT_PATH = os.path.join(
    "evidence", "2026-10-22-pc13-depth4-full-unequal",
    "depth4_unequal.json")
RECEIPT_SHA256 = (
    "efdebabab902b99416f9c2f472d1335de2f0dee4068dc4ddef8ff5287023d7a4")


def _load():
    with open(RECEIPT_PATH) as fh:
        return json.load(fh)


class ReceiptIntegrityTest(unittest.TestCase):
    def test_receipt_is_byte_stable(self):
        with open(RECEIPT_PATH, "rb") as fh:
            digest = hashlib.sha256(fh.read()).hexdigest()
        self.assertEqual(digest, RECEIPT_SHA256)


class Depth4FullTableTest(unittest.TestCase):
    """The COMPLETE depth-4 pinned table of designs/013 section 3."""

    def test_all_seven_pinned_scalars_land(self):
        receipt = _load()
        legs = receipt["depth4_2222_full_table"]
        for n in range(6, 13):
            leg = legs[str(n)]
            self.assertEqual(leg["assemblies"], PINNED_2222[n], (n, leg))
            self.assertTrue(leg["matches_pinned"], (n, leg))
            self.assertTrue(leg["law_holds"], (n, leg))

    def test_new_heights_are_new(self):
        receipt = _load()
        legs = receipt["depth4_2222_full_table"]
        self.assertEqual([legs[str(n)]["assemblies"] for n in (6, 7, 11, 12)],
                         [1099, 1511, 4134, 5091])

    def test_structure_elementwise_every_height(self):
        receipt = _load()
        for n in range(6, 13):
            leg = receipt["depth4_2222_full_table"][str(n)]
            self.assertTrue(leg["presence_equals_ideals"], (n, leg))
            self.assertTrue(leg["nesting_elementwise"], (n, leg))
            self.assertTrue(leg["expected_fiber_elementwise"], (n, leg))
            self.assertTrue(leg["fiber_hist_is_shell_hist"], (n, leg))
            self.assertTrue(leg["conduit_combos_realized"], (n, leg))
            self.assertTrue(leg["additive_falsified"], (n, leg))

    def test_fiber_histogram_n12_is_suffix_products(self):
        receipt = _load()
        leg = receipt["depth4_2222_full_table"]["12"]
        self.assertEqual(
            leg["fiber_histogram"],
            {"1": 1155, "2": 220, "4": 198, "8": 156, "16": 91},
            leg)

    def test_static_handshake_four_stages_every_height(self):
        receipt = _load()
        for n in range(6, 13):
            stat = receipt["static_depth4"][str(n)]
            self.assertTrue(stat["all_stages_ok"], (n, stat))
            self.assertEqual(sorted(stat["stages"]), ["r", "u", "v", "w"],
                             (n, stat))


class UnequalAllStagesTest(unittest.TestCase):
    """[3,2,3] — unequal multiplicities at every stage at once,
    predicted law-only BEFORE census (tool docstring, tick 165)."""

    def test_all_seven_pinned_scalars_land(self):
        receipt = _load()
        legs = receipt["unequal_all_stages_323"]
        for n in range(6, 13):
            leg = legs[str(n)]
            self.assertEqual(leg["assemblies"], PINNED_323[n], (n, leg))
            self.assertTrue(leg["matches_pinned"], (n, leg))
            self.assertTrue(leg["law_holds"], (n, leg))

    def test_pinned_scalars_match_the_law(self):
        for n in range(6, 13):
            self.assertEqual(PINNED_323[n], shell_law(n, [3, 2, 3]), n)

    def test_structure_elementwise_every_height(self):
        receipt = _load()
        for n in range(6, 13):
            leg = receipt["unequal_all_stages_323"][str(n)]
            self.assertTrue(leg["presence_equals_ideals"], (n, leg))
            self.assertTrue(leg["nesting_elementwise"], (n, leg))
            self.assertTrue(leg["expected_fiber_elementwise"], (n, leg))
            self.assertTrue(leg["conduit_combos_realized"], (n, leg))
            self.assertTrue(
                leg["readings_differ_only_at_corner_pairs"], (n, leg))

    def test_fibers_exactly_suffix_products(self):
        receipt = _load()
        for n in range(6, 13):
            leg = receipt["unequal_all_stages_323"][str(n)]
            self.assertEqual(sorted(map(int, leg["fiber_histogram"])),
                             FIBERS_323, (n, leg))

    def test_additive_falsifier_separates_everywhere(self):
        receipt = _load()
        for n in range(6, 13):
            leg = receipt["unequal_all_stages_323"][str(n)]
            self.assertGreater(
                leg["assemblies"] - leg["additive_total"], 400, (n, leg))

    def test_static_handshake_every_height(self):
        receipt = _load()
        for n in range(6, 13):
            stat = receipt["static_323"][str(n)]
            self.assertTrue(stat["all_stages_ok"], (n, stat))
            for atom, stage in stat["stages"].items():
                self.assertEqual(stage["k"], {"w": 3, "r": 2, "u": 3}[atom],
                                 (n, atom, stage))


class Depth4UnequalSinglesTest(unittest.TestCase):
    """Which depth-4 stage carries the multiplicity-3."""

    def test_terminal3_and_bottom3_land(self):
        receipt = _load()
        self.assertEqual(
            receipt["depth4_terminal3_3222"]["6"]["assemblies"], 1323)
        self.assertEqual(
            receipt["depth4_bottom3_2223"]["6"]["assemblies"], 1621)
        self.assertTrue(receipt["summary"]["depth4_unequal_singles_land"])

    def test_bottom3_fibers_exactly_suffix_products(self):
        receipt = _load()
        leg = receipt["depth4_bottom3_2223"]["6"]
        self.assertEqual(sorted(map(int, leg["fiber_histogram"])),
                         FIBERS_2223, leg)

    def test_both_match_the_law(self):
        self.assertEqual(shell_law(6, [3, 2, 2, 2]), 1323)
        self.assertEqual(shell_law(6, [2, 2, 2, 3]), 1621)


class FenceUnchangedTest(unittest.TestCase):
    def test_fence_summary(self):
        receipt = _load()
        self.assertTrue(receipt["summary"]["fence_unchanged"])
        probes = receipt["guard_probes"]
        self.assertIn("exceeds the admitted maximum 3",
                      probes["depth5_chain"]["refusal"])
        self.assertFalse(probes["and_body_at_relay"]["compiled"])
        self.assertFalse(probes["mixed_bodies_at_relay"]["compiled"])
        self.assertFalse(probes["second_terminal_consumer"]["compiled"])


class ReceiptReproductionTest(unittest.TestCase):
    """The receipt reproduces live: rebuilding it from the tools
    gives the same pinned scalars (byte-stability of the method)."""

    def test_summary_all_true_and_reproducible(self):
        receipt = _load()
        for key, val in sorted(receipt["summary"].items()):
            self.assertTrue(val, key)
        fresh = build_receipt()
        self.assertEqual(
            fresh["depth4_2222_full_table"]["12"]["assemblies"], 5091)
        self.assertEqual(
            fresh["unequal_all_stages_323"]["12"]["assemblies"], 4543)


if __name__ == "__main__":
    unittest.main()
