"""§36: the cover excess against the thresholds of the random bipartite
incidence graph -- the configuration-model cores, the peeler, the
dominance reduction and the scoring tables, on hand-checkable cases."""

import numpy as np
import pandas as pd
import pytest

from learning.cover_excess import (RATIOS, bipartite_components, connectivity_col_mean, core_fixed_point,
                                   core_quantities, core_record, core_threshold_col_mean, degree_pmfs,
                                   dominance_record, invert_analytic, measure_instance, peel, size_biased,
                                   threshold_summary, threshold_table)
from learning.ridge_theory import giant_threshold_col_mean
from mosp.instance import MOSPInstance


def test_degree_pmfs_have_the_right_means_and_no_empty_rows():
    p_c, p_p = degree_pmfs("fixed", 1.0, 3.0, repair=False)
    k = np.arange(len(p_c))
    assert (k * p_c).sum() == pytest.approx(3.0, rel=1e-6)          # Poisson(r c)
    assert p_p[3] == pytest.approx(1.0)                              # every product has exactly d customers
    p_c, p_p = degree_pmfs("fixed", 1.0, 3.0, repair=True)
    assert p_c[0] == 0.0                                             # the empty-row repair
    assert (np.arange(len(p_p)) * p_p).sum() == pytest.approx(3.0)  # and the products receive them: the realised mean stays c
    assert p_p[2] > 0.0                                              # so the design d sits below the realised col_mean
    p_c, p_p = degree_pmfs("bernoulli", 0.5, 4.0, repair=False)
    assert (np.arange(len(p_p)) * p_p).sum() == pytest.approx(4.0 / (1 - np.exp(-4.0)), rel=1e-3)


def test_size_biased_of_a_point_mass_is_the_point_mass_minus_one():
    pmf = np.zeros(6)
    pmf[4] = 1.0
    q = size_biased(pmf)
    assert q[3] == pytest.approx(1.0)


def test_two_core_appears_at_the_giant_threshold():
    # continuous transition: the 2-core is empty below the branching-factor-1 point and present above it
    for gen, r in (("fixed", 1.0), ("bernoulli", 0.5), ("fixed", 0.25)):
        c_star = giant_threshold_col_mean(r, gen)
        below = core_quantities(gen, r, 0.8 * c_star, 2, 2, repair=False)["cust_frac"]
        above = core_quantities(gen, r, 1.3 * c_star, 2, 2, repair=False)["cust_frac"]
        assert below == 0.0
        assert above > 0.01


def test_deeper_cores_appear_above_the_two_core_and_in_order():
    for gen, r in (("fixed", 1.0), ("bernoulli", 2.0), ("fixed", 0.125)):
        c22 = giant_threshold_col_mean(r, gen)
        c32 = core_threshold_col_mean(gen, r, 3, 2)
        c33 = core_threshold_col_mean(gen, r, 3, 3)
        assert c22 < c32 < c33


def test_fixed_point_on_a_regular_bipartite_graph_keeps_everything():
    # every customer has exactly 3 products and every product exactly 3 customers: nothing peels
    p_c = np.zeros(5)
    p_c[3] = 1.0
    a, b = core_fixed_point(p_c, p_c, 2, 2)
    assert a == pytest.approx(1.0) and b == pytest.approx(1.0)
    a, b = core_fixed_point(p_c, p_c, 3, 3)
    assert a == pytest.approx(1.0) and b == pytest.approx(1.0)
    a, b = core_fixed_point(p_c, p_c, 4, 2)                          # no customer has 4 products
    assert a == 0.0 and b == 0.0


def test_peel_and_cyclomatic_number_by_hand():
    # a 4-cycle of customers and products (2 x 2 all ones): whole graph is the 2-core, one cycle
    rec = core_record(np.array([[1, 1], [1, 1]]), 2, 2, "c")
    assert rec["c_cust_frac"] == 1.0 and rec["c_cyc_n"] == pytest.approx(0.5)  # one cycle over two customers
    assert rec["c_excess"] == pytest.approx(1.0)                                 # (4 - 2) / 2
    # a chain: the end customer with one product peels, then its product has one customer and peels too
    cust, prod = peel(np.array([[1, 1, 0], [0, 1, 1], [0, 0, 1]]), 2, 2)
    assert cust.sum() == 0 and prod.sum() == 0
    # a customer needing three products, each shared with a distinct 2-product customer: (3,2)-core empty, 2-core = the theta
    m = np.array([[1, 1, 1, 0, 0, 0],
                  [1, 0, 0, 1, 0, 0],
                  [0, 1, 0, 1, 0, 0],
                  [0, 0, 1, 1, 0, 0]])
    cust, prod = peel(m, 2, 2)
    assert cust.sum() == 4 and prod.sum() == 4
    rec = core_record(m, 2, 2, "c")
    assert rec["c_cyc_n"] == pytest.approx((9 - 4 - 4 + 1) / 4)          # nine ones, eight vertices, connected
    cust32, _ = peel(m, 3, 2)
    assert cust32.sum() == 0


