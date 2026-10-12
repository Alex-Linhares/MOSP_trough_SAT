"""The 48 Rome graphs still open after the minor step, no time limit.

Started 2026-10-12 on one core. The solver is a frozen snapshot of
pathwidth_solver/pathwidth at the time (minor step on by default; code hash in
code_snapshot/CODE_HASH), so edits to the live solver cannot change the run.
Graphs are taken smallest first from reports/scratch/minor_bound/rome_open_step.csv
(closed == False). Resumable: names already in results.csv are skipped.
Each row: name, n, m, width, proof, lower, nodes, seconds, order (the layout).
Ran one at a time from 03:04; from 2026-10-12 03:50 on 10 workers (one graph per
process, spawn context), smallest graphs first.
    python reports/scratch/rome_unlimited/run.py [--procs 10]
"""
import csv, json, sys, time
from datetime import datetime
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE / "code_snapshot"))
sys.path.insert(0, str(ROOT / "pathwidth_solver" / "bench"))
from pathwidth import solve          # the snapshot
from readers import HERE as INST, read_any

import multiprocessing as mp


def one(r):
    G = read_any(INST / r["name"])
    t = time.time()
    s = solve(G)
    return dict(name=r["name"], n=G.number_of_nodes(), m=G.number_of_edges(), width=s.width,
                proof=s.proof, lower=s.lower, nodes=s.nodes, seconds=round(time.time() - t, 1),
                finished=f"{datetime.now():%Y-%m-%dT%H:%M:%S}", order=json.dumps(list(s.order)))


def main():
    procs = int(sys.argv[sys.argv.index("--procs") + 1]) if "--procs" in sys.argv else 1
    todo = [r for r in csv.DictReader(open(ROOT / "reports/scratch/minor_bound/rome_open_step.csv")) if r["closed"] == "False"]
    todo.sort(key=lambda r: (int(r["n"]), r["name"]))
    out = HERE / "results.csv"
    done = {r["name"] for r in csv.DictReader(open(out))} if out.exists() else set()
    todo = [r for r in todo if r["name"] not in done]
    fields = ["name", "n", "m", "width", "proof", "lower", "nodes", "seconds", "finished", "order"]
    new = not out.exists()
    with open(out, "a", newline="") as f, mp.get_context("spawn").Pool(procs, maxtasksperchild=1) as pool:
        w = csv.DictWriter(f, fields)
        if new:
            w.writeheader()
        print(f"{datetime.now():%Y-%m-%d %H:%M:%S} {len(todo)} graphs on {procs} workers", flush=True)
        for row in pool.imap_unordered(one, todo):
            w.writerow(row); f.flush()
            print(f"{datetime.now():%Y-%m-%d %H:%M:%S} done  {row['name']} width={row['width']} "
                  f"proof={row['proof']!r} {row['seconds']:.0f}s", flush=True)


if __name__ == "__main__":
    main()
