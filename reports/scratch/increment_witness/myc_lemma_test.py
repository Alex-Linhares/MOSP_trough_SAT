"""Small-instance test of candidate Mycielskian lemmas: for random connected G on 4..11
vertices, exact pw(G) and pw(M(G)) by the C program.  Candidates:
 (L1) pw(M(G)) <= 2 pw(G) + 1      (the trivial construction gives 2 pw + 2)
 (L2) pw(M(G)) >= 2 pw(G)          (true on M_3..M_6, false on M_7: 38 < 40)
 (L3) pw(M(G)) >= pw(G) + 1        (G with an edge)
Also records pw(M(G)) - pw(G) against |V(G)|, pw(G), alpha(G), delta(G)."""
import iw, random, json, collections
import networkx as nx
from concurrent.futures import ThreadPoolExecutor
rng = random.Random(1)
graphs = []
for n in range(4, 12):
    for _ in range(40):
        p = rng.choice([0.25, 0.4, 0.55, 0.7, 0.9])
        G = nx.gnp_random_graph(n, p, seed=rng.randrange(10**9))
        if G.number_of_edges() == 0 or not nx.is_connected(G): continue
        graphs.append(G)
def run(G):
    G = nx.convert_node_labels_to_integers(G)
    w, st, _ = iw.proved_width(G, t=60)
    M = iw.mycielski_step(G)
    wm, stm, _ = iw.proved_width(M, t=120)
    a = len(nx.max_weight_clique(nx.complement(G), weight=None)[0])
    return dict(n=G.number_of_nodes(), m=G.number_of_edges(), pw=w, pwM=wm, st=st, stM=stm, alpha=a, delta=min(d for _, d in G.degree()), Delta=max(d for _, d in G.degree()), g6=iw.to_g6(G))
with ThreadPoolExecutor(max_workers=2) as ex:
    R = list(ex.map(run, graphs))
R = [r for r in R if r["pw"] is not None and r["pwM"] is not None]
json.dump(R, open("myc_lemma_test.json", "w"), indent=1)
print(len(R), "graphs with both values proved")
print("L1 pw(M) <= 2pw+1 violations:", [r for r in R if r["pwM"] > 2 * r["pw"] + 1])
print("L1' pw(M) <= 2pw violations:", sum(1 for r in R if r["pwM"] > 2 * r["pw"]), "e.g.", [ (r["n"], r["pw"], r["pwM"], r["g6"]) for r in R if r["pwM"] > 2 * r["pw"]][:5])
print("L2 pw(M) >= 2pw violations:", sum(1 for r in R if r["pwM"] < 2 * r["pw"]), "e.g.", [ (r["n"], r["pw"], r["pwM"], r["g6"]) for r in R if r["pwM"] < 2 * r["pw"]][:5])
print("L3 pw(M) >= pw+1 violations:", sum(1 for r in R if r["pwM"] < r["pw"] + 1))
print("distribution of pw(M) - 2pw:", sorted(collections.Counter(r["pwM"] - 2 * r["pw"] for r in R).items()))
print("distribution of pw(M) - pw:", sorted(collections.Counter(r["pwM"] - r["pw"] for r in R).items()))
# increment against simple invariants
import itertools
for name, f in [("n - alpha", lambda r: r["n"] - r["alpha"]), ("pw", lambda r: r["pw"]), ("n", lambda r: r["n"]), ("pw + 1", lambda r: r["pw"] + 1), ("ceil(n/2)", lambda r: (r["n"] + 1) // 2)]:
    inc = [r["pwM"] - r["pw"] for r in R]; x = [f(r) for r in R]
    eq = sum(1 for a, b in zip(inc, x) if a == b); le = sum(1 for a, b in zip(inc, x) if a <= b); ge = sum(1 for a, b in zip(inc, x) if a >= b)
    print(f"increment pw(M)-pw vs {name}: equal {eq}, inc<= {le}, inc>= {ge} of {len(R)}")
print("pw(M) == n - alpha(M)? (M has alpha >= n):", sum(1 for r in R if r["pwM"] == 2 * r["n"] + 1 - max(r["n"], 0)), "(crude: alpha(M) >= n always)")
