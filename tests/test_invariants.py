"""The `invariants` feature group and `learning.invariants_study`, on instances
small enough to check by hand."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from learning.features import (
    DEFAULT_GROUPS,
    _clique_cover_counts,
    _sweep_separator,
    feature_names,
    instance_features,
    invariant_names,
)
from mosp.instance import MOSPInstance

pytest.importorskip("sklearn")

# A path on four customers, one product per edge: a-b, b-c, c-d.
PATH4 = [[1, 0, 0],
         [1, 1, 0],
         [0, 1, 1],
         [0, 0, 1]]

# K4 from a single product: every customer needs it.
K4 = [[1], [1], [1], [1]]

# A triangle covered four times over: three edge products and the triangle.
TRIANGLE_OVERCOVERED = [[1, 1, 0, 1],
                        [1, 0, 1, 1],
                        [0, 1, 1, 1]]


def _inv(matrix, name="t"):
    return instance_features(MOSPInstance.from_matrix(matrix, name=name), groups=("invariants",))


def test_the_group_is_in_the_defaults_and_its_names_are_listed():
    assert "invariants" in DEFAULT_GROUPS
    names = invariant_names()
    assert len(names) == 13
    assert names == feature_names()[-len(names):]


def test_path_on_four_customers():
    f = _inv(PATH4)
    assert f["tw_min_fill"] == 1 and f["tw_min_degree"] == 1  # a tree
    assert f["bw_rcm"] == 1  # the path itself is the bandwidth-1 layout
    assert f["spectral_radius"] == pytest.approx((1 + math.sqrt(5)) / 2)  # 2cos(pi/5)
    assert f["fiedler"] == pytest.approx(2 - math.sqrt(2))  # 2 - 2cos(pi/4)
    assert f["fiedler_lcc"] == pytest.approx(f["fiedler"])
    assert f["cc_products"] == 3 and f["cc_greedy"] == 3  # no product is redundant
    assert f["sep_size"] == 1 and f["sep_frac"] == pytest.approx(0.25)
    # p_hat = 6/12, edge probability 1 - (1 - 1/4)^3
    assert f["rig_edge_prob"] == pytest.approx(1 - 0.75 ** 3)
    assert f["rig_deg_expected"] == pytest.approx(3 * (1 - 0.75 ** 3))
    assert f["rig_density_ratio"] == pytest.approx(0.5 / (1 - 0.75 ** 3))


def test_complete_graph_from_one_product():
    f = _inv(K4)
    assert f["tw_min_fill"] == 3 and f["tw_min_degree"] == 3 and f["bw_rcm"] == 3
    assert f["spectral_radius"] == pytest.approx(3)
    assert f["fiedler"] == pytest.approx(4)
    assert f["cc_products"] == 1 and f["cc_greedy"] == 1
    # Leaving no piece above 2n/3 = 2.67 nodes needs two nodes out of K4.
    assert f["sep_size"] == 2
    assert f["rig_edge_prob"] == pytest.approx(1) and f["rig_density_ratio"] == pytest.approx(1)


def test_bandwidth_plus_one_is_never_below_the_optimum_on_the_hand_instances():
    # Optima: the path is 2 (open at most two stacks), K4 is 4.
    assert _inv(PATH4)["bw_rcm"] + 1 >= 2
    assert _inv(K4)["bw_rcm"] + 1 >= 4


def test_greedy_clique_cover_drops_the_covered_edge_products():
    m = np.array(TRIANGLE_OVERCOVERED)
    products, greedy = _clique_cover_counts(m)
    assert (products, greedy) == (4, 1)
    # A product needed by one customer contains no edge and does not count.
    products, greedy = _clique_cover_counts(np.array([[1, 1], [1, 0], [0, 0]]))
    assert (products, greedy) == (1, 1)


def test_sweep_separator_on_a_path_and_a_clique():
    import networkx as nx

    path = nx.path_graph(6)
    assert _sweep_separator(path, list(range(6))) == 1
    assert _sweep_separator(nx.complete_graph(6), list(range(6))) == 2
    assert _sweep_separator(nx.empty_graph(2), [0, 1]) == 0


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_exact_invariants_are_permutation_invariant(seed):
    rng = np.random.default_rng(seed)
    m = (rng.random((9, 11)) < 0.3).astype(int)
    m[0, 0] = 1  # no empty instance
    shuffled = m[rng.permutation(9)][:, rng.permutation(11)]
    a = _inv(m.tolist())
    b = _inv(shuffled.tolist())
    for key in ("spectral_radius", "fiedler", "fiedler_lcc", "cc_products",
                "rig_edge_prob", "rig_deg_expected", "rig_density_ratio"):
        assert a[key] == pytest.approx(b[key]), key
    # The greedy ones are compared on the symmetric hand instances above; here
    # they must at least stay within their known slack of the exact values.
    assert a["tw_min_fill"] >= 0 and b["bw_rcm"] >= a["tw_min_fill"]


def test_point_estimates_count_bound_violations():
    from learning.invariants_study import point_estimates

    frame = pd.DataFrame({
        "optimum": [3, 4, 5],
        "lb_best": [3, 3, 5],
        "ub_best": [3, 4, 6],
        "ub_cs_dfs": [3, 4, 6],
        "tw_min_fill": [2, 3, 3],
        "tw_min_degree": [2, 4, 4],
        "bw_rcm": [2, 3, 5],
        "spectral_radius": [1.6, 2.4, 3.9],  # rounds to 3, 3, 5 against 3, 4, 5
        "g_degeneracy": [2, 2, 4],
        "sep_size": [1, 1, 2],
    })
    table = point_estimates(frame).set_index("estimate")
    assert table.loc["lb_best", "above"] == 0 and table.loc["lb_best", "below"] == 1
    assert table.loc["ub_best", "below"] == 0 and table.loc["ub_best", "above"] == 1
    assert table.loc["tw_min_fill + 1", "exact"] == pytest.approx(2 / 3)
    assert table.loc["tw_min_degree + 1", "above"] == 1
    assert table.loc["bw_rcm + 1", "below"] == 0
    assert table.loc["round(spectral_radius) + 1", "exact"] == pytest.approx(2 / 3)


def test_invariance_check_reports_no_change_on_symmetric_instances():
    from learning.invariants_study import invariance_check

    pairs = [("p", MOSPInstance.from_matrix(PATH4, name="p")),
             ("k", MOSPInstance.from_matrix(K4, name="k"))]
    table = invariance_check(pairs, sample=2, min_large=50, seed=0, workers=1)
    assert set(table["feature"]) == set(invariant_names())
    assert (table["instances"] == 2).all()
    assert (table["changed"] == 0).all()
