"""The Edwards–McDermid degree-sequence bound on pathwidth, evaluated (loop0012
item 01; `reports/edwards_mcdermid.md` §1; the plan is
`reports/edwards_mcdermid_plan.md`).

Edwards & McDermid, *Algorithmica* 72(4):940–968, 2015, Corollary 5.2:

    pw(G) ≤ Σ_{v ∈ V(r(G))} g_{1/6}(d_{r(G)}(v)) + τ(|V(G)|) + O(log |V(G)|),

where `g = g_{1/6}` is the weight function of their Section 3.1 (`g(2) = 0`,
`g(3) = 1/6`, `n g(n) = (n − 2) g(n − 1) + g(n − 2) + 1` for `n ≥ 4`), `r(G)`
is the series-parallel reduction of `G` (their Section 3.2: delete vertices of
degree ≤ 1, suppress vertices of degree 2, until every degree is ≥ 3 or the
graph is empty), and `τ(n) = o(n)` is the error term of Fomin & Høie's cubic
bound, for which the paper gives no constant.

Everything here is exact: `g` in `fractions.Fraction`, graphs as adjacency bit
masks (`adj[v]` has bit `u` iff `u ~ v`), the reduction with a bucket of
low-degree vertices so that it is linear in the number of steps (the dataset
has graphs to 2,916 vertices). Removed vertices are *isolated*, as in the Lean
design (plan §0.5): `reduce` returns the reduced adjacency on the same vertex
set and the mask of removed vertices, and `g(0) = g(1) = g(2) = 0` makes them
weightless.

Nothing here solves a pathwidth; the pathwidths come from the record.
"""
from __future__ import annotations

import math
from fractions import Fraction
from functools import lru_cache
from typing import Iterable

__all__ = [
    "g", "g_float", "g_real", "g_prime", "alternating_factorial", "g_closed_form",
    "popcount", "bits", "from_edges", "from_networkx", "degrees", "edge_count",
    "components", "min_degree", "reduce", "main_term", "histogram_term",
    "average_degree", "average_degree_term", "fminus", "f_potential",
    "is_reduced", "is_cubic", "poisson_value", "fomin_hoie_n_eps", "fomin_hoie_budget",
    "evaluate",
    # item 02: the reduction system step by step, basic graphs, the paper's
    # choice of `w`, Algorithm X, the one-component potential
    "support", "isolate", "isolate_set", "restrict", "step_vertices", "sp_step",
    "reduce_random", "global_min_degree", "F_global", "is_basic_component", "is_basic",
    "paper_choice", "algorithm_x", "pathwidth_induced",
    # item 04: the cut lemma (`CutLemma.lean`) on bit masks
    "parse_g6", "boundary_to", "separator_cut_bound", "bisection_bound",
]

ALPHA = Fraction(1, 6)


# ----------------------------------------------------------------------------
# the weights
# ----------------------------------------------------------------------------


@lru_cache(maxsize=None)
def g(n: int) -> Fraction:
    """`g_{1/6}(n)` in exact rationals; `g(0) = g(1) = g(2) = 0`, `g(3) = 1/6`,
    and `n g(n) = (n − 2) g(n − 1) + g(n − 2) + 1` for `n ≥ 4` (paper p. 6)."""
    if n < 0:
        raise ValueError("g is defined on the naturals")
    if n <= 2:
        return Fraction(0)
    if n == 3:
        return ALPHA
    return ((n - 2) * g(n - 1) + g(n - 2) + 1) / n


def g_float(n: int) -> float:
    return float(g(n))


def g_real(x: float | Fraction) -> Fraction:
    """The paper's linear interpolation between integers (p. 6), exact when `x`
    is a `Fraction`; below 2 it is 0, since `g(0) = g(1) = g(2) = 0`."""
    x = Fraction(x)
    if x < 0:
        raise ValueError("g_real is defined on x ≥ 0")
    n = math.floor(x)
    t = x - n
    return (1 - t) * g(n) + t * g(n + 1)


def g_prime(n: int) -> Fraction:
    """`g'(n) = g(n) − g(n − 1)`; zero for `n ≤ 2` (and at 0)."""
    if n <= 0:
        return Fraction(0)
    return g(n) - g(n - 1)


