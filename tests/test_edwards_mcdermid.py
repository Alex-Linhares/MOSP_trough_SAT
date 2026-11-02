"""loop0012 item 01: `learning.edwards_mcdermid` — the weights `g_{1/6}`, `g'`,
the series-parallel reduction on bit masks, and the terms of Edwards &
McDermid (2015) Corollary 5.2 and Theorem 5.3. The paper's table (p. 7) to
`d = 8` exactly; properties 3, 4, 6 and the closed form (Lemma 8.1) to
`n = 30`; `reduce` on a tree, a cycle, `K_4`, a subdivided `K_4`; no degree
rises under reduction and `main_term ≤ histogram_term` on 200 random graphs.
"""
from __future__ import annotations

import random
from fractions import Fraction as F

import networkx as nx
import pytest

from learning.edwards_mcdermid import (
    alternating_factorial, average_degree, average_degree_term, components, degrees,
    edge_count, fminus, fomin_hoie_budget, fomin_hoie_n_eps, from_edges, from_networkx,
    g, g_closed_form, g_prime, g_real, histogram_term, is_cubic, is_reduced, main_term,
    poisson_value, reduce,
)

PAPER_TABLE = {2: F(0), 3: F(1, 6), 4: F(1, 3), 5: F(13, 30), 6: F(23, 45),
               7: F(359, 630), 8: F(1553, 2520)}


def test_table_matches_the_paper_to_d8():
    for d, val in PAPER_TABLE.items():
        assert g(d) == val
    assert g(0) == g(1) == g(2) == 0


def test_recurrence_and_alternating_factorial():
    for n in range(4, 31):
        assert n * g(n) == (n - 2) * g(n - 1) + g(n - 2) + 1
    assert [alternating_factorial(k) for k in range(1, 6)] == [1, 1, 5, 19, 101]
    for n in range(2, 31):
        assert alternating_factorial(n) + alternating_factorial(n - 1) == __import__("math").factorial(n)


def test_closed_form_lemma_8_1_to_30():
    for n in range(2, 31):
        assert g_closed_form(n) == g(n)


def test_property_3_non_decreasing_to_30():
    for n in range(2, 31):
        assert g(n + 1) >= g(n)


def test_property_4_increments_non_increasing_to_30():
    assert g_prime(3) == g_prime(4) == F(1, 6)
    for n in range(3, 31):
        assert g_prime(n + 1) <= g_prime(n)
    for n in range(0, 3):
        assert g_prime(n) == 0


def test_property_5_g_over_n_decreasing_from_5():
    for n in range(5, 31):
        assert g(n + 1) / (n + 1) < g(n) / n


def test_property_6_rearrangement_to_30():
    for n in range(4, 31):
        assert 1 - g(n) == (n - 1) * g_prime(n) + g_prime(n - 1)


def test_g_real_interpolates_and_is_zero_below_2():
    assert g_real(F(7, 2)) == (g(3) + g(4)) / 2
    assert g_real(F(3)) == g(3)
    assert g_real(F(1, 2)) == 0 and g_real(2) == 0
    assert g_real(F(5, 2)) == g(3) / 2


def test_g_sandwich_of_lemma_8_3_and_8_4():
    for n in range(3, 31):
        assert g(n - 1) <= g(n) <= (1 + g(n - 1)) / 2
    for n in range(4, 31):
        assert g_prime(n - 1) >= g_prime(n) >= g_prime(n - 1) / 3


def test_reduce_tree_is_empty():
    T = nx.random_labeled_tree(40, seed=1) if hasattr(nx, "random_labeled_tree") else nx.random_tree(40, seed=1)
    adj = from_networkx(T)
    radj, removed = reduce(adj)
    assert removed == (1 << 40) - 1
    assert all(a == 0 for a in radj)
    assert main_term(adj) == 0


def test_reduce_cycle_leaves_a_triangle_then_empties():
    # operation 3 shrinks a cycle until three vertices remain; then operation 4
    # deletes one of them (adjacent neighbours), and the remaining edge goes by
    # operation 2 and 1: the cycle is series-parallel, r(C_n) is empty.
    adj = from_networkx(nx.cycle_graph(9))
    radj, removed = reduce(adj)
    assert all(a == 0 for a in radj) and removed == (1 << 9) - 1


def test_reduce_k4_is_fixed():
    adj = from_networkx(nx.complete_graph(4))
    radj, removed = reduce(adj)
    assert radj == adj and removed == 0
    assert main_term(adj) == 4 * g(3) == F(2, 3)
    assert fminus(adj) == F(2, 3) - g_prime(3) == F(1, 2)


def test_reduce_subdivided_k4_returns_to_k4():
    K = nx.complete_graph(4)
    S = nx.Graph()
    nxt = 4
    for a, b in K.edges():
        # subdivide every edge twice
        S.add_edge(a, nxt); S.add_edge(nxt, nxt + 1); S.add_edge(nxt + 1, b); nxt += 2
    adj = from_networkx(S)
    radj, removed = reduce(adj)
    surviving = [v for v in range(len(adj)) if not (removed >> v) & 1]
    assert sorted(surviving) == [0, 1, 2, 3]
    for v in range(4):
        assert radj[v] == (0b1111 & ~(1 << v))
    assert main_term(adj) == F(2, 3)
    # the unreduced histogram sum sees only the four branch vertices too
    assert histogram_term(adj) == F(2, 3)


def test_reduce_pendant_on_k4_and_triangle_hanging():
    G = nx.complete_graph(4)
    G.add_edge(0, 4); G.add_edge(4, 5); G.add_edge(5, 0)   # a triangle hanging on vertex 0
    G.add_edge(1, 6)                                        # a pendant
    adj = from_networkx(G)
    radj, removed = reduce(adj)
    assert removed == (1 << 4) | (1 << 5) | (1 << 6)
    assert is_reduced(radj) and is_cubic(radj, 0b1111)


def _random_graphs(count: int = 200, seed: int = 7):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        n = rng.randint(5, 40)
        p = rng.choice([0.05, 0.1, 0.2, 0.35, 0.5])
        G = nx.gnp_random_graph(n, p, seed=rng.randint(0, 10 ** 9))
        out.append(from_networkx(G))
    return out


def test_reduce_never_raises_a_surviving_degree_and_is_reduced():
    for adj in _random_graphs():
        radj, removed = reduce(adj)
        assert is_reduced(radj)
        d0, d1 = degrees(adj), degrees(radj)
        for v in range(len(adj)):
            if (removed >> v) & 1:
                assert radj[v] == 0
            else:
                assert d1[v] <= d0[v]
                assert d1[v] >= 3
        # the reduced graph has no edge to a removed vertex
        for v in range(len(adj)):
            assert radj[v] & removed == 0


def test_main_term_at_most_histogram_term():
    for adj in _random_graphs():
        assert main_term(adj) <= histogram_term(adj)


def test_reduce_is_idempotent_and_order_independent():
    for adj in _random_graphs(60, seed=3):
        radj, removed = reduce(adj)
        radj2, removed2 = reduce(radj)
        assert radj2 == radj and removed2 == removed
        # relabel, reduce, relabel back: the same reduced graph (uniqueness, paper p. 8)
        n = len(adj)
        perm = list(range(n)); random.Random(n).shuffle(perm)
        inv = {perm[i]: i for i in range(n)}
        padj = [0] * n
        for v in range(n):
            for u in range(n):
                if (adj[v] >> u) & 1:
                    padj[perm[v]] |= 1 << perm[u]
        pr, prem = reduce(padj)
        back = [0] * n
        for v in range(n):
            for u in range(n):
                if (pr[v] >> u) & 1:
                    back[inv[v]] |= 1 << inv[u]
        assert back == radj


