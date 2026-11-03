"""loop0013 item 06: `learning.obstruction_branch` — the theta graph gives 3
at `S = {0, 1}`, the spider of spiders 4 (depth 2) and the hand instances of
`learning.bound_harness`'s tests their recorded values; the value is never
above the optimum on 100 random instances at `n ≤ 14` with brute-force
leaves; the mask-level link condition agrees with the harness's
`linked_third`; a certificate round-trips through the independent checker
and a damaged link, a damaged branch and an inflated claim are rejected; a
trivial-node branch is accepted only with claim 0; the committed run files."""
from __future__ import annotations

import itertools
import json
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from learning import obstruction_branch as ob
from learning.obstruction_ledger import adjacency_from_matrix

ROOT = Path(__file__).resolve().parents[1]
SCRATCH = ROOT / "reports" / "scratch" / "obstruction_search" / "06_branch"
sys.path.insert(0, str(ROOT / "paper1"))
import obstruction_check as oc  # noqa: E402

nx = pytest.importorskip("networkx")


def _random_matrix(rng: random.Random, n: int, m: int, p: float) -> np.ndarray:
    while True:
        matrix = np.array([[1 if rng.random() < p else 0 for _ in range(m)] for _ in range(n)], dtype=int)
        if matrix.sum(axis=1).min() >= 1:
            return matrix


def _brute_search(matrix, seconds: float = 30.0):
    adj = adjacency_from_matrix(matrix)
    return adj, ob.branch_search(adj, seconds, kind="brute", local=True, minor_leaves=False)


# ----------------------------------------------------------------------------
# hand instances
# ----------------------------------------------------------------------------


def test_theta_gives_3_at_the_hub_pair():
    adj = adjacency_from_matrix(ob.theta_matrix())
    res = ob.branch_search(adj, 20.0)
    assert res["value"] + 1 == 3                  # optimum units; pathwidth >= 2
    assert res["S"] == [0, 1]
    assert ob.branch_widths(res["node"]) == [1, 1, 1]
    assert all(len(b["vertices"]) == 3 for b in res["node"]["branches"])


def test_spider_of_spiders_needs_depth_two():
    adj = adjacency_from_matrix(ob.spider_of_spiders_matrix())
    assert ob.branch_search(adj, 20.0)["value"] + 1 == 4
    # with the C program denied the branches (brute leaves give exact widths too), depth 1 alone sees only
    # the three spiders as leaves of width 2 - still 4; with leaves capped at 0 the recursion is what certifies
    res = ob.branch_search(adj, 20.0, depth=1, kind="brute")
    assert res["value"] + 1 == 4


@pytest.mark.parametrize("name, matrix, expected", [(h[0], h[1], h[2]) for h in ob.HAND])
def test_hand_instances_reproduce_the_seeded_form(name, matrix, expected):
    adj = adjacency_from_matrix(matrix)
    res = ob.branch_search(adj, 20.0)
    value = res["value"] + 1 if res["value"] >= 0 else None
    assert value == expected, name


# ----------------------------------------------------------------------------
# validity against brute force at n <= 14
# ----------------------------------------------------------------------------


