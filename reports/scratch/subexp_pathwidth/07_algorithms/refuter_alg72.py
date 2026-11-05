import sys, itertools; sys.path.insert(0, 'reports/scratch/subexp_pathwidth/07_algorithms')
import refuter_check as r
import networkx as nx

def alg72(g):
    """Algorithm 7.2 with my own subset DP as the vs oracle; returns (value, order)."""
    comps = list(nx.connected_components(g))
    single = [c for c in comps if len(c) == 2]
    iso = [v for v in g.nodes() if g.degree(v) == 0]
    keep = [v for v in g.nodes() if g.degree(v) > 0 and not any(v in c for c in single)]
    gp = g.subgraph(keep)
    edges = [tuple(sorted(e)) for e in gp.edges()]
    adj = {v: set(gp[v]) for v in gp.nodes()}
    if edges:
        Ladj = r.line_graph(edges)
        vsL, f, costs, Lverts = r.opt_by_subset_dp(list(Ladj), r.vs_cost(Ladj))
        # a witness L-layout from the DP: reverse argmin walk
        full = (1 << len(Lverts)) - 1; S = full; rev = []
        while S:
            for i in range(len(Lverts)):
                if S >> i & 1 and f[S ^ (1 << i)] <= f[full]:
                    rev.append(Lverts[i]); S ^= 1 << i; break
        Lo = rev[::-1]
        assert r.layout_vs(Ladj, Lo) == vsL
        order = r.vertex_layout_from_line_layout(adj, Lo, 0)
    else:
        vsL = 0; order = []
    for c in single: order += sorted(c)
    order += iso
    return max(vsL, 1 if single else 0), order

bad = 0; checked = 0; capped = 0
for gi, g in enumerate(gg for gg in nx.graph_atlas_g() if gg.number_of_nodes() <= 6):
    edges = [tuple(sorted(e)) for e in g.edges()]
    if max((d for _, d in g.degree()), default=0) > 3: continue
    cw, *_ = r.opt_by_subset_dp(list(g.nodes()), r.cw_cost(edges))
    val, order = alg72(g)
    checked += 1
    if sorted(order) != sorted(g.nodes()) or val != cw or r.layout_cw(edges, order) != cw:
        bad += 1; print('ALG72 BAD', gi, edges, cw, val, order)
print('alg72 checked', checked, 'bad', bad)

# was the 20000 cap hit anywhere in refuter_check's optimal-layout enumeration?
for gi, g in enumerate(gg for gg in nx.graph_atlas_g() if gg.number_of_nodes() <= 6):
    edges = [tuple(sorted(e)) for e in g.edges()]
    if len(edges) < 8: continue
    Ladj = r.line_graph(edges)
    vsL, f, costs, Lverts = r.opt_by_subset_dp(list(Ladj), r.vs_cost(Ladj))
    L = r.all_layouts_with_value_at_most(Lverts, r.vs_cost(Ladj), vsL, cap=20000)
    if len(L) >= 20000: capped += 1
print('graphs with m>=8 where the optimal-layout cap (20000) was hit:', capped)
