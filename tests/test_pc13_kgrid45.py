"""Tick 166 pins: the k in {2..5} depth-3 multiplicity grid — five
new full tables, every scalar pinned law-only in the tool's
docstring BEFORE this tick's census lands exactly.

Live census pins (PC13-D3, decor alphabet tyzkmba, terminal-first
ks = [k_w, k_r, k_u]):

  [4,2,2]  801/1101/1470/1918/2456/3096/3851 at n=6..12 — the 4 on
           the terminal stage; fibers exactly {1, 2, 4, 16}
  [2,4,2]  969/1325/1758/2278/2896/3624/4475 — the 4 on the middle
           relay; fibers exactly {1, 2, 8, 16}
  [2,2,4]  1059/1451/1926/2494/3166/3954/4871 — the 4 on the bottom
           relay; fibers exactly {1, 4, 8, 16}
  [5,2,2]  913/1245/1650/2138/2720/3408/4215 — the FIRST k=5 point;
           fibers exactly {1, 2, 4, 20} (never 8, never 9)
  [4,3,2]  1109/1501/1974/2538/3204/3984/4891 — first all-distinct
           non-palindromic tuple; fibers exactly {1, 2, 6, 24}

The three k=4 placements are orientation-discriminating: same
multiset, three pairwise DIFFERENT fiber sets, each exactly the
suffix products for its placement.

Element-wise at every censused height: presence == ideal set
C(n+4,4); corner nesting element-wise; realized fiber == product
of the k_i over the corners a shape contains; every full fiber
realizes all conduit combinations at the column-1 corner sites;
readings differ only at the corner site pairs.  Additive
alternative separated everywhere (margins 322..1859).  Statics:
R1/B1 handshake green at n=6 and n=12 for every point.

Fence pins: the tick-164 boundary is unchanged (depth-5 refuses;
AND/mixed bodies at relay rows refuse; second terminal consumer
refuses; both admitted depth-3 axes compile).
"""
import hashlib
import json
import os
import unittest

from tools.pc13_depth3_first_census import shell_law
from tools.pc13_kgrid45 import (
    FIBERS,
    PINNED_224,
    PINNED_242,
    PINNED_422,
    PINNED_432,
    PINNED_522,
    build_receipt,
)

RECEIPT_PATH = os.path.join(
    "evidence", "2026-10-22-pc13-kgrid45", "kgrid45.json")
RECEIPT_SHA256 = (
    "84475d167b6aeb613d2226a3e951980282b5a65343b515b8995b7624287bfdf7")

TABLES = {
    "[4,2,2]": PINNED_422,
    "[2,4,2]": PINNED_242,
    "[2,2,4]": PINNED_224,
    "[5,2,2]": PINNED_522,
    "[4,3,2]": PINNED_432,
}


def _load():
    with open(RECEIPT_PATH) as fh:
        return json.load(fh)


class TestKGridPins(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = _load()
        with open(RECEIPT_PATH, "rb") as fh:
            digest = hashlib.sha256(fh.read()).hexdigest()
        cls.digest = digest

    def test_receipt_sha256(self):
        self.assertNotEqual(
            RECEIPT_SHA256, "PIN_AT_RECEIPT_TIME",
            "pin the receipt sha256 at landing time")
        self.assertEqual(self.digest, RECEIPT_SHA256)

    def test_pinned_tables_land_exactly(self):
        for name, pinned in TABLES.items():
            table = self.receipt["tables"][name]
            for n, want in pinned.items():
                v = table[str(n)]
                self.assertEqual(
                    v["assemblies"], want,
                    "%s n=%d assemblies" % (name, n))
                self.assertTrue(v["matches_pinned"], (name, n))
                self.assertTrue(v["law_holds"], (name, n))

    def test_pinned_literals_equal_law(self):
        for name, pinned in TABLES.items():
            ks = {"[4,2,2]": [4, 2, 2], "[2,4,2]": [2, 4, 2],
                  "[2,2,4]": [2, 2, 4], "[5,2,2]": [5, 2, 2],
                  "[4,3,2]": [4, 3, 2]}[name]
            for n, want in pinned.items():
                self.assertEqual(shell_law(n, ks), want, (name, n))

    def test_fibers_exactly_suffix_products(self):
        for name, fibers in FIBERS.items():
            for n in range(6, 13):
                hist = self.receipt["tables"][name][str(n)][
                    "fiber_histogram"]
                self.assertEqual(sorted(map(int, hist)), sorted(fibers),
                                 (name, n))

    def test_k4_placements_orientation_discriminating(self):
        hists = [sorted(self.receipt["tables"][k]["6"]["fiber_histogram"])
                 for k in ("[4,2,2]", "[2,4,2]", "[2,2,4]")]
        self.assertEqual(len({tuple(h) for h in hists}), 3)

    def test_elementwise_structure_everywhere(self):
        for name, table in self.receipt["tables"].items():
            for n, v in table.items():
                self.assertTrue(v["presence_equals_ideals"], (name, n))
                self.assertTrue(v["nesting_elementwise"], (name, n))
                self.assertTrue(v["expected_fiber_elementwise"],
                                (name, n))
                self.assertTrue(v["conduit_combos_realized"], (name, n))
                self.assertTrue(v["readings_differ_only_at_corner_pairs"],
                                (name, n))
                self.assertTrue(v["additive_falsified"], (name, n))

    def test_summary_flags(self):
        s = self.receipt["summary"]
        for key in ("all_pinned_scalars_land", "first_k5_point_lands",
                    "all_distinct_432_lands", "law_holds_everywhere",
                    "additive_falsified_everywhere",
                    "presence_equals_ideals_everywhere",
                    "nesting_elementwise_everywhere",
                    "expected_fiber_elementwise_everywhere",
                    "conduit_combos_everywhere",
                    "readings_restricted_everywhere",
                    "k4_placements_pairwise_distinct_fiber_sets",
                    "static_handshake_n6_and_n12_every_point",
                    "fence_unchanged"):
            self.assertTrue(s[key], key)
        self.assertTrue(all(
            s["fibers_exactly_suffix_products_per_point"].values()))

    def test_receipt_rebuilds_identically(self):
        fresh = build_receipt()
        self.assertEqual(
            fresh["summary"], self.receipt["summary"])
        for name, table in fresh["tables"].items():
            for n, v in table.items():
                self.assertEqual(
                    v["assemblies"],
                    self.receipt["tables"][name][n]["assemblies"],
                    (name, n))


if __name__ == "__main__":
    unittest.main()
