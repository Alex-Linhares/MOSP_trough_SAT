"""Guards on `paper2.search_check` (loop0006 item 06).

The checker is only worth something if (a) its oracle is right, (b) its port
of the search is the code and not a paraphrase, and (c) it catches unsound
rules. So: the oracle against a literal minimum over closing orders; the port
against the C node for node; the fixed rules clean on every graph to 4
vertices; both known bad forms of `better_move` caught on their pinned
instances, each in the way `reports/better_move_bug.md` §7 describes; and a
planted fault (better move without its index order) caught on a 6-vertex
graph.
"""

import itertools

import pytest

import paper2.search_check as sc
from tests.test_customer_search import MINIMAL_10x13, MINIMAL_17x9


def _min_cost(masks):
    """Literal minimum over closing orders of max_i |N[S_i] - S_{i-1}|."""
    n = len(masks)
    best = None
    for order in itertools.permutations(range(n)):
        closed = opened = worst = 0
        for c in order:
            opened |= masks[c]
            worst = max(worst, (opened & ~closed).bit_count())
            closed |= 1 << c
        best = worst if best is None else min(best, worst)
    return best if n else 0


@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_the_oracle_is_the_minimum_over_closing_orders(n):
    for masks in sc.labelled_graphs(n):
        opt = _min_cost(masks)
        for k in range(n + 1):
            model = sc.Model(masks, k)
            assert model.sol(model.cl(0)) == (k >= opt)
            assert model.plain(0) == (k >= opt)


def test_every_rule_is_sound_on_every_graph_to_four_vertices():
    total = sc.empty_tally()
    for n in range(1, 5):
        for masks in sc.labelled_graphs(n):
            sc.merge(total, sc.check_graph(masks, seed=n))
    s = sc.summarise({"x": total})["x"]
    assert s["node_checks"] > 10_000 and s["tree_runs"] > 50_000 and s["lemma_f"] > 1_000
    assert s["fixed_rules_failures"] == 0 and s["lemma_f_fail"] == 0
    assert not any("fixed" in k for k in s["chain_fail"])


def test_the_port_is_the_c_node_for_node():
    pytest.importorskip("satisfiability.native")
    from satisfiability.native import native_available as available
    if not available():
        pytest.skip("C search not built")
    t = sc.empty_tally()
    for masks in list(sc.labelled_graphs(4))[::7] + [sc.masks_from_matrix(MINIMAL_10x13[0])]:
        sc.merge(t, sc.check_graph(masks, native=True, node_checks=False, pairs=False))
    assert t["native"] > 5_000
    assert sum(t["native_mismatch"].values()) == 0


def _bug_tally(matrix, k):
    masks = sc.masks_from_matrix(matrix)
    t = sc.check_graph(masks, q_sets=False, filters=sc.BUG_FILTERS, searches=sc.BUG_SEARCHES, ks=[k])
    return sc.summarise({"x": t})["x"]


def test_bug_a_fails_in_the_rule_itself_on_the_17x9():
    """The old close count: the rule's own conclusion fails, so it fails even alone."""
    s = _bug_tally(*MINIMAL_17x9)
    assert s["pair_fail"].get("better/old_close", 0) > 0
    assert "better/fixed" not in s["pair_fail"] and "better/fixed" not in s["link_fail"]
    assert s["node_fail"].get("better/L0/old_close", 0) > 0          # the rule alone
    assert s["tree_fail"].get("better/L0/old_close/old/memo", 0) == 1
    assert s["fixed_rules_failures"] == 0


def test_bug_b_is_a_cycle_of_true_premises_on_the_10x13():
    """The old order: every cited link is valid, yet the chain has no end and the node loses its solution."""
    s = _bug_tally(*MINIMAL_10x13)
    assert s["link_fail"] == {} and s["pair_fail"] == {}
    assert s["node_fail"].get("subset+better/L0/old_order", 0) > 0
    assert s["chain_fail"].get("subset+better/L0/old_order", 0) > 0
    # at the tree level this instance needs both bugs (reports/ml_nature.md §31)
    assert "subset+better/L0/old_order/old/memo" not in s["tree_fail"]
    assert s["tree_fail"].get("subset+better/L0/prefix/old/memo", 0) == 1
    assert s["fixed_rules_failures"] == 0


def test_the_covering_condition_sees_a_cycle_and_accepts_a_q_end():
    assert not sc.chains_end_in([(1, 2, "better"), (2, 1, "subset")], [(1, 0)], 0)
    assert sc.chains_end_in([(1, 2, "better"), (2, 0, "better")], [(1, 0)], 0)
    assert sc.chains_end_in([(1, 3, "subset")], [(1, 0)], 1 << 3)
    assert not sc.chains_end_in([(1, 3, "subset")], [(1, 0)], 0)


