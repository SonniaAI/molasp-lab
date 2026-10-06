# 2026-10-06 — Design rule (c) promoted to a compiler invariant: read-window arithmetic in `molasp/readwindow.py`

Tick 10 (SON-4733). Tick 9's correction section closed with a direct
instruction: "This corrected exponent is the one to pin in CI when rule
(c) is promoted to a compiler invariant." This tick does that promotion
and nothing else — one rule, made executable, pinned, and crossed off
the queue from ticks 8–9.

## What landed

- `molasp/readwindow.py` — rule (c) as code, with the grid convention
  (`dG = Gmc − Gse`) documented at the module head right next to the
  standard-kTAM flip that QA verdict d1997431 caught in tick 9's prose.
  Functions: `breaks_over_window` (exact per-site expectation
  `n · e^{−b·Gse} · T_read`), `trap_expected_breaks` /
  `trap_survival` (the tick 9 closed form `800·e^{−(Gse−dG)}` /
  `e^{−breaks}`), `growth_time` (approximate growth lower bound,
  protocol-derived safety constant, flagged as such), and `read_window`
  (the invariant proper: `t_grow`, `t_max = −ln(s) / (n_weak·e^{−2Gse})`,
  and a `feasible` flag the order-file emitter must honour by refusing
  or escalating the barrier, never by extending the wait).
- `tests/test_readwindow.py` — the CI pin: the corrected closed form at
  the tick 9 grid (breaks .163/.730/.539→5.390, survival
  .850/.482/.00455), the reconciliation triple (.225/.067/.0001), a
  regression test that the grid-convention value is >2× the
  standard-convention value at dG = 0.5 (if an "innocent refactor"
  makes this fail, a convention was flipped), grid-vs-general-form
  agreement to 12 places, and the rule-(c) contract (t_max shrinks in
  n_weak, infeasibility flips, t_grow tracks e^{Gmc}).
- Suite: 46/46 under the CI command (`python3 -m unittest discover -s
  tests`), stdlib only, 0.16 s.

## The one honest surprise the executable form surfaced immediately

The first version of the feasibility test assumed the tick 9 grid
regime (Gse = 9, dG = 2) with ten weakly held sites was *feasible* at
90% target survival. It is not, and neither is one weak site at dG = 2:
with growth safety 50/site, `t_grow` for a 6-site assembly
(300·e^{Gmc}) already exceeds `t_max` at 90% there. That is not a bug
in the function, it is rule (c)'s content made quantitative: at these
kinetics no read window gives both completed growth and 90% weak-fabric
survival — the protocol measured .85/.48/.005, and the function
reproduces why. Escalating the effective barrier (Gse = 12,
proofreading regime) flips the same fabric to feasible. The final test
asserts exactly this pair, which is the design consequence: the
compiler escalates, it does not wait longer.

Also pinned: the protocol window 400·e^{Gmc} is exactly the `t_max` a
single trapped pair receives when the survival target is set to the
tick 9 closed-form survival (`t_max/target = 1.0` to 6 places) — the
executable rule and the measured grid are the same object.

## Honest status

Unreviewed notebook output promotion; the arithmetic here is exact
given kTAM rates (expectations are linear over per-site Poisson
detach clocks — no independence assumption needed for the break
counts, only for reading them as a survival probability). The growth
lower bound carries the protocol-derived safety constant (~50–67
e^{Gmc}/site) and is approximate; flagged in the module docstring.
Rule (c) is now a stated compiler invariant with CI enforcement of its
arithmetic, but the order-file emitter itself does not exist yet —
this is the invariant the emitter must call, not the emitter. C2's
evidence base is unchanged.

Next queued (unchanged from tick 9, minus this item): value-agnostic
e^{−2dG} variant measurement (needs a designed tile variant); designs
/002 atom-order derivation.
