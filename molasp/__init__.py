"""molasp — compiling answer set programs to molecular substrates.

Public lab code for the Sonnia AI molasp programme. Submodules:

- ``resources``: the three-resource arithmetic (species count, copy
  number, search multiplicity) that the programme's feasibility claims
  rest on, with tests asserting the load-bearing numbers.
- ``tightness``: Fages tightness analysis for ground normal programs —
  the first pass of the compiler pipeline.
- ``readwindow``: design rule (c) as a compiler invariant — the read
  window a compiled order file must state, as a function of
  (Gse, Gmc, depth, weakly held sites), never a constant.
- ``offchannel``: d4 — the emit-time off-channel squat census
  (designs/004): every (site, tile) misincorporation channel the
  inventory admits against the canonical assembly, lock-site hazards
  and cross-row lock misreads called out, measured kinetic context
  quoted.  WARNING severity: reports, never gates.
"""

__version__ = "0.1.0"
