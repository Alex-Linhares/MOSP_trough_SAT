"""myciel7: build larger contraction minors (both rules) with mc_graph, replay
them, write CLAIM_edges.json/.txt and a certificate JSON, for the w = 71 probes.
  python mc_myciel7_minors.py 130 140 150"""
import json, sys
from pathlib import Path
from mc_graph import read_dgf, heuristic_sequence, replay, relabel_sorted, edges, graph_hash
HERE = Path(__file__).resolve().parent
G = read_dgf(HERE.parents[2] / "pathwidth_solver/bench/instances/coloring/myciel7.dgf")
for m in map(int, sys.argv[1:]):
    for rule in ("min-d", "least-c"):
        seq = heuristic_sequence(G, m, rule); H, br = replay(G, seq); Hs, _ = relabel_sorted(H)
        name = f"myciel7_m{m}_{rule}"
        json.dump({"graph": "myciel7", "m": m, "rule": rule, "contraction_sequence": seq,
                   "branch_sets": sorted(sorted(b) for b in br.values()), "minor_edges": edges(Hs),
                   "minor_sha256": graph_hash(Hs)}, open(HERE / f"{name}.json", "w"))
        E = edges(Hs)
        open(HERE / f"{name}_edges.txt", "w").write(f"{m} {len(E)}\n" + "".join(f"{a} {b}\n" for a, b in E))
        print(name, len(E), "edges")
