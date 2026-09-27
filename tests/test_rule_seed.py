"""The two-key rule as a registered heuristic and as the DFS seed
(`rule`, `rule+cs-dfs` in `satisfiability/heuristics.py`; `learning.rule_seed`).

Nothing here touches solver defaults or `solutions/`: the sweep test writes to
a temporary solutions directory and a temporary ledger.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import pytest

from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from satisfiability.heuristics import (
    DEFAULT_STRATEGY,
    STRATEGIES,
    product_order_from_customers,
    rule_then_dfs,
    two_key_closing_order,
    two_key_rule,
    upper_bound,
)

# Three customers on four products: 0 needs {0,1}, 1 needs {1,2}, 2 needs {2,3}.
# The MOSP graph is the path 0-1-2; the optimum is 2.
CHAIN3 = MOSPInstance.from_matrix(
    [[1, 1, 0, 0],
     [0, 1, 1, 0],
     [0, 0, 1, 1]], name="chain3")

# Becceneri, Yanasse & Soma (2004), Table 1: fourteen patterns (rows there) on
# eight piece types (columns there). Our convention is rows = customers, so
# the instance is the transpose. Their Minimal Cost Node heuristic reports
# ξ' = 4 with the printed sequence P11, P10, P14, P2, P4, P6, P12, P3, P9, P1,
# P7, P5, P8, P13, and 4 is the optimum (the complete customer search refutes
# 3 at zero nodes).
_BYS_PATTERNS = [
    [1, 1, 1, 0, 0, 0, 0, 0],
    [1, 0, 0, 1, 0, 0, 0, 0],
    [1, 0, 0, 0, 1, 0, 0, 0],
    [1, 0, 0, 0, 0, 1, 0, 0],
    [1, 0, 0, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [0, 1, 0, 0, 1, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 1, 0],
    [0, 0, 1, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 1, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 1],
    [0, 0, 0, 0, 1, 1, 0, 0],
    [0, 0, 0, 0, 1, 0, 1, 0],
    [0, 0, 0, 0, 0, 1, 0, 1],
]
BYS2004 = MOSPInstance.from_matrix(
    np.array(_BYS_PATTERNS).T.tolist(), name="becceneri-2004-table-1")
BYS2004_SEQUENCE = [p - 1 for p in (11, 10, 14, 2, 4, 6, 12, 3, 9, 1, 7, 5, 8, 13)]
BYS2004_OPTIMUM = 4


def test_two_key_order_on_the_chain_by_hand():
    # Step 1: ends 0 and 2 open two stacks each, customer 1 three; the ends
    # tie on unclosed neighbours (1) and products (2); index picks 0.
    # Step 2: closing 1 or 2 each opens one new stack (customer 2), both have
    # one unclosed neighbour; customer 1 has one product left against two.
    assert two_key_closing_order(CHAIN3) == [0, 1, 2]
    value, ordering = two_key_rule(CHAIN3)
    assert ordering == [0, 1, 2, 3]
    assert value == 2
    assert rule_then_dfs(CHAIN3) == (2, [0, 1, 2, 3])


def test_second_key_prefers_the_most_unclosed_neighbours():
    """A 4-cycle 0-1-2-3-0, one product per edge. After closing 0 (index
    breaks the all-way tie), customers 1, 2 and 3 each open exactly one new
    stack -- customer 2's -- so the first key ties. Customer 2 has two
    unclosed neighbours (1 and 3), customers 1 and 3 have one each (0 is
    closed). The rule closes 2; MCN's minimum-degree tie-break would close 1
    (`learning.distil`'s one-key hypothesis gives [0, 1, 2, 3])."""
    cycle4 = MOSPInstance.from_matrix(
        [[0, 0, 1, 1],
         [0, 1, 0, 1],
         [1, 1, 0, 0],
         [1, 0, 1, 0]], name="cycle4")
    assert two_key_closing_order(cycle4) == [0, 2, 1, 3]
    value, ordering = two_key_rule(cycle4)
    assert value == max_open_stacks(cycle4, ordering) == 3   # pathwidth(C4) + 1


def test_rule_reproduces_the_distil_rule():
    distil = pytest.importorskip("learning.distil")
    key = distil.lex_key(distil.HYPOTHESES[distil.HYPOTHESIS_RULE])
    rng = np.random.default_rng(7)
    for _ in range(60):
        n, m = int(rng.integers(3, 12)), int(rng.integers(3, 12))
        matrix = (rng.random((n, m)) < rng.uniform(0.15, 0.6)).astype(int)
        inst = MOSPInstance.from_matrix(matrix.tolist(), name="r")
        assert two_key_closing_order(inst) == distil.greedy_closing_order(inst, key)


def test_paper_example_reproduces_the_printed_value():
    assert max_open_stacks(BYS2004, BYS2004_SEQUENCE) == BYS2004_OPTIMUM
    for name in ("rule", "rule+cs-dfs", "mcn", "cs-dfs"):
        value, ordering = upper_bound(BYS2004, name)
        assert value == max_open_stacks(BYS2004, ordering)
        assert value == BYS2004_OPTIMUM


def test_paper_example_optimum_is_four():
    from satisfiability.customer_search import decide

    assert decide(BYS2004, BYS2004_OPTIMUM).status == "sat"
    assert decide(BYS2004, BYS2004_OPTIMUM - 1).status == "unsat"


def test_registered_and_not_the_default():
    assert "rule" in STRATEGIES and "rule+cs-dfs" in STRATEGIES
    assert DEFAULT_STRATEGY == "mcn+tabu"
    from satisfiability.customer_search import solve
    import inspect
    assert inspect.signature(solve).parameters["upper_strategy"].default == "cs-dfs"


def test_seeded_dfs_never_reports_above_its_seed():
    rng = np.random.default_rng(3)
    for _ in range(30):
        n, m = int(rng.integers(4, 12)), int(rng.integers(4, 12))
        matrix = (rng.random((n, m)) < 0.35).astype(int)
        inst = MOSPInstance.from_matrix(matrix.tolist(), name="s")
        seed_value, _ = two_key_rule(inst)
        dfs_value, ordering = rule_then_dfs(inst)
        assert dfs_value == max_open_stacks(inst, ordering)
        assert dfs_value <= seed_value


def test_rule_skips_customers_with_no_products():
    inst = MOSPInstance.from_matrix(
        [[1, 1], [0, 0], [0, 1]], name="empty-row")
    assert 1 not in two_key_closing_order(inst)
    value, ordering = two_key_rule(inst)
    assert sorted(ordering) == [0, 1]
    assert value == max_open_stacks(inst, ordering)


def test_sweep_writes_a_ledger_row_and_nothing_to_solutions(tmp_path: Path):
    """`learning.corpus_sweep.run` with `rule+cs-dfs`: one ledger row per
    instance in the scoring ledger, saves only into the temporary solutions
    directory it was given."""
    from learning.corpus_sweep import run

    instance_dir = tmp_path / "instances"
    instance_dir.mkdir()
    (instance_dir / "chain.txt").write_text(
        "chain3\n3 4\n1 1 0 0\n0 1 1 0\n0 0 1 1\n")
    solutions = tmp_path / "solutions"
    ledger = tmp_path / "ledger.csv"
    before = {p.name for p in Path("solutions").glob("*.json")} if Path("solutions").exists() else set()

    summary, rows = run("rule+cs-dfs", workers=1, instance_dir=instance_dir,
                        solutions_dir=solutions, ledger=ledger, verbose=False)

    assert summary["strategy"] == "rule+cs-dfs"
    assert len(rows) == 1
    name, cached, achieved, seconds, note = rows[0]
    assert cached is None and achieved == 2
    with ledger.open() as fh:
        ledger_rows = list(csv.DictReader(fh))
    assert len(ledger_rows) == 1
    assert ledger_rows[0]["driver"] == "reheuristic"
    assert ledger_rows[0]["instance"] == name
    assert float(ledger_rows[0]["seconds"]) >= 0
    saved = list(solutions.glob("*.json"))
    assert len(saved) == 1
    assert json.loads(saved[0].read_text())["mosp_value"] == 2
    after = {p.name for p in Path("solutions").glob("*.json")} if Path("solutions").exists() else set()
    assert after == before


def test_union_fold_assignment_keeps_a_class_in_one_fold(tmp_path: Path):
    from learning.rule_seed import union_fold_assignment

    canonical = tmp_path / "canonical.csv"
    canonical.write_text(
        "instance_name,source_file,graph_cert\n"
        "a1,f1,c1\n" "a2,f1,c2\n"
        "b1,f2,c2\n"              # f2 shares class c2 with f1 -> same group
        "c1,f3,c3\n" "c2,f3,c3\n" "c3,f3,c3\n"
        "d1,f4,c4\n"
        "e1,f5,c5\n"
    )
    assignment = union_fold_assignment(folds=3, seed=0, canonical=canonical)
    assert set(assignment) == {"f1", "f2", "f3", "f4", "f5"}
    assert assignment["f1"] == assignment["f2"]
    assert set(assignment.values()) <= {0, 1, 2}
    # Largest group first to the emptiest fold: f3 (3 rows) and f1∪f2 (3 rows)
    # land in different folds, f4 and f5 fill the third and then the lightest.
    assert assignment["f3"] != assignment["f1"]
    assert assignment["f4"] not in (assignment["f1"], assignment["f3"])


def test_head_to_head_and_summary_arithmetic():
    import pandas as pd
    from learning.rule_seed import head_to_head, summary_table

    frame = pd.DataFrame({
        "instance": list("abcd"),
        "optimum": [3, 5, 4, 6],
        "sweep:x": [3, 6, 4, 8],
        "sweep:y": [4, 5, 4, 8],
        "ms:x": [1.0, 2.0, 3.0, 4.0],
        "ms:y": [2.0, 2.0, 2.0, 2.0],
        "n_customers": [5, 5, 5, 5],
    })
    s = summary_table(frame, ("x", "y")).set_index("strategy")
    assert s.loc["x", "exact"] == 0.5 and s.loc["x", "worst"] == 2
    assert s.loc["x", "total overshoot"] == 3 and s.loc["y", "total overshoot"] == 3
    assert s.loc["x", "ms/instance (mean)"] == 2.5
    h = head_to_head(frame, (("x", "y"),)).iloc[0]
    assert (h["better"], h["equal"], h["worse"]) == (1, 2, 1)
    assert h["stacks saved"] == 1 and h["stacks lost"] == 1
    assert h["first exact where second misses"] == 1 and h["both miss"] == 1
