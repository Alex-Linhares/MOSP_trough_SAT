"""Exact pathwidth computation via dynamic programming over vertex subsets.

Pathwidth is equivalent to vertex separation number (Kinnersley 1992):
  PW(G) = VS(G)

The vertex separation of a linear ordering σ of V(G) is:
  vs(σ) = max_{1 ≤ i ≤ n} |{ v ∈ {σ(i+1),...,σ(n)} : ∃ u ∈ {σ(1),...,σ(i)}, uv ∈ E }|

We compute the pathwidth using a Held-Karp style DP:
  - State: (S, v) where S ⊆ V is the set of vertices placed so far, v is the last placed vertex
  - Value: minimum vertex separation achievable for the ordering of S ending with v
  - Transition: extend by adding a new vertex u ∉ S

This gives O(2^n · n²) time and O(2^n · n) space.
Practical for n ≤ ~23-25 vertices.
"""

from __future__ import annotations

from typing import Optional

import networkx as nx


def compute_pathwidth(G: nx.Graph) -> tuple[int, list[int]]:
    """Compute the exact pathwidth and a witness linear ordering.

    Args:
        G: A NetworkX graph.

    Returns:
        (pathwidth, ordering) where ordering is a list of vertices
        achieving the optimal vertex separation = pathwidth.

    Raises:
        ValueError: If the graph has more than 25 vertices.
    """
    nodes = sorted(G.nodes())
    n = len(nodes)

    if n == 0:
        return 0, []
    if n == 1:
        return 0, list(nodes)

    if n > 25:
        raise ValueError(
            f"Graph has {n} vertices; exact DP is only practical for n ≤ 25."
        )

    # Map node labels to indices 0..n-1
    node_to_idx = {v: i for i, v in enumerate(nodes)}
    idx_to_node = {i: v for i, v in enumerate(nodes)}

    # Precompute adjacency as bitmasks
    adj = [0] * n
    for u, v in G.edges():
        ui, vi = node_to_idx[u], node_to_idx[v]
        adj[ui] |= (1 << vi)
        adj[vi] |= (1 << ui)

    # Precompute: for each subset S (bitmask), the set of vertices outside S
    # that are adjacent to at least one vertex in S.
    # This is the "boundary" or "open neighborhood outside S".
    # We need this to compute the vertex separation at each step.

    # For efficiency, we compute the cost of placing vertex v into set S:
    # After placing all of S ∪ {v}, the vertex separation at this step is
    # |{w ∉ S ∪ {v} : w is adjacent to some vertex in S ∪ {v}}|
    # = popcount(neighbors_of(S ∪ {v}) & ~(S ∪ {v}))

    full = (1 << n) - 1

    def _neighbors_outside(subset_mask: int) -> int:
        """Return bitmask of vertices outside subset that have a neighbor in subset."""
        nbrs = 0
        s = subset_mask
        while s:
            bit = s & (-s)  # lowest set bit
            idx = bit.bit_length() - 1
            nbrs |= adj[idx]
            s ^= bit
        return nbrs & ~subset_mask

    def _popcount(x: int) -> int:
        return bin(x).count('1')

    # DP tables
    # dp[mask][v] = minimum over all orderings of 'mask' ending with vertex v
    #               of the maximum vertex separation seen so far.
    # We store dp as a dict of {mask: {v: cost}} for space efficiency on sparse states.
    # But for small n, a flat array is fine.

    INF = n + 1

    # Use arrays for speed: dp[mask * n + v]
    size = (1 << n) * n
    dp = [INF] * size
    parent = [-1] * size  # for backtracking the ordering

    # Base case: place a single vertex v
    for v in range(n):
        mask = 1 << v
        sep = _popcount(_neighbors_outside(mask))
        dp[mask * n + v] = sep

    # Fill DP in order of increasing subset size
    for mask in range(1, 1 << n):
        popcount_mask = _popcount(mask)
        if popcount_mask < 2:
            continue

        # For each possible last vertex v in mask
        s = mask
        while s:
            vbit = s & (-s)
            v = vbit.bit_length() - 1
            s ^= vbit

            prev_mask = mask ^ vbit  # mask without v
            # The vertex separation at this step
            sep_here = _popcount(_neighbors_outside(mask))

            # Try all possible predecessors u (the previous last vertex)
            ps = prev_mask
            while ps:
                ubit = ps & (-ps)
                u = ubit.bit_length() - 1
                ps ^= ubit

                prev_cost = dp[prev_mask * n + u]
                cost = max(prev_cost, sep_here)
                if cost < dp[mask * n + v]:
                    dp[mask * n + v] = cost
                    parent[mask * n + v] = prev_mask * n + u

    # Find the optimal: the full mask, minimized over all last vertices
    full_mask = (1 << n) - 1
    best_cost = INF
    best_last = -1
    for v in range(n):
        c = dp[full_mask * n + v]
        if c < best_cost:
            best_cost = c
            best_last = v

    # Backtrack to recover the ordering
    ordering_indices = []
    state = full_mask * n + best_last
    while state != -1:
        v = state % n
        ordering_indices.append(v)
        state = parent[state]

    ordering_indices.reverse()
    ordering = [idx_to_node[i] for i in ordering_indices]

    return best_cost, ordering


def compute_vertex_separation(G: nx.Graph, ordering: list) -> int:
    """Compute the vertex separation number of a given linear ordering.

    Args:
        G: A NetworkX graph.
        ordering: A permutation of G's vertices.

    Returns:
        The vertex separation number (max over all prefixes of the number
        of vertices in the remaining suffix adjacent to the prefix).
    """
    node_set = set(G.nodes())
    placed = set()
    remaining = set(ordering)
    max_sep = 0

    for v in ordering:
        placed.add(v)
        remaining.discard(v)
        # Count vertices in remaining that have a neighbor in placed
        sep = sum(1 for w in remaining if any(u in placed for u in G.neighbors(w)))
        max_sep = max(max_sep, sep)

    return max_sep
