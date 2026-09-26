"""Theorem 2's switch (`learning/theorem2.py`, plan 2 §2.5b, loop0003 item 07).

The module measures two arms of the complete search -- `better_move` off (the
default) and forced on -- on the same instance and scores the rules that
choose between them. Three things must hold: the arms never disagree on a
status, the off arm reproduces the counts recorded before this study, and
the scoring of a rule is the arithmetic it claims to be.
"""

import numpy as np
import pandas as pd
import pytest

from learning import theorem2 as t2
from mosp.instance import MOSPInstance
from satisfiability.customer_search import decide, sparse_enough_for_better_move


def _instance():
    # 6 customers, 5 products; optimum 3 (checked by the search below).
    matrix = [
        [1, 1, 0, 0, 0],
        [0, 1, 1, 0, 0],
        [0, 0, 1, 1, 0],
        [0, 0, 0, 1, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 1, 0, 0],
    ]
    return MOSPInstance.from_matrix(matrix, name="hexagon")


def _optimum(instance):
    k = 1
    while decide(instance, k).status != "sat":
        k += 1
    return k


def test_measure_records_both_arms_and_they_agree_on_every_status():
    inst = _instance()
    opt = _optimum(inst)
    row = t2.measure(inst, opt, deadline_seconds=30)
    assert row["hand_on"] == sparse_enough_for_better_move(inst)
    assert row["products_per_customer"] == pytest.approx(inst.matrix.sum() / inst.n_customers)
    for arm in t2.ARMS:
        assert row[f"status_lo_{arm}"] == "unsat"
        assert row[f"status_hi_{arm}"] == "sat"
        assert row[f"witness_{arm}"] <= opt
        assert row[f"nodes_lo_{arm}"] >= 0


def test_on_arm_is_the_fixed_c_with_every_candidate_a_dominator():
    """The on arm must be exactly `better_move=True, better_move_dominators=0`
    -- the `csearch` configuration with the switch forced -- so its counts are
    comparable with item 06's `csearch` counts where the hand rule was on."""
    assert t2.ARMS["off"] == {}
    assert t2.ARMS["on"] == {"better_move": True, "better_move_dominators": 0}
    inst = _instance()
    opt = _optimum(inst)
    a = decide(inst, opt - 1, **t2.ARMS["on"])
    b = decide(inst, opt - 1, better_move=True, better_move_dominators=0)
    assert (a.status, a.nodes) == (b.status, b.nodes) == ("unsat", a.nodes)


def _toy_rows():
    """Six instances: on saves on two, ties on two, costs on one, censored on one."""
    return pd.DataFrame({
        "source": ["campaign"] * 6, "instance_name": [f"i{i}" for i in range(6)],
        "n": [30] * 6, "m": [30] * 6, "col_mean": [3.0] * 6, "cell": ["c"] * 6,
        "hand_on": [True, True, False, False, True, False],
        "products_per_customer": [3.0, 4.0, 6.0, 7.0, 4.5, 8.0],
        "nodes_lo_off": [100, 50, 10, 10, 20, 1000], "nodes_lo_on": [80, 25, 10, 10, 40, 500],
        "status_lo_off": ["unsat"] * 5 + ["unsat"], "status_lo_on": ["unsat"] * 5 + ["unknown"],
        "seconds_lo_off": [0.1] * 6, "seconds_lo_on": [0.1] * 6,
        "nodes_hi_off": [1] * 6, "nodes_hi_on": [1] * 6,
        "status_hi_off": ["sat"] * 6, "status_hi_on": ["sat"] * 6,
        "seconds_hi_off": [0.0] * 6, "seconds_hi_on": [0.0] * 6,
        "optimum": [5] * 6, "witness_off": [5] * 6, "witness_on": [5] * 6,
        "ref_nodes_default": [100, 50, 10, 10, 20, 1000], "ref_status_default": ["unsat"] * 6,
    })


