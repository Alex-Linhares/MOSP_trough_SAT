"""Deadline-aware customer search against whatever is still unproven.

Wraps `benchmarks/csearch.py` with one thing it lacks: a wall-clock deadline.
Given "five days and 25 workers" it works out the per-instance budget that fills
exactly that -- `ceil(instances / workers)` waves at the budget -- and runs it.

**One round by default, and the reason is worth stating, because escalating
rounds look attractive and are usually wrong here.** A round that ends without
closing an instance kills its search. The upper bound survives, since the
solution cache holds it, but the search state does not, and for these instances
nearly all the time goes into a single refutation at a fixed `k` behind a memo
of millions of states. That memo is what makes a refutation land at all: on SP3,
without it the search burns 12M nodes and never returns, with it 3.9M nodes and
134 seconds. Restarting rebuilds it from nothing, so every round after the first
pays again for what the last one already knew.

The usual argument for escalating -- close the easy instances early and the
survivors get bigger budgets -- does not need rounds at all. The pool already
does it: when an instance closes, its slot immediately starts a waiting one,
which then gets the full remaining budget. The adaptivity is free.

Several rounds are still available through `--rounds`, for the case where
restarts are genuinely cheap: an instance whose descent is still improving its
*upper* bound loses little by starting again from the better bound. Nothing in
this corpus has looked like that, so it is not the default.

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

# One round, sized from the deadline. `None` means "whatever fills the time".
DEFAULT_ROUNDS = (None,)

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
        if budget is None and deadline is None:
            raise ValueError("a round needs either a budget or a deadline")
        if budget is None:
            budget = float("inf")   # the deadline below decides it
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

    shown = [("deadline-sized" if r is None else f"{r / 3600:.1f}h") for r in rounds]
    print(f"marathon: {args.days} days, {args.workers} workers, "
          f"rounds {shown}", flush=True)
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
