"""`learning.bound_gap` on frames and instances small enough to check by hand.

Nothing here touches the solver's defaults, the corpus or `solutions/`; the
re-certification helper is exercised on a hand-built instance whose optimum is
known and which has no cached solution, through a temporary solutions directory.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from learning.bound_gap import (
    GAP_THRESHOLD,
    LABEL_COLUMNS,
    classification_rows,
    classify,
    cluster_gap_instances,
    common_structure,
    component_shortfall,
    describe_instance,
    draw_instance,
    feature_sets,
    gap_by_band,
    mixed_cells,
    smallest_gap_instances,
    tree_text,
    treewidth_ceiling,
    treewidth_upper_bound,
    with_gap,
    within_cell_contrast,
)
from mosp.instance import MOSPInstance

pytest.importorskip("sklearn")

# A path on four customers, one product per edge: a-b, b-c, c-d.
PATH4 = [[1, 0, 0],
         [1, 1, 0],
         [0, 1, 1],
         [0, 0, 1]]

# K4 from a single product.
K4 = [[1], [1], [1], [1]]


def _frame(gaps, n=20, m=10, seed=0, signal=None):
    """A toy table: `signal`, if given, is a column whose value is the gap
    class, so that a classifier and the within-cell contrast have something
    to find; every other feature is noise."""
    rng = np.random.default_rng(seed)
    k = len(gaps)
    gaps = np.asarray(gaps)
    frame = pd.DataFrame({
        "instance_name": [f"i{i}" for i in range(k)],
        "source_file": [f"f{i % 4}" for i in range(k)],
        "collection": ["toy"] * k,
        "optimum": 5 + gaps,
        "lb_best": np.full(k, 5), "lb_trivial": np.full(k, 3), "lb_contraction": np.full(k, 5),
        "n_customers": np.full(k, n), "n_patterns": np.full(k, m), "n_ones": rng.integers(20, 60, k),
        "density": rng.uniform(0.1, 0.4, k),
    })
    for column in ("shape_ratio", "distinct_col_frac", "distinct_row_frac", "dominated_col_frac",
                   "col_max_frac", "col_min", "row_min", "row_max", "row_mean", "row_std",
                   "col_mean", "col_std", "g_density", "g_components", "g_largest_comp_frac",
                   "g_clustering", "g_degeneracy", "g_deg_min", "g_deg_max", "g_deg_mean", "g_deg_std",
                   "tw_min_fill", "tw_min_degree", "bw_rcm", "spectral_radius", "fiedler",
                   "fiedler_lcc", "cc_products", "cc_greedy", "sep_size", "sep_frac",
                   "rig_edge_prob", "rig_deg_expected", "rig_density_ratio"):
        frame[column] = rng.uniform(0.5, 2.0, k)
    if signal:
        frame[signal] = (gaps >= GAP_THRESHOLD).astype(float) + rng.normal(0, 0.05, k)
    return frame


def test_with_gap_labels_three_classes_and_refuses_a_bound_violation():
    frame = with_gap(_frame([0, 0, 1, 2, 3]))
    assert frame["gap"].tolist() == [0, 0, 1, 2, 3]
    assert frame["gap_class"].tolist() == ["tight", "tight", "gap 1", "gap >= 2", "gap >= 2"]
    rows = classification_rows(frame)
    assert rows["y"].tolist() == [0, 0, 1, 1]  # the gap-1 row is dropped
    bad = _frame([0, 1])
    bad.loc[0, "lb_best"] = 9
    with pytest.raises(ValueError, match="bound violation"):
        with_gap(bad)


def test_feature_sets_never_hold_the_label_or_an_upper_bound():
    """Iteration 6's run scored 1.000 everywhere because `y` had been swept
    into the structure set; the sets are now built from the group names and
    refuse a label."""
    rows = classification_rows(with_gap(_frame([0] * 5 + [2] * 5)))
    rows["ub_best"] = rows["optimum"]
    rows["bound_gap"] = 0.0
    sets = feature_sets(rows)
    names = sorted(k.split(" (")[0] for k in sets)
    assert names == ["density + size", "size-free", "structure", "structure + invariants",
                     "structure + invariants + lower bounds"]
    for columns in sets.values():
        assert not set(columns) & set(LABEL_COLUMNS)
        assert not [c for c in columns if c.startswith(("ub_", "bound_"))]
        assert all(c in rows.columns for c in columns)
    assert "lb_best" in sets["structure + invariants + lower bounds"]
    assert not any("lb_best" in v for k, v in sets.items() if "lower bounds" not in k)
    free = [v for k, v in sets.items() if k.startswith("size-free")][0]
    assert "g_deg_cv" in free and "g_deg_cv" in rows.columns and "tw_min_fill_frac" in free


def test_treewidth_ceiling_counts_certificates_and_checks_the_theorems():
    frame = with_gap(_frame([0, 0, 1, 2, 3]))
    # optimum = 5 + gap; tw_min_fill + 1 = optimum - 1 on the last two rows certifies pw > tw
    frame["tw_min_fill"] = [4, 6, 5, 5, 6]
    table = treewidth_ceiling(frame).set_index("rows")
    assert table.loc["tight", "pw > tw certified"] == 0
    assert table.loc["gap 1", "pw > tw certified"] == 0
    assert table.loc["gap >= 2", "pw > tw certified"] == 2 and table.loc["gap >= 2", "frac"] == 1.0
    assert table.loc["gap >= 2", "lb_best above ceiling"] == 0
    frame.loc[0, "lb_contraction"] = 9  # a "treewidth bound" above the min-fill width is a code bug
    with pytest.raises(ValueError, match="feature code is wrong"):
        treewidth_ceiling(frame)


def test_treewidth_upper_bound_on_a_path_a_clique_and_a_cycle():
    import networkx as nx

    assert treewidth_upper_bound(nx.path_graph(6), restarts=5) == 1
    assert treewidth_upper_bound(nx.complete_graph(5), restarts=5) == 4
    assert treewidth_upper_bound(nx.cycle_graph(7), restarts=5) == 2
    assert treewidth_upper_bound(nx.Graph(), restarts=5) == 0


def test_band_and_component_tables_count_by_hand():
    frame = with_gap(_frame([0, 0, 1, 2, 4]))
    band = gap_by_band(frame)
    assert len(band) == 1 and band.loc[0, "band"] == "11-20"
    assert band.loc[0, "tight"] == 2 and band.loc[0, "gap 1"] == 1 and band.loc[0, "gap >= 2"] == 2
    assert band.loc[0, "mean gap"] == pytest.approx(7 / 5)
    short = component_shortfall(frame)
    trivial = short[(short["rows"] == "gap >= 2") & (short["bound"] == "lb_trivial")].iloc[0]
    assert trivial["mean shortfall"] == pytest.approx(((7 - 3) + (9 - 3)) / 2)
    assert trivial["tight frac"] == 0.0


def test_mixed_cells_need_both_classes():
    frame = with_gap(_frame([0] * 6 + [2] * 6))
    frame.loc[6:8, "n_patterns"] = 99  # three gap rows moved to a cell of their own
    rows = classification_rows(frame)
    mask = mixed_cells(rows, min_per_class=3)
    assert mask.sum() == 9  # the 6 tight + the 3 gap rows left in the shared cell
    assert not mixed_cells(rows, min_per_class=4).any()


def test_classifier_and_contrast_find_a_planted_signal():
    frame = with_gap(_frame([0] * 40 + [2] * 40, signal="g_clustering"))
    rows = classification_rows(frame)
    sets = {"noise": ["density", "sep_frac"], "signal": ["density", "g_clustering"]}
    table, probas = classify(rows, folds=4, with_ebm=False, sets=sets,
                             splits={"file": rows["source_file"].to_numpy()})
    by = table.set_index(["model", "features"])["auc"]
    assert by[("tree (depth 3)", "signal")] > 0.95
    assert by[("tree (depth 3)", "noise")] < 0.75
    assert set(probas) == {("file", m, f) for m in ("tree (depth 3)", "boosting (ceiling)") for f in sets}
    contrast = within_cell_contrast(rows)
    assert contrast.iloc[0]["feature"] == "g_clustering"
    assert contrast.iloc[0]["auc"] > 0.95 and contrast.iloc[0]["d"] > 1.5
    assert "g_clustering" in tree_text(rows, ["density", "g_clustering"])


def test_classify_refuses_rows_without_a_label():
    with pytest.raises(ValueError, match="classification_rows"):
        classify(with_gap(_frame([0, 2])), with_ebm=False)


def test_smallest_gap_instances_orders_and_dedupes():
    frame = with_gap(_frame([2, 2, 2, 0, 3]))
    frame["n_customers"] = [30, 20, 20, 10, 20]
    frame["n_ones"] = [40, 50, 40, 10, 40]
    frame["graph_cert"] = ["a", "b", "c", "d", "c"]  # rows 2 and 4 are isomorphic
    ten = smallest_gap_instances(frame, k=10)
    assert ten["instance_name"].tolist() == ["i4", "i1", "i0"]  # 20/40 first (i4 before i2 by file, i2 then deduped), 20/50, then 30


def test_cluster_gap_instances_on_two_planted_groups():
    frame = with_gap(_frame([2] * 30))
    skip = {"instance_name", "source_file", "collection", "optimum", "lb_best", "lb_trivial",
            "lb_contraction", "n_customers", "n_patterns", "n_ones", "gap", "gap_class"}
    shifted = [c for c in frame.columns if c not in skip]
    frame.loc[:14, shifted] += 10.0  # the first fifteen sit far from the rest on every feature
    table, labelled, k = cluster_gap_instances(frame, k_range=range(2, 4))
    assert k == 2 and len(table) == 2 and labelled["cluster"].nunique() == 2
    assert table["instances"].sum() == 30
    assert set(labelled.loc[:14, "cluster"]) != set(labelled.loc[15:, "cluster"])


def test_describe_instance_on_a_path_and_a_clique():
    path = describe_instance(MOSPInstance.from_matrix(PATH4, name="path"), tw_restarts=3)
    assert path["degrees"] == [2, 2, 1, 1]
    assert path["simplicial"] == 2 and path["tw_ub"] == 1  # the two end customers; a path is a tree
    assert path["row_sums"] == "2×2, 1×2" and path["col_sums"] == "2×3"
    assert path["lb_trivial"] == 2 and path["lb_clique"] == 2 and path["lb_contraction"] == 2
    assert path["tw_min_fill+1"] == 2 and path["bw_rcm+1"] == 2
    assert path["matrix"] == ["1 0 0", "1 1 0", "0 1 1", "0 0 1"]
    k4 = describe_instance(MOSPInstance.from_matrix(K4, name="k4"), tw_restarts=3)
    assert k4["degrees"] == [3, 3, 3, 3] and k4["lb_clique"] == 4 and k4["edges"] == 6
    assert k4["simplicial"] == 4 and k4["tw_ub"] == 3
    row = pd.Series({"source_file": "x/y.txt", "optimum": 2, "lb_best": 2, "gap": 0})
    text = draw_instance(path, row, None)
    assert "degree sequence 2×2, 1×2" in text and "1 1 0" in text
    assert "2 of 4 customers in exactly one product" in text and "not separated" in text
    text = draw_instance(path, pd.Series({"source_file": "x/y.txt", "optimum": 3, "lb_best": 2, "gap": 1}), None)
    assert "pathwidth 2 > treewidth (≤ 1)" in text  # a hypothetical optimum, to exercise the branch
    table = common_structure([path, k4])
    assert table["clique"].tolist() == [2, 4] and table["deg min-max"].tolist() == ["1-2", "3-3"]
    assert table["simplicial"].tolist() == [2, 4] and table["tw_ub+1"].tolist() == [2, 4]
    assert "pw > tw" not in table.columns
    table = common_structure([path, k4], optima=[2, 4])
    assert table["pw > tw"].tolist() == [False, False] and table["optimum"].tolist() == [2, 4]


def test_recertify_on_a_hand_instance_through_a_temporary_directory(tmp_path):
    """A 7-customer spider (optimum 3, trivial bound 2): the exact re-solve
    and the independent refutation agree, through a temporary solutions
    directory so the corpus is untouched."""
    from learning.bound_gap import recertify

    spider = [[1, 1, 0, 0, 0, 0],
              [1, 0, 1, 0, 0, 0],
              [1, 0, 0, 1, 0, 0],
              [0, 1, 0, 0, 1, 0],
              [0, 0, 1, 0, 0, 1],
              [0, 0, 0, 1, 1, 0],
              [0, 0, 0, 0, 0, 1]]
    inst = MOSPInstance.from_matrix(spider, name="spider7")
    cert = recertify(inst, 3, solutions_dir=tmp_path)
    assert cert == {"cached": 3, "resolved": 3, "refute status": "unsat",
                    "refute nodes": cert["refute nodes"], "agree": True}
    assert cert["refute nodes"] > 0
    assert list(tmp_path.glob("*.json"))  # the witness was persisted, in the temporary directory
