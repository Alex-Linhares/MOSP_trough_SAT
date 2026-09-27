"""Guards on the SAT-side graph story (`learning.sat_story`).

The hand instance is `tests/test_graph_story.py`'s: products {0, 1, 2},
{2, 3} and {1, 2} on four customers. Its MOSP graph is a triangle with a
pendant, pathwidth 2, so the optimum is 3: the SAT decision must answer
`unsat` at 2 and `sat` at 3 on both backends. The third product is nested in
the first, so `decide_mosp`'s dominance step drops it before encoding -- the
formula for the hand instance and for the instance without that column are
the same, and so are the conflicts: the smallest statement of the finding
that the cover reaches the solver only through the reduced formula.
"""

import itertools
import time

import numpy as np
import pandas as pd
import pytest

from learning import sat_story
from learning.sat_story import (
    KILL_TOLERANCE,
    decide_conflicts,
    decide_seconds,
    encode_reduced,
    kill_verdict,
    ratio_table,
    select_jobs,
)
from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks

HAND = MOSPInstance.from_matrix(
    [[1, 0, 0], [1, 0, 1], [1, 1, 1], [0, 1, 0]], name="hand")
HAND_REDUCED = MOSPInstance.from_matrix(
    [[1, 0], [1, 0], [1, 1], [0, 1]], name="hand_reduced")


def _brute_optimum(instance: MOSPInstance) -> int:
    return min(max_open_stacks(instance, list(order))
               for order in itertools.permutations(range(instance.n_patterns)))


def test_hand_optimum_is_three():
    assert _brute_optimum(HAND) == 3
    assert _brute_optimum(HAND_REDUCED) == 3


def test_decide_conflicts_matches_the_optimum():
    below = decide_conflicts(HAND, 2, deadline_seconds=30)
    at = decide_conflicts(HAND, 3, deadline_seconds=30)
    assert below["status"] == "unsat"
    assert at["status"] == "sat"
    assert below["conflicts"] >= 0 and at["conflicts"] >= 0
    assert below["components"] == 1


def test_dominance_makes_the_reduced_formula_and_the_conflicts_equal():
    a = encode_reduced(HAND, 2)
    b = encode_reduced(HAND_REDUCED, 2)
    assert [m for _, m in a] == [2] == [m for _, m in b]
    assert [c.clauses for c, _ in a] == [c.clauses for c, _ in b]
    ca = decide_conflicts(HAND, 2, deadline_seconds=30)
    cb = decide_conflicts(HAND_REDUCED, 2, deadline_seconds=30)
    assert (ca["conflicts"], ca["clauses"], ca["vars"]) == (cb["conflicts"], cb["clauses"], cb["vars"])


def test_decide_seconds_agrees_on_both_sides():
    assert decide_seconds(HAND, 2, deadline_seconds=30)["status"] == "unsat"
    assert decide_seconds(HAND, 3, deadline_seconds=30)["status"] == "sat"


def test_decide_seconds_censors_at_the_deadline(monkeypatch):
    def slow(instance, k, backend):
        time.sleep(5)
        return {"status": "unsat", "seconds": 5.0}

    monkeypatch.setattr(sat_story, "_kissat_solve", slow)
    started = time.monotonic()
    out = decide_seconds(HAND, 2, deadline_seconds=0.3)
    assert out == {"status": "unknown", "seconds": 0.3}
    assert time.monotonic() - started < 3


def test_censored_conflict_call_is_a_lower_bound():
    # a deadline that has already passed: no chunk runs, the call is censored
    # and the count it reports is what was done, never a missing value
    out = decide_conflicts(HAND, 2, deadline_seconds=0.0)
    assert out["status"] == "unknown"
    assert out["conflicts"] == 0
    assert out["clauses"] > 0


def _pairs(conflicts, base=100, side="refute", method="greedy"):
    return pd.DataFrame({
        "side": side, "method": method, "n": 10,
        "c_status": "unsat", "base_c_status": "unsat",
        "c_conflicts": conflicts, "base_c_conflicts": base,
        "both_settled": True,
        "log_ratio_conflicts": np.log10(1 + np.asarray(conflicts, float)) - np.log10(1 + base),
    })


def test_ratio_table_arithmetic():
    t = ratio_table(_pairs([100, 110, 90]))
    row = t.iloc[0]
    assert row["pairs"] == 3 and row["settled"] == 3
    assert row["equal"] == 1
    assert row["within ±5%"] == pytest.approx(1 / 3)
    assert row["ratio median"] == pytest.approx(1.0)
    assert row["max"] == pytest.approx(111 / 101)
    assert row["min"] == pytest.approx(91 / 101)


def test_ratio_table_counts_censored_pairs_instead_of_dropping_them():
    p = _pairs([100, 100, 5000])
    p.loc[2, "c_status"] = "unknown"
    p.loc[2, "both_settled"] = False
    t = ratio_table(p).iloc[0]
    assert t["pairs"] == 3 and t["settled"] == 2 and t["variant censored"] == 1
    assert t["ratio median"] == pytest.approx(1.0)


def test_kill_verdict_reads_the_all_row():
    t = pd.DataFrame([{"side": "refute", "method": "all", "ratio median": 1.03, "MAD log10": 0.1, "settled": 50},
                      {"side": "witness", "method": "all", "ratio median": 0.8, "MAD log10": 0.2, "settled": 50}])
    v = kill_verdict(t)
    assert v["refute"]["within ±5%"] is True or v["refute"]["within ±5%"] == True  # noqa: E712 - numpy bool
    assert not v["witness"]["within ±5%"]
    assert KILL_TOLERANCE == 0.05


def test_select_jobs_builds_both_sides_for_every_variant():
    rec = pd.DataFrame([
        {"base_name": "b1", "cell": "c", "n": 10, "method": m, "k": k, "base_optimum": 4,
         "base_nodes_default": 7, "instance_name": f"b1__{m}{k}", "nodes_default": 7}
        for m in ("split", "merge", "greedy") for k in (0, 1)])
    rel = pd.DataFrame([{"base_name": "b1", "n": 10, "k": k, "instance_name": f"b1__relabel{k}",
                         "nodes_default": 7 + k} for k in (-1, 0, 1, 2)])
    jobs = select_jobs(rec, rel, per_n=5, per_method=1, per_base=2, sizes=(10,))
    assert len(jobs) == 2 * (1 + 3 + 2)
    assert set(jobs.side) == {"refute", "witness"}
    assert set(jobs[jobs.side == "refute"].kk) == {3} and set(jobs[jobs.side == "witness"].kk) == {4}
    assert jobs.kind.value_counts().to_dict() == {"relabel": 4, "recover": 6, "base": 2}
    assert set(jobs[jobs.kind == "recover"].k) == {0}
    assert "b1__relabel-1" not in set(jobs.instance_name)
