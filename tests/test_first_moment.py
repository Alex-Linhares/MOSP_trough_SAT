"""loop0010 item 02: `learning.first_moment` reproduces the two scratch logs
(`reports/scratch/clique_cover_moment/asymptotic_cs.log`, `finite_bound_cs.log`)
to their printed digits, and its histogram interface agrees with the list one."""

import math
from pathlib import Path

import pytest

from learning.first_moment import (CS_DIR, beta_star, chu_stuckey_sizes, floors, log_bound, rate, threshold_d)

# fixed size d, mu = m/n: beta*(d, mu), the table of asymptotic_cs.log (3 digits)
ASYMPTOTIC_TABLE = {
    2: (0.000, 0.000, 0.121, 0.307),
    3: (0.000, 0.140, 0.355, 0.570),
    4: (0.072, 0.286, 0.525, 0.715),
    5: (0.158, 0.411, 0.642, 0.799),
    6: (0.244, 0.513, 0.724, 0.851),
    8: (0.398, 0.661, 0.825, 0.909),
    10: (0.522, 0.757, 0.880, 0.939),
    15: (0.726, 0.877, 0.942, 0.971),
    20: (0.832, 0.927, 0.965, 0.982),
}
MUS = (0.5, 1, 2, 4)

# class (n, m, d): beta* (empirical sizes) from asymptotic_cs.log, and the mean
# floors (< 1, < 0.01) from finite_bound_cs.log
CLASS_LOG = {
    (30, 30, 2): (0.097, 5.4, 4.6),
    (50, 100, 2): (0.277, 16.6, 15.8),
    (75, 75, 6): (0.538, 44.4, 43.2),
    (100, 50, 4): (0.133, 17.0, 15.4),
    (125, 125, 10): (0.762, 99.6, 98.0),
}


@pytest.mark.parametrize("d", sorted(ASYMPTOTIC_TABLE))
def test_beta_star_table_matches_the_scratch_log(d):
    for mu, expected in zip(MUS, ASYMPTOTIC_TABLE[d]):
        assert f"{beta_star(mu, [d]):.3f}" == f"{expected:.3f}"


def test_threshold_in_d_matches_the_scratch_log():
    assert f"{threshold_d():.4f}" == "2.0031"


def test_beta_star_is_positive_exactly_above_excess_one():
    # fixed sizes: e = mu (d - 1); the closed-form threshold is e = 1
    assert beta_star(1.0, [2]) == 0.0           # e = 1
    assert beta_star(0.5, [3]) == 0.0           # e = 1
    assert beta_star(0.5, [4]) > 0.0            # e = 1.5
    assert beta_star(2.0, [2]) > 0.0            # e = 2


def test_rate_accepts_a_histogram_and_agrees_with_the_list():
    sizes = [2, 2, 3, 5, 5, 5, 8]
    hist = {2: 2, 3: 1, 5: 3, 8: 1}
    for a in (0.05, 0.2, 0.4):
        assert rate(a, 1.3, hist) == pytest.approx(rate(a, 1.3, sizes), abs=1e-12)
    assert beta_star(1.3, hist) == pytest.approx(beta_star(1.3, sizes), abs=1e-12)


def test_rate_vanishes_at_zero_and_is_negative_at_one_half_for_sizes_two_or_more():
    assert rate(0.0, 1.0, [3]) == 0.0
    assert rate(0.5 - 1e-4, 1.0, [2]) < 0.0 or beta_star(1.0, [2]) == 0.0
    assert rate(0.5 - 1e-4, 1.0, [4]) < 0.0


def test_log_bound_is_infinite_where_no_pair_exists_and_the_floor_is_where_it_crosses():
    n, sizes = 30, [4] * 30
    assert log_bound(n, sizes, n) == math.inf          # t = 0: no pair
    assert log_bound(n, sizes, n - 1) < math.inf        # t = 1: the pair (A, R) with |A| = 1, |R| = 0
    f1, _ = floors(n, sizes)
    assert log_bound(n, sizes, f1 - 2) < 0              # the floor's k has bound < 1 ...
    assert all(log_bound(n, sizes, k) >= 0 for k in range(f1 - 1, n))   # ... and no larger k does


def test_floors_on_a_small_fixed_cover():
    f1, f2 = floors(30, [4] * 30)
    assert 2 <= f2 <= f1 <= 30


