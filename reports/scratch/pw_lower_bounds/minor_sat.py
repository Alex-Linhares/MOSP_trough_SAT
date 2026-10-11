"""Independent check: SAT (pathwidth_solver/bench/myciel6_sat.encode, no symmetry
breaking) refutes pw <= 37 on the 58-vertex min-d minor of myciel6."""
import sys, json, time
sys.path.insert(0, "pathwidth_solver/bench"); sys.path.insert(0, "reports/scratch/pw_lower_bounds")
import networkx as nx
from myciel6_sat import encode
from minor_exact import contract_to, read_any, HERE
from pysat.solvers import Solver
G = nx.convert_node_labels_to_integers(read_any(HERE / "coloring" / "myciel6.dgf"))
H = contract_to(G, 58, "min-d")
json.dump(sorted(map(sorted, H.edges())), open("reports/scratch/pw_lower_bounds/myciel6_minor58_edges.json", "w"))
for k in (38, 37):
    cnf, pool, V, x = encode(H, k); t0 = time.time()
    with Solver(name="cadical195", bootstrap_with=cnf.clauses) as S:
        r = S.solve()
    print(f"minor58 pw<={k}: {'SAT' if r else 'UNSAT'} in {time.time()-t0:.1f}s ({pool.top} vars, {len(cnf.clauses)} clauses)", flush=True)
