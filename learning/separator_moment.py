"""The deterministic structures of the separator first moment (loop0011 item 02;
`reports/separator_moment.md` §2).

A layout of vertex separation `≤ k < n` forces, with `N = n − k` and
`t = ⌈N/2⌉`:

* **L1, the balanced separator at exact sizes** — disjoint `A, R, S` with
  `A ∪ R ∪ S = V`, `|A| = t`, `|R| = N − t`, `|S| = k`, no `A–R` edge;
* **L1′, the separator events** — a `k`-set `S` whose removal leaves components
  that can be grouped into two sides of sizes `t` and `N − t` (`E_bip`), hence
  no component larger than `t` (`E_relax`, strictly weaker);
* **L2, the closed pair** — an empty pair `(A*, R*)` with `A* = V ∖ N[R*]`,
  `R* = V ∖ N[A*]`, sides at least the forced sizes and `|S*| ≤ k`, reached
  from any exact-size pair by the alternating closure, which stops after one
  round (`R₁ = V ∖ N[A]`, `A₁ = V ∖ N[R₁]`, and then `R₂ = R₁`).

Graphs are adjacency bit masks (`adj[v]` has bit `u` iff `u ~ v`), vertex sets
are bit masks. Everything here is exact and enumerative; nothing is
probabilistic. Checked on every graph to 9 vertices, 20,000 random graphs at
10–12 and 2,000 random covers at ≤ 10 customers by
`reports/scratch/separator_moment/02_lemmas/check.py`.
"""
from __future__ import annotations

from itertools import combinations
from math import comb
from typing import Iterator

import numpy as np

__all__ = [
    "forced_sizes", "vertex_separation", "closed_nbhd", "open_nbhd",
    "is_empty_pair", "count_exact_pairs", "exact_pairs", "components",
    "separator_events", "count_separators", "close_pair", "closure_sequence",
    "is_closed_pair", "closed_pairs", "popcount", "mosp_masks",
    "pattern_meets_both", "shares_pattern",
]


def popcount(x: int) -> int:
    return bin(x).count("1")


def forced_sizes(n: int, k: int) -> tuple[int, int]:
    """`(N, t)` with `N = n − k` and `t = ⌈N/2⌉`; requires `k < n`."""
    if not 0 <= k < n:
        raise ValueError(f"need 0 <= k < n, got k={k}, n={n}")
    N = n - k
    return N, (N + 1) // 2


def vertex_separation(adj: list[int]) -> int:
    """Vertex separation (= pathwidth) by the incremental subset DP
    `f(S) = max(b(S), min_{v ∈ S} f(S − v))`, `b(S) = |N(S) ∖ S|`; `n ≤ 16`."""
    n = len(adj)
    if n == 0:
        return 0
    full = (1 << n) - 1
    nb = [0] * (1 << n)
    f = [0] * (1 << n)
    for S in range(1, 1 << n):
        low = S & -S
        v = low.bit_length() - 1
        nb[S] = nb[S ^ low] | adj[v]
        b = popcount(nb[S] & ~S & full)
        best = n
        T = S
        while T:
            low = T & -T
            T ^= low
            c = f[S ^ low]
            if c < best:
                best = c
        f[S] = best if best > b else b
    return f[full]


def closed_nbhd(adj: list[int], A: int) -> int:
    """`N[A]`: `A` and every neighbour of a vertex of `A`."""
    out = A
    T = A
    while T:
        low = T & -T
        T ^= low
        out |= adj[low.bit_length() - 1]
    return out


def open_nbhd(adj: list[int], A: int) -> int:
    """`N(A) = N[A] ∖ A`, the outer vertex boundary."""
    return closed_nbhd(adj, A) & ~A


def is_empty_pair(adj: list[int], A: int, R: int) -> bool:
    """Disjoint and no `A–R` edge, i.e. `R ∩ N[A] = ∅`."""
    return (closed_nbhd(adj, A) & R) == 0


def count_exact_pairs(adj: list[int], k: int) -> int:
    """`X₁`: the number of ordered pairs `(A, R)` with `|A| = t`, `|R| = N − t`
    and no `A–R` edge (an empty pair at the forced sizes)."""
    n = len(adj)
    N, t = forced_sizes(n, k)
    total = 0
    for combo in combinations(range(n), t):
        A = sum(1 << v for v in combo)
        free = n - popcount(closed_nbhd(adj, A))
        if free >= N - t:
            total += comb(free, N - t)
    return total


def exact_pairs(adj: list[int], k: int) -> Iterator[tuple[int, int]]:
    """Every ordered exact-size empty pair `(A, R)` as masks."""
    n = len(adj)
    N, t = forced_sizes(n, k)
    full = (1 << n) - 1
    for combo in combinations(range(n), t):
        A = sum(1 << v for v in combo)
        outside = full & ~closed_nbhd(adj, A)
        verts = [v for v in range(n) if outside >> v & 1]
        if len(verts) < N - t:
            continue
        for rc in combinations(verts, N - t):
            yield A, sum(1 << v for v in rc)


def components(adj: list[int], mask: int) -> list[int]:
    """Connected components of the induced subgraph on `mask`, as masks."""
    comps = []
    rest = mask
    while rest:
        low = rest & -rest
        comp = low
        frontier = low
        while frontier:
            v = frontier & -frontier
            frontier ^= v
            new = adj[v.bit_length() - 1] & mask & ~comp
            comp |= new
            frontier |= new
        comps.append(comp)
        rest &= ~comp
    return comps


