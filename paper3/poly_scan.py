"""Polynomial-class membership of the certified corpus (paper3/polynomial_cases.md, 2026-10-09).

Extends class_scan.py. For every distinct MOSP graph (by graph_cert): forest,
pseudoforest (every component at most one cycle: trees and unicyclic graphs),
block graph, cactus, treewidth <= 2, split (with the two-vertex criterion checked
against the certified optimum), and, for interval graphs, whether the matrix is
conformal (every maximal clique of G_M inside one pattern), which is exactly when
the dominance-reduced matrix has the consecutive-ones property in its rows.
Then the recursive component / co-component split, and whether every prime piece
lies in a class with a practical exact algorithm.
Single process:  nice python paper3/poly_scan.py
"""
import sys, csv, json, itertools, collections
sys.path.insert(0, "/home/al/dev/MOSP")
import os; os.chdir("/home/al/dev/MOSP")
import networkx as nx
from learning.dataset import enumerate_instances
from customer_inter.customer_graph import build_customer_graph

opt, cert, coll = {}, {}, {}
with open("learning/data/canonical.csv") as f:
    for r in csv.DictReader(f):
        opt[r["instance_name"]] = int(r["optimum"]); cert[r["instance_name"]] = r["graph_cert"]
        coll[r["instance_name"]] = r["collection"]

def is_block(G):
    return all(G.subgraph(b).number_of_edges() == len(b) * (len(b) - 1) // 2
               for b in nx.biconnected_components(G))

def is_cactus(G):  # every block an edge or a cycle
    for b in nx.biconnected_components(G):
        H = G.subgraph(b)
        if len(b) > 2 and H.number_of_edges() != len(b):
            return False
    return True

def is_pseudoforest(G):
    return all(G.subgraph(c).number_of_edges() <= len(c) for c in nx.connected_components(G))

def tw_le_2(G):
    H = nx.Graph(G)
    changed = True
    while changed and H.number_of_nodes():
        changed = False
        for v in list(H):
            d = H.degree(v)
            if d <= 1:
                H.remove_node(v); changed = True
            elif d == 2:
                a, b = list(H[v]); H.remove_node(v); H.add_edge(a, b); changed = True
    return H.number_of_nodes() == 0

def interval(G):
    if not nx.is_chordal(G): return False
    return at_free(G)

def at_free(H):
    nodes = list(H)
    comp = {}
    for v in nodes:
        R = H.copy(); R.remove_nodes_from(list(H[v]) + [v])
        lab = {}
        for i, c in enumerate(nx.connected_components(R)):
            for u in c: lab[u] = i
        comp[v] = lab
    nbr = {v: set(H[v]) for v in nodes}
    for i, a in enumerate(nodes):
        for j in range(i + 1, len(nodes)):
            b = nodes[j]
            if b in nbr[a]: continue
            for k in range(j + 1, len(nodes)):
                c = nodes[k]
                if c in nbr[a] or c in nbr[b]: continue
                la, lb, lc = comp[a], comp[b], comp[c]
                if lc.get(a) is not None and lc.get(a) == lc.get(b) and \
                   lb.get(a) is not None and lb.get(a) == lb.get(c) and \
                   la.get(b) is not None and la.get(b) == la.get(c):
                    return False
    return True

def is_split(H):
    d = sorted((deg for _, deg in H.degree()), reverse=True)
    m = max([i for i in range(len(d)) if d[i] >= i] + [0]) + 1
    return sum(d[:m]) == m * (m - 1) + sum(d[m:])

def split_pw(G):
    # a maximum clique whose complement is independent (not every maximum clique has one)
    om = max(len(c) for c in nx.find_cliques(G))
    K = next(set(c) for c in nx.find_cliques(G) if len(c) == om and
             not any(G.has_edge(a, b) for a, b in itertools.combinations(set(G) - set(c), 2)))
    I = set(G) - K
    for x in K:
        for y in K:
            if all(not (G.has_edge(p, x) and G.has_edge(p, y)) for p in I):
                return len(K) - 1
    return len(K)

def omega(G):
    return max(len(c) for c in nx.find_cliques(G)) if G.number_of_nodes() else 0

def practical(H):
    """(class, pw or None) for a prime piece with a practical exact algorithm."""
    n = H.number_of_nodes()
    if n == 1: return "K1", 0
    if H.number_of_edges() == n * (n - 1) // 2: return "complete", n - 1
    if nx.is_chordal(H) and at_free(H): return "interval", omega(H) - 1
    if is_split(H): return "split", split_pw(H)
    if is_block(H): return "block", None
    if is_pseudoforest(H): return "unicyclic", None
    return None, None

