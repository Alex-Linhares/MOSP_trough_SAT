"""Benchmark runner: `python bench/run.py SET [--time 600] [--procs 32]`.

Writes `bench/results/SET.csv` incrementally (one row per graph as it
finishes) and prints a summary. Graphs above 128 vertices run on the Python
search (the C declines), which the `engine` column records.
"""

from __future__ import annotations

import argparse
import csv
import multiprocessing as mp
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from readers import SETS, read_any  # noqa: E402

FIELDS = ["set", "name", "n", "m", "engine", "lower", "upper_start", "width", "proof", "nodes", "seconds", "components"]


def one(args):
    setname, path, time_limit = args
    from pathwidth import solve
    from pathwidth.native import MAX_VERTICES
    G = read_any(path)
    n, m = G.number_of_nodes(), G.number_of_edges()
    biggest = max((len(c) for c in __import__("networkx").connected_components(G)), default=0)
    engine = "C" if biggest <= MAX_VERTICES else "python"
    t = time.perf_counter()
    try:
        sol = solve(G, time_budget=time_limit)
        row = dict(set=setname, name=path.stem.replace(".mtx", ""), n=n, m=m, engine=engine,
                   lower=sol.lower, upper_start=sol.upper_start, width=sol.width,
                   proof=sol.proof or "budget", nodes=sol.nodes, seconds=round(time.perf_counter() - t, 3),
                   components=len(sol.components) or 1)
    except Exception as exc:  # keep the sweep alive
        row = dict(set=setname, name=path.stem, n=n, m=m, engine=engine, lower="", upper_start="",
                   width="", proof=f"error: {type(exc).__name__}: {exc}"[:80], nodes="",
                   seconds=round(time.perf_counter() - t, 3), components="")
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("set", choices=sorted(SETS))
    ap.add_argument("--time", type=float, default=600.0, help="per-graph wall-clock budget (s)")
    ap.add_argument("--procs", type=int, default=min(32, mp.cpu_count()))
    ap.add_argument("--limit", type=int, default=None, help="only the first N graphs")
    ap.add_argument("--out", default=None)
    ap.add_argument("--names", default=None, help="file with one graph stem per line: run only those")
    a = ap.parse_args()
    paths = SETS[a.set]()
    if a.names:
        wanted = set(Path(a.names).read_text().split())
        paths = [p for p in paths if p.stem.replace(".mtx", "") in wanted]
    if a.limit:
        paths = paths[:a.limit]
    out = Path(a.out) if a.out else Path(__file__).resolve().parent / "results" / f"{a.set}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    started = time.time()
    done = proved = 0
    with out.open("w", newline="") as fh, mp.Pool(a.procs) as pool:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for row in pool.imap_unordered(one, [(a.set, p, a.time) for p in paths], chunksize=1):
            w.writerow(row)
            fh.flush()
            done += 1
            proved += row["proof"] in ("refutation", "bound")
            if a.set != "rome" or done % 100 == 0 or a.names:
                print(f"[{done}/{len(paths)}] {row['name']:24s} n={row['n']:<4} pw={row['width']!s:>3} "
                      f"{row['proof']:11s} {row['nodes']!s:>12} {row['seconds']:>8}s {row['engine']}", flush=True)
    print(f"done: {done} graphs, {proved} proved, {time.time()-started:.0f}s wall -> {out}")


if __name__ == "__main__":
    main()
