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


def test_cs_cost_matches_its_set_definition():
    """`max_i |O(S_i) - S_{i-1}|`, computed with sets rather than bitmasks."""
    from satisfiability.heuristics import _cs_cost, _neighbour_masks

    rng = random.Random(11)
    for _ in range(60):
        n_patterns = rng.randint(1, 6)
        matrix = [[rng.randint(0, 1) for _ in range(n_patterns)]
                  for _ in range(rng.randint(1, 6))]
        inst = MOSPInstance.from_matrix(matrix, name="cs")
        neighbours = [set() for _ in range(inst.n_customers)]
        for pattern in range(inst.n_patterns):
            holders = set(inst.pattern_customers(pattern))
            for customer in holders:
                neighbours[customer] |= holders

        masks = _neighbour_masks(inst)
        order = list(range(inst.n_customers))
        rng.shuffle(order)

        opened, closed, peak = set(), set(), 0
        for customer in order:
            opened |= neighbours[customer]
            peak = max(peak, len(opened - closed))
            closed.add(customer)
        assert _cs_cost(masks, order) == peak


@pytest.mark.parametrize("seed", range(4))
def test_restricted_dfs_finds_the_optimum_almost_always(seed):
    """Chu & Stuckey report `ub_MOSP` finding the optimum nearly always. It is
    a heuristic — the `R ∩ O(S)` restriction can exclude every optimal order —
    so this pins the rate rather than demanding exactness."""
    from satisfiability.heuristics import restricted_dfs

    rng = random.Random(200 + seed)
    exact = total = 0
    for _ in range(40):
        n_patterns = rng.randint(2, 7)
        matrix = [[1 if rng.random() < rng.choice([0.3, 0.6]) else 0
                   for _ in range(n_patterns)]
                  for _ in range(rng.randint(2, 7))]
        if not any(any(row) for row in matrix):
            continue
        inst = MOSPInstance.from_matrix(matrix, name="dfs")
        value, ordering = restricted_dfs(inst)
        optimum = _brute_force(inst)

        assert value == max_open_stacks(inst, ordering)
        assert value >= optimum
        total += 1
        exact += value == optimum
    assert exact >= 0.9 * total, f"only {exact}/{total} optimal"


def test_restricted_dfs_never_loses_to_its_seed():
    """The seed is the incumbent, so the search can only improve on it."""
    from satisfiability.heuristics import (
        _cs_cost, _neighbour_masks, restricted_dfs)

    rng = random.Random(12)
    for _ in range(40):
        n_patterns = rng.randint(2, 6)
        matrix = [[rng.randint(0, 1) for _ in range(n_patterns)]
                  for _ in range(rng.randint(2, 6))]
        if not any(any(row) for row in matrix):
            continue
        inst = MOSPInstance.from_matrix(matrix, name="seeded")
        active = [c for c in range(inst.n_customers) if inst.customer_patterns(c)]
        rng.shuffle(active)

        value, _ = restricted_dfs(inst, seed_order=active)
        assert value <= _cs_cost(_neighbour_masks(inst), active)


def test_restricted_dfs_is_anytime():
    """Out of budget at the first node, it still returns the seed's ordering."""
    from satisfiability.heuristics import restricted_dfs

    matrix = [[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1], [1, 0, 0, 1]]
    inst = MOSPInstance.from_matrix(matrix, name="budget")

    value, ordering = restricted_dfs(inst, max_nodes=0)
    assert sorted(ordering) == list(range(inst.n_patterns))
    assert value == max_open_stacks(inst, ordering)
    assert value >= _brute_force(inst)


def test_restricted_dfs_crosses_disconnected_components():
    """With the frontier empty every remaining customer is a candidate, so a
    disconnected instance is still ordered rather than abandoned."""
    from satisfiability.heuristics import restricted_dfs

    matrix = [[1, 1, 0, 0], [0, 0, 1, 1]]
    inst = MOSPInstance.from_matrix(matrix, name="split")

    value, ordering = restricted_dfs(inst)
    assert sorted(ordering) == list(range(4))
    assert value == 1
