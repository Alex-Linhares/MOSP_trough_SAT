"""pw(mu^j(K_n)) for the pairs given on argv as n:j, C program, layout saved. Appends to data_kn.csv."""
import sys, csv, os, networkx as nx, multiprocessing as mp
from lib import *
def job(nj):
    n,j=map(int,nj.split(':')); G=nx.complete_graph(n)
    for _ in range(j): G=myc(G)
    w,st,lay,sec=cprog(G,int(os.environ.get('TMO','900')))
    return dict(seed=f'K{n}',seed_g6=g6(nx.complete_graph(n)),j=j,n=G.number_of_nodes(),m=G.number_of_edges(),
                pw=w if st not in ('upper','timeout') else '',ub=w,status=st,sec=round(sec,2),layout=' '.join(lay))
if __name__=='__main__':
    cols=['seed','seed_g6','j','n','m','pw','ub','status','sec','layout']
    new=not os.path.exists('data_kn.csv')
    with open('data_kn.csv','a',newline='') as f, mp.Pool(int(os.environ.get('NPROC','4'))) as P:
        W=csv.DictWriter(f,cols); 
        if new: W.writeheader()
        for r in P.imap_unordered(job,sys.argv[1:]):
            W.writerow(r); f.flush(); print(r['seed'],r['j'],r['n'],r['pw'],r['status'],r['sec'],flush=True)
