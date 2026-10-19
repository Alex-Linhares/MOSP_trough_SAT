"""pw(mu^j(G)) for named seeds (seeds_named.txt) given on argv as NAME:j. Appends to data_seeddeep.csv."""
import sys, csv, os, networkx as nx, multiprocessing as mp
from lib import *
S=dict(l.split() for l in open('seeds_named.txt') if l.strip())
def job(nj):
    name,j=nj.split(':'); j=int(j); G=nx.from_graph6_bytes(S[name].encode())
    for _ in range(j): G=myc(G)
    w,st,lay,sec=cprog(G,int(os.environ.get('TMO','900')))
    return dict(seed=name,seed_g6=S[name],j=j,n=G.number_of_nodes(),m=G.number_of_edges(),
                pw=w if st not in ('upper','timeout') else '',ub=w,status=st,sec=round(sec,2),layout=' '.join(lay))
if __name__=='__main__':
    cols=['seed','seed_g6','j','n','m','pw','ub','status','sec','layout']
    out=os.environ.get('OUT','data_seeddeep.csv'); new=not os.path.exists(out)
    with open(out,'a',newline='') as f, mp.Pool(int(os.environ.get('NPROC','4'))) as P:
        W=csv.DictWriter(f,cols)
        if new: W.writeheader()
        for r in P.imap_unordered(job,sys.argv[1:]):
            W.writerow(r); f.flush(); print(r['seed'],r['j'],r['n'],r['pw'],r['ub'],r['status'],r['sec'],flush=True)