def alternating_factorial(n: int) -> int:
    """`A(n) = n! − (n − 1)! + … ± 1!` (so `A(1) = 1`, `A(2) = 1`, `A(3) = 5`)."""
    total = 0
    sign = 1
    for k in range(n, 0, -1):
        total += sign * math.factorial(k)
        sign = -sign
    return total


def g_closed_form(n: int, alpha: Fraction = ALPHA) -> Fraction:
    """Lemma 8.1: `g_α(n) = (4 − 3α) A(n)/n! + (2 − 3α)(−1)^n/n! − (3 − 3α)`, `n ≥ 2`."""
    if n < 2:
        raise ValueError("the closed form is stated for n ≥ 2")
    fact = math.factorial(n)
    return ((4 - 3 * alpha) * Fraction(alternating_factorial(n), fact)
            + (2 - 3 * alpha) * Fraction((-1) ** n, fact) - (3 - 3 * alpha))


# ----------------------------------------------------------------------------
# graphs as bit masks
# ----------------------------------------------------------------------------


def popcount(x: int) -> int:
    return x.bit_count()


def bits(mask: int) -> Iterable[int]:
    """The set bits of `mask`, ascending."""
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def from_edges(n: int, edges: Iterable[tuple[int, int]]) -> list[int]:
    adj = [0] * n
    for a, b in edges:
        if a == b:
            continue
        adj[a] |= 1 << b
        adj[b] |= 1 << a
    return adj


def from_networkx(G) -> list[int]:
    """Vertices relabelled 0..n−1 in sorted order."""
    nodes = sorted(G.nodes())
    index = {v: i for i, v in enumerate(nodes)}
    return from_edges(len(nodes), ((index[a], index[b]) for a, b in G.edges()))


def degrees(adj: list[int]) -> list[int]:
    return [a.bit_count() for a in adj]


def edge_count(adj: list[int]) -> int:
    return sum(a.bit_count() for a in adj) // 2


def components(adj: list[int], support_only: bool = True) -> list[int]:
    """Connected components as vertex masks; by default only those of the
    support (vertices of positive degree), so isolated vertices are skipped."""
    n = len(adj)
    seen = 0
    out = []
    for v in range(n):
        if (seen >> v) & 1:
            continue
        if support_only and adj[v] == 0:
            continue
        comp = 1 << v
        frontier = 1 << v
        while frontier:
            nxt = 0
            for u in bits(frontier):
                nxt |= adj[u]
            nxt &= ~comp
            comp |= nxt
            frontier = nxt
        seen |= comp
        out.append(comp)
    return out


def min_degree(adj: list[int], mask: int) -> int:
    return min(adj[v].bit_count() for v in bits(mask))


def is_reduced(adj: list[int]) -> bool:
    """Every degree is 0 or at least 3 (the Lean `IsSPReduced`)."""
    return all(d == 0 or d >= 3 for d in degrees(adj))


def is_cubic(adj: list[int], mask: int | None = None) -> bool:
    vs = range(len(adj)) if mask is None else bits(mask)
    return all(adj[v].bit_count() == 3 for v in vs)


# ----------------------------------------------------------------------------
# the series-parallel reduction
# ----------------------------------------------------------------------------


