"""Pass 2 (owner, 2026-11-03 evening): one hour of minor search each, 12 niced workers, over the open classes
nearest to closing — every class pass 1 (600 s) left one to three stacks short of its recorded width, and the 21
classes of the unlimited run still open after the ten-minute pass (12_tenmin; floors width − 1 on 20, width − 2 on
494_bus).  Nearest first (gap, then n).  New seed (13); same minor range (40–90% of n, <= 1,000 vertices), same C
cap (20 s), same job as pass 1 (`pass1.job`).  Each worker runs under a 10 GB address-space limit (a MemoryError
becomes an error row instead of a SIGKILL that would hang the pool), and the launch is wrapped in a systemd scope:
    cd ~/dev/MOSP && systemd-run --user --scope -p MemoryMax=80G setsid nohup nice -n 19 python3 \\
        reports/scratch/obstruction_search/13_pass1/pass2.py > reports/scratch/obstruction_search/13_pass1/pass2.log 2>&1 &
Outputs, same formats as pass 1: pass2.csv, certificates_2/<id>/, results_pass2.csv (closures, run_unlimited.py's format).
"""
import csv, gzip, json, resource, sys, time
from multiprocessing import Pool
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(Path(__file__).resolve().parent))
import pass1
HERE = Path(__file__).resolve().parent
pass1.SEARCH_S, pass1.SEED = 3600.0, 13
pass1.CERT = HERE / "certificates_2"; pass1.CERT.mkdir(exist_ok=True)
CLOSED_ELSEWHERE = {"pwc-15933", "pwc-17632", "pwc-17381"}
WORKER_AS_BYTES = 10 * 2**30

def targets():
    """(id, gap) for the classes to run: pass 1's open rows at gap <= 3, and the unlimited run's 21 still open."""
    rows = list(csv.reader(open(HERE / "pass1.csv"))); hdr = rows[0]
    out = {}
    for r in rows[1:]:
        r = dict(zip(hdr, r))
        if r["closed"] == "True" or not r["m_pathwidth"]: continue
        gap = int(float(r["width"])) - int(float(r["m_pathwidth"]))
        if gap <= 3: out[r["id"]] = gap
    ten = {r["id"]: r for r in csv.DictReader(open(HERE.parent / "12_tenmin" / "open" / "minor.csv"))}
    for r in csv.DictReader(open(ROOT / "reports/scratch/dataset_open/unsolved_unlimited.csv")):
        cid = r["id_now"]
        if cid in CLOSED_ELSEWHERE: continue
        t = ten.get(cid)
        out[cid] = (int(t["width"]) - int(t["m_pathwidth"])) if t and t.get("m_pathwidth") else 9
    return out

def init():
    resource.setrlimit(resource.RLIMIT_AS, (WORKER_AS_BYTES, WORKER_AS_BYTES))

def job(rec):
    try:
        return pass1.job(rec)
    except MemoryError:
        return dict(id=rec["id"], names=rec["names"], collections=rec["collections"], n=rec["n"], m=len(rec["edges"]),
                    recorded_width=rec.get("width"), width=rec.get("width"), closed=False, status="error: MemoryError (10 GB limit)")

def main():
    want = targets()
    recs = []
    for line in gzip.open(ROOT / "paper1/data/dataset/pathwidth_dataset.jsonl.gz", "rt"):
        d = json.loads(line)
        if d["id"] not in want: continue
        if str(d.get("provenance", "")).startswith("certified"): continue
        mem = d.get("members") or [{}]; m0 = mem[0] if isinstance(mem[0], dict) else {"name": str(mem[0])}
        d["names"] = str(m0.get("name", d["id"])); d["collections"] = "; ".join(sorted({m.get("collection", "") for m in mem if isinstance(m, dict)}))
        d["gap"] = want[d["id"]]; recs.append(d)
    recs.sort(key=lambda d: (d["gap"], int(d["n"])))
    done = set(pd.read_csv(HERE / "pass2.csv")["id"]) if (HERE / "pass2.csv").exists() else set()
    recs = [d for d in recs if d["id"] not in done]
    from collections import Counter
    print(f"{time.strftime('%F %T')} pass 2: {len(recs)} classes (gaps {dict(sorted(Counter(d['gap'] for d in recs).items()))}), "
          f"12 workers, {pass1.SEARCH_S:.0f} s search each, seed {pass1.SEED}, C cap {pass1.C_CAP} s, 10 GB per worker", flush=True)
    k = closed = 0
    with Pool(12, initializer=init) as pool:
        for row in pool.imap_unordered(job, recs, chunksize=1):
            k += 1; closed += bool(row.get("closed"))
            pd.DataFrame([row]).to_csv(HERE / "pass2.csv", mode="a", header=not (HERE / "pass2.csv").exists(), index=False)
            if row.get("closed"):
                ev = {f: "" for f in pass1.FIELDS}
                ev.update(id=row["id"], collections=row["collections"].replace("; ", "|"), names=row["names"], n=row["n"], m=row["m"],
                          recorded=row["recorded_width"] if row["recorded_width"] is not None else row["width"],
                          started_from_layout=row["had_layout"], width=row["width"], proof=row["proof"],
                          lower=row["width"], nodes=row.get("c_whole_nodes", "") or 0, seconds=row["seconds"],
                          finished=time.strftime("%Y-%m-%dT%H:%M:%S"), status="ok", order=json.dumps(row["order"]),
                          minor=row.get("minor", ""))
                pd.DataFrame([ev], columns=pass1.FIELDS).to_csv(HERE / "results_pass2.csv", mode="a",
                                                                header=not (HERE / "results_pass2.csv").exists(), index=False)
            print(f"{time.strftime('%T')} {k}/{len(recs)} {row['id']} {str(row['names'])[:28]:28} n={row['n']:5} width {row.get('width')} "
                  f"floor {row.get('m_pathwidth')} ({row.get('search_m')} v) {'CLOSED ' + row['proof'] if row.get('closed') else ''} "
                  f"{row.get('seconds')}s {row.get('status')}  closed so far {closed}", flush=True)
    print(f"{time.strftime('%F %T')} pass 2 done: {k} classes, {closed} closed", flush=True)

if __name__ == "__main__":
    main()
