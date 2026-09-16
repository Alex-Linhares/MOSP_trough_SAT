"""SAT-based pathwidth solver with preprocessing and iterative deepening.

Delegates to exact DP for n <= 18. For larger graphs, preprocesses
(pendant removal, component decomposition), computes bounds, then
uses the SAT encoding with iterative deepening over target width k.
"""

from __future__ import annotations

import networkx as nx

from fixed_parameter_algorithm.pathwidth import compute_pathwidth, compute_vertex_separation
from fixed_parameter_algorithm.pathwidth_fpt import (
    _clique_lower_bound,
    _greedy_ordering,
    _greedy_upper_bound,
    _ordering_width,
    _preprocess,
    _reinsert_pendants,
    _tree_ordering,
)
from satisfiability.encoding import encode_pathwidth_decision, extract_ordering


def compute_pathwidth_sat(
    G: nx.Graph, max_width: int | None = None
) -> tuple[int, list[int]]:
    """Compute the exact pathwidth and a witness ordering using SAT solving.

    For small graphs (n <= 18), delegates to the exact DP solver.
    For larger graphs, uses preprocessing (pendant removal, component
    decomposition), greedy/clique bounds, and a SAT-based decision
    procedure with iterative deepening.

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

    # For small graphs, use the exact DP
    if n <= 18:
        return compute_pathwidth(G)

    # Handle disconnected graphs: pathwidth = max over components
    if not nx.is_connected(G):
        return _solve_disconnected(G, max_width)

    # Preprocess: iteratively remove degree-1 vertices
    core_graph, pendant_map = _preprocess(G)

    if core_graph.number_of_nodes() == 0:
        # Graph was a tree (or forest)
        if G.number_of_edges() == 0:
            return 0, nodes
        return 1, _tree_ordering(G)

    if core_graph.number_of_nodes() <= 18:
        core_pw, core_ordering = compute_pathwidth(core_graph)
    else:
        core_pw, core_ordering = _solve_core_sat(core_graph, max_width)

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
        pw, ordering = compute_pathwidth_sat(subgraph, max_width)
        best_pw = max(best_pw, pw)
        full_ordering.extend(ordering)

    return best_pw, full_ordering


def _solve_core_sat(
    G: nx.Graph, max_width: int | None
) -> tuple[int, list[int]]:
    """Solve pathwidth for a connected core graph using SAT encoding.

    Uses iterative deepening: for k = lower_bound .. upper_bound,
    test if pathwidth <= k using a SAT solver.
    """
    nodes = sorted(G.nodes())
    n = len(nodes)

    # Map node labels to indices 0..n-1 for bitmask operations
    node_to_idx = {v: i for i, v in enumerate(nodes)}
    idx_to_node = {i: v for i, v in enumerate(nodes)}

    # Bitmask adjacency for greedy bounds
    adj = [0] * n
    for u, v in G.edges():
        ui, vi = node_to_idx[u], node_to_idx[v]
        adj[ui] |= 1 << vi
        adj[vi] |= 1 << ui

    # Compute greedy upper bound
    k_upper = _greedy_upper_bound(n, adj)
    if max_width is not None:
        k_upper = min(k_upper, max_width)

    # Compute lower bound: max clique size - 1
    k_lower = _clique_lower_bound(G) - 1

    # If lower == upper, we already know the answer; just return greedy ordering
    if k_lower == k_upper:
        greedy_idx = _greedy_ordering(n, adj)
        ordering = [idx_to_node[i] for i in greedy_idx]
        return k_upper, ordering

    # Iterative deepening with SAT
    for k in range(k_lower, k_upper + 1):
        result = _sat_decision(G, k, nodes)
        if result is not None:
            return k, result

    # Fallback: the greedy ordering achieves k_upper
    greedy_idx = _greedy_ordering(n, adj)
    ordering = [idx_to_node[i] for i in greedy_idx]
    return k_upper, ordering


def _sat_decision(
    G: nx.Graph,
    k: int,
    node_list: list,
) -> list | None:
    """Test if pathwidth(G) <= k using SAT encoding.

    Returns a witness ordering if satisfiable, None otherwise.
    """
    from pysat.solvers import Solver

    cnf, pool, node_list, n = encode_pathwidth_decision(G, k, node_list)

    with Solver(name="cd195", bootstrap_with=cnf) as solver:
        if solver.solve():
            model = solver.get_model()
            return extract_ordering(model, pool, node_list, n)

    return None
