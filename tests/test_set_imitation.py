"""Tests for `learning.set_imitation` (loop0003 item 10)."""

from __future__ import annotations

import json
import random

import numpy as np
import pandas as pd
import pytest

from benchmarks.generator import generate_random_instance
from learning import set_imitation as si
from learning.degeneracy import Compact, closing_weights, lattice_counts, lattice_minimum, witness_choices
from learning.distil import HYPOTHESES, HYPOTHESIS_RULE, greedy_closing_order, lex_key
from mosp.instance import MOSPInstance
from satisfiability.heuristics import _neighbour_masks

# Three customers on a path: 0 needs {0,1}, 1 needs {1,2}, 2 needs {2,3}.
PATH = MOSPInstance.from_matrix([[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1]], name="p3")


def _random(seed: int) -> MOSPInstance:
    rng = random.Random(seed)
    n = rng.choice([5, 6, 7, 8])
    return generate_random_instance(n, rng.choice([n, 2 * n]), rng.choice([0.2, 0.35, 0.5]), seed=seed)


def test_popcount32_matches_int_bit_count():
    rng = np.random.default_rng(0)
    x = rng.integers(0, 2**32, 10_000, dtype=np.uint64).astype(np.uint32)
    x[:3] = [0, 1, 0xFFFFFFFF]
    expected = np.array([int(v).bit_count() for v in x], dtype=np.int8)
    assert np.array_equal(si.popcount32(x), expected)


def test_lattice_on_the_path_by_hand():
    lat = si.Lattice(PATH)
    assert lat.optimum == 2
    # closing 1 first opens all three stacks (cost 3); 0 or 2 first costs 2
    assert lat.optimal_choices(0) == [0, 2]
    assert lat.good_moves(0, peak=0) == {0: True, 1: False, 2: True}
    # after the bad first move the achievable value is 3 and nothing worsens it
    S1 = lat.state([1])
    assert lat.good_moves(S1, peak=3) == {0: True, 2: True}
    assert int(lat.h[S1]) <= 2 and int(lat.w[0, lat.pos[1]]) == 3


@pytest.mark.parametrize("seed", range(8))
def test_lattice_matches_degeneracy_reference(seed):
    inst = _random(seed)
    comp = Compact(inst)
    _, cw = closing_weights(comp)
    lat = si.Lattice(inst)
    assert lat.customers == comp.customers
    a = comp.a
    assert np.array_equal(np.array(cw, dtype=np.int64).reshape(1 << a, a), lat.w.astype(np.int64))
    assert lattice_minimum(cw, a) == lat.optimum
    _, g = lattice_counts(cw, a, lat.optimum)
    order = list(range(inst.n_customers))
    random.Random(seed).shuffle(order)
    ref = witness_choices(comp, cw, lat.optimum, g, order)
    counts, optimal = si.witness_choice_counts(lat, order)
    assert counts == ref["choices"] and optimal == ref["optimal"]


def test_block_cost_and_order_value_agree_with_simulation():
    for seed in range(6):
        inst = _random(seed)
        mk = si.Masks(inst)
        order = list(mk.active)
        random.Random(seed).shuffle(order)
        assert mk.order_value(order) == si.construction_value(inst, order)
        assert mk.order_value(order, cap=0) == 1 or mk.order_value(order) == 0


def test_greedy_rule_equals_distil_rule():
    key = lex_key(HYPOTHESES[HYPOTHESIS_RULE])
    for seed in range(6):
        inst = _random(seed)
        assert si.greedy_order(inst, si.rule_key) == greedy_closing_order(inst, key)


def test_constant_model_with_rule_ties_is_the_rule():
    zero = si.score_key_rule_ties(lambda F: np.zeros(len(F)))
    for seed in range(4):
        inst = _random(seed)
        assert si.greedy_order(inst, zero) == si.greedy_order(inst, si.rule_key)


