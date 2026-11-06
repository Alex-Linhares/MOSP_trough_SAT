#!/usr/bin/env python3
"""The open Rome graphs through the C program, many at a time, resumable.

The owner's rule (CLAUDE.md, 2026-10-18): pathwidth runs use the C program
`pathwidth_solver/cli/pathwidth`, never the Python solver. `bench/run.py`
drives the Python, so this driver exists for the C: each graph is converted
to graph6 and piped to `pathwidth -t T -l -v`, under `nice -n 19`, `--procs`
at a time, with a hard kill at 1.5 T + 120 s. One CSV row per graph, appended
as it finishes; `--resume` skips names already in the CSV.

    python3 pathwidth_solver/bench/rome_open_c.py --names results/rome_open_351.txt \
        --time 3600 --procs 24 --out results/rome_open_c_3600s.csv --resume
"""
from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from readers import read_any  # noqa: E402

CLI = HERE.parent / "cli" / "pathwidth"
INSTANCES = HERE / "instances" / "rome" / "rome"
FIELDS = ["name", "n", "m", "width", "status", "lower", "upper_start", "nodes", "minor_nodes",
          "seconds", "time_budget", "layout", "error"]


def graph6_of(path: Path) -> tuple[bytes, int, int]:
    G = read_any(path)
    G = nx.convert_node_labels_to_integers(G)
    return nx.to_graph6_bytes(G, header=False), G.number_of_nodes(), G.number_of_edges()


def run_one(name: str, budget: float, hard: float) -> dict:
    path = INSTANCES / f"{name}.graphml"
    row = {k: "" for k in FIELDS}
    row.update(name=name, time_budget=budget)
    try:
        g6, n, m = graph6_of(path)
        row.update(n=n, m=m)
        t0 = time.monotonic()
        proc = subprocess.run(["nice", "-n", "19", str(CLI), "-t", str(budget), "-l", "-v"],
                              input=g6, capture_output=True, timeout=hard)
        row["seconds"] = round(time.monotonic() - t0, 1)
        out = proc.stdout.decode(errors="replace").split("\n")
        err = proc.stderr.decode(errors="replace").strip().split("\n")
        for line in out:
            if line.startswith("pathwidth "):
                _, w, st = line.split()[:3]
                row.update(width=int(w), status=st)
            elif line.startswith("layout "):
                row["layout"] = line[len("layout "):].strip()
        # -v on stderr: n, width, status, lower, upper_start, nodes, minor nodes, calls, seconds
        for line in err:
            parts = line.split()
            if len(parts) >= 8 and parts[0].isdigit():
                row.update(lower=parts[3], upper_start=parts[4], nodes=parts[5], minor_nodes=parts[6])
        if proc.returncode != 0 and not row["status"]:
            row["error"] = f"exit {proc.returncode}: {err[-1][:120] if err else ''}"
    except subprocess.TimeoutExpired:
        row.update(status="killed", error=f"hard kill at {hard:.0f} s")
    except Exception as exc:  # noqa: BLE001
        row["error"] = str(exc)[:160]
    return row


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--names", required=True)
    ap.add_argument("--time", type=float, default=3600.0)
    ap.add_argument("--hard", type=float, default=None)
    ap.add_argument("--procs", type=int, default=24)
    ap.add_argument("--out", required=True)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--skip-proved-from", nargs="*", help="earlier result CSVs whose proved graphs are skipped")
    a = ap.parse_args()
    hard = a.hard or (1.5 * a.time + 120)
    names = [l.strip() for l in open(a.names) if l.strip()]
    out = Path(a.out)
    done = set()
    if a.resume and out.exists():
        done = {r["name"] for r in csv.DictReader(open(out))}
    for prev in a.skip_proved_from or []:   # names proved in an earlier run, at any budget
        done |= {r["name"] for r in csv.DictReader(open(prev)) if r["status"] in ("refutation", "bound", "minor")}
    todo = [n for n in names if n not in done]
    print(f"{time.strftime('%F %T')} rome_open_c: {len(todo)} graphs ({len(done)} done), -t {a.time:.0f}, hard {hard:.0f}, {a.procs} at a time", flush=True)
    new = not out.exists() or out.stat().st_size == 0
    k = closed = 0
    with open(out, "a", newline="") as fh, ThreadPoolExecutor(a.procs) as pool:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        if new:
            w.writeheader()
        futs = {pool.submit(run_one, n, a.time, hard): n for n in todo}
        for fut in as_completed(futs):
            row = fut.result()
            w.writerow(row); fh.flush()
            k += 1; closed += row["status"] in ("refutation", "bound", "minor")
            print(f"{time.strftime('%T')} {k}/{len(todo)} {row['name']:16} n={row['n']:>3} m={row['m']:>3} "
                  f"width {row['width']} {row['status']:10} lower {row['lower']} nodes {row['nodes']} "
                  f"{row['seconds']}s  proved so far {closed} {row['error']}", flush=True)
    print(f"{time.strftime('%F %T')} done: {k} graphs, {closed} proved", flush=True)


if __name__ == "__main__":
    main()
