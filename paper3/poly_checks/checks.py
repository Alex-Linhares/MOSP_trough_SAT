"""Small-case checks for paper3/polynomial_cases.md (2026-10-09).

Every claim is checked against exact pathwidth: pathwidth_solver (refutation-proved)
and, at n <= 18, also the independent subset DP. MOSP = pw(G_M) + 1 (MOSPGraph.lean).
Run:  nice python paper3/poly_checks/checks.py   (one core, a few minutes)
"""
import sys, random, itertools, functools, time
sys.path.insert(0, "/home/al/dev/MOSP/pathwidth_solver"); sys.path.insert(0, "/home/al/dev/MOSP")
import networkx as nx
from pathwidth.solve import solve
from fixed_parameter_algorithm.pathwidth import compute_pathwidth as dp_pw

def pw(G):
    if G.number_of_edges() == 0:
        return 0
    s = solve(G)
    assert s.proved, "unproved"
    if G.number_of_nodes() <= 18:
        d = dp_pw(G)
        d = d[0] if isinstance(d, tuple) else d
        assert d == s.width, (d, s.width)
    return s.width

def mosp_graph(rows):
    """rows: list of sets of patterns (one per customer)."""
    G = nx.Graph(); G.add_nodes_from(range(len(rows)))
    for i, j in itertools.combinations(range(len(rows)), 2):
        if rows[i] & rows[j]:
            G.add_edge(i, j)
    return G

def mosp(rows):
    G = mosp_graph(rows)
    return pw(G) + 1 if any(rows) else 0

R = random.Random(20261009)
out = []
def report(name, ok, n):
    out.append(f"{name}: {ok}/{n} agree"); print(out[-1], flush=True)

# ---- 1. Chou et al. 2008 Theorem 4 (block graphs), recursive form, against the exact solver
def chou_ns(G):
    @functools.lru_cache(maxsize=None)
    def ns(V):
        H = G.subgraph(V)
        if H.number_of_edges() == 0:
            return 1 if V else 0
        comps = list(nx.connected_components(H))
        if len(comps) > 1:
            return max(ns(frozenset(c)) for c in comps)
        blocks = [frozenset(b) for b in nx.biconnected_components(H)]
        def comp_without(x, y):  # component of H - x containing y
            K = H.subgraph(V - {x})
            return frozenset(nx.node_connected_component(K, y))
        k = 2
        while True:
            vc = True
            for x in V:
                K = H.subgraph(V - {x})
                big = sum(1 for c in nx.connected_components(K) if ns(frozenset(c)) >= k)
                if big > 2:
                    vc = False; break
            bc = vc and all(
                any(ns(comp_without(x, y) & (comp_without(y, x) | {y})) < k
                    for x in B for y in B if x != y)
                for B in blocks)
            if vc and bc:
                return k
            k += 1
    return ns(frozenset(G.nodes()))

def random_block_graph(n):
    G = nx.Graph(); G.add_node(0); nxt = 1
    while nxt < n:
        v = R.randrange(nxt); s = min(R.choice([2, 2, 3, 3, 4, 5]), n - nxt + 1)
        new = list(range(nxt, nxt + s - 1)); nxt += s - 1
        for a, b in itertools.combinations([v] + new, 2):
            G.add_edge(a, b)
    return G

