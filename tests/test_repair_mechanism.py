"""Repair-mechanism study pins (tick 24, SON-4778).

Static half: the off-channel census facts that carry the
trap-relief/substitution-repair story, recomputed (not read from a
receipt) so the pins are independent of any run artefact.

kTAM half: receipt pins on evidence/2026-10-07-repair-mechanism/
trap_grid.out once collected (skipped until it exists).
"""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EV = os.path.join(os.path.dirname(HERE), "evidence",
                  "2026-10-07-repair-mechanism")
if EV not in sys.path:
    sys.path.insert(0, EV)

import trap_census  # noqa: E402


def sites_for(report, system, tile):
    sp = report["systems"][system]["off_channel_sites_per_species"]
    return set(sp.get(tile, []))


class TestOffChannelCensus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rep = trap_census.compute()

    def test_vp_and_v0p_squat_the_lock_column(self):
        """The two exceeds-parity species are exactly the two with
        b=1 lock-site squatter channels in build1."""
        self.assertEqual(sites_for(self.rep, "build1", "Vp"),
                         {"1,1", "1,2", "2,1", "2,3", "3,2"})
        self.assertEqual(sites_for(self.rep, "build1", "V0p"),
                         {"1,1", "2,2", "3,1"})

    def test_unique_glue_species_have_no_off_channel(self):
        """DAr/L3 and the spine tiles are single-site species: no
        squatter channel anywhere (their glues are unique)."""
        for tile in ("DAr", "L3", "S1", "S2", "S3"):
            self.assertEqual(sites_for(self.rep, "build1", tile), set(),
                             tile)

    def test_spine_sites_admit_no_squatter(self):
        oc = self.rep["systems"]["build1"]["off_channel"]
        for site in ("0,1", "0,2", "0,3"):
            self.assertNotIn(site, oc)

    def test_l3_misread_channel_needs_west_substitution(self):
        """L2@(3,3) bonds only if (2,3) hosts Vp or D2T (exposing a
        q-t value glue) — the structural channel behind tick-23's
        18/500 L3-only falsifier."""
        probe = self.rep["systems"]["L3"]["lock_deep_probe"]["3,3"]
        self.assertEqual(set(probe.keys()), {"Vp", "D2T"})
        for west, channels in probe.items():
            self.assertIn("L2", channels)

    def test_stable_substitution_repairs(self):
        """The substitution-repair candidates are b=2 (stable) at the
        vacancy: D2T at Vp's site, D1T at V0p's site."""
        vp = self.rep["systems"]["Vp"]["off_channel"]["2,2"]
        self.assertEqual(vp.get("D2T"), 2)
        v0p = self.rep["systems"]["V0p"]["off_channel"]["2,1"]
        self.assertEqual(v0p.get("D1T"), 2)


class TestTrapGridReceipt(unittest.TestCase):
    """Receipt pins — active only after the queue job is collected."""
    GRID = os.path.join(EV, "trap_grid.out")

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(cls.GRID):
            raise unittest.SkipTest("trap_grid.out not collected yet")
        cls.header = None
        cls.rows = []
        cls.verdicts = None
        with open(cls.GRID, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                d = json.loads(line)
                if "n_per_point" in d:
                    cls.header = d
                elif "verdicts" in d:
                    cls.verdicts = d["verdicts"]
                elif "system" in d:
                    cls.rows.append(d)

    def test_protocol_of_record(self):
        self.assertEqual(self.header["n_per_point"], 500)
        self.assertEqual(self.header["seed_base"], 20261107)
        self.assertEqual(self.header["Gse"], 9.0)
        self.assertEqual(self.header["Gmc_grid"], [9.5, 11.0, 13.0])
        self.assertEqual(len(self.rows), 24)  # 8 systems x 3 points

    def test_continuity_with_tick23(self):
        ref = self.header["tick23_reference_pqr"]
        for row in self.rows:
            if row["key"] in ref:
                # JSON round-trip stringifies the float dG keys
                # ("0.5"/"2.0"/"4.0"); coerce the lookup, not the data.
                expected = ref[row["key"]][str(row["dGmc"])]
                self.absLT(row["pqr_frac"], expected, 0.12,
                           "%s dG %s" % (row["key"], row["dGmc"]))

    def absLT(self, a, b, tol, ctx):
        self.assertLess(abs(a - b), tol, "%s: %s vs %s" % (ctx, a, b))

    def test_verdict_block_present(self):
        for key in ("R2", "R3a", "R3b_V0p", "R3b_Vp", "R3c", "R4"):
            self.assertIn(key, self.verdicts)


if __name__ == "__main__":
    unittest.main()
