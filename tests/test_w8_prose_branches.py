"""Pins for the pre-drafted designs/011 prose branches (tick 83).

research-log/2026-10-09-w8-prose-branches.md pre-drafts the single
deliberate hand step of the w8 collection chain (the designs/011 prose
edit) for both milestone branches, committed BEFORE the data exists.
These tests keep the pre-registration honest: the drafts must stay
placeholder-only (no invented measured numbers), the placeholders must
map onto exactly the receipt fields the toolchain reads, and both
milestone branches of tools/collect_w8.py must be covered.
"""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROSE = REPO / "research-log" / "2026-10-09-w8-prose-branches.md"

# The field set tools/apply_w8_receipt.py reads from the receipt
# (figure_nums + addendum) and that the prose branches are allowed to
# quote.  If the toolchain's receipt contract changes, this pin fails
# loudly instead of letting the prose drift.
RECEIPT_FIELDS = {
    "fresh_terminal_share",
    "dev_vs_pred_w8",
    "fresh_w8_wilson95",
    "fresh_terminal_census",
    "n_per_range",
}

# Derived placeholders documented in the prose file's mapping.
PLACEHOLDERS = {"share", "dev", "lo", "hi", "d2t", "l2", "n", "date"}


class TestW8ProseBranches(unittest.TestCase):
    def setUp(self):
        self.text = PROSE.read_text(encoding="utf-8")

    def _section(self, branch):
        head = "## Branch %s" % branch
        self.assertIn(head, self.text)
        return self.text.split(head, 1)[1].split("\n## ", 1)[0]

    def test_both_milestone_branches_present(self):
        from tools.collect_w8 import ACTIONS
        milestone = {"CAL_OK+HELD", "CAL_OK+REFUTED"}
        self.assertEqual(milestone, set(ACTIONS) & milestone)
        for branch in milestone:
            self.assertIn("## Branch %s" % branch, self.text)

    def test_placeholders_are_defined(self):
        used = set(re.findall(r"\{([a-z0-9_]+)\}", self.text))
        self.assertTrue(used)
        self.assertLessEqual(used, PLACEHOLDERS)

    def test_receipt_field_contract_documented(self):
        for field in RECEIPT_FIELDS:
            self.assertIn(field, self.text)

    def test_held_edits_touch_curve_row_checks_falsifier(self):
        held = self._section("CAL_OK+HELD")
        self.assertIn("| w8 | — | 0.83376 [0.81585 hazard-95] | ratchet-tilted |", held)
        self.assertIn("P5", held)
        self.assertIn("±0.05", held)
        self.assertIn("{share}", held)
        self.assertIn("sensitivity arm, not a fit", held)

    def test_refuted_edits_retract_and_quarantine(self):
        refuted = self._section("CAL_OK+REFUTED")
        self.assertIn("RETRACTED", refuted)
        self.assertIn("Retraction", refuted)
        self.assertIn("quarantin", refuted.lower())
        self.assertIn("through w4 only", refuted)
        self.assertIn("{share}", refuted)

    def test_no_invented_measured_number(self):
        # The drafts are placeholder-only: any concrete "measured" w8
        # share would be a number invented before the data exists.
        for m in re.finditer(r"measured fill share ([0-9.]+)", self.text):
            self.fail("hardcoded measured share %r in pre-draft" % m.group(1))
        for m in re.finditer(r"share =? ([0-9]\.[0-9]+)", self.text):
            self.fail("hardcoded share value %r in pre-draft" % m.group(1))

    def test_non_verdictable_branches_excluded(self):
        tail = self.text.split("## Non-verdictable branches", 1)[1]
        self.assertIn("NO designs/011 edit", tail)
        self.assertIn("cross_check", tail)


if __name__ == "__main__":
    unittest.main()
