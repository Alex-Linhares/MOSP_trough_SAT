"""§19: the refutation cost model — Tobit with censoring, the decade rule, the noise floor,
the recertify table, and the dating of the upward run's csearch counts."""

import numpy as np
import pandas as pd
import pytest

from learning.cost_model import (CostModel, Tobit, band_of, date_upward_csearch, decade_claim, design, evaluate,
                                 noise_floor, open_lower_bound, prepare, recertify_rank_agreement, recertify_table,
                                 term_names, within_decade)


def test_bands_are_the_report_bands():
    assert [band_of(n) for n in (10, 20, 21, 40, 50, 60, 75, 82, 100, 125)] == \
        ["10-20", "10-20", "21-40", "21-40", "50-60", "50-60", "75", "75", "100", "125"]


def test_tobit_recovers_a_censored_law_where_least_squares_does_not():
    rng = np.random.default_rng(0)
    n = rng.uniform(10, 80, 4000)
    y_true = 1.0 + 0.1 * n + rng.normal(0, 0.3, len(n))
    cap = 6.0                                    # a deadline at 10^6 nodes
    cens = y_true > cap
    y = np.where(cens, cap, y_true)
    X = np.column_stack([np.ones(len(n)), n])
    ols = np.linalg.lstsq(X, y, rcond=None)[0]   # treats the lower bounds as values
    tob = Tobit().fit(X, y, cens)
    slope_t = tob.coefficients(["1", "n"]).set_index("term").loc["n", "coef"]
    assert cens.mean() > 0.3                     # the censoring is heavy enough to matter
    assert abs(slope_t - 0.1) < 0.005
    assert abs(ols[1] - 0.1) > 0.02              # least squares is pulled down by the censored rows
    assert abs(tob.sigma_ - 0.3) < 0.03
    assert np.allclose(tob.predict(X[:3]), tob.predict(X[:3]))


def test_tobit_without_censoring_is_least_squares():
    rng = np.random.default_rng(1)
    X = np.column_stack([np.ones(500), rng.normal(size=500), rng.normal(size=500)])
    y = X @ np.array([2.0, -1.0, 0.5]) + rng.normal(0, 0.1, 500)
    tob = Tobit(ridge=0.0).fit(X, y, np.zeros(500, bool))
    ols = np.linalg.lstsq(X, y, rcond=None)[0]
    assert np.allclose(tob.coefficients(["1", "a", "b"])["coef"], ols, atol=1e-3)


def test_within_decade_treats_a_censored_count_as_a_lower_bound():
    pred = np.array([5.0, 5.0, 5.0, 5.0, 5.0])
    y = np.array([5.5, 6.5, 4.5, 6.5, 3.5])
    cens = np.array([False, False, False, True, True])
    # settled: |5 − 5.5| ≤ 1 hit; |5 − 6.5| miss; |5 − 4.5| hit
    # censored ≥ 6.5: prediction 5 is more than a decade below the lower bound → miss
    # censored ≥ 3.5: the truth could be anywhere above 3.5, including within a decade → hit
    assert within_decade(pred, y, cens).tolist() == [True, False, True, False, True]
    claim = decade_claim(pred, y, cens)
    assert claim["counts"] == 5 and claim["censored"] == 2
    assert claim["within_decade"] == pytest.approx(3 / 5)
    assert claim["within_decade_settled"] == pytest.approx(2 / 3)
    assert claim["kill_met"] is True             # 60% < 80%


def test_evaluate_by_band_uses_settled_counts_for_the_errors():
    ev = evaluate(pred=np.array([1.0, 2.0, 9.0, 9.0]), y=np.array([1.5, 2.0, 9.5, 8.0]),
                  censored=np.array([False, False, False, True]), n=np.array([10, 20, 100, 100]))
    b = ev.set_index("band")
    assert b.loc["10-20", "MAE"] == pytest.approx(0.25) and b.loc["10-20", "settled"] == 2
    assert b.loc["100", "counts"] == 2 and b.loc["100", "censored"] == 1
    assert b.loc["100", "MAE"] == pytest.approx(0.5)          # the censored row is not in the MAE
    assert b.loc["100", "under_lower_bound"] == 0.0           # 9.0 ≥ 8.0: not under the bound
    assert b.loc["100", "within_decade"] == 1.0


def _synthetic_frame(rng, sizes, per=40, rate=0.1, drift=0.0):
    rows = []
    for n in sizes:
        for i in range(per):
            cm = rng.choice([2.0, 3.0, 4.0, 6.0])
            nodes = 10 ** (0.5 + (rate - drift * n) * n * (1 - 0.1 * abs(cm - 3)) + rng.normal(0, 0.05)) - 1
            rows.append({"instance_name": f"s{n}_{i}", "source": "campaign", "n": n, "m": n, "optimum": 0.3 * n,
                         "col_mean": cm, "g_deg_mean": cm * 2, "g_deg_std": 1.0, "g_largest_comp_frac": 1.0,
                         "g_components": 1, "tw_min_fill": 0.3 * n, "g_degeneracy": 0.2 * n, "g_clustering": 0.5,
                         "row_mean": cm, "nodes_default": nodes, "status_default": "unsat",
                         "nodes_csearch": nodes, "status_csearch": "unsat"})
    return prepare(pd.DataFrame(rows))


