"""Upper and lower bounds on pathwidth, in mask form.

Both sides matter to the descent in `solve.py`: the upper bound is where it
starts, and each vertex it saves is a whole decision the descent never makes;
the lower bound is where it may stop without a refutation, which on easy
instances is most of them.

Lower bounds are minor-monotone facts: `pw(G) >= tw(G) >= δ(H)` for every
minor `H` of `G`. `degeneracy` takes `H` over subgraphs (exact, linear time);
`contraction_degeneracy` over contractions found greedily (the MMD+ heuristic;
= LB5 of Yanasse, Becceneri & Soma 1999, and the same bound the MOSP project's
`_contraction_degeneracy` computes). The clique bound `ω(G) − 1` is dominated
by degeneracy and not computed separately.

A lower bound that is too high makes the descent stop above the optimum and
report a wrong width that the witness would not contradict, so these are
correctness dependencies; `tests/test_solve.py` checks them against brute
force.
"""

from __future__ import annotations

from collections.abc import Sequence


def _popcount(x: int) -> int:
    return x.bit_count()


def greedy_order(masks: Sequence[int]) -> list[int]:
    """Greedy closing order: at each step close the vertex that leaves the
    smallest boundary, ties by index (Coudert et al.'s greedy step; the first
    leaf of the search's fan order)."""
    n = len(masks)
    active = [v for v in range(n) if masks[v]]
    full = 0
    for v in active:
        full |= 1 << v
    closed = opened = 0
    order: list[int] = []
    while closed != full:
        best_v, best_w = -1, n + 1
        bits = full & ~closed
        while bits:
            bit = bits & -bits
            bits ^= bit
            v = bit.bit_length() - 1
            w = _popcount((opened | masks[v]) & ~(closed | bit))
            if w < best_w:
                best_w, best_v = w, v
        order.append(best_v)
        closed |= 1 << best_v
        opened |= masks[best_v]
    return order


def degeneracy(masks: Sequence[int]) -> int:
    """`max_H δ(H)` over subgraphs: repeatedly delete a minimum-degree vertex."""
    n = len(masks)
    alive = 0
    for v in range(n):
        if masks[v]:
            alive |= 1 << v
    best = 0
    while alive:
        best_v, best_d = -1, n + 1
        bits = alive
        while bits:
            bit = bits & -bits
            bits ^= bit
            v = bit.bit_length() - 1
            d = _popcount(masks[v] & alive & ~bit)
            if d < best_d:
                best_d, best_v = d, v
        if best_d > best:
            best = best_d
        alive &= ~(1 << best_v)
    return best


def contraction_degeneracy(masks: Sequence[int], max_vertices: int = 400) -> int:
    """MMD+ (least-c): repeatedly record the minimum degree, then contract that
    vertex into the neighbour with which it shares fewest neighbours. The
    largest minimum degree seen is a lower bound on treewidth, hence pathwidth.
    Returns `degeneracy(masks)` when the graph is too large for the O(n^3)."""
    n = len(masks)
    if n > max_vertices:
        return degeneracy(masks)
    adj = [masks[v] & ~(1 << v) for v in range(n)]
    alive = 0
    for v in range(n):
        if masks[v]:
            alive |= 1 << v
    best = 0
    while _popcount(alive) > 1:
        best_v, best_d = -1, n + 1
        bits = alive
        while bits:
            bit = bits & -bits
            bits ^= bit
            v = bit.bit_length() - 1
            d = _popcount(adj[v] & alive)
            if d < best_d:
                best_d, best_v = d, v
        if best_d > best:
            best = best_d
        v = best_v
        nbrs = adj[v] & alive
        if not nbrs:
            alive &= ~(1 << v)
            continue
        # least-c: the neighbour sharing the fewest common neighbours with v
        u, fewest = -1, n + 1
        bits = nbrs
        while bits:
            bit = bits & -bits
            bits ^= bit
            c = bit.bit_length() - 1
            common = _popcount(adj[c] & nbrs)
            if common < fewest:
                fewest, u = common, c
        # contract v into u
        merged = (adj[u] | adj[v]) & ~((1 << u) | (1 << v))
        adj[u] = merged
        bits = merged & alive
        while bits:
            bit = bits & -bits
            bits ^= bit
            w = bit.bit_length() - 1
            adj[w] = (adj[w] | (1 << u)) & ~(1 << v)
        alive &= ~(1 << v)
    return best


def lower_bound(masks: Sequence[int]) -> int:
    """The best cheap lower bound on pathwidth: contraction degeneracy."""
    if not any(masks):
        return 0
    return max(degeneracy(masks), contraction_degeneracy(masks))