def test_bipartite_components_counts_isolated_pieces():
    m = np.array([[1, 0, 0], [0, 1, 0], [0, 1, 1]])
    assert bipartite_components(m, np.ones(3, bool), np.ones(3, bool)) == 2
    assert bipartite_components(m, np.zeros(3, bool), np.zeros(3, bool)) == 0


def test_dominance_record_drops_dominated_products_and_customers():
    # product 2 sits inside product 0's customers; customer 2 has N[2] = {0, 1, 2} inside N[0] = {0, 1, 2}? no: keep
    m = np.array([[1, 1, 1],
                  [1, 1, 0],
                  [0, 0, 1]])
    rec = dominance_record(m)
    # products: {0,1}, {0,1}, {0,2}: product 1 duplicates product 0 (tie -> lowest index kept), two survive;
    # customers then: N[0] = {0,1,2}, N[1] = {0,1} strictly inside -> dropped, N[2] = {0,2} inside -> dropped;
    # with customer 0 alone both surviving products are {0}, a tie, so one product remains
    assert rec["dom_cust_frac"] == pytest.approx(1 / 3)
    assert rec["dom_prod_frac"] == pytest.approx(1 / 3)
    assert rec["dom_excess"] == pytest.approx(0.0)


def test_measure_instance_on_the_four_cycle_of_cliques():
    inst = MOSPInstance.from_matrix([[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1], [1, 0, 0, 1]], name="c4")
    row = measure_instance(inst)
    assert row["bip_cyc_exact"] == pytest.approx((8 - 4 - 4 + 1) / 4)
    assert row["core2_cust_frac"] == 1.0 and row["core32_cust_frac"] == 0.0
    assert row["dom_excess"] == pytest.approx(1.0)


def test_invert_analytic_and_connectivity():
    assert invert_analytic(lambda c: c * c, 9.0) == pytest.approx(3.0, rel=1e-6)
    assert np.isnan(invert_analytic(lambda c: 1.0, 2.0))
    assert connectivity_col_mean(1.0, 75) == pytest.approx(np.log(75))
    assert connectivity_col_mean(0.5, 75) == pytest.approx(2 * np.log(75))


def test_threshold_table_scores_a_planted_ridge_at_excess_two():
    # peaks exactly at excess 2 for the fixed generator: the excess-2 row has zero error and is within every CI
    rows = []
    for lab, r in RATIOS.items():
        c = 1 + 2 / r
        rows.append({"generator": "fixed", "ratio_label": lab, "n": 60, "r_exact": r, "peak_col_mean": c,
                     "ci_lo": c * 0.95, "ci_hi": c * 1.05, "interior": True})
    table = threshold_table(pd.DataFrame(rows))
    ex2 = table[table["threshold"] == "excess 2 (one cycle per customer)"]
    assert len(ex2) == 5 and np.allclose(ex2["log10_error"], 0.0) and ex2["within_ci"].all()
    giant = table[table["threshold"] == "giant (branching 1)"]
    assert (giant["log10_error"] < 0).all()                          # the giant threshold is always below the ridge
    summary = threshold_summary(table)
    assert summary.iloc[0]["threshold"] == "excess 2 (one cycle per customer)"
    assert summary.iloc[0]["mean_abs_log10_error"] == pytest.approx(0.0)


def test_reachable_states_against_brute_force_on_the_four_cycle():
    import itertools

    from learning.cover_excess import feasible_states, reachable_states

    inst = MOSPInstance.from_matrix([[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1], [1, 0, 0, 1]], name="c4")
    a = np.asarray(inst.matrix)
    n = a.shape[0]
    adj = (a @ a.T) > 0

    def closed(S):
        out = set(S)
        for i in S:
            out |= set(np.where(adj[i])[0])
        return out

    subsets = [frozenset(S) for r in range(n + 1) for S in itertools.combinations(range(n), r)]
    for k in (1, 2, 3):
        boundary = sum(len(closed(S)) - len(S) <= k for S in subsets)
        fits = {S: (len(closed(S)) - len(S) + 1 <= k) if S else True for S in subsets}
        reach = {frozenset(): True}
        for S in sorted(subsets, key=len):
            if S:
                reach[S] = fits[S] and any(reach[S - {c}] for c in S)
        assert feasible_states(inst, k) == boundary
        assert reachable_states(inst, k) == (sum(fits.values()), sum(reach.values()))
    # the optimum of the 4-cycle of cliques is 3: at k = 2 only the empty set is reachable (the refutation),
    # at k = 3 every set is
    assert reachable_states(inst, 2)[1] == 1
    assert reachable_states(inst, 3)[1] == 16
