"""Write complete k-ary trees of height h as graph6 (networkx balanced_tree)."""
import sys, networkx as nx
k, h = int(sys.argv[1]), int(sys.argv[2])
G = nx.balanced_tree(k, h)
sys.stdout.buffer.write(nx.to_graph6_bytes(G, header=False))
