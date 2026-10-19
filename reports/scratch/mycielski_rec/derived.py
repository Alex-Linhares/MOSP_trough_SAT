import pandas as pd, networkx as nx
from lib import *
d=pd.read_csv('data_all7.csv')
P=d.pivot_table(index='seed',columns='j',values='pw')
b=d[d.j==0].set_index('seed').copy(); b['p1']=P[1]
Gs=[nx.convert_node_labels_to_integers(nx.from_graph6_bytes(s.encode())) for s in b.seed_g6]
def dbl(G):  # bipartite double cover
    n=G.number_of_nodes(); H=nx.Graph(); H.add_nodes_from(range(2*n))
    for u,v in G.edges(): H.add_edges_from([(u,v+n),(v,u+n)]); 
    return H
def mw(G): H=myc(G); H.remove_node(2*G.number_of_nodes()); return H
def cart(G):
    n=G.number_of_nodes(); H=nx.Graph(); H.add_nodes_from(range(2*n))
    for u,v in G.edges(): H.add_edges_from([(u,v),(u+n,v+n)])
    for v in range(n): H.add_edge(v,v+n)
    return H
for name,f in [('pw_mw',mw),('pw_dbl',dbl),('pw_cart',cart)]:
    b[name]=[r['pw'] for r in dp_batch([f(G) for G in Gs],tw=False)]
b.to_csv('derived_all7.csv')
print((b.p1-b.pw_mw).value_counts())
for c in ['pw_mw','pw_dbl','pw_cart']:
    g=b.groupby(['pw',c]).p1; print(c,'conflict rows',(g.size()-g.agg(lambda x:x.value_counts().iloc[0])).sum(),'cells',g.ngroups)
g=b.groupby(['pw','pw_dbl','pw_cart']).p1; print('3',(g.size()-g.agg(lambda x:x.value_counts().iloc[0])).sum())
