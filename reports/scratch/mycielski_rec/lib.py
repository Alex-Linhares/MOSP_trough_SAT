import subprocess, networkx as nx, os
HERE=os.path.dirname(os.path.abspath(__file__))
CPROG='/home/al/dev/MOSP/pathwidth_solver/cli/pathwidth'
def myc(G):
    """Mycielskian: originals 0..n-1, shadows n..2n-1, w = 2n."""
    G=nx.convert_node_labels_to_integers(G); n=G.number_of_nodes()
    H=nx.Graph(); H.add_nodes_from(range(2*n+1))
    for u,v in G.edges(): H.add_edges_from([(u,v),(u+n,v),(v+n,u)])
    for i in range(n): H.add_edge(n+i,2*n)
    return H
def masks(G):
    nodes=sorted(G.nodes()); idx={v:i for i,v in enumerate(nodes)}
    m=[0]*len(nodes)
    for u,v in G.edges(): m[idx[u]]|=1<<idx[v]; m[idx[v]]|=1<<idx[u]
    return m
def g6(G): return nx.to_graph6_bytes(nx.convert_node_labels_to_integers(G),header=False).strip().decode()
def dp_batch(graphs, tw=True):
    inp="".join(f"{G.number_of_nodes()} {1 if tw else 0} "+" ".join(map(str,masks(G)))+"\n" for G in graphs)
    out=subprocess.run(['nice','-n','19',os.path.join(HERE,'dp')],input=inp,capture_output=True,text=True,check=True).stdout.strip().split("\n")
    res=[]
    for line in out:
        a,last,first,lay=line.split(" | ")
        pw,t,tight=map(int,a.split())
        res.append(dict(pw=pw,tw=t,tight=tight,last=list(map(int,last.split()[1:])),first=list(map(int,first.split()[1:])),layout=list(map(int,lay.split()[1:]))))
    return res
def cprog(G, t=600):
    """C program on one graph; returns (width,status,layout,seconds)."""
    import time
    s=g6(G); t0=time.time()
    out=subprocess.run(['nice','-n','19',CPROG,'-t',str(t),'-l'],input=s+"\n",capture_output=True,text=True).stdout.split("\n")
    w,status=out[0].split()[1:3]; lay=out[1].split()[1:]
    return int(w),status,lay,time.time()-t0
def vs_layout(G,order):
    pos={v:i for i,v in enumerate(order)}; best=0
    for i in range(len(order)):
        S=set(order[:i+1]); best=max(best,sum(1 for u in S if any(pos[x]>i for x in G[u])))
    return best
def lattice_batch(items):
    """items: list of (G, L, Lp) with G on vertices 0..n-1. Returns list of U."""
    lines=[]
    for G,L,Lp in items:
        n=G.number_of_nodes(); s=[str(n)]
        for v in range(n): nbrs=list(G[v]); s.append(str(len(nbrs))); s+=map(str,nbrs)
        s+=map(str,L); s+=map(str,Lp); lines.append(" ".join(s))
    out=subprocess.run(['nice','-n','19',os.path.join(HERE,'lattice')],input="\n".join(lines)+"\n",capture_output=True,text=True,check=True).stdout.split()
    return list(map(int,out))
def lattice_layout(G,L,Lp):
    n=G.number_of_nodes(); s=[str(n)]
    for v in range(n): nbrs=list(G[v]); s.append(str(len(nbrs))); s+=map(str,nbrs)
    s+=map(str,L); s+=map(str,Lp)
    env=dict(os.environ,LAYOUT='1')
    out=subprocess.run(['nice','-n','19',os.path.join(HERE,'lattice')],input=" ".join(s)+"\n",capture_output=True,text=True,check=True,env=env).stdout
    a,b=out.split('|'); return int(a), list(map(int,b.split()))
