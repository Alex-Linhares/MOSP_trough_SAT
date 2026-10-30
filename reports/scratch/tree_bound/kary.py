"""Complete k-ary trees of height h: pw by treepw (n <= 127) and the C solver."""
import sys; sys.path.insert(0, "/home/al/dev/MOSP/reports/scratch/tree_bound")
from treelib import *
import networkx as nx
for k in [2, 3, 4, 5, 6]:
    for h in range(1, 12):
        G = nx.balanced_tree(k, h); n = G.number_of_nodes()
        if n > 1100: break
        tp = treepw_many([nx_to_parents(G, 0)])[0] if n <= 127 else None
        sw, st = solver_pw(G, 900)
        print(f"k={k} h={h} N={n}: treepw={tp} solver={sw} ({st})", flush=True)
