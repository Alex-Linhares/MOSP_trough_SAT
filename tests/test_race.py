"""The raced decision procedure must answer exactly what the two do alone.

A portfolio is only as trustworthy as its agreement: if the race could return
"unsat" where a procedure run alone returns "sat", it would manufacture wrong
optima that witness verification could not catch. These check the two against
each other and against brute force on instances small enough to enumerate.
"""

import itertools
import random

import pytest

from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from satisfiability.race import decide_race, solve_race


def _instance(seed: int, n_c: int = 7, n_p: int = 6) -> MOSPInstance:
    rng = random.Random(seed)
    matrix = [[rng.randint(0, 1) for _ in range(n_p)] for _ in range(n_c)]
    for row in matrix:
        if not any(row):
            row[rng.randrange(n_p)] = 1
    return MOSPInstance.from_matrix(matrix, name=f"race{seed}")


def _brute_force(instance: MOSPInstance) -> int:
    return min(max_open_stacks(instance, list(perm))
               for perm in itertools.permutations(range(instance.n_patterns)))


@pytest.mark.parametrize("seed", range(6))
def test_race_agrees_with_each_procedure_alone(seed):
    instance = _instance(seed)
    optimum = _brute_force(instance)

    for k in range(max(1, optimum - 1), optimum + 2):
        alone = {name: decide_race(instance, k, timeout=60, procedures=(name,))
                 for name in ("csearch", "sat")}
        raced = decide_race(instance, k, timeout=60)

        statuses = {a.status for a in alone.values()} | {raced.status}
        assert statuses == {"sat"} or statuses == {"unsat"}, (
            f"k={k} disagreement: "
            f"{ {n: a.status for n, a in alone.items()} }, race={raced.status}")


@pytest.mark.parametrize("seed", range(4))
def test_race_decides_the_optimum_correctly(seed):
    """Below the optimum it must refute; at the optimum it must satisfy."""
    instance = _instance(seed)
    optimum = _brute_force(instance)

    if optimum > 1:
        assert decide_race(instance, optimum - 1, timeout=60).status == "unsat"
    assert decide_race(instance, optimum, timeout=60).status == "sat"


@pytest.mark.parametrize("seed", range(4))
def test_solve_race_finds_the_brute_forced_optimum(seed):
    instance = _instance(seed)
    answer = solve_race(instance, time_budget=120)
    assert answer.proved
    assert answer.value == _brute_force(instance)


def test_a_satisfiable_race_returns_a_usable_closing_order():
    """Whoever wins answers in the same currency: a customer closing order."""
    from satisfiability.heuristics import product_order_from_customers

    instance = _instance(9)
    optimum = _brute_force(instance)
    for procedures in (("csearch",), ("sat",), ("csearch", "sat")):
        answer = decide_race(instance, optimum, timeout=60, procedures=procedures)
        assert answer.status == "sat"
        ordering = product_order_from_customers(instance, answer.order)
        assert sorted(ordering) == list(range(instance.n_patterns))
        assert max_open_stacks(instance, ordering) <= optimum
