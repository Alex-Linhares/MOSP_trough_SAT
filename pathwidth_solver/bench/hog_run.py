"""Pathwidth of every House of Graphs graph, with our solver.

House of Graphs stores treewidth but not pathwidth. Queue order: graphs whose
treewidth House of Graphs computed come first, then the ones where it timed out,
each group by size. Each graph is solved in its own process, killed at the cap,
with the solver's defaults (minor step on). Their treewidth is recorded beside
our width and is not given to the solver, so every proof stands on its own;
tw <= pw is then a check (a row with width < their treewidth is a conflict).

Run the whole thing under nice:
    nice -n 19 python bench/hog_run.py --procs 20 --time 300

Outputs (resumable by graphId):
    bench/results/hog_pathwidth.csv   one row per graph
    bench/results/hog_witness.jsonl   layout (closing order) and minor certificate
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
GRAPHS = HERE / "instances" / "hog" / "graphs.jsonl"
CSV = HERE / "results" / "hog_pathwidth.csv"
WIT = HERE / "results" / "hog_witness.jsonl"
FIELDS = ["graphId", "graphName", "n", "m", "hog_tw", "hog_tw_status", "width", "lower", "proof",
          "nodes", "seconds", "status", "conflict"]
TW = "39"

CHILD = r"""
import json, sys, time
sys.path.insert(0, sys.argv[1])
import networkx as nx
from pathwidth import solve
G = nx.from_graph6_bytes(sys.argv[2].encode())
t = time.time()
s = solve(G, time_budget=float(sys.argv[3]))
print(json.dumps({"width": s.width, "lower": s.lower, "proof": s.proof, "nodes": s.nodes,
                  "seconds": time.time() - t, "order": list(s.order), "minor": s.minor}))
"""


def one(g, cap):
    st, tw = g["invariants"].get(TW, [None, None])
    row = dict(graphId=g["graphId"], graphName=g["graphName"], n=g["n"], m="",
               hog_tw="" if tw is None or st != 2 else int(tw), hog_tw_status=st,
               width="", lower="", proof="", nodes="", seconds="", status="", conflict="")
    m = g["invariants"].get("14", [None, None])[1]
    row["m"] = "" if m is None else int(m)
    t = time.time()
    try:
        out = subprocess.run([sys.executable, "-c", CHILD, str(ROOT), g["canonicalForm"], str(cap)],
                             capture_output=True, text=True, timeout=cap + 60)
        if out.returncode == 0 and out.stdout.strip():
            r = json.loads(out.stdout.strip().splitlines()[-1])
            row.update(width=r["width"], lower=r["lower"], proof=r["proof"], nodes=r["nodes"],
                       seconds=round(r["seconds"], 3), status="ok")
            if row["hog_tw"] != "" and r["width"] < row["hog_tw"]:
                row["conflict"] = "width<tw"
            return row, {"graphId": g["graphId"], "width": r["width"], "proof": r["proof"],
                         "order": r["order"], "minor": r["minor"]}
        row.update(status="error", seconds=round(time.time() - t, 3))
    except subprocess.TimeoutExpired:
        row.update(status="killed", seconds=round(time.time() - t, 3))
    return row, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=20)
    ap.add_argument("--time", type=float, default=300)
    a = ap.parse_args()
    graphs = [json.loads(l) for l in open(GRAPHS)]
    done = {int(r["graphId"]) for r in csv.DictReader(open(CSV))} if CSV.exists() else set()

    def key(g):
        st, tw = g["invariants"].get(TW, [None, None])
        m = g["invariants"].get("14", [0, 0])[1] or 0
        return (0 if st == 2 and tw is not None else 1, g["n"], m)

    todo = sorted((g for g in graphs if g["graphId"] not in done), key=key)
    print(f"{len(todo)} to do, {len(done)} done", flush=True)
    new = not CSV.exists()
    with open(CSV, "a", newline="") as f, open(WIT, "a") as wf, ThreadPoolExecutor(a.procs) as ex:
        w = csv.DictWriter(f, FIELDS)
        if new:
            w.writeheader()
        futs = [ex.submit(one, g, a.time) for g in todo]
        for i, fu in enumerate(as_completed(futs), 1):
            row, wit = fu.result()
            w.writerow(row); f.flush()
            if wit:
                wf.write(json.dumps(wit) + "\n"); wf.flush()
            if row["conflict"] or i % 500 == 0:
                print(f"[{i}/{len(todo)}] {row['graphId']} n={row['n']} w={row['width']} "
                      f"tw={row['hog_tw']} {row['proof']} {row['status']} {row['conflict']}", flush=True)


if __name__ == "__main__":
    main()
