"""`learning.beta_plus` (loop0010 item 07): the layer lemma against brute
force, the recursions against their `G(n, c/n)` specialisations and closed
forms, the greedy simulations' witnesses, and the ODEs against simulation on
the unpadded uniform model."""
from __future__ import annotations

import math

import numpy as np
import pytest
from scipy.sparse import csr_matrix

from learning import beta_plus as bp
from learning import excess_constructions as ec


def _pure(n, mu, d, seed):
    rng = np.random.default_rng(seed)
    m = int(round(mu * n))
    mat = np.zeros((n, m), dtype=np.int8)
    for j in range(m):
        mat[rng.choice(n, size=d, replace=False), j] = 1
    return mat


def _brute_vertex_separation(dense: np.ndarray, order: np.ndarray) -> int:
    best = 0
    for i in range(len(order)):
        prefix, suffix = order[: i + 1], order[i + 1:]
        best = max(best, sum(bool(dense[v, suffix].any()) for v in prefix))
    return best


def test_layer_lemma_against_brute_force_vertex_separation():
    rng = np.random.default_rng(11)
    tight = 0
    for _ in range(150):
        n = int(rng.integers(2, 12))
        dense = np.triu(rng.random((n, n)) < rng.uniform(0.1, 0.7), 1)
        dense = dense | dense.T
        comps = bp.bfs_components(csr_matrix(dense.astype(np.int8)), rng)
        order = np.concatenate([layer for layers in comps for layer in layers])
        assert sorted(order.tolist()) == list(range(n))
        vs = _brute_vertex_separation(dense, order)
        bound = bp.layer_layout_bound(comps)
        assert vs <= bound
        tight += vs == bound
    assert tight > 0


def test_layer_lemma_check_runs_clean():
    assert bp.layer_lemma_check(60, np.random.default_rng(3))["checked"] == 60


def test_bfs_components_match_item05_layers():
    """The same random choices as item 05's `bfs_layers`, so the concatenation is its layout."""
    mat = _pure(60, 1.0, 3, 5)
    adj = ec.mosp_adjacency(mat)
    ours = [layer for layers in bp.bfs_components(adj, np.random.default_rng(9)) for layer in layers]
    theirs = ec.bfs_layers(adj, np.random.default_rng(9))
    assert len(ours) == len(theirs)
    for a, b in zip(ours, theirs):
        assert np.array_equal(a, b)
    vs, bound, _ = ec.bfs_layout(adj, np.random.default_rng(9))
    assert bound == bp.layer_layout_bound(bp.bfs_components(adj, np.random.default_rng(9))) >= vs


def test_uniform_recursion_is_gnp_recursion_at_d_two():
    for mu in (0.5, 1.0, 2.0):
        ours = bp.bfs_recursion_uniform(mu, 2, 1.0, 1 - 1e-4)
        gnp = bp.gnp_recursion(2 * mu, 1 - 1e-4, 1e-4)
        assert max(abs(a - b) for a, b in zip(ours[:40], gnp[:40])) < 1e-12


def test_general_recursion_reduces_to_uniform_for_poisson_degrees():
    mu, d, eps = 1.0, 4, 1e-7
    deg, sizes = bp.uniform_model_histograms(mu, d)
    ek = sum(k * v for k, v in deg.items())
    general = bp.bfs_recursion(deg, sizes, eps * ek, deg_unreached={k: v * (1 - eps) for k, v in deg.items()},
                               sizes_unrevealed=sizes)
    uniform = bp.bfs_recursion_uniform(mu, d, 1.0, 1 - eps)
    assert max(abs(a - b) for a, b in zip(general[:15], uniform[:15])) < 1e-6
    assert abs(bp.layer_max([eps] + general) - bp.layer_max([eps] + uniform)) < 1e-6


def test_phase_scan_is_periodic_and_bounded():
    deg, sizes = bp.uniform_model_histograms(1.0, 4)
    a = bp.bfs_phase_scan(deg, sizes, phases=16, eps=1e-7)
    b = bp.bfs_phase_scan(deg, sizes, phases=16, eps=1e-7 / a["rho"])   # one period earlier
    assert abs(a["rho"] - 12.0) < 1e-6
    assert 0 < a["inf"] <= a["mean"] <= a["sup"] <= 1
    assert abs(a["sup"] - b["sup"]) < 1e-5 and abs(a["inf"] - b["inf"]) < 1e-5


def test_random_greedy_closed_form_at_d_two_is_log_one_plus_c_over_c():
    for mu in (0.5, 1.0, 2.0):
        c = 2 * mu
        assert abs(bp.random_greedy_uniform(mu, 2) - math.log(1 + c) / c) < 1e-6


