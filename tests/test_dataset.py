"""paper2/dataset.py: the pieces whose correctness the dataset rests on, checked
against the independent checker and against brute force."""
import itertools
import random
import sys
from pathlib import Path

import numpy as np

from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from paper2 import dataset as ds

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "paper2"))
import dataset_check as dc  # noqa: E402


def _random_graph(rng, n, p):
    return [(u, v) for u in range(n) for v in range(u + 1, n) if rng.random() < p]


def _pathwidth_brute(n, edges):
    adj = dc.adjacency(n, edges)
    return min(dc.width_of_layout(adj, L) for L in itertools.permutations(range(n)))


def test_mosp_layout_width_is_open_stacks_minus_one_at_most():
    rng = random.Random(1)
    for _ in range(200):
        c, p = rng.randint(2, 7), rng.randint(1, 6)
        M = (np.array([[rng.random() < 0.4 for _ in range(p)] for _ in range(c)])).astype(int)
        for j in range(p):                       # every pattern has a customer
            if not M[:, j].any():
                M[rng.randrange(c), j] = 1
        inst = MOSPInstance.from_matrix(M.tolist())
        order = list(range(p))
        rng.shuffle(order)
        n, edges = ds._graph_from_matrix(M)
        width = ds.layout_width(n, edges, ds.mosp_layout(inst, order))
        assert width <= max_open_stacks(inst, order) - 1
        # and at an optimal pattern order it is the pathwidth (MOSP = pw + 1)
        best = min(max_open_stacks(inst, list(o)) for o in itertools.permutations(range(p)))
        if c <= 6:
            assert best - 1 == _pathwidth_brute(n, edges)


def test_minor_certificate_replays_in_the_checker():
    rng = random.Random(2)
    for _ in range(300):
        n = rng.randint(2, 9)
        edges = _random_graph(rng, n, rng.random())
        adj = dc.adjacency(n, edges)
        target = max(dc.degeneracy(adj), dc.contraction_degeneracy(adj) or 0)
        cert = ds.minor_certificate(n, edges, target)
        assert cert is not None
        assert dc.replay_minor(adj, cert["ops"]) >= target
        if n <= 7:
            assert target <= _pathwidth_brute(n, edges)


def test_layout_width_agrees_with_the_checker():
    rng = random.Random(3)
    for _ in range(200):
        n = rng.randint(1, 12)
        edges = _random_graph(rng, n, 0.3)
        L = list(range(n))
        rng.shuffle(L)
        assert ds.layout_width(n, edges, L) == dc.width_of_layout(dc.adjacency(n, edges), L)


def test_readers_agree_with_the_checker(tmp_path):
    p = tmp_path / "x.gr"
    p.write_text("c comment\np tw 4 3\n1 2\n2 3\n3 4\n3 4\n")
    n, edges = ds.read_graph_file(p)
    assert (n, set(edges)) == dc.read_source(p, "PACE 2016", "x")
    q = tmp_path / "x.dgf"
    q.write_text("p edge 3 2\ne 1 2\ne 2 3\n")
    assert ds.read_graph_file(q) == (3, [(0, 1), (1, 2)])


def test_perm_to_rep_maps_member_onto_representative():
    rep = dict(lab="2 0 1")
    mem = dict(lab="0 1 2")
    perm = ds._perm_to_rep(mem, rep)
    assert perm == [2, 0, 1]
