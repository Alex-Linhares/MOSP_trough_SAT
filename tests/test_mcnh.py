"""Becceneri, Yanasse & Soma (2004)'s Minimal Cost Node heuristic as
`mcnh` in `satisfiability/heuristics.py`, and the study in `learning.mcnh`.

The pseudocode is checked against everything §4 of the paper prints for its
Table 1 instance: the arc chosen in each of the seven loops, the states after
loops 1–3, the sixteen arcs of ARC in order, ξ = 4, the pattern sequence and
Fig. 2's open-stack profile. Nothing here touches solver defaults or
`solutions/`.
"""

from __future__ import annotations

import random

import numpy as np
import pytest

from learning.mcnh import (
    BYS2004,
    BYS2004_ARC,
    BYS2004_FIG2,
    BYS2004_LOOP_ARCS,
    BYS2004_SEQUENCE,
    BYS2004_STATES,
    BYS2004_XI,
    paper_check,
    step_agreement,
)
from mosp.instance import MOSPInstance
from mosp.verify import count_open_stacks, max_open_stacks
from satisfiability.heuristics import (
    DEFAULT_STRATEGY,
    STRATEGIES,
    _customer_order_from_products,
    mcnh,
    mcnh_trace,
    patterns_from_arcs,
    two_key_closing_order,
    upper_bound,
)


def test_paper_loops_arcs_and_states():
    trace = mcnh_trace(BYS2004)
    assert len(trace["loops"]) == 7                     # "executes seven loops"
    assert [(L["n1"] + 1, L["n2"] + 1) for L in trace["loops"]] == BYS2004_LOOP_ARCS
    assert [frozenset((a + 1, b + 1)) for a, b in trace["arcs"]] == \
        [frozenset(arc) for arc in BYS2004_ARC]
    assert trace["xi"] == BYS2004_XI
    states = [(L["s"], L["xi"], [c + 1 for c in L["open"]], [c + 1 for c in L["setv"]])
              for L in trace["loops"][:3]]
    assert states == BYS2004_STATES


@pytest.mark.parametrize("rule", ["nodes", "arcs"])
def test_paper_sequence_and_fig2_profile(rule):
    trace = mcnh_trace(BYS2004)
    seq = patterns_from_arcs(BYS2004, trace["arcs"], rule)
    assert [p + 1 for p in seq] == BYS2004_SEQUENCE
    assert count_open_stacks(BYS2004, seq) == BYS2004_FIG2
    assert max(BYS2004_FIG2) == BYS2004_XI == 4


def test_paper_check_reports_every_match():
    result = paper_check(verbose=False)
    for key, value in result.items():
        if key.endswith("_match") or ":" in key and not key.startswith("sequence:"):
            assert value is True, key


def test_first_loop_is_not_the_first_node_of_setv():
    """Node 3 heads SETV (degree 3, lowest index) but its cheapest arc costs
    3 + 4; node 4's arc to node 8 costs 3 + 3, and the paper traverses (4, 8).
    The reading `n1 = first of SETV` would give (3, 2) and is wrong."""
    trace = mcnh_trace(BYS2004)
    assert (trace["loops"][0]["n1"], trace["loops"][0]["n2"]) == (3, 7)


def test_chain_by_hand():
    """Path 0-1-2, one product per edge plus one per end. Both arcs have the
    same Ω pair (1, 2); SETV = [0, 2, 1]; n1 = 0, n2 = 1: arc (0, 1) opens 0
    and 1, closes 0. Then (1, 2). Products: the shared product {0,1} first
    (it contains the arc; the paper's P12-before-P3 tie-break), then the end
    product of 0, then {1,2}, then the end product of 2 -- two stacks, the
    optimum."""
    chain = MOSPInstance.from_matrix(
        [[1, 1, 0, 0],
         [0, 1, 1, 0],
         [0, 0, 1, 1]], name="chain3")
    trace = mcnh_trace(chain)
    assert trace["arcs"] == [(0, 1), (1, 2)]
    value, ordering = mcnh(chain)
    assert ordering == [1, 0, 2, 3]
    assert value == 2


def test_arcs_among_open_nodes_are_swept_after_each_chosen_arc():
    """A triangle: after the first arc both endpoints are open and the third
    node is not, so nothing is swept; the second chosen arc opens the third
    node and the sweep takes the last arc. One pattern per edge: 3 stacks."""
    triangle = MOSPInstance.from_matrix(
        [[1, 1, 0],
         [1, 0, 1],
         [0, 1, 1]], name="triangle")
    trace = mcnh_trace(triangle)
    assert len(trace["loops"]) == 2
    assert trace["loops"][1]["s"] == 3
    assert mcnh(triangle)[0] == 3


def test_patterns_with_no_arc_go_last_and_sequences_are_permutations():
    inst = MOSPInstance.from_matrix(
        [[1, 1, 0, 0, 0],
         [0, 1, 0, 0, 0],
         [0, 0, 0, 1, 0],   # isolated customer, one product of its own
         [0, 0, 0, 0, 0]], name="odd")
    for rule in ("nodes", "arcs"):
        value, ordering = mcnh(inst, pattern_rule=rule)
        assert sorted(ordering) == list(range(5))
        assert ordering[-2:] == [2, 4] or ordering[-2:] == [2, 4][::-1] or set(ordering[-3:]) >= {2, 4}
        assert value == max_open_stacks(inst, ordering)


def test_nodes_and_arcs_readings_agree_on_two_piece_patterns():
    rng = random.Random(11)
    for _ in range(40):
        n = rng.randint(3, 9)
        edges = {tuple(sorted(rng.sample(range(n), 2))) for _ in range(rng.randint(1, 12))}
        matrix = [[0] * len(edges) for _ in range(n)]
        for j, (a, b) in enumerate(sorted(edges)):
            matrix[a][j] = matrix[b][j] = 1
        inst = MOSPInstance.from_matrix(matrix, name="edges")
        assert mcnh(inst)[1] == mcnh(inst, pattern_rule="arcs")[1]


def test_unknown_pattern_rule_is_rejected():
    with pytest.raises(ValueError):
        patterns_from_arcs(BYS2004, [], rule="pieces")


def test_registered_and_not_the_default():
    assert "mcnh" in STRATEGIES and "mcnh-arcs" in STRATEGIES
    assert DEFAULT_STRATEGY != "mcnh"  # the default became rule+cs-dfs on 2026-09-28
    assert upper_bound(BYS2004, "mcnh")[0] == 4


def test_step_agreement_counts_on_the_paper_instance():
    """Along MCNh's own closing order the rule's keys are recomputed from the
    same state; counts are bounded by the number of steps with a choice, and
    the rule's own order agrees with itself on both keys at every step."""
    _, ordering = mcnh(BYS2004)
    closing = _customer_order_from_products(BYS2004, ordering)
    counts = step_agreement(BYS2004, closing)
    assert counts["steps"] == BYS2004.n_customers - 1
    assert 0 <= counts["agree_both"] <= counts["agree_key1"] <= counts["steps"]
    own = step_agreement(BYS2004, two_key_closing_order(BYS2004))
    assert own["agree_both"] == own["steps"]


def test_mcnh_is_deterministic_and_a_genuine_upper_bound():
    rng = np.random.default_rng(5)
    for _ in range(30):
        n, m = int(rng.integers(3, 9)), int(rng.integers(3, 9))
        matrix = (rng.random((n, m)) < 0.4).astype(int).tolist()
        inst = MOSPInstance.from_matrix(matrix, name="r")
        first, second = mcnh(inst), mcnh(inst)
        assert first == second
        assert first[0] == max_open_stacks(inst, first[1])
