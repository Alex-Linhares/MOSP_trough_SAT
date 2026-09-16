"""Batch SAT solver for large MOSP benchmark instances.

Targets instances where both n_customers > 30 and n_patterns > 30 — the 220
instances that the branch-and-bound solver cannot handle. Uses the customer
intersection graph approach with the SAT-based pathwidth solver.

Usage:
    python -m benchmarks.solve_all_sat [--timeout SECONDS] [--output PATH]
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


# Files to skip
SKIP_PATTERNS = {
    "Dataset_Description",
    "README",
    "S1. Dataset",
}


def _should_skip(path: Path) -> bool:
    if path.suffix not in (".txt", ".dat"):
        return True
    for pattern in SKIP_PATTERNS:
        if pattern in path.name:
            return True
    if path.name.endswith("~"):
        return True
    return False


def _get_dataset_name(filepath: Path) -> str:
    return filepath.parent.name


def _solve_worker_sat(
    matrix_list: list[list[int]],
    n_customers: int,
    n_patterns: int,
    name: str,
    result_queue: multiprocessing.Queue,
) -> None:
    """Worker: solve via customer graph + SAT pathwidth solver."""
    import numpy as np

    try:
        instance = MOSPInstance(
            matrix=np.array(matrix_list, dtype=np.int8),
            n_customers=n_customers,
            n_patterns=n_patterns,
            name=name,
        )
        from customer_inter.reduction import mosp_to_pathwidth, pathwidth_to_mosp
        from satisfiability.solver import compute_pathwidth_sat
        from mosp.verify import max_open_stacks

        # Build customer graph
        pw_problem = mosp_to_pathwidth(instance)
        n_nodes = pw_problem.graph.number_of_nodes()
        n_edges = pw_problem.graph.number_of_edges()

        # Solve pathwidth with SAT
        pathwidth, customer_ordering = compute_pathwidth_sat(pw_problem.graph)

        # Convert to MOSP solution
        solution = pathwidth_to_mosp(pw_problem, pathwidth, customer_ordering)
        actual_mosp = max_open_stacks(instance, solution.ordering)

        result_queue.put({
            "mosp_value": actual_mosp,
            "pathwidth": pathwidth,
            "n_graph_nodes": n_nodes,
            "n_graph_edges": n_edges,
            "error": None,
        })
    except Exception as e:
        import traceback
        result_queue.put({
            "mosp_value": None,
            "pathwidth": None,
            "n_graph_nodes": None,
            "n_graph_edges": None,
            "error": f"{type(e).__name__}: {e}",
        })


def solve_with_timeout_sat(instance: MOSPInstance, timeout: float) -> dict:
    """Solve a MOSP instance with the SAT solver and a timeout."""
    queue: multiprocessing.Queue = multiprocessing.Queue()
    proc = multiprocessing.Process(
        target=_solve_worker_sat,
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
            "n_graph_nodes": None,
            "n_graph_edges": None,
            "time_seconds": elapsed,
            "status": "timeout",
            "error": None,
        }

    if proc.exitcode != 0:
        return {
            "mosp_value": None,
            "pathwidth": None,
            "n_graph_nodes": None,
            "n_graph_edges": None,
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
            "n_graph_nodes": result["n_graph_nodes"],
            "n_graph_edges": result["n_graph_edges"],
            "time_seconds": elapsed,
            "status": status,
            "error": result["error"],
        }

    return {
        "mosp_value": None,
        "pathwidth": None,
        "n_graph_nodes": None,
        "n_graph_edges": None,
        "time_seconds": elapsed,
        "status": "error",
        "error": "No result from worker",
    }


def find_benchmark_files(base_dir: Path) -> list[Path]:
    files = []
    for f in sorted(base_dir.rglob("*")):
        if f.is_file() and not _should_skip(f):
            files.append(f)
    return files


def run_all(
    base_dir: Path,
    timeout: float = 120.0,
    output_csv: Optional[Path] = None,
    min_size: int = 31,
    max_size: Optional[int] = None,
) -> list[dict]:
    """Parse and solve large benchmark instances with the SAT solver.

    Args:
        base_dir: Root directory containing benchmark instance files.
        timeout: Per-instance timeout in seconds.
        output_csv: Path to write CSV results.
        min_size: Minimum n_customers AND n_patterns to include (default 31).
        max_size: Maximum dimension to include (optional).

    Returns:
        List of result dictionaries.
    """
    files = find_benchmark_files(base_dir)
    print(f"Found {len(files)} benchmark files in {base_dir}")
    print(f"Filtering to instances with n_customers >= {min_size} AND n_patterns >= {min_size}")
    if max_size:
        print(f"  and max(n_customers, n_patterns) <= {max_size}")
    print(f"Timeout: {timeout}s per instance")
    print(f"Solver: SAT (customer intersection graph + CaDiCaL)")
    print()

    all_results: list[dict] = []
    skipped = 0
    instance_num = 0

    for filepath in files:
        dataset = _get_dataset_name(filepath)
        try:
            instances = MOSPInstance.from_benchmark_file(filepath)
        except Exception as e:
            continue  # Skip unparseable files silently for large runs

        for inst in instances:
            # Filter: both dimensions must be >= min_size
            if inst.n_customers < min_size or inst.n_patterns < min_size:
                skipped += 1
                continue

            if max_size and max(inst.n_customers, inst.n_patterns) > max_size:
                skipped += 1
                continue

            instance_num += 1
            print(
                f"[{instance_num}] {dataset}/{filepath.name}: "
                f"{inst.name} ({inst.n_customers}c x {inst.n_patterns}p) ... ",
                end="",
                flush=True,
            )

            result = solve_with_timeout_sat(inst, timeout)

            status = result["status"]
            if status == "solved":
                print(
                    f"MOSP={result['mosp_value']} "
                    f"(pw={result['pathwidth']}, "
                    f"graph={result['n_graph_nodes']}v/{result['n_graph_edges']}e) "
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
                "n_graph_nodes": result.get("n_graph_nodes"),
                "n_graph_edges": result.get("n_graph_edges"),
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
            "n_patterns", "n_graph_nodes", "n_graph_edges",
            "mosp_value", "pathwidth", "time_seconds", "status", "error",
        ]
        with open(output_csv, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)
        print(f"\nResults written to {output_csv}")

    # Print summary
    print()
    print(f"Skipped {skipped} instances below size threshold")
    print()
    print("=" * 90)
    print(
        f"{'Dataset':<25} {'Total':>6} {'Solved':>7} {'Timeout':>8} "
        f"{'Error':>6} {'Avg(s)':>8} {'MaxMOSP':>8}"
    )
    print("-" * 90)

    datasets: dict = {}
    for r in all_results:
        ds = r["dataset"]
        if ds not in datasets:
            datasets[ds] = {
                "total": 0, "solved": 0, "timeout": 0, "error": 0,
                "times": [], "mosp_values": [],
            }
        datasets[ds]["total"] += 1
        if r["status"] == "solved":
            datasets[ds]["solved"] += 1
            datasets[ds]["times"].append(r["time_seconds"])
            datasets[ds]["mosp_values"].append(r["mosp_value"])
        elif r["status"] == "timeout":
            datasets[ds]["timeout"] += 1
        else:
            datasets[ds]["error"] += 1

    total_all = total_solved = total_timeout = total_error = 0
    for ds, stats in sorted(datasets.items()):
        avg_t = sum(stats["times"]) / len(stats["times"]) if stats["times"] else 0
        max_mosp = max(stats["mosp_values"]) if stats["mosp_values"] else 0
        print(
            f"{ds:<25} {stats['total']:>6} {stats['solved']:>7} "
            f"{stats['timeout']:>8} {stats['error']:>6} {avg_t:>8.2f} {max_mosp:>8}"
        )
        total_all += stats["total"]
        total_solved += stats["solved"]
        total_timeout += stats["timeout"]
        total_error += stats["error"]

    print("-" * 90)
    all_times = [r["time_seconds"] for r in all_results if r["status"] == "solved"]
    avg_all = sum(all_times) / len(all_times) if all_times else 0
    all_mosp = [r["mosp_value"] for r in all_results if r["status"] == "solved"]
    max_all = max(all_mosp) if all_mosp else 0
    print(
        f"{'TOTAL':<25} {total_all:>6} {total_solved:>7} "
        f"{total_timeout:>8} {total_error:>6} {avg_all:>8.2f} {max_all:>8}"
    )
    print("=" * 90)

    return all_results


def main():
    parser = argparse.ArgumentParser(
        description="Solve large MOSP benchmark instances with SAT-based pathwidth solver."
    )
    parser.add_argument(
        "--instances", type=str,
        default="benchmarks/instances",
        help="Root directory of benchmark instances (default: benchmarks/instances)",
    )
    parser.add_argument(
        "--timeout", type=float, default=120.0,
        help="Per-instance timeout in seconds (default: 120)",
    )
    parser.add_argument(
        "--output", type=str,
        default="benchmarks/results/sat_large_benchmarks.csv",
        help="Output CSV path",
    )
    parser.add_argument(
        "--min-size", type=int, default=31,
        help="Minimum n_customers AND n_patterns to include (default: 31)",
    )
    parser.add_argument(
        "--max-size", type=int, default=None,
        help="Maximum dimension to include (optional)",
    )
    args = parser.parse_args()

    base_dir = Path(args.instances)
    if not base_dir.exists():
        print(f"Error: {base_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    output_csv = Path(args.output)
    run_all(
        base_dir,
        timeout=args.timeout,
        output_csv=output_csv,
        min_size=args.min_size,
        max_size=args.max_size,
    )


if __name__ == "__main__":
    main()
