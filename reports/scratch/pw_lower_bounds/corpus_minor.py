"""Contraction-minor bound on the MOSP graph of hard corpus instances, with the
graph pathwidth solver: pw(minor) + 1 <= MOSP optimum. Also MMD+ and the
expansion bound (cap 8) for comparison. Budget per minor in seconds."""
import sys, time, json
from pathlib import Path
import networkx as nx
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "reports/scratch/pw_lower_bounds"))
from minor_exact import contract_to, solve
from mosp.instance import MOSPInstance
from customer_inter.customer_graph import build_customer_graph
sys.path.insert(0, str(ROOT / "pathwidth_solver"))
from pathwidth.graph import masks_from_graph
from pathwidth.bounds import contraction_degeneracy
from satisfiability.expansion_bound import expansion_bound

budget = float(sys.argv[1])
FRACS = [float(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 else [0.4, 0.5, 0.6, 0.7, 0.8]
ONLY = sys.argv[3].split(',') if len(sys.argv) > 3 else None
CS = ROOT / "benchmarks/instances/MOSP_Instances/Chu_Stuckey"
targets = [("Random-125-125-2-1_0", CS / "Random-125-125-2-1.txt", 0),
           ("Random-125-125-4-1_0", CS / "Random-125-125-4-1.txt", 0),
           ("Random-125-125-6-1_0", CS / "Random-125-125-6-1.txt", 0),
           ("Random-125-125-8-2_0", CS / "Random-125-125-8-2.txt", 0),
           ("SP4", ROOT / "benchmarks/instances/ChallengeInstances2005/Wilson/sp4.txt", 3)]
for name, path, idx in targets:
    if ONLY and name not in ONLY: continue
    inst = MOSPInstance.from_benchmark_file(str(path))[idx]
    sol = json.load(open(ROOT / "solutions" / f"{name}.json")); opt = sol["mosp_value"]
    G = nx.convert_node_labels_to_integers(build_customer_graph(inst)); G.remove_edges_from(nx.selfloop_edges(G))
    n = G.number_of_nodes(); masks, _ = masks_from_graph(G)
    mmd = contraction_degeneracy(masks) + 1
    t0 = time.time(); ex = expansion_bound(inst, max_t=8, time_budget=30).value; tex = time.time() - t0
    print(f"{name}: n={n} opt={opt} MMD+ +1={mmd} expansion(t8)={ex} ({tex:.0f}s) stored relaxation lb={sol.get('lower_bound')}", flush=True)
    best = 0
    for frac in FRACS:
        m = int(frac * n); row = []
        for rule in ("min-d", "least-c"):
            H = contract_to(G, m, rule); t0 = time.time(); s = solve(H, time_budget=budget)
            val = (s.width + 1) if s.proof else (s.lower + 1)
            best = max(best, val); row.append(f"{rule} {'=' if s.proof else '>='}{val} {time.time()-t0:.0f}s")
        print(f"   minor m={m}: " + "; ".join(row), flush=True)
    print(f"   best minor bound {best} vs opt {opt}", flush=True)
