"""The checkpoint relaxation of vertex separation (`learning.checkpoint_bound`)."""
import itertools

import numpy as np
import pytest

from learning.checkpoint_bound import boundary, checkpoint_cnf, check_witness, decide, even_sizes, scan_down
from learning.checkpoint_refine import refine, segment_fills
from learning.obstruction_expansion import closed_masks, closed_masks_from_matrix
from learning.obstruction_ledger import adjacency_from_edges


def _closed(n, edges):
    return closed_masks(adjacency_from_edges(n, edges))


def _vs_brute(closed):
    """Vertex separation by enumerating every layout (n <= 7)."""
    n = len(closed)
    best = n
    for order in itertools.permutations(range(n)):
        S = 0
        worst = 0
        for v in order[:-1]:
            S |= 1 << v
            worst = max(worst, boundary(closed, S))
        best = min(best, worst)
    return best


GRAPHS = {
    "P5": (5, [(0, 1), (1, 2), (2, 3), (3, 4)]),
    "C5": (5, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]),
    "K4": (4, [(a, b) for a in range(4) for b in range(a + 1, 4)]),
    "K23": (5, [(a, b) for a in range(2) for b in range(2, 5)]),
    "star+tri": (6, [(0, 1), (0, 2), (0, 3), (3, 4), (4, 5), (3, 5)]),
    "petersen-ish": (7, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 0), (0, 3), (1, 4), (2, 5)]),
}


@pytest.mark.parametrize("name", list(GRAPHS))
def test_full_chain_is_exact(name):
    n, edges = GRAPHS[name]
    closed = _closed(n, edges)
    vs = _vs_brute(closed)
    full = list(range(1, n))
    assert decide(closed, full, vs - 1)["answer"] is False if vs >= 1 else True
    r = decide(closed, full, vs)
    assert r["answer"] is True
    check_witness(closed, r["sets"], full, vs)


@pytest.mark.parametrize("name", list(GRAPHS))
def test_fewer_checkpoints_never_prove_more(name):
    n, edges = GRAPHS[name]
    closed = _closed(n, edges)
    vs = _vs_brute(closed)
    for c in range(1, n - 1):
        sizes = even_sizes(n, c)
        # UNSAT at b proves vs >= b + 1, so no UNSAT may appear at b >= vs
        for b in range(vs, n):
            assert decide(closed, sizes, b)["answer"] is True


def test_single_checkpoint_is_harper():
    """One checkpoint at size i is min over |S| = i of the inner boundary."""
    n, edges = GRAPHS["petersen-ish"]
    closed = _closed(n, edges)
    for i in range(1, n):
        harper = min(boundary(closed, S) for S in range(1, 1 << n) if bin(S).count("1") == i)
        r = scan_down(closed, [i], n - 1, 0, None)
        assert r["vs_floor"] == harper, (i, r)


def test_witness_check_rejects_bad_sets():
    n, edges = GRAPHS["C5"]
    closed = _closed(n, edges)
    with pytest.raises(AssertionError):
        check_witness(closed, [0b00011, 0b00101], [2, 2], 5)   # not nested
    with pytest.raises(AssertionError):
        check_witness(closed, [0b00011], [3], 5)               # wrong size
    with pytest.raises(AssertionError):
        check_witness(closed, [0b00101], [2], 1)               # boundary 2 > 1


def test_scan_down_monotone_and_mosp_units():
    matrix = np.array([[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1], [1, 0, 0, 1]])  # C4 on customers: vs 2, MOSP 3
    closed = closed_masks_from_matrix(matrix)
    r = scan_down(closed, [1, 2, 3], 3, 0, None)
    assert r["status"] == "unsat" and r["vs_floor"] == 2


@pytest.mark.parametrize("name", ["C5", "K23", "star+tri", "petersen-ish"])
def test_refine_agrees_with_brute_force(name):
    n, edges = GRAPHS[name]
    closed = _closed(n, edges)
    vs = _vs_brute(closed)
    assert refine(closed, vs - 1)["answer"] == "unsat"
    assert refine(closed, vs)["answer"] == "sat"


def test_segment_fills_exact():
    n, edges = GRAPHS["P5"]
    closed = _closed(n, edges)
    # from {0} to {0,1,2,3}: the path extends with boundary 1
    assert segment_fills(closed, 0b00001, 0b01111, 1, None) is True
    # from {0} to {0,2,3,4}: vertex 2 enters before 1, so {0,2} has boundary 2
    assert segment_fills(closed, 0b00001, 0b11101, 1, None) is False
