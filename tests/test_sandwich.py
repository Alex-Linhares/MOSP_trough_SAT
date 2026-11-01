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
    """Every name the axiom check asks for is a declaration in Sandwich.lean, and no
    `sorry` is left: the conjecture was proved on 2026-10-31."""
    text = (sw.LEAN_DIR / "MOSPFormalization" / "Sandwich.lean").read_text()
    # Three of the MOSP-terms names are proved in MOSPGraph.lean and re-exported here.
    both = text + (sw.LEAN_DIR / "MOSPFormalization" / "MOSPGraph.lean").read_text()
    for name in sw.PROVED + sw.STATED:
        short = name.split(".")[-1]
        assert f"theorem {short}" in both or f"def {short}" in both or \
            f"theorem PathDecomposition.{short}" in both, name
    assert "treewidth_le_pathwidth" in sw.PROVED
    assert "branch_lemma" in sw.PROVED
    assert "branch_lemma_separator" in sw.PROVED
    assert "branch_lemma_of_separator" in sw.PROVED
    assert "conjecture_sqrt_tw_f6" in sw.PROVED
    assert sw.STATED == ()
    body = text.split("/-! ### Tree decompositions -/", 1)[1]
    assert body.count("\n  sorry") == 0


# ---------------------------------------------------------------------------
# loop0004 item 13: the separator form of the branch lemma (Lemma A of §38)
# ---------------------------------------------------------------------------

def _branches_through_separator(branch, separator_edge, attach):
    """Three copies of `branch` (nodes relabelled 10i + j) and a two-vertex separator
    `{100, 101}`, joined by an edge when `separator_edge` is set; `attach` maps each
    branch index to the separator vertex its first node is joined to."""
    g = nx.Graph()
    g.add_nodes_from([100, 101])
    if separator_edge:
        g.add_edge(100, 101)
    for i in range(3):
        b = nx.relabel_nodes(branch, {u: 10 * (i + 1) + u for u in branch.nodes()})
        g = nx.union(g, b)
        g.add_edge(attach[i], min(b.nodes()))
    return g


def test_separator_branch_lemma_hypotheses_matter_on_hand_instances():
    """`branch_lemma_separator` (Lemma A): three disjoint connected branches of
    pathwidth ≥ k, every two joined through a connected subset of a separator `S`
    disjoint from them, force pathwidth ≥ k + 1 — and the pairwise-link hypothesis
    is what carries it: with the same `S` as two isolated vertices, one pair
    unlinked, the pathwidth stays at k."""
    from fixed_parameter_algorithm.pathwidth import compute_pathwidth
    edge = nx.path_graph(2)
    # k = 1, S = {100, 101} an edge (one component of G[S]); branch A hangs from 100,
    # B and D from 101. Every pair is linked through that component: pathwidth 2.
    linked = _branches_through_separator(edge, True, {0: 100, 1: 101, 2: 101})
    assert sw.vertex_separation(linked) == 2
    # Same attachments, S without its edge: {100} links A with nothing else, {101}
    # links B with D only, so the pair (A, B) has no connector — pathwidth 1 = k.
    unlinked = _branches_through_separator(edge, False, {0: 100, 1: 101, 2: 101})
    assert sw.vertex_separation(unlinked) == 1
    # Both connectors present but A, B on one and D on the other: (A, D) unlinked,
    # pathwidth 1 = k again.
    split = _branches_through_separator(edge, False, {0: 100, 1: 100, 2: 101})
    assert sw.vertex_separation(split) == 1
    # k = 2 with triangles (11 vertices, exact DP): linked gives 3, unlinked 2.
    tri = nx.complete_graph(3)
    assert compute_pathwidth(_branches_through_separator(tri, True, {0: 100, 1: 101, 2: 101}))[0] == 3
    assert compute_pathwidth(_branches_through_separator(tri, False, {0: 100, 1: 101, 2: 101}))[0] == 2
    # The case S = {v} is `branch_lemma` (`branch_lemma_of_separator`): the spider.
    assert sw.vertex_separation(_spider()) == 2


# ---------------------------------------------------------------------------
# loop0010 item 11: ForestCover.lean — the blow-up bound, the forest form, the
# coupling inclusion — against brute force on tiny instances
# ---------------------------------------------------------------------------

