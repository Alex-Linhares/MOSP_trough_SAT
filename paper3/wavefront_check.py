"""Brute-force check: maximum wavefront (Kumfert & Pothen 1997) = pathwidth + 1.

Definition checked is Kumfert & Pothen, ICASE Report 97-33, Section 2.1, p. 4,
in its *matrix* form, not the graph paraphrase: A is symmetric with every
diagonal entry nonzero; under an ordering, equation (row) k is *active* at step
i if k >= i and some column l <= i has a_kl != 0; wf_i(A) is the set of active
equations; maxwf(A) = max_{1<=i<=n} |wf_i(A)|.  The minimum over symmetric
permutations PAP^T is compared with pathwidth computed two independent ways.

Run (one core):
    python paper3/wavefront_check.py figure1   # reproduce K&P Figure 1(c)
    python paper3/wavefront_check.py atlas     # every graph on 1..7 vertices, every ordering
    python paper3/wavefront_check.py random N  # N random graphs, 8..16 vertices, vs pathwidth_solver
    python paper3/wavefront_check.py orders N  # per-order identity on N random graphs, 20..80 vertices
"""
import itertools, random, sys, collections
sys.path.insert(0, "/home/al/dev/MOSP/pathwidth_solver")
import networkx as nx
from networkx.generators.atlas import graph_atlas_g


# ---------- the matrix definition, verbatim -------------------------------------------------

def pattern(G, nodes):
    """Nonzero pattern of a symmetric matrix with adjacency graph G and nonzero diagonal."""
    idx = {v: i for i, v in enumerate(nodes)}
    n = len(nodes)
    A = [[i == j for j in range(n)] for i in range(n)]
    for u, v in G.edges():
        A[idx[u]][idx[v]] = A[idx[v]][idx[u]] = True
    return A


def permute(A, order):
    """A' = P A P^T: row/column i of A' is row/column order[i] of A (0-based)."""
    return [[A[a][b] for b in order] for a in order]


def wavefronts(Ap):
    """|wf_i(A')| for i = 1..n (returned 0-based): rows k >= i with a nonzero in a column l <= i."""
    n = len(Ap)
    return [sum(1 for k in range(i, n) if any(Ap[k][l] for l in range(i + 1))) for i in range(n)]


def row_widths(Ap):
    """rw_i = i - f_i, f_i = first nonzero column of row i (lower triangle, diagonal included)."""
    return [i - next(j for j in range(i + 1) if Ap[i][j]) for i in range(len(Ap))]


# ---------- vertex separation, textbook (Kinnersley 1992 p. 346) ----------------------------

def masks_of(G, nodes):
    idx = {v: i for i, v in enumerate(nodes)}
    m = [0] * len(nodes)
    for u, v in G.edges():
        m[idx[u]] |= 1 << idx[v]; m[idx[v]] |= 1 << idx[u]
    return m


def vs_textbook(masks, order):
    """max over 1 <= i < n of |{u : L(u) <= i, u has a neighbour v with L(v) > i}|."""
    n = len(order); best = 0; pre = 0
    for i in range(n - 1):
        pre |= 1 << order[i]
        suf = ((1 << n) - 1) & ~pre
        c = sum(1 for u in order[:i + 1] if masks[u] & suf)
        best = max(best, c)
    return best


def maxwf_graph(masks, order):
    """Graph form, K&P p. 4: wf_i = {v_i} U adj({v_1..v_i}); adj(X) = (U adj(v)) minus X."""
    pre = nb = 0; best = 0
    for v in order:
        pre |= 1 << v; nb |= masks[v]
        best = max(best, 1 + bin(nb & ~pre).count("1"))
    return best


def min_maxwf_dp(masks):
    """min over orderings of maxwf, by subset DP over placed sets (independent of any vs code)."""
    n = len(masks)
    if n == 0:
        return 0
    INF = 10 ** 9
    f = [INF] * (1 << n); f[0] = 0
    nbr = [0] * (1 << n)
    for S in range(1, 1 << n):
        low = (S & -S).bit_length() - 1
        nbr[S] = nbr[S & (S - 1)] | masks[low]
    for S in range(1 << n):
        if f[S] == INF:
            continue
        for v in range(n):
            if S >> v & 1:
                continue
            T = S | (1 << v)
            c = max(f[S], 1 + bin(nbr[T] & ~T).count("1"))
            if c < f[T]:
                f[T] = c
    return f[(1 << n) - 1]


def pw_solver(G):
    from pathwidth import compute_pathwidth
    if G.number_of_nodes() == 0:
        return None
    w, _ = compute_pathwidth(G)
    return w


# ---------- checks --------------------------------------------------------------------------

