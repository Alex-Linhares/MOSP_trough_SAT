"""Verify the minor certificate for a corpus instance: build the min-d minor at m,
check it is a minor of the MOSP graph, refute MOSP <= opt-1 on it under several
configurations (including every dominance rule off), and confirm opt is feasible."""
import sys, time, json
from pathlib import Path
import networkx as nx
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "pathwidth_solver"))
from mosp.instance import MOSPInstance
from customer_inter.customer_graph import build_customer_graph
from pathwidth.graph import masks_from_graph
from pathwidth.search import decide

name, path, idx, m, rule = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
budget = float(sys.argv[6]) if len(sys.argv) > 6 else 600
inst = MOSPInstance.from_benchmark_file(str(ROOT / path))[idx]
opt = json.load(open(ROOT / "solutions" / f"{name}.json"))["mosp_value"]
G = nx.convert_node_labels_to_integers(build_customer_graph(inst)); G.remove_edges_from(nx.selfloop_edges(G))
H = nx.Graph(G); branch = {v: {v} for v in H}
while H.number_of_nodes() > m:
    v = min(H, key=lambda x: (H.degree(x), x)); nb = list(H[v])
    u = (min(nb, key=lambda c: (len(set(H[c]) & set(nb)), c)) if rule == "least-c" else min(nb, key=lambda c: (H.degree(c), c)))
    H = nx.contracted_nodes(H, u, v, self_loops=False); branch[u] |= branch.pop(v)
n = G.number_of_nodes()
assert sorted(x for b in branch.values() for x in b) == list(range(n))
assert all(nx.is_connected(G.subgraph(b)) for b in branch.values())
assert all(any(G.has_edge(a, b) for a in branch[u] for b in branch[v]) for u, v in H.edges())
print(f"{name}: minor of {m}/{n} vertices ({rule}) verified as a minor; opt {opt}", flush=True)
Hi = nx.convert_node_labels_to_integers(H); masks, _ = masks_from_graph(Hi)
for cfg in [dict(), dict(better_move=True), dict(subset_rule=False, definite_move=False, old_move=False, memo=True, memo_limit=50_000_000)]:
    t0 = time.time(); a = decide(masks, opt - 1, deadline=time.monotonic() + budget, **cfg)
    print(f"  {cfg or 'default'}: MOSP<= {opt-1} on minor: {a.status} nodes={a.nodes:,} {time.time()-t0:.1f}s", flush=True)
b = decide(masks, opt, deadline=time.monotonic() + budget)
print(f"  MOSP<= {opt} on minor: {b.status}", flush=True)
json.dump({"m": m, "rule": rule, "branch_sets": sorted(sorted(s) for s in branch.values())},
          open(Path(__file__).with_name(f"{name}_minor{m}_{rule}.json"), "w"))
