"""The dataset's open classes, no time limit, the C program (2026-10-21, owner's request:
"the small Rome item first, B second, all threads nice, no time limit").

Queue: the one certified class with no stored witness (pwc-05529, Rome, width 9),
then every class whose provenance is not `certified:*`, with every component within
the C engine's limit (1,024 vertices), excluding the 610 Frinhani et al. (2018)
instances of 400 to 1,000 customers (a core each, forever, with no time limit).
Cheapest first: by recorded width, then vertices. Each class runs in its own
`nice -n 19` process of `pathwidth_solver/cli/pathwidth -t 0 -l -v`, started from
the recorded witness (`-u`) where the graph is connected and the witness checks.

Rows are written to results_unlimited.csv in the format `paper1.dataset.fold`
reads (OPEN_RUNS): `order` is the closing order in the representative's labels
(the C prints the textbook layout, which is the closing order reversed; both
orientations are checked with the dataset's own width function and the one of
the printed width is kept), `minor` is the certificate the C prints. Resumable:
classes with a row are skipped. The representative is the member the previous
build used, computed as `fold` does, from the values on record before the fold.

    nohup nice -n 19 python3 reports/scratch/dataset_open/run_unlimited.py --procs 24 > run_unlimited.log 2>&1 &
    python3 reports/scratch/dataset_open/run_unlimited.py --only pwc-05529   # one class, in the foreground
"""
from __future__ import annotations

import csv
import gzip
import json
import re
import subprocess
import sys
import tempfile
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from paper1.dataset import (INDEX, VALUES_CSV, OUT, PRIORITY, ENGINE_MAX, class_order,   # noqa: E402
                            representative, load, layout_width, read_csv)

CLI = ROOT / "pathwidth_solver" / "cli" / "pathwidth"
RESULTS = HERE / "results_unlimited.csv"
FIELDS = ["id", "collections", "names", "n", "m", "recorded", "started_from_layout", "width", "proof",
          "lower", "nodes", "seconds", "finished", "status", "order", "minor"]
FIRST = ["pwc-05529"]                      # the Rome class proved without a stored witness
EXCLUDE_OWNER = {"MOSP: Frinhani et al. 2018, large"}


def stem(s: str) -> str:
    return re.sub(r"(\.mtx)?\.(dgf|gr|rnd|graphml|txt)$", "", Path(s).name)


def graph6(n: int, edges) -> str:
    import networkx as nx
    G = nx.Graph(); G.add_nodes_from(range(n)); G.add_edges_from(edges)
    return nx.to_graph6_bytes(G, header=False).decode().strip()


def connected(n: int, edges) -> bool:
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v); adj[v].append(u)
    seen, stack = {0}, [0]
    while stack:
        for w in adj[stack.pop()]:
            if w not in seen:
                seen.add(w); stack.append(w)
    return len(seen) == n


def classes() -> list[dict]:
    """(class record, representative member, recorded layout or None) for the queue."""
    idx = [r for r in read_csv(INDEX) if not r["error"]]
    by: dict[str, list[dict]] = defaultdict(list)
    for r in idx:
        by[r["cls"]].append(r)
    for members in by.values():
        members.sort(key=lambda r: (PRIORITY[r["collection"]], r["source"], r["name"]))
    ids = {f"pwc-{i + 1:05d}": c for i, c in enumerate(class_order(by))}
    # the values on record before the fold: the folded rows carry a reports/scratch/ evidence
    base = {(v["source"], v["name"]): v for v in read_csv(VALUES_CSV)
            if not v["evidence"].startswith("reports/scratch/")}
    recorded = {}
    for line in gzip.open(OUT / "pathwidth_dataset.jsonl.gz", "rt"):
        d = json.loads(line)
        recorded[d["id"]] = d
    out = []
    for c in read_csv(OUT / "classes.csv.gz"):
        proved = c["provenance"].startswith("certified")
        if c["id"] in FIRST:
            pass
        elif proved or c["owner"] in EXCLUDE_OWNER or int(c["max_component"] or 0) > ENGINE_MAX:
            continue
        rep, _ = representative(by[ids[c["id"]]], base)
        out.append((c, rep, recorded.get(c["id"])))
    def key(t):
        c = t[0]
        return (0 if c["id"] in FIRST else 1, int(c["width"] or 10**6), int(c["n"]), c["id"])
    out.sort(key=key)
    return out


