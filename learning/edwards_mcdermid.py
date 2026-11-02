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
