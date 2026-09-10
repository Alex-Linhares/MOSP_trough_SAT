"""Benchmark runner for MOSP solver.

Runs the solver on a set of instances, records results, and optionally
compares against known optimal values from the literature.
"""

from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

from mosp.instance import MOSPInstance
from mosp.solver import solve_mosp
from mosp.verify import verify_solution

# Known optimal values from Chu & Stuckey (2009) and other sources.
# Format: instance_name -> optimal MOSP value
KNOWN_OPTIMA: dict[str, int] = {
    # These would be populated from published results.
    # Example entries (from Wil_Prob series):
    # "Wil_Prob_10_10_1": 4,
}


def run_single(instance: MOSPInstance, verbose: bool = False) -> dict:
    """Run the solver on a single instance and return results.

    Returns:
        Dictionary with keys: name, n_customers, n_patterns, optimal_value,
        verified, time_seconds, ordering.
    """
    start = time.time()
    try:
        solution = solve_mosp(instance)
        elapsed = time.time() - start

        is_correct, actual = verify_solution(
            instance, solution.ordering, solution.max_open_stacks
        )

        result = {
            "name": instance.name,
            "n_customers": instance.n_customers,
            "n_patterns": instance.n_patterns,
            "optimal_value": solution.max_open_stacks,
            "pathwidth": solution.pathwidth,
            "verified": is_correct,
            "actual_open_stacks": actual,
            "time_seconds": elapsed,
            "ordering": solution.ordering,
            "error": None,
        }

        if verbose:
            status = "OK" if is_correct else "MISMATCH"
            print(
                f"  {instance.name}: optimal={solution.max_open_stacks} "
                f"(pw={solution.pathwidth}) [{status}] {elapsed:.3f}s"
            )

    except Exception as e:
        elapsed = time.time() - start
        result = {
            "name": instance.name,
            "n_customers": instance.n_customers,
            "n_patterns": instance.n_patterns,
            "optimal_value": None,
            "pathwidth": None,
            "verified": False,
            "actual_open_stacks": None,
            "time_seconds": elapsed,
            "ordering": None,
            "error": str(e),
        }
        if verbose:
            print(f"  {instance.name}: ERROR - {e}")

    return result


def run_benchmark_suite(
    instance_dir: str | Path,
    output_csv: str | Path | None = None,
    verbose: bool = True,
) -> list[dict]:
    """Run the solver on all .mosp files in a directory.

    Args:
        instance_dir: Directory containing .mosp instance files.
        output_csv: Optional path to write results CSV.
        verbose: Print progress.

    Returns:
        List of result dictionaries.
    """
    instance_dir = Path(instance_dir)
    files = sorted(instance_dir.glob("*.mosp"))

    if not files:
        print(f"No .mosp files found in {instance_dir}")
        return []

    if verbose:
        print(f"Running {len(files)} instances from {instance_dir}")
        print()

    results = []
    for f in files:
        instance = MOSPInstance.from_file(f)
        result = run_single(instance, verbose=verbose)

        # Compare with known optimum if available
        if instance.name in KNOWN_OPTIMA:
            known = KNOWN_OPTIMA[instance.name]
            result["known_optimal"] = known
            result["matches_known"] = result["optimal_value"] == known
        else:
            result["known_optimal"] = None
            result["matches_known"] = None

        results.append(result)

    # Summary
    if verbose:
        print()
        solved = [r for r in results if r["error"] is None]
        failed = [r for r in results if r["error"] is not None]
        verified = [r for r in solved if r["verified"]]
        print(f"Solved: {len(solved)}/{len(results)}")
        print(f"Verified: {len(verified)}/{len(solved)}")
        if failed:
            print(f"Failed: {len(failed)} (likely too large for exact DP)")
        if solved:
            avg_time = sum(r["time_seconds"] for r in solved) / len(solved)
            max_time = max(r["time_seconds"] for r in solved)
            print(f"Avg time: {avg_time:.3f}s, Max time: {max_time:.3f}s")

    # Write CSV
    if output_csv and results:
        output_csv = Path(output_csv)
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = [
            "name", "n_customers", "n_patterns", "optimal_value",
            "pathwidth", "verified", "time_seconds", "known_optimal",
            "matches_known", "error",
        ]
        with open(output_csv, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(results)
        if verbose:
            print(f"\nResults written to {output_csv}")

    return results


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python run_benchmarks.py <instance_dir> [output.csv]")
        print()
        print("Runs MOSP solver on all .mosp files in the given directory.")
        sys.exit(1)

    instance_dir = sys.argv[1]
    output_csv = sys.argv[2] if len(sys.argv) > 2 else None

    run_benchmark_suite(instance_dir, output_csv)


if __name__ == "__main__":
    main()
