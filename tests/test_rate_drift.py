"""Tests for `learning.rate_drift` (loop0004 item 08): the laws and their
rates, the censored likelihood on synthetic series, the cell location by
hand, the fix-cost pairing, the comparison with the record."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from learning import rate_drift as rd


def _synthetic(rate=0.1, intercept=1.0, sigma=0.2, sizes=(10, 20, 30, 40, 50, 75, 100), per=60,
               censor_at=None, seed=3):
    rng = np.random.default_rng(seed)
    rows = []
    for n in sizes:
        y = intercept + rate * n + rng.normal(0, sigma, size=per)
        for i, v in enumerate(y):
            cens = censor_at is not None and n == 100 and v > censor_at
            rows.append({"instance_name": f"s{n}_{i}", "n": n, "d": 3.0, "config": "t",
                         "log_nodes": censor_at if cens else v, "censored": bool(cens),
                         "source": "synthetic", "value_certified": True})
    return pd.DataFrame(rows)


def test_rate_is_the_derivative_of_the_mean():
    n = np.array([40.0, 75.0, 100.0])
    for model, theta in (("exponential", [0.1, 0.09]), ("quadratic", [0.1, 0.09, -1e-4]),
                         ("power", [-2.0, 5.0]), ("saturating", [0.1, 0.08, 0.12, np.log(40.0)])):
        theta = np.array(theta)
        h = 1e-4
        numeric = (rd.mean_of(model, theta, n + h) - rd.mean_of(model, theta, n - h)) / (2 * h)
        assert np.allclose(numeric, rd.rate_of(model, theta, n), atol=1e-6), model


def test_tobit_recovers_an_exact_exponential_under_censoring():
    frame = _synthetic(rate=0.1, intercept=1.0, sigma=0.2, censor_at=10.6)   # the 100 cell's true mean is 11.0
    assert frame[(frame["n"] == 100)]["censored"].mean() > 0.9
    r = rd.fit(frame, "exponential", 10, 100)
    assert abs(r["rate_100"] - 0.1) < 0.005
    assert abs(r["mean_125"] - 13.5) < 0.15
    # reading the censored counts as exact biases the top cell and the extrapolation down
    naive = rd.fit(frame.assign(censored=False), "exponential", 10, 100)
    assert naive["mean_125"] < r["mean_125"] - 0.05
    # the quadratic finds no curvature in a straight line
    q = rd.fit(frame, "quadratic", 10, 100)
    assert abs(q["theta"][2]) < 3e-5
    # the power law is the worse shape for an exponential series
    p = rd.fit(frame, "power", 10, 100)
    assert p["aic"] > r["aic"] + 50


def test_cell_location_by_hand():
    exact = pd.DataFrame({"n": [100] * 3, "log_nodes": [1.0, 1.0, 1.0], "censored": [False] * 3})
    loc = rd.cell_location(exact, 100, sigma=1.0)
    assert abs(loc["location"] - 1.0) < 1e-2 and loc["exact"] == 3 and loc["censored"] == 0
    # one exact count at 1 and two lower bounds at 1: the MLE sits above 1 and above the censored median
    mixed = pd.DataFrame({"n": [100] * 3, "log_nodes": [1.0, 1.0, 1.0], "censored": [False, True, True]})
    loc = rd.cell_location(mixed, 100, sigma=0.5)
    assert loc["location"] > 1.0 and loc["censored_median"] == 1.0
    assert loc["location_lo"] <= loc["location"] <= loc["location_hi"]
    # all censored: no upper end
    allc = pd.DataFrame({"n": [100] * 3, "log_nodes": [1.0, 1.0, 1.0], "censored": [True] * 3})
    assert rd.cell_location(allc, 100, sigma=0.5)["location_hi"] == np.inf


def test_bootstrap_band_covers_the_fit():
    frame = _synthetic(per=25, censor_at=10.6)
    r = rd.fit(frame, "exponential", 10, 100)
    b = rd.bootstrap_fit(frame, "exponential", 10, 100, resamples=15)
    assert b["resamples"] == 15
    assert b["mean_125_lo"] <= r["mean_125"] + 0.1 and b["mean_125_hi"] >= r["mean_125"] - 0.1


def test_fix_cost_pairing(tmp_path):
    calls = pd.DataFrame([
        {"instance_name": "a", "purpose": "descent", "config": "csearch", "k": 9, "status": "unknown", "nodes": 10 ** 9, "seconds": 1, "deadline_seconds": 1, "achieved": None, "started": 0, "finished": 0},
        {"instance_name": "b", "purpose": "descent", "config": "csearch", "k": 9, "status": "unsat", "nodes": 10 ** 8, "seconds": 1, "deadline_seconds": 1, "achieved": None, "started": 0, "finished": 0},
        {"instance_name": "c", "purpose": "descent", "config": "csearch", "k": 9, "status": "unknown", "nodes": 10 ** 9, "seconds": 1, "deadline_seconds": 1, "achieved": None, "started": 0, "finished": 0},
    ])
    price = pd.DataFrame({"instance_name": ["a", "b", "c"], "ub_best": [10, 10, 10], "index": [0, 1, 2]})
    prefix = pd.DataFrame([
        {"instance_name": "a", "config": "csearch-prefix", "k": 9, "status": "unsat", "nodes": 10 ** 8, "seconds": 5, "deadline_seconds": 9, "achieved": None, "started": 0, "finished": 0},
        {"instance_name": "b", "config": "csearch-prefix", "k": 9, "status": "unsat", "nodes": 10 ** 7, "seconds": 5, "deadline_seconds": 9, "achieved": None, "started": 0, "finished": 0},
        {"instance_name": "c", "config": "csearch-prefix", "k": 9, "status": "sat", "nodes": 10 ** 7, "seconds": 5, "deadline_seconds": 9, "achieved": 9, "started": 0, "finished": 0},
    ])
    cp, pp, xp = tmp_path / "calls.csv", tmp_path / "price.csv", tmp_path / "prefix.csv"
    calls.to_csv(cp, index=False); price.to_csv(pp, index=False); prefix.to_csv(xp, index=False)
    fc = rd.fix_cost_100(xp, cp, pp).set_index("instance_name")
    assert fc.loc["a", "ratio_reading"] == "lower bound" and abs(fc.loc["a", "ratio"] - 10.0) < 1e-6
    assert fc.loc["b", "ratio_reading"] == "exact" and abs(fc.loc["b", "ratio"] - 10.0) < 1e-6
    assert fc.loc["b", "value_certified"]
    assert fc.loc["c", "pre_status"] == "sat" and "ratio" not in fc.columns or pd.isna(fc.loc["c", "ratio"])
    # c's value was not optimal: it leaves every series at 100
    s = rd.ridge100_series("csearch", xp, cp, pp)
    assert set(s["instance_name"]) == {"a", "b"}
    s = rd.ridge100_series("csearch-prefix", xp, cp, pp)
    assert set(s["instance_name"]) == {"a", "b"} and not s["censored"].any()


def test_compare_with_record_counts_inside_band():
    readings = pd.DataFrame({"reading": ["x", "y"], "mean_125": [11.0, 12.0], "lo_125": [10.5, 11.9], "hi_125": [11.5, 12.1]})
    rec = pd.DataFrame({"name": ["p", "q", "r"], "d": [2, 2, 4], "log_nodes": [11.2, 11.6, 10.7], "hours": [1, 1, 1]})
    out = rd.compare_with_record(readings, rec, 3.0).set_index("reading")
    assert out.loc["x", "record_inside_band"] == 1 and out.loc["y", "record_inside_band"] == 0
    assert abs(out.loc["x", "record_median_minus_mean"] - 0.4) < 1e-9
    assert abs(rd.hours(np.log10(1.4e6 * 3600)) - 1.0) < 1e-9


def test_records_on_disk():
    rec = rd.recertify_counts()
    assert len(rec) == 6 and set(rec["d"]) == {2, 4} and (rec["rule"] == "pre-fix csearch").all()
    c = rd.corpus100()
    assert set(c["config"]) == {"default", "csearch"} and set(c["d"]) == {2, 4}
    fr = rd.campaign_series("default", 3.0)
    assert fr["n"].max() == 75 and not fr["censored"].any() and fr["value_certified"].all()
    assert set(rd.campaign_series("csearch-prefix", 3.0)["n"]) == set(fr["n"])


def test_fix_ratio_summary_and_class_cost():
    fc = pd.DataFrame({"instance_name": ["a", "b", "c"], "ratio": [2.0, 4.0, np.nan],
                       "ratio_reading": ["exact", "lower bound", None]})
    s = rd.fix_ratio_summary(fc)
    assert s["pairs"] == 2 and s["exact_pairs"] == 1 and s["median_is_lower_bound"] and abs(s["median_ratio"] - 3.0) < 1e-9
    readings = pd.DataFrame({"reading": ["Tobit exponential 10–100", "Tobit exponential 10–100"],
                             "cell_100": ["censored", "dropped"], "mean_125": [np.log10(1.4e6 * 3600), 5.0],
                             "lo_125": [9.0, 4.0], "hi_125": [10.0, 6.0]})
    cost = rd.class_cost_table({3.0: readings}, s)
    assert len(cost) == 1 and abs(cost["hours_prefix_csearch"].iloc[0] - 1.0) < 1e-9
    assert abs(cost["hours_postfix_csearch"].iloc[0] - 3.0) < 1e-9 and cost["postfix_reading"].iloc[0].startswith("≥")
    assert cost["record_log10"].iloc[0].count(",") == 2   # the three Random-125-125-2 counts on record
