"""Tests for MOSP instance parsing and representation."""

import tempfile
from pathlib import Path

import numpy as np
import pytest

from mosp.instance import MOSPInstance


def test_from_matrix():
    matrix = [[1, 0, 1], [0, 1, 1], [1, 1, 0]]
    inst = MOSPInstance.from_matrix(matrix, name="test")
    assert inst.n_customers == 3
    assert inst.n_patterns == 3
    assert inst.name == "test"
    assert inst.matrix.shape == (3, 3)


def test_from_matrix_non_square():
    matrix = [[1, 0, 1, 0], [0, 1, 0, 1]]
    inst = MOSPInstance.from_matrix(matrix)
    assert inst.n_customers == 2
    assert inst.n_patterns == 4


def test_pattern_customers():
    matrix = [
        [1, 0, 1],
        [0, 1, 1],
        [1, 1, 0],
    ]
    inst = MOSPInstance.from_matrix(matrix)
    assert inst.pattern_customers(0) == {0, 2}
    assert inst.pattern_customers(1) == {1, 2}
    assert inst.pattern_customers(2) == {0, 1}


def test_customer_patterns():
    matrix = [
        [1, 0, 1],
        [0, 1, 1],
        [1, 1, 0],
    ]
    inst = MOSPInstance.from_matrix(matrix)
    assert inst.customer_patterns(0) == {0, 2}
    assert inst.customer_patterns(1) == {1, 2}
    assert inst.customer_patterns(2) == {0, 1}


def test_file_roundtrip():
    matrix = [
        [1, 0, 1],
        [0, 1, 1],
        [1, 1, 0],
    ]
    inst = MOSPInstance.from_matrix(matrix, name="roundtrip_test")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".mosp", delete=False) as f:
        path = Path(f.name)

    inst.to_file(path)
    loaded = MOSPInstance.from_file(path)

    assert loaded.name == "roundtrip_test"
    assert loaded.n_customers == 3
    assert loaded.n_patterns == 3
    np.testing.assert_array_equal(loaded.matrix, inst.matrix)

    path.unlink()


def test_from_file_format():
    content = "my_instance\n3 4\n1 0 1 0\n0 1 0 1\n1 1 0 0\n"
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".mosp", delete=False
    ) as f:
        f.write(content)
        path = Path(f.name)

    inst = MOSPInstance.from_file(path)
    assert inst.name == "my_instance"
    assert inst.n_customers == 3
    assert inst.n_patterns == 4
    assert inst.matrix[0, 0] == 1
    assert inst.matrix[0, 1] == 0
    assert inst.matrix[2, 3] == 0

    path.unlink()
