"""Brute force for lean/MOSPFormalization/Complex/VertexSearch.lean (paper2/vertex_search_lean.md).
Run: python paper2/vertex_search_check.py
(1) BRST vertex search number vs pw+1 on all graphs 1..maxn (atlas).
(2) the reduction: a vertex search (X_1..X_m), expanded into single node-search
    moves (removals of X_i\\X_{i+1}, placements of X_{i+1}\\X_i), keeps every
    contaminated edge touching B_i at each X_i; hence success => all edges clear.
"""
import sys, random, collections, time
sys.path.insert(0, "/home/al/dev/MOSP")
sys.argv = ["x", "none"]
from paper2.complex_members_check import brst_search, atlas, from_nx, vs_dp, popcount
from paper1.complex_check import edges_of

def check1(maxn):
    t = collections.Counter(); cnt = 0
    for h in atlas(maxn):
        g = from_nx(h); cnt += 1
        t[brst_search(g) - (vs_dp(g) + 1)] += 1
    print(f"(1) graphs 1..{maxn}: {cnt}; vsn - (pw+1) tally:", dict(t))

def reach(adj, n, B, X):
    R = B & ~X; fr = R
    while fr:
        v = (fr & -fr).bit_length() - 1; fr &= fr - 1
        nb = adj[v] & ~X & ~R; R |= nb; fr |= nb
    return R

def node_step(adj, n, es, S, D):
    D = {e for e in D if not ((S >> e[0] & 1) and (S >> e[1] & 1))}
    # free reach from endpoints of D, through unguarded vertices
    seeds = 0
    for (a, b) in D:
        for x in (a, b):
            if not S >> x & 1: seeds |= 1 << x
    R = reach(adj, n, seeds, S)
    rec = {e for e in es if (R >> e[0] & 1) or (R >> e[1] & 1)}
    return D | rec

def check2(trials, maxn, seed=1):
    rng = random.Random(seed); bad = 0; succ = 0
    for _ in range(trials):
        n = rng.randint(1, maxn); p = rng.random()
        es = [(u, v) for u in range(n) for v in range(u + 1, n) if rng.random() < p]
        adj = [0] * n
        for u, v in es: adj[u] |= 1 << v; adj[v] |= 1 << u
        X = 0; B = (1 << n) - 1; S = 0; D = set(es)
        for _ in range(rng.randint(1, 3 * n + 3)):
            if rng.random() < 0.5:
                Y = X | rng.getrandbits(n) if n else 0
            else:
                Y = X & rng.getrandbits(n) if n else 0
            B = reach(adj, n, B, Y)
            for v in range(n):
                if X >> v & 1 and not Y >> v & 1:
                    S &= ~(1 << v); D = node_step(adj, n, es, S, D)
            for v in range(n):
                if Y >> v & 1 and not X >> v & 1:
                    S |= 1 << v; D = node_step(adj, n, es, S, D)
            X = Y
            assert S == X
            if any(not ((B >> a & 1) or (B >> b & 1)) for a, b in D):
                bad += 1; break
        if B == 0:
            succ += 1
            if D: bad += 1
    print(f"(2) {trials} random searches on graphs <= {maxn} vertices: {succ} successful, violations: {bad}")

if __name__ == "__main__":
    t0 = time.time(); check2(200000, 8); print(f"   {time.time()-t0:.1f}s")
    for m in (5, 6, 7):
        t0 = time.time(); check1(m); print(f"   {time.time()-t0:.1f}s")
