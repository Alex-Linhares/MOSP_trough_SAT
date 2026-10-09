"""Tests for the pebbling part of `paper1.complex_check` (loop0006 item 02):
the four games on dags whose demands can be checked by hand, Lengauer's
constructions G_u and G_d, and a quick run of every P.5 statement."""
from __future__ import annotations

import itertools

import networkx as nx
import pytest
from networkx.generators.atlas import graph_atlas_g

from paper1 import complex_check as cc

ONE = cc.dag(1, [])
ARC = cc.dag(2, [(0, 1)])
CHAIN = cc.dag(3, [(0, 1), (1, 2)])
IN_STAR = cc.dag(4, [(1, 0), (2, 0), (3, 0)])      # every edge to the centre
OUT_STAR = cc.dag(4, [(0, 1), (0, 2), (0, 3)])
EDGELESS = cc.dag(3, [])
# three legs of length 2 from the root, directed away from it: the smallest
# out-tree on which recomputation helps (P.5 statement 8)
SPIDER_OUT = cc.dag(7, [(0, 1), (1, 2), (0, 3), (3, 4), (0, 5), (5, 6)])
SPIDER_IN = cc.dag(7, [(v, u) for u, v in cc.arcs_of(SPIDER_OUT)])

# (dag, progressive bw, progressive black, unrestricted bw, unrestricted black)
HAND = [
    (ONE, 1, 1, 1, 1),
    # the head must be pebbled while the tail's pebble turns black
    (ARC, 2, 2, 2, 2),
    # slide two pebbles along the chain
    (CHAIN, 2, 2, 2, 2),
    # the centre turns only with all three leaves pebbled: 4 at that instant
    (IN_STAR, 4, 4, 4, 4),
    # keep the root, pebble and remove the leaves one by one
    (OUT_STAR, 2, 2, 2, 2),
    (EDGELESS, 1, 1, 1, 1),
    # progressive: a pebble on the root until the last leg starts, plus two on
    # a leg; with repebbling the root is re-placed for each leg
    (SPIDER_OUT, 3, 3, 2, 2),
    # the root turns with its three predecessors pebbled, as for IN_STAR
    (SPIDER_IN, 4, 4, 4, 4),
]


@pytest.mark.parametrize("d,pbw,pb,bw,b", HAND)
def test_hand_demands(d, pbw, pb, bw, b):
    assert cc.pbw(d, "kp") == pbw
    assert cc.pbw(d, "lengauer") == pbw
    assert cc.pb(d) == pb
    assert cc.bw_unrestricted(d) == bw
    assert cc.black_unrestricted(d) == b


def test_budget_is_monotone_and_exact():
    for d, pbw, *_ in HAND:
        assert not cc.progressive_bw_within(d, pbw - 1, "lengauer")
        assert all(cc.progressive_bw_within(d, k, "lengauer") for k in range(pbw, d[0] + 2))


def test_white_pebble_is_never_removed():
    # a -> b with one pebble: white on b cannot be removed or turned, and a
    # can never be pebbled, so the game cannot finish
    assert not cc.progressive_bw_within(ARC, 1, "lengauer")
    assert not cc.unrestricted_bw_within(ARC, 1)


def test_dag_rejects_cycles():
    with pytest.raises(ValueError):
        cc.dag(2, [(0, 1), (1, 0)])


def test_lengauer_u():
    assert cc.lengauer_u(IN_STAR) == cc.complete_graph(4)
    assert cc.lengauer_u(OUT_STAR) == cc.star_graph(3)
    assert cc.lengauer_u(CHAIN) == cc.path_graph(3)


def test_lengauer_d_and_triangle_graph():
    for g in (cc.complete_graph(3), cc.path_graph(4), cc.star_graph(3), cc.cycle_graph(4)):
        gd = cc.lengauer_d(g)
        assert gd[0] == g[0] + len(cc.edges_of(g))
        assert cc.lengauer_u(gd) == cc.lengauer_du(g)       # (G_d)_u = G_du
        # Thm 3 as a number, and the unrestricted games bounded by 3
        assert cc.pbw(gd) == cc.vs_dp(g) + 2
        assert cc.bw_unrestricted(gd) <= 3
        assert cc.black_unrestricted(gd) <= 3
    assert cc.pbw(cc.lengauer_d(cc.graph(2, []))) == 1


