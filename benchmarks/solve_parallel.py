"""Parallel batch MOSP solving with the direct SAT encoding.

Two independent axes of parallelism:

**Across instances** (``sweep``) — the benchmark collections hold thousands of
independent instances, so they fan out across cores with near-linear speedup.
Each instance still gets its own process, which keeps the terminate-on-timeout
behaviour of the sequential runner; this module just runs many at once instead
of one.

**Across k within one instance** (``one``) — binary search over k issues
``log2(gap)`` CaDiCaL calls strictly in sequence, and its *hardest* call is
almost always the UNSAT proof at the optimum minus one, which it reaches last.
Testing several k concurrently starts that proof immediately. Monotonicity
(SAT at k implies SAT at k+1) means every result shrinks the live interval, so
each round cuts it by a factor of ``workers + 1`` rather than 2, and results
that arrive early let the rest of the round be killed off.

Usage:
    python -m benchmarks.solve_parallel sweep [--workers N] [--timeout S]
    python -m benchmarks.solve_parallel one GP5 [--workers N] [--timeout S]
"""

from __future__ import annotations

import argparse
import csv
import multiprocessing
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from mosp.instance import MOSPInstance

DEFAULT_INSTANCE_DIR = Path("benchmarks/instances")

# Files in the benchmark tree that are documentation, not instances.
SKIP_PATTERNS = ("Dataset_Description", "README", "S1. Dataset")


def _should_skip(path: Path) -> bool:
    if path.suffix not in (".txt", ".dat"):
        return True
    if path.name.endswith("~"):
        return True
    return any(pattern in path.name for pattern in SKIP_PATTERNS)


def find_benchmark_files(base_dir: Path) -> list[Path]:
    return [f for f in sorted(base_dir.rglob("*")) if f.is_file() and not _should_skip(f)]


# -------------------------------------------------------
# Across instances
# -------------------------------------------------------


@dataclass
class _Job:
    """One instance awaiting or undergoing a solve."""

    dataset: str
    filename: str
    instance: MOSPInstance
    proc: Optional[multiprocessing.Process] = None
    queue: Optional[multiprocessing.Queue] = None
    started: float = 0.0


def _instance_worker(
    matrix_list: list[list[int]],
    n_customers: int,
    n_patterns: int,
    name: str,
    result_queue: multiprocessing.Queue,
) -> None:
    """Solve one instance with the direct MOSP-to-SAT encoding."""
    import numpy as np

    try:
        from mosp.verify import max_open_stacks
        from satisfiability.mosp_solver import solve_mosp_sat

        instance = MOSPInstance(
            matrix=np.array(matrix_list, dtype=np.int8),
            n_customers=n_customers,
            n_patterns=n_patterns,
            name=name,
        )
        value, ordering = solve_mosp_sat(instance, solutions_dir=None)
        result_queue.put(
            {
                "mosp_value": value,
                "verified": max_open_stacks(instance, ordering) if ordering else None,
                "error": None,
            }
        )
    except Exception as exc:  # noqa: BLE001 - reported, not swallowed
        result_queue.put({"mosp_value": None, "verified": None, "error": f"{type(exc).__name__}: {exc}"})


def _reap(job: _Job, timeout: float) -> Optional[dict]:
    """Return a result dict if the job has finished or timed out, else None."""
    elapsed = time.time() - job.started
    assert job.proc is not None and job.queue is not None

    if job.proc.is_alive():
        if elapsed < timeout:
            return None
        job.proc.terminate()
        job.proc.join(timeout=5)
        if job.proc.is_alive():
            job.proc.kill()
            job.proc.join()
        return {"status": "timeout", "mosp_value": None, "verified": None,
                "error": "", "time_seconds": elapsed}

    job.proc.join()

    # A worker that died without reporting (OOM killer, segfault) leaves the
    # queue empty; that is an error, not a silent skip.
    if job.queue.empty():
        return {"status": "error", "mosp_value": None, "verified": None,
                "error": f"worker exited with code {job.proc.exitcode}, no result",
                "time_seconds": elapsed}

    result = job.queue.get_nowait()
    status = "error" if result["error"] else "solved"
    return {"status": status, "mosp_value": result["mosp_value"],
            "verified": result["verified"], "error": result["error"] or "",
            "time_seconds": elapsed}


