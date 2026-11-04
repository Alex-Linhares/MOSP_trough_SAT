"""The full nested-chain encoding on the 75-customer pilot instances at the certifying level, 10M conflicts."""
import csv, os, sys, time
from multiprocessing import Pool
sys.path.insert(0, "/home/al/dev/MOSP")
from learning.checkpoint_bound import pilot_population, decide
from learning.obstruction_expansion import closed_masks_from_matrix
from learning.obstruction_ledger import corpus_instances

def _init():
    os.nice(19)

def job(a):
    name, matrix, opt, harper = a
    closed = closed_masks_from_matrix(matrix); n = len(closed)
    r = decide(closed, list(range(1, n)), opt - 2, conflicts=10_000_000)
    return dict(instance_name=name, n=n, optimum=opt, harper_ref=harper, b=opt - 2, answer=r["answer"],
                closes=r["answer"] is False, conflicts=r["conflicts"], seconds=round(r["seconds"], 1),
                n_vars=r["n_vars"], n_clauses=r["n_clauses"])

if __name__ == "__main__":
    pop = pilot_population(75); pop = pop[pop.n == 75]
    found = corpus_instances()
    jobs = [(r.instance_name, found[r.instance_name][1].matrix, int(r.optimum), int(r.harper_ref)) for r in pop.itertuples()]
    out = "/home/al/dev/MOSP/reports/scratch/checkpoint/full75/full75.csv"
    with open(out, "w", newline="") as fh, Pool(6, initializer=_init) as pool:
        w = None
        for row in pool.imap_unordered(job, jobs):
            if w is None:
                w = csv.DictWriter(fh, fieldnames=list(row)); w.writeheader()
            w.writerow(row); fh.flush()
            print(time.strftime("%T"), row, flush=True)
    print("full75 done", flush=True)
