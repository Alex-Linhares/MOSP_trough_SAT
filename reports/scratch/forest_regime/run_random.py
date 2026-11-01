"""Item 03 (b): random block trees -- one pattern, then patterns of random size (Chu & Stuckey's size law,
Binomial(n, d/n) with 0 and 1 moved up to 2) attached at a uniformly random existing customer -- at
d in {2, 3, 4}, n in {20, 40, 60, 80, 100, 120}, 50 per cell (seed = 1000 d + n*10 + i... see `seed_of`), exact
pathwidth of the MOSP graph and of the incidence tree by the C program (-t 600). Every instance regenerates
from (n, d, seed); the layouts (witnesses) are in random_layouts.txt. Writes random_block_trees.csv.
    cd /home/al/dev/MOSP && nice -n 19 python3 reports/scratch/forest_regime/run_random.py [workers]
"""
import csv, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from learning.block_trees import (CANDIDATES, block_height, candidates, default_workers, graph6, incidence_graph,
                                  is_incidence_forest, largest_pattern, mosp_graph, n_customers, random_block_tree,
                                  run_pathwidth_one, vertex_separation)
HERE = Path(__file__).resolve().parent
TIMEOUT = 600
workers = int(sys.argv[1]) if len(sys.argv) > 1 else default_workers()


def seed_of(n, d, i):
    return 100000 * d + 100 * n + i


cases = [(n, d, i) for d in (2, 3, 4) for n in (20, 40, 60, 80, 100, 120) for i in range(50)]


def job(case):
    n, d, i = case
    seed = seed_of(n, d, i)
    patterns = random_block_tree(n, d, seed)
    assert n_customers(patterns) == n and is_incidence_forest(patterns)
    G, B = mosp_graph(patterns), incidence_graph(patterns)
    r = run_pathwidth_one(graph6(G), TIMEOUT); rb = run_pathwidth_one(graph6(B), TIMEOUT)
    assert vertex_separation(G, r["layout"]) == r["width"] and vertex_separation(B, rb["layout"]) == rb["width"]
    omega, h, m = largest_pattern(patterns), block_height(patterns), len(patterns)
    row = {"n": n, "d": d, "index": i, "seed": seed, "m": m, "n_ones": sum(map(len, patterns)), "N_B": n + m,
           "omega": omega, "h": h, "pw": r["width"], "status": r["status"], "nodes": r.get("nodes"),
           "seconds": r.get("seconds"), "pw_B": rb["width"], "status_B": rb["status"]}
    row.update(candidates(omega, rb["width"], h, n + m))
    return row, (f"RBT_n{n}_d{d}_i{i:02d}", r["layout"]), (f"RBT_n{n}_d{d}_i{i:02d}_B", rb["layout"])


t0 = time.time()
print(f"{len(cases)} random block trees, {workers} workers", flush=True)
with ThreadPoolExecutor(max_workers=workers) as pool:
    results = list(pool.map(job, cases))
rows = [x[0] for x in results]
with open(HERE / "random_block_trees.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
with open(HERE / "random_layouts.txt", "w") as f:
    for _, a, b in results:
        f.write(a[0] + " " + " ".join(map(str, a[1])) + "\n"); f.write(b[0] + " " + " ".join(map(str, b[1])) + "\n")
cens = sum(r["status"] == "upper" for r in rows)
print(f"done in {time.time()-t0:.0f}s; censored {cens}; max pw {max(r['pw'] for r in rows)}; "
      f"max nodes {max(r['nodes'] or 0 for r in rows)}", flush=True)
