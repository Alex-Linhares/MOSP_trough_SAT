"""`learning.distil` on instances and frames small enough to check by hand.

Nothing here touches the solver's defaults, the corpus or `solutions/`.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from learning.distil import (
    COL,
    MCN_KEY,
    STATIC_RULES,
    _step_agreement,
    add_selected,
    bfs_order,
    candidate_matrix,
    decision_rows,
    effective_weights,
    elimination_order,
    fiedler_order,
    gain_kept,
    greedy_closing_order,
    lex_family,
    lex_key,
    lex_name,
    pick_min,
    rounded_weights,
    select_lex,
    summary,
    weights_key,
)
from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from satisfiability.heuristics import _neighbour_masks, product_order_from_customers, upper_bound

pytest.importorskip("sklearn")

# A path on four customers, one product per edge: 0-1, 1-2, 2-3.
PATH4 = MOSPInstance.from_matrix(
    [[1, 0, 0],
     [1, 1, 0],
     [0, 1, 1],
     [0, 0, 1]], name="path4")

# A star: customer 1 shares one product with each of 0, 2 and 3.
STAR = MOSPInstance.from_matrix(
    [[1, 0, 0],
     [1, 1, 1],
     [0, 1, 0],
     [0, 0, 1]], name="star")

# Three customers on four products: 0 needs {0,1}, 1 needs {1,2}, 2 needs {2,3}.
CHAIN3 = MOSPInstance.from_matrix(
    [[1, 1, 0, 0],
     [0, 1, 1, 0],
     [0, 0, 1, 1]], name="chain3")


def _random_instance(rng, n=8, m=8):
    while True:
        matrix = (rng.random((n, m)) < 0.35).astype(int)
        if matrix.sum(axis=0).min() > 0 and matrix.sum(axis=1).min() > 0:
            return MOSPInstance.from_matrix(matrix.tolist(), name="rand")


def test_pick_min_is_lexicographic_first_column_most_significant():
    keys = np.array([[2.0, 1.0], [1.0, 5.0], [1.0, 2.0]])
    assert pick_min(keys) == 2
    assert pick_min(np.array([3.0, 1.0, 2.0])) == 1


def test_candidate_matrix_counts_products_not_yet_produced():
    masks = _neighbour_masks(CHAIN3)
    pmasks = [0b0011, 0b0110, 0b1100]
    # Customer 0 closed: products 0 and 1 produced, customers 0 and 1 opened.
    X = candidate_matrix(masks, 3, pmasks, closed=0b001, opened=0b011,
                         produced=0b0011, candidates=[1, 2])
    assert X[:, COL["patterns"]].tolist() == [1.0, 2.0]
    assert X[:, COL["index"]].tolist() == [1.0, 2.0]
    assert X[:, COL["already_open"]].tolist() == [1.0, 0.0]


def test_the_empty_rule_is_mcn_and_agrees_with_the_solver_heuristic():
    # On CHAIN3 the two ends tie on degree and products; the index picks 0,
    # then customer 1 (one product left) beats customer 2 (two left).
    assert greedy_closing_order(CHAIN3, lex_key([])) == [0, 1, 2]
    assert lex_name([]) == "mcn"
    rng = np.random.default_rng(0)
    for _ in range(25):
        inst = _random_instance(rng)
        order = greedy_closing_order(inst, lex_key([]))
        ours = max_open_stacks(inst, product_order_from_customers(inst, order))
        assert ours == upper_bound(inst, "mcn")[0]


def test_lex_key_sign_prefers_large_values_and_falls_back_to_mcn():
    masks = _neighbour_masks(STAR)
    pmasks = [0b001, 0b111, 0b010, 0b100]
    X = candidate_matrix(masks, 4, pmasks, 0, 0, 0, [0, 1, 2, 3])
    # Customer 1 has the largest degree; "max total_degree" closes it first.
    assert pick_min(lex_key([("total_degree", -1)])(X)) == 1
    # "min total_degree" ties the three leaves; MCN's key then picks index 0.
    assert pick_min(lex_key([("total_degree", 1)])(X)) == 0
    assert lex_name([("total_degree", -1), ("newly_opened", 1)]) == \
        "lex:max total_degree,min newly_opened"


def test_lex_family_counts_and_starts_with_mcn():
    family = lex_family(2, features=["a", "b", "c"])
    # empty + 3*2 singles + 3*2*4 ordered pairs
    assert len(family) == 1 + 6 + 24
    assert family[0] == []
    assert all(len({f for f, _ in rule}) == len(rule) for rule in family)


def test_static_orders_on_a_path_and_a_star():
    assert fiedler_order(PATH4) == [0, 1, 2, 3]
    assert fiedler_order(PATH4, reverse=True) == [3, 2, 1, 0]
    assert bfs_order(STAR) == [0, 1, 2, 3]          # min-degree root 0, then the hub
    assert bfs_order(STAR, reverse=True) == [3, 2, 1, 0]
    assert elimination_order(PATH4) == [0, 1, 2, 3]
    for rule in STATIC_RULES.values():
        assert sorted(rule(STAR)) == [0, 1, 2, 3]
        assert sorted(rule(PATH4)) == [0, 1, 2, 3]


def test_static_orders_skip_customers_with_no_products():
    inst = MOSPInstance.from_matrix([[1, 1], [0, 0], [1, 1]], name="idle")
    for rule in STATIC_RULES.values():
        assert sorted(rule(inst)) == [0, 2]
    assert sorted(greedy_closing_order(inst, lex_key([]))) == [0, 2]


def test_decision_rows_one_row_per_candidate_at_every_real_decision():
    corpus = [("f", PATH4, {"ordering": [0, 1, 2]})]
    X, y = decision_rows(corpus)
    # Witness closes 0, 1, 2, 3: decisions with 4, 3 and 2 candidates.
    assert X.shape == (9, 8)
    assert y.sum() == 3


def test_step_agreement_counts_imitation_and_fidelity():
    keys = {"lgbm": lex_key([]), "rev": lex_key([("total_degree", -1)])}
    counts = _step_agreement(PATH4, [0, 1, 2, 3], keys)
    assert counts["steps"] == 3
    assert counts["imit:lgbm"] == 3 and counts["fid:lgbm"] == 3
    # "max total_degree" closes an inner customer first: disagrees at step 1.
    assert counts["imit:rev"] < 3
    assert counts["fid:rev"] == counts["imit:rev"]


def test_weights_and_gain_arithmetic():
    w = {"remaining_degree": -1.0, "newly_opened": -0.5, "already_open": 2.0,
         "open_after": -0.5, "open_now": 3.0, "progress": 1.0,
         "total_degree": 0.0, "n_customers": 0.1}
    eff = effective_weights(w)
    assert eff == {"remaining_degree": -1.0, "newly_opened": -1.0,
                   "already_open": 2.0, "total_degree": 0.0}
    assert rounded_weights(eff) == {"remaining_degree": -0.5, "newly_opened": -0.5,
                                    "already_open": 1.0, "total_degree": 0.0}
    assert gain_kept(1.0, 2.0, 0.0) == 0.5
    assert gain_kept(2.0, 2.0, 0.0) == 0.0
    assert np.isnan(gain_kept(1.0, 1.0, 1.0))
    # A pure "already open first" scorer on CHAIN3 after closing 0 picks 1.
    masks = _neighbour_masks(CHAIN3)
    X = candidate_matrix(masks, 3, [0b0011, 0b0110, 0b1100], 0b001, 0b011, 0b0011, [1, 2])
    assert pick_min(weights_key({"already_open": 1.0})(X)) == 0


def test_summary_and_selection_on_a_hand_frame():
    frame = pd.DataFrame({
        "fold": [1, 1, 1, 1],
        "role": ["train", "train", "test", "test"],
        "n_customers": [5, 5, 5, 5],
        "optimum": [3, 3, 3, 3],
        "mcn": [5, 5, 5, 5],
        "lgbm": [3, 3, 3, 3],
        "lex:min newly_opened": [4, 4, 4, 4],
        "lex:max newly_opened": [3, 3, 6, 6],
    })
    rules = [[], [("newly_opened", 1)], [("newly_opened", -1)]]
    sel = select_lex(frame, rules)
    # Selected on the training rows, where "max" is exact; scored held out.
    assert sel.loc[0, "rule"] == "lex:max newly_opened"
    assert sel.loc[0, "train_mae"] == 0.0 and sel.loc[0, "held_out_mae"] == 3.0
    frame = add_selected(frame, sel)
    table = summary(frame, ["mcn", "lgbm", "lex:min newly_opened", "lex-selected"])
    by = dict(zip(table["strategy"], table["gain_kept"]))
    assert by["mcn"] == 0.0 and by["lgbm"] == 1.0
    assert by["lex:min newly_opened"] == pytest.approx(0.5)
    assert by["lex-selected"] == pytest.approx(-0.5)
    assert MCN_KEY == ("remaining_degree", "patterns", "index")
