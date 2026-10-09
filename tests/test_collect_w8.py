"""Pins for the executable pre-registration (tools/collect_w8.py).

Every branch of the frozen w8 interpretation map is exercised on a
SYNTHETIC run.out built with the harness's exact output shapes, so the
gate arithmetic is committed and pinned BEFORE the real data exists.
Collection day must be mechanical: parse -> recompute -> cross-check
-> receipt + pre-registered actions.
"""

import json
import unittest

from tools.collect_w8 import collect, parse_runout, recompute, wilson


def _census(d2t, l2, n=500):
    return {"D2T": d2t, "L2": l2, "other": n - d2t - l2,
            "share": d2t / float(d2t + l2) if d2t + l2 else None}


def _stats(cal=(367, 131), fr_term=(384, 77), fr_mid=(368, 132), n=500):
    dev = abs(fr_term[0] / float(sum(fr_term)) - 0.83376)
    return {
        "n_per_range": n, "seed0_cal": 260261107, "seed0_fresh": 280261107,
        "dg": 2, "win_mult": 8, "t_mid_is_w4": True,
        "cal_mid_w4": _census(*cal, n=n), "cal_terminal_w8": _census(419, 73, n=n),
        "fresh_mid_w4": _census(*fr_mid, n=n),
        "fresh_terminal_w8": _census(*fr_term, n=n),
        "pred_w8": 0.83376, "haz95_arm": 0.81585,
        "dev_fresh_w8": dev,
        "fresh_w8_wilson95": wilson(fr_term[0], sum(fr_term)),
        "fresh_mid_w4_dev_vs_dw9_receipt": abs(fr_mid[0] / float(sum(fr_mid)) - 0.716),
        "receipts": {"dw9_fresh_w4": 0.716, "vh_heldout_w4": 0.7379032258064516},
    }


def _runout(stats, cal="CAL_OK", w8="HELD"):
    """Harness stdout shape: junk preamble, stats line, verdict line,
    VERDICTS line."""
    lines = ["[cluster preamble] node spark-4a06", ""]
    lines.append(json.dumps(stats))
    lines.append(json.dumps({"CAL": cal, "W8": w8}))
    lines.append("VERDICTS " + json.dumps({"CAL": cal, "W8": w8}, sort_keys=True))
    return "\n".join(lines) + "\n"


class ParseTests(unittest.TestCase):
    def test_parses_stats_and_verdicts_amid_junk(self):
        stats, verdicts = parse_runout(_runout(_stats()))
        self.assertEqual(stats["cal_mid_w4"]["D2T"], 367)
        self.assertEqual(verdicts, {"CAL": "CAL_OK", "W8": "HELD"})

    def test_missing_verdicts_line_refused(self):
        with self.assertRaises(ValueError):
            parse_runout(json.dumps(_stats()))


class GateArithmeticTests(unittest.TestCase):
    def test_held_branch(self):
        receipt = collect(_runout(_stats(fr_term=(384, 77))))
        # 384/(384+77) = 0.83297..., |dev| = 0.00079 <= 0.05
        self.assertEqual(receipt["branch"], "CAL_OK+HELD")
        self.assertEqual(receipt["cross_check"], "ok")
        self.assertTrue(receipt["actions"][0].startswith("w8 tier stands"))
        self.assertAlmostEqual(receipt["descriptive"]["dev_vs_pred_w8"],
                               0.00079, places=4)

    def test_refuted_branch(self):
        receipt = collect(_runout(_stats(fr_term=(300, 200)), w8="REFUTED"))
        # 300/500 = 0.6, dev 0.23376 > 0.05
        self.assertEqual(receipt["branch"], "CAL_OK+REFUTED")
        joined = " ".join(receipt["actions"])
        self.assertIn("retract", joined)
        self.assertIn("quarantine", joined)

    def test_cal_fail_voids_even_a_held_share(self):
        receipt = collect(_runout(_stats(cal=(360, 138)), cal="CAL_FAIL", w8="VOID"))
        self.assertEqual(receipt["branch"], "CAL_FAIL+VOID")
        joined = " ".join(receipt["actions"])
        self.assertIn("VOID", joined)
        self.assertIn("diagnose", joined)

    def test_no_events_branch(self):
        receipt = collect(_runout(_stats(fr_term=(30, 19)), w8="NO_EVENTS"))
        self.assertEqual(receipt["branch"], "CAL_OK+NO_EVENTS")

    def test_smoke_output_not_verdictable(self):
        receipt = collect(_runout(_stats(n=8), cal="CAL_OK", w8="HELD"))
        self.assertEqual(receipt["branch"], "SMOKE_NOT_VERDICTABLE")

    def test_band_edge_is_held(self):
        # share 0.788 -> dev 0.04576 <= 0.05 (inside), 0.78 -> dev 0.05376 (outside)
        held = collect(_runout(_stats(fr_term=(394, 106))))
        self.assertEqual(held["branch"], "CAL_OK+HELD")
        outside = collect(_runout(_stats(fr_term=(390, 110)), w8="REFUTED"))
        self.assertEqual(outside["branch"], "CAL_OK+REFUTED")


class CrossCheckTests(unittest.TestCase):
    def test_disagreement_raises(self):
        text = _runout(_stats(), cal="CAL_OK", w8="REFUTED")  # stats say HELD
        with self.assertRaises(ValueError):
            collect(text)

    def test_disagreement_forced_is_labelled(self):
        text = _runout(_stats(), cal="CAL_OK", w8="REFUTED")
        receipt = collect(text, force=True)
        self.assertEqual(receipt["cross_check"], "FORCED-DISAGREEMENT")


class DescriptiveTests(unittest.TestCase):
    def test_wilson_brackets_share_and_haz95_distance(self):
        receipt = collect(_runout(_stats(fr_term=(384, 77))))
        d = receipt["descriptive"]
        share = d["fresh_terminal_share"]
        lo, hi = d["fresh_w8_wilson95"]
        self.assertTrue(lo < share < hi)
        self.assertLess(hi - lo, 0.10)
        self.assertAlmostEqual(d["haz95_arm_distance"],
                               abs(share - 0.81585), places=10)

    def test_fresh_mid_crosschecks_against_both_receipts(self):
        receipt = collect(_runout(_stats(fr_mid=(368, 132))))
        d = receipt["descriptive"]
        # 368/500 = 0.736: near the VH held-out receipt, ~0.02 from DW9's
        self.assertAlmostEqual(d["fresh_mid_w4_dev_vs_vh_receipt"], 0.0019, places=4)
        self.assertAlmostEqual(d["fresh_mid_w4_dev_vs_dw9_receipt"], 0.020, places=3)

    def test_recompute_pure_function(self):
        self.assertEqual(recompute(_stats())["branch"], "CAL_OK+HELD")
        self.assertEqual(recompute(_stats(cal=(1, 2)))["branch"], "CAL_FAIL+VOID")


if __name__ == "__main__":
    unittest.main()
