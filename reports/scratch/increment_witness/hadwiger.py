"""Randomised greedy search for a K_t minor in M_k (t = pw + 1): contract random
edges, preferring endpoints with few common neighbours (so few edges are lost),
down to t vertices; report the densest result over many trials."""
import iw, random, networkx as nx, sys
k = int(sys.argv[1]); trials = int(sys.argv[2]); rng = random.Random(0)
G0 = iw.mycielski(k); t = iw.FAMILIES["mycielski"][1][k] + 1
best = None
for trial in range(trials):
    H = G0.copy()
    while H.number_of_nodes() > t:
        edges = list(H.edges())
        # score: common neighbours (edges lost by merging); pick among the lowest few at random
        scored = sorted(edges, key=lambda e: (len(set(H[e[0]]) & set(H[e[1]])), rng.random()))
        v, u = scored[rng.randrange(min(3, len(scored)))]
        H = nx.contracted_nodes(H, u, v, self_loops=False, copy=True)
    m = H.number_of_edges(); need = t * (t - 1) // 2
    if best is None or m > best[0]: best = (m, trial)
    if m == need:
        print(f"M_{k}: K_{t} minor FOUND at trial {trial}"); break
print(f"M_{k}: target K_{t} needs {need} edges; best minor on {t} vertices has {best[0]} edges (trial {best[1]}) over {trials} trials")
