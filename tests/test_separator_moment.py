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

import math
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


# --- item 03: the clumping decomposed ------------------------------------------

from learning.first_moment import empty_pair_count_brute  # noqa: E402
from learning.separator_moment import (  # noqa: E402
    closed_nbhd, closed_pairs_pruned, closure_image, enumerate_empty_pairs, gnp_pair_rate, move_classes,
    overlap_tables, second_moment_enum_gnp, second_moment_exact_gnp, second_moment_rate_gnp,
    separators_of, small_nbhd_sets,
)


def _edge_masks(adj):
    """The MOSP-style pattern masks of a graph: one two-customer pattern per edge."""
    n = len(adj)
    return [(1 << u) | (1 << v) for u in range(n) for v in range(u + 1, n) if adj[u] >> v & 1]


@pytest.mark.parametrize("n,p,seed", [(8, 0.3, 1), (10, 0.3, 2), (10, 0.5, 3), (12, 0.25, 4), (12, 0.5, 5)])
def test_enumeration_against_exact_pairs_and_the_brute_count(n, p, seed):
    adj = random_graph(n, p, seed)
    k = vertex_separation(adj)
    for kk in (k - 1, k, k + 1):
        if kk < 0:
            continue
        pairs = enumerate_empty_pairs(adj, kk)
        assert sorted(pairs) == sorted(exact_pairs(adj, kk))
        assert len(pairs) == count_exact_pairs(adj, kk)
        N, t = forced_sizes(n, kk)
        if N - t == t - 1:
            # the brute count of first_moment uses |R| = t − 1
            assert len(pairs) == empty_pair_count_brute(_edge_masks(adj), n, t)
        # separators among the pairs are exactly the k-sets in E_bip (L1′ c)
        assert len(separators_of(pairs, n)) == count_separators(adj, kk)[0]
        for A, R in pairs:
            assert is_empty_pair(adj, A, R)


@pytest.mark.parametrize("n,p,seed", [(8, 0.3, 1), (10, 0.4, 2), (12, 0.3, 3), (14, 0.35, 4)])
def test_pruned_closed_pairs_match_the_direct_enumeration(n, p, seed):
    adj = random_graph(n, p, seed)
    k = vertex_separation(adj)
    for kk in (k, k + 1, k + 2):
        if kk >= n:
            continue
        assert sorted(closed_pairs_pruned(adj, kk)) == sorted(closed_pairs(adj, kk))
        pairs = enumerate_empty_pairs(adj, kk)
        image = closure_image(adj, pairs)
        assert image <= set(closed_pairs(adj, kk)), "X₃′ ⊆ X₃"
        for A, R in image:
            assert is_closed_pair(adj, A, R)
            assert close_pair(adj, A, R) == (A, R), "closure is idempotent on closed pairs"


def test_small_nbhd_sets_is_the_down_closed_family():
    adj = random_graph(10, 0.3, 7)
    for limit in (3, 5, 7):
        fam = set(small_nbhd_sets(adj, limit))
        brute = {A for A in range(1 << 10) if popcount(closed_nbhd(adj, A)) <= limit}
        assert fam == brute
        assert set(small_nbhd_sets(adj, limit, 2, 3)) == {A for A in brute if 2 <= popcount(A) <= 3}
    with pytest.raises(OverflowError):
        small_nbhd_sets(adj, 10, max_sets=5)


