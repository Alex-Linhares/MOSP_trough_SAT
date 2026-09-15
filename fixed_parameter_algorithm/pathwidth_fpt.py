"""FPT pathwidth computation via branch-and-bound with iterative deepening.

For graphs with small pathwidth k, this algorithm runs in f(k) * poly(n) time
in practice, enabling computation on graphs with 100+ vertices when k is small
(k <= 5-8). For small graphs (n <= 18), it delegates to the exact DP solver.

Algorithm overview:
  1. Preprocessing: remove degree-1 vertices, decompose into components
  2. Greedy heuristic: compute an upper bound on pathwidth
  3. Lower bound: max clique size - 1
  4. Iterative deepening: for k = lower..upper, test if pathwidth <= k
  5. Decision procedure: DFS/backtracking building a vertex ordering,
     pruning when the active suffix (vertex separation) exceeds k

Memoization uses bitmasks for n <= 30; for larger graphs, relies on pruning.
"""

from __future__ import annotations

from typing import Optional

import networkx as nx

from fixed_parameter_algorithm.pathwidth import compute_pathwidth


def compute_pathwidth_fpt(
    G: nx.Graph, max_width: int | None = None
) -> tuple[int, list[int]]:
    """Compute the exact pathwidth and a witness linear ordering using FPT techniques.

    For small graphs (n <= 18), delegates to the exact DP solver.
    For larger graphs, uses branch-and-bound with iterative deepening on the
    target width k.

    Args:
        G: A NetworkX graph.
        max_width: Optional upper bound on width to search. If None, a greedy
            heuristic computes one.

    Returns:
        (pathwidth, ordering) where ordering is a list of vertices
        achieving the optimal vertex separation = pathwidth.
    """
    nodes = sorted(G.nodes())
    n = len(nodes)

    if n == 0:
        return 0, []
    if n == 1:
        return 0, list(nodes)

    # For small graphs, use the exact DP (faster for n <= 18)
    if n <= 18:
        return compute_pathwidth(G)

    # Handle disconnected graphs: pathwidth = max over components
    if not nx.is_connected(G):
        return _solve_disconnected(G, max_width)

    # Preprocess: iteratively remove degree-1 vertices
    core_graph, pendant_map = _preprocess(G)

    if core_graph.number_of_nodes() == 0:
        # Graph was a tree (or forest) — pathwidth is 1 if it had edges, 0 otherwise
        if G.number_of_edges() == 0:
            return 0, nodes
        return 1, _tree_ordering(G)

    if core_graph.number_of_nodes() <= 18:
        core_pw, core_ordering = compute_pathwidth(core_graph)
    else:
        core_pw, core_ordering = _solve_core(core_graph, max_width)

    # Reinsert pendant vertices into the ordering
    full_ordering = _reinsert_pendants(G, core_ordering, pendant_map)

    # The pathwidth is at least 1 if the graph has edges
    pw = max(core_pw, 1) if G.number_of_edges() > 0 else core_pw

    return pw, full_ordering


def _solve_disconnected(
    G: nx.Graph, max_width: int | None
) -> tuple[int, list[int]]:
    """Solve pathwidth for a disconnected graph by solving each component."""
    best_pw = 0
    full_ordering = []

    components = sorted(nx.connected_components(G), key=len, reverse=True)

    for comp_nodes in components:
        subgraph = G.subgraph(comp_nodes).copy()
        pw, ordering = compute_pathwidth_fpt(subgraph, max_width)
        best_pw = max(best_pw, pw)
        full_ordering.extend(ordering)

    return best_pw, full_ordering


def _preprocess(G: nx.Graph) -> tuple[nx.Graph, dict]:
    """Remove degree-1 vertices iteratively.

    Pendant vertices don't affect pathwidth (they can always be placed
    adjacent to their neighbor in the ordering without increasing width).

    Returns:
        (core_graph, pendant_map) where pendant_map maps each core vertex
        to the list of pendant vertices that were attached to it.
    """
    H = G.copy()
    pendant_map: dict = {v: [] for v in H.nodes()}

    changed = True
    while changed:
        changed = False
        to_remove = []
        for v in list(H.nodes()):
            if H.degree(v) == 1:
                neighbor = next(iter(H.neighbors(v)))
                to_remove.append((v, neighbor))
                changed = True

        for v, neighbor in to_remove:
            if v in H:
                if neighbor not in pendant_map:
                    pendant_map[neighbor] = []
                pendant_map[neighbor].append(v)
                H.remove_node(v)
                if v in pendant_map:
                    # Transfer v's pendants to neighbor
                    pendant_map[neighbor].extend(pendant_map.pop(v))

    # Clean up pendant_map to only include core vertices
    core_nodes = set(H.nodes())
    clean_map = {v: pendant_map.get(v, []) for v in core_nodes}

    return H, clean_map


