"""Pins for the receipt-gated blog renderer (tools/render_w8_post.py).

The renderer is the last link of the executable pre-registration chain
(run.out -> collect_w8.py -> receipt -> THIS -> blog post), committed
BEFORE the w8 data exists.  Receipts here are built through the REAL
collector on synthetic run.out shapes (same builder style as
tests/test_collect_w8.py), so the renderer is pinned against exactly
what collection day emits.  No milestone, no post — ever.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

from tools.collect_w8 import collect, wilson
from tools.render_w8_post import REQUEST_DEFAULT, render


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
    lines = ["[cluster preamble] node spark-4a06", ""]
    lines.append(json.dumps(stats))
    lines.append(json.dumps({"CAL": cal, "W8": w8}))
    lines.append("VERDICTS " + json.dumps({"CAL": cal, "W8": w8}, sort_keys=True))
    return "\n".join(lines) + "\n"


def _receipt(cal_label="CAL_OK", w8_label="HELD", **stats_kw):
    return collect(_runout(_stats(**stats_kw), cal=cal_label, w8=w8_label))


class HeldTests(unittest.TestCase):
    def test_held_receipt_renders_milestone_post(self):
        out = render(_receipt(), day="2026-10-09")
        self.assertEqual(out["filename"],
                         "2026-10-09-window-pricing-w8-held.md")
        t = out["text"]
        self.assertTrue(t.startswith("# The window curve survives w8\n"))
        # every number quoted verbatim from the receipt
        r = _receipt()
        d = r["descriptive"]
        self.assertIn("%d:%d:%d" % (d["fresh_terminal_census"]["D2T"],
                                    d["fresh_terminal_census"]["L2"],
                                    d["fresh_terminal_census"]["other"]), t)
        self.assertIn("%.4f" % d["fresh_terminal_share"], t)
        self.assertIn("%.4f" % d["dev_vs_pred_w8"], t)
        self.assertIn("[%.5f, %.5f]" % tuple(d["fresh_w8_wilson95"]), t)
        self.assertIn("±0.05", t)
        self.assertIn(REQUEST_DEFAULT, t)
        # 500 terminals per range vs the pair subset actually share-able
        self.assertIn("%d fresh" % r["n_per_range"], t)
        self.assertIn("%d pair terminals" % (d["fresh_terminal_census"]["D2T"]
                                              + d["fresh_terminal_census"]["L2"]), t)
        # frozen anchors quoted as prose constants
        self.assertIn("0.834", t)
        self.assertIn("0.816", t)
        # cross-check stated, branch stated
        self.assertIn("cross_check\nok, branch CAL_OK+HELD", t)
        # arm sentence is side-conditional, never the old unconditional claim
        self.assertNotIn("lands on the\nchain side", t)

    def test_held_below_the_arm_is_sided_correctly(self):
        # share 0.7905 (387:103) is HELD (dev 0.0433) yet BELOW the
        # hazard-95 arm 0.81585 -> must say "below", never "above"
        rec = _receipt(fr_term=(387, 103))
        self.assertEqual(rec["branch"], "CAL_OK+HELD")
        t = render(rec, day="2026-10-09")["text"]
        self.assertIn("lands below the bracket", t)
        self.assertNotIn("lands above the bracket", t)

    def test_held_above_the_arm_says_above(self):
        t = render(_receipt(fr_term=(400, 61)), day="2026-10-09")["text"]
        self.assertIn("lands above the bracket", t)


class RefutedTests(unittest.TestCase):
    def test_refuted_receipt_renders_demolition_post(self):
        rec = _receipt(fr_term=(370, 105), w8_label="REFUTED")   # share 0.7789 -> REFUTED edge side
        self.assertEqual(rec["branch"], "CAL_OK+REFUTED")
        out = render(rec, day="2026-10-09")
        self.assertEqual(out["filename"],
                         "2026-10-09-window-pricing-w8-refuted.md")
        t = out["text"]
        self.assertTrue(t.startswith("# The window curve breaks at w8\n"))
        self.assertIn("retracted", t)
        self.assertIn("quarantined", t)
        self.assertIn("the demolition takes the\nprediction, not the measurements", t)
        self.assertIn("outside the band, the prediction dies regardless", t)


class RefusalTests(unittest.TestCase):
    def test_void_receipt_refused(self):
        rec = _receipt(cal=(360, 138), cal_label="CAL_FAIL", w8_label="VOID")  # CAL_FAIL -> VOID
        self.assertEqual(rec["branch"], "CAL_FAIL+VOID")
        with self.assertRaises(ValueError):
            render(rec, day="2026-10-09")

    def test_no_events_receipt_refused(self):
        rec = _receipt(fr_term=(30, 10), w8_label="NO_EVENTS")
        self.assertEqual(rec["branch"], "CAL_OK+NO_EVENTS")
        with self.assertRaises(ValueError):
            render(rec, day="2026-10-09")

    def test_smoke_receipt_refused(self):
        rec = _receipt(n=5)
        self.assertEqual(rec["branch"], "SMOKE_NOT_VERDICTABLE")
        with self.assertRaises(ValueError):
            render(rec, day="2026-10-09")

    def test_forced_disagreement_receipt_refused(self):
        rec = _receipt()
        rec["cross_check"] = "FORCED-DISAGREMENT"
        with self.assertRaises(ValueError):
            render(rec, day="2026-10-09")

    def test_missing_descriptive_field_refused(self):
        rec = _receipt()
        del rec["descriptive"]["fresh_w8_wilson95"]
        with self.assertRaises(ValueError):
            render(rec, day="2026-10-09")

    def test_missing_receipt_branch_refused(self):
        with self.assertRaises(ValueError):
            render({"branch": None, "cross_check": "ok"}, day="2026-10-09")


class DeterminismTests(unittest.TestCase):
    def test_same_receipt_same_bytes(self):
        rec = _receipt()
        a = render(rec, day="2026-10-09")
        b = render(json.loads(json.dumps(rec)), day="2026-10-09")
        self.assertEqual(a["text"], b["text"])

    def test_numbers_flow_from_the_receipt(self):
        a = render(_receipt(), day="2026-10-09")["text"]
        b = render(_receipt(fr_term=(396, 65)), day="2026-10-09")["text"]
        self.assertNotEqual(a, b)

    def test_no_template_residue(self):
        cases = ((384, 77, "HELD"), (370, 105, "REFUTED"), (396, 65, "HELD"))
        for d2t, l2, label in cases:
            t = render(_receipt(fr_term=(d2t, l2), w8_label=label),
                       day="2026-10-09")["text"]
            for bad in ("None", "nan", "{", "}"):
                self.assertNotIn(bad, t)


class MainTests(unittest.TestCase):
    def test_main_refusal_exit_code(self):
        rec = _receipt()
        rec["branch"] = "CAL_FAIL+VOID"
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "verdict.json")
            with open(p, "w") as fh:
                json.dump(rec, fh)
            r = subprocess.run(
                [sys.executable, "tools/render_w8_post.py", p,
                 "--date", "2026-10-09", "--out", os.path.join(td, "x.md")],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 2)
            self.assertIn("RENDER REFUSED", r.stderr)

    def test_main_writes_the_post(self):
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "verdict.json")
            with open(p, "w") as fh:
                json.dump(_receipt(), fh)
            outp = os.path.join(td, "post.md")
            r = subprocess.run(
                [sys.executable, "tools/render_w8_post.py", p,
                 "--date", "2026-10-09", "--out", outp],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            with open(outp) as fh:
                self.assertIn("# The window curve survives w8", fh.read())


if __name__ == "__main__":
    unittest.main()
