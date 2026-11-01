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


# --- item 04: the planted cluster --------------------------------------------------

from learning.separator_moment import (  # noqa: E402
    beta_star_gnp, enumerate_empty_pairs, hamming_distance, lq_sides, overlap_table, plant_cover,
    plant_pair, planted_mean_gnp, second_moment_exact_cover, second_moment_exact_gnp,
)


def test_beta_star_gnp_reproduces_the_record():
    # reports/random_graph_first_moment.md §3: 0.1706 at c = 6, 0.3371 at c = 10; zero at c ≤ 4 ln 2
    assert abs(beta_star_gnp(6) - 0.1706) < 2e-4
    assert abs(beta_star_gnp(10) - 0.3371) < 2e-4
    assert beta_star_gnp(2.5) == 0.0


@pytest.mark.parametrize("n,p,seed", [(12, 0.4, 1), (16, 0.3, 2), (20, 0.5, 3)])
def test_planting_deletes_exactly_the_forbidden_edges(n, p, seed):
    rng = random.Random(seed)
    adj = [0] * n
    for u, v in combinations(range(n), 2):
        if rng.random() < p:
            adj[u] |= 1 << v
            adj[v] |= 1 << u
    t, r = n // 3, n // 4
    A = (1 << t) - 1
    R = ((1 << r) - 1) << t
    planted = plant_pair(adj, A, R)
    for u in range(n):
        for v in range(n):
            before = adj[u] >> v & 1
            after = planted[u] >> v & 1
            crossing = (A >> u & 1 and R >> v & 1) or (R >> u & 1 and A >> v & 1)
            assert after == (0 if crossing else before)
    assert is_empty_pair(planted, A, R)
    # symmetric
    for u in range(n):
        for v in range(n):
            assert (planted[u] >> v & 1) == (planted[v] >> u & 1)


def test_planting_is_idempotent_and_rejects_overlap():
    adj = [0b0110, 0b1001, 0b1001, 0b0110]
    assert plant_pair(plant_pair(adj, 1, 2), 1, 2) == plant_pair(adj, 1, 2)
    with pytest.raises(ValueError):
        plant_pair(adj, 0b11, 0b10)


def test_plant_cover_meets_at_most_one_side_and_has_the_right_shape():
    n, m, d = 14, 20, 4
    A, R = 0b1111, 0b1110000
    M = plant_cover(n, m, d, A, R, np.random.default_rng(5))
    assert M.shape == (n, m)
    assert (M.sum(axis=0) == d).all()
    for j in range(m):
        mask = sum(1 << int(c) for c in np.flatnonzero(M[:, j]))
        assert not (mask & A and mask & R)
    assert not pattern_meets_both(M, A, R)
    assert is_empty_pair(mosp_masks(M), A, R)


def test_overlap_table_sums_to_n_and_matches_hamming():
    n = 10
    P = (0b0000001111, 0b0001110000)
    Q = (0b0000011100, 0b1100000000)
    T = overlap_table(P, Q, n)
    assert sum(T) == n
    assert len(T) == 9
    # rows A, R, S of P; columns A′, R′, S′ of Q
    assert T[0] == popcount(P[0] & Q[0]) and T[4] == popcount(P[1] & Q[1])
    assert hamming_distance(P, Q, n) == n - T[0] - T[4] - T[8]
    assert hamming_distance(P, P, n) == 0
    # the reverse of an equal-sized pair differs on every side vertex
    P2 = (0b00001111, 0b11110000)
    assert hamming_distance(P2, (P2[1], P2[0]), 8) == 8


def test_overlap_table_agrees_with_overlap_tables():
    from learning.separator_moment import overlap_tables
    n = 9
    pairs = [(0b000000111, 0b000111000), (0b000001011, 0b110000000), (0b100000011, 0b000011100)]
    T = overlap_tables(pairs, n)
    k = 0
    for i, P in enumerate(pairs):
        for j, Q in enumerate(pairs):
            if i == j:
                continue
            assert list(T[k]) == overlap_table(P, Q, n)
            k += 1