def _tree_ordering(G: nx.Graph) -> list:
    """Compute a pathwidth-1 ordering for a tree (or forest)."""
    if G.number_of_nodes() == 0:
        return []
    if G.number_of_edges() == 0:
        return sorted(G.nodes())

    ordering = []
    visited = set()

    for component in nx.connected_components(G):
        subgraph = G.subgraph(component)
        # DFS ordering achieves pathwidth 1 for trees
        root = min(component)
        stack = [root]
        while stack:
            v = stack.pop()
            if v in visited:
                continue
            visited.add(v)
            ordering.append(v)
            for u in sorted(subgraph.neighbors(v), reverse=True):
                if u not in visited:
                    stack.append(u)

    return ordering


def _reinsert_pendants(
    G: nx.Graph, core_ordering: list, pendant_map: dict
) -> list:
    """Reinsert pendant vertices into the ordering.

    Each pendant is placed immediately before its anchor vertex in the ordering.
    This doesn't increase the pathwidth.
    """
    full_ordering = []
    placed = set()

    for v in core_ordering:
        # Place pendants of v before v
        pendants = pendant_map.get(v, [])
        for p in sorted(pendants):
            if p not in placed:
                full_ordering.append(p)
                placed.add(p)
        full_ordering.append(v)
        placed.add(v)

    # Any remaining nodes not in core or pendants (shouldn't happen but be safe)
    for v in sorted(G.nodes()):
        if v not in placed:
            full_ordering.append(v)

    return full_ordering


def _solve_core(
    G: nx.Graph, max_width: int | None
) -> tuple[int, list[int]]:
    """Solve pathwidth for a connected core graph (no degree-1 vertices, n > 25).

    Uses branch-and-bound with iterative deepening.
    """
    nodes = sorted(G.nodes())
    n = len(nodes)

    # Map node labels to indices 0..n-1
    node_to_idx = {v: i for i, v in enumerate(nodes)}
    idx_to_node = {i: v for i, v in enumerate(nodes)}

    # Precompute adjacency as bitmasks (for n <= 60, use Python ints)
    adj = [0] * n
    for u, v in G.edges():
        ui, vi = node_to_idx[u], node_to_idx[v]
        adj[ui] |= (1 << vi)
        adj[vi] |= (1 << ui)

    # Compute greedy upper bound
    k_upper = _greedy_upper_bound(n, adj)
    if max_width is not None:
        k_upper = min(k_upper, max_width)

    # Compute lower bound: max clique size - 1
    k_lower = _clique_lower_bound(G) - 1

    # Iterative deepening
    for k in range(k_lower, k_upper + 1):
        result = _has_pathwidth_leq(n, adj, k)
        if result is not None:
            ordering = [idx_to_node[i] for i in result]
            return k, ordering

    # Fallback: the greedy ordering itself achieves k_upper
    greedy_ordering_indices = _greedy_ordering(n, adj)
    ordering = [idx_to_node[i] for i in greedy_ordering_indices]
    return k_upper, ordering


def _greedy_upper_bound(n: int, adj: list[int]) -> int:
    """Compute an upper bound on pathwidth using a greedy heuristic.

    Greedily builds an ordering by choosing at each step the vertex
    that minimizes the resulting active suffix (vertex separation).
    """
    ordering = _greedy_ordering(n, adj)
    return _ordering_width(n, adj, ordering)


def _greedy_ordering(n: int, adj: list[int]) -> list[int]:
    """Compute a greedy vertex ordering minimizing active suffix at each step."""
    placed_mask = 0
    remaining = set(range(n))
    ordering = []

    for step in range(n):
        best_v = -1
        best_sep = n + 1

        for v in remaining:
            new_mask = placed_mask | (1 << v)
            sep = _vertex_separation_at(n, adj, new_mask)
            if sep < best_sep or (sep == best_sep and v < best_v):
                best_sep = sep
                best_v = v

        ordering.append(best_v)
        placed_mask |= (1 << best_v)
        remaining.remove(best_v)

    return ordering


