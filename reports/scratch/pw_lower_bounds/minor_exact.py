"""Contraction relaxation for pathwidth: contract (MMD+ least-c order) down to
m vertices, solve the minor exactly with the pathwidth_solver, report pw(minor).
pw is minor-monotone, so pw(minor) <= pw(G): a genuine pathwidth lower bound,
not capped by treewidth. Budget per minor in seconds."""
import sys, time
from pathlib import Path
import networkx as nx
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "pathwidth_solver")); sys.path.insert(0, str(ROOT / "pathwidth_solver" / "bench"))
from readers import read_any, HERE
from pathwidth import solve

def contract_to(G, m, rule="least-c"):
    H = nx.Graph(G)
    while H.number_of_nodes() > m:
        v = min(H, key=lambda x: (H.degree(x), x))
        nb = list(H[v])
        if not nb: H.remove_node(v); continue
        if rule == "least-c":
            u = min(nb, key=lambda c: (len(set(H[c]) & set(nb)), c))
        else:
            u = min(nb, key=lambda c: (H.degree(c), c))
        H = nx.contracted_nodes(H, u, v, self_loops=False)
    return nx.convert_node_labels_to_integers(H)

def main():
  budget = float(sys.argv[1]) if len(sys.argv) > 1 else 60
  for name, pw, sizes in [("myciel5", 20, [25, 30, 35, 40]), ("myciel6", 38, [40, 50, 60, 70])]:
      G = nx.convert_node_labels_to_integers(read_any(HERE / "coloring" / f"{name}.dgf"))
      for m in sizes:
          for rule in ("least-c", "min-d"):
              H = contract_to(G, m, rule)
              t0 = time.time(); sol = solve(H, time_budget=budget)
              print(f"{name} (pw {pw}) minor m={m} {rule}: edges={H.number_of_edges()} pw(minor) "
                    f"{'=' if sol.proof else '<='} {sol.width} lower={sol.lower} proof={sol.proof!r} {time.time()-t0:.1f}s", flush=True)

if __name__ == "__main__":
    main()
