"""Tests for the descending ratchet, especially its budget.

The budget is the part worth testing. A per-instance timeout that quietly fails
to bound some calls is worse than no timeout, because results then carry a limit
they were never actually held to.
"""

import itertools
import random
import time

import pytest

from benchmarks.ratchet import _sat_at, ratchet
from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks


def _brute_force(inst):
    return min(
        max_open_stacks(inst, list(perm))
        for perm in itertools.permutations(range(inst.n_patterns))
    )


def _hard_instance():
    """An instance whose refutation below the optimum does not return quickly."""
    from benchmarks.solve_parallel import find_benchmark_files
    from pathlib import Path

    for filepath in find_benchmark_files(Path("benchmarks/instances")):
        if filepath.name == "sp4.txt":
            for inst in MOSPInstance.from_benchmark_file(filepath):
                if inst.name.strip().startswith("SP3"):
                    return inst
    return None


def test_sat_at_reports_three_outcomes():
    inst = MOSPInstance.from_matrix([[1, 1, 0], [0, 1, 1]], name="three")
    assert _sat_at(inst, 5)[0] == "sat"
    assert _sat_at(inst, 0)[0] == "unsat"


def test_sat_at_returns_a_valid_witness():
    inst = MOSPInstance.from_matrix([[1, 1, 0], [0, 1, 1]], name="witness")
    status, ordering = _sat_at(inst, 2)
    assert status == "sat"
    assert sorted(ordering) == [0, 1, 2]
    assert max_open_stacks(inst, ordering) <= 2


@pytest.mark.parametrize("seed", range(8))
def test_ratchet_reaches_the_optimum_on_small_instances(seed, tmp_path):
    rng = random.Random(seed)
    n_patterns = rng.randint(2, 5)
    matrix = [
        [rng.randint(0, 1) for _ in range(n_patterns)]
        for _ in range(rng.randint(2, 5))
    ]
    if not any(any(row) for row in matrix):
        pytest.skip("degenerate all-zero instance")

    inst = MOSPInstance.from_matrix(matrix, name=f"r{seed}")
    value, ordering, _ = ratchet(inst, timeout=120.0,
                                 solutions_dir=tmp_path, verbose=False)
    assert value == _brute_force(inst)
    assert max_open_stacks(inst, ordering) == value


def test_budget_bounds_the_opening_call():
    """The regression this file exists for.

    The opening call at `--start` used to run unbounded, so a run given an hour
    could spend several on its first question. A hard refutation with a small
    budget must come back as a timeout, not run to completion.
    """
    inst = _hard_instance()
    if inst is None:
        pytest.skip("SP3 benchmark not available")

    started = time.time()
    # Well below SP3's optimum of 34, so this is a refutation that does not
    # return quickly; the budget is what must stop it.
    status, _ = _sat_at(inst, 25, budget=10.0)
    elapsed = time.time() - started

    assert status == "timeout"
    assert elapsed < 40.0, f"budget of 10s was not honoured: took {elapsed:.0f}s"


def test_ratchet_honours_its_deadline_from_the_first_call(tmp_path):
    inst = _hard_instance()
    if inst is None:
        pytest.skip("SP3 benchmark not available")

    started = time.time()
    value, _, proven = ratchet(inst, start=25, timeout=10.0,
                               solutions_dir=tmp_path, verbose=False)
    elapsed = time.time() - started

    assert not proven
    assert elapsed < 60.0, f"deadline not honoured: took {elapsed:.0f}s"


# -------------------------------------------------------
# Fan-out across instances
# -------------------------------------------------------


def test_ratchet_many_solves_every_instance(tmp_path):
    from benchmarks.ratchet import ratchet_many

    instances = [
        MOSPInstance.from_matrix([[1, 1, 0], [0, 1, 1]], name=f"m{i}")
        for i in range(4)
    ]
    results = ratchet_many(instances, timeout=120.0, solutions_dir=tmp_path,
                           workers=2)

    assert len(results) == len(instances)
    assert all(value == 2 for value, _, _ in results)
    assert len(list(tmp_path.glob("*.json"))) == len(instances)


def test_ratchet_many_matches_sequential(tmp_path):
    """Worker count is a resource knob and must not change any answer."""
    from benchmarks.ratchet import ratchet_many

    rng = random.Random(5)
    instances = []
    for i in range(4):
        matrix = [[rng.randint(0, 1) for _ in range(4)] for _ in range(4)]
        if not any(any(row) for row in matrix):
            continue
        instances.append(MOSPInstance.from_matrix(matrix, name=f"p{i}"))
    if not instances:
        pytest.skip("no usable instances")

    parallel = ratchet_many(instances, timeout=120.0,
                            solutions_dir=tmp_path / "par", workers=3)
    serial = ratchet_many(instances, timeout=120.0,
                          solutions_dir=tmp_path / "ser", workers=1)

    assert [v for v, _, _ in parallel] == [v for v, _, _ in serial]


def test_ratchet_many_survives_an_empty_list(tmp_path):
    from benchmarks.ratchet import ratchet_many

    assert ratchet_many([], timeout=10.0, solutions_dir=tmp_path, workers=2) == []
