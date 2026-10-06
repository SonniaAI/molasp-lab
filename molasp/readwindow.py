"""Read-window arithmetic for compiled tile assemblies — design rule (c).

Promoted from tick 9's candidate rule to a compiler invariant (tick 10,
SON-4733). The read protocol is not free: every site held at total glue
strength b detaches at rate e^(-b*Gse) while the assembly is being
waited on, so a read window long enough to finish growth also dissolves
weakly held fabric. The churn that erases wrong traps (the good half of
the mechanism) is the same churn that erases correct b = 2 tiles (the
bad half), and both scale with T_read.

Rule (c): a compiled order file must state the read window as a
function of (Gse, Gmc, assembly depth, number of weakly held sites) —
never as a constant. This module is that function.

Conventions match the tick 8/9 instrumented grid exactly:

- kTAM nondimensionalised rates: attach rate e^(-Gmc), detach rate for
  total strength b is e^(-b*Gse);
- grid convention ``dG = Gmc - Gse`` (see
  ``evidence/2026-10-06-row2-ordering/instrument_mc.py``; note this is
  the negative of the standard-kTAM dG = Gse - Gmc, the flip QA review
  d1997431 caught in tick 9's first-landed prose);
- the tick 8/9 protocol waits ``T_read = 400 * e^Gmc`` after seeding.

Closed form (tick 9, corrected): a trapped pair is two tiles each held
at b = 2, so expected breaks over the window are

    2 * e^(-2*Gse) * T_read = 800 * e^-(Gse - dG)      [T_read = 400*e^Gmc]

and survival is exp(-breaks). This is exact given the kTAM rates; the
MC, committed outputs and tests are unchanged from tick 9.
"""

from __future__ import annotations

import math

#: Read-wait multiplier used by the tick 8/9 protocol: T_read = 400 * e^Gmc.
T_READ_MULTIPLIER = 400.0

#: Growth-time safety factor per site, derived from the protocol: the
#: 6-site witness grid used 400 * e^Gmc, i.e. ~67 e^Gmc per site. The
#: default here is the conservative 50 * e^Gmc per site; it is a
#: protocol-derived engineering constant, NOT a kTAM consequence, and
#: the growth lower bound it feeds is approximate accordingly.
GROWTH_SAFETY_PER_SITE = 50.0


def breaks_over_window(gse: float, n_sites: int, b: int, t_read: float) -> float:
    """Expected detachments from ``n_sites`` sites each held at strength ``b``.

    Exact given kTAM: each site detaches at rate e^(-b*Gse), and
    expectations are linear, so this needs no independence assumption
    beyond Poisson detach clocks per site.
    """
    if n_sites < 0:
        raise ValueError("n_sites must be >= 0")
    if b <= 0:
        raise ValueError("sites at strength 0 are not attached")
    return n_sites * math.exp(-b * gse) * t_read


def trap_expected_breaks(gse: float, dg: float,
                         t_read_factor: float = T_READ_MULTIPLIER) -> float:
    """Expected breaks of one trapped pair under the grid protocol.

    Two tiles at b = 2 over T_read = ``t_read_factor`` * e^Gmc, in the
    grid convention dg = Gmc - Gse, so the Gmc terms cancel to
    ``2 * t_read_factor * e^-(Gse - dg)``.
    """
    return 2.0 * t_read_factor * math.exp(-(gse - dg))


def trap_survival(gse: float, dg: float,
                  t_read_factor: float = T_READ_MULTIPLIER) -> float:
    """Probability a trapped pair survives to read (tick 9 closed form)."""
    return math.exp(-trap_expected_breaks(gse, dg, t_read_factor))


def growth_time(n_sites: int, gmc: float,
                safety_per_site: float = GROWTH_SAFETY_PER_SITE) -> float:
    """Approximate lower bound on the read wait needed to finish growth.

    Sequential frontier growth of depth ``n_sites`` takes ~n_sites * e^Gmc
    in expectation (attach rate e^(-Gmc) per exposed site); the safety
    factor is protocol-derived, see GROWTH_SAFETY_PER_SITE.
    """
    if n_sites <= 0:
        raise ValueError("n_sites must be >= 1")
    return safety_per_site * n_sites * math.exp(gmc)


def read_window(gse: float, gmc: float, n_sites: int, n_weak: int,
                target_survival: float = 0.9,
                safety_per_site: float = GROWTH_SAFETY_PER_SITE) -> dict:
    """Rule (c) made executable: the read window an order file must state.

    Returns a dict with:

    - ``t_grow``: read wait needed for growth (approximate, see
      :func:`growth_time`);
    - ``t_max``: read wait at which weakly held fabric survives with
      probability ``target_survival`` — exact given kTAM:
      ``t_max = -ln(target_survival) / (n_weak * e^(-2*gse))``;
    - ``feasible``: whether a window satisfying both exists.

    ``n_weak`` is the number of sites held at b = 2 at read time in the
    terminal assembly (correct fabric counts too — rule (c) exists
    because the churn is not selective). A compiler emitting an order
    file for an infeasible parameterisation must refuse or add
    proofreading, not silently extend the wait.
    """
    if not 0.0 < target_survival < 1.0:
        raise ValueError("target_survival must be in (0, 1)")
    if n_weak < 0:
        raise ValueError("n_weak must be >= 0")
    t_grow = growth_time(n_sites, gmc, safety_per_site)
    if n_weak == 0:
        # No weakly held fabric: survival does not constrain the wait.
        return {"t_grow": t_grow, "t_max": math.inf, "feasible": True}
    t_max = -math.log(target_survival) / (n_weak * math.exp(-2.0 * gse))
    return {"t_grow": t_grow, "t_max": t_max, "feasible": t_grow <= t_max}
