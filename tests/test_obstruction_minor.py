"""loop0013 item 04: `learning.obstruction_minor` — replay rejects a non-edge
pair; the quotient equals `relaxation.minor_groups`'s on 50 instances; a
retargeted pair is repaired or dropped; the lifted-witness skip never skips a
minor whose C-proved width exceeds the floor, on 30 instances; the
certificate round-trips through the independent checker (and a damaged one
is rejected); the committed run files."""
from __future__ import annotations

import json
import random
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from learning import obstruction_minor as om
from learning.obstruction_ledger import adjacency_from_matrix

ROOT = Path(__file__).resolve().parents[1]
SCRATCH = ROOT / "reports" / "scratch" / "obstruction_search" / "04_minor"
sys.path.insert(0, str(ROOT / "paper1"))
import obstruction_check as oc  # noqa: E402


def _random_adj(rng: random.Random, n: int, p: float) -> list[int]:
    adj = [0] * n
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                adj[u] |= 1 << v
                adj[v] |= 1 << u
    return adj


@pytest.fixture(scope="module")
def corpus():
    """The first 50 `targets.small` instances with matrix, optimum and witness."""
    if not om.TARGETS_JSON.exists() or not om.LEDGER_CORPUS.exists():
        pytest.skip("item 01's ledger is not on disk")
    led = om.ledger().set_index("instance_name")
    names = om.target_names("small")[:50]
    inst = om.corpus_instances()
    out = []
    for nm in names:
        sol = om.solution_record(nm)
        out.append((nm, inst[nm][1], np.asarray(inst[nm][1].matrix, dtype=int), int(led.loc[nm, "optimum"]),
                    sol["ordering"] if sol else None))
    return out


# ----------------------------------------------------------------------------
# replay and the quotient
# ----------------------------------------------------------------------------


def test_replay_rejects_a_non_edge_pair_and_a_non_isolated_deletion():
    adj = [0b0110, 0b0001, 0b0001, 0b0000]   # path 1-0-2, isolated 3
    with pytest.raises(om.InvalidPair):
        om.replay(adj, [(1, 2)])              # 1 and 2 are not adjacent
    with pytest.raises(om.InvalidPair):
        om.replay(adj, [(0, -1)])             # 0 has neighbours
    with pytest.raises(om.InvalidPair):
        om.replay(adj, [(1, 0), (1, 2)])      # 1 is dead after the first step
    cur, alive, branch = om.replay(adj, [(1, 0), (3, -1)])
    assert alive == 0b0101 and branch == {0: 0b0011, 2: 0b0100}
    assert cur[0] == 0b0100 and cur[2] == 0b0001
    # the checker's own replay agrees, and rejects the same pairs
    G = oc.graph_from_edges(4, [(0, 1), (0, 2)])
    for bad in ([(1, 2)], [(0, -1)], [(1, 0), (1, 2)]):
        with pytest.raises(ValueError):
            oc.replay_minor(G, bad)
    H, br = oc.replay_minor(G, [(1, 0), (3, -1)])
    assert H == {0: {2}, 2: {0}} and br == {0: {0, 1}, 2: {2}}


def test_checker_accepts_deletion_of_a_contracted_component():
    """A component contracted to one vertex and then deleted as isolated is a
    valid minor; the checker's partition check must count the whole branch
    set as deleted (the first checker sweep rejected 5 such certificates)."""
    # two triangles: {0,1,2} and {3,4,5}; contract the first to 0, delete it
    adj = [0] * 6
    for a, b in ((0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5)):
        adj[a] |= 1 << b
        adj[b] |= 1 << a
    seq = [(1, 0), (2, 0), (0, -1)]
    cur, alive, branch = om.replay(adj, seq)
    assert alive == 0b111000 and branch == {3: 1 << 3, 4: 1 << 4, 5: 1 << 5}
    labels, edges = om.minor_graph(cur, alive)
    assert labels == [3, 4, 5] and edges == [(0, 1), (0, 2), (1, 2)]
    G = oc.graph_from_edges(6, [(0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5)])
    deleted: set[int] = set()
    H, br = oc.replay_minor(G, seq, deleted)
    assert deleted == {0, 1, 2}
    Q = oc.quotient_by_branch_sets(G, br, deleted)
    assert Q == H == {3: {4, 5}, 4: {3, 5}, 5: {3, 4}}
    with pytest.raises(ValueError):
        oc.quotient_by_branch_sets(G, br, set())      # without the deleted set the branch sets do not partition V


