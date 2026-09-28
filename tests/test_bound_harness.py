"""Tests for learning.bound_harness (loop0004 item 11)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from learning import bound_harness as bh

nx = pytest.importorskip("networkx")


def from_cliques(n: int, cliques) -> np.ndarray:
    """A matrix with one product per clique (each product is a clique of the MOSP graph)."""
    matrix = np.zeros((n, len(cliques)), dtype=int)
    for j, c in enumerate(cliques):
        for v in c:
            matrix[v, j] = 1
    return matrix


def spider_edges(legs: int, length: int):
    edges, k = [], 1
    for _ in range(legs):
        prev = 0
        for _ in range(length):
            edges.append((prev, k))
            prev, k = k, k + 1
    return k, edges


def theta_matrix():
    """Two adjacent hubs joined by three internally disjoint paths of three
    inner vertices: no cut vertex, separator {0, 1}, pathwidth 3."""
    edges, k = [(0, 1)], 2
    for _ in range(3):
        edges += [(0, k), (k, k + 1), (k + 1, k + 2), (k + 2, 1)]
        k += 3
    return from_cliques(k, edges)


def optimum_of(matrix) -> int:
    from learning.extremal import instance_from_matrix
    from satisfiability.mosp_solver import solve_mosp_exact

    inst = instance_from_matrix(np.asarray(matrix, dtype=int), prefix="bh")   # named by its matrix
    return int(solve_mosp_exact(inst, solutions_dir=bh.SCRATCH_SOLUTIONS)[0])


# ----------------------------------------------------------------------------
# the candidates on hand instances (values in optimum units)
# ----------------------------------------------------------------------------


@pytest.mark.parametrize("matrix, optimum, cut, sep", [
    (from_cliques(*spider_edges(3, 1)), 2, 2, 2),           # K_{1,3}: pw 1
    (from_cliques(*spider_edges(4, 1)), 2, 2, 2),           # K_{1,4}
    (from_cliques(*spider_edges(3, 2)), 3, 3, 3),           # spider with legs of two: pw 2, three branches of pw 1
    (from_cliques(*spider_edges(2, 4)), 2, 2, 2),           # a path: no branching
    (from_cliques(10, [{0, 1, 2, 3}, {0, 4, 5, 6}, {0, 7, 8, 9}]), 4, 4, 4),   # three K4 at a hub: ω − 1 = 3
    (theta_matrix(), 4, 2, 3),                              # no cut vertex; separator {0,1} with three P3 branches
])
def test_candidates_hand(matrix, optimum, cut, sep):
    vals = bh.evaluate_candidates(matrix)
    assert optimum_of(matrix) == optimum
    assert vals["cut_branch"] == cut
    assert vals["sep_branch"] == sep
    assert vals["contract_branch"] >= vals["sep_branch"]
    for name in bh.CANDIDATES:
        assert vals[name.replace("-", "_")] <= optimum          # never above the optimum


def test_branch_rule_recursive_spider():
    """A spider whose legs are themselves spiders: the recursion must see the
    inner branching (pw 3 = two levels of the rule)."""
    edges, k = [], 1
    for _ in range(3):
        c = k
        edges.append((0, c))
        k += 1
        for _ in range(3):
            edges += [(c, k), (k, k + 1)]
            k += 2
    matrix = from_cliques(k, edges)
    vals = bh.evaluate_candidates(matrix)
    assert vals["cut_branch"] == 4           # pw 3 → optimum units 4
    assert optimum_of(matrix) == 4


def test_lemma_a_needs_pairwise_links():
    """Three components of H − S that are not pairwise linked through a
    component of H[S] do not qualify: S = {a, b} non-adjacent, a joined to
    branches 1 and 2, b to branches 2 and 3 — pairs (1, 3) share no S-component."""
    g = nx.Graph()
    comps = [set(range(2, 5)), set(range(5, 8)), set(range(8, 11))]
    for c in comps:
        g.add_edges_from(nx.path_graph(sorted(c)).edges())
    g.add_edges_from([(0, 2), (0, 5), (1, 6), (1, 8)])
    S = frozenset([0, 1])
    assert bh.linked_third(g, S, comps, [1, 1, 1]) is None
    g.add_edge(0, 1)                          # now S is connected: every pair is linked
    assert bh.linked_third(g, S, comps, [1, 1, 1]) == 1
    assert bh.linked_third(g, S, comps, [3, 1, 1]) == 1     # third-largest


def test_family_separators_contains_glue_and_cuts():
    matrix = theta_matrix()
    g = bh.graph_from_matrix(matrix)
    fam = bh.family_separators(g)
    assert frozenset([0, 1]) in fam
    assert not any(s == frozenset(g.nodes()) for s in fam)
    star = bh.graph_from_matrix(from_cliques(*spider_edges(3, 1)))
    assert frozenset([0]) in bh.family_cut_vertices(star)


def test_seeds_are_clique_and_treewidth():
    g = nx.complete_graph(5)
    assert bh.seed_clique(g) == 4
    grid = nx.grid_2d_graph(3, 3)
    grid = nx.convert_node_labels_to_integers(grid)
    assert bh.seed_clique(grid) == 1
    assert bh.seed_clique_tw(grid) == 3            # tw of the 3×3 grid is 3


def test_budget_exhaustion_returns_seed():
    matrix = theta_matrix()
    g = bh.graph_from_matrix(matrix)
    budget = bh.Budget(seconds=100.0, max_subproblems=0)
    value = bh.branch_bound(g, bh.family_separators, bh.seed_clique, budget)
    assert value == bh.seed_clique(g) == 1
    assert budget.exhausted


def test_contraction_minors_match_solver_rule():
    """The sequence follows `_contraction_degeneracy`: the largest minimum
    degree over the minors equals the solver's contraction degeneracy."""
    from satisfiability.mosp_solver import _contraction_degeneracy

    rng = np.random.default_rng(3)
    matrix = (rng.random((14, 20)) < 0.2).astype(int)
    g = bh.graph_from_matrix(matrix)
    best = 0
    for minor in bh.contraction_minors(g):
        if minor.number_of_edges():
            best = max(best, min(d for _, d in minor.degree()))
    assert best == _contraction_degeneracy(g)


