"""Exact Boolean tensor networks, as defined in Appendix D.1 of the manuscript.

A network is a multigraph whose edges carry one bit each.  Every vertex v has
an ordered list delta(v) of incident edge ids and a tensor T_v mapping each
Boolean assignment of those edges to a ring element.  The contraction is

    Z = sum over x in {0,1}^E  of  prod over v  T_v(x restricted to delta(v)).

Ring elements are arbitrary Python objects supporting +, * and the integers
0, 1 (ints, Fractions, or the truncated polynomials in ringv.py).  The
contraction is computed by exact variable elimination over the edge bits, so
no identity from the paper is assumed anywhere in this file.
"""
from __future__ import annotations
from itertools import product


class Network:
    def __init__(self):
        self.n_edges = 0
        self.vertices = []      # list of (edge_id_list, table) ; table: dict bits-tuple -> ring element

    def new_edge(self):
        e = self.n_edges
        self.n_edges += 1
        return e

    def add_vertex(self, edges, fn):
        """edges: ordered list of edge ids; fn: tuple of bits -> ring element."""
        table = {}
        for bits in product((0, 1), repeat=len(edges)):
            val = fn(bits)
            if val != 0:
                table[bits] = val
        self.vertices.append((list(edges), table))
        return len(self.vertices) - 1

    def max_degree(self):
        return max((len(e) for e, _ in self.vertices), default=0)

    def degrees(self):
        return [len(e) for e, _ in self.vertices]

    def endpoints(self):
        ends = {}
        for vi, (edges, _) in enumerate(self.vertices):
            for e in edges:
                ends.setdefault(e, []).append(vi)
        return ends

    def is_bipartite(self):
        ends = self.endpoints()
        adj = {i: set() for i in range(len(self.vertices))}
        for e, vs in ends.items():
            if len(vs) != 2:
                return False
            a, b = vs
            adj[a].add(b); adj[b].add(a)
        colour = {}
        for s in adj:
            if s in colour:
                continue
            colour[s] = 0
            stack = [s]
            while stack:
                x = stack.pop()
                for y in adj[x]:
                    if y not in colour:
                        colour[y] = 1 - colour[x]
                        stack.append(y)
                    elif colour[y] == colour[x]:
                        return False
        return True

    # ---- exact contraction by variable elimination -------------------
    def contract(self, reduce=None):
        """Exact contraction.  `reduce` is an optional normalisation applied to
        every ring element after each multiplication/addition (e.g. mod 2^P)."""
        red = reduce if reduce is not None else (lambda v: v)
        factors = [(list(edges), dict(table)) for edges, table in self.vertices]
        # Every edge must have exactly two endpoints (a multigraph edge); an
        # edge with one endpoint would be a dangling port and is summed out too.
        alive = list(range(self.n_edges))
        while alive:
            # choose the edge whose elimination creates the smallest scope
            best = None
            for e in alive:
                idx = [i for i, (sc, _) in enumerate(factors) if e in sc]
                scope = set()
                for i in idx:
                    scope |= set(factors[i][0])
                size = len(scope)
                if best is None or size < best[0]:
                    best = (size, e, idx)
            _, e, idx = best
            # multiply the factors containing e, then sum out e
            merged_scope, merged = None, None
            for i in idx:
                sc, tb = factors[i]
                if merged is None:
                    merged_scope, merged = list(sc), dict(tb)
                else:
                    merged_scope, merged = _multiply(merged_scope, merged, sc, tb, red)
            merged_scope, merged = _sum_out(merged_scope, merged, e, red)
            factors = [f for i, f in enumerate(factors) if i not in idx]
            factors.append((merged_scope, merged))
            alive.remove(e)
        # all scopes are empty now; multiply the scalars
        total = 1
        for sc, tb in factors:
            assert sc == []
            total = red(total * tb.get((), 0))
        return total


def _multiply(sc1, t1, sc2, t2, red):
    scope = list(sc1) + [e for e in sc2 if e not in sc1]
    pos1 = [scope.index(e) for e in sc1]
    pos2 = [scope.index(e) for e in sc2]
    shared = [e for e in sc2 if e in sc1]
    sh1 = [sc1.index(e) for e in shared]
    sh2 = [sc2.index(e) for e in shared]
    # index t2 by its shared-bit pattern
    buckets = {}
    for b2, v2 in t2.items():
        key = tuple(b2[i] for i in sh2)
        buckets.setdefault(key, []).append((b2, v2))
    out = {}
    for b1, v1 in t1.items():
        key = tuple(b1[i] for i in sh1)
        for b2, v2 in buckets.get(key, ()):
            bits = [0] * len(scope)
            for p, b in zip(pos1, b1):
                bits[p] = b
            for p, b in zip(pos2, b2):
                bits[p] = b
            bits = tuple(bits)
            val = red(v1 * v2)
            if bits in out:
                out[bits] = red(out[bits] + val)
            else:
                out[bits] = val
    return scope, {k: v for k, v in out.items() if v != 0}


def _sum_out(scope, table, e, red):
    p = scope.index(e)
    new_scope = scope[:p] + scope[p + 1:]
    out = {}
    for bits, v in table.items():
        nb = bits[:p] + bits[p + 1:]
        if nb in out:
            out[nb] = red(out[nb] + v)
        else:
            out[nb] = v
    return new_scope, {k: v for k, v in out.items() if v != 0}


def brute_force_contract(net: Network):
    """Reference: literal sum over all 2^E edge assignments (tiny networks only)."""
    total = 0
    for x in product((0, 1), repeat=net.n_edges):
        term = 1
        for edges, table in net.vertices:
            bits = tuple(x[e] for e in edges)
            term = term * table.get(bits, 0)
            if term == 0:
                break
        total = total + term
    return total