def test_extended_matrix_ranks_the_rule_pick_first():
    inst = _random(3)
    mk = si.Masks(inst)
    nb = _neighbour_masks(inst)
    X = si.candidate_matrix(nb, mk.n, mk.prod, 0, 0, 0, mk.active)
    E = si.extended_matrix(X, peak_so_far=0)
    assert E.shape == (len(mk.active), len(si.FEATURE_NAMES))
    rank = E[:, si.FEATURE_NAMES.index("rule_rank")]
    assert int(np.argmin(rank)) == si.pick_min(si._RULE_KEY(X))
    assert E[:, si.FEATURE_NAMES.index("rel_newly_opened")].min() == 0
    assert (E[:, si.FEATURE_NAMES.index("n_candidates")] == len(mk.active)).all()


def test_label_states_on_the_path():
    lat = si.Lattice(PATH)
    X, y, step, stats = si.label_states(PATH, lat, {"witness": [0, 1, 2], "bad": [1, 0, 2]}, rollouts=0)
    # states: {} (3 candidates), {0} (2), {1} (2, reached with peak 3) -- {0,1} has one candidate
    assert stats["states"] == 3 and len(y) == 7
    s0 = step == step[0]
    assert y[s0].tolist() == [1, 0, 1]           # candidates 0, 1, 2 from the empty state
    assert stats["rule_good"] >= 2               # the rule never picks customer 1 first
    assert X.shape[1] == len(si.FEATURE_NAMES)


def test_bounded_choices_on_the_path():
    res = si.bounded_choices(PATH, 2, [0, 1, 2], nodes=50)
    assert res["confirmed"] == [2, 2] and res["unknown"] == [0, 0] and not res["censored"]
    assert sum(res["by_suffix"]) + sum(res["by_dfs"]) == 4


def test_bounded_completes_budget_exhaustion_is_not_an_answer():
    mk = si.Masks(PATH)
    assert si.bounded_completes(mk, 0, 0, 0, 0, 2, [50]) is True
    assert si.bounded_completes(mk, 0, 0, 0, 0, 1, [50]) is False      # optimum is 2
    assert si.bounded_completes(mk, 0, 0, 0, 0, 2, [0]) is False       # no nodes: unknown


def test_bounded_confirmations_never_exceed_exact_counts():
    for seed in range(6):
        inst = _random(seed)
        lat = si.Lattice(inst)
        order = list(lat.customers)
        random.Random(seed).shuffle(order)
        # walk an optimal order so every step has an exact count
        S, opt = 0, []
        for _ in range(lat.a):
            c = lat.optimal_choices(S)[0]
            opt.append(c)
            S |= 1 << lat.pos[c]
        exact, is_opt = si.witness_choice_counts(lat, opt)
        assert is_opt
        res = si.bounded_choices(inst, lat.optimum, opt, nodes=100)
        conf = res["confirmed"]
        assert len(conf) == len(exact) - 1        # the exact list includes the forced last step
        for lo, ex in zip(conf, exact):
            assert 1 <= lo <= ex


def test_assign_folds_balances_groups():
    groups = np.array([0] * 50 + [1] * 30 + [2] * 10 + [3] * 10 + [4] * 5 + [5] * 5)
    folds = si.assign_folds(groups, folds=3, seed=1)
    frame = pd.DataFrame({"g": groups, "f": folds})
    assert (frame.groupby("g")["f"].nunique() == 1).all()
    sizes = frame.groupby("f").size()
    assert len(sizes) == 3 and sizes.max() <= 50


def test_summary_and_bands_on_a_toy_frame():
    ev = pd.DataFrame({"optimum": [3, 4, 5, 6], "n_customers": [10, 20, 30, 80],
                       "rule": [3, 5, 5, 8], "mcn": [4, 4, 7, 9], "group": [0, 0, 1, 2]})
    s = si.summary(ev, ["rule", "mcn"]).set_index("strategy")
    assert s.loc["rule", "MAE"] == pytest.approx(0.75) and s.loc["rule", "exact"] == 0.5
    assert s.loc["mcn", "worst"] == 3
    b = si.by_band(ev, ["rule", "mcn"])
    assert list(b["customers"]) == ["9–15", "16–20", "21–40", "76–134"]
    h = si.head_to_head(ev, [("rule", "mcn")]).iloc[0]
    assert (h["better"], h["equal"], h["worse"]) == (3, 0, 1)
    g = si.grouped_mae(ev, "rule", "mcn")
    assert g["MAE diff"] == pytest.approx(0.75 - 1.5) and g["groups"] == 3
