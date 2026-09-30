"""Phase 1: the graph adapter agrees with the definitions."""
import itertools

import networkx as nx
import pytest

from pathwidth.graph import (
    boundary_sequence,
    layout_from_order,
    masks_from_graph,
    path_decomposition,
    search_cost,
    vertex_separation,
    vertex_separation_masks,
)


def textbook_vs(G, layout):
    """`max_i |{u in layout[:i] : some neighbour in layout[i:]}|`."""
    best = 0
    for i in range(1, len(layout)):
        left, right = set(layout[:i]), set(layout[i:])
        best = max(best, sum(1 for u in left if any(w in right for w in G.adj[u])))
    return best


SMALL = [
    nx.path_graph(5), nx.cycle_graph(6), nx.complete_graph(4), nx.star_graph(4),
    nx.grid_2d_graph(2, 3), nx.petersen_graph(), nx.empty_graph(3),
    nx.complete_bipartite_graph(2, 3),
]


@pytest.mark.parametrize("G", SMALL, ids=lambda G: f"n{G.number_of_nodes()}m{G.number_of_edges()}")
def test_masks_are_closed_neighbourhoods(G):
    masks, labels = masks_from_graph(G)
    index = {v: i for i, v in enumerate(labels)}
    for v in G.nodes:
        expected = {index[v]} | {index[u] for u in G.adj[v]}
        got = {i for i in range(len(labels)) if masks[index[v]] >> i & 1}
        assert got == expected


def test_self_loops_are_ignored_and_multigraphs_rejected():
    G = nx.path_graph(3)
    G.add_edge(1, 1)
    masks, _ = masks_from_graph(G)
    assert masks == [0b011, 0b111, 0b110]
    with pytest.raises(TypeError):
        masks_from_graph(nx.MultiGraph(G))
    with pytest.raises(TypeError):
        masks_from_graph(nx.DiGraph(nx.path_graph(3)))


@pytest.mark.parametrize("G", SMALL, ids=lambda G: f"n{G.number_of_nodes()}m{G.number_of_edges()}")
def test_prefix_boundary_measure_is_textbook_vs_of_the_reversed_layout(G):
    nodes = list(G.nodes)
    import random
    rng = random.Random(1)
    for _ in range(20):
        order = nodes[:]
        rng.shuffle(order)
        assert vertex_separation(G, order) == textbook_vs(G, layout_from_order(order))


@pytest.mark.parametrize("G", SMALL, ids=lambda G: f"n{G.number_of_nodes()}m{G.number_of_edges()}")
def test_search_cost_is_vertex_separation_plus_one(G):
    masks, labels = masks_from_graph(G)
    n = len(labels)
    if n == 0:
        return
    import random
    rng = random.Random(2)
    for _ in range(20):
        order = list(range(n))
        rng.shuffle(order)
        assert search_cost(masks, order) == vertex_separation_masks(masks, order) + 1
        assert max(boundary_sequence(masks, order)) == vertex_separation_masks(masks, order)


@pytest.mark.parametrize("G", SMALL, ids=lambda G: f"n{G.number_of_nodes()}m{G.number_of_edges()}")
def test_path_decomposition_is_valid_and_has_the_order_width(G):
    nodes = list(G.nodes)
    for order in itertools.islice(itertools.permutations(nodes), 5):
        bags = path_decomposition(G, order)
        # every vertex and edge covered
        assert set().union(*bags) == set(nodes) if bags else not nodes
        for u, v in G.edges:
            assert any(u in bag and v in bag for bag in bags)
        # contiguity
        for v in nodes:
            where = [i for i, bag in enumerate(bags) if v in bag]
            assert where == list(range(where[0], where[-1] + 1))
        width = max(len(bag) for bag in bags) - 1 if bags else -1
        assert width == vertex_separation(G, order)
