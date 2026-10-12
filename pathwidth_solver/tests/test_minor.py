"""The contraction-minor step (`pathwidth/minor.py`, 2026-10-12).

A lower bound that is too high makes the descent report a wrong width that no
witness contradicts, so the minor is checked three ways: the contraction is a
genuine edge contraction (against networkx's `contracted_nodes`, an
independent implementation); its pathwidth never exceeds the graph's (brute
force); and the descent with the step proves the same widths as without it.
"""

import itertools
import random
import sys
from pathlib import Path

import networkx as nx
import pytest

from pathwidth.graph import masks_from_graph, vertex_separation_masks
from pathwidth.minor import (MinorConfig, MinorLadder, check_branch_sets, contraction_sequence,
                             replay)
from pathwidth.search import decide
from pathwidth.solve import solve, solve_masks

BENCH = Path(__file__).resolve().parents[1] / "bench"
sys.path.insert(0, str(BENCH))
from readers import HERE, read_any  # noqa: E402

ALWAYS = MinorConfig(min_vertices=0, start_fraction=0.0, step_fraction=0.0, max_fraction=1.0,
                     probe_nodes=0)


def brute(masks):
    active = [v for v in range(len(masks)) if masks[v]]
    if not active:
        return -1
    return min(vertex_separation_masks(masks, list(p)) for p in itertools.permutations(active))


def random_graphs(seed, count, nmin=3, nmax=8):
    rng = random.Random(seed)
    for _ in range(count):
        yield nx.gnp_random_graph(rng.randint(nmin, nmax), rng.uniform(0.1, 0.9),
                                  seed=rng.randint(0, 10**6))


def nx_replay(G, sequence):
    """The same sequence with networkx, which knows nothing of masks."""
    H = nx.Graph(G)
    for v, u in sequence:
        if u == -1:
            assert H.degree(v) == 0
            H.remove_node(v)
        else:
            assert H.has_edge(v, u)
            H = nx.contracted_nodes(H, u, v, self_loops=False)
    return H


@pytest.mark.parametrize("rule", ["min-d", "least-c"])
def test_the_contraction_is_a_genuine_edge_contraction(rule):
    for G in random_graphs(31, 150, 2, 14):
        G = nx.convert_node_labels_to_integers(G)
        masks, _ = masks_from_graph(G)
        for size in range(0, G.number_of_nodes() + 1):
            seq = contraction_sequence(masks, size, rule)
            minor, labels, branch = replay(masks, seq)
            assert len(minor) == min(size, G.number_of_nodes())
            check_branch_sets(masks, minor, labels, branch)
            H = nx_replay(G, seq)
            assert sorted(H.nodes) == labels
            want = {frozenset((labels.index(a), labels.index(b))) for a, b in H.edges}
            got = {frozenset((i, j)) for i in range(len(minor)) for j in range(i + 1, len(minor))
                   if minor[i] >> j & 1}
            assert got == want
            assert all(minor[i] >> i & 1 for i in range(len(minor)))   # self-inclusive, no loops lost


def test_the_minor_sequence_is_a_prefix():
    for G in random_graphs(32, 40, 10, 20):
        masks, _ = masks_from_graph(G)
        n = len(masks)
        for rule in ("min-d", "least-c"):
            full = contraction_sequence(masks, 2, rule)
            for size in range(2, n + 1):
                assert contraction_sequence(masks, size, rule) == full[:n - size]


def test_replay_rejects_what_is_not_a_minor():
    masks, _ = masks_from_graph(nx.path_graph(4))      # 0-1-2-3
    with pytest.raises(ValueError):
        replay(masks, [(0, 2)])                         # not an edge
    with pytest.raises(ValueError):
        replay(masks, [(0, -1)])                        # deleting a vertex with an edge
    with pytest.raises(ValueError):
        replay(masks, [(0, 1), (0, 2)])                 # 0 is gone
    minor, labels, branch = replay(masks, [(0, 1), (3, 2)])
    assert labels == [1, 2] and branch == {1: {0, 1}, 2: {2, 3}}


