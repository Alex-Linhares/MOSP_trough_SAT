"""Guards on `paper1.search_check` (loop0006 item 06).

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
from collections import Counter

import pytest

import paper1.search_check as sc
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


# ---------------------------------------------------------------------------
# item 10: Search/BetterMove.lean
# ---------------------------------------------------------------------------


def test_better_quick_run_has_no_failures():
    r = sc.run_better(quick=True, workers=2)
    assert r["failures"] == 0
    assert r["tally"]["repaired_applications"] > 0 and r["tally"]["nodes"] > 0


def test_better_every_statement_on_every_set_to_four_vertices():
    for n in range(1, 5):
        for masks in sc.labelled_graphs(n):
            t = sc.check_better_graph(masks, all_sets=True)
            assert not any(v for key, v in t.items() if key.startswith("fail_")), (masks, t)


def test_better_move_counterexample_is_the_lean_statement():
    masks, S, r, q, k = sc.BETTER_CEX
    O, CL = sc.s_tables(masks)
    n = len(masks)
    P = sc.s_playable(masks, O, S, k, list(range(n)))
    code_def = lambda c: (lambda oc: oc[0] <= oc[1])(sc.d_counts(masks, O, S, c))
    assert not any(code_def(c) for c in P)                                # definite does not fire
    W = sc.s_subset_filter(masks, O, S, P)
    assert q in W and r in W and q < r
    assert sc.b_is_better(masks, O, S, k, r, q)
    assert not sc.b_is_repaired(masks, O, CL, S, k, r, q)
    cite = lambda W, a, b: sc.b_is_better(masks, O, S, k, a, b)
    kept = sc.b_full(masks, O, S, P, code_def, cite)
    assert r not in kept and 1 in kept                                   # the node keeps 1
    SS = sc.s_searchsol_table(masks, k, O, CL)
    assert SS[CL[S | 1 << r]] and not SS[CL[S | 1 << q]] and SS[CL[S | 1 << 1]]
    assert CL[1 << q] == 1 << q and CL[1 << r] == 1 << r                  # bm_cl_zero, bm_cl_two


def test_bug_a_counterexample_is_the_lean_graph():
    masks, S, r, q, k = sc.BUG_A_CEX
    edges = [(0, 1), (0, 2), (0, 3), (0, 5), (0, 8), (0, 10), (0, 11), (1, 3), (1, 4), (1, 10),
             (2, 3), (2, 7), (2, 10), (5, 8), (6, 7), (6, 9), (7, 9), (7, 10), (8, 10), (8, 11),
             (10, 11)]                                                    # bugAEdges
    assert masks == sc.masks_from_edges(12, edges)
    O, CL = sc.s_tables(masks)
    assert sc.b_is_better(masks, O, S, k, r, q, old=True)
    assert not sc.b_is_better(masks, O, S, k, r, q)
    SS = sc.s_searchsol_table(masks, k, O, CL)
    assert SS[CL[1 << r]] and not SS[CL[1 << q]]
    assert CL[1 << r] == (1 << 6) | (1 << 9) and CL[1 << q] == 1 << 4


def test_bug_b_counterexample_is_the_lean_graph():
    masks, S, k = sc.BUG_B_CEX
    edges = [(0, 1), (0, 3), (0, 7), (1, 3), (1, 4), (1, 5), (2, 3), (4, 5), (4, 7), (5, 6),
             (5, 7), (6, 7)]                                              # bugBEdges
    assert masks == sc.masks_from_edges(8, edges)
    O, CL = sc.s_tables(masks)
    P = sc.s_playable(masks, O, S, k, [c for c in range(8) if not S >> c & 1])
    assert P == [0, 3, 6]
    code_def = lambda c: (lambda oc: oc[0] <= oc[1])(sc.d_counts(masks, O, S, c))
    cite = lambda W, a, b: sc.b_is_better(masks, O, S, k, a, b)
    assert sc.b_old_order(masks, O, S, P, code_def, cite) == [6]
    assert sc.b_full(masks, O, S, P, code_def, cite) == [3, 6]
    SS = sc.s_searchsol_table(masks, k, O, CL)
    assert SS[S] and SS[CL[S | 1 << 3]] and not SS[CL[S | 1 << 6]]


def test_better_checker_catches_the_code_premise_as_the_repair(monkeypatch):
    masks, S, r, q, k = sc.BETTER_CEX
    assert sc.check_better_graph(masks, ks=[k], limits=(0,)).get("fail_repaired_sound", 0) == 0
    monkeypatch.setattr(sc, "b_is_repaired",
                        lambda masks, O, CL, S, k, r, q: sc.b_is_better(masks, O, S, k, r, q))
    t = sc.check_better_graph(masks, ks=[k], limits=(0,))
    assert t["fail_repaired_sound"] >= 1


def test_better_hunt_finds_the_false_link_and_the_repair_nothing(tmp_path):
    import shutil
    import subprocess
    from pathlib import Path
    if shutil.which("gcc") is None:
        pytest.skip("no gcc")
    src = Path(sc.__file__).resolve().parent / "better_hunt.c"
    exe = tmp_path / "better_hunt"
    subprocess.run(["gcc", "-O2", "-o", str(exe), str(src)], check=True)
    masks = sc.BETTER_CEX[0]
    line = f"{len(masks)} " + " ".join(map(str, masks)) + "\n"
    out = {}
    for mode in ("0", "2"):
        out[mode] = subprocess.run([str(exe)], input=line, capture_output=True, text=True,
                                   env={"MODE": mode}, check=True).stdout
    assert "PAIR k=6 S=0 r=2 q=0" in out["0"] and "NODE" not in out["0"]
    assert "PAIR" not in out["2"] and "NODE" not in out["2"]


# ----------------------------------------------------------------------------
# item 11: the memo and the old move (Search/Memo.lean)
# ----------------------------------------------------------------------------


def test_memo_quick_run_has_no_failures():
    r = sc.run_memo(quick=True, workers=2)
    assert r["failures"] == 0
    t = r["tally"]
    assert t["reinsert_cases"] > 0 and t["tree_runs"] > 0 and t["path_cases"] > 0
    assert t["untested_reinsert_fails"] > 0          # the lemma needs its test


def test_memo_every_statement_on_every_set_to_four_vertices():
    for n in range(1, 5):
        for masks in sc.labelled_graphs(n):
            t = sc.check_memo_graph(masks, all_sets=True)
            assert not any(v for key, v in t.items() if key.startswith("fail_")), (masks, t)


def test_reinsert_counterexample_is_the_lean_graph():
    masks, S, q, c, k = sc.REINSERT_CEX
    assert masks == sc.masks_from_edges(5, [(0, 2), (0, 4), (1, 2), (1, 3)])   # reinsertEdges
    O, CL = sc.s_tables(masks)
    SS = sc.s_searchsol_table(masks, k, O, CL)
    assert (O[S | 1 << c] & ~S).bit_count() <= k                               # c playable
    assert (O[S | 1 << q | 1 << c] & ~(S | 1 << q)).bit_count() == 3           # test fails
    assert CL[S | 1 << q] == 0b100 and CL[CL[S | 1 << c] | 1 << q] == 0b1110   # h2, h32
    assert SS[CL[CL[S | 1 << c] | 1 << q]] and not SS[CL[S | 1 << q]]
    assert sc.m_order_cost(masks, 0b1110, [0, 4]) <= k


def test_inherit_all_mutation_gives_a_false_refutation():
    masks, k = sc.INHERIT_ALL_CEX
    O, CL = sc.s_tables(masks)
    SS = sc.s_searchsol_table(masks, k, O, CL)
    assert SS[0]
    cfg = sc.MEMO_FILTERS[0]
    ans, bad = sc.memo_run(masks, k, cfg, O, CL, SS)
    assert ans and not bad
    ans, bad = sc.memo_run(masks, k, cfg, O, CL, SS, inherit_all=True)
    assert not ans and bad["q_not_refuted"] > 0 and bad["false_refutation_recorded"] > 0


def test_memo_checker_catches_inheritance_without_the_test(monkeypatch):
    masks, k = sc.INHERIT_ALL_CEX
    t = sc.check_memo_graph(masks, ks=[k], all_sets=False)
    assert not any(v for key, v in t.items() if key.startswith("fail_"))
    monkeypatch.setattr(sc, "inherit", lambda masks, seen, closed, opened, c, k: seen)
    t = sc.check_memo_graph(masks, ks=[k], all_sets=False)
    assert t["fail_tree_answer"] >= 1 and t["fail_q_not_refuted"] >= 1


# ---------------------------------------------------------------------------
# item 12: the search assembled (Search/Decide.lean)
# ---------------------------------------------------------------------------


def test_decide_quick_run_has_no_failures():
    r = sc.run_decide(quick=True, workers=2)
    assert r["failures"] == 0
    t = r["tally"]
    assert t["repaired_runs"] > 0 and t["code_runs"] > 0 and t["pw_cases"] > 0
    assert r["pinned"]["lean_claims_hold"]


def test_decide_every_statement_to_four_vertices_with_pathwidth():
    for n in range(1, 5):
        for masks in sc.labelled_graphs(n):
            t = sc.check_decide_graph(masks, pw=True)
            assert not any(v for key, v in t.items() if key.startswith("fail_")), (masks, t)
            assert t["code_runs_runsound"] == t["code_runs"]


def test_code_full_filter_at_the_lean_counterexample():
    masks, S, q, k = sc.DEFINITE_CEX[0]
    O, CL = sc.s_tables(masks)
    for L in range(4):                                    # codeFullFilter_cex, every L
        assert sc.k_code_filter(masks, O, S, 0, k, L) == [0]
    SS = sc.s_searchsol_table(masks, k, O, CL)
    assert SS[S] and not SS[CL[S | 1 << q]]              # not_codeFilterSound_cexGraph
    assert not sc.k_node_repaired(masks, O, CL, S, 0, k, 0)


def test_code_run_visits_a_lost_node_and_still_answers_right():
    masks, k, S = sc.RUN_LOST_CEX
    O, CL = sc.s_tables(masks)
    SS = sc.s_searchsol_table(masks, k, O, CL)
    for L in sc.DECIDE_LIMITS:
        lost = []
        ans, t = sc.decide_run(masks, k, lambda T, Q: sc.k_code_filter(masks, O, T, Q, k, L),
                               O, CL, SS, L, lost=lost)
        assert lost == [S] and ans and SS[0]
        assert t["nodes_unsound"] == 1 and t["nodes_repaired"] == t["nodes"] - 1
        ans, _ = sc.decide_run(masks, k, lambda T, Q: sc.k_repaired_filter(masks, O, CL, T, Q, k, L),
                               O, CL, SS, L, inspect=False)
        assert ans
    # one stack below the optimum nothing can be lost: no visited state has a solution
    SS = sc.s_searchsol_table(masks, k - 1, O, CL)
    lost = []
    ans, t = sc.decide_run(masks, k - 1, lambda T, Q: sc.k_code_filter(masks, O, T, Q, k - 1, 0),
                           O, CL, SS, 0, lost=lost)
    assert not ans and not lost


def test_decide_checker_catches_a_vacuous_repair_check(monkeypatch):
    monkeypatch.setattr(sc, "k_node_repaired", lambda *a: True)
    masks, k, _ = sc.RUN_LOST_CEX
    t = sc.check_decide_graph(masks, ks=[k])
    assert t["fail_repaired_not_sound"] > 0


# --- item 13: Hall's converse (Search/DefiniteMatching.lean) ---------------------------------


def test_hall_quick_run_has_no_failures():
    r = sc.run_hall(quick=True, workers=2)
    assert r["failures"] == 0 and r["tally"]["hereditary_pairs"] > 0


def test_hall_every_statement_at_every_set_to_four_vertices():
    for n in range(1, 5):
        for masks in sc.labelled_graphs(n):
            t = sc.check_hall_graph(masks)
            assert not any(v for k, v in t.items() if k.startswith("fail_")), masks
            assert t["deficiency_ne_hereditary"] == 0


def test_hall_cex_graph_has_no_matching():
    masks, S, q, _ = sc.DEFINITE_CEX[0]
    O = sc.d_opened_table(masks)
    op, _ = sc.d_counts(masks, O, S, q)
    assert (op, sc.d_matching_size(masks, O, S, q)) == (3, 1)   # 1 < open - 1 = 2
    assert not sc.h_hereditary_any(masks, O, S, q)


def test_hall_checker_catches_a_deficiency_form_without_the_slack():
    # the deficiency form with `+ |Y|` but not `+ 1` is false: `q` alone opening one stack
    t = Counter()
    for masks in sc.labelled_graphs(3):
        t.update(sc.check_hall_graph(masks, mutate=True))
    assert t["fail_hall_of_hereditary"] > 0


def test_hall_checker_catches_a_short_matching(monkeypatch):
    real = sc.d_matching_size
    monkeypatch.setattr(sc, "d_matching_size", lambda *a: max(real(*a) - 1, 0))
    t = Counter()
    for masks in sc.labelled_graphs(4):
        t.update(sc.check_hall_graph(masks))
    assert t["fail_iff_matching"] > 0