def test_components_and_fminus_additive():
    G = nx.disjoint_union(nx.complete_graph(4), nx.complete_graph(5))
    G.add_node(9)
    adj = from_networkx(G)
    comps = components(adj)
    assert len(comps) == 2
    assert fminus(adj) == (4 * g(3) - g_prime(3)) + (5 * g(4) - g_prime(4))
    assert fminus(adj) == fminus(from_networkx(nx.complete_graph(4))) + fminus(from_networkx(nx.complete_graph(5)))


def test_average_degree_term_and_cubic_value():
    adj = from_networkx(nx.petersen_graph())
    assert average_degree(adj) == 3 and average_degree_term(adj) == 10 * g(3)
    assert is_cubic(adj)
    assert main_term(adj) == F(10, 6)
    assert edge_count(adj) == 15


def test_poisson_value_matches_the_planner_to_four_places():
    assert abs(poisson_value(3) - 0.1826) < 5e-4
    assert abs(poisson_value(6) - 0.4575) < 5e-4
    assert abs(poisson_value(10) - 0.6558) < 5e-4
    assert poisson_value(0) == 0
    # Jensen: concave g on the integers puts the Poisson mean below g(c) when c ≥ 3
    assert poisson_value(6) < float(g(6))


def test_fomin_hoie_budget_is_explicit_and_vacuous_at_our_sizes():
    assert abs(fomin_hoie_n_eps(0.5) - 55.45) < 0.01
    assert abs(fomin_hoie_n_eps(0.1) - 18604.9) < 0.1
    for n in (16, 120, 2916):
        assert fomin_hoie_budget(n) > 0.17 * n  # exceeds n/6 itself
    assert fomin_hoie_budget(100000) < fomin_hoie_budget(2916) * 100000 / 2916


# ----------------------------------------------------------------------------
# item 02: the step relation, basic graphs, the paper's choice of w, Algorithm X
# (`reports/edwards_mcdermid.md` §2; every statement below was checked on every
# graph to 9 vertices by `reports/scratch/edwards_mcdermid/02_lemmas/check.py`)
# ----------------------------------------------------------------------------

from learning.edwards_mcdermid import (  # noqa: E402
    F_global, algorithm_x, f_potential, is_basic, isolate, isolate_set, paper_choice,
    pathwidth_induced, reduce_random, sp_step, step_vertices, support,
)


def _g6(line: str) -> list[int]:
    return from_networkx(nx.from_graph6_bytes(line.encode()))


def test_sp_step_four_operations():
    # operation 2: pendant vertex 4 on K4
    adj = from_edges(5, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3), (3, 4)])
    out = sp_step(adj, 4)
    assert out[4] == 0 and out[3] == adj[3] & ~(1 << 4) and edge_count(out) == 6
    # operation 3: suppress a degree-2 vertex with non-adjacent neighbours (path 0-1-2)
    adj = from_edges(3, [(0, 1), (1, 2)])
    out = sp_step(adj, 1)
    assert out == from_edges(3, [(0, 2)])
    # operation 4: degree-2 vertex on a triangle
    adj = from_edges(3, [(0, 1), (1, 2), (0, 2)])
    out = sp_step(adj, 1)
    assert out == from_edges(3, [(0, 2)])
    # no step at degree 0 or 3
    with pytest.raises(ValueError):
        sp_step(from_edges(2, []), 0)
    with pytest.raises(ValueError):
        sp_step(from_edges(4, [(0, 1), (0, 2), (0, 3)]), 0)
    assert step_vertices(from_edges(4, [(0, 1), (0, 2), (0, 3)])) == [1, 2, 3]


def test_every_step_removes_an_edge_and_raises_no_degree():
    rng = random.Random(2)
    for _ in range(300):
        n = rng.randint(2, 9)
        G = nx.gnp_random_graph(n, rng.random(), seed=rng.randint(0, 10 ** 6))
        adj = from_networkx(G)
        for v in step_vertices(adj):
            out = sp_step(adj, v)
            assert edge_count(out) <= edge_count(adj) - 1
            assert all(a.bit_count() <= b.bit_count() for a, b in zip(out, adj))
            assert f_potential(out) <= f_potential(adj)
            assert f_potential(adj) - f_potential(out) >= g(adj[v].bit_count())


def test_commutation_of_deletion_with_a_step():
    rng = random.Random(3)
    zero = one = 0
    for _ in range(300):
        n = rng.randint(2, 9)
        adj = from_networkx(nx.gnp_random_graph(n, rng.random(), seed=rng.randint(0, 10 ** 6)))
        for v in step_vertices(adj):
            H2 = sp_step(adj, v)
            for w in range(n):
                if w == v:
                    continue
                Hw, H2w = isolate(adj, w), isolate(H2, w)
                if H2w == Hw:
                    zero += 1
                else:
                    assert 1 <= Hw[v].bit_count() <= 2 and sp_step(Hw, v) == H2w
                    one += 1
    assert zero > 0 and one > 0


def test_reduct_is_order_independent_on_random_graphs():
    rng = random.Random(4)
    for _ in range(200):
        n = rng.randint(2, 10)
        adj = from_networkx(nx.gnp_random_graph(n, rng.random(), seed=rng.randint(0, 10 ** 6)))
        radj, _ = reduce(adj)
        for _ in range(10):
            assert reduce_random(adj, rng) == radj


def test_basic_graphs():
    k4 = from_edges(4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)])
    assert is_basic(k4)                       # cubic (and of the second kind)
    wheel = from_edges(5, [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (2, 3), (3, 4), (4, 1)])
    assert is_basic(wheel)                    # W_4 − hub is C_4, reduces to empty
    assert fminus(wheel) == F(5, 6)           # the floor on a non-cubic basic component
    petersen = from_networkx(nx.petersen_graph())
    assert is_basic(petersen) and fminus(petersen) == F(10, 6) - F(1, 6)
    # K_6 is not basic: not cubic, and K_6 − v = K_5 is reduced
    k6 = from_networkx(nx.complete_graph(6))
    assert not is_basic(k6)
    assert is_basic(from_edges(3, []))        # the empty graph


def test_paper_choice_tie_break_is_needed():
    # F]~vo (7 vertices): vertices 4 and 6 have maximum degree 5 with every
    # neighbour of degree 5; the paper's rule picks a maximum-degree vertex
    # with a degree-4 neighbour, and only those satisfy the step inequality.
    adj = _g6("F]~vo")
    maxs, chosen, Delta = paper_choice(adj)
    assert Delta == 5 and maxs == [0, 1, 2, 3, 4, 6] and chosen == [0, 1, 2, 3]
    assert not is_basic(adj)
    FG = F_global(adj)
    for w in maxs:
        Gs, _ = reduce(isolate(adj, w))
        holds = 1 + F_global(Gs) <= FG
        assert holds == (w in chosen)
        assert (1 + fminus(Gs) <= fminus(adj)) == (w in chosen)


