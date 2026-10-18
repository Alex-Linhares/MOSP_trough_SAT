"""Second pass on the House of Graphs graphs the first pass left unproved.

Each graph restarts from what the first pass established instead of repeating
it: its witness layout and width as the starting upper bound, and its proved
lower bound (bounds and minors, both sound) as the floor. All 3,563 are
connected, so the seeds apply to the whole graph. Same per-graph process and
cap as hog_run.py.

    nice -n 19 python bench/hog_run2.py --procs 25 --time 300

Outputs (resumable): bench/results/hog_pathwidth_pass2.csv, hog_witness_pass2.jsonl.
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import hog_run as h1  # noqa: E402

CSV = HERE / "results" / "hog_pathwidth_pass2.csv"
WIT = HERE / "results" / "hog_witness_pass2.jsonl"
FIELDS = h1.FIELDS + ["width_pass1", "lower_pass1"]

CHILD = r"""
import json, sys, time
sys.path.insert(0, sys.argv[1])
import networkx as nx
from pathwidth.solve import solve_masks, masks_from_graph
seed = json.load(open(sys.argv[2]))
G = nx.from_graph6_bytes(seed["g6"].encode())
masks, labels = masks_from_graph(G)
idx = {v: i for i, v in enumerate(labels)}
t = time.time()
s = solve_masks(masks, upper=seed["width"], upper_order=[idx[v] for v in seed["order"]],
                lower=seed["lower"], time_budget=float(sys.argv[3]))
order = [labels[i] for i in s.order]
minor = s.minor
if minor is not None:
    minor["contractions"] = [[labels[v], labels[u] if u >= 0 else None] for v, u in minor["contractions"]]
print(json.dumps({"width": s.width, "lower": s.lower, "proof": s.proof, "nodes": s.nodes,
                  "seconds": time.time() - t, "order": order, "minor": minor}))
"""


def one(g, p1, order, cap):
    row = dict(graphId=g["graphId"], graphName=g["graphName"], n=g["n"], m=p1["m"],
               hog_tw=p1["hog_tw"], hog_tw_status=p1["hog_tw_status"], width="", lower="", proof="",
               nodes="", seconds="", status="", conflict="",
               width_pass1=p1["width"], lower_pass1=p1["lower"])
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump({"g6": g["canonicalForm"], "width": int(p1["width"]), "lower": int(p1["lower"]),
                   "order": order}, f)
        seed = f.name
    t = time.time()
    try:
        out = subprocess.run([sys.executable, "-c", CHILD, str(ROOT), seed, str(cap)],
                             capture_output=True, text=True, timeout=cap + 60)
        if out.returncode == 0 and out.stdout.strip():
            r = json.loads(out.stdout.strip().splitlines()[-1])
            row.update(width=r["width"], lower=r["lower"], proof=r["proof"], nodes=r["nodes"],
                       seconds=round(r["seconds"], 3), status="ok")
            if row["hog_tw"] != "" and r["width"] < int(row["hog_tw"]):
                row["conflict"] = "width<tw"
            return row, {"graphId": g["graphId"], "width": r["width"], "proof": r["proof"],
                         "order": r["order"], "minor": r["minor"]}
        row.update(status="error", seconds=round(time.time() - t, 3), conflict=out.stderr.strip()[-120:])
    except subprocess.TimeoutExpired:
        row.update(status="killed", seconds=round(time.time() - t, 3))
    finally:
        Path(seed).unlink(missing_ok=True)
    return row, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=25)
    ap.add_argument("--time", type=float, default=300)
    a = ap.parse_args()
    p1 = {r["graphId"]: r for r in csv.DictReader(open(h1.CSV)) if r["status"] == "ok" and r["proof"] == ""}
    orders = {}
    for l in open(h1.WIT):
        w = json.loads(l)
        if str(w["graphId"]) in p1:
            orders[str(w["graphId"])] = w["order"]
    done = {r["graphId"] for r in csv.DictReader(open(CSV))} if CSV.exists() else set()
    graphs = [g for g in map(json.loads, open(h1.GRAPHS)) if str(g["graphId"]) in p1 and str(g["graphId"]) not in done]
    graphs.sort(key=lambda g: (int(p1[str(g["graphId"])]["width"]) - int(p1[str(g["graphId"])]["lower"]), g["n"]))
    print(f"{len(graphs)} to do, {len(done)} done", flush=True)
    new = not CSV.exists()
    with open(CSV, "a", newline="") as f, open(WIT, "a") as wf, ThreadPoolExecutor(a.procs) as ex:
        w = csv.DictWriter(f, FIELDS)
        if new:
            w.writeheader()
        futs = [ex.submit(one, g, p1[str(g["graphId"])], orders[str(g["graphId"])], a.time) for g in graphs]
        for i, fu in enumerate(as_completed(futs), 1):
            row, wit = fu.result()
            w.writerow(row); f.flush()
            if wit:
                wf.write(json.dumps(wit) + "\n"); wf.flush()
            if row["conflict"] or row["proof"] or i % 250 == 0:
                print(f"[{i}/{len(graphs)}] {row['graphId']} n={row['n']} w={row['width_pass1']}->{row['width']} "
                      f"lower {row['lower_pass1']}->{row['lower']} {row['proof']} {row['status']} {row['conflict']}", flush=True)


if __name__ == "__main__":
    main()
