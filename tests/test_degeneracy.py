"""Exact counts of optimal orderings (plan §2.6b, `learning.degeneracy`).

The three lattice counts are checked by hand on a three-customer path, where
the search measure over-charges two of the six closing orders and the product
order is unique up to reversal, and against brute-force permutation
enumeration on small random instances. The imitation statistics are checked by
hand on the same path.
"""

import itertools
import math

import pytest

from benchmarks.generator import generate_random_instance
from learning.degeneracy import (
    Compact,
    analyse,
    closing_weights,
    lattice_counts,
    lattice_minimum,
    path_weighted_choices,
    product_lattice,
    witness_choices,
)
from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from satisfiability.heuristics import (
    _cs_cost,
    _neighbour_masks,
    product_order_from_customers,
)

# Customers 0 -- 1 -- 2 through products 0 = {0, 1} and 1 = {1, 2}. Optimum 2.
# Both product orders reach it (the profile is 2, 2 either way), so the product
# order is unique up to reversal. Every closing order constructs to 2, but the
# search measure charges |N[1]| = 3 for closing the middle customer first, so
# two of the six closing orders are over-charged.
PATH = [[1, 0], [1, 1], [0, 1]]


def test_path_counts_by_hand():
    inst = MOSPInstance.from_matrix(PATH, name="p3")
    row = analyse(inst, optimum=2, witness=[0, 1])
    assert row["optimum"] == 2 and row["min_construction"] == 2 == row["min_products"]
    assert row["count_closing"] == 6
    assert row["count_search"] == 4
    assert row["count_products"] == 2
    assert row["unique_products"]
    assert row["closing_fraction"] == pytest.approx(1.0)
    assert not row["complete_graph"]
    assert row["audit_construction"] and row["audit_search"] and row["audit_products"]


def test_path_witness_choices_by_hand():
    inst = MOSPInstance.from_matrix(PATH, name="p3")
    comp = Compact(inst)
    _, constr = closing_weights(comp)
    f, g = lattice_counts(constr, comp.a, 2)
    # Witness [0, 1] closes customers in the order 0, then 1 and 2 at the same
    # step, index tie-break -> (0, 1, 2). Three optimal first moves, two second,
    # one last.
    info = witness_choices(comp, constr, 2, g, [0, 1, 2])
    assert info["optimal"] and info["choices"] == [3, 2, 1]
    stats = path_weighted_choices(constr, comp.a, 2, f, g)
    assert stats["mean_choices"] == pytest.approx(2.0)
    assert stats["ceiling"] == pytest.approx(11 / 18)
    assert stats["forced_frac"] == pytest.approx(1 / 3)
    row = analyse(inst, optimum=2, witness=[0, 1])
    assert row["witness_mean_choices"] == pytest.approx(2.0)
    assert row["witness_ceiling"] == pytest.approx(11 / 18)
    assert row["witness_forced_steps"] == 1 and row["witness_steps"] == 3


def test_complete_graph_makes_every_order_optimal():
    inst = MOSPInstance.from_matrix([[1], [1], [1]], name="k3")
    row = analyse(inst, optimum=3)
    assert row["complete_graph"]
    assert row["count_closing"] == math.factorial(3) == row["count_search"]
    assert row["count_products"] == 1
    assert row["all_mean_choices"] == pytest.approx((3 + 2 + 1) / 3)


def test_twins_and_empty_rows_and_columns():
    # Customers 0 and 1 are identical (twins); customer 3 and product 3 are empty.
    matrix = [[1, 1, 0, 0], [1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 0, 0]]
    inst = MOSPInstance.from_matrix(matrix, name="twins")
    comp = Compact(inst)
    assert comp.a == 3 and comp.m == 3
    assert comp.twin_factor() == 2 and comp.column_factor() == 1
    row = analyse(inst, optimum=3)
    assert row["n_active"] == 3 and row["m_active"] == 3
    assert row["count_closing"] % 2 == 0
    assert row["closing_up_to_twins"] * 2 == row["count_closing"]


def test_wrong_optimum_fails_the_audit():
    inst = MOSPInstance.from_matrix(PATH, name="p3")
    row = analyse(inst, optimum=3)
    assert not row["audit_construction"] and not row["audit_products"]
    assert row["count_closing"] == 6  # every order is within a budget of 3


@pytest.mark.parametrize("seed", range(6))
def test_lattices_agree_with_brute_force(seed):
    n, m = 4 + seed % 3, 3 + seed % 4
    inst = generate_random_instance(n, m, 0.25 + 0.1 * (seed % 3), seed=seed)
    comp = Compact(inst)
    search, constr = closing_weights(comp)
    masks = _neighbour_masks(inst)

    values_b, values_a = [], []
    for perm in itertools.permutations(comp.customers):
        values_b.append(max_open_stacks(inst, product_order_from_customers(inst, perm)))
        values_a.append(_cs_cost(masks, perm))
    opt_b, opt_a = min(values_b), min(values_a)
    assert lattice_minimum(constr, comp.a) == opt_b
    assert lattice_minimum(search, comp.a) == opt_a
    f, g = lattice_counts(constr, comp.a, opt_b)
    assert f[-1] == g[0] == values_b.count(opt_b)
    f, _ = lattice_counts(search, comp.a, opt_a)
    assert f[-1] == values_a.count(opt_a)

    extra = [p for p in range(inst.n_patterns) if p not in comp.products]
    values_p = [max_open_stacks(inst, list(perm) + extra)
                for perm in itertools.permutations(comp.products)]
    minimum, count = product_lattice(comp)
    assert minimum == min(values_p) == opt_b
    assert count == values_p.count(minimum)
    assert count % 2 == 0 or comp.m <= 1


def test_tables_are_written(tmp_path):
    from learning.degeneracy import write_tables
    import pandas as pd

    rows = []
    for name, matrix, opt, witness in (("p3", PATH, 2, [0, 1]), ("k3", [[1], [1], [1]], 3, [0])):
        inst = MOSPInstance.from_matrix(matrix, name=name)
        row = analyse(inst, optimum=opt, witness=witness)
        row.update({"source": "corpus", "source_file": "x", "collection": "hand", "seconds": 0.0})
        rows.append(row)
    frame = pd.DataFrame(rows)
    out = tmp_path / "tables.md"
    write_tables(frame, out, 1.0)
    text = out.read_text()
    assert "## Audit" in text and "Imitation" in text
    assert "| p3" in text or "p3" in text
