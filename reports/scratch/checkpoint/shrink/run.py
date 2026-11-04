"""Greedy shrink of each refinement certificate: drop a checkpoint, keep the drop if still UNSAT; the result is locally minimal."""
import csv, os, sys, time
from multiprocessing import Pool
import pandas as pd
sys.path.insert(0, "/home/al/dev/MOSP")
from learning.checkpoint_bound import decide
from learning.obstruction_expansion import closed_masks_from_matrix
from learning.obstruction_ledger import corpus_instances

def _init():
    os.nice(19)

def job(a):
    name, matrix, opt, harper, b, sizes = a
    closed = closed_masks_from_matrix(matrix); n = len(closed)
    t0 = time.monotonic(); calls = 0; conf = 0
    cur = list(sizes)
    # try dropping from the outside in, then the inside: order by distance from the band's middle, farthest first
    mid = (cur[0] + cur[-1]) / 2
    for s in sorted(cur, key=lambda x: -abs(x - mid)):
        trial = [x for x in cur if x != s]
        if not trial:
            break
        r = decide(closed, trial, b, conflicts=2_000_000); calls += 1; conf += r["conflicts"]
        if r["answer"] is False:
            cur = trial
    return dict(instance_name=name, n=n, optimum=opt, harper_ref=harper, b=b, start=len(sizes), minimal=len(cur),
                sizes=" ".join(map(str, cur)), calls=calls, conflicts=conf, seconds=round(time.monotonic() - t0, 1))

if __name__ == "__main__":
    r = pd.read_csv("/home/al/dev/MOSP/reports/scratch/checkpoint/refine/refine.csv"); r = r[r.answer == "unsat"]
    found = corpus_instances()
    jobs = [(x.instance_name, found[x.instance_name][1].matrix, int(x.optimum), int(x.harper_ref), int(x.b), list(map(int, x.sizes.split()))) for x in r.itertuples()]
    jobs.sort(key=lambda j: -j[1].shape[0])
    out = "/home/al/dev/MOSP/reports/scratch/checkpoint/shrink/shrink.csv"
    with open(out, "w", newline="") as fh, Pool(5, initializer=_init) as pool:
        w = None
        for row in pool.imap_unordered(job, jobs):
            if w is None:
                w = csv.DictWriter(fh, fieldnames=list(row)); w.writeheader()
            w.writerow(row); fh.flush(); print(time.strftime("%T"), row, flush=True)
    print("shrink done", flush=True)
