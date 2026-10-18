"""Validate ./pathwidth against the Python solver on a small House of Graphs sample.

The owner approved a small sample only (at most ~500 graphs, each already
proved by the first pass in under 5 s). The sample is stratified by proof
type and size band, drawn with a fixed seed from
bench/results/hog_pathwidth.csv, graph6 from bench/instances/hog/graphs.jsonl.

    nice -n 19 python tests/hog_sample.py select     # writes tests/hog_sample.txt
    nice -n 19 python tests/hog_sample.py run-c      # 4 processes, nice 19
    nice -n 19 python tests/hog_sample.py run-python # 4 processes, nice 19
    python tests/hog_sample.py compare               # widths, proofs, layouts, speed

Every process started is `nice -n 19`, at most four at a time.
"""
import csv
import json
import os
import random
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLI = HERE.parent
ROOT = CLI.parent
RESULTS = ROOT / "bench" / "results" / "hog_pathwidth.csv"
GRAPHS = ROOT / "bench" / "instances" / "hog" / "graphs.jsonl"
SAMPLE = HERE / "hog_sample.txt"
C_OUT = HERE / "hog_sample_c.jsonl"
PY_OUT = HERE / "hog_sample_python.jsonl"
PROCS = 4
PER_STRATUM = 36
BANDS = ((1, 19), (20, 39), (40, 64), (65, 128), (129, 10**9))


def band(n):
    return next(i for i, (lo, hi) in enumerate(BANDS) if lo <= n <= hi)


def select():
    rows = [r for r in csv.DictReader(open(RESULTS))
            if r["status"] == "ok" and r["proof"] and float(r["seconds"]) < 5.0]
    strata = defaultdict(list)
    for r in rows:
        strata[(r["proof"], band(int(r["n"])))].append(r)
    rng = random.Random(20261018)
    chosen = []
    for key in sorted(strata):
        group = sorted(strata[key], key=lambda r: int(r["graphId"]))
        chosen += rng.sample(group, min(PER_STRATUM, len(group)))
    ids = {int(r["graphId"]) for r in chosen}
    g6 = {}
    for line in open(GRAPHS):
        g = json.loads(line)
        if g["graphId"] in ids:
            g6[g["graphId"]] = g["canonicalForm"]
    chosen.sort(key=lambda r: int(r["graphId"]))
    with open(SAMPLE, "w") as f:
        for r in chosen:
            f.write(f"{r['graphId']} {g6[int(r['graphId'])]} {r['n']} {r['width']} {r['proof']} {r['seconds']}\n")
    print(len(chosen), "graphs;", Counter((r["proof"], BANDS[band(int(r["n"]))][0]) for r in chosen))


def load_sample():
    out = []
    for line in open(SAMPLE):
        gid, g6, n, width, proof, seconds = line.split()
        out.append(dict(id=int(gid), g6=g6, n=int(n), width=int(width), proof=proof, seconds=float(seconds)))
    return out


def run_c():
    sample = load_sample()
    chunks = [sample[i::PROCS] for i in range(PROCS)]
    import tempfile
    procs = []
    started = time.monotonic()
    for chunk in chunks:
        # files, not pipes: a full pipe would stall a process until we read it
        fin, fout, ferr = (tempfile.TemporaryFile("w+") for _ in range(3))
        fin.write("".join(g["g6"] + "\n" for g in chunk))
        fin.seek(0)
        p = subprocess.Popen(["nice", "-n", "19", str(CLI / "pathwidth"), "-l", "-v"],
                             stdin=fin, stdout=fout, stderr=ferr, text=True)
        procs.append((p, chunk, fout, ferr))
    for p, *_ in procs:
        p.wait()
    wall = time.monotonic() - started
    with open(C_OUT, "w") as f:
        for p, chunk, fout, ferr in procs:
            fout.seek(0)
            ferr.seek(0)
            out = fout.read().splitlines()
            err = ferr.read().splitlines()
            assert p.returncode == 0, (p.returncode, err[-3:])
            assert len(out) == 2 * len(chunk) and len(err) == len(chunk), (len(out), len(err), len(chunk))
            for i, g in enumerate(chunk):
                _, w, status = out[2 * i].split()
                layout = [int(x) for x in out[2 * i + 1].split()[1:]]
                stats = dict(kv.split("=") for kv in err[i].split()[2:])
                f.write(json.dumps(dict(id=g["id"], width=int(w), proof=status, layout=layout,
                                        nodes=int(stats["nodes"]), seconds=float(stats["seconds"]))) + "\n")
    print(f"C: {len(sample)} graphs in {wall:.1f} s wall on {PROCS} processes")