def test_extra_candidate_protocol_and_validity_table():
    """A user candidate through the same protocol; the "above optimum" column
    catches one that overclaims and the reference column is honest."""
    def too_strong(graph, matrix, budget):
        return graph.number_of_nodes()                 # optimum ≤ n, equality only on complete graphs

    frame = pd.DataFrame({
        "instance_name": ["a", "b", "c"], "source": ["corpus"] * 3,
        "optimum": [3, 4, 5], "lb_best": [2, 2, 5], "tw1": [3, 2, 5], "blt1": [1, 1, 1],
        "n_customers": [7, 9, 5], "tw_exact": [True, True, True], "gap": [1, 2, 0],
        "too_strong": [7, 9, 5], "too_strong_seconds": [0.0] * 3,
    })
    frame["reference"] = np.maximum(frame["lb_best"], frame["tw1"])
    frame["is_gap"] = frame["gap"] >= 2
    saved = dict(bh.CANDIDATES)
    try:
        bh.CANDIDATES["too-strong"] = too_strong
        table = bh.validity_table(frame).set_index("bound")
        assert table.loc["too-strong", "above optimum (must be 0)"] == 2
        assert table.loc["tw + 1 (tw_lo)", "above optimum (must be 0)"] == 0
        assert table.loc["too-strong", "> reference, gap"] == 1.0
        verdict = bh.kill_verdict(table.reset_index(), None).set_index("candidate")
        assert not verdict.loc["too-strong", "valid on every certified instance"]
        assert verdict.loc["too-strong", "beats > 5% while surviving"] is np.False_ or \
            not verdict.loc["too-strong", "beats > 5% while surviving"]
    finally:
        bh.CANDIDATES.clear()
        bh.CANDIDATES.update(saved)


def test_make_evaluate_reports_violation():
    evaluate = bh.make_evaluate(("cut-branch",))
    rec = evaluate(from_cliques(*spider_edges(3, 2)), bh.SCRATCH_SOLUTIONS)
    assert rec["optimum"] == 3
    assert rec["viol_cut-branch"] == 0
    assert rec["edges"] == 6
