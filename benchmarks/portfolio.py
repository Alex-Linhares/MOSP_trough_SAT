"""Race several SAT backends on one formula and take the first answer.

A single decision call is the unit of work that decides how long a hard instance
takes, and it runs on one core while the rest of the machine idles: SP3 spent
12.5 hours deciding one `k` with thirty-one cores doing nothing.

Portfolio solving is the cheap way to use them. The same CNF goes to several
backends at once, the first definitive answer wins, and the rest are killed. It
is weaker than a parallel solver that shares learned clauses — Mallob and
Painless do that, and won the 2025 competition doing it — because these
processes learn nothing from each other. What it does exploit is variance: the
backends disagree wildly about which formulas are hard, and `solver_portfolio.py`
measured that directly, with Kissat closing 6 of 6 refutations where the solver
then in use closed 2.

Correctness does not depend on which one wins: whatever a backend returns is the
answer to the same formula, and a returned model is checked against the instance
before it is believed.

Usage:
    python -m benchmarks.portfolio SP3 --k 34 --timeout 36000
"""

from __future__ import annotations

import argparse
import multiprocessing
import time
from pathlib import Path
from typing import Optional, Sequence

from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from satisfiability.mosp_encoding import encode_mosp_decision, extract_ordering
from satisfiability.mosp_solver import SOLUTIONS_DIR, _save_solution

DEFAULT_INSTANCE_DIR = Path("benchmarks/instances")

# Chosen for spread rather than individual rank. The portfolio only pays when
# the backends fail on different formulas, so this mixes the four CaDiCaL
# generations, Kissat, and three unrelated lineages; `solver_portfolio.py`
# measured all of them on hard MOSP calls in both directions.
DEFAULT_BACKENDS = (
    "kissat404",     # best on refutations: 6/6
    "cadical300",    # 4/6 refutations
    "cadical195",    # fastest on satisfiable calls
    "cadical153",    # 3/6 refutations
    "lingeling",     # 3/6, unrelated lineage
    "mergesat3",     # 3/6
    "maplechrono",   # 3/6
    "glucose42",     # weak on refutations, quick on easy satisfiable calls
)


def _worker(matrix_list, n_customers, n_patterns, name, k, backend, queue):
    """Decide 'MOSP <= k?' with one backend and post the answer."""
    import numpy as np
    from pysat.solvers import Solver

    try:
        instance = MOSPInstance(
            matrix=np.array(matrix_list, dtype=np.int8),
            n_customers=n_customers, n_patterns=n_patterns, name=name,
        )
        cnf, pool, m = encode_mosp_decision(instance, k)
        with Solver(name=backend, bootstrap_with=cnf.clauses) as solver:
            if solver.solve():
                queue.put((backend, "sat", extract_ordering(solver.get_model(), pool, m)))
            else:
                queue.put((backend, "unsat", None))
    except Exception as exc:  # noqa: BLE001
        queue.put((backend, "error", f"{type(exc).__name__}: {exc}"))


def portfolio_decide(
    instance: MOSPInstance,
    k: int,
    backends: Sequence[str] = DEFAULT_BACKENDS,
    timeout: Optional[float] = None,
    verbose: bool = True,
) -> tuple[str, Optional[list[int]], Optional[str], float]:
    """Race `backends` on "MOSP(instance) <= k?".

    Returns (status, ordering, winning_backend, elapsed), where status is
    "sat", "unsat" or "timeout".
    """
    queue: multiprocessing.Queue = multiprocessing.Queue()
    payload = (instance.matrix.tolist(), instance.n_customers,
               instance.n_patterns, instance.name)

    procs = []
    for backend in backends:
        proc = multiprocessing.Process(
            target=_worker, args=(*payload, k, backend, queue))
        proc.start()
        procs.append((backend, proc))

    started = time.time()
    deadline = started + timeout if timeout is not None else None

    if verbose:
        print(f"{instance.name}: k={k}, racing {len(procs)} backends", flush=True)

    def _stop_all() -> None:
        for _, proc in procs:
            if proc.is_alive():
                proc.kill()
            proc.join()

    failed = 0
    try:
        while True:
            if deadline and time.time() > deadline:
                return "timeout", None, None, time.time() - started

            try:
                backend, status, payload_out = queue.get(timeout=1.0)
            except Exception:  # noqa: BLE001 - empty queue
                # Every backend having died without an answer is a real end
                # state, not something to wait out until the deadline.
                if not any(proc.is_alive() for _, proc in procs):
                    return "timeout", None, None, time.time() - started
                continue

            elapsed = time.time() - started
            if status == "error":
                failed += 1
                if verbose:
                    print(f"  {backend}: ERROR {payload_out}", flush=True)
                if failed == len(procs):
                    return "timeout", None, None, elapsed
                continue

            if verbose:
                print(f"  {backend}: {status.upper()} in {elapsed:.0f}s", flush=True)
            return status, payload_out, backend, elapsed
    finally:
        _stop_all()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("name", help="instance name, e.g. SP3")
    parser.add_argument("--k", type=int, required=True)
    parser.add_argument("--dir", type=Path, default=DEFAULT_INSTANCE_DIR)
    parser.add_argument("--solutions-dir", type=Path, default=SOLUTIONS_DIR)
    parser.add_argument("--timeout", type=float, default=None)
    parser.add_argument("--backends", type=str, default=None,
                        help="comma-separated; default is the measured spread")
    args = parser.parse_args()

    from benchmarks.ratchet import find_instances

    matches = find_instances([args.name], args.dir)
    if not matches:
        raise SystemExit(f"no instance named {args.name!r}")
    instance = matches[0]

    backends = tuple(b.strip() for b in args.backends.split(",")) \
        if args.backends else DEFAULT_BACKENDS

    status, ordering, winner, elapsed = portfolio_decide(
        instance, args.k, backends, timeout=args.timeout)

    if status == "sat":
        achieved = max_open_stacks(instance, ordering)
        print(f"SAT at k={args.k} in {elapsed:.0f}s via {winner}; "
              f"ordering achieves {achieved}")
        if achieved > args.k:
            raise SystemExit(f"ordering does not honour k={args.k}")
        _save_solution(instance, achieved, ordering, args.solutions_dir)
        print(f"saved to {args.solutions_dir}")
    elif status == "unsat":
        print(f"UNSAT at k={args.k} in {elapsed:.0f}s via {winner} — "
              f"so {args.k + 1} is optimal")
    else:
        print(f"no backend answered within {elapsed:.0f}s")


if __name__ == "__main__":
    main()