def test_algorithm_x_theorem_3_2_on_random_reduced_graphs():
    rng = random.Random(5)
    seen = 0
    for _ in range(400):
        n = rng.randint(4, 10)
        adj = from_networkx(nx.gnp_random_graph(n, rng.uniform(0.5, 1.0), seed=rng.randint(0, 10 ** 6)))
        adj, _ = reduce(adj)
        if not any(adj):
            continue
        seen += 1
        X, B = algorithm_x(adj, rng)
        assert any(B) and is_reduced(B) and is_basic(B)
        assert X & ~support(adj) == 0
        assert X.bit_count() + fminus(B) <= fminus(adj)
        direct, _ = reduce(isolate_set(adj, X))
        assert direct == B
    assert seen > 100


def test_pathwidth_induced_agrees_with_the_project_solver():
    from fixed_parameter_algorithm.pathwidth import compute_pathwidth
    rng = random.Random(6)
    for _ in range(60):
        n = rng.randint(1, 9)
        G = nx.gnp_random_graph(n, rng.random(), seed=rng.randint(0, 10 ** 6))
        adj = from_networkx(G)
        assert pathwidth_induced(adj, (1 << n) - 1) == compute_pathwidth(G)[0]
        S = rng.randrange(1, 1 << n)
        sub = G.subgraph([v for v in range(n) if (S >> v) & 1])
        assert pathwidth_induced(adj, S) == compute_pathwidth(nx.convert_node_labels_to_integers(sub))[0]


def test_cut_lemma_separator_form_on_random_graphs():
    rng = random.Random(7)
    for _ in range(150):
        n = rng.randint(2, 8)
        adj = from_networkx(nx.gnp_random_graph(n, rng.random(), seed=rng.randint(0, 10 ** 6)))
        full = (1 << n) - 1
        pw = pathwidth_induced(adj, full)
        for _ in range(8):
            V1 = rng.randrange(0, 1 << n)
            V2 = full & ~V1
            b1 = sum(1 for v in range(n) if (V1 >> v) & 1 and adj[v] & V2)
            b2 = sum(1 for v in range(n) if (V2 >> v) & 1 and adj[v] & V1)
            p1, p2 = pathwidth_induced(adj, V1), pathwidth_induced(adj, V2)
            assert pw <= max(p1, p2) + min(b1, b2)                      # C1s
            assert pw <= max(p1 + b1, p2 + b2, b1 + b2 - 1)             # C1


# ---------------------------------------------------------------------------
# item 03: `lean/MOSPFormalization/DegreeBound/Weights.lean` against the Python
# ---------------------------------------------------------------------------

import re  # noqa: E402
from pathlib import Path  # noqa: E402

WEIGHTS_LEAN = Path(__file__).resolve().parents[1] / "lean" / "MOSPFormalization" / \
    "DegreeBound" / "Weights.lean"


def test_weights_lean_transcription_agrees_to_200():
    """`g` as `Weights.lean` defines it (transcribed in `learning.sandwich.g_lean`) equals
    the Python `g` to `n = 200` in exact rationals, and so do `g'` and the closed form."""
    import learning.sandwich as sw
    for n in range(201):
        assert sw.g_lean(n) == g(n), n
        assert sw.g_prime_lean(n) == g_prime(n), n
    for n in range(2, 60):
        assert sw.alt_factorial_lean(n) == alternating_factorial(n), n


def test_degree_bound_stage_has_no_violation():
    import learning.sandwich as sw
    frame = sw.degree_bound_check(60)
    assert (frame.checked == frame.holds).all(), frame[frame.checked != frame.holds]
    assert len(frame) == 22
    item05 = frame[frame.Lean.isin(["potentialMinus", "potentialMinus_eq_sum_vertexTerm",
                                    "potentialMinus_add"])]
    assert len(item05) == 3 and (item05.checked == 500).all()


def test_degree_bound_proved_names_are_theorems_in_the_lean_file():
    """Every name `learning.sandwich` audits for `Weights.lean` is declared there as a
    theorem; the file has no `sorry` and no `axiom`; the root module imports it; and
    `paper1/axiom_check.lean` prints the axioms of every one."""
    import learning.sandwich as sw
    src = WEIGHTS_LEAN.read_text()
    declared = set(re.findall(r"^(?:@\[simp\] )?theorem\s+([^\s:({\[]+)", src, re.M))
    missing = [n for n in sw.DEGREE_BOUND_PROVED if n.split(".")[-1] not in declared]
    assert not missing, missing
    assert all(n.startswith("DegreeBound.") for n in sw.DEGREE_BOUND_PROVED)
    assert set(sw.DEGREE_BOUND_PROVED) <= set(sw.ALL_PROVED)
    code = re.sub(r"/-.*?-/", "", src, flags=re.S)
    code = re.sub(r"--.*", "", code)
    assert "sorry" not in code
    assert not re.search(r"^\s*axiom\b", code, re.M)
    root = (WEIGHTS_LEAN.parents[2] / "MOSPFormalization.lean").read_text()
    assert "import MOSPFormalization.DegreeBound.Weights\n" in root
    axioms = (WEIGHTS_LEAN.parents[3] / "paper1" / "axiom_check.lean").read_text()
    for n in sw.DEGREE_BOUND_PROVED:
        assert f"#print axioms MOSPFormalization.{n}\n" in axioms, n
    for n in ("g_recurrence", "g_monotone", "g'_antitone_of_three_le", "one_sub_g_eq",
              "g_closed_form", "g_div_lt_g_div"):
        assert f"DegreeBound.{n}" in sw.DEGREE_BOUND_PROVED


# ---------------------------------------------------------------------------
# item 04: the cut lemma helpers and `lean/MOSPFormalization/DegreeBound/CutLemma.lean`
# ---------------------------------------------------------------------------

from learning.edwards_mcdermid import (  # noqa: E402
    bisection_bound, boundary_to, parse_g6, pathwidth_induced, separator_cut_bound,
)

CUT_LEMMA_LEAN = WEIGHTS_LEAN.parent / "CutLemma.lean"


def test_parse_g6_and_boundary_to():
    n, adj = parse_g6("F]~vo")           # the item-02 tie-break graph, 7 vertices
    assert n == 7 and sum(a.bit_count() for a in adj) % 2 == 0
    assert all(not (adj[v] >> v) & 1 for v in range(n))
    assert all(((adj[u] >> v) & 1) == ((adj[v] >> u) & 1) for u in range(n) for v in range(n))
    A, B = 0b0001111, 0b1110000
    bd = boundary_to(adj, A, B)
    assert bd & ~A == 0
    assert all(bool(adj[a] & B) == bool((bd >> a) & 1) for a in range(4))
    assert boundary_to(adj, A, 0) == 0


