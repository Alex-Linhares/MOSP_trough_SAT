"""Adversarial search, second round: families biased towards branching (where tree pathwidth lives):
random cubic trees (internal degree 3), random 'quartic' trees (internal degree 4), random trees with
internal degrees in {3,4}, random recursive trees with max degree 4, and 'random ternary subtrees' of the
complete ternary tree (random connected subtrees), at 30..400 vertices.  Exact pw by treepw (n <= 127)
and the C solver (all).  Reports any violation of pw <= K(N) (K = sharp threshold) and extremal trees."""
import sys, random, math, collections, time; sys.path.insert(0, "/home/al/dev/MOSP/reports/scratch/tree_bound")
from treelib import *
import networkx as nx
def K(N):
    s, k = 2, 1
    while 3 * s + 1 <= N: s = 3 * s + 1; k += 1
    return k if N >= 2 else 0
def bound2a(N): return math.floor(math.log(2 * N + 1, 3) + 1e-9)
def fixed_internal(n, rng, degs):
    """grow: start with an edge; repeatedly pick a leaf and give it d-1 children (d from degs), until >= n; then trim to n by deleting leaves"""
    G = nx.path_graph(2); leaves = [0, 1]; nxt = 2
    while nxt < n:
        v = leaves.pop(rng.randrange(len(leaves))); d = rng.choice(degs)
        for _ in range(d - 1): G.add_edge(v, nxt); leaves.append(nxt); nxt += 1
    while G.number_of_nodes() > n:
        lv = [v for v in G.nodes() if G.degree(v) == 1]; G.remove_node(rng.choice(lv))
    return G
def ternary_subtree(n, rng):
    h = 1
    while (3 ** (h + 1) - 1) // 2 < 2 * n: h += 1
    T = nx.balanced_tree(3, h); S = {0}; frontier = [v for v in T[0]]
    while len(S) < n and frontier:
        v = frontier.pop(rng.randrange(len(frontier))); S.add(v); frontier += [u for u in T[v] if u not in S and u not in frontier]
    return T.subgraph(S).copy()
def rec_tree(n, rng, maxdeg):
    G = nx.empty_graph(1)
    for v in range(1, n):
        while True:
            p = rng.randrange(v)
            if G.degree(p) < maxdeg: break
        G.add_edge(v, p)
    return G
FAM = {"cubic": lambda n, r: fixed_internal(n, r, [3]), "quartic": lambda n, r: fixed_internal(n, r, [4]),
       "deg34": lambda n, r: fixed_internal(n, r, [3, 4]), "rec_maxdeg4": lambda n, r: rec_tree(n, r, 4),
       "rec_maxdeg3": lambda n, r: rec_tree(n, r, 3), "ternary_sub": ternary_subtree}
seed = int(sys.argv[1]); per = int(sys.argv[2]); sizes = [int(x) for x in sys.argv[3].split(",")]
rng = random.Random(seed); best = {}; disagree = viol = count = 0; t0 = time.time(); hist = collections.defaultdict(collections.Counter)
for n in sizes:
    for fam, f in FAM.items():
        for _ in range(per):
            G = nx.convert_node_labels_to_integers(f(n, rng)); assert nx.is_tree(G) and G.number_of_nodes() == n
            tp = treepw_many([nx_to_parents(G)])[0] if n <= 127 else None
            sw, st = solver_pw(G, 600); count += 1; hist[n][sw] += 1
            if tp is not None and tp != sw: disagree += 1; print(f"DISAGREE n={n} fam={fam} treepw={tp} solver={sw} ({st}) g6={g6(G)}", flush=True)
            if sw > K(n) or sw > bound2a(n) or st not in ("refutation", "bound", "minor"): viol += 1; print(f"VIOLATION/UNPROVED n={n} fam={fam} solver={sw} ({st}) K={K(n)} g6={g6(G)}", flush=True)
            if sw > best.get(n, (0,))[0]: best[n] = (sw, fam, st, g6(G))
    b = best[n]; print(f"n={n}: max pw={b[0]} ({b[1]}, {b[2]}) K(n)={K(n)} bound2a={bound2a(n)} pw hist={dict(sorted(hist[n].items()))} | trees {count}, disagreements {disagree}, violations {viol}, {time.time()-t0:.0f}s", flush=True)
print("extremal per size:"); [print(f"  n={n} pw={b[0]} fam={b[1]} {b[2]} g6={b[3][:60]}...") for n, b in sorted(best.items())]