def test_the_subset_fallback_keeps_everything_when_all_would_go():
    # 0 and 1 are both dominated by customer 2, which is not a candidate
    opens = {0: 0b011, 1: 0b101, 2: 0b001}
    kept, links = sc.subset_pass([(2, 0), (2, 1)], [0, 1, 2], opens)
    assert kept == [(2, 0), (2, 1)] and links == []


def test_a_planted_unordered_better_move_is_caught(monkeypatch):
    """Better move letting *any* candidate cover (the Warwick 1730 cycle), with the
    C's keep-if-empty guard: the smallest failures are at 6 vertices."""
    def unordered(P, masks, full, closed, opened, k, limit, old_close=False):
        if len(P) <= 1:
            return list(P), []
        kept, links = [], []
        for item in P:
            r = item[1]
            cover = next((q for _, q in P if q != r and
                          sc.better_premise(masks, full, closed, opened, k, r, q, old_close)), None)
            if cover is None:
                kept.append(item)
            else:
                links.append((r, cover, "better"))
        return (kept, links) if kept else (list(P), [])

    cfg = dict(definite=False, subset=False, better=True, limit=0, variant="fixed")
    masks = [59, 59, 60, 15, 23, 39]
    clean = sc.check_graph(masks, q_sets=False, filters=[cfg], searches=[dict(cfg, old_move=False, memo=False)],
                           pairs=False)
    assert not clean["node_fail"] and not clean["tree_fail"]
    monkeypatch.setattr(sc, "better_pass", unordered)
    bad = sc.check_graph(masks, q_sets=False, filters=[cfg], searches=[dict(cfg, old_move=False, memo=False)],
                         pairs=False)
    assert bad["node_fail"] and bad["chain_fail"]


def test_matrix_and_masks_round_trip():
    for masks in sc.labelled_graphs(4):
        assert sc.masks_from_matrix(sc.matrix_from_masks(masks)) == masks
    assert sc.relabel([0b011, 0b011, 0b100], [2, 0, 1]) == [0b101, 0b010, 0b101]


# Smallest witnesses found by the item 06 sweep (random sparse graphs at 8-16;
# every graph to 7 vertices is clean for both bad forms).
BUG_B_NODE_8 = ([139, 59, 12, 15, 178, 242, 224, 241], 4, 0b100)   # masks, k, state S = {2}
BUG_B_TREE_10 = ([523, 519, 678, 73, 16, 548, 72, 388, 384, 551], 3)


def test_bug_b_loses_the_last_solution_at_one_node_of_an_8_vertex_graph():
    masks, k, S = BUG_B_NODE_8
    model = sc.Model(masks, k)
    full = (1 << len(masks)) - 1
    assert model.cl(S) == S
    for variant, lost in (("old_order", True), ("fixed", False), ("bm_first", False)):
        cfg = dict(definite=False, subset=True, better=True, limit=0, variant=variant, old_move=False)
        P, L, links, _, _ = sc.node_filter(masks, full, S, 0, k, cfg)
        assert [c for _, c in P] == [0, 3, 6]
        assert any(model.sol(model.cl(S | 1 << c)) for _, c in P)
        assert any(model.sol(model.cl(S | 1 << c)) for _, c in L) is not lost
    cfg = dict(definite=False, subset=True, better=True, limit=0, variant="old_order", old_move=False)
    _, L, links, _, _ = sc.node_filter(masks, full, S, 0, k, cfg)
    assert [c for _, c in L] == [6]
    assert set(links) == {(3, 0, "better"), (0, 3, "subset")}          # the two-rule cycle


def test_bug_b_alone_refutes_a_10_vertex_graph_at_its_optimum():
    masks, k = BUG_B_TREE_10
    model = sc.Model(masks, k)
    assert model.sol(model.cl(0)) and not sc.Model(masks, k - 1).sol(0)
    base = dict(definite=False, subset=True, better=True, limit=0, old_move=True, memo=True)
    assert sc.search_decide(masks, k, dict(base, variant="old_order"))[0] is False
    assert sc.search_decide(masks, k, dict(base, variant="fixed"))[0] is True


# --- item 07: the Lean model of Search/Basic.lean ---------------------------


def test_model_quick_run_has_no_failures():
    r = sc.run_model(quick=True, workers=2)
    assert r["failures"] == 0
    assert r["tally"]["layouts"] > 0 and r["tally"]["mono_pairs"] > 0


def test_model_order_cost_hand_values():
    path = sc.masks_from_edges(3, [(0, 1), (1, 2)])
    # closing 0 opens {0,1} (2); then 1 opens 2: open {1,2} (2); then 2: {2} (1)
    assert sc.m_order_cost(path, 0, [0, 1, 2]) == 2
    # closing the middle first opens everything: 3 stacks
    assert sc.m_order_cost(path, 0, [1, 0, 2]) == 3
    assert sc.m_out_narrowness(path, [0, 1, 2]) == 2
    assert sc.m_vs_of_layout(path, [0, 1, 2]) == 1
    star = sc.masks_from_edges(4, [(0, 1), (0, 2), (0, 3)])
    assert min(sc.m_order_cost(star, 0, p) for p in itertools.permutations(range(4))) == 2


