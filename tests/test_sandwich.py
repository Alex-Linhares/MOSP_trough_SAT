"""Tests for `learning.sandwich`: the Python transcription of the Lean definitions
in `lean/MOSPFormalization/Sandwich.lean`, and the axiom check on the Lean side."""
from __future__ import annotations

import subprocess

import networkx as nx
import pytest

from learning import sandwich as sw


def _path(n):
    return nx.path_graph(n)


def _spider():
    """K_{1,3} with every edge subdivided: treewidth 1, pathwidth 2."""
    g = nx.Graph()
    for k in range(3):
        g.add_edge(0, 1 + k)
        g.add_edge(1 + k, 4 + k)
    return g


def test_definitions_on_hand_checked_graphs():
    # P3: the values the Lean file decides in the kernel.
    p3 = _path(3)
    assert sw.degeneracy_subsets(p3) == 1
    assert sw.min_degree_in(p3, frozenset(p3.nodes())) == 1
    assert sw.max_later_degree(p3, [0, 1, 2]) == 1
    assert sw.vertex_sep_at(p3, [0, 1, 2], 0) == 1
    assert sw.bandwidth_of_layout(p3, [0, 1, 2]) == 1
    # K3 and the empty graph on three vertices.
    k3 = nx.complete_graph(3)
    assert sw.degeneracy_subsets(k3) == 2
    assert sw.bandwidth_of_layout(k3, [0, 1, 2]) == 2
    empty = nx.empty_graph(3)
    assert sw.degeneracy_subsets(empty) == 0
    assert sw.bandwidth_of_layout(empty, [0, 1, 2]) == 0
    # The star: degeneracy 1, bandwidth 2 (centre in the middle), pathwidth 1.
    star = nx.star_graph(3)
    assert sw.degeneracy_subsets(star) == 1
    assert sw.bandwidth(star) == 2
    assert sw.vertex_separation(star) == 1
    assert sw.bandwidth_of_layout(star, [0, 1, 2, 3]) == 3


def test_min_degree_in_empty_set_is_zero():
    assert sw.min_degree_in(_path(3), frozenset()) == 0


def test_spider_is_the_classic_treewidth_pathwidth_gap():
    s = _spider()
    row = sw.sandwich(s)
    assert row["degeneracy"] == 1
    assert row["vertex_separation"] == 2 == row["pathwidth_solver"]
    assert row["bandwidth"] == 2
    assert row["degeneracy"] <= row["vertex_separation"] <= row["bandwidth"]


def test_exhaustive_small_graphs_agree_with_references():
    frame = sw.brute_force(4)
    assert len(frame) == 1 + 2 + 8 + 64
    assert (frame.degeneracy == frame.core_number).all()
    assert (frame.degeneracy == frame.ordering_degeneracy).all()
    assert (frame.vertex_separation == frame.pathwidth_solver).all()
    assert (frame.degeneracy <= frame.vertex_separation).all()
    assert (frame.vertex_separation <= frame.bandwidth).all()
    summary = sw.brute_summary(frame)
    assert list(summary.n) == [1, 2, 3, 4]
    # C4 and the paw-free graphs: on 4 vertices exactly four graphs have pw < bandwidth.
    assert int(summary.loc[summary.n == 4, "pw = bandwidth"].iloc[0]) == 60


def test_axioms_verdict_logic():
    import pandas as pd
    good = pd.DataFrame([
        {"theorem": "a", "role": "proved", "found": True, "axioms": "propext", "uses_sorry": False},
        {"theorem": "b", "role": "stated (sorry)", "found": True, "axioms": "sorryAx", "uses_sorry": True},
    ])
    ok, problems = sw.axioms_verdict(good)
    assert ok and not problems
    bad = good.copy()
    bad.loc[0, "uses_sorry"] = True
    bad.loc[1, "uses_sorry"] = False
    ok, problems = sw.axioms_verdict(bad)
    assert not ok and len(problems) == 2
    missing = good.copy()
    missing.loc[0, "found"] = False
    ok, problems = sw.axioms_verdict(missing)
    assert not ok and "not found" in problems[0]


def test_corpus_sandwich_holds_everywhere():
    if not sw.INSTANCES.exists():
        pytest.skip("instances.csv not present")
    table = sw.corpus_check()
    total = table[table.band == "all"].iloc[0]
    assert total["degeneracy+1 ≤ optimum"] == total.instances
    assert total["optimum ≤ bw_rcm+1"] == total.instances