def test_paired_oracle_and_rule_arithmetic_by_hand():
    p = t2.paired(_toy_rows(), "lo")
    assert p.decided.tolist() == [True] * 5 + [False]
    assert p.oracle.tolist() == [1, 1, 0, 0, -1, 0]       # censored pair scores as a tie
    assert p.ratio.iloc[0] == pytest.approx(81 / 101)
    d = p[p.decided]
    assert t2.rule_nodes(d, np.zeros(5, bool)).sum() == 190          # always off
    assert t2.rule_nodes(d, np.ones(5, bool)).sum() == 165           # always on
    assert t2.rule_nodes(d, d.hand_on.to_numpy()).sum() == 80 + 25 + 10 + 10 + 40   # hand: on, on, off, off, on
    assert t2.rule_nodes(d, (d.oracle > 0).to_numpy()).sum() == 80 + 25 + 10 + 10 + 20
    assert t2.agreement_with_oracle(d, d.hand_on.to_numpy()) == pytest.approx(4 / 5)
    assert t2.agreement_with_oracle(d, np.ones(5, bool)) == pytest.approx(4 / 5)
    assert t2.agreement_with_oracle(d, (d.oracle > 0).to_numpy()) == 1.0
    table = t2.rules_table(p, np.zeros(6, bool))
    r = table.iloc[0]
    assert r.paired == 5 and r.always_off_nodes == 190 and r.hand_nodes == 165 and r.oracle_regret == 1.0
    assert r.hand_regret == pytest.approx(165 / 145)
    sweep = t2.hand_threshold_sweep(p, thresholds=[4.0, 5.0])
    assert sweep.nodes.tolist() == [80 + 25 + 10 + 10 + 20, 165]
    s = t2.paired_table(_toy_rows(), "lo", ("band",)).iloc[0]
    assert (s.instances, s.paired, s.censored, s.saves, s.ties, s.costs) == (6, 5, 1, 2, 2, 1)


def test_kill_verdict_counts_agreement_with_the_hand_threshold():
    p = t2.paired(_toy_rows(), "lo")
    same = p.hand_on.to_numpy()
    assert t2.kill_verdict(p, same)["met"] is True
    flipped = same.copy()
    flipped[0] = False
    v = t2.kill_verdict(p, flipped)
    assert v["agreement"] == pytest.approx(5 / 6) and v["met"] is False
    assert v["hand_on_learned_off"] == 1 and v["hand_off_learned_on"] == 0


def test_tree_recovers_a_planted_threshold_out_of_fold():
    """Plant: on beats off iff products per customer ≤ 4. A depth-3 tree on the
    size-free design must recover it and disagree with the hand rule (5)
    exactly on the instances between 4 and 5."""
    rng = np.random.default_rng(0)
    n = 600
    ppc = rng.uniform(1, 10, n)
    on_wins = ppc <= 4.0
    off = rng.integers(100, 10_000, n).astype(float)
    on = np.where(on_wins, off * 0.7, off * 1.3)
    rows = pd.DataFrame({
        "source": "campaign", "instance_name": [f"s{i}" for i in range(n)], "n": 30, "m": 30,
        "col_mean": ppc, "cell": [f"cell{i % 10}" for i in range(n)],
        "hand_on": ppc <= 5.0, "products_per_customer": ppc,
        "nodes_lo_off": off, "nodes_lo_on": on, "status_lo_off": "unsat", "status_lo_on": "unsat",
        "seconds_lo_off": 0.0, "seconds_lo_on": 0.0,
    })
    p = t2.paired(rows, "lo")
    X = pd.DataFrame({"products_per_customer": ppc, "noise": rng.normal(size=n)})
    groups = np.arange(n) % 10
    learned = t2.learned_out_of_fold(X, p, groups, folds=5)
    assert (learned == on_wins).mean() > 0.97
    v = t2.kill_verdict(p, learned)
    between = ((ppc > 4.0) & (ppc <= 5.0)).mean()
    assert v["agreement"] == pytest.approx(1 - between, abs=0.03)
    tree = t2.fit_tree(X, p)
    text = t2.tree_text(tree, list(X.columns))
    assert "products_per_customer" in text


def test_the_off_arm_reproduces_recorded_default_counts():
    """The default arm of this study is `decide` with no flags: it must equal
    the `nodes_default` the campaign recorded, node for node."""
    from learning.fan_order import _materialise

    frame = pd.read_csv(t2.RESULTS_CSV, low_memory=False)
    frame = frame[frame.certified.astype(bool) & (frame.n == 20) & (frame.nodes_default > 50)]
    sample = frame.sample(4, random_state=1)
    for row in sample.to_dict("records"):
        job = {"source": "campaign", **{c: row[c] for c in ("generator", "n", "m", "param", "index",
                                                             "matrix_digest", "instance_name")}}
        inst = _materialise(job)
        measured = t2.measure(inst, int(row["optimum"]), deadline_seconds=30)
        assert measured["status_lo_off"] == "unsat"
        assert measured["nodes_lo_off"] == int(row["nodes_default"])
        assert measured["status_lo_on"] == "unsat"


def test_targets_keep_only_settled_default_refutations_above_100():
    jobs = t2.targets(campaign_max_n=0, corpus_max_n=125, source="corpus")
    big = [j for j in jobs if j["n"] > 100]
    assert big and all(j["ref_status_default"] == "unsat" for j in big)
    assert all(t2.deadline_for(j) == t2.LARGE_DEADLINE for j in big)
    assert t2.deadline_for({"source": "campaign", "n": 75}) == t2.CAMPAIGN_DEADLINE
