"""Descending satisfiable-call search: improve solutions without proving anything.

The binary search in `mosp_solver` spends most of its budget on the expensive
direction. Probing the middle of `[lower, upper]` asks for a *refutation* at a
value below the optimum, and those are empirically the calls that never return:
in a parallel-k experiment on SP3, a satisfiable call at k=37 answered in
seconds while every probe from k=10..36 ran for an hour without finishing.

This mode never asks for a refutation. It starts at the best known upper bound
and steps down one at a time, each call satisfiable until the first one that is
not. Every success is a better solution, cached immediately, so an interrupted
run keeps everything it found.

Two things fall out of that:

- When the lower bound already equals the value reached, the instance is
  **closed**: the solution proves `MOSP <= k`, the bound proves `MOSP >= k`, and
  no refutation is needed. GP7 and GP8 were both settled this way after
  resisting hours of binary search.
- Otherwise the result is an improved upper bound, reported honestly as a
  solution of known value whose optimality is unproven.

Usage:
    python -m benchmarks.ratchet --instances GP8,SP3 --timeout 1800
    python -m benchmarks.ratchet --unsolved --timeout 3600
"""

from __future__ import annotations

import argparse
import multiprocessing
import time
from pathlib import Path
from typing import Optional

from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from satisfiability.mosp_encoding import encode_mosp_decision, extract_ordering
from satisfiability.mosp_solver import (
    PROVENANCE_BOUND,
    PROVENANCE_REFUTATION,
    PROVENANCE_SOLUTION,
    SAT_BACKEND,
    SOLUTIONS_DIR,
    _lower_bound,
    _save_solution,
    _solution_path,
    _upper_bound,
)

DEFAULT_INSTANCE_DIR = Path("benchmarks/instances")


def _decision_worker(matrix_list, n_customers, n_patterns, name, k, queue):
    """Decide 'MOSP <= k?' in a child process and post the answer."""
    import numpy as np
    from pysat.solvers import Solver

    try:
        instance = MOSPInstance(
            matrix=np.array(matrix_list, dtype=np.int8),
            n_customers=n_customers,
            n_patterns=n_patterns,
            name=name,
        )
        cnf, pool, m = encode_mosp_decision(instance, k)
        with Solver(name=SAT_BACKEND, bootstrap_with=cnf.clauses) as solver:
            if solver.solve():
                queue.put(("sat", extract_ordering(solver.get_model(), pool, m)))
            else:
                queue.put(("unsat", None))
    except Exception as exc:  # noqa: BLE001
        queue.put(("error", f"{type(exc).__name__}: {exc}"))


def _sat_at(
    instance: MOSPInstance, k: int, budget: Optional[float] = None
) -> tuple[str, Optional[list[int]]]:
    """Decide "MOSP(instance) <= k?" under a wall-clock budget.

    Returns ("sat", ordering), ("unsat", None) or ("timeout", None).

    The call runs in a child process that is killed when the budget expires,
    rather than in-process under `solve_limited` with an interrupt. Kissat
    accepts pysat's interrupt API but does not honour it: on a genuinely hard
    refutation the call ran past a 15-second interrupt without stopping. A
    budget that the solver may ignore is worse than none, because it reads as a
    bound in the results while not being one -- which is exactly how an
    unbounded first call spent more than an hour beyond the budget it was given.
    """
    queue: multiprocessing.Queue = multiprocessing.Queue()
    proc = multiprocessing.Process(
        target=_decision_worker,
        args=(instance.matrix.tolist(), instance.n_customers,
              instance.n_patterns, instance.name, k, queue),
    )
    proc.start()
    proc.join(timeout=budget)

    if proc.is_alive():
        proc.terminate()
        proc.join(timeout=5)
        if proc.is_alive():
            proc.kill()
            proc.join()
        return "timeout", None

    proc.join()
    if queue.empty():
        return "timeout", None

    status, payload = queue.get_nowait()
    if status == "error":
        raise RuntimeError(f"decision worker failed: {payload}")
    return status, payload


