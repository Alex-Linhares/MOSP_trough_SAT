"""Item 03 (b), second half: the forest instances on record (item 01's map, gamma = 0: 2 corpus, 3,446 ensemble)
carry certified optima, so pw = optimum - 1 with nothing solved. For each: omega, h, pw(B) by the C program
on the incidence forest (a tree per component), and every candidate. Regenerates ensemble instances from
their seeds, reads the two corpus instances from the benchmark tree and their optima from the map
(learning/data/excess.csv, which read solutions/ read-only). Writes record_forests.csv.
    cd /home/al/dev/MOSP && nice -n 19 python3 reports/scratch/forest_regime/score_record.py [workers]
"""
import csv, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from learning.block_trees import (CANDIDATES, block_height, candidates, default_workers, graph6, incidence_graph,
                                  is_incidence_forest, largest_pattern, run_pathwidth_one, vertex_separation)
from learning.ensemble import Cell, generate
from learning.excess import load
HERE = Path(__file__).resolve().parent
workers = int(sys.argv[1]) if len(sys.argv) > 1 else default_workers()
frame = load()
forests = frame[(frame["gamma"] == 0) & frame["certified"]].copy()
print(f"{len(forests)} forest instances on record ({(forests.source == 'corpus').sum()} corpus)", flush=True)


def patterns_of(matrix):
    return [list(np.flatnonzero(matrix[:, j])) for j in range(matrix.shape[1])]


def matrix_of_row(row):
    if row.source == "ensemble":
        tag = "b" if row.generator == "bernoulli" else "f"
        index = int(row.instance_name.rsplit("_i", 1)[1])
        inst = generate(Cell.parse(f"{tag}:{int(row.n)}:{int(row.m)}:{row.param:g}"), index)
        assert inst.name == row.instance_name
        return inst.matrix
    from learning.dataset import enumerate_instances
    for path, inst in enumerate_instances():
        if str(path) == row.source_file and inst.name == row.instance_name:
            return inst.matrix
    raise KeyError(row.instance_name)


def job(row):
    matrix = np.asarray(matrix_of_row(row))
    patterns = patterns_of(matrix)
    n, m = matrix.shape
    assert is_incidence_forest(patterns, n)
    B = incidence_graph(patterns, n)
    rb = run_pathwidth_one(graph6(B), 600)
    assert vertex_separation(B, rb["layout"]) == rb["width"]
    omega, h = largest_pattern(patterns), block_height(patterns)
    pw = int(row.optimum) - 1
    out = {"source": row.source, "instance_name": row.instance_name, "n": n, "m": m, "n_ones": int(matrix.sum()),
           "e": row.e, "kappa": int(row.kappa), "N_B": n + m, "omega": omega, "h": h, "optimum": int(row.optimum),
           "pw": pw, "pw_B": rb["width"], "status_B": rb["status"]}
    out.update(candidates(omega, rb["width"], h, n + m))
    return out


t0 = time.time()
with ThreadPoolExecutor(max_workers=workers) as pool:
    rows = list(pool.map(job, list(forests.itertuples(index=False))))
with open(HERE / "record_forests.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(f"done in {time.time()-t0:.0f}s", flush=True)
