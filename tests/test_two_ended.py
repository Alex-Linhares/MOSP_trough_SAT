"""The two-ended frontier enumeration (`learning.two_ended`) against a subset DP."""
from math import comb

import numpy as np
import pytest

from learning.obstruction_ledger import adjacency_from_edges
from learning.two_ended import backward_layers, forward_layers


def _layers_dp(adj, k):
    n = len(adj)
    bound = k - 1
    full = (1 << n) - 1

    def cost(S):
        NS = 0
        for u in range(n):
            if S >> u & 1:
                NS |= adj[u]
        return (NS & ~S).bit_count()

    F = [S for S in range(1 << n) if cost(S) <= bound]
    reach = {0}
    for S in sorted(F, key=lambda x: bin(x).count("1")):
        if S and any((S & ~(1 << v)) in reach for v in range(n) if S >> v & 1):
            reach.add(S)
    co = {full}
    for S in sorted(F, key=lambda x: -bin(x).count("1")):
        if S != full and any((S | (1 << v)) in co for v in range(n) if not S >> v & 1):
            co.add(S)
    Rf = [sum(1 for S in reach if bin(S).count("1") == i) for i in range(n + 1)]
    Rb = [sum(1 for S in co if bin(S).count("1") == i) for i in range(n + 1)]
    return Rf, Rb


def _trim_forward(Rf):
    out = []
    for x in Rf:
        out.append(x)
        if x == 0:
            break
    return out


def _trim_backward(Rb):
    out = []
    for x in reversed(Rb):
        out.append(x)
        if x == 0:
            break
    return out


@pytest.mark.parametrize("seed", range(12))
def test_layers_agree_with_subset_dp(seed):
    rng = np.random.default_rng(seed)
    n = int(rng.integers(4, 9))
    edges = [(a, b) for a in range(n) for b in range(a + 1, n) if rng.random() < 0.4]
    adj = adjacency_from_edges(n, edges)
    for k in range(1, n + 1):
        Rf, Rb = _layers_dp(adj, k)
        f, _closed, cens_f = forward_layers(adj, k, 10 ** 6)
        b, cens_b = backward_layers(adj, k, 10 ** 6)
        assert not cens_f and not cens_b
        assert f == _trim_forward(Rf)
        assert b == _trim_backward(Rb)


def test_backward_frontier_is_binomial_below_the_bound():
    """Every set missing at most k - 1 vertices is feasible and co-reachable:
    |N(S) \\ S| <= |V \\ S|, so R_b(n - j) = C(n, j) for j <= k - 1."""
    rng = np.random.default_rng(7)
    n = 12
    edges = [(a, b) for a in range(n) for b in range(a + 1, n) if rng.random() < 0.3]
    adj = adjacency_from_edges(n, edges)
    k = 4
    b, cens = backward_layers(adj, k, 10 ** 6)
    assert not cens
    for j in range(k):
        assert b[j] == comb(n, j)


def test_forward_and_backward_walls_agree_on_feasibility():
    rng = np.random.default_rng(11)
    for _ in range(10):
        n = int(rng.integers(5, 9))
        edges = [(a, b) for a in range(n) for b in range(a + 1, n) if rng.random() < 0.5]
        adj = adjacency_from_edges(n, edges)
        for k in range(1, n + 1):
            f, _c, _ = forward_layers(adj, k, 10 ** 6)
            b, _ = backward_layers(adj, k, 10 ** 6)
            feasible_f = len(f) == n + 1 and f[-1] == 1
            feasible_b = len(b) == n + 1 and b[-1] == 1
            assert feasible_f == feasible_b
