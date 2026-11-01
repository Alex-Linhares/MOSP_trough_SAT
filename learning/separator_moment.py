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
import random
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
    # item 04: the planted cluster
    "beta_star_gnp", "plant_pair", "plant_cover", "overlap_table", "hamming_distance",
    "lq_sides", "second_moment_exact_cover", "planted_mean_gnp", "planted_mean_cover",
    # item 05: the inner probability, exactly
    "connected_probs", "log_connected", "partitions", "log_prob_partition",
    "log_prob_bip", "log_prob_rel", "log_prob_bip_enum", "log_prob_bip_mc",
    "log_connected_enum", "log_connected_mc", "log_product_bound",
    # item 07: the MOSP version
    "closed_cover_log_prob_exact", "closed_cover_log_count_exact", "closed_cover_log_prob_na",
    "closed_cover_log_bound", "cover_log_pair_bound", "cover_pair_exponent",
    "cover_pair_exponent_beta", "cover_exponent_slope_at", "cover_lambda",
    "closed_cover_exponent_ind", "closed_cover_exponent_na", "closed_cover_rate",
    "beta_star_cover", "beta_closed_cover", "isolated_binomial_moments", "isolated_pgf",
    "isolated_pmf", "flip_joint_moments", "flip_joint_pmf", "flip_log_bound",
    "rig_branching_factor", "rig_giant", "half_giant_line", "cover_degree_law",
    "edwards_mcdermid_cover", "flip_cover_tail_exponent", "flip_cover_exponent_na",
    "flip_cover_exponent_beta", "beta_flip_cover", "flip_log_bound_fast", "_root_above",
    # item 08: the theorems on paper, in exact rationals
    "connected_probs_exact", "prob_relax_exact", "prob_bip_exact", "pair_count_exact",
    "closed_count_exact", "isolated_in", "flip_swaps", "flip_count", "weighted_count",
    "weighted_graph_count",
    # item 09: the weighted count's lower tail
    "recombinations", "recombination_pairs", "z_recomb", "side_avoiders", "z_hat0",
    "z_hat_log_laplace", "log_pair_count", "log_weighted_bound", "z_hat_exponent",
    "weighted_exponent", "beta_weighted",
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


# --- item 04: the planted cluster ------------------------------------------------
#
# Condition on one exact-size empty pair `P₀ = (A, R)` and count the *other*
# exact-size empty pairs `X′ = X − 1`. On `G(n, p)` the conditional law given
# `P₀` empty is `G(n, p)` with the `A–R` edges deleted (`plant_pair`); in the
# clique-cover model with i.i.d. uniform patterns it is the model with every
# pattern drawn uniformly among those meeting at most one side (`plant_cover`).
# By exchangeability `E[X²] = Σ_P P(P empty) · E[X | P empty] = E[X] · E[X | P₀
# empty]`, so the planted mean is `E[X′ | P₀ empty] = E[X²] / E[X] − 1`
# (`planted_mean_gnp`, `planted_mean_cover`): the second moment's ratio
# `E[X²]/E[X]²` *is* the planted mean over the unconditional mean.


def beta_star_gnp(c: float, tol: float = 1e-7) -> float:
    """`β*(c)`: the root in `β` of `g(a) = H(a, a, 1 − 2a) − c a²`, `a = (1 − β)/2`
    (the pair count's constant on `G(n, c/n)`; `0.1706` at `c = 6`, `0.3371` at
    `c = 10`). Zero when `g` is non-negative just below `a = ½` (`c ≤ 4 ln 2`)."""
    hi = 0.5 - 1e-9
    if gnp_pair_rate(hi, c) >= 0:
        return 0.0
    lo = 0.01
    while gnp_pair_rate(lo, c) <= 0:
        lo /= 2
        if lo < 1e-12:
            return 1.0
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if gnp_pair_rate(mid, c) < 0:
            hi = mid
        else:
            lo = mid
    return 1 - 2 * hi


def plant_pair(adj: list[int], A: int, R: int) -> list[int]:
    """The graph with every `A–R` edge deleted: the law of `G(n, p)` conditioned
    on `(A, R)` being an empty pair (`A`, `R` disjoint masks)."""
    if A & R:
        raise ValueError("A and R must be disjoint")
    out = []
    for v, nb in enumerate(adj):
        if A >> v & 1:
            out.append(nb & ~R)
        elif R >> v & 1:
            out.append(nb & ~A)
        else:
            out.append(nb)
    return out


def plant_cover(n: int, m: int, d: int, A: int, R: int, rng: np.random.Generator) -> np.ndarray:
    """A `customers × patterns` 0/1 matrix with `m` patterns, each a uniform
    `d`-subset of the `n` customers conditioned to meet at most one of `A`, `R`
    (rejection sampling): the clique-cover model given `(A, R)` empty."""
    if A & R:
        raise ValueError("A and R must be disjoint")
    M = np.zeros((n, m), dtype=np.int8)
    j = 0
    while j < m:
        rows = rng.choice(n, d, replace=False)
        mask = sum(1 << int(c) for c in rows)
        if mask & A and mask & R:
            continue
        M[rows, j] = 1
        j += 1
    return M


def overlap_table(P: tuple[int, int], Q: tuple[int, int], n: int) -> list[int]:
    """The `3 × 3` overlap table of two pairs, `(|A ∩ A′|, |A ∩ R′|, |A ∩ S′|,
    |R ∩ A′|, |R ∩ R′|, |R ∩ S′|, |S ∩ A′|, |S ∩ R′|, |S ∩ S′|)`; sums to `n`."""
    full = (1 << n) - 1
    A, R = P
    A2, R2 = Q
    cls = (A, R, full & ~(A | R))
    cls2 = (A2, R2, full & ~(A2 | R2))
    return [popcount(x & y) for x in cls for y in cls2]


def hamming_distance(P: tuple[int, int], Q: tuple[int, int], n: int) -> int:
    """The number of vertices whose class (`A`, `R` or `S`) differs between the
    two pairs: `n − |A ∩ A′| − |R ∩ R′| − |S ∩ S′|`."""
    full = (1 << n) - 1
    A, R = P
    A2, R2 = Q
    S, S2 = full & ~(A | R), full & ~(A2 | R2)
    return n - popcount(A & A2) - popcount(R & R2) - popcount(S & S2)


def lq_sides(n: int, t: int, r: int, s: int) -> float:
    """`log P(a uniform s-subset of n meets at most one of two disjoint sets of
    sizes t and r)` = `log [(C(n−t, s) + C(n−r, s) − C(n−t−r, s)) / C(n, s)]`
    (the general-`r` form of `learning.first_moment.lq`, which has `r = t − 1`)."""
    from learning.first_moment import lchoose
    terms = [lchoose(n - t, s), lchoose(n - r, s)]
    neg = lchoose(n - t - r, s)
    m = max(terms)
    if m == -math.inf:
        return -math.inf
    val = math.exp(terms[0] - m) + math.exp(terms[1] - m) - (math.exp(neg - m) if neg > -math.inf else 0.0)
    if val <= 0:
        return -math.inf
    return m + math.log(val) - lchoose(n, s)


def second_moment_exact_cover(n: int, t: int, r: int, sizes) -> tuple[float, float, float]:
    """`(log E[X], log E[X²], E[X²] / E[X]²)` for `X` the number of ordered empty
    pairs `(A, R)`, `|A| = t`, `|R| = r`, in the cover model with the given
    pattern sizes (a list or `{size: count}`), exactly, by the sum over the
    `3 × 3` overlap table. The general-`r` form of
    `learning.first_moment.second_moment_exact` (`r = t − 1` there)."""
    from math import lgamma
    from learning.first_moment import _histogram, _lchoose_table, _pair_square_structure, lchoose
    hist = _histogram(sizes)
    st = _pair_square_structure()
    o = n - t - r
    if o < 0:
        return math.inf, math.inf, math.nan
    logEX = lchoose(n, t) + lchoose(n - t, r) + sum(cnt * lq_sides(n, t, r, s) for s, cnt in hist.items())
    tabs = []
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
                    tabs.append((aa, ar, ao, ra, rr, ro, oa, orr, oo))
    tabs = np.array(tabs, dtype=int)
    logmult = lgamma(n + 1) - np.vectorize(lgamma)(tabs + 1).sum(axis=1)
    logp = np.zeros(len(tabs))
    for s, cnt in hist.items():
        lch = _lchoose_table(n, s)
        logp += cnt * st.log_avoid(tabs.astype(float), n, s, lch)
    terms = logmult + logp
    mx = terms.max()
    logEX2 = float(mx + math.log(np.exp(terms - mx).sum()))
    return logEX, logEX2, math.exp(logEX2 - 2 * logEX)


def planted_mean_gnp(n: int, t: int, r: int, p: float) -> float:
    """`E[X′ | P₀ empty] = E[X²] / E[X] − 1` on `G(n, p)`: the expected number of
    *other* exact-size empty pairs given one planted pair."""
    logEX, logEX2, _ = second_moment_exact_gnp(n, t, r, p)
    return math.exp(logEX2 - logEX) - 1


def planted_mean_cover(n: int, t: int, r: int, sizes) -> float:
    """`E[X′ | P₀ empty] = E[X²] / E[X] − 1` in the cover model."""
    logEX, logEX2, _ = second_moment_exact_cover(n, t, r, sizes)
    return math.exp(logEX2 - logEX) - 1


# ---------------------------------------------------------------------------
# item 05: the inner probability P_N(E_bip) and P_N(E_relax) of G(N, p), exactly
# ---------------------------------------------------------------------------
#
# For a fixed k-set S, G − S is G(N, p) with N = n − k, and the separator count
# is C(n, k) · P_N(E_bip) (§2, L1′).  P_N(E_bip) is a sum over the multiset λ of
# component sizes of G(N, p): the probability of the multiset is
#     P(λ) = N! / (Π λ_i! Π_s m_s!) · Π C_{λ_i}(p) · (1 − p)^{(N² − Σ λ_i²)/2},
# with C_j(p) the probability that G(j, p) is connected (Gilbert's recursion,
# which cancels catastrophically at small p and is done in mpmath), and E_bip
# holds iff a sub-multiset of λ sums to t.  Writing a(s) = log C_s − log s! −
# (s²/2) log(1 − p), P(λ) = N! (1 − p)^{N²/2} Π_s e^{m_s a(s)} / m_s!, which is
# the exponential formula: Σ_λ Π_s e^{m_s a(s)} / m_s! = [x^N] exp(Σ_s e^{a(s)} x^s).
# E_relax (no component larger than M) is that coefficient with the sum cut at
# s ≤ M, an O(N · M) recursion; E_bip needs the subset-sum condition, which is
# carried as a bitset through a memoised recursion over the part sizes.


