"""Phase 3: bounds are valid and the descent proves what it claims."""
import itertools
import random

import networkx as nx
import pytest

import pathwidth as pw
from pathwidth.bounds import contraction_degeneracy, degeneracy, greedy_order, lower_bound
from pathwidth.graph import masks_from_graph, vertex_separation_masks
from pathwidth.solve import initial_upper_bound, solve, solve_masks


def brute(masks):
    n = len(masks)
    return min(vertex_separation_masks(masks, p) for p in itertools.permutations(range(n))) if n else -1


def random_graphs(seed, count, nmin=3, nmax=8):
    rng = random.Random(seed)
    for _ in range(count):
        yield nx.gnp_random_graph(rng.randint(nmin, nmax), rng.uniform(0.1, 0.9), seed=rng.randint(0, 10**6))


def test_bounds_bracket_the_optimum():
    for G in random_graphs(21, 120):
        masks, _ = masks_from_graph(G)
        opt = brute(masks)
        lb = lower_bound(masks)
        assert degeneracy(masks) <= contraction_degeneracy(masks) <= opt, nx.to_graph6_bytes(G)
        assert lb <= opt
        ub_order = greedy_order(masks)
        assert sorted(ub_order) == list(range(len(masks)))
        assert vertex_separation_masks(masks, ub_order) >= opt
        ub, order = initial_upper_bound(masks)
        assert opt <= ub == vertex_separation_masks(masks, order)


def test_bounds_on_named_graphs():
    K5, _ = masks_from_graph(nx.complete_graph(5))
    assert degeneracy(K5) == contraction_degeneracy(K5) == 4
    C8, _ = masks_from_graph(nx.cycle_graph(8))
    assert contraction_degeneracy(C8) == 2          # cycle contracts to a triangle
    grid, _ = masks_from_graph(nx.grid_2d_graph(4, 4))
    assert 2 <= contraction_degeneracy(grid) <= 4
    tree, _ = masks_from_graph(nx.balanced_tree(2, 3))
    assert lower_bound(tree) == 1
    assert lower_bound([]) == 0 and lower_bound([0, 0]) == 0


def test_the_descent_matches_brute_force_and_labels_its_proof():
    proofs = {"refutation": 0, "bound": 0}
    for G in random_graphs(22, 120):
        masks, _ = masks_from_graph(G)
        sol = solve_masks(masks)
        assert sol.proved
        assert sol.width == brute(masks) == vertex_separation_masks(masks, sol.order)
        assert sol.lower <= sol.width <= sol.upper_start
        proofs[sol.proof] += 1
    assert proofs["refutation"] > 0 and proofs["bound"] > 0


def test_bound_proofs_where_the_lower_bound_is_tight():
    for G, w in [(nx.complete_graph(6), 5), (nx.cycle_graph(9), 2), (nx.path_graph(7), 1)]:
        sol = solve(G)
        assert (sol.width, sol.proof) == (w, "bound") and sol.nodes == 0


def test_refutation_proof_where_it_is_needed():
    sol = solve(nx.petersen_graph())
    assert sol.width == 5 and sol.proof == "refutation" and sol.nodes > 0
    sol = solve(nx.mycielski_graph(5))
    assert sol.width == 10 and sol.proof == "refutation"


def test_components_are_solved_separately_and_combined():
    G = nx.disjoint_union_all([nx.complete_graph(4), nx.cycle_graph(5), nx.path_graph(6), nx.empty_graph(2)])
    sol = solve(G)
    assert sol.width == 3 and sol.proved and len(sol.components) == 5   # empty_graph(2) is two components
    assert sorted(sol.order) == sorted(G.nodes)
    assert pw.vertex_separation(G, sol.order) == 3
    # the same answer with components off
    assert solve(G, components=False).width == 3
    assert pw.compute_pathwidth(G)[0] == 3


def test_budget_exhaustion_is_reported_not_claimed():
    G = nx.mycielski_graph(6)      # pw 20; refuting 19 takes ~700k nodes
    sol = solve(G, max_nodes=2000)
    assert not sol.proved and sol.proof == ""
    assert sol.width >= 20 and pw.vertex_separation(G, sol.order) == sol.width
    with pytest.raises(RuntimeError):
        pw.compute_pathwidth(G, max_nodes=2000)
    sol = solve(G, time_budget=0.02)
    assert not sol.proved


def test_on_improve_reports_each_step_and_the_start_is_honoured():
    G = nx.gnp_random_graph(14, 0.35, seed=5)
    seen = []
    sol = solve(G, upper=13, on_improve=lambda w, order: seen.append(w))
    assert sol.proved and seen and seen == sorted(seen, reverse=True) and seen[-1] == sol.width
    assert sol.upper_start == 13
    with pytest.raises(ValueError):
        solve(G, upper=0, upper_order=list(G.nodes))


def test_labels_and_empty_graphs():
    G = nx.relabel_nodes(nx.cycle_graph(5), {i: f"v{i}" for i in range(5)})
    sol = solve(G)
    assert sol.width == 2 and set(sol.order) == set(G.nodes)
    assert solve(nx.Graph()).width == -1
    assert solve(nx.empty_graph(3)).width == 0
    assert pw.compute_pathwidth(nx.Graph()) == (-1, [])
