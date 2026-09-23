"""Re-prove the optimality of entries whose certification was withdrawn.

`reports/better_move_bug.md` describes why some exist: a dominance rule could
return a false refutation, so every optimality claim resting on it had to be
withdrawn until re-proved with the fixed code. An entry is re-certified by
refuting `value - 1`; a *satisfiable* answer instead means the stored value is
wrong and the true optimum is lower, which happened once.

This is meant for unattended runs measured in days. It therefore:

- promotes each entry **as it lands**, so the corpus is correct at every moment
  and an interruption keeps everything already proved;
- writes its log and results under `recertify/`, which is outside git, so they
  survive the session that started them;
- refuses to touch an entry whose stored value it cannot confirm, and shouts
  rather than guessing if a value turns out to be wrong.

The configuration is the one calibrated in `reports/inner_loop.md` §4:
`better_move` with every candidate eligible as a dominator, and the memo on.
On sparse instances that is 3-7x fewer nodes than any alternative.

Usage:
    python -m benchmarks.recertify --days 5
    python -m benchmarks.recertify --days 5 --workers 8 --dry-run
"""

from __future__ import annotations

import argparse
import json
import multiprocessing
import time
from pathlib import Path

from mosp.instance import MOSPInstance

OUT_DIR = Path("recertify")


def _open_entries(instance_dir: Path, solutions: Path):
    """Instances whose stored provenance is not a certification."""
    from learning.dataset import enumerate_instances
    from satisfiability.mosp_solver import CERTIFIED, _solution_path

    found = []
    for _, instance in enumerate_instances(instance_dir):
        path = _solution_path(instance, solutions)
        if not path.exists():
            continue
        data = json.loads(path.read_text())
        if data.get("provenance") in CERTIFIED:
            continue
        found.append((instance, data["mosp_value"], path))
    return found


def _worker(args):
    matrix, n_customers, n_patterns, name, value, seconds = args
    import numpy as np

    from satisfiability.customer_search import decide

    instance = MOSPInstance(matrix=np.array(matrix, dtype=np.int8),
                            n_customers=n_customers, n_patterns=n_patterns,
                            name=name)
    started = time.monotonic()
    answer = decide(instance, value - 1, better_move=True,
                    better_move_dominators=0, memo=True,
                    deadline=time.monotonic() + seconds)
    return {"name": name, "value": value, "status": answer.status,
            "nodes": answer.nodes, "seconds": round(time.monotonic() - started, 1)}


def _promote(path: Path, result: dict) -> str:
    """Restore the certification, or report that the value is wrong."""
    data = json.loads(path.read_text())
    if result["status"] == "sat":
        return (f"!!! {result['name']}: k={result['value'] - 1} is SATISFIABLE, "
                f"so the stored value {result['value']} is WRONG and the optimum "
                f"is lower. Left untouched; settle it before trusting the entry.")
    if result["status"] != "unsat":
        return f"    {result['name']}: budget expired, still open"

    data["provenance"] = "certified:refutation"
    data.pop("provenance_note", None)
    data["recertified"] = (f"{time.strftime('%Y-%m-%d')}, after the better_move "
                           f"cycle fix; {result['nodes']:,} nodes")
    path.write_text(json.dumps(data, indent=2) + "\n")
    return (f"    {result['name']}: RE-CERTIFIED at {result['value']} "
            f"({result['nodes']:,} nodes, {result['seconds'] / 3600:.2f}h)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--days", type=float, default=5.0,
                        help="budget per instance")
    parser.add_argument("--workers", type=int, default=0,
                        help="default: one per open entry")
    parser.add_argument("--dir", type=Path, default=Path("benchmarks/instances"))
    parser.add_argument("--solutions-dir", type=Path, default=Path("solutions"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    entries = _open_entries(args.dir, args.solutions_dir)
    seconds = args.days * 86400
    print(f"{len(entries)} entries with optimality open, "
          f"{args.days:g}-day budget each", flush=True)
    for instance, value, _ in entries:
        print(f"    {instance.name:24s} value={value:4d} "
              f"({instance.n_customers}x{instance.n_patterns})", flush=True)
    if args.dry_run or not entries:
        return

    OUT_DIR.mkdir(exist_ok=True)
    results_path = OUT_DIR / "results.json"
    paths = {instance.name: path for instance, _, path in entries}

    jobs = [(instance.matrix.tolist(), instance.n_customers, instance.n_patterns,
             instance.name, value, seconds) for instance, value, _ in entries]
    workers = args.workers or len(jobs)

    print(f"\nstarted {time.strftime('%Y-%m-%d %H:%M:%S')} on {workers} workers\n",
          flush=True)
    rows = []
    with multiprocessing.Pool(workers) as pool:
        for result in pool.imap_unordered(_worker, jobs):
            rows.append(result)
            print(f"[{time.strftime('%H:%M:%S')}] "
                  f"{_promote(paths[result['name']], result)}", flush=True)
            results_path.write_text(json.dumps(rows, indent=1))

    certified = sum(1 for r in rows if r["status"] == "unsat")
    wrong = [r["name"] for r in rows if r["status"] == "sat"]
    print(f"\nre-certified {certified}/{len(rows)}; still open "
          f"{sum(1 for r in rows if r['status'] == 'unknown')}")
    if wrong:
        print(f"WRONG VALUES: {wrong}")


if __name__ == "__main__":
    main()
