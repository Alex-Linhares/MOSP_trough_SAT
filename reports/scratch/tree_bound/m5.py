"""M(5): 202-vertex minimal trees of pathwidth 5 by the ternary construction (root joined to three copies of
a 67-vertex M(4) tree), several attachment choices; C solver only (n > 127).  Also the 201-vertex trees
obtained by deleting one leaf (expected pw 4), spot-checked."""
import sys, random; sys.path.insert(0, "/home/al/dev/MOSP/reports/scratch/tree_bound")
from treelib import *
import networkx as nx
def M_centres(k):
    if k == 1: return nx.path_graph(2), 0
    T, r = M_centres(k - 1); G = join_at_root([(T, r)] * 3); return G, 0   # join_at_root puts the new root first? check
# join_at_root relabels with convert_node_labels_to_integers over nodes in insertion order: "r" first -> label 0
rng = random.Random(5)
M4, r4 = M_centres(4); assert M4.number_of_nodes() == 67
print("M(4) all-centres:", solver_pw(M4, 1800), flush=True)
variants = [[(M4, r4)] * 3] + [[(M4, rng.randrange(67)) for _ in range(3)] for _ in range(3)]
for i, var in enumerate(variants):
    G = join_at_root(var); n = G.number_of_nodes(); sw, st = solver_pw(G, 3600)
    print(f"M(5) variant {i} (attach at {[a for _, a in var]}): N={n} solver pw={sw} ({st})", flush=True)
    if i == 0:
        leaves = [v for v in G.nodes() if G.degree(v) == 1]
        for leaf in rng.sample(leaves, 2):
            H = G.copy(); H.remove_node(leaf); print(f"   minus leaf {leaf}: N=201 solver pw={solver_pw(H, 3600)}", flush=True)
        print("   M(5) all-centres g6:", g6(G)[:80], "...", flush=True)
