"""Structural-death build tests — tick 22 (SON-4773).

Pins the deterministic aTAM verdicts (S1) for the missing-species
build: BUILD1 (P_AND) minus the DAr tile species. kTAM arm receipts
live in evidence/2026-10-06-structural-death/ (run.out, submit.out);
the internal-consistency pin below checksums the recorded grid.
"""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EVID = os.path.join(os.path.dirname(HERE), "evidence")
DEATH_DIR = os.path.join(EVID, "2026-10-06-structural-death")
AND_DIR = os.path.join(EVID, "2026-10-06-body-conjunction-builds")
for p in (DEATH_DIR, AND_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from tiles_and import BUILD1  # noqa: E402
from tiles_death import BUILD_DEAD, DEAD_SPECIES  # noqa: E402
from atam_check_and import producible, decode  # noqa: E402

try:
    import clingo  # noqa: F401
    CLINGO_OK = True
except ImportError:
    CLINGO_OK = False

RUN_OUT = os.path.join(DEATH_DIR, "run.out")


class StructuralDeathATAM(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.seen, cls.terms = producible(BUILD_DEAD)
        cls.names = set()
        cls.site13 = 0
        for asm in cls.seen:
            for pos, name in asm:
                cls.names.add(name)
                if pos == (1, 3):
                    cls.site13 += 1

    def test_inventory_is_build1_minus_dar(self):
        self.assertEqual(
            set(BUILD1["tiles"]) - {DEAD_SPECIES},
            set(BUILD_DEAD["tiles"]))
        self.assertNotIn(DEAD_SPECIES, BUILD_DEAD["tiles"])

    def test_unique_terminal_decodes_pq(self):
        self.assertEqual(len(self.terms), 1)
        self.assertEqual(decode(BUILD_DEAD, self.terms[0]), ("pq", 2))

    def test_dead_species_never_producible(self):
        self.assertNotIn("DBr", self.names)
        self.assertNotIn("L3", self.names)

    def test_dar_site_never_occupied(self):
        self.assertEqual(self.site13, 0)

    def test_and_chain_glues_never_exposed(self):
        for asm in self.seen:
            for _pos, name in asm:
                if name.startswith("seed"):
                    continue
                for glue in BUILD_DEAD["tiles"][name].values():
                    self.assertNotIn(glue, ("and1_r", "r-t", "r-t-done"))


@unittest.skipUnless(CLINGO_OK, "clingo module not available")
class StructuralDeathSemantics(unittest.TestCase):

    def test_stable_models_anchor_the_death_readout(self):
        from atam_check_and import clingo_models
        self.assertEqual(clingo_models("p. q. r :- p, q."),
                         [["p.", "q.", "r."]])
        self.assertEqual(clingo_models("p. q."), [["p.", "q."]])


@unittest.skipUnless(os.path.exists(RUN_OUT), "grid not collected yet")
class StructuralDeathGridReceipt(unittest.TestCase):
    """Internal-consistency checksum of the recorded kTAM grid: the
    per-point pqr counts must sum to the recorded pqr_total for each
    system (guards against truncated/corrupted receipts)."""

    def test_pqr_totals_consistent(self):
        with open(RUN_OUT) as fh:
            lines = [ln for ln in fh.read().splitlines()
                     if ln.startswith("{")]
        rows = {}
        totals = {}
        for ln in lines:
            obj = json.loads(ln)
            if "decode" in obj and "system" in obj:
                rows.setdefault(obj["system"], []).append(obj)
            elif "pqr_total" in obj:
                totals[obj["system"]] = obj["pqr_total"]
        self.assertEqual(set(rows), set(totals))
        for sys_name, pts in rows.items():
            per_point = {r["dGmc"]: r["decode"].get("pqr", 0) for r in pts}
            self.assertEqual(len(per_point), 4)
            self.assertEqual(sum(per_point.values()), totals[sys_name])


if __name__ == "__main__":
    unittest.main()
