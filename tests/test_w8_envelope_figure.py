"""Pins for the tick-133 envelope figure (designs/assets/012-exactness-envelope.svg).

Measure-then-pin, same discipline as the rest of the w8 line:
- the figure is a pure function of the tick-132 evidence receipt, so the
  committed asset must be byte-identical to a fresh regeneration;
- the asset sha256 is pinned outright (a changed receipt or a layout edit
  must re-pin deliberately, not drift silently);
- the semantic anchors (worst point, class max, consumer floor) must be the
  ones measured in the receipt, not hand-typed decoration.
"""

import hashlib
import json
import re
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ASSET = REPO / "designs/assets/012-exactness-envelope.svg"
EVIDENCE = REPO / "evidence/2026-10-14-w8-exactness-envelope/envelope-full.json"

PINNED_SHA256 = "f37b264c5c44ed4c5985d13d8902ffaab00d81bdb279322a6a9bad4a6ffc6d19"


def _render_to(path: Path) -> None:
    import importlib.util

    spec = importlib.util.spec_from_file_location("w8_envelope_figure", REPO / "tools/w8_envelope_figure.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    path.write_text(mod.render(json.loads(EVIDENCE.read_text())))


class EnvelopeFigurePins(unittest.TestCase):
    def test_asset_sha256_pinned(self):
        got = hashlib.sha256(ASSET.read_bytes()).hexdigest()
        self.assertEqual(got, PINNED_SHA256, f"asset drifted: {got} != {PINNED_SHA256} (re-pin deliberately)")

    def test_regeneration_byte_identical(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td) / "regen.svg"
            _render_to(tmp)
            self.assertEqual(tmp.read_bytes(), ASSET.read_bytes(), "figure is not a pure function of the receipt")

    def test_semantic_anchors_match_receipt(self):
        ev = json.loads(EVIDENCE.read_text())
        worst = ev["per_helper"]["binom_cdf"]["complement"]
        k, n, p = worst["argmax_k_n_p"]
        svg = ASSET.read_text()
        # worst-point annotation derived from the receipt
        self.assertIn(f"worst {worst['max_rel']:.2e} @ cdf({k},{n},{p})", svg)
        self.assertIn(f"mass {worst['mass_at_argmax']:.2e}", svg)
        # grid honesty counters from the receipt
        self.assertIn(f"{ev['points_compared']} compared", svg)
        self.assertIn(f"{ev['points_below_floor']} below the 1e-290 oracle floor", svg)
        # frozen reference levels
        for anchor in ("8.3e-3", "1e-10", "7.4e-11", "binom_cdf complement", "binom_sf_ge complement"):
            self.assertIn(anchor, svg, f"missing anchor {anchor!r}")

    def test_geometry_sane(self):
        svg = ASSET.read_text()
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


if __name__ == "__main__":
    unittest.main()
