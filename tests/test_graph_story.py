"""Guards on the graph-versus-matrix study (`learning.graph_story`).

The study rests on one construction and one invariant: a re-covering must
change the matrix and leave the labelled MOSP graph -- the neighbour masks the
customer search consumes -- exactly as it was, and when it does, the node
count to refute `optimum - 1` under the default configuration cannot move,
because the search sees nothing else. The hand-checked instance: products
{0, 1, 2}, {2, 3} and {1, 2}; the third is nested in the first, so `merge`
has one legal move (the nested pair, since {0, 1, 2} ∪ {2, 3} is not a clique
-- 0 and 3 are not adjacent), `split` can cut {0, 1, 2}, and the greedy cover
rebuilds the two maximal cliques.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from learning.graph_story import (
    METHODS,
    feature_sets,
    greedy_recover,
    lattice_table,
    merge_products,
    paired_table,
    recover,
    relabel,
    relabel_table,
    same_labelled_graph,
    split_product,
)
from mosp.instance import MOSPInstance

HAND = MOSPInstance.from_matrix(
    [[1, 0, 0], [1, 0, 1], [1, 1, 1], [0, 1, 0]], name="hand")


def _edges(instance: MOSPInstance) -> set[tuple[int, int]]:
    m = np.asarray(instance.matrix)
    overlap = m @ m.T
    return {(i, j) for i in range(m.shape[0]) for j in range(i + 1, m.shape[0]) if overlap[i, j]}


def test_hand_merge_takes_the_nested_pair_only():
    rng = np.random.default_rng(0)
    merged = merge_products(HAND, rng, "merged")
    assert merged is not None
    assert merged.n_patterns == 2
    assert same_labelled_graph(HAND, merged)
    cols = {tuple(np.flatnonzero(merged.matrix[:, j])) for j in range(2)}
    assert cols == {(0, 1, 2), (2, 3)}


def test_hand_split_and_greedy_keep_the_labelled_graph():
    for seed in range(5):
        rng = np.random.default_rng(seed)
        split = split_product(HAND, rng, "split")
        assert split is not None and split.n_patterns == 4
        assert same_labelled_graph(HAND, split)
        greedy = greedy_recover(HAND, np.random.default_rng(seed), "greedy")
        assert same_labelled_graph(HAND, greedy)
        assert {tuple(np.flatnonzero(greedy.matrix[:, j])) for j in range(greedy.n_patterns)} \
            == {(0, 1, 2), (2, 3)}
        assert _edges(greedy) == _edges(HAND)


def test_recoverings_of_random_instances_change_the_matrix_not_the_graph():
    from benchmarks.generator import generate_random_instance
    from learning.canonical import matrix_digest, wl_hash, mosp_graph_adjacency

    changed = 0
    for seed in range(12):
        inst = generate_random_instance(9, 9, 0.3, seed=seed)
        inst.name = f"r{seed}"
        for method in METHODS:
            out = recover(inst, method, 0)
            if out is None:
                continue
            assert out.n_customers == inst.n_customers
            assert same_labelled_graph(inst, out), method
            assert wl_hash(mosp_graph_adjacency(out)) == wl_hash(mosp_graph_adjacency(inst))
            changed += matrix_digest(out) != matrix_digest(inst)
    assert changed >= 12


def test_default_node_count_is_invariant_under_recovering(tmp_path: Path):
    from benchmarks.generator import generate_random_instance
    from learning.node_counts import refute
    from satisfiability.mosp_solver import solve_mosp_exact

    inst = generate_random_instance(12, 12, 0.25, seed=3)
    inst.name = "base12"
    optimum, _ = solve_mosp_exact(inst, solutions_dir=tmp_path)
    assert optimum >= 2
    base = refute(inst, optimum, "default")
    for method in METHODS:
        out = recover(inst, method, 1)
        if out is None:
            continue
        value, _ = solve_mosp_exact(out, solutions_dir=tmp_path)
        assert value == optimum
        assert refute(out, optimum, "default")["nodes"] == base["nodes"]


def test_relabel_is_the_same_matrix_class():
    from learning.canonical import wl_hash, mosp_graph_adjacency

    out, perm = relabel(HAND, 0)
    assert sorted(perm.tolist()) == [0, 1, 2, 3]
    assert wl_hash(mosp_graph_adjacency(out)) == wl_hash(mosp_graph_adjacency(HAND))
    assert sorted(np.asarray(out.matrix).sum(axis=1).tolist()) == \
        sorted(np.asarray(HAND.matrix).sum(axis=1).tolist())
    again, _ = relabel(HAND, 0)
    assert np.array_equal(out.matrix, again.matrix)


def test_feature_sets_are_built_from_group_names():
    sets = feature_sets()
    assert set(sets["graph-only"]) < set(sets["full"])
    assert set(sets["matrix-only"]) < set(sets["full"])
    assert not set(sets["graph-only"]) & {"density", "row_mean", "col_max", "lb_trivial",
                                          "ub_cs_dfs", "cc_products", "rig_edge_prob"}
    assert {"g_degeneracy", "tw_min_fill", "bw_rcm", "lb_contraction", "optimum"} <= set(sets["graph-only"])
    assert "optimum" not in feature_sets(with_optimum=False)["full"]


def test_tables_on_a_tiny_frame():
    rec = pd.DataFrame({
        "base_name": ["a", "a", "b", "b"], "method": ["split", "greedy", "split", "greedy"],
        "applicable": [True, True, True, False], "matrix_digest": ["x", "y", "z", None],
        "base_matrix_digest": ["m", "m", "q", "q"], "bipartite_cert": ["x", "y", "z", None],
        "base_bipartite_cert": ["m", "m", "q", "q"], "graph_cert": ["g", "g", "h", None],
        "base_graph_cert": ["g", "g", "h", "h"], "masks_equal": [True, True, True, None],
        "same_optimum": [True, True, True, None], "witness_ok": [True, True, True, None],
        "m_new": [5, 3, 6, None], "m_base": [4, 4, 5, 5],
        "nodes_default": [10, 10, 30, None], "base_nodes_default": [10, 10, 30, 30],
        "nodes_csearch": [10, 4, 30, None], "base_nodes_csearch": [10, 10, 30, 30],
        "better_move": [True, False, True, None], "base_better_move": [True, True, True, True],
    })
    t = paired_table(rec).set_index("method")
    assert t.loc["greedy", "applicable"] == 1 and t.loc["split", "applicable"] == 2
    assert t.loc["split", "default: nodes equal"] == 2
    assert t.loc["greedy", "better_move flipped"] == 1
    assert t.loc["greedy", "csearch: nodes equal"] == 0

    rel = pd.DataFrame({"base_name": ["a"] * 3 + ["b"] * 3, "n": [10] * 6, "k": [-1, 0, 1] * 2,
                        "nodes_default": [10, 10, 10, 100, 1000, 100],
                        "nodes_csearch": [10, 10, 10, 100, 100, 100]})
    r = relabel_table(rel).iloc[0]
    assert r["default: bases with any change"] == 1 and r["csearch: bases with any change"] == 0
    assert r["default: max/min ratio max"] == pytest.approx(1001 / 101)

    lat = pd.DataFrame({"base_name": ["a", "a", "a"], "n": [10] * 3, "method": ["base", "split", "greedy"],
                        "k": [-1, 0, 0], "count_search": [100, 100, 100],
                        "count_closing": [50, 25, 100], "min_search": [3, 3, 3],
                        "min_construction": [3, 3, 3]})
    lt = lattice_table(lat).set_index("method")
    assert lt.loc["split", "count_search equal"] == 1
    assert lt.loc["split", "closing ratio median"] == pytest.approx(0.5)
    assert lt.loc["greedy", "closing ratio median"] == pytest.approx(2.0)
