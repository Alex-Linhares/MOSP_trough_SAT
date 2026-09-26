"""Guards on the scale test (`learning.scale_test`, loop0002 item 06).

Every quantity the report quotes is exercised on data small enough to check
by hand: a conformal radius on seven residuals, a cell law interpolated
between two densities, a coverage table with a censored row, the first band
where an interval fails, the formula on a complete graph, and the scaling
read off a three-size frame with a known rate.
"""

import numpy as np
import pandas as pd
import pytest

from learning.scale_test import (
    band_of,
    cell_laws,
    conformal_quantile,
    corpus_linearity,
    corpus_scaling,
    coverage_table,
    first_failure,
    formula,
    law_predict,
    parse_name,
    ridge_predict,
)


def test_parse_name_and_band():
    assert parse_name("Random-125-125-2-4_0") == (125, 125, 2, 4)
    assert parse_name("Random-50-100-10-1_0") == (50, 100, 10, 1)
    assert band_of(30) == "30-40" and band_of(40) == "30-40" and band_of(75) == "75"


def test_conformal_quantile_by_hand():
    # seven residuals; ceil((7 + 1) * 0.9) = 8 -> clamped to the largest
    r = [0.1, -0.2, 0.3, -0.4, 0.5, -0.6, 0.7]
    assert conformal_quantile(r, 0.9) == pytest.approx(0.7)
    # nineteen residuals 1..19: ceil(20 * 0.9) = 18 -> the 18th smallest
    assert conformal_quantile(np.arange(1, 20), 0.9) == pytest.approx(18.0)
    assert np.isnan(conformal_quantile([], 0.9))


def test_law_predict_interpolates_in_log_col_mean():
    laws = pd.DataFrame({"d": [2.0, 4.0], "col_mean": [2.0, 4.0], "a": [0.0, 1.0], "b": [0.1, 0.2]})
    # at the ends: exactly the rows
    assert law_predict(laws, 10, 2.0) == pytest.approx(0.0 + 0.1 * 10)
    assert law_predict(laws, 10, 4.0) == pytest.approx(1.0 + 0.2 * 10)
    # midway in log10: col_mean = sqrt(8) -> (a, b) = (0.5, 0.15)
    assert law_predict(laws, 10, np.sqrt(8.0)) == pytest.approx(0.5 + 0.15 * 10)
    # clamped beyond the ends
    assert law_predict(laws, 10, 100.0) == pytest.approx(1.0 + 0.2 * 10)
    assert ridge_predict(laws.assign(d=[3.0, 4.0]), 20) == pytest.approx(0.0 + 0.1 * 20)


def test_coverage_table_with_censoring():
    pred = np.array([1.0, 1.0, 1.0, 1.0, 5.0, 5.0])
    truth = np.array([1.2, 0.5, 3.0, np.nan, 5.1, 9.0])       # one missing, one censored far above
    n = np.array([30, 30, 30, 30, 125, 125], dtype=float)
    band = np.array(["30-40"] * 4 + ["125"] * 2)
    censored = np.array([False, False, False, False, True, True])
    cov = coverage_table(pred, truth, n, band, radius_abs=1.0, radius_rel=0.01, censored=censored)
    small = cov[cov["band"] == "30-40"].iloc[0]
    assert small["observed"] == 3 and small["inside abs"] == 2 and small["coverage abs"] == pytest.approx(2 / 3)
    assert small["inside n-scaled"] == 1                        # radius 0.3 at n = 30: only |0.2| fits
    large = cov[cov["band"] == "125"].iloc[0]
    # censored at 5.1 with interval [4, 6]: undetermined; censored at 9 > 6: a definite miss
    assert large["undetermined (censored)"] == 1 and large["determined abs"] == 1 and large["coverage abs"] == 0.0
    # with no radius, coverage is undefined rather than zero
    cov_nan = coverage_table(pred, truth, n, band, radius_abs=np.nan, radius_rel=np.nan, censored=censored)
    assert cov_nan["coverage abs"].isna().all()


def test_first_failure():
    cov = pd.DataFrame({"band": ["30-40", "50", "75", "100", "125"],
                        "coverage abs": [0.9, 0.85, 0.6, 0.9, np.nan]})
    assert first_failure(cov, "coverage abs") == "75"
    assert first_failure(cov.assign(**{"coverage abs": [0.9, 0.9, 0.9, 0.9, 0.9]}), "coverage abs") == "holds through 125"


def test_formula_ends():
    # a complete graph (p = 1, so q = 1): the optimum is n, and the formula says n exactly
    assert formula(20, 5, 1.0) == pytest.approx(20.0)
    # no edges (p = 0): q = 0, D = 0 -> a·1 + n·(1 − c/c) = a
    assert formula(20, 5, 0.0, a=2.1, c=27.0) == pytest.approx(2.1)


def _tiny_corpus():
    rows = []
    for n in (30, 40, 50):
        for i in range(2):
            # nodes grow exactly 10x per 10 customers at d = 4; optimum is 0.5 n + 1
            rows.append({"instance_name": f"Random-{n}-{n}-4-{i + 1}_0", "n": n, "m": n, "d": 4,
                         "col_mean": 4.0, "optimum": 0.5 * n + 1, "nodes_default": 10.0 ** (n / 10),
                         "censored_default": False, "status_default": "unsat"})
    rows.append({"instance_name": "Random-50-50-4-3_0", "n": 50, "m": 50, "d": 4, "col_mean": 4.0,
                 "optimum": 26, "nodes_default": 10.0 ** 5, "censored_default": False, "status_default": "unsat"})
    return pd.DataFrame(rows)


def test_corpus_scaling_and_linearity_on_a_known_rate():
    c = _tiny_corpus()
    sc = corpus_scaling(c, "default")
    assert len(sc) == 1 and sc.iloc[0]["sizes with full counts"] == "30,40,50"
    assert sc.iloc[0]["rate"] == pytest.approx(0.1, abs=1e-6)
    assert sc.iloc[0]["better"] == "exponential"
    lin = corpus_linearity(c)
    assert lin.iloc[0]["slope"] == pytest.approx(0.5) and lin.iloc[0]["r²"] == pytest.approx(1.0)


def test_cell_laws_recover_a_planted_rate():
    rows = []
    for n in (15, 20, 25, 30):
        for i in range(5):
            rows.append({"generator": "fixed", "n": n, "m": n, "param": 3.0, "col_mean": 3.0,
                         "nodes_default": 10.0 ** (0.1 * n - 1.0)})
    laws = cell_laws(pd.DataFrame(rows), "default")
    assert laws.iloc[0]["b"] == pytest.approx(0.1) and laws.iloc[0]["a"] == pytest.approx(-1.0)
    assert laws.iloc[0]["doubling_n"] == pytest.approx(np.log10(2) / 0.1)
