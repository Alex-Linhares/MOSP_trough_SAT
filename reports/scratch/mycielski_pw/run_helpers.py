import networkx as nx
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
