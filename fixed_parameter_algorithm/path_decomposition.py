"""Extract a path decomposition from a linear vertex ordering.

Given a graph G and a linear ordering σ of its vertices, we construct a
path decomposition (a sequence of bags B_1, B_2, ..., B_n) such that:
  1. Every vertex appears in at least one bag.
  2. For every edge uv, there is a bag containing both u and v.
  3. For every vertex v, the set of bags containing v is contiguous.

The width of the decomposition is max(|B_i|) - 1.

Construction: For each position i in the ordering, the bag B_i contains
vertex σ(i) plus all vertices σ(j) with j > i that have a neighbor σ(k)
with k ≤ i. Equivalently, B_i = {σ(i)} ∪ {σ(j) : j > i, ∃ k ≤ i with σ(k)σ(j) ∈ E}.
This is the standard "vertex separation to path decomposition" construction.
"""

from __future__ import annotations

import networkx as nx


def ordering_to_path_decomposition(
    G: nx.Graph, ordering: list
) -> list[set]:
    """Convert a linear vertex ordering to a path decomposition.

    Args:
        G: A NetworkX graph.
        ordering: A permutation of G's vertices.

    Returns:
        A list of bags (sets of vertices). The width of the decomposition
        is max(len(bag) for bag in bags) - 1.
    """
    n = len(ordering)
    if n == 0:
        return []

    pos = {v: i for i, v in enumerate(ordering)}
    bags = []

    for i in range(n):
        bag = {ordering[i]}
        placed = set(ordering[:i + 1])
        # Add vertices after position i that have a neighbor at position ≤ i
        for j in range(i + 1, n):
            w = ordering[j]
            if any(u in placed for u in G.neighbors(w)):
                bag.add(w)
        bags.append(bag)

    return bags


def path_decomposition_width(bags: list[set]) -> int:
    """Return the width of a path decomposition."""
    if not bags:
        return 0
    return max(len(bag) for bag in bags) - 1


def ordering_to_mosp_sequence(ordering: list[int]) -> list[int]:
    """Convert a linear ordering of pattern nodes to a MOSP production sequence.

    The ordering of patterns in the linear layout directly gives the
    production sequence for MOSP. This function is essentially the identity
    but makes the semantic mapping explicit.

    Args:
        ordering: A list of pattern indices from the pathwidth solver.

    Returns:
        The same list, interpreted as a production sequence for MOSP.
    """
    return list(ordering)