def sweep(
    base_dir: Path = DEFAULT_INSTANCE_DIR,
    workers: int = 0,
    timeout: float = 300.0,
    output_csv: Optional[Path] = None,
    min_size: int = 1,
    max_size: Optional[int] = None,
) -> list[dict]:
    """Solve every matching benchmark instance, `workers` at a time.

    Results are written to CSV as they complete, so a long run that is
    interrupted still leaves behind everything solved up to that point.
    """
    workers = workers or min(32, os.cpu_count() or 1)

    pending: list[_Job] = []
    unparseable: list[tuple[str, str]] = []
    for filepath in find_benchmark_files(base_dir):
        try:
            instances = MOSPInstance.from_benchmark_file(filepath)
        except Exception as exc:  # noqa: BLE001 - reported below, never silent
            unparseable.append((filepath.name, f"{type(exc).__name__}: {exc}"))
            continue
        for inst in instances:
            size = max(inst.n_customers, inst.n_patterns)
            if min(inst.n_customers, inst.n_patterns) < min_size:
                continue
            if max_size and size > max_size:
                continue
            pending.append(_Job(dataset=filepath.parent.name, filename=filepath.name, instance=inst))

    print(f"{len(pending)} instances, {workers} workers, {timeout:.0f}s timeout")
    if unparseable:
        print(f"WARNING: {len(unparseable)} file(s) could not be parsed:")
        for filename, reason in unparseable[:10]:
            print(f"  {filename}: {reason}")
        if len(unparseable) > 10:
            print(f"  ... and {len(unparseable) - 10} more")
    print()

    writer = None
    handle = None
    if output_csv:
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        handle = open(output_csv, "w", newline="")
        writer = csv.DictWriter(
            handle,
            fieldnames=["dataset", "filename", "instance_name", "n_customers",
                        "n_patterns", "mosp_value", "verified", "time_seconds",
                        "status", "error"],
        )
        writer.writeheader()

    results: list[dict] = []
    running: list[_Job] = []
    queue_index = 0
    done = 0

    try:
        while queue_index < len(pending) or running:
            while len(running) < workers and queue_index < len(pending):
                job = pending[queue_index]
                queue_index += 1
                job.queue = multiprocessing.Queue()
                job.proc = multiprocessing.Process(
                    target=_instance_worker,
                    args=(job.instance.matrix.tolist(), job.instance.n_customers,
                          job.instance.n_patterns, job.instance.name, job.queue),
                )
                job.started = time.time()
                job.proc.start()
                running.append(job)

            still_running = []
            for job in running:
                outcome = _reap(job, timeout)
                if outcome is None:
                    still_running.append(job)
                    continue

                done += 1
                row = {
                    "dataset": job.dataset,
                    "filename": job.filename,
                    "instance_name": job.instance.name,
                    "n_customers": job.instance.n_customers,
                    "n_patterns": job.instance.n_patterns,
                    "mosp_value": outcome["mosp_value"],
                    "verified": outcome["verified"],
                    "time_seconds": round(outcome["time_seconds"], 3),
                    "status": outcome["status"],
                    "error": outcome["error"],
                }
                results.append(row)
                if writer:
                    writer.writerow(row)
                    handle.flush()

                label = f"[{done}/{len(pending)}] {job.instance.name} " \
                        f"({job.instance.n_customers}x{job.instance.n_patterns})"
                if outcome["status"] == "solved":
                    print(f"{label}: MOSP={outcome['mosp_value']} {outcome['time_seconds']:.1f}s")
                elif outcome["status"] == "timeout":
                    print(f"{label}: TIMEOUT")
                else:
                    print(f"{label}: ERROR {outcome['error']}")

            running = still_running
            if running:
                time.sleep(0.05)
    finally:
        for job in running:
            if job.proc and job.proc.is_alive():
                job.proc.kill()
                job.proc.join()
        if handle:
            handle.close()

    solved = sum(1 for r in results if r["status"] == "solved")
    print()
    print(f"solved {solved}/{len(results)}  "
          f"timeout {sum(1 for r in results if r['status'] == 'timeout')}  "
          f"error {sum(1 for r in results if r['status'] == 'error')}")
    if output_csv:
        print(f"results: {output_csv}")
    return results


