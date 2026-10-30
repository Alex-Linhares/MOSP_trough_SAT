"""Local search for high-pathwidth trees at fixed N (an attack on pw <= K(N)): start from a random tree,
repeatedly evaluate all 'leaf relocation' neighbours (detach a leaf, reattach anywhere) in one treepw call,
move to the best (ties random), restart when stuck; keep the best tree seen.  N <= 127 (treepw).  Top trees
confirmed by the C solver at the end.  Usage: hillclimb.py N restarts steps seed"""
import sys, random, time, collections; sys.path.insert(0, "/home/al/dev/MOSP/reports/scratch/tree_bound")
from treelib import *
import networkx as nx
def K(N):
    s, k = 2, 1
    while 3 * s + 1 <= N: s = 3 * s + 1; k += 1
    return k
N, restarts, steps, seed = map(int, sys.argv[1:5]); rng = random.Random(seed)
def pw_of(G): return treepw_many([nx_to_parents(G)])[0]
def neighbours(G):
    out = []
    leaves = [v for v in G.nodes() if G.degree(v) == 1]
    for leaf in leaves:
        p = next(iter(G[leaf]))
        for q in G.nodes():
            if q != leaf and q != p:
                H = G.copy(); H.remove_edge(leaf, p); H.add_edge(leaf, q); out.append(H)
    return out
# secondary score to guide the climb: number of vertices with >= 3 non-leaf neighbours (pw>=2 witnesses) and
# number of vertices with 3 branches of pw >= 2 — we use the treepw value plus a tie-breaker: count of degree>=3 vertices
best_overall = (0, None); t0 = time.time(); hist = collections.Counter()
for r in range(restarts):
    G = nx.convert_node_labels_to_integers(random_tree(N, rng)); cur = pw_of(G)
    for s in range(steps):
        nb = neighbours(G); vals = treepw_many([nx_to_parents(H) for H in nb])
        mx = max(vals)
        if mx < cur: break
        cands = [H for H, v in zip(nb, vals) if v == mx]
        # tie-break: prefer more vertices of degree >= 3 (branching), to walk towards ternary structure
        cands.sort(key=lambda H: -sum(1 for _, d in H.degree() if d >= 3)); top = cands[: max(1, len(cands) // 10)]
        G = rng.choice(top); cur = mx
        if cur > best_overall[0]: best_overall = (cur, G.copy())
    hist[cur] += 1
    if cur > best_overall[0]: best_overall = (cur, G.copy())
    if cur > K(N): print(f"CANDIDATE VIOLATION N={N} treepw={cur} K={K(N)} g6={g6(G)}", flush=True)
print(f"N={N}: K(N)={K(N)}, best pw found={best_overall[0]}, end-of-restart pw hist={dict(sorted(hist.items()))}, {time.time()-t0:.0f}s", flush=True)
G = best_overall[1]; print(f"  best tree: solver={solver_pw(G, 1800)} degree hist={dict(sorted(collections.Counter(d for _, d in G.degree()).items()))} g6={g6(G)}", flush=True)
