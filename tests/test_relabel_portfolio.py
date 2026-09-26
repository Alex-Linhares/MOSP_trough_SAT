"""Guards on the relabelling portfolio (`learning.relabel_portfolio`).

The module's claims rest on three small computations: the exact expected
minimum of k draws without replacement (order statistics), the cheap
statistics of a labelling, and the per-instance table that turns raw counts
into speed-ups while keeping censored calls apart. Each is checked on a
hand-computable case. Beside them: relabelling never changes a decision's
status on a hand-checked instance, and the race stage returns a portfolio row
with a winner when run two ways on a tiny instance.
"""

import numpy as np
import pandas as pd
import pytest

from learning.relabel_portfolio import (
    RELABELLINGS,
    _job,
    expected_min,
    kill_verdict,
    label_statistics,
    labellings,
    per_instance,
    race,
    race_table,
    speedup_table,
)
from mosp.instance import MOSPInstance
from satisfiability.customer_search import decide

# The spider of tests/test_differential.py: centre 0, three legs of two
# customers, one product per edge; a tree of pathwidth 2, optimum 3.
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


def test_expected_min_matches_the_hand_computation():
    # values 1..4, k = 2: P(min = 1) = 3/6, P(min = 2) = 2/6, P(min = 3) = 1/6
    assert expected_min([4, 1, 3, 2], 2) == pytest.approx(10 / 6)
    assert expected_min([4, 1, 3, 2], 1) == pytest.approx(2.5)      # k = 1: the mean
    assert expected_min([4, 1, 3, 2], 4) == pytest.approx(1.0)      # k = N: the minimum
    # against a brute-force average over all subsets
    from itertools import combinations

    vals = [7, 2, 9, 4, 11]
    for k in (2, 3):
        brute = np.mean([min(c) for c in combinations(vals, k)])
        assert expected_min(vals, k) == pytest.approx(brute)
    with pytest.raises(ValueError):
        expected_min([1, 2], 3)


def test_label_statistics_on_the_spider():
    stats = label_statistics(_spider())
    assert stats["deg_first"] == 3                    # the centre
    assert stats["root_choice_index"] == 2            # lowest index among the degree-1 leaves
    assert stats["root_choice_nbr_deg"] == 2.0        # its only neighbour, customer 1
    # degrees fall with index (3, 2, 1, 2, 1, 2, 1): negative rank correlation
    assert -1.0 <= stats["rho_index_degree"] < 0
    assert stats["rho_col_index_sum"] == 0.0          # every product has two customers: no spread


def test_labellings_are_the_identity_and_sixteen_seeded_relabellings():
    inst = _spider()
    labs = labellings(inst)
    assert len(labs) == 1 + RELABELLINGS
    assert labs[0] == ("identity", inst)
    assert [name for name, _ in labs[1:]] == [f"relabel{k}" for k in range(RELABELLINGS)]
    again = labellings(inst)
    for (_, a), (_, b) in zip(labs[1:], again[1:]):
        assert np.array_equal(a.matrix, b.matrix)     # seeded from the name


def test_relabelling_never_changes_a_status_on_the_spider():
    from learning.node_counts import refutation_kwargs

    for _, lab in labellings(_spider(), relabellings=6):
        kw = refutation_kwargs(lab, "csearch")
        assert decide(lab, OPTIMUM - 1, **kw).status == "unsat"
        assert decide(lab, OPTIMUM, **kw).status == "sat"


def test_job_returns_both_sides_with_statistics():
    job = {"source": "corpus", "instance_name": "spider", "matrix": SPIDER,
           "optimum": OPTIMUM, "cell": "test"}
    row = _job((job, "relabel3", None, True))
    assert row["status_lo"] == "unsat" and row["status_hi"] == "sat"
    assert row["witness_ok"] is True and row["witness_value"] == OPTIMUM
    assert row["labelling"] == "relabel3" and row["config"] == "csearch"
    assert "rho_index_degree" in row and "root_choice_index" in row


def _toy_rows() -> pd.DataFrame:
    rows = []
    for name, nodes, status in [("identity", 100, "unsat"), ("relabel0", 10, "unsat"),
                                ("relabel1", 20, "unsat"), ("relabel2", 30, "unsat"),
                                ("relabel3", 40, "unknown")]:
        rows.append({"base_name": "toy", "labelling": name, "source": "campaign", "cell": "c",
                     "n": 60, "m": 60, "optimum": 5, "status_lo": status, "nodes_lo": nodes,
                     "seconds_lo": nodes / 1000})
    return pd.DataFrame(rows)


def test_per_instance_speedups_and_censoring():
    inst = per_instance(_toy_rows(), "lo", ks=(2, 4))
    assert len(inst) == 1
    r = inst.iloc[0]
    assert r["identity"] == 100 and r["min"] == 10 and r["max"] == 40
    assert r["max_over_min"] == pytest.approx(41 / 11)
    assert r["identity_over_min"] == pytest.approx(101 / 11)
    # E[min of 2] over 1 + nodes = {11, 21, 31, 41}: (11*3 + 21*2 + 31) / 6
    emin2 = (11 * 3 + 21 * 2 + 31) / 6
    assert r["emin_2"] == pytest.approx(emin2 - 1)
    assert r["speedup_identity_2"] == pytest.approx(101 / emin2)
    assert r["speedup_identity_4"] == pytest.approx(101 / 11)
    assert r["core_efficiency_4"] == pytest.approx(101 / (4 * 11))
    # the censored call is the maximum, not the minimum: flagged, and not the min
    assert bool(r["censored_any"]) is True and bool(r["censored_min"]) is False
    assert bool(r["censored_identity"]) is False


def test_speedup_table_and_kill_verdict_on_the_toy():
    inst = per_instance(_toy_rows(), "lo", ks=(2, 4, 8, 16))
    # only four relabellings: k = 8 and 16 are absent, the table still builds
    table = speedup_table(inst)
    assert list(table.band) == ["campaign n=60"] and table.instances.iloc[0] == 1
    assert "min-of-8 vs identity median" not in table.columns
    verdict = kill_verdict(inst)
    assert verdict["instances"] == 0          # no min-of-8 column, so nothing to judge
    inst["speedup_identity_8"] = [1.2]
    verdict = kill_verdict(inst)
    assert verdict["instances"] == 1 and verdict["kill_met_all"] is True
    assert verdict["hard_instances"] == 0     # identity 100 nodes is below the hard threshold


def test_race_two_ways_on_the_spider(tmp_path):
    job = {"source": "corpus", "instance_name": "spider", "matrix": SPIDER,
           "optimum": OPTIMUM, "cell": "test"}
    out = tmp_path / "race.csv"
    frame = race([job], ways=2, deadline=30.0, early_stop=False, out=out,
                 identity_reference={"spider": {"nodes": 5.0, "seconds": 1.0, "status": "unsat"}})
    port = frame[frame.labelling == "portfolio"].iloc[0]
    assert port.status == "unsat" and port.winner in ("identity", "relabel0")
    assert int(port.finished) == 2
    assert set(frame[frame.labelling != "portfolio"].status) == {"unsat"}
    table = race_table(frame)
    assert len(table) == 1 and table.iloc[0]["finished unsat"] == 2
    assert "×" in table.iloc[0]["wall speed-up vs identity"]
    # appends, never rewrites
    race([job], ways=2, deadline=30.0, early_stop=True, out=out)
    assert (pd.read_csv(out).labelling == "portfolio").sum() == 2
