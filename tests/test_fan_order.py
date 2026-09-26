"""The `fan_order` flag on the complete search and the restricted DFS.

Plan 2 §2.5(a), loop0003 item 06 (`learning/fan_order.py`,
`reports/ml_nature.md` §20). The flag reorders equal-cost candidates by
remaining degree instead of customer index. Three things must hold:

- the default is unchanged: no flag and `fan_order="index"` visit the same
  nodes and return the same witness, in the Python and in the C, and the
  default reproduces the node counts recorded before the flag existed;
- the flag never changes a *status*: order decides which branches are visited
  first, never which are visited, so `sat`/`unsat` is invariant at every `k`
  under both configurations;
- the C under the flag is the Python under the flag, node for node.
"""

import random

import numpy as np
import pandas as pd
import pytest

from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from satisfiability.customer_search import decide
from satisfiability.heuristics import (
    FAN_ORDERS,
    _neighbour_masks,
    fan_sort_key,
    product_order_from_customers,
    restricted_dfs,
    upper_bound,
)
from satisfiability.native import decide_native, native_available

needs_native = pytest.mark.skipif(not native_available(),
                                  reason="the C search did not build here")

CONFIGS = ({}, {"better_move": True, "better_move_dominators": 0})


def _random(rng, max_customers=9, max_patterns=8):
    n = rng.randint(2, max_customers)
    m = rng.randint(1, max_patterns)
    density = rng.choice([0.2, 0.3, 0.5, 0.7])
    rows = [[1 if rng.random() < density else 0 for _ in range(m)] for _ in range(n)]
    return MOSPInstance.from_matrix(rows, name="t")


def _active(instance, order):
    """The C lists customers with no products as free moves; the Python omits
    them. Compare witnesses on the customers that can open a stack."""
    return None if order is None else [c for c in order if instance.customer_patterns(c)]


def test_the_sort_key_orders_ties_by_remaining_degree_then_index():
    """`fan_sort_key("degree")`: cheapest first, then most unclosed neighbours,
    then index; `"index"` is the tuple's own order."""
    # Star with centre 3: N[3] = {0,1,2,3}; leaves N[i] = {i, 3}. Plus 4 isolated.
    matrix = [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [1, 1, 1, 0],
        [0, 0, 0, 1],
    ]
    inst = MOSPInstance.from_matrix(matrix, name="star")
    masks = _neighbour_masks(inst)
    remaining = 0b11111
    # Equal costs so only the tie-break decides: (cost, customer).
    playable = [(2, 0), (2, 3), (2, 4), (2, 1)]
    by_index = sorted(playable, key=fan_sort_key("index", masks, remaining))
    assert by_index == [(2, 0), (2, 1), (2, 3), (2, 4)]
    by_degree = sorted(playable, key=fan_sort_key("degree", masks, remaining))
    # 3 has remaining degree 3, the leaves 1, the isolated customer 0.
    assert by_degree == [(2, 3), (2, 0), (2, 1), (2, 4)]
    # Once the centre is closed the leaves have remaining degree 0, like the
    # isolated customer, and the tie falls back to index.
    remaining_after = 0b10111
    later = [(2, 4), (2, 1), (2, 0)]
    assert sorted(later, key=fan_sort_key("degree", masks, remaining_after)) == \
        [(2, 0), (2, 1), (2, 4)]
    with pytest.raises(ValueError):
        fan_sort_key("random", masks, remaining)


