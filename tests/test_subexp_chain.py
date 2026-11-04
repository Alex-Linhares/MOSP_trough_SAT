"""loop0014 item 05: the chain count as an algebraic object
(`reports/subexp_pathwidth.md` §5) against brute force on small graphs; the
full atlas run is `python -m learning.subexp_chain`."""
import math

import numpy as np

from learning import subexp_chain as ch
from learning.subexp_reductions import atlas, vs
from paper1.complex_check import graph


def test_chain_count_three_ways_and_positive_iff_vs():
    for g in atlas(5):
        n, adj = g
        v = vs(g)
        for k in range(n):
            c = ch.chain_count_dp(adj, k)
            assert c == ch.chain_count_perm(adj, k)
            assert c == ch.chain_count_dp(adj, k, inner=True)
            assert c == ch.layout_count_vs(adj, k)
            assert (c > 0) == (v <= k)


def test_complete_graph_counts_factorial():
    for n in range(1, 7):
        adj = tuple(((1 << n) - 1) & ~(1 << v) for v in range(n))
        for k in range(n):
            assert ch.chain_count_dp(adj, k) == (math.factorial(n) if k >= n - 1 else 0)


def test_boundary_bit_polynomial_degree_and_monomials():
    for g in atlas(5):
        n, adj = g
        for u in range(n):
            d = bin(adj[u]).count("1")
            p = ch.boundary_bit_polynomial(adj, u)
            if d == 0:
                assert p["monomials"] == 0
            else:
                assert p["degree"] == d + 1 and p["monomials"] == 2 ** (d + 1) - 2


def test_threshold_top_coefficient():
    for n in range(1, 7):
        for k in range(n):
            f = np.fromiter((bin(S).count("1") <= k for S in range(1 << n)), dtype=np.int64, count=1 << n)
            c = ch.moebius(f, n)
            assert int(c[-1]) == (-1) ** (n - k) * math.comb(n - 1, k) == ch.threshold_top_coefficient(n, k)


def test_membership_polynomial_K3_at_vs_minus_one():
    n, adj = graph(3, [(0, 1), (0, 2), (1, 2)])
    p = ch.membership_polynomial(adj, 1)
    assert p["degree_Q"] == 3 and p["monomials_Q"] == 8 and p["essential"] == 3 and p["members"] == 5


def test_nested_chain_cnf_model_count_is_chain_count():
    for g in atlas(4):
        n, adj = g
        degs = [bin(a).count("1") for a in adj]
        for k in range(n):
            cl, pool = ch.nested_chain_cnf(adj, k)
            c = ch.chain_count_dp(adj, k)
            assert ch.count_models(cl, pool.top, limit=2 * c + 10) == c
            sz = ch.cnf_size(cl)
            sz["variables"] = pool.top
            assert sz == ch.cnf_size_formula(n, degs, k)


def test_rank_formulation_and_inclusion_exclusion():
    for g in atlas(4):
        n, adj = g
        for k in range(n):
            c = ch.chain_count_dp(adj, k)
            assert ch.rank_formulation_count(adj, k) == c
            assert ch.inclusion_exclusion_count(adj, k) == c


def test_split_rank_is_bounded_by_the_trivial_rank():
    for g in atlas(5):
        n, adj = g
        if n < 4:
            continue
        for A in ch.balanced_splits(n):
            r = ch.split_rank(adj, vs(g), A)
            assert 1 <= r <= 2 ** (n // 2)


def test_exact_count_table_log2_factorial_exceeds_budget():
    for row in ch.exact_count_table((16, 64, 125, 1000)):
        assert row["log2_factorial"] > row["Bv"]
        assert row["ranks_bits"] >= row["log2_factorial"]
