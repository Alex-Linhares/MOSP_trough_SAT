"""Compare SAT backends on the decision calls that dominate MOSP solving.

Which backend to use is not obvious from general SAT benchmarks: MOSP formulas
are permutation-structured with totalizer cardinality constraints, and the call
that decides how long an instance takes is the *refutation* at k-1 that
certifies optimality, not the satisfiable call at k. Those two directions can
favour different solvers, so both are timed separately.

Instances are drawn from the sweep results, which supply a known optimum k*, so
every answer here has a ground truth: k-1 must be UNSAT and k must be SAT. A
backend disagreeing is a correctness bug, not a slow result, and is reported as
such.

Trials run concurrently, so absolute times include contention for memory
bandwidth and cache and are inflated against a quiet machine. Trial order is
shuffled so that cost falls evenly across backends, which keeps the *ranking*
meaningful; treat the absolute numbers as an upper bound and re-time the leaders
with --workers 1 before quoting any figure.

Usage:
    python -m benchmarks.solver_portfolio --instances 6 --timeout 300
    python -m benchmarks.solver_portfolio --workers 1   # clean timings, slow
"""

from __future__ import annotations

import argparse
import csv
import multiprocessing
import os
import time
from pathlib import Path
from typing import Optional

from mosp.instance import MOSPInstance

# Backends that answer a trivial UNSAT formula correctly. CryptoMinisat needs
# pycryptosat, which is not installed.
SOLVERS = [
    "Cadical103", "Cadical153", "Cadical195", "Cadical300",
    "Glucose3", "Glucose4", "Glucose42", "Gluecard3", "Gluecard4",
    "Kissat404", "Lingeling", "MapleCM", "MapleChrono", "Maplesat",
    "Mergesat3", "Minicard", "Minisat22", "MinisatEP", "MinisatGH",
]

DEFAULT_SWEEP = Path("benchmarks/results/sweep_long.csv")
DEFAULT_INSTANCE_DIR = Path("benchmarks/instances")


def _decision_worker(
    matrix_list: list[list[int]],
    n_customers: int,
    n_patterns: int,
    name: str,
    k: int,
    solver_name: str,
    result_queue: multiprocessing.Queue,
) -> None:
    """Decide 'MOSP <= k?' with one backend and report the answer and timing."""
    import numpy as np

    try:
        import pysat.solvers as solvers

        from satisfiability.mosp_encoding import encode_mosp_decision

        instance = MOSPInstance(
            matrix=np.array(matrix_list, dtype=np.int8),
            n_customers=n_customers,
            n_patterns=n_patterns,
            name=name,
        )
        encode_start = time.time()
        cnf, _, _ = encode_mosp_decision(instance, k)
        encode_time = time.time() - encode_start

        solve_start = time.time()
        solver = getattr(solvers, solver_name)(bootstrap_with=cnf.clauses)
        satisfiable = solver.solve()
        solve_time = time.time() - solve_start
        solver.delete()

        result_queue.put({
            "satisfiable": satisfiable,
            "solve_time": solve_time,
            "encode_time": encode_time,
            "n_clauses": len(cnf.clauses),
            "error": None,
        })
    except Exception as exc:  # noqa: BLE001
        result_queue.put({"satisfiable": None, "solve_time": None,
                          "encode_time": None, "n_clauses": None,
                          "error": f"{type(exc).__name__}: {exc}"})


def _run_one(instance: MOSPInstance, k: int, solver_name: str,
             timeout: float) -> dict:
    """Run one (instance, k, backend) trial under a hard timeout."""
    queue: multiprocessing.Queue = multiprocessing.Queue()
    proc = multiprocessing.Process(
        target=_decision_worker,
        args=(instance.matrix.tolist(), instance.n_customers,
              instance.n_patterns, instance.name, k, solver_name, queue),
    )
    start = time.time()
    proc.start()
    proc.join(timeout=timeout)
    elapsed = time.time() - start

    if proc.is_alive():
        proc.terminate()
        proc.join(timeout=5)
        if proc.is_alive():
            proc.kill()
            proc.join()
        return {"status": "timeout", "satisfiable": None,
                "solve_time": None, "wall_time": elapsed, "error": ""}

    proc.join()
    if queue.empty():
        return {"status": "crash", "satisfiable": None, "solve_time": None,
                "wall_time": elapsed,
                "error": f"exit {proc.exitcode}, no result"}

    result = queue.get_nowait()
    if result["error"]:
        return {"status": "error", "satisfiable": None, "solve_time": None,
                "wall_time": elapsed, "error": result["error"]}
    return {"status": "ok", "satisfiable": result["satisfiable"],
            "solve_time": result["solve_time"], "wall_time": elapsed,
            "error": ""}


def select_instances(sweep_csv: Path, instance_dir: Path, count: int,
                     min_time: float = 200.0) -> list[tuple[MOSPInstance, int]]:
    """Pick the slowest solved instances, which have the hardest refutations.

    Returns (instance, k*) pairs. A solved instance supplies the ground truth
    that k* is SAT and k* - 1 is UNSAT.
    """
    from benchmarks.solve_parallel import find_benchmark_files

    wanted: dict[str, int] = {}
    rows = [r for r in csv.DictReader(open(sweep_csv))
            if r["status"] == "solved" and float(r["time_seconds"]) > min_time
            and int(r["mosp_value"]) > 0]
    rows.sort(key=lambda r: -float(r["time_seconds"]))
    for row in rows[:count]:
        wanted[row["instance_name"]] = int(row["mosp_value"])

    found: list[tuple[MOSPInstance, int]] = []
    for filepath in find_benchmark_files(instance_dir):
        if not wanted:
            break
        try:
            instances = MOSPInstance.from_benchmark_file(filepath)
        except Exception:  # noqa: BLE001
            continue
        for inst in instances:
            if inst.name in wanted:
                found.append((inst, wanted.pop(inst.name)))
    return found


