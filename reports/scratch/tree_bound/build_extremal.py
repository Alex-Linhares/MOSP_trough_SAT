"""Extremal trees by the ternary construction: E(0) = K1, E(k+1) = new root joined to three copies of
E(k) at chosen vertices.  --all-centres: attach at the centre (root) every time (the 'spider of spiders').
Prints k, N, g6, treepw pw, and the C solver's verdict."""
import sys; sys.path.insert(0, "/home/al/dev/MOSP/reports/scratch/tree_bound")
from treelib import *
import networkx as nx
def E(k):
    if k == 0: return nx.Graph([(0, 0)]) if False else nx.empty_graph(1)
    T = E(k - 1); return join_at_root([(T, 0), (T, 0), (T, 0)])   # node 0 is the previous root after relabel? ensure:
def E_rooted(k):
    """returns (G, root) with root label 0"""
    if k == 0: return nx.empty_graph(1), 0
    T, r = E_rooted(k - 1)
    G = nx.Graph(); G.add_node("r")
    for i in range(3):
        H = nx.relabel_nodes(T, {v: (i, v) for v in T.nodes()}); G = nx.union(G, H); G.add_edge("r", (i, r))
    order = ["r"] + [v for v in G.nodes() if v != "r"]; m = {v: i for i, v in enumerate(order)}
    return nx.relabel_nodes(G, m), 0
kmax = int(sys.argv[1]) if len(sys.argv) > 1 else 4
for k in range(1, kmax + 1):
    G, r = E_rooted(k); n = G.number_of_nodes()
    tp = treepw_many([nx_to_parents(G, r)])[0] if n <= 127 else None
    sw, st = solver_pw(G, 1800)
    print(f"E({k}): N={n} treepw={tp} solver={sw} ({st}) g6={g6(G)}", flush=True)
