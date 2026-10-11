"""Mohar-Poljak spectral separator bound applied to vertex separation, and
Lucena's MCS lower bound (treewidth), on myciel5/6."""
import sys, random
from pathlib import Path
import numpy as np, networkx as nx
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "pathwidth_solver" / "bench"))
from readers import read_any, HERE

def mohar_poljak_vs(G):
    """vs >= min over layouts of max_i |X_i|; at cut i: A = prefix minus X, B = suffix,
    |X| >= 4 l2 |A||B| / (D n - l2 |A u B|) (Mohar & Poljak 1993; DPS 2002 Thm 9.4).
    For each i the bound must hold for the layout's own s=|X_i|: smallest s with
    s >= f(s) where a = i - s, b = n - i. Return max over i of that smallest s."""
    n = G.number_of_nodes(); L = nx.laplacian_matrix(G).toarray().astype(float)
    l2 = np.linalg.eigvalsh(L)[1]; D = max(d for _, d in G.degree()); best = 0
    for i in range(1, n):
        b = n - i
        for s in range(0, i + 1):
            a = i - s
            if s >= 4 * l2 * a * b / (D * n - l2 * (a + b)) - 1e-9:
                best = max(best, s); break
    return best, l2, D

def mcslb(G, rng, tries=50):
    best = 0; nodes = list(G)
    for _ in range(tries):
        visited = set(); cnt = {v: 0 for v in G}; v = rng.choice(nodes)
        while True:
            visited.add(v); best = max(best, cnt[v])
            for u in G[v]:
                if u not in visited: cnt[u] += 1
            rest = [u for u in G if u not in visited]
            if not rest: break
            mx = max(cnt[u] for u in rest); v = rng.choice([u for u in rest if cnt[u] == mx])
    return best

def mcslb_plus(G, rng):
    H = nx.Graph(G); best = 0
    while H.number_of_edges():
        best = max(best, mcslb(H, rng, 3))
        v = min(H, key=H.degree); nb = list(H[v])
        u = min(nb, key=lambda c: len(set(H[c]) & set(nb)))
        H = nx.contracted_nodes(H, u, v, self_loops=False)
    return best

rng = random.Random(3)
for name in ("myciel5", "myciel6"):
    G = nx.convert_node_labels_to_integers(read_any(HERE / "coloring" / f"{name}.dgf"))
    mp, l2, D = mohar_poljak_vs(G)
    z = max(G, key=G.degree); Gz = G.copy(); Gz.remove_node(z)
    mpz, l2z, Dz = mohar_poljak_vs(nx.convert_node_labels_to_integers(Gz))
    print(f"{name}: Mohar-Poljak vs bound {mp} (l2={l2:.2f}, D={D}); on G - hub: {mpz} (l2={l2z:.2f}, D={Dz}) => pw >= {mpz}; "
          f"MCSLB {mcslb(G, rng)}; MCSLB+ {mcslb_plus(G, rng)}", flush=True)