ok = 0; N = 0
for t in range(150):
    G = random_block_graph(R.randint(4, 15))
    assert all(len(b) == 2 or G.subgraph(b).number_of_edges() == len(b)*(len(b)-1)//2 for b in nx.biconnected_components(G))
    N += 1; ok += chou_ns(G) == pw(G) + 1
report("Chou et al. Thm 4 (block graphs, n 4-15)", ok, N)
ok = 0; N = 0
for t in range(100):  # trees (all blocks K2): Ellis-Sudborough-Turner / Scheffler via Chou
    G = nx.random_labeled_tree(R.randint(5, 16), seed=R.randrange(10**9))
    N += 1; ok += chou_ns(G) == pw(G) + 1
report("Chou Thm 4 on random trees (n 5-16)", ok, N)

# ---- 2. Split graphs: pw = |K|-1 iff some x, y in a maximum clique K (x = y allowed)
#         have every vertex of I = V - K non-adjacent to x or to y; otherwise pw = |K|.
def split_formula(G):
    # a maximum clique whose complement is independent (not every maximum clique has one)
    om = max(len(c) for c in nx.find_cliques(G))
    K = next(set(c) for c in nx.find_cliques(G) if len(c) == om and
             not any(G.has_edge(a, b) for a, b in itertools.combinations(set(G) - set(c), 2)))
    I = set(G) - K
    assert all(not G.has_edge(a, b) for a, b in itertools.combinations(I, 2))
    for x in K:
        for y in K:
            if all(not (G.has_edge(p, x) and G.has_edge(p, y)) for p in I):
                return len(K) - 1
    return len(K)
ok = 0; N = 0; dist = {0: 0, 1: 0}
for t in range(300):
    k = R.randint(2, 9); m = R.randint(1, 10); dens = R.random()
    G = nx.complete_graph(k)
    for p in range(k, k + m):
        G.add_node(p)
        for c in range(k):
            if R.random() < dens: G.add_edge(p, c)
    f = split_formula(G); w = pw(G)
    N += 1; ok += f == w; dist[f - (max(len(c) for c in nx.find_cliques(G)) - 1)] += 1
report(f"split criterion (n 3-19; pw=omega-1 on {dist[0]}, omega on {dist[1]})", ok, N)

# ---- 3. Berge-acyclic matrices (incidence graph a forest) give block MOSP graphs
def is_block(G):
    return all(G.subgraph(b).number_of_edges() == len(b)*(len(b)-1)//2 for b in nx.biconnected_components(G))
ok = 0; N = 0
for t in range(300):
    # random forest on customers + patterns, bipartite by construction
    nc, np_ = R.randint(3, 20), R.randint(2, 12)
    rows = [set() for _ in range(nc)]
    B = nx.Graph(); B.add_nodes_from([("c", i) for i in range(nc)] + [("p", j) for j in range(np_)])
    for _ in range(nc + np_):
        i, j = R.randrange(nc), R.randrange(np_)
        B.add_edge(("c", i), ("p", j))
        if not nx.is_forest(B): B.remove_edge(("c", i), ("p", j))
    for (a, b) in B.edges():
        c, p = (a, b) if a[0] == "c" else (b, a)
        rows[c[1]].add(p[1])
    G = mosp_graph(rows)
    N += 1; ok += is_block(G) and nx.is_chordal(G)
report("Berge-acyclic matrix => block MOSP graph", ok, N)

# ---- 4. C1P: rows consecutive (pattern order) => interval, conformal, MOSP = max column sum
#         columns consecutive (customer order) => proper interval, MOSP = max column sum
ok = 0; N = 0
for t in range(200):
    nc, np_ = R.randint(3, 16), R.randint(3, 16)
    rows = []
    for c in range(nc):
        a = R.randrange(np_); b = min(np_ - 1, a + R.randint(0, 4)); rows.append(set(range(a, b + 1)))
    colsum = max(sum(1 for r in rows if j in r) for j in range(np_))
    G = mosp_graph(rows)
    N += 1; ok += (mosp(rows) == colsum) and nx.is_chordal(G)
report("row-C1P => MOSP = max column sum", ok, N)
ok = 0; N = 0
for t in range(200):
    nc, np_ = R.randint(3, 16), R.randint(2, 14)
    cols = []
    for p in range(np_):
        a = R.randrange(nc); b = min(nc - 1, a + R.randint(0, 5)); cols.append(set(range(a, b + 1)))
    rows = [set(p for p in range(np_) if c in cols[p]) for c in range(nc)]
    colsum = max(len(c) for c in cols)
    N += 1; ok += mosp(rows) == colsum
report("column-C1P => MOSP = max column sum", ok, N)

# ---- 5. Circular-ones rows: MOSP graph is a circular-arc graph (Suchan-Todinca Thm 1).
#         No recognizer; check the cheap consequence pw <= 2*omega - 1 (Bodlaender 1998 Cor 31).
ok = 0; N = 0
for t in range(150):
    nc, np_ = R.randint(4, 16), R.randint(4, 14)
    rows = []
    for c in range(nc):
        a = R.randrange(np_); L = R.randint(1, max(1, np_ // 2)); rows.append({(a + i) % np_ for i in range(L)})
    G = mosp_graph(rows)
    om = max(len(c) for c in nx.find_cliques(G))
    N += 1; ok += pw(G) <= 2 * om - 1
report("circular-ones rows => pw <= 2 omega - 1", ok, N)

# ---- 6. In-forest dags (each vertex <= 1 successor): pebbling matrix M_D (column v = N^-[v])
#         is Berge-acyclic, so D_u is a block graph
ok = 0; N = 0
for t in range(200):
    n = R.randint(3, 25)
    succ = {v: (R.randrange(v + 1, n) if v < n - 1 and R.random() < 0.9 else None) for v in range(n)}
    rows = [set() for _ in range(n)]
    for v in range(n):
        rows[v].add(v)
        if succ[v] is not None: rows[v].add(succ[v])
    G = mosp_graph(rows)
    N += 1; ok += is_block(G)
report("in-forest dag => moral graph D_u is a block graph", ok, N)

# ---- 7. Polygon (cycle, one pattern per edge): MOSP = 3 (Becceneri et al. 2004 p. 2317 say xi = 2)
ok = 0; N = 0
for n in range(3, 15):
    rows = [{i, (i - 1) % n} for i in range(n)]
    N += 1; ok += mosp(rows) == 3
report("polygon C_n, n 3-14: MOSP = 3", ok, N)

# ---- 8. Complement-split (join) rule on random joins of random graphs
ok = 0; N = 0
for t in range(100):
    parts = [nx.gnp_random_graph(R.randint(1, 6), R.random(), seed=R.randrange(10**9)) for _ in range(R.randint(2, 3))]
    G = nx.Graph(); off = 0; sizes = []
    for H in parts:
        G.add_nodes_from(v + off for v in H); G.add_edges_from((a + off, b + off) for a, b in H.edges())
        sizes.append(range(off, off + H.number_of_nodes())); off += H.number_of_nodes()
    for A, Bv in itertools.combinations(sizes, 2):
        G.add_edges_from((a, b) for a in A for b in Bv)
    n = G.number_of_nodes()
    f = min(pw(G.subgraph(S).copy()) + n - len(S) for S in sizes)
    N += 1; ok += f == pw(G)
report("join rule pw = min_i pw(G_i) + n - |V_i|", ok, N)

open("/home/al/dev/MOSP/paper3/poly_checks/checks.out", "w").write("\n".join(out) + "\n")
