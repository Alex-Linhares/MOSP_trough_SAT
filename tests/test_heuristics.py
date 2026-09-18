"""Tests for the upper bound strategies."""

import itertools
import random

import pytest

from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from satisfiability.heuristics import STRATEGIES, least_cost_node, upper_bound


def _brute_force(inst):
    return min(
        max_open_stacks(inst, list(perm))
        for perm in itertools.permutations(range(inst.n_patterns))
    )


@pytest.mark.parametrize("name", sorted(STRATEGIES))
@pytest.mark.parametrize("seed", range(6))
def test_every_strategy_returns_a_valid_permutation(name, seed):
    """An upper bound is worthless if its ordering is not a real sequence."""
    rng = random.Random(seed)
    n_customers = rng.randint(1, 6)
    n_patterns = rng.randint(1, 6)
    matrix = [
        [rng.randint(0, 1) for _ in range(n_patterns)] for _ in range(n_customers)
    ]
    inst = MOSPInstance.from_matrix(matrix, name=f"h{seed}")

    value, ordering = STRATEGIES[name](inst)

    assert sorted(ordering) == list(range(n_patterns))
    assert value == max_open_stacks(inst, ordering), "value must match its ordering"


@pytest.mark.parametrize("name", sorted(STRATEGIES))
@pytest.mark.parametrize("seed", range(6))
def test_every_strategy_is_a_genuine_upper_bound(name, seed):
    """No strategy may report a value below the true optimum."""
    rng = random.Random(100 + seed)
    matrix = [[rng.randint(0, 1) for _ in range(5)] for _ in range(5)]
    if not any(any(row) for row in matrix):
        pytest.skip("degenerate all-zero instance")
    inst = MOSPInstance.from_matrix(matrix, name="ub")

    value, _ = STRATEGIES[name](inst)
    assert value >= _brute_force(inst)


def test_mcn_is_deterministic():
    """MCN is a construction, not a search: same input, same output."""
    rng = random.Random(3)
    matrix = [[rng.randint(0, 1) for _ in range(8)] for _ in range(8)]
    inst = MOSPInstance.from_matrix(matrix, name="det")
    assert least_cost_node(inst) == least_cost_node(inst)


def test_mcn_plus_tabu_is_never_worse_than_its_starts():
    """The combination must not lose to either component it is built from."""
    rng = random.Random(7)
    for _ in range(5):
        matrix = [[rng.randint(0, 1) for _ in range(9)] for _ in range(9)]
        if not any(any(row) for row in matrix):
            continue
        inst = MOSPInstance.from_matrix(matrix, name="combo")
        combined, _ = STRATEGIES["mcn+tabu"](inst)
        mcn, _ = STRATEGIES["mcn"](inst)
        assert combined <= mcn, "tabu refinement must not worsen the MCN start"


def test_empty_and_trivial_instances():
    assert upper_bound(MOSPInstance.from_matrix([[]], name="e"))[0] == 0
    value, ordering = upper_bound(MOSPInstance.from_matrix([[1]], name="one"))
    assert (value, ordering) == (1, [0])


def test_unknown_strategy_names_what_is_available():
    inst = MOSPInstance.from_matrix([[1, 1], [1, 0]], name="x")
    with pytest.raises(KeyError, match="mcn"):
        upper_bound(inst, strategy="no-such-strategy")


# -------------------------------------------------------
# Customer-order search
# -------------------------------------------------------


def test_product_order_from_customers_is_a_permutation():
    from satisfiability.heuristics import product_order_from_customers

    inst = MOSPInstance.from_matrix(
        [[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 0, 1]], name="build")
    order = product_order_from_customers(inst, [2, 0, 1])
    assert sorted(order) == [0, 1, 2, 3]


def test_product_order_groups_by_closing_customer():
    """Each customer's outstanding products are scheduled together."""
    from satisfiability.heuristics import product_order_from_customers

    inst = MOSPInstance.from_matrix(
        [[1, 1, 0, 0], [0, 0, 1, 1]], name="blocks")
    # customer 1 first: its products lead, then customer 0's
    assert product_order_from_customers(inst, [1, 0]) == [2, 3, 0, 1]
    assert product_order_from_customers(inst, [0, 1]) == [0, 1, 2, 3]


@pytest.mark.parametrize("seed", range(10))
def test_customer_orders_cover_an_optimum(seed):
    """Chu & Stuckey's reduction: searching customer orders loses nothing.

    This is the property the strategy rests on, so it is checked directly
    against exhaustive search rather than assumed from the paper.
    """
    import itertools

    from satisfiability.heuristics import product_order_from_customers

    rng = random.Random(seed)
    n_customers = rng.randint(2, 5)
    n_patterns = rng.randint(2, 5)
    matrix = [
        [rng.randint(0, 1) for _ in range(n_patterns)] for _ in range(n_customers)
    ]
    if not any(any(row) for row in matrix):
        pytest.skip("degenerate all-zero instance")
    inst = MOSPInstance.from_matrix(matrix, name=f"cover{seed}")

    by_products = min(
        max_open_stacks(inst, list(perm))
        for perm in itertools.permutations(range(n_patterns))
    )
    by_customers = min(
        max_open_stacks(inst, product_order_from_customers(inst, list(order)))
        for order in itertools.permutations(range(n_customers))
    )
    assert by_customers == by_products


@pytest.mark.parametrize("seed", range(6))
def test_customer_tabu_is_a_genuine_upper_bound(seed):
    rng = random.Random(200 + seed)
    matrix = [[rng.randint(0, 1) for _ in range(5)] for _ in range(5)]
    if not any(any(row) for row in matrix):
        pytest.skip("degenerate all-zero instance")
    inst = MOSPInstance.from_matrix(matrix, name="ct")

    value, ordering = STRATEGIES["customer-tabu"](inst)
    assert sorted(ordering) == list(range(inst.n_patterns))
    assert value == max_open_stacks(inst, ordering)
    assert value >= _brute_force(inst)
