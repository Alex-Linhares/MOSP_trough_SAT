"""Reduction between MOSP and pathwidth of the *agreement graph* (patterns as vertices).

**Not a theorem.** `pathwidth(agreement graph) + 1` is neither an upper nor a
lower bound on the optimum in general: one pattern shared by four customers
with private patterns has optimum 4 and an agreement graph of pathwidth 1
(a star), while one customer requiring m + 1 patterns has optimum 1 and a
complete agreement graph of pathwidth m. On the benchmark corpus it happens
to undercount (`CLAUDE.md`). The equality `optimum = pathwidth + 1` holds for
the *MOSP graph* — customers as vertices, a clique per pattern — and is
proved in `lean/MOSPFormalization/MOSPGraph.lean` (2026-09-27); see
`customer_inter/reduction.py`. This module is kept for the measurements that
used it.

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
