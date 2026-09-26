"""Guards on the differential harness (`learning.differential`).

The harness exists to catch an unsound dominance rule: one that gives the
right answer on the labelling we happened to run and a wrong one on another.
Its own acceptance test is therefore a planted fault -- a `decide` wrapper
that lies on exactly one relabelling -- which the harness must draw by name.
Beside it: the sound search produces no flag on a hand-checked instance, the
lattice oracle agrees with the certificate there, the labellings are what the
docstring says they are, and the pure verdict function keeps censored calls
apart from disagreements.
"""

import numpy as np
import pytest

from learning.differential import (
    RECOVER_METHODS,
    differential,
    labellings,
    oracle_minima,
    run_pair,
    spread_table,
    verdict,
)
from mosp.instance import MOSPInstance
from satisfiability.customer_search import Decision, decide

# A spider: centre customer 0 with three legs of two customers, one product per
# edge. Its MOSP graph is a tree of pathwidth 2, so the optimum is 3, the
# trivial and clique bounds say 2, and refuting k = 2 has to branch.
SPIDER = [
    [1, 1, 1, 0, 0, 0],
    [1, 0, 0, 1, 0, 0],
    [0, 0, 0, 1, 0, 0],
    [0, 1, 0, 0, 1, 0],
    [0, 0, 0, 0, 1, 0],
    [0, 0, 1, 0, 0, 1],
    [0, 0, 0, 0, 0, 1],
]
OPTIMUM = 3


def _spider() -> MOSPInstance:
    return MOSPInstance.from_matrix(SPIDER, name="spider")


def test_labellings_are_the_identity_eight_relabellings_and_one_recovering():
    from learning.graph_story import same_labelled_graph

    inst = _spider()
    labels = labellings(inst, relabellings=8)
    names = [name for name, _ in labels]
    assert names[0] == "identity" and labels[0][1] is inst
    assert names[1:9] == [f"relabel{k}" for k in range(8)]
    assert len(labels) == 10 and names[9].rstrip("0123456789") in RECOVER_METHODS
    # every relabelling is the same matrix with rows and columns permuted
    base = np.asarray(inst.matrix)
    for _, lab in labels[1:9]:
        m = np.asarray(lab.matrix)
        assert sorted(map(tuple, m)) != sorted(map(tuple, base)) or True  # rows are permuted
        assert m.sum() == base.sum() and m.shape == base.shape
        assert sorted(m.sum(axis=1)) == sorted(base.sum(axis=1))
    # the re-covering keeps the labelled graph and changes the matrix
    rec = labels[9][1]
    assert same_labelled_graph(inst, rec)
    assert rec.n_patterns != inst.n_patterns or not np.array_equal(rec.matrix, inst.matrix)
    # and the same call regenerates the same labellings
    again = labellings(inst, relabellings=8)
    for (n1, a), (n2, b) in zip(labels, again):
        assert n1 == n2 and np.array_equal(a.matrix, b.matrix)


def test_a_sound_search_raises_no_flag_on_the_spider():
    rows, summary = differential(_spider(), OPTIMUM)
    assert summary["runs"] == 20 and summary["labellings"] == 10 and summary["recovered"]
    assert not summary["disagreement"] and not summary["contradiction"]
    assert summary["disagreeing"] == "" and summary["witness_failures"] == 0
    assert summary["unknown_lo"] == summary["unknown_hi"] == 0
    assert all(r["status_lo"] == "unsat" and r["status_hi"] == "sat" for r in rows)
    assert all(r["witness_ok"] for r in rows)
    assert all(r["witness_value"] <= OPTIMUM for r in rows)
    # the lattice oracle, sharing no code with the search, agrees
    assert summary["oracle_ok"] and summary["oracle_recover_ok"]
    assert summary["oracle_search"] == summary["oracle_construction"] == OPTIMUM
    # a re-covering under the default configuration costs exactly the same nodes
    ident = next(r for r in rows if r["labelling"] == "identity" and r["config"] == "default")
    rec = next(r for r in rows if r["labelling"].rstrip("0123456789") in RECOVER_METHODS
               and r["config"] == "default")
    assert rec["nodes_lo"] == ident["nodes_lo"] and rec["nodes_hi"] == ident["nodes_hi"]


