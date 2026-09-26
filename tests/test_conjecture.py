"""Tests for learning.conjecture (loop0003 item 09)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from learning import conjecture as cj

nx = pytest.importorskip("networkx")


def _spider(legs: int, length: int):
    g = nx.Graph()
    g.add_node(0)
    k = 1
    for _ in range(legs):
        prev = 0
        for _ in range(length):
            g.add_edge(prev, k)
            prev = k
            k += 1
    return g


def _adj(g):
    return {v: list(g.neighbors(v)) for v in g.nodes()}


# ----------------------------------------------------------------------------
# tree pathwidth
# ----------------------------------------------------------------------------


@pytest.mark.parametrize("graph, expected", [
    (nx.empty_graph(1), 0), (nx.empty_graph(4), 0), (nx.path_graph(2), 1), (nx.path_graph(9), 1),
    (nx.star_graph(5), 1), (_spider(3, 2), 2), (_spider(4, 2), 2), (_spider(2, 6), 1),
])
def test_tree_pathwidth_known(graph, expected):
    assert cj.tree_pathwidth(_adj(graph)) == expected


def test_tree_pathwidth_matches_dp_on_random_trees():
    from fixed_parameter_algorithm.pathwidth import compute_pathwidth

    rng = np.random.default_rng(3)
    for _ in range(25):
        n = int(rng.integers(2, 15))
        seed = int(rng.integers(1_000_000))
        tree = nx.random_labeled_tree(n, seed=seed) if hasattr(nx, "random_labeled_tree") \
            else nx.random_tree(n, seed=seed)
        assert cj.tree_pathwidth(_adj(tree)) == compute_pathwidth(tree)[0]


def test_tree_pathwidth_three_branches_lemma():
    # a vertex with three branches of pathwidth 2 (spiders) has pathwidth 3
    g = nx.Graph()
    g.add_node("c")
    for k in range(3):
        s = nx.relabel_nodes(_spider(3, 2), {v: (k, v) for v in range(7)})
        g = nx.union(g, s)
        g.add_edge("c", (k, 0))
    assert cj.tree_pathwidth(_adj(g)) == 3


# ----------------------------------------------------------------------------
# invariants
# ----------------------------------------------------------------------------


def _three_k4_at_hub() -> np.ndarray:
    m = np.zeros((10, 3), dtype=int)
    m[[0, 1, 2, 3], 0] = 1
    m[[0, 4, 5, 6], 1] = 1
    m[[0, 7, 8, 9], 2] = 1
    return m


def test_branching_invariants_on_three_cliques_at_a_hub():
    masks = cj.masks_from_matrix(_three_k4_at_hub())
    out = cj.branching_invariants(cj._graph_from_masks(masks))
    assert out["art"] == 1 and out["blocks"] == 3 and out["bridges"] == 0
    assert out["hubs3"] == 1
    assert out["blt"] == 3          # three branches K3 of treewidth 2 → pathwidth ≥ 3
    assert out["bct_pw"] == 1       # the block–cut tree is a star
    assert cj.simplicial_count(masks) == 9


def test_simplicial_count_triangle_with_pendant():
    g = nx.Graph([(0, 1), (1, 2), (0, 2), (2, 3)])
    masks = cj.masks_from_graph(g)
    assert cj.simplicial_count(masks) == 3          # 0, 1 and 3; 2's neighbourhood is not a clique


def test_clique_tree_pathwidth_path_of_cliques_is_one():
    m = np.zeros((7, 3), dtype=int)
    m[[0, 1, 2], 0] = 1
    m[[2, 3, 4], 1] = 1
    m[[4, 5, 6], 2] = 1
    pw, cliques = cj.clique_tree_pathwidth(cj._graph_from_masks(cj.masks_from_matrix(m)))
    assert (pw, cliques) == (1, 3)
    pw3, cliques3 = cj.clique_tree_pathwidth(cj._graph_from_masks(cj.masks_from_matrix(_three_k4_at_hub())))
    assert (pw3, cliques3) == (1, 3)


def test_invariants_are_below_the_optimum_on_hand_instances(tmp_path):
    from satisfiability.mosp_solver import solve_mosp_exact

    key = ("001000110/000000100/101000000/001011000/000011001/000001000/"
           "100100001/001000000/000100100/010011100")            # §21's 10-vertex graph
    ten = np.array([[int(c) for c in r] for r in key.split("/")])
    for matrix, expected in ((_three_k4_at_hub(), 4), (ten, 6)):
        inst = cj.MOSPInstance.from_matrix(matrix.tolist(), name="t")
        optimum, _ = solve_mosp_exact(inst, solutions_dir=tmp_path)
        assert optimum == expected
        inv = cj.invariants(matrix, expansion_budget=None)
        for name in ("tw1", "omega", "exp", "blt1", "contraction"):
            assert inv[name] <= optimum, name
        assert inv["tw_exact"] and inv["tw_method"] == "dp"
    inv = cj.invariants(ten, expansion_budget=None)
    assert (inv["tw_lo"], inv["omega"], inv["exp"], inv["hubs3"]) == (3, 4, 5, 0)
    inv = cj.invariants(_three_k4_at_hub(), expansion_budget=None)
    assert (inv["tw1"], inv["blt1"], inv["exp"]) == (4, 4, 4)


# ----------------------------------------------------------------------------
# candidates
# ----------------------------------------------------------------------------


def test_candidate_value_kinds_and_missing_ingredient():
    values = {"tw1": 4, "omega": 3, "f3": float("nan")}
    assert cj.candidate_value(values, {"term": (("tw1", 1.0),), "kind": "raw", "const": 0.0}) == 4
    assert cj.candidate_value(values, {"term": (("tw1", 1.0), ("omega", 0.5)), "kind": "add",
                                       "const": -1.5}) == int(np.floor(4 * 3 ** 0.5 - 1.5))
    assert cj.candidate_value(values, {"term": (("tw1", 1.0),), "kind": "scale", "const": 0.6}) == 2
    assert cj.candidate_value(values, {"term": (("f3", 1.0),), "kind": "raw", "const": 0.0}) < -1000
    assert cj._floor_sig(1.23456789) == pytest.approx(1.234)
    assert cj._floor_sig(0.0098765) == pytest.approx(0.009876)


def _toy_frame() -> pd.DataFrame:
    rng = np.random.default_rng(0)
    n = 60
    tw1 = rng.integers(2, 8, size=n)
    opt = tw1 + rng.integers(0, 3, size=n)
    lb = np.maximum(2, opt - rng.integers(0, 4, size=n))
    frame = pd.DataFrame({
        "instance_name": [f"i{i}" for i in range(n)],
        "source": ["corpus"] * n, "group_file": [f"f{i % 7}" for i in range(n)],
        "graph_cert": [f"c{i % 11}" for i in range(n)], "optimum": opt, "lb_best": lb,
        "tw1": tw1, "omega": np.minimum(tw1, opt), "exp": np.maximum(1, opt - 1),
        "n": rng.integers(10, 30, size=n),
    })
    frame["gap"] = frame["optimum"] - frame["lb_best"]
    return frame


def test_mine_constants_are_valid_by_construction_and_theorems_are_raw():
    frame = _toy_frame()
    cands = cj.mine(frame, max_degree=2, names=("tw1", "omega", "exp", "n"))
    assert len(cands) > 10
    fitted = cands[cands["kind"] != "raw"]
    assert (fitted["above"] == 0).all()                   # every constant chosen on all rows is valid
    n_raw = cands[(cands["kind"] == "raw") & (cands["formula"] == "n")].iloc[0]
    assert n_raw["above"] > 0 and not n_raw["valid"]      # a raw term is checked, not assumed
    raw = cands[(cands["kind"] == "raw") & (cands["formula"] == "tw1")]
    assert len(raw) == 1 and bool(raw.iloc[0]["valid"])
    add = cands[(cands["kind"] == "add") & (cands["formula"] == "n")].iloc[0]
    assert add["const"] == pytest.approx(np.floor(float((frame["optimum"] - frame["n"]).min()) * 100) / 100)
    # a candidate whose additive constant leaks on hold-out is flagged, never hidden
    assert "holdout_above" in cands.columns and (cands["holdout_above"] >= 0).all()
    surv = cj.distinct_survivors(cands, top=3)
    assert len(surv) <= 3 and surv["signature"].is_unique


def test_attack_catches_a_planted_false_bound_and_spares_a_theorem(tmp_path):
    from learning.extremal import local_search, tree_of_cliques

    false = {"term": (("n", 1.0),), "kind": "raw", "const": 0.0, "formula": "n"}     # claims optimum ≥ n
    true = {"term": (("tw1", 1.0),), "kind": "raw", "const": 0.0, "formula": "tw1"}  # a theorem
    evaluate = cj.make_evaluate([false, true], tmp_path)
    rng = np.random.default_rng(5)
    seed = tree_of_cliques(8, rng)
    res = local_search(seed, "viol_0", 6, rng, solutions_dir=tmp_path, evaluate_fn=evaluate)
    assert res["best"]["viol_0"] >= 1                     # the false bound is broken at once
    res = local_search(seed, "viol_1", 6, rng, solutions_dir=tmp_path, evaluate_fn=evaluate)
    assert res["best"]["viol_1"] <= 0                     # the theorem is not


def test_attack_summary_picks_the_smallest_counterexample():
    attack = pd.DataFrame({
        "candidate": [0, 0, 0, 1, 1], "formula": ["a", "a", "a", "b", "b"],
        "n": [8, 9, 10, 8, 9], "kind": ["tree"] * 5, "restart": [0] * 5,
        "evaluations": [10, 10, 10, 10, 10], "skipped": [0] * 5,
        "best_viol": [0, 1, 2, 0, -1], "best_key": ["k8", "k9", "k10", "x", "y"],
        "best_optimum": [3] * 5, "best_edges": [5, 7, 4, 3, 3], "max_trace": [0, 1, 2, 0, 0],
    })
    summ = cj.attack_summary(attack)
    a = summ[summ["candidate"] == 0].iloc[0]
    b = summ[summ["candidate"] == 1].iloc[0]
    assert a["verdict"] == "broken" and a["counter_n"] == 9 and a["counter_key"] == "k9"
    assert b["verdict"] == "survived" and b["counter_n"] == -1
    assert a["evaluations"] == 30
