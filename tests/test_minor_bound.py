"""The contraction-minor step on both sides (2026-10-12, `reports/minor_bound.md`).

A refutation on a contraction certifies the optimum, so the failure that
matters is a minor that is not a minor, or whose pathwidth exceeds the graph's:
the descent would then stop above the optimum with a witness that verifies.
Checked here: the contraction against the exact pathwidth DP, the MOSP-side
contraction against the graph side's, the recorded sequence against its
replay, and the descent with the step against the certified optima.
"""

import json
import random
import sys
from pathlib import Path

import networkx as nx
import pytest

from fixed_parameter_algorithm.pathwidth import compute_pathwidth
from mosp.instance import MOSPInstance
from satisfiability.customer_search import decide, solve
from satisfiability.heuristics import _neighbour_masks
from satisfiability.relaxation import (MinorConfig, MinorLadder, build, minor_groups,
                                       minor_sequence)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pathwidth_solver"))
from pathwidth.minor import contraction_sequence, replay  # noqa: E402

ALWAYS = MinorConfig(min_customers=0, start_fraction=0.0, step_fraction=0.0, max_fraction=1.0,
                     probe_nodes=0)


def _graph(masks):
    G = nx.Graph()
    for v, m in enumerate(masks):
        if m:
            G.add_node(v)
            for u in range(len(masks)):
                if u != v and m >> u & 1:
                    G.add_edge(v, u)
    return G


def _random_instance(rng, n_customers, n_patterns, per_product=(2, 4)):
    rows = [[0] * n_patterns for _ in range(n_customers)]
    for p in range(n_patterns):
        for c in rng.sample(range(n_customers), rng.randint(*per_product)):
            rows[c][p] = 1
    return MOSPInstance.from_matrix(rows, name="r")


@pytest.mark.parametrize("rule", ["min-d", "least-c"])
def test_the_minor_never_exceeds_the_graph_by_exact_dp(rule):
    """pw(minor) <= pw(G) on random graphs, with the subset DP as the oracle."""
    rng = random.Random(41)
    checked = 0
    for _ in range(60):
        n = rng.randint(4, 13)
        G = nx.convert_node_labels_to_integers(
            nx.gnp_random_graph(n, rng.uniform(0.15, 0.7), seed=rng.randint(0, 10**6)))
        masks = [(1 << v) | sum(1 << u for u in G[v]) for v in range(n)]
        pw, _ = compute_pathwidth(G)
        for size in range(1, n):
            minor, _, _ = replay(masks, contraction_sequence(masks, size, rule))
            H = _graph(minor)
            H.add_nodes_from(range(len(minor)))
            assert compute_pathwidth(H)[0] <= pw
            checked += 1
    assert checked > 300


@pytest.mark.parametrize("rule", ["min-d", "least-c"])
def test_the_mosp_contraction_is_the_graph_contraction(rule):
    """Merging customers contracts the MOSP graph: the MOSP side's sequence
    is the graph side's, and the merged instance's MOSP graph is the minor."""
    rng = random.Random(42)
    for _ in range(80):
        inst = _random_instance(rng, rng.randint(4, 16), rng.randint(3, 14))
        masks = _neighbour_masks(inst)
        n = sum(1 for m in masks if m)
        for size in range(0, n + 1):
            seq = minor_sequence(inst, size, rule)
            assert seq == contraction_sequence(masks, size, rule)
            groups = minor_groups(inst, seq)
            minor, labels, branch = replay(masks, seq)
            merged = build(inst, groups)
            active = [i for i, g in enumerate(groups) if merged.customer_patterns(i)]
            got = _neighbour_masks(merged)
            assert len(active) == len(minor)
            by_members = {frozenset(b): labels.index(v) for v, b in branch.items()}
            for i in active:
                j = by_members[groups[i].members]
                want = {by_members[groups[x].members] for x in active if got[i] >> x & 1}
                assert want == {y for y in range(len(minor)) if minor[j] >> y & 1}


def test_minor_groups_rejects_what_is_not_a_contraction():
    inst = MOSPInstance.from_matrix([[1, 0, 0], [1, 1, 0], [0, 1, 1], [0, 0, 1], [0, 0, 0]])
    with pytest.raises(ValueError):
        minor_groups(inst, [(0, 2)])          # share no product
    with pytest.raises(ValueError):
        minor_groups(inst, [(0, -1)])         # 0 shares a product with 1
    with pytest.raises(ValueError):
        minor_groups(inst, [(4, 0)])          # customer 4 has no products
    groups = minor_groups(inst, [(0, 1), (3, 2)])
    assert [g.members for g in groups] == [frozenset({0, 1}), frozenset({2, 3}), frozenset({4})]


