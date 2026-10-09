"""Brute-force checks for paper2/complex_members.md (definitions, small graphs).

Run: python paper2/complex_members_check.py {wave|lw|cw3|cut|wein|mcut|mixed N|triple N|brst N|mtsp|truchet}
"""
import sys, itertools, collections, random
sys.path.insert(0, "/home/al/dev/MOSP")
from paper1.complex_check import vs_dp, _layout_dp, popcount, edges_of, graph, cutwidth_dp, mosp_value, row_graph
from networkx.generators.atlas import graph_atlas_g
from paper1.complex_check import from_nx

def linear_width(g):
    """Thomas / Fomin-Thilikos / Kobayashi-Nakahata: min over edge orders of
    max_i |mid(E_i)|, mid(F) = vertices with an edge in F and one outside."""
    n, adj = g
    es = edges_of(g)
    m = len(es)
    if m == 0:
        return 0
    inc = [0] * n
    for i, (u, v) in enumerate(es):
        inc[u] |= 1 << i; inc[v] |= 1 << i
    full = (1 << m) - 1
    def d(F):
        return sum(1 for u in range(n) if inc[u] & F and inc[u] & ~F & full)
    INF = 10**9
    f = [INF] * (1 << m); f[0] = 0
    dval = [d(F) for F in range(1 << m)]
    for s in range(1 << m):
        if f[s] == INF: continue
        rest = full & ~s
        while rest:
            b = rest & -rest; rest ^= b
            t = s | b
            c = max(f[s], dval[t])
            if c < f[t]: f[t] = c
    return f[full]

def max_wavefront(g):
    """Frontal-method wavefront (Kumfert-Pothen form): at step i the wavefront
    is N[V_i] minus V_{i-1}: v_i plus the unplaced neighbours of V_i."""
    n, adj = g
    if n == 0: return 0
    def cost(s, v):
        t = s | (1 << v)
        nb = 0
        for u in range(n):
            if t >> u & 1: nb |= adj[u]
        return 1 + popcount(nb & ~t)
    return _layout_dp(n, cost)

def atlas(maxn=7):
    for h in graph_atlas_g():
        if 0 < h.number_of_nodes() <= maxn:
            yield h

def check_lw():
    tally = collections.Counter(); exc = []
    for h in atlas(7):
        g = from_nx(h)
        if len(edges_of(g)) > 16: continue
        pw = vs_dp(g); lw = linear_width(g)
        tally[lw - pw] += 1
        if not (pw <= lw <= pw + 1): exc.append((h.number_of_nodes(), sorted(h.edges()), pw, lw))
    print("linear width - pw:", dict(tally))
    bad = [e for e in exc if e[3] >= 1]
    print("  exceptions to pw<=lw<=pw+1:", len(exc), "of which lw>=1:", len(bad))
    print("  sample exceptions:", exc[:3])

def check_wavefront():
    tally = collections.Counter()
    for h in atlas(7):
        g = from_nx(h)
        tally[max_wavefront(g) - vs_dp(g)] += 1
    print("max wavefront - pw:", dict(tally))

def check_subcubic_cutwidth():
    tally = collections.Counter(); tally_all = collections.Counter()
    for h in atlas(7):
        g = from_nx(h)
        d = cutwidth_dp(g) - vs_dp(g)
        tally_all[d] += 1
        if max((deg for _, deg in h.degree()), default=0) <= 3:
            tally[d] += 1
    print("cutwidth - pw, max degree <= 3:", dict(sorted(tally.items())))
    print("cutwidth - pw, all graphs <= 7 vertices:", dict(sorted(tally_all.items())))

def cut_mosp(matrix):
    """Open stacks counted between consecutive patterns (hypergraph cutwidth
    with patterns as vertices, customers as hyperedges)."""
    m = len(matrix[0]); best = None
    for perm in itertools.permutations(range(m)):
        spans = []
        for row in matrix:
            pos = [i for i, c in enumerate(perm) if row[c]]
            if pos: spans.append((pos[0], pos[-1]))
        z = max((sum(1 for a, b in spans if a <= j < b) for j in range(m - 1)), default=0)
        best = z if best is None else min(best, z)
    return best

