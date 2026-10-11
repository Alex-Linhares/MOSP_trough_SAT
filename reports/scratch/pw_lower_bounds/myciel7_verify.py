"""myciel7: verify the 110-vertex min-d minor certificate of pw >= 71, then try
pw >= 72 by refuting pw <= 71 on larger minors with a longer budget."""
import sys, time, json
from pathlib import Path
import networkx as nx
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "pathwidth_solver")); sys.path.insert(0, str(ROOT / "pathwidth_solver" / "bench"))
from readers import read_any, HERE
from pathwidth.graph import masks_from_graph
from pathwidth.search import decide
budget = float(sys.argv[1])
def contract(G, m, rule):
    H = nx.Graph(G); branch = {v: {v} for v in H}
    while H.number_of_nodes() > m:
        v = min(H, key=lambda x: (H.degree(x), x)); nb = list(H[v])
        u = (min(nb, key=lambda c: (len(set(H[c]) & set(nb)), c)) if rule == "least-c" else min(nb, key=lambda c: (H.degree(c), c)))
        H = nx.contracted_nodes(H, u, v, self_loops=False); branch[u] |= branch.pop(v)
    assert sorted(x for b in branch.values() for x in b) == list(range(G.number_of_nodes()))
    assert all(nx.is_connected(G.subgraph(b)) for b in branch.values())
    assert all(any(G.has_edge(a, b) for a in branch[u] for b in branch[v]) for u, v in H.edges())
    return H, branch
G = nx.convert_node_labels_to_integers(read_any(HERE / "coloring" / "myciel7.dgf"))
for cfg in ((dict(), dict(better_move=True), dict(repaired_rules=False)) if len(sys.argv) < 4 else ()):
    H, br = contract(G, 110, "min-d"); masks, _ = masks_from_graph(nx.convert_node_labels_to_integers(H))
    json.dump(sorted(sorted(b) for b in br.values()), open(Path(__file__).with_name("myciel7_minor110_branch_sets.json"), "w"))
    t0 = time.time(); a = decide(masks, 71, **cfg); b = decide(masks, 72, **cfg)
    print(f"minor110 {cfg or 'default'}: pw<=70 {a.status} ({a.nodes:,} nodes, {time.time()-t0:.1f}s); pw<=71 {b.status}", flush=True)
for m in [int(x) for x in sys.argv[2].split(",")]:
    for rule in ("min-d", "least-c"):
        H, _ = contract(G, m, rule); masks, _ = masks_from_graph(nx.convert_node_labels_to_integers(H))
        t0 = time.time(); a = decide(masks, 72, deadline=time.monotonic() + budget)
        print(f"minor{m} {rule}: pw<=71 {a.status} ({a.nodes:,} nodes, {time.time()-t0:.0f}s)", flush=True)
        if a.status == "unsat": print("==> pw(myciel7) >= 72, hence = 72 with CMN's layout", flush=True); sys.exit()
