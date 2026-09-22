"""The CP model of Martin, Yanasse & Pinto (2022) §4, run under OR-Tools CP-SAT.

**"CP-SAT" here is Google's product name for the OR-Tools constraint solver.**
It is not a SAT formulation and has nothing to do with `mosp_encoding.py`: that
paper contains no SAT at all -- three models (two ILP, one CP), all run under
CPLEX. Solving their CP model with OR-Tools instead is our choice, because it
installs freely. Prose in this project calls this "the CP oracle" to keep the
two apart.

**This file is executed by `.venv-cpsat/bin/python`, not by the project's
interpreter, and it imports nothing from the project on purpose.** It reads an
instance as JSON on stdin and writes the answer as JSON on stdout. The isolation
is the point: an oracle that shared code with the solvers it checks would not be
checking much. It is also a practical necessity -- `ortools` needs numpy >= 2 and
clashes with anaconda's native libprotobuf, so it cannot live in the same
environment as the rest of this project.

The model reads MOSP as a scheduling problem, which is what it is:

- each **pattern** is an interval of size 1, and `NoOverlap` over all of them
  forces the patterns into distinct time slots -- a permutation;
- each **item** (customer) is an interval spanning from the first pattern it
  needs to the last, which is exactly the window its stack is open;
- the space by the machine is a **renewable resource**: each open stack consumes
  one unit, and `Cumulative` caps the usage at `C`, the number to minimise.

Their `span(item_i, {pattern_j : j in J_i})` is written here as a min over the
starts and a max over the ends, which CP-SAT expresses directly.
"""

import json
import sys


def _emit(record):
    """One JSON object per line, flushed, so the caller sees it as it happens.

    A 24-hour solve that reports only at the end holds everything it found in
    memory until then, and loses all of it if interrupted.
    """
    json.dump(record, sys.stdout)
    sys.stdout.write("\n")
    sys.stdout.flush()


def solve(matrix, n_customers, n_patterns, max_seconds, workers, upper, lower,
          hint=None):
    from ortools.sat.python import cp_model

    model = cp_model.CpModel()
    horizon = n_patterns

    # One interval per pattern, size 1, no two overlapping: a permutation of
    # the time slots 0 .. n_patterns - 1.
    starts, ends, pattern_intervals = [], [], []
    for j in range(n_patterns):
        start = model.NewIntVar(0, horizon - 1, f"s{j}")
        end = model.NewIntVar(1, horizon, f"e{j}")
        starts.append(start)
        ends.append(end)
        pattern_intervals.append(model.NewIntervalVar(start, 1, end, f"p{j}"))
    model.AddNoOverlap(pattern_intervals)

    # One interval per customer, spanning the patterns it needs.
    item_intervals = []
    for i in range(n_customers):
        needed = [j for j in range(n_patterns) if matrix[i][j]]
        if not needed:
            continue                      # a customer needing nothing never opens
        first = model.NewIntVar(0, horizon - 1, f"is{i}")
        last = model.NewIntVar(1, horizon, f"ie{i}")
        model.AddMinEquality(first, [starts[j] for j in needed])
        model.AddMaxEquality(last, [ends[j] for j in needed])
        size = model.NewIntVar(1, horizon, f"il{i}")
        model.Add(size == last - first)
        item_intervals.append(model.NewIntervalVar(first, size, last, f"i{i}"))

    # A known sequence, handed over as a starting point. It costs nothing if
    # CP-SAT improves on it immediately and saves a great deal when it would
    # otherwise spend its budget rediscovering a worse one.
    if hint:
        for position, pattern in enumerate(hint):
            model.AddHint(starts[pattern], position)

    stacks = model.NewIntVar(lower, upper if upper else n_customers, "C")
    if item_intervals:
        model.AddCumulative(item_intervals, [1] * len(item_intervals), stacks)
    model.Minimize(stacks)

    def read_ordering(lookup):
        return [j for _, j in sorted((lookup(starts[j]), j)
                                     for j in range(n_patterns))]

    class Reporter(cp_model.CpSolverSolutionCallback):
        """Streams every improved solution out as it is found."""

        def on_solution_callback(self):
            _emit({"type": "improvement",
                   "value": int(self.Value(stacks)),
                   "ordering": read_ordering(self.Value),
                   "wall": self.WallTime()})

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = float(max_seconds)
    solver.parameters.num_search_workers = int(workers)
    status = solver.Solve(model, Reporter())

    answer = {
        "type": "final",
        "status": solver.StatusName(status),
        "value": None,
        "ordering": None,
        "best_bound": None,
        "wall": solver.WallTime(),
    }
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        answer["value"] = int(solver.Value(stacks))
        # The permutation, read back as the order the patterns occupy.
        answer["ordering"] = read_ordering(solver.Value)
        answer["best_bound"] = int(solver.BestObjectiveBound())
    return answer


def main():
    request = json.load(sys.stdin)
    try:
        answer = solve(
            request["matrix"], request["n_customers"], request["n_patterns"],
            request.get("max_seconds", 60.0), request.get("workers", 1),
            request.get("upper"), request.get("lower", 0),
            request.get("hint"))
    except Exception as exc:  # noqa: BLE001
        answer = {"type": "final", "status": "ERROR",
                  "error": f"{type(exc).__name__}: {exc}",
                  "value": None, "ordering": None}
    _emit(answer)


if __name__ == "__main__":
    main()
