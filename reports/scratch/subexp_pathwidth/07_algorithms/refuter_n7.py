import sys; sys.path.insert(0, 'reports/scratch/subexp_pathwidth/07_algorithms')
import refuter_check as r
import networkx as nx
bad = 0; n = 0; skipped = 0
for g in nx.graph_atlas_g():
    if g.number_of_nodes() != 7: continue
    edges = [tuple(sorted(e)) for e in g.edges()]; m = len(edges)
    if m > 16: skipped += 1; continue
    adj = {v: set(g[v]) for v in g.nodes()}
    Delta = max(d for _, d in g.degree())
    single = any(len(c) == 2 for c in nx.connected_components(g))
    cw, *_ = r.opt_by_subset_dp(list(g.nodes()), r.cw_cost(edges))
    vsL = r.opt_by_subset_dp(list(r.line_graph(edges)), r.vs_cost(r.line_graph(edges)))[0] if m else 0
    n += 1
    ok = (single or cw <= vsL) and vsL <= cw + max(0, Delta // 2 - 1) and (m == 0 or cw <= max(1, vsL)) and (Delta > 3 or single or cw == vsL)
    if not ok: bad += 1; print('BAD', edges, cw, vsL, Delta, single)
print('n=7 graphs checked (m<=16)', n, 'skipped(m>16)', skipped, 'bad', bad)
