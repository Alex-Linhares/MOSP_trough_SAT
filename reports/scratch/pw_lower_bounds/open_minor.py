"""Try to certify the two open corpus instances by a minor: refute MOSP <= value-1
on contractions of the MOSP graph. Writes nothing to solutions/."""
import sys, time, json
from pathlib import Path
import networkx as nx
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "pathwidth_solver")); sys.path.insert(0, str(ROOT / "reports/scratch/pw_lower_bounds"))
from mosp.instance import MOSPInstance
from customer_inter.customer_graph import build_customer_graph
from pathwidth.graph import masks_from_graph
from pathwidth.search import decide
from minor_exact import contract_to
budget = float(sys.argv[1])
CS = ROOT / "benchmarks/instances/MOSP_Instances/Chu_Stuckey"
for name, f in [("Random-125-125-2-3_0", "Random-125-125-2-3.txt"), ("Random-125-125-2-2_0", "Random-125-125-2-2.txt")]:
    inst = MOSPInstance.from_benchmark_file(str(CS / f))[0]
    sol = json.load(open(ROOT / "solutions" / f"{name}.json")); val = sol["mosp_value"]
    G = nx.convert_node_labels_to_integers(build_customer_graph(inst)); G.remove_edges_from(nx.selfloop_edges(G))
    print(f"{name}: n={G.number_of_nodes()} recorded {val} ({sol.get('provenance')}), stored lb {sol.get('lower_bound')}", flush=True)
    done = False
    for m in (70, 78, 85, 90, 95, 100, 105):
        for rule in ("min-d", "least-c"):
            H = contract_to(G, m, rule); masks, _ = masks_from_graph(H); t0 = time.time()
            a = decide(masks, val - 1, deadline=time.monotonic() + budget)
            print(f"   m={m} {rule}: MOSP<={val-1} on minor: {a.status} nodes={a.nodes:,} {time.time()-t0:.0f}s", flush=True)
            if a.status == "unsat":
                print(f"   ==> {name}: optimum {val} certified by a {m}-vertex minor ({rule})", flush=True); done = True; break
        if done: break