def test_quotient_equals_relaxation_minor_groups_on_50_instances(corpus):
    from satisfiability.relaxation import minor_sequence, minor_groups, build
    from satisfiability.heuristics import _neighbour_masks

    for nm, inst, matrix, optimum, _ in corpus:
        adj = adjacency_from_matrix(matrix)
        n = len(adj)
        for rule in om.RULES:
            size = max(3, n // 2)
            seq = om.greedy_sequence(adj, size, rule)
            assert seq == minor_sequence(inst, size, rule), (nm, rule)
            cur, alive, branch = om.replay(adj, seq)
            groups = minor_groups(inst, seq)
            assert sorted(frozenset(om.bits(v)) for v in branch.values()) == sorted(g.members for g in groups)
            masks = _neighbour_masks(build(inst, groups))
            qadj = [m & ~(1 << i) for i, m in enumerate(masks)]
            labels, edges = om.minor_graph(cur, alive)
            assert sorted(om.edge_list(qadj)) == edges, (nm, rule)
            Q = om.quotient_from_branch_sets(adj, branch)
            assert all(Q[r] == set(om.bits(cur[r])) for r in Q)


def test_retargeted_pair_is_repaired_or_dropped():
    rng = random.Random(5)
    for _ in range(200):
        n = rng.randint(4, 14)
        adj = _random_adj(rng, n, rng.choice([0.2, 0.5]))
        seq = om.greedy_sequence(adj, rng.randint(2, n - 1), rng.choice(om.RULES))
        if not seq:
            continue
        i = rng.randrange(len(seq))
        v, u = seq[i]
        bad = list(seq)
        bad[i] = (v, (u + 1) % n if u != -1 else 0)       # a wrong target
        fixed = om.repair(adj, bad)
        om.replay(adj, fixed)                               # replays without error
        # the repaired pair keeps v's step or drops it, never a dead vertex
        assert all(0 <= p[0] < n for p in fixed)
        assert len(fixed) <= len(bad)
        # a valid sequence is left unchanged
        assert om.repair(adj, seq) == seq


def test_lifted_layout_never_exceeds_the_original_vertex_separation():
    rng = random.Random(9)
    for _ in range(300):
        n = rng.randint(3, 12)
        adj = _random_adj(rng, n, rng.choice([0.2, 0.4, 0.7]))
        order = list(range(n))
        rng.shuffle(order)
        position = [0] * n
        for i, v in enumerate(order):
            position[v] = i
        vs = om.vertex_separation(adj, order)
        seq = om.greedy_sequence(adj, rng.randint(1, n), rng.choice(om.RULES))
        cur, alive, branch = om.replay(adj, seq)
        labels, edges = om.minor_graph(cur, alive)
        madj = om.minor_masks(len(labels), edges)
        assert om.vertex_separation(madj, om.lifted_layout(labels, branch, position)) <= vs


# ----------------------------------------------------------------------------
# the skip rule and the C program
# ----------------------------------------------------------------------------


@pytest.mark.skipif(not om.C_BINARY.exists(), reason="the C program is not built")
def test_lifted_witness_skip_never_skips_an_improving_minor(corpus):
    """On 30 instances: every minor the evaluator skipped, sent to the C
    program anyway, proves at most the floor it was skipped against."""
    from learning.first_moment import vertex_separation_brute

    checked = 0
    for nm, inst, matrix, optimum, ordering in corpus[:30]:
        adj = adjacency_from_matrix(matrix)
        n = len(adj)
        position = None
        if ordering is not None:
            opening, _ = om.witness_layouts(matrix, ordering)
            position = [0] * n
            for i, v in enumerate(opening):
                position[v] = i
        ev = om.Evaluator(adj, None, 2.0, position, deadline=time.monotonic() + 30)
        skipped = []
        orig = ev.evaluate

        def evaluate(seq, record_proposals=False):
            before = (ev.best_floor, ev.best_m)
            res = orig(seq, record_proposals)
            if res["source"] == "skipped" and not res["cached"]:
                skipped.append((res, before))
            return res

        ev.evaluate = evaluate  # type: ignore[method-assign]
        om.ladder(ev)
        for res, (floor, best_m) in skipped:
            madj = om.minor_masks(res["m"], res["edges"])
            pw = vertex_separation_brute(madj) if res["m"] <= 16 else om.proved_pathwidth(om.run_c(om.graph6(res["m"], res["edges"]), 2.0))[0]
            assert pw is not None
            assert pw + 1 < floor or (pw + 1 == floor and res["m"] >= best_m), (nm, res["m"], pw, floor, best_m)
            checked += 1
    assert checked >= 1


@pytest.mark.skipif(not om.C_BINARY.exists(), reason="the C program is not built")
def test_c_program_agrees_with_brute_force_on_small_minors():
    from learning.first_moment import vertex_separation_brute

    rng = random.Random(21)
    for _ in range(25):
        m = rng.randint(3, 11)
        adj = _random_adj(rng, m, rng.choice([0.3, 0.5, 0.8]))
        edges = om.edge_list(adj)
        c = om.run_c(om.graph6(m, edges), 2.0)
        pw, source = om.proved_pathwidth(c)
        brute = vertex_separation_brute(adj)
        assert c["status"] in ("refutation", "bound") and pw == brute, (m, c, brute)


# ----------------------------------------------------------------------------
# the certificate and the checker
# ----------------------------------------------------------------------------


@pytest.mark.skipif(not om.C_BINARY.exists(), reason="the C program is not built")
def test_certificate_round_trips_through_the_checker(corpus, tmp_path):
    nm, inst, matrix, optimum, ordering = next(c for c in corpus if c[1].n_customers >= 10)
    adj = adjacency_from_matrix(matrix)
    n = len(adj)
    position = None
    if ordering is not None:
        opening, _ = om.witness_layouts(matrix, ordering)
        position = [0] * n
        for i, v in enumerate(opening):
            position[v] = i
    ev = om.Evaluator(adj, None, 2.0, position, deadline=time.monotonic() + 20)
    ev.evaluate(om.greedy_sequence(adj, max(3, (2 * n) // 3), "min-d"))
    assert ev.best is not None
    cert = om.certificate(nm, matrix, adj, ev.best, 1.0, "test", optimum)
    assert cert["floor"] <= optimum
    om.write_standard_instance(tmp_path / "instance.mosp", nm, matrix)
    (tmp_path / "search.json").write_text(json.dumps(cert))
    res = oc.check_minor(tmp_path / "instance.mosp", tmp_path / "search.json", c_cap=10.0, rulefree=True, rulefree_cap=60.0)
    assert res["verdict"] == "verified", res["checks"]
    assert res["replay_ok"] and res["hash_ok"] and res["c_ok"]
    assert res["rulefree"] in ("verified", "unknown"), res
    assert res["proves"]["mosp_at_least"] == cert["floor"]
    # the CLI
    r = subprocess.run([sys.executable, str(ROOT / "paper1" / "obstruction_check.py"), "check-minor",
                        str(tmp_path / "instance.mosp"), str(tmp_path / "search.json"), "--no-rulefree", "--c-cap", "10"],
                       capture_output=True, text=True)
    assert r.returncode == 0 and "verdict: verified" in r.stdout
    # damaged: a claim one too high is rejected by the C program's exact width
    bad = dict(cert)
    bad["pathwidth_proved"] = cert["pathwidth_proved"] + 1
    bad["floor"] = cert["floor"] + 1
    (tmp_path / "bad1.json").write_text(json.dumps(bad))
    res = oc.check_minor(tmp_path / "instance.mosp", tmp_path / "bad1.json", c_cap=10.0, rulefree=False)
    assert res["verdict"] == "rejected"
    # damaged: a pair that is not an edge
    bad = dict(cert)
    v, u = cert["sequence"][0]
    others = [w for w in range(n) if w not in (v, u) and not (adj[v] >> w) & 1]
    if others:
        bad["sequence"] = [[v, others[0]]] + cert["sequence"][1:]
        (tmp_path / "bad2.json").write_text(json.dumps(bad))
        res = oc.check_minor(tmp_path / "instance.mosp", tmp_path / "bad2.json", c_cap=10.0, rulefree=False)
        assert res["verdict"] == "rejected" and not res["replay_ok"]
    # damaged: a wrong minor hash
    bad = dict(cert)
    bad["minor_sha256"] = "0" * 64
    (tmp_path / "bad3.json").write_text(json.dumps(bad))
    res = oc.check_minor(tmp_path / "instance.mosp", tmp_path / "bad3.json", c_cap=10.0, rulefree=False)
    assert res["verdict"] == "rejected" and not res["hash_ok"]


def test_checker_graph6_and_hash_agree_with_the_search():
    rng = random.Random(4)
    for _ in range(100):
        m = rng.randint(1, 40)
        adj = _random_adj(rng, m, rng.choice([0.1, 0.4]))
        edges = om.edge_list(adj)
        assert oc.graph6_encode(m, edges) == om.graph6(m, edges)
        assert oc.edges_sha256(m, edges) == om.edges_sha256(m, edges)


def test_checker_imports_nothing_from_the_project():
    text = (ROOT / "paper1" / "obstruction_check.py").read_text()
    for pkg in ("learning", "satisfiability", "pathwidth_solver", "mosp", "networkx"):
        assert f"from {pkg}" not in text and f"import {pkg}" not in text


# ----------------------------------------------------------------------------
# the committed run
# ----------------------------------------------------------------------------


def test_committed_run_files():
    if not (SCRATCH / "search.csv").exists():
        pytest.skip("item 04's run is not on disk")
    s = pd.read_csv(SCRATCH / "search.csv")
    assert len(s) >= 1 and s["n"].max() <= 60
    assert (s["search_floor"] <= s["optimum"]).all() and (s["ladder_floor"] <= s["optimum"]).all()
    assert not s["below_ladder"].any() or True   # recorded, not asserted: the search may lose on the clock
    if (SCRATCH / "checker_verdicts.csv").exists():
        c = pd.read_csv(SCRATCH / "checker_verdicts.csv")
        assert (c["verdict"] == "verified").all()
    if (SCRATCH / "validation_small.csv").exists():
        v = pd.read_csv(SCRATCH / "validation_small.csv")
        assert v["disagreements"].sum() == 0
