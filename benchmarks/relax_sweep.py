"""Certified lower bounds by contraction, across many instances at once.

`satisfiability/relaxation.py` settles one instance at one contraction depth.
This runs a ladder of depths over every open instance in parallel, which is
worth doing now for a reason that was not true this morning: the bound that cost
94 seconds in Python costs about one in C, so the whole ladder is affordable.

For each instance it contracts to a series of targets, loosest first, and solves
each contraction outright. By Chu & Stuckey's Lemma 1 a contraction is a
relaxation, so its optimum bounds the original's from below. The ladder stops
early when a bound reaches the cached upper bound, because at that point the
instance is settled -- there is nothing between the bounds left to search.

**What this writes and does not write.** Nothing, by default. A bound that meets
the upper bound would close an instance, but it would close it on Lemma 1, which
this project has measured on 3,167 contractions and not proved, and whose source
(Becceneri, Yanasse & Soma 2004) it does not hold. That is a different footing
from a refutation, so recording it is a deliberate act behind `--record`, not a
side effect of measuring.

Usage:
    python -m benchmarks.relax_sweep --unproven --workers 6
"""

from __future__ import annotations

import argparse
import multiprocessing
import time
from pathlib import Path

from mosp.instance import MOSPInstance
from satisfiability.mosp_solver import SOLUTIONS_DIR

DEFAULT_INSTANCE_DIR = Path("benchmarks/instances")

# Fractions of the way from the upper bound up to the full instance. Loosest
# first: a loose contraction is quick and its bound is weak, and the ladder
# stops as soon as one is good enough.
DEFAULT_LADDER = (0.0, 0.25, 0.5, 0.65, 0.8, 0.9)


def _worker(matrix_list, n_customers, n_patterns, name, ladder, budget, record,
            queue):
    import numpy as np

    from satisfiability.mosp_solver import (
        _load_solution, _lower_bound, _save_solution)
    from satisfiability.relaxation import lower_bound

    started = time.time()
    try:
        instance = MOSPInstance(
            matrix=np.array(matrix_list, dtype=np.int8),
            n_customers=n_customers, n_patterns=n_patterns, name=name)
        cached = _load_solution(instance, SOLUTIONS_DIR)
        upper = cached[0] if cached else n_customers
        base = _lower_bound(instance)

        best, best_at = base, None
        for fraction in ladder:
            target = min(n_customers,
                         int(round(upper + (n_customers - upper) * fraction)))
            bound, groups = lower_bound(instance, target, time_budget=budget)
            if bound > best:
                best, best_at = bound, groups
            if best >= upper:
                break
        if record and best > base and cached:
            # Only the bound is written; the value and its witness are left
            # exactly as they were.
            _save_solution(instance, cached[0], cached[1], SOLUTIONS_DIR,
                           provenance=_provenance_of(name),
                           lower_bound=best, lower_bound_source="relaxation")
        queue.put((name, base, best, best_at, upper, time.time() - started, None))
    except Exception as exc:  # noqa: BLE001
        queue.put((name, None, None, None, None, time.time() - started,
                   f"{type(exc).__name__}: {exc}"))


def _provenance_of(name: str) -> str:
    """Whatever the file already claims -- recording a bound must not change it."""
    import json

    from satisfiability.mosp_solver import PROVENANCE_SOLUTION, _solution_path

    path = SOLUTIONS_DIR / f"{name}.json"
    if not path.exists():
        return PROVENANCE_SOLUTION
    try:
        return json.loads(path.read_text()).get("provenance", PROVENANCE_SOLUTION)
    except Exception:  # noqa: BLE001
        return PROVENANCE_SOLUTION


def sweep(instances, ladder=DEFAULT_LADDER, budget=60.0, workers=6,
          record=False, verbose=True):
    """Best certified bound per instance. One row each."""
    queue: multiprocessing.Queue = multiprocessing.Queue()
    pending, running, results = list(instances), [], []
    in_flight = 0

    def launch(inst):
        proc = multiprocessing.Process(
            target=_worker,
            args=(inst.matrix.tolist(), inst.n_customers, inst.n_patterns,
                  inst.name, tuple(ladder), budget, record, queue))
        proc.start()
        return proc

    while pending and in_flight < workers:
        running.append(launch(pending.pop(0))); in_flight += 1

    done = 0
    while done < len(instances):
        name, base, best, at, upper, secs, error = queue.get()
        done += 1; in_flight -= 1
        if verbose:
            if error:
                print(f"[{done}/{len(instances)}] {name}: {error}", flush=True)
            else:
                settled = " SETTLED" if best >= upper else ""
                moved = f" (was {base})" if best > base else ""
                where = f" at {at} customers" if at else ""
                print(f"[{done}/{len(instances)}] {name}: lb {best}{moved}"
                      f" vs ub {upper}, gap {upper - best}{where} "
                      f"({secs:.0f}s){settled}", flush=True)
        results.append((name, base, best, upper, secs, error))

        multiprocessing.active_children()
        while pending and in_flight < workers:
            running.append(launch(pending.pop(0))); in_flight += 1

    for proc in running:
        proc.join()
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--unproven", action="store_true")
    parser.add_argument("--instances", type=str, default=None)
    parser.add_argument("--dir", type=Path, default=DEFAULT_INSTANCE_DIR)
    parser.add_argument("--solutions-dir", type=Path, default=SOLUTIONS_DIR)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--budget", type=float, default=60.0,
                        help="seconds per contraction depth")
    parser.add_argument("--record", action="store_true",
                        help="write the bounds into solutions/ (see the module "
                             "docstring on what that claim rests on)")
    args = parser.parse_args()

    from benchmarks.ratchet import find_instances, find_unproven

    if args.unproven:
        targets = find_unproven(args.dir, args.solutions_dir)
    elif args.instances:
        targets = find_instances(args.instances.split(","), args.dir)
    else:
        raise SystemExit("pass --instances or --unproven")

    print(f"{len(targets)} instances, {args.workers} workers, "
          f"{args.budget:.0f}s per depth", flush=True)
    started = time.time()
    results = sweep(targets, budget=args.budget, workers=args.workers,
                    record=args.record)

    improved = [r for r in results if r[1] is not None and r[2] > r[1]]
    settled = [r for r in results if r[2] is not None and r[2] >= r[3]]
    total_gap_before = sum(r[3] - r[1] for r in results if r[1] is not None)
    total_gap_after = sum(r[3] - r[2] for r in results if r[2] is not None)
    print(f"\n{len(improved)}/{len(results)} bounds improved, "
          f"{len(settled)} reached the upper bound, "
          f"total gap {total_gap_before} -> {total_gap_after}, "
          f"in {time.time() - started:.0f}s")


if __name__ == "__main__":
    main()
