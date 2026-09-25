"""`learning.formula_search` on frames small enough to check by hand.

Nothing here touches the solver, the corpus or `solutions/`; the searches run
single-process on a few dozen rows.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("sklearn")

from learning.formula_search import (  # noqa: E402
    bound_check,
    enumerate_terms,
    fit_term_lad,
    lad_cv,
    evaluate_terms,
    fit_term,
    folds_of,
    format_term,
    holdout_mask,
    nested,
    ols_cv,
    pair_search,
    search,
)


def test_format_term_reads_as_a_product_and_ratio():
    assert format_term((("a", 1.0), ("b", 0.5), ("c", -1.0))) == "a · sqrt(b) / c"
    assert format_term((("a", 2.0), ("b", -1.0), ("c", -0.5))) == "a² / (b · sqrt(c))"
    assert format_term((("a", -1.0),)) == "1 / a"
    assert format_term((("a", -2.0),)) == "1 / a²"


def test_enumerate_terms_counts_and_refuses_to_divide_by_a_zero_column():
    # Two columns, `z` has a zero somewhere: no negative exponent on it.
    terms = enumerate_terms(["p", "z"], positive={"p"}, max_degree=1)
    assert len(terms) == 6 + 3          # p: six exponents; z: only 0.5, 1, 2
    assert all(e > 0 for (f, e), in [t for t in terms if t[0][0] == "z"])
    # Degree 2: 5 x 5 exponent pairs minus the ones with z negative (2 x 5).
    pairs = [t for t in enumerate_terms(["p", "z"], {"p"}, 2) if len(t) == 2]
    assert len(pairs) == 25 - 10
    # Degree 3 on three positive columns: eight sign patterns for the one triple.
    triples = [t for t in enumerate_terms(["a", "b", "c"], {"a", "b", "c"}, 3) if len(t) == 3]
    assert len(triples) == 8


def test_evaluate_terms_by_hand():
    values = {"a": np.array([2.0, 3.0]), "b": np.array([4.0, 9.0]), "c": np.array([1.0, 2.0])}
    T = evaluate_terms(values, [(("a", 1.0), ("b", 0.5), ("c", -1.0)), (("c", 2.0),)])
    np.testing.assert_allclose(T[0], [2 * 2 / 1, 3 * 3 / 2])
    np.testing.assert_allclose(T[1], [1.0, 4.0])


def test_ols_cv_recovers_an_exact_line_and_flags_a_constant_term():
    rng = np.random.default_rng(0)
    x = rng.uniform(1, 10, 40)
    y = 2.0 * x + 1.0
    T = np.stack([x, np.ones(40), np.where(np.arange(40) == 3, np.inf, x)])
    folds = folds_of(None, 40, n_splits=4)
    mae, exact = ols_cv(T, y, folds)
    assert mae[0] == pytest.approx(0.0, abs=1e-9) and exact[0] == 1.0
    assert mae[1] > 1.0                       # a constant term predicts the fold mean only
    assert np.isinf(mae[2])                   # a non-finite term is never a winner
    a, b = fit_term(x, y)
    assert (a, b) == pytest.approx((2.0, 1.0))


def _toy_frame(seed=0, n=60):
    rng = np.random.default_rng(seed)
    values = {
        "x1": rng.uniform(1, 5, n), "x2": rng.uniform(1, 5, n), "x3": rng.uniform(1, 5, n),
    }
    groups = np.repeat(np.arange(6), n // 6)
    return values, groups


def test_search_finds_the_planted_product_under_a_grouped_split():
    values, groups = _toy_frame()
    y = values["x1"] * values["x2"] + 3.0
    folds = folds_of(groups, len(y), n_splits=3)
    table, n_terms = search(values, y, folds, ["x1", "x2", "x3"], max_degree=2, keep=5, workers=1)
    assert table.iloc[0]["formula"] == "x1 · x2"
    assert table.iloc[0]["mae"] == pytest.approx(0.0, abs=1e-9)
    assert (table.iloc[0]["a"], table.iloc[0]["b"]) == pytest.approx((1.0, 3.0))
    assert n_terms == 3 * 6 + 3 * 25


def test_pair_search_recovers_a_planted_two_term_law():
    values, groups = _toy_frame(seed=1)
    y = 3.0 * values["x1"] + 2.0 * values["x3"] ** 2 - 1.0
    folds = folds_of(groups, len(y), n_splits=3)
    terms = [(("x1", 1.0),), (("x2", 1.0),), (("x3", 2.0),), (("x1", 1.0), ("x2", 1.0))]
    pairs = pair_search(values, y, folds, terms, keep=3)
    best = pairs.iloc[0]
    assert best["terms"] == ((("x1", 1.0),), (("x3", 2.0),))
    assert best["mae"] == pytest.approx(0.0, abs=1e-8)
    assert best["coef"] == pytest.approx((3.0, 2.0, -1.0), abs=1e-8)


def test_nested_protocol_scores_only_held_out_groups():
    values, groups = _toy_frame(seed=2)
    y = values["x2"] / values["x1"] + 0.5
    res = nested(values, y, groups, ["x1", "x2", "x3"], max_degree=2, n_splits=3, workers=1)
    assert res["monomial"]["mae"] == pytest.approx(0.0, abs=1e-8)
    assert res["pair"]["mae"] == pytest.approx(0.0, abs=1e-6)
    assert len(res["winners"]) == 3
    assert all(w["monomial"] == "x2 / x1" for w in res["winners"])


def test_holdout_mask_holds_out_every_fifth_file():
    files = pd.Series([f"f{i}" for i in range(10)] * 2)
    mask = holdout_mask(files)
    assert sorted(files[mask].unique()) == ["f0", "f5"]
    assert mask.sum() == 4


def test_bound_check_counts_rounded_misses():
    optimum = np.array([3.0, 5.0, 7.0, 9.0])
    pred = np.array([3.4, 4.4, 7.6, 12.0])
    assert bound_check(pred, optimum) == {"below": 1, "above": 2, "max_below": 1.0, "max_above": 3.0}


def test_lad_constants_follow_the_bulk_not_the_tail():
    # y = t + 1 on every row but one outlier: LAD recovers (1, 1); OLS does not.
    t = np.arange(1.0, 41.0)
    y = t + 1.0
    y[-1] += 60.0
    a, b = fit_term_lad(t, y)
    assert (a, b) == pytest.approx((1.0, 1.0), abs=1e-2)
    a_ols, b_ols = fit_term(t, y)
    assert abs(a_ols - 1.0) > 0.05
    mae, exact = lad_cv(t[None, :], y, folds_of(None, 40, n_splits=4))
    assert exact[0] >= 0.95 and mae[0] < 2.0
