"""The contraction-minor lower bound: refute a width on a contracted minor.

Pathwidth is minor-monotone: if `H` is obtained from `G` by contracting edges
(and deleting vertices), `pw(H) <= pw(G)`. So a refutation of `pw <= w` on a
minor refutes it on the graph, and the minor's exact pathwidth is a lower bound
for the graph's. For pathwidth the bound is *not* capped by treewidth -- it is
the one bound in `reports/pathwidth_lower_bounds_survey.md` that reaches 38 on
myciel6 (tw 35) -- and a refutation on a 58-vertex minor costs 21,108 nodes
where the full graph had not finished at 1.7 x 10^9 (survey §4.1).

**Contraction.** Greedy, one edge at a time: pick a minimum-degree vertex `v`
(ties by index) and contract it into a neighbour `u`, chosen by the rule:

- `"min-d"`: the neighbour of least degree (ties by index), the survey's
  recommended rule;
- `"least-c"`: the neighbour sharing fewest neighbours with `v` (ties by
  index), the MMD+ rule of `bounds.contraction_degeneracy`.

`u` keeps its index and its neighbourhood becomes `N(u) ∪ N(v) − {u, v}`: a
genuine edge contraction, with no self-loop and no multi-edge. An isolated
vertex has no edge to contract and is deleted instead (`u = -1`), which is
also a minor operation. The contraction sequence is a list of `(v, u)` pairs
in the graph's own vertex indices; `replay` rebuilds the minor from it and
checks every pair is an edge (or an isolated deletion) at the moment it is
applied, so a recorded certificate can be checked without trusting this code's
choice of pairs. The greedy choice depends only on the current graph, so the
minor of size `m` is a prefix of the sequence that reaches any smaller size.

**The step** (`MinorLadder`). Before the descent refutes `w = UB - 1` on the
full graph -- and only if a short probe of the full graph does not settle `w`
-- contract to sizes from `start_fraction * n` upward in steps of
`step_fraction * n` to `max_fraction * n`, and on each minor try to refute `w`
under a node budget that grows geometrically with the size. Minors that admit
width `w` are recognised without a search where possible (`cheap_width`, and
a restricted search), since they can never refute it. An `unsat` proves
`pw(G) >= w + 1`, which ends the descent with proof `"minor"`. A `sat` records
the minor's witness width, so that minor is not asked again about any width at
or above it. An `unknown` on every minor of a size retries that size with a
larger budget (the next size costs about ten times more, survey §4.1), until
the call's share of the budget is spent. `MinorConfig` holds the defaults.

The descent re-enters the ladder at each new target, so a minor whose exact
pathwidth is `p` raises the lower bound to `p` as soon as the target reaches
`p - 1`: the refutation of `p - 1` on the minor is that statement.

**Soundness** rests on minor monotonicity (Fellows & Langston 1987 Lemma 4.2,
not yet in Lean here) and on the refutation of the minor, which runs `decide`
with whatever rules the descent runs -- by default the repaired rules proved
sound in MOSP's `lean/MOSPFormalization/Search/`.
"""

from __future__ import annotations

import math
import time
from collections.abc import Sequence
from dataclasses import dataclass, field

from pathwidth.graph import vertex_separation_masks

RULES = ("min-d", "least-c")


def _neighbours(masks: Sequence[int]) -> tuple[list[int], int]:
    """Open neighbourhoods and the active set from self-inclusive masks."""
    adj = [m & ~(1 << v) for v, m in enumerate(masks)]
    alive = 0
    for v, m in enumerate(masks):
        if m:
            alive |= 1 << v
    return adj, alive


def _contract(adj: list[int], alive: int, v: int, u: int) -> int:
    """Contract `v` into `u` in place (or delete `v` when `u == -1`); returns
    the new active set."""
    nv = adj[v]
    if u >= 0:
        merged = (adj[u] | nv) & ~((1 << u) | (1 << v))
        adj[u] = merged
        bits = merged
        while bits:
            bit = bits & -bits
            bits ^= bit
            w = bit.bit_length() - 1
            adj[w] = (adj[w] | (1 << u)) & ~(1 << v)
    else:
        bits = nv
        while bits:
            bit = bits & -bits
            bits ^= bit
            w = bit.bit_length() - 1
            adj[w] &= ~(1 << v)
    adj[v] = 0
    return alive & ~(1 << v)


