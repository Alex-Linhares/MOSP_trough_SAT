"""Tests for the overnight escalating-budget driver."""

from pathlib import Path

import pytest

from benchmarks.overnight import run_night, unsolved_instances


def _write_instance(path: Path, name: str, matrix: list[list[int]]) -> None:
    rows = "\n".join(" ".join(str(v) for v in row) for row in matrix)
    path.write_text(f"{name}\n{len(matrix)} {len(matrix[0])}\n{rows}\n")


@pytest.fixture
def two_instances(tmp_path):
    _write_instance(tmp_path / "a.txt", "a", [[1, 1, 0], [0, 1, 1]])
    _write_instance(tmp_path / "b.txt", "b", [[1, 0, 1], [1, 1, 0]])
    return tmp_path


def test_unsolved_lists_everything_when_cache_is_empty(two_instances):
    assert sorted(unsolved_instances(two_instances, two_instances / "sol")) == ["a", "b"]


def test_run_night_solves_and_caches(two_instances):
    solutions = two_instances / "sol"
    run_night(instance_dir=two_instances, solutions_dir=solutions,
              rounds=(60,), workers=2, results_dir=two_instances / "res")

    assert unsolved_instances(two_instances, solutions) == []
    assert sorted(p.name for p in solutions.glob("*.json")) == ["a.json", "b.json"]


def test_second_run_is_a_no_op(two_instances):
    """The cache is the state: a repeat run finds nothing left to do."""
    solutions = two_instances / "sol"
    run_night(instance_dir=two_instances, solutions_dir=solutions,
              rounds=(60,), workers=2, results_dir=two_instances / "res")
    before = {p.name: p.read_text() for p in solutions.glob("*.json")}

    run_night(instance_dir=two_instances, solutions_dir=solutions,
              rounds=(60,), workers=2, results_dir=two_instances / "res")
    after = {p.name: p.read_text() for p in solutions.glob("*.json")}

    assert before == after, "a repeat run must not rewrite solved instances"


def test_rounds_stop_early_once_everything_is_solved(two_instances):
    """Later rounds are skipped rather than re-running solved instances."""
    solutions = two_instances / "sol"
    results = two_instances / "res"
    run_night(instance_dir=two_instances, solutions_dir=solutions,
              rounds=(60, 3600, 10800), workers=2, results_dir=results)

    # Only the first round should have produced a CSV.
    assert len(list(results.glob("*round1.csv"))) == 1
    assert list(results.glob("*round2.csv")) == []


def test_hours_budget_blocks_rounds_it_cannot_honour(two_instances):
    """A round needing more per-instance time than remains is skipped.

    Otherwise it would report timeouts that only mean the clock ran out.
    """
    solutions = two_instances / "sol"
    results = two_instances / "res"
    # 3600s per instance against a ~0-hour budget: no round can run.
    run_night(instance_dir=two_instances, solutions_dir=solutions,
              rounds=(3600,), workers=2, hours=0.0001, results_dir=results)

    assert unsolved_instances(two_instances, solutions) == ["a", "b"]


def test_empty_directory(tmp_path):
    run_night(instance_dir=tmp_path, solutions_dir=tmp_path / "sol",
              rounds=(60,), workers=2, results_dir=tmp_path / "res")
    assert unsolved_instances(tmp_path, tmp_path / "sol") == []
