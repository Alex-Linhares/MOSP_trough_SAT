"""Batch solver for published MOSP benchmark instances.

Walks benchmarks/instances/ recursively, parses all benchmark files using
MOSPInstance.from_benchmark_file(), solves each instance with a per-instance
timeout, and writes results to CSV.

Usage:
    python -m benchmarks.solve_all [--timeout SECONDS] [--output PATH]
"""

from __future__ import annotations

import argparse
import csv
import multiprocessing
import sys
import time
from pathlib import Path
from typing import Optional

from mosp.instance import MOSPInstance
from mosp.solver import solve_mosp


# Files to skip (descriptions, READMEs, PDFs, backup files)
SKIP_PATTERNS = {
    "Dataset_Description",
    "README",
    "S1. Dataset",
}


def _should_skip(path: Path) -> bool:
    """Check if a file should be skipped."""
    if path.suffix not in (".txt", ".dat"):
        return True
    for pattern in SKIP_PATTERNS:
        if pattern in path.name:
            return True
    if path.name.endswith("~"):
        return True
    return False


def _get_dataset_name(filepath: Path) -> str:
    """Extract a dataset name from the file path.

    E.g. .../MOSP_Instances/Challenge/GP1.txt -> "Challenge"
         .../ChallengeInstances2005/Harvey/wbo_10_10.txt -> "Harvey"
    """
    return filepath.parent.name


def _solve_worker(
    matrix_list: list[list[int]],
    n_customers: int,
    n_patterns: int,
    name: str,
    result_queue: multiprocessing.Queue,
) -> None:
    """Worker function for solving a single instance in a subprocess."""
    import numpy as np

    try:
        instance = MOSPInstance(
            matrix=np.array(matrix_list, dtype=np.int8),
            n_customers=n_customers,
            n_patterns=n_patterns,
            name=name,
        )
        solution = solve_mosp(instance)
        result_queue.put({
            "mosp_value": solution.max_open_stacks,
            "pathwidth": solution.pathwidth,
            "ordering": solution.ordering,
            "error": None,
        })
    except Exception as e:
        result_queue.put({
            "mosp_value": None,
            "pathwidth": None,
            "ordering": None,
            "error": str(e),
        })


