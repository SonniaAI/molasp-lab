"""Invariants for the row-2 ordering instrumented MC (tick 9).

Pins the structural claims of research-log/2026-10-06-row2-ordering.md
so the instrumented pipeline cannot silently drift: every unfounded
decode is a read-time D2T+L2 trap; trap counts never exceed excursion
counts; pipeline stages are ordered; reruns from the same seed are
bit-identical. Small n (20) so CI stays fast; statistical claims live
in the committed run.out, not here.
"""
import math
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EV = os.path.join(os.path.dirname(HERE), "evidence", "2026-10-06-row2-ordering")
sys.path.insert(0, EV)

from instrument_mc import run_assembly  # noqa: E402


def sweep(seed0=20261100, n=20, Gmc=11.0, Gse=9.0):
    T_read = 400.0 * math.exp(Gmc)
    return [run_assembly(Gmc, Gse, T_read, seed0 + i) for i in range(n)]


class TestRow2Ordering(unittest.TestCase):
    def test_pipeline_ordering_and_trap_identity(self):
        runs = sweep()
        for decode, s in runs:
            g = lambda k: s.get(k, 0)  # Counter omits never-hit keys
            self.assertLessEqual(g("trap_at_read"), g("trap_ever"))
            self.assertLessEqual(g("trap_ever"), g("d2t_ever"))
            if s.get("trap_at_read"):
                self.assertIn(decode, ("ap", "p"))
            if decode in ("ap", "p"):
                self.assertEqual(s.get("trap_at_read"), 1)
            self.assertLessEqual(g("d2t_attach_with_l1"), g("d2t_attach"))
            self.assertLessEqual(g("l2_onto_d2t"), g("d2t_attach"))

    def test_deterministic_from_seed(self):
        a = sweep(seed0=20271001)
        b = sweep(seed0=20271001)
        self.assertEqual(a, b)

    def test_d2t_value_channel_cannot_reach_b2(self):
        # Structural (no MC): D2T's south glue no-p has no partner, so in
        # the correct row-1 context (S2, D1T, L1 resident; no L2) D2T can
        # only enter at b=1 via go2, while the correct D2F enters at b=2.
        # A D2T at b=2 therefore always requires a resident lock — the
        # reverse-order trap (D2T onto a resident b=1 L2) is real and was
        # caught by this test's first version failing on exactly that.
        import tiles_v2
        ctx = {(0, 0): "seed0", (1, 0): "seed1", (2, 0): "seed2",
               (0, 1): "S1", (1, 1): "D1T", (2, 1): "L1", (0, 2): "S2"}
        self.assertEqual(tiles_v2.matched_strength(ctx, (1, 2), "D2T"), 1)
        self.assertEqual(tiles_v2.matched_strength(ctx, (1, 2), "D2F"), 2)


if __name__ == "__main__":
    unittest.main()
