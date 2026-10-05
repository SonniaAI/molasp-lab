"""Fages tightness analysis for ground normal logic programs.

A normal program P is **tight** iff there is a level mapping lambda with
lambda(a) > lambda(b) for every rule ``a :- b, ...`` — equivalently, iff
the *positive* dependency graph (edge b -> a for each positive body atom b
of a rule with head a) is acyclic. Fages' theorem: for tight programs the
supported models coincide with the stable models.

This matters for the substrate question: a well-stirred chemical soup
computes supported models (mass-action kinetics cannot distinguish a
founded derivation from a self-sustaining cycle), so the tightness
verdict decides which foundedness strategy the compiler must apply.

Usage::

    python3 -m molasp.tightness program.lp

Prints ``TIGHT`` or ``NOT TIGHT`` plus representative positive cycles.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict, deque
from dataclasses import dataclass, field

ATOM = re.compile(r"^[a-z]\w*$")


@dataclass
class Rule:
    """A ground normal rule ``head :- pos, ..., not neg, ...``.

    ``head is None`` marks an integrity constraint (body-only rule).
    """

    head: str | None
    pos_body: list[str] = field(default_factory=list)
    neg_body: list[str] = field(default_factory=list)


def parse(text: str) -> list[Rule]:
    """Parse a ground normal program, one rule per line.

    Accepts facts (``a.``), rules (``a :- b, not c.``) and constraints
    (``:- b.``); ``%`` starts a comment.
    """
    rules = []
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.split("%", 1)[0].strip()
        if not line:
            continue
        if not line.endswith("."):
            raise ValueError(f"line {lineno}: rule must end with '.': {raw!r}")
        content = line[:-1]
        if ":-" in content:
            head_part, body_part = content.split(":-", 1)
        else:
            head_part, body_part = content, ""
        head = head_part.strip() or None
        pos: list[str] = []
        neg: list[str] = []
        if body_part.strip():
            for lit in body_part.split(","):
                lit = lit.strip()
                if not lit:
                    raise ValueError(f"line {lineno}: empty literal in {raw!r}")
                if lit.startswith("not "):
                    atom = lit[4:].strip()
                    neg.append(atom)
                else:
                    pos.append(lit)
        for atom in ([head] if head else []) + pos + neg:
            if not ATOM.match(atom):
                raise ValueError(f"line {lineno}: bad atom {atom!r}")
        rules.append(Rule(head, pos, neg))
    return rules


def positive_dependency_graph(program: list[Rule]) -> dict[str, set[str]]:
    """Edges b -> a for each positive body atom b of a rule with head a."""
    graph: dict[str, set[str]] = defaultdict(set)
    for rule in program:
        if rule.head is None:
            continue  # constraints create no dependencies
        for b in rule.pos_body:
            graph[b].add(rule.head)
    return graph


def _nodes(program: list[Rule]) -> set[str]:
    nodes: set[str] = set()
    for rule in program:
        if rule.head is not None:
            nodes.add(rule.head)
        nodes.update(rule.pos_body)
    return nodes


def tightness(program: list[Rule]) -> tuple[bool, list[list[str]]]:
    """Return ``(is_tight, representative_cycles)``.

    Verdict via Kahn's algorithm on the positive dependency graph;
    cycles are reported for human-facing output only.
    """
    nodes = _nodes(program)
    succ = positive_dependency_graph(program)
    pred: dict[str, set[str]] = defaultdict(set)
    for a, targets in succ.items():
        for b in targets:
            pred[b].add(a)
    indeg = {n: len(pred[n]) for n in nodes}
    queue = deque(sorted(n for n in nodes if indeg[n] == 0))
    processed = 0
    while queue:
        n = queue.popleft()
        processed += 1
        for m in sorted(succ.get(n, ())):
            indeg[m] -= 1
            if indeg[m] == 0:
                queue.append(m)
    tight = processed == len(nodes)
    cycles = [] if tight else _example_cycles(nodes, succ)
    return tight, cycles


def _example_cycles(nodes: set[str], succ: dict[str, set[str]]) -> list[list[str]]:
    """Walk first-successors from each unvisited node until a cycle closes."""
    cycles: list[list[str]] = []
    seen: set[str] = set()
    for start in sorted(nodes):
        if start in seen:
            continue
        path = [start]
        pos = {start: 0}
        cur = start
        while True:
            nxts = sorted(succ.get(cur, ()))
            if not nxts:
                break
            cur = nxts[0]
            if cur in pos:
                cycles.append(path[pos[cur]:])
                break
            pos[cur] = len(path)
            path.append(cur)
        seen.update(path)
    return cycles


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    text = open(argv[0]).read() if argv else sys.stdin.read()
    program = parse(text)
    tight, cycles = tightness(program)
    print("TIGHT" if tight else "NOT TIGHT")
    for cycle in cycles:
        print("positive cycle: " + " -> ".join(cycle + cycle[:1]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
