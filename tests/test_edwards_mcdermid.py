"""loop0012 item 01: `learning.edwards_mcdermid` — the weights `g_{1/6}`, `g'`,
the series-parallel reduction on bit masks, and the terms of Edwards &
McDermid (2015) Corollary 5.2 and Theorem 5.3. The paper's table (p. 7) to
`d = 8` exactly; properties 3, 4, 6 and the closed form (Lemma 8.1) to
`n = 30`; `reduce` on a tree, a cycle, `K_4`, a subdivided `K_4`; no degree
rises under reduction and `main_term ≤ histogram_term` on 200 random graphs.
"""
from __future__ import annotations

import random
from fractions import Fraction as F

import networkx as nx
import pytest

from learning.edwards_mcdermid import (
    alternating_factorial, average_degree, average_degree_term, components, degrees,
    edge_count, fminus, fomin_hoie_budget, fomin_hoie_n_eps, from_edges, from_networkx,
    g, g_closed_form, g_prime, g_real, histogram_term, is_cubic, is_reduced, main_term,
    poisson_value, reduce,
)

PAPER_TABLE = {2: F(0), 3: F(1, 6), 4: F(1, 3), 5: F(13, 30), 6: F(23, 45),
               7: F(359, 630), 8: F(1553, 2520)}


def test_table_matches_the_paper_to_d8():
    for d, val in PAPER_TABLE.items():
        assert g(d) == val
    assert g(0) == g(1) == g(2) == 0


def test_recurrence_and_alternating_factorial():
    for n in range(4, 31):
        assert n * g(n) == (n - 2) * g(n - 1) + g(n - 2) + 1
    assert [alternating_factorial(k) for k in range(1, 6)] == [1, 1, 5, 19, 101]
    for n in range(2, 31):
        assert alternating_factorial(n) + alternating_factorial(n - 1) == __import__("math").factorial(n)


def test_closed_form_lemma_8_1_to_30():
    for n in range(2, 31):
        assert g_closed_form(n) == g(n)


def test_property_3_non_decreasing_to_30():
    for n in range(2, 31):
        assert g(n + 1) >= g(n)


def test_property_4_increments_non_increasing_to_30():
    assert g_prime(3) == g_prime(4) == F(1, 6)
    for n in range(3, 31):
        assert g_prime(n + 1) <= g_prime(n)
    for n in range(0, 3):
        assert g_prime(n) == 0


def test_property_5_g_over_n_decreasing_from_5():
    for n in range(5, 31):
        assert g(n + 1) / (n + 1) < g(n) / n


def test_property_6_rearrangement_to_30():
    for n in range(4, 31):
        assert 1 - g(n) == (n - 1) * g_prime(n) + g_prime(n - 1)


def test_g_real_interpolates_and_is_zero_below_2():
    assert g_real(F(7, 2)) == (g(3) + g(4)) / 2
    assert g_real(F(3)) == g(3)
    assert g_real(F(1, 2)) == 0 and g_real(2) == 0
    assert g_real(F(5, 2)) == g(3) / 2


def test_g_sandwich_of_lemma_8_3_and_8_4():
    for n in range(3, 31):
        assert g(n - 1) <= g(n) <= (1 + g(n - 1)) / 2
    for n in range(4, 31):
        assert g_prime(n - 1) >= g_prime(n) >= g_prime(n - 1) / 3


def test_reduce_tree_is_empty():
    T = nx.random_labeled_tree(40, seed=1) if hasattr(nx, "random_labeled_tree") else nx.random_tree(40, seed=1)
    adj = from_networkx(T)
    radj, removed = reduce(adj)
    assert removed == (1 << 40) - 1
    assert all(a == 0 for a in radj)
    assert main_term(adj) == 0


def test_reduce_cycle_leaves_a_triangle_then_empties():
    # operation 3 shrinks a cycle until three vertices remain; then operation 4
    # deletes one of them (adjacent neighbours), and the remaining edge goes by
    # operation 2 and 1: the cycle is series-parallel, r(C_n) is empty.
    adj = from_networkx(nx.cycle_graph(9))
    radj, removed = reduce(adj)
    assert all(a == 0 for a in radj) and removed == (1 << 9) - 1


def test_reduce_k4_is_fixed():
    adj = from_networkx(nx.complete_graph(4))
    radj, removed = reduce(adj)
    assert radj == adj and removed == 0
    assert main_term(adj) == 4 * g(3) == F(2, 3)
    assert fminus(adj) == F(2, 3) - g_prime(3) == F(1, 2)