def test_model_lemma_f_needs_the_invariant():
    # K2 with customer 0 closed: |O(T) - T| = 1 > k = 0. cl(T) is everything, so
    # SearchSol holds there, while closing 1 after 0 costs one stack: not Solvable.
    k2 = sc.masks_from_edges(2, [(0, 1)])
    T = 0b01
    assert sc.m_cl(k2, T) == 0b11
    assert sc.m_searchsol_table(k2, 0)[sc.m_cl(k2, T)]
    assert not sc.m_solvable_table(k2, 0)[T]
    # at k = 1 the invariant holds and the two agree
    assert sc.m_solvable_table(k2, 1)[T] and sc.m_searchsol_table(k2, 1)[sc.m_cl(k2, T)]


def test_model_catches_a_wrong_cost():
    # a cost that forgets to count the customer being closed breaks cost = vs + 1
    path = sc.masks_from_edges(3, [(0, 1), (1, 2)])
    wrong = max((sc.m_opened(path, T | 1 << c) & ~(T | 1 << c)).bit_count()
                for T, c in ((0, 0), (1, 1), (3, 2)))
    assert wrong != sc.m_vs_of_layout(path, [0, 1, 2]) + 1
    assert sc.m_order_cost(path, 0, [0, 1, 2]) == sc.m_vs_of_layout(path, [0, 1, 2]) + 1


# --- item 08: the definite move (Search/DefiniteMove.lean) -----------------


def test_definite_quick_run_has_no_failures():
    r = sc.run_definite(quick=True, workers=2)
    assert r["failures"] == 0
    assert r["tally"]["hereditary_moves"] > 0 and r["tally"]["code_moves"] > 0


def _lean_cex():
    masks, S, q, k = sc.DEFINITE_CEX[0]
    edges = [(0, 3), (0, 4), (0, 7), (0, 11), (1, 2), (1, 5), (1, 6), (2, 3), (2, 4), (5, 9),
             (5, 11), (5, 12), (6, 8), (6, 13), (7, 9), (7, 10), (7, 13), (8, 9), (8, 10),
             (8, 11), (9, 10), (9, 11), (10, 11), (10, 12), (10, 13), (12, 13)]
    return masks, S, q, k, edges


def test_definite_counterexample_is_the_lean_graph():
    masks, S, q, k, edges = _lean_cex()
    assert masks == sc.masks_from_edges(14, edges)       # cexEdges of DefiniteMove.lean


@pytest.mark.parametrize("idx", range(len(sc.DEFINITE_CEX)))
def test_definite_move_loses_the_last_solution(idx):
    masks, S, q, k = sc.DEFINITE_CEX[idx]
    n = len(masks)
    O = sc.d_opened_table(masks)
    assert sc.m_cl(masks, S) == S and sc.d_open_stacks(O, S) <= k     # a state the search visits
    op, close = sc.d_counts(masks, O, S, q)
    assert op <= close and (O[S | 1 << q] & ~S).bit_count() <= k       # the code's premise
    cfg = {"definite": True, "subset": True, "better": True, "limit": 0, "variant": "fixed",
           "old_move": False}
    _, L, _, _, _ = sc.node_filter(masks, (1 << n) - 1, S, 0, k, cfg)
    assert [c for _, c in L] == [q]                                    # the port keeps q alone
    P = sc.d_solvable_table(masks, k, O)
    assert P[S] and not P[sc.d_child(masks, O, S, q)]
    assert sc.m_searchsol_table(masks, k)[S]
    assert not sc.d_hereditary(masks, O, S, q)


def test_definite_counterexample_lean_certificates():
    masks, S, q, k, _ = _lean_cex()
    # the solution of cex_solvable
    assert sc.m_order_cost(masks, S, [1, 3, 4, 6, 12, 13, 0, 5, 7, 8, 9, 10, 11]) <= k
    # cexFamily is closed under playable moves and misses the full set
    fam = {sum(1 << c for c in A) for A in ([0, 2, 3, 4], [0, 1, 2, 3, 4], [0, 2, 3, 4, 5],
           [0, 1, 2, 3, 4, 5], [0, 2, 3, 4, 6], [0, 1, 2, 3, 4, 6], [0, 2, 3, 4, 7])}
    assert (1 << 14) - 1 not in fam and sc.m_cl(masks, S | 1 << q) in fam
    for A in fam:
        for c in range(14):
            if not A >> c & 1 and sc.m_step_cost(masks, A, c) <= k:
                assert A | 1 << c in fam
    # not_isHereditarilyDefinite_cex: B = {2, 3, 4}
    O = sc.d_opened_table(masks)
    assert sc.d_open_stacks(O, 0b11100) == 2 and sc.d_open_stacks(O, 0b11101) == 3


