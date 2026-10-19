import pandas as pd, networkx as nx, sys
from lib import *
def maxpw_minus_closed_nbhd(G):
    Hs=[]
    for x in G:
        H=G.copy(); H.remove_nodes_from(list(G[x])+[x]); Hs.append(nx.convert_node_labels_to_integers(H))
    res=[]; nonempty=[H for H in Hs if H.number_of_nodes()>0]
    r=dp_batch(nonempty,tw=False) if nonempty else []
    it=iter(r)
    for H in Hs: res.append(next(it)['pw'] if H.number_of_nodes()>0 else -1)
    return max(res), res
if __name__=='__main__':
    for fn in sys.argv[1:]:
        d=pd.read_csv(fn)
        P=d.pivot_table(index='seed',columns='j',values='pw')
        b=d[d.j==0].set_index('seed').copy(); b['p1']=P[1]
        b=b[b.n<=20]
        b['q']=[maxpw_minus_closed_nbhd(nx.convert_node_labels_to_integers(nx.from_graph6_bytes(s.encode())))[0] for s in b.seed_g6]
        b['g']=b.p1-b.pw-1-b.q
        print(fn, len(b), 'min p1-pw-1-q =',b.g.min()); print(b.g.value_counts().sort_index().to_dict())
        print(b.sort_values('g').head(5)[['seed_g6','n','m','pw','p1','q']].to_string())