def test_the_step_never_changes_a_proved_answer_small():
    """With the step forced on at every size, the descent agrees with the
    descent without it, and every minor certificate replays and refutes."""
    rng = random.Random(43)
    proofs = {}
    for _ in range(120):
        inst = _random_instance(rng, rng.randint(5, 14), rng.randint(4, 14))
        off = solve(inst, minor=False)
        on = solve(inst, minor=ALWAYS)
        assert off.proved and on.proved
        assert on.value == off.value
        assert on.lower <= on.value
        proofs[on.proof] = proofs.get(on.proof, 0) + 1
        if on.proof == "minor" and on.minor is not None:
            cert = on.minor
            minor = build(inst, minor_groups(inst, [tuple(p) for p in cert["contractions"]]))
            assert decide(minor, cert["refuted"]).status == "unsat"
            assert decide(minor, cert["refuted"], subset_rule=False, definite_move=False,
                          old_move=False).status == "unsat"       # memo only
            assert cert["refuted"] + 1 == on.value
    assert proofs.get("minor", 0) > 10


CORPUS = ["Random-40-40-2-1_0", "Random-40-40-4-1_0", "Random-50-50-2-1_0",
          "Random-50-50-4-1_0", "Random-50-50-6-1_0", "Random-50-50-8-1_0",
          "Random-50-100-2-1_0", "Random-75-75-6-1_0"]


def _corpus_instance(name):
    stem, idx = name.rsplit("_", 1)
    path = ROOT / "benchmarks/instances/MOSP_Instances/Chu_Stuckey" / f"{stem}.txt"
    record = ROOT / "solutions" / f"{name}.json"
    if not path.exists() or not record.exists():
        pytest.skip(f"{name} not present")
    return MOSPInstance.from_benchmark_file(str(path))[int(idx)], json.loads(record.read_text())


@pytest.mark.parametrize("name", CORPUS)
def test_the_step_never_changes_a_certified_optimum(name):
    """The default step on corpus instances it reaches (>= 40 customers)."""
    inst, record = _corpus_instance(name)
    sol = solve(inst, minor=MinorConfig(total_nodes=2_000_000), time_budget=120)
    assert sol.proved, name
    assert sol.value == record["mosp_value"]
    assert sol.lower <= sol.value


def test_solve_mosp_exact_records_certified_minor(tmp_path):
    """A value proved by a minor is saved as certified:minor with its bound,
    and never replaces a refutation of the same value. Writes to tmp only."""
    from satisfiability import mosp_solver as ms

    inst, record = _corpus_instance("Random-50-50-2-1_0")
    stats = {}
    val, ordering = ms.solve_mosp_exact(inst, solutions_dir=tmp_path, stats=stats,
                                        minor=MinorConfig(min_customers=0), time_budget=120)
    assert val == record["mosp_value"]
    saved = json.loads((tmp_path / f"{inst.name}.json").read_text())
    if stats["proof"] == "minor":
        assert saved["provenance"] == ms.PROVENANCE_MINOR
        assert saved["lower_bound"] == val and saved["lower_bound_source"] == "minor"
    # a later refutation upgrades it; a later minor certificate never demotes one
    ms._save_solution(inst, val, ordering, tmp_path, provenance=ms.PROVENANCE_REFUTATION)
    ms._save_solution(inst, val, ordering, tmp_path, provenance=ms.PROVENANCE_MINOR)
    assert json.loads((tmp_path / f"{inst.name}.json").read_text())["provenance"] == \
        ms.PROVENANCE_REFUTATION
    ms._save_solution(inst, val, ordering, tmp_path, provenance=ms.PROVENANCE_SOLUTION)
    assert json.loads((tmp_path / f"{inst.name}.json").read_text())["provenance"] == \
        ms.PROVENANCE_REFUTATION


def test_the_ladder_raises_a_lower_bound_without_closing():
    """A contraction's exact optimum is a lower bound even when it is below
    the value, and it is never above the true optimum."""
    rng = random.Random(44)
    raised = 0
    for _ in range(40):
        inst = _random_instance(rng, rng.randint(8, 14), rng.randint(6, 14))
        opt = solve(inst, minor=False).value
        ladder = MinorLadder(inst, ALWAYS)
        ladder.try_refute(opt)                       # sat everywhere: records witnesses
        cert = ladder.raise_lower(0)
        if cert is not None:
            assert cert.refuted + 1 <= opt
            raised += 1
    assert raised > 10
