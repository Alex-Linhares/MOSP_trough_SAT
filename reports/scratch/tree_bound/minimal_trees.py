"""Minimal trees of pathwidth k by the ternary construction: M(1) = K2; M(k+1) = a new vertex joined by
an edge to one vertex of each of three copies of (possibly different) trees from M(k).  Enumerates all
multisets of three (tree, vertex-orbit) choices, dedupes by WL hash + isomorphism, runs treepw on all, and
the C solver on a sample.  M(2) = {S(2,2,2)} (7 vertices), M(3) should be the 10 trees of exh_22.txt,
M(4) has 67 vertices."""
import sys, itertools, random, collections; sys.path.insert(0, "/home/al/dev/MOSP/reports/scratch/tree_bound")
from treelib import *
import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher

def orbits(T):
    reps = []; seen = set()
    for v in T.nodes():
        if v in seen: continue
        orb = {v}
        for iso in GraphMatcher(T, T).isomorphisms_iter():
            orb.add(iso[v])
            if len(seen | orb) == T.number_of_nodes(): pass
        seen |= orb; reps.append(v)
    return reps

def dedupe(graphs):
    buckets = collections.defaultdict(list); out = []
    for G in graphs:
        h = nx.weisfeiler_lehman_graph_hash(G, iterations=4)
        if any(nx.is_isomorphic(G, H) for H in buckets[h]): continue
        buckets[h].append(G); out.append(G)
    return out

def next_level(Ms):
    choices = [(i, v) for i, T in enumerate(Ms) for v in orbits(T)]
    print(f"  {len(Ms)} trees, {len(choices)} (tree, orbit) choices, {len(list(itertools.combinations_with_replacement(range(len(choices)), 3)))} multisets", flush=True)
    graphs = [join_at_root([(Ms[i], v) for (i, v) in combo]) for combo in itertools.combinations_with_replacement(choices, 3)]
    return graphs

kmax = int(sys.argv[1]) if len(sys.argv) > 1 else 4
sample = int(sys.argv[2]) if len(sys.argv) > 2 else 12
Ms = [nx.path_graph(2)]
print("M(1): N=2, 1 tree (K2)")
for k in range(2, kmax + 1):
    raw = next_level(Ms); Ms = dedupe(raw) if raw[0].number_of_nodes() <= 30 else raw
    n = Ms[0].number_of_nodes()
    pws = treepw_many([nx_to_parents(G) for G in Ms]) if n <= 127 else [None] * len(Ms)
    print(f"M({k}): N={n}, {len(raw)} constructed, {len(Ms)} after dedupe; treepw values: {dict(collections.Counter(pws))}", flush=True)
    rng = random.Random(k)
    for G in rng.sample(Ms, min(sample, len(Ms))):
        sw, st = solver_pw(G, 1800); print(f"   solver pw={sw} ({st}) treepw={treepw_many([nx_to_parents(G)])[0]} g6={g6(G)}", flush=True)
    # minimality: delete each leaf of one sample tree, pw must drop to k-1 (treepw), spot-check with solver
    G = Ms[0]; drops = []
    for leaf in [v for v in G.nodes() if G.degree(v) == 1]:
        H = G.copy(); H.remove_node(leaf); H = nx.convert_node_labels_to_integers(H); drops.append(treepw_many([nx_to_parents(H)])[0])
    print(f"   minimality of first tree: pw after deleting each leaf: {dict(collections.Counter(drops))}", flush=True)
    if k == 3:
        # the all-centre tree: new vertex joined to the centres of three S(2,2,2)
        S = spider([2, 2, 2]); A = join_at_root([(S, 0)] * 3); print(f"   all-centres M(3): g6={g6(A)} treepw={treepw_many([nx_to_parents(A)])[0]} solver={solver_pw(A)}")
