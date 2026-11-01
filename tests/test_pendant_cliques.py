"""Lemma P, the two-sided pendant bound (`lean/MOSPFormalization/PendantCliques.lean`,
loop0010 item 13): the Lean statements pinned to brute force on tiny graphs, and the graph
evaluation `learning.forest_theorems.pendant_graph_bound` that the theorem licenses."""
from __future__ import annotations

import itertools

import networkx as nx
import numpy as np
import pytest

from learning import sandwich as sw
from learning.forest_theorems import pendant_candidate, pendant_graph_bound, pendant_lower_bound

PENDANT_NAMES = (
    "PathDecomposition.pendant_bound",
    "pathwidth_ge_of_pendant_cliques",
    "pathwidth_ge_of_clique_pendant_cliques",
    "MOSPInstance.mospValue_ge_of_pendant_patterns",
)


def _exact_pw(g: nx.Graph) -> int:
    from fixed_parameter_algorithm.pathwidth import compute_pathwidth
    return 0 if g.number_of_nodes() == 0 else compute_pathwidth(g)[0]


def _lemma_p_exhaustive(g: nx.Graph) -> int:
    """The best value of the Lean statement over every clique `R` and every choice of
    pendant cliques (dominated by the largest per attachment vertex), pathwidth units."""
    cliques = [frozenset(c) for c in nx.enumerate_all_cliques(g)]
    best = -1
    for R in cliques:
        per_vertex: dict = {}
        for Q in cliques:
            meet = Q & R
            if len(meet) == 1:
                (v,) = meet
                per_vertex[v] = max(per_vertex.get(v, 0), len(Q))
        sizes = sorted(per_vertex.values(), reverse=True)
        for q in range(1, len(sizes) + 1):
            best = max(best, sizes[q - 1] + (q + 1) // 2 - 2)
    return best


def _clique_with_pendants(s: int, t: int, q: int) -> nx.Graph:
    g = nx.complete_graph(s)
    nxt = s
    for v in range(q):
        block = [v] + list(range(nxt, nxt + t - 1))
        nxt += t - 1
        g.add_edges_from(itertools.combinations(block, 2))
    return g


def _brute_mosp(n: int, pats) -> int:
    best = None
    for order in itertools.permutations(range(len(pats))):
        first, last = {}, {}
        for pos, j in enumerate(order):
            for c in pats[j]:
                first.setdefault(c, pos)
                last[c] = pos
        width = max(sum(1 for c in first if first[c] <= pos <= last[c]) for pos in range(len(order)))
        best = width if best is None else min(best, width)
    return best


def test_inventory_names_are_declared_sorry_free_and_imported():
    text = (sw.LEAN_DIR / "MOSPFormalization" / "PendantCliques.lean").read_text()
    for name in PENDANT_NAMES:
        short = name.split(".")[-1]
        assert f"theorem {short}" in text, name
    code = text.split("-/", 1)[1]
    assert "sorry" not in code and "\naxiom" not in code
    root = (sw.LEAN_DIR / "MOSPFormalization.lean").read_text()
    assert "import MOSPFormalization.PendantCliques\n" in root
    assert set(PENDANT_NAMES) <= set(sw.ALL_PROVED)
    assert set(sw.PENDANT_PROVED) == set(PENDANT_NAMES)


def test_lemma_p_on_random_tiny_graphs():
    """`pathwidth_ge_of_pendant_cliques`: `t + ⌈q/2⌉ − 2 ≤ pw` for every clique `R` and
    every family of pendant cliques, against the exact subset DP."""
    rng = np.random.default_rng(1301)
    checked = tight = above = 0
    for _ in range(150):
        n = int(rng.integers(2, 8))
        g = nx.gnp_random_graph(n, float(rng.uniform(0.3, 0.9)), seed=int(rng.integers(1 << 30)))
        if g.number_of_edges() == 0:
            continue
        pw = _exact_pw(g)
        omega = max(len(c) for c in nx.find_cliques(g))
        val = _lemma_p_exhaustive(g)
        assert val <= pw
        checked += 1
        tight += val == pw
        above += val > omega - 1
    assert checked >= 100 and tight >= checked // 2


def test_graph_evaluation_is_valid_and_never_below_the_clique_floor():
    """`pendant_graph_bound`: a subset of the lemma's choices, so at most the exhaustive
    value, at most the pathwidth, and never below `ω − 1`; `pendant_candidate` reports it
    in optimum units through the harness interface."""
    from learning.bound_harness import Budget
    rng = np.random.default_rng(1302)
    for _ in range(120):
        n = int(rng.integers(2, 8))
        g = nx.gnp_random_graph(n, float(rng.uniform(0.3, 0.9)), seed=int(rng.integers(1 << 30)))
        if g.number_of_edges() == 0:
            continue
        val, info = pendant_graph_bound(g)
        omega = max(len(c) for c in nx.find_cliques(g))
        assert omega - 1 <= val <= _lemma_p_exhaustive(g) <= _exact_pw(g)
        assert info["omega"] == omega and not info["censored"]
        cand, extra = pendant_candidate(g, None, Budget(seconds=5.0))
        assert cand == val + 1 and extra["censored_eval"] is False


def test_depth_one_family_is_exact_both_ways():
    """F2 (on paper, §6 of the phase diagram): `K_s` with a pendant `K_t` at `q` of its
    vertices has pathwidth `max(s − 1, t + ⌈q/2⌉ − 2)`; the lower half is
    `pathwidth_ge_of_pendant_cliques` (with `t = q = s`,
    `pathwidth_ge_of_clique_pendant_cliques`: `⌈3s/2⌉ − 2`), and the graph evaluation
    attains it."""
    for s in range(2, 6):
        for t in range(2, 6):
            for q in range(1, s + 1):
                g = _clique_with_pendants(s, t, q)
                if g.number_of_nodes() > 13:
                    continue
                want = max(s - 1, t + (q + 1) // 2 - 2)
                assert _exact_pw(g) == want
                val, _ = pendant_graph_bound(g)
                assert val == want
    for s in range(2, 5):
        assert pendant_graph_bound(_clique_with_pendants(s, s, s))[0] == s + (s + 1) // 2 - 2


def test_mosp_form_on_tiny_instances():
    """`mospValue_ge_of_pendant_patterns`: the pattern evaluation of Lemma P
    (`pendant_lower_bound`, pathwidth units) plus one never exceeds the MOSP value, by
    brute force over pattern orders."""
    rng = np.random.default_rng(1303)
    checked = above = 0
    for _ in range(80):
        n = int(rng.integers(2, 8))
        m = int(rng.integers(1, 6))
        pats = [sorted(rng.choice(n, size=int(rng.integers(1, min(4, n) + 1)), replace=False).tolist())
                for _ in range(m)]
        value = pendant_lower_bound(pats) + 1
        mosp = _brute_mosp(n, pats)
        assert value <= mosp
        checked += 1
        above += value > max(len(p) for p in pats)
    assert checked == 80


def test_censoring_is_reported_and_still_valid():
    """With the caps set absurdly low the evaluation says so and stays a valid bound."""
    g = _clique_with_pendants(4, 4, 4)
    val, info = pendant_graph_bound(g, max_r=1, max_q=2, max_cliques=3)
    assert info["censored"] and val <= _exact_pw(g)
