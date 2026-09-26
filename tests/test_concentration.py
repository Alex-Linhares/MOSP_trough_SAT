"""Guards on the concentration study (`learning.concentration`).

Every quantity the report quotes is computed here on a frame small enough to
check by hand: the nominal random-intersection-graph features, the per-cell
moments, the kill verdict, the linear law, the sandwich position λ, the
pathwidth-minus-treewidth bracket, and the saturating structural fit on
exact synthetic data.
"""

import numpy as np
import pandas as pd
import pytest

from learning import hardness_map
from learning.concentration import (
    cell_stats,
    kill_verdict,
    linearity,
    nominal_features,
    prepare,
    regime_of,
    structural_fits,
)


def _frame(rows: list[dict]) -> pd.DataFrame:
    """A campaign-shaped frame from a few hand-written rows."""
    base = {"generator": "fixed", "n": 10, "m": 10, "param": 2, "nodes_default": 1, "nodes_csearch": 1,
            "g_components": 1, "g_largest_comp_frac": 1.0, "col_mean": 2.0, "density": 0.2,
            "g_deg_mean": 2.0, "ub_best": 3, "lb_best": 3, "g_degeneracy": 2, "bw_rcm": 2,
            "tw_min_fill": 2, "tw_min_degree": 2, "complete_graph": False, "g_deg_std": 0.0,
            "g_density": 0.5, "n_customers": 10, "optimum": 3}
    out = []
    for i, r in enumerate(rows):
        d = {**base, **r}
        d.setdefault("instance_name", f"i{i}")
        d.setdefault("graph_cert", f"c{i}")
        d["cell"] = f"{d['generator']}:{d['n']}:{d['m']}:{d['param']}"
        out.append(d)
    return prepare(hardness_map.prepare(pd.DataFrame(out)))


def test_nominal_features_by_hand():
    f = nominal_features([4, 10], [1, 20], ["bernoulli", "fixed"], [0.5, 2])
    assert f["p_nom"][0] == 0.5 and f["q_nom"][0] == pytest.approx(0.25)   # 1 − (1 − ¼)^1
    assert f["deg_nom"][0] == pytest.approx(3 * 0.25)
    assert f["p_nom"][1] == pytest.approx(0.2) and f["d_nom"][1] == pytest.approx(2.0)
    assert f["k_nom"][1] == pytest.approx(4.0)                              # 20 products × 0.2


def test_cell_moments_by_hand():
    frame = _frame([{"optimum": 2}, {"optimum": 2}, {"optimum": 4}, {"optimum": 4}])
    cells = cell_stats(frame)
    assert len(cells) == 1
    c = cells.iloc[0]
    assert c["mean"] == 3.0
    assert c["std"] == pytest.approx(np.sqrt(4 / 3))
    assert c["cv"] == pytest.approx(np.sqrt(4 / 3) / 3)
    assert c["mode_share"] == 0.5 and c["min"] == 2 and c["max"] == 4
    assert c["opt_frac"] == pytest.approx(0.3)


def test_kill_verdict_fires_only_at_largest_n():
    wide = [{"n": 40, "optimum": v} for v in (2, 2, 4, 4)]          # cv 0.385 at n = 40
    narrow = [{"n": 40, "optimum": v} for v in (3, 3, 3, 4)]        # cv 0.154
    early = [{"n": 10, "optimum": v} for v in (2, 2, 4, 4)]
    assert kill_verdict(cell_stats(_frame(wide)))["kill_fires"]
    v = kill_verdict(cell_stats(_frame(narrow + early)))
    assert not v["kill_fires"] and v["cells_above_total"] == 1


def test_linearity_recovers_an_exact_line():
    rows = []
    for n in (15, 20, 25, 30, 40):
        for i in range(3):
            rows.append({"n": n, "m": n, "param": 3, "optimum": 3 + 0.2 * n + (i - 1) * 0.0, "col_mean": 3.0})
    lin = linearity(cell_stats(_frame(rows)))
    assert len(lin) == 1
    assert lin.iloc[0]["slope"] == pytest.approx(0.2)
    assert lin.iloc[0]["intercept"] == pytest.approx(3.0)
    assert lin.iloc[0]["r2"] == pytest.approx(1.0)
    assert lin.iloc[0]["regime"] == "super"


def test_regime_of_by_hand():
    assert regime_of({"opt_frac": 1.0, "lcc_frac": 1.0}) == "complete"
    assert regime_of({"opt_frac": 0.3, "lcc_frac": 0.2}) == "sub"
    assert regime_of({"opt_frac": 0.3, "lcc_frac": 0.7}) == "critical"
    assert regime_of({"opt_frac": 0.3, "lcc_frac": 0.99}) == "super"


def test_lambda_and_the_treewidth_bracket_by_hand():
    frame = _frame([
        {"optimum": 5, "g_degeneracy": 2, "bw_rcm": 6, "tw_min_fill": 3, "tw_min_degree": 2},
        {"optimum": 3, "g_degeneracy": 2, "bw_rcm": 2, "tw_min_fill": 2, "tw_min_degree": 2},
    ])
    a, b = frame.iloc[0], frame.iloc[1]
    assert a["lam"] == pytest.approx(0.5)                # (5 − 1 − 2) / (6 − 2)
    assert not a["forced"] and b["forced"] and np.isnan(b["lam"])
    assert a["res_tw"] == 1 and a["res_tw2"] == 2 and a["res_deg"] == 2   # res_tw ≤ pw − tw ≤ res_deg
    assert b["res_tw"] == 0 and b["res_deg"] == 0


def test_structural_fit_recovers_exact_constants():
    rows = []
    for n in (15, 20, 25, 30, 35, 40):
        for d in (2, 3, 5, 8):
            f = nominal_features([n], [n], ["fixed"], [d])
            mean = 2.0 + n * f["deg_nom"][0] / (f["deg_nom"][0] + 10.0)
            for i in range(2):
                rows.append({"n": n, "m": n, "param": d, "optimum": mean, "col_mean": float(d)})
    frame = _frame(rows)
    st = structural_fits(cell_stats(frame), frame)
    assert st["best"] == "a + n·D/(D + c)"
    assert st["constants"][0] == pytest.approx(2.0, abs=1e-3)
    assert st["constants"][1] == pytest.approx(10.0, abs=1e-2)
    assert st["table"].iloc[0]["mae (held-out n)"] < 1e-3
