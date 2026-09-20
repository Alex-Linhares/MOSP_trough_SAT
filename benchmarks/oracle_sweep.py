"""Check the corpus against CP-SAT, an outside solver.

The corpus records 6,349 certified optima. They rest on two solvers written for
this project, which agree with each other -- and agreement between two
implementations by one author is weaker evidence than it looks. The customer
search, which closed the hardest of them, produces no proof object at all, so
for those instances "certified" currently means "our search says so".

This runs a third solver, Martin, Yanasse & Pinto's CP model under CP-SAT, in a
separate interpreter sharing no code with either engine, and reports every
disagreement. A disagreement is a bug in one of three places and is worth more
than any number of agreements; the agreements are worth having in bulk.

Only CP-SAT's OPTIMAL answers count as opinions. FEASIBLE means it ran out of
time and its value is an upper bound, which tells us nothing about ours.

    python -m benchmarks.oracle_sweep --sample 200 --workers 8 --seconds 30
"""

from __future__ import annotations

import argparse
import json
import multiprocessing
import random
import time
from pathlib import Path

from mosp.instance import MOSPInstance
from satisfiability.mosp_solver import CERTIFIED, SOLUTIONS_DIR

DEFAULT_INSTANCE_DIR = Path("benchmarks/instances")


def _worker(matrix_list, n_customers, n_patterns, name, claimed, seconds, queue):
    import numpy as np

    from satisfiability.cpsat import solve_cpsat

    instance = MOSPInstance(
        matrix=np.array(matrix_list, dtype=np.int8),
        n_customers=n_customers, n_patterns=n_patterns, name=name)
    answer = solve_cpsat(instance, max_seconds=seconds)
    queue.put((name, claimed, answer.status, answer.value, answer.best_bound,
               answer.seconds))


def sweep(jobs, seconds=30.0, workers=8, verbose=True):
    queue: multiprocessing.Queue = multiprocessing.Queue()
    pending, running, results = list(jobs), [], []
    in_flight = 0

    def launch(job):
        instance, claimed = job
        proc = multiprocessing.Process(
            target=_worker,
            args=(instance.matrix.tolist(), instance.n_customers,
                  instance.n_patterns, instance.name, claimed, seconds, queue))
        proc.start()
        return proc

    while pending and in_flight < workers:
        running.append(launch(pending.pop(0))); in_flight += 1

    done = agreed = disagreed = unproved = 0
    while done < len(jobs):
        name, claimed, status, value, bound, secs = queue.get()
        done += 1; in_flight -= 1
        if status == "OPTIMAL":
            if value == claimed:
                agreed += 1
            else:
                disagreed += 1
                print(f"  DISAGREEMENT {name}: corpus says {claimed}, "
                      f"CP-SAT proves {value}", flush=True)
        else:
            unproved += 1
        if verbose and done % 25 == 0:
            print(f"  {done}/{len(jobs)}: {agreed} agree, {disagreed} disagree, "
                  f"{unproved} unproved by CP-SAT", flush=True)
        results.append((name, claimed, status, value, bound, secs))

        multiprocessing.active_children()
        while pending and in_flight < workers:
            running.append(launch(pending.pop(0))); in_flight += 1

    for proc in running:
        proc.join()
    return results, agreed, disagreed, unproved


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--sample", type=int, default=200,
                        help="how many certified instances to check; 0 for all")
    parser.add_argument("--seconds", type=float, default=30.0)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--max-patterns", type=int, default=0,
                        help="skip instances wider than this; 0 for no limit")
    parser.add_argument("--dir", type=Path, default=DEFAULT_INSTANCE_DIR)
    args = parser.parse_args()

    from benchmarks.solve_parallel import find_benchmark_files

    claimed = {}
    for path in SOLUTIONS_DIR.glob("*.json"):
        data = json.loads(path.read_text())
        if data.get("provenance") in CERTIFIED:
            claimed[data["instance_name"]] = data["mosp_value"]

    jobs = []
    for filepath in find_benchmark_files(args.dir):
        try:
            instances = MOSPInstance.from_benchmark_file(filepath)
        except Exception:  # noqa: BLE001
            continue
        for instance in instances:
            if instance.name not in claimed:
                continue
            if args.max_patterns and instance.n_patterns > args.max_patterns:
                continue
            jobs.append((instance, claimed[instance.name]))

    if args.sample and args.sample < len(jobs):
        random.Random(args.seed).shuffle(jobs)
        jobs = jobs[:args.sample]

    print(f"{len(jobs)} certified instances against CP-SAT, "
          f"{args.seconds:.0f}s each, {args.workers} workers", flush=True)
    started = time.time()
    _, agreed, disagreed, unproved = sweep(jobs, args.seconds, args.workers)
    print(f"\n{agreed} agreed, {disagreed} DISAGREED, "
          f"{unproved} not settled by CP-SAT in {args.seconds:.0f}s, "
          f"in {time.time() - started:.0f}s")


if __name__ == "__main__":
    main()
