"""loop0010 item 06: the statements of `reports/excess_phase_diagram.md` §6 against
brute force on tiny graphs (the exact DP of `fixed_parameter_algorithm.pathwidth`,
which shares no code with the C program the item's check used)."""
import math
from pathlib import Path

import networkx as nx
import numpy as np
import pytest

from fixed_parameter_algorithm.pathwidth import compute_pathwidth
from learning.block_trees import clique_tree, incidence_graph, is_incidence_forest, largest_pattern, mosp_graph, tree_bound
from learning.forest_theorems import (
    branch_lower_bound_ct,
    clique_with_pendants,
    f1_bound,
    f1_log_bound,
    f2_value,
    log3_form,
    pendant_lower_bound,
    random_instance,
)

RECORD = Path(__file__).resolve().parents[1] / "reports" / "scratch" / "forest_regime"


def exact_pw(g: nx.Graph) -> int:
    if g.number_of_nodes() == 0:
        return 0
    return compute_pathwidth(g)[0]


def test_f2_value_by_hand():
    assert f2_value(4, 4, 0) == 3  # the clique alone
    assert f2_value(4, 4, 1) == 3  # one pendant: still the clique
    assert f2_value(3, 3, 3) == 3 and f2_value(4, 4, 4) == 4 and f2_value(5, 5, 5) == 6  # CT(s, 1, b) = ceil(3s/2) - 2
    for s in range(2, 9):
        assert f2_value(s, s, s) == math.ceil(3 * s / 2) - 2
    assert f2_value(3, 6, 2) == 5  # big pendants: t + ceil(q/2) - 2 = 6 + 1 - 2
    assert f2_value(6, 2, 6) == 5  # tiny pendants: the clique wins
    with pytest.raises(ValueError):
        f2_value(3, 3, 4)


def test_clique_with_pendants_structure():
    for s, t, q, b in [(3, 3, 3, 1), (4, 2, 2, 2), (5, 4, 0, 1), (2, 5, 2, 3)]:
        P = clique_with_pendants(s, t, q, b)
        n = s + q * b * (t - 1)
        assert len(P) == 1 + q * b
        assert 1 + max((v for p in P for v in p), default=0) == n or q == 0
        assert is_incidence_forest(P, n)
        assert largest_pattern(P) == (max(s, t) if q else s)
    # CT(s, 1, b) is the case t = s, q = s
    for s, b in [(3, 1), (3, 2), (4, 1)]:
        a, _ = clique_tree(s, 1, b)
        assert nx.is_isomorphic(mosp_graph(a), mosp_graph(clique_with_pendants(s, s, s, b)))


def test_f2_is_exact_on_tiny_graphs():
    """F2 against the exact DP: every (s, t, q, b) with at most 12 vertices."""
    checked = 0
    for s in range(2, 6):
        for t in range(2, 6):
            for q in range(0, s + 1):
                for b in (1, 2):
                    n = s + q * b * (t - 1)
                    if n > 12:
                        continue
                    P = clique_with_pendants(s, t, q, b)
                    assert exact_pw(mosp_graph(P, n)) == f2_value(s, t, q), (s, t, q, b)
                    checked += 1
    assert checked >= 40


def test_pendant_lower_bound_by_hand():
    assert pendant_lower_bound([[0, 1, 2, 3]]) == 3
    P, _ = clique_tree(4, 1, 1)
    assert pendant_lower_bound(P) == 4  # ceil(3 * 4 / 2) - 2
    P, _ = clique_tree(5, 1, 2)
    assert pendant_lower_bound(P) == 6
    # a pattern meeting R in two customers is not a pendant for Lemma P
    assert pendant_lower_bound([[0, 1, 2], [0, 1, 3, 4], [2, 5, 6]]) == 3


def test_lemma_p_never_exceeds_the_pathwidth():
    """Lemma P on random small instances that are mostly not forests, against the exact DP."""
    rng = np.random.default_rng(606)
    forests = 0
    for i in range(80):
        n, m = int(rng.integers(4, 9)), int(rng.integers(3, 8))
        kind, p = (("bernoulli", 0.4), ("fixed", 2), ("fixed", 3))[i % 3]
        P = random_instance(rng, n, m, kind, p)
        forests += is_incidence_forest(P, n)
        pw = exact_pw(mosp_graph(P, n))
        assert pendant_lower_bound(P) <= pw
        assert largest_pattern(P) - 1 <= pw
    assert forests < 80


def test_f1_holds_on_random_instances_forest_or_not():
    """F1 needs no forest hypothesis: pw(G_M) <= omega (pw(B) + 1) - 1 on every instance;
    F1' (the tb form) on the forests among them."""
    rng = np.random.default_rng(1606)
    forests = non_forests = 0
    for i in range(60):
        n, m = int(rng.integers(3, 8)), int(rng.integers(2, 7))
        kind, p = (("bernoulli", 0.35), ("fixed", 2), ("fixed", 3))[i % 3]
        P = random_instance(rng, n, m, kind, p)
        omega = largest_pattern(P)
        pw_g = exact_pw(mosp_graph(P, n))
        pw_b = exact_pw(incidence_graph(P, n))
        assert pw_g <= f1_bound(omega, pw_b)
        if is_incidence_forest(P, n):
            forests += 1
            assert pw_b <= tree_bound(n + m)
            assert pw_g <= f1_log_bound(omega, n + m)
        else:
            non_forests += 1
    assert forests >= 5 and non_forests >= 5


def test_tb_equals_the_log3_form():
    for N in range(1, 3000):
        assert tree_bound(N) == log3_form(N)
    assert [log3_form(N) for N in (1, 6, 7, 21, 22, 66, 67)] == [0, 1, 2, 2, 3, 3, 4]


def test_branch_lower_bound_ct_by_hand_and_against_the_record():
    assert branch_lower_bound_ct(3, 0) == 2
    assert branch_lower_bound_ct(3, 1) == 3 and branch_lower_bound_ct(3, 2) == 3 and branch_lower_bound_ct(3, 3) == 4
    assert branch_lower_bound_ct(5, 2) == 6 and branch_lower_bound_ct(8, 1) == 10
    # the b = 2 clique trees are block graphs the exact DP can do at n <= 15: CT(3, 1, 2), CT(2, h, 2)
    P, _ = clique_tree(3, 1, 2)
    assert branch_lower_bound_ct(3, 1) <= exact_pw(mosp_graph(P))
    path = RECORD / "ct_values.csv"
    if path.exists():
        import pandas as pd
        ct = pd.read_csv(path)
        for r in ct[ct.b == 2].itertuples():
            assert branch_lower_bound_ct(int(r.s), int(r.h)) <= int(r.pw), (r.s, r.h)
