"""Reductions into pathwidth / vertex separation with their vertex blow-up
(loop0014 item 03, `reports/subexp_pathwidth.md` §3).

Every reduction the catalogue calls *linear in the vertices* is implemented
here and checked against brute-force vertex separation on every graph of the
networkx atlas (all graphs to 7 vertices), plus the quadratic one of Lengauer
(1981) for the record. The checks write their log under
`reports/scratch/subexp_pathwidth/03_reductions/`.

    python -m learning.subexp_reductions            # the full check, atlas to 7
    python -m learning.subexp_reductions --nmax 5   # quick

Graphs are `(n, adj)` as in `paper1/complex_check.py`: vertices `0..n-1`,
`adj[v]` the neighbour bitmask. Vertex separation `vs` is Kinnersley's
(`vs = pw`): the minimum over layouts of the largest number of placed
vertices with an unplaced neighbour. Two exact evaluators are used: the
literal minimum over `itertools.permutations` (`vertex_separation`, to 7
vertices) and a prefix-set DP (`vs_subset_dp`, to about 20 vertices), the
latter checked against the former on every atlas graph before anything else
is checked. MOSP values are computed by a DP over *pattern* subsets
(`mosp_subset_dp`), which shares nothing with the vertex-separation code.

The reductions (`G` has `n` vertices, `m` edges, maximum degree `Δ`):

- `cobipartite_double(G)`: `H` on `2n` vertices, two cliques `A = B = V(G)`,
  `a_u ~ b_v` iff `u = v` or `uv ∈ E`. **`vs(H) = vs(G) + n`** (proved in §3.4;
  checked here). Pathwidth on all graphs reduces to pathwidth on cobipartite
  graphs (where it equals treewidth) at blow-up 2.
- `clique_blowup(G, c)`: the lexicographic product `G[K_c]`, `cn` vertices.
  **`vs(G[K_c]) + 1 = c (vs(G) + 1)`** (proved in §3.4; checked). The
  pathwidth analogue of the treewidth amplification of Bodlaender, Gilbert,
  Hafsteinsson & Kloks (Bodlaender 2024 survey, Theorem 7).
- `degree_clique_expansion(G)`: every vertex becomes a clique on its incident
  edge ports and every edge a matching edge between ports; `2m` vertices plus
  the isolated ones. **`cw(G) ≤ vs(G°)` for every `G`, with equality when
  `Δ ≤ 3`** (proved in §3.4; checked). Cutwidth on subcubic graphs reduces to
  vertex separation on subcubic graphs at blow-up ≤ 3, preserving planarity.
- `mosp_instance(G)`: one pattern per edge and one private pattern per
  isolated vertex, `n` customers; `mosp = vs + 1` (the Lean theorem
  `MOSPGraph.lean`; checked here by the pattern DP). `row_graph` is the
  converse.
- `lengauer_cliques(G)`: Lengauer (1981) Theorem 7, every vertex an
  `(N+1)`-clique, `N(N+1)` vertices, `vs(G') = mcw(G) + N`; **quadratic**,
  implemented for the record only.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

from paper1.complex_check import (cutwidth_dp, edges_of, from_nx, graph, modified_cutwidth_dp,
                                  row_graph, vertex_separation)

OUT = Path("reports/scratch/subexp_pathwidth/03_reductions")
INF = 10 ** 9


# ----------------------------------------------------------------------------
# exact evaluators
# ----------------------------------------------------------------------------


def vs_subset_dp(adj) -> int:
    """Vertex separation by DP over prefix sets, vectorised by popcount layer:
    `f(S) = max(cost(S), min_{v ∈ S} f(S ∖ v))`, `cost(S)` the vertices of `S`
    with a neighbour outside `S`. Exact; about 20 vertices in seconds."""
    n = len(adj)
    if n <= 1:
        return 0
    N = 1 << n
    states = np.arange(N, dtype=np.int64)
    cost = np.zeros(N, dtype=np.int32)
    pc = np.zeros(N, dtype=np.int32)
    for u in range(n):
        inside = (states >> u) & 1
        pc += inside.astype(np.int32)
        has_out = (np.int64(adj[u]) & ~states) != 0
        cost += (inside & has_out).astype(np.int32)
    cost[N - 1] = 0
    f = np.full(N, INF, dtype=np.int32)
    f[0] = 0
    for k in range(1, n + 1):
        S = states[pc == k]
        best = np.full(len(S), INF, dtype=np.int32)
        for v in range(n):
            has = ((S >> v) & 1).astype(bool)
            best = np.where(has, np.minimum(best, f[S ^ (1 << v)]), best)
        f[S] = np.maximum(best, cost[S])
    return int(f[N - 1])


def vs(g) -> int:
    return vs_subset_dp(g[1])


def mosp_subset_dp(matrix) -> int:
    """MOSP value by DP over the set of produced patterns: the stacks open
    after producing `S` are the customers with a pattern in `S` and one
    outside; the value of an order is the max over its prefixes. Nothing
    here mentions a graph or a layout."""
    rows = [sum(1 << j for j, x in enumerate(r) if x) for r in matrix]
    m = len(matrix[0]) if matrix else 0
    if m == 0:
        return 0
    N = 1 << m
    full = N - 1
    states = np.arange(N, dtype=np.int64)
    open_ = np.zeros(N, dtype=np.int32)
    for r in rows:
        if r:
            open_ += (((states & r) != 0) & ((states & r) != r)).astype(np.int32)
    # count a customer whose patterns are all in S *at the step it closes*:
    # the stack is open at the step that produces its last pattern, so the
    # per-step count is open_(S) + closings(S) where closings(S) = customers
    # whose last pattern is the one just added; handle by the transition.
    pc = np.zeros(N, dtype=np.int32)
    for j in range(m):
        pc += ((states >> j) & 1).astype(np.int32)
    f = np.full(N, INF, dtype=np.int32)
    f[0] = 0
    # cost of arriving at S by adding pattern p: stacks open during step =
    # customers with a pattern in S (including p) and either a pattern
    # outside S, or p as their last pattern (= closed exactly now). Equivalently
    # customers whose pattern set meets S and meets (complement of S) ∪ {p}.
    for k in range(1, m + 1):
        S = states[pc == k]
        best = np.full(len(S), INF, dtype=np.int32)
        for p in range(m):
            has = ((S >> p) & 1).astype(bool)
            prev = f[S ^ (1 << p)]
            step = np.zeros(len(S), dtype=np.int32)
            outside_or_p = (~S & full) | (1 << p)
            for r in rows:
                if r:
                    step += (((S & r) != 0) & ((outside_or_p & r) != 0)).astype(np.int32)
            cand = np.maximum(prev, step)
            best = np.where(has, np.minimum(best, cand), best)
        f[S] = best
    return int(f[full])


def mosp_permutations(matrix) -> int:
    """The literal definition (L&Y 2002 eqs. (1)-(2)) for the tests of the DP."""
    from paper1.complex_check import mosp_value
    return mosp_value(matrix)


def treewidth(g) -> int:
    from learning.treewidth import treewidth_exact
    return treewidth_exact(list(g[1]))[0]


# ----------------------------------------------------------------------------
# the reductions
# ----------------------------------------------------------------------------


def max_degree(g) -> int:
    return max((bin(a).count("1") for a in g[1]), default=0)


def is_cobipartite(g) -> bool:
    """Some bipartition into two cliques (complement bipartite)."""
    n, adj = g
    comp = [((1 << n) - 1) & ~adj[v] & ~(1 << v) for v in range(n)]
    colour = [-1] * n
    for s in range(n):
        if colour[s] >= 0:
            continue
        colour[s] = 0
        stack = [s]
        while stack:
            v = stack.pop()
            bits = comp[v]
            while bits:
                u = (bits & -bits).bit_length() - 1
                bits &= bits - 1
                if colour[u] < 0:
                    colour[u] = 1 - colour[v]
                    stack.append(u)
                elif colour[u] == colour[v]:
                    return False
    return True


def cobipartite_double(g):
    """`H`: cliques `A = {a_v}`, `B = {b_v}`; `a_u ~ b_v` iff `u = v` or `uv ∈ E`."""
    n, adj = g
    es = []
    for u in range(n):
        for v in range(u + 1, n):
            es.append((u, v))
            es.append((n + u, n + v))
        es.append((u, n + u))
        for v in range(n):
            if adj[u] >> v & 1:
                es.append((u, n + v))
    return graph(2 * n, es)


def clique_blowup(g, c: int):
    """The lexicographic product `G[K_c]`: vertex `v` becomes a clique
    `{cv, …, cv + c − 1}`, every edge a complete join between cliques."""
    n, adj = g
    es = []
    for u in range(n):
        for i in range(c):
            for j in range(i + 1, c):
                es.append((c * u + i, c * u + j))
            for v in range(u + 1, n):
                if adj[u] >> v & 1:
                    for j in range(c):
                        es.append((c * u + i, c * v + j))
    return graph(c * n, es)


def degree_clique_expansion(g):
    """`G°`: a port per (vertex, incident edge); the ports of a vertex form a
    clique; the two ports of an edge are joined. Isolated vertices stay."""
    n, adj = g
    es = edges_of(g)
    port, cnt = {}, 0
    for i, (u, v) in enumerate(es):
        port[(u, i)] = cnt
        port[(v, i)] = cnt + 1
        cnt += 2
    new = []
    for u in range(n):
        ps = [port[(u, i)] for i, e in enumerate(es) if u in e]
        new += list(itertools.combinations(ps, 2))
    for i, (u, v) in enumerate(es):
        new.append((port[(u, i)], port[(v, i)]))
    iso = sum(1 for u in range(n) if adj[u] == 0)
    return graph(cnt + iso, new)


def mosp_instance(g):
    """One pattern per edge, one private pattern per isolated vertex; the
    customers are the vertices. Its MOSP graph is `G`."""
    n, adj = g
    es = edges_of(g)
    cols = [set(e) for e in es] + [{u} for u in range(n) if adj[u] == 0]
    return tuple(tuple(int(v in c) for c in cols) for v in range(n))


def lengauer_cliques(g):
    """Lengauer 1981 Thm 7: `v_i(j)`, `0 ≤ j ≤ N`, an `(N+1)`-clique per
    vertex; edge `v_i v_j` becomes `v_i(j) v_j(i)`."""
    n, adj = g
    N = n

    def idx(i, j):
        return i * (N + 1) + j

    es = []
    for i in range(n):
        for j in range(N + 1):
            for k in range(j + 1, N + 1):
                es.append((idx(i, j), idx(i, k)))
    for i, j in edges_of(g):
        es.append((idx(i, j), idx(j, i)))
    return graph(n * (N + 1), es)


# ----------------------------------------------------------------------------
# the checks
# ----------------------------------------------------------------------------


def atlas(nmax: int):
    from networkx.generators.atlas import graph_atlas_g
    return [from_nx(h) for h in graph_atlas_g() if 1 <= h.number_of_nodes() <= nmax]


def all_matrices(rows: int, cols: int):
    for bits in range(1 << (rows * cols)):
        yield tuple(tuple(bits >> (r * cols + c) & 1 for c in range(cols)) for r in range(rows))


def run_checks(nmax: int = 7, out_dir: Path = OUT, log=print, blowup3_nmax: int = 5,
               lengauer_nmax: int = 4, mosp_max_patterns: int = 14, matrices=(3, 4),
               expansion_max_ports: int = 20, seed: int = 0) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    graphs = atlas(nmax)
    res: dict = {"nmax": nmax, "graphs": len(graphs)}
    fails: dict[str, list] = {k: [] for k in
                              ["dp_vs_permutations", "cobipartite_double", "moehring_double",
                               "moehring_atlas", "blowup2", "blowup3", "expansion_lower",
                               "expansion_subcubic", "mosp_graph_to_instance",
                               "mosp_instance_to_graph", "lengauer"]}
    counts = Counter()
    excess = Counter()
    vs_cache = {}
    for g in graphs:
        n, adj = g
        v_dp = vs(g)
        v_perm = vertex_separation(g)
        counts["dp_vs_permutations"] += 1
        if v_dp != v_perm:
            fails["dp_vs_permutations"].append((g, v_dp, v_perm))
        vs_cache[g] = v_dp
    log(f"vs DP against permutations on {len(graphs)} graphs: {len(fails['dp_vs_permutations'])} failures")
    for g in graphs:
        n, adj = g
        v = vs_cache[g]
        # cobipartite double, and Möhring (pw = tw on AT-free) on the doubles
        H = cobipartite_double(g)
        vh = vs(H)
        counts["cobipartite_double"] += 1
        if vh != v + n:
            fails["cobipartite_double"].append((g, v, vh))
        counts["moehring_double"] += 1
        if treewidth(H) != vh:
            fails["moehring_double"].append((g, vh, treewidth(H)))
        if is_cobipartite(g):
            counts["moehring_atlas"] += 1
            if treewidth(g) != v:
                fails["moehring_atlas"].append((g, v, treewidth(g)))
        # clique blow-up
        counts["blowup2"] += 1
        if vs(clique_blowup(g, 2)) + 1 != 2 * (v + 1):
            fails["blowup2"].append((g, v, vs(clique_blowup(g, 2))))
        if n <= blowup3_nmax:
            counts["blowup3"] += 1
            if vs(clique_blowup(g, 3)) + 1 != 3 * (v + 1):
                fails["blowup3"].append((g, v, vs(clique_blowup(g, 3))))
        # degree-clique expansion against cutwidth
        Ge = degree_clique_expansion(g)
        if Ge[0] <= expansion_max_ports:
            cw = cutwidth_dp(g)
            ve = vs(Ge)
            d = max_degree(g)
            counts["expansion_lower"] += 1
            if ve < cw:
                fails["expansion_lower"].append((g, cw, ve))
            if d <= 3:
                counts["expansion_subcubic"] += 1
                if ve != cw:
                    fails["expansion_subcubic"].append((g, cw, ve))
            else:
                excess[(d, ve - cw)] += 1
        # MOSP: graph -> instance
        M = mosp_instance(g)
        if len(M[0]) <= mosp_max_patterns:
            counts["mosp_graph_to_instance"] += 1
            if mosp_subset_dp(M) != v + 1:
                fails["mosp_graph_to_instance"].append((g, v, mosp_subset_dp(M)))
        # Lengauer, quadratic, for the record
        if n <= lengauer_nmax:
            counts["lengauer"] += 1
            L = lengauer_cliques(g)
            vl = vs(L)
            if vl != modified_cutwidth_dp(g) + n:
                fails["lengauer"].append((g, modified_cutwidth_dp(g), vl))
    # MOSP: instance -> graph, every 0/1 matrix to `matrices`, by the pattern DP
    r, c = matrices
    for M in all_matrices(r, c):
        if not any(any(row) for row in M):
            continue
        counts["mosp_instance_to_graph"] += 1
        Gm = row_graph(M)
        if mosp_subset_dp(M) != vs(Gm) + 1:
            fails["mosp_instance_to_graph"].append((M, mosp_subset_dp(M), vs(Gm)))
    # the pattern DP itself against the literal definition on small matrices
    rng = np.random.default_rng(seed)
    dp_vs_perm = 0
    for _ in range(300):
        M = tuple(tuple(int(x) for x in row) for row in (rng.random((4, 6)) < 0.4).astype(int))
        if mosp_subset_dp(M) != mosp_permutations(M):
            dp_vs_perm += 1
    res["mosp_dp_vs_permutations_failures"] = dp_vs_perm
    res["counts"] = dict(counts)
    res["failures"] = {k: len(v) for k, v in fails.items()}
    res["examples"] = {k: [str(x) for x in v[:5]] for k, v in fails.items() if v}
    res["expansion_excess_by_max_degree"] = {f"{d}:{e}": k for (d, e), k in sorted(excess.items())}
    res["seconds"] = round(time.time() - t0, 1)
    (out_dir / "check.json").write_text(json.dumps(res, indent=2))
    for k in counts:
        log(f"{k:28s} checked {counts[k]:6d}  failures {len(fails[k])}")
    log(f"mosp pattern DP vs permutations: {dp_vs_perm} failures of 300")
    log(f"expansion excess vs(G°) − cw(G) by (Δ, excess): {res['expansion_excess_by_max_degree']}")
    log(f"{res['seconds']} s; written {out_dir / 'check.json'}")
    return res


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmax", type=int, default=7)
    ap.add_argument("--out", type=Path, default=OUT)
    a = ap.parse_args()
    run_checks(a.nmax, a.out)


if __name__ == "__main__":
    main()