def test_relative_cut_lemma_and_bisection_on_random_graphs():
    """C1s in its relative form (disjoint `S1`, `S2` not covering `V`), the relative
    deletion lemma for every pair `(T, U)`, and the `BisectionTree` bound at depth 2
    and 3 — the forms `CutLemma.lean` proves — on random graphs to 9 vertices."""
    rng = random.Random(11)
    for _ in range(60):
        n = rng.randint(2, 9)
        adj = from_networkx(nx.gnp_random_graph(n, rng.random(), seed=rng.randint(0, 10 ** 6)))
        full = (1 << n) - 1
        cache: dict[int, int] = {}

        def pw_of(S: int) -> int:
            if S not in cache:
                cache[S] = pathwidth_induced(adj, S)
            return cache[S]

        for _ in range(12):
            S1 = rng.randrange(0, 1 << n)
            S2 = rng.randrange(0, 1 << n) & ~S1
            assert pw_of(S1 | S2) <= separator_cut_bound(adj, S1, S2, pw_of)       # C1s relative
            T, U = rng.randrange(0, 1 << n), rng.randrange(0, 1 << n)
            assert pw_of(U) <= pw_of(T) + (U & ~T).bit_count()                     # deletion, any T, U
            if T & ~U == 0:
                assert pw_of(T) <= pw_of(U)                                         # monotonicity
        verts = list(range(n))

        def tree(vs: list[int], depth: int):
            if depth == 0 or len(vs) <= 1:
                m = 0
                for v in vs:
                    m |= 1 << v
                return m
            rng.shuffle(vs)
            h = len(vs) // 2
            return (tree(vs[:h], depth - 1), tree(vs[h:], depth - 1))

        for depth in (2, 3):
            t = tree(list(verts), depth)
            k, bs = bisection_bound(adj, t, pw_of)
            assert pw_of(full) <= k + sum(bs)                                       # C2s
            km, bsm = bisection_bound(adj, t, pw_of, use_max=True)
            assert k + sum(bs) <= km + sum(bsm) <= km + 2 * sum(bsm)
            assert pw_of(full) <= km + 2 * sum(bsm)                                 # C2 (item's form)


def test_cut_lemma_proved_names_are_theorems_in_the_lean_file():
    """Every name `learning.sandwich` audits for `CutLemma.lean` is declared there; the
    file has no `sorry` and no `axiom`; the root module imports it; and
    `paper1/axiom_check.lean` prints the axioms of every one."""
    import learning.sandwich as sw
    src = CUT_LEMMA_LEAN.read_text()
    declared = set(re.findall(r"^(?:@\[simp\] )?theorem\s+([^\s:({\[]+)", src, re.M))
    assert set(sw.CUT_LEMMA_PROVED) == declared, set(sw.CUT_LEMMA_PROVED) ^ declared
    assert set(sw.CUT_LEMMA_PROVED) <= set(sw.ALL_PROVED)
    code = re.sub(r"/-.*?-/", "", src, flags=re.S)
    code = re.sub(r"--.*", "", code)
    assert "sorry" not in code
    assert not re.search(r"^\s*axiom\b", code, re.M)
    root = (CUT_LEMMA_LEAN.parents[2] / "MOSPFormalization.lean").read_text()
    assert "import MOSPFormalization.DegreeBound.CutLemma\n" in root
    axioms = (CUT_LEMMA_LEAN.parents[3] / "paper1" / "axiom_check.lean").read_text()
    for n in sw.CUT_LEMMA_PROVED:
        assert f"#print axioms MOSPFormalization.{n}\n" in axioms, n
    for n in ("pathwidth_le_max_add_min_boundary", "pathwidth_le_cut",
              "pathwidth_le_of_bisectionTree", "pathwidth_le_of_bisectionTreeMax_two_mul"):
        assert n in sw.CUT_LEMMA_PROVED


# ----------------------------------------------------------------------------
# item 05: `lean/MOSPFormalization/DegreeBound/Potential.lean`
# ----------------------------------------------------------------------------

POTENTIAL_LEAN = WEIGHTS_LEAN.parent / "Potential.lean"


def test_potential_minus_lean_transcription_agrees_with_fminus():
    """The Lean `potentialMinus` (transcribed) equals the Python `fminus` and its per-vertex
    form on random graphs with isolated vertices; additivity holds on disjoint unions."""
    import random
    import learning.sandwich as sw
    from learning.edwards_mcdermid import fminus, support
    rng = random.Random(505)
    for _ in range(200):
        n = rng.randint(1, 11)
        adj = sw._random_graph_with_isolated(rng, n)
        assert sw.potential_minus_lean(adj) == fminus(adj)
        assert sw.potential_minus_lean(adj) == sw.vertex_term_sum_lean(adj)
        # a disjoint union with a second random graph on the complementary vertices
        s = support(adj)
        rest = [v for v in range(n) if not (s >> v) & 1]
        g2 = [0] * n
        for i, u in enumerate(rest):
            for v in rest[i + 1:]:
                if rng.random() < 0.6:
                    g2[u] |= 1 << v
                    g2[v] |= 1 << u
        union = [a | b for a, b in zip(adj, g2)]
        assert sw.potential_minus_lean(union) == sw.potential_minus_lean(adj) + sw.potential_minus_lean(g2)


def test_potential_proved_names_are_theorems_in_the_lean_file():
    """Every name `learning.sandwich` audits for `Potential.lean` is declared there as a
    theorem; the file has no `sorry` and no `axiom`; the root module imports it; and
    `paper1/axiom_check.lean` prints the axioms of every one."""
    import learning.sandwich as sw
    src = POTENTIAL_LEAN.read_text()
    declared = set(re.findall(r"^(?:@\[simp\] )?theorem\s+([^\s:({\[]+)", src, re.M))
    missing = [n for n in sw.POTENTIAL_PROVED if n.split(".")[-1] not in declared]
    assert not missing, missing
    assert all(n.startswith("DegreeBound.") for n in sw.POTENTIAL_PROVED)
    assert set(sw.POTENTIAL_PROVED) <= set(sw.ALL_PROVED)
    assert len(sw.POTENTIAL_PROVED) == len(declared) == 54
    code = re.sub(r"/-.*?-/", "", src, flags=re.S)
    code = re.sub(r"--.*", "", code)
    assert "sorry" not in code
    assert not re.search(r"^\s*axiom\b", code, re.M)
    root = (POTENTIAL_LEAN.parents[2] / "MOSPFormalization.lean").read_text()
    assert "import MOSPFormalization.DegreeBound.Potential\n" in root
    axioms = (POTENTIAL_LEAN.parents[3] / "paper1" / "axiom_check.lean").read_text()
    for n in sw.POTENTIAL_PROVED:
        assert f"#print axioms MOSPFormalization.{n}\n" in axioms, n
    for n in ("degree_isolate", "potential_isolate", "potential_isolate_le_sub_one",
              "potential_isolate_regular", "potentialMinus_le_potential",
              "potentialMinus_eq_sum_compPotential", "compPotential_nonneg",
              "potentialMinus_eq_sum_vertexTerm", "potentialMinus_le_F",
              "potentialMinus_eq_F_of_connected", "potentialMinus_add",
              "potentialMinus_cubic", "potentialMinus_ge_five_sixths"):
        assert f"DegreeBound.{n}" in sw.POTENTIAL_PROVED


# ----------------------------------------------------------------------------
# item 06: `lean/MOSPFormalization/DegreeBound/SPReduction.lean` — the reduction system
# ----------------------------------------------------------------------------

SP_REDUCTION_LEAN = WEIGHTS_LEAN.parent / "SPReduction.lean"


def _step_kind(adj, v):
    nb = adj[v]
    if nb.bit_count() == 1:
        return "pendant"
    x = (nb & -nb).bit_length() - 1
    y = (nb ^ (nb & -nb)).bit_length() - 1
    return "triangle" if (adj[x] >> y) & 1 else "suppress"


