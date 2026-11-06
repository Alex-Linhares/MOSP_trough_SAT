"""Appendix D.2 (paper_flow.txt lines 4327-4349): the fixed-density encoding of a
k-CNF as a Boolean tensor network, implemented literally, and its contraction
over Z/2^{n+1} compared with a brute-force model count.

Choices the text leaves open (recorded in the report):
  * the shape of the equality tree for a variable with d >= 3 ports: we use a
    caterpillar (any tree with d leaves and d-2 trivalent internal vertices
    gives the same contraction, since every common value extends uniquely);
  * the port order delta(v) at each vertex: irrelevant to the contraction;
  * the subdivision vertex is a binary equality tensor on its two edges.

Run:  python3 -I d2_cnf_network.py [seed] [trials]
"""
from __future__ import annotations
import random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from itertools import product
from tn import Network


def build_d2_network(n, clauses, subdivide=True):
    """clauses: list of lists of nonzero ints (literal v>0 means x_v, v<0 means not x_v).
    Returns (network, number_of_unused_variables, number_of_edges_before_subdivision)."""
    net = Network()
    # normalise clauses: drop tautologies; detect empty clause
    clean = []
    for c in clauses:
        lits = set(c)
        if any(-l in lits for l in lits):
            continue  # tautology may be dropped
        clean.append(sorted(lits, key=abs))
    if any(len(c) == 0 for c in clean):
        return None, None, None  # empty clause gives count zero
    # ports: for each clause and each distinct variable, one edge
    var_ports = {v: [] for v in range(1, n + 1)}
    clause_vertices = []
    for c in clean:
        vars_ = sorted({abs(l) for l in c})
        edges = [net.new_edge() for _ in vars_]
        for v, e in zip(vars_, edges):
            var_ports[v].append(e)
        signs = {abs(l): (l > 0) for l in c}

        def sat(bits, vars_=vars_, signs=signs):
            return 1 if any((b == 1) == signs[v] for v, b in zip(vars_, bits)) else 0
        clause_vertices.append(net.add_vertex(edges, sat))
    unused = 0
    for v in range(1, n + 1):
        ports = var_ports[v]
        d = len(ports)
        if d == 0:
            unused += 1
        elif d == 1:
            net.add_vertex(ports, lambda b: 1)                       # unary (1,1)
        elif d == 2:
            net.add_vertex(ports, lambda b: 1 if b[0] == b[1] else 0)  # binary equality
        else:
            # caterpillar tree with d external ports and d-2 trivalent equality vertices
            eq3 = lambda b: 1 if b[0] == b[1] == b[2] else 0
            internal = [net.new_edge() for _ in range(d - 3)]
            if d == 3:
                net.add_vertex(ports, eq3)
            else:
                net.add_vertex([ports[0], ports[1], internal[0]], eq3)
                for j in range(1, d - 3):
                    net.add_vertex([internal[j - 1], ports[j + 1], internal[j]], eq3)
                net.add_vertex([internal[d - 4], ports[d - 2], ports[d - 1]], eq3)
    edges_before = net.n_edges
    if subdivide:
        # subdivide every edge once by a binary equality tensor
        old_vertices = net.vertices
        net2 = Network()
        # each old edge e becomes two edges (e_a, e_b) joined at a new vertex
        emap = {}
        for e in range(edges_before):
            emap[e] = (net2.new_edge(), net2.new_edge())
        for edges, table in old_vertices:
            # the first time an old edge is seen it takes copy a, the second time copy b
            pass
        seen = {}
        for edges, table in old_vertices:
            new_edges = []
            for e in edges:
                k = seen.get(e, 0)
                seen[e] = k + 1
                new_edges.append(emap[e][k])
            net2.vertices.append((new_edges, dict(table)))
        for e in range(edges_before):
            assert seen.get(e, 0) == 2, "edge must have two endpoints"
            net2.add_vertex(list(emap[e]), lambda b: 1 if b[0] == b[1] else 0)
        net = net2
    return net, unused, edges_before


def brute_count(n, clauses):
    cnt = 0
    for x in product((0, 1), repeat=n):
        ok = True
        for c in clauses:
            if not any((x[abs(l) - 1] == 1) == (l > 0) for l in c):
                ok = False
                break
        cnt += ok
    return cnt


def random_kcnf(n, m, k, rng):
    cl = []
    for _ in range(m):
        vs = rng.sample(range(1, n + 1), k)
        cl.append([v if rng.random() < 0.5 else -v for v in vs])
    return cl


def count_by_contraction(n, clauses):
    net, unused, _ = build_d2_network(n, clauses)
    if net is None:
        return 0
    P = n + 1
    mod = 1 << P
    z = net.contract(reduce=lambda v: v % mod)
    z = (z * pow(2, unused, mod)) % mod
    return z


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    trials = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    rng = random.Random(seed)
    fails = 0
    done = 0
    maxdeg_pre, maxdeg_post, bip_ok = 0, 0, True
    for trial in range(trials):
        n = rng.randint(1, 12)
        k = rng.choice([2, 3, 3, 3, 4])
        if k > n:
            k = n
        m = rng.randint(0, 3 * n)
        cl = random_kcnf(n, m, k, rng)
        # occasionally inject a tautology and duplicate literals
        if rng.random() < 0.2 and n >= 2:
            cl.append([1, -1, 2])
        if rng.random() < 0.2:
            cl.append([1, 1, 1][:k])
        ref = brute_count(n, cl)
        got = count_by_contraction(n, cl)
        net, unused, _ = build_d2_network(n, cl)
        if net is not None:
            if not net.is_bipartite():
                bip_ok = False
            maxdeg_post = max(maxdeg_post, net.max_degree())
            netpre, _, _ = build_d2_network(n, cl, subdivide=False)
            maxdeg_pre = max(maxdeg_pre, netpre.max_degree())
        done += 1
        if got != ref:
            fails += 1
            print("MISMATCH", n, k, cl, "brute", ref, "contraction", got)
    # edge cases: empty formula, empty clause, all-tautology formula
    assert count_by_contraction(3, []) == 8
    assert count_by_contraction(3, [[]]) == 0
    assert count_by_contraction(3, [[1, -1]]) == 8
    assert count_by_contraction(0, []) == 1
    print(f"D.2 encoding: {done} random instances (n<=12), {fails} mismatches; "
          f"bipartite after subdivision: {bip_ok}; max degree before/after subdivision: {maxdeg_pre}/{maxdeg_post}")


if __name__ == "__main__":
    main()
