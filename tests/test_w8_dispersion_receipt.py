"""Pins for tools/w8_dispersion_receipt.py (tick 93 — measured 2026-10-09,
BEFORE the w8 datum exists). Every constant below is pinned from the
tool's own output (measure-then-pin); the receipts use the canonical
tick-88/91 census counts so the pins cross-check the planner lineage."""
import math
import sys
import unittest
from io import StringIO
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.w8_dispersion_receipt import (
    DEFAULT_ALPHA,
    exact_two_sided_p,
    logpmf,
    main,
    parse_arm,
    receipt,
    render,
)


class DispersionReceiptPins(unittest.TestCase):
    def test_identical_arms_supported_at_p_one(self):
        rep = receipt([(417, 500), (417, 500), (417, 500)], DEFAULT_ALPHA)
        self.assertEqual(rep["arms"], 3)
        self.assertEqual(rep["pooled_phat"], 0.834)
        for r in rep["rows"]:
            self.assertEqual(r["phat"], 0.834)
            self.assertEqual(r["loo_pooled_phat"], 0.834)
            # identical arms: p-value is the whole mass, 1.0 up to float summation
            self.assertAlmostEqual(r["exact_two_sided_p"], 1.0, delta=1e-12)
        self.assertAlmostEqual(rep["min_exact_p"], 1.0, delta=1e-12)
        self.assertEqual(rep["verdict"], "POOLING_SUPPORTED")

    def test_wild_arm_contested_with_pinned_tail(self):
        rep = receipt([(417, 500), (417, 500), (250, 500)], DEFAULT_ALPHA)
        self.assertAlmostEqual(rep["pooled_phat"], 0.722667, places=6)
        # wild arm tested against the leave-one-out pool of the two normal arms
        self.assertEqual(rep["rows"][2]["loo_pooled_phat"], 0.834)
        self.assertAlmostEqual(
            rep["rows"][2]["exact_two_sided_p"], 3.030544e-66, delta=3.030544e-72
        )
        # normal arms tested against the pool polluted by the wild arm
        self.assertEqual(rep["rows"][0]["loo_pooled_phat"], 0.667)
        self.assertAlmostEqual(
            rep["rows"][0]["exact_two_sided_p"], 6.212780e-17, delta=6.212780e-23
        )
        self.assertAlmostEqual(rep["min_exact_p"], 3.030544e-66, delta=3.030544e-72)
        self.assertEqual(rep["verdict"], "POOLING_CONTESTED")

    def test_two_arm_canonical_pair_supported(self):
        rep = receipt([(417, 500), (407, 500)], DEFAULT_ALPHA)
        self.assertEqual(rep["arms"], 2)
        self.assertEqual(rep["pooled_phat"], 0.824)
        # leave-one-out identity: each arm is tested against the OTHER arm only
        self.assertEqual(rep["rows"][0]["loo_pooled_phat"], 407 / 500)
        self.assertEqual(rep["rows"][1]["loo_pooled_phat"], 417 / 500)
        self.assertAlmostEqual(
            rep["rows"][0]["exact_two_sided_p"], 2.747402e-01, delta=1e-7
        )
        self.assertAlmostEqual(
            rep["rows"][1]["exact_two_sided_p"], 2.294052e-01, delta=1e-7
        )
        self.assertAlmostEqual(rep["min_exact_p"], 2.294052e-01, delta=1e-7)
        self.assertEqual(rep["verdict"], "POOLING_SUPPORTED")

    def test_alpha_is_the_whole_rule(self):
        pairs = [(417, 500), (407, 500)]
        at_05 = receipt(pairs, 0.05)
        at_50 = receipt(pairs, 0.5)
        self.assertEqual(at_05["min_exact_p"], at_50["min_exact_p"])
        self.assertEqual(at_05["verdict"], "POOLING_SUPPORTED")
        self.assertEqual(at_50["verdict"], "POOLING_CONTESTED")
        for rep in (at_05, at_50):
            expected = (
                "POOLING_CONTESTED"
                if rep["min_exact_p"] < rep["alpha"]
                else "POOLING_SUPPORTED"
            )
            self.assertEqual(rep["verdict"], expected)

    def test_logpmf_matches_direct_combinatorics(self):
        k, p, x = 500, 0.834, 417
        direct = math.comb(k, x) * (p ** x) * ((1 - p) ** (k - x))
        self.assertAlmostEqual(math.exp(logpmf(k, p, x)), direct, delta=direct * 1e-9)
        self.assertEqual(logpmf(k, p, -1), -math.inf)
        self.assertEqual(logpmf(k, p, k + 1), -math.inf)

    def test_degenerate_pool_probability_returns_one(self):
        self.assertEqual(exact_two_sided_p(500, 0.0, 417), 1.0)
        self.assertEqual(exact_two_sided_p(500, 1.0, 417), 1.0)

    def test_parse_arm_accepts_and_refuses(self):
        self.assertEqual(parse_arm("417:500"), (417, 500))
        for bad in ("417", "417:500:1", "41a:500", "501:500", "417:0", "-3:500"):
            with self.assertRaises(ValueError):
                parse_arm(bad)

    def test_receipt_refuses_fewer_than_two_arms(self):
        with self.assertRaises(ValueError):
            receipt([(417, 500)], DEFAULT_ALPHA)

    def test_cli_success_and_refusals(self):
        out = StringIO()
        with redirect_stdout(out):
            rc = main(["417:500", "407:500"])
        self.assertEqual(rc, 0)
        self.assertIn("POOLING_SUPPORTED", out.getvalue())
        self.assertIn("min_exact_p", out.getvalue())
        for argv in (["417:500"], ["501:500", "1:500"], ["417:500", "407:500", "--alpha", "1.5"]):
            with redirect_stdout(StringIO()):
                rc = main(argv)
            self.assertEqual(rc, 2)

    def test_render_names_the_authority_limit(self):
        rep = receipt([(417, 500), (407, 500)], DEFAULT_ALPHA)
        text = render(rep)
        self.assertIn("never a HELD/REFUTED reader", text)
        self.assertIn("verdict: POOLING_SUPPORTED", text)


if __name__ == "__main__":
    unittest.main()