def connected_probs(N: int, p, dps: int | None = None) -> list:
    """`[C_0, C_1, …, C_N]` as `mpmath.mpf`: `C_j` is the probability that
    `G(j, p)` is connected, by Gilbert's recursion
    `C_1 = 1`, `C_j = 1 − Σ_{i<j} C(j−1, i−1) C_i (1−p)^{i(j−i)}`
    (the sum is the probability that the component of vertex 1 has `i < j`
    vertices).  The subtraction cancels to `C_j ≈ e^{−j(1−p)^{j}}` at small `p`,
    so the working precision grows with the expected number of isolated
    vertices (`dps = 60 + 0.6·N·(1−p)^N` digits by default)."""
    import mpmath as mp
    if dps is None:
        iso = N * (1 - float(p)) ** max(N - 1, 0)
        dps = 60 + int(0.6 * iso) + 2
    with mp.workdps(dps):
        q = mp.mpf(1) - mp.mpf(p)
        qpow = [mp.mpf(1)]
        for _ in range(N * N // 4 + N + 1):
            qpow.append(qpow[-1] * q)
        C = [mp.mpf(0)] * (N + 1)
        if N >= 1:
            C[1] = mp.mpf(1)
        for j in range(2, N + 1):
            s = mp.mpf(0)
            for i in range(1, j):
                s += comb(j - 1, i - 1) * C[i] * qpow[i * (j - i)]
            C[j] = 1 - s
        return [+c for c in C]


def log_connected(N: int, p, dps: int | None = None) -> list[float]:
    """`[−inf, log C_1, …, log C_N]` as floats, from `connected_probs`."""
    import mpmath as mp
    C = connected_probs(N, p, dps)
    out = [-math.inf]
    for c in C[1:]:
        out.append(float(mp.log(c)) if c > 0 else -math.inf)
    return out


def partitions(N: int, max_part: int | None = None) -> Iterator[tuple[int, ...]]:
    """The partitions of `N` with parts `≤ max_part`, each as a non-increasing
    tuple; `partitions(0)` yields the empty tuple once."""
    if max_part is None or max_part > N:
        max_part = N
    if N == 0:
        yield ()
        return
    for s in range(min(N, max_part), 0, -1):
        for rest in partitions(N - s, s):
            yield (s,) + rest


def _log_q(p) -> float:
    return math.log1p(-float(p))


def _part_weights(N: int, p, logC: list[float] | None = None, tilt: float = 0.0) -> list[float]:
    """`a(s) = log C_s − log s! − (s²/2) log(1 − p) + tilt` for `s = 0 … N`.
    A `tilt` of `ln 2` weights every partition by `2^{#parts}` (item 06's
    combined count, which bounds the number of balanced 2-colourings of the
    components by `2^κ`)."""
    if logC is None:
        logC = log_connected(N, p)
    lq_ = _log_q(p)
    return [-math.inf] + [logC[s] - math.lgamma(s + 1) - (s * s / 2) * lq_ + tilt for s in range(1, N + 1)]


def log_prob_partition(parts, N: int, p, logC: list[float] | None = None) -> float:
    """`log P(the component sizes of G(N, p) are the multiset `parts`)`,
    `N!/(Π λ_i! Π_s m_s!) · Π C_{λ_i}(p) · (1−p)^{(N² − Σ λ_i²)/2}`;
    requires `sum(parts) == N`."""
    parts = tuple(parts)
    if sum(parts) != N:
        raise ValueError("the parts must sum to N")
    if logC is None:
        logC = log_connected(N, p)
    lq_ = _log_q(p)
    out = math.lgamma(N + 1) + ((N * N - sum(s * s for s in parts)) / 2) * lq_
    mult: dict[int, int] = {}
    for s in parts:
        mult[s] = mult.get(s, 0) + 1
    for s, m in mult.items():
        out += m * (logC[s] - math.lgamma(s + 1)) - math.lgamma(m + 1)
    return out


def _lse(values) -> float:
    vals = [v for v in values if v != -math.inf]
    if not vals:
        return -math.inf
    mx = max(vals)
    return mx + math.log(sum(math.exp(v - mx) for v in vals))


def _coefficient_table(N: int, a: list[float], max_part: int) -> list[list[float]]:
    """`W[r][s] = log [x^r] exp(Σ_{u ≤ s} e^{a(u)} x^u)` for `r ≤ N`, `s ≤ max_part`:
    the weight of all partitions of `r` into parts `≤ s`, by the recursion on
    the multiplicity of the largest part."""
    W = [[-math.inf] * (max_part + 1) for _ in range(N + 1)]
    for s in range(max_part + 1):
        W[0][s] = 0.0
    for s in range(1, max_part + 1):
        for r in range(1, N + 1):
            terms = [W[r][s - 1]]
            m = 1
            while m * s <= r:
                terms.append(m * a[s] - math.lgamma(m + 1) + W[r - m * s][s - 1])
                m += 1
            W[r][s] = _lse(terms)
    return W


def log_prob_rel(N: int, p, M: int, logC: list[float] | None = None, tilt: float = 0.0) -> float:
    """`log P(no component of G(N, p) has more than M vertices)`, by the
    `O(N · M)` recursion over the component of the first vertex
    (`R_j = Σ_{i ≤ min(j, M)} C(j−1, i−1) C_i (1−p)^{i(j−i)} R_{j−i}`, `R_0 = 1`),
    computed as the coefficient `N! (1−p)^{N²/2} [x^N] exp(Σ_{s ≤ M} e^{a(s)} x^s)`.
    With `tilt = τ` it is `log E[1[no component > M] · e^{τ κ}]`, `κ` the
    number of components (not a probability; `τ = ln 2` is item 06's use)."""
    if M >= N and tilt == 0.0:
        return 0.0
    if M <= 0:
        return -math.inf if N > 0 else 0.0
    M = min(M, N)
    a = _part_weights(N, p, logC, tilt)
    W = _coefficient_table(N, a, M)
    val = math.lgamma(N + 1) + (N * N / 2) * _log_q(p) + W[N][M]
    return min(0.0, val) if tilt == 0.0 else val


def log_prob_rel_fast(N: int, p, M: int, logC: list[float] | None = None, tilt: float = 0.0) -> float:
    """The same quantity as `log_prob_rel` by the derivative recursion of the
    exponential formula: with `f = exp(Σ_{s ≤ M} e^{a(s)} x^s)`,
    `r [x^r] f = Σ_{s ≤ min(r, M)} s e^{a(s)} [x^{r−s}] f`, which is `O(N · M)`
    with one log-sum-exp per `r` (no multiplicity loop).  Used for the rate
    grids of item 06; pinned to `log_prob_rel` in the tests."""
    if M <= 0:
        return -math.inf if N > 0 else 0.0
    M = min(M, N)
    a = _part_weights(N, p, logC, tilt)
    la = np.array([(-math.inf if s == 0 else a[s] + math.log(s)) for s in range(M + 1)])
    W = np.full(N + 1, -math.inf)
    W[0] = 0.0
    for r in range(1, N + 1):
        top = min(r, M)
        terms = la[1:top + 1] + W[r - 1::-1][:top]
        mx = terms.max()
        W[r] = mx + math.log(np.exp(terms - mx).sum()) - math.log(r)
    val = math.lgamma(N + 1) + (N * N / 2) * _log_q(p) + W[N]
    return min(0.0, val) if tilt == 0.0 else val


def log_prob_bip(N: int, p, t: int | None = None, logC: list[float] | None = None,
                 stats: dict | None = None, t_hi: int | None = None, tilt: float = 0.0) -> float:
    """`log P_N(E_bip)`: the probability that the components of `G(N, p)` can be
    grouped into two sides of sizes `t` and `N − t` (`t = ⌈N/2⌉` by default),
    exactly, as the sum of `P(λ)` over the partitions `λ ⊢ N` with a sub-multiset
    summing to `t`.  The sum runs by a memoised recursion over the part sizes
    (largest first) with the set of achievable sub-sums as a bitset; a branch
    whose bitset already contains `t` is closed by the coefficient table (every
    completion qualifies), a part larger than `t` closes a branch at zero.
    `stats`, if given, receives the number of memo states.
    With `t_hi` the event is the *window* form `E_win`: a sub-multiset summing
    to some `x ∈ [t, t_hi]` (one side between `t` and `t_hi` vertices); with
    `tilt = τ` the sum is `E[1[E] e^{τ κ}]` over the number of components `κ`
    (item 06's combined count; not a probability when `τ ≠ 0`)."""
    if t is None:
        t = (N + 1) // 2
    if t_hi is None:
        t_hi = t
    if not 0 <= t <= t_hi <= N:
        raise ValueError("need 0 <= t <= t_hi <= N")
    if N == 0:
        return 0.0
    a = _part_weights(N, p, logC, tilt)
    smax = max(t_hi, N - t)
    W = _coefficient_table(N, a, smax)
    memo: dict[tuple[int, int, int], float] = {}
    full_t = (1 << (t_hi + 1)) - 1
    window = full_t & ~((1 << t) - 1)

    def F(r: int, s: int, B: int) -> float:
        # partitions of r into parts <= s, weighted, given the achievable sums B
        if B & window:
            return W[r][s]
        lo = t - r
        Bm = B & full_t
        if lo > 0:
            Bm &= ~((1 << lo) - 1)
        if Bm == 0:
            return -math.inf
        if r == 0:
            return -math.inf  # t not reachable (bit t was not set)
        if s == 0:
            return -math.inf
        s = min(s, r)
        key = (r, s, Bm)
        got = memo.get(key)
        if got is not None:
            return got
        terms = [F(r, s - 1, Bm)]
        Bs = Bm
        m = 1
        while m * s <= r:
            Bs = Bs | (Bs << s)
            terms.append(m * a[s] - math.lgamma(m + 1) + F(r - m * s, s - 1, Bs))
            m += 1
        val = _lse(terms)
        memo[key] = val
        return val

    import sys
    old = sys.getrecursionlimit()
    if old < 4 * N + 100:
        sys.setrecursionlimit(4 * N + 100)
    try:
        inner = F(N, smax, 1)
    finally:
        sys.setrecursionlimit(old)
    if stats is not None:
        stats["states"] = len(memo)
    val = math.lgamma(N + 1) + (N * N / 2) * _log_q(p) + inner
    return min(0.0, val) if tilt == 0.0 else val


def log_product_bound(N: int, p, t: int | None = None) -> float:
    """`log [C(N, t) (1 − p)^{t(N − t)}]`, the union bound over the bipartitions
    that the pair count uses for the same event."""
    if t is None:
        t = (N + 1) // 2
    return math.lgamma(N + 1) - math.lgamma(t + 1) - math.lgamma(N - t + 1) + t * (N - t) * _log_q(p)


def _labelled_graphs(N: int):
    pairs = list(combinations(range(N), 2))
    for mask in range(1 << len(pairs)):
        adj = [0] * N
        e = 0
        for i, (u, v) in enumerate(pairs):
            if mask >> i & 1:
                adj[u] |= 1 << v
                adj[v] |= 1 << u
                e += 1
        yield adj, e


def log_connected_enum(N: int, p) -> float:
    """`log C_N(p)` by enumeration of every labelled graph on `N ≤ 7` vertices."""
    lp, lq_ = math.log(float(p)), _log_q(p)
    terms = []
    full = (1 << N) - 1
    for adj, e in _labelled_graphs(N):
        if len(components(adj, full)) == 1:
            terms.append(e * lp + (N * (N - 1) // 2 - e) * lq_)
    return _lse(terms)


def log_prob_bip_enum(N: int, p, t: int | None = None) -> float:
    """`log P_N(E_bip)` by enumeration of every labelled graph on `N ≤ 7` vertices."""
    if t is None:
        t = (N + 1) // 2
    lp, lq_ = math.log(float(p)), _log_q(p)
    terms = []
    full = (1 << N) - 1
    for adj, e in _labelled_graphs(N):
        sizes = [popcount(c) for c in components(adj, full)]
        if _subset_sum(sizes, t):
            terms.append(e * lp + (N * (N - 1) // 2 - e) * lq_)
    return _lse(terms)


def log_connected_mc(N: int, p, samples: int, seed: int = 0) -> tuple[float, float]:
    """Monte Carlo `(log Ĉ_N, standard error of Ĉ_N)` with `networkx` graphs."""
    import networkx as nx
    rng = random.Random(seed)
    hits = 0
    for _ in range(samples):
        G = nx.fast_gnp_random_graph(N, float(p), seed=rng.randrange(1 << 30))
        hits += nx.is_connected(G)
    phat = hits / samples
    return (math.log(phat) if hits else -math.inf), math.sqrt(phat * (1 - phat) / samples)


def log_prob_bip_mc(N: int, p, t: int | None = None, samples: int = 10000, seed: int = 0) -> tuple[float, float]:
    """Monte Carlo `(log P̂_N(E_bip), standard error of P̂)` on `gnp_masks`."""
    if t is None:
        t = (N + 1) // 2
    full = (1 << N) - 1
    hits = 0
    for i in range(samples):
        adj = gnp_masks(N, float(p), seed + i)
        sizes = [popcount(c) for c in components(adj, full)]
        hits += _subset_sum(sizes, t)
    phat = hits / samples
    return (math.log(phat) if hits else -math.inf), math.sqrt(phat * (1 - phat) / samples)


# --- item 06: the constants β_sep, β_closed, β_comb on G(n, c/n) ---------------
#
# Exponents are per vertex of n, in nats; β = k/n; c′ = c(1 − β) is the mean
# degree of G − S; q(x) = 1 − e^{−cx}.  Every "rate" argument is a function
# I(c′) (or I(c′, u)) giving the exponential rate in N of the inner event; the
# three sources are the fitted rate (item 05 / the grids of item 06), the
# bracket's ends and the cited LDP rate of the largest component.

LN2 = math.log(2)


def H2(b: float) -> float:
    """Binary entropy in nats."""
    if b <= 0.0 or b >= 1.0:
        return 0.0
    return -b * math.log(b) - (1 - b) * math.log(1 - b)


def H3(a: float, r: float, s: float) -> float:
    """Entropy of (a, r, s) in nats, zeros allowed."""
    out = 0.0
    for x in (a, r, s):
        if x > 0:
            out -= x * math.log(x)
    return out


def ldp_K(rho: float, u: float) -> float:
    if u <= 0:
        return 0.0
    return u * math.log(rho * u / (1 - math.exp(-rho * u))) - rho * u * u / 2


def ldp_L(c: float, u: float) -> float:
    if u >= 1:
        return (c - math.log(c)) - c / 2
    return (1 - u) * math.log(1 - u) + (c - math.log(c)) * u - c * u * u / 2


def ldp_x_k(c: float, k: int) -> float:
    """The solution of `x/(1 − e^{−cx}) = 1 − k x` on `(0, 1/k)`, or 0."""
    lo, hi = 1e-12, 1.0 / k - 1e-12
    f = lambda x: x / (1 - math.exp(-c * x)) - (1 - k * x)
    if f(lo) > 0:
        return 0.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid) > 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def ldp_rate(c: float, u: float = 0.5) -> float:
    """`I_c^β(u)`: the large-deviation rate (scale `N`) for the largest
    component of `G(N, c/N)` to have `uN` vertices, in O'Connell's (1998) form
    as restated by Puhalskii (2005, *Ann. Probab.* 33, (2.13)–(2.14)):
    `I = k K_c(u) + L_c(k u)` on `[x_k, x_{k−1}]`.  Ported from item 01's
    `rate_check.py`; `P(no component > uN) ≤ e^{−(I(u) − o(1)) N}` for
    `u` below the typical giant, zero at and above it.  Checked by item 05
    against the exact finite computation to `0.0003–0.002` at seven `c`."""
    if c <= 0:
        return 0.0
    giant = _giant(c)
    if u >= giant:
        return 0.0
    if u <= 0:
        return ldp_L(c, max(0.0, 1 - 1 / c))
    k = 1
    while k <= 10000:
        xk = ldp_x_k(c, k)
        xk1 = 1.0 if k == 1 else ldp_x_k(c, k - 1)
        if xk <= u <= xk1 + 1e-15:
            return max(0.0, k * ldp_K(c, u) + ldp_L(c, k * u))
        k += 1
    return float("nan")


def _giant(c: float) -> float:
    if c <= 1:
        return 0.0
    lo, hi = 1e-12, 1 - 1e-12
    for _ in range(200):
        mid = (lo + hi) / 2
        if 1 - mid - math.exp(-c * mid) > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def rate_bracket(cp: float) -> tuple[float, float]:
    """The plan's analytic bracket on the rate of `E_bip` at mean degree `c′`:
    `[c′/4 − ln 2, min(c′/4, thinning)]` (lower end from the product bound,
    upper from one fixed bipartition and the thinning route); item 05 found the
    truth near the lower end plus the component gain."""
    lower = max(0.0, cp / 4 - LN2)
    thinning = cp / 2 - LN2 + LN2 * math.log(2 * LN2 / cp) if cp > 2 * LN2 else 0.0
    upper = min(cp / 4, thinning) if cp > 2 * LN2 else 0.0
    return lower, max(lower, upper)


def pair_exponent_beta(c: float, beta: float) -> float:
    """The pair count's exponent per vertex as a function of `β`:
    `H(β) − (1 − β)(c′/4 − ln 2)`, `c′ = c(1 − β)`; equal to
    `gnp_pair_rate((1 − β)/2, c)`."""
    cp = c * (1 - beta)
    return H2(beta) - (1 - beta) * (cp / 4 - LN2)


def sep_exponent(c: float, beta: float, rate) -> float:
    """The separator count's exponent `H(β) − (1 − β) I(c(1 − β))`, with `I`
    the rate of the inner event (`E_bip` or `E_relax`) in `N`."""
    return H2(beta) - (1 - beta) * rate(c * (1 - beta))


def _root_beta(f, tol: float = 1e-7) -> float:
    """The smallest `β ∈ (0, 1)` with `f(β) ≥ 0`, `f` scanned upward from
    `β = 0⁺`; 0 if `f(0⁺) ≥ 0` (the count excludes nothing)."""
    lo = 1e-6
    if f(lo) >= 0:
        return 0.0
    step = 1e-3
    b = lo
    while b < 1 - 1e-9:
        nb = min(b + step, 1 - 1e-9)
        if f(nb) >= 0:
            for _ in range(80):
                mid = (b + nb) / 2
                if f(mid) >= 0:
                    nb = mid
                else:
                    b = mid
                if nb - b < tol:
                    break
            return (b + nb) / 2
        b = nb
    return 1.0


def beta_sep(c: float, rate=ldp_rate) -> float:
    """`β_sep(c)`: the root of the separator exponent for the given rate
    function.  With `rate = lambda cp: rate_bracket(cp)[0]` it is `β*(c)`
    exactly (the lower end is the pair count's own rate); with `ldp_rate` it
    is the cited column; with a fitted rate the fitted column."""
    return _root_beta(lambda b: sep_exponent(c, b, rate))


def exponent_slope_at(c: float, beta: float, h: float = 1e-4) -> float:
    """`d/dβ` of the pair exponent at `β` (nats per unit of `β`), the
    conversion from a gain in nats per vertex to a gain in `β`."""
    return (pair_exponent_beta(c, beta + h) - pair_exponent_beta(c, beta - h)) / (2 * h)


# closed pairs ------------------------------------------------------------------

def _log_q_frac(c: float, x: float) -> float:
    """`ln q(x) = ln(1 − e^{−cx})`, `−∞` at `x = 0`."""
    if x <= 0:
        return -math.inf
    return math.log(-math.expm1(-c * x))


def closed_exponent(a: float, r: float, s: float, c: float, with_q: bool = True) -> float:
    """Exponent per vertex of the closed-pair first moment at side fractions
    `(a, r, s)`, `a + r + s = 1`: `H(a, r, s) − c a r + s ln q(a) + s ln q(r)`.
    Derivation (L2 of §2 and the Bernoulli edges): ordered triples `(A, R, S)`
    with no `A–R` edge, probability `(1 − p)^{|A||R|} → e^{−c a r n}`, and every
    vertex of `S` adjacent to `A` and to `R` — for distinct `v ∈ S` these
    events involve disjoint edge sets, so given `(A, R)` they are independent
    with probability `(1 − (1 − p)^{|A|})(1 − (1 − p)^{|R|}) → q(a) q(r)`.
    `with_q=False` drops the two `q` terms (used to pin the exponent to the
    pair exponent at the corner `a = r = (1 − β)/2`, `s = β`)."""
    out = H3(a, r, s) - c * a * r
    if with_q and s > 0:
        out += s * (_log_q_frac(c, a) + _log_q_frac(c, r))
    return out


def closed_rate(beta: float, c: float, grid: int = 60) -> tuple[float, float, float]:
    """`sup` of the closed exponent over the admissible region
    `a, r ≥ (1 − β)/2`, `s = 1 − a − r ∈ [0, β]` (L2: sides at least the
    forced sizes, `|S| ≤ k`); returns `(value, a, r)`.  A grid over the
    triangle followed by a local refinement from the best grid point."""
    lo = (1 - beta) / 2
    best = (-math.inf, lo, lo)
    for i in range(grid + 1):
        a = lo + (1 - 2 * lo) * i / grid
        for j in range(grid + 1 - i):
            r = lo + (1 - 2 * lo) * j / grid
            s = max(0.0, 1 - a - r)
            v = closed_exponent(a, r, s, c)
            if v > best[0]:
                best = (v, a, r)
    try:
        from scipy.optimize import minimize
    except ImportError:  # pragma: no cover
        return best
    def neg(x):
        a, r = x
        s = 1 - a - r
        if a < lo or r < lo or s < -1e-12:
            return 1e9
        return -closed_exponent(a, r, max(s, 0.0), c)
    res = minimize(neg, [best[1], best[2]], method="Nelder-Mead",
                   options={"xatol": 1e-9, "fatol": 1e-12, "maxiter": 4000})
    if -res.fun > best[0]:
        a, r = res.x
        best = (-res.fun, a, r)
    return best


def beta_closed(c: float) -> float:
    """`β_closed(c)`: the root in `β` of `closed_rate(β, c)`."""
    return _root_beta(lambda b: closed_rate(b, c, grid=40)[0], tol=1e-6)


def log_closed_count(n: int, k: int, p: float) -> float:
    """`log E[X₃]` on `G(n, p)`: the finite closed-pair count
    `Σ_{a ≥ t, r ≥ N − t, a + r + s = n, s ≤ k} n!/(a! r! s!) (1 − p)^{ar}
    (1 − (1 − p)^a)^s (1 − (1 − p)^r)^s`, ordered pairs `(A, R)` (L2's sizes:
    `N = n − k`, `t = ⌈N/2⌉`)."""
    N, t = forced_sizes(n, k)
    lq_ = _log_q(p)
    terms = []
    for s in range(0, k + 1):
        for a in range(t, n - s + 1):
            r = n - s - a
            if r < N - t:
                continue
            v = (math.lgamma(n + 1) - math.lgamma(a + 1) - math.lgamma(r + 1) - math.lgamma(s + 1)
                 + a * r * lq_)
            if s > 0:
                if a == 0 or r == 0:
                    continue  # a separator vertex cannot see an empty side
                v += s * (math.log(-math.expm1(a * lq_)) + math.log(-math.expm1(r * lq_)))
            terms.append(v)
    return _lse(terms)


# the combined count ----------------------------------------------------------------
#
# Closed pairs grouped by their separator S* (|S*| = s′ ≤ k).  Given G − S, the
# empty bipartitions (A, R) with |A| ∈ [t, t + k − s′] (the window, so that
# |R| ≥ N − t) are 2-colourings of the components, at most 2^κ of them, and
# each is closed with probability Π_{v ∈ S} q_{|A|} q_{|R|} ≤ Qmax(s′)^{s′}
# (edges from S to G − S are independent of G − S).  So
#
#   P(pw ≤ k) ≤ Σ_{s′ ≤ k} C(n, s′) Qmax(s′)^{s′} E_{N′ = n − s′}[1[E_win] 2^κ],
#
# with E_win relaxed, if wanted, to "no component larger than t + k − s′".

def _log_qmax(n: int, k: int, s: int, p: float) -> float:
    """`max` over the window of `ln[(1 − (1−p)^a)(1 − (1−p)^r)]`, attained at the
    most balanced split (`ln q` is concave)."""
    N, t = forced_sizes(n, k)
    Np = n - s
    lq_ = _log_q(p)
    best = -math.inf
    for a in range(t, Np - (N - t) + 1):
        r = Np - a
        if a == 0 or r == 0:
            continue
        v = math.log(-math.expm1(a * lq_)) + math.log(-math.expm1(r * lq_))
        best = max(best, v)
    return best


def log_combined_count(n: int, k: int, p: float, form: str = "rel", s_min: int = 0,
                       logC_cache: dict | None = None) -> float:
    """`log` of the combined first moment above, with the inner factor exact:
    `form="rel"` uses the relaxed window event (`log_prob_rel_fast`, `O(N²)`),
    `form="bip"` the bipartition window event (`log_prob_bip` with `t_hi`,
    exact but slow above `N ≈ 120`).  `s_min` restricts the sum to
    `s′ ≥ s_min` (a lower bound on the count, for timing)."""
    N, t = forced_sizes(n, k)
    terms = []
    for s in range(s_min, k + 1):
        Np = n - s
        t_hi = Np - (N - t)
        key = Np
        if logC_cache is not None and key in logC_cache:
            lc = logC_cache[key]
        else:
            lc = log_connected(Np, p)
            if logC_cache is not None:
                logC_cache[key] = lc
        if form == "rel":
            inner = log_prob_rel_fast(Np, p, t_hi, lc, tilt=LN2)
        elif form == "bip":
            inner = log_prob_bip(Np, p, t, lc, t_hi=t_hi, tilt=LN2)
        else:
            raise ValueError(form)
        v = lchoose(n, s) + inner
        if s > 0:
            v += s * _log_qmax(n, k, s, p)
        terms.append(v)
    return _lse(terms)


def lchoose(n: int, k: int) -> float:
    if k < 0 or k > n:
        return -math.inf
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def combined_exponent(c: float, beta: float, s: float, tilted_rate) -> float:
    """Per-vertex exponent of the combined count's `s′ = s n` term:
    `H(s) + 2 s ln q((1 − s)/2) − (1 − s) J(c(1 − s), u)`, with
    `u = ((1 + β)/2 − s)/(1 − s)` the largest allowed component as a fraction
    of `N′` and `J(c′, u)` the rate of `E[1[no component > uN′] 2^κ]` in `N′`
    (fitted; there is no LDP to cite for the tilted event)."""
    if s > beta + 1e-12:
        return -math.inf
    u = ((1 + beta) / 2 - s) / (1 - s)
    out = H2(s) - (1 - s) * tilted_rate(c * (1 - s), u)
    if s > 0:
        out += 2 * s * _log_q_frac(c, (1 - s) / 2)
    return out


def combined_rate(c: float, beta: float, tilted_rate, points: int = 41) -> tuple[float, float]:
    """`sup_{s ∈ [0, β]}` of `combined_exponent`; returns `(value, s)`."""
    best = (-math.inf, 0.0)
    for i in range(points + 1):
        s = beta * i / points
        v = combined_exponent(c, beta, s, tilted_rate)
        if v > best[0]:
            best = (v, s)
    return best


def beta_combined(c: float, tilted_rate) -> float:
    """`β_comb(c)`: the root of `combined_rate(c, β)`."""
    return _root_beta(lambda b: combined_rate(c, b, tilted_rate)[0], tol=1e-6)


# the published upper line --------------------------------------------------------

def edwards_mcdermid_g(dmax: int, alpha: float = 1 / 6) -> list[float]:
    """`g_α(d)` of Edwards & McDermid (2015, *Algorithmica* 72:940, p. 6):
    `g(2) = 0`, `g(3) = α`, `d g(d) = (d − 2) g(d − 1) + g(d − 2) + 1`."""
    g = [0.0] * (dmax + 1)
    if dmax >= 3:
        g[3] = alpha
    for d in range(4, dmax + 1):
        g[d] = ((d - 2) * g[d - 1] + g[d - 2] + 1) / d
    return g


def edwards_mcdermid_poisson(c: float, dmax: int = 200) -> float:
    """`Σ_{d ≥ 3} P(Poisson(c) = d) g_{1/6}(d)`: Corollary 5.2 of Edwards &
    McDermid (2015) on the limiting degree distribution of `G(n, c/n)`, the
    published upper line `pw/n ≤ …` whp (0.183, 0.458, 0.656 at c = 3, 6, 10;
    `reports/random_graph_pathwidth_literature_2.md` §3.3)."""
    g = edwards_mcdermid_g(dmax)
    out = 0.0
    lp = -c
    for d in range(0, dmax + 1):
        if d >= 3:
            out += math.exp(lp) * g[d]
        lp += math.log(c) - math.log(d + 1)
    return out


# ---------------------------------------------------------------------------
# item 07: the MOSP version — random clique covers
# ---------------------------------------------------------------------------
#
# The cover model of `CliqueCoverMoment.lean`: `m` independent patterns, pattern
# `j` a uniform `s_j`-subset of the `n` customers, the MOSP graph the union of
# the cliques.  For a partition `(A, R, S)` of the customers, `(A, R)` is empty
# iff no pattern meets both (L3 a), and `(A, R)` is a *closed* pair with
# separator `S` iff in addition every `v ∈ S` shares a pattern with `A` and one
# with `R` (L3 c).  Three quantities of this item:
#
# * `closed_cover_log_prob_exact`: `P(closed | A, R, S)` by inclusion–exclusion
#   over the "bad" vertices of `S` — those sharing no pattern with `A`
#   (`T_A`) or none with `R` (`T_R`).  Given `T_A`, `T_R`, a pattern is
#   allowed iff it lies in `S`, or meets `R` inside `R ∪ (S ∖ T_R)`, or meets
#   `A` inside `A ∪ (S ∖ T_A)`; the count depends only on `u = |S ∖ T_R|` and
#   `w = |S ∖ T_A|`, so the `4^|S|` terms collapse to `(|S| + 1)²`, summed in
#   exact integers (the alternation cancels catastrophically in floating point).
# * `closed_cover_log_prob_na`: a cancellation-free upper bound on the same
#   probability.  Conditional on each pattern's type (`A`-type: meets `A`,
#   avoids `R`; `R`-type; inside `S`) and on `|P_j ∩ A|`, the `S`-parts of the
#   patterns are independent uniform subsets of `S` of fixed sizes, whose
#   membership indicators are negatively associated (sampling without
#   replacement; Joag-Dev & Proschan 1983, Theorem 2.11 and property P7), so the
#   coverage indicators `C_v = max_j Y_{jv}` (nondecreasing functions of
#   disjoint index sets, property P6) are negatively associated and
#   `P(all covered | τ) ≤ Π_v P(C_v | τ)` = `(1 − e^{−L̃_A})^{|S|} (1 − e^{−L̃_R})^{|S|}`
#   with `L̃_A = −Σ_{j A-type} ln(1 − (s_j − i_j)/|S|)`.  `ln(1 − e^{−L})` is
#   concave, so the tangent at any `ℓ*` gives
#   `F(L̃) ≤ F(ℓ*) e^{θ (min(L̃, M) − ℓ*)}`, `θ = |S| e^{−ℓ*}/(1 − e^{−ℓ*})`,
#   `M = ℓ* − ln F(ℓ*)/θ` (the cap handles a pattern covering all of `S`), and
#   the expectation over the types factorises over the patterns.  Valid for
#   every `ℓ*`; minimised over `ℓ*`.
# * the flips (the weighted count `Y = Σ_P 1[P empty] / C(I_A + I_R, I_A)`,
#   with `I_A` the customers of `A` isolated in the `A`-side graph): the
#   binomial moments of `(I_A, I_R)` jointly with the empty event, exactly, and
#   the isolated-customer generating function of a random cover.


def _hist(sizes) -> dict[int, int]:
    from learning.first_moment import _histogram
    return _histogram(sizes)


def closed_cover_log_prob_exact(n: int, a: int, r: int, s: int, sizes) -> float:
    """`log P((A, R) closed with separator S)` for fixed disjoint `A, R, S` of
    sizes `a, r, s` (`a + r + s = n`) in the cover model, exactly (integers)."""
    if a + r + s != n or min(a, r, s) < 0:
        raise ValueError("a + r + s must equal n")
    hist = _hist(sizes)
    num = 0
    for u in range(s + 1):
        for w in range(s + 1):
            term = comb(s, u) * comb(s, w)
            for sz, cnt in hist.items():
                allowed = comb(s, sz) + comb(r + u, sz) - comb(u, sz) + comb(a + w, sz) - comb(w, sz)
                term *= allowed ** cnt
            num += -term if (u + w) & 1 else term
    if num < 0:
        raise ArithmeticError("negative probability numerator")
    if num == 0:
        return -math.inf
    den = 0.0
    for sz, cnt in hist.items():
        den += cnt * math.log(comb(n, sz))
    return math.log(num) - den


def closed_cover_log_count_exact(n: int, k: int, sizes) -> float:
    """`log E[X₃]` on covers: `Σ_{a ≥ t, r ≥ N − t, s ≤ k} n!/(a! r! s!) P(closed)`,
    the exact probability per triple (small `n` only)."""
    N, t = forced_sizes(n, k)
    terms = []
    for s in range(0, k + 1):
        for a in range(t, n - s + 1):
            r = n - s - a
            if r < N - t:
                continue
            lp = closed_cover_log_prob_exact(n, a, r, s, sizes)
            if lp == -math.inf:
                continue
            terms.append(math.lgamma(n + 1) - math.lgamma(a + 1) - math.lgamma(r + 1) - math.lgamma(s + 1) + lp)
    return _lse(terms)


def _type_tables(n: int, a: int, r: int, s: int, sz: int):
    """Per pattern size: `(w_S, wA, lA, wR, lR)` — the weight of "inside S",
    and for the `A`-type (`R`-type) outcomes `i = 1..sz` the weights
    `C(a, i) C(s, sz − i)` and the coverage increments `ℓ̃_i = −ln(1 − (sz − i)/s)`
    (`inf` where the pattern covers all of `S`)."""
    i = np.arange(1, sz + 1)
    wA = np.array([comb(a, int(x)) * comb(s, sz - int(x)) for x in i], dtype=float)
    wR = np.array([comb(r, int(x)) * comb(s, sz - int(x)) for x in i], dtype=float)
    with np.errstate(divide="ignore"):
        frac = (sz - i) / s if s > 0 else np.where(sz - i > 0, np.inf, 0.0)
        ell = np.where(frac < 1, -np.log1p(-np.minimum(frac, 1 - 1e-300)), np.inf)
    ell = np.where(sz - i == 0, 0.0, ell)
    return float(comb(s, sz)), wA, ell, wR, ell.copy()


def closed_cover_log_prob_na(n: int, a: int, r: int, s: int, sizes, ells=None,
                             optimise: bool = True) -> float:
    """Upper bound on `log P(closed | A, R, S)`: the negative-association /
    tangent bound above, minimised over the tangent points `(ℓ*_A, ℓ*_R)`
    (from the candidates `ells`, a list of pairs, then Nelder–Mead if
    `optimise`), and never above the empty-pair probability itself."""
    hist = _hist(sizes)
    lq_pair = sum(cnt * lq_sides(n, a, r, sz) for sz, cnt in hist.items())
    if s == 0 or lq_pair == -math.inf:
        return lq_pair
    tables = {sz: _type_tables(n, a, r, s, sz) for sz in hist}
    logC = {sz: math.log(comb(n, sz)) for sz in hist}

    def bound(lA, lR):
        if lA <= 0 or lR <= 0:
            return math.inf
        lA, lR = min(lA, 40.0), min(lR, 40.0)
        out = 0.0
        pars = []
        for l in (lA, lR):
            F = s * math.log(-math.expm1(-l))
            th = s * math.exp(-l) / (-math.expm1(-l))
            cap = l - F / th
            out += F - th * l
            pars.append((th, cap))
        (thA, capA), (thR, capR) = pars
        with np.errstate(over="ignore", invalid="ignore"):
            for sz, cnt in hist.items():
                wS, wA, eA, wR, eR = tables[sz]
                tot = wS + float(np.dot(wA, np.exp(thA * np.minimum(eA, capA)))) \
                    + float(np.dot(wR, np.exp(thR * np.minimum(eR, capR))))
                if not (tot > 0) or math.isinf(tot):
                    return math.inf
                out += cnt * (math.log(tot) - logC[sz])
        return out

    # the conditional means of L̃_A, L̃_R given the pair is empty: the natural start
    means = []
    for side in (0, 1):
        num = den = 0.0
        for sz, cnt in hist.items():
            wS, wA, eA, wR, eR = tables[sz]
            w, e = (wA, eA) if side == 0 else (wR, eR)
            q = wS + wA.sum() + wR.sum()
            if q > 0:
                num += cnt * float(np.dot(w, np.where(np.isfinite(e), e, 0.0))) / q
            den += cnt
        means.append(max(num, 1e-9))
    cands = list(ells) if ells is not None else []
    for fA in (0.6, 0.8, 1.0, 1.25):
        for fR in (0.6, 0.8, 1.0, 1.25):
            cands.append((means[0] * fA, means[1] * fR))
    best = min(((bound(lA, lR), lA, lR) for lA, lR in cands), key=lambda x: x[0])
    if optimise and math.isfinite(best[0]):
        try:
            from scipy.optimize import minimize
            res = minimize(lambda x: bound(math.exp(min(max(x[0], -12.0), 4.0)), math.exp(min(max(x[1], -12.0), 4.0))),
                           [math.log(best[1]), math.log(best[2])], method="Nelder-Mead",
                           options={"xatol": 1e-4, "fatol": 1e-9, "maxiter": 400})
            if res.fun < best[0]:
                best = (float(res.fun), math.exp(res.x[0]), math.exp(res.x[1]))
        except ImportError:  # pragma: no cover
            pass
    return min(best[0], lq_pair)


def closed_cover_log_bound(n: int, k: int, sizes, optimise: bool = False) -> float:
    """`log` of the closed-pair first moment on covers at width `k`, every
    admissible triple bounded by `closed_cover_log_prob_na` (the candidate
    tangent points only unless `optimise`); a valid upper bound on
    `P(mospValue ≤ k + 1)` by L2/L3 and the union bound."""
    N, t = forced_sizes(n, k)
    terms = []
    for s in range(0, k + 1):
        for a in range(t, n - s + 1):
            r = n - s - a
            if r < N - t:
                continue
            lp = closed_cover_log_prob_na(n, a, r, s, sizes, optimise=optimise)
            if lp == -math.inf:
                continue
            terms.append(math.lgamma(n + 1) - math.lgamma(a + 1) - math.lgamma(r + 1) - math.lgamma(s + 1) + lp)
    return _lse(terms)


def cover_log_pair_bound(n: int, k: int, sizes, exact_sizes: bool = True) -> float:
    """The pair count on covers at the exact forced sizes (`|A| = t`,
    `|R| = N − t`; the Lean statement) or at the record's `|R| = t − 1`."""
    from learning.first_moment import lchoose, log_bound
    if not exact_sizes:
        return log_bound(n, sizes, k)
    N, t = forced_sizes(n, k)
    r = N - t
    hist = _hist(sizes)
    return lchoose(n, t) + lchoose(n - t, r) + sum(cnt * lq_sides(n, t, r, sz) for sz, cnt in hist.items())


# the asymptotic exponents -------------------------------------------------------

def _hist_fracs(sizes) -> list[tuple[int, float]]:
    hist = _hist(sizes)
    tot = sum(hist.values())
    return [(sz, cnt / tot) for sz, cnt in hist.items()]


def cover_pair_exponent(alpha: float, rho: float, sigma: float, mu: float, sizes) -> float:
    """`H(α, ρ, σ) + μ E_s ln[(1 − α)^s + (1 − ρ)^s − σ^s]`: the pair count's
    exponent at general side fractions (`learning.first_moment.rate` at
    `α = ρ`)."""
    out = H3(alpha, rho, sigma)
    for sz, p in _hist_fracs(sizes):
        q = (1 - alpha) ** sz + (1 - rho) ** sz - sigma ** sz
        out += mu * p * math.log(max(q, 1e-300))
    return out


def cover_pair_exponent_beta(beta: float, mu: float, sizes) -> float:
    a = (1 - beta) / 2
    return cover_pair_exponent(a, a, beta, mu, sizes)


def cover_exponent_slope_at(beta: float, mu: float, sizes, h: float = 1e-4) -> float:
    """`d/dβ` of the pair exponent (nats per unit of `β`): the conversion."""
    return (cover_pair_exponent_beta(beta + h, mu, sizes) - cover_pair_exponent_beta(beta - h, mu, sizes)) / (2 * h)


def cover_lambda(alpha: float, rho: float, sigma: float, mu: float, sizes) -> tuple[float, float]:
    """`(λ_A, λ_R)`: the mean number of `A`-type (`R`-type) patterns containing
    a given `v ∈ S`, given the pair is empty (asymptotic)."""
    lA = lR = 0.0
    for sz, p in _hist_fracs(sizes):
        q = (1 - alpha) ** sz + (1 - rho) ** sz - sigma ** sz
        lA += mu * p * sz * ((1 - rho) ** (sz - 1) - sigma ** (sz - 1)) / q
        lR += mu * p * sz * ((1 - alpha) ** (sz - 1) - sigma ** (sz - 1)) / q
    return lA, lR


def closed_cover_exponent_ind(alpha: float, rho: float, sigma: float, mu: float, sizes) -> float:
    """The closed-pair exponent *if the coverage events of the `σ n` separator
    customers were independent*: `pair exponent + σ [ln(1 − e^{−λ_A}) + ln(1 − e^{−λ_R})]`.
    An approximation, not a bound (coverage events are positively associated
    through shared patterns); it is the `G(n, c/n)` form of §6 (b)."""
    out = cover_pair_exponent(alpha, rho, sigma, mu, sizes)
    if sigma <= 0:
        return out
    lA, lR = cover_lambda(alpha, rho, sigma, mu, sizes)
    return out + sigma * (math.log(-math.expm1(-lA)) + math.log(-math.expm1(-lR)))


def _log_closed_na_mgf(alpha: float, rho: float, sigma: float, thA: float, thR: float, sz: int) -> float:
    """`ln[σ^s + (α + σ e^{ϑ_A})^s − (σ e^{ϑ_A})^s + (ρ + σ e^{ϑ_R})^s − (σ e^{ϑ_R})^s]`,
    each of the three non-negative pieces in log form (`ϑ` may be large)."""
    ls = math.log(sigma)
    parts = [sz * ls]
    for x, th in ((alpha, thA), (rho, thR)):
        if x <= 0:
            continue
        inner = sz * math.log1p(x * math.exp(-th) / sigma)       # ln (1 + x e^{−ϑ}/σ)^s
        if inner > 0:
            parts.append(sz * (ls + th) + (math.log(math.expm1(inner)) if inner < 700 else inner))
    return _lse(parts)


def closed_cover_exponent_na(alpha: float, rho: float, sigma: float, mu: float, sizes,
                             return_argmin: bool = False):
    """The negative-association / tangent exponent of the closed-pair count
    at side fractions `(α, ρ, σ)`: `H(α, ρ, σ) + inf_{ℓ_A, ℓ_R > 0} [σ ln(1 − e^{−ℓ_A})
    + σ ln(1 − e^{−ℓ_R}) − σ(ϑ_A ℓ_A + ϑ_R ℓ_R) + μ E_s ln M_s(ϑ_A, ϑ_R)]`,
    `ϑ = e^{−ℓ}/(1 − e^{−ℓ})`, `M_s` the per-pattern generating function of the
    `S`-incidences of `A`- and `R`-type patterns (with the empty event).  A valid
    exponent of an upper bound (the limit of `closed_cover_log_prob_na`)."""
    if sigma <= 0:
        v = cover_pair_exponent(alpha, rho, sigma, mu, sizes)
        return (v, (math.nan, math.nan)) if return_argmin else v
    fr = _hist_fracs(sizes)
    H = H3(alpha, rho, sigma)

    def f(x):
        lA, lR = math.exp(min(max(x[0], -12.0), 4.0)), math.exp(min(max(x[1], -12.0), 4.0))
        thA = math.exp(-lA) / (-math.expm1(-lA))
        thR = math.exp(-lR) / (-math.expm1(-lR))
        out = sigma * (math.log(-math.expm1(-lA)) + math.log(-math.expm1(-lR))) - sigma * (thA * lA + thR * lR)
        for sz, p in fr:
            out += mu * p * _log_closed_na_mgf(alpha, rho, sigma, thA, thR, sz)
        return out

    lA0, lR0 = cover_lambda(alpha, rho, sigma, mu, sizes)
    x0 = [math.log(max(lA0, 1e-6)), math.log(max(lR0, 1e-6))]
    from scipy.optimize import minimize
    res = minimize(f, x0, method="Nelder-Mead", options={"xatol": 1e-6, "fatol": 1e-10, "maxiter": 2000})
    v = H + min(float(res.fun), f(x0))
    if return_argmin:
        return v, (math.exp(res.x[0]), math.exp(res.x[1]))
    return v


def closed_cover_rate(beta: float, mu: float, sizes, method: str = "na", grid: int = 12) -> tuple[float, float, float]:
    """`sup` over the admissible region (`α, ρ ≥ (1 − β)/2`, `σ ≤ β`) of the
    closed-pair exponent on covers (`method` `na` or `ind`); `(value, α, ρ)`."""
    fn = closed_cover_exponent_na if method == "na" else closed_cover_exponent_ind
    lo = (1 - beta) / 2
    best = (-math.inf, lo, lo)
    for i in range(grid + 1):
        a = lo + (1 - 2 * lo) * i / grid
        for j in range(grid + 1 - i):
            r = lo + (1 - 2 * lo) * j / grid
            s = max(0.0, 1 - a - r)
            v = fn(a, r, s, mu, sizes)
            if v > best[0]:
                best = (v, a, r)
    from scipy.optimize import minimize

    def neg(x):
        a, r = x
        s = 1 - a - r
        if a < lo or r < lo or s < -1e-12:
            return 1e9
        return -fn(a, r, max(s, 0.0), mu, sizes)
    res = minimize(neg, [best[1], best[2]], method="Nelder-Mead",
                   options={"xatol": 1e-7, "fatol": 1e-10, "maxiter": 1000})
    if -res.fun > best[0]:
        best = (-float(res.fun), float(res.x[0]), float(res.x[1]))
    return best


def _root_beta_bisect(f, lo: float = 1e-6, hi: float = 1 - 1e-6, tol: float = 1e-7) -> float:
    """The root of an increasing `f` on `(0, 1)`; 0 if `f(lo) ≥ 0`, 1 if `f(hi) < 0`."""
    if f(lo) >= 0:
        return 0.0
    if f(hi) < 0:
        return 1.0
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if f(mid) >= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def _root_above(f, lo: float, step: float = 0.005, tol: float = 1e-6) -> float:
    """The first root of `f` above `lo`: scan upward in steps of `step` to the
    first `b` with `f(b) ≥ 0`, then bisect (for exponents that rise through
    zero once above `β*` and fall back to zero at `β → 1`); 1 if none."""
    b = lo
    while b + step < 1:
        nb = b + step
        if f(nb) >= 0:
            hi = nb
            while hi - b > tol:
                mid = (b + hi) / 2
                if f(mid) >= 0:
                    hi = mid
                else:
                    b = mid
            return (b + hi) / 2
        b = nb
    return 1.0


def beta_star_cover(mu: float, sizes) -> float:
    """`β*(d, μ)` by bisection on the pair exponent (agrees with
    `learning.first_moment.beta_star` to its scan step)."""
    return _root_beta_bisect(lambda b: cover_pair_exponent_beta(b, mu, sizes))


def beta_closed_cover(mu: float, sizes, method: str = "na") -> float:
    """`β_closed(d, μ)`: the root in `β` of the closed-pair exponent's supremum
    (the first root above `β*`; the exponent returns to zero at `β → 1`)."""
    bs = beta_star_cover(mu, sizes)
    if bs == 0.0:
        return 0.0
    return _root_above(lambda b: closed_cover_rate(b, mu, sizes, method)[0], bs)


# the flips: isolated customers and the weighted count ------------------------------

def isolated_binomial_moments(a: int, sizes) -> list:
    """`B_i = C(a, i) Π_j C(a − i, s_j) / C(a, s_j)` (exact `Fraction`s): the
    binomial moments of the number `I` of isolated customers of a random cover
    of `a` customers (patterns of size 1 ignored: they isolate nobody), so that
    `E[z^I] = Σ_i (z − 1)^i B_i`."""
    from fractions import Fraction
    hist = {sz: cnt for sz, cnt in _hist(sizes).items() if sz >= 2}
    out = []
    for i in range(a + 1):
        B = Fraction(comb(a, i))
        for sz, cnt in hist.items():
            B *= Fraction(comb(a - i, sz), comb(a, sz)) ** cnt
        out.append(B)
    return out


def isolated_pgf(a: int, sizes, z) -> float:
    """`E[z^I]` for the isolated-customer count of a random cover of `a` customers."""
    return float(sum(B * (z - 1) ** i for i, B in enumerate(isolated_binomial_moments(a, sizes))))


def isolated_pmf(a: int, sizes) -> list:
    """`P(I = i)`, `i = 0..a`, from the binomial moments by Möbius inversion
    (`P(I = i) = Σ_{u ≥ i} (−1)^{u − i} C(u, i) B_u`), exact."""
    B = isolated_binomial_moments(a, sizes)
    return [sum((-1) ** (u - i) * comb(u, i) * B[u] for u in range(i, a + 1)) for i in range(a + 1)]


def flip_joint_moments(n: int, a: int, r: int, sizes):
    """`B(u, u′) = C(a, u) C(r, u′) P(no pattern meets both A and R, and u given
    customers of A and u′ of R are isolated on their side)` for all `u ≤ a`,
    `u′ ≤ r` (exact `Fraction`s, an `(a + 1) × (r + 1)` list of lists).  A
    pattern of size `s` is allowed iff it lies in `S`, or in `A ∪ S` with at
    most one customer of `A` or none of the `u` isolated ones, or likewise in
    `R ∪ S`: `C(a − u + s, s_j) + u C(s, s_j − 1) + C(r − u′ + s, s_j) + u′ C(s, s_j − 1) − C(s, s_j)`."""
    from fractions import Fraction
    s = n - a - r
    hist = _hist(sizes)
    out = []
    for u in range(a + 1):
        row = []
        for up in range(r + 1):
            B = Fraction(comb(a, u) * comb(r, up))
            for sz, cnt in hist.items():
                allowed = comb(a - u + s, sz) + u * comb(s, sz - 1) + comb(r - up + s, sz) + up * comb(s, sz - 1) - comb(s, sz)
                B *= Fraction(allowed, comb(n, sz)) ** cnt
            row.append(B)
        out.append(row)
    return out


def flip_joint_pmf(n: int, a: int, r: int, sizes):
    """`P(I_A = i, I_R = i′, (A, R) empty)`, exact, by two-dimensional Möbius inversion."""
    B = flip_joint_moments(n, a, r, sizes)
    out = []
    for i in range(a + 1):
        row = []
        for ip in range(r + 1):
            v = 0
            for u in range(i, a + 1):
                cu = (-1) ** (u - i) * comb(u, i)
                for up in range(ip, r + 1):
                    v += cu * (-1) ** (up - ip) * comb(up, ip) * B[u][up]
            row.append(v)
        out.append(row)
    return out


def flip_log_bound(n: int, k: int, sizes) -> tuple[float, float]:
    """`(log E[Y], log E[X])` at the exact forced sizes: the weighted count
    `Y = Σ_P 1[P empty] / C(I_A + I_R, I_A)` (every swap of equally many isolated
    customers between the sides is another exact-size empty pair, so
    `Z(P) ≤ X` and `Y ≥ 1[X > 0]`) beside the pair count; exact, small `n`."""
    from fractions import Fraction
    from learning.first_moment import lchoose
    N, t = forced_sizes(n, k)
    r = N - t
    pmf = flip_joint_pmf(n, t, r, sizes)
    EY = sum(pmf[i][ip] / comb(i + ip, i) for i in range(t + 1) for ip in range(r + 1))
    EX = sum(pmf[i][ip] for i in range(t + 1) for ip in range(r + 1))
    lp = lchoose(n, t) + lchoose(n - t, r)
    return (lp + math.log(EY) if EY > 0 else -math.inf, lp + math.log(EX) if EX > 0 else -math.inf)


# the giant of the random intersection graph ----------------------------------------

def rig_branching_factor(mu: float, sizes) -> float:
    """`μ E_s[s (s − 1)]`: the mean number of customers two steps away in the
    two-type branching process (customer → patterns → customers)."""
    return mu * sum(p * sz * (sz - 1) for sz, p in _hist_fracs(sizes))


def rig_giant(mu: float, sizes, tol: float = 1e-12) -> float:
    """`θ(d, μ)`: the survival probability of the customer → patterns → customers
    branching process, i.e. the limiting fraction of customers in the giant
    component of the MOSP graph of a random cover with `m = μ n` patterns of
    the given sizes (Behrisch 2007; Lagerås & Lindholm 2008): the largest
    root of `1 − θ = exp(−μ E_s[s (1 − (1 − θ)^{s − 1})])`; 0 iff the
    branching factor `μ E[s(s − 1)] ≤ 1`.  Real sizes are accepted."""
    fr = _hist_fracs(sizes) if not isinstance(sizes, dict) or all(isinstance(k, int) for k in sizes) \
        else [(sz, c / sum(sizes.values())) for sz, c in sizes.items()]
    if mu * sum(p * sz * (sz - 1) for sz, p in fr) <= 1:
        return 0.0
    th = 1.0
    for _ in range(100000):
        nt = -math.expm1(-mu * sum(p * sz * (1 - (1 - th) ** (sz - 1)) for sz, p in fr))
        if abs(nt - th) < tol:
            return nt
        th = nt
    return th


def half_giant_line(mu: float, lo: float = 1.0, hi: float = 40.0, iterations: int = 60) -> float:
    """The real pattern size `d` at which `θ(d, μ) = ½` (fixed size `d`), by
    bisection; the half-giant line in the `(d, μ)` plane.  In excess:
    `e = μ (d − 1)`."""
    for _ in range(iterations):
        mid = (lo + hi) / 2
        if rig_giant(mu, {mid: 1}) >= 0.5:
            hi = mid
        else:
            lo = mid
    return hi


# the published upper line on covers ---------------------------------------------------

def cover_degree_law(mu: float, sizes, kmax: int = 400) -> np.ndarray:
    """The limiting degree law of a customer of the MOSP graph: the number of
    patterns of size `s` containing it is `Poisson(μ p_s s)`, each contributing
    `s − 1` neighbours (overlaps vanish as `n → ∞`): a compound Poisson,
    returned as `P(deg = d)` for `d = 0..kmax` (mass above `kmax` dropped)."""
    law = np.zeros(kmax + 1)
    law[0] = 1.0
    for sz, p in _hist_fracs(sizes):
        if sz < 2:
            continue
        lam = mu * p * sz
        step = sz - 1
        kk = np.arange(0, kmax // step + 1)
        pois = np.exp(-lam + kk * math.log(lam) - np.array([math.lgamma(k + 1) for k in kk])) if lam > 0 else np.eye(1, len(kk))[0]
        new = np.zeros_like(law)
        for k, pk in zip(kk, pois):
            if pk < 1e-300:
                continue
            new[k * step:] += pk * law[: kmax + 1 - k * step]
        law = new
    return law


def edwards_mcdermid_cover(mu: float, sizes, kmax: int = 400) -> float:
    """`Σ_{d ≥ 3} P(deg = d) g_{1/6}(d)` on the cover degree law: Edwards &
    McDermid (2015, Cor. 5.2) applied to the MOSP graph of a random cover, the
    published upper line `pw/n ≤ …` (owner's note of 2026-11-01)."""
    law = cover_degree_law(mu, sizes, kmax)
    g = edwards_mcdermid_g(kmax)
    return float(sum(law[d] * g[d] for d in range(3, kmax + 1)))


# the flips, asymptotically (negative association + Chernoff, valid) -----------------
#
# E[1[(A, R) empty] / C(I_A + I_R, I_A)] = Σ_{i, i′} P(I = (i, i′), empty) / C(i + i′, i)
# ≤ Σ_{cells} e^{−g(lower corner)} P(I_A ≤ x n, I_R ≤ y n, empty), g = ln C; and for
# θ_A, θ_R ≥ 0, P(I_A ≤ xn, I_R ≤ yn, empty) ≤ e^{θ_A xn + θ_R yn} E[e^{−θ_A I_A − θ_R I_R} 1[empty]].
# Given the types and the sizes |P_j ∩ A| (τ), the A-parts are independent uniform
# subsets of A, so the indicators D_v = 1[v lies in a pattern with ≥ 2 customers of
# A] (v ∈ A) and D′_v (v ∈ R) are negatively associated, and with I_A = Σ_v (1 − D_v):
#   E[e^{−θ_A I_A − θ_R I_R} | τ] ≤ e^{−θ_A a − θ_R r} (1 + c_A (1 − e^{−K_A}))^a (1 + c_R (1 − e^{−K_R}))^r,
# c = e^θ − 1, K_A = −Σ_{j: |P_j ∩ A| ≥ 2} ln(1 − |P_j ∩ A| / a).  The function
# a ln(1 + c (1 − e^{−K})) is concave increasing in K, so its tangent at K* makes the
# expectation over τ factorise over the patterns.  In the limit the per-pattern
# factor is M_s(η̂_A, η̂_R) = σ^s + Σ_i C(s, i) α^i σ^{s−i} e^{η̂_A i 1[i ≥ 2]} + (R likewise),
# η̂ = c e^{−K*} / (1 + c (1 − e^{−K*})).


def _log_flip_mgf(alpha: float, rho: float, sigma: float, etaA: float, etaR: float, sz: int) -> float:
    parts = [sz * math.log(sigma)] if sigma > 0 else []
    for x, eta in ((alpha, etaA), (rho, etaR)):
        if x <= 0:
            continue
        for i in range(1, sz + 1):
            v = math.log(comb(sz, i)) + i * math.log(x) + (sz - i) * math.log(sigma) if sigma > 0 or i == sz else -math.inf
            if sz - i > 0 and sigma <= 0:
                continue
            if i >= 2:
                v += eta * i
            parts.append(v)
    return _lse(parts)


def flip_cover_tail_exponent(x: float, y: float, alpha: float, rho: float, sigma: float, mu: float, sizes) -> float:
    """`Φ(x, y)`: the exponent per customer of the bound on
    `P(I_A ≤ x n, I_R ≤ y n, (A, R) empty)` (the Chernoff / negative-association
    bound above, minimised over `θ_A, θ_R ≥ 0` and the tangent points)."""
    fr = _hist_fracs(sizes)

    def f(z):
        thA, thR = math.exp(min(z[0], 6.0)), math.exp(min(z[1], 6.0))
        KA, KR = math.exp(min(max(z[2], -12.0), 5.0)), math.exp(min(max(z[3], -12.0), 5.0))
        out = thA * (x - alpha) + thR * (y - rho)
        etas = []
        for side, th, K in ((alpha, thA, KA), (rho, thR, KR)):
            c = math.expm1(th)
            u = -math.expm1(-K)
            out += side * math.log1p(c * u)
            eta = c * math.exp(-K) / (1 + c * u)
            out -= eta * side * K
            etas.append(eta)
        for sz, p in fr:
            out += mu * p * _log_flip_mgf(alpha, rho, sigma, etas[0], etas[1], sz)
        return out

    from scipy.optimize import minimize
    # the conditional mean of K on each side, the natural tangent point
    Ks = []
    for side in (alpha, rho):
        num = den = 0.0
        for sz, p in fr:
            q = (1 - alpha) ** sz + (1 - rho) ** sz - sigma ** sz
            num += mu * p * sum(comb(sz, i) * side ** i * sigma ** (sz - i) * i for i in range(2, sz + 1)) / q
        Ks.append(math.log(max(num / side, 1e-6)) if side > 0 else 0.0)
    best = math.inf
    for zA in (-30.0, -1.0, 2.5):
        for zR in (-30.0, -1.0, 2.5):
            z0 = [zA, zR, Ks[0], Ks[1]]
            best = min(best, f(z0))
            for method in ("Powell", "Nelder-Mead"):
                res = minimize(f, z0, method=method, options={"xtol": 1e-5, "ftol": 1e-10} if method == "Powell"
                               else {"xatol": 1e-5, "fatol": 1e-10, "maxiter": 2000})
                best = min(best, float(res.fun))
    # θ = 0 is always admissible and gives the pair exponent's pattern term
    best = min(best, sum(mu * p * math.log((1 - alpha) ** sz + (1 - rho) ** sz - sigma ** sz) for sz, p in fr))
    return best


def flip_cover_exponent_na(alpha: float, rho: float, sigma: float, mu: float, sizes, grid: int = 8):
    """The exponent per customer of the weighted count `Y = Σ_P 1[P empty] /
    C(I_A + I_R, I_A)` at exact sizes `(α, ρ, σ)`, as `(value, x*, y*)`:
    `H(α, ρ, σ) + sup_{x ≤ α, y ≤ ρ} [−(x + y) H₂(x / (x + y)) + Φ(x, y)]`.  Its
    difference from the pair exponent is minus the flip gain in nats per
    customer."""
    H = H3(alpha, rho, sigma)

    def obj(x, y):
        x, y = min(max(x, 0.0), alpha), min(max(y, 0.0), rho)
        g = (x + y) * H2(x / (x + y)) if x + y > 0 else 0.0
        return -g + flip_cover_tail_exponent(x, y, alpha, rho, sigma, mu, sizes)

    best = (-math.inf, 0.0, 0.0)
    xs = [0.0] + [alpha * 10 ** (-3 + 3 * i / grid) for i in range(grid + 1)]
    ys = [0.0] + [rho * 10 ** (-3 + 3 * i / grid) for i in range(grid + 1)]
    for x in xs:
        for y in ys:
            v = obj(x, y)
            if v > best[0]:
                best = (v, x, y)
    from scipy.optimize import minimize
    res = minimize(lambda z: -obj(z[0], z[1]), [best[1], best[2]], method="Nelder-Mead",
                   options={"xatol": 1e-6, "fatol": 1e-10, "maxiter": 400})
    if -res.fun > best[0]:
        best = (-float(res.fun), float(min(max(res.x[0], 0.0), alpha)), float(min(max(res.x[1], 0.0), rho)))
    return H + best[0], best[1], best[2]


def flip_cover_exponent_beta(beta: float, mu: float, sizes) -> float:
    a = (1 - beta) / 2
    return flip_cover_exponent_na(a, a, beta, mu, sizes)[0]


def beta_flip_cover(mu: float, sizes) -> float:
    """`β_flip(d, μ)`: the root in `β` of the weighted count's exponent (the
    first above `β*`)."""
    bs = beta_star_cover(mu, sizes)
    if bs == 0.0:
        return 0.0
    return _root_above(lambda b: flip_cover_exponent_beta(b, mu, sizes), bs, tol=1e-5)


def flip_log_bound_fast(n: int, k: int, sizes) -> tuple[float, float]:
    """`flip_log_bound` with the Möbius inversion in integers over a common
    denominator and separated into its two one-dimensional sums (`n = 125`
    in seconds)."""
    from fractions import Fraction
    from learning.first_moment import lchoose
    N, t = forced_sizes(n, k)
    a, r = t, N - t
    s = n - a - r
    hist = _hist(sizes)
    Bn = [[0] * (r + 1) for _ in range(a + 1)]
    for u in range(a + 1):
        for up in range(r + 1):
            v = comb(a, u) * comb(r, up)
            for sz, cnt in hist.items():
                allowed = comb(a - u + s, sz) + u * comb(s, sz - 1) + comb(r - up + s, sz) + up * comb(s, sz - 1) - comb(s, sz)
                v *= allowed ** cnt
            Bn[u][up] = v
    # inner inversion over u′ for every (u, i′), then over u for every (i, i′)
    inner = [[0] * (r + 1) for _ in range(a + 1)]
    for u in range(a + 1):
        row = Bn[u]
        for ip in range(r + 1):
            acc = 0
            for up in range(ip, r + 1):
                term = comb(up, ip) * row[up]
                acc += -term if (up - ip) & 1 else term
            inner[u][ip] = acc
    Pn = [[0] * (r + 1) for _ in range(a + 1)]
    for ip in range(r + 1):
        for i in range(a + 1):
            acc = 0
            for u in range(i, a + 1):
                term = comb(u, i) * inner[u][ip]
                acc += -term if (u - i) & 1 else term
            Pn[i][ip] = acc
    logD = sum(cnt * math.log(comb(n, sz)) for sz, cnt in hist.items())
    EY = Fraction(0)
    EX = 0
    for i in range(a + 1):
        for ip in range(r + 1):
            if Pn[i][ip] < 0:
                raise ArithmeticError("negative probability numerator")
            EY += Fraction(Pn[i][ip], comb(i + ip, i))
            EX += Pn[i][ip]
    lp = lchoose(n, t) + lchoose(n - t, r)
    lY = lp + (math.log(EY.numerator) - math.log(EY.denominator) - logD) if EY > 0 else -math.inf
    lX = lp + (math.log(EX) - logD) if EX > 0 else -math.inf
    return lY, lX


# --- item 08: the theorems on paper, in exact rationals ------------------------------
#
# Theorem S:  P(pw(G(n, p)) ≤ k) ≤ C(n, k) · P_N(E_bip),  P_N(E_bip) the weighted count
#             of the graphs on N = n − k labelled vertices whose components can be
#             grouped into sides of sizes t = ⌈N/2⌉ and N − t   (`prob_bip_exact`, by
#             the partition formula, Lemma P; `weighted_graph_count` enumerates it);
# Cor. S′:    the same with E_relax (no component larger than t), computed by the
#             first-vertex-component recursion (Lemma F, `prob_relax_exact`) on
#             Gilbert's connectedness recursion (Lemma G, `connected_probs_exact`);
# Theorem Cl: P(pw ≤ k) ≤ Σ_{a ≥ t, r ≥ N − t, a + r + s = n} n!/(a! r! s!) (1 − p)^{ar}
#             (1 − (1 − p)^a)^s (1 − (1 − p)^r)^s = E[X₃]            (`closed_count_exact`);
# Lemma W:    Y = Σ_P 1[P empty] / Z(P) ≥ 1[X > 0] for any 1 ≤ Z ≤ X on {P empty}
#             (`weighted_count`), first instance Z = C(I_A + I_R, I_A), the flips
#             (`flip_swaps`, `flip_count`: every swap of equally many vertices isolated
#             on their sides is another exact-size empty pair).
# Every formula here is checked against the enumeration of all labelled graphs at
# n ≤ 7 by reports/scratch/separator_moment/08_theorems/check.py (exact rationals at
# p = 1/2 and 1/3).


def connected_probs_exact(N: int, p) -> list:
    """`C_j(p)`, `j = 0..N`, exactly (`Fraction` when `p` is one): Gilbert's recursion
    `C_1 = 1`, `C_j = 1 − Σ_{i=1}^{j−1} C(j−1, i−1) C_i (1−p)^{i(j−i)}` (Lemma G: the
    component of vertex 1 has `i` vertices, is connected, and sends no edge to the
    other `j − i`). `C_0 = 1` by convention."""
    from fractions import Fraction
    p = Fraction(p)
    q = 1 - p
    C = [Fraction(1), Fraction(1)]
    for j in range(2, N + 1):
        C.append(1 - sum(comb(j - 1, i - 1) * C[i] * q ** (i * (j - i)) for i in range(1, j)))
    return C[:N + 1]


def prob_relax_exact(N: int, p, M: int, C: list | None = None):
    """`P(no component of G(N, p) has more than M vertices)`, exactly, by the
    first-vertex-component recursion (Lemma F): `R_0 = 1`,
    `R_j = Σ_{i=1}^{min(M, j)} C(j−1, i−1) C_i (1−p)^{i(j−i)} R_{j−i}`."""
    from fractions import Fraction
    p = Fraction(p)
    q = 1 - p
    if C is None:
        C = connected_probs_exact(N, p)
    R = [Fraction(1)]
    for j in range(1, N + 1):
        R.append(sum(comb(j - 1, i - 1) * C[i] * q ** (i * (j - i)) * R[j - i]
                     for i in range(1, min(M, j) + 1)))
    return R[N]


def prob_bip_exact(N: int, p, t: int | None = None, C: list | None = None):
    """`P_N(E_bip)`, exactly: `Σ_λ N!/(Π λ_i! Π_s m_s!) Π C_{λ_i} (1−p)^{(N² − Σ λ_i²)/2}`
    over the partitions `λ ⊢ N` with a sub-multiset summing to `t` (Lemma P; the
    multinomial counts the vertex assignments to the parts, each part is
    connected independently, and `(N² − Σ λ_i²)/2` pairs cross between parts)."""
    from fractions import Fraction
    p = Fraction(p)
    q = 1 - p
    if t is None:
        t = (N + 1) // 2
    if N == 0:
        return Fraction(1)
    if C is None:
        C = connected_probs_exact(N, p)
    total = Fraction(0)
    for lam in partitions(N):
        if not _subset_sum(list(lam), t):
            continue
        hist = _hist(lam)
        w = Fraction(math.factorial(N))
        for s, m in hist.items():
            w /= Fraction(math.factorial(s)) ** m * math.factorial(m)
        for s in lam:
            w *= C[s]
        w *= q ** ((N * N - sum(s * s for s in lam)) // 2)
        total += w
    return total


def pair_count_exact(n: int, k: int, p):
    """`E[X₁] = C(n, t) C(n − t, N − t) (1 − p)^{t(N − t)}`, exactly (the count on
    record at exact sizes)."""
    from fractions import Fraction
    N, t = forced_sizes(n, k)
    return comb(n, t) * comb(n - t, N - t) * (1 - Fraction(p)) ** (t * (N - t))


def closed_count_exact(n: int, k: int, p):
    """`E[X₃]` on `G(n, p)`, exactly: Theorem Cl's right-hand side
    `Σ_{a ≥ t, r ≥ N − t, a + r + s = n} n!/(a! r! s!) (1 − p)^{ar} (1 − (1 − p)^a)^s (1 − (1 − p)^r)^s`."""
    from fractions import Fraction
    N, t = forced_sizes(n, k)
    q = 1 - Fraction(p)
    total = Fraction(0)
    for a in range(t, n + 1):
        for r in range(N - t, n - a + 1):
            s = n - a - r
            w = Fraction(math.factorial(n), math.factorial(a) * math.factorial(r) * math.factorial(s))
            w *= q ** (a * r) * (1 - q ** a) ** s * (1 - q ** r) ** s
            total += w
    return total


def weighted_graph_count(N: int, p, event) -> "Fraction":
    """`Σ_{H on N labelled vertices, event(adj)} p^{|E(H)|} (1 − p)^{C(N,2) − |E(H)|}`,
    exactly, by enumeration (`N ≤ 7`); `event` takes the adjacency masks."""
    from fractions import Fraction
    p = Fraction(p)
    q = 1 - p
    Cn = N * (N - 1) // 2
    counts = [0] * (Cn + 1)
    for adj, e in _labelled_graphs(N):
        if event(adj):
            counts[e] += 1
    return sum(c * p ** e * q ** (Cn - e) for e, c in enumerate(counts) if c)


def isolated_in(adj: list[int], A: int) -> int:
    """The vertices of `A` with no neighbour in `A` (isolated in `G[A]`), as a mask."""
    out = 0
    T = A
    while T:
        low = T & -T
        T ^= low
        if adj[low.bit_length() - 1] & A == 0:
            out |= low
    return out


def flip_swaps(adj: list[int], A: int, R: int) -> list[tuple[int, int]]:
    """Every pair `((A ∖ J) ∪ J′, (R ∖ J′) ∪ J)` with `J ⊆ I_A`, `J′ ⊆ I_R`, `|J| = |J′|`
    (`I_A` the vertices of `A` isolated in `G[A]`), the identity swap included: the
    flip lemma says each is an empty pair of the same sizes when `(A, R)` is, and
    the map is injective, so their number `C(I_A + I_R, I_A)` is a valid `Z`."""
    IA, IR = isolated_in(adj, A), isolated_in(adj, R)
    ia = [v for v in range(len(adj)) if IA >> v & 1]
    ir = [v for v in range(len(adj)) if IR >> v & 1]
    out = []
    for j in range(min(len(ia), len(ir)) + 1):
        for J in combinations(ia, j):
            Jm = sum(1 << v for v in J)
            for Jp in combinations(ir, j):
                Jpm = sum(1 << v for v in Jp)
                out.append(((A & ~Jm) | Jpm, (R & ~Jpm) | Jm))
    return out


def flip_count(adj: list[int], A: int, R: int) -> tuple[int, int, int]:
    """`(|I_A|, |I_R|, C(|I_A| + |I_R|, |I_A|))`: the flip count `Z` of the pair."""
    ia, ir = popcount(isolated_in(adj, A)), popcount(isolated_in(adj, R))
    return ia, ir, comb(ia + ir, ia)


def weighted_count(pairs, Z) -> "Fraction":
    """`Y = Σ_P 1 / Z(P)` over a list of (empty) pairs, exactly; `Z(P) ≥ 1`."""
    from fractions import Fraction
    total = Fraction(0)
    for P in pairs:
        z = Z(P)
        if z < 1:
            raise ValueError("Z must be at least 1")
        total += Fraction(1, z)
    return total


# --- item 09: the weighted count's lower tail --------------------------------------
#
# Lemma W (§8.1) admits any `Z(P)` with `1 ≤ Z(P) ≤ X` on `{P empty}`, and the
# weighted count `Y = Σ_P 1[P empty]/Z(P)` gives `P(pw ≤ k) ≤ E[X] · E[1/Z | P₀ empty]`.
# `Z` here counts *recombinations* of `P₀ = (A, R, S)` — the mechanism of §4.5:
# separator vertices join a side, their few neighbours on the other side are
# evicted into the new separator, and vertices of the other side are drawn into
# the separator to keep the sizes.  Two lobes (§4.4).  With `W_A, W_R ⊆ S`
# disjoint and no `W_A–W_R` edge, `U_A ⊆ A`, `U_R ⊆ R`:
#
#   same lobe:      A′ = (A ∖ U_A) ∪ W_A,  R′ = (R ∖ U_R) ∪ W_R,
#                   |U_A| = |W_A|, |U_R| = |W_R|, N_R(W_A) ⊆ U_R, N_A(W_R) ⊆ U_A;
#   reversed lobe:  A′ = (R ∖ U_R) ∪ W_A,  R′ = (A ∖ U_A) ∪ W_R,
#                   |W_A| = |U_R| + (t − r), |W_R| = |U_A| − (t − r), N_A(W_A) ⊆ U_A, N_R(W_R) ⊆ U_R.
#
# Each image is an exact-size empty pair of the planted graph (every `A′–R′`
# edge class is excluded by one of the four conditions), the map
# `(W_A, W_R, U_A, U_R) ↦ (A′, R′)` is injective on each lobe (`U_A = A ∖ A′`,
# `W_A = A′ ∩ S`, … on the same lobe; `U_R = R ∖ A′`, … on the reversed), the
# lobes are disjoint (`A′ ∩ A ≠ ∅` on one, `= ∅` on the other, for `|U_A| < t`)
# and only the identity (same lobe, `W = ∅`) is `P₀` itself.  So
# `Z_j := 1 + #(recombinations with |U_A|, |U_R| ≤ j)` satisfies `1 ≤ Z_j ≤ X`.
# Brute-force checked on every labelled graph to six vertices and on the
# planted instances (`tests/test_separator_moment.py`, `09_lower_tail/run.py`).
#
# The *computable* bound `Ẑ₀` keeps the same-lobe moves with one side's `W`
# empty: `W_A ⊆ L_R := {w ∈ S : N_R(w) = ∅}` with `U_A` any `|W_A|`-subset of
# `A`, which gives `Σ_i C(|L_R|, i) C(t, i) = C(|L_R| + t, t)` pairs (the identity
# included), and symmetrically; `Ẑ₀ = C(|L_R| + t, t) + C(|L_A| + r, r) − 1`.
# Given `(A, R)`, `|L_A|` and `|L_R|` are independent `Bin(k, (1−p)^t)`,
# `Bin(k, (1−p)^r)` (disjoint edge sets), so `E[1/Ẑ₀ | P₀ empty]` is a finite
# double sum of binomial probabilities (`z_hat_log_laplace`).


def _or_masks(masks) -> int:
    out = 0
    for m in masks:
        out |= m
    return out


def _subsets_with_small_nbhd(adj: list[int], verts: list[int], side: int, limit: int,
                             max_size: int) -> list[tuple[int, int, int]]:
    """Every `W ⊆ verts` with `|W| ≤ max_size` and `|N_side(W)| ≤ limit`, as
    `(mask, |W|, |N_side(W)|)`; the family is closed under subsets, so the
    depth-first search prunes exactly."""
    out: list[tuple[int, int, int]] = []

    def dfs(start: int, chosen: int, size: int, nb: int) -> None:
        out.append((chosen, size, popcount(nb)))
        if size == max_size:
            return
        for i in range(start, len(verts)):
            v = verts[i]
            nb2 = nb | (adj[v] & side)
            if popcount(nb2) <= limit:
                dfs(i + 1, chosen | (1 << v), size + 1, nb2)

    dfs(0, 0, 0, 0)
    return out


def recombinations(adj: list[int], A: int, R: int, jmax: int = 4,
                   lobes: tuple[str, ...] = ("same", "rev")) -> dict[tuple[str, int, int], int]:
    """The number of recombinations of the pair `(A, R)` per `(lobe, |U_A|, |U_R|)`
    with `|U_A|, |U_R| ≤ jmax` (the identity excluded), by enumerating the
    separator subsets `W_A`, `W_R` and counting the admissible `(U_A, U_R)` in
    closed form: `C(t − |N_A(W_R)|, |U_A| − |N_A(W_R)|) · C(r − |N_R(W_A)|, |U_R| − |N_R(W_A)|)`
    on the same lobe, and with `N_A(W_A)`, `N_R(W_R)` on the reversed one.
    `recombination_pairs` lists the same pairs explicitly."""
    n = len(adj)
    full = (1 << n) - 1
    S = full & ~(A | R)
    t, r = popcount(A), popcount(R)
    if jmax >= min(t, r):
        raise ValueError("jmax must be below both side sizes (so that no image is P itself)")
    sv = [v for v in range(n) if S >> v & 1]
    d = t - r
    out: dict[tuple[str, int, int], int] = {}

    def add(key, val):
        if val:
            out[key] = out.get(key, 0) + val

    if "same" in lobes:
        # W_A: |W_A| = |U_A| ≤ jmax and |N_R(W_A)| ≤ |U_R| ≤ jmax; W_R symmetric
        WA = _subsets_with_small_nbhd(adj, sv, R, jmax, jmax)
        WR = _subsets_with_small_nbhd(adj, sv, A, jmax, jmax)
        for wa, ia, nR in WA:
            forb = wa | (_or_masks(adj[v] for v in sv if wa >> v & 1) & S)  # W_R must avoid W_A and N_S(W_A)
            for wr, ir, nA in WR:
                if wr & forb or (ia == 0 and ir == 0):
                    continue
                if nA > ia or nR > ir:
                    continue
                add(("same", ia, ir), comb(t - nA, ia - nA) * comb(r - nR, ir - nR))
    if "rev" in lobes:
        # |U_R| = |W_A| − d ≤ jmax, |U_A| = |W_R| + d ≤ jmax; N_A(W_A) ⊆ U_A, N_R(W_R) ⊆ U_R
        WA = _subsets_with_small_nbhd(adj, sv, A, jmax, jmax + d)
        WR = _subsets_with_small_nbhd(adj, sv, R, jmax, max(0, jmax - d))
        for wa, ia, nA in WA:
            jR = ia - d
            if jR < 0 or jR > jmax:
                continue
            forb = wa | (_or_masks(adj[v] for v in sv if wa >> v & 1) & S)
            for wr, ir, nR in WR:
                jA = ir + d
                if wr & forb or jA > jmax or nA > jA or nR > jR:
                    continue
                add(("rev", jA, jR), comb(t - nA, jA - nA) * comb(r - nR, jR - nR))
    return out


def recombination_pairs(adj: list[int], A: int, R: int, jmax: int = 4,
                        lobes: tuple[str, ...] = ("same", "rev")) -> list[tuple[int, int]]:
    """Every recombined pair `(A′, R′)` explicitly (the identity excluded), for
    the lemma check: the list has `Σ recombinations(...)` entries, all distinct,
    all exact-size empty pairs when `(A, R)` is."""
    n = len(adj)
    full = (1 << n) - 1
    S = full & ~(A | R)
    t, r = popcount(A), popcount(R)
    if jmax >= min(t, r):
        raise ValueError("jmax must be below both side sizes")
    sv = [v for v in range(n) if S >> v & 1]
    av = [v for v in range(n) if A >> v & 1]
    rv = [v for v in range(n) if R >> v & 1]
    d = t - r
    out: list[tuple[int, int]] = []

    def supersets(base: int, verts: list[int], size: int) -> Iterator[int]:
        rest = [v for v in verts if not base >> v & 1]
        need = size - popcount(base)
        if need < 0:
            return
        for extra in combinations(rest, need):
            yield base | sum(1 << v for v in extra)

    nbS = {v: adj[v] & S for v in sv}
    for lobe in lobes:
        if lobe == "same":
            WA = _subsets_with_small_nbhd(adj, sv, R, jmax, jmax)
            WR = _subsets_with_small_nbhd(adj, sv, A, jmax, jmax)
        else:
            WA = _subsets_with_small_nbhd(adj, sv, A, jmax, jmax + d)
            WR = _subsets_with_small_nbhd(adj, sv, R, jmax, max(0, jmax - d))
        for wa, ia, na in WA:
            forb = wa | _or_masks(nbS[v] for v in sv if wa >> v & 1)
            for wr, ir, nr in WR:
                if wr & forb:
                    continue
                if lobe == "same":
                    if ia == 0 and ir == 0:
                        continue
                    jA, jR = ia, ir
                    baseA = _or_masks(adj[v] & A for v in sv if wr >> v & 1)   # N_A(W_R) ⊆ U_A
                    baseR = _or_masks(adj[v] & R for v in sv if wa >> v & 1)   # N_R(W_A) ⊆ U_R
                else:
                    jA, jR = ir + d, ia - d
                    if jR < 0:
                        continue
                    baseA = _or_masks(adj[v] & A for v in sv if wa >> v & 1)   # N_A(W_A) ⊆ U_A
                    baseR = _or_masks(adj[v] & R for v in sv if wr >> v & 1)   # N_R(W_R) ⊆ U_R
                if jA > jmax or jR > jmax or popcount(baseA) > jA or popcount(baseR) > jR:
                    continue
                for UA in supersets(baseA, av, jA):
                    for UR in supersets(baseR, rv, jR):
                        if lobe == "same":
                            out.append(((A & ~UA) | wa, (R & ~UR) | wr))
                        else:
                            out.append(((R & ~UR) | wa, (A & ~UA) | wr))
    return out


def z_recomb(adj: list[int], A: int, R: int, jmax: int = 4,
             lobes: tuple[str, ...] = ("same", "rev")) -> int:
    """`Z_j(P) = 1 + #recombinations` with `|U_A|, |U_R| ≤ jmax`: admissible in Lemma W."""
    return 1 + sum(recombinations(adj, A, R, jmax, lobes).values())


def side_avoiders(adj: list[int], A: int, R: int) -> tuple[int, int]:
    """`(|L_A|, |L_R|)`: the separator vertices with no neighbour in `A`, in `R`."""
    n = len(adj)
    S = ((1 << n) - 1) & ~(A | R)
    la = lr = 0
    T = S
    while T:
        low = T & -T
        T ^= low
        nb = adj[low.bit_length() - 1]
        la += (nb & A) == 0
        lr += (nb & R) == 0
    return la, lr


def z_hat0(adj: list[int], A: int, R: int) -> int:
    """`Ẑ₀ = C(|L_R| + t, t) + C(|L_A| + r, r) − 1`: the computable lower bound on
    the recombination count (same lobe, one side's `W` empty)."""
    la, lr = side_avoiders(adj, A, R)
    t, r = popcount(A), popcount(R)
    return comb(lr + t, t) + comb(la + r, r) - 1


def _log_binom_pmf(k: int, pi: float) -> list[float]:
    if pi <= 0.0:
        return [0.0] + [-math.inf] * k
    if pi >= 1.0:
        return [-math.inf] * k + [0.0]
    lp, lq = math.log(pi), math.log1p(-pi)
    return [lchoose(k, i) + i * lp + (k - i) * lq for i in range(k + 1)]


def z_hat_log_laplace(n: int, k: int, p: float) -> float:
    """`log E[1/Ẑ₀ | P₀ empty]` on `G(n, p)` at width `k`, exactly: the double sum
    over `|L_A| ~ Bin(k, (1−p)^t)`, `|L_R| ~ Bin(k, (1−p)^r)` (independent) of the
    binomial probabilities over `C(|L_R| + t, t) + C(|L_A| + r, r) − 1`."""
    N, t = forced_sizes(n, k)
    r = N - t
    piA = (1 - p) ** t
    piR = (1 - p) ** r
    lA = _log_binom_pmf(k, piA)
    lR = _log_binom_pmf(k, piR)
    terms = []
    for la in range(k + 1):
        if lA[la] == -math.inf:
            continue
        for lr in range(k + 1):
            if lR[lr] == -math.inf:
                continue
            z = comb(lr + t, t) + comb(la + r, r) - 1
            terms.append(lA[la] + lR[lr] - math.log(z))
    return _lse(terms)


def log_pair_count(n: int, k: int, p: float) -> float:
    """`log E[X]` at exact sizes: `C(n, t) C(n − t, r) (1 − p)^{t r}`."""
    N, t = forced_sizes(n, k)
    r = N - t
    return lchoose(n, t) + lchoose(n - t, r) + t * r * math.log1p(-p)


def log_weighted_bound(n: int, k: int, p: float) -> float:
    """`log E[Y]` for `Z = Ẑ₀`: `log E[X] + log E[1/Ẑ₀ | P₀ empty]` (Lemma W)."""
    return log_pair_count(n, k, p) + z_hat_log_laplace(n, k, p)


def _kl(x: float, pi: float) -> float:
    if x <= 0.0:
        return -math.log1p(-pi)
    if x >= 1.0:
        return -math.log(pi)
    return x * math.log(x / pi) + (1 - x) * math.log((1 - x) / (1 - pi))


def z_hat_exponent(c: float, beta: float, grid: int = 400) -> tuple[float, float, float]:
    """The exponent per vertex of `E[1/Ẑ₀ | P₀ empty]` on `G(n, c/n)` at `β`
    (a non-positive number): `−inf_{λ_A, λ_R ∈ [0, β]} [β KL(λ_A/β ‖ π) + β KL(λ_R/β ‖ π)
    + max((λ_R + a) H(λ_R/(λ_R + a)), (λ_A + a) H(λ_A/(λ_A + a)))]` with `a = (1 − β)/2`,
    `π = e^{−c a}` (the two sides have the same fraction in the limit); returns
    `(exponent, λ_A, λ_R)` at the minimiser.  At `λ = 0` the value is
    `2β ln q(a)`, the closed count's gain (§6.1 (b))."""
    a = (1 - beta) / 2
    pi = math.exp(-c * a)

    def gain(lam: float) -> float:
        if lam <= 0.0:
            return 0.0
        return (lam + a) * H2(lam / (lam + a))

    def f(lamA: float, lamR: float) -> float:
        return beta * (_kl(lamA / beta, pi) + _kl(lamR / beta, pi)) + max(gain(lamR), gain(lamA))

    best = (math.inf, 0.0, 0.0)
    for i in range(grid + 1):
        lamA = beta * i / grid
        for j in range(grid + 1):
            lamR = beta * j / grid
            v = f(lamA, lamR)
            if v < best[0]:
                best = (v, lamA, lamR)
    try:
        from scipy.optimize import minimize
        res = minimize(lambda x: f(min(max(x[0], 0.0), beta), min(max(x[1], 0.0), beta)),
                       [best[1], best[2]], method="Nelder-Mead", options={"xatol": 1e-10, "fatol": 1e-13})
        if res.fun < best[0]:
            best = (float(res.fun), float(min(max(res.x[0], 0.0), beta)), float(min(max(res.x[1], 0.0), beta)))
    except ImportError:  # pragma: no cover
        pass
    return -best[0], best[1], best[2]


def weighted_exponent(c: float, beta: float) -> float:
    """The weighted count's exponent per vertex with `Z = Ẑ₀`: the pair exponent
    plus `z_hat_exponent`."""
    return pair_exponent_beta(c, beta) + z_hat_exponent(c, beta, grid=120)[0]


def beta_weighted(c: float) -> float:
    """`β_W(c)`: the root in `β` of `weighted_exponent(c, ·)`."""
    return _root_beta(lambda b: weighted_exponent(c, b), tol=1e-6)