def test_value_never_above_the_optimum_on_random_instances():
    from learning.first_moment import vertex_separation_brute

    rng = random.Random(6)
    checked = triples = 0
    for _ in range(100):
        n = rng.randint(6, 14)
        m = rng.randint(n // 2, 2 * n)
        p = rng.choice((0.1, 0.15, 0.2, 0.3))
        matrix = _random_matrix(rng, n, m, p)
        adj, res = _brute_search(matrix, 10.0)
        optimum = vertex_separation_brute(adj) + 1
        checked += 1
        if res["value"] >= 0:
            triples += 1
            assert res["value"] + 1 <= optimum
            node = res["node"]
            assert node["pathwidth_at_least"] == node["k"] + 1
            for b in node["branches"]:
                assert b["pathwidth_at_least"] >= node["k"]
                sub = adjacency_from_matrix(np.asarray(matrix)[sorted(b["vertices"])][:, :])
                # the branch's claim is at most its true width (brute on the induced subgraph)
                labels, sadj, _ = ob.induced(adj, ob.mask_of(b["vertices"]))
                assert b["pathwidth_at_least"] <= vertex_separation_brute(sadj)
    assert checked == 100
    assert triples >= 10        # the sample is not vacuous


def test_components_and_links_agree_with_the_harness():
    from learning import bound_harness as bh

    rng = random.Random(1)
    for _ in range(60):
        n = rng.randint(6, 16)
        g = nx.gnp_random_graph(n, rng.choice((0.15, 0.25, 0.4)), seed=rng.randrange(10 ** 6))
        adj = [0] * n
        for u, v in g.edges():
            adj[u] |= 1 << v
            adj[v] |= 1 << u
        top = (1 << n) - 1
        for comp in ob.components(adj, top):
            assert nx.is_connected(g.subgraph(ob.bits(comp)))
        assert sum(ob.popcount(c) for c in ob.components(adj, top)) == n
        S = ob.mask_of(rng.sample(range(n), rng.randint(1, 3)))
        comps = ob.components(adj, top & ~S)
        values = [rng.randint(0, 3) for _ in comps]
        mine = ob.best_linked_triple(adj, S, comps, values, top=len(comps))
        theirs = bh.linked_third(g, frozenset(ob.bits(S)), [set(ob.bits(c)) for c in comps], values) \
            if len(comps) <= 10 else None
        if len(comps) <= 10:
            assert (mine[0] if mine else None) == theirs


# ----------------------------------------------------------------------------
# the certificate and the checker
# ----------------------------------------------------------------------------


def _write(tmp_path: Path, name: str, matrix) -> tuple[Path, Path, dict]:
    adj = adjacency_from_matrix(matrix)
    res = ob.branch_search(adj, 20.0)
    assert res["node"] is not None
    ob.write_standard_instance(tmp_path / f"{name}.mosp", name, matrix)
    cert = ob.certificate_dict(name, matrix, adj, res, None, 5.0)
    (tmp_path / f"{name}.json").write_text(json.dumps(cert))
    return tmp_path / f"{name}.mosp", tmp_path / f"{name}.json", cert


def test_certificate_round_trips_and_damage_is_rejected(tmp_path):
    inst, cp, cert = _write(tmp_path, "theta", ob.theta_matrix())
    res = oc.check_branch(inst, cp)
    assert res["verdict"] == "verified", [c for c in res["checks"] if not c["ok"]]
    assert res["proves"]["pathwidth_at_least"] == 2 and res["proves"]["mosp_at_least"] == 3
    assert res["c_reruns"] == 3 and res["nodes_checked"] == 4
    # a damaged link: Q taken outside S
    bad = json.loads(cp.read_text())
    bad["node"]["links"][0]["Q"] = bad["node"]["branches"][2]["vertices"][:1]
    (tmp_path / "bad1.json").write_text(json.dumps(bad))
    r = oc.check_branch(inst, tmp_path / "bad1.json")
    assert r["verdict"] == "rejected" and any("Q ⊆ S" in c["check"] for c in r["checks"] if not c["ok"])
    # a damaged branch: a vertex moved from one branch into another (disconnected, overlapping)
    bad = json.loads(cp.read_text())
    v = bad["node"]["branches"][0]["vertices"][0]
    bad["node"]["branches"][1]["vertices"].append(v)
    (tmp_path / "bad2.json").write_text(json.dumps(bad))
    r = oc.check_branch(inst, tmp_path / "bad2.json")
    assert r["verdict"] == "rejected"
    # an inflated claim: k + 1 raised by one at the top
    bad = json.loads(cp.read_text())
    bad["node"]["k"] += 1
    bad["node"]["pathwidth_at_least"] += 1
    bad["pathwidth_proved"] += 1
    bad["floor"] += 1
    (tmp_path / "bad3.json").write_text(json.dumps(bad))
    r = oc.check_branch(inst, tmp_path / "bad3.json")
    assert r["verdict"] == "rejected"
    assert any("claims >=" in c["check"] or "re-proves" in c["check"] for c in r["checks"] if not c["ok"])
    # a wrong instance file
    ob.write_standard_instance(tmp_path / "other.mosp", "other", ob.spider_of_spiders_matrix())
    assert oc.check_branch(tmp_path / "other.mosp", cp)["verdict"] == "rejected"
    # the command line
    assert oc.main(["check-branch", str(inst), str(cp)]) == 0
    assert oc.main(["check-branch", str(inst), str(tmp_path / "bad1.json")]) == 1


def test_trivial_nodes_only_certify_zero(tmp_path):
    """Two pendant vertices and a long path at a hub: k = 0 with the big
    branch left unproved (a trivial node), accepted; the same node claiming 1
    is rejected."""
    n, edges = 8, [(0, 1), (0, 2), (0, 3), (3, 4), (4, 5), (5, 6), (6, 7)]
    matrix = ob.from_cliques(n, edges)
    inst, cp, cert = _write(tmp_path, "pend", matrix)
    assert cert["k"] == 0 and cert["floor"] == 2
    kinds = sorted(b["kind"] for b in cert["node"]["branches"])
    assert "trivial" in kinds
    assert oc.check_branch(inst, cp)["verdict"] == "verified"
    bad = json.loads(cp.read_text())
    for b in bad["node"]["branches"]:
        if b["kind"] == "trivial" and len(b["vertices"]) > 1:
            b["pathwidth_at_least"] = 1
    bad["node"]["k"], bad["node"]["pathwidth_at_least"], bad["pathwidth_proved"], bad["floor"] = 1, 2, 2, 3
    (tmp_path / "bad.json").write_text(json.dumps(bad))
    assert oc.check_branch(inst, tmp_path / "bad.json")["verdict"] == "rejected"


def test_nested_certificate_checks_recursively(tmp_path):
    """The spider of spiders with brute leaves replaced by nested branch
    nodes: the checker recurses and re-runs the C program on the nine P2
    leaves (cliques: no C call) and accepts."""
    matrix = ob.spider_of_spiders_matrix()
    adj = adjacency_from_matrix(matrix)
    oracle = ob.LeafOracle(adj, 5.0, kind="c", minor_leaves=False)
    ctx = ob.Context(adj, oracle, float("inf"), random.Random(0))
    top = (1 << len(adj)) - 1
    # force the branch route: evaluate at S = {0} with the three spiders' nodes built by the rule at S = {c}
    value, node, _ = ob.value_at(ctx, top, 1, 1, 0)
    assert value == 3                                # pathwidth >= 3
    for b in node["branches"]:
        if b["kind"] == "c":
            # replace the C leaf by its own branch node (the rule inside the spider)
            hub = min(b["vertices"])
            v2, nd2, _ = ob.value_at(ctx, ob.mask_of(b["vertices"]), 1 << hub, 0, 0)
            assert v2 == 2 and nd2["kind"] == "branch"
            b.clear()
            b.update(nd2)
    res = {"value": value, "node": node, "S": [0], "stats": {"seconds": 0.0}}
    ob.write_standard_instance(tmp_path / "sos.mosp", "sos", matrix)
    cert = ob.certificate_dict("sos", matrix, adj, res, None, 5.0)
    (tmp_path / "sos.json").write_text(json.dumps(cert))
    r = oc.check_branch(tmp_path / "sos.mosp", tmp_path / "sos.json")
    assert r["verdict"] == "verified", [c for c in r["checks"] if not c["ok"]]
    assert r["nodes_checked"] == 1 + 3 + 9 and r["proves"]["mosp_at_least"] == 4


def test_lazy_evaluation_makes_no_c_call_when_two_branches_are_single_vertices():
    """A hub with two pendant vertices and one large branch: k = 0 is decided
    by the upper bounds alone."""
    n, edges = 12, [(0, 1), (0, 2)] + [(0, 3)] + [(i, i + 1) for i in range(3, 11)] + [(3, 5), (4, 6), (5, 7)]
    adj = adjacency_from_matrix(ob.from_cliques(n, edges))
    res = ob.branch_search(adj, 20.0, local=False)
    assert res["value"] == 1 and res["stats"]["c_calls"] == 0        # pathwidth >= 1 (k = 0), nothing asked of the C


# ----------------------------------------------------------------------------
# the committed run files
# ----------------------------------------------------------------------------


def test_committed_run_files():
    if not (SCRATCH / "search.csv").exists():
        pytest.skip("item 06's run is not on disk")
    s = pd.read_csv(SCRATCH / "search.csv")
    assert s.instance_name.is_unique
    assert (s.loc[s.has_triple.astype(bool), "b_value"] <= s.loc[s.has_triple.astype(bool), "optimum"]).all()
    if (SCRATCH / "checker_verdicts.csv").exists():
        ck = pd.read_csv(SCRATCH / "checker_verdicts.csv")
        assert (ck.verdict == "verified").all(), ck[ck.verdict != "verified"]
    if (SCRATCH / "hand.csv").exists():
        h = pd.read_csv(SCRATCH / "hand.csv")
        assert h.agrees.all()
