"""§25: the ridge as a condition on one parameter -- the analytics, the
interpolated peak, the calibrated predictions and the deciding grid."""

import numpy as np
import pandas as pd
import pytest

from learning.ensemble import Cell
from learning.ridge_theory import (CANDIDATES, branching_factor, calibrate, cell_medians, clique_excess_of,
                                   constancy, derive, excess, expected_degree, giant_threshold_col_mean,
                                   interpolated_peak, invert_candidate, parabola_vertex, peak_table,
                                   predict_peaks, prediction_summary, ratio_cells, ratio_label,
                                   tree_threshold_col_mean)
from mosp.instance import MOSPInstance


def test_expected_degree_exact_on_tiny_cases():
    # one product with two of three customers: one edge, mean degree 2/3
    assert expected_degree(3, 1, 2, "fixed") == pytest.approx(2 / 3)
    # every product complete: degree n - 1 whatever m
    assert expected_degree(5, 3, 5, "fixed") == pytest.approx(4.0)
    # Bernoulli p = 1: complete graph
    assert expected_degree(6, 2, 6, "bernoulli") == pytest.approx(5.0)
    # far below the giant threshold the degree is the branching factor: r c (c - 1) at large n
    n, m, c = 10_000, 10_000, 3
    assert expected_degree(n, m, c, "fixed") == pytest.approx(branching_factor(1.0, c, "fixed"), rel=1e-3)


def test_excess_is_the_matrix_identity():
    matrix = [[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1], [1, 0, 0, 1]]
    inst = MOSPInstance.from_matrix(matrix, name="c4")
    n, m = inst.n_customers, inst.n_patterns
    n_ones = int(inst.matrix.sum())
    r, c = m / n, n_ones / m
    assert excess(r, c) == pytest.approx((n_ones - m) / n)        # (8 - 4) / 4 = 1: the tree threshold
    assert excess(r, c) == pytest.approx(1.0)


def test_thresholds_invert_the_branching_factor_and_excess():
    for gen in ("fixed", "bernoulli"):
        for r in (0.125, 0.25, 0.5, 1.0, 2.0):
            c = giant_threshold_col_mean(r, gen)
            assert branching_factor(r, c, gen) == pytest.approx(1.0)
            assert excess(r, tree_threshold_col_mean(r)) == pytest.approx(1.0)
    # the hypotheses at m = n / 4: excess = 2 says 9, mean degree calibrated at 8 says about 6.2
    assert invert_candidate("excess", 2.0, 0.25, 60, "fixed") == pytest.approx(9.0)
    c_deg = invert_candidate("g_deg_mean", 8.0, 0.25, 60, "fixed")
    assert expected_degree(60, 15, c_deg, "fixed") == pytest.approx(8.0, abs=1e-6)
    assert 5.5 < c_deg < 7.0
    assert invert_candidate("row_mean", 3.0, 0.5, 60, "fixed") == pytest.approx(6.0)
    assert invert_candidate("branch", 6.0, 1.0, 60, "fixed") == pytest.approx(3.0)


def test_ratio_label_snaps_to_the_nearest_ratio():
    assert ratio_label(37, 75) == "n/2"
    assert ratio_label(18, 75) == "n/4"
    assert ratio_label(9, 75) == "n/8"
    assert ratio_label(150, 75) == "2n"
    assert ratio_label(60, 60) == "n"


def test_parabola_vertex_recovers_a_planted_peak():
    x = np.log10([4.0, 5.0, 6.0])
    x_star = np.log10(5.4)
    y = -3.0 * (x - x_star) ** 2 + 4.0
    assert 10 ** parabola_vertex(x, y) == pytest.approx(5.4)
    # a convex triple has no interior maximum: the middle cell
    assert parabola_vertex(x, -y) == pytest.approx(x[1])
    # a vertex outside the triple is clamped
    y2 = np.array([1.0, 2.0, 2.9])
    assert parabola_vertex(x, y2) <= x[2]


