"""End-to-end solve time under both seeds on large instances (§28 addendum).

For each instance and each seed (`cs-dfs`, Chu & Stuckey's MCN start;
`rule+cs-dfs`, the two-key rule), run the complete customer-search descent
exactly as `solve_mosp_exact` does -- `_lower_bound` as the floor, then
`customer_search.solve` -- but without the solution cache, so the search
really runs. One process per (instance, seed), each pinned to its own core.
Checks the value against the certified optimum in `solutions/`, which is only
read. Writes `learning/data/rule_seed/large_endtoend.csv`.

    PYTHONPATH=. python -m learning.rule_seed_large
"""
from __future__ import annotations

import csv
import json
import multiprocessing as mp
import os
import time
from pathlib import Path

INSTANCES = ["Random-100-100-4-1_0", "Random-125-125-6-1_0",
             "Random-125-125-6-3_0", "Random-125-125-6-4_0"]
SEEDS = ["cs-dfs", "rule+cs-dfs"]
OUT = Path(__file__).resolve().parent / "data" / "rule_seed" / "large_endtoend.csv"


def job(args):
    core, name, seed = args
    os.sched_setaffinity(0, {core})
    from learning import dataset as ds
    from satisfiability.customer_search import solve
    from satisfiability.heuristics import STRATEGIES
    from satisfiability.mosp_solver import SOLUTIONS_DIR, _lower_bound, _solution_path

    inst = next(i for _, i in ds.enumerate_instances(ds.DEFAULT_INSTANCE_DIR) if i.name == name)
    cert = json.load(open(_solution_path(inst, SOLUTIONS_DIR)))["mosp_value"]
    start_value = STRATEGIES[seed](inst)[0]          # recomputed inside solve; timed there too
    t0 = time.perf_counter()
    lb = _lower_bound(inst)
    t1 = time.perf_counter()
    res = solve(inst, lower=lb, upper_strategy=seed)
    t2 = time.perf_counter()
    return dict(instance=name, seed=seed, core=core, optimum=cert, start=start_value,
                lower_bound=lb, value=res.value, proof=res.proof, nodes=res.nodes,
                search_seconds=round(res.seconds, 2), lb_seconds=round(t1 - t0, 2),
                total_seconds=round(t2 - t0, 2), agrees=res.value == cert)


if __name__ == "__main__":
    jobs = [(c, n, s) for c, (n, s) in enumerate((n, s) for n in INSTANCES for s in SEEDS)]
    with mp.get_context("spawn").Pool(len(jobs)) as pool:
        rows = []
        for r in pool.imap_unordered(job, jobs):
            rows.append(r)
            print(r, flush=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: (r["instance"], r["seed"])))
    print("wrote", OUT)
