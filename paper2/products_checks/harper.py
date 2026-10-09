import numpy as np, networkx as nx, itertools, sys
P,C,K=nx.path_graph,nx.cycle_graph,nx.complete_graph
def harper(G):
    G=nx.convert_node_labels_to_integers(G); n=G.number_of_nodes()
    S=np.arange(1<<n,dtype=np.int64); pc=np.zeros(1<<n,dtype=np.int8)
    for v in range(n): pc+=((S>>v)&1).astype(np.int8)
    inner=np.zeros(1<<n,dtype=np.int8); outer=np.zeros(1<<n,dtype=np.int8)
    for v in range(n):
        Nv=sum(1<<u for u in G[v]); inS=((S>>v)&1).astype(bool)
        touches=(S & Nv)!=0
        inner+=(inS & ((S & Nv)!=Nv)).astype(np.int8)
        outer+=((~inS) & touches).astype(np.int8)
    bi=max(int(inner[pc==i].min()) for i in range(1,n+1))
    bo=max(int(outer[pc==i].min()) for i in range(1,n))
    return bi,bo
def kneser(n,k):
    V=list(itertools.combinations(range(n),k)); G=nx.Graph(); G.add_nodes_from(V)
    G.add_edges_from((a,b) for a,b in itertools.combinations(V,2) if not set(a)&set(b)); return G
def johnson(n,k):
    V=list(itertools.combinations(range(n),k)); G=nx.Graph(); G.add_nodes_from(V)
    G.add_edges_from((a,b) for a,b in itertools.combinations(V,2) if len(set(a)&set(b))==k-1); return G
def gp(n,k):
    G=nx.Graph()
    for i in range(n): G.add_edge(('o',i),('o',(i+1)%n)); G.add_edge(('o',i),('i',i)); G.add_edge(('i',i),('i',(i+k)%n))
    return G
cases=[("Q4",nx.hypercube_graph(4),7),("rook K3□K3",nx.cartesian_product(K(3),K(3)),5),("rook K4□K4",nx.cartesian_product(K(4),K(4)),9),
("torus C4xC4",nx.cartesian_product(C(4),C(4)),7),("torus C3xC5",nx.cartesian_product(C(3),C(5)),6),("torus C4xC5",nx.cartesian_product(C(4),C(5)),8),
("Petersen",nx.petersen_graph(),5),("Kneser K(6,2)",kneser(6,2),10),("L(K6)=J(6,2)",johnson(6,2),10),("J(6,3)",johnson(6,3),13),
("GP(8,3)",gp(8,3),6),("GP(10,2)",gp(10,2),6),("king P4⊠P4",nx.strong_product(P(4),P(4)),5),("strong C4⊠C4",nx.strong_product(C(4),C(4)),10),
("grid P4xP5",nx.grid_2d_graph(4,5),4),("tensor K4xK4",nx.tensor_product(K(4),K(4)),12),("lex P5[K4]",nx.lexicographic_product(P(5),K(4)),7),
("cyl C8xP2 prism",nx.cartesian_product(C(8),P(2)),4),("Circ(16;1,4)",nx.circulant_graph(16,[1,4]),7)]
for name,G,pw in cases:
    bi,bo=harper(G); print(f"{name}\tn={G.number_of_nodes()}\tpw={pw}\tHarper_inner={bi}\tHarper_outer={bo}\ttight={'yes' if max(bi,bo)==pw else 'no'}",flush=True)
