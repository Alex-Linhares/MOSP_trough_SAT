"""Phase 2: the ported search decides pathwidth correctly."""
import itertools

import networkx as nx
import pytest

import pathwidth as pw
from pathwidth.graph import masks_from_graph, vertex_separation_masks
from pathwidth.search import decide, decide_pathwidth


def brute_force_pathwidth(G):
    masks, labels = masks_from_graph(G)
    n = len(labels)
    if n == 0:
        return -1
    return min(vertex_separation_masks(masks, order) for order in itertools.permutations(range(n)))


KNOWN = [
    ("path_10", nx.path_graph(10), 1),
    ("cycle_7", nx.cycle_graph(7), 2),
    ("K6", nx.complete_graph(6), 5),
    ("K_3_3", nx.complete_bipartite_graph(3, 3), 3),
    ("grid_3x3", nx.grid_2d_graph(3, 3), 3),
    ("grid_4x4", nx.grid_2d_graph(4, 4), 4),
    ("petersen", nx.petersen_graph(), 5),
    ("mycielski_4", nx.mycielski_graph(4), 5),   # Coudert et al. Table 1: M4 (11 vertices) pw 5
    ("empty_4", nx.empty_graph(4), 0),
    ("two_triangles", nx.disjoint_union(nx.complete_graph(3), nx.complete_graph(3)), 2),
    ("binary_tree_d3", nx.balanced_tree(2, 3), 2),
]


@pytest.mark.parametrize("name,G,expected", KNOWN, ids=[k[0] for k in KNOWN])
def test_known_pathwidths(name, G, expected):
    width, order = pw.compute_pathwidth(G)
    assert width == expected
    assert sorted(order, key=str) == sorted(G.nodes, key=str)
    assert pw.vertex_separation(G, order) == width


def test_every_graph_on_at_most_six_vertices_matches_brute_force():
    checked = 0
    for G in nx.graph_atlas_g():
        if G.number_of_nodes() > 6:
            break
        width, order = pw.compute_pathwidth(G)
        assert width == brute_force_pathwidth(G), nx.to_graph6_bytes(G)
        if order:
            assert pw.vertex_separation(G, order) == width
        checked += 1
    assert checked >= 150


FLAG_SETS = [
    dict(),
    dict(old_move=False),                      # memo on, old move off
    dict(old_move=False, memo=False),
    dict(subset_rule=False),
    dict(definite_move=False),
    dict(subset_rule=False, definite_move=False, old_move=False, memo=False),
    dict(expansion_prune=True),
    dict(expansion_prune=True, old_move=False),
    dict(fan_order="degree"),
]


@pytest.mark.parametrize("flags", FLAG_SETS, ids=lambda f: ",".join(f"{k}={v}" for k, v in f.items()) or "default")
def test_every_flag_combination_gives_the_same_width(flags):
    import random
    rng = random.Random(7)
    for _ in range(25):
        n = rng.randint(4, 9)
        G = nx.gnp_random_graph(n, rng.uniform(0.2, 0.7), seed=rng.randint(0, 10**6))
        width, order = pw.compute_pathwidth(G, **flags)
        assert width == brute_force_pathwidth(G)
        assert pw.vertex_separation(G, order) == width


def test_restricted_search_never_refutes():
    G = nx.petersen_graph()
    for w in range(0, 5):
        answer = decide_pathwidth(G, w, restrict=True)
        assert answer.status in ("sat", "unknown")
        assert answer.status != "unsat"


def test_a_node_budget_returns_unknown_not_unsat():
    G = nx.mycielski_graph(5)   # 23 vertices, pw 10
    answer = decide_pathwidth(G, 8, max_nodes=50)
    assert answer.status == "unknown"
    assert answer.nodes == 51


def test_inactive_vertices_and_empty_inputs():
    assert decide([], 0) == pw.Decision("sat", [], 0)
    assert decide([0, 0], 0).status == "sat"          # two inactive vertices
    assert decide_pathwidth(nx.Graph(), 0).status == "sat"
    assert decide_pathwidth(nx.path_graph(2), -1).status == "unsat"
    assert pw.compute_pathwidth(nx.Graph()) == (-1, [])


def test_labels_survive_the_round_trip():
    G = nx.relabel_nodes(nx.path_graph(4), {0: "a", 1: "b", 2: "c", 3: "d"})
    width, order = pw.compute_pathwidth(G)
    assert width == 1 and set(order) == {"a", "b", "c", "d"}


def test_deep_recursion_on_a_large_graph_is_handled():
    # 1500 vertices: the Python path (the C declines above 128) recurses once per vertex.
    G = nx.path_graph(1500)
    masks, _ = masks_from_graph(G)
    assert decide(masks, 2, native=False).status == "sat"       # pw <= 1
    assert pw.solve(nx.cycle_graph(1200)).width == 2