def test_the_minor_never_exceeds_the_graph():
    for G in random_graphs(33, 120):
        masks, _ = masks_from_graph(G)
        pw = brute(masks)
        for rule in ("min-d", "least-c"):
            for size in range(1, len(masks) + 1):
                minor, _, _ = replay(masks, contraction_sequence(masks, size, rule))
                assert brute(minor) <= pw, (nx.to_graph6_bytes(G), rule, size)


def test_the_step_never_changes_a_proved_width_small():
    """With the step forced on at every size, the descent agrees with brute force."""
    proofs = {}
    for G in random_graphs(34, 150, 4, 8):
        masks, _ = masks_from_graph(G)
        sol = solve_masks(masks, minor=ALWAYS)
        assert sol.proved
        assert sol.width == brute(masks) == vertex_separation_masks(masks, sol.order)
        assert sol.lower <= sol.width
        proofs[sol.proof] = proofs.get(sol.proof, 0) + 1
        if sol.proof == "minor":
            cert = sol.minor
            minor, _, _ = replay(masks, [tuple(p) for p in cert["contractions"]])
            assert decide(minor, cert["refuted"] + 1).status == "unsat"
            assert cert["refuted"] + 1 == sol.width
    assert proofs.get("minor", 0) > 0


def test_the_step_never_changes_a_proved_width_medium():
    """At 20-40 vertices, on and off agree, and both carry a proof."""
    rng = random.Random(35)
    for _ in range(30):
        n = rng.randint(20, 40)
        G = nx.gnp_random_graph(n, rng.uniform(0.08, 0.4), seed=rng.randint(0, 10**6))
        off = solve(G, minor=False)
        on = solve(G, minor=MinorConfig(min_vertices=0))
        assert off.proved and on.proved
        assert on.width == off.width
        assert on.lower <= on.width


def test_a_minor_raises_the_lower_bound_of_an_unproved_descent():
    """myciel5: refuse the full refutation (one node) and the minor still
    proves the lower bound; the certificate replays."""
    path = HERE / "coloring" / "myciel5.dgf"
    if not path.exists():
        pytest.skip("bench/instances/ is git-ignored and not present")
    G = nx.convert_node_labels_to_integers(read_any(path))
    masks, _ = masks_from_graph(G)
    sol = solve_masks(masks)
    assert sol.width == 20 and sol.proof == "minor"
    cert = sol.minor
    seq = [tuple(p) for p in cert["contractions"]]
    minor, labels, branch = replay(masks, seq)
    check_branch_sets(masks, minor, labels, branch)
    assert len(minor) == cert["size"]
    assert decide(minor, cert["refuted"] + 1).status == "unsat"
    assert decide(minor, cert["refuted"] + 1, old_move=False, subset_rule=False,
                  definite_move=False).status == "unsat"         # memo only: no dominance rule

    ladder = MinorLadder(masks)
    assert ladder.try_refute(30) is None                  # far above pw: every minor is sat
    raised = ladder.raise_lower(0)
    assert raised is not None and raised.refuted + 1 <= 20


def test_solve_translates_the_certificate_to_labels():
    path = HERE / "coloring" / "myciel5.dgf"
    if not path.exists():
        pytest.skip("bench/instances/ is git-ignored and not present")
    G = read_any(path)
    G = nx.relabel_nodes(G, {v: f"v{v}" for v in G})
    sol = solve(G)
    assert sol.proof == "minor"
    masks, labels = masks_from_graph(G)
    index = {lab: i for i, lab in enumerate(labels)}
    seq = [(index[v], index[u] if u is not None else -1) for v, u in sol.minor["contractions"]]
    minor, _, _ = replay(masks, seq)
    assert decide(minor, sol.minor["refuted"] + 1).status == "unsat"