def contraction_sequence(masks: Sequence[int], size: int, rule: str = "min-d") -> list[tuple[int, int]]:
    """Greedy contractions taking the active vertices of `masks` down to `size`.

    Returns `(v, u)` pairs: contract `v` into `u`, or delete the isolated `v`
    when `u == -1`. See the module docstring for the rule.
    """
    if rule not in RULES:
        raise ValueError(f"rule must be one of {RULES}, not {rule!r}")
    adj, alive = _neighbours(masks)
    n = len(masks)
    seq: list[tuple[int, int]] = []
    while alive.bit_count() > max(size, 0):
        best_v, best_d = -1, n + 1
        bits = alive
        while bits:
            bit = bits & -bits
            bits ^= bit
            x = bit.bit_length() - 1
            d = adj[x].bit_count()
            if d < best_d:
                best_d, best_v = d, x
        v = best_v
        nb = adj[v]
        u, best = -1, None
        bits = nb
        while bits:
            bit = bits & -bits
            bits ^= bit
            c = bit.bit_length() - 1
            score = adj[c].bit_count() if rule == "min-d" else (adj[c] & nb).bit_count()
            if best is None or score < best:
                best, u = score, c
        seq.append((v, u))
        alive = _contract(adj, alive, v, u)
    return seq


def replay(masks: Sequence[int], sequence: Sequence[tuple[int, int]]) -> tuple[list[int], list[int], dict[int, set[int]]]:
    """Apply a contraction sequence and return the minor, checked.

    Returns `(minor_masks, labels, branch_sets)`: self-inclusive masks of the
    minor over `0..m-1`, `labels[i]` the graph vertex that minor vertex `i`
    kept, and for each kept vertex the set of graph vertices merged into it.

    Raises `ValueError` if a pair is not an edge of the current graph, or a
    deletion is not of an isolated vertex, or a vertex is used after it was
    contracted away: a sequence that passes is a genuine minor.
    """
    adj, alive = _neighbours(masks)
    branch = {v: {v} for v in range(len(masks)) if alive >> v & 1}
    for step, (v, u) in enumerate(sequence):
        if not (0 <= v < len(masks)) or not alive >> v & 1:
            raise ValueError(f"step {step}: vertex {v} is not in the current graph")
        if u == -1:
            if adj[v]:
                raise ValueError(f"step {step}: deleting {v}, which is not isolated")
            branch.pop(v)
        else:
            if not (0 <= u < len(masks)) or not alive >> u & 1 or not adj[v] >> u & 1:
                raise ValueError(f"step {step}: ({v}, {u}) is not an edge of the current graph")
            branch[u] |= branch.pop(v)
        alive = _contract(adj, alive, v, u)
    labels = [v for v in range(len(masks)) if alive >> v & 1]
    index = {v: i for i, v in enumerate(labels)}
    minor = []
    for i, v in enumerate(labels):
        m = 1 << i
        bits = adj[v]
        while bits:
            bit = bits & -bits
            bits ^= bit
            m |= 1 << index[bit.bit_length() - 1]
        minor.append(m)
    return minor, labels, branch


def check_branch_sets(masks: Sequence[int], minor: Sequence[int], labels: Sequence[int],
                      branch: dict[int, set[int]]) -> None:
    """Independent check of the minor model: the branch sets partition the
    active vertices, each induces a connected subgraph, and minor vertices are
    adjacent exactly when some graph edge joins their branch sets. Raises
    `AssertionError` otherwise."""
    _, alive = _neighbours(masks)
    union: set[int] = set()
    for b in branch.values():
        assert not (union & b), "branch sets overlap"
        union |= b
    assert union <= {v for v in range(len(masks)) if alive >> v & 1}, "branch set outside the graph"
    for b in branch.values():
        start = next(iter(b))
        seen, stack = {start}, [start]
        while stack:
            x = stack.pop()
            for y in b:
                if y not in seen and masks[x] >> y & 1:
                    seen.add(y)
                    stack.append(y)
        assert seen == b, "a branch set is not connected"
    sets = [branch[v] for v in labels]
    bitsets = [sum(1 << x for x in s) for s in sets]
    for i in range(len(labels)):
        reach = 0
        for x in sets[i]:
            reach |= masks[x]
        for j in range(len(labels)):
            if i != j:
                assert bool(reach & bitsets[j]) == bool(minor[i] >> j & 1), "minor edge mismatch"