def reduce(adj: list[int]) -> tuple[list[int], int]:
    """The reduced graph `r(G)` of paper Section 3.2, on the same vertex set
    with the removed vertices isolated, and the mask of removed vertices.

    The four operations, applied while a vertex of degree ≤ 2 remains:
    (1) delete an isolated vertex; (2) delete a vertex of degree 1; (3) a vertex
    of degree 2 with non-adjacent neighbours `x, y`: delete it and add `xy`;
    (4) a vertex of degree 2 with adjacent neighbours: delete it. Here an
    already-isolated vertex is left in place (it is "deleted" in the paper's
    sense: it contributes nothing), and a vertex that becomes isolated is
    recorded as removed. The result is unique (the paper, p. 8) so the order
    in which the bucket is drained does not matter for the output.

    Linear in the number of steps: degrees are kept in an array and only the
    neighbours of the deleted vertex are touched.
    """
    n = len(adj)
    adj = list(adj)
    deg = [a.bit_count() for a in adj]
    removed = 0
    for v in range(n):
        if deg[v] == 0:
            removed |= 1 << v
    stack = [v for v in range(n) if 0 < deg[v] <= 2]
    while stack:
        v = stack.pop()
        if (removed >> v) & 1 or deg[v] > 2:
            continue
        nb = adj[v]
        if deg[v] == 0:
            removed |= 1 << v
            continue
        if deg[v] == 1:
            x = nb.bit_length() - 1
            adj[x] &= ~(1 << v)
            adj[v] = 0
            deg[v] = 0
            deg[x] -= 1
            removed |= 1 << v
            if deg[x] <= 2:
                stack.append(x)
            continue
        # degree 2
        low = nb & -nb
        x = low.bit_length() - 1
        y = (nb ^ low).bit_length() - 1
        adj[x] &= ~(1 << v)
        adj[y] &= ~(1 << v)
        adj[v] = 0
        deg[v] = 0
        removed |= 1 << v
        if (adj[x] >> y) & 1:
            # operation 4: neighbours adjacent, both lose one
            deg[x] -= 1
            deg[y] -= 1
        else:
            # operation 3: suppress, degrees of x and y unchanged
            adj[x] |= 1 << y
            adj[y] |= 1 << x
        if deg[x] <= 2:
            stack.append(x)
        if deg[y] <= 2:
            stack.append(y)
    return adj, removed


# ----------------------------------------------------------------------------
# the terms of Corollary 5.2 and Theorem 5.3
# ----------------------------------------------------------------------------


def histogram_term(adj: list[int]) -> Fraction:
    """`Σ_{d ≥ 3} g(d) n_d(G)`, the unreduced form (the right-hand side of
    Corollary 5.2's displayed line)."""
    return sum((g(d) for d in degrees(adj)), Fraction(0))


def main_term(adj: list[int], reduced: tuple[list[int], int] | None = None) -> Fraction:
    """`Σ_{v ∈ V(r(G))} g(d_{r(G)}(v))`, the reduced form (the main term of
    Corollary 5.2). Pass `reduce(adj)` to avoid recomputing it."""
    radj, _ = reduced if reduced is not None else reduce(adj)
    return histogram_term(radj)


def average_degree(adj: list[int]) -> Fraction:
    n = len(adj)
    if n == 0:
        return Fraction(0)
    return Fraction(2 * edge_count(adj), n)


def average_degree_term(adj: list[int]) -> Fraction:
    """`g(d̄) · n` with the paper's linear interpolation (Theorem 5.3's main
    term). Meaningful when `G` is connected or `d̄ ≥ 5`; computed regardless."""
    return g_real(average_degree(adj)) * len(adj)


def f_potential(adj: list[int]) -> Fraction:
    """`f(G) = Σ_v g(d(v))` (the paper's `f_α`, `α = 1/6`)."""
    return histogram_term(adj)


def fminus(adj: list[int]) -> Fraction:
    """`f⁻(G) = f(G) − Σ_{components C of the support} g'(δ(C))` (paper p. 7,
    per component, as the Lean design fixes it). Isolated vertices are
    singleton components with `g'(0) = 0`. The paper defines it for minimum
    degree ≥ 3; the formula is evaluated on any graph."""
    total = f_potential(adj)
    for comp in components(adj):
        total -= g_prime(min_degree(adj, comp))
    return total


# ----------------------------------------------------------------------------
# the Poisson evaluation and Fomin–Høie's explicit budget
# ----------------------------------------------------------------------------


def poisson_value(c: float, tail: float = 1e-15) -> float:
    """`Σ_d P(Poisson(c) = d) g(d)`: Corollary 5.2's main term per vertex on
    `G(n, c/n)` in the limit, where the degree law is Poisson(`c`)."""
    if c < 0:
        raise ValueError("c must be non-negative")
    if c == 0:
        return 0.0
    total = 0.0
    p = math.exp(-c)
    d = 0
    while True:
        if d >= 3:
            total += p * float(g(d))
        d += 1
        p *= c / d
        if d > c and p < tail:
            break
    return total


def fomin_hoie_n_eps(eps: float) -> float:
    """`n_ε = (8/ε) ln(1/ε) (1 + 1/ε²)` from the proof of Fomin & Høie's Theorem 5."""
    return (8 / eps) * math.log(1 / eps) * (1 + 1 / eps ** 2)


