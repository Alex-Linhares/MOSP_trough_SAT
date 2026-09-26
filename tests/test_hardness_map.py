"""Guards on the hardness-map analysis (`learning.hardness_map`).

Every quantity the report quotes is computed on a frame small enough to check
by hand: a synthetic campaign whose node counts are a known function of
`(n, col_mean)`, so the peak, its width, the scaling rate and the order
parameter are all known in advance.
"""

import numpy as np
import pandas as pd
import pytest

from learning.hardness_map import (
    _width_at,
    cell_table,
    collapse,
    fit_scaling,
    kill_verdict,
    monotone,
    peak_by_candidate,
    peaks,
    prepare,
    sharpness,
)


def synthetic(rate: float = 0.1, peak_at: float = 3.0, per_cell: int = 30, seed: int = 0) -> pd.DataFrame:
    """Two series (fixed m = n, bernoulli m = n), n in {20, 30, 40}, d in 2..6.

    Median nodes are 10 ** (rate * n - |log10(d / peak_at)| * 4), jittered
    by a small multiplicative noise, so the peak is at d = 3 at every n, the
    ridge grows exponentially at `rate` per customer, and `col_mean` is the
    exact order parameter (the Bernoulli series carries the same law in
    col_mean, with `param` = p = d / n so its nominal grid differs).
    """
    rng = np.random.default_rng(seed)
    rows = []
    for gen in ("fixed", "bernoulli"):
        for n in (20, 30, 40):
            for d in (2, 3, 4, 5, 6):
                param = d if gen == "fixed" else d / n
                for i in range(per_cell):
                    log_nodes = rate * n - 4 * abs(np.log10(d / peak_at)) + rng.normal(0, 0.05)
                    nodes = int(round(10 ** log_nodes))
                    optimum = max(2, int(round(0.3 * n * d / peak_at)))
                    rows.append({
                        "instance_name": f"{gen[0]}_n{n}_d{d}_i{i}", "cell": f"{gen[0]}:{n}:{n}:{param}",
                        "generator": gen, "n": n, "m": n, "param": param, "optimum": optimum,
                        "nodes_default": nodes, "nodes_csearch": nodes, "g_components": 1,
                        "col_mean": d + rng.normal(0, 0.01), "density": d / n,
                        "g_deg_mean": (d - 1) * d, "ub_best": optimum + 1, "lb_best": optimum - 1,
                        "graph_cert": f"{gen}{n}{d}{i}",
                    })
    return prepare(pd.DataFrame(rows))


def test_cell_table_medians_by_hand():
    frame = prepare(pd.DataFrame({
        "generator": ["fixed"] * 4, "n": [10] * 4, "m": [10] * 4, "param": [2, 2, 3, 3],
        "optimum": [3, 3, 4, 4], "nodes_default": [1, 5, 10, 20], "nodes_csearch": [1, 5, 10, 20],
        "g_components": [1, 2, 1, 1], "col_mean": [2.1, 2.1, 3.0, 3.0], "density": [0.2] * 4,
        "g_deg_mean": [3.0] * 4, "ub_best": [3, 3, 4, 4], "lb_best": [3, 3, 3, 3],
        "graph_cert": list("abcd"), "cell": ["x"] * 4, "instance_name": list("wxyz"),
    }))
    cells = cell_table(frame)
    assert list(cells["median"]) == [3.0, 15.0]
    assert list(cells["connected_share"]) == [0.5, 1.0]
    assert list(cells["opt_frac"]) == [0.3, 0.4]
    assert list(cells["bound_gap"]) == [0.0, 1.0]
    assert cells["zero_share"].tolist() == [0.0, 0.0]


def test_peak_is_found_interior_and_significant():
    frame = synthetic()
    pk = peaks(frame, resamples=200)
    assert (pk["peak_col_mean"].round(0) == 3).all()
    assert pk["interior"].all()
    assert pk["significant_left"].all() and pk["significant_right"].all()
    verdict = kill_verdict(pk, cell_table(frame))
    assert not verdict["overall"]["kill_fires"]
    assert verdict["fixed, m = 1n"]["monotone_at"] == []


def test_monotone_series_fires_the_kill():
    frame = synthetic()
    # make the fixed series monotone: nodes fall with d at every n
    fixed = frame["generator"] == "fixed"
    frame.loc[fixed, "nodes"] = (1000 / frame.loc[fixed, "col_mean"]).round()
    frame.loc[fixed, "log_nodes"] = np.log10(1 + frame.loc[fixed, "nodes"])
    cells = cell_table(frame)
    mono = monotone(cells)
    assert mono[mono["generator"] == "fixed"]["monotone"].all()
    assert not mono[mono["generator"] == "bernoulli"]["monotone"].any()
    verdict = kill_verdict(peaks(frame, cells, resamples=100), cells)
    assert verdict["fixed, m = 1n"]["kill_fires"]
    assert not verdict["bernoulli, m = 1n"]["kill_fires"]
    assert not verdict["overall"]["kill_fires"]


def test_width_interpolates_between_cells():
    x = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    y = np.array([0.0, 1.0, 2.0, 1.0, 0.0])
    width, note = _width_at(x, y, 1.5)
    assert width == pytest.approx(1.0)
    assert note == ""
    width, note = _width_at(x, y, -1.0)
    assert note == "left open; right open"
    assert width == pytest.approx(4.0)


def test_sharpness_width_is_the_known_tent():
    # log10 nodes = const - 4 |log10(d/3)|: half height (log10 2 below the peak)
    # is reached at |log10(d/3)| = log10(2)/4 on each side, so the full width is log10(2)/2
    sharp = sharpness(cell_table(synthetic()))
    assert np.allclose(sharp["width_half_log10"], np.log10(2) / 2, atol=0.03)


def test_scaling_recovers_the_exponential_rate():
    n = np.array([15, 20, 25, 30, 35, 40])
    fit = fit_scaling(n, 10 ** (0.1 * n + 0.5))
    assert fit["rate"] == pytest.approx(0.1, abs=1e-9)
    assert fit["doubling_n"] == pytest.approx(np.log10(2) / 0.1)
    assert fit["better"] == "exponential"
    fit = fit_scaling(n, 3.0 * n ** 2.5)
    assert fit["alpha"] == pytest.approx(2.5, abs=1e-9)
    assert fit["better"] == "power"
    assert fit_scaling(n, np.ones(6))["points"] == 0


def test_col_mean_is_the_order_parameter_of_the_synthetic_law():
    frame = synthetic()
    # the two synthetic series share one law, so any candidate has dispersion near 0;
    # what separates them is the variance a candidate explains at fixed n:
    # col_mean explains it all, the constant bound_gap none
    assert collapse(frame, "col_mean")["r2"].min() > 0.9
    assert collapse(frame, "bound_gap")["r2"].max() < 0.1
    assert collapse(frame, "col_mean")["dispersion"].max() < 0.1
    pk = peak_by_candidate(frame, "col_mean", bins=5, min_per_bin=10)
    assert (pk["peak_value"].round(0) == 3).all()
    assert pk["interior"].all()