def run_portfolio(instances: list[tuple[MOSPInstance, int]],
                  solvers: list[str] = SOLVERS,
                  timeout: float = 300.0,
                  workers: int = 0,
                  output_csv: Optional[Path] = None) -> list[dict]:
    """Time every backend on the SAT call at k* and the UNSAT call at k* - 1."""
    workers = workers or min(30, os.cpu_count() or 1)

    trials = []
    for inst, k in instances:
        trials.append((inst, k, "sat", True))          # k is satisfiable
        if k >= 1:
            trials.append((inst, k - 1, "unsat", False))  # k-1 is not
    jobs = [(inst, k, kind, expected, solver)
            for inst, k, kind, expected in trials for solver in solvers]

    print(f"{len(instances)} instances x {len(solvers)} backends x 2 directions "
          f"= {len(jobs)} trials, {workers} workers, {timeout:.0f}s timeout")
    print()

    results: list[dict] = []
    # Trials are shuffled so that contention, which inflates every measurement
    # under parallel execution, is spread evenly across backends rather than
    # landing on whichever happens to be scheduled alongside a heavy job.
    import random
    random.Random(0).shuffle(jobs)

    from concurrent.futures import ThreadPoolExecutor

    def _trial(job):
        inst, k, kind, expected, solver = job
        # Each trial is its own process, so the pool here only shepherds them.
        return job, _run_one(inst, k, solver, timeout)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        completed = pool.map(_trial, jobs)
        for index, ((inst, k, kind, expected, solver), outcome) in enumerate(
                completed, 1):
            wrong = (outcome["status"] == "ok"
                     and outcome["satisfiable"] is not expected)
            row = {
                "instance": inst.name,
                "n_customers": inst.n_customers,
                "n_patterns": inst.n_patterns,
                "k": k,
                "direction": kind,
                "solver": solver,
                "status": "WRONG" if wrong else outcome["status"],
                "solve_time": (round(outcome["solve_time"], 3)
                               if outcome["solve_time"] is not None else ""),
                "wall_time": round(outcome["wall_time"], 3),
                "error": outcome["error"],
            }
            results.append(row)

            if index % 20 == 0 or wrong:
                marker = "  <-- WRONG ANSWER" if wrong else ""
                print(f"[{index}/{len(jobs)}] {solver} {kind} k={k} "
                      f"{inst.name[:28]}: {row['status']} "
                      f"{row['solve_time']}s{marker}", flush=True)

    if output_csv:
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        with open(output_csv, "w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(results[0]))
            writer.writeheader()
            writer.writerows(results)
        print(f"\nresults: {output_csv}")

    return results


def summarize(results: list[dict], timeout: float) -> None:
    """Rank backends by refutations closed, then by total time on them."""
    wrong = [r for r in results if r["status"] == "WRONG"]
    if wrong:
        print("\n*** BACKENDS DISAGREEING WITH KNOWN OPTIMA ***")
        for r in wrong:
            print(f"  {r['solver']} on {r['instance']} k={r['k']} ({r['direction']})")

    for direction in ("unsat", "sat"):
        rows = [r for r in results if r["direction"] == direction]
        if not rows:
            continue
        solvers = sorted({r["solver"] for r in rows})
        print()
        print(f"=== {direction.upper()} calls "
              f"({'proving optimality' if direction == 'unsat' else 'finding a solution'}) ===")
        print(f"{'backend':14} {'solved':>7} {'total(s)':>10} {'median(s)':>10}")
        print("-" * 45)

        table = []
        for solver in solvers:
            mine = [r for r in rows if r["solver"] == solver]
            done = [r for r in mine if r["status"] == "ok"]
            # Unsolved trials are charged the full timeout (PAR-1).
            total = sum(float(r["solve_time"]) for r in done) + \
                timeout * (len(mine) - len(done))
            times = sorted(float(r["solve_time"]) for r in done)
            median = times[len(times) // 2] if times else float("nan")
            table.append((len(done), total, median, solver, len(mine)))

        for done, total, median, solver, attempted in sorted(
                table, key=lambda t: (-t[0], t[1])):
            print(f"{solver:14} {done:>3}/{attempted:<3} {total:>10.1f} {median:>10.2f}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--sweep", type=Path, default=DEFAULT_SWEEP)
    parser.add_argument("--dir", type=Path, default=DEFAULT_INSTANCE_DIR)
    parser.add_argument("--instances", type=int, default=6)
    parser.add_argument("--timeout", type=float, default=300.0)
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--output", type=Path,
                        default=Path("benchmarks/results/solver_portfolio.csv"))
    args = parser.parse_args()

    chosen = select_instances(args.sweep, args.dir, args.instances)
    if not chosen:
        raise SystemExit("no suitable instances found")
    print("instances under test:")
    for inst, k in chosen:
        print(f"  {inst.name[:46]:46} {inst.n_customers}x{inst.n_patterns} k*={k}")
    print()

    results = run_portfolio(chosen, timeout=args.timeout, workers=args.workers,
                            output_csv=args.output)
    summarize(results, args.timeout)


if __name__ == "__main__":
    main()
