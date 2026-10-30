"""Adversarial search for trees violating (2a) or the sharp threshold: pw(T) <= K(N) := max k with
s(k) <= N, s(1)=2, s(k)=3s(k-1)+1 (2, 7, 22, 67, 202, 607).  Families at 20..200 vertices: Prufer-random,
random recursive, random with max degree <= 4, caterpillars, spiders, random trees of spiders, random
'ternary-ish' (each vertex gets 0..3 children).  Exact pw by treepw (n <= 127) and the C solver (all n);
every tree with pw >= 3 or with treepw != solver is reported.  Records the max pw per size band."""
import sys, random, math, collections, time; sys.path.insert(0, "/home/al/dev/MOSP/reports/scratch/tree_bound")
from treelib import *
import networkx as nx
def K(N):
    s, k = 2, 1
    while 3 * s + 1 <= N: s = 3 * s + 1; k += 1
    return k if N >= 2 else 0
def bound2a(N): return math.floor(math.log(2 * N + 1, 3) + 1e-9)
def rec_tree(n, rng, maxdeg=None):
    G = nx.empty_graph(1)
    for v in range(1, n):
        while True:
            p = rng.randrange(v)
            if maxdeg is None or G.degree(p) < maxdeg: break
        G.add_edge(v, p)
    return G
def tree_of_spiders(n, rng):
    G = nx.empty_graph(0); nxt = 0; centres = []
    while nxt < n:
        c = nxt; G.add_node(c); nxt += 1
        if centres: G.add_edge(c, rng.choice(list(G.nodes())[:c]))
        centres.append(c)
        for _ in range(rng.randint(2, 4)):
            prev = c
            for _ in range(rng.randint(1, 3)):
                if nxt >= n: break
                G.add_edge(prev, nxt); prev = nxt; nxt += 1
    return G
def ternaryish(n, rng):
    G = nx.empty_graph(1); frontier = [0]; nxt = 1
    while nxt < n and frontier:
        v = frontier.pop(rng.randrange(len(frontier)))
        for _ in range(rng.choice([1, 2, 3, 3, 3])):
            if nxt >= n: break
            G.add_edge(v, nxt); frontier.append(nxt); nxt += 1
    return G
def caterpillar(n, rng):
    spine = rng.randint(2, n); G = nx.path_graph(spine)
    for v in range(spine, n): G.add_edge(v, rng.randrange(spine))
    return G
def spider_rand(n, rng):
    legs = []; rem = n - 1
    while rem > 0: L = rng.randint(1, max(1, rem // 2 + 1)); L = min(L, rem); legs.append(L); rem -= L
    return spider(legs)
FAM = {"prufer": lambda n, r: random_tree(n, r), "recursive": rec_tree, "maxdeg4": lambda n, r: rec_tree(n, r, 4),
       "caterpillar": caterpillar, "spider": spider_rand, "spiders": tree_of_spiders, "ternaryish": ternaryish}
seed = int(sys.argv[1]); per = int(sys.argv[2]); sizes = [int(x) for x in sys.argv[3].split(",")]
rng = random.Random(seed); best = {}; disagree = 0; viol = 0; count = 0; t0 = time.time()
for n in sizes:
    for fam, f in FAM.items():
        for _ in range(per):
            G = nx.convert_node_labels_to_integers(f(n, rng)); assert nx.is_tree(G) and G.number_of_nodes() == n
            tp = treepw_many([nx_to_parents(G)])[0] if n <= 127 else None
            sw, st = solver_pw(G, 600); count += 1
            if tp is not None and tp != sw: disagree += 1; print(f"DISAGREE n={n} fam={fam} treepw={tp} solver={sw} ({st}) g6={g6(G)}", flush=True)
            if sw > K(n) or sw > bound2a(n): viol += 1; print(f"VIOLATION n={n} fam={fam} solver={sw} ({st}) K={K(n)} g6={g6(G)}", flush=True)
            if sw > best.get(n, (0,))[0]: best[n] = (sw, fam, st, g6(G))
    b = best[n]; print(f"n={n}: max pw={b[0]} ({b[1]}, {b[2]}) K(n)={K(n)} bound2a={bound2a(n)} | trees so far {count}, disagreements {disagree}, violations {viol}, {time.time()-t0:.0f}s", flush=True)
print("extremal per size:"); [print(f"  n={n} pw={b[0]} fam={b[1]} {b[2]} g6={b[3]}") for n, b in sorted(best.items())]
