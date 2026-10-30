"""Dense structured families: exact pathwidth (C program, cap 300 s), deficit n - pw,
independence number alpha (exact: max clique of the complement), n - alpha."""
import iw, json, itertools, sys, time
import networkx as nx
from concurrent.futures import ThreadPoolExecutor

def cycle_power(n, k):
    G = nx.Graph(); G.add_nodes_from(range(n))
    for i in range(n):
        for j in range(1, k + 1): G.add_edge(i, (i + j) % n)
    return G
def circulant(n, S):
    G = nx.Graph(); G.add_nodes_from(range(n))
    for i in range(n):
        for s in S: G.add_edge(i, (i + s) % n)
    return G
def co_matching(n):   # complement of a perfect matching = cocktail party graph, n even
    return nx.complement(nx.from_edgelist([(2 * i, 2 * i + 1) for i in range(n // 2)]))
def co_path(n): return nx.complement(nx.path_graph(n))
def co_cycle(n): return nx.complement(nx.cycle_graph(n))
def multipartite(p, q): return nx.complete_multipartite_graph(*([q] * p))
def kneser(n, k=2):
    V = list(itertools.combinations(range(n), k)); idx = {v: i for i, v in enumerate(V)}
    G = nx.Graph(); G.add_nodes_from(range(len(V)))
    for a, b in itertools.combinations(V, 2):
        if not set(a) & set(b): G.add_edge(idx[a], idx[b])
    return G
def line_complete(n): return nx.convert_node_labels_to_integers(nx.line_graph(nx.complete_graph(n)))

jobs = []
for n in range(8, 41, 2):
    for k in range(2, 6):
        if 2 * k + 1 < n: jobs.append((f"C_{n}^{k}", "cycle_power", n, k, cycle_power(n, k)))
for n in range(6, 41, 2): jobs.append((f"co-matching n={n}", "co_matching", n, None, co_matching(n)))
for n in range(6, 41, 2): jobs.append((f"co-path n={n}", "co_path", n, None, co_path(n)))
for n in range(6, 41, 2): jobs.append((f"co-cycle n={n}", "co_cycle", n, None, co_cycle(n)))
for p in range(2, 9):
    for q in range(2, 9):
        if p * q <= 40: jobs.append((f"K_{p}x{q}", "multipartite", p * q, (p, q), multipartite(p, q)))
for n in range(5, 10): jobs.append((f"Kneser({n},2)", "kneser", n * (n - 1) // 2, n, kneser(n)))
for n in range(5, 10): jobs.append((f"L(K_{n})", "line_complete", n * (n - 1) // 2, n, line_complete(n)))
for n in range(10, 41, 5):
    for S in [(1, 3), (1, 4), (2, 3), (1, 2, 4), (1, 3, 5), (1, 2, 3, 5)]:
        if max(S) < n // 2: jobs.append((f"C_{n}({','.join(map(str,S))})", "circulant", n, S, circulant(n, S)))

def alpha(G):
    C = nx.complement(G)
    c, w = nx.max_weight_clique(C, weight=None)
    return len(c)

def run(j):
    name, fam, n, par, G = j
    G = nx.convert_node_labels_to_integers(G)
    t0 = time.time(); a = alpha(G); ta = time.time() - t0
    if not nx.is_connected(G):
        pass
    r = iw.run_c(G, t=300, layout=False)
    return dict(name=name, family=fam, n=G.number_of_nodes(), m=G.number_of_edges(), param=par, alpha=a, n_minus_alpha=G.number_of_nodes() - a,
                pw=r["width"], status=r["status"], deficit=(G.number_of_nodes() - r["width"]) if r["width"] is not None else None,
                proved=r["status"] in iw.PROVED, seconds=round(r["seconds"], 2), alpha_seconds=round(ta, 2),
                regular_degree=(min(d for _, d in G.degree()) if min(d for _, d in G.degree()) == max(d for _, d in G.degree()) else None),
                min_degree=min(d for _, d in G.degree()), max_degree=max(d for _, d in G.degree()), g6=r["g6"])

if __name__ == "__main__":
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    print(len(jobs), "graphs", flush=True)
    out = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for r in ex.map(run, jobs):
            out.append(r)
            print(f"{r['name']:22s} n={r['n']:3d} m={r['m']:4d} deg[{r['min_degree']},{r['max_degree']}] alpha={r['alpha']:2d} n-alpha={r['n_minus_alpha']:2d} pw={r['pw']} {r['status']:10s} deficit={r['deficit']} {r['seconds']}s", flush=True)
            json.dump(out, open("dense.json", "w"), indent=1)
