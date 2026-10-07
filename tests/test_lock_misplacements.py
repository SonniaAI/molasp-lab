"""Receipt pins for designs/006 lock-misplacement census (tick 39).

Receipt: evidence/2026-10-07-lock-misplacement-census/
lock_misplacement_census.out
Pre-registration (gates M1-M4 verbatim) landed at 1570193 before the
census ran. Verdicts: M1 confirmed, M2 FALSIFIED as registered (the
kinetically-dominant lock-site misplacements are one-substitution-
enabled — caught by the existing pair layer lock_misreads, not the
solo census; the solo class is the via-site placements, which double
to stable b=2 under s2), M3 confirmed, M4 confirmed.

Lab rule of record (tests/README.md): every new test file shows its
names in verbose output of the exact ci.yml command before its count
is claimed anywhere.
"""
import json
import os
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EV = os.path.join(REPO, "evidence", "2026-10-07-lock-misplacement-census")
SIB_AND = os.path.join(REPO, "evidence",
                       "2026-10-06-body-conjunction-builds")
for p in (REPO, SIB_AND):
    if p not in sys.path:
        sys.path.insert(0, p)

from tiles_and import BUILD1                          # noqa: E402
from molasp.compiler import compile_program           # noqa: E402
from molasp import offchannel as oc                   # noqa: E402


def _load():
    views, verdicts = {}, None
    with open(os.path.join(EV, "lock_misplacement_census.out")) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            if line.startswith("VERDICTS "):
                verdicts = json.loads(line[len("VERDICTS "):])
            else:
                rec = json.loads(line)
                views[rec["view"]] = rec
    return views, verdicts


class ReceiptShape(unittest.TestCase):
    def test_four_views_and_verdicts_present(self):
        views, verdicts = _load()
        self.assertEqual(
            sorted(views),
            ["BUILD1_fam", "BUILD1_s2", "UNIT_ONLY_fam", "UNIT_ONLY_s2"])
        self.assertEqual(
            verdicts, {"M1": True, "M2": False, "M3": True, "M4": True})


class M1SoloClassPins(unittest.TestCase):
    """M1 CONFIRMED: fam views carry the solo L*-misplacement class,
    all channels transient (bond == 1)."""

    def test_fam_views_two_via_site_channels_bond_one(self):
        views, _ = _load()
        for v in ("BUILD1_fam", "UNIT_ONLY_fam"):
            rec = views[v]
            self.assertGreaterEqual(rec["n_channels"], 1)
            self.assertTrue(rec["all_bond_1"])
            self.assertEqual(rec["lock_misplacements"],
                             {"2,1": {"L1": {"bond": 1, "faces": {"W": 1},
                                             "w_read": True}},
                              "2,2": {"L2": {"bond": 1, "faces": {"W": 1},
                                             "w_read": True}}})

    def test_solo_class_is_via_site_w_read_carried(self):
        views, _ = _load()
        for v in ("BUILD1_fam", "BUILD1_s2"):
            self.assertEqual(views[v]["w_read_channels"],
                             ["L1@2,1", "L2@2,2"])


class M2FalsificationPins(unittest.TestCase):
    """M2 FALSIFIED as registered: the kinetically-dominant lock-site
    misplacements L2@3,3 / L3@3,2 carry ZERO solo bond in every view
    (named channels null) — they are one-substitution-enabled, not
    solo.  The s2-doubling that DID hold: via-site channels double to
    stable bond 2, and non-L lock-site squatters stay <= 1."""

    def test_named_lock_site_channels_absent_solo_everywhere(self):
        views, _ = _load()
        for v, rec in views.items():
            self.assertIsNone(rec["named"]["L2@3,3"], v)
            self.assertIsNone(rec["named"]["L3@3,2"], v)

    def test_s2_doubles_via_site_class_to_stable_bond_two(self):
        views, _ = _load()
        tile_of = {"2,1": "L1", "2,2": "L2"}
        for v in ("BUILD1_s2", "UNIT_ONLY_s2"):
            rec = views[v]
            self.assertEqual(rec["max_bond"], 2)
            self.assertFalse(rec["all_bond_1"])
            for site, tile in tile_of.items():
                self.assertEqual(
                    rec["lock_misplacements"][site][tile]["bond"], 2)

    def test_nonl_lock_site_squatters_never_gain_under_s2(self):
        views, _ = _load()
        for v in ("BUILD1_fam", "BUILD1_s2",
                  "UNIT_ONLY_fam", "UNIT_ONLY_s2"):
            self.assertLessEqual(views[v]["nonl_lock_site_max_bond"], 1)


class M3NoNewPhysics(unittest.TestCase):
    def test_receipt_mismatches_empty_all_views(self):
        views, _ = _load()
        for v, rec in views.items():
            self.assertEqual(rec["m3_mismatches"], [], v)

    def test_layer_is_relabeling_of_off_channel_on_build1(self):
        canon = oc.canonical_assembly(BUILD1)
        layer = oc.lock_misplacements(BUILD1, canon)
        table = oc.off_channel(BUILD1, canon)
        for site, placements in layer.items():
            for tile, ch in placements.items():
                self.assertTrue(tile.startswith("L"))
                self.assertNotEqual(tile, canon[tuple(
                    int(x) for x in site.split(","))])
                self.assertEqual(table[site][tile], ch["bond"])
                self.assertEqual(ch["w_read"], ch["faces"].get("W", 0) >= 1)


class M4EmitPath(unittest.TestCase):
    def test_auto_attached_d4_carries_layer_on_compile_arms(self):
        for prog in ("p. q. r :- p.", "p."):
            build = compile_program(prog, name="emit-path-check")
            self.assertIn("lock_misplacements", build["d4"])
            self.assertEqual(json.dumps(build["d4"], sort_keys=True),
                             json.dumps(oc.check_d4(build),
                                        sort_keys=True))

    def test_report_lines_flag_the_class(self):
        lines = oc.d4_report_lines(oc.check_d4(BUILD1))
        joined = "\n".join(lines)
        self.assertIn("lock misplacement: L1 at 2,1", joined)
        self.assertIn("w-read channel", joined)


class PairLayerCoveragePins(unittest.TestCase):
    """The M2 resolution: the kinetic-dominant lock-site misplacements
    ARE flagged by the existing west-substitution pair layer
    (lock_misreads), at bond 1 — one background substitution enables
    them, which is why the solo census reads null."""

    def test_lock_site_lock_channels_caught_by_deep_probe(self):
        canon = oc.canonical_assembly(BUILD1)
        locks = oc.infer_lock_sites(canon)
        mis = oc.lock_misreads_from(
            oc.lock_deep_probe(BUILD1, canon, locks))
        self.assertEqual(mis["3,3"]["D2T"], {"L2": 1})
        self.assertEqual(mis["3,3"]["Vp"], {"L2": 1})
        self.assertEqual(mis["3,2"]["DBr"], {"L3": 1})
        self.assertEqual(mis["3,1"]["Vp"], {"L2": 1})

    def test_measured_context_quotes_strength2_counts(self):
        ctx = oc.MEASURED_CONTEXT["strength2_lock_misplacements"]
        self.assertEqual(ctx["s2_b1"]["L2@(3,3)"], 67)
        self.assertEqual(ctx["s2_b1"]["L3@(3,2)"], 43)
        self.assertEqual(ctx["s2_b1_Vp_arm"]["L3@(3,2)"], 82)
        self.assertEqual(ctx["fam_refs"]["L2@(3,3)"], 10)


if __name__ == "__main__":
    unittest.main()