def test_lq_sides_reduces_to_lq_and_to_counting():
    from learning.first_moment import lq
    for n, t, s in [(12, 4, 3), (20, 7, 6), (15, 5, 2)]:
        assert abs(lq_sides(n, t, t - 1, s) - lq(n, t, s)) < 1e-12
    # by counting: 8 vertices, A = 3, R = 2, patterns of size 2 — the crossing pairs are 6 of 28
    assert abs(math.exp(lq_sides(8, 3, 2, 2)) - 22 / 28) < 1e-12


def test_second_moment_exact_cover_reduces_to_the_recorded_form():
    from learning.first_moment import second_moment_exact
    for n, t, sizes in [(12, 4, {3: 12}), (14, 5, {6: 14}), (16, 6, {4: 10, 6: 6})]:
        a = second_moment_exact(n, t, sizes)
        b = second_moment_exact_cover(n, t, t - 1, sizes)
        assert abs(a[0] - b[0]) < 1e-9 and abs(a[1] - b[1]) < 1e-9


def test_planted_mean_is_the_mean_of_the_other_pairs_on_gnp():
    # E[X′ | P₀ empty] = E[X²]/E[X] − 1, checked against a simulation of the planted law at n = 9
    n, k, p = 9, 3, 0.45
    N, t = forced_sizes(n, k)
    r = N - t
    A = (1 << t) - 1
    R = ((1 << r) - 1) << t
    rng = random.Random(11)
    reps = 1500
    tot = 0
    for _ in range(reps):
        adj = [0] * n
        for u, v in combinations(range(n), 2):
            if rng.random() < p:
                adj[u] |= 1 << v
                adj[v] |= 1 << u
        pairs = enumerate_empty_pairs(plant_pair(adj, A, R), k)
        assert (A, R) in pairs
        tot += len(pairs) - 1
    pred = planted_mean_gnp(n, t, r, p)
    sim = tot / reps
    assert abs(sim - pred) < 0.12 * pred + 0.3, (sim, pred)


def test_planted_mean_identity_against_the_enumerated_second_moment():
    # E[X²] = E[X] (1 + E[X′ | planted]) with both sides from the finite forms
    for n, t, r, p in [(8, 3, 2, 0.3), (10, 4, 3, 0.5)]:
        logEX, logEX2, _ = second_moment_exact_gnp(n, t, r, p)
        assert abs(math.exp(logEX2 - logEX) - 1 - planted_mean_gnp(n, t, r, p)) < 1e-9


def test_planted_inverse_mean_is_the_union_bound_slack():
    # Σ_P 1[P empty] / X = 1[X > 0], and by exchangeability E[Σ_P 1[P empty] f(X)] = E[X] · E[f(X) | P₀ empty],
    # so P(X > 0) / E[X] = E[1/X | P₀ empty]; checked exactly on every labelled graph at n = 6, k = 2
    n, k, p = 6, 2, 0.35
    N, t = forced_sizes(n, k)
    r = N - t
    A = (1 << t) - 1
    R = ((1 << r) - 1) << t
    edges = list(combinations(range(n), 2))
    forbidden = {e for e in edges if (A >> e[0] & 1 and R >> e[1] & 1) or (R >> e[0] & 1 and A >> e[1] & 1)}
    EX = Ppos = 0.0
    planted = 0.0
    for mask in range(1 << len(edges)):
        adj = [0] * n
        w = 1.0
        crosses = False
        for i, (u, v) in enumerate(edges):
            if mask >> i & 1:
                adj[u] |= 1 << v
                adj[v] |= 1 << u
                w *= p
                crosses |= (u, v) in forbidden
            else:
                w *= 1 - p
        X = count_exact_pairs(adj, k)
        EX += w * X
        Ppos += w * (X > 0)
        if not crosses:
            planted += w / (1 - p) ** len(forbidden) / X    # the conditional weight; X ≥ 1 here
    assert abs(Ppos / EX - planted) < 1e-12
