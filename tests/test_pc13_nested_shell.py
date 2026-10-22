"""Tick-163 pins: the nested-shell product law, tested live.

Every scalar is re-derived live on each run (no stored constants
for the census/derivation results); the receipt hash pins byte
stability of the recorded evidence, and a small set of hand-pinned
closed-form scalars guards against silent formula drift.
"""

import hashlib
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.pc13_nested_shell import (        # noqa: E402
    ROWS,
    DEPTH3_PROBES,
    additive_falsifier,
    guard_probe,
    nesting_elementwise,
    receipts_via_shell_law,
    reduction_grid,
    shell_law,
    shell_size,
    shell_sizes_agree_with_ladder,
)
from tools.pc11_coefficient_ladder import ladder_count  # noqa: E402

RECEIPT_PATH = os.path.join(
    ROOT, "evidence", "2026-10-22-pc13-nested-shell-law",
    "nested_shell.json")
RECEIPT_SHA256 = ("b639283cde1525aa667f5f211b00c985"
                  "ad84032b9296e4f93dd7951b9df15fe2")

# Hand-pinned closed-form scalars (derived independently of the tool:
# |I| + 7*C(n+2,2) + 3*2*C(n+1,2) + 1*3*C(n,2) at ks=[2,2,2]).
DEPTH3_222 = {6: 577, 7: 813, 8: 1110, 9: 1478, 10: 1928, 11: 2472,
              12: 3123}


class ShellsTest(unittest.TestCase):
    def test_shell_sizes_agree_with_ladder_everywhere(self):
        for n in ROWS:
            self.assertTrue(shell_sizes_agree_with_ladder(n, 4), n)

    def test_shells_nested_elementwise_everywhere(self):
        for n in ROWS:
            got = nesting_elementwise(n, 4)
            self.assertTrue(got["contained_pairwise"], (n, got))
            self.assertEqual(got["sizes"],
                             [ladder_count(n, d) for d in range(5)], n)
            self.assertTrue(all(got["sizes_match_ladder"]), n)

    def test_first_two_shells_are_the_measured_corners(self):
        # shell 0 = |C_w| = C(n+2,2); shells 0+1 = |C_r| = (n+1)(3n+2)/2
        for n in ROWS:
            self.assertEqual(shell_size(n, 0), (n + 1) * (n + 2) // 2, n)
            self.assertEqual(shell_size(n, 0) + shell_size(n, 1),
                             (n + 1) * (3 * n + 2) // 2, n)


class LawTest(unittest.TestCase):
    def test_reduction_identity_wide_grid(self):
        got = reduction_grid()
        self.assertTrue(got["all_equal"], got)
        self.assertEqual(got["points"], 128)

    def test_receipts_reproduced_via_shell_law(self):
        got = receipts_via_shell_law()
        self.assertTrue(got["all_four_corners_hold_shell_law"], got)
        self.assertEqual(got["scalars_checked"], 28)

    def test_depth3_predictions_pinned(self):
        for n, want in DEPTH3_222.items():
            self.assertEqual(shell_law(n, [2, 2, 2]), want, n)

    def test_discriminators_separate_at_n6(self):
        for ks in ([2, 2, 2], [3, 2, 2], [2, 2, 3], [2, 2, 2, 2]):
            self.assertGreater(
                shell_law(6, ks) - additive_falsifier(6, ks), 100, ks)


class GuardTest(unittest.TestCase):
    def test_both_depth3_axes_refused_verbatim(self):
        probes = guard_probe()
        self.assertEqual(sorted(probes), sorted(DEPTH3_PROBES))
        for label, entry in probes.items():
            self.assertFalse(entry["compiled"], label)
            self.assertIn(
                "second relayed OR head in one chain is unexamined",
                entry["refusal"], label)
            self.assertIn("designs/012", entry["refusal"], label)


class ReceiptTest(unittest.TestCase):
    def test_receipt_byte_stability(self):
        with open(RECEIPT_PATH, "rb") as fh:
            digest = hashlib.sha256(fh.read()).hexdigest()
        self.assertEqual(digest, RECEIPT_SHA256)

    def test_receipt_records_the_law_and_probes(self):
        with open(RECEIPT_PATH) as fh:
            receipt = json.load(fh)
        self.assertEqual(receipt["kind"], "pc13-nested-shell-law")
        self.assertTrue(receipt["reduction_grid"]["all_equal"])
        self.assertTrue(
            receipt["receipts_via_shell_law"]["all_four_corners_hold_shell_law"])
        self.assertTrue(all(
            not v["compiled"] for v in receipt["guard_probes"].values()))


if __name__ == "__main__":
    unittest.main()
