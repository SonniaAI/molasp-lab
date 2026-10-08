# Compiling logic into matter

2026-10-08 — molasp-lab · synthesis, v1

**TL;DR.** What this lab builds, in plain terms: a way to compile a
logic program into a self-assembling substrate of DNA tiles, and a way
to check — exhaustively, not by sampling — that the substrate cannot
compute the wrong answer. The property that matters is not "the wrong
tile rarely attaches" but "the wrong tile can never attach".

## The program side

An answer-set program is a small logic program: a list of facts and
rules, and the interesting question is what it can consistently
believe. The witness program that started this programme is two lines:

```
a.
p :- p.
```

`a` is a fact. `p` is true if `p` is already true — a self-loop with
no external evidence. The correct (stable) answer is `{a}`: `p` never
gets support. But there is a second, tempting answer — `{a, p}` — where
`p` supports itself. A circular justification that never had to be
founded anywhere. That is the failure mode this whole programme
chases: a substrate that can sit in a self-supporting wrong answer
forever, with no local signal that it is wrong.

## The matter side

The substrate is a square-tile self-assembly system, modelled as the
kinetic Tile Assembly Model (kTAM). Tiles carry matching codes on
their edges — "glues" — and a tile sticks where its glues match what
it touches *and* the bond energy clears the assembly temperature.
Growth starts from a seed and propagates; when growth stops, the
finished assembly decodes back into an answer. A correct compile is
one where **every** assembly the substrate can finish decodes to the
correct answer — not merely the likely ones.

Compiling a program to tiles — the "lowering" — maps each literal and
rule to tiles whose glues are typed so a wrong value has nowhere to
bond. The first version got lucky; the third did not need to.

## The property: improbable is not impossible

The first kinetic run of the C2 witness decoded to the unfounded
answer in 0 of 4,000 trajectories. That number was luck — the lock
tile in that geometry happened to have no partner at the height where
the wrong answer sits. Change the geometry slightly and the self-loop
locks shut as happily as the correct answer (the v2.1 grid trapped a
fifth of all trajectories at ΔG = 0.5). The fix became the
programme's first design rule: **a lock must check the value it
locks**, and every channel a wrong value can ride must be typed —
horizontal and vertical alike.

Typed that way, a wrong decision tile's bonding faces match nothing,
at any strength, in any producible assembly: its best possible bond
total is 1, under the temperature of 2. It is not improbable — it is
un-lockable. The measurement agreed (0 wrong decodes in 2,000
trajectories, against 355/2000 for the untyped geometry) and the
exhaustive census explains why: the glue table admits exactly ten
producible assemblies, one terminal assembly, decoding `{a}`; wrong
tiles appear in none of them. Those assertions run in CI, so the
property cannot quietly regress.

## Where that reaches

The same machinery now lowers more than the witness: multi-atom
recursion (designs/002), body conjunction (003), twice-derived chains
(008), AND over derived atoms (009) and — since 8 Oct — a spine rule
stated as a *class* ("every same-name spine self-bond carries
strength 2, for every row, forever") instead of three disagreeing
finite tables. That lifted a four-row build cap: the first five-row
program now assembles to a unique terminal with all five rows locked,
decoding its complete answer. The cap, it turned out, was an
inventory artefact — "the substrate was never capped. The inventory
was."

## Read on

- [Designs/001 — the C2 witness lowering](../designs/001-tile-lowering-witness.md)
- [The repairability arc summary](../research-log/2026-10-07-repairability-arc-summary.md)
- Next: [Energy, error and the knob](02-energy-error-and-the-knob.md) ·
  [How we check a design](03-how-we-check-a-design.md) ·
  [Status and open threads](04-status-and-open-threads.md)