def _python_one(g):
    import networkx as nx
    from pathwidth import solve
    G = nx.from_graph6_bytes(g["g6"].encode())
    t = time.monotonic()
    s = solve(G, time_budget=300.0)
    return dict(id=g["id"], width=s.width, proof=s.proof or "upper", nodes=s.nodes,
                seconds=time.monotonic() - t)


def _init():
    os.nice(19)          # the pool workers start at nice 0 relative to us; keep them at 19
    sys.path.insert(0, str(ROOT))


def run_python():
    import multiprocessing as mp
    sample = load_sample()
    started = time.monotonic()
    with mp.get_context("spawn").Pool(PROCS, initializer=_init) as pool, open(PY_OUT, "w") as f:
        for r in pool.imap_unordered(_python_one, sample, chunksize=4):
            f.write(json.dumps(r) + "\n")
    print(f"Python: {len(sample)} graphs in {time.monotonic() - started:.1f} s wall on {PROCS} processes")


def vs_layout(n, edges, layout):
    """Textbook vertex separation of a layout, from the edge list."""
    pos = {v: i for i, v in enumerate(layout)}
    assert sorted(pos) == list(range(n)), "not a permutation"
    far = {v: pos[v] for v in range(n)}
    for u, v in edges:
        far[u] = max(far[u], pos[v])
        far[v] = max(far[v], pos[u])
    return max((sum(1 for v in range(n) if pos[v] <= i < far[v]) for i in range(n)), default=0)


def compare():
    import networkx as nx
    sample = {g["id"]: g for g in load_sample()}
    c = {r["id"]: r for r in map(json.loads, open(C_OUT))}
    py = {r["id"]: r for r in map(json.loads, open(PY_OUT))} if PY_OUT.exists() else {}
    width_bad, proof_bad, layout_bad = [], [], []
    for gid, g in sample.items():
        r = c[gid]
        G = nx.from_graph6_bytes(g["g6"].encode())
        if r["width"] != g["width"]:
            width_bad.append((gid, g["n"], g["width"], g["proof"], r["width"], r["proof"]))
        if r["proof"] != g["proof"]:
            proof_bad.append((gid, g["n"], g["width"], g["proof"], r["width"], r["proof"],
                              nx.number_connected_components(G)))
        if vs_layout(G.number_of_nodes(), list(G.edges), r["layout"]) != r["width"]:
            layout_bad.append(gid)
    print(f"{len(sample)} graphs; width mismatches {len(width_bad)}, proof mismatches {len(proof_bad)}, "
          f"layouts not achieving the width {len(layout_bad)}")
    for x in width_bad:
        print("WIDTH", x)
    for x in proof_bad:
        print("PROOF (id, n, first-pass width, proof, C width, proof, components)", x)
    print("by proof:", Counter(g["proof"] for g in sample.values()))
    print("n > 64:", sum(1 for g in sample.values() if g["n"] > 64),
          " n >= 40:", sum(1 for g in sample.values() if g["n"] >= 40))
    if py:
        same_nodes = sum(1 for gid in sample if py[gid]["nodes"] == c[gid]["nodes"])
        pw = sum(1 for gid in sample if py[gid]["width"] != c[gid]["width"])
        pp = sum(1 for gid in sample if py[gid]["proof"] != c[gid]["proof"])
        print(f"against a fresh Python run: width differs {pw}, proof differs {pp}, "
              f"identical node counts {same_nodes}/{len(sample)}")
        for gid in sample:
            if py[gid]["nodes"] != c[gid]["nodes"]:
                print("  nodes differ", gid, sample[gid]["n"], py[gid]["nodes"], c[gid]["nodes"])
        tc = sum(c[g]["seconds"] for g in sample)
        tp = sum(py[g]["seconds"] for g in sample)
        print(f"solve time, sum over the sample: C {tc:.2f} s, Python {tp:.2f} s, ratio {tp / tc:.1f}x")
        for i, (lo, hi) in enumerate(BANDS):
            ids = [g for g in sample if band(sample[g]["n"]) == i]
            if ids:
                a = sum(c[g]["seconds"] for g in ids)
                b = sum(py[g]["seconds"] for g in ids)
                print(f"  n {lo}-{min(hi, 250)}: {len(ids)} graphs, C {a:.2f} s, Python {b:.2f} s, "
                      f"ratio {b / a if a else float('inf'):.1f}x")


if __name__ == "__main__":
    {"select": select, "run-c": run_c, "run-python": run_python, "compare": compare}[sys.argv[1]]()
