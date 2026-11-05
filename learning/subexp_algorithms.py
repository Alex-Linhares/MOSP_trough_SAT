"""Exact algorithms by exact linear transformation, unconditional
(loop0014 item 07, `reports/subexp_pathwidth.md` §7).

Everything here is an algorithm with a stated running time, run against
brute force on every graph of the networkx atlas (all graphs to 7 vertices)
and on generated graphs; the checks write their log under
`reports/scratch/subexp_pathwidth/07_algorithms/`.

    python -m learning.subexp_algorithms            # the full check, atlas to 7
    python -m learning.subexp_algorithms --nmax 5   # quick

Graphs are `(n, adj)` as in `paper1/complex_check.py`. `vs` is Kinnersley's
vertex separation (`vs = pw`); `cw` is cutwidth (edges crossing a gap).

(a) **The line graph carries cutwidth to vertex separation** (Theorem 7.1):
    `cw(G) ≤ vs(L(G)) ≤ cw(G) + max(0, ⌊Δ/2⌋ − 1)`, with equality for
    `Δ ≤ 3`; both layout maps are explicit (`vertex_layout_from_line_layout`,
    `line_layout_from_vertex_layout`). `L(G)` has `m` vertices, against the
    `2m` ports of item 03's expansion `G°` (`L(G) = G° / matching`). So any
    vertex-separation algorithm in `O*(c^N)` computes the cutwidth of a graph
    of maximum degree 3 in `O*(c^m)`: with Kitsunai et al.'s `O(1.89^N)`,
    `O(1.89^m) = O(1.89^{(m/n) n})`, below `2^n` iff `m/n < log 2 / log 1.89
    = 1.0888` (Algorithm 7.2, `cutwidth_subcubic`). The converse direction
    (`vs(G)` as the cutwidth of a linear-size graph) is explored, not found:
    `converse_exploration` tabulates `cw(T(G)) − vs(G)` for six candidate
    `T` over the subcubic atlas graphs.
(b) Item 04's algorithms with witnesses: `cobipartite_vs` in
    `O*(2^{max(a, b)})` (Theorem 4.1), `twin_vs` in `O*(2^u)` over the `u`
    twin classes (Theorem 4.4) and its MOSP form `mosp_twin` (equivalent
    customers), `starlike_pathwidth` in `O(4^{α₀} r + n)` (Gustedt 1993
    Algorithm 6.3 / Theorem 6.4, implemented from the paper with a witness
    decomposition), `2^{O(√n)}` when the centre has `≤ √n` vertices.
(c) `edge_search_equals_cutwidth_subcubic`: `es(G) = cw(G)` on every subcubic
    atlas graph with `n + 2m ≤ 20` (edge search by EST 1994 Thm 2.2,
    `es = vs(2-expansion)`): a *checked* statement, attributed to Makedon &
    Sudborough 1989 (not held), not a theorem of ours.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import random
import sys
import time
from collections import Counter
from functools import lru_cache
from pathlib import Path

from learning.subexp_classes import twin_classes
from learning.subexp_reductions import atlas, degree_clique_expansion, is_cobipartite, vs
from paper1.complex_check import (cutwidth_dp, cutwidth_of_layout, edges_of, graph, two_expansion,
                                  vs_of_layout)

OUT = Path("reports/scratch/subexp_pathwidth/07_algorithms")
INF = 10 ** 9
LOG_189_2 = math.log(2) / math.log(1.89)       # 1.0888…: the m/n threshold of Algorithm 7.2


def popcount(x: int) -> int:
    return bin(x).count("1")


def bits(x: int):
    while x:
        b = x & -x
        yield b.bit_length() - 1
        x ^= b


def max_degree(g) -> int:
    return max((popcount(a) for a in g[1]), default=0)


# ----------------------------------------------------------------------------
# a vertex-separation DP with a witness layout (pure Python, to ~16 vertices)
# ----------------------------------------------------------------------------


def vs_layout(g) -> tuple[int, list[int]]:
    """`(vs, layout)` by the prefix-set DP `f(S) = max(cost(S), min_v f(S ∖ v))`
    with argmin pointers; `cost(S)` = vertices of `S` with a neighbour outside."""
    n, adj = g
    if n == 0:
        return 0, []
    full = (1 << n) - 1
    f = [INF] * (1 << n)
    last = [-1] * (1 << n)
    f[0] = 0
    for S in range(1, 1 << n):
        cost = 0 if S == full else sum(1 for v in bits(S) if adj[v] & ~S)
        best, arg = INF, -1
        for v in bits(S):
            x = f[S & ~(1 << v)]
            if x < best:
                best, arg = x, v
        f[S] = max(best, cost)
        last[S] = arg
    order, S = [], full
    while S:
        v = last[S]
        order.append(v)
        S &= ~(1 << v)
    order.reverse()
    return f[full], order


# ----------------------------------------------------------------------------
# (a) the line graph and the two layout maps
# ----------------------------------------------------------------------------


def line_graph(g):
    """`L(G)`: a vertex per edge, two adjacent iff the edges share an endpoint.
    Returns `(L, edges)` with `edges[i]` the edge that is vertex `i` of `L`."""
    es = edges_of(g)
    new = []
    for i in range(len(es)):
        for j in range(i + 1, len(es)):
            if set(es[i]) & set(es[j]):
                new.append((i, j))
    return graph(len(es), new), es


def vertex_layout_from_line_layout(g, es, lorder) -> list[int]:
    """Order the vertices of `G` by the position of their *last* incident edge
    in the layout `lorder` of `L(G)`; isolated vertices go last. Theorem 7.1
    (`≤`): the cutwidth of this order is at most `vs` of `lorder`."""
    n, adj = g
    pos = {e: p for p, e in enumerate(lorder)}
    lastpos = [-1] * n
    for i, (u, v) in enumerate(es):
        lastpos[u] = max(lastpos[u], pos[i])
        lastpos[v] = max(lastpos[v], pos[i])
    # Vertices in order of completion (the position of their last edge).
    # Only the two endpoints `u, w` of a common last edge `e` can tie. With
    # `P` the vertices completed before `e`: `u` goes first iff `u` has a
    # neighbour in `P` or `w` has a neighbour outside `P ∪ {u, w}` (then the
    # cut after `P ∪ {u}` is within the L-cut before `e`: Theorem 7.1 (i));
    # otherwise `w` goes first, which works unless `uw` is a whole component.
    by_last = sorted((v for v in range(n) if lastpos[v] >= 0), key=lambda v: lastpos[v])
    order, i = [], 0
    while i < len(by_last):
        u = by_last[i]
        if i + 1 < len(by_last) and lastpos[by_last[i + 1]] == lastpos[u]:
            w = by_last[i + 1]
            P = sum(1 << x for x in by_last[:i])
            outside = ~(P | (1 << u) | (1 << w))
            if adj[u] & P or adj[w] & outside:
                order += [u, w]
            else:
                order += [w, u]
            i += 2
        else:
            order.append(u)
            i += 1
    return order + [v for v in range(n) if lastpos[v] < 0]


def line_layout_from_vertex_layout(g, es, order) -> list[int]:
    """Order the edges by (position of the left endpoint, position of the
    right endpoint). Theorem 7.1 (`≥`): `vs` of this layout is at most the
    cutwidth of `order` plus `max(0, ⌊Δ/2⌋ − 1)`, and at most it for `Δ ≤ 3`."""
    pos = {v: p for p, v in enumerate(order)}
    key = []
    for i, (u, v) in enumerate(es):
        a, b = sorted((pos[u], pos[v]))
        key.append((a, b, i))
    return [i for _, _, i in sorted(key)]


def cutwidth_subcubic(g, vs_algorithm=vs_layout) -> tuple[int, list[int]]:
    """Algorithm 7.2: the cutwidth of a graph of maximum degree ≤ 3 with a
    witness layout, by one run of a vertex-separation algorithm on `L(G)`
    (`m` vertices). With `vs_algorithm` the `O*(2^N)` DP this is `O*(2^m)`;
    with Kitsunai et al. (2016) it would be `O(1.89^m)`. For `Δ ≥ 4` the
    returned value is `max(vs(L(G')), [a single edge was set aside])`, an
    upper bound on `cw(G)` within `⌊Δ/2⌋ − 1`."""
    n, adj = g
    if n <= 1:
        return 0, list(range(n))
    # single-edge components (and isolated vertices) are laid out last: a
    # component `K₂` has cutwidth 1 and an edgeless line graph (Theorem 7.1
    # (i) excludes it); the cutwidth of a disjoint union is the maximum.
    k2 = []                                       # the single-edge components, each pair consecutive
    for v in range(n):
        if popcount(adj[v]) == 1:
            w = adj[v].bit_length() - 1
            if v < w and popcount(adj[w]) == 1:
                k2 += [v, w]
    iso = [v for v in range(n) if adj[v] == 0]
    tail = set(k2) | set(iso)
    core = [v for v in range(n) if v not in tail]
    if not core:
        return (1 if k2 else 0), k2 + iso
    sub = graph(len(core), [(core.index(u), core.index(w)) for u, w in edges_of(g) if u in core and w in core])
    L, es = line_graph(sub)
    value, lorder = vs_algorithm(L)
    order = [core[v] for v in vertex_layout_from_line_layout(sub, es, lorder)]
    if k2:
        value = max(value, 1)
    return value, order + k2 + iso


def base_per_vertex(ratio_m_over_n: float, c: float = 1.89) -> float:
    """`c^{m/n}`: the base of Algorithm 7.2 per vertex of `G`."""
    return c ** ratio_m_over_n


def base_table(c: float = 1.89) -> list[dict]:
    rows = []
    for name, r in (("forest, m = n − 1", 1.0), ("threshold", LOG_189_2), ("m = 1.2 n", 1.2),
                    ("m = 1.25 n (e.g. 2.5-regular)", 1.25), ("cubic, m = 1.5 n", 1.5),
                    ("expansion G°, 2m = 3n (item 03)", 3.0)):
        rows.append({"case": name, "m_over_n": round(r, 4), "base": round(base_per_vertex(r, c), 4),
                     "below_2": base_per_vertex(r, c) < 2})
    return rows


# ----------------------------------------------------------------------------
# (a') the converse direction: candidates for `T` with `cw(T(G)) = vs(G) + c`
# ----------------------------------------------------------------------------


def hub_transform(g):
    """`v` becomes `v — h_v`; every edge `uw` becomes `h_u — h_w`. `2n` vertices."""
    n, adj = g
    new = [(v, n + v) for v in range(n)]
    new += [(n + u, n + w) for u, w in edges_of(g)]
    return graph(2 * n, new)


def cross_hub_transform(g):
    """`v — h_v`; every edge `uw` becomes `h_u — w` and `u — h_w`. `2n` vertices."""
    n, adj = g
    new = [(v, n + v) for v in range(n)]
    for u, w in edges_of(g):
        new += [(n + u, w), (u, n + w)]
    return graph(2 * n, new)


def subdivision(g):
    """Every edge subdivided once. `n + m` vertices."""
    n, adj = g
    es = edges_of(g)
    new = []
    for i, (u, v) in enumerate(es):
        new += [(u, n + i), (n + i, v)]
    return graph(n + len(es), new)


def pendant_double(g):
    """`G` plus a pendant vertex on every vertex. `2n` vertices."""
    n, adj = g
    return graph(2 * n, edges_of(g) + [(v, n + v) for v in range(n)])


CONVERSE_CANDIDATES = {
    "identity G": lambda g: g,
    "line graph L(G)": lambda g: line_graph(g)[0],
    "hub (v-h_v, h_u-h_w)": hub_transform,
    "cross hub (v-h_v, h_u-w, u-h_w)": cross_hub_transform,
    "1-subdivision": subdivision,
    "pendant double": pendant_double,
    "degree-clique expansion G°": degree_clique_expansion,
}


def converse_exploration(nmax: int = 7, max_target: int = 14, log=print) -> dict:
    """For every subcubic atlas graph to `nmax` vertices and every candidate
    `T`, the distribution of `cw(T(G)) − vs(G)` (target graphs with more than
    `max_target` vertices are skipped and counted). A constant difference on
    every graph would be a converse; none of the candidates gives one."""
    out = {}
    gs = [g for g in atlas(nmax) if max_degree(g) <= 3 and g[0] >= 2]
    for name, T in CONVERSE_CANDIDATES.items():
        diff, skipped = Counter(), 0
        for g in gs:
            t = T(g)
            if t[0] > max_target:
                skipped += 1
                continue
            diff[cutwidth_dp(t) - vs(g)] += 1
        out[name] = {"diff": {str(k): v for k, v in sorted(diff.items())}, "skipped": skipped,
                     "graphs": len(gs) - skipped, "constant": len(diff) == 1}
        log(f"  {name:36s} cw(T) − vs(G): {dict(sorted(diff.items()))}  "
            f"(skipped {skipped} with > {max_target} vertices)")
    return out


# ----------------------------------------------------------------------------
# (b1) cobipartite vertex separation in O*(2^{max(a, b)}) with a witness
# ----------------------------------------------------------------------------


def chain_layout(g, X: int, Y: int) -> tuple[int, list[int]]:
    """`(chain_X, τ)`: the DP of §4.1 over suffix sets of `Y` with argmin
    pointers. `f(S) = max(|Y| − |S| + |N_X(S)|, min_{v ∈ S} f(S ∖ v))`,
    `f(∅) = 0`; `τ` reads the argmins from `S = Y` downward (the argmin at `S`
    is the first vertex of the suffix `S`)."""
    n, adj = g
    y = popcount(Y)
    if y == 0:
        return 0, []
    f = {0: 0}
    first = {}
    # iterate subsets of Y by increasing size
    ys = list(bits(Y))
    for size in range(1, y + 1):
        for comb in itertools.combinations(ys, size):
            S = 0
            for v in comb:
                S |= 1 << v
            nx = 0
            for v in comb:
                nx |= adj[v]
            cost = y - size + popcount(nx & X)
            best, arg = INF, -1
            for v in comb:
                x = f[S & ~(1 << v)]
                if x < best:
                    best, arg = x, v
            f[S] = max(cost, best)
            first[S] = arg
    tau, S = [], Y
    while S:
        v = first[S]
        tau.append(v)
        S &= ~(1 << v)
    return f[Y], tau


def cobipartite_vs(g, A: int, B: int) -> tuple[int, list[int]]:
    """Algorithm 7.3: `(vs(H), layout)` for `H` cobipartite with cliques `A`,
    `B`, by Theorem 4.1: `vs = min_X max(|X| − 1, chain_X)`, layout `X` (any
    order) then `τ`. Time `O*(2^a + 2^b) = O*(2^{max(a, b)})`."""
    best = (INF, None)
    for X, Y in ((A, B), (B, A)):
        if X == 0:
            continue
        c, tau = chain_layout(g, X, Y)
        val = max(popcount(X) - 1, c)
        if val < best[0]:
            best = (val, list(bits(X)) + tau)
    return best


def random_cobipartite(a: int, b: int, p: float, rng: random.Random):
    es = [(i, j) for i in range(a) for j in range(i + 1, a)]
    es += [(a + i, a + j) for i in range(b) for j in range(i + 1, b)]
    es += [(i, a + j) for i in range(a) for j in range(b) if rng.random() < p]
    return graph(a + b, es), (1 << a) - 1, ((1 << b) - 1) << a


# ----------------------------------------------------------------------------
# (b2) vertex separation over twin classes in O*(2^u), and the MOSP form
# ----------------------------------------------------------------------------


def _cut(adj, placed: int) -> int:
    return sum(1 for v in bits(placed) if adj[v] & ~placed)


def _block_cost(adj, P: int, Q: int) -> int:
    best, cur = 0, P
    for v in bits(Q):
        cur |= 1 << v
        best = max(best, _cut(adj, cur))
    return best


def twin_vs(g) -> tuple[int, list[int], int]:
    """Algorithm 7.4: `(vs, layout, u)` by the DP over subsets of twin
    classes (Theorem 4.4: every class consecutive in some optimal layout;
    the internal order of a class is free). Time `O*(2^u)`."""
    n, adj = g
    if n <= 1:
        return 0, list(range(n)), n
    classes = twin_classes(g)
    u = len(classes)
    f = [INF] * (1 << u)
    last = [-1] * (1 << u)
    f[0] = 0
    union = [0] * (1 << u)
    for S in range(1, 1 << u):
        i0 = (S & -S).bit_length() - 1
        union[S] = union[S & (S - 1)] | classes[i0]
    for S in range(1, 1 << u):
        best, arg = INF, -1
        for i in bits(S):
            rest = S & ~(1 << i)
            val = max(f[rest], _block_cost(adj, union[rest], classes[i]))
            if val < best:
                best, arg = val, i
        f[S], last[S] = best, arg
    order, S = [], (1 << u) - 1
    while S:
        i = last[S]
        order = list(bits(classes[i])) + order
        S &= ~(1 << i)
    return f[(1 << u) - 1], order, u


def mosp_graph(matrix):
    """Customers adjacent iff they share a pattern (`M Mᵀ` off the diagonal)."""
    rows = [sum(1 << j for j, x in enumerate(r) if x) for r in matrix]
    n = len(rows)
    es = [(i, j) for i in range(n) for j in range(i + 1, n) if rows[i] & rows[j]]
    return graph(n, es), rows


def pattern_order_from_layout(rows, m: int, order: list[int]) -> list[int]:
    """Patterns by the position of their last customer in `order` (then by
    their first customer, then index); patterns with no customer last."""
    pos = {c: p for p, c in enumerate(order)}
    key = []
    for j in range(m):
        cs = [pos[i] for i in range(len(rows)) if rows[i] >> j & 1]
        key.append((not cs, max(cs, default=0), min(cs, default=0), j))
    return [j for *_, j in sorted(key)]


def open_stacks_of_order(matrix, porder: list[int]) -> int:
    """Simulation: a customer's stack is open from its first to its last pattern."""
    rows = [sum(1 << j for j, x in enumerate(r) if x) for r in matrix]
    first, last = {}, {}
    for p, j in enumerate(porder):
        for i, r in enumerate(rows):
            if r >> j & 1:
                first.setdefault(i, p)
                last[i] = p
    best = 0
    for p in range(len(porder)):
        best = max(best, sum(1 for i in first if first[i] <= p <= last[i]))
    return best


