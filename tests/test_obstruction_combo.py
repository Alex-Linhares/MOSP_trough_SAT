"""loop0013 item 11 (reserve, F5): `learning.obstruction_combo` — the
one-pattern-per-edge instance has the graph as its MOSP graph; Harper's
cap-12 floor on a minor never exceeds the lifted layout's vertex separation
+ 1 (so never the optimum); the ceiling seeded with a layout never exceeds
that layout's vertex separation + 1; a composite certificate (a family-B
certificate on a contraction minor) round-trips through the independent
checker's `check-combo` and a damaged sequence, a wrong minor hash and an
inflated claim are rejected; the expansion inner certificate (SAT + DRAT on
the minor) verifies too; the ten targets are the residual less the largest
gap; the committed run files, where present, carry no floor above an optimum."""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from learning import obstruction_combo as occ
from learning import obstruction_branch as ob
from learning import obstruction_expansion as oe
from learning.obstruction_ledger import adjacency_from_matrix
from learning.obstruction_minor import (replay, minor_graph, minor_masks, lifted_layout, vertex_separation,
                                        greedy_sequence, edge_list)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "paper1"))
import obstruction_check as oc  # noqa: E402


def _random_matrix(rng: random.Random, n: int, m: int, p: float) -> np.ndarray:
    while True:
        matrix = np.array([[1 if rng.random() < p else 0 for _ in range(m)] for _ in range(n)], dtype=int)
        if matrix.sum(axis=1).min() >= 1:
            return matrix


def test_edge_instance_matrix_has_the_graph_as_mosp_graph():
    rng = random.Random(3)
    for _ in range(30):
        n = rng.randint(2, 12)
        matrix = _random_matrix(rng, n, rng.randint(2, 10), 0.3)
        adj = adjacency_from_matrix(matrix)
        edges = edge_list(adj)
        back = adjacency_from_matrix(occ.edge_instance_matrix(n, edges))
        assert back == adj
        # the checker's own writer agrees column for column
        rows = oc.edge_pattern_rows(n, edges)
        assert np.array_equal(np.array(rows), occ.edge_instance_matrix(n, edges))


def test_harper_floor_and_ceiling_on_minors_respect_the_lifted_layout():
    rng = random.Random(5)
    for _ in range(12):
        n = rng.randint(6, 13)
        matrix = _random_matrix(rng, n, rng.randint(n, 2 * n), 0.25)
        adj = adjacency_from_matrix(matrix)
        order = list(range(n))
        rng.shuffle(order)
        position = [0] * n
        for i, v in enumerate(order):
            position[v] = i
        seq = greedy_sequence(adj, 0, "least-c")[:rng.randint(0, max(0, n - 4))]
        cur, alive, branch = replay(adj, seq)
        labels, edges = minor_graph(cur, alive)
        m = len(labels)
        if m < 3:
            continue
        madj = minor_masks(m, edges)
        lifted = lifted_layout(labels, branch, position)
        vs = vertex_separation(madj, lifted)
        hf = occ.harper_floor_on(madj, 5.0)
        assert hf["floor"] <= vs + 1                      # Harper's floor <= pw(H) + 1 <= vs(lifted) + 1
        ce = occ.ceiling_on(madj, [lifted], 0.3)
        assert ce["ceiling"] <= vs + 1                    # seeded with the layout's prefixes
        assert ce["ceiling"] >= hf["floor"]               # the ceiling is above the family's floor
        if m <= 12:
            exact, _ = oe.exact_profile(oe.closed_masks(madj)).harper()
            assert hf["floor"] <= exact <= ce["ceiling"]


def _pendant_theta() -> np.ndarray:
    """The theta graph (11 customers) with a pendant path 0 - 11 - 12."""
    base = ob.theta_matrix()
    n, p = base.shape
    matrix = np.zeros((n + 2, p + 2), dtype=int)
    matrix[:n, :p] = base
    matrix[0, p] = matrix[n, p] = 1
    matrix[n, p + 1] = matrix[n + 1, p + 1] = 1
    return matrix


def _composite_branch(tmp_path: Path):
    name = "pendant_theta"
    matrix = _pendant_theta()
    adj = adjacency_from_matrix(matrix)
    seq = [(12, 11), (11, 0)]
    cur, alive, branch = replay(adj, seq)
    labels, edges = minor_graph(cur, alive)
    m = len(labels)
    assert m == 11 and labels == list(range(11))
    madj = minor_masks(m, edges)
    res = ob.branch_search(madj, 20.0)
    assert res["value"] + 1 == 3
    oe.write_standard_instance(tmp_path / "instance.mosp", name, matrix)
    inner = ob.certificate_dict(f"{name}::minor[{m}]", None, madj, res, None, 5.0)
    (tmp_path / "b").mkdir()
    occ.write_edge_list(tmp_path / "b" / "minor.txt", m, edges)
    (tmp_path / "b" / "branch.json").write_text(json.dumps(inner))
    comp = occ.composite_dict(name, matrix, adj, seq, labels, edges, "branch", "b/branch.json", "b/minor.txt",
                              inner["floor"], inner["pathwidth_proved"], None, "test")
    (tmp_path / "combo_branch.json").write_text(json.dumps(comp))
    return tmp_path / "instance.mosp", tmp_path / "combo_branch.json", comp


