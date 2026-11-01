"""Item 03 (c): the caterpillar of cliques -- a chain of `length` cliques K_s with a pendant K_s at every
non-shared customer -- where the additive and the multiplicative candidates differ most. s in {2..5},
length in {1, 2, 3, 5, 8, 12}; exact pathwidth of the MOSP graph and of the incidence tree by the C program.
Writes caterpillar_values.csv and caterpillar_layouts.txt.
    cd /home/al/dev/MOSP && nice -n 19 python3 reports/scratch/forest_regime/run_caterpillar.py
"""
import csv, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from learning.block_trees import (CANDIDATES, block_height, candidates, caterpillar_of_cliques, graph6,
                                  incidence_graph, mosp_graph, n_customers, run_pathwidth_one, vertex_separation)
HERE = Path(__file__).resolve().parent
rows, layouts = [], []
for s in (2, 3, 4, 5):
    for length in (1, 2, 3, 5, 8, 12):
        patterns = caterpillar_of_cliques(s, length)
        n, m = n_customers(patterns), len(patterns)
        G, B = mosp_graph(patterns), incidence_graph(patterns)
        r = run_pathwidth_one(graph6(G), 600); rb = run_pathwidth_one(graph6(B), 600)
        assert vertex_separation(G, r["layout"]) == r["width"] and vertex_separation(B, rb["layout"]) == rb["width"]
        h = block_height(patterns)
        row = {"s": s, "length": length, "n": n, "m": m, "N_B": n + m, "omega": s, "h": h, "pw": r["width"],
               "status": r["status"], "nodes": r.get("nodes"), "seconds": r.get("seconds"),
               "pw_B": rb["width"], "status_B": rb["status"]}
        row.update(candidates(s, rb["width"], h, n + m)); rows.append(row)
        layouts.append((f"CAT_{s}_{length}", r["layout"])); layouts.append((f"CAT_{s}_{length}_B", rb["layout"]))
        print(f"CAT(s={s}, L={length}) n={n} m={m} h={h}: pw={r['width']} {r['status']} nodes={r.get('nodes')} "
              f"{r.get('seconds')}s | pw(B)={rb['width']}", flush=True)
fields = list(rows[0].keys())
with open(HERE / "caterpillar_values.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
with open(HERE / "caterpillar_layouts.txt", "w") as f:
    for name, lay in layouts:
        f.write(name + " " + " ".join(map(str, lay)) + "\n")
print("done")