def test_pebble_matrix_is_the_mosp_instance():
    assert cc.pebble_matrix(ARC) == ((1, 1), (0, 1))
    for d in (ARC, CHAIN, IN_STAR, OUT_STAR, SPIDER_IN):
        m = cc.pebble_matrix(d)
        assert cc.row_graph(m) == cc.lengauer_u(d)
        if d[0] <= 7:
            assert cc.mosp_value(m) == cc.pbw(d)


def test_directives():
    c4 = cc.cycle_graph(4)
    assert len(cc.acyclic_orientations(c4)) == 14           # 2^4 minus the 2 cycles
    assert cc.mpb_mpbw(c4) == (3, 3)
    assert cc.mpb_mpbw(cc.path_graph(4)) == (2, 2)
    assert cc.mpb_mpbw(cc.star_graph(4)) == (2, 2)          # KP p. 214: mpb 2, bw(in-star) n + 1


def test_is_chordal_against_networkx():
    for h in graph_atlas_g():
        if 1 <= h.number_of_nodes() <= 6:
            assert cc.is_chordal(cc.from_nx(h)) == nx.is_chordal(h)


def test_c4_is_not_any_du():
    c4 = cc.cycle_graph(4)
    assert not any(cc.lengauer_u(d) == c4 for d in cc.acyclic_orientations(c4))


def test_recontamination_lemma_small():
    for d in (ARC, CHAIN, IN_STAR, OUT_STAR, cc.dag(4, [(0, 1), (0, 2), (1, 3), (2, 3)])):
        assert cc.repebble_play_lemma(d) > 0


def test_ternary_tree_shape():
    t = cc.ternary_tree(1)
    assert t == OUT_STAR
    assert cc.ternary_tree(2)[0] == 13


def test_quick_run_has_no_failures():
    rep = cc.run_pebbling(quick=True, workers=2, out=None)
    assert rep["summary"]
    assert all(v["failed"] == 0 for v in rep["summary"].values()), rep["counterexamples"]


# --- loop0006 item 03: the constructions of the Lean proof of Theorem 3 ---


def test_replay_rejects_illegal_moves():
    # G_d of K2: vertices 0, 1 and the edge vertex 2 with predecessors 0, 1
    gd = cc.lengauer_d(cc.complete_graph(2))
    with pytest.raises(ValueError):  # the edge turns with only one end pebbled
        cc.replay_progressive(gd, [("place", 0), ("turn", 0), ("place", 2), ("turn", 2)])
    with pytest.raises(ValueError):  # a white pebble is never removed
        cc.replay_progressive(gd, [("place", 0), ("remove", 0)])
    with pytest.raises(ValueError):  # progressive: no second placement
        cc.replay_progressive(ONE, [("place", 0), ("turn", 0), ("remove", 0), ("place", 0)])
    with pytest.raises(ValueError):  # the play must end with everything done
        cc.replay_progressive(ONE, [("place", 0)])


def test_layout_strategy_on_named_graphs():
    for g in (cc.complete_graph(2), cc.complete_graph(3), cc.complete_graph(4),
              cc.path_graph(4), cc.cycle_graph(4), cc.star_graph(3)):
        n = g[0]
        best = min(cc.replay_progressive(cc.lengauer_d(g), cc.gd_layout_strategy(g, p))
                   for p in itertools.permutations(range(n)))
        assert best == cc.vs_dp(g) + 2
    # edgeless: one pebble at a time
    g = cc.graph(3, [])
    assert cc.replay_progressive(cc.lengauer_d(g), cc.gd_layout_strategy(g, (0, 1, 2))) == 1


def test_removal_layout_is_the_clearing_order():
    g = cc.path_graph(4)
    order = (2, 0, 3, 1)
    assert cc.removal_layout(4, cc.gd_layout_strategy(g, order)) == list(order)


def test_outer_convention_has_the_same_minimum():
    for h in graph_atlas_g()[1:60]:
        g = cc.from_nx(h)
        perms = list(itertools.permutations(range(g[0])))
        assert min(cc.vs_outer_of_layout(g, p) for p in perms) == cc.vertex_separation(g)