def figure1():
    """K&P Figure 1: 4x4 grid numbered along anti-diagonals reproduces f_i, rw_i, wf_i."""
    G = nx.grid_2d_graph(4, 4)
    order = sorted(G.nodes(), key=lambda p: (p[0] + p[1], p[0]))
    A = pattern(G, order)
    wf = wavefronts(A); rw = row_widths(A)
    f = [i + 1 - r for i, r in enumerate(rw)]
    print("f_i  ", f)
    print("rw_i ", rw, "sum", sum(rw))
    print("wf_i ", wf, "sum", sum(wf))
    print("Esize", sum(rw), "bw", max(rw), "maxwf", max(wf), "mswf", sum(x * x for x in wf) / 16)
    assert f == [1, 1, 1, 2, 2, 3, 4, 4, 5, 6, 7, 8, 9, 11, 12, 14]
    assert wf == [3, 4, 4, 5, 5, 5, 5, 5, 5, 4, 4, 4, 3, 3, 2, 1]
    assert sum(rw) == 46 and max(rw) == 4 and max(wf) == 5 and sum(wf) == 16 + 46
    print("Figure 1(c) reproduced: E_size = 46, bw = 4, maxwf = 5, mswf = 16.375, sum wf = n + E_size")


def atlas(maxn=7):
    tally = collections.Counter(); per_order = 0; graphs = 0; ident = 0
    for H in graph_atlas_g():
        n = H.number_of_nodes()
        if n == 0 or n > maxn:
            continue
        graphs += 1
        nodes = list(H.nodes()); A = pattern(H, nodes); masks = masks_of(H, nodes)
        best_wf = best_vs = 10 ** 9
        for order in itertools.permutations(range(n)):
            wf = wavefronts(permute(A, order)); mw = max(wf)
            vs_rev = vs_textbook(masks, list(reversed(order)))
            assert mw == 1 + vs_rev, (sorted(H.edges()), order)             # per-order identity
            assert mw == maxwf_graph(masks, order)                          # matrix form = graph form
            assert sum(wf) == n + sum(row_widths(permute(A, order)))        # K&P identity, p. 4
            per_order += 1
            best_wf = min(best_wf, mw); best_vs = min(best_vs, vs_textbook(masks, list(order)))
        pw = pw_solver(H)
        assert best_vs == pw, (sorted(H.edges()), best_vs, pw)
        tally[best_wf - pw] += 1
        if best_wf == min_maxwf_dp(masks):
            ident += 1
    print(f"atlas 1..{maxn}: {graphs} graphs, {per_order} (graph, ordering) pairs;")
    print("  per ordering: maxwf = 1 + vs(reversed ordering) on all of them; matrix form = graph form;"
          " sum wf_i = n + E_size on all of them")
    print("  min maxwf - pw:", dict(tally), f"; DP agrees with exhaustive min on {ident}/{graphs}")


def random_graphs(N, seed=1):
    rng = random.Random(seed); tally = collections.Counter(); sizes = collections.Counter()
    for t in range(N):
        n = rng.randint(8, 16); p = rng.choice([0.1, 0.2, 0.3, 0.5, 0.7])
        G = nx.gnp_random_graph(n, p, seed=rng.randrange(10 ** 9))
        nodes = list(G.nodes()); masks = masks_of(G, nodes)
        tally[min_maxwf_dp(masks) - pw_solver(G)] += 1; sizes[n] += 1
    print(f"random G(n,p), n in 8..16: {N} graphs; min maxwf (subset DP) - pw (pathwidth_solver):",
          dict(tally))


def orders(N, seed=2):
    from pathwidth.graph import vertex_separation_masks
    rng = random.Random(seed); checked = 0; solved = collections.Counter()
    for t in range(N):
        n = rng.randint(20, 80); p = rng.choice([0.03, 0.06, 0.1, 0.2])
        G = nx.gnp_random_graph(n, p, seed=rng.randrange(10 ** 9))
        nodes = list(G.nodes()); A = pattern(G, nodes); masks = masks_of(G, nodes)
        for _ in range(5):
            order = list(range(n)); rng.shuffle(order)
            mw = max(wavefronts(permute(A, order)))
            assert mw == 1 + vs_textbook(masks, order[::-1])
            # pathwidth_solver's closing-order convention needs no reversal
            selfmask = [m | (1 << i) for i, m in enumerate(masks)]
            assert mw == 1 + vertex_separation_masks(selfmask, order)
            checked += 1
        if n <= 40:  # optimum: solver's optimal order is a wavefront order of width pw + 1
            from pathwidth import solve
            sol = solve(G, time_budget=20)
            if sol.proved:
                idx = {v: i for i, v in enumerate(nodes)}
                o = [idx[v] for v in sol.order]
                solved[max(wavefronts(permute(A, o))) - sol.width] += 1
    print(f"per-order identity on {checked} random orderings of {N} graphs, n in 20..80: all hold;"
          f" solver-optimal orders, maxwf - pw: {dict(solved)}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "atlas"
    arg = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    {"figure1": figure1, "atlas": atlas,
     "random": lambda: random_graphs(arg), "orders": lambda: orders(arg)}[cmd]()