def test_commutation_lemma_in_the_lean_form_on_random_graphs():
    """R3 as `SPStep.isolate_comm` proves it: for a step at `v` and `w ≠ v`, either
    `H − w = G − w` (then `v` was pendant at `w`) or one step at `v` in `G − w` reaches
    `H − w`, pendant if `w ∈ N(v)` and of the original kind otherwise; R3X for a random
    finset `X ∌ v`; R4 along a random maximal reduction with `X ⊆ supp H`; R5 with a
    graph `K` supported away from `G`; a vertex of degree 1 or 2 admits a step (the
    witness of `exists_spStep_of_ndeg`)."""
    import random
    from learning.edwards_mcdermid import (bits, isolate, isolate_set, sp_step, step_vertices,
                                          support)
    rng = random.Random(606)
    triples = 0
    for _ in range(300):
        n = rng.randint(2, 11)
        p = rng.choice([0.15, 0.3, 0.5])
        adj = [0] * n
        for a in range(n):
            for b in range(a + 1, n):
                if rng.random() < p:
                    adj[a] |= 1 << b
                    adj[b] |= 1 << a
        for v in step_vertices(adj):
            H = sp_step(adj, v)
            kind = _step_kind(adj, v)
            assert H[v] == 0 and sum(h.bit_count() for h in H) < sum(a.bit_count() for a in adj)
            assert all(H[u].bit_count() <= adj[u].bit_count() for u in range(n))
            for w in range(n):
                if w == v:
                    continue
                triples += 1
                Gw, Hw = isolate(adj, w), isolate(H, w)
                if Hw == Gw:
                    assert kind == "pendant" and (adj[v] >> w) & 1
                    continue
                assert 1 <= Gw[v].bit_count() <= 2 and sp_step(Gw, v) == Hw
                assert _step_kind(Gw, v) == ("pendant" if (adj[v] >> w) & 1 else kind)
            X = sum(1 << u for u in range(n) if u != v and rng.random() < 0.4)
            GX, HX = isolate_set(adj, X), isolate_set(H, X)
            assert HX == GX or (1 <= GX[v].bit_count() <= 2 and sp_step(GX, v) == HX)
            s = support(adj)
            rest = [u for u in range(n) if not (s >> u) & 1]
            K = [0] * n
            for i, a in enumerate(rest):
                for b in rest[i + 1:]:
                    if rng.random() < 0.6:
                        K[a] |= 1 << b
                        K[b] |= 1 << a
            GK = [a | k for a, k in zip(adj, K)]
            assert sp_step(GK, v) == [h | k for h, k in zip(H, K)]
        # R4 along a random maximal reduction
        seq, cur = [], list(adj)
        while step_vertices(cur):
            v = rng.choice(step_vertices(cur))
            seq.append(v)
            cur = sp_step(cur, v)
        assert all(cur[v] == 0 for v in seq)
        X = sum(1 << u for u in bits(support(cur)) if rng.random() < 0.5)
        g_cur = isolate_set(adj, X)
        for v in seq:
            assert not (X >> v) & 1
            if 1 <= g_cur[v].bit_count() <= 2:
                g_cur = sp_step(g_cur, v)
        assert g_cur == isolate_set(cur, X)
    assert triples > 1000


def test_item06_brute_force_log_has_no_violation():
    """The exhaustive check to 9 vertices (`06_reduction/check_r3.py`) was run and found
    nothing; its R3 counts are item 02's."""
    import json
    p = SP_REDUCTION_LEAN.parents[3] / "reports/scratch/edwards_mcdermid/06_reduction/summary.json"
    if not p.exists():
        pytest.skip("brute-force summary not present")
    s = json.loads(p.read_text())
    assert s["violations"] == 0
    assert s["total"]["R3"] == 3115987 and s["total"]["R3_zero"] == 95300
    assert s["total"]["R1"] == 393156


def test_sp_reduction_proved_names_are_theorems_in_the_lean_file():
    """Every name `learning.sandwich` audits for `SPReduction.lean` is declared there as a
    theorem (namespaces resolved); the file has no `sorry` and no `axiom`; the root module
    imports it; `paper1/axiom_check.lean` prints the axioms of every one; the statements
    the later items need are present."""
    import learning.sandwich as sw
    src = SP_REDUCTION_LEAN.read_text()
    code = re.sub(r"/-.*?-/", "", src, flags=re.S)
    ns, declared = [], set()
    for line in code.splitlines():
        m = re.match(r"^namespace\s+(\S+)", line)
        if m:
            ns.append(m.group(1))
            continue
        m = re.match(r"^end\s+(\S+)", line)
        if m:
            assert ns and ns[-1] == m.group(1)
            ns.pop()
            continue
        m = re.match(r"^theorem\s+([^\s:({\[]+)", line)
        if m:
            declared.add(".".join(ns[1:] + [m.group(1)]))
    assert set(sw.SP_REDUCTION_PROVED) == {"DegreeBound." + n for n in declared}
    assert len(sw.SP_REDUCTION_PROVED) == len(declared) == 69
    assert set(sw.SP_REDUCTION_PROVED) <= set(sw.ALL_PROVED)
    code = re.sub(r"--.*", "", code)
    assert "sorry" not in code
    assert not re.search(r"^\s*axiom\b", code, re.M)
    root = (SP_REDUCTION_LEAN.parents[2] / "MOSPFormalization.lean").read_text()
    assert "import MOSPFormalization.DegreeBound.SPReduction\n" in root
    axioms = (SP_REDUCTION_LEAN.parents[3] / "paper1" / "axiom_check.lean").read_text()
    for n in sw.SP_REDUCTION_PROVED:
        assert f"#print axioms MOSPFormalization.{n}\n" in axioms, n
    for n in ("SPStep.degSum_lt", "exists_reduced_reduct", "SPStep.ndeg_le",
              "SPReduces.ndeg_le", "SPReduces.degree_le", "SPReduces.potential_le",
              "SPReduces.potential_sub_ge_of_isolated", "SPStep.isolate_comm",
              "SPStep.isolateSet_comm", "SPReduces.isolateSet_comm", "SPReduces.isolate_comm",
              "SPStep.sup_of_disjoint", "SPReduces.sup_of_disjoint",
              "IsSPReduced.eq_of_spReduces", "isSPReduced_iff"):
        assert f"DegreeBound.{n}" in sw.SP_REDUCTION_PROVED
    # the four constructors of the step and the three definitions
    for s in ("inductive SPStep", "| pendant", "| suppress", "| triangle", "def SPReduces",
              "def IsSPReduced", "def IsBasic"):
        assert s in src


# ----------------------------------------------------------------------------
# item 07: `lean/MOSPFormalization/DegreeBound/Step.lean` — the step inequality
# ----------------------------------------------------------------------------

STEP_LEAN = WEIGHTS_LEAN.parent / "Step.lean"


def _random_connected_min3(rng, n):
    """A random connected graph on `n` vertices with every degree ≥ 3 (rejection)."""
    from learning.edwards_mcdermid import components, degrees
    while True:
        adj = [0] * n
        p = rng.choice([0.45, 0.6, 0.75])
        for a in range(n):
            for b in range(a + 1, n):
                if rng.random() < p:
                    adj[a] |= 1 << b
                    adj[b] |= 1 << a
        if len(components(adj)) == 1 and min(degrees(adj)) >= 3:
            return adj


