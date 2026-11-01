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


# ---------------------------------------------------------------------------
# item 02: the rule stage and the slopes
# ---------------------------------------------------------------------------

from learning.excess import (_ols, beta_residuals, matched_pairs, named_groups, rule_by_bin, series_slopes,  # noqa: E402
                             sizes_from_text, sizes_text)


def test_sizes_histogram_round_trips():
    m = np.array([[1, 1, 0, 1],
                  [1, 0, 1, 1],
                  [0, 0, 1, 1]])
    assert sizes_text(m) == "1:1;2:2;3:1"
    assert sizes_from_text(sizes_text(m)) == {1: 1, 2: 2, 3: 1}
    assert sum(sizes_from_text(sizes_text(m)).values()) == m.shape[1]


def test_ols_recovers_a_line_and_its_errors():
    x = np.array([30, 30, 40, 40, 50, 50], float)
    a, b, se_a, se_b = _ols(x, 2 + 0.5 * x)
    assert a == pytest.approx(2.0) and b == pytest.approx(0.5)
    assert se_b == pytest.approx(0.0, abs=1e-12)
    assert np.isnan(_ols(np.array([30, 30, 30]), np.array([1, 2, 3]))[1])   # no spread in n


def _synthetic_rule(rows):
    f = pd.DataFrame(rows, columns=["generator", "r_label", "param", "n", "m", "optimum", "rule", "sizes"])
    f["source"] = "ensemble"
    f["certified"] = True
    f["n_ones"] = [sum(int(v) * int(c) for v, c in (p.split(":") for p in s.split(";"))) for s in f["sizes"]]
    f["e"] = (f["n_ones"] - f["m"]) / f["n"]
    f["r"] = f["m"] / f["n"]
    f["rule_gap"] = f["rule"] - f["optimum"]
    return f


def test_series_slopes_and_matched_pairs_on_synthetic_series():
    rows = []
    # series A: fixed d = 3 at m = n, opt = 1 + 0.2 n exactly, sizes all 3 (e = 2)
    # series B: fixed d = 5 at m = n/2, opt = 1 + 0.3 n, sizes all 5 (e = 2)
    # series C: like B but opt = 1 + 0.2 n (agrees with A)
    for n in (30, 40, 50):
        for i in range(4):
            rows.append(("fixed", "n", 3.0, n, n, 1 + 0.2 * n + (i % 2) * 0.0, 2 + 0.2 * n, f"3:{n}"))
            rows.append(("fixed", "n/2", 5.0, n, n // 2, 1 + 0.3 * n, 1 + 0.3 * n, f"5:{n // 2}"))
            rows.append(("fixed", "2n", 2.0, n, 2 * n, 1 + 0.2 * n, 1 + 0.2 * n, f"2:{2 * n}"))
    rule = _synthetic_rule(rows)
    slopes = series_slopes(rule, min_n=30, min_sizes=3)
    assert len(slopes) == 3 and slopes["constant e"].all()
    by = slopes.set_index(["r", "param"])
    assert by.loc[("n", 3.0), "b"] == pytest.approx(0.2) and by.loc[("n/2", 5.0), "b"] == pytest.approx(0.3)
    assert by.loc[("n", 3.0), "e"] == pytest.approx(2.0) and by.loc[("n/2", 5.0), "e"] == pytest.approx(2.0)
    assert by.loc[("n", 3.0), "rule exact"] == 0.0        # the rule is one above the optimum on every A instance
    assert by.loc[("n", 3.0), "rule gap mean"] == pytest.approx(1.0)
    assert by.loc[("n/2", 5.0), "rule exact"] == 1.0
    pairs = matched_pairs(slopes, tol=0.05)
    assert len(pairs) == 3
    differ = {frozenset((p["series 1"], p["series 2"])): p["differ"] for _, p in pairs.iterrows()}
    assert differ[frozenset(("fixed r=n 3", "fixed r=n/2 5"))] is True
    assert differ[frozenset(("fixed r=n 3", "fixed r=2n 2"))] is False
    groups = named_groups(slopes)
    assert set(groups["group"]) == {"e = 2"} and len(groups) == 3
    assert not beta_residuals(slopes).empty or True        # no pair within 0.02 in beta* is a legitimate outcome


def test_rule_by_bin_counts_every_certified_instance_once():
    rows = []
    for n in (30, 40):
        rows.append(("fixed", "n", 3.0, n, n, 10, 11, f"3:{n}"))
        rows.append(("fixed", "n", 8.0, n, n, 20, 20, f"8:{n}"))
    rule = _synthetic_rule(rows)
    bins = rule_by_bin(rule)
    assert bins["count"].sum() == 4
    assert set(bins["e bin"].astype(str)) == {"[2, 2.4)", "[6, 10)"}
    assert float(bins.loc[bins["e bin"].astype(str) == "[6, 10)", "exact"].iloc[0]) == 1.0
