"""Guards on the dominance symmetry-breaking constraints.

The constraints are disabled because they lose optima (see the block in
`mosp_encoding.py`). These tests pin two things: that the dominance *relation*
is computed correctly, and that the encoding stays sound with the flag in its
default state. The last test is the one to run when attempting a fix.
"""

import itertools
import random

import pytest

from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from satisfiability.mosp_encoding import dominance_pairs, encode_mosp_decision


def _brute_force(inst):
    return min(
        max_open_stacks(inst, list(perm))
        for perm in itertools.permutations(range(inst.n_patterns))
    )


def _sat_optimum(inst, **kwargs):
    from pysat.solvers import Cadical195

    for k in range(inst.n_customers + 2):
        cnf, _, _ = encode_mosp_decision(inst, k, **kwargs)
        with Cadical195(bootstrap_with=cnf.clauses) as solver:
            if solver.solve():
                return k
    return None


def test_dominance_relation_matches_its_definition():
    """i dominates j iff the neighbours of j sit inside those of i, plus i."""
    matrix = [[0, 1, 0], [0, 1, 1], [1, 1, 0]]
    inst = MOSPInstance.from_matrix(matrix, name="d")

    neighbours = [set() for _ in range(inst.n_customers)]
    for pattern in range(inst.n_patterns):
        holders = set(inst.pattern_customers(pattern))
        for customer in holders:
            neighbours[customer] |= holders
    for customer in range(inst.n_customers):
        neighbours[customer].discard(customer)

    for dominant, dominated in dominance_pairs(inst):
        assert neighbours[dominated] <= neighbours[dominant] | {dominant}


def test_dominance_relation_is_acyclic():
    """Contradictory chains would make the constraints trivially unsatisfiable."""
    import networkx as nx

    rng = random.Random(0)
    for _ in range(40):
        matrix = [[rng.randint(0, 1) for _ in range(6)] for _ in range(6)]
        if not any(any(row) for row in matrix):
            continue
        inst = MOSPInstance.from_matrix(matrix, name="acyc")
        digraph = nx.DiGraph()
        digraph.add_edges_from(dominance_pairs(inst))
        assert nx.is_directed_acyclic_graph(digraph)


def test_dominance_is_off_by_default():
    """The default must stay sound while the constraints are known broken."""
    rng = random.Random(1)
    for _ in range(12):
        n_patterns = rng.randint(2, 5)
        matrix = [
            [rng.randint(0, 1) for _ in range(n_patterns)]
            for _ in range(rng.randint(2, 5))
        ]
        if not any(any(row) for row in matrix):
            continue
        inst = MOSPInstance.from_matrix(matrix, name="def")
        assert _sat_optimum(inst) == _brute_force(inst)


@pytest.mark.xfail(reason="dominance constraints lose optima; see mosp_encoding.py",
                   strict=True)
def test_dominance_preserves_optima():
    """Run this when attempting a fix: it should stop failing.

    Marked strict, so a fix that works will fail the suite as an unexpected
    pass and force this guard and the default to be revisited together.
    """
    rng = random.Random(0)
    for _ in range(60):
        n_patterns = rng.randint(2, 5)
        matrix = [
            [rng.randint(0, 1) for _ in range(n_patterns)]
            for _ in range(rng.randint(2, 5))
        ]
        if not any(any(row) for row in matrix):
            continue
        inst = MOSPInstance.from_matrix(matrix, name="dom")
        assert _sat_optimum(inst, dominance_breaking=True) == _brute_force(inst)
