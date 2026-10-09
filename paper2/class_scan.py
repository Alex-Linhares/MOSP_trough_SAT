"""Class membership of the corpus MOSP graphs (paper2 survey, 2026-10-09).

For every certified corpus instance: is the MOSP graph complete, chordal,
interval (chordal and AT-free), AT-free, a cograph, co-disconnected (a join),
split, bipartite; the largest prime piece left by recursive component /
co-component splitting; and, for cographs, pathwidth + 1 by the
Bodlaender-Mohring formulas, checked against the certified optimum.
Single process, about one minute:  nice python paper2/class_scan.py
"""
import sys, csv, collections, json
sys.path.insert(0, "/home/al/dev/MOSP")
import os; os.chdir("/home/al/dev/MOSP")
import networkx as nx
from learning.dataset import enumerate_instances
from customer_inter.customer_graph import build_customer_graph

opt = {}
cert = {}
with open("learning/data/canonical.csv") as f:
    for r in csv.DictReader(f):
        opt[r["instance_name"]] = int(r["optimum"]); cert[r["instance_name"]] = r["graph_cert"]

def pieces(H):
    """Recursive component / co-component split; returns (pw if cograph-resolvable else None, max prime size)."""
    n = H.number_of_nodes()
    if n == 1: return 0, 1
    if not nx.is_connected(H):
        res = [pieces(H.subgraph(c).copy()) for c in nx.connected_components(H)]
        pw = None if any(r[0] is None for r in res) else max(r[0] for r in res)
        return pw, max(r[1] for r in res)
    C = nx.complement(H)
    if not nx.is_connected(C):
        comps = [set(c) for c in nx.connected_components(C)]
        res = [pieces(H.subgraph(c).copy()) for c in comps]
        prime = max(r[1] for r in res)
        if any(r[0] is None for r in res): return None, prime
        pw = min(r[0] + n - len(c) for r, c in zip(res, comps))
        return pw, prime
    return None, n

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

seen = {}
rows = []
for path, inst in enumerate_instances():
    name = inst.name
    if name not in opt: continue
    key = cert[name]
    if key not in seen:
        G = build_customer_graph(inst)
        n = G.number_of_nodes()
        complete = G.number_of_edges() == n * (n - 1) // 2
        chordal = nx.is_chordal(G)
        bip = nx.is_bipartite(G)
        pw, prime = pieces(G)
        atf = at_free(G) if n <= 140 else None
        seen[key] = dict(n=n, complete=complete, chordal=chordal, interval=bool(chordal and atf),
                         bipartite=bip, split=is_split(G), cograph=(prime == 1), prime=prime,
                         codisc=(n > 1 and nx.is_connected(G) and not nx.is_connected(nx.complement(G))),
                         atfree=atf, pw_formula=pw, omega=max(len(c) for c in nx.find_cliques(G)))
    r = dict(seen[key]); r["name"] = name; r["opt"] = opt[name]; r["src"] = str(path)
    rows.append(r)

out = "paper2/class_scan.json"
json.dump(rows, open(out, "w"))
def summ(rs, label):
    print(f"== {label}: {len(rs)}")
    for k in ["complete", "chordal", "interval", "atfree", "cograph", "codisc", "split", "bipartite"]:
        print(f"  {k:10s} {sum(1 for r in rs if r[k])}")
    nc = [r for r in rs if not r["complete"]]
    print("  non-complete:", len(nc))
    for k in ["chordal", "interval", "atfree", "cograph", "codisc", "split"]:
        print(f"    {k:10s} {sum(1 for r in nc if r[k])}")
    bad = [r for r in rs if r["pw_formula"] is not None and r["pw_formula"] + 1 != r["opt"]]
    good = [r for r in rs if r["pw_formula"] is not None]
    print("  cograph formula checked:", len(good), "mismatch:", len(bad))
    badi = [r for r in rs if r["interval"] and r["omega"] != r["opt"]]
    print("  interval omega==opt checked:", sum(r["interval"] for r in rs), "mismatch:", len(badi))
    print("  prime<n (some reduction) among connected non-cograph:", sum(1 for r in nc if not r["cograph"] and r["prime"] < r["n"]))
summ(rows, "instances")
uniq = {}
for r in rows: uniq.setdefault((r["n"], r["opt"], r["src"].split("/")[2]), r)
summ(list({cert[r["name"]]: r for r in rows}.values()), "distinct graphs")
