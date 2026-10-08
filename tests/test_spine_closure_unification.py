"""Designs/010 §10.4-1 unification pin (stage 7, tick 62): exactly
one strength predicate (compiler.py); parity and offchannel consume
it; the divergent enumerated tables (parity SP1-4, offchannel
SP1-3 — the live row-4 divergence) are gone; SP5/SP6 close on BOTH
paths; value glues stay cooperative strength 1, so the cap has no
silent regression path."""

import unittest

from molasp import compiler, offchannel, parity


class SingleClosurePredicate(unittest.TestCase):
    def test_exactly_one_predicate_divergent_tables_deleted(self):
        self.assertTrue(hasattr(compiler, "glue_strength"))
        self.assertFalse(hasattr(parity, "STRENGTH"))
        self.assertFalse(hasattr(offchannel, "DEFAULT_STRENGTH"))
        self.assertIs(parity.glue_strength, compiler.glue_strength)

    def test_spine_class_closure_holds_on_both_paths(self):
        for path in (parity.glue_strength, offchannel.glue_strength):
            self.assertEqual(path("SP1", "SP1"), 2)
            self.assertEqual(path("SP4", "SP4"), 2)  # heals row 4
            self.assertEqual(path("SP5", "SP5"), 2)
            self.assertEqual(path("SP6", "SP6"), 2)
            self.assertEqual(path("SP40", "SP40"), 2)

    def test_value_glues_unchanged_on_both_paths(self):
        for path in (parity.glue_strength, offchannel.glue_strength):
            self.assertEqual(path("q-t-done", "q-t-done"), 1)
            self.assertEqual(path("and1_r", "and1_r"), 1)
            self.assertEqual(path("p-t", "q-t"), 0)
            self.assertEqual(path("SP5", "SP6"), 0)
            self.assertEqual(path("", "SP5"), 0)

    def test_offchannel_explicit_table_override_still_honored(self):
        table = {("SP9", "SP9"): 2}
        self.assertEqual(
            offchannel.glue_strength("SP9", "SP9", strength=table), 2)
        # explicit non-spine table: cooperative fallback, no closure
        self.assertEqual(
            offchannel.glue_strength("SP5", "SP5", strength={}), 1)


if __name__ == "__main__":
    unittest.main()
