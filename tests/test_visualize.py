"""Tests for the packed gate matrix drawing.

The invariant that matters: the picture must agree with the solver. Column sums
of the fill-in matrix are open-stack counts, so their maximum has to equal what
`max_open_stacks` reports — a figure that disagreed with the value printed on it
would be worse than no figure.
"""

import itertools
import random

import matplotlib
import numpy as np
import pytest

matplotlib.use("Agg")

from mosp.instance import MOSPInstance  # noqa: E402
from mosp.verify import max_open_stacks  # noqa: E402
from mosp.visualize import (  # noqa: E402
    open_counts,
    packed_matrix,
    plot_solution,
)


def test_packed_matrix_on_a_hand_checked_example():
    """Customer 0 needs patterns 0 and 2, so its stack spans steps 0..2."""
    matrix = [[1, 0, 1], [0, 1, 0]]
    inst = MOSPInstance.from_matrix(matrix, name="hand")

    packed = packed_matrix(inst, [0, 1, 2])

    assert packed[0].tolist() == [1, 1, 1], "row 0 fills the gap between its 1s"
    assert packed[1].tolist() == [0, 1, 0], "row 1 opens and closes at step 1"
    assert open_counts(packed).tolist() == [1, 2, 1]


@pytest.mark.parametrize("seed", range(20))
def test_peak_of_packed_matrix_equals_simulation(seed):
    """The figure's headline number must match the solver's own count."""
    rng = random.Random(seed)
    n_patterns = rng.randint(1, 6)
    matrix = [
        [rng.randint(0, 1) for _ in range(n_patterns)]
        for _ in range(rng.randint(1, 6))
    ]
    inst = MOSPInstance.from_matrix(matrix, name=f"v{seed}")
    ordering = list(range(n_patterns))
    rng.shuffle(ordering)

    peak = int(open_counts(packed_matrix(inst, ordering)).max())
    assert peak == max_open_stacks(inst, ordering)


def test_row_order_cannot_change_the_counts():
    """Sorting rows is cosmetic: a column sum does not depend on row order."""
    rng = random.Random(4)
    matrix = [[rng.randint(0, 1) for _ in range(7)] for _ in range(7)]
    inst = MOSPInstance.from_matrix(matrix, name="sorted")
    packed = packed_matrix(inst, list(range(7)))

    # Index-based permutation: random.shuffle on a 2D array swaps row *views*,
    # which aliases and silently corrupts the array rather than reordering it.
    order = list(range(packed.shape[0]))
    rng.shuffle(order)
    shuffled = packed[order]

    assert sorted(shuffled.tolist()) == sorted(packed.tolist()), "same rows"
    assert open_counts(packed).tolist() == open_counts(shuffled).tolist()


def test_reversing_the_sequence_preserves_the_peak():
    """Yanasse (1997c): a sequence and its reverse have the same maximum."""
    rng = random.Random(9)
    matrix = [[rng.randint(0, 1) for _ in range(8)] for _ in range(8)]
    inst = MOSPInstance.from_matrix(matrix, name="rev")
    order = list(range(8))

    forward = open_counts(packed_matrix(inst, order)).max()
    backward = open_counts(packed_matrix(inst, order[::-1])).max()
    assert forward == backward


@pytest.mark.parametrize("n_colors", [5, 10])
@pytest.mark.parametrize("show_counts", [True, False])
def test_figure_renders(n_colors, show_counts):
    matrix = [[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1]]
    inst = MOSPInstance.from_matrix(matrix, name="fig")

    figure = plot_solution(inst, [0, 1, 2, 3], n_colors=n_colors,
                           show_counts=show_counts)
    assert figure is not None
    assert "max open stacks = 2" in figure.axes[0].get_title()
    matplotlib.pyplot.close(figure)


def test_figure_handles_customers_with_no_patterns():
    """An empty row has no span to draw and must not break the layout."""
    inst = MOSPInstance.from_matrix([[1, 1], [0, 0]], name="empty-row")
    figure = plot_solution(inst, [0, 1])
    assert figure is not None
    matplotlib.pyplot.close(figure)
