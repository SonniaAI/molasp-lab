"""Tick-73 pins: window-indexed MARGINAL pricing (designs/011).

Every number here is either a RECEIPT transcribed verbatim (VH basis
fit, window census points, frozen-class persistence) or a chain
arithmetic identity the receipt already validated (w4 prediction ==
share_pred 0.74135 with held-out dev 0.0035 / fresh dev 0.0254).
The w2/w3 checks are NEW gates the fit never saw: the chain was
validated only at its terminal (VH2); here its mid-window values are
compared against the DW10 snapshot receipts.  Static computation
only — no cluster job (tick-37 rule)."""

import math
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

if REPO not in sys.path:
    sys.path.insert(0, REPO)
SIB_AND = os.path.join(REPO, "evidence",
                       "2026-10-06-body-conjunction-builds")
if SIB_AND not in sys.path:
    sys.path.insert(0, SIB_AND)

from tiles_and import BUILD1                   # noqa: E402
from molasp import offchannel as oc            # noqa: E402


class TestBasisVerbatim(unittest.TestCase):
    """VH_BASIS and WINDOW_MEASURED ARE the receipts — verbatim."""

    def test_hazards_verbatim(self):
        self.assertEqual(oc.VH_BASIS["haz_d2t"][2],
                         5.348122115210481e-09)
        self.assertEqual(oc.VH_BASIS["haz_d2t"][4],
                         1.0321999558539198e-09)
        self.assertEqual(oc.VH_BASIS["haz_l2"][2],
                         1.5280356180070675e-07)
        self.assertEqual(oc.VH_BASIS["haz_l2"][4],
                         4.359141414272266e-08)
        # the VH1 ratchet collapse, recomputed from the quoted
        # hazards: ~76x from phase 1 to phase 2
        ratio = (oc.VH_BASIS["haz_d2t"][1]
                 / oc.VH_BASIS["haz_d2t"][2])
        self.assertTrue(70 < ratio < 80, ratio)

    def test_pooled_fit_and_receipts(self):
        self.assertEqual(oc.VH_BASIS["lam"],
                         0.00013237187264826007)
        self.assertAlmostEqual(sum(oc.VH_BASIS["p"].values()),
                               1.0, places=12)
        self.assertEqual(oc.VH_BASIS["share_pred_w4_receipt"],
                         0.7413549690850645)
        self.assertEqual(oc.VH_BASIS["homo_pi_receipt"],
                         0.7123954307622163)
        # the snapshot init IS the fit-range 1/4-window census
        self.assertEqual(oc.VH_BASIS["v0"],
                         [0.0, 0.448, 0.488, 0.064])

    def test_window_census_recomputes(self):
        for w, (d2t, l2, share) in {
            1: (232, 229, 0.5032537960954447),
            2: (318, 174, 0.6463414634146342),
            3: (348, 146, 0.7044534412955465),
            4: (367, 131, 0.7369477911646586),
        }.items():
            m = oc.WINDOW_MEASURED[w]
            self.assertEqual((m["d2t"], m["l2"]), (d2t, l2))
            self.assertAlmostEqual(
                m["d2t"] / float(m["d2t"] + m["l2"]),
                share, places=12)


class TestExpmClosedForm(unittest.TestCase):
    """Tick-70 lesson: validate matrix-exponential code against a
    closed form BEFORE trusting its asserts — the row-sum assert
    alone passed a buggy variant at small m."""

    def test_two_state_closed_form(self):
        a, b = 0.7, 1.9
        Q = [[-a, a], [b, -b]]
        E = oc._expm4(Q, 1.3)
        decay = math.exp(-(a + b) * 1.3)
        p01 = a / (a + b) * (1.0 - decay)
        p10 = b / (a + b) * (1.0 - decay)
        p00 = b / (a + b) + a / (a + b) * decay
        p11 = a / (a + b) + b / (a + b) * decay
        self.assertAlmostEqual(E[0][1], p01, places=10)
        self.assertAlmostEqual(E[1][0], p10, places=10)
        self.assertAlmostEqual(E[0][0], p00, places=10)
        self.assertAlmostEqual(E[1][1], p11, places=10)

    def test_row_sums_on_the_real_chain(self):
        E = oc._expm4(oc._build_Q(5.348122115210481e-09,
                                  1.5280356180070675e-07),
                      400.0 * math.exp(9.5))
        for row in E:
            self.assertAlmostEqual(sum(row), 1.0, places=9)