def check_cut_mosp():
    # star: one shared pattern + one private pattern per customer
    for k in range(2, 7):
        M = [[1] + [1 if j == i else 0 for j in range(k)] for i in range(k)]
        print(f"  star k={k}: MOSP {mosp_value(M)}  cut-MOSP {cut_mosp(M)}")
    rnd = random.Random(1); tally = collections.Counter()
    for _ in range(400):
        n, m = rnd.randint(2, 6), rnd.randint(2, 6)
        M = [[1 if rnd.random() < 0.45 else 0 for _ in range(m)] for _ in range(n)]
        M = [r for r in M if sum(r) >= 2]
        if not M: continue
        tally[mosp_value(M) - cut_mosp(M)] += 1
    print("  MOSP - cut-MOSP, random (customers with >=2 patterns):", dict(sorted(tally.items())))

def pinned_density(matrix, l, r):
    m = len(matrix[0]); inner = [c for c in range(m) if c not in (l, r)]
    best = None
    for p in itertools.permutations(inner):
        perm = (l, *p, r); spans = []
        for row in matrix:
            pos = [i for i, c in enumerate(perm) if row[c]]
            if pos: spans.append((pos[0], pos[-1]))
        z = max(sum(1 for a, b in spans if a <= j <= b) for j in range(m))
        best = z if best is None else min(best, z)
    return best

def check_weinberger(seconds=150, seed=7):
    import time
    rnd = random.Random(seed); t0 = time.time(); tally = collections.Counter(); worst = None; cnt = 0
    while time.time() - t0 < seconds:
        n = rnd.randint(3, 8); inner = rnd.randint(3, 7); m = inner + 2
        p = rnd.choice([0.3, 0.4, 0.5])
        M = [[1 if rnd.random() < p else 0 for _ in range(m)] for _ in range(n)]
        M = [r for r in M if sum(r) >= 1]
        if not M or not any(r[0] for r in M) or not any(r[m-1] for r in M): continue
        free = mosp_value(M); pin = pinned_density(M, 0, m - 1)
        tally[pin - free] += 1; cnt += 1
        if worst is None or pin - free > worst[0]: worst = (pin - free, M)
    print(f"  Weinberger pinned - free over {cnt} random instances:", dict(sorted(tally.items())))
    print("  worst:", worst)

if __name__ == "__main__":
    what = sys.argv[1]
    {"lw": check_lw, "wave": check_wavefront, "cw3": check_subcubic_cutwidth,
     "cut": check_cut_mosp, "wein": check_weinberger, "mcut": lambda: None, "mixed": lambda: None, "triple": lambda: None, "brst": lambda: None, "mtsp": lambda: None, "truchet": lambda: None}[what]()

def padded_mcut_matrix(g):
    """Linhares 2001 Prop. 2.1 / Lemma 2.2: rows = edges (two 1s at the
    endpoint columns), plus single-1 padding rows so every column sums to
    C = max degree."""
    n, adj = g
    es = edges_of(g)
    C = max(popcount(a) for a in adj)
    M = [[1 if j in e else 0 for j in range(n)] for e in es]
    for j in range(n):
        for _ in range(C - popcount(adj[j])):
            M.append([1 if jj == j else 0 for jj in range(n)])
    return M, C

def check_mcut():
    from paper1.complex_check import modified_cutwidth_dp
    tally = collections.Counter(); bad = 0; cnt = 0
    for h in atlas(7):
        g = from_nx(h)
        if not edges_of(g): continue
        M, C = padded_mcut_matrix(g)
        if len(M) > 15: continue
        mcw = modified_cutwidth_dp(g)
        H = row_graph(M)
        z = vs_dp(H) + 1
        cnt += 1
        if z != mcw + C: bad += 1
        tally[mcw - vs_dp(g)] += 1
    print(f"  Linhares Lemma 2.2: pw(H_G)+1 == mcw(G)+Delta(G) on {cnt - bad}/{cnt} graphs with an edge")
    print("  mcw - pw on the same graph:", dict(sorted(tally.items())))

if __name__ == "__main__" and sys.argv[1] == "mcut":
    check_mcut()

from paper1.complex_check import _edge_masks, _recontaminate, edge_search

