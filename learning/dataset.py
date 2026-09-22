"""Build the supervised table: one row per instance, features plus its optimum.

Joins two things the repository already keeps separately -- the benchmark files
under `benchmarks/instances/` and the certified solutions under `solutions/` --
through the same name mapping the solver caches by, so the label of every row is
a proved optimum rather than a solver's best effort.

Two columns exist purely so that a later split cannot lie:

- `source_file` -- instances that share a file came out of one generator
  configuration and are near-duplicates of each other. Splitting rows at random
  puts siblings on both sides and the reported error collapses; every study here
  groups by this column instead. `learning.study_optimum` reports both numbers
  so the size of that illusion stays visible.
- `provenance` -- rows whose optimality is not certified would be label noise.
  All 6,376 are certified today, so nothing is dropped, but a corpus that grows
  by ratcheting upper bounds would need the filter.

Usage:
    python -m learning.dataset                  # writes learning/data/instances.csv
    python -m learning.dataset --no-bounds      # matrix + graph features only, fast
"""

from __future__ import annotations

import argparse
import json
import multiprocessing
import time
from pathlib import Path

import numpy as np
import pandas as pd

from benchmarks.solve_parallel import find_benchmark_files
from learning.features import instance_features
from mosp.instance import MOSPInstance
from satisfiability.mosp_solver import _solution_path

DEFAULT_INSTANCE_DIR = Path("benchmarks/instances")
DEFAULT_SOLUTIONS_DIR = Path("solutions")
DATA_DIR = Path("learning/data")
DEFAULT_OUT = DATA_DIR / "instances.csv"


def enumerate_instances(
    instance_dir: Path = DEFAULT_INSTANCE_DIR,
) -> list[tuple[Path, MOSPInstance]]:
    """Every instance in the benchmark tree, paired with the file it came from."""
    found: list[tuple[Path, MOSPInstance]] = []
    for filepath in find_benchmark_files(instance_dir):
        try:
            instances = MOSPInstance.from_benchmark_file(filepath)
        except Exception:  # noqa: BLE001 - a malformed file is not this module's problem
            continue
        found.extend((filepath, inst) for inst in instances)
    return found


def _row(args: tuple[Path, MOSPInstance, Path, tuple[str, ...], float]) -> dict | None:
    filepath, instance, solutions_dir, groups, clique_budget = args
    path = _solution_path(instance, solutions_dir)
    if not path.exists():
        return None
    try:
        solution = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None

    row: dict[str, object] = {
        "instance_name": instance.name,
        "source_file": str(filepath),
        "collection": filepath.parts[2] if len(filepath.parts) > 2 else "",
        "provenance": solution.get("provenance", ""),
        "optimum": int(solution["mosp_value"]),
    }
    row.update(instance_features(instance, groups=groups, clique_budget=clique_budget))
    return row


def _worker(args):
    return _row(args)


def build(
    instance_dir: Path = DEFAULT_INSTANCE_DIR,
    solutions_dir: Path = DEFAULT_SOLUTIONS_DIR,
    groups: tuple[str, ...] = ("matrix", "graph", "bounds"),
    clique_budget: float = 1.0,
    workers: int | None = None,
    verbose: bool = True,
) -> pd.DataFrame:
    """Feature table for every instance that has a cached solution."""
    pairs = enumerate_instances(instance_dir)
    if verbose:
        print(f"{len(pairs)} instances enumerated", flush=True)

    jobs = [(f, i, solutions_dir, groups, clique_budget) for f, i in pairs]
    workers = workers or max(1, (multiprocessing.cpu_count() or 2) - 1)

    started = time.time()
    rows: list[dict] = []
    if workers == 1:
        results = map(_worker, jobs)
    else:
        pool = multiprocessing.Pool(workers)
        results = pool.imap_unordered(_worker, jobs, chunksize=16)
    for done, row in enumerate(results, start=1):
        if row is not None:
            rows.append(row)
        if verbose and done % 500 == 0:
            rate = done / (time.time() - started)
            print(f"  {done}/{len(jobs)} at {rate:.0f}/s", flush=True)
    if workers != 1:
        pool.close()
        pool.join()

    frame = pd.DataFrame(rows).sort_values("instance_name").reset_index(drop=True)
    if verbose:
        missing = len(pairs) - len(frame)
        print(f"{len(frame)} rows in {time.time() - started:.0f}s "
              f"({missing} instances had no cached solution)", flush=True)
    return frame


def load(path: Path = DEFAULT_OUT) -> pd.DataFrame:
    """Read a table built earlier, failing loudly if it was never built."""
    if not path.exists():
        raise FileNotFoundError(
            f"{path} does not exist; run `python -m learning.dataset` first"
        )
    return pd.read_csv(path)


def feature_columns(frame: pd.DataFrame) -> list[str]:
    """The numeric feature columns -- everything but the identifiers and label."""
    skip = {"instance_name", "source_file", "collection", "provenance", "optimum"}
    return [c for c in frame.columns
            if c not in skip and np.issubdtype(frame[c].dtype, np.number)]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--instance-dir", type=Path, default=DEFAULT_INSTANCE_DIR)
    parser.add_argument("--solutions-dir", type=Path, default=DEFAULT_SOLUTIONS_DIR)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--workers", type=int, default=None)
    parser.add_argument("--clique-budget", type=float, default=1.0)
    parser.add_argument("--no-bounds", action="store_true",
                        help="skip the bound features, which cost most of the time")
    args = parser.parse_args()

    groups = ("matrix", "graph") if args.no_bounds else ("matrix", "graph", "bounds")
    frame = build(args.instance_dir, args.solutions_dir, groups=groups,
                  clique_budget=args.clique_budget, workers=args.workers)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.out, index=False)
    print(f"wrote {args.out} ({len(frame)} rows x {len(frame.columns)} columns)")


if __name__ == "__main__":
    main()
