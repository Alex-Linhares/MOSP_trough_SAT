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
import time
from pathlib import Path
from typing import Optional

from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from satisfiability.mosp_encoding import encode_mosp_decision, extract_ordering
from satisfiability.mosp_solver import (
    SAT_BACKEND,
    SOLUTIONS_DIR,
    _lower_bound,
    _save_solution,
    _solution_path,
    _upper_bound,
)

DEFAULT_INSTANCE_DIR = Path("benchmarks/instances")


def _sat_at(instance: MOSPInstance, k: int) -> Optional[list[int]]:
    """Return a witness ordering with at most k open stacks, or None."""
    from pysat.solvers import Solver

    cnf, pool, n_patterns = encode_mosp_decision(instance, k)
    with Solver(name=SAT_BACKEND, bootstrap_with=cnf.clauses) as solver:
        if solver.solve():
            return extract_ordering(solver.get_model(), pool, n_patterns)
    return None


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
        found = _sat_at(instance, best)
        if found is None:
            if verbose:
                print(f"  k={best}: UNSAT — start value is below the optimum",
                      flush=True)
            return None, None, False
        best_ordering = found

    _save_solution(instance, max_open_stacks(instance, best_ordering),
                   best_ordering, solutions_dir)

    while best > lower:
        if deadline and time.time() > deadline:
            if verbose:
                print(f"  timeout with best={best} (lb={lower})", flush=True)
            break

        target = best - 1
        started = time.time()
        found = _sat_at(instance, target)
        elapsed = time.time() - started

        if found is None:
            # A refutation, which also proves the current best is optimal.
            if verbose:
                print(f"  k={target}: UNSAT in {elapsed:.0f}s — {best} is optimal",
                      flush=True)
            return best, best_ordering, True

        actual = max_open_stacks(instance, found)
        best, best_ordering = min(actual, target), found
        _save_solution(instance, best, best_ordering, solutions_dir)
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
    args = parser.parse_args()

    if args.unsolved:
        targets = find_unsolved(args.dir, args.solutions_dir)
    elif args.instances:
        targets = find_instances(args.instances.split(","), args.dir)
    else:
        raise SystemExit("pass --instances or --unsolved")

    if not targets:
        raise SystemExit("no matching instances")

    closed = improved = 0
    for inst in targets:
        value, _, proven = ratchet(inst, start=args.start, timeout=args.timeout,
                                   solutions_dir=args.solutions_dir)
        if proven:
            closed += 1
        elif value is not None:
            improved += 1
        print(flush=True)

    print(f"closed {closed}, improved without proof {improved}, "
          f"of {len(targets)} instances")


if __name__ == "__main__":
    main()
