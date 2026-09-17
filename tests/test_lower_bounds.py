"""The lower bound must never exceed a known optimum.

A lower bound that is too high is not a slow bound, it is a wrong answer: the
binary search starts above the true optimum and returns it, and verifying the
witness by simulation does not catch that, because the witness really does
achieve the value reported. These tests are the guard on that.
"""

import itertools
import json
import random
from pathlib import Path

import pytest

from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from satisfiability.mosp_solver import _lower_bound

SOLUTIONS = Path("solutions")
INSTANCE_DIR = Path("benchmarks/instances")


def _brute_force(inst):
    return min(
        max_open_stacks(inst, list(perm))
        for perm in itertools.permutations(range(inst.n_patterns))
    )


@pytest.mark.parametrize("seed", range(25))
def test_bound_never_exceeds_brute_forced_optimum(seed):
    """On small instances the optimum is known exactly by exhaustion."""
    rng = random.Random(seed)
    n_customers = rng.randint(1, 6)
    n_patterns = rng.randint(1, 6)
    matrix = [
        [rng.randint(0, 1) for _ in range(n_patterns)] for _ in range(n_customers)
    ]
    if not any(any(row) for row in matrix):
        pytest.skip("degenerate all-zero instance")

    inst = MOSPInstance.from_matrix(matrix, name=f"lb{seed}")
    assert _lower_bound(inst) <= _brute_force(inst)


@pytest.mark.parametrize("density", [0.2, 0.5, 0.9])
def test_bound_never_exceeds_optimum_across_densities(density):
    rng = random.Random(int(density * 10))
    for _ in range(8):
        matrix = [
            [1 if rng.random() < density else 0 for _ in range(5)]
            for _ in range(5)
        ]
        if not any(any(row) for row in matrix):
            continue
        inst = MOSPInstance.from_matrix(matrix, name="d")
        assert _lower_bound(inst) <= _brute_force(inst)


def test_bound_never_exceeds_cached_optima():
    """Check against the corpus of solved benchmark instances.

    This is the test that matters for the contraction-degeneracy component,
    whose soundness rests on Yanasse's MOSP = pathwidth + 1 rather than on a
    direct argument.
    """
    if not SOLUTIONS.exists() or not INSTANCE_DIR.exists():
        pytest.skip("benchmark corpus not present")

    from benchmarks.solve_parallel import find_benchmark_files

    known = {}
    for path in SOLUTIONS.glob("*.json"):
        data = json.loads(path.read_text())
        known[data["instance_name"]] = data["mosp_value"]
    if not known:
        pytest.skip("no cached solutions")

    rng = random.Random(0)
    files = find_benchmark_files(INSTANCE_DIR)
    rng.shuffle(files)

    checked = 0
    violations = []
    for filepath in files:
        if checked >= 60:
            break
        try:
            instances = MOSPInstance.from_benchmark_file(filepath)
        except Exception:  # noqa: BLE001
            continue
        for inst in instances:
            if checked >= 60 or inst.name not in known:
                continue
            if inst.n_customers > 80:
                continue  # keep the suite fast; the full sweep covers the rest
            bound = _lower_bound(inst, clique_budget=0.5)
            checked += 1
            if bound > known[inst.name]:
                violations.append((inst.name, bound, known[inst.name]))

    assert checked > 0, "no instances were checked"
    assert not violations, f"lower bound exceeded known optimum: {violations[:5]}"
