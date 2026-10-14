"""The statement proved in lean/MOSPFormalization/Grid.lean, checked on small grids.

`pathwidth_grid`: the (h, w)-grid has pathwidth min(h, w) unless h = w = 1,
where it is a single vertex of pathwidth 0 (`pathwidth_grid_one_one`).
Checked with the exact subset DP on every grid of at most 18 vertices,
including the paths (h = 1 or w = 1) and the non-square grids.
"""

import networkx as nx
import pytest

from fixed_parameter_algorithm.pathwidth import compute_pathwidth, compute_vertex_separation

GRIDS = [(h, w) for h in range(1, 7) for w in range(1, 7) if h * w <= 18]


def grid(h: int, w: int) -> nx.Graph:
    return nx.grid_2d_graph(h, w)


@pytest.mark.parametrize("h,w", GRIDS)
def test_pathwidth_grid(h, w):
    pw, _ = compute_pathwidth(grid(h, w))
    expected = 0 if (h, w) == (1, 1) else min(h, w)
    assert pw == expected


@pytest.mark.parametrize("h,w", GRIDS)
def test_row_major_layout_width(h, w):
    """The upper-bound layout of the proof: row-major, of width at most w."""
    G = grid(h, w)
    order = [(i, j) for i in range(h) for j in range(w)]
    assert compute_vertex_separation(G, order) <= w