# -------------------------------------------------------
# Across k, for one instance
# -------------------------------------------------------


def _decision_worker(
    matrix_list: list[list[int]],
    n_customers: int,
    n_patterns: int,
    name: str,
    k: int,
    result_queue: multiprocessing.Queue,
) -> None:
    """Decide 'MOSP <= k?' and report SAT (with a witness) or UNSAT."""
    import numpy as np

    try:
        from pysat.solvers import Cadical153

        from satisfiability.mosp_encoding import encode_mosp_decision, extract_ordering

        instance = MOSPInstance(
            matrix=np.array(matrix_list, dtype=np.int8),
            n_customers=n_customers,
            n_patterns=n_patterns,
            name=name,
        )
        cnf, pool, m = encode_mosp_decision(instance, k)
        with Cadical153(bootstrap_with=cnf.clauses) as solver:
            if solver.solve():
                ordering = extract_ordering(solver.get_model(), pool, m)
                result_queue.put({"k": k, "sat": True, "ordering": ordering, "error": None})
            else:
                result_queue.put({"k": k, "sat": False, "ordering": None, "error": None})
    except Exception as exc:  # noqa: BLE001
        result_queue.put({"k": k, "sat": None, "ordering": None,
                          "error": f"{type(exc).__name__}: {exc}"})


@dataclass
class _Probe:
    k: int
    proc: multiprocessing.Process
    queue: multiprocessing.Queue
    started: float = field(default_factory=time.time)


def solve_one_parallel(
    instance: MOSPInstance,
    workers: int = 0,
    timeout: Optional[float] = None,
    verbose: bool = True,
) -> tuple[Optional[int], Optional[list[int]]]:
    """Find the exact MOSP optimum by testing many k concurrently.

    Maintains the invariant that `lo` is one above the largest k proven UNSAT
    and `hi` is the smallest k proven SAT. Each round probes up to `workers`
    evenly spaced k inside the live interval; every answer shrinks it, and
    probes that the answer has made irrelevant are killed rather than awaited.

    Returns (optimum, ordering), or (None, None) if the timeout hit first.
    """
    from satisfiability.mosp_solver import _lower_bound, _upper_bound

    workers = workers or min(32, os.cpu_count() or 1)
    deadline = time.time() + timeout if timeout is not None else None

    lo = _lower_bound(instance)
    hi, best_ordering = _upper_bound(instance)
    if verbose:
        print(f"{instance.name}: {instance.n_customers}x{instance.n_patterns}  "
              f"lb={lo} ub={hi} (tabu)  workers={workers}")

    if lo >= hi:
        if verbose:
            print(f"bounds meet at {hi}; no SAT call needed")
        return hi, best_ordering

    payload = (instance.matrix.tolist(), instance.n_customers,
               instance.n_patterns, instance.name)
    round_num = 0

    while lo < hi:
        # Probe evenly spaced k strictly inside (lo - 1, hi): lo..hi-1 are the
        # values still capable of being the optimum.
        candidates = list(range(lo, hi))
        if len(candidates) > workers:
            step = len(candidates) / (workers + 1)
            picked = sorted({candidates[min(int(step * (i + 1)), len(candidates) - 1)]
                             for i in range(workers)})
        else:
            picked = candidates

        round_num += 1
        if verbose:
            print(f"round {round_num}: interval [{lo},{hi}], probing k={picked}")

        probes: list[_Probe] = []
        for k in picked:
            queue: multiprocessing.Queue = multiprocessing.Queue()
            proc = multiprocessing.Process(target=_decision_worker,
                                           args=(*payload, k, queue))
            proc.start()
            probes.append(_Probe(k=k, proc=proc, queue=queue))

        def _kill_all() -> None:
            for probe in probes:
                if probe.proc.is_alive():
                    probe.proc.kill()
                probe.proc.join()

        try:
            while probes:
                if deadline and time.time() > deadline:
                    _kill_all()
                    if verbose:
                        print(f"timeout; optimum is in [{lo},{hi}]")
                    return None, None

                remaining = []
                for probe in probes:
                    if probe.proc.is_alive():
                        remaining.append(probe)
                        continue
                    probe.proc.join()
                    if probe.queue.empty():
                        if verbose:
                            print(f"  k={probe.k}: worker died "
                                  f"(exit {probe.proc.exitcode})")
                        continue
                    answer = probe.queue.get_nowait()
                    if answer["error"]:
                        if verbose:
                            print(f"  k={probe.k}: ERROR {answer['error']}")
                        continue
                    if answer["sat"]:
                        if answer["k"] < hi:
                            hi = answer["k"]
                            best_ordering = answer["ordering"]
                        if verbose:
                            print(f"  k={probe.k}: SAT   -> hi={hi}")
                    else:
                        lo = max(lo, answer["k"] + 1)
                        if verbose:
                            print(f"  k={probe.k}: UNSAT -> lo={lo}")

                probes = remaining
                # Any probe whose answer can no longer move the interval is
                # wasted work: k >= hi is known SAT, k < lo known UNSAT.
                survivors = []
                for probe in probes:
                    if probe.k >= hi or probe.k < lo:
                        probe.proc.kill()
                        probe.proc.join()
                    else:
                        survivors.append(probe)
                probes = survivors
                if probes:
                    time.sleep(0.05)
        finally:
            _kill_all()

    if verbose:
        print(f"optimum: {hi}")
    return hi, best_ordering