def _tiny_instances(count=60, seed=1101):
    """Random tiny instances as pattern lists (`n ≤ 7`, `m ≤ 5`, sizes 1–3); the
    incidence graph is a forest on a fair share of them."""
    import numpy as np
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(count):
        n = int(rng.integers(2, 8))
        m = int(rng.integers(1, 6))
        pats = [sorted(rng.choice(n, size=int(rng.integers(1, min(3, n) + 1)), replace=False).tolist())
                for _ in range(m)]
        out.append((n, pats))
    return out


def _brute_mosp(n, pats):
    """The MOSP value by brute force over pattern orders (no solver, nothing persisted)."""
    import itertools
    best = None
    for order in itertools.permutations(range(len(pats))):
        first, last = {}, {}
        for pos, j in enumerate(order):
            for c in pats[j]:
                first.setdefault(c, pos)
                last[c] = pos
        width = 0
        for pos in range(len(order)):
            width = max(width, sum(1 for c in first if first[c] <= pos <= last[c]))
        best = width if best is None else min(best, width)
    return best


def _exact_pw(g):
    from fixed_parameter_algorithm.pathwidth import compute_pathwidth
    return 0 if g.number_of_nodes() == 0 else compute_pathwidth(g)[0]


def test_forest_cover_inventory_names_are_declared():
    """Every name of `FOREST_COVER_PROVED` is a declaration in ForestCover.lean, which has
    no `sorry` and no `axiom`, and is imported by the root module."""
    text = (sw.LEAN_DIR / "MOSPFormalization" / "ForestCover.lean").read_text()
    for name in sw.FOREST_COVER_PROVED:
        short = name.split(".")[-1]
        assert f"theorem {short}" in text or f"def {short}" in text, name
    code = text.split("-/", 1)[1]  # past the module docstring
    assert "sorry" not in code and "\naxiom" not in code
    root = (sw.LEAN_DIR / "MOSPFormalization.lean").read_text()
    assert "import MOSPFormalization.ForestCover\n" in root
    assert set(sw.FOREST_COVER_PROVED) <= set(sw.ALL_PROVED)
    assert "MOSPInstance.mospValue_le_maxPatternSize_mul" in sw.FOREST_COVER_PROVED


def test_tree_bound_inverse_is_the_least_k():
    """`treeBoundInv N = ⌊log₃((6N + 3)/5)⌋` is the least `k` with `N ≤ treeBound k`
    (`le_treeBound_treeBoundInv`, `treeBound_lt_of_lt_treeBoundInv`), and agrees with
    `learning.block_trees.tree_bound`."""
    from learning.block_trees import tree_bound
    assert [sw.tree_bound_rec(k) for k in range(6)] == [1, 6, 21, 66, 201, 606]
    assert [sw.tree_bound_lean(N) for N in (0, 1, 2, 6, 7, 21, 22, 66, 67)] == [0, 0, 1, 1, 2, 2, 3, 3, 4]
    assert sw.tree_bound_identity_check(2000) == 2001
    for N in range(0, 700):
        assert sw.tree_bound_lean(N) == tree_bound(N)


def test_blowup_bound_on_tiny_instances():
    """`mospValue ≤ ω (pw(B) + 1)` (`mospValue_le_maxPatternSize_mul`) and
    `pw(G_M) + 1 ≤ (pw(B) + 1) ω` (`pathwidth_mospGraph_add_one_le`) on random tiny
    instances, forest or not, with both pathwidths by the exact subset DP and the MOSP
    value by brute force over orders; and the forest form
    `mospValue ≤ ω (treeBoundInv (n + m) + 1)` where the incidence graph is a forest."""
    from learning.block_trees import incidence_graph, is_incidence_forest, largest_pattern, mosp_graph
    forests = 0
    for n, pats in _tiny_instances():
        omega = largest_pattern(pats)
        pw_m = _exact_pw(mosp_graph(pats, n))
        pw_b = _exact_pw(incidence_graph(pats, n))
        mosp = _brute_mosp(n, pats)
        assert mosp == pw_m + 1  # mospValue_eq_pathwidth_add_one, the instance has a requirement
        assert mosp <= omega * (pw_b + 1)
        assert pw_m + 1 <= (pw_b + 1) * omega
        if is_incidence_forest(pats, n):
            forests += 1
            assert mosp <= omega * (sw.tree_bound_lean(n + len(pats)) + 1)
    assert forests >= 10


