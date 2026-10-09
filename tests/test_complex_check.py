"""Tests for `paper1.complex_check`: every quantity on graphs and matrices whose
values can be checked by hand (path, star, cycle, K4, K3,3), plus agreement
of the prefix-set DPs with the literal minimum over permutations."""
from __future__ import annotations

import itertools

import pytest

from paper1 import complex_check as cc

P4 = cc.path_graph(4)
K13 = cc.star_graph(3)
C5 = cc.cycle_graph(5)
K4 = cc.complete_graph(4)
K33 = cc.complete_bipartite(3, 3)
EMPTY3 = cc.graph(3, [])

# (graph, pw, cutwidth, modified cutwidth, bandwidth, edge search, interval bandwidth)
HAND = [
    # P4: one searcher sweeps a path; the line layout has cut 1 and nothing
    # passes over a vertex.
    (P4, 1, 1, 0, 1, 1, 1),
    # K1,3: centre in the middle, three leaves: cut 2 at the centre's side;
    # es 2 (a guard on the centre, one slider); sb = ib = 2 (Fomin: splits of
    # a tree keep >= 3 leaves, so bandwidth 1 is impossible).
    (K13, 1, 2, 1, 2, 2, 2),
    # C5: pw 2; the cycle laid out as a path of length 4 plus a closing edge.
    (C5, 2, 2, 1, 2, 2, 2),
    # K4: pw 3; cut 4 in the middle (2 x 2); es(K_n) = n for n >= 4.
    (K4, 3, 4, 2, 3, 4, 3),
    # K3,3: pw 3; es 5 (EST 1994 p. 57); cutwidth 5.
    (K33, 3, 5, 3, 4, 5, 4),
]


@pytest.mark.parametrize("g,pw,cw,mcw,bw,es,ib", HAND)
def test_hand_values(g, pw, cw, mcw, bw, es, ib):
    assert cc.pathwidth(g) == pw
    assert cc.vertex_separation(g) == pw           # Kinnersley Thm 3.1
    assert cc.vsg(g) == pw                         # Lengauer's game, by reversal
    assert cc.interval_thickness(g) == pw + 1      # Mohring Prop. 3.5
    assert cc.interval_thickness_events(g) == pw + 1
    assert cc.narrowness(g) == pw + 1              # Kornai & Tuza Prop. 3.1
    assert cc.node_search(g) == pw + 1             # K&P 1986 Thm 4.1
    assert cc.node_search(g, monotone=True) == pw + 1
    assert cc.cutwidth(g) == cw
    assert cc.modified_cutwidth(g) == mcw
    assert cc.bandwidth(g) == bw
    assert cc.edge_search(g) == es
    assert cc.edge_search(g, monotone=True) == es
    assert cc.interval_bandwidth(g) == ib


def test_edge_cases():
    assert cc.pathwidth(cc.graph(0, [])) == 0
    assert cc.pathwidth(EMPTY3) == 0
    assert cc.interval_thickness(EMPTY3) == 1
    assert cc.narrowness(EMPTY3) == 1
    # nothing to clear: the node search number is 0, not vs + 1 = 1
    assert cc.node_search(EMPTY3) == 0
    assert cc.edge_search(EMPTY3) == 0
    assert cc.vsg(EMPTY3) == 0


def test_narrowness_of_sequence_is_vs_of_sequence_plus_one():
    for order in itertools.permutations(range(5)):
        assert cc.narrowness_of_sequence(C5, order) == cc.vs_of_layout(C5, order) + 1


def test_dps_match_the_literal_minimum():
    for g in (P4, K13, C5, K4, cc.graph(5, [(0, 1), (1, 2), (0, 2), (2, 3)])):
        assert cc.vs_dp(g) == cc.vertex_separation(g)
        assert cc.cutwidth_dp(g) == cc.cutwidth(g)
        assert cc.modified_cutwidth_dp(g) == cc.modified_cutwidth(g)


def test_stars_break_both_cutwidths():
    # Lengauer's two edge readings are unbounded against pathwidth 1.
    assert cc.cutwidth_dp(cc.star_graph(7)) == 4
    assert cc.modified_cutwidth_dp(cc.star_graph(9)) == 4


def test_two_expansion_and_lengauer_du():
    # EST Thm 2.2: es(G) = vs(G'') on the 2-expansion.
    for g in (P4, K13, cc.cycle_graph(4)):
        assert cc.vs_dp(cc.two_expansion(g)) == cc.edge_search(g)
    # Lengauer Thm 4: a triangle on every edge adds exactly one.
    for g in (P4, K13, C5, K4):
        assert cc.vs_dp(cc.lengauer_du(g)) == cc.vertex_separation(g) + 1


def test_interval_bandwidth_numbering_semantics():
    # K2 with the bijection (u, v): g = 1.  K1,3 needs 2 (checked above);
    # splitting the centre of K1,3 does not help within three splittings.
    assert cc.interval_bandwidth(cc.complete_graph(2)) == 1
    assert cc.split_bandwidth_upto(K13, 3) == 2
    assert cc.split_bandwidth_upto(cc.path_graph(3), 2) == 1


def test_matrices():
    # 5 x 5 identity: every net alone, t = pw + 1 = 1, PLA folding needs 3.
    i5 = cc.identity_matrix(5)
    assert cc.mosp_value(i5) == 1
    assert cc.gate_matrix_tracks(i5) == 1
    assert cc.pla_folding_tracks(i5) == 3
    # the incidence matrix of K4 is the MOSP instance with MOSP graph K4
    m = cc.incidence_matrix(K4)
    assert cc.row_graph(m) == K4
    assert cc.mosp_value(m) == cc.gate_matrix_tracks(m) == 4
    assert cc.mosp_value(((0, 0), (0, 0))) == 0


def test_ohtsuki():
    # the item-01 family: H over all gates (eq. (6)) is two K_k joined by a
    # matching, so pinning the boundary gates costs nothing there
    for k in (2, 3):
        mx = cc.boundary_family(k)
        r = cc.ohtsuki_boundary_row(mx, (0, k + 1))
        assert r["tracks_boundary"] == r["tracks_free"] == r["pw1"] == k + 1
    mx, lr = cc.boundary_path_instance()
    r = cc.ohtsuki_boundary_row(mx, lr)
    assert (r["tracks_boundary"], r["tracks_free"], r["pw1"]) == (3, 2, 2)


def test_graph_checks_all_pass_on_small_graphs():
    for g in (P4, K13, C5, K4):
        r = cc.graph_row(g)
        bad = [name for name, ok in cc.graph_checks(r) if not ok and "within 1" not in name]
        assert not bad, bad
