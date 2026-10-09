import sys, time, itertools, math
sys.path.insert(0, '/home/al/dev/MOSP/pathwidth_solver'); sys.path.insert(0, '/home/al/dev/MOSP')
import networkx as nx
from pathwidth.solve import solve
from fixed_parameter_algorithm.pathwidth import compute_pathwidth as dp_pw

def hyp_formula(d): return sum(math.comb(m, m//2) for m in range(d))
def kneser(n,k):
    V=list(itertools.combinations(range(n),k)); G=nx.Graph(); G.add_nodes_from(V)
    G.add_edges_from((a,b) for a,b in itertools.combinations(V,2) if not set(a)&set(b)); return G
def johnson(n,k):
    V=list(itertools.combinations(range(n),k)); G=nx.Graph(); G.add_nodes_from(V)
    G.add_edges_from((a,b) for a,b in itertools.combinations(V,2) if len(set(a)&set(b))==k-1); return G
def hamming(q,d):
    V=list(itertools.product(range(q),repeat=d)); G=nx.Graph(); G.add_nodes_from(V)
    G.add_edges_from((a,b) for a,b in itertools.combinations(V,2) if sum(x!=y for x,y in zip(a,b))==1); return G
def gp(n,k):
    G=nx.Graph()
    for i in range(n): G.add_edge(('o',i),('o',(i+1)%n)); G.add_edge(('o',i),('i',i)); G.add_edge(('i',i),('i',(i+k)%n))
    return G
P,C,K=nx.path_graph,nx.cycle_graph,nx.complete_graph
cases=[]
for m in range(2,7):
    for n in range(m,9): cases.append((f"grid P{m}xP{n}", nx.grid_2d_graph(m,n), m))
for m in range(3,7):
    for n in range(m,9): cases.append((f"cyl C{m}xP{n}", nx.cartesian_product(C(m),P(n)), None))
for m in range(3,7):
    for n in range(m,8): cases.append((f"torus C{m}xC{n}", nx.cartesian_product(C(m),C(n)), None))
for d in range(3,7): cases.append((f"Q{d}", nx.hypercube_graph(d), hyp_formula(d)))
for n in (3,4): cases.append((f"grid3d P{n}^3", nx.grid_graph([n,n,n]), None))
cases.append(("grid3d P2xP3xP4", nx.grid_graph([2,3,4]), None))
cases.append(("grid3d P3xP3xP5", nx.grid_graph([3,3,5]), None))
for q,d in [(3,2),(4,2),(5,2),(3,3),(4,3),(3,4)]: cases.append((f"Hamming K{q}^{d}", hamming(q,d), None))
for n,k in [(5,2),(6,2),(7,2),(8,2),(7,3),(8,3)]: cases.append((f"Kneser K({n},{k})", kneser(n,k), None))
for n,k in [(5,2),(6,2),(7,2),(6,3),(7,3)]: cases.append((f"Johnson J({n},{k})", johnson(n,k), None))
for n in (5,10): cases.append((f"K{n}", K(n), n-1))
for m,n in [(2,5),(3,3),(3,7),(5,6)]: cases.append((f"K{m},{n}", nx.complete_bipartite_graph(m,n), min(m,n)))
for parts in [(2,2,2),(1,2,3),(3,3,4),(2,4,4,5)]: cases.append((f"K{parts}", nx.complete_multipartite_graph(*parts), sum(parts)-max(parts)))
for n in (3,8,15): cases.append((f"C{n}", C(n), 2))
for n in (4,6,12): cases.append((f"W{n} (hub+C{n})", nx.wheel_graph(n+1), 3))
cases.append(("Petersen", nx.petersen_graph(), None))
for n,k in [(5,2),(6,2),(7,2),(8,3),(10,2),(10,3),(12,5)]: cases.append((f"GP({n},{k})", gp(n,k), None))
for n,k in [(10,2),(12,3),(15,2),(20,3)]:
    cases.append((f"P{n}^{k} (path power)", nx.power(P(n),k), k))
    cases.append((f"C{n}^{k} (cycle power)", nx.power(C(n),k), 2*k))
for n,J in [(12,[1,3]),(13,[1,5]),(16,[1,4]),(15,[1,2,4])]: cases.append((f"Circ({n};{J})", nx.circulant_graph(n,J), None))
for m,n in [(3,3),(3,5),(4,4),(4,6),(5,5)]: cases.append((f"king P{m}⊠P{n}", nx.strong_product(P(m),P(n)), None))
for (g,gn),(h,hn) in [((P(4),'P4'),(K(3),'K3')),((C(5),'C5'),(K(2),'K2')),((P(5),'P5'),(K(4),'K4')),((nx.petersen_graph(),'Pet'),(K(2),'K2'))]:
    cases.append((f"lex {gn}[{hn}]", nx.lexicographic_product(g,h), None))
for (g,gn),(h,hn) in [((P(5),'P5'),(P(5),'P5')),((C(5),'C5'),(C(7),'C7')),((K(4),'K4'),(K(4),'K4')),((K(3),'K3'),(P(6),'P6')),((C(6),'C6'),(C(6),'C6'))]:
    cases.append((f"tensor {gn}x{hn}", nx.tensor_product(g,h), None))
for n in (5,6,7): cases.append((f"L(K{n})", nx.line_graph(K(n)), None))
for m,n in [(3,4),(4,4),(4,5)]: cases.append((f"rook K{m}□K{n}", nx.cartesian_product(K(m),K(n)), None))
for (g,gn),(h,hn) in [((K(3),'K3'),(P(6),'P6')),((K(4),'K4'),(C(6),'C6')),((nx.petersen_graph(),'Pet'),(K(2),'K2')),((K(4),'K4'),(K(4),'K4'))]:
    cases.append((f"cart {gn}□{hn}", nx.cartesian_product(g,h), None))
for name,G,f in cases:
    if G is None: continue
    G=nx.convert_node_labels_to_integers(G)
    t=time.time(); s=solve(G, time_budget=120)
    dp=''
    if G.number_of_nodes()<=18:
        dp=dp_pw(G)[0]
    print(f"{name}\tn={G.number_of_nodes()}\tm={G.number_of_edges()}\tpw={s.width}\tproof={s.proof or 'UNPROVED'}\tlower={s.lower}\tdp={dp}\tformula={'' if f is None else f}\t{time.time()-t:.1f}s", flush=True)
