"""Pins for the w8 envelope figures (012 = tick-132 receipt, 013 = tick-134
geometric-tail-bound receipt).

Measure-then-pin, same discipline as the rest of the w8 line:
- each figure is a pure function of its evidence receipt, so the committed
  asset must be byte-identical to a fresh regeneration;
- each asset sha256 is pinned outright (a changed receipt or a layout edit
  must re-pin deliberately, not drift silently);
- the semantic anchors (worst point, direct-class max, captions) must be the
  ones measured in the receipt, not hand-typed decoration;
- every text box sits inside the canvas and overlaps no other label (tick 133
  catch 10a, promoted from one-off audit to durable pin).
"""

import hashlib
import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ASSET012 = REPO / "designs/assets/012-exactness-envelope.svg"
EVIDENCE012 = REPO / "evidence/2026-10-14-w8-exactness-envelope/envelope-full.json"
PINNED_SHA256_012 = "f37b264c5c44ed4c5985d13d8902ffaab00d81bdb279322a6a9bad4a6ffc6d19"

ASSET013 = REPO / "designs/assets/013-exactness-envelope-geometric.svg"
EVIDENCE013 = REPO / "evidence/2026-10-14-w8-geometric-tail-bound/envelope-full.json"
PINNED_SHA256_013 = "e5b30ee3861833cd7d9f6c3dbdbdce279a0f6281e786d2faa10e9e1c38c60263"

TRANSITION_EDGE_DEC = -5


