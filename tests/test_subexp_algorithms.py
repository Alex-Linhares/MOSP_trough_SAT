"""loop0014 item 07: the exact algorithms of `reports/subexp_pathwidth.md` §7
against brute force on small graphs (the full atlas run is
`python -m learning.subexp_algorithms`)."""
import random

from learning import subexp_algorithms as sa
from learning.subexp_classes import cobipartitions
from learning.subexp_reductions import atlas, is_cobipartite, mosp_subset_dp, vs
from paper1.complex_check import cutwidth_dp, cutwidth_of_layout, edges_of, graph, vs_of_layout


def _has_single_edge_component(g):
    n, adj = g
    return any(sa.popcount(adj[v]) == 1 and sa.popcount(adj[adj[v].bit_length() - 1]) == 1
               for v in range(n))


def test_theorem_7_1_both_inequalities_to_five_vertices():
    for g in atlas(5):
        es = edges_of(g)
        if not es:
            continue
        L, _ = sa.line_graph(g)
        c, vl = cutwidth_dp(g), vs(L)
        d = sa.max_degree(g)
        assert vl <= c + max(0, d // 2 - 1)                       # (ii), every graph
        if not _has_single_edge_component(g):
            assert c <= vl                                         # (i)
            if d <= 3:
                assert c == vl


def test_single_edge_component_is_the_only_exception_to_7_1_i():
    g = graph(2, [(0, 1)])
    assert cutwidth_dp(g) == 1 and vs(sa.line_graph(g)[0]) == 0


def test_the_layout_maps_realise_the_inequalities():
    for g in atlas(5):
        es = edges_of(g)
        if not es or _has_single_edge_component(g):
            continue
        L, _ = sa.line_graph(g)
        vl, lorder = sa.vs_layout(L)
        order = sa.vertex_layout_from_line_layout(g, es, lorder)
        assert sorted(order) == list(range(g[0]))
        assert cutwidth_of_layout(g, order) <= vl
        c = cutwidth_dp(g)
        for perm in __import__("itertools").permutations(range(g[0])):
            if cutwidth_of_layout(g, perm) == c:
                lo = sa.line_layout_from_vertex_layout(g, es, list(perm))
                assert vs_of_layout(L, lo) <= c + max(0, sa.max_degree(g) // 2 - 1)
                break


def test_algorithm_7_2_cutwidth_of_subcubic_graphs_with_witness():
    for g in atlas(6):
        if sa.max_degree(g) > 3:
            continue
        c = cutwidth_dp(g)
        v, order = sa.cutwidth_subcubic(g)
        assert v == c and sorted(order) == list(range(g[0]))
        assert cutwidth_of_layout(g, order) == c


def test_base_below_two_exactly_when_m_over_n_below_threshold():
    assert sa.base_per_vertex(1.0) < 2 < sa.base_per_vertex(1.5)
    assert abs(sa.base_per_vertex(sa.LOG_189_2) - 2) < 1e-9


def test_cobipartite_algorithm_with_witness():
    for g in atlas(5):
        if not is_cobipartite(g):
            continue
        v = vs(g)
        for A, B in cobipartitions(g):
            val, order = sa.cobipartite_vs(g, A, B)
            assert val == v and sorted(order) == list(range(g[0])) and vs_of_layout(g, order) == v
    rng = random.Random(1)
    for _ in range(30):
        a, b = rng.randint(1, 5), rng.randint(1, 5)
        g, A, B = sa.random_cobipartite(a, b, 0.5, rng)
        val, order = sa.cobipartite_vs(g, A, B)
        assert val == vs(g) == vs_of_layout(g, order)


def test_twin_algorithm_with_witness():
    for g in atlas(5):
        v = vs(g)
        val, order, u = sa.twin_vs(g)
        assert val == v and sorted(order) == list(range(g[0])) and vs_of_layout(g, order) == v


def test_mosp_equivalent_customers_value_and_pattern_order():
    rng = random.Random(2)
    for _ in range(60):
        rows, cols = rng.randint(2, 5), rng.randint(2, 6)
        base = [[rng.randint(0, 1) for _ in range(cols)] for _ in range(rows)]
        matrix = [list(base[0]) if rng.random() < 0.5 else base[i] for i in range(rows)]
        if not any(any(r) for r in matrix):
            continue
        ref = mosp_subset_dp(matrix)
        val, porder, u = sa.mosp_twin(matrix)
        assert val == ref and sorted(porder) == list(range(cols))
        assert sa.open_stacks_of_order(matrix, porder) == ref


def test_starlike_algorithm_exhaustive_to_five_and_random():
    for alpha0, cliques in sa.all_starlike(5):
        g, C, specs = sa.starlike_graph(alpha0, cliques)
        v = vs(g)
        pw, layout, bags = sa.starlike_pathwidth(C, specs)
        assert pw == v and vs_of_layout(g, layout) == v and sa._is_path_decomposition(g, bags)
    rng = random.Random(3)
    for _ in range(20):
        n = rng.randint(6, 11)
        alpha0, cliques = sa.random_starlike(n, rng.randint(1, min(4, n - 1)), rng)
        g, C, specs = sa.starlike_graph(alpha0, cliques)
        pw, layout, bags = sa.starlike_pathwidth(C, specs)
        assert pw == vs(g) == vs_of_layout(g, layout)


def test_edge_search_equals_cutwidth_on_small_subcubic_graphs():
    for g in atlas(5):
        es = edges_of(g)
        if not es or sa.max_degree(g) > 3 or g[0] + 2 * len(es) > 16:
            continue
        assert sa.edge_search_via_two_expansion(g) == cutwidth_dp(g)
