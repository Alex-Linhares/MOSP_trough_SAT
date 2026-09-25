"""Guards on `learning.fingerprint`, the generator-fingerprint study.

Each quantity the module computes is checked on a frame small enough to do by
hand: the size-free transform, the leak-free grouping, the accuracy ceiling
set by cross-labelled isomorphism classes, the grouped classifier on a
separable toy, and the embedding's shape under the PCA fallback.
"""

import numpy as np
import pandas as pd
import pytest

from learning.fingerprint import (
    classify,
    embed,
    knn_purity,
    label_ceiling,
    size_free_features,
    structure_columns,
    sub_collection,
    union_groups,
)


def _frame() -> pd.DataFrame:
    # two customers, four products: rows (2, 2), columns (1, 1, 1, 1) on the
    # first instance; a 3x2 all-ones matrix on the second.
    return pd.DataFrame({
        "instance_name": ["a", "b"],
        "source_file": ["benchmarks/instances/X/Y/f1.txt", "benchmarks/instances/X/Z/f2.txt"],
        "collection": ["X/Y", "X/Z"],
        "provenance": ["certified:refutation"] * 2,
        "optimum": [2, 3],
        "n_customers": [2, 3], "n_patterns": [4, 2], "n_ones": [4, 6],
        "density": [0.5, 1.0], "shape_ratio": [0.5, 1.5],
        "distinct_col_frac": [0.5, 0.5], "distinct_row_frac": [1.0, 1 / 3],
        "dominated_col_frac": [0.0, 1.0],
        "row_min": [2, 2], "row_max": [2, 2], "row_mean": [2.0, 2.0], "row_std": [0.0, 0.0],
        "col_min": [1, 3], "col_max": [1, 3], "col_mean": [1.0, 3.0], "col_std": [0.0, 0.0],
        "col_max_frac": [0.5, 1.0],
        "g_nodes": [2, 3], "g_edges": [0, 3], "g_density": [0.0, 1.0],
        "g_components": [2, 1], "g_largest_comp_frac": [0.5, 1.0],
        "g_clustering": [0.0, 1.0], "g_degeneracy": [0, 2],
        "g_deg_min": [0, 2], "g_deg_max": [0, 2], "g_deg_mean": [0.0, 2.0], "g_deg_std": [0.0, 0.0],
        "lb_best": [1, 3], "ub_best": [2, 3], "bound_gap": [1, 0],
    })


def test_sub_collection_is_the_two_directories_under_instances():
    assert sub_collection("benchmarks/instances/MOSP_Instances/SCOOP/x.txt") == "MOSP_Instances/SCOOP"
    assert sub_collection("benchmarks/instances/Only/x.txt") == "Only"


def test_structure_columns_exclude_bounds_and_identifiers():
    cols = structure_columns(_frame())
    assert "lb_best" not in cols and "bound_gap" not in cols and "optimum" not in cols
    assert "n_customers" in cols and "g_clustering" in cols


def test_size_free_features_by_hand():
    free = size_free_features(_frame())
    assert set(("n_customers", "n_patterns", "n_ones", "g_nodes", "g_edges")).isdisjoint(free.columns)
    # first instance: every column has one customer of two, every row two of four products
    assert free.loc[0, "col_min_frac"] == pytest.approx(0.5)
    assert free.loc[0, "row_min_frac"] == pytest.approx(0.5)
    assert free.loc[0, "row_max_frac"] == pytest.approx(0.5)
    assert free.loc[0, "row_cv"] == 0.0 and free.loc[0, "col_cv"] == 0.0
    assert free.loc[0, "g_components_frac"] == pytest.approx(1.0)
    # second instance: the triangle, degeneracy 2 of a possible n - 1 = 2
    assert free.loc[1, "g_degeneracy_frac"] == pytest.approx(1.0)
    assert free.loc[1, "g_deg_max_frac"] == pytest.approx(1.0)
    # a zero mean gives a zero coefficient of variation, not NaN
    assert not free.isna().any().any()


def test_union_groups_join_files_through_shared_classes():
    files = pd.Series(["f1", "f1", "f2", "f3", "f4"])
    classes = pd.Series(["A", "B", "B", "C", np.nan])
    groups = union_groups(files, classes)
    # f1 and f2 share class B; f3 is alone; f4 has no class and is alone
    assert groups[0] == groups[1] == groups[2]
    assert len({groups[0], groups[3], groups[4]}) == 3


def test_label_ceiling_counts_the_unavoidable_errors():
    labels = pd.Series(["Shaw", "Challenge", "Shaw", "Harvey", "Harvey"])
    classes = pd.Series(["k", "k", "j", "j", "m"])
    # class k: Shaw + Challenge -> one wrong; class j: Shaw + Harvey -> one wrong
    assert label_ceiling(labels, classes) == pytest.approx(3 / 5)
    assert label_ceiling(labels, pd.Series([np.nan] * 5)) == 1.0


def test_grouped_classifier_separates_a_separable_toy_and_refuses_no_groups():
    rng = np.random.default_rng(0)
    n = 200
    x = pd.DataFrame({"u": np.r_[rng.normal(0, 1, n), rng.normal(6, 1, n)],
                      "v": rng.normal(0, 1, 2 * n)})
    y = np.array(["p"] * n + ["q"] * n)
    groups = np.arange(2 * n) % 10
    res = classify(x, y, groups, folds=5)
    assert res["accuracy"] > 0.95
    assert set(res["recall"]) == {"p", "q"}
    assert res["confusion"].to_numpy().sum() == 2 * n
    with pytest.raises(ValueError):
        classify(x, y, None, folds=5)


def test_pca_fallback_embedding_and_knn_purity():
    rng = np.random.default_rng(1)
    feats = pd.DataFrame(rng.normal(size=(30, 5)), columns=list("abcde"))
    feats.iloc[15:, :] += 50.0  # two far-apart blobs
    points, method = embed(feats, use_umap=False)
    assert method == "PCA" and points.shape == (30, 2)
    labels = np.array(["x"] * 15 + ["y"] * 15)
    purity = knn_purity(points, labels, k=5).set_index("collection")
    assert purity.loc["x", "5-NN purity"] == 1.0
    assert purity.loc["all", "instances"] == 30
