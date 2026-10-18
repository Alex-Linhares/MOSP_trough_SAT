import random, pickle, networkx as nx
def vs(adj, order):
    pos={v:i for i,v in enumerate(order)}; best=0
    for i in range(len(order)):
        S=set(order[:i+1])
        best=max(best,sum(1 for u in S if any(x not in S for x in adj[u])))
    return best
random.seed(1); worst=-99
for t in range(20000):
    n=random.randint(1,11); p=random.random()
    G=nx.gnp_random_graph(n,p,seed=random.randrange(10**9))
    adj={v:set(G[v]) for v in G}
    M={('o',v):{('o',u) for u in adj[v]}|{('s',u) for u in adj[v]} for v in adj}
    for v in adj: M[('s',v)]={('o',u) for u in adj[v]}|{('w',)}
    M[('w',)]={('s',v) for v in adj}
    L=list(adj); random.shuffle(L)
    Lm=[('w',)]+[x for v in L for x in (('o',v),('s',v))]
    a,b=vs(adj,L),vs(M,Lm); worst=max(worst,b-(2*a+1))
    assert b<=2*a+1,(n,G.edges(),L)
print("max vs(mu-layout)-(2vs(L)+1) =",worst)
