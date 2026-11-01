"""loop0010 item 09: the ridge hypothesis H1 and the vectorised closing-order
lattice. The lattice is checked against the pure-Python reference in
`learning.degeneracy` (every edge weight under both measures, both minima,
both counts); the peak, score and kill machinery on synthetic series with
known answers."""

import math

import numpy as np
import pandas as pd
import pytest

from benchmarks.generator import generate_random_instance, generate_structured_instance
from learning import excess_ridge as er
from learning.degeneracy import Compact, closing_weights, lattice_counts, lattice_minimum
from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks


def _small_instances(count: int = 40):
    rng = np.random.default_rng(7)
    out = []
    for trial in range(count):
        n, m = int(rng.integers(3, 9)), int(rng.integers(2, 12))
        if trial % 2:
            out.append(generate_random_instance(n, m, float(rng.uniform(0.15, 0.7)), seed=trial, name=f"b{trial}"))
        else:
            out.append(generate_structured_instance(n, m, int(rng.integers(1, min(n, 5) + 1)), seed=trial,
                                                    name=f"f{trial}"))
    return out


def test_vectorised_weights_equal_the_reference_on_every_edge():
    for inst in _small_instances():
        comp = Compact(inst)
        a = comp.a
        s_ref, c_ref = closing_weights(comp)
        _comp, s_np, c_np = er.lattice_weights(inst)
        for S in range(1 << a):
            for c in range(a):
                if not (S >> c) & 1:
                    assert s_np[c, S] == s_ref[S * a + c]
                    assert c_np[c, S] == c_ref[S * a + c]


def test_minima_and_counts_equal_the_reference():
    for inst in _small_instances():
        comp = Compact(inst)
        a = comp.a
        s_ref, c_ref = closing_weights(comp)
        _comp, s_np, c_np = er.lattice_weights(inst)
        k = lattice_minimum(c_ref, a)
        assert er.lattice_minimum_np(c_np) == k
        assert er.lattice_minimum_np(s_np) == lattice_minimum(s_ref, a)
        for w_ref, w_np in ((c_ref, c_np), (s_ref, s_np)):
            f, g = lattice_counts(w_ref, a, k)
            assert er.lattice_count_np(w_np, k) == (f[(1 << a) - 1], g[0])


def test_construction_minimum_is_the_optimum_by_simulation():
    """The row's audit fields agree with the lattice minimum, the share is at
    most one, and a complete graph has every order optimal."""
    for inst in _small_instances(12):
        comp = Compact(inst)
        if comp.a == 0:
            continue
        _comp, _s, c_np = er.lattice_weights(inst)
        k = er.lattice_minimum_np(c_np)
        row = er.lattice_row(inst, k)
        assert row["audit_construction"] and row["min_construction"] == k
        assert row["count_closing"] >= 1
        assert row["log10_share_closing"] <= 1e-9
    k3 = MOSPInstance.from_matrix([[1, 1, 1]] * 3, name="K3")      # one pattern, three customers: complete
    row = er.lattice_row(k3, 3)
    assert row["count_closing"] == math.factorial(3) and row["twin_factor"] == 6
    assert row["log10_share_closing"] == pytest.approx(0.0)
    assert max_open_stacks(k3, [0, 1, 2]) == 3


def test_row_rejects_a_wrong_optimum_in_the_audit():
    inst = generate_structured_instance(7, 7, 3, seed=3, name="f")
    _comp, _s, c_np = er.lattice_weights(inst)
    k = er.lattice_minimum_np(c_np)
    row = er.lattice_row(inst, k + 1)
    assert not row["audit_construction"] and row["min_construction"] == k
    assert er.lattice_count_np(c_np, k - 1) == (0, 0)


