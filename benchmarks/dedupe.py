"""Share solutions between instances that are the same problem twice.

The benchmark collections overlap. `SP3` appears in the 2005 Challenge set as a
named instance inside `Wilson/sp4.txt`, and again in the SCOOP collection as
`MOSP_Instances/Challenge/SP3.txt`, where the file carries no name line and the
parser calls it `SP3_0`. The matrices are byte-identical, so a production
sequence achieving `k` on one achieves `k` on the other — but the solver treats
them as unrelated and may solve the same problem twice, to different quality.
That is how `SP3` came to sit at 35 while `SP3_0` sat at 38.

This finds instances with identical matrices and propagates the best solution
across each group. The ordering is transferred only after checking it really
achieves the claimed value on the receiving instance, so a mismatch in the
duplicate detection cannot introduce a wrong result.

Usage:
    python -m benchmarks.dedupe --dry-run
    python -m benchmarks.dedupe
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Optional

from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from satisfiability.mosp_solver import SOLUTIONS_DIR, _save_solution

DEFAULT_INSTANCE_DIR = Path("benchmarks/instances")


def group_identical(instance_dir: Path) -> list[list[MOSPInstance]]:
    """Group instances whose matrices are identical.

    Keyed on the exact bytes of the matrix together with its shape, so only
    genuinely identical problems are grouped; instances that merely happen to
    share dimensions are not.
    """
    from benchmarks.solve_parallel import find_benchmark_files

    groups: dict[tuple, list[MOSPInstance]] = defaultdict(list)
    for filepath in find_benchmark_files(instance_dir):
        try:
            instances = MOSPInstance.from_benchmark_file(filepath)
        except Exception:  # noqa: BLE001
            continue
        for instance in instances:
            key = (instance.matrix.shape, instance.matrix.tobytes())
            groups[key].append(instance)

    return [group for group in groups.values() if len(group) > 1]


def dedupe(
    instance_dir: Path = DEFAULT_INSTANCE_DIR,
    solutions_dir: Path = SOLUTIONS_DIR,
    dry_run: bool = False,
) -> list[tuple[str, str, int, int]]:
    """Propagate the best solution within each group of identical instances.

    Returns the transfers made, as (source, target, from_value, to_value).
    """
    cached: dict[str, dict] = {}
    for path in sorted(solutions_dir.glob("*.json")):
        try:
            payload = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        cached[payload["instance_name"]] = payload

    transfers: list[tuple[str, str, int, int]] = []

    for group in group_identical(instance_dir):
        solved = [(inst, cached[inst.name]) for inst in group
                  if inst.name in cached]
        if not solved:
            continue

        best_instance, best = min(solved, key=lambda pair: pair[1]["mosp_value"])
        best_value = best["mosp_value"]

        for instance in group:
            current = cached.get(instance.name)
            if current is not None and current["mosp_value"] <= best_value:
                continue

            # Never transfer on the strength of the grouping alone: re-simulate
            # the ordering against the receiving instance and require it to
            # achieve the value claimed.
            achieved = max_open_stacks(instance, best["ordering"])
            if achieved != best_value:
                print(f"  refusing {best_instance.name} -> {instance.name}: "
                      f"ordering achieves {achieved}, not {best_value}")
                continue

            was = current["mosp_value"] if current else None
            transfers.append((best_instance.name, instance.name,
                              was if was is not None else -1, best_value))
            if not dry_run:
                _save_solution(instance, best_value, best["ordering"],
                               solutions_dir)

    return transfers


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--dir", type=Path, default=DEFAULT_INSTANCE_DIR)
    parser.add_argument("--solutions-dir", type=Path, default=SOLUTIONS_DIR)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    groups = group_identical(args.dir)
    print(f"{len(groups)} groups of identical instances, "
          f"covering {sum(len(g) for g in groups)} instances")

    transfers = dedupe(args.dir, args.solutions_dir, dry_run=args.dry_run)
    for source, target, was, now in transfers:
        previous = "none" if was < 0 else str(was)
        print(f"  {source} -> {target}: {previous} -> {now}")

    verb = "would transfer" if args.dry_run else "transferred"
    print(f"{verb} {len(transfers)} solutions")


if __name__ == "__main__":
    main()
