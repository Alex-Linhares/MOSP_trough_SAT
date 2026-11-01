"""`learning.excess_constructions` (loop0010 item 05): the sweeps against the
reference implementations, the constructions' bounds, the generators' seeds,
and the fit."""
from __future__ import annotations

import numpy as np
import pytest

from learning import excess_constructions as ec
from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from satisfiability.heuristics import two_key_rule


def _random_matrix(rng, n_lo=2, n_hi=15):
    n, m = int(rng.integers(n_lo, n_hi)), int(rng.integers(2, n_hi))
    return (rng.random((n, m)) < rng.uniform(0.1, 0.6)).astype(np.int8)


def _brute_vertex_separation(adj_dense: np.ndarray, order: np.ndarray) -> int:
    n = len(order)
    best = 0
    for i in range(n):
        prefix, suffix = order[: i + 1], order[i + 1:]
        best = max(best, sum(bool(adj_dense[v, suffix].any()) for v in prefix))
    return best


def test_max_open_stacks_fast_agrees_with_reference():
    rng = np.random.default_rng(1)
    for _ in range(200):
        matrix = _random_matrix(rng)
        inst = MOSPInstance.from_matrix(matrix)
        order = rng.permutation(matrix.shape[1])
        assert ec.max_open_stacks_fast(matrix, order) == max_open_stacks(inst, list(order))


def test_vertex_separation_agrees_with_brute_force():
    rng = np.random.default_rng(2)
    for _ in range(200):
        matrix = _random_matrix(rng)
        adj = ec.mosp_adjacency(matrix)
        order = rng.permutation(matrix.shape[0])
        assert ec.vertex_separation(adj, order) == _brute_vertex_separation(adj.toarray().astype(bool), order)


def test_rule_width_is_two_key_rule():
    rng = np.random.default_rng(3)
    for _ in range(100):
        matrix = _random_matrix(rng)
        inst = MOSPInstance.from_matrix(matrix)
        assert ec.two_key_rule_width(inst)[0] == two_key_rule(inst)[0]


def test_mosp_adjacency_is_the_customer_graph():
    matrix = np.array([[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1], [0, 0, 0, 0]], dtype=np.int8)
    adj = ec.mosp_adjacency(matrix).toarray()
    expected = np.array([[0, 1, 0, 0], [1, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 0]])
    assert (adj == expected).all()
    assert ec.edge_count(ec.mosp_adjacency(matrix)) == 2


def test_bfs_layers_cover_every_vertex_once_and_layer_bound_dominates_vs():
    rng = np.random.default_rng(4)
    for _ in range(100):
        matrix = _random_matrix(rng, 2, 25)
        adj = ec.mosp_adjacency(matrix)
        layers = ec.bfs_layers(adj, np.random.default_rng(0))
        order = np.concatenate(layers)
        assert sorted(order.tolist()) == list(range(matrix.shape[0]))
        vs, bound, n_layers = ec.bfs_layout(adj, np.random.default_rng(0))
        assert n_layers == len(layers)
        assert vs <= bound
        # consecutive layers of one BFS tree: every edge joins vertices at most one layer apart
        layer_of = np.empty(matrix.shape[0], dtype=int)
        for i, layer in enumerate(layers):
            layer_of[layer] = i
        dense = adj.toarray().astype(bool)
        for u, v in zip(*np.nonzero(np.triu(dense))):
            assert abs(layer_of[u] - layer_of[v]) <= 1


def test_greedy_independent_set_is_independent_and_maximal():
    rng = np.random.default_rng(5)
    for _ in range(100):
        matrix = _random_matrix(rng, 2, 25)
        adj = ec.mosp_adjacency(matrix)
        dense = adj.toarray().astype(bool)
        n = matrix.shape[0]
        # replay the greedy to recover the set, then check it
        alpha = ec.greedy_independent_set(adj)
        chosen: list[int] = []
        alive = np.ones(n, dtype=bool)
        deg = dense.sum(axis=1).astype(float)
        while alive.any():
            key = np.where(alive, deg, np.inf)
            v = int(np.argmin(key))
            chosen.append(v)
            closed = np.flatnonzero(dense[v]).tolist() + [v]
            closed = [u for u in closed if alive[u]]
            alive[closed] = False
            for u in closed:
                deg[dense[u]] -= 1
        assert alpha == len(chosen)
        for u in chosen:
            for v in chosen:
                assert u == v or not dense[u, v]
        covered = np.zeros(n, dtype=bool)
        for u in chosen:
            covered[u] = True
            covered[dense[u]] = True
        assert covered.all()


