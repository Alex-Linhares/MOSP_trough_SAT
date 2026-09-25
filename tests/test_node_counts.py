"""Node counts are a returned quantity and reach the ledger.

The complete customer search has always counted its branch decisions; until
2026-09-25 the count was printed by some drivers and stored by none, so the
hardness measure `reports/ml_nature_plan.md` §2.4 needs -- nodes, not seconds --
had no record. These tests pin every seam the count now crosses: the search's
own return value, `solve_mosp_exact`'s `stats`, the csearch sweep row, the
recertify worker, and the ledger's `nodes` column, including that older rows
get an empty cell rather than a zero.
"""

import csv
import json

import pytest

from benchmarks.compute import LEDGER_FIELDS, ensure_fields, record, totals
from mosp.instance import MOSPInstance

# A spider: centre customer 0 with three legs of two customers, one product per
# edge. A tree, so the trivial and clique bounds say 2; its pathwidth is 2, so
# the optimum is 3 and refuting k = 2 has to branch (the leaves cost 2 each).
SPIDER = [
    [1, 1, 1, 0, 0, 0],
    [1, 0, 0, 1, 0, 0],
    [0, 0, 0, 1, 0, 0],
    [0, 1, 0, 0, 1, 0],
    [0, 0, 0, 0, 1, 0],
    [0, 0, 1, 0, 0, 1],
    [0, 0, 0, 0, 0, 1],
]

