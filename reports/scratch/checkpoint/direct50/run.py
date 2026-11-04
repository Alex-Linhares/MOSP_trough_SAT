"""The project's direct position encoding (encode_mosp_decision) at k = optimum - 1 on the 50-customer pilot instances, 1M conflicts, for comparison with the full nested chain."""
import csv, os, sys, time
from multiprocessing import Pool
sys.path.insert(0, "/home/al/dev/MOSP")
from learning.checkpoint_bound import pilot_population
from learning.obstruction_ledger import corpus_instances
from satisfiability.mosp_encoding import encode_mosp_decision

def _init():
    os.nice(19)

def job(a):
    name, inst, opt = a
    from pysat.solvers import Solver
    t0 = time.monotonic()
    cnf, pool, m = encode_mosp_decision(inst, opt - 1)
    enc = time.monotonic() - t0
    s = Solver(name="cadical195", bootstrap_with=cnf.clauses)
    s.conf_budget(1_000_000); ans = s.solve_limited(); st = s.accum_stats() or {}; s.delete()
    return dict(instance_name=name, n=inst.n_customers, m=inst.n_patterns, optimum=opt, k=opt - 1, answer=ans,
                refutes=ans is False, conflicts=int(st.get("conflicts", 0)), seconds=round(time.monotonic() - t0, 1),
                encode_seconds=round(enc, 2), n_vars=cnf.nv, n_clauses=len(cnf.clauses))

if __name__ == "__main__":
    pop = pilot_population(75); pop = pop[pop.n == 50]
    found = corpus_instances()
    jobs = [(r.instance_name, found[r.instance_name][1], int(r.optimum)) for r in pop.itertuples()]
    out = "/home/al/dev/MOSP/reports/scratch/checkpoint/direct50/direct50.csv"
    with open(out, "w", newline="") as fh, Pool(4, initializer=_init) as pool:
        w = None
        for row in pool.imap_unordered(job, jobs):
            if w is None:
                w = csv.DictWriter(fh, fieldnames=list(row)); w.writeheader()
            w.writerow(row); fh.flush(); print(time.strftime("%T"), row, flush=True)
    print("direct50 done", flush=True)
