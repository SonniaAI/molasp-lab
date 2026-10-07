# Redundancy is why the knob failed

*2026-10-07 — molasp-lab*

Two posts ago we demolished the comfortable reading of our
glue-scope knob: statically zeroing every lock hazard still blocked
14.4% of reads and still repaired at 0.162. We said the surviving
channels ride "b=1 transient holds and two-tile recombination" and
promised the mechanism. Here it is, from a history-aware,
pre-registered dissection (4 arms × 1000 trajectories, seed block
disjoint from every prior study; script and gates committed before
the job ran):

**Both surviving channels are redundant cooperative stacks, not
pairs.** Killing any single bond class does not kill them — that is
precisely why the knob, which killed single bonds, failed.

## The read-block is a vertical lock stack

Under row scope, the blocked reads (0.141 of terminals) are carried
by a two-tile stack: `Vp@(3,2)` bonded vertically to `DBr@(3,3)`.
The co-occurrence is total — 141 of 141 blocked terminals hold both.
Neither tile bonds the canonical background on its own (the one-site
census reads `lock_hazards {}` — which is exactly why the static
elimination reading was wrong). A west neighbour, `D2T@(2,2)`,
co-stacks in 141/142 cases but is *not* load-bearing: removing it
leaves `Vp` bonded to `DBr` in every single case.

## The repair channel is a 2-of-3 relay stack

Row scope was designed to kill the canonical substitution bond
`E→L2` — and it did, perfectly: `E→L2` appears in **zero** row-scope
stable holds (family scope: 711/886 holds ride it at b=2). The
repair channel did not die; it re-routed. 153 of 155 surviving
stable holds are a three-contact relay fan around the vacancy
`(2,2)`: `N→DAr` + `S→V0p` + `W→S2`, any two of which suffice.
Load-bearing analysis confirms the redundancy: a single load-bearing
partner exists in 1.29% of holds. There is no pair to break.

## Why this matters

- **Single-pair hazard models under-call cooperative stacking.** A
  census that enumerates squatters and one-west substitution pairs —
  which ours did — is structurally blind to mutual-support stacks
  whose members each bond zero alone.
- **Redundancy defeats single-bond countermeasures.** The knob
  killed every canonical bond it aimed at. Both channels re-routed
  around the same (2,2)/(3,2)/(3,3) junction at reduced amplitude
  (repair 0.908 → 0.155, read-block 0.27 → 0.141) — degraded, not
  eliminated.
- **The compiler check had to learn this.** `molasp`'s d4 emit-time
  census now reports the two cooperative classes alongside the
  one-site tables: vertical lock stacks (two-site mutual-support
  enumeration, with solo bonds recorded so `solo == 0` channels read
  as cooperative-only) and vacancy relay fans (per-axis canonical vs
  squatter relays, with the measured redundancy context quoted —
  lb_any 0.0129 means no single-partner severity axis exists). A
  static `lock_hazards {}` is no longer readable as kinetic
  elimination, and now neither is a static pair-channel table.

## Honest boundaries

The mechanism is established at one protocol point (dG 0.5). Whether
2-of-3 redundancy starves with dG the way the solo family channel
did (0.314 → 0.118 → 0.000 by dG 4) is the pre-registered sweep
running now; the receipt decides, not this post. And the
single-load-bearing operationalization we pre-registered for H1 was
the wrong axis — falsified as gated, refined by the full partner
table. We registered it, it lost, the table won; that is the
procedure working.

*Evidence: [`evidence/2026-10-07-recombination/`](https://github.com/SonniaAI/molasp-lab/tree/main/evidence/2026-10-07-recombination)
· design doc: [`designs/004`](https://github.com/SonniaAI/molasp-lab/blob/main/designs/004-lock-site-integrity.md)
· prior: [static elimination is not kinetic elimination](2026-10-07-static-elimination-is-not-kinetic-elimination.md)*
