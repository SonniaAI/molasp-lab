"""Receipt + layer pins for the tick-42 vacancy contention-set
pricing census (evidence/2026-10-07-vacancy-contention/).  Verdicts
as REGISTERED in the census header — including the disclosed C4
registration-defect correction (v1 receipt kept verbatim, falsified
on the defective clause; corrected clause CONFIRMED)."""

import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
EV = os.path.join(REPO, "evidence", "2026-10-07-vacancy-contention")
VB_EV = os.path.join(REPO, "evidence", "2026-10-07-vacancy-background")

import sys                                         # noqa: E402

if REPO not in sys.path:
    sys.path.insert(0, REPO)
SIB_AND = os.path.join(REPO, "evidence",
                       "2026-10-06-body-conjunction-builds")
if SIB_AND not in sys.path:
    sys.path.insert(0, SIB_AND)

from tiles_and import BUILD1, BUILD2, BUILD3        # noqa: E402
from molasp.compiler import compile_program         # noqa: E402
from molasp import offchannel as oc                 # noqa: E402


def _load(path):
    recs = []
    verdicts = None
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            body = line[9:] if line.startswith("VERDICTS ") else line
            d = json.loads(body)
            if isinstance(d, dict) and "system" in d:
                recs.append(d)
            else:
                verdicts = d
    return recs, verdicts


class TestVacancyContentionReceipt(unittest.TestCase):
    """Pins the corrected census receipt AND the v1 falsified run
    (the disclosure is load-bearing: the correction must never be
    quietly rewritten into a clean history)."""

    @classmethod
    def setUpClass(cls):
        cls.recs, cls.verdicts = _load(os.path.join(
            EV, "vacancy_contention.out"))
        with open(os.path.join(
                EV, "vacancy_contention.v1-c4-registration-defect.out")
                ) as fh:
            cls.v1 = json.loads([
                ln for ln in fh if ln.startswith("VERDICTS ")][-1][9:])
        cls.vp = next(r for r in cls.recs
                      if r.get("site") == "2,2"
                      and r["species"] == "Vp")

    def test_corrected_verdicts_all_confirmed(self):
        self.assertEqual(
            self.verdicts,
            {"C1": "CONFIRMED", "C2": "CONFIRMED", "C3": "CONFIRMED",
             "C4": "CONFIRMED", "C5": "CONFIRMED"})

    def test_v1_receipt_records_falsified_c4_others_confirmed(self):
        self.assertEqual(self.v1["C4"], "FALSIFIED")
        for k in ("C1", "C2", "C3", "C5"):
            self.assertEqual(self.v1[k], "CONFIRMED")

    def test_receipt_carries_measured_anchors(self):
        self.assertEqual(
            self.vp["measured_s2_occupants"],
            {"D2T": 203, "L2": 150, "DBr": 78, "L3": 54,
             "D1T": 6, "S2": 4})
        self.assertEqual(self.vp["family_stable"], ["D2T", "L2"])
        self.assertEqual(
            self.vp["s2_stable"],
            ["D1T", "D2T", "DBr", "L2", "V0p"])


