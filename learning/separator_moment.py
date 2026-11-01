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

import math
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
    # item 03: the clumping decomposed
    "small_nbhd_sets", "enumerate_empty_pairs", "separators_of",
    "closed_pairs_pruned", "closure_image", "move_classes", "overlap_tables",
    "second_moment_rate_gnp", "second_moment_exact_gnp", "second_moment_enum_gnp",
    "gnp_masks",
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


# --- item 03: the clumping decomposed ------------------------------------------
#
# `X₁` exact-size empty pairs, `X₂` distinct separators among them (= the
# `k`-sets in `E_bip`, L1′ c), `X₃` closed pairs of the forced sizes, `X₃′` the
# image of the exact-size pairs under the `A`-first closure, `X₄` move-classes:
# the connected components of the graph on exact-size pairs in which two pairs
# are adjacent when their class labellings `V → {A, R, S}` differ on at most two
# vertices (at exact sizes that is exactly one swap of two vertices between two
# classes; a single vertex changing class would change the sizes).


def small_nbhd_sets(adj: list[int], limit: int, min_size: int = 0,
                    max_size: int | None = None, max_sets: int | None = None) -> list[int]:
    """Every vertex set `A` with `|N[A]| ≤ limit` and `min_size ≤ |A| ≤ max_size`,
    by a depth-first search in index order; the family `{A : |N[A]| ≤ limit}` is
    closed under subsets, so pruning a branch whose closed neighbourhood is
    already too large is exact (the cut of `expansion_bound._f_exact`, listing
    the sets instead of minimising). Raises `OverflowError` past `max_sets`."""
    n = len(adj)
    if max_size is None:
        max_size = n
    out: list[int] = []

    def dfs(start: int, chosen: int, size: int, union: int) -> None:
        if size >= min_size:
            out.append(chosen)
            if max_sets is not None and len(out) > max_sets:
                raise OverflowError(f"more than {max_sets} sets with |N[A]| <= {limit}")
        if size == max_size:
            return
        for v in range(start, n):
            u = union | adj[v] | (1 << v)
            if popcount(u) <= limit:
                dfs(v + 1, chosen | (1 << v), size + 1, u)

    dfs(0, 0, 0, 0)
    return out


def enumerate_empty_pairs(adj: list[int], k: int, max_pairs: int | None = None) -> list[tuple[int, int]]:
    """Every ordered exact-size empty pair `(A, R)` at width `k` (`|A| = t`,
    `|R| = N − t`, `R ∩ N[A] = ∅`), by the pruned search over `t`-sets `A` with
    `|N[A]| ≤ n − (N − t)` and then every `(N − t)`-subset of `V ∖ N[A]`. The
    same list as `exact_pairs`, faster when few `t`-sets qualify."""
    n = len(adj)
    N, t = forced_sizes(n, k)
    full = (1 << n) - 1
    r = N - t
    out: list[tuple[int, int]] = []
    for A in small_nbhd_sets(adj, n - r, t, t):
        outside = full & ~closed_nbhd(adj, A)
        verts = [v for v in range(n) if outside >> v & 1]
        for rc in combinations(verts, r):
            out.append((A, sum(1 << v for v in rc)))
        if max_pairs is not None and len(out) > max_pairs:
            raise OverflowError(f"more than {max_pairs} exact-size pairs")
    return out


def separators_of(pairs: Iterator[tuple[int, int]] | list[tuple[int, int]], n: int) -> set[int]:
    """The distinct separators `S = V ∖ (A ∪ R)` of a list of pairs (`X₂` when
    the pairs are all exact-size empty pairs, by L1′ c)."""
    full = (1 << n) - 1
    return {full & ~(A | R) for A, R in pairs}


def closed_pairs_pruned(adj: list[int], k: int, max_sets: int | None = None) -> list[tuple[int, int]]:
    """`X₃` as `closed_pairs` but by the pruned search: a closed pair of the
    forced sizes has `|A| ≥ t` and `|N[A]| = n − |R| ≤ n − (N − t)`, so `A` is
    in the down-closed family of `small_nbhd_sets`; then `R = V ∖ N[A]` and the
    pair is closed iff `A = V ∖ N[R]`. Works beyond `n = 16`."""
    n = len(adj)
    N, t = forced_sizes(n, k)
    full = (1 << n) - 1
    out = []
    for A in small_nbhd_sets(adj, n - (N - t), t, max_sets=max_sets):
        R = full & ~closed_nbhd(adj, A)
        if A == full & ~closed_nbhd(adj, R):
            out.append((A, R))
    return out


