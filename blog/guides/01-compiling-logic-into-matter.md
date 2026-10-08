# Compiling logic into matter

2026-10-08 — molasp-lab · synthesis, v1

## Start here

There is a kind of bug that never crashes. It does not throw an exception or fill a log line; it just sits there, quietly being wrong forever, and every computation built on top of it inherits the mistake. In logic programming that bug has a name — the self-supporting assumption, a conclusion that bootstraps itself into truth by pointing at itself — and this lab exists because we decided it was worth building *matter* that cannot make that mistake.

This guide is the map for the whole site. It explains, without prerequisites, what we compile, what we compile it *into*, and what property we are actually chasing. The dated lab-log entries underneath assume nothing beyond this page; if any term here feels foreign, the glossary habit of this blog is to explain a reference the first time it appears.

## The program side

An answer-set program is a small logic program: a list of facts and rules, where the interesting question is what the program can consistently believe. The witness program that started this programme is two lines:

```
a.
p :- p.
```

Read the second line as "p is true if p is already true". It is a loop with no external evidence: `p` is true because `p` is true. The correct reading of the program — the *stable model* — is `{a}`: `a` was given as a fact, and `p` never gets support from anywhere and so stays false. But there is a second, tempting reading — `{a, p}` — in which `p` supports itself. A circular justification that never had to be founded anywhere. That is the failure mode this programme chases in the physical world: a substrate that can sit in a self-supporting wrong answer forever, with no local signal that it is wrong.

## The matter side

The substrate is a square-tile self-assembly system, modelled in the kinetic Tile Assembly Model (kTAM). Picture graph-paper tiles a few nanometres across. Each edge carries a "glue" — a short DNA sticky-end with a matching code — and a tile sticks where its glues match what it touches *and* the bond energy clears the assembly temperature, written τ and measured in units of kT, the ambient energy of thermal agitation at room temperature. Growth begins from a seed tile and propagates outward; when growth stops, the finished assembly decodes back into an answer. A correct compile is one where **every** assembly the substrate can finish decodes to the correct answer — not merely the likely ones.

Compiling a program to tiles — we call it the *lowering* — maps each literal and rule to tiles whose glues are typed so that a wrong value has nowhere to bond. The first version of the lowering got lucky. The third did not need to, and that difference is the whole story of this guide.

## The property: improbable is not impossible

The first kinetic run of the witness lowering decoded to the unfounded answer `{a, p}` in 0 of 4,000 trajectories. We initially read that as success. It was luck. The lock tile — the tile whose job is to refuse an unfounded value — had no bonding partner in that particular geometry *by accident*; move the lock a row over, into the v2.1 geometry, and the self-loop locks shut as happily as the correct answer, trapping a fifth of all trajectories at ΔG = 0.5. (ΔG is the energy gap that decides whether an attachment can break again; guide two unpacks it.)

The fix became the programme's first design rule: **a lock must check the value it locks**, and every channel a wrong value can ride — horizontal *and* vertical — must be typed the same way. Typed correctly, a wrong decision tile's bonding faces match nothing, at any bond strength, in any producible assembly: its best possible bond total is 1, against a temperature of 2. It is not improbable — it is *un-lockable*. The trajectories agreed (0 wrong decodes in 2,000 runs, against 355/2000 for the untyped geometry), and the exhaustive census explains why: the glue table admits exactly ten producible assemblies, one terminal assembly, decoding `{a}`; wrong tiles appear in none of them. That census check runs in CI on every commit, so the property cannot quietly regress while we are not looking.

## Where that reaches

The same machinery now lowers more than the witness: multi-atom recursion (designs/002), body conjunction (003), twice-derived chains (008), AND over derived atoms (009) and — since 8 Oct — a spine rule stated as a *class* ("every same-name spine self-bond carries strength 2, for every row, forever") instead of three disagreeing finite tables. That lifted a four-row build cap: the first five-row program now assembles to a unique terminal with all five rows locked, decoding its complete answer. The cap, it turned out, was an inventory artefact — three hand-maintained bond-strength tables, the longest one four rows deep. "The substrate was never capped. The inventory was."

## Read on

- [Designs/001 — the C2 witness lowering](../designs/001-tile-lowering-witness.md)
- [The repairability arc summary](../research-log/2026-10-07-repairability-arc-summary.md)
- Next: [Energy, error and the knob](02-energy-error-and-the-knob.md) ·
  [How we check a design](03-how-we-check-a-design.md) ·
  [Status and open threads](04-status-and-open-threads.md)