def test_step_inequality_in_the_lean_form_on_random_graphs():
    """S1 as `Step.lean` proves it: for a connected non-basic graph of minimum degree 3 and
    every two-key `w`, `Δ ≥ 4`, `G*` non-empty, the unsorted SJ identity, `j₄ ≥ g'(d)` for
    every `d = deg_{G'} v` (no `d ≥ 3` needed), the neighbour-sum bound, the regular-case
    propagation (`degree_eq_of_reachable`), and `1 + F(G*) ≤ F(G)`, `1 + f⁻(G*) ≤ f⁻(G)`.
    Also `minNbrDeg`'s two-key choice is realised (`exists_paper_choice`)."""
    import random
    from fractions import Fraction
    from learning.edwards_mcdermid import (F_global, bits, degrees, f_potential, fminus,
                                          g_prime, global_min_degree, is_basic, isolate,
                                          paper_choice, reduce)
    rng = random.Random(707)
    pairs = 0
    for _ in range(150):
        n = rng.randint(5, 10)
        adj = _random_connected_min3(rng, n)
        if is_basic(adj):
            continue
        deg = degrees(adj)
        maxs, chosen, D = paper_choice(adj)
        assert D >= 4 and chosen and set(chosen) <= set(maxs)
        key = {v: min(deg[u] for u in bits(adj[v])) for v in maxs}
        assert all(key[w] == min(key.values()) for w in chosen)
        for w in chosen:
            pairs += 1
            Gp = isolate(adj, w)
            dp = degrees(Gp)
            Gs, _ = reduce(Gp)
            assert any(Gs), "G* empty though G is not basic"
            S = sum((g_prime(deg[v]) for v in bits(adj[w])), Fraction(0))
            assert 1 + f_potential(Gp) == f_potential(adj) + (D - 1) * g_prime(D) + g_prime(D - 1) - S
            j4 = f_potential(Gp) - f_potential(Gs) + g_prime(global_min_degree(Gs))
            assert all(j4 >= g_prime(dp[v]) for v in range(n))
            assert all(S >= g_prime(deg[v0]) + (D - 1) * g_prime(D) for v0 in bits(adj[w]))
            if all(deg[v] == D for v in bits(adj[w])):
                assert all(deg[v] == D for v in range(n) if adj[v])
            assert 1 + f_potential(Gs) - g_prime(global_min_degree(Gs)) <= F_global(adj)
            assert 1 + fminus(Gs) <= fminus(adj)
    assert pairs >= 50


def test_item07_brute_force_log_has_no_violation():
    """The exhaustive check to 9 vertices (`07_step/check.py`) was run and found nothing;
    its (G, w) count is item 02's S1 count."""
    import json
    p = STEP_LEAN.parents[3] / "reports/scratch/edwards_mcdermid/07_step/summary.json"
    if not p.exists():
        pytest.skip("brute-force summary not present")
    s = json.loads(p.read_text())
    assert s["violations"] == 0
    assert s["total"]["pairs"] == 133055 and s["total"]["nonbasic"] == 82419
    assert s["total"]["case_R"] + s["total"]["case_A"] + s["total"]["case_B1"] + s["total"]["case_B2"] == s["total"]["triples"]


def test_step_proved_names_are_theorems_in_the_lean_file():
    """Every name `learning.sandwich` audits for `Step.lean` is declared there as a theorem
    (namespaces resolved); the file has no `sorry` and no `axiom`; the root module imports
    it; `paper1/axiom_check.lean` prints the axioms of every one; S1′ is not stated."""
    import learning.sandwich as sw
    src = STEP_LEAN.read_text()
    code = re.sub(r"/-.*?-/", "", src, flags=re.S)
    ns, declared = [], set()
    for line in code.splitlines():
        m = re.match(r"^namespace\s+(\S+)", line)
        if m:
            ns.append(m.group(1))
            continue
        m = re.match(r"^end\s+(\S+)", line)
        if m and ns and ns[-1] == m.group(1):
            ns.pop()
            continue
        m = re.match(r"^theorem\s+([^\s:({\[]+)", line)
        if m:
            declared.add(".".join(ns[1:] + [m.group(1)]))
    assert set(sw.STEP_PROVED) == {"DegreeBound." + n for n in declared}
    assert len(sw.STEP_PROVED) == len(declared) == 21
    assert set(sw.STEP_PROVED) <= set(sw.ALL_PROVED)
    code = re.sub(r"--.*", "", code)
    assert "sorry" not in code
    assert not re.search(r"^\s*axiom\b", code, re.M)
    root = (STEP_LEAN.parents[2] / "MOSPFormalization.lean").read_text()
    assert "import MOSPFormalization.DegreeBound.Step\n" in root
    axioms = (STEP_LEAN.parents[3] / "paper1" / "axiom_check.lean").read_text()
    for n in sw.STEP_PROVED:
        assert f"#print axioms MOSPFormalization.{n}\n" in axioms, n
    for n in ("exists_paper_choice", "four_le_degree_of_not_isBasic", "nonbasic_reduct_ne_bot",
              "one_add_potential_isolate", "j_identity", "j4_ge", "degree_eq_of_reachable",
              "one_add_F_le", "one_add_potentialMinus_le", "StepData.one_add_potentialMinus_le"):
        assert f"DegreeBound.{n}" in sw.STEP_PROVED
    assert "structure StepData" in src and "def minNbrDeg" in src
    # the two-key rule is a hypothesis of the theorem; S1′ (every maximum-degree w) is not stated
    assert "minNbrDeg G w ≤ minNbrDeg G u" in src


# ----------------------------------------------------------------------------
# item 08: Theorem 3.2, the reduction theorem (`DegreeBound/ReductionTheorem.lean`)
# ----------------------------------------------------------------------------

REDUCTION_THEOREM_LEAN = WEIGHTS_LEAN.parent / "ReductionTheorem.lean"


def _sp_reaches(G, H):
    """`SPReduces G H` decided by a search over step sequences (every step empties a vertex)."""
    from learning.edwards_mcdermid import sp_step, step_vertices
    target = tuple(H)
    seen = {tuple(G)}
    stack = [list(G)]
    while stack:
        cur = stack.pop()
        if tuple(cur) == target:
            return True
        for v in step_vertices(cur):
            nxt = sp_step(cur, v)
            if tuple(nxt) not in seen:
                seen.add(tuple(nxt))
                stack.append(nxt)
    return False


def _lean_recursion(adj, rng):
    """The induction of `exists_reduction_set_of_card`, replayed: basic → (∅, G); support
    disconnected → split off the component of a random support vertex, recurse on both
    halves, union; connected non-basic → the two-key `w`, a random reduct `G*` of `G − w`,
    recurse, insert `w`. Returns `(X, B)`."""
    from learning.edwards_mcdermid import (bits, components, is_basic, isolate, paper_choice,
                                          reduce_random, restrict, support)
    n = len(adj)
    supp = support(adj)
    if is_basic(adj):
        return 0, adj
    comps = components(adj)
    if len(comps) >= 2:
        u = rng.choice(list(bits(supp)))
        C = next(c for c in comps if (c >> u) & 1)
        X1, B1 = _lean_recursion(restrict(adj, C), rng)
        X2, B2 = _lean_recursion(restrict(adj, ((1 << n) - 1) & ~C), rng)
        return X1 | X2, [a | b for a, b in zip(B1, B2)]
    _, chosen, _ = paper_choice(adj)
    w = rng.choice(chosen)
    Xs, B = _lean_recursion(reduce_random(isolate(adj, w), rng), rng)
    return Xs | (1 << w), B