def test_composite_branch_certificate_round_trips_and_damage_is_rejected(tmp_path):
    inst, cp, comp = _composite_branch(tmp_path)
    assert comp["floor"] == 3 and comp["pathwidth_proved"] == 2
    res = oc.check_combo(inst, cp)
    assert res["verdict"] == "verified", [c for c in res["checks"] if not c["ok"]]
    assert res["proves"]["mosp_at_least"] == 3 and res["m"] == 11 and res["inner_kind"] == "branch"
    # damaged 1: a pair that is not an edge at its step
    bad = json.loads(cp.read_text())
    bad["sequence"] = [[12, 0], [11, 0]]
    (tmp_path / "bad1.json").write_text(json.dumps(bad))
    r = oc.check_combo(inst, tmp_path / "bad1.json")
    assert r["verdict"] == "rejected" and any("edge of the current graph" in c["check"] for c in r["checks"] if not c["ok"])
    # damaged 2: a different (legal) sequence with the old minor hash
    bad = json.loads(cp.read_text())
    bad["sequence"] = [[12, 11]]
    (tmp_path / "bad2.json").write_text(json.dumps(bad))
    r = oc.check_combo(inst, tmp_path / "bad2.json")
    assert r["verdict"] == "rejected" and any("minor" in c["check"] for c in r["checks"] if not c["ok"])
    # damaged 3: the claim inflated by one (the inner certificate proves only 2)
    bad = json.loads(cp.read_text())
    bad["pathwidth_proved"] += 1
    bad["floor"] += 1
    (tmp_path / "bad3.json").write_text(json.dumps(bad))
    r = oc.check_combo(inst, tmp_path / "bad3.json")
    assert r["verdict"] == "rejected" and any("proves pathwidth(minor)" in c["check"] for c in r["checks"] if not c["ok"])
    # the CLI
    assert oc.main(["check-combo", str(inst), str(cp)]) == 0
    assert oc.main(["check-combo", str(inst), str(tmp_path / "bad3.json")]) == 1


def test_composite_expansion_certificate_verifies(tmp_path):
    pytest.importorskip("pysat")
    if not oc.DEFAULT_DRAT_TRIM.exists():
        pytest.skip("drat-trim is not built")
    name = "pendant_theta"
    matrix = _pendant_theta()
    adj = adjacency_from_matrix(matrix)
    seq = [(12, 11), (11, 0)]
    cur, alive, branch = replay(adj, seq)
    labels, edges = minor_graph(cur, alive)
    m = len(labels)
    madj = minor_masks(m, edges)
    closed = oe.closed_masks(madj)
    prof = oe.exact_profile(closed)
    value, t = prof.harper()
    b = prof.values[t] - 1
    emat = occ.edge_instance_matrix(m, edges)
    pdir = tmp_path / "e"
    pdir.mkdir()
    oe.write_standard_instance(pdir / "instance.mosp", f"{name}::minor[{m}]", emat)
    res = oe.exact_sat(closed, t, b, proof_dir=pdir, conflicts=100000, deadline=30.0,
                       instance_name=f"{name}::minor[{m}]", matrix_sha=oe.matrix_sha256(emat), source_file="test")
    assert res["status"] == "unsat" and res["verdict"] == "verified"
    oe.write_standard_instance(tmp_path / "instance.mosp", name, matrix)
    comp = occ.composite_dict(name, matrix, adj, seq, labels, edges, "expansion", f"e/t{t}_b{b}.json",
                              "e/instance.mosp", b + 2 - t, b + 1 - t, None, "test")
    (tmp_path / "combo_expansion.json").write_text(json.dumps(comp))
    out = oc.check_combo(tmp_path / "instance.mosp", tmp_path / "combo_expansion.json")
    assert out["verdict"] == "verified", [c for c in out["checks"] if not c["ok"]]
    assert out["proves"]["mosp_at_least"] == value == b + 2 - t
    assert out["proves"]["mosp_at_least"] == 4           # the theta graph has pathwidth 3 (brute force), and Harper is tight on it


def test_harper_evaluator_keeps_minors_in_the_window():
    matrix = _pendant_theta()
    adj = adjacency_from_matrix(matrix)
    n = len(adj)
    ev = occ.HarperEvaluator(adj, 3, 0.0, None, deadline=float("inf"), min_m=8, max_m=n, eval_seconds=2.0)
    full = greedy_sequence(adj, 0, "least-c")
    small = ev.evaluate(full[:n - 4])            # 4 vertices: outside the window
    assert small["source"] == "out_of_range" and small["floor"] == 1
    inside = ev.evaluate(full[:n - 9])           # 9 vertices
    assert inside["source"].startswith("harper_cap") and 1 <= inside["floor"] <= 3
    assert ev.best_floor == inside["floor"] and ev.evaluations == 1


def test_residual_ten_is_the_residual_less_the_largest_gap():
    if not occ.MAP_CSV.exists():
        pytest.skip("item 08's map is not on disk")
    ten = occ.residual_ten()
    m = pd.read_csv(occ.MAP_CSV)
    residual = m[m["is_gap338"] & (m["gap_best"] > 0)]
    assert len(ten) == len(residual) - 1
    assert ten["gap_best"].max() <= residual["gap_best"].max()
    assert residual["gap_best"].idxmax() not in set(ten.index) or len(residual) == 1
    assert "Random-125-125-4-1_0" not in set(ten["instance_name"])


def test_committed_scan_has_no_floor_above_an_optimum():
    if not occ.SCAN_CSV.exists():
        pytest.skip("item 11's scan is not on disk")
    s = pd.read_csv(occ.SCAN_CSV)
    for col in ("c_floor", "e_floor12", "b_value", "combo_floor"):
        v = s[col].dropna()
        assert (v <= s.loc[v.index, "optimum"]).all(), col
    assert (s["e_ceiling"].dropna() <= s.loc[s["e_ceiling"].dropna().index, "optimum"]).all()
    if occ.CHECKER_CSV.exists():
        ck = pd.read_csv(occ.CHECKER_CSV)
        assert (ck["verdict"] == "verified").all(), ck[ck["verdict"] != "verified"]
