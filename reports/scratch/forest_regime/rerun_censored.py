"""Item 03 (b): the random block trees censored at 600 s re-run for 3600 s each, restarted from their stored
layout (-u, the closing order = the layout reversed) and the clique floor (-L omega-1), two at a time under
nice 19. Writes random_censored_rerun.csv; a run still censored is an interval [lower, upper], never a value.
    cd /home/al/dev/MOSP && nice -n 19 python3 reports/scratch/forest_regime/rerun_censored.py
"""
import csv, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
from learning.block_trees import PATHWIDTH_BIN, graph6, mosp_graph, random_block_tree, vertex_separation
TIMEOUT = 3600
rows = [r for r in csv.DictReader(open(HERE / "random_block_trees.csv")) if r["status"] == "upper"]
layouts = {line.split()[0]: [int(x) for x in line.split()[1:]] for line in open(HERE / "random_layouts.txt")}


def job(r):
    n, d, i, seed = int(r["n"]), int(r["d"]), int(r["index"]), int(r["seed"])
    P = random_block_tree(n, d, seed); G = mosp_graph(P)
    name = f"RBT_n{n}_d{d}_i{i:02d}"
    layout = layouts[name]
    assert vertex_separation(G, layout) == int(r["pw"])
    order = HERE / f"{name}.closing"
    order.write_text(" ".join(map(str, reversed(layout))) + "\n")
    floor = int(r["omega"]) - 1
    cmd = ["nice", "-n", "19", str(PATHWIDTH_BIN), "-t", str(TIMEOUT), "-l", "-v", "-u", str(order), "-L", str(floor)]
    t0 = time.time()
    proc = subprocess.run(cmd, input=graph6(G) + "\n", capture_output=True, text=True)
    out = proc.stdout.strip().splitlines(); head = out[0].split()
    m = re.search(r"nodes=(\d+).*?seconds=([\d.]+)", proc.stderr)
    res = {"name": name, "n": n, "d": d, "index": i, "seed": seed, "omega": r["omega"], "pw_600s": r["pw"],
           "floor": floor, "width": int(head[1]), "status": head[2], "nodes": int(m.group(1)) if m else None,
           "seconds": float(m.group(2)) if m else None, "wall": round(time.time() - t0, 1), "stderr": proc.stderr.strip()[:300]}
    if len(out) > 1 and out[1].startswith("layout"):
        lay = [int(x) for x in out[1].split()[1:]]
        assert vertex_separation(G, lay) == res["width"]
        (HERE / f"{name}.layout_rerun").write_text(" ".join(map(str, lay)) + "\n")
    print(res, flush=True)
    return res


with ThreadPoolExecutor(max_workers=2) as pool:
    results = list(pool.map(job, rows))
with open(HERE / "random_censored_rerun.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(results[0].keys())); w.writeheader(); w.writerows(results)
print("done")