def test_reduction_theorem_in_the_lean_form_on_random_graphs():
    """T1 as `ReductionTheorem.lean` proves it, on random reduced graphs (including disjoint
    unions, so that the disconnected case fires): `X ⊆ supp G`, `G − X →* B` (by search),
    `B ≠ ⊥`, `B` reduced and basic, `|X| + f⁻(B) ≤ f⁻(G)`; and the two transfer lemmas, that
    "reduced" and "basic" pass to a union with disjoint supports and that `f⁻` adds."""
    import random
    from learning.edwards_mcdermid import fminus, is_basic, is_reduced, isolate_set, support
    rng = random.Random(808)
    done = disconnected = 0
    for _ in range(300):
        n1 = rng.randint(4, 7)
        a1 = _random_connected_min3(rng, n1)
        adj = a1
        if rng.random() < 0.5:
            n2 = rng.randint(4, 6)
            a2 = _random_connected_min3(rng, n2)
            adj = a1 + [0] * n2
            other = [0] * n1 + [a << n1 for a in a2]
            # SUP: reduced and basic pass to the union; f⁻ adds
            assert is_reduced([x | y for x, y in zip(adj, other)])
            if is_basic(adj) and is_basic(other):
                assert is_basic([x | y for x, y in zip(adj, other)])
            assert fminus([x | y for x, y in zip(adj, other)]) == fminus(adj) + fminus(other)
            adj = [x | y for x, y in zip(adj, other)]
            disconnected += 1
        assert is_reduced(adj) and any(adj)
        X, B = _lean_recursion(adj, rng)
        done += 1
        assert X & ~support(adj) == 0
        assert any(B) and is_reduced(B) and is_basic(B)
        assert X.bit_count() + fminus(B) <= fminus(adj)
        assert _sp_reaches(isolate_set(adj, X), B)
    assert done == 300 and disconnected >= 100


def test_item08_brute_force_log_has_no_violation():
    """The exhaustive check to 9 vertices (`08_reduction/check.py`) was run and found nothing;
    its T1 count is item 02's (89,972 reduced non-empty graphs), and the disconnected case of
    the induction fired on the random disjoint unions."""
    import json
    p = REDUCTION_THEOREM_LEAN.parents[3] / "reports/scratch/edwards_mcdermid/08_reduction/summary.json"
    if not p.exists():
        pytest.skip("brute-force summary not present")
    s = json.loads(p.read_text())
    assert s["violations"] == 0
    assert s["total"]["T1"] == 89972 and s["total"]["graphs"] == 288266
    assert s["total"]["CP_components"] == 290103
    assert s["pairs"]["union_case_disconnected"] >= 1000
    assert s["total"]["rec_calls"] == s["total"]["case_basic"] + s["total"]["case_disconnected"] + s["total"]["case_connected"]


def test_reduction_theorem_proved_names_are_theorems_in_the_lean_file():
    """Every name `learning.sandwich` audits for `ReductionTheorem.lean` is declared there as a
    theorem (namespaces resolved); the file has no `sorry` and no `axiom`; the root module
    imports it; `paper1/axiom_check.lean` prints the axioms of every one; T1 is stated with
    `IsSPReduced G` and `G ≠ ⊥` and no confluence hypothesis."""
    import learning.sandwich as sw
    src = REDUCTION_THEOREM_LEAN.read_text()
    code = re.sub(r"/-.*?-/", "", src, flags=re.S)
    ns, declared = [], set()
    for line in code.splitlines():
        m = re.match(r"^namespace\s+(\S+)", line)
        if m:
            ns.append(m.group(1))
            continue
        m = re.match(r"^end\s+(\S+)", line)
        if m and ns and ns[-1] == m.group(1):
            ns.pop()
            continue
        m = re.match(r"^theorem\s+([^\s:({\[]+)", line)
        if m:
            declared.add(".".join(ns[1:] + [m.group(1)]))
    assert set(sw.REDUCTION_THEOREM_PROVED) == {"DegreeBound." + n for n in declared}
    assert len(sw.REDUCTION_THEOREM_PROVED) == len(declared) == 41
    assert set(sw.REDUCTION_THEOREM_PROVED) <= set(sw.ALL_PROVED)
    code = re.sub(r"--.*", "", code)
    assert "sorry" not in code
    assert not re.search(r"^\s*axiom\b", code, re.M)
    root = (REDUCTION_THEOREM_LEAN.parents[2] / "MOSPFormalization.lean").read_text()
    assert "import MOSPFormalization.DegreeBound.ReductionTheorem\n" in root
    axioms = (REDUCTION_THEOREM_LEAN.parents[3] / "paper1" / "axiom_check.lean").read_text()
    for n in sw.REDUCTION_THEOREM_PROVED:
        assert f"#print axioms MOSPFormalization.{n}\n" in axioms, n
    for n in ("exists_reduction_set", "exists_reduction_set_and", "isReductionSet_insert",
              "isReductionSet_sup", "isBasic_sup", "isSPReduced_sup", "compPotential_cubic",
              "compPotential_ge_five_sixths", "isBasic_component"):
        assert f"DegreeBound.{n}" in sw.REDUCTION_THEOREM_PROVED
    assert "structure IsReductionSet" in src
    assert "(hG : IsSPReduced G)\n    (hne : G ≠ ⊥)" in src
    assert "Confluence" not in code and "hstep" not in code


# ---------------------------------------------------------------------------
# item 09: the pathwidth assembly, `lean/MOSPFormalization/DegreeBound/Pathwidth.lean`
# ---------------------------------------------------------------------------

import json  # noqa: E402
from fractions import Fraction  # noqa: E402

from learning.edwards_mcdermid import bits  # noqa: E402

PATHWIDTH_LEAN = WEIGHTS_LEAN.parent / "Pathwidth.lean"
ITEM09 = Path(__file__).resolve().parents[1] / "reports" / "scratch" / "edwards_mcdermid" / "09_assembly"


def _connected_in(adj, C):
    v = (C & -C).bit_length() - 1
    seen, frontier = 1 << v, 1 << v
    while frontier:
        nxt = 0
        for u in bits(frontier):
            nxt |= adj[u] & C
        nxt &= ~seen
        seen |= nxt
        frontier = nxt
    return seen == C


