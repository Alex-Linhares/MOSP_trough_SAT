"""§37: the ridge's height -- the new cells, the candidate formulas, the
excess partial, the collapse statistic and the width crossings."""

import numpy as np
import pandas as pd
import pytest

from learning.ridge_height import (MODELS, _crossings, collapse_stats, design, excess_partial, fit,
                                   fit_points, fixed_n_table, height_cells, heldout, hundred_cell,
                                   model_table, predict, ratio_label)


def test_ratio_label_extends_to_4n_and_8n():
    assert ratio_label(200, 50) == "4n"
    assert ratio_label(400, 50) == "8n"
    assert ratio_label(37, 75) == "n/2"
    assert ratio_label(9, 75) == "n/8"
    assert ratio_label(150, 75) == "2n"


def test_height_cells_design():
    cells, counts = height_cells()
    assert len(cells) == 82 and len(set(cells)) == 82
    assert all(c.generator == "bernoulli" for c in cells if c.n < 100)
    assert sum(counts.values()) == 3380
    # p = c / n to four decimals; the n = 75 cells follow the cheap ones, the 100 cells come last
    c75 = [c for c in cells if c.n == 75]
    c100 = [c for c in cells if c.n == 100]
    assert cells[-len(c100):] == c100 and all(counts[c] == 30 for c in c100)
    assert cells[-len(c100) - len(c75): -len(c100)] == c75 and all(counts[c] == 20 for c in c75)
    assert any(c.m == 300 and c.param == round(1.6 / 75, 4) for c in c75)
    assert {c.m // c.n for c in cells if c.n < 100} == {2, 4, 8}
    assert {(c.generator, c.m) for c in c100} == {("fixed", 25), ("bernoulli", 25), ("fixed", 50), ("bernoulli", 50)}
    assert any(c.generator == "fixed" and c.m == 25 and c.param == 10.0 for c in c100)


def _synthetic_peaks(law, ns=(20, 30, 40, 50, 60, 75, 100), rs=(0.25, 0.5, 1.0, 2.0), generator="fixed"):
    rows = []
    for n in ns:
        for r in rs:
            m = int(round(r * n))
            ex = 2.0 + 0.1 * np.log2(r)          # varies across series, like the measured peaks
            rows.append({"config": "default", "generator": generator, "ratio_label": ratio_label(m, n),
                         "n": n, "m": m, "r_exact": m / n, "excess": ex, "peak_col_mean": 1 + 2.4 / (m / n),
                         "height": law(n, m, ex), "height_is_lower_bound": False})
    return pd.DataFrame(rows)


def test_design_shapes_match_parameter_counts():
    for model in MODELS:
        X = design(model, [10, 20], [10, 40], [2.0, 2.2], [3.4, 1.6])
        assert X.shape[0] == 2 and X.shape[1] >= 2


def test_fit_recovers_a_planted_n_g_r_law_exactly():
    law = lambda n, m, ex: 0.1 + n * (0.09 + 0.02 * np.log10(m / n))
    pts = fit_points(_synthetic_peaks(law))
    beta = fit("n·g(r) linear", pts)
    assert beta == pytest.approx([0.1, 0.09, 0.02], abs=1e-9)
    assert np.max(np.abs(predict("n·g(r) linear", beta, pts) - pts["height"])) < 1e-9
    for scheme in ("loso", "lono", "extrap75", "extrap100"):
        h = heldout("n·g(r) linear", pts, scheme)
        d = h - pts["height"]
        assert np.nanmax(np.abs(d)) < 1e-8
    assert np.isnan(heldout("n·g(r) linear", pts, "extrap75")[pts["n"] != 75]).all()
    assert np.isfinite(heldout("n·g(r) linear", pts, "extrap100")[pts["n"] == 100]).all()


def test_fit_recovers_the_log_clique_law_and_excess_adds_nothing():
    law = lambda n, m, ex: -0.16 + n * (0.13 - 0.077 * np.log10(1 + 2.4 * n / m))
    peaks = _synthetic_peaks(law)
    beta = fit("n·g(c*) log clique", fit_points(peaks))
    assert beta == pytest.approx([-0.16, 0.13, -0.077], abs=1e-9)
    ep = excess_partial(peaks, "fixed", base="n·g(c*) log clique")
    assert abs(ep["slope_per_unit_excess"]) < 1e-6 and ep["residual_sd"] < 1e-9


def test_model_table_reports_the_hundred_cell():
    law = lambda n, m, ex: 0.1 + n * (0.09 + 0.02 * np.log10(m / n))
    peaks = _synthetic_peaks(law)
    hundred = {"height": 9.1, "height_lo": 8.9, "height_hi": 9.3}
    mt = model_table(peaks, "fixed", hundred)
    row = mt[mt["model"] == "n·g(r) linear"].iloc[0]
    assert row["pred_100"] == pytest.approx(0.1 + 100 * 0.09)     # 9.1 exactly: inside
    assert bool(row["inside_100"]) and row["err_100"] == pytest.approx(0.0)
    assert row["loso_rmse"] < 1e-8 and row["params"] == 3
    assert row["extrap100_mae"] < 1e-8 and row["points"] == 24     # n = 100 is never fitted
    wrong = mt[mt["model"] == "n only"].iloc[0]
    assert wrong["loso_rmse"] > 0.1


def test_fixed_n_table_increments_per_doubling():
    peaks = pd.DataFrame({"generator": "fixed", "n": 50, "ratio_label": ["n/2", "n", "2n"],
                          "r_exact": [0.5, 1.0, 2.0], "m": [25, 50, 100], "height": [2.0, 3.0, 4.0],
                          "height_is_lower_bound": [False, False, True]})
    t = fixed_n_table(peaks).iloc[0]
    assert t["Δ/doubling n/2→n"] == pytest.approx(1.0) and t["Δ/doubling n→2n"] == pytest.approx(1.0)
    assert t["slope_log_height_per_log_m"] == pytest.approx(1 / np.log10(2))
    assert bool(t["h[2n] lb"]) and not bool(t["h[n] lb"])


def test_collapse_stats_perfect_and_broken():
    rng = np.random.default_rng(0)
    x = rng.uniform(0, 1, 200)
    series = np.array(["a", "b", "c", "d"] * 50)
    y = np.sin(3 * x)                          # one curve for every series
    st = collapse_stats(x, y, np.ones(200), series, bins=10)
    assert st["dispersion"] < 0.2 and st["r2"] > 0.95
    offset = np.where(series == "a", 5.0, 0.0)  # one series lifted by five decades
    st2 = collapse_stats(x, y + offset, np.ones(200), series, bins=10)
    assert st2["dispersion"] > 4.5 and st2["r2"] < 0.3


def test_crossings_on_a_triangle():
    x = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    y = np.array([0.0, 1.0, 2.0, 1.0, 0.0])
    lo, hi, le, he = _crossings(x, y, 1.0, 2)
    assert (lo, hi) == (1.0, 3.0) and not le and not he
    lo, hi, le, he = _crossings(x, y, 1.5, 2)
    assert (lo, hi) == pytest.approx((1.5, 2.5))
    lo, hi, le, he = _crossings(x, y, -1.0, 2)
    assert (lo, hi) == (0.0, 4.0) and le and he


def test_hundred_cell_matches_section_35():
    h = hundred_cell("default")
    assert h["exact"] == 1 and h["censored"] >= 20
    assert 9.9 < h["height_lo"] < h["height"] < h["height_hi"] < 10.8
