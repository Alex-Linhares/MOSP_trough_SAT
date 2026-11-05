"""Refuter brute force for Theorem 7.1 / Algorithm 7.2 (written from scratch; imports nothing from the repo)."""
import itertools, random, sys, time
from collections import defaultdict
import networkx as nx

random.seed(7)

def layout_vs(adj, order):
    """adj: dict v -> set. vs of a layout = max over gaps of placed vertices with an unplaced neighbour."""
    placed = set(); best = 0
    for v in order:
        placed.add(v)
        c = sum(1 for x in placed if adj[x] - placed)
        best = max(best, c)
    return best

def layout_cw(edges, order):
    placed = set(); best = 0
    for v in order:
        placed.add(v)
        c = sum(1 for (a, b) in edges if (a in placed) != (b in placed))
        best = max(best, c)
    return best

def opt_by_subset_dp(verts, cost):
    """min over orderings of max over proper prefix-sets of cost(S); cost depends on the set only."""
    verts = list(verts); n = len(verts); idx = {v: i for i, v in enumerate(verts)}
    INF = 10**9
    f = [INF] * (1 << n); f[0] = 0
    costs = [0] * (1 << n)
    for S in range(1, 1 << n):
        costs[S] = cost({verts[i] for i in range(n) if S >> i & 1})
    for S in range(1, 1 << n):
        best = INF
        for i in range(n):
            if S >> i & 1:
                best = min(best, f[S ^ (1 << i)])
        f[S] = max(best, costs[S])
    return f[(1 << n) - 1], f, costs, verts

def vs_cost(adj):
    return lambda S: sum(1 for x in S if adj[x] - S)

def cw_cost(edges):
    return lambda S: sum(1 for (a, b) in edges if (a in S) != (b in S))

def line_graph(edges):
    E = [tuple(sorted(e)) for e in edges]
    Ladj = {e: set() for e in E}
    for e, f in itertools.combinations(E, 2):
        if set(e) & set(f):
            Ladj[e].add(f); Ladj[f].add(e)
    return Ladj

def vertex_layout_from_line_layout(G_adj, L_order, label):
    """Proof (i): vertices by completion; a double step uw split by the rule
    'add u first if u has a neighbour in P or w has a neighbour outside P∪{u,w}; otherwise add w first'.
    label: 0 -> u = e[0], w = e[1]; 1 -> swapped."""
    last = {}
    for q, e in enumerate(L_order):
        for v in e: last[v] = q
    order = []; P = set()
    for q, e in enumerate(L_order):
        done = [v for v in e if last[v] == q]
        if len(done) == 1:
            order.append(done[0]); P.add(done[0])
        elif len(done) == 2:
            u, w = (done[0], done[1]) if label == 0 else (done[1], done[0])
            a_u = len(G_adj[u] & P)
            b_w = len(G_adj[w] - P - {u, w})
            first, second = (u, w) if (a_u >= 1 or b_w >= 1) else (w, u)
            order += [first, second]; P |= {u, w}
    for v in G_adj:
        if v not in P: order.append(v)   # isolated vertices last
    return order

def line_layout_from_vertex_layout(edges, V_order):
    pos = {v: i for i, v in enumerate(V_order)}
    return sorted((tuple(sorted(e)) for e in edges), key=lambda e: (min(pos[e[0]], pos[e[1]]), max(pos[e[0]], pos[e[1]])))

def all_layouts_with_value_at_most(verts, cost, k, cap):
    """DFS enumeration of every ordering whose every prefix set has cost <= k (i.e. exactly the layouts of value <= k)."""
    out = []; n = len(verts)
    def rec(prefix, S):
        if len(out) >= cap: return
        if len(prefix) == n:
            out.append(tuple(prefix)); return
        for v in verts:
            if v not in S:
                S2 = S | {v}
                if cost(S2) <= k:
                    rec(prefix + [v], S2)
    rec([], frozenset())
    return out