def run_one(c: dict, rep: dict, rec: dict | None) -> dict:
    n, edges = load(rep)
    edges = [tuple(e) for e in edges]
    members = "|".join(sorted({m for m in c["collections"].split("|")}))
    row = dict(id=c["id"], collections=members, names=stem(rep["name"]), n=n, m=len(edges),
               recorded=c["width"] or n, started_from_layout=False, width="", proof="", lower="",
               nodes="", seconds="", finished="", status="", order="", minor="")
    args = [str(CLI), "-t", "0", "-l", "-v"]
    tmp = None
    if rec and rec.get("layout") and c["width"] and connected(n, edges):
        lay = list(rec["layout"])
        if sorted(lay) == list(range(n)):
            # the stored witness, in the representative's labels already (the record's graph is it)
            for cand in (lay, lay[::-1]):
                if layout_width(n, edges, cand) == int(c["width"]) and (n, len(edges)) == (rec["n"], rec["m"]):
                    tmp = tempfile.NamedTemporaryFile("w", suffix=".order", delete=False)
                    tmp.write(" ".join(map(str, cand)) + "\n"); tmp.close()
                    args += ["-u", tmp.name]
                    row["started_from_layout"] = True
                    break
    t = time.time()
    try:
        p = subprocess.run(["nice", "-n", "19"] + args, input=graph6(n, edges) + "\n",
                           capture_output=True, text=True)
    finally:
        if tmp:
            Path(tmp.name).unlink(missing_ok=True)
    row["seconds"] = round(time.time() - t, 1)
    row["finished"] = f"{datetime.now():%Y-%m-%dT%H:%M:%S}"
    m = re.search(r"^pathwidth (-?\d+) (\w+)$", p.stdout, re.M)
    if p.returncode != 0 or not m:
        row["status"] = "error: " + (p.stderr.strip()[-200:] or p.stdout.strip()[-200:])
        return row
    w, status = int(m.group(1)), m.group(2)
    lay = re.search(r"^layout((?: \d+)+)$", p.stdout, re.M)
    printed = list(map(int, lay.group(1).split())) if lay else []
    order = next((o for o in (printed[::-1], printed) if layout_width(n, edges, o) == w), None)
    if order is None:
        row["status"] = "error: printed layout does not have the printed width under the dataset's convention"
        row["width"] = w
        return row
    v = dict(re.findall(r"(\w+)=([\d.]+)", p.stderr))
    cert = None
    mc = re.search(r"^minor refuted (\d+) size (\d+) rule (\S+) contractions((?: -?\d+,-?\d+)*)$", p.stdout, re.M)
    if mc:
        pairs = [[int(a), None if int(b) < 0 else int(b)] for a, b in
                 (x.split(",") for x in mc.group(4).split())]
        cert = dict(refuted=int(mc.group(1)), size=int(mc.group(2)), rule=mc.group(3),
                    contractions=pairs, nodes=int(v.get("minor_nodes", 0)))
    row.update(width=w, proof="" if status == "upper" else status, lower=v.get("lower", ""),
               nodes=v.get("nodes", ""), status="ok", order=json.dumps(order),
               minor=json.dumps(cert) if cert else "")
    return row


def main() -> None:
    procs = int(sys.argv[sys.argv.index("--procs") + 1]) if "--procs" in sys.argv else 1
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    queue = classes()
    if only:
        queue = [t for t in queue if t[0]["id"] == only]
    done = {r["id"] for r in csv.DictReader(open(RESULTS))} if RESULTS.exists() else set()
    queue = [t for t in queue if t[0]["id"] not in done]
    new = not RESULTS.exists()
    print(f"{datetime.now():%Y-%m-%d %H:%M:%S} {len(queue)} classes, {procs} workers, no time limit", flush=True)
    with open(RESULTS, "a", newline="") as f, ThreadPoolExecutor(procs) as ex:
        w = csv.DictWriter(f, FIELDS)
        if new:
            w.writeheader(); f.flush()
        futs = {ex.submit(run_one, *t): t[0]["id"] for t in queue}
        for fut in as_completed(futs):
            try:
                row = fut.result()
            except Exception as e:                     # a loader or encoder failure: record it, carry on
                row = dict.fromkeys(FIELDS, "")
                row.update(id=futs[fut], status=f"error: {e!r}"[:200], finished=f"{datetime.now():%Y-%m-%dT%H:%M:%S}")
            w.writerow(row); f.flush()
            print(f"{datetime.now():%Y-%m-%d %H:%M:%S} {row['id']} {str(row['names'])[:40]} n={row['n']} "
                  f"recorded={row['recorded']} width={row['width']} proof={row['proof']!r} {row['status']} "
                  f"{row['seconds']}s", flush=True)


if __name__ == "__main__":
    main()
