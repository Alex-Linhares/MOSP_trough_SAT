"""Side-by-side comparison of agreement graph vs customer graph MOSP solvers.

Solves instances using both approaches and prints a comparison table showing
pathwidth and MOSP values from each, plus published optimal values where known.

Usage:
    python -m customer_inter.compare [--instances DIR] [--timeout SECONDS]
"""

from __future__ import annotations

import argparse
import multiprocessing
import sys
import time
from pathlib import Path

import numpy as np

from mosp.instance import MOSPInstance


# Published optimal values for SCOOP instances from the literature.
# Sources: Chu & Stuckey (2009), SCOOP project documentation.
KNOWN_OPTIMA: dict[str, int] = {
    # SCOOP instances (from published tables)
    "scoop-A_AP-9.d_10_0": 6,
    "scoop-B_39Q18_82_0": 5,
    "scoop-B_22X18_50_0": 6,
    "scoop-B_42F22_93_0": 5,
    "scoop-B_CARLET_137_0": 5,
}


def _solve_agreement(instance: MOSPInstance) -> dict:
    """Solve using the agreement graph (original approach)."""
    from mosp.solver import solve_mosp
    solution = solve_mosp(instance)
    return {
        "pathwidth": solution.pathwidth,
        "mosp": solution.max_open_stacks,
    }


def _solve_customer(instance: MOSPInstance) -> dict:
    """Solve using the customer intersection graph."""
    from customer_inter.solver import solve_mosp
    solution = solve_mosp(instance)
    return {
        "pathwidth": solution.pathwidth,
        "mosp": solution.max_open_stacks,
    }


def _worker(
    approach: str,
    matrix_list: list[list[int]],
    n_customers: int,
    n_patterns: int,
    name: str,
    result_queue: multiprocessing.Queue,
) -> None:
    """Worker for solving in a subprocess with timeout support."""
    try:
        instance = MOSPInstance(
            matrix=np.array(matrix_list, dtype=np.int8),
            n_customers=n_customers,
            n_patterns=n_patterns,
            name=name,
        )
        if approach == "agreement":
            result = _solve_agreement(instance)
        else:
            result = _solve_customer(instance)
        result_queue.put(result)
    except Exception as e:
        result_queue.put({"error": str(e)})


