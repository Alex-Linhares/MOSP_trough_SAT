"""Tests for the pathwidth solver."""

import networkx as nx
import pytest

from fixed_parameter_algorithm.pathwidth import (
    compute_pathwidth,
    compute_vertex_separation,
)


def test_single_vertex():
    G = nx.Graph()
    G.add_node(0)
    pw, ordering = compute_pathwidth(G)
    assert pw == 0
    assert ordering == [0]


def test_empty_graph():
    G = nx.Graph()
    pw, ordering = compute_pathwidth(G)
    assert pw == 0
    assert ordering == []


def test_path_graph():
    """Pathwidth of a path P_n is 1."""
    G = nx.path_graph(5)
    pw, ordering = compute_pathwidth(G)
    assert pw == 1
    assert len(ordering) == 5


def test_cycle_graph():
    """Pathwidth of a cycle C_n (n >= 3) is 2."""
    G = nx.cycle_graph(5)
    pw, ordering = compute_pathwidth(G)
    assert pw == 2
    assert len(ordering) == 5


def test_complete_graph_k4():
    """Pathwidth of K_n is n-1."""
    G = nx.complete_graph(4)
    pw, ordering = compute_pathwidth(G)
    assert pw == 3
    assert len(ordering) == 4


def test_complete_graph_k3():
    G = nx.complete_graph(3)
    pw, ordering = compute_pathwidth(G)
    assert pw == 2


def test_star_graph():
    """Pathwidth of a star K_{1,n} is 1 for n >= 1."""
    G = nx.star_graph(4)  # 5 vertices: center 0, leaves 1-4
    pw, ordering = compute_pathwidth(G)
    assert pw == 1


def test_two_components():
    """Pathwidth of a disconnected graph is the max pathwidth of its components."""
    G = nx.Graph()
    G.add_edges_from([(0, 1), (1, 2)])  # path of length 2, pw=1
    G.add_edges_from([(3, 4), (4, 5), (5, 3)])  # triangle, pw=2
    pw, ordering = compute_pathwidth(G)
    assert pw == 2
    assert len(ordering) == 6


def test_vertex_separation_matches_pathwidth():
    """The ordering returned should achieve the claimed pathwidth."""
    G = nx.petersen_graph()
    pw, ordering = compute_pathwidth(G)
    vs = compute_vertex_separation(G, ordering)
    assert vs == pw


def test_vertex_separation_path():
    """Verify vertex separation computation on a known case."""
    G = nx.path_graph(4)  # 0-1-2-3
    vs = compute_vertex_separation(G, [0, 1, 2, 3])
    assert vs == 1
    # A bad ordering
    vs_bad = compute_vertex_separation(G, [0, 2, 1, 3])
    assert vs_bad >= 1


def test_too_large_raises():
    """Graphs with > 25 vertices should raise ValueError."""
    G = nx.path_graph(30)
    with pytest.raises(ValueError, match="25"):
        compute_pathwidth(G)


def test_petersen_graph():
    """Pathwidth of the Petersen graph is 5."""
    G = nx.petersen_graph()
    pw, ordering = compute_pathwidth(G)
    assert pw == 5
    assert len(ordering) == 10