def closure_image(adj: list[int], pairs, side: str = "A") -> set[tuple[int, int]]:
    """`X₃′`: the set of closed pairs reached from the given pairs by
    `close_pair` (the `A`-first map by default)."""
    return {close_pair(adj, A, R, side) for A, R in pairs}


def move_classes(pairs: list[tuple[int, int]], n: int) -> list[int]:
    """`X₄`: the move-classes of a list of (exact-size empty) pairs — the
    connected components of the graph in which two pairs are adjacent when
    their labellings `V → {A, R, S}` differ on at most two vertices. Returns
    the class index of every pair (classes numbered from 0 in order of first
    appearance); `X₄ = max + 1`."""
    full = (1 << n) - 1
    index = {P: i for i, P in enumerate(pairs)}
    parent = list(range(len(pairs)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i: int, j: int) -> None:
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[max(ri, rj)] = min(ri, rj)

    for i, (A, R) in enumerate(pairs):
        S = full & ~(A | R)
        av = [v for v in range(n) if A >> v & 1]
        rv = [v for v in range(n) if R >> v & 1]
        sv = [v for v in range(n) if S >> v & 1]
        for a in av:
            Aa = A & ~(1 << a)
            for s in sv:                       # A ↔ S
                j = index.get((Aa | (1 << s), R))
                if j is not None:
                    union(i, j)
            for r in rv:                       # A ↔ R
                j = index.get((Aa | (1 << r), (R & ~(1 << r)) | (1 << a)))
                if j is not None:
                    union(i, j)
        for r in rv:
            Rr = R & ~(1 << r)
            for s in sv:                       # R ↔ S
                j = index.get((A, Rr | (1 << s)))
                if j is not None:
                    union(i, j)
    roots = {}
    out = []
    for i in range(len(pairs)):
        r = find(i)
        out.append(roots.setdefault(r, len(roots)))
    return out


def overlap_tables(pairs: list[tuple[int, int]], n: int) -> np.ndarray:
    """For every ordered pair of *distinct* pairs `(P, P′)`, the `3 × 3`
    overlap table `(|A ∩ A′|, |A ∩ R′|, |A ∩ S′|, |R ∩ A′|, |R ∩ R′|, |R ∩ S′|,
    |S ∩ A′|, |S ∩ R′|, |S ∩ S′|)` as an integer array of shape `(X₁(X₁ − 1), 9)`."""
    full = (1 << n) - 1
    rows = []
    cls = [(A, R, full & ~(A | R)) for A, R in pairs]
    for i, P in enumerate(cls):
        for j, Q in enumerate(cls):
            if i == j:
                continue
            rows.append([popcount(x & y) for x in P for y in Q])
    return np.array(rows, dtype=int).reshape(-1, 9)


# --- the second moment of the pair count on G(n, p) -----------------------------
#
# Two pairs `(A, R)`, `(A′, R′)` are empty together iff no edge lies in
# `A × R ∪ A′ × R′`, whose size is `|A||R| + |A′||R′| − |A ∩ A′||R ∩ R′| −
# |A ∩ R′||R ∩ A′|` (an unordered pair lies in both products iff it joins
# `A ∩ A′` to `R ∩ R′` or `A ∩ R′` to `R ∩ A′`). So `E[X²]` is a sum over the
# `3 × 3` overlap table of a multinomial times `(1 − p)^{that size}`, and with
# `p = c/n` and both sides `a n` its exponent per vertex at a table of fractions
# `T` is `H(T) − c (2a² − T_AA′ T_RR′ − T_AR′ T_RA′)`.


def _entropy(T: np.ndarray) -> float:
    T = np.asarray(T, dtype=float)
    pos = T[T > 1e-300]
    return float(-(pos * np.log(pos)).sum())


def gnp_pair_rate(a: float, c: float) -> float:
    """`g(a)`: the exponent per vertex of `E[X]` on `G(n, c/n)` with both sides
    `a n`: `H(a, a, 1 − 2a) − c a²`."""
    return _entropy(np.array([a, a, 1 - 2 * a])) - c * a * a


def second_moment_rate_gnp(a: float, c: float, starts: int = 16, seed: int = 0) -> tuple[float, float, np.ndarray]:
    """The asymptotic exponent of `E[X²]` on `G(n, c/n)` (sup over the overlap
    table of two pairs with both sides `a n`) beside `2 g(a)`; their difference
    is the exponent of `E[X²] / E[X]²`. Returns `(sup, 2 g(a), table)` with the
    table in the order of `overlap_tables` (`AA′, AR′, AS′, RA′, RR′, RS′, SA′,
    SR′, SS′`). The Bernoulli form of `learning.first_moment.second_moment_rate`."""
    from scipy.optimize import minimize

    def table(v):
        aa, ar, ra, rr = v
        ao = a - aa - ar
        ro = a - ra - rr
        oa = a - aa - ra
        orr = a - ar - rr
        oo = 1 - 2 * a - oa - orr
        return np.array([aa, ar, ao, ra, rr, ro, oa, orr, oo])

    def exponent(v):
        T = table(v)
        return _entropy(T) - c * (2 * a * a - T[0] * T[4] - T[1] * T[3])

    f = lambda v: -exponent(v)  # noqa: E731
    cons = {"type": "ineq", "fun": lambda v: table(v)}
    rng = np.random.default_rng(seed)
    prod = np.array([a * a, a * a, a * a, a * a])
    best_v, best = prod, exponent(prod)
    pts = [prod, np.array([0.0, a, a, 0.0]) * 0.9, np.array([a, 0.0, 0.0, a]) * 0.9]
    pts += [rng.uniform(0, a, 4) for _ in range(starts)]
    for v0 in pts:
        if np.any(table(v0) < 0):
            v0 = prod * rng.uniform(0.5, 1.5)
            if np.any(table(v0) < 0):
                continue
        res = minimize(f, v0, method="SLSQP", constraints=[cons], options={"maxiter": 500, "ftol": 1e-13})
        if np.all(table(res.x) >= -1e-9):
            val = exponent(res.x)
            if val > best:
                best, best_v = val, res.x
    return float(best), 2 * gnp_pair_rate(a, c), table(best_v)


def second_moment_exact_gnp(n: int, t: int, r: int, p: float) -> tuple[float, float, float]:
    """`(log E[X], log E[X²], E[X²] / E[X]²)` for `X` the number of ordered empty
    pairs `(A, R)`, `|A| = t`, `|R| = r`, of `G(n, p)`, exactly, by the sum over
    the `3 × 3` overlap table."""
    from math import lgamma
    o = n - t - r
    if o < 0:
        return math.inf, math.inf, math.nan
    lq1 = math.log1p(-p)
    logEX = lgamma(n + 1) - lgamma(t + 1) - lgamma(r + 1) - lgamma(o + 1) + t * r * lq1
    terms = []
    for aa in range(t + 1):
        for ar in range(t - aa + 1):
            ao = t - aa - ar
            for ra in range(min(r, t - aa) + 1):
                for rr in range(min(r - ra, r - ar) + 1):
                    ro = r - ra - rr
                    oa = t - aa - ra
                    orr = r - ar - rr
                    oo = o - oa - orr
                    if oo < 0:
                        continue
                    cells = (aa, ar, ao, ra, rr, ro, oa, orr, oo)
                    logmult = lgamma(n + 1) - sum(lgamma(x + 1) for x in cells)
                    forbidden = 2 * t * r - aa * rr - ar * ra
                    terms.append(logmult + forbidden * lq1)
    m = max(terms)
    logEX2 = m + math.log(sum(math.exp(x - m) for x in terms))
    return logEX, logEX2, math.exp(logEX2 - 2 * logEX)


def second_moment_enum_gnp(n: int, t: int, r: int, p: float) -> tuple[float, float]:
    """`(E[X], E[X²])` by enumerating every ordered pair of pairs and summing
    `(1 − p)^{|A × R ∪ A′ × R′|}`; the check of `second_moment_exact_gnp` (`n ≤ 10`)."""
    verts = range(n)
    pairs = []
    for ac in combinations(verts, t):
        A = sum(1 << v for v in ac)
        rest = [v for v in verts if not A >> v & 1]
        for rc in combinations(rest, r):
            pairs.append((A, sum(1 << v for v in rc)))
    EX = len(pairs) * (1 - p) ** (t * r)
    EX2 = 0.0
    for A, R in pairs:
        for A2, R2 in pairs:
            forb = 2 * t * r - popcount(A & A2) * popcount(R & R2) - popcount(A & R2) * popcount(R & A2)
            EX2 += (1 - p) ** forb
    return EX, EX2


def gnp_masks(n: int, p: float, seed: int) -> list[int]:
    """Adjacency masks of `networkx.gnp_random_graph(n, p, seed=seed)` (the
    pilot's generator, `reports/scratch/gnp_pilot/pilot.py`)."""
    import networkx as nx
    G = nx.gnp_random_graph(n, p, seed=seed)
    adj = [0] * n
    for u, v in G.edges():
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj
