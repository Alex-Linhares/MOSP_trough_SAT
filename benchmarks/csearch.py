"""Close instances with the complete customer search, in parallel.

The counterpart of `benchmarks/ratchet.py` for `satisfiability.customer_search`.
The ratchet only ever asks satisfiable questions and so can only lower an upper
bound; this driver descends until the search *refutes*, which is what turns a
best known solution into a certified optimum.

Provenance is recorded exactly as it was established: `certified:refutation`
when the search exhausted `value - 1`, `certified:bound` when the descent met
the lower bound and needed no refutation, and `solution` when the budget ran out
first. A cached ordering that the descent never improved on is still re-saved
when the descent proved it optimal, which upgrades its provenance without
touching the witness.

Usage:
    python -m benchmarks.csearch --unproven --timeout 600 --workers 20
"""

from __future__ import annotations

import argparse
import multiprocessing
import time
from pathlib import Path

from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from satisfiability.mosp_solver import (
    PROVENANCE_BOUND,
    PROVENANCE_REFUTATION,
    PROVENANCE_SOLUTION,
    SOLUTIONS_DIR,
    _load_solution,
    _lower_bound,
    _save_solution,
)

DEFAULT_INSTANCE_DIR = Path("benchmarks/instances")

PROVENANCE = {
    "refutation": PROVENANCE_REFUTATION,
    "bound": PROVENANCE_BOUND,
    "": PROVENANCE_SOLUTION,
}


def _worker(matrix_list, n_customers, n_patterns, name, timeout, max_nodes,
            solutions_dir, queue):
    """Descend one instance in a child process and post what it established."""
    import numpy as np

    from satisfiability.customer_search import solve
    from satisfiability.heuristics import product_order_from_customers

    started = time.time()
    try:
        instance = MOSPInstance(
            matrix=np.array(matrix_list, dtype=np.int8),
            n_customers=n_customers, n_patterns=n_patterns, name=name,
        )
        cached = _load_solution(instance, solutions_dir)
        before = cached[0] if cached else None

        result = solve(instance, upper=before, lower=_lower_bound(instance),
                       time_budget=timeout, max_nodes=max_nodes)

        if result.order:
            ordering = product_order_from_customers(instance, result.order)
        elif cached:
            ordering = cached[1]
        else:
            queue.put((name, before, None, time.time() - started, "no witness"))
            return

        # The search's claim is never taken on trust: a witness that does not
        # simulate to its value is a bug, and must not reach the corpus.
        achieved = max_open_stacks(instance, ordering)
        if achieved != result.value:
            queue.put((name, before, None, time.time() - started,
                       f"claimed {result.value}, achieves {achieved}"))
            return

        _save_solution(instance, achieved, ordering, solutions_dir,
                       provenance=PROVENANCE[result.proof])
        queue.put((name, before, achieved, time.time() - started, result.proof))
    except Exception as exc:  # noqa: BLE001
        queue.put((name, None, None, time.time() - started,
                   f"{type(exc).__name__}: {exc}"))


def sweep(
    instances: list[MOSPInstance],
    timeout: float,
    workers: int = 8,
    max_nodes: int | None = None,
    solutions_dir: Path = SOLUTIONS_DIR,
    verbose: bool = True,
) -> list[tuple]:
    """Descend every instance, at most `workers` at a time. One row each."""
    queue: multiprocessing.Queue = multiprocessing.Queue()
    pending = list(instances)
    running: list[multiprocessing.Process] = []
    results = []

    def _launch(inst: MOSPInstance) -> multiprocessing.Process:
        proc = multiprocessing.Process(
            target=_worker,
            args=(inst.matrix.tolist(), inst.n_customers, inst.n_patterns,
                  inst.name, timeout, max_nodes, solutions_dir, queue),
        )
        proc.start()
        return proc

    # Slots are counted, not inferred from `is_alive()`. A worker posts its
    # result and then takes a moment to exit, so a just-finished process still
    # reads as alive; freeing slots by that test loses one slot per completion
    # and deadlocks outright at `workers=1`, with `queue.get()` waiting on a
    # process that was never launched. Each worker posts exactly one message,
    # so counting messages is exact.
    in_flight = 0
    while pending and in_flight < workers:
        running.append(_launch(pending.pop(0)))
        in_flight += 1

    done, total = 0, len(instances)
    while done < total:
        name, before, after, elapsed, note = queue.get()
        done += 1
        in_flight -= 1
        if verbose:
            if note in PROVENANCE:
                moved = "" if before is None or after == before else f" (was {before})"
                tag = {"refutation": "PROVED", "bound": "PROVED (bound)",
                       "": "open"}[note]
                print(f"[{done}/{total}] {name}: {after}{moved} {tag} "
                      f"({elapsed:.0f}s)", flush=True)
            else:
                print(f"[{done}/{total}] {name}: {note}", flush=True)
        results.append((name, before, after, elapsed, note))

        multiprocessing.active_children()  # reap whatever has exited
        while pending and in_flight < workers:
            running.append(_launch(pending.pop(0)))
            in_flight += 1

    for proc in running:
        proc.join()

    # One ledger write per sweep, not per worker: concurrent appends to the same
    # file would interleave. `benchmarks/compute.py` totals what lands here.
    from benchmarks.compute import record
    record("csearch", [(r[0], r[3]) for r in results if r[3]])
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--instances", type=str, default=None)
    parser.add_argument("--unproven", action="store_true")
    parser.add_argument("--dir", type=Path, default=DEFAULT_INSTANCE_DIR)
    parser.add_argument("--solutions-dir", type=Path, default=SOLUTIONS_DIR)
    parser.add_argument("--timeout", type=float, default=600.0)
    parser.add_argument("--max-nodes", type=int, default=None)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    from benchmarks.ratchet import find_instances, find_unproven

    if args.unproven:
        targets = find_unproven(args.dir, args.solutions_dir)
    elif args.instances:
        targets = find_instances(args.instances.split(","), args.dir)
    else:
        raise SystemExit("pass --instances or --unproven")

    print(f"{len(targets)} instances, {args.timeout:.0f}s each, "
          f"{args.workers} workers", flush=True)

    started = time.time()
    results = sweep(targets, args.timeout, workers=args.workers,
                    max_nodes=args.max_nodes, solutions_dir=args.solutions_dir)

    proved = [r for r in results if r[4] in ("refutation", "bound")]
    improved = [r for r in results if r[1] is not None and r[2] is not None
                and r[2] < r[1]]
    drop = sum(r[1] - r[2] for r in improved)
    print(f"\n{len(proved)}/{len(results)} proved optimal, "
          f"{len(improved)} improved ({drop} stacks), "
          f"in {time.time() - started:.0f}s")


if __name__ == "__main__":
    main()
