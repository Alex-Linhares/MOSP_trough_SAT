"""loop0010 item 03: the node search number of block graphs by Chou, Ko, Ho & Chen's Theorem 4
(`learning/chou_block.py`), on hand-checkable graphs and against the C program on small random block trees."""

import networkx as nx
import pytest

from learning.block_trees import PATHWIDTH_BIN, clique_tree, graph6, mosp_graph, random_block_tree, run_pathwidth
from learning.chou_block import is_block_graph, node_search_number, pathwidth_block_graph


def test_is_block_graph():
    assert is_block_graph(nx.complete_graph(5))
    assert is_block_graph(nx.path_graph(6))
    assert is_block_graph(mosp_graph(clique_tree(3, 2, 2)[0]))
    assert not is_block_graph(nx.cycle_graph(4))
    with pytest.raises(ValueError):
        node_search_number(nx.cycle_graph(5))


def test_hand_values():
    assert node_search_number(nx.empty_graph(1)) == 1
    assert pathwidth_block_graph(nx.complete_graph(4)) == 3
    assert pathwidth_block_graph(nx.path_graph(7)) == 1
    assert pathwidth_block_graph(nx.star_graph(5)) == 1
    assert pathwidth_block_graph(nx.balanced_tree(3, 2)) == 2          # complete ternary tree of height 2
    assert pathwidth_block_graph(nx.balanced_tree(2, 3)) == 2          # complete binary tree of height 3
    # a triangle with a pendant triangle at each corner: the three pendant bags cannot all sit next to the centre
    assert pathwidth_block_graph(mosp_graph(clique_tree(3, 1, 1)[0])) == 3
    # K_5 with a pendant K_5 at each vertex: ceil(3 * 5 / 2) - 2 = 6, not 5
    assert pathwidth_block_graph(mosp_graph(clique_tree(5, 1, 1)[0])) == 6
    # K_4 with a pendant edge at every vertex keeps pathwidth 3
    g = nx.complete_graph(4)
    g.add_edges_from([(0, 4), (1, 5), (2, 6), (3, 7)])
    assert pathwidth_block_graph(g) == 3


def test_disconnected_is_the_maximum():
    g = nx.disjoint_union(nx.complete_graph(3), nx.path_graph(4))
    assert pathwidth_block_graph(g) == 2


@pytest.mark.skipif(not PATHWIDTH_BIN.exists(), reason="the C pathwidth program is not built")
def test_agrees_with_the_c_program_on_small_random_block_trees():
    graphs = [mosp_graph(random_block_tree(n, d, 500 + 10 * n + d)) for n in (8, 12, 16) for d in (2, 3, 4)]
    c = [r["width"] for r in run_pathwidth([graph6(g) for g in graphs], timeout=30, workers=2)]
    assert c == [pathwidth_block_graph(g) for g in graphs]
