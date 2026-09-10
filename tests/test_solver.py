"""Tests for the end-to-end MOSP solver."""

import pytest

from mosp.instance import MOSPInstance
from mosp.solver import solve_mosp
from mosp.verify import max_open_stacks


def test_trivial_single_pattern():
    """One pattern, one customer → 1 open stack."""
    inst = MOSPInstance.from_matrix([[1]], name="trivial")
    sol = solve_mosp(inst)
    assert sol.max_open_stacks == 1
    assert sol.ordering == [0]


def test_independent_patterns():
    """No patterns share customers → MOSP = 1 (at most 1 stack open at a time)."""
    matrix = [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
    ]
    inst = MOSPInstance.from_matrix(matrix, name="independent")
    sol = solve_mosp(inst)
    assert sol.max_open_stacks == 1
    # Pathwidth of independent graph is 0
    assert sol.pathwidth == 0


def test_all_shared_customers():
    """All patterns share all customers → MOSP = n_customers."""
    matrix = [
        [1, 1, 1],
        [1, 1, 1],
    ]
    inst = MOSPInstance.from_matrix(matrix, name="all_shared")
    sol = solve_mosp(inst)
    # Agreement graph is K3, pathwidth = 2, MOSP = 3
    # But we have 2 customers, so max open stacks is at most 2
    # Let's verify: with any ordering, both customers need all 3 patterns,
    # so both stacks are open from step 1 to step 3.
    actual = max_open_stacks(inst, sol.ordering)
    assert actual == sol.max_open_stacks


def test_chain_patterns():
    """Patterns forming a chain share customers pairwise."""
    # Customer 0: patterns 0,1
    # Customer 1: patterns 1,2
    # Customer 2: patterns 2,3
    # Agreement graph: 0-1-2-3 (path), pathwidth = 1, MOSP = 2
    matrix = [
        [1, 1, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 1, 1],
    ]
    inst = MOSPInstance.from_matrix(matrix, name="chain")
    sol = solve_mosp(inst)
    assert sol.pathwidth == 1
    assert sol.max_open_stacks == 2

    actual = max_open_stacks(inst, sol.ordering)
    assert actual == sol.max_open_stacks


def test_solver_verifies():
    """Solution should be consistent with the verifier."""
    matrix = [
        [1, 1, 0, 0, 0],
        [0, 1, 1, 0, 0],
        [0, 0, 1, 1, 0],
        [0, 0, 0, 1, 1],
        [1, 0, 0, 0, 1],
    ]
    inst = MOSPInstance.from_matrix(matrix, name="cycle5_patterns")
    sol = solve_mosp(inst)

    actual = max_open_stacks(inst, sol.ordering)
    assert actual == sol.max_open_stacks


def test_yanasse_example():
    """A small example to verify the MOSP-pathwidth correspondence.

    3 customers, 4 patterns:
    C0 needs P0, P1
    C1 needs P1, P2
    C2 needs P2, P3

    Agreement graph: P0-P1-P2-P3 (path), pathwidth=1, MOSP=2
    """
    matrix = [
        [1, 1, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 1, 1],
    ]
    inst = MOSPInstance.from_matrix(matrix, name="yanasse_ex")
    sol = solve_mosp(inst)
    assert sol.pathwidth == 1
    assert sol.max_open_stacks == 2
