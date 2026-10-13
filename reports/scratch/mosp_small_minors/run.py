"""Quick lower bounds for the unsolved MOSP instances of the dataset, from small minors.

Started 2026-10-13 at the owner's request: 2 cores, about 5 s per instance.
Instances: the Carvalho & Soma classes not yet proved (dataset records with
provenance "solution", minus those proved in reports/scratch/dataset_open/), then
the 610 large instances of Frinhani et al. (2018), which have no value at all.
Each MOSP graph is contracted (min-d) to 40, 60, 80, 100, 120, n/4, n/3 and n/2 vertices,
smallest first while about 5 s remain, and
each minor is solved by our search for about 1 s; the best width proved on a
minor, or the lower bound the search reaches there, is a lower bound on the
pathwidth (Theorem 4.11), and MOSP = pathwidth + 1. Upper bound: the recorded
layout for Carvalho & Soma, a greedy layout for Frinhani (checked here).
Resumable; results in results.csv.
    python reports/scratch/mosp_small_minors/run.py --procs 2
"""
import csv, gzip, json, multiprocessing as mp, sys, time
from datetime import datetime
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SNAP = ROOT / "reports/scratch/myciel7_refute71/code_snapshot"
SIZES = (40, 60, 80, 100, 120)
FIELDS = ["key", "collection", "name", "n", "m", "upper", "upper_source", "lower", "lower_minor_size",
          "mosp_lower", "mosp_upper", "closed", "seconds", "finished"]


def width_closing(masks, order):
    p = nb = w = 0
    for v in order:
        p |= 1 << v; nb |= masks[v]; w = max(w, bin(nb & ~p).count("1"))
    return w


def one(job):
    sys.path.insert(0, str(SNAP)); sys.path.insert(0, str(ROOT))
    from pathwidth.minor import contraction_sequence, replay
    from pathwidth.solve import solve_masks
    from pathwidth.bounds import greedy_order
    key, coll, name, n, edges, upper, usrc = job
    t = time.time()
    if edges is None:                      # Frinhani: load the instance here, not in the parent
        import paper1.dataset as ds
        n, edges = ds.load(n)
    masks = [1 << v for v in range(n)]
    for u, v in edges:
        masks[u] |= 1 << v; masks[v] |= 1 << u
    if upper is None:
        order = greedy_order(masks)
        upper, usrc = width_closing(masks, order), "greedy (checked)"
    best, at = 0, ""
    sizes = sorted(set(SIZES) | {n // 4, n // 3, n // 2})   # larger minors for large dense graphs, while time remains
    for size in sizes:
        if size >= n or time.time() - t > 5:
            break
        minor, _, _ = replay(masks, contraction_sequence(masks, size, "min-d"))
        s = solve_masks(minor, time_budget=1.0, minor=False)
        lb = s.width if s.proof else s.lower
        if lb > best:
            best, at = lb, size
        if best >= upper:
            break
    return dict(key=key, collection=coll, name=name, n=n, m=len(edges), upper=upper, upper_source=usrc,
                lower=best, lower_minor_size=at, mosp_lower=best + 1, mosp_upper=upper + 1,
                closed=best >= upper, seconds=round(time.time() - t, 1),
                finished=f"{datetime.now():%Y-%m-%dT%H:%M:%S}")


def jobs():
    sys.path.insert(0, str(ROOT))
    import paper1.dataset as ds
    proved = set()
    for f in ("results.csv", "results_quick.csv"):
        p = ROOT / "reports/scratch/dataset_open" / f
        if p.exists():
            proved |= {r["id"] for r in csv.DictReader(open(p)) if r.get("proof")}
    out = []
    for l in gzip.open(ROOT / "paper1/data/dataset/pathwidth_dataset.jsonl.gz", "rt"):
        r = json.loads(l)
        if r["provenance"] == "solution" and r["id"] not in proved and \
                any(m["collection"] == "MOSP: Carvalho & Soma 2015" for m in r["members"]):
            nm = next(m["name"] for m in r["members"] if m["collection"] == "MOSP: Carvalho & Soma 2015")
            out.append((r["id"], "Carvalho & Soma 2015", nm, r["n"], r["edges"], r["width"], "recorded layout"))
    fr = [s for s in ds.sources() if s["collection"] == "MOSP: Frinhani et al. 2018, large"]
    import re
    size = lambda nm: int(re.match(r"Random-(\d+)", nm).group(1))
    for s in sorted(fr, key=lambda s: (size(s["name"]), s["name"])):
        out.append((s["name"], "Frinhani et al. 2018, large", s["name"], s, None, None, ""))
    out.sort(key=lambda j: (j[1] != "Carvalho & Soma 2015", j[3] if isinstance(j[3], int) else 10**6))
    return out


def guarded(job):
    """Run one() in its own process with a hard 30 s kill: a step that ignores its
    budget costs 30 s, not hours (two workers hung for 2 h on 2026-10-13)."""
    import subprocess, pickle, tempfile
    with tempfile.NamedTemporaryFile("wb", suffix=".pkl", delete=False) as f:
        pickle.dump(job, f); path = f.name
    code = ("import sys, pickle, json; sys.path.insert(0, %r); import run; "
            "print(json.dumps(run.one(pickle.load(open(%r, 'rb')))))" % (str(HERE), path))
    try:
        out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=30)
        row = json.loads(out.stdout.strip().splitlines()[-1]) if out.returncode == 0 else None
    except subprocess.TimeoutExpired:
        row = None
    Path(path).unlink(missing_ok=True)
    if row is None:
        key, coll, name = job[0], job[1], job[2]
        row = dict(key=key, collection=coll, name=name, n="", m="", upper="", upper_source="killed at 30 s",
                   lower="", lower_minor_size="", mosp_lower="", mosp_upper="", closed=False, seconds=30,
                   finished=f"{datetime.now():%Y-%m-%dT%H:%M:%S}")
    return row


def main():
    procs = int(sys.argv[sys.argv.index("--procs") + 1]) if "--procs" in sys.argv else 2
    out = HERE / "results.csv"
    done = {r["key"] for r in csv.DictReader(open(out))} if out.exists() else set()
    todo = [j for j in jobs() if j[0] not in done]
    new = not out.exists()
    with open(out, "a", newline="") as f, mp.get_context("spawn").Pool(procs) as pool:
        w = csv.DictWriter(f, FIELDS)
        if new:
            w.writeheader()
        print(f"{datetime.now():%Y-%m-%d %H:%M:%S} {len(todo)} instances on {procs} workers", flush=True)
        for row in pool.imap_unordered(guarded, todo):
            w.writerow(row); f.flush()
            print(f"{datetime.now():%H:%M:%S} {row['name'][:28]:28s} n={row['n']} MOSP in "
                  f"[{row['mosp_lower']}, {row['mosp_upper']}] {row['upper_source'] if 'killed' in row['upper_source'] else ''}{' CLOSED' if row['closed'] else ''} "
                  f"(minor {row['lower_minor_size']}) {row['seconds']}s", flush=True)


if __name__ == "__main__":
    main()
