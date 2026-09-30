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
