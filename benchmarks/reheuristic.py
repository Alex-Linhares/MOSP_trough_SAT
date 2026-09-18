"""Re-run an upper bound heuristic over instances and keep any improvement.

A new heuristic arrives after the corpus has already been solved, and the cached
values were produced by the old one. Re-solving from scratch to benefit from it
would be enormously wasteful, but the heuristic alone is cheap: seconds per
instance against hours for a SAT descent.

This runs a named strategy over a set of instances and saves whatever it finds.
Saving is monotone in `_save_solution`, so a worse result is discarded and a
certified value is never demoted — the sweep can only improve the corpus.

Two things make it worth running on its own rather than inside the ratchet:

- An improvement that reaches the instance's lower bound **closes** it outright,
  with no SAT call at all.
- Otherwise it lowers the ratchet's starting point, so the descent that follows
  skips the steps the heuristic already made.

Usage:
    python -m benchmarks.reheuristic --unproven --strategy customer-tabu
"""

from __future__ import annotations

import argparse
import multiprocessing
import time
from pathlib import Path
from typing import Optional

from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from satisfiability.mosp_solver import (
    SOLUTIONS_DIR,
    _load_solution,
    _lower_bound,
    _save_solution,
)

DEFAULT_INSTANCE_DIR = Path("benchmarks/instances")


def _worker(matrix_list, n_customers, n_patterns, name, strategy, seeds,
            kwargs, solutions_dir, queue):
    """Run `strategy` under several seeds and post the best value found."""
    import numpy as np

    from satisfiability.heuristics import upper_bound

    started = time.time()
    try:
        instance = MOSPInstance(
            matrix=np.array(matrix_list, dtype=np.int8),
            n_customers=n_customers, n_patterns=n_patterns, name=name,
        )
        cached = _load_solution(instance, solutions_dir)
        before = cached[0] if cached else None

        best_val, best_ordering = None, None
        for seed in seeds:
            value, ordering = upper_bound(
                instance, strategy=strategy, seed=seed, **kwargs)
            if best_val is None or value < best_val:
                best_val, best_ordering = value, ordering

        # The heuristic's own claim is not taken on trust: re-simulate before
        # anything reaches disk, so a bug in a strategy cannot corrupt the corpus.
        achieved = max_open_stacks(instance, best_ordering)
        if achieved != best_val:
            queue.put((name, before, None, 0, f"claimed {best_val}, achieves {achieved}"))
            return

        improved = before is None or achieved < before
        if improved:
            _save_solution(instance, achieved, best_ordering, solutions_dir)

        closed = achieved <= _lower_bound(instance)
        queue.put((name, before, achieved, time.time() - started,
                   "closed" if closed else None))
    except Exception as exc:  # noqa: BLE001
        queue.put((name, None, None, time.time() - started,
                   f"{type(exc).__name__}: {exc}"))


def sweep(
    instances: list[MOSPInstance],
    strategy: str,
    seeds: tuple[int, ...] = (42,),
    workers: int = 8,
    solutions_dir: Path = SOLUTIONS_DIR,
    ledger: Path | None = None,
    verbose: bool = True,
    **kwargs: object,
) -> list[tuple[str, Optional[int], Optional[int], float, Optional[str]]]:
    """Run `strategy` over `instances`, keeping improvements. Returns one row each."""
    queue: multiprocessing.Queue = multiprocessing.Queue()
    pending = list(instances)
    running: list[multiprocessing.Process] = []
    results = []

    def _launch(inst: MOSPInstance) -> multiprocessing.Process:
        proc = multiprocessing.Process(
            target=_worker,
            args=(inst.matrix.tolist(), inst.n_customers, inst.n_patterns,
                  inst.name, strategy, tuple(seeds), dict(kwargs),
                  solutions_dir, queue),
        )
        proc.start()
        return proc

    # Slots are counted rather than inferred from `is_alive()`: a worker that
    # has posted its result is still alive for a moment afterwards, so testing
    # liveness loses a slot per completion and deadlocks at `workers=1`.
    in_flight = 0
    while pending and in_flight < workers:
        running.append(_launch(pending.pop(0)))
        in_flight += 1

    done = 0
    total = len(instances)
    while done < total:
        name, before, after, elapsed, note = queue.get()
        done += 1
        in_flight -= 1
        if verbose:
            if note and note not in ("closed",):
                print(f"[{done}/{total}] {name}: {note}", flush=True)
            elif before is not None and after is not None and after < before:
                tag = " CLOSED" if note == "closed" else ""
                print(f"[{done}/{total}] {name}: {before} -> {after}"
                      f" ({elapsed:.0f}s){tag}", flush=True)
        results.append((name, before, after, elapsed, note))

        multiprocessing.active_children()  # reap whatever has exited
        while pending and in_flight < workers:
            running.append(_launch(pending.pop(0)))
            in_flight += 1

    for proc in running:
        proc.join()

    from benchmarks.compute import LEDGER, record
    record("reheuristic", [(r[0], r[3]) for r in results if r[3]],
           ledger=LEDGER if ledger is None else ledger)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--instances", type=str, default=None)
    parser.add_argument("--unproven", action="store_true")
    parser.add_argument("--strategy", type=str, default="customer-tabu")
    parser.add_argument("--dir", type=Path, default=DEFAULT_INSTANCE_DIR)
    parser.add_argument("--solutions-dir", type=Path, default=SOLUTIONS_DIR)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--seeds", type=str, default="42",
                        help="comma-separated; the best across them is kept")
    parser.add_argument("--max-iterations", type=int, default=500)
    parser.add_argument("--n-neighbors", type=int, default=200)
    args = parser.parse_args()

    from benchmarks.ratchet import find_instances, find_unproven

    if args.unproven:
        targets = find_unproven(args.dir, args.solutions_dir)
    elif args.instances:
        targets = find_instances(args.instances.split(","), args.dir)
    else:
        raise SystemExit("pass --instances or --unproven")

    seeds = tuple(int(s) for s in args.seeds.split(","))
    print(f"{len(targets)} instances, strategy={args.strategy}, "
          f"seeds={seeds}, iterations={args.max_iterations}", flush=True)

    started = time.time()
    results = sweep(
        targets, args.strategy, seeds=seeds, workers=args.workers,
        solutions_dir=args.solutions_dir,
        max_iterations=args.max_iterations, n_neighbors=args.n_neighbors,
    )

    improved = [r for r in results if r[1] is not None and r[2] is not None
                and r[2] < r[1]]
    closed = [r for r in improved if r[4] == "closed"]
    total_drop = sum(r[1] - r[2] for r in improved)
    print(f"\n{len(improved)}/{len(results)} improved, {total_drop} stacks saved, "
          f"{len(closed)} reached the lower bound, in {time.time() - started:.0f}s")


if __name__ == "__main__":
    main()
