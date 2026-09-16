"""Tests for the SAT-based pathwidth solver."""

import networkx as nx
import pytest

from satisfiability.solver import compute_pathwidth_sat
from fixed_parameter_algorithm.pathwidth import (
    compute_pathwidth,
    compute_vertex_separation,
)


# --- Mirror all tests from test_pathwidth_fpt.py ---


def test_single_vertex():
    G = nx.Graph()
    G.add_node(0)
    pw, ordering = compute_pathwidth_sat(G)
    assert pw == 0
    assert ordering == [0]


def test_empty_graph():
    G = nx.Graph()
    pw, ordering = compute_pathwidth_sat(G)
    assert pw == 0
    assert ordering == []


def test_path_graph():
    """Pathwidth of a path P_n is 1."""
    G = nx.path_graph(5)
    pw, ordering = compute_pathwidth_sat(G)
    assert pw == 1
    assert len(ordering) == 5


def test_cycle_graph():
    """Pathwidth of a cycle C_n (n >= 3) is 2."""
    G = nx.cycle_graph(5)
    pw, ordering = compute_pathwidth_sat(G)
    assert pw == 2
    assert len(ordering) == 5


def test_complete_graph_k4():
    """Pathwidth of K_n is n-1."""
    G = nx.complete_graph(4)
    pw, ordering = compute_pathwidth_sat(G)
    assert pw == 3
    assert len(ordering) == 4


def test_complete_graph_k3():
    G = nx.complete_graph(3)
    pw, ordering = compute_pathwidth_sat(G)
    assert pw == 2


def test_star_graph():
    """Pathwidth of a star K_{1,n} is 1 for n >= 1."""
    G = nx.star_graph(4)  # 5 vertices: center 0, leaves 1-4
    pw, ordering = compute_pathwidth_sat(G)
    assert pw == 1


def test_two_components():
    """Pathwidth of a disconnected graph is the max pathwidth of its components."""
    G = nx.Graph()
    G.add_edges_from([(0, 1), (1, 2)])  # path of length 2, pw=1
    G.add_edges_from([(3, 4), (4, 5), (5, 3)])  # triangle, pw=2
    pw, ordering = compute_pathwidth_sat(G)
    assert pw == 2
    assert len(ordering) == 6


def test_vertex_separation_matches_pathwidth():
    """The ordering returned should achieve the claimed pathwidth."""
    G = nx.petersen_graph()
    pw, ordering = compute_pathwidth_sat(G)
    vs = compute_vertex_separation(G, ordering)
    assert vs == pw


def test_petersen_graph():
    """Pathwidth of the Petersen graph is 5."""
    G = nx.petersen_graph()
    pw, ordering = compute_pathwidth_sat(G)
    assert pw == 5
    assert len(ordering) == 10


# --- Large graph tests (beyond n=18 exact DP limit) ---


def test_large_path_graph():
    """Pathwidth of P_50 is 1. Should complete quickly via preprocessing."""
    G = nx.path_graph(50)
    pw, ordering = compute_pathwidth_sat(G)
    assert pw == 1
    assert len(ordering) == 50
    vs = compute_vertex_separation(G, ordering)
    assert vs == 1


def test_large_star_graph():
    """Pathwidth of a star with 50 leaves is 1."""
    G = nx.star_graph(49)  # 50 vertices: center 0, leaves 1-49
    pw, ordering = compute_pathwidth_sat(G)
    assert pw == 1
    assert len(ordering) == 50


def test_large_path_100():
    """Pathwidth of P_100 is 1. Preprocessing handles this without SAT."""
    G = nx.path_graph(100)
    pw, ordering = compute_pathwidth_sat(G)
    assert pw == 1
    assert len(ordering) == 100
    vs = compute_vertex_separation(G, ordering)
    assert vs == 1


def test_grid_graph_2xn():
    """Pathwidth of a 2xn grid is 2."""
    G = nx.grid_2d_graph(2, 10)
    pw, ordering = compute_pathwidth_sat(G)
    assert pw == 2
    assert len(ordering) == 20


def test_grid_graph_3xn():
    """Pathwidth of a 3xn grid is 3 for n >= 3."""
    G = nx.grid_2d_graph(3, 10)
    pw, ordering = compute_pathwidth_sat(G)
    assert pw == 3
    assert len(ordering) == 30
    vs = compute_vertex_separation(G, ordering)
    assert vs == pw


def test_caterpillar_graph():
    """Pathwidth of a caterpillar is 1."""
    G = nx.path_graph(5)
    node_id = 5
    for v in range(5):
        for _ in range(3):
            G.add_edge(v, node_id)
            node_id += 1
    pw, ordering = compute_pathwidth_sat(G)
    assert pw == 1
    assert len(ordering) == 20


