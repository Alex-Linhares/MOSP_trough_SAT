"""Capped pass beside run.py: the remaining classes, 40 minutes each, 4 workers.

Started 2026-10-12 17:1x at the owner's request ("keep what's running but put 4
cores on the remaining classes for 40 mins"). Same classes and solver as run.py,
minus: those run.py has finished, the 7 it is working on (the smallest
unfinished ones in its order), and skip.txt. Each class gets a 2,400 s time
budget (the minor step may use half of it, with the large node budget) and is
killed 120 s after. Results in results_quick.csv; run.py's workers skip every
class proved here (see run.py, one()). Resumable.
    python reports/scratch/dataset_open/run_quick.py --procs 4
    python reports/scratch/dataset_open/run_quick.py --procs 14 --hours 2 --then 4   (2026-10-13)
"""
import csv, json, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run as main_run

BUDGET = 2400.0
CHILD = r'''
import json, sys, time
sys.path.insert(0, sys.argv[1])
from pathwidth.solve import solve_masks
from pathwidth.minor import MinorConfig
r = json.load(open(sys.argv[2]))
n = r["n"]; masks = [1 << v for v in range(n)]
for u, v in r["edges"]:
    masks[u] |= 1 << v; masks[v] |= 1 << u
def wc(o):
    p = nb = w = 0
    for v in o:
        p |= 1 << v; nb |= masks[v]; w = max(w, bin(nb & ~p).count("1"))
    return w
kw = {}
for o in (r["layout"], r["layout"][::-1]):
    if sorted(o) == list(range(n)) and wc(o) == r["width"]:
        kw = dict(upper=r["width"], upper_order=o); break
cfg = MinorConfig(first_nodes=1_000_000, total_nodes=500_000_000, time_fraction=0.5)
t = time.time()
s = solve_masks(masks, minor=cfg, time_budget=float(sys.argv[3]), **kw)
print(json.dumps(dict(width=s.width, proof=s.proof, lower=s.lower, nodes=s.nodes,
      seconds=round(time.time() - t, 1), order=list(s.order), minor=getattr(s, "minor", None),
      started_from_layout=bool(kw))))
'''
FIELDS = ["id", "collections", "names", "n", "m", "recorded", "started_from_layout", "width", "proof",
          "lower", "nodes", "seconds", "finished", "status", "order", "minor"]


GATE = threading.Condition()
ACTIVE = [0]
LIMIT = {"procs": 4, "after": None, "later": 4}     # set in main()


def admit():
    """Block until a worker slot is free under the current limit (it drops after LIMIT['after'])."""
    with GATE:
        while True:
            cap = LIMIT["procs"]
            if LIMIT["after"] is not None and time.time() >= LIMIT["after"]:
                cap = LIMIT["later"]
            if ACTIVE[0] < cap:
                ACTIVE[0] += 1
                return
            GATE.wait(30)


def release():
    with GATE:
        ACTIVE[0] -= 1
        GATE.notify_all()


def one(r):
    admit()
    try:
        return one_(r)
    finally:
        release()


def one_(r):
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(r, f); path = f.name
    row = dict(id=r["id"], collections="|".join(sorted({m["collection"] for m in r["members"]})),
               names="|".join(sorted(main_run.stem(m.get("name") or m["source"]) for m in r["members"])),
               n=r["n"], m=r["m"], recorded=r["width"], width=r["width"], proof="", lower="", nodes="",
               seconds="", status="", order="", minor="", started_from_layout="")
    t = time.time()
    try:
        out = subprocess.run([sys.executable, "-c", CHILD, str(main_run.SNAP), path, str(BUDGET)],
                             capture_output=True, text=True, timeout=BUDGET + 120)
        if out.returncode == 0 and out.stdout.strip():
            d = json.loads(out.stdout.strip().splitlines()[-1])
            row.update(d, order=json.dumps(d["order"]), minor=json.dumps(d["minor"]), status="ok")
        else:
            row.update(status="error: " + out.stderr.strip()[-200:])
    except subprocess.TimeoutExpired:
        row.update(status="killed at cap")
    row["seconds"] = row["seconds"] or round(time.time() - t, 1)
    row["finished"] = f"{datetime.now():%Y-%m-%dT%H:%M:%S}"
    Path(path).unlink(missing_ok=True)
    return row


def main():
    procs = int(sys.argv[sys.argv.index("--procs") + 1]) if "--procs" in sys.argv else 4
    LIMIT["procs"] = procs
    if "--hours" in sys.argv:          # after this many hours, drop to --then workers
        LIMIT["after"] = time.time() + 3600 * float(sys.argv[sys.argv.index("--hours") + 1])
        LIMIT["later"] = int(sys.argv[sys.argv.index("--then") + 1])
    import gzip, glob
    proved = set()
    for p in glob.glob(str(main_run.ROOT / "reports/scratch/minor_bound/bench_*_on.csv")):
        for row in csv.DictReader(open(p)):
            if row.get("proof"):
                proved.add(main_run.stem(row["name"]))
    recs = [json.loads(l) for l in gzip.open(main_run.ROOT / "paper1/data/dataset/pathwidth_dataset.jsonl.gz", "rt")]
    todo = [r for r in recs if r["provenance"] == "solution"
            and {m["collection"] for m in r["members"]} != {"Rome graphs"}
            and not ({main_run.stem(m.get("name") or m["source"]) for m in r["members"]} & proved)]
    todo.sort(key=lambda r: (r["n"], r["m"], r["id"]))
    done = {row["id"] for row in csv.DictReader(open(HERE / "results.csv"))}
    skip = set((HERE / "skip.txt").read_text().split()) if (HERE / "skip.txt").exists() else set()
    left = [r for r in todo if r["id"] not in done and r["id"] not in skip]
    busy = {r["id"] for r in left[:7]}               # run.py's workers take the smallest first
    out = HERE / "results_quick.csv"
    quick_done = {row["id"] for row in csv.DictReader(open(out))} if out.exists() else set()
    left = [r for r in left if r["id"] not in busy and r["id"] not in quick_done]
    new = not out.exists()
    with open(out, "a", newline="") as f, ThreadPoolExecutor(procs) as ex:
        w = csv.DictWriter(f, FIELDS)
        if new:
            w.writeheader()
        print(f"{datetime.now():%Y-%m-%d %H:%M:%S} {len(left)} classes, {procs} workers, {BUDGET:.0f} s each; "
              f"leaving to run.py: {sorted(busy)}", flush=True)
        for row in ex.map(one, left):
            w.writerow(row); f.flush()
            print(f"{datetime.now():%Y-%m-%d %H:%M:%S} {row['id']} {row['names'][:40]} n={row['n']} "
                  f"recorded={row['recorded']} width={row['width']} proof={row['proof']!r} {row['status']} "
                  f"{row['seconds']}s", flush=True)


if __name__ == "__main__":
    main()
