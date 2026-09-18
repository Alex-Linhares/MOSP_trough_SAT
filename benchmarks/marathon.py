"""Escalating-budget customer search against whatever is still unproven.

`benchmarks/csearch.py` runs one budget over one set of instances. A long
unattended run wants something else: most of what survives a short budget falls
to a medium one, and spending the whole night on the first instance in the list
is how a budget gets wasted. So rounds escalate, and each round re-reads what is
still open -- anything closed in an earlier round drops out by itself, because
the solution cache is the state.

The deadline is honoured rather than hoped for. Before each round the driver
works out how long that round can take -- `ceil(instances / workers)` waves of
the per-instance budget -- and shrinks the budget to fit the time left instead of
overrunning. A round with no time for even one wave is skipped.

Usage:
    python -m benchmarks.marathon --days 5 --workers 25
"""

from __future__ import annotations

import argparse
import math
import time
from pathlib import Path

from satisfiability.mosp_solver import SOLUTIONS_DIR

DEFAULT_INSTANCE_DIR = Path("benchmarks/instances")

# Per-instance budgets, in seconds. Each round is a fresh descent from whatever
# upper bound the last one left behind, so the work is not repeated: a descent
# that timed out still ratcheted its bound down, and the next round starts there.
DEFAULT_ROUNDS = (6 * 3600, 18 * 3600, 48 * 3600, 96 * 3600)

# Below this a round is not worth starting: the search spends the first seconds
# on bounds and heuristics before its first decision call.
MIN_BUDGET = 60.0


def marathon(
    rounds: tuple[int, ...] = DEFAULT_ROUNDS,
    workers: int = 25,
    deadline: float | None = None,
    instance_dir: Path = DEFAULT_INSTANCE_DIR,
    solutions_dir: Path = SOLUTIONS_DIR,
    verbose: bool = True,
) -> list[tuple]:
    """Run escalating rounds until the rounds run out or the deadline does."""
    from benchmarks.csearch import sweep
    from benchmarks.ratchet import find_unproven

    everything = []
    for index, budget in enumerate(rounds, 1):
        targets = find_unproven(instance_dir, solutions_dir)
        if not targets:
            if verbose:
                print("\nnothing left open -- stopping early", flush=True)
            break

        waves = math.ceil(len(targets) / workers)
        if deadline is not None:
            left = deadline - time.time()
            if left <= 0:
                print(f"\nout of time before round {index}", flush=True)
                break
            # Shrink rather than overrun: a round that cannot fit at its stated
            # budget still does useful work at a smaller one. But a floor on the
            # budget would override the deadline -- granting a minimum to a round
            # with no time for it is how a five-day run becomes a five-day-plus-
            # change run -- so below the floor the round is skipped instead.
            fits = left / waves * 0.98
            if fits < MIN_BUDGET:
                if verbose:
                    print(f"\nround {index} skipped: {left / 60:.0f} min left, "
                          f"{waves} wave(s) needs at least "
                          f"{waves * MIN_BUDGET / 60:.0f}", flush=True)
                break
            budget = min(budget, fits)

        if verbose:
            print(f"\n=== round {index}: {len(targets)} open, "
                  f"{budget / 3600:.1f}h each, {waves} wave(s), "
                  f"~{waves * budget / 3600:.1f}h", flush=True)

        results = sweep(targets, budget, workers=workers,
                        solutions_dir=solutions_dir, verbose=verbose)
        everything.extend(results)

        proved = [r for r in results if r[4] in ("refutation", "bound")]
        improved = [r for r in results if r[1] is not None and r[2] is not None
                    and r[2] < r[1]]
        if verbose:
            print(f"--- round {index}: {len(proved)} proved, "
                  f"{len(improved)} improved", flush=True)

    return everything


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--days", type=float, default=5.0)
    parser.add_argument("--workers", type=int, default=25)
    parser.add_argument("--rounds", type=str, default=None,
                        help="comma-separated per-instance budgets in seconds")
    parser.add_argument("--dir", type=Path, default=DEFAULT_INSTANCE_DIR)
    parser.add_argument("--solutions-dir", type=Path, default=SOLUTIONS_DIR)
    args = parser.parse_args()

    rounds = (tuple(float(r) for r in args.rounds.split(","))
              if args.rounds else DEFAULT_ROUNDS)
    started = time.time()
    deadline = started + args.days * 86400

    print(f"marathon: {args.days} days, {args.workers} workers, "
          f"rounds {[round(r / 3600, 1) for r in rounds]}h", flush=True)
    print(f"deadline {time.strftime('%Y-%m-%d %H:%M', time.localtime(deadline))}",
          flush=True)

    marathon(rounds, workers=args.workers, deadline=deadline,
             instance_dir=args.dir, solutions_dir=args.solutions_dir)

    from benchmarks.ratchet import find_unproven
    left = find_unproven(args.dir, args.solutions_dir)
    print(f"\nfinished in {(time.time() - started) / 3600:.1f}h; "
          f"{len(left)} still open", flush=True)


if __name__ == "__main__":
    main()