def mosp_twin(matrix) -> tuple[int, list[int], int]:
    """Algorithm 7.5 (equivalent customers): `(mosp, pattern order, u)` —
    `mosp = vs(MOSP graph) + 1` (the Lean theorem), the vertex separation by
    Algorithm 7.4 over the `u` twin classes of the MOSP graph, which contain
    the classes of customers with equal pattern sets; the pattern order is
    read from the customer layout by last customer. Time `O*(2^u)`."""
    m = len(matrix[0]) if matrix else 0
    if not matrix or m == 0:
        return 0, list(range(m)), 0
    g, rows = mosp_graph(matrix)
    v, order, u = twin_vs(g)
    porder = pattern_order_from_layout(rows, m, order)
    return v + 1, porder, u


# ----------------------------------------------------------------------------
# (b3) starlike chordal graphs: Gustedt's Algorithm 6.3 with a witness
# ----------------------------------------------------------------------------


def starlike_graph(alpha0: int, cliques: list[tuple[int, int]]):
    """The starlike graph with centre `C = {0, …, α₀ − 1}` and peripheral
    cliques `(c_i, β_i)`: `c_i ⊆ C` a bitmask (the central part), `β_i ≥ 1`
    private vertices numbered after the centre. Returns `(g, C, specs)` with
    `specs[i] = (c_i, R_i)` as bitmasks."""
    es = [(i, j) for i in range(alpha0) for j in range(i + 1, alpha0)]
    specs, nxt = [], alpha0
    for c, beta in cliques:
        R = list(range(nxt, nxt + beta))
        nxt += beta
        members = list(bits(c)) + R
        es += [(x, y) for x, y in itertools.combinations(members, 2) if x >= alpha0 or y >= alpha0]
        specs.append((c, sum(1 << r for r in R)))
    return graph(nxt, es), (1 << alpha0) - 1, specs


