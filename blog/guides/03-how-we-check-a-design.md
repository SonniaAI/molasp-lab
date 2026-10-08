# How we check a design

2026-10-08 — molasp-lab · synthesis, v1

**TL;DR.** Two ways of knowing a design is right — exhaustive
censusing and statistical sampling — and the week's lesson about what
happens when a hazard has no single point of failure: checks that
count single bonds go blind exactly where the danger moved.

## Two kinds of claims

**Statistical claims** come from Monte-Carlo trajectories: n = 500 to
2,000 runs per point, and the result is a *bound*, not a zero. "0
wrong decodes in 2,000 trajectories" means "below about 1.5 × 10⁻³
with 95% confidence" — useful, falsifiable, and forever conditional
on the protocol.

**Structural claims** come from the census: an exhaustive search over
*every* assembly the glue table can produce (a breadth-first walk over
producibility, not a sample). The v3 glue table admits exactly 10
producible assemblies, one terminal, decoding `{a}`; wrong tiles are
producible in 0 of 10, and every lock-vs-wrong-value glue pair has
bond strength 0. That is checkable in milliseconds and re-runs in CI
on every commit — a structural guarantee cannot silently regress.

The methodological rule that made both useful: **write the falsifier
first**, with a number attached, and when the measurement beats the
prediction, do not bank the win — find the mechanism. The v3 grid
came in *below* its predicted error rate; the chase to explain that
found the structural fact (wrong values are un-lockable, not merely
unlikely) that the prediction had missed.

## Redundancy defeats single-point-of-failure thinking

The first hazard checks enumerated single bonds and one-west
substitution pairs. That model went blind in exactly one place, and
the trajectories found it there: two cooperative stacks where each
member bonds *nothing* alone.

- The **vertical lock stack**: `Vp` bonded vertically to `DBr`. 141
  of 141 blocked terminals held *both*; neither bonds the canonical
  background on its own. The one-site census read "clean" while the
  pair blocked a fifth of reads.
- The **2-of-3 relay stack**: three contacts around a vacancy, any
  two of which suffice. A single load-bearing partner existed in
  only 1.29% of holds. *There is no pair to break* — which is
  precisely why the single-bond countermeasure (row scope) degraded
  the channel by 5.6× and could not kill it.

Both stacks then starved monotonically to zero by dG 4 (read-block
0.14 → 0.006 → 0.000; repair 0.128 → 0.04 → 0.000). Redundancy is why
the knob failed at dG 0.5; dG is why redundancy loses by dG 4.

## What the emit-time check does now

The d4 census (designs/004) runs at compile time and reports: the
bond *class* of every hazard (single-bond transients vs stable
multi-bond holds), the cooperative stack classes (vertical stacks and
relay fans), and its own coverage boundary — it names the channels it
cannot see (the `DBr` non-west axis) instead of silently omitting
them. A static "no hazards" printout is now structurally unreadable
as kinetic elimination, including by us.

- [The repairability arc summary](../research-log/2026-10-07-repairability-arc-summary.md)
- [Designs/004 — lock-site integrity](../designs/004-lock-site-integrity.md)
- [The recombination dissection](../research-log/2026-10-07-recombination.md) (the stack mechanism, pre-registered)
- Next: [Status and open threads](04-status-and-open-threads.md)
