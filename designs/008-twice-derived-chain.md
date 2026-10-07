# 008 — Twice-derived chains: a fragment design for two derived atoms

Status: **DESIGN ONLY** — nothing in this document is compiled, emitted,
or BFS-verified. No measurements are claimed. This is the tick-46
corpus successor proposal (single-derived-atom boundary U3; "two
derived atoms needs multi-row-chain design", research-log
2026-10-07-parity-corpus.md). Implementation target: a future tick;
every count marked `predicted` below is hand arithmetic, not output.

## 1. What v0.1 refuses, exactly

The v0.1 fragment admits exactly one derived atom (a rule head) per
program, at the terminal row. A chain `q :- p. r :- q.` needs two
relaxations, both currently loud refusals in `molasp/compiler.py`:

| gate | location | message (fragment) | blocks |
| --- | --- | --- | --- |
| G1 | compiler.py:213–217 | `rule atom … at non-terminal row …` (PR3) | `q` as a derived row at y=2 |
| G2 | compiler.py:260–263 | `not via-carried (row-1); direct-below unit` | `r :- q` reading `q` at y=2 (unit body) |

Everything else the minimal chain needs already exists: `q :- p`
reads `p` on the standard row-1 via channel (slot B, col 2), and the
adjacent-below read channel (slot A) already carries conjunctive
literals (compiler.py docstring; PR1 pins the adjacency requirement).

## 2. Channel choice for the new read (two options)

**Option I — direct-below unit at slot A (recommended).** `r`'s unit
reader consumes the N-face signal of `q`'s row-2 lock column, the
same strength-2 channel AND bodies already use one row up. Reuses an
existing glue class; delta is one new glue name per chain link, no
new column semantics.

**Option II — via-carry extension.** `q`'s true lock exposes a slot-B
via glue carried up col 2, generalizing "row-1 witness" to
"any derived row witness". Rejected for v0.2: it makes the via column
stateful at every height (a carried witness must reflect the
*conditional* truth of `q`, not the unconditional truth of a fact),
which multiplies column-2 tile variants per link and touches the
channel PC3/PC4 dead-reader pins depend on.

## 3. Row-class machinery (the real design content)

v0.1 has two row classes: **fact rows** (single truth value: growth +
one lock tile) and the **terminal row** (per-body true-lock variants
`-t`, false cap, dead relays). A chain introduces a third class:

**Intermediate derived row** (`q` at y=k, 1 < k < n):
fact-row growth/cover tiles unchanged, plus terminal-style variant
machinery scoped to `q`'s rule set — one true-lock variant per live
body, one false cap (relay) when all bodies are dead, dead-body
reader glues that must never realize. Decode (parity.py `decode`,
col-3 W-face `-t` suffix) generalizes unchanged: `q` true iff its
lock tile ends `-t`.

Tile-count arithmetic, per row class (hand counts from the PC2
baseline, n=3, 14 tiles):

| row class | variant tiles | predicted delta vs a fact row |
| --- | --- | --- |
| fact row | 1 lock | 0 |
| intermediate derived row, k=1 body (`q :- p`) | 1 true lock + 1 false cap | +1 |
| terminal row, unit reader on slot A | as v0.1 unit reader | 0 (channel rename only) |

Predicted PC9 tile count: **15–16** vs PC2's 14 (PC2 carries 2 bodies
on the terminal row; PC9 carries 1+1 across two rows). Exact counts
are implementation output, not claims.

## 4. Proposed corpus additions (v0.2 candidates)

| name | program | least model (hand) | exercises |
| --- | --- | --- | --- |
| PC9 | `p. q :- p. r :- q.` | {p,q,r} | live two-link unit chain (G1+G2 minimal) |
| PC10 | `p. q :- z. r :- q.` | {p} | dead-link cascade at depth 2: `q` false-caps at row 2, `r`'s slot-A reader must stay absent |
| PC11 | `p. q. s. q2 :- p. r :- q2, s. r :- q2.` | {p,q,s,q2,r} | chain + AND terminal + OR pair; dead-variant glue pin alongside a live chain |

Refusal corpus updates: PR3's message splits — rule atoms below the
terminal row become legal **only** with bodies over (row-1 via) ∪
(adjacent-below derived). New refusals: non-adjacent chain (head
reads a derived atom ≥2 rows below), cyclic rules (`q :- r. r :- q.`
has no fact row and no founded order), and unit body over a derived
atom that is not directly below. PR1/PR2/PR4/PR5/PR6 stand verbatim.

## 5. Parity conditions to pin (unchanged claim shape)

Per corpus program, the tick-46 conjunction: predicted model = least
model; every terminal assembly decodes to exactly the least model;
full locks on all n rows (PC10 forces the false-relay lock at the
intermediate row); every dead-body reader glue absent from every
producible assembly (PC10 pins the *cascade*: one dead link must kill
every reader above it without breaking row locks below).

## 6. Cost and honesty boundaries

BFS is exhaustive over the 4×n grid (tau=2). Variant machinery on row
2 roughly doubles row-2 lock states: predicted assembly counts
O(50–150) at n=3 — bounded by PC8's 85-at-n=4 scale, comfortably
local and static (tick-37 rule: no cluster job). Boundaries of this
design: chain length 2 only (depth 3 unexamined); Option I keeps
slot A read-only-up (no feedback glues); tile counts and BFS numbers
are predictions; the false-cap relay at an intermediate row is new
machinery with no existing pin — PC10 is its first test, and if it
fails the failure mode is *over*-production (r true on a dead link),
which the decode-uniqueness pin catches.