def test_definite_repair_and_matching_agree_and_are_sound_on_small_graphs():
    for n in range(1, 5):
        for masks in sc.labelled_graphs(n):
            t = sc.check_definite_graph(masks)
            assert not any(v for key, v in t.items() if key.startswith("fail_")), (masks, t)


def test_definite_checker_catches_a_planted_fault(monkeypatch):
    # replace the repaired premise by the code's (B = S only): the checker must then report
    # the repair as unsound on the pinned instance
    masks, S, q, k = sc.DEFINITE_CEX[0]
    assert sc.check_definite_graph(masks, ks=[k]).get("fail_hereditary_sound", 0) == 0

    def code_premise(masks, O, S, q):
        op, close = sc.d_counts(masks, O, S, q)
        return op <= close

    monkeypatch.setattr(sc, "d_hereditary", code_premise)
    t = sc.check_definite_graph(masks, ks=[k])
    assert t["fail_hereditary_sound"] >= 1


# --- item 09: the subset rule (Search/SubsetRule.lean) ---------------------


def test_subset_quick_run_has_no_failures():
    r = sc.run_subset(quick=True, workers=2)
    assert r["failures"] == 0
    assert r["tally"]["covering_premises"] > 0 and r["tally"]["nodes"] > 0
    assert r["tally"]["port_nodes"] > 0 and r["tally"].get("fail_port", 0) == 0


def test_subset_every_statement_on_every_set_to_four_vertices():
    for n in range(1, 5):
        for masks in sc.labelled_graphs(n):
            t = sc.check_subset_graph(masks, all_sets=True)
            assert not any(v for key, v in t.items() if key.startswith("fail_")), (masks, t)


def test_subset_tie_break_counterexample_is_the_lean_graph():
    masks, S, k = sc.SUBSET_TIE_CEX
    edges = [(0, 2), (0, 3), (0, 6), (1, 4), (1, 6), (3, 6), (4, 5), (4, 6)]   # tieEdges
    assert masks == sc.masks_from_edges(7, edges)
    O, CL = sc.s_tables(masks)
    assert CL[S] == S and (O[S] & ~S).bit_count() <= k
    P = sc.s_playable(masks, O, S, k, [c for c in range(7) if not S >> c & 1])
    assert P == [0, 3, 5]
    assert sc.s_filter_by(sc.s_weak_dominated, masks, O, S, P) == [5]
    assert sc.s_subset_filter(masks, O, S, P) == [0, 5]
    SS = sc.s_searchsol_table(masks, k, O, CL)
    assert SS[S] and not SS[CL[S | 1 << 5]] and SS[CL[S | 1]]
    assert CL[S | 1 << 5] == 0b100100                                      # tie_cl_insert
    assert sc.m_order_cost(masks, S, [0, 3, 1, 4, 5, 6]) <= k               # tie_solvable
    # from {2, 5} nothing is playable within 3: the invariant family is {{2, 5}}
    assert all(sc.m_step_cost(masks, 0b100100, c) > k for c in (0, 1, 3, 4, 6))


def test_subset_checker_catches_a_missing_tie_break(monkeypatch):
    masks, S, k = sc.SUBSET_TIE_CEX
    assert not any(v for key, v in sc.check_subset_graph(masks, ks=[k], all_sets=False).items()
                   if key.startswith("fail_"))

    def no_tie_break(masks, O, S, d, r):
        a, b = masks[d] & ~O[S], masks[r] & ~O[S]
        return d != r and a & ~b == 0

    monkeypatch.setattr(sc, "s_dominates", no_tie_break)
    t = sc.check_subset_graph(masks, ks=[k], all_sets=False)
    assert t["fail_subset_node"] >= 1 and t["fail_exists_undominated"] >= 1


def test_subset_composition_with_the_code_definite_move_loses_on_the_cex():
    masks, S, q, k = sc.DEFINITE_CEX[0]
    O, CL = sc.s_tables(masks)
    P = sc.s_playable(masks, O, S, k, [c for c in range(len(masks)) if not S >> c & 1])

    def code(c):
        op, close = sc.d_counts(masks, O, S, c)
        return op <= close

    assert sc.s_composed(masks, O, S, P, code) == [q]                     # codeFilter = {0}
    SS = sc.s_searchsol_table(masks, k, O, CL)
    assert SS[S] and not SS[CL[S | 1 << q]]
    L = sc.s_composed(masks, O, S, P, lambda c: sc.d_hereditary(masks, O, S, c))
    assert any(SS[CL[S | 1 << c]] for c in L)                              # repairedFilter
