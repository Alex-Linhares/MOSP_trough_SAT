"""Pass 1b: the open classes with no recorded layout (742; absent from the dataset's jsonl), loaded
through the dataset index as run_unlimited.py does; those with a component above the engine's
1,024-vertex limit are skipped.  Each: 60 s of the C program on the whole graph for a layout (closed
outright if it proves the width), then the ten-minute minor search of pass1.py.  Same outputs as
pass 1, in this directory with the `b` suffix.
"""
import csv, gzip, json, sys, time
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(Path(__file__).resolve().parent))
import pass1
from paper1.dataset import INDEX, VALUES_CSV, PRIORITY, ENGINE_MAX, class_order, representative, load, read_csv
HERE = Path(__file__).resolve().parent

def records():
    cls = {r["id"]: r for r in csv.DictReader(gzip.open(ROOT / "paper1/data/dataset/classes.csv.gz", "rt"))}
    in_jsonl = set()
    for line in gzip.open(ROOT / "paper1/data/dataset/pathwidth_dataset.jsonl.gz", "rt"):
        in_jsonl.add(json.loads(line)["id"])
    idx = [r for r in read_csv(INDEX) if not r["error"]]
    by = defaultdict(list)
    for r in idx: by[r["cls"]].append(r)
    for members in by.values(): members.sort(key=lambda r: (PRIORITY[r["collection"]], r["source"], r["name"]))
    ids = {f"pwc-{i + 1:05d}": c for i, c in enumerate(class_order(by))}
    base = {(v["source"], v["name"]): v for v in read_csv(VALUES_CSV) if not v["evidence"].startswith("reports/scratch/")}
    out = []
    for cid, c in cls.items():
        if c["provenance"].startswith("certified") or cid in in_jsonl or cid in pass1.SKIP: continue
        # blank max_component means the class was never measured (the `big` graphs, 6,040 to 24.6 M vertices);
        # the old `or 0` let all 78 of them through and one worker reached 74 GB (OOM-killed 2026-11-03 18:10)
        if not str(c["max_component"]).strip() or int(c["max_component"]) > ENGINE_MAX: continue
        if "Frinhani" in c["owner"]: continue   # owner, 2026-11-03: the dense Frinhani instances skipped after 24 (floors ~62% of a greedy width ~0.97 n)
        rep, _ = representative(by[ids[cid]], base)
        out.append((cid, c["collections"], rep))
    return out

def make_rec(t):
    cid, collections, rep = t
    n, edges = load(rep)
    return dict(id=cid, n=n, edges=[tuple(e) for e in edges], width=None, layout=[], names=pass1.Path(rep["name"]).name,
                collections=collections)

def job_lazy(t):
    return pass1.job(make_rec(t))


def main():
    todo = records()
    done = set(pd.read_csv(HERE / "pass1b.csv")["id"]) if (HERE / "pass1b.csv").exists() else set()
    todo = [t for t in todo if t[0] not in done]
    print(f"{time.strftime('%F %T')} pass 1b: {len(todo)} width-less open classes within the engine limit, 24 workers", flush=True)
    k = closed = 0
    with Pool(24) as pool:
        # each worker loads its own record just before running it (the eager two-stage version held
        # every edge list in the parent at once: 35 GB)
        for row in pool.imap_unordered(job_lazy, todo, chunksize=1):
            k += 1; closed += bool(row.get("closed"))
            pd.DataFrame([row]).to_csv(HERE / "pass1b.csv", mode="a", header=not (HERE / "pass1b.csv").exists(), index=False)
            if row.get("closed"):
                ev = {f: "" for f in pass1.FIELDS}
                ev.update(id=row["id"], collections=row["collections"].replace("; ", "|"), names=row["names"], n=row["n"], m=row["m"],
                          recorded=row["width"], started_from_layout=False, width=row["width"], proof=row["proof"], lower=row["width"],
                          nodes=row.get("c_whole_nodes", "") or 0, seconds=row["seconds"], finished=time.strftime("%Y-%m-%dT%H:%M:%S"),
                          status="ok", order=json.dumps(row["order"]), minor=row.get("minor", ""))
                pd.DataFrame([ev], columns=pass1.FIELDS).to_csv(HERE / "results_pass1b.csv", mode="a",
                                                                header=not (HERE / "results_pass1b.csv").exists(), index=False)
            print(f"{time.strftime('%T')} {k}/{len(todo)} {row['id']} {str(row['names'])[:28]:28} n={row['n']:5} width {row.get('width')} "
                  f"[C whole: {row.get('c_whole')}] floor {row.get('m_pathwidth')} ({row.get('search_m')} v) "
                  f"{'CLOSED ' + row['proof'] if row.get('closed') else ''} {row.get('seconds')}s  closed so far {closed}", flush=True)
    print(f"{time.strftime('%F %T')} pass 1b done: {k} classes, {closed} closed", flush=True)

if __name__ == "__main__":
    main()