def main(max_n=6):
    t0 = time.time()
    graphs = [g for g in nx.graph_atlas_g() if g.number_of_nodes() <= max_n]
    stats = defaultdict(int)
    wrong = []
    for gi, g in enumerate(graphs):
        n = g.number_of_nodes(); edges = [tuple(sorted(e)) for e in g.edges()]; m = len(edges)
        adj = {v: set(g[v]) for v in g.nodes()}
        Delta = max((len(adj[v]) for v in adj), default=0)
        single_edge_comp = any(len(c) == 2 for c in nx.connected_components(g))
        stats['graphs'] += 1
        # exact values
        cw, fcw, _, _ = opt_by_subset_dp(list(g.nodes()), cw_cost(edges))
        Ladj = line_graph(edges)
        if m:
            vsL, fvs, vcost, Lverts = opt_by_subset_dp(list(Ladj), vs_cost(Ladj))
        else:
            vsL = 0
        # (i)
        if not single_edge_comp and not cw <= vsL:
            wrong.append(('(i)', gi, edges, cw, vsL))
        if m and not cw <= max(1, vsL):
            wrong.append(('general', gi, edges, cw, vsL))
        # (ii)
        excess = max(0, Delta // 2 - 1)
        if not vsL <= cw + excess:
            wrong.append(('(ii)', gi, edges, cw, vsL, Delta))
        if Delta <= 3 and not single_edge_comp and cw != vsL:
            wrong.append(('eq', gi, edges, cw, vsL))
        if single_edge_comp: stats['graphs_with_single_edge_comp'] += 1
        if Delta <= 3 and not single_edge_comp: stats['graphs_subcubic_no_single_edge'] += 1
        # star check
        if m and nx.is_isomorphic(g, nx.star_graph(m)) and m >= 2:
            if not (cw == (m + 1) // 2 and vsL == m - 1):
                wrong.append(('star', gi, cw, vsL))
            stats['stars'] += 1

        # ---- map (i): every L-layout when m <= 7; every optimal L-layout (cap) otherwise; plus random ----
        if m >= 1:
            if m <= 7:
                L_layouts = list(itertools.permutations(Lverts)); tag = 'all'
            else:
                L_layouts = all_layouts_with_value_at_most(Lverts, vs_cost(Ladj), vsL, cap=20000); tag = 'opt'
                for _ in range(300):
                    p = list(Lverts); random.shuffle(p); L_layouts.append(tuple(p))
            for Lo in L_layouts:
                k = layout_vs(Ladj, Lo)
                stats['L_layouts_' + tag] += 1
                for label in (0, 1):
                    order = vertex_layout_from_line_layout(adj, Lo, label)
                    assert sorted(order) == sorted(adj) and len(order) == n
                    c = layout_cw(edges, order)
                    if single_edge_comp:
                        if not c <= max(1, k):
                            wrong.append(('map_i_single', gi, edges, Lo, label, order, c, k))
                    elif not c <= k:
                        wrong.append(('map_i', gi, edges, Lo, label, order, c, k))
                    stats['map_i_checks'] += 1
            # also: is the map's layout optimal when the L-layout is optimal (Alg 7.2 witness)?
            if Delta <= 3 and not single_edge_comp:
                opt_layouts = [Lo for Lo in L_layouts if layout_vs(Ladj, Lo) == vsL]
                for Lo in opt_layouts:
                    for label in (0, 1):
                        order = vertex_layout_from_line_layout(adj, Lo, label)
                        if layout_cw(edges, order) != cw:
                            wrong.append(('witness', gi, edges, Lo, label, order))
                stats['opt_L_layouts_subcubic'] += len(opt_layouts)

        # ---- map (ii): every vertex layout ----
        for Vo in itertools.permutations(g.nodes()):
            kcw = layout_cw(edges, Vo)
            if m == 0: continue
            Lo = line_layout_from_vertex_layout(edges, Vo)
            v = layout_vs(Ladj, Lo)
            stats['map_ii_checks'] += 1
            if not v <= kcw + excess:
                wrong.append(('map_ii', gi, edges, Vo, Lo, v, kcw, Delta))
            if kcw == cw: stats['map_ii_opt_layouts'] += 1
    print('time', round(time.time() - t0, 1))
    for k_, v_ in sorted(stats.items()): print(k_, v_)
    print('WRONG', len(wrong))
    for w in wrong[:20]: print(w)
    return wrong

if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 6)
