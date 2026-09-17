"""Tests for the independent checking tools."""

import itertools
import random

import pytest

from mosp.certify import check_witness, count_open_stacks, export_cnf
from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks


@pytest.mark.parametrize("seed", range(20))
def test_independent_counter_agrees_with_the_solver(seed):
    """The checker reimplements the count; the two must still agree.

    If they ever diverge, one of them is wrong, and the whole point of the
    checker is that it is not the same code as the thing it checks.
    """
    rng = random.Random(seed)
    n_patterns = rng.randint(1, 7)
    matrix = [
        [rng.randint(0, 1) for _ in range(n_patterns)]
        for _ in range(rng.randint(1, 7))
    ]
    inst = MOSPInstance.from_matrix(matrix, name=f"c{seed}")
    ordering = list(range(n_patterns))
    rng.shuffle(ordering)

    assert count_open_stacks(matrix, ordering) == max_open_stacks(inst, ordering)


def test_check_witness_accepts_a_correct_solution():
    inst = MOSPInstance.from_matrix([[1, 1, 0], [0, 1, 1]], name="ok")
    ok, message = check_witness(inst, {"ordering": [0, 1, 2], "mosp_value": 2})
    assert ok, message


def test_check_witness_rejects_a_wrong_value():
    """A claim that does not match its own ordering must fail."""
    inst = MOSPInstance.from_matrix([[1, 1, 0], [0, 1, 1]], name="bad")
    ok, message = check_witness(inst, {"ordering": [0, 1, 2], "mosp_value": 1})
    assert not ok
    assert "achieves 2" in message


def test_check_witness_rejects_a_non_permutation():
    inst = MOSPInstance.from_matrix([[1, 1, 0], [0, 1, 1]], name="dup")
    ok, message = check_witness(inst, {"ordering": [0, 0, 1], "mosp_value": 2})
    assert not ok
    assert "permutation" in message


def test_check_witness_rejects_incomplete_payloads():
    inst = MOSPInstance.from_matrix([[1, 1]], name="partial")
    ok, _ = check_witness(inst, {"ordering": [0, 1]})
    assert not ok


def test_exported_cnf_is_refutable_by_another_solver(tmp_path):
    """The export exists so a third party can re-derive the lower bound."""
    from pysat.formula import CNF
    from pysat.solvers import Glucose42

    inst = MOSPInstance.from_matrix([[1, 1, 0], [0, 1, 1], [1, 0, 1]], name="x")
    optimum = min(
        max_open_stacks(inst, list(p)) for p in itertools.permutations(range(3))
    )

    path = tmp_path / "x.cnf"
    n_vars, n_clauses = export_cnf(inst, optimum - 1, path)
    assert n_vars > 0 and n_clauses > 0

    # A solver that is not the one the project uses must also refute k-1.
    formula = CNF(from_file=str(path))
    with Glucose42(bootstrap_with=formula.clauses) as solver:
        assert solver.solve() is False, "k-1 must be unsatisfiable"

    path_sat = tmp_path / "x_sat.cnf"
    export_cnf(inst, optimum, path_sat)
    formula = CNF(from_file=str(path_sat))
    with Glucose42(bootstrap_with=formula.clauses) as solver:
        assert solver.solve() is True, "k must be satisfiable"