def test_the_flag_reaches_the_python_fan():
    """The `branch` hook sees the candidate list in the flagged order."""
    matrix = [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [1, 1, 1, 0],
        [0, 0, 0, 1],
    ]
    inst = MOSPInstance.from_matrix(matrix, name="star")
    seen = {}

    def spy(closed, opened, playable):
        seen.setdefault("first", list(playable))
        return playable

    decide(inst, 4, branch=spy, fan_order="degree", subset_rule=False, definite_move=False)
    first = seen["first"]
    # At the root the leaves cost 2 (N = {leaf, 3}), the centre 4, customer 4 costs 1.
    assert first[0] == (1, 4)
    assert [c for _, c in first][1:] == [0, 1, 2, 3]   # ties at cost 2 by index: leaves all degree 1
    seen.clear()
    decide(inst, 4, branch=spy, fan_order="index", subset_rule=False, definite_move=False)
    assert seen["first"] == first


def test_an_unknown_fan_order_is_rejected():
    inst = MOSPInstance.from_matrix([[1, 1], [0, 1]], name="t")
    with pytest.raises(ValueError):
        decide(inst, 2, fan_order="random")
    with pytest.raises(ValueError):
        decide(inst, 2, fan_order="random", native=False)
    with pytest.raises(ValueError):
        restricted_dfs(inst, fan_order="random")


def test_the_default_is_index_and_is_unchanged_by_naming_it():
    """No flag and `fan_order="index"` are the same search: same status, nodes
    and witness, Python and C."""
    rng = random.Random(6)
    for _ in range(120):
        inst = _random(rng)
        for k in range(0, inst.n_customers + 1):
            for native in (False, True):
                bare = decide(inst, k, native=native)
                named = decide(inst, k, native=native, fan_order="index")
                assert (bare.status, bare.nodes, bare.order) == (named.status, named.nodes, named.order)


@pytest.mark.parametrize("config", CONFIGS, ids=("default", "csearch"))
def test_the_flag_never_changes_a_status(config):
    """At every k, both fan orders answer alike, and a `sat` witness under the
    flag simulates within k."""
    rng = random.Random(11)
    for _ in range(150):
        inst = _random(rng)
        for k in range(0, inst.n_customers + 1):
            index = decide(inst, k, **config)
            degree = decide(inst, k, fan_order="degree", **config)
            assert index.status == degree.status, (inst.matrix, k, index, degree)
            if degree.status == "sat":
                value = max_open_stacks(inst, product_order_from_customers(inst, degree.order))
                assert value <= k


@needs_native
def test_the_c_under_the_flag_is_the_python_under_the_flag():
    """Node for node, under the configurations the Python implements."""
    rng = random.Random(23)
    checked = differing = 0
    for _ in range(150):
        inst = _random(rng)
        for k in range(0, inst.n_customers + 1):
            for kwargs in ({}, {"memo": False, "old_move": False},
                           {"subset_rule": False, "definite_move": False, "memo": False}):
                py = decide(inst, k, native=False, fan_order="degree", **kwargs)
                c = decide_native(inst, k, fan_order="degree", **kwargs)
                assert c is not None
                assert (py.status, py.nodes) == (c.status, c.nodes)
                assert _active(inst, py.order) == _active(inst, c.order)
                checked += 1
                if decide(inst, k, native=False, **kwargs).nodes != py.nodes:
                    differing += 1
    assert checked > 1000
    # The flag is not a no-op: on some instance at some k it visits a
    # different number of nodes.
    assert differing > 0


def test_the_default_reproduces_the_counts_recorded_before_the_flag_existed():
    """Byte-for-byte: regenerate campaign instances and check `decide` without
    a flag visits exactly the recorded `nodes_default`, and `cs-dfs` returns
    the recorded `ub_cs_dfs`."""
    from learning.canonical import matrix_digest
    from learning.ensemble import Cell, generate
    from learning.fan_order import RESULTS_CSV

    if not RESULTS_CSV.exists():
        pytest.skip("campaign results not present")
    frame = pd.read_csv(RESULTS_CSV, low_memory=False)
    frame = frame[frame.certified.astype(bool) & (frame.status_default == "unsat")
                  & (frame.nodes_default > 50) & (frame.n <= 30)]
    sample = frame.sample(n=8, random_state=7)
    for row in sample.to_dict("records"):
        inst = generate(Cell(row["generator"], int(row["n"]), int(row["m"]), float(row["param"])),
                        int(row["index"]))
        assert matrix_digest(inst) == row["matrix_digest"]
        answer = decide(inst, int(row["optimum"]) - 1)
        assert answer.status == "unsat"
        assert answer.nodes == int(row["nodes_default"]), row["instance_name"]
        value, _ = upper_bound(inst, "cs-dfs")
        assert value == int(row["ub_cs_dfs"]), row["instance_name"]


