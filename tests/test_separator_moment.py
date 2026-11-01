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
import re
from pathlib import Path
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


# ---------------------------------------------------------------------------
# item 05: the inner probability P_N(E_bip), exactly
# ---------------------------------------------------------------------------

from learning.separator_moment import (  # noqa: E402
    connected_probs, log_connected, log_connected_enum, log_prob_bip, log_prob_bip_enum,
    log_prob_bip_mc, log_prob_partition, log_prob_rel, log_product_bound, partitions,
)
from learning.separator_moment import _lse  # noqa: E402


def test_connected_probs_against_enumeration():
    # the connected labelled graphs on j vertices number 1, 1, 4, 38, 728 (OEIS A001187)
    for p in (0.1, 0.5):
        lc = log_connected(5, p)
        for j in range(1, 6):
            assert lc[j] == pytest.approx(log_connected_enum(j, p), abs=1e-9)
    counts = [round(math.exp(log_connected(5, 0.5)[j]) * 2 ** (j * (j - 1) // 2)) for j in range(1, 6)]
    assert counts == [1, 1, 4, 38, 728]


def test_connected_probs_small_p_precision():
    # at small p the recursion cancels to C_N ~ e^{-N (1-p)^{N-1}}; the mpmath value is positive and monotone in p
    C = [connected_probs(40, p)[40] for p in (0.02, 0.05, 0.1)]
    assert all(c > 0 for c in C)
    assert C[0] < C[1] < C[2]
    assert float(C[2]) == pytest.approx(math.exp(log_connected(40, 0.1)[40]))


def test_partitions_count_and_shape():
    assert sum(1 for _ in partitions(10)) == 42
    assert sum(1 for _ in partitions(20)) == 627
    assert list(partitions(0)) == [()]
    for lam in partitions(8, 3):
        assert sum(lam) == 8 and max(lam) <= 3 and list(lam) == sorted(lam, reverse=True)


def test_partition_law_sums_to_one():
    for N in (1, 4, 9, 14):
        for p in (0.05, 0.3):
            lc = log_connected(N, p)
            assert _lse([log_prob_partition(lam, N, p, lc) for lam in partitions(N)]) == pytest.approx(0.0, abs=1e-9)
    with pytest.raises(ValueError):
        log_prob_partition((2, 2), 5, 0.3)


def test_prob_bip_against_enumeration():
    for N in range(1, 6):
        for p in (0.1, 0.5):
            for t in range(N + 1):
                a = log_prob_bip(N, p, t)
                b = log_prob_bip_enum(N, p, t)
                if b == -math.inf:
                    assert a == -math.inf
                else:
                    assert a == pytest.approx(b, abs=1e-9)


def test_prob_bip_edge_cases_and_orderings():
    # t = 0 or t = N: the event always holds (one empty side); the two sides are exchangeable
    for N in (3, 8, 13):
        assert log_prob_bip(N, 0.2, 0) == pytest.approx(0.0, abs=1e-12)
        assert log_prob_bip(N, 0.2, N) == pytest.approx(0.0, abs=1e-12)
        for t in range(1, N):
            assert log_prob_bip(N, 0.2, t) == pytest.approx(log_prob_bip(N, 0.2, N - t), abs=1e-9)
    assert log_prob_bip(0, 0.5) == 0.0
    with pytest.raises(ValueError):
        log_prob_bip(5, 0.2, 6)


def test_prob_bip_below_relaxed_and_product_bound():
    for N in (10, 25, 40):
        for cp in (1.0, 3.0, 8.0):
            p = cp / N
            lc = log_connected(N, p)
            for t in range(0, N + 1, 5):
                a = log_prob_bip(N, p, t, lc)
                r = log_prob_rel(N, p, max(t, N - t), lc)
                assert a <= r + 1e-9 <= 1e-9
                assert a <= log_product_bound(N, p, t) + 1e-9


def test_prob_rel_edge_cases_and_recursion():
    assert log_prob_rel(7, 0.3, 7) == 0.0
    assert log_prob_rel(7, 0.3, 10) == 0.0
    assert log_prob_rel(7, 0.3, 0) == -math.inf
    # M = 1: every vertex isolated, probability (1-p)^{C(N,2)}
    for N in (2, 5, 9):
        assert log_prob_rel(N, 0.3, 1) == pytest.approx(N * (N - 1) / 2 * math.log1p(-0.3), abs=1e-9)
    # M = N - 1: everything but "connected"
    N, p = 9, 0.25
    assert log_prob_rel(N, p, N - 1) == pytest.approx(math.log1p(-math.exp(log_connected(N, p)[N])), abs=1e-9)
    # the relaxed law is the partition sum over partitions with parts <= M
    N, p, M = 12, 0.15, 5
    lc = log_connected(N, p)
    direct = _lse([log_prob_partition(lam, N, p, lc) for lam in partitions(N) if max(lam) <= M])
    assert log_prob_rel(N, p, M, lc) == pytest.approx(direct, abs=1e-9)


def test_prob_bip_is_the_partition_sum():
    N, p, t = 12, 0.15, 6
    lc = log_connected(N, p)
    from learning.separator_moment import _subset_sum
    direct = _lse([log_prob_partition(lam, N, p, lc) for lam in partitions(N) if _subset_sum(list(lam), t)])
    assert log_prob_bip(N, p, t, lc) == pytest.approx(direct, abs=1e-9)


def test_prob_bip_monte_carlo():
    N, p = 14, 0.12
    exact = math.exp(log_prob_bip(N, p))
    mc, se = log_prob_bip_mc(N, p, samples=3000, seed=3)
    assert abs(exact - math.exp(mc)) < 4 * se + 1e-12


# --- item 06: the constants β_sep, β_closed, β_comb ----------------------------

from learning.separator_moment import (  # noqa: E402
    LN2, beta_closed, beta_combined, beta_sep, beta_star_gnp, closed_exponent, closed_rate,
    combined_exponent, components, edwards_mcdermid_poisson, exponent_slope_at, gnp_pair_rate,
    ldp_rate, log_closed_count, log_combined_count, log_connected, log_prob_bip, log_prob_rel,
    log_prob_rel_fast, pair_exponent_beta, rate_bracket,
)


def _enum_tilted_window(N, p, t_lo, t_hi, tilt):
    full = (1 << N) - 1
    E = N * (N - 1) // 2
    tot = 0.0
    for adj in all_labelled_graphs(N):
        m = sum(popcount(a) for a in adj) // 2
        comps = components(adj, full)
        reach = 1
        for cm in comps:
            reach |= reach << popcount(cm)
        if any(reach >> x & 1 for x in range(t_lo, t_hi + 1)):
            tot += p ** m * (1 - p) ** (E - m) * math.exp(tilt * len(comps))
    return math.log(tot) if tot > 0 else -math.inf


def test_window_and_tilt_recursion_against_enumeration():
    for N in range(1, 6):
        p = 0.3
        lc = log_connected(N, p)
        for t_lo in range(0, N + 1):
            for t_hi in range(t_lo, N + 1):
                for tilt in (0.0, LN2):
                    a = log_prob_bip(N, p, t_lo, lc, t_hi=t_hi, tilt=tilt)
                    b = _enum_tilted_window(N, p, t_lo, t_hi, tilt)
                    assert a == pytest.approx(b, abs=1e-9)


def test_fast_relaxed_recursion_pinned_to_the_table_one():
    for N, cp in ((6, 2.0), (30, 3.0), (80, 6.0)):
        p = cp / N
        lc = log_connected(N, p)
        for M in sorted({1, N // 3, N // 2, N}):
            for tilt in (0.0, LN2, 0.3):
                a = log_prob_rel(N, p, M, lc, tilt=tilt)
                b = log_prob_rel_fast(N, p, M, lc, tilt=tilt)
                assert a == pytest.approx(b, abs=1e-8, rel=1e-9)
    # the tilted sum over every partition is E[e^{tilt κ}], exceeding 1
    assert log_prob_rel(10, 0.1, 10, tilt=LN2) > 0


def _enum_closed_count(n, k, p):
    E = n * (n - 1) // 2
    tot = 0.0
    for adj in all_labelled_graphs(n):
        m = sum(popcount(a) for a in adj) // 2
        tot += p ** m * (1 - p) ** (E - m) * len(closed_pairs(adj, k))
    return math.log(tot) if tot > 0 else -math.inf


def test_finite_closed_count_against_enumeration():
    for n in range(2, 6):
        for p in (0.25, 0.6):
            for k in range(0, n):
                assert log_closed_count(n, k, p) == pytest.approx(_enum_closed_count(n, k, p), abs=1e-9)


def test_combined_count_is_a_valid_bound_at_small_sizes():
    # E[Σ_{S} 1[E_win(G − S)] 2^κ Qmax^{|S|}] ≥ P(pw ≤ k): check against every labelled graph at n = 5
    # (vertex separation by the brute-force DP) and that the two inner forms agree
    n, p = 5, 0.4
    E = n * (n - 1) // 2
    for k in range(0, n):
        prob = 0.0
        for adj in all_labelled_graphs(n):
            m = sum(popcount(a) for a in adj) // 2
            if vertex_separation(adj) <= k:
                prob += p ** m * (1 - p) ** (E - m)
        bip = log_combined_count(n, k, p, form="bip")
        rel = log_combined_count(n, k, p, form="rel")
        assert bip <= rel + 1e-12
        assert math.log(prob) <= bip + 1e-12
        closed = log_closed_count(n, k, p)
        assert math.log(prob) <= closed + 1e-12


def test_pair_exponent_in_beta_and_the_closed_exponent_at_the_corner():
    for c in (3.0, 6.0, 10.0):
        for b in (0.02, 0.17, 0.3):
            a = (1 - b) / 2
            assert pair_exponent_beta(c, b) == pytest.approx(gnp_pair_rate(a, c), abs=1e-12)
            assert closed_exponent(a, a, b, c, with_q=False) == pytest.approx(gnp_pair_rate(a, c), abs=1e-12)
            assert closed_exponent(a, a, b, c) < gnp_pair_rate(a, c)  # the q terms only lower it
        # the sup is at least the corner value, so β_closed ≥ β* is not automatic: test it
        assert closed_rate(0.17, c)[0] >= closed_exponent((1 - 0.17) / 2, (1 - 0.17) / 2, 0.17, c) - 1e-12


def test_beta_sep_with_the_brackets_lower_end_is_beta_star():
    for c in (2.0, 3.0, 4.0, 6.0, 10.0, 20.0):
        assert beta_sep(c, lambda cp: rate_bracket(cp)[0]) == pytest.approx(beta_star_gnp(c), abs=2e-6)


def test_the_constants_are_ordered():
    for c in (2.5, 3.0, 4.0, 6.0, 10.0, 16.0):
        bs = beta_star_gnp(c)
        lo, hi = rate_bracket(c * (1 - bs))
        assert lo <= ldp_rate(c * (1 - bs), 0.5) <= hi + 1e-12
        b_cited = beta_sep(c)
        b_hi = beta_sep(c, lambda cp: rate_bracket(cp)[1])
        assert bs <= b_cited <= b_hi
        assert beta_closed(c) >= bs
    # the separator count is positive strictly above 2 ln 2 and zero below (cited rate)
    assert beta_sep(1.2) == 0.0
    assert beta_sep(2.0) > 0.0
    assert beta_star_gnp(2.0) == 0.0


def test_ldp_rate_zero_at_the_giant_and_positive_below_half():
    assert ldp_rate(3.0, 0.5) == pytest.approx(0.18309, abs=1e-4)
    assert ldp_rate(10.0, 0.5) == pytest.approx(1.81023, abs=1e-4)
    assert ldp_rate(1.2, 0.5) == 0.0
    assert ldp_rate(3.0, 0.99) == 0.0
    assert 0 < ldp_rate(3.0, 0.7) < ldp_rate(3.0, 0.5)


def test_combined_exponent_reduces_to_the_separator_form_at_the_corner():
    # at s = β the window is the balanced bipartition (u = ½) and the exponent is
    # H(β) + 2β ln q((1−β)/2) − (1−β) J(c′, ½)
    c, b = 6.0, 0.18
    J = lambda cp, u: 0.5 + 0.1 * u
    v = combined_exponent(c, b, b, J)
    q = math.log(-math.expm1(-c * (1 - b) / 2))
    H = -b * math.log(b) - (1 - b) * math.log(1 - b)
    assert v == pytest.approx(H + 2 * b * q - (1 - b) * J(c * (1 - b), 0.5), abs=1e-12)
    assert combined_exponent(c, b, b + 0.01, J) == -math.inf
    assert 0 < beta_combined(c, J) < 1


def test_edwards_mcdermid_and_the_slope_conversion():
    assert [round(edwards_mcdermid_poisson(c), 3) for c in (3, 6, 10)] == [0.183, 0.458, 0.656]
    assert exponent_slope_at(6.0, beta_star_gnp(6.0)) == pytest.approx(3.38, abs=0.02)
    assert exponent_slope_at(10.0, beta_star_gnp(10.0)) == pytest.approx(3.30, abs=0.02)


# --- item 07: the MOSP version — random clique covers -----------------------------

from fractions import Fraction

from learning.separator_moment import (
    beta_closed_cover, beta_star_cover, closed_cover_exponent_ind, closed_cover_exponent_na,
    closed_cover_log_count_exact, closed_cover_log_prob_exact, closed_cover_log_prob_na,
    closed_cover_rate, cover_log_pair_bound, cover_pair_exponent, cover_pair_exponent_beta,
    edwards_mcdermid_cover, flip_cover_exponent_na, flip_joint_pmf, flip_log_bound,
    flip_log_bound_fast, half_giant_line, isolated_pgf, isolated_pmf, rig_branching_factor,
    rig_giant,
)


def all_covers(n, sizes):
    choices = [[sum(1 << c for c in cs) for cs in combinations(range(n), s)] for s in sizes]
    for masks in __import__("itertools").product(*choices):
        yield masks


def _closed_prob_enum(n, A, R, S, sizes):
    tot = cnt = 0
    for masks in all_covers(n, sizes):
        cnt += 1
        if any(m & A and m & R for m in masks):
            continue
        if all(any((m >> v & 1) and (m & A) for m in masks) and any((m >> v & 1) and (m & R) for m in masks)
               for v in range(n) if S >> v & 1):
            tot += 1
    return Fraction(tot, cnt)


def test_closed_cover_probability_against_enumeration_and_the_na_bound_above_it():
    rng = random.Random(7)
    for n in range(3, 7):
        for m in range(1, 4):
            sizes = [rng.randint(1, min(4, n)) for _ in range(m)]
            a = rng.randint(1, n - 1)
            r = rng.randint(0, n - a)
            s = n - a - r
            A, R = (1 << a) - 1, ((1 << r) - 1) << a
            S = ((1 << n) - 1) & ~(A | R)
            pe = _closed_prob_enum(n, A, R, S, sizes)
            lp = closed_cover_log_prob_exact(n, a, r, s, sizes)
            if pe == 0:
                assert lp == -math.inf
            else:
                assert lp == pytest.approx(math.log(pe), abs=1e-9)
            if s > 0:
                assert closed_cover_log_prob_na(n, a, r, s, sizes) >= lp - 1e-9
    # the NA/tangent bound never falls below the exact probability (random, larger)
    for _ in range(10):
        n = rng.randint(8, 14)
        sizes = [rng.randint(2, 5) for _ in range(rng.randint(2, n))]
        a = rng.randint(1, n - 2)
        r = rng.randint(1, n - a - 1)
        s = n - a - r
        assert closed_cover_log_prob_na(n, a, r, s, sizes) >= closed_cover_log_prob_exact(n, a, r, s, sizes) - 1e-9


def test_closed_cover_count_is_below_the_pair_count_and_the_corner_reduces_to_the_pair_exponent():
    sizes = [3, 3, 2, 4, 3]
    for n, k in ((9, 3), (10, 4), (11, 5)):
        exact = closed_cover_log_count_exact(n, k, sizes)
        assert exact <= cover_log_pair_bound(n, k, sizes) + 1e-9
    d, mu = 6, 1.0
    b = 0.5
    a = (1 - b) / 2
    from learning.first_moment import rate
    assert cover_pair_exponent(a, a, b, mu, {d: 1}) == pytest.approx(rate(a, mu, {d: 1}), abs=1e-12)
    assert closed_cover_exponent_na(a, a, b, mu, {d: 1}) <= cover_pair_exponent_beta(b, mu, {d: 1})
    assert closed_cover_exponent_ind(a, a, b, mu, {d: 1}) <= closed_cover_exponent_na(a, a, b, mu, {d: 1}) + 1e-9
    from learning.first_moment import beta_star
    assert beta_star_cover(mu, {d: 1}) == pytest.approx(beta_star(mu, {d: 1}), abs=3e-4)
    bc = beta_closed_cover(mu, {d: 1})
    assert beta_star_cover(mu, {d: 1}) < bc < beta_star_cover(mu, {d: 1}) + 0.02
    assert closed_cover_rate(bc, mu, {d: 1})[0] == pytest.approx(0.0, abs=1e-4)


def test_isolated_and_flip_laws_against_enumeration():
    rng = random.Random(11)
    for n in range(2, 6):
        for m in range(1, 4):
            sizes = [rng.randint(1, min(4, n)) for _ in range(m)]
            counts = [0] * (n + 1)
            tot = 0
            for masks in all_covers(n, sizes):
                tot += 1
                counts[sum(1 for v in range(n) if not any((mk >> v & 1) and popcount(mk) >= 2 for mk in masks))] += 1
            assert isolated_pmf(n, sizes) == [Fraction(c, tot) for c in counts]
            assert isolated_pgf(n, sizes, 1.0) == pytest.approx(1.0)
    for n in range(3, 7):
        for m in range(1, 4):
            sizes = [rng.randint(1, min(4, n)) for _ in range(m)]
            a = rng.randint(1, n - 1)
            r = rng.randint(1, n - a)
            A, R = (1 << a) - 1, ((1 << r) - 1) << a
            counts = {}
            tot = 0
            for masks in all_covers(n, sizes):
                tot += 1
                if any(mk & A and mk & R for mk in masks):
                    continue
                iA = sum(1 for v in range(a) if not any((mk >> v & 1) and (mk & A & ~(1 << v)) for mk in masks))
                iR = sum(1 for v in range(a, a + r) if not any((mk >> v & 1) and (mk & R & ~(1 << v)) for mk in masks))
                counts[(iA, iR)] = counts.get((iA, iR), 0) + 1
            pmf = flip_joint_pmf(n, a, r, sizes)
            assert all(pmf[i][ip] == Fraction(counts.get((i, ip), 0), tot) for i in range(a + 1) for ip in range(r + 1))
    for n, k in ((7, 2), (9, 3)):
        sizes = [2, 3, 2, 4]
        slow, fast = flip_log_bound(n, k, sizes), flip_log_bound_fast(n, k, sizes)
        assert slow == pytest.approx(fast, abs=1e-9)
        assert slow[0] <= slow[1] + 1e-12       # the weighted count never exceeds the pair count
        assert slow[1] == pytest.approx(cover_log_pair_bound(n, k, sizes), abs=1e-9)
    d, mu = 6, 1.0
    b = beta_star_cover(mu, {d: 1})
    a = (1 - b) / 2
    v, x, y = flip_cover_exponent_na(a, a, b, mu, {d: 1}, grid=4)
    assert -0.02 < v < 0.0 and 0 <= x <= a and 0 <= y <= a


def test_rig_giant_and_the_half_giant_line():
    assert rig_giant(0.5, {2: 1}) == 0.0                       # branching factor exactly 1
    assert rig_branching_factor(0.5, {2: 1}) == pytest.approx(1.0)
    assert rig_giant(0.25, {3: 1}) > 0 and rig_giant(1.0, {2: 1}) == pytest.approx(0.7968, abs=1e-3)
    th = rig_giant(1.0, {6: 1})
    assert 1 - th == pytest.approx(math.exp(-6 * (1 - (1 - th) ** 5)), abs=1e-9)
    for mu in (0.25, 0.5, 1.0, 2.0):
        d = half_giant_line(mu)
        e = mu * (d - 1)
        e_g = (math.sqrt(mu * mu + 4 * mu) - mu) / 2
        assert e_g < e < 1.0
        assert rig_giant(mu, {d: 1}) == pytest.approx(0.5, abs=1e-6)
    assert 0 < edwards_mcdermid_cover(1.0, {6: 1}) < 1


# --- item 08: the theorems on paper, in exact rationals (§8) -------------------------
#
# Theorem S  P(pw(G(n, p)) ≤ k) ≤ C(n, k) · P_N(E_bip), with the factorisation of
#            the G(n, p) weight over G[V ∖ S] as the step item 10 must formalise;
# Cor. S′    the same with E_relax, by Lemmas G (Gilbert) and F (first-vertex component);
# Lemma P    P_N(E_bip) as a sum over the partitions of N;
# Theorem Cl P(pw ≤ k) ≤ E[X₃] = Σ n!/(a! r! s!) (1−p)^{ar} (1−(1−p)^a)^s (1−(1−p)^r)^s;
# Lemma W    Y = Σ_P 1[P empty]/Z(P) ≥ 1[X > 0] for 1 ≤ Z ≤ X, first instance the flips.
# The full check (every labelled graph to 7 vertices, 1,000 random instances at
# n = 10, Monte Carlo covers) is reports/scratch/separator_moment/08_theorems/check.py.

from fractions import Fraction  # noqa: E402
from math import comb  # noqa: E402

from learning.separator_moment import (  # noqa: E402
    closed_count_exact, components, connected_probs_exact, flip_count, flip_swaps, isolated_in,
    log_closed_count, log_prob_bip, log_prob_rel, pair_count_exact, prob_bip_exact,
    prob_relax_exact, weighted_count, weighted_graph_count,
)


def _weighted(n, p, pred):
    """Σ_G w_p(G) · pred(adj) over every labelled graph on n vertices, exactly."""
    q = 1 - p
    Cn = n * (n - 1) // 2
    total = Fraction(0)
    for adj in all_labelled_graphs(n):
        e = sum(popcount(a) for a in adj) // 2
        v = pred(adj)
        if v:
            total += v * p ** e * q ** (Cn - e)
    return total


def test_gilbert_and_the_first_vertex_recursion_against_enumeration():
    # A001187: labelled connected graphs 1, 1, 4, 38, 728, 26704, 1866256
    C = connected_probs_exact(7, Fraction(1, 2))
    assert [c * 2 ** (j * (j - 1) // 2) for j, c in enumerate(C)] == [1, 1, 1, 4, 38, 728, 26704, 1866256]
    p = Fraction(1, 3)
    for N in range(1, 6):
        full = (1 << N) - 1
        C = connected_probs_exact(N, p)
        assert weighted_graph_count(N, p, lambda adj: len(components(adj, full)) == 1) == C[N]
        t = (N + 1) // 2
        bip = weighted_graph_count(N, p, lambda adj: _bip(adj, t))
        assert bip == prob_bip_exact(N, p)                                   # Lemma P
        assert math.log(bip) == pytest.approx(log_prob_bip(N, float(p)), abs=1e-9)
        for M in range(1, N + 1):
            rel = weighted_graph_count(N, p, lambda adj, M=M: max(popcount(c) for c in components(adj, full)) <= M)
            assert rel == prob_relax_exact(N, p, M, C)                       # Lemma F
            assert math.log(rel) == pytest.approx(log_prob_rel(N, float(p), M), abs=1e-9)
        assert prob_bip_exact(N, p) <= prob_relax_exact(N, p, t)             # E_bip ⊆ E_relax


def _bip(adj, t):
    full = (1 << len(adj)) - 1
    reach = 1
    for c in components(adj, full):
        reach |= reach << popcount(c)
    return bool(reach >> t & 1)


def test_theorems_S_and_Cl_and_the_factorisation_on_every_labelled_graph_to_five():
    for p in (Fraction(1, 2), Fraction(1, 3)):
        for n in range(1, 6):
            pw = {}
            for adj in all_labelled_graphs(n):
                pw[tuple(adj)] = vertex_separation(adj)
            for k in range(n):
                N, t = forced_sizes(n, k)
                lhs = _weighted(n, p, lambda adj: int(pw[tuple(adj)] <= k))
                inner = prob_bip_exact(N, p)
                assert lhs <= comb(n, k) * inner                                            # Theorem S
                assert comb(n, k) * inner <= comb(n, k) * prob_relax_exact(N, p, t)          # Corollary S′
                ex3 = _weighted(n, p, lambda adj: len(closed_pairs(adj, k)))
                assert ex3 == closed_count_exact(n, k, p)                                    # Cl's formula = E[X₃]
                assert lhs <= ex3                                                           # Theorem Cl
                assert math.log(ex3) == pytest.approx(log_closed_count(n, k, float(p)), abs=1e-9)
                ex1 = _weighted(n, p, lambda adj: count_exact_pairs(adj, k))
                assert ex1 == pair_count_exact(n, k, p) and lhs <= ex1                      # the count on record
                # the factorisation: for every k-set S the weighted count of {E_bip(S)} is P_N(E_bip)
                full = (1 << n) - 1
                for combo in combinations(range(n), k):
                    S = sum(1 << v for v in combo)
                    got = _weighted(n, p, lambda adj, S=S: int(_bip_minus(adj, S, full, t)))
                    assert got == inner


def _bip_minus(adj, S, full, t):
    reach = 1
    for c in components(adj, full & ~S):
        reach |= reach << popcount(c)
    return bool(reach >> t & 1)


def test_flip_lemma_and_lemma_W_on_random_graphs():
    for seed in range(40):
        n = 8 + seed % 3
        adj = random_graph(n, (0.2, 0.35, 0.5, 0.65)[seed % 4], seed)
        pw = vertex_separation(adj)
        for k in (pw, pw - 1):
            if k < 0:
                continue
            ps = enumerate_empty_pairs(adj, k)
            X = len(ps)
            pset = set(ps)
            if k == pw:
                assert X > 0                                                                # L1
            if not X:
                assert weighted_count([], lambda P: 1) == 0
                continue
            cls = move_classes(ps, n)
            size = {}
            for c in cls:
                size[c] = size.get(c, 0) + 1
            Zm = {P: size[c] for P, c in zip(ps, cls)}
            for (A, R) in ps:
                IA, IR = isolated_in(adj, A), isolated_in(adj, R)
                assert all(adj[v] & A == 0 for v in range(n) if IA >> v & 1)
                sw = flip_swaps(adj, A, R)
                ia, ir, Z = flip_count(adj, A, R)
                assert (ia, ir) == (popcount(IA), popcount(IR)) and Z == comb(ia + ir, ia)
                assert sw[0] == (A, R) and len(sw) == len(set(sw)) == Z                     # injective
                assert all(Q in pset for Q in sw)                                           # exact-size empty pairs
                assert all(popcount(Q[0]) == popcount(A) and popcount(Q[1]) == popcount(R)
                           and is_empty_pair(adj, *Q) for Q in sw)
                assert 1 <= Z <= X and 1 <= Zm[(A, R)] <= X
            Yf = weighted_count(ps, lambda P: flip_count(adj, *P)[2])
            Ym = weighted_count(ps, lambda P: Zm[P])
            assert 1 <= Yf <= X and Ym == len(size) <= X                                    # Lemma W
    with pytest.raises(ValueError):
        weighted_count([(1, 2)], lambda P: 0)


# --- item 09: the weighted count's lower tail -------------------------------------

from learning.separator_moment import (  # noqa: E402
    beta_closed, beta_star_gnp, beta_weighted, enumerate_empty_pairs, forced_sizes, gnp_masks, log_pair_count,
    log_weighted_bound, plant_pair, recombination_pairs, recombinations, side_avoiders, vertex_separation, z_hat0,
    z_hat_exponent, z_hat_log_laplace, z_recomb,
)


def _all_graphs(n):
    pairs = list(combinations(range(n), 2))
    for bits in range(1 << len(pairs)):
        adj = [0] * n
        for i, (u, v) in enumerate(pairs):
            if bits >> i & 1:
                adj[u] |= 1 << v
                adj[v] |= 1 << u
        yield adj


def test_recombination_lemma_on_every_labelled_graph_to_five():
    """Every recombined pair is an exact-size empty pair, distinct, not P₀; the
    closed-form count equals the explicit enumeration; Ẑ₀ ≤ Z ≤ X."""
    checked = 0
    for n in (4, 5):
        for adj in _all_graphs(n):
            for k in range(n):
                N, t = forced_sizes(n, k)
                r = N - t
                if min(t, r) < 2:
                    continue
                ex = set(enumerate_empty_pairs(adj, k))
                jm = min(4, min(t, r) - 1)
                for (A, R) in ex:
                    imgs = recombination_pairs(adj, A, R, jm)
                    cnt = recombinations(adj, A, R, jm)
                    assert len(imgs) == len(set(imgs)) == sum(cnt.values())
                    assert all(P in ex and P != (A, R) for P in imgs)
                    la, lr = side_avoiders(adj, A, R)
                    zfull = z_recomb(adj, A, R, min(max(jm, la, lr), min(t, r) - 1))
                    assert 1 <= z_hat0(adj, A, R) <= zfull <= len(ex)
                    checked += 1
    assert checked > 2000


def test_recombined_pairs_are_empty_on_planted_instances():
    """200 planted G(16, 6/16) instances at β*: every recombined pair is in the
    enumerated set of exact-size empty pairs, and Ẑ₀ ≤ Z_4 ≤ X."""
    n, c = 16, 6.0
    k = int(round(beta_star_gnp(c) * n))
    N, t = forced_sizes(n, k)
    r = N - t
    A = (1 << t) - 1
    R = ((1 << r) - 1) << t
    for i in range(200):
        adj = plant_pair(gnp_masks(n, c / n, 1000 + i), A, R)
        ex = set(enumerate_empty_pairs(adj, k))
        assert (A, R) in ex
        jm = min(4, min(t, r) - 1)
        imgs = recombination_pairs(adj, A, R, jm)
        assert all(P in ex for P in imgs) and (A, R) not in imgs
        assert len(set(imgs)) == len(imgs) == z_recomb(adj, A, R, jm) - 1
        la, lr = side_avoiders(adj, A, R)
        assert z_hat0(adj, A, R) <= z_recomb(adj, A, R, min(max(jm, la, lr), min(t, r) - 1)) <= len(ex)


def test_z_hat_laplace_against_the_planted_enumeration():
    """`E[1/Ẑ₀ | P₀ empty]` by the binomial double sum equals the average over
    every planted graph (all A–R edges deleted, the rest Bernoulli(p))."""
    from fractions import Fraction
    n, k, p = 6, 2, Fraction(1, 3)
    N, t = forced_sizes(n, k)
    r = N - t
    A = (1 << t) - 1
    R = ((1 << r) - 1) << t
    pairs = [(u, v) for u, v in combinations(range(n), 2) if not ((A >> u & 1 and R >> v & 1) or (R >> u & 1 and A >> v & 1))]
    total = Fraction(0)
    for bits in range(1 << len(pairs)):
        adj = [0] * n
        e = 0
        for i, (u, v) in enumerate(pairs):
            if bits >> i & 1:
                adj[u] |= 1 << v
                adj[v] |= 1 << u
                e += 1
        total += p ** e * (1 - p) ** (len(pairs) - e) / z_hat0(adj, A, R)
    assert abs(math.log(total) - z_hat_log_laplace(n, k, float(p))) < 1e-9


def test_weighted_bound_is_valid_on_every_labelled_graph_at_five():
    """`P(pw ≤ k) ≤ E[X] · E[1/Ẑ₀ | planted]` (Lemma W with Z = Ẑ₀) at p = 1/2 on
    every labelled graph with five vertices, every k; and the bound is below
    the pair count."""
    n = 5
    graphs = list(_all_graphs(n))
    for k in range(1, n - 2):
        N, t = forced_sizes(n, k)
        if min(t, N - t) < 1:
            continue
        prob = sum(1 for adj in graphs if vertex_separation(adj) <= k) / len(graphs)
        lw = log_weighted_bound(n, k, 0.5)
        assert math.log(prob) <= lw + 1e-12
        assert lw <= log_pair_count(n, k, 0.5) + 1e-12


def test_z_hat_exponent_is_the_closed_corner_and_beta_W_is_beta_closed():
    """The exponent of `E[1/Ẑ₀]` sits at the lower tail: within 0.001 nats of
    `2β ln q(a)` (the closed count's gain, §6.1 (b)), minimiser at λ ≈ 0; and
    `β_W(c)` is within 0.0005 of `β_closed(c)` at c = 6 and 10."""
    for c in (6.0, 10.0):
        b = beta_star_gnp(c)
        a = (1 - b) / 2
        corner = 2 * b * math.log(-math.expm1(-c * a))
        expo, lamA, lamR = z_hat_exponent(c, b, grid=100)
        assert corner - 1e-9 <= expo <= corner + 0.001
        assert lamA < 0.002 and lamR < 0.002
        assert abs(beta_weighted(c) - beta_closed(c)) < 5e-4


# ---------------------------------------------------------------------------
# loop0011 item 10: `lean/MOSPFormalization/SeparatorMoment.lean` against the Python
# ---------------------------------------------------------------------------

LEAN_FILE = Path(__file__).resolve().parents[1] / "lean" / "MOSPFormalization" / "SeparatorMoment.lean"


def test_separator_proved_names_are_theorems_in_the_lean_file():
    """Every name `learning.sandwich` audits for `SeparatorMoment.lean` is declared
    there as a theorem, and the file has no `sorry` and no `axiom`."""
    import learning.sandwich as sw
    src = LEAN_FILE.read_text()
    declared = set(re.findall(r"^theorem\s+([^\s:({\[]+)", src, re.M))
    missing = [n for n in sw.SEPARATOR_PROVED if n.split(".")[-1] not in declared]
    assert not missing, missing
    code = re.sub(r"/-.*?-/", "", src, flags=re.S)
    code = re.sub(r"--.*", "", code)
    assert "sorry" not in code
    assert not re.search(r"^\s*axiom\b", code, re.M)
    assert "SeparatorMoment" in (LEAN_FILE.parents[1] / "MOSPFormalization.lean").read_text()


def test_close_step_transcription_equals_close_pair():
    """`closeStep` as Lean defines it (`A` first) is item 03's `close_pair(..., 'A')`,
    is idempotent, and lands on a closed pair, on every labelled graph to 5 vertices
    and every `A`."""
    import learning.sandwich as sw
    for n in range(1, 6):
        for adj in all_labelled_graphs(n):
            full = (1 << n) - 1
            for A in range(1 << n):
                As, Rs = sw.close_step(adj, A)
                assert (As, Rs) == close_pair(adj, A, full & ~closed_nbhd(adj, A), "A")
                assert sw.close_step(adj, As) == (As, Rs)
                assert is_closed_pair(adj, As, Rs)
                assert A & As == A


def test_sees_both_is_the_closed_pair_characterisation():
    """`isClosedPair_iff_sees_both`: closed iff disjoint, empty and every outside vertex
    sees both sides, on every pair of disjoint sets of every labelled graph to 5 vertices."""
    import learning.sandwich as sw
    for n in range(1, 6):
        for adj in all_labelled_graphs(n):
            for A in range(1 << n):
                R = 0
                full = (1 << n) - 1
                rest = full & ~A
                sub = rest
                while True:
                    assert is_closed_pair(adj, A, sub) == sw.sees_both(adj, A, sub)
                    if sub == 0:
                        break
                    sub = (sub - 1) & rest


def test_separator_check_has_no_violations():
    import learning.sandwich as sw
    frame = sw.separator_check(n_graphs=60, seed=3)
    assert len(frame) >= 60
    assert frame.ok_L1.all() and frame.ok_L1prime.all() and frame.ok_L2.all()
    assert frame.ok_sees_both.all()
    summary = sw.separator_summary(frame)
    assert (summary["L1"] == summary["rows"]).all()


def test_three_k2_is_relaxed_and_not_bipartitioned_at_k_zero():
    """`not_isBalancedBip_threeK2` and `card_componentOff_threeK2_le`: at `k = 0`,
    `S = ∅`, `3K₂` is in `E_relax` and not in `E_bip`."""
    adj = [0] * 6
    for u, v in [(0, 3), (1, 4), (2, 5)]:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    bip, relax = separator_events(adj, 0, 0)
    assert relax and not bip
    assert count_exact_pairs(adj, 0) == 0
    assert all(popcount(c) <= 3 for c in components(adj, 63))


# --- item 11: the slack ledger ---------------------------------------------------

def test_harper_graph_is_a_lower_bound_on_vertex_separation():
    """`harper_bound_graph` (the graph form of Harper's bound, on the `vs`
    scale) never exceeds the exact vertex separation, at every cap."""
    from learning.separator_moment import harper_bound_graph, gnp_masks, layout_vertex_separation
    rng = random.Random(11)
    for trial in range(60):
        n = rng.randint(4, 9)
        adj = gnp_masks(n, rng.choice([0.2, 0.4, 0.6]), seed=rng.randint(0, 10**6))
        vs = vertex_separation(adj)
        for max_t in (1, 3, n - 1):
            hb = harper_bound_graph(adj, max_t=max_t, time_budget=None)
            assert hb.complete and hb.value <= vs, (adj, max_t, hb, vs)
            assert hb.levels == sorted(hb.levels)          # f is non-decreasing
            assert len(hb.levels) == min(max_t, n - 1) + 1
        full = harper_bound_graph(adj, max_t=n - 1, time_budget=None)
        # the layout form: every layout has a prefix of size i with ≥ i − M(i) active vertices
        assert full.value <= layout_vertex_separation(adj, list(range(n)))


def test_harper_graph_equals_expansion_bound_on_the_edge_cover():
    """On the MOSP instance whose patterns are the edges (one column per edge,
    one per isolated vertex) the MOSP graph is the graph, and
    `expansion_bound` returns the same levels, cap and value `+ 1`."""
    from mosp.instance import MOSPInstance
    from satisfiability.expansion_bound import expansion_bound
    from learning.separator_moment import harper_bound_graph, gnp_masks
    rng = random.Random(7)
    for trial in range(40):
        n = rng.randint(3, 10)
        adj = gnp_masks(n, rng.choice([0.25, 0.5]), seed=rng.randint(0, 10**6))
        cols = []
        for u in range(n):
            for v in range(u + 1, n):
                if (adj[u] >> v) & 1:
                    col = [0] * n
                    col[u] = col[v] = 1
                    cols.append(col)
            if adj[u] == 0:
                col = [0] * n
                col[u] = 1
                cols.append(col)
        inst = MOSPInstance.from_matrix(np.array(cols, dtype=np.int8).T, name=f"edges_{trial}")
        for max_t in (2, 4):
            eb = expansion_bound(inst, max_t=max_t, time_budget=None)
            hb = harper_bound_graph(adj, max_t=max_t, time_budget=None)
            assert hb.levels == eb.levels and hb.cap == eb.cap
            assert eb.value == (hb.value + 1 if hb.value else 0)


def test_floor_pw_convention_matches_the_record_minus_one():
    """`floor_pw` is the record's `floors` (optimum scale) minus one."""
    from learning.first_moment import floors, log_bound
    from learning.separator_moment import floor_pw
    assert floor_pw({0: -5.0, 1: -3.0, 2: -1.0, 3: 0.5}, 1.0) == 3
    assert floor_pw({0: -5.0, 1: -3.0, 2: -1.0, 3: 0.5}, 0.01) == 1
    assert floor_pw({0: 0.2, 1: 0.5}, 1.0) == 0
    n, sizes = 20, [4] * 20
    lb = {k: log_bound(n, sizes, k) for k in range(n)}
    f1, f2 = floors(n, sizes)
    assert floor_pw(lb, 1.0) == f1 - 1 and floor_pw(lb, 0.01) == f2 - 1


def test_layout_vertex_separation_of_an_optimal_layout_is_the_vertex_separation():
    from learning.separator_moment import gnp_masks, layout_vertex_separation
    from fixed_parameter_algorithm.pathwidth import compute_pathwidth
    rng = random.Random(3)
    for trial in range(20):
        n = rng.randint(4, 9)
        adj = gnp_masks(n, 0.4, seed=rng.randint(0, 10**6))
        G = nx.Graph()
        G.add_nodes_from(range(n))
        G.add_edges_from((u, v) for u in range(n) for v in range(u + 1, n) if (adj[u] >> v) & 1)
        pw, order = compute_pathwidth(G)
        assert layout_vertex_separation(adj, list(order)) == pw == vertex_separation(adj)
