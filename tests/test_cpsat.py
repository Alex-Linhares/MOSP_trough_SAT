"""The CP-SAT oracle must agree with what this project already believes.

Its purpose is to be an outside opinion: a mature solver, in its own
interpreter, sharing no code with the SAT encoding or the customer search. That
only means something if it is held to the same standard as everything else --
agreement with exhaustive search on instances small enough to enumerate, before
its agreement on large ones is treated as evidence.

Skipped entirely when `.venv-cpsat` is absent, since it is a 240 MB dependency
the rest of the project does not need.
"""

import itertools
import random

import pytest

from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from satisfiability.cpsat import available, solve_cpsat

needs_cpsat = pytest.mark.skipif(not available(),
                                 reason=".venv-cpsat is not built here")


def _brute(inst):
    return min(max_open_stacks(inst, list(perm))
               for perm in itertools.permutations(range(inst.n_patterns)))


def _random(rng, max_customers=6, max_patterns=6):
    n_patterns = rng.randint(1, max_patterns)
    rows = [[1 if rng.random() < rng.choice([0.2, 0.4, 0.6, 0.8]) else 0
             for _ in range(n_patterns)]
            for _ in range(rng.randint(1, max_customers))]
    return MOSPInstance.from_matrix(rows, name="t")


@needs_cpsat
def test_it_agrees_with_exhaustive_search():
    """The model is Martin, Yanasse & Pinto's; this checks we transcribed it."""
    rng = random.Random(31)
    for _ in range(25):
        instance = _random(rng)
        answer = solve_cpsat(instance, max_seconds=20)
        assert answer.status == "OPTIMAL", f"{answer.status}: {answer.error}"
        assert answer.value == _brute(instance)


@needs_cpsat
def test_its_orderings_hold_up_under_our_own_checker():
    """A value is worth nothing without a sequence that achieves it, and the
    sequence is checked by the simulator, not by CP-SAT's word."""
    rng = random.Random(32)
    for _ in range(25):
        instance = _random(rng)
        answer = solve_cpsat(instance, max_seconds=20)
        assert sorted(answer.ordering) == list(range(instance.n_patterns))
        assert max_open_stacks(instance, answer.ordering) == answer.value


@needs_cpsat
def test_it_agrees_with_both_of_our_engines():
    """Three implementations, one answer. The SAT encoding and the customer
    search share this project's assumptions; CP-SAT shares none of them."""
    from satisfiability.customer_search import solve as search_solve
    from satisfiability.mosp_solver import solve_mosp_sat

    rng = random.Random(33)
    for _ in range(8):
        instance = _random(rng, max_customers=7, max_patterns=6)
        oracle = solve_cpsat(instance, max_seconds=20)
        sat_value, _ = solve_mosp_sat(instance, solutions_dir=None)
        searched = search_solve(instance)

        assert oracle.status == "OPTIMAL"
        assert searched.proved
        assert oracle.value == sat_value == searched.value


@needs_cpsat
def test_an_unfinished_run_is_not_an_optimality_claim():
    """FEASIBLE means it found something and ran out of time proving it least;
    only OPTIMAL may be read as an answer."""
    instance = MOSPInstance.from_matrix(
        [[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1]], name="quick")
    answer = solve_cpsat(instance, max_seconds=0.001)
    assert answer.proved == (answer.status == "OPTIMAL")
    if answer.status == "FEASIBLE":
        assert answer.value is not None and answer.best_bound is not None


def test_it_reports_absence_rather_than_failing(tmp_path, monkeypatch):
    """With no interpreter, callers get a status they can act on."""
    import satisfiability.cpsat as cpsat

    monkeypatch.setattr(cpsat, "VENV_PYTHON", tmp_path / "nothing")
    answer = cpsat.solve_cpsat(
        MOSPInstance.from_matrix([[1]], name="x"), max_seconds=1)
    assert answer.status == "UNAVAILABLE"
    assert not answer.proved