def _toy_frame(peak_col_mean: float = 5.4, per_cell: int = 40, n: int = 60, m: int = 30,
               generator: str = "fixed") -> pd.DataFrame:
    """Cells d = 3..8 at one (generator, m, n) whose log nodes peak at `peak_col_mean`."""
    rng = np.random.default_rng(1)
    rows = []
    for d in range(3, 9):
        centre = 4.0 - 3.0 * (np.log10(d) - np.log10(peak_col_mean)) ** 2
        for i in range(per_cell):
            ln = centre + rng.normal(0, 0.05)
            rows.append({"instance_name": f"t_{d}_{i}", "cell": f"f_n{n}_m{m}_d{d}", "generator": generator,
                         "n": n, "m": m, "param": float(d), "index": i, "certified": True, "witness_ok": True,
                         "optimum": int(round(0.3 * n * d / 5)), "nodes_default": 10 ** ln - 1,
                         "nodes_csearch": 10 ** ln - 1, "status_default": "unsat", "status_csearch": "unsat",
                         "col_mean": float(d), "row_mean": d * m / n, "n_ones": d * m, "g_components": 1,
                         "g_edges": m * d * (d - 1) // 2, "g_deg_mean": m * d * (d - 1) / n, "g_density": 0.1,
                         "tw_min_fill": 0.3 * n, "g_degeneracy": 0.1 * n, "bw_rcm": 0.5 * n, "lb_best": 0.2 * n,
                         "g_clustering": 0.5, "g_largest_comp_frac": 1.0, "complete_graph": False,
                         "graph_cert": f"c{d}{i}", "total_seconds": 0.1})
    return pd.DataFrame(rows)


def test_interpolated_peak_and_interval_on_a_planted_ridge():
    frame = derive(_toy_frame(5.4))
    cells = cell_medians(frame)
    assert len(cells) == 6
    assert cells["excess"].iloc[0] == pytest.approx(0.5 * (3 - 1))          # r (c - 1) from the matrix columns
    pk = interpolated_peak(cells, frame, resamples=200)
    assert pk["interior"] and pk["peak_param"] == 5.0
    assert pk["peak_col_mean"] == pytest.approx(5.4, abs=0.4)          # cell medians carry noise sd ~0.008
    assert pk["ci_lo"] <= 5.4 <= pk["ci_hi"]                            # the planted location is inside the interval
    assert pk["ci_lo"] <= pk["peak_col_mean"] <= pk["ci_hi"]
    assert pk["ci_hi"] - pk["ci_lo"] < 1.0
    # an edge peak has no interval and is reported on the cell
    edge = interpolated_peak(cells[cells["param"] >= 5.0], frame, resamples=0)
    assert not edge["interior"] and edge["peak_col_mean"] == 5.0 and np.isnan(edge["ci_lo"])


def test_calibrated_prediction_hits_a_ridge_that_follows_the_excess():
    # two series, m = n and m = n / 2, both with their peak where r (c - 1) = 2: c = 3 and c = 5
    a = _toy_frame(3.0, n=60, m=60)
    b = _toy_frame(5.0, n=60, m=30)
    frame = derive(pd.concat([a, b], ignore_index=True))
    cells = cell_medians(frame)
    peaks = peak_table(frame, cells, min_n=30, resamples=100)
    assert set(peaks["ratio_label"]) == {"n", "n/2"}
    assert calibrate(peaks, "excess", "fixed", min_n=50) == pytest.approx(2.0, abs=0.15)
    pred = predict_peaks(peaks, cells, min_n=50, candidates=("excess", "col_mean"))
    summary = prediction_summary(pred).set_index("candidate")
    assert summary.loc["excess", "mean_abs_log10_error"] < 0.03           # 5 predicted at m = n / 2
    assert summary.loc["col_mean", "mean_abs_log10_error"] > 0.15          # 3 predicted, 5 measured
    const = constancy(peaks, min_n=50, candidates=("excess", "col_mean"))
    # with two ratios only the per-(gen, n) CV needs three; the all-peaks CV still orders them
    assert const.set_index("candidate").loc["excess", "cv_all_peaks"] < const.set_index("candidate").loc["col_mean", "cv_all_peaks"]


def test_clique_excess_equals_the_matrix_excess_on_a_tree_of_cliques():
    # two triangles sharing one customer: products are the maximal cliques
    matrix = [[1, 0], [1, 0], [1, 1], [0, 1], [0, 1]]
    inst = MOSPInstance.from_matrix(matrix, name="bowtie")
    out = clique_excess_of(inst)
    assert out["clique_excess"] == pytest.approx((6 - 2) / 5)
    assert out["max_cliques_over_m"] == pytest.approx(1.0)


def test_deciding_grid():
    cells = ratio_cells()
    ms = {(c.n, c.m) for c in cells}
    assert ms == {(50, 12), (60, 15), (75, 18), (75, 9)}
    assert len(cells) == 3 * (9 + 6) + 10 == 55
    assert len(set(cells)) == len(cells)
    assert all(c.param <= c.n for c in cells)
    assert Cell("fixed", 75, 9, 24) in cells
