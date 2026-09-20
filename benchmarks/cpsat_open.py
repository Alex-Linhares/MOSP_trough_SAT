"""CP-SAT against the instances that are still open.

Its authors report this model as weakest exactly here -- many patterns, sparse
MOSP graph -- so closing one would be a surprise. Two other outcomes are not:

- **an upper bound.** CP-SAT's incumbent is a real sequence, re-simulated here
  before it is believed, and a better one shortens every future descent.
- **a lower bound, on a better footing than the ones we have.** CP-SAT's
  `BestObjectiveBound` is proved by the solver against a model this project has
  checked against exhaustive search and against 5,266 corpus optima. Our current
  bounds come from contraction and rest additionally on Chu & Stuckey's Lemma 1,
  which is measured here and never proved. A CP-SAT bound of equal value is the
  stronger claim, and one that meets an upper bound closes an instance without
  Lemma 1 in the chain at all.

    python -m benchmarks.cpsat_open --hours 24 --workers 26 --record
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
    PROVENANCE_SOLUTION,
    SOLUTIONS_DIR,
    _load_solution,
    _save_solution,
    load_lower_bound,
)

DEFAULT_INSTANCE_DIR = Path("benchmarks/instances")


def _worker(matrix_list, n_customers, n_patterns, name, seconds, record,
            solutions_dir, queue):
    import numpy as np

    from satisfiability.cpsat import solve_cpsat

    started = time.time()
    try:
        instance = MOSPInstance(
            matrix=np.array(matrix_list, dtype=np.int8),
            n_customers=n_customers, n_patterns=n_patterns, name=name)
        cached = _load_solution(instance, solutions_dir)
        ours_ub = cached[0] if cached else None
        recorded = load_lower_bound(instance, solutions_dir)
        ours_lb = recorded[0] if recorded else 0

        # Start from what is already known: the witness as a hint, and its
        # value as a ceiling. The recorded lower bound is deliberately NOT
        # passed -- it comes from contraction and rests on Lemma 1, and
        # CP-SAT's own bound is worth having precisely because it does not.
        answer = solve_cpsat(instance, max_seconds=seconds, workers=1,
                             upper=ours_ub,
                             hint=cached[1] if cached else None)

        better_ub = better_lb = None
        if answer.value is not None and answer.ordering:
            # Never trust the value; trust the sequence, simulated here.
            achieved = max_open_stacks(instance, answer.ordering)
            if ours_ub is None or achieved < ours_ub:
                better_ub = achieved
                if record:
                    _save_solution(instance, achieved, answer.ordering,
                                   solutions_dir)
        if answer.best_bound is not None and answer.best_bound > ours_lb:
            better_lb = answer.best_bound
            if record and cached:
                # The witness is untouched; only the bound is added. If the
                # bound reaches the value the instance is settled -- and by
                # certified:bound rather than certified:relaxation, because a
                # CP-SAT bound does not rest on Lemma 1.
                value = better_ub if better_ub is not None else cached[0]
                witness = answer.ordering if better_ub is not None else cached[1]
                settled = answer.best_bound >= value
                _save_solution(
                    instance, value, witness, solutions_dir,
                    provenance=PROVENANCE_BOUND if settled else PROVENANCE_SOLUTION,
                    lower_bound=min(answer.best_bound, value),
                    lower_bound_source="cpsat")

        queue.put((name, ours_lb, ours_ub, answer.status, answer.value,
                   answer.best_bound, better_ub, better_lb,
                   time.time() - started, None))
    except Exception as exc:  # noqa: BLE001
        queue.put((name, None, None, "ERROR", None, None, None, None,
                   time.time() - started, f"{type(exc).__name__}: {exc}"))


def sweep(instances, seconds, workers, record, solutions_dir=SOLUTIONS_DIR):
    queue: multiprocessing.Queue = multiprocessing.Queue()
    pending, running, in_flight = list(instances), [], 0

    def launch(inst):
        proc = multiprocessing.Process(
            target=_worker,
            args=(inst.matrix.tolist(), inst.n_customers, inst.n_patterns,
                  inst.name, seconds, record, solutions_dir, queue))
        proc.start()
        return proc

    while pending and in_flight < workers:
        running.append(launch(pending.pop(0))); in_flight += 1

    done, closed, ub_wins, lb_wins = 0, 0, 0, 0
    while done < len(instances):
        (name, lb, ub, status, value, bound, better_ub, better_lb, secs,
         error) = queue.get()
        done += 1; in_flight -= 1
        if error:
            print(f"[{done}/{len(instances)}] {name}: {error}", flush=True)
        else:
            notes = []
            if better_ub is not None:
                notes.append(f"ub {ub} -> {better_ub}"); ub_wins += 1
            if better_lb is not None:
                notes.append(f"lb {lb} -> {better_lb}"); lb_wins += 1
            if status == "OPTIMAL":
                notes.append("CLOSED"); closed += 1
            print(f"[{done}/{len(instances)}] {name}: {status} "
                  f"value={value} bound={bound} ({secs / 3600:.1f}h)"
                  f"{'  ' + ', '.join(notes) if notes else ''}", flush=True)

        multiprocessing.active_children()
        while pending and in_flight < workers:
            running.append(launch(pending.pop(0))); in_flight += 1

    for proc in running:
        proc.join()
    return closed, ub_wins, lb_wins


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--hours", type=float, default=24.0)
    parser.add_argument("--workers", type=int, default=26)
    parser.add_argument("--record", action="store_true")
    parser.add_argument("--dir", type=Path, default=DEFAULT_INSTANCE_DIR)
    parser.add_argument("--solutions-dir", type=Path, default=SOLUTIONS_DIR)
    args = parser.parse_args()

    from benchmarks.ratchet import find_unproven

    targets, seen = [], set()
    for inst in find_unproven(args.dir, args.solutions_dir):
        if inst.name not in seen:
            seen.add(inst.name)
            targets.append(inst)

    seconds = args.hours * 3600
    print(f"{len(targets)} open instances, {args.hours:.0f}h each, "
          f"{args.workers} workers, record={args.record}", flush=True)
    started = time.time()
    closed, ub_wins, lb_wins = sweep(targets, seconds, args.workers,
                                     args.record, args.solutions_dir)
    print(f"\n{closed} closed, {ub_wins} upper bounds improved, "
          f"{lb_wins} lower bounds improved, in "
          f"{(time.time() - started) / 3600:.1f}h")


if __name__ == "__main__":
    main()