def starlike_pathwidth(C: int, specs: list[tuple[int, int]]) -> tuple[int, list[int], list[int]]:
    """Algorithm 7.6 = Gustedt (1993) Algorithm 6.3 with a witness: `(pw,
    layout, bags)` for the starlike graph with centre `C` and peripheral
    cliques `(c_i, R_i)`. The cliques are processed in decreasing `|R_i|`;
    a state `(S⁻, S⁺)` is the pair of unions of central parts on the two
    sides of `C`; placing clique `i` next to `C` on the left makes a bag
    `R_i ∪ S⁻` with `S⁻ ⊇ c_i` (Lemma 6.2). `pw = max(|C|, min_{S⁻,S⁺}
    Opt_r) − 1`. Time `O(4^{α₀} r)` table updates (`α₀ = |C|`); the layout
    orders the vertices by first bag (Kinnersley's direction)."""
    alpha0 = popcount(C)
    idx = sorted(range(len(specs)), key=lambda i: -popcount(specs[i][1]))
    opt = {(0, 0): 0}
    parents = []                                   # per stage: state -> (prev state, side)
    for i in idx:
        c, R = specs[i]
        beta = popcount(R)
        new, par = {}, {}
        for (tm, tp), val in opt.items():
            sm = tm | c
            v = max(val, popcount(sm) + beta)
            if v < new.get((sm, tp), INF):
                new[(sm, tp)] = v
                par[(sm, tp)] = ((tm, tp), "L")
            sp = tp | c
            v = max(val, popcount(sp) + beta)
            if v < new.get((tm, sp), INF):
                new[(tm, sp)] = v
                par[(tm, sp)] = ((tm, tp), "R")
        opt, parents_i = new, par
        parents.append(parents_i)
    state = min(opt, key=lambda s: opt[s])
    width = max(alpha0, opt[state]) if specs else alpha0
    # reconstruct sides: processing order idx; side of each clique
    side = {}
    for stage in range(len(idx) - 1, -1, -1):
        prev, s = parents[stage][state]
        side[idx[stage]] = s
        state = prev
    left = [i for i in idx if side[i] == "L"]        # far from C → near, in processing order
    right = [i for i in idx if side[i] == "R"]       # processing order; near C is the last
    bags, acc = [], 0
    for i in left:
        acc |= specs[i][0]
        bags.append(specs[i][1] | acc)
    bags.append(C)
    rbags, acc = [], 0
    for i in right:
        acc |= specs[i][0]
        rbags.append(specs[i][1] | acc)
    bags += rbags[::-1]                              # near C first
    seen, layout = 0, []
    for b in bags:
        for v in bits(b & ~seen):
            layout.append(v)
        seen |= b
    return width - 1, layout, bags