def fomin_hoie_budget(n: int) -> float:
    """`τ_FH(n) = min{ε n : n > n_ε} + 1/6`: the smallest explicit error term
    Fomin & Høie's Theorem 5 offers at size `n`, read as a budget for the
    cubic base case `pw ≤ N/6 − 1/6 + τ(N)` (plan §0.3). `n_ε` decreases in
    `ε` on (0, 1), so the minimum is at the smallest admissible `ε`, found by
    bisection."""
    if n <= 0:
        return 1 / 6
    lo, hi = 1e-9, 1.0 - 1e-12
    if n > fomin_hoie_n_eps(lo):
        return lo * n + 1 / 6
    for _ in range(200):
        mid = (lo + hi) / 2
        if n > fomin_hoie_n_eps(mid):
            hi = mid
        else:
            lo = mid
    return hi * n + 1 / 6


# ----------------------------------------------------------------------------
# one graph, every term
# ----------------------------------------------------------------------------


def evaluate(adj: list[int], pw: int | None = None) -> dict:
    """Every term of Corollary 5.2 and Theorem 5.3 on one graph, as floats
    (the exact rationals are available through the functions above), with the
    deficits `pw − term` when `pw` is given. `avg_term` is Theorem 5.3's
    `g(d̄) n`, recorded whenever `d̄ ≥ 2`; `avg_applies` says whether the
    theorem's hypothesis (connected, or `d̄ ≥ 5`) holds."""
    n = len(adj)
    m = edge_count(adj)
    red = reduce(adj)
    radj, removed = red
    hist = histogram_term(adj)
    main = histogram_term(radj)
    comps = components(adj)
    isolated = sum(1 for a in adj if a == 0)
    connected = len(comps) == 1 and isolated == 0
    dbar = average_degree(adj)
    avg_term = g_real(dbar) * n if dbar >= 2 else None
    out = {
        "n": n, "m": m, "pw": pw,
        "main_term": float(main), "histogram_term": float(hist),
        "n_reduced": n - removed.bit_count(),
        "components": len(comps) + isolated, "connected": connected,
        "avg_degree": float(dbar),
        "avg_term": None if avg_term is None else float(avg_term),
        "avg_applies": bool(connected or dbar >= 5),
        "fminus": float(fminus(adj)),
        "max_degree": max(degrees(adj)) if n else 0,
        "reduced_is_cubic": bool(radj and any(radj) and is_cubic(radj, ((1 << n) - 1) & ~removed)),
    }
    out["main_gt_avg"] = bool(avg_term is not None and main > avg_term)
    if pw is not None:
        out["deficit"] = pw - out["main_term"]
        out["deficit_hist"] = pw - out["histogram_term"]
        out["deficit_avg"] = None if avg_term is None else pw - out["avg_term"]
    return out


# ----------------------------------------------------------------------------
# item 02: the reduction system one step at a time, basic graphs, Algorithm X
# (`reports/edwards_mcdermid.md` §2; checked on every graph to 9 vertices by
# `reports/scratch/edwards_mcdermid/02_lemmas/check.py`)
# ----------------------------------------------------------------------------


def support(adj: list[int]) -> int:
    """Mask of the vertices of positive degree."""
    m = 0
    for v, a in enumerate(adj):
        if a:
            m |= 1 << v
    return m


def isolate(adj: list[int], w: int) -> list[int]:
    """`G − w` in the Lean design: every edge at `w` deleted, `w` kept isolated."""
    out = list(adj)
    for u in bits(adj[w]):
        out[u] &= ~(1 << w)
    out[w] = 0
    return out


def isolate_set(adj: list[int], X: int) -> list[int]:
    out = list(adj)
    for w in bits(X):
        out = isolate(out, w)
    return out


def restrict(adj: list[int], C: int) -> list[int]:
    """The edges inside `C`, every other vertex isolated (`G|C` on the same vertex set)."""
    return [adj[v] & C if (C >> v) & 1 else 0 for v in range(len(adj))]


def step_vertices(adj: list[int]) -> list[int]:
    """The vertices at which an `SPStep` applies: degree 1 or 2. (A vertex of
    degree 0 is already "deleted"; isolating it would be the identity, which is
    why the Lean step relation is defined for degrees 1 and 2 only.)"""
    return [v for v in range(len(adj)) if 1 <= adj[v].bit_count() <= 2]


