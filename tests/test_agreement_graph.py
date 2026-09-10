"""Tests for agreement graph construction."""

import pytest

from mosp.instance import MOSPInstance
from mosp.agreement_graph import build_agreement_graph


def test_complete_graph():
    """If every pair of patterns shares a customer, the graph is complete."""
    # All customers need all patterns → complete graph on 3 nodes
    matrix = [
        [1, 1, 1],
        [1, 1, 1],
    ]
    inst = MOSPInstance.from_matrix(matrix)
    G = build_agreement_graph(inst)
    assert G.number_of_nodes() == 3
    assert G.number_of_edges() == 3  # K3 has 3 edges


def test_independent_patterns():
    """If no two patterns share a customer, the graph has no edges."""
    # Each customer needs exactly one pattern
    matrix = [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
    ]
    inst = MOSPInstance.from_matrix(matrix)
    G = build_agreement_graph(inst)
    assert G.number_of_nodes() == 3
    assert G.number_of_edges() == 0


def test_path_graph():
    """Patterns that share customers in a chain form a path graph."""
    # Customer 0 needs patterns 0,1
    # Customer 1 needs patterns 1,2
    # → edges: 0-1, 1-2 (a path)
    matrix = [
        [1, 1, 0],
        [0, 1, 1],
    ]
    inst = MOSPInstance.from_matrix(matrix)
    G = build_agreement_graph(inst)
    assert G.number_of_nodes() == 3
    assert G.number_of_edges() == 2
    assert G.has_edge(0, 1)
    assert G.has_edge(1, 2)
    assert not G.has_edge(0, 2)


def test_single_pattern():
    """A single pattern results in a single-node graph."""
    matrix = [[1], [1], [0]]
    inst = MOSPInstance.from_matrix(matrix)
    G = build_agreement_graph(inst)
    assert G.number_of_nodes() == 1
    assert G.number_of_edges() == 0


def test_isolated_pattern():
    """A pattern needed by no customer still appears as a node."""
    matrix = [
        [1, 0, 1],
        [1, 0, 0],
    ]
    inst = MOSPInstance.from_matrix(matrix)
    G = build_agreement_graph(inst)
    assert G.number_of_nodes() == 3
    # Pattern 1 has no customers so no edges to it
    assert not G.has_edge(0, 1)
    assert not G.has_edge(1, 2)
    # Patterns 0 and 2 share customer 0
    assert G.has_edge(0, 2)