def _series(values, col_means, generator="fixed", lab="n", n=50, per_cell=30, noise=0.01, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for p, (v, c) in enumerate(zip(values, col_means)):
        for _ in range(per_cell):
            rows.append({"generator": generator, "ratio_label": lab, "n": n, "param": float(p), "col_mean": c,
                         "gap_floor": v + rng.normal(0, noise), "gap_beta": v + rng.normal(0, noise),
                         "ln_default": 1.0, "cens_default": False, "m": n, "r_exact": 1.0, "e": c - 1,
                         "optimum": 10, "opt_n": 0.2, "floor_001": 5, "floor_1": 5, "beta_star": 0.1,
                         "gap_floor_1": v})
    return pd.DataFrame(rows)


def test_peak_of_interior_vertex_and_interval():
    cols = [2.0, 3.0, 4.5, 7.0]
    inst = _series([0.10, 0.20, 0.18, 0.05], cols)
    cells = er.cell_frame(inst)
    pk = er.peak_of(cells, inst, "gap_floor", resamples=200)
    assert pk["gap_floor_interior"] and pk["gap_floor_peak_param"] == 1.0
    assert 3.0 < pk["gap_floor_peak_col_mean"] < 4.5          # vertex pulled toward the near-equal neighbour
    assert pk["gap_floor_ci_lo"] <= pk["gap_floor_peak_col_mean"] <= pk["gap_floor_ci_hi"]
    assert pk["gap_floor_ci_lo"] >= 3.0 and pk["gap_floor_ci_hi"] <= 4.5


def test_peak_of_edge_has_no_interval():
    inst = _series([0.30, 0.20, 0.10], [2.0, 3.0, 4.5])
    cells = er.cell_frame(inst)
    pk = er.peak_of(cells, inst, "gap_beta", resamples=50)
    assert not pk["gap_beta_interior"] and pk["gap_beta_peak_col_mean"] == 2.0
    assert np.isnan(pk["gap_beta_ci_lo"])


def test_cell_frame_means_and_errors():
    inst = _series([0.1, 0.2], [2.0, 3.0], noise=0.0)
    cells = er.cell_frame(inst)
    assert list(cells["gap_floor"]) == pytest.approx([0.1, 0.2])
    assert list(cells["gap_floor_se"]) == pytest.approx([0.0, 0.0])
    assert list(cells["instances"]) == [30, 30]


def test_profile_shapes():
    inst = pd.concat([_series([0.1, 0.2, 0.3], [2.0, 3.0, 4.0], lab="n", noise=0.0),
                      _series([0.3, 0.2, 0.1], [2.0, 3.0, 4.0], lab="2n", noise=0.0),
                      _series([0.1, 0.3, 0.2], [2.0, 3.0, 4.0], lab="n/2", noise=0.0)])
    prof = er.profile_table(er.cell_frame(inst)).set_index("ratio_label")
    assert prof.loc["n", "gap_floor_shape"] == "increasing"
    assert prof.loc["2n", "gap_floor_shape"] == "decreasing"
    assert prof.loc["n/2", "gap_floor_shape"] == "peaked"


def test_kill_verdict_rules():
    base = {"series": 25, "max_abs_log10_error": 0.3, "mean_signed_log10_error": 0.0, "within_ci": 0,
            "gap_peak_interior": 25}
    ok = pd.DataFrame([{"gap": "gap_floor", "mean_abs_log10_error": 0.05, "outside_ci": 10, **base},
                       {"gap": "gap_beta", "mean_abs_log10_error": 0.20, "outside_ci": 3, **base}])
    v = er.kill_verdict(ok)
    assert not v["gap_floor"]["dead"] and v["gap_beta"]["dead"] and not v["h1_dead"]
    dead = pd.DataFrame([{"gap": "gap_floor", "mean_abs_log10_error": 0.05, "outside_ci": 13, **base},
                         {"gap": "gap_beta", "mean_abs_log10_error": 0.16, "outside_ci": 0, **base}])
    v = er.kill_verdict(dead)
    assert v["gap_floor"]["dead"] and v["gap_beta"]["dead"] and v["h1_dead"]


def test_pooled_histogram():
    assert er.pooled_histogram(["2:3;4:1", "2:1;5:2"]) == {2: 4, 4: 1, 5: 2}
    assert er.sizes_from_text("3:10") == {3: 10}
