import pandas as pd, networkx as nx, itertools, multiprocessing as mp
from lib import *
def work(args):
    s,pw=args
    G=nx.convert_node_labels_to_integers(nx.from_graph6_bytes(s.encode()))
    perms=list(itertools.permutations(range(G.number_of_nodes())))
    U=lattice_batch([(G,list(p),list(p)) for p in perms])
    Urev=lattice_batch([(G,list(p),list(p)[::-1]) for p in perms])
    vsl=[vs_layout(G,p) for p in perms]
    same=min(U); sameopt=min(u for u,v in zip(U,vsl) if v==pw)
    # best U among layouts by vs: min U for vs = pw, pw+1, ...
    return s,same,sameopt,min(Urev)
if __name__=='__main__':
    d=pd.read_csv('data_all7.csv')
    P=d.pivot_table(index='seed',columns='j',values='pw')
    b=d[d.j==0].set_index('seed').copy(); b['p1']=P[1]
    with mp.Pool(8) as Pl: R=Pl.map(work,list(zip(b.seed_g6,b.pw)),chunksize=4)
    r=pd.DataFrame(R,columns=['seed_g6','same','sameopt','rev']).set_index('seed_g6')
    b=b.join(r,on='seed_g6')
    b[['seed_g6','n','pw','p1','same','sameopt','rev']].to_csv('same_order_all7.csv')
    for c in ['same','sameopt','rev']: print(c,(b[c]==b.p1).sum(),len(b),(b[c]-b.p1).value_counts().to_dict())
