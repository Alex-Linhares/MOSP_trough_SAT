"""§16: the upward grid, its price, and the censoring-aware rate machinery."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from learning.ensemble import (Cell, RIDGE100_CORE_HOURS_CAP, price_ridge100, ridge100_cells, run,
                               upward_cells)
from learning.upward import (censored_median, drift, finish_uncertified, load_all, local_rates,
                             pooled_drift, prepare, cell_stats)


def test_upward_grid_is_the_one_the_plan_asked_for():
    cells = upward_cells()
    assert len(cells) == 3 * 3 * (9 + 6) == 135
    assert sum(50 for _ in cells) == 6750
    ms = {(c.n, c.m) for c in cells}
    assert (75, 37) in ms and (50, 25) in ms and (60, 30) in ms      # m = n // 2, never generated before
    assert (75, 150) in ms and (50, 50) in ms
    assert all(c.param <= c.n for c in cells)
    assert {c.id for c in ridge100_cells()} == {"f_n100_m100_d2", "f_n100_m100_d3", "f_n100_m100_d4"}
    assert len(set(cells)) == len(cells)                             # no cell twice


def _synthetic_campaign(a: float, b: float, sizes=(15, 20, 25, 30, 35, 40), per_cell: int = 5,
                        minus_one: bool = True) -> pd.DataFrame:
    """Fixed d = 3, m = n cells whose node counts are 10^(a + b n) - 1, so that
    log10(1 + nodes) is exactly a + b n; `minus_one=False` for the raw law."""
    rows = []
    for n in sizes:
        for i in range(per_cell):
            rows.append({"instance_name": f"s{n}_{i}", "cell": f"f_n{n}_m{n}_d3", "generator": "fixed",
                         "n": n, "m": n, "param": 3.0, "index": i, "certified": True, "witness_ok": True,
                         "optimum": 5, "nodes_default": 10 ** (a + b * n) - (1 if minus_one else 0),
                         "nodes_csearch": 10 ** (a + b * n) - (1 if minus_one else 0),
                         "status_default": "unsat", "status_csearch": "unsat", "col_mean": 3.0,
                         "g_components": 1, "complete_graph": False, "graph_cert": f"c{n}{i}", "row_mean": 3.0,
                         "total_seconds": 0.1})
    return pd.DataFrame(rows)


def test_price_ridge100_is_the_closed_form(tmp_path: Path):
    a, b = -0.2, 0.095
    csv = tmp_path / "results.csv"
    _synthetic_campaign(a, b, minus_one=False).to_csv(csv, index=False)
    price = price_ridge100(csv, per_cell=25, calls_per_instance=3.0, ds=(3,), nodes_per_second=2e6)
    expected_seconds = 10 ** (a + b * 100) / 2e6
    assert price.iloc[0]["log10_median_nodes_at_100"] == pytest.approx(a + b * 100, abs=0.01)
    assert price.iloc[0]["median_refutation_s"] == pytest.approx(expected_seconds, rel=0.01)
    assert price.attrs["total_core_hours"] == pytest.approx(expected_seconds * 3 * 25 / 3600, rel=0.01)
    assert price.attrs["cap_core_hours"] == RIDGE100_CORE_HOURS_CAP
    assert price.attrs["within_cap"] is False                        # 10^9.3 nodes x 75 calls is days


def test_local_rates_recover_an_exact_exponential_with_zero_drift():
    frame = prepare(_synthetic_campaign(0.5, 0.1, sizes=(20, 30, 40, 50, 60, 75)))
    rates = local_rates(frame, "default", resamples=50)
    assert len(rates) == 5
    assert np.allclose(rates["rate"], 0.1, atol=1e-6)
    assert (rates["reading"] == "exact").all()
    assert np.allclose(rates["rate_lo"], 0.1, atol=1e-6) and np.allclose(rates["rate_hi"], 0.1, atol=1e-6)
    d = drift(rates)
    assert len(d) == 1 and d.iloc[0]["slope_per_customer"] == pytest.approx(0.0, abs=1e-9)
    assert pooled_drift(rates)["intervals"] == 5


def test_censored_median_is_flagged_as_a_lower_bound():
    med, lb = censored_median([1.0, 2.0, 3.0, 4.0, 5.0], [False, False, False, False, True])
    assert med == 3.0 and lb is False                                # the censored value is above the median
    med, lb = censored_median([1.0, 2.0, 3.0, 4.0, 5.0], [False, False, True, False, False])
    assert med == 3.0 and lb is True                                 # the median itself is censored
    frame = _synthetic_campaign(0.0, 0.1, sizes=(30, 40), per_cell=4)
    frame.loc[frame["n"] == 40, "status_default"] = ["unsat", "unknown", "unknown", "unknown"]
    cells = cell_stats(prepare(frame), "default")
    at40 = cells[cells["n"] == 40].iloc[0]
    assert at40["censored"] == 3 and bool(at40["median_is_lower_bound"]) is True
    rates = local_rates(prepare(frame), "default", resamples=20)
    assert rates.iloc[0]["reading"] == "rate is a lower bound"


def test_run_honours_per_cell_counts(tmp_path: Path):
    hard, easy = Cell("fixed", 8, 8, 2), Cell("bernoulli", 8, 8, 0.3)
    frame = run([hard, easy], per_cell=3, workers=1, csv=tmp_path / "r.csv", instance_dir=None,
                solutions_dir=tmp_path / "sol", verbose=False, counts={hard: 1})
    assert len(frame) == 4
    assert (frame["cell"] == hard.id).sum() == 1 and (frame["cell"] == easy.id).sum() == 3
    assert list(frame["cell"])[0] == hard.id                         # the named cell ran first
    both = load_all(tmp_path / "r.csv", tmp_path / "missing.csv")
    assert set(both["source"]) == {"campaign"} and "ratio" in both


def test_finish_uncertified_certifies_a_row_whose_descent_ran_out(tmp_path: Path):
    cell = Cell("fixed", 8, 8, 2)
    csv = tmp_path / "r.csv"
    frame = run([cell], per_cell=2, workers=1, csv=csv, instance_dir=None,
                solutions_dir=tmp_path / "sol", verbose=False)
    assert frame["certified"].all()
    # pretend the second row's descent ran out at its true value: no refutation recorded
    frame.loc[1, ["certified", "status_default", "status_csearch"]] = [False, "uncertified", "uncertified"]
    frame.loc[1, ["nodes_default", "nodes_csearch"]] = np.nan
    frame.to_csv(csv, index=False)
    out = finish_uncertified(csv, deadline=60, workers=1, min_n=8, verbose=False, out=tmp_path / "fin.csv")
    assert bool(out.loc[1, "certified"]) is True
    assert out.loc[1, "status_default"] == "unsat" and out.loc[1, "status_csearch"] == "unsat"
    assert out.loc[1, "nodes_default"] >= 0
    assert out.loc[1, "solve_proof"] == "refutation (finish stage)"
    assert bool(pd.read_csv(csv).loc[1, "certified"]) is False       # the run's file is never rewritten
    assert len(pd.read_csv(tmp_path / "fin.csv")) == 2                # one answer per configuration
    again = finish_uncertified(csv, deadline=60, workers=1, min_n=8, verbose=False, out=tmp_path / "fin.csv")
    assert len(pd.read_csv(tmp_path / "fin.csv")) == 2                # answered calls are not repeated
    assert bool(again.loc[1, "certified"]) is True