def test_subinstance_monotonicity_on_tiny_instances():
    """`mospValue_mono`: adding requirements never lowers the MOSP value."""
    import numpy as np
    rng = np.random.default_rng(1102)
    for n, pats in _tiny_instances(30, seed=1103):
        bigger = [sorted(set(p) | set(rng.choice(n, size=1).tolist())) for p in pats]
        assert _brute_mosp(n, pats) <= _brute_mosp(n, bigger)


def test_coupling_inclusion_on_tiny_covers():
    """`isEmptyPair_coverGraph_of_subset`: every empty pair of the larger cover's graph is
    an empty pair of the smaller's; `pathwidth_coverGraph_mono`: pathwidth is monotone."""
    import itertools
    import numpy as np
    from learning.block_trees import mosp_graph
    rng = np.random.default_rng(1104)
    for n, pats in _tiny_instances(30, seed=1105):
        bigger = [sorted(set(p) | set(rng.choice(n, size=1).tolist())) for p in pats]
        g, g2 = mosp_graph(pats, n), mosp_graph(bigger, n)
        assert set(g.edges()) <= set(g2.edges())
        assert _exact_pw(g) <= _exact_pw(g2)
        verts = range(n)
        for a_size in range(1, 3):
            for A in itertools.combinations(verts, a_size):
                rest = [v for v in verts if v not in A]
                for R in itertools.combinations(rest, 1):
                    empty2 = not any(g2.has_edge(a, r) for a in A for r in R)
                    empty1 = not any(g.has_edge(a, r) for a in A for r in R)
                    assert (not empty2) or empty1


def test_forest_cover_record_has_no_violation():
    """The Lean statements on item 03's record (item 06's CSV): zero violations of (L2)
    and (L4), slack at least one on every row."""
    if not sw.FOREST_RECORD.exists():
        pytest.skip("item 06's record CSV is absent")
    frame = sw.forest_cover_check()
    total = frame[frame.family == "all"].iloc[0]
    assert total["rows"] == 4419 and total["both exact (L2)"] == 4410
    assert total["L2 violations"] == 0 and total["L4 violations"] == 0
    assert total["L2 slack min"] >= 1 and total["L4 slack min"] >= 1


def test_layer_lemma_on_small_connected_graphs():
    """`pathwidth_le_layerWidth_dist`: on random small connected graphs, with `L_i` the BFS
    layers from vertex 0, `pathwidth ≤ max_i (|L_i| + |L_{i+1}|) − 1` (exact DP pathwidth);
    and any 1-Lipschitz level function works (`pathwidth_le_layerWidth`), not only BFS."""
    import numpy as np
    rng = np.random.default_rng(1106)
    checked = tight = 0
    while checked < 40:
        n = int(rng.integers(2, 9))
        g = nx.gnp_random_graph(n, float(rng.uniform(0.2, 0.7)), seed=int(rng.integers(1 << 30)))
        if not nx.is_connected(g):
            continue
        dist = nx.single_source_shortest_path_length(g, 0)
        h = max(dist.values())
        sizes = [sum(1 for v in g if dist[v] == i) for i in range(h + 2)]
        width = max(sizes[i] + sizes[i + 1] for i in range(h + 1))
        pw = _exact_pw(g)
        assert pw <= width - 1
        tight += pw == width - 1
        # a non-BFS layering: levels shifted by a random 1-Lipschitz perturbation along levels
        lvl = {v: dist[v] // 2 for v in g}
        for u, v in g.edges():
            assert abs(lvl[u] - lvl[v]) <= 1
        hh = max(lvl.values())
        sizes2 = [sum(1 for v in g if lvl[v] == i) for i in range(hh + 2)]
        assert pw <= max(sizes2[i] + sizes2[i + 1] for i in range(hh + 1)) - 1
        checked += 1
    assert tight >= 1