@dataclass
class MinorConfig:
    """Budgets and shape of the minor ladder.

    The defaults are those of `reports/minor_bound.md`, chosen by
    measurement: the step is skipped below `min_vertices`, where the full
    refutation is cheap, and at each target the descent first probes the full
    graph with `probe_nodes` nodes, so a graph the search settles at once never
    pays for the step. The ladder starts at half the graph and stops at 85%;
    the node budget starts at `first_nodes` on the smallest minor and is
    multiplied by `growth` per size, with `total_nodes` over the whole descent;
    one call (one target) may spend at most `share` of what is left of it;
    under a descent time budget the step stops after `time_fraction` of it.
    When every minor asked runs out at a size, `on_stall="retry"` repeats that
    size with the grown budget (`"stop"` gives up): on the open Rome graphs
    retrying closed 48 more of 94. Before a minor is searched, the descent's
    layout lifted to it, the greedy layout and a restricted search of
    `restrict_nodes` nodes are tried, since a minor that admits width `w` can
    never refute it; on the VSPLIB trees this cut the step's cost by 99%.
    """

    min_vertices: int = 40
    start_fraction: float = 0.5
    step_fraction: float = 0.05
    max_fraction: float = 0.85
    rules: tuple[str, ...] = RULES
    first_nodes: int = 100_000
    growth: float = 3.0
    total_nodes: int = 20_000_000
    time_fraction: float = 0.25
    on_stall: str = "retry"
    probe_nodes: int = 100_000
    share: float = 0.5
    restrict_nodes: int = 20_000

    def sizes(self, n: int, w: int) -> list[int]:
        lo = max(w + 2, math.ceil(self.start_fraction * n))
        hi = int(self.max_fraction * n)
        step = max(2, int(round(self.step_fraction * n)))
        out = []
        m = lo
        while m <= hi and m < n:
            out.append(m)
            m += step
        return out


@dataclass
class MinorCertificate:
    """A refutation on a minor: checkable as `replay(masks, contractions)` plus
    a refutation of `pw <= refuted` on the result."""

    refuted: int
    size: int
    rule: str
    contractions: list
    nodes: int

    def as_dict(self) -> dict:
        return dict(refuted=self.refuted, size=self.size, rule=self.rule,
                    contractions=[list(p) for p in self.contractions], nodes=self.nodes)


