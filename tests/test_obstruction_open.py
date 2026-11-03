"""loop0013 item 07: the 24 open classes. The complete ternary tree's nested B
certificate (`ternary_tree_certificate`) verifies through the independent
checker and matches brute force at small heights; non-trees and incomplete
trees are refused; the evaluator's size window and the leaf oracle's size cap
never send an out-of-range graph to the C program; `open_class_graphs` reads
the 24 with a layout of the recorded width in the prefix orientation; the
committed run files carry no floor above a recorded width."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import pytest

from learning import obstruction_branch as ob
from learning import obstruction_minor as om

ROOT = Path(__file__).resolve().parents[1]
OPEN = ROOT / "reports" / "scratch" / "obstruction_search" / "07_open"
sys.path.insert(0, str(ROOT / "paper1"))
import obstruction_check as oc  # noqa: E402


def ternary_tree(height: int) -> tuple[int, list[tuple[int, int]]]:
    """The complete ternary tree of the given height, root 0, BFS labels."""
    edges, frontier, nxt = [], [0], 1
    for _ in range(height):
        new = []
        for v in frontier:
            for _ in range(3):
                edges.append((v, nxt))
                new.append(nxt)
                nxt += 1
        frontier = new
    return nxt, edges


@pytest.mark.parametrize("height", [1, 2, 3])
def test_tree_certificate_verifies_and_claims_the_height(height, tmp_path):
    n, edges = ternary_tree(height)
    cert = ob.ternary_tree_certificate(n, edges, f"T{height}")
    assert cert["pathwidth_proved"] == height and cert["height"] == height and cert["root"] == 0
    inst = tmp_path / "tree.txt"
    inst.write_text(f"{n} {len(edges)}\n" + "".join(f"{a} {b}\n" for a, b in edges))
    cp = tmp_path / "cert.json"
    cp.write_text(json.dumps(cert))
    res = oc.check_branch(inst, cp)
    assert res["verdict"] == "verified", [c for c in res["checks"] if not c["ok"]]
    assert res["c_reruns"] == 0 and res["nodes_checked"] == n


@pytest.mark.parametrize("height", [1, 2])
def test_tree_height_is_the_exact_pathwidth_at_small_heights(height):
    from learning.first_moment import vertex_separation_brute
    from learning.obstruction_ledger import adjacency_from_edges

    n, edges = ternary_tree(height)
    assert vertex_separation_brute(adjacency_from_edges(n, edges)) == height


def test_tree_certificate_refuses_non_trees_and_incomplete_trees():
    n, edges = ternary_tree(2)
    with pytest.raises(ValueError):
        ob.ternary_tree_certificate(n, edges + [(1, 2)], "cycle")          # not a tree
    with pytest.raises(ValueError):
        ob.ternary_tree_certificate(n, edges[:-1] + [(12, 13)] if False else edges[:-1], "short")  # disconnected
    # a leaf removed from one subtree: unequal heights
    n2, e2 = ternary_tree(2)
    e2 = [e for e in e2 if e != (3, 12)]
    with pytest.raises(ValueError):
        ob.ternary_tree_certificate(n2 - 1, e2, "incomplete")


def test_damaged_tree_certificate_is_rejected(tmp_path):
    n, edges = ternary_tree(2)
    cert = ob.ternary_tree_certificate(n, edges, "T2")
    cert["pathwidth_proved"] += 1
    cert["floor"] += 1
    cert["node"]["pathwidth_at_least"] += 1
    inst = tmp_path / "tree.txt"
    inst.write_text(f"{n} {len(edges)}\n" + "".join(f"{a} {b}\n" for a, b in edges))
    cp = tmp_path / "cert.json"
    cp.write_text(json.dumps(cert))
    assert oc.check_branch(inst, cp)["verdict"] == "rejected"


def test_evaluator_size_window_skips_without_a_c_call():
    from learning.obstruction_ledger import adjacency_from_edges

    n, edges = ternary_tree(2)
    adj = adjacency_from_edges(n, edges)
    ev = om.Evaluator(adj, None, 1.0, None, min_m=5, max_m=8, greedy_upper_max_m=0)
    res = ev.evaluate([])                                 # the whole graph, 13 > max_m
    assert res["source"] == "out_of_range" and ev.calls == 0 and ev.out_of_range == 1
    seq = om.greedy_sequence(adj, 4, "min-d")             # down to 4 < min_m
    res = ev.evaluate(seq)
    assert res["source"] == "out_of_range" and ev.calls == 0 and ev.out_of_range == 2
    seq = om.greedy_sequence(adj, 6, "min-d")             # inside the window: sent to the C program
    res = ev.evaluate(seq)
    assert res["source"] != "out_of_range" and ev.calls == 1 and res["m"] == 6


def test_leaf_oracle_size_cap_yields_a_trivial_node():
    from learning.obstruction_ledger import adjacency_from_edges

    n, edges = ternary_tree(2)
    adj = adjacency_from_edges(n, edges)
    oracle = ob.LeafOracle(adj, 1.0, max_m=5)
    node = oracle.width((1 << n) - 1)
    assert node["kind"] == "trivial" and node["pathwidth_at_least"] == 0 and node["source"] == "skipped_large"
    assert oracle.calls == 0 and oracle.skipped_large == 1
    # the recorded layout restricted to a set is an upper bound; the greedy layout is off above greedy_max_m
    oracle2 = ob.LeafOracle(adj, 1.0, position=list(range(n)), greedy_max_m=0)
    assert oracle2.upper((1 << n) - 1) <= n - 1


def test_open_class_graphs_reads_the_24_with_layouts_of_the_recorded_width():
    from learning.obstruction_ledger import open_class_graphs

    recs = open_class_graphs(check_representative=False)
    assert len(recs) == 24
    for r in recs:
        assert r["layout"] is not None and r["layout_vs"] == r["width"], r["id"]
        assert len(r["edges"]) == r["m"] and len(r["adj"]) == r["n"]
    tree = next(r for r in recs if r["names"] == "BalancedTree_3_5")
    assert (tree["n"], tree["m"]) == (364, 363)


@pytest.mark.skipif(not (OPEN / "joined.csv").exists(), reason="item 07 run files not present")
def test_committed_open_run_files_carry_no_floor_above_a_recorded_width():
    j = pd.read_csv(OPEN / "joined.csv")
    assert len(j) == 24
    assert not j["above_width"].any()
    assert (j["e_ceiling_pw"].dropna() <= j.loc[j["e_ceiling_pw"].notna(), "width"]).all()
    tree = j[j["names"] == "BalancedTree_3_5"].iloc[0]
    assert tree["theorem_pw"] == 5 and tree["closed"]
    rows = pd.read_csv(OPEN / "results_obstruction.csv")
    assert list(rows.columns) == om.OPEN_FIELDS
    assert (rows["lower"] >= rows["width"]).all() and (rows["width"] == rows["recorded"]).all()
    if (OPEN / "checker_verdicts.csv").exists():
        v = pd.read_csv(OPEN / "checker_verdicts.csv")
        assert (v["verdict"] == "verified").all(), v[v["verdict"] != "verified"]
