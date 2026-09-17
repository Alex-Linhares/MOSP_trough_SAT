"""Tests for sharing solutions between identical instances."""

import json

import pytest

from benchmarks.dedupe import dedupe, group_identical
from mosp.instance import MOSPInstance
from satisfiability.mosp_solver import _save_solution


def _write_instance(path, name, matrix):
    rows = "\n".join(" ".join(str(v) for v in row) for row in matrix)
    path.write_text(f"{name}\n{len(matrix)} {len(matrix[0])}\n{rows}\n")


@pytest.fixture
def twin_instances(tmp_path):
    """The same matrix under two names, plus an unrelated one."""
    # Orderings of this matrix genuinely differ: [0,2,1,3] gives 2, [0,1,2,3]
    # gives 3, so there is a better solution to propagate.
    matrix = [[1, 0, 1, 0], [0, 1, 0, 1], [1, 1, 0, 0]]
    _write_instance(tmp_path / "a.txt", "twinA", matrix)
    _write_instance(tmp_path / "b.txt", "twinB", matrix)
    _write_instance(tmp_path / "c.txt", "other", [[1, 0, 0, 1], [0, 1, 0, 0]])
    return tmp_path


def test_groups_only_identical_matrices(twin_instances):
    groups = group_identical(twin_instances)
    assert len(groups) == 1
    assert sorted(inst.name for inst in groups[0]) == ["twinA", "twinB"]


def test_same_shape_is_not_enough(tmp_path):
    """Instances sharing dimensions but not content must not be grouped."""
    _write_instance(tmp_path / "a.txt", "x", [[1, 1, 0], [0, 1, 1]])
    _write_instance(tmp_path / "b.txt", "y", [[1, 0, 1], [1, 1, 0]])
    assert group_identical(tmp_path) == []


def test_better_solution_is_propagated(twin_instances, tmp_path):
    solutions = tmp_path / "sol"
    instances = {i.name: i for g in group_identical(twin_instances) for i in g}

    _save_solution(instances["twinA"], 2, [0, 2, 1, 3], solutions)
    _save_solution(instances["twinB"], 3, [0, 1, 2, 3], solutions)

    transfers = dedupe(twin_instances, solutions)

    assert transfers == [("twinA", "twinB", 3, 2)]
    payload = json.loads((solutions / "twinB.json").read_text())
    assert payload["mosp_value"] == 2


def test_dry_run_changes_nothing(twin_instances, tmp_path):
    solutions = tmp_path / "sol"
    instances = {i.name: i for g in group_identical(twin_instances) for i in g}
    _save_solution(instances["twinA"], 2, [0, 2, 1, 3], solutions)
    _save_solution(instances["twinB"], 3, [0, 1, 2, 3], solutions)

    assert dedupe(twin_instances, solutions, dry_run=True)
    assert json.loads((solutions / "twinB.json").read_text())["mosp_value"] == 3


def test_equal_values_are_left_alone(twin_instances, tmp_path):
    solutions = tmp_path / "sol"
    instances = {i.name: i for g in group_identical(twin_instances) for i in g}
    _save_solution(instances["twinA"], 2, [0, 2, 1, 3], solutions)
    _save_solution(instances["twinB"], 2, [0, 2, 1, 3], solutions)

    assert dedupe(twin_instances, solutions) == []


def test_saves_never_replace_a_better_value(tmp_path):
    """The property that makes concurrent writers and dedupe safe together."""
    inst = MOSPInstance.from_matrix([[1, 1, 0], [0, 1, 1]], name="mono")

    _save_solution(inst, 3, [0, 1, 2], tmp_path)
    _save_solution(inst, 2, [2, 1, 0], tmp_path)
    _save_solution(inst, 7, [1, 0, 2], tmp_path)

    payload = json.loads((tmp_path / "mono.json").read_text())
    assert payload["mosp_value"] == 2, "a worse value must not overwrite a better"


def test_a_mismatched_ordering_is_refused(twin_instances, tmp_path):
    """Grouping alone never licenses a transfer.

    The ordering is re-simulated against the receiving instance, so a claimed
    value that the ordering does not achieve is rejected rather than copied.
    """
    solutions = tmp_path / "sol"
    instances = {i.name: i for g in group_identical(twin_instances) for i in g}

    # A value no ordering of this matrix achieves.
    _save_solution(instances["twinA"], 1, [0, 2, 1, 3], solutions)
    _save_solution(instances["twinB"], 3, [0, 1, 2, 3], solutions)

    assert dedupe(twin_instances, solutions) == []
    assert json.loads((solutions / "twinB.json").read_text())["mosp_value"] == 3
