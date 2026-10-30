"""Brute-force checks of the prover's L3 and L4 (gossip 19:40).
L3: for every tree T and every path P (incl. single vertices), pw(T) <= 1 + max_C pw(C), C components of T - P.
L4: every tree on N <= 3m vertices has a path P with every component of T - P smaller than m; the binding
    case is m = ceil(N/3); we also record the best achievable max-component size per tree (min over paths)."""
import sys, subprocess, itertools, collections, math
sys.path.insert(0, "/home/al/dev/MOSP/reports/scratch/empty_pair"); sys.path.insert(0, "/home/al/dev/MOSP/reports/scratch/tree_bound")
from check import vs
from treelib import *
import networkx as nx

def adj_masks(G):
    n = G.number_of_nodes(); adj = [0] * n
    for u, v in G.edges(): adj[u] |= 1 << v; adj[v] |= 1 << u
    return n, adj

def comps(G, P):
    H = G.copy(); H.remove_nodes_from(P); return list(nx.connected_components(H))

def paths(G):
    for s, t in itertools.combinations_with_replacement(G.nodes(), 2):
        yield nx.shortest_path(G, s, t)

def pw_set(G, adj, S):
    S = sorted(S); idx = {v: i for i, v in enumerate(S)}; a = [0] * len(S)
    for v in S:
        for u in G[v]:
            if u in idx: a[idx[v]] |= 1 << idx[u]
    return vs(len(S), a)

def main():
    maxL3 = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    maxL4 = int(sys.argv[2]) if len(sys.argv) > 2 else 18
    print("L3: pw(T) <= 1 + max pw(C) over components of T - P, every tree, every path")
    for N in range(2, maxL3 + 1):
        lines = subprocess.run(["nauty-gentreeg", "-p", "-q", str(N)], capture_output=True, text=True).stdout.splitlines()
        viol = tight = tot = 0
        for line in lines:
            G = parents_to_nx([int(x) for x in line.split()]); n, adj = adj_masks(G); pw = vs(n, adj)
            for P in paths(G):
                m = max([pw_set(G, adj, C) for C in comps(G, P)], default=0)
                tot += 1
                if pw > 1 + m: viol += 1; print("  L3 VIOLATION", line, P)
                if pw == 1 + m: tight += 1
        print(f"  N={N} trees={len(lines)} (tree,path) pairs={tot} violations={viol} tight={tight}", flush=True)
    print("L4: path P with all components of T - P of size < m, m = ceil(N/3) (the binding case)")
    for N in range(1, maxL4 + 1):
        lines = subprocess.run(["nauty-gentreeg", "-p", "-q", str(N)], capture_output=True, text=True).stdout.splitlines()
        m = math.ceil(N / 3); viol = 0; worst = 0; hist = collections.Counter()
        for line in lines:
            G = parents_to_nx([int(x) for x in line.split()])
            best = min(max([len(C) for C in comps(G, P)], default=0) for P in paths(G))
            hist[best] += 1
            if best >= m: viol += 1; print("  L4 VIOLATION", line, "best max-component", best, "m", m)
        print(f"  N={N} m={m} trees={len(lines)} violations={viol} min-over-paths max-component hist={dict(sorted(hist.items()))}", flush=True)

if __name__ == "__main__": main()