def test_random_greedy_ode_matches_closed_form():
    for mu, d in ((1.0, 2), (1.0, 4), (0.5, 6), (2.0, 3)):
        deg, sizes = bp.uniform_model_histograms(mu, d)
        assert abs(bp.greedy_ode(deg, sizes, "random")["alpha"] - bp.random_greedy_uniform(mu, d)) < 2e-4


def test_greedy_simulations_return_maximal_independent_sets():
    rng = np.random.default_rng(4)
    for _ in range(30):
        n, m = int(rng.integers(3, 30)), int(rng.integers(2, 30))
        mat = (rng.random((n, m)) < 0.2).astype(np.int8)
        for policy in ("pattern_count", "random"):
            alpha, chosen = bp.greedy_simulation(mat, policy, rng)
            assert alpha == len(chosen) and bp.is_independent(mat, chosen)
            taken = np.zeros(n, dtype=bool)
            taken[chosen] = True
            conflict = mat[chosen].sum(axis=0) > 0          # patterns met by the set
            for v in np.flatnonzero(~taken):
                assert (mat[v].astype(bool) & conflict).any(), "greedy left an addable customer"


def test_greedy_odes_against_simulation_on_the_uniform_model():
    n = 8000
    for mu, d in ((1.0, 3), (0.5, 4), (2.0, 6)):
        mat = _pure(n, mu, d, 21)
        deg, sizes = bp.degree_and_size_histograms(mat)
        for policy, tol in (("pattern_count", 0.02), ("random", 0.03)):
            sim, _ = bp.greedy_simulation(mat, policy, np.random.default_rng(1))
            ode = bp.greedy_ode(deg, sizes, policy)["alpha"]
            assert abs(sim / n - ode) / ode < tol, (mu, d, policy, sim / n, ode)


def test_bfs_recursion_against_simulation_on_the_uniform_model():
    n = 8000
    mat = _pure(n, 1.0, 4, 8)
    adj = ec.mosp_adjacency(mat)
    comps = bp.bfs_components(adj, np.random.default_rng(8))
    state = bp.bfs_state(mat, comps, min_layer=16)
    assert state is not None
    pred = bp.bfs_recursion(state["deg_unreached"], state["sizes_unrevealed"], state["slots_layer"],
                            deg_unreached=state["deg_unreached"], sizes_unrevealed=state["sizes_unrevealed"])
    observed = state["observed_after"]
    k = min(3, len(observed))
    for o, p in zip(observed[:k], pred[:k]):
        assert abs(o - p) < 0.03, (observed, pred)
    largest = max(comps, key=lambda ls: sum(len(x) for x in ls))
    obs_max = bp.layer_max([len(x) / n for x in largest])
    pred_max = bp.layer_max(state["observed_before"] + pred)
    assert abs(obs_max - pred_max) / obs_max < 0.03


def test_fixed_generator_histograms_are_laws():
    deg, sizes = bp.fixed_generator_histograms(1.0, 4)
    assert 0 not in deg and abs(sum(deg.values()) - 1) < 1e-9
    assert min(sizes) == 4 and abs(sum(sizes.values()) - 1.0) < 1e-9
    assert abs(sum(k * v for k, v in deg.items()) - sum(s * v for s, v in sizes.items())) < 1e-6


def test_growth_factor_is_mu_d_d_minus_one_for_the_uniform_model():
    for mu, d in ((1.0, 4), (0.5, 3), (2.0, 10)):
        deg, sizes = bp.uniform_model_histograms(mu, d)
        assert abs(bp.growth_factor(deg, sizes) - mu * d * (d - 1)) < 1e-6


def test_padded_layers_add_leaves_and_keep_the_growth_factor():
    """The fixed generator's limit: the uniform orbit plus `e^{-mu d}` leaves
    per revealed pattern; nothing at the critical cell `(2, 1/2)`, and
    indistinguishable from the uniform model where `e^{-mu d}` is negligible."""
    assert bp.padded_phase_scan(0.5, 2)["sup"] < 1e-5          # critical: no giant component
    dense_u = bp.bfs_phase_scan(*bp.uniform_model_histograms(2.0, 10), phases=8)
    dense_p = bp.padded_phase_scan(2.0, 10, phases=8)
    assert abs(dense_u["sup"] - dense_p["sup"]) < 1e-6
    eps = 1e-7
    padded = bp.padded_layers(1.0, 2, eps)
    uniform = [eps] + bp.bfs_recursion_uniform(1.0, 2, 1.0, 1.0 - eps)
    assert all(p >= u for p, u in zip(padded, uniform))
    assert abs(sum(padded) - sum(uniform) - math.exp(-2.0) * (1 - (1 - sum(uniform)) ** 2)) < 1e-6
