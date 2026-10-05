"""Resource arithmetic for the molasp programme.

Three resources, never one (conflating them is how exponentials disappear):

- **species count** |Σ| — distinct sequences; the program size.
- **copy number** c — molecules per species in the vessel.
- **search multiplicity** m — independent trajectories the vessel
  explores. This is the quantity that is exponential.

Every number here is derived, not remembered: the tests assert the
load-bearing figures used across the programme. Constants are approximate
where flagged; tests carry tolerances, not false precision.
"""

from __future__ import annotations

import math

AVOGADRO = 6.02214076e23          # mol^-1 (exact by SI definition)
NT_MASS = 330.0                   # g/mol per nucleotide (approximate)
EARTH_MASS_G = 5.97e27            # g (approximate)

#: Branching number of the standard 3-SAT recursion, which Brun's tile
#: system lays out in space: b = 2^(1/3) * ... derived from the
#: 3-SAT recursion T(n) = T(n-1) + T(n-2) + T(n-3); golden-ratio-like
#: root of x^3 = x^2 + x + 1.
BRANCHING_3SAT = 1.8392867552141612


def mass_per_assignment_grams(ell: int = 50) -> float:
    """Mass of one n-variable assignment strand, per variable block.

    A Lipton-style library needs 2^n of these, so library mass is
    ``2**n * n * mass_per_assignment_grams()``.
    """
    return ell * NT_MASS / AVOGADRO


def library_mass_grams(n: int, ell: int = 50) -> float:
    """Total mass of a Lipton-style brute-force assignment library."""
    return float(2 ** n) * n * mass_per_assignment_grams(ell)


def max_variables_for_mass(total_g: float, ell: int = 50) -> int:
    """Largest n whose brute-force library fits in ``total_g`` grams."""
    n = 0
    while library_mass_grams(n + 1, ell) <= total_g:
        n += 1
    return n


def vessel_molecules(volume_l: float = 100e-6, concentration_m: float = 1e-6) -> float:
    """Molecules in a well of ``volume_l`` litres at ``concentration_m``."""
    return volume_l * concentration_m * AVOGADRO


def bits(x: float) -> float:
    """log2, the natural unit for vessel and library comparisons."""
    return math.log2(x)


def brute_force_ceiling_n(volume_l: float = 100e-6, concentration_m: float = 10e-9) -> int:
    """Largest n the vessel can hold one library strand per assignment."""
    return int(math.floor(bits(vessel_molecules(volume_l, concentration_m))))


def plate_bits(wells: int = 1536) -> float:
    """Extra search-multiplicity bits from partitioning across ``wells``."""
    return math.log2(wells)


def pruning_ratio(n: int, b: float = BRANCHING_3SAT) -> float:
    """Brute-force mass / branching-b mass, per trajectory.

    The saving physical pruning buys on the search exponent at instance
    width ``n``: (2/b)**n. At b = 1.8393 this is 1.0873**n.
    """
    return (2.0 / b) ** n


def n_for_ratio(target: float, b: float = BRANCHING_3SAT) -> float:
    """Instance width at which ``pruning_ratio`` reaches ``target``."""
    return math.log(target) / math.log(2.0 / b)


def extra_variables(n_naive: float, b: float = BRANCHING_3SAT) -> float:
    """Extra variables branching-b explores at equal mass vs brute force.

    Equal mass: b**n_b = 2**n_naive, so n_b = n_naive * log2/log(b).
    """
    return n_naive * (math.log(2.0) / math.log(b)) - n_naive


def proofread_error(eps0: float, k: int) -> float:
    """Effective per-tile error after k x k proofreading (~eps0**k)."""
    return eps0 ** k


def max_assembly_size(delta: float, eps0: float, k: int) -> float:
    """Largest N with P(error-free assembly) >= 1 - delta: N ~ delta/eps."""
    return delta / proofread_error(eps0, k)
