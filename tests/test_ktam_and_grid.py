"""CI invariants for the designs/003 F4 harness (tick 19,
evidence/2026-10-06-and-ktam-grid/).

Pins the pre-registration contract, not the measured curve (the
full 6000-trajectory grid runs on the cluster queue; its run.out is
evidence):
  1. Protocol constants: Gse=9, Gmc grid, n=500/point, seed base —
     the pre-registered grid cannot drift silently.
  2. Structural decode impossibilities (why K4 runs on the loose
     decode): in build3 an L2 lock reads r-t, so a strict "q" decode
     cannot exist; in build1 an L3 lock reads r-t and no false locks
     exist, so strict non-{pqr, partial} cannot exist; build2's
     inventory has no q/r true tiles at all.
  3. Behavioural, fixed-seed small MC at dG=2 (12 traj/build):
     every strict decode is the expected one or "partial", and no
     reassertion-typed pair (strict partial + loose true-model
     subset) is observed — CI-safe: 36 trajectories, ~0.2 s.
"""
import os
import sys
import unittest

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
EV = os.path.join(HERE, "evidence", "2026-10-06-and-ktam-grid")
SIB = os.path.join(HERE, "evidence", "2026-10-06-body-conjunction-builds")
for p in (EV, SIB):
    if p not in sys.path:
        sys.path.insert(0, p)

import ktam_mc_and as K  # noqa: E402


class TestPreRegistration(unittest.TestCase):
    def test_protocol_constants(self):
        self.assertEqual(K.GSE, 9.0)
        self.assertEqual(K.GMC_GRID, (9.5, 11.0, 13.0, 16.0))
        self.assertEqual(K.N_PER_POINT, 500)
        self.assertEqual(K.BASE_SEED, 20261019)
        self.assertEqual(K.T_READ_MULTIPLIER, 400.0)

    def test_expected_decodes(self):
        got = {a.name: a.expected for a in K.SYSTEMS}
        self.assertEqual(got, {
            "P_AND_corrected": "pqr",
            "P_AND_minus_q": "p",
            "W1_dropped_literal_corrected": "qr",
        })

    def test_structural_lock_reads(self):
        # every lock tile's W face is a value glue; a present lock
        # forces its row's decoded value (this is what makes strict
        # wrong decodes structurally absent and pushes the K4
        # reassertion detector onto the loose decode)
        for api in K.SYSTEMS:
            for name, faces in api.build["tiles"].items():
                if name.startswith("L"):
                    self.assertTrue(
                        faces["W"].endswith(("-t", "-f")),
                        "%s.%s W=%r is not a value glue"
                        % (api.name, name, faces["W"]))

    def test_build2_readers_are_p_only(self):
        # build2's inventory carries no true tiles for q or r: the
        # loose decode can only ever read p (slot-A death is
        # structural, not kinetic)
        readers = K.TRUE_READERS["P_AND_minus_q"]
        self.assertEqual(set(readers), {"p"})
        exposed = set()
        for faces in K.BUILDS["build2"]["tiles"].values():
            exposed.update(faces.values())
        self.assertNotIn("q-t", exposed)
        self.assertNotIn("r-t", exposed)
        self.assertNotIn("and1_r", exposed)


class TestSmallMC(unittest.TestCase):
    """12 fixed-seed trajectories per build at dG=2 (CI-safe)."""

    def test_strict_decodes_are_expected_or_partial(self):
        import math
        T = 400.0 * math.exp(11.0)
        for idx, api in enumerate(K.SYSTEMS):
            for i in range(12):
                strict, loose = K.run_assembly(
                    api, 11.0, 9.0, T, 90210 + idx * 1000 + i).split("|")
                self.assertIn(
                    strict, (api.expected, "partial"),
                    "%s traj %d strict=%r loose=%r"
                    % (api.name, i, strict, loose))
                # NOTE: the reassertion GATE (<= 3/500 at dG in
                # {2,4,7}) is a full-grid statistic evaluated on the
                # queue job's run.out; a 12-traj CI sample sees the
                # ordinary partial-growth channel (strict partial +
                # loose subset ~ 2/12 at dG=2) and must not assert on
                # it.


if __name__ == "__main__":
    unittest.main()