def all_starlike(nmax: int):
    """Every starlike graph to `nmax` vertices up to the obvious symmetries:
    centre size `α₀ ≥ 1`, peripheral cliques `(c_i, β_i)` with `c_i ⊊ C`,
    `β_i ≥ 1`, listed as a multiset, `Σ β_i = n − α₀`."""
    for n in range(1, nmax + 1):
        for alpha0 in range(1, n + 1):
            rest = n - alpha0
            cs = list(range(0, (1 << alpha0) - 1))     # proper subsets of C
            # compositions of `rest` into parts ≥ 1, each part with a central part
            def comps(k):
                if k == 0:
                    yield ()
                    return
                for first in range(1, k + 1):
                    for tail in comps(k - first):
                        yield (first,) + tail
            seen = set()
            for comp in comps(rest):
                for cents in itertools.product(cs, repeat=len(comp)):
                    key = tuple(sorted(zip(cents, comp)))
                    if key in seen:
                        continue
                    seen.add(key)
                    yield alpha0, list(key)


def random_starlike(n: int, alpha0: int, rng: random.Random):
    rest, cliques = n - alpha0, []
    while rest > 0:
        beta = rng.randint(1, min(rest, 3))
        c = rng.randrange(0, (1 << alpha0) - 1)
        cliques.append((c, beta))
        rest -= beta
    return alpha0, cliques


