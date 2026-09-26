"""Tests for learning.treewidth and learning.extremal (loop0003 item 08)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from learning import extremal as ex
from learning.treewidth import (
    elimination_width,
    masks_from_graph,
    masks_from_matrix,
    min_fill_upper_bound,
    mmd_lower_bound,
    treewidth_bounded,
    treewidth_decide,
    treewidth_exact,
    treewidth_reference,
)

nx = pytest.importorskip("networkx")


def _grid(r, c):
    return nx.convert_node_labels_to_integers(nx.grid_2d_graph(r, c))


# ----------------------------------------------------------------------------
# exact treewidth
# ----------------------------------------------------------------------------


@pytest.mark.parametrize("graph, expected", [
    (nx.path_graph(7), 1), (nx.cycle_graph(8), 2), (nx.complete_graph(5), 4),
    (_grid(3, 3), 3), (_grid(3, 5), 3), (_grid(4, 4), 4), (nx.petersen_graph(), 4),
    (nx.complete_bipartite_graph(3, 4), 3), (nx.empty_graph(5), 0), (nx.star_graph(6), 1),
])
def test_dp_known_values(graph, expected):
    masks = masks_from_graph(graph)
    width, order = treewidth_exact(masks)
    assert width == expected
    assert elimination_width(masks, order) == width      # the ordering is a checkable witness


def test_dp_against_python_reference_and_min_fill():
    rng = np.random.default_rng(7)
    for trial in range(40):
        n = int(rng.integers(3, 10))
        p = float(rng.uniform(0.15, 0.6))
        g = nx.gnp_random_graph(n, p, seed=int(rng.integers(1 << 30)))
        masks = masks_from_graph(g)
        width, order = treewidth_exact(masks)
        assert width == treewidth_reference(masks)
        assert elimination_width(masks, order) == width
        assert width <= min_fill_upper_bound(masks)[0]     # heuristic is an upper bound
        assert width >= mmd_lower_bound(masks)             # MMD is a lower bound
        # networkx's min-fill: also an upper bound, never below the exact value
        from networkx.algorithms.approximation import treewidth_min_fill_in
        assert width <= treewidth_min_fill_in(g)[0]


def test_decision_search_agrees_with_dp():
    rng = np.random.default_rng(11)
    for trial in range(25):
        n = int(rng.integers(8, 15))
        g = nx.gnp_random_graph(n, float(rng.uniform(0.1, 0.5)), seed=int(rng.integers(1 << 30)))
        masks = masks_from_graph(g)
        width, _ = treewidth_exact(masks)
        bb = treewidth_bounded(masks, deadline_seconds=30)
        assert bb["exact"] and bb["lo"] == bb["hi"] == width, (n, width, bb)
        assert elimination_width(masks, bb["order"]) == width
        assert treewidth_decide(masks, width)[0] == "yes"
        if width > 0:
            assert treewidth_decide(masks, width - 1)[0] == "no"
    masks = masks_from_graph(_grid(4, 6))
    assert treewidth_exact(masks)[0] == 4
    assert treewidth_bounded(masks, 30)["lo"] == 4


def test_decision_search_budget_is_censoring_not_an_answer():
    masks = masks_from_graph(nx.petersen_graph())
    status, order, nodes = treewidth_decide(masks, 3, budget=1)
    assert status == "unknown" and order is None and nodes >= 1
    bb = treewidth_bounded(masks, deadline_seconds=30, node_budget_per_call=1)
    assert bb["censored"] and bb["lo"] <= 4 <= bb["hi"]


def test_elimination_width_rejects_non_permutation():
    with pytest.raises(ValueError):
        elimination_width(masks_from_graph(nx.path_graph(3)), [0, 0, 1])


# ----------------------------------------------------------------------------
# the oracle and the objectives
# ----------------------------------------------------------------------------


def _spider() -> np.ndarray:
    """Centre 0 with three legs 0-1-2, 0-3-4, 0-5-6: the smallest tree that is
    not a caterpillar, so tw = 1 and pw = 2 (Ellis, Sudborough & Turner),
    hence MOSP optimum 3 with every edge a product."""
    edges = [(0, 1), (1, 2), (0, 3), (3, 4), (0, 5), (5, 6)]
    m = np.zeros((7, len(edges)), dtype=int)
    for j, (a, b) in enumerate(edges):
        m[a, j] = m[b, j] = 1
    return m


def test_masks_from_matrix_is_the_mosp_graph():
    m = np.array([[1, 1, 0], [1, 0, 1], [0, 1, 0], [0, 0, 1]])
    masks = masks_from_matrix(m)
    # product 0 = {0, 1}, product 1 = {0, 2}, product 2 = {1, 3}
    assert masks == [0b0110, 0b1001, 0b0001, 0b0010]


def test_evaluate_on_the_spider(tmp_path):
    rec = ex.evaluate(_spider(), tmp_path)
    assert rec["optimum"] == 3 and rec["tw"] == 1 and rec["pwtw"] == 1
    assert rec["gap"] == rec["optimum"] - rec["lb_best"]
    assert rec["overshoot"] == rec["ub_cs_dfs"] - rec["optimum"] >= 0
    assert rec["disagree"] == 0
    assert rec["status_lo_default"] == "unsat" and rec["status_hi_csearch"] == "sat"
    assert elimination_width(masks_from_matrix(_spider()), [int(v) for v in rec["tw_order"].split()]) == 1
    assert ex.matrix_from_key(rec["key"]).tolist() == _spider().tolist()
    cert = ex.recertify(rec["key"], tmp_path)
    assert cert["agree"] and cert["lattice"] == 3 and cert["pathwidth_dp"] == 2 and cert["tw"] == 1


def test_certificate_is_invariant_under_relabelling_and_recovering():
    m = _spider()
    perm = np.array([3, 0, 6, 1, 5, 2, 4])
    assert ex.graph_certificate(m) == ex.graph_certificate(m[perm])
    # the same graph covered by one product per vertex-star is the same certificate
    star = np.zeros((7, 1), dtype=int)
    star[[0, 1, 3, 5], 0] = 1                 # a K4 on the centre and its neighbours
    other = np.hstack([m[:, [1, 3, 5]], star])
    assert ex.graph_certificate(other) != ex.graph_certificate(m)


def test_tree_of_cliques_covers_and_connects():
    rng = np.random.default_rng(3)
    for n in (6, 10, 15):
        m = ex.tree_of_cliques(n, rng)
        assert m.shape[0] == n and (m.sum(axis=1) >= 1).all()
        masks = masks_from_matrix(m)
        g = nx.Graph()
        g.add_nodes_from(range(n))
        g.add_edges_from((i, j) for i in range(n) for j in range(i + 1, n) if masks[i] >> j & 1)
        assert nx.is_connected(g)


def test_local_search_improves_and_dedupes(tmp_path):
    """A planted objective (number of edges) the search must climb; the seen
    set skips every canonical duplicate."""
    calls = []

    def fake(matrix, solutions_dir):
        masks = masks_from_matrix(matrix)
        edges = sum(bin(x).count("1") for x in masks) // 2
        calls.append(ex.matrix_key(matrix))
        return {"key": ex.matrix_key(matrix), "edges": edges, "score_edges": edges, "n": matrix.shape[0]}

    seed = np.zeros((6, 4), dtype=int)
    seed[0, 0] = 1
    rng = np.random.default_rng(0)
    seen: set = set()
    out = ex.local_search(seed, "score_edges", 60, rng, tmp_path, patience=10, seen=seen, evaluate_fn=fake)
    assert out["best"]["score_edges"] > 0
    assert out["evaluations"] == len(calls) and len(set(calls)) == len(calls)   # never the same matrix twice
    assert len(seen) == out["evaluations"]
    assert out["skipped"] >= 0 and out["evaluations"] <= 61


def test_kill_verdict_and_growth_on_toy_frames():
    best = pd.DataFrame([
        {"objective": "gap", "n": 10, "value": 1, "evaluations": 5},
        {"objective": "pwtw", "n": 10, "value": 1, "evaluations": 5},
        {"objective": "pwtw", "n": 12, "value": 2, "evaluations": 5},
    ])
    baseline = pd.DataFrame([{"n": 10, "instances": 3, "gap": 1, "overshoot": 0, "disagree": 0,
                              "nodes": 4, "pwtw": 0, "pwtw_instances": 3},
                             {"n": 12, "instances": 2, "gap": 0, "overshoot": 0, "disagree": 0,
                              "nodes": 4, "pwtw": 2, "pwtw_instances": 2}])
    verdict = ex.kill_verdict(best, baseline)
    assert verdict["beats corpus"].tolist() == ["no", "yes", "no"]
    corpus_tw = pd.DataFrame([{"n_customers": 10, "pw": 3, "tw_lo": 3, "tw_exact": True, "gap": 0},
                              {"n_customers": 12, "pw": 5, "tw_lo": 3, "tw_exact": True, "gap": 2}])
    growth = ex.pwtw_growth(best, corpus_tw)
    assert growth.set_index("n").loc[12, "corpus max pw − tw"] == 2
    assert growth.set_index("n").loc[10, "corpus with pw − tw ≥ 1"] == 0


def test_tw_job_settles_pw_gt_tw_by_the_decision_search():
    """Warwick 871's structure in miniature: a K4 with three pendant triangles;
    the job must certify tw exactly and say whether pw exceeds it."""
    # customers 0-3 a K4 (product 0); triangles {0,4,5}, {1,6,7}, {2,8,9}
    m = np.zeros((10, 4), dtype=int)
    m[[0, 1, 2, 3], 0] = 1
    m[[0, 4, 5], 1] = 1
    m[[1, 6, 7], 2] = 1
    m[[2, 8, 9], 3] = 1
    tw = treewidth_exact(masks_from_matrix(m))[0]
    assert tw == 3
    from satisfiability.mosp_solver import solve_mosp_exact
    import tempfile, pathlib
    inst = ex.instance_from_matrix(m)
    opt = solve_mosp_exact(inst, solutions_dir=pathlib.Path(tempfile.mkdtemp()))[0]
    rec = ex._tw_job(("toy", "toy", 10, opt, 0, ex.matrix_key(m), 10.0))
    assert rec["tw_exact"] and rec["tw_lo"] == 3 and rec["method"] == "dp"
    assert rec["pw_gt_tw"] == ("yes" if opt - 1 > 3 else "no")
    # force the decision search on the same instance
    old = ex.DP_MAX_N
    try:
        ex.DP_MAX_N = 5
        rec2 = ex._tw_job(("toy", "toy", 10, opt, 0, ex.matrix_key(m), 10.0))
    finally:
        ex.DP_MAX_N = old
    assert rec2["method"] == "bb" and rec2["tw_exact"] and rec2["tw_lo"] == 3
    assert rec2["pw_gt_tw"] == rec["pw_gt_tw"]


def test_tw_job_beyond_64_customers_reports_heuristic_bounds_only():
    """Above the decision search's word the job records min-fill / MMD bounds
    and marks the row censored; on a path both bounds coincide."""
    n = 70
    m = np.zeros((n, n - 1), dtype=int)
    for j in range(n - 1):
        m[j, j] = m[j + 1, j] = 1
    rec = ex._tw_job(("path70", "toy", n, 3, 0, ex.matrix_key(m), 5.0))
    assert rec["method"] == "heuristic" and rec["censored"]
    assert rec["tw_lo"] == rec["tw_hi"] == 1 and rec["pw_gt_tw"] == "yes"   # pw = 2 > tw = 1