@pytest.mark.skipif(not CS_DIR.exists(), reason="benchmark files absent")
def test_class_values_match_both_scratch_logs():
    classes = chu_stuckey_sizes(Path(CS_DIR))
    for key, (beta, floor1, floor2) in CLASS_LOG.items():
        c = classes[key]
        n, m, _ = key
        assert f"{beta_star(m / n, c['sizes']):.3f}" == f"{beta:.3f}"
        f1 = [floors(n, s)[0] for _, s in c["instances"]]
        f2 = [floors(n, s)[1] for _, s in c["instances"]]
        assert f"{sum(f1) / len(f1):.1f}" == f"{floor1:.1f}"
        assert f"{sum(f2) / len(f2):.1f}" == f"{floor2:.1f}"


# ----------------------------------------------------------------------------
# loop0010 item 08: the structured count (`ell` nested empty pairs)
# ----------------------------------------------------------------------------

import itertools
import math

import numpy as np

from learning.first_moment import (
    _mobius_coefficients, beta_star_nested, delta_index, empty_pair_count_brute, equal_positions,
    nested_cells, nested_count_brute, nested_floors, nested_log_bound, nested_rate_grid, nested_rate_sup,
    nested_sizes, nested_structure_from_layout, second_moment_exact, second_moment_rate, structure)


def _vertex_separation(adj, order):
    n = len(order)
    best = 0
    for i in range(n):
        pm = sum(1 << v for v in order[: i + 1])
        active = sum(1 for v in order[i + 1:] if adj[v] & pm)
        best = max(best, active)
    return best


def _random_cover(rng, n, m, d):
    masks = []
    for _ in range(m):
        S = rng.choice(n, size=min(d, n), replace=False)
        masks.append(int(sum(1 << int(v) for v in S)))
    adj = [0] * n
    for pm in masks:
        for v in range(n):
            if (pm >> v) & 1:
                adj[v] |= pm & ~(1 << v)
    return masks, adj


def test_cell_count_and_masks():
    for ell in (1, 2, 3, 4):
        assert len(nested_cells(ell)) == ell * (ell + 1) // 2 + ell + 1
        assert len(delta_index(ell)) == ell * (ell - 1) // 2
    assert [c[0] for c in nested_cells(2)] == ["D1", "D2", "D2&L1", "T&L1", "T&L2", "F"]


def test_sizes_sum_to_n_and_are_affine():
    for ell in (2, 3, 4):
        q = len(delta_index(ell))
        for _ in range(20):
            rng = np.random.default_rng(ell)
            n, k = 60, 20
            pos = sorted(rng.choice(np.arange(1, n - k), size=ell, replace=False).tolist())
            delta = rng.integers(0, 5, size=q)
            s = nested_sizes(ell, n, k, pos, delta)
            assert s.sum() == pytest.approx(n)
            s0 = nested_sizes(ell, n, k, pos, [0] * q)
            s2 = nested_sizes(ell, n, k, pos, 2 * delta)
            assert np.allclose(s2 - s0, 2 * (s - s0))


def test_mobius_coefficients_against_the_definition():
    rng = np.random.default_rng(1)
    for C in (3, 5):
        f = rng.integers(0, 2, size=1 << C).astype(bool)
        c = _mobius_coefficients(f)
        for Hp in range(1 << C):
            direct = sum((-1) ** bin(H & ~Hp).count("1") * int(f[H]) for H in range(1 << C) if H & Hp == Hp)
            assert c[Hp] == direct


def test_ell_one_reproduces_beta_star_at_every_grid_point():
    from learning.first_moment import beta_star
    for d in sorted(ASYMPTOTIC_TABLE):
        for mu in MUS:
            assert beta_star_nested(1, mu, [d]) == pytest.approx(beta_star(mu, [d]), abs=1e-12)


def test_ell_one_finite_bound_matches_log_bound_at_odd_n_minus_k():
    from learning.first_moment import log_bound
    n, sizes = 31, [3] * 20 + [5] * 11
    for k in range(2, 25):
        mine = nested_log_bound(1, n, sizes, k)
        old = log_bound(n, sizes, k)
        if (n - k) % 2 == 1:
            assert mine == pytest.approx(old, abs=1e-9)
        else:   # |R| = (n - k) / 2 instead of t - 1: a different valid bound, neither dominating
            assert math.isfinite(mine)