def test_move_classes_on_a_hand_built_example():
    # the path 0-1-2-3-4-5 has pathwidth 1; at k = 1, N = 5, t = 3, |R| = 2:
    # every exact-size pair is (A, R) with A three vertices, R two, no A–R edge
    n = 6
    adj = [0] * n
    for u in range(n - 1):
        adj[u] |= 1 << (u + 1)
        adj[u + 1] |= 1 << u
    assert vertex_separation(adj) == 1
    pairs = enumerate_empty_pairs(adj, 1)
    # the cut vertex S = {3}: A = {0,1,2}, R = {4,5}; S = {2}: A = {3,4,5}, R = {0,1}
    assert set(pairs) == {(0b000111, 0b110000), (0b111000, 0b000011)}
    cls = move_classes(pairs, n)
    assert max(cls) + 1 == 2, "the two pairs differ on every vertex: two classes"
    # a disjoint union of two triangles with a pendant: pairs sharing a separator differ by swaps
    adj = [0] * 7
    for u, v in [(0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5), (2, 6)]:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    k = vertex_separation(adj)
    pairs = enumerate_empty_pairs(adj, k)
    cls = move_classes(pairs, 7)
    # the pair (A, R) and the pair with one A-vertex swapped against one S-vertex
    # are adjacent: check the adjacency relation directly on every pair
    index = {P: i for i, P in enumerate(pairs)}
    full = (1 << 7) - 1
    for (A, R), i in index.items():
        for (A2, R2), j in index.items():
            S, S2 = full & ~(A | R), full & ~(A2 | R2)
            moved = popcount(A ^ A2 | R ^ R2 | S ^ S2) // 2 * 1  # vertices whose class differs
            differing = popcount((A & ~A2) | (R & ~R2) | (S & ~S2))
            if differing <= 2:
                assert cls[i] == cls[j]
    # and every class is connected through such steps: a BFS over the relation reproduces the classes
    seen = {}
    for P in pairs:
        if P in seen:
            continue
        stack = [P]
        seen[P] = len(seen)
        while stack:
            A, R = stack.pop()
            S = full & ~(A | R)
            for Q in pairs:
                if Q in seen and seen[Q] == seen[P]:
                    continue
                A2, R2 = Q
                S2 = full & ~(A2 | R2)
                if popcount((A & ~A2) | (R & ~R2) | (S & ~S2)) <= 2:
                    if Q not in seen:
                        seen[Q] = seen[P]
                        stack.append(Q)
    assert len(set(seen.values())) == max(cls) + 1


@pytest.mark.parametrize("n,t,r,p", [(8, 3, 2, 0.3), (10, 3, 2, 0.3), (10, 4, 3, 0.5)])
def test_bernoulli_second_moment_against_enumeration(n, t, r, p):
    logEX, logEX2, ratio = second_moment_exact_gnp(n, t, r, p)
    EX, EX2 = second_moment_enum_gnp(n, t, r, p)
    assert abs(math.exp(logEX) - EX) < 1e-9 * EX
    assert abs(math.exp(logEX2) - EX2) < 1e-9 * EX2
    assert abs(ratio - EX2 / EX ** 2) < 1e-9


def test_bernoulli_second_moment_rate_is_consistent_with_the_finite_form():
    # the sup over tables bounds the finite exponent from above, and the finite
    # exponent per vertex approaches it as n grows (p = c/n, sides a n)
    a, c = 0.3, 6.0
    sup, twog, T = second_moment_rate_gnp(a, c)
    assert abs(twog - 2 * gnp_pair_rate(a, c)) < 1e-12
    assert sup >= twog - 1e-9, "the product table is one candidate, so sup ≥ 2 g(a) − c-order terms"
    assert abs(T.sum() - 1) < 1e-9 and np.all(T >= -1e-9)
    # the finite sum has order t⁴ terms, so n stays small here; the polynomial
    # correction to the exponent is at most 9 log(n + 1) / (2 n) (nine cells)
    prev = None
    for n in (30, 60, 120):
        t = round(a * n)
        _, logEX2, _ = second_moment_exact_gnp(n, t, t, c / n)
        val = logEX2 / n
        corr = 9 * math.log(n + 1) / (2 * n)
        assert val <= sup + corr + 1e-9
        assert val >= sup - corr - 0.05
        if prev is not None:
            assert abs(val - sup) < abs(prev - sup) + 1e-9
        prev = val


def test_overlap_tables_shape_and_margins():
    adj = random_graph(10, 0.4, 11)
    k = vertex_separation(adj)
    pairs = enumerate_empty_pairs(adj, k)
    T = overlap_tables(pairs, 10)
    N, t = forced_sizes(10, k)
    assert T.shape == (len(pairs) * (len(pairs) - 1), 9)
    assert np.all(T[:, :3].sum(axis=1) == t) and np.all(T[:, 3:6].sum(axis=1) == N - t)
    assert np.all(T[:, [0, 3, 6]].sum(axis=1) == t) and np.all(T.sum(axis=1) == 10)
