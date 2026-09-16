"""Overnight driver: attack whatever is still unsolved, at escalating budgets.

Designed to be run repeatedly, night after night, with no bookkeeping between
runs. The solution cache is the state: an instance with a cached solution is
verified from disk in milliseconds and skipped, so each run spends its whole
budget on what remains open. Killing the run at any point loses only the
instance in flight.

Budgets escalate within a single run. An instance that resists 15 minutes is not
usually going to fall at 16, but it might at 90, and the cheap rounds first mean
the easy remainder is cleared before anything expensive starts. Instances still
unsolved at the end of the last round are reported so the next night can start
from a longer budget.

Usage:
    python -m benchmarks.overnight                      # default escalation
    python -m benchmarks.overnight --rounds 900,3600    # custom, seconds
    python -m benchmarks.overnight --hours 8            # stop after 8 hours
"""

from __future__ import annotations

import argparse
import csv
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from benchmarks.solve_parallel import find_benchmark_files, sweep
from mosp.instance import MOSPInstance
from satisfiability.mosp_solver import SOLUTIONS_DIR, _solution_path

DEFAULT_INSTANCE_DIR = Path("benchmarks/instances")
DEFAULT_ROUNDS = (900, 3600, 10800)  # 15 min, 1 h, 3 h
RESULTS_DIR = Path("benchmarks/results")


def unsolved_instances(instance_dir: Path, solutions_dir: Path) -> list[str]:
    """Names of instances with no cached solution.

    Presence of the cache file is the criterion; solve_mosp_sat verifies the
    contents when it loads one, and discards it if invalid, so a corrupt file
    costs one re-solve rather than a wrong answer.
    """
    pending = []
    for filepath in find_benchmark_files(instance_dir):
        try:
            instances = MOSPInstance.from_benchmark_file(filepath)
        except Exception:  # noqa: BLE001
            continue
        for inst in instances:
            if not _solution_path(inst, solutions_dir).exists():
                pending.append(inst.name)
    return pending


def run_night(
    instance_dir: Path = DEFAULT_INSTANCE_DIR,
    solutions_dir: Path = SOLUTIONS_DIR,
    rounds: tuple[int, ...] = DEFAULT_ROUNDS,
    workers: int = 0,
    hours: Optional[float] = None,
    results_dir: Path = RESULTS_DIR,
) -> None:
    """Run escalating-budget rounds until everything is solved or time is up."""
    workers = workers or min(30, os.cpu_count() or 1)
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    deadline = time.time() + hours * 3600 if hours else None

    start_pending = unsolved_instances(instance_dir, solutions_dir)
    print(f"=== overnight run {stamp} ===")
    print(f"unsolved at start: {len(start_pending)}")
    print(f"rounds: {', '.join(str(r) + 's' for r in rounds)}   workers: {workers}")
    if deadline:
        print(f"hard stop after {hours}h")
    print()

    if not start_pending:
        print("nothing left to solve.")
        return

    for round_num, budget in enumerate(rounds, 1):
        pending = unsolved_instances(instance_dir, solutions_dir)
        if not pending:
            print("\nall instances solved.")
            break

        if deadline and time.time() >= deadline:
            print(f"\nhard stop reached before round {round_num}.")
            break

        remaining = deadline - time.time() if deadline else None
        if remaining is not None and remaining < budget:
            # A round whose per-instance budget exceeds the time left cannot
            # finish even one instance honestly; stop rather than report a
            # timeout that only means the clock ran out.
            print(f"\nskipping round {round_num} ({budget}s): only "
                  f"{remaining / 60:.0f} min left.")
            break

        print(f"--- round {round_num}: {budget}s per instance, "
              f"{len(pending)} unsolved ---", flush=True)

        output = results_dir / f"overnight_{stamp}_round{round_num}.csv"
        # sweep re-reads the cache, so solved instances cost a verify and the
        # budget lands on the genuinely open ones.
        sweep(base_dir=instance_dir, workers=workers, timeout=float(budget),
              output_csv=output, solutions_dir=solutions_dir)

        still = unsolved_instances(instance_dir, solutions_dir)
        print(f"--- round {round_num} done: {len(pending) - len(still)} newly "
              f"solved, {len(still)} remaining ---\n", flush=True)

    final = unsolved_instances(instance_dir, solutions_dir)
    print()
    print("=" * 60)
    print(f"solved this run: {len(start_pending) - len(final)}")
    print(f"still unsolved:  {len(final)}")

    if final:
        listing = results_dir / f"overnight_{stamp}_unsolved.txt"
        listing.parent.mkdir(parents=True, exist_ok=True)
        listing.write_text("\n".join(sorted(final)) + "\n")
        print(f"remaining instances: {listing}")
        print("start the next run at the budget this one ended on.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--dir", type=Path, default=DEFAULT_INSTANCE_DIR)
    parser.add_argument("--solutions-dir", type=Path, default=SOLUTIONS_DIR)
    parser.add_argument("--rounds", type=str, default=None,
                        help="comma-separated per-instance budgets in seconds "
                             f"(default: {','.join(map(str, DEFAULT_ROUNDS))})")
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--hours", type=float, default=None,
                        help="stop starting new rounds after this many hours")
    args = parser.parse_args()

    rounds = DEFAULT_ROUNDS
    if args.rounds:
        rounds = tuple(int(r) for r in args.rounds.split(","))

    run_night(instance_dir=args.dir, solutions_dir=args.solutions_dir,
              rounds=rounds, workers=args.workers, hours=args.hours)


if __name__ == "__main__":
    main()