def _solve_with_timeout(
    approach: str, instance: MOSPInstance, timeout: float
) -> dict:
    """Solve with a per-instance timeout."""
    queue: multiprocessing.Queue = multiprocessing.Queue()
    proc = multiprocessing.Process(
        target=_worker,
        args=(
            approach,
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
        return {"pathwidth": None, "mosp": None, "time": elapsed, "status": "timeout"}

    if not queue.empty():
        result = queue.get_nowait()
        if "error" in result:
            return {"pathwidth": None, "mosp": None, "time": elapsed, "status": f"error: {result['error']}"}
        result["time"] = elapsed
        result["status"] = "solved"
        return result

    return {"pathwidth": None, "mosp": None, "time": elapsed, "status": "error"}


def compare_instance(
    instance: MOSPInstance, timeout: float = 120.0
) -> dict:
    """Compare both solvers on a single instance.

    Returns a dict with all comparison fields.
    """
    agree_result = _solve_with_timeout("agreement", instance, timeout)
    cust_result = _solve_with_timeout("customer", instance, timeout)

    known = KNOWN_OPTIMA.get(instance.name)

    return {
        "name": instance.name,
        "n_customers": instance.n_customers,
        "n_patterns": instance.n_patterns,
        "agree_pw": agree_result.get("pathwidth"),
        "agree_mosp": agree_result.get("mosp"),
        "agree_time": agree_result.get("time", 0),
        "agree_status": agree_result.get("status"),
        "cust_pw": cust_result.get("pathwidth"),
        "cust_mosp": cust_result.get("mosp"),
        "cust_time": cust_result.get("time", 0),
        "cust_status": cust_result.get("status"),
        "known_optimal": known,
    }


def print_comparison_table(results: list[dict]) -> None:
    """Print a formatted comparison table."""
    header = (
        f"{'Instance':<30} {'n_c':>4} {'n_p':>4} "
        f"{'ag_PW':>5} {'ag_MOSP':>7} "
        f"{'cu_PW':>5} {'cu_MOSP':>7} "
        f"{'lit':>4} {'match':>5}"
    )
    print(header)
    print("-" * len(header))

    for r in results:
        ag_pw = str(r["agree_pw"]) if r["agree_pw"] is not None else "---"
        ag_mosp = str(r["agree_mosp"]) if r["agree_mosp"] is not None else "---"
        cu_pw = str(r["cust_pw"]) if r["cust_pw"] is not None else "---"
        cu_mosp = str(r["cust_mosp"]) if r["cust_mosp"] is not None else "---"
        known = str(r["known_optimal"]) if r["known_optimal"] is not None else "?"

        if r["known_optimal"] is not None and r["cust_mosp"] is not None:
            match = "Y" if r["cust_mosp"] == r["known_optimal"] else "N"
        else:
            match = "-"

        print(
            f"{r['name']:<30} {r['n_customers']:>4} {r['n_patterns']:>4} "
            f"{ag_pw:>5} {ag_mosp:>7} "
            f"{cu_pw:>5} {cu_mosp:>7} "
            f"{known:>4} {match:>5}"
        )


def run_comparison(
    instance_dir: Path,
    timeout: float = 120.0,
    max_patterns: int | None = 25,
) -> list[dict]:
    """Run comparison on all parseable instances in the directory tree.

    Args:
        instance_dir: Root directory of benchmark instances.
        timeout: Per-solver timeout in seconds.
        max_patterns: Skip instances with more patterns than this (for speed).

    Returns:
        List of comparison result dicts.
    """
    # Collect instance files
    files = []
    for f in sorted(instance_dir.rglob("*")):
        if f.is_file() and f.suffix in (".txt", ".dat"):
            if any(skip in f.name for skip in ("Dataset_Description", "README", "S1. Dataset")):
                continue
            files.append(f)

    print(f"Found {len(files)} benchmark files in {instance_dir}")
    if max_patterns:
        print(f"Filtering to instances with n_patterns <= {max_patterns}")
    print()

    results = []
    count = 0
    for filepath in files:
        try:
            instances = MOSPInstance.from_benchmark_file(filepath)
        except Exception:
            continue

        for inst in instances:
            if max_patterns is not None and inst.n_patterns > max_patterns:
                continue
            if inst.n_customers > max_patterns:
                continue

            count += 1
            print(
                f"[{count}] {inst.name} ({inst.n_customers}x{inst.n_patterns}) ... ",
                end="", flush=True,
            )

            result = compare_instance(inst, timeout)
            results.append(result)

            ag = result["agree_mosp"]
            cu = result["cust_mosp"]
            print(
                f"agree={ag} cust={cu}"
                + (f" lit={result['known_optimal']}" if result["known_optimal"] else "")
            )

    print()
    print_comparison_table(results)
    return results


def run_scoop_comparison(timeout: float = 120.0) -> list[dict]:
    """Run comparison specifically on SCOOP instances.

    This focuses on the dataset where discrepancies between agreement graph
    and customer graph approaches were observed.
    """
    scoop_dir = Path("benchmarks/instances/MOSP_Instances/SCOOP")
    if not scoop_dir.exists():
        print(f"SCOOP directory not found: {scoop_dir}")
        return []

    print("=" * 78)
    print("MOSP Solver Comparison: Agreement Graph vs Customer Intersection Graph")
    print("=" * 78)
    print()

    files = sorted(scoop_dir.glob("scoop-*.txt"))
    print(f"Found {len(files)} SCOOP instances")
    print()

    results = []
    for filepath in files:
        try:
            instances = MOSPInstance.from_benchmark_file(filepath)
        except Exception as e:
            print(f"  Parse error: {filepath.name}: {e}")
            continue

        for inst in instances:
            # SCOOP instances can be large — skip very large ones
            if inst.n_patterns > 25 or inst.n_customers > 25:
                print(f"  Skipping {inst.name} ({inst.n_customers}x{inst.n_patterns}) — too large")
                continue

            print(
                f"  {inst.name} ({inst.n_customers}x{inst.n_patterns}) ... ",
                end="", flush=True,
            )

            result = compare_instance(inst, timeout)
            results.append(result)

            ag = result["agree_mosp"]
            cu = result["cust_mosp"]
            known = result["known_optimal"]
            status = ""
            if known is not None:
                if cu == known:
                    status = " [cust matches lit]"
                elif ag == known:
                    status = " [agree matches lit]"
                else:
                    status = " [neither matches lit]"
            print(f"agree_MOSP={ag} cust_MOSP={cu} lit={known or '?'}{status}")

    print()
    print_comparison_table(results)

    # Summary
    with_known = [r for r in results if r["known_optimal"] is not None]
    if with_known:
        print()
        agree_match = sum(
            1 for r in with_known if r["agree_mosp"] == r["known_optimal"]
        )
        cust_match = sum(
            1 for r in with_known if r["cust_mosp"] == r["known_optimal"]
        )
        print(f"Agreement graph matches literature: {agree_match}/{len(with_known)}")
        print(f"Customer graph matches literature:   {cust_match}/{len(with_known)}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Compare agreement graph vs customer graph MOSP solvers."
    )
    parser.add_argument(
        "--instances", type=str, default=None,
        help="Root directory of instances. If not set, runs SCOOP comparison.",
    )
    parser.add_argument(
        "--timeout", type=float, default=120.0,
        help="Per-solver timeout in seconds (default: 120).",
    )
    parser.add_argument(
        "--max-size", type=int, default=25,
        help="Max patterns/customers to attempt (default: 25).",
    )
    args = parser.parse_args()

    if args.instances:
        run_comparison(Path(args.instances), args.timeout, args.max_size)
    else:
        run_scoop_comparison(args.timeout)


if __name__ == "__main__":
    main()
