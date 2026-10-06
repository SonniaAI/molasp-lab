"""designs/002 F2-boundary build — WRONG_CUT with lock-on-false.

Program P (unchanged):   a.   p :- a.   p :- q.   q :- p.
Unique stable model {a,p,q} (clingo cross-check, tick 7/14).

WRONG_CUT (tick 14/15) placed the cut the wrong way round — q:-p cut,
p:-q nominally wired — but still keyed row 3's lock to the TRUE value
(L3.W = rq-t).  Kinetics then SELF-CORRECTED the wrong compile: the
aTAM-dead true tile rode a b=1 transient and was captured by the
true-typed lock into a b=2 terminal decoding the stable model
{a,p,q} at 100/99.2/72.6% for dG<=4 (tick 15, F2).

The honest boundary tick 15 left open: "a compiler that re-predicted
q=false after cutting would emit lock-on-rq-f and would presumably
capture {a,p} instead — the cut's kinetic fate is decided by the
lock's value typing, not by the cut.  That variant is the natural
next build."

This file IS that build.  The compiler, having made the same wrong
cut, now re-runs its fixpoint on the severed program: with q:-p cut,
q loses its only support and the fixpoint predicts q = FALSE.  The
emission follows the same discipline as the 2cycle falsity chain
(designs/002 construction of record): a predicted-false atom's
  - false tile carries the row-below's PREDICTED-value done glue on
    its south face (here rp-t-done: p stays true via the anchor), and
  - lock bonds the PREDICTED value's output (L3.W = rq-f).

Everything else is byte-identical to WRONG_CUT: same stage order
a<p<q, same OR pair for p (anchor live, cycle edge dead-at-b=1), same
Q_CUT true tile (south u-cut, value outputs intact) — the true tile
is still emitted (the decision pair is the substrate's vocabulary;
the lock + falsity chain encode the prediction, v3 rule (a)).

Predicted aTAM terminal decode: {a,p} — the same wrong-but-terminal
decode as WRONG_CUT, now reached by the false tile's anchored chain
instead of being unreachable.  Predicted kTAM behaviour (this tick's
question): the true tile's b=1 transient can no longer be captured
(no tile bonds rq-t from the lock side), so the self-correction
channel is structurally gone and the assembly should execute the
compile's error faithfully — strict {a,p} at high rate.
"""
from tiles_anchored import (ROW_A, SPINE, P_ANCHOR, P_CYCLE_WIRED,
                            P_FALSE, L_P, Q_CUT)

# q, predicted FALSE by the post-cut fixpoint: falsity-chain south
# glue reads the row-below's PREDICTED-TRUE done face (p via anchor).
Q_FALSE_CHAINED = {"W": "go3", "S": "rp-t-done",
                   "E": "rq-f", "N": "rq-f-done"}
# lock keyed to the PREDICTED value's output — the false one.
L_Q_FALSE = {"W": "rq-f", "S": "base3", "N": "cap3"}

WRONG_CUT_LOCKFALSE = {
    "name": "wrong_cut_lock_on_false",
    "rows": {1: "a", 2: "p", 3: "q"},
    "tiles": {
        **SPINE, **ROW_A,
        "D2TA": dict(P_ANCHOR), "D2TQ": dict(P_CYCLE_WIRED),
        "D2F": dict(P_FALSE), "L2": dict(L_P),
        "D3T": dict(Q_CUT),
        "D3F": dict(Q_FALSE_CHAINED), "L3": dict(L_Q_FALSE),
    },
    "true_tiles": {1: "D1T", 2: "D2TA", 3: "D3T"},
    "expected_terminal_decode": "ap",
}
