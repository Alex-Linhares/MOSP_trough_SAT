"""Write the PACE .gr file of a pilot graph: python3 to_gr.py n c sample > g.gr"""
import csv, sys
from pathlib import Path
import networkx as nx
n, c, s = int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3])
r = next(r for r in csv.DictReader(open(Path(__file__).with_name("results.csv")))
         if int(r["n"]) == n and float(r["c"]) == c and int(r["sample"]) == s)
G = nx.gnp_random_graph(n, c / n, seed=int(r["seed"]))
print(f"c pilot n={n} c={c} sample={s} seed={r['seed']} pw={r['width']}")
print(f"p tw {n} {G.number_of_edges()}")
for u, v in G.edges(): print(u + 1, v + 1)