def test_binary_tree():
    """A complete binary tree of depth d has pathwidth d."""
    G = nx.balanced_tree(2, 3)  # binary tree, depth 3
    pw, ordering = compute_pathwidth_sat(G)
    assert pw == 2
    vs = compute_vertex_separation(G, ordering)
    assert vs == pw


# --- Cross-validation against exact DP ---


def test_cross_validate_small_random():
    """For small random graphs, SAT result should match exact DP."""
    import random
    rng = random.Random(42)

    for _ in range(10):
        n = rng.randint(4, 15)
        p = rng.uniform(0.2, 0.5)
        G = nx.gnp_random_graph(n, p, seed=rng.randint(0, 10000))

        if G.number_of_edges() == 0:
            continue

        pw_exact, _ = compute_pathwidth(G)
        pw_sat, ordering_sat = compute_pathwidth_sat(G)

        assert pw_sat == pw_exact, (
            f"Mismatch on n={n}: exact={pw_exact}, sat={pw_sat}"
        )
        vs = compute_vertex_separation(G, ordering_sat)
        assert vs == pw_sat


def test_cross_validate_small_dense():
    """Cross-validate on small denser graphs."""
    import random
    rng = random.Random(123)

    for _ in range(5):
        n = rng.randint(5, 12)
        p = rng.uniform(0.4, 0.7)
        G = nx.gnp_random_graph(n, p, seed=rng.randint(0, 10000))

        pw_exact, _ = compute_pathwidth(G)
        pw_sat, ordering_sat = compute_pathwidth_sat(G)

        assert pw_sat == pw_exact
        vs = compute_vertex_separation(G, ordering_sat)
        assert vs == pw_sat


# --- Edge cases ---


def test_isolated_vertices():
    """Graph with only isolated vertices has pathwidth 0."""
    G = nx.Graph()
    G.add_nodes_from(range(30))
    pw, ordering = compute_pathwidth_sat(G)
    assert pw == 0
    assert len(ordering) == 30


def test_single_edge_large():
    """Graph with one edge and many isolated vertices."""
    G = nx.Graph()
    G.add_nodes_from(range(30))
    G.add_edge(0, 1)
    pw, ordering = compute_pathwidth_sat(G)
    assert pw == 1
    assert len(ordering) == 30


def test_max_width_parameter():
    """The max_width parameter should limit the search."""
    G = nx.complete_graph(5)
    # K5 has pathwidth 4; if we set max_width=4, should still find it
    pw, ordering = compute_pathwidth_sat(G, max_width=4)
    assert pw == 4


def test_ordering_is_valid_permutation():
    """The returned ordering should be a valid permutation of all vertices."""
    G = nx.petersen_graph()
    pw, ordering = compute_pathwidth_sat(G)
    assert set(ordering) == set(G.nodes())
    assert len(ordering) == len(set(ordering))


# --- SAT-specific tests ---


def test_sat_on_medium_cycle():
    """Cycle with 25 vertices — exercises the SAT path (n > 18, core > 18)."""
    G = nx.cycle_graph(25)
    pw, ordering = compute_pathwidth_sat(G)
    assert pw == 2
    assert len(ordering) == 25
    vs = compute_vertex_separation(G, ordering)
    assert vs == pw


def test_sat_on_medium_grid():
    """4x5 grid — 20 vertices after preprocessing, exercises SAT solver."""
    G = nx.grid_2d_graph(4, 5)
    pw, ordering = compute_pathwidth_sat(G)
    assert pw == 4
    assert len(ordering) == 20
    vs = compute_vertex_separation(G, ordering)
    assert vs == pw


def test_sat_cross_validate_medium():
    """Cross-validate SAT vs FPT on graphs in the 19-25 vertex range."""
    from fixed_parameter_algorithm.pathwidth_fpt import compute_pathwidth_fpt
    import random
    rng = random.Random(99)

    for _ in range(3):
        n = rng.randint(19, 22)
        p = rng.uniform(0.15, 0.3)
        G = nx.gnp_random_graph(n, p, seed=rng.randint(0, 10000))

        if G.number_of_edges() == 0:
            continue

        pw_fpt, _ = compute_pathwidth_fpt(G)
        pw_sat, ordering_sat = compute_pathwidth_sat(G)

        assert pw_sat == pw_fpt, (
            f"Mismatch on n={n}: fpt={pw_fpt}, sat={pw_sat}"
        )
        vs = compute_vertex_separation(G, ordering_sat)
        assert vs == pw_sat
