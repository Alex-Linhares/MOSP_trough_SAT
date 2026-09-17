"""Tests for the parallel batch solver."""

import itertools
import random

import pytest

from benchmarks.solve_parallel import _should_skip, solve_one_parallel, sweep
from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks


def _brute_force(inst):
    return min(
        max_open_stacks(inst, list(perm))
        for perm in itertools.permutations(range(inst.n_patterns))
    )


# -------------------------------------------------------
# File filtering
# -------------------------------------------------------


@pytest.mark.parametrize(
    "name",
    ["Dataset_Description - SCOOP.txt", "README_1.1", "README_1.1~",
     "S1. Dataset - README FIRST.pdf", "notes.md"],
)
def test_skips_non_instance_files(tmp_path, name):
    assert _should_skip(tmp_path / name)


@pytest.mark.parametrize("name", ["GP1.txt", "problem_10_10.dat", "wbp_10_10.txt"])
def test_keeps_instance_files(tmp_path, name):
    assert not _should_skip(tmp_path / name)


# -------------------------------------------------------
# Parallel search over k
# -------------------------------------------------------


def test_parallel_k_matches_brute_force_trivial():
    """Single pattern, single customer."""
    inst = MOSPInstance.from_matrix([[1]], name="one")
    value, ordering = solve_one_parallel(inst, workers=2, verbose=False)
    assert value == _brute_force(inst)
    assert max_open_stacks(inst, ordering) == value


@pytest.mark.parametrize("seed", range(6))
def test_parallel_k_matches_brute_force(seed):
    """The parallel search must land on the same optimum as exhaustive search."""
    rng = random.Random(seed)
    n_customers = rng.randint(2, 5)
    n_patterns = rng.randint(2, 5)
    matrix = [
        [rng.randint(0, 1) for _ in range(n_patterns)] for _ in range(n_customers)
    ]
    if not any(any(row) for row in matrix):
        pytest.skip("degenerate all-zero instance")

    inst = MOSPInstance.from_matrix(matrix, name=f"rand{seed}")
    value, ordering = solve_one_parallel(inst, workers=4, verbose=False)
    assert value == _brute_force(inst)
    assert max_open_stacks(inst, ordering) == value


@pytest.mark.parametrize("workers", [1, 2, 8])
def test_parallel_k_independent_of_worker_count(workers):
    """Worker count is a resource knob; it must not change the answer."""
    matrix = [[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1], [1, 0, 0, 1]]
    inst = MOSPInstance.from_matrix(matrix, name="fixed")
    value, ordering = solve_one_parallel(inst, workers=workers, verbose=False)
    assert value == _brute_force(inst)
    assert max_open_stacks(inst, ordering) == value


def test_parallel_k_returns_none_on_timeout():
    """A timeout reports failure rather than a wrong answer.

    Needs an instance whose bounds do not already meet, otherwise the solver
    answers from the bounds alone and never reaches the deadline check.
    """
    # The instance is searched for rather than hard-coded. Every time the bounds
    # improve, a fixed fixture stops having a gap, the solver answers from the
    # bounds alone, and this test fails for a reason unrelated to timeouts --
    # which happened three times. Searching keeps it honest against future
    # improvements.
    from satisfiability.mosp_solver import _lower_bound, _upper_bound

    inst = None
    for seed in range(60):
        rng = random.Random(seed)
        matrix = [
            [1 if rng.random() < 0.35 else 0 for _ in range(12)] for _ in range(12)
        ]
        if not any(any(row) for row in matrix):
            continue
        candidate = MOSPInstance.from_matrix(matrix, name="timeout")
        if _lower_bound(candidate) < _upper_bound(candidate)[0]:
            inst = candidate
            break

    if inst is None:
        pytest.skip("no instance found whose bounds leave a gap to search")

    value, ordering = solve_one_parallel(inst, workers=2, timeout=0.0, verbose=False)
    assert value is None
    assert ordering is None


