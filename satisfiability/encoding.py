"""SAT encoding for the pathwidth decision problem.

Position-based formulation: given graph G and target width k, encode
"does G have pathwidth <= k?" as a CNF formula.

Variables (managed via pysat IDPool):
  x[v,t] — vertex v is placed at position t
  y[v,t] — vertex v is placed by step t (prefix membership)
  s[v,t] — vertex v is separated at step t (not yet placed, but has a placed neighbor)

Clauses:
  1. Permutation: each vertex gets exactly one position, each position gets exactly one vertex
  2. Prefix linking: x[v,t] -> y[v,t]; y[v,t] -> y[v,t+1]; y[v,t] -> y[v,t-1] OR x[v,t]
  3. Separation: for each edge (u,v), if u is placed by step t but v is not, then v is separated
  4. Width bound: at most k vertices are separated at each step
"""

from __future__ import annotations

import networkx as nx
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool


def encode_pathwidth_decision(
    G: nx.Graph,
    k: int,
    node_list: list | None = None,
) -> tuple[CNF, IDPool, list, int]:
    """Encode the decision problem 'pathwidth(G) <= k?' as a CNF formula.

    Args:
        G: A NetworkX graph (should be connected, no isolated vertices for best results).
        k: Target pathwidth bound.
        node_list: Optional fixed ordering of nodes. If None, uses sorted(G.nodes()).

    Returns:
        (cnf, pool, node_list, n) where:
          - cnf: the CNF formula
          - pool: the IDPool mapping variable names to SAT variable IDs
          - node_list: the list of node labels in index order
          - n: number of vertices
    """
    if node_list is None:
        node_list = sorted(G.nodes())
    n = len(node_list)
    node_to_idx = {v: i for i, v in enumerate(node_list)}

    # Build adjacency list as index sets
    adj: list[list[int]] = [[] for _ in range(n)]
    for u, v in G.edges():
        ui, vi = node_to_idx[u], node_to_idx[v]
        adj[ui].append(vi)
        adj[vi].append(ui)

    pool = IDPool()
    cnf = CNF()

    # Variable accessors
    def x(v: int, t: int) -> int:
        return pool.id(("x", v, t))

    def y(v: int, t: int) -> int:
        return pool.id(("y", v, t))

    def s(v: int, t: int) -> int:
        return pool.id(("s", v, t))

    # Track the top variable ID so CardEnc doesn't collide
    def top() -> int:
        return pool.top

    # -------------------------------------------------------
    # 1. Permutation constraints
    # -------------------------------------------------------
    # Each vertex is assigned to at least one position
    for v in range(n):
        cnf.append([x(v, t) for t in range(n)])

    # Each vertex is assigned to at most one position (ladder encoding)
    for v in range(n):
        lits = [x(v, t) for t in range(n)]
        atmost = CardEnc.atmost(lits, bound=1, top_id=top(), encoding=EncType.ladder)
        pool.occupy(pool.top + 1, atmost.nv)
        cnf.extend(atmost)

    # Each position has at least one vertex
    for t in range(n):
        cnf.append([x(v, t) for v in range(n)])

    # Each position has at most one vertex (ladder encoding)
    for t in range(n):
        lits = [x(v, t) for v in range(n)]
        atmost = CardEnc.atmost(lits, bound=1, top_id=top(), encoding=EncType.ladder)
        pool.occupy(pool.top + 1, atmost.nv)
        cnf.extend(atmost)

    # -------------------------------------------------------
    # 2. Prefix linking
    # -------------------------------------------------------
    for v in range(n):
        for t in range(n):
            # x[v,t] -> y[v,t]
            cnf.append([-x(v, t), y(v, t)])

            # y[v,t] -> y[v,t+1]  (monotonicity)
            if t < n - 1:
                cnf.append([-y(v, t), y(v, t + 1)])

            # y[v,t] -> y[v,t-1] OR x[v,t]
            # (if v is placed by step t, then either it was placed by step t-1
            #  or it was placed exactly at step t)
            if t > 0:
                cnf.append([-y(v, t), y(v, t - 1), x(v, t)])

    # -------------------------------------------------------
    # 3. Separation definition
    # -------------------------------------------------------
    for v in range(n):
        for t in range(n):
            # If v is placed by step t, it cannot be separated at step t
            # y[v,t] -> NOT s[v,t]
            cnf.append([-y(v, t), -s(v, t)])

            # For each neighbor u of v:
            # If u is placed by step t but v is not, then v is separated at step t
            # y[u,t] AND NOT y[v,t] -> s[v,t]
            # Equivalently: NOT y[u,t] OR y[v,t] OR s[v,t]
            for u in adj[v]:
                cnf.append([-y(u, t), y(v, t), s(v, t)])

    # -------------------------------------------------------
    # 4. Width bound: at most k vertices separated at each step
    # -------------------------------------------------------
    for t in range(n):
        sep_lits = [s(v, t) for v in range(n)]
        atmost = CardEnc.atmost(
            sep_lits, bound=k, top_id=top(), encoding=EncType.totalizer
        )
        pool.occupy(pool.top + 1, atmost.nv)
        cnf.extend(atmost)

    # -------------------------------------------------------
    # 5. Symmetry breaking: fix the first vertex at position 0
    # -------------------------------------------------------
    cnf.append([x(0, 0)])

    return cnf, pool, node_list, n


def extract_ordering(
    model: list[int],
    pool: IDPool,
    node_list: list,
    n: int,
) -> list:
    """Extract the vertex ordering from a satisfying assignment.

    Args:
        model: List of literals (positive = true, negative = false).
        pool: The IDPool used during encoding.
        node_list: List of node labels in index order.
        n: Number of vertices.

    Returns:
        A list of node labels in the order determined by the assignment.
    """
    true_vars = set(model)
    ordering = [None] * n

    for v in range(n):
        for t in range(n):
            var_id = pool.id(("x", v, t))
            if var_id in true_vars:
                ordering[t] = node_list[v]
                break

    return ordering