def test_strategy_quick_run_has_no_failures():
    rep = cc.run_pebbling_strategy(quick=True, workers=2, out=None)
    assert rep["graphs"] > 0 and rep["plays"] > 0
    assert all(v == 0 for v in rep["failures"].values()), rep["counterexamples"]


# --- loop0006 item 04: Lengauer Thm 2 and KP Thm 3.1 (Complex/PebblingGu.lean) ---

TWO_CYCLE = cc.digraph_pred(2, [(0, 1), (1, 0)])
LOOP = cc.digraph_pred(1, [(0, 0)])


def test_lengauer_u_general_agrees_on_dags():
    for d in [ONE, ARC, CHAIN, IN_STAR, OUT_STAR, EDGELESS, SPIDER_OUT, SPIDER_IN]:
        assert cc.lengauer_u_general(d) == cc.lengauer_u(d)
    # a loop adds no edge; a 2-cycle is one edge
    assert cc.edges_of(cc.lengauer_u_general(LOOP)) == []
    assert cc.edges_of(cc.lengauer_u_general(TWO_CYCLE)) == [(0, 1)]


@pytest.mark.parametrize("d", [ONE, ARC, CHAIN, IN_STAR, OUT_STAR, EDGELESS, SPIDER_IN,
                               TWO_CYCLE, LOOP])
def test_gu_strategy_is_legal_and_within_bound(d):
    u = cc.lengauer_u_general(d)
    for order in itertools.permutations(range(d[0])):
        k = cc.replay_progressive(d, cc.gu_layout_strategy(d, order))
        assert k <= cc.vs_outer_of_layout(u, order) + 1


def test_theorem2_holds_on_cyclic_digraphs():
    # the Lean statement needs no acyclicity: pbw = vs(G_u) + 1 on a 2-cycle and a loop
    for d, want in [(TWO_CYCLE, 2), (LOOP, 1)]:
        assert cc.vs_dp(cc.lengauer_u_general(d)) + 1 == want
        assert cc.progressive_bw_within(d, want) and not cc.progressive_bw_within(d, want - 1)


def test_gu_strategy_needs_the_successor_turns():
    # dropping step 3 (turn the successors of v) leaves the head of an arc unturnable
    moves = [m for m in cc.gu_layout_strategy(ARC, (0, 1)) if m != ("turn", 1)]
    with pytest.raises(ValueError):
        cc.replay_progressive(ARC, moves)


def test_kp_black_strategy_on_named_graphs():
    path = cc.graph(4, [(0, 1), (1, 2), (2, 3)])
    moves = cc.kp_black_strategy(path, (0, 1, 2, 3))
    assert cc.replay_black(cc.orient(path, (0, 1, 2, 3)), moves) == 2
    star = cc.graph(4, [(0, 1), (0, 2), (0, 3)])
    # centre first: 2 pebbles; centre last: all four at once
    assert cc.replay_black(cc.orient(star, (0, 1, 2, 3)), cc.kp_black_strategy(star, (0, 1, 2, 3))) == 2
    assert cc.replay_black(cc.orient(star, (1, 2, 3, 0)), cc.kp_black_strategy(star, (1, 2, 3, 0))) == 4


def test_replay_black_rejects_unpebbled_predecessor():
    with pytest.raises(ValueError):
        cc.replay_black(ARC, [("place", 1), ("place", 0), ("remove", 0), ("remove", 1)])


def test_black_to_bw_is_a_legal_bw_play():
    k5 = cc.graph(5, list(itertools.combinations(range(5), 2)))
    order = (2, 0, 4, 1, 3)
    moves = cc.kp_black_strategy(k5, order)
    d = cc.orient(k5, order)
    assert cc.replay_progressive(d, cc.black_to_bw(moves)) == cc.replay_black(d, moves) == 5


def test_gu_quick_run_has_no_failures():
    rep = cc.run_pebbling_gu(quick=True, workers=2, out=None)
    assert not any(rep["gu_failures"].values())
    assert not any(rep["kp_failures"].values())
    assert rep["digraphs"] == 1 + 2 + 16 + 512
