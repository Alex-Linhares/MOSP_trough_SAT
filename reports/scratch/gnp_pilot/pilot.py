"""Pilot: exact pathwidth of Erdős–Rényi G(n, c/n), to price the full measurement.

Grid: c in {0.5, 1, 1.5, 2, 3, 4, 6, 8, 10}, n in {20, 30, 40, 50, 60}, samples
drawn round-robin over the cells (smallest n first), seeds recorded so every
graph regenerates. Each graph goes to the C program (pathwidth_solver/cli) in
its own process with a 240 s limit; new graphs stop being started at 55 min, so
the pilot ends within about an hour. Run under nice:
    nice -n 19 python reports/scratch/gnp_pilot/pilot.py --procs 14
Output (resumable by key): results.csv, with the witness layout for every graph.
New graphs only: none of these has ever been solved.
"""
import argparse, csv, subprocess, time, threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import networkx as nx

HERE = Path(__file__).resolve().parent
BIN = HERE.parents[2] / "pathwidth_solver/cli/pathwidth"
OUT = HERE / "results.csv"
CS = [0.5, 1, 1.5, 2, 3, 4, 6, 8, 10]
NS = [20, 30, 40, 50, 60, 70, 80, 90, 100, 120]
FIELDS = ["n", "c", "sample", "seed", "m", "components", "width", "status", "lower", "nodes", "seconds", "layout"]


def jobs():
    for s in range(1000):  # 2026-10-18: sizes 70-120 added after the first 2 min priced 20-60 at seconds
        for n in sorted(NS, key=lambda n: -n if n > 60 else n + 1000):
            for c in CS:
                yield n, c, s, 1_000_003 * n + 1_009 * int(c * 10) + s


def one(n, c, s, seed, cap):
    G = nx.gnp_random_graph(n, c / n, seed=seed)
    g6 = nx.to_graph6_bytes(G, header=False)
    t = time.time()
    row = dict(n=n, c=c, sample=s, seed=seed, m=G.number_of_edges(),
               components=nx.number_connected_components(G), width="", status="", lower="",
               nodes="", seconds="", layout="")
    try:
        p = subprocess.run([str(BIN), "-t", str(cap), "-l", "-v"], input=g6, capture_output=True, timeout=cap + 60)
        out = p.stdout.decode().split("\n")
        _, w, st = out[0].split()
        err = dict(kv.split("=") for kv in p.stderr.decode().split() if "=" in kv)
        row.update(width=int(w), status=st, lower=err.get("lower", ""), nodes=err.get("nodes", ""),
                   seconds=round(time.time() - t, 3), layout=out[1].split(" ", 1)[1] if len(out) > 1 and out[1] else "")
    except subprocess.TimeoutExpired:
        row.update(status="killed", seconds=round(time.time() - t, 3))
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=14)
    ap.add_argument("--cap", type=float, default=240)
    ap.add_argument("--stop-after", type=float, default=55 * 60)
    a = ap.parse_args()
    done = {(int(r["n"]), float(r["c"]), int(r["sample"])) for r in csv.DictReader(open(OUT))} if OUT.exists() else set()
    new = not OUT.exists()
    f = open(OUT, "a", newline=""); w = csv.DictWriter(f, FIELDS)
    if new: w.writeheader(); f.flush()
    lock = threading.Lock(); start = time.time()
    it = (j for j in jobs() if (j[0], j[1], j[2]) not in done)

    def worker():
        while time.time() - start < a.stop_after:
            with lock:
                j = next(it, None)
            if j is None: return
            row = one(*j, a.cap)
            with lock:
                w.writerow(row); f.flush()

    with ThreadPoolExecutor(a.procs) as ex:
        for _ in range(a.procs): ex.submit(worker)
    f.close()


if __name__ == "__main__":
    main()
