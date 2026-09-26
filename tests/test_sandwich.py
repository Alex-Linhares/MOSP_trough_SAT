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
