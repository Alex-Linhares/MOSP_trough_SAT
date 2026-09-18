"""Guards on the escalating-budget driver.

The risk in a five-day unattended run is not a wrong answer -- `sweep` and the
search underneath it are tested elsewhere -- but a driver that overruns its
deadline, or that re-solves what it has already closed. Both are checked here
against a stubbed `sweep`, so the tests cost nothing and still pin the arithmetic.
"""

import math
import time

import benchmarks.marathon as marathon_module
from benchmarks.marathon import marathon


def _stub(monkeypatch, open_after_each, record, clock=None):
    """Replace sweep, find_unproven and the clock.

    A round that returns instantly would let every round believe it has the
    whole budget left, which is not how the driver behaves in production and
    would make the deadline test vacuous. So the fake sweep advances a fake
    clock by exactly the wall time it would have taken: `ceil(n / workers)`
    waves at the per-instance budget.
    """
    state = {"round": 0}

    def fake_sweep(targets, timeout, workers, solutions_dir, verbose):
        record.append((len(targets), timeout, workers))
        if clock is not None:
            clock["now"] += math.ceil(len(targets) / workers) * timeout
        return [(f"i{n}", 10, 9, 1.0, "refutation") for n in range(len(targets))]

    def fake_find_unproven(instance_dir, solutions_dir):
        n = open_after_each[min(state["round"], len(open_after_each) - 1)]
        state["round"] += 1
        return [object()] * n

    monkeypatch.setattr("benchmarks.csearch.sweep", fake_sweep)
    monkeypatch.setattr("benchmarks.ratchet.find_unproven", fake_find_unproven)
    if clock is not None:
        monkeypatch.setattr(marathon_module.time, "time", lambda: clock["now"])


def test_rounds_escalate_and_shrink_to_the_deadline(monkeypatch):
    """The rounds together may not run past the deadline; budgets shrink to fit.

    Nothing ever closes here, so every round faces the same 50 instances -- the
    case where a fixed schedule would overrun by the most.
    """
    record = []
    clock = {"now": 1_000_000.0}
    _stub(monkeypatch, [50, 50, 50, 50], record, clock)

    start = clock["now"]
    deadline = start + 10 * 3600                # ten hours
    marathon(rounds=(6 * 3600, 18 * 3600, 48 * 3600), workers=25,
             deadline=deadline, verbose=False)

    assert record, "no round ran"
    assert clock["now"] <= deadline + 1, (
        f"overran by {(clock['now'] - deadline) / 3600:.2f}h")
    # 50 instances over 25 workers is two waves, so six hours each cannot fit.
    assert record[0][1] < 6 * 3600


def test_a_round_asks_only_for_what_is_still_open(monkeypatch):
    """Closed instances drop out between rounds rather than being re-solved."""
    record = []
    _stub(monkeypatch, [40, 12, 3], record)

    marathon(rounds=(60, 60, 60), workers=25, deadline=None, verbose=False)

    assert [n for n, _, _ in record] == [40, 12, 3]


def test_it_stops_early_when_nothing_is_open(monkeypatch):
    record = []
    _stub(monkeypatch, [0], record)

    marathon(rounds=(60, 60), workers=25, deadline=None, verbose=False)

    assert record == []


def test_it_stops_when_the_deadline_has_already_passed(monkeypatch):
    record = []
    _stub(monkeypatch, [10], record)

    marathon(rounds=(60,), workers=25, deadline=time.time() - 1, verbose=False)

    assert record == []
