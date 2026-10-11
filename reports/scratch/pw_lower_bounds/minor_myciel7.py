"""Contraction relaxation on myciel7 (M8, 191 vertices, pw <= 72 open) and the
myciel6 size sweep: how small can the minor be and still certify?"""
import sys, time
sys.path.insert(0, "reports/scratch/pw_lower_bounds")
from minor_exact import contract_to, read_any, HERE, solve, nx
import builtins
budget = float(sys.argv[1])
G6 = nx.convert_node_labels_to_integers(read_any(HERE / "coloring" / "myciel6.dgf"))
for m in (52, 54, 56, 58, 62, 65, 75, 80, 85, 90):
    for rule in ("min-d", "least-c"):
        H = contract_to(G6, m, rule); t0 = time.time(); s = solve(H, time_budget=budget)
        print(f"myciel6 m={m} {rule}: pw(minor) {'=' if s.proof else '<='} {s.width} [{s.lower}] {time.time()-t0:.1f}s nodes={s.nodes}", flush=True)
G = nx.convert_node_labels_to_integers(read_any(HERE / "coloring" / "myciel7.dgf"))
for m in (80, 100, 110, 120, 130, 140):
    for rule in ("min-d", "least-c"):
        H = contract_to(G, m, rule); t0 = time.time(); s = solve(H, time_budget=budget)
        print(f"myciel7 m={m} {rule}: pw(minor) {'=' if s.proof else '<='} {s.width} [{s.lower}] {time.time()-t0:.1f}s nodes={s.nodes}", flush=True)