@dataclass
class MinorLadder:
    """The minor step's state across one descent: contraction sequences per
    rule, the witness width found on each minor, and the nodes spent."""

    masks: Sequence[int]
    config: MinorConfig = field(default_factory=MinorConfig)
    nodes: int = 0
    seconds: float = 0.0
    calls: int = 0
    log: list = field(default_factory=list)
    _sequences: dict = field(default_factory=dict)
    _upper: dict = field(default_factory=dict)        # (rule, size) -> witness width
    _refuted: dict = field(default_factory=dict)      # (rule, size) -> largest w refuted
    best: "MinorCertificate | None" = None            # the highest lower bound proved
    _cache: dict = field(default_factory=dict)        # (rule, size) -> minor, seq, labels, branch
    _cheap_done: set = field(default_factory=set)
    _restricted: dict = field(default_factory=dict)   # (rule, size) -> lowest w tried restricted

    def _decide(self, minor, k, budget, deadline, note, size, rule, flags):
        from pathwidth.search import decide
        t0 = time.monotonic()
        answer = decide(minor, k, max_nodes=budget, deadline=deadline, **flags)
        dt = time.monotonic() - t0
        self.nodes += answer.nodes
        self.seconds += dt
        self.calls += 1
        self.log.append((k - 1, size, rule, note + answer.status, answer.nodes, round(dt, 3)))
        return answer

    @property
    def n(self) -> int:
        return sum(1 for m in self.masks if m)

    @property
    def applies(self) -> bool:
        return self.n >= self.config.min_vertices

    def _sequence(self, rule: str, size: int) -> list[tuple[int, int]]:
        seq = self._sequences.get(rule)
        need = self.n - size
        if seq is None or len(seq) < need:
            smallest = min(self.config.sizes(self.n, 0) or [size])
            seq = contraction_sequence(self.masks, min(size, smallest), rule)
            self._sequences[rule] = seq
        return seq[:need]

    def minor(self, rule: str, size: int) -> tuple[list[int], list[tuple[int, int]]]:
        key = (rule, size)
        if key not in self._cache:
            seq = self._sequence(rule, size)
            minor, labels, branch = replay(self.masks, seq)
            self._cache[key] = (minor, seq, labels, branch)
        minor, seq, _, _ = self._cache[key]
        return minor, seq

    def cheap_width(self, rule: str, size: int, order: Sequence[int] | None) -> int:
        """A layout width of the minor found without search: the descent's own
        order lifted to the minor, and the greedy order.

        Lifting: close each branch set when its last vertex closes in `order`.
        A minor vertex on the boundary of a prefix of that order has a vertex
        of its (connected) branch set on the boundary of the corresponding
        prefix of `order`, and branch sets are disjoint, so the lifted width
        never exceeds the width of `order`.
        """
        from pathwidth.bounds import greedy_order
        minor, _ = self.minor(rule, size)
        _, _, labels, branch = self._cache[(rule, size)]
        best = vertex_separation_masks(minor, greedy_order(minor))
        if order:
            position = {v: i for i, v in enumerate(order)}
            last = [max(position.get(x, -1) for x in branch[v]) for v in labels]
            lifted = sorted(range(len(labels)), key=lambda i: last[i])
            best = min(best, vertex_separation_masks(minor, lifted))
        return best

    def try_refute(self, w: int, *, deadline: float | None = None, max_nodes: int | None = None,
                   order: Sequence[int] | None = None, **flags: object) -> MinorCertificate | None:
        """Try to prove `pw(G) >= w + 1` on a minor. Returns the certificate,
        or None if no minor within budget refutes `w`. `order`, the descent's
        current layout of the graph, lets most "sat" answers be had for free
        (`cheap_width`)."""
        from pathwidth.search import decide

        cfg = self.config
        n = self.n
        if n < cfg.min_vertices:
            return None
        flags = {k: v for k, v in flags.items() if k not in ("max_nodes", "deadline", "restrict")}
        budget = float(cfg.first_nodes)
        # one call may spend at most `share` of what is left, so a target far
        # above the optimum cannot starve the ones below it
        cap = self.nodes + int(cfg.share * max(0, cfg.total_nodes - self.nodes))
        sizes = cfg.sizes(n, w)
        i = 0
        while i < len(sizes):
            size = sizes[i]
            stalled = asked = 0
            seen: set = set()
            for rule in cfg.rules:
                key = (rule, size)
                minor, seq = self.minor(rule, size)
                if tuple(minor) in seen:
                    continue                      # both rules built the same minor
                seen.add(tuple(minor))
                if self._upper.get(key, n) <= w:
                    continue                      # minor already has a layout of width <= w
                if key not in self._cheap_done:
                    self._cheap_done.add(key)
                    cheap = self.cheap_width(rule, size, order)
                    self._upper[key] = min(self._upper.get(key, n), cheap)
                    if cheap <= w:
                        continue
                remaining = cap - self.nodes
                if max_nodes is not None:
                    remaining = min(remaining, max_nodes)
                if remaining <= 0 or (deadline is not None and time.monotonic() >= deadline):
                    return None
                if cfg.restrict_nodes and self._restricted.get(key, n + 1) > w:
                    # Chu & Stuckey's restricted search finds most layouts in
                    # hundreds of nodes; it never refutes, so it only saves
                    self._restricted[key] = w
                    quick = self._decide(minor, w + 1, min(cfg.restrict_nodes, remaining), deadline,
                                         "restrict:", size, rule, dict(flags, restrict=True))
                    if quick.status == "sat":
                        self._upper[key] = vertex_separation_masks(minor, quick.order)
                        continue
                asked += 1
                t0 = time.monotonic()
                answer = decide(minor, w + 1, max_nodes=int(min(budget, remaining)),
                                deadline=deadline, **flags)
                dt = time.monotonic() - t0
                self.nodes += answer.nodes
                self.seconds += dt
                self.calls += 1
                self.log.append((w, size, rule, answer.status, answer.nodes, round(dt, 3)))
                if answer.status == "unsat":
                    self._refuted[key] = max(w, self._refuted.get(key, -1))
                    cert = MinorCertificate(w, size, rule, list(seq), answer.nodes)
                    if self.best is None or w > self.best.refuted:
                        self.best = cert
                    return cert
                if answer.status == "sat":
                    self._upper[key] = vertex_separation_masks(minor, answer.order)
                else:
                    stalled += 1
            budget *= cfg.growth
            if asked and stalled == asked:
                # every minor asked ran out at this size; bigger minors cost more
                if cfg.on_stall != "retry":
                    return None
                continue                      # the same size, with the grown budget
            i += 1
        return None

    def raise_lower(self, lower: int, *, deadline: float | None = None,
                    max_nodes: int | None = None, **flags: object) -> MinorCertificate | None:
        """Prove minors' exact pathwidth, to raise the lower bound above `lower`.

        A minor that answered "sat" has a witness of value `p`; descending on
        it until a refutation proves its exact value, a lower bound for the
        instance. Minors are taken smallest first, each only while its witness
        is above the best bound so far, so the bound climbs with the size; the
        first budget overrun stops the climb (a larger minor costs more).
        Returns the best certificate held, if it beats `lower`; its
        `refuted + 1` is the bound.
        """
        cfg = self.config
        flags = {f: v for f, v in flags.items() if f not in ("max_nodes", "deadline", "restrict")}
        best = self.best
        cap = self.nodes + int(cfg.share * max(0, cfg.total_nodes - self.nodes))
        floor = max(lower, best.refuted + 1 if best else lower)
        for size, rule in sorted(((s_, r_) for (r_, s_) in self._upper), key=lambda t: t):
            p = self._upper[(rule, size)]
            minor, seq = self.minor(rule, size)
            stop = False
            while p > floor:
                if self._refuted.get((rule, size), -1) >= p - 1:
                    best, floor = MinorCertificate(p - 1, size, rule, list(seq), 0), p
                    break
                remaining = cap - self.nodes
                if max_nodes is not None:
                    remaining = min(remaining, max_nodes)
                if remaining <= 0 or (deadline is not None and time.monotonic() >= deadline):
                    stop = True
                    break
                if cfg.restrict_nodes:
                    quick = self._decide(minor, p, min(cfg.restrict_nodes, int(remaining)), deadline,
                                         "restrict:", size, rule, dict(flags, restrict=True))
                    if quick.status == "sat":
                        p = min(p - 1, vertex_separation_masks(minor, quick.order))
                        self._upper[(rule, size)] = p
                        continue
                    remaining = cap - self.nodes
                    if max_nodes is not None:
                        remaining = min(remaining, max_nodes)
                    if remaining <= 0:
                        stop = True
                        break
                # what is left of this call's share: minors come smallest
                # first, and the first overrun ends the climb
                budget = int(remaining)
                answer = self._decide(minor, p, budget, deadline, "lower:", size, rule, flags)
                if answer.status == "unsat":
                    self._refuted[(rule, size)] = p - 1
                    best, floor = MinorCertificate(p - 1, size, rule, list(seq), answer.nodes), p
                    break
                if answer.status != "sat":
                    stop = True
                    break
                p = min(p - 1, vertex_separation_masks(minor, answer.order))
                self._upper[(rule, size)] = p
            if stop:
                break
        self.best = best
        return best if best is not None and best.refuted + 1 > lower else None