class TestVacancyContentionLayer(unittest.TestCase):
    """The layer itself: classes, per-knob pricing, stack
    partnership, and the family-minority / s2-minting structure."""

    @classmethod
    def setUpClass(cls):
        cls.canon = oc.canonical_assembly(BUILD1)
        cls.vc = oc.vacancy_contention(BUILD1, cls.canon)
        cls.rec = cls.vc["Vp"]["2,2"]

    def test_c1_set_coverage(self):
        self.assertIn("fill", self.rec["D2T"]["classes"])
        self.assertIn("via_squatter", self.rec["L2"]["classes"])
        self.assertTrue(self.rec["L2"]["w_read"])
        self.assertIn("stack_partner", self.rec["DBr"]["classes"])
        en = self.rec["DBr"]["enables"]["L3@3,2"]
        self.assertGreaterEqual(en["s2"]["b_with"], 2)
        self.assertLess(en["s2"]["b_without"], 2)

    def test_c2_family_minority_not_monopoly(self):
        fam = sorted(t for t, c in self.rec.items()
                     if "family" in c["stable_under"])
        self.assertEqual(fam, ["D2T", "L2"])
        self.assertEqual(self.rec["D2T"]["bond"]["family"], 2)

    def test_c3_s2_minting(self):
        fam = {t for t, c in self.rec.items()
               if "family" in c["stable_under"]}
        s2 = {t for t, c in self.rec.items()
              if "s2" in c["stable_under"]}
        self.assertTrue({"D2T", "L2", "DBr"} <= s2)
        self.assertGreater(s2, fam)
        self.assertEqual(self.rec["L2"]["bond"],
                         {"family": 1, "s2": 2})

    def test_dbr_channel_is_the_measured_stack(self):
        # the cooperative channel a solo census cannot price: DBr's
        # own family bond is 1, its stability arrives via L3@(3,2)
        self.assertEqual(self.rec["DBr"]["bond"]["family"], 1)
        self.assertEqual(
            self.rec["DBr"]["enables"]["L3@3,2"]["family"],
            {"b_with": 1, "b_without": 0})

    def test_deterministic_across_calls(self):
        for b in (BUILD1, BUILD2, BUILD3):
            a = json.dumps(oc.vacancy_contention(b), sort_keys=True)
            c = json.dumps(oc.vacancy_contention(b), sort_keys=True)
            self.assertEqual(a, c)

    def test_minting_is_constructional_across_corpus(self):
        # every build has at least one vacancy whose stable set
        # strictly grows under s2 (the pricing surface the census
        # exists to expose)
        for b in (BUILD1, BUILD2, BUILD3):
            table = oc.vacancy_contention(b)
            minted = False
            for sites in table.values():
                for cont in sites.values():
                    fam = {t for t, c in cont.items()
                           if "family" in c["stable_under"]}
                    s2 = {t for t, c in cont.items()
                          if "s2" in c["stable_under"]}
                    if s2 > fam:
                        minted = True
            self.assertTrue(minted)

    def test_d4_integration(self):
        rep = oc.check_d4(BUILD1)
        self.assertEqual(rep["vacancy_contention"], self.vc)
        lines = oc.d4_report_lines(rep)
        self.assertTrue(any(
            "vacancy contention (Vp-missing) at 2,2" in ln
            for ln in lines))
        self.assertIn("vacancy_contention",
                      compile_program("and")["d4"])

    def test_measured_context_matches_tick41_receipt(self):
        # cross-receipt consistency: the MEASURED_CONTEXT block the
        # d4 warning quotes must equal the tick-41 receipt values
        with open(os.path.join(VB_EV, "vacancy_bg.out")) as fh:
            vb = [json.loads(ln) for ln in fh if '"arm"' in ln]
        s2 = next(r for r in vb if r["arm"] == "s2_b1_Vp")
        fam = next(r for r in vb if r["arm"] == "fam_b1_Vp")
        ctx = oc.MEASURED_CONTEXT["vacancy_contention"]
        self.assertEqual(
            ctx["s2_west_site_terminal_occupants_of_500"],
            s2["west_site_occupants"])
        self.assertEqual(ctx["fill_frac"]["s2"], s2["fill_frac"])
        self.assertEqual(ctx["fill_frac"]["family"], fam["fill_frac"])
        self.assertEqual(ctx["fill_given_L3_present"],
                         s2["fill_given_L3"])
        # MEASURED_CONTEXT quotes the receipt at 3 digits (0.214);
        # the receipt stores the full float — compare at quote
        # precision (tick-25 lesson: pins reading serialized
        # receipts must honor stored precision, not invent it)
        self.assertAlmostEqual(ctx["race_L3_first_frac"],
                               s2["race_L3_first_frac"], places=3)


if __name__ == "__main__":
    unittest.main()
