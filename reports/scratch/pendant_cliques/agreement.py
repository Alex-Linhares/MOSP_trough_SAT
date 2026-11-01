"""Does the maximal-clique evaluation (`pendant_graph_bound`) attain the exhaustive value of
Lemma P (every clique as `R`) on the random graphs of check.py?  Same seed, same graphs."""
import sys
from pathlib import Path
import networkx as nx
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from learning.forest_theorems import pendant_graph_bound
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check import lemma_p_best

rng = np.random.default_rng(1301)
total = equal = below = 0
for n in range(2, 9):
    for _ in range(300):
        p = float(rng.uniform(0.2, 0.9))
        g = nx.gnp_random_graph(n, p, seed=int(rng.integers(1 << 30)))
        if g.number_of_edges() == 0:
            continue
        cliques = [frozenset(c) for c in nx.enumerate_all_cliques(g)]
        best, _ = lemma_p_best(g, cliques)
        val, _ = pendant_graph_bound(g)
        total += 1
        equal += val == best
        below += val < best
        assert val <= best
print(f"{total} graphs: maximal-clique evaluation equals the exhaustive value on {equal}, below on {below}")
