"""Exploration (not the deliverable): which candidate transforms give exact
identities on all graphs to 6 vertices?  vs by subset DP (numpy)."""
import itertools, sys, time
import numpy as np
import networkx as nx
from networkx.generators.atlas import graph_atlas_g
sys.path.insert(0, '.')
from paper1.complex_check import graph, edges_of, from_nx, vs_dp, cutwidth_dp, vertex_separation, two_expansion

def vs_np(adj):
    n = len(adj)
    if n <= 1: return 0
    N = 1 << n
    states = np.arange(N, dtype=np.int64)
    cost = np.zeros(N, dtype=np.int32)
    for u in range(n):
        inside = (states >> u) & 1
        has_out = ((np.int64(adj[u]) & ~states) != 0)
        cost += (inside & has_out).astype(np.int32)
    cost[N - 1] = 0
    pc = np.zeros(N, dtype=np.int32)
    for u in range(n): pc += ((states >> u) & 1).astype(np.int32)
    f = np.full(N, 10**9, dtype=np.int32); f[0] = 0
    for k in range(1, n + 1):
        S = states[pc == k]
        best = np.full(len(S), 10**9, dtype=np.int32)
        for v in range(n):
            has = ((S >> v) & 1).astype(bool)
            prev = f[S ^ (1 << v)]
            best = np.where(has, np.minimum(best, prev), best)
        f[S] = np.maximum(best, cost[S])
    return int(f[N - 1])

def cobip_double(g):
    n, adj = g
    es = []
    for u in range(n):
        for v in range(u + 1, n):
            es.append((u, v)); es.append((n + u, n + v))
        es.append((u, n + u))
        for v in range(n):
            if adj[u] >> v & 1: es.append((u, n + v))
    return graph(2 * n, es)

def clique_blowup(g, c):
    n, adj = g
    es = []
    for u in range(n):
        for i in range(c):
            for j in range(i + 1, c): es.append((c * u + i, c * u + j))
            for v in range(u + 1, n):
                if adj[u] >> v & 1:
                    for j in range(c): es.append((c * u + i, c * v + j))
    return graph(c * n, es)

def degree_clique_expansion(g):
    """each vertex -> clique on its incident edges; each edge -> matching edge."""
    n, adj = g
    es = edges_of(g)
    port = {}
    cnt = 0
    for i, (u, v) in enumerate(es):
        port[(u, i)] = cnt; cnt += 1
        port[(v, i)] = cnt; cnt += 1
    new = []
    for u in range(n):
        ps = [port[(u, i)] for i, e in enumerate(es) if u in e]
        new += list(itertools.combinations(ps, 2))
    for i, (u, v) in enumerate(es):
        new.append((port[(u, i)], port[(v, i)]))
    iso = [u for u in range(n) if adj[u] == 0]
    return graph(cnt + len(iso), new)

def line_graph(g):
    es = edges_of(g)
    new = [(i, j) for i in range(len(es)) for j in range(i + 1, len(es)) if set(es[i]) & set(es[j])]
    return graph(len(es), new)

def subdivision(g):
    n, adj = g; es = edges_of(g); new = []
    for i, (u, v) in enumerate(es): new += [(u, n + i), (n + i, v)]
    return graph(n + len(es), new)

nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 6
atlas = [from_nx(h) for h in graph_atlas_g() if 1 <= h.number_of_nodes() <= nmax]
t0 = time.time()
# sanity: vs_np == permutations
for g in atlas:
    if g[0] <= 6: assert vs_np(g[1]) == vertex_separation(g), g
print("vs_np agrees with permutations on", len(atlas), "graphs", time.time() - t0)
bad = {k: [] for k in ['cobip', 'blow2', 'cw=vs(deg-clique)', 'cw=vs(line)', 'cw=vs(subdiv)', 'cw=vs(2exp)', 'cw=vs(deg-clique)+1?']}
for g in atlas:
    n, adj = g
    vs = vs_np(adj); cw = cutwidth_dp(g)
    if vs_np(cobip_double(g)[1]) != vs + n: bad['cobip'].append(g)
    if n <= 6 and vs_np(clique_blowup(g, 2)[1]) != 2 * (vs + 1) - 1: bad['blow2'].append(g)
    if len(edges_of(g)) <= 9:
        d = vs_np(degree_clique_expansion(g)[1])
        if d != cw: bad['cw=vs(deg-clique)'].append((g, cw, d))
        if vs_np(line_graph(g)[1]) != cw: bad['cw=vs(line)'].append((g, cw, vs_np(line_graph(g)[1])))
        if vs_np(subdivision(g)[1]) != cw: bad['cw=vs(subdiv)'].append((g, cw))
        if vs_np(two_expansion(g)[1]) != cw: bad['cw=vs(2exp)'].append((g, cw, vs_np(two_expansion(g)[1])))
for k, v in bad.items():
    print(k, 'failures', len(v), v[:3])
print('time', time.time() - t0)