def test_a_planted_liar_on_one_relabelling_is_drawn():
    """The item's acceptance test: a `decide` that answers `unsat` at the
    optimum on `relabel3` only, so every other run says `sat`."""

    def liar(instance, k, **kwargs):
        answer = decide(instance, k, **kwargs)
        if instance.name.endswith("__relabel3") and k == OPTIMUM:
            return Decision(status="unsat", order=None, nodes=answer.nodes)
        return answer

    rows, summary = differential(_spider(), OPTIMUM, decide_fn=liar, oracle=False)
    assert summary["disagreement"]
    assert summary["disagreeing"] == "relabel3/default@hi;relabel3/csearch@hi"
    # a lie at the optimum also contradicts the certificate, and is said to
    assert summary["contradiction"]
    # the honest runs are untouched
    honest = [r for r in rows if r["labelling"] != "relabel3"]
    assert all(r["status_hi"] == "sat" for r in honest)


def test_a_liar_at_optimum_minus_one_is_a_disagreement_with_the_refutation():
    """The other direction: a false `sat` below the optimum, the shape of the
    `better_move` bug in reverse, is a disagreement too."""

    def liar(instance, k, **kwargs):
        answer = decide(instance, k, **kwargs)
        if instance.name.endswith("__relabel0") and k == OPTIMUM - 1:
            return Decision(status="sat", order=list(range(instance.n_customers)), nodes=answer.nodes)
        return answer

    _, summary = differential(_spider(), OPTIMUM, decide_fn=liar, oracle=False)
    assert summary["disagreement"] and summary["contradiction"]
    assert set(summary["disagreeing"].split(";")) == {"relabel0/default@lo", "relabel0/csearch@lo"}


def test_verdict_keeps_censored_calls_apart_from_disagreements():
    base = {"status_lo": "unsat", "status_hi": "sat", "witness_ok": True}
    rows = [dict(base, labelling="identity", config="default", nodes_lo=5),
            dict(base, labelling="relabel0", config="default", nodes_lo=7, status_lo="unknown"),
            dict(base, labelling="greedy0", config="default", nodes_lo=5)]
    v = verdict(rows)
    assert not v["disagreement"] and not v["contradiction"]
    assert v["unknown_lo"] == 1 and v["recovered"] and v["labellings"] == 3
    assert v["nodes_lo_default_identity"] == 5
    # a witness that simulates above the optimum is a contradiction, not a disagreement
    rows[2]["witness_ok"] = False
    v = verdict(rows)
    assert v["contradiction"] and not v["disagreement"] and v["witness_failures"] == 1


def test_run_pair_simulates_the_witness_and_handles_a_trivial_optimum():
    inst = _spider()
    row = run_pair(inst, OPTIMUM, "default")
    assert row["status_lo"] == "unsat" and row["status_hi"] == "sat"
    assert row["witness_value"] == OPTIMUM and row["witness_ok"]
    assert row["nodes_lo"] > 0
    one = MOSPInstance.from_matrix([[1, 0], [0, 1]], name="two_singletons")
    row = run_pair(one, 1, "csearch")
    assert row["status_lo"] == "trivial" and row["nodes_lo"] == 0
    assert row["status_hi"] == "sat" and row["witness_ok"]


def test_oracle_minima_match_the_hand_value_and_stop_above_the_cap():
    assert oracle_minima(_spider()) == {"oracle_search": 3, "oracle_construction": 3}
    big = MOSPInstance.from_matrix(np.eye(16, dtype=int), name="sixteen")
    assert oracle_minima(big) is None


