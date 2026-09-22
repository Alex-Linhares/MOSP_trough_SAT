"""Race the two decision procedures and take the first definitive answer.

The project has two complete ways to decide "MOSP(I) <= k?", and they fail on
disjoint sets of instances:

| | SAT encoding | customer search |
|---|---|---|
| dense (d >= 6) | refutations do not return | seconds |
| sparse (d = 2) | refutations do not return | branching factor explodes |
| what it searches | product positions, `O(m^2)` variables | customer closing orders |
| what it needs | a small formula | a small branching factor |

*(`reports/customer_search.md` §1.)* Nothing ran both, so every hard instance
was decided by whichever procedure the caller happened to pick, and picking
wrong cost the whole budget. This runs them at once on separate cores, takes the
first definitive answer and kills the other.

**Correctness does not depend on who wins.** Both answer the same question about
the same instance; a satisfiable answer carries a closing order, which the caller
re-simulates, and a refutation from either is a refutation. What the race buys is
the *minimum* of two runtimes instead of a guess at which is smaller -- and on a
machine with spare cores that minimum costs nothing extra in wall clock.

Usage:
    from satisfiability.race import decide_race, solve_race
    answer = decide_race(instance, k, timeout=60)
"""

from __future__ import annotations

import multiprocessing
import queue as _queue
import time
from dataclasses import dataclass
from typing import Callable, Optional, Sequence

from mosp.instance import MOSPInstance
from mosp.verify import max_open_stacks
from satisfiability.heuristics import product_order_from_customers

PROCEDURES = ("csearch", "sat")


@dataclass
class RaceDecision:
    """The answer, and which procedure got there first.

    `status` is "sat" with a customer closing order, "unsat", or "unknown" when
    both ran out of budget. `winner` is the procedure that answered; on
    "unknown" it is empty.
    """

    status: str
    order: list[int] | None
    winner: str
    seconds: float
    losers: dict[str, str]


def _csearch_worker(matrix, n_customers, n_patterns, name, k, seconds, out) -> None:
    import numpy as np

    from satisfiability.customer_search import decide, sparse_enough_for_better_move

    instance = MOSPInstance(matrix=np.array(matrix, dtype=np.int8),
                            n_customers=n_customers, n_patterns=n_patterns,
                            name=name)
    answer = decide(
        instance, k,
        deadline=None if seconds is None else time.monotonic() + seconds,
        better_move=sparse_enough_for_better_move(instance),
    )
    out.put(("csearch", answer.status, answer.order))


def _sat_worker(matrix, n_customers, n_patterns, name, k, seconds, out) -> None:
    import numpy as np

    from satisfiability.customer_search import _closing_order
    from satisfiability.mosp_solver import decide_mosp

    instance = MOSPInstance(matrix=np.array(matrix, dtype=np.int8),
                            n_customers=n_customers, n_patterns=n_patterns,
                            name=name)
    ordering = decide_mosp(instance, k)
    if ordering is None:
        out.put(("sat", "unsat", None))
    else:
        # Reported as a closing order so that both procedures answer in the same
        # currency and the caller need not know who won.
        out.put(("sat", "sat", _closing_order(instance, ordering)))


_WORKERS: dict[str, Callable] = {"csearch": _csearch_worker, "sat": _sat_worker}


def decide_race(
    instance: MOSPInstance,
    k: int,
    *,
    timeout: float | None = None,
    procedures: Sequence[str] = PROCEDURES,
) -> RaceDecision:
    """Decide "MOSP(instance) <= k?" with every named procedure at once.

    Args:
        timeout: wall clock for the whole race. Each procedure gets the same
            budget; the first definitive answer ends it early.
        procedures: any of "csearch" (the complete customer search, in C) and
            "sat" (the direct CNF encoding through CaDiCaL). One name runs that
            procedure alone, which is how the benchmark gets its baselines
            through the same harness as the race.

    Returns:
        A `RaceDecision`. "unknown" means every procedure exhausted the budget,
        which proves nothing either way.
    """
    started = time.monotonic()
    out: multiprocessing.Queue = multiprocessing.Queue()
    payload = (instance.matrix.tolist(), instance.n_customers,
               instance.n_patterns, instance.name, k, timeout, out)

    running: dict[str, multiprocessing.Process] = {}
    for name in procedures:
        proc = multiprocessing.Process(target=_WORKERS[name], args=payload)
        proc.start()
        running[name] = proc

    losers: dict[str, str] = {}
    winner, status, order = "", "unknown", None
    deadline = None if timeout is None else started + timeout

    try:
        while running:
            remaining = None if deadline is None else max(0.0, deadline - time.monotonic())
            if remaining == 0.0:
                break
            try:
                name, result, found = out.get(timeout=remaining)
            except _queue.Empty:
                break

            running.pop(name, None)
            if result in ("sat", "unsat"):
                winner, status, order = name, result, found
                break
            losers[name] = result
    finally:
        for name, proc in running.items():
            if proc.is_alive():
                proc.terminate()
            proc.join(timeout=5)
        out.close()

    return RaceDecision(status, order, winner, time.monotonic() - started, losers)


@dataclass
class RaceSolution:
    """What a raced descent established. Mirrors `customer_search.Solution`."""

    value: int
    order: list[int]
    proof: str
    seconds: float
    winners: dict[int, str]

    @property
    def proved(self) -> bool:
        return bool(self.proof)


def solve_race(
    instance: MOSPInstance,
    *,
    upper: int | None = None,
    upper_strategy: str = "cs-dfs",
    lower: int = 0,
    time_budget: float | None = None,
    procedures: Sequence[str] = PROCEDURES,
    on_improve: "Optional[Callable[[int, list[int]], None]]" = None,
) -> RaceSolution:
    """Descend `k` with the race until it refutes or the budget runs out.

    The same descent `customer_search.solve` runs, with `decide_race` in place
    of `decide`. Each satisfiable answer is re-simulated on the product order it
    induces rather than trusted at `k`, for the reason that function gives: the
    closing-order measure can over-charge, so the witness is often worth more
    than the `k` it was found at.
    """
    from satisfiability.heuristics import upper_bound

    started = time.monotonic()
    winners: dict[int, str] = {}

    if upper is None:
        value, ordering = upper_bound(instance, upper_strategy)
        order = _as_closing_order(instance, ordering)
    else:
        value, order = upper, []

    if value <= lower:
        return RaceSolution(value, order, "bound", time.monotonic() - started, winners)

    k = value - 1
    while k >= lower:
        left = None if time_budget is None else time_budget - (time.monotonic() - started)
        if left is not None and left <= 0:
            break
        answer = decide_race(instance, k, timeout=left, procedures=procedures)
        if answer.winner:
            winners[k] = answer.winner

        if answer.status == "unsat":
            return RaceSolution(value, order, "refutation",
                                time.monotonic() - started, winners)
        if answer.status == "unknown":
            break

        found = answer.order or []
        achieved = max_open_stacks(instance, product_order_from_customers(instance, found))
        if achieved < value:
            value, order = achieved, found
            if on_improve:
                on_improve(value, order)
        k = min(k, value) - 1

    return RaceSolution(value, order, "", time.monotonic() - started, winners)


def _as_closing_order(instance: MOSPInstance, ordering: list[int]) -> list[int]:
    from satisfiability.customer_search import _closing_order

    return _closing_order(instance, ordering)