def sp_step(adj: list[int], v: int) -> list[int]:
    """One series-parallel operation at `v` (degree 1 or 2): operation 2 deletes
    a degree-1 vertex; operation 3 suppresses a degree-2 vertex with
    non-adjacent neighbours `x, y` (adds `xy`); operation 4 deletes a degree-2
    vertex with adjacent neighbours. The removed vertex is left isolated."""
    d = adj[v].bit_count()
    if d not in (1, 2):
        raise ValueError(f"no series-parallel step at a vertex of degree {d}")
    nb = adj[v]
    out = isolate(adj, v)
    if d == 2:
        low = nb & -nb
        x = low.bit_length() - 1
        y = (nb ^ low).bit_length() - 1
        if not (adj[x] >> y) & 1:
            out[x] |= 1 << y
            out[y] |= 1 << x
    return out


def reduce_random(adj: list[int], rng) -> list[int]:
    """A maximal reduction sequence in a random order; the reduct on the same
    vertex set. Used to measure whether the reduct depends on the order (it
    does not, on every graph to 9 vertices and 200 orders each)."""
    adj = list(adj)
    while True:
        cands = step_vertices(adj)
        if not cands:
            return adj
        adj = sp_step(adj, rng.choice(cands))


def global_min_degree(adj: list[int]) -> int:
    """`δ` over the support; 0 for the empty graph."""
    s = support(adj)
    return min_degree(adj, s) if s else 0


def F_global(adj: list[int]) -> Fraction:
    """`f(H) − g'(δ(H))` with `δ` over the whole support: the paper's `f⁻` for a
    connected graph, and an upper bound on the per-component `fminus` in
    general (`fminus ≤ F_global`, since every component's `g'(δ(C))` is ≥ 0 and
    one of them is `g'(δ(H))`)."""
    return f_potential(adj) - g_prime(global_min_degree(adj))


def is_basic_component(adj: list[int], C: int) -> bool:
    """`adj` restricted to its component `C` (every degree ≥ 3 there) is basic:
    cubic, or some `v ∈ C` has `r(G|C − v)` empty (paper p. 8)."""
    sub = restrict(adj, C)
    if is_cubic(sub, C):
        return True
    for v in bits(C):
        radj, _ = reduce(isolate(sub, v))
        if not any(radj):
            return True
    return False


def is_basic(adj: list[int]) -> bool:
    """Every component of the support is basic (the empty graph is basic)."""
    return all(is_basic_component(adj, C) for C in components(adj))


def paper_choice(adj: list[int], C: int | None = None) -> tuple[list[int], list[int], int]:
    """The maximum-degree vertices (within the component mask `C` if given),
    those among them whose lowest-degree neighbour has the smallest degree —
    the proof of Theorem 3.2's rule for `w` — and `Δ`. The step inequality
    holds for every vertex of the second list and fails for some of the first
    (`reports/edwards_mcdermid.md` §2, S1 against S1′)."""
    verts = list(bits(C)) if C is not None else [v for v in range(len(adj)) if adj[v]]
    deg = degrees(adj)
    Delta = max(deg[v] for v in verts)
    maxs = [v for v in verts if deg[v] == Delta]
    key = {v: min(deg[u] for u in bits(adj[v])) for v in maxs}
    best = min(key.values())
    return maxs, [v for v in maxs if key[v] == best], Delta


def algorithm_x(adj: list[int], rng=None) -> tuple[int, list[int]]:
    """Algorithm X of the paper (p. 12) on a graph with every degree 0 or ≥ 3:
    while some component is not basic, take a maximum-degree vertex `w` of it
    by the paper's rule (ties broken by `rng`, or the first), `G ← r(G − w)`,
    `X ← X ∪ {w}`. Returns the mask `X` and the final basic graph `B`, with
    `|X| + fminus(B) ≤ fminus(G)` (Theorem 3.2 (ii))."""
    X = 0
    cur = list(adj)
    while True:
        nonbasic = [C for C in components(cur) if not is_basic_component(cur, C)]
        if not nonbasic:
            return X, cur
        _, chosen, _ = paper_choice(cur, nonbasic[0])
        w = rng.choice(chosen) if rng is not None else chosen[0]
        X |= 1 << w
        cur, _ = reduce(isolate(cur, w))


