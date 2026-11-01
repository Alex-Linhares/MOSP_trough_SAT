"""loop0010 item 03: the block-graph families, their invariants and the
candidate formulas, on hand-checkable cases; the C program on tiny graphs."""

import networkx as nx
import pytest

from learning.block_trees import (CANDIDATES, PATHWIDTH_BIN, block_height, candidates, caterpillar_of_cliques,
                                  clique_tree, ct_size, graph6, incidence_graph, is_incidence_forest,
                                  largest_pattern, matrix_of, mosp_graph, n_customers, pattern_adjacency,
                                  random_block_tree, run_pathwidth, ternary_subtree_height, tree_bound, vertex_separation)


def test_ct_size_matches_construction():
    for s in (2, 3, 4, 5):
        for h in (0, 1, 2, 3):
            for b in (1, 2, 3):
                if ct_size(s, h, b) > 500:
                    continue
                patterns, depth = clique_tree(s, h, b)
                assert n_customers(patterns) == ct_size(s, h, b) == len(depth)
                assert len(patterns) == 1 + (ct_size(s, h, b) - s) // (s - 1)
                assert max(depth) == h


def test_ct_2_h_3_is_two_ternary_trees_joined_at_their_roots():
    patterns, depth = clique_tree(2, 2, 3)
    g = mosp_graph(patterns)
    assert nx.is_tree(g)
    # the root pair has degree 4 (each other plus three children); every other internal vertex degree 4 as well
    assert sorted(d for _, d in g.degree) == [1] * 18 + [4] * 8
    g.remove_edge(0, 1)
    halves = list(nx.connected_components(g))
    assert len(halves) == 2 and all(len(c) == 13 for c in halves)      # a complete ternary tree of height 2


def test_ct_is_a_block_graph_with_a_forest_incidence():
    for s, h, b in [(2, 3, 2), (3, 2, 1), (4, 1, 3), (5, 1, 2)]:
        patterns, _ = clique_tree(s, h, b)
        assert is_incidence_forest(patterns)
        assert nx.is_connected(incidence_graph(patterns))
        assert largest_pattern(patterns) == s and all(len(p) == s for p in patterns)
        assert block_height(patterns) == h
        # patterns at one hub are pairwise adjacent, so the pattern adjacency graph is a tree only for b = 1
        assert nx.is_connected(pattern_adjacency(patterns))
        assert nx.is_tree(pattern_adjacency(patterns)) == (b == 1)


def test_caterpillar_of_cliques_by_hand():
    # three triangles in a chain: shared customers 2 and 4; non-shared 0, 1, 3, 5, 6 get a pendant triangle each
    patterns = caterpillar_of_cliques(3, 3)
    assert patterns[:3] == [[0, 1, 2], [2, 3, 4], [4, 5, 6]]
    assert len(patterns) == 3 + 5 and all(len(p) == 3 for p in patterns)
    assert sorted(p[0] for p in patterns[3:]) == [0, 1, 3, 5, 6]
    assert is_incidence_forest(patterns) and n_customers(patterns) == 7 + 10
    assert block_height(patterns) == 2
    assert matrix_of(patterns).sum() == 8 * 3


def test_random_block_tree_is_a_forest_on_exactly_n_customers_and_regenerates():
    for d in (2, 3, 4):
        for seed in range(5):
            patterns = random_block_tree(37, d, seed)
            assert n_customers(patterns) == 37
            assert is_incidence_forest(patterns) and nx.is_connected(incidence_graph(patterns))
            assert min(map(len, patterns)) >= 2
            assert patterns == random_block_tree(37, d, seed)


def test_tree_bound_thresholds():
    # treeBound k = 1, 6, 21, 66: the largest N with tb(N) = k
    assert [tree_bound(N) for N in (0, 1, 2, 6, 7, 21, 22, 66, 67)] == [0, 0, 1, 1, 2, 2, 3, 3, 4]


def test_candidates_on_a_single_clique():
    # one K_4: B is a star (pathwidth 1), h = 0, n + m = 5
    c = candidates(omega=4, pw_b=1, h=0, n_plus_m=5)
    assert set(c) == set(CANDIDATES)
    assert c["omega-1"] == 3 and c["omega-1+pw(B)"] == 4 and c["omega-2+pw(B)"] == 3
    assert c["omega-1+h"] == 3 and c["omega(pw(B)+1)-1"] == 7 and c["omega(tb+1)-1"] == 4 * 2 - 1


def test_vertex_separation_by_hand():
    p4 = nx.path_graph(4)
    assert vertex_separation(p4, [0, 1, 2, 3]) == 1
    assert vertex_separation(p4, [0, 2, 1, 3]) == 2
    with pytest.raises(ValueError):
        vertex_separation(p4, [0, 1, 2])


@pytest.mark.skipif(not PATHWIDTH_BIN.exists(), reason="the C pathwidth program is not built")
def test_c_program_on_tiny_graphs():
    graphs = [nx.path_graph(5), nx.complete_graph(4), nx.balanced_tree(3, 2), nx.star_graph(6)]
    results = run_pathwidth([graph6(g) for g in graphs], timeout=30, workers=2)
    assert [r["width"] for r in results] == [1, 3, 2, 1]
    assert all(r["status"] in ("refutation", "bound", "minor") for r in results)
    for g, r in zip(graphs, results):
        assert vertex_separation(g, r["layout"]) == r["width"]


def test_ternary_subtree_height():
    assert ternary_subtree_height(nx.balanced_tree(3, 3)) == 3
    assert ternary_subtree_height(nx.balanced_tree(2, 4)) == 1      # an interior vertex has three neighbours, no more
    assert ternary_subtree_height(nx.star_graph(3)) == 1
    assert ternary_subtree_height(nx.path_graph(9)) == 0
    # the incidence tree of CT(4, 2, 3): every internal vertex has at least three children from the root pattern, five levels
    assert ternary_subtree_height(incidence_graph(clique_tree(4, 2, 3)[0])) == 5
    with pytest.raises(ValueError):
        ternary_subtree_height(nx.cycle_graph(4))