def test_constructions_on_small_instance_bounds(tmp_path):
    """On a graph with a known pathwidth the proved constructions are above it
    and the rule reproduces the certified optimum minus one."""
    from satisfiability import solve_mosp_exact
    rng = np.random.default_rng(6)
    for _ in range(20):
        matrix = _random_matrix(rng, 4, 12)
        inst = MOSPInstance.from_matrix(matrix)
        opt, _ = solve_mosp_exact(inst, solutions_dir=tmp_path)
        row = ec.constructions_on(matrix, seed=0)
        assert row["rule_stacks"] == two_key_rule(inst)[0]
        assert row["rule"] == row["rule_stacks"] - 1
        # every layout's width and n - alpha are upper bounds on the pathwidth = opt - 1
        assert row["rule"] >= opt - 1
        assert row["bfs_vs"] >= opt - 1
        assert row["bfs_layer_bound"] >= row["bfs_vs"]
        assert row["n_minus_alpha"] >= opt - 1
        assert row["edges"] == ec.edge_count(ec.mosp_adjacency(matrix))
        assert row["n_ones"] == int(matrix.sum())


def test_draws_are_reproducible_and_have_the_right_shape():
    a, _ = ec.draw_fixed(40, 0.5, 3, seed=11)
    b, _ = ec.draw_fixed(40, 0.5, 3, seed=11)
    assert a.shape == (40, 20) and (a == b).all()
    assert (a.sum(axis=0) >= 3).all() and (a.sum(axis=1) >= 1).all()
    c, tries = ec.draw_fitted(40, 1.0, 4, seed=11, cap=200)
    d, tries2 = ec.draw_fitted(40, 1.0, 4, seed=11, cap=200)
    assert c is not None and c.shape == (40, 40) and (c == d).all() and tries == tries2
    assert (c.sum(axis=1) >= 1).all() and (c.sum(axis=0) >= 2).all()
    assert ec.cell_seed("fixed", 100, 0.5, 2, 3) != ec.cell_seed("fitted", 100, 0.5, 2, 3)
    assert ec.cell_seed("fixed", 100, 0.5, 2, 3) == ec.cell_seed("fixed", 100, 0.5, 2, 3)


def test_fit_beta_plus_recovers_a_synthetic_law():
    ns = np.array([100, 200, 500, 1000, 2000, 5000] * 3, dtype=float)
    width = 0.37 * ns + 12.0
    beta, se, a, _ = ec.fit_beta_plus(ns, width)
    assert beta == pytest.approx(0.37, abs=1e-9)
    assert a == pytest.approx(12.0, abs=1e-6)
    assert se == pytest.approx(0.0, abs=1e-9)
    assert np.isnan(ec.fit_beta_plus(np.array([100.0, 200.0]), np.array([1.0, 2.0]))[0])


def test_tables_on_a_synthetic_frame(monkeypatch):
    import pandas as pd
    rows = []
    for gen in ("fixed", "fitted"):
        for n in (100, 200, 500):
            for i in range(2):
                r = ec.constructions_on(ec.draw_fixed(n, 1.0, 4, seed=i)[0], seed=i)
                r.update({"generator": gen, "n": n, "mu": 1.0, "d": 4, "index": i, "seed": i, "tries": 1,
                          "accepted": True, "draw_seconds": 0.0, "seconds": 0.0})
                rows.append(r)
    rows.append({"generator": "fitted", "n": 1000, "mu": 1.0, "d": 2, "index": 0, "seed": 0, "tries": 5,
                 "accepted": False, "draw_seconds": 0.1})
    frame = pd.DataFrame(rows)
    slopes = pd.DataFrame([{"generator": "fixed", "mu": 1.0, "d": 4, "b": 0.35, "se_b": 0.003,
                            "b_source": "test", "rule_n_small": 0.45, "opt_n_small": 0.38, "small_max_n": 100}])
    monkeypatch.setattr(ec, "certified_slopes", lambda: slopes)
    cells = ec.cell_table(frame)
    assert len(cells) == 2
    fixed = cells[cells["generator"] == "fixed"].iloc[0]
    assert fixed["b (certified, n <= 100)"] == 0.35
    assert np.isfinite(fixed["rule beta+"]) and np.isfinite(fixed["n_minus_alpha beta+"])
    fitted = cells[cells["generator"] == "fitted"].iloc[0]
    assert np.isnan(fitted["b (certified, n <= 100)"]) and fitted["kill"] == "no certified b"
    text = ec.tables(frame)
    assert "NOT trusted" in text and "untested" in text and "fitted (4, 1)" in text
    assert len(ec.rejected_table(frame)) == 1
