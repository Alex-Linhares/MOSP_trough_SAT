"""The induced-subgraph claims behind finding 3's monotone lower bounds, by code: CT(s-1, h, b),
CT(s, h-1, b) and CT(s, h, b-1) are induced subgraphs of CT(s, h, b) (networkx VF2 on induced subgraph
isomorphism, small cells), and CT(2, h, 3) contains the complete ternary tree of height h as a rooted
subtree (ternary_subtree_height)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher
from learning.block_trees import clique_tree, ct_size, mosp_graph, ternary_subtree_height
ok = 0
for s in (2, 3, 4):
    for h in (1, 2):
        for b in (1, 2, 3):
            if ct_size(s, h, b) > 60: continue
            G = mosp_graph(clique_tree(s, h, b)[0])
            for key in ((s - 1, h, b), (s, h - 1, b), (s, h, b - 1)):
                if key[0] < 2 or key[1] < 0 or key[2] < 1: continue
                H = mosp_graph(clique_tree(*key)[0])
                found = GraphMatcher(G, H).subgraph_is_isomorphic()   # induced subgraph isomorphism
                print(f"CT{key} induced in CT({s},{h},{b}): {found}"); ok += found
                assert found
for h in (1, 2, 3, 4):
    G = mosp_graph(clique_tree(2, h, 3)[0])
    print(f"CT(2,{h},3): complete ternary subtree height {ternary_subtree_height(G)} (>= {h} claimed)")
    assert ternary_subtree_height(G) >= h
print("all claims hold:", ok, "inclusions")