def decompose(H):
    """Returns (pw if fully resolved by formulas else None, all_prime_pieces_practical, prime classes)."""
    n = H.number_of_nodes()
    if n == 1: return 0, True, []
    if not nx.is_connected(H):
        res = [decompose(H.subgraph(c).copy()) for c in nx.connected_components(H)]
        pw = None if any(r[0] is None for r in res) else max(r[0] for r in res)
        return pw, all(r[1] for r in res), sum((r[2] for r in res), [])
    C = nx.complement(H)
    if not nx.is_connected(C):
        comps = [set(c) for c in nx.connected_components(C)]
        res = [decompose(H.subgraph(c).copy()) for c in comps]
        pw = None if any(r[0] is None for r in res) else min(r[0] + n - len(c) for r, c in zip(res, comps))
        return pw, all(r[1] for r in res), sum((r[2] for r in res), [])
    cls, pw = practical(H)
    return pw, cls is not None, [cls]

def conformal(inst, G):
    cols = [frozenset(inst.pattern_customers(j)) for j in range(inst.n_patterns)]
    return all(any(set(Q) <= c for c in cols) for Q in nx.find_cliques(G) if len(Q) > 1)

seen, rows = {}, []
for path, inst in enumerate_instances():
    name = inst.name
    if name not in opt: continue
    key = cert[name]
    G = build_customer_graph(inst)
    n = G.number_of_nodes()
    if key not in seen:
        complete = G.number_of_edges() == n * (n - 1) // 2
        chordal = nx.is_chordal(G)
        itv = chordal and at_free(G)
        spl = is_split(G)
        pwf, prac, classes = decompose(G)
        seen[key] = dict(n=n, complete=complete, forest=nx.is_forest(G), pseudoforest=is_pseudoforest(G),
                         block=is_block(G), cactus=is_cactus(G), tw2=tw_le_2(G), chordal=chordal,
                         interval=itv, split=spl, split_pw=(split_pw(G) if spl else None), omega=omega(G),
                         formula_pw=pwf, prime_practical=prac,
                         prime_classes=sorted(set(c for c in classes if c)))
    r = dict(seen[key]); r["name"] = name; r["opt"] = opt[name]; r["coll"] = coll[name]
    r["conformal"] = conformal(inst, G) if r["interval"] else None
    rows.append(r)

json.dump(rows, open("paper3/poly_scan.json", "w"))
def cnt(f, rs): return sum(1 for r in rs if f(r))
def summ(rs, label):
    print(f"== {label}: {len(rs)}")
    for k in ["complete", "forest", "pseudoforest", "block", "cactus", "tw2", "chordal", "interval", "split"]:
        print(f"  {k:13s} {cnt(lambda r: r[k], rs):5d}   non-complete {cnt(lambda r: r[k] and not r['complete'], rs)}")
    print("  interval & conformal (row-C1P after dominance):", cnt(lambda r: r["interval"] and r["conformal"], rs))
    print("  split formula checked:", cnt(lambda r: r["split"], rs), "mismatch:", cnt(lambda r: r["split"] and r["split_pw"] + 1 != r["opt"], rs))
    print("  formula-resolved (cograph/interval/split pieces):", cnt(lambda r: r["formula_pw"] is not None, rs),
          "mismatch:", cnt(lambda r: r["formula_pw"] is not None and r["formula_pw"] + 1 != r["opt"], rs))
    print("  every prime piece practical:", cnt(lambda r: r["prime_practical"], rs),
          " non-complete:", cnt(lambda r: r["prime_practical"] and not r["complete"], rs))
    print("  ... needing block/unicyclic algorithm:", cnt(lambda r: r["prime_practical"] and r["formula_pw"] is None, rs))
    print("  poly in theory only (tw<=2, not practical):", cnt(lambda r: r["tw2"] and not r["prime_practical"], rs))
    byc = collections.Counter(r["coll"].split("/")[-1] for r in rs if r["prime_practical"])
    tot = collections.Counter(r["coll"].split("/")[-1] for r in rs)
    print("  per collection (practical / total):", {k: f"{byc.get(k,0)}/{v}" for k, v in sorted(tot.items())})
summ(rows, "instances")
summ(list({cert[r["name"]]: r for r in rows}.values()), "distinct graphs")
