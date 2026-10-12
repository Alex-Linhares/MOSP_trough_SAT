"""The dataset's upper-bound-only classes, outside Rome, with the minor step: no time limit.

Started 2026-10-12 on the owner's request (paper1/todo.md, "Re-run the dataset's 860
upper-bound-only classes"). Classes: provenance "solution" in
paper1/data/dataset/pathwidth_dataset.jsonl.gz, minus the Rome-only ones (their
own run is reports/scratch/rome_unlimited/) and minus seven already proved by
the minor-step runs (reports/scratch/minor_bound/bench_*_on.csv): 527 classes,
60 to 1,024 vertices, smallest first. Each starts from its recorded layout
(width checked here), so the descent's first question is width - 1. Solver: the
frozen committed snapshot of reports/scratch/myciel7_refute71/code_snapshot, with
the large minor budget (the owner's decision for long runs). Resumable.
    python reports/scratch/dataset_open/run.py --procs 7
"""
import csv, glob, gzip, json, multiprocessing as mp, re, sys, time
from datetime import datetime
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SNAP = ROOT / "reports/scratch/myciel7_refute71/code_snapshot"


def stem(s):
    return re.sub(r"(\.mtx)?\.(dgf|gr|rnd|graphml|txt)$", "", Path(s).name)


def width_closing(masks, order):
    """Unplaced vertices with a neighbour in the prefix, maximised: the search's convention."""
    placed, nb, w = 0, 0, 0
    for v in order:
        placed |= 1 << v
        nb |= masks[v]
        w = max(w, bin(nb & ~placed).count("1"))
    return w


def one(r):
    skip = HERE / "skip.txt"      # classes run separately (W4: reports/scratch/w4/), added 2026-10-12
    if skip.exists() and r["id"] in skip.read_text().split():
        return dict(id=r["id"], collections="|".join(sorted({m["collection"] for m in r["members"]})),
                    names="|".join(sorted(stem(m.get("name") or m["source"]) for m in r["members"])),
                    n=r["n"], m=r["m"], recorded=r["width"], started_from_layout=False, width=r["width"],
                    proof="", lower="", nodes=0, seconds=0.0, finished="skipped: run separately",
                    order="", minor="")
    sys.path.insert(0, str(SNAP))
    from pathwidth.solve import solve_masks
    from pathwidth.minor import MinorConfig
    LARGE = MinorConfig(first_nodes=1_000_000, total_nodes=500_000_000, time_fraction=0.9)
    n = r["n"]
    masks = [1 << v for v in range(n)]
    for u, v in r["edges"]:
        masks[u] |= 1 << v; masks[v] |= 1 << u
    order, kw = list(r["layout"]), {}
    for cand in (order, order[::-1]):
        if sorted(cand) == list(range(n)) and width_closing(masks, cand) == r["width"]:
            kw = dict(upper=r["width"], upper_order=cand)
            break
    t = time.time()
    s = solve_masks(masks, minor=LARGE, **kw)
    return dict(id=r["id"], collections="|".join(sorted({m["collection"] for m in r["members"]})),
                names="|".join(sorted(stem(m.get("name") or m["source"]) for m in r["members"])),
                n=n, m=r["m"], recorded=r["width"], started_from_layout=bool(kw), width=s.width,
                proof=s.proof, lower=s.lower, nodes=s.nodes, seconds=round(time.time() - t, 1),
                finished=f"{datetime.now():%Y-%m-%dT%H:%M:%S}", order=json.dumps(list(s.order)),
                minor=json.dumps(getattr(s, "minor", None)))


def main():
    procs = int(sys.argv[sys.argv.index("--procs") + 1]) if "--procs" in sys.argv else 1
    proved = set()
    for p in glob.glob(str(ROOT / "reports/scratch/minor_bound/bench_*_on.csv")):
        for row in csv.DictReader(open(p)):
            if row.get("proof"):
                proved.add(stem(row["name"]))
    recs = [json.loads(l) for l in gzip.open(ROOT / "paper1/data/dataset/pathwidth_dataset.jsonl.gz", "rt")]
    todo = [r for r in recs if r["provenance"] == "solution"
            and {m["collection"] for m in r["members"]} != {"Rome graphs"}
            and not ({stem(m.get("name") or m["source"]) for m in r["members"]} & proved)]
    todo.sort(key=lambda r: (r["n"], r["m"], r["id"]))
    out = HERE / "results.csv"
    done = {row["id"] for row in csv.DictReader(open(out))} if out.exists() else set()
    todo = [r for r in todo if r["id"] not in done]
    fields = ["id", "collections", "names", "n", "m", "recorded", "started_from_layout", "width", "proof",
              "lower", "nodes", "seconds", "finished", "order", "minor"]
    new = not out.exists()
    with open(out, "a", newline="") as f, mp.get_context("spawn").Pool(procs, maxtasksperchild=1) as pool:
        w = csv.DictWriter(f, fields)
        if new:
            w.writeheader()
        print(f"{datetime.now():%Y-%m-%d %H:%M:%S} {len(todo)} classes on {procs} workers", flush=True)
        for row in pool.imap_unordered(one, todo):
            w.writerow(row); f.flush()
            print(f"{datetime.now():%Y-%m-%d %H:%M:%S} done {row['id']} {row['names'][:40]} n={row['n']} "
                  f"recorded={row['recorded']} width={row['width']} proof={row['proof']!r} lower={row['lower']} "
                  f"{row['seconds']:.0f}s", flush=True)


if __name__ == "__main__":
    main()
