"""Check an upper-bound layout: python mc_layout_check.py GRAPH.dgf ORDER.txt
Prints max over prefixes P of |N(P) - P| (= vertex separation of the reversed
layout, hence an upper bound on pathwidth). ORDER.txt holds 0-based labels."""
import sys
from mc_graph import read_dgf
G = read_dgf(sys.argv[1]); order = list(map(int, open(sys.argv[2]).read().split()))
assert sorted(order) == sorted(G), "not a permutation"
P, worst = set(), 0
for v in order:
    P.add(v)
    worst = max(worst, len({u for x in P for u in G[x]} - P))
print(f"{sys.argv[2]}: layout of {len(order)} vertices, max prefix boundary {worst}")