def pathwidth_induced(adj: list[int], S: int) -> int:
    """Vertex separation (= pathwidth) of `G[S]` by the subset DP over the
    submasks of `S` (`|S| ≤ 16` or so)."""
    if S == 0:
        return 0
    f = {0: 0}
    T = (0 - S) & S
    while True:
        rest = S & ~T
        cost = 0
        U = T
        while U:
            low = U & -U
            U ^= low
            if adj[low.bit_length() - 1] & rest:
                cost += 1
        best = None
        U = T
        while U:
            low = U & -U
            U ^= low
            c = f[T ^ low]
            if best is None or c < best:
                best = c
        f[T] = cost if cost > best else best
        if T == S:
            break
        T = (T - S) & S
    return f[S]


# ----------------------------------------------------------------------------
# item 04: the cut lemma and its iterated form, as `DegreeBound/CutLemma.lean`
# states them (`reports/edwards_mcdermid.md` §4)
# ----------------------------------------------------------------------------


def parse_g6(line: str) -> tuple[int, list[int]]:
    """A graph6 line (`nauty-geng` output) as `(n, adjacency bit masks)`."""
    b = line.strip().encode()
    n = b[0] - 63
    bitlist: list[int] = []
    for ch in b[1:]:
        v = ch - 63
        bitlist += [(v >> i) & 1 for i in range(5, -1, -1)]
    adj = [0] * n
    k = 0
    for j in range(1, n):
        for i in range(j):
            if bitlist[k]:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
            k += 1
    return n, adj


def boundary_to(adj: list[int], A: int, B: int) -> int:
    """`boundaryTo G A B` of `CutLemma.lean`: the vertices of `A` with a neighbour
    in `B`, as a mask. With `B` the complement of `A` it is the boundary `∂A`."""
    out = 0
    for a in bits(A):
        if adj[a] & B:
            out |= 1 << a
    return out


def separator_cut_bound(adj: list[int], S1: int, S2: int, pw_of) -> int:
    """C1s in its relative form (`pathwidth_induce_union_le_max_add_min`):
    `max(pw(G[S1]), pw(G[S2])) + min(|∂(S1 → S2)|, |∂(S2 → S1)|)`, an upper bound
    on `pw(G[S1 ∪ S2])` for disjoint `S1`, `S2`; `pw_of(S)` returns `pw(G[S])`."""
    b1 = boundary_to(adj, S1, S2).bit_count()
    b2 = boundary_to(adj, S2, S1).bit_count()
    return max(pw_of(S1), pw_of(S2)) + min(b1, b2)


def bisection_bound(adj: list[int], tree, pw_of, use_max: bool = False) -> tuple[int, list[int]]:
    """`BisectionTree G S bs k` of `CutLemma.lean` evaluated on a concrete tree:
    `tree` is a mask (a leaf) or a pair `(left, right)` of trees on disjoint
    masks; returns `(k, bs)` with `k` the largest leaf pathwidth and `bs[i]` the
    largest `min(|∂₁|, |∂₂|)` (or `max`, with `use_max`) over the splits at depth
    `i`; the theorem gives `pw(G[S]) ≤ k + sum(bs)` (and `≤ k + 2 sum(bs)` for the
    max form, the item's C2)."""
    levels: list[int] = []
    leaves: list[int] = []

    def mask_of(t) -> int:
        return t if isinstance(t, int) else mask_of(t[0]) | mask_of(t[1])

    def walk(t, depth: int) -> None:
        if isinstance(t, int):
            leaves.append(pw_of(t))
            return
        S1, S2 = mask_of(t[0]), mask_of(t[1])
        if S1 & S2:
            raise ValueError("the two sides of a split must be disjoint")
        b1 = boundary_to(adj, S1, S2).bit_count()
        b2 = boundary_to(adj, S2, S1).bit_count()
        b = max(b1, b2) if use_max else min(b1, b2)
        while len(levels) <= depth:
            levels.append(0)
        levels[depth] = max(levels[depth], b)
        walk(t[0], depth + 1)
        walk(t[1], depth + 1)

    walk(tree, 0)
    return max(leaves), levels
