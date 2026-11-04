"""loop0014 item 04: the structural claims of `reports/subexp_pathwidth.md` §4
(cobipartite normal form, split dichotomy, twin lemma) against brute force on
small graphs (the full atlas run is `python -m learning.subexp_classes`)."""
import random

from learning import subexp_classes as sc
from learning.subexp_reductions import atlas, vs
from paper1.complex_check import graph


def _graphs(nmax):
    return atlas(nmax)


def test_cobipartite_normal_form_matches_vs_on_every_partition():
    for g in _graphs(5):
        v = vs(g)
        for A, B in sc.cobipartitions(g):
            assert sc.cobipartite_normal_form(g, A, B) == v


def test_some_optimal_layout_places_one_clique_first():
    for g in _graphs(5):
        v = vs(g)
        for A, B in sc.cobipartitions(g):
            assert min(sc.one_side_first_layout_value(g, A, B),
                       sc.one_side_first_layout_value(g, B, A)) == v


def test_corollary_4_2_decision_on_every_partition_and_k():
    for g in _graphs(5):
        v = vs(g)
        for A, B in sc.cobipartitions(g):
            for k in range(g[0] + 1):
                assert sc.cobipartite_decision(g, A, B, k) == (v <= k)


def test_cobipartite_patterns_to_six_vertices():
    for a in range(1, 4):
        for b in range(a, 7 - a):
            for g, A, B in sc.bipartite_patterns(a, b):
                assert sc.cobipartite_normal_form(g, A, B) == vs(g)


def test_split_dichotomy_and_criterion_on_every_partition():
    for g in _graphs(5):
        v = vs(g)
        for K, I in sc.split_partitions(g):
            kappa = sc.popcount(K)
            assert v in (kappa - 1, kappa)
            assert sc.split_formula(g, K, I) == v


def test_split_criterion_on_random_split_graphs():
    rng = random.Random(1)
    for _ in range(60):
        g, K, I = sc.random_split_graph(10, rng)
        assert sc.split_formula(g, K, I) == vs(g)


def test_split_criterion_examples():
    # K_3 plus a pendant on each clique vertex: v's single independent
    # neighbour misses the other two clique vertices, so vs = kappa - 1 = 2.
    g = graph(6, [(0, 1), (1, 2), (0, 2), (0, 3), (1, 4), (2, 5)])
    assert sc.split_formula(g, 0b111, 0b111000) == 2 == vs(g)
    # K_3 plus three independent vertices, one on each pair of clique
    # vertices: every clique vertex's independent neighbours together hit all
    # of K, so vs = kappa = 3 (the graph is the 3-sun).
    g = graph(6, [(0, 1), (1, 2), (0, 2), (0, 3), (1, 3), (1, 4), (2, 4), (0, 5), (2, 5)])
    assert sc.split_formula(g, 0b111, 0b111000) == 3 == vs(g)
    # The same with one independent vertex removed: vertex 2's independent
    # neighbours are {4} (hitting 1, 2), which miss 0, so vs = 2.
    g = graph(5, [(0, 1), (1, 2), (0, 2), (0, 3), (1, 3), (1, 4), (2, 4)])
    assert sc.split_formula(g, 0b111, 0b11000) == 2 == vs(g)


def test_twin_unit_dp_and_consecutive_layouts():
    for g in _graphs(5):
        v = vs(g)
        d, u = sc.twin_unit_dp(g)
        assert d == v
        assert u <= g[0]
        assert sc.consecutive_twin_layout_value(g) == v


def test_twin_classes_partition_the_vertices():
    for g in _graphs(5):
        classes = sc.twin_classes(g)
        assert sum(classes) == (1 << g[0]) - 1
        for c in classes:
            assert sc.is_clique(g, c) or sc.is_independent(g, c)


def test_orientation_does_not_determine_the_value():
    # Two disjoint edges: oriented, the interleaved and the block-wise
    # linear extensions have values 2 and 1.
    g = graph(4, [(0, 1), (2, 3)])
    r = sc.orientation_spread(g)
    assert r["disagreeing"] > 0 and r["max_spread"] == 1
