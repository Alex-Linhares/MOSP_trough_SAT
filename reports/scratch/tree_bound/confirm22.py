import sys; sys.path.insert(0, "/home/al/dev/MOSP/reports/scratch/tree_bound")
from treelib import *
f = sys.argv[1]
for line in open(f):
    if not line.startswith("pw"): continue
    w, par = line.split(":")[0].split()[1], [int(x) for x in line.split(":")[1].split()]
    G = parents_to_nx(par); sw, st = solver_pw(G, 600)
    degs = sorted((d for _, d in G.degree()), reverse=True)
    print(f"filter pw={w}  solver pw={sw} ({st})  g6={g6(G)}  maxdeg={degs[0]} leaves={degs.count(1)}", flush=True)