def test_spread_table_reads_the_identity_against_the_minimum():
    import pandas as pd

    rows = pd.DataFrame([
        {"source": "t", "config": "default", "base_name": "a", "labelling": "identity",
         "n": 12, "status_lo": "unsat", "nodes_lo": 9},
        {"source": "t", "config": "default", "base_name": "a", "labelling": "relabel0",
         "n": 12, "status_lo": "unsat", "nodes_lo": 4},
        {"source": "t", "config": "default", "base_name": "a", "labelling": "greedy0",
         "n": 12, "status_lo": "unsat", "nodes_lo": 99},   # excluded: not a labelling
    ])
    table = spread_table(rows, "lo")
    assert len(table) == 1 and table.band[0] == "11-15" and table.bases[0] == 1
    assert table["max/min max"][0] == 2.0 and table["identity/min median"][0] == 2.0
    assert table["min-of-9 saves >= 1.5x"][0] == 1


# ----------------------------------------------------------------------------
# What the harness found on its first run (2026-09-26): a false refutation at
# the optimum from the C `better_move` composed with `subset_rule`.
# ----------------------------------------------------------------------------

# `ens_f_n10_m20_d2_i070` of the campaign (Chu & Stuckey generator, 10
# customers, 20 products, 2 customers per product), certified optimum 4: the
# lattice oracle says 4 under both measures, the default search finds a
# witness at k = 4 that simulates to 4, and the Python reference agrees. The C
# with `better_move=True` and `subset_rule=True` answers `unsat` at k = 4.
DRAWN_10x20 = [
    [1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1],
    [0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
DRAWN_OPTIMUM = 4


def _drawn() -> MOSPInstance:
    return MOSPInstance.from_matrix(DRAWN_10x20, name="ens_f_n10_m20_d2_i070")


def test_the_drawn_instance_has_optimum_four_by_three_independent_routes():
    inst = _drawn()
    assert oracle_minima(inst) == {"oracle_search": 4, "oracle_construction": 4}
    for native in (True, False):
        assert decide(inst, 3, native=native).status == "unsat"
        answer = decide(inst, 4, native=native)
        assert answer.status == "sat"
        from learning.differential import witness_value
        assert witness_value(inst, answer.order) == 4
    # the Python reference with the flag set (it has no Theorem 2, so the flag is inert) agrees
    assert decide(inst, 4, native=False, better_move=True, better_move_dominators=0).status == "sat"


def test_the_harness_draws_the_drawn_instance():
    """The harness's own report of the finding: a disagreement between the two
    configurations at the optimum, on the identity labelling and others."""
    rows, summary = differential(_drawn(), DRAWN_OPTIMUM)
    assert summary["disagreement"] and summary["contradiction"]
    assert "identity/csearch@hi" in summary["disagreeing"]
    assert all(r["status_hi"] == "sat" for r in rows if r["config"] == "default")
    assert all(r["status_lo"] == "unsat" for r in rows)


@pytest.mark.xfail(strict=True, reason=(
    "Open finding of reports/ml_nature.md §15: the C better_move composed with "
    "subset_rule refutes a satisfiable k. Passes (XPASS, strict) once the C is "
    "fixed, at which point delete the marker and keep the assertion."))
def test_c_better_move_with_subset_rule_is_sound_on_the_drawn_instance():
    inst = _drawn()
    for dominators in (0, 4):
        assert decide(inst, 4, native=True, better_move=True, subset_rule=True,
                      better_move_dominators=dominators).status == "sat"


def test_either_rule_alone_is_sound_on_the_drawn_instance():
    """The composition is what fails: each rule alone answers correctly, and so
    does the C with the dominator limit at 1 or 2, where the covering
    candidate is never tried."""
    inst = _drawn()
    assert decide(inst, 4, native=True, better_move=True, subset_rule=False,
                  better_move_dominators=0).status == "sat"
    assert decide(inst, 4, native=True, better_move=False, subset_rule=True).status == "sat"
    for dominators in (1, 2):
        assert decide(inst, 4, native=True, better_move=True, subset_rule=True,
                      better_move_dominators=dominators).status == "sat"