def test_pathwidth_assembly_lemmas_in_the_lean_form_on_random_graphs():
    """The deterministic statements of `Pathwidth.lean`, on 200 random graphs at 1–11
    vertices with isolated vertices: `pathwidth ⊥ = 0`; `pw(G) ≤ pw(G − X) + |X|` and
    `pw(G[Xᶜ]) ≤ pw(G − X)` for random `X`; `pw(G) ≤ pw(G − v) + 1`; a connected `C` lies in
    the component of any of its vertices and `pw(G[C]) ≤ pw(G[C₀])`; `pw(G[C₀]) ≤ pw(G|C₀)`;
    an edgeless `C` induces `⊥`; `pw(G) = max_C pw(G[C])`; for a reduced basic `B` and a
    non-trivial component `C₀`: cubic ⇒ `compPotential = |C₀|/6 − 1/6`, else some `u ∈ C₀`
    has `r(B|C₀ − u) = ∅` and `pw(B[C₀]) ≤ pw(B|C₀ − u) + 1`; and `compPotential ≤ f⁻`."""
    from learning.edwards_mcdermid import (components, fminus, g, g_prime, is_basic, is_reduced,
                                           isolate, isolate_set, min_degree, reduce, restrict,
                                           support)
    rng = random.Random(1109)
    seen_basic = 0
    for _ in range(200):
        n = rng.randint(1, 11)
        p = rng.choice([0.2, 0.4, 0.6, 0.9])
        adj = [0] * n
        for u in range(n):
            for v in range(u + 1, n):
                if rng.random() < p and rng.random() < 0.9:
                    adj[u] |= 1 << v
                    adj[v] |= 1 << u
        full = (1 << n) - 1
        assert pathwidth_induced([0] * n, full) == 0
        pw = pathwidth_induced(adj, full)
        X = rng.randrange(full + 1)
        GX = isolate_set(adj, X)
        assert pw <= pathwidth_induced(GX, full) + X.bit_count()
        assert pathwidth_induced(adj, full & ~X) <= pathwidth_induced(GX, full)
        v = rng.randrange(n)
        assert pw <= pathwidth_induced(isolate(adj, v), full) + 1
        comps = components(adj, support_only=False)
        assert pw == max(pathwidth_induced(adj, C) for C in comps)
        for C0 in comps:
            assert _connected_in(adj, C0)
            assert pathwidth_induced(adj, C0) <= pathwidth_induced(restrict(adj, C0), full)
        C = rng.randrange(1, full + 1)
        if _connected_in(adj, C):
            v = (C & -C).bit_length() - 1
            C0 = next(c for c in comps if (c >> v) & 1)
            assert C & ~C0 == 0
            assert pathwidth_induced(adj, C) <= pathwidth_induced(adj, C0)
            if all(adj[u] == 0 for u in bits(C)):
                assert C.bit_count() == 1 and pathwidth_induced(adj, C) == 0
        if is_reduced(adj) and support(adj) and is_basic(adj):
            seen_basic += 1
            fm = fminus(adj)
            for C0 in components(adj):
                cp = sum((g(adj[u].bit_count()) for u in bits(C0)), Fraction(0)) \
                    - g_prime(min_degree(adj, C0))
                assert cp <= fm
                sub = restrict(adj, C0)
                if all(adj[u].bit_count() == 3 for u in bits(C0)):
                    assert cp == Fraction(C0.bit_count(), 6) - Fraction(1, 6)
                else:
                    us = [u for u in bits(C0) if not any(reduce(isolate(sub, u))[0])]
                    assert us
                    assert all(pathwidth_induced(adj, C0) <= pathwidth_induced(isolate(sub, u), full) + 1
                               for u in us)
    assert seen_basic >= 3


def test_item09_brute_force_log_has_no_violation():
    """The exhaustive check of item 09 (`09_assembly/check.py`): every graph on 1–8 vertices,
    every vertex set `X` (IX) and every connected vertex set (CM), the pin on 500 random
    graphs at `n ≤ 12`, zero violations; the maxima measured (what the budgets must reach at
    these sizes) as recorded."""
    summary = json.loads((ITEM09 / "summary.json").read_text())
    assert summary["violations"] == 0
    tot = summary["total"]
    assert tot["graphs"] == 13598 and tot["FC"] == 13598 and tot["PB"] == 13598
    assert tot["IX"] == 3305498 and tot["CM"] == 2047623
    assert tot["BC_components"] == 622 and tot["BC_cubic"] == 18 and tot["BC_second"] == 604
    assert tot["A1"] == 2964
    assert summary["pin"]["ok"] == summary["pin"]["graphs"] == 500
    mx = summary["mx"]
    assert Fraction(mx["A1_pw_minus_fminus"]) == Fraction(17, 6)
    assert Fraction(mx["A2_pw_minus_fB"]) == 3 and Fraction(mx["rho_need_A2"]) == 3
    assert Fraction(mx["tau_need_cubic"]) == Fraction(17, 6)
    assert Fraction(mx["rho_need_second_min_u"]) == 3
    log = (ITEM09 / "check.log").read_text()
    assert log.rstrip().endswith("OK") and "violations: 0" in log


def test_pathwidth_assembly_proved_names_are_theorems_in_the_lean_file():
    """Every name `learning.sandwich` audits for `Pathwidth.lean` is declared there as a
    theorem (namespaces resolved); the file has no `sorry` and no `axiom`; the two hypotheses
    are `def … : Prop` and are never asserted (no `theorem` or `instance` proving them); the
    root module imports the file; `paper1/axiom_check.lean` prints the axioms of every
    theorem; the final theorems carry exactly the hypotheses the report's table lists."""
    import learning.sandwich as sw
    src = PATHWIDTH_LEAN.read_text()
    code = re.sub(r"/-.*?-/", "", src, flags=re.S)
    ns, declared, defs = [], set(), set()
    for line in code.splitlines():
        m = re.match(r"^namespace\s+(\S+)", line)
        if m:
            ns.append(m.group(1))
            continue
        m = re.match(r"^end\s+(\S+)", line)
        if m and ns and ns[-1] == m.group(1):
            ns.pop()
            continue
        m = re.match(r"^theorem\s+([^\s:({\[]+)", line)
        if m:
            declared.add(".".join(ns[1:] + [m.group(1)]))
        m = re.match(r"^def\s+([^\s:({\[]+)", line)
        if m:
            defs.add(m.group(1))
    assert set(sw.PATHWIDTH_ASSEMBLY_PROVED) == {"DegreeBound." + n for n in declared}
    assert len(sw.PATHWIDTH_ASSEMBLY_PROVED) == len(declared) == 21
    assert set(sw.PATHWIDTH_ASSEMBLY_PROVED) <= set(sw.ALL_PROVED)
    assert defs == {"CubicPathwidthBound", "ReductionPathwidthBound"}
    assert "def CubicPathwidthBound (τ : ℕ → ℚ) : Prop :=" in src
    assert "def ReductionPathwidthBound (ρ : ℕ → ℚ) : Prop :=" in src
    code = re.sub(r"--.*", "", code)
    assert "sorry" not in code
    assert not re.search(r"^\s*axiom\b", code, re.M)
    assert not re.search(r"^\s*instance\b", code, re.M)
    # the hypotheses are never concluded: no statement has them to the right of its last `:`
    for thm in re.findall(r"^theorem\s[\s\S]*?:= by", code, re.M):
        head = thm.split(":=")[0]
        conclusion = head.split(" :\n")[-1] if " :\n" in head else head.rsplit(":", 1)[-1]
        assert "CubicPathwidthBound" not in conclusion and \
            "ReductionPathwidthBound" not in conclusion, thm[:80]
    root = (PATHWIDTH_LEAN.parents[2] / "MOSPFormalization.lean").read_text()
    assert "import MOSPFormalization.DegreeBound.Pathwidth\n" in root
    axioms = (PATHWIDTH_LEAN.parents[3] / "paper1" / "axiom_check.lean").read_text()
    for n in sw.PATHWIDTH_ASSEMBLY_PROVED:
        assert f"#print axioms MOSPFormalization.{n}\n" in axioms, n
    for n in ("pathwidth_le_potentialMinus_of_hypotheses", "pathwidth_le_degreeSum_of_hypotheses",
              "pathwidth_le_histogram_of_hypotheses", "pathwidth_basic_le", "pathwidth_bot",
              "pathwidth_le_pathwidth_isolateSet_add_card"):
        assert f"DegreeBound.{n}" in sw.PATHWIDTH_ASSEMBLY_PROVED
    hyp = "(h1 : CubicPathwidthBound.{u} τ)\n    (h3 : ReductionPathwidthBound.{u} ρ) " \
          "(hτ : Monotone τ) (hτ0 : ∀ n, 0 ≤ τ n)"
    assert src.count(hyp) == 7
    assert "+ τ (Fintype.card V) + 2 * ρ (Fintype.card V) + 1" in src
    assert "+ τ (Fintype.card V) + 3 * ρ (Fintype.card V) + 1" in src
