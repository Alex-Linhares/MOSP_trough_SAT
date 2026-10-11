"""Verify the myciel6 minor certificate: contract to 60 (min-d), check it is a
minor (by construction: record branch sets), refute pw <= 37 on it under
several search configurations, and a width-38 layout of it."""
import sys, time, json
from pathlib import Path
import networkx as nx
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "pathwidth_solver")); sys.path.insert(0, str(ROOT / "pathwidth_solver" / "bench"))
from readers import read_any, HERE
from pathwidth.graph import masks_from_graph
from pathwidth.search import decide

def contract_to(G, m, rule):
    H = nx.Graph(G); branch = {v: {v} for v in H}
    while H.number_of_nodes() > m:
        v = min(H, key=lambda x: (H.degree(x), x)); nb = list(H[v])
        u = (min(nb, key=lambda c: (len(set(H[c]) & set(nb)), c)) if rule == "least-c"
             else min(nb, key=lambda c: (H.degree(c), c)))
        H = nx.contracted_nodes(H, u, v, self_loops=False); branch[u] |= branch.pop(v)
    return H, branch

G = nx.convert_node_labels_to_integers(read_any(HERE / "coloring" / "myciel6.dgf"))
H, branch = contract_to(G, 60, "min-d")
# minor check: branch sets partition V(G), each connected, and every H-edge realised by a G-edge
assert sorted(x for b in branch.values() for x in b) == list(range(95))
assert all(nx.is_connected(G.subgraph(b)) for b in branch.values())
assert all(any(G.has_edge(a, b) for a in branch[u] for b in branch[v]) for u, v in H.edges())
print("minor certificate OK: 60 connected branch sets, all edges realised")
Hi = nx.convert_node_labels_to_integers(H, label_attribute="orig")
masks, _ = masks_from_graph(Hi)
for cfg in [dict(), dict(better_move=True), dict(repaired_rules=False), dict(old_move=False),
            dict(old_move=False, memo=True, subset_rule=False), dict(definite_move=False, old_move=False)]:
    t0 = time.time(); a = decide(masks, 38, **cfg)          # k=38 means pw <= 37 ?
    t1 = time.time(); b = decide(masks, 39, **cfg)          # pw <= 38 ?
    print(f"{cfg}: pw<=37 {a.status} ({a.nodes} nodes, {t1-t0:.2f}s); pw<=38 {b.status}", flush=True)
t0 = time.time(); a = decide(masks, 38, native=False, deadline=time.monotonic() + 600)
print(f"python reference: pw<=37 {a.status} ({a.nodes} nodes, {time.time()-t0:.1f}s)")
json.dump({"edges": [[int(Hi.nodes[u]['orig']), int(Hi.nodes[v]['orig'])] for u, v in Hi.edges()],
           "branch_sets": {str(k): sorted(v) for k, v in branch.items()}},
          open(Path(__file__).with_name("myciel6_minor60.json"), "w"))