def test_restricted_dfs_under_the_flag_is_still_a_bound_and_is_registered():
    """A valid upper bound at or below its seed, under both fan orders, and
    `cs-dfs+degree` is the flagged search."""
    rng = random.Random(5)
    for _ in range(40):
        inst = _random(rng, max_customers=12, max_patterns=10)
        active = [c for c in range(inst.n_customers) if inst.customer_patterns(c)]
        if not active:
            continue
        optimum = next(k for k in range(0, inst.n_customers + 1) if decide(inst, k).status == "sat")
        for fan in FAN_ORDERS:
            value, ordering = restricted_dfs(inst, fan_order=fan)
            assert sorted(ordering) == list(range(inst.n_patterns))
            assert value == max_open_stacks(inst, ordering)
            assert value >= optimum
        v_flag, _ = restricted_dfs(inst, fan_order="degree")
        v_reg, _ = upper_bound(inst, "cs-dfs+degree")
        assert v_flag == v_reg


def test_measure_and_tables_on_a_toy():
    """`measure` returns every column the tables read; the kill verdict and
    audit come out right on a frame built from it."""
    from learning.fan_order import (
        CONFIGS as CFG,
        audit_table,
        dfs_table,
        kill_verdict,
        measure,
        paired_table,
    )

    inst = MOSPInstance.from_matrix(
        [[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1], [1, 0, 0, 1]], name="c4")
    row = measure(inst, 3)
    for config in CFG:
        for fan in FAN_ORDERS:
            assert row[f"status_lo_{config}_{fan}"] == "unsat"
            assert row[f"status_hi_{config}_{fan}"] == "sat"
            assert row[f"witness_{config}_{fan}"] <= 3
    assert row["dfs_index"] == row["dfs_degree"] == 3
    row.update(source="campaign", instance_name="c4", cell="toy", n=4, m=4,
               col_mean=2.0, graph_cert="", ref_nodes_default=row["nodes_lo_default_index"],
               ref_status_default="unsat", ref_ub_cs_dfs=3, deadline=10.0, seconds_total=0.0)
    frame = pd.DataFrame([row] * 25)
    audit = audit_table(frame)
    assert (audit.lo_status_disagreements == 0).all()
    assert int(audit[audit.config == "default"].ref_counts_equal.iloc[0]) == 25
    assert int(audit[audit.config == "default"].ref_dfs_equal.iloc[0]) == 25
    table = paired_table(frame, "lo", "default")
    assert list(table.band) == ["campaign 4"]
    assert table.paired.iloc[0] == 25
    verdict = kill_verdict(frame)
    assert verdict["met"] is True
    # Make the degree arm 30% more expensive: the kill is no longer met.
    frame2 = frame.copy()
    frame2["nodes_lo_default_degree"] = (frame2["nodes_lo_default_index"] + 1) * 1.3 - 1
    verdict2 = kill_verdict(frame2)
    assert verdict2["default_met"] is False
    assert verdict2["met"] is False
    assert "campaign 4" in verdict2["default_bands_outside"]
    # A censored pair is excluded from the ratio and counted.
    frame3 = frame.copy()
    frame3.loc[0, "status_lo_default_degree"] = "unknown"
    t3 = paired_table(frame3, "lo", "default")
    assert t3.paired.iloc[0] == 24 and t3.censored.iloc[0] == 1
    assert len(dfs_table(frame)) == 2
