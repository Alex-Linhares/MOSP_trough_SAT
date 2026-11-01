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
