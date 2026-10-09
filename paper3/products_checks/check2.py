import sys, time, itertools, math
sys.path.insert(0, '/home/al/dev/MOSP/pathwidth_solver'); sys.path.insert(0, '/home/al/dev/MOSP')
import numpy as np, networkx as nx
from pathwidth.solve import solve
P,C,K=nx.path_graph,nx.cycle_graph,nx.complete_graph
def kneser(n,k):
    V=list(itertools.combinations(range(n),k)); G=nx.Graph(); G.add_nodes_from(V)
    G.add_edges_from((a,b) for a,b in itertools.combinations(V,2) if not set(a)&set(b)); return G
def genhyp(t,n):
    V=list(itertools.product((0,1),repeat=n)); G=nx.Graph(); G.add_nodes_from(V)
    G.add_edges_from((a,b) for a,b in itertools.combinations(V,2) if sum(x!=y for x,y in zip(a,b))<=t); return G
def genhyp_formula(t,n):
    lo=(n-t)//2
    s=sum(math.comb(n,k) for k in range(lo,lo+t))
    s+=sum(math.comb(t+2*a,t+a-1)-(math.comb(t+2*a,a-1) if a>=1 else 0) for a in range((n-t-1)//2+1))
    return s
def gp(n,k):
    G=nx.Graph()
    for i in range(n): G.add_edge(('o',i),('o',(i+1)%n)); G.add_edge(('o',i),('i',i)); G.add_edge(('i',i),('i',(i+k)%n))
    return G
def run(name,G,f=None,budget=180):
    G=nx.convert_node_labels_to_integers(G); t=time.time(); s=solve(G,time_budget=budget)
    print(f"{name}\tn={G.number_of_nodes()}\tpw={s.width}\tproof={s.proof or 'UNPROVED'}\tlower={s.lower}\tformula={'' if f is None else f}\t{time.time()-t:.1f}s",flush=True)
for t,n in [(1,3),(1,4),(2,4),(2,5),(3,5),(2,6),(3,6)]: run(f"H({t},2,{n})",genhyp(t,n),genhyp_formula(t,n))
for n in (9,10): run(f"Kneser K({n},2)",kneser(n,2),f"tw={math.comb(n-1,2)-1}")
run("Kneser K(9,3)",kneser(9,3),f"tw={math.comb(8,3)-1}")
for n in (12,16,20,24,30): run(f"GP({n},1) prism",gp(n,1),"2k+1..2k+2 = 3..4")
for n in (12,16,20,30,40): run(f"GP({n},2)",gp(n,2),"5..6")
for n in (15,21,30,40): run(f"GP({n},3)",gp(n,3),"7..8")
for n in (6,7,8): run(f"king P{n}⊠P{n}",nx.strong_product(P(n),P(n)))
for m,n in [(4,4),(4,5),(5,5),(4,7),(5,6)]: run(f"strong C{m}⊠C{n}",nx.strong_product(C(m),C(n)))
for m,n in [(6,3),(8,3),(8,4),(10,4),(12,5)]: run(f"cyl C{m}xP{n} (n<m)",nx.cartesian_product(C(m),P(n)))
for m,n in [(3,9),(4,9),(5,9),(7,7),(7,8)]: run(f"torus C{m}xC{n}",nx.cartesian_product(C(m),C(n)))
run("grid4d P3^4",nx.grid_graph([3,3,3,3]),"conj (8n^3+3n^2+4n)/12 = 21",budget=400)
run("grid3d P5^3",nx.grid_graph([5,5,5]),"Otachi-Suda 25-4=21",budget=300)
run("grid3d P3xP4xP4",nx.grid_graph([3,4,4]),"12-1=11")
run("Hamming K3^4",nx.cartesian_product(nx.cartesian_product(K(3),K(3)),nx.cartesian_product(K(3),K(3))),budget=400)
