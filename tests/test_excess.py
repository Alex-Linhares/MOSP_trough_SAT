"""loop0010 item 01: the excess `e = (n_ones - m) / n`, the incidence graph's
components and cyclomatic number, the forest flag against the (2, 2)-core, and
the three lines, on hand-checkable matrices."""

import numpy as np
import pandas as pd
import pytest

from learning.excess import (collection_of, crossing_table, excess, giant_threshold_excess, incidence_stats,
                             ratio_label, repaired_giant_threshold_excess, series_table)

# A forest: the path c0 - p0 - c1 - p1 - c2 in the incidence graph.
PATH = np.array([[1, 0],
                 [1, 1],
                 [0, 1]])
# A non-forest: K_{2,2} plus a pendant pattern on c0, one cycle.
CYCLE = np.array([[1, 1, 1],
                  [1, 1, 0]])
# Two components, one of them a 4-cycle: gamma = 1, kappa = 2.
TWO = np.array([[1, 1, 0],
                [1, 1, 0],
                [0, 0, 1]])


def test_path_is_a_forest_by_hand():
    s = incidence_stats(PATH)
    assert (s["n"], s["m"], s["n_ones"]) == (3, 2, 4)
    assert s["e"] == pytest.approx((4 - 2) / 3)          # mean patterns per customer 4/3, minus one
    assert s["kappa"] == 1 and s["gamma"] == 0 and s["forest"]
    assert s["lcc_frac"] == 1.0 and s["lcc_cust_frac"] == 1.0
    assert s["core2_cust_frac"] == 0.0 and s["core2_vertex_frac"] == 0.0


def test_cycle_by_hand():
    s = incidence_stats(CYCLE)
    assert (s["n"], s["m"], s["n_ones"]) == (2, 3, 5)
    assert s["e"] == pytest.approx((5 - 3) / 2)
    assert s["kappa"] == 1
    assert s["gamma"] == 5 - 2 - 3 + 1 == 1 and not s["forest"]
    assert s["gamma_n"] == pytest.approx(0.5)
    # the 2-core is the 4-cycle: both customers, two of the three patterns
    assert s["core2_cust_frac"] == 1.0 and s["core2_prod_frac"] == pytest.approx(2 / 3)
    assert s["core2_vertex_frac"] == pytest.approx(4 / 5)


def test_two_components_by_hand():
    s = incidence_stats(TWO)
    assert s["kappa"] == 2
    assert s["gamma"] == 5 - 3 - 3 + 2 == 1
    assert s["gamma_n"] == pytest.approx(s["e"] - 1 + s["kappa"] / s["n"])   # the identity gamma/n = e - 1 + kappa/n
    assert s["lcc_frac"] == pytest.approx(4 / 6) and s["lcc_cust_frac"] == pytest.approx(2 / 3)
    assert not s["forest"]


def test_excess_is_r_times_c_minus_one():
    rng = np.random.default_rng(7)
    for _ in range(20):
        n, m = int(rng.integers(2, 30)), int(rng.integers(2, 40))
        a = (rng.random((n, m)) < 0.3).astype(int)
        a[np.arange(n), rng.integers(0, m, n)] = 1
        a[rng.integers(0, n, m), np.arange(m)] = 1
        s = incidence_stats(a)
        assert s["e"] == pytest.approx(excess(n, m, a.sum()))
        assert s["e"] == pytest.approx(s["r"] * (s["c"] - 1))
        assert s["gamma_n"] == pytest.approx(s["e"] - 1 + s["kappa"] / n)
        assert s["forest"] == (s["core2_vertex_frac"] == 0.0)


def test_giant_threshold_in_excess_coordinates():
    # fixed sizes: r c (c - 1) = 1 with e = r (c - 1)
    for r in (0.125, 0.5, 1.0, 2.0, 8.0):
        e = giant_threshold_excess(r)
        c = 1 + e / r
        assert r * c * (c - 1) == pytest.approx(1.0)
    assert giant_threshold_excess(1.0) == pytest.approx((np.sqrt(5) - 1) / 2)
    # Poisson sizes: r c^2 = 1
    assert giant_threshold_excess(0.25, "bernoulli") == pytest.approx(0.5 - 0.25)
    # the padded generators' threshold is finite and sits in [0, e_g(r)] at r = 1/2 (0.475 against 0.5)
    rep = repaired_giant_threshold_excess("fixed", 0.5)
    assert np.isfinite(rep) and 0.0 <= rep <= giant_threshold_excess(0.5)


def test_ratio_labels_absorb_the_frames_rounding():
    assert ratio_label(0.12) == "n/8" and ratio_label(0.24) == "n/4" and ratio_label(0.493) == "n/2"
    assert ratio_label(1.0) == "n" and ratio_label(8.0) == "8n"


def test_collections_and_classes():
    assert collection_of("benchmarks/instances/MOSP_Instances/Chu_Stuckey/Random-125-125-2-2.txt",
                         "Random-125-125-2-2_0") == ("Chu & Stuckey", "Random-125-125-2")
    assert collection_of("benchmarks/instances/ChallengeInstances2005/Harvey/wbo_10_10.txt", "x") == ("Harvey", "wbo_10_10")
    assert collection_of("benchmarks/instances/MOSP_Instances/SCOOP/scoop-B_REVAL_145.txt", "scoop-B_REVAL_145_0") == ("SCOOP", "SCOOP")
    assert collection_of("benchmarks/instances/MOSP_Instances/Faggioli_Bentivoglio/x.txt", "y")[0] == "Faggioli-Bentivoglio"


def _synthetic_frame() -> pd.DataFrame:
    """Three cells of one series whose largest component rises through one half."""
    rows = []
    for param, e, lcc in ((2, 0.4, 0.2), (3, 0.8, 0.6), (4, 1.2, 0.9)):
        for i in range(3):
            rows.append({"source": "ensemble", "generator": "fixed", "r_label": "n", "r": 1.0, "param": param,
                         "n": 50, "m": 50, "e": e, "gamma_n": e - 1 + 0.02, "forest": False,
                         "core2_cust_frac": 0.5, "lcc_frac": lcc, "lcc_cust_frac": lcc, "certified": True})
    return pd.DataFrame(rows)


def test_crossing_is_interpolated_between_the_straddling_cells():
    f = _synthetic_frame()
    cells = series_table(f)
    assert len(cells) == 3 and list(cells["param"]) == [2, 3, 4]
    cross = crossing_table(f, min_n=50)
    assert len(cross) == 1
    # between (0.4, 0.2) and (0.8, 0.6): one half at e = 0.7
    assert cross["crossing"].iloc[0] == pytest.approx(0.7)
    assert cross["delta"].iloc[0] == pytest.approx(0.7 - giant_threshold_excess(1.0))
    assert cross["verdict"].iloc[0] == "within tolerance"
    f.loc[:, "lcc_frac"] = 0.9
    assert crossing_table(f, min_n=50)["verdict"].iloc[0].startswith("not observable")
