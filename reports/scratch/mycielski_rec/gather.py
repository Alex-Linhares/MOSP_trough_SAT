"""Exact pw of mu^j(G) for seeds G.  Usage: python3 gather.py SEEDFILE OUTCSV MAXN_CHAIN TIMEOUT
SEEDFILE: lines 'name g6'.  Chains continue while |V(mu^j)| <= MAXN_CHAIN and the previous call was exact."""
import os, sys, csv, networkx as nx, multiprocessing as mp, time
from lib import *
KNOWN={}  # M_k, k>=5, certified values (owner's rule: do not re-solve)
def mk(k):
    G=nx.complete_graph(2)
    for _ in range(k-2): G=myc(G)
    return G
for k,v in [(5,10),(6,20),(7,38),(8,72)]:
    KNOWN[nx.weisfeiler_lehman_graph_hash(mk(k))]=(k,v)
DPMAX=22; TWMAX=18
def basic(H):
    d=dict(n=H.number_of_nodes(),m=H.number_of_edges())
    degs=[x for _,x in H.degree()]
    d['maxdeg']=max(degs); d['mindeg']=min(degs)
    d['degen']=max(nx.core_number(H).values()) if H.number_of_edges() else 0
    if d['n']<=22:
        d['alpha']=max(len(c) for c in nx.find_cliques(nx.complement(H)))
        d['omega']=max(len(c) for c in nx.find_cliques(H))
    d['ncomp']=nx.number_connected_components(H); d['niso']=sum(1 for x in degs if x==0)
    return d
def chain(args):
    name,s,maxn,tmo=args
    G=nx.from_graph6_bytes(s.encode()); rows=[]; j=0; H=G
    while True:
        d=dict(seed=name,seed_g6=s,j=j); d.update(basic(H))
        h=nx.weisfeiler_lehman_graph_hash(H)
        t0=time.time()
        if h in KNOWN and d['n']>=23:
            k,v=KNOWN[h]; d.update(pw=v,status=f'certified_M{k}',sec=0,layout='')
        elif d['n']<=DPMAX:
            r=dp_batch([H],tw=d['n']<=TWMAX)[0]
            d.update(pw=r['pw'],tw=r['tw'] if r['tw']>=0 else '',tight=r['tight'],
                     lastmin=min(r['last']),firstmin=min(r['first']),
                     nlast_opt=sum(1 for x in r['last'] if x==r['pw']),
                     status='dp',layout=' '.join(map(str,r['layout'])))
            d['sec']=round(time.time()-t0,3)
        else:
            w,st,lay,sec=cprog(H,tmo)
            d.update(pw=w if st not in ('timeout','upper') else '',ub=w,status=st,sec=round(sec,3),layout=' '.join(lay))
        rows.append(d)
        if d['status'] in ('timeout',) or d['pw']=='' : break
        H=myc(H); j+=1
        if H.number_of_nodes()>maxn: break
    return rows
if __name__=='__main__':
    seeds=[l.split() for l in open(sys.argv[1]) if l.strip()]
    maxn=int(sys.argv[3]); tmo=int(sys.argv[4])
    cols=['seed','seed_g6','j','n','m','maxdeg','mindeg','degen','alpha','omega','ncomp','niso','pw','tw','tight','lastmin','firstmin','nlast_opt','ub','status','sec','layout']
    with open(sys.argv[2],'w',newline='') as f, mp.Pool(int(os.environ.get("NPROC","8"))) as P:
        W=csv.DictWriter(f,cols); W.writeheader()
        for rows in P.imap_unordered(chain,[(a,b,maxn,tmo) for a,b in seeds]):
            for r in rows: W.writerow(r)
            f.flush()
