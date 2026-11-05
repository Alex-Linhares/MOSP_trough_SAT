"""loop0014 item 06: the encodings of `reports/subexp_pathwidth.md` §6 against
brute force on small graphs (the full atlas run is
`python -m learning.subexp_crossover`)."""
import math
import random

from learning import subexp_crossover as sx
from learning.subexp_reductions import atlas
from paper1.complex_check import graph


def _graphs(nmax):
    return atlas(nmax)


def test_indep_cnf_counts_independent_sets_and_has_width_two():
    for g in _graphs(5):
        cl, nv = sx.indep_cnf(g)
        assert sx.count_models(cl, nv) == len(sx.independent_sets(g))
        assert sx.cnf_size(cl, nv)["width"] <= 2
        assert nv == g[0]


def test_indep_atleast_is_count_preserving_and_decides_alpha():
    for g in _graphs(5):
        IS = sx.independent_sets(g)
        alpha = max(sx.popcount(S) for S in IS)
        for t in range(g[0] + 2):
            cl, nv = sx.indep_atleast_cnf(g, t)
            cnt = sx.count_models(cl, nv)
            assert cnt == sum(1 for S in IS if sx.popcount(S) >= t)
            assert (cnt > 0) == (alpha >= t)
            assert sx.cnf_size(cl, nv)["width"] <= 3


def test_threshold_circuit_is_linear():
    r = sx.threshold_aux_ratio(120)
    assert r["max_aux_per_input"] <= 7.0
    assert all(row["width"] <= 3 for row in r["rows"].values())


def test_coloring_cnf_counts_proper_colorings():
    for g in _graphs(5):
        for q in (2, 3):
            cl, nv = sx.coloring_cnf(g, q)
            assert sx.count_models(cl, nv) == sx.proper_colorings(g, q)
            assert nv == q * g[0]
            assert sx.cnf_size(cl, nv)["width"] <= max(q, 2)


def test_domset_cnfs_count_dominating_sets_and_decide_gamma():
    for g in _graphs(5):
        DS = sx.dominating_sets(g)
        gamma = min(sx.popcount(S) for S in DS)
        for ts in (False, True):
            cl, nv = sx.domset_cnf(g, tseitin=ts)
            assert sx.count_models(cl, nv) == len(DS)
        for t in range(g[0] + 1):
            cl, nv = sx.domset_atmost_cnf(g, t)
            assert (sx.count_models(cl, nv) > 0) == (gamma <= t)


def test_maxcut_cnf_decides_and_counts():
    for g in _graphs(5):
        cuts = sx.cut_sizes(g)
        for t in range(len(sx.edges_of(g)) + 2):
            cl, nv = sx.maxcut_cnf(g, t)
            cnt = sx.count_models(cl, nv)
            assert cnt == sum(1 for c in cuts if c >= t)
            assert (cnt > 0) == (max(cuts) >= t)


def test_cut_and_count_parity_and_two_factor_sum():
    for g in _graphs(6):
        n, _ = g
        if n < 3 or len(sx.edges_of(g)) > 12:
            continue
        cl, nv = sx.hamcycle_cutcount_cnf(g)
        cnt = sx.count_models(cl, nv)
        assert cnt == sum(2 ** (cc - 1) for _, cc in sx.two_factors(g))
        assert cnt % 2 == sx.hamiltonian_cycles(g) % 2


def test_cut_and_count_weighted_decision_is_sound():
    rng = random.Random(1)
    for g in _graphs(5):
        n, _ = g
        if n < 3:
            continue
        m = len(sx.edges_of(g))
        dec, _ = sx.hamcycle_weighted_decision(g, [rng.randint(1, 2 * m) for _ in range(m)])
        if dec:
            assert sx.hamiltonian_cycles(g) > 0


def test_examples_by_hand():
    c5 = graph(5, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)])
    assert sx.count_models(*sx.indep_cnf(c5)) == 11          # Lucas number L_5
    assert sx.count_models(*sx.coloring_cnf(c5, 3)) == 30    # (q−1)^n + (−1)^n (q−1)
    assert sx.hamiltonian_cycles(c5) == 1
    assert sx.count_models(*sx.hamcycle_cutcount_cnf(c5)) == 1
    k4 = graph(4, [(a, b) for a in range(4) for b in range(a + 1, 4)])
    assert sx.hamiltonian_cycles(k4) == 3
    assert sx.count_models(*sx.hamcycle_cutcount_cnf(k4)) == 3


def test_crossover_table_arithmetic():
    rows = sx.crossover_table(cs=(2,), exps=(3,))
    r = rows[0]
    assert math.isclose(r["paper_pw_star"], 1000 / math.sqrt(math.log(1000)))
    assert math.isclose(r["verified_pw_star"], sx.rho(1000))
    # the verified ratio exceeds 1 at every n in the table for c = 2 (§6.3)
    assert all(row["verified_ratio"] > 1 for row in sx.crossover_table(cs=(2,)))
    assert all(row["paper_ratio"] < 0.5 for row in sx.crossover_table(cs=(2,)))