class TestChainPredictions(unittest.TestCase):
    """P1: the chain reproduces the receipt's w4 prediction exactly
    (same fit, same construction — an implementation-identity check).
    P2: mid-window chain values against the DW10 snapshot receipts
    (never gated during the fit).  P3: w8 extrapolation band."""

    def test_p1_w4_receipt_identity(self):
        self.assertAlmostEqual(
            oc._vh_share(4),
            oc.VH_BASIS["share_pred_w4_receipt"], delta=5e-4)

    def test_p2_w2_w3_against_snapshots(self):
        for w, share in {2: 0.6463414634146342,
                         3: 0.7044534412955465}.items():
            self.assertAlmostEqual(oc._vh_share(w), share, delta=0.05)

    def test_p3_w8_extrapolation_band(self):
        # band brackets the point extrapolation AND the Poisson-95
        # hazard sensitivity arm (designs/011 P3; not a guess — both
        # are deterministic arithmetic from the receipt hazards)
        s8 = oc._vh_share(8)
        self.assertTrue(0.81 <= s8 <= 0.85, s8)
        wp = oc.marginal_window_pricing((8,))
        self.assertAlmostEqual(wp["windows"]["8"]["hazard95_share"],
                               0.8159, delta=2e-3)
        # the ratchet is monotone-by-construction late (D2T hazard
        # ~0, L2 keeps detaching): w8 must not fall below w4
        self.assertGreaterEqual(s8, oc._vh_share(4) - 1e-9)

    def test_chain_monotone_w1_to_w4(self):
        shares = [oc._vh_share(w) for w in (1, 2, 3, 4)]
        self.assertEqual(shares, sorted(shares))


class TestWindowPricingAPI(unittest.TestCase):

    def test_curve_and_tiers(self):
        wp = oc.marginal_window_pricing()
        wins = wp["windows"]
        self.assertEqual(sorted(int(k) for k in wins),
                         [1, 2, 3, 4, 8])
        self.assertAlmostEqual(wins["1"]["measured_share"],
                               0.5033, delta=5e-4)
        self.assertEqual(wins["1"]["tier"], "contested")
        self.assertEqual(wins["4"]["tier"], "ratchet-tilting")
        self.assertEqual(
            wins["8"]["chain_kind"],
            "EXTRAPOLATED (phase-4 hazards held)")
        self.assertEqual(wp["frozen_class"]["persist"], 0.826)
        self.assertEqual(wp["frozen_class"]["window"], 4)

    def test_tier_thresholds(self):
        self.assertEqual(oc.window_tier(0.50), "contested")
        self.assertEqual(oc.window_tier(0.55), "ratchet-tilting")
        self.assertEqual(oc.window_tier(0.60), "ratchet-tilting")
        self.assertEqual(oc.window_tier(0.75), "ratchet-tilted")
        self.assertEqual(oc.window_tier(0.80), "ratchet-tilted")

    def test_severity_carries_window_block_at_marginal_only(self):
        sev = oc.contention_severity(BUILD1, dg=2.0)
        self.assertEqual(sev["regime"], "marginal")
        self.assertIn("window_pricing", sev)
        for other in (0.5, 4.0, 7.0):
            self.assertNotIn(
                "window_pricing",
                oc.contention_severity(BUILD1, dg=other))

    def test_d4_report_line(self):
        rep = oc.check_d4(BUILD1, dg=2.0)
        joined = "\n".join(oc.d4_report_lines(rep))
        self.assertIn("window pricing (MARGINAL)", joined)
        self.assertIn("0.826", joined)


if __name__ == "__main__":
    unittest.main()