def _module():
    spec = importlib.util.spec_from_file_location("w8_envelope_figure", REPO / "tools/w8_envelope_figure.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _render_to(path: Path, evidence: Path) -> None:
    mod = _module()
    path.write_text(mod.render(json.loads(evidence.read_text()), evidence.parent.name))


def _has_band(evidence: Path) -> bool:
    ev = json.loads(evidence.read_text())
    pts = []
    for helper in ev["per_helper"].values():
        pts += [int(k) for k in helper["complement"]["decade_buckets"]]
    return any(d < TRANSITION_EDGE_DEC for d in pts)


class EnvelopeFigure012Pins(unittest.TestCase):
    """tick-132 receipt: transition band present, worst point inside it."""

    def test_asset_sha256_pinned(self):
        got = hashlib.sha256(ASSET012.read_bytes()).hexdigest()
        self.assertEqual(got, PINNED_SHA256_012, f"asset drifted: {got} != {PINNED_SHA256_012} (re-pin deliberately)")

    def test_regeneration_byte_identical(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td) / "regen.svg"
            _render_to(tmp, EVIDENCE012)
            self.assertEqual(tmp.read_bytes(), ASSET012.read_bytes(), "figure is not a pure function of the receipt")

    def test_semantic_anchors_match_receipt(self):
        ev = json.loads(EVIDENCE012.read_text())
        worst = ev["per_helper"]["binom_cdf"]["complement"]
        k, n, p = worst["argmax_k_n_p"]
        svg = ASSET012.read_text()
        # worst-point annotation derived from the receipt
        self.assertIn(f"worst {worst['max_rel']:.2e} @ cdf({k},{n},{p})", svg)
        self.assertIn(f"mass {worst['mass_at_argmax']:.2e}", svg)
        # grid honesty counters from the receipt
        self.assertIn(f"{ev['points_compared']} compared", svg)
        self.assertIn(f"{ev['points_below_floor']} below the {ev['oracle_floor']:.0e} oracle floor", svg)
        # frozen reference levels
        for anchor in ("8.3e-3", "1e-10", "7.4e-11", "binom_cdf complement", "binom_sf_ge complement"):
            self.assertIn(anchor, svg, f"missing anchor {anchor!r}")

    def test_band_caption_matches_receipt(self):
        svg = ASSET012.read_text()
        self.assertTrue(_has_band(EVIDENCE012), "receipt lost its below-edge buckets; re-derive the caption story")
        self.assertIn("transition band: guard bound ≥ 1e-5", svg)
        self.assertNotIn("transition band eliminated", svg)

    def test_geometry_sane(self):
        svg = ASSET012.read_text()
        self.assertNotIn("nan", svg)
        self.assertNotIn("inf", svg)
        W, H = 960.0, 560.0
        L, R, T, B = 96.0, 250.0, 76.0, 74.0
        PW, PH = W - L - R, H - T - B
        pts = re.findall(r'<circle cx="([\d.]+)" cy="([\d.]+)"', svg)
        self.assertEqual(len(pts), 15, f"expected 15 bucket points, got {len(pts)}")
        for cx, cy in pts:
            x, y = float(cx), float(cy)
            self.assertLessEqual(L - 0.5, x)
            self.assertLessEqual(x, L + PW + 0.5, f"point x outside frame: {x}")
            self.assertLessEqual(T - 0.5, y)
            self.assertLessEqual(y, T + PH + 0.5, f"point y outside frame: {y}")

    def test_text_audit(self):
        mod = _module()
        self.assertEqual(mod.audit_text_bounds(ASSET012.read_text()), [])


class EnvelopeFigure013Pins(unittest.TestCase):
    """tick-134 receipt: geometric tail-ratio bound eliminated the band.

    The 013 figure re-renders the same chart from the re-measured envelope;
    every moved annotation (worst point at cdf(494,500,0.999), lifted prose,
    eliminated-band caption, direct-path label) is derived from the receipt.
    """

    def test_asset_sha256_pinned(self):
        got = hashlib.sha256(ASSET013.read_bytes()).hexdigest()
        self.assertEqual(got, PINNED_SHA256_013, f"asset drifted: {got} != {PINNED_SHA256_013} (re-pin deliberately)")

    def test_regeneration_byte_identical(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td) / "regen.svg"
            _render_to(tmp, EVIDENCE013)
            self.assertEqual(tmp.read_bytes(), ASSET013.read_bytes(), "figure is not a pure function of the receipt")

    def test_semantic_anchors_match_receipt(self):
        ev = json.loads(EVIDENCE013.read_text())
        worst = ev["per_helper"]["binom_cdf"]["complement"]
        k, n, p = worst["argmax_k_n_p"]
        svg = ASSET013.read_text()
        self.assertIn(f"worst {worst['max_rel']:.2e} @ cdf({k},{n},{p})", svg)
        self.assertIn(f"mass {worst['mass_at_argmax']:.2e}", svg)
        self.assertIn(f"{ev['points_compared']} compared", svg)
        self.assertIn(f"{ev['points_below_floor']} below the {ev['oracle_floor']:.0e} oracle floor", svg)
        self.assertIn(f"evidence {EVIDENCE013.parent.name}", svg)
        for anchor in ("8.3e-3", "1e-10", "binom_cdf complement", "binom_sf_ge complement"):
            self.assertIn(anchor, svg, f"missing anchor {anchor!r}")

    def test_direct_label_derived_from_receipt(self):
        ev = json.loads(EVIDENCE013.read_text())
        mod = _module()
        direct_max = max(
            h[b]["max_rel"] for h in ev["per_helper"].values() for b in ("short_side", "deep_direct")
        )
        self.assertEqual(f"{mod.ceil_2sig(direct_max):.1e}", "7.4e-11")
        self.assertIn("direct paths ≤ 7.4e-11 domain-wide", ASSET013.read_text())

    def test_band_eliminated_caption_matches_receipt(self):
        svg = ASSET013.read_text()
        # the caption's claim, checked against the receipt itself
        self.assertFalse(_has_band(EVIDENCE013), "receipt still has below-edge buckets; caption would be wrong")
        self.assertIn(
            "transition band eliminated (geometric tail-ratio bound): no bucket below decade −5",
            svg,
        )
        self.assertNotIn("transition band: guard bound", svg)
        # no amber band fill in the eliminated world
        self.assertNotIn("#fff6e5", svg)

    def test_geometry_sane(self):
        svg = ASSET013.read_text()
        self.assertNotIn("nan", svg)
        self.assertNotIn("inf", svg)
        W, H = 960.0, 560.0
        L, R, T, B = 96.0, 250.0, 76.0, 74.0
        PW, PH = W - L - R, H - T - B
        pts = re.findall(r'<circle cx="([\d.]+)" cy="([\d.]+)"', svg)
        # 6 cdf buckets + 4 sf buckets, none below decade -5
        self.assertEqual(len(pts), 10, f"expected 10 bucket points, got {len(pts)}")
        for cx, cy in pts:
            x, y = float(cx), float(cy)
            self.assertLessEqual(L - 0.5, x)
            self.assertLessEqual(x, L + PW + 0.5, f"point x outside frame: {x}")
            self.assertLessEqual(T - 0.5, y)
            self.assertLessEqual(y, T + PH + 0.5, f"point y outside frame: {y}")

    def test_text_audit(self):
        mod = _module()
        self.assertEqual(mod.audit_text_bounds(ASSET013.read_text()), [])


if __name__ == "__main__":
    unittest.main()
