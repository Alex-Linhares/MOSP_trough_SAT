"""loop0011 item 02: the deterministic lemmas of the separator first moment
(`learning.separator_moment`, `reports/separator_moment.md` §2).

L1  a graph of pathwidth `k < n` has an exact-size empty pair (`|A| = ⌈(n − k)/2⌉`,
    `|R| = ⌊(n − k)/2⌋`);
L1′ equivalently a `k`-set `S` in `E_bip`; `E_bip ⊆ E_relax`, strictly;
L2  the alternating closure of any empty pair is monotone, stops after one
    round, and lands on a closed pair `S* = N(A*) ∩ N(R*)` of the forced sizes;
L3  on the MOSP graph a pair is empty iff no pattern meets both sides.

Every labelled graph on ≤ 6 vertices is enumerated here; the full check (every
graph to 9 vertices, 20,000 random at 10–12, 2,000 covers) is
`reports/scratch/separator_moment/02_lemmas/check.py`.
"""
from __future__ import annotations

import random
from itertools import combinations

import networkx as nx
import numpy as np
import pytest

from benchmarks.generator import generate_structured_instance
from fixed_parameter_algorithm.pathwidth import compute_pathwidth
from learning.first_moment import vertex_separation_brute
from learning.separator_moment import (
    close_pair, closed_pairs, closure_sequence, count_exact_pairs, count_separators,
    exact_pairs, forced_sizes, is_closed_pair, is_empty_pair, mosp_masks, open_nbhd,
    pattern_meets_both, popcount, separator_events, shares_pattern, vertex_separation,
)


def all_labelled_graphs(n):
    pairs = list(combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        adj = [0] * n
        for i, (u, v) in enumerate(pairs):
            if mask >> i & 1:
                adj[u] |= 1 << v
                adj[v] |= 1 << u
        yield adj


def random_graph(n, p, seed):
    rng = random.Random(seed)
    adj = [0] * n
    for u, v in combinations(range(n), 2):
        if rng.random() < p:
            adj[u] |= 1 << v
            adj[v] |= 1 << u
    return adj


def test_vertex_separation_agrees_with_the_two_other_implementations():
    for n in range(1, 6):
        for adj in all_labelled_graphs(n):
            G = nx.Graph()
            G.add_nodes_from(range(n))
            G.add_edges_from((u, v) for u in range(n) for v in range(u + 1, n) if adj[u] >> v & 1)
            k = vertex_separation(adj)
            assert k == vertex_separation_brute(adj) == compute_pathwidth(G)[0]


def test_forced_sizes():
    assert forced_sizes(10, 3) == (7, 4)
    assert forced_sizes(10, 4) == (6, 3)
    with pytest.raises(ValueError):
        forced_sizes(5, 5)


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 6])
def test_L1_and_L1prime_on_every_labelled_graph(n):
    for adj in all_labelled_graphs(n):
        k = vertex_separation(adj)
        X1 = count_exact_pairs(adj, k)
        X2, X2r = count_separators(adj, k)
        assert X1 > 0, "L1: an exact-size empty pair exists at k = pw"
        assert X2 > 0, "L1′: a k-set in E_bip exists at k = pw"
        assert X2 <= X2r, "E_bip ⊆ E_relax"
        assert sum(1 for _ in exact_pairs(adj, k)) == X1
        if k >= 1:
            Y1 = count_exact_pairs(adj, k - 1)
            Y2, Y2r = count_separators(adj, k - 1)
            assert (Y1 > 0) == (Y2 > 0), "an exact-size pair exists iff some S is in E_bip"
            assert Y2 <= Y2r


def test_E_relax_strictly_contains_E_bip_on_three_disjoint_edges():
    adj = [0] * 6
    for u, v in [(0, 3), (1, 4), (2, 5)]:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    assert separator_events(adj, 0, 0) == (False, True)
    assert vertex_separation(adj) == 1


@pytest.mark.parametrize("n", [3, 4, 5, 6])
def test_L2_closure_on_every_labelled_graph(n):
    full = (1 << n) - 1
    for adj in all_labelled_graphs(n):
        k = vertex_separation(adj)
        N, t = forced_sizes(n, k)
        X3 = set(closed_pairs(adj, k))
        for A, R in exact_pairs(adj, k):
            seq = closure_sequence(adj, A, R)
            for (a0, r0), (a1, r1) in zip(seq, seq[1:]):
                assert a0 & ~a1 == 0 and r0 & ~r1 == 0, "monotone"
            assert seq[2] == seq[3] == seq[4], "stops after one round"
            As, Rs = seq[-1]
            Ss = full & ~(As | Rs)
            assert is_closed_pair(adj, As, Rs) and is_empty_pair(adj, As, Rs)
            assert popcount(As) >= t and popcount(Rs) >= N - t and popcount(Ss) <= k
            assert Ss == open_nbhd(adj, As) & open_nbhd(adj, Rs)
            assert (As, Rs) == close_pair(adj, A, R, "A")
            assert (As, Rs) in X3
            Ar, Rr = close_pair(adj, A, R, "R")
            assert is_closed_pair(adj, Ar, Rr)


def test_the_two_closure_orders_can_differ():
    # the fixpoint is a representative, not canonical: on some 4-vertex graph
    # closing A first and closing R first land on different closed pairs
    found = 0
    for adj in all_labelled_graphs(4):
        k = vertex_separation(adj)
        for A, R in exact_pairs(adj, k):
            if close_pair(adj, A, R, "A") != close_pair(adj, A, R, "R"):
                found += 1
    assert found > 0


@pytest.mark.parametrize("seed", range(5))
def test_L3_on_random_covers(seed):
    inst = generate_structured_instance(8, 12, 3, seed=seed)
    M = inst.matrix
    adj = mosp_masks(M)
    n = M.shape[0]
    full = (1 << n) - 1
    k = vertex_separation(adj)
    assert count_exact_pairs(adj, k) > 0
    rng = random.Random(seed)
    for _ in range(50):
        A = rng.randrange(1, full)
        R = rng.randrange(0, full) & ~A
        assert is_empty_pair(adj, A, R) == (not pattern_meets_both(M, A, R))
    for A, R in exact_pairs(adj, k):
        As, Rs = close_pair(adj, A, R)
        Ss = full & ~(As | Rs)
        for s in range(n):
            if Ss >> s & 1:
                assert shares_pattern(M, s, As) and shares_pattern(M, s, Rs)


def test_mosp_masks_matches_networkx_graph():
    M = np.array([[1, 1, 0], [0, 1, 1], [0, 0, 1], [1, 0, 0]])
    adj = mosp_masks(M)
    assert adj == [0b1010, 0b0101, 0b0010, 0b0001]


def test_random_graphs_at_10():
    for seed in range(20):
        adj = random_graph(10, 0.3, seed)
        k = vertex_separation(adj)
        assert count_exact_pairs(adj, k) > 0
        X2, X2r = count_separators(adj, k)
        assert 0 < X2 <= X2r