def solve_with_timeout(
    instance: MOSPInstance, timeout: float
) -> dict:
    """Solve a MOSP instance with a timeout.

    Returns a result dict with keys: mosp_value, pathwidth, time_seconds,
    status, error.
    """
    queue: multiprocessing.Queue = multiprocessing.Queue()
    proc = multiprocessing.Process(
        target=_solve_worker,
        args=(
            instance.matrix.tolist(),
            instance.n_customers,
            instance.n_patterns,
            instance.name,
            queue,
        ),
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
        return {
            "mosp_value": None,
            "pathwidth": None,
            "time_seconds": elapsed,
            "status": "timeout",
            "error": None,
        }

    if proc.exitcode != 0:
        return {
            "mosp_value": None,
            "pathwidth": None,
            "time_seconds": elapsed,
            "status": "error",
            "error": f"Process exited with code {proc.exitcode}",
        }

    if not queue.empty():
        result = queue.get_nowait()
        status = "solved" if result["error"] is None else "error"
        return {
            "mosp_value": result["mosp_value"],
            "pathwidth": result["pathwidth"],
            "time_seconds": elapsed,
            "status": status,
            "error": result["error"],
        }

    return {
        "mosp_value": None,
        "pathwidth": None,
        "time_seconds": elapsed,
        "status": "error",
        "error": "No result from worker",
    }


def find_benchmark_files(base_dir: Path) -> list[Path]:
    """Find all benchmark instance files recursively."""
    files = []
    for f in sorted(base_dir.rglob("*")):
        if f.is_file() and not _should_skip(f):
            files.append(f)
    return files


def run_all(
    base_dir: Path,
    timeout: float = 60.0,
    output_csv: Optional[Path] = None,
    max_patterns: Optional[int] = None,
) -> list[dict]:
    """Parse and solve all benchmark instances.

    Args:
        base_dir: Root directory containing benchmark instance files.
        timeout: Per-instance timeout in seconds.
        output_csv: Path to write CSV results.
        max_patterns: If set, only solve instances with n_patterns <= this.

    Returns:
        List of result dictionaries.
    """
    files = find_benchmark_files(base_dir)
    print(f"Found {len(files)} benchmark files in {base_dir}")
    if max_patterns is not None:
        print(f"Filtering to instances with n_patterns <= {max_patterns}")
    print()

    all_results: list[dict] = []
    total_instances = 0

    for filepath in files:
        dataset = _get_dataset_name(filepath)
        try:
            instances = MOSPInstance.from_benchmark_file(filepath)
        except Exception as e:
            print(f"  PARSE ERROR: {filepath}: {e}")
            all_results.append({
                "dataset": dataset,
                "filename": filepath.name,
                "instance_name": filepath.stem,
                "n_customers": None,
                "n_patterns": None,
                "mosp_value": None,
                "pathwidth": None,
                "time_seconds": 0,
                "status": "parse_error",
                "error": str(e),
            })
            continue

        for inst in instances:
            if max_patterns is not None and inst.n_patterns > max_patterns:
                continue
            total_instances += 1
            print(
                f"[{total_instances}] {dataset}/{filepath.name}: "
                f"{inst.name} ({inst.n_customers}x{inst.n_patterns}) ... ",
                end="",
                flush=True,
            )

            result = solve_with_timeout(inst, timeout)

            status = result["status"]
            if status == "solved":
                print(
                    f"MOSP={result['mosp_value']} "
                    f"(pw={result['pathwidth']}) "
                    f"{result['time_seconds']:.2f}s"
                )
            elif status == "timeout":
                print(f"TIMEOUT ({timeout}s)")
            else:
                print(f"ERROR: {result['error']}")

            all_results.append({
                "dataset": dataset,
                "filename": filepath.name,
                "instance_name": inst.name,
                "n_customers": inst.n_customers,
                "n_patterns": inst.n_patterns,
                "mosp_value": result["mosp_value"],
                "pathwidth": result["pathwidth"],
                "time_seconds": round(result["time_seconds"], 3),
                "status": result["status"],
                "error": result["error"] or "",
            })

    # Write CSV
    if output_csv and all_results:
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = [
            "dataset", "filename", "instance_name", "n_customers",
            "n_patterns", "mosp_value", "pathwidth", "time_seconds",
            "status", "error",
        ]
        with open(output_csv, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)
        print(f"\nResults written to {output_csv}")

    # Print summary table
    print()
    print("=" * 78)
    print(f"{'Dataset':<25} {'Total':>6} {'Solved':>7} {'Timeout':>8} {'Error':>6} {'Avg(s)':>8}")
    print("-" * 78)

    datasets = {}
    for r in all_results:
        ds = r["dataset"]
        if ds not in datasets:
            datasets[ds] = {"total": 0, "solved": 0, "timeout": 0, "error": 0, "times": []}
        datasets[ds]["total"] += 1
        if r["status"] == "solved":
            datasets[ds]["solved"] += 1
            datasets[ds]["times"].append(r["time_seconds"])
        elif r["status"] == "timeout":
            datasets[ds]["timeout"] += 1
        else:
            datasets[ds]["error"] += 1

    total_all = total_solved = total_timeout = total_error = 0
    for ds, stats in sorted(datasets.items()):
        avg_t = sum(stats["times"]) / len(stats["times"]) if stats["times"] else 0
        print(
            f"{ds:<25} {stats['total']:>6} {stats['solved']:>7} "
            f"{stats['timeout']:>8} {stats['error']:>6} {avg_t:>8.2f}"
        )
        total_all += stats["total"]
        total_solved += stats["solved"]
        total_timeout += stats["timeout"]
        total_error += stats["error"]

    print("-" * 78)
    all_times = [r["time_seconds"] for r in all_results if r["status"] == "solved"]
    avg_all = sum(all_times) / len(all_times) if all_times else 0
    print(
        f"{'TOTAL':<25} {total_all:>6} {total_solved:>7} "
        f"{total_timeout:>8} {total_error:>6} {avg_all:>8.2f}"
    )
    print("=" * 78)

    return all_results


def main():
    parser = argparse.ArgumentParser(
        description="Solve all published MOSP benchmark instances."
    )
    parser.add_argument(
        "--instances", type=str,
        default="benchmarks/instances",
        help="Root directory of benchmark instances (default: benchmarks/instances)",
    )
    parser.add_argument(
        "--timeout", type=float, default=60.0,
        help="Per-instance timeout in seconds (default: 60)",
    )
    parser.add_argument(
        "--output", type=str,
        default="benchmarks/results/all_benchmarks.csv",
        help="Output CSV path (default: benchmarks/results/all_benchmarks.csv)",
    )
    parser.add_argument(
        "--max-patterns", type=int, default=None,
        help="Only solve instances with n_patterns <= this value",
    )
    args = parser.parse_args()

    base_dir = Path(args.instances)
    if not base_dir.exists():
        print(f"Error: {base_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    output_csv = Path(args.output)
    run_all(base_dir, timeout=args.timeout, output_csv=output_csv,
            max_patterns=args.max_patterns)


if __name__ == "__main__":
    main()