def _ordering_width(n: int, adj: list[int], ordering: list[int]) -> int:
    """Compute the vertex separation (pathwidth) of a given ordering."""
    placed_mask = 0
    max_sep = 0

    for v in ordering:
        placed_mask |= (1 << v)
        sep = _vertex_separation_at(n, adj, placed_mask)
        max_sep = max(max_sep, sep)

    return max_sep


def _vertex_separation_at(n: int, adj: list[int], placed_mask: int) -> int:
    """Compute vertex separation: count unplaced vertices adjacent to placed ones."""
    nbrs_of_placed = 0
    s = placed_mask
    while s:
        bit = s & (-s)
        idx = bit.bit_length() - 1
        nbrs_of_placed |= adj[idx]
        s ^= bit
    # Vertices outside placed_mask that are neighbors of placed_mask
    active = nbrs_of_placed & ~placed_mask
    return bin(active).count('1')


def _clique_lower_bound(G: nx.Graph) -> int:
    """Compute a lower bound using a greedy max clique approximation.

    pathwidth >= omega(G) - 1 where omega(G) is the clique number.
    We use a greedy approach for speed.
    """
    # Use networkx's greedy clique approximation
    clique = max(nx.find_cliques(G), key=len, default=[])
    return len(clique)


def _has_pathwidth_leq(
    n: int, adj: list[int], k: int
) -> list[int] | None:
    """Test if pathwidth <= k. Returns a witness ordering or None.

    Uses DFS/backtracking, building the ordering left-to-right.
    Prunes when the active suffix exceeds k.
    """
    use_memo = n <= 30

    if use_memo:
        # memo[remaining_mask] = minimum width achievable for the remaining vertices,
        # or n+1 if no ordering with width <= k exists
        memo: dict[int, int] = {}

    full_mask = (1 << n) - 1
    best_ordering: list[int] = []

    def dfs(placed_mask: int, ordering: list[int], current_max: int) -> bool:
        nonlocal best_ordering

        remaining_mask = full_mask ^ placed_mask

        if remaining_mask == 0:
            best_ordering = list(ordering)
            return True

        if use_memo:
            if remaining_mask in memo and memo[remaining_mask] > k:
                return False

        # Determine candidate vertices to place next
        # Prefer vertices in the active suffix (adjacent to placed vertices)
        # as they are already "open" and placing them reduces the suffix
        if placed_mask == 0:
            candidates = list(range(n))
        else:
            # Active suffix: unplaced vertices adjacent to placed vertices
            active_mask = 0
            s = placed_mask
            while s:
                bit = s & (-s)
                idx = bit.bit_length() - 1
                active_mask |= adj[idx]
                s ^= bit
            active_mask &= remaining_mask

            if active_mask:
                # Prefer active vertices, sorted by degree in remaining subgraph
                # (fewer remaining neighbors = less future branching)
                active_list = []
                a = active_mask
                while a:
                    bit = a & (-a)
                    idx = bit.bit_length() - 1
                    # Count neighbors in remaining (excluding self)
                    remaining_nbrs = bin(adj[idx] & remaining_mask & ~(1 << idx)).count('1')
                    active_list.append((remaining_nbrs, idx))
                    a ^= bit
                active_list.sort()
                candidates = [idx for _, idx in active_list]

                # Also add non-active vertices (for completeness in disconnected remaining)
                non_active = remaining_mask & ~active_mask
                if non_active:
                    na_list = []
                    s = non_active
                    while s:
                        bit = s & (-s)
                        idx = bit.bit_length() - 1
                        na_list.append(idx)
                        s ^= bit
                    candidates.extend(na_list)
            else:
                # No active vertices — remaining graph is disconnected from placed
                # Pick the vertex with smallest index from remaining
                candidates = []
                s = remaining_mask
                while s:
                    bit = s & (-s)
                    idx = bit.bit_length() - 1
                    candidates.append(idx)
                    s ^= bit

        for v in candidates:
            new_placed = placed_mask | (1 << v)
            sep = _vertex_separation_at(n, adj, new_placed)

            if sep > k:
                continue

            new_max = max(current_max, sep)

            ordering.append(v)
            if dfs(new_placed, ordering, new_max):
                return True
            ordering.pop()

        if use_memo:
            memo[remaining_mask] = k + 1  # Mark as infeasible at this k

        return False

    if dfs(0, [], 0):
        return best_ordering
    return None

