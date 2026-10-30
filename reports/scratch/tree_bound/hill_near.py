"""Focused attack at N = 66: start from M(4) (67 vertices, pw 4) minus one leaf (pw 3) and from the ten
22-vertex trees minus one leaf (N = 21, pw 2); explore every leaf-relocation neighbour (and, at N = 66,
two rounds of neighbours of the best) looking for a tree of pw K(N)+1.  treepw oracle; any hit confirmed by
the C solver."""
import sys, random, collections; sys.path.insert(0, "/home/al/dev/MOSP/reports/scratch/tree_bound")
from treelib import *
import networkx as nx
rng = random.Random(7)
def pws(Gs): return treepw_many([nx_to_parents(G) for G in Gs])
def neighbours(G):
    out = []
    for leaf in [v for v in G.nodes() if G.degree(v) == 1]:
        p = next(iter(G[leaf]))
        for q in G.nodes():
            if q != leaf and q != p:
                H = G.copy(); H.remove_edge(leaf, p); H.add_edge(leaf, q); out.append(H)
    return out
def M(k):
    G = nx.path_graph(2)
    for _ in range(k - 1): G = join_at_root([(G, 0)] * 3)
    return G
def attack(starts, N, K, rounds):
    seen = set(); frontier = starts; hits = 0; evaluated = 0; hist = collections.Counter()
    for r in range(rounds):
        nb = []
        for G in frontier: nb += neighbours(G)
        vals = pws(nb); evaluated += len(nb); hist.update(vals)
        for H, v in zip(nb, vals):
            if v > K: hits += 1; print(f"HIT N={N} treepw={v} > K={K}: solver={solver_pw(H)} g6={g6(H)}", flush=True)
        best = max(vals); cands = [H for H, v in zip(nb, vals) if v == best]
        frontier = rng.sample(cands, min(6, len(cands)))
        print(f"  N={N} round {r}: {len(nb)} neighbours, pw hist {dict(sorted(collections.Counter(vals).items()))}, best {best}", flush=True)
    print(f"N={N}: K={K}, evaluated {evaluated}, hits {hits}, overall hist {dict(sorted(hist.items()))}", flush=True)
# N = 21 from the ten 22-vertex trees minus each leaf
starts = []
for line in open("/home/al/dev/MOSP/reports/scratch/tree_bound/exh_22.txt"):
    if line.startswith("pw"):
        G = parents_to_nx([int(x) for x in line.split(":")[1].split()])
        for leaf in [v for v in G.nodes() if G.degree(v) == 1]:
            H = G.copy(); H.remove_node(leaf); starts.append(nx.convert_node_labels_to_integers(H))
print(f"N=21 starts: {len(starts)}, their pw: {dict(collections.Counter(pws(starts)))}", flush=True)
attack(starts, 21, 2, 3)
G4 = M(4); starts = []
for leaf in [v for v in G4.nodes() if G4.degree(v) == 1]:
    H = G4.copy(); H.remove_node(leaf); starts.append(nx.convert_node_labels_to_integers(H))
print(f"N=66 starts: {len(starts)}, their pw: {dict(collections.Counter(pws(starts)))}", flush=True)
attack(starts, 66, 3, 3)
