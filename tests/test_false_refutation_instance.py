"""A whole-instance false refutation by Chu & Stuckey's published rules.

Found 2026-10-09 by gluing two copies of a 17-customer near-miss of the
false-refutation hunt (paper2/near_miss_study.py). On this 34-customer instance
the published definite move, with the subset rule and old move (memo on or
off, better move off), answers "unsat" at k = 6, while a closing order with 6
open stacks exists: the published search would report the optimum as 7. The
repaired rules answer sat at 6 and unsat at 5 (optimum 6).
"""
import json
from pathlib import Path

import pytest

from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from satisfiability.customer_search import decide

HIT = Path(__file__).resolve().parents[1] / "paper2" / "data" / "false_refutation" / "instance34.json"


def _instance():
    d = json.loads(HIT.read_text())["minimised"]
    masks = d["masks"]
    n = len(masks)
    edges = [(i, j) for i in range(n) for j in range(i + 1, n) if masks[i] >> j & 1]
    matrix = [[1 if v in e else 0 for e in edges] for v in range(n)]
    return MOSPInstance.from_matrix(matrix, name="false_refutation_34"), edges, d


def _product_order(edges, closing):
    placed, prod = set(), []
    for c in closing:  # closing c cuts every pattern of c not yet cut
        for p, e in enumerate(edges):
            if c in e and p not in placed:
                placed.add(p)
                prod.append(p)
    return prod


@pytest.mark.parametrize("native", [True, False])
def test_published_rules_refute_a_feasible_k(native):
    inst, edges, d = _instance()
    k = d["k"]
    assert k == 6
    # a product order with k open stacks exists, checked by plain simulation
    assert max_open_stacks(inst, _product_order(edges, d["witness"])) == k
    # the published rules nevertheless refute k
    assert decide(inst, k, repaired_rules=False, native=native).status == "unsat"


@pytest.mark.parametrize("native", [True, False])
def test_repaired_rules_find_the_optimum(native):
    inst, edges, d = _instance()
    k = d["k"]
    sat = decide(inst, k, repaired_rules=True, native=native)
    assert sat.status == "sat"
    assert max_open_stacks(inst, _product_order(edges, sat.order)) <= k
    assert decide(inst, k - 1, repaired_rules=True, native=native).status == "unsat"