def ratchet(
    instance: MOSPInstance,
    start: Optional[int] = None,
    timeout: Optional[float] = None,
    solutions_dir: Path = SOLUTIONS_DIR,
    verbose: bool = True,
) -> tuple[Optional[int], Optional[list[int]], bool]:
    """Step k downwards, one satisfiable call at a time.

    Returns (best_value, best_ordering, proven_optimal). `proven_optimal` is
    True when the value reached meets the lower bound, which certifies it
    without any refutation.
    """
    deadline = time.time() + timeout if timeout is not None else None

    lower = _lower_bound(instance)
    if start is None:
        start, best_ordering = _upper_bound(instance)
    else:
        best_ordering = None

    best = start
    if verbose:
        print(f"{instance.name}: lb={lower} starting at k={start}", flush=True)

    if best_ordering is None:
        # The opening call gets the same budget as any other. It used to get
        # none at all, which made `--timeout` a bound on every call except the
        # first -- usually the hardest, since `--start` is often set to a value
        # near the optimum.
        remaining = (deadline - time.time()) if deadline else None
        status, found = _sat_at(instance, best, budget=remaining)
        if status == "unsat":
            if verbose:
                print(f"  k={best}: UNSAT — start value is below the optimum",
                      flush=True)
            return None, None, False
        if status == "timeout":
            if verbose:
                print(f"  k={best}: timed out; no solution found", flush=True)
            return None, None, False
        best_ordering = found

    opening = max_open_stacks(instance, best_ordering)
    _save_solution(instance, opening, best_ordering, solutions_dir,
                   provenance=(PROVENANCE_BOUND if opening <= lower
                               else PROVENANCE_SOLUTION))

    while best > lower:
        if deadline and time.time() > deadline:
            if verbose:
                print(f"  timeout with best={best} (lb={lower})", flush=True)
            break

        target = best - 1
        started = time.time()
        remaining = (deadline - time.time()) if deadline else None
        status, found = _sat_at(instance, target, budget=remaining)
        elapsed = time.time() - started

        if status == "unsat":
            # A refutation, which also proves the current best is optimal.
            _save_solution(instance, best, best_ordering, solutions_dir,
                           provenance=PROVENANCE_REFUTATION)
            if verbose:
                print(f"  k={target}: UNSAT in {elapsed:.0f}s — {best} is optimal",
                      flush=True)
            return best, best_ordering, True

        if status == "timeout":
            # Distinct from a refutation: the solver did not answer, so nothing
            # is proved about `target`. Reporting this as UNSAT would silently
            # claim the current best is optimal when it may not be.
            if verbose:
                print(f"  k={target}: timed out after {elapsed:.0f}s, "
                      f"best stays {best}", flush=True)
            break

        actual = max_open_stacks(instance, found)
        best, best_ordering = min(actual, target), found
        _save_solution(instance, best, best_ordering, solutions_dir,
                       provenance=(PROVENANCE_BOUND if best <= lower
                                   else PROVENANCE_SOLUTION))
        if verbose:
            print(f"  k={target}: SAT in {elapsed:.0f}s -> best={best}", flush=True)

    proven = best <= lower
    if verbose:
        print(f"{instance.name}: best={best} lb={lower} "
              f"{'PROVEN OPTIMAL (bound met)' if proven else 'optimality unproven'}",
              flush=True)
    return best, best_ordering, proven


def find_instances(names: list[str], instance_dir: Path) -> list[MOSPInstance]:
    """Locate instances whose name starts with any of `names`."""
    from benchmarks.solve_parallel import find_benchmark_files

    wanted = [n.strip().lower() for n in names if n.strip()]
    found = []
    for filepath in find_benchmark_files(instance_dir):
        try:
            instances = MOSPInstance.from_benchmark_file(filepath)
        except Exception:  # noqa: BLE001
            continue
        for inst in instances:
            label = inst.name.strip().lower()
            if any(label.startswith(n) for n in wanted):
                found.append(inst)
    return found


def find_unsolved(instance_dir: Path, solutions_dir: Path) -> list[MOSPInstance]:
    from benchmarks.solve_parallel import find_benchmark_files

    pending = []
    for filepath in find_benchmark_files(instance_dir):
        try:
            instances = MOSPInstance.from_benchmark_file(filepath)
        except Exception:  # noqa: BLE001
            continue
        for inst in instances:
            if not _solution_path(inst, solutions_dir).exists():
                pending.append(inst)
    return pending


def _ratchet_worker(matrix_list, n_customers, n_patterns, name, start, timeout,
                    solutions_dir, queue):
    """Run the ratchet on one instance in a child process."""
    import numpy as np

    try:
        instance = MOSPInstance(
            matrix=np.array(matrix_list, dtype=np.int8),
            n_customers=n_customers, n_patterns=n_patterns, name=name,
        )
        value, ordering, proven = ratchet(
            instance, start=start, timeout=timeout,
            solutions_dir=solutions_dir, verbose=False,
        )
        queue.put((value, ordering, proven, None))
    except Exception as exc:  # noqa: BLE001
        queue.put((None, None, False, f"{type(exc).__name__}: {exc}"))


