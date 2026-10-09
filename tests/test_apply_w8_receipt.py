"""Pins for the one-command collection application (tools/apply_w8_receipt.py).

End-to-end through the REAL collector, REAL figure renderer and REAL blog
renderer into a throwaway repo root: the seam the receipt crosses on
collection day is pinned as one chain, not three.  Refusals are pinned
hard — a non-milestone or forced receipt must never autowrite anything.
"""

import json
import tempfile
import unittest
from pathlib import Path

from tools.apply_w8_receipt import apply
from tools.collect_w8 import collect, wilson


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
    lines.append("VERDICTS " + json.dumps({"CAL": cal, "W8": w8}, sort_keys=True))
    return "\n".join(lines) + "\n"


def _receipt(cal_label="CAL_OK", w8_label="HELD", **stats_kw):
    return collect(_runout(_stats(**stats_kw), cal=cal_label, w8=w8_label))


def _root():
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    rl = root / "research-log"
    rl.mkdir(parents=True)
    (rl / "2026-10-08-w8-hazardhold.md").write_text(
        "# w8 hazard-hold pre-registration\n\n(interpretation map body)\n",
        encoding="utf-8")
    return tmp, root


class HeldTests(unittest.TestCase):
    def test_applies_figure_blog_and_note(self):
        r = _receipt()
        tmp, root = _root()
        with tmp:
            out = apply(r, root, date="2026-10-09")
            self.assertEqual(out["branch"], "CAL_OK+HELD")
            self.assertTrue(out["note_appended"])
            fig = (root / "designs/assets/011-window-curve.svg").read_text()
            self.assertIn('class="w8-measured"', fig)
            self.assertIn('class="w8-wilson95"', fig)
            self.assertIn(">384:77<", fig)            # census label, verbatim
            self.assertNotIn("VERDICT PENDING", fig)
            self.assertIn("w8 MEASURED", fig)
            blog = (root / "blog/2026-10-09-window-pricing-w8-held.md").read_text()
            self.assertIn("held", blog.lower())
            note = (root / "research-log/2026-10-08-w8-hazardhold.md").read_text()
            self.assertIn(
                "## Collection (2026-10-09, SON-4885) — CAL_OK+HELD", note)
            self.assertIn("(interpretation map body)", note)  # seed preserved
            # every quoted number verbatim from the receipt
            self.assertIn("%.5f" % r["descriptive"]["fresh_terminal_share"], note)
            self.assertIn("%.5f" % r["descriptive"]["dev_vs_pred_w8"], note)
            self.assertIn("D2T 384 / L2 77 / other 39", note)
            self.assertIn("stands on a measured receipt", note)
            self.assertIn("blog/2026-10-09-window-pricing-w8-held.md", note)

    def test_note_append_is_idempotent(self):
        r = _receipt()
        tmp, root = _root()
        with tmp:
            apply(r, root, date="2026-10-09")
            note1 = (root / "research-log/2026-10-08-w8-hazardhold.md").read_text()
            out2 = apply(r, root, date="2026-10-09")
            note2 = (root / "research-log/2026-10-08-w8-hazardhold.md").read_text()
            self.assertFalse(out2["note_appended"])
            self.assertEqual(note1, note2)


class RefutedTests(unittest.TestCase):
    def test_quarantines_figure_and_renders_demolition(self):
        r = _receipt(w8_label="REFUTED", fr_term=(390, 300))
        tmp, root = _root()
        with tmp:
            out = apply(r, root, date="2026-10-09")
            self.assertEqual(out["branch"], "CAL_OK+REFUTED")
            fig = (root / "designs/assets/011-window-curve.svg").read_text()
            self.assertNotIn("chain-extrap", fig)
            self.assertNotIn("hazard95", fig)
            self.assertIn("QUARANTINED", fig)
            self.assertIn("measured", fig)            # w1-w4 receipts unchanged
            blog = (root / "blog/2026-10-09-window-pricing-w8-refuted.md").read_text()
            self.assertIn("refut", blog.lower())
            note = (root / "research-log/2026-10-08-w8-hazardhold.md").read_text()
            self.assertIn("falsified at w8", note)
            self.assertIn("%.5f" % r["descriptive"]["fresh_terminal_share"], note)


class RefusalTests(unittest.TestCase):
    def _assert_no_writes(self, root):
        self.assertFalse((root / "designs").exists())
        self.assertFalse((root / "blog").exists())
        note = (root / "research-log/2026-10-08-w8-hazardhold.md").read_text()
        self.assertNotIn("## Collection", note)

    def test_void_receipt_refuses(self):
        r = _receipt(cal_label="CAL_FAIL", w8_label="VOID", cal=(366, 131))
        tmp, root = _root()
        with tmp:
            with self.assertRaises(ValueError) as cm:
                apply(r, root, date="2026-10-09")
            self.assertIn("refusing branch 'CAL_FAIL+VOID'", str(cm.exception))
            self.assertIn("VOID: instrument drift", str(cm.exception))
            self._assert_no_writes(root)

    def test_no_events_receipt_refuses(self):
        r = _receipt(w8_label="NO_EVENTS", fr_term=(30, 15))
        tmp, root = _root()
        with tmp:
            with self.assertRaises(ValueError) as cm:
                apply(r, root, date="2026-10-09")
            self.assertIn("NO_EVENTS", str(cm.exception))
            self._assert_no_writes(root)

    def test_smoke_receipt_refuses(self):
        r = _receipt(w8_label="HELD", n=100)  # n != 500 -> SMOKE_NOT_VERDICTABLE
        self.assertEqual(r["branch"], "SMOKE_NOT_VERDICTABLE")
        tmp, root = _root()
        with tmp:
            with self.assertRaises(ValueError) as cm:
                apply(r, root, date="2026-10-09")
            self.assertIn("SMOKE_NOT_VERDICTABLE", str(cm.exception))
            self._assert_no_writes(root)

    def test_forced_disagreement_receipt_refuses(self):
        r = _receipt()
        r["cross_check"] = "FORCED-DISAGREEMENT"
        tmp, root = _root()
        with tmp:
            with self.assertRaises(ValueError) as cm:
                apply(r, root, date="2026-10-09")
            self.assertIn("forced receipt can never autowrite", str(cm.exception))
            self._assert_no_writes(root)


class PendingDefaultTests(unittest.TestCase):
    def test_pending_render_still_byte_identical_to_committed_figure(self):
        from tools.window_curve_svg import render
        committed = (Path(__file__).resolve().parents[1]
                     / "designs/assets/011-window-curve.svg").read_text()
        self.assertEqual(render(), committed)


if __name__ == "__main__":
    unittest.main()