# ----------------------------------------------------------------------------
# (c) edge search against cutwidth on subcubic graphs
# ----------------------------------------------------------------------------


def edge_search_via_two_expansion(g) -> int:
    """EST 1994 Thm 2.2: `es(G) = vs(G₂)`, `G₂` every edge subdivided twice."""
    return vs(two_expansion(g))


# ----------------------------------------------------------------------------
# the checks
# ----------------------------------------------------------------------------


def run_checks(nmax: int = 7, out_dir: Path = OUT, log=print, seed: int = 7,
               random_cobip: int = 200, random_star: int = 200, converse: bool = True) -> dict:
    t0 = time.time()
    out_dir.mkdir(parents=True, exist_ok=True)
    res: dict = {"nmax": nmax}
    gs = atlas(nmax)
    rng = random.Random(seed)

    # (a) Theorem 7.1 on every atlas graph: both inequalities, both layout maps
    log(f"[a] line graph: {len(gs)} atlas graphs to {nmax} vertices")
    fail_lower = fail_upper = fail_eq3 = fail_map_down = fail_map_up = 0
    excess, checked, by_delta = Counter(), 0, Counter()
    with_k2, k2_fail = 0, 0
    for g in gs:
        n, adj = g
        es = edges_of(g)
        if not es or len(es) > 14:
            continue
        has_k2 = any(popcount(adj[v]) == 1 and popcount(adj[adj[v].bit_length() - 1]) == 1 for v in range(n))
        L, _ = line_graph(g)
        c = cutwidth_dp(g)
        vl, lorder = vs_layout(L)
        d = max_degree(g)
        exc = vl - c
        if exc > max(0, d // 2 - 1):
            fail_upper += 1                     # (ii) holds for every graph
        if has_k2:
            with_k2 += 1
            if c > max(1, vl):
                k2_fail += 1
            continue
        checked += 1
        excess[(d, exc)] += 1
        by_delta[d] += 1
        if vl < c:
            fail_lower += 1
        if d <= 3 and exc != 0:
            fail_eq3 += 1
        # the map L-layout → vertex layout realises cw ≤ vs(L-layout)
        order = vertex_layout_from_line_layout(g, es, lorder)
        if cutwidth_of_layout(g, order) > vl:
            fail_map_down += 1
        # the map vertex layout → L-layout realises vs ≤ cw + excess, exactly for Δ ≤ 3
        best_vorder = None
        for perm in itertools.permutations(range(n)):      # an optimal cutwidth layout
            if cutwidth_of_layout(g, perm) == c:
                best_vorder = list(perm)
                break
        lo = line_layout_from_vertex_layout(g, es, best_vorder)
        if vs_of_layout(L, lo) > c + max(0, d // 2 - 1):
            fail_map_up += 1
    res["a_line_graph"] = {"checked_without_K2_component": checked, "with_K2_component": with_k2,
                           "fail_K2_case_cw_le_max_1_vsL": k2_fail,
                           "fail_lower": fail_lower, "fail_upper": fail_upper,
                           "fail_equality_delta_le_3": fail_eq3, "fail_map_line_to_vertex": fail_map_down,
                           "fail_map_vertex_to_line": fail_map_up,
                           "excess_by_delta": {f"delta={d}": {str(e): v for (dd, e), v in sorted(excess.items()) if dd == d}
                                               for d in sorted(by_delta)}}
    log(f"  checked {checked} without a K₂ component ({with_k2} with one: cw ≤ max(1, vs(L)) failures {k2_fail}); "
        f"cw ≤ vs(L) failures {fail_lower}; excess bound failures {fail_upper}; "
        f"equality (Δ ≤ 3) failures {fail_eq3}; map failures {fail_map_down} / {fail_map_up}")
    log(f"  excess vs(L) − cw by Δ: {res['a_line_graph']['excess_by_delta']}")

    # Algorithm 7.2 on every subcubic atlas graph, against cutwidth_dp, with the witness simulated
    sub = [g for g in gs if max_degree(g) <= 3]
    fail_alg, fail_wit = 0, 0
    for g in sub:
        c = cutwidth_dp(g)
        v, order = cutwidth_subcubic(g)
        if v != c:
            fail_alg += 1
        if cutwidth_of_layout(g, order) != c:
            fail_wit += 1
    res["a_algorithm_7_2"] = {"subcubic": len(sub), "fail_value": fail_alg, "fail_witness": fail_wit}
    log(f"  Algorithm 7.2 on {len(sub)} subcubic graphs: value failures {fail_alg}, witness failures {fail_wit}")
    res["a_base_table"] = base_table()
    for r in res["a_base_table"]:
        log(f"  base: {r}")

    if converse:
        log("[a'] converse candidates on the subcubic atlas graphs")
        res["a_converse"] = converse_exploration(nmax, log=log)

    # (b1) cobipartite: every cobipartition of every cobipartite atlas graph, plus random
    log("[b1] cobipartite vertex separation")
    from learning.subexp_classes import cobipartitions
    cob = [g for g in gs if is_cobipartite(g)]
    checked = fail_val = fail_wit = 0
    for g in cob:
        v = vs(g)
        for A, B in cobipartitions(g):
            checked += 1
            val, order = cobipartite_vs(g, A, B)
            if val != v:
                fail_val += 1
            if sorted(order) != list(range(g[0])) or vs_of_layout(g, order) != v:
                fail_wit += 1
    rchecked = rfail = 0
    for _ in range(random_cobip):
        a = rng.randint(1, 6)
        b = rng.randint(a, 12 - a)
        g, A, B = random_cobipartite(a, b, rng.choice((0.2, 0.4, 0.6, 0.8)), rng)
        v = vs(g)
        val, order = cobipartite_vs(g, A, B)
        rchecked += 1
        if val != v or vs_of_layout(g, order) != v:
            rfail += 1
    res["b1_cobipartite"] = {"atlas_graphs": len(cob), "partitions": checked, "fail_value": fail_val,
                             "fail_witness": fail_wit, "random": rchecked, "random_fail": rfail}
    log(f"  {len(cob)} cobipartite atlas graphs, {checked} partitions: value failures {fail_val}, "
        f"witness failures {fail_wit}; random (a + b ≤ 12): {rchecked}, failures {rfail}")

    # (b2) twin DP with witness on every atlas graph; MOSP form on random matrices with duplicate rows
    log("[b2] twin-class vertex separation and the MOSP form")
    from learning.subexp_reductions import mosp_subset_dp
    fail_val = fail_wit = fewer = 0
    for g in gs:
        v = vs(g)
        val, order, u = twin_vs(g)
        fewer += u < g[0]
        if val != v:
            fail_val += 1
        if sorted(order) != list(range(g[0])) or vs_of_layout(g, order) != v:
            fail_wit += 1
    mchecked = mfail = mwit = 0
    for _ in range(300):
        rows, cols = rng.randint(2, 7), rng.randint(2, 8)
        base = [[rng.randint(0, 1) for _ in range(cols)] for _ in range(rows)]
        matrix = [list(base[rng.randrange(rows)]) if rng.random() < 0.4 else base[i] for i in range(rows)]
        if not any(any(r) for r in matrix):
            continue
        ref = mosp_subset_dp(matrix)
        val, porder, u = mosp_twin(matrix)
        mchecked += 1
        if val != ref:
            mfail += 1
        if sorted(porder) != list(range(cols)) or open_stacks_of_order(matrix, porder) != ref:
            mwit += 1
    res["b2_twins"] = {"atlas": len(gs), "fail_value": fail_val, "fail_witness": fail_wit,
                       "graphs_with_fewer_classes": fewer, "mosp_matrices": mchecked,
                       "mosp_fail_value": mfail, "mosp_fail_witness": mwit}
    log(f"  atlas: value failures {fail_val}, witness failures {fail_wit} ({fewer} graphs have u < n); "
        f"MOSP matrices {mchecked}: value failures {mfail}, pattern-order failures {mwit}")

    # (b3) starlike: every starlike graph to nmax vertices, plus random to 14
    log("[b3] starlike pathwidth (Gustedt Algorithm 6.3 with witness)")
    checked = fail_val = fail_wit = fail_bags = 0
    for alpha0, cliques in all_starlike(nmax):
        g, C, specs = starlike_graph(alpha0, cliques)
        v = vs(g)
        pw, layout, bags = starlike_pathwidth(C, specs)
        checked += 1
        if pw != v:
            fail_val += 1
        if sorted(layout) != list(range(g[0])) or vs_of_layout(g, layout) != v:
            fail_wit += 1
        if max(popcount(b) for b in bags) - 1 != v or not _is_path_decomposition(g, bags):
            fail_bags += 1
    rchecked = rfail = 0
    for _ in range(random_star):
        n = rng.randint(6, 14)
        alpha0, cliques = random_starlike(n, rng.randint(1, min(5, n - 1)), rng)
        g, C, specs = starlike_graph(alpha0, cliques)
        v = vs(g)
        pw, layout, bags = starlike_pathwidth(C, specs)
        rchecked += 1
        if pw != v or vs_of_layout(g, layout) != v or not _is_path_decomposition(g, bags):
            rfail += 1
    res["b3_starlike"] = {"exhaustive": checked, "fail_value": fail_val, "fail_witness": fail_wit,
                          "fail_decomposition": fail_bags, "random": rchecked, "random_fail": rfail}
    log(f"  exhaustive to {nmax}: {checked} graphs, value failures {fail_val}, witness failures "
        f"{fail_wit}, decomposition failures {fail_bags}; random (6–14 vertices): {rchecked}, failures {rfail}")

    # (c) es = cw on subcubic atlas graphs with n + 2m ≤ 20
    log("[c] edge search against cutwidth on subcubic graphs")
    checked = fail = 0
    diff = Counter()
    for g in sub:
        es = edges_of(g)
        if not es or g[0] + 2 * len(es) > 20:
            continue
        checked += 1
        d = edge_search_via_two_expansion(g) - cutwidth_dp(g)
        diff[d] += 1
        if d != 0:
            fail += 1
    res["c_edge_search"] = {"checked": checked, "es_minus_cw": {str(k): v for k, v in sorted(diff.items())},
                            "not_equal": fail}
    log(f"  {checked} subcubic graphs with n + 2m ≤ 20: es − cw distribution {dict(diff)}")

    res["seconds"] = round(time.time() - t0, 1)
    (out_dir / "check.json").write_text(json.dumps(res, indent=1))
    log(f"done in {res['seconds']} s; results in {out_dir / 'check.json'}")
    return res


def _is_path_decomposition(g, bags: list[int]) -> bool:
    n, adj = g
    full = (1 << n) - 1
    if any(b & ~full for b in bags):
        return False
    cover = 0
    for b in bags:
        cover |= b
    if cover != full:
        return False
    for u in range(n):
        for w in bits(adj[u]):
            if w > u and not any(b >> u & 1 and b >> w & 1 for b in bags):
                return False
    for v in range(n):
        where = [i for i, b in enumerate(bags) if b >> v & 1]
        if where and where[-1] - where[0] + 1 != len(where):
            return False
    return True


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmax", type=int, default=7)
    ap.add_argument("--no-converse", action="store_true")
    args = ap.parse_args()
    run_checks(args.nmax, converse=not args.no_converse)


if __name__ == "__main__":
    main()
