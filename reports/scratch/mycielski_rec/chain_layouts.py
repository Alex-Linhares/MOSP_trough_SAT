import networkx as nx
from lib import *
C='/home/al/dev/MOSP/reports/scratch/minor_certificates/'
def load_edges(fn):
    L=open(fn).read().split("\n"); n,m=map(int,L[0].split())
    G=nx.Graph(); G.add_nodes_from(range(n)); G.add_edges_from(tuple(map(int,l.split())) for l in L[1:] if l.strip()); return G
def oriented(G,order):
    a=vs_layout_fast(G,order); b=vs_layout_fast(G,order[::-1])
    return (order,a) if a<=b else (order[::-1],b)
def vs_layout_fast(G,order):
    pos={v:i for i,v in enumerate(order)}; last={v:max([pos[u] for u in G[v]]+[-1]) for v in G}
    best=0; act=0
    # active at cut i: placed v (pos<=i) with last[v]>i
    import collections
    ends=collections.Counter(last[v] for v in G)
    cnt=0
    for i,v in enumerate(order):
        if last[v]>i: cnt+=1
        # remove vertices whose last neighbour is i (placed earlier)
        cnt-=sum(1 for u in G[v] if pos[u]<i and last[u]==i)
        best=max(best,cnt)
    return best
if __name__=='__main__':
    G6=load_edges(C+'myciel6_full_edges.txt'); G7=load_edges(C+'myciel7_full_edges.txt')
    o6=list(map(int,open(C+'myciel6_w38_order.txt').read().split())); o7=list(map(int,open(C+'myciel7_w72_order.txt').read().split()))
    for name,G,o in [('M7',G6,o6),('M8',G7,o7)]:
        o,w=oriented(G,o); print(name,G.number_of_nodes(),'layout width',w, 'check',vs_layout(G,o) if G.number_of_nodes()<100 else '')
        U=lattice_batch([(G,o,o)])[0]; print('  U(L,L) ->',U)
