"""Item 03 (a): exact pathwidth of every clique tree CT(s, h, b), s in {2..5}, h in {1..3}, b in {1..3},
with at most 400 customers, by the C program pathwidth_solver/cli/pathwidth (-t 600, nice 19), largest
first; and of its incidence tree B. Writes ct/CT_s_h_b.g6, ct/CT_s_h_b_B.g6, ct_values.csv (one row per
graph with every candidate), ct_layouts.txt (the layouts, the witnesses of the upper bounds).
    cd /home/al/dev/MOSP && nice -n 19 python3 reports/scratch/forest_regime/run_ct.py [workers]
"""
import csv, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from learning.block_trees import (CANDIDATES, block_height, candidates, clique_tree, ct_size, default_workers,
                                  graph6, incidence_graph, mosp_graph, n_customers, run_pathwidth_one,
                                  vertex_separation)
from concurrent.futures import ThreadPoolExecutor

HERE = Path(__file__).resolve().parent
TIMEOUT = 600
workers = int(sys.argv[1]) if len(sys.argv) > 1 else default_workers()
cases = [(s, h, b) for s in (2, 3, 4, 5) for h in (1, 2, 3) for b in (1, 2, 3) if ct_size(s, h, b) <= 400]
cases.sort(key=lambda c: -ct_size(*c))
print(f"{len(cases)} clique trees, {workers} workers, timeout {TIMEOUT}s each", flush=True)


def job(case):
    s, h, b = case
    patterns, _ = clique_tree(s, h, b)
    n, m = n_customers(patterns), len(patterns)
    G, B = mosp_graph(patterns), incidence_graph(patterns)
    g6, g6b = graph6(G), graph6(B)
    (HERE / "ct" / f"CT_{s}_{h}_{b}.g6").write_text(g6 + "\n")
    (HERE / "ct" / f"CT_{s}_{h}_{b}_B.g6").write_text(g6b + "\n")
    t0 = time.time()
    rb = run_pathwidth_one(g6b, TIMEOUT)
    r = run_pathwidth_one(g6, TIMEOUT)
    assert vertex_separation(G, r["layout"]) == r["width"], "layout does not realise the width"
    assert vertex_separation(B, rb["layout"]) == rb["width"]
    hh = block_height(patterns)
    assert hh == h
    row = {"s": s, "h": h, "b": b, "n": n, "m": m, "N_B": n + m, "omega": s, "pw": r["width"], "status": r["status"],
           "nodes": r.get("nodes"), "seconds": r.get("seconds"), "lower": r.get("lower"), "upper_start": r.get("upper_start"),
           "pw_B": rb["width"], "status_B": rb["status"], "nodes_B": rb.get("nodes"), "seconds_B": rb.get("seconds")}
    row.update(candidates(s, rb["width"], h, n + m))
    print(f"CT({s},{h},{b}) n={n} m={m}: pw={r['width']} {r['status']} nodes={r.get('nodes')} {r.get('seconds')}s | "
          f"pw(B)={rb['width']} {rb['status']} | wall {time.time()-t0:.1f}s", flush=True)
    return row, (f"CT_{s}_{h}_{b}", r["layout"]), (f"CT_{s}_{h}_{b}_B", rb["layout"])


with ThreadPoolExecutor(max_workers=workers) as pool:
    results = list(pool.map(job, cases))
rows = [x[0] for x in results]
rows.sort(key=lambda r: (r["s"], r["b"], r["h"]))
fields = ["s", "h", "b", "n", "m", "N_B", "omega", "pw", "status", "nodes", "seconds", "lower", "upper_start",
          "pw_B", "status_B", "nodes_B", "seconds_B", *CANDIDATES]
with open(HERE / "ct_values.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
with open(HERE / "ct_layouts.txt", "w") as f:
    for _, lay, layb in results:
        f.write(f"{lay[0]} " + " ".join(map(str, lay[1])) + "\n")
        f.write(f"{layb[0]} " + " ".join(map(str, layb[1])) + "\n")
print("done", flush=True)
