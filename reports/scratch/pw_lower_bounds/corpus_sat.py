"""Independent SAT check (graph pathwidth encoding of pathwidth_solver/bench/myciel6_sat.py)
of the corpus minor certificates: refute pw <= opt-2 (MOSP <= opt-1) on the minor."""
import sys, time, json
from pathlib import Path
import networkx as nx
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "pathwidth_solver/bench"))
from mosp.instance import MOSPInstance
from customer_inter.customer_graph import build_customer_graph
from myciel6_sat import encode
from pysat.solvers import Solver
CS = "benchmarks/instances/MOSP_Instances/Chu_Stuckey/"
for name, f, m, rule in [("Random-125-125-2-3_0", "Random-125-125-2-3.txt", 70, "least-c"),
                         ("Random-125-125-2-1_0", "Random-125-125-2-1.txt", 87, "min-d")]:
    inst = MOSPInstance.from_benchmark_file(str(ROOT / CS / f))[0]
    opt = json.load(open(ROOT / "solutions" / f"{name}.json"))["mosp_value"]
    G = nx.convert_node_labels_to_integers(build_customer_graph(inst)); G.remove_edges_from(nx.selfloop_edges(G))
    H = nx.Graph(G)
    while H.number_of_nodes() > m:
        v = min(H, key=lambda x: (H.degree(x), x)); nb = list(H[v])
        u = (min(nb, key=lambda c: (len(set(H[c]) & set(nb)), c)) if rule == "least-c" else min(nb, key=lambda c: (H.degree(c), c)))
        H = nx.contracted_nodes(H, u, v, self_loops=False)
    k = opt - 2
    cnf, pool, V, x = encode(H, k); t0 = time.time()
    with Solver(name="cadical195", bootstrap_with=cnf.clauses) as S:
        r = S.solve()
    print(f"{name} minor{m} {rule}: pw<={k} {'SAT' if r else 'UNSAT'} in {time.time()-t0:.0f}s ({pool.top} vars, {len(cnf.clauses)} clauses)", flush=True)
