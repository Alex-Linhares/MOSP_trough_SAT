"""loop0014 item 03: the linear reductions into vertex separation, checked
against brute force on small graphs (the full atlas run is
`python -m learning.subexp_reductions`)."""
import itertools

import pytest

from learning import subexp_reductions as sr
from paper1.complex_check import cutwidth_dp, graph, modified_cutwidth_dp, vertex_separation


def _graphs(nmax):
    return sr.atlas(nmax)


def test_subset_dp_matches_permutations():
    for g in _graphs(5):
        assert sr.vs(g) == vertex_separation(g)


def test_mosp_pattern_dp_matches_literal_definition():
    rows, cols = 3, 4
    seen = 0
    for M in sr.all_matrices(rows, cols):
        if seen >= 300 or not any(any(r) for r in M):
            continue
        seen += 1
        assert sr.mosp_subset_dp(M) == sr.mosp_permutations(M)


def test_cobipartite_double_adds_n():
    for g in _graphs(5):
        assert sr.vs(sr.cobipartite_double(g)) == sr.vs(g) + g[0]
        assert sr.is_cobipartite(sr.cobipartite_double(g))


def test_clique_blowup_multiplies_pw_plus_one():
    for g in _graphs(5):
        assert sr.vs(sr.clique_blowup(g, 2)) + 1 == 2 * (sr.vs(g) + 1)


def test_degree_clique_expansion_against_cutwidth():
    for g in _graphs(5):
        ve = sr.vs(sr.degree_clique_expansion(g))
        cw = cutwidth_dp(g)
        assert ve >= cw
        if sr.max_degree(g) <= 3:
            assert ve == cw


def test_degree_clique_expansion_exceeds_cutwidth_at_degree_four():
    star = graph(5, [(4, i) for i in range(4)])  # K_{1,4}
    assert sr.vs(sr.degree_clique_expansion(star)) == cutwidth_dp(star) + 1


def test_mosp_instance_of_graph_is_vs_plus_one():
    for g in _graphs(5):
        M = sr.mosp_instance(g)
        assert sr.mosp_subset_dp(M) == sr.vs(g) + 1


def test_lengauer_offset():
    for g in _graphs(3):
        assert sr.vs(sr.lengauer_cliques(g)) == modified_cutwidth_dp(g) + g[0]
