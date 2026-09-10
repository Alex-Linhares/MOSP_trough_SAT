"""Formal reduction between MOSP and pathwidth.

Theorem (Yanasse 1997, Kinnersley 1992):
    Let M be a MOSP instance and G(M) its agreement graph.
    Then: optimal MOSP value = pathwidth(G(M)) + 1

This module provides:
  - mosp_to_pathwidth: Map a MOSP instance to a pathwidth problem (graph).
  - pathwidth_to_mosp: Map a pathwidth solution back to a MOSP solution.
"""

from __future__ import annotations

from dataclasses import dataclass

import networkx as nx

from mosp.instance import MOSPInstance
from mosp.agreement_graph import build_agreement_graph


@dataclass
class PathwidthProblem:
    """A pathwidth problem instance derived from a MOSP instance."""
    graph: nx.Graph
    source_instance: MOSPInstance


@dataclass
class MOSPSolution:
    """A complete MOSP solution."""
    ordering: list[int]        # Pattern production sequence
    max_open_stacks: int       # Optimal MOSP objective value
    pathwidth: int             # Pathwidth of the agreement graph
    agreement_graph: nx.Graph  # The MOSP/agreement graph


def mosp_to_pathwidth(instance: MOSPInstance) -> PathwidthProblem:
    """Reduce a MOSP instance to a pathwidth problem.

    Args:
        instance: A MOSP instance.

    Returns:
        A PathwidthProblem containing the agreement graph and source instance.
    """
    G = build_agreement_graph(instance)
    return PathwidthProblem(graph=G, source_instance=instance)


def pathwidth_to_mosp(
    pw_problem: PathwidthProblem,
    pathwidth: int,
    ordering: list[int],
) -> MOSPSolution:
    """Convert a pathwidth solution back to a MOSP solution.

    Args:
        pw_problem: The pathwidth problem that was solved.
        pathwidth: The computed pathwidth of the agreement graph.
        ordering: The linear ordering (vertex layout) achieving this pathwidth.

    Returns:
        A MOSPSolution with the production sequence and optimal value.
    """
    return MOSPSolution(
        ordering=ordering,
        max_open_stacks=pathwidth + 1,
        pathwidth=pathwidth,
        agreement_graph=pw_problem.graph,
    )