# `p1010n10_0` from Faggioli & Bentivoglio: 9 customers, 10 products, certified
# optimum 6 against a best lower bound of 5, so `solve_mosp_exact` has to make
# a real refutation call rather than stop at the bound.
GAP_9x10 = [
    [0, 1, 0, 1, 0, 0, 0, 1, 0, 1], [0, 0, 1, 0, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 1, 0], [0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
    [1, 1, 0, 0, 1, 0, 1, 0, 0, 0], [0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 1, 0, 0, 0, 0, 0, 1, 0], [0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 0, 1, 1, 0, 1],
]


def test_a_tiny_refutation_returns_a_positive_count():
    """The item's own acceptance test: a tiny instance, a positive count, from
    both the Python and the C search, and the two agree."""
    from satisfiability.customer_search import decide, solve

    instance = MOSPInstance.from_matrix(SPIDER, name="spider")
    assert solve(instance).value == 3

    native = decide(instance, 2, native=True)
    python = decide(instance, 2, native=False)
    assert native.status == python.status == "unsat"
    assert native.nodes > 0
    assert native.nodes == python.nodes


def test_solve_mosp_exact_reports_its_nodes_without_changing_its_return(tmp_path):
    from satisfiability.mosp_solver import solve_mosp_exact

    instance = MOSPInstance.from_matrix(GAP_9x10, name="gap")
    stats: dict = {}
    value, ordering = solve_mosp_exact(instance, solutions_dir=tmp_path, stats=stats)

    assert value == 6 and len(ordering) == 10
    assert stats["proof"] == "refutation"
    assert stats["procedure"] == "csearch"
    assert stats["nodes"] > 0
    assert stats["seconds"] >= 0

    # The same call from the cache searched nothing, and must not say "0 nodes"
    # as if the instance were trivial.
    again: dict = {}
    assert solve_mosp_exact(instance, solutions_dir=tmp_path, stats=again) == (value, ordering)
    assert again["proof"] == "cached" and again["nodes"] is None

    # Without `stats`, nothing changes for the existing callers.
    assert solve_mosp_exact(instance, solutions_dir=tmp_path) == (value, ordering)


def test_the_ledger_writes_nodes_and_leaves_them_empty_where_unknown(tmp_path):
    ledger = tmp_path / "compute_ledger.csv"
    record("csearch", [("a", 12.0, 345), ("b", 1.0, 0)], ledger=ledger)
    record("reheuristic", [("c", 0.5)], ledger=ledger)          # no search behind it
    record("recertify", [("d", 7200.0, None)], ledger=ledger)   # failed before searching

    with ledger.open(newline="") as fh:
        reader = csv.DictReader(fh)
        assert tuple(reader.fieldnames) == LEDGER_FIELDS
        rows = list(reader)
    assert [r["nodes"] for r in rows] == ["345", "0", "", ""]
    # nodes are not compute: the total is unchanged by them
    assert totals(tmp_path)[0][1] == pytest.approx((12 + 1 + 0.5 + 7200) / 3600)


def test_an_older_ledger_gains_the_column_with_empty_cells_once(tmp_path):
    """Existing rows carry no count, and an empty cell says so where a zero
    would claim the search did nothing."""
    ledger = tmp_path / "compute_ledger.csv"
    ledger.write_text("when,driver,instance,seconds\n"
                      "2026-09-18T23:05:30,csearch,Random-100-100-10-2_0,2.0\n"
                      "2026-09-19T01:00:00,reheuristic,GP1,0.3\n")

    assert ensure_fields(ledger) == 1
    assert ensure_fields(ledger) == 0          # idempotent
    record("csearch", [("new", 3.0, 99)], ledger=ledger)

    rows = list(csv.DictReader(ledger.open(newline="")))
    assert [r["instance"] for r in rows] == ["Random-100-100-10-2_0", "GP1", "new"]
    assert [r["nodes"] for r in rows] == ["", "", "99"]
    assert [r["seconds"] for r in rows] == ["2.0", "0.3", "3.0"]


def test_the_csearch_sweep_puts_the_count_in_its_row_and_in_the_ledger(tmp_path):
    from benchmarks.csearch import sweep

    instance = MOSPInstance.from_matrix(GAP_9x10, name="gap")
    ledger = tmp_path / "ledger.csv"
    results = sweep([instance], timeout=30, workers=1, solutions_dir=tmp_path,
                    ledger=ledger, verbose=False)

    (name, before, after, seconds, note, nodes), = results
    assert (name, after, note) == ("gap", 6, "refutation")
    assert nodes > 0

    rows = list(csv.DictReader(ledger.open(newline="")))
    assert rows[0]["instance"] == "gap"
    assert int(rows[0]["nodes"]) == nodes


def test_the_recertify_worker_returns_nodes_and_records_a_row(tmp_path):
    from benchmarks.recertify import _record, _worker

    instance = MOSPInstance.from_matrix(GAP_9x10, name="gap")
    result = _worker((instance.matrix.tolist(), instance.n_customers,
                      instance.n_patterns, "gap", 6, 30.0))
    assert result["status"] == "unsat"
    assert result["nodes"] > 0

    ledger = tmp_path / "ledger.csv"
    _record(result, ledger)
    rows = list(csv.DictReader(ledger.open(newline="")))
    assert rows[0]["driver"] == "recertify"
    assert int(rows[0]["nodes"]) == result["nodes"]


def test_the_study_module_audits_and_summarises(tmp_path):
    """`learning.node_counts.refute` reports the search's verdict on the stored
    optimum -- `unsat` at optimum - 1 is agreement, `sat` would be a wrong
    value -- and the summary groups by size band with the counts intact."""
    import pandas as pd

    from learning.node_counts import ledger_summary, refute, summarise

    spider = MOSPInstance.from_matrix(SPIDER, name="spider")
    agreed = refute(spider, 3)
    assert agreed["status"] == "unsat" and agreed["nodes"] > 0
    too_high = refute(spider, 4)          # a wrongly stored optimum of 4
    assert too_high["status"] == "sat"

    frame = pd.DataFrame([
        {"instance_name": "spider", "collection": "toy", "n_customers": 7,
         "n_patterns": 6, "optimum": 3, **agreed},
        {"instance_name": "spider", "collection": "toy", "n_customers": 7,
         "n_patterns": 6, "optimum": 3, **{**agreed, "config": "csearch"}},
    ])
    tables = summarise(frame)
    band = tables["by_band"]
    assert list(band["band"].unique()) == ["0-10"]
    assert (band["max"] == agreed["nodes"]).all()
    assert tables["config_ratio"].loc[0, "equal"] == 1

    ledger = tmp_path / "ledger.csv"
    record("csearch", [("a", 1.0, 5), ("b", 1.0)], ledger=ledger)
    summary = ledger_summary(ledger).set_index("driver")
    assert summary.loc["csearch", "rows"] == 2
    assert summary.loc["csearch", "with_nodes"] == 1