def test_reduce_subdivided_k4_returns_to_k4():
    K = nx.complete_graph(4)
    S = nx.Graph()
    nxt = 4
    for a, b in K.edges():
        # subdivide every edge twice
        S.add_edge(a, nxt); S.add_edge(nxt, nxt + 1); S.add_edge(nxt + 1, b); nxt += 2
    adj = from_networkx(S)
    radj, removed = reduce(adj)
    surviving = [v for v in range(len(adj)) if not (removed >> v) & 1]
    assert sorted(surviving) == [0, 1, 2, 3]
    for v in range(4):
        assert radj[v] == (0b1111 & ~(1 << v))
    assert main_term(adj) == F(2, 3)
    # the unreduced histogram sum sees only the four branch vertices too
    assert histogram_term(adj) == F(2, 3)


def test_reduce_pendant_on_k4_and_triangle_hanging():
    G = nx.complete_graph(4)
    G.add_edge(0, 4); G.add_edge(4, 5); G.add_edge(5, 0)   # a triangle hanging on vertex 0
    G.add_edge(1, 6)                                        # a pendant
    adj = from_networkx(G)
    radj, removed = reduce(adj)
    assert removed == (1 << 4) | (1 << 5) | (1 << 6)
    assert is_reduced(radj) and is_cubic(radj, 0b1111)


def _random_graphs(count: int = 200, seed: int = 7):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        n = rng.randint(5, 40)
        p = rng.choice([0.05, 0.1, 0.2, 0.35, 0.5])
        G = nx.gnp_random_graph(n, p, seed=rng.randint(0, 10 ** 9))
        out.append(from_networkx(G))
    return out


def test_reduce_never_raises_a_surviving_degree_and_is_reduced():
    for adj in _random_graphs():
        radj, removed = reduce(adj)
        assert is_reduced(radj)
        d0, d1 = degrees(adj), degrees(radj)
        for v in range(len(adj)):
            if (removed >> v) & 1:
                assert radj[v] == 0
            else:
                assert d1[v] <= d0[v]
                assert d1[v] >= 3
        # the reduced graph has no edge to a removed vertex
        for v in range(len(adj)):
            assert radj[v] & removed == 0


def test_main_term_at_most_histogram_term():
    for adj in _random_graphs():
        assert main_term(adj) <= histogram_term(adj)


def test_reduce_is_idempotent_and_order_independent():
    for adj in _random_graphs(60, seed=3):
        radj, removed = reduce(adj)
        radj2, removed2 = reduce(radj)
        assert radj2 == radj and removed2 == removed
        # relabel, reduce, relabel back: the same reduced graph (uniqueness, paper p. 8)
        n = len(adj)
        perm = list(range(n)); random.Random(n).shuffle(perm)
        inv = {perm[i]: i for i in range(n)}
        padj = [0] * n
        for v in range(n):
            for u in range(n):
                if (adj[v] >> u) & 1:
                    padj[perm[v]] |= 1 << perm[u]
        pr, prem = reduce(padj)
        back = [0] * n
        for v in range(n):
            for u in range(n):
                if (pr[v] >> u) & 1:
                    back[inv[v]] |= 1 << inv[u]
        assert back == radj


def test_components_and_fminus_additive():
    G = nx.disjoint_union(nx.complete_graph(4), nx.complete_graph(5))
    G.add_node(9)
    adj = from_networkx(G)
    comps = components(adj)
    assert len(comps) == 2
    assert fminus(adj) == (4 * g(3) - g_prime(3)) + (5 * g(4) - g_prime(4))
    assert fminus(adj) == fminus(from_networkx(nx.complete_graph(4))) + fminus(from_networkx(nx.complete_graph(5)))


def test_average_degree_term_and_cubic_value():
    adj = from_networkx(nx.petersen_graph())
    assert average_degree(adj) == 3 and average_degree_term(adj) == 10 * g(3)
    assert is_cubic(adj)
    assert main_term(adj) == F(10, 6)
    assert edge_count(adj) == 15


def test_poisson_value_matches_the_planner_to_four_places():
    assert abs(poisson_value(3) - 0.1826) < 5e-4
    assert abs(poisson_value(6) - 0.4575) < 5e-4
    assert abs(poisson_value(10) - 0.6558) < 5e-4
    assert poisson_value(0) == 0
    # Jensen: concave g on the integers puts the Poisson mean below g(c) when c ≥ 3
    assert poisson_value(6) < float(g(6))


def test_fomin_hoie_budget_is_explicit_and_vacuous_at_our_sizes():
    assert abs(fomin_hoie_n_eps(0.5) - 55.45) < 0.01
    assert abs(fomin_hoie_n_eps(0.1) - 18604.9) < 0.1
    for n in (16, 120, 2916):
        assert fomin_hoie_budget(n) > 0.17 * n  # exceeds n/6 itself
    assert fomin_hoie_budget(100000) < fomin_hoie_budget(2916) * 100000 / 2916
