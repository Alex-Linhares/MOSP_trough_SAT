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


# -------------------------------------------------------
# Packed gate matrix layout
# -------------------------------------------------------


def test_packing_never_puts_overlapping_spans_on_one_track():
    """Two stacks open at the same moment cannot share a physical track."""
    from mosp.visualize import pack_into_tracks

    rng = random.Random(3)
    for _ in range(30):
        spans = []
        for _ in range(rng.randint(1, 12)):
            start = rng.randint(0, 20)
            spans.append((start, start + rng.randint(0, 8)))
        tracks = pack_into_tracks(spans)

        by_track = {}
        for (start, stop), track in zip(spans, tracks):
            for other_start, other_stop in by_track.get(track, []):
                assert stop < other_start or start > other_stop, (
                    f"({start},{stop}) overlaps ({other_start},{other_stop}) "
                    f"on track {track}"
                )
            by_track.setdefault(track, []).append((start, stop))


@pytest.mark.parametrize("seed", range(15))
def test_track_count_equals_open_stacks(seed):
    """Proposition 2 of Linhares & Yanasse: open stacks equal tracks.

    The greedy packing is optimal for intervals, so the number of tracks it
    uses must come out equal to the maximum number of simultaneously open
    stacks. If these ever diverged the figure would be captioned with a number
    the picture does not show.
    """
    from mosp.visualize import pack_into_tracks

    rng = random.Random(seed)
    n_patterns = rng.randint(1, 7)
    matrix = [
        [rng.randint(0, 1) for _ in range(n_patterns)]
        for _ in range(rng.randint(1, 7))
    ]
    inst = MOSPInstance.from_matrix(matrix, name=f"t{seed}")
    ordering = list(range(n_patterns))
    rng.shuffle(ordering)

    position = {p: i for i, p in enumerate(ordering)}
    spans = []
    for customer in range(inst.n_customers):
        steps = sorted(position[p] for p in inst.customer_patterns(customer))
        if steps:
            spans.append((steps[0], steps[-1]))

    expected = max_open_stacks(inst, ordering)
    if not spans:
        assert expected == 0
        return
    assert max(pack_into_tracks(spans)) + 1 == expected


def test_gate_matrix_figure_renders():
    from mosp.visualize import plot_gate_matrix

    matrix = [[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1]]
    inst = MOSPInstance.from_matrix(matrix, name="gm")
    figure = plot_gate_matrix(inst, [0, 1, 2, 3])
    assert "2 tracks = 2 open stacks" in figure.axes[0].get_title()
    matplotlib.pyplot.close(figure)


def test_track_comparison_renders_and_shares_scale():
    from mosp.visualize import plot_track_comparison

    sparse = MOSPInstance.from_matrix([[1, 1, 0, 0], [0, 0, 1, 1]], name="sparse")
    dense = MOSPInstance.from_matrix(
        [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]], name="dense"
    )
    figure = plot_track_comparison(
        [(sparse, [0, 1, 2, 3]), (dense, [0, 1, 2, 3])], labels=["s", "d"]
    )

    # Both panels must use the taller instance's scale, or the comparison of
    # heights — which is the entire point — would be meaningless.
    assert figure.axes[0].get_ylim() == figure.axes[1].get_ylim()
    assert "1 tracks" in figure.axes[0].get_title()
    assert "3 tracks" in figure.axes[1].get_title()
    matplotlib.pyplot.close(figure)