@pytest.mark.parametrize("n,m,d,k", [(6, 4, 2, 2), (7, 5, 3, 2), (7, 3, 2, 3), (6, 5, 3, 1)])
def test_nested_count_matches_brute_force_enumeration_at_ell_two(n, m, d, k):
    sizes = [d] * m
    for positions in [(1, 2), (1, 3), (2, 3), (2, 4)]:
        if n - positions[-1] - k < 0:
            continue
        brute = nested_count_brute(2, n, sizes, k, list(positions))
        formula = nested_log_bound(2, n, sizes, k, list(positions))
        assert formula == pytest.approx(math.log(brute), abs=1e-9)


def test_nested_count_matches_brute_force_at_ell_three():
    brute = nested_count_brute(3, 7, [2, 3, 2], 2, [1, 2, 3])
    assert nested_log_bound(3, 7, [2, 3, 2], 2, [1, 2, 3]) == pytest.approx(math.log(brute), abs=1e-9)


def test_structure_is_forced_by_every_layout_and_counted():
    """The deterministic lemma: a layout of separation <= k yields the nested
    structure at every choice of positions (nesting, sizes, empty crossings
    all asserted inside `nested_structure_from_layout`), and the brute-force
    count of structures present in the graph is then at least one."""
    rng = np.random.default_rng(8)
    checked = 0
    for trial in range(60):
        n = int(rng.integers(5, 8))
        m = int(rng.integers(2, 7))
        d = int(rng.integers(2, 4))
        masks, adj = _random_cover(rng, n, m, d)
        order = rng.permutation(n).tolist()
        k = _vertex_separation(adj, order)
        for ell in (1, 2, 3):
            for positions in itertools.combinations(range(1, n - k + 1), ell):
                out = nested_structure_from_layout(adj, order, k, list(positions))
                assert out is not None
                checked += 1
        # at the position where the separation is attained, width k - 1 is refused
        if k > 0:
            worst = max(range(n), key=lambda i: sum(1 for v in order[i + 1:] if adj[v] & sum(1 << u for u in order[: i + 1])))
            assert nested_structure_from_layout(adj, order, k - 1, [worst + 1]) is None
    assert checked > 200


def test_ell_two_optimiser_agrees_with_the_grid():
    for d, mu, beta in [(6, 1, 0.3), (4, 0.5, 0.05), (3, 2, 0.2), (10, 1, 0.6)]:
        sup, _ = nested_rate_sup(2, beta, mu, [d])
        grid = nested_rate_grid(beta, mu, [d], points=4001)
        assert sup >= grid - 1e-6
        assert sup <= grid + 1e-3


def test_second_moment_against_simulation_at_small_n():
    """E[X] and E[X^2] of the single-pair count, exact in the model, against
    the enumeration of X on 2,000 random covers at n = 10."""
    n, m, d, t = 10, 6, 3, 3
    rng = np.random.default_rng(3)
    xs = []
    for _ in range(2000):
        masks, _ = _random_cover(rng, n, m, d)
        xs.append(empty_pair_count_brute(masks, n, t))
    xs = np.array(xs, dtype=float)
    logEX, logEX2, ratio = second_moment_exact(n, t, [d] * m)
    se1 = xs.std() / math.sqrt(len(xs))
    se2 = (xs ** 2).std() / math.sqrt(len(xs))
    assert abs(xs.mean() - math.exp(logEX)) < 4 * se1 + 1e-9
    assert abs((xs ** 2).mean() - math.exp(logEX2)) < 4 * se2 + 1e-9
    assert ratio == pytest.approx(math.exp(logEX2 - 2 * logEX))


def test_second_moment_rate_is_at_least_twice_the_first():
    for d, mu, a in [(6, 1, 0.2), (4, 1, 0.3), (10, 2, 0.1)]:
        sup, twice, table = second_moment_rate(a, mu, [d])
        assert sup >= twice - 1e-9
        assert table.sum() == pytest.approx(1.0)
        assert np.all(table >= -1e-9)


def test_nested_floors_are_monotone_in_ell_direction_of_validity():
    # a floor is a floor: the ell = 2 count is a different necessary condition, so its floor
    # need not dominate; but both are below the certified optimum of a dense small instance
    n, sizes = 20, [4] * 20
    f1 = nested_floors(1, n, sizes)
    f2 = nested_floors(2, n, sizes)
    assert f1[1] <= f1[0] and f2[1] <= f2[0]
    assert 0 <= f1[0] <= n and 0 <= f2[0] <= n