def _subset_sum(sizes: list[int], target: int) -> bool:
    reach = 1  # bit i set iff some sub-multiset sums to i
    for s in sizes:
        reach |= reach << s
        if reach >> target & 1:
            return True
    return bool(reach >> target & 1)


def separator_events(adj: list[int], S: int, k: int) -> tuple[bool, bool]:
    """`(E_bip, E_relax)` for the `k`-set `S`: can the components of `G − S` be
    grouped into two sides of sizes `t` and `N − t`; is no component larger
    than `t`."""
    n = len(adj)
    N, t = forced_sizes(n, k)
    full = (1 << n) - 1
    sizes = [popcount(c) for c in components(adj, full & ~S)]
    relax = max(sizes, default=0) <= t
    bip = relax and _subset_sum(sizes, t)
    return bip, relax


def count_separators(adj: list[int], k: int) -> tuple[int, int]:
    """`(X₂, X₂′)`: the number of `k`-sets `S` in `E_bip` and in `E_relax`."""
    n = len(adj)
    nb = nr = 0
    for combo in combinations(range(n), k):
        S = sum(1 << v for v in combo)
        b, r = separator_events(adj, S, k)
        nb += b
        nr += r
    return nb, nr


def closure_sequence(adj: list[int], A: int, R: int, rounds: int = 2) -> list[tuple[int, int]]:
    """The alternating closure from the empty pair `(A, R)`, closing `A`'s side
    first: `R₁ = V ∖ N[A]`, `A₁ = V ∖ N[R₁]`, `R₂ = V ∖ N[A₁]`, … for `rounds`
    rounds. Returns `[(A, R), (A, R₁), (A₁, R₁), (A₁, R₂), (A₂, R₂), …]`; the
    claim checked by item 02 is that the second round repeats the first."""
    n = len(adj)
    full = (1 << n) - 1
    seq = [(A, R)]
    a = A
    for _ in range(rounds):
        r2 = full & ~closed_nbhd(adj, a)
        seq.append((a, r2))
        a = full & ~closed_nbhd(adj, r2)
        seq.append((a, r2))
    return seq


def close_pair(adj: list[int], A: int, R: int, side: str = "A") -> tuple[int, int]:
    """The closed pair reached from `(A, R)`: `R* = V ∖ N[A]`, `A* = V ∖ N[R*]`
    when `side == "A"`; the mirror when `side == "R"`. The two can differ."""
    n = len(adj)
    full = (1 << n) - 1
    if side == "A":
        Rs = full & ~closed_nbhd(adj, A)
        As = full & ~closed_nbhd(adj, Rs)
    else:
        As = full & ~closed_nbhd(adj, R)
        Rs = full & ~closed_nbhd(adj, As)
    return As, Rs


def is_closed_pair(adj: list[int], A: int, R: int) -> bool:
    """`A = V ∖ N[R]` and `R = V ∖ N[A]`, equivalently `S = N(A) ∩ N(R)` with
    no `A–R` edge."""
    n = len(adj)
    full = (1 << n) - 1
    return A == full & ~closed_nbhd(adj, R) and R == full & ~closed_nbhd(adj, A)


def closed_pairs(adj: list[int], k: int) -> list[tuple[int, int]]:
    """`X₃`: every closed pair `(A, R)` with `|A| ≥ t`, `|R| ≥ N − t` and
    `|V ∖ (A ∪ R)| ≤ k`, by enumerating `A` (which determines `R = V ∖ N[A]`)."""
    n = len(adj)
    N, t = forced_sizes(n, k)
    full = (1 << n) - 1
    out = []
    for A in range(1 << n):
        if popcount(A) < t:
            continue
        R = full & ~closed_nbhd(adj, A)
        if popcount(R) < N - t:
            continue
        if A != full & ~closed_nbhd(adj, R):
            continue
        if n - popcount(A) - popcount(R) <= k:
            out.append((A, R))
    return out


# --- the MOSP forms -----------------------------------------------------------


def mosp_masks(matrix: np.ndarray) -> list[int]:
    """Adjacency masks of the MOSP graph of a `customers × patterns` 0/1 matrix
    (customers adjacent iff some pattern needs both)."""
    n, m = matrix.shape
    adj = [0] * n
    for j in range(m):
        rows = np.flatnonzero(matrix[:, j])
        mask = sum(1 << int(c) for c in rows)
        for c in rows:
            adj[int(c)] |= mask & ~(1 << int(c))
    return adj


def pattern_meets_both(matrix: np.ndarray, A: int, R: int) -> bool:
    """Some pattern needs a customer of `A` and a customer of `R`."""
    n, m = matrix.shape
    for j in range(m):
        mask = sum(1 << int(c) for c in np.flatnonzero(matrix[:, j]))
        if mask & A and mask & R:
            return True
    return False


def shares_pattern(matrix: np.ndarray, c: int, A: int) -> bool:
    """Customer `c` shares a pattern with some customer of `A ∖ {c}`."""
    n, m = matrix.shape
    other = A & ~(1 << c)
    for j in np.flatnonzero(matrix[c]):
        mask = sum(1 << int(r) for r in np.flatnonzero(matrix[:, j]))
        if mask & other:
            return True
    return False