# -------------------------------------------------------
# CLI
# -------------------------------------------------------


def _find_named_instance(name: str, base_dir: Path) -> Optional[MOSPInstance]:
    for filepath in find_benchmark_files(base_dir):
        try:
            instances = MOSPInstance.from_benchmark_file(filepath)
        except Exception:  # noqa: BLE001
            continue
        for inst in instances:
            if inst.name == name:
                return inst
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="mode", required=True)

    p_sweep = sub.add_parser("sweep", help="solve many instances in parallel")
    p_sweep.add_argument("--dir", type=Path, default=DEFAULT_INSTANCE_DIR)
    p_sweep.add_argument("--workers", type=int, default=0, help="default: min(32, cores)")
    p_sweep.add_argument("--timeout", type=float, default=300.0)
    p_sweep.add_argument("--output", type=Path, default=None)
    p_sweep.add_argument("--min-size", type=int, default=1)
    p_sweep.add_argument("--max-size", type=int, default=None)

    p_one = sub.add_parser("one", help="solve one instance, parallel over k")
    p_one.add_argument("name", help="instance name, e.g. GP5")
    p_one.add_argument("--dir", type=Path, default=DEFAULT_INSTANCE_DIR)
    p_one.add_argument("--workers", type=int, default=0)
    p_one.add_argument("--timeout", type=float, default=None)

    args = parser.parse_args()

    if args.mode == "sweep":
        sweep(base_dir=args.dir, workers=args.workers, timeout=args.timeout,
              output_csv=args.output, min_size=args.min_size, max_size=args.max_size)
        return

    instance = _find_named_instance(args.name, args.dir)
    if instance is None:
        raise SystemExit(f"no instance named {args.name!r} under {args.dir}")

    from mosp.verify import max_open_stacks

    start = time.time()
    value, ordering = solve_one_parallel(instance, workers=args.workers, timeout=args.timeout)
    if value is None:
        raise SystemExit("timed out")
    print(f"{args.name}: MOSP={value} verified={max_open_stacks(instance, ordering)} "
          f"({time.time() - start:.1f}s)")


if __name__ == "__main__":
    main()
