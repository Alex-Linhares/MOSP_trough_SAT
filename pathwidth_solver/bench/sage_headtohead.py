"""Head to head against SageMath's exact vertex separation, on this machine.

SageMath's `vertex_separation(G, algorithm="BAB")` is the branch and bound of
Coudert, Mazauric & Nisse (2014, 2016), put there by its authors "to perform
comparisons on a fair basis". This runs it and our solver on the same graphs,
one core each, the same wall-clock cap, each graph in its own process killed at
the cap. SageMath runs from the `sage` conda environment (10.8 here).

    python bench/sage_headtohead.py --sets coloring named vsplib-tree vsplib-hb vsplib-grids \
        --rome-sample 500 --time 600 --procs 8 --out bench/results/sage_headtohead.csv

Resumable: rows already in --out are skipped. Columns: set, name, n, m, solver,
width, proved (1 if the solver claims optimality), seconds, status
(ok / timeout / error), detail. Sage's BAB is exact when it returns, so a
returned value counts as proved. Our solver runs with its defaults (the minor
step on), so the row records what the shipped solver does.
"""
from __future__ import annotations

import argparse
import csv
import json
import multiprocessing as mp
import random
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from readers import HERE as INST, SETS, read_any  # noqa: E402

SAGE_PY = "/home/al/anaconda3/envs/sage/bin/python"
FIELDS = ["set", "name", "n", "m", "solver", "width", "proved", "seconds", "status", "detail"]

SAGE_CODE = r"""
import json, sys, time
from sage.all import Graph
from sage.graphs.graph_decompositions.vertex_separation import vertex_separation
n, edges = json.load(open(sys.argv[1]))
G = Graph(); G.add_vertices(range(n)); G.add_edges(edges)
t = time.time()
w, order = vertex_separation(G, algorithm="BAB")
print(json.dumps({"width": int(w), "seconds": time.time() - t}))
"""

OURS_CODE = r"""
import json, sys, time
sys.path.insert(0, sys.argv[2])
import networkx as nx
from pathwidth import solve
n, edges = json.load(open(sys.argv[1]))
G = nx.Graph(); G.add_nodes_from(range(n)); G.add_edges_from(edges)
t = time.time()
s = solve(G, time_budget=float(sys.argv[3]))
print(json.dumps({"width": s.width, "proved": bool(s.proof), "proof": s.proof, "seconds": time.time() - t}))
"""


def graphs(sets, rome_sample, seed):
    for name in sets:
        for p in SETS[name]():
            yield name, p
    if rome_sample:
        rome = list(SETS["rome"]())
        random.Random(seed).shuffle(rome)
        for p in sorted(rome[:rome_sample]):
            yield "rome-sample", p


def one(job):
    setname, path, solver, cap = job
    G = read_any(path)
    idx = {v: i for i, v in enumerate(G.nodes())}
    edges = [(idx[u], idx[v]) for u, v in G.edges()]
    row = dict(set=setname, name=str(path.relative_to(INST)), n=G.number_of_nodes(),
               m=G.number_of_edges(), solver=solver, width="", proved="", seconds="", status="", detail="")
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump([G.number_of_nodes(), edges], f)
        gfile = f.name
    if solver == "sage":
        cmd = [SAGE_PY, "-c", SAGE_CODE, gfile]
    else:
        cmd = [sys.executable, "-c", OURS_CODE, gfile, str(ROOT), str(cap)]
    t = time.time()
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=cap + 30)
        if out.returncode == 0 and out.stdout.strip():
            r = json.loads(out.stdout.strip().splitlines()[-1])
            row.update(width=r["width"], seconds=round(time.time() - t, 3), status="ok",
                       proved=int(r.get("proved", True)), detail=r.get("proof", ""))
        else:
            row.update(status="error", seconds=round(time.time() - t, 3), detail=out.stderr.strip()[-200:])
    except subprocess.TimeoutExpired:
        row.update(status="timeout", seconds=round(time.time() - t, 3))
    Path(gfile).unlink(missing_ok=True)
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sets", nargs="*", default=["coloring", "named", "vsplib-tree", "vsplib-hb", "vsplib-grids"])
    ap.add_argument("--rome-sample", type=int, default=500)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--time", type=float, default=600)
    ap.add_argument("--procs", type=int, default=8)
    ap.add_argument("--solvers", nargs="*", default=["sage", "ours"])
    ap.add_argument("--out", type=Path, default=HERE / "results" / "sage_headtohead.csv")
    a = ap.parse_args()
    done = set()
    if a.out.exists():
        done = {(r["name"], r["solver"]) for r in csv.DictReader(open(a.out))}
    jobs = [(s, p, solver, a.time) for s, p in graphs(a.sets, a.rome_sample, a.seed)
            for solver in a.solvers if (str(p.relative_to(INST)), solver) not in done]
    new = not a.out.exists()
    with open(a.out, "a", newline="") as f, mp.get_context("spawn").Pool(a.procs) as pool:
        w = csv.DictWriter(f, FIELDS)
        if new:
            w.writeheader()
        for i, row in enumerate(pool.imap_unordered(one, jobs), 1):
            w.writerow(row); f.flush()
            print(f"[{i}/{len(jobs)}] {row['solver']:5} {row['name']} n={row['n']} "
                  f"{row['status']} w={row['width']} {row['seconds']}s", flush=True)


if __name__ == "__main__":
    main()