@pytest.mark.skipif(not sw.lake_available(), reason="lake not on PATH")
def test_lean_theorems_are_sorry_free():
    """The two halves of the sandwich, the chain to pathwidth and the equality of
    the two degeneracy forms compile with the standard axioms only; the statements
    left open still carry `sorryAx`."""
    try:
        frame = sw.print_axioms()
    except subprocess.TimeoutExpired:  # pragma: no cover
        pytest.skip("lean took too long")
    if frame.attrs.get("returncode", 1) != 0 and not frame.found.any():
        pytest.skip("the Lean library is not built; run `lake build` in lean/")
    ok, problems = sw.axioms_verdict(frame)
    assert ok, problems


# ---------------------------------------------------------------------------
# loop0004 item 12: the tree-decomposition section of Sandwich.lean
# ---------------------------------------------------------------------------

def _three_branches_at(v, branches, attach):
    """`v` plus the given branch graphs; each branch is joined to `v` at one vertex
    when `attach` is set, else left as it is (disjoint from `v`)."""
    g = nx.Graph()
    g.add_node(v)
    for branch in branches:
        g = nx.union(g, branch)
        if attach:
            g.add_edge(v, next(iter(branch.nodes())))
    return g


def test_branch_lemma_hypotheses_matter_on_hand_instances():
    """The corrected `branch_lemma`: three disjoint *connected* branches of pathwidth
    ≥ k, each *attached* to `v`, force pathwidth ≥ k + 1 — and dropping either
    hypothesis breaks it, which is why the statement Sandwich.lean carried with
    `sorry` until 2026-09-28 (neither hypothesis) was false."""
    # k = 1: three edges (pathwidth 1 each) attached to v give the subdivided claw,
    # pathwidth 2 = k + 1 (`spider` in the Lean file).
    edges = [nx.relabel_nodes(nx.path_graph(2), {0: 1 + 2 * i, 1: 2 + 2 * i}) for i in range(3)]
    attached = _three_branches_at(0, edges, attach=True)
    assert nx.is_isomorphic(attached, _spider())
    assert sw.vertex_separation(attached) == 2
    # Same branches, not attached: pathwidth stays 1. The old statement's other
    # hypotheses all hold (v outside, disjoint, no edges between branches).
    unattached = _three_branches_at(0, edges, attach=False)
    assert sw.vertex_separation(unattached) == 1
    # `old_branch_statement_false` in Lean: k = 0, four isolated vertices, pathwidth 0.
    assert sw.vertex_separation(nx.empty_graph(4)) == 0
    # Attached but disconnected branches: each branch is an edge plus an isolated
    # vertex, v attached to the isolated vertex; pathwidth 1 = k, not k + 1.
    disconnected = []
    for i in range(3):
        b = nx.Graph()
        b.add_edge(10 * (i + 1) + 1, 10 * (i + 1) + 2)
        b.add_node(10 * (i + 1))          # first node: the isolated one, attached to v
        b = nx.relabel_nodes(b, {})
        disconnected.append(b)
    g = nx.Graph()
    g.add_node(0)
    for b in disconnected:
        g = nx.union(g, b)
        g.add_edge(0, min(b.nodes()))
    assert sw.vertex_separation(g) == 1
    # Attached and connected but with edges between the branches: still ≥ k + 1
    # (the lemma needs no separation hypothesis) — a triangle of edges' endpoints.
    linked = attached.copy()
    linked.add_edges_from([(2, 4), (4, 6), (6, 2)])
    assert sw.vertex_separation(linked) >= 2


def test_inventory_names_are_declared_in_the_lean_file():
    """Every name the axiom check asks for is a declaration in Sandwich.lean, and the
    only `sorry` left is the conjecture's."""
    text = (sw.LEAN_DIR / "MOSPFormalization" / "Sandwich.lean").read_text()
    # Three of the MOSP-terms names are proved in MOSPGraph.lean and re-exported here.
    both = text + (sw.LEAN_DIR / "MOSPFormalization" / "MOSPGraph.lean").read_text()
    for name in sw.PROVED + sw.STATED:
        short = name.split(".")[-1]
        assert f"theorem {short}" in both or f"def {short}" in both or \
            f"theorem PathDecomposition.{short}" in both, name
    assert "treewidth_le_pathwidth" in sw.PROVED
    assert "branch_lemma" in sw.PROVED
    assert sw.STATED == ("conjecture_sqrt_tw_f6",)
    body = text.split("/-! ### Tree decompositions -/", 1)[1]
    assert body.count("\n  sorry") == 1
