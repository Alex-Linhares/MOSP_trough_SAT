"""Prover's L4 candidates (message at 19:56): on every tree to N vertices,
  w(P) = largest component of T - P;  W = min over paths P (incl. single vertices) of w(P);
  b3(v) = third-largest component size of T - v (0 if deg < 3);  B = max_v b3(v).
(D) W == B ?   (C) W attained by a leaf-to-leaf path?   (B) for every vertex r, some path through r has w < m = ceil(N/3)?
Reports violations and the distribution of W - B."""
import sys, subprocess, itertools, collections, math
from multiprocessing import Pool
sys.path.insert(0, "/home/al/dev/MOSP/reports/scratch/tree_bound")
from treelib import parents_to_nx
import networkx as nx

def analyse(line):
    G = parents_to_nx([int(x) for x in line.split()]); N = G.number_of_nodes(); m = math.ceil(N / 3)
    leaves = {v for v in G.nodes() if G.degree(v) == 1} if N > 1 else set(G.nodes())
    B = 0
    for v in G.nodes():
        H = G.copy(); H.remove_node(v); sz = sorted((len(c) for c in nx.connected_components(H)), reverse=True)
        if len(sz) >= 3: B = max(B, sz[2])
    W = N; Wleaf = N; through = {r: N for r in G.nodes()}
    for s, t in itertools.combinations_with_replacement(list(G.nodes()), 2):
        P = nx.shortest_path(G, s, t); H = G.copy(); H.remove_nodes_from(P)
        w = max((len(c) for c in nx.connected_components(H)), default=0)
        W = min(W, w)
        if s in leaves and t in leaves: Wleaf = min(Wleaf, w)
        for r in P: through[r] = min(through[r], w)
    Bfail = sum(1 for r in G.nodes() if through[r] >= m)   # vertices r with no path through r achieving < m
    return N, W, B, Wleaf, Bfail, line

if __name__ == "__main__":
    maxN = int(sys.argv[1]) if len(sys.argv) > 1 else 14
    for N in range(2, maxN + 1):
        lines = subprocess.run(["nauty-gentreeg", "-p", "-q", str(N)], capture_output=True, text=True).stdout.splitlines()
        with Pool(4) as p: res = p.map(analyse, lines, chunksize=32)
        diff = collections.Counter(W - B for _, W, B, _, _, _ in res)
        Cviol = sum(1 for _, W, B, Wl, _, _ in res if Wl != W)
        Bviol = sum(1 for *_, bf, _ in res if bf > 0)
        print(f"N={N} trees={len(res)} | (D) W-B distribution {dict(sorted(diff.items()))} violations={sum(v for d, v in diff.items() if d != 0)} | (C) leaf-leaf path not optimal on {Cviol} trees | (B) trees with a vertex r no path through r reaches < ceil(N/3): {Bviol}", flush=True)
        for _, W, B, _, _, line in res:
            if W != B: print(f"   (D) counterexample N={N} W={W} B={B} parents={line}"); break