def mixed_search(g, kmax=None):
    """Mixed search (Takahashi, Ueno, Kajitani; Bodlaender 1998 p. 28): the
    edge-search moves (place, remove, slide), and an edge is also cleared
    when both its endpoints carry a searcher. Full game (recontamination
    allowed in the state space)."""
    n, adj = g
    es, inc = _edge_masks(g)
    if not es:
        return 0
    allc = (1 << len(es)) - 1
    eidx = {}
    for i, (u, v) in enumerate(es):
        eidx[(u, v)] = eidx[(v, u)] = i
    kmax = kmax or len(es) + 1
    for k in range(1, kmax + 1):
        start = ((0,) * n, allc); seen = {start}; stack = [start]; found = False
        while stack and not found:
            cnt, c = stack.pop(); total = sum(cnt); succ = []
            for v in range(n):
                if total < k:
                    t = list(cnt); t[v] += 1; succ.append((tuple(t), None))
                if cnt[v]:
                    t = list(cnt); t[v] -= 1; succ.append((tuple(t), None))
                    x = adj[v]
                    while x:
                        w = (x & -x).bit_length() - 1; x &= x - 1
                        t = list(cnt); t[v] -= 1; t[w] += 1
                        succ.append((tuple(t), eidx[(v, w)]))
            for t, e in succ:
                guarded = 0
                for v in range(n):
                    if t[v]: guarded |= 1 << v
                c1 = c if e is None else c & ~(1 << e)
                for i, (u, v) in enumerate(es):
                    if guarded >> u & 1 and guarded >> v & 1:
                        c1 &= ~(1 << i)
                c2 = _recontaminate(n, inc, guarded, c1)
                if c2 == 0:
                    found = True; break
                s = (t, c2)
                if s not in seen:
                    seen.add(s); stack.append(s)
        if found:
            return k
    return None

def triple_subdivided(g):
    """KP 1986 Thm 2.3's G_e (each edge tripled), with two of the three
    parallel copies subdivided once to keep the graph simple (subdivision
    does not change the edge-search number, KP p. 209)."""
    n, adj = g
    es = edges_of(g); new = []; nxt = n
    for u, v in es:
        new.append((u, v))
        for _ in range(2):
            new += [(u, nxt), (nxt, v)]; nxt += 1
    return graph(nxt, new)

def check_mixed(maxn=6):
    tally = collections.Counter()
    for h in atlas(maxn):
        g = from_nx(h)
        if not edges_of(g): continue
        tally[mixed_search(g) - vs_dp(g)] += 1
    print(f"  mixed search - pw, graphs with an edge on <= {maxn} vertices:", dict(sorted(tally.items())))

def check_triple(maxn=4):
    import time
    tally = collections.Counter()
    for h in atlas(maxn):
        g = from_nx(h)
        if not edges_of(g): continue
        t0 = time.time()
        es3 = edge_search(triple_subdivided(g), monotone=True)
        tally[es3 - vs_dp(g)] += 1
    print(f"  progressive edge search of tripled graph - pw, <= {maxn} vertices:", dict(sorted(tally.items())))

if __name__ == "__main__" and sys.argv[1] == "mixed":
    check_mixed(int(sys.argv[2]))
if __name__ == "__main__" and sys.argv[1] == "triple":
    check_triple(int(sys.argv[2]))

def brst_search(g):
    """Bienstock-Robertson-Seymour-Thomas 1991 sec. 5, p. 282: a search is
    X_1 = {}, ..., X_m with X_{i+1} a subset or superset of X_i; B_1 = V and
    B_i = vertices joined to B_{i-1} by a path avoiding X_i; successful if
    B_m is empty. Value: least n with a successful search, all |X_i| <= n."""
    n, adj = g
    full = (1 << n) - 1
    if n == 0: return 0
    def closure(B, X):
        # vertices reachable from B \ X avoiding X
        R = B & ~X; frontier = R
        while frontier:
            v = (frontier & -frontier).bit_length() - 1; frontier &= frontier - 1
            nb = adj[v] & ~X & ~R
            R |= nb; frontier |= nb
        return R
    subsets = list(range(1 << n))
    for k in range(0, n + 1):
        start = (0, full); seen = {start}; stack = [start]
        while stack:
            X, B = stack.pop()
            if B == 0: return k
            for Y in subsets:
                if popcount(Y) > k: continue
                if not (Y & X == Y or Y & X == X): continue
                s = (Y, closure(B, Y))
                if s[1] == 0: return k
                if s not in seen: seen.add(s); stack.append(s)
    return None

