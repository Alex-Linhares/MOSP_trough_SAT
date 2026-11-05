import sys; sys.path.insert(0, 'reports/scratch/subexp_pathwidth/07_algorithms')
import refuter_check as r
import networkx as nx
CAP = 3_000_000
tot = 0; capped = []; bad = 0; graphs = 0
for gi, g in enumerate(gg for gg in nx.graph_atlas_g() if gg.number_of_nodes() <= 6):
    edges = [tuple(sorted(e)) for e in g.edges()]
    if len(edges) < 8: continue
    if any(len(c) == 2 for c in nx.connected_components(g)): continue
    adj = {v: set(g[v]) for v in g.nodes()}
    Ladj = r.line_graph(edges)
    vsL, f, costs, Lverts = r.opt_by_subset_dp(list(Ladj), r.vs_cost(Ladj))
    L = r.all_layouts_with_value_at_most(Lverts, r.vs_cost(Ladj), vsL, cap=CAP)
    graphs += 1; tot += len(L)
    if len(L) >= CAP: capped.append((gi, len(edges), vsL))
    for Lo in L:
        for label in (0, 1):
            order = r.vertex_layout_from_line_layout(adj, Lo, label)
            if r.layout_cw(edges, order) > vsL:
                bad += 1; print('BAD', gi, edges, Lo, label, order)
print('graphs(m>=8, no single edge)', graphs, 'optimal L-layouts checked', tot, 'bad', bad)
print('capped at', CAP, ':', capped)
