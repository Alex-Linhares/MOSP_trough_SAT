"""Exact pathwidth by closing-order search (Chu & Stuckey 2009, ported from MOSP).

`compute_pathwidth(G)` returns the width and an optimal closing order;
`solve(G)` returns the full `Solution` with its proof, bounds and budgets;
`decide_pathwidth(G, w)` answers a single "pw(G) <= w?".
"""

from __future__ import annotations

import networkx as nx

from pathwidth.bounds import contraction_degeneracy, degeneracy, greedy_order, lower_bound
from pathwidth.graph import (
    FAN_ORDERS,
    layout_from_order,
    masks_from_graph,
    path_decomposition,
    vertex_separation,
)
from pathwidth.search import Decision, GraphDecision, decide, decide_pathwidth
from pathwidth.solve import Solution, solve, solve_masks

__all__ = [
    "FAN_ORDERS", "Decision", "GraphDecision", "Solution", "compute_pathwidth",
    "contraction_degeneracy", "decide", "decide_pathwidth", "degeneracy", "greedy_order",
    "layout_from_order", "lower_bound", "masks_from_graph", "path_decomposition", "solve",
    "solve_masks", "vertex_separation",
]


def compute_pathwidth(G: nx.Graph, **kwargs: object) -> tuple[int, list]:
    """Pathwidth of `G` and an optimal closing order, proved.

    Raises `RuntimeError` if a budget (`max_nodes`, `time_budget`) stopped the
    descent before optimality was proved; use `solve` to get the bound found.
    """
    sol = solve(G, **kwargs)
    if not sol.proved:
        raise RuntimeError(f"compute_pathwidth: budget exhausted at width {sol.width} "
                           f"(lower bound {sol.lower}); use solve() for the partial result")
    return sol.width, sol.order
