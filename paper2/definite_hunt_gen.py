"""Random graphs for `paper2/definite_hunt.c` (loop0006 item 08).

    python3 paper2/definite_hunt_gen.py SEED COUNT NMIN NMAX [FAMILY]

Families: 0 G(n, p); 1 tree plus extra edges; 2 bounded degree; 3 union of small cliques
(MOSP-like); 4 the gadget -- a closed customer s whose open neighbours d_1..d_r share one new
stack y with q, q's other new stacks z_1..z_t hanging into a random rest. Family 4 is where
the definite move's counterexamples live. Default: a family drawn per graph.
"""
import sys, random
seed=int(sys.argv[1]); cnt=int(sys.argv[2]); lo,hi=int(sys.argv[3]),int(sys.argv[4])
rng=random.Random(seed)
def out(n,edges):
    m=[1<<v for v in range(n)]
    for u,v in edges: m[u]|=1<<v; m[v]|=1<<u
    print(n,*m)
for _ in range(cnt):
    n=rng.randint(lo,hi); fam=int(sys.argv[5]) if len(sys.argv)>5 else rng.randrange(5); E=set()
    if fam==0:
        p=rng.uniform(0.08,0.45); E={(u,v) for u in range(n) for v in range(u+1,n) if rng.random()<p}
    elif fam==1:  # tree + extra
        for v in range(1,n): E.add((rng.randrange(v),v))
        for _ in range(rng.randint(0,n//2)):
            u,v=sorted(rng.sample(range(n),2)); E.add((u,v))
    elif fam==2:  # bounded degree
        deg=[0]*n; D=rng.randint(2,4)
        for _ in range(3*n):
            u,v=sorted(rng.sample(range(n),2))
            if deg[u]<D and deg[v]<D and (u,v) not in E: E.add((u,v)); deg[u]+=1; deg[v]+=1
    elif fam==3:  # union of small cliques (MOSP-like)
        for _ in range(rng.randint(n//2,n)):
            s=rng.sample(range(n),rng.choice([2,2,3,3,4]))
            for i in s:
                for j in s:
                    if i<j: E.add((i,j))
    else:  # gadget: s, d's, q, y, z's + random rest
        r=rng.randint(2,3); t=rng.randint(2,r); rest=n-(3+r+t)
        if rest<1: continue
        s=0; q=1; y=2; ds=list(range(3,3+r)); zs=list(range(3+r,3+r+t)); R=list(range(3+r+t,n))
        E|={(s,q)}|{(s,d) for d in ds}|{(min(d,y),max(d,y)) for d in ds}|{(q,y)}|{(q,z) for z in zs}
        for z in zs:
            for w in rng.sample(R,rng.randint(1,len(R))): E.add((z,w))
        E.add((y,rng.choice(R)))
        p=rng.uniform(0.15,0.5)
        E|={(u,v) for u in R for v in R if u<v and rng.random()<p}
        for _ in range(rng.randint(0,2)):
            E.add((s,rng.choice(R)))
    out(n,E)
