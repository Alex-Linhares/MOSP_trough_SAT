"""Witness layouts for the 25 Rome classes whose width w is proved on a minor but whose
stored layout has width w + 1 (the run that reached w kept no layout). Owner's request,
2026-10-14. One satisfiable search per graph, `decide_pathwidth(G, w)` (no minor step),
in its own process, 15 minutes at most; the order is checked here with the dataset's
own width function before it is written. Results feed paper1/dataset.py's fold.
    python reports/scratch/rome_witness/run.py --procs 10
"""
import csv, gzip, json, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CHILD = r'''
import json, sys
sys.path.insert(0, sys.argv[1]); sys.path.insert(0, sys.argv[1] + "/pathwidth_solver")
import networkx as nx
import paper1.dataset as ds
from pathwidth.search import decide_pathwidth
m = json.loads(sys.argv[2]); w = int(sys.argv[3])
n, edges = ds.load(m)
G = nx.Graph(); G.add_nodes_from(range(n)); G.add_edges_from(edges)
d = decide_pathwidth(G, w)
order = d.order
ok = None
if order is not None:
    for o in (order, order[::-1]):
        if ds.layout_width(n, edges, o) == w:
            ok = o; break
print(json.dumps(dict(status=d.status, nodes=d.nodes, layout=ok)))
'''


def one(r):
    t = time.time()
    try:
        out = subprocess.run([sys.executable, "-c", CHILD, str(ROOT), json.dumps(r["member"]), r["width"]],
                             capture_output=True, text=True, timeout=900)
        d = json.loads(out.stdout.strip().splitlines()[-1]) if out.returncode == 0 else dict(status="error: " + out.stderr[-200:])
    except subprocess.TimeoutExpired:
        d = dict(status="killed at 900 s")
    return dict(name=r["name"], source=r["source"], width=r["width"], status=d["status"], nodes=d.get("nodes", ""),
                seconds=round(time.time() - t, 1), layout=json.dumps(d.get("layout")) if d.get("layout") else "")


def main():
    sys.path.insert(0, str(ROOT))
    import paper1.dataset as ds
    idx = {(r["source"], r["name"]): r for r in ds.read_csv(ds.INDEX)}
    todo = [dict(name=r["name"], source=r["source"], width=r["width"], member=idx[(r["source"], r["name"])])
            for r in csv.DictReader(gzip.open(ROOT / "paper1/data/dataset/values.csv.gz", "rt"))
            if r["provenance"] == "certified:minor" and not r["layout"]]
    out = HERE / "results.csv"
    procs = int(sys.argv[sys.argv.index("--procs") + 1]) if "--procs" in sys.argv else 10
    with open(out, "w", newline="") as f, ThreadPoolExecutor(procs) as ex:
        w = csv.DictWriter(f, ["name", "source", "width", "status", "nodes", "seconds", "layout"]); w.writeheader()
        for fut in as_completed([ex.submit(one, r) for r in todo]):
            row = fut.result(); w.writerow(row); f.flush()
            print(row["name"], row["width"], row["status"], row["seconds"], "witness" if row["layout"] else "-", flush=True)


if __name__ == "__main__":
    main()
