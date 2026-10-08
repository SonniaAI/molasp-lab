"""Pins for the designs/011 window-curve figure (tools/window_curve_svg.py).

The figure must carry the exact measured censuses and chain numbers the
pricing functions emit, keep the extrapolated w8 arm visually distinct,
and render deterministically.  Every value asserted here is derived
from marginal_window_pricing(), never re-typed independently.
"""

import unittest

from molasp.offchannel import marginal_window_pricing
from tools.window_curve_svg import render


class WindowCurveSvgTests(unittest.TestCase):
    def setUp(self):
        self.svg = render()

    def test_measured_points_with_censuses_and_shares(self):
        for census in ("232:229", "318:174", "348:146", "367:131"):
            self.assertIn(census, self.svg)
        curve = marginal_window_pricing()
        for w in ("1", "2", "3", "4"):
            share = curve["windows"][w]["measured_share"]
            self.assertIn(f"{share:.4f}", self.svg)

    def test_w8_pending_with_hazard_bracket(self):
        curve = marginal_window_pricing()
        w8 = curve["windows"]["8"]
        self.assertIn(f"{w8['chain_share']:.4f}", self.svg)
        self.assertIn(f"{w8['hazard95_share']:.4f}", self.svg)
        self.assertIn("VERDICT PENDING", self.svg)
        self.assertIn('class="hazard95"', self.svg)
        self.assertIn('class="w8-pending"', self.svg)

    def test_reference_lines_pinned_to_curve(self):
        curve = marginal_window_pricing()
        self.assertIn(f"{curve['homo_stationary']:.4f}", self.svg)
        self.assertIn(f"{curve['frozen_class']['persist']:.3f}", self.svg)
        self.assertIn("window-immune", self.svg)

    def test_tier_bands_and_extrapolation_style(self):
        for tier in ("contested", "ratchet-tilting", "ratchet-tilted"):
            self.assertIn(tier, self.svg)
        self.assertIn('class="chain-fit"', self.svg)
        self.assertIn('class="chain-extrap"', self.svg)
        self.assertIn('stroke-dasharray="7 5"', self.svg)

    def test_deterministic_render(self):
        self.assertEqual(render(), render())


if __name__ == "__main__":
    unittest.main()
