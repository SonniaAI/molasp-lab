"""Receipt pins for designs/005 census-generality (tick 37).

Receipt: evidence/2026-10-07-census-generality/census_generality.out
Pre-registration (gates G1-G4 verbatim) landed at 79d1f90 before the
census ran. Verdicts: G1 confirmed, G2 confirmed, G3 falsified as
registered (lo-read stack refinement), G4 confirmed.

Lab rule of record (tests/README.md): every new test file shows its
names in verbose output of the exact ci.yml command before its count
is claimed anywhere.
"""
import json
import os
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EV = os.path.join(REPO, "evidence", "2026-10-07-census-generality")
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from molasp.compiler import compile_program          # noqa: E402
from molasp.offchannel import check_d4               # noqa: E402


def _load():
    arms, verdicts = {}, None
    with open(os.path.join(EV, "census_generality.out")) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            if line.startswith("VERDICTS "):
                verdicts = json.loads(line[len("VERDICTS "):])
            else:
                rec = json.loads(line)
                arms[rec["arm"]] = rec
    return arms, verdicts


class TestCensusGeneralityReceipt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.arms, cls.verdicts = _load()

    def test_receipt_shape_and_machine_verdicts(self):
        self.assertEqual(sorted(self.arms), [
            "AND_ONLY", "DEEP_FACTS", "MINIMAL", "UNIT_ONLY"])
        self.assertEqual(self.verdicts, {
            "G1": True, "G2": True, "G3": False, "G4": True})

    def test_minimal_one_fact_program_carries_row1_v0_hazard(self):
        m = self.arms["MINIMAL"]
        self.assertEqual(m["program"], "p.")
        self.assertEqual(m["lock_hazards"], {"3,1": {"V0p": 1}})
        self.assertEqual(m["lock_hazards_stable"], {})
        self.assertEqual(m["lock_stack_channels"], {})
        self.assertEqual(m["lock_misreads"], {})

    def test_g1_g2_all_squatters_vclass_b1_transient(self):
        for name, rec in self.arms.items():
            squatters = [t for sq in rec["lock_hazards"].values()
                         for t in sq]
            self.assertTrue(squatters, f"{name}: no lock hazards")
            for t in squatters:
                self.assertTrue(
                    t.startswith("V"),
                    f"{name}: non-V lock squatter {t}")
            self.assertEqual(
                rec["lock_hazards_stable"], {},
                f"{name}: stable solo hazard appeared")

    def test_g3_falsified_loread_stack_in_both_reader_geometries(self):
        # the registered gate expected zero stacks in UNIT_ONLY; the
        # receipt refines the mechanism instead: the lo-read stack
        # (reader south face = row-1 via glue) is constructional.
        sig = {"b_lower_solo": 1, "b_upper_solo": 0,
               "b_mutual_vertical": 1}
        for arm, pair in (("AND_ONLY", "V2p+DBr"),
                          ("UNIT_ONLY", "V2p+Ur")):
            got = self.arms[arm]["lock_stack_channels"]["3,2|3,3"][pair]
            for k, v in sig.items():
                self.assertEqual(got[k], v, f"{arm} {pair} {k}")
        # depth repeats the class: DEEP_FACTS carries it at 3,3|3,4
        deep = self.arms["DEEP_FACTS"]["lock_stack_channels"][
            "3,3|3,4"]["V3p+DBr"]
        self.assertEqual(deep["b_lower_solo"], 1)
        self.assertEqual(deep["b_upper_solo"], 0)

    def test_g4_depth_scaling_of_off_channel_sites(self):
        sites = {a: r["off_channel_sites"] for a, r in self.arms.items()}
        self.assertEqual(sites["MINIMAL"], 3)
        self.assertEqual(sites["AND_ONLY"], 7)
        self.assertEqual(sites["UNIT_ONLY"], 7)
        self.assertEqual(sites["DEEP_FACTS"], 10)

    def test_live_recompute_matches_receipt(self):
        # A1-style cross-check: the committed census is a deterministic
        # function of the compiler; recompute two arms live and compare
        # the gated fields.
        for arm in ("MINIMAL", "DEEP_FACTS"):
            rec = self.arms[arm]
            build = compile_program(rec["program"], name=arm)
            rep = check_d4(build)
            self.assertEqual(rep["lock_hazards"],
                             {k: dict(v) for k, v in
                              rec["lock_hazards"].items()})
            self.assertEqual(len(rep["lock_stack_channels"]),
                             len(rec["lock_stack_channels"]))
            self.assertEqual(rep["lock_misreads"], rec["lock_misreads"])


if __name__ == "__main__":
    unittest.main()