def test_parallel_k_when_bounds_already_meet():
    """If tabu meets the lower bound, the answer needs no SAT call."""
    # Every customer needs every pattern: all stacks are open throughout, so
    # the lower bound (max customers per pattern) already equals the optimum.
    inst = MOSPInstance.from_matrix([[1] * 3 for _ in range(4)], name="complete")
    value, ordering = solve_one_parallel(inst, workers=4, verbose=False)
    assert value == _brute_force(inst) == 4
    assert max_open_stacks(inst, ordering) == value


# -------------------------------------------------------
# Sweep across instances
# -------------------------------------------------------


def _write_instance(path, name, matrix):
    rows = "\n".join(" ".join(str(v) for v in row) for row in matrix)
    path.write_text(f"{name}\n{len(matrix)} {len(matrix[0])}\n{rows}\n")


def test_sweep_solves_every_instance(tmp_path):
    """A sweep over a small directory solves and verifies each instance."""
    _write_instance(tmp_path / "a.txt", "a", [[1, 1, 0], [0, 1, 1]])
    _write_instance(tmp_path / "b.txt", "b", [[1, 0, 1], [0, 1, 1]])

    results = sweep(base_dir=tmp_path, workers=2, timeout=120.0,
                    solutions_dir=tmp_path / "solutions")

    assert len(results) == 2
    assert all(r["status"] == "solved" for r in results), results
    for row in results:
        assert row["mosp_value"] == row["verified"]


def test_sweep_writes_csv(tmp_path):
    """Results are persisted as they complete."""
    _write_instance(tmp_path / "a.txt", "a", [[1, 1, 0], [0, 1, 1]])
    out = tmp_path / "out" / "results.csv"

    sweep(base_dir=tmp_path, workers=2, timeout=120.0, output_csv=out,
          solutions_dir=tmp_path / "solutions")

    assert out.exists()
    lines = out.read_text().strip().splitlines()
    assert lines[0].startswith("dataset,filename,instance_name")
    assert len(lines) == 2


def test_sweep_respects_size_filters(tmp_path):
    """Size filters select which instances run."""
    _write_instance(tmp_path / "small.txt", "small", [[1, 1, 0], [1, 0, 1]])
    _write_instance(
        tmp_path / "big.txt", "big", [[1] * 6 for _ in range(6)]
    )

    only_big = sweep(base_dir=tmp_path, workers=2, timeout=120.0, min_size=5,
                     solutions_dir=tmp_path / "solutions")
    assert [r["instance_name"] for r in only_big] == ["big"]

    only_small = sweep(base_dir=tmp_path, workers=2, timeout=120.0, max_size=5,
                       solutions_dir=tmp_path / "solutions")
    assert [r["instance_name"] for r in only_small] == ["small"]


def test_sweep_on_empty_directory(tmp_path):
    assert sweep(base_dir=tmp_path, workers=2, timeout=10.0,
                 solutions_dir=tmp_path / "solutions") == []


def test_sweep_persists_witness_orderings(tmp_path):
    """The ordering is the result of a solve and must survive the run."""
    import json

    _write_instance(tmp_path / "a.txt", "keepme", [[1, 1, 0], [0, 1, 1]])
    solutions = tmp_path / "solutions"

    results = sweep(base_dir=tmp_path, workers=2, timeout=120.0,
                    solutions_dir=solutions)

    saved = list(solutions.glob("*.json"))
    assert len(saved) == 1, f"expected one cached solution, got {saved}"
    payload = json.loads(saved[0].read_text())
    assert payload["instance_name"] == "keepme"
    assert sorted(payload["ordering"]) == [0, 1, 2]
    assert payload["mosp_value"] == results[0]["mosp_value"]


def test_sweep_reuses_cached_solutions(tmp_path):
    """A second pass verifies from disk instead of re-solving."""
    _write_instance(tmp_path / "a.txt", "cached", [[1, 1, 0], [0, 1, 1]])
    solutions = tmp_path / "solutions"

    first = sweep(base_dir=tmp_path, workers=2, timeout=120.0, solutions_dir=solutions)
    second = sweep(base_dir=tmp_path, workers=2, timeout=120.0, solutions_dir=solutions)

    assert first[0]["mosp_value"] == second[0]["mosp_value"]
    assert second[0]["status"] == "solved"
