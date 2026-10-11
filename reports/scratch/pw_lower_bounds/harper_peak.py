"""Heavier local search for Phi(i) near the peak of the profile."""
import sys, random
from harper_ceiling_lib import *
for name, rng_i in [("myciel5", range(24, 38)), ("myciel6", range(44, 76))]:
    G = nx.convert_node_labels_to_integers(read_any(HERE / "coloring" / f"{name}.dgf"))
    rng = random.Random(7); res = {}
    for i in rng_i:
        res[i] = min(phi_search(G, i, 150000, rng) for _ in range(4))
    print(name, "max over these i of best found:", max(res.values()), res, flush=True)