def check_brst(maxn=6):
    tally = collections.Counter()
    for h in atlas(maxn):
        g = from_nx(h)
        tally[brst_search(g) - vs_dp(g)] += 1
    print(f"  BRST vertex-fugitive search - pw, all graphs on 1..{maxn} vertices:", dict(tally))

def mtsp_switches(M, perm, C):
    """Tool switches of a fixed job sequence under KTNS (Tang & Denardo 1988):
    rows = tools, columns = jobs; insertions beyond the first C count."""
    jobs = [{t for t in range(len(M)) if M[t][j]} for j in perm]
    if any(len(s) > C for s in jobs): return None
    mag = set(); ins = 0
    for i, need in enumerate(jobs):
        for t in need - mag:
            if len(mag) >= C:
                def nxt(u):
                    for k in range(i, len(jobs)):
                        if u in jobs[k]: return k
                    return 10**9
                cand = [u for u in mag if u not in need]
                u = max(cand, key=nxt); mag.remove(u)
            mag.add(t); ins += 1
    return max(0, ins - C)

def check_mtsp(trials=300, seed=5):
    rnd = random.Random(seed); ok = 0; cnt = 0
    for _ in range(trials):
        n, m = rnd.randint(3, 7), rnd.randint(3, 6)
        M = [[1 if rnd.random() < 0.4 else 0 for _ in range(m)] for _ in range(n)]
        M = [r for r in M if any(r)]
        if not M: continue
        T = len(M); z = mosp_value(M)
        cmax = max(sum(M[t][j] for t in range(T)) for j in range(m))
        thr = None
        for C in range(cmax, T + 1):
            best = min(s for p in itertools.permutations(range(m)) if (s := mtsp_switches(M, p, C)) is not None)
            if best == T - C: thr = C; break
        cnt += 1; ok += (thr == z)
    print(f"  least C with MTSP_C = M - C equals MOSP on {ok}/{cnt} random instances")

if __name__ == "__main__" and sys.argv[1] == "brst":
    check_brst(int(sys.argv[2]))
if __name__ == "__main__" and sys.argv[1] == "mtsp":
    check_mtsp()

def check_truchet(trials=3000, seed=3):
    """Truchet, Bourdon & Codognet (CSP Challenge 2005): maximise g, the number
    of customer pairs whose product intervals are disjoint. Is some
    g-maximising order always MOSP-optimal? Random instances, then the vertex-
    edge incidence instances of all atlas graphs with 3..8 edges."""
    from networkx.generators.atlas import graph_atlas_g
    def evals(M):
        m = len(M[0]); res = []
        for perm in itertools.permutations(range(m)):
            sp = []
            for row in M:
                pos = [i for i, c in enumerate(perm) if row[c]]
                if pos: sp.append((pos[0], pos[-1]))
            z = max(sum(1 for a, b in sp if a <= j <= b) for j in range(m))
            gg = sum(1 for (a, b), (c, d) in itertools.combinations(sp, 2) if b < c or d < a)
            res.append((z, gg))
        return res
    def bad(M):
        res = evals(M); zopt = min(z for z, _ in res); gmax = max(gg for _, gg in res)
        return min(z for z, gg in res if gg == gmax) > zopt
    rnd = random.Random(seed); t = f = 0
    for _ in range(trials):
        n, m = rnd.randint(4, 8), rnd.randint(4, 7)
        M = [[1 if rnd.random() < 0.4 else 0 for _ in range(m)] for _ in range(n)]
        M = [r for r in M if any(r)]
        if len(M) < 2: continue
        t += 1; f += bad(M)
    t2 = f2 = 0
    for h in graph_atlas_g():
        if not 3 <= h.number_of_edges() <= 8: continue
        es = list(h.edges())
        M = [[1 if v in e else 0 for e in es] for v in h.nodes() if h.degree(v) > 0]
        t2 += 1; f2 += bad(M)
    print(f"  no g-maximiser MOSP-optimal: {f}/{t} random, {f2}/{t2} graph incidence instances")

if __name__ == "__main__" and sys.argv[1] == "truchet":
    check_truchet()