def test_cost_model_extrapolates_an_exact_exponential_law():
    rng = np.random.default_rng(2)
    train = _synthetic_frame(rng, (20, 30, 40, 50, 60))
    test = _synthetic_frame(rng, (100,), per=20)
    model = CostModel(drift=False).fit(train, "default")
    err = model.predict(test) - test["y_default"].to_numpy()
    assert np.abs(err).mean() < 0.15             # 40 customers beyond the fit, inside a sixth of a decade
    assert design(train, drift=True).shape[1] == len(term_names(True))
    assert design(train, drift=False).shape[1] == len(term_names(False)) == len(term_names(True)) - 2


def test_noise_floor_is_the_sd_over_labellings(tmp_path):
    rows = []
    for inst, vals in (("a", [1000, 1000, 1000, 1000]), ("b", [10 ** 4, 10 ** 4.2, 10 ** 4.4, 10 ** 4.6])):
        for k, v in enumerate(vals):
            rows.append({"base_name": inst, "labelling": f"l{k}", "n": 50, "config": "csearch",
                         "status_lo": "unsat", "nodes_lo": v - 1, "source": "campaign"})
    port = tmp_path / "p.csv.gz"
    pd.DataFrame(rows).to_csv(port, index=False)
    out = noise_floor(portfolio=port, differential=tmp_path / "missing.csv.gz")
    assert len(out) == 1 and out.iloc[0]["instances"] == 2
    sd_b = np.std([4.0, 4.2, 4.4, 4.6], ddof=1)
    assert out.iloc[0]["sd_median"] == pytest.approx(sd_b / 2)            # median of {0, sd_b}
    assert out.iloc[0]["sd_median_hard(≥1e4 nodes)"] == pytest.approx(sd_b)


class _Const:
    def __init__(self, table):
        self.table = table

    def predict(self, frame):
        return np.array([self.table[i] for i in frame["instance_name"]])


def test_recertify_table_ranks_cheapest_first_and_bounds_the_open_entry(tmp_path):
    rec = tmp_path / "results.json"
    import json
    json.dump([{"name": "Random-125-125-4-5_0", "value": 46, "status": "unsat", "nodes": 10 ** 10, "seconds": 5000.0},
               {"name": "Random-125-125-2-1_0", "value": 24, "status": "unsat", "nodes": 10 ** 11, "seconds": 50000.0}],
              open(rec, "w"))
    names = ["Random-125-125-4-5_0", "Random-125-125-2-1_0", "Random-125-125-2-2_0"]
    frame = pd.DataFrame({"instance_name": names, "optimum": [46, 24, 25], "col_mean": [3.9, 2.7, 2.8]})
    model = _Const({"Random-125-125-4-5_0": 10.2, "Random-125-125-2-1_0": 11.1, "Random-125-125-2-2_0": 10.5})
    started, now = 1000.0, 1000.0 + 36000.0            # ten hours in
    out = recertify_table(frame, {"m": model}, None, recertify=rec, started=started, now=now)
    assert out["instance"].tolist() == ["Random-125-125-4-5_0", "Random-125-125-2-2_0", "Random-125-125-2-1_0"]
    assert out["cheapest_first_rank"].tolist() == [1, 2, 3]
    open_row = out[out["status"] == "open"].iloc[0]
    assert open_row["running_hours"] == pytest.approx(10.0)
    # seconds per node: median of 5e-7 and 5e-7 = 5e-7; 36000 s → 7.2e10 nodes
    assert open_row["log10_nodes_at_least"] == pytest.approx(np.log10(1 + 36000 / 5e-7))
    assert np.isnan(out[out["status"] == "unsat"]["running_hours"]).all()
    assert out.set_index("instance").loc["Random-125-125-4-5_0", "pred_hours_m"] == pytest.approx(10 ** 10.2 * 0.55e-6 / 3600)
    agree = recertify_rank_agreement(out, "pred_m")
    assert agree["finished"] == 2 and np.isnan(agree["spearman"])      # fewer than three finished: no rank statistic
    assert all(np.isnan(v) for v in open_lower_bound({}, started, now))  # nothing finished: no rate, no bound


def test_date_upward_csearch_reads_pre_and_post_fix_cells(tmp_path):
    up = pd.DataFrame({"instance_name": ["a1", "a2", "b1", "b2", "c1"], "cell": ["A", "A", "B", "B", "C"],
                       "nodes_csearch": [100, 200, 300, 400, 500], "row_mean": [3.0, 3.0, 3.0, 3.0, 8.0]})
    port = pd.DataFrame({"base_name": ["a1", "a2", "b1", "b2", "c1"], "labelling": ["identity"] * 5,
                         "source": ["campaign"] * 5, "nodes_lo": [100, 200, 300, 999, 500]})
    up_csv, port_csv = tmp_path / "up.csv", tmp_path / "port.csv.gz"
    up.to_csv(up_csv, index=False)
    port.to_csv(port_csv, index=False)
    out = date_upward_csearch(up_csv, port_csv).set_index("cell")
    assert out.loc["A", "verdict"] == "all equal: post-fix"
    assert out.loc["B", "verdict"] == "differs: pre-fix"
    assert out.loc["C", "verdict"] == "rule off: pre = post"