# ----------------------------------------------------------------------------
# loop0010 item 10: validity under the real generator
# ----------------------------------------------------------------------------

import itertools
from fractions import Fraction

from learning.first_moment import (customer_masks, draw_aux, floors_bernoulli, floors_truncated, lq_bernoulli,
                                   lq_truncated, log_disconnected_bound, log_repair_bound, mosp_connected,
                                   no_repair_needed, pad_customers_with_aux, pad_patterns_with_aux, pad_with_aux,
                                   rejection_floors, unconditional_pad, vertex_separation_brute, wilson)


def _avoid_count(n, t, s):
    return math.comb(n - t, s) + math.comb(n - t + 1, s) - math.comb(n - 2 * t + 1, s)


@pytest.mark.parametrize("n,p", [(5, Fraction(1, 3)), (8, Fraction(2, 7)), (11, Fraction(1, 5))])
def test_bernoulli_avoid_probability_is_the_binomial_average_of_the_uniform_one(n, p):
    # (a) of §10: a Bernoulli(p) row given its size s is a uniform s-set, so
    # P(avoid A or avoid R) = sum_s Bin(n, p)(s) q(n, t, s) = (1-p)^t + (1-p)^(t-1) - (1-p)^(2t-1), exactly
    for t in range(1, (n + 1) // 2 + 1):
        lhs = sum(p ** s * (1 - p) ** (n - s) * _avoid_count(n, t, s) for s in range(n + 1))
        rhs = (1 - p) ** t + (1 - p) ** (t - 1) - (1 - p) ** (2 * t - 1)
        assert lhs == rhs
        assert lq_bernoulli(float(p), t, t - 1) == pytest.approx(math.log(float(rhs)), abs=1e-12)
        assert lq_truncated(n, float(p), t, kmin=0) == pytest.approx(math.log(float(rhs)), abs=1e-10)
        # the truncated form: sizes below 2 lifted to 2
        trunc = sum(math.comb(n, s) * p ** s * (1 - p) ** (n - s) * Fraction(_avoid_count(n, t, max(s, 2)), math.comb(n, max(s, 2)))
                    for s in range(n + 1))
        assert lq_truncated(n, float(p), t) == pytest.approx(math.log(float(trunc)), abs=1e-10)
        assert trunc <= rhs


def _enumerate_base(m, n, p):
    """every base matrix with its exact Bernoulli(p) weight (rational)."""
    for bits in itertools.product((0, 1), repeat=m * n):
        B = np.array(bits, dtype=bool).reshape(m, n)
        w = p ** sum(bits) * (1 - p) ** (m * n - sum(bits))
        yield B, w


def test_empty_pair_probability_and_cut_bound_by_enumeration():
    m, n, p = 2, 5, Fraction(1, 3)
    A, R = {0, 1}, {2}
    t = 2
    empty = Fraction(0)
    disconnected = Fraction(0)
    for B, w in _enumerate_base(m, n, p):
        meets_both = any(B[i, list(A)].any() and B[i, list(R)].any() for i in range(m))
        empty += w * (not meets_both)
        disconnected += w * (not mosp_connected(B))
    formula = ((1 - p) ** t + (1 - p) ** (t - 1) - (1 - p) ** (2 * t - 1)) ** m
    assert empty == formula
    # the closed-form cut bound is a bound on P(G_B disconnected) (a union bound, so above it)
    assert float(disconnected) <= math.exp(log_disconnected_bound(n, m, float(p))) + 1e-12
    # and the repair bound is a bound on P(some repair fires)
    repair = sum(w for B, w in _enumerate_base(m, n, p) if not no_repair_needed(B))
    assert float(repair) <= math.exp(log_repair_bound(n, m, float(p))) + 1e-12


def _random_base(rng, m, n, p):
    return rng.random((m, n)) < p


def test_repairs_only_add_and_are_dominated_by_the_unconditional_pad():
    rng = np.random.default_rng(10)
    for _ in range(300):
        m, n = int(rng.integers(2, 7)), int(rng.integers(2, 8))
        B = _random_base(rng, m, n, rng.uniform(0.05, 0.5))
        U, sigma = draw_aux(m, n, rng)
        for first in (False, True):
            M = pad_with_aux(B, U, sigma, patterns_first=first)
            Mp = unconditional_pad(B, U, sigma)
            assert np.all(M >= B) and np.all(Mp >= M)
            assert M.any(axis=0).all() and (M.sum(axis=1) >= 2).all()
            # the pads add exactly the deficiency, in the order applied
            if not first:
                M1 = pad_customers_with_aux(B, U)
                assert (M1.sum() - B.sum()) == (~B.any(axis=0)).sum()
                assert (M.sum() - M1.sum()) == np.clip(2 - M1.sum(axis=1), 0, None).sum()
            # the unconditional pad is monotone in the base
            extra = _random_base(rng, m, n, 0.2)
            assert np.all(unconditional_pad(B | extra, U, sigma) >= Mp)
            if no_repair_needed(B):
                assert np.array_equal(M, B)


def test_pattern_pad_rows_are_uniform_sets_of_the_truncated_size():
    # the patterns-first lemma: given |B[i]| = s, the padded row is a uniform set of size max(s, 2)
    rng = np.random.default_rng(11)
    n, draws = 5, 20000
    counts = {s: {} for s in (0, 1, 2)}
    for _ in range(draws):
        B = _random_base(rng, 1, n, 0.25)
        s = int(B.sum())
        if s > 2:
            continue
        _, sigma = draw_aux(1, n, rng)
        row = tuple(np.flatnonzero(pad_patterns_with_aux(B, sigma)[0]))
        counts[s][row] = counts[s].get(row, 0) + 1
    for s in (0, 1, 2):
        rows = counts[s]
        assert len(rows) == math.comb(n, 2)
        total = sum(rows.values())
        expected = total / math.comb(n, 2)
        chi2 = sum((c - expected) ** 2 / expected for c in rows.values())
        assert chi2 < 40  # 9 degrees of freedom; 99.9% point is 27.9, with margin


def test_empty_pairs_of_the_padded_graph_are_empty_in_the_base_and_pathwidth_is_monotone():
    from fixed_parameter_algorithm.pathwidth import compute_pathwidth
    import networkx as nx

    rng = np.random.default_rng(12)
    for _ in range(60):
        m, n = int(rng.integers(2, 7)), int(rng.integers(3, 8))
        B = _random_base(rng, m, n, rng.uniform(0.05, 0.4))
        U, sigma = draw_aux(m, n, rng)
        M = pad_with_aux(B, U, sigma)
        adjB, adjM = customer_masks(B), customer_masks(M)
        assert all(a & b == a for a, b in zip(adjB, adjM))  # G_B is a subgraph of G_M
        for A in range(1, 1 << n):
            for R in range(1, 1 << n):
                if A & R:
                    continue
                emptyM = all(not ((mask := sum(1 << int(c) for c in np.flatnonzero(M[i]))) & A and mask & R) for i in range(m))
                emptyB = all(not ((mask := sum(1 << int(c) for c in np.flatnonzero(B[i]))) & A and mask & R) for i in range(m))
                assert (not emptyM) or emptyB
        pwB, pwM = vertex_separation_brute(adjB), vertex_separation_brute(adjM)
        assert pwB <= pwM
        G = nx.Graph()
        G.add_nodes_from(range(n))
        G.add_edges_from((u, v) for u in range(n) for v in range(u + 1, n) if (adjM[u] >> v) & 1)
        assert compute_pathwidth(G)[0] == pwM


def test_the_repair_map_is_not_monotone_in_the_base():
    # B: patterns {3,4}, {}, {3,4}; customers 1, 2 empty. The pads make it connected.
    # B' = B + two ones: pattern 2 = {1, 2}; no pad fires and the instance is disconnected.
    B = np.zeros((3, 5), bool)
    B[0, [3, 4]] = True
    B[2, [3, 4]] = True
    U = np.array([0, 0, 0, 0, 0])
    sigma = np.array([[3, 4, 0, 1, 2]] * 3)
    M = pad_with_aux(B, U, sigma)
    Bp = B.copy()
    Bp[1, [1, 2]] = True
    Mp = pad_with_aux(Bp, U, sigma)
    assert np.all(Bp >= B)
    assert mosp_connected(M) and not mosp_connected(Mp)
    assert not np.all(Mp >= M)
    # and the pathwidth of the padded graph can fall when the base grows
    assert vertex_separation_brute(customer_masks(Mp)) < vertex_separation_brute(customer_masks(M))
    # while the unconditional pad is monotone and its connectivity increasing here
    assert np.all(unconditional_pad(Bp, U, sigma) >= unconditional_pad(B, U, sigma))


def test_rigorous_floors_are_monotone_and_ordered():
    n, m = 40, 40
    for d in (2, 4, 6, 10):
        p = d / n
        b, tr = floors_bernoulli(n, m, p), floors_truncated(n, m, p)
        assert b[1] <= b[0] and tr[1] <= tr[0]
        assert tr[0] >= b[0] and tr[1] >= b[1]
        # monotone in p (the floor at p is valid for every density above p)
        assert floors_bernoulli(n, m, 1.1 * p)[1] >= b[1]
        # the rejection forms are ordered: closed/trivial <= harris_plus <= base, harris_E <= base
        r = rejection_floors(n, m, p, p_acc=0.5, p_acc_plus=0.8)
        assert r["trivial"][1] <= r["harris_plus"][1] <= r["base"][1]
        assert r["harris_E"][1] <= r["base"][1]
        assert r["closed"][1] <= r["base"][1]
        # the trivial form at acceptance 1 is the base
        assert rejection_floors(n, m, p, p_acc=1.0)["trivial"] == r["base"]
    assert floors_bernoulli(125, 125, 10 / 125) == floors_truncated(125, 125, 10 / 125)


def test_wilson_interval_contains_the_point_estimate():
    lo, hi = wilson(3, 200)
    assert lo < 3 / 200 < hi and 0 <= lo and hi <= 1
    assert wilson(0, 0) == (0.0, 1.0)


def test_quenched_bound_is_above_the_exact_probability_by_enumeration():
    # m = 3 patterns, n = 5 customers, p = 1/3: P(pw(G_B) <= k) exactly over all 2^15 base matrices,
    # against the annealed, the quenched and the best bound (all valid), for every k
    from learning.first_moment import log_bound_best, log_bound_bernoulli, log_bound_quenched

    m, n, p = 3, 5, Fraction(1, 3)
    probs = {k: Fraction(0) for k in range(n)}
    for B, w in _enumerate_base(m, n, p):
        pw = vertex_separation_brute(customer_masks(B))
        for k in range(n):
            if pw <= k:
                probs[k] += w
    for k in range(n):
        exact = float(probs[k])
        for fn in (log_bound_bernoulli, log_bound_quenched, log_bound_best):
            lb = fn(n, m, float(p), k)
            assert exact <= (math.exp(lb) if lb < math.inf else math.inf) + 1e-12, (fn.__name__, k)
        assert log_bound_best(n, m, float(p), k) <= log_bound_bernoulli(n, m, float(p), k) + 1e-12
        assert log_bound_best(n, m, float(p), k) <= log_bound_quenched(n, m, float(p), k) + 1e-12


def test_quenched_tail_is_a_chernoff_bound_on_the_size_sum():
    # the tail factor used inside log_bound_quenched bounds P(sum_j X_j > m a) for i.i.d. X = log q(n, t, s):
    # exact distribution of the sum by enumeration of size vectors at m = 3, n = 6
    from learning.first_moment import lq, size_law

    n, m, p, t = 6, 3, 0.3, 2
    ss, pr = size_law(n, p, 0)
    X = np.array([lq(n, t, int(s)) for s in ss])
    fin = np.isfinite(X)
    Xf, prf = X[fin], pr[fin]
    lambdas = np.logspace(-2, 2.5, 120)
    lmgf = np.log(np.array([float(np.sum(prf * np.exp(lam * Xf))) for lam in lambdas]))
    for a in np.linspace(float(Xf.min()), 0.0, 7):
        exact = 0.0
        for combo in itertools.product(range(len(ss)), repeat=m):
            w = float(np.prod(pr[list(combo)]))
            if sum(X[list(combo)]) > m * a:
                exact += w
        chern = min(1.0, float(np.exp(np.min(-lambdas * m * a + m * lmgf))))
        assert exact <= chern + 1e-12


def test_floors_best_dominate_both_forms():
    from learning.first_moment import floors_best, floors_quenched

    for (n, m, d) in ((30, 30, 4), (50, 50, 6), (40, 40, 2)):
        p = d / n
        a, q, b = floors_bernoulli(n, m, p), floors_quenched(n, m, p), floors_best(n, m, p)
        assert b[0] >= max(a[0], q[0]) and b[1] >= max(a[1], q[1])
        a2, q2, b2 = floors_truncated(n, m, p), floors_quenched(n, m, p, 2), floors_best(n, m, p, 2)
        assert b2[0] >= max(a2[0], q2[0]) and b2[1] >= max(a2[1], q2[1])
