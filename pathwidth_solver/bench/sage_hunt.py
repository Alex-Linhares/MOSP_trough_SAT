"""Hunt for graphs that SageMath's exact pathwidth solver cannot settle and ours can.

Started 2026-10-15 at the owner's request: 8 processes, smallest graphs first.
For each graph: SageMath's vertex_separation(algorithm="BAB") (Coudert, Mazauric &
Nisse) under a 600 s cap; only if Sage times out or errors, our solver (defaults,
minor step on) under the same cap. One process per solver call, killed at the cap,
via sage_headtohead.one. Sets: TreewidthLIB colouring, freetdi named, VSPLIB trees,
Harwell-Boeing and grids (Rome excluded: 11,534 small graphs Sage settles quickly).
The machine is shared, so times are wall clock under load; a Sage timeout is
recorded as such, not as a proof that Sage cannot do it. Resumable.
    python bench/sage_hunt.py --procs 8
"""
import csv, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import sage_headtohead as h2h
from readers import HERE as INST, SETS, read_any

CAP = 600.0
FIELDS = ["set", "name", "n", "m", "sage_status", "sage_width", "sage_seconds",
          "ours_status", "ours_width", "ours_proof", "ours_seconds", "finished"]


def hunt(job):
    setname, path = job
    s = h2h.one((setname, path, "sage", CAP))
    row = dict(set=setname, name=s["name"], n=s["n"], m=s["m"], sage_status=s["status"], sage_width=s["width"],
               sage_seconds=s["seconds"], ours_status="", ours_width="", ours_proof="", ours_seconds="")
    if s["status"] != "ok":
        o = h2h.one((setname, path, "ours", CAP))
        row.update(ours_status=o["status"], ours_width=o["width"], ours_proof=o["detail"], ours_seconds=o["seconds"])
    row["finished"] = f"{datetime.now():%Y-%m-%dT%H:%M:%S}"
    return row


def main():
    procs = int(sys.argv[sys.argv.index("--procs") + 1]) if "--procs" in sys.argv else 8
    jobs = []
    for name in ["coloring", "named", "vsplib-tree", "vsplib-hb", "vsplib-grids"]:
        for p in SETS[name]():
            G = read_any(p)
            jobs.append((G.number_of_nodes(), G.number_of_edges(), name, p))
    jobs.sort(key=lambda j: (j[0], j[1], str(j[3])))
    out = HERE / "results" / "sage_hunt.csv"
    done = {r["name"] for r in csv.DictReader(open(out))} if out.exists() else set()
    todo = [(j[2], j[3]) for j in jobs if str(j[3].relative_to(INST)) not in done]
    new = not out.exists()
    with open(out, "a", newline="") as f, ThreadPoolExecutor(procs) as ex:
        w = csv.DictWriter(f, FIELDS)
        if new:
            w.writeheader()
        print(f"{datetime.now():%Y-%m-%d %H:%M:%S} {len(todo)} graphs, {procs} workers, cap {CAP:.0f} s", flush=True)
        for fut in as_completed([ex.submit(hunt, j) for j in todo]):
            r = fut.result(); w.writerow(r); f.flush()
            flag = "  <== Sage failed, ours " + (f"proved {r['ours_width']} ({r['ours_proof']}) in {r['ours_seconds']}s"
                                                  if r["ours_proof"] else r["ours_status"]) if r["sage_status"] != "ok" else ""
            print(f"{datetime.now():%H:%M:%S} {r['name']} n={r['n']} sage {r['sage_status']} "
                  f"w={r['sage_width']} {r['sage_seconds']}s{flag}", flush=True)


if __name__ == "__main__":
    main()
