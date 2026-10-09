import sys; sys.path.insert(0,'/home/al/dev/MOSP')
import numpy as np, networkx as nx, itertools
from mosp.instance import MOSPInstance
from satisfiability import solve_mosp_exact
def inc(G):
    V=sorted(G.nodes()); E=sorted(G.edges()); M=np.zeros((len(V),len(E)),dtype=int)
    for j,(u,v) in enumerate(E): M[V.index(u),j]=M[V.index(v),j]=1
    return M
def mospgraph(M):
    A=(M@M.T)>0; n=len(M); G=nx.Graph(); G.add_nodes_from(range(n))
    G.add_edges_from((i,j) for i in range(n) for j in range(i+1,n) if A[i,j]); return G
P,C=nx.path_graph,nx.cycle_graph
for (g,gn),(h,hn) in [((P(3),'P3'),(P(3),'P3')),((C(4),'C4'),(P(3),'P3')),((P(4),'P4'),(C(3),'C3')),((C(5),'C5'),(P(2),'P2'))]:
    M1,M2=inc(g),inc(h); n1,n2=len(M1),len(M2)
    Ms=np.kron(M1,M2); Mc=np.hstack([np.kron(M1,np.eye(n2,dtype=int)),np.kron(np.eye(n1,dtype=int),M2)])
    ok_s=nx.is_isomorphic(mospgraph(Ms),nx.strong_product(g,h)); ok_c=nx.is_isomorphic(mospgraph(Mc),nx.cartesian_product(g,h))
    vs,_=solve_mosp_exact(MOSPInstance.from_matrix(Ms,name=f'kron_{gn}_{hn}'),solutions_dir='sols')
    vc,_=solve_mosp_exact(MOSPInstance.from_matrix(Mc,name=f'cart_{gn}_{hn}'),solutions_dir='sols')
    v1,_=solve_mosp_exact(MOSPInstance.from_matrix(M1,name=gn),solutions_dir='sols'); v2,_=solve_mosp_exact(MOSPInstance.from_matrix(M2,name=hn),solutions_dir='sols')
    print(gn,hn,'shape kron',Ms.shape,'graph=strong',ok_s,'MOSP',vs,'>= prod',v1*v2,'| cart shape',Mc.shape,'graph=cart',ok_c,'MOSP',vc)
