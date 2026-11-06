"""Audit of Appendix D.2 (fixed clause density): build the clause/equality-tree
tensor network for a k-CNF, count edges, vertices and maximum degree, and check
that its contraction equals #F by an honest (sparse) tensor contraction.

Run:  python3 -I d2_network.py
"""
import itertools, math, random, sys
from collections import defaultdict

def build_network(n, clauses, k):
    """clauses: list of lists of (var, neg) literals. Returns (vertices, edges).
    vertices: dict id -> ('clause', literal list) | ('eq', arity) | ('one',)
    edges: list of (u, v); ports are implicit (order of appearance in δ(v))."""
    V = {}
    E = []
    def newv(kind):
        i = len(V); V[i] = kind; return i
    ports = defaultdict(list)       # var -> list of (clause vertex)
    for cl in clauses:
        lits = {}
        taut = False
        for (v, b) in cl:
            if v in lits and lits[v] != b: taut = True
            lits[v] = b
        if taut: continue           # tautology dropped
        if not lits:                # empty clause: count zero
            return None
        cv = newv(('clause', tuple(sorted(lits.items()))))
        for v in lits: ports[v].append(cv)
    for v, cvs in sorted(ports.items()):   # increasing var: clause port order = sorted lits
        d = len(cvs)
        if d == 1:
            u = newv(('one',)); E.append((cvs[0], u))
        elif d == 2:
            u = newv(('eq',)); E.append((cvs[0], u)); E.append((cvs[1], u))
        else:
            # caterpillar tree with d-2 trivalent internal vertices
            internal = [newv(('eq',)) for _ in range(d - 2)]
            E.append((cvs[0], internal[0])); E.append((cvs[1], internal[0]))
            for j in range(1, d - 2):
                E.append((internal[j-1], internal[j]))
                E.append((cvs[j+1], internal[j]))
            E.append((cvs[d-1], internal[d-3]))
    # subdivide every edge once by a binary equality tensor
    nold = len(V)
    E2 = []
    for (a, b) in E:
        u = newv(('eq',)); E2.append((a, u)); E2.append((u, b))
    used = len(ports)
    return V, E2, used, nold

def check_bipartite(V, E, nold):
    # old vertices (id < nold) on one side, subdivision vertices on the other
    return all((a < nold) != (b < nold) for (a, b) in E)

def tensor(kind, deg):
    """dict port-assignment -> value"""
    T = {}
    if kind[0] == 'clause':
        lits = kind[1]
        for bits in itertools.product((0, 1), repeat=deg):
            sat = any(x ^ b for x, (v, b) in zip(bits, lits))
            T[bits] = 1 if sat else 0
    elif kind[0] == 'eq':
        T[(0,)*deg] = 1; T[(1,)*deg] = 1
    else:
        T[(0,)] = 1; T[(1,)] = 1
    return T

def contract(V, E):
    """Honest contraction: tensors as sparse dicts keyed by (edge id -> bit)
    frozen tuples; eliminate edges one by one."""
    inc = defaultdict(list)
    for eid, (a, b) in enumerate(E):
        inc[a].append(eid); inc[b].append(eid)
    # tensor as dict: tuple(sorted (eid,bit)) -> value
    tens = {}
    for v, kind in V.items():
        eids = inc[v]
        T = tensor(kind, len(eids))
        tens[v] = {tuple(sorted(zip(eids, bits))): val for bits, val in T.items() if val}
    # merge the endpoints of each edge, summing the edge bit
    owner = {v: v for v in V}
    def find(v):
        while owner[v] != v: v = owner[v]
        return v
    for eid, (a, b) in enumerate(E):
        ra, rb = find(a), find(b)
        if ra == rb:
            T = tens[ra]; new = defaultdict(int)
            for key, val in T.items():
                d = dict(key); d.pop(eid); new[tuple(sorted(d.items()))] += val
            tens[ra] = dict(new); continue
        Ta, Tb = tens[ra], tens[rb]
        new = defaultdict(int)
        byb = defaultdict(list)
        for key, val in Tb.items():
            d = dict(key); bit = d.pop(eid); byb[bit].append((d, val))
        for key, val in Ta.items():
            d = dict(key); bit = d.pop(eid)
            for d2, val2 in byb[bit]:
                # shared, not-yet-eliminated edges must carry equal bits
                if any(e in d and d[e] != bb for e, bb in d2.items()): continue
                dd = dict(d); dd.update(d2)
                new[tuple(sorted(dd.items()))] += val * val2
        tens[ra] = dict(new); del tens[rb]; owner[rb] = ra
    total = 1
    for v, T in tens.items():
        total *= sum(T.values())
    return total

def brute(n, clauses):
    c = 0
    for x in itertools.product((0, 1), repeat=n):
        if all(any(x[v] ^ b for (v, b) in cl) for cl in clauses): c += 1
    return c

def random_cnf(n, m, k, rng):
    return [[(rng.randrange(n), rng.randrange(2)) for _ in range(k)] for _ in range(m)]

if __name__ == '__main__':
    rng = random.Random(1)
    # 1. correctness of the encoding on small instances
    bad = 0; tested = 0
    for trial in range(300):
        n = rng.randint(1, 6); m = rng.randint(0, 7); k = rng.choice([2, 3, 4])
        cl = random_cnf(n, m, k, rng)
        net = build_network(n, cl, k)
        if net is None:
            val = 0
        else:
            V, E, used, nold = net
            assert check_bipartite(V, E, nold)
            Z = contract(V, E) if E else 1
            val = (Z * 2 ** (n - used)) % 2 ** (n + 1)
        if val != brute(n, cl): bad += 1; print('MISMATCH', n, cl, val, brute(n, cl))
        tested += 1
    print(f'encoding check: {tested} random instances, {bad} mismatches')
    # 2. size bounds: edges <= 4 k m, vertices polynomial, max degree <= max(k,3)
    for (n, m, k) in [(100, 300, 3), (1000, 4000, 3), (10**5, 3*10**5, 3), (10**6, 10**6, 3), (10**6, 4*10**6, 4)]:
        cl = random_cnf(n, m, k, rng)
        V, E, used, nold = build_network(n, cl, k)
        deg = defaultdict(int)
        for a, b in E: deg[a] += 1; deg[b] += 1
        s = n + m
        print(f'n={n} m={m} k={k}: s={s} edges={len(E)} (4km={4*k*m}, edges/s={len(E)/s:.2f}) '
              f'vertices={len(V)} maxdeg={max(deg.values())} ceil(s^0.9)={math.ceil(s**0.9)}')
    # 3. worst-case occurrence pattern: one variable in every clause
    n, m, k = 50, 10**5, 3
    cl = [[(0, 0), (rng.randrange(1, n), 0), (rng.randrange(1, n), 1)] for _ in range(m)]
    V, E, used, nold = build_network(n, cl, k)
    deg = defaultdict(int)
    for a, b in E: deg[a] += 1; deg[b] += 1
    print(f'variable 0 in all {m} clauses: edges={len(E)} maxdeg={max(deg.values())} (tree keeps degree 3)')
    # 4. threshold s0 where max(k,3) <= ceil(s^(9/10))
    for k in (2, 3, 4, 8, 16, 64):
        s0 = next(s for s in range(2, 10**7) if math.ceil(s ** 0.9) >= max(k, 3))
        print(f'k={k}: degree hypothesis holds for all s >= {s0}')
