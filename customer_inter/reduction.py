"""Reduction between MOSP and pathwidth of the customer intersection graph.

Theorem: Let M be a MOSP instance and G_c(M) its customer intersection graph.
    Then: optimal MOSP value = pathwidth(G_c(M)) + 1

This module provides:
  - mosp_to_pathwidth: Map a MOSP instance to a pathwidth problem on the
    customer graph.
  - pathwidth_to_mosp: Map a pathwidth solution (customer ordering) back to
    a MOSP solution (pattern ordering).
"""

from __future__ import annotations

from dataclasses import dataclass

import networkx as nx

from mosp.instance import MOSPInstance
from customer_inter.customer_graph import build_customer_graph


@dataclass
class CustomerPathwidthProblem:
    """A pathwidth problem instance derived from a MOSP instance via customer graph."""
    graph: nx.Graph
    source_instance: MOSPInstance


@dataclass
class CustomerMOSPSolution:
    """A MOSP solution obtained via the customer intersection graph."""
    ordering: list[int]            # Pattern production sequence
    max_open_stacks: int           # MOSP objective value
    pathwidth: int                 # Pathwidth of the customer graph
    customer_graph: nx.Graph       # The customer intersection graph
    customer_ordering: list[int]   # The customer ordering achieving pathwidth


def mosp_to_pathwidth(instance: MOSPInstance) -> CustomerPathwidthProblem:
    """Reduce a MOSP instance to a pathwidth problem on the customer graph.

    Args:
        instance: A MOSP instance.

    Returns:
        A CustomerPathwidthProblem containing the customer intersection graph
        and source instance.
    """
    G = build_customer_graph(instance)
    return CustomerPathwidthProblem(graph=G, source_instance=instance)


def customer_ordering_to_pattern_ordering(
    instance: MOSPInstance, customer_ordering: list[int]
) -> list[int]:
    """Derive a pattern ordering from a customer ordering.

    Given a customer ordering sigma = [c_0, c_1, ..., c_{n-1}], assign each
    pattern p a priority:
      - first(p) = min position of any customer needing p in sigma
      - last(p) = max position of any customer needing p in sigma

    Sort patterns by (first(p), last(p)) ascending. This processes patterns
    as their earliest customer arrives, breaking ties by earliest completion.

    Args:
        instance: A MOSP instance.
        customer_ordering: A permutation of customer indices (0..n-1).

    Returns:
        A permutation of pattern indices (0..m-1).
    """
    n = instance.n_customers
    m = instance.n_patterns

    # Map each customer to its position in the ordering
    pos = {c: i for i, c in enumerate(customer_ordering)}

    pattern_priority = []
    for p in range(m):
        customers = instance.pattern_customers(p)
        if customers:
            positions = [pos[c] for c in customers]
            first = min(positions)
            last = max(positions)
        else:
            # Pattern not needed by any customer — place at end
            first = n
            last = n
        pattern_priority.append((first, last, p))

    pattern_priority.sort()
    return [p for _, _, p in pattern_priority]


def pathwidth_to_mosp(
    pw_problem: CustomerPathwidthProblem,
    pathwidth: int,
    customer_ordering: list[int],
) -> CustomerMOSPSolution:
    """Convert a pathwidth solution on the customer graph to a MOSP solution.

    Args:
        pw_problem: The customer pathwidth problem that was solved.
        pathwidth: The computed pathwidth of the customer graph.
        customer_ordering: The linear ordering achieving this pathwidth.

    Returns:
        A CustomerMOSPSolution with the pattern production sequence and
        MOSP value.
    """
    instance = pw_problem.source_instance
    pattern_ordering = customer_ordering_to_pattern_ordering(
        instance, customer_ordering
    )

    return CustomerMOSPSolution(
        ordering=pattern_ordering,
        max_open_stacks=pathwidth + 1,
        pathwidth=pathwidth,
        customer_graph=pw_problem.graph,
        customer_ordering=customer_ordering,
    )
