import sys, subprocess, time; sys.path.insert(0, "/home/al/dev/MOSP/reports/scratch/tree_bound")
from treelib import *
import networkx as nx
def big(G):
    inp = " ".join(map(str, nx_to_parents(G))) + "\n"
    return int(subprocess.run(["./treepw_big"], input=inp, capture_output=True, text=True, cwd="/home/al/dev/MOSP/reports/scratch/tree_bound").stdout.split()[0])
# agreement with treepw on the 22- and 67-vertex trees and random trees
import random; rng = random.Random(3)
for n in [22, 67, 100, 127]:
    for _ in range(5):
        G = random_tree(n, rng); a = treepw_many([nx_to_parents(G)])[0]; b = big(G); assert a == b, (n, a, b)
print("treepw_big agrees with treepw on 20 random trees at 22..127", flush=True)
def M(k):
    G = nx.path_graph(2)
    for _ in range(k - 1): G = join_at_root([(G, 0)] * 3)
    return G
for name, G in [("ternary h=5 (364)", nx.balanced_tree(3, 5)), ("M(5) (202)", M(5)), ("ternary h=6 (1093)?", None), ("binary h=9 (1023)?", None)]:
    if G is None: continue
    t = time.time(); print(f"{name}: treepw_big pw = {big(G)}  ({time.time()-t:.1f}s)", flush=True)
# minus one leaf of each
for name, G in [("ternary h=5 minus a leaf (363)", nx.balanced_tree(3, 5)), ("M(5) minus a leaf (201)", M(5))]:
    leaf = [v for v in G.nodes() if G.degree(v) == 1][0]; H = G.copy(); H.remove_node(leaf); H = nx.convert_node_labels_to_integers(H)
    t = time.time(); print(f"{name}: treepw_big pw = {big(H)}  ({time.time()-t:.1f}s)", flush=True)