def ratchet_many(
    instances: list[MOSPInstance],
    start: Optional[int] = None,
    timeout: Optional[float] = None,
    solutions_dir: Path = SOLUTIONS_DIR,
    workers: int = 0,
) -> list[tuple[Optional[int], Optional[list[int]], bool]]:
    """Ratchet many instances at once, `workers` in flight.

    Instances are independent, so this is a plain fan-out, but it is what makes
    a night's budget usable: run sequentially, sixteen hours across a hundred
    and fifty instances leaves each about six minutes, which does not reach the
    part of the descent where the interesting values are. Fanned out over thirty
    cores the same budget gives each instance hours.

    Each instance runs in its own process, so one that wedges or exhausts memory
    is killed without taking the run down, and every improvement is cached as it
    is found.
    """
    import os

    workers = workers or min(30, os.cpu_count() or 1)
    pending = list(instances)
    running: list[tuple] = []
    results: list[tuple] = []
    index = 0
    done = 0

    print(f"{len(pending)} instances, {workers} workers, "
          f"{('%.0fs' % timeout) if timeout else 'no'} budget each", flush=True)

    while index < len(pending) or running:
        while len(running) < workers and index < len(pending):
            inst = pending[index]
            index += 1
            queue: multiprocessing.Queue = multiprocessing.Queue()
            proc = multiprocessing.Process(
                target=_ratchet_worker,
                args=(inst.matrix.tolist(), inst.n_customers, inst.n_patterns,
                      inst.name, start, timeout, solutions_dir, queue),
            )
            proc.start()
            running.append((inst, proc, queue, time.time()))

        still = []
        for inst, proc, queue, started in running:
            if proc.is_alive():
                # Each child already honours its own budget; this only catches
                # one wedged well past it, with enough slack that a live solve
                # is never cut short.
                if timeout and time.time() - started > timeout * 2 + 300:
                    proc.kill()
                    proc.join()
                    results.append((None, None, False))
                    done += 1
                    print(f"[{done}/{len(pending)}] {inst.name[:40]}: "
                          f"killed, overran its budget", flush=True)
                    continue
                still.append((inst, proc, queue, started))
                continue

            proc.join()
            if queue.empty():
                results.append((None, None, False))
                done += 1
                print(f"[{done}/{len(pending)}] {inst.name[:40]}: "
                      f"worker exited with no result", flush=True)
                continue

            value, ordering, proven, error = queue.get_nowait()
            results.append((value, ordering, proven))
            done += 1
            elapsed = time.time() - started
            if error:
                label = f"ERROR {error}"
            elif proven:
                label = f"MOSP={value} PROVEN OPTIMAL"
            elif value is not None:
                label = f"best={value} (optimality unproven)"
            else:
                label = "no solution found"
            print(f"[{done}/{len(pending)}] {inst.name[:40]}: {label} "
                  f"{elapsed:.0f}s", flush=True)

        running = still
        if running:
            time.sleep(0.2)

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--instances", type=str, default=None,
                        help="comma-separated name prefixes, e.g. GP8,SP3")
    parser.add_argument("--unsolved", action="store_true",
                        help="run against every instance with no cached solution")
    parser.add_argument("--dir", type=Path, default=DEFAULT_INSTANCE_DIR)
    parser.add_argument("--solutions-dir", type=Path, default=SOLUTIONS_DIR)
    parser.add_argument("--start", type=int, default=None,
                        help="first k to try (default: the tabu upper bound)")
    parser.add_argument("--timeout", type=float, default=None,
                        help="per-instance budget in seconds")
    parser.add_argument("--workers", type=int, default=1,
                        help="instances to run at once (default 1; 0 = min(30, cores))")
    args = parser.parse_args()

    if args.unsolved:
        targets = find_unsolved(args.dir, args.solutions_dir)
    elif args.instances:
        targets = find_instances(args.instances.split(","), args.dir)
    else:
        raise SystemExit("pass --instances or --unsolved")

    if not targets:
        raise SystemExit("no matching instances")

    if args.workers == 1:
        results = []
        for inst in targets:
            results.append(ratchet(inst, start=args.start, timeout=args.timeout,
                                   solutions_dir=args.solutions_dir))
            print(flush=True)
    else:
        results = ratchet_many(targets, start=args.start, timeout=args.timeout,
                               solutions_dir=args.solutions_dir,
                               workers=args.workers)

    closed = sum(1 for _, _, proven in results if proven)
    improved = sum(1 for value, _, proven in results
                   if not proven and value is not None)
    print(f"closed {closed}, improved without proof {improved}, "
          f"of {len(targets)} instances")


if __name__ == "__main__":
    main()
