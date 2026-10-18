import subprocess, sys, networkx as nx
def masks(G):
    nodes=list(G.nodes()); idx={v:i for i,v in enumerate(nodes)}
    m=[0]*len(nodes)
    for u,v in G.edges(): m[idx[u]]|=1<<idx[v]; m[idx[v]]|=1<<idx[u]
    return m
def myc(G):
    n=G.number_of_nodes(); G=nx.convert_node_labels_to_integers(G)
    H=nx.Graph(); H.add_nodes_from(range(2*n+1))
    for u,v in G.edges(): H.add_edges_from([(u,v),(u+n,v),(v+n,u)])
    for i in range(n): H.add_edge(n+i,2*n)
    return H
graphs=[]
for n in range(1,8):
    out=subprocess.run(['nauty-geng','-q',str(n)],capture_output=True,text=True).stdout.split()
    graphs+= [nx.from_graph6_bytes(s.encode()) for s in out]
print(len(graphs),file=sys.stderr)
inp=[]
for G in graphs:
    for H in (G,myc(G)):
        m=masks(H); inp.append(f"{len(m)} "+" ".join(map(str,m)))
res=subprocess.run(['nice','-n','19','./pwtw'],input="\n".join(inp)+"\n",capture_output=True,text=True).stdout.split("\n")
import pickle
rows=[]
for k,G in enumerate(graphs):
    pg,tg=map(int,res[2*k].split()); pm,tm=map(int,res[2*k+1].split())
    rows.append((nx.to_graph6_bytes(G,header=False).strip().decode(),G.number_of_nodes(),G.number_of_edges(),pg,tg,pm,tm))
pickle.dump(rows,open('rows.pkl','wb'))
